import time

from src.config import INTERVAL_TO_SEND_CURRENT_STATUS, REMOTE_API_URI
from src.http.http_client import HTTPClient
from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider
from src.utils.request_status_checker import raise_if_failed

if PlatformChecker.is_device():
    from urequests import post
else:
    from requests import post


class StatusSender(HTTPClient):
    def __init__(self) -> None:
        self._last_status_sent = 0

    def send_current_status_if_required(self, turned_on: bool, force_send: bool = False) -> None:
        now = time.time()
        if force_send or (now - self._last_status_sent >= INTERVAL_TO_SEND_CURRENT_STATUS):
            try:
                self._send_current_status(turned_on)
                self._last_status_sent = now
            except Exception as e:
                print(e)

    def _send_current_status(self, turned_on: bool) -> None:
        device_id = StateProvider.get('device_id')
        try:
            response = post(
                url=f'{REMOTE_API_URI}/devices/update_state/{device_id}',
                json={'turned_on': turned_on},
                headers={'Authorization': self._get_token()}
            )
            # If it failed raise an exception
            raise_if_failed(response)
        except Exception as e:
            print(e)
