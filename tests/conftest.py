import pytest

from src.state.state_provider import StateProvider


@pytest.fixture(scope='session', autouse=True)
def configure_tests_env(*args, **kwargs):
    # Disable StateProvider persistence for neither overriding local files nor loading them
    StateProvider.use_persistence(False)
    print('RESET')


@pytest.fixture(scope='function', autouse=True)
def on_each_test(*args, **kwargs):
    # Reset state provider's state
    StateProvider._state = {}
