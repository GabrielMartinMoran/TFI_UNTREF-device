from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from machine import Pin
else:
    from platform_mocks.machine import Pin


class GPIOOut:

    def __init__(self, pin_number: int, initial_status: bool) -> None:
        self._pin = Pin(pin_number, Pin.OUT)
        self.set_status(initial_status)

    def set_status(self, status: bool) -> None:
        self._pin.value(self._on_value() if status else self._off_value())

    @classmethod
    def _on_value(cls) -> int:
        return 1

    @classmethod
    def _off_value(cls) -> int:
        return 0
