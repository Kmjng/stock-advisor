from fastapi import APIRouter, Query

from services.price_history import get_price_history

router = APIRouter(prefix="/api/chart", tags=["chart"])


@router.get("/{stock_code}")
def get_chart_data(
    stock_code: str,
    period: str = Query(default="3m", pattern="^(1m|3m|6m|1y)$"),
    market: str = Query(default="KR", pattern="^(KR|US)$"),
):
    prices = get_price_history(stock_code, period=period, market=market)
    return {
        "stock_code": stock_code,
        "market": market,
        "period": period,
        "count": len(prices),
        "prices": prices,
    }
