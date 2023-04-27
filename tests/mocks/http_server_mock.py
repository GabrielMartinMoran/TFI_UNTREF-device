from src.http.http_server import HTTPServer


class HTTPServerMock(HTTPServer):

    def __init__(self, host: str, port: int, max_clients: int = 1, print_log: bool = False) -> None:
        super().__init__(host, port, max_clients, print_log)
        self.running = False

    def start(self, threaded=True) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False
