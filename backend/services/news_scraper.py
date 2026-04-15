import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Optional
import time
import re

NAVER_NEWS_URL = "https://finance.naver.com/item/news_news.naver"
NAVER_NEWS_READ_URL = "https://finance.naver.com"
NAVER_SEARCH_NEWS_URL = "https://search.naver.com/search.naver"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

_cache: dict[str, tuple[list, datetime]] = {}
CACHE_TTL = timedelta(minutes=30)


def get_stock_news(stock_code: str, days: int = 7, market: str = "KR") -> list[dict]:
    cache_key = f"{market}_{stock_code}_{days}"
    if cache_key in _cache:
        cached_data, cached_at = _cache[cache_key]
        if datetime.now() - cached_at < CACHE_TTL:
            return cached_data

    if market == "US":
        articles = _get_us_stock_news(stock_code, days)
    else:
        articles = _get_kr_stock_news(stock_code, days)

    _cache[cache_key] = (articles, datetime.now())
    return articles


def _get_kr_stock_news(stock_code: str, days: int) -> list[dict]:
    articles = []
    cutoff_date = datetime.now() - timedelta(days=days)

    for page in range(1, 6):
        try:
            params = {"code": stock_code, "page": page, "sm": "title_entity_id.basic", "clusterId": ""}
            resp = requests.get(NAVER_NEWS_URL, params=params, headers=HEADERS, timeout=10)
            resp.encoding = "euc-kr"
            soup = BeautifulSoup(resp.text, "html.parser")

            rows = soup.select("table.type5 tbody tr")
            stop = False

            for row in rows:
                if row.get("class") and "relation_lst" in " ".join(row.get("class", [])):
                    continue

                title_tag = row.select_one("td.title a")
                date_tag = row.select_one("td.date")
                info_tag = row.select_one("td.info")

                if not title_tag or not date_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                if link and not link.startswith("http"):
                    link = NAVER_NEWS_READ_URL + link
                date_str = date_tag.get_text(strip=True)
                source = info_tag.get_text(strip=True) if info_tag else ""

                article_date = _parse_date(date_str)
                if article_date and article_date < cutoff_date:
                    stop = True
                    break

                articles.append({
                    "title": title,
                    "link": link,
                    "date": date_str,
                    "source": source,
                    "parsed_date": article_date.isoformat() if article_date else None,
                })

            if stop:
                break
            time.sleep(0.5)
        except Exception:
            break

    return articles


def _get_us_stock_news(stock_code: str, days: int) -> list[dict]:
    """네이버 검색에서 미국 주식 뉴스 수집"""
    articles = []
    try:
        params = {
            "where": "news",
            "query": f"{stock_code} 주식",
            "sort": "1",  # 최신순
        }
        resp = requests.get(NAVER_SEARCH_NEWS_URL, params=params, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        news_items = soup.select("div.news_area")
        for item in news_items[:15]:
            title_tag = item.select_one("a.news_tit")
            info_tag = item.select_one("div.info_group a.press")
            date_tag = item.select_one("div.info_group span.info")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            source = info_tag.get_text(strip=True) if info_tag else ""
            date_str = ""
            if date_tag:
                date_str = date_tag.get_text(strip=True)

            articles.append({
                "title": title,
                "link": link,
                "date": date_str,
                "source": source,
                "parsed_date": None,
            })
    except Exception:
        pass

    return articles


def _parse_date(date_str: str) -> Optional[datetime]:
    date_str = date_str.strip()
    patterns = [
        r"(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})",
        r"(\d{4})\.(\d{2})\.(\d{2})",
    ]
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 5:
                return datetime(int(groups[0]), int(groups[1]), int(groups[2]),
                                int(groups[3]), int(groups[4]))
            elif len(groups) == 3:
                return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
    return None
