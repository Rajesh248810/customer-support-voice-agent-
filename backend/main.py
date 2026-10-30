import os
import json
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import Config
from backend import admin_manager
from backend import voice_agent_service
from backend import crm_engine

app = FastAPI(
    title="AI Customer Support Voice Agent",
    description="Enterprise-grade AI Voice Agent for e-commerce order confirmation, delivery alerts, exchange pickups, and reviews.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(Config.BASE_DIR, "frontend")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Auth Dependency
def get_current_admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Admin token required")
    if not admin_manager.verify_admin_token(authorization):
        raise HTTPException(status_code=403, detail="Invalid or expired admin session")
    return True

# Request Schemas
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class VoiceSettingsRequest(BaseModel):
    sarvam_api_key: Optional[str] = None
    sarvam_org_id: Optional[str] = None
    sarvam_workspace_id: Optional[str] = None
    sarvam_app_id: Optional[str] = None
    sarvam_connection_id: Optional[str] = None
    sarvam_agent_phone_number: Optional[str] = None
    primary_language: Optional[str] = "hi-IN"
    delivery_review_hour: Optional[int] = 20

class CrmDispatchCallRequest(BaseModel):
    target_phone: str
    target_type: str = "delivery"
    customer_name: str
    selected_products: List[Dict[str, Any]] = []
    subject: str = "confirm"
    admin_note: Optional[str] = ""
    language: Optional[str] = "hi-IN"
    city: Optional[str] = ""
    courier: Optional[str] = ""
    awb: Optional[str] = ""
    order_number: Optional[str] = ""
    custom_opening_text: Optional[str] = ""

class ResolveEscalationRequest(BaseModel):
    escalation_id: str
    admin_note: Optional[str] = ""

# ================= AUTH ENDPOINTS =================
@app.post("/api/admin/login")
def admin_login(req: AdminLoginRequest):
    token = admin_manager.verify_admin_login(req.username, req.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"success": True, "token": token, "username": req.username}

# ================= SARVAM AI VOICE WEBHOOK =================
@app.post("/api/voice/webhook")
async def voice_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return voice_agent_service.process_voice_webhook(payload)

# ================= VOICE CRM DISPATCH & CALLS =================
@app.get("/api/admin/voice/crm/customers")
def admin_crm_customers(q: Optional[str] = "", is_admin = Depends(get_current_admin)):
    customers = crm_engine.search_crm_customers(q or "")
    return {"success": True, "customers": customers, "total": len(customers)}

@app.post("/api/admin/voice/crm/dispatch-call")
def admin_crm_dispatch_call(req: CrmDispatchCallRequest, is_admin = Depends(get_current_admin)):
    prompt_data = crm_engine.build_crm_call_payload(
        target_phone=req.target_phone,
        target_type=req.target_type,
        customer_name=req.customer_name,
        selected_products=req.selected_products,
        subject=req.subject,
        admin_note=req.admin_note or "",
        language=req.language or "hi-IN",
        address_info={"city": req.city, "courier": req.courier}
    )
    first_oid = req.selected_products[0].get("order_id") if req.selected_products else f"ORD{int(time.time())}"
    context = {
        "customer_name": req.customer_name,
        "order_number": req.order_number if req.order_number is not None else first_oid,
        "total_amount": prompt_data["total_amount"],
        "product_summary_hindi": prompt_data["product_summary"],
        "language": req.language or "hi-IN",
        "courier_name": req.courier or prompt_data["courier"],
        "tracking_id": req.awb or "",
        "custom_opening_text": req.custom_opening_text or prompt_data["opening_text"],
        "custom_system_prompt": prompt_data["system_prompt"],
        "admin_note": req.admin_note or "",
        "target_type": req.target_type
    }
    return voice_agent_service.dispatch_voice_call(
        phone=req.target_phone,
        scenario=req.subject,
        context=context,
        force=True
    )

@app.get("/api/admin/voice/calls")
def admin_voice_calls(limit: int = 50, is_admin = Depends(get_current_admin)):
    calls = voice_agent_service._load_json(voice_agent_service.CALLS_FILE, [])
    clean_calls = [c for c in calls if (c.get("phone") or c.get("customer_name") != "Customer") and c.get("status") != "ping"]
    def get_sort_key(c):
        cid = str(c.get("call_id") or "")
        digits = "".join(ch for ch in cid if ch.isdigit())
        if digits and len(digits) >= 10:
            try:
                return int(digits)
            except Exception:
                pass
        return 0
    try:
        clean_calls.sort(key=get_sort_key, reverse=True)
    except Exception:
        pass
    return clean_calls[:limit]

@app.get("/api/admin/voice/analytics")
def admin_voice_analytics(is_admin = Depends(get_current_admin)):
    return voice_agent_service.get_voice_analytics()

@app.get("/api/admin/voice/reviews")
def admin_voice_reviews(limit: int = 50, is_admin = Depends(get_current_admin)):
    return voice_agent_service.get_customer_reviews(limit=limit)

@app.get("/api/admin/voice/escalations")
def admin_voice_escalations(limit: int = 50, is_admin = Depends(get_current_admin)):
    return voice_agent_service.get_voice_escalations(limit=limit)

@app.post("/api/admin/voice/resolve-escalation")
def admin_voice_resolve_escalation(req: ResolveEscalationRequest, is_admin = Depends(get_current_admin)):
    res = voice_agent_service.resolve_escalation(req.escalation_id, req.admin_note)
    return {"success": res}

@app.get("/api/admin/voice/settings")
def admin_voice_get_settings(is_admin = Depends(get_current_admin)):
    return voice_agent_service.get_settings()

@app.post("/api/admin/voice/settings")
def admin_voice_update_settings(req: VoiceSettingsRequest, is_admin = Depends(get_current_admin)):
    data = req.dict(exclude_unset=True)
    return voice_agent_service.update_settings(data)

# ================= DASHBOARD ROUTE =================
@app.get("/")
@app.get("/admin")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AI Customer Support Voice Agent Backend Online"}
