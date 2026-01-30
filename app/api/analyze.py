from fastapi import APIRouter
import yfinance as yf
import pandas as pd
import numpy as np

router = APIRouter()

# -------------------------
# Indicator calculations
# -------------------------
def add_indicators(df):
    df["EMA9"] = df["Close"].ewm(span=9).mean()
    df["EMA21"] = df["Close"].ewm(span=21).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Volume_Avg"] = df["Volume"].rolling(20).mean()

    return df


# -------------------------
# Core logic (Entry + Trap + Reasons)
# -------------------------
def generate_signal(df):
    df = add_indicators(df)
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    reasons = []
    traps = []
    confidence = 50

    ema9 = latest["EMA9"]
    ema21 = latest["EMA21"]
    rsi = latest["RSI"]
    volume = latest["Volume"]
    avg_volume = latest["Volume_Avg"]

    # ---------------- TREND ----------------
    if ema9 > ema21:
        reasons.append(f"EMA9 ({ema9:.2f}) above EMA21 ({ema21:.2f}) → bullish trend")
        confidence += 15
    else:
        reasons.append(f"EMA9 ({ema9:.2f}) below EMA21 ({ema21:.2f}) → weak trend")

    # ---------------- MOMENTUM ----------------
    if 40 < rsi < 65:
        reasons.append(f"RSI {rsi:.2f} → healthy momentum")
        confidence += 15
    elif rsi > 70:
        traps.append(f"RSI {rsi:.2f} → overbought (bull trap risk)")
    elif rsi < 30:
        reasons.append(f"RSI {rsi:.2f} → oversold bounce possible")

    # ---------------- VOLUME CONFIRMATION ----------------
    if volume > avg_volume:
        reasons.append("Volume higher than average → breakout confirmation")
        confidence += 20
    else:
        traps.append("Low volume → breakout may fail")

    # ---------------- PRICE STRUCTURE ----------------
    if latest["Close"] > prev["Close"]:
        confidence += 10

    # ---------------- FINAL SIGNAL ----------------
    if confidence >= 75 and len(traps) == 0:
        signal = "BUY"
    elif confidence < 55 or len(traps) >= 2:
        signal = "SELL"
    else:
        signal = "HOLD"

    return signal, min(confidence, 95), reasons, traps, {
        "EMA9": round(ema9, 2),
        "EMA21": round(ema21, 2),
        "RSI": round(rsi, 2),
        "Volume": int(volume),
        "AvgVolume": int(avg_volume)
    }


# -------------------------
# Symbol fetch (NSE + BSE fallback)
# -------------------------
def fetch_stock(symbol):
    df = yf.Ticker(symbol + ".NS").history(period="3mo")
    if not df.empty:
        return df, symbol + ".NS"

    df = yf.Ticker(symbol + ".BO").history(period="3mo")
    if not df.empty:
        return df, symbol + ".BO"

    return None, None


# -------------------------
# API endpoint
# -------------------------
@router.get("/analyze")
def analyze(stock: str):
    symbol = stock.upper().replace(" ", "").strip()

    try:
        df, final_symbol = fetch_stock(symbol)

        if df is None:
            return {"error": "Invalid stock symbol"}

        price = round(df["Close"].iloc[-1], 2)

        signal, confidence, reasons, traps, indicators = generate_signal(df)

        # Smart risk-reward
        if signal == "BUY":
            target = round(price * 1.06, 2)
            stoploss = round(price * 0.97, 2)
        elif signal == "SELL":
            target = round(price * 0.95, 2)
            stoploss = round(price * 1.03, 2)
        else:
            target = round(price * 1.02, 2)
            stoploss = round(price * 0.99, 2)

        return {
            "symbol": final_symbol,
            "price": price,
            "signal": signal,
            "confidence": confidence,
            "target": target,
            "stoploss": stoploss,
            "reasons": reasons,
            "traps": traps,
            "indicators": indicators
        }

    except:
        return {"error": "Invalid stock symbol"}
