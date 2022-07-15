import socket
from _thread import start_new_thread
from time import sleep


class HTTPServer:
    _started = False
    _connected_clients = 0

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
    def _is_request(cls, string: str):
        # TODO add more HTTP methods
        return string[:3] == 'GET'

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

    def _map_params(self, params):
        map = {}
        for x in params:
            param = x.split('=')
            map[param[0]] = param[1]
        return map

    def __dividir_url(self, url):
        data = url.replace('?', ' ')
        data = data.replace('&', ' ')
        return data.split(' ')

    """
    #En desuso debido a problema de profundidad de recursion
    def __atender_request(self, request_str):
        data = request_str[4:].split(' ')[0]
        request_data = self.__dividir_url(data)
        url = request_data[0]
        parametros = self.__mapear_parametros(request_data[1:])
        if(self.__imprimir_log):
            print("REQUEST TO:",url)
        return self.__rutear(url,parametros)
    """

    def __atender_cliente(self, conexion):
        # Agregamos el cliente como conectado
        self._connected_clients += 1
        cl_file = conexion.makefile('rwb', 0)
        data = b''
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break
            data += line

        decoded_data = data.decode('utf-8')
        response = ""
        if (self._is_request(decoded_data)):
            # __atender_request
            data = decoded_data[4:].split(' ')[0]
            request_data = self.__dividir_url(data)
            url = request_data[0]
            parametros = self._map_params(request_data[1:])
            if (self._print_log):
                print("REQUEST TO:", url)
            decoded_data = None
            # __atender_request
            response = self.__rutear(url, parametros)
        conexion.sendall(response.encode('utf-8'))
        conexion.close()
        response = None
        conexion = None
        # Quitamos este cliente
        self._connected_clients -= 1

    def _listen_clients(self):
        while self._started:
            try:
                conexion, addr = self._server.accept()
            except:
                # Posible error cuando se cierra el socket
                break
            if (self._print_log):
                print('Cliente conectado desde:', addr)
            start_new_thread(self.__atender_cliente, (conexion,))

    """
    La funcion debe permitir recibir un parametro ya que se utilizara de la manera funcion(parametros_url)
    """

    def register_route(self, path: str, function: 'Callable'):
        self._routes[path] = function

    def __generar_response(self, data, error=False):
        codigo = None
        if (not error):
            codigo = "200 OK"
        else:
            codigo = "404 Not Found"
        return "HTTP/1.1 " + codigo + "\r\nContent-Type: text/html\r\n\r\n" + data

    def __rutear(self, url, parametros):
        if (url in self._routes):
            return self.__generar_response(self._routes[url](parametros))
        else:
            return self.__generar_response("URL NO ENCONTRADA", error=True)
