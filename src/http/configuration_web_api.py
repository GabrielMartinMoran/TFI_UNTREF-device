from src.config import HTTP_SERVER_HOST, HTTP_SERVER_PORT, HTTP_SERVER_MAX_CLIENTS, HTTP_SERVER_PRINT_LOGS
from src.http import http_methods
from src.http.http_server import HTTPServer
from src.state.state_provider import StateProvider
from src.status.status_updater import StatusUpdater
from src.wifi.wifi_network import WiFiNetwork
from src.wifi.wifi_client import WiFiClient


class ConfigurationWebAPI:

    def __init__(self, wifi_client: WiFiClient, status_updater: StatusUpdater) -> None:
        self._wifi_client = wifi_client
        self._status_updater = status_updater
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
        self._server.register_route(http_methods.GET, '/api/health', self._health_route)
        self._server.register_route(http_methods.GET, '/api/stop', self._stop_server_route)
        self._server.register_route(http_methods.GET, '/api/networks', self._get_available_networks_route)
        self._server.register_route(http_methods.POST, '/api/networks', self._configure_network_route)
        self._server.register_route(http_methods.GET, '/api/networks/configured',
                                    self._get_configured_wifi_networks_route)
        self._server.register_route(http_methods.POST, '/api/token', self._register_token_route)
        self._server.register_route(http_methods.GET, '/api/device_id', self._get_device_id_route)
        self._server.register_route(http_methods.POST, '/api/device_id', self._set_device_id_route)
        self._server.register_route(http_methods.POST, '/api/status', self._set_device_status_route)

    def _health_route(self, params: dict, body: dict) -> dict:
        return {'active': True}

    def _stop_server_route(self, params: dict, body: dict) -> dict:
        self._should_be_running = False
        return {'stopping': True}

    def _get_available_networks_route(self, params: dict, body: dict) -> 'List[str]':
        return self._wifi_client.get_available_networks()

    def _configure_network_route(self, params: dict, body: dict) -> dict:
        self._wifi_client.register_network(WiFiNetwork.from_dict(body))
        return {}

    def _get_configured_wifi_networks_route(self, params: dict, body: dict) -> 'List[dict]':
        return [x.to_dict() for x in self._wifi_client.get_configured_networks()]

    def _register_token_route(self, params: dict, body: dict) -> dict:
        StateProvider.put('token', body['token'])
        return {}

    def _get_device_id_route(self, params: dict, body: dict) -> dict:
        return {'device_id': StateProvider.get('device_id')}

    def _set_device_id_route(self, params: dict, body: dict) -> dict:
        if StateProvider.get('device_id') is not None:
            raise AssertionError('device_id already set')
        StateProvider.put('device_id', body['device_id'])
        return {}

    def _set_device_status_route(self, params: dict, body: dict) -> dict:
        assert 'turn_on' in body, 'turn_on is required'
        assert isinstance(body['turn_on'], bool), 'turn_on must be a valid boolean'
        self._status_updater.set_status(body['turn_on'])
        return {}
