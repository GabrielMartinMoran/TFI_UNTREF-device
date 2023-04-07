class DeviceAction:
    TURN_ON_STATUS = 'TURN_DEVICE_ON'

    def __init__(self, action: str) -> None:
        self._action = action

    def is_turn_on(self) -> bool:
        return self._action == self.TURN_ON_STATUS
