import ctypes
import ctypes.wintypes
import time

from .structs import (
    CA_WMCAEVENT, CA_CONNECTED, CA_RECEIVEDATA,
    CA_RECEIVEMESSAGE, CA_RECEIVECOMPLETE, CA_RECEIVEERROR,
    LOGINBLOCK, LOGININFO, ACCOUNTINFO, OUTDATABLOCK, MSGHEADER,
)

user32 = ctypes.windll.user32

# ANSI Win32 API types
WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_long,
)


class WNDCLASSEXA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("style", ctypes.c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.c_void_p),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.c_char_p),
        ("lpszClassName", ctypes.c_char_p),
        ("hIconSm", ctypes.c_void_p),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_uint),
        ("lParam", ctypes.c_long),
        ("time", ctypes.c_uint),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]


class NHMessageLoop:
    def __init__(self):
        self.hwnd = None
        self._wndproc_ref = None  # prevent GC of callback
        self._login_info = None
        self._login_done = False
        self._responses = {}  # tr_index -> list of (block_name, data)
        self._completed = set()
        self._errors = {}

    def create_window(self) -> bool:
        hinstance = ctypes.windll.kernel32.GetModuleHandleA(None)
        class_name = b"NHSyncWnd"

        self._wndproc_ref = WNDPROC(self._wndproc)

        wc = WNDCLASSEXA()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXA)
        wc.lpfnWndProc = self._wndproc_ref
        wc.hInstance = hinstance
        wc.lpszClassName = class_name

        atom = user32.RegisterClassExA(ctypes.byref(wc))
        if not atom:
            return False

        self.hwnd = user32.CreateWindowExA(
            0, class_name, b"NHSync", 0,
            0, 0, 0, 0,
            None, None, hinstance, None,
        )
        return self.hwnd is not None and self.hwnd != 0

    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg == CA_WMCAEVENT:
            self._on_event(wparam, lparam)
            return 0
        return user32.DefWindowProcA(hwnd, msg, wparam, lparam)

    def _on_event(self, event_type, lparam):
        if event_type == CA_CONNECTED:
            self._on_login(lparam)
        elif event_type == CA_RECEIVEDATA:
            self._on_receive_data(lparam)
        elif event_type == CA_RECEIVEMESSAGE:
            self._on_receive_message(lparam)
        elif event_type == CA_RECEIVECOMPLETE:
            self._on_receive_complete(lparam)
        elif event_type == CA_RECEIVEERROR:
            self._on_receive_error(lparam)

    def _on_login(self, lparam):
        block = ctypes.cast(lparam, ctypes.POINTER(LOGINBLOCK)).contents
        info = block.pLoginInfo.contents

        acct_count_str = bytes(info.szAccountCount).decode("ascii", errors="replace").strip()
        acct_count = int(acct_count_str) if acct_count_str.isdigit() else 0

        self._login_info = {
            "date": bytes(info.szDate).decode("ascii", errors="replace").strip(),
            "server": bytes(info.szServerName).decode("ascii", errors="replace").strip(),
            "user_id": bytes(info.szUserID).decode("ascii", errors="replace").strip(),
            "account_count": acct_count,
            "accounts": [],
        }

        print(f"[NH] Connected - {acct_count} account(s)")
        for i in range(acct_count):
            acct = info.accountlist[i]
            no = bytes(acct.szAccountNo).decode("ascii", errors="replace").strip()
            name = bytes(acct.szAccountName).decode("euc-kr", errors="replace").strip()
            pdt = bytes(acct.act_pdt_cdz3).decode("ascii", errors="replace").strip()
            print(f"  [{i+1}] {no} ({name}) product={pdt}")
            self._login_info["accounts"].append({"no": no, "name": name, "product": pdt})

        self._login_done = True

    def _on_receive_data(self, lparam):
        out = ctypes.cast(lparam, ctypes.POINTER(OUTDATABLOCK)).contents
        tr_index = out.TrIndex
        received = out.pData.contents

        block_name = received.szBlockName.decode("ascii", errors="replace") if received.szBlockName else ""
        data = ctypes.string_at(received.szData, received.nLen) if received.szData and received.nLen > 0 else b""

        print(f"[NH] Data [{tr_index}] block={block_name}, len={received.nLen}")

        if tr_index not in self._responses:
            self._responses[tr_index] = []
        self._responses[tr_index].append((block_name, data))

    def _on_receive_message(self, lparam):
        out = ctypes.cast(lparam, ctypes.POINTER(OUTDATABLOCK)).contents
        tr_index = out.TrIndex
        received = out.pData.contents

        if received.szData and received.nLen >= ctypes.sizeof(MSGHEADER):
            msg_hdr = MSGHEADER.from_buffer_copy(ctypes.string_at(received.szData, min(received.nLen, ctypes.sizeof(MSGHEADER))))
            code = bytes(msg_hdr.msg_cd).decode("ascii", errors="replace").strip()
            text = bytes(msg_hdr.user_msg).decode("euc-kr", errors="replace").strip()
            print(f"[NH] Message [{tr_index}] {code}: {text}")

    def _on_receive_complete(self, lparam):
        out = ctypes.cast(lparam, ctypes.POINTER(OUTDATABLOCK)).contents
        tr_index = out.TrIndex
        print(f"[NH] Complete [{tr_index}]")
        self._completed.add(tr_index)

    def _on_receive_error(self, lparam):
        out = ctypes.cast(lparam, ctypes.POINTER(OUTDATABLOCK)).contents
        tr_index = out.TrIndex
        received = out.pData.contents

        error_msg = ""
        if received.szData and received.nLen >= ctypes.sizeof(MSGHEADER):
            msg_hdr = MSGHEADER.from_buffer_copy(ctypes.string_at(received.szData, min(received.nLen, ctypes.sizeof(MSGHEADER))))
            error_msg = bytes(msg_hdr.user_msg).decode("euc-kr", errors="replace").strip()

        print(f"[NH] Error [{tr_index}]: {error_msg}")
        self._errors[tr_index] = error_msg
        self._completed.add(tr_index)

    def pump_messages(self, duration_ms=10):
        msg = MSG()
        deadline = time.monotonic() + duration_ms / 1000.0
        while time.monotonic() < deadline:
            while user32.PeekMessageA(ctypes.byref(msg), None, 0, 0, 1):  # PM_REMOVE=1
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
            time.sleep(0.01)

    def prepare(self, tr_index):
        self._responses.pop(tr_index, None)
        self._completed.discard(tr_index)
        self._errors.pop(tr_index, None)

    def wait_for_login(self, timeout=15):
        self._login_done = False
        self._login_info = None
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.pump_messages(100)
            if self._login_done:
                return self._login_info
        return {"error": "login timeout"}

    def wait_for_response(self, tr_index, timeout=10) -> list:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.pump_messages(100)
            if tr_index in self._completed:
                return self._responses.get(tr_index, [])
        print(f"[NH] Timeout waiting for TR {tr_index}")
        return self._responses.get(tr_index, [])

    def stop(self):
        if self.hwnd:
            user32.DestroyWindow(self.hwnd)
            self.hwnd = None
