import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/nh", tags=["nh-sync"])

PY32 = r"C:\Users\user\AppData\Local\Programs\Python\Python312-32\python.exe"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class SyncRequest(BaseModel):
    sync_holdings: bool = True
    sync_transactions: bool = True
    start_date: str | None = None  # YYYYMMDD
    end_date: str | None = None    # YYYYMMDD


def _run_sync_subprocess(args: list[str], timeout: int = 120) -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        proc = subprocess.run(
            args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        output = proc.stdout.decode("utf-8", errors="replace")
        if proc.stderr:
            output += proc.stderr.decode("utf-8", errors="replace")
        success = proc.returncode == 0
        return {"success": success, "output": output, "returncode": proc.returncode}

    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"시간 초과 ({timeout}초)"}
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"32-bit Python을 찾을 수 없습니다: {PY32}",
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/accounts")
def get_accounts():
    args = [PY32, "-m", "nh_sync.sync", "--list-accounts"]
    result = _run_sync_subprocess(args, timeout=30)

    if not result["success"]:
        return result

    output = result.get("output", "")
    for line in output.strip().splitlines():
        try:
            accounts = json.loads(line)
            if isinstance(accounts, list):
                return {"success": True, "accounts": accounts}
        except json.JSONDecodeError:
            continue

    return {"success": False, "message": "계좌 목록을 파싱할 수 없습니다", "output": output}


@router.post("/sync")
def sync_nh(req: SyncRequest):
    today = datetime.now().strftime("%Y%m%d")
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

    start_date = req.start_date or seven_days_ago
    end_date = req.end_date or today

    args = [PY32, "-m", "nh_sync.sync", "--sync-all-accounts"]

    if req.sync_holdings and req.sync_transactions:
        args.append("--all")
    elif req.sync_holdings:
        args.append("--holdings")
    elif req.sync_transactions:
        args.append("--transactions")
    else:
        return {"success": False, "message": "동기화 항목을 선택하세요"}

    if req.sync_transactions:
        args.extend(["--start-date", start_date, "--end-date", end_date])

    return _run_sync_subprocess(args, timeout=600)
