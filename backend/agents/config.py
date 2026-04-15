"""Agent configuration — loads API keys and model settings from environment."""

import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:8b-instruct")

# Rate limits
MAX_TRADE_NEWS_QUERIES = 15  # max Gemini calls for TradeReporter
TRADE_CLUSTER_DAYS = 7       # group trades within N days into one query
