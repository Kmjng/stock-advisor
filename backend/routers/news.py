from fastapi import APIRouter, Query

from services.news_scraper import get_stock_news

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/{stock_code}")
def get_news(stock_code: str, days: int = Query(default=7, le=30)):
    articles = get_stock_news(stock_code, days=days)
    return {"stock_code": stock_code, "count": len(articles), "articles": articles}
