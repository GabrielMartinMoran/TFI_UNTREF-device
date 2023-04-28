from unittest.mock import patch, MagicMock

from src.main import main


@patch('src.main.Orchestrator')
@patch('src.main.StatusUpdater')
@patch('src.main.MeasuresSender')
@patch('src.main.MeasuresTaker')
@patch('src.main.WiFiClient')
@patch('src.main.AccessPoint')
def test_main(
        mock_ap_cls,
        mock_wifi_client_cls,
        mock_measures_taker_cls,
        mock_measures_sender_cls,
        mock_status_updater_cls,
        mock_orchestrator_cls,
):
    # Instantiate the mocks
    mock_ap = MagicMock()
    mock_ap_cls.return_value = mock_ap
    mock_wifi_client = MagicMock()
    mock_wifi_client_cls.return_value = mock_wifi_client
    mock_measures_taker_cls.return_value = MagicMock()  # FIX: Changed variable name to mock_measures_taker_cls
    mock_measures_sender = MagicMock()
    mock_measures_sender_cls.return_value = mock_measures_sender
    mock_status_updater = MagicMock()
    mock_status_updater_cls.return_value = mock_status_updater
    mock_orchestrator = MagicMock()
    mock_orchestrator_cls.return_value = mock_orchestrator

    # Call the function to test
    main()

    # Assertions
    mock_ap_cls.assert_called_once()
    mock_wifi_client_cls.assert_called_once()
    mock_measures_taker_cls.assert_called_once()
    mock_measures_sender_cls.assert_called_once_with(mock_measures_taker_cls.return_value)
    mock_status_updater_cls.assert_called_once()
    mock_orchestrator_cls.assert_called_once_with(
        mock_ap,
        mock_wifi_client,
        mock_measures_taker_cls.return_value,
        mock_measures_sender,
        mock_status_updater,
    )
    mock_orchestrator.start.assert_called_once()
