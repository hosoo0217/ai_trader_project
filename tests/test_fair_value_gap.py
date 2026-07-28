from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from enum import Enum
import inspect
from pathlib import Path

import pytest

from smc.dealing_range import DealingRangeEventType
from smc.fair_value_gap import (
    FAIR_VALUE_GAP_DETECTOR_VERSION,
    FairValueGap,
    FairValueGapCandle,
    FairValueGapContextLink,
    FairValueGapResult,
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    analyze_fair_value_gaps,
    make_fair_value_gap_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


_BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
_HASH_A = "a" * 64
_HASH_B = "b" * 64
_HASH_C = "c" * 64


def _time(index: int) -> datetime:
    return _BASE_TIME + timedelta(minutes=5 * index)


def _candle(
    index: int,
    *,
    open_tick: int,
    high_tick: int,
    low_tick: int,
    close_tick: int,
    timestamp: datetime | None = None,
) -> FairValueGapCandle:
    return FairValueGapCandle(
        index=index,
        timestamp=_time(index) if timestamp is None else timestamp,
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
    )


def _bullish_window(
    *,
    lower_tick: int = 102,
    upper_tick: int = 106,
    middle: FairValueGapCandle | None = None,
) -> tuple[FairValueGapCandle, ...]:
    first = _candle(
        0,
        open_tick=lower_tick - 2,
        high_tick=lower_tick,
        low_tick=lower_tick - 3,
        close_tick=lower_tick - 1,
    )
    middle_candle = middle or _candle(
        1,
        open_tick=lower_tick,
        high_tick=upper_tick + 6,
        low_tick=lower_tick - 1,
        close_tick=upper_tick + 5,
    )
    third = _candle(
        2,
        open_tick=upper_tick,
        high_tick=upper_tick + 3,
        low_tick=upper_tick,
        close_tick=upper_tick + 3,
    )
    return (first, middle_candle, third)


def _bearish_window(
    *,
    lower_tick: int = 106,
    upper_tick: int = 110,
) -> tuple[FairValueGapCandle, ...]:
    return (
        _candle(
            0,
            open_tick=upper_tick + 2,
            high_tick=upper_tick + 3,
            low_tick=upper_tick,
            close_tick=upper_tick + 1,
        ),
        _candle(
            1,
            open_tick=upper_tick,
            high_tick=upper_tick + 1,
            low_tick=lower_tick - 6,
            close_tick=lower_tick - 5,
        ),
        _candle(
            2,
            open_tick=lower_tick - 1,
            high_tick=lower_tick,
            low_tick=lower_tick - 3,
            close_tick=lower_tick - 2,
        ),
    )


def _analyze(
    candles: tuple[FairValueGapCandle, ...] | None,
    *,
    context_links: tuple[FairValueGapContextLink, ...] | None = (),
    instrument: str = "GC",
    timeframe: str = "M5",
) -> FairValueGapResult:
    return analyze_fair_value_gaps(
        instrument=instrument,
        timeframe=timeframe,
        candles=candles,
        context_links=context_links,
    )


def _link(
    index: int = 2,
    *,
    timestamp: datetime | None = None,
    displacement_id: str | None = _HASH_A,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
) -> FairValueGapContextLink:
    return FairValueGapContextLink(
        formation_end_index=index,
        formation_end_timestamp=_time(index) if timestamp is None else timestamp,
        displacement_id=displacement_id,
        structure_event_id=structure_event_id,
        structure_event_type=structure_event_type,
    )


def _first_gap(result: FairValueGapResult) -> FairValueGap:
    assert result.gaps
    return result.gaps[0]


def _gap_snapshots(
    result: FairValueGapResult,
    gap_id: str,
) -> tuple[FairValueGapSnapshot, ...]:
    return tuple(snapshot for snapshot in result.snapshots if snapshot.gap_id == gap_id)


def _gap_transitions(
    result: FairValueGapResult,
    gap_id: str,
) -> tuple[FairValueGapTransition, ...]:
    return tuple(
        transition for transition in result.transitions if transition.gap_id == gap_id
    )


def _append(
    candles: tuple[FairValueGapCandle, ...],
    *,
    low_tick: int,
    high_tick: int,
    open_tick: int,
    close_tick: int,
) -> tuple[FairValueGapCandle, ...]:
    index = candles[-1].index + 1
    return (
        *candles,
        _candle(
            index,
            open_tick=open_tick,
            high_tick=high_tick,
            low_tick=low_tick,
            close_tick=close_tick,
        ),
    )


def _gap_identity_kwargs(gap: FairValueGap) -> dict[str, object]:
    return {
        "identity_kind": "GAP",
        "instrument": "GC",
        "timeframe": "M5",
        "direction": gap.direction,
        "source_indices": gap.source_indices,
        "source_timestamps": gap.source_timestamps,
        "boundaries": SMCV2TickRange(gap.lower_tick, gap.upper_tick),
        "midpoint_tick": gap.midpoint_tick,
        "formation_end_index": gap.formation_end_index,
        "formation_end_timestamp": gap.formation_end_timestamp,
        "displacement_id": gap.displacement_id,
        "structure_event_id": gap.structure_event_id,
        "structure_event_type": gap.structure_event_type,
    }


def _transition_identity_kwargs(
    gap: FairValueGap,
    transition: FairValueGapTransition,
) -> dict[str, object]:
    return {
        "identity_kind": "TRANSITION",
        "instrument": "GC",
        "timeframe": "M5",
        "direction": gap.direction,
        "gap_id": gap.gap_id,
        "from_state": transition.from_state,
        "to_state": transition.to_state,
        "effective_index": transition.index,
        "effective_timestamp": transition.timestamp,
        "reason": transition.reason,
    }


def _snapshot_identity_kwargs(
    gap: FairValueGap,
    snapshot: FairValueGapSnapshot,
) -> dict[str, object]:
    return {
        "identity_kind": "SNAPSHOT",
        "instrument": "GC",
        "timeframe": "M5",
        "direction": gap.direction,
        "gap_id": gap.gap_id,
        "effective_index": snapshot.index,
        "effective_timestamp": snapshot.timestamp,
        "state": snapshot.state,
        "transition_ids": snapshot.transition_ids,
    }


def test_01_bullish_exact_two_tick_gap_forms() -> None:
    result = _analyze(_bullish_window(lower_tick=102, upper_tick=104))
    gap = _first_gap(result)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert gap.direction is SMCV2Direction.BULLISH
    assert (gap.lower_tick, gap.upper_tick) == (102, 104)


def test_02_bearish_exact_two_tick_gap_forms() -> None:
    result = _analyze(_bearish_window(lower_tick=108, upper_tick=110))
    gap = _first_gap(result)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert gap.direction is SMCV2Direction.BEARISH
    assert (gap.lower_tick, gap.upper_tick) == (108, 110)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_03_one_tick_near_miss_emits_no_gap(direction: str) -> None:
    candles = (
        _bullish_window(lower_tick=102, upper_tick=103)
        if direction == "bullish"
        else _bearish_window(lower_tick=109, upper_tick=110)
    )
    result = _analyze(candles)
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.gaps == ()


def test_04_middle_body_ratio_exactly_point_six_qualifies() -> None:
    middle = _candle(
        1,
        open_tick=102,
        high_tick=110,
        low_tick=100,
        close_tick=108,
    )
    result = _analyze(_bullish_window(lower_tick=102, upper_tick=104, middle=middle))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.gaps) == 1


@pytest.mark.parametrize(
    "middle",
    [
        _candle(
            1,
            open_tick=102,
            high_tick=110,
            low_tick=100,
            close_tick=107,
        ),
        _candle(
            1,
            open_tick=105,
            high_tick=105,
            low_tick=105,
            close_tick=105,
        ),
    ],
)
def test_05_below_ratio_and_zero_range_do_not_qualify(
    middle: FairValueGapCandle,
) -> None:
    result = _analyze(_bullish_window(lower_tick=102, upper_tick=108, middle=middle))
    assert result.status is SMCV2PrimitiveStatus.NONE


def test_06_nothing_is_knowable_before_third_candle_close() -> None:
    result = _analyze(_bullish_window()[:2])
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.gaps == result.transitions == result.snapshots == ()


def test_07_bullish_boundaries_are_exact_and_immutable() -> None:
    gap = _first_gap(_analyze(_bullish_window(lower_tick=102, upper_tick=106)))
    assert (gap.lower_tick, gap.upper_tick) == (102, 106)
    with pytest.raises(FrozenInstanceError):
        gap.lower_tick = 101  # type: ignore[misc]


def test_08_bearish_boundaries_are_exact_and_immutable() -> None:
    gap = _first_gap(_analyze(_bearish_window(lower_tick=106, upper_tick=110)))
    assert (gap.lower_tick, gap.upper_tick) == (106, 110)
    with pytest.raises(FrozenInstanceError):
        gap.upper_tick = 111  # type: ignore[misc]


def test_09_even_width_has_integer_consequent_encroachment() -> None:
    gap = _first_gap(_analyze(_bullish_window(lower_tick=102, upper_tick=106)))
    assert gap.midpoint_tick == Decimal("104")


@pytest.mark.parametrize(
    ("lower_tick", "upper_tick", "expected"),
    [
        (100, 103, Decimal("101.5")),
        (-5, -2, Decimal("-3.5")),
        (-1, 1, Decimal("0")),
        (10**100, 10**100 + 3, Decimal(f"{10**100 + 1}.5")),
    ],
)
def test_10_odd_negative_zero_and_huge_midpoints_are_exact(
    lower_tick: int,
    upper_tick: int,
    expected: Decimal,
) -> None:
    with localcontext() as context:
        context.prec = 3
        result = _analyze(
            _bullish_window(lower_tick=lower_tick, upper_tick=upper_tick)
        )
    gap = _first_gap(result)
    assert gap.midpoint_tick == expected
    reproduced = make_fair_value_gap_id(
        identity_kind="GAP",
        instrument=" gc ",
        timeframe=" m5 ",
        direction=gap.direction,
        source_indices=gap.source_indices,
        source_timestamps=gap.source_timestamps,
        boundaries=SMCV2TickRange(gap.lower_tick, gap.upper_tick),
        midpoint_tick=Decimal("-0") if expected.is_zero() else expected,
        formation_end_index=gap.formation_end_index,
        formation_end_timestamp=gap.formation_end_timestamp,
    )
    assert reproduced == gap.gap_id


def test_11_formation_emits_active_transition_and_snapshot_only() -> None:
    result = _analyze(_bullish_window())
    gap = _first_gap(result)
    transitions = _gap_transitions(result, gap.gap_id)
    snapshots = _gap_snapshots(result, gap.gap_id)
    assert [(item.from_state, item.to_state) for item in transitions] == [
        (None, FairValueGapState.ACTIVE)
    ]
    assert snapshots[0].state is FairValueGapState.ACTIVE
    assert snapshots[0].index == 2


def test_12_later_bullish_exact_touch() -> None:
    candles = _append(
        _bullish_window(),
        low_tick=106,
        high_tick=109,
        open_tick=108,
        close_tick=107,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert _gap_snapshots(result, gap.gap_id)[-1].state is FairValueGapState.TOUCHED


def test_13_later_bullish_partial_fill() -> None:
    candles = _append(
        _bullish_window(),
        low_tick=105,
        high_tick=109,
        open_tick=108,
        close_tick=107,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert (
        _gap_snapshots(result, gap.gap_id)[-1].state
        is FairValueGapState.PARTIALLY_FILLED
    )


def test_14_later_bullish_midpoint_fill() -> None:
    candles = _append(
        _bullish_window(),
        low_tick=104,
        high_tick=108,
        open_tick=107,
        close_tick=106,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert (
        _gap_snapshots(result, gap.gap_id)[-1].state
        is FairValueGapState.MIDPOINT_FILLED
    )


def test_15_later_bullish_full_fill() -> None:
    candles = _append(
        _bullish_window(),
        low_tick=102,
        high_tick=107,
        open_tick=106,
        close_tick=103,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert (
        _gap_snapshots(result, gap.gap_id)[-1].state
        is FairValueGapState.FULLY_FILLED
    )


def test_16_bullish_close_through_invalidation_has_precedence() -> None:
    candles = _append(
        _bullish_window(),
        low_tick=100,
        high_tick=107,
        open_tick=106,
        close_tick=101,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    transition = _gap_transitions(result, gap.gap_id)[-1]
    assert transition.to_state is FairValueGapState.INVALIDATED
    assert transition.reason == "CLOSE_THROUGH_INVALIDATION"


@pytest.mark.parametrize(
    ("high_tick", "expected"),
    [
        (106, FairValueGapState.TOUCHED),
        (107, FairValueGapState.PARTIALLY_FILLED),
    ],
)
def test_17_bearish_touch_and_partial_mirror_bullish(
    high_tick: int,
    expected: FairValueGapState,
) -> None:
    candles = _append(
        _bearish_window(),
        low_tick=102,
        high_tick=high_tick,
        open_tick=103,
        close_tick=104,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert _gap_snapshots(result, gap.gap_id)[-1].state is expected


@pytest.mark.parametrize(
    ("high_tick", "expected"),
    [
        (108, FairValueGapState.MIDPOINT_FILLED),
        (110, FairValueGapState.FULLY_FILLED),
    ],
)
def test_18_bearish_midpoint_and_full_fill_mirror_bullish(
    high_tick: int,
    expected: FairValueGapState,
) -> None:
    candles = _append(
        _bearish_window(),
        low_tick=102,
        high_tick=high_tick,
        open_tick=103,
        close_tick=104,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert _gap_snapshots(result, gap.gap_id)[-1].state is expected


def test_19_bearish_close_through_invalidation_has_precedence() -> None:
    candles = _append(
        _bearish_window(),
        low_tick=103,
        high_tick=112,
        open_tick=104,
        close_tick=111,
    )
    result = _analyze(candles)
    gap = _first_gap(result)
    transition = _gap_transitions(result, gap.gap_id)[-1]
    assert transition.to_state is FairValueGapState.INVALIDATED
    assert transition.reason == "CLOSE_THROUGH_INVALIDATION"


def test_20_direct_jump_no_regression_terminal_and_no_expiry() -> None:
    candles = _bullish_window()
    candles = _append(
        candles,
        low_tick=106,
        high_tick=109,
        open_tick=108,
        close_tick=107,
    )
    candles = _append(
        candles,
        low_tick=102,
        high_tick=108,
        open_tick=107,
        close_tick=103,
    )
    for _ in range(5):
        candles = _append(
            candles,
            low_tick=105,
            high_tick=108,
            open_tick=107,
            close_tick=106,
        )
    result = _analyze(candles)
    gap = _first_gap(result)
    assert [item.state for item in _gap_snapshots(result, gap.gap_id)] == [
        FairValueGapState.ACTIVE,
        FairValueGapState.TOUCHED,
        FairValueGapState.FULLY_FILLED,
    ]


def test_21_displacement_only_link_is_immutable_metadata() -> None:
    result = _analyze(_bullish_window(), context_links=(_link(),))
    gap = _first_gap(result)
    assert gap.displacement_id == _HASH_A
    assert gap.structure_event_id is None
    assert gap.structure_event_type is None


@pytest.mark.parametrize("include_displacement", [False, True])
def test_22_bos_link_is_preserved(include_displacement: bool) -> None:
    result = _analyze(
        _bullish_window(),
        context_links=(
            _link(
                displacement_id=_HASH_A if include_displacement else None,
                structure_event_id=_HASH_B,
                structure_event_type=DealingRangeEventType.BOS,
            ),
        ),
    )
    gap = _first_gap(result)
    assert gap.structure_event_id == _HASH_B
    assert gap.structure_event_type is DealingRangeEventType.BOS


@pytest.mark.parametrize("include_displacement", [False, True])
def test_23_choch_link_is_preserved(include_displacement: bool) -> None:
    result = _analyze(
        _bearish_window(),
        context_links=(
            _link(
                displacement_id=_HASH_A if include_displacement else None,
                structure_event_id=_HASH_C,
                structure_event_type=DealingRangeEventType.CHOCH,
            ),
        ),
    )
    gap = _first_gap(result)
    assert gap.structure_event_id == _HASH_C
    assert gap.structure_event_type is DealingRangeEventType.CHOCH


def test_24_empty_link_tuple_produces_unlinked_gap() -> None:
    gap = _first_gap(_analyze(_bullish_window(), context_links=()))
    assert (
        gap.displacement_id,
        gap.structure_event_id,
        gap.structure_event_type,
    ) == (None, None, None)


def test_25_duplicate_link_is_invalid_without_group_promotion() -> None:
    link = _link()
    result = _analyze(_bullish_window(), context_links=(link, link))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.gaps == result.transitions == result.snapshots == ()


def test_26_conflicting_links_are_ambiguous_and_order_independent() -> None:
    first = _link(displacement_id=_HASH_A)
    second = _link(displacement_id=_HASH_B)
    one = _analyze(_bullish_window(), context_links=(first, second))
    two = _analyze(_bullish_window(), context_links=(second, first))
    assert one.status is two.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert one.gaps == two.gaps == ()


@pytest.mark.parametrize(
    "link",
    [
        _link(index=9),
        _link(timestamp=_time(2) + timedelta(seconds=1)),
        _link(
            displacement_id=None,
            structure_event_id=_HASH_B,
            structure_event_type=None,
        ),
    ],
)
def test_27_dangling_mismatched_and_invalid_pair_are_invalid(
    link: FairValueGapContextLink,
) -> None:
    result = _analyze(_bullish_window(), context_links=(link,))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    unlinked = _analyze(_bullish_window(), context_links=())
    asserted_contemporaneous = _analyze(
        _bullish_window(),
        context_links=(_link(),),
    )
    assert asserted_contemporaneous.status is SMCV2PrimitiveStatus.VALID
    assert asserted_contemporaneous.gaps != unlinked.gaps
    assert (
        asserted_contemporaneous.gaps[: len(unlinked.gaps)]
        != unlinked.gaps
    )
    assert "previous_result" not in inspect.signature(
        analyze_fair_value_gaps
    ).parameters


@pytest.mark.parametrize("missing", ["candles", "context_links"])
def test_28_missing_top_level_context_is_unknown(missing: str) -> None:
    result = _analyze(
        None if missing == "candles" else _bullish_window(),
        context_links=None if missing == "context_links" else (),
    )
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.gaps == result.transitions == result.snapshots == ()


@pytest.mark.parametrize(
    "candles",
    [
        (),
        (_bullish_window()[0],),
        _bullish_window()[:2],
    ],
)
def test_29_empty_and_short_complete_inputs_are_none(
    candles: tuple[FairValueGapCandle, ...],
) -> None:
    assert _analyze(candles).status is SMCV2PrimitiveStatus.NONE


def test_30_valid_history_without_qualifying_window_is_none() -> None:
    candles = (
        _candle(0, open_tick=100, high_tick=102, low_tick=99, close_tick=101),
        _candle(1, open_tick=101, high_tick=103, low_tick=100, close_tick=102),
        _candle(2, open_tick=102, high_tick=104, low_tick=101, close_tick=103),
        _candle(3, open_tick=103, high_tick=105, low_tick=102, close_tick=104),
    )
    assert _analyze(candles).status is SMCV2PrimitiveStatus.NONE


@pytest.mark.parametrize(
    "bad",
    [
        FairValueGapCandle(
            index=True,  # type: ignore[arg-type]
            timestamp=_time(2),
            open_tick=107,
            high_tick=109,
            low_tick=106,
            close_tick=108,
        ),
        FairValueGapCandle(
            index=2,
            timestamp=datetime(2026, 1, 1),
            open_tick=107,
            high_tick=109,
            low_tick=106,
            close_tick=108,
        ),
        FairValueGapCandle(
            index=2,
            timestamp=_time(2),
            open_tick=110,
            high_tick=109,
            low_tick=106,
            close_tick=108,
        ),
        FairValueGapCandle(
            index=2,
            timestamp=_time(2),
            open_tick=107,
            high_tick=109,
            low_tick=106,
            close_tick=108.0,  # type: ignore[arg-type]
        ),
        object.__new__(FairValueGapCandle),
    ],
)
def test_31_malformed_candle_fails_closed_without_leakage(
    bad: FairValueGapCandle,
) -> None:
    result = _analyze((*_bullish_window()[:2], bad))
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "bad",
    [
        _link(displacement_id="A" * 64),
        _link(displacement_id="x"),
        _link(
            displacement_id=None,
            structure_event_id=None,
            structure_event_type=DealingRangeEventType.BOS,
        ),
        _link(
            displacement_id=None,
            structure_event_id=None,
            structure_event_type=None,
        ),
        object.__new__(FairValueGapContextLink),
    ],
)
def test_32_malformed_link_fails_closed_without_leakage(
    bad: FairValueGapContextLink,
) -> None:
    result = _analyze(_bullish_window(), context_links=(bad,))
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "variant",
    [
        "duplicate_index",
        "duplicate_time",
        "candle_list",
        "out_of_order_links",
        "context_link_list",
    ],
)
def test_33_chronology_and_collection_types_are_not_repaired(variant: str) -> None:
    candles: object = _bullish_window()
    context_links: object = ()
    if variant == "duplicate_index":
        candles = (
            *_bullish_window()[:2],
            _candle(
                1,
                timestamp=_time(2),
                open_tick=107,
                high_tick=109,
                low_tick=106,
                close_tick=108,
            ),
        )
    elif variant == "duplicate_time":
        candles = (
            *_bullish_window()[:2],
            _candle(
                2,
                timestamp=_time(1),
                open_tick=107,
                high_tick=109,
                low_tick=106,
                close_tick=108,
            ),
        )
    elif variant == "candle_list":
        candles = list(_bullish_window())
    elif variant == "out_of_order_links":
        candles = _append(
            _bullish_window(),
            low_tick=106,
            high_tick=109,
            open_tick=108,
            close_tick=107,
        )
        context_links = (
            _link(3, timestamp=_time(3)),
            _link(2, timestamp=_time(2)),
        )
    elif variant == "context_link_list":
        context_links = [_link()]
    result = analyze_fair_value_gaps(
        instrument="GC",
        timeframe="M5",
        candles=candles,  # type: ignore[arg-type]
        context_links=context_links,  # type: ignore[arg-type]
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    if variant == "out_of_order_links":
        assert "nondecreasing" in result.reasons[0]


def test_34_later_ambiguous_group_preserves_atomic_prior_evidence() -> None:
    candles = (
        *_bullish_window(),
        _candle(
            3,
            open_tick=114,
            high_tick=116,
            low_tick=114,
            close_tick=116,
        ),
        _candle(
            4,
            open_tick=103,
            high_tick=104,
            low_tick=101,
            close_tick=103,
        ),
    )
    links = (
        _link(
            4,
            displacement_id=_HASH_A,
            timestamp=_time(4),
        ),
        _link(
            4,
            displacement_id=_HASH_B,
            timestamp=_time(4),
        ),
    )
    result = _analyze(candles, context_links=links)
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert len(result.gaps) == 2
    assert all(snapshot.index < 4 for snapshot in result.snapshots)
    assert all(transition.index < 4 for transition in result.transitions)


def test_35_gap_identity_is_deterministic_and_schema_strict() -> None:
    result = _analyze(_bullish_window(), context_links=(_link(),))
    gap = _first_gap(result)
    offset = timezone(timedelta(hours=9))
    base = _gap_identity_kwargs(gap)
    reproduced = make_fair_value_gap_id(
        **{
            **base,
            "instrument": " gc ",
            "timeframe": " m5 ",
            "source_timestamps": tuple(
                timestamp.astimezone(offset) for timestamp in gap.source_timestamps
            ),
            "formation_end_timestamp": gap.formation_end_timestamp.astimezone(offset),
        }
    )
    assert reproduced == gap.gap_id
    varied_ids = {
        make_fair_value_gap_id(
            **{
                **base,
                "direction": SMCV2Direction.BEARISH,
            }
        ),
        make_fair_value_gap_id(
            **{
                **base,
                "source_indices": (0, 1, 3),
                "source_timestamps": (_time(0), _time(1), _time(3)),
                "formation_end_index": 3,
                "formation_end_timestamp": _time(3),
            }
        ),
        make_fair_value_gap_id(
            **{
                **base,
                "boundaries": SMCV2TickRange(gap.lower_tick, gap.upper_tick + 2),
                "midpoint_tick": Decimal(gap.lower_tick + gap.upper_tick + 2) / 2,
            }
        ),
        make_fair_value_gap_id(
            **{
                **base,
                "displacement_id": _HASH_B,
            }
        ),
    }
    assert gap.gap_id not in varied_ids
    assert len(varied_ids) == 4

    forbidden = {
        "gap_id": _HASH_A,
        "from_state": FairValueGapState.ACTIVE,
        "to_state": FairValueGapState.TOUCHED,
        "effective_index": 3,
        "effective_timestamp": _time(3),
        "reason": "WICK_TOUCH",
        "state": FairValueGapState.ACTIVE,
        "transition_ids": (_HASH_A,),
    }
    for name, value in forbidden.items():
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: value})

    for name in (
        "source_indices",
        "source_timestamps",
        "boundaries",
        "midpoint_tick",
        "formation_end_index",
        "formation_end_timestamp",
    ):
        missing = {
            "source_indices": (),
            "source_timestamps": (),
            "boundaries": None,
            "midpoint_tick": None,
            "formation_end_index": None,
            "formation_end_timestamp": None,
        }[name]
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: missing})

    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            **{
                **base,
                "midpoint_tick": gap.midpoint_tick + Decimal("0.5"),
            }
        )


def test_36_transition_identity_graph_reason_and_schema_are_strict() -> None:
    result = _analyze(
        _append(
            _bullish_window(),
            low_tick=106,
            high_tick=109,
            open_tick=108,
            close_tick=107,
        )
    )
    gap = _first_gap(result)
    transition = _gap_transitions(result, gap.gap_id)[-1]
    base = _transition_identity_kwargs(gap, transition)
    reproduced = make_fair_value_gap_id(**base)
    assert reproduced == transition.transition_id

    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            **{
                **base,
                "from_state": FairValueGapState.FULLY_FILLED,
                "to_state": FairValueGapState.TOUCHED,
                "reason": "WICK_TOUCH",
            }
        )
    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(**{**base, "reason": "NOT_LOCKED"})

    reason_edges = (
        (None, FairValueGapState.ACTIVE, "FORMATION_CONFIRMED"),
        (FairValueGapState.ACTIVE, FairValueGapState.TOUCHED, "WICK_TOUCH"),
        (
            FairValueGapState.ACTIVE,
            FairValueGapState.PARTIALLY_FILLED,
            "PARTIAL_FILL",
        ),
        (
            FairValueGapState.ACTIVE,
            FairValueGapState.MIDPOINT_FILLED,
            "MIDPOINT_FILL",
        ),
        (FairValueGapState.ACTIVE, FairValueGapState.FULLY_FILLED, "FULL_FILL"),
        (
            FairValueGapState.ACTIVE,
            FairValueGapState.INVALIDATED,
            "CLOSE_THROUGH_INVALIDATION",
        ),
    )
    accepted = {
        make_fair_value_gap_id(
            **{
                **base,
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
            }
        )
        for from_state, to_state, reason in reason_edges
    }
    assert len(accepted) == len(reason_edges)

    forbidden = {
        "source_indices": (0, 1, 2),
        "source_timestamps": (_time(0), _time(1), _time(2)),
        "boundaries": SMCV2TickRange(102, 106),
        "midpoint_tick": Decimal("104"),
        "formation_end_index": 2,
        "formation_end_timestamp": _time(2),
        "displacement_id": _HASH_A,
        "structure_event_id": _HASH_B,
        "structure_event_type": DealingRangeEventType.BOS,
        "state": FairValueGapState.TOUCHED,
        "transition_ids": (_HASH_A,),
    }
    for name, value in forbidden.items():
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: value})

    for name in (
        "gap_id",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
    ):
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: None})


def test_37_snapshot_identity_reconciles_complete_transition_prefix() -> None:
    result = _analyze(
        _append(
            _bullish_window(),
            low_tick=105,
            high_tick=109,
            open_tick=108,
            close_tick=107,
        )
    )
    gap = _first_gap(result)
    snapshot = _gap_snapshots(result, gap.gap_id)[-1]
    base = _snapshot_identity_kwargs(gap, snapshot)
    reproduced = make_fair_value_gap_id(**base)
    assert reproduced == snapshot.snapshot_id

    transitions = _gap_transitions(result, gap.gap_id)
    snapshots = _gap_snapshots(result, gap.gap_id)
    for position, item in enumerate(snapshots, start=1):
        assert item.transition_ids == tuple(
            transition.transition_id for transition in transitions[:position]
        )
        assert make_fair_value_gap_id(
            **_snapshot_identity_kwargs(gap, item)
        ) == item.snapshot_id

    assert make_fair_value_gap_id(
        **{
            **base,
            "transition_ids": tuple(reversed(snapshot.transition_ids)),
        }
    ) != snapshot.snapshot_id
    assert make_fair_value_gap_id(
        **{
            **base,
            "state": FairValueGapState.MIDPOINT_FILLED,
        }
    ) != snapshot.snapshot_id
    assert make_fair_value_gap_id(
        **{
            **base,
            "effective_index": snapshot.index + 1,
            "effective_timestamp": snapshot.timestamp + timedelta(minutes=5),
        }
    ) != snapshot.snapshot_id

    forbidden = {
        "source_indices": (0, 1, 2),
        "source_timestamps": (_time(0), _time(1), _time(2)),
        "boundaries": SMCV2TickRange(102, 106),
        "midpoint_tick": Decimal("104"),
        "formation_end_index": 2,
        "formation_end_timestamp": _time(2),
        "displacement_id": _HASH_A,
        "structure_event_id": _HASH_B,
        "structure_event_type": DealingRangeEventType.BOS,
        "from_state": FairValueGapState.ACTIVE,
        "to_state": FairValueGapState.TOUCHED,
        "reason": "WICK_TOUCH",
    }
    for name, value in forbidden.items():
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: value})

    for name, value in {
        "gap_id": None,
        "state": None,
        "effective_index": None,
        "effective_timestamp": None,
        "transition_ids": (),
    }.items():
        with pytest.raises((TypeError, ValueError)):
            make_fair_value_gap_id(**{**base, name: value})


def test_38_public_contracts_enums_exports_and_exception_containment() -> None:
    import smc.fair_value_gap as module

    assert FAIR_VALUE_GAP_DETECTOR_VERSION == "SMC-V2-FAIR-VALUE-GAP-1"
    assert [item.value for item in FairValueGapState] == [
        "ACTIVE",
        "TOUCHED",
        "PARTIALLY_FILLED",
        "MIDPOINT_FILLED",
        "FULLY_FILLED",
        "INVALIDATED",
    ]
    assert [field.name for field in fields(FairValueGapCandle)] == [
        "index",
        "timestamp",
        "open_tick",
        "high_tick",
        "low_tick",
        "close_tick",
    ]
    assert [field.name for field in fields(FairValueGapContextLink)] == [
        "formation_end_index",
        "formation_end_timestamp",
        "displacement_id",
        "structure_event_id",
        "structure_event_type",
    ]
    assert [field.name for field in fields(FairValueGap)] == [
        "gap_id",
        "direction",
        "source_indices",
        "source_timestamps",
        "lower_tick",
        "upper_tick",
        "midpoint_tick",
        "formation_end_index",
        "formation_end_timestamp",
        "displacement_id",
        "structure_event_id",
        "structure_event_type",
    ]
    assert [field.name for field in fields(FairValueGapTransition)] == [
        "transition_id",
        "gap_id",
        "from_state",
        "to_state",
        "index",
        "timestamp",
        "reason",
    ]
    assert [field.name for field in fields(FairValueGapSnapshot)] == [
        "snapshot_id",
        "gap_id",
        "direction",
        "state",
        "index",
        "timestamp",
        "transition_ids",
    ]
    assert [field.name for field in fields(FairValueGapResult)] == [
        "status",
        "gaps",
        "transitions",
        "snapshots",
        "reasons",
        "blocking_reasons",
    ]
    assert list(inspect.signature(analyze_fair_value_gaps).parameters) == [
        "instrument",
        "timeframe",
        "candles",
        "context_links",
    ]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(analyze_fair_value_gaps).parameters.values()
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(make_fair_value_gap_id).parameters.values()
    )
    builder_signature = inspect.signature(make_fair_value_gap_id)
    assert list(builder_signature.parameters) == [
        "identity_kind",
        "instrument",
        "timeframe",
        "direction",
        "source_indices",
        "source_timestamps",
        "boundaries",
        "midpoint_tick",
        "formation_end_index",
        "formation_end_timestamp",
        "displacement_id",
        "structure_event_id",
        "structure_event_type",
        "gap_id",
        "from_state",
        "to_state",
        "effective_index",
        "effective_timestamp",
        "reason",
        "state",
        "transition_ids",
    ]
    required = {"identity_kind", "instrument", "timeframe", "direction"}
    for name, parameter in builder_signature.parameters.items():
        expected_default = (
            inspect.Parameter.empty
            if name in required
            else ()
            if name in {"source_indices", "source_timestamps", "transition_ids"}
            else None
        )
        assert parameter.default == expected_default
    for public_dataclass in (
        FairValueGapCandle,
        FairValueGapContextLink,
        FairValueGap,
        FairValueGapTransition,
        FairValueGapSnapshot,
        FairValueGapResult,
    ):
        assert public_dataclass.__dataclass_params__.frozen is True
    assert module.__all__ == [
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
    malformed_range = object.__new__(SMCV2TickRange)
    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            identity_kind="GAP",
            instrument="GC",
            timeframe="M5",
            direction=SMCV2Direction.BULLISH,
            source_indices=(0, 1, 2),
            source_timestamps=(_time(0), _time(1), _time(2)),
            boundaries=malformed_range,
            midpoint_tick=Decimal("104"),
            formation_end_index=2,
            formation_end_timestamp=_time(2),
        )
    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            identity_kind="UNKNOWN",
            instrument="GC",
            timeframe="M5",
            direction=SMCV2Direction.BULLISH,
        )
    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            identity_kind="TRANSITION",
            instrument="GC",
            timeframe="M5",
            direction=SMCV2Direction.BULLISH,
            gap_id="A" * 64,
            from_state=FairValueGapState.ACTIVE,
            to_state=FairValueGapState.TOUCHED,
            effective_index=3,
            effective_timestamp=_time(3),
            reason="WICK_TOUCH",
        )
    with pytest.raises((TypeError, ValueError)):
        make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument="GC",
            timeframe="M5",
            direction=SMCV2Direction.BULLISH,
            gap_id=_HASH_A,
            effective_index=3,
            effective_timestamp=_time(3),
            state=FairValueGapState.ACTIVE,
            transition_ids=(_HASH_A, object()),  # type: ignore[arg-type]
        )


def test_39_repeatability_prefix_invariance_and_later_failure_preservation() -> None:
    prefix = _bullish_window()
    repeated_one = _analyze(prefix)
    repeated_two = _analyze(prefix)
    assert repeated_one == repeated_two

    longer = _append(
        prefix,
        low_tick=106,
        high_tick=109,
        open_tick=108,
        close_tick=107,
    )
    longer_result = _analyze(longer)
    assert longer_result.gaps[: len(repeated_one.gaps)] == repeated_one.gaps
    assert (
        longer_result.transitions[: len(repeated_one.transitions)]
        == repeated_one.transitions
    )
    assert longer_result.snapshots[0] == repeated_one.snapshots[0]

    malformed = FairValueGapCandle(
        index=4,
        timestamp=_time(4),
        open_tick=110,
        high_tick=109,
        low_tick=105,
        close_tick=106,
    )
    failed = _analyze((*longer, malformed))
    assert failed.status is SMCV2PrimitiveStatus.INVALID
    assert failed.gaps == longer_result.gaps
    assert failed.transitions == longer_result.transitions
    assert failed.snapshots == longer_result.snapshots

    same_effective_change = _analyze(prefix, context_links=(_link(),))
    assert same_effective_change.status is SMCV2PrimitiveStatus.VALID
    assert same_effective_change.gaps[: len(repeated_one.gaps)] != repeated_one.gaps

    multi_gap_candles = (
        *prefix,
        _candle(
            3,
            open_tick=114,
            high_tick=116,
            low_tick=114,
            close_tick=116,
        ),
        _candle(
            4,
            open_tick=103,
            high_tick=104,
            low_tick=101,
            close_tick=103,
        ),
    )
    deterministic_prefix = _analyze(multi_gap_candles[:4])
    deterministic_repeat = _analyze(multi_gap_candles[:4])
    assert deterministic_prefix == deterministic_repeat
    assert [gap.formation_end_index for gap in deterministic_prefix.gaps] == [2, 3]
    assert deterministic_prefix.gaps == tuple(
        sorted(
            deterministic_prefix.gaps,
            key=lambda gap: (
                gap.formation_end_index,
                gap.formation_end_timestamp,
                gap.direction.value,
                gap.source_indices,
                gap.gap_id,
            ),
        )
    )

    ambiguous_links = (
        _link(4, timestamp=_time(4), displacement_id=_HASH_A),
        _link(4, timestamp=_time(4), displacement_id=_HASH_B),
    )
    ambiguous = _analyze(multi_gap_candles, context_links=ambiguous_links)
    assert ambiguous.status is SMCV2PrimitiveStatus.AMBIGUOUS
    invalid_over_ambiguous = _analyze(
        multi_gap_candles,
        context_links=(
            *ambiguous_links,
            _link(4, timestamp=_time(4), displacement_id="A" * 64),
        ),
    )
    assert invalid_over_ambiguous.status is SMCV2PrimitiveStatus.INVALID
    assert invalid_over_ambiguous.gaps == deterministic_prefix.gaps
    assert invalid_over_ambiguous.transitions == deterministic_prefix.transitions
    assert invalid_over_ambiguous.snapshots == deterministic_prefix.snapshots


def test_40_module_is_standalone_and_has_no_forbidden_dependency() -> None:
    module_path = Path(__file__).parents[1] / "smc" / "fair_value_gap.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module)
            imported_modules.add(node.module)
    assert "pandas" not in imported_roots
    forbidden_modules = {
        "broker",
        "risk",
        "strategy",
        "execution",
        "smc.liquidity_map",
        "smc.premium_discount",
        "smc.market_structure",
        "smc.bos_choch",
    }
    assert imported_modules.isdisjoint(forbidden_modules)
    assert not any(
        isinstance(node, (ast.With, ast.AsyncWith))
        for node in ast.walk(tree)
    )
