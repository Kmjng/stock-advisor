"""TradeAdvisor — analyzes trading decisions using Ollama (qwen3-vl:8b-instruct)."""

import json
from datetime import datetime

from openai import OpenAI

from agents.state import AdvisorState, TradeAdvisorResult
from agents.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from agents.prompts.trade_advisor_prompts import (
    TRADE_ADVISOR_SYSTEM,
    TRADE_ADVISOR_PROMPT,
)


def _build_portfolio_summary(holdings: list[dict]) -> str:
    if not holdings:
        return "보유 종목 없음"
    lines = []
    total_eval = 0
    for h in holdings:
        eval_amt = h.get("eval_amount") or (h["avg_price"] * h["quantity"])
        total_eval += eval_amt
        ret = h.get("return_rate")
        ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
        currency = "USD" if h["currency"] == "USD" else "KRW"
        lines.append(
            f"- {h['stock_name']} ({h['stock_code']}, {h['market']}): "
            f"{h['quantity']}주, 평균단가 {h['avg_price']:,.0f}{currency}, "
            f"수익률 {ret_str}"
        )
    lines.insert(0, f"총 평가금액: {total_eval:,.0f}")
    return "\n".join(lines)


def _build_pnl_summary(pnl: dict | None) -> str:
    if not pnl:
        return "실현손익 데이터 없음"
    return (
        f"총 실현손익: {pnl['total_profit']:,.0f}원\n"
        f"총 매도 건수: {pnl['total_trades']}건\n"
        f"수익 {pnl['win_count']}건 / 손실 {pnl['loss_count']}건\n"
        f"승률: {pnl['win_rate']:.1f}%"
    )


def _build_transactions_summary(transactions: list[dict]) -> str:
    if not transactions:
        return "거래 내역 없음"
    lines = []
    for tx in transactions[:30]:  # limit to recent 30
        action = "매수" if tx["trade_type"] == "buy" else "매도"
        profit = ""
        if tx.get("realized_profit") is not None:
            profit = f" (실현손익: {tx['realized_profit']:+,.0f})"
        lines.append(
            f"- {tx['traded_at'][:10]} {action} {tx['stock_name']} "
            f"{tx['quantity']}주 @ {tx['price']:,.0f}{profit}"
        )
    return "\n".join(lines)


def _build_market_news_summary(news: list[dict]) -> str:
    if not news:
        return "시장 뉴스 없음"
    lines = []
    for n in news[:15]:
        lines.append(f"- [{n.get('date', '')}] {n['title']}: {n.get('summary', '')}")
    return "\n".join(lines)


def _build_trade_news_summary(trade_news: list[dict]) -> str:
    if not trade_news:
        return "매매 시점 뉴스 없음"
    lines = []
    for tn in trade_news:
        action = "매수" if tn.get("trade_type") == "buy" else "매도"
        events = ", ".join(tn.get("key_events", [])[:3])
        lines.append(
            f"- {tn['stock_name']} ({tn.get('traded_at', '')[:10]} {action}): "
            f"{tn.get('context_summary', '')} [이벤트: {events}]"
        )
    return "\n".join(lines)


def _parse_advisor_response(text: str) -> TradeAdvisorResult:
    """Parse the Ollama model response into structured result."""
    # Try to extract JSON
    cleaned = text.strip()
    # qwen3 may wrap in <think> tags — skip thinking block
    if "<think>" in cleaned:
        think_end = cleaned.find("</think>")
        if think_end != -1:
            cleaned = cleaned[think_end + len("</think>"):].strip()

    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
        return TradeAdvisorResult(
            overall_assessment=data.get("overall_assessment", ""),
            stock_analyses=data.get("stock_analyses", []),
            recommendations=data.get("recommendations", []),
            risk_warnings=data.get("risk_warnings", []),
        )
    except (json.JSONDecodeError, ValueError):
        # Fallback: return raw text as overall assessment
        return TradeAdvisorResult(
            overall_assessment=text.strip()[:2000],
            stock_analyses=[],
            recommendations=[],
            risk_warnings=[],
        )


def analyze_trades(state: AdvisorState) -> dict:
    prompt = TRADE_ADVISOR_PROMPT.format(
        portfolio_summary=_build_portfolio_summary(state.get("holdings", [])),
        pnl_summary=_build_pnl_summary(state.get("pnl")),
        transactions_summary=_build_transactions_summary(state.get("transactions", [])),
        market_news_summary=_build_market_news_summary(state.get("market_news", [])),
        trade_news_summary=_build_trade_news_summary(state.get("trade_news", [])),
    )

    try:
        client = OpenAI(
            base_url=f"{OLLAMA_BASE_URL}/v1",
            api_key="ollama",
        )
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": TRADE_ADVISOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        result_text = response.choices[0].message.content or ""
        advisor_result = _parse_advisor_response(result_text)
    except Exception as e:
        print(f"[TradeAdvisor] Ollama error: {e}")
        advisor_result = TradeAdvisorResult(
            overall_assessment=f"분석 중 오류가 발생했습니다: {str(e)}",
            stock_analyses=[],
            recommendations=[],
            risk_warnings=[],
        )

    return {
        "advisor_result": advisor_result,
        "completed_at": datetime.now().isoformat(),
    }
