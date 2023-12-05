from src.platform_checker import PlatformChecker

STATUS_LED_PIN = 2
AC_SENSOR_PIN = 34
STATUS_CHANGE_BUTTON_PIN = 25
RELAY_PIN = 32

AC_LIN_FREQUENCY = 50
AC_LINE_VOLTAGE = 220
RMS_SINE_FACTOR = 0.707
AC_LINE_RMS_VOLTAGE = AC_LINE_VOLTAGE * RMS_SINE_FACTOR


"""
    Sensor: ACS712 5A version
    Regarding sensor sensitivity, for a 5v output, the default sensitivity is 0.185 V/A going from -5V to 5V
    Reducing the voltage with a voltage divider where R1=1KΩ and R2=2KΩ, we get a reference voltage of 3.3V
    We can correct SENSOR_SENSITIVITY from 0.185 V/A at 5V to -> 0.185 V/A * (R1/(R1+R2)) = 0.06167 V/A
    (Thanks to https://github.com/RobTillaart/ACS712)
"""
CURRENT_SENSOR_BASE_SENSITIVITY = 0.185  # [V/A]
CURRENT_SENSOR_VOLTAGE_DIVIDER_R1 = 1000  # [Ω]
CURRENT_SENSOR_VOLTAGE_DIVIDER_R2 = 2000  # [Ω]
CURRENT_SENSOR_SENSITIVITY = CURRENT_SENSOR_BASE_SENSITIVITY * (
        CURRENT_SENSOR_VOLTAGE_DIVIDER_R1 / (CURRENT_SENSOR_VOLTAGE_DIVIDER_R1 + CURRENT_SENSOR_VOLTAGE_DIVIDER_R2)
)

MEASURES_PER_CICLE = 20

ON = 1
OFF = 0

if PlatformChecker.is_device():
    HTTP_SERVER_HOST = '192.168.4.1'
    HTTP_SERVER_PORT = 80
else:
    HTTP_SERVER_HOST = ''
    HTTP_SERVER_PORT = 5001

HTTP_SERVER_MAX_CLIENTS = 1
HTTP_SERVER_PRINT_LOGS = True

REMOTE_API_URI = 'http://192.168.0.9:5000/api'

AP_SSID = 'ESP32'
AP_PASSWORD = 'micropython'

WIFI_CLIENT_MAX_CONNECTION_ATTEMPTS = 3
WIFI_CLIENT_DELAY_BETWEEN_ATTEMPTS = 5

SYNC_TIME_MAX_ATTEMPTS = 3
SYNC_TIME_DELAY_BETWEEN_ATTEMPTS = 3

MAX_MEASURES_BATCH_SIZE = 5

INTERVAL_TO_CHECK_NEXT_SCHEDULING_ACTION = 20  # Seconds
INTERVAL_TO_SEND_CURRENT_STATUS = 10  # Seconds
