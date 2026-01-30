import pandas as pd

def advanced_analysis(df):
    close = df["Close"]
    high = df["High"]
    volume = df["Volume"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    last = df.iloc[-1]

    price = last["Close"]
    prev_high = high.iloc[-10:-1].max()

    # -------- Trap Detector ----------
    if price > prev_high and volume.iloc[-1] < volume.rolling(20).mean().iloc[-1]:
        trap = "⚠️ Possible Bull Trap"
    elif price < ema50.iloc[-1] and volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]:
        trap = "⚠️ Possible Bear Trap"
    else:
        trap = "No trap detected"

    # -------- Entry Timing ----------
    if price > ema20.iloc[-1] and price > ema50.iloc[-1]:
        entry = f"Buy on pullback near ₹{round(ema20.iloc[-1],2)}"
    elif price < ema20.iloc[-1]:
        entry = f"Wait for breakout above ₹{round(prev_high,2)}"
    else:
        entry = "Avoid trade for now"

    # -------- Health Score ----------
    score = 0
    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 30
    if price > ema20.iloc[-1]:
        score += 25
    if volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]:
        score += 20
    if df["Close"].pct_change().std() < 0.02:
        score += 25

    score = min(100, score)

    return trap, entry, score
