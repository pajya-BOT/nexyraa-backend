from fastapi import APIRouter
import yfinance as yf
import pandas as pd

router = APIRouter()

SYMBOLS = [
    "TCS", "INFY", "RELIANCE", "ICICIBANK",
    "SBIN", "HDFCBANK", "ITC", "AXISBANK",
    "LT", "BHARTIARTL"
]

def generate_signal(df):
    df["EMA9"] = df["Close"].ewm(span=9).mean()
    df["EMA21"] = df["Close"].ewm(span=21).mean()
    df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))

    latest = df.iloc[-1]
    reasons = []

    if latest["EMA9"] > latest["EMA21"]:
        reasons.append("EMA9 above EMA21 → bullish momentum")
    else:
        reasons.append("EMA9 below EMA21 → weak trend")

    if latest["RSI"] < 70:
        reasons.append("RSI healthy → room for upside")
    else:
        reasons.append("RSI high → risk of pullback")

    # Signal logic
    if latest["EMA9"] > latest["EMA21"] and latest["RSI"] < 70:
        signal = "BUY"
    elif latest["RSI"] > 75:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(90, 60 + len(reasons) * 10)

    return signal, confidence, reasons


@router.get("/scan")
def scan_market():
    results = []

    for s in SYMBOLS:
        try:
            df = yf.Ticker(s + ".NS").history(period="3mo")
            if df.empty:
                continue

            price = round(df["Close"].iloc[-1], 2)

            signal, confidence, reasons = generate_signal(df)

            results.append({
                "symbol": s,
                "price": price,
                "signal": signal,
                "confidence": confidence,
                "target": round(price * 1.05, 2),
                "stoploss": round(price * 0.96, 2),
                "reasons": reasons
            })

        except Exception:
            continue

    return {"top_results": results[:6]}
