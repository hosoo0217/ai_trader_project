from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import inspect
from pathlib import Path

import pytest

import smc.order_block as order_block_module
from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    DealingRangeSwingSide,
    make_dealing_range_id,
)
from smc.order_block import (
    ORDER_BLOCK_DETECTOR_VERSION,
    OrderBlock,
    OrderBlockCandle,
    OrderBlockResult,
    OrderBlockSnapshot,
    OrderBlockState,
    OrderBlockTransition,
    analyze_order_blocks,
    make_order_block_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


_BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
_SWING_A = "a" * 64
_SWING_B = "b" * 64


def _time(index: int) -> datetime:
    return _BASE + timedelta(minutes=5 * index)


def _candle(
    index: int,
    *,
    open_tick: int = 100,
    high_tick: int = 102,
    low_tick: int = 98,
    close_tick: int = 101,
    timestamp: datetime | None = None,
) -> OrderBlockCandle:
    return OrderBlockCandle(
        index=index,
        timestamp=_time(index) if timestamp is None else timestamp,
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
    )


def _swing(
    *,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    source_index: int = 5,
    confirmation_index: int = 7,
    swing_id: str = _SWING_A,
) -> DealingRangeSwing:
    side = (
        DealingRangeSwingSide.HIGH
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.LOW
    )
    price = 110 if side is DealingRangeSwingSide.HIGH else 90
    return DealingRangeSwing(
        side=side,
        price_tick=price,
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
    *,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    event_type: DealingRangeEventType = DealingRangeEventType.BOS,
    source_indices: tuple[int, ...] = (14,),
) -> DealingRangeStructureEvent:
    provenance = SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(_time(index) for index in source_indices),
        confirmation_index=source_indices[-1],
        confirmation_timestamp=_time(source_indices[-1]),
    )
    event_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument="GC",
        timeframe="M5",
        direction=direction,
        source_indices=source_indices,
        event_type=event_type,
        broken_swing_id=swing.swing_id,
        confirmation_index=source_indices[-1],
        boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick),
    )
    return DealingRangeStructureEvent(
        direction=direction,
        event_type=event_type,
        broken_swing_id=swing.swing_id,
        provenance=provenance,
        event_id=event_id,
    )


def _market(
    *,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    displacement_indices: tuple[int, ...] = (14,),
    event_type: DealingRangeEventType = DealingRangeEventType.BOS,
) -> tuple[
    tuple[OrderBlockCandle, ...],
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    candles = []
    for index in range(15):
        candles.append(_candle(index))
    source_index = displacement_indices[0] - 1
    if direction is SMCV2Direction.BULLISH:
        candles[5] = _candle(5, open_tick=105, high_tick=110, low_tick=103, close_tick=106)
        candles[source_index] = _candle(source_index, open_tick=104, high_tick=105, low_tick=100, close_tick=101)
        for index in displacement_indices:
            candles[index] = _candle(index, open_tick=104, high_tick=113, low_tick=103, close_tick=111)
    else:
        candles[5] = _candle(5, open_tick=95, high_tick=97, low_tick=90, close_tick=94)
        candles[source_index] = _candle(source_index, open_tick=96, high_tick=100, low_tick=95, close_tick=99)
        for index in displacement_indices:
            candles[index] = _candle(index, open_tick=96, high_tick=97, low_tick=87, close_tick=89)
    swing = _swing(direction=direction)
    event = _event(
        swing,
        direction=direction,
        event_type=event_type,
        source_indices=displacement_indices,
    )
    return tuple(candles), (swing,), (event,)


def _analyze(
    candles: tuple[OrderBlockCandle, ...] | None,
    swings: tuple[DealingRangeSwing, ...] | None,
    events: tuple[DealingRangeStructureEvent, ...] | None,
) -> OrderBlockResult:
    return analyze_order_blocks(
        instrument="GC",
        timeframe="M5",
        candles=candles,
        swings=swings,
        structure_events=events,
    )


def _valid(direction: SMCV2Direction = SMCV2Direction.BULLISH) -> OrderBlockResult:
    return _analyze(*_market(direction=direction))


def _history_market(
    displacement_index: int,
    *,
    baseline_bodies: tuple[int, ...] | None = None,
    displacement_body: int = 7,
) -> tuple[
    tuple[OrderBlockCandle, ...],
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    bodies = baseline_bodies or tuple(1 for _ in range(displacement_index))
    assert len(bodies) == displacement_index
    candles = []
    for index, body in enumerate(bodies):
        candles.append(
            _candle(
                index,
                open_tick=100,
                high_tick=max(101 + body, 110 if index == 1 else 0),
                low_tick=99,
                close_tick=100 + body,
            )
        )
    source_body = bodies[-1]
    candles[-1] = _candle(
        displacement_index - 1,
        open_tick=100 + source_body,
        high_tick=101 + source_body,
        low_tick=99,
        close_tick=100,
    )
    candles.append(
        _candle(
            displacement_index,
            open_tick=111 - displacement_body,
            high_tick=112,
            low_tick=111 - displacement_body,
            close_tick=111,
        )
    )
    swing = DealingRangeSwing(
        side=DealingRangeSwingSide.HIGH,
        price_tick=110,
        provenance=SMCV2EventProvenance(
            source_indices=(1,),
            source_timestamps=(_time(1),),
            confirmation_index=3,
            confirmation_timestamp=_time(3),
        ),
        swing_id=_SWING_A,
    )
    return tuple(candles), (swing,), (_event(swing, source_indices=(displacement_index,)),)


def _lifecycle_result(
    direction: SMCV2Direction,
    *,
    open_tick: int,
    high_tick: int,
    low_tick: int,
    close_tick: int,
) -> OrderBlockResult:
    candles, swings, events = _market(direction=direction)
    return _analyze(
        _append(
            candles,
            open_tick=open_tick,
            high_tick=high_tick,
            low_tick=low_tick,
            close_tick=close_tick,
        ),
        swings,
        events,
    )


def _append(
    candles: tuple[OrderBlockCandle, ...],
    *,
    open_tick: int,
    high_tick: int,
    low_tick: int,
    close_tick: int,
) -> tuple[OrderBlockCandle, ...]:
    index = candles[-1].index + 1
    return (*candles, _candle(index, open_tick=open_tick, high_tick=high_tick, low_tick=low_tick, close_tick=close_tick))


def test_01_bullish_exact_one_tick_break_forms() -> None:
    result = _valid()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.blocks[0].direction is SMCV2Direction.BULLISH


def test_02_bearish_exact_one_tick_break_forms() -> None:
    result = _valid(SMCV2Direction.BEARISH)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.blocks[0].direction is SMCV2Direction.BEARISH


def test_03_bos_and_choch_share_rules() -> None:
    candles, swings, _ = _market()
    assert _analyze(candles, swings, (_event(swings[0], event_type=DealingRangeEventType.CHOCH),)).blocks


def test_04_empty_event_near_miss_is_none() -> None:
    candles, swings, _ = _market()
    candles = (*candles[:-1], _candle(14, open_tick=106, high_tick=112, low_tick=105, close_tick=110))
    assert _analyze(candles, swings, ()).status is SMCV2PrimitiveStatus.NONE


def test_05_present_event_without_break_is_invalid() -> None:
    candles, swings, events = _market()
    candles = (*candles[:-1], _candle(14, open_tick=106, high_tick=112, low_tick=105, close_tick=110))
    assert _analyze(candles, swings, events).status is SMCV2PrimitiveStatus.INVALID


def test_06_swing_must_precede_displacement() -> None:
    candles, _, _ = _market()
    swing = _swing(source_index=11, confirmation_index=14)
    assert _analyze(candles, (swing,), (_event(swing),)).status is SMCV2PrimitiveStatus.INVALID


def test_07_event_provenance_is_contiguous_and_ends_at_confirmation() -> None:
    candles, swings, _ = _market(displacement_indices=(12, 13, 14))
    result = _analyze(candles, swings, (_event(swings[0], source_indices=(12, 13, 14)),))
    assert result.status is SMCV2PrimitiveStatus.VALID


def test_08_dangling_event_identity_is_invalid() -> None:
    candles, swings, events = _market()
    broken = DealingRangeStructureEvent(
        events[0].direction, events[0].event_type, _SWING_B, events[0].provenance, events[0].event_id
    )
    assert _analyze(candles, swings, (broken,)).status is SMCV2PrimitiveStatus.INVALID


def test_09_longest_provenance_suffix_selected() -> None:
    result = _analyze(*_market(displacement_indices=(12, 13, 14)))
    assert result.blocks[0].displacement_indices == (12, 13, 14)


def test_10_wrong_color_member_rejects_long_suffix() -> None:
    candles, swings, events = _market(displacement_indices=(12, 13, 14))
    changed = list(candles)
    changed[12] = _candle(12, open_tick=106, high_tick=107, low_tick=103, close_tick=104)
    result = _analyze(tuple(changed), swings, events)
    assert result.blocks[0].displacement_indices in ((13, 14), (14,))


def test_11_ratio_exactly_point_six_qualifies() -> None:
    candles, swings, events = _market()
    candles = (*candles[:-1], _candle(14, open_tick=105, high_tick=111, low_tick=101, close_tick=111))
    assert _analyze(candles, swings, events).blocks


def test_12_ratio_below_point_six_fails() -> None:
    candles, swings, events = _market()
    candles = (*candles[:-1], _candle(14, open_tick=106, high_tick=116, low_tick=100, close_tick=111))
    assert not _analyze(candles, swings, events).blocks


def test_13_one_member_may_qualify_multi_candle_sequence() -> None:
    result = _analyze(*_market(displacement_indices=(13, 14)))
    assert result.blocks[0].displacement_indices == (13, 14)


def test_14_nine_history_unknown_ten_qualifies() -> None:
    assert _analyze(*_history_market(9)).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _analyze(*_history_market(10)).status is SMCV2PrimitiveStatus.VALID


@pytest.mark.parametrize(
    ("history", "bodies", "displacement_body", "expected"),
    (
        (
            19,
            (1,) * 9 + tuple(range(2, 12)),
            3,
            SMCV2PrimitiveStatus.VALID,
        ),
        (
            25,
            (0,) * 5 + (9,) * 10 + (1,) * 10,
            3,
            SMCV2PrimitiveStatus.NONE,
        ),
    ),
)
def test_15_median_window_is_bounded_to_twenty(
    history: int,
    bodies: tuple[int, ...],
    displacement_body: int,
    expected: SMCV2PrimitiveStatus,
) -> None:
    result = _analyze(
        *_history_market(
            history,
            baseline_bodies=bodies,
            displacement_body=displacement_body,
        )
    )
    assert result.status is expected


@pytest.mark.parametrize(
    ("bodies", "displacement_body"),
    (
        (tuple(range(1, 11)), 6),
        (tuple(range(1, 12)), 6),
    ),
)
def test_16_even_and_odd_medians_are_exact(
    bodies: tuple[int, ...],
    displacement_body: int,
) -> None:
    result = _analyze(
        *_history_market(
            len(bodies),
            baseline_bodies=bodies,
            displacement_body=displacement_body,
        )
    )
    assert result.status is SMCV2PrimitiveStatus.VALID


def test_17_median_equality_qualifies() -> None:
    equal = _history_market(11, baseline_bodies=(1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12), displacement_body=7)
    below_half = _history_market(10, baseline_bodies=(1, 2, 3, 4, 7, 8, 9, 10, 11, 12), displacement_body=7)
    assert _analyze(*equal).status is SMCV2PrimitiveStatus.VALID
    assert _analyze(*below_half).status is SMCV2PrimitiveStatus.NONE


@pytest.mark.parametrize(
    ("precision", "bodies", "displacement_body"),
    (
        (2, (0, 0, 0, 0, 0, 0, 0, 0, 1, 1), 7),
        (
            2,
            (
                10**80 - 3,
                1,
                10**80 - 2,
                10**80 - 1,
                10**80,
                10**80 + 1,
                10**80 + 2,
                10**80 + 3,
                10**80 + 4,
                10**80 + 5,
            ),
            10**80 + 1,
        ),
        (
            50,
            (
                10**80 - 3,
                1,
                10**80 - 2,
                10**80 - 1,
                10**80,
                10**80 + 1,
                10**80 + 2,
                10**80 + 3,
                10**80 + 4,
                10**80 + 5,
            ),
            10**80 + 1,
        ),
    ),
)
def test_18_decimal_context_does_not_change_result(
    precision: int,
    bodies: tuple[int, ...],
    displacement_body: int,
) -> None:
    with localcontext() as context:
        context.prec = precision
        result = _analyze(
            *_history_market(
                10,
                baseline_bodies=bodies,
                displacement_body=displacement_body,
            )
        )
        assert result.status is SMCV2PrimitiveStatus.VALID


@pytest.mark.parametrize("mutation", ("skipped", "timestamp"))
def test_19_non_suffix_cannot_be_selected(mutation: str) -> None:
    candles, swings, events = _market(displacement_indices=(12, 13, 14))
    result = _analyze(*_market(displacement_indices=(12, 13, 14)))
    assert result.blocks[0].displacement_indices == (12, 13, 14)
    event = events[0]
    if mutation == "skipped":
        forged = object.__new__(SMCV2EventProvenance)
        object.__setattr__(forged, "source_indices", (12, 14))
        object.__setattr__(forged, "source_timestamps", (_time(12), _time(14)))
        object.__setattr__(forged, "confirmation_index", 14)
        object.__setattr__(forged, "confirmation_timestamp", _time(14))
    else:
        forged = object.__new__(SMCV2EventProvenance)
        object.__setattr__(forged, "source_indices", (12, 13, 14))
        object.__setattr__(forged, "source_timestamps", (_time(12), _time(13), _time(15)))
        object.__setattr__(forged, "confirmation_index", 14)
        object.__setattr__(forged, "confirmation_timestamp", _time(14))
    bad = DealingRangeStructureEvent(
        event.direction, event.event_type, event.broken_swing_id, forged, event.event_id
    )
    assert _analyze(candles, swings, (bad,)).status is SMCV2PrimitiveStatus.INVALID


def test_20_baseline_precedes_displacement() -> None:
    block = _valid().blocks[0]
    assert block.displacement_indices[0] > block.source_candle_index
    assert block.source_candle_index == 13


def test_21_bullish_selects_latest_bearish_source() -> None:
    assert _valid().blocks[0].source_candle_index == 13


def test_22_bearish_selects_latest_bullish_source() -> None:
    assert _valid(SMCV2Direction.BEARISH).blocks[0].source_candle_index == 13


def test_23_doji_is_not_source() -> None:
    candles, swings, events = _market()
    changed = list(candles)
    changed[12] = _candle(12, open_tick=104, high_tick=105, low_tick=100, close_tick=101)
    changed[13] = _candle(13, open_tick=102, high_tick=104, low_tick=100, close_tick=102)
    assert _analyze(tuple(changed), swings, events).blocks[0].source_candle_index == 12


def test_24_no_opposite_source_emits_none() -> None:
    candles, swings, events = _market()
    changed = list(candles)
    changed[13] = _candle(13)
    assert _analyze(tuple(changed), swings, events).status is SMCV2PrimitiveStatus.NONE


def test_25_wick_and_body_boundaries_are_exact() -> None:
    block = _valid().blocks[0]
    assert (block.wick_low_tick, block.wick_high_tick, block.body_low_tick, block.body_high_tick) == (100, 105, 101, 104)


def test_26_proximal_distal_are_directional() -> None:
    bull = _valid().blocks[0]
    bear = _valid(SMCV2Direction.BEARISH).blocks[0]
    assert (bull.proximal_tick, bull.distal_tick) == (105, 100)
    assert (bear.proximal_tick, bear.distal_tick) == (95, 100)


def test_27_midpoint_is_exact_for_large_and_negative_ticks() -> None:
    kwargs = _block_id_kwargs(_valid().blocks[0])
    kwargs["wick_boundaries"] = SMCV2TickRange(-10**50, 10**50 + 1)
    kwargs["body_boundaries"] = kwargs["wick_boundaries"]
    kwargs["proximal_tick"] = 10**50 + 1
    kwargs["distal_tick"] = -10**50
    kwargs["midpoint_tick"] = Decimal("0.5")
    assert len(make_order_block_id(**kwargs)) == 64


def test_28_formation_emits_detected_transition_snapshot() -> None:
    result = _valid()
    assert result.transitions[0].from_state is None
    assert result.transitions[0].to_state is OrderBlockState.DETECTED
    assert result.snapshots[0].state is OrderBlockState.DETECTED


def test_29_first_later_candle_activates_before_deeper_state() -> None:
    candles, swings, events = _market()
    result = _analyze(_append(candles, open_tick=107, high_tick=108, low_tick=105, close_tick=106), swings, events)
    assert [t.to_state for t in result.transitions][-1] is OrderBlockState.TOUCHED
    assert OrderBlockState.ACTIVE in [t.to_state for t in result.transitions]


@pytest.mark.parametrize(
    ("low_tick", "close_tick", "expected"),
    (
        (105, 106, OrderBlockState.TOUCHED),
        (104, 105, OrderBlockState.PARTIALLY_MITIGATED),
        (102, 103, OrderBlockState.MITIGATED),
        (100, 101, OrderBlockState.FULLY_TRAVERSED),
        (99, 99, OrderBlockState.INVALIDATED),
    ),
)
def test_30_bullish_lifecycle_depths(
    low_tick: int,
    close_tick: int,
    expected: OrderBlockState,
) -> None:
    result = _lifecycle_result(
        SMCV2Direction.BULLISH,
        open_tick=max(close_tick, low_tick + 1),
        high_tick=max(close_tick, low_tick + 1) + 1,
        low_tick=low_tick,
        close_tick=close_tick,
    )
    assert result.snapshots[-1].state is expected


@pytest.mark.parametrize(
    ("high_tick", "close_tick", "expected"),
    (
        (95, 94, OrderBlockState.TOUCHED),
        (96, 95, OrderBlockState.PARTIALLY_MITIGATED),
        (98, 97, OrderBlockState.MITIGATED),
        (100, 99, OrderBlockState.FULLY_TRAVERSED),
        (101, 101, OrderBlockState.INVALIDATED),
    ),
)
def test_31_bearish_lifecycle_is_mirrored(
    high_tick: int,
    close_tick: int,
    expected: OrderBlockState,
) -> None:
    result = _lifecycle_result(
        SMCV2Direction.BEARISH,
        open_tick=min(close_tick, high_tick - 1),
        high_tick=high_tick,
        low_tick=min(close_tick, high_tick - 1) - 1,
        close_tick=close_tick,
    )
    assert result.snapshots[-1].state is expected


def test_32_close_through_invalidates_boundary_equal_does_not() -> None:
    candles, swings, events = _market()
    equal = _analyze(_append(candles, open_tick=102, high_tick=104, low_tick=99, close_tick=100), swings, events)
    through = _analyze(_append(candles, open_tick=102, high_tick=104, low_tick=98, close_tick=99), swings, events)
    assert equal.snapshots[-1].state is OrderBlockState.FULLY_TRAVERSED
    assert through.snapshots[-1].state is OrderBlockState.INVALIDATED


def test_33_invalidation_has_same_candle_precedence() -> None:
    candles, swings, events = _market()
    result = _analyze(_append(candles, open_tick=103, high_tick=104, low_tick=90, close_tick=90), swings, events)
    assert result.snapshots[-1].state is OrderBlockState.INVALIDATED
    progressed = _append(candles, open_tick=106, high_tick=107, low_tick=102, close_tick=104)
    progressed = _append(progressed, open_tick=106, high_tick=107, low_tick=105, close_tick=106)
    no_regression = _analyze(progressed, swings, events)
    assert no_regression.snapshots[-1].state is OrderBlockState.MITIGATED


def test_34_terminal_and_no_expiry_rules() -> None:
    candles, swings, events = _market()
    invalidated = _append(candles, open_tick=103, high_tick=104, low_tick=90, close_tick=90)
    terminal = _analyze(
        _append(invalidated, open_tick=106, high_tick=107, low_tick=105, close_tick=106),
        swings,
        events,
    )
    assert terminal.snapshots[-1].state is OrderBlockState.INVALIDATED
    assert len(terminal.transitions) == 3
    quiet = candles
    for _ in range(25):
        quiet = _append(quiet, open_tick=107, high_tick=108, low_tick=106, close_tick=107)
    preserved = _analyze(quiet, swings, events)
    assert preserved.blocks[0] == _valid().blocks[0]
    assert preserved.snapshots[-1].state is OrderBlockState.ACTIVE


@pytest.mark.parametrize("slot", ("candles", "swings", "events"))
def test_35_missing_top_level_is_unknown(slot: str) -> None:
    candles, swings, events = _market()
    values = {"candles": candles, "swings": swings, "events": events}
    values[slot] = None
    assert _analyze(values["candles"], values["swings"], values["events"]).status is SMCV2PrimitiveStatus.UNKNOWN


@pytest.mark.parametrize("kind", ("list", "bool_tick", "naive_time", "missing_field"))
def test_36_malformed_inputs_fail_closed(kind: str) -> None:
    candles, swings, events = _market()
    if kind == "list":
        supplied = list(candles)  # type: ignore[assignment]
    elif kind == "bool_tick":
        supplied = (_candle(0, open_tick=True), *candles[1:])
    elif kind == "naive_time":
        supplied = (_candle(0, timestamp=datetime(2026, 1, 1)), *candles[1:])
    else:
        malformed = object.__new__(OrderBlockCandle)
        object.__setattr__(malformed, "index", 0)
        object.__setattr__(malformed, "timestamp", _time(0))
        supplied = (malformed, *candles[1:])
    assert _analyze(supplied, swings, events).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[arg-type]


@pytest.mark.parametrize("kind", ("candle_order", "swing_price", "duplicate_swing"))
def test_37_non_increasing_candles_are_invalid(kind: str) -> None:
    candles, swings, events = _market()
    supplied_candles = candles
    supplied_swings = swings
    if kind == "candle_order":
        supplied_candles = (candles[1], candles[0], *candles[2:])
    elif kind == "swing_price":
        supplied_swings = (
            DealingRangeSwing(swings[0].side, 109, swings[0].provenance, swings[0].swing_id),
        )
    else:
        supplied_swings = (swings[0], swings[0])
    assert _analyze(supplied_candles, supplied_swings, events).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("kind", ("duplicate", "noncontiguous", "timestamp_mismatch"))
def test_38_duplicate_events_are_invalid(kind: str) -> None:
    candles, swings, events = _market()
    if kind == "duplicate":
        supplied = (events[0], events[0])
    else:
        provenance = object.__new__(SMCV2EventProvenance)
        object.__setattr__(provenance, "source_indices", (12, 14) if kind == "noncontiguous" else (14,))
        object.__setattr__(
            provenance,
            "source_timestamps",
            (_time(12), _time(14)) if kind == "noncontiguous" else (_time(13),),
        )
        object.__setattr__(provenance, "confirmation_index", 14)
        object.__setattr__(provenance, "confirmation_timestamp", _time(14))
        supplied = (
            DealingRangeStructureEvent(
                events[0].direction,
                events[0].event_type,
                events[0].broken_swing_id,
                provenance,
                events[0].event_id,
            ),
        )
    assert _analyze(candles, swings, supplied).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("later_invalid", (False, True))
def test_39_distinct_same_group_candidates_are_ambiguous(
    later_invalid: bool,
) -> None:
    candles, swings, events = _market()
    changed = list(candles)
    changed[6] = _candle(6, open_tick=104, high_tick=109, low_tick=102, close_tick=105)
    swing_b = DealingRangeSwing(
        DealingRangeSwingSide.HIGH,
        109,
        SMCV2EventProvenance(
            source_indices=(6,),
            source_timestamps=(_time(6),),
            confirmation_index=8,
            confirmation_timestamp=_time(8),
        ),
        _SWING_B,
    )
    event_b = _event(swing_b)
    ordered_events = tuple(sorted((events[0], event_b), key=lambda item: item.event_id))
    supplied = tuple(changed)
    expected = SMCV2PrimitiveStatus.AMBIGUOUS
    if later_invalid:
        supplied = _append(
            supplied, open_tick=106, high_tick=108, low_tick=106, close_tick=107
        )
        supplied = (
            *supplied,
            _candle(16, open_tick=100, high_tick=99, low_tick=98, close_tick=100),
        )
        expected = SMCV2PrimitiveStatus.INVALID
    result = _analyze(supplied, (swings[0], swing_b), ordered_events)
    assert result.status is expected
    assert not result.blocks
    assert not result.transitions
    assert not result.snapshots


@pytest.mark.parametrize(
    "failure_kind",
    ("candle", "swing", "unknown_moment", "unknown_then_invalid"),
)
def test_40_later_invalid_group_preserves_prior_evidence(failure_kind: str) -> None:
    candles, swings, events = (
        _history_market(9) if failure_kind == "unknown_then_invalid" else _market()
    )
    candles = _append(candles, open_tick=106, high_tick=108, low_tick=106, close_tick=107)
    if failure_kind == "candle":
        bad_candle = _candle(
            16, open_tick=100, high_tick=99, low_tick=98, close_tick=100
        )
        result = _analyze((*candles, bad_candle), swings, events)
    elif failure_kind == "swing":
        candles = _append(
            candles, open_tick=108, high_tick=111, low_tick=107, close_tick=110
        )
        bad_swing = DealingRangeSwing(
            side=DealingRangeSwingSide.HIGH,
            price_tick=112,
            provenance=SMCV2EventProvenance(
                source_indices=(14,),
                source_timestamps=(_time(14),),
                confirmation_index=16,
                confirmation_timestamp=_time(16),
            ),
            swing_id=_SWING_B,
        )
        result = _analyze(candles, (*swings, bad_swing), events)
    elif failure_kind == "unknown_moment":
        bad_swing = object.__new__(DealingRangeSwing)
        object.__setattr__(bad_swing, "side", DealingRangeSwingSide.HIGH)
        object.__setattr__(bad_swing, "price_tick", 112)
        object.__setattr__(bad_swing, "provenance", object())
        object.__setattr__(bad_swing, "swing_id", _SWING_B)
        result = _analyze(candles, (*swings, bad_swing), events)
    else:
        result = _analyze(
            (
                *candles,
                _candle(11, open_tick=100, high_tick=99, low_tick=98, close_tick=100),
            ),
            swings,
            events,
        )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    if failure_kind in ("unknown_moment", "unknown_then_invalid"):
        assert not result.blocks
    else:
        assert len(result.blocks) == 1
        assert all(transition.index < 16 for transition in result.transitions)


def _block_id_kwargs(block: OrderBlock) -> dict[str, object]:
    return {
        "identity_kind": "BLOCK", "instrument": "GC", "timeframe": "M5",
        "direction": block.direction, "source_candle_index": block.source_candle_index,
        "source_candle_timestamp": block.source_candle_timestamp,
        "source_swing_id": block.source_swing_id,
        "displacement_indices": block.displacement_indices,
        "displacement_timestamps": block.displacement_timestamps,
        "structure_event_id": block.structure_event_id,
        "structure_event_type": block.structure_event_type,
        "wick_boundaries": SMCV2TickRange(block.wick_low_tick, block.wick_high_tick),
        "body_boundaries": SMCV2TickRange(block.body_low_tick, block.body_high_tick),
        "proximal_tick": block.proximal_tick, "distal_tick": block.distal_tick,
        "midpoint_tick": block.midpoint_tick, "detection_index": block.detection_index,
        "detection_timestamp": block.detection_timestamp,
    }


def _transition_id_kwargs(
    block: OrderBlock,
    transition: OrderBlockTransition,
) -> dict[str, object]:
    return {
        "identity_kind": "TRANSITION",
        "instrument": "GC",
        "timeframe": "M5",
        "direction": block.direction,
        "block_id": block.block_id,
        "from_state": transition.from_state,
        "to_state": transition.to_state,
        "effective_index": transition.index,
        "effective_timestamp": transition.timestamp,
        "reason": transition.reason,
    }


def _snapshot_id_kwargs(
    block: OrderBlock,
    snapshot: OrderBlockSnapshot,
) -> dict[str, object]:
    return {
        "identity_kind": "SNAPSHOT",
        "instrument": "GC",
        "timeframe": "M5",
        "direction": block.direction,
        "block_id": block.block_id,
        "state": snapshot.state,
        "effective_index": snapshot.index,
        "effective_timestamp": snapshot.timestamp,
        "transition_ids": snapshot.transition_ids,
    }


@pytest.mark.parametrize("variant", ("reproduce", "sensitive", "forbidden", "required"))
def test_41_block_identity_reproduces(variant: str) -> None:
    block = _valid().blocks[0]
    kwargs = _block_id_kwargs(block)
    if variant == "reproduce":
        assert make_order_block_id(**kwargs) == block.block_id
    elif variant == "sensitive":
        alternatives = []
        for field_name, value in (
            ("instrument", "SI"),
            ("timeframe", "M15"),
            ("source_candle_index", block.source_candle_index - 1),
            ("source_candle_timestamp", block.source_candle_timestamp - timedelta(minutes=1)),
            ("source_swing_id", _SWING_B),
            ("structure_event_id", "c" * 64),
            ("structure_event_type", DealingRangeEventType.CHOCH),
            ("body_boundaries", SMCV2TickRange(block.body_low_tick - 1, block.body_high_tick)),
        ):
            changed = dict(kwargs)
            changed[field_name] = value
            alternatives.append(changed)
        changed = dict(kwargs)
        changed.update(
            direction=SMCV2Direction.BEARISH,
            proximal_tick=block.distal_tick,
            distal_tick=block.proximal_tick,
        )
        alternatives.append(changed)
        changed = dict(kwargs)
        changed.update(
            source_candle_index=block.source_candle_index - 1,
            source_candle_timestamp=block.source_candle_timestamp - timedelta(minutes=1),
            displacement_indices=(block.detection_index - 1, block.detection_index),
            displacement_timestamps=(
                block.detection_timestamp - timedelta(minutes=5),
                block.detection_timestamp,
            ),
        )
        alternatives.append(changed)
        changed = dict(kwargs)
        shifted_detection = block.detection_timestamp + timedelta(seconds=1)
        changed.update(
            displacement_timestamps=(shifted_detection,),
            detection_timestamp=shifted_detection,
        )
        alternatives.append(changed)
        changed = dict(kwargs)
        changed.update(
            wick_boundaries=SMCV2TickRange(
                block.wick_low_tick - 1, block.wick_high_tick
            ),
            proximal_tick=block.wick_high_tick,
            distal_tick=block.wick_low_tick - 1,
            midpoint_tick=Decimal(block.wick_low_tick + block.wick_high_tick - 1)
            / Decimal(2),
        )
        alternatives.append(changed)
        for changed in alternatives:
            assert make_order_block_id(**changed) != block.block_id
    elif variant == "forbidden":
        forbidden = {
            "block_id": block.block_id,
            "from_state": OrderBlockState.DETECTED,
            "to_state": OrderBlockState.ACTIVE,
            "effective_index": block.detection_index,
            "effective_timestamp": block.detection_timestamp,
            "reason": "FIRST_ELIGIBLE_BAR",
            "state": OrderBlockState.DETECTED,
            "transition_ids": ("d" * 64,),
        }
        for field_name, value in forbidden.items():
            changed = dict(kwargs)
            changed[field_name] = value
            with pytest.raises(ValueError):
                make_order_block_id(**changed)
    else:
        defaults = {
            "source_candle_index": None,
            "source_candle_timestamp": None,
            "source_swing_id": None,
            "displacement_indices": (),
            "displacement_timestamps": (),
            "structure_event_id": None,
            "structure_event_type": None,
            "wick_boundaries": None,
            "body_boundaries": None,
            "proximal_tick": None,
            "distal_tick": None,
            "midpoint_tick": None,
            "detection_index": None,
            "detection_timestamp": None,
        }
        for field_name, value in defaults.items():
            changed = dict(kwargs)
            changed[field_name] = value
            with pytest.raises((TypeError, ValueError)):
                make_order_block_id(**changed)


@pytest.mark.parametrize(
    "variant",
    (
        "reproduce",
        "allowed_edges",
        "impossible_edges",
        "transition_required",
        "transition_forbidden",
        "snapshot_required",
        "snapshot_forbidden",
        "snapshot_sensitive",
        "malformed_hashes",
    ),
)
def test_42_transition_and_snapshot_identities_reproduce(variant: str) -> None:
    result = _valid()
    block, transition, snapshot = result.blocks[0], result.transitions[0], result.snapshots[0]
    transition_kwargs = _transition_id_kwargs(block, transition)
    snapshot_kwargs = _snapshot_id_kwargs(block, snapshot)
    if variant == "reproduce":
        assert make_order_block_id(**transition_kwargs) == transition.transition_id
        assert make_order_block_id(**snapshot_kwargs) == snapshot.snapshot_id
    elif variant == "allowed_edges":
        reason_for = {
            OrderBlockState.TOUCHED: "WICK_TOUCHED",
            OrderBlockState.PARTIALLY_MITIGATED: "PARTIAL_MITIGATION",
            OrderBlockState.MITIGATED: "MIDPOINT_MITIGATION",
            OrderBlockState.FULLY_TRAVERSED: "DISTAL_TRAVERSAL",
            OrderBlockState.INVALIDATED: "CLOSE_THROUGH_INVALIDATION",
        }
        edges = [
            (None, OrderBlockState.DETECTED, "FORMATION_CONFIRMED"),
            (
                OrderBlockState.DETECTED,
                OrderBlockState.ACTIVE,
                "FIRST_ELIGIBLE_BAR",
            ),
        ]
        depth = (
            OrderBlockState.ACTIVE,
            OrderBlockState.TOUCHED,
            OrderBlockState.PARTIALLY_MITIGATED,
            OrderBlockState.MITIGATED,
            OrderBlockState.FULLY_TRAVERSED,
        )
        for position, from_state in enumerate(depth):
            for to_state in depth[position + 1 :]:
                edges.append((from_state, to_state, reason_for[to_state]))
            edges.append(
                (
                    from_state,
                    OrderBlockState.INVALIDATED,
                    reason_for[OrderBlockState.INVALIDATED],
                )
            )
        for from_state, to_state, reason in edges:
            changed = dict(transition_kwargs)
            changed.update(from_state=from_state, to_state=to_state, reason=reason)
            assert len(make_order_block_id(**changed)) == 64
    elif variant == "impossible_edges":
        impossible = (
            (None, OrderBlockState.ACTIVE, "FIRST_ELIGIBLE_BAR"),
            (
                OrderBlockState.ACTIVE,
                OrderBlockState.DETECTED,
                "FORMATION_CONFIRMED",
            ),
            (
                OrderBlockState.MITIGATED,
                OrderBlockState.TOUCHED,
                "WICK_TOUCHED",
            ),
            (
                OrderBlockState.FULLY_TRAVERSED,
                OrderBlockState.MITIGATED,
                "MIDPOINT_MITIGATION",
            ),
            (
                OrderBlockState.INVALIDATED,
                OrderBlockState.FULLY_TRAVERSED,
                "DISTAL_TRAVERSAL",
            ),
            (
                OrderBlockState.ACTIVE,
                OrderBlockState.TOUCHED,
                "NOT_LOCKED",
            ),
        )
        for from_state, to_state, reason in impossible:
            changed = dict(transition_kwargs)
            changed.update(from_state=from_state, to_state=to_state, reason=reason)
            with pytest.raises(ValueError):
                make_order_block_id(**changed)
    elif variant == "transition_required":
        for field_name, value in (
            ("block_id", None),
            ("to_state", None),
            ("effective_index", None),
            ("effective_timestamp", None),
            ("reason", None),
        ):
            changed = dict(transition_kwargs)
            changed[field_name] = value
            with pytest.raises((TypeError, ValueError)):
                make_order_block_id(**changed)
    elif variant == "transition_forbidden":
        block_fields = _block_id_kwargs(block)
        for field_name in (
            "source_candle_index",
            "source_candle_timestamp",
            "source_swing_id",
            "displacement_indices",
            "displacement_timestamps",
            "structure_event_id",
            "structure_event_type",
            "wick_boundaries",
            "body_boundaries",
            "proximal_tick",
            "distal_tick",
            "midpoint_tick",
            "detection_index",
            "detection_timestamp",
        ):
            changed = dict(transition_kwargs)
            changed[field_name] = block_fields[field_name]
            with pytest.raises(ValueError):
                make_order_block_id(**changed)
        for field_name, value in (
            ("state", OrderBlockState.DETECTED),
            ("transition_ids", (transition.transition_id,)),
        ):
            changed = dict(transition_kwargs)
            changed[field_name] = value
            with pytest.raises(ValueError):
                make_order_block_id(**changed)
    elif variant == "snapshot_required":
        for field_name, value in (
            ("block_id", None),
            ("state", None),
            ("effective_index", None),
            ("effective_timestamp", None),
            ("transition_ids", ()),
        ):
            changed = dict(snapshot_kwargs)
            changed[field_name] = value
            with pytest.raises((TypeError, ValueError)):
                make_order_block_id(**changed)
    elif variant == "snapshot_forbidden":
        forbidden = _block_id_kwargs(block)
        forbidden.update(
            from_state=OrderBlockState.DETECTED,
            to_state=OrderBlockState.ACTIVE,
            reason="FIRST_ELIGIBLE_BAR",
        )
        for field_name, value in forbidden.items():
            if field_name in ("identity_kind", "instrument", "timeframe", "direction"):
                continue
            changed = dict(snapshot_kwargs)
            changed[field_name] = value
            with pytest.raises(ValueError):
                make_order_block_id(**changed)
    elif variant == "snapshot_sensitive":
        original = make_order_block_id(**snapshot_kwargs)
        alternatives = []
        for field_name, value in (
            ("instrument", "SI"),
            ("timeframe", "M15"),
            ("direction", SMCV2Direction.BEARISH),
            ("block_id", "e" * 64),
            ("state", OrderBlockState.ACTIVE),
            ("effective_index", snapshot.index + 1),
            ("effective_timestamp", snapshot.timestamp + timedelta(seconds=1)),
            (
                "transition_ids",
                (*snapshot.transition_ids, "f" * 64),
            ),
        ):
            changed = dict(snapshot_kwargs)
            changed[field_name] = value
            alternatives.append(changed)
        assert all(make_order_block_id(**changed) != original for changed in alternatives)
    else:
        for target_kwargs, field_name, value in (
            (transition_kwargs, "block_id", "bad"),
            (snapshot_kwargs, "block_id", "bad"),
            (snapshot_kwargs, "transition_ids", ("bad",)),
            (
                snapshot_kwargs,
                "transition_ids",
                (transition.transition_id, transition.transition_id),
            ),
        ):
            changed = dict(target_kwargs)
            changed[field_name] = value
            with pytest.raises(ValueError):
                make_order_block_id(**changed)


def test_43_public_contract_is_exact_and_frozen() -> None:
    assert ORDER_BLOCK_DETECTOR_VERSION == "SMC-V2-ORDER-BLOCK-1"
    analyzer_signature = inspect.signature(analyze_order_blocks)
    builder_signature = inspect.signature(make_order_block_id)
    assert list(analyzer_signature.parameters) == [
        "instrument",
        "timeframe",
        "candles",
        "swings",
        "structure_events",
    ]
    builder_names = [
        "identity_kind", "instrument", "timeframe", "direction",
        "source_candle_index", "source_candle_timestamp", "source_swing_id",
        "displacement_indices", "displacement_timestamps", "structure_event_id",
        "structure_event_type", "wick_boundaries", "body_boundaries",
        "proximal_tick", "distal_tick", "midpoint_tick", "detection_index",
        "detection_timestamp", "block_id", "from_state", "to_state",
        "effective_index", "effective_timestamp", "reason", "state",
        "transition_ids",
    ]
    assert list(builder_signature.parameters) == builder_names
    assert {
        name: parameter.default
        for name, parameter in builder_signature.parameters.items()
    } == {
        "identity_kind": inspect.Parameter.empty,
        "instrument": inspect.Parameter.empty,
        "timeframe": inspect.Parameter.empty,
        "direction": inspect.Parameter.empty,
        "source_candle_index": None,
        "source_candle_timestamp": None,
        "source_swing_id": None,
        "displacement_indices": (),
        "displacement_timestamps": (),
        "structure_event_id": None,
        "structure_event_type": None,
        "wick_boundaries": None,
        "body_boundaries": None,
        "proximal_tick": None,
        "distal_tick": None,
        "midpoint_tick": None,
        "detection_index": None,
        "detection_timestamp": None,
        "block_id": None,
        "from_state": None,
        "to_state": None,
        "effective_index": None,
        "effective_timestamp": None,
        "reason": None,
        "state": None,
        "transition_ids": (),
    }
    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in analyzer_signature.parameters.values()
    )
    assert [field.name for field in fields(OrderBlockCandle)] == ["index", "timestamp", "open_tick", "high_tick", "low_tick", "close_tick"]
    assert [field.name for field in fields(OrderBlock)] == [
        "block_id", "direction", "source_candle_index", "source_candle_timestamp",
        "source_swing_id", "displacement_indices", "displacement_timestamps",
        "structure_event_id", "structure_event_type", "wick_low_tick",
        "wick_high_tick", "body_low_tick", "body_high_tick", "proximal_tick",
        "distal_tick", "midpoint_tick", "detection_index", "detection_timestamp",
    ]
    assert [field.name for field in fields(OrderBlockTransition)] == [
        "transition_id",
        "block_id",
        "from_state",
        "to_state",
        "index",
        "timestamp",
        "reason",
    ]
    assert [field.name for field in fields(OrderBlockSnapshot)] == [
        "snapshot_id",
        "block_id",
        "direction",
        "state",
        "index",
        "timestamp",
        "transition_ids",
    ]
    assert [field.name for field in fields(OrderBlockResult)] == [
        "status",
        "blocks",
        "transitions",
        "snapshots",
        "reasons",
        "blocking_reasons",
    ]
    assert [state.value for state in OrderBlockState] == [
        "DETECTED", "ACTIVE", "TOUCHED", "PARTIALLY_MITIGATED", "MITIGATED",
        "FULLY_TRAVERSED", "INVALIDATED",
    ]
    assert order_block_module.__all__ == [
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
    result = _valid()
    public_types_and_instances = (
        (OrderBlockCandle, _market()[0][0]),
        (OrderBlock, result.blocks[0]),
        (OrderBlockTransition, result.transitions[0]),
        (OrderBlockSnapshot, result.snapshots[0]),
        (OrderBlockResult, result),
    )
    for public_type, instance in public_types_and_instances:
        assert public_type.__dataclass_params__.frozen is True
        first_field = fields(instance)[0].name
        with pytest.raises(FrozenInstanceError):
            setattr(instance, first_field, getattr(instance, first_field))
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in builder_signature.parameters.values()
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in analyzer_signature.parameters.values()
    )


def test_44_standalone_scope_and_full_contract() -> None:
    first = _valid()
    repeated = _valid()
    assert first == repeated
    candles, swings, events = _market()
    longer = _analyze(
        _append(candles, open_tick=107, high_tick=108, low_tick=106, close_tick=107),
        swings,
        events,
    )
    assert longer.blocks[: len(first.blocks)] == first.blocks
    assert longer.transitions[: len(first.transitions)] == first.transitions
    assert longer.snapshots[: len(first.snapshots)] == first.snapshots
    same_effective = _analyze((*candles, candles[-1]), swings, events)
    assert same_effective.status is SMCV2PrimitiveStatus.INVALID
    multi_candles = _append(
        candles, open_tick=105, high_tick=106, low_tick=100, close_tick=101
    )
    multi_candles = _append(
        multi_candles, open_tick=104, high_tick=113, low_tick=103, close_tick=111
    )
    later_event = _event(swings[0], source_indices=(16,))
    multi = _analyze(multi_candles, swings, (events[0], later_event))
    assert [block.detection_index for block in multi.blocks] == [14, 16]
    tree = ast.parse(Path("smc/order_block.py").read_text(encoding="utf-8"))
    import_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    import_modules.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert import_modules <= {
        "__future__", "dataclasses", "datetime", "decimal", "enum", "hashlib",
        "json", "re", "smc.dealing_range", "smc.smc_v2_primitives",
    }
    assert fields(OrderBlockResult)
