"""Tiny standalone web server that serves an elegant HTML chat page.

This is an optional alternative to the Gradio interface. It reuses the exact
same RestaurantChatbot backend and does not modify any existing code.

Run it with:
    python restaurant_chatbot_web.py

Then open http://localhost:7862 in your browser.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from dotenv import load_dotenv

from restaurant_chatbot import RestaurantChatbot
from restaurant_db import initialize_database


HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "restaurant_chat.html")
DB_PATH = os.path.join(HERE, "restaurant.sqlite")
PORT = 7862

# One shared bot instance keeps reservation state and history in memory,
# just like the CLI does.
load_dotenv()
initialize_database(DB_PATH)
bot = RestaurantChatbot(db_path=DB_PATH)
chat_history: list[str] = []


class ChatHandler(BaseHTTPRequestHandler):
    """Serves the chat page and answers POST /chat requests."""

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            try:
                with open(HTML_PATH, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, b"restaurant_chat.html not found", "text/plain")
        elif self.path == "/reset":
            bot.reset_conversation()
            chat_history.clear()
            self._send(200, b'{"ok": true}', "application/json")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self) -> None:
        if self.path != "/chat":
            self._send(404, b"Not found", "text/plain")
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            message = (payload.get("message") or "").strip()

            reply = bot.answer(message, history=chat_history)

            # Keep the conversation memory short, mirroring the CLI behaviour.
            chat_history.append(f"User: {message}")
            chat_history.append(f"Bot: {reply}")
            del chat_history[:-6]

            body = json.dumps({"reply": reply}).encode("utf-8")
            self._send(200, body, "application/json")

        except Exception as exc:  # keep the server alive on any error
            body = json.dumps({"error": f"Server error: {exc}"}).encode("utf-8")
            self._send(500, body, "application/json")

    def log_message(self, *args) -> None:
        # Silence the default per-request console noise.
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), ChatHandler)
    print(f"Sakura chat page running at  http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
