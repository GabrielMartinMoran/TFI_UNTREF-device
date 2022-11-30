from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
from src.state.state_provider import StateProvider
from src.status.status_updater import StatusUpdater
from src.wifi.access_point import AccessPoint
from src.config import LED_PIN, ON
from src.http.configuration_web_api import ConfigurationWebAPI
from src.platform_checker import PlatformChecker
from src.wifi.wifi_client import WiFiClient

if PlatformChecker.is_device():
    import machine
else:
    import platform_mocks.machine as machine
import time


def is_configured() -> bool:
    return StateProvider.get('token') is not None and StateProvider.get('device_id') is not None


def main() -> None:
    led = machine.Pin(LED_PIN, machine.Pin.OUT)

    ap = AccessPoint()
    ap.start()

    wifi_client = WiFiClient()
    measures_taker = MeasuresTaker()
    measures_sender = MeasuresSender(measures_taker)
    status_updater = StatusUpdater()

    config_web_api = ConfigurationWebAPI(wifi_client, status_updater)
    config_web_api.start(True)

    while True:
        time.sleep(1)
        if not wifi_client.has_any_network_configured() or not is_configured():
            continue
        while not wifi_client.is_connected():
            wifi_client.connect()
            time.sleep(1)

        if status_updater.is_turned_on():
            # It only has to take measures when the device is turned on
            measures_taker.take_measure()

        measures_sender.pull_and_send(status_updater.is_turned_on())

        status_updater.update_status()

    led.value(ON)
