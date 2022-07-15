import os
import json


class StateProvider:
    _SAVED_STATE_PATH = 'state.json'
    _state: dict = None

    @staticmethod
    def get(key: str) -> 'Optional[Any]':
        if not StateProvider._config_loaded():
            StateProvider._load()
        return StateProvider._state.get(key)

    @staticmethod
    def put(key: str, value: 'Any') -> None:
        StateProvider._state[key] = value
        StateProvider._save()

    @staticmethod
    def _save() -> None:
        with open(StateProvider._SAVED_STATE_PATH, 'w') as f:
            f.write(json.dumps(StateProvider._state))

    @staticmethod
    def _load() -> None:
        if StateProvider._config_file_exists():
            with open(StateProvider._SAVED_STATE_PATH, 'r') as f:
                StateProvider._state = json.loads(f.read())
        else:
            StateProvider._state = {}

    @staticmethod
    def _config_file_exists() -> bool:
        # Micropython doesn't implement os.path
        return StateProvider._SAVED_STATE_PATH in os.listdir()

    @staticmethod
    def _config_loaded() -> bool:
        return StateProvider._state is not None
