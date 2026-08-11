from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import re

from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
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
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    make_fair_value_gap_id,
)
from smc.liquidity_map import (
    LiquidityClassification,
    LiquidityMapSnapshot,
    LiquidityReclassification,
    LiquidityScope,
    LiquiditySide,
    LiquiditySourceKind,
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


INDUCEMENT_DETECTOR_VERSION = "SMC-V2-INDUCEMENT-1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_FORMATION_REASON = "FORMATION_CONFIRMED"
_FVG_REASON_BY_STATE = {
    FairValueGapState.TOUCHED: "WICK_TOUCH",
    FairValueGapState.PARTIALLY_FILLED: "PARTIAL_FILL",
    FairValueGapState.MIDPOINT_FILLED: "MIDPOINT_FILL",
    FairValueGapState.FULLY_FILLED: "FULL_FILL",
    FairValueGapState.INVALIDATED: "CLOSE_THROUGH_INVALIDATION",
}
_FVG_ALLOWED_TARGETS = {
    FairValueGapState.ACTIVE: frozenset(_FVG_REASON_BY_STATE),
    FairValueGapState.TOUCHED: frozenset(
        {
            FairValueGapState.PARTIALLY_FILLED,
            FairValueGapState.MIDPOINT_FILLED,
            FairValueGapState.FULLY_FILLED,
            FairValueGapState.INVALIDATED,
        }
    ),
    FairValueGapState.PARTIALLY_FILLED: frozenset(
        {
            FairValueGapState.MIDPOINT_FILLED,
            FairValueGapState.FULLY_FILLED,
            FairValueGapState.INVALIDATED,
        }
    ),
    FairValueGapState.MIDPOINT_FILLED: frozenset(
        {
            FairValueGapState.FULLY_FILLED,
            FairValueGapState.INVALIDATED,
        }
    ),
    FairValueGapState.FULLY_FILLED: frozenset(),
    FairValueGapState.INVALIDATED: frozenset(),
}


@dataclass(frozen=True)
class InducementObservation:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    is_closed: bool


@dataclass(frozen=True)
class Inducement:
    inducement_id: str
    direction: SMCV2Direction
    active_range_lineage_id: str
    active_range_snapshot_id: str
    liquidity_map_snapshot_id: str
    external_target_classification_id: str
    internal_pool_classification_id: str
    internal_pool_id: str
    sweep_index: int
    sweep_timestamp: datetime
    sweep_extreme_tick: int
    reclaim_close_tick: int
    structure_event_id: str
    structure_event_type: DealingRangeEventType
    confirmation_index: int
    confirmation_timestamp: datetime
    confirmation_offset_bars: int
    fair_value_gap_id: str
    displacement_id: str


@dataclass(frozen=True)
class InducementSnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    inducement_ids: tuple[str, ...]


@dataclass(frozen=True)
class InducementResult:
    status: SMCV2PrimitiveStatus
    inducements: tuple[Inducement, ...] = ()
    snapshots: tuple[InducementSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Moment:
    index: int
    timestamp: datetime


@dataclass(frozen=True)
class _Sweep:
    direction: SMCV2Direction
    active_range: DealingRangeSnapshot
    map_snapshot: LiquidityMapSnapshot
    external_target: LiquidityClassification
    internal_classification: LiquidityClassification
    active_pool: EqualLiquidityPool
    swept_pool: EqualLiquidityPool
    observation: InducementObservation
    observation_position: int


class _NoCandidate(ValueError):
    pass


def make_inducement_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction | None = None,
    active_range_lineage_id: str | None = None,
    active_range_snapshot_id: str | None = None,
    liquidity_map_snapshot_id: str | None = None,
    external_target_classification_id: str | None = None,
    internal_pool_classification_id: str | None = None,
    internal_pool_id: str | None = None,
    sweep_index: int | None = None,
    sweep_timestamp: datetime | None = None,
    sweep_extreme_tick: int | None = None,
    reclaim_close_tick: int | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    confirmation_offset_bars: int | None = None,
    fair_value_gap_id: str | None = None,
    displacement_id: str | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    inducement_ids: tuple[str, ...] = (),
) -> str:
    kind = _text(identity_kind, "identity_kind")
    if kind not in {"INDUCEMENT", "SNAPSHOT"}:
        raise ValueError("identity_kind must be INDUCEMENT or SNAPSHOT")
    canonical_instrument = _text(instrument, "instrument").upper()
    canonical_timeframe = _text(timeframe, "timeframe").upper()
    common = {
        "detector_version": INDUCEMENT_DETECTOR_VERSION,
        "identity_kind": kind,
        "instrument": canonical_instrument,
        "timeframe": canonical_timeframe,
    }
    source_values = (
        direction,
        active_range_lineage_id,
        active_range_snapshot_id,
        liquidity_map_snapshot_id,
        external_target_classification_id,
        internal_pool_classification_id,
        internal_pool_id,
        sweep_index,
        sweep_timestamp,
        sweep_extreme_tick,
        reclaim_close_tick,
        structure_event_id,
        structure_event_type,
        confirmation_index,
        confirmation_timestamp,
        confirmation_offset_bars,
        fair_value_gap_id,
        displacement_id,
    )
    if kind == "INDUCEMENT":
        if effective_index is not None or effective_timestamp is not None or inducement_ids != ():
            raise ValueError("INDUCEMENT forbids snapshot-only parameters")
        if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("direction must be BULLISH or BEARISH")
        hashes = {
            "active_range_lineage_id": active_range_lineage_id,
            "active_range_snapshot_id": active_range_snapshot_id,
            "liquidity_map_snapshot_id": liquidity_map_snapshot_id,
            "external_target_classification_id": external_target_classification_id,
            "internal_pool_classification_id": internal_pool_classification_id,
            "internal_pool_id": internal_pool_id,
            "structure_event_id": structure_event_id,
            "fair_value_gap_id": fair_value_gap_id,
            "displacement_id": displacement_id,
        }
        for name, value in hashes.items():
            _hash_value(value, name)
        _nonnegative(sweep_index, "sweep_index")
        _tick(sweep_extreme_tick, "sweep_extreme_tick")
        _tick(reclaim_close_tick, "reclaim_close_tick")
        sweep_time = _timestamp(sweep_timestamp, "sweep_timestamp")
        _nonnegative(confirmation_index, "confirmation_index")
        confirmation_time = _timestamp(
            confirmation_timestamp, "confirmation_timestamp"
        )
        if structure_event_type not in (
            DealingRangeEventType.BOS,
            DealingRangeEventType.CHOCH,
        ):
            raise ValueError("structure_event_type must be BOS or CHOCH")
        if type(confirmation_offset_bars) is not int or confirmation_offset_bars not in (1, 2, 3):
            raise ValueError("confirmation_offset_bars must be 1, 2, or 3")
        if (sweep_index, sweep_time) >= (confirmation_index, confirmation_time):
            raise ValueError("sweep must be strictly before confirmation")
        if direction is SMCV2Direction.BULLISH:
            if sweep_extreme_tick >= reclaim_close_tick:
                raise ValueError("bullish sweep extreme must be below reclaim close")
        elif sweep_extreme_tick <= reclaim_close_tick:
            raise ValueError("bearish sweep extreme must be above reclaim close")
        payload = {
            **common,
            "direction": direction.value,
            **hashes,
            "sweep_index": sweep_index,
            "sweep_timestamp": _timestamp_text(sweep_time),
            "sweep_extreme_tick": sweep_extreme_tick,
            "reclaim_close_tick": reclaim_close_tick,
            "structure_event_type": structure_event_type.value,
            "confirmation_index": confirmation_index,
            "confirmation_timestamp": _timestamp_text(confirmation_time),
            "confirmation_offset_bars": confirmation_offset_bars,
        }
    else:
        if any(value is not None for value in source_values):
            raise ValueError("SNAPSHOT forbids inducement-only parameters")
        _nonnegative(effective_index, "effective_index")
        effective_time = _timestamp(effective_timestamp, "effective_timestamp")
        _hash_tuple(inducement_ids, "inducement_ids", allow_empty=False)
        if len(set(inducement_ids)) != len(inducement_ids):
            raise ValueError("inducement_ids must be unique")
        payload = {
            **common,
            "effective_index": effective_index,
            "effective_timestamp": _timestamp_text(effective_time),
            "inducement_ids": list(inducement_ids),
        }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def analyze_inducements(
    *,
    instrument: str,
    timeframe: str,
    dealing_range_snapshots: tuple[DealingRangeSnapshot, ...] | None,
    liquidity_map_snapshots: tuple[LiquidityMapSnapshot, ...] | None,
    equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    fair_value_gaps: tuple[FairValueGap, ...] | None,
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...] | None,
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] | None,
    observations: tuple[InducementObservation, ...] | None,
) -> InducementResult:
    try:
        canonical_instrument = _text(instrument, "instrument").upper()
        canonical_timeframe = _text(timeframe, "timeframe").upper()
        supplied = {
            "dealing_range_snapshots": dealing_range_snapshots,
            "liquidity_map_snapshots": liquidity_map_snapshots,
            "equal_liquidity_pools": equal_liquidity_pools,
            "structure_events": structure_events,
            "fair_value_gaps": fair_value_gaps,
            "fair_value_gap_transitions": fair_value_gap_transitions,
            "fair_value_gap_snapshots": fair_value_gap_snapshots,
            "observations": observations,
        }
        missing = tuple(name for name, value in supplied.items() if value is None)
        for name, value in supplied.items():
            if value is not None and type(value) is not tuple:
                raise ValueError(f"{name} must be an exact tuple or None")
        try:
            obs = _validate_observations(observations or ())
        except (AttributeError, TypeError, ValueError, OverflowError) as observation_error:
            prefix, bad_value = _observation_prefix(observations)
            if prefix and _has_strictly_later_determinable_moment(bad_value, prefix[-1]):
                prefix_result = analyze_inducements(
                    instrument=instrument,
                    timeframe=timeframe,
                    dealing_range_snapshots=dealing_range_snapshots,
                    liquidity_map_snapshots=liquidity_map_snapshots,
                    equal_liquidity_pools=equal_liquidity_pools,
                    structure_events=structure_events,
                    fair_value_gaps=fair_value_gaps,
                    fair_value_gap_transitions=fair_value_gap_transitions,
                    fair_value_gap_snapshots=fair_value_gap_snapshots,
                    observations=prefix,
                )
                if prefix_result.status in (
                    SMCV2PrimitiveStatus.VALID,
                    SMCV2PrimitiveStatus.AMBIGUOUS,
                ):
                    return InducementResult(
                        status=SMCV2PrimitiveStatus.INVALID,
                        inducements=prefix_result.inducements,
                        snapshots=prefix_result.snapshots,
                        reasons=(str(observation_error) or type(observation_error).__name__,),
                        blocking_reasons=(
                            "determinably later malformed observation",
                        ),
                    )
            raise
        ranges = _validate_ranges(
            dealing_range_snapshots or (),
            canonical_instrument,
            canonical_timeframe,
        )
        pools = _validate_pools(
            equal_liquidity_pools or (),
            canonical_instrument,
            canonical_timeframe,
        )
        maps = _validate_maps(
            liquidity_map_snapshots or (),
            canonical_instrument,
            canonical_timeframe,
        )
        if missing:
            partial_observations = (
                {item.index: item for item in obs}
                if observations is not None
                else None
            )
            events = (
                _validate_events(structure_events, partial_observations)
                if structure_events is not None
                else ()
            )
            _validate_partial_gap_history(
                fair_value_gap_transitions or (),
                fair_value_gap_snapshots or (),
                canonical_instrument,
                canonical_timeframe,
                transitions_are_complete=fair_value_gap_transitions is not None,
                snapshots_are_complete=fair_value_gap_snapshots is not None,
            )
            if fair_value_gaps is not None:
                gaps, _, _ = _validate_gaps(
                    fair_value_gaps,
                    fair_value_gap_transitions or (),
                    fair_value_gap_snapshots or (),
                    partial_observations,
                    canonical_instrument,
                    canonical_timeframe,
                    history_is_complete=(
                        fair_value_gap_transitions is not None
                        and fair_value_gap_snapshots is not None
                    ),
                )
            else:
                gaps = ()
            if structure_events is not None and fair_value_gaps is not None:
                event_ids = {item.event_id for item in events}
                if any(item.structure_event_id not in event_ids for item in gaps):
                    raise ValueError("FVG has a dangling structure-event reference")
            return InducementResult(
                status=SMCV2PrimitiveStatus.UNKNOWN,
                reasons=("top-level context is missing",),
                blocking_reasons=missing,
            )
        obs_by_index = {item.index: item for item in obs}
        events = _validate_events(structure_events or (), obs_by_index)
        gaps, gap_transitions, gap_snapshots = _validate_gaps(
            fair_value_gaps or (),
            fair_value_gap_transitions or (),
            fair_value_gap_snapshots or (),
            obs_by_index,
            canonical_instrument,
            canonical_timeframe,
        )
        _validate_cross_references(ranges, pools, maps, events, gaps)
        if not any(
            (
                ranges,
                pools,
                maps,
                events,
                gaps,
                gap_transitions,
                gap_snapshots,
                obs,
            )
        ):
            return InducementResult(
                status=SMCV2PrimitiveStatus.NONE,
                reasons=("complete supplied evidence contains no inducement sequence",),
            )
        result = _analyze_valid(
            instrument=canonical_instrument,
            timeframe=canonical_timeframe,
            ranges=ranges,
            maps=maps,
            pools=pools,
            events=events,
            gaps=gaps,
            gap_transitions=gap_transitions,
            gap_snapshots=gap_snapshots,
            observations=obs,
        )
        return result
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        recovered = _recover_prior_evidence(
            instrument=instrument,
            timeframe=timeframe,
            dealing_range_snapshots=dealing_range_snapshots,
            liquidity_map_snapshots=liquidity_map_snapshots,
            equal_liquidity_pools=equal_liquidity_pools,
            structure_events=structure_events,
            fair_value_gaps=fair_value_gaps,
            fair_value_gap_transitions=fair_value_gap_transitions,
            fair_value_gap_snapshots=fair_value_gap_snapshots,
            observations=observations,
        )
        if recovered is not None and recovered.inducements:
            return InducementResult(
                status=SMCV2PrimitiveStatus.INVALID,
                inducements=recovered.inducements,
                snapshots=recovered.snapshots,
                reasons=(str(exc) or type(exc).__name__,),
                blocking_reasons=("determinably later malformed evidence",),
            )
        return InducementResult(
            status=SMCV2PrimitiveStatus.INVALID,
            reasons=(str(exc) or type(exc).__name__,),
            blocking_reasons=("malformed or contradictory supplied evidence",),
        )


def _recover_prior_evidence(
    *,
    instrument: object,
    timeframe: object,
    dealing_range_snapshots: object,
    liquidity_map_snapshots: object,
    equal_liquidity_pools: object,
    structure_events: object,
    fair_value_gaps: object,
    fair_value_gap_transitions: object,
    fair_value_gap_snapshots: object,
    observations: object,
) -> InducementResult | None:
    streams = {
        "dealing_range_snapshots": dealing_range_snapshots,
        "liquidity_map_snapshots": liquidity_map_snapshots,
        "equal_liquidity_pools": equal_liquidity_pools,
        "structure_events": structure_events,
        "fair_value_gaps": fair_value_gaps,
        "fair_value_gap_transitions": fair_value_gap_transitions,
        "fair_value_gap_snapshots": fair_value_gap_snapshots,
        "observations": observations,
    }
    if type(instrument) is not str or type(timeframe) is not str:
        return None
    if any(type(value) is not tuple for value in streams.values()):
        return None
    moments = sorted(
        {
            moment
            for values in streams.values()
            for item in values
            if (moment := _safe_effective_pair(item)) is not None
        },
        reverse=True,
    )
    for cutoff in moments:
        reduced: dict[str, tuple[object, ...]] = {}
        changed = False
        for name, values in streams.items():
            kept: list[object] = []
            for item in values:
                moment = _safe_effective_pair(item)
                if moment is None or moment < cutoff:
                    kept.append(item)
                else:
                    changed = True
            reduced[name] = tuple(kept)
        if not changed:
            continue
        result = analyze_inducements(
            instrument=instrument,
            timeframe=timeframe,
            dealing_range_snapshots=reduced["dealing_range_snapshots"],  # type: ignore[arg-type]
            liquidity_map_snapshots=reduced["liquidity_map_snapshots"],  # type: ignore[arg-type]
            equal_liquidity_pools=reduced["equal_liquidity_pools"],  # type: ignore[arg-type]
            structure_events=reduced["structure_events"],  # type: ignore[arg-type]
            fair_value_gaps=reduced["fair_value_gaps"],  # type: ignore[arg-type]
            fair_value_gap_transitions=reduced["fair_value_gap_transitions"],  # type: ignore[arg-type]
            fair_value_gap_snapshots=reduced["fair_value_gap_snapshots"],  # type: ignore[arg-type]
            observations=reduced["observations"],  # type: ignore[arg-type]
        )
        if result.status in (
            SMCV2PrimitiveStatus.VALID,
            SMCV2PrimitiveStatus.AMBIGUOUS,
        ):
            return result
    return None


def _safe_effective_pair(value: object) -> tuple[int, datetime] | None:
    try:
        if type(value) is InducementObservation:
            index, timestamp = value.index, value.timestamp
        elif type(value) is DealingRangeSnapshot:
            if value.transitions:
                index, timestamp = value.transitions[-1].index, value.transitions[-1].timestamp
            else:
                index = value.first_known_provenance.confirmation_index
                timestamp = value.first_known_provenance.confirmation_timestamp
        elif type(value) is LiquidityMapSnapshot:
            index, timestamp = value.index, value.timestamp
        elif type(value) is EqualLiquidityPool:
            moment = _pool_effective_moment(value)
            index, timestamp = moment.index, moment.timestamp
        elif type(value) is DealingRangeStructureEvent:
            index = value.provenance.confirmation_index
            timestamp = value.provenance.confirmation_timestamp
        elif type(value) is FairValueGap:
            index, timestamp = value.formation_end_index, value.formation_end_timestamp
        elif type(value) in (FairValueGapTransition, FairValueGapSnapshot):
            index, timestamp = value.index, value.timestamp
        else:
            index, timestamp = value.index, value.timestamp  # type: ignore[attr-defined]
        if type(index) is not int or index < 0:
            return None
        return index, _timestamp(timestamp, "effective timestamp")
    except (AttributeError, TypeError, ValueError, OverflowError, IndexError, KeyError):
        return None


def _analyze_valid(
    *,
    instrument: str,
    timeframe: str,
    ranges: tuple[DealingRangeSnapshot, ...],
    maps: tuple[LiquidityMapSnapshot, ...],
    pools: tuple[EqualLiquidityPool, ...],
    events: tuple[DealingRangeStructureEvent, ...],
    gaps: tuple[FairValueGap, ...],
    gap_transitions: tuple[FairValueGapTransition, ...],
    gap_snapshots: tuple[FairValueGapSnapshot, ...],
    observations: tuple[InducementObservation, ...],
) -> InducementResult:
    observation_positions = {item.index: position for position, item in enumerate(observations)}
    pool_by_lineage: dict[str, list[EqualLiquidityPool]] = {}
    for pool in pools:
        pool_by_lineage.setdefault(pool.lineage_id, []).append(pool)
    sweeps: list[_Sweep] = []
    for lineage, revisions in pool_by_lineage.items():
        for position, pool in enumerate(revisions):
            if pool.lifecycle_state is not SMCV2LifecycleState.SWEPT:
                continue
            if position == 0:
                raise ValueError("SWEPT pool is missing its prior ACTIVE revision")
            active = revisions[position - 1]
            if active.lifecycle_state is not SMCV2LifecycleState.ACTIVE:
                raise ValueError("SWEPT pool must immediately extend an ACTIVE revision")
            if pool.lifecycle_events[:-1] != active.lifecycle_events:
                raise ValueError("pool lifecycle history is not an immutable prefix")
            lifecycle = pool.lifecycle_events[-1]
            if (
                lifecycle.from_state is not SMCV2LifecycleState.ACTIVE
                or lifecycle.to_state is not SMCV2LifecycleState.SWEPT
            ):
                raise ValueError("pool terminal event is not ACTIVE to SWEPT")
            observation = _observation_at(observations, lifecycle.index, lifecycle.timestamp)
            obs_position = observation_positions[observation.index]
            latest_member_confirmation = active.first_known_provenance.confirmation_index
            if observation.index <= latest_member_confirmation:
                raise ValueError("formation/member observation cannot sweep its own pool")
            direction = (
                SMCV2Direction.BULLISH
                if pool.side is EqualLiquiditySide.LOW
                else SMCV2Direction.BEARISH
            )
            qualifies = (
                observation.low_tick <= pool.lower_tick - 1
                and observation.close_tick >= pool.lower_tick
                if direction is SMCV2Direction.BULLISH
                else observation.high_tick >= pool.upper_tick + 1
                and observation.close_tick <= pool.upper_tick
            )
            if not qualifies:
                raise ValueError("SWEPT lifecycle contradicts observation geometry")
            try:
                active_range = _latest_range_before(ranges, observation, direction, pool)
                map_snapshot, internal, external = _latest_map_before(
                    maps, observation, direction, pool, active_range
                )
            except _NoCandidate:
                continue
            sweeps.append(
                _Sweep(
                    direction=direction,
                    active_range=active_range,
                    map_snapshot=map_snapshot,
                    external_target=external,
                    internal_classification=internal,
                    active_pool=active,
                    swept_pool=pool,
                    observation=observation,
                    observation_position=obs_position,
                )
            )
        latest = revisions[-1]
        if latest.lifecycle_state is SMCV2LifecycleState.ACTIVE:
            formation = _pool_effective_moment(latest)
            direction = (
                SMCV2Direction.BULLISH
                if latest.side is EqualLiquiditySide.LOW
                else SMCV2Direction.BEARISH
            )
            for observation in observations:
                if (observation.index, observation.timestamp) <= (
                    formation.index,
                    formation.timestamp,
                ):
                    continue
                qualifies = (
                    observation.low_tick <= latest.lower_tick - 1
                    and observation.close_tick >= latest.lower_tick
                    if direction is SMCV2Direction.BULLISH
                    else observation.high_tick >= latest.upper_tick + 1
                    and observation.close_tick <= latest.upper_tick
                )
                if qualifies:
                    raise ValueError(
                        "qualifying sweep observation lacks required SWEPT lifecycle evidence"
                    )
    if not sweeps:
        return InducementResult(
            status=SMCV2PrimitiveStatus.NONE,
            reasons=("no qualifying internal-liquidity sweep was supplied",),
        )
    emitted: list[Inducement] = []
    snapshots: list[InducementSnapshot] = []
    pending = False
    candidates_by_confirmation: dict[tuple[int, datetime], list[Inducement]] = {}
    for sweep in sweeps:
        eligible_positions = range(
            sweep.observation_position + 1,
            min(sweep.observation_position + 4, len(observations)),
        )
        chosen: tuple[DealingRangeStructureEvent, FairValueGap, int] | None = None
        for offset, obs_position in enumerate(eligible_positions, start=1):
            observation = observations[obs_position]
            matched_events = tuple(
                event
                for event in events
                if event.direction is sweep.direction
                and event.provenance.confirmation_index == observation.index
                and _timestamp(event.provenance.confirmation_timestamp, "event timestamp")
                == observation.timestamp
            )
            if len(matched_events) > 1:
                raise ValueError("multiple same-direction events occupy one confirmation group")
            if not matched_events:
                continue
            event = matched_events[0]
            matched_gaps = tuple(
                gap
                for gap in gaps
                if gap.direction is sweep.direction
                and gap.formation_end_index == observation.index
                and _timestamp(gap.formation_end_timestamp, "gap timestamp")
                == observation.timestamp
                and gap.structure_event_id == event.event_id
                and gap.structure_event_type is event.event_type
            )
            if len(matched_gaps) != 1:
                if not matched_gaps:
                    continue
                raise ValueError("confirmation event has duplicate or forked linked FVGs")
            gap = matched_gaps[0]
            _validate_event_gap_binding(event, gap)
            _validate_gap_formation_history(gap, gap_transitions, gap_snapshots)
            try:
                _validate_retention(sweep, observation, ranges, maps, pools)
            except _NoCandidate:
                continue
            chosen = event, gap, offset
            break
        if chosen is None:
            if len(observations) - sweep.observation_position - 1 < 3:
                pending = True
            continue
        event, gap, offset = chosen
        item_id = make_inducement_id(
            identity_kind="INDUCEMENT",
            instrument=instrument,
            timeframe=timeframe,
            direction=sweep.direction,
            active_range_lineage_id=sweep.active_range.lineage_id,
            active_range_snapshot_id=sweep.active_range.snapshot_id,
            liquidity_map_snapshot_id=sweep.map_snapshot.snapshot_id,
            external_target_classification_id=sweep.external_target.classification_id,
            internal_pool_classification_id=sweep.internal_classification.classification_id,
            internal_pool_id=sweep.active_pool.lineage_id,
            sweep_index=sweep.observation.index,
            sweep_timestamp=sweep.observation.timestamp,
            sweep_extreme_tick=(
                sweep.observation.low_tick
                if sweep.direction is SMCV2Direction.BULLISH
                else sweep.observation.high_tick
            ),
            reclaim_close_tick=sweep.observation.close_tick,
            structure_event_id=event.event_id,
            structure_event_type=event.event_type,
            confirmation_index=event.provenance.confirmation_index,
            confirmation_timestamp=event.provenance.confirmation_timestamp,
            confirmation_offset_bars=offset,
            fair_value_gap_id=gap.gap_id,
            displacement_id=gap.displacement_id,
        )
        item = Inducement(
            inducement_id=item_id,
            direction=sweep.direction,
            active_range_lineage_id=sweep.active_range.lineage_id or "",
            active_range_snapshot_id=sweep.active_range.snapshot_id,
            liquidity_map_snapshot_id=sweep.map_snapshot.snapshot_id,
            external_target_classification_id=sweep.external_target.classification_id,
            internal_pool_classification_id=sweep.internal_classification.classification_id,
            internal_pool_id=sweep.active_pool.lineage_id,
            sweep_index=sweep.observation.index,
            sweep_timestamp=sweep.observation.timestamp,
            sweep_extreme_tick=(
                sweep.observation.low_tick
                if sweep.direction is SMCV2Direction.BULLISH
                else sweep.observation.high_tick
            ),
            reclaim_close_tick=sweep.observation.close_tick,
            structure_event_id=event.event_id,
            structure_event_type=event.event_type,
            confirmation_index=event.provenance.confirmation_index,
            confirmation_timestamp=_timestamp(
                event.provenance.confirmation_timestamp, "confirmation_timestamp"
            ),
            confirmation_offset_bars=offset,
            fair_value_gap_id=gap.gap_id,
            displacement_id=gap.displacement_id or "",
        )
        candidates_by_confirmation.setdefault(
            (item.confirmation_index, item.confirmation_timestamp), []
        ).append(item)
    ordered_history: list[str] = []
    for moment in sorted(candidates_by_confirmation):
        group = candidates_by_confirmation[moment]
        directions = {item.direction for item in group}
        if len(directions) > 1:
            return InducementResult(
                status=SMCV2PrimitiveStatus.AMBIGUOUS,
                inducements=tuple(emitted),
                snapshots=tuple(snapshots),
                reasons=("opposing valid inducement sequences share one confirmation group",),
                blocking_reasons=("same-group directional ambiguity",),
            )
        group.sort(
            key=lambda item: (
                item.confirmation_index,
                item.confirmation_timestamp,
                item.direction.value,
                item.sweep_index,
                item.internal_pool_id,
                item.inducement_id,
            )
        )
        emitted.extend(group)
        ordered_history.extend(item.inducement_id for item in group)
        snapshot_id = make_inducement_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            effective_index=moment[0],
            effective_timestamp=moment[1],
            inducement_ids=tuple(ordered_history),
        )
        snapshots.append(
            InducementSnapshot(
                snapshot_id=snapshot_id,
                index=moment[0],
                timestamp=moment[1],
                inducement_ids=tuple(ordered_history),
            )
        )
    if pending:
        return InducementResult(
            status=SMCV2PrimitiveStatus.UNKNOWN,
            inducements=tuple(emitted),
            snapshots=tuple(snapshots),
            reasons=("a swept pool has a truncated confirmation horizon",),
            blocking_reasons=("next three closed bars are incomplete",),
        )
    if emitted:
        return InducementResult(
            status=SMCV2PrimitiveStatus.VALID,
            inducements=tuple(emitted),
            snapshots=tuple(snapshots),
            reasons=("one or more complete inducement sequences were confirmed",),
        )
    return InducementResult(
        status=SMCV2PrimitiveStatus.NONE,
        reasons=("complete evidence contains no confirmed inducement sequence",),
    )


def _validate_observations(
    values: tuple[InducementObservation, ...],
) -> tuple[InducementObservation, ...]:
    normalized: list[InducementObservation] = []
    previous_index = -1
    previous_timestamp: datetime | None = None
    for value in values:
        if type(value) is not InducementObservation:
            raise ValueError("observations contain a malformed element")
        _nonnegative(value.index, "observation.index")
        timestamp = _timestamp(value.timestamp, "observation.timestamp")
        for name in ("open_tick", "high_tick", "low_tick", "close_tick"):
            _tick(getattr(value, name), f"observation.{name}")
        if type(value.is_closed) is not bool or not value.is_closed:
            raise ValueError("observations must be fully closed")
        if value.low_tick > value.high_tick:
            raise ValueError("observation low exceeds high")
        if not (
            value.low_tick <= value.open_tick <= value.high_tick
            and value.low_tick <= value.close_tick <= value.high_tick
        ):
            raise ValueError("observation OHLC geometry is invalid")
        if value.index <= previous_index:
            raise ValueError("observation indices must be strictly increasing")
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            raise ValueError("observation timestamps must be strictly increasing")
        previous_index = value.index
        previous_timestamp = timestamp
        normalized.append(_replace_observation_timestamp(value, timestamp))
    return tuple(normalized)


def _observation_prefix(
    values: tuple[InducementObservation, ...] | None,
) -> tuple[tuple[InducementObservation, ...], object | None]:
    if type(values) is not tuple:
        return (), None
    prefix: tuple[InducementObservation, ...] = ()
    for position, value in enumerate(values):
        try:
            prefix = _validate_observations(values[: position + 1])
        except (AttributeError, TypeError, ValueError, OverflowError):
            return _validate_observations(values[:position]), value
    return prefix, None


def _has_strictly_later_determinable_moment(
    value: object | None,
    prior: InducementObservation,
) -> bool:
    if value is None:
        return False
    try:
        index = value.index
        timestamp = _timestamp(value.timestamp, "malformed observation timestamp")
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False
    return (
        type(index) is int
        and index >= 0
        and (index, timestamp) > (prior.index, prior.timestamp)
    )


def _replace_observation_timestamp(
    value: InducementObservation,
    timestamp: datetime,
) -> InducementObservation:
    return InducementObservation(
        index=value.index,
        timestamp=timestamp,
        open_tick=value.open_tick,
        high_tick=value.high_tick,
        low_tick=value.low_tick,
        close_tick=value.close_tick,
        is_closed=value.is_closed,
    )


def _validate_ranges(
    values: tuple[DealingRangeSnapshot, ...],
    instrument: str,
    timeframe: str,
) -> tuple[DealingRangeSnapshot, ...]:
    previous: tuple[int, datetime] | None = None
    for value in values:
        if type(value) is not DealingRangeSnapshot:
            raise ValueError("dealing_range_snapshots contain a malformed element")
        if value.kind is not DealingRangeKind.EXTERNAL:
            raise ValueError("only EXTERNAL ranges are eligible")
        if value.direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("range direction is invalid")
        _hash_value(value.snapshot_id, "range.snapshot_id")
        _hash_tuple(value.source_swing_ids, "range.source_swing_ids", allow_empty=False)
        _index_tuple(value.source_indices, "range.source_indices", allow_empty=False)
        if len(value.source_swing_ids) != len(value.source_indices):
            raise ValueError("range source tuple lengths differ")
        _tick(value.low_tick, "range.low_tick")
        _tick(value.high_tick, "range.high_tick")
        if value.low_tick >= value.high_tick:
            raise ValueError("range boundaries are invalid")
        if (
            type(value.midpoint_tick) is not Decimal
            or value.midpoint_tick * 2 != Decimal(value.low_tick + value.high_tick)
        ):
            raise ValueError("range midpoint is invalid")
        if value.lineage_id is None or value.protected_swing_id is None or value.construction_event_id is None:
            raise ValueError("range canonical identity context is missing")
        for name, item in (
            ("range.lineage_id", value.lineage_id),
            ("range.protected_swing_id", value.protected_swing_id),
            ("range.construction_event_id", value.construction_event_id),
        ):
            _hash_value(item, name)
        if (
            type(value.transitions) is not tuple
            or type(value.transition_ids) is not tuple
            or not value.transitions
        ):
            raise ValueError("range transition history must be exact tuples")
        if tuple(item.transition_id for item in value.transitions) != value.transition_ids:
            raise ValueError("range transition IDs do not match history")
        prior_state: DealingRangeState | None = None
        prior_transition_moment: tuple[int, datetime] | None = None
        for transition in value.transitions:
            if type(transition) is not DealingRangeTransition:
                raise ValueError("range transition is malformed")
            if transition.lineage_id != value.lineage_id or transition.from_state is not prior_state:
                raise ValueError("range transition history is not a canonical state chain")
            transition_moment = (
                transition.index,
                _timestamp(transition.timestamp, "range transition timestamp"),
            )
            if (
                prior_transition_moment is not None
                and transition_moment <= prior_transition_moment
            ):
                raise ValueError("range transition moments must be strictly increasing")
            expected_transition = make_dealing_range_id(
                identity_kind="TRANSITION",
                instrument=instrument,
                timeframe=timeframe,
                direction=value.direction,
                source_indices=(transition.index,),
                lineage_id=value.lineage_id,
                transition_from_state=transition.from_state,
                transition_to_state=transition.to_state,
                transition_index=transition.index,
                transition_timestamp=transition.timestamp,
                transition_reason=transition.reason,
                related_event_id=transition.related_event_id,
                replacement_lineage_id=transition.replacement_lineage_id,
            )
            if expected_transition != transition.transition_id:
                raise ValueError("range transition identity mismatch")
            prior_state = transition.to_state
            prior_transition_moment = transition_moment
        if prior_state is not value.state:
            raise ValueError("range state does not match final transition")
        expected_snapshot = make_dealing_range_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=value.direction,
            source_indices=value.source_indices,
            swing_ids=value.source_swing_ids,
            boundaries=SMCV2TickRange(value.low_tick, value.high_tick),
            lineage_id=value.lineage_id,
            construction_event_id=value.construction_event_id,
            range_kind=value.kind,
            state=value.state,
            transition_ids=value.transition_ids,
            replacement_lineage_id=value.replacement_lineage_id,
        )
        if expected_snapshot != value.snapshot_id:
            raise ValueError("range snapshot identity mismatch")
        _provenance_moment(value.first_known_provenance, "range provenance")
        moment = _range_effective_moment(value)
        current = (moment.index, moment.timestamp)
        if previous is not None and current < previous:
            raise ValueError("range snapshots are not in causal order")
        previous = current
    return values


def _validate_pools(
    values: tuple[EqualLiquidityPool, ...],
    instrument: str,
    timeframe: str,
) -> tuple[EqualLiquidityPool, ...]:
    prior_by_lineage: dict[str, EqualLiquidityPool] = {}
    previous_moment: tuple[int, datetime] | None = None
    for value in values:
        if type(value) is not EqualLiquidityPool:
            raise ValueError("equal_liquidity_pools contain a malformed element")
        if value.side not in (EqualLiquiditySide.HIGH, EqualLiquiditySide.LOW):
            raise ValueError("pool side is invalid")
        _hash_value(value.lineage_id, "pool.lineage_id")
        _hash_value(value.snapshot_id, "pool.snapshot_id")
        _hash_tuple(value.member_swing_ids, "pool.member_swing_ids", allow_empty=False)
        _index_tuple(value.source_indices, "pool.source_indices", allow_empty=False)
        if len(value.member_swing_ids) != len(value.source_indices) or len(value.source_indices) < 2:
            raise ValueError("pool source tuple lengths are invalid")
        for name in ("reference_tick", "lower_tick", "upper_tick"):
            _tick(getattr(value, name), f"pool.{name}")
        if not value.lower_tick <= value.reference_tick <= value.upper_tick:
            raise ValueError("pool band is invalid")
        _provenance_moment(value.first_known_provenance, "pool provenance")
        if type(value.lifecycle_events) is not tuple or not value.lifecycle_events:
            raise ValueError("pool lifecycle history is incomplete")
        _validate_pool_lifecycle(value.lifecycle_events)
        if value.lifecycle_events[-1].to_state is not value.lifecycle_state:
            raise ValueError("pool lifecycle state mismatches history")
        expected = make_equal_liquidity_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            side=value.side,
            source_indices=value.source_indices,
            swing_ids=value.member_swing_ids,
            reference_tick=value.reference_tick,
            lower_tick=value.lower_tick,
            upper_tick=value.upper_tick,
            lineage_id=value.lineage_id,
            lifecycle_state=value.lifecycle_state,
        )
        if expected != value.snapshot_id:
            raise ValueError("pool snapshot identity mismatch")
        prior = prior_by_lineage.get(value.lineage_id)
        if prior is not None:
            if value.member_swing_ids[: len(prior.member_swing_ids)] != prior.member_swing_ids:
                raise ValueError("pool member history is not a prefix extension")
            if value.source_indices[: len(prior.source_indices)] != prior.source_indices:
                raise ValueError("pool source history is not a prefix extension")
            if value.lifecycle_events[: len(prior.lifecycle_events)] != prior.lifecycle_events:
                raise ValueError("pool lifecycle history is not a prefix extension")
        prior_by_lineage[value.lineage_id] = value
        effective = _pool_effective_moment(value)
        current = (effective.index, effective.timestamp)
        if previous_moment is not None and current < previous_moment:
            raise ValueError("pool revisions are not in causal order")
        previous_moment = current
    return values


def _validate_pool_lifecycle(events: tuple[SMCV2LifecycleEvent, ...]) -> None:
    previous_state: SMCV2LifecycleState | None = None
    previous_moment: tuple[int, datetime] | None = None
    for position, event in enumerate(events):
        if type(event) is not SMCV2LifecycleEvent:
            raise ValueError("pool lifecycle event is malformed")
        if event.from_state is not previous_state:
            raise ValueError("pool lifecycle chain is broken")
        if position == 0 and (
            event.from_state is not None
            or event.to_state is not SMCV2LifecycleState.ACTIVE
        ):
            raise ValueError("pool lifecycle must begin with None to ACTIVE")
        if position > 0 and (
            event.from_state is not SMCV2LifecycleState.ACTIVE
            or event.to_state
            not in (SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN)
        ):
            raise ValueError("pool lifecycle state is invalid")
        if position > 1:
            raise ValueError("terminal pool lifecycle cannot transition again")
        _nonnegative(event.index, "pool lifecycle index")
        timestamp = _timestamp(event.timestamp, "pool lifecycle timestamp")
        current = (event.index, timestamp)
        if previous_moment is not None and current <= previous_moment:
            raise ValueError("pool lifecycle moments must be strictly increasing")
        previous_state = event.to_state
        previous_moment = current


def _validate_maps(
    values: tuple[LiquidityMapSnapshot, ...],
    instrument: str,
    timeframe: str,
) -> tuple[LiquidityMapSnapshot, ...]:
    previous: tuple[int, datetime] | None = None
    for value in values:
        if type(value) is not LiquidityMapSnapshot:
            raise ValueError("liquidity_map_snapshots contain a malformed element")
        for name, item in (
            ("map.map_id", value.map_id),
            ("map.snapshot_id", value.snapshot_id),
            ("map.active_range_lineage_id", value.active_range_lineage_id),
            ("map.active_range_snapshot_id", value.active_range_snapshot_id),
        ):
            _hash_value(item, name)
        _nonnegative(value.index, "map.index")
        timestamp = _timestamp(value.timestamp, "map.timestamp")
        if type(value.classifications) is not tuple or type(value.classification_ids) is not tuple:
            raise ValueError("map classifications must be exact tuples")
        if tuple(item.classification_id for item in value.classifications) != value.classification_ids:
            raise ValueError("map classification IDs mismatch")
        if len(set(value.classification_ids)) != len(value.classification_ids):
            raise ValueError("map classification IDs must be unique")
        for item in value.classifications:
            _validate_classification(
                item,
                value.active_range_lineage_id,
                instrument,
                timeframe,
            )
        if type(value.reclassifications) is not tuple or type(value.reclassification_ids) is not tuple:
            raise ValueError("map reclassifications must be exact tuples")
        if tuple(item.reclassification_id for item in value.reclassifications) != value.reclassification_ids:
            raise ValueError("map reclassification IDs mismatch")
        if len(set(value.reclassification_ids)) != len(value.reclassification_ids):
            raise ValueError("map reclassification IDs must be unique")
        for item in value.reclassifications:
            if type(item) is not LiquidityReclassification:
                raise ValueError("map reclassification is malformed")
            expected_reclassification = make_liquidity_map_id(
                identity_kind="RECLASSIFICATION",
                instrument=instrument,
                timeframe=timeframe,
                active_range_lineage_id=value.active_range_lineage_id,
                source_kind=item.source_kind,
                source_id=item.source_id,
                side=item.side,
                prior_classification_id=item.prior_classification_id,
                new_classification_id=item.new_classification_id,
                event_index=item.index,
                event_timestamp=item.timestamp,
                from_scope=item.from_scope,
                to_scope=item.to_scope,
                reason=item.reason,
            )
            if expected_reclassification != item.reclassification_id:
                raise ValueError("map reclassification identity mismatch")
        expected_map = make_liquidity_map_id(
            identity_kind="MAP",
            instrument=instrument,
            timeframe=timeframe,
            active_range_lineage_id=value.active_range_lineage_id,
        )
        if expected_map != value.map_id:
            raise ValueError("map identity mismatch")
        expected_snapshot = make_liquidity_map_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            active_range_lineage_id=value.active_range_lineage_id,
            active_range_snapshot_id=value.active_range_snapshot_id,
            classification_ids=value.classification_ids,
            reclassification_ids=value.reclassification_ids,
            event_index=value.index,
            event_timestamp=timestamp,
        )
        if expected_snapshot != value.snapshot_id:
            raise ValueError("map snapshot identity mismatch")
        current = (value.index, timestamp)
        if previous is not None and current < previous:
            raise ValueError("map snapshots are not in causal order")
        previous = current
    return values


def _validate_classification(
    value: LiquidityClassification,
    lineage_id: str,
    instrument: str,
    timeframe: str,
) -> None:
    if type(value) is not LiquidityClassification:
        raise ValueError("map classification is malformed")
    if value.active_range_lineage_id != lineage_id:
        raise ValueError("classification active-range lineage mismatch")
    _hash_value(value.classification_id, "classification.classification_id")
    _hash_value(value.source_id, "classification.source_id")
    _index_tuple(value.source_indices, "classification.source_indices", allow_empty=False)
    if type(value.boundaries) is not SMCV2TickRange:
        raise ValueError("classification boundaries are malformed")
    expected = make_liquidity_map_id(
        identity_kind="CLASSIFICATION",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=lineage_id,
        source_indices=value.source_indices,
        source_kind=value.source_kind,
        source_id=value.source_id,
        side=value.side,
        scope=value.scope,
        boundaries=value.boundaries,
        active_range_snapshot_id=value.active_range_snapshot_id,
        version=value.version,
        prior_classification_id=value.prior_classification_id,
        event_index=value.classification_index,
        event_timestamp=value.classification_timestamp,
    )
    if expected != value.classification_id:
        raise ValueError("classification identity mismatch")


def _validate_events(
    values: tuple[DealingRangeStructureEvent, ...],
    observations: dict[int, InducementObservation] | None,
) -> tuple[DealingRangeStructureEvent, ...]:
    previous: tuple[int, datetime, str, str, str] | None = None
    per_group: set[tuple[int, datetime, SMCV2Direction]] = set()
    for value in values:
        if type(value) is not DealingRangeStructureEvent:
            raise ValueError("structure_events contain a malformed element")
        if value.direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
            raise ValueError("event direction is invalid")
        if value.event_type not in (DealingRangeEventType.BOS, DealingRangeEventType.CHOCH):
            raise ValueError("event type is invalid")
        _hash_value(value.event_id, "event.event_id")
        _hash_value(value.broken_swing_id, "event.broken_swing_id")
        moment = _provenance_moment(value.provenance, "event provenance")
        if observations is not None:
            _reconcile_provenance(value.provenance, observations, "event provenance")
        key = (
            moment.index,
            moment.timestamp,
            value.direction.value,
            value.event_type.value,
            value.event_id,
        )
        if previous is not None and key <= previous:
            raise ValueError("structure events are not strictly ordered")
        group_key = (moment.index, moment.timestamp, value.direction)
        if group_key in per_group:
            raise ValueError("duplicate same-direction confirmation event")
        per_group.add(group_key)
        previous = key
    return values


def _validate_partial_gap_history(
    transitions: tuple[FairValueGapTransition, ...],
    snapshots: tuple[FairValueGapSnapshot, ...],
    instrument: str,
    timeframe: str,
    *,
    transitions_are_complete: bool,
    snapshots_are_complete: bool,
) -> None:
    transition_by_id: dict[str, FairValueGapTransition] = {}
    transitions_by_gap: dict[str, list[FairValueGapTransition]] = {}
    previous_transition_moment: tuple[int, datetime] | None = None
    for transition in transitions:
        if type(transition) is not FairValueGapTransition:
            raise ValueError("FVG transition is malformed")
        _hash_value(transition.transition_id, "transition.transition_id")
        _hash_value(transition.gap_id, "transition.gap_id")
        _validate_partial_fvg_transition_edge(
            transition.from_state,
            transition.to_state,
            transition.reason,
        )
        _nonnegative(transition.index, "transition.index")
        timestamp = _timestamp(transition.timestamp, "transition.timestamp")
        moment = (transition.index, timestamp)
        if (
            previous_transition_moment is not None
            and moment < previous_transition_moment
        ):
            raise ValueError("FVG transitions are not in causal order")
        if transition.transition_id in transition_by_id:
            raise ValueError("FVG transition identity is duplicated")
        previous_transition_moment = moment
        transition_by_id[transition.transition_id] = transition
        transitions_by_gap.setdefault(transition.gap_id, []).append(transition)

    for gap_history in transitions_by_gap.values():
        prior_state: FairValueGapState | None = None
        prior_moment: tuple[int, datetime] | None = None
        for transition in gap_history:
            moment = (
                transition.index,
                _timestamp(transition.timestamp, "transition.timestamp"),
            )
            if transition.from_state is not prior_state:
                raise ValueError("FVG transition state chain is broken")
            if prior_moment is not None and moment <= prior_moment:
                raise ValueError("per-gap FVG transitions must be strictly later")
            prior_state = transition.to_state
            prior_moment = moment

    snapshot_by_id: dict[str, FairValueGapSnapshot] = {}
    snapshots_by_gap: dict[str, list[FairValueGapSnapshot]] = {}
    previous_snapshot_moment: tuple[int, datetime] | None = None
    for snapshot in snapshots:
        if type(snapshot) is not FairValueGapSnapshot:
            raise ValueError("FVG snapshot is malformed")
        _hash_value(snapshot.snapshot_id, "snapshot.snapshot_id")
        _hash_value(snapshot.gap_id, "snapshot.gap_id")
        if snapshot.direction not in (
            SMCV2Direction.BULLISH,
            SMCV2Direction.BEARISH,
        ):
            raise ValueError("FVG snapshot direction is invalid")
        if not isinstance(snapshot.state, FairValueGapState):
            raise ValueError("FVG snapshot state is invalid")
        _nonnegative(snapshot.index, "snapshot.index")
        timestamp = _timestamp(snapshot.timestamp, "snapshot.timestamp")
        _hash_tuple(snapshot.transition_ids, "snapshot.transition_ids", allow_empty=False)
        if len(set(snapshot.transition_ids)) != len(snapshot.transition_ids):
            raise ValueError("FVG snapshot transition history is duplicated")
        expected_snapshot_id = make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=snapshot.direction,
            gap_id=snapshot.gap_id,
            effective_index=snapshot.index,
            effective_timestamp=timestamp,
            state=snapshot.state,
            transition_ids=snapshot.transition_ids,
        )
        if expected_snapshot_id != snapshot.snapshot_id:
            raise ValueError("FVG snapshot identity mismatch")
        moment = (snapshot.index, timestamp)
        if previous_snapshot_moment is not None and moment < previous_snapshot_moment:
            raise ValueError("FVG snapshots are not in causal order")
        if snapshot.snapshot_id in snapshot_by_id:
            raise ValueError("FVG snapshot identity is duplicated")
        previous_snapshot_moment = moment
        snapshot_by_id[snapshot.snapshot_id] = snapshot
        snapshots_by_gap.setdefault(snapshot.gap_id, []).append(snapshot)

    for gap_snapshots in snapshots_by_gap.values():
        prior_ids: tuple[str, ...] = ()
        prior_moment: tuple[int, datetime] | None = None
        prior_direction: SMCV2Direction | None = None
        for snapshot in gap_snapshots:
            moment = (
                snapshot.index,
                _timestamp(snapshot.timestamp, "snapshot.timestamp"),
            )
            if prior_moment is not None and moment <= prior_moment:
                raise ValueError("per-gap FVG snapshots must be strictly later")
            if prior_ids and (
                len(snapshot.transition_ids) <= len(prior_ids)
                or snapshot.transition_ids[: len(prior_ids)] != prior_ids
            ):
                raise ValueError("FVG snapshot history is not a causal prefix extension")
            if prior_direction is not None and snapshot.direction is not prior_direction:
                raise ValueError("FVG snapshot direction changed within one gap")
            prior_ids = snapshot.transition_ids
            prior_moment = moment
            prior_direction = snapshot.direction

    if transitions_are_complete and snapshots_are_complete:
        if len(transitions) != len(snapshots):
            raise ValueError("FVG transition/snapshot history is incomplete")
        if tuple(item.transition_id for item in transitions) != tuple(
            item.transition_ids[-1] for item in snapshots
        ):
            raise ValueError("FVG snapshot stream does not mirror transition order")
        for gap_id in set(transitions_by_gap) | set(snapshots_by_gap):
            gap_transitions = transitions_by_gap.get(gap_id, [])
            gap_snapshots = snapshots_by_gap.get(gap_id, [])
            if len(gap_transitions) != len(gap_snapshots):
                raise ValueError("per-gap FVG history is incomplete")
            ordered_ids: list[str] = []
            for transition, snapshot in zip(
                gap_transitions,
                gap_snapshots,
                strict=True,
            ):
                ordered_ids.append(transition.transition_id)
                if (
                    snapshot.transition_ids != tuple(ordered_ids)
                    or snapshot.state is not transition.to_state
                    or snapshot.index != transition.index
                    or _timestamp(snapshot.timestamp, "snapshot.timestamp")
                    != _timestamp(transition.timestamp, "transition.timestamp")
                ):
                    raise ValueError("FVG snapshot does not mirror transition history")


def _validate_partial_fvg_transition_edge(
    from_state: object,
    to_state: object,
    reason: object,
) -> None:
    if from_state is not None and not isinstance(from_state, FairValueGapState):
        raise ValueError("FVG transition from_state is invalid")
    if not isinstance(to_state, FairValueGapState):
        raise ValueError("FVG transition to_state is invalid")
    if type(reason) is not str:
        raise ValueError("FVG transition reason is invalid")
    if from_state is None:
        if to_state is not FairValueGapState.ACTIVE or reason != _FORMATION_REASON:
            raise ValueError("initial FVG transition is not canonical formation")
        return
    if to_state not in _FVG_ALLOWED_TARGETS[from_state]:
        raise ValueError("FVG transition is outside the locked lifecycle graph")
    if reason != _FVG_REASON_BY_STATE[to_state]:
        raise ValueError("FVG transition reason contradicts target state")


def _validate_gaps(
    gaps: tuple[FairValueGap, ...],
    transitions: tuple[FairValueGapTransition, ...],
    snapshots: tuple[FairValueGapSnapshot, ...],
    observations: dict[int, InducementObservation] | None,
    instrument: str,
    timeframe: str,
    *,
    history_is_complete: bool = True,
) -> tuple[
    tuple[FairValueGap, ...],
    tuple[FairValueGapTransition, ...],
    tuple[FairValueGapSnapshot, ...],
]:
    prior_gap_key: tuple[int, datetime, str, tuple[int, ...], str] | None = None
    by_gap: dict[str, FairValueGap] = {}
    gap_order: dict[str, int] = {}
    for gap in gaps:
        if type(gap) is not FairValueGap:
            raise ValueError("fair_value_gaps contain a malformed element")
        _hash_value(gap.gap_id, "gap.gap_id")
        if gap.displacement_id is None:
            raise ValueError("qualifying FVG requires displacement_id")
        _hash_value(gap.displacement_id, "gap.displacement_id")
        _hash_value(gap.structure_event_id, "gap.structure_event_id")
        _index_tuple(gap.source_indices, "gap.source_indices", allow_empty=False)
        if len(gap.source_indices) != 3 or type(gap.source_timestamps) is not tuple or len(gap.source_timestamps) != 3:
            raise ValueError("FVG source tuple must contain exactly three moments")
        if gap.source_indices[-1] != gap.formation_end_index:
            raise ValueError("FVG source sequence does not end at formation")
        normalized_times = tuple(
            _timestamp(item, "gap.source_timestamp") for item in gap.source_timestamps
        )
        if normalized_times[-1] != _timestamp(gap.formation_end_timestamp, "gap formation"):
            raise ValueError("FVG final source timestamp mismatches formation")
        if observations is not None:
            for index, timestamp in zip(
                gap.source_indices,
                normalized_times,
                strict=True,
            ):
                _observation_at_map(observations, index, timestamp)
        expected = make_fair_value_gap_id(
            identity_kind="GAP",
            instrument=instrument,
            timeframe=timeframe,
            direction=gap.direction,
            source_indices=gap.source_indices,
            source_timestamps=normalized_times,
            boundaries=SMCV2TickRange(gap.lower_tick, gap.upper_tick),
            midpoint_tick=gap.midpoint_tick,
            formation_end_index=gap.formation_end_index,
            formation_end_timestamp=gap.formation_end_timestamp,
            displacement_id=gap.displacement_id,
            structure_event_id=gap.structure_event_id,
            structure_event_type=gap.structure_event_type,
        )
        if expected != gap.gap_id:
            raise ValueError("FVG identity mismatch")
        key = (
            gap.formation_end_index,
            _timestamp(gap.formation_end_timestamp, "gap formation"),
            gap.direction.value,
            gap.source_indices,
            gap.gap_id,
        )
        if prior_gap_key is not None and key <= prior_gap_key:
            raise ValueError("FVGs are not in canonical causal order")
        prior_gap_key = key
        by_gap[gap.gap_id] = gap
        gap_order[gap.gap_id] = len(gap_order)
    previous_transition: tuple[int, datetime, int, int] | None = None
    transition_by_id: dict[str, FairValueGapTransition] = {}
    for transition in transitions:
        if type(transition) is not FairValueGapTransition:
            raise ValueError("FVG transition is malformed")
        gap = by_gap.get(transition.gap_id)
        if gap is None:
            raise ValueError("FVG transition has a dangling gap reference")
        expected = make_fair_value_gap_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=gap.direction,
            gap_id=gap.gap_id,
            from_state=transition.from_state,
            to_state=transition.to_state,
            effective_index=transition.index,
            effective_timestamp=transition.timestamp,
            reason=transition.reason,
        )
        if expected != transition.transition_id:
            raise ValueError("FVG transition identity mismatch")
        current = (
            transition.index,
            _timestamp(transition.timestamp, "FVG transition timestamp"),
        )
        formation = (
            gap.formation_end_index,
            _timestamp(gap.formation_end_timestamp, "FVG formation timestamp"),
        )
        if current < formation:
            raise ValueError("FVG transition precedes gap formation")
        causal_key = (
            current[0],
            current[1],
            1 if transition.from_state is None else 0,
            gap_order[gap.gap_id],
        )
        if previous_transition is not None and causal_key < previous_transition:
            raise ValueError("FVG transitions are not in causal order")
        previous_transition = causal_key
        transition_by_id[transition.transition_id] = transition
    previous_snapshot: tuple[int, datetime] | None = None
    for snapshot in snapshots:
        if type(snapshot) is not FairValueGapSnapshot:
            raise ValueError("FVG snapshot is malformed")
        gap = by_gap.get(snapshot.gap_id)
        if gap is None:
            raise ValueError("FVG snapshot has a dangling gap reference")
        _hash_tuple(snapshot.transition_ids, "FVG snapshot transition_ids", allow_empty=False)
        if history_is_complete and any(
            item not in transition_by_id for item in snapshot.transition_ids
        ):
            raise ValueError("FVG snapshot references an unknown transition")
        expected = make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=gap.direction,
            gap_id=gap.gap_id,
            effective_index=snapshot.index,
            effective_timestamp=snapshot.timestamp,
            state=snapshot.state,
            transition_ids=snapshot.transition_ids,
        )
        if expected != snapshot.snapshot_id:
            raise ValueError("FVG snapshot identity mismatch")
        final_transition = transition_by_id.get(snapshot.transition_ids[-1])
        if final_transition is not None:
            if (
                final_transition.gap_id != snapshot.gap_id
                or final_transition.index != snapshot.index
                or _timestamp(final_transition.timestamp, "transition timestamp")
                != _timestamp(snapshot.timestamp, "snapshot timestamp")
                or final_transition.to_state is not snapshot.state
            ):
                raise ValueError("FVG snapshot does not mirror its final transition")
        current = (
            snapshot.index,
            _timestamp(snapshot.timestamp, "FVG snapshot timestamp"),
        )
        if previous_snapshot is not None and current < previous_snapshot:
            raise ValueError("FVG snapshots are not in causal order")
        previous_snapshot = current
    if not history_is_complete:
        return gaps, transitions, snapshots
    if len(transitions) != len(snapshots):
        raise ValueError("FVG transition/snapshot history is incomplete")
    for transition, snapshot in zip(transitions, snapshots, strict=True):
        if (
            snapshot.gap_id != transition.gap_id
            or snapshot.transition_ids[-1] != transition.transition_id
            or snapshot.index != transition.index
            or _timestamp(snapshot.timestamp, "FVG snapshot timestamp")
            != _timestamp(transition.timestamp, "FVG transition timestamp")
            or snapshot.state is not transition.to_state
        ):
            raise ValueError("FVG snapshot stream does not mirror transition order")
    for gap in gaps:
        gap_history = tuple(
            item for item in transitions if item.gap_id == gap.gap_id
        )
        gap_snapshots = tuple(
            item for item in snapshots if item.gap_id == gap.gap_id
        )
        if not gap_history or len(gap_snapshots) != len(gap_history):
            raise ValueError("FVG transition/snapshot history is incomplete")
        prior_state: FairValueGapState | None = None
        prior_moment: tuple[int, datetime] | None = None
        ordered_ids: list[str] = []
        for transition, snapshot in zip(
            gap_history, gap_snapshots, strict=True
        ):
            current = (
                transition.index,
                _timestamp(transition.timestamp, "FVG transition timestamp"),
            )
            if transition.from_state is not prior_state:
                raise ValueError("FVG transition state chain is broken")
            if prior_moment is not None and current <= prior_moment:
                raise ValueError("per-gap FVG transitions must be strictly later")
            ordered_ids.append(transition.transition_id)
            if snapshot.transition_ids != tuple(ordered_ids):
                raise ValueError("FVG snapshot history is not complete and ordered")
            if (
                snapshot.state is not transition.to_state
                or snapshot.index != transition.index
                or _timestamp(snapshot.timestamp, "FVG snapshot timestamp")
                != current[1]
            ):
                raise ValueError("FVG snapshot does not mirror transition history")
            prior_state = transition.to_state
            prior_moment = current
        first = gap_history[0]
        if (
            first.from_state is not None
            or first.to_state is not FairValueGapState.ACTIVE
            or first.reason != _FORMATION_REASON
            or first.index != gap.formation_end_index
            or _timestamp(first.timestamp, "FVG formation transition")
            != _timestamp(gap.formation_end_timestamp, "FVG formation")
        ):
            raise ValueError("FVG history lacks canonical formation transition")
    return gaps, transitions, snapshots


def _validate_cross_references(
    ranges: tuple[DealingRangeSnapshot, ...],
    pools: tuple[EqualLiquidityPool, ...],
    maps: tuple[LiquidityMapSnapshot, ...],
    events: tuple[DealingRangeStructureEvent, ...],
    gaps: tuple[FairValueGap, ...],
) -> None:
    range_pairs = {(item.lineage_id, item.snapshot_id) for item in ranges}
    pool_lineages = {item.lineage_id for item in pools}
    event_ids = {item.event_id for item in events}
    for snapshot in maps:
        if (
            snapshot.active_range_lineage_id,
            snapshot.active_range_snapshot_id,
        ) not in range_pairs:
            raise ValueError("map snapshot has a dangling active-range reference")
        for classification in snapshot.classifications:
            if (
                classification.source_kind
                is LiquiditySourceKind.EQUAL_LIQUIDITY_POOL
                and classification.source_id not in pool_lineages
            ):
                raise ValueError("map classification has a dangling pool reference")
    for gap in gaps:
        if gap.structure_event_id not in event_ids:
            raise ValueError("FVG has a dangling structure-event reference")


def _latest_range_before(
    ranges: tuple[DealingRangeSnapshot, ...],
    observation: InducementObservation,
    direction: SMCV2Direction,
    pool: EqualLiquidityPool,
) -> DealingRangeSnapshot:
    eligible = [
        item
        for item in ranges
        if item.direction is direction
        and item.kind is DealingRangeKind.EXTERNAL
        and _moment_le(_range_effective_moment(item), _Moment(observation.index, observation.timestamp))
    ]
    if not eligible:
        raise _NoCandidate("no active external range exists before sweep")
    latest = eligible[-1]
    if latest.state is not DealingRangeState.ACTIVE:
        raise _NoCandidate("latest external range is not ACTIVE")
    if not (latest.low_tick < pool.lower_tick <= pool.upper_tick < latest.high_tick):
        raise ValueError("internal pool is not strictly inside active range")
    return latest


def _latest_map_before(
    maps: tuple[LiquidityMapSnapshot, ...],
    observation: InducementObservation,
    direction: SMCV2Direction,
    pool: EqualLiquidityPool,
    active_range: DealingRangeSnapshot,
) -> tuple[LiquidityMapSnapshot, LiquidityClassification, LiquidityClassification]:
    eligible = [
        item
        for item in maps
        if item.active_range_lineage_id == active_range.lineage_id
        and (item.index, _timestamp(item.timestamp, "map timestamp"))
        < (observation.index, observation.timestamp)
    ]
    if not eligible:
        raise _NoCandidate("no pre-group Liquidity Map snapshot exists")
    snapshot = eligible[-1]
    if snapshot.active_range_snapshot_id != active_range.snapshot_id:
        raise ValueError("map snapshot does not bind the selected range revision")
    internal_side = (
        LiquiditySide.SELL_SIDE
        if direction is SMCV2Direction.BULLISH
        else LiquiditySide.BUY_SIDE
    )
    external_side = (
        LiquiditySide.BUY_SIDE
        if direction is SMCV2Direction.BULLISH
        else LiquiditySide.SELL_SIDE
    )
    internal = tuple(
        item
        for item in snapshot.classifications
        if item.source_kind is LiquiditySourceKind.EQUAL_LIQUIDITY_POOL
        and item.source_id == pool.lineage_id
        and item.side is internal_side
        and item.scope is LiquidityScope.INTERNAL
    )
    if len(internal) != 1:
        if not internal:
            raise _NoCandidate("internal pool classification is missing")
        raise ValueError("internal pool classification is ambiguous")
    targets = tuple(
        item
        for item in snapshot.classifications
        if item.side is external_side and item.scope is LiquidityScope.EXTERNAL
    )
    if not targets:
        raise _NoCandidate("external target classification is missing")
    if direction is SMCV2Direction.BULLISH:
        beyond = tuple(
            item
            for item in targets
            if item.boundaries.lower_tick > observation.close_tick
        )
        if not beyond:
            raise _NoCandidate("no bullish external target lies beyond reclaim close")
        external = min(
            beyond,
            key=lambda item: (item.boundaries.lower_tick, item.classification_id),
        )
    else:
        beyond = tuple(
            item
            for item in targets
            if item.boundaries.upper_tick < observation.close_tick
        )
        if not beyond:
            raise _NoCandidate("no bearish external target lies beyond reclaim close")
        external = max(
            beyond,
            key=lambda item: (item.boundaries.upper_tick, item.classification_id),
        )
    return snapshot, internal[0], external


def _validate_event_gap_binding(
    event: DealingRangeStructureEvent,
    gap: FairValueGap,
) -> None:
    event_sequence = tuple(
        zip(
            event.provenance.source_indices,
            tuple(
                _timestamp(item, "event source timestamp")
                for item in event.provenance.source_timestamps
            ),
            strict=True,
        )
    )
    gap_sequence = tuple(
        zip(
            gap.source_indices,
            tuple(
                _timestamp(item, "gap source timestamp")
                for item in gap.source_timestamps
            ),
            strict=True,
        )
    )
    shorter, longer = (
        (event_sequence, gap_sequence)
        if len(event_sequence) <= len(gap_sequence)
        else (gap_sequence, event_sequence)
    )
    if not shorter or longer[-len(shorter) :] != shorter:
        raise ValueError("event and FVG sources lack exact positional-suffix binding")
    if event_sequence[-1] != gap_sequence[-1]:
        raise ValueError("event and FVG sequences do not share confirmation moment")


def _validate_gap_formation_history(
    gap: FairValueGap,
    transitions: tuple[FairValueGapTransition, ...],
    snapshots: tuple[FairValueGapSnapshot, ...],
) -> None:
    matched_transitions = tuple(
        item
        for item in transitions
        if item.gap_id == gap.gap_id
        and item.index == gap.formation_end_index
        and _timestamp(item.timestamp, "transition timestamp")
        == _timestamp(gap.formation_end_timestamp, "gap formation")
    )
    matched_snapshots = tuple(
        item
        for item in snapshots
        if item.gap_id == gap.gap_id
        and item.index == gap.formation_end_index
        and _timestamp(item.timestamp, "snapshot timestamp")
        == _timestamp(gap.formation_end_timestamp, "gap formation")
    )
    if len(matched_transitions) != 1 or len(matched_snapshots) != 1:
        raise ValueError("FVG lacks exactly one formation transition and snapshot")
    transition = matched_transitions[0]
    snapshot = matched_snapshots[0]
    if (
        transition.from_state is not None
        or transition.to_state is not FairValueGapState.ACTIVE
        or transition.reason != _FORMATION_REASON
        or snapshot.state is not FairValueGapState.ACTIVE
        or snapshot.transition_ids != (transition.transition_id,)
    ):
        raise ValueError("FVG formation history is not canonical")


def _validate_retention(
    sweep: _Sweep,
    confirmation: InducementObservation,
    ranges: tuple[DealingRangeSnapshot, ...],
    maps: tuple[LiquidityMapSnapshot, ...],
    pools: tuple[EqualLiquidityPool, ...],
) -> None:
    later_ranges = [
        item
        for item in ranges
        if item.lineage_id == sweep.active_range.lineage_id
        and _moment_le(
            _range_effective_moment(item),
            _Moment(confirmation.index, confirmation.timestamp),
        )
    ]
    if later_ranges and later_ranges[-1].state is not DealingRangeState.ACTIVE:
        raise _NoCandidate("active external range terminated before confirmation")
    later_maps = [
        item
        for item in maps
        if item.active_range_lineage_id == sweep.active_range.lineage_id
        and (item.index, _timestamp(item.timestamp, "map timestamp"))
        <= (confirmation.index, confirmation.timestamp)
    ]
    if later_maps:
        latest_ids = later_maps[-1].classification_ids
        if sweep.external_target.classification_id not in latest_ids:
            raise ValueError("external target was not retained through confirmation")
    if (
        sweep.external_target.source_kind
        is LiquiditySourceKind.EQUAL_LIQUIDITY_POOL
    ):
        target_revisions = [
            item
            for item in pools
            if item.lineage_id == sweep.external_target.source_id
            and _moment_le(
                _pool_effective_moment(item),
                _Moment(confirmation.index, confirmation.timestamp),
            )
        ]
        if (
            not target_revisions
            or target_revisions[-1].lifecycle_state
            is not SMCV2LifecycleState.ACTIVE
        ):
            raise ValueError(
                "external equal-liquidity target did not remain ACTIVE"
            )


def _range_effective_moment(value: DealingRangeSnapshot) -> _Moment:
    if value.transitions:
        final = value.transitions[-1]
        return _Moment(final.index, _timestamp(final.timestamp, "range transition timestamp"))
    return _provenance_moment(value.first_known_provenance, "range provenance")


def _pool_effective_moment(value: EqualLiquidityPool) -> _Moment:
    latest_member = _provenance_moment(value.first_known_provenance, "pool provenance")
    lifecycle = value.lifecycle_events[-1]
    terminal = _Moment(
        lifecycle.index,
        _timestamp(lifecycle.timestamp, "pool lifecycle timestamp"),
    )
    return max((latest_member, terminal), key=lambda item: (item.index, item.timestamp))


def _provenance_moment(value: SMCV2EventProvenance, name: str) -> _Moment:
    if type(value) is not SMCV2EventProvenance:
        raise ValueError(f"{name} is malformed")
    _index_tuple(value.source_indices, f"{name}.source_indices", allow_empty=False)
    if type(value.source_timestamps) is not tuple or len(value.source_timestamps) != len(value.source_indices):
        raise ValueError(f"{name} source tuple lengths differ")
    normalized = tuple(
        _timestamp(item, f"{name}.source_timestamp")
        for item in value.source_timestamps
    )
    _nonnegative(value.confirmation_index, f"{name}.confirmation_index")
    confirmation = _timestamp(
        value.confirmation_timestamp, f"{name}.confirmation_timestamp"
    )
    if any(
        (index, timestamp) > (value.confirmation_index, confirmation)
        for index, timestamp in zip(value.source_indices, normalized, strict=True)
    ):
        raise ValueError(f"{name} source moment follows confirmation")
    return _Moment(value.confirmation_index, confirmation)


def _reconcile_provenance(
    value: SMCV2EventProvenance,
    observations: dict[int, InducementObservation],
    name: str,
) -> None:
    for index, timestamp in zip(
        value.source_indices, value.source_timestamps, strict=True
    ):
        _observation_at_map(
            observations,
            index,
            _timestamp(timestamp, f"{name}.source_timestamp"),
        )
    _observation_at_map(
        observations,
        value.confirmation_index,
        _timestamp(value.confirmation_timestamp, f"{name}.confirmation_timestamp"),
    )


def _observation_at(
    values: tuple[InducementObservation, ...],
    index: int,
    timestamp: datetime,
) -> InducementObservation:
    for value in values:
        if value.index == index:
            if value.timestamp != _timestamp(timestamp, "referenced timestamp"):
                raise ValueError("referenced observation timestamp mismatch")
            return value
    raise ValueError("referenced observation is missing")


def _observation_at_map(
    values: dict[int, InducementObservation],
    index: int,
    timestamp: datetime,
) -> InducementObservation:
    value = values.get(index)
    if value is None:
        raise ValueError("referenced observation is missing")
    if value.timestamp != timestamp:
        raise ValueError("referenced observation timestamp mismatch")
    return value


def _moment_le(left: _Moment, right: _Moment) -> bool:
    return (left.index, left.timestamp) <= (right.index, right.timestamp)


def _text(value: object, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _timestamp(value: object, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _timestamp_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _hash_value(value: object, name: str) -> None:
    if type(value) is not str or _HASH.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 hash")


def _hash_tuple(value: object, name: str, *, allow_empty: bool) -> None:
    if type(value) is not tuple or (not allow_empty and not value):
        raise ValueError(f"{name} must be an exact non-empty tuple")
    for item in value:
        _hash_value(item, name)


def _index_tuple(value: object, name: str, *, allow_empty: bool) -> None:
    if type(value) is not tuple or (not allow_empty and not value):
        raise ValueError(f"{name} must be an exact non-empty tuple")
    previous = -1
    for item in value:
        _nonnegative(item, name)
        if item <= previous:
            raise ValueError(f"{name} must be strictly increasing")
        previous = item


def _nonnegative(value: object, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative exact int")


def _tick(value: object, name: str) -> None:
    if type(value) is not int:
        raise ValueError(f"{name} must be an exact int")


__all__ = (
    "INDUCEMENT_DETECTOR_VERSION",
    "InducementObservation",
    "Inducement",
    "InducementSnapshot",
    "InducementResult",
    "make_inducement_id",
    "analyze_inducements",
)
