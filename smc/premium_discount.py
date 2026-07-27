"""Deterministic standalone Premium, Equilibrium, and Discount diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from smc.dealing_range import (
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeTransition,
    make_dealing_range_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


PREMIUM_DISCOUNT_DETECTOR_VERSION = "SMC-V2-PREMIUM-DISCOUNT-1"

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY_KINDS = frozenset({"ZONE_SET", "CLASSIFICATION", "SNAPSHOT"})
_CONSTRUCTION_REASON = "CONSTRUCTION_ACTIVE"
_TERMINAL_REASONS = frozenset(
    {
        "OBSERVATION_CLOSE_THROUGH_INVALIDATION",
        "CHOCH_CLOSE_THROUGH_INVALIDATION",
        "BOS_PULLBACK_REPLACEMENT",
    }
)

_Moment = tuple[int, datetime]


class PremiumDiscountZone(str, Enum):
    DISCOUNT = "DISCOUNT"
    EQUILIBRIUM = "EQUILIBRIUM"
    PREMIUM = "PREMIUM"


@dataclass(frozen=True)
class PremiumDiscountObservation:
    index: int
    timestamp: datetime
    price_tick: int


@dataclass(frozen=True)
class PremiumDiscountZoneSet:
    zone_set_id: str
    active_range_lineage_id: str
    creation_range_snapshot_id: str
    direction: SMCV2Direction
    source_swing_ids: tuple[str, ...]
    source_indices: tuple[int, ...]
    protected_swing_id: str
    construction_event_id: str
    low_tick: int
    high_tick: int
    equilibrium_tick: Decimal
    version: int
    first_known_index: int
    first_known_timestamp: datetime
    prior_zone_set_id: str | None


@dataclass(frozen=True)
class PremiumDiscountClassification:
    classification_id: str
    zone_set_id: str
    active_range_lineage_id: str
    active_range_snapshot_id: str
    direction: SMCV2Direction
    zone_set_version: int
    observation_index: int
    observation_timestamp: datetime
    price_tick: int
    zone: PremiumDiscountZone


@dataclass(frozen=True)
class PremiumDiscountSnapshot:
    snapshot_id: str
    active_range_lineage_id: str
    active_range_snapshot_id: str
    zone_set_id: str
    zone_set_version: int
    index: int
    timestamp: datetime
    classification: PremiumDiscountClassification
    classification_id: str


@dataclass(frozen=True)
class PremiumDiscountResult:
    status: SMCV2PrimitiveStatus
    zone_sets: tuple[PremiumDiscountZoneSet, ...] = ()
    classifications: tuple[PremiumDiscountClassification, ...] = ()
    snapshots: tuple[PremiumDiscountSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _RangeRecord:
    value: DealingRangeSnapshot
    moment: _Moment


@dataclass(frozen=True)
class _ObservationRecord:
    value: PremiumDiscountObservation
    moment: _Moment


@dataclass(frozen=True)
class _Issue:
    moment: _Moment | None
    reason: str


@dataclass
class _AnalysisState:
    current_range: DealingRangeSnapshot | None
    latest_by_lineage: dict[str, DealingRangeSnapshot]
    zone_history: dict[str, list[PremiumDiscountZoneSet]]
    zone_sets: list[PremiumDiscountZoneSet]
    classifications: list[PremiumDiscountClassification]
    snapshots: list[PremiumDiscountSnapshot]

    def clone(self) -> _AnalysisState:
        return _AnalysisState(
            current_range=self.current_range,
            latest_by_lineage=dict(self.latest_by_lineage),
            zone_history={
                lineage_id: list(history)
                for lineage_id, history in self.zone_history.items()
            },
            zone_sets=list(self.zone_sets),
            classifications=list(self.classifications),
            snapshots=list(self.snapshots),
        )


class _InvalidGroup(ValueError):
    pass


class _AmbiguousGroup(ValueError):
    pass


def make_premium_discount_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    active_range_lineage_id: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...] = (),
    source_swing_ids: tuple[str, ...] = (),
    protected_swing_id: str | None = None,
    construction_event_id: str | None = None,
    boundaries: SMCV2TickRange | None = None,
    equilibrium_tick: Decimal | None = None,
    creation_range_snapshot_id: str | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    current_range_snapshot_id: str | None = None,
    version: int | None = None,
    prior_zone_set_id: str | None = None,
    zone_set_id: str | None = None,
    observation_index: int | None = None,
    observation_timestamp: datetime | None = None,
    price_tick: int | None = None,
    zone: PremiumDiscountZone | None = None,
    classification_id: str | None = None,
) -> str:
    """Build one canonical kind-specific identity."""

    if not isinstance(identity_kind, str) or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked Premium/Discount identity kind")
    canonical_instrument = _normalize_text(instrument, name="instrument")
    canonical_timeframe = _normalize_text(timeframe, name="timeframe")
    _validate_hash(active_range_lineage_id, name="active_range_lineage_id")
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("direction must be BULLISH or BEARISH")
    _validate_source_indices(source_indices, allow_empty=True)
    _validate_hash_tuple(source_swing_ids, name="source_swing_ids", allow_empty=True)

    common: dict[str, object] = {
        "active_range_lineage_id": active_range_lineage_id,
        "detector_version": PREMIUM_DISCOUNT_DETECTOR_VERSION,
        "direction": direction.value,
        "identity_kind": identity_kind,
        "instrument": canonical_instrument,
        "timeframe": canonical_timeframe,
    }

    if identity_kind == "ZONE_SET":
        if len(source_indices) < 2:
            raise ValueError("ZONE_SET requires at least two source_indices")
        if len(source_indices) != len(source_swing_ids):
            raise ValueError("ZONE_SET source tuples must have equal length")
        if len(set(source_swing_ids)) != len(source_swing_ids):
            raise ValueError("ZONE_SET source_swing_ids must be unique")
        _validate_hash(protected_swing_id, name="protected_swing_id")
        _validate_hash(construction_event_id, name="construction_event_id")
        if source_swing_ids.count(protected_swing_id) != 1:
            raise ValueError("protected_swing_id must occur exactly once")
        low_tick, high_tick = _validate_boundaries(boundaries)
        equilibrium = _validate_equilibrium(
            equilibrium_tick,
            low_tick=low_tick,
            high_tick=high_tick,
        )
        _validate_hash(
            creation_range_snapshot_id,
            name="creation_range_snapshot_id",
        )
        _validate_non_negative_int(first_known_index, name="first_known_index")
        canonical_first_known = _normalize_timestamp(
            first_known_timestamp,
            name="first_known_timestamp",
        )
        _validate_positive_int(version, name="version")
        if version == 1:
            if prior_zone_set_id is not None:
                raise ValueError("ZONE_SET version 1 forbids prior_zone_set_id")
        else:
            _validate_hash(prior_zone_set_id, name="prior_zone_set_id")
        _require_defaults(
            current_range_snapshot_id=current_range_snapshot_id,
            zone_set_id=zone_set_id,
            observation_index=observation_index,
            observation_timestamp=observation_timestamp,
            price_tick=price_tick,
            zone=zone,
            classification_id=classification_id,
        )
        common.update(
            {
                "boundaries": [low_tick, high_tick],
                "construction_event_id": construction_event_id,
                "creation_range_snapshot_id": creation_range_snapshot_id,
                "equilibrium_tick": _decimal_text(equilibrium),
                "first_known_index": first_known_index,
                "first_known_timestamp": _timestamp_text(canonical_first_known),
                "prior_zone_set_id": prior_zone_set_id,
                "protected_swing_id": protected_swing_id,
                "source_indices": list(source_indices),
                "source_swing_ids": list(source_swing_ids),
                "version": version,
            }
        )
    elif identity_kind == "CLASSIFICATION":
        _require_defaults(
            source_indices=source_indices,
            source_swing_ids=source_swing_ids,
            protected_swing_id=protected_swing_id,
            construction_event_id=construction_event_id,
            creation_range_snapshot_id=creation_range_snapshot_id,
            first_known_index=first_known_index,
            first_known_timestamp=first_known_timestamp,
            prior_zone_set_id=prior_zone_set_id,
            classification_id=classification_id,
        )
        low_tick, high_tick = _validate_boundaries(boundaries)
        equilibrium = _validate_equilibrium(
            equilibrium_tick,
            low_tick=low_tick,
            high_tick=high_tick,
        )
        _validate_hash(
            current_range_snapshot_id,
            name="current_range_snapshot_id",
        )
        _validate_hash(zone_set_id, name="zone_set_id")
        _validate_positive_int(version, name="version")
        _validate_non_negative_int(observation_index, name="observation_index")
        canonical_observation = _normalize_timestamp(
            observation_timestamp,
            name="observation_timestamp",
        )
        _validate_tick(price_tick, name="price_tick")
        if not isinstance(zone, PremiumDiscountZone):
            raise TypeError("zone must be a PremiumDiscountZone")
        expected_zone = _zone_for_price(
            price_tick,
            low_tick=low_tick,
            high_tick=high_tick,
            equilibrium_tick=equilibrium,
        )
        if expected_zone is None:
            raise ValueError("CLASSIFICATION price is outside supplied boundaries")
        if zone is not expected_zone:
            raise ValueError("CLASSIFICATION zone contradicts supplied price")
        common.update(
            {
                "boundaries": [low_tick, high_tick],
                "current_range_snapshot_id": current_range_snapshot_id,
                "equilibrium_tick": _decimal_text(equilibrium),
                "observation_index": observation_index,
                "observation_timestamp": _timestamp_text(canonical_observation),
                "price_tick": price_tick,
                "version": version,
                "zone": zone.value,
                "zone_set_id": zone_set_id,
            }
        )
    else:
        _require_defaults(
            source_indices=source_indices,
            source_swing_ids=source_swing_ids,
            protected_swing_id=protected_swing_id,
            construction_event_id=construction_event_id,
            creation_range_snapshot_id=creation_range_snapshot_id,
            first_known_index=first_known_index,
            first_known_timestamp=first_known_timestamp,
            prior_zone_set_id=prior_zone_set_id,
        )
        low_tick, high_tick = _validate_boundaries(boundaries)
        equilibrium = _validate_equilibrium(
            equilibrium_tick,
            low_tick=low_tick,
            high_tick=high_tick,
        )
        _validate_hash(
            current_range_snapshot_id,
            name="current_range_snapshot_id",
        )
        _validate_hash(zone_set_id, name="zone_set_id")
        _validate_positive_int(version, name="version")
        _validate_non_negative_int(observation_index, name="observation_index")
        canonical_observation = _normalize_timestamp(
            observation_timestamp,
            name="observation_timestamp",
        )
        _validate_tick(price_tick, name="price_tick")
        if not isinstance(zone, PremiumDiscountZone):
            raise TypeError("zone must be a PremiumDiscountZone")
        _validate_hash(classification_id, name="classification_id")
        expected_classification_id = make_premium_discount_id(
            identity_kind="CLASSIFICATION",
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
            active_range_lineage_id=active_range_lineage_id,
            direction=direction,
            boundaries=SMCV2TickRange(low_tick, high_tick),
            equilibrium_tick=equilibrium,
            current_range_snapshot_id=current_range_snapshot_id,
            version=version,
            zone_set_id=zone_set_id,
            observation_index=observation_index,
            observation_timestamp=canonical_observation,
            price_tick=price_tick,
            zone=zone,
        )
        if classification_id != expected_classification_id:
            raise ValueError("SNAPSHOT classification_id is not canonical")
        common.update(
            {
                "boundaries": [low_tick, high_tick],
                "classification_id": classification_id,
                "current_range_snapshot_id": current_range_snapshot_id,
                "equilibrium_tick": _decimal_text(equilibrium),
                "observation_index": observation_index,
                "observation_timestamp": _timestamp_text(canonical_observation),
                "price_tick": price_tick,
                "version": version,
                "zone": zone.value,
                "zone_set_id": zone_set_id,
            }
        )

    canonical_json = json.dumps(
        common,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def analyze_premium_discount(
    *,
    instrument: str,
    timeframe: str,
    dealing_ranges: tuple[DealingRangeSnapshot, ...] | None,
    observations: tuple[PremiumDiscountObservation, ...] | None,
) -> PremiumDiscountResult:
    """Analyze immutable range and closed-price evidence without integration."""

    if dealing_ranges is None or observations is None:
        missing = []
        if dealing_ranges is None:
            missing.append("dealing_ranges")
        if observations is None:
            missing.append("observations")
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return PremiumDiscountResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    try:
        canonical_instrument = _normalize_text(instrument, name="instrument")
        canonical_timeframe = _normalize_text(timeframe, name="timeframe")
        range_records, range_issues = _collect_ranges(
            dealing_ranges,
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
        )
        observation_records, observation_issues = _collect_observations(observations)
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return _result_with_status(
            SMCV2PrimitiveStatus.INVALID,
            reason=f"Invalid Premium/Discount input: {exc}",
        )

    all_issues = (*range_issues, *observation_issues)
    if any(issue.moment is None for issue in all_issues):
        reason = next(
            issue.reason for issue in all_issues if issue.moment is None
        )
        return _result_with_status(
            SMCV2PrimitiveStatus.INVALID,
            reason=reason,
        )

    groups: dict[
        _Moment,
        dict[str, list[object]],
    ] = {}
    for record in range_records:
        groups.setdefault(
            record.moment,
            {"ranges": [], "observations": [], "issues": []},
        )["ranges"].append(record.value)
    for record in observation_records:
        groups.setdefault(
            record.moment,
            {"ranges": [], "observations": [], "issues": []},
        )["observations"].append(record.value)
    for issue in all_issues:
        assert issue.moment is not None
        groups.setdefault(
            issue.moment,
            {"ranges": [], "observations": [], "issues": []},
        )["issues"].append(issue)

    state = _AnalysisState(
        current_range=None,
        latest_by_lineage={},
        zone_history={},
        zone_sets=[],
        classifications=[],
        snapshots=[],
    )
    for moment in sorted(groups):
        group = groups[moment]
        issues = group["issues"]
        if issues:
            issue = issues[0]
            assert isinstance(issue, _Issue)
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.INVALID,
                reason=issue.reason,
            )
        candidate = state.clone()
        try:
            _apply_range_group(
                candidate,
                tuple(group["ranges"]),  # type: ignore[arg-type]
                instrument=canonical_instrument,
                timeframe=canonical_timeframe,
            )
            observations_in_group = tuple(group["observations"])
            if len(observations_in_group) > 1:
                raise _InvalidGroup("multiple observations share one effective moment")
            if observations_in_group:
                observation = observations_in_group[0]
                assert isinstance(observation, PremiumDiscountObservation)
                _classify_observation(
                    candidate,
                    observation,
                    instrument=canonical_instrument,
                    timeframe=canonical_timeframe,
                )
        except _InvalidGroup as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.INVALID,
                reason=str(exc),
            )
        except _AmbiguousGroup as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.AMBIGUOUS,
                reason=str(exc),
            )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return _state_result(
                state,
                status=SMCV2PrimitiveStatus.INVALID,
                reason=f"Invalid Premium/Discount group: {exc}",
            )
        state = candidate

    status = (
        SMCV2PrimitiveStatus.VALID
        if state.classifications
        else SMCV2PrimitiveStatus.NONE
    )
    reason = (
        "Premium/Discount classifications emitted"
        if status is SMCV2PrimitiveStatus.VALID
        else "No observation was classifiable inside an active external range"
    )
    return _state_result(state, status=status, reason=reason, blocking=False)


def _normalize_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _normalize_timestamp(value: object, *, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    try:
        return normalize_utc_timestamp(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} is not a valid timezone-aware timestamp") from exc


def _timestamp_text(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_hash(value: object, *, name: str) -> None:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 identity")


def _validate_optional_hash(value: object, *, name: str) -> None:
    if value is not None:
        _validate_hash(value, name=name)


def _validate_hash_tuple(
    values: object,
    *,
    name: str,
    allow_empty: bool,
) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    if not allow_empty and not values:
        raise ValueError(f"{name} cannot be empty")
    for value in values:
        _validate_hash(value, name=f"{name} member")


def _validate_source_indices(values: object, *, allow_empty: bool) -> None:
    if not isinstance(values, tuple):
        raise TypeError("source_indices must be a tuple")
    if not allow_empty and not values:
        raise ValueError("source_indices cannot be empty")
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("source_indices must contain non-negative integers")
    if any(left >= right for left, right in zip(values, values[1:])):
        raise ValueError("source_indices must be strictly increasing")


def _validate_non_negative_int(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _validate_positive_int(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _validate_tick(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer tick")


def _validate_boundaries(value: object) -> tuple[int, int]:
    if not isinstance(value, SMCV2TickRange):
        raise TypeError("boundaries must be an SMCV2TickRange")
    try:
        low_tick = value.lower_tick
        high_tick = value.upper_tick
    except AttributeError as exc:
        raise TypeError("boundaries is internally malformed") from exc
    _validate_tick(low_tick, name="boundaries.lower_tick")
    _validate_tick(high_tick, name="boundaries.upper_tick")
    if low_tick >= high_tick:
        raise ValueError("boundaries must have positive width")
    return low_tick, high_tick


def _validate_equilibrium(
    value: object,
    *,
    low_tick: int,
    high_tick: int,
) -> Decimal:
    if not isinstance(value, Decimal):
        raise TypeError("equilibrium_tick must be a Decimal")
    if not value.is_finite():
        raise ValueError("equilibrium_tick must be finite")
    expected = _exact_midpoint(low_tick, high_tick)
    if value != expected:
        raise ValueError("equilibrium_tick does not match exact range midpoint")
    return value


def _exact_midpoint(low_tick: int, high_tick: int) -> Decimal:
    total = low_tick + high_tick
    if total % 2 == 0:
        return Decimal(total // 2)
    sign = "-" if total < 0 else ""
    absolute = abs(total)
    return Decimal(f"{sign}{absolute // 2}.5")


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if "." in text else f"{text}.0"


def _require_defaults(**values: object) -> None:
    for name, value in values.items():
        expected = () if name in {"source_indices", "source_swing_ids"} else None
        if value != expected:
            raise ValueError(f"{name} is forbidden for this identity kind")


def _zone_for_price(
    price_tick: int,
    *,
    low_tick: int,
    high_tick: int,
    equilibrium_tick: Decimal,
) -> PremiumDiscountZone | None:
    if price_tick < low_tick or price_tick > high_tick:
        return None
    price = Decimal(price_tick)
    if price < equilibrium_tick:
        return PremiumDiscountZone.DISCOUNT
    if price == equilibrium_tick:
        return PremiumDiscountZone.EQUILIBRIUM
    return PremiumDiscountZone.PREMIUM


def _validate_provenance(value: object, *, name: str) -> _Moment:
    if not isinstance(value, SMCV2EventProvenance):
        raise TypeError(f"{name} must be an SMCV2EventProvenance")
    try:
        source_indices = value.source_indices
        source_timestamps = value.source_timestamps
        confirmation_index = value.confirmation_index
        confirmation_timestamp = value.confirmation_timestamp
    except AttributeError as exc:
        raise TypeError(f"{name} is internally malformed") from exc
    _validate_source_indices(source_indices, allow_empty=False)
    if not isinstance(source_timestamps, tuple):
        raise TypeError(f"{name}.source_timestamps must be a tuple")
    if len(source_timestamps) != len(source_indices):
        raise ValueError(f"{name} source tuples must have equal length")
    normalized_sources = tuple(
        _normalize_timestamp(item, name=f"{name}.source_timestamp")
        for item in source_timestamps
    )
    if any(left >= right for left, right in zip(normalized_sources, normalized_sources[1:])):
        raise ValueError(f"{name}.source_timestamps must be strictly increasing")
    _validate_non_negative_int(confirmation_index, name=f"{name}.confirmation_index")
    normalized_confirmation = _normalize_timestamp(
        confirmation_timestamp,
        name=f"{name}.confirmation_timestamp",
    )
    if confirmation_index < source_indices[-1]:
        raise ValueError(f"{name} confirmation index precedes source evidence")
    if normalized_confirmation < normalized_sources[-1]:
        raise ValueError(f"{name} confirmation timestamp precedes source evidence")
    return confirmation_index, normalized_confirmation


def _safe_provenance_moment(value: object) -> _Moment | None:
    try:
        return _validate_provenance(value, name="first_known_provenance")
    except (TypeError, ValueError, AttributeError):
        return None


def _safe_observation_moment(value: object) -> _Moment | None:
    try:
        index = getattr(value, "index")
        timestamp = getattr(value, "timestamp")
        _validate_non_negative_int(index, name="observation.index")
        return index, _normalize_timestamp(timestamp, name="observation.timestamp")
    except (TypeError, ValueError, AttributeError):
        return None


def _safe_range_moment(value: object) -> _Moment | None:
    try:
        if not isinstance(value, DealingRangeSnapshot):
            return None
        kind = getattr(value, "kind")
        state = getattr(value, "state")
        if (
            kind is DealingRangeKind.EXTERNAL
            and state in (DealingRangeState.SUPERSEDED, DealingRangeState.INVALIDATED)
        ):
            transitions = getattr(value, "transitions")
            if not isinstance(transitions, tuple) or not transitions:
                return None
            last = transitions[-1]
            index = getattr(last, "index")
            timestamp = getattr(last, "timestamp")
            _validate_non_negative_int(index, name="transition.index")
            return index, _normalize_timestamp(timestamp, name="transition.timestamp")
        return _safe_provenance_moment(getattr(value, "first_known_provenance"))
    except (TypeError, ValueError, AttributeError, IndexError):
        return None


def _validate_transition(
    value: object,
    *,
    snapshot: DealingRangeSnapshot,
    instrument: str,
    timeframe: str,
) -> _Moment:
    if not isinstance(value, DealingRangeTransition):
        raise TypeError("range transition must be a DealingRangeTransition")
    try:
        transition_id = value.transition_id
        lineage_id = value.lineage_id
        from_state = value.from_state
        to_state = value.to_state
        index = value.index
        timestamp = value.timestamp
        reason = value.reason
        related_event_id = value.related_event_id
        replacement_lineage_id = value.replacement_lineage_id
    except AttributeError as exc:
        raise TypeError("range transition is internally malformed") from exc
    _validate_hash(transition_id, name="transition_id")
    _validate_hash(lineage_id, name="transition.lineage_id")
    if lineage_id != snapshot.lineage_id:
        raise ValueError("transition lineage does not match snapshot")
    if from_state is not None and not isinstance(from_state, DealingRangeState):
        raise TypeError("transition.from_state is invalid")
    if not isinstance(to_state, DealingRangeState):
        raise TypeError("transition.to_state is invalid")
    _validate_non_negative_int(index, name="transition.index")
    canonical_timestamp = _normalize_timestamp(timestamp, name="transition.timestamp")
    if not isinstance(reason, str):
        raise TypeError("transition.reason must be a string")
    _validate_optional_hash(related_event_id, name="transition.related_event_id")
    _validate_optional_hash(
        replacement_lineage_id,
        name="transition.replacement_lineage_id",
    )
    expected_id = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=instrument,
        timeframe=timeframe,
        direction=snapshot.direction,
        source_indices=(index,),
        lineage_id=lineage_id,
        transition_from_state=from_state,
        transition_to_state=to_state,
        transition_index=index,
        transition_timestamp=canonical_timestamp,
        transition_reason=reason,
        related_event_id=related_event_id,
        replacement_lineage_id=replacement_lineage_id,
    )
    if transition_id != expected_id:
        raise ValueError("transition_id does not match canonical identity")
    return index, canonical_timestamp


def _validate_range(
    value: object,
    *,
    instrument: str,
    timeframe: str,
) -> _RangeRecord:
    if not isinstance(value, DealingRangeSnapshot):
        raise TypeError("range item must be a DealingRangeSnapshot")
    try:
        kind = value.kind
        direction = value.direction
        snapshot_id = value.snapshot_id
        source_swing_ids = value.source_swing_ids
        source_indices = value.source_indices
        low_tick = value.low_tick
        high_tick = value.high_tick
        midpoint_tick = value.midpoint_tick
        first_known_provenance = value.first_known_provenance
        lineage_id = value.lineage_id
        protected_swing_id = value.protected_swing_id
        construction_event_id = value.construction_event_id
        state = value.state
        transitions = value.transitions
        transition_ids = value.transition_ids
        replacement_lineage_id = value.replacement_lineage_id
    except AttributeError as exc:
        raise TypeError("range snapshot is internally malformed") from exc

    if not isinstance(kind, DealingRangeKind):
        raise TypeError("range kind is invalid")
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("range direction must be BULLISH or BEARISH")
    _validate_hash(snapshot_id, name="range.snapshot_id")
    _validate_source_indices(source_indices, allow_empty=False)
    _validate_hash_tuple(
        source_swing_ids,
        name="range.source_swing_ids",
        allow_empty=False,
    )
    if len(source_indices) != len(source_swing_ids):
        raise ValueError("range source tuples must have equal length")
    if len(set(source_swing_ids)) != len(source_swing_ids):
        raise ValueError("range source_swing_ids must be unique")
    _validate_tick(low_tick, name="range.low_tick")
    _validate_tick(high_tick, name="range.high_tick")
    if low_tick >= high_tick:
        raise ValueError("range boundaries must have positive width")
    equilibrium = _validate_equilibrium(
        midpoint_tick,
        low_tick=low_tick,
        high_tick=high_tick,
    )
    first_known = _validate_provenance(
        first_known_provenance,
        name="range.first_known_provenance",
    )
    boundaries = SMCV2TickRange(low_tick, high_tick)

    if kind is DealingRangeKind.INTERNAL:
        if len(source_indices) != 2:
            raise ValueError("internal range requires exactly two sources")
        if any(
            item is not None
            for item in (
                lineage_id,
                protected_swing_id,
                construction_event_id,
                state,
                replacement_lineage_id,
            )
        ):
            raise ValueError("internal range contains external-only context")
        if transitions != () or transition_ids != ():
            raise ValueError("internal range cannot contain transitions")
        expected_snapshot_id = make_dealing_range_id(
            identity_kind="INTERNAL_RANGE",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_indices=source_indices,
            swing_ids=source_swing_ids,
            boundaries=boundaries,
            range_kind=kind,
        )
        if snapshot_id != expected_snapshot_id:
            raise ValueError("internal range snapshot_id is not canonical")
        return _RangeRecord(value=value, moment=first_known)

    if len(source_indices) < 2:
        raise ValueError("external range requires at least two sources")
    _validate_hash(lineage_id, name="range.lineage_id")
    _validate_hash(protected_swing_id, name="range.protected_swing_id")
    _validate_hash(construction_event_id, name="range.construction_event_id")
    if source_swing_ids.count(protected_swing_id) != 1:
        raise ValueError("protected_swing_id must occur exactly once")
    if not isinstance(state, DealingRangeState):
        raise TypeError("external range state is invalid")
    if not isinstance(transitions, tuple) or not transitions:
        raise ValueError("external range requires transition history")
    if not isinstance(transition_ids, tuple):
        raise TypeError("range.transition_ids must be a tuple")
    _validate_hash_tuple(
        transition_ids,
        name="range.transition_ids",
        allow_empty=False,
    )
    if tuple(item.transition_id for item in transitions) != transition_ids:
        raise ValueError("range transition_ids do not match transition history")

    transition_moments: list[_Moment] = []
    previous_state: DealingRangeState | None = None
    for position, transition in enumerate(transitions):
        moment = _validate_transition(
            transition,
            snapshot=value,
            instrument=instrument,
            timeframe=timeframe,
        )
        if transition.from_state is not previous_state:
            raise ValueError("range transition state chain is broken")
        if position == 0:
            if (
                transition.from_state is not None
                or transition.to_state is not DealingRangeState.ACTIVE
                or transition.reason != _CONSTRUCTION_REASON
                or transition.related_event_id != construction_event_id
                or moment != first_known
            ):
                raise ValueError("range construction transition is not canonical")
        else:
            if moment <= transition_moments[-1]:
                raise ValueError("range transitions must be strictly chronological")
            if transition.reason not in _TERMINAL_REASONS:
                raise ValueError("range transition reason is not locked")
        previous_state = transition.to_state
        transition_moments.append(moment)
    if previous_state is not state:
        raise ValueError("range final transition state does not match snapshot")
    if state is DealingRangeState.ACTIVE and len(transitions) != 1:
        raise ValueError("active range cannot contain a later terminal transition")
    if replacement_lineage_id != transitions[-1].replacement_lineage_id:
        raise ValueError(
            "range replacement_lineage_id does not match final transition"
        )

    _validate_optional_hash(
        replacement_lineage_id,
        name="range.replacement_lineage_id",
    )
    expected_snapshot_id = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_indices=source_indices,
        swing_ids=source_swing_ids,
        boundaries=boundaries,
        lineage_id=lineage_id,
        construction_event_id=construction_event_id,
        range_kind=kind,
        state=state,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )
    if snapshot_id != expected_snapshot_id:
        raise ValueError("external range snapshot_id is not canonical")
    effective = (
        transition_moments[-1]
        if state in (DealingRangeState.SUPERSEDED, DealingRangeState.INVALIDATED)
        else first_known
    )
    return _RangeRecord(value=value, moment=effective)


def _collect_ranges(
    values: object,
    *,
    instrument: str,
    timeframe: str,
) -> tuple[tuple[_RangeRecord, ...], tuple[_Issue, ...]]:
    if not isinstance(values, tuple):
        raise TypeError("dealing_ranges must be a tuple")
    records: list[_RangeRecord] = []
    issues: list[_Issue] = []
    previous_moment: _Moment | None = None
    seen_snapshot_ids: set[str] = set()
    active_seen_at_moment: dict[_Moment, bool] = {}
    for value in values:
        safe_moment = _safe_range_moment(value)
        try:
            record = _validate_range(
                value,
                instrument=instrument,
                timeframe=timeframe,
            )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            issues.append(_Issue(safe_moment, f"Invalid range snapshot: {exc}"))
            if safe_moment is not None:
                previous_moment = safe_moment
            continue
        if record.value.snapshot_id in seen_snapshot_ids:
            issues.append(_Issue(record.moment, "Duplicate range snapshot identity"))
        seen_snapshot_ids.add(record.value.snapshot_id)
        if previous_moment is not None and record.moment < previous_moment:
            issues.append(_Issue(record.moment, "Range tuple is causally out of order"))
        if (
            record.value.kind is DealingRangeKind.EXTERNAL
            and record.value.state in (
                DealingRangeState.SUPERSEDED,
                DealingRangeState.INVALIDATED,
            )
            and active_seen_at_moment.get(record.moment, False)
        ):
            issues.append(
                _Issue(
                    record.moment,
                    "Terminal range must precede ACTIVE range at one effective moment",
                )
            )
        if (
            record.value.kind is DealingRangeKind.EXTERNAL
            and record.value.state is DealingRangeState.ACTIVE
        ):
            active_seen_at_moment[record.moment] = True
        previous_moment = record.moment
        records.append(record)
    return tuple(records), tuple(issues)


def _validate_observation(value: object) -> _ObservationRecord:
    if not isinstance(value, PremiumDiscountObservation):
        raise TypeError("observation must be a PremiumDiscountObservation")
    try:
        index = value.index
        timestamp = value.timestamp
        price_tick = value.price_tick
    except AttributeError as exc:
        raise TypeError("observation is internally malformed") from exc
    _validate_non_negative_int(index, name="observation.index")
    canonical_timestamp = _normalize_timestamp(
        timestamp,
        name="observation.timestamp",
    )
    _validate_tick(price_tick, name="observation.price_tick")
    return _ObservationRecord(
        value=value,
        moment=(index, canonical_timestamp),
    )


def _collect_observations(
    values: object,
) -> tuple[tuple[_ObservationRecord, ...], tuple[_Issue, ...]]:
    if not isinstance(values, tuple):
        raise TypeError("observations must be a tuple")
    records: list[_ObservationRecord] = []
    issues: list[_Issue] = []
    previous_index: int | None = None
    previous_timestamp: datetime | None = None
    seen_indices: set[int] = set()
    seen_timestamps: set[datetime] = set()
    for value in values:
        safe_moment = _safe_observation_moment(value)
        try:
            record = _validate_observation(value)
        except (TypeError, ValueError, AttributeError) as exc:
            issues.append(_Issue(safe_moment, f"Invalid observation: {exc}"))
            continue
        index, timestamp = record.moment
        if index in seen_indices:
            issues.append(_Issue(record.moment, "Duplicate observation index"))
        if timestamp in seen_timestamps:
            issues.append(_Issue(record.moment, "Duplicate observation timestamp"))
        if previous_index is not None and index <= previous_index:
            issues.append(
                _Issue(record.moment, "Observation indices are not strictly increasing")
            )
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            issues.append(
                _Issue(
                    record.moment,
                    "Observation timestamps are not strictly increasing",
                )
            )
        seen_indices.add(index)
        seen_timestamps.add(timestamp)
        previous_index = index
        previous_timestamp = timestamp
        records.append(record)
    return tuple(records), tuple(issues)


def _same_material(
    left: DealingRangeSnapshot,
    right: DealingRangeSnapshot,
) -> bool:
    return (
        left.direction,
        left.source_swing_ids,
        left.source_indices,
        left.protected_swing_id,
        left.construction_event_id,
        left.low_tick,
        left.high_tick,
        left.midpoint_tick,
    ) == (
        right.direction,
        right.source_swing_ids,
        right.source_indices,
        right.protected_swing_id,
        right.construction_event_id,
        right.low_tick,
        right.high_tick,
        right.midpoint_tick,
    )


def _validate_revision(
    prior: DealingRangeSnapshot,
    current: DealingRangeSnapshot,
) -> None:
    if prior.state is not DealingRangeState.ACTIVE:
        raise _InvalidGroup("An inactive lineage cannot receive an ACTIVE revision")
    if current.first_known_provenance != prior.first_known_provenance:
        raise _InvalidGroup("Same-lineage revision changed first-known provenance")
    if current.direction is not prior.direction:
        raise _InvalidGroup("Same-lineage revision changed direction")
    if current.protected_swing_id != prior.protected_swing_id:
        raise _InvalidGroup("Same-lineage revision changed protected swing")
    if current.construction_event_id != prior.construction_event_id:
        raise _InvalidGroup("Same-lineage revision changed construction event")
    if current.transitions != prior.transitions:
        raise _InvalidGroup("ACTIVE revision changed immutable transition history")
    if (
        current.source_indices[: len(prior.source_indices)] != prior.source_indices
        or current.source_swing_ids[: len(prior.source_swing_ids)]
        != prior.source_swing_ids
    ):
        raise _InvalidGroup("Same-lineage revision is not a causal source prefix extension")


def _validate_terminal(
    prior: DealingRangeSnapshot,
    terminal: DealingRangeSnapshot,
) -> None:
    if prior.state is not DealingRangeState.ACTIVE:
        raise _InvalidGroup("Terminal range has no prior ACTIVE lineage")
    if (
        terminal.direction is not prior.direction
        or terminal.source_swing_ids != prior.source_swing_ids
        or terminal.source_indices != prior.source_indices
        or terminal.low_tick != prior.low_tick
        or terminal.high_tick != prior.high_tick
        or terminal.midpoint_tick != prior.midpoint_tick
        or terminal.first_known_provenance != prior.first_known_provenance
        or terminal.protected_swing_id != prior.protected_swing_id
        or terminal.construction_event_id != prior.construction_event_id
    ):
        raise _InvalidGroup("Terminal range changed immutable active evidence")
    if terminal.transitions[:-1] != prior.transitions:
        raise _InvalidGroup("Terminal range history is not an exact prior prefix")


def _apply_range_group(
    state: _AnalysisState,
    ranges: tuple[DealingRangeSnapshot, ...],
    *,
    instrument: str,
    timeframe: str,
) -> None:
    terminals = tuple(
        item
        for item in ranges
        if item.kind is DealingRangeKind.EXTERNAL
        and item.state in (
            DealingRangeState.SUPERSEDED,
            DealingRangeState.INVALIDATED,
        )
    )
    actives = tuple(
        item
        for item in ranges
        if item.kind is DealingRangeKind.EXTERNAL
        and item.state is DealingRangeState.ACTIVE
    )

    terminal_by_lineage: dict[str, DealingRangeSnapshot] = {}
    for terminal in terminals:
        lineage_id = terminal.lineage_id
        assert lineage_id is not None
        prior = state.latest_by_lineage.get(lineage_id)
        if prior is not None:
            _validate_terminal(prior, terminal)
        if lineage_id in terminal_by_lineage:
            raise _InvalidGroup("One lineage has duplicate terminal snapshots in a group")
        terminal_by_lineage[lineage_id] = terminal
        state.latest_by_lineage[lineage_id] = terminal
        if (
            state.current_range is not None
            and state.current_range.lineage_id == lineage_id
        ):
            state.current_range = None

    new_lineages: list[str] = []
    for active in actives:
        lineage_id = active.lineage_id
        assert lineage_id is not None
        prior = state.latest_by_lineage.get(lineage_id)
        if prior is not None:
            _validate_revision(prior, active)
        else:
            new_lineages.append(lineage_id)
        if state.current_range is not None:
            if state.current_range.lineage_id != lineage_id:
                raise _AmbiguousGroup(
                    "Multiple unrelated active external ranges share one effective moment"
                )
            _validate_revision(state.current_range, active)
        state.latest_by_lineage[lineage_id] = active
        state.current_range = active
        _resolve_zone_set(
            state,
            active,
            instrument=instrument,
            timeframe=timeframe,
        )

    if len(set(new_lineages)) > 1:
        raise _AmbiguousGroup(
            "Multiple unrelated active external ranges share one effective moment"
        )
    if terminals and actives:
        for terminal in terminals:
            if terminal.state is DealingRangeState.SUPERSEDED:
                replacement_ids = {
                    item.lineage_id for item in actives if item.lineage_id is not None
                }
                if terminal.replacement_lineage_id not in replacement_ids:
                    raise _InvalidGroup(
                        "SUPERSEDED range does not identify its replacement lineage"
                    )


def _zone_material(value: DealingRangeSnapshot) -> tuple[object, ...]:
    return (
        value.direction,
        value.source_swing_ids,
        value.source_indices,
        value.protected_swing_id,
        value.construction_event_id,
        value.low_tick,
        value.high_tick,
        value.midpoint_tick,
    )


def _resolve_zone_set(
    state: _AnalysisState,
    active: DealingRangeSnapshot,
    *,
    instrument: str,
    timeframe: str,
) -> PremiumDiscountZoneSet:
    lineage_id = active.lineage_id
    protected_swing_id = active.protected_swing_id
    construction_event_id = active.construction_event_id
    assert lineage_id is not None
    assert protected_swing_id is not None
    assert construction_event_id is not None
    history = state.zone_history.setdefault(lineage_id, [])
    if history:
        prior = history[-1]
        prior_material = (
            prior.direction,
            prior.source_swing_ids,
            prior.source_indices,
            prior.protected_swing_id,
            prior.construction_event_id,
            prior.low_tick,
            prior.high_tick,
            prior.equilibrium_tick,
        )
        if prior_material == _zone_material(active):
            return prior
        version = prior.version + 1
        prior_zone_set_id = prior.zone_set_id
    else:
        version = 1
        prior_zone_set_id = None
    first_known_index, first_known_timestamp = _validate_provenance(
        active.first_known_provenance,
        name="range.first_known_provenance",
    )
    boundaries = SMCV2TickRange(active.low_tick, active.high_tick)
    zone_set_id = make_premium_discount_id(
        identity_kind="ZONE_SET",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=lineage_id,
        direction=active.direction,
        source_indices=active.source_indices,
        source_swing_ids=active.source_swing_ids,
        protected_swing_id=protected_swing_id,
        construction_event_id=construction_event_id,
        boundaries=boundaries,
        equilibrium_tick=active.midpoint_tick,
        creation_range_snapshot_id=active.snapshot_id,
        first_known_index=first_known_index,
        first_known_timestamp=first_known_timestamp,
        version=version,
        prior_zone_set_id=prior_zone_set_id,
    )
    zone_set = PremiumDiscountZoneSet(
        zone_set_id=zone_set_id,
        active_range_lineage_id=lineage_id,
        creation_range_snapshot_id=active.snapshot_id,
        direction=active.direction,
        source_swing_ids=active.source_swing_ids,
        source_indices=active.source_indices,
        protected_swing_id=protected_swing_id,
        construction_event_id=construction_event_id,
        low_tick=active.low_tick,
        high_tick=active.high_tick,
        equilibrium_tick=active.midpoint_tick,
        version=version,
        first_known_index=first_known_index,
        first_known_timestamp=first_known_timestamp,
        prior_zone_set_id=prior_zone_set_id,
    )
    history.append(zone_set)
    state.zone_sets.append(zone_set)
    return zone_set


def _classify_observation(
    state: _AnalysisState,
    observation: PremiumDiscountObservation,
    *,
    instrument: str,
    timeframe: str,
) -> None:
    active = state.current_range
    if active is None:
        return
    lineage_id = active.lineage_id
    assert lineage_id is not None
    history = state.zone_history.get(lineage_id)
    if not history:
        raise _InvalidGroup("Active range has no resolved zone-set history")
    zone_set = history[-1]
    zone = _zone_for_price(
        observation.price_tick,
        low_tick=zone_set.low_tick,
        high_tick=zone_set.high_tick,
        equilibrium_tick=zone_set.equilibrium_tick,
    )
    if zone is None:
        return
    canonical_timestamp = _normalize_timestamp(
        observation.timestamp,
        name="observation.timestamp",
    )
    boundaries = SMCV2TickRange(zone_set.low_tick, zone_set.high_tick)
    classification_id = make_premium_discount_id(
        identity_kind="CLASSIFICATION",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=lineage_id,
        direction=active.direction,
        boundaries=boundaries,
        equilibrium_tick=zone_set.equilibrium_tick,
        current_range_snapshot_id=active.snapshot_id,
        version=zone_set.version,
        zone_set_id=zone_set.zone_set_id,
        observation_index=observation.index,
        observation_timestamp=canonical_timestamp,
        price_tick=observation.price_tick,
        zone=zone,
    )
    classification = PremiumDiscountClassification(
        classification_id=classification_id,
        zone_set_id=zone_set.zone_set_id,
        active_range_lineage_id=lineage_id,
        active_range_snapshot_id=active.snapshot_id,
        direction=active.direction,
        zone_set_version=zone_set.version,
        observation_index=observation.index,
        observation_timestamp=canonical_timestamp,
        price_tick=observation.price_tick,
        zone=zone,
    )
    snapshot_id = make_premium_discount_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=lineage_id,
        direction=active.direction,
        boundaries=boundaries,
        equilibrium_tick=zone_set.equilibrium_tick,
        current_range_snapshot_id=active.snapshot_id,
        version=zone_set.version,
        zone_set_id=zone_set.zone_set_id,
        observation_index=observation.index,
        observation_timestamp=canonical_timestamp,
        price_tick=observation.price_tick,
        zone=zone,
        classification_id=classification_id,
    )
    snapshot = PremiumDiscountSnapshot(
        snapshot_id=snapshot_id,
        active_range_lineage_id=lineage_id,
        active_range_snapshot_id=active.snapshot_id,
        zone_set_id=zone_set.zone_set_id,
        zone_set_version=zone_set.version,
        index=observation.index,
        timestamp=canonical_timestamp,
        classification=classification,
        classification_id=classification_id,
    )
    state.classifications.append(classification)
    state.snapshots.append(snapshot)


def _result_with_status(
    status: SMCV2PrimitiveStatus,
    *,
    reason: str,
) -> PremiumDiscountResult:
    return PremiumDiscountResult(
        status=status,
        reasons=(reason,),
        blocking_reasons=(reason,),
    )


def _state_result(
    state: _AnalysisState,
    *,
    status: SMCV2PrimitiveStatus,
    reason: str,
    blocking: bool = True,
) -> PremiumDiscountResult:
    return PremiumDiscountResult(
        status=status,
        zone_sets=tuple(state.zone_sets),
        classifications=tuple(state.classifications),
        snapshots=tuple(state.snapshots),
        reasons=(reason,),
        blocking_reasons=(reason,) if blocking else (),
    )


__all__ = [
    "PREMIUM_DISCOUNT_DETECTOR_VERSION",
    "PremiumDiscountZone",
    "PremiumDiscountObservation",
    "PremiumDiscountZoneSet",
    "PremiumDiscountClassification",
    "PremiumDiscountSnapshot",
    "PremiumDiscountResult",
    "make_premium_discount_id",
    "analyze_premium_discount",
]
