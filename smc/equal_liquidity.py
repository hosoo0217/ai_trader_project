"""Deterministic standalone Equal High and Equal Low diagnostics.

The detector consumes immutable, already-confirmed swings represented in integer
ticks. It is intentionally isolated from the current application, strategy,
risk, and execution paths and performs no I/O or runtime registration.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import re
from typing import Literal

from smc.smc_v2_primitives import (
    SMCV2EventProvenance,
    SMCV2LifecycleEvent,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    normalize_utc_timestamp,
    validate_lifecycle_history,
)


EQUAL_LIQUIDITY_DETECTOR_VERSION = "SMC-V2-EQUAL-LIQUIDITY-1"

_IdentityKind = Literal["SWING", "CANDIDATE", "LINEAGE", "SNAPSHOT"]
_IDENTITY_KINDS = frozenset({"SWING", "CANDIDATE", "LINEAGE", "SNAPSHOT"})
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_MISSING = object()


class EqualLiquiditySide(str, Enum):
    """Liquidity side without directional trading interpretation."""

    HIGH = "HIGH"
    LOW = "LOW"


@dataclass(frozen=True)
class EqualLiquidityConfig:
    """Locked configuration for the first detector version."""

    tolerance_ticks: int = 2
    minimum_members: int = 2
    minimum_separation_bars: int = 3

    def __post_init__(self) -> None:
        values = (
            self.tolerance_ticks,
            self.minimum_members,
            self.minimum_separation_bars,
        )
        if any(type(value) is not int for value in values):
            raise TypeError("equal-liquidity configuration values must be integers")
        if self.tolerance_ticks < 0:
            raise ValueError("tolerance_ticks cannot be negative")
        if self.minimum_members <= 0 or self.minimum_separation_bars <= 0:
            raise ValueError("member and separation minimums must be positive")
        if values != (2, 2, 3):
            raise ValueError("this detector version requires the locked 2/2/3 configuration")


@dataclass(frozen=True)
class EqualLiquiditySwing:
    """One caller-supplied, already-confirmed swing point."""

    side: EqualLiquiditySide
    price_tick: int
    provenance: SMCV2EventProvenance
    swing_id: str


@dataclass(frozen=True)
class EqualLiquidityObservation:
    """One fully closed integer-tick bar used only for pool lifecycle checks."""

    index: int
    timestamp: datetime
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class EqualLiquidityPool:
    """One immutable emitted snapshot of a completed liquidity pool."""

    side: EqualLiquiditySide
    lineage_id: str
    snapshot_id: str
    member_swing_ids: tuple[str, ...]
    source_indices: tuple[int, ...]
    reference_tick: int
    lower_tick: int
    upper_tick: int
    first_known_provenance: SMCV2EventProvenance
    lifecycle_state: SMCV2LifecycleState
    lifecycle_events: tuple[SMCV2LifecycleEvent, ...]


@dataclass(frozen=True)
class EqualLiquidityResult:
    """Fail-closed standalone detector result."""

    status: SMCV2PrimitiveStatus
    pools: tuple[EqualLiquidityPool, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass
class _Candidate:
    side: EqualLiquiditySide
    candidate_id: str
    members: list[EqualLiquiditySwing] = field(default_factory=list)
    lineage_id: str | None = None
    first_known_provenance: SMCV2EventProvenance | None = None
    lifecycle_events: tuple[SMCV2LifecycleEvent, ...] = ()
    consumed: bool = False

    @property
    def active(self) -> bool:
        return self.lineage_id is not None

    @property
    def assignment_id(self) -> str:
        return self.lineage_id if self.lineage_id is not None else self.candidate_id


class _InvalidAnalysis(ValueError):
    pass


class _AmbiguousAnalysis(ValueError):
    pass


def make_equal_liquidity_id(
    *,
    identity_kind: _IdentityKind | str,
    instrument: str,
    timeframe: str,
    side: EqualLiquiditySide,
    source_indices: tuple[int, ...],
    swing_ids: tuple[str, ...] = (),
    reference_tick: int | None = None,
    lower_tick: int | None = None,
    upper_tick: int | None = None,
    lineage_id: str | None = None,
    lifecycle_state: SMCV2LifecycleState | None = None,
) -> str:
    """Return one side-aware canonical SHA-256 identity.

    Required and forbidden fields are validated separately for each locked
    identity kind so semantically different identities cannot share a payload
    shape accidentally.
    """

    if not isinstance(identity_kind, str) or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind must be SWING, CANDIDATE, LINEAGE, or SNAPSHOT")
    canonical_instrument = _normalize_required_text(instrument, name="instrument").upper()
    canonical_timeframe = _normalize_required_text(timeframe, name="timeframe").upper()
    if not isinstance(side, EqualLiquiditySide):
        raise TypeError("side must be an EqualLiquiditySide")
    _validate_source_indices(source_indices)
    _validate_swing_ids(swing_ids)

    payload: dict[str, object] = {
        "detector_version": EQUAL_LIQUIDITY_DETECTOR_VERSION,
        "identity_kind": identity_kind,
        "instrument": canonical_instrument,
        "side": side.value,
        "timeframe": canonical_timeframe,
    }

    if identity_kind == "SWING":
        _require_length(source_indices, 1, name="SWING source_indices")
        _require_length(swing_ids, 0, name="SWING swing_ids")
        _validate_tick_triplet(reference_tick, lower_tick, upper_tick)
        if lower_tick != reference_tick or upper_tick != reference_tick:
            raise ValueError("SWING boundaries must equal its reference tick")
        _reject_identity_extras(lineage_id=lineage_id, lifecycle_state=lifecycle_state)
        payload.update(
            {
                "boundary": {"lower_tick": lower_tick, "upper_tick": upper_tick},
                "source_index": source_indices[0],
            }
        )
    elif identity_kind == "CANDIDATE":
        _require_length(source_indices, 1, name="CANDIDATE source_indices")
        _require_length(swing_ids, 1, name="CANDIDATE swing_ids")
        _reject_tick_fields(reference_tick, lower_tick, upper_tick)
        _reject_identity_extras(lineage_id=lineage_id, lifecycle_state=lifecycle_state)
        payload.update(
            {
                "first_member_source_index": source_indices[0],
                "first_member_swing_id": swing_ids[0],
            }
        )
    elif identity_kind == "LINEAGE":
        _require_length(source_indices, 2, name="LINEAGE source_indices")
        _require_length(swing_ids, 2, name="LINEAGE swing_ids")
        _validate_tick_triplet(reference_tick, lower_tick, upper_tick)
        _reject_identity_extras(lineage_id=lineage_id, lifecycle_state=lifecycle_state)
        payload.update(
            {
                "founding_lower_tick": lower_tick,
                "founding_reference_tick": reference_tick,
                "founding_source_indices": list(source_indices),
                "founding_swing_ids": list(swing_ids),
                "founding_upper_tick": upper_tick,
            }
        )
    else:
        if len(source_indices) < 2:
            raise ValueError("SNAPSHOT requires at least two source indices")
        if len(swing_ids) != len(source_indices):
            raise ValueError("SNAPSHOT swing_ids must match source_indices")
        _validate_tick_triplet(reference_tick, lower_tick, upper_tick)
        _validate_hash(lineage_id, name="lineage_id")
        if not isinstance(lifecycle_state, SMCV2LifecycleState):
            raise TypeError("SNAPSHOT lifecycle_state must be SMCV2LifecycleState")
        payload.update(
            {
                "lifecycle_state": lifecycle_state.value,
                "lineage_id": lineage_id,
                "lower_tick": lower_tick,
                "reference_tick": reference_tick,
                "source_indices": list(source_indices),
                "swing_ids": list(swing_ids),
                "upper_tick": upper_tick,
            }
        )

    canonical_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def analyze_equal_liquidity(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[EqualLiquiditySwing, ...] | None,
    observations: tuple[EqualLiquidityObservation, ...] | None,
    config: EqualLiquidityConfig = EqualLiquidityConfig(),
) -> EqualLiquidityResult:
    """Analyze confirmed swings and closed observations without integration."""

    if swings is None or observations is None:
        missing = []
        if swings is None:
            missing.append("swings")
        if observations is None:
            missing.append("observations")
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return EqualLiquidityResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    try:
        canonical_instrument = _normalize_required_text(instrument, name="instrument").upper()
        canonical_timeframe = _normalize_required_text(timeframe, name="timeframe").upper()
        _validate_config(config)
        _validate_swings(
            swings,
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
        )
        _validate_observations(observations)
        snapshots = _analyze_valid_inputs(
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
            swings=swings,
            observations=observations,
            config=config,
        )
    except _AmbiguousAnalysis as exc:
        reason = str(exc)
        return EqualLiquidityResult(
            status=SMCV2PrimitiveStatus.AMBIGUOUS,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )
    except (TypeError, ValueError, _InvalidAnalysis) as exc:
        reason = str(exc) or exc.__class__.__name__
        return EqualLiquidityResult(
            status=SMCV2PrimitiveStatus.INVALID,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    if not snapshots:
        return EqualLiquidityResult(
            status=SMCV2PrimitiveStatus.NONE,
            reasons=("No completed Equal High or Equal Low pool",),
        )
    return EqualLiquidityResult(
        status=SMCV2PrimitiveStatus.VALID,
        pools=tuple(snapshots),
        reasons=("Deterministic Equal High and Equal Low analysis completed",),
    )


def _analyze_valid_inputs(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[EqualLiquiditySwing, ...],
    observations: tuple[EqualLiquidityObservation, ...],
    config: EqualLiquidityConfig,
) -> list[EqualLiquidityPool]:
    candidates: list[_Candidate] = []
    snapshots: list[EqualLiquidityPool] = []
    swings_by_confirmation: dict[int, list[EqualLiquiditySwing]] = {}
    observations_by_index: dict[int, EqualLiquidityObservation] = {}

    for swing in swings:
        swings_by_confirmation.setdefault(swing.provenance.confirmation_index, []).append(swing)
    for observation in observations:
        observations_by_index[observation.index] = observation

    event_indices = sorted(set(swings_by_confirmation) | set(observations_by_index))
    for event_index in event_indices:
        observation = observations_by_index.get(event_index)
        if observation is not None:
            _apply_observation(
                observation,
                candidates=candidates,
                snapshots=snapshots,
                instrument=instrument,
                timeframe=timeframe,
            )

        for swing in swings_by_confirmation.get(event_index, ()):
            _assign_swing(
                swing,
                candidates=candidates,
                snapshots=snapshots,
                instrument=instrument,
                timeframe=timeframe,
                config=config,
            )

    return snapshots


def _assign_swing(
    swing: EqualLiquiditySwing,
    *,
    candidates: list[_Candidate],
    snapshots: list[EqualLiquidityPool],
    instrument: str,
    timeframe: str,
    config: EqualLiquidityConfig,
) -> None:
    eligible: list[tuple[tuple[object, ...], _Candidate]] = []
    for candidate in candidates:
        if candidate.consumed or candidate.side is not swing.side:
            continue
        if not _can_join(candidate, swing, config=config):
            continue
        first = candidate.members[0]
        first_key = (
            first.provenance.confirmation_index,
            normalize_utc_timestamp(first.provenance.confirmation_timestamp),
        )
        rank = (
            abs(swing.price_tick - _median_tick(candidate.members)),
            *first_key,
            candidate.assignment_id,
        )
        eligible.append((rank, candidate))

    if not eligible:
        candidate_id = make_equal_liquidity_id(
            identity_kind="CANDIDATE",
            instrument=instrument,
            timeframe=timeframe,
            side=swing.side,
            source_indices=(_source_index(swing),),
            swing_ids=(swing.swing_id,),
        )
        if any(candidate.candidate_id == candidate_id for candidate in candidates):
            raise _InvalidAnalysis("duplicate pending candidate identity")
        candidates.append(
            _Candidate(
                side=swing.side,
                candidate_id=candidate_id,
                members=[swing],
            )
        )
        return

    eligible.sort(key=lambda item: item[0])
    if len(eligible) > 1 and eligible[0][0] == eligible[1][0]:
        raise _AmbiguousAnalysis("candidate assignment remains tied after all tie-breakers")
    candidate = eligible[0][1]
    candidate.members.append(swing)

    if not candidate.active:
        _activate_candidate(
            candidate,
            snapshots=snapshots,
            instrument=instrument,
            timeframe=timeframe,
            config=config,
        )
        return
    snapshots.append(
        _snapshot(
            candidate,
            instrument=instrument,
            timeframe=timeframe,
            config=config,
        )
    )


def _activate_candidate(
    candidate: _Candidate,
    *,
    snapshots: list[EqualLiquidityPool],
    instrument: str,
    timeframe: str,
    config: EqualLiquidityConfig,
) -> None:
    if len(candidate.members) != config.minimum_members:
        raise _InvalidAnalysis("a pending candidate must activate with exactly two founders")
    founders = tuple(candidate.members)
    reference_tick = _median_tick(candidate.members)
    lower_tick = reference_tick - config.tolerance_ticks
    upper_tick = reference_tick + config.tolerance_ticks
    source_indices = tuple(_source_index(member) for member in founders)
    swing_ids = tuple(member.swing_id for member in founders)
    candidate.lineage_id = make_equal_liquidity_id(
        identity_kind="LINEAGE",
        instrument=instrument,
        timeframe=timeframe,
        side=candidate.side,
        source_indices=source_indices,
        swing_ids=swing_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
    )

    later = max(
        founders,
        key=lambda member: (
            member.provenance.confirmation_index,
            normalize_utc_timestamp(member.provenance.confirmation_timestamp),
        ),
    )
    candidate.first_known_provenance = SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(
            member.provenance.source_timestamps[0] for member in founders
        ),
        confirmation_index=later.provenance.confirmation_index,
        confirmation_timestamp=later.provenance.confirmation_timestamp,
    )
    candidate.lifecycle_events = (
        SMCV2LifecycleEvent(
            from_state=None,
            to_state=SMCV2LifecycleState.ACTIVE,
            index=candidate.first_known_provenance.confirmation_index,
            timestamp=candidate.first_known_provenance.confirmation_timestamp,
            reason="second qualifying equal-liquidity swing confirmed",
        ),
    )
    _validate_candidate_lifecycle(candidate.lifecycle_events)
    snapshots.append(
        _snapshot(
            candidate,
            instrument=instrument,
            timeframe=timeframe,
            config=config,
        )
    )


def _apply_observation(
    observation: EqualLiquidityObservation,
    *,
    candidates: list[_Candidate],
    snapshots: list[EqualLiquidityPool],
    instrument: str,
    timeframe: str,
) -> None:
    normalized_timestamp = normalize_utc_timestamp(observation.timestamp)
    for candidate in candidates:
        if not candidate.active or candidate.consumed:
            continue
        if candidate.first_known_provenance is None:
            raise _InvalidAnalysis("active pool is missing first-known provenance")
        first_known = candidate.first_known_provenance
        if observation.index <= first_known.confirmation_index:
            continue
        if normalized_timestamp < first_known.confirmation_timestamp:
            raise _InvalidAnalysis("lifecycle observation precedes first-known timestamp")

        lineage_snapshots = [
            pool for pool in snapshots if pool.lineage_id == candidate.lineage_id
        ]
        if not lineage_snapshots:
            raise _InvalidAnalysis("active lineage has no emitted snapshot")
        current = lineage_snapshots[-1]
        terminal_state = _terminal_state(candidate.side, current, observation)
        if terminal_state is None:
            continue

        candidate.lifecycle_events = (
            *candidate.lifecycle_events,
            SMCV2LifecycleEvent(
                from_state=SMCV2LifecycleState.ACTIVE,
                to_state=terminal_state,
                index=observation.index,
                timestamp=normalized_timestamp,
                reason=f"{candidate.side.value} liquidity pool {terminal_state.value.lower()}",
            ),
        )
        _validate_candidate_lifecycle(candidate.lifecycle_events)
        candidate.consumed = True
        snapshots.append(
            _snapshot_from_values(
                candidate,
                reference_tick=current.reference_tick,
                lower_tick=current.lower_tick,
                upper_tick=current.upper_tick,
                instrument=instrument,
                timeframe=timeframe,
            )
        )


def _terminal_state(
    side: EqualLiquiditySide,
    pool: EqualLiquidityPool,
    observation: EqualLiquidityObservation,
) -> SMCV2LifecycleState | None:
    if side is EqualLiquiditySide.HIGH:
        if observation.close_tick >= pool.upper_tick + 1:
            return SMCV2LifecycleState.BROKEN
        if (
            observation.high_tick >= pool.upper_tick + 1
            and observation.close_tick <= pool.upper_tick
        ):
            return SMCV2LifecycleState.SWEPT
        return None
    if observation.close_tick <= pool.lower_tick - 1:
        return SMCV2LifecycleState.BROKEN
    if (
        observation.low_tick <= pool.lower_tick - 1
        and observation.close_tick >= pool.lower_tick
    ):
        return SMCV2LifecycleState.SWEPT
    return None


def _can_join(
    candidate: _Candidate,
    swing: EqualLiquiditySwing,
    *,
    config: EqualLiquidityConfig,
) -> bool:
    latest_source = _source_index(candidate.members[-1])
    source_index = _source_index(swing)
    if source_index - latest_source < config.minimum_separation_bars:
        return False

    current_reference = _median_tick(candidate.members)
    if abs(swing.price_tick - current_reference) > config.tolerance_ticks:
        return False

    tentative = [*candidate.members, swing]
    tentative_reference = _median_tick(tentative)
    lower_tick = tentative_reference - config.tolerance_ticks
    upper_tick = tentative_reference + config.tolerance_ticks
    return all(lower_tick <= member.price_tick <= upper_tick for member in tentative)


def _snapshot(
    candidate: _Candidate,
    *,
    instrument: str,
    timeframe: str,
    config: EqualLiquidityConfig,
) -> EqualLiquidityPool:
    reference_tick = _median_tick(candidate.members)
    return _snapshot_from_values(
        candidate,
        reference_tick=reference_tick,
        lower_tick=reference_tick - config.tolerance_ticks,
        upper_tick=reference_tick + config.tolerance_ticks,
        instrument=instrument,
        timeframe=timeframe,
    )


def _snapshot_from_values(
    candidate: _Candidate,
    *,
    reference_tick: int,
    lower_tick: int,
    upper_tick: int,
    instrument: str,
    timeframe: str,
) -> EqualLiquidityPool:
    if candidate.lineage_id is None or candidate.first_known_provenance is None:
        raise _InvalidAnalysis("cannot emit a snapshot for an inactive candidate")
    if not candidate.lifecycle_events:
        raise _InvalidAnalysis("cannot emit a snapshot without lifecycle history")
    source_indices = tuple(_source_index(member) for member in candidate.members)
    swing_ids = tuple(member.swing_id for member in candidate.members)
    lifecycle_state = candidate.lifecycle_events[-1].to_state
    snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        side=candidate.side,
        source_indices=source_indices,
        swing_ids=swing_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        lineage_id=candidate.lineage_id,
        lifecycle_state=lifecycle_state,
    )
    return EqualLiquidityPool(
        side=candidate.side,
        lineage_id=candidate.lineage_id,
        snapshot_id=snapshot_id,
        member_swing_ids=swing_ids,
        source_indices=source_indices,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        first_known_provenance=candidate.first_known_provenance,
        lifecycle_state=lifecycle_state,
        lifecycle_events=candidate.lifecycle_events,
    )


def _median_tick(members: list[EqualLiquiditySwing]) -> int:
    if not members:
        raise _InvalidAnalysis("cannot calculate a median without members")
    prices = sorted(member.price_tick for member in members)
    midpoint = len(prices) // 2
    if len(prices) % 2:
        return prices[midpoint]
    total = prices[midpoint - 1] + prices[midpoint]
    if total % 2 == 0:
        return total // 2
    lower = total // 2
    return lower if lower % 2 == 0 else lower + 1


def _validate_config(config: EqualLiquidityConfig) -> None:
    if not isinstance(config, EqualLiquidityConfig):
        raise TypeError("config must be EqualLiquidityConfig")
    values = (
        config.tolerance_ticks,
        config.minimum_members,
        config.minimum_separation_bars,
    )
    if any(type(value) is not int for value in values) or values != (2, 2, 3):
        raise ValueError("config does not match the locked 2/2/3 detector version")


def _validate_swings(
    swings: tuple[EqualLiquiditySwing, ...],
    *,
    instrument: str,
    timeframe: str,
) -> None:
    if not isinstance(swings, tuple):
        raise TypeError("swings must be an immutable tuple")
    previous_source_index = -1
    previous_source_timestamp: datetime | None = None
    previous_confirmation_key: tuple[object, ...] | None = None
    seen_swing_ids: set[str] = set()

    for swing in swings:
        if not isinstance(swing, EqualLiquiditySwing):
            raise TypeError("swings must contain only EqualLiquiditySwing values")
        side = _required_attribute(swing, "side", owner="EqualLiquiditySwing")
        price_tick = _required_attribute(swing, "price_tick", owner="EqualLiquiditySwing")
        provenance = _required_attribute(swing, "provenance", owner="EqualLiquiditySwing")
        swing_id = _required_attribute(swing, "swing_id", owner="EqualLiquiditySwing")
        if not isinstance(side, EqualLiquiditySide):
            raise TypeError("swing side must be EqualLiquiditySide")
        if type(price_tick) is not int:
            raise TypeError("swing price_tick must be an integer")
        if not isinstance(provenance, SMCV2EventProvenance):
            raise TypeError("swing provenance must be SMCV2EventProvenance")
        source_indices = _required_attribute(
            provenance,
            "source_indices",
            owner="SMCV2EventProvenance",
        )
        source_timestamps = _required_attribute(
            provenance,
            "source_timestamps",
            owner="SMCV2EventProvenance",
        )
        confirmation_index = _required_attribute(
            provenance,
            "confirmation_index",
            owner="SMCV2EventProvenance",
        )
        confirmation_timestamp_value = _required_attribute(
            provenance,
            "confirmation_timestamp",
            owner="SMCV2EventProvenance",
        )
        if not isinstance(source_indices, tuple) or not isinstance(source_timestamps, tuple):
            raise TypeError("swing provenance source fields must be tuples")
        if len(source_indices) != 1 or len(source_timestamps) != 1:
            raise ValueError("each swing provenance must contain exactly one source event")
        source_index = source_indices[0]
        if type(source_index) is not int or source_index < 0:
            raise TypeError("swing provenance source index must be a non-negative integer")
        if type(confirmation_index) is not int or confirmation_index < 0:
            raise TypeError("swing confirmation index must be a non-negative integer")
        source_timestamp = normalize_utc_timestamp(source_timestamps[0])
        confirmation_timestamp = normalize_utc_timestamp(confirmation_timestamp_value)
        if confirmation_index < source_index + 2:
            raise ValueError("swing confirmation cannot precede source index plus two")
        if source_index <= previous_source_index:
            raise ValueError("swing source indices must be unique and strictly chronological")
        if previous_source_timestamp is not None and source_timestamp <= previous_source_timestamp:
            raise ValueError("swing source timestamps must be strictly chronological")
        confirmation_key = (
            confirmation_index,
            confirmation_timestamp,
            source_index,
            swing_id,
        )
        if previous_confirmation_key is not None and confirmation_key < previous_confirmation_key:
            raise ValueError("swing confirmations must be supplied chronologically")
        _validate_hash(swing_id, name="swing_id")
        if swing_id in seen_swing_ids:
            raise ValueError("duplicate swing identity")
        expected_id = make_equal_liquidity_id(
            identity_kind="SWING",
            instrument=instrument,
            timeframe=timeframe,
            side=side,
            source_indices=(source_index,),
            reference_tick=price_tick,
            lower_tick=price_tick,
            upper_tick=price_tick,
        )
        if swing_id != expected_id:
            raise ValueError("swing_id does not match reviewed swing fields")

        seen_swing_ids.add(swing_id)
        previous_source_index = source_index
        previous_source_timestamp = source_timestamp
        previous_confirmation_key = confirmation_key


def _validate_observations(
    observations: tuple[EqualLiquidityObservation, ...],
) -> None:
    if not isinstance(observations, tuple):
        raise TypeError("observations must be an immutable tuple")
    previous_index = -1
    previous_timestamp: datetime | None = None
    for observation in observations:
        if not isinstance(observation, EqualLiquidityObservation):
            raise TypeError("observations must contain only EqualLiquidityObservation values")
        index = _required_attribute(
            observation,
            "index",
            owner="EqualLiquidityObservation",
        )
        timestamp = _required_attribute(
            observation,
            "timestamp",
            owner="EqualLiquidityObservation",
        )
        high_tick = _required_attribute(
            observation,
            "high_tick",
            owner="EqualLiquidityObservation",
        )
        low_tick = _required_attribute(
            observation,
            "low_tick",
            owner="EqualLiquidityObservation",
        )
        close_tick = _required_attribute(
            observation,
            "close_tick",
            owner="EqualLiquidityObservation",
        )
        if type(index) is not int or index < 0:
            raise TypeError("observation index must be a non-negative integer")
        ticks = (high_tick, low_tick, close_tick)
        if any(type(tick) is not int for tick in ticks):
            raise TypeError("observation ticks must be integers")
        if not low_tick <= close_tick <= high_tick:
            raise ValueError("observation must satisfy low <= close <= high")
        normalized_timestamp = normalize_utc_timestamp(timestamp)
        if index <= previous_index:
            raise ValueError("observation indices must be unique and strictly chronological")
        if previous_timestamp is not None and normalized_timestamp < previous_timestamp:
            raise ValueError("observation timestamps must be chronological")
        previous_index = index
        previous_timestamp = normalized_timestamp


def _validate_candidate_lifecycle(
    events: tuple[SMCV2LifecycleEvent, ...],
) -> None:
    state = SMCV2LifecycleState
    allowed: Mapping[
        SMCV2LifecycleState | None,
        frozenset[SMCV2LifecycleState],
    ] = {
        None: frozenset({state.ACTIVE}),
        state.ACTIVE: frozenset({state.SWEPT, state.BROKEN}),
        state.SWEPT: frozenset(),
        state.BROKEN: frozenset(),
    }
    validate_lifecycle_history(
        events,
        allowed_transitions=allowed,
        terminal_states=frozenset({state.SWEPT, state.BROKEN}),
    )


def _source_index(swing: EqualLiquiditySwing) -> int:
    return swing.provenance.source_indices[0]


def _required_attribute(instance: object, name: str, *, owner: str) -> object:
    value = getattr(instance, name, _MISSING)
    if value is _MISSING:
        raise _InvalidAnalysis(f"{owner} is missing required field: {name}")
    return value


def _validate_source_indices(source_indices: tuple[int, ...]) -> None:
    if not isinstance(source_indices, tuple):
        raise TypeError("source_indices must be a tuple")
    if not source_indices:
        raise ValueError("source_indices cannot be empty")
    if any(type(index) is not int for index in source_indices):
        raise TypeError("source_indices must contain integers")
    if any(index < 0 for index in source_indices):
        raise ValueError("source_indices cannot contain negative values")
    if any(left >= right for left, right in zip(source_indices, source_indices[1:])):
        raise ValueError("source_indices must be unique and strictly increasing")


def _validate_swing_ids(swing_ids: tuple[str, ...]) -> None:
    if not isinstance(swing_ids, tuple):
        raise TypeError("swing_ids must be a tuple")
    for swing_id in swing_ids:
        _validate_hash(swing_id, name="swing_id")
    if len(set(swing_ids)) != len(swing_ids):
        raise ValueError("swing_ids must be unique")


def _validate_hash(value: object, *, name: str) -> None:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase 64-character hexadecimal text")


def _validate_tick_triplet(
    reference_tick: object,
    lower_tick: object,
    upper_tick: object,
) -> None:
    if any(type(value) is not int for value in (reference_tick, lower_tick, upper_tick)):
        raise TypeError("reference and boundary ticks must be integers")
    if lower_tick > reference_tick or reference_tick > upper_tick:
        raise ValueError("ticks must satisfy lower <= reference <= upper")


def _reject_tick_fields(
    reference_tick: object,
    lower_tick: object,
    upper_tick: object,
) -> None:
    if any(value is not None for value in (reference_tick, lower_tick, upper_tick)):
        raise ValueError("this identity kind does not accept reference or boundary ticks")


def _reject_identity_extras(
    *,
    lineage_id: object,
    lifecycle_state: object,
) -> None:
    if lineage_id is not None or lifecycle_state is not None:
        raise ValueError("this identity kind does not accept lineage or lifecycle fields")


def _require_length(values: tuple[object, ...], expected: int, *, name: str) -> None:
    if len(values) != expected:
        raise ValueError(f"{name} must contain exactly {expected} item(s)")


def _normalize_required_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


__all__ = [
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
