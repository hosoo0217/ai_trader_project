from __future__ import annotations

import ast
from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone, tzinfo
import hashlib
import importlib.metadata
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest
from zoneinfo import ZoneInfo

import smc.kill_zones as kill_zones
from smc.kill_zones import (
    KILL_ZONE_DETECTOR_VERSION,
    KILL_ZONE_TIMEZONE,
    KillZoneCalendarEntry,
    KillZoneContext,
    KillZoneName,
    KillZoneObservation,
    KillZoneQuality,
    KillZoneResult,
    KillZoneSessionStatus,
    KillZoneSnapshot,
    analyze_kill_zones,
    make_kill_zone_id,
)
from smc.smc_v2_primitives import SMCV2PrimitiveStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
CALENDAR_VERSION = "CME-SYNTHETIC-1"
TIMEZONE_DATA_VERSION = importlib.metadata.version("tzdata").upper()


def _utc(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    *,
    fold: int = 0,
) -> datetime:
    return datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond,
        tzinfo=NY,
        fold=fold,
    ).astimezone(UTC)


def _observation(
    index: int,
    timestamp: datetime,
    *,
    is_closed: bool = True,
) -> KillZoneObservation:
    return KillZoneObservation(index=index, timestamp=timestamp, is_closed=is_closed)


def _entry(
    trade_date: date,
    *,
    status: KillZoneSessionStatus = KillZoneSessionStatus.OPEN,
    open_local: datetime | None = None,
    close_local: datetime | None = None,
    calendar_version: str = CALENDAR_VERSION,
) -> KillZoneCalendarEntry:
    if status is KillZoneSessionStatus.SESSION_CLOSED:
        return KillZoneCalendarEntry(
            calendar_version=calendar_version,
            trade_date=trade_date,
            session_status=status,
            session_open_timestamp=None,
            session_close_timestamp=None,
        )
    opening = open_local or datetime.combine(
        trade_date - timedelta(days=1),
        time(18, 0),
        tzinfo=NY,
    )
    closing = close_local or datetime.combine(
        trade_date,
        time(17, 0),
        tzinfo=NY,
    )
    return KillZoneCalendarEntry(
        calendar_version=calendar_version,
        trade_date=trade_date,
        session_status=status,
        session_open_timestamp=opening.astimezone(UTC),
        session_close_timestamp=closing.astimezone(UTC),
    )


def _analyze(
    observations: tuple[KillZoneObservation, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    *,
    instrument: str = "GC",
    timeframe: str = "M5",
    calendar_version: str = CALENDAR_VERSION,
    timezone_data_version: str = TIMEZONE_DATA_VERSION,
) -> KillZoneResult:
    return analyze_kill_zones(
        instrument=instrument,
        timeframe=timeframe,
        observations=observations,
        calendar_entries=calendar_entries,
        calendar_version=calendar_version,
        timezone_data_version=timezone_data_version,
    )


def _context_id(
    *,
    index: int = 1,
    timestamp: datetime | None = None,
    trade_date: date = date(2026, 1, 5),
    zone: KillZoneName | None = KillZoneName.LONDON,
    session_status: KillZoneSessionStatus | None = KillZoneSessionStatus.OPEN,
    quality: KillZoneQuality = KillZoneQuality.VERIFIED,
    instrument: str = "GC",
    timeframe: str = "M5",
    calendar_version: str = CALENDAR_VERSION,
    timezone_data_version: str = TIMEZONE_DATA_VERSION,
) -> str:
    return make_kill_zone_id(
        identity_kind="CONTEXT",
        instrument=instrument,
        timeframe=timeframe,
        calendar_version=calendar_version,
        timezone_name=KILL_ZONE_TIMEZONE,
        timezone_data_version=timezone_data_version,
        observation_index=index,
        observation_timestamp=timestamp or _utc(2026, 1, 5, 2),
        trade_date=trade_date,
        zone=zone,
        session_status=session_status,
        quality=quality,
    )


def _snapshot_id(
    *,
    effective_index: int = 1,
    effective_timestamp: datetime | None = None,
    context_ids: tuple[str, ...] | None = None,
    instrument: str = "GC",
    timeframe: str = "M5",
    calendar_version: str = CALENDAR_VERSION,
    timezone_data_version: str = TIMEZONE_DATA_VERSION,
) -> str:
    return make_kill_zone_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        calendar_version=calendar_version,
        timezone_name=KILL_ZONE_TIMEZONE,
        timezone_data_version=timezone_data_version,
        effective_index=effective_index,
        effective_timestamp=effective_timestamp or _utc(2026, 1, 5, 2),
        context_ids=context_ids or (_context_id(),),
    )


# Logical case 1.
def test_case_01_missing_top_level_context_and_invalid_text_precedence() -> None:
    assert _analyze(None, ()).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _analyze((), None).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _analyze(None, (), instrument=" ").status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(None, (), timezone_data_version="").status is SMCV2PrimitiveStatus.INVALID
    malformed_observation = KillZoneObservation(
        index=1,
        timestamp=datetime(2026, 1, 5, 2),
        is_closed=True,
    )
    malformed_calendar = replace(
        _entry(date(2026, 1, 5)),
        session_close_timestamp=None,
    )
    invalid_observation = _analyze((malformed_observation,), None)
    invalid_calendar = _analyze(None, (malformed_calendar,))
    assert invalid_observation.status is SMCV2PrimitiveStatus.INVALID
    assert invalid_calendar.status is SMCV2PrimitiveStatus.INVALID
    assert invalid_observation.contexts == invalid_observation.snapshots == ()
    assert invalid_calendar.contexts == invalid_calendar.snapshots == ()


# Logical case 2.
def test_case_02_complete_empty_inputs_are_none() -> None:
    result = _analyze((), ())
    assert result == KillZoneResult(status=SMCV2PrimitiveStatus.NONE)


# Logical case 3.
def test_case_03_text_and_equivalent_utc_normalization_are_deterministic() -> None:
    timestamp = _utc(2026, 1, 5, 2)
    equivalent = timestamp.astimezone(timezone(timedelta(hours=9)))
    first = _context_id(timestamp=timestamp, instrument=" gc ", timeframe=" m5 ")
    second = _context_id(
        timestamp=equivalent,
        instrument="GC",
        timeframe="M5",
        calendar_version=" cme-synthetic-1 ",
        timezone_data_version=f" {TIMEZONE_DATA_VERSION.lower()} ",
    )
    assert first == second


# Logical case 4.
@pytest.mark.parametrize(
    "value",
    [
        KillZoneObservation(index=-1, timestamp=_utc(2026, 1, 5, 2), is_closed=True),
        KillZoneObservation(index=True, timestamp=_utc(2026, 1, 5, 2), is_closed=True),
        KillZoneObservation(index=1, timestamp=datetime(2026, 1, 5, 2), is_closed=True),
        KillZoneObservation(index=1, timestamp=_utc(2026, 1, 5, 2), is_closed=False),
        KillZoneObservation(index=1, timestamp=_utc(2026, 1, 5, 2), is_closed=1),
    ],
)
def test_case_04_observation_contract_is_fail_closed(value: KillZoneObservation) -> None:
    assert _analyze((value,), ()).status is SMCV2PrimitiveStatus.INVALID


# Logical case 5.
@pytest.mark.parametrize(
    "observations",
    [
        [
            _observation(1, _utc(2026, 1, 5, 1)),
        ],
        (
            _observation(1, _utc(2026, 1, 5, 1)),
            _observation(1, _utc(2026, 1, 5, 2)),
        ),
        (
            _observation(1, _utc(2026, 1, 5, 2)),
            _observation(2, _utc(2026, 1, 5, 1)),
        ),
        (
            _observation(2, _utc(2026, 1, 5, 1)),
            _observation(1, _utc(2026, 1, 5, 2)),
        ),
    ],
)
def test_case_05_observation_order_is_not_silently_sorted(
    observations: object,
) -> None:
    assert _analyze(observations, ()).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[arg-type]


# Logical case 6.
def test_case_06_calendar_contract_and_frozen_state() -> None:
    entry = _entry(date(2026, 1, 5))
    with pytest.raises(FrozenInstanceError):
        entry.trade_date = date(2026, 1, 6)  # type: ignore[misc]
    malformed_date = replace(entry, trade_date=datetime(2026, 1, 5))  # type: ignore[arg-type]
    malformed_status = replace(entry, session_status="OPEN")  # type: ignore[arg-type]
    mismatched = replace(entry, calendar_version="OTHER")
    for value in (malformed_date, malformed_status, mismatched):
        assert _analyze((), (value,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 7.
@pytest.mark.parametrize("mode", ["duplicate", "reordered", "weekend_open"])
def test_case_07_calendar_order_uniqueness_and_weekend_closure(mode: str) -> None:
    monday = _entry(date(2026, 1, 5))
    tuesday = _entry(date(2026, 1, 6))
    entries = {
        "duplicate": (monday, monday),
        "reordered": (tuesday, monday),
        "weekend_open": (_entry(date(2026, 1, 10)),),
    }[mode]
    assert _analyze((), entries).status is SMCV2PrimitiveStatus.INVALID


# Logical case 8.
@pytest.mark.parametrize("mode", ["missing", "closed_has_times", "reverse", "duration", "local_date"])
def test_case_08_calendar_interval_rules(mode: str) -> None:
    trade_date = date(2026, 1, 5)
    base = _entry(trade_date)
    values = {
        "missing": replace(base, session_close_timestamp=None),
        "closed_has_times": replace(base, session_status=KillZoneSessionStatus.SESSION_CLOSED),
        "reverse": replace(
            base,
            session_open_timestamp=_utc(2026, 1, 5, 17),
            session_close_timestamp=_utc(2026, 1, 5, 16),
        ),
        "duration": replace(
            base,
            session_open_timestamp=_utc(2026, 1, 3, 16),
            session_close_timestamp=_utc(2026, 1, 5, 17),
        ),
        "local_date": replace(base, session_close_timestamp=_utc(2026, 1, 6, 17)),
    }
    assert _analyze((), (values[mode],)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 9.
def test_case_09_only_exact_new_york_timezone_token_is_accepted() -> None:
    with pytest.raises(ValueError):
        make_kill_zone_id(
            identity_kind="CONTEXT",
            instrument="GC",
            timeframe="M5",
            calendar_version=CALENDAR_VERSION,
            timezone_name="UTC-5",
            timezone_data_version=TIMEZONE_DATA_VERSION,
            observation_index=1,
            observation_timestamp=_utc(2026, 1, 5, 2),
            trade_date=date(2026, 1, 5),
            zone=KillZoneName.LONDON,
            session_status=KillZoneSessionStatus.OPEN,
            quality=KillZoneQuality.VERIFIED,
        )


# Logical case 10.
def test_case_10_timezone_runtime_unknown_and_version_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kill_zones, "_runtime_timezone_data_version", lambda: None)
    assert _analyze((), ()).status is SMCV2PrimitiveStatus.UNKNOWN
    malformed = KillZoneObservation(
        index=1,
        timestamp=datetime(2026, 1, 5, 2),
        is_closed=True,
    )
    assert _analyze((malformed,), ()).status is SMCV2PrimitiveStatus.INVALID
    monkeypatch.undo()
    assert _analyze((), (), timezone_data_version="WRONG").status is SMCV2PrimitiveStatus.INVALID
    monkeypatch.setattr(kill_zones, "_load_timezone", lambda: None)
    assert _analyze((), ()).status is SMCV2PrimitiveStatus.UNKNOWN
    malformed_entry = replace(
        _entry(date(2026, 1, 5)),
        session_close_timestamp=None,
    )
    assert _analyze((), (malformed_entry,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 11.
@pytest.mark.parametrize("timestamp", [_utc(2026, 1, 4, 20), _utc(2026, 7, 5, 20)])
def test_case_11_asia_start_is_inclusive_in_winter_and_summer(timestamp: datetime) -> None:
    trade_date = timestamp.astimezone(NY).date() + timedelta(days=1)
    result = _analyze((_observation(1, timestamp),), (_entry(trade_date),))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.contexts[0].zone is KillZoneName.ASIA


# Logical case 12.
def test_case_12_local_midnight_is_outside_asia() -> None:
    assert _analyze((_observation(1, _utc(2026, 1, 5, 0)),), ()).status is SMCV2PrimitiveStatus.NONE


# Logical case 13.
def test_case_13_london_boundaries_are_start_inclusive_end_exclusive() -> None:
    entry = _entry(date(2026, 1, 5))
    start = _analyze((_observation(1, _utc(2026, 1, 5, 2)),), (entry,))
    end = _analyze((_observation(1, _utc(2026, 1, 5, 5)),), (entry,))
    assert start.contexts[0].zone is KillZoneName.LONDON
    assert end.status is SMCV2PrimitiveStatus.NONE


# Logical case 14.
def test_case_14_new_york_am_boundaries() -> None:
    entry = _entry(date(2026, 1, 5))
    start = _analyze((_observation(1, _utc(2026, 1, 5, 7)),), (entry,))
    end = _analyze((_observation(1, _utc(2026, 1, 5, 10)),), (entry,))
    assert start.contexts[0].zone is KillZoneName.NEW_YORK_AM
    assert end.status is SMCV2PrimitiveStatus.NONE


# Logical case 15.
def test_case_15_new_york_pm_boundaries() -> None:
    entry = _entry(date(2026, 1, 5))
    start = _analyze((_observation(1, _utc(2026, 1, 5, 13)),), (entry,))
    end = _analyze((_observation(1, _utc(2026, 1, 5, 16)),), (entry,))
    assert start.contexts[0].zone is KillZoneName.NEW_YORK_PM
    assert end.status is SMCV2PrimitiveStatus.NONE


# Logical case 16.
@pytest.mark.parametrize("hour,minute,microsecond", [(1, 59, 999999), (5, 0, 0), (6, 59, 999999), (10, 0, 0), (12, 59, 999999), (16, 0, 0), (19, 59, 999999)])
def test_case_16_outside_microsecond_boundaries_never_overlap(
    hour: int,
    minute: int,
    microsecond: int,
) -> None:
    result = _analyze(
        (_observation(1, _utc(2026, 1, 5, hour, minute, microsecond=microsecond)),),
        (),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE


# Logical case 17.
def test_case_17_asia_uses_following_trade_date() -> None:
    timestamp = _utc(2026, 1, 5, 20)
    result = _analyze((_observation(1, timestamp),), (_entry(date(2026, 1, 6)),))
    assert result.contexts[0].trade_date == date(2026, 1, 6)


# Logical case 18.
def test_case_18_sunday_asia_may_open_and_friday_asia_is_closed() -> None:
    sunday = _analyze(
        (_observation(1, _utc(2026, 1, 4, 20)),),
        (_entry(date(2026, 1, 5)),),
    )
    friday = _analyze((_observation(1, _utc(2026, 1, 9, 20)),), ())
    assert sunday.status is SMCV2PrimitiveStatus.VALID
    assert friday.status is SMCV2PrimitiveStatus.NONE
    assert friday.contexts[0].session_status is KillZoneSessionStatus.SESSION_CLOSED


# Logical case 19.
@pytest.mark.parametrize("hour,zone", [(2, KillZoneName.LONDON), (7, KillZoneName.NEW_YORK_AM), (13, KillZoneName.NEW_YORK_PM)])
def test_case_19_non_asia_windows_keep_local_trade_date(hour: int, zone: KillZoneName) -> None:
    trade_date = date(2026, 1, 5)
    result = _analyze((_observation(1, _utc(2026, 1, 5, hour)),), (_entry(trade_date),))
    assert result.contexts[0].trade_date == trade_date
    assert result.contexts[0].zone is zone


# Logical case 20.
def test_case_20_outside_windows_need_no_calendar() -> None:
    result = _analyze((_observation(1, _utc(2026, 1, 5, 6)),), ())
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.contexts == ()


# Logical case 21.
def test_case_21_open_session_boundaries_are_start_inclusive_end_exclusive() -> None:
    trade_date = date(2026, 1, 5)
    entry = _entry(
        trade_date,
        open_local=datetime(2026, 1, 5, 2, tzinfo=NY),
        close_local=datetime(2026, 1, 5, 3, tzinfo=NY),
    )
    opened = _analyze((_observation(1, _utc(2026, 1, 5, 2)),), (entry,))
    closed = _analyze((_observation(1, _utc(2026, 1, 5, 3)),), (entry,))
    assert opened.status is SMCV2PrimitiveStatus.VALID
    assert closed.contexts[0].zone is None


# Logical case 22.
def test_case_22_holiday_is_verified_closed_context_not_valid() -> None:
    trade_date = date(2026, 1, 5)
    result = _analyze(
        (_observation(1, _utc(2026, 1, 5, 7)),),
        (_entry(trade_date, status=KillZoneSessionStatus.SESSION_CLOSED),),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.contexts[0].quality is KillZoneQuality.VERIFIED
    assert result.contexts[0].zone is None


# Logical case 23.
def test_case_23_early_close_truncates_an_overlapping_window() -> None:
    trade_date = date(2026, 1, 5)
    entry = _entry(
        trade_date,
        status=KillZoneSessionStatus.EARLY_CLOSE,
        close_local=datetime(2026, 1, 5, 14, tzinfo=NY),
    )
    before = _analyze((_observation(1, _utc(2026, 1, 5, 13, 59, 59)),), (entry,))
    at_close = _analyze((_observation(1, _utc(2026, 1, 5, 14)),), (entry,))
    assert before.contexts[0].zone is KillZoneName.NEW_YORK_PM
    assert at_close.contexts[0].zone is None


# Logical case 24.
@pytest.mark.parametrize("hour", [7, 9])
def test_case_24_before_open_or_after_close_is_effectively_closed(hour: int) -> None:
    trade_date = date(2026, 1, 5)
    entry = _entry(
        trade_date,
        open_local=datetime(2026, 1, 5, 8, tzinfo=NY),
        close_local=datetime(2026, 1, 5, 9, tzinfo=NY),
    )
    result = _analyze((_observation(1, _utc(2026, 1, 5, hour)),), (entry,))
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.contexts[0].session_status is KillZoneSessionStatus.SESSION_CLOSED


# Logical case 25.
def test_case_25_missing_calendar_emits_unverified_unknown_context_and_snapshot() -> None:
    result = _analyze((_observation(1, _utc(2026, 1, 5, 7)),), ())
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.contexts[0].zone is KillZoneName.NEW_YORK_AM
    assert result.contexts[0].session_status is None
    assert result.contexts[0].quality is KillZoneQuality.CALENDAR_UNVERIFIED
    assert result.snapshots[0].context_ids == (result.contexts[0].context_id,)


# Logical case 26.
def test_case_26_calendar_repair_is_a_different_run_not_retroactive_enrichment() -> None:
    observation = _observation(1, _utc(2026, 1, 5, 7))
    unknown = _analyze((observation,), ())
    verified = _analyze((observation,), (_entry(date(2026, 1, 5)),))
    assert unknown.contexts[0].quality is KillZoneQuality.CALENDAR_UNVERIFIED
    assert verified.contexts[0].quality is KillZoneQuality.VERIFIED
    assert unknown.contexts[0].context_id != verified.contexts[0].context_id


# Logical case 27.
def test_case_27_winter_database_offset_classifies_exact_local_time() -> None:
    timestamp = datetime(2026, 1, 5, 12, tzinfo=UTC)
    result = _analyze((_observation(1, timestamp),), (_entry(date(2026, 1, 5)),))
    assert result.contexts[0].zone is KillZoneName.NEW_YORK_AM


# Logical case 28.
def test_case_28_summer_database_offset_classifies_exact_local_time() -> None:
    timestamp = datetime(2026, 7, 6, 11, tzinfo=UTC)
    result = _analyze((_observation(1, timestamp),), (_entry(date(2026, 7, 6)),))
    assert result.contexts[0].zone is KillZoneName.NEW_YORK_AM


# Logical case 29.
def test_case_29_spring_forward_conversion_is_deterministic_from_utc() -> None:
    before = _analyze((_observation(1, datetime(2026, 3, 8, 6, 59, 59, tzinfo=UTC)),), ())
    after = _analyze((_observation(1, datetime(2026, 3, 8, 7, 0, tzinfo=UTC)),), ())
    assert before == _analyze((_observation(1, datetime(2026, 3, 8, 6, 59, 59, tzinfo=UTC)),), ())
    assert after == _analyze((_observation(1, datetime(2026, 3, 8, 7, 0, tzinfo=UTC)),), ())


# Logical case 30.
def test_case_30_fall_back_repeated_hour_is_deterministic_from_utc() -> None:
    first_utc = datetime(2026, 11, 1, 5, 30, tzinfo=UTC)
    second_utc = datetime(2026, 11, 1, 6, 30, tzinfo=UTC)
    first_local = first_utc.astimezone(NY)
    second_local = second_utc.astimezone(NY)
    first = _analyze((_observation(1, first_utc),), ())
    second = _analyze((_observation(1, second_utc),), ())
    assert first.status is SMCV2PrimitiveStatus.NONE
    assert second.status is SMCV2PrimitiveStatus.NONE
    assert first_utc != second_utc
    assert first_local.replace(tzinfo=None) == second_local.replace(tzinfo=None)
    assert (first_local.fold, second_local.fold) == (0, 1)
    assert first_local.utcoffset() != second_local.utcoffset()
    assert first == _analyze((_observation(1, first_utc),), ())
    assert second == _analyze((_observation(1, second_utc),), ())


# Logical case 31.
def test_case_31_timestamp_conversion_exceptions_are_contained() -> None:
    class ExplodingTZ(tzinfo):
        def utcoffset(self, dt: datetime | None) -> timedelta:
            raise RuntimeError("boom")

    malformed = KillZoneObservation(
        index=1,
        timestamp=datetime(2026, 1, 5, 2, tzinfo=ExplodingTZ()),
        is_closed=True,
    )
    assert _analyze((malformed,), ()).status is SMCV2PrimitiveStatus.INVALID


# Logical case 32.
def test_case_32_public_context_is_non_directional() -> None:
    names = {item.name for item in fields(KillZoneContext)}
    forbidden = {"direction", "bias", "signal", "score", "confidence", "trade", "side"}
    assert names.isdisjoint(forbidden)


# Logical case 33.
def test_case_33_multi_zone_output_is_chronological_and_deterministic() -> None:
    entry = _entry(date(2026, 1, 5))
    observations = (
        _observation(1, _utc(2026, 1, 5, 2)),
        _observation(2, _utc(2026, 1, 5, 7)),
        _observation(3, _utc(2026, 1, 5, 13)),
    )
    result = _analyze(observations, (entry,))
    assert tuple(item.zone for item in result.contexts) == (
        KillZoneName.LONDON,
        KillZoneName.NEW_YORK_AM,
        KillZoneName.NEW_YORK_PM,
    )
    assert result == _analyze(observations, (entry,), instrument=" gc ")


# Logical case 34.
def test_case_34_later_malformed_observation_preserves_strict_prior_evidence() -> None:
    entry = _entry(date(2026, 1, 5))
    first = _observation(1, _utc(2026, 1, 5, 2))
    prefix = _analyze((first,), (entry,))
    later = KillZoneObservation(index=2, timestamp=_utc(2026, 1, 5, 7), is_closed=False)
    failed = _analyze((first, later), (entry,))
    assert failed.status is SMCV2PrimitiveStatus.INVALID
    assert failed.contexts == prefix.contexts
    assert failed.snapshots == prefix.snapshots
    unknowable = object.__new__(KillZoneObservation)
    object.__setattr__(unknowable, "is_closed", False)
    assert _analyze((first, unknowable), (entry,)).contexts == ()


# Logical case 35.
def test_case_35_later_malformed_calendar_preserves_strict_prior_evidence() -> None:
    monday = _entry(date(2026, 1, 5))
    tuesday = replace(_entry(date(2026, 1, 6)), session_close_timestamp=None)
    observations = (
        _observation(1, _utc(2026, 1, 5, 2)),
        _observation(2, _utc(2026, 1, 6, 2)),
    )
    prefix = _analyze(observations[:1], (monday,))
    failed = _analyze(observations, (monday, tuesday))
    assert failed.status is SMCV2PrimitiveStatus.INVALID
    assert failed.contexts == prefix.contexts
    assert failed.snapshots == prefix.snapshots


# Logical case 36.
def test_case_36_invalid_has_precedence_over_prior_unknown() -> None:
    observations = (
        _observation(1, _utc(2026, 1, 5, 2)),
        KillZoneObservation(index=2, timestamp=_utc(2026, 1, 5, 7), is_closed=False),
    )
    result = _analyze(observations, ())
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.contexts[0].quality is KillZoneQuality.CALENDAR_UNVERIFIED
    assert SMCV2PrimitiveStatus.AMBIGUOUS not in (result.status,)


# Logical case 37.
@pytest.mark.parametrize(
    "kwargs",
    [
        {"effective_index": 1},
        {"effective_timestamp": _utc(2026, 1, 5, 2)},
        {"context_ids": (hashlib.sha256(b"x").hexdigest(),)},
        {"quality": KillZoneQuality.VERIFIED, "zone": None, "session_status": KillZoneSessionStatus.OPEN},
        {"quality": KillZoneQuality.VERIFIED, "zone": KillZoneName.LONDON, "session_status": KillZoneSessionStatus.SESSION_CLOSED},
        {"quality": KillZoneQuality.CALENDAR_UNVERIFIED, "zone": None, "session_status": None},
        {
            "quality": KillZoneQuality.CALENDAR_UNVERIFIED,
            "zone": KillZoneName.NEW_YORK_AM,
            "session_status": None,
            "observation_timestamp": _utc(2026, 1, 5, 6),
        },
        {
            "quality": KillZoneQuality.VERIFIED,
            "zone": KillZoneName.NEW_YORK_AM,
            "session_status": KillZoneSessionStatus.OPEN,
            "observation_timestamp": _utc(2026, 1, 5, 2),
        },
        {"trade_date": date(2026, 1, 6)},
    ],
)
def test_case_37_context_identity_schema_is_exhaustive(kwargs: dict[str, object]) -> None:
    base: dict[str, object] = {
        "identity_kind": "CONTEXT",
        "instrument": "GC",
        "timeframe": "M5",
        "calendar_version": CALENDAR_VERSION,
        "timezone_name": KILL_ZONE_TIMEZONE,
        "timezone_data_version": TIMEZONE_DATA_VERSION,
        "observation_index": 1,
        "observation_timestamp": _utc(2026, 1, 5, 2),
        "trade_date": date(2026, 1, 5),
        "zone": KillZoneName.LONDON,
        "session_status": KillZoneSessionStatus.OPEN,
        "quality": KillZoneQuality.VERIFIED,
    }
    base.update(kwargs)
    with pytest.raises((TypeError, ValueError)):
        make_kill_zone_id(**base)  # type: ignore[arg-type]


def test_case_37_context_identity_is_field_sensitive_and_version_bound() -> None:
    base = _context_id()
    normalized_version = _context_id(
        timezone_data_version=f" {TIMEZONE_DATA_VERSION.lower()} ",
    )
    assert normalized_version == base
    assert _context_id(instrument="SI") != base
    assert _context_id(timeframe="M1") != base
    assert _context_id(calendar_version="CME-SYNTHETIC-2") != base
    assert _context_id(index=2) != base
    assert _context_id(timestamp=_utc(2026, 1, 5, 2, 0, 1)) != base
    assert _context_id(
        session_status=KillZoneSessionStatus.EARLY_CLOSE
    ) != base
    assert _context_id(
        zone=KillZoneName.NEW_YORK_AM,
        timestamp=_utc(2026, 1, 5, 7),
    ) != base
    assert _context_id(
        zone=KillZoneName.NEW_YORK_AM,
        session_status=None,
        quality=KillZoneQuality.CALENDAR_UNVERIFIED,
        timestamp=_utc(2026, 1, 5, 7),
    ) != base
    for missing in (
        {"observation_index": None},
        {"observation_timestamp": None},
        {"trade_date": None},
        {"quality": None},
    ):
        with pytest.raises((TypeError, ValueError)):
            make_kill_zone_id(
                identity_kind="CONTEXT",
                instrument="GC",
                timeframe="M5",
                calendar_version=CALENDAR_VERSION,
                timezone_name=KILL_ZONE_TIMEZONE,
                timezone_data_version=TIMEZONE_DATA_VERSION,
                observation_index=missing.get("observation_index", 1),
                observation_timestamp=missing.get(
                    "observation_timestamp",
                    _utc(2026, 1, 5, 2),
                ),
                trade_date=missing.get("trade_date", date(2026, 1, 5)),
                zone=KillZoneName.LONDON,
                session_status=KillZoneSessionStatus.OPEN,
                quality=missing.get("quality", KillZoneQuality.VERIFIED),
            )


# Logical case 38.
@pytest.mark.parametrize("context_ids", [(), ("bad",), ("a" * 64, "a" * 64), ["a" * 64]])
def test_case_38_snapshot_identity_schema_is_exhaustive(context_ids: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_kill_zone_id(
            identity_kind="SNAPSHOT",
            instrument="GC",
            timeframe="M5",
            calendar_version=CALENDAR_VERSION,
            timezone_name=KILL_ZONE_TIMEZONE,
            timezone_data_version=TIMEZONE_DATA_VERSION,
            effective_index=1,
            effective_timestamp=_utc(2026, 1, 5, 2),
            context_ids=context_ids,  # type: ignore[arg-type]
        )


def test_case_38_snapshot_identity_is_ordered_and_field_sensitive() -> None:
    first = _context_id()
    second = _context_id(
        index=2,
        timestamp=_utc(2026, 1, 5, 7),
        zone=KillZoneName.NEW_YORK_AM,
    )
    base = _snapshot_id(context_ids=(first, second))
    assert _snapshot_id(context_ids=(second, first)) != base
    assert _snapshot_id(instrument="SI", context_ids=(first, second)) != base
    assert _snapshot_id(timeframe="M1", context_ids=(first, second)) != base
    assert _snapshot_id(
        calendar_version="CME-SYNTHETIC-2",
        context_ids=(first, second),
    ) != base
    assert _snapshot_id(effective_index=2, context_ids=(first, second)) != base
    assert _snapshot_id(
        effective_timestamp=_utc(2026, 1, 5, 2, 0, 1),
        context_ids=(first, second),
    ) != base
    assert _snapshot_id(context_ids=(first,)) != base
    for missing_name in ("effective_index", "effective_timestamp"):
        kwargs = {
            "identity_kind": "SNAPSHOT",
            "instrument": "GC",
            "timeframe": "M5",
            "calendar_version": CALENDAR_VERSION,
            "timezone_name": KILL_ZONE_TIMEZONE,
            "timezone_data_version": TIMEZONE_DATA_VERSION,
            "effective_index": 1,
            "effective_timestamp": _utc(2026, 1, 5, 2),
            "context_ids": (first,),
            missing_name: None,
        }
        with pytest.raises((TypeError, ValueError)):
            make_kill_zone_id(**kwargs)  # type: ignore[arg-type]
    for forbidden_name, forbidden_value in (
        ("observation_index", 1),
        ("observation_timestamp", _utc(2026, 1, 5, 2)),
        ("trade_date", date(2026, 1, 5)),
        ("zone", KillZoneName.LONDON),
        ("session_status", KillZoneSessionStatus.OPEN),
        ("quality", KillZoneQuality.VERIFIED),
    ):
        kwargs = {
            "identity_kind": "SNAPSHOT",
            "instrument": "GC",
            "timeframe": "M5",
            "calendar_version": CALENDAR_VERSION,
            "timezone_name": KILL_ZONE_TIMEZONE,
            "timezone_data_version": TIMEZONE_DATA_VERSION,
            "effective_index": 1,
            "effective_timestamp": _utc(2026, 1, 5, 2),
            "context_ids": (first,),
            forbidden_name: forbidden_value,
        }
        with pytest.raises((TypeError, ValueError)):
            make_kill_zone_id(**kwargs)  # type: ignore[arg-type]


# Logical case 39.
@pytest.mark.parametrize(
    "kwargs",
    [
        {"identity_kind": "OTHER"},
        {"observation_index": True},
        {"observation_timestamp": datetime(2026, 1, 5, 2)},
        {"trade_date": datetime(2026, 1, 5)},
        {"zone": "LONDON"},
        {"quality": "VERIFIED"},
    ],
)
def test_case_39_builder_contains_malformed_input_exceptions(kwargs: dict[str, object]) -> None:
    base: dict[str, object] = {
        "identity_kind": "CONTEXT",
        "instrument": "GC",
        "timeframe": "M5",
        "calendar_version": CALENDAR_VERSION,
        "timezone_name": KILL_ZONE_TIMEZONE,
        "timezone_data_version": TIMEZONE_DATA_VERSION,
        "observation_index": 1,
        "observation_timestamp": _utc(2026, 1, 5, 2),
        "trade_date": date(2026, 1, 5),
        "zone": KillZoneName.LONDON,
        "session_status": KillZoneSessionStatus.OPEN,
        "quality": KillZoneQuality.VERIFIED,
    }
    base.update(kwargs)
    with pytest.raises((TypeError, ValueError)):
        make_kill_zone_id(**base)  # type: ignore[arg-type]


def test_case_39_builder_binds_runtime_timezone_version_and_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    normalized = f" {TIMEZONE_DATA_VERSION.lower()} "
    assert _context_id(timezone_data_version=normalized) == _context_id()
    assert _snapshot_id(timezone_data_version=normalized) == _snapshot_id()
    with pytest.raises((TypeError, ValueError)):
        _context_id(timezone_data_version="WRONG-VERSION")
    with pytest.raises((TypeError, ValueError)):
        _snapshot_id(timezone_data_version="WRONG-VERSION")
    with pytest.raises((TypeError, ValueError)):
        make_kill_zone_id(
            identity_kind="SNAPSHOT",
            instrument="GC",
            timeframe="M5",
            calendar_version=CALENDAR_VERSION,
            timezone_name="UTC",
            timezone_data_version=TIMEZONE_DATA_VERSION,
            effective_index=1,
            effective_timestamp=_utc(2026, 1, 5, 2),
            context_ids=(_context_id(),),
        )

    required = {
        "identity_kind": "CONTEXT",
        "instrument": "GC",
        "timeframe": "M5",
        "calendar_version": CALENDAR_VERSION,
        "timezone_name": KILL_ZONE_TIMEZONE,
        "timezone_data_version": TIMEZONE_DATA_VERSION,
        "observation_index": 1,
        "observation_timestamp": _utc(2026, 1, 5, 2),
        "trade_date": date(2026, 1, 5),
        "zone": KillZoneName.LONDON,
        "session_status": KillZoneSessionStatus.OPEN,
        "quality": KillZoneQuality.VERIFIED,
    }
    for name in (
        "identity_kind",
        "instrument",
        "timeframe",
        "calendar_version",
        "timezone_name",
        "timezone_data_version",
    ):
        incomplete = dict(required)
        incomplete.pop(name)
        with pytest.raises(TypeError):
            make_kill_zone_id(**incomplete)  # type: ignore[arg-type]

    monkeypatch.setattr(kill_zones, "_runtime_timezone_data_version", lambda: None)
    with pytest.raises((TypeError, ValueError)):
        _context_id()
    with pytest.raises((TypeError, ValueError)):
        _snapshot_id()

    monkeypatch.undo()
    monkeypatch.setattr(kill_zones, "_load_timezone", lambda: None)
    with pytest.raises((TypeError, ValueError)):
        _context_id()
    with pytest.raises((TypeError, ValueError)):
        _snapshot_id()


# Logical case 40.
def test_case_40_exact_public_api_dataclasses_enums_and_exports() -> None:
    analyzer_signature = inspect.signature(analyze_kill_zones)
    builder_signature = inspect.signature(make_kill_zone_id)
    assert tuple(analyzer_signature.parameters) == (
        "instrument",
        "timeframe",
        "observations",
        "calendar_entries",
        "calendar_version",
        "timezone_data_version",
    )
    assert tuple(builder_signature.parameters) == (
        "identity_kind",
        "instrument",
        "timeframe",
        "calendar_version",
        "timezone_name",
        "timezone_data_version",
        "observation_index",
        "observation_timestamp",
        "trade_date",
        "zone",
        "session_status",
        "quality",
        "effective_index",
        "effective_timestamp",
        "context_ids",
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in analyzer_signature.parameters.values()
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in builder_signature.parameters.values()
    )
    assert all(
        item.default is inspect.Parameter.empty
        for item in analyzer_signature.parameters.values()
    )
    required_builder = {
        "identity_kind",
        "instrument",
        "timeframe",
        "calendar_version",
        "timezone_name",
        "timezone_data_version",
    }
    assert all(
        parameter.default is inspect.Parameter.empty
        for name, parameter in builder_signature.parameters.items()
        if name in required_builder
    )
    assert all(
        parameter.default is None
        for name, parameter in builder_signature.parameters.items()
        if name not in required_builder and name != "context_ids"
    )
    assert builder_signature.parameters["context_ids"].default == ()

    expected_fields = {
        KillZoneObservation: {
            "index": int,
            "timestamp": datetime,
            "is_closed": bool,
        },
        KillZoneCalendarEntry: {
            "calendar_version": str,
            "trade_date": date,
            "session_status": KillZoneSessionStatus,
            "session_open_timestamp": datetime | None,
            "session_close_timestamp": datetime | None,
        },
        KillZoneContext: {
            "context_id": str,
            "observation_index": int,
            "observation_timestamp": datetime,
            "trade_date": date,
            "zone": KillZoneName | None,
            "session_status": KillZoneSessionStatus | None,
            "quality": KillZoneQuality,
            "calendar_version": str,
            "timezone_name": str,
            "timezone_data_version": str,
        },
        KillZoneSnapshot: {
            "snapshot_id": str,
            "index": int,
            "timestamp": datetime,
            "context_ids": tuple[str, ...],
        },
        KillZoneResult: {
            "status": SMCV2PrimitiveStatus,
            "contexts": tuple[KillZoneContext, ...],
            "snapshots": tuple[KillZoneSnapshot, ...],
            "reasons": tuple[str, ...],
            "blocking_reasons": tuple[str, ...],
        },
    }
    for data_class, expected in expected_fields.items():
        assert data_class.__dataclass_params__.frozen is True
        assert tuple(item.name for item in fields(data_class)) == tuple(expected)
        assert get_type_hints(data_class) == expected
    for data_class in (
        KillZoneObservation,
        KillZoneCalendarEntry,
        KillZoneContext,
        KillZoneSnapshot,
    ):
        assert all(item.default is MISSING for item in fields(data_class))
    result_fields = fields(KillZoneResult)
    assert result_fields[0].default is MISSING
    assert tuple(item.default for item in result_fields[1:]) == ((), (), (), ())

    frozen_observation = _observation(1, _utc(2026, 1, 5, 2))
    with pytest.raises(FrozenInstanceError):
        frozen_observation.index = 2  # type: ignore[misc]

    assert tuple(item.value for item in KillZoneName) == (
        "ASIA",
        "LONDON",
        "NEW_YORK_AM",
        "NEW_YORK_PM",
    )
    assert tuple(item.value for item in KillZoneSessionStatus) == (
        "OPEN",
        "EARLY_CLOSE",
        "SESSION_CLOSED",
    )
    assert tuple(item.value for item in KillZoneQuality) == (
        "VERIFIED",
        "CALENDAR_UNVERIFIED",
    )
    assert KILL_ZONE_DETECTOR_VERSION == "SMC-V2-KILL-ZONE-1"
    assert KILL_ZONE_TIMEZONE == "America/New_York"
    assert tuple(kill_zones.__all__) == (
        "KILL_ZONE_DETECTOR_VERSION",
        "KILL_ZONE_TIMEZONE",
        "KillZoneName",
        "KillZoneSessionStatus",
        "KillZoneQuality",
        "KillZoneObservation",
        "KillZoneCalendarEntry",
        "KillZoneContext",
        "KillZoneSnapshot",
        "KillZoneResult",
        "make_kill_zone_id",
        "analyze_kill_zones",
    )


# Logical case 41.
def test_case_41_repeatability_across_quality_states() -> None:
    observation = _observation(1, _utc(2026, 1, 5, 7))
    variants = (
        (),
        (_entry(date(2026, 1, 5)),),
        (_entry(date(2026, 1, 5), status=KillZoneSessionStatus.SESSION_CLOSED),),
        (_entry(date(2026, 1, 5), status=KillZoneSessionStatus.EARLY_CLOSE),),
    )
    for entries in variants:
        assert _analyze((observation,), entries) == _analyze((observation,), entries)


# Logical case 42.
def test_case_42_strictly_later_complete_append_preserves_prefix() -> None:
    entry = _entry(date(2026, 1, 5))
    later_entry = _entry(date(2026, 1, 6))
    first = _observation(1, _utc(2026, 1, 5, 2))
    second = _observation(2, _utc(2026, 1, 5, 7))
    prefix = _analyze((first,), (entry,))
    extended = _analyze((first, second), (entry,))
    assert extended.contexts[:1] == prefix.contexts
    assert extended.snapshots[:1] == prefix.snapshots
    calendar_extended = _analyze((first,), (entry, later_entry))
    assert calendar_extended.contexts == prefix.contexts
    assert calendar_extended.snapshots == prefix.snapshots
    next_day = _observation(3, _utc(2026, 1, 6, 2))
    fully_extended = _analyze(
        (first, second, next_day),
        (entry, later_entry),
    )
    assert fully_extended.contexts[:1] == prefix.contexts
    assert fully_extended.snapshots[:1] == prefix.snapshots
    duplicate = _analyze((first, first), (entry,))
    assert duplicate.status is SMCV2PrimitiveStatus.INVALID
    reordered_calendar = _analyze((first,), (later_entry, entry))
    assert reordered_calendar.status is SMCV2PrimitiveStatus.INVALID
    version_mutation = _analyze(
        (first,),
        (replace(entry, calendar_version="CME-SYNTHETIC-2"),),
    )
    assert version_mutation.status is SMCV2PrimitiveStatus.INVALID
    repaired = _analyze((first,), (entry,))
    unverified = _analyze((first,), ())
    assert repaired.contexts[0].context_id != unverified.contexts[0].context_id


# Logical case 43.
def test_case_43_context_and_complete_history_snapshot_promote_atomically() -> None:
    entry = _entry(date(2026, 1, 5))
    observations = (
        _observation(1, _utc(2026, 1, 5, 2)),
        _observation(2, _utc(2026, 1, 5, 7)),
    )
    result = _analyze(observations, (entry,))
    assert len(result.contexts) == len(result.snapshots) == 2
    assert result.snapshots[0].context_ids == (result.contexts[0].context_id,)
    assert result.snapshots[1].context_ids == tuple(
        item.context_id for item in result.contexts
    )
    assert all(not hasattr(item, "transition_id") for item in result.snapshots)


# Logical case 44.
def test_case_44_module_is_standalone_and_has_no_forbidden_dependency() -> None:
    module_path = Path(__file__).parents[1] / "smc" / "kill_zones.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert imported_roots.isdisjoint(
        {
            "requests",
            "urllib",
            "pandas",
            "broker",
            "risk",
            "orderflow",
            "pathlib",
        }
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "open"
        for node in ast.walk(tree)
    )
