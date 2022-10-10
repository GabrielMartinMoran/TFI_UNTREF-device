from src.exceptions.unauthenticated_exception import UnauthenticatedException
from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
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


def main() -> None:
    led = machine.Pin(LED_PIN, machine.Pin.OUT)

    ap = AccessPoint()
    ap.start()

    wifi_client = WiFiClient()

    config_web_api = ConfigurationWebAPI(wifi_client)
    config_web_api.start(True)

    measures_taker = MeasuresTaker()
    measures_sender = MeasuresSender()

    while True:
        time.sleep(1)
        if not wifi_client.has_any_network_configured():
            continue
        while not wifi_client.is_connected():
            wifi_client.connect()
            time.sleep(1)
        measures_taker.take_measure()
        measures = measures_taker.measures
        try:
            could_send = measures_sender.send_measures(measures)
            if could_send:
                measures_taker.clear_measures(measures)
        except UnauthenticatedException:
            print('ERROR: Unauthenticated')

    led.value(ON)
