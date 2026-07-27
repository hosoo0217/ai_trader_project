from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import inspect
from pathlib import Path

import pytest

import smc.premium_discount as premium_discount
from smc.dealing_range import (
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeTransition,
    make_dealing_range_id,
)
from smc.premium_discount import (
    PREMIUM_DISCOUNT_DETECTOR_VERSION,
    PremiumDiscountClassification,
    PremiumDiscountObservation,
    PremiumDiscountResult,
    PremiumDiscountSnapshot,
    PremiumDiscountZone,
    PremiumDiscountZoneSet,
    analyze_premium_discount,
    make_premium_discount_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


UTC = timezone.utc
T0 = datetime(2026, 7, 27, 10, 0, tzinfo=UTC)
INSTRUMENT = "GC"
TIMEFRAME = "M5"

_CONSTRUCTION = "CONSTRUCTION_ACTIVE"
_INVALIDATION = "CHOCH_CLOSE_THROUGH_INVALIDATION"
_REPLACEMENT = "BOS_PULLBACK_REPLACEMENT"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _exact_midpoint(low_tick: int, high_tick: int) -> Decimal:
    total = low_tick + high_tick
    if total % 2 == 0:
        return Decimal(total // 2)
    sign = "-" if total < 0 else ""
    absolute = abs(total)
    return Decimal(f"{sign}{absolute // 2}.5")


def _provenance(index: int) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=(index,),
        source_timestamps=(T0 + timedelta(minutes=index),),
        confirmation_index=index,
        confirmation_timestamp=T0 + timedelta(minutes=index),
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


def _range(
    *,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    low_tick: int = 90,
    high_tick: int = 110,
    index: int = 6,
    kind: DealingRangeKind = DealingRangeKind.EXTERNAL,
    state: DealingRangeState = DealingRangeState.ACTIVE,
    source_indices: tuple[int, ...] = (0, 3),
    source_swing_ids: tuple[str, ...] | None = None,
    lineage_id: str | None = None,
    protected_swing_id: str | None = None,
    construction_event_id: str | None = None,
    transitions: tuple[DealingRangeTransition, ...] | None = None,
    first_known_provenance: SMCV2EventProvenance | None = None,
    replacement_lineage_id: str | None = None,
) -> DealingRangeSnapshot:
    swing_ids = source_swing_ids or tuple(
        _hash(f"swing:{direction.value}:{item}:{position}")
        for position, item in enumerate(source_indices)
    )
    boundaries = SMCV2TickRange(low_tick, high_tick)
    first_known = first_known_provenance or _provenance(index)

    if kind is DealingRangeKind.INTERNAL:
        snapshot_id = make_dealing_range_id(
            identity_kind="INTERNAL_RANGE",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            direction=direction,
            source_indices=source_indices,
            swing_ids=swing_ids,
            boundaries=boundaries,
            range_kind=kind,
        )
        return DealingRangeSnapshot(
            kind=kind,
            direction=direction,
            snapshot_id=snapshot_id,
            source_swing_ids=swing_ids,
            source_indices=source_indices,
            low_tick=low_tick,
            high_tick=high_tick,
            midpoint_tick=_exact_midpoint(low_tick, high_tick),
            first_known_provenance=first_known,
        )

    protected = protected_swing_id or swing_ids[0]
    event_id = construction_event_id or _hash(
        f"event:{direction.value}:{index}:{protected}"
    )
    canonical_lineage = lineage_id or make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices[:2],
        swing_ids=swing_ids[:2],
        boundaries=boundaries,
        protected_swing_id=protected,
        construction_event_id=event_id,
        range_kind=kind,
    )
    history = transitions
    if history is None:
        history = (
            _transition(
                lineage_id=canonical_lineage,
                direction=direction,
                from_state=None,
                to_state=DealingRangeState.ACTIVE,
                index=first_known.confirmation_index,
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
        swing_ids=swing_ids,
        boundaries=boundaries,
        lineage_id=canonical_lineage,
        construction_event_id=event_id,
        range_kind=kind,
        state=state,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )
    return DealingRangeSnapshot(
        kind=kind,
        direction=direction,
        snapshot_id=snapshot_id,
        source_swing_ids=swing_ids,
        source_indices=source_indices,
        low_tick=low_tick,
        high_tick=high_tick,
        midpoint_tick=_exact_midpoint(low_tick, high_tick),
        first_known_provenance=first_known,
        lineage_id=canonical_lineage,
        protected_swing_id=protected,
        construction_event_id=event_id,
        state=state,
        transitions=history,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )


def _revision(
    active: DealingRangeSnapshot,
    *,
    low_tick: int | None = None,
    high_tick: int | None = None,
    source_indices: tuple[int, ...] | None = None,
    source_swing_ids: tuple[str, ...] | None = None,
) -> DealingRangeSnapshot:
    return _range(
        direction=active.direction,
        low_tick=active.low_tick if low_tick is None else low_tick,
        high_tick=active.high_tick if high_tick is None else high_tick,
        index=active.first_known_provenance.confirmation_index,
        source_indices=source_indices or active.source_indices,
        source_swing_ids=source_swing_ids or active.source_swing_ids,
        lineage_id=active.lineage_id,
        protected_swing_id=active.protected_swing_id,
        construction_event_id=active.construction_event_id,
        transitions=active.transitions,
        first_known_provenance=active.first_known_provenance,
    )


def _terminal(
    active: DealingRangeSnapshot,
    *,
    index: int,
    state: DealingRangeState = DealingRangeState.INVALIDATED,
    replacement_lineage_id: str | None = None,
) -> DealingRangeSnapshot:
    reason = _REPLACEMENT if state is DealingRangeState.SUPERSEDED else _INVALIDATION
    transition = _transition(
        lineage_id=active.lineage_id or "",
        direction=active.direction,
        from_state=DealingRangeState.ACTIVE,
        to_state=state,
        index=index,
        reason=reason,
        related_event_id=_hash(f"terminal:{index}:{reason}"),
        replacement_lineage_id=replacement_lineage_id,
    )
    return _range(
        direction=active.direction,
        low_tick=active.low_tick,
        high_tick=active.high_tick,
        index=active.first_known_provenance.confirmation_index,
        state=state,
        source_indices=active.source_indices,
        source_swing_ids=active.source_swing_ids,
        lineage_id=active.lineage_id,
        protected_swing_id=active.protected_swing_id,
        construction_event_id=active.construction_event_id,
        transitions=(*active.transitions, transition),
        first_known_provenance=active.first_known_provenance,
        replacement_lineage_id=replacement_lineage_id,
    )


def _observation(index: int, price_tick: int) -> PremiumDiscountObservation:
    return PremiumDiscountObservation(
        index=index,
        timestamp=T0 + timedelta(minutes=index),
        price_tick=price_tick,
    )


def _analyze(
    ranges: tuple[DealingRangeSnapshot, ...] | None,
    observations: tuple[PremiumDiscountObservation, ...] | None,
    *,
    instrument: str = INSTRUMENT,
    timeframe: str = TIMEFRAME,
) -> PremiumDiscountResult:
    return analyze_premium_discount(
        instrument=instrument,
        timeframe=timeframe,
        dealing_ranges=ranges,
        observations=observations,
    )


def _without_field(instance: object, name: str) -> object:
    malformed = object.__new__(type(instance))
    for field_name, value in vars(instance).items():
        if field_name != name:
            object.__setattr__(malformed, field_name, value)
    return malformed


def _id_context(result: PremiumDiscountResult) -> tuple[
    PremiumDiscountZoneSet,
    PremiumDiscountClassification,
]:
    assert result.zone_sets and result.classifications
    return result.zone_sets[-1], result.classifications[-1]


def test_01_bullish_below_equilibrium_is_discount() -> None:
    result = _analyze((_range(),), (_observation(7, 99),))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.classifications[-1].zone is PremiumDiscountZone.DISCOUNT


def test_02_bullish_exact_midpoint_is_equilibrium() -> None:
    result = _analyze((_range(),), (_observation(7, 100),))
    assert result.classifications[-1].zone is PremiumDiscountZone.EQUILIBRIUM


def test_03_bullish_above_equilibrium_is_premium() -> None:
    result = _analyze((_range(),), (_observation(7, 101),))
    assert result.classifications[-1].zone is PremiumDiscountZone.PREMIUM


def test_04_bearish_uses_same_location_labels_with_direction_context() -> None:
    values = _analyze(
        (_range(direction=SMCV2Direction.BEARISH),),
        (_observation(7, 99), _observation(8, 100), _observation(9, 101)),
    ).classifications
    assert tuple(item.zone for item in values) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.EQUILIBRIUM,
        PremiumDiscountZone.PREMIUM,
    )
    assert all(item.direction is SMCV2Direction.BEARISH for item in values)


def test_05_direction_never_creates_a_trade_signal_surface() -> None:
    result = _analyze((_range(),), (_observation(7, 99),))
    public_fields = {item.name for item in fields(PremiumDiscountResult)}
    forbidden = {"action", "bias", "confidence", "readiness", "side"}
    assert public_fields.isdisjoint(forbidden)
    assert result.classifications[-1].zone.value == "DISCOUNT"


def test_06_exact_low_and_high_boundaries_are_classified() -> None:
    values = _analyze(
        (_range(),),
        (_observation(7, 90), _observation(8, 110)),
    ).classifications
    assert tuple(item.zone for item in values) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.PREMIUM,
    )


def test_07_outside_ticks_are_omitted() -> None:
    result = _analyze(
        (_range(),),
        (_observation(7, 89), _observation(8, 111), _observation(9, 100)),
    )
    assert tuple(item.observation_index for item in result.classifications) == (9,)


def test_08_all_outside_observations_return_none() -> None:
    result = _analyze((_range(),), (_observation(7, 89), _observation(8, 111)))
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.classifications == result.snapshots == ()


def test_09_even_span_has_integer_equilibrium() -> None:
    result = _analyze((_range(low_tick=90, high_tick=110),), (_observation(7, 100),))
    assert result.zone_sets[-1].equilibrium_tick == Decimal("100")


def test_10_odd_span_has_half_tick_equilibrium() -> None:
    result = _analyze(
        (_range(low_tick=90, high_tick=109),),
        (_observation(7, 99), _observation(8, 100)),
    )
    assert result.zone_sets[-1].equilibrium_tick == Decimal("99.5")
    assert tuple(item.zone for item in result.classifications) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.PREMIUM,
    )


def test_11_negative_zero_and_positive_ticks_use_decimal_exactly() -> None:
    negative = _analyze(
        (_range(low_tick=-10, high_tick=10),),
        (_observation(7, -1), _observation(8, 0), _observation(9, 1)),
    )
    assert negative.zone_sets[-1].equilibrium_tick == Decimal("0")
    assert tuple(item.zone for item in negative.classifications) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.EQUILIBRIUM,
        PremiumDiscountZone.PREMIUM,
    )
    huge = 10**100
    positive_even = _analyze(
        (_range(low_tick=huge, high_tick=huge + 2),),
        (_observation(7, huge + 1),),
    )
    negative_even = _analyze(
        (_range(low_tick=-huge - 2, high_tick=-huge),),
        (_observation(7, -huge - 1),),
    )
    positive_odd = _analyze(
        (_range(low_tick=huge, high_tick=huge + 1),),
        (_observation(7, huge), _observation(8, huge + 1)),
    )
    negative_odd = _analyze(
        (_range(low_tick=-huge - 1, high_tick=-huge),),
        (_observation(7, -huge - 1), _observation(8, -huge)),
    )
    assert positive_even.zone_sets[-1].equilibrium_tick == Decimal(huge + 1)
    assert negative_even.zone_sets[-1].equilibrium_tick == Decimal(-huge - 1)
    assert positive_odd.zone_sets[-1].equilibrium_tick == Decimal(f"{huge}.5")
    assert negative_odd.zone_sets[-1].equilibrium_tick == Decimal(f"-{huge}.5")
    assert tuple(item.zone for item in positive_odd.classifications) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.PREMIUM,
    )
    assert tuple(item.zone for item in negative_odd.classifications) == (
        PremiumDiscountZone.DISCOUNT,
        PremiumDiscountZone.PREMIUM,
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"high_tick": 90, "midpoint_tick": Decimal(90)},
        {"low_tick": 111, "high_tick": 110, "midpoint_tick": Decimal("110.5")},
        {"midpoint_tick": Decimal("100.1")},
    ),
)
def test_12_invalid_boundaries_or_midpoint_fail_closed(changes: dict[str, object]) -> None:
    malformed = replace(_range(), **changes)
    assert _analyze((malformed,), (_observation(7, 100),)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("missing", ("ranges", "observations", "both"))
def test_13_missing_top_level_context_is_unknown(missing: str) -> None:
    ranges = None if missing in ("ranges", "both") else (_range(),)
    observations = None if missing in ("observations", "both") else (_observation(7, 100),)
    assert _analyze(ranges, observations).status is SMCV2PrimitiveStatus.UNKNOWN


def test_14_complete_empty_context_is_none() -> None:
    assert _analyze((), ()).status is SMCV2PrimitiveStatus.NONE


def test_15_internal_and_terminal_only_context_is_none() -> None:
    internal = _range(kind=DealingRangeKind.INTERNAL, source_indices=(0, 3))
    active = _range(index=8)
    terminal = _terminal(active, index=9)
    internal_only = _analyze((internal,), (_observation(10, 100),))
    terminal_only = _analyze((terminal,), (_observation(10, 100),))
    assert internal_only.status is SMCV2PrimitiveStatus.NONE
    assert terminal_only.status is SMCV2PrimitiveStatus.NONE


def test_16_initial_active_range_is_usable_at_construction_moment() -> None:
    active = _range(index=6)
    result = _analyze((active,), (_observation(6, 100),))
    assert result.status is SMCV2PrimitiveStatus.VALID


def test_17_same_moment_terminal_without_replacement_has_no_zone() -> None:
    active = _range(index=6)
    terminal = _terminal(active, index=8)
    result = _analyze((active, terminal), (_observation(8, 100),))
    assert result.status is SMCV2PrimitiveStatus.NONE


@pytest.mark.parametrize(
    ("old_direction", "new_direction"),
    (
        (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH),
        (SMCV2Direction.BEARISH, SMCV2Direction.BULLISH),
    ),
)
def test_18_same_moment_reversal_uses_only_new_range(
    old_direction: SMCV2Direction,
    new_direction: SMCV2Direction,
) -> None:
    old = _range(direction=old_direction, index=6)
    new = _range(direction=new_direction, low_tick=120, high_tick=140, index=8)
    terminal = _terminal(
        old,
        index=8,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=new.lineage_id,
    )
    result = _analyze((old, terminal, new), (_observation(8, 130),))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.classifications[-1].active_range_lineage_id == new.lineage_id
    wrong_replacement = _hash(
        f"wrong:{old_direction.value}:{new_direction.value}"
    )
    mismatched_transition = _transition(
        lineage_id=old.lineage_id or "",
        direction=old.direction,
        from_state=DealingRangeState.ACTIVE,
        to_state=DealingRangeState.SUPERSEDED,
        index=8,
        reason=_REPLACEMENT,
        related_event_id=_hash(f"mismatch-event:{old_direction.value}"),
        replacement_lineage_id=wrong_replacement,
    )
    mismatched_terminal = _range(
        direction=old.direction,
        low_tick=old.low_tick,
        high_tick=old.high_tick,
        index=old.first_known_provenance.confirmation_index,
        state=DealingRangeState.SUPERSEDED,
        source_indices=old.source_indices,
        source_swing_ids=old.source_swing_ids,
        lineage_id=old.lineage_id,
        protected_swing_id=old.protected_swing_id,
        construction_event_id=old.construction_event_id,
        transitions=(*old.transitions, mismatched_transition),
        first_known_provenance=old.first_known_provenance,
        replacement_lineage_id=new.lineage_id,
    )
    failed = _analyze(
        (old, mismatched_terminal, new),
        (_observation(7, 100), _observation(8, 130)),
    )
    assert failed.status is SMCV2PrimitiveStatus.INVALID
    assert tuple(item.observation_index for item in failed.classifications) == (7,)
    assert tuple(item.index for item in failed.snapshots) == (7,)
    assert tuple(item.active_range_lineage_id for item in failed.zone_sets) == (
        old.lineage_id,
    )


def test_19_unchanged_revision_reuses_zone_set_creation_context() -> None:
    active = _range()
    result = _analyze(
        (active,),
        (_observation(7, 99), _observation(8, 101)),
    )
    assert len(result.zone_sets) == 1
    zone_set = result.zone_sets[0]
    assert zone_set.version == 1
    assert zone_set.creation_range_snapshot_id == active.snapshot_id
    assert all(
        item.zone_set_id == zone_set.zone_set_id
        for item in result.classifications
    )


def test_20_boundary_extension_creates_next_version() -> None:
    active = _range()
    revised = _revision(active, high_tick=120)
    result = _analyze((active, revised), (_observation(7, 105),))
    assert tuple(item.version for item in result.zone_sets) == (1, 2)
    assert result.zone_sets[-1].prior_zone_set_id == result.zone_sets[0].zone_set_id
    assert result.zone_sets[-1].equilibrium_tick == Decimal("105")


def test_21_source_change_versions_but_snapshot_only_change_does_not() -> None:
    active = _range()
    source_changed = _revision(
        active,
        source_indices=(*active.source_indices, 5),
        source_swing_ids=(*active.source_swing_ids, _hash("later-source")),
    )
    result = _analyze((active, source_changed), (_observation(7, 100),))
    assert tuple(item.version for item in result.zone_sets) == (1, 2)
    assert "current_range_snapshot_id" not in {
        item.name for item in fields(PremiumDiscountZoneSet)
    }


def test_22_new_lineage_starts_version_one_and_preserves_old() -> None:
    old = _range(index=6)
    new = _range(low_tick=120, high_tick=140, index=8)
    terminal = _terminal(
        old,
        index=8,
        state=DealingRangeState.SUPERSEDED,
        replacement_lineage_id=new.lineage_id,
    )
    result = _analyze(
        (old, terminal, new),
        (_observation(7, 100), _observation(8, 130)),
    )
    assert tuple(item.version for item in result.zone_sets) == (1, 1)
    assert result.classifications[0].active_range_lineage_id == old.lineage_id
    assert result.classifications[1].active_range_lineage_id == new.lineage_id


def test_23_unrelated_same_moment_ranges_are_ambiguous_without_group_output() -> None:
    first = _range(direction=SMCV2Direction.BULLISH, index=6)
    second = _range(direction=SMCV2Direction.BEARISH, low_tick=80, high_tick=120, index=6)
    result = _analyze((first, second), (_observation(6, 100),))
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert result.zone_sets == result.classifications == result.snapshots == ()


def test_24_malformed_later_group_preserves_prior_evidence() -> None:
    active = _range(index=6)
    malformed = replace(_terminal(active, index=9), transition_ids=())
    result = _analyze(
        (active, malformed),
        (_observation(7, 100), _observation(9, 100)),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert tuple(item.observation_index for item in result.classifications) == (7,)


@pytest.mark.parametrize("variant", ("missing", "wrong_type", "duplicate_index", "duplicate_time"))
def test_25_malformed_or_duplicate_observations_fail_closed(variant: str) -> None:
    first = _observation(7, 100)
    if variant == "missing":
        observations = (_without_field(first, "price_tick"),)
    elif variant == "wrong_type":
        observations = (replace(first, price_tick=True),)
    elif variant == "duplicate_index":
        observations = (first, PremiumDiscountObservation(7, T0 + timedelta(minutes=8), 101))
    else:
        observations = (first, PremiumDiscountObservation(8, first.timestamp, 101))
    result = _analyze((_range(),), observations)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("field_name", ("kind", "snapshot_id", "midpoint_tick", "first_known_provenance"))
def test_26_malformed_range_fields_fail_closed(field_name: str) -> None:
    malformed = _without_field(_range(), field_name)
    result = _analyze((malformed,), (_observation(7, 100),))  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "mutation",
    ("hash", "length", "protected", "transition_ids", "transition_chain", "snapshot_id"),
)
def test_27_snapshot_local_identity_and_transition_errors_are_invalid(mutation: str) -> None:
    active = _range()
    if mutation == "hash":
        malformed = replace(active, construction_event_id="bad")
    elif mutation == "length":
        malformed = replace(active, source_indices=(0,))
    elif mutation == "protected":
        malformed = replace(active, protected_swing_id=_hash("absent"))
    elif mutation == "transition_ids":
        malformed = replace(active, transition_ids=())
    elif mutation == "transition_chain":
        bad_transition = replace(active.transitions[0], from_state=DealingRangeState.ACTIVE)
        malformed = replace(active, transitions=(bad_transition,))
    else:
        malformed = replace(active, snapshot_id=_hash("wrong-snapshot"))
    assert _analyze((malformed,), (_observation(7, 100),)).status is SMCV2PrimitiveStatus.INVALID
    if mutation == "transition_chain":
        new = _range(
            direction=SMCV2Direction.BEARISH,
            low_tick=120,
            high_tick=140,
            index=8,
        )
        wrong_transition = _transition(
            lineage_id=active.lineage_id or "",
            direction=active.direction,
            from_state=DealingRangeState.ACTIVE,
            to_state=DealingRangeState.SUPERSEDED,
            index=8,
            reason=_REPLACEMENT,
            related_event_id=_hash("case-27-mismatch"),
            replacement_lineage_id=_hash("wrong-case-27-lineage"),
        )
        mismatched_terminal = _range(
            direction=active.direction,
            low_tick=active.low_tick,
            high_tick=active.high_tick,
            index=active.first_known_provenance.confirmation_index,
            state=DealingRangeState.SUPERSEDED,
            source_indices=active.source_indices,
            source_swing_ids=active.source_swing_ids,
            lineage_id=active.lineage_id,
            protected_swing_id=active.protected_swing_id,
            construction_event_id=active.construction_event_id,
            transitions=(*active.transitions, wrong_transition),
            first_known_provenance=active.first_known_provenance,
            replacement_lineage_id=new.lineage_id,
        )
        assert _analyze(
            (active, mismatched_terminal, new),
            (_observation(8, 130),),
        ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("variant", ("duplicate_snapshot", "contradictory_revision", "impossible_terminal"))
def test_28_duplicate_or_contradictory_range_evidence_is_invalid(variant: str) -> None:
    active = _range()
    if variant == "duplicate_snapshot":
        ranges = (active, active)
    elif variant == "contradictory_revision":
        revised = _revision(active, source_indices=(0, 4))
        ranges = (active, revised)
    else:
        first_terminal = _terminal(active, index=8)
        second_terminal = _terminal(active, index=9)
        ranges = (active, first_terminal, second_terminal)
    assert _analyze(ranges, (_observation(9, 100),)).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("variant", ("observation_index", "observation_time", "range_order", "same_append"))
def test_29_invalid_chronology_is_not_silently_sorted(variant: str) -> None:
    active = _range()
    if variant == "observation_index":
        observations = (
            PremiumDiscountObservation(8, T0 + timedelta(minutes=7), 100),
            PremiumDiscountObservation(7, T0 + timedelta(minutes=8), 100),
        )
        ranges = (active,)
    elif variant == "observation_time":
        observations = (
            PremiumDiscountObservation(7, T0 + timedelta(minutes=8), 100),
            PremiumDiscountObservation(8, T0 + timedelta(minutes=7), 100),
        )
        ranges = (active,)
    elif variant == "range_order":
        terminal = _terminal(active, index=8)
        ranges = (terminal, active)
        observations = (_observation(9, 100),)
    else:
        observations = (_observation(7, 100), _observation(7, 101))
        ranges = (active,)
    assert _analyze(ranges, observations).status is SMCV2PrimitiveStatus.INVALID


def test_30_zone_set_identity_is_deterministic_and_schema_strict() -> None:
    result = _analyze((_range(),), (_observation(7, 100),))
    zone_set = result.zone_sets[-1]
    kwargs = dict(
        identity_kind="ZONE_SET",
        instrument=" gc ",
        timeframe=" m5 ",
        active_range_lineage_id=zone_set.active_range_lineage_id,
        direction=zone_set.direction,
        source_indices=zone_set.source_indices,
        source_swing_ids=zone_set.source_swing_ids,
        protected_swing_id=zone_set.protected_swing_id,
        construction_event_id=zone_set.construction_event_id,
        boundaries=SMCV2TickRange(zone_set.low_tick, zone_set.high_tick),
        equilibrium_tick=zone_set.equilibrium_tick,
        creation_range_snapshot_id=zone_set.creation_range_snapshot_id,
        first_known_index=zone_set.first_known_index,
        first_known_timestamp=zone_set.first_known_timestamp.astimezone(
            timezone(timedelta(hours=9))
        ),
        version=zone_set.version,
        prior_zone_set_id=zone_set.prior_zone_set_id,
    )
    assert make_premium_discount_id(**kwargs) == zone_set.zone_set_id
    with pytest.raises(ValueError):
        make_premium_discount_id(**kwargs, current_range_snapshot_id=_hash("forbidden"))
    huge = 10**100
    huge_kwargs = {
        **kwargs,
        "boundaries": SMCV2TickRange(huge, huge + 1),
        "equilibrium_tick": Decimal(f"{huge}.5"),
    }
    with localcontext() as context:
        context.prec = 6
        low_precision_id = make_premium_discount_id(**huge_kwargs)
    with localcontext() as context:
        context.prec = 150
        high_precision_id = make_premium_discount_id(**huge_kwargs)
    assert low_precision_id == high_precision_id
    zero_result = _analyze(
        (_range(low_tick=-1, high_tick=1),),
        (_observation(7, 0),),
    )
    zero_zone_set = zero_result.zone_sets[-1]
    zero_kwargs = {
        **{
            key: value
            for key, value in kwargs.items()
            if key != "equilibrium_tick"
        },
        "active_range_lineage_id": zero_zone_set.active_range_lineage_id,
        "direction": zero_zone_set.direction,
        "source_indices": zero_zone_set.source_indices,
        "source_swing_ids": zero_zone_set.source_swing_ids,
        "protected_swing_id": zero_zone_set.protected_swing_id,
        "construction_event_id": zero_zone_set.construction_event_id,
        "boundaries": SMCV2TickRange(-1, 1),
        "creation_range_snapshot_id": zero_zone_set.creation_range_snapshot_id,
        "first_known_index": zero_zone_set.first_known_index,
        "first_known_timestamp": zero_zone_set.first_known_timestamp,
        "version": zero_zone_set.version,
        "prior_zone_set_id": zero_zone_set.prior_zone_set_id,
    }
    zero_ids = {
        make_premium_discount_id(
            **zero_kwargs,
            equilibrium_tick=representation,
        )
        for representation in (
            Decimal("0"),
            Decimal("-0"),
            Decimal("0.0"),
            Decimal("-0.0"),
        )
    }
    assert zero_ids == {zero_zone_set.zone_set_id}


def test_31_classification_identity_reconciles_price_zone_and_zone_set() -> None:
    result = _analyze((_range(),), (_observation(7, 100),))
    zone_set, classification = _id_context(result)
    kwargs = dict(
        identity_kind="CLASSIFICATION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        active_range_lineage_id=classification.active_range_lineage_id,
        direction=classification.direction,
        boundaries=SMCV2TickRange(zone_set.low_tick, zone_set.high_tick),
        equilibrium_tick=zone_set.equilibrium_tick,
        current_range_snapshot_id=classification.active_range_snapshot_id,
        version=classification.zone_set_version,
        zone_set_id=classification.zone_set_id,
        observation_index=classification.observation_index,
        observation_timestamp=classification.observation_timestamp,
        price_tick=classification.price_tick,
        zone=classification.zone,
    )
    assert make_premium_discount_id(**kwargs) == classification.classification_id
    with pytest.raises(ValueError):
        make_premium_discount_id(**{**kwargs, "zone": PremiumDiscountZone.PREMIUM})
    with pytest.raises(ValueError):
        make_premium_discount_id(**{**kwargs, "price_tick": 200})


def test_32_snapshot_identity_recomputes_classification_identity() -> None:
    result = _analyze((_range(),), (_observation(7, 100),))
    zone_set, classification = _id_context(result)
    snapshot = result.snapshots[-1]
    kwargs = dict(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        active_range_lineage_id=snapshot.active_range_lineage_id,
        direction=classification.direction,
        boundaries=SMCV2TickRange(zone_set.low_tick, zone_set.high_tick),
        equilibrium_tick=zone_set.equilibrium_tick,
        current_range_snapshot_id=snapshot.active_range_snapshot_id,
        version=snapshot.zone_set_version,
        zone_set_id=snapshot.zone_set_id,
        observation_index=snapshot.index,
        observation_timestamp=snapshot.timestamp,
        price_tick=classification.price_tick,
        zone=classification.zone,
        classification_id=snapshot.classification_id,
    )
    assert make_premium_discount_id(**kwargs) == snapshot.snapshot_id
    with pytest.raises(ValueError):
        make_premium_discount_id(**{**kwargs, "classification_id": _hash("wrong")})


def test_33_identity_builder_signature_normalization_and_rejection() -> None:
    signature = inspect.signature(make_premium_discount_id)
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in signature.parameters.values()
    )
    assert PREMIUM_DISCOUNT_DETECTOR_VERSION == "SMC-V2-PREMIUM-DISCOUNT-1"
    with pytest.raises(ValueError):
        make_premium_discount_id(
            identity_kind="UNKNOWN",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            active_range_lineage_id=_hash("lineage"),
            direction=SMCV2Direction.BULLISH,
        )
    with pytest.raises((TypeError, ValueError)):
        make_premium_discount_id(
            identity_kind="ZONE_SET",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            active_range_lineage_id="bad",
            direction=SMCV2Direction.BULLISH,
        )
    huge = 10**100
    huge_kwargs = dict(
        identity_kind="ZONE_SET",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        active_range_lineage_id=_hash("huge-lineage"),
        direction=SMCV2Direction.BULLISH,
        source_indices=(0, 1),
        source_swing_ids=(_hash("huge-a"), _hash("huge-b")),
        protected_swing_id=_hash("huge-a"),
        construction_event_id=_hash("huge-event"),
        boundaries=SMCV2TickRange(huge, huge + 2),
        equilibrium_tick=Decimal(huge + 1),
        creation_range_snapshot_id=_hash("huge-snapshot"),
        first_known_index=1,
        first_known_timestamp=T0,
        version=1,
    )
    with localcontext() as context:
        context.prec = 6
        assert len(make_premium_discount_id(**huge_kwargs)) == 64
        with pytest.raises(ValueError):
            make_premium_discount_id(
                **{**huge_kwargs, "equilibrium_tick": Decimal(huge)}
            )
    signed_zero_kwargs = {
        **huge_kwargs,
        "boundaries": SMCV2TickRange(-1, 1),
        "equilibrium_tick": Decimal("0"),
    }
    positive_zero_id = make_premium_discount_id(**signed_zero_kwargs)
    negative_zero_id = make_premium_discount_id(
        **{**signed_zero_kwargs, "equilibrium_tick": Decimal("-0.0")}
    )
    assert positive_zero_id == negative_zero_id


def test_34_public_dataclasses_fields_frozen_signatures_and_exports() -> None:
    public_dataclasses = (
        PremiumDiscountObservation,
        PremiumDiscountZoneSet,
        PremiumDiscountClassification,
        PremiumDiscountSnapshot,
        PremiumDiscountResult,
    )
    assert all(item.__dataclass_params__.frozen for item in public_dataclasses)
    assert tuple(item.name for item in fields(PremiumDiscountObservation)) == (
        "index",
        "timestamp",
        "price_tick",
    )
    assert tuple(item.name for item in fields(PremiumDiscountZoneSet)) == (
        "zone_set_id",
        "active_range_lineage_id",
        "creation_range_snapshot_id",
        "direction",
        "source_swing_ids",
        "source_indices",
        "protected_swing_id",
        "construction_event_id",
        "low_tick",
        "high_tick",
        "equilibrium_tick",
        "version",
        "first_known_index",
        "first_known_timestamp",
        "prior_zone_set_id",
    )
    assert tuple(item.name for item in fields(PremiumDiscountClassification)) == (
        "classification_id",
        "zone_set_id",
        "active_range_lineage_id",
        "active_range_snapshot_id",
        "direction",
        "zone_set_version",
        "observation_index",
        "observation_timestamp",
        "price_tick",
        "zone",
    )
    assert tuple(item.name for item in fields(PremiumDiscountSnapshot)) == (
        "snapshot_id",
        "active_range_lineage_id",
        "active_range_snapshot_id",
        "zone_set_id",
        "zone_set_version",
        "index",
        "timestamp",
        "classification",
        "classification_id",
    )
    assert tuple(item.name for item in fields(PremiumDiscountResult)) == (
        "status",
        "zone_sets",
        "classifications",
        "snapshots",
        "reasons",
        "blocking_reasons",
    )
    observation = _observation(7, 100)
    with pytest.raises(FrozenInstanceError):
        observation.price_tick = 101  # type: ignore[misc]
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in inspect.signature(analyze_premium_discount).parameters.values()
    )
    assert tuple(inspect.signature(analyze_premium_discount).parameters) == (
        "instrument",
        "timeframe",
        "dealing_ranges",
        "observations",
    )
    assert tuple(inspect.signature(make_premium_discount_id).parameters) == (
        "identity_kind",
        "instrument",
        "timeframe",
        "active_range_lineage_id",
        "direction",
        "source_indices",
        "source_swing_ids",
        "protected_swing_id",
        "construction_event_id",
        "boundaries",
        "equilibrium_tick",
        "creation_range_snapshot_id",
        "first_known_index",
        "first_known_timestamp",
        "current_range_snapshot_id",
        "version",
        "prior_zone_set_id",
        "zone_set_id",
        "observation_index",
        "observation_timestamp",
        "price_tick",
        "zone",
        "classification_id",
    )
    assert tuple(premium_discount.__all__) == (
        "PREMIUM_DISCOUNT_DETECTOR_VERSION",
        "PremiumDiscountZone",
        "PremiumDiscountObservation",
        "PremiumDiscountZoneSet",
        "PremiumDiscountClassification",
        "PremiumDiscountSnapshot",
        "PremiumDiscountResult",
        "make_premium_discount_id",
        "analyze_premium_discount",
    )
    assert tuple(item.value for item in PremiumDiscountZone) == (
        "DISCOUNT",
        "EQUILIBRIUM",
        "PREMIUM",
    )


def test_35_repeatability_prefix_invariance_and_later_invalid_preservation() -> None:
    active = _range()
    prefix = _analyze((active,), (_observation(7, 99),))
    repeat = _analyze((active,), (_observation(7, 99),))
    longer = _analyze(
        (active,),
        (_observation(7, 99), _observation(8, 100)),
    )
    assert prefix == repeat
    assert longer.zone_sets[: len(prefix.zone_sets)] == prefix.zone_sets
    assert longer.classifications[: len(prefix.classifications)] == prefix.classifications
    malformed_later = replace(_terminal(active, index=9), transition_ids=())
    failed = _analyze(
        (active, malformed_later),
        (_observation(7, 99), _observation(9, 100)),
    )
    assert failed.status is SMCV2PrimitiveStatus.INVALID
    assert failed.zone_sets == prefix.zone_sets
    assert failed.classifications == prefix.classifications


def test_36_module_is_standalone_and_has_no_forbidden_dependency() -> None:
    module_path = Path(__file__).parents[1] / "smc" / "premium_discount.py"
    source = module_path.read_text(encoding="utf-8")
    forbidden = (
        "pandas",
        "liquidity_map",
        "liquidity_sweep",
        "market_structure",
        "bos_choch",
        "requests",
        "broker",
        "risk",
        "orderflow",
    )
    assert all(token not in source.lower() for token in forbidden)
    assert "__all__" in source
