import time

from src.config import INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION, REMOTE_API_URI
from src.http.http_client import HTTPClient
from src.status.actions.device_action import DeviceAction
from src.status.device_status import DeviceStatus
from src.status.actions.scheduling_action import SchedulingAction

from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider
from src.utils.request_status_checker import raise_if_failed

if PlatformChecker.is_device():
    from urequests import get
else:
    from requests import get


class RemoteStatusChangeDetector(HTTPClient):

    def __init__(self, device_status: DeviceStatus) -> None:
        self._device_status = device_status
        self._next_scheduling_action = None
        self._last_scheduling_action_check = 0

    def update_status(self) -> None:
        # First: Evaluate instant actions
        instant_action = self._pull_instant_action()
        if instant_action is not None:
            self.set_status(instant_action.is_turn_on())

        # Second: Pull scheduling actions
        self._pull_scheduling_action_if_required()

        # Third: apply the scheduling action if required
        self._apply_scheduled_action_if_required()

    def _pull_scheduling_action_if_required(self) -> None:
        now = time.time()
        if self._next_scheduling_action is None or now - self._last_scheduling_action_check \
                >= INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION:
            try:
                self._next_scheduling_action = self._get_next_scheduling_action()
                self._last_scheduling_action_check = now
            except Exception as e:
                print(e)

    def set_status(self, turned_on: bool) -> None:
        if self._device_status.is_turned_on() != turned_on:
            self._device_status.set_status(turned_on)
            print(f'Updated device status to {"turned on" if turned_on else "turned off"} by a remote action')

    def _get_next_scheduling_action(self) -> 'Optional[SchedulingAction]':
        device_id = StateProvider.get('device_id')
        try:
            response = get(
                url=f'{REMOTE_API_URI}/scheduler/get_next_scheduling_action/{device_id}?use_epochs=true',
                headers={'Authorization': self._get_token()}
            )
            # If it failed raise an exception
            raise_if_failed(response)
            json_data = response.json()
        except Exception as e:
            print(e)
            return None
        if len(json_data) == 0:
            return None
        return SchedulingAction.from_dict(json_data)

    def _pull_instant_action(self) -> 'Optional[DeviceAction]':
        device_id = StateProvider.get('device_id')
        try:
            response = get(
                url=f'{REMOTE_API_URI}/instantactions/action/{device_id}',
                headers={'Authorization': self._get_token()}
            )
            # If it failed raise an exception
            raise_if_failed(response)
            json_data = response.json()
        except Exception as e:
            print(e)
            return None
        action = json_data.get('action')
        if action is None:
            return None
        return DeviceAction(action)

    def _apply_scheduled_action_if_required(self):
        if self._next_scheduling_action is None:
            return
        now = time.time()
        if now >= self._next_scheduling_action.moment and not self._next_scheduling_action.was_evaluated:
            self._next_scheduling_action.was_evaluated = True
            self.set_status(self._next_scheduling_action.is_turn_on())
