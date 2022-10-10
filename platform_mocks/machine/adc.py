import math
import random
import time

from platform_mocks.machine import Pin


class ADC:
    WIDTH_12BIT = 12
    ATTN_11DB = 11

    def __init__(self, pin: Pin) -> None:
        self._pin = pin
        self._width = 0
        self._atten = 0
        self._start_time = time.time()

    def width(self, width: int) -> None:
        self._width = width

    def atten(self, atten: int) -> None:
        self._atten = atten

    def read_uv(self) -> int:
        # To simulate a current that varies across time
        time_diff = time.time() - self._start_time
        return time_diff * 1000 * math.sin(time_diff) + 1000 * 1000
