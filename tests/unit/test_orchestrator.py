import pytest
from unittest.mock import MagicMock, patch

from src.orchestrator import Orchestrator


@pytest.fixture
def mock_ap():
    return MagicMock()


@pytest.fixture
def mock_wifi_client():
    return MagicMock()


@pytest.fixture
def mock_measures_taker():
    return MagicMock()


@pytest.fixture
def mock_measures_sender():
    return MagicMock()


@pytest.fixture
def mock_status_updater():
    return MagicMock()


def test_is_configured_method_returns_true_when_token_and_device_id_are_set():
    mock_state_provider = MagicMock()
    mock_state_provider.get.side_effect = ['my_token', 'my_device_id']
    with patch('src.orchestrator.StateProvider', mock_state_provider):
        is_configured = Orchestrator._is_configured()
        assert is_configured is True


def test_is_configured_method_returns_false_when_token_is_not_set():
    mock_state_provider = MagicMock()
    mock_state_provider.get.side_effect = [None, 'my_device_id']
    with patch('src.orchestrator.StateProvider', mock_state_provider):
        is_configured = Orchestrator._is_configured()
        assert is_configured is False


def test_is_configured_method_returns_false_when_device_id_is_not_set():
    mock_state_provider = MagicMock()
    mock_state_provider.get.side_effect = ['my_token', None]
    with patch('src.orchestrator.StateProvider', mock_state_provider):
        is_configured = Orchestrator._is_configured()
        assert is_configured is False


def test_orchestrate_with_no_configured_networks():
    ap = MagicMock()
    wifi_client = MagicMock()
    wifi_client.has_any_network_configured.return_value = False
    measures_taker = MagicMock()
    measures_sender = MagicMock()
    device_status = MagicMock()
    remote_status_change_detector = MagicMock()
    mechanical_status_change_detector = MagicMock()
    configuration_web_api = MagicMock()

    orchestrator = Orchestrator(ap, wifi_client, measures_taker, measures_sender, device_status,
                                remote_status_change_detector, mechanical_status_change_detector, configuration_web_api)

    orchestrator._orchestrate()

    wifi_client.has_any_network_configured.assert_called_once()
    wifi_client.is_connected.assert_not_called()
    measures_taker.take_measure.assert_not_called()
    measures_sender.pull_and_send.assert_not_called()
    remote_status_change_detector.update_status.assert_not_called()
