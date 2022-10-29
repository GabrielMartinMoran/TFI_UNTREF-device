import time

from src.config import INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION, REMOTE_API_URI
from src.http.http_client import HTTPClient
from src.status.scheduling_action import SchedulingAction

from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider

if PlatformChecker.is_device():
    from urequests import get
else:
    from requests import get


class StatusUpdater(HTTPClient):

    def __init__(self) -> None:
        self._turned_on = False
        self._next_scheduling_action = None
        self._last_check = 0

    def update_status(self) -> None:
        self._pull_scheduling_action_if_required()
        if self._next_scheduling_action is None:
            return
        now = time.time()
        if now >= self._next_scheduling_action.moment and not self._next_scheduling_action.was_evaluated:
            self._next_scheduling_action.was_evaluated = True
            self.set_status(self._next_scheduling_action.is_turn_on())

    def _pull_scheduling_action_if_required(self) -> None:
        now = time.time()
        if self._next_scheduling_action is None or now - self._last_check >= INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION:
            try:
                self._next_scheduling_action = self._get_next_scheduling_action()
                self._last_check = now
            except Exception as e:
                print(e)

    def set_status(self, turned_on: bool) -> None:
        if turned_on == self._turned_on:
            return
        self._turned_on = turned_on
        print(f'DEVICE TURNED {"ON" if turned_on else "OFF"}')

    def _get_next_scheduling_action(self) -> 'Optional[SchedulingAction]':
        device_id = StateProvider.get('device_id')
        response = get(f'{REMOTE_API_URI}/scheduler/get_next_scheduling_action/{device_id}?use_epochs=true',
                       headers={'Authorization': self._get_token()})
        # If it failed raise an exception
        response.raise_for_status()
        json_data = response.json()
        if len(json_data) == 0:
            return None
        return SchedulingAction.from_dict(json_data)
