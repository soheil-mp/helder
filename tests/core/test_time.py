"""Time handling: RWS's fixed MET offset, the mislabelled WFS layer and interval alignment."""

from datetime import UTC, datetime, timedelta, timezone
from itertools import pairwise
from zoneinfo import ZoneInfo

import pytest
from hypothesis import given
from hypothesis import strategies as st

from helder_core.time import (
    MET,
    RWS_INTERVAL,
    NaiveDatetimeError,
    ensure_utc,
    floor_to_interval,
    format_rws_time,
    interval_range,
    is_aligned,
    parse_rws_time,
    parse_rws_wfs_time,
)

AMSTERDAM = ZoneInfo("Europe/Amsterdam")

aware_moments = st.datetimes(
    min_value=datetime(1980, 1, 1),  # noqa: DTZ001 (bounds for st.datetimes must be naive)
    max_value=datetime(2100, 1, 1),  # noqa: DTZ001
    timezones=st.sampled_from([UTC, MET, AMSTERDAM, timezone(timedelta(hours=-5))]),
    allow_imaginary=False,  # local times skipped by a spring-forward clock change do not exist
)
intervals = st.sampled_from([timedelta(minutes=m) for m in (1, 5, 10, 15, 30, 60)])


# --- Values observed on the live services on 2026-11-03 ----------------------------------


def test_api_timestamp_is_met() -> None:
    assert parse_rws_time("2026-11-03T10:10:00.000+01:00") == datetime(
        2026, 11, 3, 9, 10, tzinfo=UTC
    )


def test_api_keeps_plus_one_in_summer() -> None:
    # RWS reported a June value as 08:50+01:00, which is 09:50 Amsterdam summer time.
    moment = parse_rws_time("2026-06-23T08:50:00.000+01:00")
    assert moment == datetime(2026, 6, 23, 7, 50, tzinfo=UTC)
    assert moment.astimezone(AMSTERDAM).hour == 9


def test_wfs_z_label_is_read_as_met() -> None:
    # The WFS layer showed 10:10:00Z at 09:33 UTC: that value is 09:10 UTC, not 10:10 UTC.
    assert parse_rws_wfs_time("2026-11-03T10:10:00.000Z") == datetime(
        2026, 11, 3, 9, 10, tzinfo=UTC
    )


def test_wfs_and_api_agree_on_the_same_value() -> None:
    assert parse_rws_wfs_time("2026-11-03T10:10:00.000Z") == parse_rws_time(
        "2026-11-03T10:10:00.000+01:00"
    )


def test_wfs_explicit_offset_is_honoured() -> None:
    assert parse_rws_wfs_time("2026-11-03T10:10:00+01:00") == datetime(
        2026, 11, 3, 9, 10, tzinfo=UTC
    )
    assert parse_rws_wfs_time("2026-11-03T10:10:00") == datetime(2026, 11, 3, 9, 10, tzinfo=UTC)


def test_format_matches_the_rws_request_format() -> None:
    assert format_rws_time(datetime(2026, 11, 3, 9, 10, tzinfo=UTC)) == (
        "2026-11-03T10:10:00.000+01:00"
    )


# --- Refusing to guess ---------------------------------------------------------------------


def test_naive_input_is_refused() -> None:
    with pytest.raises(NaiveDatetimeError):
        ensure_utc(datetime(2026, 11, 3, 10, 10))  # noqa: DTZ001 (deliberately naive)
    with pytest.raises(NaiveDatetimeError):
        parse_rws_time("2026-11-03T10:10:00.000")


def test_garbage_is_refused() -> None:
    with pytest.raises(ValueError, match="Invalid isoformat"):
        parse_rws_time("yesterday")


def test_non_positive_interval_is_refused() -> None:
    with pytest.raises(ValueError, match="positive"):
        floor_to_interval(datetime(2026, 1, 1, tzinfo=UTC), timedelta(0))


# --- Properties ----------------------------------------------------------------------------


@given(aware_moments)
def test_results_are_utc(moment: datetime) -> None:
    assert ensure_utc(moment).tzinfo is UTC
    # Compare instants, not objects: Python never treats an ambiguous local time (a repeated
    # hour in autumn) as equal to a datetime in another zone (PEP 495).
    assert ensure_utc(moment).timestamp() == moment.timestamp()


@given(aware_moments)
def test_format_then_parse_round_trips_at_millisecond_precision(moment: datetime) -> None:
    expected = ensure_utc(moment).replace(microsecond=moment.microsecond // 1000 * 1000)
    assert parse_rws_time(format_rws_time(moment)) == expected


@given(aware_moments)
def test_formatted_offset_never_changes_with_daylight_saving(moment: datetime) -> None:
    assert format_rws_time(moment).endswith("+01:00")


@given(aware_moments, intervals)
def test_floor_is_aligned_idempotent_and_close(moment: datetime, interval: timedelta) -> None:
    floored = floor_to_interval(moment, interval)
    assert floored <= moment < floored + interval
    assert is_aligned(floored, interval)
    assert floor_to_interval(floored, interval) == floored


@given(aware_moments, st.integers(min_value=0, max_value=500), intervals)
def test_interval_range_lists_every_boundary_once(
    start: datetime, steps: int, interval: timedelta
) -> None:
    # Arithmetic on zoned datetimes is wall-clock arithmetic; elapsed time is counted in UTC.
    start = ensure_utc(start)
    end = start + steps * interval
    values = list(interval_range(start, end, interval))
    assert all(is_aligned(v, interval) for v in values)
    assert all(b - a == interval for a, b in pairwise(values))
    if values:
        assert values[0] >= start
        assert values[0] - interval < start
        assert values[-1] < end
    assert steps - 1 <= len(values) <= steps


def test_interval_range_across_the_autumn_clock_change() -> None:
    # Amsterdam clocks go back on 2026-10-25 at 03:00 CEST; RWS's MET series does not notice.
    start = datetime(2026, 10, 25, 0, 0, tzinfo=MET)
    values = list(interval_range(start, start + timedelta(hours=4)))
    assert len(values) == 4 * 60 // 10
    assert len({v.astimezone(MET).isoformat() for v in values}) == len(values)


def test_default_interval_is_ten_minutes() -> None:
    assert timedelta(minutes=10) == RWS_INTERVAL
    assert is_aligned(datetime(2026, 11, 3, 9, 40, tzinfo=UTC))
    assert not is_aligned(datetime(2026, 11, 3, 9, 45, tzinfo=UTC))
