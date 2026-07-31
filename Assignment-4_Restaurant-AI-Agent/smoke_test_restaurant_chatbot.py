"""Smoke and regression test for the SQLite restaurant chatbot."""

import os
import sqlite3
import tempfile
import uuid

from restaurant_chatbot import RestaurantChatbot
from restaurant_db import (
    get_menu_items,
    get_restaurant_details_and_hours,
    initialize_database,
)


def count_reservations(db_path: str) -> int:
    """Return the number of reservations stored in the test database."""

    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM reservations").fetchone()

    return row[0]


def run_smoke_test() -> None:
    """Test database setup, menu routing, reservation flow, duplicates, and cancellation."""

    # Use a temporary database so this test never changes the real restaurant.sqlite file.
    db_path = os.path.join(
        tempfile.gettempdir(),
        f"test_restaurant_{uuid.uuid4().hex}.sqlite"
    )

    initialize_database(db_path)

    menu = get_menu_items(db_path)
    details, hours = get_restaurant_details_and_hours(db_path)

    assert len(menu) >= 3, "Menu should have seeded items"
    assert details.get("name"), "Restaurant details should be seeded"
    assert len(hours) == 7, "Opening hours should include all days"

    # Temporarily disable OpenAI so the test does not use API credits.
    old_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        bot = RestaurantChatbot(db_path=db_path)

        menu_reply = bot.answer("What vegetarian dishes are on the menu?")
        missing_item_reply = bot.answer("Do you have pizza in the menu?")
        details_reply = bot.answer("What are your opening hours and address?")
        other_reply = bot.answer("Can you tell me a joke?")

        # Cancellation must always be routed before reservation.
        assert bot.classify_question("Cancel a reservation") == "cancellation"

        # Start a reservation without an email address.
        pending_reply = bot._complete_reservation({
            "customer_name": "Amit",
            "date": "2099-10-04",
            "time": "20:00",
            "party_size": 2,
            "contact": None
        })

        assert "provide your email" in pending_reply.lower()
        assert count_reservations(db_path) == 0

        # Complete the pending reservation using an email-only message.
        confirmation_reply = bot.answer("amitza333@gmail.com")

        assert "Reservation confirmed" in confirmation_reply
        assert count_reservations(db_path) == 1

        # Repeating the same booking must not insert another database row.
        bot._complete_reservation({
            "customer_name": "Amit",
            "date": "2099-10-04",
            "time": "20:00",
            "party_size": 2,
            "contact": None
        })

        duplicate_reply = bot.answer("amitza333@gmail.com")

        assert "already exists" in duplicate_reply.lower()
        assert count_reservations(db_path) == 1

        # The system must not treat 8pm or 2 people as the booking number.
        missing_id_reply = bot.answer(
            "Cancel a reservation for Amit tomorrow at 8pm for 2 people"
        )

        assert "booking ID" in missing_id_reply
        assert count_reservations(db_path) == 1

        # Cancel the real booking using its ID.
        cancel_reply = bot.answer("Cancel reservation #1")

        assert "has been cancelled" in cancel_reply
        assert count_reservations(db_path) == 0

        # Cancelling the same booking again must report that it no longer exists.
        second_cancel_reply = bot.answer("Cancel reservation #1")

        assert "was not found" in second_cancel_reply
        # General restaurant follow-ups should be passed to the LLM with chat history.
        assert bot.classify_question(
            "How much is the total with a 10% tip?"
        ) == "general"

        assert bot.classify_question(
            "Tell me my order again"
        ) == "general"

    finally:
        if old_key is not None:
            os.environ["OPENAI_API_KEY"] = old_key

    assert "Vegan Zen Roll" in menu_reply or "Edamame" in menu_reply
    assert "could not find that item" in missing_item_reply
    assert "Opening Hours" in details_reply and "Address" in details_reply
    assert "I can help with menu items" in other_reply

    try:
        os.remove(db_path)
    except OSError:
        pass


if __name__ == "__main__":
    run_smoke_test()
    print("smoke_test_restaurant_chatbot.py: PASS")