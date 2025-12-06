🚨 Real-Time Text Moderation System
AI-Powered Content Filtering using OpenAI Moderation API

This project implements a real-time content moderation system using the OpenAI Moderation API (2024+), designed for chat apps, social platforms, and enterprise communication tools.

It classifies text into harmful categories (hate speech, sexual content, violence, self-harm, scams, etc.) and takes automated actions based on configurable thresholds.

📌 Features

✅ Real-time text moderation (<500ms latency)
✅ Category-wise scoring with thresholds
✅ Auto-block & soft-warning actions
✅ Configurable moderation policy (JSON)
✅ Save test results to CSV
✅ Supports batch moderation
✅ Easy integration with chat frontend (WebSocket optional)

🧠 Tech Stack

Python 3.9+

OpenAI Python SDK

CSV / JSON

(Optional) WebSocket for real-time streaming

📂 Project Structure
.
├── moderation_runner.py
├── moderation_policy.json
├── test_messages.csv
├── results.csv
├── README.md
└── requirements.txt

🔧 Installation
1️⃣ Install Python Packages
pip install openai pandas

2️⃣ Add Your OpenAI API Key
setx OPENAI_API_KEY "your-api-key-here"


or create a .env file:

OPENAI_API_KEY=your-key

⚙️ Moderation Policy (Editable)

moderation_policy.json:

{
  "hate": 0.80,
  "self_harm": 0.70,
  "sexual": 0.80,
  "violence": 0.75,
  "harassment": 0.85,
  "scam": 0.60
}


You can modify thresholds anytime without changing the code.

▶️ Run the Moderation System
python moderation_runner.py


The script will:

✔ Load test messages
✔ Send them to OpenAI Moderation API
✔ Compare results with your thresholds
✔ Apply actions: ALLOW / WARN / BLOCK
✔ Save results to results.csv

🧪 Test Dataset Format

Create test_messages.csv:

message
Hello, how are you?
I will kill you
Click this link to win money: scam.com
You are stupid
Let's have sex tonight
Have a great day!

📊 Output: results.csv
message_text	flagged_categories	confidence_scores	action_taken	response_time_ms
Hello	[]	{}	ALLOW	120
I will kill you	["violence"]	{"violence": 0.92}	BLOCK	160
You are stupid	["harassment"]	{"harassment": 0.76}	WARN	150
💰 Cost Analysis
OpenAI Moderation Endpoint Pricing

(Example — varies by model)

Avg tokens per message: 20  
Cost per 1K tokens: ~$0.05  
10,000 messages = 200,000 tokens  
Estimated monthly cost ≈ $10 – $15

⭐ Future Enhancements

Real-time WebSocket-based moderation

Dashboard for analytics

Multi-language moderation

Integration with mobile apps

Message shadow-banning system

📚 Reference Links

https://platform.openai.com/docs/guides/moderation

https://platform.openai.com/docs/api-reference/moderations
