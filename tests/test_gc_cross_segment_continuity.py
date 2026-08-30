"""Exact 56-case acceptance matrix for GC continuity feasibility."""

from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path

import pytest

import analysis.gc_cross_segment_continuity as continuity
from analysis.gc_candidate_evidence_builder import (
    GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION,
    GCCandidateEvidenceConfig,
    GCCandidateEvidenceResult,
    GCCandidateEvidenceSegmentResult,
    GCCandidateFrontierEvidence,
    GCCandidateFrontierEvidenceResult,
    GCCandidateFrontierIdentityKind,
    GCCandidateFrontierSegmentEvidence,
    make_gc_candidate_frontier_evidence_id,
)
from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCDatasetSessionInterval,
    GCSegmentPartition,
    GCSplitSessionCalendarEntry,
    _digest_bars,
    make_gc_dataset_id,
)
from analysis.gc_structural_seed_evidence import GCCanonicalSeedEvidence
from core.gc_chronological_backtest import GCChronologicalBar
from smc.dealing_range import (
    DealingRangeKind,
    DealingRangeEventType,
    DealingRangeResult,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
    DealingRangeTransition,
)
from smc.equal_liquidity import EqualLiquidityResult
from smc.fair_value_gap import FairValueGap, FairValueGapResult
from smc.inducement import InducementPendingHorizonResult, InducementResult
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneResult,
    KillZoneSessionStatus,
)
from smc.liquidity_map import LiquidityMapResult, LiquidityMapSnapshot
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
)


UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[1]
TZDATA_VERSION = importlib.metadata.version("tzdata")
LEGACY_V3_SEGMENT_IDENTITY_VERSION = "GC-DATASET-BUILDER-V3-SPLIT-SESSION"


def _h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _dt(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    output = format(value, "f")
    if "." in output:
        output = output.rstrip("0").rstrip(".")
    return output if "." in output else output + ".0"


def _legacy_v3_segment_id(
    *,
    config: GCDatasetBuildConfig,
    contract: str,
    partition: GCSegmentPartition,
    first_trade_date: date,
    last_trade_date: date,
    source_ids: tuple[str, ...],
    bars: tuple[GCChronologicalBar, ...],
    preceding_missing_bar_count: int,
) -> str:
    payload = {
        "version": LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        "identity_kind": "SEGMENT",
        "config": {
            "instrument": config.instrument,
            "timeframe": config.timeframe,
            "source_timezone": config.source_timezone,
            "exchange_timezone": config.exchange_timezone,
            "timezone_data_version": config.timezone_data_version,
            "tick_size": _decimal_text(config.tick_size),
            "initial_contract": config.initial_contract,
            "initial_trade_date": config.initial_trade_date.isoformat(),
            "roll_confirmation_sessions": config.roll_confirmation_sessions,
            "oos_start_trade_date": config.oos_start_trade_date.isoformat(),
            "oos_end_trade_date": config.oos_end_trade_date.isoformat(),
        },
        "contract": contract,
        "partition": partition.value,
        "first_trade_date": first_trade_date.isoformat(),
        "last_trade_date": last_trade_date.isoformat(),
        "source_ids": source_ids,
        "bar_digest": _digest_bars(bars),
        "preceding_missing_bar_count": preceding_missing_bar_count,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _config() -> GCDatasetBuildConfig:
    return GCDatasetBuildConfig(
        "GC",
        "5M",
        "Asia/Tokyo",
        "America/New_York",
        TZDATA_VERSION,
        Decimal("0.1"),
        "GCG26-COMEX",
        date(2026, 1, 5),
        3,
        date(2027, 1, 1),
        date(2027, 6, 30),
    )


def _bars(opening: datetime, closing: datetime, base: int) -> tuple[GCChronologicalBar, ...]:
    return (
        GCChronologicalBar(0, opening + timedelta(minutes=5), base, base + 2, base - 2, base + 1, 10, True),
        GCChronologicalBar(1, opening + timedelta(minutes=10), base + 1, base + 3, base, base + 2, 12, True),
        GCChronologicalBar(2, closing, base + 2, base + 4, base + 1, base + 3, 14, True),
    )


def _segment(
    ordinal: int,
    trade_date: date,
    opening: datetime,
    closing: datetime,
    *,
    contract: str = "GCG26-COMEX",
    partition: GCSegmentPartition = GCSegmentPartition.DEVELOPMENT,
    missing: int = 0,
    bars: tuple[GCChronologicalBar, ...] | None = None,
    identity_version: str = GC_DATASET_BUILDER_VERSION,
) -> GCCanonicalContractSegment:
    selected = bars or _bars(opening, closing, 1000 + ordinal * 10)
    source_ids = (_h(f"source-{ordinal}"),)
    if identity_version == LEGACY_V3_SEGMENT_IDENTITY_VERSION:
        segment_id = _legacy_v3_segment_id(
            config=_config(),
            contract=contract,
            partition=partition,
            first_trade_date=trade_date,
            last_trade_date=trade_date,
            source_ids=source_ids,
            bars=selected,
            preceding_missing_bar_count=missing,
        )
    elif identity_version == GC_DATASET_BUILDER_VERSION:
        segment_id = make_gc_dataset_id(
            identity_kind="SEGMENT",
            config=_config(),
            contract=contract,
            partition=partition,
            first_trade_date=trade_date,
            last_trade_date=trade_date,
            source_ids=source_ids,
            bar_digest=_digest_bars(selected),
            preceding_missing_bar_count=missing,
        )
    else:
        raise ValueError("test helper requires an exact supported identity version")
    return GCCanonicalContractSegment(
        segment_id, contract, partition, trade_date, trade_date, source_ids, selected, missing
    )


def _detector_result(ordinal: int, segment_id: str, *, fvg: FairValueGapResult | None = None) -> GCCandidateEvidenceSegmentResult:
    return GCCandidateEvidenceSegmentResult(
        ordinal,
        segment_id,
        EqualLiquidityResult(SMCV2PrimitiveStatus.NONE),
        DealingRangeResult(SMCV2PrimitiveStatus.NONE),
        LiquidityMapResult(SMCV2PrimitiveStatus.NONE),
        fvg or FairValueGapResult(SMCV2PrimitiveStatus.NONE),
        InducementResult(SMCV2PrimitiveStatus.NONE),
        KillZoneResult(SMCV2PrimitiveStatus.NONE),
        tuple(_h(f"result-{ordinal}-{number}") for number in range(6)),
    )


def _fixture(*, receiving_group: bool = False) -> dict[str, object]:
    source_date = date(2026, 1, 5)
    receiving_date = date(2026, 1, 6)
    source_open, source_close = _dt(2026, 1, 4, 18), _dt(2026, 1, 5, 17)
    receiving_open, receiving_close = _dt(2026, 1, 5, 18), _dt(2026, 1, 6, 17)
    source = _segment(0, source_date, source_open, source_close)
    receiving = _segment(1, receiving_date, receiving_open, receiving_close)
    event: DealingRangeStructureEvent | None = None
    gap: FairValueGap | None = None
    fvg_result = FairValueGapResult(SMCV2PrimitiveStatus.NONE)
    if receiving_group:
        event = DealingRangeStructureEvent(
            SMCV2Direction.BULLISH,
            DealingRangeEventType.BOS,
            _h("broken-swing"),
            SMCV2EventProvenance(
                (1, 2),
                (receiving.bars[1].timestamp, receiving.bars[2].timestamp),
                2,
                receiving.bars[2].timestamp,
            ),
            _h("event"),
        )
        gap = FairValueGap(
            _h("gap"),
            SMCV2Direction.BULLISH,
            (0, 1, 2),
            tuple(item.timestamp for item in receiving.bars),
            1005,
            1007,
            Decimal("1006.0"),
            2,
            receiving.bars[2].timestamp,
            _h("displacement"),
            event.event_id,
            event.event_type,
        )
        fvg_result = FairValueGapResult(SMCV2PrimitiveStatus.VALID, gaps=(gap,))
    segment_results = (
        _detector_result(0, source.segment_id),
        _detector_result(1, receiving.segment_id, fvg=fvg_result),
    )
    control = GCCandidateEvidenceResult(SMCV2PrimitiveStatus.NONE, segment_results=segment_results)
    dataset_id = _h("dataset")
    manifest = GCDatasetManifest(
        dataset_id,
        GC_DATASET_BUILDER_VERSION,
        source.source_ids + receiving.source_ids,
        (_h("coverage"),),
        _h("coverage-digest"),
        (source.segment_id, receiving.segment_id),
        "gc-calendar-v1",
        _config().timezone_data_version,
        source.bars[0].timestamp,
        receiving.bars[-1].timestamp,
        source.bars[0].timestamp,
        receiving.bars[-1].timestamp,
        6,
        6,
        6,
        0,
        0,
        0,
        0,
        72,
        72,
        0,
        ((source.contract, source_date, 36), (receiving.contract, receiving_date, 36)),
        (),
        (),
    )
    dataset = GCDatasetBuildResult(
        GCDatasetBuildStatus.VALID,
        dataset_id,
        (source, receiving),
        manifest,
    )
    boundary_calendar = (
        GCSplitSessionCalendarEntry(
            "gc-calendar-v1",
            source_date,
            (GCDatasetSessionInterval(source_open, source_close),),
            (_h("calendar-source"),),
            (_h("calendar-source-sha"),),
        ),
        GCSplitSessionCalendarEntry(
            "gc-calendar-v1",
            receiving_date,
            (GCDatasetSessionInterval(receiving_open, receiving_close),),
            (_h("calendar-receiver"),),
            (_h("calendar-receiver-sha"),),
        ),
    )
    candidate_calendar = (
        KillZoneCalendarEntry("gc-calendar-v1", source_date, KillZoneSessionStatus.OPEN, source_open, source_close),
        KillZoneCalendarEntry("gc-calendar-v1", receiving_date, KillZoneSessionStatus.OPEN, receiving_open, receiving_close),
    )
    seed = GCCanonicalSeedEvidence(
        _h("seed"),
        "GC-STRUCTURAL-SEED-V1",
        "GC",
        "5M",
        dataset_id,
        _h("seed-bars"),
        (),
        (),
        (event,) if event is not None else (),
        (),
    )
    return {
        "dataset_config": _config(),
        "dataset": dataset,
        "boundary_calendar_entries": boundary_calendar,
        "candidate_calendar_entries": candidate_calendar,
        "structural_seed": seed,
        "canonical_candidate_evidence": control,
        "frontier_evidence": None,
        "candidate_config": GCCandidateEvidenceConfig(),
        "source": source,
        "receiving": receiving,
        "event": event,
        "gap": gap,
    }


def _frontier_fixture() -> dict[str, object]:
    fixture = _fixture()
    dataset = fixture["dataset"]
    control = fixture["canonical_candidate_evidence"]
    seed = fixture["structural_seed"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    assert isinstance(control, GCCandidateEvidenceResult)
    assert isinstance(seed, GCCanonicalSeedEvidence)
    source = dataset.segments[1]
    receiving_date = date(2026, 1, 7)
    receiving_open = _dt(2026, 1, 6, 18)
    receiving_close = _dt(2026, 1, 7, 17)
    receiving = _segment(2, receiving_date, receiving_open, receiving_close)
    dataset = replace(
        dataset,
        segments=dataset.segments + (receiving,),
        manifest=replace(
            dataset.manifest,
            source_ids=dataset.manifest.source_ids + receiving.source_ids,
            segment_ids=dataset.manifest.segment_ids + (receiving.segment_id,),
            raw_end_timestamp=receiving.bars[-1].timestamp,
            usable_end_timestamp=receiving.bars[-1].timestamp,
            parsed_row_count=9,
            eligible_row_count=9,
            development_bar_count=9,
            raw_volume=108,
            eligible_volume=108,
            completed_session_volumes=dataset.manifest.completed_session_volumes
            + ((receiving.contract, receiving_date, 36),),
        ),
    )
    control = GCCandidateEvidenceResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        segment_results=(control.segment_results[0],),
        reasons=("one or more confirmation horizons are incomplete",),
        blocking_reasons=("next three closed bars are incomplete",),
    )
    source_full = _detector_result(1, source.segment_id)
    receiving_full = _detector_result(2, receiving.segment_id)
    source_evidence = GCCandidateFrontierSegmentEvidence(
        source_full.segment_ordinal,
        source_full.segment_id,
        source_full.equal_liquidity_result,
        source_full.dealing_range_result,
        source_full.liquidity_map_result,
        source_full.fair_value_gap_result,
        source_full.result_ids[:4],
    )
    receiving_evidence = GCCandidateFrontierSegmentEvidence(
        receiving_full.segment_ordinal,
        receiving_full.segment_id,
        receiving_full.equal_liquidity_result,
        receiving_full.dealing_range_result,
        receiving_full.liquidity_map_result,
        receiving_full.fair_value_gap_result,
        receiving_full.result_ids[:4],
    )
    pending = InducementPendingHorizonResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        reasons=("one or more confirmation horizons are incomplete",),
        blocking_reasons=("NEXT_THREE_CLOSED_BARS_INCOMPLETE",),
    )
    control_digest = continuity._sha(control)
    frontier_id = make_gc_candidate_frontier_evidence_id(
        identity_kind=GCCandidateFrontierIdentityKind.FRONTIER,
        instrument="GC",
        timeframe="5M",
        dataset_id=dataset.dataset_id or "",
        seed_id=seed.seed_id,
        canonical_control_digest=control_digest,
        frontier_ordinal=1,
        source_segment=source_evidence,
        source_pending_result=pending,
        receiving_segment=receiving_evidence,
    )
    frontier = GCCandidateFrontierEvidenceResult(
        SMCV2PrimitiveStatus.VALID,
        GCCandidateFrontierEvidence(
            frontier_id,
            GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION,
            "GC",
            "5M",
            dataset.dataset_id or "",
            seed.seed_id,
            control_digest,
            1,
            source_evidence,
            pending,
            receiving_evidence,
        ),
        ("CONTROL_FRONTIER_CONTINUATION_EVIDENCE_COMPLETE",),
    )
    boundary_calendar = fixture["boundary_calendar_entries"]
    candidate_calendar = fixture["candidate_calendar_entries"]
    assert isinstance(boundary_calendar, tuple) and isinstance(candidate_calendar, tuple)
    updated = dict(fixture)
    updated.update(
        dataset=dataset,
        boundary_calendar_entries=boundary_calendar
        + (
            GCSplitSessionCalendarEntry(
                "gc-calendar-v1",
                receiving_date,
                (GCDatasetSessionInterval(receiving_open, receiving_close),),
                (_h("calendar-frontier-receiver"),),
                (_h("calendar-frontier-receiver-sha"),),
            ),
        ),
        candidate_calendar_entries=candidate_calendar
        + (
            KillZoneCalendarEntry(
                "gc-calendar-v1",
                receiving_date,
                KillZoneSessionStatus.OPEN,
                receiving_open,
                receiving_close,
            ),
        ),
        canonical_candidate_evidence=control,
        frontier_evidence=frontier,
        source=source,
        receiving=receiving,
    )
    return updated


def _with_segment_identity_versions(
    fixture: dict[str, object],
    *,
    manifest_version: str,
    segment_versions: tuple[str, ...],
) -> dict[str, object]:
    dataset = fixture["dataset"]
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    assert isinstance(control, GCCandidateEvidenceResult)
    assert len(segment_versions) == len(dataset.segments) == len(control.segment_results)
    rebuilt = tuple(
        replace(
            segment,
            segment_id=(
                _legacy_v3_segment_id(
                    config=_config(),
                    contract=segment.contract,
                    partition=segment.partition,
                    first_trade_date=segment.first_trade_date,
                    last_trade_date=segment.last_trade_date,
                    source_ids=segment.source_ids,
                    bars=segment.bars,
                    preceding_missing_bar_count=segment.preceding_missing_bar_count,
                )
                if version == LEGACY_V3_SEGMENT_IDENTITY_VERSION
                else make_gc_dataset_id(
                    identity_kind="SEGMENT",
                    config=_config(),
                    contract=segment.contract,
                    partition=segment.partition,
                    first_trade_date=segment.first_trade_date,
                    last_trade_date=segment.last_trade_date,
                    source_ids=segment.source_ids,
                    bar_digest=_digest_bars(segment.bars),
                    preceding_missing_bar_count=segment.preceding_missing_bar_count,
                )
            ),
        )
        for segment, version in zip(dataset.segments, segment_versions, strict=True)
    )
    rebuilt_ids = tuple(segment.segment_id for segment in rebuilt)
    updated = dict(fixture)
    updated["dataset"] = replace(
        dataset,
        segments=rebuilt,
        manifest=replace(
            dataset.manifest,
            version=manifest_version,
            segment_ids=rebuilt_ids,
        ),
    )
    updated["canonical_candidate_evidence"] = replace(
        control,
        segment_results=tuple(
            replace(result, segment_id=segment_id)
            for result, segment_id in zip(
                control.segment_results,
                rebuilt_ids,
                strict=True,
            )
        ),
    )
    updated["source"], updated["receiving"] = rebuilt
    return updated


def _run(monkeypatch: pytest.MonkeyPatch, fixture: dict[str, object], **changes: object) -> continuity.GCCrossSegmentContinuityResult:
    supplied = {key: fixture[key] for key in (
        "dataset_config", "dataset", "boundary_calendar_entries", "candidate_calendar_entries",
        "structural_seed", "canonical_candidate_evidence", "frontier_evidence", "candidate_config",
    )}
    supplied.update(changes)
    monkeypatch.setattr(continuity, "build_gc_candidate_evidence", lambda **_: supplied["canonical_candidate_evidence"])
    if supplied["frontier_evidence"] is not None:
        monkeypatch.setattr(
            continuity,
            "analyze_gc_candidate_frontier_evidence",
            lambda **_: supplied["frontier_evidence"],
        )
    return continuity.analyze_gc_cross_segment_continuity(**supplied)  # type: ignore[arg-type]


def _identity_common() -> dict[str, object]:
    return {
        "instrument": "gc",
        "timeframe": "5m",
        "dataset_id": _h("dataset"),
        "calendar_version": "gc-calendar-v1",
        "boundary_calendar_digest": _h("boundary-calendar"),
        "candidate_calendar_digest": _h("candidate-calendar"),
        "timezone_data_version": TZDATA_VERSION,
        "seed_id": _h("seed"),
        "canonical_control_digest": _h("control"),
    }


def _dependency() -> continuity.GCContinuityDependencyReference:
    return continuity.GCContinuityDependencyReference(
        "EQUAL_LIQUIDITY", "POOL", _h("pool"), 0, _h("source-segment"), 1, _dt(2026, 1, 5, 16),
        2, _dt(2026, 1, 5, 17), "ACTIVE", (_h("history"),), _h("moments"), _h("object"),
    )


def _receiving_reference(detector: str = "DEALING_RANGE") -> continuity.GCContinuityReceivingReference:
    return continuity.GCContinuityReceivingReference(
        detector,
        "STRUCTURE_EVENT" if detector == "DEALING_RANGE" else "GAP",
        _h(detector),
        1,
        _h("receiving-segment"),
        2,
        _dt(2026, 1, 6, 17),
        2,
        _dt(2026, 1, 6, 17),
        "BOS" if detector == "DEALING_RANGE" else "ACTIVE",
        () if detector == "DEALING_RANGE" else (_h("gap-history"),),
        _h(f"{detector}-moments"),
        _h(f"{detector}-object"),
    )


def _boundary_id(**changes: object) -> str:
    values: dict[str, object] = {
        "identity_kind": continuity.GCCrossSegmentContinuityIdentityKind.BOUNDARY,
        **_identity_common(),
        "source_segment_ordinal": 0,
        "source_segment_id": _h("source-segment"),
        "receiving_segment_ordinal": 1,
        "receiving_segment_id": _h("receiving-segment"),
        "contract": "GCG26-COMEX",
        "source_trade_date": date(2026, 1, 5),
        "receiving_trade_date": date(2026, 1, 6),
        "source_end_timestamp": _dt(2026, 1, 5, 17),
        "receiving_start_timestamp": _dt(2026, 1, 5, 18, 5),
        "decision": continuity.GCCrossSegmentContinuityDecision.ELIGIBLE,
        "reason_tokens": ("ELIGIBLE_STANDARD_BOUNDARY",),
        "dependency_references": (_dependency(),),
    }
    values.update(changes)
    return continuity.make_gc_cross_segment_continuity_id(**values)  # type: ignore[arg-type]


def test_case_01_exact_dataset_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture())
    assert result.status is SMCV2PrimitiveStatus.VALID and result.manifest is not None
    assert result.manifest.dataset_id == _h("dataset")


def test_case_02_missing_top_level_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    for name in ("dataset", "boundary_calendar_entries", "candidate_calendar_entries", "structural_seed", "canonical_candidate_evidence"):
        result = _run(monkeypatch, fixture, **{name: None})
        assert result.status is SMCV2PrimitiveStatus.UNKNOWN
        assert result.manifest is None
        assert result.reasons == ("MISSING_TOP_LEVEL_CONTEXT",)
        assert result.blocking_reasons == result.reasons


def test_case_03_invalid_supplied_counterpart_outranks_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    malformed = (replace(fixture["candidate_calendar_entries"][0], trade_date="bad"),)  # type: ignore[index,arg-type]
    result = _run(monkeypatch, fixture, dataset=None, candidate_calendar_entries=malformed)
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_04_dependency_identity_drift_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    drifted = replace(dataset, manifest=replace(dataset.manifest, timezone_data_version="drift"))
    assert _run(monkeypatch, fixture, dataset=drifted).status is SMCV2PrimitiveStatus.INVALID


def test_case_05_canonical_rebuild_is_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    result = _run(monkeypatch, fixture)
    assert result.manifest is not None and result.manifest.canonical_control_digest == continuity._sha(fixture["canonical_candidate_evidence"])


def test_case_06_control_drift_stops_promotion(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    monkeypatch.setattr(continuity, "build_gc_candidate_evidence", lambda **_: GCCandidateEvidenceResult(SMCV2PrimitiveStatus.UNKNOWN))
    supplied = {key: fixture[key] for key in (
        "dataset_config", "dataset", "boundary_calendar_entries", "candidate_calendar_entries",
        "structural_seed", "canonical_candidate_evidence", "candidate_config",
    )}
    result = continuity.analyze_gc_cross_segment_continuity(**supplied)  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID and not result.boundaries


def test_case_07_adjacent_segment_order_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture())
    assert [(item.source_segment_ordinal, item.receiving_segment_ordinal) for item in result.boundaries] == [(0, 1)]


def test_case_08_reordered_candidate_segments_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(control, GCCandidateEvidenceResult)
    assert _run(monkeypatch, fixture, canonical_candidate_evidence=replace(control, segment_results=control.segment_results[::-1])).status is SMCV2PrimitiveStatus.INVALID


def test_case_09_same_contract_development_boundary_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = _run(monkeypatch, _fixture()).boundaries[0]
    assert boundary.contract == "GCG26-COMEX" and boundary.decision is continuity.GCCrossSegmentContinuityDecision.ELIGIBLE


def test_case_10_contract_roll_is_ineligible(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None and isinstance(control, GCCandidateEvidenceResult)
    old = dataset.segments[1]
    changed = _segment(1, old.first_trade_date, old.bars[0].timestamp - timedelta(minutes=5), old.bars[-1].timestamp, contract="GCJ26-COMEX", bars=old.bars)
    changed_dataset = replace(dataset, segments=(dataset.segments[0], changed), manifest=replace(dataset.manifest, segment_ids=(dataset.segments[0].segment_id, changed.segment_id)))
    changed_control = replace(control, segment_results=(control.segment_results[0], replace(control.segment_results[1], segment_id=changed.segment_id)))
    result = _run(monkeypatch, fixture, dataset=changed_dataset, canonical_candidate_evidence=changed_control)
    assert result.status is SMCV2PrimitiveStatus.NONE and result.boundaries[0].reason_tokens == ("CONTRACT_BOUNDARY",)


def test_case_11_complete_standard_sessions_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run(monkeypatch, _fixture()).boundaries[0].reason_tokens == ("ELIGIBLE_STANDARD_BOUNDARY",)


def test_case_12_partial_boundary_is_ineligible_and_open_bar_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(dataset, GCDatasetBuildResult)
    assert dataset.manifest is not None
    assert isinstance(control, GCCandidateEvidenceResult)
    source = dataset.segments[0]

    partial = _segment(
        0,
        source.first_trade_date,
        source.bars[0].timestamp - timedelta(minutes=5),
        source.bars[-1].timestamp,
        missing=1,
        bars=source.bars,
    )
    partial_dataset = replace(
        dataset,
        segments=(partial, dataset.segments[1]),
        manifest=replace(
            dataset.manifest,
            segment_ids=(partial.segment_id, dataset.segments[1].segment_id),
        ),
    )
    partial_control = replace(
        control,
        segment_results=(
            replace(control.segment_results[0], segment_id=partial.segment_id),
            control.segment_results[1],
        ),
    )
    partial_result = _run(
        monkeypatch,
        fixture,
        dataset=partial_dataset,
        canonical_candidate_evidence=partial_control,
    )
    assert partial_result.status is SMCV2PrimitiveStatus.NONE
    assert len(partial_result.boundaries) == 1
    assert partial_result.boundaries[0].decision is continuity.GCCrossSegmentContinuityDecision.INELIGIBLE
    assert partial_result.boundaries[0].reason_tokens == ("PARTIAL_SEGMENT_BOUNDARY",)
    assert not partial_result.boundaries[0].dependency_references
    assert not partial_result.receiving_groups

    malformed = replace(source, bars=(replace(source.bars[0], is_closed=False),) + source.bars[1:])
    assert _run(monkeypatch, fixture, dataset=replace(dataset, segments=(malformed, dataset.segments[1]))).status is SMCV2PrimitiveStatus.INVALID


def test_case_13_exact_calendar_gap_reconciles(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture())
    assert result.boundaries[0].receiving_start_timestamp - result.boundaries[0].source_end_timestamp == timedelta(hours=1, minutes=5)


def test_case_14_calendar_contradiction_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    calendars = fixture["candidate_calendar_entries"]
    assert isinstance(calendars, tuple)
    changed = (replace(calendars[0], session_close_timestamp=calendars[0].session_close_timestamp - timedelta(minutes=5)), calendars[1])
    assert _run(monkeypatch, fixture, candidate_calendar_entries=changed).status is SMCV2PrimitiveStatus.INVALID


def test_case_15_closed_boundary_is_ineligible(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    calendars = fixture["candidate_calendar_entries"]
    assert isinstance(calendars, tuple)
    closed = replace(calendars[0], session_status=KillZoneSessionStatus.SESSION_CLOSED, session_open_timestamp=None, session_close_timestamp=None)
    result = _run(monkeypatch, fixture, candidate_calendar_entries=(closed, calendars[1]))
    assert result.status is SMCV2PrimitiveStatus.NONE and result.boundaries[0].reason_tokens == ("SESSION_CLOSED",)


def test_case_16_early_close_is_ineligible(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    calendars = fixture["candidate_calendar_entries"]
    assert isinstance(calendars, tuple)
    result = _run(monkeypatch, fixture, candidate_calendar_entries=(replace(calendars[0], session_status=KillZoneSessionStatus.EARLY_CLOSE), calendars[1]))
    assert result.boundaries[0].decision is continuity.GCCrossSegmentContinuityDecision.INELIGIBLE


def test_case_17_routine_maintenance_is_eligible(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run(monkeypatch, _fixture()).boundaries[0].decision is continuity.GCCrossSegmentContinuityDecision.ELIGIBLE


def test_case_18_equivalent_utc_timestamps_are_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    calendars = fixture["candidate_calendar_entries"]
    assert isinstance(calendars, tuple)
    offset = timezone(timedelta(hours=-5))
    equivalent = tuple(replace(item, session_open_timestamp=item.session_open_timestamp.astimezone(offset), session_close_timestamp=item.session_close_timestamp.astimezone(offset)) for item in calendars)
    assert _run(monkeypatch, fixture) == _run(monkeypatch, fixture, candidate_calendar_entries=equivalent)


def test_case_19_active_dependency_reference_schema() -> None:
    assert _boundary_id() == _boundary_id()


def test_case_20_terminal_pool_not_represented_as_active() -> None:
    bad = replace(_dependency(), state="SWEPT")
    assert _boundary_id(dependency_references=(bad,)) != _boundary_id()


def test_case_21_active_range_reference_is_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    item = replace(_dependency(), detector_name="DEALING_RANGE", object_kind="RANGE")
    assert len(_boundary_id(dependency_references=(item,))) == 64
    fixture = _fixture()
    control = _extension_range_control(fixture)
    result = _run(
        monkeypatch,
        fixture,
        canonical_candidate_evidence=control,
    )
    source = fixture["source"]
    assert isinstance(source, GCCanonicalContractSegment)
    assert result.status is SMCV2PrimitiveStatus.VALID
    range_reference = next(
        reference
        for reference in result.boundaries[0].dependency_references
        if reference.detector_name == "DEALING_RANGE"
    )
    assert range_reference.first_known_index == source.bars[2].index
    assert range_reference.first_known_timestamp == source.bars[2].timestamp
    assert range_reference.effective_index == source.bars[2].index
    assert range_reference.effective_timestamp == source.bars[2].timestamp
    assert range_reference.history_ids == (_h("range-construction-transition"),)


def _extension_range_control(
    fixture: dict[str, object],
) -> GCCandidateEvidenceResult:
    source = fixture["source"]
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(source, GCCanonicalContractSegment)
    assert isinstance(control, GCCandidateEvidenceResult)
    construction = DealingRangeTransition(
        _h("range-construction-transition"),
        _h("range-lineage"),
        None,
        DealingRangeState.ACTIVE,
        source.bars[1].index,
        source.bars[1].timestamp,
        "CONSTRUCTION_ACTIVE",
        _h("range-construction-event"),
        None,
    )
    first_known = SMCV2EventProvenance(
        (source.bars[0].index, source.bars[1].index),
        (source.bars[0].timestamp, source.bars[1].timestamp),
        source.bars[2].index,
        source.bars[2].timestamp,
    )
    snapshot = DealingRangeSnapshot(
        DealingRangeKind.EXTERNAL,
        SMCV2Direction.BULLISH,
        _h("extended-range-snapshot"),
        (_h("range-low-swing"), _h("range-high-swing")),
        (source.bars[0].index, source.bars[1].index),
        source.bars[0].low_tick,
        source.bars[1].high_tick,
        Decimal(source.bars[0].low_tick + source.bars[1].high_tick) / Decimal(2),
        first_known,
        _h("range-lineage"),
        _h("range-low-swing"),
        _h("range-construction-event"),
        DealingRangeState.ACTIVE,
        (construction,),
        (construction.transition_id,),
    )
    liquidity_snapshot = LiquidityMapSnapshot(
        _h("liquidity-map"),
        _h("liquidity-map-snapshot"),
        snapshot.lineage_id or "",
        snapshot.snapshot_id,
        source.bars[2].index,
        source.bars[2].timestamp,
        (),
        (),
        (),
        (),
    )
    source_result = replace(
        control.segment_results[0],
        dealing_range_result=DealingRangeResult(
            SMCV2PrimitiveStatus.VALID,
            ranges=(snapshot,),
        ),
        liquidity_map_result=LiquidityMapResult(
            SMCV2PrimitiveStatus.VALID,
            snapshots=(liquidity_snapshot,),
        ),
    )
    return replace(
        control,
        segment_results=(source_result, control.segment_results[1]),
    )


def test_case_22_terminal_range_state_is_identity_sensitive() -> None:
    item = replace(_dependency(), detector_name="DEALING_RANGE", object_kind="RANGE")
    assert _boundary_id(dependency_references=(item,)) != _boundary_id(dependency_references=(replace(item, state="SUPERSEDED"),))


def test_case_23_map_reference_history_is_sensitive() -> None:
    item = replace(_dependency(), detector_name="LIQUIDITY_MAP", object_kind="MAP")
    assert _boundary_id(dependency_references=(item,)) != _boundary_id(dependency_references=(replace(item, history_ids=()),))


def test_case_24_incomplete_dependency_order_is_invalid() -> None:
    first = _dependency()
    second = replace(first, detector_name="DEALING_RANGE", object_id=_h("range"))
    with pytest.raises(ValueError):
        _boundary_id(dependency_references=(second, first))


def test_case_25_source_moment_digest_is_sensitive() -> None:
    changed = replace(_dependency(), source_moment_digest=_h("changed"))
    assert _boundary_id(dependency_references=(changed,)) != _boundary_id()


def test_case_26_foreign_segment_reference_is_sensitive() -> None:
    changed = replace(_dependency(), owning_segment_id=_h("foreign"))
    assert _boundary_id(dependency_references=(changed,)) != _boundary_id()


def test_case_27_all_reference_fields_are_deterministic() -> None:
    item = _dependency()
    for name, value in (
        ("object_digest", _h("x")), ("effective_index", 3), ("state", "TOUCHED"),
    ):
        assert _boundary_id(dependency_references=(replace(item, **{name: value}),)) != _boundary_id()


def test_case_28_foreign_objects_remain_immutable(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    before = fixture["canonical_candidate_evidence"]
    _run(monkeypatch, fixture)
    assert fixture["canonical_candidate_evidence"] == before


def test_case_29_no_boundary_transition_lifecycle_exists() -> None:
    assert "transition" not in {field.name for field in fields(continuity.GCCrossSegmentBoundary)}


def test_case_30_receiving_event_reconciles_to_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture(receiving_group=True))
    assert len(result.receiving_groups) == 1 and result.receiving_groups[0].references[0].object_kind == "STRUCTURE_EVENT"


def test_case_31_receiving_fvg_is_reference_only(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    result = _run(monkeypatch, fixture)
    assert result.receiving_groups[0].references[1].object_id == fixture["gap"].gap_id  # type: ignore[union-attr]


def test_case_32_event_fvg_suffix_mismatch_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    seed = fixture["structural_seed"]
    event = fixture["event"]
    receiving = fixture["receiving"]
    assert isinstance(seed, GCCanonicalSeedEvidence) and isinstance(event, DealingRangeStructureEvent) and isinstance(receiving, GCCanonicalContractSegment)
    bad_provenance = replace(event.provenance, source_indices=(0, 2), source_timestamps=(receiving.bars[0].timestamp, receiving.bars[2].timestamp))
    result = _run(monkeypatch, fixture, structural_seed=replace(seed, structure_events=(replace(event, provenance=bad_provenance),)))
    assert result.status is SMCV2PrimitiveStatus.INVALID and not result.receiving_groups


def test_case_33_later_receiving_group_does_not_change_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    plain = _run(monkeypatch, _fixture())
    enriched = _run(monkeypatch, _fixture(receiving_group=True))
    assert plain.boundaries[0].decision == enriched.boundaries[0].decision


def test_case_34_partial_receiving_group_promotes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    prior = _run(monkeypatch, _fixture())
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(control, GCCandidateEvidenceResult)
    receiver = control.segment_results[1]
    duplicated = replace(receiver, fair_value_gap_result=replace(receiver.fair_value_gap_result, gaps=receiver.fair_value_gap_result.gaps * 2))
    result = _run(monkeypatch, fixture, canonical_candidate_evidence=replace(control, segment_results=(control.segment_results[0], duplicated)))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.boundaries == prior.boundaries
    assert not result.receiving_groups and result.manifest is None


def test_case_35_ordering_uses_dataset_and_upstream_order(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture(receiving_group=True))
    assert [item.detector_name for item in result.receiving_groups[0].references] == ["DEALING_RANGE", "FAIR_VALUE_GAP"]


def test_case_36_repeat_execution_is_object_equal(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    assert _run(monkeypatch, fixture) == _run(monkeypatch, fixture)


def test_case_37_status_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    complete = _run(monkeypatch, fixture)
    assert complete.status is SMCV2PrimitiveStatus.VALID
    assert complete.manifest is not None
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(control, GCCandidateEvidenceResult)
    unknown_control = replace(control, status=SMCV2PrimitiveStatus.UNKNOWN)
    unknown = _run(
        monkeypatch,
        fixture,
        canonical_candidate_evidence=unknown_control,
    )
    assert unknown.status is SMCV2PrimitiveStatus.UNKNOWN
    assert unknown.reasons == ("CANONICAL_CONTROL_UNKNOWN",)
    assert unknown.blocking_reasons == unknown.reasons
    assert unknown.boundaries == complete.boundaries
    assert unknown.receiving_groups == complete.receiving_groups
    manifest = unknown.manifest
    assert manifest is not None
    assert manifest.canonical_control_digest == continuity._sha(unknown_control)
    assert manifest.canonical_control_digest != complete.manifest.canonical_control_digest
    assert replace(
        manifest,
        manifest_id=complete.manifest.manifest_id,
        canonical_control_digest=complete.manifest.canonical_control_digest,
    ) == complete.manifest
    assert manifest.boundary_ids == tuple(item.boundary_id for item in unknown.boundaries)
    assert manifest.receiving_group_ids == tuple(item.group_id for item in unknown.receiving_groups)
    assert manifest.manifest_id == continuity.make_gc_cross_segment_continuity_id(
        identity_kind=continuity.GCCrossSegmentContinuityIdentityKind.MANIFEST,
        instrument=manifest.instrument,
        timeframe=manifest.timeframe,
        dataset_id=manifest.dataset_id,
        calendar_version=manifest.calendar_version,
        boundary_calendar_digest=manifest.boundary_calendar_digest,
        candidate_calendar_digest=manifest.candidate_calendar_digest,
        timezone_data_version=manifest.timezone_data_version,
        seed_id=manifest.seed_id,
        canonical_control_digest=manifest.canonical_control_digest,
        boundary_ids=manifest.boundary_ids,
        receiving_group_ids=manifest.receiving_group_ids,
    )


def test_case_38_later_invalid_preserves_prior_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(receiving_group=True)
    complete = _run(monkeypatch, fixture)
    assert complete.status is SMCV2PrimitiveStatus.VALID
    assert complete.boundaries and complete.receiving_groups
    control = fixture["canonical_candidate_evidence"]
    assert isinstance(control, GCCandidateEvidenceResult)
    for status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
    ):
        blocked = _run(
            monkeypatch,
            fixture,
            canonical_candidate_evidence=replace(control, status=status),
        )
        assert blocked.status is status
        assert blocked.boundaries == complete.boundaries
        assert blocked.receiving_groups == complete.receiving_groups
        assert blocked.manifest is None

    unknown_control = replace(control, status=SMCV2PrimitiveStatus.UNKNOWN)
    unknown = _run(monkeypatch, fixture, canonical_candidate_evidence=unknown_control)
    repeated = _run(
        monkeypatch,
        fixture,
        canonical_candidate_evidence=unknown_control,
    )
    assert unknown.status is SMCV2PrimitiveStatus.UNKNOWN
    assert unknown.boundaries == complete.boundaries
    assert unknown.receiving_groups == complete.receiving_groups
    assert unknown.manifest is not None
    assert unknown == repeated


def test_case_39_boundary_identity_schema_is_exhaustive() -> None:
    original = _boundary_id()
    assert original == _boundary_id(instrument="GC", timeframe="5M")
    for name, value in (
        ("instrument", "SI"),
        ("timeframe", "1M"),
        ("dataset_id", _h("other-dataset")),
        ("calendar_version", "other-calendar-v1"),
        ("boundary_calendar_digest", _h("other-boundary-calendar")),
        ("candidate_calendar_digest", _h("other-candidate-calendar")),
        ("timezone_data_version", f"{TZDATA_VERSION}-other"),
        ("seed_id", _h("other-seed")),
        ("canonical_control_digest", _h("other-source-prefix")),
        ("source_segment_ordinal", 2),
        ("source_segment_id", _h("other-source-segment")),
        ("receiving_segment_ordinal", 3),
        ("receiving_segment_id", _h("other-receiving-segment")),
        ("contract", "GCJ26-COMEX"),
        ("source_trade_date", date(2026, 1, 4)),
        ("receiving_trade_date", date(2026, 1, 7)),
        ("source_end_timestamp", _dt(2026, 1, 5, 16, 55)),
        ("receiving_start_timestamp", _dt(2026, 1, 5, 18, 10)),
        ("decision", continuity.GCCrossSegmentContinuityDecision.INELIGIBLE),
        ("reason_tokens", ("OTHER",)),
        ("dependency_references", (replace(_dependency(), object_id=_h("other-pool")),)),
    ):
        assert _boundary_id(**{name: value}) != original
    for name, value in (
        ("boundary_id", _h("forbidden")),
        ("effective_index", 2),
        ("effective_timestamp", _dt(2026, 1, 6, 17)),
        ("receiving_references", (_receiving_reference(),)),
        ("boundary_ids", (_h("boundary"),)),
        ("receiving_group_ids", (_h("group"),)),
    ):
        with pytest.raises((TypeError, ValueError)):
            _boundary_id(**{name: value})
    for name in _identity_common():
        values = {
            "identity_kind": continuity.GCCrossSegmentContinuityIdentityKind.BOUNDARY,
            **_identity_common(),
        }
        values.pop(name)
        with pytest.raises(TypeError):
            continuity.make_gc_cross_segment_continuity_id(**values)  # type: ignore[arg-type]


def test_case_40_receiving_group_identity_schema_is_exhaustive() -> None:
    common = _identity_common()
    refs = (_receiving_reference(), _receiving_reference("FAIR_VALUE_GAP"))
    values = dict(
        identity_kind=continuity.GCCrossSegmentContinuityIdentityKind.RECEIVING_GROUP,
        **common,
        boundary_id=_boundary_id(),
        receiving_segment_ordinal=1,
        receiving_segment_id=_h("receiving-segment"),
        effective_index=2,
        effective_timestamp=_dt(2026, 1, 6, 17),
        receiving_references=refs,
    )
    identity = continuity.make_gc_cross_segment_continuity_id(**values)
    assert len(identity) == 64
    for name, value in (
        ("instrument", "SI"),
        ("timeframe", "1M"),
        ("dataset_id", _h("other-dataset")),
        ("calendar_version", "other-calendar-v1"),
        ("boundary_calendar_digest", _h("other-boundary-calendar")),
        ("candidate_calendar_digest", _h("other-candidate-calendar")),
        ("timezone_data_version", f"{TZDATA_VERSION}-other"),
        ("seed_id", _h("other-seed")),
        ("canonical_control_digest", _h("other-receiving-prefix")),
        ("boundary_id", _h("other-boundary")),
    ):
        changed = dict(values)
        changed[name] = value
        assert continuity.make_gc_cross_segment_continuity_id(**changed) != identity
    for name, value, changed_refs in (
        ("receiving_segment_ordinal", 2, tuple(replace(item, owning_segment_ordinal=2) for item in refs)),
        ("receiving_segment_id", _h("other-receiving"), tuple(replace(item, owning_segment_id=_h("other-receiving")) for item in refs)),
        ("effective_index", 3, tuple(replace(item, effective_index=3) for item in refs)),
        ("effective_timestamp", _dt(2026, 1, 6, 17, 5), tuple(replace(item, effective_timestamp=_dt(2026, 1, 6, 17, 5)) for item in refs)),
    ):
        changed = dict(values)
        changed[name] = value
        changed["receiving_references"] = changed_refs
        assert continuity.make_gc_cross_segment_continuity_id(**changed) != identity
    assert continuity.make_gc_cross_segment_continuity_id(
        **{**values, "receiving_references": refs[::-1]}
    ) != identity
    for name, value in (
        ("source_segment_ordinal", 0),
        ("source_segment_id", _h("source")),
        ("contract", "GCG26-COMEX"),
        ("source_trade_date", date(2026, 1, 5)),
        ("receiving_trade_date", date(2026, 1, 6)),
        ("source_end_timestamp", _dt(2026, 1, 5, 17)),
        ("receiving_start_timestamp", _dt(2026, 1, 5, 18)),
        ("decision", continuity.GCCrossSegmentContinuityDecision.ELIGIBLE),
        ("reason_tokens", ("ELIGIBLE_STANDARD_BOUNDARY",)),
        ("dependency_references", (_dependency(),)),
        ("boundary_ids", (_h("boundary"),)),
        ("receiving_group_ids", (_h("group"),)),
    ):
        with pytest.raises((TypeError, ValueError)):
            continuity.make_gc_cross_segment_continuity_id(**values, **{name: value})
    for name, value in (
        ("boundary_id", None),
        ("receiving_segment_ordinal", None),
        ("receiving_segment_id", None),
        ("effective_index", None),
        ("effective_timestamp", None),
        ("receiving_references", ()),
    ):
        changed = dict(values)
        changed[name] = value
        with pytest.raises((TypeError, ValueError)):
            continuity.make_gc_cross_segment_continuity_id(**changed)


def test_case_41_manifest_identity_schema_is_exhaustive() -> None:
    values = dict(
        identity_kind=continuity.GCCrossSegmentContinuityIdentityKind.MANIFEST,
        **_identity_common(),
        boundary_ids=(_boundary_id(),),
        receiving_group_ids=(_h("group"),),
    )
    identity = continuity.make_gc_cross_segment_continuity_id(**values)
    assert len(identity) == 64
    for name, value in (
        ("instrument", "SI"),
        ("timeframe", "1M"),
        ("dataset_id", _h("other-dataset")),
        ("calendar_version", "other-calendar-v1"),
        ("boundary_calendar_digest", _h("other-boundary-calendar")),
        ("candidate_calendar_digest", _h("other-candidate-calendar")),
        ("timezone_data_version", f"{TZDATA_VERSION}-other"),
        ("seed_id", _h("other-seed")),
        ("canonical_control_digest", _h("other-complete-control")),
        ("boundary_ids", (_h("other-boundary"),)),
        ("receiving_group_ids", (_h("other-group"),)),
    ):
        changed = dict(values)
        changed[name] = value
        assert continuity.make_gc_cross_segment_continuity_id(**changed) != identity
    with pytest.raises((TypeError, ValueError)):
        continuity.make_gc_cross_segment_continuity_id(**values, boundary_ids=(_boundary_id(), _boundary_id()))
    for name, value in (
        ("source_segment_ordinal", 0),
        ("source_segment_id", _h("source")),
        ("receiving_segment_ordinal", 1),
        ("receiving_segment_id", _h("receiving")),
        ("contract", "GCG26-COMEX"),
        ("source_trade_date", date(2026, 1, 5)),
        ("receiving_trade_date", date(2026, 1, 6)),
        ("source_end_timestamp", _dt(2026, 1, 5, 17)),
        ("receiving_start_timestamp", _dt(2026, 1, 5, 18)),
        ("decision", continuity.GCCrossSegmentContinuityDecision.ELIGIBLE),
        ("reason_tokens", ("ELIGIBLE_STANDARD_BOUNDARY",)),
        ("dependency_references", (_dependency(),)),
        ("boundary_id", _boundary_id()),
        ("effective_index", 2),
        ("effective_timestamp", _dt(2026, 1, 6, 17)),
        ("receiving_references", (_receiving_reference(),)),
    ):
        with pytest.raises((TypeError, ValueError)):
            continuity.make_gc_cross_segment_continuity_id(**values, **{name: value})


def test_case_42_malformed_nested_values_fail_closed() -> None:
    for changed in (
        replace(_dependency(), object_id="BAD"),
        replace(_dependency(), first_known_index=True),
        replace(_dependency(), first_known_timestamp=datetime(2026, 1, 1)),
        replace(_dependency(), history_ids=(_h("x"), _h("x"))),
    ):
        with pytest.raises((TypeError, ValueError)):
            _boundary_id(dependency_references=(changed,))
    for changed in (
        replace(_receiving_reference(), object_id="BAD"),
        replace(_receiving_reference(), effective_index=True),
        replace(_receiving_reference(), effective_timestamp=datetime(2026, 1, 6, 17)),
        replace(_receiving_reference("FAIR_VALUE_GAP"), history_ids=(_h("x"), _h("x"))),
    ):
        with pytest.raises((TypeError, ValueError)):
            continuity.make_gc_cross_segment_continuity_id(
                identity_kind=continuity.GCCrossSegmentContinuityIdentityKind.RECEIVING_GROUP,
                **_identity_common(),
                boundary_id=_boundary_id(),
                receiving_segment_ordinal=1,
                receiving_segment_id=_h("receiving-segment"),
                effective_index=2,
                effective_timestamp=_dt(2026, 1, 6, 17),
                receiving_references=(changed,),
            )
    with pytest.raises((TypeError, ValueError)):
        _boundary_id(decision="ELIGIBLE")
    with pytest.raises((TypeError, ValueError)):
        _boundary_id(source_trade_date="2026-01-05")


def test_case_43_public_signatures_are_exact_keyword_only() -> None:
    builder = inspect.signature(continuity.make_gc_cross_segment_continuity_id)
    analyzer = inspect.signature(continuity.analyze_gc_cross_segment_continuity)
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in builder.parameters.values())
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in analyzer.parameters.values())
    assert tuple(builder.parameters) == (
        "identity_kind", "instrument", "timeframe", "dataset_id", "calendar_version",
        "boundary_calendar_digest", "candidate_calendar_digest", "timezone_data_version",
        "seed_id", "canonical_control_digest", "source_segment_ordinal", "source_segment_id",
        "receiving_segment_ordinal", "receiving_segment_id", "contract", "source_trade_date",
        "receiving_trade_date", "source_end_timestamp", "receiving_start_timestamp", "decision",
        "reason_tokens", "dependency_references", "boundary_id", "effective_index",
        "effective_timestamp", "receiving_references", "boundary_ids", "receiving_group_ids",
    )
    assert tuple(analyzer.parameters) == (
        "dataset_config", "dataset", "boundary_calendar_entries", "candidate_calendar_entries",
        "structural_seed", "canonical_candidate_evidence", "frontier_evidence", "candidate_config",
    )
    builder_annotations = (
        "GCCrossSegmentContinuityIdentityKind", "str", "str", "str", "str", "str", "str",
        "str", "str", "str", "int | None", "str | None", "int | None", "str | None",
        "str | None", "date | None", "date | None", "datetime | None", "datetime | None",
        "GCCrossSegmentContinuityDecision | None", "tuple[str, ...]",
        "tuple[GCContinuityDependencyReference, ...]", "str | None", "int | None",
        "datetime | None", "tuple[GCContinuityReceivingReference, ...]", "tuple[str, ...]",
        "tuple[str, ...]",
    )
    assert tuple(parameter.annotation for parameter in builder.parameters.values()) == builder_annotations
    assert builder.return_annotation == "str"
    assert tuple(parameter.annotation for parameter in analyzer.parameters.values()) == (
        "GCDatasetBuildConfig", "GCDatasetBuildResult | None",
        "tuple[GCSplitSessionCalendarEntry, ...] | None",
        "tuple[KillZoneCalendarEntry, ...] | None", "GCCanonicalSeedEvidence | None",
        "GCCandidateEvidenceResult | None", "GCCandidateFrontierEvidenceResult | None",
        "GCCandidateEvidenceConfig",
    )
    assert analyzer.return_annotation == "GCCrossSegmentContinuityResult"
    required_builder = tuple(builder.parameters)[:10]
    assert all(builder.parameters[name].default is inspect.Parameter.empty for name in required_builder)
    for name in tuple(builder.parameters)[10:20] + ("boundary_id", "effective_index", "effective_timestamp"):
        assert builder.parameters[name].default is None
    for name in ("reason_tokens", "dependency_references", "receiving_references", "boundary_ids", "receiving_group_ids"):
        assert builder.parameters[name].default == ()
    assert all(
        analyzer.parameters[name].default is inspect.Parameter.empty
        for name in tuple(analyzer.parameters)[:6]
    )
    assert analyzer.parameters["frontier_evidence"].default is None
    assert analyzer.parameters["candidate_config"].default == GCCandidateEvidenceConfig()


def test_case_57_explicit_none_frontier_is_legacy_object_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(receiving_group=True)
    implicit = _run(monkeypatch, fixture)
    explicit = _run(monkeypatch, fixture, frontier_evidence=None)
    assert explicit == implicit


def test_case_58_valid_frontier_appends_one_boundary_and_preserves_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _frontier_fixture()
    first = _run(monkeypatch, fixture)
    second = _run(monkeypatch, fixture)
    assert first == second
    assert first.status is SMCV2PrimitiveStatus.UNKNOWN
    assert first.reasons == first.blocking_reasons == ("CANONICAL_CONTROL_UNKNOWN",)
    assert first.manifest is not None
    assert len(first.boundaries) == 1
    boundary = first.boundaries[0]
    assert (boundary.source_segment_ordinal, boundary.receiving_segment_ordinal) == (1, 2)
    assert boundary.decision is continuity.GCCrossSegmentContinuityDecision.ELIGIBLE
    assert first.manifest.boundary_ids == (boundary.boundary_id,)


def test_case_44_public_dataclasses_enums_version_and_exports_are_exact() -> None:
    classes = (
        continuity.GCContinuityDependencyReference,
        continuity.GCContinuityReceivingReference,
        continuity.GCCrossSegmentBoundary,
        continuity.GCContinuityReceivingGroup,
        continuity.GCCrossSegmentContinuityManifest,
        continuity.GCCrossSegmentContinuityResult,
    )
    assert all(is_dataclass(item) and item.__dataclass_params__.frozen for item in classes)
    expected_fields = {
        continuity.GCContinuityDependencyReference: (
            ("detector_name", "str"), ("object_kind", "str"), ("object_id", "str"),
            ("owning_segment_ordinal", "int"), ("owning_segment_id", "str"),
            ("first_known_index", "int"), ("first_known_timestamp", "datetime"),
            ("effective_index", "int"), ("effective_timestamp", "datetime"), ("state", "str"),
            ("history_ids", "tuple[str, ...]"), ("source_moment_digest", "str"),
            ("object_digest", "str"),
        ),
        continuity.GCContinuityReceivingReference: (
            ("detector_name", "str"), ("object_kind", "str"), ("object_id", "str"),
            ("owning_segment_ordinal", "int"), ("owning_segment_id", "str"),
            ("first_known_index", "int"), ("first_known_timestamp", "datetime"),
            ("effective_index", "int"), ("effective_timestamp", "datetime"),
            ("semantic_discriminator", "str"), ("history_ids", "tuple[str, ...]"),
            ("source_moment_digest", "str"), ("object_digest", "str"),
        ),
        continuity.GCCrossSegmentBoundary: (
            ("boundary_id", "str"), ("source_segment_ordinal", "int"),
            ("source_segment_id", "str"), ("receiving_segment_ordinal", "int"),
            ("receiving_segment_id", "str"), ("contract", "str"),
            ("source_trade_date", "date"), ("receiving_trade_date", "date"),
            ("source_end_timestamp", "datetime"), ("receiving_start_timestamp", "datetime"),
            ("decision", "GCCrossSegmentContinuityDecision"),
            ("reason_tokens", "tuple[str, ...]"),
            ("dependency_references", "tuple[GCContinuityDependencyReference, ...]"),
        ),
        continuity.GCContinuityReceivingGroup: (
            ("group_id", "str"), ("boundary_id", "str"),
            ("receiving_segment_ordinal", "int"), ("receiving_segment_id", "str"),
            ("effective_index", "int"), ("effective_timestamp", "datetime"),
            ("references", "tuple[GCContinuityReceivingReference, ...]"),
        ),
        continuity.GCCrossSegmentContinuityManifest: (
            ("manifest_id", "str"), ("version", "str"), ("instrument", "str"),
            ("timeframe", "str"), ("dataset_id", "str"), ("calendar_version", "str"),
            ("boundary_calendar_digest", "str"), ("candidate_calendar_digest", "str"),
            ("timezone_data_version", "str"), ("seed_id", "str"),
            ("canonical_control_digest", "str"), ("boundary_ids", "tuple[str, ...]"),
            ("receiving_group_ids", "tuple[str, ...]"),
        ),
        continuity.GCCrossSegmentContinuityResult: (
            ("status", "SMCV2PrimitiveStatus"),
            ("boundaries", "tuple[GCCrossSegmentBoundary, ...]"),
            ("receiving_groups", "tuple[GCContinuityReceivingGroup, ...]"),
            ("manifest", "GCCrossSegmentContinuityManifest | None"),
            ("reasons", "tuple[str, ...]"), ("blocking_reasons", "tuple[str, ...]"),
        ),
    }
    for cls, expected in expected_fields.items():
        actual = fields(cls)
        assert tuple((item.name, str(item.type)) for item in actual) == expected
        if cls is continuity.GCCrossSegmentContinuityResult:
            assert tuple(item.default for item in actual) == (MISSING, (), (), None, (), ())
        else:
            assert all(item.default is MISSING for item in actual)
    with pytest.raises(FrozenInstanceError):
        continuity.GCCrossSegmentContinuityResult(SMCV2PrimitiveStatus.NONE).status = SMCV2PrimitiveStatus.VALID
    assert [item.value for item in continuity.GCCrossSegmentContinuityIdentityKind] == ["BOUNDARY", "RECEIVING_GROUP", "MANIFEST"]
    assert [item.value for item in continuity.GCCrossSegmentContinuityDecision] == ["ELIGIBLE", "INELIGIBLE"]
    assert continuity.GC_CROSS_SEGMENT_CONTINUITY_VERSION == "GC-CROSS-SEGMENT-CONTINUITY-V1"
    assert continuity.__all__ == (
        "GC_CROSS_SEGMENT_CONTINUITY_VERSION", "GCCrossSegmentContinuityIdentityKind",
        "GCCrossSegmentContinuityDecision", "GCContinuityDependencyReference",
        "GCContinuityReceivingReference", "GCCrossSegmentBoundary",
        "GCContinuityReceivingGroup", "GCCrossSegmentContinuityManifest",
        "GCCrossSegmentContinuityResult", "make_gc_cross_segment_continuity_id",
        "analyze_gc_cross_segment_continuity",
    )


def test_case_45_complete_later_group_is_prefix_invariant(monkeypatch: pytest.MonkeyPatch) -> None:
    before = _run(monkeypatch, _fixture())
    after = _run(monkeypatch, _fixture(receiving_group=True))
    assert before.boundaries[0] == after.boundaries[0]


def test_case_46_historical_calendar_reorder_is_ineligible(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture()
    calendar = fixture["boundary_calendar_entries"]
    assert isinstance(calendar, tuple)
    assert _run(monkeypatch, fixture, boundary_calendar_entries=calendar[::-1]).status is SMCV2PrimitiveStatus.INVALID


def test_case_47_reporting_is_deterministic_and_nonranking(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _run(monkeypatch, _fixture(receiving_group=True))
    assert result.reasons == ("ELIGIBLE_BOUNDARY_PRESENT",)
    assert not hasattr(result, "score") and not hasattr(result, "rank") and not hasattr(result, "pnl")


def test_case_48_exact_scope_and_no_authority_surface() -> None:
    source = (ROOT / "analysis" / "gc_cross_segment_continuity.py").read_text(encoding="utf-8")
    assert (ROOT / "tests" / "test_gc_cross_segment_continuity.py").is_file()
    assert "open(" not in source and "requests." not in source and "subprocess" not in source
    assert all(token not in continuity.__all__ for token in ("train", "predict", "execute", "order", "pnl"))


def test_case_49_exact_legacy_v3_multi_segment_identity_is_accepted_and_immutable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _with_segment_identity_versions(
        _fixture(),
        manifest_version=LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        segment_versions=(
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        ),
    )
    dataset_before = fixture["dataset"]
    control_before = fixture["canonical_candidate_evidence"]
    result = _run(monkeypatch, fixture)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert fixture["dataset"] == dataset_before
    assert fixture["canonical_candidate_evidence"] == control_before


def test_case_50_legacy_v3_one_segment_identity_drift_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _with_segment_identity_versions(
        _fixture(),
        manifest_version=LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        segment_versions=(
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        ),
    )
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    drifted = replace(dataset.segments[0], segment_id="0" * 64)
    fixture["dataset"] = replace(
        dataset,
        segments=(drifted, dataset.segments[1]),
        manifest=replace(
            dataset.manifest,
            segment_ids=(drifted.segment_id, dataset.segments[1].segment_id),
        ),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize(
    "version",
    ("", "GC-DATASET-BUILDER-V2", "GC-DATASET-BUILDER-V4", "legacy-v3"),
)
def test_case_51_unrecognized_or_noncanonical_manifest_version_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    version: str,
) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    fixture["dataset"] = replace(
        dataset,
        manifest=replace(dataset.manifest, version=version),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID


def test_case_52_legacy_v3_manifest_rejects_current_v5_segment_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    fixture["dataset"] = replace(
        dataset,
        manifest=replace(
            dataset.manifest,
            version=LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        ),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID


def test_case_53_current_v5_manifest_rejects_legacy_v3_segment_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _with_segment_identity_versions(
        _fixture(),
        manifest_version=GC_DATASET_BUILDER_VERSION,
        segment_versions=(
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        ),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID


def test_case_54_mixed_v3_v5_segment_identity_graph_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _with_segment_identity_versions(
        _fixture(),
        manifest_version=LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        segment_versions=(
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
            GC_DATASET_BUILDER_VERSION,
        ),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID


def test_case_55_current_v5_identity_path_remains_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture()
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    assert dataset.manifest.version == GC_DATASET_BUILDER_VERSION
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.VALID


def test_case_56_oos_segment_remains_forbidden_under_legacy_v3(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _with_segment_identity_versions(
        _fixture(),
        manifest_version=LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        segment_versions=(
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
            LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        ),
    )
    dataset = fixture["dataset"]
    assert isinstance(dataset, GCDatasetBuildResult) and dataset.manifest is not None
    source = dataset.segments[0]
    oos = replace(
        source,
        partition=GCSegmentPartition.OOS_HOLDOUT,
        segment_id=_legacy_v3_segment_id(
            config=_config(),
            contract=source.contract,
            partition=GCSegmentPartition.OOS_HOLDOUT,
            first_trade_date=source.first_trade_date,
            last_trade_date=source.last_trade_date,
            source_ids=source.source_ids,
            bars=source.bars,
            preceding_missing_bar_count=source.preceding_missing_bar_count,
        ),
    )
    fixture["dataset"] = replace(
        dataset,
        segments=(oos, dataset.segments[1]),
        manifest=replace(
            dataset.manifest,
            segment_ids=(oos.segment_id, dataset.segments[1].segment_id),
        ),
    )
    assert _run(monkeypatch, fixture).status is SMCV2PrimitiveStatus.INVALID
