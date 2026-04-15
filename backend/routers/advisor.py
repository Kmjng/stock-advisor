"""Advisor API — triggers the LangGraph agent pipeline."""

import asyncio
import json
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agents.graph import build_advisor_graph
from database import get_db
from models import AdvisorResult

router = APIRouter(prefix="/api/advisor", tags=["advisor"])


class AdvisorRequest(BaseModel):
    market: Optional[str] = None  # "KR", "US", or None for all


@router.get("/saved")
def get_saved_advisor(db: Session = Depends(get_db)):
    """Return the most recent saved advisor result."""
    result = db.query(AdvisorResult).order_by(AdvisorResult.analysis_date.desc()).first()
    if not result:
        return {"status": "empty", "result": None, "saved_at": None}
    return {
        "status": "ok",
        "result": json.loads(result.result_json),
        "saved_at": result.updated_at.isoformat() if result.updated_at else result.created_at.isoformat(),
        "market_filter": result.market_filter,
    }


@router.post("/run")
async def run_advisor(req: AdvisorRequest):
    """Run the full advisor pipeline synchronously."""
    graph = build_advisor_graph()
    initial_state = {
        "market_filter": req.market,
        "holdings": [],
        "transactions": [],
        "pnl": None,
        "market_news": [],
        "trade_news": [],
        "advisor_result": None,
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    result = await asyncio.to_thread(graph.invoke, initial_state)

    return {
        "status": "completed",
        "holdings_count": len(result.get("holdings", [])),
        "transactions_count": len(result.get("transactions", [])),
        "market_news_count": len(result.get("market_news", [])),
        "trade_news_count": len(result.get("trade_news", [])),
        "advisor_result": result.get("advisor_result"),
        "started_at": result.get("started_at"),
        "completed_at": result.get("completed_at"),
    }


@router.post("/run/stream")
async def run_advisor_stream(req: AdvisorRequest):
    """Run the advisor pipeline with SSE streaming for progress updates."""
    graph = build_advisor_graph()
    initial_state = {
        "market_filter": req.market,
        "holdings": [],
        "transactions": [],
        "pnl": None,
        "market_news": [],
        "trade_news": [],
        "advisor_result": None,
        "error": None,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    NODE_LABELS = {
        "gather_portfolio": "포트폴리오 데이터 수집",
        "search_market_news": "시장 뉴스 검색",
        "search_trade_news": "매매시점 뉴스 검색",
        "analyze_trades": "AI 매매 분석",
    }

    def generate():
        final_result = None
        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                label = NODE_LABELS.get(node_name, node_name)
                payload = {"node": node_name, "label": label, "status": "completed"}

                # Include summary info per node
                if node_name == "gather_portfolio":
                    payload["holdings_count"] = len(node_output.get("holdings", []))
                    payload["transactions_count"] = len(node_output.get("transactions", []))
                elif node_name == "search_market_news":
                    payload["news_count"] = len(node_output.get("market_news", []))
                elif node_name == "search_trade_news":
                    payload["news_count"] = len(node_output.get("trade_news", []))
                elif node_name == "analyze_trades":
                    payload["advisor_result"] = node_output.get("advisor_result")
                    final_result = node_output.get("advisor_result")

                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Auto-save to DB (1 per day, upsert)
        if final_result:
            db = next(get_db())
            try:
                today = date.today()
                existing = db.query(AdvisorResult).filter(AdvisorResult.analysis_date == today).first()
                result_str = json.dumps(final_result, ensure_ascii=False, default=str)
                if existing:
                    existing.market_filter = req.market
                    existing.result_json = result_str
                else:
                    db.add(AdvisorResult(
                        analysis_date=today,
                        market_filter=req.market,
                        result_json=result_str,
                    ))
                db.commit()
            finally:
                db.close()

        # Final done event
        done = {"node": "all", "status": "done", "advisor_result": final_result}
        yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
