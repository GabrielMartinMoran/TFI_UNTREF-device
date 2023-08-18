from src.config import REMOTE_API_URI, MAX_MEASURES_BATCH_SIZE
from src.exceptions.unauthenticated_exception import UnauthenticatedException
from src.http.http_client import HTTPClient
from src.measures.measure import Measure
from src.measures.measures_taker import MeasuresTaker
from src.platform_checker import PlatformChecker
from src.state.state_provider import StateProvider
from src.utils.request_status_checker import raise_if_failed

if PlatformChecker.is_device():
    from urequests import post
else:
    from requests import post


class MeasuresSender(HTTPClient):

    def __init__(self, measures_taker: MeasuresTaker) -> None:
        self._measures_taker = measures_taker

    def _send_measures(self, measures: 'List[Measure]') -> bool:
        """
        :param measures: List of measures to send
        :return: Returns True when measures could be sent to the server
        """
        device_id = StateProvider.get('device_id')
        try:
            response = post(f'{REMOTE_API_URI}/devices/add_measures/{device_id}', json=[
                measure.to_dict() for measure in measures
            ], headers={'Authorization': self._get_token()})
            # If it failed raise an exception
            raise_if_failed(response)
            return True
        except Exception as e:
            print(e)
            return False

    def pull_and_send(self, device_turned_on: bool) -> None:
        measures = self._measures_taker.measures
        # If the amount of measures reached the batch size or
        #   if there are pending measures to be sent and the device is turned off
        if len(measures) >= MAX_MEASURES_BATCH_SIZE or (len(measures) > 0 and not device_turned_on):
            try:
                print(f'Sending {len(measures)} measures to the server')
                could_send = self._send_measures(measures)
                if could_send:
                    self._measures_taker.clear_measures(measures)
            except UnauthenticatedException:
                print('ERROR: Unauthenticated')
