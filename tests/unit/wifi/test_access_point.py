import pytest

from platform_mocks.network import AUTH_WPA_WPA2_PSK
from src.config import AP_PASSWORD, AP_SSID
from src.wifi.access_point import AccessPoint


@pytest.fixture
def access_point() -> AccessPoint:
    return AccessPoint()


def test_start_activates_and_configures_access_point(access_point):
    access_point.start()

    assert access_point._ap_if._status
    assert access_point._ap_if._essid == AP_SSID
    assert access_point._ap_if._authmode == AUTH_WPA_WPA2_PSK
    assert access_point._ap_if._password == AP_PASSWORD


def test_stop_sets_ap_if_as_inactive(access_point):
    access_point.start()
    access_point.stop()

    assert not access_point._ap_if._status
