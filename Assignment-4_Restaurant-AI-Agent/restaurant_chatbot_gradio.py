"""Gradio web interface for the restaurant chatbot."""

from dotenv import load_dotenv
import gradio as gr

from restaurant_chatbot import RestaurantChatbot
from restaurant_db import initialize_database


def create_bot(db_path: str = "restaurant.sqlite") -> RestaurantChatbot:
    """Load environment variables, initialize SQLite, and create the chatbot."""

    load_dotenv()
    initialize_database(db_path)

    return RestaurantChatbot(db_path=db_path)


def build_demo(bot: RestaurantChatbot) -> gr.Blocks:
    """Create the Gradio interface around the chatbot backend."""

    def chat_handler(message: str, history: list[dict]) -> tuple[list[dict], str]:
        """Send the current message and previous conversation to the chatbot."""

        history = history or []
        user_text = (message or "").strip()

        if not user_text:
            return history, ""

        # Convert Gradio messages into simple readable history lines for LangChain.
        history_for_bot = [
            f"{item.get('role', 'user').title()}: {item.get('content', '')}"
            for item in history
        ]

        answer = bot.answer(user_text, history=history_for_bot)

        updated_history = history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": answer}
        ]

        return updated_history, ""

    def clear_chat() -> list:
        """Clear the visible chat and any incomplete reservation."""

        bot.reset_conversation()

        return []

    with gr.Blocks(title="Restaurant Chatbot") as demo:
        gr.Markdown(
            "## Sakura Asian Kitchen Chatbot\n"
            "Ask about menu items, prices, opening hours, reservations, or cancellations."
        )

        chatbot = gr.Chatbot(label="Conversation", height=450)

        message_box = gr.Textbox(
            label="Your question",
            placeholder="e.g., Make a reservation for Amit tomorrow at 8pm for 2 people"
        )

        with gr.Row():
            send_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")

        send_btn.click(
            chat_handler,
            inputs=[message_box, chatbot],
            outputs=[chatbot, message_box]
        )

        message_box.submit(
            chat_handler,
            inputs=[message_box, chatbot],
            outputs=[chatbot, message_box]
        )

        clear_btn.click(
            clear_chat,
            outputs=chatbot,
            queue=False
        )

        gr.Examples(
            examples=[
                "What are your opening hours?",
                "What spicy dishes are available?",
                "Make a reservation for Amit tomorrow at 8pm for 2 people",
                "Cancel reservation #1"
            ],
            inputs=message_box
        )

    return demo


def main() -> None:
    """Start the Gradio application."""

    bot = create_bot()
    demo = build_demo(bot)

    demo.launch(server_port=7861)


if __name__ == "__main__":
    main()