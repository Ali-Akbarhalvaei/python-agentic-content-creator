# app.py
# Final Version: With flexible topic parsing from user messages.

import os
import json
import asyncio
import threading
import time
from datetime import datetime
from glob import glob
from flask import Flask, request
from dotenv import load_dotenv
import telegram

# --- Import our main workflow function ---
from main import run_workflow

# Load environment variables from your .env file
load_dotenv(override=True)

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Initialize the Telegram Bot ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file.")
    bot = None
else:
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# --- Professional Async Task Handling ---
async_loop = asyncio.new_event_loop()


def run_async_loop():
    asyncio.set_event_loop(async_loop)
    async_loop.run_forever()


async_thread = threading.Thread(target=run_async_loop)
async_thread.daemon = True
async_thread.start()
# --- End of Async Setup ---


def send_telegram_message(chat_id, text):
    """Submits the async send_message task to our running event loop."""
    print(f"Submitting text message to {chat_id}...")
    try:
        asyncio.run_coroutine_threadsafe(
            bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"),
            async_loop,
        )
    except Exception as e:
        print(f"❌ FAILED to submit text message task: {e}")


def send_telegram_photo(chat_id, photo_path):
    """Submits the async send_photo task to our running event loop."""
    print(f"Submitting photo '{photo_path}' to {chat_id}...")
    try:
        photo_file = open(photo_path, "rb")
        asyncio.run_coroutine_threadsafe(
            bot.send_photo(chat_id=chat_id, photo=photo_file), async_loop
        )
    except Exception as e:
        print(f"❌ FAILED to submit photo task: {e}")


def run_workflow_and_reply(chat_id, topics: list, date_filter: str = None):
    """
    Runs the main workflow with user-defined topics and an optional date filter.
    """
    try:
        print(
            f"--- Starting background workflow for chat {chat_id} with topics: {topics}, date_filter: {date_filter} ---"
        )
        output_folder_path = run_workflow(topics=topics, date_filter=date_filter)

        if not output_folder_path:
            send_telegram_message(
                chat_id,
                "❌ I'm sorry, the content generation failed. This might be because no relevant news was found for your request. Please try again with different topics.",
            )
            return

        print(
            f"--- Workflow finished successfully. Sending results from '{output_folder_path}'. ---"
        )

        all_posts = sorted(
            list(set(f.split("_")[1] for f in os.listdir(output_folder_path)))
        )

        if not all_posts:
            send_telegram_message(
                chat_id, "❌ Workflow finished, but no content packages were found."
            )
            return

        for post_num_str in all_posts:
            send_telegram_message(
                chat_id, f"*--- Content for Post {int(post_num_str)} ---*"
            )
            time.sleep(1)

            caption_file = os.path.join(
                output_folder_path, f"post_{post_num_str}_caption.txt"
            )
            image_files = sorted(
                glob(
                    os.path.join(output_folder_path, f"post_{post_num_str}_slide_*.png")
                )
            )

            if os.path.exists(caption_file):
                with open(caption_file, "r", encoding="utf-8") as f:
                    caption = f.read()
                send_telegram_message(chat_id, caption)
                time.sleep(1)

            for image_path in image_files:
                send_telegram_photo(chat_id, image_path)
                time.sleep(1)

        send_telegram_message(chat_id, "✅ All content packages delivered!")

    except Exception as e:
        print(f"❌ An error occurred in the background workflow thread: {e}")
        send_telegram_message(
            chat_id, f"😥 An unexpected error occurred during content creation: {e}"
        )


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    if bot is None:
        return {"ok": False}
    update = request.get_json()

    try:
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            message_text = update["message"]["text"].lower()
            parts = message_text.split()
            command = parts[0]

            if command == "/start":
                reply_text = "Welcome! Use `/generate <topic1> <topic2>...` to get started.\nExample: `/generate AI` or `/generate finance politics`\nAdd `--date today` for today's popular news."
                send_telegram_message(chat_id, reply_text)

            elif command == "/generate":
                # --- NEW: Advanced Command Parsing ---
                date_arg = None
                user_topics = []

                # Check for the optional date flag and remove it
                if "--date" in parts and "today" in parts:
                    date_arg = datetime.now().strftime("%Y-%m-%d")
                    parts.remove("--date")
                    parts.remove("today")

                # The remaining parts are the topics
                user_topics = parts[1:]  # All parts after the /generate command

                # If no topics were provided, use defaults
                if not user_topics:
                    user_topics = ["finance", "politics"]
                    reply_text = f"No topics provided. Searching for default topics: {user_topics}..."
                else:
                    reply_text = (
                        f"✅ Roger that! Searching for news on: {user_topics}..."
                    )

                send_telegram_message(chat_id, reply_text)

                # Trigger the workflow with the parsed arguments
                workflow_thread = threading.Thread(
                    target=run_workflow_and_reply, args=(chat_id, user_topics, date_arg)
                )
                workflow_thread.start()

            else:
                reply_text = "I'm sorry, I only understand the `/start` and `/generate` commands."
                send_telegram_message(chat_id, reply_text)

    except Exception as e:
        print(f"❌❌❌ An error occurred processing the update: {e} ❌❌❌")

    return {"ok": True}


if __name__ == "__main__":
    print("🚀 Starting Flask web server for Telegram Bot...")
    app.run(port=4040, debug=True)
