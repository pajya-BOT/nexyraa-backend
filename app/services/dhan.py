import requests
from app.config import DHAN_API_KEY, DHAN_ACCESS_TOKEN

BASE = "https://api.dhan.co/v2"

def get_candles(symbol: str):
    url = f"{BASE}/charts/intraday"

    headers = {
        "client-id": DHAN_API_KEY,
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": symbol.upper(),
        "exchange": "NSE",
        "interval": "15",
        "fromDate": "2024-01-01",
        "toDate": "2026-12-31"
    }

    r = requests.post(url, json=payload, headers=headers, timeout=10)

    if r.status_code != 200:
        raise Exception(r.text)

    return r.json()
