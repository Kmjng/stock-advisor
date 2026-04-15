import os
import json
import google.generativeai as genai

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _configured = True


def analyze_stock_news(stock_name: str, stock_code: str, articles: list[dict]) -> dict:
    if not articles:
        return {
            "recommendation": "hold",
            "sentiment_score": 0.0,
            "summary": f"{stock_name}({stock_code})에 대한 최근 뉴스가 없어 판단이 어렵습니다. 관망을 추천합니다.",
            "reasons": [],
        }

    news_text = "\n".join(
        f"- [{a['date']}] {a['title']} ({a.get('source', '')})"
        for a in articles[:20]
    )

    prompt = f"""당신은 한국 주식 시장 전문 애널리스트입니다.
아래는 {stock_name}({stock_code}) 종목의 최근 7일간 뉴스 기사 제목 목록입니다.

{news_text}

위 뉴스들을 종합적으로 분석하여 다음 JSON 형식으로 응답해주세요:

{{
  "recommendation": "buy" | "sell" | "hold",
  "sentiment_score": -1.0 ~ 1.0 사이의 감성 점수 (양수=긍정, 음수=부정),
  "summary": "종합 분석 요약 (2-3문장)",
  "reasons": ["근거1", "근거2", "근거3"]
}}

분석 시 고려사항:
- 실적/매출 관련 뉴스
- 신규 사업/투자 뉴스
- 규제/법적 이슈
- 시장 트렌드와 업종 전반 동향
- 기관/외국인 매매 동향

반드시 유효한 JSON만 출력하세요. 다른 텍스트는 포함하지 마세요."""

    try:
        _ensure_configured()
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
        response = model.generate_content(prompt)

        result_text = response.text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        return json.loads(result_text)
    except Exception as e:
        return {
            "recommendation": "hold",
            "sentiment_score": 0.0,
            "summary": f"AI 분석 중 오류가 발생했습니다: {str(e)}",
            "reasons": [],
        }
