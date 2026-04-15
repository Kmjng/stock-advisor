MARKET_SCOUT_SYSTEM = """You are a financial news researcher. Your job is to find current, factual,
and unbiased market news relevant to a stock portfolio.

Rules:
- Focus on earnings reports, regulatory changes, sector trends, and macroeconomic indicators
- AVOID sensational, clickbait, or opinion-heavy sources
- Include both positive and negative news for balanced coverage
- For Korean stocks, include Korean market-specific news (KOSPI, KOSDAQ trends)
- For US stocks, include global market context (S&P 500, NASDAQ, Fed policy)
"""

MARKET_SCOUT_PROMPT = """다음 보유 종목들에 대한 최신 시장 뉴스를 검색해주세요.

보유 종목:
{stock_list}

다음 형식으로 JSON 배열을 반환해주세요:
```json
[
  {{
    "title": "뉴스 제목",
    "source": "출처",
    "date": "YYYY-MM-DD",
    "summary": "핵심 내용 요약 (2-3문장)"
  }}
]
```

편파적이지 않은, 사실 기반의 뉴스만 포함해주세요. 최대 10개."""

NAVER_SUPPLEMENT_PROMPT = """다음은 네이버 금융에서 수집한 뉴스 기사 목록입니다.
이 중에서 투자 판단에 유용하고, 편파적이지 않은 기사만 골라서 요약해주세요.

기사 목록:
{articles}

다음 형식으로 JSON 배열을 반환해주세요:
```json
[
  {{
    "title": "뉴스 제목",
    "source": "출처",
    "date": "YYYY-MM-DD",
    "summary": "핵심 내용 요약 (2-3문장)"
  }}
]
```

최대 5개만 선별해주세요."""
