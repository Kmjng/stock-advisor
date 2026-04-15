"""AdvisorState — shared state schema for the LangGraph agent pipeline."""

from typing import TypedDict, Annotated, Optional
import operator


class HoldingInfo(TypedDict):
    stock_code: str
    stock_name: str
    quantity: float
    avg_price: float
    current_price: Optional[float]
    profit_loss: Optional[float]
    return_rate: Optional[float]
    eval_amount: Optional[float]
    market: str
    currency: str


class TransactionInfo(TypedDict):
    stock_code: str
    stock_name: str
    trade_type: str
    quantity: float
    price: float
    total_amount: float
    realized_profit: Optional[float]
    traded_at: str
    market: str
    currency: str


class PnlSummary(TypedDict):
    total_profit: float
    total_trades: int
    win_count: int
    loss_count: int
    win_rate: float


class NewsArticle(TypedDict):
    title: str
    source: str
    date: str
    summary: str
    url: Optional[str]


class TradeNewsItem(TypedDict):
    stock_code: str
    stock_name: str
    trade_type: str
    traded_at: str
    price: float
    context_summary: str
    key_events: list[str]


class TradeAdvisorResult(TypedDict):
    overall_assessment: str
    stock_analyses: list[dict]
    recommendations: list[str]
    risk_warnings: list[str]


class AdvisorState(TypedDict):
    # Input
    market_filter: Optional[str]

    # PortfolioProvider output
    holdings: list[HoldingInfo]
    transactions: list[TransactionInfo]
    pnl: Optional[PnlSummary]

    # MarketScout output (Annotated for parallel merge)
    market_news: Annotated[list[NewsArticle], operator.add]

    # TradeReporter output (Annotated for parallel merge)
    trade_news: Annotated[list[TradeNewsItem], operator.add]

    # TradeAdvisor output
    advisor_result: Optional[TradeAdvisorResult]

    # Metadata
    error: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
