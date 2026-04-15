"""PortfolioProvider — gathers holdings, transactions, and P&L from the DB."""

from datetime import datetime

from database import SessionLocal
from models import Portfolio, Transaction, TradeType
from agents.state import AdvisorState, HoldingInfo, TransactionInfo, PnlSummary


def gather_portfolio(state: AdvisorState) -> dict:
    db = SessionLocal()
    try:
        # Holdings
        q = db.query(Portfolio)
        if state.get("market_filter"):
            q = q.filter(Portfolio.market == state["market_filter"])
        stocks = q.all()

        holdings = [
            HoldingInfo(
                stock_code=s.stock_code,
                stock_name=s.stock_name,
                quantity=s.quantity,
                avg_price=s.avg_price,
                current_price=s.current_price,
                profit_loss=s.profit_loss,
                return_rate=s.return_rate,
                eval_amount=s.eval_amount,
                market=s.market.value,
                currency=s.currency,
            )
            for s in stocks
        ]

        # Transactions
        tq = db.query(Transaction).order_by(Transaction.traded_at.desc())
        if state.get("market_filter"):
            tq = tq.filter(Transaction.market == state["market_filter"])
        txs = tq.all()

        transactions = [
            TransactionInfo(
                stock_code=t.stock_code,
                stock_name=t.stock_name,
                trade_type=t.trade_type.value,
                quantity=t.quantity,
                price=t.price,
                total_amount=t.total_amount,
                realized_profit=t.realized_profit,
                traded_at=t.traded_at.isoformat(),
                market=t.market.value,
                currency=t.currency,
            )
            for t in txs
        ]

        # P&L summary
        sells = [t for t in txs if t.trade_type == TradeType.SELL and t.realized_profit is not None]
        win = sum(1 for t in sells if t.realized_profit > 0)
        pnl = PnlSummary(
            total_profit=sum(t.realized_profit for t in sells),
            total_trades=len(sells),
            win_count=win,
            loss_count=len(sells) - win,
            win_rate=(win / len(sells) * 100) if sells else 0,
        )

        return {
            "holdings": holdings,
            "transactions": transactions,
            "pnl": pnl,
            "started_at": datetime.now().isoformat(),
        }
    finally:
        db.close()
