import ctypes
import os

from .config import DLL_DIR, DLL_PATH


class WmcaWrapper:
    def __init__(self):
        self._dll = None

    def load(self) -> bool:
        os.chdir(DLL_DIR)
        self._dll = ctypes.WinDLL(DLL_PATH)
        return bool(self._dll.wmcaLoad())

    def free(self) -> bool:
        if self._dll:
            return bool(self._dll.wmcaFree())
        return False

    def set_server(self, server: str) -> bool:
        self._dll.wmcaSetServer.argtypes = [ctypes.c_char_p]
        self._dll.wmcaSetServer.restype = ctypes.c_bool
        return self._dll.wmcaSetServer(server.encode("ascii"))

    def set_port(self, port: int) -> bool:
        self._dll.wmcaSetPort.argtypes = [ctypes.c_int]
        self._dll.wmcaSetPort.restype = ctypes.c_bool
        return self._dll.wmcaSetPort(port)

    def is_connected(self) -> bool:
        self._dll.wmcaIsConnected.restype = ctypes.c_bool
        return self._dll.wmcaIsConnected()

    def connect(self, hwnd, msg, media_type, user_type, user_id, password, cert_password) -> bool:
        self._dll.wmcaConnect.argtypes = [
            ctypes.c_void_p, ctypes.c_uint,
            ctypes.c_char, ctypes.c_char,
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
        ]
        self._dll.wmcaConnect.restype = ctypes.c_bool
        return self._dll.wmcaConnect(
            hwnd, msg,
            media_type if isinstance(media_type, bytes) else media_type.encode(),
            user_type if isinstance(user_type, bytes) else user_type.encode(),
            user_id.encode("ascii") if isinstance(user_id, str) else user_id,
            password.encode("ascii") if isinstance(password, str) else password,
            cert_password.encode("ascii") if isinstance(cert_password, str) else cert_password,
        )

    def disconnect(self) -> bool:
        if self._dll:
            self._dll.wmcaDisconnect.restype = ctypes.c_bool
            return self._dll.wmcaDisconnect()
        return False

    def query(self, hwnd, tr_index, tr_code, input_data, input_len, account_index) -> bool:
        self._dll.wmcaQuery.argtypes = [
            ctypes.c_void_p, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
        ]
        self._dll.wmcaQuery.restype = ctypes.c_bool
        return self._dll.wmcaQuery(
            hwnd, tr_index,
            tr_code.encode("ascii") if isinstance(tr_code, str) else tr_code,
            input_data, input_len, account_index,
        )

    def set_account_index_pwd(self, hash_out, account_index, password) -> bool:
        self._dll.wmcaSetAccountIndexPwd.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
        ]
        self._dll.wmcaSetAccountIndexPwd.restype = ctypes.c_bool
        return self._dll.wmcaSetAccountIndexPwd(
            hash_out, account_index,
            password.encode("ascii") if isinstance(password, str) else password,
        )

    def set_order_pwd(self, hash_out, password) -> bool:
        self._dll.wmcaSetOrderPwd.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p,
        ]
        self._dll.wmcaSetOrderPwd.restype = ctypes.c_bool
        return self._dll.wmcaSetOrderPwd(
            hash_out,
            password.encode("ascii") if isinstance(password, str) else password,
        )

    def set_option(self, key: str, value: str) -> bool:
        self._dll.wmcaSetOption.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._dll.wmcaSetOption.restype = ctypes.c_bool
        return self._dll.wmcaSetOption(key.encode("ascii"), value.encode("ascii"))
