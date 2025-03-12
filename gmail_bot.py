
import os
import sqlite3
import pickle
import base64
import time
import json
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Load Local NLP Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Define OAuth Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Initialize SQLite Database
conn = sqlite3.connect("email_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS unanswered_emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    subject TEXT,
    category TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    reminded INTEGER DEFAULT 0
)
""")
conn.commit()


def authenticate_gmail():
    """✅ Authenticate and return Gmail API service."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def get_email_body(service, msg_id):
    """✅ Extract the email body."""
    try:
        msg = service.users().messages().get(userId="me", id=msg_id).execute()
        payload = msg["payload"]

        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break
        elif "body" in payload and "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

        return body[:1000] if body else "No content available."
    except Exception as e:
        print(f"⚠️ Error fetching email body: {e}")
        return "No content available."


def summarize_email(email_body):
    """✅ Summarize email using a local NLP model."""
    try:
        max_len = max(10, min(len(email_body) // 2, 100))
        return summarizer(email_body, max_length=max_len, min_length=5, do_sample=False)[0]["summary_text"]
    except Exception as e:
        print(f"⚠️ Summarization Error: {e}")
        return "Summary unavailable."


# Predefined responses for context-aware suggestions
response_database = {
    "meeting": ["What time works for you?", "Let’s schedule it.", "Do we need an agenda?"],
    "urgent": ["Got it! I'll handle it ASAP.", "I'll prioritize this.", "I'll get back to you shortly."],
    "invoice": ["Please find the attached invoice.", "I'll check the payment status.", "Can you share the invoice number?"],
    "support": ["How can I assist you?", "Can you provide more details?", "I'll forward this to the support team."],
    "deadline": ["Understood! I'll ensure it's completed on time.", "I'll work on it and update you soon.", "Can you confirm the due date?"],
    "thank you": ["You're welcome!", "Happy to help!", "Glad I could assist!"]
}

# Train TF-IDF model on predefined response categories
queries = list(response_database.keys())
vectorizer = TfidfVectorizer().fit(queries)


def suggest_reply(email_body):
    """✅ Suggest replies using TF-IDF similarity."""
    email_vec = vectorizer.transform([email_body])
    query_vecs = vectorizer.transform(queries)

    # Compute similarity scores
    similarities = cosine_similarity(email_vec, query_vecs).flatten()

    # Get the best matching response
    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]

    # If similarity score is good, return the matching replies
    if best_match_score > 0.3:
        return response_database[queries[best_match_index]]

    # Otherwise, return fallback replies
    return ["Thanks for reaching out!", "I'll check and update you.", "Let me get back to you soon."]


def categorize_email(subject, sender):
    """Categorize an email."""
    urgent_keywords = ["urgent", "immediate", "important", "asap", "action required"]
    follow_up_keywords = ["follow up", "reminder", "update", "check-in"]
    low_priority_keywords = ["newsletter", "promotion", "sale", "discount", "subscription"]

    subject_lower = subject.lower()
    if any(keyword in subject_lower for keyword in urgent_keywords):
        return "Urgent 🚨"
    elif any(keyword in subject_lower for keyword in follow_up_keywords):
        return "Follow-up ⏳"
    elif any(keyword in subject_lower for keyword in low_priority_keywords):
        return "Low Priority 📨"
    else:
        return "General 📩"


def fetch_and_process_emails():
    """Fetch and process emails."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("✅ No new messages.")
        return

    email_data = []

    for msg in messages:
        msg_id = msg["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        email_body = get_email_body(service, msg_id)

        category = categorize_email(subject, sender)
        priority_order = {"Urgent 🚨": 1, "Follow-up ⏳": 2, "General 📩": 3, "Low Priority 📨": 4}
        priority = priority_order.get(category, 3)

        summary = summarize_email(email_body)
        suggested_replies = suggest_reply(email_body)

        email_data.append((priority, category, sender, subject, summary, suggested_replies))

    email_data.sort(key=lambda x: x[0])

    for _, category, sender, subject, summary, suggested_replies in email_data:
        print(f"📩 Category: {category}")
        print(f"🔹 From: {sender}")
        print(f"🔹 Subject: {subject}")
        print(f"📜 Summary: {summary}")
        print("💬 Suggested Replies:")
        for i, reply in enumerate(suggested_replies, 1):
            print(f" {reply}")
        print("\n")

def check_unanswered_emails():
    """Find and track important unanswered emails."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId="me", q="is:unread", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("✅ No unanswered emails.")
        return

    for msg in messages:
        msg_id = msg["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

        category = categorize_email(subject, sender)
        cursor.execute("INSERT INTO unanswered_emails (sender, subject, category) VALUES (?, ?, ?)",
                       (sender, subject, category))
        conn.commit()
        print(f"📩 Unanswered Email Tracked: {subject} from {sender}")

def send_reminders():
    """Send reminders for unanswered emails that are still pending."""
    cursor.execute("SELECT * FROM unanswered_emails WHERE reminded=0")  # Get unreminded emails
    emails = cursor.fetchall()

    if not emails:
        print("✅ No pending reminders.")
        return

    for email in emails:
        email_id, sender, subject, category, timestamp, reminded = email

        reminder_msg = f"🔔 *Reminder: Unanswered Email!*\n🔹 *From:* {sender}\n🔹 *Subject:* {subject}\n🔹 *Category:* {category}\n⏳ Please respond soon."

        # Mark the email as reminded in the database
        cursor.execute("UPDATE unanswered_emails SET reminded=1 WHERE id=?", (email_id,))
        conn.commit()

        print(f"🔔 Reminder for: {subject}")


if __name__ == "__main__":
    fetch_and_process_emails()
    time.sleep(1)
    check_unanswered_emails()
    time.sleep(1)
    send_reminders()  

