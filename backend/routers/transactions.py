from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import Transaction, TradeType, Portfolio, Market

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    stock_code: str
    stock_name: str
    trade_type: TradeType
    quantity: float
    price: float
    traded_at: datetime
    market: Market = Market.KR
    currency: str = "KRW"
    account_no: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    trade_type: TradeType
    quantity: float
    price: float
    total_amount: float
    realized_profit: Optional[float] = None
    market: Market
    currency: str
    account_no: Optional[str] = None
    traded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    stock_code: Optional[str] = Query(None),
    market: Optional[Market] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction).order_by(Transaction.traded_at.desc())
    if stock_code:
        query = query.filter(Transaction.stock_code == stock_code)
    if market:
        query = query.filter(Transaction.market == market)
    return query.all()


@router.get("/pnl")
def get_pnl(
    market: Optional[Market] = Query(None),
    db: Session = Depends(get_db),
):
    """실현손익 요약: 총 실현손익, 월별 실현손익, 승률"""
    query = db.query(Transaction).filter(
        Transaction.trade_type == TradeType.SELL,
        Transaction.realized_profit.isnot(None),
    )
    if market:
        query = query.filter(Transaction.market == market)

    sells = query.order_by(Transaction.traded_at.asc()).all()

    total_profit = sum(t.realized_profit for t in sells)
    win_count = sum(1 for t in sells if t.realized_profit > 0)
    loss_count = sum(1 for t in sells if t.realized_profit <= 0)
    win_rate = (win_count / len(sells) * 100) if sells else 0

    # 월별 집계
    monthly = {}
    for t in sells:
        key = t.traded_at.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"month": key, "profit": 0, "count": 0}
        monthly[key]["profit"] += t.realized_profit
        monthly[key]["count"] += 1

    # 누적 수익 추이
    cumulative = []
    running = 0
    for t in sells:
        running += t.realized_profit
        cumulative.append({
            "date": t.traded_at.isoformat(),
            "stock_name": t.stock_name,
            "profit": t.realized_profit,
            "cumulative": running,
        })

    return {
        "total_profit": total_profit,
        "total_trades": len(sells),
        "win_count": win_count,
        "loss_count": loss_count,
        "win_rate": round(win_rate, 1),
        "monthly": sorted(monthly.values(), key=lambda x: x["month"]),
        "cumulative": cumulative,
    }


@router.get("/by-stock")
def get_by_stock(
    market: Optional[Market] = Query(None),
    db: Session = Depends(get_db),
):
    """종목별 매매 요약"""
    query = db.query(Transaction)
    if market:
        query = query.filter(Transaction.market == market)

    txs = query.order_by(Transaction.traded_at.asc()).all()

    stocks = {}
    for t in txs:
        key = t.stock_code
        if key not in stocks:
            stocks[key] = {
                "stock_code": t.stock_code,
                "stock_name": t.stock_name,
                "market": t.market.value,
                "currency": t.currency,
                "buy_count": 0,
                "sell_count": 0,
                "total_buy_amount": 0,
                "total_sell_amount": 0,
                "realized_profit": 0,
                "transactions": [],
            }
        s = stocks[key]
        if t.trade_type == TradeType.BUY:
            s["buy_count"] += 1
            s["total_buy_amount"] += t.total_amount
        else:
            s["sell_count"] += 1
            s["total_sell_amount"] += t.total_amount
            if t.realized_profit is not None:
                s["realized_profit"] += t.realized_profit
        s["transactions"].append({
            "id": t.id,
            "trade_type": t.trade_type.value,
            "quantity": t.quantity,
            "price": t.price,
            "total_amount": t.total_amount,
            "realized_profit": t.realized_profit,
            "traded_at": t.traded_at.isoformat(),
        })

    result = sorted(stocks.values(), key=lambda x: abs(x["realized_profit"]), reverse=True)
    return result


@router.post("/", response_model=TransactionResponse)
def add_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    realized_profit = None

    # 보유종목 자동 반영
    portfolio = db.query(Portfolio).filter(Portfolio.stock_code == tx.stock_code).first()

    if tx.trade_type == TradeType.SELL and portfolio:
        # 실현손익 = (매도가 - 평균매수가) × 수량
        realized_profit = (tx.price - portfolio.avg_price) * tx.quantity

    db_tx = Transaction(
        **tx.model_dump(),
        total_amount=tx.quantity * tx.price,
        realized_profit=realized_profit,
    )
    db.add(db_tx)

    if tx.trade_type == TradeType.BUY:
        if portfolio:
            old_total = portfolio.quantity * portfolio.avg_price
            new_total = tx.quantity * tx.price
            portfolio.quantity += tx.quantity
            portfolio.avg_price = (old_total + new_total) / portfolio.quantity
        else:
            portfolio = Portfolio(
                stock_code=tx.stock_code,
                stock_name=tx.stock_name,
                quantity=tx.quantity,
                avg_price=tx.price,
                market=tx.market,
                currency=tx.currency,
            )
            db.add(portfolio)

    elif tx.trade_type == TradeType.SELL:
        if portfolio:
            portfolio.quantity -= tx.quantity
            if portfolio.quantity <= 0.0001:
                db.delete(portfolio)

    db.commit()
    db.refresh(db_tx)
    return db_tx


@router.delete("/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="거래내역을 찾을 수 없습니다")

    portfolio = db.query(Portfolio).filter(Portfolio.stock_code == tx.stock_code).first()

    if tx.trade_type == TradeType.BUY:
        if portfolio:
            portfolio.quantity -= tx.quantity
            if portfolio.quantity <= 0:
                db.delete(portfolio)
    elif tx.trade_type == TradeType.SELL:
        if portfolio:
            portfolio.quantity += tx.quantity
        else:
            portfolio = Portfolio(
                stock_code=tx.stock_code,
                stock_name=tx.stock_name,
                quantity=tx.quantity,
                avg_price=tx.price,
                market=tx.market,
                currency=tx.currency,
            )
            db.add(portfolio)

    db.delete(tx)
    db.commit()
    return {"message": "삭제되었습니다"}
