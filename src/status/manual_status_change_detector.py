import time

from src.components.status_change_button import StatusChangeButton
from src.status.status_updater import StatusUpdater


class ManualStatusChangeDetector:

    def __init__(self, status_updater: StatusUpdater) -> None:
        self._btn = StatusChangeButton()
        self._status_updater = status_updater

    def start_detection(self) -> None:
        while True:
            if not self._btn.is_pressed():
                time.sleep(0.01)
                continue
            self._on_button_press()

    def _on_button_press(self) -> None:
        while self._btn.is_pressed():
            time.sleep(0.1)
        self._status_updater.schedule_manual_action()
