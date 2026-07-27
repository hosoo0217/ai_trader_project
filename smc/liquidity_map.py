"""Deterministic standalone Internal and External Liquidity Map diagnostics.

The analyzer consumes immutable outputs from the completed Equal Liquidity and
Dealing Range diagnostics. It performs no raw detection, I/O, configuration,
runtime registration, strategy, risk, or execution work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from enum import Enum
import hashlib
import json
import re

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
    EqualLiquidityPool,
    EqualLiquiditySide,
    make_equal_liquidity_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2LifecycleEvent,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
    validate_lifecycle_history,
)


LIQUIDITY_MAP_DETECTOR_VERSION = "SMC-V2-LIQUIDITY-MAP-1"

_IDENTITY_KINDS = frozenset(
    {"MAP", "BOUNDARY", "CLASSIFICATION", "SNAPSHOT", "RECLASSIFICATION"}
)
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_RECLASSIFICATION_REASONS = frozenset(
    {
        "INTERNAL_TO_EXTERNAL_RANGE_DEFINING",
        "EXTERNAL_TO_INTERNAL_SUBORDINATE",
    }
)
_RANGE_TRANSITION_REASONS = frozenset(
    {
        "CONSTRUCTION_ACTIVE",
        "OBSERVATION_CLOSE_THROUGH_INVALIDATION",
        "CHOCH_CLOSE_THROUGH_INVALIDATION",
        "BOS_PULLBACK_REPLACEMENT",
    }
)

_Moment = tuple[int, datetime]
_SourceKey = tuple["LiquiditySourceKind", str]


class LiquiditySide(str, Enum):
    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"


class LiquidityScope(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class LiquiditySourceKind(str, Enum):
    SWING = "SWING"
    EQUAL_LIQUIDITY_POOL = "EQUAL_LIQUIDITY_POOL"
    RANGE_BOUNDARY = "RANGE_BOUNDARY"


@dataclass(frozen=True)
class LiquidityClassification:
    classification_id: str
    source_kind: LiquiditySourceKind
    source_id: str
    side: LiquiditySide
    scope: LiquidityScope
    source_indices: tuple[int, ...]
    boundaries: SMCV2TickRange
    active_range_lineage_id: str
    active_range_snapshot_id: str
    version: int
    classification_index: int
    classification_timestamp: datetime
    prior_classification_id: str | None


@dataclass(frozen=True)
class LiquidityReclassification:
    reclassification_id: str
    source_kind: LiquiditySourceKind
    source_id: str
    side: LiquiditySide
    from_scope: LiquidityScope
    to_scope: LiquidityScope
    prior_classification_id: str
    new_classification_id: str
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class LiquidityMapSnapshot:
    map_id: str
    snapshot_id: str
    active_range_lineage_id: str
    active_range_snapshot_id: str
    index: int
    timestamp: datetime
    classifications: tuple[LiquidityClassification, ...]
    classification_ids: tuple[str, ...]
    reclassifications: tuple[LiquidityReclassification, ...]
    reclassification_ids: tuple[str, ...]


@dataclass(frozen=True)
class LiquidityMapResult:
    status: SMCV2PrimitiveStatus
    snapshots: tuple[LiquidityMapSnapshot, ...] = ()
    reclassifications: tuple[LiquidityReclassification, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Issue:
    moment: _Moment | None
    reason: str


@dataclass(frozen=True)
class _ClassificationSpec:
    source_kind: LiquiditySourceKind
    source_id: str
    side: LiquiditySide
    scope: LiquidityScope
    source_indices: tuple[int, ...]
    boundaries: SMCV2TickRange
    active_range_lineage_id: str

    @property
    def key(self) -> _SourceKey:
        return self.source_kind, self.source_id

    @property
    def material(self) -> tuple[object, ...]:
        return (
            self.source_kind,
            self.source_id,
            self.side,
            self.scope,
            self.source_indices,
            self.boundaries.lower_tick,
            self.boundaries.upper_tick,
            self.active_range_lineage_id,
        )


class _InvalidGroup(ValueError):
    pass


class _AmbiguousGroup(ValueError):
    pass


def make_liquidity_map_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    active_range_lineage_id: str,
    source_indices: tuple[int, ...] = (),
    source_kind: LiquiditySourceKind | None = None,
    source_id: str | None = None,
    side: LiquiditySide | None = None,
    scope: LiquidityScope | None = None,
    boundaries: SMCV2TickRange | None = None,
    active_range_snapshot_id: str | None = None,
    version: int | None = None,
    prior_classification_id: str | None = None,
    new_classification_id: str | None = None,
    classification_ids: tuple[str, ...] = (),
    reclassification_ids: tuple[str, ...] = (),
    event_index: int | None = None,
    event_timestamp: datetime | None = None,
    from_scope: LiquidityScope | None = None,
    to_scope: LiquidityScope | None = None,
    reason: str | None = None,
) -> str:
    """Return one kind-specific canonical SHA-256 identity."""

    if not isinstance(identity_kind, str) or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked Liquidity Map identity kind")
    canonical_instrument = _normalize_text(instrument, name="instrument").upper()
    canonical_timeframe = _normalize_text(timeframe, name="timeframe").upper()
    _validate_hash(active_range_lineage_id, name="active_range_lineage_id")
    _validate_optional_hash(source_id, name="source_id")
    _validate_optional_hash(active_range_snapshot_id, name="active_range_snapshot_id")
    _validate_optional_hash(prior_classification_id, name="prior_classification_id")
    _validate_optional_hash(new_classification_id, name="new_classification_id")
    _validate_hash_tuple(classification_ids, name="classification_ids")
    _validate_hash_tuple(reclassification_ids, name="reclassification_ids")

    payload: dict[str, object] = {
        "active_range_lineage_id": active_range_lineage_id,
        "detector_version": LIQUIDITY_MAP_DETECTOR_VERSION,
        "identity_kind": identity_kind,
        "instrument": canonical_instrument,
        "timeframe": canonical_timeframe,
    }

    if identity_kind == "MAP":
        _require_defaults(
            source_indices=source_indices,
            source_kind=source_kind,
            source_id=source_id,
            side=side,
            scope=scope,
            boundaries=boundaries,
            active_range_snapshot_id=active_range_snapshot_id,
            version=version,
            prior_classification_id=prior_classification_id,
            new_classification_id=new_classification_id,
            classification_ids=classification_ids,
            reclassification_ids=reclassification_ids,
            event_index=event_index,
            event_timestamp=event_timestamp,
            from_scope=from_scope,
            to_scope=to_scope,
            reason=reason,
        )
    elif identity_kind == "BOUNDARY":
        if source_kind is not LiquiditySourceKind.RANGE_BOUNDARY:
            raise ValueError("BOUNDARY requires source_kind=RANGE_BOUNDARY")
        if not isinstance(side, LiquiditySide):
            raise TypeError("BOUNDARY requires one LiquiditySide")
        _require_defaults(
            source_indices=source_indices,
            source_id=source_id,
            scope=scope,
            boundaries=boundaries,
            active_range_snapshot_id=active_range_snapshot_id,
            version=version,
            prior_classification_id=prior_classification_id,
            new_classification_id=new_classification_id,
            classification_ids=classification_ids,
            reclassification_ids=reclassification_ids,
            event_index=event_index,
            event_timestamp=event_timestamp,
            from_scope=from_scope,
            to_scope=to_scope,
            reason=reason,
        )
        payload.update({"side": side.value, "source_kind": source_kind.value})
    elif identity_kind == "CLASSIFICATION":
        _validate_source_indices(source_indices)
        if not isinstance(source_kind, LiquiditySourceKind):
            raise TypeError("CLASSIFICATION requires source_kind")
        _validate_hash(source_id, name="source_id")
        if not isinstance(side, LiquiditySide):
            raise TypeError("CLASSIFICATION requires side")
        if not isinstance(scope, LiquidityScope):
            raise TypeError("CLASSIFICATION requires scope")
        lower, upper = _validate_boundaries(boundaries)
        _validate_hash(active_range_snapshot_id, name="active_range_snapshot_id")
        _validate_positive_int(version, name="version")
        _validate_event(event_index, event_timestamp)
        if version == 1 and prior_classification_id is not None:
            raise ValueError("classification version 1 forbids prior_classification_id")
        if version > 1 and prior_classification_id is None:
            raise ValueError("classification versions above 1 require prior_classification_id")
        _require_defaults(
            new_classification_id=new_classification_id,
            classification_ids=classification_ids,
            reclassification_ids=reclassification_ids,
            from_scope=from_scope,
            to_scope=to_scope,
            reason=reason,
        )
        payload.update(
            {
                "active_range_snapshot_id": active_range_snapshot_id,
                "boundaries": {"lower_tick": lower, "upper_tick": upper},
                "event_index": event_index,
                "event_timestamp": _timestamp_text(event_timestamp),
                "prior_classification_id": prior_classification_id,
                "scope": scope.value,
                "side": side.value,
                "source_id": source_id,
                "source_indices": list(source_indices),
                "source_kind": source_kind.value,
                "version": version,
            }
        )
    elif identity_kind == "SNAPSHOT":
        _validate_hash(active_range_snapshot_id, name="active_range_snapshot_id")
        _validate_event(event_index, event_timestamp)
        if len(classification_ids) < 2:
            raise ValueError("SNAPSHOT requires at least two classification_ids")
        if len(set(classification_ids)) != len(classification_ids):
            raise ValueError("classification_ids cannot contain duplicates")
        if len(set(reclassification_ids)) != len(reclassification_ids):
            raise ValueError("reclassification_ids cannot contain duplicates")
        _require_defaults(
            source_indices=source_indices,
            source_kind=source_kind,
            source_id=source_id,
            side=side,
            scope=scope,
            boundaries=boundaries,
            version=version,
            prior_classification_id=prior_classification_id,
            new_classification_id=new_classification_id,
            from_scope=from_scope,
            to_scope=to_scope,
            reason=reason,
        )
        payload.update(
            {
                "active_range_snapshot_id": active_range_snapshot_id,
                "classification_ids": list(classification_ids),
                "event_index": event_index,
                "event_timestamp": _timestamp_text(event_timestamp),
                "reclassification_ids": list(reclassification_ids),
            }
        )
    else:
        if source_kind is not LiquiditySourceKind.SWING:
            raise ValueError("RECLASSIFICATION requires source_kind=SWING")
        _validate_hash(source_id, name="source_id")
        if not isinstance(side, LiquiditySide):
            raise TypeError("RECLASSIFICATION requires side")
        _validate_hash(prior_classification_id, name="prior_classification_id")
        _validate_hash(new_classification_id, name="new_classification_id")
        if prior_classification_id == new_classification_id:
            raise ValueError("reclassification identities must differ")
        _validate_event(event_index, event_timestamp)
        if not isinstance(from_scope, LiquidityScope) or not isinstance(
            to_scope, LiquidityScope
        ):
            raise TypeError("RECLASSIFICATION requires from_scope and to_scope")
        if from_scope is to_scope:
            raise ValueError("reclassification scopes must differ")
        if reason not in _RECLASSIFICATION_REASONS:
            raise ValueError("reason must be an exact reclassification token")
        _require_defaults(
            source_indices=source_indices,
            scope=scope,
            boundaries=boundaries,
            active_range_snapshot_id=active_range_snapshot_id,
            version=version,
            classification_ids=classification_ids,
            reclassification_ids=reclassification_ids,
        )
        payload.update(
            {
                "event_index": event_index,
                "event_timestamp": _timestamp_text(event_timestamp),
                "from_scope": from_scope.value,
                "new_classification_id": new_classification_id,
                "prior_classification_id": prior_classification_id,
                "reason": reason,
                "side": side.value,
                "source_id": source_id,
                "source_kind": source_kind.value,
                "to_scope": to_scope.value,
            }
        )

    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def analyze_liquidity_map(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...] | None,
    equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None,
    dealing_ranges: tuple[DealingRangeSnapshot, ...] | None,
) -> LiquidityMapResult:
    """Classify immutable upstream liquidity evidence without integration."""

    if swings is None or equal_liquidity_pools is None or dealing_ranges is None:
        missing = []
        if swings is None:
            missing.append("swings")
        if equal_liquidity_pools is None:
            missing.append("equal_liquidity_pools")
        if dealing_ranges is None:
            missing.append("dealing_ranges")
        reason = f"Missing complete top-level context: {', '.join(missing)}"
        return LiquidityMapResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            reasons=(reason,),
            blocking_reasons=(reason,),
        )

    try:
        canonical_instrument = _normalize_text(instrument, name="instrument").upper()
        canonical_timeframe = _normalize_text(timeframe, name="timeframe").upper()
        if not isinstance(swings, tuple):
            raise TypeError("swings must be a tuple or None")
        if not isinstance(equal_liquidity_pools, tuple):
            raise TypeError("equal_liquidity_pools must be a tuple or None")
        if not isinstance(dealing_ranges, tuple):
            raise TypeError("dealing_ranges must be a tuple or None")
    except (TypeError, ValueError) as exc:
        return _invalid_result(str(exc))

    valid_swings, swing_issue = _collect_swings(swings)
    swing_by_id = {item.swing_id: item for item in valid_swings}
    valid_pools, pool_issue = _collect_pools(
        equal_liquidity_pools,
        swings_by_id=swing_by_id,
        instrument=canonical_instrument,
        timeframe=canonical_timeframe,
    )
    valid_ranges, range_issue = _collect_ranges(
        dealing_ranges,
        swings_by_id=swing_by_id,
        instrument=canonical_instrument,
        timeframe=canonical_timeframe,
    )
    issues = tuple(item for item in (swing_issue, pool_issue, range_issue) if item is not None)
    first_issue = min(issues, key=_issue_order) if issues else None
    if first_issue is not None and first_issue.moment is None:
        return _invalid_result(first_issue.reason)

    try:
        snapshots, reclassifications, process_issue = _analyze_valid_prefix(
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
            swings=valid_swings,
            pools=valid_pools,
            ranges=valid_ranges,
            stop_before=None if first_issue is None else first_issue.moment,
        )
    except (TypeError, ValueError, AttributeError, KeyError, IndexError, ArithmeticError) as exc:
        return _invalid_result(str(exc))

    chosen_issue = first_issue
    if process_issue is not None and (
        chosen_issue is None or _issue_order(process_issue) < _issue_order(chosen_issue)
    ):
        chosen_issue = process_issue
    if chosen_issue is not None:
        status = (
            SMCV2PrimitiveStatus.AMBIGUOUS
            if chosen_issue.reason.startswith("AMBIGUOUS:")
            else SMCV2PrimitiveStatus.INVALID
        )
        return LiquidityMapResult(
            status=status,
            snapshots=snapshots,
            reclassifications=reclassifications,
            reasons=(chosen_issue.reason,),
            blocking_reasons=(chosen_issue.reason,),
        )
    if snapshots:
        return LiquidityMapResult(
            status=SMCV2PrimitiveStatus.VALID,
            snapshots=snapshots,
            reclassifications=reclassifications,
            reasons=("Liquidity Map analysis completed",),
        )
    return LiquidityMapResult(
        status=SMCV2PrimitiveStatus.NONE,
        reasons=("No valid active external Dealing Range was supplied",),
    )


def _normalize_text(value: str, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _validate_hash(value: object, *, name: str) -> None:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 value")


def _validate_optional_hash(value: object, *, name: str) -> None:
    if value is not None:
        _validate_hash(value, name=name)


def _validate_hash_tuple(values: object, *, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    for value in values:
        _validate_hash(value, name=name)


def _validate_source_indices(values: object, *, allow_empty: bool = False) -> None:
    if not isinstance(values, tuple):
        raise TypeError("source_indices must be a tuple")
    if not values and not allow_empty:
        raise ValueError("source_indices cannot be empty")
    if any(type(value) is not int for value in values):
        raise TypeError("source_indices must contain only integers")
    if any(value < 0 for value in values):
        raise ValueError("source_indices cannot be negative")
    if any(left >= right for left, right in zip(values, values[1:])):
        raise ValueError("source_indices must be unique and strictly increasing")


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


def _validate_boundaries(value: object) -> tuple[int, int]:
    if not isinstance(value, SMCV2TickRange):
        raise TypeError("boundaries must be an SMCV2TickRange")
    try:
        lower = value.lower_tick
        upper = value.upper_tick
    except AttributeError as exc:
        raise ValueError("boundaries are malformed") from exc
    if type(lower) is not int or type(upper) is not int:
        raise TypeError("boundary ticks must be integers")
    if lower > upper:
        raise ValueError("lower boundary cannot exceed upper boundary")
    return lower, upper


def _validate_event(index: object, timestamp: object) -> _Moment:
    _validate_non_negative_int(index, name="event_index")
    normalized = normalize_utc_timestamp(timestamp)  # type: ignore[arg-type]
    return index, normalized  # type: ignore[return-value]


def _timestamp_text(value: object) -> str:
    normalized = normalize_utc_timestamp(value)  # type: ignore[arg-type]
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _require_defaults(**values: object) -> None:
    for name, value in values.items():
        expected = () if name in {"source_indices", "classification_ids", "reclassification_ids"} else None
        if value != expected or type(value) is not type(expected):
            raise ValueError(f"{name} is forbidden for this identity kind")


def _invalid_result(reason: str) -> LiquidityMapResult:
    return LiquidityMapResult(
        status=SMCV2PrimitiveStatus.INVALID,
        reasons=(reason,),
        blocking_reasons=(reason,),
    )


def _issue_order(issue: _Issue) -> tuple[object, ...]:
    if issue.moment is None:
        return 0, -1, ""
    return 1, issue.moment[0], issue.moment[1].isoformat()


def _validate_provenance(value: object, *, name: str) -> _Moment:
    if not isinstance(value, SMCV2EventProvenance):
        raise TypeError(f"{name} must be SMCV2EventProvenance")
    try:
        source_indices = value.source_indices
        source_timestamps = value.source_timestamps
        confirmation_index = value.confirmation_index
        confirmation_timestamp = value.confirmation_timestamp
    except AttributeError as exc:
        raise ValueError(f"{name} is missing a required field") from exc
    _validate_source_indices(source_indices)
    if not isinstance(source_timestamps, tuple):
        raise TypeError(f"{name}.source_timestamps must be a tuple")
    if len(source_timestamps) != len(source_indices):
        raise ValueError(f"{name} source timestamp count does not match")
    normalized_sources = tuple(normalize_utc_timestamp(item) for item in source_timestamps)
    if any(left >= right for left, right in zip(normalized_sources, normalized_sources[1:])):
        raise ValueError(f"{name} source timestamps must be strictly chronological")
    _validate_non_negative_int(confirmation_index, name=f"{name}.confirmation_index")
    normalized_confirmation = normalize_utc_timestamp(confirmation_timestamp)
    if confirmation_index < source_indices[-1]:
        raise ValueError(f"{name} confirmation precedes source index")
    if normalized_confirmation < normalized_sources[-1]:
        raise ValueError(f"{name} confirmation precedes source timestamp")
    return confirmation_index, normalized_confirmation


def _safe_provenance_moment(value: object) -> _Moment | None:
    try:
        provenance = getattr(value, "provenance", None)
        if provenance is None:
            provenance = getattr(value, "first_known_provenance")
        return _validate_provenance(provenance, name="provenance")
    except (TypeError, ValueError, AttributeError):
        return None


def _collect_swings(
    values: tuple[DealingRangeSwing, ...],
) -> tuple[tuple[DealingRangeSwing, ...], _Issue | None]:
    accepted: list[DealingRangeSwing] = []
    seen_ids: set[str] = set()
    previous_key: tuple[object, ...] | None = None
    for value in values:
        fallback = _safe_provenance_moment(value)
        try:
            if not isinstance(value, DealingRangeSwing):
                raise TypeError("swings must contain only DealingRangeSwing values")
            try:
                side = value.side
                price_tick = value.price_tick
                provenance = value.provenance
                swing_id = value.swing_id
            except AttributeError as exc:
                raise ValueError("swing is missing a required field") from exc
            if not isinstance(side, DealingRangeSwingSide):
                raise TypeError("swing side must be DealingRangeSwingSide")
            if type(price_tick) is not int:
                raise TypeError("swing price_tick must be an integer")
            moment = _validate_provenance(provenance, name="swing provenance")
            if len(provenance.source_indices) != 1:
                raise ValueError("a confirmed swing requires one source index")
            _validate_hash(swing_id, name="swing_id")
            key = (*moment, side.value, swing_id)
            if previous_key is not None and key <= previous_key:
                raise ValueError("swings are not in strict composite order")
            if swing_id in seen_ids:
                raise ValueError("duplicate swing_id")
            previous_key = key
            seen_ids.add(swing_id)
            accepted.append(value)
        except (TypeError, ValueError, AttributeError) as exc:
            return tuple(accepted), _Issue(fallback, str(exc))
    return tuple(accepted), None


def _median_tick(values: tuple[int, ...]) -> int:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    midpoint = (Decimal(ordered[middle - 1]) + Decimal(ordered[middle])) / Decimal(2)
    return int(midpoint.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))


def _validate_lifecycle_event(value: object, *, name: str) -> None:
    if not isinstance(value, SMCV2LifecycleEvent):
        raise TypeError(f"{name} must be SMCV2LifecycleEvent")
    try:
        from_state = value.from_state
        to_state = value.to_state
        index = value.index
        timestamp = value.timestamp
        reason = value.reason
    except AttributeError as exc:
        raise ValueError(f"{name} is missing a required field") from exc
    if from_state is not None and not isinstance(from_state, SMCV2LifecycleState):
        raise TypeError(f"{name}.from_state is invalid")
    if not isinstance(to_state, SMCV2LifecycleState):
        raise TypeError(f"{name}.to_state is invalid")
    _validate_non_negative_int(index, name=f"{name}.index")
    normalize_utc_timestamp(timestamp)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(f"{name}.reason must be non-empty text")


def _pool_effective(
    pool: EqualLiquidityPool,
    *,
    swings_by_id: dict[str, DealingRangeSwing],
) -> _Moment:
    members = tuple(swings_by_id[item] for item in pool.member_swing_ids)
    latest = max(
        (
            member.provenance.confirmation_index,
            normalize_utc_timestamp(member.provenance.confirmation_timestamp),
            member.provenance.source_indices[0],
            member.swing_id,
        )
        for member in members
    )
    member_moment = latest[0], latest[1]
    if pool.lifecycle_state in (SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN):
        last = pool.lifecycle_events[-1]
        lifecycle_moment = last.index, normalize_utc_timestamp(last.timestamp)
        return max(member_moment, lifecycle_moment)
    return member_moment


def _validate_pool(
    pool: object,
    *,
    swings_by_id: dict[str, DealingRangeSwing],
    instrument: str,
    timeframe: str,
) -> _Moment:
    if not isinstance(pool, EqualLiquidityPool):
        raise TypeError("equal_liquidity_pools must contain EqualLiquidityPool values")
    try:
        side = pool.side
        lineage_id = pool.lineage_id
        snapshot_id = pool.snapshot_id
        member_ids = pool.member_swing_ids
        source_indices = pool.source_indices
        reference_tick = pool.reference_tick
        lower_tick = pool.lower_tick
        upper_tick = pool.upper_tick
        first_known = pool.first_known_provenance
        state = pool.lifecycle_state
        events = pool.lifecycle_events
    except AttributeError as exc:
        raise ValueError("Equal Liquidity pool is missing a required field") from exc
    if not isinstance(side, EqualLiquiditySide):
        raise TypeError("pool side must be EqualLiquiditySide")
    _validate_hash(lineage_id, name="pool.lineage_id")
    _validate_hash(snapshot_id, name="pool.snapshot_id")
    _validate_hash_tuple(member_ids, name="pool.member_swing_ids")
    _validate_source_indices(source_indices)
    if len(member_ids) < 2 or len(member_ids) != len(source_indices):
        raise ValueError("pool members and source indices must match and contain two")
    if len(set(member_ids)) != len(member_ids):
        raise ValueError("pool member identities cannot repeat")
    if any(type(value) is not int for value in (reference_tick, lower_tick, upper_tick)):
        raise TypeError("pool ticks must be integers")
    if lower_tick != reference_tick - 2 or upper_tick != reference_tick + 2:
        raise ValueError("pool must preserve the locked two-tick band")
    members: list[DealingRangeSwing] = []
    expected_side = (
        DealingRangeSwingSide.HIGH
        if side is EqualLiquiditySide.HIGH
        else DealingRangeSwingSide.LOW
    )
    for member_id in member_ids:
        if member_id not in swings_by_id:
            raise ValueError("pool member swing identity is missing")
        member = swings_by_id[member_id]
        if member.side is not expected_side:
            raise ValueError("pool side conflicts with member swing side")
        if not lower_tick <= member.price_tick <= upper_tick:
            raise ValueError("pool member price is outside its supplied band")
        members.append(member)
    resolved_indices = tuple(item.provenance.source_indices[0] for item in members)
    if resolved_indices != source_indices:
        raise ValueError("pool source indices conflict with member provenance")
    if reference_tick != _median_tick(tuple(item.price_tick for item in members)):
        raise ValueError("pool reference tick does not match the exact median")
    first_moment = _validate_provenance(first_known, name="pool first-known provenance")
    founders = tuple(members[:2])
    founder_indices = tuple(item.provenance.source_indices[0] for item in founders)
    if first_known.source_indices != founder_indices:
        raise ValueError("pool first-known provenance must preserve founder indices")
    latest_founder = max(
        (
            item.provenance.confirmation_index,
            normalize_utc_timestamp(item.provenance.confirmation_timestamp),
        )
        for item in founders
    )
    if first_moment != latest_founder:
        raise ValueError("pool first-known moment must equal latest founder confirmation")
    if not isinstance(events, tuple) or not events:
        raise ValueError("pool lifecycle_events must be a non-empty tuple")
    for position, event in enumerate(events):
        _validate_lifecycle_event(event, name=f"pool lifecycle event {position}")
    validate_lifecycle_history(
        events,
        allowed_transitions={
            None: frozenset({SMCV2LifecycleState.ACTIVE}),
            SMCV2LifecycleState.ACTIVE: frozenset(
                {SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN}
            ),
        },
        terminal_states=frozenset(
            {SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN}
        ),
    )
    if events[0].index != first_moment[0] or normalize_utc_timestamp(events[0].timestamp) != first_moment[1]:
        raise ValueError("pool activation must match first-known moment")
    if state not in (
        SMCV2LifecycleState.ACTIVE,
        SMCV2LifecycleState.SWEPT,
        SMCV2LifecycleState.BROKEN,
    ):
        raise ValueError("pool lifecycle_state is not allowed")
    if events[-1].to_state is not state:
        raise ValueError("pool lifecycle state does not match its history")
    founding_reference = _median_tick(tuple(item.price_tick for item in founders))
    expected_lineage = make_equal_liquidity_id(
        identity_kind="LINEAGE",
        instrument=instrument,
        timeframe=timeframe,
        side=side,
        source_indices=source_indices[:2],
        swing_ids=member_ids[:2],
        reference_tick=founding_reference,
        lower_tick=founding_reference - 2,
        upper_tick=founding_reference + 2,
    )
    if lineage_id != expected_lineage:
        raise ValueError("pool lineage identity does not match its founders")
    expected_snapshot = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference_tick,
        lower_tick=lower_tick,
        upper_tick=upper_tick,
        lineage_id=lineage_id,
        lifecycle_state=state,
    )
    if snapshot_id != expected_snapshot:
        raise ValueError("pool snapshot identity does not match its content")
    return _pool_effective(pool, swings_by_id=swings_by_id)


def _collect_pools(
    values: tuple[EqualLiquidityPool, ...],
    *,
    swings_by_id: dict[str, DealingRangeSwing],
    instrument: str,
    timeframe: str,
) -> tuple[tuple[EqualLiquidityPool, ...], _Issue | None]:
    accepted: list[EqualLiquidityPool] = []
    previous_moment: _Moment | None = None
    seen_snapshots: set[str] = set()
    latest_by_lineage: dict[str, EqualLiquidityPool] = {}
    moment_by_lineage: dict[str, _Moment] = {}
    for value in values:
        fallback = _safe_provenance_moment(value)
        try:
            moment = _validate_pool(
                value,
                swings_by_id=swings_by_id,
                instrument=instrument,
                timeframe=timeframe,
            )
            if previous_moment is not None and moment < previous_moment:
                raise ValueError("pool tuple is not ordered by nondecreasing effective moment")
            if value.snapshot_id in seen_snapshots:
                raise ValueError("duplicate pool snapshot identity")
            prior = latest_by_lineage.get(value.lineage_id)
            if prior is not None:
                if prior.lifecycle_state in (
                    SMCV2LifecycleState.SWEPT,
                    SMCV2LifecycleState.BROKEN,
                ):
                    raise ValueError("terminal pool lineage cannot receive another snapshot")
                if value.side is not prior.side:
                    raise ValueError("pool lineage side changed")
                if value.member_swing_ids[: len(prior.member_swing_ids)] != prior.member_swing_ids:
                    raise ValueError("pool membership is not an exact prefix extension")
                if value.source_indices[: len(prior.source_indices)] != prior.source_indices:
                    raise ValueError("pool source indices are not an exact prefix extension")
                if value.lifecycle_events[: len(prior.lifecycle_events)] != prior.lifecycle_events:
                    raise ValueError("pool lifecycle history is not immutable")
                prior_moment = moment_by_lineage[value.lineage_id]
                if moment == prior_moment and value.lifecycle_state is SMCV2LifecycleState.ACTIVE:
                    if len(value.member_swing_ids) <= len(prior.member_swing_ids):
                        raise ValueError("same-moment ACTIVE revision must add members")
                if value.lifecycle_state in (
                    SMCV2LifecycleState.SWEPT,
                    SMCV2LifecycleState.BROKEN,
                ) and value.member_swing_ids != prior.member_swing_ids:
                    raise ValueError("terminal pool snapshot must retain final membership")
            previous_moment = moment
            seen_snapshots.add(value.snapshot_id)
            latest_by_lineage[value.lineage_id] = value
            moment_by_lineage[value.lineage_id] = moment
            accepted.append(value)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(accepted), _Issue(fallback, str(exc))
    return tuple(accepted), None


def _validate_range_transition(
    transition: object,
    *,
    direction: SMCV2Direction,
    lineage_id: str,
    instrument: str,
    timeframe: str,
) -> _Moment:
    if not isinstance(transition, DealingRangeTransition):
        raise TypeError("range transitions must contain DealingRangeTransition values")
    try:
        transition_id = transition.transition_id
        supplied_lineage = transition.lineage_id
        from_state = transition.from_state
        to_state = transition.to_state
        index = transition.index
        timestamp = transition.timestamp
        reason = transition.reason
        related_event_id = transition.related_event_id
        replacement_lineage_id = transition.replacement_lineage_id
    except AttributeError as exc:
        raise ValueError("range transition is missing a required field") from exc
    _validate_hash(transition_id, name="transition_id")
    if supplied_lineage != lineage_id:
        raise ValueError("transition lineage does not match range lineage")
    if from_state is not None and not isinstance(from_state, DealingRangeState):
        raise TypeError("transition from_state is invalid")
    if not isinstance(to_state, DealingRangeState):
        raise TypeError("transition to_state is invalid")
    if reason not in _RANGE_TRANSITION_REASONS:
        raise ValueError("transition reason is not locked")
    moment = _validate_event(index, timestamp)
    expected = make_dealing_range_id(
        identity_kind="TRANSITION",
        instrument=instrument,
        timeframe=timeframe,
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
    if transition_id != expected:
        raise ValueError("transition identity does not match its content")
    return moment


def _validate_range(
    value: object,
    *,
    swings_by_id: dict[str, DealingRangeSwing],
    instrument: str,
    timeframe: str,
) -> _Moment:
    if not isinstance(value, DealingRangeSnapshot):
        raise TypeError("dealing_ranges must contain DealingRangeSnapshot values")
    try:
        kind = value.kind
        direction = value.direction
        snapshot_id = value.snapshot_id
        source_ids = value.source_swing_ids
        source_indices = value.source_indices
        low_tick = value.low_tick
        high_tick = value.high_tick
        midpoint_tick = value.midpoint_tick
        first_known = value.first_known_provenance
        lineage_id = value.lineage_id
        protected_swing_id = value.protected_swing_id
        construction_event_id = value.construction_event_id
        state = value.state
        transitions = value.transitions
        transition_ids = value.transition_ids
        replacement_lineage_id = value.replacement_lineage_id
    except AttributeError as exc:
        raise ValueError("Dealing Range snapshot is missing a required field") from exc
    if not isinstance(kind, DealingRangeKind):
        raise TypeError("range kind must be DealingRangeKind")
    if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("range direction must be BULLISH or BEARISH")
    _validate_hash(snapshot_id, name="range.snapshot_id")
    _validate_hash_tuple(source_ids, name="range.source_swing_ids")
    _validate_source_indices(source_indices)
    if len(source_ids) < 2 or len(source_ids) != len(source_indices):
        raise ValueError("range source identities and indices must match and contain two")
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("range source swing identities cannot repeat")
    if type(low_tick) is not int or type(high_tick) is not int:
        raise TypeError("range boundaries must be integers")
    if low_tick >= high_tick:
        raise ValueError("range low_tick must be below high_tick")
    if not isinstance(midpoint_tick, Decimal):
        raise TypeError("range midpoint_tick must be Decimal")
    if midpoint_tick != Decimal(low_tick + high_tick) / Decimal(2):
        raise ValueError("range midpoint_tick is not exact")
    moment = _validate_provenance(first_known, name="range first-known provenance")
    resolved: list[DealingRangeSwing] = []
    for source_id in source_ids:
        if source_id not in swings_by_id:
            raise ValueError("range source swing identity is missing")
        resolved.append(swings_by_id[source_id])
    if tuple(item.provenance.source_indices[0] for item in resolved) != source_indices:
        raise ValueError("range source indices conflict with swing provenance")
    if any(
        (
            item.provenance.confirmation_index,
            normalize_utc_timestamp(item.provenance.confirmation_timestamp),
        )
        > moment
        for item in resolved
    ):
        raise ValueError("range source swing was not confirmed by its effective moment")

    boundaries = SMCV2TickRange(low_tick, high_tick)
    if kind is DealingRangeKind.INTERNAL:
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
            raise ValueError("internal range contains forbidden external fields")
        if transitions != () or transition_ids != ():
            raise ValueError("internal range cannot contain transitions")
        expected_snapshot = make_dealing_range_id(
            identity_kind="INTERNAL_RANGE",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_indices=source_indices,
            swing_ids=source_ids,
            boundaries=boundaries,
            range_kind=DealingRangeKind.INTERNAL,
        )
        if snapshot_id != expected_snapshot:
            raise ValueError("internal range identity does not match its content")
        return moment

    _validate_hash(lineage_id, name="range.lineage_id")
    _validate_hash(protected_swing_id, name="range.protected_swing_id")
    _validate_hash(construction_event_id, name="range.construction_event_id")
    if not isinstance(state, DealingRangeState):
        raise TypeError("external range state must be DealingRangeState")
    if protected_swing_id not in source_ids:
        raise ValueError("protected swing is not a range source identity")
    protected = swings_by_id[protected_swing_id]
    expected_protected_side = (
        DealingRangeSwingSide.LOW
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.HIGH
    )
    expected_protected_tick = low_tick if direction is SMCV2Direction.BULLISH else high_tick
    if protected.side is not expected_protected_side or protected.price_tick != expected_protected_tick:
        raise ValueError("protected swing does not match direction and protected boundary")
    expected_target_side = (
        DealingRangeSwingSide.HIGH
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.LOW
    )
    if any(
        item.swing_id != protected_swing_id and item.side is not expected_target_side
        for item in resolved
    ):
        raise ValueError("range target swing side conflicts with range direction")
    if not isinstance(transitions, tuple) or not transitions:
        raise ValueError("external range requires transition history")
    _validate_hash_tuple(transition_ids, name="range.transition_ids")
    if len(transition_ids) != len(transitions):
        raise ValueError("range transition IDs do not match transition objects")
    previous_state: DealingRangeState | None = None
    previous_moment: _Moment | None = None
    for position, transition in enumerate(transitions):
        transition_moment = _validate_range_transition(
            transition,
            direction=direction,
            lineage_id=lineage_id,
            instrument=instrument,
            timeframe=timeframe,
        )
        if transition.transition_id != transition_ids[position]:
            raise ValueError("range transition ID order does not match objects")
        if position == 0 and transition.from_state is not None:
            raise ValueError("range transition chain must begin from None")
        if position > 0 and transition.from_state is not previous_state:
            raise ValueError("range transition state chain is broken")
        if previous_moment is not None and transition_moment <= previous_moment:
            raise ValueError("range transition moments must be strictly increasing")
        previous_state = transition.to_state
        previous_moment = transition_moment
    if transitions[0].to_state is not DealingRangeState.ACTIVE:
        raise ValueError("range must begin ACTIVE")
    if previous_state is not state:
        raise ValueError("range state does not match transition history")
    if transitions[0].related_event_id != construction_event_id:
        raise ValueError("construction transition does not match construction event")
    if state in (DealingRangeState.SUPERSEDED, DealingRangeState.INVALIDATED):
        if previous_moment != moment:
            raise ValueError("terminal range transition must equal effective moment")
    elif len(transitions) == 1 and previous_moment is not None and moment < previous_moment:
        raise ValueError("active range effective moment precedes construction")
    expected_snapshot = make_dealing_range_id(
        identity_kind="SNAPSHOT",
        instrument=instrument,
        timeframe=timeframe,
        direction=direction,
        source_indices=source_indices,
        swing_ids=source_ids,
        boundaries=boundaries,
        lineage_id=lineage_id,
        construction_event_id=construction_event_id,
        range_kind=DealingRangeKind.EXTERNAL,
        state=state,
        transition_ids=transition_ids,
        replacement_lineage_id=replacement_lineage_id,
    )
    if snapshot_id != expected_snapshot:
        raise ValueError("range snapshot identity does not match its content")
    return moment


def _collect_ranges(
    values: tuple[DealingRangeSnapshot, ...],
    *,
    swings_by_id: dict[str, DealingRangeSwing],
    instrument: str,
    timeframe: str,
) -> tuple[tuple[DealingRangeSnapshot, ...], _Issue | None]:
    accepted: list[DealingRangeSnapshot] = []
    previous_moment: _Moment | None = None
    seen_snapshots: set[str] = set()
    latest_by_lineage: dict[str, DealingRangeSnapshot] = {}
    for value in values:
        fallback = _safe_provenance_moment(value)
        try:
            moment = _validate_range(
                value,
                swings_by_id=swings_by_id,
                instrument=instrument,
                timeframe=timeframe,
            )
            if previous_moment is not None and moment < previous_moment:
                raise ValueError("range tuple is not ordered by nondecreasing effective moment")
            if value.snapshot_id in seen_snapshots:
                raise ValueError("duplicate range snapshot identity")
            if value.kind is DealingRangeKind.EXTERNAL:
                assert value.lineage_id is not None
                prior = latest_by_lineage.get(value.lineage_id)
                if prior is None and value.state is DealingRangeState.ACTIVE:
                    construction_moment = _validate_event(
                        value.transitions[0].index,
                        value.transitions[0].timestamp,
                    )
                    if moment != construction_moment:
                        raise ValueError(
                            "initial or replacement ACTIVE range effective moment "
                            "must equal construction transition"
                        )
                if prior is not None:
                    if prior.state in (
                        DealingRangeState.SUPERSEDED,
                        DealingRangeState.INVALIDATED,
                    ):
                        raise ValueError("terminal range lineage cannot receive another snapshot")
                    if value.direction is not prior.direction:
                        raise ValueError("range lineage direction changed")
                    if value.protected_swing_id != prior.protected_swing_id:
                        raise ValueError("range protected swing identity changed")
                    if value.construction_event_id != prior.construction_event_id:
                        raise ValueError("range construction event identity changed")
                    if value.source_swing_ids[: len(prior.source_swing_ids)] != prior.source_swing_ids:
                        raise ValueError("range source identities are not an exact prefix extension")
                    if value.source_indices[: len(prior.source_indices)] != prior.source_indices:
                        raise ValueError("range source indices are not an exact prefix extension")
                    if value.transitions[: len(prior.transitions)] != prior.transitions:
                        raise ValueError("range transition history is not immutable")
                    if value.direction is SMCV2Direction.BULLISH:
                        if value.low_tick != prior.low_tick or value.high_tick < prior.high_tick:
                            raise ValueError("bullish range extension changed protected boundary")
                    else:
                        if value.high_tick != prior.high_tick or value.low_tick > prior.low_tick:
                            raise ValueError("bearish range extension changed protected boundary")
                latest_by_lineage[value.lineage_id] = value
            previous_moment = moment
            seen_snapshots.add(value.snapshot_id)
            accepted.append(value)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return tuple(accepted), _Issue(fallback, str(exc))
    return tuple(accepted), None


def _range_effective(value: DealingRangeSnapshot) -> _Moment:
    return _validate_provenance(value.first_known_provenance, name="range provenance")


def _swing_effective(value: DealingRangeSwing) -> _Moment:
    return _validate_provenance(value.provenance, name="swing provenance")


def _apply_range_group(
    active: DealingRangeSnapshot | None,
    values: tuple[DealingRangeSnapshot, ...],
) -> DealingRangeSnapshot | None:
    external = tuple(item for item in values if item.kind is DealingRangeKind.EXTERNAL)
    if not external:
        return active
    pre_active = active
    terminal: DealingRangeSnapshot | None = None
    candidates: list[DealingRangeSnapshot] = []
    current = active
    for item in external:
        if item.state in (DealingRangeState.SUPERSEDED, DealingRangeState.INVALIDATED):
            if candidates:
                raise _InvalidGroup("new ACTIVE range appeared before old terminal evidence")
            if current is None or item.lineage_id != current.lineage_id:
                raise _InvalidGroup("terminal range does not match pre-index active lineage")
            if terminal is not None:
                raise _InvalidGroup("one effective group cannot terminate two active lineages")
            terminal = item
            current = None
            continue
        if item.state is not DealingRangeState.ACTIVE:
            raise _InvalidGroup("external range has unsupported state")
        if pre_active is not None and terminal is None:
            if item.lineage_id != pre_active.lineage_id:
                raise _InvalidGroup("new active lineage lacks prior terminal evidence")
            if candidates:
                raise _InvalidGroup("same lineage has contradictory active snapshots")
            candidates.append(item)
            current = item
            continue
        candidates.append(item)
        current = item

    distinct = {item.lineage_id for item in candidates}
    if len(distinct) > 1:
        raise _AmbiguousGroup("two unrelated active-range candidates share one effective moment")
    if terminal is not None and candidates:
        candidate = candidates[-1]
        last_transition = terminal.transitions[-1]
        if terminal.state is DealingRangeState.SUPERSEDED:
            if terminal.replacement_lineage_id != candidate.lineage_id:
                raise _InvalidGroup("superseded range does not link its replacement lineage")
        elif last_transition.reason == "CHOCH_CLOSE_THROUGH_INVALIDATION":
            if pre_active is None or candidate.direction is pre_active.direction:
                raise _InvalidGroup("reverse CHOCH replacement must reverse direction")
        else:
            raise _InvalidGroup("observation invalidation cannot activate a same-moment range")
    return current


def _classification_material(value: LiquidityClassification) -> tuple[object, ...]:
    return (
        value.source_kind,
        value.source_id,
        value.side,
        value.scope,
        value.source_indices,
        value.boundaries.lower_tick,
        value.boundaries.upper_tick,
        value.active_range_lineage_id,
    )


def _classification_sort_key(value: LiquidityClassification) -> tuple[str, ...]:
    return (
        value.scope.value,
        value.side.value,
        value.source_kind.value,
        value.source_id,
        value.classification_id,
    )


def _reclassification_sort_key(value: LiquidityReclassification) -> tuple[object, ...]:
    return (
        value.index,
        normalize_utc_timestamp(value.timestamp),
        value.source_kind.value,
        value.source_id,
        value.reclassification_id,
    )


def _spec_sort_key(value: _ClassificationSpec) -> tuple[str, ...]:
    return value.source_kind.value, value.source_id, value.side.value, value.scope.value


def _side_for_swing(value: DealingRangeSwing) -> LiquiditySide:
    return (
        LiquiditySide.BUY_SIDE
        if value.side is DealingRangeSwingSide.HIGH
        else LiquiditySide.SELL_SIDE
    )


def _side_for_pool(value: EqualLiquidityPool) -> LiquiditySide:
    return (
        LiquiditySide.BUY_SIDE
        if value.side is EqualLiquiditySide.HIGH
        else LiquiditySide.SELL_SIDE
    )


def _build_specs(
    *,
    instrument: str,
    timeframe: str,
    active: DealingRangeSnapshot,
    known_swings: tuple[DealingRangeSwing, ...],
    active_pools: tuple[EqualLiquidityPool, ...],
) -> tuple[_ClassificationSpec, ...]:
    assert active.lineage_id is not None
    source_indices = active.source_indices[:2]
    specs: list[_ClassificationSpec] = []
    for side, tick in (
        (LiquiditySide.BUY_SIDE, active.high_tick),
        (LiquiditySide.SELL_SIDE, active.low_tick),
    ):
        source_id = make_liquidity_map_id(
            identity_kind="BOUNDARY",
            instrument=instrument,
            timeframe=timeframe,
            active_range_lineage_id=active.lineage_id,
            source_kind=LiquiditySourceKind.RANGE_BOUNDARY,
            side=side,
        )
        specs.append(
            _ClassificationSpec(
                source_kind=LiquiditySourceKind.RANGE_BOUNDARY,
                source_id=source_id,
                side=side,
                scope=LiquidityScope.EXTERNAL,
                source_indices=source_indices,
                boundaries=SMCV2TickRange(tick, tick),
                active_range_lineage_id=active.lineage_id,
            )
        )

    active_source_ids = set(active.source_swing_ids)
    for swing in known_swings:
        side = _side_for_swing(swing)
        boundary_tick = active.high_tick if side is LiquiditySide.BUY_SIDE else active.low_tick
        if swing.swing_id in active_source_ids and swing.price_tick == boundary_tick:
            scope = LiquidityScope.EXTERNAL
        elif active.low_tick < swing.price_tick < active.high_tick:
            scope = LiquidityScope.INTERNAL
        else:
            continue
        specs.append(
            _ClassificationSpec(
                source_kind=LiquiditySourceKind.SWING,
                source_id=swing.swing_id,
                side=side,
                scope=scope,
                source_indices=swing.provenance.source_indices,
                boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick),
                active_range_lineage_id=active.lineage_id,
            )
        )

    for pool in active_pools:
        if not (
            active.low_tick
            < pool.lower_tick
            <= pool.reference_tick
            <= pool.upper_tick
            < active.high_tick
        ):
            continue
        specs.append(
            _ClassificationSpec(
                source_kind=LiquiditySourceKind.EQUAL_LIQUIDITY_POOL,
                source_id=pool.lineage_id,
                side=_side_for_pool(pool),
                scope=LiquidityScope.INTERNAL,
                source_indices=pool.source_indices,
                boundaries=SMCV2TickRange(pool.lower_tick, pool.upper_tick),
                active_range_lineage_id=active.lineage_id,
            )
        )
    if len({item.key for item in specs}) != len(specs):
        raise _InvalidGroup("duplicate semantic classification source identity")
    return tuple(sorted(specs, key=_spec_sort_key))


def _make_classification(
    spec: _ClassificationSpec,
    *,
    instrument: str,
    timeframe: str,
    active_range_snapshot_id: str,
    moment: _Moment,
    prior: LiquidityClassification | None,
) -> LiquidityClassification:
    version = 1 if prior is None else prior.version + 1
    prior_id = None if prior is None else prior.classification_id
    classification_id = make_liquidity_map_id(
        identity_kind="CLASSIFICATION",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=spec.active_range_lineage_id,
        source_indices=spec.source_indices,
        source_kind=spec.source_kind,
        source_id=spec.source_id,
        side=spec.side,
        scope=spec.scope,
        boundaries=spec.boundaries,
        active_range_snapshot_id=active_range_snapshot_id,
        version=version,
        prior_classification_id=prior_id,
        event_index=moment[0],
        event_timestamp=moment[1],
    )
    return LiquidityClassification(
        classification_id=classification_id,
        source_kind=spec.source_kind,
        source_id=spec.source_id,
        side=spec.side,
        scope=spec.scope,
        source_indices=spec.source_indices,
        boundaries=spec.boundaries,
        active_range_lineage_id=spec.active_range_lineage_id,
        active_range_snapshot_id=active_range_snapshot_id,
        version=version,
        classification_index=moment[0],
        classification_timestamp=moment[1],
        prior_classification_id=prior_id,
    )


def _make_reclassification(
    prior: LiquidityClassification,
    current: LiquidityClassification,
    *,
    instrument: str,
    timeframe: str,
    moment: _Moment,
) -> LiquidityReclassification:
    if prior.scope is LiquidityScope.INTERNAL and current.scope is LiquidityScope.EXTERNAL:
        reason = "INTERNAL_TO_EXTERNAL_RANGE_DEFINING"
    elif prior.scope is LiquidityScope.EXTERNAL and current.scope is LiquidityScope.INTERNAL:
        reason = "EXTERNAL_TO_INTERNAL_SUBORDINATE"
    else:
        raise _InvalidGroup("scope change is not a locked reclassification")
    reclassification_id = make_liquidity_map_id(
        identity_kind="RECLASSIFICATION",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=current.active_range_lineage_id,
        source_kind=LiquiditySourceKind.SWING,
        source_id=current.source_id,
        side=current.side,
        prior_classification_id=prior.classification_id,
        new_classification_id=current.classification_id,
        event_index=moment[0],
        event_timestamp=moment[1],
        from_scope=prior.scope,
        to_scope=current.scope,
        reason=reason,
    )
    return LiquidityReclassification(
        reclassification_id=reclassification_id,
        source_kind=LiquiditySourceKind.SWING,
        source_id=current.source_id,
        side=current.side,
        from_scope=prior.scope,
        to_scope=current.scope,
        prior_classification_id=prior.classification_id,
        new_classification_id=current.classification_id,
        index=moment[0],
        timestamp=moment[1],
        reason=reason,
    )


def _analyze_valid_prefix(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...],
    pools: tuple[EqualLiquidityPool, ...],
    ranges: tuple[DealingRangeSnapshot, ...],
    stop_before: _Moment | None,
) -> tuple[
    tuple[LiquidityMapSnapshot, ...],
    tuple[LiquidityReclassification, ...],
    _Issue | None,
]:
    swing_by_id = {item.swing_id: item for item in swings}
    swing_groups: dict[_Moment, list[DealingRangeSwing]] = {}
    pool_groups: dict[_Moment, list[EqualLiquidityPool]] = {}
    range_groups: dict[_Moment, list[DealingRangeSnapshot]] = {}
    moments: set[_Moment] = set()
    for swing in swings:
        moment = _swing_effective(swing)
        swing_groups.setdefault(moment, []).append(swing)
        moments.add(moment)
    for pool in pools:
        moment = _pool_effective(pool, swings_by_id=swing_by_id)
        pool_groups.setdefault(moment, []).append(pool)
        moments.add(moment)
    for range_snapshot in ranges:
        moment = _range_effective(range_snapshot)
        range_groups.setdefault(moment, []).append(range_snapshot)
        moments.add(moment)

    active_range: DealingRangeSnapshot | None = None
    pool_state: dict[str, EqualLiquidityPool] = {}
    history: dict[_SourceKey, list[LiquidityClassification]] = {}
    present_keys: set[_SourceKey] = set()
    snapshots: list[LiquidityMapSnapshot] = []
    all_reclassifications: list[LiquidityReclassification] = []

    for moment in sorted(moments):
        if stop_before is not None and moment >= stop_before:
            break
        group_ranges = tuple(range_groups.get(moment, ()))
        group_pools = tuple(pool_groups.get(moment, ()))
        try:
            active_range = _apply_range_group(active_range, group_ranges)
            for pool in group_pools:
                if pool.lifecycle_state is SMCV2LifecycleState.ACTIVE:
                    pool_state[pool.lineage_id] = pool
                else:
                    pool_state.pop(pool.lineage_id, None)
            if active_range is None:
                present_keys = set()
                continue
            known_swings = tuple(
                item for item in swings if _swing_effective(item) <= moment
            )
            specs = _build_specs(
                instrument=instrument,
                timeframe=timeframe,
                active=active_range,
                known_swings=known_swings,
                active_pools=tuple(pool_state.values()),
            )
            current: list[LiquidityClassification] = []
            event_reclassifications: list[LiquidityReclassification] = []
            new_present: set[_SourceKey] = set()
            for spec in specs:
                prior = history.get(spec.key, [None])[-1]
                if (
                    prior is not None
                    and _classification_material(prior) == spec.material
                    and spec.key in present_keys
                ):
                    classification = prior
                else:
                    classification = _make_classification(
                        spec,
                        instrument=instrument,
                        timeframe=timeframe,
                        active_range_snapshot_id=active_range.snapshot_id,
                        moment=moment,
                        prior=prior,
                    )
                    history.setdefault(spec.key, []).append(classification)
                    if (
                        prior is not None
                        and prior.scope is not classification.scope
                        and classification.source_kind is LiquiditySourceKind.SWING
                    ):
                        event_reclassifications.append(
                            _make_reclassification(
                                prior,
                                classification,
                                instrument=instrument,
                                timeframe=timeframe,
                                moment=moment,
                            )
                        )
                current.append(classification)
                new_present.add(spec.key)
            present_keys = new_present
            ordered_classifications = tuple(sorted(current, key=_classification_sort_key))
            ordered_reclassifications = tuple(
                sorted(event_reclassifications, key=_reclassification_sort_key)
            )
            classification_ids = tuple(
                item.classification_id for item in ordered_classifications
            )
            reclassification_ids = tuple(
                item.reclassification_id for item in ordered_reclassifications
            )
            assert active_range.lineage_id is not None
            map_id = make_liquidity_map_id(
                identity_kind="MAP",
                instrument=instrument,
                timeframe=timeframe,
                active_range_lineage_id=active_range.lineage_id,
            )
            snapshot_id = make_liquidity_map_id(
                identity_kind="SNAPSHOT",
                instrument=instrument,
                timeframe=timeframe,
                active_range_lineage_id=active_range.lineage_id,
                active_range_snapshot_id=active_range.snapshot_id,
                classification_ids=classification_ids,
                reclassification_ids=reclassification_ids,
                event_index=moment[0],
                event_timestamp=moment[1],
            )
            if snapshots:
                prior_snapshot = snapshots[-1]
                if (
                    prior_snapshot.map_id == map_id
                    and prior_snapshot.active_range_snapshot_id == active_range.snapshot_id
                    and prior_snapshot.classification_ids == classification_ids
                    and not reclassification_ids
                ):
                    continue
            snapshots.append(
                LiquidityMapSnapshot(
                    map_id=map_id,
                    snapshot_id=snapshot_id,
                    active_range_lineage_id=active_range.lineage_id,
                    active_range_snapshot_id=active_range.snapshot_id,
                    index=moment[0],
                    timestamp=moment[1],
                    classifications=ordered_classifications,
                    classification_ids=classification_ids,
                    reclassifications=ordered_reclassifications,
                    reclassification_ids=reclassification_ids,
                )
            )
            all_reclassifications.extend(ordered_reclassifications)
        except _AmbiguousGroup as exc:
            return (
                tuple(snapshots),
                tuple(sorted(all_reclassifications, key=_reclassification_sort_key)),
                _Issue(moment, f"AMBIGUOUS: {exc}"),
            )
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
            return (
                tuple(snapshots),
                tuple(sorted(all_reclassifications, key=_reclassification_sort_key)),
                _Issue(moment, str(exc)),
            )
    return (
        tuple(snapshots),
        tuple(sorted(all_reclassifications, key=_reclassification_sort_key)),
        None,
    )


__all__ = [
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
]
