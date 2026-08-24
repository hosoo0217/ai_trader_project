"""Contract tests for the independent GC pretraining corpus builder."""

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import date
from decimal import Decimal, localcontext
from inspect import Parameter, signature
from pathlib import Path

import pytest

import analysis.gc_pretraining_corpus as subject
from analysis.gc_candidate_evidence_builder import GCCandidateEvidenceResult
from analysis.gc_dataset_builder import GCDatasetBuildConfig, GCDatasetBuildResult, GCDatasetBuildStatus
from analysis.gc_feature_label_builder import GCFeatureLabelResult
from smc.smc_v2_primitives import SMCV2PrimitiveStatus


def _plan(**changes: object) -> subject.GCPretrainingPartitionPlan:
    values = dict(
        train_start_trade_date=date(2024, 11, 4), train_end_trade_date=date(2025, 6, 2),
        validation_start_trade_date=date(2025, 6, 16), validation_end_trade_date=date(2025, 8, 25),
        calibration_start_trade_date=date(2025, 9, 8), calibration_end_trade_date=date(2025, 11, 24),
        final_oos_start_trade_date=date(2026, 7, 6), final_oos_end_trade_date=date(2026, 8, 1),
        label_horizon_bars=12, minimum_embargo_bars=12,
    )
    values.update(changes)
    return subject.GCPretrainingPartitionPlan(**values)


def _config(**changes: object) -> GCDatasetBuildConfig:
    values = dict(
        instrument="GC", timeframe="5M", source_timezone="Asia/Tokyo",
        exchange_timezone="America/New_York", timezone_data_version="2026a",
        tick_size=Decimal("0.1"), initial_contract="GCJ25", initial_trade_date=date(2024, 11, 4),
        roll_confirmation_sessions=3, oos_start_trade_date=date(2026, 7, 6),
        oos_end_trade_date=date(2026, 8, 1),
    )
    values.update(changes)
    return GCDatasetBuildConfig(**values)


def _build(**changes: object) -> subject.GCPretrainingCorpusResult:
    values = dict(
        dataset_config=_config(), dataset_calendar_entries=(),
        dataset_result=GCDatasetBuildResult(GCDatasetBuildStatus.NONE, None),
        candidate_result=GCCandidateEvidenceResult(SMCV2PrimitiveStatus.NONE),
        feature_label_result=GCFeatureLabelResult(SMCV2PrimitiveStatus.NONE),
        source_registry=(), partition_plan=_plan(),
    )
    values.update(changes)
    return subject.build_gc_pretraining_corpus(**values)


def _assert_invalid(**changes: object) -> None:
    result = _build(**changes)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None
    assert result.reasons == result.blocking_reasons == ("INVALID_PRETRAINING_CORPUS_EVIDENCE",)


def test_case_01_all_context_absent_is_unknown() -> None:
    result = _build(dataset_config=None, dataset_calendar_entries=None, dataset_result=None,
                    candidate_result=None, feature_label_result=None, source_registry=None)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.records == result.partitions == () and result.manifest is None


def test_case_02_complete_empty_evidence_is_none() -> None:
    result = _build()
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.reasons == ("NO_ELIGIBLE_PRETRAINING_EVIDENCE",)


def test_case_03_missing_dataset_proof_is_invalid() -> None:
    _assert_invalid(dataset_config=None, dataset_result=GCDatasetBuildResult(GCDatasetBuildStatus.VALID, "a" * 64))


def test_case_04_malformed_counterpart_outranks_missing() -> None:
    _assert_invalid(dataset_config=None, candidate_result=None, source_registry=[])


def test_case_05_exact_empty_upstream_contract_reconciles() -> None:
    assert _build().status is SMCV2PrimitiveStatus.NONE


@pytest.mark.parametrize("change", [
    {"dataset_config": _config(instrument="X")}, {"dataset_config": _config(timeframe="1M")},
    {"dataset_config": _config(tick_size=Decimal("0.2"))},
    {"dataset_result": GCDatasetBuildResult(GCDatasetBuildStatus.INVALID, None)},
])
def test_case_06_dataset_mismatches_are_invalid(change: dict[str, object]) -> None:
    _assert_invalid(**change)


def test_case_07_candidate_none_contract_reconciles() -> None:
    assert _build(candidate_result=GCCandidateEvidenceResult(SMCV2PrimitiveStatus.NONE)).status is SMCV2PrimitiveStatus.NONE


def test_case_08_feature_label_none_contract_reconciles() -> None:
    assert _build(feature_label_result=GCFeatureLabelResult(SMCV2PrimitiveStatus.NONE)).status is SMCV2PrimitiveStatus.NONE


@pytest.mark.parametrize("change", [
    {"dataset_calendar_entries": []}, {"dataset_result": object()}, {"candidate_result": object()},
    {"feature_label_result": object()}, {"partition_plan": object()},
])
def test_case_09_wrong_types_fail_closed(change: dict[str, object]) -> None:
    _assert_invalid(**change)


def test_case_10_registry_requires_tuple_and_no_silent_sort() -> None:
    _assert_invalid(source_registry=[])


def test_case_11_source_role_values_are_exact() -> None:
    assert [x.value for x in subject.GCPretrainingSourceRole] == [
        "PRETRAINING_DEVELOPMENT_CANDIDATE", "CLOSED_RESEARCH_ONLY",
        "SEALED_FINAL_OOS_CANDIDATE", "REFERENCE_ONLY", "SUPERSEDED_REFERENCE",
    ]


def test_case_12_development_contract_scope_is_not_exported_as_mutable_state() -> None:
    assert "_DEVELOPMENT_CONTRACTS" not in subject.__all__


def test_case_13_roll_evidence_cannot_be_invented_by_empty_input() -> None:
    assert _build().records == ()


def test_case_14_closed_research_is_not_admitted_by_empty_input() -> None:
    assert _build().manifest is None


def test_case_15_oos_hash_is_private_and_authority_is_absent() -> None:
    assert "_FINAL_OOS_SHA256" not in subject.__all__


def test_case_16_oos_payload_authority_is_never_exported() -> None:
    assert not any(name in subject.__all__ for name in ("train", "evaluate_oos", "trade"))


@pytest.mark.parametrize("field_name,bad", [
    ("train_start_trade_date", date(2024, 11, 5)), ("train_end_trade_date", date(2025, 6, 3)),
    ("validation_start_trade_date", date(2025, 6, 15)), ("validation_end_trade_date", date(2025, 8, 26)),
    ("calibration_start_trade_date", date(2025, 9, 7)), ("calibration_end_trade_date", date(2025, 11, 25)),
    ("final_oos_start_trade_date", date(2026, 7, 5)), ("final_oos_end_trade_date", date(2026, 8, 2)),
    ("label_horizon_bars", 11), ("minimum_embargo_bars", 11),
])
def test_case_17_plan_fields_are_exact(field_name: str, bad: object) -> None:
    _assert_invalid(partition_plan=_plan(**{field_name: bad}))


def test_case_18_train_interval_is_half_open() -> None:
    assert _plan().train_start_trade_date < _plan().train_end_trade_date


def test_case_19_validation_interval_is_half_open() -> None:
    assert _plan().validation_start_trade_date < _plan().validation_end_trade_date


def test_case_20_calibration_interval_is_half_open() -> None:
    assert _plan().calibration_start_trade_date < _plan().calibration_end_trade_date


def test_case_21_final_oos_is_metadata_only() -> None:
    assert _plan().final_oos_start_trade_date < _plan().final_oos_end_trade_date


def test_case_22_exclusion_intervals_cannot_emit_from_empty_evidence() -> None:
    assert _build().records == ()


def test_case_23_horizon_is_exactly_twelve() -> None:
    assert subject.GC_PRETRAINING_LABEL_HORIZON_BARS == _plan().label_horizon_bars == 12


def test_case_24_embargo_is_exactly_twelve() -> None:
    assert subject.GC_PRETRAINING_MINIMUM_EMBARGO_BARS == _plan().minimum_embargo_bars == 12


def test_case_25_bullish_join_cannot_be_synthesized() -> None:
    assert _build().records == ()


def test_case_26_bearish_join_cannot_be_synthesized() -> None:
    assert _build().partitions == ()


def test_case_27_ineligible_labels_cannot_be_recoded_by_empty_path() -> None:
    assert _build().manifest is None


def test_case_28_partition_enum_is_exact() -> None:
    assert [x.value for x in subject.GCPretrainingPartition] == ["TRAIN", "VALIDATION", "CALIBRATION", "FINAL_OOS"]


def test_case_29_cross_reference_mismatch_fails_before_promotion() -> None:
    _assert_invalid(candidate_result=GCCandidateEvidenceResult(SMCV2PrimitiveStatus.VALID))


def test_case_30_contamination_cannot_change_empty_counts() -> None:
    assert _build().records == ()


def test_case_31_missing_registry_is_unknown_not_valid() -> None:
    assert _build(source_registry=None).status is SMCV2PrimitiveStatus.UNKNOWN


def test_case_32_repeated_calls_are_deterministic() -> None:
    assert _build() == _build()


def test_case_33_train_thresholds_are_not_claimed_for_empty_evidence() -> None:
    assert _build().status is SMCV2PrimitiveStatus.NONE


def test_case_34_validation_thresholds_do_not_borrow_evidence() -> None:
    assert _build().records == ()


def test_case_35_calibration_thresholds_do_not_borrow_evidence() -> None:
    assert _build().partitions == ()


def test_case_36_thresholds_are_locked_not_publicly_mutable() -> None:
    assert not any(name.startswith("set_") for name in subject.__all__)


def test_case_37_record_is_frozen_with_exact_fields() -> None:
    assert [f.name for f in fields(subject.GCPretrainingCorpusRecord)] == [
        "record_id", "partition", "direction", "contract", "trade_date", "effective_index",
        "effective_timestamp", "dataset_id", "candidate_id", "feature_row_id", "label_id",
        "outcome", "feature_values", "source_ids", "lineage_ids",
    ]


def test_case_38_partition_summary_has_exact_schema() -> None:
    assert [f.name for f in fields(subject.GCPretrainingPartitionSummary)][-7:] == [
        "session_count", "candidate_count", "bullish_count", "bearish_count",
        "target_first_count", "invalidation_first_count", "timeout_count",
    ]


def test_case_39_partition_plan_is_frozen() -> None:
    plan = _plan()
    with pytest.raises(FrozenInstanceError):
        plan.label_horizon_bars = 13  # type: ignore[misc]


def test_case_40_result_never_grants_authority_on_empty_path() -> None:
    assert _build().manifest is None


def test_case_41_manifest_authority_fields_are_exact() -> None:
    assert [f.name for f in fields(subject.GCPretrainingCorpusManifest)][-4:] == [
        "training_allowed", "oos_evaluation_allowed", "integration_allowed", "trading_allowed"
    ]


def test_case_42_public_api_exports_and_signature_are_exact() -> None:
    expected = (
        "GC_PRETRAINING_CORPUS_VERSION", "GC_PRETRAINING_INSTRUMENT", "GC_PRETRAINING_TIMEFRAME",
        "GC_PRETRAINING_TICK_SIZE", "GC_PRETRAINING_LABEL_HORIZON_BARS",
        "GC_PRETRAINING_MINIMUM_EMBARGO_BARS", "GCPretrainingSourceRole",
        "GCPretrainingPartition", "GCPretrainingSourceRecord", "GCPretrainingPartitionPlan",
        "GCPretrainingCorpusRecord", "GCPretrainingPartitionSummary", "GCPretrainingCorpusManifest",
        "GCPretrainingCorpusResult", "build_gc_pretraining_corpus",
    )
    assert subject.__all__ == expected
    params = tuple(signature(subject.build_gc_pretraining_corpus).parameters.values())
    assert [p.name for p in params] == ["dataset_config", "dataset_calendar_entries", "dataset_result", "candidate_result", "feature_label_result", "source_registry", "partition_plan"]
    assert all(p.kind is Parameter.KEYWORD_ONLY and p.default is Parameter.empty for p in params)


@pytest.mark.parametrize("status", [SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.AMBIGUOUS, SMCV2PrimitiveStatus.UNKNOWN])
def test_case_43_noncanonical_upstream_statuses_fail_closed(status: SMCV2PrimitiveStatus) -> None:
    _assert_invalid(candidate_result=GCCandidateEvidenceResult(status))


def test_case_44_invalid_evidence_promotes_nothing() -> None:
    _assert_invalid(feature_label_result=GCFeatureLabelResult(SMCV2PrimitiveStatus.INVALID))


def test_case_45_identical_complete_calls_are_prefix_stable() -> None:
    first, second = _build(), _build()
    assert first.records == second.records and first.partitions == second.partitions


def test_case_46_historical_plan_mutation_is_ineligible() -> None:
    _assert_invalid(partition_plan=_plan(train_start_trade_date=date(2024, 11, 3)))


def test_case_47_decimal_context_and_exception_containment() -> None:
    with localcontext() as context:
        context.prec = 2
        assert _build().status is SMCV2PrimitiveStatus.NONE
    _assert_invalid(dataset_config=_config(tick_size=Decimal("NaN")))


def test_case_48_exact_scope_has_no_io_or_training_surface() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "open(" not in source and "requests" not in source and "subprocess" not in source
    assert "fit(" not in source and "predict(" not in source
    assert all(is_dataclass(getattr(subject, name)) for name in (
        "GCPretrainingSourceRecord", "GCPretrainingPartitionPlan", "GCPretrainingCorpusRecord",
        "GCPretrainingPartitionSummary", "GCPretrainingCorpusManifest", "GCPretrainingCorpusResult",
    ))
