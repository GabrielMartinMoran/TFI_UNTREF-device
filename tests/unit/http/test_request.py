import json

import pytest

from src.http import http_methods
from src.http.request import Request


def test_request_properties():
    headers = {'content-type': 'application/json'}
    body = {'name': 'John Doe', 'age': 30}
    request = Request(http_methods.POST, '/users', 'HTTP/1.1', headers, body)

    assert request.method == http_methods.POST
    assert request.route == '/users'
    assert request.protocol == 'HTTP/1.1'
    assert request.headers == headers
    assert request.body == body
    assert not request.is_cors
    assert request.is_valid_method


def test_request_from_bytes():
    headers = {'content-type': 'application/json'}
    body = {'name': 'John Doe', 'age': 30}
    data = f'POST /users HTTP/1.1\r\ncontent-type: application/json\r\n\r\n{json.dumps(body)}'.encode('utf-8')
    request = Request.from_bytes(data)

    assert request.method == http_methods.POST
    assert request.route == '/users'
    assert request.protocol == 'HTTP/1.1'
    assert request.headers == headers
    assert request.body == body
    assert not request.is_cors
    assert request.is_valid_method


def test_request_from_bytes_raises_exception_when_body_is_invalid():
    data = 'POST /users HTTP/1.1\r\ncontent-type: application/json\r\n\r\nnot-a-json-body'.encode('utf-8')

    with pytest.raises(AssertionError) as exc_info:
        Request.from_bytes(data)
    assert exc_info.value.args[0] == 'Invalid body encoding'


def test_request_is_cors():
    headers = {'content-type': 'application/json'}
    request = Request(http_methods.OPTIONS, '/users', 'HTTP/1.1', headers, {})

    assert request.is_cors
    assert request.is_valid_method


def test_request_is_invalid_method():
    headers = {'content-type': 'application/json'}
    request = Request('INVALID_METHOD', '/users', 'HTTP/1.1', headers, {})

    assert not request.is_cors
    assert not request.is_valid_method
