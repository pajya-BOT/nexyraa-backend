import os
from dotenv import load_dotenv

load_dotenv()

DHAN_API_KEY = os.getenv("DHAN_API_KEY")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not DHAN_API_KEY or not DHAN_ACCESS_TOKEN:
    raise ValueError("API keys not loaded from .env")

BASE_DHAN_URL = "https://api.dhan.co/v2"
