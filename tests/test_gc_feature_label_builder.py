from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import importlib.metadata
import inspect
import json
import sys
from typing import get_type_hints
from zoneinfo import ZoneInfo

import pytest

from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCSegmentPartition,
    make_gc_dataset_id,
)
from analysis.gc_feature_label_builder import (
    GC_AI_FEATURE_SCHEMA_ID,
    GC_AI_LABEL_HORIZON_BARS,
    GC_AI_LABEL_SCHEMA_ID,
    GC_FEATURE_LABEL_VERSION,
    GCFeatureLabelCandidateEvidence,
    GCFeatureLabelConfig,
    GCFeatureLabelIdentityKind,
    GCFeatureLabelManifest,
    GCFeatureLabelResult,
    GCFeatureRow,
    GCLabelOutcome,
    GCResearchLabel,
    build_gc_feature_labels,
    make_gc_feature_label_id,
)
from core.gc_chronological_backtest import GCChronologicalBar
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
from smc.equal_liquidity import EqualLiquidityPool, EqualLiquiditySide, make_equal_liquidity_id
from smc.fair_value_gap import (
    FairValueGapCandle,
    FairValueGapContextLink,
    FairValueGapState,
    analyze_fair_value_gaps,
    make_fair_value_gap_id,
)
from smc.inducement import InducementObservation, analyze_inducements, make_inducement_id
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneName,
    KillZoneObservation,
    KillZoneQuality,
    KillZoneSessionStatus,
    analyze_kill_zones,
)
from smc.liquidity_map import (
    LiquidityScope,
    LiquiditySide,
    analyze_liquidity_map,
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


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TRADE_DATE = date(2026, 7, 29)
CONTRACT = "GCQ26-COMEX"
INSTRUMENT = "GC"
TIMEFRAME = "5M"
CALENDAR_VERSION = "GC-FEATURE-LABEL-SYNTHETIC-1"
TZDATA_VERSION = importlib.metadata.version("tzdata")
SOURCE_ID = hashlib.sha256(b"synthetic-source").hexdigest()
COVERAGE_ID = hashlib.sha256(b"synthetic-coverage").hexdigest()
COVERAGE_DIGEST = hashlib.sha256(b"synthetic-coverage-digest").hexdigest()
BASE_INDEX = 161


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _timestamp_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _hash_payload(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _calendar() -> tuple[KillZoneCalendarEntry, ...]:
    return (
        KillZoneCalendarEntry(
            calendar_version=CALENDAR_VERSION,
            trade_date=TRADE_DATE,
            session_status=KillZoneSessionStatus.OPEN,
            session_open_timestamp=datetime.combine(
                TRADE_DATE - timedelta(days=1), time(18), tzinfo=NY
            ).astimezone(UTC),
            session_close_timestamp=datetime.combine(
                TRADE_DATE, time(17), tzinfo=NY
            ).astimezone(UTC),
        ),
    )


def _bar_timestamp(index: int) -> datetime:
    opening = _calendar()[0].session_open_timestamp
    assert opening is not None
    return opening + timedelta(minutes=5 * (index + 1))


def _moment(relative_index: int) -> datetime:
    return _bar_timestamp(BASE_INDEX + relative_index)


def _provenance(
    source_indices: tuple[int, ...], confirmation_index: int
) -> SMCV2EventProvenance:
    return SMCV2EventProvenance(
        source_indices=source_indices,
        source_timestamps=tuple(_bar_timestamp(index) for index in source_indices),
        confirmation_index=confirmation_index,
        confirmation_timestamp=_bar_timestamp(confirmation_index),
    )


def _dataset_bars(outcome: str = "target") -> tuple[GCChronologicalBar, ...]:
    output: list[GCChronologicalBar] = []
    for index in range(276):
        open_tick, high_tick, low_tick, close_tick = 107, 110, 105, 108
        if index == BASE_INDEX + 6:
            open_tick, high_tick, low_tick, close_tick = 107, 110, 105, 108
        if index == BASE_INDEX + 7:
            if outcome == "target":
                high_tick = 120
            elif outcome == "invalidation":
                low_tick, close_tick = 97, 97
            elif outcome == "same_bar":
                high_tick, low_tick, close_tick = 120, 97, 97
        output.append(
            GCChronologicalBar(
                index=index,
                timestamp=_bar_timestamp(index),
                open_tick=open_tick,
                high_tick=high_tick,
                low_tick=low_tick,
                close_tick=close_tick,
                volume=100,
                is_closed=True,
            )
        )
    return tuple(output)


def _config(**changes: object) -> GCDatasetBuildConfig:
    values: dict[str, object] = {
        "instrument": "gc",
        "timeframe": "5m",
        "source_timezone": "Asia/Tokyo",
        "exchange_timezone": "America/New_York",
        "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
        "initial_contract": CONTRACT,
        "initial_trade_date": TRADE_DATE,
        "roll_confirmation_sessions": 3,
        "oos_start_trade_date": date(2026, 9, 1),
        "oos_end_trade_date": date(2026, 9, 30),
    }
    values.update(changes)
    return GCDatasetBuildConfig(**values)  # type: ignore[arg-type]


def _bar_digest(bars: tuple[GCChronologicalBar, ...]) -> str:
    return _hash_payload(
        tuple(
            {
                "index": bar.index,
                "timestamp": _timestamp_text(bar.timestamp),
                "open_tick": bar.open_tick,
                "high_tick": bar.high_tick,
                "low_tick": bar.low_tick,
                "close_tick": bar.close_tick,
                "volume": bar.volume,
                "is_closed": bar.is_closed,
            }
            for bar in bars
        )
    )


def _calendar_digest(entries: tuple[KillZoneCalendarEntry, ...]) -> str:
    return _hash_payload(
        tuple(
            {
                "calendar_version": item.calendar_version,
                "trade_date": item.trade_date.isoformat(),
                "session_status": item.session_status.value,
                "opening": (
                    _timestamp_text(item.session_open_timestamp)
                    if item.session_open_timestamp is not None
                    else None
                ),
                "closing": (
                    _timestamp_text(item.session_close_timestamp)
                    if item.session_close_timestamp is not None
                    else None
                ),
            }
            for item in entries
        )
    )


def _dataset(
    *,
    outcome: str = "target",
    truncate_after: int | None = None,
    partition: GCSegmentPartition = GCSegmentPartition.DEVELOPMENT,
    bars_override: tuple[GCChronologicalBar, ...] | None = None,
    calendar_override: tuple[KillZoneCalendarEntry, ...] | None = None,
) -> tuple[GCDatasetBuildConfig, GCDatasetBuildResult, tuple[KillZoneCalendarEntry, ...]]:
    config = _config()
    calendars = _calendar() if calendar_override is None else calendar_override
    bars = _dataset_bars(outcome) if bars_override is None else bars_override
    if truncate_after is not None:
        bars = tuple(item for item in bars if item.index <= truncate_after)
    segment_id = make_gc_dataset_id(
        identity_kind="SEGMENT",
        config=config,
        contract=CONTRACT,
        partition=partition,
        first_trade_date=TRADE_DATE,
        last_trade_date=TRADE_DATE,
        source_ids=(SOURCE_ID,),
        bar_digest=_bar_digest(bars),
        preceding_missing_bar_count=0,
    )
    segment = GCCanonicalContractSegment(
        segment_id=segment_id,
        contract=CONTRACT,
        partition=partition,
        first_trade_date=TRADE_DATE,
        last_trade_date=TRADE_DATE,
        source_ids=(SOURCE_ID,),
        bars=bars,
        preceding_missing_bar_count=0,
    )
    count = len(bars)
    volume = sum(item.volume for item in bars)
    missing = 276 - count
    raw_start = bars[0].timestamp
    raw_end = bars[-1].timestamp
    evidence = {
        "version": GC_DATASET_BUILDER_VERSION,
        "source_ids": (SOURCE_ID,),
        "coverage_ids": (COVERAGE_ID,),
        "coverage_digest": COVERAGE_DIGEST,
        "segment_ids": (segment_id,),
        "calendar_version": CALENDAR_VERSION,
        "timezone_data_version": TZDATA_VERSION,
        "raw_start_timestamp": _timestamp_text(raw_start),
        "raw_end_timestamp": _timestamp_text(raw_end),
        "usable_start_timestamp": _timestamp_text(raw_start),
        "usable_end_timestamp": _timestamp_text(raw_end),
        "parsed_row_count": count,
        "eligible_row_count": count,
        "development_bar_count": count if partition is GCSegmentPartition.DEVELOPMENT else 0,
        "oos_bar_count": count if partition is GCSegmentPartition.OOS_HOLDOUT else 0,
        "excluded_row_count": 0,
        "missing_bar_count": missing,
        "attested_no_trade_interval_count": missing,
        "raw_volume": volume,
        "eligible_volume": volume,
        "excluded_volume": 0,
        "completed_session_volumes": ((CONTRACT, TRADE_DATE.isoformat(), volume),),
        "exclusion_counts": (),
        "roll_trade_dates": (),
    }
    evidence_digest = _hash_payload(evidence)
    dataset_id = make_gc_dataset_id(
        identity_kind="DATASET",
        config=config,
        source_ids=(SOURCE_ID,),
        coverage_ids=(COVERAGE_ID,),
        segment_ids=(segment_id,),
        calendar_digest=_calendar_digest(calendars),
        coverage_digest=COVERAGE_DIGEST,
        evidence_digest=evidence_digest,
        roll_trade_dates=(),
    )
    manifest = GCDatasetManifest(
        dataset_id=dataset_id,
        version=GC_DATASET_BUILDER_VERSION,
        source_ids=(SOURCE_ID,),
        coverage_ids=(COVERAGE_ID,),
        coverage_digest=COVERAGE_DIGEST,
        segment_ids=(segment_id,),
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
        raw_start_timestamp=raw_start,
        raw_end_timestamp=raw_end,
        usable_start_timestamp=raw_start,
        usable_end_timestamp=raw_end,
        parsed_row_count=count,
        eligible_row_count=count,
        development_bar_count=count if partition is GCSegmentPartition.DEVELOPMENT else 0,
        oos_bar_count=count if partition is GCSegmentPartition.OOS_HOLDOUT else 0,
        excluded_row_count=0,
        missing_bar_count=missing,
        attested_no_trade_interval_count=missing,
        raw_volume=volume,
        eligible_volume=volume,
        excluded_volume=0,
        completed_session_volumes=((CONTRACT, TRADE_DATE, volume),),
        exclusion_counts=(),
        roll_trade_dates=(),
    )
    result = GCDatasetBuildResult(
        status=GCDatasetBuildStatus.VALID,
        dataset_id=dataset_id,
        segments=(segment,),
        manifest=manifest,
        reasons=("CANONICAL_DATASET_BUILT",),
    )
    return config, result, calendars


def _swing(
    side: DealingRangeSwingSide,
    relative_source: int,
    price_tick: int,
    relative_confirmation: int,
) -> DealingRangeSwing:
    source = BASE_INDEX + relative_source
    confirmation = BASE_INDEX + relative_confirmation
    return DealingRangeSwing(
        side=side,
        price_tick=price_tick,
        provenance=_provenance((source,), confirmation),
        swing_id=_hash(f"swing:{side.value}:{source}:{price_tick}"),
    )


def _range(direction: SMCV2Direction) -> tuple[tuple[DealingRangeSwing, ...], DealingRangeSnapshot]:
    low = _swing(DealingRangeSwingSide.LOW, 0, 90, 1)
    high = _swing(DealingRangeSwingSide.HIGH, 1, 120, 2)
    swings = (low, high)
    source_indices = (BASE_INDEX, BASE_INDEX + 1)
    swing_ids = (low.swing_id, high.swing_id)
    protected = low if direction is SMCV2Direction.BULLISH else high
    construction_event_id = _hash(f"construction:{direction.value}")
    boundaries = SMCV2TickRange(90, 120)
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
        source_indices=(BASE_INDEX + 2,),
        lineage_id=lineage_id,
        transition_from_state=None,
        transition_to_state=DealingRangeState.ACTIVE,
        transition_index=BASE_INDEX + 2,
        transition_timestamp=_moment(2),
        transition_reason="CONSTRUCTION_ACTIVE",
        related_event_id=construction_event_id,
    )
    transition = DealingRangeTransition(
        transition_id=transition_id,
        lineage_id=lineage_id,
        from_state=None,
        to_state=DealingRangeState.ACTIVE,
        index=BASE_INDEX + 2,
        timestamp=_moment(2),
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
        low_tick=90,
        high_tick=120,
        midpoint_tick=Decimal("105"),
        first_known_provenance=_provenance((BASE_INDEX + 2,), BASE_INDEX + 2),
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
    side = EqualLiquiditySide.LOW if direction is SMCV2Direction.BULLISH else EqualLiquiditySide.HIGH
    dealing_side = DealingRangeSwingSide.LOW if side is EqualLiquiditySide.LOW else DealingRangeSwingSide.HIGH
    reference = 100 if direction is SMCV2Direction.BULLISH else 110
    members = (
        _swing(dealing_side, 0, reference - 1, 1),
        _swing(dealing_side, 1, reference + 1, 2),
    )
    source_indices = (BASE_INDEX, BASE_INDEX + 1)
    member_ids = tuple(item.swing_id for item in members)
    lower, upper = reference - 2, reference + 2
    lineage_id = make_equal_liquidity_id(
        identity_kind="LINEAGE",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference,
        lower_tick=lower,
        upper_tick=upper,
    )
    first_known = _provenance(source_indices, BASE_INDEX + 2)
    active_event = SMCV2LifecycleEvent(
        None,
        SMCV2LifecycleState.ACTIVE,
        BASE_INDEX + 2,
        _moment(2),
        "SECOND_EQUAL_SWING_CONFIRMED",
    )
    active_snapshot_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference,
        lower_tick=lower,
        upper_tick=upper,
        lineage_id=lineage_id,
        lifecycle_state=SMCV2LifecycleState.ACTIVE,
    )
    active = EqualLiquidityPool(
        side,
        lineage_id,
        active_snapshot_id,
        member_ids,
        source_indices,
        reference,
        lower,
        upper,
        first_known,
        SMCV2LifecycleState.ACTIVE,
        (active_event,),
    )
    swept_event = SMCV2LifecycleEvent(
        SMCV2LifecycleState.ACTIVE,
        SMCV2LifecycleState.SWEPT,
        BASE_INDEX + 5,
        _moment(5),
        "OBSERVATION_SWEEP",
    )
    swept_id = make_equal_liquidity_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        side=side,
        source_indices=source_indices,
        swing_ids=member_ids,
        reference_tick=reference,
        lower_tick=lower,
        upper_tick=upper,
        lineage_id=lineage_id,
        lifecycle_state=SMCV2LifecycleState.SWEPT,
    )
    return members, active, replace(
        active,
        snapshot_id=swept_id,
        lifecycle_state=SMCV2LifecycleState.SWEPT,
        lifecycle_events=(active_event, swept_event),
    )


def _candidate(
    dataset: GCDatasetBuildResult,
    calendars: tuple[KillZoneCalendarEntry, ...],
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
) -> GCFeatureLabelCandidateEvidence:
    swings, active_range = _range(direction)
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
    source_indices = (BASE_INDEX + 5, BASE_INDEX + 6)
    broken = swings[1] if direction is SMCV2Direction.BULLISH else swings[0]
    event_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=direction,
        source_indices=source_indices,
        event_type=DealingRangeEventType.BOS,
        broken_swing_id=broken.swing_id,
        confirmation_index=BASE_INDEX + 6,
        boundaries=SMCV2TickRange(broken.price_tick, broken.price_tick),
    )
    event = DealingRangeStructureEvent(
        direction=direction,
        event_type=DealingRangeEventType.BOS,
        broken_swing_id=broken.swing_id,
        provenance=_provenance(source_indices, BASE_INDEX + 6),
        event_id=event_id,
    )
    if direction is SMCV2Direction.BULLISH:
        candles = (
            FairValueGapCandle(BASE_INDEX + 4, _moment(4), 102, 104, 101, 103),
            FairValueGapCandle(BASE_INDEX + 5, _moment(5), 103, 112, 102, 111),
            FairValueGapCandle(BASE_INDEX + 6, _moment(6), 106, 110, 106, 109),
        )
    else:
        candles = (
            FairValueGapCandle(BASE_INDEX + 4, _moment(4), 114, 115, 112, 113),
            FairValueGapCandle(BASE_INDEX + 5, _moment(5), 113, 114, 102, 103),
            FairValueGapCandle(BASE_INDEX + 6, _moment(6), 109, 110, 106, 107),
        )
    displacement_id = _hash(f"displacement:{direction.value}")
    fvg_result = analyze_fair_value_gaps(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        candles=candles,
        context_links=(
            FairValueGapContextLink(
                BASE_INDEX + 6,
                _moment(6),
                displacement_id,
                event_id,
                DealingRangeEventType.BOS,
            ),
        ),
    )
    assert fvg_result.status is SMCV2PrimitiveStatus.VALID
    observations = tuple(
        InducementObservation(
            index=BASE_INDEX + index,
            timestamp=_moment(index),
            open_tick=107,
            high_tick=110,
            low_tick=105,
            close_tick=108,
            is_closed=True,
        )
        for index in range(9)
    )
    sweep = (
        InducementObservation(BASE_INDEX + 5, _moment(5), 101, 106, 97, 99, True)
        if direction is SMCV2Direction.BULLISH
        else InducementObservation(BASE_INDEX + 5, _moment(5), 109, 113, 106, 112, True)
    )
    observations = (*observations[:5], sweep, *observations[6:])
    inducement_result = analyze_inducements(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        dealing_range_snapshots=(active_range,),
        liquidity_map_snapshots=map_result.snapshots,
        equal_liquidity_pools=(active_pool, swept_pool),
        structure_events=(event,),
        fair_value_gaps=fvg_result.gaps,
        fair_value_gap_transitions=fvg_result.transitions,
        fair_value_gap_snapshots=fvg_result.snapshots,
        observations=tuple(observations),
    )
    assert inducement_result.status is SMCV2PrimitiveStatus.VALID
    inducement = inducement_result.inducements[0]
    map_snapshot = next(
        item for item in map_result.snapshots if item.snapshot_id == inducement.liquidity_map_snapshot_id
    )
    external = next(
        item
        for item in map_snapshot.classifications
        if item.classification_id == inducement.external_target_classification_id
    )
    internal = next(
        item
        for item in map_snapshot.classifications
        if item.classification_id == inducement.internal_pool_classification_id
    )
    kz_result = analyze_kill_zones(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        observations=(KillZoneObservation(BASE_INDEX + 6, _moment(6), True),),
        calendar_entries=calendars,
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
    )
    assert kz_result.status is SMCV2PrimitiveStatus.VALID
    confirmation_bar = next(
        bar
        for segment in dataset.segments
        for bar in segment.bars
        if bar.index == BASE_INDEX + 6
    )
    return GCFeatureLabelCandidateEvidence(
        inducement=inducement,
        inducement_snapshot=inducement_result.snapshots[0],
        active_range=active_range,
        liquidity_map_snapshot=map_snapshot,
        external_target=external,
        internal_pool_classification=internal,
        internal_pool=swept_pool,
        structure_event=event,
        fair_value_gap=fvg_result.gaps[0],
        fair_value_gap_transitions=fvg_result.transitions,
        fair_value_gap_snapshots=fvg_result.snapshots,
        kill_zone_context=kz_result.contexts[0],
        kill_zone_snapshot=kz_result.snapshots[0],
        confirmation_bar=confirmation_bar,
    )


def _retime_liquidity_map_to_sweep(
    candidate: GCFeatureLabelCandidateEvidence,
) -> GCFeatureLabelCandidateEvidence:
    inducement = candidate.inducement
    map_snapshot = candidate.liquidity_map_snapshot
    late_snapshot_id = make_liquidity_map_id(
        identity_kind="SNAPSHOT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        active_range_lineage_id=map_snapshot.active_range_lineage_id,
        active_range_snapshot_id=map_snapshot.active_range_snapshot_id,
        classification_ids=map_snapshot.classification_ids,
        reclassification_ids=map_snapshot.reclassification_ids,
        event_index=inducement.sweep_index,
        event_timestamp=inducement.sweep_timestamp,
    )
    late_map = replace(
        map_snapshot,
        snapshot_id=late_snapshot_id,
        index=inducement.sweep_index,
        timestamp=inducement.sweep_timestamp,
    )
    late_inducement_id = make_inducement_id(
        identity_kind="INDUCEMENT",
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        direction=inducement.direction,
        active_range_lineage_id=inducement.active_range_lineage_id,
        active_range_snapshot_id=inducement.active_range_snapshot_id,
        liquidity_map_snapshot_id=late_snapshot_id,
        external_target_classification_id=inducement.external_target_classification_id,
        internal_pool_classification_id=inducement.internal_pool_classification_id,
        internal_pool_id=inducement.internal_pool_id,
        sweep_index=inducement.sweep_index,
        sweep_timestamp=inducement.sweep_timestamp,
        sweep_extreme_tick=inducement.sweep_extreme_tick,
        reclaim_close_tick=inducement.reclaim_close_tick,
        structure_event_id=inducement.structure_event_id,
        structure_event_type=inducement.structure_event_type,
        confirmation_index=inducement.confirmation_index,
        confirmation_timestamp=inducement.confirmation_timestamp,
        confirmation_offset_bars=inducement.confirmation_offset_bars,
        fair_value_gap_id=inducement.fair_value_gap_id,
        displacement_id=inducement.displacement_id,
    )
    late_inducement = replace(
        inducement,
        inducement_id=late_inducement_id,
        liquidity_map_snapshot_id=late_snapshot_id,
    )
    inducement_snapshot = candidate.inducement_snapshot
    inducement_ids = tuple(
        late_inducement_id if item == inducement.inducement_id else item
        for item in inducement_snapshot.inducement_ids
    )
    late_inducement_snapshot = replace(
        inducement_snapshot,
        snapshot_id=make_inducement_id(
            identity_kind="SNAPSHOT",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            effective_index=inducement_snapshot.index,
            effective_timestamp=inducement_snapshot.timestamp,
            inducement_ids=inducement_ids,
        ),
        inducement_ids=inducement_ids,
    )
    return replace(
        candidate,
        inducement=late_inducement,
        inducement_snapshot=late_inducement_snapshot,
        liquidity_map_snapshot=late_map,
    )


def _build(
    *,
    outcome: str = "target",
    truncate_after: int | None = None,
    candidates: tuple[GCFeatureLabelCandidateEvidence, ...] | None | object = object(),
    dataset_override: GCDatasetBuildResult | None | object = object(),
    calendar_override: tuple[KillZoneCalendarEntry, ...] | None | object = object(),
    config_override: GCDatasetBuildConfig | object = object(),
    feature_config: GCFeatureLabelConfig = GCFeatureLabelConfig(),
) -> GCFeatureLabelResult:
    config, dataset, calendars = _dataset(outcome=outcome, truncate_after=truncate_after)
    selected_candidates = (_candidate(dataset, calendars),) if type(candidates) is object else candidates
    selected_dataset = dataset if type(dataset_override) is object else dataset_override
    selected_calendar = calendars if type(calendar_override) is object else calendar_override
    selected_config = config if type(config_override) is object else config_override
    return build_gc_feature_labels(
        dataset_config=selected_config,  # type: ignore[arg-type]
        dataset=selected_dataset,  # type: ignore[arg-type]
        calendar_entries=selected_calendar,  # type: ignore[arg-type]
        candidates=selected_candidates,  # type: ignore[arg-type]
        config=feature_config,
    )


def _malformed(instance: object, field_name: str) -> object:
    value = object.__new__(type(instance))
    for name, field_value in vars(instance).items():
        if name != field_name:
            object.__setattr__(value, name, field_value)
    return value


# Logical cases 1-9: top-level contracts and canonical dataset evidence.
def test_case_01_missing_top_level_context_and_invalid_precedence() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    assert build_gc_feature_labels(dataset_config=config, dataset=None, calendar_entries=calendars, candidates=(candidate,)).status is SMCV2PrimitiveStatus.UNKNOWN
    bad = replace(candidate, confirmation_bar=replace(candidate.confirmation_bar, index=True))
    result = build_gc_feature_labels(dataset_config=config, dataset=None, calendar_entries=calendars, candidates=(bad,))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert not result.rows and not result.labels and result.manifest is None
    manifest = dataset.manifest
    assert manifest is not None
    malformed_dataset = replace(
        dataset,
        manifest=replace(
            manifest,
            eligible_row_count=manifest.eligible_row_count + 1,
        ),
    )
    for missing_context in (
        build_gc_feature_labels(
            dataset_config=config,
            dataset=malformed_dataset,
            calendar_entries=None,
            candidates=(candidate,),
        ),
        build_gc_feature_labels(
            dataset_config=config,
            dataset=malformed_dataset,
            calendar_entries=calendars,
            candidates=None,
        ),
    ):
        assert missing_context.status is SMCV2PrimitiveStatus.INVALID
        assert not missing_context.rows and not missing_context.labels
        assert missing_context.manifest is None


def test_case_02_complete_empty_candidates_is_none() -> None:
    assert _build(candidates=()).status is SMCV2PrimitiveStatus.NONE


def test_case_03_bullish_feature_row_exact_schema() -> None:
    result = _build()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.rows[0].feature_values) == 17
    assert result.rows[0].feature_values == (
        "BULLISH", "BOS", 1, "LOW", 4, 2, 1, 1, "SWING", 21,
        "BULLISH", 30, 6, 2, 6, 60, 120,
    )


def test_case_04_bearish_mirror_feature_row() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.rows[0].feature_values[0] == "BEARISH"
    assert result.rows[0].feature_values[3] == "HIGH"


def test_case_05_outside_new_york_am_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    context = replace(candidate.kill_zone_context, zone=KillZoneName.LONDON)
    malformed = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=(replace(candidate, kill_zone_context=context),),
    )
    assert malformed.status is SMCV2PrimitiveStatus.INVALID

    monkeypatch.setitem(globals(), "BASE_INDEX", 101)
    london_config, london_dataset, london_calendars = _dataset()
    london_candidate = _candidate(london_dataset, london_calendars)
    assert london_candidate.kill_zone_context.zone is KillZoneName.LONDON
    result = build_gc_feature_labels(
        dataset_config=london_config,
        dataset=london_dataset,
        calendar_entries=london_calendars,
        candidates=(london_candidate,),
    )
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.reasons == ("NO_ELIGIBLE_CANDIDATES",)
    assert not result.rows and not result.labels and result.manifest is None


def test_case_06_new_york_am_context_is_verified_and_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    assert candidate.kill_zone_context.zone is KillZoneName.NEW_YORK_AM
    assert candidate.kill_zone_context.quality is KillZoneQuality.VERIFIED
    assert _build().status is SMCV2PrimitiveStatus.VALID

    monkeypatch.setitem(globals(), "BASE_INDEX", 149)
    open_config, open_dataset, open_calendars = _dataset()
    open_candidate = _candidate(open_dataset, open_calendars)
    assert open_candidate.inducement.confirmation_timestamp.astimezone(NY).time() == time(7)
    exact_open = build_gc_feature_labels(
        dataset_config=open_config,
        dataset=open_dataset,
        calendar_entries=open_calendars,
        candidates=(open_candidate,),
    )
    assert exact_open.status is SMCV2PrimitiveStatus.VALID

    monkeypatch.setitem(globals(), "BASE_INDEX", 185)
    close_config, close_dataset, close_calendars = _dataset()
    close_moment = _moment(6)
    assert close_moment.astimezone(NY).time() == time(10)
    kill_zone = analyze_kill_zones(
        instrument=INSTRUMENT,
        timeframe=TIMEFRAME,
        observations=(KillZoneObservation(BASE_INDEX + 6, close_moment, True),),
        calendar_entries=close_calendars,
        calendar_version=CALENDAR_VERSION,
        timezone_data_version=TZDATA_VERSION,
    )
    assert kill_zone.status is SMCV2PrimitiveStatus.NONE
    exact_close = build_gc_feature_labels(
        dataset_config=close_config,
        dataset=close_dataset,
        calendar_entries=close_calendars,
        candidates=(),
    )
    assert exact_close.status is SMCV2PrimitiveStatus.NONE
    assert exact_close.reasons == ("NO_ELIGIBLE_CANDIDATES",)


def test_case_07_confirmation_moments_match_exactly() -> None:
    result = _build()
    assert result.rows[0].effective_index == BASE_INDEX + 6
    assert result.rows[0].effective_timestamp == _moment(6)


@pytest.mark.parametrize("field,value", [("index", True), ("timestamp", datetime(2026, 1, 1))])
def test_case_08_malformed_bar_fields_fail_closed(field: str, value: object) -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    result = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=(replace(candidate, confirmation_bar=replace(candidate.confirmation_bar, **{field: value})),),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("field", ["dataset_id", "segment_ids", "eligible_row_count", "eligible_volume"])
def test_case_09_manifest_tampering_is_invalid(field: str) -> None:
    config, dataset, calendars = _dataset()
    manifest = dataset.manifest
    assert manifest is not None
    changes: dict[str, object] = {field: (_hash("bad") if field == "dataset_id" else ())}
    if field == "eligible_row_count": changes[field] = manifest.eligible_row_count + 1
    if field == "eligible_volume": changes[field] = manifest.eligible_volume + 1
    bad_dataset = replace(dataset, manifest=replace(manifest, **changes))
    assert build_gc_feature_labels(dataset_config=config, dataset=bad_dataset, calendar_entries=calendars, candidates=()).status is SMCV2PrimitiveStatus.INVALID


# Logical cases 10-29: ordering, binding, geometry, and look-ahead exclusion.
def test_case_10_caller_candidate_order_is_not_silently_sorted() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    later = replace(
        candidate,
        inducement=replace(candidate.inducement, confirmation_index=candidate.inducement.confirmation_index + 1),
    )
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(later, candidate))
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_11_bullish_side_roles_are_exact() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    assert candidate.internal_pool_classification.side is LiquiditySide.SELL_SIDE
    assert candidate.external_target.side is LiquiditySide.BUY_SIDE


def test_case_12_bearish_side_roles_are_exact() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    assert candidate.internal_pool_classification.side is LiquiditySide.BUY_SIDE
    assert candidate.external_target.side is LiquiditySide.SELL_SIDE


def test_case_13_wrong_scope_is_invalid() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(replace(candidate, external_target=replace(candidate.external_target, scope=LiquidityScope.INTERNAL)),))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    detached_external = replace(
        candidate.external_target,
        boundaries=SMCV2TickRange(
            candidate.external_target.boundaries.lower_tick + 1,
            candidate.external_target.boundaries.upper_tick + 1,
        ),
    )
    detached_internal = replace(
        candidate.internal_pool_classification,
        boundaries=SMCV2TickRange(
            candidate.internal_pool_classification.boundaries.lower_tick - 1,
            candidate.internal_pool_classification.boundaries.upper_tick,
        ),
    )
    for detached in (
        replace(candidate, external_target=detached_external),
        replace(candidate, internal_pool_classification=detached_internal),
    ):
        invalid = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(detached,),
        )
        assert invalid.status is SMCV2PrimitiveStatus.INVALID
        assert not invalid.rows and not invalid.labels and invalid.manifest is None

    late_range = replace(
        candidate.active_range,
        first_known_provenance=_provenance((BASE_INDEX + 6,), BASE_INDEX + 6),
    )
    transition_mismatched_range = replace(
        candidate.active_range,
        first_known_provenance=_provenance(
            (BASE_INDEX + 2,),
            BASE_INDEX + 3,
        ),
    )
    for late_candidate in (
        replace(candidate, active_range=late_range),
        replace(candidate, active_range=transition_mismatched_range),
        _retime_liquidity_map_to_sweep(candidate),
    ):
        invalid = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(late_candidate,),
        )
        assert invalid.status is SMCV2PrimitiveStatus.INVALID
        assert not invalid.rows and not invalid.labels and invalid.manifest is None

    detached_transition = replace(
        candidate.active_range.transitions[0],
        reason="OBSERVATION_CLOSE_THROUGH_INVALIDATION",
    )
    malformed_pool_chain = replace(
        candidate.internal_pool,
        lifecycle_events=(
            candidate.internal_pool.lifecycle_events[0],
            replace(candidate.internal_pool.lifecycle_events[1], from_state=None),
        ),
    )
    pool_provenance_mismatch = replace(
        candidate.internal_pool,
        first_known_provenance=_provenance(
            candidate.internal_pool.source_indices,
            BASE_INDEX + 3,
        ),
    )
    for malformed in (
        replace(
            candidate,
            active_range=replace(
                candidate.active_range,
                transitions=(detached_transition,),
            ),
        ),
        replace(
            candidate,
            liquidity_map_snapshot=replace(
                candidate.liquidity_map_snapshot,
                map_id=_hash("detached-map"),
            ),
        ),
        replace(candidate, internal_pool=malformed_pool_chain),
        replace(candidate, internal_pool=pool_provenance_mismatch),
    ):
        invalid = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(malformed,),
        )
        assert invalid.status is SMCV2PrimitiveStatus.INVALID
        assert not invalid.rows and not invalid.labels and invalid.manifest is None


def test_case_14_event_and_fvg_source_sequences_end_at_confirmation() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    assert candidate.structure_event.provenance.source_indices[-1] == BASE_INDEX + 6
    assert candidate.fair_value_gap.source_indices[-1] == BASE_INDEX + 6
    assert _build().status is SMCV2PrimitiveStatus.VALID

    original_snapshot = candidate.fair_value_gap_snapshots[0]
    forged_snapshots = []
    for state, index, timestamp in (
        (
            FairValueGapState.TOUCHED,
            original_snapshot.index,
            original_snapshot.timestamp,
        ),
        (
            original_snapshot.state,
            original_snapshot.index + 1,
            original_snapshot.timestamp + timedelta(minutes=5),
        ),
    ):
        snapshot_id = make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument=INSTRUMENT,
            timeframe=TIMEFRAME,
            direction=original_snapshot.direction,
            gap_id=original_snapshot.gap_id,
            state=state,
            effective_index=index,
            effective_timestamp=timestamp,
            transition_ids=original_snapshot.transition_ids,
        )
        forged_snapshots.append(
            replace(
                original_snapshot,
                snapshot_id=snapshot_id,
                state=state,
                index=index,
                timestamp=timestamp,
            )
        )

    for forged_snapshot in forged_snapshots:
        invalid = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(
                replace(
                    candidate,
                    fair_value_gap_snapshots=(forged_snapshot,),
                ),
            ),
        )
        assert invalid.status is SMCV2PrimitiveStatus.INVALID
        assert not invalid.rows and not invalid.labels and invalid.manifest is None


def test_case_15_opaque_displacement_requires_exact_equality() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    bad = replace(candidate, inducement=replace(candidate.inducement, displacement_id=_hash("other")))
    assert build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(bad,)).status is SMCV2PrimitiveStatus.INVALID


def test_case_16_exact_duplicate_candidate_is_deterministic() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate, candidate))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.rows) == 1


def test_case_17_same_group_opposing_valid_candidates_are_ambiguous() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    bullish = _candidate(dataset, calendars)
    bearish = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    ordered = tuple(sorted((bullish, bearish), key=lambda item: (item.inducement.direction.value, item.inducement.inducement_id)))
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=ordered)
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert not result.rows and not result.labels

    malformed_bearish = replace(
        bearish,
        confirmation_bar=replace(
            bearish.confirmation_bar,
            timestamp=bearish.confirmation_bar.timestamp + timedelta(minutes=5),
        ),
    )
    invalid_first = tuple(
        sorted(
            (bullish, malformed_bearish),
            key=lambda item: (
                item.inducement.direction.value,
                item.inducement.inducement_id,
            ),
        )
    )
    invalid = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=invalid_first,
    )
    assert invalid.status is SMCV2PrimitiveStatus.INVALID
    assert invalid.reasons == ("INVALID_FEATURE_LABEL_EVIDENCE",)
    assert not invalid.rows and not invalid.labels and invalid.manifest is None


def test_case_18_pool_width_and_member_count() -> None:
    row = _build().rows[0]
    assert row.feature_values[4:6] == (4, 2)


def test_case_19_bullish_penetration_is_one_tick() -> None:
    assert _build().rows[0].feature_values[6] == 1


def test_case_20_bullish_reclaim_boundary_distance_is_one_tick() -> None:
    assert _build().rows[0].feature_values[7] == 1


def test_case_21_bullish_external_target_distance() -> None:
    assert _build().rows[0].feature_values[9] == 21


def test_case_22_bearish_external_target_distance_is_nonnegative() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,))
    assert result.rows[0].feature_values[9] >= 0


def test_case_23_already_reached_target_geometry_is_invalid() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    bar = replace(candidate.confirmation_bar, high_tick=120)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(replace(candidate, confirmation_bar=bar),))
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_24_range_and_fvg_widths() -> None:
    values = _build().rows[0].feature_values
    assert values[11] == 30 and values[13] == 2


def test_case_25_midpoint_offsets_are_exact_half_tick_units() -> None:
    values = _build().rows[0].feature_values
    assert values[12] == 6 and values[14] == 6


def test_case_26_decimal_context_does_not_change_output() -> None:
    config, dataset, calendars = _dataset()
    candidate = _candidate(dataset, calendars)
    with localcontext() as context:
        context.prec = 2
        low = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,)).rows[0].row_id
    with localcontext() as context:
        context.prec = 50
        high = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,)).rows[0].row_id
    assert low == high


def test_case_27_dst_database_conversion_produces_exact_ny_minutes() -> None:
    values = _build().rows[0].feature_values
    assert values[15:] == (60, 120)


def test_case_28_feature_tuple_has_no_future_values() -> None:
    row = _build().rows[0]
    forbidden = {"TARGET_FIRST", "INVALIDATION_FIRST", "TIMEOUT"}
    assert not forbidden.intersection(row.feature_values)


def test_case_29_post_confirmation_bars_do_not_change_features() -> None:
    assert _build(outcome="target").rows[0].feature_values == _build(outcome="timeout").rows[0].feature_values


# Logical cases 30-43: labeling, cutoff, and prefix behavior.
def test_case_30_horizon_is_exactly_next_twelve_bars() -> None:
    label = _build(outcome="timeout").labels[0]
    assert label.horizon_end_index == BASE_INDEX + 18
    assert label.horizon_bars == 12


def test_case_31_bullish_target_wick_equality_is_target_first() -> None:
    assert _build(outcome="target").labels[0].outcome is GCLabelOutcome.TARGET_FIRST


def test_case_32_bearish_target_wick_equality_is_target_first() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    target = candidate.external_target.boundaries.upper_tick
    bars = list(dataset.segments[0].bars)
    bars[BASE_INDEX + 7] = replace(bars[BASE_INDEX + 7], low_tick=target)
    config, dataset, calendars = _dataset(bars_override=tuple(bars))
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    result = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=(candidate,),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.labels[0].target_tick == target
    assert result.labels[0].outcome is GCLabelOutcome.TARGET_FIRST


def test_case_33_bullish_close_through_is_invalidation_first() -> None:
    assert _build(outcome="invalidation").labels[0].outcome is GCLabelOutcome.INVALIDATION_FIRST


def test_case_34_bearish_invalidation_threshold_is_pool_upper_plus_one() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    threshold = candidate.internal_pool.upper_tick + 1
    bars = list(dataset.segments[0].bars)
    bars[BASE_INDEX + 7] = replace(
        bars[BASE_INDEX + 7],
        high_tick=max(bars[BASE_INDEX + 7].high_tick, threshold),
        close_tick=threshold,
    )
    config, dataset, calendars = _dataset(bars_override=tuple(bars))
    candidate = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,))
    assert result.labels[0].invalidation_tick == threshold
    assert result.labels[0].outcome is GCLabelOutcome.INVALIDATION_FIRST


@pytest.mark.parametrize("direction", [SMCV2Direction.BULLISH, SMCV2Direction.BEARISH])
def test_case_35_pool_boundary_equality_does_not_invalidate(direction: SMCV2Direction) -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars, direction)
    boundary = (
        candidate.internal_pool.lower_tick
        if direction is SMCV2Direction.BULLISH
        else candidate.internal_pool.upper_tick
    )
    bars = list(dataset.segments[0].bars)
    original = bars[BASE_INDEX + 7]
    bars[BASE_INDEX + 7] = replace(
        original,
        high_tick=max(original.high_tick, boundary),
        low_tick=min(original.low_tick, boundary),
        close_tick=boundary,
    )
    config, dataset, calendars = _dataset(bars_override=tuple(bars))
    candidate = _candidate(dataset, calendars, direction)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,))
    assert result.labels[0].outcome is GCLabelOutcome.TIMEOUT


def test_case_36_first_outcome_order_is_chronological() -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    candidate = _candidate(dataset, calendars)
    target = candidate.external_target.boundaries.lower_tick
    invalidation = candidate.internal_pool.lower_tick - 1
    for target_offset, invalidation_offset, expected in (
        (7, 8, GCLabelOutcome.TARGET_FIRST),
        (8, 7, GCLabelOutcome.INVALIDATION_FIRST),
    ):
        bars = list(_dataset_bars("timeout"))
        bars[BASE_INDEX + target_offset] = replace(
            bars[BASE_INDEX + target_offset],
            high_tick=target,
        )
        bars[BASE_INDEX + invalidation_offset] = replace(
            bars[BASE_INDEX + invalidation_offset],
            low_tick=invalidation,
            close_tick=invalidation,
        )
        config, dataset, calendars = _dataset(bars_override=tuple(bars))
        candidate = _candidate(dataset, calendars)
        label = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(candidate,),
        ).labels[0]
        assert label.outcome is expected
        assert label.first_outcome_index == BASE_INDEX + min(target_offset, invalidation_offset)


def test_case_37_same_bar_collision_is_ambiguous_label() -> None:
    result = _build(outcome="same_bar")
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.labels[0].outcome is GCLabelOutcome.SAME_BAR_AMBIGUOUS
    assert result.manifest is None


def test_case_38_no_outcome_in_twelve_bars_is_timeout() -> None:
    assert _build(outcome="timeout").labels[0].outcome is GCLabelOutcome.TIMEOUT


def test_case_39_truncated_horizon_is_incomplete_unknown() -> None:
    variants: list[tuple[GCChronologicalBar, ...]] = []
    base = list(_dataset_bars("timeout"))
    variants.append(tuple(base[: BASE_INDEX + 11]))
    variants.append(tuple((*base[: BASE_INDEX + 8], *base[BASE_INDEX + 9 :])))
    substituted = list(base)
    substituted[BASE_INDEX + 8] = replace(
        substituted[BASE_INDEX + 8],
        timestamp=substituted[BASE_INDEX + 8].timestamp + timedelta(minutes=1),
        high_tick=120,
    )
    variants.append(tuple(substituted))
    non_closed = list(base)
    non_closed[BASE_INDEX + 8] = replace(non_closed[BASE_INDEX + 8], is_closed=False, high_tick=120)
    variants.append(tuple(non_closed))
    discontinuous = list(base)
    discontinuous[BASE_INDEX + 8] = replace(
        discontinuous[BASE_INDEX + 8],
        index=discontinuous[BASE_INDEX + 8].index + 1,
        high_tick=120,
    )
    variants.append(tuple(discontinuous))
    for bars in variants:
        config, dataset, calendars = _dataset(bars_override=bars)
        candidate = _candidate(dataset, calendars)
        result = build_gc_feature_labels(
            dataset_config=config,
            dataset=dataset,
            calendar_entries=calendars,
            candidates=(candidate,),
        )
        assert result.status is SMCV2PrimitiveStatus.UNKNOWN
        assert result.labels[0].outcome is GCLabelOutcome.INCOMPLETE
        assert result.labels[0].first_outcome_index is None
        assert result.manifest is None


def test_case_40_session_or_calendar_boundary_is_incomplete() -> None:
    opening = _calendar()[0].session_open_timestamp
    assert opening is not None
    early_close = (
        KillZoneCalendarEntry(
            CALENDAR_VERSION,
            TRADE_DATE,
            KillZoneSessionStatus.EARLY_CLOSE,
            opening,
            datetime.combine(TRADE_DATE, time(8, 30), tzinfo=NY).astimezone(UTC),
        ),
    )
    config, dataset, calendars = _dataset(outcome="timeout", calendar_override=early_close)
    candidate = _candidate(dataset, calendars)
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(candidate,))
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.labels[0].outcome is GCLabelOutcome.INCOMPLETE

    unrelated = (
        KillZoneCalendarEntry(
            CALENDAR_VERSION,
            TRADE_DATE + timedelta(days=1),
            KillZoneSessionStatus.OPEN,
            datetime.combine(TRADE_DATE, time(18), tzinfo=NY).astimezone(UTC),
            datetime.combine(TRADE_DATE + timedelta(days=1), time(17), tzinfo=NY).astimezone(UTC),
        ),
    )
    config, dataset, _ = _dataset(outcome="timeout", calendar_override=unrelated)
    candidate = _candidate(dataset, _calendar())
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=unrelated, candidates=(candidate,))
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.labels[0].outcome is GCLabelOutcome.INCOMPLETE


def test_case_41_later_invalid_group_preserves_prior_complete_evidence() -> None:
    config, dataset, calendars = _dataset()
    first = _candidate(dataset, calendars)
    bad = replace(first, inducement=replace(first.inducement, inducement_id=_hash("bad-later"), confirmation_index=first.inducement.confirmation_index + 1))
    result = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first, bad))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.rows and result.labels

    incomplete_config, incomplete_dataset, incomplete_calendars = _dataset(
        outcome="timeout",
        truncate_after=BASE_INDEX + 10,
    )
    incomplete_first = _candidate(incomplete_dataset, incomplete_calendars)
    incomplete_prefix = build_gc_feature_labels(
        dataset_config=incomplete_config,
        dataset=incomplete_dataset,
        calendar_entries=incomplete_calendars,
        candidates=(incomplete_first,),
    )
    assert incomplete_prefix.status is SMCV2PrimitiveStatus.UNKNOWN
    malformed_later = replace(
        incomplete_first,
        inducement=replace(
            incomplete_first.inducement,
            inducement_id=_hash("bad-after-incomplete"),
            confirmation_index=incomplete_first.inducement.confirmation_index + 1,
        ),
    )
    invalid_after_incomplete = build_gc_feature_labels(
        dataset_config=incomplete_config,
        dataset=incomplete_dataset,
        calendar_entries=incomplete_calendars,
        candidates=(incomplete_first, malformed_later),
    )
    assert invalid_after_incomplete.status is SMCV2PrimitiveStatus.INVALID
    assert invalid_after_incomplete.rows == incomplete_prefix.rows
    assert invalid_after_incomplete.labels == incomplete_prefix.labels
    assert invalid_after_incomplete.manifest is None
    assert invalid_after_incomplete.reasons == (
        "INVALID_FEATURE_LABEL_EVIDENCE",
        "INCOMPLETE_LABEL_HORIZON",
    )
    assert invalid_after_incomplete.blocking_reasons == invalid_after_incomplete.reasons


def test_case_42_repeatability_and_complete_prefix_invariance(monkeypatch: pytest.MonkeyPatch) -> None:
    config, dataset, calendars = _dataset(outcome="timeout")
    first_candidate = _candidate(dataset, calendars)
    prefix = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first_candidate,))
    assert prefix.status is SMCV2PrimitiveStatus.VALID
    monkeypatch.setattr(sys.modules[__name__], "BASE_INDEX", BASE_INDEX + 12)
    later_candidate = _candidate(dataset, calendars)
    full = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first_candidate, later_candidate))
    repeat = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first_candidate, later_candidate))
    assert full == repeat
    assert full.status is SMCV2PrimitiveStatus.VALID
    assert full.rows[:1] == prefix.rows
    assert full.labels[:1] == prefix.labels


def test_case_43_historical_repair_changes_dataset_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    _, full, _ = _dataset()
    _, short, _ = _dataset(truncate_after=BASE_INDEX + 10)
    assert full.dataset_id != short.dataset_id
    config, dataset, calendars = _dataset(outcome="timeout")
    first = _candidate(dataset, calendars)
    opposing = _candidate(dataset, calendars, SMCV2Direction.BEARISH)
    same_effective = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=tuple(
            sorted(
                (first, opposing),
                key=lambda item: (
                    item.inducement.confirmation_index,
                    item.inducement.confirmation_timestamp,
                    item.inducement.direction.value,
                    item.inducement.inducement_id,
                ),
            )
        ),
    )
    assert same_effective.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert not same_effective.rows and not same_effective.labels
    monkeypatch.setattr(sys.modules[__name__], "BASE_INDEX", BASE_INDEX + 12)
    later = _candidate(dataset, calendars)
    reordered = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=(later, first),
    )
    assert reordered.status is SMCV2PrimitiveStatus.INVALID
    mutated = replace(
        first,
        kill_zone_context=replace(first.kill_zone_context, timezone_data_version="MUTATED"),
    )
    version_mutation = build_gc_feature_labels(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        candidates=(mutated,),
    )
    assert version_mutation.status is SMCV2PrimitiveStatus.INVALID


# Logical cases 44-48: exhaustive identity schemas and public surface.
def test_case_44_feature_row_identity_schema_and_sensitivity() -> None:
    row = _build().rows[0]
    kwargs = {
        "identity_kind": GCFeatureLabelIdentityKind.FEATURE_ROW,
        "instrument": row.instrument,
        "timeframe": row.timeframe,
        "tick_size": row.tick_size,
        "timezone_data_version": row.timezone_data_version,
        "calendar_version": row.calendar_version,
        "dataset_id": row.dataset_id,
        "candidate_id": row.candidate_id,
        "contract": row.contract,
        "trade_date": row.trade_date,
        "source_ids": row.source_ids,
        "lineage_ids": row.lineage_ids,
        "detector_versions": row.detector_versions,
        "feature_schema_id": row.feature_schema_id,
        "feature_values": row.feature_values,
        "effective_index": row.effective_index,
        "effective_timestamp": row.effective_timestamp,
    }
    assert make_gc_feature_label_id(**kwargs) == row.row_id
    for name in (
        "identity_kind", "instrument", "timeframe", "tick_size",
        "timezone_data_version", "calendar_version", "dataset_id",
    ):
        missing = dict(kwargs)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**missing)
    for name, value in {
        "candidate_id": None,
        "contract": None,
        "trade_date": None,
        "source_ids": (),
        "lineage_ids": (),
        "detector_versions": (),
        "feature_schema_id": None,
        "feature_values": (),
        "effective_index": None,
        "effective_timestamp": None,
    }.items():
        invalid = dict(kwargs, **{name: value})
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**invalid)
    for name, value in {
        "label_schema_id": GC_AI_LABEL_SCHEMA_ID,
        "horizon_bars": GC_AI_LABEL_HORIZON_BARS,
        "target_tick": 120,
        "invalidation_tick": 97,
        "outcome": GCLabelOutcome.TIMEOUT,
        "first_outcome_index": row.effective_index + 1,
        "first_outcome_timestamp": row.effective_timestamp + timedelta(minutes=5),
        "horizon_end_index": row.effective_index + 12,
        "horizon_end_timestamp": row.effective_timestamp + timedelta(minutes=60),
        "feature_row_ids": (_hash("row"),),
        "label_ids": (_hash("label"),),
    }.items():
        forbidden = dict(kwargs, **{name: value})
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**forbidden)
    sensitivities = (
        {"instrument": "MGC"},
        {"timeframe": "15M"},
        {"tick_size": Decimal("0.2")},
        {"timezone_data_version": "ALT-TZDATA"},
        {"calendar_version": "ALT-CALENDAR"},
        {"dataset_id": _hash("other-dataset")},
        {"candidate_id": _hash("other-candidate")},
        {"contract": "GCZ26-COMEX"},
        {"trade_date": row.trade_date + timedelta(days=1)},
        {"source_ids": (_hash("other-source"),)},
        {"lineage_ids": (*row.lineage_ids[:-1], _hash("other-lineage"))},
        {"detector_versions": (*row.detector_versions[:-1], ("kill_zones", "ALT"))},
        {"feature_schema_id": "ALT_FEATURE_SCHEMA"},
        {"feature_values": (*row.feature_values[:-1], row.feature_values[-1] + 1)},
        {"effective_index": row.effective_index + 1},
        {"effective_timestamp": row.effective_timestamp + timedelta(minutes=5)},
    )
    for change in sensitivities:
        assert make_gc_feature_label_id(**dict(kwargs, **change)) != row.row_id


@pytest.mark.parametrize("outcome", ["target", "invalidation", "timeout", "same_bar"])
def test_case_45_label_identity_schema(outcome: str) -> None:
    label = _build(outcome=outcome).labels[0]
    kwargs = {
        "identity_kind": GCFeatureLabelIdentityKind.LABEL,
        "instrument": label.instrument,
        "timeframe": label.timeframe,
        "tick_size": label.tick_size,
        "timezone_data_version": label.timezone_data_version,
        "calendar_version": label.calendar_version,
        "dataset_id": label.dataset_id,
        "candidate_id": label.candidate_id,
        "contract": label.contract,
        "trade_date": label.trade_date,
        "label_schema_id": label.label_schema_id,
        "horizon_bars": label.horizon_bars,
        "target_tick": label.target_tick,
        "invalidation_tick": label.invalidation_tick,
        "outcome": label.outcome,
        "effective_index": label.effective_index,
        "effective_timestamp": label.effective_timestamp,
        "first_outcome_index": label.first_outcome_index,
        "first_outcome_timestamp": label.first_outcome_timestamp,
        "horizon_end_index": label.horizon_end_index,
        "horizon_end_timestamp": label.horizon_end_timestamp,
    }
    rebuilt = make_gc_feature_label_id(**kwargs)
    assert rebuilt == label.label_id
    if outcome == "target":
        for name in (
            "identity_kind", "instrument", "timeframe", "tick_size",
            "timezone_data_version", "calendar_version", "dataset_id",
        ):
            missing = dict(kwargs)
            missing.pop(name)
            with pytest.raises((TypeError, ValueError)):
                make_gc_feature_label_id(**missing)
        required_failures = (
            {"candidate_id": None},
            {"contract": None},
            {"trade_date": None},
            {"label_schema_id": None},
            {"horizon_bars": None},
            {"target_tick": None},
            {"invalidation_tick": None},
            {"outcome": None},
            {"effective_index": None},
            {"effective_timestamp": None},
            {"first_outcome_index": None, "first_outcome_timestamp": None},
            {"horizon_end_index": None, "horizon_end_timestamp": None},
        )
        for change in required_failures:
            with pytest.raises((TypeError, ValueError)):
                make_gc_feature_label_id(**dict(kwargs, **change))
        for name, value in {
            "source_ids": (_hash("source"),),
            "lineage_ids": (_hash("lineage"),),
            "detector_versions": (("detector", "version"),),
            "feature_schema_id": GC_AI_FEATURE_SCHEMA_ID,
            "feature_values": (1,),
            "feature_row_ids": (_hash("row"),),
            "label_ids": (_hash("label"),),
        }.items():
            with pytest.raises((TypeError, ValueError)):
                make_gc_feature_label_id(**dict(kwargs, **{name: value}))
        sensitivities = (
            {"instrument": "MGC"},
            {"timeframe": "15M"},
            {"tick_size": Decimal("0.2")},
            {"timezone_data_version": "ALT-TZDATA"},
            {"calendar_version": "ALT-CALENDAR"},
            {"dataset_id": _hash("other-dataset")},
            {"candidate_id": _hash("other-candidate")},
            {"contract": "GCZ26-COMEX"},
            {"trade_date": label.trade_date + timedelta(days=1)},
            {"label_schema_id": "ALT_LABEL_SCHEMA"},
            {"horizon_bars": label.horizon_bars + 1},
            {"target_tick": label.target_tick + 1},
            {"invalidation_tick": label.invalidation_tick - 1},
            {"outcome": GCLabelOutcome.SAME_BAR_AMBIGUOUS},
            {"effective_index": label.effective_index + 1},
            {"effective_timestamp": label.effective_timestamp + timedelta(minutes=5)},
            {"first_outcome_index": label.first_outcome_index + 1},
            {"first_outcome_timestamp": label.first_outcome_timestamp + timedelta(minutes=5)},
            {"horizon_end_index": label.horizon_end_index + 1},
            {"horizon_end_timestamp": label.horizon_end_timestamp + timedelta(minutes=5)},
        )
        for change in sensitivities:
            assert make_gc_feature_label_id(**dict(kwargs, **change)) != label.label_id


def test_case_46_manifest_identity_schema_and_order() -> None:
    manifest = _build().manifest
    assert manifest is not None
    kwargs = {
        "identity_kind": GCFeatureLabelIdentityKind.MANIFEST,
        "instrument": manifest.instrument,
        "timeframe": manifest.timeframe,
        "tick_size": manifest.tick_size,
        "timezone_data_version": manifest.timezone_data_version,
        "calendar_version": manifest.calendar_version,
        "dataset_id": manifest.dataset_id,
        "feature_schema_id": manifest.feature_schema_id,
        "label_schema_id": manifest.label_schema_id,
        "horizon_bars": manifest.horizon_bars,
        "feature_row_ids": manifest.feature_row_ids,
        "label_ids": manifest.label_ids,
    }
    rebuilt = make_gc_feature_label_id(**kwargs)
    assert rebuilt == manifest.manifest_id
    for name in (
        "identity_kind", "instrument", "timeframe", "tick_size",
        "timezone_data_version", "calendar_version", "dataset_id",
    ):
        missing = dict(kwargs)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**missing)
    for change in (
        {"feature_schema_id": None},
        {"label_schema_id": None},
        {"horizon_bars": None},
        {"feature_row_ids": ()},
        {"label_ids": ()},
        {"feature_row_ids": (manifest.feature_row_ids[0], manifest.feature_row_ids[0])},
        {"label_ids": (manifest.label_ids[0], manifest.label_ids[0])},
    ):
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**dict(kwargs, **change))
    for name, value in {
        "candidate_id": _hash("candidate"),
        "contract": "GCQ26-COMEX",
        "trade_date": TRADE_DATE,
        "source_ids": (_hash("source"),),
        "lineage_ids": (_hash("lineage"),),
        "detector_versions": (("detector", "version"),),
        "feature_values": (1,),
        "target_tick": 120,
        "invalidation_tick": 97,
        "outcome": GCLabelOutcome.TIMEOUT,
        "effective_index": BASE_INDEX + 6,
        "effective_timestamp": _moment(6),
        "first_outcome_index": BASE_INDEX + 7,
        "first_outcome_timestamp": _moment(7),
        "horizon_end_index": BASE_INDEX + 18,
        "horizon_end_timestamp": _moment(18),
    }.items():
        with pytest.raises((TypeError, ValueError)):
            make_gc_feature_label_id(**dict(kwargs, **{name: value}))
    for change in (
        {"instrument": "MGC"},
        {"timeframe": "15M"},
        {"tick_size": Decimal("0.2")},
        {"timezone_data_version": "ALT-TZDATA"},
        {"calendar_version": "ALT-CALENDAR"},
        {"dataset_id": _hash("other-dataset")},
        {"feature_schema_id": "ALT_FEATURE_SCHEMA"},
        {"label_schema_id": "ALT_LABEL_SCHEMA"},
        {"horizon_bars": manifest.horizon_bars + 1},
    ):
        assert make_gc_feature_label_id(**dict(kwargs, **change)) != manifest.manifest_id
    row_history = (manifest.feature_row_ids[0], _hash("row-2"))
    label_history = (manifest.label_ids[0], _hash("label-2"))
    forward = make_gc_feature_label_id(
        **dict(kwargs, feature_row_ids=row_history, label_ids=label_history)
    )
    reverse = make_gc_feature_label_id(
        **dict(
            kwargs,
            feature_row_ids=tuple(reversed(row_history)),
            label_ids=tuple(reversed(label_history)),
        )
    )
    assert forward != reverse


def test_case_47_exact_public_api_frozen_types_constants_and_reasons() -> None:
    builder = inspect.signature(make_gc_feature_label_id)
    analyzer = inspect.signature(build_gc_feature_labels)
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in builder.parameters.values())
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in analyzer.parameters.values())
    assert tuple(builder.parameters) == (
        "identity_kind", "instrument", "timeframe", "tick_size",
        "timezone_data_version", "calendar_version", "dataset_id",
        "candidate_id", "contract", "trade_date", "source_ids",
        "lineage_ids", "detector_versions", "feature_schema_id",
        "label_schema_id", "horizon_bars", "feature_values", "target_tick",
        "invalidation_tick", "outcome", "effective_index",
        "effective_timestamp", "first_outcome_index",
        "first_outcome_timestamp", "horizon_end_index",
        "horizon_end_timestamp", "feature_row_ids", "label_ids",
    )
    for name in (
        "identity_kind", "instrument", "timeframe", "tick_size",
        "timezone_data_version", "calendar_version", "dataset_id",
    ):
        assert builder.parameters[name].default is inspect.Parameter.empty
    assert {
        name: parameter.default
        for name, parameter in tuple(builder.parameters.items())[7:]
    } == {
        "candidate_id": None,
        "contract": None,
        "trade_date": None,
        "source_ids": (),
        "lineage_ids": (),
        "detector_versions": (),
        "feature_schema_id": None,
        "label_schema_id": None,
        "horizon_bars": None,
        "feature_values": (),
        "target_tick": None,
        "invalidation_tick": None,
        "outcome": None,
        "effective_index": None,
        "effective_timestamp": None,
        "first_outcome_index": None,
        "first_outcome_timestamp": None,
        "horizon_end_index": None,
        "horizon_end_timestamp": None,
        "feature_row_ids": (),
        "label_ids": (),
    }
    assert tuple(analyzer.parameters) == ("dataset_config", "dataset", "calendar_entries", "candidates", "config")
    for name in ("dataset_config", "dataset", "calendar_entries", "candidates"):
        assert analyzer.parameters[name].default is inspect.Parameter.empty
    assert analyzer.parameters["config"].default == GCFeatureLabelConfig()
    assert GC_FEATURE_LABEL_VERSION == "GC-FEATURE-LABEL-V1"
    assert GC_AI_FEATURE_SCHEMA_ID == "GC_AI_FEATURE_SCHEMA_V1"
    assert GC_AI_LABEL_SCHEMA_ID == "GC_AI_LABEL_SCHEMA_V1"
    assert GC_AI_LABEL_HORIZON_BARS == 12
    assert [item.value for item in GCFeatureLabelIdentityKind] == ["FEATURE_ROW", "LABEL", "MANIFEST"]
    assert [item.value for item in GCLabelOutcome] == ["TARGET_FIRST", "INVALIDATION_FIRST", "TIMEOUT", "SAME_BAR_AMBIGUOUS", "INCOMPLETE", "INVALID"]
    exact_annotations = {
        GCFeatureLabelConfig: (
            ("feature_schema_id", "str"),
            ("label_schema_id", "str"),
            ("horizon_bars", "int"),
        ),
        GCFeatureLabelCandidateEvidence: (
            ("inducement", "Inducement"),
            ("inducement_snapshot", "InducementSnapshot"),
            ("active_range", "DealingRangeSnapshot"),
            ("liquidity_map_snapshot", "LiquidityMapSnapshot"),
            ("external_target", "LiquidityClassification"),
            ("internal_pool_classification", "LiquidityClassification"),
            ("internal_pool", "EqualLiquidityPool"),
            ("structure_event", "DealingRangeStructureEvent"),
            ("fair_value_gap", "FairValueGap"),
            ("fair_value_gap_transitions", "tuple[FairValueGapTransition, ...]"),
            ("fair_value_gap_snapshots", "tuple[FairValueGapSnapshot, ...]"),
            ("kill_zone_context", "KillZoneContext"),
            ("kill_zone_snapshot", "KillZoneSnapshot"),
            ("confirmation_bar", "GCChronologicalBar"),
        ),
        GCFeatureRow: (
            ("row_id", "str"), ("instrument", "str"), ("timeframe", "str"),
            ("tick_size", "Decimal"), ("dataset_id", "str"),
            ("candidate_id", "str"), ("contract", "str"),
            ("trade_date", "date"), ("effective_index", "int"),
            ("effective_timestamp", "datetime"), ("calendar_version", "str"),
            ("timezone_data_version", "str"), ("source_ids", "tuple[str, ...]"),
            ("lineage_ids", "tuple[str, ...]"),
            ("detector_versions", "tuple[tuple[str, str], ...]"),
            ("feature_schema_id", "str"),
            ("feature_values", "tuple[object, ...]"),
        ),
        GCResearchLabel: (
            ("label_id", "str"), ("instrument", "str"), ("timeframe", "str"),
            ("tick_size", "Decimal"), ("dataset_id", "str"),
            ("candidate_id", "str"), ("contract", "str"),
            ("trade_date", "date"), ("effective_index", "int"),
            ("effective_timestamp", "datetime"), ("calendar_version", "str"),
            ("timezone_data_version", "str"), ("label_schema_id", "str"),
            ("horizon_bars", "int"), ("target_tick", "int"),
            ("invalidation_tick", "int"), ("outcome", "GCLabelOutcome"),
            ("first_outcome_index", "int | None"),
            ("first_outcome_timestamp", "datetime | None"),
            ("horizon_end_index", "int | None"),
            ("horizon_end_timestamp", "datetime | None"),
        ),
        GCFeatureLabelManifest: (
            ("manifest_id", "str"), ("instrument", "str"),
            ("timeframe", "str"), ("tick_size", "Decimal"),
            ("timezone_data_version", "str"), ("calendar_version", "str"),
            ("dataset_id", "str"), ("feature_schema_id", "str"),
            ("label_schema_id", "str"), ("horizon_bars", "int"),
            ("feature_row_ids", "tuple[str, ...]"),
            ("label_ids", "tuple[str, ...]"),
        ),
        GCFeatureLabelResult: (
            ("status", "SMCV2PrimitiveStatus"),
            ("rows", "tuple[GCFeatureRow, ...]"),
            ("labels", "tuple[GCResearchLabel, ...]"),
            ("manifest", "GCFeatureLabelManifest | None"),
            ("reasons", "tuple[str, ...]"),
            ("blocking_reasons", "tuple[str, ...]"),
        ),
    }
    for cls, annotations in exact_annotations.items():
        with pytest.raises(FrozenInstanceError):
            setattr(object.__new__(cls), "x", 1)
        assert tuple(cls.__annotations__.items()) == annotations
        assert tuple(get_type_hints(cls)) == tuple(name for name, _ in annotations)
        assert tuple(item.name for item in fields(cls)) == tuple(name for name, _ in annotations)
    assert {
        item.name: item.default
        for item in fields(GCFeatureLabelConfig)
        if item.default is not MISSING
    } == {
        "feature_schema_id": GC_AI_FEATURE_SCHEMA_ID,
        "label_schema_id": GC_AI_LABEL_SCHEMA_ID,
        "horizon_bars": GC_AI_LABEL_HORIZON_BARS,
    }
    assert {
        item.name: item.default
        for item in fields(GCFeatureLabelResult)
        if item.default is not MISSING
    } == {
        "rows": (), "labels": (), "manifest": None,
        "reasons": (), "blocking_reasons": (),
    }
    assert _build().reasons == ("FEATURE_LABEL_VALID",)


def test_case_48_repeatability_exports_and_no_forbidden_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    import analysis.gc_feature_label_builder as module

    assert tuple(module.__all__) == (
        "GC_FEATURE_LABEL_VERSION",
        "GC_AI_FEATURE_SCHEMA_ID",
        "GC_AI_LABEL_SCHEMA_ID",
        "GC_AI_LABEL_HORIZON_BARS",
        "GCLabelOutcome",
        "GCFeatureLabelIdentityKind",
        "GCFeatureLabelConfig",
        "GCFeatureLabelCandidateEvidence",
        "GCFeatureRow",
        "GCResearchLabel",
        "GCFeatureLabelManifest",
        "GCFeatureLabelResult",
        "make_gc_feature_label_id",
        "build_gc_feature_labels",
    )
    assert not ({"fit", "predict", "score", "order", "pnl"} & set(module.__dict__))
    config, dataset, calendars = _dataset(outcome="timeout")
    first = _candidate(dataset, calendars)
    monkeypatch.setattr(sys.modules[__name__], "BASE_INDEX", BASE_INDEX + 12)
    second = _candidate(dataset, calendars)
    multi_a = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first, second))
    multi_b = build_gc_feature_labels(dataset_config=config, dataset=dataset, calendar_entries=calendars, candidates=(first, second))
    assert multi_a == multi_b
    assert tuple(row.effective_index for row in multi_a.rows) == tuple(sorted(row.effective_index for row in multi_a.rows))
    with pytest.raises((TypeError, ValueError)):
        make_gc_feature_label_id(
            identity_kind="UNKNOWN",  # type: ignore[arg-type]
            instrument="GC", timeframe="5M", tick_size=Decimal("0.1"),
            timezone_data_version=TZDATA_VERSION, calendar_version=CALENDAR_VERSION,
            dataset_id=_hash("dataset"),
        )
    config, oos_dataset, calendars = _dataset(
        partition=GCSegmentPartition.OOS_HOLDOUT
    )
    oos_candidate = _candidate(oos_dataset, calendars)
    sealed = build_gc_feature_labels(
        dataset_config=config,
        dataset=oos_dataset,
        calendar_entries=calendars,
        candidates=(oos_candidate,),
    )
    assert sealed.status is SMCV2PrimitiveStatus.INVALID
    assert not sealed.rows and not sealed.labels and sealed.manifest is None
