import json
import yfinance as yf


def safe_parse(raw: str) -> dict:
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    if not clean:
        print("WARNING: Empty response from LLM, using fallback")
        return {
            "verdict": "INCONCLUSIVE", "reason": "Empty response", "confidence": "low",
            "decision": "CONTINUE", "next_focus": "Continue current research",
            "claim": "Unable to form hypothesis", "reasoning": "Empty response",
            "assessment": "FLAWED", "challenged_result": None, "recommendation": "Retry"
        }

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        clean = clean.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            print("WARNING: Failed to parse LLM response as JSON, using fallback")
            return {
                "verdict": "INCONCLUSIVE", "reason": "Failed to parse JSON", "confidence": "low",
                "decision": "CONTINUE", "next_focus": "Continue current research",
                "claim": "Unable to form hypothesis", "reasoning": "Failed to parse JSON",
                "assessment": "FLAWED", "challenged_result": None, "recommendation": "Retry"
            }


def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "current_price": info.get("currentPrice"),
        "pe_ratio": info.get("trailingPE"),
        "revenue_growth": info.get("revenueGrowth"),
        "market_cap": info.get("marketCap"),
        "profit_margins": info.get("profitMargins"),
        "debt_to_equity": info.get("debtToEquity"),
        "return_on_equity": info.get("returnOnEquity"),
        "free_cashflow": info.get("freeCashflow"),
        "earnings_growth": info.get("earningsGrowth")
    }
