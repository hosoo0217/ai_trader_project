"""Deterministic completed-session Volume Profile diagnostics.

The module consumes only immutable, integer-normalized, caller-supplied
full-footprint evidence. It performs no import, file, network, strategy, risk,
execution, or integration activity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from math import gcd
import hashlib
from importlib import metadata
import json
import re
from zoneinfo import ZoneInfo

from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus
from smc.smc_v2_primitives import SMCV2PrimitiveStatus, normalize_utc_timestamp


COMPLETED_SESSION_VOLUME_PROFILE_VERSION = (
    "SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-1"
)
COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE = "America/New_York"
COMPLETED_SESSION_VOLUME_PROFILE_SOURCE = "ACSIL_FULL_FOOTPRINT"

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY_KINDS = frozenset({"PROFILE", "SNAPSHOT"})


class CompletedSessionVolumeProfileCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class CompletedSessionVolumeProfileDataQuality(str, Enum):
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"


@dataclass(frozen=True)
class CompletedSessionVolumeLevel:
    price_tick: int
    bid_volume: int
    ask_volume: int
    reported_total_volume: int


@dataclass(frozen=True)
class CompletedSessionVolumeBar:
    index: int
    open_timestamp: datetime
    close_timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    is_closed: bool
    source_format: str
    reported_total_volume: int
    levels: tuple[CompletedSessionVolumeLevel, ...]


@dataclass(frozen=True)
class CompletedSessionVolumeAtPrice:
    price_tick: int
    bid_volume: int
    ask_volume: int
    total_volume: int


@dataclass(frozen=True)
class CompletedSessionVolumeProfile:
    profile_id: str
    trade_date: date
    session_open_timestamp: datetime
    session_close_timestamp: datetime
    first_known_timestamp: datetime
    source_format: str
    timezone_name: str
    timezone_data_version: str
    calendar_version: str
    bar_duration_seconds: int
    source_bar_indices: tuple[int, ...]
    source_bar_open_timestamps: tuple[datetime, ...]
    source_bar_close_timestamps: tuple[datetime, ...]
    source_bar_ohlc_ticks: tuple[tuple[int, int, int, int], ...]
    price_levels: tuple[CompletedSessionVolumeAtPrice, ...]
    poc_tick: int
    poc_tied_ticks: tuple[int, ...]
    volume_weighted_mean_numerator: int
    volume_weighted_mean_denominator: int
    val_tick: int
    vah_tick: int
    total_volume: int
    covered_volume: int
    covered_percentage_numerator: int
    covered_percentage_denominator: int
    completeness: CompletedSessionVolumeProfileCompleteness
    data_quality: CompletedSessionVolumeProfileDataQuality


@dataclass(frozen=True)
class CompletedSessionVolumeProfileSnapshot:
    snapshot_id: str
    effective_timestamp: datetime
    profile_ids: tuple[str, ...]


@dataclass(frozen=True)
class CompletedSessionVolumeProfileResult:
    status: SMCV2PrimitiveStatus
    profiles: tuple[CompletedSessionVolumeProfile, ...] = ()
    snapshots: tuple[CompletedSessionVolumeProfileSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _BarScan:
    bars: tuple[CompletedSessionVolumeBar, ...]
    issue_timestamp: datetime | None
    issue_reason: str | None
    issue_unknowable: bool


@dataclass(frozen=True)
class _CalendarScan:
    entries: tuple[KillZoneCalendarEntry, ...]
    issue_date: date | None
    issue_reason: str | None
    issue_unknowable: bool


def make_volume_profile_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    calendar_version: str,
    timezone_name: str,
    timezone_data_version: str,
    trade_date: date | None = None,
    session_open_timestamp: datetime | None = None,
    session_close_timestamp: datetime | None = None,
    first_known_timestamp: datetime | None = None,
    source_format: str | None = None,
    bar_duration_seconds: int | None = None,
    source_bar_indices: tuple[int, ...] = (),
    source_bar_open_timestamps: tuple[datetime, ...] = (),
    source_bar_close_timestamps: tuple[datetime, ...] = (),
    source_bar_ohlc_ticks: tuple[tuple[int, int, int, int], ...] = (),
    price_levels: tuple[CompletedSessionVolumeAtPrice, ...] = (),
    poc_tick: int | None = None,
    poc_tied_ticks: tuple[int, ...] = (),
    volume_weighted_mean_numerator: int | None = None,
    volume_weighted_mean_denominator: int | None = None,
    val_tick: int | None = None,
    vah_tick: int | None = None,
    total_volume: int | None = None,
    covered_volume: int | None = None,
    covered_percentage_numerator: int | None = None,
    covered_percentage_denominator: int | None = None,
    completeness: CompletedSessionVolumeProfileCompleteness | None = None,
    data_quality: CompletedSessionVolumeProfileDataQuality | None = None,
    effective_timestamp: datetime | None = None,
    profile_ids: tuple[str, ...] = (),
) -> str:
    """Build one canonical kind-specific Volume Profile identity."""

    try:
        return _make_volume_profile_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            calendar_version=calendar_version,
            timezone_name=timezone_name,
            timezone_data_version=timezone_data_version,
            trade_date=trade_date,
            session_open_timestamp=session_open_timestamp,
            session_close_timestamp=session_close_timestamp,
            first_known_timestamp=first_known_timestamp,
            source_format=source_format,
            bar_duration_seconds=bar_duration_seconds,
            source_bar_indices=source_bar_indices,
            source_bar_open_timestamps=source_bar_open_timestamps,
            source_bar_close_timestamps=source_bar_close_timestamps,
            source_bar_ohlc_ticks=source_bar_ohlc_ticks,
            price_levels=price_levels,
            poc_tick=poc_tick,
            poc_tied_ticks=poc_tied_ticks,
            volume_weighted_mean_numerator=volume_weighted_mean_numerator,
            volume_weighted_mean_denominator=volume_weighted_mean_denominator,
            val_tick=val_tick,
            vah_tick=vah_tick,
            total_volume=total_volume,
            covered_volume=covered_volume,
            covered_percentage_numerator=covered_percentage_numerator,
            covered_percentage_denominator=covered_percentage_denominator,
            completeness=completeness,
            data_quality=data_quality,
            effective_timestamp=effective_timestamp,
            profile_ids=profile_ids,
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        raise ValueError("malformed Volume Profile identity evidence") from exc


def analyze_completed_session_volume_profiles(
    *,
    instrument: str,
    timeframe: str,
    bar_duration_seconds: int,
    trade_dates: tuple[date, ...] | None,
    bars: tuple[CompletedSessionVolumeBar, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
    timezone_data_version: str,
    as_of_timestamp: datetime,
) -> CompletedSessionVolumeProfileResult:
    """Analyze immutable completed-session full-footprint evidence fail closed."""

    try:
        normalized_instrument = _normalize_text(
            instrument, name="instrument", uppercase=True
        )
        normalized_timeframe = _normalize_text(
            timeframe, name="timeframe", uppercase=True
        )
        duration = _positive_int(bar_duration_seconds, name="bar_duration_seconds")
        normalized_calendar_version = _normalize_text(
            calendar_version, name="calendar_version"
        )
        normalized_timezone_version = _normalize_text(
            timezone_data_version, name="timezone_data_version"
        )
        normalized_as_of = normalize_utc_timestamp(as_of_timestamp)
    except Exception:
        return _result(SMCV2PrimitiveStatus.INVALID, "INVALID_ARGUMENT")

    try:
        normalized_trade_dates = _validate_trade_dates(trade_dates)
    except Exception:
        return _result(SMCV2PrimitiveStatus.INVALID, "INVALID_TRADE_DATES")

    timezone_value = _load_timezone()
    bar_scan = _scan_bars(bars, duration=duration)
    calendar_scan = _scan_calendar_entries(
        calendar_entries,
        calendar_version=normalized_calendar_version,
        timezone_value=timezone_value,
    )

    if bar_scan.issue_reason is not None and bar_scan.issue_unknowable:
        return _result(SMCV2PrimitiveStatus.INVALID, bar_scan.issue_reason)
    if calendar_scan.issue_reason is not None and calendar_scan.issue_unknowable:
        return _result(SMCV2PrimitiveStatus.INVALID, calendar_scan.issue_reason)

    try:
        runtime_version = _runtime_timezone_data_version()
    except Exception:
        runtime_version = None
    if timezone_value is None or runtime_version is None:
        if bar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, bar_scan.issue_reason)
        if calendar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, calendar_scan.issue_reason)
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            "TIMEZONE_AUTHORITY_UNAVAILABLE",
            blocking=True,
        )

    try:
        normalized_runtime_version = _normalize_text(
            runtime_version, name="runtime_timezone_data_version"
        )
    except Exception:
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            "TIMEZONE_AUTHORITY_UNAVAILABLE",
            blocking=True,
        )
    if normalized_timezone_version != normalized_runtime_version:
        return _result(SMCV2PrimitiveStatus.INVALID, "TIMEZONE_DATA_VERSION_MISMATCH")

    if normalized_trade_dates == ():
        if bar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, bar_scan.issue_reason)
        if calendar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, calendar_scan.issue_reason)
        if bar_scan.bars:
            return _result(SMCV2PrimitiveStatus.INVALID, "UNREQUESTED_BAR")
        if calendar_scan.entries:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                "UNREQUESTED_CALENDAR_ENTRY",
            )
        if bars is None or calendar_entries is None:
            return _result(
                SMCV2PrimitiveStatus.UNKNOWN,
                "MISSING_TOP_LEVEL_CONTEXT",
                blocking=True,
            )
        return _result(SMCV2PrimitiveStatus.NONE, "NO_REQUESTED_SESSIONS")

    if trade_dates is None or bars is None or calendar_entries is None:
        if bar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, bar_scan.issue_reason)
        if calendar_scan.issue_reason is not None:
            return _result(SMCV2PrimitiveStatus.INVALID, calendar_scan.issue_reason)
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            "MISSING_TOP_LEVEL_CONTEXT",
            blocking=True,
        )

    assert normalized_trade_dates is not None
    requested = frozenset(normalized_trade_dates)
    entry_map = {entry.trade_date: entry for entry in calendar_scan.entries}
    extra_entries = tuple(
        entry.trade_date for entry in calendar_scan.entries if entry.trade_date not in requested
    )
    calendar_issue_date = calendar_scan.issue_date
    calendar_issue_reason = calendar_scan.issue_reason
    if extra_entries:
        earliest_extra = min(extra_entries)
        if calendar_issue_date is None or earliest_extra < calendar_issue_date:
            calendar_issue_date = earliest_extra
            calendar_issue_reason = "UNREQUESTED_CALENDAR_ENTRY"

    inferred_bar_dates: dict[int, date | None] = {}
    attribution_issue_timestamp: datetime | None = None
    for position, bar in enumerate(bar_scan.bars):
        inferred = _infer_trade_date(bar.open_timestamp, timezone_value)
        inferred_bar_dates[position] = inferred
        if inferred is None or inferred not in requested:
            if (
                attribution_issue_timestamp is None
                or bar.open_timestamp < attribution_issue_timestamp
            ):
                attribution_issue_timestamp = bar.open_timestamp

    issue_timestamp = _earliest_timestamp(
        bar_scan.issue_timestamp, attribution_issue_timestamp
    )
    issue_reason = (
        bar_scan.issue_reason
        if bar_scan.issue_timestamp == issue_timestamp and bar_scan.issue_reason is not None
        else "BAR_SESSION_ATTRIBUTION_INVALID"
    )

    profiles: list[CompletedSessionVolumeProfile] = []
    snapshots: list[CompletedSessionVolumeProfileSnapshot] = []
    saw_none = False
    pending_unknown_reason: str | None = None

    for current_date in normalized_trade_dates:
        entry = entry_map.get(current_date)

        if calendar_issue_reason is not None:
            if calendar_issue_date is None or calendar_issue_date <= current_date:
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    calendar_issue_reason,
                    profiles=tuple(profiles),
                    snapshots=tuple(snapshots),
                )

        _, standard_close = _standard_session_bounds(current_date, timezone_value)
        issue_cutoff = standard_close
        if (
            entry is not None
            and entry.session_status is not KillZoneSessionStatus.SESSION_CLOSED
        ):
            issue_cutoff = normalize_utc_timestamp(entry.session_close_timestamp)  # type: ignore[arg-type]
        if issue_timestamp is not None and issue_timestamp <= issue_cutoff:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                issue_reason,
                profiles=tuple(profiles),
                snapshots=tuple(snapshots),
            )

        if current_date.weekday() >= 5:
            if entry is not None and entry.session_status is not KillZoneSessionStatus.SESSION_CLOSED:
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    "WEEKEND_OPEN_CONTRADICTION",
                    profiles=tuple(profiles),
                    snapshots=tuple(snapshots),
                )
            weekend_bars = tuple(
                bar
                for position, bar in enumerate(bar_scan.bars)
                if inferred_bar_dates[position] == current_date
            )
            if weekend_bars:
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    "BAR_FOR_CLOSED_SESSION",
                    profiles=tuple(profiles),
                    snapshots=tuple(snapshots),
                )
            saw_none = True
            continue

        if entry is None:
            pending_unknown_reason = pending_unknown_reason or "CALENDAR_UNVERIFIED"
            continue

        if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
            closed_bars = tuple(
                bar
                for position, bar in enumerate(bar_scan.bars)
                if inferred_bar_dates[position] == current_date
            )
            if closed_bars:
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    "BAR_FOR_CLOSED_SESSION",
                    profiles=tuple(profiles),
                    snapshots=tuple(snapshots),
                )
            saw_none = True
            continue

        session_open = normalize_utc_timestamp(entry.session_open_timestamp)  # type: ignore[arg-type]
        session_close = normalize_utc_timestamp(entry.session_close_timestamp)  # type: ignore[arg-type]

        session_bars = tuple(
            bar
            for position, bar in enumerate(bar_scan.bars)
            if inferred_bar_dates[position] == current_date
        )

        if normalized_as_of < session_close:
            saw_none = True
            continue
        if not session_bars:
            pending_unknown_reason = pending_unknown_reason or "DATA_UNAVAILABLE"
            continue

        try:
            profile = _build_profile(
                instrument=normalized_instrument,
                timeframe=normalized_timeframe,
                calendar_version=normalized_calendar_version,
                timezone_data_version=normalized_timezone_version,
                trade_date_value=current_date,
                session_open=session_open,
                session_close=session_close,
                duration=duration,
                bars=session_bars,
            )
        except _ZeroVolume:
            saw_none = True
            continue
        except Exception:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                "SESSION_PROFILE_INVALID",
                profiles=tuple(profiles),
                snapshots=tuple(snapshots),
            )

        if pending_unknown_reason is not None:
            continue

        profiles.append(profile)
        profile_ids = tuple(item.profile_id for item in profiles)
        try:
            snapshot_id = make_volume_profile_id(
                identity_kind="SNAPSHOT",
                instrument=normalized_instrument,
                timeframe=normalized_timeframe,
                calendar_version=normalized_calendar_version,
                timezone_name=COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
                timezone_data_version=normalized_timezone_version,
                effective_timestamp=profile.first_known_timestamp,
                profile_ids=profile_ids,
            )
        except Exception:
            profiles.pop()
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                "SNAPSHOT_IDENTITY_INVALID",
                profiles=tuple(profiles),
                snapshots=tuple(snapshots),
            )
        snapshots.append(
            CompletedSessionVolumeProfileSnapshot(
                snapshot_id=snapshot_id,
                effective_timestamp=profile.first_known_timestamp,
                profile_ids=profile_ids,
            )
        )

    if issue_timestamp is not None:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            issue_reason,
            profiles=tuple(profiles),
            snapshots=tuple(snapshots),
        )
    if calendar_issue_reason is not None:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            calendar_issue_reason,
            profiles=tuple(profiles),
            snapshots=tuple(snapshots),
        )
    if pending_unknown_reason is not None:
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            pending_unknown_reason,
            profiles=tuple(profiles),
            snapshots=tuple(snapshots),
            blocking=True,
        )
    if profiles:
        reasons = ["PROFILE_EMITTED"]
        if any(
            profile.completeness is CompletedSessionVolumeProfileCompleteness.INCOMPLETE
            for profile in profiles
        ):
            reasons.append("INCOMPLETE_SESSION")
        return CompletedSessionVolumeProfileResult(
            status=SMCV2PrimitiveStatus.VALID,
            profiles=tuple(profiles),
            snapshots=tuple(snapshots),
            reasons=tuple(reasons),
        )
    if saw_none:
        return _result(SMCV2PrimitiveStatus.NONE, "NO_COMPLETED_POSITIVE_VOLUME_PROFILE")
    return _result(SMCV2PrimitiveStatus.NONE, "NO_PROFILE")


class _ZeroVolume(Exception):
    pass


def _make_volume_profile_id(
    *,
    identity_kind: object,
    instrument: object,
    timeframe: object,
    calendar_version: object,
    timezone_name: object,
    timezone_data_version: object,
    trade_date: object,
    session_open_timestamp: object,
    session_close_timestamp: object,
    first_known_timestamp: object,
    source_format: object,
    bar_duration_seconds: object,
    source_bar_indices: object,
    source_bar_open_timestamps: object,
    source_bar_close_timestamps: object,
    source_bar_ohlc_ticks: object,
    price_levels: object,
    poc_tick: object,
    poc_tied_ticks: object,
    volume_weighted_mean_numerator: object,
    volume_weighted_mean_denominator: object,
    val_tick: object,
    vah_tick: object,
    total_volume: object,
    covered_volume: object,
    covered_percentage_numerator: object,
    covered_percentage_denominator: object,
    completeness: object,
    data_quality: object,
    effective_timestamp: object,
    profile_ids: object,
) -> str:
    if type(identity_kind) is not str or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind must be PROFILE or SNAPSHOT")
    normalized_instrument = _normalize_text(instrument, name="instrument", uppercase=True)
    normalized_timeframe = _normalize_text(timeframe, name="timeframe", uppercase=True)
    normalized_calendar_version = _normalize_text(
        calendar_version, name="calendar_version"
    )
    if type(timezone_name) is not str or timezone_name != COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE:
        raise ValueError("timezone_name must be exactly America/New_York")
    normalized_timezone_version = _normalize_text(
        timezone_data_version, name="timezone_data_version"
    )
    runtime_version = _runtime_timezone_data_version()
    timezone_value = _load_timezone()
    if runtime_version is None or timezone_value is None:
        raise ValueError("runtime timezone authority is unavailable")
    if normalized_timezone_version != _normalize_text(
        runtime_version, name="runtime_timezone_data_version"
    ):
        raise ValueError("timezone-data version mismatch")

    payload: dict[str, object] = {
        "calendar_version": normalized_calendar_version,
        "detector_version": COMPLETED_SESSION_VOLUME_PROFILE_VERSION,
        "identity_kind": identity_kind,
        "instrument": normalized_instrument,
        "timeframe": normalized_timeframe,
        "timezone_data_version": normalized_timezone_version,
        "timezone_name": COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
    }

    profile_values = {
        "trade_date": trade_date,
        "session_open_timestamp": session_open_timestamp,
        "session_close_timestamp": session_close_timestamp,
        "first_known_timestamp": first_known_timestamp,
        "source_format": source_format,
        "bar_duration_seconds": bar_duration_seconds,
        "source_bar_indices": source_bar_indices,
        "source_bar_open_timestamps": source_bar_open_timestamps,
        "source_bar_close_timestamps": source_bar_close_timestamps,
        "source_bar_ohlc_ticks": source_bar_ohlc_ticks,
        "price_levels": price_levels,
        "poc_tick": poc_tick,
        "poc_tied_ticks": poc_tied_ticks,
        "volume_weighted_mean_numerator": volume_weighted_mean_numerator,
        "volume_weighted_mean_denominator": volume_weighted_mean_denominator,
        "val_tick": val_tick,
        "vah_tick": vah_tick,
        "total_volume": total_volume,
        "covered_volume": covered_volume,
        "covered_percentage_numerator": covered_percentage_numerator,
        "covered_percentage_denominator": covered_percentage_denominator,
        "completeness": completeness,
        "data_quality": data_quality,
    }

    if identity_kind == "SNAPSHOT":
        for name, value in profile_values.items():
            default = () if name in {
                "source_bar_indices", "source_bar_open_timestamps",
                "source_bar_close_timestamps", "source_bar_ohlc_ticks",
                "price_levels", "poc_tied_ticks",
            } else None
            if value != default:
                raise ValueError(f"SNAPSHOT forbids {name}")
        normalized_effective = normalize_utc_timestamp(effective_timestamp)  # type: ignore[arg-type]
        validated_ids = _validate_hash_tuple(profile_ids, name="profile_ids")
        payload.update(
            {
                "effective_timestamp": _timestamp_text(normalized_effective),
                "profile_ids": list(validated_ids),
            }
        )
    else:
        if effective_timestamp is not None or profile_ids != ():
            raise ValueError("PROFILE forbids snapshot parameters")
        normalized_trade_date = _validate_date(trade_date, name="trade_date")
        session_open = normalize_utc_timestamp(session_open_timestamp)  # type: ignore[arg-type]
        session_close = normalize_utc_timestamp(session_close_timestamp)  # type: ignore[arg-type]
        first_known = normalize_utc_timestamp(first_known_timestamp)  # type: ignore[arg-type]
        if session_open >= session_close or first_known != session_close:
            raise ValueError("invalid session or first-known timestamps")
        if normalized_trade_date.weekday() >= 5:
            raise ValueError("PROFILE trade_date must be Monday through Friday")
        standard_open, standard_close = _standard_session_bounds(
            normalized_trade_date,
            timezone_value,
        )
        if session_open != standard_open or session_close > standard_close:
            raise ValueError("PROFILE session provenance does not match trade_date")
        if type(source_format) is not str or source_format != COMPLETED_SESSION_VOLUME_PROFILE_SOURCE:
            raise ValueError("source_format is not qualified")
        duration = _positive_int(bar_duration_seconds, name="bar_duration_seconds")
        session_microseconds = _timedelta_microseconds(session_close - session_open)
        duration_microseconds = duration * 1_000_000
        if session_microseconds % duration_microseconds != 0:
            raise ValueError("bar duration must divide session exactly")
        expected_bar_count = session_microseconds // duration_microseconds

        indices = _validate_int_tuple(
            source_bar_indices, name="source_bar_indices", nonempty=True, nonnegative=True
        )
        opens = _validate_timestamp_tuple(
            source_bar_open_timestamps, name="source_bar_open_timestamps"
        )
        closes = _validate_timestamp_tuple(
            source_bar_close_timestamps, name="source_bar_close_timestamps"
        )
        ohlc = _validate_ohlc_tuple(source_bar_ohlc_ticks)
        if not (len(indices) == len(opens) == len(closes) == len(ohlc)):
            raise ValueError("source bar tuples must have equal length")
        for opening, closing in zip(opens, closes):
            if closing - opening != timedelta(seconds=duration):
                raise ValueError("source bar duration mismatch")
            if not (session_open <= opening < closing <= session_close):
                raise ValueError("source bar is outside session")
            if _timedelta_microseconds(opening - session_open) % duration_microseconds:
                raise ValueError("source bar is off grid")
        if any(earlier >= later for earlier, later in zip(closes, closes[1:])):
            raise ValueError("source close timestamps must be strictly increasing")

        validated_levels = _validate_output_levels(price_levels)
        if any(
            not any(
                low_tick <= level.price_tick <= high_tick
                for _, high_tick, low_tick, _ in ohlc
            )
            for level in validated_levels
        ):
            raise ValueError("price level is outside all source-bar OHLC ranges")
        metrics = _compute_metrics(validated_levels)
        supplied_total = _positive_int(total_volume, name="total_volume")
        if supplied_total != metrics["total_volume"]:
            raise ValueError("total volume mismatch")
        supplied_poc = _exact_int(poc_tick, name="poc_tick")
        tied = _validate_int_tuple(
            poc_tied_ticks, name="poc_tied_ticks", nonempty=True, nonnegative=False
        )
        if supplied_poc != metrics["poc_tick"] or tied != metrics["poc_tied_ticks"]:
            raise ValueError("POC reconciliation failed")
        mean_numerator = _exact_int(
            volume_weighted_mean_numerator, name="volume_weighted_mean_numerator"
        )
        mean_denominator = _positive_int(
            volume_weighted_mean_denominator, name="volume_weighted_mean_denominator"
        )
        if (mean_numerator, mean_denominator) != metrics["mean_fraction"]:
            raise ValueError("weighted mean reconciliation failed")
        supplied_val = _exact_int(val_tick, name="val_tick")
        supplied_vah = _exact_int(vah_tick, name="vah_tick")
        supplied_covered = _positive_int(covered_volume, name="covered_volume")
        percentage_numerator = _positive_int(
            covered_percentage_numerator, name="covered_percentage_numerator"
        )
        percentage_denominator = _positive_int(
            covered_percentage_denominator, name="covered_percentage_denominator"
        )
        if (
            supplied_val != metrics["val_tick"]
            or supplied_vah != metrics["vah_tick"]
            or supplied_covered != metrics["covered_volume"]
            or (percentage_numerator, percentage_denominator)
            != metrics["covered_fraction"]
        ):
            raise ValueError("Value Area reconciliation failed")
        if type(completeness) is not CompletedSessionVolumeProfileCompleteness:
            raise TypeError("completeness has the wrong type")
        if type(data_quality) is not CompletedSessionVolumeProfileDataQuality:
            raise TypeError("data_quality has the wrong type")
        complete_grid = len(opens) == expected_bar_count and all(
            _timedelta_microseconds(opening - session_open)
            == position * duration_microseconds
            for position, opening in enumerate(opens)
        )
        expected_pair = (
            CompletedSessionVolumeProfileCompleteness.COMPLETE,
            CompletedSessionVolumeProfileDataQuality.QUALIFIED,
        ) if complete_grid else (
            CompletedSessionVolumeProfileCompleteness.INCOMPLETE,
            CompletedSessionVolumeProfileDataQuality.UNQUALIFIED,
        )
        if (completeness, data_quality) != expected_pair:
            raise ValueError("completeness and data quality do not reconcile")

        payload.update(
            {
                "bar_duration_seconds": duration,
                "completeness": completeness.value,
                "covered_percentage_denominator": percentage_denominator,
                "covered_percentage_numerator": percentage_numerator,
                "covered_volume": supplied_covered,
                "data_quality": data_quality.value,
                "first_known_timestamp": _timestamp_text(first_known),
                "poc_tick": supplied_poc,
                "poc_tied_ticks": list(tied),
                "price_levels": [
                    {
                        "ask_volume": level.ask_volume,
                        "bid_volume": level.bid_volume,
                        "price_tick": level.price_tick,
                        "total_volume": level.total_volume,
                    }
                    for level in validated_levels
                ],
                "session_close_timestamp": _timestamp_text(session_close),
                "session_open_timestamp": _timestamp_text(session_open),
                "source_bar_close_timestamps": [_timestamp_text(value) for value in closes],
                "source_bar_indices": list(indices),
                "source_bar_ohlc_ticks": [list(value) for value in ohlc],
                "source_bar_open_timestamps": [_timestamp_text(value) for value in opens],
                "source_format": source_format,
                "total_volume": supplied_total,
                "trade_date": normalized_trade_date.isoformat(),
                "vah_tick": supplied_vah,
                "val_tick": supplied_val,
                "volume_weighted_mean_denominator": mean_denominator,
                "volume_weighted_mean_numerator": mean_numerator,
            }
        )

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _scan_bars(
    values: tuple[CompletedSessionVolumeBar, ...] | None,
    *,
    duration: int,
) -> _BarScan:
    if values is None:
        return _BarScan((), None, None, False)
    if type(values) is not tuple:
        return _BarScan((), None, "BARS_MUST_BE_TUPLE", True)
    valid: list[CompletedSessionVolumeBar] = []
    previous: CompletedSessionVolumeBar | None = None
    for raw in values:
        effective = _safe_bar_moment(raw)
        try:
            bar = _validate_bar(raw, duration=duration)
            if previous is not None:
                if bar.index <= previous.index:
                    raise ValueError("bar indices must be strictly increasing")
                if bar.open_timestamp <= previous.open_timestamp:
                    raise ValueError("bar opens must be strictly increasing")
                if (
                    bar.open_timestamp,
                    bar.close_timestamp,
                    bar.index,
                ) <= (
                    previous.open_timestamp,
                    previous.close_timestamp,
                    previous.index,
                ):
                    raise ValueError("bar composite order is invalid")
                if bar.open_timestamp < previous.close_timestamp:
                    raise ValueError("bars cannot overlap")
            valid.append(bar)
            previous = bar
        except Exception:
            return _BarScan(
                tuple(valid),
                effective,
                "MALFORMED_OR_MISORDERED_BAR",
                effective is None,
            )
    return _BarScan(tuple(valid), None, None, False)


def _scan_calendar_entries(
    values: tuple[KillZoneCalendarEntry, ...] | None,
    *,
    calendar_version: str,
    timezone_value: ZoneInfo | None,
) -> _CalendarScan:
    if values is None:
        return _CalendarScan((), None, None, False)
    if type(values) is not tuple:
        return _CalendarScan((), None, "CALENDAR_ENTRIES_MUST_BE_TUPLE", True)
    valid: list[KillZoneCalendarEntry] = []
    previous_date: date | None = None
    for raw in values:
        effective = _safe_calendar_date(raw)
        try:
            entry = _validate_calendar_entry(
                raw,
                calendar_version=calendar_version,
                timezone_value=timezone_value,
            )
            if previous_date is not None and entry.trade_date <= previous_date:
                raise ValueError("calendar dates must be strictly increasing")
            valid.append(entry)
            previous_date = entry.trade_date
        except Exception:
            return _CalendarScan(
                tuple(valid),
                effective,
                "MALFORMED_OR_MISORDERED_CALENDAR_ENTRY",
                effective is None,
            )
    return _CalendarScan(tuple(valid), None, None, False)


def _validate_bar(value: object, *, duration: int) -> CompletedSessionVolumeBar:
    if type(value) is not CompletedSessionVolumeBar:
        raise TypeError("bars must contain CompletedSessionVolumeBar values")
    try:
        index = _exact_int(value.index, name="bar index")
        opening = normalize_utc_timestamp(value.open_timestamp)
        closing = normalize_utc_timestamp(value.close_timestamp)
        open_tick = _exact_int(value.open_tick, name="open_tick")
        high_tick = _exact_int(value.high_tick, name="high_tick")
        low_tick = _exact_int(value.low_tick, name="low_tick")
        close_tick = _exact_int(value.close_tick, name="close_tick")
        is_closed = value.is_closed
        source_format = value.source_format
        reported_total = _exact_int(
            value.reported_total_volume, name="bar reported_total_volume"
        )
        levels = value.levels
    except Exception as exc:
        raise ValueError("malformed bar") from exc
    if index < 0 or reported_total < 0:
        raise ValueError("bar index and volume cannot be negative")
    if closing - opening != timedelta(seconds=duration):
        raise ValueError("bar duration mismatch")
    if not (low_tick <= open_tick <= high_tick and low_tick <= close_tick <= high_tick):
        raise ValueError("invalid OHLC geometry")
    if type(is_closed) is not bool or not is_closed:
        raise ValueError("bar must be fully closed")
    if type(source_format) is not str or source_format != COMPLETED_SESSION_VOLUME_PROFILE_SOURCE:
        raise ValueError("unqualified source format")
    if type(levels) is not tuple or not levels:
        raise TypeError("levels must be a nonempty tuple")
    validated_levels: list[CompletedSessionVolumeLevel] = []
    previous_tick: int | None = None
    for raw_level in levels:
        level = _validate_input_level(raw_level)
        if previous_tick is not None and level.price_tick <= previous_tick:
            raise ValueError("price levels must be strictly increasing")
        if not low_tick <= level.price_tick <= high_tick:
            raise ValueError("price level is outside bar range")
        validated_levels.append(level)
        previous_tick = level.price_tick
    if sum(level.reported_total_volume for level in validated_levels) != reported_total:
        raise ValueError("bar volume does not conserve")
    return CompletedSessionVolumeBar(
        index=index,
        open_timestamp=opening,
        close_timestamp=closing,
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
        is_closed=True,
        source_format=COMPLETED_SESSION_VOLUME_PROFILE_SOURCE,
        reported_total_volume=reported_total,
        levels=tuple(validated_levels),
    )


def _validate_input_level(value: object) -> CompletedSessionVolumeLevel:
    if type(value) is not CompletedSessionVolumeLevel:
        raise TypeError("levels must contain CompletedSessionVolumeLevel values")
    try:
        price_tick = _exact_int(value.price_tick, name="price_tick")
        bid_volume = _exact_int(value.bid_volume, name="bid_volume")
        ask_volume = _exact_int(value.ask_volume, name="ask_volume")
        reported_total = _exact_int(
            value.reported_total_volume, name="reported_total_volume"
        )
    except Exception as exc:
        raise ValueError("malformed price level") from exc
    if min(bid_volume, ask_volume, reported_total) < 0:
        raise ValueError("volume cannot be negative")
    if bid_volume + ask_volume != reported_total:
        raise ValueError("price-level volume does not conserve")
    return CompletedSessionVolumeLevel(
        price_tick=price_tick,
        bid_volume=bid_volume,
        ask_volume=ask_volume,
        reported_total_volume=reported_total,
    )


def _validate_calendar_entry(
    value: object,
    *,
    calendar_version: str,
    timezone_value: ZoneInfo | None,
) -> KillZoneCalendarEntry:
    if type(value) is not KillZoneCalendarEntry:
        raise TypeError("calendar entries must use KillZoneCalendarEntry")
    try:
        version = _normalize_text(value.calendar_version, name="entry calendar_version")
        trade_date_value = _validate_date(value.trade_date, name="trade_date")
        status = value.session_status
        opening = value.session_open_timestamp
        closing = value.session_close_timestamp
    except Exception as exc:
        raise ValueError("malformed calendar entry") from exc
    if version != calendar_version:
        raise ValueError("calendar version mismatch")
    if type(status) is not KillZoneSessionStatus:
        raise TypeError("invalid calendar session status")
    if status is KillZoneSessionStatus.SESSION_CLOSED:
        if opening is not None or closing is not None:
            raise ValueError("closed sessions require absent timestamps")
        return KillZoneCalendarEntry(version, trade_date_value, status, None, None)
    normalized_open = normalize_utc_timestamp(opening)  # type: ignore[arg-type]
    normalized_close = normalize_utc_timestamp(closing)  # type: ignore[arg-type]
    if normalized_open >= normalized_close:
        raise ValueError("calendar session interval is invalid")
    if trade_date_value.weekday() >= 5:
        raise ValueError("weekend sessions cannot be open")
    if timezone_value is not None:
        expected_open, expected_close = _standard_session_bounds(
            trade_date_value, timezone_value
        )
        if normalized_open != expected_open:
            raise ValueError("calendar open mismatch")
        if status is KillZoneSessionStatus.OPEN and normalized_close != expected_close:
            raise ValueError("OPEN close mismatch")
        if status is KillZoneSessionStatus.EARLY_CLOSE and not (
            normalized_open < normalized_close < expected_close
        ):
            raise ValueError("EARLY_CLOSE boundary mismatch")
    return KillZoneCalendarEntry(
        calendar_version=version,
        trade_date=trade_date_value,
        session_status=status,
        session_open_timestamp=normalized_open,
        session_close_timestamp=normalized_close,
    )


def _build_profile(
    *,
    instrument: str,
    timeframe: str,
    calendar_version: str,
    timezone_data_version: str,
    trade_date_value: date,
    session_open: datetime,
    session_close: datetime,
    duration: int,
    bars: tuple[CompletedSessionVolumeBar, ...],
) -> CompletedSessionVolumeProfile:
    duration_microseconds = duration * 1_000_000
    session_microseconds = _timedelta_microseconds(session_close - session_open)
    if session_microseconds % duration_microseconds:
        raise ValueError("duration does not divide session")
    expected_count = session_microseconds // duration_microseconds
    expected_positions: set[int] = set()
    aggregate: dict[int, list[int]] = {}
    for bar in bars:
        if not (session_open <= bar.open_timestamp < bar.close_timestamp <= session_close):
            raise ValueError("bar falls outside session")
        offset = _timedelta_microseconds(bar.open_timestamp - session_open)
        if offset % duration_microseconds:
            raise ValueError("bar is off the session grid")
        position = offset // duration_microseconds
        if position in expected_positions:
            raise ValueError("duplicate grid position")
        expected_positions.add(position)
        for level in bar.levels:
            totals = aggregate.setdefault(level.price_tick, [0, 0])
            totals[0] += level.bid_volume
            totals[1] += level.ask_volume
    price_levels = tuple(
        CompletedSessionVolumeAtPrice(
            price_tick=tick,
            bid_volume=volumes[0],
            ask_volume=volumes[1],
            total_volume=volumes[0] + volumes[1],
        )
        for tick, volumes in sorted(aggregate.items())
    )
    total_volume = sum(level.total_volume for level in price_levels)
    if total_volume == 0:
        raise _ZeroVolume
    if total_volume != sum(bar.reported_total_volume for bar in bars):
        raise ValueError("profile volume does not conserve")
    metrics = _compute_metrics(price_levels)
    complete = expected_positions == set(range(expected_count))
    completeness = (
        CompletedSessionVolumeProfileCompleteness.COMPLETE
        if complete
        else CompletedSessionVolumeProfileCompleteness.INCOMPLETE
    )
    quality = (
        CompletedSessionVolumeProfileDataQuality.QUALIFIED
        if complete
        else CompletedSessionVolumeProfileDataQuality.UNQUALIFIED
    )
    kwargs: dict[str, object] = {
        "identity_kind": "PROFILE",
        "instrument": instrument,
        "timeframe": timeframe,
        "calendar_version": calendar_version,
        "timezone_name": COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
        "timezone_data_version": timezone_data_version,
        "trade_date": trade_date_value,
        "session_open_timestamp": session_open,
        "session_close_timestamp": session_close,
        "first_known_timestamp": session_close,
        "source_format": COMPLETED_SESSION_VOLUME_PROFILE_SOURCE,
        "bar_duration_seconds": duration,
        "source_bar_indices": tuple(bar.index for bar in bars),
        "source_bar_open_timestamps": tuple(bar.open_timestamp for bar in bars),
        "source_bar_close_timestamps": tuple(bar.close_timestamp for bar in bars),
        "source_bar_ohlc_ticks": tuple(
            (bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick) for bar in bars
        ),
        "price_levels": price_levels,
        "poc_tick": metrics["poc_tick"],
        "poc_tied_ticks": metrics["poc_tied_ticks"],
        "volume_weighted_mean_numerator": metrics["mean_fraction"][0],
        "volume_weighted_mean_denominator": metrics["mean_fraction"][1],
        "val_tick": metrics["val_tick"],
        "vah_tick": metrics["vah_tick"],
        "total_volume": total_volume,
        "covered_volume": metrics["covered_volume"],
        "covered_percentage_numerator": metrics["covered_fraction"][0],
        "covered_percentage_denominator": metrics["covered_fraction"][1],
        "completeness": completeness,
        "data_quality": quality,
    }
    profile_id = make_volume_profile_id(**kwargs)
    return CompletedSessionVolumeProfile(
        profile_id=profile_id,
        trade_date=trade_date_value,
        session_open_timestamp=session_open,
        session_close_timestamp=session_close,
        first_known_timestamp=session_close,
        source_format=COMPLETED_SESSION_VOLUME_PROFILE_SOURCE,
        timezone_name=COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE,
        timezone_data_version=timezone_data_version,
        calendar_version=calendar_version,
        bar_duration_seconds=duration,
        source_bar_indices=kwargs["source_bar_indices"],  # type: ignore[arg-type]
        source_bar_open_timestamps=kwargs["source_bar_open_timestamps"],  # type: ignore[arg-type]
        source_bar_close_timestamps=kwargs["source_bar_close_timestamps"],  # type: ignore[arg-type]
        source_bar_ohlc_ticks=kwargs["source_bar_ohlc_ticks"],  # type: ignore[arg-type]
        price_levels=price_levels,
        poc_tick=metrics["poc_tick"],  # type: ignore[arg-type]
        poc_tied_ticks=metrics["poc_tied_ticks"],  # type: ignore[arg-type]
        volume_weighted_mean_numerator=metrics["mean_fraction"][0],  # type: ignore[index]
        volume_weighted_mean_denominator=metrics["mean_fraction"][1],  # type: ignore[index]
        val_tick=metrics["val_tick"],  # type: ignore[arg-type]
        vah_tick=metrics["vah_tick"],  # type: ignore[arg-type]
        total_volume=total_volume,
        covered_volume=metrics["covered_volume"],  # type: ignore[arg-type]
        covered_percentage_numerator=metrics["covered_fraction"][0],  # type: ignore[index]
        covered_percentage_denominator=metrics["covered_fraction"][1],  # type: ignore[index]
        completeness=completeness,
        data_quality=quality,
    )


def _compute_metrics(
    levels: tuple[CompletedSessionVolumeAtPrice, ...],
) -> dict[str, object]:
    if not levels:
        raise ValueError("price levels cannot be empty")
    total_volume = sum(level.total_volume for level in levels)
    if total_volume <= 0:
        raise ValueError("total volume must be positive")
    weighted_numerator = sum(level.price_tick * level.total_volume for level in levels)
    mean_fraction = _reduce_fraction(weighted_numerator, total_volume)
    maximum = max(level.total_volume for level in levels)
    tied = tuple(level.price_tick for level in levels if level.total_volume == maximum)
    poc_tick = min(
        tied,
        key=lambda tick: (abs(tick * total_volume - weighted_numerator), tick),
    )
    volumes = {level.price_tick: level.total_volume for level in levels}
    val_tick = poc_tick
    vah_tick = poc_tick
    covered = volumes[poc_tick]
    minimum_tick = levels[0].price_tick
    maximum_tick = levels[-1].price_tick
    while covered * 10 < total_volume * 7:
        below = val_tick - 1 if val_tick > minimum_tick else None
        above = vah_tick + 1 if vah_tick < maximum_tick else None
        if below is None and above is None:
            break
        if below is None:
            selected = above
        elif above is None:
            selected = below
        else:
            below_volume = volumes.get(below, 0)
            above_volume = volumes.get(above, 0)
            selected = below if below_volume >= above_volume else above
        assert selected is not None
        covered += volumes.get(selected, 0)
        if selected < val_tick:
            val_tick = selected
        else:
            vah_tick = selected
    return {
        "covered_fraction": _reduce_fraction(covered, total_volume),
        "covered_volume": covered,
        "mean_fraction": mean_fraction,
        "poc_tick": poc_tick,
        "poc_tied_ticks": tied,
        "total_volume": total_volume,
        "vah_tick": vah_tick,
        "val_tick": val_tick,
    }


def _validate_output_levels(value: object) -> tuple[CompletedSessionVolumeAtPrice, ...]:
    if type(value) is not tuple or not value:
        raise TypeError("price_levels must be a nonempty tuple")
    result: list[CompletedSessionVolumeAtPrice] = []
    previous_tick: int | None = None
    for raw in value:
        if type(raw) is not CompletedSessionVolumeAtPrice:
            raise TypeError("malformed output price level")
        try:
            tick = _exact_int(raw.price_tick, name="price_tick")
            bid = _exact_int(raw.bid_volume, name="bid_volume")
            ask = _exact_int(raw.ask_volume, name="ask_volume")
            total = _exact_int(raw.total_volume, name="total_volume")
        except Exception as exc:
            raise ValueError("malformed output price level") from exc
        if min(bid, ask, total) < 0 or total != bid + ask:
            raise ValueError("output price level does not conserve")
        if previous_tick is not None and tick <= previous_tick:
            raise ValueError("output levels must be strictly increasing")
        result.append(CompletedSessionVolumeAtPrice(tick, bid, ask, total))
        previous_tick = tick
    return tuple(result)


def _validate_trade_dates(value: object) -> tuple[date, ...] | None:
    if value is None:
        return None
    if type(value) is not tuple:
        raise TypeError("trade_dates must be a tuple")
    result = tuple(_validate_date(item, name="trade_date") for item in value)
    if any(earlier >= later for earlier, later in zip(result, result[1:])):
        raise ValueError("trade_dates must be strictly increasing")
    return result


def _validate_int_tuple(
    value: object,
    *,
    name: str,
    nonempty: bool,
    nonnegative: bool,
) -> tuple[int, ...]:
    if type(value) is not tuple or (nonempty and not value):
        raise TypeError(f"{name} must be a{' nonempty' if nonempty else ''} tuple")
    result = tuple(_exact_int(item, name=name) for item in value)
    if nonnegative and any(item < 0 for item in result):
        raise ValueError(f"{name} cannot contain negative values")
    if any(earlier >= later for earlier, later in zip(result, result[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return result


def _validate_timestamp_tuple(value: object, *, name: str) -> tuple[datetime, ...]:
    if type(value) is not tuple or not value:
        raise TypeError(f"{name} must be a nonempty tuple")
    result = tuple(normalize_utc_timestamp(item) for item in value)
    if any(earlier >= later for earlier, later in zip(result, result[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return result


def _validate_ohlc_tuple(value: object) -> tuple[tuple[int, int, int, int], ...]:
    if type(value) is not tuple or not value:
        raise TypeError("source_bar_ohlc_ticks must be a nonempty tuple")
    result: list[tuple[int, int, int, int]] = []
    for raw in value:
        if type(raw) is not tuple or len(raw) != 4:
            raise TypeError("each OHLC value must be a four-member tuple")
        opening, high, low, closing = (
            _exact_int(item, name="OHLC tick") for item in raw
        )
        if not (low <= opening <= high and low <= closing <= high):
            raise ValueError("invalid OHLC geometry")
        result.append((opening, high, low, closing))
    return tuple(result)


def _validate_hash_tuple(value: object, *, name: str) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise TypeError(f"{name} must be a nonempty tuple")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        if type(item) is not str or _HASH_PATTERN.fullmatch(item) is None:
            raise ValueError(f"{name} contains a malformed hash")
        if item in seen:
            raise ValueError(f"{name} must be unique")
        seen.add(item)
        result.append(item)
    return tuple(result)


def _standard_session_bounds(
    trade_date_value: date, timezone_value: ZoneInfo
) -> tuple[datetime, datetime]:
    opening = datetime.combine(
        trade_date_value - timedelta(days=1), time(18), tzinfo=timezone_value
    )
    closing = datetime.combine(trade_date_value, time(17), tzinfo=timezone_value)
    return normalize_utc_timestamp(opening), normalize_utc_timestamp(closing)


def _infer_trade_date(timestamp: datetime, timezone_value: ZoneInfo) -> date | None:
    local = normalize_utc_timestamp(timestamp).astimezone(timezone_value)
    local_time = local.timetz().replace(tzinfo=None)
    if local_time >= time(18):
        return local.date() + timedelta(days=1)
    if local_time < time(17):
        return local.date()
    return None


def _safe_bar_moment(value: object) -> datetime | None:
    try:
        return normalize_utc_timestamp(value.open_timestamp)  # type: ignore[attr-defined]
    except Exception:
        return None


def _safe_calendar_date(value: object) -> date | None:
    try:
        return _validate_date(value.trade_date, name="trade_date")  # type: ignore[attr-defined]
    except Exception:
        return None


def _earliest_timestamp(
    first: datetime | None, second: datetime | None
) -> datetime | None:
    if first is None:
        return second
    if second is None:
        return first
    return min(first, second)


def _runtime_timezone_data_version() -> str | None:
    try:
        return metadata.version("tzdata")
    except Exception:
        return None


def _load_timezone() -> ZoneInfo | None:
    try:
        return ZoneInfo(COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE)
    except Exception:
        return None


def _normalize_text(value: object, *, name: str, uppercase: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized.upper() if uppercase else normalized


def _validate_date(value: object, *, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be a date")
    return value


def _exact_int(value: object, *, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    return value


def _positive_int(value: object, *, name: str) -> int:
    normalized = _exact_int(value, name=name)
    if normalized <= 0:
        raise ValueError(f"{name} must be positive")
    return normalized


def _reduce_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator <= 0:
        raise ValueError("fraction denominator must be positive")
    divisor = gcd(abs(numerator), denominator)
    return numerator // divisor, denominator // divisor


def _timedelta_microseconds(value: timedelta) -> int:
    return (
        value.days * 86_400_000_000
        + value.seconds * 1_000_000
        + value.microseconds
    )


def _timestamp_text(value: datetime) -> str:
    normalized = normalize_utc_timestamp(value)
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _result(
    status: SMCV2PrimitiveStatus,
    reason: str,
    *,
    profiles: tuple[CompletedSessionVolumeProfile, ...] = (),
    snapshots: tuple[CompletedSessionVolumeProfileSnapshot, ...] = (),
    blocking: bool = False,
) -> CompletedSessionVolumeProfileResult:
    return CompletedSessionVolumeProfileResult(
        status=status,
        profiles=profiles,
        snapshots=snapshots,
        reasons=(reason,),
        blocking_reasons=(reason,) if blocking else (),
    )


__all__ = (
    "COMPLETED_SESSION_VOLUME_PROFILE_VERSION",
    "COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE",
    "COMPLETED_SESSION_VOLUME_PROFILE_SOURCE",
    "CompletedSessionVolumeProfileCompleteness",
    "CompletedSessionVolumeProfileDataQuality",
    "CompletedSessionVolumeLevel",
    "CompletedSessionVolumeBar",
    "CompletedSessionVolumeAtPrice",
    "CompletedSessionVolumeProfile",
    "CompletedSessionVolumeProfileSnapshot",
    "CompletedSessionVolumeProfileResult",
    "make_volume_profile_id",
    "analyze_completed_session_volume_profiles",
)
