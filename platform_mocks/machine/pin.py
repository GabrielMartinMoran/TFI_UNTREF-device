class Pin:
    IN = 'IN'
    OUT = 'OUT'

    def __init__(self, number: int, mode: str = IN) -> None:
        self._number = number
        self._mode = mode
        self._value = 0

    def value(self, value: int) -> None:
        self._value = value
        print(f'📟 Pin {self._number} in {self._mode} mode set to {self._value}')
