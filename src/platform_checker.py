from sys import platform


class PlatformChecker:

    @classmethod
    def is_linux(cls):
        return platform == 'linux'
