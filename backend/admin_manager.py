import json
import os
import time
from typing import Dict, Any, Optional
from jose import jwt
from backend.config import Config

ADMINS_FILE = os.path.join(Config.DATA_DIR, "admins.json")
SETTINGS_FILE = os.path.join(Config.DATA_DIR, "settings.json")

ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days

def _load_admins() -> Dict[str, Any]:
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Initialize from environment
    configured_pass = Config.ADMIN_PASSWORD or "admin"
    default_admin = {
        Config.ADMIN_USERNAME: {
            "username": Config.ADMIN_USERNAME,
            "password": configured_pass,
            "role": "superadmin"
        }
    }
    _save_admins(default_admin)
    return default_admin

def _save_admins(data: Dict[str, Any]):
    try:
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving admins: {e}")

def verify_admin_login(username: str, password: str) -> Optional[str]:
    admins = _load_admins()
    user_record = admins.get(username)
    expected_pass = Config.ADMIN_PASSWORD or "admin"
    if not user_record:
        if username == Config.ADMIN_USERNAME and password == expected_pass:
            return create_admin_token(username)
        return None
    
    if user_record.get("password") == password or (username == Config.ADMIN_USERNAME and password == expected_pass):
        return create_admin_token(username)
    return None

def create_admin_token(username: str) -> str:
    now = time.time()
    payload = {
        "sub": username,
        "role": "admin",
        "iat": int(now),
        "exp": int(now + TOKEN_EXPIRE_SECONDS)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=ALGORITHM)

def verify_admin_token(token: str) -> bool:
    if not token:
        return False
    if token.startswith("Bearer "):
        token = token[7:].strip()
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("role") == "admin"
    except Exception:
        return False
