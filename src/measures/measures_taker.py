import gc
import math
import time
from typing import List

from src import config
from src.platform_checker import PlatformChecker
from src.status.device_status import DeviceStatus

if PlatformChecker.is_device():
    from machine import RTC, Pin, ADC
else:
    from platform_mocks.machine import RTC, Pin, ADC

from src.measures.measure import Measure


class MeasuresTaker:
    _MAX_MEASURES_BUFFER_SIZE = 20
    _MAX_SENSOR_OUT_VOLTAGE = 3.3
    _ADC_RESOLUTION_SIZE = 4096.0

    _MEASUREMENT_TIME = 1  # Seconds
    _STANDBY_VOLTAGE_MEASUREMENT_TIME = 2  # Seconds

    # At least twice the speed for better sampling (Nyquist theorem)
    _TIME_TO_WAIT_BETWEEN_MEASURES = 1 / (config.AC_LINE_FREQUENCY * config.MEASURES_PER_CYCLE)

    def __init__(self, device_status: DeviceStatus) -> None:
        self._device_status = device_status
        self._rtc = RTC()
        self._measures = []
        self._ac_sensor = ADC(Pin(config.AC_SENSOR_PIN))
        self._ac_sensor.width(ADC.WIDTH_12BIT)
        self._ac_sensor.atten(ADC.ATTN_0DB)
        self._calculate_current_error()

    def _measure_current(self, measurement_time: float, use_calibration_factor: bool = True) -> float:
        t_end = time.time() + measurement_time

        measures = []

        while time.time() < t_end:
            measure = self._ac_sensor.read()
            if use_calibration_factor:
                measure -= config.MEASURES_CALIBRATION_OFFSET
            measures.append(measure)
            time.sleep(self._TIME_TO_WAIT_BETWEEN_MEASURES)

        current = self._calculate_rms_current(measures)

        # To free the memory used
        del measures
        gc.collect()

        return current

    def _calculate_current_error(self) -> None:
        prev_status = self._device_status.is_turned_on()
        # Force turn off
        self._device_status.set_status(False)
        # Wait to ensure the status change
        time.sleep(0.5)
        # It assumes the connected device is turned off
        self._current_error = self._measure_current(self._STANDBY_VOLTAGE_MEASUREMENT_TIME, False)
        print(f'IDLE CURRENT MEASUREMENT ERROR: {self._current_error} A')
        # Recover the previous status
        self._device_status.set_status(prev_status)

    def _add_measure(self, measure: Measure) -> None:
        print(f'Measure added: {measure}')
        self._measures.append(measure)
        if len(self._measures) > self._MAX_MEASURES_BUFFER_SIZE:
            self._measures = self._measures[1:]

    def clear_measures(self, measures_to_clear: List[Measure]) -> None:
        for measure in measures_to_clear:
            if measure in self._measures:
                self._measures.remove(measure)

    @property
    def measures(self) -> List[Measure]:
        # Copy the list so in case of adding new measures, the List returned by this function won't be updated
        return [x for x in self._measures]

    def take_measure(self) -> None:
        # We take the absolute value of the rms current
        measured_current = self._measure_current(self._MEASUREMENT_TIME)
        rms_current = abs(measured_current - self._current_error)
        print(f'Measured Current: {measured_current} A | ' +
              f'RMS Current: {rms_current} A | ' +
              f'RMS Power: {rms_current * config.AC_LINE_RMS_VOLTAGE} W')
        measure = Measure(
            timestamp=RTC().datetime(),
            voltage=config.AC_LINE_RMS_VOLTAGE,
            current=rms_current
        )
        self._add_measure(measure)

    @classmethod
    def _calculate_rms(cls, measures: List[int]) -> float:
        return math.sqrt(sum([x ** 2 for x in measures]) / len(measures))

    def _calculate_rms_current(self, measures: List[int]) -> float:
        m_rms = self._calculate_rms(measures)
        print(f'Muestra RMS: {m_rms}')
        v_rms = (m_rms * self._MAX_SENSOR_OUT_VOLTAGE) / self._ADC_RESOLUTION_SIZE
        return (v_rms - (self._MAX_SENSOR_OUT_VOLTAGE / 2)) / config.CURRENT_SENSOR_SENSITIVITY
