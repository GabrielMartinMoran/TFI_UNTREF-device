from unittest.mock import patch, MagicMock

from src.main import main


@patch('src.main.Orchestrator')
@patch('src.main.ConfigurationWebAPI')
@patch('src.main.MechanicalStatusChangeDetector')
@patch('src.main.RemoteStatusChangeDetector')
@patch('src.main.DeviceStatus')
@patch('src.main.StatusSender')
@patch('src.main.MeasuresSender')
@patch('src.main.MeasuresTaker')
@patch('src.main.Relay')
@patch('src.main.StatusLed')
@patch('src.main.WiFiClient')
@patch('src.main.AccessPoint')
def test_main(
        AccessPointMock,
        WiFiClientMock,
        StatusLedMock,
        RelayMock,
        MeasuresTakerMock,
        MeasuresSenderMock,
        StatusSenderMock,
        DeviceStatusMock,
        RemoteStatusChangeDetectorMock,
        MechanicalStatusChangeDetectorMock,
        ConfigurationWebAPIMock,
        OrchestratorMock
):
    mocked_classes = [
        AccessPointMock, WiFiClientMock, StatusLedMock, RelayMock, MeasuresTakerMock, MeasuresSenderMock,
        StatusSenderMock, DeviceStatusMock, RemoteStatusChangeDetectorMock, MechanicalStatusChangeDetectorMock,
        ConfigurationWebAPIMock, OrchestratorMock
    ]

    for mocked_class in mocked_classes:
        mocked_class.return_value = MagicMock()

    # Call the function to test
    main()

    for mocked_class in mocked_classes:
        mocked_class.assert_called_once()

    StatusLedMock.assert_called_once_with(False)
    RelayMock.assert_called_once_with(False)
    MeasuresSenderMock.assert_called_once_with(MeasuresTakerMock.return_value)
    DeviceStatusMock.assert_called_once_with(
        StatusSenderMock.return_value, StatusLedMock.return_value, RelayMock.return_value
    )
    RemoteStatusChangeDetectorMock.assert_called_once_with(DeviceStatusMock.return_value)
    MechanicalStatusChangeDetectorMock.assert_called_once_with(DeviceStatusMock.return_value)
    ConfigurationWebAPIMock.assert_called_once_with(WiFiClientMock.return_value, DeviceStatusMock.return_value)
    OrchestratorMock.assert_called_once_with(
        AccessPointMock.return_value,
        WiFiClientMock.return_value,
        MeasuresTakerMock.return_value,
        MeasuresSenderMock.return_value,
        DeviceStatusMock.return_value,
        RemoteStatusChangeDetectorMock.return_value,
        MechanicalStatusChangeDetectorMock.return_value,
        ConfigurationWebAPIMock.return_value
    )
    OrchestratorMock.return_value.start.assert_called_once()
