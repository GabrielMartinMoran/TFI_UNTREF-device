import time

from _thread import start_new_thread

from src.http.configuration_web_api import ConfigurationWebAPI
from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
from src.state.state_provider import StateProvider
from src.status.device_status import DeviceStatus
from src.status.mechanical_status_change_detector import MechanicalStatusChangeDetector
from src.status.remote_status_change_detector import RemoteStatusChangeDetector
from src.wifi.access_point import AccessPoint
from src.wifi.wifi_client import WiFiClient


class Orchestrator:

    def __init__(self, ap: AccessPoint, wifi_client: WiFiClient, measures_taker: MeasuresTaker,
                 measures_sender: MeasuresSender, device_status: DeviceStatus,
                 remote_status_change_detector: RemoteStatusChangeDetector,
                 mechanical_status_change_detector: MechanicalStatusChangeDetector,
                 configuration_web_api: ConfigurationWebAPI) -> None:
        self._ap = ap
        self._wifi_client = wifi_client
        self._measures_taker = measures_taker
        self._measures_sender = measures_sender
        self._device_status = device_status
        self._remote_status_change_detector = remote_status_change_detector
        self._mechanical_status_change_detector = mechanical_status_change_detector
        self._configuration_web_api = configuration_web_api

    def start(self) -> None:
        self._ap.start()
        self._configuration_web_api.start(True)
        start_new_thread(self._mechanical_status_change_detector.start_detection, ())
        self._run_orchestration_loop()

    def _run_orchestration_loop(self) -> None:
        while True:
            time.sleep(1)
            self._orchestrate()

    def _orchestrate(self) -> None:
        if not self._wifi_client.has_any_network_configured() or not self._is_configured():
            return

        self._try_connect_to_wifi()

        if self._device_status.is_turned_on():
            # It only has to take measures when the device is turned on
            self._measures_taker.take_measure()

        self._measures_sender.pull_and_send(self._device_status.is_turned_on())

        self._remote_status_change_detector.update_status()

        self._device_status.send_current_status_if_required()

    def _try_connect_to_wifi(self) -> None:
        while not self._wifi_client.is_connected():
            self._wifi_client.connect()
            time.sleep(1)

    @classmethod
    def _is_configured(cls) -> bool:
        return StateProvider.get('token') is not None and StateProvider.get('device_id') is not None
