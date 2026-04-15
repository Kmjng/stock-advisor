"""나무증권 Open API -> Stock Advisor sync script.

Must run under 32-bit Python:
    & "C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python312-32\\python.exe" -m nh_sync.sync --holdings
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

import requests

from .config import load_credentials, STOCK_ADVISOR_API
from .nh_client import NHClient


def sync_holdings(client: NHClient, api_url: str, account_no: str, account_index: int):
    print(f"\n=== Syncing Holdings [계좌 {account_index}: {account_no}] ===")
    holdings = client.query_holdings(account_index)

    if not holdings:
        print("No holdings found.")
        return

    success = 0
    fail = 0

    for h in holdings:
        payload = {
            "stock_code": h["stock_code"],
            "stock_name": h["stock_name"],
            "quantity": h["quantity"],
            "avg_price": h["avg_price"],
            "market": "KR",
            "currency": "KRW",
            "account_no": account_no,
            "current_price": h.get("current_price"),
            "profit_loss": h.get("profit_loss"),
            "return_rate": h.get("return_rate"),
            "eval_amount": h.get("eval_amount"),
        }

        try:
            resp = requests.post(f"{api_url}/api/portfolio/", json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"  [OK] {h['stock_code']} {h['stock_name']}: "
                      f"{h['quantity']}주 @ {h['avg_price']:,}원 "
                      f"(현재가 {h['current_price']:,}원, 수익률 {h['return_rate']:.2f}%)")
                success += 1
            else:
                print(f"  [FAIL] {h['stock_code']}: {resp.status_code} {resp.text}")
                fail += 1
        except requests.RequestException as e:
            print(f"  [ERROR] {h['stock_code']}: {e}")
            fail += 1

    print(f"\nHoldings sync: {success} success, {fail} fail")


def sync_transactions(client: NHClient, api_url: str, start_date: str, end_date: str, account_no: str, account_index: int):
    print(f"\n=== Syncing Transactions [계좌 {account_index}: {account_no}] ({start_date} ~ {end_date}) ===")

    existing = set()
    try:
        resp = requests.get(f"{api_url}/api/transactions/", timeout=10)
        if resp.status_code == 200:
            for tx in resp.json():
                key = (tx["stock_code"], tx["traded_at"], tx["quantity"], tx["price"], tx["trade_type"])
                existing.add(key)
    except requests.RequestException:
        print("  Warning: Could not fetch existing transactions for dedup")

    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    current = start

    total_new = 0
    total_skip = 0
    total_fail = 0

    while current <= end:
        date_str = current.strftime("%Y%m%d")
        trades = client.query_trade_history(date_str, account_index)

        if trades:
            print(f"\n  [{date_str}] {len(trades)} trade(s) found")

        for t in trades:
            key = (t["stock_code"], t["traded_at"], t["quantity"], t["price"], t["trade_type"])
            if key in existing:
                total_skip += 1
                continue

            payload = {
                "stock_code": t["stock_code"],
                "stock_name": t["stock_name"],
                "trade_type": t["trade_type"],
                "quantity": t["quantity"],
                "price": t["price"],
                "traded_at": t["traded_at"],
                "market": "KR",
                "currency": "KRW",
                "account_no": account_no,
            }

            try:
                resp = requests.post(f"{api_url}/api/transactions/", json=payload, timeout=10)
                if resp.status_code == 200:
                    action = "BUY" if t["trade_type"] == "buy" else "SELL"
                    print(f"    [{action}] {t['stock_code']} {t['stock_name']}: "
                          f"{t['quantity']}주 @ {t['price']:,}원")
                    existing.add(key)
                    total_new += 1
                else:
                    print(f"    [FAIL] {t['stock_code']}: {resp.status_code} {resp.text}")
                    total_fail += 1
            except requests.RequestException as e:
                print(f"    [ERROR] {t['stock_code']}: {e}")
                total_fail += 1

        current += timedelta(days=1)

    print(f"\nTransaction sync: {total_new} new, {total_skip} skipped (dup), {total_fail} fail")


def sync_all_accounts(client: NHClient, api_url: str, do_holdings: bool, do_transactions: bool, start_date: str, end_date: str):
    accounts = client.get_accounts()
    if not accounts:
        print("No accounts found.")
        return

    print(f"\n총 {len(accounts)}개 계좌 동기화 시작")
    for i, acct in enumerate(accounts):
        account_no = acct["no"]
        account_name = acct["name"]
        idx = i + 1
        print(f"\n{'='*60}")
        print(f"[{idx}/{len(accounts)}] {account_no} ({account_name})")
        print(f"{'='*60}")

        if do_transactions:
            sync_transactions(client, api_url, start_date, end_date, account_no, idx)

        if do_holdings:
            sync_holdings(client, api_url, account_no, idx)

    print(f"\n전체 계좌 동기화 완료")


def list_accounts(client: NHClient):
    accounts = client.get_accounts()
    print(json.dumps(accounts, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Sync 나무증권 data to Stock Advisor")
    parser.add_argument("--holdings", action="store_true", help="Sync account holdings")
    parser.add_argument("--transactions", action="store_true", help="Sync trade history")
    parser.add_argument("--all", action="store_true", help="Sync both holdings and transactions")
    parser.add_argument("--sync-all-accounts", action="store_true", help="Sync all accounts")
    parser.add_argument("--list-accounts", action="store_true", help="List available accounts as JSON")
    parser.add_argument("--account-index", type=int, default=None, help="Account index to sync (1-based)")
    parser.add_argument("--start-date", default=None, help="Start date (YYYYMMDD)")
    parser.add_argument("--end-date", default=None, help="End date (YYYYMMDD)")
    args = parser.parse_args()

    if not (args.holdings or args.transactions or args.all or args.list_accounts or args.sync_all_accounts):
        parser.print_help()
        sys.exit(1)

    today = datetime.now().strftime("%Y%m%d")
    start_date = args.start_date or today
    end_date = args.end_date or today

    try:
        creds = load_credentials()
        print(f"Credentials loaded for user: {creds.user_id}")
    except Exception as e:
        print(f"Failed to load credentials: {e}")
        sys.exit(1)

    client = NHClient(creds)
    try:
        print("Connecting to NH server...")
        if not client.connect():
            print("Connection failed.")
            sys.exit(1)

        if args.list_accounts:
            list_accounts(client)
            return

        if args.sync_all_accounts:
            do_holdings = args.holdings or args.all or (not args.holdings and not args.transactions)
            do_transactions = args.transactions or args.all or (not args.holdings and not args.transactions)
            sync_all_accounts(client, STOCK_ADVISOR_API, do_holdings, do_transactions, start_date, end_date)
            return

        account_index = args.account_index if args.account_index is not None else creds.account_index
        accounts = client.get_accounts()
        account_no = accounts[account_index - 1]["no"] if accounts and account_index <= len(accounts) else None

        if args.holdings or args.all:
            sync_holdings(client, STOCK_ADVISOR_API, account_no, account_index)

        if args.transactions or args.all:
            sync_transactions(client, STOCK_ADVISOR_API, start_date, end_date, account_no, account_index)

    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nDisconnecting...")
        client.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
