from datetime import datetime, timedelta


def round_datetime_to_microsecond(dt: datetime) -> datetime:
    """Rounds a datetime object to the nearest microsecond."""

    rounded_dt = dt + timedelta(microseconds=round(dt.microsecond / 1000) * 1000)
    return rounded_dt.replace(microsecond=rounded_dt.microsecond // 1000 * 1000)
