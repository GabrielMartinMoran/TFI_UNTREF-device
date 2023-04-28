import random
from typing import Optional, List

from src.state.state_provider import StateProvider

AP_IF = 'AP_IF'
STA_IF = 'STA_IF'
AUTH_WPA_WPA2_PSK = 'AUTH_WPA_WPA2_PSK'


class WLAN:

    def __init__(self, ap_if: str) -> None:
        self._ap_if = ap_if
        self._status = False
        self._essid = None
        self._authmode = None
        self._password = None
        self._is_connected = False

    def active(self, status: bool) -> None:
        self._status = status

    def config(self, essid: str, authmode: Optional[str] = None, password: Optional[str] = None) -> None:
        self._essid = essid
        self._authmode = authmode
        self._password = password

    def scan(self) -> List[tuple]:
        configured_networks = StateProvider.get('wifi_network')
        if configured_networks is None:
            configured_networks = []
        return [tuple([x['ssid'].encode('utf-8')]) for x in configured_networks] + self._get_mocked_networks()

    def isconnected(self) -> bool:
        return self._is_connected

    def connect(self, ssid: str, password: str) -> None:
        self._is_connected = True

    @classmethod
    def _get_mocked_networks(cls) -> List[tuple[bytes]]:
        mocked_networks = []
        for x in range(random.randint(1, 10)):
            mocked_networks.append(tuple([f'MockedNetwork-{x}'.encode('utf-8')]))
        return mocked_networks
