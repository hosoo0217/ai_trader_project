"""Deterministic standalone primitives for future SMC v2 diagnostics.

This module is intentionally isolated from the current SMC, decision, risk, and
execution paths. It performs no I/O, reads no configuration, and has no runtime
registration behavior. The types and functions here are shared foundations for
later separately reviewed diagnostic detectors.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from enum import Enum
import hashlib
import json


FLOAT_ALIGNMENT_TOLERANCE_TICKS = Decimal("1e-9")

_DecimalInput = Decimal | int | float | str


class SMCV2PrimitiveStatus(str, Enum):
    """Shared non-directional result vocabulary for future diagnostics."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"
    NONE = "NONE"
    AMBIGUOUS = "AMBIGUOUS"


class SMCV2Direction(str, Enum):
    """Canonical direction vocabulary for deterministic detector identity."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class SMCV2LifecycleState(str, Enum):
    """Reviewed union of lifecycle states used by planned SMC v2 detectors.

    State availability here does not authorize every detector to use every
    state. Each future detector must provide its own reviewed transition graph.
    """

    DETECTED = "DETECTED"
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    PARTIALLY_TOUCHED = "PARTIALLY_TOUCHED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    MIDPOINT_FILLED = "MIDPOINT_FILLED"
    FULLY_FILLED = "FULLY_FILLED"
    PARTIALLY_MITIGATED = "PARTIALLY_MITIGATED"
    MITIGATED = "MITIGATED"
    FULLY_TRAVERSED = "FULLY_TRAVERSED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"
    SWEPT = "SWEPT"
    BROKEN = "BROKEN"


@dataclass(frozen=True)
class SMCV2EventProvenance:
    """Immutable source and first-known confirmation identity."""

    source_indices: tuple[int, ...]
    source_timestamps: tuple[datetime, ...]
    confirmation_index: int
    confirmation_timestamp: datetime

    def __post_init__(self) -> None:
        _validate_source_indices(self.source_indices)
        if not isinstance(self.source_timestamps, tuple):
            raise TypeError("source_timestamps must be a tuple")
        if len(self.source_timestamps) != len(self.source_indices):
            raise ValueError("source_timestamps must match source_indices length")

        normalized_sources = tuple(
            normalize_utc_timestamp(timestamp) for timestamp in self.source_timestamps
        )
        if any(
            earlier >= later
            for earlier, later in zip(normalized_sources, normalized_sources[1:])
        ):
            raise ValueError("source_timestamps must be strictly chronological")

        if type(self.confirmation_index) is not int:
            raise TypeError("confirmation_index must be an integer")
        if self.confirmation_index < self.source_indices[-1]:
            raise ValueError("confirmation_index cannot precede the latest source index")

        normalized_confirmation = normalize_utc_timestamp(self.confirmation_timestamp)
        if normalized_confirmation < normalized_sources[-1]:
            raise ValueError("confirmation_timestamp cannot precede the latest source timestamp")

        object.__setattr__(self, "source_timestamps", normalized_sources)
        object.__setattr__(self, "confirmation_timestamp", normalized_confirmation)


@dataclass(frozen=True)
class SMCV2TickRange:
    """Immutable inclusive price boundaries represented as integer ticks."""

    lower_tick: int
    upper_tick: int

    def __post_init__(self) -> None:
        if type(self.lower_tick) is not int or type(self.upper_tick) is not int:
            raise TypeError("tick boundaries must be integers")
        if self.lower_tick > self.upper_tick:
            raise ValueError("lower_tick cannot exceed upper_tick")

    @property
    def width_ticks(self) -> int:
        """Return the exact distance between inclusive boundaries in ticks."""
        return self.upper_tick - self.lower_tick


@dataclass(frozen=True)
class SMCV2LifecycleEvent:
    """One immutable, timestamped lifecycle transition."""

    from_state: SMCV2LifecycleState | None
    to_state: SMCV2LifecycleState
    index: int
    timestamp: datetime
    reason: str

    def __post_init__(self) -> None:
        if self.from_state is not None and not isinstance(self.from_state, SMCV2LifecycleState):
            raise TypeError("from_state must be an SMCV2LifecycleState or None")
        if not isinstance(self.to_state, SMCV2LifecycleState):
            raise TypeError("to_state must be an SMCV2LifecycleState")
        if self.from_state == self.to_state:
            raise ValueError("a lifecycle event must change state")
        if type(self.index) is not int:
            raise TypeError("lifecycle index must be an integer")
        if self.index < 0:
            raise ValueError("lifecycle index cannot be negative")
        if not isinstance(self.reason, str):
            raise TypeError("lifecycle reason must be text")
        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("lifecycle reason cannot be empty")

        object.__setattr__(self, "timestamp", normalize_utc_timestamp(self.timestamp))
        object.__setattr__(self, "reason", normalized_reason)


def normalize_utc_timestamp(value: datetime) -> datetime:
    """Return one timezone-aware timestamp normalized to UTC.

    Naive timestamps are rejected because silently assigning a timezone could
    change event order and first-known-time evidence.
    """
    if not isinstance(value, datetime):
        raise TypeError("timestamp must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def validate_tick_size(tick_size: _DecimalInput) -> Decimal:
    """Return a canonical positive finite tick size."""
    normalized = _to_finite_decimal(tick_size, name="tick_size")
    if normalized <= 0:
        raise ValueError("tick_size must be greater than zero")
    return normalized.normalize()


def price_to_ticks(price: _DecimalInput, tick_size: _DecimalInput) -> int:
    """Convert an aligned price to an integer tick count deterministically.

    The fixed tolerance absorbs only common binary-float representation noise.
    It does not round a genuinely off-tick price onto a valid boundary.
    """
    normalized_price = _to_finite_decimal(price, name="price")
    normalized_tick = validate_tick_size(tick_size)
    tick_ratio = normalized_price / normalized_tick
    nearest_tick = tick_ratio.to_integral_value(rounding=ROUND_HALF_EVEN)

    if abs(tick_ratio - nearest_tick) > FLOAT_ALIGNMENT_TOLERANCE_TICKS:
        raise ValueError("price must be aligned to tick_size")
    return int(nearest_tick)


def ticks_to_price(ticks: int, tick_size: _DecimalInput) -> Decimal:
    """Convert an integer tick count to an exact canonical Decimal price."""
    if type(ticks) is not int:
        raise TypeError("ticks must be an integer")
    normalized_tick = validate_tick_size(tick_size)
    return (Decimal(ticks) * normalized_tick).normalize()


def validate_lifecycle_history(
    events: tuple[SMCV2LifecycleEvent, ...],
    *,
    allowed_transitions: Mapping[
        SMCV2LifecycleState | None,
        frozenset[SMCV2LifecycleState],
    ],
    terminal_states: frozenset[SMCV2LifecycleState],
) -> None:
    """Validate one detector-specific immutable lifecycle history.

    This function deliberately receives the transition graph from the future
    detector. It does not invent a universal graph for detector-specific states.
    """
    if not isinstance(events, tuple):
        raise TypeError("events must be a tuple")
    if not events:
        raise ValueError("events cannot be empty")
    if not isinstance(allowed_transitions, Mapping):
        raise TypeError("allowed_transitions must be a mapping")
    if not isinstance(terminal_states, frozenset):
        raise TypeError("terminal_states must be a frozenset")
    if any(not isinstance(state, SMCV2LifecycleState) for state in terminal_states):
        raise TypeError("terminal_states must contain only SMCV2LifecycleState values")

    for current_state, next_states in allowed_transitions.items():
        if current_state is not None and not isinstance(current_state, SMCV2LifecycleState):
            raise TypeError("transition keys must be SMCV2LifecycleState or None")
        if not isinstance(next_states, frozenset):
            raise TypeError("allowed transition values must be frozenset instances")
        if any(not isinstance(state, SMCV2LifecycleState) for state in next_states):
            raise TypeError("transition targets must be SMCV2LifecycleState values")

    previous_state: SMCV2LifecycleState | None = None
    previous_index = -1
    previous_timestamp: datetime | None = None

    for position, event in enumerate(events):
        if not isinstance(event, SMCV2LifecycleEvent):
            raise TypeError("events must contain only SMCV2LifecycleEvent values")
        if position == 0:
            if event.from_state is not None:
                raise ValueError("lifecycle chain must begin from None")
        elif event.from_state != previous_state:
            raise ValueError("lifecycle chain does not match the previous state")

        if event.index <= previous_index:
            raise ValueError("lifecycle indices must be strictly chronological")
        if previous_timestamp is not None and event.timestamp < previous_timestamp:
            raise ValueError("lifecycle timestamps must be chronological")
        if position > 0 and previous_state in terminal_states:
            raise ValueError("a terminal lifecycle state cannot transition")

        allowed_next_states = allowed_transitions.get(event.from_state, frozenset())
        if event.to_state not in allowed_next_states:
            raise ValueError(
                f"lifecycle transition {event.from_state!r} -> {event.to_state.value} is not allowed"
            )

        previous_state = event.to_state
        previous_index = event.index
        previous_timestamp = event.timestamp


def make_deterministic_id(
    *,
    detector_version: str,
    instrument: str,
    timeframe: str,
    source_indices: tuple[int, ...],
    direction: SMCV2Direction,
    boundaries: SMCV2TickRange,
) -> str:
    """Return a stable SHA-256 identifier from reviewed normalized inputs."""
    canonical_version = _normalize_required_text(
        detector_version,
        name="detector_version",
    ).lower()
    canonical_instrument = _normalize_required_text(instrument, name="instrument").upper()
    canonical_timeframe = _normalize_required_text(timeframe, name="timeframe").upper()
    _validate_source_indices(source_indices)

    if not isinstance(direction, SMCV2Direction):
        raise TypeError("direction must be an SMCV2Direction")
    if not isinstance(boundaries, SMCV2TickRange):
        raise TypeError("boundaries must be an SMCV2TickRange")

    payload = {
        "boundaries": {
            "lower_tick": boundaries.lower_tick,
            "upper_tick": boundaries.upper_tick,
        },
        "detector_version": canonical_version,
        "direction": direction.value,
        "instrument": canonical_instrument,
        "source_indices": list(source_indices),
        "timeframe": canonical_timeframe,
    }
    canonical_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _to_finite_decimal(value: _DecimalInput, *, name: str) -> Decimal:
    if isinstance(value, bool):
        raise TypeError(f"{name} cannot be a boolean")
    if not isinstance(value, (Decimal, int, float, str)):
        raise TypeError(f"{name} must be Decimal, int, float, or str")
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{name} cannot be empty")

    try:
        normalized = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not normalized.is_finite():
        raise ValueError(f"{name} must be finite")
    return normalized


def _validate_source_indices(source_indices: tuple[int, ...]) -> None:
    if not isinstance(source_indices, tuple):
        raise TypeError("source_indices must be a tuple")
    if not source_indices:
        raise ValueError("source_indices cannot be empty")
    if any(type(index) is not int for index in source_indices):
        raise TypeError("source_indices must contain only integers")
    if any(index < 0 for index in source_indices):
        raise ValueError("source_indices cannot contain negative values")
    if any(earlier >= later for earlier, later in zip(source_indices, source_indices[1:])):
        raise ValueError("source_indices must be unique and strictly increasing")


def _normalize_required_text(value: str, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


__all__ = [
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
