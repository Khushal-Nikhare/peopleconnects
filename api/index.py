"""
Vercel Entry Point for FastAPI Application
"""
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

# Vercel expects the app to be named 'app'
handler = app
