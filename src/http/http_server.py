import gc
import json
import socket
from _thread import start_new_thread
from time import sleep

from src.http import http_methods
from src.http.request import Request


class HTTPServer:
    _started = False
    _connected_clients = 0
    _STATUS_CODES = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
    _READ_BUFFER_SIZE = 4046

    def __init__(self, host: str, port: int, max_clients: int = 1, print_log: bool = False) -> None:
        self._host = host
        self._port = port
        self._max_clients = max_clients
        self._print_log = print_log
        self._server = None
        self._routes = {}

    def start(self, threaded=True) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.settimeout(None)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self._host, self._port))
        self._server.listen(self._max_clients)
        self._started = True
        if self._print_log:
            print(f'HTTP server listening on on http://{self._host}:{self._port}')
        if threaded:
            start_new_thread(self._listen_clients, ())
        else:
            self._listen_clients()

    def stop(self) -> None:
        self._started = False
        # Wait until no more clients are connected
        while self._connected_clients > 0:
            sleep(0.01)
        try:
            self._server.shutdown(socket.SHUT_RDWR)
        except Exception:
            # When using UDP
            pass
        self._server.close()

    @classmethod
    def _map_url_params(cls, params: 'List[str]') -> dict:
        params_map = {}
        for x in params:
            param = x.split('=')
            params_map[param[0]] = param[1]
        return params_map

    @classmethod
    def _partition_url(cls, url: str) -> 'List[str]':
        data = url.replace('?', ' ')
        data = data.replace('&', ' ')
        return data.split(' ')

    def _attend_client(self, connection: socket.socket) -> None:
        self._connected_clients += 1

        data = b''
        while True:
            pulled = connection.recv(self._READ_BUFFER_SIZE)
            data += pulled
            if len(pulled) < self._READ_BUFFER_SIZE:
                break

        response = None
        try:
            request = Request.from_bytes(data)
        except Exception:
            response = self._make_response({}, status_code=400)
        if response is None and request.is_valid_method:
            # Solve CORS
            if request.is_cors:
                response = self._make_cors_response(request)
            else:
                partitioned_url = self._partition_url(request.route)
                url = partitioned_url[0]
                url_params = self._map_url_params(partitioned_url[1:])
                print(f'{request.method} request to:', url)
                response = self._route_request(request.method, url, url_params, request.body)
        connection.sendall(response.encode('utf-8'))
        connection.close()
        # Clean all variables and run garbage collector
        request = None
        response = None
        connection = None
        gc.collect()
        self._connected_clients -= 1

    def _listen_clients(self) -> None:
        while self._started:
            try:
                connection, addr = self._server.accept()
            except Exception:
                # An error may occur when closing the socket
                break
            start_new_thread(self._attend_client, (connection,))

    @classmethod
    def _merge_url(cls, http_method: str, path: str) -> str:
        return f'{http_method}|{path}'

    def register_route(self, http_method: str, path: str, function: 'Callable'):
        self._routes[self._merge_url(http_method, path)] = function

    def _make_response(self, response_data: 'Any', status_code: int = 200, headers: dict = None) -> str:
        serialized_data = json.dumps(response_data)
        status = f'{status_code} {self._STATUS_CODES.get(status_code, "")}'
        _headers = {**(headers if headers is not None else {}), **{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
        }}
        serialized_headers = '\r\n'.join([f'{k}: {v}' for k, v in _headers.items()])
        return f'HTTP/1.1 {status}\r\n{serialized_headers}\r\n\r\n{serialized_data}'

    def _route_request(self, http_method: str, path: str, url_params: dict, body: dict) -> str:
        route = self._merge_url(http_method, path)
        if route in self._routes:
            try:
                return self._make_response(self._routes[route](url_params, body))
            except AssertionError as e:
                return self._make_response({'message': str(e)}, status_code=400)
            except Exception:
                return self._make_response({}, status_code=500)
        else:
            return self._make_response({}, status_code=404)

    def _make_cors_response(self, request: Request) -> str:
        return self._make_response({}, headers={
            'Access-Control-Allow-Origin': request.headers['Origin'],
            'Access-Control-Allow-Methods': request.headers['Access-Control-Request-Method'],
            'Access-Control-Allow-Headers': request.headers['Access-Control-Request-Headers']
        })

    @classmethod
    def _is_cors_request(cls, method: str) -> bool:
        return method == http_methods.OPTIONS
