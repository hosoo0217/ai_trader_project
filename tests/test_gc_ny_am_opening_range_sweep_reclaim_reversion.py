"""Exact 48-case acceptance matrix for GC NY-AM sweep/reclaim reversion feasibility."""

from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import importlib.metadata
import inspect
import pickle
import re
from pathlib import Path
from typing import get_type_hints

import pytest
from zoneinfo import ZoneInfo

import analysis.gc_ny_am_opening_range_sweep_reclaim_reversion as sweep_reclaim
from analysis.gc_dataset_builder import (
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCDatasetSessionInterval,
    GCSegmentPartition,
    GCSplitSessionCalendarEntry,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneContext,
    KillZoneName,
    KillZoneQuality,
    KillZoneResult,
    KillZoneSessionStatus,
    KillZoneSnapshot,
    make_kill_zone_id,
)
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TZDATA_VERSION = importlib.metadata.version("tzdata")
TRADE_DATE = date(2026, 1, 6)
CALENDAR_VERSION = "GC-CALENDAR-SYNTHETIC-V1"

EXPECTED_EXPORTS = (
    "GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION",
    "GCNYAMSweepReclaimIdentityKind",
    "GCNYAMSweepReclaimOutcomeType",
    "GCNYAMSweepReclaimObservation",
    "GCNYAMSweepReclaimOpeningRange",
    "GCNYAMSweepReclaimCandidate",
    "GCNYAMSweepReclaimOutcome",
    "GCNYAMSweepReclaimManifest",
    "GCNYAMSweepReclaimResult",
    "make_gc_ny_am_sweep_reclaim_id",
    "analyze_gc_ny_am_opening_range_sweep_reclaim_reversion",
)

COUNT_FUNNEL_KEYS = (
    "REQUESTED_TRADE_DATES", "CALENDAR_ELIGIBLE_TRADE_DATES",
    "ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES", "COMPLETE_OPENING_RANGES",
    "NO_SWEEP_RECLAIM_TRADE_DATES", "AMBIGUOUS_SWEEP_GROUPS", "COMPLETE_CANDIDATES",
    "BULLISH_CANDIDATES", "BEARISH_CANDIDATES", "MIDPOINT_REACHED_OUTCOMES",
    "INVALIDATED_OUTCOMES", "SAME_BAR_AMBIGUOUS_OUTCOMES", "TIMEOUT_OUTCOMES",
    "COMPLETE_OUTCOMES", "INCOMPLETE_HORIZONS", "INVALID_GROUPS",
)

REASON_TOKENS = (
    "MISSING_TOP_LEVEL_CONTEXT", "INVALID_DATASET", "OOS_CONTACT", "UNREQUESTED_EVIDENCE",
    "INVALID_OBSERVATION", "MISSING_SPLIT_SESSION_CALENDAR", "INVALID_SPLIT_SESSION_CALENDAR",
    "MISSING_KILL_ZONE_CALENDAR", "INVALID_KILL_ZONE_CALENDAR", "MISSING_KILL_ZONE_EVIDENCE",
    "INVALID_KILL_ZONE_EVIDENCE", "SESSION_INELIGIBLE", "ATTESTED_NO_TRADE_OPENING_RANGE",
    "INCOMPLETE_OPENING_RANGE", "INVALID_OPENING_RANGE", "NO_SWEEP_RECLAIM", "AMBIGUOUS_SWEEP_RECLAIM",
    "INCOMPLETE_OUTCOME_HORIZON", "INVALID_OUTCOME_EVIDENCE",
    "AMBIGUOUS_CANONICAL_INTERPRETATION",
)


def _h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), NY).astimezone(UTC)


def _config(**changes: object) -> GCDatasetBuildConfig:
    values: dict[str, object] = {
        "instrument": "GC",
        "timeframe": "5M",
        "source_timezone": "Asia/Tokyo",
        "exchange_timezone": "America/New_York",
        "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
        "initial_contract": "GCG26-COMEX",
        "initial_trade_date": TRADE_DATE,
        "roll_confirmation_sessions": 3,
        "oos_start_trade_date": date(2027, 1, 1),
        "oos_end_trade_date": date(2027, 6, 30),
    }
    values.update(changes)
    return GCDatasetBuildConfig(**values)  # type: ignore[arg-type]


def _prices(count: int = 22, *, direction: str = "bear", collision: bool = False) -> list[tuple[int, int, int, int]]:
    values = [(100, 102, 99, 101), (101, 103, 100, 102), (102, 104, 101, 103),
              (103, 105, 102, 104), (104, 106, 103, 105), (105, 107, 104, 106)]
    if direction == "bear":
        values.append((106, 108, 98 if collision else 104, 106))
        values.append((106, 107, 103, 105))
        values.extend([(106, 107, 104, 106)] * max(0, count - 8))
    elif direction == "bull":
        values.append((100, 108 if collision else 102, 98, 100))
        values.append((100, 103, 99, 101))
        values.extend([(100, 102, 99, 100)] * max(0, count - 8))
    else:
        values.extend([(106, 107, 100, 104)] * max(0, count - 6))
    return values[:count]


def _fixture(
    *,
    direction: str = "bear",
    count: int = 22,
    collision: bool = False,
    target_event: bool = True,
    full_session_edges: bool = False,
    trade_date: date = TRADE_DATE,
    segment_seed: str = "segment",
) -> dict[str, object]:
    opening = _utc(trade_date - timedelta(days=1), 18)
    session_close = _utc(trade_date, 17)
    first_open = _utc(trade_date, 7)
    prices = _prices(count, direction=direction, collision=collision)
    analysis_bars = tuple(
        GCChronologicalBar(
            index,
            first_open + timedelta(minutes=5 * (index + 1)),
            price[0], price[1], price[2], price[3], 10 + index, True,
        )
        for index, price in enumerate(prices)
    )
    if not target_event and len(analysis_bars) >= 8:
        neutral = (106, 107, 104, 106) if direction == "bear" else (100, 102, 99, 100)
        analysis_bars = tuple(
            replace(
                bar,
                open_tick=neutral[0], high_tick=neutral[1], low_tick=neutral[2], close_tick=neutral[3],
            ) if bar.index >= 7 else bar
            for bar in analysis_bars
        )
    bars = analysis_bars
    if full_session_edges:
        analysis_bars = tuple(replace(bar, index=bar.index + 1) for bar in analysis_bars)
        bars = (
            GCChronologicalBar(0, _utc(trade_date, 4, 5), 100, 101, 99, 100, 9, True),
            *analysis_bars,
            GCChronologicalBar(
                len(analysis_bars) + 1,
                _utc(trade_date, 10, 5),
                106,
                107,
                105,
                106,
                11,
                True,
            ),
        )
    segment_id = _h(segment_seed)
    segment = GCCanonicalContractSegment(
        segment_id, "GCG26-COMEX", GCSegmentPartition.DEVELOPMENT,
        trade_date, trade_date, (_h("source"),), bars, 0,
    )
    dataset_id = _h("dataset")
    manifest = GCDatasetManifest(
        dataset_id, "GC-DATASET-V1", (_h("source"),), (_h("coverage"),), _h("coverage-digest"),
        (segment_id,), CALENDAR_VERSION, TZDATA_VERSION, bars[0].timestamp, bars[-1].timestamp,
        bars[0].timestamp, bars[-1].timestamp, len(bars), len(bars), len(bars), 0, 0, 0, 0,
        sum(bar.volume for bar in bars), sum(bar.volume for bar in bars), 0,
        ((segment.contract, trade_date, sum(bar.volume for bar in bars)),), (), (),
    )
    dataset = GCDatasetBuildResult(GCDatasetBuildStatus.VALID, dataset_id, (segment,), manifest)
    split_calendar = (
        GCSplitSessionCalendarEntry(
            CALENDAR_VERSION, trade_date,
            (GCDatasetSessionInterval(opening, session_close),),
            (_h("calendar-source"),), (_h("calendar-sha"),),
        ),
    )
    kill_calendar = (
        KillZoneCalendarEntry(CALENDAR_VERSION, trade_date, KillZoneSessionStatus.OPEN, opening, session_close),
    )
    split_digest = sweep_reclaim._split_calendar_digest(split_calendar)
    kill_digest = sweep_reclaim._kill_calendar_digest(kill_calendar)
    observations: list[sweep_reclaim.GCNYAMSweepReclaimObservation] = []
    contexts: list[KillZoneContext] = []
    snapshots: list[KillZoneSnapshot] = []
    for bar in analysis_bars:
        bar_open = bar.timestamp - timedelta(minutes=5)
        local_open = bar_open.astimezone(NY)
        local_close = bar.timestamp.astimezone(NY)
        if not (
            local_open.date() == trade_date
            and local_close.date() == trade_date
            and time(7, 0) <= local_open.time().replace(tzinfo=None) < time(10, 0)
            and time(7, 0) <= local_close.time().replace(tzinfo=None) < time(10, 0)
        ):
            continue
        context_id = make_kill_zone_id(
            identity_kind="CONTEXT",
            instrument="GC", timeframe="5M", calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York", timezone_data_version=TZDATA_VERSION,
            observation_index=bar.index, observation_timestamp=bar.timestamp, trade_date=trade_date,
            zone=KillZoneName.NEW_YORK_AM, session_status=KillZoneSessionStatus.OPEN,
            quality=KillZoneQuality.VERIFIED,
        )
        snapshot_id = make_kill_zone_id(
            identity_kind="SNAPSHOT",
            instrument="GC", timeframe="5M", calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York", timezone_data_version=TZDATA_VERSION,
            effective_index=bar.index, effective_timestamp=bar.timestamp,
            context_ids=tuple(item.context_id for item in contexts) + (context_id,),
        )
        observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
            identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
            instrument="GC", timeframe="5M", dataset_id=dataset_id,
            calendar_version=CALENDAR_VERSION, split_session_calendar_digest=split_digest,
            kill_zone_calendar_digest=kill_digest, timezone_name="America/New_York",
            timezone_data_version=TZDATA_VERSION,
            segment_ordinal=0, segment_id=segment_id, contract=segment.contract,
            trade_date=trade_date, index=bar.index, bar_open_timestamp=bar_open,
            bar_close_timestamp=bar.timestamp, open_tick=bar.open_tick, high_tick=bar.high_tick,
            low_tick=bar.low_tick, close_tick=bar.close_tick, volume=bar.volume, is_closed=True,
            kill_zone_context_id=context_id, kill_zone_snapshot_id=snapshot_id,
        )
        observations.append(sweep_reclaim.GCNYAMSweepReclaimObservation(
            observation_id, 0, segment_id, segment.contract, trade_date, bar.index,
            bar_open, bar.timestamp, bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick,
            bar.volume, True, context_id, snapshot_id,
        ))
        contexts.append(KillZoneContext(
            context_id, bar.index, bar.timestamp, trade_date, KillZoneName.NEW_YORK_AM,
            KillZoneSessionStatus.OPEN, KillZoneQuality.VERIFIED, CALENDAR_VERSION,
            "America/New_York", TZDATA_VERSION,
        ))
        snapshots.append(KillZoneSnapshot(
            snapshot_id,
            bar.index,
            bar.timestamp,
            tuple(item.context_id for item in contexts),
        ))
    return {
        "instrument": "GC", "timeframe": "5M", "dataset_config": _config(),
        "dataset_result": dataset, "observations": tuple(observations),
        "split_session_calendar": split_calendar, "kill_zone_calendar": kill_calendar,
        "kill_zone_contexts": tuple(contexts), "kill_zone_snapshots": tuple(snapshots),
        "kill_zone_result": KillZoneResult(SMCV2PrimitiveStatus.VALID, tuple(contexts), tuple(snapshots)),
        "requested_trade_dates": (trade_date,),
    }


def _two_segment_reset_fixture() -> dict[str, object]:
    """Build two canonical days whose public local indices both begin at zero."""
    first = _fixture(count=5, trade_date=TRADE_DATE, segment_seed="segment-a")
    second_day = TRADE_DATE + timedelta(days=1)
    second = _fixture(count=5, trade_date=second_day, segment_seed="segment-b")
    first_dataset = first["dataset_result"]
    second_dataset = second["dataset_result"]
    segments = first_dataset.segments + second_dataset.segments  # type: ignore[union-attr]
    dataset_id = _h("two-segment-reset-dataset")
    first_manifest = first_dataset.manifest  # type: ignore[union-attr]
    bars = tuple(bar for segment in segments for bar in segment.bars)
    manifest = replace(
        first_manifest,
        dataset_id=dataset_id,
        segment_ids=tuple(segment.segment_id for segment in segments),
        raw_start_timestamp=bars[0].timestamp,
        raw_end_timestamp=bars[-1].timestamp,
        usable_start_timestamp=bars[0].timestamp,
        usable_end_timestamp=bars[-1].timestamp,
        parsed_row_count=len(bars),
        eligible_row_count=len(bars),
        development_bar_count=len(bars),
        raw_volume=sum(bar.volume for bar in bars),
        eligible_volume=sum(bar.volume for bar in bars),
        completed_session_volumes=tuple(
            (segment.contract, segment.first_trade_date, sum(bar.volume for bar in segment.bars))
            for segment in segments
        ),
    )
    dataset = replace(first_dataset, dataset_id=dataset_id, segments=segments, manifest=manifest)  # type: ignore[arg-type]
    split_calendar = first["split_session_calendar"] + second["split_session_calendar"]  # type: ignore[operator]
    kill_calendar = first["kill_zone_calendar"] + second["kill_zone_calendar"]  # type: ignore[operator]
    contexts = first["kill_zone_contexts"] + second["kill_zone_contexts"]  # type: ignore[operator]
    snapshots = first["kill_zone_snapshots"] + second["kill_zone_snapshots"]  # type: ignore[operator]
    common = {
        "instrument": "GC",
        "timeframe": "5M",
        "dataset_id": dataset_id,
        "calendar_version": CALENDAR_VERSION,
        "split_session_calendar_digest": sweep_reclaim._split_calendar_digest(split_calendar),
        "kill_zone_calendar_digest": sweep_reclaim._kill_calendar_digest(kill_calendar),
        "timezone_name": "America/New_York",
        "timezone_data_version": TZDATA_VERSION,
    }
    observations: list[sweep_reclaim.GCNYAMSweepReclaimObservation] = []
    for ordinal, source in enumerate((first, second)):
        for item in source["observations"]:  # type: ignore[union-attr]
            observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
                identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                **common,
                segment_ordinal=ordinal,
                segment_id=item.segment_id,
                contract=item.contract,
                trade_date=item.trade_date,
                index=item.index,
                bar_open_timestamp=item.bar_open_timestamp,
                bar_close_timestamp=item.bar_close_timestamp,
                open_tick=item.open_tick,
                high_tick=item.high_tick,
                low_tick=item.low_tick,
                close_tick=item.close_tick,
                volume=item.volume,
                is_closed=item.is_closed,
                kill_zone_context_id=item.kill_zone_context_id,
                kill_zone_snapshot_id=item.kill_zone_snapshot_id,
            )
            observations.append(replace(item, segment_ordinal=ordinal, observation_id=observation_id))
    return {
        "instrument": "GC",
        "timeframe": "5M",
        "dataset_config": _config(),
        "dataset_result": dataset,
        "requested_trade_dates": (TRADE_DATE, second_day),
        "split_session_calendar": split_calendar,
        "kill_zone_calendar": kill_calendar,
        "observations": tuple(observations),
        "kill_zone_contexts": contexts,
        "kill_zone_snapshots": snapshots,
        "kill_zone_result": KillZoneResult(SMCV2PrimitiveStatus.VALID, contexts, snapshots),
    }


def _attested_opening_range_gap_fixture(
    *,
    corrupt_attestation: bool = False,
    trade_date: date = TRADE_DATE,
) -> dict[str, object]:
    """Build a canonical gap with only the 07:20 source member and later evidence."""
    base = _fixture(trade_date=trade_date)
    split_calendar = base["split_session_calendar"]
    kill_calendar = base["kill_zone_calendar"]
    contract = "GCG26-COMEX"
    source_ids = (_h("source"),)
    segment_specs = (
        (f"attested-pre-{trade_date}", 0, (GCChronologicalBar(0, _utc(trade_date, 6, 55), 100, 101, 99, 100, 9, True),)),
        (f"attested-range-{trade_date}", 0 if corrupt_attestation else 5, (GCChronologicalBar(0, _utc(trade_date, 7, 25), 104, 106, 103, 105, 14, True),)),
        (
            f"attested-later-{trade_date}",
            1,
            tuple(
                GCChronologicalBar(index, _utc(trade_date, 7, 35 + 5 * index), 106, 107, 104, 106, 15 + index, True)
                for index in range(4)
            ),
        ),
    )
    segments = tuple(
        GCCanonicalContractSegment(
            _h(seed), contract, GCSegmentPartition.DEVELOPMENT, trade_date, trade_date,
            source_ids, bars, missing,
        )
        for seed, missing, bars in segment_specs
    )
    all_bars = tuple(bar for segment in segments for bar in segment.bars)
    dataset_id = _h(f"attested-gap-dataset-{trade_date}-{'corrupt' if corrupt_attestation else 'valid'}")
    manifest = GCDatasetManifest(
        dataset_id, "GC-DATASET-V1", source_ids, (_h("coverage"),), _h("coverage-digest"),
        tuple(segment.segment_id for segment in segments), CALENDAR_VERSION, TZDATA_VERSION,
        all_bars[0].timestamp, all_bars[-1].timestamp, all_bars[0].timestamp, all_bars[-1].timestamp,
        len(all_bars), len(all_bars), len(all_bars), 0, 0,
        1 if corrupt_attestation else 6, 1 if corrupt_attestation else 2,
        sum(bar.volume for bar in all_bars), sum(bar.volume for bar in all_bars), 0,
        ((contract, trade_date, sum(bar.volume for bar in all_bars)),), (), (),
    )
    dataset = GCDatasetBuildResult(GCDatasetBuildStatus.VALID, dataset_id, segments, manifest)
    common = {
        "instrument": "GC", "timeframe": "5M", "dataset_id": dataset_id,
        "calendar_version": CALENDAR_VERSION,
        "split_session_calendar_digest": sweep_reclaim._split_calendar_digest(split_calendar),
        "kill_zone_calendar_digest": sweep_reclaim._kill_calendar_digest(kill_calendar),
        "timezone_name": "America/New_York", "timezone_data_version": TZDATA_VERSION,
    }
    observations: list[sweep_reclaim.GCNYAMSweepReclaimObservation] = []
    contexts: list[KillZoneContext] = []
    snapshots: list[KillZoneSnapshot] = []
    for ordinal, segment in enumerate(segments):
        segment_context_ids: list[str] = []
        for bar in segment.bars:
            bar_open = bar.timestamp - timedelta(minutes=5)
            if not (time(7, 0) <= bar_open.astimezone(NY).time().replace(tzinfo=None) < time(10, 0)):
                continue
            context_id = make_kill_zone_id(
                identity_kind="CONTEXT", instrument="GC", timeframe="5M",
                calendar_version=CALENDAR_VERSION, timezone_name="America/New_York",
                timezone_data_version=TZDATA_VERSION, observation_index=bar.index,
                observation_timestamp=bar.timestamp, trade_date=trade_date,
                zone=KillZoneName.NEW_YORK_AM, session_status=KillZoneSessionStatus.OPEN,
                quality=KillZoneQuality.VERIFIED,
            )
            segment_context_ids.append(context_id)
            snapshot_id = make_kill_zone_id(
                identity_kind="SNAPSHOT", instrument="GC", timeframe="5M",
                calendar_version=CALENDAR_VERSION, timezone_name="America/New_York",
                timezone_data_version=TZDATA_VERSION, effective_index=bar.index,
                effective_timestamp=bar.timestamp, context_ids=tuple(segment_context_ids),
            )
            observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
                identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                **common, segment_ordinal=ordinal, segment_id=segment.segment_id,
                contract=contract, trade_date=trade_date, index=bar.index,
                bar_open_timestamp=bar_open, bar_close_timestamp=bar.timestamp,
                open_tick=bar.open_tick, high_tick=bar.high_tick, low_tick=bar.low_tick,
                close_tick=bar.close_tick, volume=bar.volume, is_closed=True,
                kill_zone_context_id=context_id, kill_zone_snapshot_id=snapshot_id,
            )
            observations.append(sweep_reclaim.GCNYAMSweepReclaimObservation(
                observation_id, ordinal, segment.segment_id, contract, trade_date, bar.index,
                bar_open, bar.timestamp, bar.open_tick, bar.high_tick, bar.low_tick,
                bar.close_tick, bar.volume, True, context_id, snapshot_id,
            ))
            contexts.append(KillZoneContext(
                context_id, bar.index, bar.timestamp, trade_date, KillZoneName.NEW_YORK_AM,
                KillZoneSessionStatus.OPEN, KillZoneQuality.VERIFIED, CALENDAR_VERSION,
                "America/New_York", TZDATA_VERSION,
            ))
            snapshots.append(KillZoneSnapshot(snapshot_id, bar.index, bar.timestamp, tuple(segment_context_ids)))
    return {
        "instrument": "GC", "timeframe": "5M", "dataset_config": _config(),
        "dataset_result": dataset, "requested_trade_dates": (trade_date,),
        "split_session_calendar": split_calendar, "kill_zone_calendar": kill_calendar,
        "observations": tuple(observations), "kill_zone_contexts": tuple(contexts),
        "kill_zone_snapshots": tuple(snapshots),
        "kill_zone_result": KillZoneResult(SMCV2PrimitiveStatus.VALID, tuple(contexts), tuple(snapshots)),
    }


def _combine_date_fixtures(first: dict[str, object], second: dict[str, object]) -> dict[str, object]:
    first_dataset = first["dataset_result"]
    second_dataset = second["dataset_result"]
    segments = first_dataset.segments + second_dataset.segments  # type: ignore[union-attr]
    dataset_id = _h("combined-complete-attested-dataset")
    bars = tuple(bar for segment in segments for bar in segment.bars)
    first_manifest = first_dataset.manifest  # type: ignore[union-attr]
    second_manifest = second_dataset.manifest  # type: ignore[union-attr]
    manifest = replace(
        first_manifest,
        dataset_id=dataset_id,
        segment_ids=tuple(segment.segment_id for segment in segments),
        raw_start_timestamp=bars[0].timestamp,
        raw_end_timestamp=bars[-1].timestamp,
        usable_start_timestamp=bars[0].timestamp,
        usable_end_timestamp=bars[-1].timestamp,
        parsed_row_count=len(bars),
        eligible_row_count=len(bars),
        development_bar_count=len(bars),
        missing_bar_count=first_manifest.missing_bar_count + second_manifest.missing_bar_count,
        attested_no_trade_interval_count=(
            first_manifest.attested_no_trade_interval_count
            + second_manifest.attested_no_trade_interval_count
        ),
        raw_volume=sum(bar.volume for bar in bars),
        eligible_volume=sum(bar.volume for bar in bars),
        completed_session_volumes=(
            first_manifest.completed_session_volumes + second_manifest.completed_session_volumes
        ),
    )
    dataset = replace(first_dataset, dataset_id=dataset_id, segments=segments, manifest=manifest)  # type: ignore[arg-type]
    split_calendar = first["split_session_calendar"] + second["split_session_calendar"]  # type: ignore[operator]
    kill_calendar = first["kill_zone_calendar"] + second["kill_zone_calendar"]  # type: ignore[operator]
    contexts = first["kill_zone_contexts"] + second["kill_zone_contexts"]  # type: ignore[operator]
    snapshots = first["kill_zone_snapshots"] + second["kill_zone_snapshots"]  # type: ignore[operator]
    common = {
        "instrument": "GC", "timeframe": "5M", "dataset_id": dataset_id,
        "calendar_version": CALENDAR_VERSION,
        "split_session_calendar_digest": sweep_reclaim._split_calendar_digest(split_calendar),
        "kill_zone_calendar_digest": sweep_reclaim._kill_calendar_digest(kill_calendar),
        "timezone_name": "America/New_York", "timezone_data_version": TZDATA_VERSION,
    }
    observations: list[sweep_reclaim.GCNYAMSweepReclaimObservation] = []
    ordinal_offset = 0
    for source in (first, second):
        for item in source["observations"]:  # type: ignore[union-attr]
            ordinal = item.segment_ordinal + ordinal_offset
            observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
                identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                **common, segment_ordinal=ordinal, segment_id=item.segment_id,
                contract=item.contract, trade_date=item.trade_date, index=item.index,
                bar_open_timestamp=item.bar_open_timestamp, bar_close_timestamp=item.bar_close_timestamp,
                open_tick=item.open_tick, high_tick=item.high_tick, low_tick=item.low_tick,
                close_tick=item.close_tick, volume=item.volume, is_closed=item.is_closed,
                kill_zone_context_id=item.kill_zone_context_id,
                kill_zone_snapshot_id=item.kill_zone_snapshot_id,
            )
            observations.append(replace(item, segment_ordinal=ordinal, observation_id=observation_id))
        ordinal_offset += len(source["dataset_result"].segments)  # type: ignore[union-attr]
    return {
        "instrument": "GC", "timeframe": "5M", "dataset_config": _config(),
        "dataset_result": dataset,
        "requested_trade_dates": first["requested_trade_dates"] + second["requested_trade_dates"],  # type: ignore[operator]
        "split_session_calendar": split_calendar, "kill_zone_calendar": kill_calendar,
        "observations": tuple(observations), "kill_zone_contexts": contexts,
        "kill_zone_snapshots": snapshots,
        "kill_zone_result": KillZoneResult(SMCV2PrimitiveStatus.VALID, contexts, snapshots),
    }


def _run(fixture: dict[str, object], **changes: object) -> sweep_reclaim.GCNYAMSweepReclaimResult:
    supplied = dict(fixture)
    supplied.update(changes)
    return sweep_reclaim.analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(**supplied)  # type: ignore[arg-type]


def _valid() -> sweep_reclaim.GCNYAMSweepReclaimResult:
    return _run(_fixture())


def _identity_common(fixture: dict[str, object]) -> dict[str, object]:
    dataset = fixture["dataset_result"]
    return {
        "instrument": "GC", "timeframe": "5M", "dataset_id": dataset.dataset_id,
        "calendar_version": CALENDAR_VERSION,
        "split_session_calendar_digest": sweep_reclaim._split_calendar_digest(fixture["split_session_calendar"]),
        "kill_zone_calendar_digest": sweep_reclaim._kill_calendar_digest(fixture["kill_zone_calendar"]),
        "timezone_name": "America/New_York", "timezone_data_version": TZDATA_VERSION,
    }


def _identity_payloads() -> dict[sweep_reclaim.GCNYAMSweepReclaimIdentityKind, dict[str, object]]:
    fixture = _fixture()
    result = _run(fixture)
    observation = fixture["observations"][0]  # type: ignore[index]
    range_item = result.opening_ranges[0]
    candidate = result.candidates[0]
    outcome = result.outcomes[0]
    manifest = result.manifest
    assert manifest is not None
    common = _identity_common(fixture)
    return {
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION: {
            "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION, **common,
            "segment_ordinal": observation.segment_ordinal, "segment_id": observation.segment_id,
            "contract": observation.contract, "trade_date": observation.trade_date,
            "index": observation.index, "bar_open_timestamp": observation.bar_open_timestamp,
            "bar_close_timestamp": observation.bar_close_timestamp, "open_tick": observation.open_tick,
            "high_tick": observation.high_tick, "low_tick": observation.low_tick,
            "close_tick": observation.close_tick, "volume": observation.volume,
            "is_closed": observation.is_closed, "kill_zone_context_id": observation.kill_zone_context_id,
            "kill_zone_snapshot_id": observation.kill_zone_snapshot_id,
        },
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OPENING_RANGE: {
            "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OPENING_RANGE, **common,
            "segment_ordinal": range_item.segment_ordinal, "segment_id": range_item.segment_id,
            "contract": range_item.contract, "trade_date": range_item.trade_date,
            "source_observation_ids": range_item.source_observation_ids,
            "source_context_ids": range_item.source_context_ids,
            "source_snapshot_ids": range_item.source_snapshot_ids,
            "first_known_index": range_item.first_known_index,
            "first_known_timestamp": range_item.first_known_timestamp,
            "high_tick": range_item.high_tick, "low_tick": range_item.low_tick,
            "midpoint_tick": range_item.midpoint_tick, "width_ticks": range_item.width_ticks,
        },
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.CANDIDATE: {
            "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.CANDIDATE, **common,
            "range_id": candidate.range_id, "segment_ordinal": candidate.segment_ordinal,
            "segment_id": candidate.segment_id, "contract": candidate.contract,
            "trade_date": candidate.trade_date, "direction": candidate.direction,
            "formation_observation_id": candidate.formation_observation_id,
            "formation_context_id": candidate.formation_context_id,
            "formation_snapshot_id": candidate.formation_snapshot_id,
            "formation_index": candidate.formation_index,
            "first_known_timestamp": candidate.first_known_timestamp,
            "swept_boundary_tick": candidate.swept_boundary_tick,
            "sweep_extreme_tick": candidate.sweep_extreme_tick,
            "reclaim_close_tick": candidate.reclaim_close_tick,
            "midpoint_tick": candidate.midpoint_tick,
            "invalidation_tick": candidate.invalidation_tick,
            "width_ticks": candidate.width_ticks,
        },
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OUTCOME: {
            "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OUTCOME, **common,
            "candidate_id": outcome.candidate_id, "outcome": outcome.outcome,
            "first_known_index": outcome.first_known_index,
            "first_known_timestamp": outcome.first_known_timestamp,
            "horizon_observation_ids": outcome.horizon_observation_ids,
            "event_observation_id": outcome.event_observation_id,
        },
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.MANIFEST: {
            "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.MANIFEST, **common,
            "version": manifest.version,
            "requested_trade_dates": manifest.requested_trade_dates,
            "opening_range_ids": manifest.opening_range_ids, "candidate_ids": manifest.candidate_ids,
            "outcome_ids": manifest.outcome_ids, "count_funnel": manifest.count_funnel,
            "reason_counts": manifest.reason_counts,
        },
    }


def _assert_required_and_forbidden_schema(
    kind: sweep_reclaim.GCNYAMSweepReclaimIdentityKind,
    allowed_specific: set[str],
) -> None:
    payloads = _identity_payloads()
    payload = payloads[kind]
    common = {
        "identity_kind", "instrument", "timeframe", "dataset_id", "calendar_version",
        "split_session_calendar_digest", "kill_zone_calendar_digest", "timezone_name",
        "timezone_data_version",
    }
    for name in common:
        missing = dict(payload)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**missing)  # type: ignore[arg-type]
    for name in allowed_specific:
        if kind is sweep_reclaim.GCNYAMSweepReclaimIdentityKind.MANIFEST and name in {
            "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids", "reason_counts",
        }:
            continue
        if name not in payload or payload[name] in ((), None):
            continue
        missing = dict(payload)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**missing)  # type: ignore[arg-type]
    witnesses: dict[str, object] = {}
    for candidate_payload in payloads.values():
        witnesses.update(candidate_payload)
    witnesses["reason_counts"] = (("NO_SWEEP_RECLAIM", 1),)
    builder_specific = set(inspect.signature(sweep_reclaim.make_gc_ny_am_sweep_reclaim_id).parameters) - common
    for name in builder_specific - allowed_specific:
        forbidden = dict(payload)
        forbidden[name] = witnesses[name]
        with pytest.raises((TypeError, ValueError)):
            sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**forbidden)  # type: ignore[arg-type]


def _with_prices(fixture: dict[str, object], position: int, **changes: int) -> dict[str, object]:
    dataset = fixture["dataset_result"]
    segment = dataset.segments[0]
    bars = list(segment.bars)
    bars[position] = replace(bars[position], **changes)
    updated_segment = replace(segment, bars=tuple(bars))
    updated_dataset = replace(dataset, segments=(updated_segment,))
    observations = list(fixture["observations"])
    item = replace(observations[position], **changes)
    common = _identity_common(fixture)
    observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
        identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
        **common,
        segment_ordinal=item.segment_ordinal,
        segment_id=item.segment_id,
        contract=item.contract,
        trade_date=item.trade_date,
        index=item.index,
        bar_open_timestamp=item.bar_open_timestamp,
        bar_close_timestamp=item.bar_close_timestamp,
        open_tick=item.open_tick,
        high_tick=item.high_tick,
        low_tick=item.low_tick,
        close_tick=item.close_tick,
        volume=item.volume,
        is_closed=item.is_closed,
        kill_zone_context_id=item.kill_zone_context_id,
        kill_zone_snapshot_id=item.kill_zone_snapshot_id,
    )
    observations[position] = replace(item, observation_id=observation_id)
    updated = dict(fixture)
    updated["dataset_result"] = updated_dataset
    updated["observations"] = tuple(observations)
    return updated


def _with_calendars(
    fixture: dict[str, object],
    *,
    split_session_calendar: tuple[GCSplitSessionCalendarEntry, ...] | None = None,
    kill_zone_calendar: tuple[KillZoneCalendarEntry, ...] | None = None,
) -> dict[str, object]:
    """Rebind observation identities after an identity-bearing calendar change."""
    updated = dict(fixture)
    if split_session_calendar is not None:
        updated["split_session_calendar"] = split_session_calendar
    if kill_zone_calendar is not None:
        updated["kill_zone_calendar"] = kill_zone_calendar
    common = _identity_common(updated)
    observations: list[sweep_reclaim.GCNYAMSweepReclaimObservation] = []
    for item in fixture["observations"]:  # type: ignore[union-attr]
        observation_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
            identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
            **common,
            segment_ordinal=item.segment_ordinal,
            segment_id=item.segment_id,
            contract=item.contract,
            trade_date=item.trade_date,
            index=item.index,
            bar_open_timestamp=item.bar_open_timestamp,
            bar_close_timestamp=item.bar_close_timestamp,
            open_tick=item.open_tick,
            high_tick=item.high_tick,
            low_tick=item.low_tick,
            close_tick=item.close_tick,
            volume=item.volume,
            is_closed=item.is_closed,
            kill_zone_context_id=item.kill_zone_context_id,
            kill_zone_snapshot_id=item.kill_zone_snapshot_id,
        )
        observations.append(replace(item, observation_id=observation_id))
    updated["observations"] = tuple(observations)
    return updated


# Logical cases 1-48.  Each numbered function maps one-to-one to the locked proposal matrix.
def test_case_01_missing_bars_or_calendar_is_unknown_without_range() -> None:
    fixture = _fixture()
    for change in ({"dataset_result": None}, {"split_session_calendar": None}, {"kill_zone_calendar": None}):
        result = _run(fixture, **change)
        assert result.status is SMCV2PrimitiveStatus.UNKNOWN
        assert not result.opening_ranges and not result.candidates and not result.outcomes


def test_case_02_malformed_supplied_counterpart_outranks_missing_unknown() -> None:
    fixture = _fixture()
    bad_observation = replace(fixture["observations"][0], observation_id="bad")  # type: ignore[index]
    malformed_context = replace(fixture["kill_zone_contexts"][0], context_id="bad")  # type: ignore[index]
    malformed_snapshot = replace(fixture["kill_zone_snapshots"][0], snapshot_id="bad")  # type: ignore[index]
    for changes in (
        {"dataset_result": None, "observations": (bad_observation,)},
        {"observations": None, "kill_zone_contexts": (malformed_context,)},
        {"observations": None, "kill_zone_snapshots": (malformed_snapshot,)},
    ):
        result = _run(fixture, **changes)
        assert result.status is SMCV2PrimitiveStatus.INVALID
        assert not result.opening_ranges and not result.candidates and not result.outcomes


def test_case_03_observation_tuple_duplicates_reordering_and_forks() -> None:
    fixture = _fixture()
    observations = fixture["observations"]  # type: ignore[assignment]
    assert _run(fixture, observations=list(observations)).status is SMCV2PrimitiveStatus.INVALID
    assert _run(fixture, observations=(observations[1], observations[0]) + observations[2:]).status is SMCV2PrimitiveStatus.INVALID
    fork = replace(observations[1], observation_id="OBSERVATION:" + _h("fork"), close_tick=101)
    assert _run(fixture, observations=(observations[0], observations[1], fork) + observations[2:]).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("change", (
    {"high_tick": True}, {"low_tick": Decimal("99")}, {"volume": -1},
    {"volume": Decimal("1.5")}, {"close_tick": float("inf")}, {"is_closed": False},
))
def test_case_04_malformed_numeric_and_closed_bar_evidence_fails_closed(change: dict[str, object]) -> None:
    fixture = _fixture()
    bad = replace(fixture["observations"][0], **change)  # type: ignore[index]
    result = _run(fixture, observations=(bad,) + fixture["observations"][1:])  # type: ignore[index]
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_05_naive_timestamp_and_timezone_version_mismatch_fail() -> None:
    fixture = _fixture()
    naive = replace(fixture["observations"][0], bar_open_timestamp=datetime(2026, 1, 6, 7))  # type: ignore[index]
    assert _run(fixture, observations=(naive,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]
    assert _run(fixture, dataset_config=_config(exchange_timezone="UTC")).status is SMCV2PrimitiveStatus.INVALID
    assert _run(fixture, dataset_config=_config(timezone_data_version="0.0")).status is SMCV2PrimitiveStatus.INVALID
    assert fixture["kill_zone_contexts"][0].observation_timestamp == fixture["observations"][0].bar_close_timestamp  # type: ignore[index]
    at_open = replace(
        fixture["kill_zone_contexts"][0],  # type: ignore[index]
        observation_timestamp=fixture["observations"][0].bar_open_timestamp,  # type: ignore[index]
    )
    assert _run(
        fixture,
        kill_zone_contexts=(at_open,) + fixture["kill_zone_contexts"][1:],  # type: ignore[index]
        kill_zone_result=KillZoneResult(
            SMCV2PrimitiveStatus.VALID,
            (at_open,) + fixture["kill_zone_contexts"][1:],  # type: ignore[index]
            fixture["kill_zone_snapshots"],  # type: ignore[arg-type]
        ),
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("contract", ("MGCJ26-COMEX", "XAUUSD", "GC", "GCJ26-CME", "GCJ26-COMEX-OPT"))
def test_case_06_only_unambiguous_gc_outright_contract_is_accepted(contract: str) -> None:
    fixture = _fixture()
    dataset = fixture["dataset_result"]
    segment = replace(dataset.segments[0], contract=contract)  # type: ignore[union-attr]
    assert _run(fixture, dataset_result=replace(dataset, segments=(segment,))).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[arg-type]


def test_case_07_only_closed_five_minute_single_contract_source_is_accepted() -> None:
    fixture = _fixture()
    assert _run(fixture, dataset_config=_config(timeframe="1M")).status is SMCV2PrimitiveStatus.INVALID
    unfinished = replace(fixture["observations"][0], is_closed=False)  # type: ignore[index]
    assert _run(fixture, observations=(unfinished,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]
    oos_segment = replace(fixture["dataset_result"].segments[0], partition=GCSegmentPartition.OOS_HOLDOUT)  # type: ignore[union-attr]
    assert _run(fixture, dataset_result=replace(fixture["dataset_result"], segments=(oos_segment,))).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[arg-type]


def test_case_08_calendar_missing_closed_and_malformed_semantics() -> None:
    fixture = _fixture()
    assert _run(fixture, split_session_calendar=()).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _run(fixture, kill_zone_calendar=()).status is SMCV2PrimitiveStatus.UNKNOWN
    closed = replace(
        fixture["kill_zone_calendar"][0], session_status=KillZoneSessionStatus.SESSION_CLOSED,
        session_open_timestamp=None, session_close_timestamp=None,
    )  # type: ignore[index]
    assert _run(_with_calendars(fixture, kill_zone_calendar=(closed,))).status is SMCV2PrimitiveStatus.NONE
    malformed = replace(fixture["split_session_calendar"][0], intervals=())  # type: ignore[index]
    assert _run(fixture, split_session_calendar=(malformed,)).status is SMCV2PrimitiveStatus.INVALID


def test_case_09_early_close_preventing_source_or_horizon_is_ineligible() -> None:
    fixture = _fixture()
    kill_entry = fixture["kill_zone_calendar"][0]  # type: ignore[index]
    for closing in (_utc(TRADE_DATE, 7, 20), _utc(TRADE_DATE, 9, 59)):
        early = replace(kill_entry, session_status=KillZoneSessionStatus.EARLY_CLOSE, session_close_timestamp=closing)
        result = _run(_with_calendars(fixture, kill_zone_calendar=(early,)))
        assert result.status is SMCV2PrimitiveStatus.NONE
        assert result.reasons == ("SESSION_INELIGIBLE",)
    reset_result = _run(_two_segment_reset_fixture())
    assert reset_result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert reset_result.reasons == ("INCOMPLETE_OPENING_RANGE",)
    attested = _run(_attested_opening_range_gap_fixture())
    assert attested.status is SMCV2PrimitiveStatus.NONE
    assert attested.reasons == ("ATTESTED_NO_TRADE_OPENING_RANGE",)


def test_case_10_exact_six_bar_opening_range_first_known_at_0730() -> None:
    item = _valid().opening_ranges[0]
    assert len(item.source_observation_ids) == 6
    assert (item.first_known_index, item.first_known_timestamp) == (5, _utc(TRADE_DATE, 7, 30))
    assert (item.low_tick, item.high_tick, item.midpoint_tick, item.width_ticks) == (99, 107, Decimal("103.0"), 8)


def test_case_11_five_bars_insufficient_and_seventh_never_enters_source() -> None:
    incomplete = _run(_fixture(count=5))
    assert incomplete.status is SMCV2PrimitiveStatus.UNKNOWN and not incomplete.opening_ranges
    complete = _valid().opening_ranges[0]
    assert complete.source_observation_ids == tuple(item.observation_id for item in _fixture()["observations"][:6])  # type: ignore[index]
    assert _fixture()["observations"][6].observation_id not in complete.source_observation_ids  # type: ignore[index]
    attested = _run(_attested_opening_range_gap_fixture())
    assert attested.status is SMCV2PrimitiveStatus.NONE
    assert not attested.opening_ranges and not attested.candidates and not attested.outcomes


def test_case_12_missing_middle_timestamp_substitution_and_nonconsecutive_source_invalid() -> None:
    fixture = _fixture()
    observations = fixture["observations"]  # type: ignore[assignment]
    assert _run(fixture, observations=observations[:2] + observations[3:]).status is SMCV2PrimitiveStatus.INVALID
    substituted = replace(observations[2], bar_open_timestamp=observations[2].bar_open_timestamp + timedelta(seconds=1))
    assert _run(fixture, observations=observations[:2] + (substituted,) + observations[3:]).status is SMCV2PrimitiveStatus.INVALID
    skipped = replace(observations[2], index=99)
    assert _run(fixture, observations=observations[:2] + (skipped,) + observations[3:]).status is SMCV2PrimitiveStatus.INVALID
    corrupted = _run(_attested_opening_range_gap_fixture(corrupt_attestation=True))
    assert corrupted.status is SMCV2PrimitiveStatus.INVALID
    assert corrupted.reasons == ("INVALID_OPENING_RANGE",)


def test_case_13_cross_date_segment_and_session_source_is_invalid() -> None:
    fixture = _fixture()
    first = fixture["observations"][0]  # type: ignore[index]
    for change in ({"trade_date": date(2026, 1, 7)}, {"segment_ordinal": 1}, {"contract": "GCJ26-COMEX"}):
        bad = replace(first, **change)
        assert _run(fixture, observations=(bad,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]


def test_case_14_positive_one_tick_range_valid_zero_width_invalid() -> None:
    one_tick = _fixture(direction="none")
    for position in range(6):
        one_tick = _with_prices(one_tick, position, open_tick=100, high_tick=101, low_tick=100, close_tick=100)
    assert _run(one_tick).opening_ranges[0].width_ticks == 1
    zero = _fixture(direction="none")
    for position in range(6):
        zero = _with_prices(zero, position, open_tick=100, high_tick=100, low_tick=100, close_tick=100)
    assert _run(zero).status is SMCV2PrimitiveStatus.INVALID


def test_case_15_exact_midpoint_signed_zero_and_arbitrary_magnitude_are_context_independent() -> None:
    payload = _identity_payloads()[sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OPENING_RANGE]
    identities: list[str] = []
    huge = 10**300
    for precision in (2, 6, 28):
        with localcontext() as context:
            context.prec = precision
            for high, low, midpoint in ((1, -1, Decimal("-0.0")), (huge + 1, huge, Decimal(f"{huge}.5")), (-huge, -huge - 1, Decimal(f"-{huge}.5"))):
                changed = dict(payload, high_tick=high, low_tick=low, midpoint_tick=midpoint, width_ticks=1 if high - low == 1 else 2)
                identities.append(sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**changed))
    assert identities[0] == identities[3] == identities[6]
    assert all(re.fullmatch(r"OPENING_RANGE:[0-9a-f]{64}", item) for item in identities)


def test_case_16_full_session_pre_nyam_bars_are_valid_but_not_expected_observations() -> None:
    fixture = _fixture(full_session_edges=True)
    dataset_bars = fixture["dataset_result"].segments[0].bars  # type: ignore[union-attr]
    observations = fixture["observations"]  # type: ignore[assignment]
    result = _run(fixture)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(dataset_bars) == len(observations) + 2
    assert dataset_bars[0].timestamp - timedelta(minutes=5) == _utc(TRADE_DATE, 4)
    assert dataset_bars[0].index not in {item.index for item in observations}
    assert result.candidates[0].formation_observation_id not in result.opening_ranges[0].source_observation_ids


def test_case_17_exact_nyam_membership_is_0700_inclusive_1000_exclusive() -> None:
    fixture = _fixture(count=36, full_session_edges=True)
    observations = fixture["observations"]  # type: ignore[assignment]
    dataset_bars = fixture["dataset_result"].segments[0].bars  # type: ignore[union-attr]
    result = _run(fixture)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(observations) == 35
    assert observations[0].bar_open_timestamp == _utc(TRADE_DATE, 7)
    assert observations[-1].bar_open_timestamp == _utc(TRADE_DATE, 9, 50)
    assert observations[-1].bar_close_timestamp == _utc(TRADE_DATE, 9, 55)
    terminal_bar = next(
        bar
        for bar in dataset_bars
        if bar.timestamp - timedelta(minutes=5) == _utc(TRADE_DATE, 9, 55)
    )
    assert terminal_bar.timestamp == _utc(TRADE_DATE, 10)
    assert terminal_bar.index not in {item.index for item in observations}
    with pytest.raises((TypeError, ValueError)):
        make_kill_zone_id(
            identity_kind="CONTEXT",
            instrument="GC",
            timeframe="5M",
            calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York",
            timezone_data_version=TZDATA_VERSION,
            observation_index=terminal_bar.index,
            observation_timestamp=terminal_bar.timestamp,
            trade_date=TRADE_DATE,
            zone=KillZoneName.NEW_YORK_AM,
            session_status=KillZoneSessionStatus.OPEN,
            quality=KillZoneQuality.VERIFIED,
        )
    assert dataset_bars[-1].timestamp - timedelta(minutes=5) == _utc(TRADE_DATE, 10)
    assert dataset_bars[-1].index not in {item.index for item in observations}


def test_case_18_nyam_projection_missing_extra_and_reordered_evidence_fails_closed() -> None:
    fixture = _fixture(full_session_edges=True)
    observations = fixture["observations"]  # type: ignore[assignment]
    contexts = fixture["kill_zone_contexts"]  # type: ignore[assignment]
    snapshots = fixture["kill_zone_snapshots"]  # type: ignore[assignment]
    assert _run(fixture, observations=observations[:3] + observations[4:]).status is SMCV2PrimitiveStatus.INVALID
    assert _run(
        fixture,
        kill_zone_contexts=(contexts[1], contexts[0]) + contexts[2:],
        kill_zone_result=KillZoneResult(
            SMCV2PrimitiveStatus.VALID,
            (contexts[1], contexts[0]) + contexts[2:],
            snapshots,
        ),
    ).status is SMCV2PrimitiveStatus.INVALID
    assert _run(
        fixture,
        kill_zone_snapshots=(snapshots[1], snapshots[0]) + snapshots[2:],
        kill_zone_result=KillZoneResult(
            SMCV2PrimitiveStatus.VALID,
            contexts,
            (snapshots[1], snapshots[0]) + snapshots[2:],
        ),
    ).status is SMCV2PrimitiveStatus.INVALID


def test_case_19_complete_non_nyam_member_is_valid_but_never_becomes_a_phase_b_observation() -> None:
    fixture = _fixture(full_session_edges=True)
    common = _identity_common(fixture)
    pre_bar = fixture["dataset_result"].segments[0].bars[0]  # type: ignore[union-attr]
    context_id = make_kill_zone_id(
        identity_kind="CONTEXT",
        instrument="GC",
        timeframe="5M",
        calendar_version=CALENDAR_VERSION,
        timezone_name="America/New_York",
        timezone_data_version=TZDATA_VERSION,
        observation_index=pre_bar.index,
        observation_timestamp=pre_bar.timestamp,
        trade_date=TRADE_DATE,
        zone=KillZoneName.LONDON,
        session_status=KillZoneSessionStatus.OPEN,
        quality=KillZoneQuality.VERIFIED,
    )
    snapshot_id = make_kill_zone_id(
        identity_kind="SNAPSHOT",
        instrument="GC",
        timeframe="5M",
        calendar_version=CALENDAR_VERSION,
        timezone_name="America/New_York",
        timezone_data_version=TZDATA_VERSION,
        effective_index=pre_bar.index,
        effective_timestamp=pre_bar.timestamp,
        context_ids=(context_id,),
    )
    extra_context = KillZoneContext(
        context_id,
        pre_bar.index,
        pre_bar.timestamp,
        TRADE_DATE,
        KillZoneName.LONDON,
        KillZoneSessionStatus.OPEN,
        KillZoneQuality.VERIFIED,
        CALENDAR_VERSION,
        common["timezone_name"],
        common["timezone_data_version"],
    )
    extra_snapshot = KillZoneSnapshot(snapshot_id, pre_bar.index, pre_bar.timestamp, (context_id,))
    contexts = (extra_context,) + fixture["kill_zone_contexts"]  # type: ignore[operator]
    snapshots = [extra_snapshot]
    for snapshot in fixture["kill_zone_snapshots"]:  # type: ignore[union-attr]
        history = (context_id,) + snapshot.context_ids
        rebound_id = make_kill_zone_id(
            identity_kind="SNAPSHOT",
            instrument="GC",
            timeframe="5M",
            calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York",
            timezone_data_version=TZDATA_VERSION,
            effective_index=snapshot.index,
            effective_timestamp=snapshot.timestamp,
            context_ids=history,
        )
        snapshots.append(KillZoneSnapshot(rebound_id, snapshot.index, snapshot.timestamp, history))
    rebound_observations = tuple(
        replace(
            item,
            kill_zone_snapshot_id=snapshot.snapshot_id,
            observation_id=sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
                identity_kind=sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION,
                **common,
                segment_ordinal=item.segment_ordinal,
                segment_id=item.segment_id,
                contract=item.contract,
                trade_date=item.trade_date,
                index=item.index,
                bar_open_timestamp=item.bar_open_timestamp,
                bar_close_timestamp=item.bar_close_timestamp,
                open_tick=item.open_tick,
                high_tick=item.high_tick,
                low_tick=item.low_tick,
                close_tick=item.close_tick,
                volume=item.volume,
                is_closed=item.is_closed,
                kill_zone_context_id=item.kill_zone_context_id,
                kill_zone_snapshot_id=snapshot.snapshot_id,
            ),
        )
        for item, snapshot in zip(fixture["observations"], snapshots[1:])  # type: ignore[arg-type]
    )
    snapshots_tuple = tuple(snapshots)
    result = _run(
        fixture,
        observations=rebound_observations,
        kill_zone_contexts=contexts,
        kill_zone_snapshots=snapshots_tuple,
        kill_zone_result=KillZoneResult(SMCV2PrimitiveStatus.VALID, contexts, snapshots_tuple),
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.opening_ranges and result.candidates and result.outcomes
    assert context_id not in {item.kill_zone_context_id for item in rebound_observations}


@pytest.mark.parametrize("changes", (
    {"high_tick": 107, "close_tick": 106},
    {"high_tick": 108, "low_tick": 103, "close_tick": 103},
    {"high_tick": 108, "close_tick": 108},
))
def test_case_20_boundary_miss_midpoint_equality_and_outside_close_are_non_candidates(changes: dict[str, int]) -> None:
    fixture = _with_prices(_fixture(direction="bear"), 6, **changes)
    result = _run(fixture)
    assert not result.candidates


def test_case_21_close_at_swept_boundary_qualifies_outside_close_does_not() -> None:
    boundary = _with_prices(_fixture(direction="bear"), 6, open_tick=106, high_tick=108, low_tick=104, close_tick=107)
    assert _run(boundary).candidates[0].reclaim_close_tick == 107
    outside = _with_prices(_fixture(direction="bear"), 6, open_tick=106, high_tick=108, low_tick=104, close_tick=108)
    assert not _run(outside).candidates


def test_case_22_outside_close_then_later_reclaim_cannot_relabel_prior_sweep() -> None:
    fixture = _with_prices(_fixture(direction="none"), 6, open_tick=106, high_tick=108, low_tick=104, close_tick=108)
    fixture = _with_prices(fixture, 7, open_tick=106, high_tick=107, low_tick=104, close_tick=106)
    assert not _run(fixture).candidates


def test_case_23_both_boundary_formation_is_ambiguous_and_atomic() -> None:
    result = _run(_fixture(collision=True))
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert result.opening_ranges and not result.candidates and not result.outcomes
    assert result.reasons == ("AMBIGUOUS_SWEEP_RECLAIM",)


def test_case_24_earliest_formation_wins_and_later_bars_are_outcome_only() -> None:
    fixture = _fixture(target_event=False)
    fixture = _with_prices(fixture, 8, open_tick=106, high_tick=109, low_tick=104, close_tick=106)
    result = _run(fixture)
    assert len(result.candidates) == 1 and result.candidates[0].formation_index == 6
    assert fixture["observations"][8].observation_id in result.outcomes[0].horizon_observation_ids  # type: ignore[index]


def test_case_25_exact_duplicates_collapse_but_forked_same_effective_evidence_is_invalid() -> None:
    fixture = _fixture()
    observations = fixture["observations"]  # type: ignore[assignment]
    duplicated = observations[:2] + (observations[1],) + observations[2:]
    assert _run(fixture, observations=duplicated) == _run(fixture)
    fork = replace(observations[1], observation_id="OBSERVATION:" + _h("fork"), close_tick=101)
    invalid = _run(fixture, observations=observations[:2] + (fork,) + observations[2:])
    assert invalid.status is SMCV2PrimitiveStatus.INVALID


def test_case_26_bullish_bearish_mirror_geometry_and_opposite_boundary_reconcile() -> None:
    bearish = _valid().candidates[0]
    bullish = _run(_fixture(direction="bull")).candidates[0]
    assert (bearish.invalidation_tick, bullish.invalidation_tick) == (109, 97)
    assert bearish.swept_boundary_tick - bearish.width_ticks == 99
    assert bullish.swept_boundary_tick + bullish.width_ticks == 107
    assert bearish.midpoint_tick == bullish.midpoint_tick == Decimal("103.0")


def test_case_27_bearish_candidate_fields_provenance_identity_and_immutability() -> None:
    candidate = _valid().candidates[0]
    payload = _identity_payloads()[sweep_reclaim.GCNYAMSweepReclaimIdentityKind.CANDIDATE]
    assert sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**payload) == candidate.candidate_id
    for field_name, changed_value in (("formation_index", candidate.formation_index + 1), ("formation_context_id", _h("other")), ("segment_id", _h("other-segment"))):
        assert sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**dict(payload, **{field_name: changed_value})) != candidate.candidate_id
    with pytest.raises(FrozenInstanceError):
        candidate.formation_index = 999  # type: ignore[misc]


def test_case_28_bullish_candidate_identity_and_impossible_geometry_rejection() -> None:
    fixture = _fixture(direction="bull")
    candidate = _run(fixture).candidates[0]
    payload = _identity_payloads()[sweep_reclaim.GCNYAMSweepReclaimIdentityKind.CANDIDATE]
    payload.update(
        direction=candidate.direction, formation_observation_id=candidate.formation_observation_id,
        formation_context_id=candidate.formation_context_id, formation_snapshot_id=candidate.formation_snapshot_id,
        swept_boundary_tick=candidate.swept_boundary_tick, sweep_extreme_tick=candidate.sweep_extreme_tick,
        reclaim_close_tick=candidate.reclaim_close_tick, invalidation_tick=candidate.invalidation_tick,
    )
    assert sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**payload).startswith("CANDIDATE:")
    with pytest.raises((TypeError, ValueError)):
        sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**dict(payload, midpoint_tick=Decimal("103.5")))


def test_case_29_formation_bar_is_excluded_from_outcome_evaluation() -> None:
    fixture = _with_prices(_fixture(target_event=False), 6, open_tick=106, high_tick=108, low_tick=100, close_tick=106)
    outcome = _run(fixture).outcomes[0]
    assert outcome.outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.TIMEOUT
    assert fixture["observations"][6].observation_id not in outcome.horizon_observation_ids  # type: ignore[index]


def test_case_30_outcome_horizon_is_next_exact_twelve_same_lineage_bars() -> None:
    fixture = _fixture(target_event=False)
    result = _run(fixture)
    outcome = result.outcomes[0]
    assert len(outcome.horizon_observation_ids) == 12
    expected = fixture["observations"][7:19]  # type: ignore[index]
    assert outcome.horizon_observation_ids == tuple(item.observation_id for item in expected)
    assert len({(item.segment_id, item.contract, item.trade_date) for item in expected}) == 1


def test_case_31_bearish_low_at_midpoint_is_target_equality() -> None:
    fixture = _with_prices(_fixture(target_event=False), 7, open_tick=106, high_tick=107, low_tick=103, close_tick=105)
    assert _run(fixture).outcomes[0].outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.MIDPOINT_REACHED


def test_case_32_bullish_high_at_midpoint_is_target_equality() -> None:
    fixture = _with_prices(_fixture(direction="bull", target_event=False), 7, open_tick=100, high_tick=103, low_tick=99, close_tick=101)
    assert _run(fixture).outcomes[0].outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.MIDPOINT_REACHED


def test_case_33_bearish_close_at_formation_high_plus_one_invalidates() -> None:
    fixture = _with_prices(_fixture(target_event=False), 7, open_tick=108, high_tick=110, low_tick=107, close_tick=109)
    assert _run(fixture).outcomes[0].outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.INVALIDATED


def test_case_34_bullish_close_at_formation_low_minus_one_invalidates() -> None:
    fixture = _with_prices(_fixture(direction="bull", target_event=False), 7, open_tick=98, high_tick=100, low_tick=97, close_tick=97)
    assert _run(fixture).outcomes[0].outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.INVALIDATED


def test_case_35_same_first_bar_target_and_invalidation_is_ambiguous_outcome() -> None:
    fixture = _with_prices(_fixture(target_event=False), 7, open_tick=108, high_tick=110, low_tick=103, close_tick=109)
    assert _run(fixture).outcomes[0].outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.SAME_BAR_AMBIGUOUS


def test_case_36_twelve_bars_with_neither_event_timeout() -> None:
    outcome = _run(_fixture(target_event=False)).outcomes[0]
    assert outcome.outcome is sweep_reclaim.GCNYAMSweepReclaimOutcomeType.TIMEOUT
    assert outcome.event_observation_id is None and len(outcome.horizon_observation_ids) == 12


def test_case_37_truncated_horizon_is_unknown_without_outcome_or_later_relabel() -> None:
    result = _run(_fixture(count=12, target_event=False))
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.candidates and not result.outcomes and result.manifest is None
    assert result.reasons == ("INCOMPLETE_OUTCOME_HORIZON",)


def test_case_38_later_malformed_group_preserves_strictly_prior_complete_evidence() -> None:
    fixture = _fixture()
    baseline = _run(fixture)
    values = list(fixture["observations"])  # type: ignore[arg-type]
    values[-1] = replace(values[-1], observation_id="bad")
    result = _run(fixture, observations=tuple(values))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.opening_ranges == baseline.opening_ranges
    assert result.candidates == baseline.candidates
    assert result.outcomes == baseline.outcomes
    assert result.manifest is None


def test_case_39_final_status_precedence_is_locked() -> None:
    invalid_fixture = _fixture(count=12, target_event=False)
    values = list(invalid_fixture["observations"])  # type: ignore[arg-type]
    values[-1] = replace(values[-1], observation_id="bad")
    assert _run(invalid_fixture, observations=tuple(values)).status is SMCV2PrimitiveStatus.INVALID
    assert _run(_fixture(collision=True)).status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert _run(_fixture(count=12, target_event=False)).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _valid().status is SMCV2PrimitiveStatus.VALID
    assert _run(_fixture(direction="none")).status is SMCV2PrimitiveStatus.NONE
    assert _run(_attested_opening_range_gap_fixture()).status is SMCV2PrimitiveStatus.NONE
    mixed = _run(_combine_date_fixtures(
        _fixture(trade_date=TRADE_DATE),
        _attested_opening_range_gap_fixture(trade_date=TRADE_DATE + timedelta(days=1)),
    ))
    assert mixed.status is SMCV2PrimitiveStatus.VALID
    assert len(mixed.opening_ranges) == len(mixed.candidates) == len(mixed.outcomes) == 1
    assert "ATTESTED_NO_TRADE_OPENING_RANGE" in mixed.reasons
    attested_then_incomplete = _run(_combine_date_fixtures(
        _attested_opening_range_gap_fixture(trade_date=TRADE_DATE),
        _fixture(trade_date=TRADE_DATE + timedelta(days=1), count=5),
    ))
    assert attested_then_incomplete.status is SMCV2PrimitiveStatus.UNKNOWN
    assert attested_then_incomplete.reasons == (
        "ATTESTED_NO_TRADE_OPENING_RANGE",
        "INCOMPLETE_OPENING_RANGE",
    )
    assert [item.value for item in (SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.AMBIGUOUS, SMCV2PrimitiveStatus.UNKNOWN, SMCV2PrimitiveStatus.VALID, SMCV2PrimitiveStatus.NONE)] == ["INVALID", "AMBIGUOUS", "UNKNOWN", "VALID", "NONE"]


def test_case_40_all_identity_kinds_have_exhaustive_required_and_forbidden_schemas() -> None:
    allowed = {
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION: {"segment_ordinal", "segment_id", "contract", "trade_date", "index", "bar_open_timestamp", "bar_close_timestamp", "open_tick", "high_tick", "low_tick", "close_tick", "volume", "is_closed", "kill_zone_context_id", "kill_zone_snapshot_id"},
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OPENING_RANGE: {"segment_ordinal", "segment_id", "contract", "trade_date", "source_observation_ids", "source_context_ids", "source_snapshot_ids", "first_known_index", "first_known_timestamp", "high_tick", "low_tick", "midpoint_tick", "width_ticks"},
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.CANDIDATE: {"range_id", "segment_ordinal", "segment_id", "contract", "trade_date", "direction", "formation_observation_id", "formation_context_id", "formation_snapshot_id", "formation_index", "first_known_timestamp", "swept_boundary_tick", "sweep_extreme_tick", "reclaim_close_tick", "midpoint_tick", "invalidation_tick", "width_ticks"},
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OUTCOME: {"candidate_id", "outcome", "first_known_index", "first_known_timestamp", "horizon_observation_ids", "event_observation_id"},
        sweep_reclaim.GCNYAMSweepReclaimIdentityKind.MANIFEST: {"version", "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids", "count_funnel", "reason_counts"},
    }
    for kind, fields_for_kind in allowed.items():
        _assert_required_and_forbidden_schema(kind, fields_for_kind)
        identity = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**_identity_payloads()[kind])
        assert re.fullmatch(fr"{kind.value}:[0-9a-f]{{64}}", identity)


def test_case_41_ordered_history_moments_reason_tokens_and_malformed_hashes() -> None:
    fixture = _fixture(target_event=False)
    result = _run(fixture)
    outcome = result.outcomes[0]
    payload = {
        "identity_kind": sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OUTCOME,
        **_identity_common(fixture),
        "candidate_id": outcome.candidate_id,
        "outcome": outcome.outcome,
        "first_known_index": outcome.first_known_index,
        "first_known_timestamp": outcome.first_known_timestamp,
        "horizon_observation_ids": outcome.horizon_observation_ids,
        "event_observation_id": outcome.event_observation_id,
    }
    original_id = sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**payload)
    reversed_history = tuple(reversed(payload["horizon_observation_ids"]))  # type: ignore[arg-type]
    assert sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
        **dict(payload, horizon_observation_ids=reversed_history)
    ) != original_id
    with pytest.raises((TypeError, ValueError)):
        sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(
            **dict(payload, horizon_observation_ids=(payload["horizon_observation_ids"][0],) * 2)  # type: ignore[index]
        )
    with pytest.raises((TypeError, ValueError)):
        sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**dict(payload, candidate_id="bad"))
    none_result = _run(_fixture(direction="none"))
    assert none_result.reasons == tuple(token for token in REASON_TOKENS if token in none_result.reasons)
    assert tuple(key for key, _ in none_result.manifest.count_funnel) == COUNT_FUNNEL_KEYS  # type: ignore[union-attr]


def test_case_42_exact_public_apis_defaults_frozen_types_enums_version_and_exports() -> None:
    builder = inspect.signature(sweep_reclaim.make_gc_ny_am_sweep_reclaim_id)
    analyzer = inspect.signature(sweep_reclaim.analyze_gc_ny_am_opening_range_sweep_reclaim_reversion)
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in builder.parameters.values())
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in analyzer.parameters.values())
    assert tuple(analyzer.parameters) == ("instrument", "timeframe", "dataset_config", "dataset_result", "requested_trade_dates", "split_session_calendar", "kill_zone_calendar", "observations", "kill_zone_contexts", "kill_zone_snapshots", "kill_zone_result")
    assert tuple(builder.parameters) == ("identity_kind", "instrument", "timeframe", "dataset_id", "calendar_version", "split_session_calendar_digest", "kill_zone_calendar_digest", "timezone_name", "timezone_data_version", "segment_ordinal", "segment_id", "contract", "trade_date", "index", "bar_open_timestamp", "bar_close_timestamp", "open_tick", "high_tick", "low_tick", "close_tick", "volume", "is_closed", "kill_zone_context_id", "kill_zone_snapshot_id", "source_observation_ids", "source_context_ids", "source_snapshot_ids", "first_known_index", "first_known_timestamp", "midpoint_tick", "width_ticks", "range_id", "direction", "formation_observation_id", "formation_context_id", "formation_snapshot_id", "formation_index", "swept_boundary_tick", "sweep_extreme_tick", "reclaim_close_tick", "invalidation_tick", "candidate_id", "outcome", "horizon_observation_ids", "event_observation_id", "version", "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids", "count_funnel", "reason_counts")
    assert all(builder.parameters[name].default is inspect.Parameter.empty for name in tuple(builder.parameters)[:9])
    assert all(builder.parameters[name].default is None for name in tuple(builder.parameters)[9:])
    assert all(item.default is inspect.Parameter.empty for item in analyzer.parameters.values())
    assert sweep_reclaim.__all__ == EXPECTED_EXPORTS
    assert sweep_reclaim.GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION == (
        "GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V2"
    )
    assert tuple(item.value for item in sweep_reclaim.GCNYAMSweepReclaimIdentityKind) == (
        "OBSERVATION", "OPENING_RANGE", "CANDIDATE", "OUTCOME", "MANIFEST",
    )
    assert tuple(item.value for item in sweep_reclaim.GCNYAMSweepReclaimOutcomeType) == (
        "MIDPOINT_REACHED", "INVALIDATED", "TIMEOUT", "SAME_BAR_AMBIGUOUS",
        "INCOMPLETE", "INVALID",
    )
    expected_public_dataclasses = {
        sweep_reclaim.GCNYAMSweepReclaimObservation: {
            "observation_id": str,
            "segment_ordinal": int,
            "segment_id": str,
            "contract": str,
            "trade_date": date,
            "index": int,
            "bar_open_timestamp": datetime,
            "bar_close_timestamp": datetime,
            "open_tick": int,
            "high_tick": int,
            "low_tick": int,
            "close_tick": int,
            "volume": int,
            "is_closed": bool,
            "kill_zone_context_id": str,
            "kill_zone_snapshot_id": str,
        },
        sweep_reclaim.GCNYAMSweepReclaimOpeningRange: {
            "range_id": str,
            "segment_ordinal": int,
            "segment_id": str,
            "contract": str,
            "trade_date": date,
            "source_observation_ids": tuple[str, ...],
            "source_context_ids": tuple[str, ...],
            "source_snapshot_ids": tuple[str, ...],
            "first_known_index": int,
            "first_known_timestamp": datetime,
            "high_tick": int,
            "low_tick": int,
            "midpoint_tick": Decimal,
            "width_ticks": int,
        },
        sweep_reclaim.GCNYAMSweepReclaimCandidate: {
            "candidate_id": str,
            "range_id": str,
            "segment_ordinal": int,
            "segment_id": str,
            "contract": str,
            "trade_date": date,
            "direction": SMCV2Direction,
            "formation_observation_id": str,
            "formation_context_id": str,
            "formation_snapshot_id": str,
            "formation_index": int,
            "first_known_timestamp": datetime,
            "swept_boundary_tick": int,
            "sweep_extreme_tick": int,
            "reclaim_close_tick": int,
            "midpoint_tick": Decimal,
            "invalidation_tick": int,
            "width_ticks": int,
        },
        sweep_reclaim.GCNYAMSweepReclaimOutcome: {
            "outcome_id": str,
            "candidate_id": str,
            "outcome": sweep_reclaim.GCNYAMSweepReclaimOutcomeType,
            "first_known_index": int,
            "first_known_timestamp": datetime,
            "horizon_observation_ids": tuple[str, ...],
            "event_observation_id": str | None,
        },
        sweep_reclaim.GCNYAMSweepReclaimManifest: {
            "manifest_id": str,
            "version": str,
            "instrument": str,
            "timeframe": str,
            "dataset_id": str,
            "calendar_version": str,
            "split_session_calendar_digest": str,
            "kill_zone_calendar_digest": str,
            "timezone_name": str,
            "timezone_data_version": str,
            "requested_trade_dates": tuple[date, ...],
            "opening_range_ids": tuple[str, ...],
            "candidate_ids": tuple[str, ...],
            "outcome_ids": tuple[str, ...],
            "count_funnel": tuple[tuple[str, int], ...],
            "reason_counts": tuple[tuple[str, int], ...],
        },
        sweep_reclaim.GCNYAMSweepReclaimResult: {
            "status": SMCV2PrimitiveStatus,
            "opening_ranges": tuple[sweep_reclaim.GCNYAMSweepReclaimOpeningRange, ...],
            "candidates": tuple[sweep_reclaim.GCNYAMSweepReclaimCandidate, ...],
            "outcomes": tuple[sweep_reclaim.GCNYAMSweepReclaimOutcome, ...],
            "manifest": sweep_reclaim.GCNYAMSweepReclaimManifest | None,
            "reasons": tuple[str, ...],
            "blocking_reasons": tuple[str, ...],
        },
    }
    for data_type, expected_hints in expected_public_dataclasses.items():
        assert data_type.__dataclass_params__.frozen is True
        assert tuple(item.name for item in fields(data_type)) == tuple(expected_hints)
        assert get_type_hints(data_type) == expected_hints
        if data_type is not sweep_reclaim.GCNYAMSweepReclaimResult:
            assert all(item.default is MISSING for item in fields(data_type))
    defaults = {item.name: item.default for item in fields(sweep_reclaim.GCNYAMSweepReclaimResult)}
    assert defaults == {"status": MISSING, "opening_ranges": (), "candidates": (), "outcomes": (), "manifest": None, "reasons": (), "blocking_reasons": ()}


def test_case_43_repeatability_identity_counts_manifest_order_and_bytes() -> None:
    fixture = _fixture()
    first = _run(fixture)
    second = _run(fixture)
    assert first == second
    assert pickle.dumps(first, protocol=5) == pickle.dumps(second, protocol=5)
    assert first.manifest is not None
    assert first.manifest.opening_range_ids == tuple(item.range_id for item in first.opening_ranges)
    assert first.manifest.candidate_ids == tuple(item.candidate_id for item in first.candidates)
    assert first.manifest.outcome_ids == tuple(item.outcome_id for item in first.outcomes)
    shifted = fixture["observations"][0]  # type: ignore[index]
    payload = _identity_payloads()[sweep_reclaim.GCNYAMSweepReclaimIdentityKind.OBSERVATION]
    payload["bar_open_timestamp"] = shifted.bar_open_timestamp.astimezone(timezone(timedelta(hours=9)))
    payload["bar_close_timestamp"] = shifted.bar_close_timestamp.astimezone(timezone(timedelta(hours=9)))
    assert sweep_reclaim.make_gc_ny_am_sweep_reclaim_id(**payload) == shifted.observation_id
    attested = _run(_attested_opening_range_gap_fixture())
    assert attested.manifest is not None
    assert tuple(key for key, _ in attested.manifest.count_funnel) == COUNT_FUNNEL_KEYS
    assert dict(attested.manifest.count_funnel)["ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES"] == 1
    assert dict(attested.manifest.reason_counts)["ATTESTED_NO_TRADE_OPENING_RANGE"] == 1
    assert pickle.dumps(attested, protocol=5) == pickle.dumps(
        _run(_attested_opening_range_gap_fixture()), protocol=5,
    )


def test_case_44_strictly_later_complete_append_is_prefix_invariant() -> None:
    prefix = _run(_fixture(count=22))
    extended = _run(_fixture(count=23))
    assert extended.opening_ranges[:len(prefix.opening_ranges)] == prefix.opening_ranges
    assert extended.candidates[:len(prefix.candidates)] == prefix.candidates
    assert extended.outcomes[:len(prefix.outcomes)] == prefix.outcomes
    attested = _attested_opening_range_gap_fixture()
    attested_result = _run(attested)
    assert _run(attested) == attested_result


def test_case_45_retained_dependency_prefix_is_unknown_and_preserves_only_complete_prior_evidence() -> None:
    fixture = _fixture(count=36, full_session_edges=True)
    complete = _run(fixture)
    observations = fixture["observations"]  # type: ignore[assignment]
    contexts = fixture["kill_zone_contexts"]  # type: ignore[assignment]
    snapshots = fixture["kill_zone_snapshots"]  # type: ignore[assignment]
    retained_count = 30
    prefix = _run(
        fixture,
        observations=observations[:retained_count],
        kill_zone_contexts=contexts[:retained_count],
        kill_zone_snapshots=snapshots[:retained_count],
        kill_zone_result=KillZoneResult(
            SMCV2PrimitiveStatus.VALID,
            contexts[:retained_count],
            snapshots[:retained_count],
        ),
    )
    assert complete.status is SMCV2PrimitiveStatus.VALID
    assert prefix.status is SMCV2PrimitiveStatus.UNKNOWN
    assert "MISSING_TOP_LEVEL_CONTEXT" in prefix.reasons
    assert prefix.manifest is None
    assert prefix.opening_ranges == complete.opening_ranges
    assert prefix.candidates == complete.candidates
    assert prefix.outcomes == complete.outcomes

    root = Path(__file__).resolve().parents[1]
    correction = (root / "docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md").read_text(encoding="utf-8")
    assert "133" in correction and "113" in correction
    assert "missing suffix segments" in correction.lower()


def test_case_46_complete_dependency_preserves_native_valid_and_none_statuses() -> None:
    valid_fixture = _fixture(count=36, full_session_edges=True)
    none_fixture = _fixture(direction="none", count=36, full_session_edges=True)
    valid_result = _run(valid_fixture)
    none_result = _run(none_fixture)
    assert valid_result.status is SMCV2PrimitiveStatus.VALID
    assert none_result.status is SMCV2PrimitiveStatus.NONE
    assert len(valid_fixture["observations"]) == len(valid_fixture["kill_zone_contexts"]) == len(valid_fixture["kill_zone_snapshots"]) == 35  # type: ignore[arg-type]
    assert len(none_fixture["observations"]) == len(none_fixture["kill_zone_contexts"]) == len(none_fixture["kill_zone_snapshots"]) == 35  # type: ignore[arg-type]
    assert valid_result.candidates and valid_result.outcomes
    assert not none_result.candidates and not none_result.outcomes


def test_case_47_exact_three_path_scope_and_private_root_immutability_are_locked() -> None:
    root = Path(__file__).resolve().parents[1]
    reserved = {
        "analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py",
        "tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py",
        "docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md",
    }
    correction = (root / "docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md").read_text(encoding="utf-8")
    for path in reserved:
        assert path in correction
    assert "Candidate Evidence artifact remains immutable" in " ".join(correction.split())
    source = (root / "analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py").read_text(encoding="utf-8")
    for forbidden in ("pathlib", "private_data", "open(", "read_text", "write_text"):
        assert forbidden not in source
    attested = _attested_opening_range_gap_fixture()
    assert attested["dataset_result"].manifest.attested_no_trade_interval_count == 2  # type: ignore[union-attr]
    assert _run(attested).reasons == ("ATTESTED_NO_TRADE_OPENING_RANGE",)


def test_case_48_private_run_training_oos_integration_push_and_trading_remain_unused() -> None:
    fixture = _fixture()
    observations = fixture["observations"]  # type: ignore[assignment]
    assert _run(fixture, observations=(observations[1], observations[0]) + observations[2:]).status is SMCV2PrimitiveStatus.INVALID
    repaired = replace(observations[1], observation_id="OBSERVATION:" + _h("repair"), close_tick=101)
    assert _run(fixture, observations=observations[:2] + (repaired,) + observations[2:]).status is SMCV2PrimitiveStatus.INVALID
    changed_calendar = replace(fixture["kill_zone_calendar"][0], calendar_version="OTHER")  # type: ignore[index]
    assert _run(fixture, kill_zone_calendar=(changed_calendar,)).status is SMCV2PrimitiveStatus.INVALID
    changed_dataset = replace(fixture["dataset_result"], dataset_id=_h("other"))  # type: ignore[arg-type]
    assert _run(fixture, dataset_result=changed_dataset).status is SMCV2PrimitiveStatus.INVALID
    root = Path(__file__).resolve().parents[1]
    correction = (root / "docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md").read_text(encoding="utf-8")
    source = (root / "analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py").read_text(encoding="utf-8")
    for forbidden in ("import main", "storage.decision_trace", "DECISION_CANDIDATE", "place_order", "execute_trade", "PRIVATE_RUN", "TRAINING"):
        assert forbidden not in source
    for forbidden in ("private execution", "training", "OOS", "integration", "push", "trading"):
        assert forbidden.lower() in correction.lower()
