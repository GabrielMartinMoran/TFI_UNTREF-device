from src.config import REMOTE_API_URI
from src.exceptions.unauthenticated_exception import UnauthenticatedException
from src.measures.measure import Measure
from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider

if PlatformChecker.is_device():
    from urequests import post
else:
    from requests import post


class MeasuresSender:

    def send_measures(self, measures: 'List[Measure]') -> bool:
        """
        :param measures: List of measures to send
        :return: Returns True when measures could be sent to the server
        """
        try:
            print(f'Sending {len(measures)} measures to the server')
            self._send_measures(measures)
            return True
        except Exception as e:
            print(e)
            return False

    def _send_measures(self, measures: 'List[Measure]') -> None:
        device_id = StateProvider.get('device_id')
        response = post(f'{REMOTE_API_URI}/devices/add_measures/{device_id}', json=[
            measure.to_dict() for measure in measures
        ], headers={'Authorization': self._get_token()})
        # If it failed raise an exception
        response.raise_for_status()

    @classmethod
    def _get_token(cls) -> str:
        token = StateProvider.get('token')
        if token is None:
            raise UnauthenticatedException()
        return f'Bearer {token}'
