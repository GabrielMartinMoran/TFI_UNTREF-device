from src.measures.measures_sender import MeasuresSender
from src.measures.measures_taker import MeasuresTaker
from src.orchestrator import Orchestrator
from src.status.status_updater import StatusUpdater
from src.wifi.access_point import AccessPoint
from src.wifi.wifi_client import WiFiClient


def main() -> None:
    # Instantiate the dependencies
    ap = AccessPoint()
    wifi_client = WiFiClient()
    measures_taker = MeasuresTaker()
    measures_sender = MeasuresSender(measures_taker)
    status_updater = StatusUpdater()

    # Instantiate the orchestrator injecting the dependencies
    orchestrator = Orchestrator(ap, wifi_client, measures_taker, measures_sender, status_updater)

    # Start the orchestrator
    orchestrator.start()
