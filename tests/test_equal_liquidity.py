from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

import smc.equal_liquidity as equal_liquidity
from smc.equal_liquidity import (
    EQUAL_LIQUIDITY_DETECTOR_VERSION,
    EqualLiquidityConfig,
    EqualLiquidityObservation,
    EqualLiquidityPool,
    EqualLiquidityResult,
    EqualLiquiditySide,
    EqualLiquiditySwing,
    analyze_equal_liquidity,
    make_equal_liquidity_id,
)
from smc.smc_v2_primitives import (
    SMCV2EventProvenance,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
)


UTC = timezone.utc
T0 = datetime(2026, 7, 19, 10, 0, tzinfo=UTC)
INSTRUMENT = "GC"
TIMEFRAME = "M5"


def _provenance(
    source_index: int,
    *,
    confirmation_index: int | None = None,
    confirmation_minute: int | None = None,
) -> SMCV2EventProvenance:
    confirmation = source_index + 2 if confirmation_index is None else confirmation_index
    minute = confirmation if confirmation_minute is None else confirmation_minute
    return SMCV2EventProvenance(
        source_indices=(source_index,),
        source_timestamps=(T0 + timedelta(minutes=source_index),),
        confirmation_index=confirmation,
        confirmation_timestamp=T0 + timedelta(minutes=minute),
    )


def _swing(
    side: EqualLiquiditySide,
    source_index: int,
    price_tick: int,
    *,
    confirmation_index: int | None = None,
    confirmation_minute: int | None = None,
) -> EqualLiquiditySwing:
    provenance = _provenance(
        source_index,
        confirmation_index=confirmation_index,
        confirmation_minute=confirmation_minute,
    )
    swing_id = make_equal_liquidity_id(
        identity_kind="SWING",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=(source_index,),
        reference_tick=price_tick,
        lower_tick=price_tick,
        upper_tick=price_tick,
    )
    return EqualLiquiditySwing(
        side=side,
        price_tick=price_tick,
        provenance=provenance,
        swing_id=swing_id,
    )


def _observation(
    index: int,
    *,
    high_tick: int,
    low_tick: int,
    close_tick: int,
    minute: int | None = None,
) -> EqualLiquidityObservation:
    return EqualLiquidityObservation(
        index=index,
        timestamp=T0 + timedelta(minutes=index if minute is None else minute),
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
    )


def _analyze(
    swings: tuple[EqualLiquiditySwing, ...] | None,
    observations: tuple[EqualLiquidityObservation, ...] | None = (),
    *,
    instrument: str = INSTRUMENT,
    timeframe: str = TIMEFRAME,
    config: EqualLiquidityConfig = EqualLiquidityConfig(),
) -> EqualLiquidityResult:
    return analyze_equal_liquidity(
        instrument=instrument,
        timeframe=timeframe,
        swings=swings,
        observations=observations,
        config=config,
    )


def _latest(result: EqualLiquidityResult) -> EqualLiquidityPool:
    assert result.pools
    return result.pools[-1]


def _active_pool(
    side: EqualLiquiditySide,
    *,
    first_price: int = 100,
    second_price: int = 100,
) -> tuple[EqualLiquiditySwing, EqualLiquiditySwing]:
    return (
        _swing(side, 0, first_price),
        _swing(side, 3, second_price),
    )


def test_01_equal_high_positive_formation() -> None:
    result = _analyze(_active_pool(EqualLiquiditySide.HIGH))

    assert result.status is SMCV2PrimitiveStatus.VALID
    assert _latest(result).side is EqualLiquiditySide.HIGH
    assert _latest(result).lifecycle_state is SMCV2LifecycleState.ACTIVE
    assert len(_latest(result).member_swing_ids) == 2


def test_02_equal_low_positive_formation() -> None:
    result = _analyze(_active_pool(EqualLiquiditySide.LOW))

    assert result.status is SMCV2PrimitiveStatus.VALID
    assert _latest(result).side is EqualLiquiditySide.LOW
    assert _latest(result).lifecycle_state is SMCV2LifecycleState.ACTIVE


def test_03_two_tick_inclusive_equality() -> None:
    swings = _active_pool(EqualLiquiditySide.HIGH, first_price=100, second_price=102)
    result = _analyze(swings)

    assert result.status is SMCV2PrimitiveStatus.VALID
    assert _latest(result).reference_tick == 101
    assert (_latest(result).lower_tick, _latest(result).upper_tick) == (99, 103)


def test_04_three_tick_price_near_miss() -> None:
    swings = _active_pool(EqualLiquiditySide.HIGH, first_price=100, second_price=103)

    assert _analyze(swings).status is SMCV2PrimitiveStatus.NONE


def test_05_three_bar_inclusive_member_separation() -> None:
    swings = (
        _swing(EqualLiquiditySide.HIGH, 10, 100),
        _swing(EqualLiquiditySide.HIGH, 13, 100),
    )

    assert _analyze(swings).status is SMCV2PrimitiveStatus.VALID


def test_06_two_bar_member_separation_is_rejected() -> None:
    swings = (
        _swing(EqualLiquiditySide.HIGH, 10, 100),
        _swing(EqualLiquiditySide.HIGH, 12, 100),
    )

    assert _analyze(swings).status is SMCV2PrimitiveStatus.NONE


def test_07_one_member_returns_none() -> None:
    result = _analyze((_swing(EqualLiquiditySide.HIGH, 0, 100),))

    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.pools == ()


def test_08_missing_swing_context_returns_unknown() -> None:
    result = _analyze(None, ())

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.pools == ()


def test_09_missing_observation_context_returns_unknown() -> None:
    result = _analyze((), None)

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.pools == ()


@pytest.mark.parametrize("provenance", [None, object()])
def test_10_missing_or_malformed_swing_provenance_is_invalid(provenance: object) -> None:
    swing = EqualLiquiditySwing(
        side=EqualLiquiditySide.HIGH,
        price_tick=100,
        provenance=provenance,  # type: ignore[arg-type]
        swing_id="0" * 64,
    )

    assert _analyze((swing,)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("malformed_kind", ["provenance", "swing", "observation"])
def test_10_internally_malformed_required_fields_are_invalid(
    malformed_kind: str,
) -> None:
    valid_swing = _swing(EqualLiquiditySide.HIGH, 0, 100)
    if malformed_kind == "provenance":
        malformed_provenance = object.__new__(SMCV2EventProvenance)
        object.__setattr__(malformed_provenance, "source_indices", (0,))
        object.__setattr__(malformed_provenance, "confirmation_index", 2)
        object.__setattr__(
            malformed_provenance,
            "confirmation_timestamp",
            T0 + timedelta(minutes=2),
        )
        malformed_swing = replace(valid_swing, provenance=malformed_provenance)
        result = _analyze((malformed_swing,))
    elif malformed_kind == "swing":
        malformed_swing = object.__new__(EqualLiquiditySwing)
        object.__setattr__(malformed_swing, "side", valid_swing.side)
        object.__setattr__(malformed_swing, "provenance", valid_swing.provenance)
        object.__setattr__(malformed_swing, "swing_id", valid_swing.swing_id)
        result = _analyze((malformed_swing,))
    else:
        malformed_observation = object.__new__(EqualLiquidityObservation)
        object.__setattr__(malformed_observation, "index", 1)
        object.__setattr__(malformed_observation, "timestamp", T0 + timedelta(minutes=1))
        object.__setattr__(malformed_observation, "low_tick", 99)
        object.__setattr__(malformed_observation, "close_tick", 100)
        result = _analyze((), (malformed_observation,))

    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_11_invalid_types_chronology_and_ohlc_fail_closed() -> None:
    valid = _swing(EqualLiquiditySide.HIGH, 0, 100)
    malformed_swings: tuple[tuple[EqualLiquiditySwing, ...], ...] = (
        (replace(valid, side="HIGH"),),  # type: ignore[arg-type]
        (replace(valid, price_tick=100.0),),  # type: ignore[arg-type]
        (replace(valid, price_tick=True),),
        (valid, valid),
        (_swing(EqualLiquiditySide.HIGH, 3, 100), valid),
    )
    for swings in malformed_swings:
        assert _analyze(swings).status is SMCV2PrimitiveStatus.INVALID

    naive = EqualLiquidityObservation(6, datetime(2026, 7, 19, 10, 6), 103, 99, 101)
    invalid_ohlc = EqualLiquidityObservation(6, T0, 100, 101, 100)
    float_tick = EqualLiquidityObservation(6, T0, 103.0, 99, 101)  # type: ignore[arg-type]
    bool_tick = EqualLiquidityObservation(6, T0, True, 0, 0)  # type: ignore[arg-type]
    for observation in (naive, invalid_ohlc, float_tick, bool_tick):
        assert _analyze((), (observation,)).status is SMCV2PrimitiveStatus.INVALID

    duplicate = _observation(6, high_tick=101, low_tick=99, close_tick=100)
    earlier = _observation(5, high_tick=101, low_tick=99, close_tick=100)
    assert _analyze((), (duplicate, duplicate)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze((), (duplicate, earlier)).status is SMCV2PrimitiveStatus.INVALID

    with pytest.raises(TypeError):
        EqualLiquidityConfig(tolerance_ticks=True)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        EqualLiquidityConfig(tolerance_ticks=3)


def test_12_pool_first_known_time_uses_second_founder_confirmation() -> None:
    first = _swing(EqualLiquiditySide.HIGH, 0, 100, confirmation_index=5)
    second = _swing(EqualLiquiditySide.HIGH, 3, 100, confirmation_index=8)
    pool = _latest(_analyze((first, second)))

    assert pool.first_known_provenance.confirmation_index == 8
    assert pool.first_known_provenance.confirmation_timestamp == T0 + timedelta(minutes=8)


@pytest.mark.parametrize("side", [EqualLiquiditySide.HIGH, EqualLiquiditySide.LOW])
def test_13_founding_confirmation_bar_cannot_consume_new_pool(
    side: EqualLiquiditySide,
) -> None:
    swings = _active_pool(side)
    observation = (
        _observation(5, high_tick=104, low_tick=99, close_tick=103)
        if side is EqualLiquiditySide.HIGH
        else _observation(5, high_tick=101, low_tick=96, close_tick=97)
    )
    result = _analyze(swings, (observation,))

    assert _latest(result).lifecycle_state is SMCV2LifecycleState.ACTIVE


def test_14_same_index_observation_precedes_existing_pool_member_join() -> None:
    founding = _active_pool(EqualLiquiditySide.HIGH)
    third = _swing(EqualLiquiditySide.HIGH, 5, 101)
    terminal = _observation(7, high_tick=103, low_tick=99, close_tick=102)
    result = _analyze((*founding, third), (terminal,))

    assert _latest(result).lifecycle_state is SMCV2LifecycleState.SWEPT
    assert len(_latest(result).member_swing_ids) == 2
    assert third.swing_id not in _latest(result).member_swing_ids


def test_15_terminal_same_index_event_prevents_all_later_joins() -> None:
    founding = _active_pool(EqualLiquiditySide.HIGH)
    same_index = _swing(EqualLiquiditySide.HIGH, 5, 101)
    later = _swing(EqualLiquiditySide.HIGH, 8, 100)
    terminal = _observation(7, high_tick=104, low_tick=99, close_tick=103)
    result = _analyze((*founding, same_index, later), (terminal,))

    old_lineage = result.pools[0].lineage_id
    old_snapshots = tuple(pool for pool in result.pools if pool.lineage_id == old_lineage)
    assert old_snapshots[-1].lifecycle_state is SMCV2LifecycleState.BROKEN
    assert all(len(pool.member_swing_ids) == 2 for pool in old_snapshots)


def test_16_later_member_join_preserves_earlier_snapshot() -> None:
    founding = _active_pool(EqualLiquiditySide.HIGH)
    third = _swing(EqualLiquiditySide.HIGH, 6, 101)
    result = _analyze((*founding, third))

    assert len(result.pools) == 2
    assert len(result.pools[0].member_swing_ids) == 2
    assert len(result.pools[1].member_swing_ids) == 3
    assert result.pools[0].snapshot_id != result.pools[1].snapshot_id


def test_17_multiple_clusters_choose_closest_current_reference() -> None:
    a1 = _swing(EqualLiquiditySide.HIGH, 0, 100)
    a2 = _swing(EqualLiquiditySide.HIGH, 3, 100)
    b1 = _swing(EqualLiquiditySide.HIGH, 6, 110)
    b2 = _swing(EqualLiquiditySide.HIGH, 9, 110)
    joining = _swing(EqualLiquiditySide.HIGH, 12, 109)
    result = _analyze((a1, a2, b1, b2, joining))

    joined = tuple(pool for pool in result.pools if joining.swing_id in pool.member_swing_ids)
    assert joined
    assert joined[-1].reference_tick == 110


def test_18_candidate_id_is_repeatable_and_side_aware() -> None:
    high = _swing(EqualLiquiditySide.HIGH, 0, 100)
    kwargs = {
        "identity_kind": "CANDIDATE",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "source_indices": (0,),
        "swing_ids": (high.swing_id,),
    }
    candidate_a = make_equal_liquidity_id(side=EqualLiquiditySide.HIGH, **kwargs)
    candidate_b = make_equal_liquidity_id(side=EqualLiquiditySide.HIGH, **kwargs)
    low = make_equal_liquidity_id(side=EqualLiquiditySide.LOW, **kwargs)

    assert candidate_a == candidate_b
    assert candidate_a != low
    assert len(candidate_a) == 64


def test_19_mixed_pending_and_active_tie_uses_assignment_identity() -> None:
    a1 = _swing(EqualLiquiditySide.HIGH, 0, 100, confirmation_index=5)
    b1 = _swing(EqualLiquiditySide.HIGH, 1, 102, confirmation_index=5)
    a2 = _swing(EqualLiquiditySide.HIGH, 3, 100, confirmation_index=6)
    joining = _swing(EqualLiquiditySide.HIGH, 6, 101, confirmation_index=8)
    prefix = _analyze((a1, b1, a2))
    active_lineage = prefix.pools[-1].lineage_id
    pending_id = make_equal_liquidity_id(
        identity_kind="CANDIDATE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=EqualLiquiditySide.HIGH,
        source_indices=(1,),
        swing_ids=(b1.swing_id,),
    )
    result = _analyze((a1, b1, a2, joining))

    joined_lineages = {
        pool.lineage_id for pool in result.pools if joining.swing_id in pool.member_swing_ids
    }
    if active_lineage < pending_id:
        assert joined_lineages == {active_lineage}
    else:
        assert joined_lineages and active_lineage not in joined_lineages


def test_20_pending_member_reservation_prevents_cross_candidate_reuse() -> None:
    a1 = _swing(EqualLiquiditySide.HIGH, 0, 100)
    b1 = _swing(EqualLiquiditySide.HIGH, 1, 110)
    b2 = _swing(EqualLiquiditySide.HIGH, 4, 110)
    a2 = _swing(EqualLiquiditySide.HIGH, 7, 100)
    result = _analyze((a1, b1, b2, a2))
    latest_by_lineage = {pool.lineage_id: pool for pool in result.pools}
    member_sets = [set(pool.member_swing_ids) for pool in latest_by_lineage.values()]

    assert len(member_sets) == 2
    assert member_sets[0].isdisjoint(member_sets[1])


def test_21_reservation_conversion_and_no_reuse_after_consumption() -> None:
    old = _active_pool(EqualLiquiditySide.HIGH)
    new1 = _swing(EqualLiquiditySide.HIGH, 7, 100)
    new2 = _swing(EqualLiquiditySide.HIGH, 10, 100)
    terminal = _observation(6, high_tick=104, low_tick=99, close_tick=103)
    result = _analyze((*old, new1, new2), (terminal,))
    latest_by_lineage = {pool.lineage_id: pool for pool in result.pools}

    assert len(latest_by_lineage) == 2
    member_sets = [set(pool.member_swing_ids) for pool in latest_by_lineage.values()]
    assert member_sets[0].isdisjoint(member_sets[1])


def test_22_tentative_all_member_containment_accepts_inclusive_boundary() -> None:
    swings = tuple(
        _swing(EqualLiquiditySide.HIGH, index, price)
        for index, price in ((0, 100), (3, 102), (6, 103), (9, 104))
    )
    result = _analyze(swings)

    assert len(_latest(result).member_swing_ids) == 4
    assert _latest(result).lower_tick == 100
    assert _latest(result).upper_tick == 104


def test_23_chain_drift_is_rejected_when_founder_leaves_new_band() -> None:
    swings = tuple(
        _swing(EqualLiquiditySide.HIGH, index, price)
        for index, price in ((0, 100), (3, 102), (6, 103), (9, 104), (12, 104))
    )
    result = _analyze(swings)

    assert max(len(pool.member_swing_ids) for pool in result.pools) == 4
    assert swings[-1].swing_id not in _latest(result).member_swing_ids


def test_24_locked_odd_and_half_even_medians() -> None:
    cases = (
        ((100, 101), 100),
        ((101, 102), 102),
        ((100, 102), 101),
        ((100, 102, 103), 102),
    )
    for prices, expected in cases:
        swings = tuple(
            _swing(EqualLiquiditySide.HIGH, offset * 3, price)
            for offset, price in enumerate(prices)
        )
        assert _latest(_analyze(swings)).reference_tick == expected


@pytest.mark.parametrize(
    ("observation", "expected"),
    [
        (_observation(6, high_tick=103, low_tick=99, close_tick=102), SMCV2LifecycleState.SWEPT),
        (_observation(6, high_tick=104, low_tick=99, close_tick=103), SMCV2LifecycleState.BROKEN),
        (_observation(6, high_tick=102, low_tick=99, close_tick=102), SMCV2LifecycleState.ACTIVE),
    ],
)
def test_25_equal_high_lifecycle_and_exact_boundary(
    observation: EqualLiquidityObservation,
    expected: SMCV2LifecycleState,
) -> None:
    result = _analyze(_active_pool(EqualLiquiditySide.HIGH), (observation,))

    assert _latest(result).lifecycle_state is expected


@pytest.mark.parametrize(
    ("observation", "expected"),
    [
        (_observation(6, high_tick=101, low_tick=97, close_tick=98), SMCV2LifecycleState.SWEPT),
        (_observation(6, high_tick=101, low_tick=96, close_tick=97), SMCV2LifecycleState.BROKEN),
        (_observation(6, high_tick=101, low_tick=98, close_tick=98), SMCV2LifecycleState.ACTIVE),
    ],
)
def test_26_equal_low_mirrors_lifecycle(
    observation: EqualLiquidityObservation,
    expected: SMCV2LifecycleState,
) -> None:
    result = _analyze(_active_pool(EqualLiquiditySide.LOW), (observation,))

    assert _latest(result).lifecycle_state is expected


def test_27_broken_is_terminal_and_cannot_transition_or_reactivate() -> None:
    founding = _active_pool(EqualLiquiditySide.HIGH)
    later = _swing(EqualLiquiditySide.HIGH, 8, 100)
    observations = (
        _observation(6, high_tick=104, low_tick=99, close_tick=103),
        _observation(7, high_tick=104, low_tick=99, close_tick=102),
    )
    result = _analyze((*founding, later), observations)
    old_lineage = result.pools[0].lineage_id
    old_snapshots = tuple(pool for pool in result.pools if pool.lineage_id == old_lineage)

    assert old_snapshots[-1].lifecycle_state is SMCV2LifecycleState.BROKEN
    assert len(old_snapshots[-1].lifecycle_events) == 2
    assert later.swing_id not in old_snapshots[-1].member_swing_ids


def test_28_lineage_is_stable_while_snapshot_id_changes() -> None:
    founding = _active_pool(EqualLiquiditySide.HIGH)
    third = _swing(EqualLiquiditySide.HIGH, 6, 101)
    result = _analyze((*founding, third))

    assert result.pools[0].lineage_id == result.pools[1].lineage_id
    assert result.pools[0].snapshot_id != result.pools[1].snapshot_id


def test_29_identical_runs_are_repeatable() -> None:
    swings = (*_active_pool(EqualLiquiditySide.HIGH), _swing(EqualLiquiditySide.HIGH, 6, 101))
    observations = (_observation(9, high_tick=104, low_tick=99, close_tick=103),)

    assert _analyze(swings, observations) == _analyze(swings, observations)


def test_30_appended_future_events_preserve_prior_snapshot_prefix() -> None:
    prefix_swings = (
        *_active_pool(EqualLiquiditySide.HIGH),
        _swing(EqualLiquiditySide.HIGH, 6, 101),
    )
    prefix = _analyze(prefix_swings)
    full = _analyze(
        (*prefix_swings, _swing(EqualLiquiditySide.HIGH, 9, 101)),
        (_observation(12, high_tick=104, low_tick=99, close_tick=103),),
    )

    assert full.pools[: len(prefix.pools)] == prefix.pools


def test_31_normalized_integer_tick_scaling_preserves_relationships() -> None:
    small = _analyze(_active_pool(EqualLiquiditySide.HIGH, first_price=21, second_price=23))
    large = _analyze(_active_pool(EqualLiquiditySide.HIGH, first_price=210, second_price=212))

    assert _latest(small).upper_tick - _latest(small).lower_tick == 4
    assert _latest(large).upper_tick - _latest(large).lower_tick == 4
    assert small.status is large.status is SMCV2PrimitiveStatus.VALID


def test_32_public_api_is_exact_and_models_are_frozen() -> None:
    assert equal_liquidity.__all__ == [
        "EQUAL_LIQUIDITY_DETECTOR_VERSION",
        "EqualLiquiditySide",
        "EqualLiquidityConfig",
        "EqualLiquiditySwing",
        "EqualLiquidityObservation",
        "EqualLiquidityPool",
        "EqualLiquidityResult",
        "make_equal_liquidity_id",
        "analyze_equal_liquidity",
    ]
    assert EQUAL_LIQUIDITY_DETECTOR_VERSION
    config = EqualLiquidityConfig()
    with pytest.raises(FrozenInstanceError):
        config.tolerance_ticks = 3  # type: ignore[misc]
    result = _analyze(_active_pool(EqualLiquiditySide.HIGH))
    with pytest.raises(FrozenInstanceError):
        result.status = SMCV2PrimitiveStatus.NONE  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.pools[0].reference_tick = 0  # type: ignore[misc]


def test_33_module_has_no_forbidden_runtime_or_integration_dependency() -> None:
    source = inspect.getsource(equal_liquidity)
    forbidden = (
        "pandas",
        "market_structure",
        "DecisionContext",
        "requests",
        "open(",
        "main.py",
        "paper",
        "broker",
    )

    assert all(marker not in source for marker in forbidden)
    assert not any(name.startswith("register") for name in equal_liquidity.__dict__)
    mutable_domain_globals = {
        name: value
        for name, value in equal_liquidity.__dict__.items()
        if not name.startswith("__")
        and name != "__all__"
        and isinstance(value, (list, dict, set))
    }
    assert mutable_domain_globals == {}
