from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import inspect

import pytest

import smc.dealing_range as dealing_range
from smc.dealing_range import (
    DEALING_RANGE_DETECTOR_VERSION,
    DealingRangeConfig,
    DealingRangeEventType,
    DealingRangeKind,
    DealingRangeObservation,
    DealingRangeResult,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    DealingRangeSwingSide,
    analyze_dealing_ranges,
    make_dealing_range_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


UTC = timezone.utc
T0 = datetime(2026, 7, 19, 10, 0, tzinfo=UTC)
INSTRUMENT = "GC"
TIMEFRAME = "M5"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _without_field(instance: object, field_name: str) -> object:
    malformed = object.__new__(type(instance))
    for name, value in vars(instance).items():
        if name != field_name:
            object.__setattr__(malformed, name, value)
    return malformed


def _malformed_provenance(
    provenance: SMCV2EventProvenance,
    field_name: str,
    value: object,
) -> SMCV2EventProvenance:
    malformed = object.__new__(SMCV2EventProvenance)
    for name, existing in vars(provenance).items():
        object.__setattr__(malformed, name, value if name == field_name else existing)
    return malformed


def _provenance(
    source_indices: tuple[int, ...],
    confirmation_index: int,
    *,
    confirmation_timestamp: datetime | None = None,
) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(T0 + timedelta(minutes=index) for index in source_indices),
        confirmation_index=confirmation_index,
        confirmation_timestamp=(
            T0 + timedelta(minutes=confirmation_index)
            if confirmation_timestamp is None
            else confirmation_timestamp
        ),
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


def _observations(
    end: int,
    *,
    overrides: dict[int, tuple[int, int, int]] | None = None,
    omit: frozenset[int] = frozenset(),
) -> tuple[DealingRangeObservation, ...]:
    changed = overrides or {}
    rows = []
    for index in range(end + 1):
        if index in omit:
            continue
        high_tick, low_tick, close_tick = changed.get(index, (105, 95, 100))
        rows.append(
            DealingRangeObservation(
                index=index,
                timestamp=T0 + timedelta(minutes=index),
                high_tick=high_tick,
                low_tick=low_tick,
                close_tick=close_tick,
            )
        )
    return tuple(rows)


def _event(
    direction: SMCV2Direction,
    event_type: DealingRangeEventType,
    broken_swing: DealingRangeSwing,
    *,
    displacement_start: int,
    confirmation_index: int,
    event_id: str | None = None,
    confirmation_timestamp: datetime | None = None,
) -> DealingRangeStructureEvent:
    provenance = _provenance(
        tuple(range(displacement_start, confirmation_index + 1)),
        confirmation_index,
        confirmation_timestamp=confirmation_timestamp,
    )
    canonical_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=provenance.source_indices,
        event_type=event_type,
        broken_swing_id=broken_swing.swing_id,
        confirmation_index=confirmation_index,
        boundaries=SMCV2TickRange(broken_swing.price_tick, broken_swing.price_tick),
    )
    return DealingRangeStructureEvent(
        direction=direction,
        event_type=event_type,
        broken_swing_id=broken_swing.swing_id,
        provenance=provenance,
        event_id=event_id or canonical_id,
    )


def _analyze(
    swings: tuple[DealingRangeSwing, ...] | None,
    observations: tuple[DealingRangeObservation, ...] | None,
    events: tuple[DealingRangeStructureEvent, ...] | None,
    *,
    instrument: str = INSTRUMENT,
    timeframe: str = TIMEFRAME,
    config: DealingRangeConfig = DealingRangeConfig(),
) -> DealingRangeResult:
    return analyze_dealing_ranges(
        instrument=instrument,
        timeframe=timeframe,
        swings=swings,
        observations=observations,
        structure_events=events,
        config=config,
    )


def _bullish_base(
    *,
    end: int = 10,
    extra_overrides: dict[int, tuple[int, int, int]] | None = None,
    omit: frozenset[int] = frozenset(),
) -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    overrides = {2: (100, 90, 95), 5: (110, 100, 105), 10: (112, 100, 111)}
    overrides.update(extra_overrides or {})
    observations = _observations(end, overrides=overrides, omit=omit)
    protected = _swing(DealingRangeSwingSide.LOW, 2, 90)
    broken = _swing(DealingRangeSwingSide.HIGH, 5, 110)
    event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        broken,
        displacement_start=8,
        confirmation_index=10,
    )
    return (protected, broken), observations, (event,)


def _bearish_base(
    *,
    end: int = 10,
    extra_overrides: dict[int, tuple[int, int, int]] | None = None,
) -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    overrides = {2: (110, 100, 105), 5: (100, 90, 95), 10: (100, 88, 89)}
    overrides.update(extra_overrides or {})
    observations = _observations(end, overrides=overrides)
    protected = _swing(DealingRangeSwingSide.HIGH, 2, 110)
    broken = _swing(DealingRangeSwingSide.LOW, 5, 90)
    event = _event(
        SMCV2Direction.BEARISH,
        DealingRangeEventType.BOS,
        broken,
        displacement_start=8,
        confirmation_index=10,
    )
    return (protected, broken), observations, (event,)


def _external(result: DealingRangeResult) -> tuple[DealingRangeSnapshot, ...]:
    return tuple(item for item in result.ranges if item.kind is DealingRangeKind.EXTERNAL)


def test_01_bullish_external_range_positive_construction() -> None:
    result = _analyze(*_bullish_base())

    assert result.status is SMCV2PrimitiveStatus.VALID
    latest = _external(result)[-1]
    assert latest.direction is SMCV2Direction.BULLISH
    assert (latest.low_tick, latest.high_tick) == (90, 112)
    assert latest.state is DealingRangeState.ACTIVE


def test_02_bearish_external_range_positive_construction() -> None:
    result = _analyze(*_bearish_base())

    latest = _external(result)[-1]
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert latest.direction is SMCV2Direction.BEARISH
    assert (latest.low_tick, latest.high_tick) == (88, 110)


@pytest.mark.parametrize("factory", [_bullish_base, _bearish_base])
def test_03_exact_one_tick_close_break_is_accepted(factory: object) -> None:
    result = _analyze(*factory())  # type: ignore[operator]

    assert result.status is SMCV2PrimitiveStatus.VALID


def test_04_close_exactly_at_broken_swing_is_invalid() -> None:
    swings, observations, _ = _bullish_base(
        extra_overrides={10: (112, 100, 110)},
    )
    event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        swings[1],
        displacement_start=8,
        confirmation_index=10,
    )

    result = _analyze(swings, observations, (event,))

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.ranges == ()


def test_05_wick_only_break_is_invalid() -> None:
    swings, observations, _ = _bullish_base(
        extra_overrides={10: (112, 100, 110)},
    )
    result = _analyze(swings, observations, (_event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        swings[1],
        displacement_start=8,
        confirmation_index=10,
    ),))

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert not result.ranges


def test_06_missing_swings_return_unknown_without_partial_promotion() -> None:
    _, observations, events = _bullish_base()
    result = _analyze(None, observations, events)

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.ranges == ()


def test_07_missing_observations_return_unknown_without_partial_promotion() -> None:
    swings, _, events = _bullish_base()
    result = _analyze(swings, None, events)

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.ranges == ()


def test_08_missing_events_return_unknown_without_partial_promotion() -> None:
    swings, observations, _ = _bullish_base()
    result = _analyze(swings, observations, None)

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.ranges == ()


def test_09_complete_empty_context_returns_none() -> None:
    result = _analyze((), (), ())

    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.ranges == ()


def test_10_malformed_swing_and_dangling_reference_fail_closed() -> None:
    swings, observations, events = _bullish_base()
    malformed = replace(swings[0], price_tick=True)
    missing = _without_field(swings[0], "swing_id")
    bad_provenance = replace(
        swings[0],
        provenance=_malformed_provenance(
            swings[0].provenance,
            "source_indices",
            [2],
        ),
    )
    for candidate in (malformed, missing, bad_provenance):
        assert _analyze((candidate, swings[1]), observations, events).status is (
            SMCV2PrimitiveStatus.INVALID
        )

    dangling = replace(events[0], broken_swing_id=_hash("missing"), event_id=_hash("event"))
    assert _analyze(swings, observations, (dangling,)).status is SMCV2PrimitiveStatus.INVALID

    assert _analyze((swings[1],), observations, events).status is SMCV2PrimitiveStatus.UNKNOWN


def test_11_malformed_event_timestamp_and_id_fail_closed() -> None:
    swings, observations, events = _bullish_base()
    malformed = replace(events[0], direction="BULLISH")  # type: ignore[arg-type]
    missing = _without_field(events[0], "event_id")
    bad_provenance = replace(
        events[0],
        provenance=_malformed_provenance(
            events[0].provenance,
            "source_timestamps",
            list(events[0].provenance.source_timestamps),
        ),
    )
    mismatch_time = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        swings[1],
        displacement_start=8,
        confirmation_index=10,
        confirmation_timestamp=T0 + timedelta(minutes=11),
    )
    mismatch_id = replace(events[0], event_id=_hash("wrong"))

    for candidate in (malformed, missing, bad_provenance, mismatch_time, mismatch_id):
        result = _analyze(swings, observations, (candidate,))
        assert result.status is SMCV2PrimitiveStatus.INVALID
        assert result.ranges == ()


def test_12_invalid_observation_types_chronology_timestamp_and_ohlc() -> None:
    swings, observations, events = _bullish_base()
    bad_rows = (
        replace(observations[0], high_tick=True),
        replace(observations[0], timestamp=datetime(2026, 7, 19, 10, 0)),
        replace(observations[0], high_tick=90, low_tick=95),
        _without_field(observations[0], "close_tick"),
    )
    for bad in bad_rows:
        candidate = (bad,) + observations[1:]
        assert _analyze(swings, candidate, events).status is SMCV2PrimitiveStatus.INVALID
    duplicate = observations[:2] + (observations[1],) + observations[2:]
    assert _analyze(swings, duplicate, events).status is SMCV2PrimitiveStatus.INVALID


def test_13_exact_two_bar_swing_confirmation_is_accepted_and_earlier_rejected() -> None:
    assert _analyze(*_bullish_base()).status is SMCV2PrimitiveStatus.VALID
    swings, observations, events = _bullish_base()
    early = replace(swings[0], provenance=_provenance((2,), 3))

    assert _analyze((early, swings[1]), observations, events).status is (
        SMCV2PrimitiveStatus.INVALID
    )


def test_14_broken_swing_must_confirm_strictly_before_displacement() -> None:
    swings, observations, _ = _bullish_base()
    late_broken = _swing(
        DealingRangeSwingSide.HIGH,
        5,
        110,
        confirmation_index=8,
    )
    event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        late_broken,
        displacement_start=8,
        confirmation_index=10,
    )

    assert _analyze((swings[0], late_broken), observations, (event,)).status is (
        SMCV2PrimitiveStatus.INVALID
    )


def test_15_protected_swing_must_confirm_strictly_before_displacement() -> None:
    swings, observations, events = _bullish_base()
    late = _swing(DealingRangeSwingSide.LOW, 2, 90, confirmation_index=8)

    assert _analyze((swings[1], late), observations, events).status is (
        SMCV2PrimitiveStatus.UNKNOWN
    )


@pytest.mark.parametrize("confirmation", [8, 9])
def test_16_same_index_or_later_protected_confirmation_is_excluded(
    confirmation: int,
) -> None:
    swings, observations, events = _bullish_base()
    late = _swing(DealingRangeSwingSide.LOW, 2, 90, confirmation_index=confirmation)

    assert _analyze((swings[1], late), observations, events).status is (
        SMCV2PrimitiveStatus.UNKNOWN
    )


def test_17_most_recent_protected_swing_is_selected_deterministically() -> None:
    swings, observations, events = _bullish_base(
        extra_overrides={1: (100, 85, 90), 3: (100, 92, 95)},
    )
    older = _swing(DealingRangeSwingSide.LOW, 1, 85)
    newer = _swing(DealingRangeSwingSide.LOW, 3, 92)
    ordered = (older, swings[0], newer, swings[1])

    result = _analyze(ordered, observations, events)

    assert _external(result)[-1].protected_swing_id == newer.swing_id


def test_18_missing_protected_swing_returns_unknown() -> None:
    swings, observations, events = _bullish_base()
    result = _analyze((swings[1],), observations, events)

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.ranges == ()


def test_19_public_api_rejects_duplicate_protected_identity_as_invalid() -> None:
    observations = _observations(
        10,
        overrides={2: (100, 90, 95), 5: (110, 100, 105), 10: (112, 100, 111)},
    )
    duplicate_low_a = _swing(
        DealingRangeSwingSide.LOW,
        2,
        90,
        swing_id=("0" * 64),
    )
    duplicate_low_b = _swing(
        DealingRangeSwingSide.LOW,
        2,
        90,
        swing_id=("1" * 64),
    )
    broken = _swing(DealingRangeSwingSide.HIGH, 5, 110)
    event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        broken,
        displacement_start=8,
        confirmation_index=10,
    )

    result = _analyze((duplicate_low_a, duplicate_low_b, broken), observations, (event,))

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.ranges == ()
    assert any("duplicate source-side swing identity" in reason for reason in result.reasons)


def test_20_external_extreme_uses_complete_inclusive_interval() -> None:
    bullish = _analyze(*_bullish_base(extra_overrides={7: (120, 95, 100)}))
    bearish = _analyze(*_bearish_base(extra_overrides={7: (105, 80, 100)}))

    assert _external(bullish)[-1].high_tick == 120
    assert _external(bearish)[-1].low_tick == 80


def test_21_missing_interval_is_unknown_and_malformed_present_row_is_invalid() -> None:
    swings, observations, events = _bullish_base(omit=frozenset({6}))
    assert _analyze(swings, observations, events).status is SMCV2PrimitiveStatus.UNKNOWN

    swings, observations, events = _bullish_base()
    bad = replace(observations[6], close_tick=200)
    candidate = observations[:6] + (bad,) + observations[7:]
    assert _analyze(swings, candidate, events).status is SMCV2PrimitiveStatus.INVALID


def test_22_swing_price_must_match_source_observation() -> None:
    swings, observations, events = _bullish_base()
    wrong = replace(swings[0], price_tick=91)

    assert _analyze((wrong, swings[1]), observations, events).status is (
        SMCV2PrimitiveStatus.INVALID
    )


def test_23_midpoint_is_exact_for_integer_and_both_half_tick_directions() -> None:
    integer = _analyze(*_bullish_base())
    bullish_half = _analyze(*_bullish_base(extra_overrides={10: (113, 100, 111)}))
    bearish_half = _analyze(*_bearish_base(extra_overrides={10: (100, 87, 89)}))

    assert _external(integer)[-1].midpoint_tick == Decimal("101")
    assert _external(bullish_half)[-1].midpoint_tick == Decimal("101.5")
    assert _external(bearish_half)[-1].midpoint_tick == Decimal("98.5")


def test_24_all_identity_kinds_are_repeatable_normalized_and_schema_locked() -> None:
    swings, _, events = _bullish_base()
    event = events[0]
    normalized = make_dealing_range_id(
        identity_kind="EVENT",
        instrument=" gc ",
        timeframe=" m5 ",
        direction=SMCV2Direction.BULLISH,
        source_indices=event.provenance.source_indices,
        event_type=event.event_type,
        broken_swing_id=event.broken_swing_id,
        confirmation_index=10,
        boundaries=SMCV2TickRange(110, 110),
    )
    assert normalized == event.event_id

    lineage = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_indices=(2, 5),
        swing_ids=(swings[0].swing_id, swings[1].swing_id),
        boundaries=SMCV2TickRange(90, 112),
        protected_swing_id=swings[0].swing_id,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    repeated_lineage = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_indices=(2, 5),
        swing_ids=(swings[0].swing_id, swings[1].swing_id),
        boundaries=SMCV2TickRange(90, 112),
        protected_swing_id=swings[0].swing_id,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    bearish_lineage = make_dealing_range_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BEARISH,
        source_indices=(2, 5),
        swing_ids=(swings[0].swing_id, swings[1].swing_id),
        boundaries=SMCV2TickRange(90, 112),
        protected_swing_id=swings[0].swing_id,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
    )
    assert lineage == repeated_lineage
    assert lineage != bearish_lineage
    related = event.event_id
    replacement = _hash("replacement")
    transition_specs = (
        (None, DealingRangeState.ACTIVE, "CONSTRUCTION_ACTIVE", related, None),
        (
            DealingRangeState.ACTIVE,
            DealingRangeState.INVALIDATED,
            "OBSERVATION_CLOSE_THROUGH_INVALIDATION",
            None,
            None,
        ),
        (
            DealingRangeState.ACTIVE,
            DealingRangeState.INVALIDATED,
            "CHOCH_CLOSE_THROUGH_INVALIDATION",
            related,
            None,
        ),
        (
            DealingRangeState.ACTIVE,
            DealingRangeState.SUPERSEDED,
            "BOS_PULLBACK_REPLACEMENT",
            related,
            replacement,
        ),
    )
    transition_ids = []
    for from_state, to_state, reason, related_id, replacement_id in transition_specs:
        transition_ids.append(make_dealing_range_id(
            identity_kind="TRANSITION",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            direction=SMCV2Direction.BULLISH,
            source_indices=(10,),
            lineage_id=lineage,
            transition_from_state=from_state,
            transition_to_state=to_state,
            transition_index=10,
            transition_timestamp=T0 + timedelta(minutes=10),
            transition_reason=reason,
            related_event_id=related_id,
            replacement_lineage_id=replacement_id,
        ))
    offset_time = (T0 + timedelta(minutes=10)).astimezone(
        timezone(timedelta(hours=9)),
    )
    offset_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_indices=(10,),
        lineage_id=lineage,
        transition_from_state=None,
        transition_to_state=DealingRangeState.ACTIVE,
        transition_index=10,
        transition_timestamp=offset_time,
        transition_reason="CONSTRUCTION_ACTIVE",
        related_event_id=related,
    )
    assert offset_id == transition_ids[0]
    assert dealing_range._serialize_timestamp(offset_time) == "2026-07-19T10:10:00.000000Z"

    snapshot = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_indices=(2, 5),
        swing_ids=(swings[0].swing_id, swings[1].swing_id),
        boundaries=SMCV2TickRange(90, 112),
        lineage_id=lineage,
        construction_event_id=event.event_id,
        range_kind=DealingRangeKind.EXTERNAL,
        state=DealingRangeState.ACTIVE,
        transition_ids=(transition_ids[0],),
    )
    internal = make_dealing_range_id(
        identity_kind="INTERNAL_RANGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=SMCV2Direction.BULLISH,
        source_indices=(2, 5),
        swing_ids=(swings[0].swing_id, swings[1].swing_id),
        boundaries=SMCV2TickRange(90, 112),
        range_kind=DealingRangeKind.INTERNAL,
    )
    assert all(len(value) == 64 for value in (lineage, snapshot, internal, *transition_ids))
    with pytest.raises(ValueError):
        make_dealing_range_id(
            identity_kind="EVENT",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            direction=SMCV2Direction.BULLISH,
            source_indices=event.provenance.source_indices,
            event_type=event.event_type,
            broken_swing_id=event.broken_swing_id,
            confirmation_index=10,
            boundaries=SMCV2TickRange(110, 110),
            lineage_id=lineage,
        )
    with pytest.raises(ValueError):
        make_dealing_range_id(
            identity_kind="TRANSITION",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            direction=SMCV2Direction.BULLISH,
            source_indices=(10,),
            lineage_id=lineage,
            transition_from_state=None,
            transition_to_state=DealingRangeState.ACTIVE,
            transition_index=10,
            transition_timestamp=T0,
            transition_reason="free text",
            related_event_id=related,
        )

    malformed_boundary_rows = (
        _without_field(SMCV2TickRange(110, 110), "lower_tick"),
        _without_field(SMCV2TickRange(110, 110), "upper_tick"),
    )
    for malformed_boundaries in malformed_boundary_rows:
        with pytest.raises((TypeError, ValueError)) as exc_info:
            make_dealing_range_id(
                identity_kind="EVENT",
                instrument=INSTRUMENT,
                timeframe=TIMEFRAME,
                direction=SMCV2Direction.BULLISH,
                source_indices=event.provenance.source_indices,
                event_type=event.event_type,
                broken_swing_id=event.broken_swing_id,
                confirmation_index=10,
                boundaries=malformed_boundaries,  # type: ignore[arg-type]
            )
        assert type(exc_info.value) is not AttributeError


def _bullish_extension(
    *,
    initial_high: int = 112,
    extension_high: int = 116,
) -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    overrides = {
        10: (initial_high, 100, 111),
        12: (113, 102, 108),
        17: (extension_high, 103, 114),
    }
    swings, observations, events = _bullish_base(end=17, extra_overrides=overrides)
    later_broken = _swing(DealingRangeSwingSide.HIGH, 12, 113)
    later_event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        later_broken,
        displacement_start=15,
        confirmation_index=17,
    )
    return swings + (later_broken,), observations, events + (later_event,)


def test_25_same_direction_bos_extends_target_and_preserves_lineage() -> None:
    swings, observations, events = _bullish_extension()
    result = _analyze(swings, observations, events)
    external = _external(result)

    assert len(external) == 2
    assert external[0].lineage_id == external[1].lineage_id
    assert external[0].protected_swing_id == external[1].protected_swing_id
    assert (external[0].high_tick, external[1].high_tick) == (112, 116)
    assert external[1].source_swing_ids == external[0].source_swing_ids
    assert external[1].source_indices == external[0].source_indices
    assert external[0].construction_event_id == events[0].event_id
    assert external[1].construction_event_id == events[0].event_id
    assert external[1].transitions[0].related_event_id == events[0].event_id
    assert external[1].first_known_provenance == events[1].provenance
    assert external[1].construction_event_id != events[1].event_id


def test_26_non_extending_bos_does_not_duplicate_snapshot() -> None:
    result = _analyze(*_bullish_extension(initial_high=120, extension_high=115))

    assert len(_external(result)) == 1


def test_27_later_extension_preserves_every_prior_snapshot() -> None:
    swings, observations, events = _bullish_extension()
    baseline = _analyze(swings[:2], observations[:11], events[:1])
    extended = _analyze(swings, observations, events)
    external = _external(extended)

    assert extended.ranges[: len(baseline.ranges)] == baseline.ranges
    assert external[1].source_swing_ids == external[0].source_swing_ids
    assert external[1].source_indices == external[0].source_indices
    assert external[1].construction_event_id == external[0].construction_event_id
    assert external[1].transitions == external[0].transitions


def _replacement_scenario() -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    overrides = {
        12: (106, 100, 103),
        13: (113, 102, 110),
        18: (116, 100, 115),
    }
    swings, observations, events = _bullish_base(end=18, extra_overrides=overrides)
    pullback = _swing(DealingRangeSwingSide.LOW, 12, 100)
    later_broken = _swing(DealingRangeSwingSide.HIGH, 13, 113)
    later_event = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        later_broken,
        displacement_start=16,
        confirmation_index=18,
    )
    return swings + (pullback, later_broken), observations, events + (later_event,)


def test_28_confirmed_pullback_plus_later_bos_replaces_lineage() -> None:
    result = _analyze(*_replacement_scenario())
    external = _external(result)

    assert external[-2].state is DealingRangeState.SUPERSEDED
    assert external[-1].state is DealingRangeState.ACTIVE
    assert external[-2].replacement_lineage_id == external[-1].lineage_id
    assert external[-2].lineage_id != external[-1].lineage_id


def test_29_pullback_without_later_bos_does_not_replace_range() -> None:
    swings, observations, events = _replacement_scenario()
    result = _analyze(swings[:-1], observations, events[:1])

    external = _external(result)
    assert len(external) == 1
    assert external[0].state is DealingRangeState.ACTIVE


@pytest.mark.parametrize("factory,boundary,wick", [
    (_bullish_base, 90, (100, 89, 90)),
    (_bearish_base, 110, (111, 100, 110)),
])
def test_30_boundary_close_and_wick_do_not_invalidate_but_one_tick_close_does(
    factory: object,
    boundary: int,
    wick: tuple[int, int, int],
) -> None:
    swings, _, events = factory()  # type: ignore[operator]
    exact_rows = factory(end=11, extra_overrides={11: wick})[1]  # type: ignore[operator]
    exact = _analyze(swings, exact_rows, events)
    assert _external(exact)[-1].state is DealingRangeState.ACTIVE

    if boundary == 90:
        invalidating = (100, 89, 89)
    else:
        invalidating = (111, 100, 111)
    invalid_rows = factory(  # type: ignore[operator]
        end=11,
        extra_overrides={11: invalidating},
    )[1]
    invalid = _analyze(swings, invalid_rows, events)
    assert _external(invalid)[-1].state is DealingRangeState.INVALIDATED


def _reverse_scenario(*, omit: frozenset[int] = frozenset()) -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    overrides = {12: (108, 98, 104), 18: (100, 88, 89)}
    swings, observations, events = _bullish_base(
        end=18,
        extra_overrides=overrides,
        omit=omit,
    )
    new_protected = _swing(DealingRangeSwingSide.HIGH, 12, 108)
    reverse = _event(
        SMCV2Direction.BEARISH,
        DealingRangeEventType.CHOCH,
        swings[0],
        displacement_start=16,
        confirmation_index=18,
    )
    return swings + (new_protected,), observations, events + (reverse,)


def _later_choch_after_terminal(
    *,
    initial_direction: SMCV2Direction,
    later_direction: SMCV2Direction,
) -> tuple[
    tuple[DealingRangeSwing, ...],
    tuple[DealingRangeObservation, ...],
    tuple[DealingRangeStructureEvent, ...],
]:
    if initial_direction is SMCV2Direction.BULLISH:
        invalidating = (100, 89, 89)
        factory = _bullish_base
    else:
        invalidating = (111, 100, 111)
        factory = _bearish_base

    if later_direction is SMCV2Direction.BEARISH:
        broken = _swing(DealingRangeSwingSide.LOW, 12, 94)
        protected = _swing(DealingRangeSwingSide.HIGH, 13, 108)
        later_rows = {
            12: (100, 94, 97),
            13: (108, 98, 104),
            18: (100, 92, 93),
        }
    else:
        broken = _swing(DealingRangeSwingSide.HIGH, 12, 106)
        protected = _swing(DealingRangeSwingSide.LOW, 13, 92)
        later_rows = {
            12: (106, 96, 103),
            13: (102, 92, 96),
            18: (108, 100, 107),
        }

    swings, observations, events = factory(
        end=18,
        extra_overrides={11: invalidating, **later_rows},
    )
    later = _event(
        later_direction,
        DealingRangeEventType.CHOCH,
        broken,
        displacement_start=16,
        confirmation_index=18,
    )
    return swings + (broken, protected), observations, events + (later,)


def test_31_reverse_choch_invalidates_once_before_new_range() -> None:
    result = _analyze(*_reverse_scenario())
    external = _external(result)

    old_terminal = external[-2]
    assert old_terminal.state is DealingRangeState.INVALIDATED
    assert len(old_terminal.transitions) == 2
    assert len(set(old_terminal.transition_ids)) == 2
    assert external[-1].direction is SMCV2Direction.BEARISH
    assert external[-1].state is DealingRangeState.ACTIVE


@pytest.mark.parametrize(
    "initial_direction,later_direction",
    [
        (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH),
        (SMCV2Direction.BEARISH, SMCV2Direction.BULLISH),
    ],
)
def test_31_strictly_later_opposite_choch_uses_terminal_context_without_mutation(
    initial_direction: SMCV2Direction,
    later_direction: SMCV2Direction,
) -> None:
    swings, observations, events = _later_choch_after_terminal(
        initial_direction=initial_direction,
        later_direction=later_direction,
    )
    prefix = _analyze(swings[:2], observations[:12], events[:1])
    result = _analyze(swings, observations, events)
    external = _external(result)
    old_terminal = _external(prefix)[-1]
    new_active = external[-1]

    assert prefix.status is SMCV2PrimitiveStatus.VALID
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.ranges[: len(prefix.ranges)] == prefix.ranges
    assert external[-2] == old_terminal
    assert old_terminal.state is DealingRangeState.INVALIDATED
    assert new_active.direction is later_direction
    assert new_active.state is DealingRangeState.ACTIVE
    assert new_active.lineage_id != old_terminal.lineage_id
    assert new_active.replacement_lineage_id is None
    assert new_active.first_known_provenance == events[-1].provenance
    assert new_active.transitions[0].from_state is None
    assert new_active.transitions[0].to_state is DealingRangeState.ACTIVE
    assert new_active.transitions[0].index == events[-1].provenance.confirmation_index
    assert new_active.transitions[0].timestamp == events[-1].provenance.confirmation_timestamp
    assert new_active.transitions[0].related_event_id == events[-1].event_id


@pytest.mark.parametrize(
    "direction",
    [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH],
)
def test_31_same_direction_choch_after_terminal_is_invalid_without_promotion(
    direction: SMCV2Direction,
) -> None:
    swings, observations, events = _later_choch_after_terminal(
        initial_direction=direction,
        later_direction=direction,
    )
    prefix = _analyze(swings[:2], observations[:12], events[:1])
    result = _analyze(swings, observations, events)

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.blocking_reasons == ("same-direction event must be BOS",)
    assert result.ranges == prefix.ranges


def test_31_multiple_terminal_cycles_use_only_latest_direction() -> None:
    first_broken = _swing(DealingRangeSwingSide.LOW, 12, 94)
    first_protected = _swing(DealingRangeSwingSide.HIGH, 13, 108)
    second_broken = _swing(DealingRangeSwingSide.HIGH, 20, 110)
    second_protected = _swing(DealingRangeSwingSide.LOW, 21, 90)
    swings, observations, events = _bullish_base(
        end=26,
        extra_overrides={
            11: (100, 89, 89),
            12: (100, 94, 97),
            13: (108, 98, 104),
            18: (100, 92, 93),
            19: (109, 100, 109),
            20: (110, 100, 105),
            21: (100, 90, 95),
            26: (112, 100, 111),
        },
    )
    bearish = _event(
        SMCV2Direction.BEARISH,
        DealingRangeEventType.CHOCH,
        first_broken,
        displacement_start=16,
        confirmation_index=18,
    )
    bullish = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.CHOCH,
        second_broken,
        displacement_start=24,
        confirmation_index=26,
    )
    result = _analyze(
        swings + (first_broken, first_protected, second_broken, second_protected),
        observations,
        events + (bearish, bullish),
    )
    external = _external(result)

    assert result.status is SMCV2PrimitiveStatus.VALID
    assert [item.direction for item in external if item.state is DealingRangeState.INVALIDATED] == [
        SMCV2Direction.BULLISH,
        SMCV2Direction.BEARISH,
    ]
    assert external[-1].direction is SMCV2Direction.BULLISH
    assert external[-1].state is DealingRangeState.ACTIVE


def test_32_reverse_missing_new_context_preserves_old_terminal_snapshot() -> None:
    result = _analyze(*_reverse_scenario(omit=frozenset({13})))

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert _external(result)[-1].state is DealingRangeState.INVALIDATED
    assert all(item.direction is SMCV2Direction.BULLISH for item in _external(result))


@pytest.mark.parametrize(
    "direction",
    [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH],
)
def test_32_lone_choch_without_same_input_terminal_context_remains_unknown(
    direction: SMCV2Direction,
) -> None:
    opposite = (
        SMCV2Direction.BEARISH
        if direction is SMCV2Direction.BULLISH
        else SMCV2Direction.BULLISH
    )
    swings, observations, events = _later_choch_after_terminal(
        initial_direction=opposite,
        later_direction=direction,
    )
    result = _analyze(swings[2:], observations, events[1:])

    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.ranges == ()
    assert result.blocking_reasons == ("initial CHOCH lacks prior external range context",)


@pytest.mark.parametrize("minute", [11, 10])
def test_32_non_later_choch_timestamp_is_invalid_and_preserves_terminal_prefix(
    minute: int,
) -> None:
    swings, observations, events = _later_choch_after_terminal(
        initial_direction=SMCV2Direction.BULLISH,
        later_direction=SMCV2Direction.BEARISH,
    )
    prefix = _analyze(swings[:2], observations[:12], events[:1])
    malformed_provenance = _malformed_provenance(
        events[-1].provenance,
        "confirmation_timestamp",
        T0 + timedelta(minutes=minute),
    )
    result = _analyze(
        swings,
        observations,
        events[:-1] + (replace(events[-1], provenance=malformed_provenance),),
    )

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.ranges == prefix.ranges


def test_33_same_index_ordering_duplicate_direction_and_opposition_are_atomic() -> None:
    protected_low = _swing(DealingRangeSwingSide.LOW, 1, 95)
    broken_high_a = _swing(DealingRangeSwingSide.HIGH, 2, 100)
    broken_high_b = _swing(DealingRangeSwingSide.HIGH, 3, 99)
    protected_high = _swing(DealingRangeSwingSide.HIGH, 4, 110)
    broken_low = _swing(DealingRangeSwingSide.LOW, 5, 102)
    observations = _observations(
        10,
        overrides={
            1: (100, 95, 98),
            2: (100, 95, 98),
            3: (99, 95, 98),
            4: (110, 100, 105),
            5: (105, 102, 103),
            10: (105, 95, 101),
        },
    )
    bull_a = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        broken_high_a,
        displacement_start=8,
        confirmation_index=10,
    )
    bull_b = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        broken_high_b,
        displacement_start=8,
        confirmation_index=10,
    )
    bear = _event(
        SMCV2Direction.BEARISH,
        DealingRangeEventType.BOS,
        broken_low,
        displacement_start=8,
        confirmation_index=10,
    )
    swings = (
        protected_low,
        broken_high_a,
        broken_high_b,
        protected_high,
        broken_low,
    )
    duplicate_direction = tuple(sorted(
        (bull_a, bull_b),
        key=lambda item: (
            item.provenance.confirmation_index,
            item.provenance.confirmation_timestamp,
            item.direction.value,
            item.event_type.value,
            item.event_id,
        ),
    ))
    assert _analyze(swings, observations, duplicate_direction).status is (
        SMCV2PrimitiveStatus.INVALID
    )
    opposing = tuple(sorted(
        (bull_a, bear),
        key=lambda item: (
            item.provenance.confirmation_index,
            item.provenance.confirmation_timestamp,
            item.direction.value,
            item.event_type.value,
            item.event_id,
        ),
    ))
    ambiguous = _analyze(swings, observations, opposing)
    assert ambiguous.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert ambiguous.ranges == ()
    assert _analyze(swings, observations, tuple(reversed(opposing))).status is (
        SMCV2PrimitiveStatus.INVALID
    )

    base_swings, later_observations, base_events = _bullish_base(
        end=18,
        extra_overrides={1: (80, 70, 75), 18: (95, 80, 85)},
    )
    earlier_high = _swing(DealingRangeSwingSide.HIGH, 1, 80)
    later_bull = _event(
        SMCV2Direction.BULLISH,
        DealingRangeEventType.BOS,
        earlier_high,
        displacement_start=16,
        confirmation_index=18,
    )
    later_bear = _event(
        SMCV2Direction.BEARISH,
        DealingRangeEventType.CHOCH,
        base_swings[0],
        displacement_start=16,
        confirmation_index=18,
    )
    later_group = tuple(sorted(
        (later_bull, later_bear),
        key=lambda item: (
            item.provenance.confirmation_index,
            item.provenance.confirmation_timestamp,
            item.direction.value,
            item.event_type.value,
            item.event_id,
        ),
    ))
    prior_preserved = _analyze(
        (earlier_high,) + base_swings,
        later_observations,
        base_events + later_group,
    )
    assert prior_preserved.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert len(_external(prior_preserved)) == 1
    assert _external(prior_preserved)[0].state is DealingRangeState.ACTIVE

    extension_swings, extension_observations, extension_events = _bullish_extension()
    malformed_later_event = replace(extension_events[1], event_id=_hash("wrong-later-event"))
    expected_prior = _analyze(
        extension_swings,
        extension_observations,
        extension_events[:1],
    )
    later_invalid = _analyze(
        extension_swings,
        extension_observations,
        (extension_events[0], malformed_later_event),
    )
    assert later_invalid.status is SMCV2PrimitiveStatus.INVALID
    assert _external(later_invalid) == _external(expected_prior)
    assert all(
        all(
            transition.index < malformed_later_event.provenance.confirmation_index
            for transition in item.transitions
        )
        for item in _external(later_invalid)
    )


def _case33_later_event_variant(
    event: DealingRangeStructureEvent,
    variant: str,
) -> DealingRangeStructureEvent:
    if variant == "missing_event_type":
        return _without_field(event, "event_type")  # type: ignore[return-value]
    if variant == "malformed_event_type":
        return replace(event, event_type="BOS")  # type: ignore[arg-type]
    if variant == "missing_direction":
        return _without_field(event, "direction")  # type: ignore[return-value]
    if variant == "malformed_direction":
        return replace(event, direction="BULLISH")  # type: ignore[arg-type]
    if variant == "missing_broken_swing_id":
        return _without_field(event, "broken_swing_id")  # type: ignore[return-value]
    if variant == "malformed_broken_swing_id":
        return replace(event, broken_swing_id=123)  # type: ignore[arg-type]
    if variant == "missing_event_id":
        return _without_field(event, "event_id")  # type: ignore[return-value]
    if variant == "malformed_event_id":
        return replace(event, event_id="not-a-hash")
    raise AssertionError(f"unknown case33 variant: {variant}")


@pytest.mark.parametrize("variant", [
    "missing_event_type",
    "malformed_event_type",
    "missing_direction",
    "malformed_direction",
    "missing_broken_swing_id",
    "malformed_broken_swing_id",
    "missing_event_id",
    "malformed_event_id",
])
def test_33_later_required_event_field_failures_preserve_prior_immutable_snapshots(
    variant: str,
) -> None:
    extension_swings, extension_observations, extension_events = _bullish_extension()
    failing_event = _case33_later_event_variant(extension_events[1], variant)
    expected_prior = _analyze(
        extension_swings,
        extension_observations,
        extension_events[:1],
    )
    result = _analyze(
        extension_swings,
        extension_observations,
        (extension_events[0], failing_event),
    )

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert _external(result) == _external(expected_prior)
    failing_index = extension_events[1].provenance.confirmation_index
    assert all(
        item.first_known_provenance.confirmation_index < failing_index
        for item in result.ranges
    )
    assert all(
        all(transition.index < failing_index for transition in item.transitions)
        for item in _external(result)
    )


def test_33_malformed_provenance_without_confirmation_index_is_fail_closed_invalid() -> None:
    extension_swings, extension_observations, extension_events = _bullish_extension()
    malformed_provenance = _without_field(extension_events[1].provenance, "confirmation_index")
    malformed_later = replace(extension_events[1], provenance=malformed_provenance)  # type: ignore[arg-type]
    result = _analyze(
        extension_swings,
        extension_observations,
        (extension_events[0], malformed_later),
    )

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.ranges == ()


def test_33_distinct_confirmation_indices_reverse_order_is_invalid_without_repair() -> None:
    extension_swings, extension_observations, extension_events = _bullish_extension()
    result = _analyze(
        extension_swings,
        extension_observations,
        tuple(reversed(extension_events)),
    )

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.ranges == ()


def _case33_later_provenance_variant(
    provenance: SMCV2EventProvenance,
    variant: str,
) -> SMCV2EventProvenance:
    if variant == "missing_source_indices":
        return _without_field(provenance, "source_indices")  # type: ignore[return-value]
    if variant == "malformed_source_indices":
        return _malformed_provenance(provenance, "source_indices", [16, 17])
    if variant == "missing_source_timestamps":
        return _without_field(provenance, "source_timestamps")  # type: ignore[return-value]
    if variant == "malformed_source_timestamps":
        return _malformed_provenance(
            provenance,
            "source_timestamps",
            list(provenance.source_timestamps),
        )
    if variant == "missing_confirmation_timestamp":
        return _without_field(provenance, "confirmation_timestamp")  # type: ignore[return-value]
    if variant == "malformed_confirmation_timestamp":
        return _malformed_provenance(provenance, "confirmation_timestamp", "2026-07-19T10:17:00Z")
    raise AssertionError(f"unknown case33 provenance variant: {variant}")


@pytest.mark.parametrize("variant", [
    "missing_source_indices",
    "malformed_source_indices",
    "missing_source_timestamps",
    "malformed_source_timestamps",
    "missing_confirmation_timestamp",
    "malformed_confirmation_timestamp",
])
def test_33_later_provenance_required_field_failures_preserve_prior_immutable_snapshots(
    variant: str,
) -> None:
    extension_swings, extension_observations, extension_events = _bullish_extension()
    malformed_provenance = _case33_later_provenance_variant(
        extension_events[1].provenance,
        variant,
    )
    malformed_later = replace(extension_events[1], provenance=malformed_provenance)
    expected_prior = _analyze(
        extension_swings,
        extension_observations,
        extension_events[:1],
    )
    result = _analyze(
        extension_swings,
        extension_observations,
        (extension_events[0], malformed_later),
    )

    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert _external(result) == _external(expected_prior)
    failing_index = extension_events[1].provenance.confirmation_index
    assert all(
        item.first_known_provenance.confirmation_index < failing_index
        for item in result.ranges
    )
    assert all(
        all(transition.index < failing_index for transition in item.transitions)
        for item in _external(result)
    )


def test_34_nested_internal_ranges_never_replace_external_range() -> None:
    overrides = {12: (106, 95, 100), 15: (105, 96, 101)}
    swings, observations, events = _bullish_base(end=17, extra_overrides=overrides)
    inside_low = _swing(DealingRangeSwingSide.LOW, 12, 95)
    inside_high = _swing(DealingRangeSwingSide.HIGH, 15, 105)
    result = _analyze(swings + (inside_low, inside_high), observations, events)

    internal = tuple(item for item in result.ranges if item.kind is DealingRangeKind.INTERNAL)
    assert {item.direction for item in internal} == {
        SMCV2Direction.BULLISH,
        SMCV2Direction.BEARISH,
    }
    assert all(90 < item.low_tick < item.high_tick < 112 for item in internal)
    assert len(_external(result)) == 1


def test_35_identical_runs_and_appended_future_are_prefix_invariant() -> None:
    inputs = _bullish_base()
    first = _analyze(*inputs)
    second = _analyze(*inputs)
    swings, _, events = inputs
    future = _analyze(swings, _bullish_base(end=15)[1], events)

    assert first == second
    assert future.ranges[: len(first.ranges)] == first.ranges


def test_36_public_api_signatures_freezing_and_forbidden_dependencies() -> None:
    assert dealing_range.__all__ == [
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
    assert str(inspect.signature(analyze_dealing_ranges)) == (
        "(*, instrument: 'str', timeframe: 'str', "
        "swings: 'tuple[DealingRangeSwing, ...] | None', "
        "observations: 'tuple[DealingRangeObservation, ...] | None', "
        "structure_events: 'tuple[DealingRangeStructureEvent, ...] | None', "
        "config: 'DealingRangeConfig' = DealingRangeConfig("
        "swing_confirmation_bars=2, break_buffer_ticks=1)) -> 'DealingRangeResult'"
    )
    config = DealingRangeConfig()
    with pytest.raises(FrozenInstanceError):
        config.break_buffer_ticks = 2  # type: ignore[misc]
    malformed_config = _without_field(config, "break_buffer_ticks")
    assert _analyze(*_bullish_base(), config=malformed_config).status is (
        SMCV2PrimitiveStatus.INVALID
    )
    source = inspect.getsource(dealing_range)
    forbidden = (
        "pandas",
        "market_structure",
        "bos_choch",
        "DecisionContext",
        "requests",
        "open(",
        "main.py",
        "paper",
        "broker",
        "equal_liquidity",
    )
    assert all(marker not in source for marker in forbidden)
    assert not any(name.startswith("register") for name in dealing_range.__dict__)
