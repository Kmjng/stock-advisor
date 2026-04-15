import re
from datetime import datetime, timedelta

import requests

NAVER_CHART_URL = "https://fchart.stock.naver.com/siseJson.nhn"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

_cache: dict[str, tuple[list, datetime]] = {}
CACHE_TTL = timedelta(minutes=30)

PERIOD_DAYS = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}
YAHOO_RANGE = {"1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y"}


def get_price_history(stock_code: str, period: str = "3m", market: str = "KR") -> list[dict]:
    cache_key = f"{market}_{stock_code}_{period}"
    if cache_key in _cache:
        data, cached_at = _cache[cache_key]
        if datetime.now() - cached_at < CACHE_TTL:
            return data

    if market == "KR":
        data = _get_kr_price_history(stock_code, period)
    else:
        data = _get_us_price_history(stock_code, period)

    _cache[cache_key] = (data, datetime.now())
    return data


def _get_kr_price_history(stock_code: str, period: str) -> list[dict]:
    days = PERIOD_DAYS.get(period, 90)
    end = datetime.now()
    start = end - timedelta(days=days)

    params = {
        "symbol": stock_code,
        "requestType": "1",
        "startTime": start.strftime("%Y%m%d"),
        "endTime": end.strftime("%Y%m%d"),
        "timeframe": "day",
    }

    try:
        resp = requests.get(NAVER_CHART_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    return _parse_naver_chart(resp.text)


def _parse_naver_chart(text: str) -> list[dict]:
    """Parse Naver's JS-like array response into a list of dicts."""
    results = []
    # Each data row looks like: ['20260115', 50000, 51000, 49500, 50500, 123456]
    for line in text.strip().splitlines():
        line = line.strip().rstrip(",")
        if not line.startswith("["):
            continue
        # Skip header row (contains quoted strings for all columns)
        if "'날짜" in line or '"날짜' in line:
            continue
        # Remove brackets
        inner = line.strip("[]")
        parts = [p.strip().strip("'\"") for p in inner.split(",")]
        if len(parts) < 6:
            continue
        date_str = parts[0].strip()
        if not re.match(r"^\d{8}$", date_str):
            continue
        try:
            results.append({
                "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
                "open": int(parts[1]),
                "high": int(parts[2]),
                "low": int(parts[3]),
                "close": int(parts[4]),
                "volume": int(parts[5]),
            })
        except (ValueError, IndexError):
            continue
    return results


def _get_us_price_history(stock_code: str, period: str) -> list[dict]:
    yahoo_range = YAHOO_RANGE.get(period, "3mo")

    try:
        resp = requests.get(
            f"{YAHOO_CHART_URL}/{stock_code}",
            params={"range": yahoo_range, "interval": "1d"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    return _parse_yahoo_chart(data)


def _parse_yahoo_chart(data: dict) -> list[dict]:
    """Parse Yahoo Finance chart API response."""
    try:
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError):
        return []

    results = []
    for i, ts in enumerate(timestamps):
        try:
            close = quote["close"][i]
            if close is None:
                continue
            dt = datetime.utcfromtimestamp(ts)
            results.append({
                "date": dt.strftime("%Y-%m-%d"),
                "open": round(quote["open"][i], 2) if quote["open"][i] else None,
                "high": round(quote["high"][i], 2) if quote["high"][i] else None,
                "low": round(quote["low"][i], 2) if quote["low"][i] else None,
                "close": round(close, 2),
                "volume": quote["volume"][i] or 0,
            })
        except (IndexError, TypeError):
            continue
    return results
