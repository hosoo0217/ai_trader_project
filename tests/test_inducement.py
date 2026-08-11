from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import inspect
import re
from types import SimpleNamespace

import pytest

from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    DealingRangeSwingSide,
    DealingRangeTransition,
    make_dealing_range_id,
)
from smc.equal_liquidity import (
    EqualLiquidityPool,
    EqualLiquiditySide,
    make_equal_liquidity_id,
)
from smc.fair_value_gap import (
    FairValueGap,
    FairValueGapCandle,
    FairValueGapContextLink,
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    analyze_fair_value_gaps,
    make_fair_value_gap_id,
)
from smc.inducement import (
    INDUCEMENT_DETECTOR_VERSION,
    Inducement,
    InducementObservation,
    InducementResult,
    InducementSnapshot,
    analyze_inducements,
    make_inducement_id,
)
from smc.liquidity_map import (
    LiquidityMapSnapshot,
    LiquidityScope,
    LiquiditySide,
    LiquiditySourceKind,
    analyze_liquidity_map,
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
T0 = datetime(2026, 7, 29, 10, 0, tzinfo=UTC)
INSTRUMENT = "GC"
TIMEFRAME = "M5"


def _time(index: int) -> datetime:
    return T0 + timedelta(minutes=5 * index)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _provenance(
    source_indices: tuple[int, ...],
    confirmation_index: int,
) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(_time(index) for index in source_indices),
        confirmation_index=confirmation_index,
        confirmation_timestamp=_time(confirmation_index),
    )


def _observation(
    index: int,
    *,
    low_tick: int = 105,
    high_tick: int = 110,
    close_tick: int = 108,
    open_tick: int = 107,
    timestamp: datetime | None = None,
    is_closed: bool = True,
) -> InducementObservation:
    return InducementObservation(
        index=index,
        timestamp=_time(index) if timestamp is None else timestamp,
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
        is_closed=is_closed,
    )


def _swing(
    side: DealingRangeSwingSide,
    source_index: int,
    price_tick: int,
    confirmation_index: int,
) -> DealingRangeSwing:
    return DealingRangeSwing(
        side=side,
        price_tick=price_tick,
        provenance=_provenance((source_index,), confirmation_index),
        swing_id=_hash(f"swing:{side.value}:{source_index}:{price_tick}"),
    )


def _range_snapshot(
    direction: SMCV2Direction,
    *,
    low_tick: int = 90,
    high_tick: int = 120,
) -> tuple[tuple[DealingRangeSwing, ...], DealingRangeSnapshot]:
    low = _swing(DealingRangeSwingSide.LOW, 0, low_tick, 1)
    high = _swing(DealingRangeSwingSide.HIGH, 1, high_tick, 2)
    swings = (low, high)
    source_indices = (0, 1)
    swing_ids = (low.swing_id, high.swing_id)
    protected = low if direction is SMCV2Direction.BULLISH else high
    construction_event_id = _hash(f"construction:{direction.value}")
    boundaries = SMCV2TickRange(low_tick, high_tick)
    lineage_id = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices,
        swing_ids=swing_ids,
        boundaries=boundaries,
        protected_swing_id=protected.swing_id,
        construction_event_id=construction_event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    transition_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=(2,),
        lineage_id=lineage_id,
        transition_from_state=None,
        transition_to_state=DealingRangeState.ACTIVE,
        transition_index=2,
        transition_timestamp=_time(2),
        transition_reason="CONSTRUCTION_ACTIVE",
        related_event_id=construction_event_id,
    )
    transition = DealingRangeTransition(
        transition_id=transition_id,
        lineage_id=lineage_id,
        from_state=None,
        to_state=DealingRangeState.ACTIVE,
        index=2,
        timestamp=_time(2),
        reason="CONSTRUCTION_ACTIVE",
        related_event_id=construction_event_id,
        replacement_lineage_id=None,
    )
    snapshot_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices,
        swing_ids=swing_ids,
        boundaries=boundaries,
        lineage_id=lineage_id,
        construction_event_id=construction_event_id,
        range_kind=DealingRangeKind.EXTERNAL,
        state=DealingRangeState.ACTIVE,
        transition_ids=(transition_id,),
    )
    return swings, DealingRangeSnapshot(
        kind=DealingRangeKind.EXTERNAL,
        direction=direction,
        snapshot_id=snapshot_id,
        source_swing_ids=swing_ids,
        source_indices=source_indices,
        low_tick=low_tick,
        high_tick=high_tick,
        midpoint_tick=Decimal(low_tick + high_tick) / Decimal(2),
        first_known_provenance=_provenance((2,), 2),
        lineage_id=lineage_id,
        protected_swing_id=protected.swing_id,
        construction_event_id=construction_event_id,
        state=DealingRangeState.ACTIVE,
        transitions=(transition,),
        transition_ids=(transition_id,),
        replacement_lineage_id=None,
    )


def _pool(
    direction: SMCV2Direction,
) -> tuple[tuple[DealingRangeSwing, ...], EqualLiquidityPool, EqualLiquidityPool]:
    side = (
        EqualLiquiditySide.LOW
        if direction is SMCV2Direction.BULLISH
        else EqualLiquiditySide.HIGH
    )
    reference_tick = 100 if direction is SMCV2Direction.BULLISH else 110
    dealing_side = (
        DealingRangeSwingSide.LOW
        if side is EqualLiquiditySide.LOW
        else DealingRangeSwingSide.HIGH
    )
    members = (
        _swing(dealing_side, 0, reference_tick - 1, 1),
        _swing(dealing_side, 1, reference_tick + 1, 2),
    )
    source_indices = tuple(item.provenance.source_indices[0] for item in members)
    member_ids = tuple(item.swing_id for item in members)
    lower_tick, upper_tick = reference_tick - 2, reference_tick + 2
    lineage_id = make_equal_liquidity_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
    )
    first_known = _provenance(source_indices, 2)
    active_event = SMCV2LifecycleEvent(
        from_state=None,
        to_state=SMCV2LifecycleState.ACTIVE,
        index=2,
        timestamp=_time(2),
        reason="SECOND_EQUAL_SWING_CONFIRMED",
    )
    active_snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        lineage_id=lineage_id,
        lifecycle_state=SMCV2LifecycleState.ACTIVE,
    )
    active = EqualLiquidityPool(
        side=side,
        lineage_id=lineage_id,
        snapshot_id=active_snapshot_id,
        member_swing_ids=member_ids,
        source_indices=source_indices,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        first_known_provenance=first_known,
        lifecycle_state=SMCV2LifecycleState.ACTIVE,
        lifecycle_events=(active_event,),
    )
    swept_event = SMCV2LifecycleEvent(
        from_state=SMCV2LifecycleState.ACTIVE,
        to_state=SMCV2LifecycleState.SWEPT,
        index=5,
        timestamp=_time(5),
        reason="OBSERVATION_SWEEP",
    )
    swept_snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        lineage_id=lineage_id,
        lifecycle_state=SMCV2LifecycleState.SWEPT,
    )
    swept = replace(
        active,
        snapshot_id=swept_snapshot_id,
        lifecycle_state=SMCV2LifecycleState.SWEPT,
        lifecycle_events=(active_event, swept_event),
    )
    return members, active, swept


def _fvg(
    direction: SMCV2Direction,
    event_id: str,
    event_type: DealingRangeEventType,
) -> tuple[
    tuple[FairValueGap, ...],
    tuple[FairValueGapTransition, ...],
    tuple[FairValueGapSnapshot, ...],
]:
    if direction is SMCV2Direction.BULLISH:
        candles = (
            FairValueGapCandle(4, _time(4), 102, 104, 101, 103),
            FairValueGapCandle(5, _time(5), 103, 112, 102, 111),
            FairValueGapCandle(6, _time(6), 106, 110, 106, 109),
        )
    else:
        candles = (
            FairValueGapCandle(4, _time(4), 114, 115, 112, 113),
            FairValueGapCandle(5, _time(5), 113, 114, 102, 103),
            FairValueGapCandle(6, _time(6), 109, 110, 106, 107),
        )
    result = analyze_fair_value_gaps(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        candles=candles,
        context_links=(
            FairValueGapContextLink(
                formation_end_index=6,
                formation_end_timestamp=_time(6),
                displacement_id=_hash(f"displacement:{direction.value}"),
                structure_event_id=event_id,
                structure_event_type=event_type,
            ),
        ),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    return result.gaps, result.transitions, result.snapshots


def _fixture(
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    *,
    event_type: DealingRangeEventType = DealingRangeEventType.BOS,
) -> dict[str, object]:
    swings, active_range = _range_snapshot(direction)
    pool_swings, active_pool, swept_pool = _pool(direction)
    map_result = analyze_liquidity_map(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        swings=tuple(
            sorted(
                (*swings, *pool_swings),
                key=lambda item: (
                    item.provenance.confirmation_index,
                    item.provenance.source_indices[0],
                    item.side.value,
                    item.swing_id,
                ),
            )
        ),
        equal_liquidity_pools=(active_pool,),
        dealing_ranges=(active_range,),
    )
    assert map_result.status is SMCV2PrimitiveStatus.VALID
    event_id = _hash(f"event:{direction.value}")
    event = DealingRangeStructureEvent(
        direction=direction,
        event_type=event_type,
        broken_swing_id=(
            swings[1].swing_id
            if direction is SMCV2Direction.BULLISH
            else swings[0].swing_id
        ),
        provenance=_provenance((5, 6), 6),
        event_id=event_id,
    )
    gaps, gap_transitions, gap_snapshots = _fvg(direction, event_id, event_type)
    observations = tuple(_observation(index) for index in range(9))
    if direction is SMCV2Direction.BULLISH:
        observations = (
            *observations[:5],
            _observation(5, low_tick=97, high_tick=106, close_tick=99, open_tick=101),
            *observations[6:],
        )
    else:
        observations = (
            *observations[:5],
            _observation(5, low_tick=106, high_tick=113, close_tick=112, open_tick=109),
            *observations[6:],
        )
    return {
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "dealing_range_snapshots": (active_range,),
        "liquidity_map_snapshots": map_result.snapshots,
        "equal_liquidity_pools": (active_pool, swept_pool),
        "structure_events": (event,),
        "fair_value_gaps": gaps,
        "fair_value_gap_transitions": gap_transitions,
        "fair_value_gap_snapshots": gap_snapshots,
        "observations": observations,
    }


def _combined_fixture() -> dict[str, object]:
    bullish = _fixture(SMCV2Direction.BULLISH)
    bearish = _fixture(SMCV2Direction.BEARISH)
    observations = list(bullish["observations"])
    observations[5] = _observation(
        5,
        low_tick=97,
        high_tick=113,
        close_tick=105,
        open_tick=105,
    )

    def moment(value: object) -> tuple[int, datetime]:
        if isinstance(value, EqualLiquidityPool):
            event = value.lifecycle_events[-1]
            return event.index, event.timestamp
        return value.index, value.timestamp  # type: ignore[attr-defined]

    ranges = tuple(
        sorted(
            (*bullish["dealing_range_snapshots"], *bearish["dealing_range_snapshots"]),  # type: ignore[arg-type]
            key=lambda item: (
                item.first_known_provenance.confirmation_index,
                item.first_known_provenance.confirmation_timestamp,
                item.direction.value,
                item.snapshot_id,
            ),
        )
    )
    maps = tuple(
        sorted(
            (*bullish["liquidity_map_snapshots"], *bearish["liquidity_map_snapshots"]),  # type: ignore[arg-type]
            key=lambda item: (
                item.index,
                item.timestamp,
                item.active_range_lineage_id,
            ),
        )
    )
    pools = tuple(
        sorted(
            (*bullish["equal_liquidity_pools"], *bearish["equal_liquidity_pools"]),  # type: ignore[arg-type]
            key=lambda item: (*moment(item), item.lineage_id),
        )
    )
    events = tuple(
        sorted(
            (*bullish["structure_events"], *bearish["structure_events"]),  # type: ignore[arg-type]
            key=lambda item: (
                item.provenance.confirmation_index,
                item.provenance.confirmation_timestamp,
                item.direction.value,
                item.event_type.value,
                item.event_id,
            ),
        )
    )
    gaps = tuple(
        sorted(
            (*bullish["fair_value_gaps"], *bearish["fair_value_gaps"]),  # type: ignore[arg-type]
            key=lambda item: (
                item.formation_end_index,
                item.formation_end_timestamp,
                item.direction.value,
                item.source_indices,
                item.gap_id,
            ),
        )
    )
    gap_order = {item.gap_id: position for position, item in enumerate(gaps)}
    transitions = tuple(
        sorted(
            (*bullish["fair_value_gap_transitions"], *bearish["fair_value_gap_transitions"]),  # type: ignore[arg-type]
            key=lambda item: (item.index, item.timestamp, gap_order[item.gap_id]),
        )
    )
    snapshots = tuple(
        sorted(
            (*bullish["fair_value_gap_snapshots"], *bearish["fair_value_gap_snapshots"]),  # type: ignore[arg-type]
            key=lambda item: (item.index, item.timestamp, gap_order[item.gap_id]),
        )
    )
    return {
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "dealing_range_snapshots": ranges,
        "liquidity_map_snapshots": maps,
        "equal_liquidity_pools": pools,
        "structure_events": events,
        "fair_value_gaps": gaps,
        "fair_value_gap_transitions": transitions,
        "fair_value_gap_snapshots": snapshots,
        "observations": tuple(observations),
    }


def _analyze(**overrides: object) -> InducementResult:
    values = _fixture()
    values.update(overrides)
    return analyze_inducements(**values)  # type: ignore[arg-type]


def _malformed(instance: object, field_name: str) -> object:
    value = object.__new__(type(instance))
    for name, field_value in vars(instance).items():
        if name != field_name:
            object.__setattr__(value, name, field_value)
    return value


def _reversed_partial_fvg_snapshots(fixture: dict[str, object]) -> dict[str, object]:
    first = fixture["fair_value_gap_snapshots"][0]  # type: ignore[index]
    later_gap_id = _hash("later-independent-gap")
    later_transition_id = _hash("later-independent-transition")
    later_snapshot_id = make_fair_value_gap_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=first.direction,
        gap_id=later_gap_id,
        effective_index=7,
        effective_timestamp=_time(7),
        state=FairValueGapState.ACTIVE,
        transition_ids=(later_transition_id,),
    )
    later = FairValueGapSnapshot(
        snapshot_id=later_snapshot_id,
        gap_id=later_gap_id,
        direction=first.direction,
        state=FairValueGapState.ACTIVE,
        index=7,
        timestamp=_time(7),
        transition_ids=(later_transition_id,),
    )
    return {
        "fair_value_gap_transitions": None,
        "fair_value_gap_snapshots": (later, first),
    }


class _TupleSubclass(tuple):
    pass


def test_13_full_bullish_positive_sequence() -> None:
    result = _analyze()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.inducements[0].direction is SMCV2Direction.BULLISH


def test_14_full_bearish_mirror_positive_sequence() -> None:
    result = analyze_inducements(**_fixture(SMCV2Direction.BEARISH))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.inducements[0].direction is SMCV2Direction.BEARISH


def test_15_bullish_exact_one_tick_penetration_qualifies() -> None:
    result = _analyze()
    assert result.inducements[0].sweep_extreme_tick == 97


def test_15b_bullish_boundary_equality_reclaim_qualifies() -> None:
    result = _analyze()
    assert result.inducements[0].reclaim_close_tick == 99


def test_17_wick_contact_without_penetration_is_none() -> None:
    fixture = _fixture()
    observations = list(fixture["observations"])
    observations[5] = _observation(
        5,
        low_tick=98,
        high_tick=106,
        close_tick=99,
        open_tick=101,
    )
    result = _analyze(
        equal_liquidity_pools=(fixture["equal_liquidity_pools"][0],),  # type: ignore[index]
        observations=tuple(observations),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE


def test_21_bullish_internal_external_roles_are_side_correct() -> None:
    result = _analyze()
    assert result.inducements[0].external_target_classification_id


def test_09_canonical_pool_uses_lineage_source_identity() -> None:
    fixture = _fixture()
    pool = fixture["equal_liquidity_pools"][0]  # type: ignore[index]
    result = analyze_inducements(**fixture)  # type: ignore[arg-type]
    assert result.inducements[0].internal_pool_id == pool.lineage_id


def test_06_terminal_or_noncanonical_range_is_invalid() -> None:
    fixture = _fixture()
    active = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
    result = _analyze(
        dealing_range_snapshots=(replace(active, state=DealingRangeState.INVALIDATED),)
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_07_canonical_map_snapshot_is_bound_pre_group() -> None:
    result = _analyze()
    fixture = _fixture()
    assert result.inducements[0].liquidity_map_snapshot_id == fixture[
        "liquidity_map_snapshots"
    ][-1].snapshot_id  # type: ignore[index]


def test_20_internal_pool_must_be_strictly_inside_range() -> None:
    fixture = _fixture()
    pools = fixture["equal_liquidity_pools"]
    changed = tuple(replace(pool, lower_tick=90) for pool in pools)  # type: ignore[arg-type]
    result = _analyze(equal_liquidity_pools=changed)
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_11_structure_event_sources_reconcile_to_observations() -> None:
    fixture = _fixture()
    event = fixture["structure_events"][0]  # type: ignore[index]
    changed = replace(
        event,
        provenance=replace(
            event.provenance,
            source_timestamps=(_time(4), _time(6)),
        ),
    )
    assert _analyze(structure_events=(changed,)).status is SMCV2PrimitiveStatus.INVALID


def test_32_event_and_fvg_sources_require_positional_suffix() -> None:
    fixture = _fixture()
    event = fixture["structure_events"][0]  # type: ignore[index]
    changed = replace(event, provenance=_provenance((4, 6), 6))
    assert _analyze(structure_events=(changed,)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("offset", (1, 2, 3))
def test_25_to_27_confirmation_offsets_are_positional(offset: int) -> None:
    fixture = _fixture()
    event = fixture["structure_events"][0]  # type: ignore[index]
    sweep = 6 - offset
    observations = list(fixture["observations"])
    observations[sweep] = _observation(
        sweep, low_tick=97, high_tick=106, close_tick=99, open_tick=101
    )
    pools = fixture["equal_liquidity_pools"]
    swept = pools[1]  # type: ignore[index]
    events = list(swept.lifecycle_events)
    events[-1] = replace(events[-1], index=sweep, timestamp=_time(sweep))
    swept = replace(swept, lifecycle_events=tuple(events))
    result = _analyze(
        equal_liquidity_pools=(pools[0], swept),  # type: ignore[index]
        observations=tuple(observations),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.inducements[0].confirmation_offset_bars == offset


def test_28_same_or_fourth_bar_confirmation_does_not_qualify() -> None:
    fixture = _fixture()
    event = fixture["structure_events"][0]  # type: ignore[index]
    changed = replace(event, provenance=_provenance((5, 9), 9))
    assert _analyze(structure_events=(changed,)).status is not SMCV2PrimitiveStatus.VALID


def test_41_truncated_pending_window_is_unknown() -> None:
    fixture = _fixture()
    assert _analyze(
        structure_events=(),
        fair_value_gaps=(),
        fair_value_gap_transitions=(),
        fair_value_gap_snapshots=(),
        observations=fixture["observations"][:7],  # type: ignore[index]
    ).status is SMCV2PrimitiveStatus.UNKNOWN


def test_31_earliest_confirmation_wins() -> None:
    result = _analyze()
    assert result.inducements[0].confirmation_index == 6


def test_12_fvg_is_required_at_confirmation() -> None:
    assert _analyze(
        fair_value_gaps=(),
        fair_value_gap_transitions=(),
        fair_value_gap_snapshots=(),
    ).status is not SMCV2PrimitiveStatus.VALID


def test_32b_fvg_direction_must_match() -> None:
    fixture = _fixture()
    gap = fixture["fair_value_gaps"][0]  # type: ignore[index]
    assert _analyze(
        fair_value_gaps=(replace(gap, direction=SMCV2Direction.BEARISH),)
    ).status is SMCV2PrimitiveStatus.INVALID


def test_35_opaque_displacement_is_preserved_without_reproof() -> None:
    fixture = _fixture()
    gap = fixture["fair_value_gaps"][0]  # type: ignore[index]
    result = _analyze()
    assert result.inducements[0].displacement_id == gap.displacement_id


def test_33_first_known_is_exact_confirmation_time() -> None:
    result = _analyze()
    assert result.snapshots[0].index == result.inducements[0].confirmation_index
    assert result.snapshots[0].timestamp == result.inducements[0].confirmation_timestamp


def test_38_same_direction_candidate_output_is_deterministic() -> None:
    first = _analyze()
    second = _analyze()
    assert first == second


def test_37_opposing_same_group_status_vocabulary_is_available() -> None:
    assert SMCV2PrimitiveStatus.AMBIGUOUS.value == "AMBIGUOUS"


def test_40_unknowable_malformed_observation_is_invalid_without_leakage() -> None:
    observations = list(_fixture()["observations"])
    observations[5] = _malformed(observations[5], "index")
    result = _analyze(observations=tuple(observations))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == result.snapshots == ()


@pytest.mark.parametrize(
    "name",
    (
        "dealing_range_snapshots",
        "liquidity_map_snapshots",
        "equal_liquidity_pools",
        "structure_events",
        "fair_value_gaps",
        "fair_value_gap_transitions",
        "fair_value_gap_snapshots",
        "observations",
    ),
)
@pytest.mark.parametrize(
    "invalid_factory",
    (
        list,
        lambda: iter(()),
        dict,
        set,
        _TupleSubclass,
    ),
)
def test_02_non_tuple_inputs_are_invalid(
    name: str,
    invalid_factory: object,
) -> None:
    invalid = invalid_factory()  # type: ignore[operator]
    assert _analyze(**{name: invalid}).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "name",
    (
        "dealing_range_snapshots",
        "liquidity_map_snapshots",
        "equal_liquidity_pools",
        "structure_events",
        "fair_value_gaps",
        "fair_value_gap_transitions",
        "fair_value_gap_snapshots",
        "observations",
    ),
)
def test_01_missing_top_level_input_is_unknown(name: str) -> None:
    assert _analyze(**{name: None}).status is SMCV2PrimitiveStatus.UNKNOWN


@pytest.mark.parametrize(
    ("missing_name", "malformed_name", "malformed_factory"),
    (
        (
            "structure_events",
            "fair_value_gaps",
            lambda fixture: (
                replace(
                    fixture["fair_value_gaps"][0],
                    direction=SMCV2Direction.BEARISH,
                ),
            ),
        ),
        (
            "fair_value_gaps",
            "structure_events",
            lambda fixture: (
                _malformed(fixture["structure_events"][0], "event_id"),
            ),
        ),
    ),
)
def test_01_missing_top_level_does_not_mask_malformed_counterpart(
    missing_name: str,
    malformed_name: str,
    malformed_factory: object,
) -> None:
    fixture = _fixture()
    malformed = malformed_factory(fixture)  # type: ignore[operator]
    result = _analyze(**{missing_name: None, malformed_name: malformed})
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == ()
    assert result.snapshots == ()


@pytest.mark.parametrize(
    "malformed_history_factory",
    (
        lambda fixture: {
            "fair_value_gap_transitions": (
                _malformed(fixture["fair_value_gap_transitions"][0], "reason"),
            ),
            "fair_value_gap_snapshots": None,
        },
        lambda fixture: {
            "fair_value_gap_transitions": None,
            "fair_value_gap_snapshots": (
                _malformed(fixture["fair_value_gap_snapshots"][0], "state"),
            ),
        },
        lambda fixture: {
            "fair_value_gap_transitions": (
                replace(
                    fixture["fair_value_gap_transitions"][0],
                    transition_id=_hash("later-independent-transition"),
                    gap_id=_hash("later-independent-gap"),
                    index=7,
                    timestamp=_time(7),
                ),
                fixture["fair_value_gap_transitions"][0],
            ),
            "fair_value_gap_snapshots": None,
        },
        lambda fixture: _reversed_partial_fvg_snapshots(fixture),
    ),
)
def test_01_missing_gap_does_not_mask_malformed_partial_history(
    malformed_history_factory: object,
) -> None:
    fixture = _fixture()
    malformed_history = malformed_history_factory(fixture)  # type: ignore[operator]
    result = _analyze(fair_value_gaps=None, **malformed_history)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == ()
    assert result.snapshots == ()


def test_03_observation_contract_is_exact_frozen_closed_integer_ohlc() -> None:
    valid = _observation(1)
    with pytest.raises(FrozenInstanceError):
        valid.close_tick = 999  # type: ignore[misc]
    for changed in (
        replace(valid, is_closed=False),
        replace(valid, close_tick=True),
        replace(valid, low_tick=111),
        replace(valid, open_tick=200),
    ):
        assert _analyze(observations=(changed,)).status is SMCV2PrimitiveStatus.INVALID
    assert _analyze(observations=(_malformed(valid, "index"),)).status is SMCV2PrimitiveStatus.INVALID


def test_05_canonical_bullish_and_bearish_external_ranges_validate() -> None:
    for direction in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        fixture = _fixture(direction)
        snapshot = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
        assert snapshot.kind is DealingRangeKind.EXTERNAL
        assert snapshot.state is DealingRangeState.ACTIVE
        assert analyze_inducements(**fixture).status is SMCV2PrimitiveStatus.VALID  # type: ignore[arg-type]


def test_10_pool_lifecycle_source_and_effective_moment_fail_closed() -> None:
    fixture = _fixture()
    active, swept = fixture["equal_liquidity_pools"]  # type: ignore[misc]
    for changed in (
        replace(active, snapshot_id=_hash("wrong-pool")),
        replace(active, side=EqualLiquiditySide.HIGH),
        replace(swept, lifecycle_events=()),
    ):
        assert _analyze(equal_liquidity_pools=(changed,)).status is SMCV2PrimitiveStatus.INVALID


def test_41b_complete_empty_inputs_are_none() -> None:
    result = analyze_inducements(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        dealing_range_snapshots=(),
        liquidity_map_snapshots=(),
        equal_liquidity_pools=(),
        structure_events=(),
        fair_value_gaps=(),
        fair_value_gap_transitions=(),
        fair_value_gap_snapshots=(),
        observations=(),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE


def test_04_observation_order_is_not_silently_sorted() -> None:
    observations = _fixture()["observations"]
    assert _analyze(
        observations=(*observations[:4], observations[5], observations[4], *observations[6:])  # type: ignore[index]
    ).status is SMCV2PrimitiveStatus.INVALID


def test_06b_range_snapshot_foreign_identity_is_validated() -> None:
    fixture = _fixture()
    snapshot = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
    assert _analyze(
        dealing_range_snapshots=(replace(snapshot, snapshot_id=_hash("wrong")),)
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("malformation", ("transition_type", "midpoint_type"))
def test_06c_range_nested_fields_require_exact_canonical_types(
    malformation: str,
) -> None:
    fixture = _fixture()
    snapshot = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
    if malformation == "transition_type":
        transition = snapshot.transitions[0]
        changed = replace(
            snapshot,
            transitions=(
                SimpleNamespace(
                    **{
                        field.name: getattr(transition, field.name)
                        for field in fields(DealingRangeTransition)
                    }
                ),
            ),
        )
    else:
        changed = replace(snapshot, midpoint_tick=float(snapshot.midpoint_tick))
    assert _analyze(
        dealing_range_snapshots=(changed,)
    ).status is SMCV2PrimitiveStatus.INVALID


def test_06d_range_stream_uses_final_transition_effective_moment() -> None:
    fixture = _fixture()
    active = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
    transition_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=active.direction,
        source_indices=(8,),
        lineage_id=active.lineage_id,
        transition_from_state=DealingRangeState.ACTIVE,
        transition_to_state=DealingRangeState.INVALIDATED,
        transition_index=8,
        transition_timestamp=_time(8),
        transition_reason="OBSERVATION_CLOSE_THROUGH_INVALIDATION",
    )
    terminal_transition = DealingRangeTransition(
        transition_id=transition_id,
        lineage_id=active.lineage_id or "",
        from_state=DealingRangeState.ACTIVE,
        to_state=DealingRangeState.INVALIDATED,
        index=8,
        timestamp=_time(8),
        reason="OBSERVATION_CLOSE_THROUGH_INVALIDATION",
        related_event_id=None,
        replacement_lineage_id=None,
    )
    transition_ids = (*active.transition_ids, transition_id)
    terminal_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=active.direction,
        source_indices=active.source_indices,
        swing_ids=active.source_swing_ids,
        boundaries=SMCV2TickRange(active.low_tick, active.high_tick),
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        range_kind=active.kind,
        state=DealingRangeState.INVALIDATED,
        transition_ids=transition_ids,
        replacement_lineage_id=None,
    )
    terminal = replace(
        active,
        snapshot_id=terminal_id,
        state=DealingRangeState.INVALIDATED,
        transitions=(*active.transitions, terminal_transition),
        transition_ids=transition_ids,
    )
    assert _analyze(
        dealing_range_snapshots=(terminal, active)
    ).status is SMCV2PrimitiveStatus.INVALID


def test_08_liquidity_map_snapshot_foreign_identity_is_validated() -> None:
    fixture = _fixture()
    snapshot = fixture["liquidity_map_snapshots"][0]  # type: ignore[index]
    assert _analyze(
        liquidity_map_snapshots=(replace(snapshot, snapshot_id=_hash("wrong")),)
    ).status is SMCV2PrimitiveStatus.INVALID


def test_08b_classification_lineage_must_match_map_lineage() -> None:
    fixture = _fixture()
    snapshots = fixture["liquidity_map_snapshots"]  # type: ignore[assignment]
    snapshot = snapshots[0]
    classifications = snapshot.classifications
    changed = replace(
        snapshot,
        classifications=(
            replace(
                classifications[0],
                active_range_lineage_id=_hash("wrong-classification-lineage"),
            ),
            *classifications[1:],
        ),
    )
    assert _analyze(
        liquidity_map_snapshots=(changed, *snapshots[1:])
    ).status is SMCV2PrimitiveStatus.INVALID


def test_12c_fvg_canonical_order_includes_source_indices() -> None:
    fixture = _fixture()
    gap = fixture["fair_value_gaps"][0]  # type: ignore[index]
    assert gap.source_indices == (4, 5, 6)


def test_34_fvg_transition_history_is_complete() -> None:
    fixture = _fixture()
    assert _analyze(fair_value_gap_transitions=()).status is SMCV2PrimitiveStatus.INVALID


def test_34b_fvg_snapshot_mirrors_transition() -> None:
    fixture = _fixture()
    snapshot = fixture["fair_value_gap_snapshots"][0]  # type: ignore[index]
    assert _analyze(
        fair_value_gap_snapshots=(replace(snapshot, transition_ids=()),)
    ).status is SMCV2PrimitiveStatus.INVALID


def test_42_inducement_identity_is_repeatable_and_sensitive() -> None:
    result = _analyze()
    item = result.inducements[0]
    kwargs = {
        "identity_kind": "INDUCEMENT",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        **{field.name: getattr(item, field.name) for field in fields(Inducement) if field.name != "inducement_id"},
    }
    assert item.inducement_id == make_inducement_id(**kwargs)
    assert item.inducement_id != make_inducement_id(
        **{**kwargs, "reclaim_close_tick": item.reclaim_close_tick + 1}
    )


def test_43_snapshot_identity_recomputes() -> None:
    result = _analyze()
    snapshot = result.snapshots[0]
    assert snapshot.snapshot_id == make_inducement_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        effective_index=snapshot.index,
        effective_timestamp=snapshot.timestamp,
        inducement_ids=snapshot.inducement_ids,
    )


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("direction", SMCV2Direction.BULLISH),
        ("active_range_lineage_id", _hash("range")),
        ("sweep_index", 5),
        ("structure_event_type", DealingRangeEventType.BOS),
        ("fair_value_gap_id", _hash("gap")),
    ),
)
def test_43b_snapshot_identity_forbids_source_fields(
    name: str,
    value: object,
) -> None:
    snapshot = _analyze().snapshots[0]
    base = {
        "identity_kind": "SNAPSHOT",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "effective_index": snapshot.index,
        "effective_timestamp": snapshot.timestamp,
        "inducement_ids": snapshot.inducement_ids,
    }
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(**{**base, name: value})


@pytest.mark.parametrize(
    "changes",
    (
        {"effective_index": None},
        {"effective_timestamp": None},
        {"inducement_ids": ()},
        {"inducement_ids": ("A" * 64,)},
        {"inducement_ids": (_hash("same"), _hash("same"))},
    ),
)
def test_43c_snapshot_identity_rejects_missing_or_malformed_history(
    changes: dict[str, object],
) -> None:
    snapshot = _analyze().snapshots[0]
    base = {
        "identity_kind": "SNAPSHOT",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        "effective_index": snapshot.index,
        "effective_timestamp": snapshot.timestamp,
        "inducement_ids": snapshot.inducement_ids,
    }
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(**{**base, **changes})


def test_42b_identity_required_forbidden_schemas_fail_closed() -> None:
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(
            identity_kind="SNAPSHOT",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            effective_index=6,
            effective_timestamp=_time(6),
            inducement_ids=(),
        )
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(
            identity_kind="UNKNOWN",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
        )


def test_42c_instrument_timeframe_and_utc_normalization_are_deterministic() -> None:
    result = _analyze()
    item = result.inducements[0]
    kwargs = {
        "identity_kind": "INDUCEMENT",
        "instrument": " gc ",
        "timeframe": " m5 ",
        **{field.name: getattr(item, field.name) for field in fields(Inducement) if field.name != "inducement_id"},
    }
    assert item.inducement_id == make_inducement_id(**kwargs)


@pytest.mark.parametrize(
    "required_name",
    (
        "direction",
        "active_range_lineage_id",
        "active_range_snapshot_id",
        "liquidity_map_snapshot_id",
        "external_target_classification_id",
        "internal_pool_classification_id",
        "internal_pool_id",
        "sweep_index",
        "sweep_timestamp",
        "sweep_extreme_tick",
        "reclaim_close_tick",
        "structure_event_id",
        "structure_event_type",
        "confirmation_index",
        "confirmation_timestamp",
        "confirmation_offset_bars",
        "fair_value_gap_id",
        "displacement_id",
    ),
)
def test_42d_inducement_identity_requires_every_source_field(
    required_name: str,
) -> None:
    item = _analyze().inducements[0]
    kwargs = {
        "identity_kind": "INDUCEMENT",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        **{
            field.name: getattr(item, field.name)
            for field in fields(Inducement)
            if field.name != "inducement_id"
        },
    }
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(**{**kwargs, required_name: None})


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("effective_index", 6),
        ("effective_timestamp", T0),
        ("inducement_ids", (_hash("forbidden"),)),
    ),
)
def test_42e_inducement_identity_forbids_snapshot_fields(
    name: str,
    value: object,
) -> None:
    item = _analyze().inducements[0]
    kwargs = {
        "identity_kind": "INDUCEMENT",
        "instrument": INSTRUMENT,
        "timeframe": TIMEFRAME,
        **{
            field.name: getattr(item, field.name)
            for field in fields(Inducement)
            if field.name != "inducement_id"
        },
    }
    with pytest.raises((TypeError, ValueError)):
        make_inducement_id(**{**kwargs, name: value})


def test_44_public_api_is_exact_keyword_only() -> None:
    analyzer = inspect.signature(analyze_inducements)
    builder = inspect.signature(make_inducement_id)
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in analyzer.parameters.values()
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in builder.parameters.values()
    )
    assert tuple(analyzer.parameters) == (
        "instrument",
        "timeframe",
        "dealing_range_snapshots",
        "liquidity_map_snapshots",
        "equal_liquidity_pools",
        "structure_events",
        "fair_value_gaps",
        "fair_value_gap_transitions",
        "fair_value_gap_snapshots",
        "observations",
    )
    assert tuple(builder.parameters) == (
        "identity_kind",
        "instrument",
        "timeframe",
        "direction",
        "active_range_lineage_id",
        "active_range_snapshot_id",
        "liquidity_map_snapshot_id",
        "external_target_classification_id",
        "internal_pool_classification_id",
        "internal_pool_id",
        "sweep_index",
        "sweep_timestamp",
        "sweep_extreme_tick",
        "reclaim_close_tick",
        "structure_event_id",
        "structure_event_type",
        "confirmation_index",
        "confirmation_timestamp",
        "confirmation_offset_bars",
        "fair_value_gap_id",
        "displacement_id",
        "effective_index",
        "effective_timestamp",
        "inducement_ids",
    )
    assert all(
        analyzer.parameters[name].default is inspect.Parameter.empty
        for name in analyzer.parameters
    )
    assert all(
        builder.parameters[name].default is None
        for name in tuple(builder.parameters)[3:-1]
    )
    assert builder.parameters["inducement_ids"].default == ()
    assert analyzer.return_annotation in (InducementResult, "InducementResult")
    assert builder.return_annotation in (str, "str")


def test_45_public_dataclasses_are_frozen_with_exact_fields() -> None:
    assert tuple(field.name for field in fields(InducementObservation)) == (
        "index",
        "timestamp",
        "open_tick",
        "high_tick",
        "low_tick",
        "close_tick",
        "is_closed",
    )
    result = _analyze()
    with pytest.raises(FrozenInstanceError):
        result.inducements[0].direction = SMCV2Direction.BEARISH  # type: ignore[misc]
    assert tuple(field.name for field in fields(InducementResult)) == (
        "status",
        "inducements",
        "snapshots",
        "reasons",
        "blocking_reasons",
    )
    assert tuple(field.name for field in fields(Inducement)) == (
        "inducement_id",
        "direction",
        "active_range_lineage_id",
        "active_range_snapshot_id",
        "liquidity_map_snapshot_id",
        "external_target_classification_id",
        "internal_pool_classification_id",
        "internal_pool_id",
        "sweep_index",
        "sweep_timestamp",
        "sweep_extreme_tick",
        "reclaim_close_tick",
        "structure_event_id",
        "structure_event_type",
        "confirmation_index",
        "confirmation_timestamp",
        "confirmation_offset_bars",
        "fair_value_gap_id",
        "displacement_id",
    )
    assert tuple(field.name for field in fields(InducementSnapshot)) == (
        "snapshot_id",
        "index",
        "timestamp",
        "inducement_ids",
    )
    result_fields = {field.name: field for field in fields(InducementResult)}
    assert result_fields["inducements"].default == ()
    assert result_fields["snapshots"].default == ()
    assert result_fields["reasons"].default == ()
    assert result_fields["blocking_reasons"].default == ()


def test_44b_version_status_and_exports_are_locked() -> None:
    import smc.inducement as module

    assert not hasattr(module, "replace_observation_timestamp")
    assert INDUCEMENT_DETECTOR_VERSION == "SMC-V2-INDUCEMENT-1"
    assert tuple(module.__all__) == (
        "INDUCEMENT_DETECTOR_VERSION",
        "InducementObservation",
        "Inducement",
        "InducementSnapshot",
        "InducementResult",
        "make_inducement_id",
        "analyze_inducements",
    )


def test_47_strictly_later_complete_append_preserves_prefix() -> None:
    first = _analyze()
    fixture = _fixture()
    observations = fixture["observations"]
    second = _analyze(observations=(*observations, _observation(9)))  # type: ignore[arg-type]
    assert second.inducements[: len(first.inducements)] == first.inducements
    assert second.snapshots[: len(first.snapshots)] == first.snapshots


def test_47b_same_effective_append_is_not_silently_repaired() -> None:
    observations = _fixture()["observations"]
    duplicate = replace(observations[-1], close_tick=observations[-1].close_tick - 1)  # type: ignore[index]
    assert _analyze(observations=(*observations, duplicate)).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "reordered_streams",
    ("transitions", "snapshots", "both"),
)
def test_47d_same_moment_fvg_streams_follow_gap_order_and_mirror(
    reordered_streams: str,
) -> None:
    fixture = _combined_fixture()
    assert analyze_inducements(**fixture).status is SMCV2PrimitiveStatus.AMBIGUOUS  # type: ignore[arg-type]
    if reordered_streams in ("transitions", "both"):
        fixture["fair_value_gap_transitions"] = tuple(
            reversed(fixture["fair_value_gap_transitions"])  # type: ignore[arg-type]
        )
    if reordered_streams in ("snapshots", "both"):
        fixture["fair_value_gap_snapshots"] = tuple(
            reversed(fixture["fair_value_gap_snapshots"])  # type: ignore[arg-type]
        )
    result = analyze_inducements(**fixture)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == result.snapshots == ()


@pytest.mark.parametrize(
    "kind",
    ("observation", "range", "map", "pool", "event", "gap"),
)
def test_39_determinably_later_malformed_preserves_prior_evidence(
    kind: str,
) -> None:
    first = _analyze()
    assert first.inducements and first.snapshots
    fixture = _fixture()
    overrides: dict[str, object] = {}
    if kind == "observation":
        malformed = _malformed(_observation(9), "close_tick")
        overrides["observations"] = (*fixture["observations"], malformed)  # type: ignore[arg-type]
    elif kind == "range":
        active = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
        bad_transition = replace(
            active.transitions[-1],
            index=9,
            timestamp=_time(9),
        )
        bad = replace(
            active,
            snapshot_id=_hash("later-bad-range"),
            transitions=(*active.transitions, bad_transition),
            transition_ids=(*active.transition_ids, bad_transition.transition_id),
        )
        overrides["dealing_range_snapshots"] = (active, bad)
    elif kind == "map":
        active = fixture["liquidity_map_snapshots"][-1]  # type: ignore[index]
        bad = replace(
            active,
            snapshot_id=_hash("later-bad-map"),
            index=9,
            timestamp=_time(9),
        )
        overrides["liquidity_map_snapshots"] = (
            *fixture["liquidity_map_snapshots"],  # type: ignore[arg-type]
            bad,
        )
    elif kind == "pool":
        active, swept = fixture["equal_liquidity_pools"]  # type: ignore[misc]
        bad_event = SMCV2LifecycleEvent(
            from_state=SMCV2LifecycleState.SWEPT,
            to_state=SMCV2LifecycleState.ACTIVE,
            index=9,
            timestamp=_time(9),
            reason="FORBIDDEN_REACTIVATION",
        )
        bad = replace(
            swept,
            snapshot_id=_hash("later-bad-pool"),
            lifecycle_events=(*swept.lifecycle_events, bad_event),
        )
        overrides["equal_liquidity_pools"] = (active, swept, bad)
    elif kind == "event":
        event = fixture["structure_events"][0]  # type: ignore[index]
        later = replace(event, provenance=_provenance((8, 9), 9))
        overrides["structure_events"] = (
            event,
            _malformed(later, "event_id"),
        )
    else:
        gap = fixture["fair_value_gaps"][0]  # type: ignore[index]
        later = replace(
            gap,
            formation_end_index=9,
            formation_end_timestamp=_time(9),
            source_indices=(7, 8, 9),
            source_timestamps=(_time(7), _time(8), _time(9)),
        )
        overrides["fair_value_gaps"] = (gap, later)
    result = _analyze(**overrides)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == first.inducements
    assert result.snapshots == first.snapshots


def test_46_invalid_precedence_beats_unknown() -> None:
    fixture = _fixture()
    observations = list(fixture["observations"])
    observations[5] = _malformed(observations[5], "low_tick")
    result = _analyze(observations=tuple(observations), structure_events=None)
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_41_unknown_precedence_preserves_prior_valid_evidence() -> None:
    prior_fixture = _fixture(SMCV2Direction.BULLISH)
    prior_observations = list(prior_fixture["observations"])
    prior_observations[5] = _observation(
        5,
        low_tick=97,
        high_tick=110,
        close_tick=105,
        open_tick=105,
    )
    prior_fixture["observations"] = tuple(prior_observations)
    prior = analyze_inducements(**prior_fixture)  # type: ignore[arg-type]
    assert prior.status is SMCV2PrimitiveStatus.VALID

    fixture = _combined_fixture()
    observations = list(fixture["observations"])
    observations[5] = prior_observations[5]
    observations[7] = _observation(
        7,
        low_tick=105,
        high_tick=113,
        close_tick=105,
        open_tick=107,
    )
    fixture["observations"] = tuple(observations)

    pools = []
    for pool in fixture["equal_liquidity_pools"]:  # type: ignore[union-attr]
        if (
            pool.side is EqualLiquiditySide.HIGH
            and pool.lifecycle_state is SMCV2LifecycleState.SWEPT
        ):
            terminal = replace(
                pool.lifecycle_events[-1],
                index=7,
                timestamp=_time(7),
            )
            pool = replace(
                pool,
                lifecycle_events=(*pool.lifecycle_events[:-1], terminal),
            )
        pools.append(pool)
    fixture["equal_liquidity_pools"] = tuple(
        sorted(
            pools,
            key=lambda item: (
                item.lifecycle_events[-1].index,
                item.lifecycle_events[-1].timestamp,
                item.lineage_id,
            ),
        )
    )
    fixture["structure_events"] = tuple(
        item
        for item in fixture["structure_events"]  # type: ignore[union-attr]
        if item.direction is SMCV2Direction.BULLISH
    )
    fixture["fair_value_gaps"] = tuple(
        item
        for item in fixture["fair_value_gaps"]  # type: ignore[union-attr]
        if item.direction is SMCV2Direction.BULLISH
    )
    bullish_gap_ids = {
        item.gap_id for item in fixture["fair_value_gaps"]  # type: ignore[union-attr]
    }
    fixture["fair_value_gap_transitions"] = tuple(
        item
        for item in fixture["fair_value_gap_transitions"]  # type: ignore[union-attr]
        if item.gap_id in bullish_gap_ids
    )
    fixture["fair_value_gap_snapshots"] = tuple(
        item
        for item in fixture["fair_value_gap_snapshots"]  # type: ignore[union-attr]
        if item.gap_id in bullish_gap_ids
    )

    result = analyze_inducements(**fixture)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.inducements == prior.inducements
    assert result.snapshots == prior.snapshots


def test_47c_repeatability_is_byte_stable_at_object_level() -> None:
    assert repr(_analyze()) == repr(_analyze())


def test_36_no_outcome_or_integration_surface_exists() -> None:
    source = inspect.getsource(inspect.getmodule(analyze_inducements))
    for forbidden in ("pnl", "entry_price", "exit_price", "broker", "orderflow"):
        assert forbidden not in source.lower()


def test_16_bearish_exact_one_tick_and_upper_reclaim_equality() -> None:
    result = analyze_inducements(**_fixture(SMCV2Direction.BEARISH))  # type: ignore[arg-type]
    item = result.inducements[0]
    assert item.sweep_extreme_tick == 113
    assert item.reclaim_close_tick == 112


def test_18_penetration_without_reclaim_is_none() -> None:
    fixture = _fixture()
    active = fixture["equal_liquidity_pools"][0]  # type: ignore[index]
    broken_event = SMCV2LifecycleEvent(
        from_state=SMCV2LifecycleState.ACTIVE,
        to_state=SMCV2LifecycleState.BROKEN,
        index=5,
        timestamp=_time(5),
        reason="CLOSE_THROUGH_BREAK",
    )
    broken_snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=active.side,
        source_indices=active.source_indices,
        swing_ids=active.member_swing_ids,
        reference_tick=active.reference_tick,
        lower_tick=active.lower_tick,
        upper_tick=active.upper_tick,
        lineage_id=active.lineage_id,
        lifecycle_state=SMCV2LifecycleState.BROKEN,
    )
    broken = replace(
        active,
        snapshot_id=broken_snapshot_id,
        lifecycle_state=SMCV2LifecycleState.BROKEN,
        lifecycle_events=(*active.lifecycle_events, broken_event),
    )
    observations = list(fixture["observations"])
    observations[5] = _observation(
        5,
        low_tick=97,
        high_tick=106,
        close_tick=97,
        open_tick=101,
    )
    result = _analyze(
        equal_liquidity_pools=(active, broken),
        observations=tuple(observations),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE


def test_19_pool_formation_moment_cannot_be_reused_as_sweep() -> None:
    fixture = _fixture()
    active, swept = fixture["equal_liquidity_pools"]  # type: ignore[misc]
    terminal = replace(
        swept.lifecycle_events[-1],
        index=2,
        timestamp=_time(2),
    )
    swept = replace(
        swept,
        lifecycle_events=(active.lifecycle_events[0], terminal),
    )
    observations = list(fixture["observations"])
    observations[2] = _observation(
        2,
        low_tick=97,
        high_tick=106,
        close_tick=99,
        open_tick=101,
    )
    assert _analyze(
        equal_liquidity_pools=(active, swept),
        observations=tuple(observations),
    ).status is SMCV2PrimitiveStatus.INVALID


def test_22_external_target_must_remain_beyond_reclaimed_close() -> None:
    fixture = _fixture()
    observations = list(fixture["observations"])
    observations[5] = _observation(
        5,
        low_tick=97,
        high_tick=121,
        close_tick=120,
        open_tick=101,
    )
    assert _analyze(observations=tuple(observations)).status is SMCV2PrimitiveStatus.NONE


def test_22b_range_termination_before_confirmation_makes_sequence_ineligible() -> None:
    fixture = _fixture()
    active = fixture["dealing_range_snapshots"][0]  # type: ignore[index]
    transition_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=active.direction,
        source_indices=(6,),
        lineage_id=active.lineage_id,
        transition_from_state=DealingRangeState.ACTIVE,
        transition_to_state=DealingRangeState.INVALIDATED,
        transition_index=6,
        transition_timestamp=_time(6),
        transition_reason="OBSERVATION_CLOSE_THROUGH_INVALIDATION",
    )
    terminal_transition = DealingRangeTransition(
        transition_id=transition_id,
        lineage_id=active.lineage_id or "",
        from_state=DealingRangeState.ACTIVE,
        to_state=DealingRangeState.INVALIDATED,
        index=6,
        timestamp=_time(6),
        reason="OBSERVATION_CLOSE_THROUGH_INVALIDATION",
        related_event_id=None,
        replacement_lineage_id=None,
    )
    transition_ids = (*active.transition_ids, transition_id)
    terminal_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=active.direction,
        source_indices=active.source_indices,
        swing_ids=active.source_swing_ids,
        boundaries=SMCV2TickRange(active.low_tick, active.high_tick),
        lineage_id=active.lineage_id,
        construction_event_id=active.construction_event_id,
        range_kind=active.kind,
        state=DealingRangeState.INVALIDATED,
        transition_ids=transition_ids,
        replacement_lineage_id=None,
    )
    terminal = replace(
        active,
        snapshot_id=terminal_id,
        state=DealingRangeState.INVALIDATED,
        transitions=(*active.transitions, terminal_transition),
        transition_ids=transition_ids,
    )

    result = _analyze(dealing_range_snapshots=(active, terminal))

    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.inducements == ()
    assert result.snapshots == ()


def test_23_nearest_external_target_selection_is_deterministic() -> None:
    fixture = _fixture()
    snapshot = fixture["liquidity_map_snapshots"][-1]  # type: ignore[index]
    targets = tuple(
        item
        for item in snapshot.classifications
        if item.scope is LiquidityScope.EXTERNAL
        and item.side is LiquiditySide.BUY_SIDE
        and item.boundaries.lower_tick > 99
    )
    result = _analyze()
    expected = min(
        targets,
        key=lambda item: (item.boundaries.lower_tick, item.classification_id),
    )
    assert result.inducements[0].external_target_classification_id == expected.classification_id


def test_24_independent_pool_candidate_has_no_reuse_and_stable_order() -> None:
    result = _analyze()
    assert len({item.internal_pool_id for item in result.inducements}) == len(
        result.inducements
    )
    assert result.inducements == tuple(
        sorted(
            result.inducements,
            key=lambda item: (
                item.confirmation_index,
                item.confirmation_timestamp,
                item.direction.value,
                item.sweep_index,
                item.internal_pool_id,
                item.inducement_id,
            ),
        )
    )


@pytest.mark.parametrize(
    ("direction", "event_type"),
    (
        (SMCV2Direction.BULLISH, DealingRangeEventType.BOS),
        (SMCV2Direction.BEARISH, DealingRangeEventType.BOS),
    ),
)
def test_29_bullish_and_bearish_bos_confirm(
    direction: SMCV2Direction,
    event_type: DealingRangeEventType,
) -> None:
    fixture = _fixture(direction, event_type=event_type)
    result = analyze_inducements(**fixture)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.inducements[0].structure_event_type is event_type


@pytest.mark.parametrize(
    "direction",
    (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH),
)
def test_30_bullish_and_bearish_choch_confirm(
    direction: SMCV2Direction,
) -> None:
    fixture = _fixture(direction, event_type=DealingRangeEventType.CHOCH)
    result = analyze_inducements(**fixture)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.inducements[0].structure_event_type is DealingRangeEventType.CHOCH


def test_37_simultaneous_opposing_group_is_ambiguous_without_promotion() -> None:
    result = analyze_inducements(**_combined_fixture())  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert result.inducements == result.snapshots == ()


def test_48_exception_containment_and_forbidden_surface() -> None:
    fixture = _fixture()
    gap = fixture["fair_value_gaps"][0]  # type: ignore[index]
    malformed = _malformed(gap, "source_indices")
    result = _analyze(fair_value_gaps=(malformed,))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.inducements == result.snapshots == ()
    source = inspect.getsource(inspect.getmodule(analyze_inducements)).lower()
    for forbidden in ("requests", "urllib", "socket", "subprocess", "broker"):
        assert forbidden not in source


def test_48_logical_matrix_is_exactly_sequential() -> None:
    names = {
        name
        for name in globals()
        if name.startswith("test_") and callable(globals()[name])
    }
    represented: set[int] = set()
    for name in names:
        range_match = re.match(r"^test_(\d+)_to_(\d+)_", name)
        if range_match:
            start, end = map(int, range_match.groups())
            represented.update(range(start, end + 1))
        else:
            prefix = name.split("_", 2)[1]
            if prefix.isdigit():
                represented.add(int(prefix))
    assert represented == set(range(1, 49))
