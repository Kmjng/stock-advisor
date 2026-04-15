"""
기존 DB에 realized_profit 컬럼을 추가하고,
과거 매도 거래의 실현손익을 소급 계산하는 마이그레이션 스크립트.

사용법: cd backend && python migrate_realized_profit.py
"""
import sqlite3

DB_PATH = "./stock_advisor.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1) 컬럼 추가 (이미 있으면 무시)
try:
    cur.execute("ALTER TABLE transactions ADD COLUMN realized_profit REAL")
    print("realized_profit 컬럼 추가 완료")
except sqlite3.OperationalError:
    print("realized_profit 컬럼이 이미 존재합니다")

# 2) 매도 거래에 대해 실현손익 소급 계산
#    각 매도 시점의 평균매수가를 구하기 위해 시간순으로 매매를 재생(replay)
cur.execute("SELECT DISTINCT stock_code FROM transactions")
stock_codes = [row[0] for row in cur.fetchall()]

updated = 0
for code in stock_codes:
    cur.execute(
        "SELECT id, trade_type, quantity, price FROM transactions "
        "WHERE stock_code = ? ORDER BY traded_at ASC",
        (code,),
    )
    rows = cur.fetchall()

    # 평균매수가 추적
    total_qty = 0.0
    total_cost = 0.0

    for tx_id, trade_type, qty, price in rows:
        if trade_type == "buy":
            total_cost += qty * price
            total_qty += qty
        elif trade_type == "sell":
            avg_price = total_cost / total_qty if total_qty > 0 else 0
            realized = (price - avg_price) * qty
            cur.execute(
                "UPDATE transactions SET realized_profit = ? WHERE id = ?",
                (round(realized, 2), tx_id),
            )
            updated += 1
            # 매도 후 잔량/비용 조정
            total_qty -= qty
            total_cost = avg_price * total_qty if total_qty > 0 else 0

conn.commit()
conn.close()
print(f"매도 거래 {updated}건의 실현손익 계산 완료")
