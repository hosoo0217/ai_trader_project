"""Locked inline-synthetic tests for standalone Breaker Block diagnostics."""

from __future__ import annotations

import ast
from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from inspect import Parameter, signature
from pathlib import Path
from typing import get_type_hints

import pytest

import smc.breaker_block as breaker_module
from smc.breaker_block import (
    BREAKER_BLOCK_DETECTOR_VERSION,
    BreakerBlock,
    BreakerBlockObservation,
    BreakerBlockResult,
    BreakerBlockSnapshot,
    BreakerBlockState,
    BreakerBlockTransition,
    analyze_breaker_blocks,
    make_breaker_block_id,
)
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
)


_BASE = datetime(2026, 7, 28, tzinfo=timezone.utc)
_INSTRUMENT = "GC"
_TIMEFRAME = "M5"


def _time(index: int) -> datetime:
    return _BASE + timedelta(minutes=5 * index)


def _obs(
    index: int,
    *,
    high: int = 106,
    low: int = 105,
    close: int = 105,
    timestamp: datetime | None = None,
) -> BreakerBlockObservation:
    return BreakerBlockObservation(
        index,
        _time(index) if timestamp is None else timestamp,
        high,
        low,
        close,
    )


def _swing(
    side: DealingRangeSwingSide,
    *,
    source_index: int,
    confirmation_index: int,
    price_tick: int,
    swing_id: str,
) -> DealingRangeSwing:
    return DealingRangeSwing(
        side=side,
        price_tick=price_tick,
        provenance=SMCV2EventProvenance(
            source_indices=(source_index,),
            source_timestamps=(_time(source_index),),
            confirmation_index=confirmation_index,
            confirmation_timestamp=_time(confirmation_index),
        ),
        swing_id=swing_id,
    )


def _event(
    swing: DealingRangeSwing,
    direction: SMCV2Direction,
    *,
    confirmation_index: int,
    event_type: DealingRangeEventType = DealingRangeEventType.BOS,
) -> DealingRangeStructureEvent:
    provenance = SMCV2EventProvenance(
        source_indices=(confirmation_index,),
        source_timestamps=(_time(confirmation_index),),
        confirmation_index=confirmation_index,
        confirmation_timestamp=_time(confirmation_index),
    )
    event_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=direction,
        source_indices=(confirmation_index,),
        event_type=event_type,
        broken_swing_id=swing.swing_id,
        confirmation_index=confirmation_index,
        boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick),
    )
    return DealingRangeStructureEvent(
        direction,
        event_type,
        swing.swing_id,
        provenance,
        event_id,
    )


def _source_block(
    direction: SMCV2Direction,
    swing: DealingRangeSwing,
    event: DealingRangeStructureEvent,
    *,
    shift: int = 0,
) -> OrderBlock:
    source_index = 5 + shift
    detection_index = 10 + shift
    proximal, distal = (
        (104, 100)
        if direction is SMCV2Direction.BULLISH
        else (100, 104)
    )
    midpoint = Decimal("102")
    values = dict(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=direction,
        source_candle_index=source_index,
        source_candle_timestamp=_time(source_index),
        source_swing_id=swing.swing_id,
        displacement_indices=(detection_index,),
        displacement_timestamps=(_time(detection_index),),
        structure_event_id=event.event_id,
        structure_event_type=event.event_type,
        wick_boundaries=SMCV2TickRange(100, 104),
        body_boundaries=SMCV2TickRange(101, 103),
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
        source_swing_id=swing.swing_id,
        displacement_indices=(detection_index,),
        displacement_timestamps=(_time(detection_index),),
        structure_event_id=event.event_id,
        structure_event_type=event.event_type,
        wick_low_tick=100,
        wick_high_tick=104,
        body_low_tick=101,
        body_high_tick=103,
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
    transition_ids = tuple(item.transition_id for item in transitions) + (
        transition_id,
    )
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
    block: OrderBlock,
    *,
    invalidation_index: int | None,
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
    if invalidation_index is not None:
        _append_source_transition(
            block,
            transitions,
            snapshots,
            from_state=OrderBlockState.ACTIVE,
            to_state=OrderBlockState.INVALIDATED,
            index=invalidation_index,
            reason="CLOSE_THROUGH_INVALIDATION",
        )
    return tuple(transitions), tuple(snapshots)


def _event_key(event: DealingRangeStructureEvent) -> tuple[object, ...]:
    return (
        event.provenance.confirmation_index,
        event.provenance.confirmation_timestamp,
        event.direction.value,
        event.event_type.value,
        event.event_id,
    )


def _swing_key(swing: DealingRangeSwing) -> tuple[object, ...]:
    return (
        swing.provenance.confirmation_index,
        swing.provenance.source_indices[0],
        swing.side.value,
        swing.swing_id,
    )


def _bundle(
    source_direction: SMCV2Direction = SMCV2Direction.BULLISH,
    *,
    confirmation_offset: int = 2,
    include_candidate: bool = True,
    complete_window: bool = False,
    event_type: DealingRangeEventType = DealingRangeEventType.BOS,
    shift: int = 0,
    source_char: str = "a",
    candidate_char: str = "b",
) -> dict[str, object]:
    detection_index = 10 + shift
    invalidation_index = 20 + shift
    confirmation_index = invalidation_index + confirmation_offset
    source_side = (
        DealingRangeSwingSide.HIGH
        if source_direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.LOW
    )
    source_price = 110 if source_side is DealingRangeSwingSide.HIGH else 90
    source_swing = _swing(
        source_side,
        source_index=2 + shift,
        confirmation_index=4 + shift,
        price_tick=source_price,
        swing_id=source_char * 64,
    )
    source_event = _event(
        source_swing,
        source_direction,
        confirmation_index=detection_index,
    )
    block = _source_block(
        source_direction,
        source_swing,
        source_event,
        shift=shift,
    )
    transitions, snapshots = _history(
        block,
        invalidation_index=invalidation_index,
    )
    proposed = (
        SMCV2Direction.BEARISH
        if source_direction is SMCV2Direction.BULLISH
        else SMCV2Direction.BULLISH
    )
    candidate_side = (
        DealingRangeSwingSide.LOW
        if proposed is SMCV2Direction.BEARISH
        else DealingRangeSwingSide.HIGH
    )
    candidate_price = 90 if candidate_side is DealingRangeSwingSide.LOW else 110
    candidate_swing = _swing(
        candidate_side,
        source_index=12 + shift,
        confirmation_index=14 + shift,
        price_tick=candidate_price,
        swing_id=candidate_char * 64,
    )
    events = [source_event]
    if include_candidate:
        events.append(
            _event(
                candidate_swing,
                proposed,
                confirmation_index=confirmation_index,
                event_type=event_type,
            )
        )
    observations = {
        2 + shift: _obs(
            2 + shift,
            high=110 if source_side is DealingRangeSwingSide.HIGH else 95,
            low=90 if source_side is DealingRangeSwingSide.LOW else 105,
            close=94 if source_side is DealingRangeSwingSide.LOW else 108,
        ),
        4 + shift: _obs(4 + shift),
        5 + shift: _obs(5 + shift, high=104, low=100, close=102),
        detection_index: (
            _obs(detection_index, high=112, low=107, close=111)
            if source_direction is SMCV2Direction.BULLISH
            else _obs(detection_index, high=93, low=88, close=89)
        ),
        11 + shift: (
            _obs(11 + shift, high=106, low=105, close=105)
            if source_direction is SMCV2Direction.BULLISH
            else _obs(11 + shift, high=99, low=98, close=99)
        ),
        12 + shift: (
            _obs(12 + shift, high=105, low=90, close=101)
            if candidate_side is DealingRangeSwingSide.LOW
            else _obs(12 + shift, high=110, low=100, close=103)
        ),
        14 + shift: (
            _obs(14 + shift)
            if source_direction is SMCV2Direction.BULLISH
            else _obs(14 + shift, high=104, low=102, close=103)
        ),
        invalidation_index: (
            _obs(invalidation_index, high=105, low=98, close=99)
            if source_direction is SMCV2Direction.BULLISH
            else _obs(invalidation_index, high=106, low=100, close=105)
        ),
    }
    last_offset = 10 if complete_window else max(confirmation_offset, 0)
    for offset in range(1, last_offset + 1):
        index = invalidation_index + offset
        observations[index] = _obs(index)
    if include_candidate:
        observations[confirmation_index] = (
            _obs(confirmation_index, high=95, low=88, close=89)
            if proposed is SMCV2Direction.BEARISH
            else _obs(confirmation_index, high=112, low=105, close=111)
        )
    return dict(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(block,),
        order_block_transitions=transitions,
        order_block_snapshots=snapshots,
        swings=tuple(sorted((source_swing, candidate_swing), key=_swing_key)),
        structure_events=tuple(sorted(events, key=_event_key)),
        observations=tuple(observations[index] for index in sorted(observations)),
    )


def _analyze(values: dict[str, object]) -> BreakerBlockResult:
    return analyze_breaker_blocks(**values)  # type: ignore[arg-type]


def _valid(
    source_direction: SMCV2Direction = SMCV2Direction.BULLISH,
) -> BreakerBlockResult:
    return _analyze(_bundle(source_direction))


def _retest(
    index: int,
    direction: SMCV2Direction,
    state: BreakerBlockState,
) -> BreakerBlockObservation:
    if direction is SMCV2Direction.BULLISH:
        values = {
            BreakerBlockState.TOUCHED: (106, 104, 105),
            BreakerBlockState.PARTIALLY_MITIGATED: (106, 103, 104),
            BreakerBlockState.MITIGATED: (106, 102, 103),
            BreakerBlockState.INVALIDATED: (105, 98, 99),
        }[state]
    else:
        values = {
            BreakerBlockState.TOUCHED: (100, 98, 99),
            BreakerBlockState.PARTIALLY_MITIGATED: (101, 98, 100),
            BreakerBlockState.MITIGATED: (102, 98, 101),
            BreakerBlockState.INVALIDATED: (106, 100, 105),
        }[state]
    high, low, close = values
    return _obs(index, high=high, low=low, close=close)


def _with_observations(
    values: dict[str, object],
    *observations: BreakerBlockObservation,
) -> dict[str, object]:
    existing = values["observations"]
    assert isinstance(existing, tuple)
    return {**values, "observations": (*existing, *observations)}


def _merge_bundles(
    first: dict[str, object],
    second: dict[str, object],
) -> dict[str, object]:
    return dict(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=first["order_blocks"] + second["order_blocks"],  # type: ignore[operator]
        order_block_transitions=first["order_block_transitions"] + second["order_block_transitions"],  # type: ignore[operator]
        order_block_snapshots=first["order_block_snapshots"] + second["order_block_snapshots"],  # type: ignore[operator]
        swings=tuple(sorted(first["swings"] + second["swings"], key=_swing_key)),  # type: ignore[operator]
        structure_events=tuple(
            sorted(
                first["structure_events"] + second["structure_events"],  # type: ignore[operator]
                key=_event_key,
            )
        ),
        observations=first["observations"] + second["observations"],  # type: ignore[operator]
    )


# Logical case 1
@pytest.mark.parametrize(
    "missing",
    (
        "order_blocks",
        "order_block_transitions",
        "order_block_snapshots",
        "swings",
        "structure_events",
        "observations",
    ),
)
def test_case_01_missing_top_level_is_unknown(missing: str) -> None:
    values = _bundle()
    values[missing] = None
    result = _analyze(values)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.breakers == result.transitions == result.snapshots == ()
    values["instrument"] = " "
    assert _analyze(values).status is SMCV2PrimitiveStatus.INVALID


# Logical case 2
def test_case_02_complete_empty_is_none() -> None:
    result = analyze_breaker_blocks(
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        order_blocks=(),
        order_block_transitions=(),
        order_block_snapshots=(),
        swings=(),
        structure_events=(),
        observations=(),
    )
    assert result == BreakerBlockResult(SMCV2PrimitiveStatus.NONE)


# Logical case 3
def test_case_03_normalization_and_utc_are_deterministic() -> None:
    values = _bundle()
    assert _analyze(values) == _analyze(
        {**values, "instrument": " gc ", "timeframe": " m5 "}
    )
    observations = values["observations"]
    assert isinstance(observations, tuple)
    bad = replace(observations[-1], timestamp=datetime(2026, 7, 28))
    assert _analyze({**values, "observations": (*observations[:-1], bad)}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 4
def test_case_04_observation_contract_and_frozen_state() -> None:
    with pytest.raises(FrozenInstanceError):
        _obs(1).close_tick = 1  # type: ignore[misc]
    values = _bundle()
    observations = values["observations"]
    assert isinstance(observations, tuple)
    for bad in (
        replace(observations[-1], index=True),
        replace(observations[-1], close_tick=200),
        object.__new__(BreakerBlockObservation),
    ):
        assert _analyze({**values, "observations": (*observations[:-1], bad)}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 5
def test_case_05_observation_chronology_is_not_sorted() -> None:
    values = _bundle()
    observations = values["observations"]
    assert isinstance(observations, tuple)
    assert _analyze({**values, "observations": tuple(reversed(observations))}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "observations": list(observations)}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 6
def test_case_06_source_block_identity_is_canonical() -> None:
    values = _bundle()
    assert _analyze(values).status is SMCV2PrimitiveStatus.VALID
    blocks = values["order_blocks"]
    swings = values["swings"]
    events = values["structure_events"]
    assert isinstance(blocks, tuple)
    assert isinstance(swings, tuple) and isinstance(events, tuple)
    malformed = object.__new__(OrderBlock)
    object.__setattr__(malformed, "block_id", blocks[0].block_id)
    assert _analyze({**values, "order_blocks": (malformed,)}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "swings": swings[1:]}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "structure_events": events[1:]}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 7
def test_case_07_source_block_order_and_duplicates_are_invalid() -> None:
    first = _bundle()
    second = _bundle(shift=40, source_char="c", candidate_char="d")
    blocks = (first["order_blocks"][0], second["order_blocks"][0])  # type: ignore[index]
    assert _analyze({**first, "order_blocks": tuple(reversed(blocks))}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**first, "order_blocks": (blocks[0], blocks[0])}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 8
def test_case_08_complete_source_history_and_prefix_are_exact() -> None:
    values = _bundle()
    transitions = values["order_block_transitions"]
    snapshots = values["order_block_snapshots"]
    assert isinstance(transitions, tuple) and isinstance(snapshots, tuple)
    assert _analyze({**values, "order_block_snapshots": snapshots[:-1]}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "order_block_transitions": transitions[:-1]}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 9
def test_case_09_separate_history_streams_follow_causal_order() -> None:
    values = _bundle()
    transitions = values["order_block_transitions"]
    snapshots = values["order_block_snapshots"]
    assert isinstance(transitions, tuple) and isinstance(snapshots, tuple)
    assert _analyze({**values, "order_block_transitions": tuple(reversed(transitions))}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "order_block_snapshots": tuple(reversed(snapshots))}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 10
def test_case_10_source_invalidation_and_coverage_are_exact() -> None:
    values = _bundle()
    observations = values["observations"]
    assert isinstance(observations, tuple)
    missing = tuple(item for item in observations if item.index != 20)
    assert _analyze({**values, "observations": missing}).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "observations": ()}).status is SMCV2PrimitiveStatus.UNKNOWN
    transitions = values["order_block_transitions"]
    snapshots = values["order_block_snapshots"]
    assert isinstance(transitions, tuple) and isinstance(snapshots, tuple)
    assert _analyze(
        {
            **values,
            "order_block_transitions": transitions[:-1],
            "order_block_snapshots": snapshots[:-1],
        }
    ).status is SMCV2PrimitiveStatus.INVALID


# Logical case 11
def test_case_11_swing_contract_and_composite_order_are_exact() -> None:
    values = _bundle()
    swings = values["swings"]
    assert isinstance(swings, tuple)
    assert _analyze({**values, "swings": tuple(reversed(swings))}).status is SMCV2PrimitiveStatus.INVALID
    malformed = object.__new__(DealingRangeSwing)
    object.__setattr__(malformed, "swing_id", swings[-1].swing_id)
    assert _analyze({**values, "swings": (*swings[:-1], malformed)}).status is SMCV2PrimitiveStatus.INVALID
    too_early = replace(
        swings[-1],
        provenance=replace(
            swings[-1].provenance,
            confirmation_index=swings[-1].provenance.source_indices[0] + 1,
            confirmation_timestamp=_time(
                swings[-1].provenance.source_indices[0] + 1
            ),
        ),
    )
    assert _analyze({**values, "swings": (*swings[:-1], too_early)}).status is SMCV2PrimitiveStatus.INVALID
    duplicate_source_side = replace(swings[-1], swing_id="e" * 64)
    duplicated = tuple(sorted((*swings, duplicate_source_side), key=_swing_key))
    assert _analyze({**values, "swings": duplicated}).status is SMCV2PrimitiveStatus.INVALID
    observations = values["observations"]
    assert isinstance(observations, tuple)
    for missing_index in (
        swings[-1].provenance.source_indices[0],
        swings[-1].provenance.confirmation_index,
    ):
        missing = tuple(item for item in observations if item.index != missing_index)
        assert _analyze({**values, "observations": missing}).status is SMCV2PrimitiveStatus.INVALID
    mismatched_source = replace(
        swings[-1],
        provenance=replace(
            swings[-1].provenance,
            source_timestamps=(_time(13),),
        ),
    )
    mismatched_confirmation = replace(
        swings[-1],
        provenance=replace(
            swings[-1].provenance,
            confirmation_timestamp=_time(15),
        ),
    )
    for changed in (mismatched_source, mismatched_confirmation):
        assert _analyze(
            {**values, "swings": (*swings[:-1], changed)}
        ).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze({**values, "observations": ()}).status is SMCV2PrimitiveStatus.UNKNOWN


# Logical case 12
def test_case_12_event_contract_identity_and_order_are_exact() -> None:
    values = _bundle()
    events = values["structure_events"]
    assert isinstance(events, tuple)
    assert _analyze({**values, "structure_events": tuple(reversed(events))}).status is SMCV2PrimitiveStatus.INVALID
    bad = replace(events[-1], event_id="f" * 64)
    assert _analyze({**values, "structure_events": (*events[:-1], bad)}).status is SMCV2PrimitiveStatus.INVALID
    observations = values["observations"]
    assert isinstance(observations, tuple)
    missing_event_bar = tuple(item for item in observations if item.index != 22)
    assert _analyze({**values, "observations": missing_event_bar}).status is SMCV2PrimitiveStatus.INVALID
    mismatched = replace(
        events[-1],
        provenance=replace(
            events[-1].provenance,
            source_timestamps=(_time(21),),
        ),
    )
    assert _analyze(
        {**values, "structure_events": (*events[:-1], mismatched)}
    ).status is SMCV2PrimitiveStatus.INVALID


# Logical case 13
def test_case_13_failed_bearish_source_forms_bullish_breaker() -> None:
    result = _valid(SMCV2Direction.BEARISH)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.breakers[0].direction is SMCV2Direction.BULLISH


# Logical case 14
def test_case_14_failed_bullish_source_forms_bearish_breaker() -> None:
    result = _valid(SMCV2Direction.BULLISH)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.breakers[0].direction is SMCV2Direction.BEARISH


# Logical case 15
def test_case_15_offset_zero_confirmation_qualifies() -> None:
    result = _analyze(_bundle(confirmation_offset=0))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.breakers[0].confirmation_index == 20


# Logical case 16
def test_case_16_inside_window_confirmation_qualifies() -> None:
    result = _analyze(_bundle(confirmation_offset=4))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.breakers[0].confirmation_index == 24


# Logical case 17
def test_case_17_exact_offset_ten_qualifies() -> None:
    result = _analyze(_bundle(confirmation_offset=10))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.breakers[0].confirmation_index == 30


# Logical case 18
def test_case_18_offset_eleven_does_not_qualify() -> None:
    result = _analyze(_bundle(confirmation_offset=11))
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.breakers == ()


# Logical case 19
def test_case_19_incomplete_window_is_unknown_and_invalid_wins() -> None:
    values = _bundle(include_candidate=False)
    assert _analyze(values).status is SMCV2PrimitiveStatus.UNKNOWN
    observations = values["observations"]
    assert isinstance(observations, tuple)
    malformed = object.__new__(BreakerBlockObservation)
    object.__setattr__(malformed, "index", 24)
    object.__setattr__(malformed, "timestamp", _time(24))
    assert _analyze({**values, "observations": (*observations, malformed)}).status is SMCV2PrimitiveStatus.INVALID


# Logical case 20
def test_case_20_exhausted_no_event_window_is_none() -> None:
    assert _analyze(
        _bundle(include_candidate=False, complete_window=True)
    ).status is SMCV2PrimitiveStatus.NONE


# Logical case 21
def test_case_21_wrong_direction_event_does_not_form() -> None:
    values = _bundle(include_candidate=False, complete_window=True)
    swings = values["swings"]
    observations = values["observations"]
    events = values["structure_events"]
    assert isinstance(swings, tuple) and isinstance(events, tuple)
    assert isinstance(observations, tuple)
    wrong = _event(
        swings[0],
        SMCV2Direction.BULLISH,
        confirmation_index=22,
    )
    changed = tuple(
        _obs(22, high=112, low=105, close=111) if item.index == 22 else item
        for item in observations
    )
    result = _analyze(
        {
            **values,
            "structure_events": tuple(sorted((*events, wrong), key=_event_key)),
            "observations": changed,
        }
    )
    assert result.status is SMCV2PrimitiveStatus.NONE


# Logical case 22
def test_case_22_bos_type_is_retained() -> None:
    assert _valid().breakers[0].structure_event_type is DealingRangeEventType.BOS


# Logical case 23
def test_case_23_choch_type_is_retained() -> None:
    result = _analyze(_bundle(event_type=DealingRangeEventType.CHOCH))
    assert result.breakers[0].structure_event_type is DealingRangeEventType.CHOCH


# Logical case 24
def test_case_24_earliest_qualifying_event_wins() -> None:
    values = _bundle()
    swings = values["swings"]
    events = values["structure_events"]
    observations = values["observations"]
    assert isinstance(swings, tuple) and isinstance(events, tuple)
    assert isinstance(observations, tuple)
    early = _event(
        swings[-1],
        SMCV2Direction.BEARISH,
        confirmation_index=21,
        event_type=DealingRangeEventType.CHOCH,
    )
    changed = tuple(
        _obs(21, high=95, low=88, close=89) if item.index == 21 else item
        for item in observations
    )
    result = _analyze(
        {
            **values,
            "structure_events": tuple(sorted((*events, early), key=_event_key)),
            "observations": changed,
        }
    )
    assert result.breakers[0].confirmation_index == 21
    assert result.breakers[0].structure_event_type is DealingRangeEventType.CHOCH


# Logical case 25
@pytest.mark.parametrize(
    ("source_direction", "breaker_direction", "proximal", "distal"),
    (
        (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH, 100, 104),
        (SMCV2Direction.BEARISH, SMCV2Direction.BULLISH, 104, 100),
    ),
)
def test_case_25_geometry_and_role_reversal_are_immutable(
    source_direction: SMCV2Direction,
    breaker_direction: SMCV2Direction,
    proximal: int,
    distal: int,
) -> None:
    block = _bundle(source_direction)["order_blocks"][0]  # type: ignore[index]
    breaker = _valid(source_direction).breakers[0]
    assert breaker.direction is breaker_direction
    assert (breaker.wick_low_tick, breaker.wick_high_tick) == (
        block.wick_low_tick,
        block.wick_high_tick,
    )
    assert (breaker.proximal_tick, breaker.distal_tick) == (proximal, distal)
    assert breaker.midpoint_tick == Decimal("102")


# Logical case 26
def test_case_26_creation_transition_and_snapshot_are_exact() -> None:
    result = _valid()
    assert len(result.breakers) == len(result.transitions) == len(result.snapshots) == 1
    transition = result.transitions[0]
    snapshot = result.snapshots[0]
    assert (transition.from_state, transition.to_state, transition.reason) == (
        None,
        BreakerBlockState.ACTIVE,
        "ROLE_REVERSAL_CONFIRMED",
    )
    assert snapshot.transition_ids == (transition.transition_id,)


# Logical case 27
def test_case_27_formation_observation_cannot_retest() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    observations = values["observations"]
    assert isinstance(observations, tuple)
    changed = tuple(
        _obs(22, high=112, low=99, close=111) if item.index == 22 else item
        for item in observations
    )
    result = _analyze({**values, "observations": changed})
    assert result.snapshots[-1].state is BreakerBlockState.ACTIVE
    assert len(result.transitions) == 1


# Logical case 28
@pytest.mark.parametrize(
    "source_direction",
    (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH),
)
def test_case_28_proximal_equality_touches(
    source_direction: SMCV2Direction,
) -> None:
    values = _bundle(source_direction)
    direction = _valid(source_direction).breakers[0].direction
    result = _analyze(_with_observations(values, _retest(23, direction, BreakerBlockState.TOUCHED)))
    assert result.snapshots[-1].state is BreakerBlockState.TOUCHED


# Logical case 29
def test_case_29_strict_penetration_is_partial() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    result = _analyze(
        _with_observations(
            values,
            _retest(23, SMCV2Direction.BULLISH, BreakerBlockState.PARTIALLY_MITIGATED),
        )
    )
    assert result.snapshots[-1].state is BreakerBlockState.PARTIALLY_MITIGATED


# Logical case 30
def test_case_30_midpoint_is_exact_and_context_independent() -> None:
    with localcontext() as context:
        context.prec = 2
        result = _valid(SMCV2Direction.BEARISH)
    assert result.breakers[0].midpoint_tick == Decimal("102")
    values = _bundle(SMCV2Direction.BEARISH)
    result = _analyze(
        _with_observations(
            values,
            _retest(23, SMCV2Direction.BULLISH, BreakerBlockState.MITIGATED),
        )
    )
    assert result.snapshots[-1].state is BreakerBlockState.MITIGATED
    breaker = result.breakers[0]
    base = _breaker_kwargs(breaker)
    huge = 10**120
    huge_values = {
        **base,
        "wick_boundaries": SMCV2TickRange(-huge - 1, huge),
        "body_boundaries": SMCV2TickRange(-huge, huge - 1),
        "proximal_tick": huge,
        "distal_tick": -huge - 1,
        "midpoint_tick": Decimal("-0.5"),
    }
    with localcontext() as context:
        context.prec = 2
        low_precision_id = make_breaker_block_id(**huge_values)
    with localcontext() as context:
        context.prec = 80
        high_precision_id = make_breaker_block_id(**huge_values)
    assert low_precision_id == high_precision_id


# Logical case 31
def test_case_31_direct_deeper_and_wick_beyond_distal_are_mitigated() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    beyond = _obs(23, high=106, low=99, close=103)
    result = _analyze(_with_observations(values, beyond))
    assert result.snapshots[-1].state is BreakerBlockState.MITIGATED


# Logical case 32
def test_case_32_same_index_invalidation_has_precedence() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    result = _analyze(
        _with_observations(
            values,
            _retest(23, SMCV2Direction.BULLISH, BreakerBlockState.INVALIDATED),
        )
    )
    assert result.snapshots[-1].state is BreakerBlockState.INVALIDATED
    assert result.transitions[-1].reason == "CLOSE_THROUGH_INVALIDATION"


# Logical case 33
@pytest.mark.parametrize(
    "prior_state",
    (
        BreakerBlockState.ACTIVE,
        BreakerBlockState.TOUCHED,
        BreakerBlockState.PARTIALLY_MITIGATED,
        BreakerBlockState.MITIGATED,
    ),
)
def test_case_33_every_live_state_can_invalidate(
    prior_state: BreakerBlockState,
) -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    direction = SMCV2Direction.BULLISH
    additions: list[BreakerBlockObservation] = []
    if prior_state is not BreakerBlockState.ACTIVE:
        additions.append(_retest(23, direction, prior_state))
    additions.append(_retest(24, direction, BreakerBlockState.INVALIDATED))
    result = _analyze(_with_observations(values, *additions))
    assert result.snapshots[-1].state is BreakerBlockState.INVALIDATED


# Logical case 34
def test_case_34_no_regression_expiry_or_post_terminal_change() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    direction = SMCV2Direction.BULLISH
    result = _analyze(
        _with_observations(
            values,
            _retest(23, direction, BreakerBlockState.MITIGATED),
            _retest(24, direction, BreakerBlockState.TOUCHED),
            _retest(25, direction, BreakerBlockState.INVALIDATED),
            _retest(26, direction, BreakerBlockState.TOUCHED),
        )
    )
    assert [item.state for item in result.snapshots] == [
        BreakerBlockState.ACTIVE,
        BreakerBlockState.MITIGATED,
        BreakerBlockState.INVALIDATED,
    ]


# Logical case 35
def test_case_35_duplicate_fork_and_opposing_pair_statuses() -> None:
    values = _bundle()
    events = values["structure_events"]
    swings = values["swings"]
    assert isinstance(events, tuple) and isinstance(swings, tuple)
    assert _analyze({**values, "structure_events": (*events, events[-1])}).status is SMCV2PrimitiveStatus.INVALID
    fork = _event(
        swings[-1],
        SMCV2Direction.BEARISH,
        confirmation_index=22,
        event_type=DealingRangeEventType.CHOCH,
    )
    assert _analyze({**values, "structure_events": tuple(sorted((*events, fork), key=_event_key))}).status is SMCV2PrimitiveStatus.INVALID
    opposing_low = _swing(
        DealingRangeSwingSide.LOW,
        source_index=12,
        confirmation_index=14,
        price_tick=120,
        swing_id="b" * 64,
    )
    bearish = _event(
        opposing_low,
        SMCV2Direction.BEARISH,
        confirmation_index=22,
    )
    opposing = _event(
        swings[0],
        SMCV2Direction.BULLISH,
        confirmation_index=22,
    )
    observations = values["observations"]
    assert isinstance(observations, tuple)
    changed = tuple(
        _obs(12, high=125, low=120, close=122)
        if item.index == 12
        else _obs(22, high=116, low=110, close=115)
        if item.index == 22
        else item
        for item in observations
    )
    ambiguous = _analyze(
        {
            **values,
            "swings": tuple(sorted((swings[0], opposing_low), key=_swing_key)),
            "structure_events": tuple(
                sorted((events[0], bearish, opposing), key=_event_key)
            ),
            "observations": changed,
        }
    )
    assert ambiguous.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert ambiguous.breakers == ()
    first = _bundle(SMCV2Direction.BULLISH)
    later = _bundle(
        SMCV2Direction.BULLISH,
        shift=40,
        source_char="c",
        candidate_char="d",
    )
    later_swings = later["swings"]
    later_events = later["structure_events"]
    later_observations = later["observations"]
    assert isinstance(later_swings, tuple)
    assert isinstance(later_events, tuple)
    assert isinstance(later_observations, tuple)
    later_low = _swing(
        DealingRangeSwingSide.LOW,
        source_index=52,
        confirmation_index=54,
        price_tick=120,
        swing_id="d" * 64,
    )
    later_bearish = _event(
        later_low,
        SMCV2Direction.BEARISH,
        confirmation_index=62,
    )
    later_bullish = _event(
        later_swings[0],
        SMCV2Direction.BULLISH,
        confirmation_index=62,
    )
    changed_later_observations = tuple(
        _obs(52, high=125, low=120, close=122)
        if item.index == 52
        else _obs(62, high=116, low=110, close=115)
        if item.index == 62
        else item
        for item in later_observations
    )
    later = {
        **later,
        "swings": tuple(
            sorted((later_swings[0], later_low), key=_swing_key)
        ),
        "structure_events": tuple(
            sorted(
                (later_events[0], later_bearish, later_bullish),
                key=_event_key,
            )
        ),
        "observations": changed_later_observations,
    }
    later_ambiguous = _analyze(_merge_bundles(first, later))
    expected_prior = _analyze(
        {
            **first,
            "observations": (
                *first["observations"],  # type: ignore[misc]
                *tuple(
                    item
                    for item in changed_later_observations
                    if item.index < 62
                ),
            ),
        }
    )
    assert later_ambiguous.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert later_ambiguous.breakers == expected_prior.breakers
    assert later_ambiguous.transitions == expected_prior.transitions
    assert later_ambiguous.snapshots == expected_prior.snapshots


# Logical case 36
def test_case_36_multiple_sources_are_deterministic() -> None:
    first = _bundle(SMCV2Direction.BULLISH)
    second = _bundle(
        SMCV2Direction.BEARISH,
        shift=40,
        source_char="c",
        candidate_char="d",
    )
    merged = _merge_bundles(first, second)
    result = _analyze(merged)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.breakers) == 2


# Logical case 37
def test_case_37_later_malformed_group_preserves_prior_evidence() -> None:
    values = _with_observations(
        _bundle(SMCV2Direction.BEARISH),
        _retest(23, SMCV2Direction.BULLISH, BreakerBlockState.TOUCHED),
    )
    malformed = object.__new__(BreakerBlockObservation)
    object.__setattr__(malformed, "index", 24)
    object.__setattr__(malformed, "timestamp", _time(24))
    result = _analyze(
        {**values, "observations": (*values["observations"], malformed)}  # type: ignore[misc]
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.breakers
    assert result.snapshots[-1].state is BreakerBlockState.TOUCHED
    first = _bundle(SMCV2Direction.BULLISH)
    second = _bundle(
        SMCV2Direction.BEARISH,
        shift=40,
        source_char="c",
        candidate_char="d",
    )
    merged = _merge_bundles(first, second)
    baseline = _analyze(merged)
    assert len(baseline.breakers) == 2
    blocks = merged["order_blocks"]
    transitions = merged["order_block_transitions"]
    snapshots = merged["order_block_snapshots"]
    swings = merged["swings"]
    events = merged["structure_events"]
    observations = merged["observations"]
    assert all(
        isinstance(value, tuple)
        for value in (blocks, transitions, snapshots, swings, events, observations)
    )
    variants = (
        (
            {
                **merged,
                "order_blocks": (
                    blocks[0],  # type: ignore[index]
                    replace(blocks[1], block_id="f" * 64),  # type: ignore[index]
                ),
            },
            50,
        ),
        (
            {
                **merged,
                "order_block_transitions": (
                    *transitions[:-1],  # type: ignore[index]
                    replace(transitions[-1], transition_id="f" * 64),  # type: ignore[index]
                ),
            },
            60,
        ),
        (
            {
                **merged,
                "order_block_snapshots": (
                    *snapshots[:-1],  # type: ignore[index]
                    replace(snapshots[-1], snapshot_id="f" * 64),  # type: ignore[index]
                ),
            },
            60,
        ),
        (
            {
                **merged,
                "swings": (
                    *swings[:-1],  # type: ignore[index]
                    replace(swings[-1], price_tick=swings[-1].price_tick + 1),  # type: ignore[index]
                ),
            },
            54,
        ),
        (
            {
                **merged,
                "structure_events": (
                    *events[:-1],  # type: ignore[index]
                    replace(events[-1], event_id="f" * 64),  # type: ignore[index]
                ),
            },
            62,
        ),
    )
    for changed, cutoff_index in variants:
        invalid = _analyze(changed)
        assert invalid.status is SMCV2PrimitiveStatus.INVALID
        assert invalid.breakers == tuple(
            item
            for item in baseline.breakers
            if item.confirmation_index < cutoff_index
        )
        assert invalid.transitions == tuple(
            item for item in baseline.transitions if item.index < cutoff_index
        )
        assert invalid.snapshots == tuple(
            item for item in baseline.snapshots if item.index < cutoff_index
        )
    malformed_unknown = object.__new__(BreakerBlockObservation)
    assert _analyze(
        {**merged, "observations": (*observations, malformed_unknown)}  # type: ignore[misc]
    ).breakers == ()


# Logical case 38
def test_case_38_final_status_precedence_is_exact() -> None:
    values = _bundle(include_candidate=False)
    malformed = object.__new__(BreakerBlockObservation)
    object.__setattr__(malformed, "index", 24)
    object.__setattr__(malformed, "timestamp", _time(24))
    result = _analyze(
        {**values, "observations": (*values["observations"], malformed)}  # type: ignore[misc]
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


def _breaker_kwargs(breaker: BreakerBlock) -> dict[str, object]:
    return dict(
        identity_kind="BREAKER",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=breaker.direction,
        source_order_block_id=breaker.source_order_block_id,
        source_order_block_invalidation_transition_id=breaker.source_order_block_invalidation_transition_id,
        source_order_block_invalidation_snapshot_id=breaker.source_order_block_invalidation_snapshot_id,
        structure_event_id=breaker.structure_event_id,
        structure_event_type=breaker.structure_event_type,
        wick_boundaries=SMCV2TickRange(
            breaker.wick_low_tick,
            breaker.wick_high_tick,
        ),
        body_boundaries=SMCV2TickRange(
            breaker.body_low_tick,
            breaker.body_high_tick,
        ),
        proximal_tick=breaker.proximal_tick,
        distal_tick=breaker.distal_tick,
        midpoint_tick=breaker.midpoint_tick,
        source_invalidation_index=breaker.source_invalidation_index,
        source_invalidation_timestamp=breaker.source_invalidation_timestamp,
        confirmation_index=breaker.confirmation_index,
        confirmation_timestamp=breaker.confirmation_timestamp,
    )


# Logical case 39
def test_case_39_breaker_identity_schema_and_sensitivity() -> None:
    breaker = _valid().breakers[0]
    kwargs = _breaker_kwargs(breaker)
    assert make_breaker_block_id(**kwargs) == breaker.breaker_id
    for required in tuple(kwargs):
        missing = dict(kwargs)
        missing.pop(required)
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**missing)  # type: ignore[arg-type]
    forbidden_values = {
        "breaker_id": breaker.breaker_id,
        "from_state": BreakerBlockState.ACTIVE,
        "to_state": BreakerBlockState.TOUCHED,
        "effective_index": 23,
        "effective_timestamp": _time(23),
        "reason": "WICK_TOUCHED",
        "state": BreakerBlockState.ACTIVE,
        "transition_ids": ("a" * 64,),
    }
    for name, value in forbidden_values.items():
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**{**kwargs, name: value})
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(**{**kwargs, "midpoint_tick": Decimal("102.5")})
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(**{**kwargs, "breaker_id": breaker.breaker_id})
    assert make_breaker_block_id(
        **{**kwargs, "instrument": " gc ", "timeframe": " m5 "}
    ) == breaker.breaker_id
    for name in (
        "source_order_block_id",
        "source_order_block_invalidation_transition_id",
        "source_order_block_invalidation_snapshot_id",
        "structure_event_id",
    ):
        assert make_breaker_block_id(
            **{**kwargs, name: "e" * 64}
        ) != breaker.breaker_id
    assert make_breaker_block_id(
        **{
            **kwargs,
            "direction": SMCV2Direction.BULLISH,
            "proximal_tick": 104,
            "distal_tick": 100,
        }
    ) != breaker.breaker_id
    assert make_breaker_block_id(
        **{
            **kwargs,
            "wick_boundaries": SMCV2TickRange(99, 104),
            "body_boundaries": SMCV2TickRange(100, 103),
            "proximal_tick": 99,
            "midpoint_tick": Decimal("101.5"),
        }
    ) != breaker.breaker_id
    assert make_breaker_block_id(
        **{
            **kwargs,
            "confirmation_index": breaker.confirmation_index + 1,
            "confirmation_timestamp": breaker.confirmation_timestamp
            + timedelta(minutes=5),
        }
    ) != breaker.breaker_id
    malformed_range = object.__new__(SMCV2TickRange)
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(
            **{**kwargs, "wick_boundaries": malformed_range}
        )


# Logical case 40
def test_case_40_transition_identity_edges_and_reasons_are_exact() -> None:
    result = _valid()
    breaker = result.breakers[0]
    transition = result.transitions[0]
    kwargs = dict(
        identity_kind="TRANSITION",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=breaker.direction,
        source_order_block_id=breaker.source_order_block_id,
        source_order_block_invalidation_transition_id=breaker.source_order_block_invalidation_transition_id,
        source_order_block_invalidation_snapshot_id=breaker.source_order_block_invalidation_snapshot_id,
        structure_event_id=breaker.structure_event_id,
        breaker_id=breaker.breaker_id,
        from_state=transition.from_state,
        to_state=transition.to_state,
        effective_index=transition.index,
        effective_timestamp=transition.timestamp,
        reason=transition.reason,
    )
    assert make_breaker_block_id(**kwargs) == transition.transition_id
    required = (
        "identity_kind",
        "instrument",
        "timeframe",
        "direction",
        "source_order_block_id",
        "source_order_block_invalidation_transition_id",
        "source_order_block_invalidation_snapshot_id",
        "structure_event_id",
        "breaker_id",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
    )
    for name in required:
        missing = dict(kwargs)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**missing)  # type: ignore[arg-type]
    forbidden_values = {
        "structure_event_type": DealingRangeEventType.BOS,
        "wick_boundaries": SMCV2TickRange(100, 104),
        "body_boundaries": SMCV2TickRange(101, 103),
        "proximal_tick": 100,
        "distal_tick": 104,
        "midpoint_tick": Decimal("102"),
        "source_invalidation_index": 20,
        "source_invalidation_timestamp": _time(20),
        "confirmation_index": 22,
        "confirmation_timestamp": _time(22),
        "state": BreakerBlockState.ACTIVE,
        "transition_ids": ("a" * 64,),
    }
    for name, value in forbidden_values.items():
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**{**kwargs, name: value})
    allowed_edges = (
        (None, BreakerBlockState.ACTIVE, "ROLE_REVERSAL_CONFIRMED"),
        (BreakerBlockState.ACTIVE, BreakerBlockState.TOUCHED, "WICK_TOUCHED"),
        (
            BreakerBlockState.ACTIVE,
            BreakerBlockState.PARTIALLY_MITIGATED,
            "PARTIAL_MITIGATION",
        ),
        (
            BreakerBlockState.ACTIVE,
            BreakerBlockState.MITIGATED,
            "MIDPOINT_MITIGATION",
        ),
        (
            BreakerBlockState.TOUCHED,
            BreakerBlockState.PARTIALLY_MITIGATED,
            "PARTIAL_MITIGATION",
        ),
        (
            BreakerBlockState.TOUCHED,
            BreakerBlockState.MITIGATED,
            "MIDPOINT_MITIGATION",
        ),
        (
            BreakerBlockState.PARTIALLY_MITIGATED,
            BreakerBlockState.MITIGATED,
            "MIDPOINT_MITIGATION",
        ),
        *tuple(
            (state, BreakerBlockState.INVALIDATED, "CLOSE_THROUGH_INVALIDATION")
            for state in (
                BreakerBlockState.ACTIVE,
                BreakerBlockState.TOUCHED,
                BreakerBlockState.PARTIALLY_MITIGATED,
                BreakerBlockState.MITIGATED,
            )
        ),
    )
    for from_state, to_state, reason in allowed_edges:
        assert len(
            make_breaker_block_id(
                **{
                    **kwargs,
                    "from_state": from_state,
                    "to_state": to_state,
                    "reason": reason,
                }
            )
        ) == 64
    impossible_edges = (
        (
            BreakerBlockState.TOUCHED,
            BreakerBlockState.ACTIVE,
            "WICK_TOUCHED",
        ),
        (
            BreakerBlockState.MITIGATED,
            BreakerBlockState.TOUCHED,
            "WICK_TOUCHED",
        ),
        (
            BreakerBlockState.INVALIDATED,
            BreakerBlockState.INVALIDATED,
            "CLOSE_THROUGH_INVALIDATION",
        ),
    )
    for from_state, to_state, reason in impossible_edges:
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(
                **{
                    **kwargs,
                    "from_state": from_state,
                    "to_state": to_state,
                    "reason": reason,
                }
            )
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(**{**kwargs, "reason": "role_reversal_confirmed"})
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(
            **{**kwargs, "to_state": BreakerBlockState.INVALIDATED}
        )


# Logical case 41
def test_case_41_snapshot_identity_history_is_exact() -> None:
    result = _valid()
    breaker = result.breakers[0]
    snapshot = result.snapshots[0]
    kwargs = dict(
        identity_kind="SNAPSHOT",
        instrument=_INSTRUMENT,
        timeframe=_TIMEFRAME,
        direction=breaker.direction,
        source_order_block_id=breaker.source_order_block_id,
        source_order_block_invalidation_transition_id=breaker.source_order_block_invalidation_transition_id,
        source_order_block_invalidation_snapshot_id=breaker.source_order_block_invalidation_snapshot_id,
        structure_event_id=breaker.structure_event_id,
        breaker_id=breaker.breaker_id,
        state=snapshot.state,
        effective_index=snapshot.index,
        effective_timestamp=snapshot.timestamp,
        transition_ids=snapshot.transition_ids,
    )
    assert make_breaker_block_id(**kwargs) == snapshot.snapshot_id
    required = (
        "identity_kind",
        "instrument",
        "timeframe",
        "direction",
        "source_order_block_id",
        "source_order_block_invalidation_transition_id",
        "source_order_block_invalidation_snapshot_id",
        "structure_event_id",
        "breaker_id",
        "state",
        "effective_index",
        "effective_timestamp",
        "transition_ids",
    )
    for name in required:
        missing = dict(kwargs)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**missing)  # type: ignore[arg-type]
    forbidden_values = {
        "structure_event_type": DealingRangeEventType.BOS,
        "wick_boundaries": SMCV2TickRange(100, 104),
        "body_boundaries": SMCV2TickRange(101, 103),
        "proximal_tick": 100,
        "distal_tick": 104,
        "midpoint_tick": Decimal("102"),
        "source_invalidation_index": 20,
        "source_invalidation_timestamp": _time(20),
        "confirmation_index": 22,
        "confirmation_timestamp": _time(22),
        "from_state": BreakerBlockState.ACTIVE,
        "to_state": BreakerBlockState.TOUCHED,
        "reason": "WICK_TOUCHED",
    }
    for name, value in forbidden_values.items():
        with pytest.raises((TypeError, ValueError)):
            make_breaker_block_id(**{**kwargs, name: value})
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(**{**kwargs, "transition_ids": ()})
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(
            **{**kwargs, "transition_ids": (*snapshot.transition_ids,) * 2}
        )
    for name in (
        "source_order_block_id",
        "source_order_block_invalidation_transition_id",
        "source_order_block_invalidation_snapshot_id",
        "structure_event_id",
        "breaker_id",
    ):
        assert make_breaker_block_id(
            **{**kwargs, name: "e" * 64}
        ) != snapshot.snapshot_id
    assert make_breaker_block_id(
        **{**kwargs, "state": BreakerBlockState.TOUCHED}
    ) != snapshot.snapshot_id
    assert make_breaker_block_id(
        **{
            **kwargs,
            "effective_index": snapshot.index + 1,
            "effective_timestamp": snapshot.timestamp + timedelta(minutes=5),
        }
    ) != snapshot.snapshot_id
    second_id = "e" * 64
    first_order = make_breaker_block_id(
        **{**kwargs, "transition_ids": (*snapshot.transition_ids, second_id)}
    )
    reversed_order = make_breaker_block_id(
        **{**kwargs, "transition_ids": (second_id, *snapshot.transition_ids)}
    )
    assert first_order != reversed_order
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(**{**kwargs, "breaker_id": "not-a-hash"})


# Logical case 42
def test_case_42_public_api_fields_enums_and_exports_are_exact() -> None:
    assert BREAKER_BLOCK_DETECTOR_VERSION == "SMC-V2-BREAKER-BLOCK-1"
    assert [item.value for item in BreakerBlockState] == [
        "ACTIVE",
        "TOUCHED",
        "PARTIALLY_MITIGATED",
        "MITIGATED",
        "INVALIDATED",
    ]
    expected_fields = {
        BreakerBlockObservation: (
            ("index", int),
            ("timestamp", datetime),
            ("high_tick", int),
            ("low_tick", int),
            ("close_tick", int),
        ),
        BreakerBlock: (
            ("breaker_id", str),
            ("direction", SMCV2Direction),
            ("source_order_block_id", str),
            ("source_order_block_invalidation_transition_id", str),
            ("source_order_block_invalidation_snapshot_id", str),
            ("structure_event_id", str),
            ("structure_event_type", DealingRangeEventType),
            ("wick_low_tick", int),
            ("wick_high_tick", int),
            ("body_low_tick", int),
            ("body_high_tick", int),
            ("proximal_tick", int),
            ("distal_tick", int),
            ("midpoint_tick", Decimal),
            ("source_invalidation_index", int),
            ("source_invalidation_timestamp", datetime),
            ("confirmation_index", int),
            ("confirmation_timestamp", datetime),
        ),
        BreakerBlockTransition: (
            ("transition_id", str),
            ("breaker_id", str),
            ("source_order_block_id", str),
            ("source_order_block_invalidation_transition_id", str),
            ("source_order_block_invalidation_snapshot_id", str),
            ("structure_event_id", str),
            ("from_state", BreakerBlockState | None),
            ("to_state", BreakerBlockState),
            ("index", int),
            ("timestamp", datetime),
            ("reason", str),
        ),
        BreakerBlockSnapshot: (
            ("snapshot_id", str),
            ("breaker_id", str),
            ("source_order_block_id", str),
            ("source_order_block_invalidation_transition_id", str),
            ("source_order_block_invalidation_snapshot_id", str),
            ("structure_event_id", str),
            ("direction", SMCV2Direction),
            ("state", BreakerBlockState),
            ("index", int),
            ("timestamp", datetime),
            ("transition_ids", tuple[str, ...]),
        ),
        BreakerBlockResult: (
            ("status", SMCV2PrimitiveStatus),
            ("breakers", tuple[BreakerBlock, ...]),
            ("transitions", tuple[BreakerBlockTransition, ...]),
            ("snapshots", tuple[BreakerBlockSnapshot, ...]),
            ("reasons", tuple[str, ...]),
            ("blocking_reasons", tuple[str, ...]),
        ),
    }
    for model, expected in expected_fields.items():
        assert [(field.name, get_type_hints(model)[field.name]) for field in fields(model)] == list(expected)
        assert model.__dataclass_params__.frozen is True
    for model in (
        BreakerBlockObservation,
        BreakerBlock,
        BreakerBlockTransition,
        BreakerBlockSnapshot,
    ):
        assert all(field.default is MISSING for field in fields(model))
    result_fields = fields(BreakerBlockResult)
    assert result_fields[0].default is MISSING
    assert all(field.default == () for field in result_fields[1:])
    analyzer = signature(analyze_breaker_blocks)
    assert list(analyzer.parameters) == [
        "instrument",
        "timeframe",
        "order_blocks",
        "order_block_transitions",
        "order_block_snapshots",
        "swings",
        "structure_events",
        "observations",
    ]
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY
        for parameter in analyzer.parameters.values()
    )
    assert all(
        parameter.default is Parameter.empty
        for parameter in analyzer.parameters.values()
    )
    builder = signature(make_breaker_block_id)
    assert list(builder.parameters) == [
        "identity_kind",
        "instrument",
        "timeframe",
        "direction",
        "source_order_block_id",
        "source_order_block_invalidation_transition_id",
        "source_order_block_invalidation_snapshot_id",
        "structure_event_id",
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
        "breaker_id",
        "from_state",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
        "state",
        "transition_ids",
    ]
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY
        for parameter in builder.parameters.values()
    )
    assert all(
        builder.parameters[name].default is Parameter.empty
        for name in ("identity_kind", "instrument", "timeframe", "direction")
    )
    assert all(
        builder.parameters[name].default is None
        for name in list(builder.parameters)[4:-1]
    )
    assert builder.parameters["transition_ids"].default == ()
    with pytest.raises((TypeError, ValueError)):
        make_breaker_block_id(
            identity_kind="UNKNOWN",
            instrument=_INSTRUMENT,
            timeframe=_TIMEFRAME,
            direction=SMCV2Direction.BULLISH,
        )
    samples = (
        _obs(1),
        *_valid().breakers,
        *_valid().transitions,
        *_valid().snapshots,
        _valid(),
    )
    for sample in samples:
        with pytest.raises(FrozenInstanceError):
            setattr(sample, fields(type(sample))[0].name, None)
    assert breaker_module.__all__ == [
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


# Logical case 43
def test_case_43_repeatability_and_complete_prefix_invariance() -> None:
    values = _bundle(SMCV2Direction.BEARISH)
    first = _analyze(values)
    second = _analyze(values)
    assert first == second
    extended = _analyze(
        _with_observations(
            values,
            _retest(23, SMCV2Direction.BULLISH, BreakerBlockState.TOUCHED),
        )
    )
    assert extended.breakers[: len(first.breakers)] == first.breakers
    assert extended.transitions[: len(first.transitions)] == first.transitions
    assert extended.snapshots[: len(first.snapshots)] == first.snapshots
    observations = values["observations"]
    snapshots = values["order_block_snapshots"]
    swings = values["swings"]
    assert isinstance(observations, tuple)
    assert isinstance(snapshots, tuple)
    assert isinstance(swings, tuple)
    same_effective = _analyze(
        {**values, "observations": (*observations, observations[-1])}
    )
    assert same_effective.status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(
        {**values, "order_block_snapshots": snapshots[:-1]}
    ).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(
        {**values, "swings": tuple(reversed(swings))}
    ).status is SMCV2PrimitiveStatus.INVALID
    historical = _obs(
        19,
        high=105,
        low=104,
        close=104,
        timestamp=_time(19),
    )
    assert _analyze(
        {**values, "observations": (*observations, historical)}
    ).status is SMCV2PrimitiveStatus.INVALID
    first_bundle = _bundle(SMCV2Direction.BULLISH)
    second_bundle = _bundle(
        SMCV2Direction.BEARISH,
        shift=40,
        source_char="c",
        candidate_char="d",
    )
    merged = _merge_bundles(first_bundle, second_bundle)
    assert _analyze(merged) == _analyze(merged)


# Logical case 44
def test_case_44_module_is_standalone_and_has_no_forbidden_surface() -> None:
    source = Path(breaker_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not imported.intersection(
        {"pandas", "requests", "broker", "risk", "strategy", "execution"}
    )
    assert not {
        "smc.mitigation_block",
        "smc.liquidity_map",
        "smc.premium_discount",
        "smc.fair_value_gap",
    }.intersection(imported_from)
    assert "open(" not in source
