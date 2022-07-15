from src.config import AP_PASSWORD, AP_SSID
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from network import WLAN, AP_IF, AUTH_WPA_WPA2_PSK
else:
    from platform_mocks.network import WLAN, AP_IF, AUTH_WPA_WPA2_PSK


class AccessPoint:

    def __init__(self) -> None:
        self._ap_if = WLAN(AP_IF)

    def start(self) -> None:
        self._ap_if.active(True)
        self._ap_if.config(essid=AP_SSID, authmode=AUTH_WPA_WPA2_PSK, password=AP_PASSWORD)

    def stop(self) -> None:
        self._ap_if.active(False)
