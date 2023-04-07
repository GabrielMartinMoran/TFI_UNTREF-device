from src.status.actions.device_action import DeviceAction


class SchedulingAction(DeviceAction):

    def __init__(self, action: str, moment: int) -> None:
        super().__init__(action)
        self._moment = moment
        self._was_evaluated = False

    @property
    def moment(self) -> int:
        return self._moment

    @property
    def was_evaluated(self) -> bool:
        return self._was_evaluated

    @was_evaluated.setter
    def was_evaluated(self, was_evaluated: bool) -> None:
        self._was_evaluated = was_evaluated

    @classmethod
    def from_dict(cls, data: dict) -> 'SchedulingAction':
        return SchedulingAction(
            action=data['action'],
            moment=data['moment']
        )
