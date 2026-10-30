import os
import json
import time
import datetime
import logging
import requests
from typing import Dict, Any, List, Optional
from backend.config import Config

logger = logging.getLogger("voice_agent_service")

# Data Storage Paths
SETTINGS_FILE = os.path.join(Config.DATA_DIR, "voice_settings.json")
CALLS_FILE = os.path.join(Config.DATA_DIR, "voice_calls.json")
REVIEWS_FILE = os.path.join(Config.DATA_DIR, "customer_reviews.json")
ESCALATIONS_FILE = os.path.join(Config.DATA_DIR, "voice_escalations.json")
SCHEDULED_FILE = os.path.join(Config.DATA_DIR, "voice_scheduled_calls.json")
LOCKS_FILE = os.path.join(Config.DATA_DIR, "voice_call_locks.json")

def get_default_settings() -> Dict[str, Any]:
    return {
        "sarvam_api_key": Config.SARVAM_API_KEY,
        "sarvam_org_id": Config.SARVAM_ORG_ID,
        "sarvam_workspace_id": Config.SARVAM_WORKSPACE_ID,
        "sarvam_app_id": Config.SARVAM_APP_ID,
        "sarvam_app_version": Config.SARVAM_APP_VERSION,
        "sarvam_connection_id": Config.SARVAM_CONNECTION_ID,
        "sarvam_agent_phone_number": Config.SARVAM_AGENT_PHONE_NUMBER,
        "primary_language": Config.DEFAULT_PRIMARY_LANGUAGE,
        "voice_name": Config.DEFAULT_VOICE_NAME,
        "speaker": Config.DEFAULT_VOICE_NAME,
        "auto_confirmation": False,
        "auto_shipped": False,
        "auto_ofd": False,
        "auto_delivery_review": False,
        "delivery_review_hour": Config.DELIVERY_REVIEW_HOUR,
        "batch_window_minutes": 10,
        "fallback_support_phone": "+918000000000",
        "test_mode": False
    }

def _load_json(file_path: str, default: Any) -> Any:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return default

def _save_json(file_path: str, data: Any):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")

def get_ist_time_str() -> str:
    """Returns current India Standard Time (UTC+5:30) in human readable 12-hour format."""
    ist_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    return ist_time.strftime("%d %b %Y, %I:%M %p")

def get_settings() -> Dict[str, Any]:
    defaults = get_default_settings()
    current = _load_json(SETTINGS_FILE, defaults)
    for k, v in defaults.items():
        if k not in current or (isinstance(current[k], str) and not current[k] and v):
            current[k] = v
    return current

def update_settings(new_settings: Dict[str, Any]) -> Dict[str, Any]:
    current = get_settings()
    current.update(new_settings)
    _save_json(SETTINGS_FILE, current)
    return current

def is_call_locked(phone: str, lock_seconds: int = 120) -> bool:
    locks = _load_json(LOCKS_FILE, {})
    last_time = locks.get(phone, 0)
    return (time.time() - last_time) < lock_seconds

def acquire_call_lock(phone: str):
    locks = _load_json(LOCKS_FILE, {})
    now = time.time()
    locks[phone] = now
    cleaned = {k: v for k, v in locks.items() if (now - v) < 3600}
    _save_json(LOCKS_FILE, cleaned)

# ================= SCRIPT GENERATORS (HINDI, ODIA, ENGLISH) =================
def generate_hindi_script(scenario: str, context: Dict[str, Any]) -> Dict[str, str]:
    name = context.get("customer_name") or "ग्राहक"
    summary = context.get("product_summary_hindi") or "आपका आर्डर"
    courier = context.get("courier_name") or "डिलीवरी पार्टनर"

    guardrail = (
        "आप ई-कॉमर्स कस्टमर सपोर्ट के आधिकारिक AI वॉइस कॉल असिस्टेंट हैं। "
        "कठोर नियम 1: केवल विनम्र, मधुर और आदरणीय हिंदी में बात करें। "
        "कठोर नियम 2: अगर आर्डर प्रीपेड है तो किसी भी तरह की कीमत या कैश ऑन डिलीवरी (COD) का कोई जिक्र न करें। "
        "कठोर नियम 3: कभी भी मन से या कल्पना करके कोई बात न बनाएं। "
        "अगर ग्राहक कोई ऐसा सवाल पूछे जिसका उत्तर आपके पास नहीं है, तो कहें: "
        "'माफ़ कीजिए, मुझे इसकी विस्तृत जानकारी नहीं है। मैं हमारे सपोर्ट एग्जीक्यूटिव को आपका संदेश पहुँचा देता हूँ, वे आपसे जल्द संपर्क करेंगे।'"
    )

    if scenario == "confirm":
        prompt = (
            f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            f"आपके आर्डर '{summary}' की पुष्टि (Confirmation) के लिए कॉल किया गया है। "
            f"क्या आप इस आर्डर को कन्फर्म करना चाहते हैं? कृपया 'हाँ' या 'ना' बताएं।"
        )
    elif scenario == "outofdelivery":
        prompt = (
            f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            f"खुशखबरी! आपका पार्सल '{summary}' आज आपके पते पर डिलीवर होने वाला है। "
            f"क्या आज आप घर पर डिलीवरी लेने के लिए उपलब्ध हैं?"
        )
    elif scenario == "ship":
        prompt = (
            f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            f"आपका आर्डर '{summary}' {courier} कूरियर के माध्यम से डिस्पैच कर दिया गया है।"
        )
    elif scenario == "delivered_review":
        prompt = (
            f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            f"आपके डिलीवर हुए पार्सल '{summary}' का अनुभव जानने के लिए कॉल किया गया है। "
            f"आपको प्रोडक्ट कैसा लगा? 1 से 5 स्टार में से आप कितना रेटिंग देना चाहेंगे?"
        )
    elif scenario == "exchange":
        prompt = (
            f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। "
            f"आपके पार्सल '{summary}' की एक्सचेंज रिक्वेस्ट स्वीकार कर ली गई है। "
            f"डिलीवरी पार्टनर जल्द ही आकर नया पार्सल देकर पुराना पार्सल कलेक्ट कर लेंगे।"
        )
    else:
        prompt = f"नमस्ते {name} जी! मैं कस्टमर केयर से बात कर रही हूँ। आपके आर्डर '{summary}' के संबंध में कॉल किया गया है।"

    return {"opening_text": prompt, "system_prompt": guardrail}

# ================= OUTBOUND CALL DISPATCHER =================
def dispatch_voice_call(
    phone: str,
    scenario: str,
    context: Dict[str, Any],
    force: bool = False
) -> Dict[str, Any]:
    clean_phone = "".join(c for c in str(phone) if c.isdigit())
    if len(clean_phone) == 10:
        clean_phone = f"91{clean_phone}"

    if not force and is_call_locked(clean_phone, lock_seconds=Config.CALL_LOCK_SECONDS):
        logger.warning(f"Call to {clean_phone} debounced (cooldown lock active).")
        return {"status": "debounced", "message": "Call placed recently to this number."}

    acquire_call_lock(clean_phone)
    settings = get_settings()

    target_lang = context.get("language") or settings.get("primary_language", "hi-IN")

    if context.get("custom_opening_text"):
        script_info = {
            "opening_text": context["custom_opening_text"],
            "system_prompt": context.get("custom_system_prompt", "")
        }
        prod_summary = context.get("product_summary_hindi") or "Items"
    else:
        script_info = generate_hindi_script(scenario, context)
        prod_summary = context.get("product_summary_hindi", "Items")

    call_id = f"call_{int(time.time()*1000)}"

    call_record = {
        "call_id": call_id,
        "phone": clean_phone,
        "customer_name": context.get("customer_name", "Customer"),
        "order_number": context.get("order_number", ""),
        "scenario": scenario,
        "language": target_lang,
        "status": "initiated",
        "opening_text": script_info["opening_text"],
        "timestamp": get_ist_time_str(),
        "total_amount": context.get("total_amount", 0),
        "products": prod_summary,
        "outcome": "pending",
        "admin_note": context.get("admin_note", ""),
        "target_type": context.get("target_type", "delivery"),
        "mode": "live" if settings.get("sarvam_api_key") else "simulation"
    }

    # Trigger Sarvam AI Outbound Call
    api_key = settings.get("sarvam_api_key")
    org_id = settings.get("sarvam_org_id", "").strip()
    workspace_id = settings.get("sarvam_workspace_id", "").strip()

    if api_key and org_id and workspace_id:
        try:
            url = f"https://apps.sarvam.ai/api/outbounds/v1/orgs/{org_id}/workspaces/{workspace_id}/outbounds"
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }

            app_id = settings.get("sarvam_app_id") or "salesbot-24888afc-8792"
            app_version = int(settings.get("sarvam_app_version") or 2)
            connection_id = settings.get("sarvam_connection_id") or ""
            agent_phone = settings.get("sarvam_agent_phone_number") or "+918000000000"

            webhook_url = f"{Config.WEBHOOK_BASE_URL}/api/voice/webhook"

            payload = {
                "app_config": {
                    "app_id": app_id,
                    "app_version": app_version,
                    "app_type": "agent",
                    "connection_config": {
                        "connection_id": connection_id,
                        "agent_phone_number": agent_phone
                    },
                    "agent_variables": {
                        "customer_name": str(context.get("customer_name") or "Customer"),
                        "order_id": str(context.get("order_number") or "Order"),
                        "order_amount": "Prepaid" if not context.get("total_amount") else f"Rs {context.get('total_amount')}",
                        "product_details": str(prod_summary or "Products"),
                        "courier_name": str(context.get("courier_name") or "Courier Partner"),
                        "payment_mode": "Prepaid (Paid Online)",
                        "call_purpose": scenario,
                        "call_summary": f"Customer support {scenario} call",
                        "call_disposition": "initiated",
                        "customer_feedback": "",
                        "expected_delivery_date": "Today" if "out" in scenario else "2-3 days",
                        "promotional_offer": "",
                        "rating_score": ""
                    },
                    "app_overrides": {
                        "initial_bot_message": script_info["opening_text"]
                    }
                },
                "user_config": {
                    "user_phone_number": f"+{clean_phone}"
                },
                "webhook_config": {
                    "url": webhook_url,
                    "metadata": {
                        "lead_id": call_id,
                        "scenario": scenario,
                        "phone": clean_phone
                    }
                }
            }

            res = requests.post(url, json=payload, headers=headers, timeout=12)
            if res.status_code in [200, 201, 202]:
                data = res.json()
                call_record["sarvam_call_id"] = data.get("call_id") or data.get("attempt_id") or data.get("id") or ""
                call_record["status"] = "ringing"
                logger.info(f"Sarvam Outbound call initiated to {clean_phone}: {data}")
            else:
                logger.warning(f"Sarvam AI call returned {res.status_code}: {res.text}")
                call_record["status"] = "failed_upstream"
                call_record["error"] = res.text
        except Exception as e:
            logger.error(f"Error calling Sarvam API: {e}")
            call_record["status"] = "error"
            call_record["error"] = str(e)
    else:
        # Simulation Mode (when API keys are not yet configured)
        call_record["status"] = "simulated_success"
        call_record["outcome"] = "ready_for_review"
        logger.info(f"[SIMULATION] Outbound Voice Call to {clean_phone}: {script_info['opening_text']}")

    # Save to call logs
    calls = _load_json(CALLS_FILE, [])
    calls.insert(0, call_record)
    _save_json(CALLS_FILE, calls[:500])

    return call_record

# ================= WEBHOOK PROCESSOR =================
def process_voice_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles live webhooks from Sarvam AI upon call completion.
    Parses attempt_id, duration, multi-turn conversation dialogues, star ratings, and outcomes.
    """
    logger.info(f"Received voice webhook: {json.dumps(payload)[:500]}")

    attempt_id = payload.get("attempt_id") or payload.get("call_id") or payload.get("id")
    sarvam_status = (payload.get("status") or payload.get("event") or "").lower()
    duration = payload.get("duration") or payload.get("call_duration")
    failure_reason = payload.get("failure_reason") or payload.get("error")
    final_vars = payload.get("final_agent_variables") or payload.get("agent_variables") or {}
    webhook_cfg = payload.get("webhook_config") or {}
    meta = webhook_cfg.get("metadata") or payload.get("metadata") or {}

    lead_id = meta.get("lead_id") or meta.get("call_id") or payload.get("call_id") or payload.get("lead_id")
    scenario = meta.get("scenario") or payload.get("scenario", "order_confirmation")
    customer_phone = meta.get("phone") or payload.get("phone") or payload.get("user_phone_number") or ""

    # Parse multi-turn transcript
    raw_transcript_list = payload.get("interaction_transcript") or payload.get("transcript_history")
    formatted_transcript = ""
    if isinstance(raw_transcript_list, list) and raw_transcript_list:
        lines = []
        for t in raw_transcript_list:
            role = str(t.get("role") or "speaker").lower()
            speaker_label = "AI Agent" if (role in ["agent", "bot", "assistant"]) else "Customer"
            txt = t.get("text") or t.get("en_text") or ""
            if txt:
                lines.append(f"{speaker_label}: {txt}")
        formatted_transcript = "\n".join(lines)
    elif payload.get("transcript"):
        formatted_transcript = str(payload.get("transcript"))

    feedback_text = final_vars.get("customer_feedback") or payload.get("feedback") or ""
    star_rating_raw = final_vars.get("rating_score") or payload.get("rating")
    call_disposition = final_vars.get("call_disposition") or payload.get("disposition") or ""

    star_rating = None
    if star_rating_raw:
        try:
            digits = "".join(c for c in str(star_rating_raw) if c.isdigit())
            if digits:
                star_rating = int(digits[0])
        except Exception:
            pass

    call_status = "completed"
    if sarvam_status in ["connected", "completed", "answered"]:
        call_status = "completed"
    elif sarvam_status in ["no_answer", "no-answer", "unanswered"]:
        call_status = "no_answer"
    elif sarvam_status == "busy":
        call_status = "busy"
    elif sarvam_status in ["failed", "error"]:
        call_status = "failed"
    elif sarvam_status:
        call_status = sarvam_status

    # Update in-memory / file call record
    calls = _load_json(CALLS_FILE, [])
    matched = False

    for c in calls:
        if (attempt_id and (c.get("sarvam_call_id") == attempt_id or c.get("call_id") == attempt_id)) or (lead_id and c.get("call_id") == lead_id):
            c["status"] = call_status
            if attempt_id:
                c["sarvam_call_id"] = attempt_id
            if formatted_transcript:
                c["transcript"] = formatted_transcript
            if star_rating is not None:
                c["star_rating"] = star_rating
            if feedback_text:
                c["feedback"] = feedback_text
            if call_disposition:
                c["disposition"] = call_disposition
            if duration is not None:
                c["duration"] = round(float(duration), 1)
            if failure_reason:
                c["error"] = failure_reason
            matched = True
            break

    # Phone fallback match
    if not matched and customer_phone:
        clean_target = "".join(ch for ch in str(customer_phone) if ch.isdigit())[-10:]
        for c in calls:
            c_phone = "".join(ch for ch in str(c.get("phone", "")) if ch.isdigit())[-10:]
            if c_phone == clean_target and c.get("status") in ["ringing", "initiated", "in_progress"]:
                c["status"] = call_status
                if attempt_id:
                    c["sarvam_call_id"] = attempt_id
                if formatted_transcript:
                    c["transcript"] = formatted_transcript
                if star_rating is not None:
                    c["star_rating"] = star_rating
                if feedback_text:
                    c["feedback"] = feedback_text
                if call_disposition:
                    c["disposition"] = call_disposition
                if duration is not None:
                    c["duration"] = round(float(duration), 1)
                matched = True
                break

    if not matched:
        new_entry = {
            "call_id": lead_id or attempt_id or f"call_{int(time.time()*1000)}",
            "sarvam_call_id": attempt_id or "",
            "phone": customer_phone,
            "customer_name": final_vars.get("customer_name") or "Customer",
            "scenario": scenario,
            "status": call_status,
            "duration": round(float(duration), 1) if duration is not None else None,
            "transcript": formatted_transcript,
            "star_rating": star_rating,
            "feedback": feedback_text,
            "timestamp": get_ist_time_str()
        }
        calls.insert(0, new_entry)

    _save_json(CALLS_FILE, calls[:500])

    # Record Customer Review if feedback or rating present
    if star_rating is not None or feedback_text or scenario == "delivered_review":
        rating_val = star_rating if star_rating is not None else 5
        review_item = {
            "review_id": f"rev_{int(time.time()*1000)}",
            "order_number": final_vars.get("order_id") or payload.get("order_number", "Order"),
            "phone": customer_phone,
            "rating": rating_val,
            "feedback": feedback_text or (formatted_transcript[:200] if formatted_transcript else "Call completed."),
            "transcript": formatted_transcript,
            "sentiment": "positive" if rating_val >= 4 else ("neutral" if rating_val == 3 else "negative"),
            "timestamp": get_ist_time_str()
        }
        reviews = _load_json(REVIEWS_FILE, [])
        reviews.insert(0, review_item)
        _save_json(REVIEWS_FILE, reviews)

        # Auto-escalate if rating <= 2 or complaint keywords present
        if rating_val <= 2 or any(w in (feedback_text + formatted_transcript).lower() for w in ["damage", "kharab", "wrong", "broken", "fraud", "complaint"]):
            record_escalation(
                category="damaged_or_wrong_item",
                order_number=review_item["order_number"],
                phone=customer_phone,
                customer_speech=formatted_transcript or feedback_text,
                note=f"Customer gave {rating_val} stars and reported dissatisfaction."
            )

    return {"success": True, "processed": True}

def record_escalation(category: str, order_number: str, phone: str, customer_speech: str, note: str):
    escalation = {
        "id": f"esc_{int(time.time()*1000)}",
        "category": category,
        "order_number": order_number,
        "phone": phone,
        "customer_speech": customer_speech,
        "note": note,
        "status": "pending",
        "timestamp": get_ist_time_str()
    }
    escalations = _load_json(ESCALATIONS_FILE, [])
    escalations.insert(0, escalation)
    _save_json(ESCALATIONS_FILE, escalations)

def get_voice_analytics() -> Dict[str, Any]:
    calls = _load_json(CALLS_FILE, [])
    reviews = _load_json(REVIEWS_FILE, [])
    escalations = _load_json(ESCALATIONS_FILE, [])

    total_calls = len(calls)
    total_reviews = len(reviews)
    ratings = [r.get("rating") for r in reviews if r.get("rating")]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 5.0
    pending_escalations = sum(1 for e in escalations if e.get("status") == "pending")

    return {
        "total_calls": total_calls,
        "total_reviews": total_reviews,
        "average_rating": avg_rating,
        "pending_escalations": pending_escalations
    }

def get_voice_escalations(limit: int = 50) -> List[Dict[str, Any]]:
    return _load_json(ESCALATIONS_FILE, [])[:limit]

def resolve_escalation(escalation_id: str, admin_note: str = "") -> bool:
    escalations = _load_json(ESCALATIONS_FILE, [])
    for e in escalations:
        if e.get("id") == escalation_id:
            e["status"] = "resolved"
            e["resolution_note"] = admin_note
            e["resolved_at"] = get_ist_time_str()
            _save_json(ESCALATIONS_FILE, escalations)
            return True
    return False

def get_customer_reviews(limit: int = 50) -> List[Dict[str, Any]]:
    return _load_json(REVIEWS_FILE, [])[:limit]
