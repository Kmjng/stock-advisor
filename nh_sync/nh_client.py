import ctypes

from .config import NHCredentials, NH_SERVER, NH_PORT
from .structs import (
    CA_WMCAEVENT,
    Tc8201InBlock, Tc8201OutBlock, Tc8201OutBlock1,
    Ts8180InBlock, Ts8180OutBlock, Ts8180OutBlock1, Ts8180OutBlock_IN,
    init_block, parse_field, parse_int, parse_float,
)
from .wmca_wrapper import WmcaWrapper
from .message_loop import NHMessageLoop

_TRID_HOLDINGS = 1001
_TRID_TRADES_BASE = 2001


class NHClient:
    def __init__(self, credentials: NHCredentials):
        self.creds = credentials
        self.wmca = WmcaWrapper()
        self.msg_loop = NHMessageLoop()
        self._trade_tr_counter = _TRID_TRADES_BASE

    def get_accounts(self) -> list[dict]:
        if self.msg_loop._login_info:
            return self.msg_loop._login_info.get("accounts", [])
        return []

    def connect(self) -> bool:
        if not self.msg_loop.create_window():
            print("[NH] Failed to create message window")
            return False

        print(f"[NH] Window created: hwnd={self.msg_loop.hwnd}")

        r3 = self.wmca.load()
        r1 = self.wmca.set_server(NH_SERVER)
        r2 = self.wmca.set_port(NH_PORT)
        print(f"[NH] Load={r3}, SetServer={r1}, SetPort={r2}")

        # 나무증권: mediaType='T', userType='W'
        print(f"[NH] Connecting as '{self.creds.user_id}'...")
        result = self.wmca.connect(
            self.msg_loop.hwnd,
            CA_WMCAEVENT,
            b"T", b"W",
            self.creds.user_id,
            self.creds.password,
            self.creds.cert_password,
        )

        print(f"[NH] wmcaConnect returned: {result}")
        if not result:
            print("[NH] wmcaConnect returned False")
            return False

        print("[NH] Waiting for login response (15s timeout)...")
        login_info = self.msg_loop.wait_for_login(timeout=15)
        if not login_info or "error" in login_info:
            print(f"[NH] Login failed: {login_info}")
            return False

        print(f"[NH] Login successful at {login_info['date']}")
        return True

    def _get_field_ptr(self, struct_instance, field_name):
        field_offset = getattr(type(struct_instance), field_name).offset
        return ctypes.cast(
            ctypes.addressof(struct_instance) + field_offset,
            ctypes.c_char_p,
        )

    def query_holdings(self, account_index: int | None = None) -> list[dict]:
        acct_idx = account_index if account_index is not None else self.creds.account_index
        inblock = Tc8201InBlock()
        init_block(inblock)

        pwd_ptr = self._get_field_ptr(inblock, "pswd_noz8")
        self.wmca.set_account_index_pwd(
            pwd_ptr, acct_idx, self.creds.account_password,
        )
        inblock.bnc_bse_cdz1 = b"1"

        tr_index = _TRID_HOLDINGS
        self.msg_loop.prepare(tr_index)

        self.wmca.query(
            self.msg_loop.hwnd, tr_index, "c8201",
            ctypes.cast(ctypes.addressof(inblock), ctypes.c_char_p),
            ctypes.sizeof(Tc8201InBlock),
            acct_idx,
        )

        blocks = self.msg_loop.wait_for_response(tr_index, timeout=10)
        return self._parse_c8201(blocks)

    def query_trade_history(self, date: str, account_index: int | None = None) -> list[dict]:
        acct_idx = account_index if account_index is not None else self.creds.account_index
        all_trades = []
        cts = b" " * 56
        page = 0

        while True:
            inblock = Ts8180InBlock()
            init_block(inblock)

            inblock.inq_gubunz1 = b"3"  # 계좌별 조회
            pwd_ptr = self._get_field_ptr(inblock, "pswd_noz8")
            self.wmca.set_account_index_pwd(
                pwd_ptr, acct_idx, self.creds.account_password,
            )
            trad_pwd_ptr1 = self._get_field_ptr(inblock, "trad_pswd1z8")
            self.wmca.set_order_pwd(trad_pwd_ptr1, self.creds.trade_password)
            trad_pwd_ptr2 = self._get_field_ptr(inblock, "trad_pswd2z8")
            self.wmca.set_order_pwd(trad_pwd_ptr2, self.creds.trade_password)
            inblock.group_noz4 = b"0000"
            inblock.mkt_slctz1 = b"0"
            inblock.order_datez8 = date.encode("ascii")
            inblock.comm_order_typez2 = b"CC"
            inblock.conc_gubunz1 = b"0"       # 전체
            inblock.inq_seq_gubunz1 = b"0"
            inblock.sort_gubunz1 = b"0"
            inblock.sell_buy_typez1 = b"0"
            inblock.mrgn_typez1 = b"0"
            inblock.accnt_admin_typez1 = b"0"
            inblock.order_noz10 = b"0000000000"

            ctypes.memmove(inblock.ctsz56, cts, 56)

            tr_index = self._trade_tr_counter
            self._trade_tr_counter += 1
            self.msg_loop.prepare(tr_index)

            self.wmca.query(
                self.msg_loop.hwnd, tr_index, "s8180",
                ctypes.cast(ctypes.addressof(inblock), ctypes.c_char_p),
                ctypes.sizeof(Ts8180InBlock),
                acct_idx,
            )

            blocks = self.msg_loop.wait_for_response(tr_index, timeout=10)
            trades, next_cts, has_next = self._parse_s8180(blocks)
            all_trades.extend(trades)

            if not has_next or not trades:
                break

            cts = next_cts
            page += 1

        return all_trades

    def disconnect(self):
        self.wmca.disconnect()
        self.msg_loop.stop()

    # --- Parsers ---

    def _parse_c8201(self, blocks: list) -> list[dict]:
        holdings = []

        for block_name, data in blocks:
            if block_name == "c8201OutBlock":
                if len(data) >= ctypes.sizeof(Tc8201OutBlock):
                    summary = Tc8201OutBlock.from_buffer_copy(data)
                    deposit = parse_field(summary.dpsit_amtz16, "ascii")
                    total_asset = parse_field(summary.asset_tot_amtz16, "ascii")
                    total_pl = parse_field(summary.tot_eal_plsz18, "ascii")
                    print(f"[NH] Account: deposit={deposit}, assets={total_asset}, P/L={total_pl}")

            elif block_name == "c8201OutBlock1":
                record_size = ctypes.sizeof(Tc8201OutBlock1)
                count = len(data) // record_size

                for i in range(count):
                    offset = i * record_size
                    record = Tc8201OutBlock1.from_buffer_copy(data[offset:offset + record_size])

                    stock_code = parse_field(record.issue_codez6, "ascii")
                    if not stock_code:
                        continue

                    stock_name = parse_field(record.issue_namez40, "euc-kr")
                    quantity = parse_int(record.bal_qtyz16)
                    slby_amt = parse_int(record.slby_amtz16)
                    current_price = parse_int(record.prsnt_pricez16)
                    profit_loss = parse_int(record.lsnpf_amtz16)
                    return_rate = parse_float(record.earn_ratez9)
                    eval_amount = parse_int(record.ass_amtz16)

                    # slby_amtz16은 1주당 매입단가
                    avg_price = slby_amt

                    holdings.append({
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "quantity": quantity,
                        "avg_price": avg_price,
                        "current_price": current_price,
                        "profit_loss": profit_loss,
                        "return_rate": return_rate,
                        "eval_amount": eval_amount,
                    })

        return holdings

    def _parse_s8180(self, blocks: list) -> tuple[list[dict], bytes, bool]:
        trades = []
        next_cts = b" " * 56
        has_next = False

        for block_name, data in blocks:
            if block_name == "s8180OutBlock1":
                record_size = ctypes.sizeof(Ts8180OutBlock1)
                count = len(data) // record_size

                for i in range(count):
                    offset = i * record_size
                    record = Ts8180OutBlock1.from_buffer_copy(data[offset:offset + record_size])

                    conc_qty = parse_int(record.conc_qtyz10)
                    trd_type_no = record.trd_gubun_noz1.strip()
                    stock_code_raw = parse_field(record.issue_codez12, "ascii")

                    if conc_qty <= 0:
                        continue

                    # trd_gubun_noz1 may be empty; fall back to order_kindz20
                    order_kind = parse_field(record.order_kindz20, "euc-kr")
                    if trd_type_no == b"2" or "매수" in order_kind:
                        trade_type = "buy"
                    elif trd_type_no == b"1" or "매도" in order_kind:
                        trade_type = "sell"
                    else:
                        continue

                    stock_code = stock_code_raw[:6].strip() if stock_code_raw else ""
                    if not stock_code:
                        continue

                    stock_name = parse_field(record.issue_namez40, "euc-kr")
                    price = parse_int(record.conc_unit_pricez12)
                    order_date = parse_field(record.order_datez8, "ascii")
                    proc_time = parse_field(record.proc_timez8, "ascii")
                    order_no = parse_field(record.order_noz10, "ascii")

                    traded_at = f"{order_date[:4]}-{order_date[4:6]}-{order_date[6:8]}"
                    if len(proc_time) >= 6:
                        traded_at += f" {proc_time[:2]}:{proc_time[2:4]}:{proc_time[4:6]}"
                    else:
                        traded_at += " 09:00:00"

                    trades.append({
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "trade_type": trade_type,
                        "quantity": conc_qty,
                        "price": price,
                        "total_amount": conc_qty * price,
                        "traded_at": traded_at,
                        "order_no": order_no,
                    })

            elif block_name == "s8180OutBlock_IN":
                if len(data) >= ctypes.sizeof(Ts8180OutBlock_IN):
                    pagination = Ts8180OutBlock_IN.from_buffer_copy(data)
                    next_cts = bytes(pagination.ctsz56)
                    has_next = pagination.nextbutton.strip() == b"1"

        return trades, next_cts, has_next
