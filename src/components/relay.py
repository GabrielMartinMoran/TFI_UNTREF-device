from src import config
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from machine import Pin
else:
    from platform_mocks.machine import Pin


class Relay:
    _ON = 0
    _OFF = 1

    def __init__(self, initial_status: bool) -> None:
        self._pin = Pin(config.RELAY_PIN, Pin.OUT)
        self.set_status(initial_status)

    def set_status(self, status: bool) -> None:
        self._pin.value(self._ON if status else self._OFF)
