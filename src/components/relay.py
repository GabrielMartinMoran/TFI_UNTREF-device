from src import config
from src.components.gpio_out import GPIOOut


class Relay(GPIOOut):

    def __init__(self, initial_status: bool) -> None:
        super().__init__(config.RELAY_PIN, initial_status)
