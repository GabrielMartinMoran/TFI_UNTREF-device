import pytest
from unittest.mock import patch, MagicMock

from src.config import MAX_MEASURES_BATCH_SIZE
from src.exceptions.unauthenticated_exception import UnauthenticatedException
from src.measures.measures_sender import MeasuresSender


@pytest.fixture
def measures_sender():
    measures_taker = MagicMock()
    return MeasuresSender(measures_taker)


@pytest.fixture
def mock_send_measures():
    with patch.object(MeasuresSender, '_send_measures') as mock_send_measures:
        yield mock_send_measures


def test_send_measures_raises_exception_on_unauthenticated(measures_sender, mock_send_measures):
    mock_send_measures.side_effect = UnauthenticatedException()
    with pytest.raises(UnauthenticatedException):
        measures_sender._send_measures([])


def test_pull_and_send_no_sending_when_there_are_no_measures_to_send(measures_sender, mock_send_measures):
    measures_sender._measures_taker.measures = []
    measures_sender.pull_and_send(True)
    measures_sender._send_measures.assert_not_called()


def test_pull_and_send_sending_pending_measures_with_device_on(measures_sender, mock_send_measures):
    measures = ['measure' for _ in range(MAX_MEASURES_BATCH_SIZE)]
    measures_sender._measures_taker.measures = measures
    measures_sender.pull_and_send(True)
    measures_sender._send_measures.assert_called()
    mock_send_measures.assert_called_once_with(measures)
    measures_sender._measures_taker.clear_measures.assert_called()


def test_pull_and_send_sending_pending_measures_with_device_off(measures_sender, mock_send_measures):
    measures = ['measure']
    measures_sender._measures_taker.measures = measures
    measures_sender.pull_and_send(False)
    measures_sender._send_measures.assert_called()
    mock_send_measures.assert_called_once_with(measures)
