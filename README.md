# Personalized-AI-Assistant

1. Overview
Objective:
The project develops a Personal AI Communication Assistant to streamline Gmail, Slack, and WhatsApp by prioritizing messages, summarizing chats, and suggesting smart replies. It boosts productivity with automation, reminders, and AI insights, reducing overload and improving workflow.
 Key Problem Statements:
●	Overwhelming Communication Workload – Managing messages across Gmail, Slack, and WhatsApp is time-consuming and inefficient.
●	Inefficient Response Management – Users struggle with drafting replies, tracking follow-ups, and handling repetitive messages.
●	Lack of Cross-Platform Integration – No unified system exists to manage, prioritize, and synchronize messages across platforms.
2. Tools, Libraries, and Frameworks Used
Development & Environment:
●	Python (Primary language)
●	VS Code (Development environment)
●	Git & GitHub (Version control and collaboration)
●	SQLite (Database)
●	Selenium (Automation & Web Interaction)
●	Flask (For API server)
●	Google Gemini AI
●	Google Gmail API
●	Slack API
Libraries Used:
1)	Authentication & Environment Management:
•	os (Handle environment variables)
•	dotenv (Load environment variables from .env files)
•	pickle (Store and retrieve OAuth tokens)

2)	AI & NLP:
•	Transformers (NLP model for summarization)
•	Spacy (NLP model for text processing)
•	sklearn.feature_extraction.text.TfidfVectorizer (Text vectorization for similarity matching)
•	sklearn.metrics.pairwise.cosine_similarity (Compute similarity scores)

3)	Google & Slack Integration:
•	google_auth_oauthlib.flow  (OAuth authentication for Gmail API)
•	google.oauth2.credentials (Manage OAuth tokens)
•	googleapiclient.discovery  (Interact with Gmail API)
•	google.generativeai  (Google Gemini AI for text generation)
•	slack_sdk  (Slack bot integration)
3. Methodology & Approach

1. Gmail Integration (Email Summarization & Reply Suggestions)
•	Methodology:
•	Authenticate using OAuth 2.0 via the Google Gmail API.
•	Fetch emails, extract subject, sender, and body.
•	Process emails using NLP-based summarization and categorize them based on priority.
•	Suggest replies using TF-IDF vectorization and cosine similarity.
•	Approach:
•	Use google-auth, googleapiclient, and sqlite3 for authentication, email retrieval, and tracking.
•	Summarize emails with Hugging Face transformers (BART-Large CNN model).
•	Generate intelligent responses by matching email content with predefined categories using TF-IDF.
•	Store and track unanswered emails in an SQLite database and send reminders.

2. Slack Integration (Message Processing & Task Management)
•	Methodology:
•	Authenticate using Slack API (slack_sdk).
•	Capture real-time user messages and events.
•	Extract important information and identify action items using NLP.
•	Summarize daily discussions and send a digest using Google Gemini AI.
•	Approach:
•	Use Flask to create a webhook endpoint for Slack event handling.
•	Filter out bot messages and process human inputs.
•	Extract key insights from Slack messages using spaCy NLP models.
•	Identify tasks, to-dos, and follow-ups based on keyword analysis.
•	Summarize daily Slack conversations using Google Gemini-Pro API and send structured reports.

3. WhatsApp Automation (AI-based Smart Replies & Chat Summarization)
•	Methodology:
•	Automate WhatsApp Web using Selenium WebDriver.
•	Extract incoming messages and process them with NLP.
•	Generate context-aware replies using a rule-based AI model.
•	Handle basic customer support queries automatically.
•	Approach:
•	Use selenium to detect unread messages, extract text, and simulate user input for automated replies.
•	Utilize spaCy NLP models to identify intents and respond accordingly.
•	Implement a deque-based caching system to prevent duplicate processing of messages.

4. AI Summarization & Reply Generation
•	Methodology:
•	Use transformers (Hugging Face BART) for text summarization.
•	Apply TF-IDF similarity for categorizing emails and generating relevant responses.
•	Integrate Google Gemini AI for structured summaries and intelligent task extraction.
•	Approach:
•	Fine-tune text length constraints in summarization models to keep responses concise.
•	Use predefined response templates to suggest human-like replies.
•	Implement adaptive context analysis to refine AI-driven responses.

5. Task Scheduling & Automation
•	Methodology:
•	Automate daily report generation using background threads.
•	Send unanswered email reminders based on SQLite database tracking.
•	Implement real-time Slack monitoring for extracting actionable insights.
•	Approach:
•	Run Flask API for Slack message handling.
•	Use threading and time to schedule daily digests and email reminders.
•	Store message timestamps to avoid duplicate processing in Slack and WhatsApp.


5. Key Insights & Findings

1. Smart Email Management (Gmail)

 ![image](https://github.com/user-attachments/assets/da5f950a-406b-484e-83c9-e14cbe20d195)

 
 ![image](https://github.com/user-attachments/assets/13dccece-2642-480b-b339-e3ab6b2f2aa3)


 ![image](https://github.com/user-attachments/assets/4ef0a6a2-ded8-437c-822e-25b727f92366)



The screenshots categorizes emails based on urgency (e.g., Urgent, General, Low Priority), generates summaries for each email, and provides suggested replies to streamline communication. Additionally, it tracks unanswered emails and sends reminders for important messages, helping users stay organized and responsive across platforms.

2) Team Communication Optimization (Slack)

 ![image](https://github.com/user-attachments/assets/58d7ca02-f3ca-452f-84f7-7675b27399cb)

 ![image](https://github.com/user-attachments/assets/1f97c1fc-16d8-45ea-ada2-153ca7cda01a)



The first image displays the backend logs, where the bot processes messages, extracts key details, and generates structured summaries.
The second image shows a Slack chat, where a user posts a message about a marketing meeting and a task. The bot detects the task and confirms its addition, demonstrating its ability to extract actionable items.

3) WhatsApp Assistant for Personal & Business Chats

![image](https://github.com/user-attachments/assets/93424c55-6bfe-4c04-9cc0-0fcf4d37ca13)

 

The bot detects a new message from a user and generates a reply based on predefined NLP rules. It continuously checks for new messages, ensuring timely responses. If no unread messages are found, the system waits for a short period before checking again, maintaining an automated and efficient chat experience.

9. Conclusion

In an era of overwhelming digital communication, the Personal AI Communication Assistant steps in as a game-changer, transforming the way we interact with emails and messages. By leveraging AI-driven categorization, summarization, and smart replies, it not only declutters inboxes but also ensures that important messages receive timely attention. The seamless integration of automation and intelligence reduces manual effort, allowing users to focus on what truly matters. With its ability to learn, adapt, and optimize workflows, this assistant doesn’t just manage communication—it redefines efficiency, making productivity effortless and smarter than ever before. ________________________________________

