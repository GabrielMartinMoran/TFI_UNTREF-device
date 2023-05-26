class DeviceAction:
    TURN_ON_STATUS = 'TURN_DEVICE_ON'
    TURN_OFF_STATUS = 'TURN_DEVICE_OFF'

    def __init__(self, action: str) -> None:
        self._action = action

    def is_turn_on(self) -> bool:
        return self._action == self.TURN_ON_STATUS

    @classmethod
    def build_turn_on(cls) -> 'DeviceAction':
        return DeviceAction(DeviceAction.TURN_ON_STATUS)

    @classmethod
    def build_turn_off(cls) -> 'DeviceAction':
        return DeviceAction(DeviceAction.TURN_OFF_STATUS)
