"""Deterministic standalone Breaker Block diagnostics.

This module consumes immutable canonical Order Block and confirmed Dealing
Range evidence.  It performs no I/O, registration, strategy, risk, execution,
or integration work.
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
from smc.order_block import (
    OrderBlock,
    OrderBlockSnapshot,
    OrderBlockState,
    OrderBlockTransition,
    make_order_block_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


BREAKER_BLOCK_DETECTOR_VERSION = "SMC-V2-BREAKER-BLOCK-1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_KINDS = frozenset({"BREAKER", "TRANSITION", "SNAPSHOT"})
_CREATION = "ROLE_REVERSAL_CONFIRMED"
_TOUCH = "WICK_TOUCHED"
_PARTIAL = "PARTIAL_MITIGATION"
_MITIGATION = "MIDPOINT_MITIGATION"
_INVALIDATION = "CLOSE_THROUGH_INVALIDATION"
_REASONS = frozenset(
    {_CREATION, _TOUCH, _PARTIAL, _MITIGATION, _INVALIDATION}
)

_SOURCE_REASONS = {
    (None, OrderBlockState.DETECTED): "FORMATION_CONFIRMED",
    (OrderBlockState.DETECTED, OrderBlockState.ACTIVE): "FIRST_ELIGIBLE_BAR",
    (OrderBlockState.ACTIVE, OrderBlockState.TOUCHED): "WICK_TOUCHED",
    (OrderBlockState.ACTIVE, OrderBlockState.PARTIALLY_MITIGATED): "PARTIAL_MITIGATION",
    (OrderBlockState.ACTIVE, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.ACTIVE, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.ACTIVE, OrderBlockState.INVALIDATED): _INVALIDATION,
    (OrderBlockState.TOUCHED, OrderBlockState.PARTIALLY_MITIGATED): "PARTIAL_MITIGATION",
    (OrderBlockState.TOUCHED, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.TOUCHED, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.TOUCHED, OrderBlockState.INVALIDATED): _INVALIDATION,
    (OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.INVALIDATED): _INVALIDATION,
    (OrderBlockState.MITIGATED, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.MITIGATED, OrderBlockState.INVALIDATED): _INVALIDATION,
    (OrderBlockState.FULLY_TRAVERSED, OrderBlockState.INVALIDATED): _INVALIDATION,
}

_Moment = tuple[int, datetime]


class BreakerBlockState(str, Enum):
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    PARTIALLY_MITIGATED = "PARTIALLY_MITIGATED"
    MITIGATED = "MITIGATED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class BreakerBlockObservation:
    index: int
    timestamp: datetime
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class BreakerBlock:
    breaker_id: str
    direction: SMCV2Direction
    source_order_block_id: str
    source_order_block_invalidation_transition_id: str
    source_order_block_invalidation_snapshot_id: str
    structure_event_id: str
    structure_event_type: DealingRangeEventType
    wick_low_tick: int
    wick_high_tick: int
    body_low_tick: int
    body_high_tick: int
    proximal_tick: int
    distal_tick: int
    midpoint_tick: Decimal
    source_invalidation_index: int
    source_invalidation_timestamp: datetime
    confirmation_index: int
    confirmation_timestamp: datetime


@dataclass(frozen=True)
class BreakerBlockTransition:
    transition_id: str
    breaker_id: str
    source_order_block_id: str
    source_order_block_invalidation_transition_id: str
    source_order_block_invalidation_snapshot_id: str
    structure_event_id: str
    from_state: BreakerBlockState | None
    to_state: BreakerBlockState
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class BreakerBlockSnapshot:
    snapshot_id: str
    breaker_id: str
    source_order_block_id: str
    source_order_block_invalidation_transition_id: str
    source_order_block_invalidation_snapshot_id: str
    structure_event_id: str
    direction: SMCV2Direction
    state: BreakerBlockState
    index: int
    timestamp: datetime
    transition_ids: tuple[str, ...]


@dataclass(frozen=True)
class BreakerBlockResult:
    status: SMCV2PrimitiveStatus
    breakers: tuple[BreakerBlock, ...] = ()
    transitions: tuple[BreakerBlockTransition, ...] = ()
    snapshots: tuple[BreakerBlockSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _SourceHistory:
    block: OrderBlock
    transitions: tuple[OrderBlockTransition, ...]
    snapshots: tuple[OrderBlockSnapshot, ...]
    invalidation: OrderBlockTransition | None
    invalidation_snapshot: OrderBlockSnapshot | None


@dataclass(frozen=True)
class _Runtime:
    breaker: BreakerBlock
    state: BreakerBlockState
    transition_ids: tuple[str, ...]


@dataclass
class _State:
    breakers: list[BreakerBlock]
    transitions: list[BreakerBlockTransition]
    snapshots: list[BreakerBlockSnapshot]
    runtimes: dict[str, _Runtime]

    def clone(self) -> "_State":
        return _State(
            list(self.breakers),
            list(self.transitions),
            list(self.snapshots),
            dict(self.runtimes),
        )


@dataclass(frozen=True)
class _Issue:
    moment: _Moment | None
    reason: str


class _AmbiguousGroup(ValueError):
    pass


def make_breaker_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_order_block_id: str | None = None,
    source_order_block_invalidation_transition_id: str | None = None,
    source_order_block_invalidation_snapshot_id: str | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    source_invalidation_index: int | None = None,
    source_invalidation_timestamp: datetime | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    breaker_id: str | None = None,
    from_state: BreakerBlockState | None = None,
    to_state: BreakerBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: BreakerBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    """Build an exact kind-specific Breaker Block identity."""

    try:
        return _make_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_order_block_id=source_order_block_id,
            source_order_block_invalidation_transition_id=source_order_block_invalidation_transition_id,
            source_order_block_invalidation_snapshot_id=source_order_block_invalidation_snapshot_id,
            structure_event_id=structure_event_id,
            structure_event_type=structure_event_type,
            wick_boundaries=wick_boundaries,
            body_boundaries=body_boundaries,
            proximal_tick=proximal_tick,
            distal_tick=distal_tick,
            midpoint_tick=midpoint_tick,
            source_invalidation_index=source_invalidation_index,
            source_invalidation_timestamp=source_invalidation_timestamp,
            confirmation_index=confirmation_index,
            confirmation_timestamp=confirmation_timestamp,
            breaker_id=breaker_id,
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
        raise ValueError("identity_kind is not a locked Breaker Block kind")
    direction = values["direction"]
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")
    payload: dict[str, object] = {
        "detector_version": BREAKER_BLOCK_DETECTOR_VERSION,
        "identity_kind": kind,
        "instrument": _text(values["instrument"], "instrument"),
        "timeframe": _text(values["timeframe"], "timeframe"),
        "direction": direction.value,
        "source_order_block_id": _hash(
            values["source_order_block_id"], "source_order_block_id"
        ),
        "source_order_block_invalidation_transition_id": _hash(
            values["source_order_block_invalidation_transition_id"],
            "source_order_block_invalidation_transition_id",
        ),
        "source_order_block_invalidation_snapshot_id": _hash(
            values["source_order_block_invalidation_snapshot_id"],
            "source_order_block_invalidation_snapshot_id",
        ),
        "structure_event_id": _hash(
            values["structure_event_id"], "structure_event_id"
        ),
    }
    geometry = (
        "structure_event_type",
        "wick_boundaries",
        "body_boundaries",
        "proximal_tick",
        "distal_tick",
        "midpoint_tick",
        "source_invalidation_index",
        "source_invalidation_timestamp",
        "confirmation_index",
        "confirmation_timestamp",
    )
    transition = (
        "breaker_id",
        "from_state",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
    )
    if kind == "BREAKER":
        _defaults(values, (*transition, "state", "transition_ids"))
        event_type = values["structure_event_type"]
        if not isinstance(event_type, DealingRangeEventType):
            raise TypeError("structure_event_type must be DealingRangeEventType")
        wick = _range(values["wick_boundaries"], "wick_boundaries")
        body = _range(values["body_boundaries"], "body_boundaries")
        if body.lower_tick < wick.lower_tick or body.upper_tick > wick.upper_tick:
            raise ValueError("body boundaries must be inside wick boundaries")
        proximal = _integer(values["proximal_tick"], "proximal_tick")
        distal = _integer(values["distal_tick"], "distal_tick")
        expected = (
            (wick.upper_tick, wick.lower_tick)
            if direction is SMCV2Direction.BULLISH
            else (wick.lower_tick, wick.upper_tick)
        )
        if (proximal, distal) != expected:
            raise ValueError("proximal/distal do not match role-reversed direction")
        midpoint = _midpoint(wick.lower_tick, wick.upper_tick)
        supplied_midpoint = values["midpoint_tick"]
        if not isinstance(supplied_midpoint, Decimal) or supplied_midpoint != midpoint:
            raise ValueError("midpoint_tick does not reconcile with wick boundaries")
        source_index = _nonnegative(
            values["source_invalidation_index"], "source_invalidation_index"
        )
        source_time = _timestamp(
            values["source_invalidation_timestamp"],
            "source_invalidation_timestamp",
        )
        confirmation_index = _nonnegative(
            values["confirmation_index"], "confirmation_index"
        )
        confirmation_time = _timestamp(
            values["confirmation_timestamp"], "confirmation_timestamp"
        )
        if (confirmation_index, confirmation_time) < (source_index, source_time):
            raise ValueError("confirmation cannot precede source invalidation")
        payload.update(
            {
                "structure_event_type": event_type.value,
                "wick_boundaries": [wick.lower_tick, wick.upper_tick],
                "body_boundaries": [body.lower_tick, body.upper_tick],
                "proximal_tick": proximal,
                "distal_tick": distal,
                "midpoint_tick": _decimal_text(midpoint),
                "source_invalidation_index": source_index,
                "source_invalidation_timestamp": _timestamp_text(source_time),
                "confirmation_index": confirmation_index,
                "confirmation_timestamp": _timestamp_text(confirmation_time),
            }
        )
    elif kind == "TRANSITION":
        _defaults(values, (*geometry, "state", "transition_ids"))
        breaker = _hash(values["breaker_id"], "breaker_id")
        from_state = values["from_state"]
        to_state = values["to_state"]
        reason_token = values["reason"]
        _edge(from_state, to_state, reason_token)
        index = _nonnegative(values["effective_index"], "effective_index")
        timestamp = _timestamp(
            values["effective_timestamp"], "effective_timestamp"
        )
        payload.update(
            {
                "breaker_id": breaker,
                "from_state": None if from_state is None else from_state.value,
                "to_state": to_state.value,
                "effective_index": index,
                "effective_timestamp": _timestamp_text(timestamp),
                "reason": reason_token,
            }
        )
    else:
        _defaults(values, (*geometry, "from_state", "to_state", "reason"))
        breaker = _hash(values["breaker_id"], "breaker_id")
        snapshot_state = values["state"]
        if not isinstance(snapshot_state, BreakerBlockState):
            raise TypeError("state must be BreakerBlockState")
        index = _nonnegative(values["effective_index"], "effective_index")
        timestamp = _timestamp(
            values["effective_timestamp"], "effective_timestamp"
        )
        ids = _hash_tuple(values["transition_ids"], "transition_ids")
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("transition_ids must be non-empty and unique")
        payload.update(
            {
                "breaker_id": breaker,
                "state": snapshot_state.value,
                "effective_index": index,
                "effective_timestamp": _timestamp_text(timestamp),
                "transition_ids": list(ids),
            }
        )
    canonical = json.dumps(
        payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def analyze_breaker_blocks(
    *,
    instrument: str,
    timeframe: str,
    order_blocks: tuple[OrderBlock, ...] | None,
    order_block_transitions: tuple[OrderBlockTransition, ...] | None,
    order_block_snapshots: tuple[OrderBlockSnapshot, ...] | None,
    swings: tuple[DealingRangeSwing, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    observations: tuple[BreakerBlockObservation, ...] | None,
) -> BreakerBlockResult:
    """Analyze canonical source failures and confirmed role reversals."""

    try:
        canonical_instrument = _text(instrument, "instrument")
        canonical_timeframe = _text(timeframe, "timeframe")
    except (TypeError, ValueError, AttributeError) as exc:
        return BreakerBlockResult(
            SMCV2PrimitiveStatus.INVALID,
            reasons=(str(exc),),
            blocking_reasons=(str(exc),),
        )
    missing = tuple(
        name
        for name, value in (
            ("order_blocks", order_blocks),
            ("order_block_transitions", order_block_transitions),
            ("order_block_snapshots", order_block_snapshots),
            ("swings", swings),
            ("structure_events", structure_events),
            ("observations", observations),
        )
        if value is None
    )
    if missing:
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return BreakerBlockResult(
            SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    state = _State([], [], [], {})
    try:
        if not isinstance(order_blocks, tuple):
            raise TypeError("order_blocks must be a tuple")
        if not isinstance(order_block_transitions, tuple):
            raise TypeError("order_block_transitions must be a tuple")
        if not isinstance(order_block_snapshots, tuple):
            raise TypeError("order_block_snapshots must be a tuple")
        if not isinstance(swings, tuple):
            raise TypeError("swings must be a tuple")
        if not isinstance(structure_events, tuple):
            raise TypeError("structure_events must be a tuple")
        if not isinstance(observations, tuple):
            raise TypeError("observations must be a tuple")

        observation_values, issue = _collect_observations(observations)
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        blocks, issue = _collect_blocks(
            canonical_instrument, canonical_timeframe, order_blocks
        )
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        histories, issue = _collect_histories(
            canonical_instrument,
            canonical_timeframe,
            blocks,
            order_block_transitions,
            order_block_snapshots,
        )
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        swing_values, issue = _collect_swings(swings, observation_values)
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        event_values, issue = _collect_events(
            canonical_instrument,
            canonical_timeframe,
            structure_events,
            swing_values,
            observation_values,
        )
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        issue = _collect_block_reference_issue(
            blocks, swing_values, event_values
        )
        if issue is not None:
            return _invalid_at_cutoff(
                canonical_instrument,
                canonical_timeframe,
                order_blocks,
                order_block_transitions,
                order_block_snapshots,
                swings,
                structure_events,
                observations,
                issue,
            )
        unknown = _analyze_valid(
            canonical_instrument,
            canonical_timeframe,
            histories,
            swing_values,
            event_values,
            observation_values,
            state,
        )
        if unknown:
            reason = "Source confirmation coverage remains incomplete"
            return _result(state, SMCV2PrimitiveStatus.UNKNOWN, reason)
        if state.breakers:
            return _result(state, SMCV2PrimitiveStatus.VALID, "Breaker evidence is valid")
        return BreakerBlockResult(SMCV2PrimitiveStatus.NONE)
    except _AmbiguousGroup as exc:
        return _result(
            state, SMCV2PrimitiveStatus.AMBIGUOUS, str(exc) or "Ambiguous event group"
        )
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return _invalid(state, str(exc) or "Malformed Breaker Block evidence")


def _validate_blocks(
    instrument: str, timeframe: str, values: tuple[OrderBlock, ...]
) -> tuple[OrderBlock, ...]:
    result: list[OrderBlock] = []
    prior: tuple[object, ...] | None = None
    ids: set[str] = set()
    for value in values:
        if type(value) is not OrderBlock:
            raise TypeError("every order block must be exact OrderBlock")
        direction = value.direction
        if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("source direction is invalid")
        source_index = _nonnegative(value.source_candle_index, "source_candle_index")
        source_time = _timestamp(
            value.source_candle_timestamp, "source_candle_timestamp"
        )
        displacement_indices = _indices(value.displacement_indices)
        displacement_times = _timestamps(
            value.displacement_timestamps, len(displacement_indices)
        )
        detection_index = _nonnegative(value.detection_index, "detection_index")
        detection_time = _timestamp(value.detection_timestamp, "detection_timestamp")
        if source_index >= displacement_indices[0] or source_time >= displacement_times[0]:
            raise ValueError("source candle must precede displacement")
        if (detection_index, detection_time) != (
            displacement_indices[-1],
            displacement_times[-1],
        ):
            raise ValueError("detection must equal final displacement moment")
        expected = make_order_block_id(
            identity_kind="BLOCK",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_candle_index=source_index,
            source_candle_timestamp=source_time,
            source_swing_id=_hash(value.source_swing_id, "source_swing_id"),
            displacement_indices=displacement_indices,
            displacement_timestamps=displacement_times,
            structure_event_id=_hash(value.structure_event_id, "structure_event_id"),
            structure_event_type=value.structure_event_type,
            wick_boundaries=SMCV2TickRange(
                _integer(value.wick_low_tick, "wick_low_tick"),
                _integer(value.wick_high_tick, "wick_high_tick"),
            ),
            body_boundaries=SMCV2TickRange(
                _integer(value.body_low_tick, "body_low_tick"),
                _integer(value.body_high_tick, "body_high_tick"),
            ),
            proximal_tick=_integer(value.proximal_tick, "proximal_tick"),
            distal_tick=_integer(value.distal_tick, "distal_tick"),
            midpoint_tick=value.midpoint_tick,
            detection_index=detection_index,
            detection_timestamp=detection_time,
        )
        if _hash(value.block_id, "block_id") != expected:
            raise ValueError("source Order Block identity is not canonical")
        key = (
            detection_index,
            detection_time,
            source_index,
            direction.value,
            displacement_indices,
            value.block_id,
        )
        if prior is not None and key <= prior:
            raise ValueError("source Order Blocks are not in canonical order")
        if value.block_id in ids:
            raise ValueError("duplicate source Order Block")
        result.append(value)
        ids.add(value.block_id)
        prior = key
    return tuple(result)


def _collect_blocks(
    instrument: str,
    timeframe: str,
    values: tuple[OrderBlock, ...],
) -> tuple[tuple[OrderBlock, ...], _Issue | None]:
    valid: tuple[OrderBlock, ...] = ()
    for value in values:
        try:
            valid = _validate_blocks(instrument, timeframe, (*valid, value))
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return valid, _Issue(
                _safe_block_moment(value),
                str(exc) or "malformed source Order Block",
            )
    return valid, None


def _validate_histories(
    instrument: str,
    timeframe: str,
    blocks: tuple[OrderBlock, ...],
    transitions: tuple[OrderBlockTransition, ...],
    snapshots: tuple[OrderBlockSnapshot, ...],
) -> tuple[_SourceHistory, ...]:
    block_map = {item.block_id: item for item in blocks}
    block_order = {item.block_id: position for position, item in enumerate(blocks)}
    transition_groups = {item.block_id: [] for item in blocks}
    snapshot_groups = {item.block_id: [] for item in blocks}
    prior_transition: tuple[object, ...] | None = None
    prior_snapshot: tuple[object, ...] | None = None
    for value in transitions:
        if type(value) is not OrderBlockTransition:
            raise TypeError("source transition must be exact OrderBlockTransition")
        block = block_map.get(_hash(value.block_id, "source transition block_id"))
        if block is None:
            raise ValueError("source transition references absent block")
        index = _nonnegative(value.index, "source transition index")
        timestamp = _timestamp(value.timestamp, "source transition timestamp")
        expected = make_order_block_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=block.direction,
            block_id=block.block_id,
            from_state=value.from_state,
            to_state=value.to_state,
            effective_index=index,
            effective_timestamp=timestamp,
            reason=value.reason,
        )
        if _hash(value.transition_id, "source transition_id") != expected:
            raise ValueError("source transition identity is not canonical")
        group = transition_groups[block.block_id]
        key = (index, timestamp, block_order[block.block_id], len(group))
        if prior_transition is not None and key < prior_transition:
            raise ValueError("source transitions are not in causal order")
        group.append(value)
        prior_transition = key
    for value in snapshots:
        if type(value) is not OrderBlockSnapshot:
            raise TypeError("source snapshot must be exact OrderBlockSnapshot")
        block = block_map.get(_hash(value.block_id, "source snapshot block_id"))
        if block is None:
            raise ValueError("source snapshot references absent block")
        if value.direction is not block.direction:
            raise ValueError("source snapshot direction contradicts source block")
        index = _nonnegative(value.index, "source snapshot index")
        timestamp = _timestamp(value.timestamp, "source snapshot timestamp")
        ids = _hash_tuple(value.transition_ids, "source snapshot transition_ids")
        expected = make_order_block_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=block.direction,
            block_id=block.block_id,
            state=value.state,
            effective_index=index,
            effective_timestamp=timestamp,
            transition_ids=ids,
        )
        if _hash(value.snapshot_id, "source snapshot_id") != expected:
            raise ValueError("source snapshot identity is not canonical")
        group = snapshot_groups[block.block_id]
        key = (index, timestamp, block_order[block.block_id], len(group))
        if prior_snapshot is not None and key < prior_snapshot:
            raise ValueError("source snapshots are not in causal order")
        group.append(value)
        prior_snapshot = key
    result: list[_SourceHistory] = []
    for block in blocks:
        source_transitions = tuple(transition_groups[block.block_id])
        source_snapshots = tuple(snapshot_groups[block.block_id])
        if not source_transitions or len(source_transitions) != len(source_snapshots):
            raise ValueError("source history must be complete one-to-one evidence")
        ids: tuple[str, ...] = ()
        previous: OrderBlockState | None = None
        invalidation: OrderBlockTransition | None = None
        invalidation_snapshot: OrderBlockSnapshot | None = None
        for transition, snapshot in zip(source_transitions, source_snapshots):
            if transition.from_state is not previous:
                raise ValueError("source transition chain is not contiguous")
            expected_reason = _SOURCE_REASONS.get(
                (transition.from_state, transition.to_state)
            )
            if expected_reason != transition.reason:
                raise ValueError("source transition edge/reason is invalid")
            ids = (*ids, transition.transition_id)
            if (
                snapshot.state is not transition.to_state
                or snapshot.index != transition.index
                or snapshot.timestamp != transition.timestamp
                or snapshot.transition_ids != ids
            ):
                raise ValueError("source snapshot does not mirror transition")
            previous = transition.to_state
            if transition.to_state is OrderBlockState.INVALIDATED:
                if invalidation is not None:
                    raise ValueError("source history has duplicate invalidation")
                invalidation = transition
                invalidation_snapshot = snapshot
        result.append(
            _SourceHistory(
                block,
                source_transitions,
                source_snapshots,
                invalidation,
                invalidation_snapshot,
            )
        )
    if not blocks and (transitions or snapshots):
        raise ValueError("source history exists without blocks")
    return tuple(result)


def _collect_histories(
    instrument: str,
    timeframe: str,
    blocks: tuple[OrderBlock, ...],
    transitions: tuple[OrderBlockTransition, ...],
    snapshots: tuple[OrderBlockSnapshot, ...],
) -> tuple[tuple[_SourceHistory, ...], _Issue | None]:
    try:
        return (
            _validate_histories(
                instrument, timeframe, blocks, transitions, snapshots
            ),
            None,
        )
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as overall:
        block_ids = {block.block_id for block in blocks}
        for value in transitions:
            try:
                if type(value) is not OrderBlockTransition:
                    raise TypeError(
                        "source transition must be exact OrderBlockTransition"
                    )
                if value.block_id not in block_ids:
                    raise ValueError("source transition references absent block")
            except (
                TypeError,
                ValueError,
                AttributeError,
                KeyError,
                IndexError,
            ) as exc:
                return (), _Issue(
                    _safe_record_moment(value),
                    str(exc) or "malformed source transition",
                )
        for value in snapshots:
            try:
                if type(value) is not OrderBlockSnapshot:
                    raise TypeError(
                        "source snapshot must be exact OrderBlockSnapshot"
                    )
                if value.block_id not in block_ids:
                    raise ValueError("source snapshot references absent block")
            except (
                TypeError,
                ValueError,
                AttributeError,
                KeyError,
                IndexError,
            ) as exc:
                return (), _Issue(
                    _safe_record_moment(value),
                    str(exc) or "malformed source snapshot",
                )
        for block in blocks:
            block_transitions = tuple(
                value for value in transitions if value.block_id == block.block_id
            )
            block_snapshots = tuple(
                value for value in snapshots if value.block_id == block.block_id
            )
            common = min(len(block_transitions), len(block_snapshots))
            for index in range(common):
                try:
                    _validate_histories(
                        instrument,
                        timeframe,
                        (block,),
                        block_transitions[: index + 1],
                        block_snapshots[: index + 1],
                    )
                except (
                    TypeError,
                    ValueError,
                    AttributeError,
                    KeyError,
                    IndexError,
                ) as exc:
                    moment = _earliest_known_moment(
                        _safe_record_moment(block_transitions[index]),
                        _safe_record_moment(block_snapshots[index]),
                    )
                    return (), _Issue(
                        moment, str(exc) or "malformed source history group"
                    )
            if len(block_transitions) != len(block_snapshots):
                extra = (
                    block_transitions[common]
                    if len(block_transitions) > common
                    else block_snapshots[common]
                )
                return (), _Issue(
                    _safe_record_moment(extra),
                    "source history must be complete one-to-one evidence",
                )
        for stream in (transitions, snapshots):
            prior: _Moment | None = None
            for value in stream:
                moment = _safe_record_moment(value)
                if moment is None:
                    return (), _Issue(None, str(overall))
                if prior is not None and moment < prior:
                    return (), _Issue(
                        moment, "source history stream is not in causal order"
                    )
                prior = moment
        fallback = _latest_known_moment(
            *(_safe_record_moment(value) for value in (*transitions, *snapshots))
        )
        return (), _Issue(fallback, str(overall) or "malformed source history")


def _validate_swings(
    values: tuple[DealingRangeSwing, ...],
    observations: tuple[BreakerBlockObservation, ...],
) -> tuple[DealingRangeSwing, ...]:
    observation_map = {item.index: item for item in observations}
    result: list[DealingRangeSwing] = []
    prior: tuple[object, ...] | None = None
    ids: set[str] = set()
    source_sides: set[tuple[int, DealingRangeSwingSide]] = set()
    for value in values:
        if type(value) is not DealingRangeSwing:
            raise TypeError("every swing must be exact DealingRangeSwing")
        if value.side not in (DealingRangeSwingSide.HIGH, DealingRangeSwingSide.LOW):
            raise ValueError("swing side is invalid")
        price = _integer(value.price_tick, "swing price_tick")
        provenance = _provenance(value.provenance, exact_one=True)
        source_index = provenance.source_indices[0]
        if provenance.confirmation_index < source_index + 2:
            raise ValueError("swing confirmation must respect the two-bar delay")
        source_observation = observation_map.get(source_index)
        if source_observation is not None:
            if source_observation.timestamp != provenance.source_timestamps[0]:
                raise ValueError("swing source timestamp contradicts observation")
            expected_price = (
                source_observation.high_tick
                if value.side is DealingRangeSwingSide.HIGH
                else source_observation.low_tick
            )
            if price != expected_price:
                raise ValueError("swing price contradicts source observation")
        elif _inside_horizon(source_index, observations):
            raise ValueError("in-horizon swing source observation is missing")
        confirmation_observation = observation_map.get(
            provenance.confirmation_index
        )
        if (
            confirmation_observation is not None
            and confirmation_observation.timestamp
            != provenance.confirmation_timestamp
        ):
            raise ValueError("swing confirmation timestamp contradicts observation")
        if confirmation_observation is None and _inside_horizon(
            provenance.confirmation_index, observations
        ):
            raise ValueError("in-horizon swing confirmation observation is missing")
        swing_id = _hash(value.swing_id, "swing_id")
        key = (
            provenance.confirmation_index,
            source_index,
            value.side.value,
            swing_id,
        )
        if prior is not None and key <= prior:
            raise ValueError("swings are not in canonical order")
        if swing_id in ids:
            raise ValueError("duplicate swing identity")
        source_side = (source_index, value.side)
        if source_side in source_sides:
            raise ValueError("duplicate swing source-side identity")
        result.append(value)
        ids.add(swing_id)
        source_sides.add(source_side)
        prior = key
    return tuple(result)


def _collect_swings(
    values: tuple[DealingRangeSwing, ...],
    observations: tuple[BreakerBlockObservation, ...],
) -> tuple[tuple[DealingRangeSwing, ...], _Issue | None]:
    valid: tuple[DealingRangeSwing, ...] = ()
    for value in values:
        try:
            valid = _validate_swings((*valid, value), observations)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return valid, _Issue(
                _safe_swing_moment(value),
                str(exc) or "malformed confirmed swing",
            )
    return valid, None


def _validate_events(
    instrument: str,
    timeframe: str,
    values: tuple[DealingRangeStructureEvent, ...],
    swings: tuple[DealingRangeSwing, ...],
    observations: tuple[BreakerBlockObservation, ...],
) -> tuple[DealingRangeStructureEvent, ...]:
    swing_map = {item.swing_id: item for item in swings}
    observation_map = {item.index: item for item in observations}
    result: list[DealingRangeStructureEvent] = []
    prior: tuple[object, ...] | None = None
    event_ids: set[str] = set()
    same_group: dict[tuple[int, datetime, SMCV2Direction], int] = {}
    for value in values:
        if type(value) is not DealingRangeStructureEvent:
            raise TypeError("every event must be exact DealingRangeStructureEvent")
        if value.direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("event direction is invalid")
        if value.event_type not in (
            DealingRangeEventType.BOS,
            DealingRangeEventType.CHOCH,
        ):
            raise ValueError("event type is invalid")
        swing_id = _hash(value.broken_swing_id, "broken_swing_id")
        swing = swing_map.get(swing_id)
        if swing is None:
            raise ValueError("event references absent swing")
        required_side = (
            DealingRangeSwingSide.HIGH
            if value.direction is SMCV2Direction.BULLISH
            else DealingRangeSwingSide.LOW
        )
        if swing.side is not required_side:
            raise ValueError("event direction contradicts swing side")
        provenance = _provenance(value.provenance, exact_one=False)
        if any(
            later != earlier + 1
            for earlier, later in zip(
                provenance.source_indices, provenance.source_indices[1:]
            )
        ):
            raise ValueError("event provenance source indices must be contiguous")
        if (
            provenance.source_indices[-1] != provenance.confirmation_index
            or provenance.source_timestamps[-1]
            != provenance.confirmation_timestamp
        ):
            raise ValueError("event source must equal confirmation moment")
        if swing.provenance.confirmation_index >= provenance.source_indices[0]:
            raise ValueError("broken swing must confirm before event displacement")
        for source_index, source_timestamp in zip(
            provenance.source_indices, provenance.source_timestamps
        ):
            source_observation = observation_map.get(source_index)
            if source_observation is None:
                if observations and source_index >= observations[0].index:
                    raise ValueError("in-horizon event source observation is missing")
                continue
            if source_observation.timestamp != source_timestamp:
                raise ValueError("event provenance timestamp contradicts observation")
        observation = observation_map.get(provenance.confirmation_index)
        if observation is not None:
            if observation.timestamp != provenance.confirmation_timestamp:
                raise ValueError("event timestamp contradicts observation")
            if (
                value.direction is SMCV2Direction.BULLISH
                and observation.close_tick < swing.price_tick + 1
            ) or (
                value.direction is SMCV2Direction.BEARISH
                and observation.close_tick > swing.price_tick - 1
            ):
                raise ValueError("confirmed event lacks exact close break")
        expected = make_dealing_range_id(
            identity_kind="EVENT",
            instrument=instrument,
            timeframe=timeframe,
            direction=value.direction,
            source_indices=provenance.source_indices,
            event_type=value.event_type,
            broken_swing_id=swing.swing_id,
            confirmation_index=provenance.confirmation_index,
            boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick),
        )
        if _hash(value.event_id, "event_id") != expected:
            raise ValueError("event identity is not canonical")
        key = (
            provenance.confirmation_index,
            provenance.confirmation_timestamp,
            value.direction.value,
            value.event_type.value,
            value.event_id,
        )
        if prior is not None and key <= prior:
            raise ValueError("events are not in canonical order")
        if value.event_id in event_ids:
            raise ValueError("duplicate event identity")
        group_key = (
            provenance.confirmation_index,
            provenance.confirmation_timestamp,
            value.direction,
        )
        same_group[group_key] = same_group.get(group_key, 0) + 1
        if same_group[group_key] > 1:
            raise ValueError("same-direction event fork is invalid")
        result.append(value)
        event_ids.add(value.event_id)
        prior = key
    return tuple(result)


def _collect_events(
    instrument: str,
    timeframe: str,
    values: tuple[DealingRangeStructureEvent, ...],
    swings: tuple[DealingRangeSwing, ...],
    observations: tuple[BreakerBlockObservation, ...],
) -> tuple[tuple[DealingRangeStructureEvent, ...], _Issue | None]:
    valid: tuple[DealingRangeStructureEvent, ...] = ()
    for value in values:
        try:
            valid = _validate_events(
                instrument,
                timeframe,
                (*valid, value),
                swings,
                observations,
            )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return valid, _Issue(
                _safe_event_moment(value),
                str(exc) or "malformed confirmed structure event",
            )
    return valid, None


def _validate_block_references(
    blocks: tuple[OrderBlock, ...],
    swings: tuple[DealingRangeSwing, ...],
    events: tuple[DealingRangeStructureEvent, ...],
) -> None:
    swing_map = {item.swing_id: item for item in swings}
    event_map = {item.event_id: item for item in events}
    for block in blocks:
        swing = swing_map.get(block.source_swing_id)
        if swing is None:
            raise ValueError("source Order Block references absent swing")
        event = event_map.get(block.structure_event_id)
        if event is None:
            raise ValueError("source Order Block references absent structure event")
        if (
            event.direction is not block.direction
            or event.event_type is not block.structure_event_type
            or event.broken_swing_id != swing.swing_id
            or event.provenance.confirmation_index != block.detection_index
            or event.provenance.confirmation_timestamp != block.detection_timestamp
        ):
            raise ValueError("source Order Block swing/event references do not reconcile")
        displacement_length = len(block.displacement_indices)
        if (
            event.provenance.source_indices[-displacement_length:]
            != block.displacement_indices
            or event.provenance.source_timestamps[-displacement_length:]
            != block.displacement_timestamps
        ):
            raise ValueError("source event provenance does not bind displacement suffix")


def _collect_block_reference_issue(
    blocks: tuple[OrderBlock, ...],
    swings: tuple[DealingRangeSwing, ...],
    events: tuple[DealingRangeStructureEvent, ...],
) -> _Issue | None:
    for block in blocks:
        try:
            _validate_block_references((block,), swings, events)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return _Issue(
                _safe_block_moment(block),
                str(exc) or "source Order Block reference mismatch",
            )
    return None


def _analyze_valid(
    instrument: str,
    timeframe: str,
    histories: tuple[_SourceHistory, ...],
    swings: tuple[DealingRangeSwing, ...],
    events: tuple[DealingRangeStructureEvent, ...],
    observations: tuple[BreakerBlockObservation, ...],
    state: _State,
) -> bool:
    observation_map = {item.index: item for item in observations}
    event_groups: dict[tuple[int, datetime], list[DealingRangeStructureEvent]] = {}
    for event in events:
        moment = (
            event.provenance.confirmation_index,
            event.provenance.confirmation_timestamp,
        )
        event_groups.setdefault(moment, []).append(event)

    unknown = False
    formation_by_moment: dict[_Moment, list[tuple[_SourceHistory, DealingRangeStructureEvent]]] = {}
    ambiguous_moments: set[_Moment] = set()
    for history in histories:
        transition = history.invalidation
        snapshot = history.invalidation_snapshot
        if transition is None or snapshot is None:
            final_snapshot = history.snapshots[-1]
            for observation in observations:
                if (
                    _observation_moment(observation)
                    > (final_snapshot.index, final_snapshot.timestamp)
                    and _source_close_through(history.block, observation)
                ):
                    raise ValueError(
                        "source close-through lacks invalidation transition/snapshot"
                    )
            continue
        invalidation_observation = observation_map.get(transition.index)
        if invalidation_observation is None:
            if not observations or transition.index < observations[0].index:
                unknown = True
                continue
            raise ValueError("in-horizon source invalidation observation is missing")
        if invalidation_observation.timestamp != transition.timestamp:
            raise ValueError("source invalidation timestamp mismatch")
        block = history.block
        for earlier in observations:
            if _observation_moment(earlier) >= (
                transition.index,
                transition.timestamp,
            ):
                break
            if (
                _observation_moment(earlier)
                > (block.detection_index, block.detection_timestamp)
                and _source_close_through(block, earlier)
            ):
                raise ValueError(
                    "source close-through precedes claimed invalidation history"
                )
        if not _source_close_through(block, invalidation_observation):
            raise ValueError("source invalidation geometry does not reconcile")
        proposed = _opposite(block.direction)
        window = tuple(
            item
            for item in observations
            if _observation_moment(item) >= _observation_moment(invalidation_observation)
        )[:11]
        candidate: DealingRangeStructureEvent | None = None
        for observation in window:
            group = event_groups.get(_observation_moment(observation), ())
            matching = tuple(item for item in group if item.direction is proposed)
            if matching:
                if len(matching) != 1:
                    raise ValueError("event group has duplicate proposed direction")
                candidate = matching[0]
                directions = {item.direction for item in group}
                if directions == {
                    SMCV2Direction.BULLISH,
                    SMCV2Direction.BEARISH,
                }:
                    ambiguous_moments.add(_observation_moment(observation))
                    candidate = None
                break
        if candidate is None:
            if len(window) < 11:
                unknown = True
            continue
        moment = (
            candidate.provenance.confirmation_index,
            candidate.provenance.confirmation_timestamp,
        )
        formation_by_moment.setdefault(moment, []).append((history, candidate))

    for observation in observations:
        moment = _observation_moment(observation)
        if moment in ambiguous_moments:
            raise _AmbiguousGroup(
                "Opposing canonical events share one confirmation group"
            )
        group_state = state.clone()
        for breaker_id in tuple(group_state.runtimes):
            runtime = group_state.runtimes[breaker_id]
            if moment <= (
                runtime.breaker.confirmation_index,
                runtime.breaker.confirmation_timestamp,
            ):
                continue
            target = _target(runtime.breaker, runtime.state, observation)
            if target is not None and target is not runtime.state:
                _append_transition(
                    instrument,
                    timeframe,
                    group_state,
                    runtime,
                    target,
                    observation,
                )
        for history, event in formation_by_moment.get(moment, ()):
            if history.block.block_id in group_state.runtimes:
                raise ValueError("source block attempts duplicate Breaker formation")
            _append_creation(
                instrument,
                timeframe,
                group_state,
                history,
                event,
            )
        state.breakers = group_state.breakers
        state.transitions = group_state.transitions
        state.snapshots = group_state.snapshots
        state.runtimes = group_state.runtimes
    return unknown


def _append_creation(
    instrument: str,
    timeframe: str,
    state: _State,
    history: _SourceHistory,
    event: DealingRangeStructureEvent,
) -> None:
    block = history.block
    transition = history.invalidation
    snapshot = history.invalidation_snapshot
    if transition is None or snapshot is None:
        raise ValueError("source invalidation evidence is incomplete")
    direction = _opposite(block.direction)
    proximal, distal = (
        (block.wick_high_tick, block.wick_low_tick)
        if direction is SMCV2Direction.BULLISH
        else (block.wick_low_tick, block.wick_high_tick)
    )
    midpoint = _midpoint(block.wick_low_tick, block.wick_high_tick)
    kwargs = dict(
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_order_block_id=block.block_id,
        source_order_block_invalidation_transition_id=transition.transition_id,
        source_order_block_invalidation_snapshot_id=snapshot.snapshot_id,
        structure_event_id=event.event_id,
    )
    breaker_id = make_breaker_block_id(
        identity_kind="BREAKER",
        **kwargs,
        structure_event_type=event.event_type,
        wick_boundaries=SMCV2TickRange(block.wick_low_tick, block.wick_high_tick),
        body_boundaries=SMCV2TickRange(block.body_low_tick, block.body_high_tick),
        proximal_tick=proximal,
        distal_tick=distal,
        midpoint_tick=midpoint,
        source_invalidation_index=transition.index,
        source_invalidation_timestamp=transition.timestamp,
        confirmation_index=event.provenance.confirmation_index,
        confirmation_timestamp=event.provenance.confirmation_timestamp,
    )
    breaker = BreakerBlock(
        breaker_id,
        direction,
        block.block_id,
        transition.transition_id,
        snapshot.snapshot_id,
        event.event_id,
        event.event_type,
        block.wick_low_tick,
        block.wick_high_tick,
        block.body_low_tick,
        block.body_high_tick,
        proximal,
        distal,
        midpoint,
        transition.index,
        transition.timestamp,
        event.provenance.confirmation_index,
        event.provenance.confirmation_timestamp,
    )
    transition_id = make_breaker_block_id(
        identity_kind="TRANSITION",
        **kwargs,
        breaker_id=breaker_id,
        from_state=None,
        to_state=BreakerBlockState.ACTIVE,
        effective_index=breaker.confirmation_index,
        effective_timestamp=breaker.confirmation_timestamp,
        reason=_CREATION,
    )
    creation = BreakerBlockTransition(
        transition_id,
        breaker_id,
        block.block_id,
        transition.transition_id,
        snapshot.snapshot_id,
        event.event_id,
        None,
        BreakerBlockState.ACTIVE,
        breaker.confirmation_index,
        breaker.confirmation_timestamp,
        _CREATION,
    )
    snapshot_id = make_breaker_block_id(
        identity_kind="SNAPSHOT",
        **kwargs,
        breaker_id=breaker_id,
        state=BreakerBlockState.ACTIVE,
        effective_index=breaker.confirmation_index,
        effective_timestamp=breaker.confirmation_timestamp,
        transition_ids=(transition_id,),
    )
    current = BreakerBlockSnapshot(
        snapshot_id,
        breaker_id,
        block.block_id,
        transition.transition_id,
        snapshot.snapshot_id,
        event.event_id,
        direction,
        BreakerBlockState.ACTIVE,
        breaker.confirmation_index,
        breaker.confirmation_timestamp,
        (transition_id,),
    )
    state.breakers.append(breaker)
    state.transitions.append(creation)
    state.snapshots.append(current)
    state.runtimes[block.block_id] = _Runtime(
        breaker, BreakerBlockState.ACTIVE, (transition_id,)
    )


def _append_transition(
    instrument: str,
    timeframe: str,
    state: _State,
    runtime: _Runtime,
    target: BreakerBlockState,
    observation: BreakerBlockObservation,
) -> None:
    breaker = runtime.breaker
    reason = {
        BreakerBlockState.TOUCHED: _TOUCH,
        BreakerBlockState.PARTIALLY_MITIGATED: _PARTIAL,
        BreakerBlockState.MITIGATED: _MITIGATION,
        BreakerBlockState.INVALIDATED: _INVALIDATION,
    }[target]
    kwargs = dict(
        instrument=instrument,
        timeframe=timeframe,
        direction=breaker.direction,
        source_order_block_id=breaker.source_order_block_id,
        source_order_block_invalidation_transition_id=breaker.source_order_block_invalidation_transition_id,
        source_order_block_invalidation_snapshot_id=breaker.source_order_block_invalidation_snapshot_id,
        structure_event_id=breaker.structure_event_id,
        breaker_id=breaker.breaker_id,
    )
    transition_id = make_breaker_block_id(
        identity_kind="TRANSITION",
        **kwargs,
        from_state=runtime.state,
        to_state=target,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        reason=reason,
    )
    transition = BreakerBlockTransition(
        transition_id,
        breaker.breaker_id,
        breaker.source_order_block_id,
        breaker.source_order_block_invalidation_transition_id,
        breaker.source_order_block_invalidation_snapshot_id,
        breaker.structure_event_id,
        runtime.state,
        target,
        observation.index,
        observation.timestamp,
        reason,
    )
    ids = (*runtime.transition_ids, transition_id)
    snapshot_id = make_breaker_block_id(
        identity_kind="SNAPSHOT",
        **kwargs,
        state=target,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        transition_ids=ids,
    )
    snapshot = BreakerBlockSnapshot(
        snapshot_id,
        breaker.breaker_id,
        breaker.source_order_block_id,
        breaker.source_order_block_invalidation_transition_id,
        breaker.source_order_block_invalidation_snapshot_id,
        breaker.structure_event_id,
        breaker.direction,
        target,
        observation.index,
        observation.timestamp,
        ids,
    )
    state.transitions.append(transition)
    state.snapshots.append(snapshot)
    state.runtimes[breaker.source_order_block_id] = _Runtime(
        breaker, target, ids
    )


def _target(
    breaker: BreakerBlock,
    current: BreakerBlockState,
    observation: BreakerBlockObservation,
) -> BreakerBlockState | None:
    if current is BreakerBlockState.INVALIDATED:
        return None
    if breaker.direction is SMCV2Direction.BULLISH:
        if observation.close_tick <= breaker.distal_tick - 1:
            return BreakerBlockState.INVALIDATED
        if current is BreakerBlockState.MITIGATED:
            return None
        if Decimal(observation.low_tick) <= breaker.midpoint_tick:
            return BreakerBlockState.MITIGATED
        if observation.low_tick < breaker.proximal_tick:
            candidate = BreakerBlockState.PARTIALLY_MITIGATED
        elif observation.low_tick == breaker.proximal_tick:
            candidate = BreakerBlockState.TOUCHED
        else:
            return None
    else:
        if observation.close_tick >= breaker.distal_tick + 1:
            return BreakerBlockState.INVALIDATED
        if current is BreakerBlockState.MITIGATED:
            return None
        if Decimal(observation.high_tick) >= breaker.midpoint_tick:
            return BreakerBlockState.MITIGATED
        if observation.high_tick > breaker.proximal_tick:
            candidate = BreakerBlockState.PARTIALLY_MITIGATED
        elif observation.high_tick == breaker.proximal_tick:
            candidate = BreakerBlockState.TOUCHED
        else:
            return None
    rank = {
        BreakerBlockState.ACTIVE: 0,
        BreakerBlockState.TOUCHED: 1,
        BreakerBlockState.PARTIALLY_MITIGATED: 2,
        BreakerBlockState.MITIGATED: 3,
    }
    return candidate if rank[candidate] > rank[current] else None


def _source_close_through(
    block: OrderBlock, observation: BreakerBlockObservation
) -> bool:
    return (
        observation.close_tick <= block.distal_tick - 1
        if block.direction is SMCV2Direction.BULLISH
        else observation.close_tick >= block.distal_tick + 1
    )


def _collect_observations(
    values: tuple[BreakerBlockObservation, ...],
) -> tuple[tuple[BreakerBlockObservation, ...], _Issue | None]:
    result: list[BreakerBlockObservation] = []
    prior_index: int | None = None
    prior_time: datetime | None = None
    for value in values:
        try:
            if type(value) is not BreakerBlockObservation:
                raise TypeError("every observation must be exact BreakerBlockObservation")
            index = _nonnegative(value.index, "observation index")
            timestamp = _timestamp(value.timestamp, "observation timestamp")
            high = _integer(value.high_tick, "observation high_tick")
            low = _integer(value.low_tick, "observation low_tick")
            close = _integer(value.close_tick, "observation close_tick")
            if low > high or not low <= close <= high:
                raise ValueError("observation OHLC ticks are inconsistent")
            if prior_index is not None and index <= prior_index:
                raise ValueError("observation indices must be strictly increasing")
            if prior_time is not None and timestamp <= prior_time:
                raise ValueError("observation timestamps must be strictly increasing")
            normalized = BreakerBlockObservation(index, timestamp, high, low, close)
            result.append(normalized)
            prior_index = index
            prior_time = timestamp
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(result), _Issue(
                _safe_moment(value), str(exc) or "malformed observation"
            )
    return tuple(result), None


def _edge(
    from_state: object, to_state: object, reason: object
) -> None:
    if from_state is not None and not isinstance(from_state, BreakerBlockState):
        raise TypeError("from_state must be BreakerBlockState or None")
    if not isinstance(to_state, BreakerBlockState):
        raise TypeError("to_state must be BreakerBlockState")
    if not isinstance(reason, str) or reason not in _REASONS:
        raise ValueError("reason is not a locked Breaker Block reason")
    if from_state is None:
        valid = to_state is BreakerBlockState.ACTIVE and reason == _CREATION
    elif from_state is BreakerBlockState.INVALIDATED:
        valid = False
    elif to_state is BreakerBlockState.INVALIDATED:
        valid = reason == _INVALIDATION
    else:
        rank = {
            BreakerBlockState.ACTIVE: 0,
            BreakerBlockState.TOUCHED: 1,
            BreakerBlockState.PARTIALLY_MITIGATED: 2,
            BreakerBlockState.MITIGATED: 3,
        }
        expected_reason = {
            BreakerBlockState.TOUCHED: _TOUCH,
            BreakerBlockState.PARTIALLY_MITIGATED: _PARTIAL,
            BreakerBlockState.MITIGATED: _MITIGATION,
        }.get(to_state)
        valid = (
            from_state in rank
            and to_state in rank
            and rank[to_state] > rank[from_state]
            and reason == expected_reason
        )
    if not valid:
        raise ValueError("impossible Breaker Block lifecycle edge")


def _provenance(value: object, *, exact_one: bool) -> SMCV2EventProvenance:
    if type(value) is not SMCV2EventProvenance:
        raise TypeError("provenance must be exact SMCV2EventProvenance")
    indices = value.source_indices
    timestamps = value.source_timestamps
    if not isinstance(indices, tuple) or not isinstance(timestamps, tuple):
        raise TypeError("provenance source members must be tuples")
    if len(indices) != len(timestamps) or not indices:
        raise ValueError("provenance source tuples must be non-empty and equal")
    if exact_one and len(indices) != 1:
        raise ValueError("provenance must contain exactly one source")
    normalized_indices = tuple(_nonnegative(item, "source index") for item in indices)
    normalized_times = tuple(_timestamp(item, "source timestamp") for item in timestamps)
    if any(
        later <= earlier
        for earlier, later in zip(normalized_indices, normalized_indices[1:])
    ) or any(
        later <= earlier
        for earlier, later in zip(normalized_times, normalized_times[1:])
    ):
        raise ValueError("provenance sources must be strictly increasing")
    confirmation_index = _nonnegative(
        value.confirmation_index, "confirmation_index"
    )
    confirmation_time = _timestamp(
        value.confirmation_timestamp, "confirmation_timestamp"
    )
    if normalized_indices[-1] > confirmation_index or normalized_times[-1] > confirmation_time:
        raise ValueError("provenance source cannot follow confirmation")
    return SMCV2EventProvenance(
        normalized_indices,
        normalized_times,
        confirmation_index,
        confirmation_time,
    )


def _inside_horizon(
    index: int, observations: tuple[BreakerBlockObservation, ...]
) -> bool:
    return bool(
        observations
        and observations[0].index <= index <= observations[-1].index
    )


def _safe_block_moment(value: object) -> _Moment | None:
    try:
        return (
            _nonnegative(getattr(value, "detection_index"), "detection_index"),
            _timestamp(
                getattr(value, "detection_timestamp"), "detection_timestamp"
            ),
        )
    except (TypeError, ValueError, AttributeError):
        return None


def _safe_record_moment(value: object) -> _Moment | None:
    return _safe_moment(value)


def _safe_swing_moment(value: object) -> _Moment | None:
    try:
        provenance = getattr(value, "provenance")
        return (
            _nonnegative(
                getattr(provenance, "confirmation_index"),
                "confirmation_index",
            ),
            _timestamp(
                getattr(provenance, "confirmation_timestamp"),
                "confirmation_timestamp",
            ),
        )
    except (TypeError, ValueError, AttributeError):
        return None


def _safe_event_moment(value: object) -> _Moment | None:
    return _safe_swing_moment(value)


def _earliest_known_moment(
    *moments: _Moment | None,
) -> _Moment | None:
    known = tuple(moment for moment in moments if moment is not None)
    return min(known) if known else None


def _latest_known_moment(
    *moments: _Moment | None,
) -> _Moment | None:
    known = tuple(moment for moment in moments if moment is not None)
    return max(known) if known else None


def _safe_moment(value: object) -> _Moment | None:
    try:
        index = getattr(value, "index")
        timestamp = getattr(value, "timestamp")
        return (_nonnegative(index, "index"), _timestamp(timestamp, "timestamp"))
    except (TypeError, ValueError, AttributeError):
        return None


def _observation_moment(value: BreakerBlockObservation) -> _Moment:
    return (value.index, value.timestamp)


def _opposite(direction: SMCV2Direction) -> SMCV2Direction:
    return (
        SMCV2Direction.BEARISH
        if direction is SMCV2Direction.BULLISH
        else SMCV2Direction.BULLISH
    )


def _midpoint(low: int, high: int) -> Decimal:
    total = low + high
    sign = "-" if total < 0 else ""
    magnitude = abs(total)
    whole, remainder = divmod(magnitude, 2)
    return Decimal(f"{sign}{whole}.{'5' if remainder else '0'}")


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0.0"
    text = format(value, "f")
    if "." not in text:
        return f"{text}.0"
    whole, fraction = text.split(".", 1)
    if set(fraction) <= {"0"}:
        return f"{whole}.0"
    if fraction == "5":
        return text
    raise ValueError("midpoint must be an exact integer or half tick")


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip().upper()


def _integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    return value


def _nonnegative(value: object, name: str) -> int:
    integer = _integer(value, name)
    if integer < 0:
        raise ValueError(f"{name} must be non-negative")
    return integer


def _timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return normalize_utc_timestamp(value)


def _timestamp_text(value: datetime) -> str:
    return _timestamp(value, "timestamp").strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _hash(value: object, name: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return value


def _hash_tuple(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    return tuple(_hash(item, name) for item in value)


def _range(value: object, name: str) -> SMCV2TickRange:
    if type(value) is not SMCV2TickRange:
        raise TypeError(f"{name} must be exact SMCV2TickRange")
    return SMCV2TickRange(
        _integer(value.lower_tick, f"{name}.lower_tick"),
        _integer(value.upper_tick, f"{name}.upper_tick"),
    )


def _indices(value: object) -> tuple[int, ...]:
    if not isinstance(value, tuple) or not 1 <= len(value) <= 3:
        raise ValueError("displacement_indices must have length 1 through 3")
    result = tuple(_nonnegative(item, "displacement index") for item in value)
    if any(later <= earlier for earlier, later in zip(result, result[1:])):
        raise ValueError("displacement indices must be strictly increasing")
    return result


def _timestamps(value: object, length: int) -> tuple[datetime, ...]:
    if not isinstance(value, tuple) or len(value) != length:
        raise ValueError("displacement timestamps must match indices")
    result = tuple(_timestamp(item, "displacement timestamp") for item in value)
    if any(later <= earlier for earlier, later in zip(result, result[1:])):
        raise ValueError("displacement timestamps must be strictly increasing")
    return result


def _defaults(values: dict[str, object], names: tuple[str, ...]) -> None:
    for name in names:
        expected = () if name == "transition_ids" else None
        if values[name] != expected:
            raise ValueError(f"{name} is forbidden for this identity kind")


def _invalid_at_cutoff(
    instrument: str,
    timeframe: str,
    order_blocks: tuple[OrderBlock, ...],
    order_block_transitions: tuple[OrderBlockTransition, ...],
    order_block_snapshots: tuple[OrderBlockSnapshot, ...],
    swings: tuple[DealingRangeSwing, ...],
    structure_events: tuple[DealingRangeStructureEvent, ...],
    observations: tuple[BreakerBlockObservation, ...],
    issue: _Issue,
) -> BreakerBlockResult:
    cutoff = issue.moment
    if cutoff is None:
        return BreakerBlockResult(
            SMCV2PrimitiveStatus.INVALID,
            reasons=(issue.reason,),
            blocking_reasons=(issue.reason,),
        )
    prefix = analyze_breaker_blocks(
        instrument=instrument,
        timeframe=timeframe,
        order_blocks=tuple(
            value
            for value in order_blocks
            if (moment := _safe_block_moment(value)) is not None
            and moment < cutoff
        ),
        order_block_transitions=tuple(
            value
            for value in order_block_transitions
            if (moment := _safe_record_moment(value)) is not None
            and moment < cutoff
        ),
        order_block_snapshots=tuple(
            value
            for value in order_block_snapshots
            if (moment := _safe_record_moment(value)) is not None
            and moment < cutoff
        ),
        swings=tuple(
            value
            for value in swings
            if (moment := _safe_swing_moment(value)) is not None
            and moment < cutoff
        ),
        structure_events=tuple(
            value
            for value in structure_events
            if (moment := _safe_event_moment(value)) is not None
            and moment < cutoff
        ),
        observations=tuple(
            value
            for value in observations
            if (moment := _safe_moment(value)) is not None and moment < cutoff
        ),
    )
    return BreakerBlockResult(
        SMCV2PrimitiveStatus.INVALID,
        prefix.breakers,
        prefix.transitions,
        prefix.snapshots,
        (issue.reason,),
        (issue.reason,),
    )


def _invalid(state: _State, reason: str) -> BreakerBlockResult:
    return _result(state, SMCV2PrimitiveStatus.INVALID, reason)


def _result(
    state: _State, status: SMCV2PrimitiveStatus, reason: str
) -> BreakerBlockResult:
    blocking = (reason,) if status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ) else ()
    return BreakerBlockResult(
        status,
        tuple(state.breakers),
        tuple(state.transitions),
        tuple(state.snapshots),
        (reason,),
        blocking,
    )


__all__ = [
    "BREAKER_BLOCK_DETECTOR_VERSION",
    "BreakerBlockState",
    "BreakerBlockObservation",
    "BreakerBlock",
    "BreakerBlockTransition",
    "BreakerBlockSnapshot",
    "BreakerBlockResult",
    "make_breaker_block_id",
    "analyze_breaker_blocks",
]
