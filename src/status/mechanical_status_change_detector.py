import time

from src.components.status_change_button import StatusChangeButton
from src.status.device_status import DeviceStatus


class MechanicalStatusChangeDetector:

    def __init__(self, device_status: DeviceStatus) -> None:
        self._btn = StatusChangeButton()
        self._device_status = device_status

    def start_detection(self) -> None:
        while True:
            if not self._btn.is_pressed():
                time.sleep(0.01)
                continue
            self._on_button_press()

    def _on_button_press(self) -> None:
        while self._btn.is_pressed():
            # To wait until the button is released
            time.sleep(0.1)
        is_turned_on = self._device_status.is_turned_on()
        self._device_status.set_status(not is_turned_on)
        print(f'Updated device status to {"turned off" if is_turned_on else "turned on"} by a mechanical action')
