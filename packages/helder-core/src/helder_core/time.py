"""Time handling: UTC inside Helder, source quirks fixed at the edge.

Rijkswaterstaat (RWS) reports every timestamp in MET, a fixed UTC+1 offset that does not follow
daylight saving time: a value measured in June reads ``2026-06-23T08:50:00.000+01:00``. Its
WFS layer ``locatiesmetlaatstewaarneming`` writes the same MET wall-clock time with a ``Z``
suffix, as if it were UTC (verified on 2026-11-03, see docs/research/02-data-sources.md §2).

Every function here returns timezone-aware UTC datetimes and refuses naive input, so a wrong
assumption fails loudly instead of shifting data by an hour.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "MET",
    "RWS_INTERVAL",
    "NaiveDatetimeError",
    "ensure_utc",
    "floor_to_interval",
    "format_rws_time",
    "interval_range",
    "is_aligned",
    "parse_rws_time",
    "parse_rws_wfs_time",
]

MET: Final = timezone(timedelta(hours=1), "MET")
"""The fixed UTC+1 offset RWS uses all year (no daylight saving time)."""

RWS_INTERVAL: Final = timedelta(minutes=10)
"""The measurement interval of most RWS sensor series."""

_EPOCH: Final = datetime(1970, 1, 1, tzinfo=UTC)


class NaiveDatetimeError(ValueError):
    """Raised when a datetime or timestamp has no timezone information."""


def ensure_utc(moment: datetime) -> datetime:
    """Return ``moment`` converted to UTC; refuse naive datetimes.

    Args:
        moment: A timezone-aware datetime.

    Returns:
        The same instant with ``tzinfo=UTC``.

    Raises:
        NaiveDatetimeError: If ``moment`` has no timezone.
    """
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        msg = f"naive datetime {moment.isoformat()} has no timezone; refusing to guess"
        raise NaiveDatetimeError(msg)
    return moment.astimezone(UTC)


def parse_rws_time(text: str) -> datetime:
    """Parse a WaterWebservices timestamp such as ``2026-11-03T10:10:00.000+01:00``.

    Any explicit offset (``+01:00``, ``Z``) is honoured; a timestamp without one is refused.

    Args:
        text: An ISO 8601 timestamp with an offset.

    Returns:
        The instant in UTC.

    Raises:
        NaiveDatetimeError: If the timestamp has no offset.
        ValueError: If the text is not an ISO 8601 timestamp.
    """
    return ensure_utc(datetime.fromisoformat(text.strip()))


def parse_rws_wfs_time(text: str) -> datetime:
    """Parse a time from the RWS WFS latest-observation layer.

    The layer labels MET wall-clock times with ``Z``. A ``Z`` (or a missing offset) is therefore
    read as MET. An explicit numeric offset is honoured as written, so a corrected layer that
    writes ``+01:00`` keeps working; the live contract test (roadmap M4.4) detects a switch to
    true UTC.

    Args:
        text: A timestamp such as ``2026-11-03T10:10:00.000Z``.

    Returns:
        The instant in UTC.
    """
    stripped = text.strip()
    if stripped.endswith(("Z", "z")):
        stripped = stripped[:-1]
    parsed = datetime.fromisoformat(stripped)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=MET)
    return ensure_utc(parsed)


def format_rws_time(moment: datetime) -> str:
    """Format a moment for an RWS request: MET with milliseconds and an explicit offset.

    Args:
        moment: A timezone-aware datetime.

    Returns:
        A string such as ``2026-11-03T10:10:00.000+01:00``.
    """
    return ensure_utc(moment).astimezone(MET).isoformat(timespec="milliseconds")


def floor_to_interval(moment: datetime, interval: timedelta = RWS_INTERVAL) -> datetime:
    """Round a moment down to the start of its interval, aligned to the Unix epoch in UTC.

    Args:
        moment: A timezone-aware datetime.
        interval: A positive interval that divides a day, such as 10 minutes.

    Returns:
        The aligned instant in UTC, never later than ``moment``.

    Raises:
        ValueError: If the interval is not positive.
    """
    if interval <= timedelta(0):
        msg = f"interval must be positive, got {interval}"
        raise ValueError(msg)
    since_epoch = ensure_utc(moment) - _EPOCH
    return _EPOCH + (since_epoch // interval) * interval


def is_aligned(moment: datetime, interval: timedelta = RWS_INTERVAL) -> bool:
    """Whether ``moment`` lies exactly on an interval boundary."""
    return floor_to_interval(moment, interval) == ensure_utc(moment)


def interval_range(
    start: datetime, end: datetime, interval: timedelta = RWS_INTERVAL
) -> Iterator[datetime]:
    """Yield the aligned interval starts in ``[start, end)``, in UTC.

    The first value is the first boundary at or after ``start``. Use it to list the expected
    timestamps of a series, for example to find gaps.

    Args:
        start: Inclusive lower bound (timezone-aware).
        end: Exclusive upper bound (timezone-aware).
        interval: The series interval.

    Yields:
        Aligned UTC datetimes.
    """
    current = floor_to_interval(start, interval)
    if current < ensure_utc(start):
        current += interval
    stop = ensure_utc(end)
    while current < stop:
        yield current
        current += interval
