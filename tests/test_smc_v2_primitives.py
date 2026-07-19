from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re

import pytest

import smc.smc_v2_primitives as primitives
from smc.smc_v2_primitives import (
    FLOAT_ALIGNMENT_TOLERANCE_TICKS,
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2LifecycleEvent,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    make_deterministic_id,
    normalize_utc_timestamp,
    price_to_ticks,
    ticks_to_price,
    validate_lifecycle_history,
    validate_tick_size,
)


UTC = timezone.utc
T0 = datetime(2026, 7, 19, 10, 0, tzinfo=UTC)


def _event(
    from_state: SMCV2LifecycleState | None,
    to_state: SMCV2LifecycleState,
    index: int,
    *,
    minutes: int | None = None,
    reason: str = "synthetic transition",
) -> SMCV2LifecycleEvent:
    return SMCV2LifecycleEvent(
        from_state=from_state,
        to_state=to_state,
        index=index,
        timestamp=T0 + timedelta(minutes=index if minutes is None else minutes),
        reason=reason,
    )


def _allowed_transitions() -> dict[
    SMCV2LifecycleState | None,
    frozenset[SMCV2LifecycleState],
]:
    state = SMCV2LifecycleState
    return {
        None: frozenset({state.DETECTED}),
        state.DETECTED: frozenset({state.ACTIVE}),
        state.ACTIVE: frozenset({state.TOUCHED, state.INVALIDATED}),
        state.TOUCHED: frozenset({state.MITIGATED, state.INVALIDATED}),
        state.MITIGATED: frozenset(),
        state.INVALIDATED: frozenset(),
    }


def _terminal_states() -> frozenset[SMCV2LifecycleState]:
    return frozenset(
        {
            SMCV2LifecycleState.MITIGATED,
            SMCV2LifecycleState.INVALIDATED,
        }
    )


def _identity(**overrides: object) -> str:
    values: dict[str, object] = {
        "detector_version": "SMC-V2.0",
        "instrument": "gc",
        "timeframe": "m5",
        "source_indices": (10, 11, 12),
        "direction": SMCV2Direction.BULLISH,
        "boundaries": SMCV2TickRange(41875, 41900),
    }
    values.update(overrides)
    return make_deterministic_id(**values)  # type: ignore[arg-type]


def test_public_api_is_exact_and_directly_importable() -> None:
    assert primitives.__all__ == [
        "FLOAT_ALIGNMENT_TOLERANCE_TICKS",
        "SMCV2PrimitiveStatus",
        "SMCV2Direction",
        "SMCV2LifecycleState",
        "SMCV2EventProvenance",
        "SMCV2TickRange",
        "SMCV2LifecycleEvent",
        "normalize_utc_timestamp",
        "validate_tick_size",
        "price_to_ticks",
        "ticks_to_price",
        "validate_lifecycle_history",
        "make_deterministic_id",
    ]


def test_enum_values_are_locked() -> None:
    assert {item.value for item in SMCV2PrimitiveStatus} == {
        "VALID",
        "INVALID",
        "UNKNOWN",
        "NONE",
        "AMBIGUOUS",
    }
    assert {item.value for item in SMCV2Direction} == {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
        "UNKNOWN",
    }
    assert {item.value for item in SMCV2LifecycleState} == {
        "DETECTED",
        "ACTIVE",
        "TOUCHED",
        "PARTIALLY_TOUCHED",
        "PARTIALLY_FILLED",
        "MIDPOINT_FILLED",
        "FULLY_FILLED",
        "PARTIALLY_MITIGATED",
        "MITIGATED",
        "FULLY_TRAVERSED",
        "INVALIDATED",
        "EXPIRED",
        "SWEPT",
        "BROKEN",
    }


def test_float_alignment_tolerance_is_locked() -> None:
    assert FLOAT_ALIGNMENT_TOLERANCE_TICKS == Decimal("1e-9")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, Decimal("1")),
        (0.25, Decimal("0.25")),
        ("0.10", Decimal("0.1")),
        (Decimal("0.0100"), Decimal("0.01")),
    ],
)
def test_validate_tick_size_accepts_supported_positive_values(
    value: Decimal | int | float | str,
    expected: Decimal,
) -> None:
    assert validate_tick_size(value) == expected


@pytest.mark.parametrize(
    "value",
    [0, -1, "0", "-0.1", float("nan"), float("inf"), Decimal("NaN")],
)
def test_validate_tick_size_rejects_non_positive_or_non_finite_values(
    value: Decimal | int | float | str,
) -> None:
    with pytest.raises(ValueError):
        validate_tick_size(value)


@pytest.mark.parametrize("value", [True, False, "", "not-a-number", [], None])
def test_validate_tick_size_rejects_invalid_types_or_text(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        validate_tick_size(value)  # type: ignore[arg-type]


def test_price_to_ticks_handles_exact_and_negative_prices() -> None:
    assert price_to_ticks("4187.5", "0.1") == 41875
    assert price_to_ticks(0, "0.25") == 0
    assert price_to_ticks("-1.25", "0.25") == -5


def test_price_to_ticks_absorbs_only_small_float_representation_noise() -> None:
    assert price_to_ticks(0.1 + 0.2, 0.1) == 3
    assert price_to_ticks(Decimal("0.30000000005"), Decimal("0.1")) == 3


def test_price_to_ticks_rejects_noise_above_locked_tolerance() -> None:
    with pytest.raises(ValueError, match="aligned"):
        price_to_ticks(Decimal("0.3000000002"), Decimal("0.1"))


def test_price_to_ticks_rejects_real_fractional_tick_instead_of_rounding() -> None:
    with pytest.raises(ValueError, match="aligned"):
        price_to_ticks(Decimal("0.35"), Decimal("0.1"))


@pytest.mark.parametrize("price", [True, "bad", float("nan"), float("inf")])
def test_price_to_ticks_rejects_invalid_prices(price: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        price_to_ticks(price, "0.1")  # type: ignore[arg-type]


def test_ticks_to_price_is_exact_and_round_trips() -> None:
    price = ticks_to_price(41875, "0.1")

    assert price == Decimal("4187.5")
    assert price_to_ticks(price, "0.1") == 41875


@pytest.mark.parametrize("ticks", [True, 1.0, Decimal("1"), "1"])
def test_ticks_to_price_requires_a_real_integer(ticks: object) -> None:
    with pytest.raises(TypeError):
        ticks_to_price(ticks, "0.1")  # type: ignore[arg-type]


def test_consistent_price_and_tick_scaling_preserves_tick_relationships() -> None:
    assert price_to_ticks("10.5", "0.5") == 21
    assert price_to_ticks("105", "5") == 21


def test_normalize_utc_timestamp_converts_aware_time() -> None:
    local = datetime(2026, 7, 19, 18, 0, tzinfo=timezone(timedelta(hours=8)))

    normalized = normalize_utc_timestamp(local)

    assert normalized == T0
    assert normalized.tzinfo is UTC


@pytest.mark.parametrize("value", [datetime(2026, 7, 19, 10, 0), "2026-07-19T10:00:00Z", None])
def test_normalize_utc_timestamp_rejects_naive_or_wrong_types(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        normalize_utc_timestamp(value)  # type: ignore[arg-type]


def test_event_provenance_normalizes_timestamps_and_is_frozen() -> None:
    eastern = timezone(timedelta(hours=-4))
    provenance = SMCV2EventProvenance(
        source_indices=(2, 4),
        source_timestamps=(
            datetime(2026, 7, 19, 6, 0, tzinfo=eastern),
            datetime(2026, 7, 19, 6, 5, tzinfo=eastern),
        ),
        confirmation_index=5,
        confirmation_timestamp=datetime(2026, 7, 19, 6, 10, tzinfo=eastern),
    )

    assert provenance.source_timestamps == (T0, T0 + timedelta(minutes=5))
    assert provenance.confirmation_timestamp == T0 + timedelta(minutes=10)
    with pytest.raises(FrozenInstanceError):
        provenance.confirmation_index = 6  # type: ignore[misc]


@pytest.mark.parametrize(
    "source_indices",
    [(), (-1,), (2, 2), (3, 2), (True,)],
)
def test_event_provenance_rejects_invalid_source_indices(
    source_indices: tuple[int, ...],
) -> None:
    timestamps = tuple(T0 + timedelta(minutes=index) for index in range(len(source_indices)))
    with pytest.raises((TypeError, ValueError)):
        SMCV2EventProvenance(
            source_indices=source_indices,
            source_timestamps=timestamps,
            confirmation_index=10,
            confirmation_timestamp=T0 + timedelta(minutes=10),
        )


def test_event_provenance_requires_tuple_inputs_of_equal_length() -> None:
    with pytest.raises(TypeError):
        SMCV2EventProvenance(
            source_indices=[1],  # type: ignore[arg-type]
            source_timestamps=(T0,),
            confirmation_index=1,
            confirmation_timestamp=T0,
        )
    with pytest.raises(ValueError):
        SMCV2EventProvenance(
            source_indices=(1, 2),
            source_timestamps=(T0,),
            confirmation_index=2,
            confirmation_timestamp=T0,
        )


def test_event_provenance_rejects_bad_timestamp_order() -> None:
    with pytest.raises(ValueError, match="chronological"):
        SMCV2EventProvenance(
            source_indices=(1, 2),
            source_timestamps=(T0 + timedelta(minutes=1), T0),
            confirmation_index=2,
            confirmation_timestamp=T0 + timedelta(minutes=2),
        )


def test_event_provenance_rejects_early_confirmation_index_or_time() -> None:
    with pytest.raises(ValueError, match="confirmation_index"):
        SMCV2EventProvenance(
            source_indices=(2, 4),
            source_timestamps=(T0, T0 + timedelta(minutes=5)),
            confirmation_index=3,
            confirmation_timestamp=T0 + timedelta(minutes=10),
        )
    with pytest.raises(ValueError, match="confirmation_timestamp"):
        SMCV2EventProvenance(
            source_indices=(2, 4),
            source_timestamps=(T0, T0 + timedelta(minutes=5)),
            confirmation_index=4,
            confirmation_timestamp=T0 + timedelta(minutes=4),
        )


def test_tick_range_supports_point_and_width_and_is_frozen() -> None:
    point = SMCV2TickRange(10, 10)
    zone = SMCV2TickRange(10, 14)

    assert point.width_ticks == 0
    assert zone.width_ticks == 4
    with pytest.raises(FrozenInstanceError):
        zone.upper_tick = 15  # type: ignore[misc]


@pytest.mark.parametrize("lower,upper", [(2, 1), (True, 2), (1, False), (1.0, 2)])
def test_tick_range_rejects_invalid_boundaries(lower: object, upper: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        SMCV2TickRange(lower, upper)  # type: ignore[arg-type]


def test_lifecycle_event_normalizes_time_and_reason_and_is_frozen() -> None:
    event = SMCV2LifecycleEvent(
        from_state=None,
        to_state=SMCV2LifecycleState.DETECTED,
        index=1,
        timestamp=datetime(2026, 7, 19, 18, 0, tzinfo=timezone(timedelta(hours=8))),
        reason="  synthetic detection  ",
    )

    assert event.timestamp == T0
    assert event.reason == "synthetic detection"
    with pytest.raises(FrozenInstanceError):
        event.index = 2  # type: ignore[misc]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"from_state": SMCV2LifecycleState.ACTIVE, "to_state": SMCV2LifecycleState.ACTIVE},
        {"index": -1},
        {"index": True},
        {"reason": "  "},
        {"to_state": "DETECTED"},
    ],
)
def test_lifecycle_event_rejects_invalid_fields(kwargs: dict[str, object]) -> None:
    values: dict[str, object] = {
        "from_state": None,
        "to_state": SMCV2LifecycleState.DETECTED,
        "index": 0,
        "timestamp": T0,
        "reason": "synthetic",
    }
    values.update(kwargs)
    with pytest.raises((TypeError, ValueError)):
        SMCV2LifecycleEvent(**values)  # type: ignore[arg-type]


def test_validate_lifecycle_history_accepts_valid_synthetic_graph() -> None:
    events = (
        _event(None, SMCV2LifecycleState.DETECTED, 1),
        _event(SMCV2LifecycleState.DETECTED, SMCV2LifecycleState.ACTIVE, 2),
        _event(SMCV2LifecycleState.ACTIVE, SMCV2LifecycleState.TOUCHED, 3),
        _event(SMCV2LifecycleState.TOUCHED, SMCV2LifecycleState.MITIGATED, 4),
    )

    assert (
        validate_lifecycle_history(
            events,
            allowed_transitions=_allowed_transitions(),
            terminal_states=_terminal_states(),
        )
        is None
    )


def test_validate_lifecycle_history_rejects_empty_or_non_tuple_history() -> None:
    with pytest.raises(ValueError):
        validate_lifecycle_history(
            (),
            allowed_transitions=_allowed_transitions(),
            terminal_states=_terminal_states(),
        )
    with pytest.raises(TypeError):
        validate_lifecycle_history(
            [],  # type: ignore[arg-type]
            allowed_transitions=_allowed_transitions(),
            terminal_states=_terminal_states(),
        )


def test_validate_lifecycle_history_rejects_illegal_or_broken_chain() -> None:
    illegal = (
        _event(None, SMCV2LifecycleState.DETECTED, 1),
        _event(SMCV2LifecycleState.DETECTED, SMCV2LifecycleState.MITIGATED, 2),
    )
    broken = (
        _event(None, SMCV2LifecycleState.DETECTED, 1),
        _event(SMCV2LifecycleState.ACTIVE, SMCV2LifecycleState.TOUCHED, 2),
    )

    with pytest.raises(ValueError, match="not allowed"):
        validate_lifecycle_history(
            illegal,
            allowed_transitions=_allowed_transitions(),
            terminal_states=_terminal_states(),
        )
    with pytest.raises(ValueError, match="chain"):
        validate_lifecycle_history(
            broken,
            allowed_transitions=_allowed_transitions(),
            terminal_states=_terminal_states(),
        )


def test_validate_lifecycle_history_rejects_non_chronological_events() -> None:
    same_index = (
        _event(None, SMCV2LifecycleState.DETECTED, 1),
        _event(SMCV2LifecycleState.DETECTED, SMCV2LifecycleState.ACTIVE, 1, minutes=2),
    )
    reversed_time = (
        _event(None, SMCV2LifecycleState.DETECTED, 1, minutes=2),
        _event(SMCV2LifecycleState.DETECTED, SMCV2LifecycleState.ACTIVE, 2, minutes=1),
    )

    for events in (same_index, reversed_time):
        with pytest.raises(ValueError, match="chronological"):
            validate_lifecycle_history(
                events,
                allowed_transitions=_allowed_transitions(),
                terminal_states=_terminal_states(),
            )


def test_validate_lifecycle_history_rejects_transition_after_terminal_state() -> None:
    transitions = _allowed_transitions()
    transitions[SMCV2LifecycleState.MITIGATED] = frozenset({SMCV2LifecycleState.ACTIVE})
    events = (
        _event(None, SMCV2LifecycleState.DETECTED, 1),
        _event(SMCV2LifecycleState.DETECTED, SMCV2LifecycleState.ACTIVE, 2),
        _event(SMCV2LifecycleState.ACTIVE, SMCV2LifecycleState.TOUCHED, 3),
        _event(SMCV2LifecycleState.TOUCHED, SMCV2LifecycleState.MITIGATED, 4),
        _event(SMCV2LifecycleState.MITIGATED, SMCV2LifecycleState.ACTIVE, 5),
    )

    with pytest.raises(ValueError, match="terminal"):
        validate_lifecycle_history(
            events,
            allowed_transitions=transitions,
            terminal_states=_terminal_states(),
        )


def test_validate_lifecycle_history_requires_immutable_transition_sets() -> None:
    transitions = _allowed_transitions()
    transitions[None] = {SMCV2LifecycleState.DETECTED}  # type: ignore[assignment]

    with pytest.raises(TypeError, match="frozenset"):
        validate_lifecycle_history(
            (_event(None, SMCV2LifecycleState.DETECTED, 1),),
            allowed_transitions=transitions,
            terminal_states=_terminal_states(),
        )


def test_deterministic_id_matches_locked_golden_vector() -> None:
    assert _identity() == "802b6904dd2583ccd69ffc809457644ba218a93eab8ee7a6ca21ac8a0fb1b180"


def test_deterministic_id_is_repeatable_and_canonicalizes_text_case() -> None:
    first = _identity()
    second = _identity(detector_version="smc-v2.0", instrument="GC", timeframe="M5")

    assert first == second
    assert re.fullmatch(r"[0-9a-f]{64}", first)


@pytest.mark.parametrize(
    "override",
    [
        {"detector_version": "smc-v2.1"},
        {"instrument": "SI"},
        {"timeframe": "M10"},
        {"source_indices": (10, 11, 13)},
        {"direction": SMCV2Direction.BEARISH},
        {"boundaries": SMCV2TickRange(41875, 41901)},
    ],
)
def test_deterministic_id_changes_when_identity_input_changes(
    override: dict[str, object],
) -> None:
    assert _identity(**override) != _identity()


@pytest.mark.parametrize(
    "override",
    [
        {"detector_version": " "},
        {"instrument": ""},
        {"timeframe": " "},
        {"source_indices": ()},
        {"source_indices": (2, 2)},
        {"source_indices": (2, 1)},
        {"source_indices": (True,)},
        {"direction": "BULLISH"},
        {"boundaries": (1, 2)},
    ],
)
def test_deterministic_id_rejects_invalid_inputs(override: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        _identity(**override)


def test_tick_scaling_preserves_identity_when_normalized_boundaries_match() -> None:
    lower_a = price_to_ticks("10.5", "0.5")
    upper_a = price_to_ticks("12.0", "0.5")
    lower_b = price_to_ticks("105", "5")
    upper_b = price_to_ticks("120", "5")

    assert _identity(boundaries=SMCV2TickRange(lower_a, upper_a)) == _identity(
        boundaries=SMCV2TickRange(lower_b, upper_b)
    )


def test_identity_is_prefix_invariant_to_unrelated_future_observations() -> None:
    source_indices = (10, 11, 12)
    extended_observations = source_indices + (13, 14, 15)

    prefix_id = _identity(source_indices=source_indices)
    replayed_prefix_id = _identity(source_indices=extended_observations[: len(source_indices)])

    assert replayed_prefix_id == prefix_id
