import gc
import time

from src import config
from src.platform_checker import PlatformChecker
from src.utils.math import mean

if PlatformChecker.is_device():
    from machine import RTC, Pin, ADC
else:
    from platform_mocks.machine import RTC, Pin, ADC

from src.measures.measure import Measure


# REFERENCE: https://www.circuitschools.com/measure-ac-current-by-interfacing-acs712-sensor-with-esp32/

class MeasuresTaker:
    _MAX_SIZE = 20
    _MAX_SENSOR_OUT_VOLTAGE = 3.3
    _ADC_RESOLUTION_SIZE = 4096.0
    _RMS_FACTOR = 0.707  # (1/(2^1/2))
    """
    Sensor: ACS712 30A version
    Regarding sensor sensitivity, for a 5v output, the default sensitivity is 0.066 V/A
    Reducing the voltage with a voltage divider where R1=1KΩ and R2=2KΩ, we get a reference voltage of 3.3V
    So, if we convert the sensitivity from 5v to 3.31V, we get a sensitivity value of 0.043 V/A

    Sensor: ACS712 5A version
    Regarding sensor sensitivity, for a 5v output, the default sensitivity is 0.185 V/A going from -5V to 5V
    Reducing the voltage with a voltage divider where R1=1KΩ and R2=2KΩ, we get a reference voltage of 3.3V
    We can correct SENSOR_SENSITIVITY from 0.185 V/A at 5V to -> 0.185 V/A * (R1/(R1+R2)) = 0.06167
    (Thanks to https://github.com/RobTillaart/ACS712)
    """
    _SENSOR_SENSITIVITY = 0.06167
    _RMS_VOLTAGE = config.AC_VOLTAGE * _RMS_FACTOR
    _MEASUREMENT_TIME = 1  # Seconds
    _STANDBY_VOLTAGE_MEASUREMENT_TIME = 2  # Seconds

    # Twice the speed for better sampling (Nyquist theorem)
    _TIME_TO_WAIT_BETWEEN_MEASURES = 1 / (config.AC_FREQUENCY * 2)

    def __init__(self) -> None:
        self._rtc = RTC()
        self._measures = []
        self._ac_sensor = ADC(Pin(config.AC_SENSOR_PIN))
        self._ac_sensor.width(ADC.WIDTH_12BIT)
        self._ac_sensor.atten(ADC.ATTN_0DB)
        time.sleep(0.2)  # Wait to let the sensor start
        self._calculate_measurement_error()

    def _calculate_measurement_error(self) -> None:
        # It assumes the connected device is turned off
        t_end = time.time() + self._STANDBY_VOLTAGE_MEASUREMENT_TIME

        measures = []

        while time.time() < t_end:
            measures.append(self._ac_sensor.read())
            time.sleep(self._TIME_TO_WAIT_BETWEEN_MEASURES)

        self._measurement_error = (self._ADC_RESOLUTION_SIZE / 2) - mean(measures)

        print(f'MEASUREMENT ERROR ---> {self._measurement_error}')

        # To free the memory used
        del measures
        gc.collect()

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

    def _measure_vpp_current(self) -> float:
        min_value = self._ADC_RESOLUTION_SIZE
        max_value = 0

        t_end = time.time() + self._MEASUREMENT_TIME

        while time.time() < t_end:
            read_value = self._ac_sensor.read() - self._measurement_error

            if read_value > max_value:
                max_value = read_value
            if read_value < min_value:
                min_value = read_value

            time.sleep(self._TIME_TO_WAIT_BETWEEN_MEASURES)

        return ((max_value - min_value) * self._MAX_SENSOR_OUT_VOLTAGE) / self._ADC_RESOLUTION_SIZE

    def _calculate_rms_current(self, vpp_current: float) -> float:
        rms_voltage = (vpp_current / 2) * self._RMS_FACTOR
        return rms_voltage / self._SENSOR_SENSITIVITY

    def take_measure(self) -> None:
        vpp_current = self._measure_vpp_current()
        rms_current = self._calculate_rms_current(vpp_current)
        print(
            f'Current: {vpp_current} | Irms: {rms_current} | Power: {rms_current * config.AC_VOLTAGE}'
        )  # 1.2 is empirical
        measure = Measure(
            timestamp=RTC().datetime(),
            voltage=self._RMS_VOLTAGE,
            current=rms_current
        )
        self._add_measure(measure)
