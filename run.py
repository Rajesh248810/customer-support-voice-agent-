#!/usr/bin/env python3
"""
Entry point to launch the AI Customer Support Voice Agent Backend & Dashboard.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Add backend directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.config import Config

if __name__ == "__main__":
    print(f"[*] Starting AI Customer Support Voice Agent on http://{Config.HOST}:{Config.PORT}")
    print(f"[*] Dashboard URL: http://{Config.HOST}:{Config.PORT}/admin")
    uvicorn.run(
        "backend.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )
