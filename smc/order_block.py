"""Deterministic standalone Order Block diagnostics.

This module consumes immutable, fully closed integer-tick candles and
caller-confirmed Dealing Range swing/event evidence.  It performs no I/O,
registration, strategy, risk, execution, or integration work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    DealingRangeSwingSide,
    make_dealing_range_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


ORDER_BLOCK_DETECTOR_VERSION = "SMC-V2-ORDER-BLOCK-1"
_HASH = re.compile(r"^[0-9a-f]{64}$")
_KINDS = frozenset({"BLOCK", "TRANSITION", "SNAPSHOT"})
_FORMATION = "FORMATION_CONFIRMED"
_ACTIVE = "FIRST_ELIGIBLE_BAR"
_TOUCH = "WICK_TOUCHED"
_PARTIAL = "PARTIAL_MITIGATION"
_MIDPOINT = "MIDPOINT_MITIGATION"
_TRAVERSAL = "DISTAL_TRAVERSAL"
_INVALIDATION = "CLOSE_THROUGH_INVALIDATION"
_REASONS = frozenset(
    {_FORMATION, _ACTIVE, _TOUCH, _PARTIAL, _MIDPOINT, _TRAVERSAL, _INVALIDATION}
)


class OrderBlockState(str, Enum):
    DETECTED = "DETECTED"
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    PARTIALLY_MITIGATED = "PARTIALLY_MITIGATED"
    MITIGATED = "MITIGATED"
    FULLY_TRAVERSED = "FULLY_TRAVERSED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class OrderBlockCandle:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class OrderBlock:
    block_id: str
    direction: SMCV2Direction
    source_candle_index: int
    source_candle_timestamp: datetime
    source_swing_id: str
    displacement_indices: tuple[int, ...]
    displacement_timestamps: tuple[datetime, ...]
    structure_event_id: str
    structure_event_type: DealingRangeEventType
    wick_low_tick: int
    wick_high_tick: int
    body_low_tick: int
    body_high_tick: int
    proximal_tick: int
    distal_tick: int
    midpoint_tick: Decimal
    detection_index: int
    detection_timestamp: datetime


@dataclass(frozen=True)
class OrderBlockTransition:
    transition_id: str
    block_id: str
    from_state: OrderBlockState | None
    to_state: OrderBlockState
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class OrderBlockSnapshot:
    snapshot_id: str
    block_id: str
    direction: SMCV2Direction
    state: OrderBlockState
    index: int
    timestamp: datetime
    transition_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrderBlockResult:
    status: SMCV2PrimitiveStatus
    blocks: tuple[OrderBlock, ...] = ()
    transitions: tuple[OrderBlockTransition, ...] = ()
    snapshots: tuple[OrderBlockSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Runtime:
    block: OrderBlock
    state: OrderBlockState
    transition_ids: tuple[str, ...]


@dataclass
class _State:
    blocks: list[OrderBlock]
    transitions: list[OrderBlockTransition]
    snapshots: list[OrderBlockSnapshot]
    runtimes: dict[str, _Runtime]

    def clone(self) -> "_State":
        return _State(
            list(self.blocks), list(self.transitions), list(self.snapshots), dict(self.runtimes)
        )


class _UnknownGroup(ValueError):
    pass


class _AmbiguousGroup(ValueError):
    pass


def make_order_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_candle_index: int | None = None,
    source_candle_timestamp: datetime | None = None,
    source_swing_id: str | None = None,
    displacement_indices: tuple[int, ...] = (),
    displacement_timestamps: tuple[datetime, ...] = (),
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    detection_index: int | None = None,
    detection_timestamp: datetime | None = None,
    block_id: str | None = None,
    from_state: OrderBlockState | None = None,
    to_state: OrderBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: OrderBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    """Build one exact kind-specific Order Block identity."""
    try:
        return _make_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_candle_index=source_candle_index,
            source_candle_timestamp=source_candle_timestamp,
            source_swing_id=source_swing_id,
            displacement_indices=displacement_indices,
            displacement_timestamps=displacement_timestamps,
            structure_event_id=structure_event_id,
            structure_event_type=structure_event_type,
            wick_boundaries=wick_boundaries,
            body_boundaries=body_boundaries,
            proximal_tick=proximal_tick,
            distal_tick=distal_tick,
            midpoint_tick=midpoint_tick,
            detection_index=detection_index,
            detection_timestamp=detection_timestamp,
            block_id=block_id,
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


def _make_id(**values: object) -> str:
    kind = values["identity_kind"]
    if not isinstance(kind, str) or kind not in _KINDS:
        raise ValueError("identity_kind is not a locked Order Block identity kind")
    direction = values["direction"]
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")
    payload: dict[str, object] = {
        "detector_version": ORDER_BLOCK_DETECTOR_VERSION,
        "identity_kind": kind,
        "instrument": _text(values["instrument"], "instrument"),
        "timeframe": _text(values["timeframe"], "timeframe"),
        "direction": direction.value,
    }
    block_fields = (
        "source_candle_index", "source_candle_timestamp", "source_swing_id",
        "displacement_indices", "displacement_timestamps", "structure_event_id",
        "structure_event_type", "wick_boundaries", "body_boundaries",
        "proximal_tick", "distal_tick", "midpoint_tick", "detection_index",
        "detection_timestamp",
    )
    transition_fields = (
        "block_id", "from_state", "to_state", "effective_index",
        "effective_timestamp", "reason",
    )
    if kind == "BLOCK":
        _defaults(values, (*transition_fields, "state", "transition_ids"))
        source_index = _integer(values["source_candle_index"], "source_candle_index")
        source_time = _timestamp(values["source_candle_timestamp"], "source_candle_timestamp")
        swing_id = _hash(values["source_swing_id"], "source_swing_id")
        indices = _indices(values["displacement_indices"], "displacement_indices", 1, 3)
        timestamps = _timestamps(values["displacement_timestamps"], "displacement_timestamps", len(indices))
        if source_index >= indices[0] or source_time >= timestamps[0]:
            raise ValueError("source candle must strictly precede displacement")
        event_id = _hash(values["structure_event_id"], "structure_event_id")
        event_type = values["structure_event_type"]
        if not isinstance(event_type, DealingRangeEventType):
            raise TypeError("structure_event_type must be DealingRangeEventType")
        wick = _boundaries(values["wick_boundaries"], "wick_boundaries")
        body = _boundaries(values["body_boundaries"], "body_boundaries")
        if body.lower_tick < wick.lower_tick or body.upper_tick > wick.upper_tick:
            raise ValueError("body boundaries must be inside wick boundaries")
        proximal = _tick(values["proximal_tick"], "proximal_tick")
        distal = _tick(values["distal_tick"], "distal_tick")
        expected_pd = (
            (wick.upper_tick, wick.lower_tick)
            if direction is SMCV2Direction.BULLISH
            else (wick.lower_tick, wick.upper_tick)
        )
        if (proximal, distal) != expected_pd:
            raise ValueError("proximal/distal do not reconcile with direction")
        midpoint = _midpoint(wick.lower_tick, wick.upper_tick)
        if not isinstance(values["midpoint_tick"], Decimal) or values["midpoint_tick"] != midpoint:
            raise ValueError("midpoint_tick does not reconcile")
        detection_index = _integer(values["detection_index"], "detection_index")
        detection_time = _timestamp(values["detection_timestamp"], "detection_timestamp")
        if detection_index != indices[-1] or detection_time != timestamps[-1]:
            raise ValueError("detection moment must equal final displacement moment")
        payload.update({
            "source_candle_index": source_index,
            "source_candle_timestamp": _timestamp_text(source_time),
            "source_swing_id": swing_id,
            "displacement_indices": list(indices),
            "displacement_timestamps": [_timestamp_text(v) for v in timestamps],
            "structure_event_id": event_id,
            "structure_event_type": event_type.value,
            "wick_boundaries": [wick.lower_tick, wick.upper_tick],
            "body_boundaries": [body.lower_tick, body.upper_tick],
            "proximal_tick": proximal,
            "distal_tick": distal,
            "midpoint_tick": _decimal_text(midpoint),
            "detection_index": detection_index,
            "detection_timestamp": _timestamp_text(detection_time),
        })
    elif kind == "TRANSITION":
        _defaults(values, (*block_fields, "state", "transition_ids"))
        block_id = _hash(values["block_id"], "block_id")
        from_state = values["from_state"]
        to_state = values["to_state"]
        reason = values["reason"]
        _transition_edge(from_state, to_state, reason)
        index = _integer(values["effective_index"], "effective_index")
        timestamp = _timestamp(values["effective_timestamp"], "effective_timestamp")
        payload.update({
            "block_id": block_id,
            "from_state": None if from_state is None else from_state.value,
            "to_state": to_state.value,
            "effective_index": index,
            "effective_timestamp": _timestamp_text(timestamp),
            "reason": reason,
        })
    else:
        _defaults(values, (*block_fields, "from_state", "to_state", "reason"))
        block_id = _hash(values["block_id"], "block_id")
        state = values["state"]
        if not isinstance(state, OrderBlockState):
            raise TypeError("state must be OrderBlockState")
        index = _integer(values["effective_index"], "effective_index")
        timestamp = _timestamp(values["effective_timestamp"], "effective_timestamp")
        ids = _hash_tuple(values["transition_ids"], "transition_ids", allow_empty=False)
        if len(set(ids)) != len(ids):
            raise ValueError("transition_ids cannot contain duplicates")
        payload.update({
            "block_id": block_id,
            "state": state.value,
            "effective_index": index,
            "effective_timestamp": _timestamp_text(timestamp),
            "transition_ids": list(ids),
        })
    canonical = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def analyze_order_blocks(
    *,
    instrument: str,
    timeframe: str,
    candles: tuple[OrderBlockCandle, ...] | None,
    swings: tuple[DealingRangeSwing, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
) -> OrderBlockResult:
    """Analyze standalone immutable Order Block evidence."""
    if candles is None or swings is None or structure_events is None:
        reason = "Missing complete top-level Order Block context"
        return OrderBlockResult(SMCV2PrimitiveStatus.UNKNOWN, reasons=(reason,), blocking_reasons=(reason,))
    try:
        canonical_instrument = _text(instrument, "instrument")
        canonical_timeframe = _text(timeframe, "timeframe")
        if not isinstance(candles, tuple):
            raise TypeError("candles must be a tuple")
        issues: list[tuple[tuple[int, datetime], str, Exception]] = []
        candle_values: tuple[OrderBlockCandle, ...] = ()
        for end in range(1, len(candles) + 1):
            try:
                candle_values = _validate_candles(candles[:end])
            except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
                moment = _safe_candle_moment(candles[end - 1])
                if moment is None:
                    raise
                issues.append((moment, "candle", exc))
                break
        candle_map = {(c.index, c.timestamp): c for c in candle_values}
        if not isinstance(swings, tuple):
            raise TypeError("swings must be a tuple")
        swing_values: tuple[DealingRangeSwing, ...] = ()
        for end in range(1, len(swings) + 1):
            try:
                swing_values = _validate_swings(swings[:end], candle_map)
            except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
                moment = _safe_swing_moment(swings[end - 1])
                if moment is None:
                    raise
                issues.append((moment, "swing", exc))
                break
        if not isinstance(structure_events, tuple):
            raise TypeError("structure_events must be a tuple")
        event_values: tuple[DealingRangeStructureEvent, ...] = ()
        for end in range(1, len(structure_events) + 1):
            try:
                event_values = _validate_events(
                    structure_events[:end],
                    swing_values,
                    candle_map,
                    canonical_instrument,
                    canonical_timeframe,
                )
            except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
                moment = _safe_event_moment(structure_events[end - 1])
                if moment is None:
                    raise
                issues.append((moment, "structure-event", exc))
                break
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return _empty(SMCV2PrimitiveStatus.INVALID, f"Invalid Order Block input: {exc}")
    if not candle_values:
        if issues:
            first_issue = min(issues, key=lambda item: item[0])
            return _empty(
                SMCV2PrimitiveStatus.INVALID,
                f"Invalid {first_issue[1]} group: {first_issue[2]}",
            )
        return _empty(SMCV2PrimitiveStatus.NONE, "Complete inputs contain no candles")

    events_by_index: dict[int, list[DealingRangeStructureEvent]] = {}
    for event in event_values:
        events_by_index.setdefault(event.provenance.confirmation_index, []).append(event)
    state = _State([], [], [], {})
    candle_position = {c.index: pos for pos, c in enumerate(candle_values)}
    swing_by_id = {s.swing_id: s for s in swing_values}
    try:
        first_issue = min(issues, key=lambda item: item[0]) if issues else None
        for position, candle in enumerate(candle_values):
            if first_issue is not None and (candle.index, candle.timestamp) >= first_issue[0]:
                break
            candidate_state = state.clone()
            _advance(
                candidate_state, candle, canonical_instrument, canonical_timeframe
            )
            candidates: list[tuple[OrderBlock, DealingRangeStructureEvent]] = []
            unknown = False
            for event in events_by_index.get(candle.index, []):
                try:
                    block = _candidate(
                        event=event,
                        swing=swing_by_id[event.broken_swing_id],
                        candles=candle_values,
                        candle_position=candle_position,
                        instrument=canonical_instrument,
                        timeframe=canonical_timeframe,
                    )
                except _UnknownGroup:
                    unknown = True
                    continue
                if block is not None:
                    candidates.append((block, event))
            unique = {item[0].block_id: item for item in candidates}
            if len(unique) > 1:
                raise _AmbiguousGroup("multiple distinct qualifying candidates in one atomic group")
            if unknown and not unique:
                raise _UnknownGroup("insufficient pre-displacement median history")
            if unique:
                block, _ = next(iter(unique.values()))
                _form(candidate_state, block, canonical_instrument, canonical_timeframe)
            state = candidate_state
    except _AmbiguousGroup as exc:
        if first_issue is not None:
            return _result(
                state,
                SMCV2PrimitiveStatus.INVALID,
                f"Invalid {first_issue[1]} group: {first_issue[2]}",
            )
        return _result(state, SMCV2PrimitiveStatus.AMBIGUOUS, str(exc))
    except _UnknownGroup as exc:
        if first_issue is not None:
            return _result(
                state,
                SMCV2PrimitiveStatus.INVALID,
                f"Invalid {first_issue[1]} group: {first_issue[2]}",
            )
        return _result(state, SMCV2PrimitiveStatus.UNKNOWN, str(exc))
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return _result(state, SMCV2PrimitiveStatus.INVALID, f"Invalid effective group: {exc}")
    if first_issue is not None:
        return _result(
            state,
            SMCV2PrimitiveStatus.INVALID,
            f"Invalid {first_issue[1]} group: {first_issue[2]}",
        )
    if state.blocks:
        return _result(state, SMCV2PrimitiveStatus.VALID, "Deterministic Order Block evidence emitted")
    return _result(state, SMCV2PrimitiveStatus.NONE, "No qualifying Order Block emitted")


def _validate_candles(values: object) -> tuple[OrderBlockCandle, ...]:
    if not isinstance(values, tuple):
        raise TypeError("candles must be a tuple")
    result = []
    prior_index = -1
    prior_time: datetime | None = None
    for value in values:
        if not isinstance(value, OrderBlockCandle):
            raise TypeError("candle must be OrderBlockCandle")
        index = _integer(value.index, "candle.index")
        timestamp = _timestamp(value.timestamp, "candle.timestamp")
        ticks = tuple(_tick(getattr(value, name), f"candle.{name}") for name in ("open_tick", "high_tick", "low_tick", "close_tick"))
        open_tick, high_tick, low_tick, close_tick = ticks
        if low_tick > high_tick or not low_tick <= open_tick <= high_tick or not low_tick <= close_tick <= high_tick:
            raise ValueError("invalid candle OHLC")
        if index <= prior_index or (prior_time is not None and timestamp <= prior_time):
            raise ValueError("candle indices and timestamps must independently increase")
        prior_index, prior_time = index, timestamp
        result.append(OrderBlockCandle(index, timestamp, open_tick, high_tick, low_tick, close_tick))
    return tuple(result)


def _validate_swings(
    values: object,
    candles: dict[tuple[int, datetime], OrderBlockCandle],
) -> tuple[DealingRangeSwing, ...]:
    if not isinstance(values, tuple):
        raise TypeError("swings must be a tuple")
    result = []
    prior_key: tuple[object, ...] | None = None
    identities: set[tuple[object, ...]] = set()
    ids: set[str] = set()
    for swing in values:
        if not isinstance(swing, DealingRangeSwing):
            raise TypeError("swing must be DealingRangeSwing")
        if swing.side not in (DealingRangeSwingSide.HIGH, DealingRangeSwingSide.LOW):
            raise ValueError("invalid swing side")
        _tick(swing.price_tick, "swing.price_tick")
        _hash(swing.swing_id, "swing.swing_id")
        provenance = _provenance(swing.provenance, exact_one=True)
        source_pair = (provenance.source_indices[0], provenance.source_timestamps[0])
        confirmation_pair = (provenance.confirmation_index, provenance.confirmation_timestamp)
        if source_pair not in candles or confirmation_pair not in candles:
            raise ValueError("swing candle reference is dangling")
        if provenance.confirmation_index < provenance.source_indices[0] + 2:
            raise ValueError("swing confirmation delay is below two closed bars")
        expected = candles[source_pair].high_tick if swing.side is DealingRangeSwingSide.HIGH else candles[source_pair].low_tick
        if swing.price_tick != expected:
            raise ValueError("swing price does not reconcile with source candle")
        key = (provenance.confirmation_index, provenance.source_indices[0], swing.side.value, swing.swing_id)
        source_identity = (provenance.source_indices[0], swing.side)
        if prior_key is not None and key <= prior_key:
            raise ValueError("swing tuple composite order is not increasing")
        if swing.swing_id in ids or source_identity in identities:
            raise ValueError("duplicate swing identity")
        prior_key = key
        ids.add(swing.swing_id)
        identities.add(source_identity)
        result.append(swing)
    return tuple(result)


def _validate_events(
    values: object,
    swings: tuple[DealingRangeSwing, ...],
    candles: dict[tuple[int, datetime], OrderBlockCandle],
    instrument: str,
    timeframe: str,
) -> tuple[DealingRangeStructureEvent, ...]:
    if not isinstance(values, tuple):
        raise TypeError("structure_events must be a tuple")
    swing_map = {s.swing_id: s for s in swings}
    result = []
    prior_key: tuple[object, ...] | None = None
    seen: set[str] = set()
    for event in values:
        if not isinstance(event, DealingRangeStructureEvent):
            raise TypeError("event must be DealingRangeStructureEvent")
        if event.direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("invalid event direction")
        if not isinstance(event.event_type, DealingRangeEventType):
            raise TypeError("invalid event type")
        _hash(event.event_id, "event.event_id")
        _hash(event.broken_swing_id, "event.broken_swing_id")
        if event.broken_swing_id not in swing_map:
            raise ValueError("event broken swing is dangling")
        provenance = _provenance(event.provenance, contiguous=True)
        for pair in zip(provenance.source_indices, provenance.source_timestamps):
            if pair not in candles:
                raise ValueError("event source candle is dangling")
        if (provenance.confirmation_index, provenance.confirmation_timestamp) != (
            provenance.source_indices[-1], provenance.source_timestamps[-1]
        ):
            raise ValueError("event confirmation must equal final provenance source")
        swing = swing_map[event.broken_swing_id]
        expected_side = DealingRangeSwingSide.HIGH if event.direction is SMCV2Direction.BULLISH else DealingRangeSwingSide.LOW
        if swing.side is not expected_side:
            raise ValueError("event direction and swing side conflict")
        final = candles[(provenance.confirmation_index, provenance.confirmation_timestamp)]
        if event.direction is SMCV2Direction.BULLISH:
            break_ok = final.close_tick >= swing.price_tick + 1
        else:
            break_ok = final.close_tick <= swing.price_tick - 1
        if not break_ok:
            raise ValueError("present confirmed event lacks exact one-tick close break")
        expected_id = make_dealing_range_id(
            identity_kind="EVENT", instrument=instrument, timeframe=timeframe,
            direction=event.direction, source_indices=provenance.source_indices,
            event_type=event.event_type, broken_swing_id=event.broken_swing_id,
            confirmation_index=provenance.confirmation_index,
            boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick),
        )
        if event.event_id != expected_id:
            raise ValueError("event identity mismatch")
        if not (
            (swing.provenance.confirmation_index, swing.provenance.confirmation_timestamp)
            < (provenance.source_indices[0], provenance.source_timestamps[0])
        ):
            raise ValueError("swing confirmation must strictly precede displacement")
        key = (provenance.confirmation_index, provenance.confirmation_timestamp, event.direction.value, event.event_type.value, event.event_id)
        if prior_key is not None and key <= prior_key:
            raise ValueError("event tuple composite order is not increasing")
        if event.event_id in seen:
            raise ValueError("duplicate event identity")
        prior_key = key
        seen.add(event.event_id)
        result.append(event)
    return tuple(result)


def _safe_event_moment(value: object) -> tuple[int, datetime] | None:
    try:
        provenance = value.provenance
        index = provenance.confirmation_index
        timestamp = provenance.confirmation_timestamp
        if type(index) is not int or index < 0 or not isinstance(timestamp, datetime):
            return None
        return index, normalize_utc_timestamp(timestamp)
    except (AttributeError, TypeError, ValueError):
        return None


def _safe_candle_moment(value: object) -> tuple[int, datetime] | None:
    try:
        index = value.index
        timestamp = value.timestamp
        if type(index) is not int or index < 0 or not isinstance(timestamp, datetime):
            return None
        return index, normalize_utc_timestamp(timestamp)
    except (AttributeError, TypeError, ValueError):
        return None


def _safe_swing_moment(value: object) -> tuple[int, datetime] | None:
    try:
        provenance = value.provenance
        index = provenance.confirmation_index
        timestamp = provenance.confirmation_timestamp
        if type(index) is not int or index < 0 or not isinstance(timestamp, datetime):
            return None
        return index, normalize_utc_timestamp(timestamp)
    except (AttributeError, TypeError, ValueError):
        return None


def _candidate(
    *,
    event: DealingRangeStructureEvent,
    swing: DealingRangeSwing,
    candles: tuple[OrderBlockCandle, ...],
    candle_position: dict[int, int],
    instrument: str,
    timeframe: str,
) -> OrderBlock | None:
    by_index = {c.index: c for c in candles}
    chosen: tuple[OrderBlockCandle, ...] | None = None
    insufficient = True
    for length in (3, 2, 1):
        if len(event.provenance.source_indices) < length:
            continue
        indices = event.provenance.source_indices[-length:]
        timestamps = event.provenance.source_timestamps[-length:]
        sequence = tuple(by_index[index] for index in indices)
        if tuple(c.timestamp for c in sequence) != timestamps:
            raise ValueError("displacement timestamp suffix mismatch")
        positions = tuple(candle_position[index] for index in indices)
        if any(b != a + 1 for a, b in zip(positions, positions[1:])):
            raise ValueError("displacement suffix is not contiguous supplied evidence")
        baseline = candles[max(0, positions[0] - 20):positions[0]]
        if len(baseline) < 10:
            continue
        insufficient = False
        directional = all(
            (c.close_tick > c.open_tick if event.direction is SMCV2Direction.BULLISH else c.close_tick < c.open_tick)
            for c in sequence
        )
        if not directional:
            continue
        median = _median(tuple(abs(c.close_tick - c.open_tick) for c in baseline))
        if any(
            c.high_tick > c.low_tick
            and 5 * abs(c.close_tick - c.open_tick) >= 3 * (c.high_tick - c.low_tick)
            and Decimal(abs(c.close_tick - c.open_tick)) >= median
            for c in sequence
        ):
            chosen = sequence
            break
    if chosen is None:
        if insufficient:
            raise _UnknownGroup("fewer than ten pre-displacement candles")
        return None
    start_position = candle_position[chosen[0].index]
    search = candles[max(0, start_position - 10):start_position]
    source = next(
        (
            c for c in reversed(search)
            if (
                c.close_tick < c.open_tick
                if event.direction is SMCV2Direction.BULLISH
                else c.close_tick > c.open_tick
            )
        ),
        None,
    )
    if source is None:
        return None
    wick_low, wick_high = source.low_tick, source.high_tick
    body_low, body_high = sorted((source.open_tick, source.close_tick))
    if event.direction is SMCV2Direction.BULLISH:
        proximal, distal = wick_high, wick_low
    else:
        proximal, distal = wick_low, wick_high
    midpoint = _midpoint(wick_low, wick_high)
    kwargs = {
        "identity_kind": "BLOCK", "instrument": instrument, "timeframe": timeframe,
        "direction": event.direction, "source_candle_index": source.index,
        "source_candle_timestamp": source.timestamp, "source_swing_id": swing.swing_id,
        "displacement_indices": tuple(c.index for c in chosen),
        "displacement_timestamps": tuple(c.timestamp for c in chosen),
        "structure_event_id": event.event_id, "structure_event_type": event.event_type,
        "wick_boundaries": SMCV2TickRange(wick_low, wick_high),
        "body_boundaries": SMCV2TickRange(body_low, body_high),
        "proximal_tick": proximal, "distal_tick": distal, "midpoint_tick": midpoint,
        "detection_index": chosen[-1].index, "detection_timestamp": chosen[-1].timestamp,
    }
    block_id = make_order_block_id(**kwargs)
    return OrderBlock(
        block_id, event.direction, source.index, source.timestamp, swing.swing_id,
        tuple(c.index for c in chosen), tuple(c.timestamp for c in chosen),
        event.event_id, event.event_type, wick_low, wick_high, body_low, body_high,
        proximal, distal, midpoint, chosen[-1].index, chosen[-1].timestamp,
    )


def _form(state: _State, block: OrderBlock, instrument: str, timeframe: str) -> None:
    state.blocks.append(block)
    transition = _transition(block, None, OrderBlockState.DETECTED, block.detection_index, block.detection_timestamp, _FORMATION, instrument, timeframe)
    state.transitions.append(transition)
    snapshot = _snapshot(block, OrderBlockState.DETECTED, block.detection_index, block.detection_timestamp, (transition.transition_id,), instrument, timeframe)
    state.snapshots.append(snapshot)
    state.runtimes[block.block_id] = _Runtime(block, OrderBlockState.DETECTED, (transition.transition_id,))


def _advance(state: _State, candle: OrderBlockCandle, instrument: str, timeframe: str) -> None:
    runtimes = sorted(state.runtimes.values(), key=lambda r: (r.block.detection_index, r.block.detection_timestamp, r.block.source_candle_index, r.block.direction.value, r.block.displacement_indices, r.block.block_id))
    for runtime in runtimes:
        block = runtime.block
        if candle.index <= block.detection_index or runtime.state is OrderBlockState.INVALIDATED:
            continue
        current = runtime
        if current.state is OrderBlockState.DETECTED:
            current = _emit(state, current, OrderBlockState.ACTIVE, candle, _ACTIVE, instrument, timeframe)
        target = _target(current.block, current.state, candle)
        if target is not None and target is not current.state:
            reason = {
                OrderBlockState.TOUCHED: _TOUCH,
                OrderBlockState.PARTIALLY_MITIGATED: _PARTIAL,
                OrderBlockState.MITIGATED: _MIDPOINT,
                OrderBlockState.FULLY_TRAVERSED: _TRAVERSAL,
                OrderBlockState.INVALIDATED: _INVALIDATION,
            }[target]
            current = _emit(state, current, target, candle, reason, instrument, timeframe)
        state.runtimes[block.block_id] = current


def _target(block: OrderBlock, state: OrderBlockState, candle: OrderBlockCandle) -> OrderBlockState | None:
    if state is OrderBlockState.INVALIDATED:
        return None
    candidate: OrderBlockState | None = None
    if block.direction is SMCV2Direction.BULLISH:
        if candle.close_tick <= block.distal_tick - 1:
            return OrderBlockState.INVALIDATED
        if state is not OrderBlockState.FULLY_TRAVERSED:
            if candle.low_tick <= block.distal_tick:
                candidate = OrderBlockState.FULLY_TRAVERSED
            elif Decimal(candle.low_tick) <= block.midpoint_tick:
                candidate = OrderBlockState.MITIGATED
            elif candle.low_tick < block.proximal_tick:
                candidate = OrderBlockState.PARTIALLY_MITIGATED
            elif candle.low_tick == block.proximal_tick:
                candidate = OrderBlockState.TOUCHED
    else:
        if candle.close_tick >= block.distal_tick + 1:
            return OrderBlockState.INVALIDATED
        if state is not OrderBlockState.FULLY_TRAVERSED:
            if candle.high_tick >= block.distal_tick:
                candidate = OrderBlockState.FULLY_TRAVERSED
            elif Decimal(candle.high_tick) >= block.midpoint_tick:
                candidate = OrderBlockState.MITIGATED
            elif candle.high_tick > block.proximal_tick:
                candidate = OrderBlockState.PARTIALLY_MITIGATED
            elif candle.high_tick == block.proximal_tick:
                candidate = OrderBlockState.TOUCHED
    depths = {
        OrderBlockState.ACTIVE: 0,
        OrderBlockState.TOUCHED: 1,
        OrderBlockState.PARTIALLY_MITIGATED: 2,
        OrderBlockState.MITIGATED: 3,
        OrderBlockState.FULLY_TRAVERSED: 4,
    }
    if candidate is None or depths.get(candidate, -1) <= depths.get(state, -1):
        return None
    return candidate


def _emit(state: _State, runtime: _Runtime, to_state: OrderBlockState, candle: OrderBlockCandle, reason: str, instrument: str, timeframe: str) -> _Runtime:
    transition = _transition(runtime.block, runtime.state, to_state, candle.index, candle.timestamp, reason, instrument, timeframe)
    ids = (*runtime.transition_ids, transition.transition_id)
    state.transitions.append(transition)
    state.snapshots.append(_snapshot(runtime.block, to_state, candle.index, candle.timestamp, ids, instrument, timeframe))
    return _Runtime(runtime.block, to_state, ids)


def _transition(block: OrderBlock, from_state: OrderBlockState | None, to_state: OrderBlockState, index: int, timestamp: datetime, reason: str, instrument: str, timeframe: str) -> OrderBlockTransition:
    identity = make_order_block_id(
        identity_kind="TRANSITION", instrument=instrument, timeframe=timeframe,
        direction=block.direction, block_id=block.block_id, from_state=from_state,
        to_state=to_state, effective_index=index, effective_timestamp=timestamp, reason=reason,
    )
    return OrderBlockTransition(identity, block.block_id, from_state, to_state, index, timestamp, reason)


def _snapshot(block: OrderBlock, state: OrderBlockState, index: int, timestamp: datetime, ids: tuple[str, ...], instrument: str, timeframe: str) -> OrderBlockSnapshot:
    identity = make_order_block_id(
        identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe,
        direction=block.direction, block_id=block.block_id, state=state,
        effective_index=index, effective_timestamp=timestamp, transition_ids=ids,
    )
    return OrderBlockSnapshot(identity, block.block_id, block.direction, state, index, timestamp, ids)


def _transition_edge(from_state: object, to_state: object, reason: object) -> None:
    if from_state is not None and not isinstance(from_state, OrderBlockState):
        raise TypeError("from_state must be OrderBlockState or None")
    if not isinstance(to_state, OrderBlockState):
        raise TypeError("to_state must be OrderBlockState")
    if reason not in _REASONS:
        raise ValueError("reason must be an exact locked token")
    if from_state is None:
        if (to_state, reason) != (OrderBlockState.DETECTED, _FORMATION):
            raise ValueError("invalid formation transition")
        return
    if from_state is OrderBlockState.DETECTED:
        if (to_state, reason) != (OrderBlockState.ACTIVE, _ACTIVE):
            raise ValueError("DETECTED must transition to ACTIVE")
        return
    allowed_reason = {
        OrderBlockState.TOUCHED: _TOUCH,
        OrderBlockState.PARTIALLY_MITIGATED: _PARTIAL,
        OrderBlockState.MITIGATED: _MIDPOINT,
        OrderBlockState.FULLY_TRAVERSED: _TRAVERSAL,
        OrderBlockState.INVALIDATED: _INVALIDATION,
    }.get(to_state)
    depth = {s: i for i, s in enumerate((OrderBlockState.ACTIVE, OrderBlockState.TOUCHED, OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.MITIGATED, OrderBlockState.FULLY_TRAVERSED))}
    valid = to_state is OrderBlockState.INVALIDATED or (
        from_state in depth and to_state in depth and depth[to_state] > depth[from_state]
    )
    if from_state is OrderBlockState.FULLY_TRAVERSED:
        valid = to_state is OrderBlockState.INVALIDATED
    if from_state is OrderBlockState.INVALIDATED or not valid or reason != allowed_reason:
        raise ValueError("invalid lifecycle edge or reason")


def _provenance(value: object, *, exact_one: bool = False, contiguous: bool = False) -> SMCV2EventProvenance:
    if not isinstance(value, SMCV2EventProvenance):
        raise TypeError("provenance must be SMCV2EventProvenance")
    indices = _indices(value.source_indices, "provenance.source_indices", 1, None)
    timestamps = _timestamps(value.source_timestamps, "provenance.source_timestamps", len(indices))
    confirmation_index = _integer(value.confirmation_index, "provenance.confirmation_index")
    confirmation_timestamp = _timestamp(value.confirmation_timestamp, "provenance.confirmation_timestamp")
    if exact_one and len(indices) != 1:
        raise ValueError("swing provenance requires one source")
    if contiguous and any(b != a + 1 for a, b in zip(indices, indices[1:])):
        raise ValueError("event source indices must be contiguous")
    return SMCV2EventProvenance(indices, timestamps, confirmation_index, confirmation_timestamp)


def _median(values: tuple[int, ...]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return Decimal(ordered[middle])
    return _midpoint(ordered[middle - 1], ordered[middle])


def _midpoint(low: int, high: int) -> Decimal:
    total = low + high
    if total % 2 == 0:
        return Decimal(total // 2)
    sign = "-" if total < 0 else ""
    return Decimal(f"{sign}{abs(total) // 2}.5")


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0.0"
    text = format(value, "f")
    return text if "." in text else f"{text}.0"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip().upper()


def _integer(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise TypeError(f"{name} must be a non-negative exact integer")
    return value


def _tick(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact integer tick")
    return value


def _timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be datetime")
    try:
        return normalize_utc_timestamp(value)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"{name} must be timezone-aware") from exc


def _timestamp_text(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _hash(value: object, name: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _hash_tuple(value: object, name: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(value, tuple) or (not allow_empty and not value):
        raise TypeError(f"{name} must be a non-empty tuple")
    return tuple(_hash(item, name) for item in value)


def _indices(value: object, name: str, minimum: int, maximum: int | None) -> tuple[int, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        raise ValueError(f"{name} has invalid length")
    result = tuple(_integer(item, name) for item in value)
    if any(a >= b for a, b in zip(result, result[1:])):
        raise ValueError(f"{name} must strictly increase")
    return result


def _timestamps(value: object, name: str, length: int) -> tuple[datetime, ...]:
    if not isinstance(value, tuple) or len(value) != length:
        raise TypeError(f"{name} must be an equal-length tuple")
    result = tuple(_timestamp(item, name) for item in value)
    if any(a >= b for a, b in zip(result, result[1:])):
        raise ValueError(f"{name} must strictly increase")
    return result


def _boundaries(value: object, name: str) -> SMCV2TickRange:
    if not isinstance(value, SMCV2TickRange):
        raise TypeError(f"{name} must be SMCV2TickRange")
    return SMCV2TickRange(_tick(value.lower_tick, name), _tick(value.upper_tick, name))


def _defaults(values: dict[str, object], names: tuple[str, ...]) -> None:
    for name in names:
        value = values[name]
        default = () if name in ("displacement_indices", "displacement_timestamps", "transition_ids") else None
        if value != default:
            raise ValueError(f"{name} is forbidden for this identity kind")


def _empty(status: SMCV2PrimitiveStatus, reason: str) -> OrderBlockResult:
    return OrderBlockResult(status, reasons=(reason,), blocking_reasons=(reason,) if status in (SMCV2PrimitiveStatus.UNKNOWN, SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.AMBIGUOUS) else ())


def _result(state: _State, status: SMCV2PrimitiveStatus, reason: str) -> OrderBlockResult:
    return OrderBlockResult(
        status, tuple(state.blocks), tuple(state.transitions), tuple(state.snapshots),
        (reason,), (reason,) if status in (SMCV2PrimitiveStatus.UNKNOWN, SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.AMBIGUOUS) else (),
    )


__all__ = [
    "ORDER_BLOCK_DETECTOR_VERSION",
    "OrderBlockState",
    "OrderBlockCandle",
    "OrderBlock",
    "OrderBlockTransition",
    "OrderBlockSnapshot",
    "OrderBlockResult",
    "make_order_block_id",
    "analyze_order_blocks",
]
