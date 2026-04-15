"""TradeReporter — searches for news around specific buy/sell dates using Gemini."""

import json
from datetime import datetime, timedelta

import google.generativeai as genai
from google.generativeai.types import Tool

from agents.state import AdvisorState, TradeNewsItem
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TRADE_NEWS_QUERIES, TRADE_CLUSTER_DAYS
from agents.prompts.trade_reporter_prompts import (
    TRADE_REPORTER_SYSTEM,
    TRADE_REPORTER_PROMPT,
)


def _parse_json_response(text: str) -> list[dict]:
    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()
    try:
        result = json.loads(cleaned)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def _cluster_trades(transactions: list[dict]) -> list[dict]:
    """Group transactions by stock + date cluster to reduce API calls."""
    clusters: dict[str, list[dict]] = {}

    for tx in transactions:
        stock = tx["stock_code"]
        traded_at = tx["traded_at"]
        try:
            dt = datetime.fromisoformat(traded_at)
        except ValueError:
            continue

        # Find existing cluster for this stock within TRADE_CLUSTER_DAYS
        matched = False
        for key, group in clusters.items():
            if not key.startswith(stock + "|"):
                continue
            ref_dt = datetime.fromisoformat(group[0]["traded_at"])
            if abs((dt - ref_dt).days) <= TRADE_CLUSTER_DAYS:
                group.append(tx)
                matched = True
                break

        if not matched:
            clusters[f"{stock}|{traded_at}"] = [tx]

    # Build cluster summaries
    result = []
    for group in clusters.values():
        first = group[0]
        trades_desc = []
        for tx in group:
            action = "매수" if tx["trade_type"] == "buy" else "매도"
            currency_symbol = "$" if tx.get("currency") == "USD" else ""
            trades_desc.append(
                f"  - {tx['traded_at'][:10]}: {action} {tx['quantity']}주 @ {currency_symbol}{tx['price']:,.0f}"
            )
        result.append({
            "stock_code": first["stock_code"],
            "stock_name": first["stock_name"],
            "market": first.get("market", "KR"),
            "trades": group,
            "description": f"{first['stock_name']} ({first['stock_code']}):\n" + "\n".join(trades_desc),
        })

    return result[:MAX_TRADE_NEWS_QUERIES]


def search_trade_news(state: AdvisorState) -> dict:
    transactions = state.get("transactions", [])
    if not transactions:
        return {"trade_news": []}

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=TRADE_REPORTER_SYSTEM,
    )

    clusters = _cluster_trades(transactions)
    all_trade_news: list[TradeNewsItem] = []

    for cluster in clusters:
        try:
            prompt = TRADE_REPORTER_PROMPT.format(trade_details=cluster["description"])
            response = model.generate_content(
                prompt,
                tools=[Tool(google_search=genai.types.GoogleSearch())],
            )
            items = _parse_json_response(response.text)

            for item in items:
                all_trade_news.append(TradeNewsItem(
                    stock_code=item.get("stock_code", cluster["stock_code"]),
                    stock_name=item.get("stock_name", cluster["stock_name"]),
                    trade_type=item.get("trade_type", ""),
                    traded_at=item.get("traded_at", ""),
                    price=item.get("price", 0),
                    context_summary=item.get("context_summary", ""),
                    key_events=item.get("key_events", []),
                ))
        except Exception as e:
            print(f"[TradeReporter] Error for {cluster['stock_code']}: {e}")
            continue

    return {"trade_news": all_trade_news}
