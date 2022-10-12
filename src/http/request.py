import json

from src.http import http_methods


class Request:
    _DIVIDER = '\r\n'

    def __init__(self, method: str, route: str, protocol: str, headers: str, body: dict) -> None:
        self._method = method
        self._route = route
        self._protocol = protocol
        self._headers = headers
        self._body = body

    @property
    def method(self) -> str:
        return self._method

    @property
    def route(self) -> str:
        return self._route

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def body(self) -> dict:
        return self._body

    @property
    def is_cors(self) -> bool:
        return self.method == http_methods.OPTIONS

    @property
    def is_valid_method(self) -> bool:
        return self.method in {http_methods.POST, http_methods.GET, http_methods.OPTIONS}

    @staticmethod
    def from_bytes(data: bytes) -> 'Request':
        heading, raw_body = data.decode('utf-8').split(Request._DIVIDER * 2)

        split_heading = heading.split(Request._DIVIDER)

        head = split_heading[0]
        method, route, protocol = head.split(' ')

        # Headers
        raw_headers = split_heading[1:]
        headers = {}
        for raw_header in raw_headers:
            k, v = raw_header.split(': ')
            headers[k] = v

        # Body
        try:
            body = json.loads(raw_body) if len(raw_body) > 0 else {}
        except Exception:
            raise AssertionError('Invalid body encoding')

        return Request(method, route, protocol, headers, body)
