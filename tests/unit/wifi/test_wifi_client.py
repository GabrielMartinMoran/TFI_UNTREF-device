import pytest
from unittest.mock import patch

from src.wifi.wifi_client import WiFiClient
from src.wifi.wifi_network import WiFiNetwork


@pytest.fixture
def wifi_client() -> WiFiClient:
    return WiFiClient()


def test_has_any_network_configured_returns_false_when_no_networks_configured(wifi_client):
    assert not wifi_client.has_any_network_configured()


def test_has_any_network_configured_returns_true_when_networks_configured(wifi_client):
    wifi_client.register_network(WiFiNetwork('my_network', 'my_password'))
    assert wifi_client.has_any_network_configured()


def test_load_configured_networks_returns_empty_list_when_no_networks_configured(wifi_client):
    assert wifi_client._load_configured_networks() == []


def test_load_configured_networks_returns_list_of_networks_when_networks_configured(wifi_client):
    expected_network = WiFiNetwork('my_network', 'my_password')
    wifi_client.register_network(expected_network)
    assert len(wifi_client._load_configured_networks()) == 1
    assert wifi_client._load_configured_networks()[0].ssid == expected_network.ssid
    assert wifi_client._load_configured_networks()[0].password == expected_network.password


def test_register_network_adds_network_to_list_of_configured_networks(wifi_client):
    expected_network = WiFiNetwork('my_network', 'my_password')
    wifi_client.register_network(expected_network)
    assert wifi_client._wifi_networks == [expected_network]


def test_register_network_overrides_existing_network(wifi_client):
    network1 = WiFiNetwork('my_network', 'my_password')
    network2 = WiFiNetwork('my_network', 'my_new_password')
    wifi_client.register_network(network1)
    wifi_client.register_network(network2)
    assert wifi_client._wifi_networks == [network2]


def test_get_configured_networks_returns_list_of_configured_networks(wifi_client):
    expected_networks = [
        WiFiNetwork('network1', 'password1'),
        WiFiNetwork('network2', 'password2')
    ]
    for network in expected_networks:
        wifi_client.register_network(network)
    assert wifi_client.get_configured_networks() == expected_networks


def test_connect_prints_error_message_when_no_networks_configured(wifi_client, capsys):
    wifi_client.connect()
    captured = capsys.readouterr()
    assert 'Can not connect to WiFi: There are no networks configured.\n' == captured.out


@patch('src.wifi.wifi_client.WiFiClient._try_connect_to_network')
@patch('src.wifi.wifi_client.WiFiClient.is_connected', return_value=True)
@patch('src.wifi.wifi_client.WiFiClient.get_available_networks', return_value=['my_network'])
def test_connect_calls_try_connect_to_network_for_each_registered_network(
        mock_get_available_networks, mock_is_connected, mock_try_connect_to_network, wifi_client, capsys
):
    expected_networks = [
        WiFiNetwork('my_network', 'password1')
    ]
    for network in expected_networks:
        wifi_client.register_network(network)
    wifi_client.connect()
    assert mock_try_connect_to_network.call_count == len(expected_networks)
