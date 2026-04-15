from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

from database import engine, Base
from routers import portfolio, transactions, news, analysis, nh_sync_router, chart, advisor

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Advisor", description="주식 뉴스 분석 & 매수/매도 추천")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(transactions.router)
app.include_router(news.router)
app.include_router(analysis.router)
app.include_router(nh_sync_router.router)
app.include_router(chart.router)
app.include_router(advisor.router)


@app.get("/")
def root():
    return {"message": "Stock Advisor API"}
