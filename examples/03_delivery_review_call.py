#!/usr/bin/env python3
"""
Example: Triggering an automated AI Delivery Rating & Feedback Collection Voice Call.
"""
import os
import requests
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def trigger_review_call():
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
        "target_phone": "9123456789",
        "customer_name": "Pooja Verma",
        "selected_products": [
            {
                "name": "Women Floral Printed Anarkali Kurta",
                "price": 649,
                "quantity": 1,
                "subject": "delivered_review"
            }
        ],
        "subject": "delivered_review",
        "language": "hi-IN",
        "city": "New Delhi",
        "order_number": "ORD-204918"
    }

    print("Dispatching product review and rating call...")
    res = requests.post(f"{BASE_URL}/api/admin/voice/crm/dispatch-call", headers=headers, json=payload)
    print("Response Status:", res.status_code)
    print("Response Body:", json.dumps(res.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    trigger_review_call()
