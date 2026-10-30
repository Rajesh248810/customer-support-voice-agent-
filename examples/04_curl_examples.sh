#!/bin/bash
# ==============================================================
# AI Customer Support Voice Agent - cURL Reference Examples
# ==============================================================

BASE_URL="http://localhost:8000"
ADMIN_USER="${ADMIN_USERNAME:-admin}"
ADMIN_PASS="${ADMIN_PASSWORD:-admin}"

# 1. Admin Login (Get Bearer Token)
echo "=== 1. Login ==="
TOKEN=$(curl -s -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$ADMIN_USER\", \"password\": \"$ADMIN_PASS\"}" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

echo "Obtained Token: $TOKEN"

# 2. Search CRM Customers
echo -e "\n=== 2. Search Customers ==="
curl -s -X GET "$BASE_URL/api/admin/voice/crm/customers?q=Rahul" \
  -H "Authorization: Bearer $TOKEN"

# 3. Trigger Outbound Order Confirmation Voice Call
echo -e "\n=== 3. Dispatch Voice Call ==="
curl -s -X POST "$BASE_URL/api/admin/voice/crm/dispatch-call" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_phone": "9876543210",
    "customer_name": "Rahul Sharma",
    "selected_products": [
      {
        "name": "Men Casual Shirt",
        "price": 499,
        "quantity": 1,
        "subject": "confirm"
      }
    ],
    "subject": "confirm",
    "admin_note": "Prepaid order confirmation.",
    "language": "hi-IN"
  }'

# 4. View Real-Time Call Logs with Transcripts and Ratings
echo -e "\n=== 4. View Call Logs ==="
curl -s -X GET "$BASE_URL/api/admin/voice/calls?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 5. View Voice Analytics
echo -e "\n=== 5. View Analytics ==="
curl -s -X GET "$BASE_URL/api/admin/voice/analytics" \
  -H "Authorization: Bearer $TOKEN"
