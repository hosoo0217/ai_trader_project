"""Locked public-contract tests for the GC Candidate Evidence builder."""

from __future__ import annotations

import inspect
from dataclasses import MISSING, fields, is_dataclass, replace
from datetime import datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import get_type_hints
from zoneinfo import ZoneInfo

import pytest

import analysis.gc_candidate_evidence_builder as candidate_module
from analysis.gc_dataset_builder import (
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
)
from analysis.gc_structural_seed_evidence import (
    GCStructuralSeedResult,
    build_gc_structural_seed_evidence,
)

from analysis.gc_candidate_evidence_builder import (
    GC_CANDIDATE_EVIDENCE_VERSION,
    GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION,
    GCCandidateEvidenceConfig,
    GCCandidateEvidenceIdentityKind,
    GCCandidateEvidenceManifest,
    GCCandidateEvidenceResult,
    GCCandidateEvidenceSegmentResult,
    GCCandidateFrontierEvidence,
    GCCandidateFrontierEvidenceResult,
    GCCandidateFrontierIdentityKind,
    GCCandidateFrontierSegmentEvidence,
    GCSegmentCandidateEvidence,
    analyze_gc_candidate_frontier_evidence,
    build_gc_candidate_evidence,
    make_gc_candidate_evidence_id,
    make_gc_candidate_frontier_evidence_id,
)
from smc.dealing_range import DealingRangeConfig
from smc.dealing_range import DealingRangeResult
from smc.equal_liquidity import EqualLiquidityConfig, EqualLiquidityResult
from smc.fair_value_gap import FairValueGapContextLink, FairValueGapResult
from smc.inducement import (
    InducementPendingHorizon,
    InducementPendingHorizonResult,
    InducementResult,
)
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneResult,
    KillZoneSessionStatus,
)
from smc.liquidity_map import LiquidityMapResult
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus
from smc.smc_v2_primitives import SMCV2EventProvenance
from tests.test_gc_structural_seed_evidence import (
    _bullish_bars as _structural_bars,
    _dataset as _structural_dataset,
)
from tests.test_gc_feature_label_builder import (
    _candidate as _feature_candidate,
    _dataset as _feature_dataset,
)


_DETECTOR_VERSIONS = (
    ("EQUAL_LIQUIDITY", "SMC-V2-EQUAL-LIQUIDITY-1"),
    ("DEALING_RANGE", "SMC-V2-DEALING-RANGE-1"),
    ("LIQUIDITY_MAP", "SMC-V2-LIQUIDITY-MAP-1"),
    ("FAIR_VALUE_GAP", "SMC-V2-FAIR-VALUE-GAP-1"),
    ("INDUCEMENT", "SMC-V2-INDUCEMENT-1"),
    ("KILL_ZONE", "SMC-V2-KILL-ZONE-1"),
)


def _identity_kwargs() -> dict[str, object]:
    segment_id = "1" * 64
    return {
        "identity_kind": GCCandidateEvidenceIdentityKind.BUNDLE,
        "instrument": "gc",
        "timeframe": "5m",
        "tick_size": Decimal("0.10"),
        "dataset_id": "2" * 64,
        "calendar_version": "CME-GC-2026-V1",
        "timezone_data_version": "2025.2",
        "seed_id": "3" * 64,
        "config": GCCandidateEvidenceConfig(),
        "detector_versions": _DETECTOR_VERSIONS,
        "segment_result_ids": ((segment_id, tuple(str(index) * 64 for index in range(4, 10))),),
        "candidate_references": ((segment_id, "a" * 64),),
    }


def _calendar(dataset: GCDatasetBuildResult) -> tuple[KillZoneCalendarEntry, ...]:
    assert dataset.manifest is not None
    ny = ZoneInfo("America/New_York")
    return tuple(
        KillZoneCalendarEntry(
            calendar_version=dataset.manifest.calendar_version,
            trade_date=segment.first_trade_date,
            session_status=KillZoneSessionStatus.OPEN,
            session_open_timestamp=datetime.combine(
                segment.first_trade_date - timedelta(days=1), time(18), tzinfo=ny
            ),
            session_close_timestamp=datetime.combine(
                segment.first_trade_date, time(17), tzinfo=ny
            ),
        )
        for segment in dataset.segments
    )


def _valid_inputs(*, two_segments: bool = False):
    config, dataset = _structural_dataset(
        second_bars=_structural_bars() if two_segments else None
    )
    seed_result = build_gc_structural_seed_evidence(
        dataset_config=config,
        dataset=dataset,
    )
    assert seed_result.status is SMCV2PrimitiveStatus.VALID
    assert seed_result.seed is not None
    return config, dataset, _calendar(dataset), seed_result.seed


def _none_result(result_type: type):
    return result_type(SMCV2PrimitiveStatus.NONE, reasons=("NONE",))


def _patch_valid_candidate_pipeline(monkeypatch: pytest.MonkeyPatch):
    config, dataset, calendars = _feature_dataset()
    candidate = _feature_candidate(dataset, calendars)
    seed_result = build_gc_structural_seed_evidence(
        dataset_config=config,
        dataset=dataset,
    )
    assert seed_result.seed is not None
    gap = candidate.fair_value_gap
    seed = replace(
        seed_result.seed,
        structure_events=(candidate.structure_event,),
        fair_value_gap_context_links=(
            FairValueGapContextLink(
                gap.formation_end_index,
                gap.formation_end_timestamp,
                gap.displacement_id,
                gap.structure_event_id,
                gap.structure_event_type,
            ),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "validate_gc_structural_seed_evidence",
        lambda **_kwargs: GCStructuralSeedResult(
            SMCV2PrimitiveStatus.VALID,
            seed,
            ("STRUCTURAL_EVIDENCE_VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_equal_liquidity",
        lambda **_kwargs: EqualLiquidityResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.internal_pool,),
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_dealing_ranges",
        lambda **_kwargs: DealingRangeResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.active_range,),
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_liquidity_map",
        lambda **_kwargs: LiquidityMapResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.liquidity_map_snapshot,),
            (),
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_fair_value_gaps",
        lambda **_kwargs: FairValueGapResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.fair_value_gap,),
            candidate.fair_value_gap_transitions,
            candidate.fair_value_gap_snapshots,
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_inducements",
        lambda **_kwargs: InducementResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.inducement,),
            (candidate.inducement_snapshot,),
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_kill_zones",
        lambda **_kwargs: KillZoneResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.kill_zone_context,),
            (candidate.kill_zone_snapshot,),
            ("VALID",),
        ),
    )
    return config, dataset, calendars, seed, candidate


def test_case_39_bundle_and_manifest_identity_are_deterministic() -> None:
    kwargs = _identity_kwargs()
    bundle = make_gc_candidate_evidence_id(**kwargs)  # type: ignore[arg-type]
    assert len(bundle) == 64
    assert bundle == make_gc_candidate_evidence_id(**kwargs)  # type: ignore[arg-type]
    assert bundle == make_gc_candidate_evidence_id(
        **{**kwargs, "instrument": " GC ", "timeframe": " 5M ", "tick_size": Decimal("0.1")}
    )  # type: ignore[arg-type]
    manifest = make_gc_candidate_evidence_id(
        **{**kwargs, "identity_kind": GCCandidateEvidenceIdentityKind.MANIFEST, "bundle_id": bundle}
    )  # type: ignore[arg-type]
    assert len(manifest) == 64 and manifest != bundle


def test_cases_01_03_47_canonical_inputs_build_repeatable_none_evidence() -> None:
    config, dataset, calendars, seed = _valid_inputs()
    first = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    second = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert first == second
    assert first.status is SMCV2PrimitiveStatus.NONE
    assert first.manifest is None and first.candidates == ()
    assert len(first.segment_results) == 1
    assert len(first.segment_results[0].result_ids) == 6


def test_cases_04_05_missing_context_does_not_mask_malformed_dataset() -> None:
    config, dataset, _, _ = _valid_inputs()
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=object(),  # type: ignore[arg-type]
        calendar_entries=None,
        structural_seed=None,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.candidates == () and result.segment_results == ()

    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=replace(dataset, dataset_id="f" * 64),
        calendar_entries=None,
        structural_seed=None,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_04_genuine_missing_context_is_unknown_after_validation() -> None:
    config, dataset, _, seed = _valid_inputs()
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=None,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.reasons == ("MISSING_TOP_LEVEL_CONTEXT",)


def test_cases_03_05_missing_dataset_does_not_mask_malformed_calendar_geometry() -> None:
    config, dataset, calendars, seed = _valid_inputs()
    entry = calendars[0]
    assert entry.session_open_timestamp is not None
    malformed = replace(
        entry,
        session_open_timestamp=entry.session_open_timestamp - timedelta(days=3),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=None,
        calendar_entries=(malformed,),
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_SUPPLIED_CONTEXT",)
    assert result.candidates == result.segment_results == ()


def test_case_06_exposed_oos_stops_before_seed_validation_or_analyzers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs()
    assert dataset.manifest is not None
    oos_dataset = replace(
        dataset,
        manifest=replace(dataset.manifest, oos_bar_count=1),
    )
    calls: list[str] = []

    def forbidden(**_kwargs):
        calls.append("CALLED")
        raise AssertionError("OOS evidence must stop before validation/analyzers")

    monkeypatch.setattr(candidate_module, "validate_gc_structural_seed_evidence", forbidden)
    for name in (
        "analyze_equal_liquidity",
        "analyze_dealing_ranges",
        "analyze_liquidity_map",
        "analyze_fair_value_gaps",
        "analyze_inducements",
        "analyze_kill_zones",
    ):
        monkeypatch.setattr(candidate_module, name, forbidden)

    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=oos_dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("OOS_ACCESS_FORBIDDEN",)
    assert result.candidates == result.segment_results == ()
    assert calls == []


def test_case_09_public_seed_validator_is_called_exactly_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs()
    original = candidate_module.validate_gc_structural_seed_evidence
    calls = 0

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return original(**kwargs)

    monkeypatch.setattr(candidate_module, "validate_gc_structural_seed_evidence", counted)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert calls == 1


@pytest.mark.parametrize(
    "status",
    (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ),
)
def test_case_10_structural_validator_higher_status_stops_before_analyzers(
    monkeypatch: pytest.MonkeyPatch,
    status: SMCV2PrimitiveStatus,
) -> None:
    config, dataset, calendars, seed = _valid_inputs()
    calls: list[str] = []
    monkeypatch.setattr(
        candidate_module,
        "validate_gc_structural_seed_evidence",
        lambda **_kwargs: GCStructuralSeedResult(
            status,
            reasons=(f"SEED_{status.value}",),
            blocking_reasons=(f"SEED_{status.value}",),
        ),
    )

    def forbidden(**_kwargs):
        calls.append("ANALYZER")
        raise AssertionError("blocked structural evidence must stop before analyzers")

    for name in (
        "analyze_equal_liquidity",
        "analyze_dealing_ranges",
        "analyze_liquidity_map",
        "analyze_fair_value_gaps",
        "analyze_inducements",
        "analyze_kill_zones",
    ):
        monkeypatch.setattr(candidate_module, name, forbidden)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is status
    assert result.candidates == result.segment_results == ()
    assert calls == []


def test_cases_17_24_analyzers_run_once_in_locked_segment_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs(two_segments=True)
    calls: list[str] = []
    specifications = (
        ("analyze_equal_liquidity", "EQUAL", EqualLiquidityResult),
        ("analyze_dealing_ranges", "RANGE", DealingRangeResult),
        ("analyze_liquidity_map", "MAP", LiquidityMapResult),
        ("analyze_fair_value_gaps", "FVG", FairValueGapResult),
        ("analyze_inducements", "INDUCEMENT", InducementResult),
        ("analyze_kill_zones", "KILL", KillZoneResult),
    )
    for function_name, label, result_type in specifications:
        def fake(*, _label=label, _result_type=result_type, **_kwargs):
            calls.append(_label)
            return _none_result(_result_type)

        monkeypatch.setattr(candidate_module, function_name, fake)

    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    expected = ["EQUAL", "RANGE", "MAP", "FVG", "INDUCEMENT", "KILL"] * 2
    assert calls == expected
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert len(result.segment_results) == 2


def test_cases_07_22_23_bar_projection_and_calendar_slices_are_segment_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs(two_segments=True)
    captured: list[tuple[str, object]] = []

    def equal(**kwargs):
        captured.append(("EQUAL", kwargs))
        return _none_result(EqualLiquidityResult)

    def ranges(**kwargs):
        captured.append(("RANGE", kwargs))
        return _none_result(DealingRangeResult)

    def liquidity(**kwargs):
        captured.append(("MAP", kwargs))
        return _none_result(LiquidityMapResult)

    def gaps(**kwargs):
        captured.append(("FVG", kwargs))
        return _none_result(FairValueGapResult)

    def inducements(**kwargs):
        captured.append(("INDUCEMENT", kwargs))
        return _none_result(InducementResult)

    def kill(**kwargs):
        captured.append(("KILL", kwargs))
        return _none_result(KillZoneResult)

    monkeypatch.setattr(candidate_module, "analyze_equal_liquidity", equal)
    monkeypatch.setattr(candidate_module, "analyze_dealing_ranges", ranges)
    monkeypatch.setattr(candidate_module, "analyze_liquidity_map", liquidity)
    monkeypatch.setattr(candidate_module, "analyze_fair_value_gaps", gaps)
    monkeypatch.setattr(candidate_module, "analyze_inducements", inducements)
    monkeypatch.setattr(candidate_module, "analyze_kill_zones", kill)

    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert [name for name, _ in captured] == [
        "EQUAL", "RANGE", "MAP", "FVG", "INDUCEMENT", "KILL",
    ] * 2
    for ordinal, segment in enumerate(dataset.segments):
        block = dict(captured[ordinal * 6 : ordinal * 6 + 6])
        equal_observations = block["EQUAL"]["observations"]
        range_observations = block["RANGE"]["observations"]
        candles = block["FVG"]["candles"]
        observations = block["INDUCEMENT"]["observations"]
        kill_observations = block["KILL"]["observations"]
        assert len(equal_observations) == len(segment.bars)
        assert len(range_observations) == len(segment.bars)
        assert len(candles) == len(segment.bars)
        assert len(observations) == len(segment.bars)
        assert len(kill_observations) == len(segment.bars)
        for bar, equal_item, range_item, candle, observation, kill_item in zip(
            segment.bars,
            equal_observations,
            range_observations,
            candles,
            observations,
            kill_observations,
            strict=True,
        ):
            assert (equal_item.index, equal_item.timestamp, equal_item.high_tick, equal_item.low_tick, equal_item.close_tick) == (
                bar.index, bar.timestamp, bar.high_tick, bar.low_tick, bar.close_tick,
            )
            assert range_item == candidate_module.DealingRangeObservation(
                bar.index, bar.timestamp, bar.high_tick, bar.low_tick, bar.close_tick,
            )
            assert candle == candidate_module.FairValueGapCandle(
                bar.index, bar.timestamp, bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick,
            )
            assert observation == candidate_module.InducementObservation(
                bar.index, bar.timestamp, bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick, True,
            )
            assert kill_item == candidate_module.KillZoneObservation(bar.index, bar.timestamp, True)
        assert block["KILL"]["calendar_entries"] == tuple(
            item
            for item in calendars
            if segment.first_trade_date <= item.trade_date <= segment.last_trade_date
        )


def test_cases_21_22_inducement_receives_only_eligible_dependency_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(
        monkeypatch
    )
    internal_range = replace(
        candidate.active_range,
        kind=candidate_module.DealingRangeKind.INTERNAL,
    )
    unqualified_gap_id = "d" * 64
    unqualified_gap = replace(
        candidate.fair_value_gap,
        gap_id=unqualified_gap_id,
        displacement_id=None,
    )
    unqualified_transitions = tuple(
        replace(
            item,
            transition_id=f"{position + 1:064x}",
            gap_id=unqualified_gap_id,
        )
        for position, item in enumerate(candidate.fair_value_gap_transitions)
    )
    unqualified_snapshots = tuple(
        replace(
            item,
            snapshot_id=f"{position + 101:064x}",
            gap_id=unqualified_gap_id,
            transition_ids=tuple(
                transition.transition_id
                for transition in unqualified_transitions[: position + 1]
            ),
        )
        for position, item in enumerate(candidate.fair_value_gap_snapshots)
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_dealing_ranges",
        lambda **_kwargs: DealingRangeResult(
            SMCV2PrimitiveStatus.VALID,
            (internal_range, candidate.active_range),
            ("VALID",),
        ),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_fair_value_gaps",
        lambda **_kwargs: FairValueGapResult(
            SMCV2PrimitiveStatus.VALID,
            (unqualified_gap, candidate.fair_value_gap),
            unqualified_transitions + candidate.fair_value_gap_transitions,
            unqualified_snapshots + candidate.fair_value_gap_snapshots,
            ("VALID",),
        ),
    )
    captured: dict[str, object] = {}

    def inducements(**kwargs):
        captured.update(kwargs)
        return _none_result(InducementResult)

    monkeypatch.setattr(candidate_module, "analyze_inducements", inducements)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert captured["dealing_range_snapshots"] == (candidate.active_range,)
    assert captured["fair_value_gaps"] == (candidate.fair_value_gap,)
    assert captured["fair_value_gap_transitions"] == (
        candidate.fair_value_gap_transitions
    )
    assert captured["fair_value_gap_snapshots"] == candidate.fair_value_gap_snapshots


@pytest.mark.parametrize(
    ("status", "reason"),
    (
        (SMCV2PrimitiveStatus.UNKNOWN, "UPSTREAM_UNKNOWN"),
        (SMCV2PrimitiveStatus.AMBIGUOUS, "UPSTREAM_AMBIGUOUS"),
        (SMCV2PrimitiveStatus.INVALID, "UPSTREAM_INVALID"),
    ),
)
def test_cases_24_36_blocking_upstream_status_stops_downstream_calls(
    monkeypatch: pytest.MonkeyPatch,
    status: SMCV2PrimitiveStatus,
    reason: str,
) -> None:
    config, dataset, calendars, seed = _valid_inputs()
    calls: list[str] = []
    monkeypatch.setattr(
        candidate_module,
        "analyze_equal_liquidity",
        lambda **_kwargs: EqualLiquidityResult(status, reasons=(reason,)),
    )

    def forbidden(**_kwargs):
        calls.append("DOWNSTREAM")
        raise AssertionError("a blocked detector must stop the current chain")

    for name in (
        "analyze_dealing_ranges",
        "analyze_liquidity_map",
        "analyze_fair_value_gaps",
        "analyze_inducements",
        "analyze_kill_zones",
    ):
        monkeypatch.setattr(candidate_module, name, forbidden)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is status
    assert result.reasons == (reason,)
    assert result.candidates == result.segment_results == ()
    assert calls == []


@pytest.mark.parametrize("failure", ("EXCEPTION", "WRONG_RESULT_TYPE", "MALFORMED_REASONS"))
def test_cases_23_24_41_detector_failure_is_contained_without_partial_promotion(
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    config, dataset, calendars, seed = _valid_inputs()

    def broken(**_kwargs):
        if failure == "EXCEPTION":
            raise RuntimeError("contained detector failure")
        if failure == "WRONG_RESULT_TYPE":
            return object()
        return replace(
            _none_result(EqualLiquidityResult),
            reasons=["NOT_A_TUPLE"],  # type: ignore[arg-type]
        )

    monkeypatch.setattr(candidate_module, "analyze_equal_liquidity", broken)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_CANDIDATE_EVIDENCE",)
    assert result.candidates == result.segment_results == ()


def test_cases_24_37_45_later_invalid_group_preserves_only_prior_segment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs(two_segments=True)
    equal_calls = 0

    def equal(**_kwargs):
        nonlocal equal_calls
        equal_calls += 1
        if equal_calls == 2:
            return EqualLiquidityResult(
                SMCV2PrimitiveStatus.INVALID,
                reasons=("LATER_INVALID",),
                blocking_reasons=("LATER_INVALID",),
            )
        return _none_result(EqualLiquidityResult)

    monkeypatch.setattr(candidate_module, "analyze_equal_liquidity", equal)
    monkeypatch.setattr(candidate_module, "analyze_dealing_ranges", lambda **_kwargs: _none_result(DealingRangeResult))
    monkeypatch.setattr(candidate_module, "analyze_liquidity_map", lambda **_kwargs: _none_result(LiquidityMapResult))
    monkeypatch.setattr(candidate_module, "analyze_fair_value_gaps", lambda **_kwargs: _none_result(FairValueGapResult))
    monkeypatch.setattr(candidate_module, "analyze_inducements", lambda **_kwargs: _none_result(InducementResult))
    monkeypatch.setattr(candidate_module, "analyze_kill_zones", lambda **_kwargs: _none_result(KillZoneResult))

    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("LATER_INVALID",)
    assert len(result.segment_results) == 1
    assert result.segment_results[0].segment_id == dataset.segments[0].segment_id
    assert result.candidates == () and result.manifest is None


def test_cases_25_35_valid_candidate_is_byte_exact_and_manifest_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert len(result.candidates) == len(result.segment_results) == 1
    wrapped = result.candidates[0]
    assert wrapped.segment_ordinal == 0
    assert wrapped.segment_id == dataset.segments[0].segment_id
    assert wrapped.evidence == candidate
    assert result.manifest is not None
    assert result.manifest.candidate_references == (
        (wrapped.segment_id, candidate.inducement.inducement_id),
    )
    assert result.manifest.segment_result_ids == (
        (wrapped.segment_id, result.segment_results[0].result_ids),
    )
    assert result.manifest.bundle_id == make_gc_candidate_evidence_id(
        **{
            **_identity_kwargs(),
            "instrument": config.instrument,
            "timeframe": config.timeframe,
            "tick_size": config.tick_size,
            "dataset_id": dataset.dataset_id,
            "calendar_version": dataset.manifest.calendar_version,
            "timezone_data_version": dataset.manifest.timezone_data_version,
            "seed_id": seed.seed_id,
            "config": GCCandidateEvidenceConfig(),
            "segment_result_ids": result.manifest.segment_result_ids,
            "candidate_references": result.manifest.candidate_references,
        }
    )


@pytest.mark.parametrize("forked", (False, True))
def test_cases_33_34_same_segment_duplicate_collapses_but_fork_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    forked: bool,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    duplicate = candidate.inducement
    if forked:
        duplicate = replace(
            duplicate,
            reclaim_close_tick=duplicate.reclaim_close_tick + 1,
        )
    monkeypatch.setattr(
        candidate_module,
        "analyze_inducements",
        lambda **_kwargs: InducementResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.inducement, duplicate),
            (candidate.inducement_snapshot,),
            ("VALID",),
        ),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    if forked:
        assert result.status is SMCV2PrimitiveStatus.INVALID
        assert result.candidates == result.segment_results == ()
    else:
        assert result.status is SMCV2PrimitiveStatus.VALID
        assert len(result.candidates) == 1


def test_cases_21_30_event_fvg_source_suffix_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    timestamps = candidate.fair_value_gap.source_timestamps
    mismatched_gap = replace(
        candidate.fair_value_gap,
        source_timestamps=(timestamps[0], timestamps[1], timestamps[2] + timedelta(microseconds=1)),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_fair_value_gaps",
        lambda **_kwargs: FairValueGapResult(
            SMCV2PrimitiveStatus.VALID,
            (mismatched_gap,),
            candidate.fair_value_gap_transitions,
            candidate.fair_value_gap_snapshots,
            ("VALID",),
        ),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_CANDIDATE_EVIDENCE",)
    assert result.candidates == result.segment_results == ()


def test_case_28_fvg_transition_snapshot_history_must_mirror_one_to_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    snapshots = candidate.fair_value_gap_snapshots
    assert snapshots
    malformed = (
        replace(snapshots[0], transition_ids=("f" * 64,)),
        *snapshots[1:],
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_fair_value_gaps",
        lambda **_kwargs: FairValueGapResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.fair_value_gap,),
            candidate.fair_value_gap_transitions,
            malformed,
            ("VALID",),
        ),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_CANDIDATE_EVIDENCE",)
    assert result.candidates == result.segment_results == ()


@pytest.mark.parametrize("mutation", ("MAP_RANGE", "INTERNAL_SOURCE"))
def test_cases_25_27_candidate_references_reconcile_range_and_pool_roles(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    map_snapshot = candidate.liquidity_map_snapshot
    if mutation == "MAP_RANGE":
        malformed_map = replace(map_snapshot, active_range_lineage_id="e" * 64)
    else:
        classifications = tuple(
            replace(item, source_id="e" * 64)
            if item.classification_id == candidate.internal_pool_classification.classification_id
            else item
            for item in map_snapshot.classifications
        )
        malformed_map = replace(map_snapshot, classifications=classifications)
    monkeypatch.setattr(
        candidate_module,
        "analyze_liquidity_map",
        lambda **_kwargs: LiquidityMapResult(
            SMCV2PrimitiveStatus.VALID,
            (malformed_map,),
            (),
            ("VALID",),
        ),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.candidates == result.segment_results == ()


def test_cases_27_30_stale_pre_sweep_active_range_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed, candidate = _patch_valid_candidate_pipeline(monkeypatch)
    original = candidate.active_range.first_known_provenance
    later = SMCV2EventProvenance(
        source_indices=(original.source_indices[-1] + 1,),
        source_timestamps=(original.source_timestamps[-1] + timedelta(minutes=5),),
        confirmation_index=original.confirmation_index + 1,
        confirmation_timestamp=original.confirmation_timestamp + timedelta(minutes=5),
    )
    later_range = replace(
        candidate.active_range,
        snapshot_id="b" * 64,
        first_known_provenance=later,
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_dealing_ranges",
        lambda **_kwargs: DealingRangeResult(
            SMCV2PrimitiveStatus.VALID,
            (candidate.active_range, later_range),
            ("VALID",),
        ),
    )
    result = build_gc_candidate_evidence(
        dataset_config=config,
        dataset=dataset,
        calendar_entries=calendars,
        structural_seed=seed,
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_CANDIDATE_EVIDENCE",)
    assert result.candidates == result.segment_results == ()


def test_case_42_public_functions_are_exactly_keyword_only() -> None:
    builder = inspect.signature(build_gc_candidate_evidence)
    assert tuple(builder.parameters) == (
        "dataset_config",
        "dataset",
        "calendar_entries",
        "structural_seed",
        "config",
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in builder.parameters.values()
    )
    assert builder.parameters["config"].default == GCCandidateEvidenceConfig()

    identity = inspect.signature(make_gc_candidate_evidence_id)
    assert tuple(identity.parameters) == (
        "identity_kind",
        "instrument",
        "timeframe",
        "tick_size",
        "dataset_id",
        "calendar_version",
        "timezone_data_version",
        "seed_id",
        "config",
        "detector_versions",
        "segment_result_ids",
        "candidate_references",
        "bundle_id",
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in identity.parameters.values()
    )
    assert identity.parameters["bundle_id"].default is None

    frontier = inspect.signature(analyze_gc_candidate_frontier_evidence)
    assert tuple(frontier.parameters) == (
        "dataset_config",
        "dataset",
        "calendar_entries",
        "structural_seed",
        "canonical_candidate_evidence",
        "config",
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in frontier.parameters.values()
    )
    assert frontier.parameters["config"].default == GCCandidateEvidenceConfig()

    frontier_identity = inspect.signature(make_gc_candidate_frontier_evidence_id)
    assert tuple(frontier_identity.parameters) == (
        "identity_kind",
        "instrument",
        "timeframe",
        "dataset_id",
        "seed_id",
        "canonical_control_digest",
        "frontier_ordinal",
        "source_segment",
        "source_pending_result",
        "receiving_segment",
    )
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in frontier_identity.parameters.values()
    )


def test_case_43_public_dataclasses_are_frozen_with_exact_fields() -> None:
    expected = {
        GCCandidateEvidenceConfig: (
            "equal_liquidity_config",
            "dealing_range_config",
        ),
        GCSegmentCandidateEvidence: (
            "segment_ordinal",
            "segment_id",
            "evidence",
        ),
        GCCandidateEvidenceSegmentResult: (
            "segment_ordinal",
            "segment_id",
            "equal_liquidity_result",
            "dealing_range_result",
            "liquidity_map_result",
            "fair_value_gap_result",
            "inducement_result",
            "kill_zone_result",
            "result_ids",
        ),
        GCCandidateEvidenceManifest: (
            "manifest_id",
            "bundle_id",
            "version",
            "instrument",
            "timeframe",
            "tick_size",
            "dataset_id",
            "calendar_version",
            "timezone_data_version",
            "seed_id",
            "config",
            "detector_versions",
            "segment_result_ids",
            "candidate_references",
        ),
        GCCandidateEvidenceResult: (
            "status",
            "candidates",
            "segment_results",
            "manifest",
            "reasons",
            "blocking_reasons",
        ),
        GCCandidateFrontierSegmentEvidence: (
            "segment_ordinal",
            "segment_id",
            "equal_liquidity_result",
            "dealing_range_result",
            "liquidity_map_result",
            "fair_value_gap_result",
            "result_ids",
        ),
        GCCandidateFrontierEvidence: (
            "frontier_id",
            "version",
            "instrument",
            "timeframe",
            "dataset_id",
            "seed_id",
            "canonical_control_digest",
            "frontier_ordinal",
            "source_segment",
            "source_pending_result",
            "receiving_segment",
        ),
        GCCandidateFrontierEvidenceResult: (
            "status",
            "frontier",
            "reasons",
            "blocking_reasons",
        ),
    }
    for cls, names in expected.items():
        assert is_dataclass(cls)
        assert cls.__dataclass_params__.frozen is True
        assert tuple(item.name for item in fields(cls)) == names


def test_case_44_public_versions_enums_defaults_and_exports() -> None:
    assert GC_CANDIDATE_EVIDENCE_VERSION == "GC-CANDIDATE-EVIDENCE-V1"
    assert GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION == "GC-CANDIDATE-FRONTIER-EVIDENCE-V1"
    assert tuple(item.value for item in GCCandidateEvidenceIdentityKind) == (
        "BUNDLE",
        "MANIFEST",
    )
    assert tuple(item.value for item in GCCandidateFrontierIdentityKind) == ("FRONTIER",)
    assert GCCandidateEvidenceConfig() == GCCandidateEvidenceConfig(
        equal_liquidity_config=EqualLiquidityConfig(2, 2, 3),
        dealing_range_config=DealingRangeConfig(2, 1),
    )
    assert candidate_module._DETECTOR_VERSIONS == _DETECTOR_VERSIONS
    assert candidate_module.__all__ == (
        "GC_CANDIDATE_EVIDENCE_VERSION",
        "GCCandidateEvidenceIdentityKind",
        "GCCandidateEvidenceConfig",
        "GCSegmentCandidateEvidence",
        "GCCandidateEvidenceSegmentResult",
        "GCCandidateEvidenceManifest",
        "GCCandidateEvidenceResult",
        "GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION",
        "GCCandidateFrontierIdentityKind",
        "GCCandidateFrontierSegmentEvidence",
        "GCCandidateFrontierEvidence",
        "GCCandidateFrontierEvidenceResult",
        "make_gc_candidate_evidence_id",
        "make_gc_candidate_frontier_evidence_id",
        "build_gc_candidate_evidence",
        "analyze_gc_candidate_frontier_evidence",
    )


def test_case_49_frontier_missing_context_is_unknown() -> None:
    config, _dataset, _calendars, _seed = _valid_inputs()
    result = analyze_gc_candidate_frontier_evidence(
        dataset_config=config,
        dataset=None,
        calendar_entries=None,
        structural_seed=None,
        canonical_candidate_evidence=None,
    )
    assert result == GCCandidateFrontierEvidenceResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        reasons=("MISSING_TOP_LEVEL_CONTEXT",),
        blocking_reasons=("MISSING_TOP_LEVEL_CONTEXT",),
    )


def test_case_50_frontier_identity_is_deterministic_and_typed() -> None:
    base = GCCandidateFrontierSegmentEvidence(
        2,
        "1" * 64,
        EqualLiquidityResult(SMCV2PrimitiveStatus.NONE),
        DealingRangeResult(SMCV2PrimitiveStatus.NONE),
        LiquidityMapResult(SMCV2PrimitiveStatus.NONE),
        FairValueGapResult(SMCV2PrimitiveStatus.NONE),
        tuple(str(value) * 64 for value in range(2, 6)),
    )
    receiving = replace(base, segment_ordinal=3, segment_id="6" * 64)
    pending = InducementPendingHorizonResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        reasons=("one or more confirmation horizons are incomplete",),
        blocking_reasons=("NEXT_THREE_CLOSED_BARS_INCOMPLETE",),
    )
    kwargs = {
        "identity_kind": GCCandidateFrontierIdentityKind.FRONTIER,
        "instrument": "gc",
        "timeframe": "5m",
        "dataset_id": "7" * 64,
        "seed_id": "8" * 64,
        "canonical_control_digest": "9" * 64,
        "frontier_ordinal": 2,
        "source_segment": base,
        "source_pending_result": pending,
        "receiving_segment": receiving,
    }
    first = make_gc_candidate_frontier_evidence_id(**kwargs)
    assert first == make_gc_candidate_frontier_evidence_id(**kwargs)
    assert len(first) == 64
    with pytest.raises((TypeError, ValueError)):
        make_gc_candidate_frontier_evidence_id(**{**kwargs, "identity_kind": "FRONTIER"})


def test_case_51_frontier_analyzer_derives_one_repeatable_adjacent_pair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, dataset, calendars, seed = _valid_inputs(two_segments=True)
    assert dataset.manifest is not None
    first, source = dataset.segments
    receiving = replace(
        source,
        segment_id="f" * 64,
        first_trade_date=source.first_trade_date + timedelta(days=1),
        last_trade_date=source.last_trade_date + timedelta(days=1),
        bars=tuple(
            replace(bar, timestamp=bar.timestamp + timedelta(days=1))
            for bar in source.bars
        ),
    )
    dataset = replace(
        dataset,
        segments=(first, source, receiving),
        manifest=replace(
            dataset.manifest,
            segment_ids=(first.segment_id, source.segment_id, receiving.segment_id),
        ),
    )
    calendars = calendars + (
        replace(
            calendars[-1],
            trade_date=receiving.first_trade_date,
            session_open_timestamp=calendars[-1].session_open_timestamp
            + timedelta(days=1),
            session_close_timestamp=calendars[-1].session_close_timestamp
            + timedelta(days=1),
        ),
    )
    prefix = GCCandidateEvidenceSegmentResult(
        0,
        first.segment_id,
        EqualLiquidityResult(SMCV2PrimitiveStatus.NONE),
        DealingRangeResult(SMCV2PrimitiveStatus.NONE),
        LiquidityMapResult(SMCV2PrimitiveStatus.NONE),
        FairValueGapResult(SMCV2PrimitiveStatus.NONE),
        InducementResult(SMCV2PrimitiveStatus.NONE),
        KillZoneResult(SMCV2PrimitiveStatus.NONE),
        tuple(str(value) * 64 for value in range(1, 7)),
    )
    control = GCCandidateEvidenceResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        segment_results=(prefix,),
        reasons=("a swept pool has a truncated confirmation horizon",),
        blocking_reasons=("next three closed bars are incomplete",),
    )
    monkeypatch.setattr(candidate_module, "build_gc_candidate_evidence", lambda **_: control)
    monkeypatch.setattr(
        candidate_module,
        "analyze_equal_liquidity",
        lambda **_: EqualLiquidityResult(SMCV2PrimitiveStatus.NONE),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_dealing_ranges",
        lambda **_: DealingRangeResult(SMCV2PrimitiveStatus.NONE),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_liquidity_map",
        lambda **_: LiquidityMapResult(SMCV2PrimitiveStatus.NONE),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_fair_value_gaps",
        lambda **_: FairValueGapResult(SMCV2PrimitiveStatus.NONE),
    )
    horizon = InducementPendingHorizon(
        "a" * 64,
        SMCV2Direction.BULLISH,
        "b" * 64,
        "c" * 64,
        "d" * 64,
        "e" * 64,
        "1" * 64,
        "2" * 64,
        source.bars[-1].index,
        source.bars[-1].timestamp,
        source.bars[-1].low_tick,
        source.bars[-1].close_tick,
        (),
        (),
        3,
        source.bars[-1].index,
        source.bars[-1].timestamp,
        "NEXT_THREE_CLOSED_BARS_INCOMPLETE",
    )
    pending = InducementPendingHorizonResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        (horizon,),
        ("one or more confirmation horizons are incomplete",),
        ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",),
    )
    monkeypatch.setattr(
        candidate_module,
        "analyze_inducement_pending_horizons",
        lambda **_: pending,
    )
    kwargs = {
        "dataset_config": config,
        "dataset": dataset,
        "calendar_entries": calendars,
        "structural_seed": seed,
        "canonical_candidate_evidence": control,
    }
    first_result = analyze_gc_candidate_frontier_evidence(**kwargs)
    second_result = analyze_gc_candidate_frontier_evidence(**kwargs)
    assert first_result == second_result
    assert first_result.status is SMCV2PrimitiveStatus.VALID
    assert first_result.frontier is not None
    assert first_result.frontier.frontier_ordinal == 1
    assert first_result.frontier.source_segment.segment_id == source.segment_id
    assert first_result.frontier.receiving_segment.segment_id == receiving.segment_id
    assert first_result.frontier.source_pending_result == pending
    assert len(first_result.frontier.source_segment.result_ids) == 4


@pytest.mark.parametrize(
    "mutator",
    (
        lambda value: {**value, "identity_kind": "BUNDLE"},
        lambda value: {**value, "tick_size": Decimal("NaN")},
        lambda value: {**value, "config": object()},
        lambda value: {**value, "detector_versions": value["detector_versions"][::-1]},
        lambda value: {**value, "segment_result_ids": list(value["segment_result_ids"])},
        lambda value: {**value, "segment_result_ids": (("1" * 64, ()),)},
        lambda value: {**value, "segment_result_ids": value["segment_result_ids"] * 2},
        lambda value: {**value, "candidate_references": list(value["candidate_references"])},
        lambda value: {**value, "candidate_references": (("f" * 64, "a" * 64),)},
        lambda value: {**value, "candidate_references": value["candidate_references"] * 2},
        lambda value: {**value, "candidate_references": ()},
        lambda value: {**value, "bundle_id": "b" * 64},
    ),
)
def test_case_39_bundle_identity_rejects_malformed_or_forbidden_schema(mutator) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_gc_candidate_evidence_id(**mutator(_identity_kwargs()))


def test_case_40_manifest_requires_exact_recomputed_bundle() -> None:
    kwargs = _identity_kwargs()
    bundle = make_gc_candidate_evidence_id(**kwargs)  # type: ignore[arg-type]
    with pytest.raises((TypeError, ValueError)):
        make_gc_candidate_evidence_id(
            **{
                **kwargs,
                "identity_kind": GCCandidateEvidenceIdentityKind.MANIFEST,
                "bundle_id": "b" * 64,
            }
        )
    manifest = make_gc_candidate_evidence_id(
        **{
            **kwargs,
            "identity_kind": GCCandidateEvidenceIdentityKind.MANIFEST,
            "bundle_id": bundle,
        }
    )
    assert manifest != bundle


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("instrument", "MGC"),
        ("timeframe", "1M"),
        ("tick_size", Decimal("0.2")),
        ("dataset_id", "d" * 64),
        ("calendar_version", "CME-GC-2026-V2"),
        ("timezone_data_version", "2026.1"),
        ("seed_id", "e" * 64),
    ),
)
def test_case_39_bundle_identity_is_sensitive_to_every_common_field(
    field: str,
    replacement: object,
) -> None:
    kwargs = _identity_kwargs()
    baseline = make_gc_candidate_evidence_id(**kwargs)  # type: ignore[arg-type]
    changed = make_gc_candidate_evidence_id(**{**kwargs, field: replacement})
    assert changed != baseline


def test_cases_42_43_exact_annotations_defaults_and_frozen_construction() -> None:
    expected_annotations = {
        GCCandidateEvidenceConfig: {
            "equal_liquidity_config": EqualLiquidityConfig,
            "dealing_range_config": DealingRangeConfig,
        },
        GCSegmentCandidateEvidence: {
            "segment_ordinal": int,
            "segment_id": str,
            "evidence": candidate_module.GCFeatureLabelCandidateEvidence,
        },
        GCCandidateEvidenceResult: {
            "status": SMCV2PrimitiveStatus,
            "candidates": tuple[GCSegmentCandidateEvidence, ...],
            "segment_results": tuple[GCCandidateEvidenceSegmentResult, ...],
            "manifest": GCCandidateEvidenceManifest | None,
            "reasons": tuple[str, ...],
            "blocking_reasons": tuple[str, ...],
        },
    }
    for cls, annotations in expected_annotations.items():
        hints = get_type_hints(cls)
        for name, annotation in annotations.items():
            assert hints[name] == annotation
    result_fields = {item.name: item for item in fields(GCCandidateEvidenceResult)}
    assert result_fields["status"].default is MISSING
    assert result_fields["candidates"].default == ()
    assert result_fields["segment_results"].default == ()
    assert result_fields["manifest"].default is None
    assert result_fields["reasons"].default == ()
    assert result_fields["blocking_reasons"].default == ()


def test_case_48_module_has_no_downstream_training_or_io_authority() -> None:
    source = inspect.getsource(candidate_module)
    forbidden = (
        "build_gc_feature_labels(",
        "open(",
        "Path(",
        "requests.",
        "subprocess",
        "sklearn",
        "torch",
        "tensorflow",
        "place_order",
        "execute_trade",
    )
    assert all(token not in source for token in forbidden)
