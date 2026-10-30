#!/usr/bin/env python3
"""
Example: Triggering an automated AI Order Confirmation Voice Call.
"""
import os
import requests
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def trigger_confirmation_call():
    # 1. Login as Admin
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

    # 2. Dispatch Order Confirmation Call
    payload = {
        "target_phone": "9876543210",
        "customer_name": "Rahul Sharma",
        "selected_products": [
            {
                "name": "Men Slim Fit Cotton Casual Shirt",
                "price": 499,
                "quantity": 1,
                "subject": "confirm"
            }
        ],
        "subject": "confirm",
        "admin_note": "Order is 100% Prepaid. Do not disclose price or ask for COD. Confirm order politely.",
        "language": "hi-IN",
        "city": "Mumbai",
        "courier": "Delhivery",
        "order_number": "ORD-109281"
    }

    print("Dispatching confirmation call...")
    res = requests.post(f"{BASE_URL}/api/admin/voice/crm/dispatch-call", headers=headers, json=payload)
    print("Response Status:", res.status_code)
    print("Response Body:", json.dumps(res.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    trigger_confirmation_call()
