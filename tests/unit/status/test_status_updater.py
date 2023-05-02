import pytest
from unittest.mock import Mock, patch, MagicMock

from src.status.actions.device_action import DeviceAction
from src.status.status_updater import StatusUpdater


@pytest.fixture
def status_updater() -> StatusUpdater:
    return StatusUpdater()


@patch('src.status.status_updater.time.time')
def test_pull_scheduling_action_if_required(mock_time, status_updater):
    mock_time.return_value = 0
    status_updater._last_scheduling_action_check = 0
    status_updater._next_scheduling_action = None
    status_updater._get_next_scheduling_action = Mock(return_value=None)
    status_updater._pull_scheduling_action_if_required()
    assert status_updater._next_scheduling_action is None
    status_updater._last_scheduling_action_check = 0
    status_updater._next_scheduling_action = None
    status_updater._get_next_scheduling_action = Mock(return_value='action')
    status_updater._pull_scheduling_action_if_required()
    assert status_updater._next_scheduling_action == 'action'


@patch('src.status.status_updater.time.time')
def test_send_current_state_if_required(mock_time, status_updater):
    mock_time.return_value = 0
    status_updater._last_status_sent = 0
    status_updater._has_to_send_current_status = False
    status_updater._send_current_status_if_required()
    assert not status_updater._has_to_send_current_status
    status_updater._last_status_sent = 0
    status_updater._has_to_send_current_status = True
    status_updater._send_current_status = Mock()
    status_updater._send_current_status_if_required()
    assert not status_updater._has_to_send_current_status


def test_set_status(status_updater):
    status_updater._has_to_send_current_status = False
    status_updater.set_status(True)
    assert status_updater._turned_on
    assert status_updater._has_to_send_current_status


@patch('src.status.status_updater.get')
def test_get_next_scheduling_action(mock_get, status_updater):
    mock_get.return_value.json.return_value = {}
    status_updater._get_next_scheduling_action()
    assert status_updater._next_scheduling_action is None


@patch('src.status.status_updater.get')
def test_pull_instant_action(mock_get, status_updater):
    mock_get.return_value.json.return_value = {}
    assert status_updater._pull_instant_action() is None


@patch('src.status.status_updater.time.time')
def test_apply_scheduled_action_if_required(mock_time, status_updater):
    mock_time.return_value = 0
    status_updater._next_scheduling_action = None
    status_updater._apply_scheduled_action_if_required()
    assert not status_updater._next_scheduling_action


def test_update_status_sets_status_when_it_get_an_instant_action(status_updater):
    status_updater._pull_instant_action = lambda: DeviceAction('TURN_DEVICE_ON')
    status_updater.set_status = MagicMock()
    status_updater.update_status()
    status_updater.set_status.assert_called_with(True)
