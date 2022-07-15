import json

from src.config import HTTP_SERVER_HOST, HTTP_SERVER_PORT, HTTP_SERVER_MAX_CLIENTS, HTTP_SERVER_PRINT_LOGS
from src.http.http_server import HTTPServer
from src.wifi.wifi_network import WiFiNetwork
from src.wifi.wifi_client import WiFiClient


class ConfigurationWebAPI:

    def __init__(self, wifi_network: WiFiClient) -> None:
        self._wifi_network = wifi_network
        self._should_be_running = False
        self._server = HTTPServer(HTTP_SERVER_HOST, HTTP_SERVER_PORT, HTTP_SERVER_MAX_CLIENTS, HTTP_SERVER_PRINT_LOGS)
        self._add_routes()

    def start(self, threaded: bool = False) -> None:
        self._should_be_running = True
        self._server.start(threaded)

    def stop(self) -> None:
        self._should_be_running = False
        self._server.stop()

    @property
    def should_be_running(self) -> bool:
        return self._should_be_running

    def _add_routes(self) -> None:
        self._server.register_route('/api/health', self._health_route)
        self._server.register_route('/api/stop', self._stop_server_route)
        self._server.register_route('/api/configure', self._configure_route)
        self._server.register_route('/api/networks', self._get_configured_wifi_networks_route)

    def _health_route(self, params: dict) -> str:
        return json.dumps({'active': True})

    def _stop_server_route(self, params: dict) -> str:
        self._should_be_running = False
        return json.dumps({'stopping': True})

    def _configure_route(self, params: dict) -> str:
        params['ssid'] = params['ssid'].replace('%20', ' ')
        self._wifi_network.register_network(WiFiNetwork.from_dict(params))
        return json.dumps({})

    def _get_configured_wifi_networks_route(self, params: dict) -> str:
        return json.dumps([x.to_dict() for x in self._wifi_network.get_configured_networks()])
