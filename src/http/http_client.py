from src.exceptions.unauthenticated_exception import UnauthenticatedException
from src.state.state_provider import StateProvider


class HTTPClient:

    @classmethod
    def _get_token(cls) -> str:
        token = StateProvider.get('token')
        if token is None:
            raise UnauthenticatedException()
        return f'Bearer {token}'
