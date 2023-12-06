import time
from typing import List

from src.config import WIFI_CLIENT_MAX_CONNECTION_ATTEMPTS, WIFI_CLIENT_DELAY_BETWEEN_ATTEMPTS, \
    SYNC_TIME_MAX_ATTEMPTS, SYNC_TIME_DELAY_BETWEEN_ATTEMPTS
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from network import WLAN, STA_IF
    import ntptime
else:
    from platform_mocks.network import WLAN, STA_IF
    from platform_mocks import ntptime

from src.state.state_provider import StateProvider
from src.wifi.wifi_network import WiFiNetwork


class WiFiClient:
    _WIFI_NETWORK_STATE_KEY = 'wifi_network'

    def __init__(self) -> None:
        self._wifi_networks = self._load_configured_networks()
        self._sta_if = WLAN(STA_IF)

    def has_any_network_configured(self) -> bool:
        return len(self._wifi_networks) > 0

    def _load_configured_networks(self) -> List[WiFiNetwork]:
        config = StateProvider.get(self._WIFI_NETWORK_STATE_KEY)
        if config is None:
            return []
        return [WiFiNetwork.from_dict(x) for x in config]

    def register_network(self, wifi_network: WiFiNetwork) -> None:
        # If the network is already registered override it
        already_registered_network = [x for x in self._wifi_networks if x.ssid == wifi_network.ssid]
        already_registered_network = already_registered_network[0] if len(already_registered_network) > 0 else None
        if already_registered_network is not None:
            self._wifi_networks.remove(already_registered_network)
        self._wifi_networks.append(wifi_network)
        StateProvider.set(self._WIFI_NETWORK_STATE_KEY, [x.to_dict() for x in self._wifi_networks])

    def get_configured_networks(self) -> List[WiFiNetwork]:
        return self._wifi_networks

    def connect(self) -> None:
        if not self.has_any_network_configured():
            print('Can not connect to WiFi: There are no networks configured.')
            return
        self._sta_if.active(True)
        available_networks = self.get_available_networks()
        print(f'Available WiFi networks: {", ".join(available_networks)}')
        for network in self._wifi_networks:
            if network.ssid in available_networks:
                print(f'Trying to connect to WiFi network {network.ssid}')
                self._try_connect_to_network(network)
                if self.is_connected():
                    print(f'Connected successfully to WiFi network {network.ssid}')
                    self._try_sync_time()
                    return

    def get_available_networks(self) -> List[str]:
        self._sta_if.active(True)
        return [x[0].decode('utf-8') for x in self._sta_if.scan()]

    def is_connected(self) -> bool:
        return self._sta_if.isconnected()

    def _try_connect_to_network(self, network: WiFiNetwork) -> None:
        attempts = 1
        while not self._sta_if.isconnected() and attempts <= WIFI_CLIENT_MAX_CONNECTION_ATTEMPTS:
            print(f'Attempt number {attempts}...')
            try:
                self._sta_if.connect(network.ssid, network.password)
            except Exception as e:
                print(str(e))
            attempts += 1
            time.sleep(WIFI_CLIENT_DELAY_BETWEEN_ATTEMPTS)

    @classmethod
    def _try_sync_time(cls) -> None:
        attempts = 1
        while attempts <= SYNC_TIME_MAX_ATTEMPTS:
            try:
                ntptime.settime()
                print('Time synchronized successfully!')
                return
            except Exception as e:
                print(f'An error has occurred when trying to synchronize the time: {str(e)}')
                attempts += 1
                time.sleep(SYNC_TIME_DELAY_BETWEEN_ATTEMPTS)
