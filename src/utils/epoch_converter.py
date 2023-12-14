DAYS_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
START_YEAR = 1970


def is_leap_year(year) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def datetime_to_epoch(timestamp_tuple: tuple) -> int:
    """
    :param timestamp_tuple: It should have this format
        (year, month, day, weekday, hours, minutes, seconds, microseconds)
    :return: Seconds since epoch
    """
    year, month, day, _, hour, minute, second, _ = timestamp_tuple
    days = (year - START_YEAR) * 365 + sum(DAYS_PER_MONTH[:month - 1]) + day - 1

    # Leap years adjustment
    leap_years = sum(1 for y in range(START_YEAR, year) if is_leap_year(y))
    days += leap_years

    # if current year is a leap one
    if is_leap_year(year) and month > 2:
        days += 1

    seconds = days * 24 * 3600 + hour * 3600 + minute * 60 + second

    return seconds
