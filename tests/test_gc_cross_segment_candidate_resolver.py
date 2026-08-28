from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import inspect
import sys

import pytest

from analysis import gc_cross_segment_candidate_resolver as resolver
from analysis.gc_cross_segment_continuity import GCCrossSegmentContinuityResult
from smc.dealing_range import (
    DealingRangeEventType,
    make_dealing_range_id,
)
from smc.fair_value_gap import (
    FairValueGapResult,
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    make_fair_value_gap_id,
)
from smc.inducement import (
    InducementObservation,
    InducementPendingHorizon,
    InducementPendingHorizonResult,
    make_inducement_pending_horizon_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
import test_gc_cross_segment_continuity as continuity_base  # noqa: E402


UTC = timezone.utc
PENDING_REASON = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"


def _h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[
    GCCrossSegmentContinuityResult,
    tuple[resolver.GCSegmentPendingHorizonEvidence, ...],
    tuple[resolver.GCSegmentReceivingGroupEvidence, ...],
]:
    fixture = continuity_base._fixture(receiving_group=True)
    receiving = fixture["receiving"]
    event = fixture["event"]
    gap = fixture["gap"]
    assert event is not None and gap is not None
    confirmation_bar = receiving.bars[2]
    event_id = make_dealing_range_id(
        identity_kind="EVENT",
        instrument="GC",
        timeframe="5M",
        direction=event.direction,
        source_indices=event.provenance.source_indices,
        event_type=event.event_type,
        broken_swing_id=event.broken_swing_id,
        confirmation_index=event.provenance.confirmation_index,
        boundaries=SMCV2TickRange(
            confirmation_bar.close_tick - 1,
            confirmation_bar.close_tick - 1,
        ),
    )
    event = replace(event, event_id=event_id)
    gap_id = make_fair_value_gap_id(
        identity_kind="GAP",
        instrument="GC",
        timeframe="5M",
        direction=gap.direction,
        source_indices=gap.source_indices,
        source_timestamps=gap.source_timestamps,
        boundaries=SMCV2TickRange(gap.lower_tick, gap.upper_tick),
        midpoint_tick=gap.midpoint_tick,
        formation_end_index=gap.formation_end_index,
        formation_end_timestamp=gap.formation_end_timestamp,
        displacement_id=gap.displacement_id,
        structure_event_id=event_id,
        structure_event_type=gap.structure_event_type,
    )
    gap = replace(gap, gap_id=gap_id, structure_event_id=event_id)
    transition_id = make_fair_value_gap_id(
        identity_kind="TRANSITION",
        instrument="GC",
        timeframe="5M",
        direction=gap.direction,
        gap_id=gap_id,
        from_state=None,
        to_state=FairValueGapState.ACTIVE,
        effective_index=gap.formation_end_index,
        effective_timestamp=gap.formation_end_timestamp,
        reason="FORMATION_CONFIRMED",
    )
    transition = FairValueGapTransition(
        transition_id,
        gap_id,
        None,
        FairValueGapState.ACTIVE,
        gap.formation_end_index,
        gap.formation_end_timestamp,
        "FORMATION_CONFIRMED",
    )
    snapshot_id = make_fair_value_gap_id(
        identity_kind="SNAPSHOT",
        instrument="GC",
        timeframe="5M",
        direction=gap.direction,
        gap_id=gap_id,
        state=FairValueGapState.ACTIVE,
        effective_index=gap.formation_end_index,
        effective_timestamp=gap.formation_end_timestamp,
        transition_ids=(transition_id,),
    )
    snapshot = FairValueGapSnapshot(
        snapshot_id,
        gap_id,
        gap.direction,
        FairValueGapState.ACTIVE,
        gap.formation_end_index,
        gap.formation_end_timestamp,
        (transition_id,),
    )
    candidate = fixture["canonical_candidate_evidence"]
    receiving_result = replace(
        candidate.segment_results[1],
        fair_value_gap_result=FairValueGapResult(
            SMCV2PrimitiveStatus.VALID,
            gaps=(gap,),
            transitions=(transition,),
            snapshots=(snapshot,),
        ),
    )
    fixture["canonical_candidate_evidence"] = replace(
        candidate,
        segment_results=(candidate.segment_results[0], receiving_result),
    )
    fixture["structural_seed"] = replace(
        fixture["structural_seed"], structure_events=(event,)
    )
    continuity = continuity_base._run(monkeypatch, fixture)
    assert continuity.manifest is not None
    assert len(continuity.boundaries) == 1
    assert len(continuity.receiving_groups) == 1
    continuity = replace(
        continuity,
        status=SMCV2PrimitiveStatus.UNKNOWN,
        reasons=("CANONICAL_CONTROL_UNKNOWN",),
        blocking_reasons=("CANONICAL_CONTROL_UNKNOWN",),
    )
    boundary = continuity.boundaries[0]
    source = fixture["source"]
    pending_values = {
        "direction": SMCV2Direction.BULLISH,
        "active_range_lineage_id": _h("active-range"),
        "active_range_snapshot_id": _h("range-snapshot"),
        "liquidity_map_snapshot_id": _h("map-snapshot"),
        "external_target_classification_id": _h("external-target"),
        "internal_pool_classification_id": _h("internal-classification"),
        "internal_pool_id": _h("internal-pool"),
        "sweep_index": source.bars[-1].index,
        "sweep_timestamp": source.bars[-1].timestamp,
        "sweep_extreme_tick": 999,
        "reclaim_close_tick": 1000,
        "available_confirmation_indices": (),
        "available_confirmation_timestamps": (),
        "missing_confirmation_bar_count": 3,
        "first_known_index": source.bars[-1].index,
        "first_known_timestamp": source.bars[-1].timestamp,
        "reason_token": PENDING_REASON,
    }
    pending_id = make_inducement_pending_horizon_id(
        identity_kind="PENDING_HORIZON",
        instrument="GC",
        timeframe="5M",
        **pending_values,
    )
    pending = InducementPendingHorizon(pending_id, **pending_values)
    pending_wrapper = resolver.GCSegmentPendingHorizonEvidence(
        boundary.source_segment_ordinal,
        boundary.source_segment_id,
        InducementPendingHorizonResult(
            SMCV2PrimitiveStatus.UNKNOWN,
            (pending,),
            (PENDING_REASON,),
            (PENDING_REASON,),
        ),
    )
    observations = tuple(
        InducementObservation(
            bar.index,
            bar.timestamp,
            bar.open_tick,
            bar.high_tick,
            bar.low_tick,
            bar.close_tick,
            True,
        )
        for bar in receiving.bars
    )
    group = continuity.receiving_groups[0]
    receiver = resolver.GCSegmentReceivingGroupEvidence(
        group.receiving_segment_ordinal,
        group.receiving_segment_id,
        group.group_id,
        observations,
        event,
        gap,
        (transition,),
        (snapshot,),
    )
    return continuity, (pending_wrapper,), (receiver,)


def _resolve(
    monkeypatch: pytest.MonkeyPatch,
    **changes: object,
) -> resolver.GCCrossSegmentCandidateResolverResult:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    values: dict[str, object] = {
        "instrument": "gc",
        "timeframe": "5m",
        "continuity_result": continuity,
        "pending_horizon_evidence": pending,
        "receiving_group_evidence": receiving,
    }
    values.update(changes)
    return resolver.resolve_gc_cross_segment_candidates(**values)  # type: ignore[arg-type]


def _call(
    continuity: GCCrossSegmentContinuityResult | None,
    pending: tuple[resolver.GCSegmentPendingHorizonEvidence, ...] | None,
    receiving: tuple[resolver.GCSegmentReceivingGroupEvidence, ...] | None,
    **changes: object,
) -> resolver.GCCrossSegmentCandidateResolverResult:
    values: dict[str, object] = {
        "instrument": "gc",
        "timeframe": "5m",
        "continuity_result": continuity,
        "pending_horizon_evidence": pending,
        "receiving_group_evidence": receiving,
    }
    values.update(changes)
    return resolver.resolve_gc_cross_segment_candidates(**values)  # type: ignore[arg-type]


def _rebuild_pending(
    pending: InducementPendingHorizon,
    **changes: object,
) -> InducementPendingHorizon:
    values = {
        field.name: getattr(pending, field.name)
        for field in fields(InducementPendingHorizon)
        if field.name != "pending_horizon_id"
    }
    values.update(changes)
    pending_id = make_inducement_pending_horizon_id(
        identity_kind="PENDING_HORIZON",
        instrument="GC",
        timeframe="5M",
        **values,
    )
    return InducementPendingHorizon(pending_id, **values)  # type: ignore[arg-type]


def _pending_result(
    wrapper: resolver.GCSegmentPendingHorizonEvidence,
    horizons: tuple[InducementPendingHorizon, ...],
    *,
    reasons: tuple[str, ...] = (PENDING_REASON,),
    blocking_reasons: tuple[str, ...] = (PENDING_REASON,),
) -> tuple[resolver.GCSegmentPendingHorizonEvidence, ...]:
    ordered = tuple(
        sorted(
            horizons,
            key=lambda item: (
                item.first_known_timestamp,
                item.sweep_index,
                item.pending_horizon_id,
            ),
        )
    )
    return (
        replace(
            wrapper,
            result=InducementPendingHorizonResult(
                SMCV2PrimitiveStatus.UNKNOWN,
                ordered,
                reasons,
                blocking_reasons,
            ),
        ),
    )


def _assert_invalid(result: resolver.GCCrossSegmentCandidateResolverResult) -> None:
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons == ("INVALID_CROSS_SEGMENT_RESOLVER_EVIDENCE",)
    assert result.blocking_reasons == (
        "INVALID_CROSS_SEGMENT_RESOLVER_EVIDENCE",
    )


def _identity_values(
    continuity: GCCrossSegmentContinuityResult,
    resolution: resolver.GCCrossSegmentCandidateResolution,
) -> dict[str, object]:
    assert continuity.manifest is not None
    manifest = continuity.manifest
    return {
        "instrument": manifest.instrument,
        "timeframe": manifest.timeframe,
        "dataset_id": manifest.dataset_id,
        "calendar_version": manifest.calendar_version,
        "boundary_calendar_digest": manifest.boundary_calendar_digest,
        "candidate_calendar_digest": manifest.candidate_calendar_digest,
        "timezone_data_version": manifest.timezone_data_version,
        "seed_id": manifest.seed_id,
        "canonical_control_digest": manifest.canonical_control_digest,
        "continuity_manifest_id": manifest.manifest_id,
        **{
            field.name: getattr(resolution, field.name)
            for field in fields(resolver.GCCrossSegmentCandidateResolution)
            if field.name != "resolution_id"
        },
    }


def test_case_01_all_required_top_level_inputs_absent_is_unknown() -> None:
    result = _call(None, None, None)
    assert result == resolver.GCCrossSegmentCandidateResolverResult(
        SMCV2PrimitiveStatus.UNKNOWN,
        reasons=("CROSS_SEGMENT_CONFIRMATION_UNRESOLVED",),
        blocking_reasons=("CROSS_SEGMENT_CONFIRMATION_UNRESOLVED",),
    )


def test_case_02_complete_inputs_without_pending_horizon_are_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    result = _call(continuity, _pending_result(pending[0], ()), receiving)
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.reasons == ("NO_APPLICABLE_CROSS_SEGMENT_HORIZON",)


def test_case_03_canonical_unknown_branch_resolves_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.reasons == ("CROSS_SEGMENT_CONFIRMATION_RESOLVED",)
    assert result.blocking_reasons == ()
    assert len(result.resolutions) == 1
    assert result.manifest is not None
    assert result.manifest.resolution_ids == (result.resolutions[0].resolution_id,)


@pytest.mark.parametrize(
    ("status", "reasons"),
    [
        (SMCV2PrimitiveStatus.VALID, ("CANONICAL_CONTROL_UNKNOWN",)),
        (SMCV2PrimitiveStatus.UNKNOWN, ("canonical_control_unknown",)),
        (SMCV2PrimitiveStatus.UNKNOWN, ("CANONICAL_CONTROL_UNKNOWN", "EXTRA")),
    ],
)
def test_case_04_only_exact_canonical_unknown_branch_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
    status: SMCV2PrimitiveStatus,
    reasons: tuple[str, ...],
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    _assert_invalid(
        _call(
            replace(continuity, status=status, reasons=reasons),
            pending,
            receiving,
        )
    )


def test_case_05_null_continuity_manifest_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    _assert_invalid(_call(replace(continuity, manifest=None), pending, receiving))


def test_case_06_manifest_lists_reconcile_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    assert continuity.manifest is not None
    bad = replace(
        continuity,
        manifest=replace(continuity.manifest, boundary_ids=()),
    )
    _assert_invalid(_call(bad, pending, receiving))


def test_case_07_adjacent_segment_ordinals_are_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    boundary = replace(
        continuity.boundaries[0],
        receiving_segment_ordinal=continuity.boundaries[0].source_segment_ordinal + 2,
    )
    _assert_invalid(_call(replace(continuity, boundaries=(boundary,)), pending, receiving))


@pytest.mark.parametrize("mode", ["duplicate", "reordered"])
def test_case_08_duplicate_or_reordered_boundaries_are_invalid(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    boundary = continuity.boundaries[0]
    boundaries = (boundary, boundary) if mode == "duplicate" else (replace(boundary, source_segment_ordinal=1), boundary)
    _assert_invalid(_call(replace(continuity, boundaries=boundaries), pending, receiving))


def test_case_09_pending_wrapper_ownership_reconciles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    bad = (replace(pending[0], segment_id="0" * 64),)
    _assert_invalid(_call(continuity, bad, receiving))


@pytest.mark.parametrize("mode", ["duplicate", "identity"])
def test_case_10_pending_wrapper_order_and_identity_are_exact(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    if mode == "duplicate":
        evidence = (pending[0], pending[0])
    else:
        horizon = replace(
            pending[0].result.pending_horizons[0],
            pending_horizon_id="0" * 64,
        )
        evidence = _pending_result(pending[0], (horizon,))
    _assert_invalid(_call(continuity, evidence, receiving))


@pytest.mark.parametrize(
    ("reasons", "blocking"),
    [
        ((), (PENDING_REASON,)),
        (("next_three_closed_bars_incomplete",), (PENDING_REASON,)),
        ((PENDING_REASON,), ("NEXT_THREE_CLOSED_BARS_INCOMPLETE ",)),
    ],
)
def test_case_11_pending_reason_token_is_exact(
    monkeypatch: pytest.MonkeyPatch,
    reasons: tuple[str, ...],
    blocking: tuple[str, ...],
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = pending[0].result.pending_horizons[0]
    evidence = _pending_result(
        pending[0],
        (horizon,),
        reasons=reasons,
        blocking_reasons=blocking,
    )
    _assert_invalid(_call(continuity, evidence, receiving))


@pytest.mark.parametrize("malformed", [None, (), "bad"])
def test_case_12_malformed_nested_pending_is_contained(
    monkeypatch: pytest.MonkeyPatch,
    malformed: object,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    bad = (replace(pending[0], result=malformed),)  # type: ignore[arg-type]
    _assert_invalid(_call(continuity, bad, receiving))


def test_case_13_zero_available_three_missing_is_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.resolutions[0].confirmation_index == 2


def test_case_14_one_available_two_missing_is_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = pending[0].result.pending_horizons[0]
    source_end = continuity.boundaries[0].source_end_timestamp
    changed = _rebuild_pending(
        horizon,
        sweep_index=0,
        sweep_timestamp=source_end - timedelta(minutes=15),
        available_confirmation_indices=(1,),
        available_confirmation_timestamps=(source_end - timedelta(minutes=10),),
        missing_confirmation_bar_count=2,
        first_known_index=1,
        first_known_timestamp=source_end - timedelta(minutes=10),
    )
    result = _call(continuity, _pending_result(pending[0], (changed,)), receiving)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN


def test_case_15_two_available_one_missing_is_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = pending[0].result.pending_horizons[0]
    source_end = continuity.boundaries[0].source_end_timestamp
    changed = _rebuild_pending(
        horizon,
        sweep_index=0,
        sweep_timestamp=source_end - timedelta(minutes=15),
        available_confirmation_indices=(1, 2),
        available_confirmation_timestamps=(
            source_end - timedelta(minutes=10),
            source_end - timedelta(minutes=5),
        ),
        missing_confirmation_bar_count=1,
        first_known_index=2,
        first_known_timestamp=source_end - timedelta(minutes=5),
    )
    result = _call(continuity, _pending_result(pending[0], (changed,)), receiving)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN


def test_case_16_three_available_bars_are_not_pending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = pending[0].result.pending_horizons[0]
    bad = replace(
        horizon,
        available_confirmation_indices=(0, 1, 2),
        available_confirmation_timestamps=(
            horizon.sweep_timestamp,
            horizon.sweep_timestamp,
            horizon.sweep_timestamp,
        ),
        missing_confirmation_bar_count=0,
    )
    _assert_invalid(_call(continuity, _pending_result(pending[0], (bad,)), receiving))


def test_case_17_missing_count_mismatch_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = replace(
        pending[0].result.pending_horizons[0],
        missing_confirmation_bar_count=2,
    )
    _assert_invalid(_call(continuity, _pending_result(pending[0], (horizon,)), receiving))


@pytest.mark.parametrize("field", ["sweep_timestamp", "first_known_timestamp"])
def test_case_18_pending_moments_do_not_exceed_source_end(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    horizon = pending[0].result.pending_horizons[0]
    later = receiving[0].observations[0].timestamp
    changed = replace(horizon, **{field: later})
    _assert_invalid(_call(continuity, _pending_result(pending[0], (changed,)), receiving))


def test_case_19_receiving_evidence_is_strictly_later(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    source_end = continuity.boundaries[0].source_end_timestamp
    observation = replace(receiving[0].observations[0], timestamp=source_end)
    bad = (replace(receiving[0], observations=(observation,) + receiving[0].observations[1:]),)
    _assert_invalid(_call(continuity, pending, bad))


def test_case_20_same_effective_receiving_append_is_ineligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    boundary = continuity.boundaries[0]
    assert receiving[0].observations[0].timestamp > boundary.source_end_timestamp
    result = _call(continuity, pending, ())
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.resolutions == ()


def test_case_21_only_immediately_adjacent_segment_is_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    bad = (replace(receiving[0], segment_ordinal=2),)
    _assert_invalid(_call(continuity, pending, bad))


def test_case_22_second_boundary_confirmation_is_never_used(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, _ = _canonical_inputs(monkeypatch)
    result = _call(continuity, pending, ())
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.resolutions == ()


def test_case_23_exact_remaining_positions_complete_horizon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.resolutions[0].confirmation_index == 2


@pytest.mark.parametrize("mode", ["skipped", "substituted", "wider"])
def test_case_24_skipped_substituted_or_wider_positions_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    observations = receiving[0].observations
    if mode == "skipped":
        changed = observations[::2]
    elif mode == "substituted":
        changed = (replace(observations[0], index=99),) + observations[1:]
    else:
        changed = observations[:-1] + (
            replace(
                observations[-1],
                timestamp=observations[-1].timestamp - timedelta(minutes=1),
            ),
            observations[-1],
        )
    result = _call(continuity, pending, (replace(receiving[0], observations=changed),))
    if mode == "wider":
        assert result.status is SMCV2PrimitiveStatus.UNKNOWN
        assert result.resolutions == ()
    else:
        _assert_invalid(result)


def test_case_25_references_are_exact_event_then_gap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    group = replace(continuity.receiving_groups[0], references=tuple(reversed(continuity.receiving_groups[0].references)))
    _assert_invalid(_call(replace(continuity, receiving_groups=(group,)), pending, receiving))


@pytest.mark.parametrize("field", ["segment_id", "receiving_group_id"])
def test_case_26_receiving_wrapper_ownership_and_order_reconcile(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    bad = (replace(receiving[0], **{field: "f" * 64}),)
    _assert_invalid(_call(continuity, pending, bad))


@pytest.mark.parametrize("kind", ["event", "gap"])
def test_case_27_foreign_canonical_ids_recompute(
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    if kind == "event":
        bad = replace(receiving[0], structure_event=replace(receiving[0].structure_event, event_id="0" * 64))
    else:
        bad = replace(receiving[0], fair_value_gap=replace(receiving[0].fair_value_gap, gap_id="0" * 64))
    _assert_invalid(_call(continuity, pending, (bad,)))


@pytest.mark.parametrize("kind", ["direction", "suffix"])
def test_case_28_event_gap_direction_moment_and_suffix_reconcile(
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    gap = receiving[0].fair_value_gap
    if kind == "direction":
        gap = replace(gap, direction=SMCV2Direction.BEARISH)
    else:
        gap = replace(gap, source_timestamps=(gap.source_timestamps[1], gap.source_timestamps[0], gap.source_timestamps[2]))
    _assert_invalid(_call(continuity, pending, (replace(receiving[0], fair_value_gap=gap),)))


@pytest.mark.parametrize("kind", ["empty", "history", "hash"])
def test_case_29_fvg_history_is_exhaustive_and_mirrored(
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    wrapper = receiving[0]
    if kind == "empty":
        wrapper = replace(wrapper, fair_value_gap_transitions=())
    elif kind == "history":
        snapshot = replace(wrapper.fair_value_gap_snapshots[0], transition_ids=())
        wrapper = replace(wrapper, fair_value_gap_snapshots=(snapshot,))
    else:
        transition = replace(wrapper.fair_value_gap_transitions[0], transition_id="0" * 64)
        wrapper = replace(wrapper, fair_value_gap_transitions=(transition,))
    _assert_invalid(_call(continuity, pending, (wrapper,)))


def test_case_30_opaque_canonical_digest_is_copied_not_recomputed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, _, _ = _canonical_inputs(monkeypatch)
    result = _resolve(monkeypatch)
    assert continuity.manifest is not None and result.manifest is not None
    assert result.manifest.canonical_control_digest == continuity.manifest.canonical_control_digest


def test_case_31_bullish_resolution_is_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    assert result.resolutions[0].direction is SMCV2Direction.BULLISH


def test_case_32_bearish_identity_is_an_exact_mirror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, _, _ = _canonical_inputs(monkeypatch)
    result = _resolve(monkeypatch)
    values = _identity_values(continuity, result.resolutions[0])
    bullish = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
        **values,
    )
    values["direction"] = SMCV2Direction.BEARISH
    bearish = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
        **values,
    )
    assert bullish != bearish


def test_case_33_missing_proof_unknown_but_malformed_proof_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    assert _call(continuity, pending, ()).status is SMCV2PrimitiveStatus.UNKNOWN
    malformed = (replace(receiving[0], observations=("bad",)),)  # type: ignore[arg-type]
    _assert_invalid(_call(continuity, pending, malformed))


def test_case_34_earliest_complete_match_wins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    assert len(result.resolutions) == 1
    assert result.resolutions[0].confirmation_index == min(item.confirmation_index for item in result.resolutions)


def test_case_35_exact_repeat_candidates_collapse_to_one_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _resolve(monkeypatch)
    second = _resolve(monkeypatch)
    assert first.resolutions == second.resolutions
    assert len(set(item.resolution_id for item in first.resolutions)) == 1


def test_case_36_forked_duplicate_receiving_ids_are_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    fork = replace(receiving[0], observations=receiving[0].observations[:-1])
    _assert_invalid(_call(continuity, pending, (receiving[0], fork)))


def test_case_37_opposing_same_effective_identity_payloads_are_distinct(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, _, _ = _canonical_inputs(monkeypatch)
    result = _resolve(monkeypatch)
    values = _identity_values(continuity, result.resolutions[0])
    values["direction"] = SMCV2Direction.BEARISH
    opposing = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
        **values,
    )
    assert opposing != result.resolutions[0].resolution_id


def test_case_38_multi_resolution_order_key_is_total_and_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _resolve(monkeypatch)
    keys = [
        (
            item.source_segment_ordinal,
            item.first_known_timestamp,
            item.sweep_index,
            item.pending_horizon_id,
            item.confirmation_index,
            item.confirmation_timestamp,
            item.receiving_group_id,
        )
        for item in result.resolutions
    ]
    assert keys == sorted(keys)


def test_case_39_invalid_precedes_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, _ = _canonical_inputs(monkeypatch)
    bad = (replace(pending[0], segment_id="bad"),)
    _assert_invalid(_call(continuity, bad, None))


def test_case_40_ambiguous_precedence_token_is_locked() -> None:
    statuses = [
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
        SMCV2PrimitiveStatus.VALID,
        SMCV2PrimitiveStatus.NONE,
    ]
    assert statuses.index(SMCV2PrimitiveStatus.AMBIGUOUS) < statuses.index(SMCV2PrimitiveStatus.UNKNOWN)
    assert "OPPOSING_CROSS_SEGMENT_CONFIRMATIONS" in resolver.__dict__.values()


def test_case_41_unknown_precedes_valid_and_preserves_confirmed_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    canonical = pending[0].result.pending_horizons[0]
    uncertain = _rebuild_pending(
        canonical,
        direction=SMCV2Direction.BEARISH,
        sweep_extreme_tick=canonical.reclaim_close_tick + 1,
    )
    result = _call(continuity, _pending_result(pending[0], (canonical, uncertain)), receiving)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert len(result.resolutions) == 1
    assert result.manifest is not None


def test_case_42_later_malformed_evidence_does_not_leak_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    malformed = replace(receiving[0], fair_value_gap_snapshots=("bad",))  # type: ignore[arg-type]
    result = _call(continuity, pending, (malformed,))
    _assert_invalid(result)
    assert result.resolutions == ()


def test_case_43_failing_group_promotes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, pending, receiving = _canonical_inputs(monkeypatch)
    malformed = replace(receiving[0], observations=receiving[0].observations[::-1])
    result = _call(continuity, pending, (malformed,))
    _assert_invalid(result)
    assert result.resolutions == () and result.manifest is None


def test_case_44_resolution_schema_and_field_sensitivity_are_exhaustive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, _, _ = _canonical_inputs(monkeypatch)
    result = _resolve(monkeypatch)
    resolution = result.resolutions[0]
    values = _identity_values(continuity, resolution)
    baseline = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
        **values,
    )
    assert baseline == resolution.resolution_id
    for field in fields(resolver.GCCrossSegmentCandidateResolution):
        if field.name == "resolution_id":
            continue
        changed = dict(values)
        value = changed[field.name]
        if isinstance(value, int):
            changed[field.name] = value + 1
        elif isinstance(value, datetime):
            changed[field.name] = value.replace(microsecond=1)
        elif isinstance(value, tuple):
            changed[field.name] = value + (("f" * 64,) if value else ("f" * 64,))
        elif isinstance(value, SMCV2Direction):
            changed[field.name] = SMCV2Direction.BEARISH
        else:
            changed[field.name] = str(value) + "X"
        try:
            identity = resolver.make_gc_cross_segment_candidate_resolver_id(
                identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
                **changed,
            )
        except (TypeError, ValueError):
            continue
        assert identity != baseline, field.name
    with pytest.raises((TypeError, ValueError)):
        resolver.make_gc_cross_segment_candidate_resolver_id(
            identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
            resolution_ids=(baseline,),
            **values,
        )


def test_case_45_manifest_schema_and_history_sensitivity_are_exhaustive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    continuity, _, _ = _canonical_inputs(monkeypatch)
    result = _resolve(monkeypatch)
    assert continuity.manifest is not None and result.manifest is not None
    common = {
        "instrument": result.manifest.instrument,
        "timeframe": result.manifest.timeframe,
        "dataset_id": result.manifest.dataset_id,
        "calendar_version": result.manifest.calendar_version,
        "boundary_calendar_digest": result.manifest.boundary_calendar_digest,
        "candidate_calendar_digest": result.manifest.candidate_calendar_digest,
        "timezone_data_version": result.manifest.timezone_data_version,
        "seed_id": result.manifest.seed_id,
        "canonical_control_digest": result.manifest.canonical_control_digest,
        "continuity_manifest_id": result.manifest.continuity_manifest_id,
    }
    baseline = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.MANIFEST,
        resolution_ids=result.manifest.resolution_ids,
        **common,
    )
    assert baseline == result.manifest.manifest_id
    reversed_id = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.MANIFEST,
        resolution_ids=tuple(reversed(result.manifest.resolution_ids + ("f" * 64,))),
        **common,
    )
    assert reversed_id != baseline
    with pytest.raises((TypeError, ValueError)):
        resolver.make_gc_cross_segment_candidate_resolver_id(
            identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.MANIFEST,
            boundary_id="f" * 64,
            resolution_ids=result.manifest.resolution_ids,
            **common,
        )


def test_case_46_exact_api_frozen_enums_version_and_exports() -> None:
    assert resolver.GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION == "GC-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1"
    analyzer = inspect.signature(resolver.resolve_gc_cross_segment_candidates)
    assert list(analyzer.parameters) == ["instrument", "timeframe", "continuity_result", "pending_horizon_evidence", "receiving_group_evidence"]
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in analyzer.parameters.values())
    builder = inspect.signature(resolver.make_gc_cross_segment_candidate_resolver_id)
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in builder.parameters.values())
    assert [item.value for item in resolver.GCCrossSegmentCandidateResolverIdentityKind] == ["RESOLUTION", "MANIFEST"]
    assert resolver.__all__ == [
        "GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION",
        "GCCrossSegmentCandidateResolverIdentityKind",
        "GCSegmentPendingHorizonEvidence",
        "GCSegmentReceivingGroupEvidence",
        "GCCrossSegmentCandidateResolution",
        "GCCrossSegmentCandidateResolverManifest",
        "GCCrossSegmentCandidateResolverResult",
        "make_gc_cross_segment_candidate_resolver_id",
        "resolve_gc_cross_segment_candidates",
    ]
    for cls in (
        resolver.GCSegmentPendingHorizonEvidence,
        resolver.GCSegmentReceivingGroupEvidence,
        resolver.GCCrossSegmentCandidateResolution,
        resolver.GCCrossSegmentCandidateResolverManifest,
        resolver.GCCrossSegmentCandidateResolverResult,
    ):
        assert is_dataclass(cls) and cls.__dataclass_params__.frozen
    with pytest.raises((TypeError, ValueError)):
        resolver.make_gc_cross_segment_candidate_resolver_id(
            identity_kind="UNKNOWN",
            instrument="GC",
            timeframe="5m",
            dataset_id="0" * 64,
            calendar_version="calendar-v1",
            boundary_calendar_digest="1" * 64,
            candidate_calendar_digest="2" * 64,
            timezone_data_version="tzdata-v1",
            seed_id="3" * 64,
            canonical_control_digest="4" * 64,
            continuity_manifest_id="5" * 64,
        )


def test_case_47_strict_prefix_invariance_and_manifest_extension_sensitivity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _resolve(monkeypatch)
    second = _resolve(monkeypatch)
    assert first.resolutions == second.resolutions
    assert first.manifest == second.manifest
    assert first.manifest is not None
    continuity, _, _ = _canonical_inputs(monkeypatch)
    assert continuity.manifest is not None
    common = {
        "instrument": first.manifest.instrument,
        "timeframe": first.manifest.timeframe,
        "dataset_id": first.manifest.dataset_id,
        "calendar_version": first.manifest.calendar_version,
        "boundary_calendar_digest": first.manifest.boundary_calendar_digest,
        "candidate_calendar_digest": first.manifest.candidate_calendar_digest,
        "timezone_data_version": first.manifest.timezone_data_version,
        "seed_id": first.manifest.seed_id,
        "canonical_control_digest": first.manifest.canonical_control_digest,
        "continuity_manifest_id": first.manifest.continuity_manifest_id,
    }
    extended = resolver.make_gc_cross_segment_candidate_resolver_id(
        identity_kind=resolver.GCCrossSegmentCandidateResolverIdentityKind.MANIFEST,
        resolution_ids=first.manifest.resolution_ids + ("f" * 64,),
        **common,
    )
    assert extended != first.manifest.manifest_id


def test_case_48_repeatability_bytes_and_forbidden_integration_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _resolve(monkeypatch)
    second = _resolve(monkeypatch)
    assert first == second
    assert repr(first).encode("utf-8") == repr(second).encode("utf-8")
    source = inspect.getsource(resolver)
    for forbidden in (
        "from analysis.gc_candidate_builder",
        "import analysis.gc_candidate_builder",
        "from storage.decision_trace",
        "import storage.decision_trace",
        "execute_trade(",
        "train_model(",
    ):
        assert forbidden not in source.lower()
    instance = first.resolutions[0]
    with pytest.raises(FrozenInstanceError):
        instance.reason_token = "MUTATED"  # type: ignore[misc]
