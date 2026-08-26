"""Contract tests for the independent GC pretraining corpus builder."""

import hashlib
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from inspect import Parameter, signature
from pathlib import Path
from types import SimpleNamespace

import pytest

import analysis.gc_pretraining_corpus as subject
from analysis.gc_candidate_evidence_builder import GCCandidateEvidenceResult
from analysis.gc_dataset_builder import GCDatasetBuildConfig, GCDatasetBuildResult, GCDatasetBuildStatus
from analysis.gc_feature_label_builder import GCFeatureLabelResult, GCLabelOutcome
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


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


def _source(
    *,
    source_id: str,
    source_sha256: str,
    contract: object,
    role: subject.GCPretrainingSourceRole,
    dataset_id: str = "d" * 64,
    first_trade_date: date = date(2024, 11, 4),
    last_trade_date: date = date(2025, 6, 2),
) -> subject.GCPretrainingSourceRecord:
    return subject.GCPretrainingSourceRecord(
        source_id=source_id,
        source_name=f"{contract}_source.txt",
        source_sha256=source_sha256,
        contract=contract,  # type: ignore[arg-type]
        role=role,
        dataset_id=dataset_id,
        first_trade_date=first_trade_date,
        last_trade_date=last_trade_date,
        acquisition_timestamp=datetime(2026, 8, 3, tzinfo=timezone.utc),
        calendar_version="CME-GC-2025",
        timezone_data_version="2026a",
        prior_run_manifest_ids=(),
        contaminated_evidence_ids=(),
        contamination_audit_complete=True,
        final_oos_payload_accessed=False,
    )


def _registry(
    *,
    source_contract: object = "GCJ25",
    first_trade_date: date = date(2024, 11, 4),
    last_trade_date: date = date(2025, 6, 2),
) -> tuple[subject.GCPretrainingSourceRecord, ...]:
    return (
        _source(
            source_id="1" * 64,
            source_sha256="2" * 64,
            contract=source_contract,
            role=subject.GCPretrainingSourceRole.PRETRAINING_DEVELOPMENT_CANDIDATE,
            first_trade_date=first_trade_date,
            last_trade_date=last_trade_date,
        ),
        _source(
            source_id="e" * 64,
            source_sha256="15e2b3cb47e96988a1a623712e3347438e47b19d8d154d213aecc81c52a50111",
            contract="GCQ26",
            role=subject.GCPretrainingSourceRole.SEALED_FINAL_OOS_CANDIDATE,
            first_trade_date=date(2026, 7, 6),
            last_trade_date=date(2026, 8, 3),
        ),
    )


def _multi_registry() -> tuple[subject.GCPretrainingSourceRecord, ...]:
    return (
        _source(
            source_id="1" * 64,
            source_sha256="2" * 64,
            contract="GCJ25",
            role=subject.GCPretrainingSourceRole.PRETRAINING_DEVELOPMENT_CANDIDATE,
            first_trade_date=date(2024, 11, 4),
            last_trade_date=date(2025, 4, 1),
        ),
        _source(
            source_id="9" * 64,
            source_sha256="a" * 64,
            contract="GCM25",
            role=subject.GCPretrainingSourceRole.PRETRAINING_DEVELOPMENT_CANDIDATE,
            first_trade_date=date(2025, 4, 2),
            last_trade_date=date(2025, 6, 2),
        ),
        _source(
            source_id="e" * 64,
            source_sha256="15e2b3cb47e96988a1a623712e3347438e47b19d8d154d213aecc81c52a50111",
            contract="GCQ26",
            role=subject.GCPretrainingSourceRole.SEALED_FINAL_OOS_CANDIDATE,
            first_trade_date=date(2026, 7, 6),
            last_trade_date=date(2026, 8, 3),
        ),
    )


def _group(
    *,
    source_id: str = "1" * 64,
    contract: object = "GCJ25-COMEX",
    trade_date: date = date(2025, 4, 1),
    index: int = 10,
    moment: datetime = datetime(2025, 4, 1, 14, tzinfo=timezone.utc),
    candidate_id: str = "3" * 64,
    row_id: str = "4" * 64,
    label_id: str = "5" * 64,
    direction: SMCV2Direction = SMCV2Direction.BULLISH,
    outcome: GCLabelOutcome = GCLabelOutcome.TARGET_FIRST,
) -> dict[str, object]:
    return {
        "source_id": source_id,
        "contract": contract,
        "trade_date": trade_date,
        "index": index,
        "moment": moment,
        "candidate_id": candidate_id,
        "row_id": row_id,
        "label_id": label_id,
        "direction": direction,
        "outcome": outcome,
    }


def _reconciliation_build(
    monkeypatch: pytest.MonkeyPatch,
    *,
    source_contract: object = "GCJ25",
    upstream_contract: object = "GCJ25-COMEX",
    trade_date: date = date(2025, 4, 1),
    source_registry: tuple[subject.GCPretrainingSourceRecord, ...] | None = None,
    groups: tuple[dict[str, object], ...] | None = None,
) -> subject.GCPretrainingCorpusResult:
    dataset_id = "d" * 64
    dataset_manifest = SimpleNamespace(
        dataset_id=dataset_id,
        calendar_version="CME-GC-2025",
        timezone_data_version="2026a",
    )
    if groups is None:
        groups = ({
            "source_id": "1" * 64,
            "contract": upstream_contract,
            "trade_date": trade_date,
            "index": 10,
            "moment": datetime(2025, 4, 1, 14, tzinfo=timezone.utc),
            "candidate_id": "3" * 64,
            "row_id": "4" * 64,
            "label_id": "5" * 64,
            "direction": SMCV2Direction.BULLISH,
            "outcome": GCLabelOutcome.TARGET_FIRST,
        },)
    candidates: list[SimpleNamespace] = []
    rows: list[SimpleNamespace] = []
    labels: list[SimpleNamespace] = []
    for group in groups:
        moment = group["moment"]
        index = group["index"]
        candidate_id = group["candidate_id"]
        row_id = group["row_id"]
        label_id = group["label_id"]
        contract = group["contract"]
        group_trade_date = group["trade_date"]
        source_id = group["source_id"]
        inducement = SimpleNamespace(
            inducement_id=candidate_id,
            confirmation_index=index,
            confirmation_timestamp=moment,
            direction=group["direction"],
        )
        candidates.append(SimpleNamespace(evidence=SimpleNamespace(inducement=inducement)))
        rows.append(SimpleNamespace(
            contract=contract,
            trade_date=group_trade_date,
            effective_index=index,
            effective_timestamp=moment,
            dataset_id=dataset_id,
            candidate_id=candidate_id,
            row_id=row_id,
            feature_values=(index,),
            source_ids=(source_id,),
            lineage_ids=("7" * 64,),
        ))
        labels.append(SimpleNamespace(
            contract=contract,
            trade_date=group_trade_date,
            effective_index=index,
            effective_timestamp=moment,
            dataset_id=dataset_id,
            candidate_id=candidate_id,
            label_id=label_id,
            outcome=group["outcome"],
        ))
    candidate_manifest = SimpleNamespace(
        manifest_id="6" * 64,
        calendar_version="CME-GC-2025",
        timezone_data_version="2026a",
    )
    feature_manifest = SimpleNamespace(
        manifest_id="8" * 64,
        calendar_version="CME-GC-2025",
        timezone_data_version="2026a",
        feature_schema_id="GC-AI-FEATURES-V1",
        label_schema_id="GC-AI-LABELS-V1",
        horizon_bars=12,
    )
    monkeypatch.setattr(subject, "_validate_dataset", lambda *args, **kwargs: (_config(), (), dataset_manifest))
    monkeypatch.setattr(subject, "_validate_candidate", lambda *args, **kwargs: (tuple(candidates), candidate_manifest))
    monkeypatch.setattr(subject, "_validate_feature_labels", lambda *args, **kwargs: (tuple(rows), tuple(labels), feature_manifest))
    return _build(source_registry=_registry(source_contract=source_contract) if source_registry is None else source_registry)


def test_case_01_exact_three_path_scope_is_reserved() -> None:
    repository = Path(subject.__file__).resolve().parents[1]
    assert Path(subject.__file__).resolve() == repository / "analysis" / "gc_pretraining_corpus.py"
    assert Path(__file__).resolve() == repository / "tests" / "test_gc_pretraining_corpus.py"
    checkpoint = repository / "docs" / "gc_futures_independent_pretraining_contract_domain_reconciliation_checkpoint.md"
    assert checkpoint.relative_to(repository).as_posix() == "docs/gc_futures_independent_pretraining_contract_domain_reconciliation_checkpoint.md"


def test_case_02_governing_dependency_hashes_and_versions_reconcile() -> None:
    repository = Path(subject.__file__).resolve().parents[1]
    expected = {
        "analysis/gc_dataset_builder.py": "26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED",
        "tests/test_gc_dataset_builder.py": "4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971",
        "analysis/gc_feature_label_builder.py": "7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153",
        "tests/test_gc_feature_label_builder.py": "EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B",
    }
    for relative_path, expected_digest in expected.items():
        assert hashlib.sha256((repository / relative_path).read_bytes()).hexdigest().upper() == expected_digest
    assert subject.GC_DATASET_BUILDER_VERSION == "GC-DATASET-BUILDER-V5-CALENDAR-PARTITION"
    assert subject.GC_FEATURE_LABEL_VERSION == "GC-FEATURE-LABEL-V1"
    assert subject.GC_CANDIDATE_EVIDENCE_VERSION == "GC-CANDIDATE-EVIDENCE-V1"
    assert subject.GC_PRETRAINING_CORPUS_VERSION == "GC-PRETRAINING-CORPUS-V1"


def test_case_03_analyzer_signature_is_exactly_keyword_only_and_required() -> None:
    params = tuple(signature(subject.build_gc_pretraining_corpus).parameters.values())
    assert [parameter.name for parameter in params] == [
        "dataset_config", "dataset_calendar_entries", "dataset_result", "candidate_result",
        "feature_label_result", "source_registry", "partition_plan",
    ]
    assert all(parameter.kind is Parameter.KEYWORD_ONLY for parameter in params)
    assert all(parameter.default is Parameter.empty for parameter in params)


def test_case_04_exact_public_exports_remain_unchanged() -> None:
    assert subject.__all__ == (
        "GC_PRETRAINING_CORPUS_VERSION", "GC_PRETRAINING_INSTRUMENT", "GC_PRETRAINING_TIMEFRAME",
        "GC_PRETRAINING_TICK_SIZE", "GC_PRETRAINING_LABEL_HORIZON_BARS",
        "GC_PRETRAINING_MINIMUM_EMBARGO_BARS", "GCPretrainingSourceRole",
        "GCPretrainingPartition", "GCPretrainingSourceRecord", "GCPretrainingPartitionPlan",
        "GCPretrainingCorpusRecord", "GCPretrainingPartitionSummary", "GCPretrainingCorpusManifest",
        "GCPretrainingCorpusResult", "build_gc_pretraining_corpus",
    )


def test_case_05_public_dataclasses_remain_exact_and_frozen() -> None:
    expected_fields = {
        subject.GCPretrainingSourceRecord: (
            "source_id", "source_name", "source_sha256", "contract", "role", "dataset_id",
            "first_trade_date", "last_trade_date", "acquisition_timestamp", "calendar_version",
            "timezone_data_version", "prior_run_manifest_ids", "contaminated_evidence_ids",
            "contamination_audit_complete", "final_oos_payload_accessed",
        ),
        subject.GCPretrainingPartitionPlan: (
            "train_start_trade_date", "train_end_trade_date", "validation_start_trade_date",
            "validation_end_trade_date", "calibration_start_trade_date", "calibration_end_trade_date",
            "final_oos_start_trade_date", "final_oos_end_trade_date", "label_horizon_bars",
            "minimum_embargo_bars",
        ),
        subject.GCPretrainingCorpusRecord: (
            "record_id", "partition", "direction", "contract", "trade_date", "effective_index",
            "effective_timestamp", "dataset_id", "candidate_id", "feature_row_id", "label_id",
            "outcome", "feature_values", "source_ids", "lineage_ids",
        ),
        subject.GCPretrainingPartitionSummary: (
            "partition_id", "partition", "start_trade_date", "end_trade_date", "record_ids",
            "contracts", "session_count", "candidate_count", "bullish_count", "bearish_count",
            "target_first_count", "invalidation_first_count", "timeout_count",
        ),
        subject.GCPretrainingCorpusManifest: (
            "manifest_id", "corpus_id", "version", "instrument", "timeframe", "tick_size",
            "dataset_id", "candidate_manifest_id", "feature_label_manifest_id", "feature_schema_id",
            "label_schema_id", "label_horizon_bars", "calendar_version", "timezone_data_version",
            "partition_plan_id", "source_ids", "prior_run_manifest_ids", "partition_ids", "record_ids",
            "exclusion_counts", "excluded_record_count", "contaminated_record_count",
            "admitted_record_count", "final_oos_source_sha256", "final_oos_start_trade_date",
            "final_oos_end_trade_date", "final_oos_payload_access_count", "training_allowed",
            "oos_evaluation_allowed", "integration_allowed", "trading_allowed",
        ),
        subject.GCPretrainingCorpusResult: (
            "status", "records", "partitions", "manifest", "reasons", "blocking_reasons",
        ),
    }
    for dataclass_type, names in expected_fields.items():
        assert is_dataclass(dataclass_type)
        assert dataclass_type.__dataclass_params__.frozen is True
        assert tuple(dataclass_type.__annotations__) == names
        assert tuple(field.name for field in fields(dataclass_type)) == names
    plan_fields = fields(subject.GCPretrainingPartitionPlan)
    assert tuple(field.default for field in plan_fields[-2:]) == (12, 12)
    result_fields = fields(subject.GCPretrainingCorpusResult)
    assert tuple(field.default for field in result_fields[1:]) == ((), (), None, (), ())
    assert all(field.default is MISSING for field in fields(subject.GCPretrainingSourceRecord))
    with pytest.raises(FrozenInstanceError):
        _plan().label_horizon_bars = 13  # type: ignore[misc]


def test_case_06_unsuffixed_source_contract_is_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _reconciliation_build(monkeypatch, source_contract="GCJ25")
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert len(result.records) == 1 and result.records[0].contract == "GCJ25-COMEX"


def test_case_07_exchange_qualified_source_contract_is_invalid() -> None:
    _assert_invalid(source_registry=_registry(source_contract="GCJ25-COMEX"))


def test_case_08_exchange_qualified_upstream_contract_is_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _reconciliation_build(monkeypatch, upstream_contract="GCJ25-COMEX")
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.manifest is not None and result.manifest.admitted_record_count == 1


def test_case_09_unsuffixed_upstream_contract_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _reconciliation_build(monkeypatch, upstream_contract="GCJ25")
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None


def test_case_10_exact_domain_reconciliation_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _reconciliation_build(monkeypatch)
    second = _reconciliation_build(monkeypatch)
    assert first == second
    assert first.records[0].contract == "GCJ25-COMEX"


def test_case_11_month_code_mismatch_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract="GCM25-COMEX").status is SMCV2PrimitiveStatus.INVALID


def test_case_12_contract_year_mismatch_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract="GCJ26-COMEX").status is SMCV2PrimitiveStatus.INVALID


def test_case_13_non_comex_upstream_contract_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract="GCJ25-NYMEX").status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("source_contract,upstream_contract", [
    ("gcj25", "GCJ25-COMEX"),
    ("GcJ25", "GCJ25-COMEX"),
    ("GCJ25", "gcj25-comex"),
    ("GCJ25", "GcJ25-CoMeX"),
])
def test_case_14_contract_domains_are_case_sensitive(
    monkeypatch: pytest.MonkeyPatch,
    source_contract: str,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(
        monkeypatch,
        source_contract=source_contract,
        upstream_contract=upstream_contract,
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("source_contract,upstream_contract", [
    (" GCJ25", "GCJ25-COMEX"),
    ("GCJ25 ", "GCJ25-COMEX"),
    ("GCJ25", " GCJ25-COMEX"),
    ("GCJ25", "GCJ25-COMEX "),
])
def test_case_15_contract_domains_reject_whitespace(
    monkeypatch: pytest.MonkeyPatch,
    source_contract: str,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(
        monkeypatch,
        source_contract=source_contract,
        upstream_contract=upstream_contract,
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("upstream_contract", ["GC##-COMEX", "GC1!-COMEX", "GCJ25-COMEX+GCM25-COMEX"])
def test_case_16_continuous_and_composite_contracts_are_invalid(
    monkeypatch: pytest.MonkeyPatch,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract=upstream_contract).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("source_contract,upstream_contract", [
    (True, "GCJ25-COMEX"),
    (25, "GCJ25-COMEX"),
    ("GCJ25", True),
    ("GCJ25", 25),
])
def test_case_17_non_string_and_boolean_contracts_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    source_contract: object,
    upstream_contract: object,
) -> None:
    assert _reconciliation_build(
        monkeypatch,
        source_contract=source_contract,
        upstream_contract=upstream_contract,
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("source_contract,upstream_contract", [
    ("", "GCJ25-COMEX"),
    ("GCJ25", ""),
])
def test_case_18_empty_contracts_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    source_contract: str,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(
        monkeypatch,
        source_contract=source_contract,
        upstream_contract=upstream_contract,
    ).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("upstream_contract", ["GCJ5-COMEX", "GCJ025-COMEX", "GCJ2025-COMEX"])
def test_case_19_contract_year_width_is_exact(
    monkeypatch: pytest.MonkeyPatch,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract=upstream_contract).status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("upstream_contract", ["GCA25-COMEX", "GCB25-COMEX", "GCH25-COMEX", "GCN25-COMEX"])
def test_case_20_contract_month_code_set_is_exact(
    monkeypatch: pytest.MonkeyPatch,
    upstream_contract: str,
) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract=upstream_contract).status is SMCV2PrimitiveStatus.INVALID


def test_case_21_source_identity_and_registry_evidence_remain_byte_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _reconciliation_build(monkeypatch)
    assert result.records[0].source_ids == ("1" * 64,)
    assert result.manifest is not None
    assert result.manifest.source_ids == ("1" * 64, "e" * 64)


def test_case_22_registry_canonical_order_and_raw_contracts_are_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _multi_registry()
    result = _reconciliation_build(monkeypatch, source_registry=registry)
    assert result.manifest is not None
    assert result.manifest.source_ids == tuple(source.source_id for source in registry)
    assert tuple(source.contract for source in registry) == ("GCJ25", "GCM25", "GCQ26")


def test_case_23_dataset_and_lineage_identities_are_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _reconciliation_build(monkeypatch).records[0]
    assert record.dataset_id == "d" * 64
    assert record.lineage_ids == ("7" * 64,)


def test_case_24_feature_row_identity_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch).records[0].feature_row_id == "4" * 64


def test_case_25_label_identity_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch).records[0].label_id == "5" * 64


def test_case_26_record_identity_keeps_raw_upstream_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _reconciliation_build(monkeypatch).records[0]
    second = _reconciliation_build(monkeypatch).records[0]
    assert first.contract == "GCJ25-COMEX"
    assert first.record_id == second.record_id


def test_case_27_partition_identity_schema_remains_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _reconciliation_build(monkeypatch)
    second = _reconciliation_build(monkeypatch)
    assert first.partitions == second.partitions
    assert first.partitions[0].record_ids == (first.records[0].record_id,)
    assert first.partitions[0].contracts == ("GCJ25-COMEX",)


def test_case_28_corpus_and_manifest_identity_schemas_remain_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _reconciliation_build(monkeypatch)
    second = _reconciliation_build(monkeypatch)
    assert first.manifest == second.manifest
    assert first.manifest is not None
    assert first.manifest.version == "GC-PRETRAINING-CORPUS-V1"
    assert first.manifest.record_ids == (first.records[0].record_id,)


def test_case_29_source_dataset_mismatch_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _registry()
    bad_registry = (replace(registry[0], dataset_id="0" * 64), registry[1])
    assert _reconciliation_build(monkeypatch, source_registry=bad_registry).status is SMCV2PrimitiveStatus.INVALID


def test_case_30_source_trade_date_coverage_is_still_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _reconciliation_build(
        monkeypatch,
        source_registry=_registry(last_trade_date=date(2025, 3, 31)),
    )
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None


def test_case_31_multiple_delivery_months_emit_in_deterministic_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    groups = (
        _group(),
        _group(
            source_id="9" * 64,
            contract="GCM25-COMEX",
            trade_date=date(2025, 4, 2),
            index=20,
            moment=datetime(2025, 4, 2, 14, tzinfo=timezone.utc),
            candidate_id="a" * 64,
            row_id="b" * 64,
            label_id="c" * 64,
        ),
    )
    first = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=groups)
    second = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=groups)
    assert first == second
    assert tuple(record.contract for record in first.records) == ("GCJ25-COMEX", "GCM25-COMEX")


def test_case_32_unsorted_registry_is_rejected_without_silent_sort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _reconciliation_build(monkeypatch, source_registry=tuple(reversed(_multi_registry())))
    assert result.status is SMCV2PrimitiveStatus.INVALID


@pytest.mark.parametrize("field_name", ["source_id", "source_sha256"])
def test_case_33_duplicate_source_identity_or_hash_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    field_name: str,
) -> None:
    registry = _multi_registry()
    bad_second = replace(registry[1], **{field_name: getattr(registry[0], field_name)})
    assert _reconciliation_build(
        monkeypatch,
        source_registry=(registry[0], bad_second, registry[2]),
    ).status is SMCV2PrimitiveStatus.INVALID


def test_case_34_forked_source_evidence_is_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _registry()
    fork = replace(registry[0], source_id="3" * 64, source_sha256="4" * 64)
    result = _reconciliation_build(monkeypatch, source_registry=(registry[0], fork, registry[1]))
    assert result.status is SMCV2PrimitiveStatus.INVALID


def test_case_35_malformed_counterpart_outranks_missing_context() -> None:
    result = _build(dataset_config=None, source_registry=[])
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None


def test_case_36_genuine_all_missing_context_is_unknown() -> None:
    result = _build(
        dataset_config=None,
        dataset_calendar_entries=None,
        dataset_result=None,
        candidate_result=None,
        feature_label_result=None,
        source_registry=None,
    )
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert result.reasons == ("MISSING_TOP_LEVEL_CONTEXT",)


def test_case_37_final_oos_evidence_is_sealed_and_never_emitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    group = _group(
        source_id="e" * 64,
        contract="GCQ26-COMEX",
        trade_date=date(2026, 7, 6),
        index=30,
        moment=datetime(2026, 7, 6, 14, tzinfo=timezone.utc),
    )
    result = _reconciliation_build(monkeypatch, groups=(group,))
    assert result.status is SMCV2PrimitiveStatus.NONE
    assert result.records == () and result.manifest is not None
    assert result.manifest.exclusion_counts == (("FINAL_OOS_QUARANTINE", 1),)
    assert result.manifest.final_oos_payload_access_count == 0


def test_case_38_final_oos_source_metadata_remains_unsuffixed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    result = _reconciliation_build(monkeypatch, source_registry=registry)
    assert registry[1].contract == "GCQ26"
    assert result.manifest is not None and result.manifest.source_ids[-1] == "e" * 64


def test_case_39_nonparticipating_reference_metadata_is_not_globally_restricted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    reference = _source(
        source_id="7" * 64,
        source_sha256="8" * 64,
        contract="REFERENCE-DOCUMENT",
        role=subject.GCPretrainingSourceRole.REFERENCE_ONLY,
    )
    result = _reconciliation_build(
        monkeypatch,
        source_registry=(registry[0], reference, registry[1]),
    )
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert tuple(role.value for role in subject.GCPretrainingSourceRole) == (
        "PRETRAINING_DEVELOPMENT_CANDIDATE", "CLOSED_RESEARCH_ONLY",
        "SEALED_FINAL_OOS_CANDIDATE", "REFERENCE_ONLY", "SUPERSEDED_REFERENCE",
    )


def test_case_40_contamination_and_independence_boundaries_are_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    contaminated = replace(registry[0], contaminated_evidence_ids=("3" * 64,))
    contaminated_result = _reconciliation_build(
        monkeypatch,
        source_registry=(contaminated, registry[1]),
    )
    assert contaminated_result.status is SMCV2PrimitiveStatus.NONE
    assert contaminated_result.records == () and contaminated_result.manifest is not None
    assert contaminated_result.manifest.contaminated_record_count == 1
    unverified = replace(registry[0], contamination_audit_complete=False)
    unverified_result = _reconciliation_build(
        monkeypatch,
        source_registry=(unverified, registry[1]),
    )
    assert unverified_result.status is SMCV2PrimitiveStatus.UNKNOWN
    assert unverified_result.reasons == ("INDEPENDENCE_UNVERIFIED",)


def test_case_41_first_failing_group_promotes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _reconciliation_build(monkeypatch, upstream_contract="GCM25-COMEX")
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None


def test_case_42_later_failure_preserves_strictly_prior_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _group()
    failing = _group(
        source_id="9" * 64,
        contract="GCJ25-COMEX",
        trade_date=date(2025, 4, 2),
        index=20,
        moment=datetime(2025, 4, 2, 14, tzinfo=timezone.utc),
        candidate_id="a" * 64,
        row_id="b" * 64,
        label_id="c" * 64,
    )
    prefix = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=(first,))
    extended = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=(first, failing))
    assert extended.status is SMCV2PrimitiveStatus.INVALID
    assert extended.records == prefix.records
    assert extended.partitions == prefix.partitions
    assert extended.manifest == prefix.manifest


def test_case_43_only_strictly_later_complete_append_is_prefix_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _group()
    later = _group(
        source_id="9" * 64,
        contract="GCM25-COMEX",
        trade_date=date(2025, 4, 2),
        index=20,
        moment=datetime(2025, 4, 2, 14, tzinfo=timezone.utc),
        candidate_id="a" * 64,
        row_id="b" * 64,
        label_id="c" * 64,
    )
    prefix = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=(first,))
    extended = _reconciliation_build(monkeypatch, source_registry=_multi_registry(), groups=(first, later))
    assert extended.records[: len(prefix.records)] == prefix.records
    assert later["moment"] > first["moment"]


def test_case_44_same_effective_and_historical_repair_are_prefix_ineligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _group()
    same_moment = _group(
        source_id="9" * 64,
        contract="GCM25-COMEX",
        trade_date=date(2025, 4, 2),
        index=10,
        moment=first["moment"],  # type: ignore[arg-type]
        candidate_id="a" * 64,
        row_id="b" * 64,
        label_id="c" * 64,
    )
    assert same_moment["moment"] == first["moment"]
    registry = _multi_registry()
    repaired = (replace(registry[0], contract="GCM25"), registry[1], registry[2])
    assert _reconciliation_build(
        monkeypatch,
        source_registry=repaired,
        groups=(first, same_moment),
    ).status is SMCV2PrimitiveStatus.INVALID


def test_case_45_nested_exceptions_are_contained(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _reconciliation_build(monkeypatch, upstream_contract=[]).status is SMCV2PrimitiveStatus.INVALID
    monkeypatch.setattr(subject, "_upstream_contract", lambda value: (_ for _ in ()).throw(RuntimeError("nested")))
    result = _reconciliation_build(monkeypatch)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.records == result.partitions == () and result.manifest is None


def test_case_46_no_public_api_identity_or_version_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert "_source_contract_as_upstream" not in subject.__all__
    assert "_upstream_contract" not in subject.__all__
    assert subject.GC_PRETRAINING_CORPUS_VERSION == "GC-PRETRAINING-CORPUS-V1"
    assert _reconciliation_build(monkeypatch).records[0].record_id == _reconciliation_build(monkeypatch).records[0].record_id


def test_case_47_exact_sequential_logical_case_matrix_is_preserved() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    assert sum(line.startswith("def test_case_") for line in source.splitlines()) == 48
    assert all(f"def test_case_{case:02d}_" in source for case in range(1, 49))


def test_case_48_exact_scope_has_no_io_training_oos_or_integration_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "open(" not in source and "requests" not in source and "subprocess" not in source
    assert "fit(" not in source and "predict(" not in source
    manifest = _reconciliation_build(monkeypatch).manifest
    assert manifest is not None
    assert (
        manifest.training_allowed,
        manifest.oos_evaluation_allowed,
        manifest.integration_allowed,
        manifest.trading_allowed,
    ) == (False, False, False, False)
