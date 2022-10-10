import random
import time

from src.config import AC_SENSOR_PIN
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from machine import RTC, Pin, ADC
else:
    from platform_mocks.machine import RTC, Pin, ADC

from src.measures.measure import Measure


class MeasuresTaker:
    _MAX_SIZE = 10
    _STANDBY_VOLTAGE_CALCULATION_TIME = 2  # Seconds
    _REF_VOLTAGE = 220.0
    _RMS_FACTOR = 0.707  # (1/(2^1/2))
    _SENSOR_SENSITIVITY = 0.066  # V / A of the sensor (because of ACS712 30A version)
    _RMS_VOLTAGE = _REF_VOLTAGE * _RMS_FACTOR
    _SENSOR_PIN = 34
    _CURRENT_MEASUREMENT_TIME = 1  # Seconds

    def __init__(self) -> None:
        self._rtc = RTC()
        self._measures = []
        self._ac_sensor = ADC(Pin(self._SENSOR_PIN))
        self._ac_sensor.width(ADC.WIDTH_12BIT)
        self._ac_sensor.atten(ADC.ATTN_11DB)
        self._calculate_standby_voltage()

    def _calculate_standby_voltage(self) -> None:
        # It assumes the connected device is turned off
        self._standby_voltage = 0
        t_end = time.time() + self._STANDBY_VOLTAGE_CALCULATION_TIME
        while time.time() < t_end:
            voltage = self._get_sensor_voltage()
            if voltage > self._standby_voltage:
                self._standby_voltage = voltage

    def _get_sensor_voltage(self) -> float:
        # Convert uV to V
        return (self._ac_sensor.read_uv() / 1000.0) / 1000.0

    def _add_measure(self, measure: Measure) -> None:
        print(f'Measure added: {measure}')
        self._measures.append(measure)
        if len(self._measures) > self._MAX_SIZE:
            self._measures = self._measures[1:]

    def clear_measures(self, measures_to_clear: 'List[Measure]') -> None:
        for measure in measures_to_clear:
            if measure in self._measures:
                self._measures.remove(measure)

    @property
    def measures(self) -> 'List[Measure]':
        # Copy the list so in case of adding new measures, the List returned by this function won't be updated
        return [x for x in self._measures]

    def _measure_current(self) -> float:
        current = 0
        min_current = 0
        max_current = 0

        t_end = time.time() + self._CURRENT_MEASUREMENT_TIME

        while time.time() < t_end:
            sensor_voltage = self._get_sensor_voltage()
            sensor_voltage -= self._standby_voltage  # 0A en sensor en 0 corresponde a 2.5V de salida -> El 2.35 se obtiene al medir la salida del sensor a 0A (valor de referencia 2.5V)
            if sensor_voltage < 0:
                sensor_voltage = 0
            # current = 0.9 * current + 0.1 * (sensor_voltage / sensitivity)
            current = round(sensor_voltage / self._SENSOR_SENSITIVITY, 3)
            if current < min_current:
                min_current = current
            if current > max_current:
                max_current = current
        return (max_current - min_current) / 2.0

    def take_measure(self) -> None:
        current = self._measure_current()
        rms_current = current * self._RMS_FACTOR
        print(f'Current: {current} | Irms: {rms_current} | Power: {rms_current * self._RMS_VOLTAGE}')
        measure = Measure(
            timestamp=RTC().datetime(),
            voltage=self._RMS_VOLTAGE,
            current=rms_current
        )
        self._add_measure(measure)
