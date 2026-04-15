"""MarketScout — searches for current global & Korean market news using Gemini + Naver."""

import json
import google.generativeai as genai
from google.generativeai.types import Tool

from agents.state import AdvisorState, NewsArticle
from agents.config import GEMINI_API_KEY, GEMINI_MODEL
from agents.prompts.market_scout_prompts import (
    MARKET_SCOUT_SYSTEM,
    MARKET_SCOUT_PROMPT,
    NAVER_SUPPLEMENT_PROMPT,
)
from services.news_scraper import get_stock_news


def _parse_json_response(text: str) -> list[dict]:
    """Extract JSON array from Gemini response (may be wrapped in ```json blocks)."""
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


def search_market_news(state: AdvisorState) -> dict:
    holdings = state.get("holdings", [])
    if not holdings:
        return {"market_news": []}

    genai.configure(api_key=GEMINI_API_KEY)

    all_news: list[NewsArticle] = []

    # 1) Gemini Search Grounding — global & Korean market news
    try:
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction=MARKET_SCOUT_SYSTEM,
        )
        stock_list = "\n".join(
            f"- {h['stock_name']} ({h['stock_code']}, {h['market']})" for h in holdings
        )
        prompt = MARKET_SCOUT_PROMPT.format(stock_list=stock_list)

        response = model.generate_content(
            prompt,
            tools=[Tool(google_search=genai.types.GoogleSearch())],
        )
        articles = _parse_json_response(response.text)
        for a in articles:
            all_news.append(NewsArticle(
                title=a.get("title", ""),
                source=a.get("source", "Gemini Search"),
                date=a.get("date", ""),
                summary=a.get("summary", ""),
                url=a.get("url"),
            ))
    except Exception as e:
        print(f"[MarketScout] Gemini search error: {e}")

    # 2) Naver scraping — Korean stock news supplement
    kr_holdings = [h for h in holdings if h["market"] == "KR"]
    if kr_holdings:
        naver_articles = []
        for h in kr_holdings[:5]:  # limit to 5 stocks
            try:
                articles = get_stock_news(h["stock_code"], days=3, market="KR")
                for a in articles[:3]:  # top 3 per stock
                    naver_articles.append(f"- [{h['stock_name']}] {a['title']} ({a.get('source', '')}, {a.get('date', '')})")
            except Exception:
                continue

        if naver_articles:
            try:
                model = genai.GenerativeModel(GEMINI_MODEL)
                prompt = NAVER_SUPPLEMENT_PROMPT.format(articles="\n".join(naver_articles))
                response = model.generate_content(prompt)
                filtered = _parse_json_response(response.text)
                for a in filtered:
                    all_news.append(NewsArticle(
                        title=a.get("title", ""),
                        source=a.get("source", "네이버 금융"),
                        date=a.get("date", ""),
                        summary=a.get("summary", ""),
                        url=a.get("url"),
                    ))
            except Exception as e:
                print(f"[MarketScout] Naver supplement error: {e}")

    return {"market_news": all_news}
