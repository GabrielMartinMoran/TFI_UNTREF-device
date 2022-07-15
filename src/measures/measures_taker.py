import random

from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from machine import RTC
else:
    from platform_mocks.machine import RTC

from src.measures.measure import Measure


class MeasuresTaker:
    _MAX_SIZE = 10

    def __init__(self) -> None:
        self._rtc = RTC()
        self._measures = []

    def _add_measure(self, measure: Measure) -> None:
        print(f'Measure added: {measure}')
        self._measures.append(measure)
        if len(self._measures) > self._MAX_SIZE:
            self._measures = self._measures[1:]

    def clean_measures(self) -> None:
        self._measures = []

    @property
    def measures(self) -> 'List[Measure]':
        return self._measures

    def take_measure(self) -> None:
        ref_voltage = 220
        voltage_variation = ref_voltage * 0.1
        ref_current = 1
        current_variation = ref_current * 0.2
        measure = Measure(
            timestamp=RTC().datetime(),
            voltage=ref_voltage + random.uniform(-voltage_variation, voltage_variation),
            current=ref_current + random.uniform(-current_variation, current_variation)
        )
        self._add_measure(measure)
