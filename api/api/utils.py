"""This module provides utilities functions."""

import datetime
import zoneinfo


def utcnow() -> datetime.datetime:
    """Return current datetime."""
    return datetime.datetime.now(tz=zoneinfo.ZoneInfo('UTC'))


def now() -> datetime.datetime:
    """Return current datetime."""
    return datetime.datetime.now(tz=zoneinfo.ZoneInfo('America/Santo_Domingo'))


def today_midnight() -> datetime.datetime:
    """Return today midnight datetime."""
    return datetime.datetime.combine(now(), datetime.time.min).astimezone(
        zoneinfo.ZoneInfo('America/Santo_Domingo')
    )


def yesterday_midnight() -> datetime.datetime:
    """Return yesterday midnight datetime."""
    return datetime.datetime.combine(
        now() - datetime.timedelta(days=1), datetime.time.min
    ).astimezone(zoneinfo.ZoneInfo('America/Santo_Domingo'))


def last_week() -> datetime.datetime:
    """Return datetime of the first day of last week."""
    t = today_midnight()
    return t - datetime.timedelta(days=t.weekday(), weeks=1)


def current_month() -> datetime.datetime:
    """Return datetime of the first day of last month."""
    dt = now()
    return datetime.datetime(
        year=dt.year,
        month=dt.month,
        day=1,
        tzinfo=zoneinfo.ZoneInfo('America/Santo_Domingo'),
    )


def last_month() -> datetime.datetime:
    """Return datetime of the first day of last month."""
    dt = now()
    return datetime.datetime(
        year=dt.year,
        month=dt.month - 1,
        day=1,
        tzinfo=zoneinfo.ZoneInfo('America/Santo_Domingo'),
    )


def current_year() -> datetime.datetime:
    """Return datetime of the first day of last month."""
    dt = now()
    return datetime.datetime(
        year=dt.year,
        month=1,
        day=1,
        tzinfo=zoneinfo.ZoneInfo('America/Santo_Domingo'),
    )


def round_to_hour(dt: datetime.datetime) -> datetime.datetime:
    """Round datetime to hour."""
    return dt.replace(microsecond=0, second=0, minute=0)


def round_to_day(dt: datetime.datetime) -> datetime.datetime:
    """Round datetime to day."""
    return datetime.datetime.combine(dt, datetime.time.min)


def round_to_week(dt: datetime.datetime) -> datetime.datetime:
    """Return datetime of the first day of the week of the given datetime."""
    weekday = dt.weekday()
    return round_to_day(dt) - datetime.timedelta(days=weekday)


def round_to_month(dt: datetime.datetime) -> datetime.datetime:
    """Return datetime of the first day of the month of the given datetime."""
    return datetime.datetime(
        year=dt.year,
        month=dt.month,
        day=1,
        tzinfo=zoneinfo.ZoneInfo('America/Santo_Domingo'),
    )


def convert_to_default_tz(dt: datetime.datetime) -> datetime.datetime:
    """Convert datetime to default timezone."""
    return dt.astimezone(zoneinfo.ZoneInfo('America/Santo_Domingo'))


def today_hour(hour: int) -> datetime.datetime:
    """Return datetime of the first day of last month."""
    dt = now()
    return datetime.datetime(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=hour,
        tzinfo=zoneinfo.ZoneInfo('America/Santo_Domingo'),
    )
