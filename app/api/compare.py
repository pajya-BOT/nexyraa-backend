from fastapi import APIRouter
import yfinance as yf

router = APIRouter()

# 🔥 FIX: clean user input like "tata power" -> "TATAPOWER"
def clean_symbol(symbol: str):
    return symbol.upper().replace(" ", "").replace("-", "")

def get_metrics(symbol):
    symbol = clean_symbol(symbol)
    ticker = yf.Ticker(symbol + ".NS")

    info = ticker.info
    hist = ticker.history(period="1y")

    if hist.empty:
        return None

    price = round(hist["Close"][-1], 2)
    return_1y = round(((hist["Close"][-1] / hist["Close"][0]) - 1) * 100, 2)

    roe = round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else 0
    debt = round(info.get("debtToEquity", 0), 2)
    pe = round(info.get("trailingPE", 0), 2)
    growth = round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else 0

    score = 0
    reasons = []

    if roe > 15:
        score += 20
        reasons.append("Strong ROE")

    if debt < 80:
        score += 15
        reasons.append("Low Debt")

    if growth > 10:
        score += 20
        reasons.append("Good Revenue Growth")

    if return_1y > 15:
        score += 20
        reasons.append("Strong Price Performance")

    if pe < 30:
        score += 10
        reasons.append("Reasonable Valuation")

    return {
        "price": price,
        "1Y Return %": return_1y,
        "ROE %": roe,
        "Debt/Equity": debt,
        "PE Ratio": pe,
        "Revenue Growth %": growth,
        "Score": score,
        "reasons": reasons
    }


@router.get("/compare")
def compare(stock1: str, stock2: str):

    s1 = clean_symbol(stock1)
    s2 = clean_symbol(stock2)

    data1 = get_metrics(s1)
    data2 = get_metrics(s2)

    if not data1 or not data2:
        return {"error": "Invalid stock symbols"}

    winner = s1 if data1["Score"] > data2["Score"] else s2

    conclusion = (
        f"{winner} looks stronger overall based on better fundamentals, growth and performance."
    )

    return {
        "stocks": {
            s1: data1,
            s2: data2
        },
        "winner": winner,
        "conclusion": conclusion,
        "disclaimer": "This is data-based analysis, not financial advice."
    }
