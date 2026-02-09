from __future__ import annotations

from datetime import datetime, time, timedelta, date
import calendar

from django.utils import timezone


def _local_now() -> datetime:
    # Always return an aware datetime in current TZ
    return timezone.localtime(timezone.now())


def _combine_local(d: date, t: time) -> datetime:
    """
    Combine date + time into an aware datetime in the current timezone.

    We create a naive dt then make it aware in the active Django timezone.
    """
    if t is None:
        raise ValueError("time_of_day is required for non-instant schedules")

    naive = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)

    tz = timezone.get_current_timezone()
    # make_aware expects naive dt
    return timezone.make_aware(naive, tz)


def _validate_weekday(weekday: int) -> None:
    if weekday is None:
        raise ValueError("weekday is required for weekly schedules")
    if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
        raise ValueError("weekday must be an int in range 0..6 (Mon..Sun)")


def _validate_day_of_month(day_of_month: int) -> None:
    if day_of_month is None:
        raise ValueError("day_of_month is required for monthly schedules")
    if not isinstance(day_of_month, int) or day_of_month < 1 or day_of_month > 31:
        raise ValueError("day_of_month must be an int in range 1..31")


def _validate_yearly(month_of_year: int, day_of_year: int) -> None:
    if month_of_year is None or day_of_year is None:
        raise ValueError("month_of_year and day_of_year are required for yearly schedules")
    if not isinstance(month_of_year, int) or month_of_year < 1 or month_of_year > 12:
        raise ValueError("month_of_year must be an int in range 1..12")
    if not isinstance(day_of_year, int) or day_of_year < 1 or day_of_year > 31:
        raise ValueError("day_of_year must be an int in range 1..31")


def next_daily(after_dt: datetime, tod: time) -> datetime:
    if after_dt is None:
        after_dt = _local_now()
    if timezone.is_naive(after_dt):
        after_dt = timezone.make_aware(after_dt, timezone.get_current_timezone())

    today = after_dt.date()
    candidate = _combine_local(today, tod)
    if candidate <= after_dt:
        candidate = _combine_local(today + timedelta(days=1), tod)
    return candidate


def next_weekly(after_dt: datetime, tod: time, weekday: int) -> datetime:
    if after_dt is None:
        after_dt = _local_now()
    if timezone.is_naive(after_dt):
        after_dt = timezone.make_aware(after_dt, timezone.get_current_timezone())

    _validate_weekday(weekday)

    today = after_dt.date()
    current_wd = after_dt.weekday()
    delta = (weekday - current_wd) % 7

    candidate_date = today + timedelta(days=delta)
    candidate = _combine_local(candidate_date, tod)

    if candidate <= after_dt:
        candidate = _combine_local(candidate_date + timedelta(days=7), tod)

    return candidate


def next_monthly(after_dt: datetime, tod: time, day_of_month: int) -> datetime:
    if after_dt is None:
        after_dt = _local_now()
    if timezone.is_naive(after_dt):
        after_dt = timezone.make_aware(after_dt, timezone.get_current_timezone())

    _validate_day_of_month(day_of_month)

    y, m = after_dt.year, after_dt.month

    # Try this month first
    last_day = calendar.monthrange(y, m)[1]
    dom = min(day_of_month, last_day)

    candidate = _combine_local(date(y, m, dom), tod)

    if candidate <= after_dt:
        # Move to next month
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1

        last_day = calendar.monthrange(y, m)[1]
        dom = min(day_of_month, last_day)
        candidate = _combine_local(date(y, m, dom), tod)

    return candidate


def next_yearly(after_dt: datetime, tod: time, month_of_year: int, day_of_year: int) -> datetime:
    if after_dt is None:
        after_dt = _local_now()
    if timezone.is_naive(after_dt):
        after_dt = timezone.make_aware(after_dt, timezone.get_current_timezone())

    _validate_yearly(month_of_year, day_of_year)

    y = after_dt.year

    # Try this year first
    last_day = calendar.monthrange(y, month_of_year)[1]
    d = min(day_of_year, last_day)

    candidate = _combine_local(date(y, month_of_year, d), tod)

    if candidate <= after_dt:
        y += 1
        last_day = calendar.monthrange(y, month_of_year)[1]
        d = min(day_of_year, last_day)
        candidate = _combine_local(date(y, month_of_year, d), tod)

    return candidate
