class HTTPException(Exception):

    def __init__(self, status_code: int, reason: str) -> None:
        super().__init__()
        self._status_code = status_code
        self._reason = reason

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def reason(self) -> int:
        return self._reason

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} ({self.status_code} error): {self.reason}'

    def __str__(self) -> str:
        return self.__repr__()
