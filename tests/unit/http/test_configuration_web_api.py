from unittest.mock import patch

import pytest

from src.config import HTTP_SERVER_HOST, HTTP_SERVER_PORT, HTTP_SERVER_MAX_CLIENTS, HTTP_SERVER_PRINT_LOGS
from src.http.configuration_web_api import ConfigurationWebAPI
from src.state.state_provider import StateProvider
from src.wifi.wifi_network import WiFiNetwork
from tests.mocks.http_server_mock import HTTPServerMock


@pytest.fixture(autouse=True)
@patch('src.wifi.wifi_client.WiFiClient')
@patch('src.status.status_updater.StatusUpdater')
def configuration_web_api(WiFiClientMock, StatusUpdaterMock) -> ConfigurationWebAPI:
    wifi_client_mock = WiFiClientMock()
    status_updater_mock = StatusUpdaterMock()
    instance = ConfigurationWebAPI(wifi_client_mock, status_updater_mock)

    # Mock HTTPServer
    mocked_server = HTTPServerMock(HTTP_SERVER_HOST, HTTP_SERVER_PORT, HTTP_SERVER_MAX_CLIENTS,
                                   HTTP_SERVER_PRINT_LOGS)
    mocked_server._routes = instance._server._routes
    instance._server = mocked_server

    return instance


def test_configuration_web_api_registers_routes_when_init(configuration_web_api):
    assert configuration_web_api._server._routes == {
        'GET|/api/device_id': configuration_web_api._get_device_id_route,
        'GET|/api/health': configuration_web_api._health_route,
        'GET|/api/networks': configuration_web_api._get_available_networks_route,
        'GET|/api/networks/configured': configuration_web_api._get_configured_wifi_networks_route,
        'GET|/api/stop': configuration_web_api._stop_server_route,
        'POST|/api/device_id': configuration_web_api._set_device_id_route,
        'POST|/api/networks': configuration_web_api._configure_network_route,
        'POST|/api/status': configuration_web_api._set_device_status_route,
        'POST|/api/token': configuration_web_api._register_token_route
    }


def test_start_starts_the_http_server(configuration_web_api):
    configuration_web_api.start()

    assert configuration_web_api._should_be_running
    assert configuration_web_api._server.running


def test_stop_stops_the_http_server(configuration_web_api):
    configuration_web_api.start()
    configuration_web_api.stop()

    assert not configuration_web_api._should_be_running
    assert not configuration_web_api._server.running


def test_health_route(configuration_web_api):
    expected = {'active': True}

    actual = configuration_web_api._health_route({}, {})

    assert actual == expected


def test_stop_server_route(configuration_web_api):
    configuration_web_api.start()

    expected = {'stopping': True}

    actual = configuration_web_api._stop_server_route({}, {})

    assert actual == expected
    assert not configuration_web_api._should_be_running


def test_get_available_networks_route(configuration_web_api):
    configuration_web_api._wifi_client.get_available_networks = lambda: ['Network 1', 'Network 2']

    expected = ['Network 1', 'Network 2']

    actual = configuration_web_api._get_available_networks_route({}, {})

    assert actual == expected


def test_configure_network_route(configuration_web_api):
    actual = configuration_web_api._configure_network_route({}, {
        'ssid': 'Network',
        'password': '1234'
    })

    assert actual == {}
    configuration_web_api._wifi_client.register_network.assert_called()
    called_wifi_network = configuration_web_api._wifi_client.register_network.call_args[0][0]
    assert called_wifi_network.ssid == 'Network'
    assert called_wifi_network.password == '1234'


def test_get_configured_wifi_networks_route(configuration_web_api):
    configuration_web_api._wifi_client.get_configured_networks = lambda: [WiFiNetwork('Network', '1234')]

    expected = [{
        'ssid': 'Network',
        'password': '1234'
    }]

    actual = configuration_web_api._get_configured_wifi_networks_route({}, {})

    assert actual == expected


def test_register_token_route(configuration_web_api):
    actual = configuration_web_api._register_token_route({}, {'token': 'TOKEN'})

    assert actual == {}
    assert StateProvider.get('token') == 'TOKEN'


def test_get_device_id_route(configuration_web_api):
    StateProvider.put('device_id', 'test_device_id')

    actual = configuration_web_api._get_device_id_route({}, {})

    assert actual == {'device_id': 'test_device_id'}


def test_set_device_id_route(configuration_web_api):
    actual = configuration_web_api._set_device_id_route({}, {'device_id': 'test_device_id'})

    assert actual == {}
    assert StateProvider.get('device_id') == 'test_device_id'


def test_set_device_id_raises_error_when_device_already_has_an_configured_id(configuration_web_api):
    StateProvider.put('device_id', 'test_device_id')

    with pytest.raises(AssertionError) as exc_info:
        configuration_web_api._set_device_id_route({}, {'device_id': 'new_device_id'})
    assert exc_info.value.args[0] == 'device_id already set'


def test_set_device_status_route(configuration_web_api):
    actual = configuration_web_api._set_device_status_route({}, {'turn_on': True})

    assert actual == {}
    configuration_web_api._status_updater.set_status.assert_called_with(True)


def test_set_device_status_route_raises_error_when_turn_on_is_not_provided(configuration_web_api):
    with pytest.raises(AssertionError) as exc_info:
        configuration_web_api._set_device_status_route({}, {})
    assert exc_info.value.args[0] == 'turn_on is required'


def test_set_device_status_route_raises_error_when_turn_on_is_not_a_bool(configuration_web_api):
    with pytest.raises(AssertionError) as exc_info:
        configuration_web_api._set_device_status_route({}, {'turn_on': 'TRUE'})
    assert exc_info.value.args[0] == 'turn_on must be a valid boolean'
