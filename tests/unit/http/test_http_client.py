import pytest
from src.http.http_client import HTTPClient, UnauthenticatedException
from src.state.state_provider import StateProvider


def test_get_token_raises_exception_when_token_does_not_exist():
    with pytest.raises(UnauthenticatedException):
        HTTPClient._get_token()


def test_get_token_returns_bearer_token_when_token_exists():
    StateProvider.put('token', '12345')

    actual = HTTPClient._get_token()

    assert actual == 'Bearer 12345'
