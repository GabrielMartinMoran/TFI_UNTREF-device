from src import config
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from machine import Pin
else:
    from platform_mocks.machine import Pin


class StatusChangeButton:

    def __init__(self) -> None:
        self._pin = Pin(config.STATUS_CHANGE_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    def is_pressed(self) -> bool:
        return not self._pin.value()
