from __future__ import annotations

import ast
from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
import importlib.metadata
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest
from zoneinfo import ZoneInfo

import orderflow.volume_profile as volume_profile
from orderflow.footprint import FootprintCandle
from orderflow.volume_profile import (
    COMPLETED_SESSION_VOLUME_PROFILE_SOURCE,
    COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
    COMPLETED_SESSION_VOLUME_PROFILE_VERSION,
    CompletedSessionVolumeAtPrice,
    CompletedSessionVolumeBar,
    CompletedSessionVolumeLevel,
    CompletedSessionVolumeProfile,
    CompletedSessionVolumeProfileCompleteness,
    CompletedSessionVolumeProfileDataQuality,
    CompletedSessionVolumeProfileResult,
    CompletedSessionVolumeProfileSnapshot,
    analyze_completed_session_volume_profiles,
    make_volume_profile_id,
)
from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus
from smc.smc_v2_primitives import SMCV2PrimitiveStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
CALENDAR_VERSION = "CME-SYNTHETIC-1"
TZDATA_VERSION = importlib.metadata.version("tzdata")
TRADE_DATE = date(2026, 1, 6)


def _session_bounds(trade_date: date = TRADE_DATE) -> tuple[datetime, datetime]:
    opening = datetime.combine(
        trade_date - timedelta(days=1), time(18), tzinfo=NY
    ).astimezone(UTC)
    closing = datetime.combine(trade_date, time(17), tzinfo=NY).astimezone(UTC)
    return opening, closing


def _entry(
    trade_date: date = TRADE_DATE,
    *,
    status: KillZoneSessionStatus = KillZoneSessionStatus.OPEN,
    opening: datetime | None = None,
    closing: datetime | None = None,
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
    expected_open, expected_close = _session_bounds(trade_date)
    return KillZoneCalendarEntry(
        calendar_version=calendar_version,
        trade_date=trade_date,
        session_status=status,
        session_open_timestamp=opening or expected_open,
        session_close_timestamp=closing or expected_close,
    )


def _level(
    price_tick: int,
    bid_volume: int,
    ask_volume: int,
    *,
    reported_total_volume: int | None = None,
) -> CompletedSessionVolumeLevel:
    return CompletedSessionVolumeLevel(
        price_tick=price_tick,
        bid_volume=bid_volume,
        ask_volume=ask_volume,
        reported_total_volume=(
            bid_volume + ask_volume
            if reported_total_volume is None
            else reported_total_volume
        ),
    )


def _bar(
    *,
    index: int = 0,
    opening: datetime | None = None,
    closing: datetime | None = None,
    levels: tuple[CompletedSessionVolumeLevel, ...] | None = None,
    source_format: str = COMPLETED_SESSION_VOLUME_PROFILE_SOURCE,
    is_closed: bool = True,
    reported_total_volume: int | None = None,
    open_tick: int | None = None,
    high_tick: int | None = None,
    low_tick: int | None = None,
    close_tick: int | None = None,
) -> CompletedSessionVolumeBar:
    session_open, session_close = _session_bounds()
    selected_levels = levels or (_level(100, 2, 3),)
    prices = [level.price_tick for level in selected_levels]
    return CompletedSessionVolumeBar(
        index=index,
        open_timestamp=opening or session_open,
        close_timestamp=closing or session_close,
        open_tick=prices[0] if open_tick is None else open_tick,
        high_tick=max(prices) if high_tick is None else high_tick,
        low_tick=min(prices) if low_tick is None else low_tick,
        close_tick=prices[-1] if close_tick is None else close_tick,
        is_closed=is_closed,
        source_format=source_format,
        reported_total_volume=(
            sum(level.reported_total_volume for level in selected_levels)
            if reported_total_volume is None
            else reported_total_volume
        ),
        levels=selected_levels,
    )


def _hourly_bars(
    trade_date: date = TRADE_DATE,
    *,
    missing: frozenset[int] = frozenset(),
) -> tuple[CompletedSessionVolumeBar, ...]:
    opening, closing = _session_bounds(trade_date)
    count = int((closing - opening).total_seconds() // 3600)
    result: list[CompletedSessionVolumeBar] = []
    for position in range(count):
        if position in missing:
            continue
        start = opening + timedelta(hours=position)
        finish = start + timedelta(hours=1)
        tick = 100 + (position % 3)
        result.append(
            _bar(
                index=position,
                opening=start,
                closing=finish,
                levels=(_level(tick, position + 1, 1),),
            )
        )
    return tuple(result)


def _analyze(
    *,
    trade_dates: tuple[date, ...] | None = (TRADE_DATE,),
    bars: tuple[CompletedSessionVolumeBar, ...] | None = None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None = None,
    bar_duration_seconds: int | None = None,
    calendar_version: str = CALENDAR_VERSION,
    timezone_data_version: str = TZDATA_VERSION,
    as_of_timestamp: datetime | None = None,
    instrument: str = "GC",
    timeframe: str = "M5",
) -> CompletedSessionVolumeProfileResult:
    session_open, session_close = _session_bounds()
    selected_bars = (_bar(),) if bars is None else bars
    selected_calendar = (_entry(),) if calendar_entries is None else calendar_entries
    return analyze_completed_session_volume_profiles(
        instrument=instrument,
        timeframe=timeframe,
        bar_duration_seconds=(
            int((session_close - session_open).total_seconds())
            if bar_duration_seconds is None
            else bar_duration_seconds
        ),
        trade_dates=trade_dates,
        bars=selected_bars,
        calendar_entries=selected_calendar,
        calendar_version=calendar_version,
        timezone_data_version=timezone_data_version,
        as_of_timestamp=as_of_timestamp or session_close,
    )


def _profile_kwargs(profile: CompletedSessionVolumeProfile) -> dict[str, object]:
    return {
        "identity_kind": "PROFILE",
        "instrument": "GC",
        "timeframe": "M5",
        "calendar_version": profile.calendar_version,
        "timezone_name": profile.timezone_name,
        "timezone_data_version": profile.timezone_data_version,
        "trade_date": profile.trade_date,
        "session_open_timestamp": profile.session_open_timestamp,
        "session_close_timestamp": profile.session_close_timestamp,
        "first_known_timestamp": profile.first_known_timestamp,
        "source_format": profile.source_format,
        "bar_duration_seconds": profile.bar_duration_seconds,
        "source_bar_indices": profile.source_bar_indices,
        "source_bar_open_timestamps": profile.source_bar_open_timestamps,
        "source_bar_close_timestamps": profile.source_bar_close_timestamps,
        "source_bar_ohlc_ticks": profile.source_bar_ohlc_ticks,
        "price_levels": profile.price_levels,
        "poc_tick": profile.poc_tick,
        "poc_tied_ticks": profile.poc_tied_ticks,
        "volume_weighted_mean_numerator": profile.volume_weighted_mean_numerator,
        "volume_weighted_mean_denominator": profile.volume_weighted_mean_denominator,
        "val_tick": profile.val_tick,
        "vah_tick": profile.vah_tick,
        "total_volume": profile.total_volume,
        "covered_volume": profile.covered_volume,
        "covered_percentage_numerator": profile.covered_percentage_numerator,
        "covered_percentage_denominator": profile.covered_percentage_denominator,
        "completeness": profile.completeness,
        "data_quality": profile.data_quality,
    }


def _valid_profile() -> CompletedSessionVolumeProfile:
    result = _analyze()
    assert result.status is SMCV2PrimitiveStatus.VALID
    return result.profiles[0]


# Logical case 1.
def test_case_01_constants_are_exact() -> None:
    assert COMPLETED_SESSION_VOLUME_PROFILE_VERSION == (
        "SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-1"
    )
    assert COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE == "America/New_York"
    assert COMPLETED_SESSION_VOLUME_PROFILE_SOURCE == "ACSIL_FULL_FOOTPRINT"


# Logical case 2.
def test_case_02_fully_closed_integer_happy_path_and_frozen_inputs() -> None:
    result = _analyze()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.profiles) == len(result.snapshots) == 1
    with pytest.raises(FrozenInstanceError):
        result.profiles[0].poc_tick = 1  # type: ignore[misc]


# Logical case 3.
@pytest.mark.parametrize(
    ("field", "value"),
    [("price_tick", True), ("bid_volume", True), ("ask_volume", 1.5), ("index", True)],
)
def test_case_03_exact_types_and_tuple_contract(field: str, value: object) -> None:
    bar = _bar()
    if field == "index":
        bad = replace(bar, index=value)  # type: ignore[arg-type]
    else:
        bad_level = replace(bar.levels[0], **{field: value})
        bad = replace(bar, levels=(bad_level,))
    assert _analyze(bars=(bad,)).status is SMCV2PrimitiveStatus.INVALID
    direct = analyze_completed_session_volume_profiles(
        instrument="GC",
        timeframe="M5",
        bar_duration_seconds=82800,
        trade_dates=(TRADE_DATE,),
        bars=[bar],  # type: ignore[arg-type]
        calendar_entries=(_entry(),),
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=_session_bounds()[1],
    )
    assert direct.status is SMCV2PrimitiveStatus.INVALID


# Logical case 4.
@pytest.mark.parametrize("value", [-1, 1.25, float("nan"), float("inf"), "4"])
def test_case_04_malformed_volume_fails_closed(value: object) -> None:
    bad = replace(_bar().levels[0], bid_volume=value)  # type: ignore[arg-type]
    result = _analyze(bars=(replace(_bar(), levels=(bad,)),))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.profiles == result.snapshots == ()


# Logical case 5.
def test_case_05_level_conservation() -> None:
    bad = _level(100, 2, 3, reported_total_volume=6)
    assert _analyze(bars=(_bar(levels=(bad,), reported_total_volume=6),)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 6.
def test_case_06_bar_conservation() -> None:
    assert _analyze(bars=(_bar(reported_total_volume=99),)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 7.
def test_case_07_level_order_duplicates_and_cross_bar_aggregation() -> None:
    reversed_levels = (_level(101, 1, 0), _level(100, 1, 0))
    duplicate_levels = (_level(100, 1, 0), _level(100, 2, 0))
    assert _analyze(bars=(_bar(levels=reversed_levels),)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(bars=(_bar(levels=duplicate_levels),)).status is SMCV2PrimitiveStatus.INVALID
    result = _analyze(bars=_hourly_bars(), bar_duration_seconds=3600)
    aggregate = {level.price_tick: level.total_volume for level in result.profiles[0].price_levels}
    assert aggregate[100] > 0


# Logical case 8.
@pytest.mark.parametrize(
    "bar",
    [
        replace(_bar(), open_timestamp=datetime(2026, 1, 5, 23)),
        replace(_bar(), is_closed=False),
        _bar(open_tick=99),
        _bar(low_tick=101, high_tick=100),
    ],
)
def test_case_08_bar_timestamp_ohlc_duration_and_closed_rules(bar: CompletedSessionVolumeBar) -> None:
    assert _analyze(bars=(bar,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 9.
def test_case_09_bar_order_overlap_and_no_silent_sort() -> None:
    first, second = _hourly_bars()[:2]
    assert _analyze(bars=(second, first), bar_duration_seconds=3600).status is SMCV2PrimitiveStatus.INVALID
    overlapping = replace(second, open_timestamp=first.open_timestamp + timedelta(minutes=30))
    assert _analyze(bars=(first, overlapping), bar_duration_seconds=3600).status is SMCV2PrimitiveStatus.INVALID


# Logical case 10.
def test_case_10_full_footprint_acceptance_and_bar_summary_rejection() -> None:
    assert _analyze().status is SMCV2PrimitiveStatus.VALID
    rejected = replace(_bar(), source_format="BAR_SUMMARY")
    assert _analyze(bars=(rejected,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 11.
def test_case_11_unknown_mixed_and_legacy_sources_are_invalid() -> None:
    assert _analyze(bars=(replace(_bar(), source_format="OTHER"),)).status is SMCV2PrimitiveStatus.INVALID
    legacy = FootprintCandle(time=None, open=1, high=1, low=1, close=1)
    result = analyze_completed_session_volume_profiles(
        instrument="GC", timeframe="M5", bar_duration_seconds=82800,
        trade_dates=(TRADE_DATE,), bars=(legacy,),  # type: ignore[arg-type]
        calendar_entries=(_entry(),), calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION, as_of_timestamp=_session_bounds()[1],
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


# Logical case 12.
def test_case_12_equivalent_source_requires_new_version() -> None:
    assert _analyze(bars=(replace(_bar(), source_format="EQUIVALENT_FULL"),)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 13.
def test_case_13_timezone_name_and_runtime_availability(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = _valid_profile()
    kwargs = _profile_kwargs(profile)
    kwargs["timezone_name"] = "UTC"
    with pytest.raises(ValueError):
        make_volume_profile_id(**kwargs)
    monkeypatch.setattr(volume_profile, "_load_timezone", lambda: None)
    assert _analyze().status is SMCV2PrimitiveStatus.UNKNOWN


# Logical case 14.
def test_case_14_tzdata_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _analyze(timezone_data_version="mismatch").status is SMCV2PrimitiveStatus.INVALID
    monkeypatch.setattr(volume_profile, "_runtime_timezone_data_version", lambda: None)
    assert _analyze().status is SMCV2PrimitiveStatus.UNKNOWN


# Logical case 15.
def test_case_15_standard_session_boundaries() -> None:
    profile = _valid_profile()
    opening, closing = _session_bounds()
    assert profile.session_open_timestamp == opening
    assert profile.session_close_timestamp == closing
    assert profile.first_known_timestamp == closing


# Logical case 16.
def test_case_16_spring_forward_session_uses_iana_database() -> None:
    trade_date = date(2026, 3, 9)
    opening, closing = _session_bounds(trade_date)
    bar = _bar(index=0, opening=opening, closing=closing)
    result = _analyze(
        trade_dates=(trade_date,), bars=(bar,), calendar_entries=(_entry(trade_date),),
        bar_duration_seconds=int((closing-opening).total_seconds()), as_of_timestamp=closing,
    )
    assert result.status is SMCV2PrimitiveStatus.VALID


# Logical case 17.
def test_case_17_fall_back_session_is_repeatable() -> None:
    trade_date = date(2026, 11, 2)
    opening, closing = _session_bounds(trade_date)
    bar = _bar(index=0, opening=opening, closing=closing)
    kwargs = dict(
        trade_dates=(trade_date,), bars=(bar,), calendar_entries=(_entry(trade_date),),
        bar_duration_seconds=int((closing-opening).total_seconds()), as_of_timestamp=closing,
    )
    assert _analyze(**kwargs) == _analyze(**kwargs)


# Logical case 18.
def test_case_18_maintenance_and_boundary_straddle_rejection() -> None:
    opening, closing = _session_bounds()
    maintenance = _bar(opening=closing, closing=closing + timedelta(hours=1))
    straddle = _bar(opening=opening - timedelta(minutes=1), closing=closing)
    assert _analyze(bars=(maintenance,)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(bars=(straddle,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 19.
def test_case_19_weekday_weekend_and_contradictory_weekend_open() -> None:
    saturday = date(2026, 1, 10)
    closed = _analyze(trade_dates=(saturday,), bars=(), calendar_entries=())
    assert closed.status is SMCV2PrimitiveStatus.NONE
    contradiction = _analyze(
        trade_dates=(saturday,), bars=(), calendar_entries=(_entry(saturday),)
    )
    assert contradiction.status is SMCV2PrimitiveStatus.INVALID


# Logical case 20.
def test_case_20_open_calendar_and_unrequested_entry() -> None:
    assert _analyze().status is SMCV2PrimitiveStatus.VALID
    extra = _entry(date(2026, 1, 7))
    invalid = _analyze(calendar_entries=(_entry(), extra))
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    assert len(invalid.profiles) == len(invalid.snapshots) == 1
    empty_request = _analyze(trade_dates=(), bars=(), calendar_entries=(extra,))
    assert empty_request.status is SMCV2PrimitiveStatus.INVALID
    assert empty_request.reasons == ("UNREQUESTED_CALENDAR_ENTRY",)
    assert empty_request.profiles == empty_request.snapshots == ()

    _, close = _session_bounds()
    missing_bars = analyze_completed_session_volume_profiles(
        instrument="GC",
        timeframe="M5",
        bar_duration_seconds=int(
            (close - _session_bounds()[0]).total_seconds()
        ),
        trade_dates=(),
        bars=None,
        calendar_entries=(_entry(),),
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=close,
    )
    assert missing_bars.status is SMCV2PrimitiveStatus.INVALID
    assert missing_bars.reasons == ("UNREQUESTED_CALENDAR_ENTRY",)
    assert missing_bars.profiles == missing_bars.snapshots == ()

    genuine_missing = analyze_completed_session_volume_profiles(
        instrument="GC",
        timeframe="M5",
        bar_duration_seconds=int(
            (close - _session_bounds()[0]).total_seconds()
        ),
        trade_dates=(),
        bars=None,
        calendar_entries=None,
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=close,
    )
    assert genuine_missing.status is SMCV2PrimitiveStatus.UNKNOWN
    assert genuine_missing.reasons == ("MISSING_TOP_LEVEL_CONTEXT",)
    assert genuine_missing.profiles == genuine_missing.snapshots == ()


# Logical case 21.
def test_case_21_early_close_rules() -> None:
    opening, standard_close = _session_bounds()
    early_close = standard_close - timedelta(hours=4)
    entry = _entry(status=KillZoneSessionStatus.EARLY_CLOSE, closing=early_close)
    bar = _bar(opening=opening, closing=early_close)
    result = _analyze(
        bars=(bar,), calendar_entries=(entry,),
        bar_duration_seconds=int((early_close-opening).total_seconds()),
        as_of_timestamp=early_close,
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    equal_standard = _entry(status=KillZoneSessionStatus.EARLY_CLOSE)
    assert _analyze(calendar_entries=(equal_standard,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 22.
def test_case_22_session_closed_requires_none_timestamps() -> None:
    result = _analyze(bars=(), calendar_entries=(_entry(status=KillZoneSessionStatus.SESSION_CLOSED),))
    assert result.status is SMCV2PrimitiveStatus.NONE
    malformed = replace(
        _entry(status=KillZoneSessionStatus.SESSION_CLOSED),
        session_open_timestamp=_session_bounds()[0],
    )
    assert _analyze(bars=(), calendar_entries=(malformed,)).status is SMCV2PrimitiveStatus.INVALID


# Logical case 23.
def test_case_23_missing_calendar_is_unknown_after_counterpart_validation() -> None:
    result = analyze_completed_session_volume_profiles(
        instrument="GC", timeframe="M5", bar_duration_seconds=82800,
        trade_dates=(TRADE_DATE,), bars=(_bar(),), calendar_entries=None,
        calendar_version=CALENDAR_VERSION, timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=_session_bounds()[1],
    )
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    bad_bar = replace(_bar(), reported_total_volume=999)
    invalid = analyze_completed_session_volume_profiles(
        instrument="GC", timeframe="M5", bar_duration_seconds=82800,
        trade_dates=(TRADE_DATE,), bars=(bad_bar,), calendar_entries=None,
        calendar_version=CALENDAR_VERSION, timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=_session_bounds()[1],
    )
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    empty_calendar_invalid = _analyze(
        bars=(bad_bar,),
        calendar_entries=(),
    )
    assert empty_calendar_invalid.status is SMCV2PrimitiveStatus.INVALID
    missing_dates_invalid_bar = analyze_completed_session_volume_profiles(
        instrument="GC", timeframe="M5", bar_duration_seconds=82800,
        trade_dates=None, bars=(bad_bar,), calendar_entries=(_entry(),),
        calendar_version=CALENDAR_VERSION, timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=_session_bounds()[1],
    )
    assert missing_dates_invalid_bar.status is SMCV2PrimitiveStatus.INVALID
    malformed_entry = replace(_entry(), session_status="OPEN")  # type: ignore[arg-type]
    missing_bars_invalid_calendar = analyze_completed_session_volume_profiles(
        instrument="GC", timeframe="M5", bar_duration_seconds=82800,
        trade_dates=(TRADE_DATE,), bars=None, calendar_entries=(malformed_entry,),
        calendar_version=CALENDAR_VERSION, timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=_session_bounds()[1],
    )
    assert missing_bars_invalid_calendar.status is SMCV2PrimitiveStatus.INVALID


# Logical case 24.
def test_case_24_calendar_duplicate_fork_version_and_order() -> None:
    assert _analyze(calendar_entries=(_entry(), _entry())).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(calendar_entries=(_entry(calendar_version="bad"),)).status is SMCV2PrimitiveStatus.INVALID
    later = _entry(date(2026, 1, 7))
    assert _analyze(trade_dates=(TRADE_DATE, date(2026,1,7)), calendar_entries=(later, _entry()), bars=()).status is SMCV2PrimitiveStatus.INVALID


# Logical case 25.
def test_case_25_before_close_is_none_without_developing_profile() -> None:
    result = _analyze(as_of_timestamp=_session_bounds()[1] - timedelta(microseconds=1))
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.profiles == result.snapshots == ()


# Logical case 26.
@pytest.mark.parametrize("offset", [timedelta(0), timedelta(hours=2)])
def test_case_26_at_or_after_close_is_completed(offset: timedelta) -> None:
    assert _analyze(as_of_timestamp=_session_bounds()[1] + offset).status is SMCV2PrimitiveStatus.VALID


# Logical case 27.
def test_case_27_bar_unique_session_attribution() -> None:
    opening, closing = _session_bounds()
    outside = _bar(opening=opening - timedelta(days=1), closing=closing - timedelta(days=1))
    assert _analyze(bars=(outside,)).status is SMCV2PrimitiveStatus.INVALID
    empty_request = _analyze(trade_dates=(), bars=(_bar(),), calendar_entries=())
    assert empty_request.status is SMCV2PrimitiveStatus.INVALID
    assert empty_request.reasons == ("UNREQUESTED_BAR",)
    assert empty_request.profiles == empty_request.snapshots == ()
    no_evidence = _analyze(trade_dates=(), bars=(), calendar_entries=())
    assert no_evidence.status is SMCV2PrimitiveStatus.NONE
    assert no_evidence.reasons == ("NO_REQUESTED_SESSIONS",)

    missing_calendar = analyze_completed_session_volume_profiles(
        instrument="GC",
        timeframe="M5",
        bar_duration_seconds=int((closing - opening).total_seconds()),
        trade_dates=(),
        bars=(_bar(),),
        calendar_entries=None,
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
        as_of_timestamp=closing,
    )
    assert missing_calendar.status is SMCV2PrimitiveStatus.INVALID
    assert missing_calendar.reasons == ("UNREQUESTED_BAR",)
    assert missing_calendar.profiles == missing_calendar.snapshots == ()


# Logical case 28.
def test_case_28_exact_grid_complete_and_off_grid_rejection() -> None:
    result = _analyze(bars=_hourly_bars(), bar_duration_seconds=3600)
    assert result.profiles[0].completeness is CompletedSessionVolumeProfileCompleteness.COMPLETE
    assert result.profiles[0].data_quality is CompletedSessionVolumeProfileDataQuality.QUALIFIED
    first = _hourly_bars()[0]
    off_grid = replace(first, open_timestamp=first.open_timestamp + timedelta(minutes=1), close_timestamp=first.close_timestamp + timedelta(minutes=1))
    assert _analyze(bars=(off_grid,), bar_duration_seconds=3600).status is SMCV2PrimitiveStatus.INVALID
    opening, _ = _session_bounds()
    nondividing = _bar(opening=opening, closing=opening + timedelta(seconds=1000))
    assert _analyze(bars=(nondividing,), bar_duration_seconds=1000).status is SMCV2PrimitiveStatus.INVALID


# Logical case 29.
def test_case_29_missing_grid_bar_is_reportable_unqualified() -> None:
    result = _analyze(bars=_hourly_bars(missing=frozenset({5})), bar_duration_seconds=3600)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.profiles[0].completeness is CompletedSessionVolumeProfileCompleteness.INCOMPLETE
    assert result.profiles[0].data_quality is CompletedSessionVolumeProfileDataQuality.UNQUALIFIED


# Logical case 30.
def test_case_30_empty_unknown_and_zero_volume_none() -> None:
    assert _analyze(bars=()).status is SMCV2PrimitiveStatus.UNKNOWN
    zero = _bar(levels=(_level(100, 0, 0),), reported_total_volume=0)
    assert _analyze(bars=(zero,)).status is SMCV2PrimitiveStatus.NONE


# Logical case 31.
def test_case_31_exact_aggregation_and_profile_conservation() -> None:
    result = _analyze(bars=_hourly_bars(), bar_duration_seconds=3600)
    profile = result.profiles[0]
    assert profile.total_volume == sum(level.total_volume for level in profile.price_levels)
    assert profile.total_volume == sum(bar.reported_total_volume for bar in _hourly_bars())


# Logical case 32.
def test_case_32_unique_poc() -> None:
    levels = (_level(99, 1, 0), _level(100, 5, 0), _level(101, 2, 0))
    profile = _analyze(bars=(_bar(levels=levels),)).profiles[0]
    assert profile.poc_tick == 100
    assert profile.poc_tied_ticks == (100,)


# Logical case 33.
def test_case_33_poc_tie_uses_exact_weighted_mean_distance() -> None:
    levels = (_level(99, 5, 0), _level(102, 4, 0), _level(103, 5, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=103),)).profiles[0]
    assert profile.poc_tied_ticks == (99, 103)
    assert profile.poc_tick == 103


# Logical case 34.
def test_case_34_remaining_poc_tie_uses_lower_tick() -> None:
    levels = (_level(99, 5, 0), _level(101, 5, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=101),)).profiles[0]
    assert profile.poc_tied_ticks == (99, 101)
    assert profile.poc_tick == 99


# Logical case 35.
def test_case_35_arbitrary_magnitude_ticks_use_exact_rational_mean() -> None:
    base = 10**80
    levels = (_level(-base, 1, 0), _level(-base + 1, 3, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=-base, high_tick=-base+1),)).profiles[0]
    assert profile.volume_weighted_mean_denominator > 0
    assert profile.poc_tick == -base + 1


# Logical case 36.
def test_case_36_value_area_exact_threshold() -> None:
    levels = (_level(99, 2, 0), _level(100, 7, 0), _level(101, 1, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=101),)).profiles[0]
    assert (profile.val_tick, profile.vah_tick, profile.covered_volume) == (100, 100, 7)


# Logical case 37.
def test_case_37_value_area_chooses_greater_adjacent_volume() -> None:
    levels = (_level(99, 2, 0), _level(100, 4, 0), _level(101, 3, 0), _level(102, 1, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=102),)).profiles[0]
    assert profile.val_tick == 100
    assert profile.vah_tick == 101


# Logical case 38.
def test_case_38_value_area_tie_chooses_lower_side() -> None:
    levels = (_level(99, 3, 0), _level(100, 4, 0), _level(101, 3, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=101),)).profiles[0]
    assert (profile.val_tick, profile.vah_tick) == (99, 100)


# Logical case 39.
def test_case_39_sparse_ticks_are_zero_volume_adjacency() -> None:
    levels = (_level(100, 6, 0), _level(103, 4, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=100, high_tick=103),)).profiles[0]
    assert (profile.val_tick, profile.vah_tick) == (100, 103)


# Logical case 40.
def test_case_40_covered_fraction_is_reduced_and_may_overshoot() -> None:
    levels = (_level(99, 4, 0), _level(100, 5, 0), _level(101, 1, 0))
    profile = _analyze(bars=(_bar(levels=levels, low_tick=99, high_tick=101),)).profiles[0]
    assert profile.covered_volume == 9
    assert (profile.covered_percentage_numerator, profile.covered_percentage_denominator) == (9, 10)


# Logical case 41.
@pytest.mark.parametrize(
    "field",
    [
        "trade_date", "session_open_timestamp", "session_close_timestamp",
        "first_known_timestamp", "source_format", "bar_duration_seconds",
        "source_bar_indices", "source_bar_open_timestamps",
        "source_bar_close_timestamps", "source_bar_ohlc_ticks", "price_levels",
        "poc_tick", "poc_tied_ticks", "volume_weighted_mean_numerator",
        "volume_weighted_mean_denominator", "val_tick", "vah_tick", "total_volume",
        "covered_volume", "covered_percentage_numerator",
        "covered_percentage_denominator", "completeness", "data_quality",
    ],
)
def test_case_41_profile_identity_requires_every_profile_field(field: str) -> None:
    kwargs = _profile_kwargs(_valid_profile())
    value = kwargs[field]
    kwargs[field] = () if isinstance(value, tuple) else None
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)


@pytest.mark.parametrize(
    ("field", "value"),
    [("effective_timestamp", _session_bounds()[1]), ("profile_ids", ("0" * 64,))],
)
def test_case_41_profile_identity_forbids_snapshot_fields(field: str, value: object) -> None:
    kwargs = _profile_kwargs(_valid_profile())
    kwargs[field] = value
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)


def test_case_41_profile_identity_reconciles_trade_date_and_session_provenance() -> None:
    profile = _valid_profile()
    kwargs = _profile_kwargs(profile)
    kwargs["trade_date"] = date(2026, 1, 7)
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)

    kwargs = _profile_kwargs(profile)
    kwargs["session_open_timestamp"] = profile.session_open_timestamp + timedelta(hours=1)
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)

    opening, standard_close = _session_bounds()
    early_close = standard_close - timedelta(hours=4)
    entry = _entry(status=KillZoneSessionStatus.EARLY_CLOSE, closing=early_close)
    bar = _bar(opening=opening, closing=early_close)
    early = _analyze(
        bars=(bar,),
        calendar_entries=(entry,),
        bar_duration_seconds=int((early_close - opening).total_seconds()),
        as_of_timestamp=early_close,
    ).profiles[0]
    assert make_volume_profile_id(**_profile_kwargs(early)) == early.profile_id


def test_case_41_profile_identity_reconciles_price_levels_with_source_ohlc() -> None:
    kwargs = _profile_kwargs(_valid_profile())
    kwargs["source_bar_ohlc_ticks"] = ((0, 0, 0, 0),)
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)


# Logical case 42.
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("trade_date", TRADE_DATE),
        ("session_open_timestamp", _session_bounds()[0]),
        ("session_close_timestamp", _session_bounds()[1]),
        ("first_known_timestamp", _session_bounds()[1]),
        ("source_format", COMPLETED_SESSION_VOLUME_PROFILE_SOURCE),
        ("bar_duration_seconds", 1),
        ("source_bar_indices", (1,)),
        ("source_bar_open_timestamps", (_session_bounds()[0],)),
        ("source_bar_close_timestamps", (_session_bounds()[1],)),
        ("source_bar_ohlc_ticks", ((1, 1, 1, 1),)),
        ("price_levels", (CompletedSessionVolumeAtPrice(1, 1, 0, 1),)),
        ("poc_tick", 1),
        ("poc_tied_ticks", (1,)),
        ("volume_weighted_mean_numerator", 1),
        ("volume_weighted_mean_denominator", 1),
        ("val_tick", 1),
        ("vah_tick", 1),
        ("total_volume", 1),
        ("covered_volume", 1),
        ("covered_percentage_numerator", 1),
        ("covered_percentage_denominator", 1),
        ("completeness", CompletedSessionVolumeProfileCompleteness.COMPLETE),
        ("data_quality", CompletedSessionVolumeProfileDataQuality.QUALIFIED),
    ],
)
def test_case_42_snapshot_schema_forbids_profile_fields(field: str, value: object) -> None:
    profile = _valid_profile()
    kwargs: dict[str, object] = {
        "identity_kind": "SNAPSHOT", "instrument": "GC", "timeframe": "M5",
        "calendar_version": CALENDAR_VERSION,
        "timezone_name": COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
        "timezone_data_version": TZDATA_VERSION,
        "effective_timestamp": profile.first_known_timestamp,
        "profile_ids": (profile.profile_id,), field: value,
    }
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)


@pytest.mark.parametrize("missing", ["effective_timestamp", "profile_ids"])
def test_case_42_snapshot_requires_both_snapshot_fields(missing: str) -> None:
    profile = _valid_profile()
    kwargs: dict[str, object] = {
        "identity_kind": "SNAPSHOT", "instrument": "GC", "timeframe": "M5",
        "calendar_version": CALENDAR_VERSION,
        "timezone_name": COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
        "timezone_data_version": TZDATA_VERSION,
        "effective_timestamp": profile.first_known_timestamp,
        "profile_ids": (profile.profile_id,),
    }
    kwargs[missing] = None if missing == "effective_timestamp" else ()
    with pytest.raises((TypeError, ValueError)):
        make_volume_profile_id(**kwargs)


# Logical case 43.
def test_case_43_identity_normalization_utc_equivalence_and_repeatability() -> None:
    profile = _valid_profile()
    kwargs = _profile_kwargs(profile)
    assert make_volume_profile_id(**kwargs) == profile.profile_id
    kwargs["instrument"] = " gc "
    kwargs["timeframe"] = " m5 "
    assert make_volume_profile_id(**kwargs) == profile.profile_id
    kwargs["session_open_timestamp"] = profile.session_open_timestamp.astimezone(NY)
    assert make_volume_profile_id(**kwargs) == profile.profile_id


# Logical case 44.
def test_case_44_builder_signature_defaults_and_unknown_kind() -> None:
    signature = inspect.signature(make_volume_profile_id)
    assert tuple(signature.parameters) == (
        "identity_kind", "instrument", "timeframe", "calendar_version",
        "timezone_name", "timezone_data_version", "trade_date",
        "session_open_timestamp", "session_close_timestamp",
        "first_known_timestamp", "source_format", "bar_duration_seconds",
        "source_bar_indices", "source_bar_open_timestamps",
        "source_bar_close_timestamps", "source_bar_ohlc_ticks", "price_levels",
        "poc_tick", "poc_tied_ticks", "volume_weighted_mean_numerator",
        "volume_weighted_mean_denominator", "val_tick", "vah_tick", "total_volume",
        "covered_volume", "covered_percentage_numerator",
        "covered_percentage_denominator", "completeness", "data_quality",
        "effective_timestamp", "profile_ids",
    )
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in signature.parameters.values())
    required = tuple(signature.parameters)[:6]
    assert all(signature.parameters[name].default is inspect.Parameter.empty for name in required)
    tuple_defaults = {
        "source_bar_indices", "source_bar_open_timestamps",
        "source_bar_close_timestamps", "source_bar_ohlc_ticks", "price_levels",
        "poc_tied_ticks", "profile_ids",
    }
    for name, parameter in tuple(signature.parameters.items())[6:]:
        assert parameter.default == (() if name in tuple_defaults else None)
    with pytest.raises(ValueError):
        make_volume_profile_id(
            identity_kind="OTHER", instrument="GC", timeframe="M5",
            calendar_version=CALENDAR_VERSION,
            timezone_name=COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
            timezone_data_version=TZDATA_VERSION,
        )


# Logical case 45.
def test_case_45_analyzer_signature_and_public_dataclass_contracts() -> None:
    signature = inspect.signature(analyze_completed_session_volume_profiles)
    assert tuple(signature.parameters) == (
        "instrument", "timeframe", "bar_duration_seconds", "trade_dates", "bars",
        "calendar_entries", "calendar_version", "timezone_data_version", "as_of_timestamp",
    )
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in signature.parameters.values())
    assert all(parameter.default is inspect.Parameter.empty for parameter in signature.parameters.values())
    expected_fields = {
        CompletedSessionVolumeLevel: [
            "price_tick", "bid_volume", "ask_volume", "reported_total_volume"
        ],
        CompletedSessionVolumeBar: [
            "index", "open_timestamp", "close_timestamp", "open_tick", "high_tick",
            "low_tick", "close_tick", "is_closed", "source_format",
            "reported_total_volume", "levels",
        ],
        CompletedSessionVolumeAtPrice: [
            "price_tick", "bid_volume", "ask_volume", "total_volume"
        ],
        CompletedSessionVolumeProfile: [
            "profile_id", "trade_date", "session_open_timestamp",
            "session_close_timestamp", "first_known_timestamp", "source_format",
            "timezone_name", "timezone_data_version", "calendar_version",
            "bar_duration_seconds", "source_bar_indices",
            "source_bar_open_timestamps", "source_bar_close_timestamps",
            "source_bar_ohlc_ticks", "price_levels", "poc_tick", "poc_tied_ticks",
            "volume_weighted_mean_numerator", "volume_weighted_mean_denominator",
            "val_tick", "vah_tick", "total_volume", "covered_volume",
            "covered_percentage_numerator", "covered_percentage_denominator",
            "completeness", "data_quality",
        ],
        CompletedSessionVolumeProfileSnapshot: [
            "snapshot_id", "effective_timestamp", "profile_ids"
        ],
        CompletedSessionVolumeProfileResult: [
            "status", "profiles", "snapshots", "reasons", "blocking_reasons"
        ],
    }
    for dataclass_type, names in expected_fields.items():
        assert [field.name for field in fields(dataclass_type)] == names
        assert dataclass_type.__dataclass_params__.frozen is True
    result_fields = fields(CompletedSessionVolumeProfileResult)
    assert [field.name for field in result_fields] == ["status", "profiles", "snapshots", "reasons", "blocking_reasons"]
    assert all(field.default == () for field in result_fields[1:])
    assert get_type_hints(CompletedSessionVolumeProfile)["price_levels"] == tuple[CompletedSessionVolumeAtPrice, ...]


# Logical case 46.
def test_case_46_exact_enums_exports_and_no_hvn_lvn_surface() -> None:
    assert [member.value for member in CompletedSessionVolumeProfileCompleteness] == ["COMPLETE", "INCOMPLETE"]
    assert [member.value for member in CompletedSessionVolumeProfileDataQuality] == ["QUALIFIED", "UNQUALIFIED"]
    expected = (
        "COMPLETED_SESSION_VOLUME_PROFILE_VERSION",
        "COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE",
        "COMPLETED_SESSION_VOLUME_PROFILE_SOURCE",
        "CompletedSessionVolumeProfileCompleteness",
        "CompletedSessionVolumeProfileDataQuality",
        "CompletedSessionVolumeLevel", "CompletedSessionVolumeBar",
        "CompletedSessionVolumeAtPrice", "CompletedSessionVolumeProfile",
        "CompletedSessionVolumeProfileSnapshot", "CompletedSessionVolumeProfileResult",
        "make_volume_profile_id", "analyze_completed_session_volume_profiles",
    )
    assert volume_profile.__all__ == expected
    assert not any("hvn" in name.lower() or "lvn" in name.lower() for name in volume_profile.__all__)
    assert not hasattr(volume_profile, "CompletedSessionVolumeProfileTransition")


# Logical case 47.
def test_case_47_status_precedence_atomic_cutoff_and_prior_evidence() -> None:
    second_date = date(2026, 1, 7)
    first_open, first_close = _session_bounds(TRADE_DATE)
    second_open, second_close = _session_bounds(second_date)
    first_bar = _bar(index=0, opening=first_open, closing=first_close)
    second_bar = _bar(index=1, opening=second_open, closing=second_close)
    unknown = _analyze(
        trade_dates=(TRADE_DATE, second_date), bars=(first_bar, second_bar),
        calendar_entries=(_entry(),), as_of_timestamp=second_close,
    )
    assert unknown.status is SMCV2PrimitiveStatus.UNKNOWN
    assert len(unknown.profiles) == len(unknown.snapshots) == 1
    malformed = replace(second_bar, reported_total_volume=999)
    invalid = _analyze(
        trade_dates=(TRADE_DATE, second_date), bars=(first_bar, malformed),
        calendar_entries=(_entry(), _entry(second_date)), as_of_timestamp=second_close,
    )
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    assert invalid.profiles == unknown.profiles
    assert invalid.snapshots == unknown.snapshots
    missing_calendar_but_invalid_later = _analyze(
        trade_dates=(TRADE_DATE, second_date),
        bars=(first_bar, malformed),
        calendar_entries=(_entry(),),
        as_of_timestamp=second_close,
    )
    assert missing_calendar_but_invalid_later.status is SMCV2PrimitiveStatus.INVALID
    assert missing_calendar_but_invalid_later.profiles == unknown.profiles
    assert missing_calendar_but_invalid_later.snapshots == unknown.snapshots

    only_later_unrequested = _analyze(
        trade_dates=(TRADE_DATE,),
        bars=(second_bar,),
        calendar_entries=(_entry(),),
        as_of_timestamp=second_close,
    )
    assert only_later_unrequested.status is SMCV2PrimitiveStatus.INVALID
    assert only_later_unrequested.profiles == only_later_unrequested.snapshots == ()


# Logical case 48.
def test_case_48_prefix_invariance_determinism_and_forbidden_import_surface() -> None:
    second_date = date(2026, 1, 7)
    first_open, first_close = _session_bounds(TRADE_DATE)
    second_open, second_close = _session_bounds(second_date)
    first = _analyze(
        bars=(_bar(index=0, opening=first_open, closing=first_close),),
        as_of_timestamp=first_close,
    )
    extended = _analyze(
        trade_dates=(TRADE_DATE, second_date),
        bars=(
            _bar(index=0, opening=first_open, closing=first_close),
            _bar(index=1, opening=second_open, closing=second_close),
        ),
        calendar_entries=(_entry(), _entry(second_date)),
        as_of_timestamp=second_close,
    )
    assert first.profiles == extended.profiles[:1]
    assert first.snapshots == extended.snapshots[:1]
    assert extended == _analyze(
        trade_dates=(TRADE_DATE, second_date),
        bars=(
            _bar(index=0, opening=first_open, closing=first_close),
            _bar(index=1, opening=second_open, closing=second_close),
        ),
        calendar_entries=(_entry(), _entry(second_date)),
        as_of_timestamp=second_close,
    )
    assert _analyze(
        bars=(_bar(), _bar()),
        calendar_entries=(_entry(),),
    ).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(
        trade_dates=(second_date, TRADE_DATE),
        bars=(), calendar_entries=(), as_of_timestamp=second_close,
    ).status is SMCV2PrimitiveStatus.INVALID
    source = Path(volume_profile.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "orderflow.footprint" not in imported_modules
    assert "orderflow.sierra_chart_importer" not in imported_modules
