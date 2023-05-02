from typing import Optional

import pytest
import requests
from time import sleep

from src.http.http_server import HTTPServer

http_server: Optional[HTTPServer] = None


@pytest.fixture(scope='session', autouse=True)
def run_http_server() -> HTTPServer:
    global http_server
    http_server = HTTPServer('localhost', 8080, max_clients=2, print_log=True)
    # Start http_server
    http_server.start(threaded=True)
    sleep(1)

    yield

    # Stop http_server
    http_server.stop()


def test_invalid_get_route():
    response = requests.get(f'http://{http_server.host}:{http_server.port}/invalid_route')
    assert response.status_code == 404


def test_valid_get_route():
    http_server.register_route('GET', '/test', lambda *args: {'message': 'Test response'})

    response = requests.get(f'http://{http_server.host}:{http_server.port}/test')

    assert response.status_code == 200
    assert response.json() == {'message': 'Test response'}


def test_invalid_post_route():
    response = requests.post(f'http://{http_server.host}:{http_server.port}/invalid_route')
    assert response.status_code == 404


def test_valid_post_route():
    def test_route(params, body):
        assert body == {'message': 'Test request'}
        return {'message': 'Test response'}

    http_server.register_route('POST', '/test', test_route)

    response = requests.post(f'http://{http_server.host}:{http_server.port}/test', json={'message': 'Test request'})
    assert response.status_code == 200
    assert response.json() == {'message': 'Test response'}


def test_cors_request():
    response = requests.options(f'http://{http_server.host}:{http_server.port}/test', headers={
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Requested-With"
    })
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert response.headers["Access-Control-Allow-Methods"] == "GET"
    assert response.headers["Access-Control-Allow-Headers"] == "X-Requested-With"
