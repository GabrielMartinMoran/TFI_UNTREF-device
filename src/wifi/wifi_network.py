class WiFiNetwork:

    def __init__(self, ssid: str, password: str) -> None:
        self._ssid = ssid
        self._password = password

    @property
    def ssid(self) -> str:
        return self._ssid

    @property
    def password(self) -> str:
        return self._password

    @staticmethod
    def from_dict(data: dict) -> 'WiFiNetwork':
        return WiFiNetwork(
            ssid=data['ssid'],
            password=data['password']
        )

    def to_dict(self) -> dict:
        return {
            'ssid': self.ssid,
            'password': self.password
        }
