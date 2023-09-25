from src import config
from src.components.gpio_out import GPIOOut


class StatusLed(GPIOOut):

    def __init__(self, initial_status: bool) -> None:
        super().__init__(config.STATUS_LED_PIN, initial_status)

    @classmethod
    def _on_value(cls) -> int:
        return 1

    @classmethod
    def _off_value(cls) -> int:
        return 0
