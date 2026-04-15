from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Enum as SqlEnum
from datetime import datetime, date
import enum

from database import Base


class TradeType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Market(str, enum.Enum):
    KR = "KR"
    US = "US"


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    account_no = Column(String, nullable=True)
    stock_code = Column(String, unique=True, nullable=False)
    stock_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    market = Column(SqlEnum(Market), nullable=False, default=Market.KR)
    currency = Column(String, nullable=False, default="KRW")
    current_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    return_rate = Column(Float, nullable=True)
    eval_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_no = Column(String, nullable=True)
    stock_code = Column(String, nullable=False)
    stock_name = Column(String, nullable=False)
    trade_type = Column(SqlEnum(TradeType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    realized_profit = Column(Float, nullable=True)
    market = Column(SqlEnum(Market), nullable=False, default=Market.KR)
    currency = Column(String, nullable=False, default="KRW")
    traded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(Date, unique=True, nullable=False, default=date.today)
    market_filter = Column(String, nullable=True)
    results_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdvisorResult(Base):
    __tablename__ = "advisor_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(Date, unique=True, nullable=False, default=date.today)
    market_filter = Column(String, nullable=True)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
