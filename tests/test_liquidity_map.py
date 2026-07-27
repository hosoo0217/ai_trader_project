from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import inspect

import pytest

from smc.dealing_range import (
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeSwing,
    DealingRangeSwingSide,
    DealingRangeTransition,
    make_dealing_range_id,
)
from smc.equal_liquidity import (
    EqualLiquidityConfig,
    EqualLiquidityPool,
    EqualLiquiditySide,
    EqualLiquiditySwing,
    analyze_equal_liquidity,
    make_equal_liquidity_id,
)
from smc.liquidity_map import (
    LIQUIDITY_MAP_DETECTOR_VERSION,
    LiquidityClassification,
    LiquidityMapResult,
    LiquidityMapSnapshot,
    LiquidityReclassification,
    LiquidityScope,
    LiquiditySide,
    LiquiditySourceKind,
    analyze_liquidity_map,
    make_liquidity_map_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2LifecycleEvent,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


UTC = timezone.utc
T0 = datetime(2026, 7, 20, 10, 0, tzinfo=UTC)
INSTRUMENT = "GC"
TIMEFRAME = "M5"

_CONSTRUCTION = "CONSTRUCTION_ACTIVE"
_OBSERVATION_INVALIDATION = "OBSERVATION_CLOSE_THROUGH_INVALIDATION"
_CHOCH_INVALIDATION = "CHOCH_CLOSE_THROUGH_INVALIDATION"
_REPLACEMENT = "BOS_PULLBACK_REPLACEMENT"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _provenance(source_indices: tuple[int, ...], confirmation_index: int) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(T0 + timedelta(minutes=index) for index in source_indices),
        confirmation_index=confirmation_index,
        confirmation_timestamp=T0 + timedelta(minutes=confirmation_index),
    )


def _swing(
    side: DealingRangeSwingSide,
    source_index: int,
    price_tick: int,
    *,
    confirmation_index: int | None = None,
    swing_id: str | None = None,
) -> DealingRangeSwing:
    confirmation = source_index + 2 if confirmation_index is None else confirmation_index
    return DealingRangeSwing(
        side=side,
        price_tick=price_tick,
        provenance=_provenance((source_index,), confirmation),
        swing_id=swing_id or _hash(f"{side.value}:{source_index}:{price_tick}"),
    )


def _transition(
    *,
    lineage_id: str,
    direction: SMCV2Direction,
    from_state: DealingRangeState | None,
    to_state: DealingRangeState,
    index: int,
    reason: str,
    related_event_id: str | None,
    replacement_lineage_id: str | None = None,
) -> DealingRangeTransition:
    timestamp = T0 + timedelta(minutes=index)
    transition_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
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
        timestamp=timestamp,
        reason=reason,
        related_event_id=related_event_id,
        replacement_lineage_id=replacement_lineage_id,
    )


def _range_snapshot(
    *,
    direction: SMCV2Direction,
    source_swings: tuple[DealingRangeSwing, ...],
    low_tick: int,
    high_tick: int,
    index: int,
    state: DealingRangeState = DealingRangeState.ACTIVE,
    protected_swing: DealingRangeSwing | None = None,
    lineage_id: str | None = None,
    construction_event_id: str | None = None,
    transitions: tuple[DealingRangeTransition, ...] | None = None,
    replacement_lineage_id: str | None = None,
) -> DealingRangeSnapshot:
    ordered = tuple(sorted(source_swings, key=lambda item: item.provenance.source_indices[0]))
    source_indices = tuple(item.provenance.source_indices[0] for item in ordered)
    source_ids = tuple(item.swing_id for item in ordered)
    protected = protected_swing or (
        next(item for item in ordered if item.side is DealingRangeSwingSide.LOW)
        if direction is SMCV2Direction.BULLISH
        else next(item for item in ordered if item.side is DealingRangeSwingSide.HIGH)
    )
    event_id = construction_event_id or _hash(
        f"event:{direction.value}:{index}:{protected.swing_id}"
    )
    boundaries = SMCV2TickRange(low_tick, high_tick)
    canonical_lineage = lineage_id or make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices[:2],
        swing_ids=source_ids[:2],
        boundaries=boundaries,
        protected_swing_id=protected.swing_id,
        construction_event_id=event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    history = transitions
    if history is None:
        history = (
            _transition(
                lineage_id=canonical_lineage,
                direction=direction,
                from_state=None,
                to_state=DealingRangeState.ACTIVE,
                index=index,
                reason=_CONSTRUCTION,
                related_event_id=event_id,
            ),
        )
    transition_ids = tuple(item.transition_id for item in history)
    snapshot_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices,
        swing_ids=source_ids,
        boundaries=boundaries,
        lineage_id=canonical_lineage,
        construction_event_id=event_id,
        range_kind=DealingRangeKind.EXTERNAL,
        state=state,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )
    return DealingRangeSnapshot(
        kind=DealingRangeKind.EXTERNAL,
        direction=direction,
        snapshot_id=snapshot_id,
        source_swing_ids=source_ids,
        source_indices=source_indices,
        low_tick=low_tick,
        high_tick=high_tick,
        midpoint_tick=Decimal(low_tick + high_tick) / Decimal(2),
        first_known_provenance=_provenance((index,), index),
        lineage_id=canonical_lineage,
        protected_swing_id=protected.swing_id,
        construction_event_id=event_id,
        state=state,
        transitions=history,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )


def _terminal_range(
    active: DealingRangeSnapshot,
    swings: tuple[DealingRangeSwing, ...],
    *,
    index: int,
    state: DealingRangeState,
    replacement_lineage_id: str | None = None,
    reason: str | None = None,
) -> DealingRangeSnapshot:
    token = reason or (
        _REPLACEMENT if state is DealingRangeState.SUPERSEDED else _CHOCH_INVALIDATION
    )
    related = None if token == _OBSERVATION_INVALIDATION else _hash(f"terminal:{index}:{token}")
    terminal = _transition(
        lineage_id=active.lineage_id or "",
        direction=active.direction,
        from_state=DealingRangeState.ACTIVE,
        to_state=state,
        index=index,
        reason=token,
        related_event_id=related,
        replacement_lineage_id=replacement_lineage_id,
    )
    by_id = {item.swing_id: item for item in swings}
    source = tuple(by_id[item] for item in active.source_swing_ids)
    protected = by_id[active.protected_swing_id or ""]
    return _range_snapshot(
        direction=active.direction,
        source_swings=source,
        low_tick=active.low_tick,
        high_tick=active.high_tick,
        index=index,
        state=state,
        protected_swing=protected,
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        transitions=(*active.transitions, terminal),
        replacement_lineage_id=replacement_lineage_id,
    )


def _median_tick(values: tuple[int, ...]) -> int:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return int(
        ((Decimal(ordered[middle - 1]) + Decimal(ordered[middle])) / Decimal(2)).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


def _pool(
    side: EqualLiquiditySide,
    members: tuple[DealingRangeSwing, ...],
    *,
    state: SMCV2LifecycleState = SMCV2LifecycleState.ACTIVE,
    lineage_id: str | None = None,
    first_known_provenance: SMCV2EventProvenance | None = None,
    lifecycle_events: tuple[SMCV2LifecycleEvent, ...] | None = None,
    terminal_index: int | None = None,
) -> EqualLiquidityPool:
    source_indices = tuple(item.provenance.source_indices[0] for item in members)
    member_ids = tuple(item.swing_id for item in members)
    founding = members[:2]
    founding_reference = _median_tick(tuple(item.price_tick for item in founding))
    canonical_lineage = lineage_id or make_equal_liquidity_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices[:2],
        swing_ids=member_ids[:2],
        reference_tick=founding_reference,
        lower_tick=founding_reference - 2,
        upper_tick=founding_reference + 2,
    )
    latest_founder = max(
        founding,
        key=lambda item: (
            item.provenance.confirmation_index,
            item.provenance.confirmation_timestamp,
        ),
    )
    first_known = first_known_provenance or SMCV2EventProvenance(
        source_indices=source_indices[:2],
        source_timestamps=tuple(item.provenance.source_timestamps[0] for item in founding),
        confirmation_index=latest_founder.provenance.confirmation_index,
        confirmation_timestamp=latest_founder.provenance.confirmation_timestamp,
    )
    history = lifecycle_events or (
        SMCV2LifecycleEvent(
            from_state=None,
            to_state=SMCV2LifecycleState.ACTIVE,
            index=first_known.confirmation_index,
            timestamp=first_known.confirmation_timestamp,
            reason="second qualifying equal-liquidity swing confirmed",
        ),
    )
    if state in (SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN) and len(history) == 1:
        assert terminal_index is not None
        history = (
            *history,
            SMCV2LifecycleEvent(
                from_state=SMCV2LifecycleState.ACTIVE,
                to_state=state,
                index=terminal_index,
                timestamp=T0 + timedelta(minutes=terminal_index),
                reason=f"synthetic {state.value.lower()}",
            ),
        )
    reference = _median_tick(tuple(item.price_tick for item in members))
    lower, upper = reference - 2, reference + 2
    snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference,
        lower_tick=lower,
        upper_tick=upper,
        lineage_id=canonical_lineage,
        lifecycle_state=state,
    )
    return EqualLiquidityPool(
        side=side,
        lineage_id=canonical_lineage,
        snapshot_id=snapshot_id,
        member_swing_ids=member_ids,
        source_indices=source_indices,
        reference_tick=reference,
        lower_tick=lower,
        upper_tick=upper,
        first_known_provenance=first_known,
        lifecycle_state=state,
        lifecycle_events=history,
    )


def _base_range(
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    *,
    index: int = 6,
) -> tuple[tuple[DealingRangeSwing, ...], DealingRangeSnapshot]:
    low = _swing(DealingRangeSwingSide.LOW, 0, 90, confirmation_index=2)
    high = _swing(DealingRangeSwingSide.HIGH, 3, 110, confirmation_index=5)
    swings = (low, high)
    return swings, _range_snapshot(
        direction=direction,
        source_swings=swings,
        low_tick=90,
        high_tick=110,
        index=index,
    )


def _analyze(
    swings: tuple[DealingRangeSwing, ...] | None,
    pools: tuple[EqualLiquidityPool, ...] | None,
    ranges: tuple[DealingRangeSnapshot, ...] | None,
    *,
    instrument: str = INSTRUMENT,
    timeframe: str = TIMEFRAME,
) -> LiquidityMapResult:
    return analyze_liquidity_map(
        instrument=instrument,
        timeframe=timeframe,
        swings=swings,
        equal_liquidity_pools=pools,
        dealing_ranges=ranges,
    )


def _current(result: LiquidityMapResult) -> LiquidityMapSnapshot:
    assert result.snapshots
    return result.snapshots[-1]


def _classifications(
    result: LiquidityMapResult,
    *,
    kind: LiquiditySourceKind | None = None,
) -> tuple[LiquidityClassification, ...]:
    values = _current(result).classifications
    return values if kind is None else tuple(item for item in values if item.source_kind is kind)


def _without_field(instance: object, name: str) -> object:
    malformed = object.__new__(type(instance))
    for field_name, value in vars(instance).items():
        if field_name != name:
            object.__setattr__(malformed, field_name, value)
    return malformed


def test_01_bullish_range_has_side_correct_external_boundaries() -> None:
    swings, active = _base_range(SMCV2Direction.BULLISH)
    result = _analyze(swings, (), (active,))
    boundaries = _classifications(result, kind=LiquiditySourceKind.RANGE_BOUNDARY)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert {(item.side, item.boundaries.lower_tick) for item in boundaries} == {
        (LiquiditySide.BUY_SIDE, 110),
        (LiquiditySide.SELL_SIDE, 90),
    }


def test_02_bearish_range_keeps_side_independent_from_direction() -> None:
    swings, active = _base_range(SMCV2Direction.BEARISH)
    result = _analyze(swings, (), (active,))
    boundaries = _classifications(result, kind=LiquiditySourceKind.RANGE_BOUNDARY)
    assert {(item.side, item.boundaries.lower_tick) for item in boundaries} == {
        (LiquiditySide.BUY_SIDE, 110),
        (LiquiditySide.SELL_SIDE, 90),
    }


def test_03_inside_high_swing_is_buy_side_internal() -> None:
    base, active = _base_range()
    inside = _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9)
    result = _analyze((*base, inside), (), (active,))
    item = next(value for value in _classifications(result) if value.source_id == inside.swing_id)
    assert (item.side, item.scope) == (LiquiditySide.BUY_SIDE, LiquidityScope.INTERNAL)


def test_04_inside_low_swing_is_sell_side_internal() -> None:
    base, active = _base_range()
    inside = _swing(DealingRangeSwingSide.LOW, 7, 100, confirmation_index=9)
    result = _analyze((*base, inside), (), (active,))
    item = next(value for value in _classifications(result) if value.source_id == inside.swing_id)
    assert (item.side, item.scope) == (LiquiditySide.SELL_SIDE, LiquidityScope.INTERNAL)


def test_05_inside_equal_high_pool_is_buy_side_internal() -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, *members), (pool,), (active,))
    item = next(value for value in _classifications(result) if value.source_id == pool.lineage_id)
    assert (item.side, item.scope) == (LiquiditySide.BUY_SIDE, LiquidityScope.INTERNAL)


def test_06_inside_equal_low_pool_is_sell_side_internal() -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.LOW, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.LOW, 10, 100, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.LOW, members)
    result = _analyze((*base, *members), (pool,), (active,))
    item = next(value for value in _classifications(result) if value.source_id == pool.lineage_id)
    assert (item.side, item.scope) == (LiquiditySide.SELL_SIDE, LiquidityScope.INTERNAL)


def test_07_one_tick_inside_sources_are_internal() -> None:
    base, active = _base_range()
    inside = _swing(DealingRangeSwingSide.LOW, 7, 91, confirmation_index=9)
    members = (
        _swing(DealingRangeSwingSide.HIGH, 10, 93, confirmation_index=12),
        _swing(DealingRangeSwingSide.HIGH, 13, 93, confirmation_index=15),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, inside, *members), (pool,), (active,))
    current = _classifications(result)
    assert next(item for item in current if item.source_id == inside.swing_id).scope is LiquidityScope.INTERNAL
    assert next(item for item in current if item.source_id == pool.lineage_id).scope is LiquidityScope.INTERNAL


def test_08_exact_range_defining_swings_are_external() -> None:
    swings, active = _base_range()
    result = _analyze(swings, (), (active,))
    swing_items = _classifications(result, kind=LiquiditySourceKind.SWING)
    assert {item.source_id for item in swing_items} == {item.swing_id for item in swings}
    assert all(item.scope is LiquidityScope.EXTERNAL for item in swing_items)


def test_09_unrelated_same_price_swing_is_omitted() -> None:
    base, active = _base_range()
    unrelated = _swing(DealingRangeSwingSide.HIGH, 7, 110, confirmation_index=9)
    result = _analyze((*base, unrelated), (), (active,))
    assert unrelated.swing_id not in {item.source_id for item in _classifications(result)}


@pytest.mark.parametrize("price", [92, 108])
def test_10_pool_touching_boundary_is_omitted(price: int) -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, price, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, price, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, *members), (pool,), (active,))
    assert pool.lineage_id not in {item.source_id for item in _classifications(result)}


@pytest.mark.parametrize("price", [91, 109])
def test_11_pool_crossing_boundary_is_omitted(price: int) -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, price, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, price, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, *members), (pool,), (active,))
    assert pool.lineage_id not in {item.source_id for item in _classifications(result)}


def test_12_outside_sources_are_omitted_without_invalidating() -> None:
    base, active = _base_range()
    outside = _swing(DealingRangeSwingSide.HIGH, 7, 120, confirmation_index=9)
    members = (
        _swing(DealingRangeSwingSide.LOW, 10, 120, confirmation_index=12),
        _swing(DealingRangeSwingSide.LOW, 13, 120, confirmation_index=15),
    )
    pool = _pool(EqualLiquiditySide.LOW, members)
    result = _analyze((*base, outside, *members), (pool,), (active,))
    ids = {item.source_id for item in _classifications(result)}
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert outside.swing_id not in ids and pool.lineage_id not in ids


@pytest.mark.parametrize("terminal_state", [SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN])
def test_13_only_latest_active_pool_snapshot_is_eligible(
    terminal_state: SMCV2LifecycleState,
) -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    first = _pool(EqualLiquiditySide.HIGH, members)
    terminal = _pool(
        EqualLiquiditySide.HIGH,
        members,
        state=terminal_state,
        lineage_id=first.lineage_id,
        first_known_provenance=first.first_known_provenance,
        lifecycle_events=first.lifecycle_events,
        terminal_index=16,
    )
    result = _analyze((*base, *members), (first, terminal), (active,))
    assert terminal.lineage_id not in {item.source_id for item in _current(result).classifications}


@pytest.mark.parametrize("terminal_state", [DealingRangeState.SUPERSEDED, DealingRangeState.INVALIDATED])
def test_14_terminal_range_cannot_remain_active(terminal_state: DealingRangeState) -> None:
    swings, active = _base_range()
    replacement = _hash("replacement") if terminal_state is DealingRangeState.SUPERSEDED else None
    terminal = _terminal_range(
        active,
        swings,
        index=12,
        state=terminal_state,
        replacement_lineage_id=replacement,
        reason=_REPLACEMENT if replacement else _OBSERVATION_INVALIDATION,
    )
    result = _analyze(swings, (), (active, terminal))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert _current(result).active_range_snapshot_id == active.snapshot_id


def test_15_complete_context_without_active_range_is_none() -> None:
    swing = _swing(DealingRangeSwingSide.HIGH, 0, 100)
    result = _analyze((swing,), (), ())
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.snapshots == ()


@pytest.mark.parametrize("missing", ["swings", "pools", "ranges"])
def test_16_missing_top_level_context_is_unknown(missing: str) -> None:
    values = {"swings": (), "pools": (), "ranges": ()}
    values[missing] = None
    result = _analyze(values["swings"], values["pools"], values["ranges"])
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.snapshots == ()


def test_17_complete_empty_tuples_are_none() -> None:
    assert _analyze((), (), ()).status is SMCV2PrimitiveStatus.NONE


def test_18_active_range_always_has_two_canonical_boundaries() -> None:
    swings, active = _base_range()
    result = _analyze(swings, (), (active,))
    boundaries = _classifications(result, kind=LiquiditySourceKind.RANGE_BOUNDARY)
    assert len(boundaries) == 2
    assert len({item.source_id for item in boundaries}) == 2


@pytest.mark.parametrize("variant", ["missing", "wrong_type", "malformed_provenance"])
def test_19_malformed_swing_is_fail_closed(variant: str) -> None:
    base, active = _base_range()
    target = _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9)
    if variant == "missing":
        malformed = _without_field(target, "price_tick")
    elif variant == "wrong_type":
        malformed = replace(target, price_tick=True)
    else:
        provenance = object.__new__(SMCV2EventProvenance)
        object.__setattr__(provenance, "source_indices", (7,))
        object.__setattr__(provenance, "source_timestamps", (T0 + timedelta(minutes=7),))
        object.__setattr__(provenance, "confirmation_index", "9")
        object.__setattr__(provenance, "confirmation_timestamp", T0 + timedelta(minutes=9))
        malformed = replace(target, provenance=provenance)
    result = _analyze((*base, malformed), (), (active,))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("variant", ["missing", "wrong_type", "malformed_provenance"])
def test_20_malformed_pool_is_fail_closed(variant: str) -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    if variant == "missing":
        malformed = _without_field(pool, "snapshot_id")
    elif variant == "wrong_type":
        malformed = replace(pool, reference_tick=True)
    else:
        provenance = object.__new__(SMCV2EventProvenance)
        object.__setattr__(provenance, "source_indices", (7, 10))
        object.__setattr__(provenance, "source_timestamps", ())
        object.__setattr__(provenance, "confirmation_index", 12)
        object.__setattr__(provenance, "confirmation_timestamp", T0 + timedelta(minutes=12))
        malformed = replace(pool, first_known_provenance=provenance)
    result = _analyze((*base, *members), (malformed,), (active,))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "variant",
    [
        "missing",
        "wrong_type",
        "malformed_provenance",
        "initial_transition_mismatch",
    ],
)
def test_21_malformed_range_is_fail_closed(variant: str) -> None:
    swings, active = _base_range()
    if variant == "missing":
        malformed = _without_field(active, "snapshot_id")
    elif variant == "wrong_type":
        malformed = replace(active, low_tick=True)
    elif variant == "malformed_provenance":
        provenance = object.__new__(SMCV2EventProvenance)
        object.__setattr__(provenance, "source_indices", (6,))
        object.__setattr__(provenance, "source_timestamps", (T0 + timedelta(minutes=6),))
        object.__setattr__(provenance, "confirmation_index", 6)
        object.__setattr__(provenance, "confirmation_timestamp", "bad")
        malformed = replace(active, first_known_provenance=provenance)
    else:
        malformed = replace(
            active,
            first_known_provenance=_provenance((10,), 10),
        )
    result = _analyze(swings, (), (malformed,))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_22_dangling_pool_member_is_invalid() -> None:
    base, active = _base_range()
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, members[0]), (pool,), (active,))
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_23_dangling_range_source_or_protected_swing_is_invalid() -> None:
    swings, active = _base_range()
    result = _analyze((swings[0],), (), (active,))
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "direction",
    [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH],
)
def test_24_cross_source_side_or_provenance_conflict_is_invalid(
    direction: SMCV2Direction,
) -> None:
    base, active = _base_range(direction)
    members = (
        _swing(DealingRangeSwingSide.LOW, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.LOW, 10, 100, confirmation_index=12),
    )
    contradictory = _pool(EqualLiquiditySide.HIGH, members)
    result = _analyze((*base, *members), (contradictory,), (active,))
    assert result.status is SMCV2PrimitiveStatus.INVALID

    protected = next(item for item in base if item.swing_id == active.protected_swing_id)
    target = next(item for item in base if item.swing_id != active.protected_swing_id)
    contradictory_target = replace(target, side=protected.side)
    contradictory_swings = tuple(
        contradictory_target if item.swing_id == target.swing_id else item
        for item in base
    )
    target_result = _analyze(contradictory_swings, (), (active,))
    assert target_result.status is SMCV2PrimitiveStatus.INVALID
    assert target_result.snapshots == ()


def test_25_duplicate_semantic_identities_are_invalid() -> None:
    swings, active = _base_range()
    assert _analyze((*swings, swings[-1]), (), (active,)).status is SMCV2PrimitiveStatus.INVALID

    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    assert _analyze((*swings, *members), (pool, pool), (active,)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(swings, (), (active, active)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("kind", ["swing", "pool", "range"])
def test_26_out_of_order_tuples_are_invalid_without_sorting(kind: str) -> None:
    base, active = _base_range()
    if kind == "swing":
        result = _analyze(tuple(reversed(base)), (), (active,))
    elif kind == "pool":
        early_members = (
            _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
            _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
        )
        late_members = (
            _swing(DealingRangeSwingSide.LOW, 13, 100, confirmation_index=15),
            _swing(DealingRangeSwingSide.LOW, 16, 100, confirmation_index=18),
        )
        result = _analyze(
            (*base, *early_members, *late_members),
            (_pool(EqualLiquiditySide.LOW, late_members), _pool(EqualLiquiditySide.HIGH, early_members)),
            (active,),
        )
    else:
        later = _range_snapshot(
            direction=active.direction,
            source_swings=base,
            low_tick=90,
            high_tick=110,
            index=12,
            lineage_id=active.lineage_id,
            construction_event_id=active.construction_event_id,
            transitions=active.transitions,
        )
        result = _analyze(base, (), (later, active))
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_27_same_effective_pool_revisions_use_causal_prefix_not_hash_order() -> None:
    specs = (
        (0, 100, 2, "HIGH:0:100"),
        (3, 102, 5, "HIGH:3:102"),
        (6, 103, 11, "HIGH:6:103"),
        (9, 104, 11, "HIGH:9:104:0"),
    )
    mapped_swings = tuple(
        DealingRangeSwing(
            side=DealingRangeSwingSide.HIGH,
            price_tick=price,
            provenance=_provenance((index,), confirmation),
            swing_id=_hash(seed),
        )
        for index, price, confirmation, seed in specs
    )
    earlier = _pool(EqualLiquiditySide.HIGH, mapped_swings[:3])
    later = _pool(
        EqualLiquiditySide.HIGH,
        mapped_swings,
        lineage_id=earlier.lineage_id,
        first_known_provenance=earlier.first_known_provenance,
        lifecycle_events=earlier.lifecycle_events,
    )
    pools = (earlier, later)
    base, active = _base_range()
    all_swings = tuple(
        sorted(
            (*base, *mapped_swings),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(all_swings, pools, (active,))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert pools[-1].member_swing_ids[: len(pools[-2].member_swing_ids)] == pools[-2].member_swing_ids
    assert pools[-1].source_indices[: len(pools[-2].source_indices)] == pools[-2].source_indices
    assert pools[-1].snapshot_id < pools[-2].snapshot_id
    pool_item = next(item for item in _classifications(result) if item.source_id == pools[-1].lineage_id)
    assert pool_item.source_indices == pools[-1].source_indices


def test_28_same_index_malformed_member_has_no_partial_promotion() -> None:
    base, active = _base_range(index=6)
    members = (
        _swing(DealingRangeSwingSide.HIGH, 1, 100, confirmation_index=6),
        _swing(DealingRangeSwingSide.HIGH, 4, 100, confirmation_index=6),
    )
    pool = _pool(EqualLiquiditySide.HIGH, members)
    malformed = _without_field(pool, "snapshot_id")
    all_swings = tuple(
        sorted(
            (*base, *members),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(all_swings, (malformed,), (active,))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.snapshots == ()


@pytest.mark.parametrize(
    "old_direction",
    [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH],
)
def test_29_old_terminal_precedes_new_active_in_both_reversals(
    old_direction: SMCV2Direction,
) -> None:
    base, active = _base_range(old_direction, index=6)
    new_direction = (
        SMCV2Direction.BEARISH
        if old_direction is SMCV2Direction.BULLISH
        else SMCV2Direction.BULLISH
    )
    new_low = _swing(DealingRangeSwingSide.LOW, 7, 80, confirmation_index=9)
    new_high = _swing(DealingRangeSwingSide.HIGH, 9, 120, confirmation_index=11)
    new_active = _range_snapshot(
        direction=new_direction,
        source_swings=(new_low, new_high),
        low_tick=80,
        high_tick=120,
        index=12,
    )
    terminal = _terminal_range(
        active,
        base,
        index=12,
        state=DealingRangeState.INVALIDATED,
        reason=_CHOCH_INVALIDATION,
    )
    swings = tuple(
        sorted(
            (*base, new_low, new_high),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (), (active, terminal, new_active))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert _current(result).active_range_lineage_id == new_active.lineage_id

    late_replacement = replace(
        new_active,
        first_known_provenance=_provenance((13,), 13),
    )
    invalid = _analyze(swings, (), (active, terminal, late_replacement))
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    assert all(item.index < 12 for item in invalid.snapshots)


def test_30_same_index_new_range_swing_and_pool_use_post_transition_context() -> None:
    base, active = _base_range(index=6)
    new_low = _swing(DealingRangeSwingSide.LOW, 4, 80, confirmation_index=6)
    new_high = _swing(DealingRangeSwingSide.HIGH, 6, 120, confirmation_index=8)
    inside = _swing(DealingRangeSwingSide.HIGH, 9, 105, confirmation_index=12)
    pool_members = (
        _swing(DealingRangeSwingSide.LOW, 7, 100, confirmation_index=12),
        _swing(DealingRangeSwingSide.LOW, 8, 100, confirmation_index=12),
    )
    new_active = _range_snapshot(
        direction=SMCV2Direction.BEARISH,
        source_swings=(new_low, new_high),
        low_tick=80,
        high_tick=120,
        index=12,
    )
    terminal = _terminal_range(
        active,
        base,
        index=12,
        state=DealingRangeState.INVALIDATED,
        reason=_CHOCH_INVALIDATION,
    )
    pool = _pool(EqualLiquiditySide.LOW, pool_members)
    swings = tuple(
        sorted(
            (*base, new_low, new_high, inside, *pool_members),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (pool,), (active, terminal, new_active))
    current_ids = {item.source_id for item in _current(result).classifications}
    assert inside.swing_id in current_ids
    assert pool.lineage_id in current_ids
    assert _current(result).active_range_lineage_id == new_active.lineage_id


def test_31_same_index_terminal_pool_is_excluded() -> None:
    base, active = _base_range(index=6)
    members = (
        _swing(DealingRangeSwingSide.HIGH, 7, 100, confirmation_index=9),
        _swing(DealingRangeSwingSide.HIGH, 10, 100, confirmation_index=12),
    )
    first = _pool(EqualLiquiditySide.HIGH, members)
    terminal = _pool(
        EqualLiquiditySide.HIGH,
        members,
        state=SMCV2LifecycleState.BROKEN,
        lineage_id=first.lineage_id,
        first_known_provenance=first.first_known_provenance,
        lifecycle_events=first.lifecycle_events,
        terminal_index=16,
    )
    result = _analyze((*base, *members), (first, terminal), (active,))
    assert terminal.lineage_id not in {item.source_id for item in _current(result).classifications}


def test_32_two_unrelated_same_moment_active_ranges_are_ambiguous() -> None:
    first_swings, first = _base_range(index=6)
    second_low = _swing(DealingRangeSwingSide.LOW, 1, 80, confirmation_index=3)
    second_high = _swing(DealingRangeSwingSide.HIGH, 4, 120, confirmation_index=6)
    second = _range_snapshot(
        direction=SMCV2Direction.BEARISH,
        source_swings=(second_low, second_high),
        low_tick=80,
        high_tick=120,
        index=6,
    )
    swings = tuple(
        sorted(
            (*first_swings, second_low, second_high),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (), (first, second))
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert result.snapshots == ()


def test_33_transitionless_extension_reuses_unchanged_boundary_version() -> None:
    base, active = _base_range(index=6)
    new_high = _swing(DealingRangeSwingSide.HIGH, 7, 120, confirmation_index=10)
    extended = _range_snapshot(
        direction=active.direction,
        source_swings=(*base, new_high),
        low_tick=90,
        high_tick=120,
        index=10,
        protected_swing=base[0],
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        transitions=active.transitions,
    )
    result = _analyze((*base, new_high), (), (active, extended))
    assert len(result.snapshots) == 2
    first_boundaries = {
        item.side: item
        for item in result.snapshots[0].classifications
        if item.source_kind is LiquiditySourceKind.RANGE_BOUNDARY
    }
    last_boundaries = {
        item.side: item
        for item in result.snapshots[-1].classifications
        if item.source_kind is LiquiditySourceKind.RANGE_BOUNDARY
    }
    assert result.snapshots[0].map_id == result.snapshots[-1].map_id
    assert first_boundaries[LiquiditySide.SELL_SIDE] == last_boundaries[LiquiditySide.SELL_SIDE]
    assert last_boundaries[LiquiditySide.BUY_SIDE].version == 2
    assert last_boundaries[LiquiditySide.BUY_SIDE].prior_classification_id == first_boundaries[LiquiditySide.BUY_SIDE].classification_id


def test_34_range_replacement_creates_new_map_and_preserves_old_snapshot() -> None:
    base, active = _base_range(index=6)
    new_low = _swing(DealingRangeSwingSide.LOW, 7, 80, confirmation_index=9)
    new_high = _swing(DealingRangeSwingSide.HIGH, 9, 120, confirmation_index=11)
    replacement = _range_snapshot(
        direction=SMCV2Direction.BULLISH,
        source_swings=(new_low, new_high),
        low_tick=80,
        high_tick=120,
        index=12,
    )
    terminal = _terminal_range(
        active,
        base,
        index=12,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=replacement.lineage_id,
        reason=_REPLACEMENT,
    )
    swings = tuple(
        sorted(
            (*base, new_low, new_high),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (), (active, terminal, replacement))
    assert len(result.snapshots) == 2
    assert result.snapshots[0].map_id != result.snapshots[-1].map_id
    assert result.snapshots[0].active_range_snapshot_id == active.snapshot_id


def test_35_internal_to_external_swing_emits_one_reclassification() -> None:
    base, active = _base_range(index=6)
    target = _swing(DealingRangeSwingSide.HIGH, 4, 100, confirmation_index=5)
    new_low = _swing(DealingRangeSwingSide.LOW, 7, 80, confirmation_index=9)
    replacement = _range_snapshot(
        direction=SMCV2Direction.BULLISH,
        source_swings=(new_low, target),
        low_tick=80,
        high_tick=100,
        index=12,
    )
    terminal = _terminal_range(
        active,
        base,
        index=12,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=replacement.lineage_id,
        reason=_REPLACEMENT,
    )
    swings = tuple(
        sorted(
            (*base, target, new_low),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (), (active, terminal, replacement))
    event = next(item for item in result.reclassifications if item.source_id == target.swing_id)
    assert (event.from_scope, event.to_scope, event.reason) == (
        LiquidityScope.INTERNAL,
        LiquidityScope.EXTERNAL,
        "INTERNAL_TO_EXTERNAL_RANGE_DEFINING",
    )


def test_36_external_to_internal_swing_emits_one_reclassification() -> None:
    base, active = _base_range(index=6)
    new_low = _swing(DealingRangeSwingSide.LOW, 7, 80, confirmation_index=9)
    new_high = _swing(DealingRangeSwingSide.HIGH, 9, 120, confirmation_index=11)
    replacement = _range_snapshot(
        direction=SMCV2Direction.BEARISH,
        source_swings=(new_low, new_high),
        low_tick=80,
        high_tick=120,
        index=12,
    )
    terminal = _terminal_range(
        active,
        base,
        index=12,
        state=DealingRangeState.INVALIDATED,
        reason=_CHOCH_INVALIDATION,
    )
    swings = tuple(
        sorted(
            (*base, new_low, new_high),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(swings, (), (active, terminal, replacement))
    old_high = base[1]
    event = next(item for item in result.reclassifications if item.source_id == old_high.swing_id)
    assert (event.from_scope, event.to_scope, event.reason) == (
        LiquidityScope.EXTERNAL,
        LiquidityScope.INTERNAL,
        "EXTERNAL_TO_INTERNAL_SUBORDINATE",
    )


def test_37_omission_and_reentry_increment_version_without_scope_event() -> None:
    base, first = _base_range(index=6)
    target = _swing(DealingRangeSwingSide.HIGH, 4, 100, confirmation_index=5)
    second_low = _swing(DealingRangeSwingSide.LOW, 7, 110, confirmation_index=9)
    second_high = _swing(DealingRangeSwingSide.HIGH, 9, 130, confirmation_index=11)
    second = _range_snapshot(
        direction=SMCV2Direction.BULLISH,
        source_swings=(second_low, second_high),
        low_tick=110,
        high_tick=130,
        index=12,
    )
    first_terminal = _terminal_range(
        first,
        base,
        index=12,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=second.lineage_id,
        reason=_REPLACEMENT,
    )
    third_low = _swing(DealingRangeSwingSide.LOW, 13, 80, confirmation_index=15)
    third_high = _swing(DealingRangeSwingSide.HIGH, 15, 120, confirmation_index=17)
    third = _range_snapshot(
        direction=SMCV2Direction.BULLISH,
        source_swings=(third_low, third_high),
        low_tick=80,
        high_tick=120,
        index=18,
    )
    second_terminal = _terminal_range(
        second,
        (second_low, second_high),
        index=18,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=third.lineage_id,
        reason=_REPLACEMENT,
    )
    swings = tuple(
        sorted(
            (*base, target, second_low, second_high, third_low, third_high),
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.side.value,
                item.swing_id,
            ),
        )
    )
    result = _analyze(
        swings,
        (),
        (first, first_terminal, second, second_terminal, third),
    )
    current = next(item for item in _current(result).classifications if item.source_id == target.swing_id)
    assert current.scope is LiquidityScope.INTERNAL
    assert current.version == 2
    assert all(item.source_id != target.swing_id for item in result.reclassifications)


def test_38_identity_kinds_are_deterministic_and_schema_strict() -> None:
    lineage = _hash("map-lineage")
    source = _hash("source")
    range_snapshot = _hash("range-snapshot")
    second_classification = _hash("second-classification")
    newer = _hash("new-classification")
    common = {
        "instrument": " gc ",
        "timeframe": " m5 ",
        "active_range_lineage_id": lineage,
    }
    valid: dict[str, dict[str, object]] = {
        "MAP": {"identity_kind": "MAP", **common},
        "BOUNDARY": {
            "identity_kind": "BOUNDARY",
            **common,
            "source_kind": LiquiditySourceKind.RANGE_BOUNDARY,
            "side": LiquiditySide.BUY_SIDE,
        },
        "CLASSIFICATION": {
            "identity_kind": "CLASSIFICATION",
            **common,
            "source_indices": (1,),
            "source_kind": LiquiditySourceKind.SWING,
            "source_id": source,
            "side": LiquiditySide.BUY_SIDE,
            "scope": LiquidityScope.INTERNAL,
            "boundaries": SMCV2TickRange(100, 100),
            "active_range_snapshot_id": range_snapshot,
            "version": 1,
            "event_index": 3,
            "event_timestamp": T0 + timedelta(minutes=3),
        },
        "SNAPSHOT": {
            "identity_kind": "SNAPSHOT",
            **common,
            "active_range_snapshot_id": range_snapshot,
            "classification_ids": tuple(sorted((source, second_classification))),
            "reclassification_ids": (),
            "event_index": 3,
            "event_timestamp": T0 + timedelta(minutes=3),
        },
        "RECLASSIFICATION": {
            "identity_kind": "RECLASSIFICATION",
            **common,
            "source_kind": LiquiditySourceKind.SWING,
            "source_id": source,
            "side": LiquiditySide.BUY_SIDE,
            "prior_classification_id": second_classification,
            "new_classification_id": newer,
            "event_index": 4,
            "event_timestamp": T0 + timedelta(minutes=4),
            "from_scope": LiquidityScope.INTERNAL,
            "to_scope": LiquidityScope.EXTERNAL,
            "reason": "INTERNAL_TO_EXTERNAL_RANGE_DEFINING",
        },
    }
    identities = {
        kind: make_liquidity_map_id(**kwargs)  # type: ignore[arg-type]
        for kind, kwargs in valid.items()
    }
    assert all(len(value) == 64 for value in identities.values())
    assert identities["MAP"] == make_liquidity_map_id(
        identity_kind="MAP",
        instrument="GC",
        timeframe="M5",
        active_range_lineage_id=lineage,
    )

    boundary_sell = {
        **valid["BOUNDARY"],
        "side": LiquiditySide.SELL_SIDE,
    }
    assert identities["BOUNDARY"] != make_liquidity_map_id(  # type: ignore[arg-type]
        **boundary_sell,
    )
    classification_external = {
        **valid["CLASSIFICATION"],
        "scope": LiquidityScope.EXTERNAL,
    }
    classification_sell = {
        **valid["CLASSIFICATION"],
        "side": LiquiditySide.SELL_SIDE,
    }
    classification_pool = {
        **valid["CLASSIFICATION"],
        "source_kind": LiquiditySourceKind.EQUAL_LIQUIDITY_POOL,
    }
    assert identities["CLASSIFICATION"] != make_liquidity_map_id(  # type: ignore[arg-type]
        **classification_external,
    )
    assert identities["CLASSIFICATION"] != make_liquidity_map_id(  # type: ignore[arg-type]
        **classification_sell,
    )
    assert identities["CLASSIFICATION"] != make_liquidity_map_id(  # type: ignore[arg-type]
        **classification_pool,
    )
    version_two = {
        **valid["CLASSIFICATION"],
        "version": 2,
        "prior_classification_id": identities["CLASSIFICATION"],
    }
    assert identities["CLASSIFICATION"] != make_liquidity_map_id(  # type: ignore[arg-type]
        **version_two,
    )
    equivalent_utc = {
        **valid["CLASSIFICATION"],
        "event_timestamp": (T0 + timedelta(minutes=3)).astimezone(
            timezone(timedelta(hours=9))
        ),
    }
    assert identities["CLASSIFICATION"] == make_liquidity_map_id(  # type: ignore[arg-type]
        **equivalent_utc,
    )

    required: dict[str, tuple[str, ...]] = {
        "MAP": ("identity_kind", "instrument", "timeframe", "active_range_lineage_id"),
        "BOUNDARY": (
            "identity_kind",
            "instrument",
            "timeframe",
            "active_range_lineage_id",
            "source_kind",
            "side",
        ),
        "CLASSIFICATION": (
            "identity_kind",
            "instrument",
            "timeframe",
            "active_range_lineage_id",
            "source_indices",
            "source_kind",
            "source_id",
            "side",
            "scope",
            "boundaries",
            "active_range_snapshot_id",
            "version",
            "event_index",
            "event_timestamp",
        ),
        "SNAPSHOT": (
            "identity_kind",
            "instrument",
            "timeframe",
            "active_range_lineage_id",
            "active_range_snapshot_id",
            "classification_ids",
            "event_index",
            "event_timestamp",
        ),
        "RECLASSIFICATION": (
            "identity_kind",
            "instrument",
            "timeframe",
            "active_range_lineage_id",
            "source_kind",
            "source_id",
            "side",
            "prior_classification_id",
            "new_classification_id",
            "event_index",
            "event_timestamp",
            "from_scope",
            "to_scope",
            "reason",
        ),
    }
    for kind, names in required.items():
        for name in names:
            missing = dict(valid[kind])
            del missing[name]
            with pytest.raises((TypeError, ValueError)):
                make_liquidity_map_id(**missing)  # type: ignore[arg-type]

    non_defaults: dict[str, object] = {
        "source_indices": (1,),
        "source_kind": LiquiditySourceKind.SWING,
        "source_id": source,
        "side": LiquiditySide.BUY_SIDE,
        "scope": LiquidityScope.INTERNAL,
        "boundaries": SMCV2TickRange(100, 100),
        "active_range_snapshot_id": range_snapshot,
        "version": 1,
        "prior_classification_id": second_classification,
        "new_classification_id": newer,
        "classification_ids": (source, second_classification),
        "reclassification_ids": (newer,),
        "event_index": 4,
        "event_timestamp": T0 + timedelta(minutes=4),
        "from_scope": LiquidityScope.INTERNAL,
        "to_scope": LiquidityScope.EXTERNAL,
        "reason": "INTERNAL_TO_EXTERNAL_RANGE_DEFINING",
    }
    forbidden: dict[str, tuple[str, ...]] = {
        "MAP": tuple(non_defaults),
        "BOUNDARY": tuple(
            name for name in non_defaults if name not in {"source_kind", "side"}
        ),
        "CLASSIFICATION": (
            "new_classification_id",
            "classification_ids",
            "reclassification_ids",
            "from_scope",
            "to_scope",
            "reason",
        ),
        "SNAPSHOT": (
            "source_indices",
            "source_kind",
            "source_id",
            "side",
            "scope",
            "boundaries",
            "version",
            "prior_classification_id",
            "new_classification_id",
            "from_scope",
            "to_scope",
            "reason",
        ),
        "RECLASSIFICATION": (
            "source_indices",
            "scope",
            "boundaries",
            "active_range_snapshot_id",
            "version",
            "classification_ids",
            "reclassification_ids",
        ),
    }
    for kind, names in forbidden.items():
        for name in names:
            supplied = {**valid[kind], name: non_defaults[name]}
            with pytest.raises((TypeError, ValueError)):
                make_liquidity_map_id(**supplied)  # type: ignore[arg-type]

    free_reason = {
        **valid["RECLASSIFICATION"],
        "reason": "FREE_TEXT",
    }
    with pytest.raises((TypeError, ValueError)):
        make_liquidity_map_id(**free_reason)  # type: ignore[arg-type]


def test_39_repeatability_prefix_and_later_invalid_preservation() -> None:
    base, active = _base_range(index=6)
    baseline = _analyze(base, (), (active,))
    assert baseline == _analyze(base, (), (active,))

    new_high = _swing(DealingRangeSwingSide.HIGH, 7, 120, confirmation_index=10)
    extended = _range_snapshot(
        direction=active.direction,
        source_swings=(*base, new_high),
        low_tick=90,
        high_tick=120,
        index=10,
        protected_swing=base[0],
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        transitions=active.transitions,
    )
    future = _analyze((*base, new_high), (), (active, extended))
    assert future.snapshots[: len(baseline.snapshots)] == baseline.snapshots

    malformed = _without_field(extended, "state")
    invalid = _analyze((*base, new_high), (), (active, malformed))  # type: ignore[arg-type]
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    assert invalid.snapshots == baseline.snapshots


def test_40_public_surface_is_frozen_keyword_only_and_standalone() -> None:
    assert LIQUIDITY_MAP_DETECTOR_VERSION == "SMC-V2-LIQUIDITY-MAP-1"
    expected_fields = {
        LiquidityClassification: [
            "classification_id",
            "source_kind",
            "source_id",
            "side",
            "scope",
            "source_indices",
            "boundaries",
            "active_range_lineage_id",
            "active_range_snapshot_id",
            "version",
            "classification_index",
            "classification_timestamp",
            "prior_classification_id",
        ],
        LiquidityReclassification: [
            "reclassification_id",
            "source_kind",
            "source_id",
            "side",
            "from_scope",
            "to_scope",
            "prior_classification_id",
            "new_classification_id",
            "index",
            "timestamp",
            "reason",
        ],
        LiquidityMapSnapshot: [
            "map_id",
            "snapshot_id",
            "active_range_lineage_id",
            "active_range_snapshot_id",
            "index",
            "timestamp",
            "classifications",
            "classification_ids",
            "reclassifications",
            "reclassification_ids",
        ],
        LiquidityMapResult: [
            "status",
            "snapshots",
            "reclassifications",
            "reasons",
            "blocking_reasons",
        ],
    }
    for cls, names in expected_fields.items():
        assert cls.__dataclass_params__.frozen is True
        assert [field.name for field in fields(cls)] == names
    assert [item.value for item in LiquiditySide] == ["BUY_SIDE", "SELL_SIDE"]
    assert [item.value for item in LiquidityScope] == ["INTERNAL", "EXTERNAL"]
    assert [item.value for item in LiquiditySourceKind] == [
        "SWING",
        "EQUAL_LIQUIDITY_POOL",
        "RANGE_BOUNDARY",
    ]
    assert list(inspect.signature(analyze_liquidity_map).parameters) == [
        "instrument",
        "timeframe",
        "swings",
        "equal_liquidity_pools",
        "dealing_ranges",
    ]
    assert all(
        value.kind is inspect.Parameter.KEYWORD_ONLY
        for value in inspect.signature(analyze_liquidity_map).parameters.values()
    )
    identity_parameters = inspect.signature(make_liquidity_map_id).parameters
    assert list(identity_parameters) == [
        "identity_kind",
        "instrument",
        "timeframe",
        "active_range_lineage_id",
        "source_indices",
        "source_kind",
        "source_id",
        "side",
        "scope",
        "boundaries",
        "active_range_snapshot_id",
        "version",
        "prior_classification_id",
        "new_classification_id",
        "classification_ids",
        "reclassification_ids",
        "event_index",
        "event_timestamp",
        "from_scope",
        "to_scope",
        "reason",
    ]
    assert all(
        value.kind is inspect.Parameter.KEYWORD_ONLY
        for value in identity_parameters.values()
    )
    assert all(
        identity_parameters[name].default is inspect.Parameter.empty
        for name in (
            "identity_kind",
            "instrument",
            "timeframe",
            "active_range_lineage_id",
        )
    )
    assert identity_parameters["source_indices"].default == ()
    assert identity_parameters["classification_ids"].default == ()
    assert identity_parameters["reclassification_ids"].default == ()
    assert all(
        identity_parameters[name].default is None
        for name in (
            "source_kind",
            "source_id",
            "side",
            "scope",
            "boundaries",
            "active_range_snapshot_id",
            "version",
            "prior_classification_id",
            "new_classification_id",
            "event_index",
            "event_timestamp",
            "from_scope",
            "to_scope",
            "reason",
        )
    )
    expected_exports = {
        "LIQUIDITY_MAP_DETECTOR_VERSION",
        "LiquiditySide",
        "LiquidityScope",
        "LiquiditySourceKind",
        "LiquidityClassification",
        "LiquidityReclassification",
        "LiquidityMapSnapshot",
        "LiquidityMapResult",
        "make_liquidity_map_id",
        "analyze_liquidity_map",
    }
    import smc.liquidity_map as module

    assert set(module.__all__) == expected_exports
    source = inspect.getsource(module)
    for forbidden in ("pandas", "liquidity_sweep", "open(", "requests", "broker", "main"):
        assert forbidden not in source
    sample = LiquidityMapResult(status=SMCV2PrimitiveStatus.NONE)
    with pytest.raises(FrozenInstanceError):
        sample.status = SMCV2PrimitiveStatus.VALID  # type: ignore[misc]
