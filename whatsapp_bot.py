
import os
import time
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from collections import deque

# 🔹 Load API Key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Initialize SQLite Database
conn = sqlite3.connect("whatsapp_chat.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# 🔹 Initialize Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://web.whatsapp.com")

input("🔹 Scan QR Code and press Enter to continue...")

# ✅ Store processed messages efficiently
processed_messages = deque(maxlen=50)

def send_reply(message):
    """Sends a reply in the current chat."""
    try:
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//footer//div[@contenteditable='true']"))
        )
        message_box.send_keys(message)
        time.sleep(1)
        message_box.send_keys(Keys.ENTER)
        print("✅ Reply sent successfully!")
    except Exception as e:
        print(f"⚠️ Error sending reply: {str(e)}")

def send_whatsapp_message(contact, message):
    """Send WhatsApp message to a contact."""
    try:
        print(f"🔍 Searching for contact: {contact}")

        # Locate and enter contact name in search box
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='Search input textbox']"))
        )
        search_box.clear()
        search_box.send_keys(contact)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Allow chat to load

        print("✅ Contact found! Sending message...")
        send_reply(message)  # Use the existing send_reply function
        print(f"📩 Message sent to {contact}: {message}")

    except Exception as e:
        print(f"❌ Error sending message to {contact}: {str(e)}")

def get_unread_chats():
    """Finds unread chats and refreshes elements before accessing."""
    try:
        time.sleep(2)  # Allow elements to fully load
        driver.refresh()  # Ensure the page is up-to-date
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@aria-label, 'unread message')]"))
        )
        return driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
    except Exception as e:
        print(f"⚠️ Error finding unread chats: {str(e)}")
        return []

def get_latest_message():
    """Extracts the latest message and sender name."""
    try:
        time.sleep(2)

        # Extract sender's name
        sender_elements = driver.find_elements(By.XPATH, "//header//span[contains(@class, 'selectable-text')]")
        sender_name = sender_elements[0].text if sender_elements else "Unknown"

        # Extract latest message text
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')]//span[@dir='ltr']")
        if not messages:
            return sender_name, None
        
        last_message = messages[-1].text.strip()
        return sender_name, last_message.encode('utf-8', 'ignore').decode('utf-8')  # Handle special characters

    except Exception as e:
        print(f"⚠️ Error getting latest message: {str(e)}")
        return "Unknown", None

def summarize_text(text):
    """Summarizes long messages using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        summary = model.generate_content(f"Summarize this text: {text}")
        return summary.text if summary else "Summary unavailable."
    except Exception as e:
        return f"⚠️ Summarization Error: {str(e)}"

def generate_ai_response(text):
    """Generates AI-based responses using Gemini."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(text)
        return response.text if response else "I couldn't process your request."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

def handle_chat():
    """Processes incoming messages and replies accordingly."""
    while True:
        unread_chats = get_unread_chats()
        if not unread_chats:
            print("✅ No unread chats found. Waiting...")
            time.sleep(2)
            continue

        for chat in unread_chats:
            try:
                chat.click()
                time.sleep(2)
                sender, message = get_latest_message()
                if not message or message in processed_messages:
                    continue

                processed_messages.append(message)

                print(f"📩 New message from {sender}: {message}")
                cursor.execute("INSERT OR IGNORE INTO chats (sender, message) VALUES (?, ?)", (sender, message))
                conn.commit()

                # Auto-reply logic
                auto_replies = {
                    "hi": "Hello! How can I assist you today? 😊",
                    "hello": "Hi there! Need any help? 🚀",
                    "how are you": "I'm an AI assistant, always ready to help! 🤖"
                }
                if message.lower() in auto_replies:
                    send_reply(auto_replies[message.lower()])
                    continue

                # Summarize long messages
                if len(message) > 100:
                    summarized_text = summarize_text(message)
                    send_reply(f"🔹 Summary: {summarized_text}")
                    continue

                # Customer service queries
                common_questions = {
                    "what are your services?": "We offer AI-powered chat automation, smart replies, and data analytics! 🚀",
                    "how to contact support?": "You can reach us at support@example.com or call +1234567890 📞",
                    "where are you located?": "We are based in Bangalore, India! 🌍"
                }

                for question, answer in common_questions.items():
                    if question in message.lower():
                        send_reply(answer)
                        break
                else:
                    # Generate AI response for other queries
                    ai_response = generate_ai_response(message)
                    send_reply(ai_response)

                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Error processing chat: {str(e)}")
                continue

        print("🔄 Refreshing unread messages list...")
        time.sleep(2)

try:
    while True:
        handle_chat()
        time.sleep(5)
except KeyboardInterrupt:
    print("\n🚀 Bot Stopped. Closing database...")
    conn.close()
    driver.quit()
