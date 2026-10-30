import os
import json
import logging
from typing import Dict, Any, List, Optional
from backend.config import Config

logger = logging.getLogger("crm_engine")

CUSTOMERS_FILE = os.path.join(Config.DATA_DIR, "customers.json")
SAMPLE_CUSTOMERS_FILE = os.path.join(Config.DATA_DIR, "sample_customers.json")

def load_all_customers() -> List[Dict[str, Any]]:
    # Priority: customers.json -> sample_customers.json -> default mock
    target_file = CUSTOMERS_FILE if os.path.exists(CUSTOMERS_FILE) else SAMPLE_CUSTOMERS_FILE
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading customers from {target_file}: {e}")
    
    # Built-in demo customer records
    default_customers = [
        {
            "delivery_phone": "9876543210",
            "primary_name": "Rahul Sharma",
            "all_names": ["Rahul Sharma"],
            "city": "Mumbai",
            "state": "Maharashtra",
            "pin": "400001",
            "account_phones": ["9876543210"],
            "has_different_account": False,
            "total_orders": 2,
            "orders": [
                {
                    "order_id": "ORD-109281",
                    "courier": "Delhivery",
                    "awb": "DEL98234190",
                    "status": "Shipped",
                    "account_phone": "9876543210",
                    "product": {
                        "name": "Men Slim Fit Cotton Casual Shirt",
                        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=300",
                        "price": 499,
                        "status": "Shipped",
                        "courier": "Delhivery",
                        "awb": "DEL98234190",
                        "default_subject": "ship"
                    }
                },
                {
                    "order_id": "ORD-109282",
                    "courier": "Shadowfax",
                    "awb": "SHD4490123",
                    "status": "Out for Delivery",
                    "account_phone": "9876543210",
                    "product": {
                        "name": "Wireless Bluetooth Earbuds Pro",
                        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300",
                        "price": 899,
                        "status": "Out for Delivery",
                        "courier": "Shadowfax",
                        "awb": "SHD4490123",
                        "default_subject": "outofdelivery"
                    }
                }
            ]
        },
        {
            "delivery_phone": "9123456789",
            "primary_name": "Pooja Verma",
            "all_names": ["Pooja Verma"],
            "city": "New Delhi",
            "state": "Delhi",
            "pin": "110001",
            "account_phones": ["9123456789"],
            "has_different_account": False,
            "total_orders": 1,
            "orders": [
                {
                    "order_id": "ORD-204918",
                    "courier": "BlueDart",
                    "awb": "BLU901283",
                    "status": "Delivered",
                    "account_phone": "9123456789",
                    "product": {
                        "name": "Women Floral Printed Anarkali Kurta",
                        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=300",
                        "price": 649,
                        "status": "Delivered",
                        "courier": "BlueDart",
                        "awb": "BLU901283",
                        "default_subject": "delivered_review"
                    }
                }
            ]
        }
    ]
    return default_customers

def search_crm_customers(query: str = "") -> List[Dict[str, Any]]:
    customers = load_all_customers()
    if not query:
        return customers

    q = query.lower().strip()
    clean_q = "".join(c for c in q if c.isdigit())

    matched = []
    for c in customers:
        if clean_q and (clean_q in c["delivery_phone"] or c["delivery_phone"] in clean_q):
            matched.append(c)
            continue
        if any(q in nm.lower() for nm in c.get("all_names", [])):
            matched.append(c)
            continue
        if q in c.get("city", "").lower() or q in c.get("state", "").lower():
            matched.append(c)
            continue
        if any(q in o.get("order_id", "").lower() or q in o.get("awb", "").lower() for o in c.get("orders", [])):
            matched.append(c)
            continue
    return matched

def build_crm_call_payload(
    target_phone: str,
    target_type: str,
    customer_name: str,
    selected_products: List[Dict[str, Any]],
    subject: str = "confirm",
    admin_note: str = "",
    language: str = "hi-IN",
    address_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    address_info = address_info or {}
    city = address_info.get("city", "")
    courier = address_info.get("courier", "Courier Partner")

    total_qty = 0
    total_amt = 0.0

    subject_groups: Dict[str, List[str]] = {}
    all_prod_names = []

    for p in selected_products:
        name = p.get("name") or p.get("product_name") or "Ordered Item"
        short_name = name.split(" - ")[0].split(" | ")[0][:35].strip()
        qty = int(p.get("quantity", 1))
        price = float(p.get("price", 0))
        prod_subj = p.get("subject") or subject or "confirm"

        total_qty += qty
        total_amt += (price * qty)

        item_label = f"{short_name}" if qty == 1 else f"{short_name} ({qty} पीस)"
        all_prod_names.append(item_label)

        if prod_subj not in subject_groups:
            subject_groups[prod_subj] = []
        subject_groups[prod_subj].append(item_label)

    prod_summary_str = ", ".join(all_prod_names) if all_prod_names else "आपका आर्डर"

    base_guardrail = (
        "आप ई-कॉमर्स कस्टमर सपोर्ट के आधिकारिक AI वॉइस कॉल असिस्टेंट हैं। "
        "कठोर नियम 1: केवल विनम्र, सहज, मधुर और आदरणीय हिंदी में बात करें। "
        "कठोर नियम 2: अगर आर्डर प्रीपेड है तो किसी भी तरह की कीमत (Price, Amount) या कैश ऑन डिलीवरी (COD) का कोई जिक्र न करें। "
        "कठोर नियम 3: कभी भी मन से या कल्पना करके कोई गैर-संबंधित प्रोडक्ट न बताएं। "
        "केवल ग्राहक द्वारा चुने गए वास्तविक प्रोडक्ट्स पर ही चर्चा करें। "
        "अगर ग्राहक कोई ऐसा सवाल पूछे जिसका उत्तर आपके पास नहीं है, तो कहें: "
        "'माफ़ कीजिए, मुझे इसकी विस्तृत जानकारी नहीं है। मैं हमारे सपोर्ट एग्जीक्यूटिव को आपका संदेश पहुँचा देता हूँ, वे आपसे जल्द संपर्क करेंगे।'"
    )

    if admin_note:
        base_guardrail += f"\n\n[ADMIN SPECIAL INSTRUCTION]: स्टोर ओनर ने विशेष निर्देश दिया है: '{admin_note}'। इस निर्देश का बातचीत में अनिवार्य रूप से पालन करें।"

    subject_phrases = []
    for s_key, items in subject_groups.items():
        items_text = ", ".join(items)
        if s_key == "confirm":
            subject_phrases.append(f"आपके आर्डर '{items_text}' की पुष्टि (Confirmation) के लिए")
        elif s_key == "outofdelivery":
            subject_phrases.append(f"आपके पार्सल '{items_text}' जो आज डिलीवर होने वाला है उसके संबंध में")
        elif s_key == "delivery_attempt_failed":
            subject_phrases.append(f"आपके पार्सल '{items_text}' की डिलीवरी री-शेड्यूल करने के लिए")
        elif s_key == "ship":
            subject_phrases.append(f"आपके आर्डर '{items_text}' के डिस्पैच व ट्रैकिंग के लिए")
        elif s_key == "cancel":
            subject_phrases.append(f"आपके आर्डर '{items_text}' के कैंसलेशन कारण जानने के लिए")
        elif s_key == "delivered_review":
            subject_phrases.append(f"आपके डिलीवर हुए पार्सल '{items_text}' की क्वालिटी व रेटिंग (1-5 Star) जानने के लिए")
        elif s_key == "exchange":
            subject_phrases.append(f"आपके पार्सल '{items_text}' के एक्सचेंज (Exchange Request) के संबंध में")
        elif s_key == "announcement":
            subject_phrases.append(f"आपके आर्डर '{items_text}' पर नई स्टोर सूचना देने के लिए")
        elif s_key == "promotion":
            subject_phrases.append(f"आपके लिए विशेष ऑफ़र व डिस्काउंट के संबंध में")
        else:
            subject_phrases.append(f"आपके आर्डर '{items_text}' के संबंध में")

    combined_purpose = " और ".join(subject_phrases)

    opening = (
        f"नमस्ते {customer_name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
        f"{combined_purpose} कॉल किया गया है।"
    )

    first_subj = list(subject_groups.keys())[0] if subject_groups else subject
    if first_subj == "confirm":
        opening += " क्या आप इस आर्डर को कन्फर्म करना चाहते हैं? कृपया बताएं।"
    elif first_subj == "outofdelivery":
        opening += " क्या आज आप घर पर डिलीवरी लेने के लिए उपलब्ध हैं?"
    elif first_subj == "delivered_review":
        opening += " आपको प्रोडक्ट कैसा लगा? 1 से 5 स्टार में से आप कितना रेटिंग देना चाहेंगे?"
    elif first_subj == "delivery_attempt_failed":
        opening += " क्या आप डिलीवरी कल के लिए री-शेड्यूल कराना चाहते हैं?"
    elif first_subj == "exchange":
        opening += " आपके पार्सल की एक्सचेंज रिक्वेस्ट स्वीकार कर ली गई है और डिलीवरी पार्टनर जल्द ही आकर पार्सल एक्सचेंज कर देंगे।"

    if admin_note:
        opening += f" {admin_note}"

    primary_purpose_desc = f"{first_subj.replace('_', ' ').title()} ({len(selected_products)} Items)"

    return {
        "opening_text": opening,
        "system_prompt": base_guardrail,
        "purpose_desc": primary_purpose_desc,
        "product_summary": prod_summary_str,
        "total_amount": total_amt,
        "total_count": total_qty,
        "courier": courier,
        "city": city
    }
