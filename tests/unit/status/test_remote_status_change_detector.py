import pytest
from unittest.mock import Mock, patch, MagicMock

from src.status.actions.device_action import DeviceAction
from src.status.remote_status_change_detector import RemoteStatusChangeDetector


@pytest.fixture
@patch('src.status.device_status.DeviceStatus')
def remote_status_change_detector(DeviceStatusMock) -> RemoteStatusChangeDetector:
    device_status_mock = DeviceStatusMock()
    return RemoteStatusChangeDetector(device_status_mock)


@patch('src.status.remote_status_change_detector.time.time')
def test_pull_scheduling_action_if_required(mock_time, remote_status_change_detector):
    mock_time.return_value = 0
    remote_status_change_detector._last_scheduling_action_check = 0
    remote_status_change_detector._next_scheduling_action = None
    remote_status_change_detector._get_next_scheduling_action = Mock(return_value=None)
    remote_status_change_detector._pull_scheduling_action_if_required()
    assert remote_status_change_detector._next_scheduling_action is None
    remote_status_change_detector._last_scheduling_action_check = 0
    remote_status_change_detector._next_scheduling_action = None
    remote_status_change_detector._get_next_scheduling_action = Mock(return_value='action')
    remote_status_change_detector._pull_scheduling_action_if_required()
    assert remote_status_change_detector._next_scheduling_action == 'action'


def test_set_status(remote_status_change_detector):
    remote_status_change_detector._has_to_send_current_status = False
    remote_status_change_detector._device_status.is_turned_on = Mock(return_value=False)
    remote_status_change_detector.set_status(True)
    remote_status_change_detector._device_status.set_status.assert_called_once_with(True)


@patch('src.status.remote_status_change_detector.get')
def test_get_next_scheduling_action(mock_get, remote_status_change_detector):
    mock_get.return_value.json.return_value = {}
    remote_status_change_detector._get_next_scheduling_action()
    assert remote_status_change_detector._next_scheduling_action is None


@patch('src.status.remote_status_change_detector.get')
def test_pull_instant_action(mock_get, remote_status_change_detector):
    mock_get.return_value.json.return_value = {}
    assert remote_status_change_detector._pull_instant_action() is None


@patch('src.status.remote_status_change_detector.time.time')
def test_apply_scheduled_action_if_required(mock_time, remote_status_change_detector):
    mock_time.return_value = 0
    remote_status_change_detector._next_scheduling_action = None
    remote_status_change_detector._apply_scheduled_action_if_required()
    assert not remote_status_change_detector._next_scheduling_action


def test_update_status_sets_status_when_it_get_an_instant_action(remote_status_change_detector):
    remote_status_change_detector._pull_instant_action = lambda: DeviceAction('TURN_DEVICE_ON')
    remote_status_change_detector.set_status = MagicMock()
    remote_status_change_detector.update_status()
    remote_status_change_detector.set_status.assert_called_with(True)
