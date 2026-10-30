import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    SECRET_KEY = os.getenv("SECRET_KEY", "voice_agent_default_secret_key_change_in_production")
    
    # Public Webhook URL where Sarvam AI sends call completion notifications
    WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://your-domain.com").rstrip("/")
    
    # Telephony Provider (Sarvam AI Instant Outbound)
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
    SARVAM_ORG_ID = os.getenv("SARVAM_ORG_ID", "")
    SARVAM_WORKSPACE_ID = os.getenv("SARVAM_WORKSPACE_ID", "")
    SARVAM_APP_ID = os.getenv("SARVAM_APP_ID", "salesbot-24888afc-8792")
    SARVAM_APP_VERSION = int(os.getenv("SARVAM_APP_VERSION", 2))
    SARVAM_CONNECTION_ID = os.getenv("SARVAM_CONNECTION_ID", "")
    SARVAM_AGENT_PHONE_NUMBER = os.getenv("SARVAM_AGENT_PHONE_NUMBER", "+918000000000")
    
    # Voice Defaults
    DEFAULT_VOICE_NAME = os.getenv("DEFAULT_VOICE_NAME", "ritu")
    DEFAULT_PRIMARY_LANGUAGE = os.getenv("DEFAULT_PRIMARY_LANGUAGE", "hi-IN")
    DELIVERY_REVIEW_HOUR = int(os.getenv("DELIVERY_REVIEW_HOUR", 20))
    CALL_LOCK_SECONDS = int(os.getenv("CALL_LOCK_SECONDS", 120))
    
    # Admin Credentials (configured via environment)
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    
    # Data directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(Config.DATA_DIR, exist_ok=True)
