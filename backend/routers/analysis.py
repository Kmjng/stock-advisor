import json
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Portfolio, Market, AnalysisResult
from services.news_scraper import get_stock_news
from services.ai_analyzer import analyze_stock_news

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/saved")
def get_saved_analysis(db: Session = Depends(get_db)):
    """Return the most recent saved analysis result."""
    result = db.query(AnalysisResult).order_by(AnalysisResult.analysis_date.desc()).first()
    if not result:
        return {"status": "empty", "results": [], "saved_at": None}
    return {
        "status": "ok",
        "results": json.loads(result.results_json),
        "saved_at": result.updated_at.isoformat() if result.updated_at else result.created_at.isoformat(),
        "analysis_date": result.analysis_date.isoformat(),
    }


@router.get("/{stock_code}")
def analyze_single(stock_code: str):
    articles = get_stock_news(stock_code, days=7)
    result = analyze_stock_news("", stock_code, articles)
    return {
        "stock_code": stock_code,
        "news_count": len(articles),
        "analysis": result,
    }


@router.get("/")
def analyze_all(
    market: Optional[Market] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Portfolio)
    if market:
        query = query.filter(Portfolio.market == market)
    stocks = query.all()

    results = []
    for stock in stocks:
        articles = get_stock_news(stock.stock_code, days=7, market=stock.market.value)
        analysis = analyze_stock_news(stock.stock_name, stock.stock_code, articles)
        results.append({
            "stock_code": stock.stock_code,
            "stock_name": stock.stock_name,
            "quantity": stock.quantity,
            "avg_price": stock.avg_price,
            "market": stock.market.value,
            "currency": stock.currency,
            "news_count": len(articles),
            "articles": articles[:5],
            "analysis": analysis,
        })

    # Auto-save: upsert today's result (1 per day)
    today = date.today()
    existing = db.query(AnalysisResult).filter(AnalysisResult.analysis_date == today).first()
    if existing:
        existing.market_filter = market.value if market else None
        existing.results_json = json.dumps(results, ensure_ascii=False, default=str)
    else:
        db.add(AnalysisResult(
            analysis_date=today,
            market_filter=market.value if market else None,
            results_json=json.dumps(results, ensure_ascii=False, default=str),
        ))
    db.commit()

    return results
