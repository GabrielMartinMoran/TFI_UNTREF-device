from src.components.relay import Relay
from src.components.status_led import StatusLed
from src.http.configuration_web_api import ConfigurationWebAPI
from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
from src.orchestrator import Orchestrator
from src.status.device_status import DeviceStatus
from src.status.mechanical_status_change_detector import MechanicalStatusChangeDetector
from src.status.remote_status_change_detector import RemoteStatusChangeDetector
from src.status.status_sender import StatusSender
from src.wifi.access_point import AccessPoint
from src.wifi.wifi_client import WiFiClient


def main() -> None:
    # Instantiate the dependencies
    ap = AccessPoint()
    wifi_client = WiFiClient()

    status_led = StatusLed(False)
    relay = Relay(False)

    # Measures
    measures_taker = MeasuresTaker()
    measures_sender = MeasuresSender(measures_taker)

    # Status
    status_sender = StatusSender()
    device_status = DeviceStatus(status_sender, status_led, relay)
    remote_status_change_detector = RemoteStatusChangeDetector(device_status)
    mechanical_status_change_detector = MechanicalStatusChangeDetector(device_status)

    configuration_web_api = ConfigurationWebAPI(wifi_client, device_status)

    # Instantiate the orchestrator injecting the dependencies
    orchestrator = Orchestrator(
        ap,
        wifi_client,
        measures_taker,
        measures_sender,
        device_status,
        remote_status_change_detector,
        mechanical_status_change_detector,
        configuration_web_api
    )

    # Start the orchestrator
    orchestrator.start()

    """
    # Code for testing ACS712 current sensor
    from src.components.relay import Relay

    relay = Relay(False)

    measures_taker = MeasuresTaker()

    relay.set_status(True)

    ITERATIONS = 50

    print('{')
    for i in range(ITERATIONS):  # 50 iteraciones
        measures = measures_taker.debug_take_measures()
        print(f'{i + 1}: [{", ".join(measures)}]{"," if i < ITERATIONS - 1 else ""}')
        del measures
    print('}')
    """
