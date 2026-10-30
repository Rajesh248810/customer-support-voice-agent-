# 🎙️ AI Customer Support Voice Agent CRM

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Sarvam AI](https://img.shields.io/badge/Telephony-Sarvam%20AI-pink.svg)](https://apps.sarvam.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

An enterprise-ready, open-source **Automated Outbound & Inbound AI Voice Agent CRM** designed for e-commerce stores, D2C brands, and logistics companies. Powered by **Sarvam AI Telephony**, this platform automates real phone calls to customers for **order confirmations, delivery tracking, exchange pickups, and post-delivery review collections with live audio transcripts and 1-5 star ratings**.

---

## 🚀 Key Highlights & Capabilities

- 🤖 **Natural Indian Voice Agents**: Lifelike female and male voices (e.g. `Ritu`, `Subha`, `Ananya`) speaking natural, polite conversational Hindi, Odia, and Indian English.
- 📦 **Multi-Scenario Automated Outbound Workflows**:
  - **Order Confirmation**: Verifies high-risk orders, multi-item baskets, and reduces RTO (Return to Origin).
  - **Out for Delivery (OFD)**: Alerts customers on delivery morning to ensure availability.
  - **Exchange / Return Acceptance**: Notifies customers of approved exchanges with simultaneous pickup instructions.
  - **Order Review & Rating**: Automatically calls delivered orders to collect 1-5 star ratings and audio feedback.
  - **Reschedule Attempt**: Reaches out when courier delivery attempt fails.
  - **Store Announcements & Deal Alerts**: Informs VIP customers of exclusive promotions.
- 💬 **Live Multi-Turn Transcript Renderer**: Displays dialogue turns in clean chat bubbles (`AI Agent` in pink, `Customer` in emerald) with exact call duration.
- ⭐ **Customer Sentiment & Rating Dashboard**: Tracks average star ratings, customer feedback quotes, and escalates dissatisfied customers (`<= 2 stars`) to an admin escalation queue.
- 🛡️ **Anti-Hallucination & Anti-Leak Guardrails**: Strict instructions preventing AI from disclosing dummy prices or asking for cash on prepaid orders.
- 🎛️ **Interactive Outbound Calling Studio**:
  - Live customer directory search by phone, name, or order ID.
  - Per-item scenario dropdown selector (e.g. Product A for exchange, Product B for rating).
  - Direct target number dialer (dial any number instantly).
  - Live Dynamic Speech Preview (updates in real-time as you type notes).
- ⚙️ **Hot-Swappable Telephony Settings**: Switch Sarvam AI API keys, Org IDs, Workspace IDs, and Caller IDs directly from the web dashboard UI without restarting the server!

---

## 🏗️ System Architecture & Workflow

```mermaid
flowchart TD
    Admin["Admin / CRM System"] -->|1. Trigger Call / Dispatch API| Backend["FastAPI Voice Backend"]
    Backend -->|2. Construct Prompt & Guardrails| Sarvam["Sarvam AI Telephony API"]
    Sarvam -->|3. Place Live Phone Call| Customer["Customer Mobile Phone (+91)"]
    Customer <-->|4. 2-Way Speech Interaction (Voice: Ritu)| Sarvam
    Sarvam -->|5. POST Webhook /api/voice/webhook| Backend
    Backend -->|6. Parse Transcripts, Stars & Sentiment| DB[("JSON / SQLite Storage")]
    DB -->|7. Real-Time Auto-Polling| Dashboard["Live Studio & Call Logs Dashboard"]
```

---

## 📁 Repository Structure

```
customer-support-voice-agent/
├── backend/
│   ├── config.py              # Environment configuration & safe defaults
│   ├── main.py                # FastAPI REST API & Webhook endpoints
│   ├── voice_agent_service.py # Sarvam AI Outbound caller & webhook parser
│   ├── crm_engine.py          # Universal customer CRM & dynamic speech generator
│   └── admin_manager.py       # JWT auth & settings manager
├── frontend/
│   └── index.html             # Full enterprise dark-mode CRM & Studio Dashboard
├── data/
│   ├── sample_customers.json  # Pre-seeded mock e-commerce customer data
│   └── .gitkeep
├── examples/
│   ├── 01_order_confirmation_call.py
│   ├── 02_exchange_pickup_call.py
│   ├── 03_delivery_review_call.py
│   └── 04_curl_examples.sh
├── .env.example               # Clean configuration template
├── .gitignore                 # Prevents committing secrets or live call data
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
├── run.py                     # One-click startup script
└── README.md                  # Comprehensive documentation
```

---

## ⚡ 5-Minute Quickstart

### 1. Clone & Setup Virtual Environment

```bash
git clone https://github.com/Rajesh248810/customer-support-voice-agent-.git
cd customer-support-voice-agent-

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
HOST=0.0.0.0
PORT=8000
SECRET_KEY=generate_a_secure_random_32_character_secret_key

# Your Public Domain or Tunnel URL (where Sarvam AI can reach your webhook)
WEBHOOK_BASE_URL=https://your-domain.com

# Sarvam AI Credentials (from https://apps.sarvam.ai/)
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_ORG_ID=your_org_id_here
SARVAM_WORKSPACE_ID=your_workspace_id_here
SARVAM_APP_ID=salesbot-24888afc-8792
SARVAM_APP_VERSION=2
SARVAM_CONNECTION_ID=your_connection_id_here
SARVAM_AGENT_PHONE_NUMBER=+918064267640

# Dashboard Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password_here
```

> [!NOTE]
> If you don't have Sarvam AI keys yet, the system automatically starts in **Simulation Mode**, allowing you to test the dashboard, customer search, call dispatching, and transcript UI immediately without incurring telephony costs!

### 3. Launch the Server

```bash
python run.py
```

Open your browser and navigate to:
👉 **`http://localhost:8000/admin`**  
*(Default Login: Username: `admin` | Password: configured in your `.env`)*

---

## 🐳 Docker Deployment

Run with a single command using Docker Compose:

```bash
docker compose up -d --build
```

View live logs:
```bash
docker compose logs -f
```

---

## 🔑 Sarvam AI Telephony Setup Guide

To connect live real-world phone calling:

1. Sign up on **[Sarvam AI Platform](https://apps.sarvam.ai/)**.
2. **Create an Agent**:
   - Go to **Agents** -> Create Agent (e.g. `salesbot`).
   - Select Voice: **Ritu** (Female Hindi) or your preferred voice.
   - Copy the **App ID** (e.g. `salesbot-24888afc-8792`) and note the version (e.g. `2`).
3. **Setup Telephony Connection**:
   - Go to **Connections / Telephony**.
   - Generate your outbound phone number (e.g. `+918064267640`) and copy the **Connection ID**.
4. **Copy API Credentials**:
   - Go to **Settings / Workspace Settings**.
   - Copy your **API Key**, **Organization ID**, and **Workspace ID**.
5. **Paste into Dashboard**:
   - Open your Dashboard (`/admin`) -> Click **Settings** (slider icon on top right).
   - Paste the credentials and click **Save Settings**!

---

## 🔗 Webhook & Multi-Turn Transcript Parsing

When a call completes, Sarvam AI sends an HTTP POST webhook to:
`https://your-domain.com/api/voice/webhook`

### Sample Webhook Payload Received from Sarvam:
```json
{
  "attempt_id": "attempt_98124901",
  "status": "connected",
  "duration": 24.5,
  "final_agent_variables": {
    "customer_name": "Satyajit",
    "order_id": "ORD-109281",
    "rating_score": "5",
    "customer_feedback": "Product quality is very good!",
    "call_disposition": "completed"
  },
  "interaction_transcript": [
    {"role": "agent", "text": "नमस्ते सत्यजीत जी! मैं कस्टमर केयर से बात कर रही हूँ। आपके आर्डर की पुष्टि के लिए कॉल किया गया है।"},
    {"role": "user", "text": "हाँ नमस्ते, आर्डर कन्फर्म है।"},
    {"role": "agent", "text": "बहुत धन्यवाद! आपका पार्सल जल्द ही डिस्पैच कर दिया जाएगा।"}
  ],
  "webhook_config": {
    "metadata": {
      "lead_id": "call_1791111236312",
      "phone": "919876543210"
    }
  }
}
```

The backend automatically parses speaker tags, assigns star ratings, logs sentiment, and streams updates directly to the **Live Call Logs Table**.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/admin/login` | Authenticate admin & get JWT token | No |
| `POST` | `/api/voice/webhook` | Receives Sarvam call completion webhooks | No |
| `GET` | `/api/admin/voice/crm/customers` | Search & list customer order profiles | Yes (Bearer) |
| `POST` | `/api/admin/voice/crm/dispatch-call`| Trigger outbound AI voice call | Yes (Bearer) |
| `GET` | `/api/admin/voice/calls` | Fetch real-time call logs & transcripts | Yes (Bearer) |
| `GET` | `/api/admin/voice/analytics` | View total calls, avg rating, escalations| Yes (Bearer) |
| `GET` | `/api/admin/voice/settings` | Get active telephony settings | Yes (Bearer) |
| `POST` | `/api/admin/voice/settings` | Update telephony settings dynamically | Yes (Bearer) |
| `GET` | `/api/admin/voice/escalations` | List customer complaint escalations | Yes (Bearer) |
| `POST` | `/api/admin/voice/resolve-escalation`| Resolve a customer complaint | Yes (Bearer) |

---

## 🔒 Security Best Practices

> [!CAUTION]
> **Never commit your `.env` file or real API keys to version control!**
> - The `.gitignore` in this repository is strictly configured to ignore `.env`, `*.key`, `*.pem`, and dynamic call logs in `data/`.
> - Always use environment variables in production.
> - Set a strong admin password in your `.env` before deploying to a public VPS.

---

## 🌐 Production VPS Deployment (Nginx + Systemd)

1. **Create a Systemd Service** (`/etc/systemd/system/voice_agent.service`):
```ini
[Unit]
Description=AI Customer Support Voice Agent
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/customer-support-voice-agent
ExecStart=/var/www/customer-support-voice-agent/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

2. **Configure Nginx Reverse Proxy** (`/etc/nginx/sites-available/voice_agent`):
```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable SSL**:
```bash
certbot --nginx -d your-domain.com
systemctl restart voice_agent
systemctl restart nginx
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
