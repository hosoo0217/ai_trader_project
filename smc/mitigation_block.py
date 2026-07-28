"""Deterministic standalone Mitigation Block diagnostics.

This module consumes canonical Order Block evidence and fully closed integer-tick
observations.  It performs no I/O, registration, strategy, risk, execution, or
integration work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from smc.order_block import (
    OrderBlock,
    OrderBlockSnapshot,
    OrderBlockState,
    OrderBlockTransition,
    make_order_block_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


MITIGATION_BLOCK_DETECTOR_VERSION = "SMC-V2-MITIGATION-BLOCK-1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_KINDS = frozenset({"MITIGATION", "TRANSITION", "SNAPSHOT"})
_CREATION = "FIRST_QUALIFYING_MIDPOINT_RETEST"
_INVALIDATION = "SOURCE_CLOSE_THROUGH_INVALIDATION"
_SOURCE_CREATION = {
    OrderBlockState.MITIGATED: "MIDPOINT_MITIGATION",
    OrderBlockState.FULLY_TRAVERSED: "DISTAL_TRAVERSAL",
}
_SOURCE_REASONS = {
    (None, OrderBlockState.DETECTED): "FORMATION_CONFIRMED",
    (OrderBlockState.DETECTED, OrderBlockState.ACTIVE): "FIRST_ELIGIBLE_BAR",
    (OrderBlockState.ACTIVE, OrderBlockState.TOUCHED): "WICK_TOUCHED",
    (OrderBlockState.ACTIVE, OrderBlockState.PARTIALLY_MITIGATED): "PARTIAL_MITIGATION",
    (OrderBlockState.ACTIVE, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.ACTIVE, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.TOUCHED, OrderBlockState.PARTIALLY_MITIGATED): "PARTIAL_MITIGATION",
    (OrderBlockState.TOUCHED, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.TOUCHED, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
    (OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.MITIGATED): "MIDPOINT_MITIGATION",
    (OrderBlockState.PARTIALLY_MITIGATED, OrderBlockState.FULLY_TRAVERSED): "DISTAL_TRAVERSAL",
}
_SOURCE_ELIGIBLE = frozenset(
    {
        OrderBlockState.ACTIVE,
        OrderBlockState.TOUCHED,
        OrderBlockState.PARTIALLY_MITIGATED,
    }
)
_SOURCE_TERMINAL_FOR_CREATION = frozenset(
    {
        OrderBlockState.MITIGATED,
        OrderBlockState.FULLY_TRAVERSED,
        OrderBlockState.INVALIDATED,
    }
)

_Moment = tuple[int, datetime]


class MitigationBlockState(str, Enum):
    MITIGATED = "MITIGATED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class MitigationBlockObservation:
    index: int
    timestamp: datetime
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class MitigationBlock:
    mitigation_id: str
    direction: SMCV2Direction
    source_order_block_id: str
    source_order_block_snapshot_id: str
    source_order_block_transition_id: str
    wick_low_tick: int
    wick_high_tick: int
    body_low_tick: int
    body_high_tick: int
    proximal_tick: int
    distal_tick: int
    midpoint_tick: Decimal
    first_retouch_index: int
    first_retouch_timestamp: datetime
    deepest_penetration_tick: int
    close_tick: int
    midpoint_reached: bool


@dataclass(frozen=True)
class MitigationBlockTransition:
    transition_id: str
    mitigation_id: str
    source_order_block_id: str
    source_order_block_snapshot_id: str
    source_order_block_transition_id: str
    from_state: MitigationBlockState | None
    to_state: MitigationBlockState
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class MitigationBlockSnapshot:
    snapshot_id: str
    mitigation_id: str
    source_order_block_id: str
    source_order_block_snapshot_id: str
    source_order_block_transition_id: str
    direction: SMCV2Direction
    state: MitigationBlockState
    index: int
    timestamp: datetime
    transition_ids: tuple[str, ...]


@dataclass(frozen=True)
class MitigationBlockResult:
    status: SMCV2PrimitiveStatus
    mitigations: tuple[MitigationBlock, ...] = ()
    transitions: tuple[MitigationBlockTransition, ...] = ()
    snapshots: tuple[MitigationBlockSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Issue:
    moment: _Moment | None
    reason: str


@dataclass(frozen=True)
class _SourceHistory:
    block: OrderBlock
    transitions: tuple[OrderBlockTransition, ...]
    snapshots: tuple[OrderBlockSnapshot, ...]


@dataclass
class _Runtime:
    mitigation: MitigationBlock
    state: MitigationBlockState
    transition_ids: tuple[str, ...]


@dataclass
class _AnalysisState:
    mitigations: list[MitigationBlock]
    transitions: list[MitigationBlockTransition]
    snapshots: list[MitigationBlockSnapshot]
    runtimes: dict[str, _Runtime]

    def clone(self) -> "_AnalysisState":
        return _AnalysisState(
            mitigations=list(self.mitigations),
            transitions=list(self.transitions),
            snapshots=list(self.snapshots),
            runtimes=dict(self.runtimes),
        )


class _InvalidGroup(ValueError):
    pass


def make_mitigation_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_order_block_id: str | None = None,
    source_order_block_snapshot_id: str | None = None,
    source_order_block_transition_id: str | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    first_retouch_index: int | None = None,
    first_retouch_timestamp: datetime | None = None,
    deepest_penetration_tick: int | None = None,
    close_tick: int | None = None,
    midpoint_reached: bool | None = None,
    mitigation_id: str | None = None,
    from_state: MitigationBlockState | None = None,
    to_state: MitigationBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: MitigationBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    """Build one exact kind-specific Mitigation Block identity."""

    try:
        return _make_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_order_block_id=source_order_block_id,
            source_order_block_snapshot_id=source_order_block_snapshot_id,
            source_order_block_transition_id=source_order_block_transition_id,
            wick_boundaries=wick_boundaries,
            body_boundaries=body_boundaries,
            proximal_tick=proximal_tick,
            distal_tick=distal_tick,
            midpoint_tick=midpoint_tick,
            first_retouch_index=first_retouch_index,
            first_retouch_timestamp=first_retouch_timestamp,
            deepest_penetration_tick=deepest_penetration_tick,
            close_tick=close_tick,
            midpoint_reached=midpoint_reached,
            mitigation_id=mitigation_id,
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
        raise ValueError("identity_kind is not a locked Mitigation Block identity kind")
    direction = values["direction"]
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")
    payload: dict[str, object] = {
        "detector_version": MITIGATION_BLOCK_DETECTOR_VERSION,
        "identity_kind": kind,
        "instrument": _text(values["instrument"], "instrument"),
        "timeframe": _text(values["timeframe"], "timeframe"),
        "direction": direction.value,
        "source_order_block_id": _hash(
            values["source_order_block_id"], "source_order_block_id"
        ),
        "source_order_block_snapshot_id": _hash(
            values["source_order_block_snapshot_id"],
            "source_order_block_snapshot_id",
        ),
        "source_order_block_transition_id": _hash(
            values["source_order_block_transition_id"],
            "source_order_block_transition_id",
        ),
    }
    geometry_fields = (
        "wick_boundaries",
        "body_boundaries",
        "proximal_tick",
        "distal_tick",
        "midpoint_tick",
        "first_retouch_index",
        "first_retouch_timestamp",
        "deepest_penetration_tick",
        "close_tick",
        "midpoint_reached",
    )
    transition_fields = (
        "mitigation_id",
        "from_state",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
    )
    if kind == "MITIGATION":
        _defaults(values, (*transition_fields, "state", "transition_ids"))
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
            raise ValueError("proximal/distal do not reconcile with direction")
        midpoint = _midpoint(wick.lower_tick, wick.upper_tick)
        supplied_midpoint = values["midpoint_tick"]
        if not isinstance(supplied_midpoint, Decimal) or supplied_midpoint != midpoint:
            raise ValueError("midpoint_tick does not reconcile with wick boundaries")
        first_index = _nonnegative_integer(
            values["first_retouch_index"], "first_retouch_index"
        )
        first_time = _timestamp(
            values["first_retouch_timestamp"], "first_retouch_timestamp"
        )
        deepest = _integer(
            values["deepest_penetration_tick"], "deepest_penetration_tick"
        )
        close = _integer(values["close_tick"], "close_tick")
        if values["midpoint_reached"] is not True:
            raise ValueError("midpoint_reached must be exactly True")
        if direction is SMCV2Direction.BULLISH:
            if Decimal(deepest) > midpoint:
                raise ValueError("bullish deepest penetration must reach midpoint")
            if close < deepest:
                raise ValueError("bullish close cannot be below deepest penetration")
            if close <= distal - 1:
                raise ValueError(
                    "bullish close meets adverse one-tick invalidation"
                )
        else:
            if Decimal(deepest) < midpoint:
                raise ValueError("bearish deepest penetration must reach midpoint")
            if close > deepest:
                raise ValueError("bearish close cannot exceed deepest penetration")
            if close >= distal + 1:
                raise ValueError(
                    "bearish close meets adverse one-tick invalidation"
                )
        payload.update(
            {
                "wick_boundaries": [wick.lower_tick, wick.upper_tick],
                "body_boundaries": [body.lower_tick, body.upper_tick],
                "proximal_tick": proximal,
                "distal_tick": distal,
                "midpoint_tick": _decimal_text(midpoint),
                "first_retouch_index": first_index,
                "first_retouch_timestamp": _timestamp_text(first_time),
                "deepest_penetration_tick": deepest,
                "close_tick": close,
                "midpoint_reached": True,
            }
        )
    elif kind == "TRANSITION":
        _defaults(values, (*geometry_fields, "state", "transition_ids"))
        mitigation = _hash(values["mitigation_id"], "mitigation_id")
        from_state = values["from_state"]
        to_state = values["to_state"]
        transition_reason = values["reason"]
        _mitigation_edge(from_state, to_state, transition_reason)
        index = _nonnegative_integer(values["effective_index"], "effective_index")
        timestamp = _timestamp(
            values["effective_timestamp"], "effective_timestamp"
        )
        payload.update(
            {
                "mitigation_id": mitigation,
                "from_state": None if from_state is None else from_state.value,
                "to_state": to_state.value,
                "effective_index": index,
                "effective_timestamp": _timestamp_text(timestamp),
                "reason": transition_reason,
            }
        )
    else:
        _defaults(
            values,
            (*geometry_fields, "from_state", "to_state", "reason"),
        )
        mitigation = _hash(values["mitigation_id"], "mitigation_id")
        snapshot_state = values["state"]
        if not isinstance(snapshot_state, MitigationBlockState):
            raise TypeError("state must be MitigationBlockState")
        index = _nonnegative_integer(values["effective_index"], "effective_index")
        timestamp = _timestamp(
            values["effective_timestamp"], "effective_timestamp"
        )
        ids = _hash_tuple(
            values["transition_ids"], "transition_ids", allow_empty=False
        )
        if len(set(ids)) != len(ids):
            raise ValueError("transition_ids cannot contain duplicates")
        payload.update(
            {
                "mitigation_id": mitigation,
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


def analyze_mitigation_blocks(
    *,
    instrument: str,
    timeframe: str,
    order_blocks: tuple[OrderBlock, ...] | None,
    order_block_transitions: tuple[OrderBlockTransition, ...] | None,
    order_block_snapshots: tuple[OrderBlockSnapshot, ...] | None,
    observations: tuple[MitigationBlockObservation, ...] | None,
) -> MitigationBlockResult:
    """Analyze canonical source history and closed retest observations."""

    missing = tuple(
        name
        for name, value in (
            ("order_blocks", order_blocks),
            ("order_block_transitions", order_block_transitions),
            ("order_block_snapshots", order_block_snapshots),
            ("observations", observations),
        )
        if value is None
    )
    if missing:
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return MitigationBlockResult(
            SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    state = _AnalysisState([], [], [], {})
    try:
        canonical_instrument = _text(instrument, "instrument")
        canonical_timeframe = _text(timeframe, "timeframe")
        if not isinstance(order_blocks, tuple):
            raise TypeError("order_blocks must be a tuple")
        if not isinstance(order_block_transitions, tuple):
            raise TypeError("order_block_transitions must be a tuple")
        if not isinstance(order_block_snapshots, tuple):
            raise TypeError("order_block_snapshots must be a tuple")
        if not isinstance(observations, tuple):
            raise TypeError("observations must be a tuple")

        blocks = _validate_blocks(
            canonical_instrument, canonical_timeframe, order_blocks
        )
        transition_values, transition_issue = _collect_source_transitions(
            order_block_transitions
        )
        snapshot_values, snapshot_issue = _collect_source_snapshots(
            order_block_snapshots
        )
        observation_values, observation_issue = _collect_observations(observations)
        issues = tuple(
            issue
            for issue in (transition_issue, snapshot_issue, observation_issue)
            if issue is not None
        )
        if any(issue.moment is None for issue in issues):
            issue = next(issue for issue in issues if issue.moment is None)
            return _invalid(state, issue.reason)
        cutoff = min(
            (issue.moment for issue in issues if issue.moment is not None),
            default=None,
        )
        if cutoff is not None:
            transition_values = tuple(
                value
                for value in transition_values
                if _source_transition_moment(value) < cutoff
            )
            snapshot_values = tuple(
                value
                for value in snapshot_values
                if _source_snapshot_moment(value) < cutoff
            )
            observation_values = tuple(
                value
                for value in observation_values
                if _observation_moment(value) < cutoff
            )

        histories, history_issue = _validate_source_history_with_issue(
            canonical_instrument,
            canonical_timeframe,
            blocks,
            transition_values,
            snapshot_values,
        )
        if history_issue is not None:
            issues = (*issues, history_issue)
            if cutoff is None or (
                history_issue.moment is not None and history_issue.moment < cutoff
            ):
                cutoff = history_issue.moment
            if cutoff is None:
                return _invalid(state, history_issue.reason)
            transition_values = tuple(
                value
                for value in transition_values
                if _source_transition_moment(value) < cutoff
            )
            snapshot_values = tuple(
                value
                for value in snapshot_values
                if _source_snapshot_moment(value) < cutoff
            )
            observation_values = tuple(
                value
                for value in observation_values
                if _observation_moment(value) < cutoff
            )
            histories = _validate_source_history(
                canonical_instrument,
                canonical_timeframe,
                blocks,
                transition_values,
                snapshot_values,
                require_formation=False,
            )
        unknown_coverage = _analyze_valid_prefix(
            canonical_instrument,
            canonical_timeframe,
            histories,
            observation_values,
            state,
        )
        if cutoff is not None:
            reason = next(
                issue.reason for issue in issues if issue.moment == cutoff
            )
            return _invalid(state, reason)
        if unknown_coverage:
            reason = "Observation coverage cannot reconstruct the first midpoint retest"
            return MitigationBlockResult(
                SMCV2PrimitiveStatus.UNKNOWN,
                tuple(state.mitigations),
                tuple(state.transitions),
                tuple(state.snapshots),
                (reason,),
                (reason,),
            )
        if state.mitigations:
            return MitigationBlockResult(
                SMCV2PrimitiveStatus.VALID,
                tuple(state.mitigations),
                tuple(state.transitions),
                tuple(state.snapshots),
            )
        return MitigationBlockResult(SMCV2PrimitiveStatus.NONE)
    except (
        TypeError,
        ValueError,
        AttributeError,
        KeyError,
        IndexError,
    ) as exc:
        return _invalid(state, str(exc) or "Invalid Mitigation Block evidence")


def _analyze_valid_prefix(
    instrument: str,
    timeframe: str,
    histories: tuple[_SourceHistory, ...],
    observations: tuple[MitigationBlockObservation, ...],
    state: _AnalysisState,
) -> bool:
    if not observations:
        return any(
            transition.to_state
            in (OrderBlockState.MITIGATED, OrderBlockState.FULLY_TRAVERSED)
            for history in histories
            for transition in history.transitions
        )
    first_moment = _observation_moment(observations[0])
    final_moment = _observation_moment(observations[-1])
    observation_moments = {_observation_moment(item) for item in observations}

    unknown_sources: set[str] = set()
    for history in histories:
        for transition in history.transitions:
            moment = _source_transition_moment(transition)
            if moment < first_moment and transition.to_state in (
                OrderBlockState.MITIGATED,
                OrderBlockState.FULLY_TRAVERSED,
            ):
                unknown_sources.add(history.block.block_id)
            if moment > final_moment and transition.index > history.block.detection_index:
                raise _InvalidGroup("source history extends beyond observation horizon")
            if (
                first_moment <= moment <= final_moment
                and transition.index > history.block.detection_index
                and moment not in observation_moments
            ):
                raise _InvalidGroup(
                    "in-horizon source transition lacks an observation"
                )
    for observation in observations:
        moment = _observation_moment(observation)
        group_state = state.clone()
        try:
            for history in histories:
                if history.block.block_id in unknown_sources:
                    _validate_unknown_source_group(history, observation, moment)
                else:
                    _process_source_group(
                        instrument,
                        timeframe,
                        history,
                        observation,
                        moment,
                        group_state,
                        first_moment,
                    )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            raise _InvalidGroup(str(exc) or "invalid effective group") from exc
        state.mitigations = group_state.mitigations
        state.transitions = group_state.transitions
        state.snapshots = group_state.snapshots
        state.runtimes = group_state.runtimes
    return bool(unknown_sources)


def _validate_unknown_source_group(
    history: _SourceHistory,
    observation: MitigationBlockObservation,
    moment: _Moment,
) -> None:
    before = tuple(
        transition
        for transition in history.transitions
        if _source_transition_moment(transition) < moment
    )
    same = tuple(
        transition
        for transition in history.transitions
        if _source_transition_moment(transition) == moment
    )
    pre_state = before[-1].to_state if before else None
    if pre_state is OrderBlockState.INVALIDATED:
        if same:
            raise _InvalidGroup("terminal unknown-coverage source has later transitions")
        return
    if pre_state not in (
        OrderBlockState.MITIGATED,
        OrderBlockState.FULLY_TRAVERSED,
    ):
        raise _InvalidGroup("unknown-coverage source state is not canonical")
    if _close_through(history.block, observation):
        if len(same) != 1 or not _is_source_invalidation(same[0], pre_state):
            raise _InvalidGroup(
                "unknown-coverage source invalidation does not reconcile"
            )
        _snapshot_for_transition(history, same[0])
    elif same:
        raise _InvalidGroup(
            "unknown-coverage source transition lacks geometric cause"
        )


def _process_source_group(
    instrument: str,
    timeframe: str,
    history: _SourceHistory,
    observation: MitigationBlockObservation,
    moment: _Moment,
    state: _AnalysisState,
    first_observation_moment: _Moment,
) -> None:
    block = history.block
    before = tuple(
        transition
        for transition in history.transitions
        if _source_transition_moment(transition) < moment
    )
    same = tuple(
        transition
        for transition in history.transitions
        if _source_transition_moment(transition) == moment
    )
    after = tuple(
        transition
        for transition in history.transitions
        if _source_transition_moment(transition) > moment
    )
    del after
    pre_state = before[-1].to_state if before else None
    runtime = state.runtimes.get(block.block_id)

    if runtime is not None:
        if runtime.state is MitigationBlockState.INVALIDATED:
            if same:
                raise _InvalidGroup("terminal mitigation source has later transitions")
            return
        close_through = _close_through(block, observation)
        if close_through:
            if len(same) != 1 or not _is_source_invalidation(same[0], pre_state):
                raise _InvalidGroup("source invalidation evidence does not reconcile")
            source_snapshot = _snapshot_for_transition(history, same[0])
            _append_invalidation(
                instrument,
                timeframe,
                block,
                runtime,
                same[0],
                source_snapshot,
                observation,
                state,
            )
        elif same:
            raise _InvalidGroup("unexpected source transition after mitigation creation")
        return

    current_state = pre_state
    remaining = list(same)
    if current_state is None:
        if (
            block.detection_index == observation.index
            and block.detection_timestamp == observation.timestamp
        ):
            raise _InvalidGroup("formation observation cannot create mitigation")
        if moment > (block.detection_index, block.detection_timestamp):
            raise _InvalidGroup("source history lacks formation state")
        return
    if current_state is OrderBlockState.DETECTED and remaining:
        first = remaining[0]
        if (
            first.from_state is OrderBlockState.DETECTED
            and first.to_state is OrderBlockState.ACTIVE
            and first.reason == "FIRST_ELIGIBLE_BAR"
        ):
            current_state = OrderBlockState.ACTIVE
            remaining.pop(0)

    if moment <= (block.detection_index, block.detection_timestamp):
        if remaining:
            raise _InvalidGroup("formation moment cannot qualify")
        return
    if current_state in _SOURCE_TERMINAL_FOR_CREATION:
        if remaining:
            raise _InvalidGroup("terminal source has contradictory later transition")
        return
    if current_state not in _SOURCE_ELIGIBLE:
        if remaining:
            raise _InvalidGroup("source is not eligible for transition")
        return

    expected_state = _expected_source_state(block, observation)
    if expected_state is None:
        if remaining:
            raise _InvalidGroup("source transition lacks geometric cause")
        return
    if (
        expected_state is not OrderBlockState.INVALIDATED
        and _source_depth_rank(expected_state) <= _source_depth_rank(current_state)
    ):
        expected_state = current_state
    if expected_state is current_state:
        if remaining:
            raise _InvalidGroup("source state must not repeat")
        return
    if len(remaining) != 1:
        raise _InvalidGroup("source state change requires one canonical transition")
    transition = remaining[0]
    if (
        transition.from_state is not current_state
        or transition.to_state is not expected_state
        or not _source_transition_reason_matches(transition)
    ):
        raise _InvalidGroup("source transition does not reconcile with observation")
    source_snapshot = _snapshot_for_transition(history, transition)
    if expected_state is OrderBlockState.INVALIDATED:
        return
    if expected_state not in (
        OrderBlockState.MITIGATED,
        OrderBlockState.FULLY_TRAVERSED,
    ):
        return
    if _close_through(block, observation):
        return
    _append_creation(
        instrument,
        timeframe,
        block,
        transition,
        source_snapshot,
        observation,
        state,
    )


def _append_creation(
    instrument: str,
    timeframe: str,
    block: OrderBlock,
    source_transition: OrderBlockTransition,
    source_snapshot: OrderBlockSnapshot,
    observation: MitigationBlockObservation,
    state: _AnalysisState,
) -> None:
    deepest = (
        observation.low_tick
        if block.direction is SMCV2Direction.BULLISH
        else observation.high_tick
    )
    kwargs = dict(
        instrument=instrument,
        timeframe=timeframe,
        direction=block.direction,
        source_order_block_id=block.block_id,
        source_order_block_snapshot_id=source_snapshot.snapshot_id,
        source_order_block_transition_id=source_transition.transition_id,
    )
    mitigation_id = make_mitigation_block_id(
        identity_kind="MITIGATION",
        **kwargs,
        wick_boundaries=SMCV2TickRange(block.wick_low_tick, block.wick_high_tick),
        body_boundaries=SMCV2TickRange(block.body_low_tick, block.body_high_tick),
        proximal_tick=block.proximal_tick,
        distal_tick=block.distal_tick,
        midpoint_tick=block.midpoint_tick,
        first_retouch_index=observation.index,
        first_retouch_timestamp=observation.timestamp,
        deepest_penetration_tick=deepest,
        close_tick=observation.close_tick,
        midpoint_reached=True,
    )
    mitigation = MitigationBlock(
        mitigation_id,
        block.direction,
        block.block_id,
        source_snapshot.snapshot_id,
        source_transition.transition_id,
        block.wick_low_tick,
        block.wick_high_tick,
        block.body_low_tick,
        block.body_high_tick,
        block.proximal_tick,
        block.distal_tick,
        block.midpoint_tick,
        observation.index,
        observation.timestamp,
        deepest,
        observation.close_tick,
        True,
    )
    transition_id = make_mitigation_block_id(
        identity_kind="TRANSITION",
        **kwargs,
        mitigation_id=mitigation_id,
        from_state=None,
        to_state=MitigationBlockState.MITIGATED,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        reason=_CREATION,
    )
    transition = MitigationBlockTransition(
        transition_id,
        mitigation_id,
        block.block_id,
        source_snapshot.snapshot_id,
        source_transition.transition_id,
        None,
        MitigationBlockState.MITIGATED,
        observation.index,
        observation.timestamp,
        _CREATION,
    )
    snapshot_id = make_mitigation_block_id(
        identity_kind="SNAPSHOT",
        **kwargs,
        mitigation_id=mitigation_id,
        state=MitigationBlockState.MITIGATED,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        transition_ids=(transition_id,),
    )
    snapshot = MitigationBlockSnapshot(
        snapshot_id,
        mitigation_id,
        block.block_id,
        source_snapshot.snapshot_id,
        source_transition.transition_id,
        block.direction,
        MitigationBlockState.MITIGATED,
        observation.index,
        observation.timestamp,
        (transition_id,),
    )
    state.mitigations.append(mitigation)
    state.transitions.append(transition)
    state.snapshots.append(snapshot)
    state.runtimes[block.block_id] = _Runtime(
        mitigation, MitigationBlockState.MITIGATED, (transition_id,)
    )


def _append_invalidation(
    instrument: str,
    timeframe: str,
    block: OrderBlock,
    runtime: _Runtime,
    source_transition: OrderBlockTransition,
    source_snapshot: OrderBlockSnapshot,
    observation: MitigationBlockObservation,
    state: _AnalysisState,
) -> None:
    kwargs = dict(
        instrument=instrument,
        timeframe=timeframe,
        direction=block.direction,
        source_order_block_id=block.block_id,
        source_order_block_snapshot_id=source_snapshot.snapshot_id,
        source_order_block_transition_id=source_transition.transition_id,
        mitigation_id=runtime.mitigation.mitigation_id,
    )
    transition_id = make_mitigation_block_id(
        identity_kind="TRANSITION",
        **kwargs,
        from_state=MitigationBlockState.MITIGATED,
        to_state=MitigationBlockState.INVALIDATED,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        reason=_INVALIDATION,
    )
    transition = MitigationBlockTransition(
        transition_id,
        runtime.mitigation.mitigation_id,
        block.block_id,
        source_snapshot.snapshot_id,
        source_transition.transition_id,
        MitigationBlockState.MITIGATED,
        MitigationBlockState.INVALIDATED,
        observation.index,
        observation.timestamp,
        _INVALIDATION,
    )
    ids = runtime.transition_ids + (transition_id,)
    snapshot_id = make_mitigation_block_id(
        identity_kind="SNAPSHOT",
        **kwargs,
        state=MitigationBlockState.INVALIDATED,
        effective_index=observation.index,
        effective_timestamp=observation.timestamp,
        transition_ids=ids,
    )
    snapshot = MitigationBlockSnapshot(
        snapshot_id,
        runtime.mitigation.mitigation_id,
        block.block_id,
        source_snapshot.snapshot_id,
        source_transition.transition_id,
        block.direction,
        MitigationBlockState.INVALIDATED,
        observation.index,
        observation.timestamp,
        ids,
    )
    state.transitions.append(transition)
    state.snapshots.append(snapshot)
    state.runtimes[block.block_id] = _Runtime(
        runtime.mitigation, MitigationBlockState.INVALIDATED, ids
    )


def _validate_blocks(
    instrument: str, timeframe: str, values: tuple[OrderBlock, ...]
) -> tuple[OrderBlock, ...]:
    canonical: list[OrderBlock] = []
    prior_key: tuple[object, ...] | None = None
    ids: set[str] = set()
    for value in values:
        if type(value) is not OrderBlock:
            raise TypeError("every order block must be an exact OrderBlock")
        direction = value.direction
        if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("source direction must be BULLISH or BEARISH")
        source_index = _nonnegative_integer(
            value.source_candle_index, "source_candle_index"
        )
        source_time = _timestamp(
            value.source_candle_timestamp, "source_candle_timestamp"
        )
        displacement_indices = _strict_indices(
            value.displacement_indices, "displacement_indices", minimum=1, maximum=3
        )
        displacement_times = _strict_timestamps(
            value.displacement_timestamps,
            "displacement_timestamps",
            expected_length=len(displacement_indices),
        )
        detection_index = _nonnegative_integer(
            value.detection_index, "detection_index"
        )
        detection_time = _timestamp(
            value.detection_timestamp, "detection_timestamp"
        )
        if source_index >= displacement_indices[0] or source_time >= displacement_times[0]:
            raise ValueError("source must strictly precede displacement")
        if (
            detection_index != displacement_indices[-1]
            or detection_time != displacement_times[-1]
        ):
            raise ValueError("detection must equal final displacement moment")
        expected_id = make_order_block_id(
            identity_kind="BLOCK",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_candle_index=source_index,
            source_candle_timestamp=source_time,
            source_swing_id=_hash(value.source_swing_id, "source_swing_id"),
            displacement_indices=displacement_indices,
            displacement_timestamps=displacement_times,
            structure_event_id=_hash(
                value.structure_event_id, "structure_event_id"
            ),
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
        if _hash(value.block_id, "block_id") != expected_id:
            raise ValueError("source Order Block identity is not canonical")
        key = (
            detection_index,
            detection_time,
            source_index,
            direction.value,
            displacement_indices,
            value.block_id,
        )
        if prior_key is not None and key <= prior_key:
            raise ValueError("source Order Blocks are not in canonical formation order")
        if value.block_id in ids:
            raise ValueError("duplicate source Order Block")
        ids.add(value.block_id)
        prior_key = key
        canonical.append(value)
    return tuple(canonical)


def _collect_source_transitions(
    values: tuple[OrderBlockTransition, ...],
) -> tuple[tuple[OrderBlockTransition, ...], _Issue | None]:
    valid: list[OrderBlockTransition] = []
    for value in values:
        try:
            if type(value) is not OrderBlockTransition:
                raise TypeError("every source transition must be exact OrderBlockTransition")
            _hash(value.transition_id, "source transition_id")
            _hash(value.block_id, "source transition block_id")
            _nonnegative_integer(value.index, "source transition index")
            _timestamp(value.timestamp, "source transition timestamp")
            valid.append(value)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(valid), _Issue(
                _safe_moment(value, "index", "timestamp"),
                str(exc) or "malformed source transition",
            )
    return tuple(valid), None


def _collect_source_snapshots(
    values: tuple[OrderBlockSnapshot, ...],
) -> tuple[tuple[OrderBlockSnapshot, ...], _Issue | None]:
    valid: list[OrderBlockSnapshot] = []
    for value in values:
        try:
            if type(value) is not OrderBlockSnapshot:
                raise TypeError("every source snapshot must be exact OrderBlockSnapshot")
            _hash(value.snapshot_id, "source snapshot_id")
            _hash(value.block_id, "source snapshot block_id")
            _nonnegative_integer(value.index, "source snapshot index")
            _timestamp(value.timestamp, "source snapshot timestamp")
            valid.append(value)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(valid), _Issue(
                _safe_moment(value, "index", "timestamp"),
                str(exc) or "malformed source snapshot",
            )
    return tuple(valid), None


def _collect_observations(
    values: tuple[MitigationBlockObservation, ...],
) -> tuple[tuple[MitigationBlockObservation, ...], _Issue | None]:
    valid: list[MitigationBlockObservation] = []
    prior_index: int | None = None
    prior_time: datetime | None = None
    for value in values:
        try:
            if type(value) is not MitigationBlockObservation:
                raise TypeError(
                    "every observation must be exact MitigationBlockObservation"
                )
            index = _nonnegative_integer(value.index, "observation index")
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
            normalized = MitigationBlockObservation(index, timestamp, high, low, close)
            valid.append(normalized)
            prior_index = index
            prior_time = timestamp
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(valid), _Issue(
                _safe_moment(value, "index", "timestamp"),
                str(exc) or "malformed observation",
            )
    return tuple(valid), None


def _validate_source_history(
    instrument: str,
    timeframe: str,
    blocks: tuple[OrderBlock, ...],
    transitions: tuple[OrderBlockTransition, ...],
    snapshots: tuple[OrderBlockSnapshot, ...],
    *,
    require_formation: bool = True,
) -> tuple[_SourceHistory, ...]:
    block_map = {block.block_id: block for block in blocks}
    if not blocks and (transitions or snapshots):
        raise ValueError("source history exists without source blocks")
    block_order = {block.block_id: index for index, block in enumerate(blocks)}
    prior_transition_key: tuple[object, ...] | None = None
    prior_snapshot_key: tuple[object, ...] | None = None
    grouped_transitions: dict[str, list[OrderBlockTransition]] = {
        block.block_id: [] for block in blocks
    }
    grouped_snapshots: dict[str, list[OrderBlockSnapshot]] = {
        block.block_id: [] for block in blocks
    }
    for transition in transitions:
        block = block_map.get(transition.block_id)
        if block is None:
            raise ValueError("source transition references absent block")
        expected_id = make_order_block_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=block.direction,
            block_id=block.block_id,
            from_state=transition.from_state,
            to_state=transition.to_state,
            effective_index=transition.index,
            effective_timestamp=transition.timestamp,
            reason=transition.reason,
        )
        if transition.transition_id != expected_id:
            raise ValueError("source transition identity is not canonical")
        key = (
            transition.index,
            transition.timestamp,
            block_order[block.block_id],
            len(grouped_transitions[block.block_id]),
        )
        if prior_transition_key is not None and key < prior_transition_key:
            raise ValueError("source transitions are not in causal order")
        prior_transition_key = key
        grouped_transitions[block.block_id].append(transition)
    for snapshot in snapshots:
        block = block_map.get(snapshot.block_id)
        if block is None:
            raise ValueError("source snapshot references absent block")
        if snapshot.direction is not block.direction:
            raise ValueError("source snapshot direction contradicts source block")
        expected_id = make_order_block_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=block.direction,
            block_id=block.block_id,
            state=snapshot.state,
            effective_index=snapshot.index,
            effective_timestamp=snapshot.timestamp,
            transition_ids=snapshot.transition_ids,
        )
        if snapshot.snapshot_id != expected_id:
            raise ValueError("source snapshot identity is not canonical")
        key = (
            snapshot.index,
            snapshot.timestamp,
            block_order[block.block_id],
            len(grouped_snapshots[block.block_id]),
        )
        if prior_snapshot_key is not None and key < prior_snapshot_key:
            raise ValueError("source snapshots are not in causal order")
        prior_snapshot_key = key
        grouped_snapshots[block.block_id].append(snapshot)
    result: list[_SourceHistory] = []
    for block in blocks:
        block_transitions = tuple(grouped_transitions[block.block_id])
        block_snapshots = tuple(grouped_snapshots[block.block_id])
        if len(block_transitions) != len(block_snapshots):
            raise ValueError("source transition/snapshot histories are incomplete")
        if require_formation and not block_transitions:
            raise ValueError("each source block requires complete formation history")
        prior_state: OrderBlockState | None = None
        ids: list[str] = []
        for position, (transition, snapshot) in enumerate(
            zip(block_transitions, block_snapshots)
        ):
            if position == 0 and (
                transition.from_state is not None
                or transition.to_state is not OrderBlockState.DETECTED
            ):
                raise ValueError("source history must begin with formation")
            if transition.from_state is not prior_state:
                raise ValueError("source transition chain is not contiguous")
            if not _source_transition_reason_matches(transition):
                raise ValueError("source transition reason is not canonical")
            if (
                transition.index < block.detection_index
                or transition.timestamp < block.detection_timestamp
            ):
                raise ValueError("source history precedes block detection")
            ids.append(transition.transition_id)
            if (
                snapshot.state is not transition.to_state
                or snapshot.index != transition.index
                or snapshot.timestamp != transition.timestamp
                or snapshot.transition_ids != tuple(ids)
            ):
                raise ValueError("source snapshot does not mirror transition history")
            prior_state = transition.to_state
        result.append(_SourceHistory(block, block_transitions, block_snapshots))
    return tuple(result)


def _validate_source_history_with_issue(
    instrument: str,
    timeframe: str,
    blocks: tuple[OrderBlock, ...],
    transitions: tuple[OrderBlockTransition, ...],
    snapshots: tuple[OrderBlockSnapshot, ...],
) -> tuple[tuple[_SourceHistory, ...], _Issue | None]:
    try:
        return (
            _validate_source_history(
                instrument,
                timeframe,
                blocks,
                transitions,
                snapshots,
            ),
            None,
        )
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as full_exc:
        moments = sorted(
            {
                *(_source_transition_moment(value) for value in transitions),
                *(_source_snapshot_moment(value) for value in snapshots),
            }
        )
        for moment in moments:
            transition_prefix = tuple(
                value
                for value in transitions
                if _source_transition_moment(value) <= moment
            )
            snapshot_prefix = tuple(
                value
                for value in snapshots
                if _source_snapshot_moment(value) <= moment
            )
            try:
                _validate_source_history(
                    instrument,
                    timeframe,
                    blocks,
                    transition_prefix,
                    snapshot_prefix,
                )
            except (
                TypeError,
                ValueError,
                AttributeError,
                KeyError,
                IndexError,
            ) as exc:
                prior_transitions = tuple(
                    value
                    for value in transitions
                    if _source_transition_moment(value) < moment
                )
                prior_snapshots = tuple(
                    value
                    for value in snapshots
                    if _source_snapshot_moment(value) < moment
                )
                prior = _validate_source_history(
                    instrument,
                    timeframe,
                    blocks,
                    prior_transitions,
                    prior_snapshots,
                    require_formation=False,
                )
                return prior, _Issue(
                    moment,
                    str(exc) or "invalid source-history effective group",
                )
        return (), _Issue(
            None,
            str(full_exc) or "invalid source history",
        )


def _source_transition_reason_matches(transition: OrderBlockTransition) -> bool:
    if transition.to_state is OrderBlockState.INVALIDATED:
        return (
            transition.from_state is not None
            and transition.from_state is not OrderBlockState.INVALIDATED
            and transition.reason == "CLOSE_THROUGH_INVALIDATION"
        )
    expected = _SOURCE_REASONS.get((transition.from_state, transition.to_state))
    return expected == transition.reason


def _expected_source_state(
    block: OrderBlock, observation: MitigationBlockObservation
) -> OrderBlockState | None:
    if _close_through(block, observation):
        return OrderBlockState.INVALIDATED
    if block.direction is SMCV2Direction.BULLISH:
        if observation.low_tick <= block.distal_tick:
            return OrderBlockState.FULLY_TRAVERSED
        if Decimal(observation.low_tick) <= block.midpoint_tick:
            return OrderBlockState.MITIGATED
        if observation.low_tick < block.proximal_tick:
            return OrderBlockState.PARTIALLY_MITIGATED
        if observation.low_tick == block.proximal_tick:
            return OrderBlockState.TOUCHED
    else:
        if observation.high_tick >= block.distal_tick:
            return OrderBlockState.FULLY_TRAVERSED
        if Decimal(observation.high_tick) >= block.midpoint_tick:
            return OrderBlockState.MITIGATED
        if observation.high_tick > block.proximal_tick:
            return OrderBlockState.PARTIALLY_MITIGATED
        if observation.high_tick == block.proximal_tick:
            return OrderBlockState.TOUCHED
    return None


def _source_depth_rank(state: OrderBlockState) -> int:
    return {
        OrderBlockState.DETECTED: -1,
        OrderBlockState.ACTIVE: 0,
        OrderBlockState.TOUCHED: 1,
        OrderBlockState.PARTIALLY_MITIGATED: 2,
        OrderBlockState.MITIGATED: 3,
        OrderBlockState.FULLY_TRAVERSED: 4,
        OrderBlockState.INVALIDATED: 5,
    }[state]


def _close_through(
    block: OrderBlock, observation: MitigationBlockObservation
) -> bool:
    if block.direction is SMCV2Direction.BULLISH:
        return observation.close_tick <= block.distal_tick - 1
    return observation.close_tick >= block.distal_tick + 1


def _is_source_invalidation(
    transition: OrderBlockTransition, prior_state: OrderBlockState | None
) -> bool:
    return (
        transition.from_state is prior_state
        and transition.to_state is OrderBlockState.INVALIDATED
        and transition.reason == "CLOSE_THROUGH_INVALIDATION"
    )


def _snapshot_for_transition(
    history: _SourceHistory, transition: OrderBlockTransition
) -> OrderBlockSnapshot:
    for snapshot in history.snapshots:
        if snapshot.transition_ids[-1] == transition.transition_id:
            return snapshot
    raise _InvalidGroup("source transition lacks corresponding snapshot")


def _mitigation_edge(
    from_state: object, to_state: object, reason: object
) -> None:
    if (
        from_state is None
        and to_state is MitigationBlockState.MITIGATED
        and reason == _CREATION
    ):
        return
    if (
        from_state is MitigationBlockState.MITIGATED
        and to_state is MitigationBlockState.INVALIDATED
        and reason == _INVALIDATION
    ):
        return
    raise ValueError("invalid Mitigation Block transition edge or reason")


def _invalid(state: _AnalysisState, reason: str) -> MitigationBlockResult:
    text = reason or "Invalid Mitigation Block evidence"
    return MitigationBlockResult(
        SMCV2PrimitiveStatus.INVALID,
        tuple(state.mitigations),
        tuple(state.transitions),
        tuple(state.snapshots),
        (text,),
        (text,),
    )


def _safe_moment(value: object, index_name: str, timestamp_name: str) -> _Moment | None:
    try:
        index = getattr(value, index_name)
        timestamp = getattr(value, timestamp_name)
        return (
            _nonnegative_integer(index, index_name),
            _timestamp(timestamp, timestamp_name),
        )
    except (TypeError, ValueError, AttributeError):
        return None


def _source_transition_moment(value: OrderBlockTransition) -> _Moment:
    return value.index, value.timestamp


def _source_snapshot_moment(value: OrderBlockSnapshot) -> _Moment:
    return value.index, value.timestamp


def _observation_moment(value: MitigationBlockObservation) -> _Moment:
    return value.index, value.timestamp


def _text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    canonical = value.strip().upper()
    if not canonical:
        raise ValueError(f"{name} cannot be empty")
    return canonical


def _hash(value: object, name: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 string")
    return value


def _integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    return value


def _nonnegative_integer(value: object, name: str) -> int:
    result = _integer(value, name)
    if result < 0:
        raise ValueError(f"{name} cannot be negative")
    return result


def _timestamp(value: object, name: str) -> datetime:
    try:
        return normalize_utc_timestamp(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise type(exc)(f"{name}: {exc}") from exc


def _timestamp_text(value: datetime) -> str:
    normalized = _timestamp(value, "timestamp")
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _range(value: object, name: str) -> SMCV2TickRange:
    if type(value) is not SMCV2TickRange:
        raise TypeError(f"{name} must be an exact SMCV2TickRange")
    return SMCV2TickRange(
        _integer(value.lower_tick, f"{name}.lower_tick"),
        _integer(value.upper_tick, f"{name}.upper_tick"),
    )


def _midpoint(lower: int, upper: int) -> Decimal:
    total = lower + upper
    if total % 2 == 0:
        return Decimal(total // 2)
    sign = "-" if total < 0 else ""
    absolute = abs(total)
    return Decimal(f"{sign}{absolute // 2}.5")


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TypeError("decimal identity value must be a finite Decimal")
    if value.is_zero():
        return "0.0"
    numerator, denominator = value.as_integer_ratio()
    if denominator not in (1, 2):
        raise ValueError("decimal identity value must be an integer or half tick")
    integer = numerator * (2 // denominator)
    sign = "-" if integer < 0 else ""
    absolute = abs(integer)
    if absolute % 2 == 0:
        return f"{sign}{absolute // 2}.0"
    return f"{sign}{absolute // 2}.5"


def _hash_tuple(
    value: object, name: str, *, allow_empty: bool
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise ValueError(f"{name} cannot be empty")
    return tuple(_hash(item, f"{name} item") for item in value)


def _strict_indices(
    value: object, name: str, *, minimum: int, maximum: int
) -> tuple[int, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} length is outside locked bounds")
    result = tuple(_nonnegative_integer(item, f"{name} item") for item in value)
    if any(left >= right for left, right in zip(result, result[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return result


def _strict_timestamps(
    value: object, name: str, *, expected_length: int
) -> tuple[datetime, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    if len(value) != expected_length:
        raise ValueError(f"{name} length does not match")
    result = tuple(_timestamp(item, f"{name} item") for item in value)
    if any(left >= right for left, right in zip(result, result[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return result


def _defaults(values: dict[str, object], names: tuple[str, ...]) -> None:
    for name in names:
        expected: object = () if name == "transition_ids" else None
        if values[name] != expected:
            raise ValueError(f"{name} is forbidden for this identity kind")


__all__ = [
    "MITIGATION_BLOCK_DETECTOR_VERSION",
    "MitigationBlockState",
    "MitigationBlockObservation",
    "MitigationBlock",
    "MitigationBlockTransition",
    "MitigationBlockSnapshot",
    "MitigationBlockResult",
    "make_mitigation_block_id",
    "analyze_mitigation_blocks",
]
