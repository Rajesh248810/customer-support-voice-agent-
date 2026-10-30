#!/usr/bin/env python3
"""
Example: Triggering an automated AI Exchange / Return Acceptance Voice Call.
"""
import os
import requests
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def trigger_exchange_call():
    login_res = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=10
    )
    token = login_res.json().get("token")
    if not token:
        print("Login failed:", login_res.text)
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "target_phone": "9988776655",
        "customer_name": "Amit Kumar",
        "selected_products": [
            {
                "name": "Men Running Sport Shoes",
                "price": 0,
                "quantity": 1,
                "subject": "exchange"
            }
        ],
        "subject": "exchange",
        "custom_opening_text": (
            "नमस्ते अमित जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            "आपके शूज की एक्सचेंज रिक्वेस्ट स्वीकार कर ली गई है। "
            "हमारी डिलीवरी टीम जल्द ही आपके पते पर आकर नया पार्सल आपको सौंप देगी और पुराना पार्सल कलेक्ट कर लेगी। "
            "यह बिल्कुल फ्री एक्सचेंज है। क्या इस एक्सचेंज को लेकर आपका कोई सवाल है?"
        ),
        "admin_note": "Free exchange accepted. Delivery partner will pickup and handover new parcel simultaneously.",
        "language": "hi-IN",
        "city": "Bengaluru",
        "order_number": "EXC-305819"
    }

    print("Dispatching exchange notification call...")
    res = requests.post(f"{BASE_URL}/api/admin/voice/crm/dispatch-call", headers=headers, json=payload)
    print("Response Status:", res.status_code)
    print("Response Body:", json.dumps(res.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    trigger_exchange_call()
