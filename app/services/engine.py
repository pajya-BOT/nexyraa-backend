import yfinance as yf
import pandas_ta as ta
import pandas as pd

# ===============================
# CONFIG
# ===============================
MIN_CANDLES = 150

TOP_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "SBIN.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "ITC.NS"
]


# ===============================
# SAFE DATA FETCH
# ===============================
def fetch_data(ticker: str):
    try:
        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return None

        # Fix MultiIndex bug
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if len(df) < MIN_CANDLES:
            return None

        return df

    except Exception as e:
        print(f"[fetch_data error] {ticker}: {e}")
        return None


# ===============================
# CORE ANALYSIS
# ===============================
def analyze_stock(symbol: str):
    try:
        ticker = symbol.upper()
        if not ticker.endswith(".NS"):
            ticker += ".NS"

        df = fetch_data(ticker)

        if df is None:
            return {"symbol": symbol, "signal": "WAIT", "error": "No data"}

        # Indicators
        df["EMA20"] = ta.ema(df["Close"], 20)
        df["EMA50"] = ta.ema(df["Close"], 50)
        df["EMA200"] = ta.ema(df["Close"], 200)
        df["RSI"] = ta.rsi(df["Close"], 14)
        df["ATR"] = ta.atr(df["High"], df["Low"], df["Close"], 14)

        df = df.dropna()

        if df.empty:
            return {"symbol": symbol, "signal": "WAIT", "error": "Indicators not ready"}

        last = df.iloc[-1]

        price = float(last["Close"])
        ema20 = float(last["EMA20"])
        ema50 = float(last["EMA50"])
        ema200 = float(last["EMA200"])
        rsi = float(last["RSI"])
        atr = float(last["ATR"])

        # ======================
        # LOGIC
        # ======================
        score = 50
        reasons = []

        if price > ema200:
            score += 10
            reasons.append("Above EMA200")

        if ema20 > ema50:
            score += 10
            reasons.append("EMA20 > EMA50")

        if 35 < rsi < 55:
            score += 10
            reasons.append("Healthy RSI")

        if rsi < 35:
            score += 5
            reasons.append("Oversold bounce zone")

        # Final signal
        if score >= 70:
            signal = "BUY"
        elif score <= 40:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol": symbol.upper(),
            "price": round(price, 2),
            "signal": signal,
            "confidence": score,
            "stoploss": round(price - atr * 1.5, 2),
            "target": round(price + atr * 2, 2),
            "reasons": reasons
        }

    except Exception as e:
        print("[analyze error]", e)
        return {"symbol": symbol, "signal": "ERROR", "error": str(e)}


# ===============================
# SCANNER
# ===============================
def scan_top_stocks():
    results = []

    for stock in TOP_STOCKS:
        res = analyze_stock(stock)

        if res and res.get("signal") in ["BUY", "HOLD"]:
            results.append(res)

    results = sorted(results, key=lambda x: x.get("confidence", 0), reverse=True)

    return {
        "count": len(results),
        "top_results": results[:10]
    }
