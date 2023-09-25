from unittest.mock import MagicMock

import pytest

from src.measures.measure import Measure
from src.measures.measures_taker import MeasuresTaker

from platform_mocks.machine import RTC


@pytest.fixture
def measures_taker() -> MeasuresTaker:
    MeasuresTaker._MEASUREMENT_TIME = 0.01
    MeasuresTaker._STANDBY_VOLTAGE_MEASUREMENT_TIME = 0.01
    device_status = MagicMock()
    return MeasuresTaker(device_status)


def test_measures_taker_adds_new_measure(measures_taker):
    measure = Measure(RTC().datetime(), 123, 456)
    measures_taker._add_measure(measure)
    assert len(measures_taker.measures) == 1
    assert measures_taker.measures[0] == measure


def test_measures_taker_adds_multiple_new_measures(measures_taker):
    measure1 = Measure(RTC().datetime(), 123, 456)
    measure2 = Measure(RTC().datetime(), 789, 101112)
    measures_taker._add_measure(measure1)
    measures_taker._add_measure(measure2)
    assert len(measures_taker.measures) == 2
    assert measures_taker.measures[0] == measure1
    assert measures_taker.measures[1] == measure2


def test_measures_taker_clears_measures(measures_taker):
    measure = Measure(RTC().datetime(), 123, 456)
    measures_taker._add_measure(measure)
    assert len(measures_taker.measures) == 1
    measures_taker.clear_measures([measure])
    assert len(measures_taker.measures) == 0


def test_measures_taker_clears_multiple_measures(measures_taker):
    measure1 = Measure(RTC().datetime(), 123, 456)
    measure2 = Measure(RTC().datetime(), 789, 101112)
    measures_taker._add_measure(measure1)
    measures_taker._add_measure(measure2)
    assert len(measures_taker.measures) == 2
    measures_taker.clear_measures([measure1, measure2])
    assert len(measures_taker.measures) == 0


def test_measures_taker_clears_all_measures(measures_taker):
    measure1 = Measure(RTC().datetime(), 123, 456)
    measure2 = Measure(RTC().datetime(), 789, 101112)
    measures_taker._add_measure(measure1)
    measures_taker._add_measure(measure2)
    assert len(measures_taker.measures) == 2
    measures_taker.clear_measures(measures_taker.measures)
    assert len(measures_taker.measures) == 0
