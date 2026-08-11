"""Deterministic standalone Swing Hierarchy and Dealing Range diagnostics.

The detector consumes immutable confirmed swings, closed integer-tick bars, and
caller-supplied confirmed structure events. It is isolated from current runtime
paths and performs no I/O or registration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


DEALING_RANGE_DETECTOR_VERSION = "SMC-V2-DEALING-RANGE-1"

_IDENTITY_KINDS = frozenset({
    "EVENT",
    "TRANSITION",
    "LINEAGE",
    "SNAPSHOT",
    "INTERNAL_RANGE",
})
_REASON_CONSTRUCTION = "CONSTRUCTION_ACTIVE"
_REASON_OBSERVATION = "OBSERVATION_CLOSE_THROUGH_INVALIDATION"
_REASON_CHOCH = "CHOCH_CLOSE_THROUGH_INVALIDATION"
_REASON_REPLACEMENT = "BOS_PULLBACK_REPLACEMENT"
_REASON_TOKENS = frozenset({
    _REASON_CONSTRUCTION,
    _REASON_OBSERVATION,
    _REASON_CHOCH,
    _REASON_REPLACEMENT,
})
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_MISSING = object()


class DealingRangeSwingSide(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class DealingRangeEventType(str, Enum):
    BOS = "BOS"
    CHOCH = "CHOCH"


class DealingRangeKind(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


class DealingRangeState(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class DealingRangeConfig:
    swing_confirmation_bars: int = 2
    break_buffer_ticks: int = 1

    def __post_init__(self) -> None:
        if type(self.swing_confirmation_bars) is not int:
            raise TypeError("swing_confirmation_bars must be an integer")
        if type(self.break_buffer_ticks) is not int:
            raise TypeError("break_buffer_ticks must be an integer")
        if (self.swing_confirmation_bars, self.break_buffer_ticks) != (2, 1):
            raise ValueError("this detector version requires the locked 2/1 configuration")


@dataclass(frozen=True)
class DealingRangeSwing:
    side: DealingRangeSwingSide
    price_tick: int
    provenance: SMCV2EventProvenance
    swing_id: str


@dataclass(frozen=True)
class DealingRangeObservation:
    index: int
    timestamp: datetime
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class DealingRangeStructureEvent:
    direction: SMCV2Direction
    event_type: DealingRangeEventType
    broken_swing_id: str
    provenance: SMCV2EventProvenance
    event_id: str


@dataclass(frozen=True)
class DealingRangeTransition:
    transition_id: str
    lineage_id: str
    from_state: DealingRangeState | None
    to_state: DealingRangeState
    index: int
    timestamp: datetime
    reason: str
    related_event_id: str | None
    replacement_lineage_id: str | None


@dataclass(frozen=True)
class DealingRangeSnapshot:
    kind: DealingRangeKind
    direction: SMCV2Direction
    snapshot_id: str
    source_swing_ids: tuple[str, ...]
    source_indices: tuple[int, ...]
    low_tick: int
    high_tick: int
    midpoint_tick: Decimal
    first_known_provenance: SMCV2EventProvenance
    lineage_id: str | None = None
    protected_swing_id: str | None = None
    construction_event_id: str | None = None
    state: DealingRangeState | None = None
    transitions: tuple[DealingRangeTransition, ...] = ()
    transition_ids: tuple[str, ...] = ()
    replacement_lineage_id: str | None = None


@dataclass(frozen=True)
class DealingRangeResult:
    status: SMCV2PrimitiveStatus
    ranges: tuple[DealingRangeSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass
class _ActiveRange:
    direction: SMCV2Direction
    lineage_id: str
    protected_swing: DealingRangeSwing
    construction_event_id: str
    construction_index: int
    source_swings: tuple[DealingRangeSwing, ...]
    low_tick: int
    high_tick: int
    transitions: tuple[DealingRangeTransition, ...] = field(default_factory=tuple)


class _InvalidAnalysis(ValueError):
    pass


class _UnknownAnalysis(ValueError):
    pass


class _AmbiguousAnalysis(ValueError):
    pass


def make_dealing_range_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...],
    swing_ids: tuple[str, ...] = (),
    event_type: DealingRangeEventType | None = None,
    broken_swing_id: str | None = None,
    confirmation_index: int | None = None,
    boundaries: SMCV2TickRange | None = None,
    lineage_id: str | None = None,
    protected_swing_id: str | None = None,
    construction_event_id: str | None = None,
    range_kind: DealingRangeKind | None = None,
    state: DealingRangeState | None = None,
    transition_ids: tuple[str, ...] = (),
    transition_from_state: DealingRangeState | None = None,
    transition_to_state: DealingRangeState | None = None,
    transition_index: int | None = None,
    transition_timestamp: datetime | None = None,
    transition_reason: str | None = None,
    related_event_id: str | None = None,
    replacement_lineage_id: str | None = None,
) -> str:
    """Build one canonical identity after exact kind-specific validation."""

    if not isinstance(identity_kind, str) or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked Dealing Range identity kind")
    canonical_instrument = _normalize_required_text(instrument, name="instrument").upper()
    canonical_timeframe = _normalize_required_text(timeframe, name="timeframe").upper()
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")
    _validate_source_indices(source_indices)
    _validate_hash_tuple(swing_ids, name="swing_ids")
    _validate_hash_tuple(transition_ids, name="transition_ids")

    payload: dict[str, object] = {
        "detector_version": DEALING_RANGE_DETECTOR_VERSION,
        "direction": direction.value,
        "identity_kind": identity_kind,
        "instrument": canonical_instrument,
        "timeframe": canonical_timeframe,
    }

    if identity_kind == "EVENT":
        _require_empty(swing_ids, name="swing_ids")
        if not isinstance(event_type, DealingRangeEventType):
            raise TypeError("EVENT requires event_type")
        _validate_hash(broken_swing_id, name="broken_swing_id")
        _validate_non_negative_int(confirmation_index, name="confirmation_index")
        lower_tick, upper_tick = _validate_boundaries(
            boundaries,
            allow_zero_width=True,
        )
        if lower_tick != upper_tick:
            raise ValueError("EVENT boundaries must contain one broken-swing tick")
        _reject_non_defaults(
            lineage_id=lineage_id,
            protected_swing_id=protected_swing_id,
            construction_event_id=construction_event_id,
            range_kind=range_kind,
            state=state,
            transition_ids=transition_ids,
            transition_from_state=transition_from_state,
            transition_to_state=transition_to_state,
            transition_index=transition_index,
            transition_timestamp=transition_timestamp,
            transition_reason=transition_reason,
            related_event_id=related_event_id,
            replacement_lineage_id=replacement_lineage_id,
        )
        payload.update({
            "boundary_tick": lower_tick,
            "broken_swing_id": broken_swing_id,
            "confirmation_index": confirmation_index,
            "event_type": event_type.value,
            "source_indices": list(source_indices),
        })
    elif identity_kind == "TRANSITION":
        _require_empty(swing_ids, name="swing_ids")
        if len(source_indices) != 1:
            raise ValueError("TRANSITION requires exactly one source index")
        _validate_hash(lineage_id, name="lineage_id")
        if transition_from_state is not None and not isinstance(
            transition_from_state,
            DealingRangeState,
        ):
            raise TypeError("transition_from_state must be DealingRangeState or None")
        if not isinstance(transition_to_state, DealingRangeState):
            raise TypeError("TRANSITION requires transition_to_state")
        _validate_non_negative_int(transition_index, name="transition_index")
        if transition_index != source_indices[0]:
            raise ValueError("transition_index must equal the transition source index")
        timestamp_text = _serialize_timestamp(transition_timestamp)
        if transition_reason not in _REASON_TOKENS:
            raise ValueError("transition_reason must be an exact locked token")
        _validate_transition_shape(
            from_state=transition_from_state,
            to_state=transition_to_state,
            reason=transition_reason,
            related_event_id=related_event_id,
            replacement_lineage_id=replacement_lineage_id,
        )
        _reject_non_defaults(
            event_type=event_type,
            broken_swing_id=broken_swing_id,
            confirmation_index=confirmation_index,
            boundaries=boundaries,
            protected_swing_id=protected_swing_id,
            construction_event_id=construction_event_id,
            range_kind=range_kind,
            state=state,
            transition_ids=transition_ids,
        )
        payload.update({
            "from_state": (
                None if transition_from_state is None else transition_from_state.value
            ),
            "lineage_id": lineage_id,
            "reason": transition_reason,
            "related_event_id": related_event_id,
            "replacement_lineage_id": replacement_lineage_id,
            "source_indices": list(source_indices),
            "timestamp": timestamp_text,
            "to_state": transition_to_state.value,
            "transition_index": transition_index,
        })
    elif identity_kind == "LINEAGE":
        _require_length(source_indices, 2, name="source_indices")
        _require_length(swing_ids, 2, name="swing_ids")
        _validate_hash(protected_swing_id, name="protected_swing_id")
        _validate_hash(construction_event_id, name="construction_event_id")
        if range_kind is not DealingRangeKind.EXTERNAL:
            raise ValueError("LINEAGE requires range_kind=EXTERNAL")
        _validate_boundaries(boundaries)
        _reject_non_defaults(
            event_type=event_type,
            broken_swing_id=broken_swing_id,
            confirmation_index=confirmation_index,
            lineage_id=lineage_id,
            state=state,
            transition_ids=transition_ids,
            transition_from_state=transition_from_state,
            transition_to_state=transition_to_state,
            transition_index=transition_index,
            transition_timestamp=transition_timestamp,
            transition_reason=transition_reason,
            related_event_id=related_event_id,
            replacement_lineage_id=replacement_lineage_id,
        )
        payload.update({
            "boundaries": _boundary_payload(boundaries),
            "construction_event_id": construction_event_id,
            "protected_swing_id": protected_swing_id,
            "range_kind": range_kind.value,
            "source_indices": list(source_indices),
            "swing_ids": list(swing_ids),
        })
    elif identity_kind == "SNAPSHOT":
        if len(source_indices) < 2 or len(source_indices) != len(swing_ids):
            raise ValueError("SNAPSHOT source and swing tuples must match and contain two")
        _validate_boundaries(boundaries)
        _validate_hash(lineage_id, name="lineage_id")
        _validate_hash(construction_event_id, name="construction_event_id")
        if range_kind is not DealingRangeKind.EXTERNAL:
            raise ValueError("SNAPSHOT requires range_kind=EXTERNAL")
        if not isinstance(state, DealingRangeState):
            raise TypeError("SNAPSHOT requires state")
        if not transition_ids:
            raise ValueError("SNAPSHOT requires ordered transition_ids")
        if state is DealingRangeState.SUPERSEDED:
            _validate_hash(replacement_lineage_id, name="replacement_lineage_id")
        elif replacement_lineage_id is not None:
            raise ValueError("replacement_lineage_id is allowed only for SUPERSEDED")
        _reject_non_defaults(
            event_type=event_type,
            broken_swing_id=broken_swing_id,
            confirmation_index=confirmation_index,
            protected_swing_id=protected_swing_id,
            transition_from_state=transition_from_state,
            transition_to_state=transition_to_state,
            transition_index=transition_index,
            transition_timestamp=transition_timestamp,
            transition_reason=transition_reason,
            related_event_id=related_event_id,
        )
        payload.update({
            "boundaries": _boundary_payload(boundaries),
            "construction_event_id": construction_event_id,
            "lineage_id": lineage_id,
            "range_kind": range_kind.value,
            "replacement_lineage_id": replacement_lineage_id,
            "source_indices": list(source_indices),
            "state": state.value,
            "swing_ids": list(swing_ids),
            "transition_ids": list(transition_ids),
        })
    else:
        _require_length(source_indices, 2, name="source_indices")
        _require_length(swing_ids, 2, name="swing_ids")
        _validate_boundaries(boundaries)
        if range_kind is not DealingRangeKind.INTERNAL:
            raise ValueError("INTERNAL_RANGE requires range_kind=INTERNAL")
        _reject_non_defaults(
            event_type=event_type,
            broken_swing_id=broken_swing_id,
            confirmation_index=confirmation_index,
            lineage_id=lineage_id,
            protected_swing_id=protected_swing_id,
            construction_event_id=construction_event_id,
            state=state,
            transition_ids=transition_ids,
            transition_from_state=transition_from_state,
            transition_to_state=transition_to_state,
            transition_index=transition_index,
            transition_timestamp=transition_timestamp,
            transition_reason=transition_reason,
            related_event_id=related_event_id,
            replacement_lineage_id=replacement_lineage_id,
        )
        payload.update({
            "boundaries": _boundary_payload(boundaries),
            "range_kind": range_kind.value,
            "source_indices": list(source_indices),
            "swing_ids": list(swing_ids),
        })

    canonical_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def analyze_dealing_ranges(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...] | None,
    observations: tuple[DealingRangeObservation, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    config: DealingRangeConfig = DealingRangeConfig(),
) -> DealingRangeResult:
    """Analyze immutable Dealing Range evidence without runtime integration."""

    if swings is None or observations is None or structure_events is None:
        missing = []
        if swings is None:
            missing.append("swings")
        if observations is None:
            missing.append("observations")
        if structure_events is None:
            missing.append("structure_events")
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return DealingRangeResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    try:
        canonical_instrument = _normalize_required_text(instrument, name="instrument").upper()
        canonical_timeframe = _normalize_required_text(timeframe, name="timeframe").upper()
        _validate_config(config)
        observations_by_index = _validate_observations(observations)
        swings_by_id = _validate_swings(
            swings,
            observations_by_index=observations_by_index,
            config=config,
        )
        events_by_index = _validate_events(structure_events)
        status, snapshots, reason = _analyze_valid_inputs(
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
            swings=swings,
            swings_by_id=swings_by_id,
            observations=observations,
            observations_by_index=observations_by_index,
            events_by_index=events_by_index,
            config=config,
        )
    except _AmbiguousAnalysis as exc:
        reason = str(exc)
        return DealingRangeResult(
            status=SMCV2PrimitiveStatus.AMBIGUOUS,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )
    except _UnknownAnalysis as exc:
        reason = str(exc)
        return DealingRangeResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )
    except (TypeError, ValueError, _InvalidAnalysis) as exc:
        reason = str(exc) or exc.__class__.__name__
        return DealingRangeResult(
            status=SMCV2PrimitiveStatus.INVALID,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    if status is not None:
        return DealingRangeResult(
            status=status,
            ranges=tuple(snapshots),
            reasons=(reason,),
            blocking_reasons=(reason,),
        )
    if not snapshots:
        return DealingRangeResult(
            status=SMCV2PrimitiveStatus.NONE,
            reasons=("No qualifying confirmed Dealing Range",),
        )
    return DealingRangeResult(
        status=SMCV2PrimitiveStatus.VALID,
        ranges=tuple(snapshots),
        reasons=("Deterministic Dealing Range analysis completed",),
    )


def _analyze_valid_inputs(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...],
    swings_by_id: dict[str, DealingRangeSwing],
    observations: tuple[DealingRangeObservation, ...],
    observations_by_index: dict[int, DealingRangeObservation],
    events_by_index: dict[int, tuple[DealingRangeStructureEvent, ...]],
    config: DealingRangeConfig,
) -> tuple[SMCV2PrimitiveStatus | None, list[DealingRangeSnapshot], str]:
    snapshots: list[DealingRangeSnapshot] = []
    active: _ActiveRange | None = None
    terminal_context: _ActiveRange | None = None
    previous_event_key: tuple[object, ...] | None = None
    seen_event_ids: set[str] = set()
    swings_by_confirmation: dict[int, tuple[DealingRangeSwing, ...]] = {}
    for swing in swings:
        existing = swings_by_confirmation.get(swing.provenance.confirmation_index, ())
        swings_by_confirmation[swing.provenance.confirmation_index] = existing + (swing,)
    indices = sorted(
        set(observation.index for observation in observations)
        | set(swings_by_confirmation)
        | set(events_by_index),
    )

    try:
        for index in indices:
            event_group = events_by_index.get(index, ())
            if event_group:
                for candidate in event_group:
                    _validate_event(
                        candidate,
                        swings_by_id=swings_by_id,
                        observations_by_index=observations_by_index,
                        instrument=instrument,
                        timeframe=timeframe,
                        config=config,
                    )
                    key = _event_composite_key(candidate)
                    if previous_event_key is not None and key <= previous_event_key:
                        raise ValueError("structure-event tuple must be strictly composite ordered")
                    if candidate.event_id in seen_event_ids:
                        raise ValueError("duplicate event_id")
                    seen_event_ids.add(candidate.event_id)
                    previous_event_key = key
                    _validate_event_state_relationship(
                        candidate,
                        active=active,
                        terminal_context=terminal_context,
                    )
                _validate_event_group(event_group)
            event = event_group[0] if len(event_group) == 1 else None
            observation = observations_by_index.get(index)

            if active is not None and observation is not None:
                if _observation_invalidates(active, observation):
                    if event is not None and event.direction is not active.direction:
                        active = _process_reverse_event(
                            active,
                            event,
                            observation=observation,
                            swings=swings,
                            observations_by_index=observations_by_index,
                            snapshots=snapshots,
                            instrument=instrument,
                            timeframe=timeframe,
                        )
                        terminal_context = None
                        _emit_internal_ranges(
                            index,
                            active=active,
                            swings=swings,
                            snapshots=snapshots,
                            instrument=instrument,
                            timeframe=timeframe,
                        )
                        continue
                    terminal_context = active
                    active = _invalidate_from_observation(
                        active,
                        observation,
                        snapshots=snapshots,
                        instrument=instrument,
                        timeframe=timeframe,
                    )
                    continue

            if event is not None:
                if active is None:
                    active = _construct_active_range(
                        event,
                        swings=swings,
                        observations_by_index=observations_by_index,
                        snapshots=snapshots,
                        instrument=instrument,
                        timeframe=timeframe,
                    )
                    terminal_context = None
                elif event.direction is active.direction:
                    active = _process_same_direction_event(
                        active,
                        event,
                        swings=swings,
                        observations_by_index=observations_by_index,
                        snapshots=snapshots,
                        instrument=instrument,
                        timeframe=timeframe,
                    )
                else:
                    raise _InvalidAnalysis(
                        "reverse CHOCH did not invalidate the protected boundary",
                    )

            _emit_internal_ranges(
                index,
                active=active,
                swings=swings,
                snapshots=snapshots,
                instrument=instrument,
                timeframe=timeframe,
            )
    except _AmbiguousAnalysis as exc:
        return SMCV2PrimitiveStatus.AMBIGUOUS, snapshots, str(exc)
    except _UnknownAnalysis as exc:
        return SMCV2PrimitiveStatus.UNKNOWN, snapshots, str(exc)
    except (TypeError, ValueError, _InvalidAnalysis) as exc:
        return SMCV2PrimitiveStatus.INVALID, snapshots, str(exc)

    return None, snapshots, ""


def _construct_active_range(
    event: DealingRangeStructureEvent,
    *,
    swings: tuple[DealingRangeSwing, ...],
    observations_by_index: dict[int, DealingRangeObservation],
    snapshots: list[DealingRangeSnapshot],
    instrument: str,
    timeframe: str,
) -> _ActiveRange:
    displacement_start = event.provenance.source_indices[0]
    start_observation = _required_observation(observations_by_index, displacement_start)
    protected = _select_protected_swing(
        swings,
        direction=event.direction,
        displacement_start=displacement_start,
        displacement_timestamp=start_observation.timestamp,
    )
    broken = _find_swing(swings, event.broken_swing_id)
    low_tick, high_tick = _external_boundaries(
        event.direction,
        protected,
        confirmation_index=event.provenance.confirmation_index,
        observations_by_index=observations_by_index,
    )
    ordered_swings = _chronological_swings((protected, broken))
    source_indices = tuple(_source_index(swing) for swing in ordered_swings)
    swing_ids = tuple(swing.swing_id for swing in ordered_swings)
    boundaries = SMCV2TickRange(low_tick, high_tick)
    lineage_id = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=instrument,
        timeframe=timeframe,
        direction=event.direction,
        source_indices=source_indices,
        swing_ids=swing_ids,
        boundaries=boundaries,
        protected_swing_id=protected.swing_id,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    transition = _transition(
        lineage_id=lineage_id,
        direction=event.direction,
        from_state=None,
        to_state=DealingRangeState.ACTIVE,
        index=event.provenance.confirmation_index,
        timestamp=event.provenance.confirmation_timestamp,
        reason=_REASON_CONSTRUCTION,
        related_event_id=event.event_id,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    )
    active = _ActiveRange(
        direction=event.direction,
        lineage_id=lineage_id,
        protected_swing=protected,
        construction_event_id=event.event_id,
        construction_index=event.provenance.confirmation_index,
        source_swings=ordered_swings,
        low_tick=low_tick,
        high_tick=high_tick,
        transitions=(transition,),
    )
    snapshots.append(_external_snapshot(
        active,
        state=DealingRangeState.ACTIVE,
        provenance=event.provenance,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    ))
    return active


def _process_same_direction_event(
    active: _ActiveRange,
    event: DealingRangeStructureEvent,
    *,
    swings: tuple[DealingRangeSwing, ...],
    observations_by_index: dict[int, DealingRangeObservation],
    snapshots: list[DealingRangeSnapshot],
    instrument: str,
    timeframe: str,
) -> _ActiveRange:
    pullback = _select_replacement_pullback(active, event, swings=swings)
    if pullback is not None:
        new_active = _build_replacement_active(
            event,
            pullback=pullback,
            swings=swings,
            observations_by_index=observations_by_index,
            instrument=instrument,
            timeframe=timeframe,
        )
        terminal = _transition(
            lineage_id=active.lineage_id,
            direction=active.direction,
            from_state=DealingRangeState.ACTIVE,
            to_state=DealingRangeState.SUPERSEDED,
            index=event.provenance.confirmation_index,
            timestamp=event.provenance.confirmation_timestamp,
            reason=_REASON_REPLACEMENT,
            related_event_id=event.event_id,
            replacement_lineage_id=new_active.lineage_id,
            instrument=instrument,
            timeframe=timeframe,
        )
        active.transitions += (terminal,)
        snapshots.append(_external_snapshot(
            active,
            state=DealingRangeState.SUPERSEDED,
            provenance=event.provenance,
            replacement_lineage_id=new_active.lineage_id,
            instrument=instrument,
            timeframe=timeframe,
        ))
        snapshots.append(_external_snapshot(
            new_active,
            state=DealingRangeState.ACTIVE,
            provenance=event.provenance,
            replacement_lineage_id=None,
            instrument=instrument,
            timeframe=timeframe,
        ))
        return new_active

    rows = _closed_interval(
        observations_by_index,
        _source_index(active.protected_swing),
        event.provenance.confirmation_index,
    )
    changed = False
    if active.direction is SMCV2Direction.BULLISH:
        target = max(row.high_tick for row in rows)
        if target > active.high_tick:
            active.high_tick = target
            changed = True
    else:
        target = min(row.low_tick for row in rows)
        if target < active.low_tick:
            active.low_tick = target
            changed = True
    if not changed:
        return active
    snapshots.append(_external_snapshot(
        active,
        state=DealingRangeState.ACTIVE,
        provenance=event.provenance,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    ))
    return active


def _build_replacement_active(
    event: DealingRangeStructureEvent,
    *,
    pullback: DealingRangeSwing,
    swings: tuple[DealingRangeSwing, ...],
    observations_by_index: dict[int, DealingRangeObservation],
    instrument: str,
    timeframe: str,
) -> _ActiveRange:
    broken = _find_swing(swings, event.broken_swing_id)
    low_tick, high_tick = _external_boundaries(
        event.direction,
        pullback,
        confirmation_index=event.provenance.confirmation_index,
        observations_by_index=observations_by_index,
    )
    ordered_swings = _chronological_swings((pullback, broken))
    source_indices = tuple(_source_index(swing) for swing in ordered_swings)
    swing_ids = tuple(swing.swing_id for swing in ordered_swings)
    lineage_id = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=instrument,
        timeframe=timeframe,
        direction=event.direction,
        source_indices=source_indices,
        swing_ids=swing_ids,
        boundaries=SMCV2TickRange(low_tick, high_tick),
        protected_swing_id=pullback.swing_id,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    activation = _transition(
        lineage_id=lineage_id,
        direction=event.direction,
        from_state=None,
        to_state=DealingRangeState.ACTIVE,
        index=event.provenance.confirmation_index,
        timestamp=event.provenance.confirmation_timestamp,
        reason=_REASON_CONSTRUCTION,
        related_event_id=event.event_id,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    )
    return _ActiveRange(
        direction=event.direction,
        lineage_id=lineage_id,
        protected_swing=pullback,
        construction_event_id=event.event_id,
        construction_index=event.provenance.confirmation_index,
        source_swings=ordered_swings,
        low_tick=low_tick,
        high_tick=high_tick,
        transitions=(activation,),
    )


def _process_reverse_event(
    active: _ActiveRange,
    event: DealingRangeStructureEvent,
    *,
    observation: DealingRangeObservation,
    swings: tuple[DealingRangeSwing, ...],
    observations_by_index: dict[int, DealingRangeObservation],
    snapshots: list[DealingRangeSnapshot],
    instrument: str,
    timeframe: str,
) -> _ActiveRange | None:
    terminal = _transition(
        lineage_id=active.lineage_id,
        direction=active.direction,
        from_state=DealingRangeState.ACTIVE,
        to_state=DealingRangeState.INVALIDATED,
        index=observation.index,
        timestamp=observation.timestamp,
        reason=_REASON_CHOCH,
        related_event_id=event.event_id,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    )
    active.transitions += (terminal,)
    snapshots.append(_external_snapshot(
        active,
        state=DealingRangeState.INVALIDATED,
        provenance=event.provenance,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    ))
    return _construct_active_range(
        event,
        swings=swings,
        observations_by_index=observations_by_index,
        snapshots=snapshots,
        instrument=instrument,
        timeframe=timeframe,
    )


def _invalidate_from_observation(
    active: _ActiveRange,
    observation: DealingRangeObservation,
    *,
    snapshots: list[DealingRangeSnapshot],
    instrument: str,
    timeframe: str,
) -> None:
    transition = _transition(
        lineage_id=active.lineage_id,
        direction=active.direction,
        from_state=DealingRangeState.ACTIVE,
        to_state=DealingRangeState.INVALIDATED,
        index=observation.index,
        timestamp=observation.timestamp,
        reason=_REASON_OBSERVATION,
        related_event_id=None,
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    )
    active.transitions += (transition,)
    snapshots.append(_external_snapshot(
        active,
        state=DealingRangeState.INVALIDATED,
        provenance=_observation_provenance(observation),
        replacement_lineage_id=None,
        instrument=instrument,
        timeframe=timeframe,
    ))
    return None


def _external_snapshot(
    active: _ActiveRange,
    *,
    state: DealingRangeState,
    provenance: SMCV2EventProvenance,
    replacement_lineage_id: str | None,
    instrument: str,
    timeframe: str,
) -> DealingRangeSnapshot:
    _validate_transition_history(
        active,
        expected_state=state,
        instrument=instrument,
        timeframe=timeframe,
    )
    source_swings = _chronological_swings(active.source_swings)
    source_indices = tuple(_source_index(swing) for swing in source_swings)
    swing_ids = tuple(swing.swing_id for swing in source_swings)
    transition_ids = tuple(item.transition_id for item in active.transitions)
    boundaries = SMCV2TickRange(active.low_tick, active.high_tick)
    snapshot_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        direction=active.direction,
        source_indices=source_indices,
        swing_ids=swing_ids,
        boundaries=boundaries,
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        range_kind=DealingRangeKind.EXTERNAL,
        state=state,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )
    return DealingRangeSnapshot(
        kind=DealingRangeKind.EXTERNAL,
        direction=active.direction,
        snapshot_id=snapshot_id,
        source_swing_ids=swing_ids,
        source_indices=source_indices,
        low_tick=active.low_tick,
        high_tick=active.high_tick,
        midpoint_tick=_midpoint(active.low_tick, active.high_tick),
        first_known_provenance=provenance,
        lineage_id=active.lineage_id,
        protected_swing_id=active.protected_swing.swing_id,
        construction_event_id=active.construction_event_id,
        state=state,
        transitions=active.transitions,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )


def _emit_internal_ranges(
    index: int,
    *,
    active: _ActiveRange | None,
    swings: tuple[DealingRangeSwing, ...],
    snapshots: list[DealingRangeSnapshot],
    instrument: str,
    timeframe: str,
) -> None:
    if active is None:
        return
    for position in range(1, len(swings)):
        first = swings[position - 1]
        second = swings[position]
        if second.provenance.confirmation_index != index:
            continue
        if first.side is second.side:
            continue
        low_tick = min(first.price_tick, second.price_tick)
        high_tick = max(first.price_tick, second.price_tick)
        if not active.low_tick < low_tick < high_tick < active.high_tick:
            continue
        direction = (
            SMCV2Direction.BULLISH
            if first.side is DealingRangeSwingSide.LOW
            else SMCV2Direction.BEARISH
        )
        ordered = _chronological_swings((first, second))
        source_indices = tuple(_source_index(swing) for swing in ordered)
        swing_ids = tuple(swing.swing_id for swing in ordered)
        boundaries = SMCV2TickRange(low_tick, high_tick)
        snapshot_id = make_dealing_range_id(
            identity_kind="INTERNAL_RANGE",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_indices=source_indices,
            swing_ids=swing_ids,
            boundaries=boundaries,
            range_kind=DealingRangeKind.INTERNAL,
        )
        if any(item.snapshot_id == snapshot_id for item in snapshots):
            continue
        snapshots.append(DealingRangeSnapshot(
            kind=DealingRangeKind.INTERNAL,
            direction=direction,
            snapshot_id=snapshot_id,
            source_swing_ids=swing_ids,
            source_indices=source_indices,
            low_tick=low_tick,
            high_tick=high_tick,
            midpoint_tick=_midpoint(low_tick, high_tick),
            first_known_provenance=second.provenance,
        ))


def _transition(
    *,
    lineage_id: str,
    direction: SMCV2Direction,
    from_state: DealingRangeState | None,
    to_state: DealingRangeState,
    index: int,
    timestamp: datetime,
    reason: str,
    related_event_id: str | None,
    replacement_lineage_id: str | None,
    instrument: str,
    timeframe: str,
) -> DealingRangeTransition:
    transition_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_indices=(index,),
        lineage_id=lineage_id,
        transition_from_state=from_state,
        transition_to_state=to_state,
        transition_index=index,
        transition_timestamp=timestamp,
        transition_reason=reason,
        related_event_id=related_event_id,
        replacement_lineage_id=replacement_lineage_id,
    )
    return DealingRangeTransition(
        transition_id=transition_id,
        lineage_id=lineage_id,
        from_state=from_state,
        to_state=to_state,
        index=index,
        timestamp=normalize_utc_timestamp(timestamp),
        reason=reason,
        related_event_id=related_event_id,
        replacement_lineage_id=replacement_lineage_id,
    )


def _validate_config(config: DealingRangeConfig) -> None:
    if not isinstance(config, DealingRangeConfig):
        raise TypeError("config must be DealingRangeConfig")
    swing_confirmation_bars = _required_attribute(
        config,
        "swing_confirmation_bars",
        owner="DealingRangeConfig",
    )
    break_buffer_ticks = _required_attribute(
        config,
        "break_buffer_ticks",
        owner="DealingRangeConfig",
    )
    values = (swing_confirmation_bars, break_buffer_ticks)
    if any(type(value) is not int for value in values) or values != (2, 1):
        raise ValueError("config does not match the locked 2/1 detector version")


def _validate_observations(
    observations: tuple[DealingRangeObservation, ...],
) -> dict[int, DealingRangeObservation]:
    if not isinstance(observations, tuple):
        raise TypeError("observations must be an immutable tuple")
    result: dict[int, DealingRangeObservation] = {}
    previous_index = -1
    previous_timestamp: datetime | None = None
    for observation in observations:
        if not isinstance(observation, DealingRangeObservation):
            raise TypeError("observations must contain DealingRangeObservation values")
        index = _required_attribute(observation, "index", owner="DealingRangeObservation")
        timestamp = _required_attribute(
            observation,
            "timestamp",
            owner="DealingRangeObservation",
        )
        high_tick = _required_attribute(
            observation,
            "high_tick",
            owner="DealingRangeObservation",
        )
        low_tick = _required_attribute(observation, "low_tick", owner="DealingRangeObservation")
        close_tick = _required_attribute(
            observation,
            "close_tick",
            owner="DealingRangeObservation",
        )
        _validate_non_negative_int(index, name="observation index")
        if any(type(value) is not int for value in (high_tick, low_tick, close_tick)):
            raise TypeError("observation ticks must be integers")
        if not low_tick <= close_tick <= high_tick:
            raise ValueError("observation must satisfy low <= close <= high")
        normalized = normalize_utc_timestamp(timestamp)
        if index <= previous_index:
            raise ValueError("observation indices must be strictly increasing")
        if previous_timestamp is not None and normalized <= previous_timestamp:
            raise ValueError("observation timestamps must be strictly increasing")
        result[index] = observation
        previous_index = index
        previous_timestamp = normalized
    return result


def _validate_swings(
    swings: tuple[DealingRangeSwing, ...],
    *,
    observations_by_index: dict[int, DealingRangeObservation],
    config: DealingRangeConfig,
) -> dict[str, DealingRangeSwing]:
    if not isinstance(swings, tuple):
        raise TypeError("swings must be an immutable tuple")
    previous_key: tuple[object, ...] | None = None
    seen_ids: set[str] = set()
    seen_source_side: set[tuple[int, DealingRangeSwingSide]] = set()
    result: dict[str, DealingRangeSwing] = {}
    for swing in swings:
        if not isinstance(swing, DealingRangeSwing):
            raise TypeError("swings must contain DealingRangeSwing values")
        side = _required_attribute(swing, "side", owner="DealingRangeSwing")
        price_tick = _required_attribute(swing, "price_tick", owner="DealingRangeSwing")
        provenance = _required_attribute(swing, "provenance", owner="DealingRangeSwing")
        swing_id = _required_attribute(swing, "swing_id", owner="DealingRangeSwing")
        if not isinstance(side, DealingRangeSwingSide):
            raise TypeError("swing side must be DealingRangeSwingSide")
        if type(price_tick) is not int:
            raise TypeError("swing price_tick must be an integer")
        _validate_provenance(provenance, name="swing provenance", single_source=True)
        _validate_hash(swing_id, name="swing_id")
        source_index = provenance.source_indices[0]
        if provenance.confirmation_index < source_index + config.swing_confirmation_bars:
            raise ValueError("swing confirmation cannot precede source plus two")
        source_observation = _required_observation(observations_by_index, source_index)
        confirmation_observation = _required_observation(
            observations_by_index,
            provenance.confirmation_index,
        )
        if normalize_utc_timestamp(source_observation.timestamp) != provenance.source_timestamps[0]:
            raise ValueError("swing source timestamp conflicts with source observation")
        if (
            normalize_utc_timestamp(confirmation_observation.timestamp)
            != provenance.confirmation_timestamp
        ):
            raise ValueError("swing confirmation timestamp conflicts with observation")
        expected_price = (
            source_observation.high_tick
            if side is DealingRangeSwingSide.HIGH
            else source_observation.low_tick
        )
        if price_tick != expected_price:
            raise ValueError("swing price conflicts with source observation")
        key = (
            provenance.confirmation_index,
            source_index,
            side.value,
            swing_id,
        )
        if previous_key is not None and key <= previous_key:
            raise ValueError("swing tuple must be strictly ordered")
        source_side = (source_index, side)
        if source_side in seen_source_side:
            raise ValueError("duplicate source-side swing identity")
        if swing_id in seen_ids:
            raise ValueError("duplicate swing_id")
        seen_source_side.add(source_side)
        seen_ids.add(swing_id)
        result[swing_id] = swing
        previous_key = key
    return result


def _validate_events(
    events: tuple[DealingRangeStructureEvent, ...],
) -> dict[int, tuple[DealingRangeStructureEvent, ...]]:
    if not isinstance(events, tuple):
        raise TypeError("structure_events must be an immutable tuple")
    grouped: dict[int, tuple[DealingRangeStructureEvent, ...]] = {}
    previous_confirmation_index: int | None = None
    for event in events:
        if not isinstance(event, DealingRangeStructureEvent):
            raise TypeError("structure_events must contain DealingRangeStructureEvent values")
        provenance = _required_attribute(
            event,
            "provenance",
            owner="DealingRangeStructureEvent",
        )
        if not isinstance(provenance, SMCV2EventProvenance):
            raise TypeError("event provenance must be SMCV2EventProvenance")
        confirmation_index = _required_attribute(
            provenance,
            "confirmation_index",
            owner="event provenance",
        )
        _validate_non_negative_int(
            confirmation_index,
            name="event provenance confirmation_index",
        )
        if (
            previous_confirmation_index is not None
            and confirmation_index < previous_confirmation_index
        ):
            raise ValueError("structure-event confirmation indices must be nondecreasing")
        existing = grouped.get(confirmation_index, ())
        grouped[confirmation_index] = existing + (event,)
        previous_confirmation_index = confirmation_index
    return grouped


def _event_composite_key(event: DealingRangeStructureEvent) -> tuple[object, ...]:
    direction = _required_attribute(event, "direction", owner="DealingRangeStructureEvent")
    event_type = _required_attribute(event, "event_type", owner="DealingRangeStructureEvent")
    provenance = _required_attribute(event, "provenance", owner="DealingRangeStructureEvent")
    event_id = _required_attribute(event, "event_id", owner="DealingRangeStructureEvent")
    if (
        not isinstance(direction, SMCV2Direction)
        or direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH)
    ):
        raise TypeError("event direction must be BULLISH or BEARISH")
    if not isinstance(event_type, DealingRangeEventType):
        raise TypeError("event_type must be DealingRangeEventType")
    _validate_hash(event_id, name="event_id")
    _validate_provenance(provenance, name="event provenance", single_source=False)
    return (
        provenance.confirmation_index,
        provenance.confirmation_timestamp,
        direction.value,
        event_type.value,
        event_id,
    )


def _validate_event(
    event: DealingRangeStructureEvent,
    *,
    swings_by_id: dict[str, DealingRangeSwing],
    observations_by_index: dict[int, DealingRangeObservation],
    instrument: str,
    timeframe: str,
    config: DealingRangeConfig,
) -> None:
    direction = _required_attribute(event, "direction", owner="DealingRangeStructureEvent")
    event_type = _required_attribute(
        event,
        "event_type",
        owner="DealingRangeStructureEvent",
    )
    broken_swing_id = _required_attribute(
        event,
        "broken_swing_id",
        owner="DealingRangeStructureEvent",
    )
    provenance = _required_attribute(
        event,
        "provenance",
        owner="DealingRangeStructureEvent",
    )
    event_id = _required_attribute(event, "event_id", owner="DealingRangeStructureEvent")
    if (
        not isinstance(direction, SMCV2Direction)
        or direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH)
    ):
        raise TypeError("event direction must be BULLISH or BEARISH")
    if not isinstance(event_type, DealingRangeEventType):
        raise TypeError("event_type must be DealingRangeEventType")
    _validate_hash(broken_swing_id, name="broken_swing_id")
    _validate_hash(event_id, name="event_id")
    _validate_provenance(provenance, name="event provenance", single_source=False)
    if any(
        right != left + 1
        for left, right in zip(provenance.source_indices, provenance.source_indices[1:])
    ):
        raise ValueError("event displacement source indices must be contiguous")
    if provenance.source_indices[-1] != provenance.confirmation_index:
        raise ValueError("event source sequence must end at confirmation index")
    for source_index, source_timestamp in zip(
        provenance.source_indices,
        provenance.source_timestamps,
    ):
        observation = _required_observation(observations_by_index, source_index)
        if normalize_utc_timestamp(observation.timestamp) != source_timestamp:
            raise ValueError("event source timestamp conflicts with observation")
    confirmation = _required_observation(
        observations_by_index,
        provenance.confirmation_index,
    )
    if normalize_utc_timestamp(confirmation.timestamp) != provenance.confirmation_timestamp:
        raise ValueError("event confirmation timestamp conflicts with observation")
    broken = swings_by_id.get(broken_swing_id)
    if broken is None:
        raise ValueError("broken_swing_id is a dangling reference")
    required_side = (
        DealingRangeSwingSide.HIGH
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.LOW
    )
    if broken.side is not required_side:
        raise ValueError("event references the wrong broken swing side")
    displacement_start = provenance.source_indices[0]
    start_observation = _required_observation(observations_by_index, displacement_start)
    if broken.provenance.confirmation_index >= displacement_start:
        raise ValueError("broken swing must confirm before displacement start")
    if broken.provenance.confirmation_timestamp >= normalize_utc_timestamp(
        start_observation.timestamp,
    ):
        raise ValueError("broken swing timestamp must precede displacement start")
    if direction is SMCV2Direction.BULLISH:
        accepted = confirmation.close_tick >= broken.price_tick + config.break_buffer_ticks
    else:
        accepted = confirmation.close_tick <= broken.price_tick - config.break_buffer_ticks
    if not accepted:
        raise ValueError("supplied structure event lacks the exact close break")
    expected_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_indices=provenance.source_indices,
        event_type=event_type,
        broken_swing_id=broken_swing_id,
        confirmation_index=provenance.confirmation_index,
        boundaries=SMCV2TickRange(broken.price_tick, broken.price_tick),
    )
    if event_id != expected_id:
        raise ValueError("event_id does not match canonical EVENT identity")


def _validate_event_group(events: tuple[DealingRangeStructureEvent, ...]) -> None:
    if len(events) <= 1:
        return
    directions = [event.direction for event in events]
    if len(directions) != len(set(directions)):
        raise _InvalidAnalysis("same-index event group contains duplicate direction")
    if set(directions) == {SMCV2Direction.BULLISH, SMCV2Direction.BEARISH}:
        raise _AmbiguousAnalysis("same-index event group contains opposing valid events")
    raise _InvalidAnalysis("same-index event group exceeds locked cardinality")


def _validate_event_state_relationship(
    event: DealingRangeStructureEvent,
    *,
    active: _ActiveRange | None,
    terminal_context: _ActiveRange | None,
) -> None:
    if active is None:
        if event.event_type is DealingRangeEventType.CHOCH:
            if terminal_context is None:
                raise _UnknownAnalysis("initial CHOCH lacks prior external range context")
            terminal = terminal_context.transitions[-1]
            if terminal.to_state is not DealingRangeState.INVALIDATED:
                raise _InvalidAnalysis("retained terminal context must be INVALIDATED")
            if event.direction is terminal_context.direction:
                raise _InvalidAnalysis("same-direction event must be BOS")
            if (
                event.provenance.confirmation_index <= terminal.index
                or normalize_utc_timestamp(event.provenance.confirmation_timestamp)
                <= normalize_utc_timestamp(terminal.timestamp)
            ):
                raise _InvalidAnalysis(
                    "terminal context must strictly precede reverse CHOCH",
                )
        return
    if event.direction is active.direction:
        if event.event_type is not DealingRangeEventType.BOS:
            raise _InvalidAnalysis("same-direction event must be BOS")
        return
    if event.event_type is not DealingRangeEventType.CHOCH:
        raise _InvalidAnalysis("opposite-direction event must be CHOCH")
    if event.broken_swing_id != active.protected_swing.swing_id:
        raise _InvalidAnalysis("reverse CHOCH must reference the protected swing")


def _select_protected_swing(
    swings: tuple[DealingRangeSwing, ...],
    *,
    direction: SMCV2Direction,
    displacement_start: int,
    displacement_timestamp: datetime,
) -> DealingRangeSwing:
    required_side = (
        DealingRangeSwingSide.LOW
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.HIGH
    )
    normalized_start = normalize_utc_timestamp(displacement_timestamp)
    eligible = [
        swing
        for swing in swings
        if swing.side is required_side
        and _source_index(swing) < displacement_start
        and swing.provenance.confirmation_index < displacement_start
        and swing.provenance.confirmation_timestamp < normalized_start
    ]
    if not eligible:
        raise _UnknownAnalysis("eligible protected opposite swing is missing")
    greatest_source = max(_source_index(swing) for swing in eligible)
    latest = [swing for swing in eligible if _source_index(swing) == greatest_source]
    greatest_confirmation = max(swing.provenance.confirmation_index for swing in latest)
    latest = [
        swing
        for swing in latest
        if swing.provenance.confirmation_index == greatest_confirmation
    ]
    if len(latest) > 1:
        if len({swing.price_tick for swing in latest}) > 1:
            raise _InvalidAnalysis("contradictory protected swing identity")
        raise _InvalidAnalysis("duplicate protected swing source identity")
    return min(latest, key=lambda swing: swing.swing_id)


def _select_replacement_pullback(
    active: _ActiveRange,
    event: DealingRangeStructureEvent,
    *,
    swings: tuple[DealingRangeSwing, ...],
) -> DealingRangeSwing | None:
    displacement_start = event.provenance.source_indices[0]
    required_side = (
        DealingRangeSwingSide.LOW
        if active.direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.HIGH
    )
    eligible = tuple(
        swing
        for swing in swings
        if swing.side is required_side
        and _source_index(swing) > active.construction_index
        and swing.provenance.confirmation_index > active.construction_index
        and swing.provenance.confirmation_index < displacement_start
        and active.low_tick < swing.price_tick < active.high_tick
    )
    if not eligible:
        return None
    greatest_source = max(_source_index(swing) for swing in eligible)
    latest = [swing for swing in eligible if _source_index(swing) == greatest_source]
    greatest_confirmation = max(swing.provenance.confirmation_index for swing in latest)
    latest = [
        swing
        for swing in latest
        if swing.provenance.confirmation_index == greatest_confirmation
    ]
    return min(latest, key=lambda swing: swing.swing_id)


def _external_boundaries(
    direction: SMCV2Direction,
    protected: DealingRangeSwing,
    *,
    confirmation_index: int,
    observations_by_index: dict[int, DealingRangeObservation],
) -> tuple[int, int]:
    rows = _closed_interval(
        observations_by_index,
        _source_index(protected),
        confirmation_index,
    )
    if direction is SMCV2Direction.BULLISH:
        low_tick = protected.price_tick
        high_tick = max(row.high_tick for row in rows)
    else:
        low_tick = min(row.low_tick for row in rows)
        high_tick = protected.price_tick
    if low_tick >= high_tick:
        raise _InvalidAnalysis("external Dealing Range must have positive width")
    return low_tick, high_tick


def _observation_invalidates(
    active: _ActiveRange,
    observation: DealingRangeObservation,
) -> bool:
    if active.direction is SMCV2Direction.BULLISH:
        return observation.close_tick <= active.low_tick - 1
    return observation.close_tick >= active.high_tick + 1


def _validate_provenance(
    provenance: object,
    *,
    name: str,
    single_source: bool,
) -> None:
    if not isinstance(provenance, SMCV2EventProvenance):
        raise TypeError(f"{name} must be SMCV2EventProvenance")
    source_indices = _required_attribute(provenance, "source_indices", owner=name)
    source_timestamps = _required_attribute(provenance, "source_timestamps", owner=name)
    confirmation_index = _required_attribute(provenance, "confirmation_index", owner=name)
    confirmation_timestamp = _required_attribute(
        provenance,
        "confirmation_timestamp",
        owner=name,
    )
    _validate_source_indices(source_indices)
    if single_source and len(source_indices) != 1:
        raise ValueError(f"{name} must contain exactly one source")
    if not isinstance(source_timestamps, tuple):
        raise TypeError(f"{name} source_timestamps must be a tuple")
    if len(source_timestamps) != len(source_indices):
        raise ValueError(f"{name} source timestamps must match source indices")
    normalized = tuple(normalize_utc_timestamp(value) for value in source_timestamps)
    if any(left >= right for left, right in zip(normalized, normalized[1:])):
        raise ValueError(f"{name} source timestamps must be strictly increasing")
    _validate_non_negative_int(confirmation_index, name=f"{name} confirmation_index")
    normalized_confirmation = normalize_utc_timestamp(confirmation_timestamp)
    if confirmation_index < source_indices[-1]:
        raise ValueError(f"{name} confirmation cannot precede its latest source")
    if normalized_confirmation < normalized[-1]:
        raise ValueError(f"{name} confirmation timestamp cannot precede latest source")


def _validate_transition_shape(
    *,
    from_state: DealingRangeState | None,
    to_state: DealingRangeState,
    reason: str,
    related_event_id: str | None,
    replacement_lineage_id: str | None,
) -> None:
    if reason == _REASON_CONSTRUCTION:
        expected = from_state is None and to_state is DealingRangeState.ACTIVE
        _validate_hash(related_event_id, name="related_event_id")
        if replacement_lineage_id is not None:
            raise ValueError("construction transition forbids replacement lineage")
    elif reason == _REASON_OBSERVATION:
        expected = (
            from_state is DealingRangeState.ACTIVE
            and to_state is DealingRangeState.INVALIDATED
        )
        if related_event_id is not None or replacement_lineage_id is not None:
            raise ValueError("observation invalidation forbids related identities")
    elif reason == _REASON_CHOCH:
        expected = (
            from_state is DealingRangeState.ACTIVE
            and to_state is DealingRangeState.INVALIDATED
        )
        _validate_hash(related_event_id, name="related_event_id")
        if replacement_lineage_id is not None:
            raise ValueError("CHOCH invalidation forbids replacement lineage")
    else:
        expected = (
            from_state is DealingRangeState.ACTIVE
            and to_state is DealingRangeState.SUPERSEDED
        )
        _validate_hash(related_event_id, name="related_event_id")
        _validate_hash(replacement_lineage_id, name="replacement_lineage_id")
    if not expected:
        raise ValueError("transition state graph does not match reason token")


def _validate_transition_history(
    active: _ActiveRange,
    *,
    expected_state: DealingRangeState,
    instrument: str,
    timeframe: str,
) -> None:
    if not active.transitions:
        raise _InvalidAnalysis("external range requires a transition history")
    previous_state: DealingRangeState | None = None
    previous_index = -1
    previous_timestamp: datetime | None = None
    seen_ids: set[str] = set()
    for position, transition in enumerate(active.transitions):
        if not isinstance(transition, DealingRangeTransition):
            raise _InvalidAnalysis("transition history contains an invalid record")
        if transition.lineage_id != active.lineage_id:
            raise _InvalidAnalysis("transition lineage does not match active range")
        if transition.from_state is not previous_state:
            raise _InvalidAnalysis("transition history has a broken state chain")
        normalized_timestamp = normalize_utc_timestamp(transition.timestamp)
        if transition.index <= previous_index:
            raise _InvalidAnalysis("transition indices must be strictly chronological")
        if previous_timestamp is not None and normalized_timestamp <= previous_timestamp:
            raise _InvalidAnalysis("transition timestamps must be strictly chronological")
        expected_id = make_dealing_range_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=active.direction,
            source_indices=(transition.index,),
            lineage_id=transition.lineage_id,
            transition_from_state=transition.from_state,
            transition_to_state=transition.to_state,
            transition_index=transition.index,
            transition_timestamp=transition.timestamp,
            transition_reason=transition.reason,
            related_event_id=transition.related_event_id,
            replacement_lineage_id=transition.replacement_lineage_id,
        )
        if transition.transition_id != expected_id:
            raise _InvalidAnalysis("transition_id does not match canonical identity")
        if transition.transition_id in seen_ids:
            raise _InvalidAnalysis("duplicate transition identity")
        if position < len(active.transitions) - 1 and transition.to_state in (
            DealingRangeState.INVALIDATED,
            DealingRangeState.SUPERSEDED,
        ):
            raise _InvalidAnalysis("terminal transition cannot be followed")
        seen_ids.add(transition.transition_id)
        previous_state = transition.to_state
        previous_index = transition.index
        previous_timestamp = normalized_timestamp
    if previous_state is not expected_state:
        raise _InvalidAnalysis("snapshot state does not match transition history")


def _closed_interval(
    observations_by_index: dict[int, DealingRangeObservation],
    start: int,
    end: int,
) -> tuple[DealingRangeObservation, ...]:
    if start > end:
        raise _InvalidAnalysis("interval start cannot follow confirmation")
    rows = []
    for index in range(start, end + 1):
        observation = observations_by_index.get(index)
        if observation is None:
            raise _UnknownAnalysis("required closed observation interval is incomplete")
        rows.append(observation)
    return tuple(rows)


def _required_observation(
    observations_by_index: dict[int, DealingRangeObservation],
    index: int,
) -> DealingRangeObservation:
    observation = observations_by_index.get(index)
    if observation is None:
        raise _UnknownAnalysis(f"required observation is missing at index {index}")
    return observation


def _find_swing(
    swings: tuple[DealingRangeSwing, ...],
    swing_id: str,
) -> DealingRangeSwing:
    for swing in swings:
        if swing.swing_id == swing_id:
            return swing
    raise _InvalidAnalysis("referenced swing is missing")


def _chronological_swings(
    swings: tuple[DealingRangeSwing, ...],
) -> tuple[DealingRangeSwing, ...]:
    unique = {swing.swing_id: swing for swing in swings}
    ordered = tuple(sorted(
        unique.values(),
        key=lambda swing: (_source_index(swing), swing.side.value, swing.swing_id),
    ))
    if len({_source_index(swing) for swing in ordered}) != len(ordered):
        raise _InvalidAnalysis("range identity requires distinct source indices")
    return ordered


def _observation_provenance(
    observation: DealingRangeObservation,
) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=(observation.index,),
        source_timestamps=(normalize_utc_timestamp(observation.timestamp),),
        confirmation_index=observation.index,
        confirmation_timestamp=normalize_utc_timestamp(observation.timestamp),
    )


def _source_index(swing: DealingRangeSwing) -> int:
    return swing.provenance.source_indices[0]


def _midpoint(low_tick: int, high_tick: int) -> Decimal:
    return Decimal(low_tick + high_tick) / Decimal(2)


def _boundary_payload(boundaries: SMCV2TickRange) -> dict[str, int]:
    return {
        "lower_tick": boundaries.lower_tick,
        "upper_tick": boundaries.upper_tick,
    }


def _serialize_timestamp(value: datetime | None) -> str:
    if value is None:
        raise TypeError("transition_timestamp is required")
    normalized = normalize_utc_timestamp(value)
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_boundaries(
    boundaries: SMCV2TickRange | None,
    *,
    allow_zero_width: bool = False,
) -> tuple[int, int]:
    if not isinstance(boundaries, SMCV2TickRange):
        raise TypeError("boundaries must be SMCV2TickRange")
    lower_tick = _required_attribute(boundaries, "lower_tick", owner="SMCV2TickRange")
    upper_tick = _required_attribute(boundaries, "upper_tick", owner="SMCV2TickRange")
    if type(lower_tick) is not int or type(upper_tick) is not int:
        raise TypeError("range boundaries must contain integer ticks")
    if allow_zero_width and lower_tick > upper_tick:
        raise ValueError("range boundaries cannot invert lower and upper ticks")
    if not allow_zero_width and lower_tick >= upper_tick:
        raise ValueError("range boundaries must have positive width")
    return lower_tick, upper_tick


def _validate_source_indices(source_indices: object) -> None:
    if not isinstance(source_indices, tuple):
        raise TypeError("source_indices must be a tuple")
    if not source_indices:
        raise ValueError("source_indices cannot be empty")
    if any(type(index) is not int for index in source_indices):
        raise TypeError("source_indices must contain integers")
    if any(index < 0 for index in source_indices):
        raise ValueError("source_indices cannot contain negative values")
    if any(left >= right for left, right in zip(source_indices, source_indices[1:])):
        raise ValueError("source_indices must be unique and strictly increasing")


def _validate_hash_tuple(values: object, *, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    for value in values:
        _validate_hash(value, name=name)
    if len(set(values)) != len(values):
        raise ValueError(f"{name} cannot contain duplicates")


def _validate_hash(value: object, *, name: str) -> None:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase 64-character hexadecimal text")


def _validate_non_negative_int(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _normalize_required_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _required_attribute(instance: object, name: str, *, owner: str) -> object:
    dataclass_fields = getattr(type(instance), "__dataclass_fields__", {})
    instance_values = getattr(instance, "__dict__", {})
    if name in dataclass_fields and name not in instance_values:
        raise _InvalidAnalysis(f"{owner} is missing required field: {name}")
    value = getattr(instance, name, _MISSING)
    if value is _MISSING:
        raise _InvalidAnalysis(f"{owner} is missing required field: {name}")
    return value


def _require_empty(value: tuple[object, ...], *, name: str) -> None:
    if value:
        raise ValueError(f"{name} must be empty for this identity kind")


def _require_length(value: tuple[object, ...], length: int, *, name: str) -> None:
    if len(value) != length:
        raise ValueError(f"{name} must contain exactly {length} values")


def _reject_non_defaults(**values: object) -> None:
    for name, value in values.items():
        if value not in (None, ()):
            raise ValueError(f"{name} is forbidden for this identity kind")


__all__ = [
    "DEALING_RANGE_DETECTOR_VERSION",
    "DealingRangeSwingSide",
    "DealingRangeEventType",
    "DealingRangeKind",
    "DealingRangeState",
    "DealingRangeConfig",
    "DealingRangeSwing",
    "DealingRangeObservation",
    "DealingRangeStructureEvent",
    "DealingRangeTransition",
    "DealingRangeSnapshot",
    "DealingRangeResult",
    "make_dealing_range_id",
    "analyze_dealing_ranges",
]
