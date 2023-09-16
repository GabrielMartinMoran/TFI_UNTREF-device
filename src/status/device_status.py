from src.components.relay import Relay
from src.components.status_led import StatusLed
from src.state.state_provider import StateProvider
from _thread import allocate_lock

from src.status.status_sender import StatusSender


class DeviceStatus:

    def __init__(self, status_sender: StatusSender, status_led: StatusLed, relay: Relay) -> None:
        self._status_sender = status_sender
        self._status_led = status_led
        self._relay = relay
        self._concurrent_lock = allocate_lock()
        self._turned_on = StateProvider.get('turned_on', False)
        self._status_led.set_status(self._turned_on)
        self._relay.set_status(self._turned_on)

    def is_turned_on(self) -> bool:
        with self._concurrent_lock:
            return self._turned_on

    def set_status(self, turned_on: bool) -> None:
        with self._concurrent_lock:
            self._turned_on = turned_on
            self._status_led.set_status(self._turned_on)
            self._relay.set_status(self._turned_on)
            StateProvider.set('turned_on', self._turned_on)
        # We do the request outside the lock for preventing it to hang out due to network errors
        self._status_sender.send_current_status_if_required(turned_on, force_send=True)

    def send_current_status_if_required(self) -> None:
        self._status_sender.send_current_status_if_required(self._turned_on)
