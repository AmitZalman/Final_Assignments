"""LangChain chatbot that routes questions to menu, hours, reservations, cancellations, and general questions."""

import os
import json
import logging
import requests
import re
from datetime import datetime
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from restaurant_db import (
    get_restaurant_details_and_hours,
    search_menu_items,
    get_menu_items,
    book_reservation,
    find_duplicate_reservation,
    cancel_reservation,
)


# Configure basic debug logging for reservations, cancellations, and errors.
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


class RestaurantChatbot:
    """Restaurant assistant backed by LangChain, OpenAI, SQLite, and n8n."""

    def __init__(self, db_path: str, model_name: str = None) -> None:
        self.db_path = db_path
        self.llm = None

        # Stores an incomplete reservation while waiting for the user's email address.
        self.pending_reservation = None
        self.pending_cancellation = None

        actual_model = model_name or os.getenv("LLM_MODEL", "gpt-4o-mini")

        if os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(model=actual_model, temperature=0)

            # Main prompt used for menu and restaurant-information questions.
            self.answer_prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a helpful restaurant assistant for Sakura Asian Kitchen. "
                    "Base your answers strictly on the provided Context and Chat History. "
                    "Use the Chat History to remember dishes previously recommended or selected. "
                    "You may calculate order totals, percentages, and tips using prices from the conversation. "
                    "When the user asks to repeat their order, list only the items that were previously selected. "
                    "Do not invent dishes, prices, orders, or restaurant information. "
                    "If the requested information is not available in the Context or Chat History, "
                    "politely say you are not sure.\n\n"
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. If the user asks to see the menu, and the menu items are provided in the Context, you MUST list them exactly as provided. Do not claim it is too long or refuse to provide the full list.\n"
                    "2. If the user asks for opening hours, and they are in the Context, you MUST provide them without hesitation.\n"
                    "3. If the user asks you to build or recommend a full course meal (e.g., starters, mains, desserts, drinks) based on their preferences or dietary restrictions, act as an expert chef and host: select appropriate dishes strictly from the provided Context, explain why they complement each other, and calculate the total estimated price for the course."
                ),
                (
                    "human",
                    "Chat History:\n{history}\n\n"
                    "Question: {question}\n\n"
                    "Context:\n{context}"
                ),
            ])

    def reset_conversation(self) -> None:
        """Clear any reservation that is still waiting for missing information."""

        self.pending_reservation = None
        logger.info("Pending reservation state cleared")

    def classify_question(self, question: str) -> str:
        """Classify the user's question into one supported chatbot route."""

        lower_q = question.lower()

        # Cancellation must be checked first because cancellation messages often contain "reservation".
        if "cancel" in lower_q:
            return "cancellation"

        reservation_keywords = ["reserve", "reservation", "book", "table"]

        if any(keyword in lower_q for keyword in reservation_keywords):
            return "reservation"

        menu_keywords = [
            "menu", "dish", "food", "price", "cost", "person", "vegan",
            "vegetarian", "spicy", "drink", "peanut", "allergic",
            "allergy", "meat", "without", "eat"
        ]

        if any(keyword in lower_q for keyword in menu_keywords):
            return "menu"

        hours_keywords = ["hour", "open", "close", "address", "phone", "location", "email", "website"]

        if any(keyword in lower_q for keyword in hours_keywords):
            return "hours"

        # Use the LLM only when keyword routing cannot determine the category.
        if not self.llm:
            return "general"

        classify_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a router for a restaurant chatbot. "
                "Classify the user message into exactly one category: "
                "reservation, cancellation, menu, hours, or general. "
                "Return ONLY the category word."
            ),
            ("human", "{question}")
        ])

        try:
            chain = classify_prompt | self.llm | StrOutputParser()
            result = chain.invoke({"question": question}).strip().lower()
        except Exception:
            logger.exception("Question classification failed")
            return "general"

        valid_categories = {"reservation", "cancellation", "menu", "hours", "general"}

        return result if result in valid_categories else "general"

    def _build_menu_context(self, question: str) -> tuple[str, bool]:
        """Retrieve menu information from SQLite for the user's question."""

        lower_q = question.lower()

        # Broad questions require the full menu so the LLM can filter the results.
        complex_keywords = [
            "without", "no ", "allergy", "allergic", "popular",
            "recommend", "meat", "cost", "price", "person",
            "menu", "whole", "full", "all", "list", "show"
        ]

        if self.llm and any(keyword in lower_q for keyword in complex_keywords):
            rows = get_menu_items(self.db_path)
        else:
            rows = search_menu_items(self.db_path, question)

            # If the targeted search finds nothing, let the LLM inspect the full menu.
            if not rows and self.llm:
                rows = get_menu_items(self.db_path)

        if not rows:
            return "No menu records matched the question.", False

        lines: List[str] = []

        for row in rows:
            veg = "vegetarian" if row["is_vegetarian"] else "non-vegetarian"
            spicy = "spicy" if row["is_spicy"] else "not spicy"
            status = "available" if row["is_available"] else "currently unavailable"

            lines.append(
                f"- {row['item_name']} ({row['category']}): {row['description']} | "
                f"${row['price']:.2f} | {veg}, {spicy}, {status}"
            )

        return "\n".join(lines), True

    def _build_details_context(self) -> str:
        """Retrieve restaurant contact details and opening hours from SQLite."""

        details, hours = get_restaurant_details_and_hours(self.db_path)

        if not details:
            return "No restaurant details found."

        details_text = (
            f"Name: {details['name']}\n"
            f"Address: {details['address']}\n"
            f"Phone: {details['phone']}\n"
            f"Email: {details['email']}\n"
            f"Website: {details['website']}"
        )

        hours_lines = [
            f"- {item['day_of_week']}: {item['open_time']} to {item['close_time']}"
            + (f" ({item['notes']})" if item.get("notes") else "")
            for item in hours
        ]

        return details_text + "\n\nOpening Hours:\n" + "\n".join(hours_lines)

    def _complete_reservation(self, details: dict) -> str:
        """Validate, deduplicate, save, and confirm a reservation."""

        # 1. Validations First! Check the data we already have to block bad requests immediately.
        if details.get("party_size"):
            try:
                party_size = int(details["party_size"])
                # Solution for Scenario 2 (Edge case validations): Block oversized parties
                if party_size > 15:
                    self.pending_reservation = None  # Cancel the flow
                    return "For large parties over 15 guests, please call us directly at +1-555-0888 so we can accommodate you perfectly!"
                if party_size < 1:
                    return "The party size must be at least 1."
            except (TypeError, ValueError):
                return "Party size must be a valid number."

        if details.get("time"):
            reservation_time = str(details["time"]).strip()
            try:
                hour = int(reservation_time.split(":")[0])
                if hour < 11 or hour > 23:
                    self.pending_reservation = None  # Cancel the flow
                    return "Our kitchen is open from 11:30 to 22:00 (and later on weekends). Please select a time within our operating hours."
            except ValueError:
                pass

        # 2. Check for missing details only AFTER validations have passed.
        required_fields = {
            "customer_name": "your name",
            "date": "the date",
            "time": "the time",
            "party_size": "the party size",
        }

        missing = [label for field, label in required_fields.items() if not details.get(field)]

        # Solution for Scenario 3 (Amnesia): More natural and polite phrasing
        if missing:
            self.pending_reservation = details
            logger.info("Reservation waiting for: %s", ", ".join(missing))

            if "your name" in missing:
                return f"Just to make sure I have everything right, could you provide {', '.join(missing)}?"
            return f"Almost there! I just need {', '.join(missing)} to secure your table."

        if not details.get("contact"):
            self.pending_reservation = details
            logger.info("Waiting for reservation email")
            return (
                "Perfect! Just in case I missed it earlier, could you please provide your email address "
                "so I can send you the confirmation?"
            )

        customer_name = str(details["customer_name"]).strip()
        reservation_date = str(details["date"]).strip()
        reservation_time = str(details["time"]).strip()
        party_size = int(details["party_size"])
        contact = str(details["contact"]).strip().lower()

        # Prevent the same reservation from being inserted more than once.
        existing_id = find_duplicate_reservation(
            self.db_path,
            customer_name,
            reservation_date,
            reservation_time,
            party_size,
            contact
        )

        if existing_id:
            self.pending_reservation = None
            logger.info("Duplicate reservation prevented: booking_id=%s", existing_id)

            return f"This reservation already exists. Booking #{existing_id}"

        res_id = book_reservation(
            self.db_path,
            customer_name,
            reservation_date,
            reservation_time,
            party_size,
            contact
        )

        self.pending_reservation = None
        logger.info("Reservation created: booking_id=%s", res_id)

        reservation_data = {
            "customer_name": customer_name,
            "date": reservation_date,
            "time": reservation_time,
            "party_size": party_size,
            "contact": contact,
            "id": res_id
        }

        self._notify_n8n(reservation_data, event="reservation")

        return (
            "✅ Reservation confirmed!\n"
            f"Name: {customer_name}\n"
            f"Date: {reservation_date} at {reservation_time}\n"
            f"Party of {party_size} · Booking #{res_id}\n"
            f"Confirmation sent to: {contact}"
        )

    def _handle_reservation(self, question: str) -> str:
        """Extract reservation details from the message and start the booking flow."""

        if not self.llm:
            return "Please call us directly to make a reservation!"

        # Providing today's date prevents the model from resolving "tomorrow" to an old date.
        current_date = datetime.now().strftime("%Y-%m-%d")

        menu_context, _ = self._build_menu_context(question)
        details_context = self._build_details_context()

        extract_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Extract reservation details from the message. "
                "Return ONLY valid JSON with keys: customer_name, date, time, party_size, contact, extra_answer. "
                "If the user asks an additional question (like menu recommendations or hours), provide a brief, friendly answer in 'extra_answer' USING ONLY THE PROVIDED CONTEXT. If no extra question, use null. "
                f"Today's date is {current_date}. "
                "Resolve today and tomorrow relative to today's date. "
                "Return date as YYYY-MM-DD and time as HH:MM in 24-hour format. "
                "Interpret 22pm as 22:00. "
                "Do not include markdown or explanations.\n\n"
                f"Context:\n{details_context}\n\nMenu:\n{menu_context}"
            ),
            ("human", "{question}")
        ])

        try:
            chain = extract_prompt | self.llm | StrOutputParser()
            raw = chain.invoke({"question": question})
            new_details = json.loads(raw)

            # Extract the additional answer (if the client asked something beyond the reservation)
            extra_answer = new_details.pop("extra_answer", None)

            # Start from any details already gathered in previous turns, then
            # merge in the newly extracted values (ignoring nulls) so nothing
            # collected earlier is lost.
            details = dict(self.pending_reservation) if self.pending_reservation else {}

            for key, value in new_details.items():
                if value:
                    details[key] = value

            # Also capture a bare email address typed on its own.
            email_match = re.search(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                question
            )

            if email_match and not details.get("contact"):
                details["contact"] = email_match.group(0)

            # Complete the reservation and combine both answers if needed
            reply = self._complete_reservation(details)

            if extra_answer:
                return f"{extra_answer}\n\n{reply}"
            return reply

        except (json.JSONDecodeError, ValueError):
            logger.exception("The reservation extractor returned invalid data")

            return "Sorry, I couldn't process that reservation. Please try again."

        except Exception:
            logger.exception("Reservation extraction failed")

            return "Sorry, I couldn't process that reservation. Please try again."

    def _handle_cancellation(self, question: str) -> str:
        """Cancel a reservation using a booking ID or customer name."""
        import sqlite3

        lower_q = question.lower()

        # Try to find a booking ID using Regex
        match = re.search(
            r"(?:reservation|booking)(?:\s+(?:number|id))?\s*#?\s*(\d+)|#\s*(\d+)|^(\d+)$",
            question,
            re.IGNORECASE
        )

        if match:
            res_id = int(match.group(1) or match.group(2) or match.group(3))
            deleted = cancel_reservation(self.db_path, res_id)

            if not deleted:
                logger.warning("Cancellation requested for missing booking_id=%s", res_id)
                return f"Reservation #{res_id} was not found."

            self.pending_cancellation = None
            logger.info("Reservation cancelled: booking_id=%s", res_id)
            self._notify_n8n({"id": res_id}, event="cancellation")
            return f"Reservation #{res_id} has been cancelled."

        # If no ID was provided, search DB by name
        search_name = lower_q.replace("my name is", "").strip()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, date, time FROM reservations WHERE LOWER(customer_name) LIKE ?",
                (f"%{search_name}%",)
            ).fetchall()

        if rows:
            if len(rows) == 1:
                res_id = rows[0]["id"]
                cancel_reservation(self.db_path, res_id)
                self.pending_cancellation = None
                self._notify_n8n({"id": res_id}, event="cancellation")
                return f"I found your reservation (#{res_id} for {rows[0]['date']} at {rows[0]['time']}) and cancelled it."
            else:
                options = ", ".join([f"#{r['id']} ({r['date']} at {r['time']})" for r in rows])
                return f"I found multiple reservations for that name: {options}. Please reply with the exact ID."

        # Activate the pending cancellation state if we don't have enough info yet
        self.pending_cancellation = True
        return (
            "Please provide your booking ID number to cancel (e.g., 'Cancel reservation #4') or simply provide your name."
        )

    def _notify_n8n(self, data: dict, event: str) -> None:
        """Send reservation events to n8n without crashing the chatbot."""

        webhook_url = os.getenv("N8N_WEBHOOK_URL")

        if not webhook_url:
            return

        try:
            response = requests.post(
                webhook_url,
                json={**data, "event": event},
                timeout=5
            )

            response.raise_for_status()

        except requests.RequestException:
            # The reservation remains saved locally even if n8n is temporarily unavailable.
            logger.exception("Failed to send %s event to n8n", event)

    def answer(self, question: str, history: list = None) -> str:
        """Route a question, retrieve SQLite data, and return the chatbot response."""

        question = (question or "").strip()

        if not question:
            return "Please enter a question."

        # While a reservation is being collected, keep every follow-up message
        # inside the booking flow so partial details (name, date, email, ...)
        # can be gathered across multiple turns. Cancellation still breaks out.
        lower_q = question.lower()
        escape_words = ["cancel", "stop", "nevermind", "abort", "start over"]


        if self.pending_reservation and any(w in lower_q for w in escape_words):
            self.reset_conversation()
            return "No problem, I've cancelled that booking process. What else can I help you with?"


        if self.pending_reservation:
            return self._handle_reservation(question)

        if self.pending_cancellation:
            return self._handle_cancellation(question)

        route = self.classify_question(question)
        logger.info("Question route: %s", route)

        if route == "menu":
            context, has_match = self._build_menu_context(question)

            if not has_match:
                return (
                    "I could not find that item in the current menu. "
                    "Ask me to list available mains, starters, desserts, or drinks."
                )

        elif route == "hours":
            context = self._build_details_context()

        elif route == "reservation":
            return self._handle_reservation(question)

        elif route == "cancellation":
            return self._handle_cancellation(question)

        else:

            # General restaurant follow-up questions may depend on chat history.
            # Examples: asking for the previous order or calculating a tip.
            if not self.llm:
                return (

                    "I can help with menu items, prices, booking a table, "
                    "cancelling a reservation, and restaurant details "
                    "like opening hours, phone, and address."
                )

            basic_details = self._build_details_context()
            context = (

                f"Restaurant Details & Hours:\n{basic_details}\n\n"
                "About Sakura Asian Kitchen: We are a premium Asian fusion restaurant "
                "blending traditional Japanese techniques with modern pan-Asian flavors. "
                "Established to bring authentic and fresh ingredients to our guests, "
                "we offer a cozy, elegant atmosphere perfect for intimate dinners, "
                "family gatherings, and special occasions. We pride ourselves on our "
                "hand-crafted sushi, sizzling woks, and warm hospitality.\n\n"
                "Instructions:\n"
                "Use the 'About' section above and the 'Restaurant Details' to answer "
                "general questions about the restaurant warmly and enthusiastically. "
                "Use the Chat History to answer follow-up questions about "
                "previous menu recommendations, selected dishes, order totals, or tip calculations. "
                "Do not invent dishes, prices, or order details. "
                "If the question is completely unrelated to the restaurant or the conversation, "
                "politely explain what restaurant topics you can help with."

            )

        if not self.llm:
            return f"(Local fallback, no OpenAI key configured)\n{context}"

        history_text = "\n".join(history) if history else "No previous history."

        try:
            chain = self.answer_prompt | self.llm | StrOutputParser()

            return chain.invoke({
                "question": question,
                "context": context,
                "history": history_text
            })

        except Exception:
            logger.exception("Failed to generate the final chatbot answer")

            return (
                "I'm sorry, I'm currently having trouble connecting to our servers. "
                "Please try asking your question again in a moment."
            )