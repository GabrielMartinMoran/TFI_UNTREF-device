import time

from src.components.relay import Relay
from src.config import INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION, REMOTE_API_URI, INTERVAL_TO_SEND_CURRENT_STATE
from src.http.http_client import HTTPClient
from src.status.actions.device_action import DeviceAction
from src.status.actions.scheduling_action import SchedulingAction

from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider
from src.utils.request_status_checker import raise_if_failed

if PlatformChecker.is_device():
    from urequests import get, post
else:
    from requests import get, post


class StatusUpdater(HTTPClient):

    def __init__(self) -> None:
        self._turned_on = StateProvider.get('turned_on', False)
        self._next_scheduling_action = None
        self._last_scheduling_action_check = 0
        self._last_status_sent = 0
        self._has_to_send_current_status = False
        self._manual_action = None
        self._relay = Relay(self._turned_on)

    def update_status(self) -> None:
        # First: Evaluate instant actions
        instant_action = self._pull_instant_action()
        if instant_action is not None:
            self.set_status(instant_action.is_turn_on())

        # Second: Pull scheduling actions
        self._pull_scheduling_action_if_required()

        # Third: apply the scheduling action if required
        self._apply_scheduled_action_if_required()

        # Fourth: Evaluate manual actions
        if self._manual_action is not None:
            self.set_status(self._manual_action.is_turn_on())

        # Last: Send current status
        self._send_current_status_if_required()

    def schedule_manual_action(self) -> None:
        if self._turned_on:
            self._manual_action = DeviceAction.build_turn_off()
            print('Scheduled manual action to turn device off')
        else:
            self._manual_action = DeviceAction.build_turn_on()
            print('Scheduled manual action to turn device on')

    def _pull_scheduling_action_if_required(self) -> None:
        now = time.time()
        if self._next_scheduling_action is None or now - self._last_scheduling_action_check \
                >= INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION:
            try:
                self._next_scheduling_action = self._get_next_scheduling_action()
                self._last_scheduling_action_check = now
            except Exception as e:
                print(e)

    def _send_current_status_if_required(self) -> None:
        now = time.time()
        if self._has_to_send_current_status or (now - self._last_status_sent >= INTERVAL_TO_SEND_CURRENT_STATE):
            self._has_to_send_current_status = False
            try:
                self._send_current_status()
                self._last_status_sent = now
            except Exception as e:
                print(e)

    def set_status(self, turned_on: bool) -> None:
        if turned_on == self._turned_on:
            return
        self._turned_on = turned_on
        self._relay.set_status(self._turned_on)
        StateProvider.set('turned_on', self._turned_on)
        self._has_to_send_current_status = True
        print(f'DEVICE TURNED {"ON" if turned_on else "OFF"}')

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

    def _send_current_status(self) -> None:
        device_id = StateProvider.get('device_id')
        try:
            response = post(
                url=f'{REMOTE_API_URI}/devices/update_state/{device_id}',
                json={'turned_on': self._turned_on},
                headers={'Authorization': self._get_token()}
            )
            # If it failed raise an exception
            raise_if_failed(response)
        except Exception as e:
            print(e)

    def is_turned_on(self) -> bool:
        return self._turned_on

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
