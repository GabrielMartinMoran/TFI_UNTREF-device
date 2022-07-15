from sys import platform


class PlatformChecker:

    @classmethod
    def is_device(cls):
        return platform == 'esp32'
