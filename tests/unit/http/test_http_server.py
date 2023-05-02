import socket

import pytest
from unittest.mock import MagicMock, Mock

from src.http.http_server import HTTPServer


@pytest.fixture(scope='module')
def http_server():
    return HTTPServer('localhost', 8080, max_clients=1, print_log=True)


def test_register_route(http_server):
    assert not http_server._routes
    http_server.register_route('GET', '/test', MagicMock())
    assert http_server._routes


def test_map_url_params(http_server):
    params = ['a=1', 'b=2', 'c=3']
    actual = http_server._map_url_params(params)
    assert actual == {'a': '1', 'b': '2', 'c': '3'}


def test_partition_url(http_server):
    url = '/test?a=1&b=2&c=3'
    actual = http_server._partition_url(url)
    assert actual == ['/test', 'a=1', 'b=2', 'c=3']


def test_merge_url(http_server):
    actual = http_server._merge_url('GET', '/test')

    assert actual == 'GET|/test'


def test_make_response(http_server):
    expected = ('HTTP/1.1 200 OK\r\n'
                'Content-Type: application/json; charset=utf-8\r\n'
                'Access-Control-Allow-Origin: *\r\n'
                '\r\n'
                '{"message": "success"}')

    actual = http_server._make_response({'message': 'success'}, status_code=200, headers={'Content-Type': 'text/html'})

    assert actual == expected


def test_route_request(http_server):
    expected = ('HTTP/1.1 200 OK\r\n'
                'Content-Type: application/json; charset=utf-8\r\n'
                'Access-Control-Allow-Origin: *\r\n'
                '\r\n'
                '{"a": "1", "b": "2", "message": "success"}')

    http_server.register_route('GET', '/test', lambda p, b: {'a': p['a'], 'b': p['b'], **b})

    url_params = {'a': '1', 'b': '2'}
    body = {'message': 'success'}
    actual = http_server._route_request('GET', '/test', url_params, body)

    assert actual == expected


def test_attend_client(http_server):
    mock_socket = Mock(spec=socket.socket)
    mock_socket.recv.side_effect = [('GET /test_url?param1=1&param2=2 HTTP/1.1\r\n'
                                     'Host: example.com;\r\n'
                                     'Content-Type: application/json;'
                                     'charset=utf-8\r\n'
                                     '\r\n'
                                     '{"a": "1", "b": "2", "message": "success"}').encode()]

    http_server._attend_client(mock_socket)

    assert mock_socket.recv.call_count == 1
    assert mock_socket.sendall.call_args[0][0] == (
        b'HTTP/1.1 404 Not Found\r\nContent-Type: application/json; charset=utf-8\r\nA'
        b'ccess-Control-Allow-Origin: *\r\n\r\n{}'
    )
