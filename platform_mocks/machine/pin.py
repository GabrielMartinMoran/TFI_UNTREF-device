from typing import Optional

try:
    from pynput.keyboard import Listener
except ImportError:
    # If there is an import error, import a mock instead (this only happens in the CI pipeline)
    from unittest.mock import MagicMock

    Listener = MagicMock()

from _thread import start_new_thread

from src import config


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 0
    PULL_DOWN = 1

    def __init__(self, number: int, mode: str = IN, pull: int = -1) -> None:
        self._number = number
        self._mode = mode
        self._value = 0
        self._pull = pull
        if self._mode == Pin.IN:
            start_new_thread(self._register_key_listener, ())

    def value(self, value: Optional[int] = None) -> Optional[int]:
        if value is None:
            return self._value
        self._value = value
        print(f'📟 Pin {self._number} in {"IN" if self._mode == Pin.IN else "OUT"} mode set to {self._value}')

    def _register_key_listener(self) -> None:
        def key_press(key) -> None:
            if self._number == config.STATUS_CHANGE_BUTTON_PIN and getattr(key, 'char', None) == 's':
                self._value = 0 if self._pull == Pin.PULL_UP else 1

        def key_release(key) -> None:
            if self._number == config.STATUS_CHANGE_BUTTON_PIN and getattr(key, 'char', None) == 's':
                self._value = 1 if self._pull == Pin.PULL_UP else 0

        with Listener(on_press=key_press, on_release=key_release) as listener:
            listener.join()
