"""CLI entrypoint for the LangChain and SQLite restaurant chatbot."""

from dotenv import load_dotenv

from restaurant_chatbot import RestaurantChatbot
from restaurant_db      import initialize_database


def main() -> None:
    # Load OPENAI_API_KEY (and any other secrets) from the .env file.
    load_dotenv()

    db_path = "restaurant.sqlite"

    # Creates the SQLite file and tables if they do not exist.
    initialize_database(db_path)

    bot = RestaurantChatbot(db_path=db_path)

    # Updated greeting and suggested prompts for Sakura Asian Kitchen.
    print("Welcome to Sakura Asian Kitchen Chatbot! Type 'exit' to quit.")
    print("Try: 'What are your opening hours?', 'What is your most popular dish?', or 'Do you have dishes without peanuts?'\n")

    # Initialize conversational memory so the bot understands context and follow-up questions.
    chat_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Bot: Goodbye!")
            break

        # Pass the user input along with the chat history to the bot.
        reply = bot.answer(user_input, history=chat_history)
        print(f"Bot: {reply}\n")

        # Update the chat history, keeping only the last 6 messages to optimize token usage.
        chat_history.append(f"User: {user_input}")
        chat_history.append(f"Bot: {reply}")
        if len(chat_history) > 6:
            chat_history = chat_history[-6:]


if __name__ == "__main__":
    main()