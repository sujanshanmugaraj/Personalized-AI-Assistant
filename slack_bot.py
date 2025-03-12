
import os
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import google.generativeai as genai  # ✅ Google Gemini


def run_flask():
    """Function to start Flask server."""
    app.run(port=5001, debug=True)  # Set the desired port


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Slack & Google Gemini API Keys
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ Missing Google Gemini API Key! Add it to your .env file.")

slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")
  # ✅ Use Google Gemini-Pro

# Channel to post the daily digest (Change it to your channel ID)
DAILY_DIGEST_CHANNEL = "C06XYZ1234"  # 🔹 Replace with your actual Slack channel ID

@app.route("/", methods=["GET"])
def home():
    return "✅ Slack AI Bot (Google Gemini) is Running!"

# Store processed message timestamps to prevent duplicates
processed_messages = set()

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Slack Challenge Verification (for event subscription)
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        event = data["event"]

        # Ignore bot messages
        if event.get("bot_id"):
            return jsonify({"status": "ignored"}), 200  

        # Handle user messages
        if event.get("type") == "message" and "subtype" not in event:
            event_ts = event.get("ts")  # Get unique event timestamp
            if event_ts in processed_messages:
                return jsonify({"status": "duplicate ignored"}), 200  # Ignore duplicate messages
            processed_messages.add(event_ts)

            user_id = event.get("user")  # Extract user ID
            text = event.get("text")
            channel_id = event.get("channel")

            # Fetch user name from Slack API
            user_info = slack_client.users_info(user=user_id)
            user_name = user_info["user"].get("real_name", f"User-{user_id}")

            print(f"\n📝 Captured Message from {user_name}: {text}")
            print(f"💬 Processing message from {user_name}: {text}")

            # Summarize conversation without generating a solution
            summary = summarize_chat(text)
            print(f"✅ Summary: {summary}")  # Print instead of sending to Slack

            # Extract tasks from messages
            task = extract_task(text)
            if task:
                print(f"✅ Task Identified: {task}")
                send_slack_message(channel_id, f"📌 *Task Added:* {task}")

    return jsonify({"status": "ok"}), 200

import time

import spacy

nlp = spacy.load("en_core_web_sm")

def summarize_chat(text):
    """Extracts key phrases from chat messages."""
    try:
        doc = nlp(text)
        keywords = [chunk.text for chunk in doc.noun_chunks]
        return ", ".join(set(keywords))  # Return unique keywords as summary
    except Exception as e:
        print(f"⚠️ Error summarizing chat: {str(e)}")
        return "⚠️ Could not generate summary."


def extract_task(text):
    """Identifies and extracts actionable tasks from Slack messages."""
    keywords = ["task", "action", "to-do", "follow up", "assign"]
    if any(keyword in text.lower() for keyword in keywords):
        return text  # Returns the message as a task if a keyword is found
    return None

# 🔹 Function to fetch and summarize daily messages
def generate_daily_digest():
    try:
        print("📅 Generating Daily Digest...")

        # Get yesterday's timestamp
        yesterday = datetime.now() - timedelta(days=1)
        response = slack_client.conversations_history(channel=DAILY_DIGEST_CHANNEL, oldest=str(yesterday.timestamp()))

        messages = [msg["text"] for msg in response.get("messages", []) if "text" in msg]

        if not messages:
            summary = "No messages to summarize for today."
        else:
            summary_prompt = f"Summarize the key discussions from today in a structured format without generating solutions:\n{messages}"
            response = gemini_model.generate_content(summary_prompt)
            summary = response.text if response and hasattr(response, "text") else "⚠️ Could not generate summary."

        send_slack_message(DAILY_DIGEST_CHANNEL, f"📢 *Daily Digest Summary*\n{summary}")

    except Exception as e:
        print(f"❌ Digest Error: {str(e)}")

# 🔹 Background Task: Run Daily Digest at Midnight
def run_daily_digest():
    while True:
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        time_to_wait = (midnight - now).total_seconds()
        print(f"⏳ Waiting {time_to_wait} seconds until next digest...")

        time.sleep(time_to_wait)
        generate_daily_digest()

# 🔹 Function to send messages to Slack
def send_slack_message(channel, text):
    try:
        slack_client.chat_postMessage(channel=channel, text=text)
        print(f"📩 Sent message: {text}")
    except SlackApiError as e:
        print(f"❌ Error sending message: {e.response['error']}")

import sys
import threading

# Flag to control the loop
running = True

import time
from slack_sdk import WebClient
from slack_sdk.rtm_v2 import RTMClient

SLACK_BOT_TOKEN = "xoxb-8495207468883-8493210135303-wQqs6ho8GLq1I1fDWkJfOpMy"  
client = WebClient(token=SLACK_BOT_TOKEN)

def process_slack_messages(event_data):
    """Handles incoming Slack messages."""
    message = event_data.get("text", "")
    print(f"📩 New Slack Message: {message}")

def start_slack_listener():
    """Continuously listens for Slack messages."""
    print("🔄 Listening for Slack messages...")

    rtm_client = RTMClient(token=SLACK_BOT_TOKEN)
    rtm_client.on(event="message", callback=process_slack_messages)

    # Keep Slack running forever
    while True:
        time.sleep(1)

if __name__ == "__main__":
    # Start the daily digest in the background
    threading.Thread(target=run_daily_digest, daemon=True).start()

    app.run(port=5000, debug=True)
