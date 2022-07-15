class Measure:
    _ROUND_DECIMALS = 2

    def __init__(self, timestamp: tuple, voltage: float, current: float) -> None:
        self._timestamp = timestamp
        self._voltage = voltage
        self._current = current

    @property
    def timestamp(self) -> str:
        year, month, day, weekday, hours, minutes, seconds, microsecond = self._timestamp
        return f'{year}-{month:02}-{day:02}T{hours:02}:{minutes:02}:{seconds:02}.{microsecond}'

    @property
    def voltage(self) -> float:
        return round(self._voltage, self._ROUND_DECIMALS)

    @property
    def current(self) -> float:
        return round(self._current, self._ROUND_DECIMALS)

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'voltage': self.voltage,
            'current': self.current
        }

    def __repr__(self) -> str:
        return f'{self.timestamp} {self.voltage}V {self.current}A'
