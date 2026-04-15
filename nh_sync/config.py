import keyring
import os
from dataclasses import dataclass

NH_SERVER = "wmca.nhsec.com"
NH_PORT = 8200

DLL_DIR = r"C:\works\openapi.nm\bin"
DLL_PATH = os.path.join(DLL_DIR, "wmca.dll")

STOCK_ADVISOR_API = "http://localhost:8000"


@dataclass
class NHCredentials:
    user_id: str
    password: str
    cert_password: str
    account_password: str
    trade_password: str
    account_index: int


def load_credentials() -> NHCredentials:
    return NHCredentials(
        user_id=keyring.get_password("NH_stock_bot", "user_id"),
        password=keyring.get_password("NH_stock_bot", "password"),
        cert_password=keyring.get_password("NH_stock_bot", "cert_password"),
        account_password=keyring.get_password("NH_stock_bot", "account_password"),
        trade_password=keyring.get_password("NH_stock_bot", "trade_password"),
        account_index=1,
    )