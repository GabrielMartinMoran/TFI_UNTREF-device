import time

from src.config import LED_PIN, ON
from src.http.configuration_web_api import ConfigurationWebAPI
from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider
from src.status.status_updater import StatusUpdater
from src.wifi.access_point import AccessPoint
from src.wifi.wifi_client import WiFiClient

if PlatformChecker.is_device():
    import machine
else:
    import platform_mocks.machine as machine


class Orchestrator:

    def __init__(self, ap: AccessPoint, wifi_client: WiFiClient, measures_taker: MeasuresTaker,
                 measures_sender: MeasuresSender, status_updater: StatusUpdater) -> None:
        self._ap = ap
        self._wifi_client = wifi_client
        self._measures_taker = measures_taker
        self._measures_sender = measures_sender
        self._status_updater = status_updater
        self._config_web_api = ConfigurationWebAPI(wifi_client, status_updater)
        self._led = machine.Pin(LED_PIN, machine.Pin.OUT)

    def start(self) -> None:
        self._led.value(ON)
        self._ap.start()
        self._config_web_api.start(True)
        self._run_orchestration_loop()

    def _run_orchestration_loop(self) -> None:
        while True:
            time.sleep(1)
            self._orchestrate()

    def _orchestrate(self) -> None:
        if not self._wifi_client.has_any_network_configured() or not self._is_configured():
            return

        self._try_connect_to_wifi()

        if self._status_updater.is_turned_on():
            # It only has to take measures when the device is turned on
            self._measures_taker.take_measure()

        self._measures_sender.pull_and_send(self._status_updater.is_turned_on())

        self._status_updater.update_status()

    def _try_connect_to_wifi(self) -> None:
        while not self._wifi_client.is_connected():
            self._wifi_client.connect()
            time.sleep(1)

    @classmethod
    def _is_configured(cls) -> bool:
        return StateProvider.get('token') is not None and StateProvider.get('device_id') is not None
