"""Deterministic GC NY-AM opening-range sweep/reclaim reversion feasibility.

This module is deliberately standalone and diagnostic-only.  It consumes immutable
dataset and kill-zone evidence, emits immutable evidence objects, and has no
training, ranking, decision, execution, persistence, or network authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import hashlib
import importlib.metadata
import json
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from analysis.gc_dataset_builder import (
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCSplitSessionCalendarEntry,
)
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneContext,
    KillZoneResult,
    KillZoneSnapshot,
    make_kill_zone_id,
)
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION = "GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1"


class GCNYAMSweepReclaimIdentityKind(str, Enum):
    OBSERVATION = "OBSERVATION"
    OPENING_RANGE = "OPENING_RANGE"
    CANDIDATE = "CANDIDATE"
    OUTCOME = "OUTCOME"
    MANIFEST = "MANIFEST"


class GCNYAMSweepReclaimOutcomeType(str, Enum):
    MIDPOINT_REACHED = "MIDPOINT_REACHED"
    INVALIDATED = "INVALIDATED"
    TIMEOUT = "TIMEOUT"
    SAME_BAR_AMBIGUOUS = "SAME_BAR_AMBIGUOUS"
    INCOMPLETE = "INCOMPLETE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class GCNYAMSweepReclaimObservation:
    observation_id: str
    segment_ordinal: int
    segment_id: str
    contract: str
    trade_date: date
    index: int
    bar_open_timestamp: datetime
    bar_close_timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    volume: int
    is_closed: bool
    kill_zone_context_id: str
    kill_zone_snapshot_id: str


@dataclass(frozen=True)
class GCNYAMSweepReclaimOpeningRange:
    range_id: str
    segment_ordinal: int
    segment_id: str
    contract: str
    trade_date: date
    source_observation_ids: tuple[str, ...]
    source_context_ids: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    first_known_index: int
    first_known_timestamp: datetime
    high_tick: int
    low_tick: int
    midpoint_tick: Decimal
    width_ticks: int


@dataclass(frozen=True)
class GCNYAMSweepReclaimCandidate:
    candidate_id: str
    range_id: str
    segment_ordinal: int
    segment_id: str
    contract: str
    trade_date: date
    direction: SMCV2Direction
    formation_observation_id: str
    formation_context_id: str
    formation_snapshot_id: str
    formation_index: int
    first_known_timestamp: datetime
    swept_boundary_tick: int
    sweep_extreme_tick: int
    reclaim_close_tick: int
    midpoint_tick: Decimal
    invalidation_tick: int
    width_ticks: int


@dataclass(frozen=True)
class GCNYAMSweepReclaimOutcome:
    outcome_id: str
    candidate_id: str
    outcome: GCNYAMSweepReclaimOutcomeType
    first_known_index: int
    first_known_timestamp: datetime
    horizon_observation_ids: tuple[str, ...]
    event_observation_id: str | None


@dataclass(frozen=True)
class GCNYAMSweepReclaimManifest:
    manifest_id: str
    version: str
    instrument: str
    timeframe: str
    dataset_id: str
    calendar_version: str
    split_session_calendar_digest: str
    kill_zone_calendar_digest: str
    timezone_name: str
    timezone_data_version: str
    requested_trade_dates: tuple[date, ...]
    opening_range_ids: tuple[str, ...]
    candidate_ids: tuple[str, ...]
    outcome_ids: tuple[str, ...]
    count_funnel: tuple[tuple[str, int], ...]
    reason_counts: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class GCNYAMSweepReclaimResult:
    status: SMCV2PrimitiveStatus
    opening_ranges: tuple[GCNYAMSweepReclaimOpeningRange, ...] = ()
    candidates: tuple[GCNYAMSweepReclaimCandidate, ...] = ()
    outcomes: tuple[GCNYAMSweepReclaimOutcome, ...] = ()
    manifest: GCNYAMSweepReclaimManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


__all__ = (
    "GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION",
    "GCNYAMSweepReclaimIdentityKind",
    "GCNYAMSweepReclaimOutcomeType",
    "GCNYAMSweepReclaimObservation",
    "GCNYAMSweepReclaimOpeningRange",
    "GCNYAMSweepReclaimCandidate",
    "GCNYAMSweepReclaimOutcome",
    "GCNYAMSweepReclaimManifest",
    "GCNYAMSweepReclaimResult",
    "make_gc_ny_am_sweep_reclaim_id",
    "analyze_gc_ny_am_opening_range_sweep_reclaim_reversion",
)


_COUNT_FUNNEL_KEYS = (
    "REQUESTED_TRADE_DATES",
    "CALENDAR_ELIGIBLE_TRADE_DATES",
    "COMPLETE_OPENING_RANGES",
    "NO_SWEEP_RECLAIM_TRADE_DATES",
    "AMBIGUOUS_SWEEP_GROUPS",
    "COMPLETE_CANDIDATES",
    "BULLISH_CANDIDATES",
    "BEARISH_CANDIDATES",
    "MIDPOINT_REACHED_OUTCOMES",
    "INVALIDATED_OUTCOMES",
    "SAME_BAR_AMBIGUOUS_OUTCOMES",
    "TIMEOUT_OUTCOMES",
    "COMPLETE_OUTCOMES",
    "INCOMPLETE_HORIZONS",
    "INVALID_GROUPS",
)

_REASON_TOKENS = (
    "MISSING_TOP_LEVEL_CONTEXT",
    "INVALID_DATASET",
    "OOS_CONTACT",
    "UNREQUESTED_EVIDENCE",
    "INVALID_OBSERVATION",
    "MISSING_SPLIT_SESSION_CALENDAR",
    "INVALID_SPLIT_SESSION_CALENDAR",
    "MISSING_KILL_ZONE_CALENDAR",
    "INVALID_KILL_ZONE_CALENDAR",
    "MISSING_KILL_ZONE_EVIDENCE",
    "INVALID_KILL_ZONE_EVIDENCE",
    "SESSION_INELIGIBLE",
    "INCOMPLETE_OPENING_RANGE",
    "INVALID_OPENING_RANGE",
    "NO_SWEEP_RECLAIM",
    "AMBIGUOUS_SWEEP_RECLAIM",
    "INCOMPLETE_OUTCOME_HORIZON",
    "INVALID_OUTCOME_EVIDENCE",
    "AMBIGUOUS_CANONICAL_INTERPRETATION",
)

_UTC = timezone.utc
_TIMEZONE_NAME = "America/New_York"
_TERMINAL_OUTCOMES = {
    GCNYAMSweepReclaimOutcomeType.MIDPOINT_REACHED,
    GCNYAMSweepReclaimOutcomeType.INVALIDATED,
    GCNYAMSweepReclaimOutcomeType.TIMEOUT,
    GCNYAMSweepReclaimOutcomeType.SAME_BAR_AMBIGUOUS,
}

_CausalKey = tuple[int, int, datetime]


class _EvidenceError(ValueError):
    def __init__(
        self,
        reason: str,
        position: _CausalKey | None = None,
        prefix: tuple[Any, ...] = (),
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.position = position
        self.prefix = prefix


def _enum(value: Any, enum_type: type[Enum], name: str) -> Enum:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {name}") from None


def _text(value: Any, name: str, *, upper: bool = False) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise TypeError(f"{name} must be non-empty canonical text")
    return value.upper() if upper else value


def _hash(value: Any, name: str) -> str:
    value = _text(value, name)
    if len(value) != 64 or value.lower() != value or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return value


def _identity_id(
    value: Any,
    name: str,
    *,
    expected_kind: GCNYAMSweepReclaimIdentityKind | None = None,
) -> str:
    value = _text(value, name)
    try:
        prefix, digest = value.split(":", 1)
    except ValueError:
        raise ValueError(f"{name} must be an uppercase kind-prefixed SHA-256") from None
    if prefix not in {item.value for item in GCNYAMSweepReclaimIdentityKind}:
        raise ValueError(f"{name} identity kind")
    if expected_kind is not None and prefix != expected_kind.value:
        raise ValueError(f"{name} identity kind")
    _hash(digest, name)
    return value


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be int")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} is below minimum")
    return value


def _day(value: Any, name: str) -> date:
    if isinstance(value, datetime) or not isinstance(value, date):
        raise TypeError(f"{name} must be date")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be timezone-aware datetime")
    try:
        return value.astimezone(_UTC)
    except (OverflowError, ValueError, OSError) as exc:
        raise ValueError(f"invalid {name}") from exc


def _decimal(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite() or value <= 0:
        raise ValueError(f"invalid {name}")
    return value


def _midpoint(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be an exact integer/half-tick")
    canonical = _decimal_text(value)
    if not (canonical.endswith(".0") or canonical.endswith(".5")):
        raise ValueError(f"{name} must be an exact integer/half-tick")
    return Decimal("0.0") if value.is_zero() else value


def _exact_midpoint(high_tick: int, low_tick: int) -> Decimal:
    total = high_tick + low_tick
    sign = "-" if total < 0 else ""
    magnitude = abs(total)
    return Decimal(f"{sign}{magnitude // 2}.{'5' if magnitude % 2 else '0'}")


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    sign, digits, exponent = value.as_tuple()
    coefficient = "".join(str(item) for item in digits) or "0"
    if exponent >= 0:
        rendered = coefficient + "0" * exponent + ".0"
    else:
        point = len(coefficient) + exponent
        rendered = (coefficient[:point] + "." + coefficient[point:]) if point > 0 else ("0." + "0" * (-point) + coefficient)
        rendered = rendered.rstrip("0").rstrip(".")
        if "." not in rendered:
            rendered += ".0"
    return ("-" if sign else "") + rendered


def _tuple(value: Any, name: str) -> tuple[Any, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be tuple")
    return value


def _hash_tuple(value: Any, name: str, *, exact: int | None = None, allow_empty: bool = True) -> tuple[str, ...]:
    result = tuple(_hash(item, name) for item in _tuple(value, name))
    if exact is not None and len(result) != exact:
        raise ValueError(f"{name} length")
    if not allow_empty and not result:
        raise ValueError(f"{name} empty")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} duplicates")
    return result


def _identity_tuple(
    value: Any,
    name: str,
    *,
    expected_kind: GCNYAMSweepReclaimIdentityKind,
    exact: int | None = None,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    result = tuple(
        _identity_id(item, name, expected_kind=expected_kind)
        for item in _tuple(value, name)
    )
    if exact is not None and len(result) != exact:
        raise ValueError(f"{name} length")
    if not allow_empty and not result:
        raise ValueError(f"{name} empty")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} duplicates")
    return result


def _date_tuple(value: Any, name: str) -> tuple[date, ...]:
    result = tuple(_day(item, name) for item in _tuple(value, name))
    if len(set(result)) != len(result) or tuple(sorted(result)) != result:
        raise ValueError(f"{name} order")
    return result


def _count_tuple(value: Any, name: str) -> tuple[tuple[str, int], ...]:
    result: list[tuple[str, int]] = []
    for pair in _tuple(value, name):
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise TypeError(f"{name} member")
        result.append((_text(pair[0], name, upper=True), _integer(pair[1], name, minimum=0)))
    if len({key for key, _ in result}) != len(result):
        raise ValueError(f"{name} duplicate key")
    return tuple(result)


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return _timestamp(value, "timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return _decimal_text(value)
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    return value


def _sha(payload: dict[str, Any], identity_kind: str | None = None) -> str:
    encoded = json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return f"{identity_kind}:{digest}" if identity_kind is not None else digest


def _gc_outright_contract(value: Any, name: str = "contract") -> str:
    contract = _text(value, name, upper=True)
    if re.fullmatch(r"GC[FGHJKMNQUVXZ]\d{2}-COMEX", contract) is None:
        raise ValueError(f"{name} must be an unambiguous outright GC contract")
    return contract


def _runtime_tzdata_version() -> str:
    try:
        version = importlib.metadata.version("tzdata")
        ZoneInfo(_TIMEZONE_NAME)
    except (importlib.metadata.PackageNotFoundError, ZoneInfoNotFoundError) as exc:
        raise ValueError("timezone runtime unavailable") from exc
    return _text(version, "runtime timezone-data version", upper=True)


def _calendar_payload(entries: tuple[Any, ...]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for item in entries:
        if isinstance(item, GCSplitSessionCalendarEntry):
            payload.append({
                "calendar_version": item.calendar_version,
                "trade_date": item.trade_date,
                "intervals": tuple((part.start_timestamp, part.end_timestamp) for part in item.intervals),
                "source_artifact_ids": item.source_artifact_ids,
                "source_artifact_sha256s": item.source_artifact_sha256s,
            })
        elif isinstance(item, KillZoneCalendarEntry):
            payload.append({
                "calendar_version": item.calendar_version,
                "trade_date": item.trade_date,
                "session_status": getattr(item.session_status, "value", item.session_status),
                "session_open_timestamp": item.session_open_timestamp,
                "session_close_timestamp": item.session_close_timestamp,
            })
        else:
            raise TypeError("invalid calendar entry")
    return payload


def _split_calendar_digest(entries: tuple[GCSplitSessionCalendarEntry, ...]) -> str:
    return _sha({"kind": "SPLIT_SESSION_CALENDAR", "entries": _calendar_payload(_tuple(entries, "entries"))})


def _kill_calendar_digest(entries: tuple[KillZoneCalendarEntry, ...]) -> str:
    return _sha({"kind": "KILL_ZONE_CALENDAR", "entries": _calendar_payload(_tuple(entries, "entries"))})


def make_gc_ny_am_sweep_reclaim_id(
    *,
    identity_kind: GCNYAMSweepReclaimIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    split_session_calendar_digest: str,
    kill_zone_calendar_digest: str,
    timezone_name: str,
    timezone_data_version: str,
    segment_ordinal: int | None = None,
    segment_id: str | None = None,
    contract: str | None = None,
    trade_date: date | None = None,
    index: int | None = None,
    bar_open_timestamp: datetime | None = None,
    bar_close_timestamp: datetime | None = None,
    open_tick: int | None = None,
    high_tick: int | None = None,
    low_tick: int | None = None,
    close_tick: int | None = None,
    volume: int | None = None,
    is_closed: bool | None = None,
    kill_zone_context_id: str | None = None,
    kill_zone_snapshot_id: str | None = None,
    source_observation_ids: tuple[str, ...] | None = None,
    source_context_ids: tuple[str, ...] | None = None,
    source_snapshot_ids: tuple[str, ...] | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    midpoint_tick: Decimal | None = None,
    width_ticks: int | None = None,
    range_id: str | None = None,
    direction: SMCV2Direction | None = None,
    formation_observation_id: str | None = None,
    formation_context_id: str | None = None,
    formation_snapshot_id: str | None = None,
    formation_index: int | None = None,
    swept_boundary_tick: int | None = None,
    sweep_extreme_tick: int | None = None,
    reclaim_close_tick: int | None = None,
    invalidation_tick: int | None = None,
    candidate_id: str | None = None,
    outcome: GCNYAMSweepReclaimOutcomeType | None = None,
    horizon_observation_ids: tuple[str, ...] | None = None,
    event_observation_id: str | None = None,
    version: str | None = None,
    requested_trade_dates: tuple[date, ...] | None = None,
    opening_range_ids: tuple[str, ...] | None = None,
    candidate_ids: tuple[str, ...] | None = None,
    outcome_ids: tuple[str, ...] | None = None,
    count_funnel: tuple[tuple[str, int], ...] | None = None,
    reason_counts: tuple[tuple[str, int], ...] | None = None,
) -> str:
    try:
        kind = _enum(identity_kind, GCNYAMSweepReclaimIdentityKind, "identity_kind")
        common = {
            "version": GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION,
            "identity_kind": kind.value,
            "instrument": _text(instrument, "instrument", upper=True),
            "timeframe": _text(timeframe, "timeframe", upper=True),
            "dataset_id": _hash(dataset_id, "dataset_id"),
            "calendar_version": _text(calendar_version, "calendar_version"),
            "split_session_calendar_digest": _hash(split_session_calendar_digest, "split calendar digest"),
            "kill_zone_calendar_digest": _hash(kill_zone_calendar_digest, "kill calendar digest"),
            "timezone_name": _text(timezone_name, "timezone_name"),
            "timezone_data_version": _text(timezone_data_version, "timezone_data_version", upper=True),
        }
        if common["timezone_name"] != _TIMEZONE_NAME or common["timezone_data_version"] != _runtime_tzdata_version():
            raise ValueError("timezone identity mismatch")
        supplied = locals().copy()
        all_specific = {
            "segment_ordinal", "segment_id", "contract", "trade_date", "index", "bar_open_timestamp",
            "bar_close_timestamp", "open_tick", "high_tick", "low_tick", "close_tick", "volume", "is_closed",
            "kill_zone_context_id", "kill_zone_snapshot_id", "source_observation_ids", "source_context_ids",
            "source_snapshot_ids", "first_known_index", "first_known_timestamp", "midpoint_tick", "width_ticks", "range_id", "direction",
            "formation_observation_id", "formation_context_id", "formation_snapshot_id", "formation_index",
            "swept_boundary_tick", "sweep_extreme_tick", "reclaim_close_tick", "invalidation_tick", "candidate_id", "outcome",
            "horizon_observation_ids", "event_observation_id", "requested_trade_dates", "opening_range_ids",
            "candidate_ids", "outcome_ids", "count_funnel", "reason_counts", "version",
        }
        required: dict[GCNYAMSweepReclaimIdentityKind, set[str]] = {
            GCNYAMSweepReclaimIdentityKind.OBSERVATION: {"segment_ordinal", "segment_id", "contract", "trade_date", "index", "bar_open_timestamp", "bar_close_timestamp", "open_tick", "high_tick", "low_tick", "close_tick", "volume", "is_closed", "kill_zone_context_id", "kill_zone_snapshot_id"},
            GCNYAMSweepReclaimIdentityKind.OPENING_RANGE: {"segment_ordinal", "segment_id", "contract", "trade_date", "source_observation_ids", "source_context_ids", "source_snapshot_ids", "first_known_index", "first_known_timestamp", "high_tick", "low_tick", "midpoint_tick", "width_ticks"},
            GCNYAMSweepReclaimIdentityKind.CANDIDATE: {"range_id", "segment_ordinal", "segment_id", "contract", "trade_date", "direction", "formation_observation_id", "formation_context_id", "formation_snapshot_id", "formation_index", "first_known_timestamp", "swept_boundary_tick", "sweep_extreme_tick", "reclaim_close_tick", "midpoint_tick", "invalidation_tick", "width_ticks"},
            GCNYAMSweepReclaimIdentityKind.OUTCOME: {"candidate_id", "outcome", "first_known_index", "first_known_timestamp", "horizon_observation_ids"},
            GCNYAMSweepReclaimIdentityKind.MANIFEST: {"version", "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids", "count_funnel", "reason_counts"},
        }
        allowed = required[kind] | ({"event_observation_id"} if kind is GCNYAMSweepReclaimIdentityKind.OUTCOME else set())
        manifest_tuple_fields = {
            "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids",
            "count_funnel", "reason_counts",
        }
        payload: dict[str, Any] = dict(common)
        for name in all_specific:
            value = supplied[name]
            absent = value is None or value == ()
            if name in required[kind] and absent and not (kind is GCNYAMSweepReclaimIdentityKind.MANIFEST and name in manifest_tuple_fields):
                raise ValueError(f"missing {name}")
            if name not in allowed and not absent:
                raise ValueError(f"forbidden {name}")
        if kind is GCNYAMSweepReclaimIdentityKind.OBSERVATION:
            opening = _timestamp(bar_open_timestamp, "bar_open_timestamp")
            closing = _timestamp(bar_close_timestamp, "bar_close_timestamp")
            ticks = tuple(_integer(value, name) for name, value in (("open_tick", open_tick), ("high_tick", high_tick), ("low_tick", low_tick), ("close_tick", close_tick)))
            if closing - opening != timedelta(minutes=5) or ticks[1] < max(ticks[0], ticks[3]) or ticks[2] > min(ticks[0], ticks[3]) or ticks[1] < ticks[2] or is_closed is not True:
                raise ValueError("invalid observation geometry")
            payload.update(segment_ordinal=_integer(segment_ordinal, "segment_ordinal", minimum=0), segment_id=_hash(segment_id, "segment_id"), contract=_gc_outright_contract(contract), trade_date=_day(trade_date, "trade_date"), index=_integer(index, "index", minimum=0), bar_open_timestamp=opening, bar_close_timestamp=closing, open_tick=ticks[0], high_tick=ticks[1], low_tick=ticks[2], close_tick=ticks[3], volume=_integer(volume, "volume", minimum=0), is_closed=True, kill_zone_context_id=_hash(kill_zone_context_id, "context_id"), kill_zone_snapshot_id=_hash(kill_zone_snapshot_id, "snapshot_id"))
        elif kind is GCNYAMSweepReclaimIdentityKind.OPENING_RANGE:
            observation_ids = _identity_tuple(
                source_observation_ids,
                "source_observation_ids",
                expected_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                exact=6,
            )
            context_ids = _hash_tuple(source_context_ids, "source_context_ids", exact=6)
            snapshot_ids = _hash_tuple(source_snapshot_ids, "source_snapshot_ids", exact=6)
            high = _integer(high_tick, "high_tick")
            low = _integer(low_tick, "low_tick")
            midpoint = _midpoint(midpoint_tick, "midpoint_tick")
            width = _integer(width_ticks, "width_ticks", minimum=1)
            if high - low != width or midpoint != _exact_midpoint(high, low):
                raise ValueError("range width mismatch")
            payload.update(segment_ordinal=_integer(segment_ordinal, "segment_ordinal", minimum=0), segment_id=_hash(segment_id, "segment_id"), contract=_gc_outright_contract(contract), trade_date=_day(trade_date, "trade_date"), source_observation_ids=observation_ids, source_context_ids=context_ids, source_snapshot_ids=snapshot_ids, first_known_index=_integer(first_known_index, "first_known_index", minimum=0), first_known_timestamp=_timestamp(first_known_timestamp, "first_known_timestamp"), high_tick=high, low_tick=low, midpoint_tick=midpoint, width_ticks=width)
        elif kind is GCNYAMSweepReclaimIdentityKind.CANDIDATE:
            selected_direction = _enum(direction, SMCV2Direction, "direction")
            if selected_direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
                raise ValueError("candidate direction")
            boundary = _integer(swept_boundary_tick, "swept_boundary_tick")
            extreme = _integer(sweep_extreme_tick, "sweep_extreme_tick")
            reclaim = _integer(reclaim_close_tick, "reclaim_close_tick")
            midpoint = _midpoint(midpoint_tick, "midpoint_tick")
            invalidation = _integer(invalidation_tick, "invalidation_tick")
            width = _integer(width_ticks, "width_ticks", minimum=1)
            if selected_direction is SMCV2Direction.BULLISH:
                implied_high = boundary + width
                valid_geometry = (
                    extreme <= boundary - 1
                    and boundary <= reclaim < midpoint
                    and invalidation == extreme - 1
                    and midpoint == _exact_midpoint(implied_high, boundary)
                )
            else:
                implied_low = boundary - width
                valid_geometry = (
                    extreme >= boundary + 1
                    and midpoint < reclaim <= boundary
                    and invalidation == extreme + 1
                    and midpoint == _exact_midpoint(boundary, implied_low)
                )
            if not valid_geometry:
                raise ValueError("candidate geometry")
            payload.update(range_id=_identity_id(range_id, "range_id", expected_kind=GCNYAMSweepReclaimIdentityKind.OPENING_RANGE), segment_ordinal=_integer(segment_ordinal, "segment_ordinal", minimum=0), segment_id=_hash(segment_id, "segment_id"), contract=_gc_outright_contract(contract), trade_date=_day(trade_date, "trade_date"), direction=selected_direction, formation_observation_id=_identity_id(formation_observation_id, "formation_observation_id", expected_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION), formation_context_id=_hash(formation_context_id, "formation_context_id"), formation_snapshot_id=_hash(formation_snapshot_id, "formation_snapshot_id"), formation_index=_integer(formation_index, "formation_index", minimum=0), first_known_timestamp=_timestamp(first_known_timestamp, "first_known_timestamp"), swept_boundary_tick=boundary, sweep_extreme_tick=extreme, reclaim_close_tick=reclaim, midpoint_tick=midpoint, invalidation_tick=invalidation, width_ticks=width)
        elif kind is GCNYAMSweepReclaimIdentityKind.OUTCOME:
            selected_outcome = _enum(outcome, GCNYAMSweepReclaimOutcomeType, "outcome")
            if selected_outcome not in _TERMINAL_OUTCOMES:
                raise ValueError("nonterminal outcome identity")
            horizon = _identity_tuple(
                horizon_observation_ids,
                "horizon_observation_ids",
                expected_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                allow_empty=False,
            )
            if len(horizon) > 12 or (selected_outcome is GCNYAMSweepReclaimOutcomeType.TIMEOUT and len(horizon) != 12):
                raise ValueError("outcome horizon length")
            if selected_outcome is GCNYAMSweepReclaimOutcomeType.TIMEOUT:
                if event_observation_id is not None:
                    raise ValueError("timeout event forbidden")
                event = None
            else:
                event = _identity_id(event_observation_id, "event_observation_id", expected_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION)
                if event != horizon[-1]:
                    raise ValueError("event must end horizon")
            payload.update(candidate_id=_identity_id(candidate_id, "candidate_id", expected_kind=GCNYAMSweepReclaimIdentityKind.CANDIDATE), outcome=selected_outcome, first_known_index=_integer(first_known_index, "first_known_index", minimum=0), first_known_timestamp=_timestamp(first_known_timestamp, "first_known_timestamp"), horizon_observation_ids=horizon, event_observation_id=event)
        else:
            if _text(version, "version") != GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION:
                raise ValueError("manifest version mismatch")
            days = _date_tuple(requested_trade_dates, "requested_trade_dates")
            ranges = _identity_tuple(opening_range_ids, "opening_range_ids", expected_kind=GCNYAMSweepReclaimIdentityKind.OPENING_RANGE)
            candidates = _identity_tuple(candidate_ids, "candidate_ids", expected_kind=GCNYAMSweepReclaimIdentityKind.CANDIDATE)
            outcomes = _identity_tuple(outcome_ids, "outcome_ids", expected_kind=GCNYAMSweepReclaimIdentityKind.OUTCOME)
            counts = _count_tuple(count_funnel, "count_funnel")
            reasons = _count_tuple(reason_counts, "reason_counts")
            if tuple(key for key, _ in counts) != _COUNT_FUNNEL_KEYS:
                raise ValueError("count funnel key order")
            if tuple(key for key, _ in reasons) != tuple(token for token in _REASON_TOKENS if any(key == token for key, _ in reasons)):
                raise ValueError("reason count order")
            payload.update(requested_trade_dates=days, opening_range_ids=ranges, candidate_ids=candidates, outcome_ids=outcomes, count_funnel=counts, reason_counts=reasons)
        return _sha(payload, kind.value)
    except (InvalidOperation, OverflowError, OSError) as exc:
        raise ValueError("invalid identity input") from exc


def _ordered_reasons(reasons: set[str]) -> tuple[str, ...]:
    return tuple(token for token in _REASON_TOKENS if token in reasons)


def _status_value(value: Any) -> str:
    return str(getattr(value, "value", value)).upper()


def _validate_config(config: Any) -> GCDatasetBuildConfig:
    if not isinstance(config, GCDatasetBuildConfig):
        raise _EvidenceError("INVALID_DATASET")
    if (
        config.instrument != "GC"
        or config.timeframe != "5M"
        or config.source_timezone != "Asia/Tokyo"
        or config.exchange_timezone != _TIMEZONE_NAME
        or config.timezone_data_version.upper() != _runtime_tzdata_version()
        or config.tick_size != Decimal("0.1")
        or not _gc_outright_contract(config.initial_contract)
    ):
        raise _EvidenceError("INVALID_DATASET")
    return config


def _validate_dataset(config: GCDatasetBuildConfig, dataset: Any) -> tuple[str, tuple[Any, ...], Any]:
    if not isinstance(dataset, GCDatasetBuildResult) or _status_value(dataset.status) != "VALID":
        raise _EvidenceError("INVALID_DATASET")
    dataset_id = _hash(dataset.dataset_id, "dataset_id")
    if dataset.manifest is None or dataset.manifest.dataset_id != dataset_id or dataset.manifest.calendar_version == "" or dataset.manifest.timezone_data_version.upper() != config.timezone_data_version.upper():
        raise _EvidenceError("INVALID_DATASET")
    segments = _tuple(dataset.segments, "segments")
    previous_segment_timestamp: datetime | None = None
    for ordinal, segment in enumerate(segments):
        if _status_value(segment.partition) != "DEVELOPMENT":
            raise _EvidenceError("OOS_CONTACT", ordinal)
        _hash(segment.segment_id, "segment_id")
        _gc_outright_contract(segment.contract)
        _day(segment.first_trade_date, "first_trade_date")
        _day(segment.last_trade_date, "last_trade_date")
        if segment.first_trade_date > segment.last_trade_date:
            raise _EvidenceError("INVALID_DATASET", ordinal)
        previous_index: int | None = None
        previous_timestamp: datetime | None = None
        for bar in _tuple(segment.bars, "bars"):
            bar_timestamp = _timestamp(bar.timestamp, "bar timestamp")
            bar_index = _integer(bar.index, "bar index", minimum=0)
            if (
                (previous_index is not None and bar_index <= previous_index)
                or (previous_timestamp is not None and bar_timestamp <= previous_timestamp)
            ):
                raise _EvidenceError("INVALID_DATASET", (ordinal, bar_index, bar_timestamp))
            previous_index = bar_index
            previous_timestamp = bar_timestamp
            if bar.is_closed is not True:
                raise _EvidenceError("INVALID_DATASET", (ordinal, bar_index, bar_timestamp))
        if previous_timestamp is not None:
            first_timestamp = _timestamp(segment.bars[0].timestamp, "bar timestamp")
            if previous_segment_timestamp is not None and first_timestamp <= previous_segment_timestamp:
                raise _EvidenceError("INVALID_DATASET", (ordinal, segment.bars[0].index, first_timestamp))
            previous_segment_timestamp = previous_timestamp
    return dataset_id, segments, dataset.manifest


def _validate_split_calendar(entries: Any, calendar_version: str) -> tuple[GCSplitSessionCalendarEntry, ...]:
    result = _tuple(entries, "split_session_calendar_entries")
    previous: date | None = None
    for item in result:
        if not isinstance(item, GCSplitSessionCalendarEntry) or item.calendar_version != calendar_version:
            raise _EvidenceError("INVALID_SPLIT_SESSION_CALENDAR")
        day = _day(item.trade_date, "trade_date")
        if previous is not None and day <= previous:
            raise _EvidenceError("INVALID_SPLIT_SESSION_CALENDAR")
        previous = day
        intervals = _tuple(item.intervals, "intervals")
        if not intervals:
            raise _EvidenceError("INVALID_SPLIT_SESSION_CALENDAR")
        last: datetime | None = None
        for interval in intervals:
            opening = _timestamp(interval.start_timestamp, "session start")
            closing = _timestamp(interval.end_timestamp, "session close")
            if opening >= closing or (last is not None and opening < last):
                raise _EvidenceError("INVALID_SPLIT_SESSION_CALENDAR")
            last = closing
        ids = _hash_tuple(item.source_artifact_ids, "source_artifact_ids", allow_empty=False)
        hashes = _hash_tuple(item.source_artifact_sha256s, "source_artifact_sha256s", allow_empty=False)
        if len(ids) != len(hashes):
            raise _EvidenceError("INVALID_SPLIT_SESSION_CALENDAR")
    return result  # type: ignore[return-value]


def _validate_kill_calendar(entries: Any, calendar_version: str) -> tuple[KillZoneCalendarEntry, ...]:
    result = _tuple(entries, "kill_zone_calendar_entries")
    previous: date | None = None
    for item in result:
        if not isinstance(item, KillZoneCalendarEntry) or item.calendar_version != calendar_version:
            raise _EvidenceError("INVALID_KILL_ZONE_CALENDAR")
        day = _day(item.trade_date, "trade_date")
        if previous is not None and day <= previous:
            raise _EvidenceError("INVALID_KILL_ZONE_CALENDAR")
        previous = day
        status = _status_value(item.session_status)
        if status not in {"OPEN", "EARLY_CLOSE", "SESSION_CLOSED"}:
            raise _EvidenceError("INVALID_KILL_ZONE_CALENDAR")
        if status == "SESSION_CLOSED":
            if item.session_open_timestamp is not None or item.session_close_timestamp is not None:
                raise _EvidenceError("INVALID_KILL_ZONE_CALENDAR")
        else:
            opening = _timestamp(item.session_open_timestamp, "session_open_timestamp")
            closing = _timestamp(item.session_close_timestamp, "session_close_timestamp")
            if opening >= closing:
                raise _EvidenceError("INVALID_KILL_ZONE_CALENDAR")
    return result  # type: ignore[return-value]


def _bar_trade_date(timestamp: datetime, entries: tuple[GCSplitSessionCalendarEntry, ...]) -> date | None:
    moment = _timestamp(timestamp, "bar timestamp")
    for item in entries:
        if any(_timestamp(interval.start_timestamp, "start") < moment <= _timestamp(interval.end_timestamp, "end") for interval in item.intervals):
            return item.trade_date
    return None


def _session_covers_full_analysis_window(
    trade_day: date,
    split_entry: GCSplitSessionCalendarEntry,
    kill_entry: KillZoneCalendarEntry,
) -> bool:
    """Return whether calendars cover every possible V1 source/candidate/horizon bar."""
    if _status_value(kill_entry.session_status) == "SESSION_CLOSED":
        return False
    required_open = datetime.combine(trade_day, time(7, 0), ZoneInfo(_TIMEZONE_NAME)).astimezone(_UTC)
    required_close = datetime.combine(trade_day, time(10, 0), ZoneInfo(_TIMEZONE_NAME)).astimezone(_UTC)
    split_covers = any(
        _timestamp(interval.start_timestamp, "session start") <= required_open
        and _timestamp(interval.end_timestamp, "session end") >= required_close
        for interval in split_entry.intervals
    )
    if not split_covers:
        return False
    return (
        _timestamp(kill_entry.session_open_timestamp, "session open") <= required_open
        and _timestamp(kill_entry.session_close_timestamp, "session close") >= required_close
    )


def _is_expected_ny_am_bar(bar: Any, trade_day: date) -> bool:
    """Return the exact five-minute structural/evidence NY-AM intersection."""
    bar_close = _timestamp(bar.timestamp, "bar timestamp")
    bar_open = bar_close - timedelta(minutes=5)
    local_open = bar_open.astimezone(ZoneInfo(_TIMEZONE_NAME))
    local_close = bar_close.astimezone(ZoneInfo(_TIMEZONE_NAME))
    return (
        local_open.date() == trade_day
        and local_close.date() == trade_day
        and time(7, 0) <= local_open.time().replace(tzinfo=None) < time(10, 0)
        and time(7, 0) <= local_close.time().replace(tzinfo=None) < time(10, 0)
    )


def _validate_observation(item: Any, expected: tuple[int, Any, date], common: dict[str, Any]) -> GCNYAMSweepReclaimObservation:
    ordinal, segment, trade_date = expected
    if not isinstance(item, GCNYAMSweepReclaimObservation):
        raise _EvidenceError("INVALID_OBSERVATION")
    position = None
    if (
        isinstance(getattr(item, "index", None), int)
        and not isinstance(getattr(item, "index", None), bool)
        and isinstance(getattr(item, "bar_close_timestamp", None), datetime)
    ):
        try:
            position = (ordinal, item.index, _timestamp(item.bar_close_timestamp, "bar_close_timestamp"))
        except (TypeError, ValueError):
            position = None
    try:
        if item.segment_ordinal != ordinal or item.segment_id != segment.segment_id or item.contract != segment.contract or item.trade_date != trade_date:
            raise ValueError("observation foreign reference")
        bars = {bar.index: bar for bar in segment.bars}
        bar = bars[item.index]
        if (
            item.bar_close_timestamp != bar.timestamp
            or item.bar_open_timestamp != bar.timestamp - timedelta(minutes=5)
            or (item.open_tick, item.high_tick, item.low_tick, item.close_tick, item.volume, item.is_closed)
            != (bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick, bar.volume, bar.is_closed)
        ):
            raise ValueError("observation/bar mismatch")
        expected_id = make_gc_ny_am_sweep_reclaim_id(
            identity_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION, **common,
            segment_ordinal=item.segment_ordinal, segment_id=item.segment_id, contract=item.contract,
            trade_date=item.trade_date, index=item.index, bar_open_timestamp=item.bar_open_timestamp,
            bar_close_timestamp=item.bar_close_timestamp, open_tick=item.open_tick, high_tick=item.high_tick,
            low_tick=item.low_tick, close_tick=item.close_tick, volume=item.volume, is_closed=item.is_closed,
            kill_zone_context_id=item.kill_zone_context_id, kill_zone_snapshot_id=item.kill_zone_snapshot_id,
        )
        if item.observation_id != expected_id:
            raise ValueError("observation identity")
        return item
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        raise _EvidenceError("INVALID_OBSERVATION", position) from exc


def _validate_supplied_observation_shape(value: Any) -> tuple[GCNYAMSweepReclaimObservation, ...]:
    """Validate evidence that does not depend on a missing foreign collection."""
    result = _tuple(value, "observations")
    previous_key: _CausalKey | None = None
    previous_opening: datetime | None = None
    collapsed: list[GCNYAMSweepReclaimObservation] = []
    seen_ids: dict[str, GCNYAMSweepReclaimObservation] = {}
    seen_effective: dict[tuple[int, int, datetime], GCNYAMSweepReclaimObservation] = {}
    for item in result:
        safe_position: _CausalKey | None = None
        if not isinstance(item, GCNYAMSweepReclaimObservation):
            raise _EvidenceError("INVALID_OBSERVATION")
        try:
            observation_id = _identity_id(
                item.observation_id,
                "observation_id",
                expected_kind=GCNYAMSweepReclaimIdentityKind.OBSERVATION,
            )
            segment_ordinal = _integer(item.segment_ordinal, "segment_ordinal", minimum=0)
            _hash(item.segment_id, "segment_id")
            _gc_outright_contract(item.contract)
            _day(item.trade_date, "trade_date")
            index = _integer(item.index, "index", minimum=0)
            opening = _timestamp(item.bar_open_timestamp, "bar_open_timestamp")
            closing = _timestamp(item.bar_close_timestamp, "bar_close_timestamp")
            if closing - opening != timedelta(minutes=5):
                raise ValueError("bar duration")
            open_tick = _integer(item.open_tick, "open_tick")
            high_tick = _integer(item.high_tick, "high_tick")
            low_tick = _integer(item.low_tick, "low_tick")
            close_tick = _integer(item.close_tick, "close_tick")
            if low_tick > min(open_tick, close_tick) or high_tick < max(open_tick, close_tick) or low_tick > high_tick:
                raise ValueError("OHLC geometry")
            _integer(item.volume, "volume", minimum=0)
            if item.is_closed is not True:
                raise ValueError("observation must be fully closed")
            _hash(item.kill_zone_context_id, "kill_zone_context_id")
            _hash(item.kill_zone_snapshot_id, "kill_zone_snapshot_id")
            effective_key = (segment_ordinal, index, closing)
            safe_position = effective_key
            prior_by_id = seen_ids.get(observation_id)
            prior_by_effective = seen_effective.get(effective_key)
            if prior_by_id is not None:
                if prior_by_id != item or prior_by_effective != item:
                    raise ValueError("contradictory duplicate observation")
                continue
            if prior_by_effective is not None:
                raise ValueError("forked observation")
            if previous_key is not None:
                prior_ordinal, prior_index, prior_closing = previous_key
                if segment_ordinal < prior_ordinal:
                    raise ValueError("observation ordering")
                if segment_ordinal == prior_ordinal and (
                    index <= prior_index
                    or opening <= previous_opening
                    or closing <= prior_closing
                ):
                    raise ValueError("observation ordering")
                if segment_ordinal > prior_ordinal and closing <= prior_closing:
                    raise ValueError("observation ordering")
            previous_key = effective_key
            previous_opening = opening
            seen_ids[observation_id] = item
            seen_effective[effective_key] = item
            collapsed.append(item)
        except (AttributeError, TypeError, ValueError) as exc:
            raise _EvidenceError(
                "INVALID_OBSERVATION",
                safe_position,
                tuple(collapsed),
            ) from exc
    return tuple(collapsed)


def _validate_supplied_kill_result_shape(value: Any) -> KillZoneResult:
    """Validate Kill-zone evidence that is independent of missing foreign inputs."""
    if not isinstance(value, KillZoneResult) or _status_value(value.status) not in {"VALID", "NONE"}:
        raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
    contexts = _tuple(value.contexts, "contexts")
    snapshots = _tuple(value.snapshots, "snapshots")
    for name in ("reasons", "blocking_reasons"):
        members = _tuple(getattr(value, name), name)
        if any(not isinstance(item, str) or not item or item != item.strip() for item in members):
            raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
    context_ids: set[str] = set()
    snapshot_ids: set[str] = set()
    try:
        for context in contexts:
            if not isinstance(context, KillZoneContext):
                raise ValueError("context type")
            context_id = _hash(context.context_id, "context_id")
            if context_id in context_ids:
                raise ValueError("duplicate context")
            context_ids.add(context_id)
            _integer(context.observation_index, "observation_index", minimum=0)
            _timestamp(context.observation_timestamp, "observation_timestamp")
            _day(context.trade_date, "context trade_date")
            if context.zone is not None and (
                not isinstance(context.zone, Enum)
                or _status_value(context.zone) not in {"ASIA", "LONDON", "NEW_YORK_AM", "NEW_YORK_PM"}
            ):
                raise ValueError("context zone")
            if context.session_status is not None and (
                not isinstance(context.session_status, Enum)
                or _status_value(context.session_status) not in {"OPEN", "EARLY_CLOSE", "SESSION_CLOSED"}
            ):
                raise ValueError("context session status")
            if not isinstance(context.quality, Enum) or _status_value(context.quality) not in {
                "VERIFIED", "CALENDAR_UNVERIFIED",
            }:
                raise ValueError("context quality")
            _text(context.calendar_version, "context calendar_version")
            _text(context.timezone_name, "context timezone_name")
            _text(context.timezone_data_version, "context timezone_data_version", upper=True)
        for snapshot in snapshots:
            if not isinstance(snapshot, KillZoneSnapshot):
                raise ValueError("snapshot type")
            snapshot_id = _hash(snapshot.snapshot_id, "snapshot_id")
            if snapshot_id in snapshot_ids:
                raise ValueError("duplicate snapshot")
            snapshot_ids.add(snapshot_id)
            _integer(snapshot.index, "snapshot index", minimum=0)
            _timestamp(snapshot.timestamp, "snapshot timestamp")
            history = _hash_tuple(snapshot.context_ids, "snapshot context_ids", allow_empty=False)
            if len(set(history)) != len(history):
                raise ValueError("snapshot history duplicates")
    except (AttributeError, TypeError, ValueError) as exc:
        raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE") from exc
    if _status_value(value.status) == "NONE" and (contexts or snapshots):
        raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
    return value


def _validate_kill_evidence(
    observations: tuple[GCNYAMSweepReclaimObservation, ...],
    result: Any,
    common: dict[str, Any],
    *,
    segments: tuple[Any, ...],
    split_entries: tuple[GCSplitSessionCalendarEntry, ...],
) -> None:
    result = _validate_supplied_kill_result_shape(result)
    contexts = _tuple(result.contexts, "contexts")
    snapshots = _tuple(result.snapshots, "snapshots")
    bar_owners: dict[tuple[int, datetime, date], list[tuple[int, Any]]] = {}
    for ordinal, segment in enumerate(segments):
        for bar in _tuple(segment.bars, "bars"):
            moment = _timestamp(bar.timestamp, "bar timestamp")
            trade_day = _bar_trade_date(moment, split_entries)
            if trade_day is None:
                continue
            owner_key = (_integer(bar.index, "bar index", minimum=0), moment, trade_day)
            bar_owners.setdefault(owner_key, []).append((ordinal, segment))

    context_map: dict[str, tuple[KillZoneContext, _CausalKey]] = {}
    contexts_by_segment: dict[int, list[str]] = {}
    previous_context: _CausalKey | None = None
    for context in contexts:
        safe_key: _CausalKey | None = None
        try:
            if not isinstance(context, KillZoneContext):
                raise ValueError("context type")
            index = _integer(context.observation_index, "observation_index", minimum=0)
            moment = _timestamp(context.observation_timestamp, "observation_timestamp")
            trade_day = _day(context.trade_date, "context trade_date")
            owners = bar_owners.get((index, moment, trade_day), ())
            if len(owners) != 1:
                raise ValueError("context/dataset ownership")
            ordinal, _ = owners[0]
            key = (ordinal, index, moment)
            safe_key = key
            if previous_context is not None:
                if key[0] < previous_context[0]:
                    raise ValueError("context ordering")
                if key[0] == previous_context[0] and (
                    key[1] <= previous_context[1] or key[2] <= previous_context[2]
                ):
                    raise ValueError("context ordering")
                if key[0] > previous_context[0] and key[2] <= previous_context[2]:
                    raise ValueError("context ordering")
            context_id = _hash(context.context_id, "context_id")
            if context_id in context_map:
                raise ValueError("duplicate context")
            expected_context = make_kill_zone_id(
                identity_kind="CONTEXT", instrument=common["instrument"], timeframe=common["timeframe"],
                calendar_version=common["calendar_version"], timezone_name=_TIMEZONE_NAME,
                timezone_data_version=common["timezone_data_version"], observation_index=context.observation_index,
                observation_timestamp=context.observation_timestamp, trade_date=context.trade_date, zone=context.zone,
                session_status=context.session_status, quality=context.quality,
            )
            if expected_context != context_id:
                raise ValueError("context identity")
        except (AttributeError, TypeError, ValueError) as exc:
            raise _EvidenceError(
                "INVALID_KILL_ZONE_EVIDENCE",
                safe_key,
            ) from exc
        previous_context = key
        context_map[context_id] = (context, key)
        contexts_by_segment.setdefault(ordinal, []).append(context_id)

    snapshot_map: dict[str, tuple[KillZoneSnapshot, _CausalKey]] = {}
    snapshot_counts: dict[int, int] = {}
    previous_snapshot: _CausalKey | None = None
    for snapshot in snapshots:
        safe_key = None
        try:
            if not isinstance(snapshot, KillZoneSnapshot):
                raise ValueError("snapshot type")
            history = _hash_tuple(snapshot.context_ids, "snapshot context_ids", allow_empty=False)
            if len(set(history)) != len(history) or history[-1] not in context_map:
                raise ValueError("snapshot context reference")
            terminal_context, terminal_key = context_map[history[-1]]
            ordinal = terminal_key[0]
            key = (
                ordinal,
                _integer(snapshot.index, "snapshot index", minimum=0),
                _timestamp(snapshot.timestamp, "snapshot timestamp"),
            )
            safe_key = key
            if key != terminal_key:
                raise ValueError("snapshot/context moment")
            if previous_snapshot is not None:
                if key[0] < previous_snapshot[0]:
                    raise ValueError("snapshot ordering")
                if key[0] == previous_snapshot[0] and (
                    key[1] <= previous_snapshot[1] or key[2] <= previous_snapshot[2]
                ):
                    raise ValueError("snapshot ordering")
                if key[0] > previous_snapshot[0] and key[2] <= previous_snapshot[2]:
                    raise ValueError("snapshot ordering")
            expected_position = snapshot_counts.get(ordinal, 0)
            expected_history = tuple(contexts_by_segment.get(ordinal, ())[: expected_position + 1])
            if history != expected_history or terminal_context.context_id != history[-1]:
                raise ValueError("snapshot history mirroring")
            snapshot_id = _hash(snapshot.snapshot_id, "snapshot_id")
            if snapshot_id in snapshot_map:
                raise ValueError("duplicate snapshot")
            expected_snapshot = make_kill_zone_id(
                identity_kind="SNAPSHOT", instrument=common["instrument"], timeframe=common["timeframe"],
                calendar_version=common["calendar_version"], timezone_name=_TIMEZONE_NAME,
                timezone_data_version=common["timezone_data_version"], effective_index=snapshot.index,
                effective_timestamp=snapshot.timestamp, context_ids=snapshot.context_ids,
            )
            if expected_snapshot != snapshot_id:
                raise ValueError("snapshot identity")
        except (AttributeError, TypeError, ValueError) as exc:
            raise _EvidenceError(
                "INVALID_KILL_ZONE_EVIDENCE",
                safe_key,
            ) from exc
        previous_snapshot = key
        snapshot_counts[ordinal] = expected_position + 1
        snapshot_map[snapshot_id] = (snapshot, key)

    if any(snapshot_counts.get(ordinal, 0) != len(ids) for ordinal, ids in contexts_by_segment.items()):
        raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
    referenced_context_ids = {item.kill_zone_context_id for item in observations}
    referenced_snapshot_ids = {item.kill_zone_snapshot_id for item in observations}
    if not referenced_context_ids.issubset(context_map) or not referenced_snapshot_ids.issubset(snapshot_map):
        raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
    for item in observations:
        try:
            context, context_key = context_map[item.kill_zone_context_id]
            snapshot, snapshot_key = snapshot_map[item.kill_zone_snapshot_id]
            expected_key = (
                item.segment_ordinal,
                item.index,
                _timestamp(item.bar_close_timestamp, "bar close"),
            )
            if (
                context_key != expected_key
                or context.trade_date != item.trade_date
                or _status_value(context.zone) != "NEW_YORK_AM"
                or _status_value(context.session_status) not in {"OPEN", "EARLY_CLOSE"}
                or _status_value(context.quality) != "VERIFIED"
                or context.calendar_version != common["calendar_version"]
                or context.timezone_name != _TIMEZONE_NAME
                or context.timezone_data_version.upper() != common["timezone_data_version"]
            ):
                raise ValueError("context mismatch")
            if snapshot_key != expected_key or snapshot.context_ids[-1] != context.context_id:
                raise ValueError("snapshot mismatch")
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise _EvidenceError(
                "INVALID_KILL_ZONE_EVIDENCE",
                (item.segment_ordinal, item.index, _timestamp(item.bar_close_timestamp, "bar close")),
            ) from exc


def _make_manifest(common: dict[str, Any], requested: tuple[date, ...], ranges: tuple[GCNYAMSweepReclaimOpeningRange, ...], candidates: tuple[GCNYAMSweepReclaimCandidate, ...], outcomes: tuple[GCNYAMSweepReclaimOutcome, ...], counts: dict[str, int], reasons: tuple[str, ...]) -> GCNYAMSweepReclaimManifest:
    funnel = tuple((key, counts.get(key, 0)) for key in _COUNT_FUNNEL_KEYS)
    occurrence_counts = {token: 1 for token in reasons}
    occurrence_counts["SESSION_INELIGIBLE"] = max(
        0,
        counts.get("REQUESTED_TRADE_DATES", 0) - counts.get("CALENDAR_ELIGIBLE_TRADE_DATES", 0),
    )
    occurrence_counts["NO_SWEEP_RECLAIM"] = counts.get("NO_SWEEP_RECLAIM_TRADE_DATES", 0)
    occurrence_counts["AMBIGUOUS_SWEEP_RECLAIM"] = counts.get("AMBIGUOUS_SWEEP_GROUPS", 0)
    reason_counts = tuple(
        (token, occurrence_counts[token])
        for token in _REASON_TOKENS
        if token in reasons and occurrence_counts.get(token, 0) > 0
    )
    manifest_id = make_gc_ny_am_sweep_reclaim_id(
        identity_kind=GCNYAMSweepReclaimIdentityKind.MANIFEST, **common,
        version=GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION,
        requested_trade_dates=requested,
        opening_range_ids=tuple(item.range_id for item in ranges),
        candidate_ids=tuple(item.candidate_id for item in candidates),
        outcome_ids=tuple(item.outcome_id for item in outcomes), count_funnel=funnel, reason_counts=reason_counts,
    )
    return GCNYAMSweepReclaimManifest(
        manifest_id, GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION, common["instrument"], common["timeframe"],
        common["dataset_id"], common["calendar_version"], common["split_session_calendar_digest"],
        common["kill_zone_calendar_digest"], common["timezone_name"], common["timezone_data_version"],
        requested, tuple(item.range_id for item in ranges), tuple(item.candidate_id for item in candidates),
        tuple(item.outcome_id for item in outcomes), funnel, reason_counts,
    )


def analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(
    *,
    instrument: str,
    timeframe: str,
    dataset_config: GCDatasetBuildConfig,
    dataset_result: GCDatasetBuildResult | None,
    requested_trade_dates: tuple[date, ...] | None,
    split_session_calendar: tuple[GCSplitSessionCalendarEntry, ...] | None,
    kill_zone_calendar: tuple[KillZoneCalendarEntry, ...] | None,
    observations: tuple[GCNYAMSweepReclaimObservation, ...] | None,
    kill_zone_contexts: tuple[KillZoneContext, ...] | None,
    kill_zone_snapshots: tuple[KillZoneSnapshot, ...] | None,
    kill_zone_result: KillZoneResult | None,
) -> GCNYAMSweepReclaimResult:
    reasons: set[str] = set()
    ranges: list[GCNYAMSweepReclaimOpeningRange] = []
    candidates: list[GCNYAMSweepReclaimCandidate] = []
    outcomes: list[GCNYAMSweepReclaimOutcome] = []
    counts = {key: 0 for key in _COUNT_FUNNEL_KEYS}
    final_status: SMCV2PrimitiveStatus | None = None
    observation_shape_issue: _EvidenceError | None = None
    try:
        config = _validate_config(dataset_config)
        if _text(instrument, "instrument", upper=True) != config.instrument or _text(timeframe, "timeframe", upper=True) != config.timeframe:
            raise _EvidenceError("INVALID_DATASET")
    except (AttributeError, TypeError, ValueError, _EvidenceError):
        return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.INVALID, reasons=("INVALID_DATASET",), blocking_reasons=("INVALID_DATASET",))

    missing = any(item is None for item in (
        dataset_result, requested_trade_dates, split_session_calendar, kill_zone_calendar,
        observations, kill_zone_contexts, kill_zone_snapshots, kill_zone_result,
    ))
    try:
        requested = _date_tuple(requested_trade_dates, "requested_trade_dates") if requested_trade_dates is not None else ()
        if observations is None:
            supplied_observations = ()
        else:
            try:
                supplied_observations = _validate_supplied_observation_shape(observations)
            except _EvidenceError as exc:
                if missing:
                    raise
                supplied_observations = exc.prefix
                observation_shape_issue = exc
        if dataset_result is not None:
            dataset_id, segments, manifest = _validate_dataset(config, dataset_result)
        else:
            dataset_id, segments, manifest = "", (), None
        if split_session_calendar is not None:
            split_entries = _validate_split_calendar(split_session_calendar, manifest.calendar_version if manifest is not None else _calendar_version_fallback(split_session_calendar))
        else:
            split_entries = ()
        if kill_zone_calendar is not None:
            calendar_version = manifest.calendar_version if manifest is not None else _calendar_version_fallback(kill_zone_calendar)
            kill_entries = _validate_kill_calendar(kill_zone_calendar, calendar_version)
        else:
            kill_entries = ()
        if kill_zone_contexts is not None or kill_zone_snapshots is not None:
            _validate_supplied_kill_result_shape(KillZoneResult(
                SMCV2PrimitiveStatus.VALID,
                _tuple(kill_zone_contexts, "kill_zone_contexts") if kill_zone_contexts is not None else (),
                _tuple(kill_zone_snapshots, "kill_zone_snapshots") if kill_zone_snapshots is not None else (),
            ))
        if kill_zone_result is not None:
            _validate_supplied_kill_result_shape(kill_zone_result)
            if kill_zone_contexts is not None and kill_zone_result.contexts != kill_zone_contexts:
                raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
            if kill_zone_snapshots is not None and kill_zone_result.snapshots != kill_zone_snapshots:
                raise _EvidenceError("INVALID_KILL_ZONE_EVIDENCE")
        if requested_trade_dates is not None and not requested:
            supplied_nonempty = any(item not in (None, ()) for item in (observations, split_session_calendar, kill_zone_calendar, kill_zone_contexts, kill_zone_snapshots))
            if kill_zone_result is not None:
                supplied_nonempty = supplied_nonempty or bool(kill_zone_result.contexts or kill_zone_result.snapshots)
            if supplied_nonempty:
                return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.INVALID, reasons=("UNREQUESTED_EVIDENCE",), blocking_reasons=("UNREQUESTED_EVIDENCE",))
            if missing:
                return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.UNKNOWN, reasons=("MISSING_TOP_LEVEL_CONTEXT",), blocking_reasons=("MISSING_TOP_LEVEL_CONTEXT",))
            return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.NONE)
        if missing:
            # Independently determinable supplied objects above have already been validated.
            if observations is not None and not isinstance(observations, tuple):
                raise _EvidenceError("INVALID_OBSERVATION")
            return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.UNKNOWN, reasons=("MISSING_TOP_LEVEL_CONTEXT",), blocking_reasons=("MISSING_TOP_LEVEL_CONTEXT",))
        split_days = {entry.trade_date for entry in split_entries}
        kill_days = {entry.trade_date for entry in kill_entries}
        if any(day not in split_days for day in requested):
            reasons.add("MISSING_SPLIT_SESSION_CALENDAR")
        if any(day not in kill_days for day in requested):
            reasons.add("MISSING_KILL_ZONE_CALENDAR")
        if reasons:
            return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.UNKNOWN, reasons=_ordered_reasons(reasons), blocking_reasons=_ordered_reasons(reasons))
        if any(entry.trade_date not in requested for entry in split_entries + kill_entries):
            raise _EvidenceError("UNREQUESTED_EVIDENCE")
        split_digest = _split_calendar_digest(split_entries)
        kill_digest = _kill_calendar_digest(kill_entries)
        common = {
            "instrument": config.instrument,
            "timeframe": config.timeframe,
            "dataset_id": dataset_id,
            "calendar_version": manifest.calendar_version,
            "split_session_calendar_digest": split_digest,
            "kill_zone_calendar_digest": kill_digest,
            "timezone_name": config.exchange_timezone,
            "timezone_data_version": config.timezone_data_version.upper(),
        }
        counts["REQUESTED_TRADE_DATES"] = len(requested)
        split_by_day = {entry.trade_date: entry for entry in split_entries}
        kill_by_day = {entry.trade_date: entry for entry in kill_entries}
        eligible_days = tuple(
            day for day in requested
            if _session_covers_full_analysis_window(day, split_by_day[day], kill_by_day[day])
        )
        counts["CALENDAR_ELIGIBLE_TRADE_DATES"] = len(eligible_days)
        if len(eligible_days) != len(requested):
            reasons.add("SESSION_INELIGIBLE")

        expected: list[tuple[int, Any, date, Any]] = []
        for ordinal, segment in enumerate(segments):
            for bar in segment.bars:
                trade_day = _bar_trade_date(bar.timestamp, split_entries)
                if trade_day in requested and _is_expected_ny_am_bar(bar, trade_day):
                    expected.append((ordinal, segment, trade_day, bar))
        if len(supplied_observations) > len(expected):
            raise _EvidenceError("UNREQUESTED_EVIDENCE")
        valid_observations: list[GCNYAMSweepReclaimObservation] = []
        invalid_position: _CausalKey | None = (
            observation_shape_issue.position
            if observation_shape_issue is not None
            else None
        )
        if observation_shape_issue is not None:
            reasons.add(observation_shape_issue.reason)
        for position, item in enumerate(supplied_observations):
            if position >= len(expected):
                invalid_position = (
                    item.segment_ordinal,
                    item.index,
                    _timestamp(item.bar_close_timestamp, "bar close"),
                )
                reasons.add("UNREQUESTED_EVIDENCE")
                break
            ordinal, segment, trade_day, bar = expected[position]
            if getattr(item, "index", None) != bar.index:
                invalid_position = (
                    ordinal,
                    _integer(bar.index, "bar index", minimum=0),
                    _timestamp(bar.timestamp, "bar timestamp"),
                )
                reasons.add("INVALID_OBSERVATION")
                break
            try:
                valid_observations.append(_validate_observation(item, (ordinal, segment, trade_day), common))
            except _EvidenceError as exc:
                invalid_position = exc.position if exc.position is not None else position
                reasons.add(exc.reason)
                break
        if invalid_position is None and len(supplied_observations) < len(expected):
            final_status = SMCV2PrimitiveStatus.UNKNOWN
            reasons.add("MISSING_TOP_LEVEL_CONTEXT")
        try:
            _validate_kill_evidence(
                tuple(valid_observations),
                kill_zone_result,
                common,
                segments=segments,
                split_entries=split_entries,
            )
        except _EvidenceError as exc:
            invalid_position = exc.position
            reasons.add(exc.reason)
            if invalid_position is None:
                valid_observations = []
        if "INVALID_OBSERVATION" in reasons or "UNREQUESTED_EVIDENCE" in reasons or "INVALID_KILL_ZONE_EVIDENCE" in reasons:
            if invalid_position is not None:
                valid_observations = [
                    item for item in valid_observations
                    if (
                        item.segment_ordinal,
                        item.index,
                        _timestamp(item.bar_close_timestamp, "bar close"),
                    ) < invalid_position
                ]
            final_status = SMCV2PrimitiveStatus.INVALID
            counts["INVALID_GROUPS"] += 1

        grouped = {day: tuple(item for item in valid_observations if item.trade_date == day) for day in requested}
        for day in requested:
            if day not in eligible_days:
                continue
            group = grouped[day]
            local = tuple((item, item.bar_open_timestamp.astimezone(ZoneInfo(_TIMEZONE_NAME))) for item in group)
            range_source = tuple(item for item, local_open in local if local_open.date() == day and (local_open.hour, local_open.minute) in ((7, 0), (7, 5), (7, 10), (7, 15), (7, 20), (7, 25)))
            if len(range_source) < 6:
                has_later_evidence = any(
                    local_open.date() == day
                    and local_open.time().replace(tzinfo=None) >= time(7, 30)
                    for _, local_open in local
                )
                if has_later_evidence:
                    reasons.add("INVALID_OPENING_RANGE")
                    final_status = SMCV2PrimitiveStatus.INVALID
                    counts["INVALID_GROUPS"] += 1
                else:
                    reasons.add("INCOMPLETE_OPENING_RANGE")
                    if final_status is None:
                        final_status = SMCV2PrimitiveStatus.UNKNOWN
                continue
            if (
                len(range_source) != 6
                or len({(item.segment_ordinal, item.segment_id, item.contract, item.trade_date) for item in range_source}) != 1
                or any(
                    range_source[index].index + 1 != range_source[index + 1].index
                    or range_source[index].bar_close_timestamp != range_source[index + 1].bar_open_timestamp
                    for index in range(5)
                )
            ):
                reasons.add("INVALID_OPENING_RANGE")
                final_status = SMCV2PrimitiveStatus.INVALID
                counts["INVALID_GROUPS"] += 1
                continue
            high = max(item.high_tick for item in range_source)
            low = min(item.low_tick for item in range_source)
            width = high - low
            midpoint = _exact_midpoint(high, low)
            if width <= 0:
                reasons.add("INVALID_OPENING_RANGE")
                final_status = SMCV2PrimitiveStatus.INVALID
                continue
            last = range_source[-1]
            range_id = make_gc_ny_am_sweep_reclaim_id(
                identity_kind=GCNYAMSweepReclaimIdentityKind.OPENING_RANGE, **common,
                segment_ordinal=last.segment_ordinal, segment_id=last.segment_id, contract=last.contract,
                trade_date=day, source_observation_ids=tuple(item.observation_id for item in range_source),
                source_context_ids=tuple(item.kill_zone_context_id for item in range_source),
                source_snapshot_ids=tuple(item.kill_zone_snapshot_id for item in range_source),
                first_known_index=last.index, first_known_timestamp=last.bar_close_timestamp,
                high_tick=high, low_tick=low, midpoint_tick=midpoint, width_ticks=width,
            )
            range_item = GCNYAMSweepReclaimOpeningRange(
                range_id, last.segment_ordinal, last.segment_id, last.contract, day,
                tuple(item.observation_id for item in range_source), tuple(item.kill_zone_context_id for item in range_source),
                tuple(item.kill_zone_snapshot_id for item in range_source), last.index,
                last.bar_close_timestamp, high, low, midpoint, width,
            )
            ranges.append(range_item)
            counts["COMPLETE_OPENING_RANGES"] += 1
            membership = (last.segment_ordinal, last.segment_id, last.contract, last.trade_date)
            formations = tuple(
                item for item, local_open in local
                if (item.segment_ordinal, item.segment_id, item.contract, item.trade_date) == membership
                and time(7, 30) <= local_open.time().replace(tzinfo=None) < time(9, 0)
            )
            candidate_source: GCNYAMSweepReclaimObservation | None = None
            direction_value: SMCV2Direction | None = None
            opposing_ambiguity = False
            for item in formations:
                upper_sweep = item.high_tick >= high + 1
                lower_sweep = item.low_tick <= low - 1
                if upper_sweep and lower_sweep:
                    opposing_ambiguity = True
                    break
                if upper_sweep and midpoint < item.close_tick <= high:
                    candidate_source, direction_value = item, SMCV2Direction.BEARISH
                    break
                if lower_sweep and low <= item.close_tick < midpoint:
                    candidate_source, direction_value = item, SMCV2Direction.BULLISH
                    break
            if opposing_ambiguity:
                reasons.add("AMBIGUOUS_SWEEP_RECLAIM")
                counts["AMBIGUOUS_SWEEP_GROUPS"] += 1
                if final_status is not SMCV2PrimitiveStatus.INVALID:
                    final_status = SMCV2PrimitiveStatus.AMBIGUOUS
                continue
            if candidate_source is None or direction_value is None:
                reasons.add("NO_SWEEP_RECLAIM")
                counts["NO_SWEEP_RECLAIM_TRADE_DATES"] += 1
                continue
            boundary = low if direction_value is SMCV2Direction.BULLISH else high
            extreme = candidate_source.low_tick if direction_value is SMCV2Direction.BULLISH else candidate_source.high_tick
            invalidation = extreme - 1 if direction_value is SMCV2Direction.BULLISH else extreme + 1
            candidate_id = make_gc_ny_am_sweep_reclaim_id(
                identity_kind=GCNYAMSweepReclaimIdentityKind.CANDIDATE, **common, range_id=range_id,
                segment_ordinal=candidate_source.segment_ordinal, segment_id=candidate_source.segment_id,
                contract=candidate_source.contract, trade_date=day, direction=direction_value,
                formation_observation_id=candidate_source.observation_id,
                formation_context_id=candidate_source.kill_zone_context_id,
                formation_snapshot_id=candidate_source.kill_zone_snapshot_id,
                formation_index=candidate_source.index, first_known_timestamp=candidate_source.bar_close_timestamp,
                swept_boundary_tick=boundary, sweep_extreme_tick=extreme,
                reclaim_close_tick=candidate_source.close_tick, midpoint_tick=midpoint,
                invalidation_tick=invalidation, width_ticks=width,
            )
            candidate = GCNYAMSweepReclaimCandidate(
                candidate_id, range_id, candidate_source.segment_ordinal, candidate_source.segment_id,
                candidate_source.contract, day, direction_value, candidate_source.observation_id,
                candidate_source.kill_zone_context_id, candidate_source.kill_zone_snapshot_id,
                candidate_source.index, candidate_source.bar_close_timestamp, boundary, extreme,
                candidate_source.close_tick, midpoint, invalidation, width,
            )
            candidates.append(candidate)
            counts["COMPLETE_CANDIDATES"] += 1
            counts["BULLISH_CANDIDATES" if direction_value is SMCV2Direction.BULLISH else "BEARISH_CANDIDATES"] += 1
            later = tuple(
                item for item in group
                if (item.segment_ordinal, item.segment_id, item.contract, item.trade_date) == membership
                and item.index > candidate_source.index
            )[:12]
            if any(
                previous.index + 1 != current.index
                or previous.bar_close_timestamp != current.bar_open_timestamp
                for previous, current in zip((candidate_source,) + later, later)
            ):
                reasons.add("INVALID_OUTCOME_EVIDENCE")
                final_status = SMCV2PrimitiveStatus.INVALID
                counts["INVALID_GROUPS"] += 1
                continue
            selected: GCNYAMSweepReclaimOutcomeType | None = None
            event: GCNYAMSweepReclaimObservation | None = None
            horizon: list[GCNYAMSweepReclaimObservation] = []
            for item in later:
                horizon.append(item)
                target_hit = item.high_tick >= midpoint if direction_value is SMCV2Direction.BULLISH else item.low_tick <= midpoint
                invalid_hit = item.close_tick <= invalidation if direction_value is SMCV2Direction.BULLISH else item.close_tick >= invalidation
                if target_hit or invalid_hit:
                    selected = GCNYAMSweepReclaimOutcomeType.SAME_BAR_AMBIGUOUS if target_hit and invalid_hit else (GCNYAMSweepReclaimOutcomeType.MIDPOINT_REACHED if target_hit else GCNYAMSweepReclaimOutcomeType.INVALIDATED)
                    event = item
                    break
            if selected is None:
                if len(later) < 12:
                    reasons.add("INCOMPLETE_OUTCOME_HORIZON")
                    counts["INCOMPLETE_HORIZONS"] += 1
                    if final_status is None:
                        final_status = SMCV2PrimitiveStatus.UNKNOWN
                    continue
                selected = GCNYAMSweepReclaimOutcomeType.TIMEOUT
                horizon = list(later)
                first_known = later[-1]
            else:
                first_known = event
            outcome_id = make_gc_ny_am_sweep_reclaim_id(
                identity_kind=GCNYAMSweepReclaimIdentityKind.OUTCOME, **common, candidate_id=candidate_id,
                outcome=selected, first_known_index=first_known.index, first_known_timestamp=first_known.bar_close_timestamp,
                horizon_observation_ids=tuple(item.observation_id for item in horizon),
                event_observation_id=event.observation_id if event is not None else None,
            )
            outcomes.append(GCNYAMSweepReclaimOutcome(
                outcome_id, candidate_id, selected, first_known.index, first_known.bar_close_timestamp,
                tuple(item.observation_id for item in horizon), event.observation_id if event is not None else None,
            ))
            counts[f"{selected.value}_OUTCOMES"] += 1
            counts["COMPLETE_OUTCOMES"] += 1
        ordered_ranges = tuple(sorted(ranges, key=lambda item: (item.trade_date, item.segment_ordinal, item.first_known_index, _timestamp(item.first_known_timestamp, "timestamp"))))
        ordered_candidates = tuple(sorted(candidates, key=lambda item: (item.trade_date, item.segment_ordinal, item.formation_index, _timestamp(item.first_known_timestamp, "timestamp"), item.direction.value)))
        outcome_map = {item.candidate_id: item for item in outcomes}
        ordered_outcomes = tuple(outcome_map[item.candidate_id] for item in ordered_candidates if item.candidate_id in outcome_map)
        reason_tuple = _ordered_reasons(reasons)
        if final_status is not None:
            status = final_status
        elif ordered_candidates and len(ordered_outcomes) == len(ordered_candidates):
            status = SMCV2PrimitiveStatus.VALID
        elif not ordered_candidates:
            status = SMCV2PrimitiveStatus.NONE
        else:
            status = SMCV2PrimitiveStatus.UNKNOWN
            reasons.add("INCOMPLETE_OUTCOME_HORIZON")
            reason_tuple = _ordered_reasons(reasons)
        manifest_output = _make_manifest(common, requested, ordered_ranges, ordered_candidates, ordered_outcomes, counts, reason_tuple) if status in (SMCV2PrimitiveStatus.VALID, SMCV2PrimitiveStatus.NONE) else None
        return GCNYAMSweepReclaimResult(status, ordered_ranges, ordered_candidates, ordered_outcomes, manifest_output, reason_tuple, reason_tuple if status in (SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.UNKNOWN, SMCV2PrimitiveStatus.AMBIGUOUS) else ())
    except _EvidenceError as exc:
        reasons.add(exc.reason)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError, InvalidOperation, OverflowError, OSError):
        reasons.add("INVALID_DATASET")
    reason_tuple = _ordered_reasons(reasons)
    return GCNYAMSweepReclaimResult(SMCV2PrimitiveStatus.INVALID, tuple(ranges), tuple(candidates), tuple(outcomes), None, reason_tuple, reason_tuple)


def _calendar_version_fallback(entries: tuple[Any, ...]) -> str:
    values = _tuple(entries, "calendar entries")
    if not values:
        raise _EvidenceError("INVALID_DATASET")
    return _text(values[0].calendar_version, "calendar_version")
