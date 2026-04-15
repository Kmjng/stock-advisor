from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import Portfolio, Market, Transaction, TradeType

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class PortfolioCreate(BaseModel):
    stock_code: str
    stock_name: str
    quantity: float
    avg_price: float
    market: Market = Market.KR
    currency: str = "KRW"
    account_no: Optional[str] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    return_rate: Optional[float] = None
    eval_amount: Optional[float] = None


class PortfolioResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    quantity: float
    avg_price: float
    market: Market
    currency: str
    account_no: Optional[str] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    return_rate: Optional[float] = None
    eval_amount: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[PortfolioResponse])
def get_portfolio(
    market: Optional[Market] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Portfolio)
    if market:
        query = query.filter(Portfolio.market == market)
    return query.all()


@router.get("/by-account")
def get_portfolio_by_account(db: Session = Depends(get_db)):
    stocks = db.query(Portfolio).all()
    grouped = {}
    for s in stocks:
        key = s.account_no or "unknown"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(PortfolioResponse.model_validate(s).model_dump())
    return grouped


@router.post("/", response_model=PortfolioResponse)
def add_stock(stock: PortfolioCreate, db: Session = Depends(get_db)):
    existing = db.query(Portfolio).filter(Portfolio.stock_code == stock.stock_code).first()

    # NH 동기화에서 수량 0으로 오면, 거래내역 기반으로 실제 보유량 확인
    if stock.quantity <= 0:
        txs = db.query(Transaction).filter(
            Transaction.stock_code == stock.stock_code
        ).all()
        actual_qty = sum(
            t.quantity if t.trade_type == TradeType.BUY else -t.quantity
            for t in txs
        )
        if actual_qty <= 0:
            # 진짜 0이면 삭제
            if existing:
                db.delete(existing)
                db.commit()
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=200, content={"message": "수량 0 - 삭제됨"})
        else:
            # 거래내역에 잔량이 있으면 NH 수량 무시, 현재가만 업데이트
            if existing:
                if stock.current_price is not None:
                    existing.current_price = stock.current_price
                    existing.eval_amount = stock.current_price * existing.quantity
                    existing.profit_loss = existing.eval_amount - (existing.avg_price * existing.quantity)
                    existing.return_rate = ((stock.current_price - existing.avg_price) / existing.avg_price) * 100 if existing.avg_price > 0 else 0
                    existing.updated_at = datetime.utcnow()
                    db.commit()
                    db.refresh(existing)
                return existing
            # 포트폴리오에 없으면 거래내역 기반으로 생성
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=200, content={"message": "NH 수량 0이나 거래내역 잔량 있음 - 무시"})

    # current_price가 있으면 profit_loss, return_rate, eval_amount를 직접 계산
    current_price = stock.current_price
    eval_amount = None
    profit_loss = None
    return_rate = None
    if current_price is not None and stock.avg_price > 0:
        eval_amount = current_price * stock.quantity
        buy_amount = stock.avg_price * stock.quantity
        profit_loss = eval_amount - buy_amount
        return_rate = ((current_price - stock.avg_price) / stock.avg_price) * 100

    if existing:
        existing.quantity = stock.quantity
        existing.avg_price = stock.avg_price
        existing.stock_name = stock.stock_name
        if stock.account_no:
            existing.account_no = stock.account_no
        if current_price is not None:
            existing.current_price = current_price
            existing.eval_amount = eval_amount
            existing.profit_loss = profit_loss
            existing.return_rate = return_rate
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    db_stock = Portfolio(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        quantity=stock.quantity,
        avg_price=stock.avg_price,
        market=stock.market,
        currency=stock.currency,
        account_no=stock.account_no,
        current_price=current_price,
        eval_amount=eval_amount,
        profit_loss=profit_loss,
        return_rate=return_rate,
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


@router.delete("/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Portfolio).filter(Portfolio.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다")
    db.delete(stock)
    db.commit()
    return {"message": "삭제되었습니다"}
