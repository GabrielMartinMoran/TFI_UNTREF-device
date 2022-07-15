from datetime import datetime


class RTC:

    @classmethod
    def datetime(cls) -> tuple:
        now = datetime.utcnow()
        return now.year, now.month, now.day, now.weekday(), now.hour, now.minute, now.second, now.microsecond
