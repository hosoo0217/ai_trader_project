"""Locked inline-synthetic tests for standalone Mitigation Block diagnostics."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from inspect import Parameter, signature

import pytest

from smc.dealing_range import DealingRangeEventType
from smc.mitigation_block import (
    MITIGATION_BLOCK_DETECTOR_VERSION,
    MitigationBlock,
    MitigationBlockObservation,
    MitigationBlockResult,
    MitigationBlockSnapshot,
    MitigationBlockState,
    MitigationBlockTransition,
    analyze_mitigation_blocks,
    make_mitigation_block_id,
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
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


_BASE = datetime(2026, 7, 28, tzinfo=timezone.utc)
_INSTRUMENT = "GC"
_TIMEFRAME = "M5"
_SWING_ID = "1" * 64
_EVENT_ID = "2" * 64


def _time(index: int) -> datetime:
    return _BASE + timedelta(minutes=index)


def _block(
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    *,
    source_index: int = 5,
    detection_index: int = 10,
    low_tick: int = 100,
    high_tick: int = 104,
) -> OrderBlock:
    proximal, distal = (
        (high_tick, low_tick)
        if direction is SMCV2Direction.BULLISH
        else (low_tick, high_tick)
    )
    midpoint = Decimal(low_tick + high_tick) / Decimal(2)
    values = dict(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=direction,
        source_candle_index=source_index,
        source_candle_timestamp=_time(source_index),
        source_swing_id=_SWING_ID,
        displacement_indices=(detection_index,),
        displacement_timestamps=(_time(detection_index),),
        structure_event_id=_EVENT_ID,
        structure_event_type=DealingRangeEventType.BOS,
        wick_boundaries=SMCV2TickRange(low_tick, high_tick),
        body_boundaries=SMCV2TickRange(low_tick + 1, high_tick - 1),
        proximal_tick=proximal,
        distal_tick=distal,
        midpoint_tick=midpoint,
        detection_index=detection_index,
        detection_timestamp=_time(detection_index),
    )
    return OrderBlock(
        block_id=make_order_block_id(identity_kind="BLOCK", **values),
        direction=direction,
        source_candle_index=source_index,
        source_candle_timestamp=_time(source_index),
        source_swing_id=_SWING_ID,
        displacement_indices=(detection_index,),
        displacement_timestamps=(_time(detection_index),),
        structure_event_id=_EVENT_ID,
        structure_event_type=DealingRangeEventType.BOS,
        wick_low_tick=low_tick,
        wick_high_tick=high_tick,
        body_low_tick=low_tick + 1,
        body_high_tick=high_tick - 1,
        proximal_tick=proximal,
        distal_tick=distal,
        midpoint_tick=midpoint,
        detection_index=detection_index,
        detection_timestamp=_time(detection_index),
    )


def _append_source_transition(
    block: OrderBlock,
    transitions: list[OrderBlockTransition],
    snapshots: list[OrderBlockSnapshot],
    *,
    from_state: OrderBlockState | None,
    to_state: OrderBlockState,
    index: int,
    reason: str,
) -> None:
    transition_id = make_order_block_id(
        identity_kind="TRANSITION",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=block.direction,
        block_id=block.block_id,
        from_state=from_state,
        to_state=to_state,
        effective_index=index,
        effective_timestamp=_time(index),
        reason=reason,
    )
    transition = OrderBlockTransition(
        transition_id,
        block.block_id,
        from_state,
        to_state,
        index,
        _time(index),
        reason,
    )
    transition_ids = tuple(item.transition_id for item in transitions) + (transition_id,)
    snapshot_id = make_order_block_id(
        identity_kind="SNAPSHOT",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=block.direction,
        block_id=block.block_id,
        state=to_state,
        effective_index=index,
        effective_timestamp=_time(index),
        transition_ids=transition_ids,
    )
    transitions.append(transition)
    snapshots.append(
        OrderBlockSnapshot(
            snapshot_id,
            block.block_id,
            block.direction,
            to_state,
            index,
            _time(index),
            transition_ids,
        )
    )


def _history(
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    *,
    creation_index: int | None = 12,
    creation_state: OrderBlockState = OrderBlockState.MITIGATED,
    invalidation_index: int | None = None,
) -> tuple[OrderBlock, tuple[OrderBlockTransition, ...], tuple[OrderBlockSnapshot, ...]]:
    block = _block(direction)
    transitions, snapshots = _history_for_block(
        block,
        creation_index=creation_index,
        creation_state=creation_state,
        invalidation_index=invalidation_index,
    )
    return block, transitions, snapshots


def _history_for_block(
    block: OrderBlock,
    *,
    creation_index: int | None,
    creation_state: OrderBlockState = OrderBlockState.MITIGATED,
    invalidation_index: int | None = None,
) -> tuple[tuple[OrderBlockTransition, ...], tuple[OrderBlockSnapshot, ...]]:
    transitions: list[OrderBlockTransition] = []
    snapshots: list[OrderBlockSnapshot] = []
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=None,
        to_state=OrderBlockState.DETECTED,
        index=block.detection_index,
        reason="FORMATION_CONFIRMED",
    )
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=OrderBlockState.DETECTED,
        to_state=OrderBlockState.ACTIVE,
        index=block.detection_index + 1,
        reason="FIRST_ELIGIBLE_BAR",
    )
    if creation_index is not None:
        _append_source_transition(
            block,
            transitions,
            snapshots,
            from_state=OrderBlockState.ACTIVE,
            to_state=creation_state,
            index=creation_index,
            reason=(
                "MIDPOINT_MITIGATION"
                if creation_state is OrderBlockState.MITIGATED
                else "DISTAL_TRAVERSAL"
            ),
        )
    if invalidation_index is not None:
        _append_source_transition(
            block,
            transitions,
            snapshots,
            from_state=creation_state,
            to_state=OrderBlockState.INVALIDATED,
            index=invalidation_index,
            reason="CLOSE_THROUGH_INVALIDATION",
        )
    return tuple(transitions), tuple(snapshots)


def _merge_histories(
    blocks: tuple[OrderBlock, ...],
    histories: tuple[
        tuple[tuple[OrderBlockTransition, ...], tuple[OrderBlockSnapshot, ...]], ...
    ],
) -> tuple[tuple[OrderBlockTransition, ...], tuple[OrderBlockSnapshot, ...]]:
    order = {block.block_id: position for position, block in enumerate(blocks)}
    transitions = tuple(
        sorted(
            (item for history, _ in histories for item in history),
            key=lambda item: (
                item.index,
                item.timestamp,
                order[item.block_id],
                next(
                    position
                    for history, _ in histories
                    if item in history
                    for position, candidate in enumerate(history)
                    if candidate is item
                ),
            ),
        )
    )
    snapshots = tuple(
        sorted(
            (item for _, history in histories for item in history),
            key=lambda item: (
                item.index,
                item.timestamp,
                order[item.block_id],
                len(item.transition_ids),
            ),
        )
    )
    return transitions, snapshots


def _observation(
    index: int,
    *,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    depth_tick: int = 102,
    close_tick: int | None = None,
) -> MitigationBlockObservation:
    resolved_close = depth_tick if close_tick is None else close_tick
    if direction is SMCV2Direction.BULLISH:
        return MitigationBlockObservation(
            index, _time(index), 105, depth_tick, resolved_close
        )
    return MitigationBlockObservation(
        index, _time(index), depth_tick, 99, resolved_close
    )


def _analyze(
    block: OrderBlock,
    transitions: tuple[OrderBlockTransition, ...],
    snapshots: tuple[OrderBlockSnapshot, ...],
    observations: tuple[MitigationBlockObservation, ...],
) -> MitigationBlockResult:
    return analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(block,),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        observations=observations,
    )


def _valid_result(
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
) -> MitigationBlockResult:
    block, transitions, snapshots = _history(direction)
    return _analyze(
        block,
        transitions,
        snapshots,
        (_observation(11, direction=direction, depth_tick=105 if direction is SMCV2Direction.BULLISH else 99),
         _observation(12, direction=direction)),
    )


# Logical case 1
@pytest.mark.parametrize(
    "missing",
    ["order_blocks", "order_block_transitions", "order_block_snapshots", "observations"],
)
def test_case_01_missing_top_level_is_unknown(missing: str) -> None:
    values = dict(
        instrument=" GC ",
        timeframe=" m5 ",
        order_blocks=(),
        order_block_transitions=(),
        order_block_snapshots=(),
        observations=(),
    )
    values[missing] = None
    result = analyze_mitigation_blocks(**values)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.mitigations == result.transitions == result.snapshots == ()
    invalid = analyze_mitigation_blocks(**{**values, missing: (), "instrument": " "})
    assert invalid.status is SMCV2PrimitiveStatus.INVALID


# Logical case 2
def test_case_02_complete_empty_is_none() -> None:
    result = analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(),
        order_block_transitions=(),
        order_block_snapshots=(),
        observations=(),
    )
    assert result == MitigationBlockResult(status=SMCV2PrimitiveStatus.NONE)


# Logical case 3
def test_case_03_normalization_utc_and_naive_timestamp() -> None:
    result = _valid_result()
    normalized = analyze_mitigation_blocks(
        instrument=" gc ",
        timeframe=" m5 ",
        order_blocks=(_history()[0],),
        order_block_transitions=_history()[1],
        order_block_snapshots=_history()[2],
        observations=(_observation(11, depth_tick=105), _observation(12)),
    )
    assert result == normalized
    bad = MitigationBlockObservation(11, datetime(2026, 7, 28), 105, 102, 103)
    block, transitions, snapshots = _history()
    assert _analyze(block, transitions, snapshots, (bad,)).status is SMCV2PrimitiveStatus.INVALID


# Logical cases 4-10: canonical source/history and observation contracts.
def test_case_04_source_block_malformed_fails_closed() -> None:
    block, transitions, snapshots = _history()
    malformed = object.__new__(OrderBlock)
    object.__setattr__(malformed, "block_id", block.block_id)
    result = analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(malformed,),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        observations=(),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_05_source_order_and_duplicates_are_invalid() -> None:
    first = _block(source_index=5, detection_index=10)
    second = _block(source_index=6, detection_index=20)
    for supplied in ((second, first), (first, first)):
        result = analyze_mitigation_blocks(
            instrument=_INSTRUMENT,
            timeframe=_TIMEFRAME,
            order_blocks=supplied,
            order_block_transitions=(),
            order_block_snapshots=(),
            observations=(),
        )
        assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_06_canonical_source_history_is_accepted() -> None:
    block, transitions, snapshots = _history(creation_index=None)
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105),))
    assert result.status is SMCV2PrimitiveStatus.NONE
    wrong_direction = replace(
        snapshots[-1],
        direction=SMCV2Direction.BEARISH,
    )
    result = _analyze(
        block,
        transitions,
        (*snapshots[:-1], wrong_direction),
        (_observation(11, depth_tick=105),),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_07_incomplete_history_and_prehorizon_unknown() -> None:
    block, transitions, snapshots = _history()
    assert _analyze(block, transitions, snapshots[:-1], (_observation(12),)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(block, (), (), ()).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(block, transitions, snapshots, ()).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _analyze(block, transitions, snapshots, (_observation(13),)).status is SMCV2PrimitiveStatus.UNKNOWN


def test_case_08_separate_history_tuple_order_is_causal() -> None:
    block, transitions, snapshots = _history()
    assert _analyze(block, tuple(reversed(transitions)), snapshots, (_observation(12),)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(block, transitions, tuple(reversed(snapshots)), (_observation(12),)).status is SMCV2PrimitiveStatus.INVALID
    block, transitions, snapshots = _history(invalidation_index=13)
    wrong_direction = replace(
        snapshots[-1],
        direction=SMCV2Direction.BEARISH,
    )
    result = _analyze(
        block,
        transitions,
        (*snapshots[:-1], wrong_direction),
        (
            _observation(11, depth_tick=105),
            _observation(12),
            _observation(13, depth_tick=99, close_tick=99),
        ),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert len(result.mitigations) == 1
    assert len(result.transitions) == 1
    assert len(result.snapshots) == 1


def test_case_09_observation_contract_is_fail_closed_and_frozen() -> None:
    observation = _observation(12)
    with pytest.raises(FrozenInstanceError):
        observation.close_tick = 101  # type: ignore[misc]
    block, transitions, snapshots = _history()
    bad = MitigationBlockObservation(12, _time(12), 101, 102, 102)
    assert _analyze(block, transitions, snapshots, (bad,)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "observations",
    [
        [_observation(12)],
        (_observation(12), _observation(12)),
        (_observation(13), _observation(12)),
    ],
)
def test_case_10_observation_container_and_chronology(observations: object) -> None:
    block, transitions, snapshots = _history()
    result = analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(block,),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        observations=observations,  # type: ignore[arg-type]
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


# Logical cases 11-18: creation and exact geometry.
def test_case_11_bullish_midpoint_creation() -> None:
    result = _valid_result(SMCV2Direction.BULLISH)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.mitigations) == 1
    assert result.mitigations[0].direction is SMCV2Direction.BULLISH


def test_case_12_bearish_midpoint_creation() -> None:
    result = _valid_result(SMCV2Direction.BEARISH)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.mitigations) == 1
    assert result.mitigations[0].direction is SMCV2Direction.BEARISH


def test_case_13_eligible_and_terminal_source_states() -> None:
    valid = _valid_result()
    assert valid.status is SMCV2PrimitiveStatus.VALID
    block, transitions, snapshots = _history()
    later = _analyze(block, transitions, snapshots, (_observation(13),))
    assert later.status is SMCV2PrimitiveStatus.UNKNOWN


def test_case_14_same_group_activation_then_creation() -> None:
    block = _block()
    transitions: list[OrderBlockTransition] = []
    snapshots: list[OrderBlockSnapshot] = []
    _append_source_transition(block, transitions, snapshots, from_state=None, to_state=OrderBlockState.DETECTED, index=10, reason="FORMATION_CONFIRMED")
    _append_source_transition(block, transitions, snapshots, from_state=OrderBlockState.DETECTED, to_state=OrderBlockState.ACTIVE, index=11, reason="FIRST_ELIGIBLE_BAR")
    _append_source_transition(block, transitions, snapshots, from_state=OrderBlockState.ACTIVE, to_state=OrderBlockState.MITIGATED, index=11, reason="MIDPOINT_MITIGATION")
    result = _analyze(block, tuple(transitions), tuple(snapshots), (_observation(11),))
    assert result.status is SMCV2PrimitiveStatus.VALID
    detection = _analyze(block, tuple(transitions), tuple(snapshots), (_observation(10),))
    assert detection.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("state", [OrderBlockState.MITIGATED, OrderBlockState.FULLY_TRAVERSED])
def test_case_15_midpoint_and_traversal_source_transitions_qualify(state: OrderBlockState) -> None:
    block, transitions, snapshots = _history(creation_state=state)
    depth = 99 if state is OrderBlockState.FULLY_TRAVERSED else 102
    close = 100 if state is OrderBlockState.FULLY_TRAVERSED else 102
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12, depth_tick=depth, close_tick=close)))
    assert result.status is SMCV2PrimitiveStatus.VALID


@pytest.mark.parametrize(
    ("low", "high"),
    [(100, 104), (100, 105)],
)
def test_case_16_integer_and_half_tick_midpoint_equality(low: int, high: int) -> None:
    block = _block(low_tick=low, high_tick=high)
    midpoint = block.midpoint_tick
    assert midpoint in (Decimal("102"), Decimal("102.5"))


def test_case_17_arbitrary_magnitude_decimal_context_independence() -> None:
    huge = 10**80
    geometry = dict(
        midpoint_tick=Decimal(f"{huge}.5"),
        wick_boundaries=SMCV2TickRange(huge, huge + 1),
        body_boundaries=SMCV2TickRange(huge, huge + 1),
        proximal_tick=huge + 1,
        distal_tick=huge,
        deepest_penetration_tick=huge,
        close_tick=huge,
    )
    with localcontext() as context:
        context.prec = 3
        first = make_mitigation_block_id(**_mitigation_kwargs(**geometry))
    with localcontext() as context:
        context.prec = 80
        second = make_mitigation_block_id(**_mitigation_kwargs(**geometry))
    assert first == second


def test_case_18_directional_depth_close_geometry() -> None:
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(**_mitigation_kwargs(close_tick=99))
    bearish = _mitigation_kwargs(
        direction=SMCV2Direction.BEARISH,
        proximal_tick=100,
        distal_tick=104,
        deepest_penetration_tick=103,
        close_tick=104,
    )
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(**bearish)


# Logical cases 19-34: qualification, lifecycle, atomicity, precedence.
def test_case_19_proximal_touch_is_not_creation() -> None:
    block, transitions_tuple, snapshots_tuple = _history(creation_index=None)
    transitions = list(transitions_tuple)
    snapshots = list(snapshots_tuple)
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=OrderBlockState.ACTIVE,
        to_state=OrderBlockState.TOUCHED,
        index=11,
        reason="WICK_TOUCHED",
    )
    assert _analyze(block, tuple(transitions), tuple(snapshots), (_observation(11, depth_tick=104, close_tick=104),)).status is SMCV2PrimitiveStatus.NONE


def test_case_20_partial_then_midpoint_can_create() -> None:
    block, transitions_tuple, snapshots_tuple = _history(creation_index=None)
    transitions = list(transitions_tuple)
    snapshots = list(snapshots_tuple)
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=OrderBlockState.ACTIVE,
        to_state=OrderBlockState.PARTIALLY_MITIGATED,
        index=11,
        reason="PARTIAL_MITIGATION",
    )
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=OrderBlockState.PARTIALLY_MITIGATED,
        to_state=OrderBlockState.MITIGATED,
        index=12,
        reason="MIDPOINT_MITIGATION",
    )
    result = _analyze(
        block,
        tuple(transitions),
        tuple(snapshots),
        (_observation(11, depth_tick=103), _observation(12)),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID


def test_case_21_outside_zone_is_none() -> None:
    block, transitions, snapshots = _history(creation_index=None)
    assert _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105, close_tick=105),)).status is SMCV2PrimitiveStatus.NONE


def test_case_22_in_horizon_reconciliation_is_required() -> None:
    block, transitions, snapshots = _history(creation_index=None)
    assert _analyze(block, transitions, snapshots, (_observation(12),)).status is SMCV2PrimitiveStatus.INVALID


def test_case_23_creation_binds_exact_source_ids() -> None:
    result = _valid_result()
    mitigation = result.mitigations[0]
    assert mitigation.source_order_block_id
    assert mitigation.source_order_block_transition_id
    assert mitigation.source_order_block_snapshot_id


@pytest.mark.parametrize("direction", [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH])
def test_case_24_same_candle_close_through_prevents_creation(direction: SMCV2Direction) -> None:
    block, transitions_tuple, snapshots_tuple = _history(direction, creation_index=None)
    transitions = list(transitions_tuple)
    snapshots = list(snapshots_tuple)
    _append_source_transition(
        block,
        transitions,
        snapshots,
        from_state=OrderBlockState.ACTIVE,
        to_state=OrderBlockState.INVALIDATED,
        index=12,
        reason="CLOSE_THROUGH_INVALIDATION",
    )
    close = 99 if direction is SMCV2Direction.BULLISH else 105
    result = _analyze(block, tuple(transitions), tuple(snapshots), (_observation(11, direction=direction, depth_tick=105 if direction is SMCV2Direction.BULLISH else 99), _observation(12, direction=direction, depth_tick=99 if direction is SMCV2Direction.BULLISH else 105, close_tick=close)))
    assert result.status is SMCV2PrimitiveStatus.NONE


def test_case_25_close_at_distal_can_qualify() -> None:
    block, transitions, snapshots = _history(
        creation_state=OrderBlockState.FULLY_TRAVERSED
    )
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12, depth_tick=100, close_tick=100)))
    assert result.status is SMCV2PrimitiveStatus.VALID


def test_case_26_wick_beyond_distal_without_close_through_qualifies() -> None:
    block, transitions, snapshots = _history(creation_state=OrderBlockState.FULLY_TRAVERSED)
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12, depth_tick=99, close_tick=100)))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.snapshots[-1].state is MitigationBlockState.MITIGATED


def test_case_27_immutable_fields_preserve_source_geometry() -> None:
    result = _valid_result()
    mitigation = result.mitigations[0]
    assert (mitigation.wick_low_tick, mitigation.wick_high_tick) == (100, 104)
    assert (mitigation.body_low_tick, mitigation.body_high_tick) == (101, 103)
    assert mitigation.midpoint_tick == Decimal(102)
    assert mitigation.midpoint_reached is True


def test_case_28_creation_lifecycle_is_exact() -> None:
    result = _valid_result()
    transition = result.transitions[0]
    assert (transition.from_state, transition.to_state, transition.reason) == (
        None,
        MitigationBlockState.MITIGATED,
        "FIRST_QUALIFYING_MIDPOINT_RETEST",
    )
    assert result.snapshots[0].transition_ids == (transition.transition_id,)


def test_case_29_later_close_through_invalidates() -> None:
    block, transitions, snapshots = _history(invalidation_index=13)
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12), _observation(13, depth_tick=99, close_tick=99)))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.snapshots[-1].state is MitigationBlockState.INVALIDATED
    assert result.transitions[-1].reason == "SOURCE_CLOSE_THROUGH_INVALIDATION"


def test_case_30_existing_invalidation_precedes_new_creation() -> None:
    first = _block(source_index=5, detection_index=10)
    second = _block(
        SMCV2Direction.BEARISH,
        source_index=15,
        detection_index=18,
        low_tick=200,
        high_tick=204,
    )
    first_history = _history_for_block(
        first, creation_index=12, invalidation_index=20
    )
    second_history = _history_for_block(
        second,
        creation_index=20,
        creation_state=OrderBlockState.FULLY_TRAVERSED,
    )
    transitions, snapshots = _merge_histories(
        (first, second), (first_history, second_history)
    )
    result = analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(first, second),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        observations=(
            _observation(11, depth_tick=105),
            _observation(12),
            _observation(19, depth_tick=105),
            MitigationBlockObservation(20, _time(20), 205, 99, 99),
        ),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.transitions[-2].to_state is MitigationBlockState.INVALIDATED
    assert result.transitions[-1].from_state is None
    assert result.transitions[-1].to_state is MitigationBlockState.MITIGATED


def test_case_31_invalidated_is_terminal_without_revision() -> None:
    block, transitions, snapshots = _history(invalidation_index=13)
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12), _observation(13, depth_tick=99, close_tick=99), _observation(14, depth_tick=102)))
    assert len(result.mitigations) == 1
    assert len(result.transitions) == 2


def test_case_32_multiple_sources_are_deterministic() -> None:
    first_block = _block(source_index=4, detection_index=10)
    second_block = _block(
        SMCV2Direction.BEARISH, source_index=5, detection_index=10
    )
    first_history = _history_for_block(first_block, creation_index=12)
    second_history = _history_for_block(
        second_block,
        creation_index=12,
        creation_state=OrderBlockState.FULLY_TRAVERSED,
    )
    transitions, snapshots = _merge_histories(
        (first_block, second_block), (first_history, second_history)
    )
    kwargs = dict(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(first_block, second_block),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        observations=(_observation(12),),
    )
    first = analyze_mitigation_blocks(**kwargs)
    assert first == analyze_mitigation_blocks(**kwargs)
    assert first.status is SMCV2PrimitiveStatus.VALID
    assert len(first.mitigations) == 2
    assert tuple(item.source_order_block_id for item in first.mitigations) == (
        first_block.block_id,
        second_block.block_id,
    )


def test_case_33_later_invalid_preserves_prior_evidence() -> None:
    block, transitions, snapshots = _history()
    malformed = object.__new__(MitigationBlockObservation)
    object.__setattr__(malformed, "index", 13)
    object.__setattr__(malformed, "timestamp", _time(13))
    result = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12), malformed))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert len(result.mitigations) == 1

    block, transitions, snapshots = _history(invalidation_index=13)
    bad_transition = replace(transitions[-1], transition_id="0" * 64)
    transition_result = _analyze(
        block,
        (*transitions[:-1], bad_transition),
        snapshots,
        (
            _observation(11, depth_tick=105),
            _observation(12),
            _observation(13, depth_tick=99, close_tick=99),
        ),
    )
    assert transition_result.status is SMCV2PrimitiveStatus.INVALID
    assert len(transition_result.mitigations) == 1

    bad_snapshot = replace(snapshots[-1], snapshot_id="0" * 64)
    snapshot_result = _analyze(
        block,
        transitions,
        (*snapshots[:-1], bad_snapshot),
        (
            _observation(11, depth_tick=105),
            _observation(12),
            _observation(13, depth_tick=99, close_tick=99),
        ),
    )
    assert snapshot_result.status is SMCV2PrimitiveStatus.INVALID
    assert len(snapshot_result.mitigations) == 1


def test_case_34_invalid_precedence_and_no_ambiguous_branch() -> None:
    result = _valid_result()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.status is not SMCV2PrimitiveStatus.AMBIGUOUS

    block, transitions, snapshots = _history(invalidation_index=14)
    invalid_later_group = _analyze(
        block,
        transitions,
        snapshots,
        (
            _observation(13, depth_tick=105),
            _observation(14, depth_tick=105),
        ),
    )
    assert invalid_later_group.status is SMCV2PrimitiveStatus.INVALID
    assert invalid_later_group.mitigations == ()
    assert invalid_later_group.transitions == ()
    assert invalid_later_group.snapshots == ()

    unknown_block = _block(source_index=4, detection_index=10)
    prior_valid_block = _block(source_index=5, detection_index=10)
    unknown_history = _history_for_block(
        unknown_block,
        creation_index=12,
        invalidation_index=14,
    )
    prior_valid_history = _history_for_block(
        prior_valid_block,
        creation_index=13,
    )
    combined_transitions, combined_snapshots = _merge_histories(
        (unknown_block, prior_valid_block),
        (unknown_history, prior_valid_history),
    )
    preserved_prior = analyze_mitigation_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(unknown_block, prior_valid_block),
        order_block_transitions=combined_transitions,
        order_block_snapshots=combined_snapshots,
        observations=(
            _observation(13),
            _observation(14, depth_tick=105),
        ),
    )
    assert preserved_prior.status is SMCV2PrimitiveStatus.INVALID
    assert len(preserved_prior.mitigations) == 1
    assert len(preserved_prior.transitions) == 1
    assert len(preserved_prior.snapshots) == 1
    assert (
        preserved_prior.mitigations[0].source_order_block_id
        == prior_valid_block.block_id
    )

    valid_later_group = _analyze(
        block,
        transitions,
        snapshots,
        (
            _observation(13, depth_tick=105),
            _observation(14, depth_tick=99, close_tick=99),
        ),
    )
    assert valid_later_group.status is SMCV2PrimitiveStatus.UNKNOWN
    assert valid_later_group.mitigations == ()
    assert valid_later_group.transitions == ()
    assert valid_later_group.snapshots == ()


# Logical cases 35-38: exhaustive identity and public surface.
def _mitigation_kwargs(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = dict(
        identity_kind="MITIGATION",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_order_block_id="3" * 64,
        source_order_block_snapshot_id="4" * 64,
        source_order_block_transition_id="5" * 64,
        wick_boundaries=SMCV2TickRange(100, 104),
        body_boundaries=SMCV2TickRange(101, 103),
        proximal_tick=104,
        distal_tick=100,
        midpoint_tick=Decimal(102),
        first_retouch_index=12,
        first_retouch_timestamp=_time(12),
        deepest_penetration_tick=102,
        close_tick=102,
        midpoint_reached=True,
    )
    values.update(overrides)
    return values


def test_case_35_mitigation_identity_schema_and_sensitivity() -> None:
    base = make_mitigation_block_id(**_mitigation_kwargs())
    assert base == make_mitigation_block_id(**_mitigation_kwargs(instrument=" gc "))
    assert base == make_mitigation_block_id(
        **_mitigation_kwargs(
            first_retouch_timestamp=_time(12).astimezone(
                timezone(timedelta(hours=9))
            )
        )
    )
    assert base != make_mitigation_block_id(**_mitigation_kwargs(close_tick=103))
    zero_kwargs = _mitigation_kwargs(
        wick_boundaries=SMCV2TickRange(-1, 1),
        body_boundaries=SMCV2TickRange(-1, 1),
        proximal_tick=1,
        distal_tick=-1,
        midpoint_tick=Decimal("0"),
        deepest_penetration_tick=0,
        close_tick=0,
    )
    zero = make_mitigation_block_id(**zero_kwargs)
    for representation in (
        Decimal("-0"),
        Decimal("0.0"),
        Decimal("-0.0"),
    ):
        assert zero == make_mitigation_block_id(
            **{**zero_kwargs, "midpoint_tick": representation}
        )
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(
            **_mitigation_kwargs(
                deepest_penetration_tick=99,
                close_tick=99,
            )
        )
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(
            **_mitigation_kwargs(
                direction=SMCV2Direction.BEARISH,
                proximal_tick=100,
                distal_tick=104,
                deepest_penetration_tick=105,
                close_tick=105,
            )
        )
    bullish_distal = make_mitigation_block_id(
        **_mitigation_kwargs(
            deepest_penetration_tick=99,
            close_tick=100,
        )
    )
    bearish_distal = make_mitigation_block_id(
        **_mitigation_kwargs(
            direction=SMCV2Direction.BEARISH,
            proximal_tick=100,
            distal_tick=104,
            deepest_penetration_tick=105,
            close_tick=104,
        )
    )
    assert bullish_distal != bearish_distal
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(**_mitigation_kwargs(midpoint_reached=False))
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(**_mitigation_kwargs(state=MitigationBlockState.MITIGATED))


def test_case_36_transition_identity_schema_and_edges() -> None:
    mitigation_id = make_mitigation_block_id(**_mitigation_kwargs())
    transition_id = make_mitigation_block_id(
        identity_kind="TRANSITION",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_order_block_id="3" * 64,
        source_order_block_snapshot_id="4" * 64,
        source_order_block_transition_id="5" * 64,
        mitigation_id=mitigation_id,
        from_state=None,
        to_state=MitigationBlockState.MITIGATED,
        effective_index=12,
        effective_timestamp=_time(12),
        reason="FIRST_QUALIFYING_MIDPOINT_RETEST",
    )
    assert len(transition_id) == 64
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(
            identity_kind="TRANSITION",
            instrument=_INSTRUMENT,
            timeframe=_TIMEFRAME,
            direction=SMCV2Direction.BULLISH,
            source_order_block_id="3" * 64,
            source_order_block_snapshot_id="4" * 64,
            source_order_block_transition_id="5" * 64,
            mitigation_id=mitigation_id,
            from_state=None,
            to_state=MitigationBlockState.INVALIDATED,
            effective_index=12,
            effective_timestamp=_time(12),
            reason="SOURCE_CLOSE_THROUGH_INVALIDATION",
        )


def test_case_37_snapshot_identity_schema() -> None:
    result = _valid_result()
    snapshot = result.snapshots[0]
    assert len(snapshot.snapshot_id) == 64
    with pytest.raises((TypeError, ValueError)):
        make_mitigation_block_id(
            identity_kind="SNAPSHOT",
            instrument=_INSTRUMENT,
            timeframe=_TIMEFRAME,
            direction=snapshot.direction,
            source_order_block_id=snapshot.source_order_block_id,
            source_order_block_snapshot_id=snapshot.source_order_block_snapshot_id,
            source_order_block_transition_id=snapshot.source_order_block_transition_id,
            mitigation_id=snapshot.mitigation_id,
            state=snapshot.state,
            effective_index=snapshot.index,
            effective_timestamp=snapshot.timestamp,
            transition_ids=(),
        )


def test_case_38_exact_public_surface_signatures_and_frozen_types() -> None:
    import smc.mitigation_block as module

    assert MITIGATION_BLOCK_DETECTOR_VERSION == "SMC-V2-MITIGATION-BLOCK-1"
    assert tuple(MitigationBlockState) == (
        MitigationBlockState.MITIGATED,
        MitigationBlockState.INVALIDATED,
    )
    assert tuple(signature(analyze_mitigation_blocks).parameters) == (
        "instrument",
        "timeframe",
        "order_blocks",
        "order_block_transitions",
        "order_block_snapshots",
        "observations",
    )
    assert tuple(signature(make_mitigation_block_id).parameters) == (
        "identity_kind", "instrument", "timeframe", "direction",
        "source_order_block_id", "source_order_block_snapshot_id",
        "source_order_block_transition_id", "wick_boundaries", "body_boundaries",
        "proximal_tick", "distal_tick", "midpoint_tick", "first_retouch_index",
        "first_retouch_timestamp", "deepest_penetration_tick", "close_tick",
        "midpoint_reached", "mitigation_id", "from_state", "to_state",
        "effective_index", "effective_timestamp", "reason", "state",
        "transition_ids",
    )
    assert tuple(field.name for field in fields(MitigationBlockObservation)) == (
        "index", "timestamp", "high_tick", "low_tick", "close_tick",
    )
    assert tuple(field.name for field in fields(MitigationBlock)) == (
        "mitigation_id", "direction", "source_order_block_id",
        "source_order_block_snapshot_id", "source_order_block_transition_id",
        "wick_low_tick", "wick_high_tick", "body_low_tick", "body_high_tick",
        "proximal_tick", "distal_tick", "midpoint_tick", "first_retouch_index",
        "first_retouch_timestamp", "deepest_penetration_tick", "close_tick",
        "midpoint_reached",
    )
    assert tuple(field.name for field in fields(MitigationBlockTransition)) == (
        "transition_id", "mitigation_id", "source_order_block_id",
        "source_order_block_snapshot_id", "source_order_block_transition_id",
        "from_state", "to_state", "index", "timestamp", "reason",
    )
    assert tuple(field.name for field in fields(MitigationBlockSnapshot)) == (
        "snapshot_id", "mitigation_id", "source_order_block_id",
        "source_order_block_snapshot_id", "source_order_block_transition_id",
        "direction", "state", "index", "timestamp", "transition_ids",
    )
    assert tuple(field.name for field in fields(MitigationBlockResult)) == (
        "status", "mitigations", "transitions", "snapshots", "reasons",
        "blocking_reasons",
    )
    for model in (
        MitigationBlockObservation,
        MitigationBlock,
        MitigationBlockTransition,
        MitigationBlockSnapshot,
        MitigationBlockResult,
    ):
        assert model.__dataclass_params__.frozen is True
    for function in (analyze_mitigation_blocks, make_mitigation_block_id):
        assert all(
            parameter.kind is Parameter.KEYWORD_ONLY
            for parameter in signature(function).parameters.values()
        )
    assert module.__all__ == [
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


def test_case_39_repeatability_and_prefix_invariance() -> None:
    result = _valid_result()
    assert result == _valid_result()
    block, transitions, snapshots = _history(invalidation_index=13)
    extended = _analyze(block, transitions, snapshots, (_observation(11, depth_tick=105), _observation(12), _observation(13, depth_tick=99, close_tick=99)))
    assert extended.mitigations == result.mitigations
    assert extended.transitions[:1] == result.transitions
    assert extended.snapshots[:1] == result.snapshots


def test_case_40_standalone_module_surface() -> None:
    import ast
    import smc.mitigation_block as module

    source = open(module.__file__, encoding="utf-8").read()
    imports = {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }
    for forbidden in ("pandas", "requests", "broker", "strategy", "risk", "execution"):
        assert all(forbidden not in imported for imported in imports)
