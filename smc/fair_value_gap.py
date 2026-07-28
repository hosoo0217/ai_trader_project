"""Deterministic standalone Fair Value Gap diagnostics.

This module is intentionally isolated from strategy, risk, execution, runtime
registration, and current SMC integration paths. It consumes only immutable,
fully closed, integer-tick evidence supplied directly by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from smc.dealing_range import DealingRangeEventType
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


FAIR_VALUE_GAP_DETECTOR_VERSION = "SMC-V2-FAIR-VALUE-GAP-1"

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY_KINDS = frozenset({"GAP", "TRANSITION", "SNAPSHOT"})
_REASON_FORMATION = "FORMATION_CONFIRMED"
_REASON_TOUCH = "WICK_TOUCH"
_REASON_PARTIAL = "PARTIAL_FILL"
_REASON_MIDPOINT = "MIDPOINT_FILL"
_REASON_FULL = "FULL_FILL"
_REASON_INVALIDATION = "CLOSE_THROUGH_INVALIDATION"
_REASONS = frozenset(
    {
        _REASON_FORMATION,
        _REASON_TOUCH,
        _REASON_PARTIAL,
        _REASON_MIDPOINT,
        _REASON_FULL,
        _REASON_INVALIDATION,
    }
)
_Moment = tuple[int, datetime]


class FairValueGapState(str, Enum):
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    MIDPOINT_FILLED = "MIDPOINT_FILLED"
    FULLY_FILLED = "FULLY_FILLED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class FairValueGapCandle:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class FairValueGapContextLink:
    formation_end_index: int
    formation_end_timestamp: datetime
    displacement_id: str | None
    structure_event_id: str | None
    structure_event_type: DealingRangeEventType | None


@dataclass(frozen=True)
class FairValueGap:
    gap_id: str
    direction: SMCV2Direction
    source_indices: tuple[int, int, int]
    source_timestamps: tuple[datetime, datetime, datetime]
    lower_tick: int
    upper_tick: int
    midpoint_tick: Decimal
    formation_end_index: int
    formation_end_timestamp: datetime
    displacement_id: str | None
    structure_event_id: str | None
    structure_event_type: DealingRangeEventType | None


@dataclass(frozen=True)
class FairValueGapTransition:
    transition_id: str
    gap_id: str
    from_state: FairValueGapState | None
    to_state: FairValueGapState
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class FairValueGapSnapshot:
    snapshot_id: str
    gap_id: str
    direction: SMCV2Direction
    state: FairValueGapState
    index: int
    timestamp: datetime
    transition_ids: tuple[str, ...]


@dataclass(frozen=True)
class FairValueGapResult:
    status: SMCV2PrimitiveStatus
    gaps: tuple[FairValueGap, ...] = ()
    transitions: tuple[FairValueGapTransition, ...] = ()
    snapshots: tuple[FairValueGapSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _CandleRecord:
    value: FairValueGapCandle
    moment: _Moment


@dataclass(frozen=True)
class _LinkRecord:
    value: FairValueGapContextLink
    moment: _Moment


@dataclass(frozen=True)
class _Issue:
    moment: _Moment | None
    reason: str


@dataclass(frozen=True)
class _GapRuntime:
    gap: FairValueGap
    state: FairValueGapState
    transition_ids: tuple[str, ...]
    last_index: int
    last_timestamp: datetime


@dataclass
class _AnalysisState:
    gaps: list[FairValueGap]
    transitions: list[FairValueGapTransition]
    snapshots: list[FairValueGapSnapshot]
    runtimes: dict[str, _GapRuntime]

    def clone(self) -> _AnalysisState:
        return _AnalysisState(
            gaps=list(self.gaps),
            transitions=list(self.transitions),
            snapshots=list(self.snapshots),
            runtimes=dict(self.runtimes),
        )


class _InvalidGroup(ValueError):
    pass


class _AmbiguousGroup(ValueError):
    pass


def make_fair_value_gap_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...] = (),
    source_timestamps: tuple[datetime, ...] = (),
    boundaries: SMCV2TickRange | None = None,
    midpoint_tick: Decimal | None = None,
    formation_end_index: int | None = None,
    formation_end_timestamp: datetime | None = None,
    displacement_id: str | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    gap_id: str | None = None,
    from_state: FairValueGapState | None = None,
    to_state: FairValueGapState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: FairValueGapState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    """Build one canonical kind-specific Fair Value Gap identity."""

    try:
        return _make_fair_value_gap_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_indices=source_indices,
            source_timestamps=source_timestamps,
            boundaries=boundaries,
            midpoint_tick=midpoint_tick,
            formation_end_index=formation_end_index,
            formation_end_timestamp=formation_end_timestamp,
            displacement_id=displacement_id,
            structure_event_id=structure_event_id,
            structure_event_type=structure_event_type,
            gap_id=gap_id,
            from_state=from_state,
            to_state=to_state,
            effective_index=effective_index,
            effective_timestamp=effective_timestamp,
            reason=reason,
            state=state,
            transition_ids=transition_ids,
        )
    except (AttributeError, KeyError, IndexError) as exc:
        raise ValueError("identity input is internally malformed") from exc


def _make_fair_value_gap_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...],
    source_timestamps: tuple[datetime, ...],
    boundaries: SMCV2TickRange | None,
    midpoint_tick: Decimal | None,
    formation_end_index: int | None,
    formation_end_timestamp: datetime | None,
    displacement_id: str | None,
    structure_event_id: str | None,
    structure_event_type: DealingRangeEventType | None,
    gap_id: str | None,
    from_state: FairValueGapState | None,
    to_state: FairValueGapState | None,
    effective_index: int | None,
    effective_timestamp: datetime | None,
    reason: str | None,
    state: FairValueGapState | None,
    transition_ids: tuple[str, ...],
) -> str:
    if not isinstance(identity_kind, str) or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked Fair Value Gap identity kind")
    canonical_instrument = _normalize_text(instrument, name="instrument")
    canonical_timeframe = _normalize_text(timeframe, name="timeframe")
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")

    payload: dict[str, object] = {
        "detector_version": FAIR_VALUE_GAP_DETECTOR_VERSION,
        "direction": direction.value,
        "identity_kind": identity_kind,
        "instrument": canonical_instrument,
        "timeframe": canonical_timeframe,
    }

    if identity_kind == "GAP":
        canonical_indices = _validate_source_indices(
            source_indices,
            exact_length=3,
        )
        canonical_timestamps = _validate_source_timestamps(
            source_timestamps,
            exact_length=3,
        )
        lower_tick, upper_tick = _validate_boundaries(boundaries)
        midpoint = _validate_midpoint(
            midpoint_tick,
            lower_tick=lower_tick,
            upper_tick=upper_tick,
        )
        _validate_non_negative_int(
            formation_end_index,
            name="formation_end_index",
        )
        canonical_formation_timestamp = _normalize_timestamp(
            formation_end_timestamp,
            name="formation_end_timestamp",
        )
        if formation_end_index != canonical_indices[-1]:
            raise ValueError("formation_end_index must equal the third source index")
        if canonical_formation_timestamp != canonical_timestamps[-1]:
            raise ValueError(
                "formation_end_timestamp must equal the third source timestamp"
            )
        _validate_optional_hash(displacement_id, name="displacement_id")
        _validate_structure_pair(
            structure_event_id,
            structure_event_type,
        )
        _require_defaults(
            gap_id=gap_id,
            from_state=from_state,
            to_state=to_state,
            effective_index=effective_index,
            effective_timestamp=effective_timestamp,
            reason=reason,
            state=state,
            transition_ids=transition_ids,
        )
        payload.update(
            {
                "boundaries": [lower_tick, upper_tick],
                "displacement_id": displacement_id,
                "formation_end_index": formation_end_index,
                "formation_end_timestamp": _timestamp_text(
                    canonical_formation_timestamp
                ),
                "midpoint_tick": _decimal_text(midpoint),
                "source_indices": list(canonical_indices),
                "source_timestamps": [
                    _timestamp_text(timestamp)
                    for timestamp in canonical_timestamps
                ],
                "structure_event_id": structure_event_id,
                "structure_event_type": (
                    structure_event_type.value
                    if structure_event_type is not None
                    else None
                ),
            }
        )
    elif identity_kind == "TRANSITION":
        _require_defaults(
            source_indices=source_indices,
            source_timestamps=source_timestamps,
            boundaries=boundaries,
            midpoint_tick=midpoint_tick,
            formation_end_index=formation_end_index,
            formation_end_timestamp=formation_end_timestamp,
            displacement_id=displacement_id,
            structure_event_id=structure_event_id,
            structure_event_type=structure_event_type,
            state=state,
            transition_ids=transition_ids,
        )
        _validate_hash(gap_id, name="gap_id")
        _validate_transition_edge(from_state, to_state, reason)
        _validate_non_negative_int(effective_index, name="effective_index")
        canonical_effective_timestamp = _normalize_timestamp(
            effective_timestamp,
            name="effective_timestamp",
        )
        assert to_state is not None
        assert reason is not None
        payload.update(
            {
                "effective_index": effective_index,
                "effective_timestamp": _timestamp_text(
                    canonical_effective_timestamp
                ),
                "from_state": from_state.value if from_state is not None else None,
                "gap_id": gap_id,
                "reason": reason,
                "to_state": to_state.value,
            }
        )
    else:
        _require_defaults(
            source_indices=source_indices,
            source_timestamps=source_timestamps,
            boundaries=boundaries,
            midpoint_tick=midpoint_tick,
            formation_end_index=formation_end_index,
            formation_end_timestamp=formation_end_timestamp,
            displacement_id=displacement_id,
            structure_event_id=structure_event_id,
            structure_event_type=structure_event_type,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )
        _validate_hash(gap_id, name="gap_id")
        if not isinstance(state, FairValueGapState):
            raise TypeError("state must be a FairValueGapState")
        _validate_non_negative_int(effective_index, name="effective_index")
        canonical_effective_timestamp = _normalize_timestamp(
            effective_timestamp,
            name="effective_timestamp",
        )
        canonical_transition_ids = _validate_hash_tuple(
            transition_ids,
            name="transition_ids",
            allow_empty=False,
        )
        if len(set(canonical_transition_ids)) != len(canonical_transition_ids):
            raise ValueError("transition_ids must not contain duplicates")
        payload.update(
            {
                "effective_index": effective_index,
                "effective_timestamp": _timestamp_text(
                    canonical_effective_timestamp
                ),
                "gap_id": gap_id,
                "state": state.value,
                "transition_ids": list(canonical_transition_ids),
            }
        )

    canonical_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def analyze_fair_value_gaps(
    *,
    instrument: str,
    timeframe: str,
    candles: tuple[FairValueGapCandle, ...] | None,
    context_links: tuple[FairValueGapContextLink, ...] | None,
) -> FairValueGapResult:
    """Analyze immutable closed-candle evidence without runtime integration."""

    if candles is None or context_links is None:
        missing = []
        if candles is None:
            missing.append("candles")
        if context_links is None:
            missing.append("context_links")
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return FairValueGapResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    try:
        canonical_instrument = _normalize_text(instrument, name="instrument")
        canonical_timeframe = _normalize_text(timeframe, name="timeframe")
        candle_records, candle_issue = _collect_candles(candles)
        link_records, link_issue = _collect_links(context_links)
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return _empty_result(
            SMCV2PrimitiveStatus.INVALID,
            reason=f"Invalid Fair Value Gap input: {exc}",
        )

    issues = tuple(
        issue for issue in (candle_issue, link_issue) if issue is not None
    )
    if any(issue.moment is None for issue in issues):
        issue = next(issue for issue in issues if issue.moment is None)
        return _empty_result(
            SMCV2PrimitiveStatus.INVALID,
            reason=issue.reason,
        )

    candle_by_index = {
        record.moment[0]: record.moment for record in candle_records
    }
    candle_by_timestamp = {
        record.moment[1]: record.moment for record in candle_records
    }
    reconciled_link_records: list[_LinkRecord] = []
    dangling_issues: list[_Issue] = []
    for record in link_records:
        if record.moment in {
            candle_by_index.get(record.moment[0]),
            candle_by_timestamp.get(record.moment[1]),
        } and (
            candle_by_index.get(record.moment[0]) == record.moment
            and candle_by_timestamp.get(record.moment[1]) == record.moment
        ):
            reconciled_link_records.append(record)
            continue
        cutoff = (
            candle_by_index.get(record.moment[0])
            or candle_by_timestamp.get(record.moment[1])
            or record.moment
        )
        dangling_issues.append(
            _Issue(
                moment=cutoff,
                reason="Context link does not match an exact candle effective moment",
            )
        )

    all_issues = (*issues, *dangling_issues)
    cutoff_issue: _Issue | None = None
    if all_issues:
        cutoff_issue = min(
            all_issues,
            key=lambda issue: issue.moment,
        )
        assert cutoff_issue.moment is not None

    state = _AnalysisState(
        gaps=[],
        transitions=[],
        snapshots=[],
        runtimes={},
    )
    links_by_moment: dict[_Moment, list[FairValueGapContextLink]] = {}
    for record in reconciled_link_records:
        if cutoff_issue is None or record.moment < cutoff_issue.moment:
            links_by_moment.setdefault(record.moment, []).append(record.value)

    consumed_link_moments: set[_Moment] = set()
    processed_candles: list[FairValueGapCandle] = []
    for record in candle_records:
        if cutoff_issue is not None and record.moment >= cutoff_issue.moment:
            break
        candidate = state.clone()
        links = tuple(links_by_moment.get(record.moment, ()))
        try:
            _advance_existing_gaps(
                candidate,
                record.value,
                instrument=canonical_instrument,
                timeframe=canonical_timeframe,
            )
            window = (
                (*processed_candles[-2:], record.value)
                if len(processed_candles) >= 2
                else ()
            )
            _evaluate_formation(
                candidate,
                window,
                links,
                instrument=canonical_instrument,
                timeframe=canonical_timeframe,
            )
        except _InvalidGroup as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.INVALID,
                reason=str(exc),
            )
        except _AmbiguousGroup as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.AMBIGUOUS,
                reason=str(exc),
            )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.INVALID,
                reason=f"Invalid Fair Value Gap group: {exc}",
            )
        state = candidate
        processed_candles.append(record.value)
        if links:
            consumed_link_moments.add(record.moment)

    unconsumed = [
        moment
        for moment in links_by_moment
        if moment not in consumed_link_moments
    ]
    if unconsumed:
        return _state_result(
            state,
            status=SMCV2PrimitiveStatus.INVALID,
            reason="Context link is dangling from every qualifying formation",
        )
    if cutoff_issue is not None:
        return _state_result(
            state,
            status=SMCV2PrimitiveStatus.INVALID,
            reason=cutoff_issue.reason,
        )

    status = (
        SMCV2PrimitiveStatus.VALID
        if state.gaps
        else SMCV2PrimitiveStatus.NONE
    )
    reason = (
        "Fair Value Gap diagnostics emitted"
        if status is SMCV2PrimitiveStatus.VALID
        else "No qualifying Fair Value Gap formation was found"
    )
    return _state_result(
        state,
        status=status,
        reason=reason,
        blocking=False,
    )


def _normalize_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _normalize_timestamp(value: object, *, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    try:
        return normalize_utc_timestamp(value)
    except (TypeError, ValueError) as exc:
        raise type(exc)(f"{name}: {exc}") from exc


def _timestamp_text(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_hash(value: object, *, name: str) -> None:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 value")


def _validate_optional_hash(value: object, *, name: str) -> None:
    if value is not None:
        _validate_hash(value, name=name)


def _validate_hash_tuple(
    values: object,
    *,
    name: str,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    if not allow_empty and not values:
        raise ValueError(f"{name} cannot be empty")
    for value in values:
        _validate_hash(value, name=name)
    return values


def _validate_non_negative_int(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _validate_tick(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer tick")


def _validate_source_indices(
    values: object,
    *,
    exact_length: int,
) -> tuple[int, ...]:
    if not isinstance(values, tuple):
        raise TypeError("source_indices must be a tuple")
    if len(values) != exact_length:
        raise ValueError(f"source_indices must contain exactly {exact_length} values")
    for value in values:
        _validate_non_negative_int(value, name="source_indices")
    if any(earlier >= later for earlier, later in zip(values, values[1:])):
        raise ValueError("source_indices must be independently strictly increasing")
    return values


def _validate_source_timestamps(
    values: object,
    *,
    exact_length: int,
) -> tuple[datetime, ...]:
    if not isinstance(values, tuple):
        raise TypeError("source_timestamps must be a tuple")
    if len(values) != exact_length:
        raise ValueError(
            f"source_timestamps must contain exactly {exact_length} values"
        )
    normalized = tuple(
        _normalize_timestamp(value, name="source_timestamps")
        for value in values
    )
    if any(
        earlier >= later
        for earlier, later in zip(normalized, normalized[1:])
    ):
        raise ValueError(
            "source_timestamps must be independently strictly increasing"
        )
    return normalized


def _validate_boundaries(value: object) -> tuple[int, int]:
    if not isinstance(value, SMCV2TickRange):
        raise TypeError("boundaries must be an SMCV2TickRange")
    try:
        lower_tick = value.lower_tick
        upper_tick = value.upper_tick
    except AttributeError as exc:
        raise TypeError("boundaries is internally malformed") from exc
    _validate_tick(lower_tick, name="boundaries.lower_tick")
    _validate_tick(upper_tick, name="boundaries.upper_tick")
    if upper_tick - lower_tick < 2:
        raise ValueError("boundaries must have a minimum two-tick width")
    return lower_tick, upper_tick


def _exact_midpoint(lower_tick: int, upper_tick: int) -> Decimal:
    total = lower_tick + upper_tick
    if total % 2 == 0:
        return Decimal(total // 2)
    sign = "-" if total < 0 else ""
    absolute = abs(total)
    return Decimal(f"{sign}{absolute // 2}.5")


def _validate_midpoint(
    value: object,
    *,
    lower_tick: int,
    upper_tick: int,
) -> Decimal:
    if not isinstance(value, Decimal):
        raise TypeError("midpoint_tick must be a Decimal")
    if not value.is_finite():
        raise ValueError("midpoint_tick must be finite")
    expected = _exact_midpoint(lower_tick, upper_tick)
    if value != expected:
        raise ValueError("midpoint_tick does not match the exact gap midpoint")
    return value


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if "." in text else f"{text}.0"


def _validate_structure_pair(
    structure_event_id: object,
    structure_event_type: object,
) -> None:
    if (structure_event_id is None) != (structure_event_type is None):
        raise ValueError(
            "structure_event_id and structure_event_type must be paired"
        )
    if structure_event_id is None:
        return
    _validate_hash(structure_event_id, name="structure_event_id")
    if not isinstance(structure_event_type, DealingRangeEventType):
        raise TypeError("structure_event_type must be a DealingRangeEventType")
    if structure_event_type not in (
        DealingRangeEventType.BOS,
        DealingRangeEventType.CHOCH,
    ):
        raise ValueError("structure_event_type must be BOS or CHOCH")


def _require_defaults(**values: object) -> None:
    for name, value in values.items():
        expected = (
            ()
            if name in {"source_indices", "source_timestamps", "transition_ids"}
            else None
        )
        if value != expected:
            raise ValueError(f"{name} is forbidden for this identity kind")


def _validate_transition_edge(
    from_state: object,
    to_state: object,
    reason: object,
) -> None:
    if from_state is not None and not isinstance(from_state, FairValueGapState):
        raise TypeError("from_state must be a FairValueGapState or None")
    if not isinstance(to_state, FairValueGapState):
        raise TypeError("to_state must be a FairValueGapState")
    if not isinstance(reason, str) or reason not in _REASONS:
        raise ValueError("reason is not a locked Fair Value Gap transition reason")

    if from_state is None:
        if to_state is not FairValueGapState.ACTIVE or reason != _REASON_FORMATION:
            raise ValueError("initial transition must be formation to ACTIVE")
        return

    allowed: dict[FairValueGapState, frozenset[FairValueGapState]] = {
        FairValueGapState.ACTIVE: frozenset(
            {
                FairValueGapState.TOUCHED,
                FairValueGapState.PARTIALLY_FILLED,
                FairValueGapState.MIDPOINT_FILLED,
                FairValueGapState.FULLY_FILLED,
                FairValueGapState.INVALIDATED,
            }
        ),
        FairValueGapState.TOUCHED: frozenset(
            {
                FairValueGapState.PARTIALLY_FILLED,
                FairValueGapState.MIDPOINT_FILLED,
                FairValueGapState.FULLY_FILLED,
                FairValueGapState.INVALIDATED,
            }
        ),
        FairValueGapState.PARTIALLY_FILLED: frozenset(
            {
                FairValueGapState.MIDPOINT_FILLED,
                FairValueGapState.FULLY_FILLED,
                FairValueGapState.INVALIDATED,
            }
        ),
        FairValueGapState.MIDPOINT_FILLED: frozenset(
            {
                FairValueGapState.FULLY_FILLED,
                FairValueGapState.INVALIDATED,
            }
        ),
        FairValueGapState.FULLY_FILLED: frozenset(),
        FairValueGapState.INVALIDATED: frozenset(),
    }
    if to_state not in allowed[from_state]:
        raise ValueError("transition is not in the locked lifecycle graph")
    expected_reason = {
        FairValueGapState.TOUCHED: _REASON_TOUCH,
        FairValueGapState.PARTIALLY_FILLED: _REASON_PARTIAL,
        FairValueGapState.MIDPOINT_FILLED: _REASON_MIDPOINT,
        FairValueGapState.FULLY_FILLED: _REASON_FULL,
        FairValueGapState.INVALIDATED: _REASON_INVALIDATION,
    }[to_state]
    if reason != expected_reason:
        raise ValueError("transition reason contradicts the target state")


def _safe_candle_moment(value: object) -> _Moment | None:
    try:
        index = value.index
        timestamp = value.timestamp
    except AttributeError:
        return None
    if type(index) is not int or index < 0:
        return None
    try:
        normalized = _normalize_timestamp(timestamp, name="candle.timestamp")
    except (TypeError, ValueError, AttributeError):
        return None
    return index, normalized


def _validate_candle(value: object) -> _CandleRecord:
    if not isinstance(value, FairValueGapCandle):
        raise TypeError("candles must contain only FairValueGapCandle values")
    try:
        index = value.index
        timestamp = value.timestamp
        open_tick = value.open_tick
        high_tick = value.high_tick
        low_tick = value.low_tick
        close_tick = value.close_tick
    except AttributeError as exc:
        raise TypeError("FairValueGapCandle is internally malformed") from exc
    _validate_non_negative_int(index, name="candle.index")
    normalized_timestamp = _normalize_timestamp(
        timestamp,
        name="candle.timestamp",
    )
    for name, tick in (
        ("open_tick", open_tick),
        ("high_tick", high_tick),
        ("low_tick", low_tick),
        ("close_tick", close_tick),
    ):
        _validate_tick(tick, name=f"candle.{name}")
    if low_tick > high_tick:
        raise ValueError("candle.low_tick cannot exceed candle.high_tick")
    if not low_tick <= open_tick <= high_tick:
        raise ValueError("candle.open_tick must lie inside its range")
    if not low_tick <= close_tick <= high_tick:
        raise ValueError("candle.close_tick must lie inside its range")
    normalized = FairValueGapCandle(
        index=index,
        timestamp=normalized_timestamp,
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
    )
    return _CandleRecord(normalized, (index, normalized_timestamp))


def _collect_candles(
    values: object,
) -> tuple[tuple[_CandleRecord, ...], _Issue | None]:
    if not isinstance(values, tuple):
        raise TypeError("candles must be a tuple")
    records: list[_CandleRecord] = []
    previous: _Moment | None = None
    for value in values:
        safe_moment = _safe_candle_moment(value)
        try:
            record = _validate_candle(value)
            if previous is not None:
                if record.moment[0] <= previous[0]:
                    raise ValueError(
                        "candle indices must be independently strictly increasing"
                    )
                if record.moment[1] <= previous[1]:
                    raise ValueError(
                        "candle timestamps must be independently strictly increasing"
                    )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(records), _Issue(
                moment=safe_moment,
                reason=f"Invalid Fair Value Gap candle: {exc}",
            )
        records.append(record)
        previous = record.moment
    return tuple(records), None


def _safe_link_moment(value: object) -> _Moment | None:
    try:
        index = value.formation_end_index
        timestamp = value.formation_end_timestamp
    except AttributeError:
        return None
    if type(index) is not int or index < 0:
        return None
    try:
        normalized = _normalize_timestamp(
            timestamp,
            name="context_link.formation_end_timestamp",
        )
    except (TypeError, ValueError, AttributeError):
        return None
    return index, normalized


def _validate_link(value: object) -> _LinkRecord:
    if not isinstance(value, FairValueGapContextLink):
        raise TypeError(
            "context_links must contain only FairValueGapContextLink values"
        )
    try:
        formation_end_index = value.formation_end_index
        formation_end_timestamp = value.formation_end_timestamp
        displacement_id = value.displacement_id
        structure_event_id = value.structure_event_id
        structure_event_type = value.structure_event_type
    except AttributeError as exc:
        raise TypeError("FairValueGapContextLink is internally malformed") from exc
    _validate_non_negative_int(
        formation_end_index,
        name="context_link.formation_end_index",
    )
    normalized_timestamp = _normalize_timestamp(
        formation_end_timestamp,
        name="context_link.formation_end_timestamp",
    )
    _validate_optional_hash(displacement_id, name="displacement_id")
    _validate_structure_pair(structure_event_id, structure_event_type)
    if displacement_id is None and structure_event_id is None:
        raise ValueError("context link must contain displacement or structure metadata")
    normalized = FairValueGapContextLink(
        formation_end_index=formation_end_index,
        formation_end_timestamp=normalized_timestamp,
        displacement_id=displacement_id,
        structure_event_id=structure_event_id,
        structure_event_type=structure_event_type,
    )
    return _LinkRecord(
        normalized,
        (formation_end_index, normalized_timestamp),
    )


def _collect_links(
    values: object,
) -> tuple[tuple[_LinkRecord, ...], _Issue | None]:
    if not isinstance(values, tuple):
        raise TypeError("context_links must be a tuple")
    records: list[_LinkRecord] = []
    previous: _Moment | None = None
    for value in values:
        safe_moment = _safe_link_moment(value)
        try:
            record = _validate_link(value)
            if previous is not None:
                if record.moment[0] < previous[0]:
                    raise ValueError("context-link indices must be nondecreasing")
                if record.moment[1] < previous[1]:
                    raise ValueError("context-link timestamps must be nondecreasing")
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(records), _Issue(
                moment=safe_moment,
                reason=f"Invalid Fair Value Gap context link: {exc}",
            )
        records.append(record)
        previous = record.moment
    return tuple(records), None


def _middle_ratio_qualifies(candle: FairValueGapCandle) -> bool:
    full_range = candle.high_tick - candle.low_tick
    if full_range == 0:
        return False
    real_body = abs(candle.close_tick - candle.open_tick)
    return 5 * real_body >= 3 * full_range


def _formation_values(
    window: tuple[FairValueGapCandle, ...],
) -> tuple[SMCV2Direction, int, int] | None:
    if len(window) != 3:
        return None
    first, middle, third = window
    if not _middle_ratio_qualifies(middle):
        return None
    bullish_size = third.low_tick - first.high_tick
    bearish_size = first.low_tick - third.high_tick
    if bullish_size >= 2:
        return SMCV2Direction.BULLISH, first.high_tick, third.low_tick
    if bearish_size >= 2:
        return SMCV2Direction.BEARISH, third.high_tick, first.low_tick
    return None


def _evaluate_formation(
    state: _AnalysisState,
    window: tuple[FairValueGapCandle, ...],
    links: tuple[FairValueGapContextLink, ...],
    *,
    instrument: str,
    timeframe: str,
) -> None:
    formation = _formation_values(window)
    if formation is None:
        if links:
            raise _InvalidGroup(
                "Context link is dangling from a qualifying Fair Value Gap"
            )
        return

    if links:
        if len(set(links)) != len(links):
            raise _InvalidGroup("duplicate context links share one formation")
        if len(links) > 1:
            raise _AmbiguousGroup(
                "multiple distinct context links share one formation"
            )
        link = links[0]
    else:
        link = None

    direction, lower_tick, upper_tick = formation
    first, middle, third = window
    source_indices = (first.index, middle.index, third.index)
    source_timestamps = (
        first.timestamp,
        middle.timestamp,
        third.timestamp,
    )
    midpoint = _exact_midpoint(lower_tick, upper_tick)
    gap_id = make_fair_value_gap_id(
        identity_kind="GAP",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_indices=source_indices,
        source_timestamps=source_timestamps,
        boundaries=SMCV2TickRange(lower_tick, upper_tick),
        midpoint_tick=midpoint,
        formation_end_index=third.index,
        formation_end_timestamp=third.timestamp,
        displacement_id=link.displacement_id if link is not None else None,
        structure_event_id=link.structure_event_id if link is not None else None,
        structure_event_type=(
            link.structure_event_type if link is not None else None
        ),
    )
    gap = FairValueGap(
        gap_id=gap_id,
        direction=direction,
        source_indices=source_indices,
        source_timestamps=source_timestamps,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        midpoint_tick=midpoint,
        formation_end_index=third.index,
        formation_end_timestamp=third.timestamp,
        displacement_id=link.displacement_id if link is not None else None,
        structure_event_id=link.structure_event_id if link is not None else None,
        structure_event_type=(
            link.structure_event_type if link is not None else None
        ),
    )
    transition_id = make_fair_value_gap_id(
        identity_kind="TRANSITION",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        gap_id=gap_id,
        from_state=None,
        to_state=FairValueGapState.ACTIVE,
        effective_index=third.index,
        effective_timestamp=third.timestamp,
        reason=_REASON_FORMATION,
    )
    transition = FairValueGapTransition(
        transition_id=transition_id,
        gap_id=gap_id,
        from_state=None,
        to_state=FairValueGapState.ACTIVE,
        index=third.index,
        timestamp=third.timestamp,
        reason=_REASON_FORMATION,
    )
    transition_ids = (transition_id,)
    snapshot_id = make_fair_value_gap_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        gap_id=gap_id,
        effective_index=third.index,
        effective_timestamp=third.timestamp,
        state=FairValueGapState.ACTIVE,
        transition_ids=transition_ids,
    )
    snapshot = FairValueGapSnapshot(
        snapshot_id=snapshot_id,
        gap_id=gap_id,
        direction=direction,
        state=FairValueGapState.ACTIVE,
        index=third.index,
        timestamp=third.timestamp,
        transition_ids=transition_ids,
    )
    state.gaps.append(gap)
    state.transitions.append(transition)
    state.snapshots.append(snapshot)
    state.runtimes[gap_id] = _GapRuntime(
        gap=gap,
        state=FairValueGapState.ACTIVE,
        transition_ids=transition_ids,
        last_index=third.index,
        last_timestamp=third.timestamp,
    )


def _runtime_sort_key(runtime: _GapRuntime) -> tuple[object, ...]:
    gap = runtime.gap
    return (
        gap.formation_end_index,
        gap.formation_end_timestamp,
        gap.direction.value,
        gap.source_indices,
        gap.gap_id,
    )


def _target_state(
    gap: FairValueGap,
    candle: FairValueGapCandle,
) -> FairValueGapState | None:
    if gap.direction is SMCV2Direction.BULLISH:
        if candle.close_tick <= gap.lower_tick - 1:
            return FairValueGapState.INVALIDATED
        if candle.low_tick <= gap.lower_tick:
            return FairValueGapState.FULLY_FILLED
        if Decimal(candle.low_tick) <= gap.midpoint_tick:
            return FairValueGapState.MIDPOINT_FILLED
        if candle.low_tick < gap.upper_tick:
            return FairValueGapState.PARTIALLY_FILLED
        if candle.low_tick == gap.upper_tick:
            return FairValueGapState.TOUCHED
        return None

    if candle.close_tick >= gap.upper_tick + 1:
        return FairValueGapState.INVALIDATED
    if candle.high_tick >= gap.upper_tick:
        return FairValueGapState.FULLY_FILLED
    if Decimal(candle.high_tick) >= gap.midpoint_tick:
        return FairValueGapState.MIDPOINT_FILLED
    if candle.high_tick > gap.lower_tick:
        return FairValueGapState.PARTIALLY_FILLED
    if candle.high_tick == gap.lower_tick:
        return FairValueGapState.TOUCHED
    return None


def _advance_existing_gaps(
    state: _AnalysisState,
    candle: FairValueGapCandle,
    *,
    instrument: str,
    timeframe: str,
) -> None:
    rank = {
        FairValueGapState.ACTIVE: 0,
        FairValueGapState.TOUCHED: 1,
        FairValueGapState.PARTIALLY_FILLED: 2,
        FairValueGapState.MIDPOINT_FILLED: 3,
        FairValueGapState.FULLY_FILLED: 4,
        FairValueGapState.INVALIDATED: 5,
    }
    reason_for_state = {
        FairValueGapState.TOUCHED: _REASON_TOUCH,
        FairValueGapState.PARTIALLY_FILLED: _REASON_PARTIAL,
        FairValueGapState.MIDPOINT_FILLED: _REASON_MIDPOINT,
        FairValueGapState.FULLY_FILLED: _REASON_FULL,
        FairValueGapState.INVALIDATED: _REASON_INVALIDATION,
    }
    runtimes = sorted(state.runtimes.values(), key=_runtime_sort_key)
    for runtime in runtimes:
        if runtime.state in (
            FairValueGapState.FULLY_FILLED,
            FairValueGapState.INVALIDATED,
        ):
            continue
        if candle.index <= runtime.last_index:
            raise _InvalidGroup("lifecycle index must be strictly later")
        if candle.timestamp <= runtime.last_timestamp:
            raise _InvalidGroup("lifecycle timestamp must be strictly later")
        target = _target_state(runtime.gap, candle)
        if target is None or rank[target] <= rank[runtime.state]:
            continue
        reason = reason_for_state[target]
        transition_id = make_fair_value_gap_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=runtime.gap.direction,
            gap_id=runtime.gap.gap_id,
            from_state=runtime.state,
            to_state=target,
            effective_index=candle.index,
            effective_timestamp=candle.timestamp,
            reason=reason,
        )
        transition = FairValueGapTransition(
            transition_id=transition_id,
            gap_id=runtime.gap.gap_id,
            from_state=runtime.state,
            to_state=target,
            index=candle.index,
            timestamp=candle.timestamp,
            reason=reason,
        )
        transition_ids = (*runtime.transition_ids, transition_id)
        snapshot_id = make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=runtime.gap.direction,
            gap_id=runtime.gap.gap_id,
            effective_index=candle.index,
            effective_timestamp=candle.timestamp,
            state=target,
            transition_ids=transition_ids,
        )
        snapshot = FairValueGapSnapshot(
            snapshot_id=snapshot_id,
            gap_id=runtime.gap.gap_id,
            direction=runtime.gap.direction,
            state=target,
            index=candle.index,
            timestamp=candle.timestamp,
            transition_ids=transition_ids,
        )
        state.transitions.append(transition)
        state.snapshots.append(snapshot)
        state.runtimes[runtime.gap.gap_id] = _GapRuntime(
            gap=runtime.gap,
            state=target,
            transition_ids=transition_ids,
            last_index=candle.index,
            last_timestamp=candle.timestamp,
        )


def _empty_result(
    status: SMCV2PrimitiveStatus,
    *,
    reason: str,
) -> FairValueGapResult:
    return FairValueGapResult(
        status=status,
        reasons=(reason,),
        blocking_reasons=(reason,),
    )


def _state_result(
    state: _AnalysisState,
    *,
    status: SMCV2PrimitiveStatus,
    reason: str,
    blocking: bool = True,
) -> FairValueGapResult:
    return FairValueGapResult(
        status=status,
        gaps=tuple(state.gaps),
        transitions=tuple(state.transitions),
        snapshots=tuple(state.snapshots),
        reasons=(reason,),
        blocking_reasons=(reason,) if blocking else (),
    )


__all__ = [
    "FAIR_VALUE_GAP_DETECTOR_VERSION",
    "FairValueGapState",
    "FairValueGapCandle",
    "FairValueGapContextLink",
    "FairValueGap",
    "FairValueGapTransition",
    "FairValueGapSnapshot",
    "FairValueGapResult",
    "make_fair_value_gap_id",
    "analyze_fair_value_gaps",
]
