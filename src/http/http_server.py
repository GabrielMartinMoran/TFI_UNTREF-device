import gc
import json
import socket
from _thread import start_new_thread
from time import sleep

from src.http import http_methods


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

    def __init__(self, host: str, port: int, max_clients: int = 1, print_log: bool = False):
        self._configure(host, port, max_clients, print_log)
        self._server = None
        self._routes = {}

    def _configure(self, host: str, port: int, max_clients: int, print_log: bool):
        self._host = host
        self._port = port
        self._max_clients = max_clients
        self._print_log = print_log

    def start(self, threaded=True):
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

    @classmethod
    def _is_request(cls, head: str) -> bool:
        for method in [http_methods.GET, http_methods.POST]:
            if head.startswith(f'{method} '):
                return True
        return False

    def stop(self):
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

        head, body = data.decode('utf-8').split('\r\n\r\n')
        head = head.split('\r\n')[0]
        response = None
        try:
            body = json.loads(body) if len(body) > 0 else {}
        except Exception:
            response = self._make_response({}, status_code=400)
        if response is None and self._is_request(head):
            method, route, protocol = head.split(' ')
            partitioned_url = self._partition_url(route)
            url = partitioned_url[0]
            url_params = self._map_url_params(partitioned_url[1:])
            print(f'{method} request to:', url)
            response = self._route_request(method, url, url_params, body)
        connection.sendall(response.encode('utf-8'))
        connection.close()
        # Clean all variables and run garbage collector
        head = None
        body = None
        response = None
        connection = None
        gc.collect()
        self._connected_clients -= 1

    def _listen_clients(self):
        while self._started:
            try:
                conexion, addr = self._server.accept()
            except Exception:
                # An error may occur when closing the socket
                break
            start_new_thread(self._attend_client, (conexion,))

    @classmethod
    def _merge_url(cls, http_method: str, path: str) -> str:
        return f'{http_method}|{path}'

    def register_route(self, http_method: str, path: str, function: 'Callable'):
        self._routes[self._merge_url(http_method, path)] = function

    def _make_response(self, response_data: 'Any', status_code: int = 200) -> str:
        serialized_data = json.dumps(response_data)
        status = f'{status_code} {self._STATUS_CODES.get(status_code, "")}'
        content_type = 'application/json; charset=utf-8'
        return f'HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\n\r\n{serialized_data}'

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
