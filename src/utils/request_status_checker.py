from src.exceptions.http_exception import HTTPException
from src.platform_checker import PlatformChecker

if PlatformChecker.is_device():
    from urequests import Response
else:
    from requests import Response

MIN_SUCCESS_STATUS_CODE = 200
MAX_SUCCESS_STATUS_CODE = 299


def raise_if_failed(response: Response) -> None:
    if response.status_code < MIN_SUCCESS_STATUS_CODE or response.status_code > MAX_SUCCESS_STATUS_CODE:
        raise HTTPException(response.status_code, response.reason.decode('utf-8'))
