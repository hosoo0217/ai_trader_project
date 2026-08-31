from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import inspect
from pathlib import Path

import pytest

import analysis.gc_prospective_acquisition_manifest as acquisition
from analysis.gc_prospective_acquisition_manifest import (
    GCProspectiveAcquisitionConfig,
    GCProspectiveAcquisitionManifest,
    GCProspectiveAcquisitionSourceRecord,
    GCProspectiveAcquisitionSourceRole,
    GCProspectiveCalendarEvidenceRecord,
    GCProspectiveContaminationRecord,
    GCProspectiveContractRosterRecord,
    GCProspectiveProviderLogRecord,
    make_gc_prospective_acquisition_id,
    validate_gc_prospective_acquisition_manifest,
)
from smc.smc_v2_primitives import SMCV2PrimitiveStatus


UTC = timezone.utc
MISSING = object()
GOVERNING_HASHES = (
    ("prospective_acquisition_manifest_schedule_proposal", "fa4af7ddd77d5e75ae82988aebd5fe98a55b514c2d063c8012ad95ca4335f3b5"),
    ("prospective_acquisition_first_decision", "966521b3fd0e945c8b5dc524fce2752324d4ec968e4e09c10284851cf3e8455b"),
    ("post_resolver_pretraining_readiness_decision", "f344b32a9b3b923ec79f4f96519501d93bf00e4f67eda1012c8f382991366296"),
    ("terminal_cross_segment_resolver_outcome", "107df12717c0afc60ba89d1721c02a77e1bd2631bb3c19fa5ffbeef7330eb67d"),
    ("gc_ai_strategy_and_training_decision", "237655d31c54133e6e3ae49db59cd3ec32d5b5d3fc436ee476fa00dcd4629688"),
)


def _hash(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def _identity(kind: str, value: object, omitted: str) -> str:
    return make_gc_prospective_acquisition_id(
        kind,
        {field.name: getattr(value, field.name) for field in fields(value) if field.name != omitted},
    )


def _config() -> GCProspectiveAcquisitionConfig:
    return GCProspectiveAcquisitionConfig(
        decision_timestamp=datetime(2026, 8, 31, 8, 17, 34, tzinfo=UTC),
        cohort_start_trade_date=date(2026, 9, 1),
        cohort_end_trade_date=date(2027, 3, 1),
        capture_window_start_timestamp=datetime(2027, 3, 2, tzinfo=UTC),
        capture_window_end_timestamp=datetime(2027, 3, 9, tzinfo=UTC),
        provider="SIERRA_CHART_HISTORICAL_INTRADAY_DATA",
        instrument="GC",
        venue="COMEX",
        timeframe="5M",
        storage_time_unit="1 Tick",
        maximum_historical_days_to_download=220,
        chart_timezone="Asia/Tokyo",
        exchange_timezone="America/New_York",
        timezone_data_version="tzdata-2026a",
        governing_proposal_sha256=GOVERNING_HASHES[0][1],
    )


def _roster_record(contract: str, role: GCProspectiveAcquisitionSourceRole, order: int) -> GCProspectiveContractRosterRecord:
    value = GCProspectiveContractRosterRecord(
        roster_record_id="pending",
        contract=contract,
        role=role,
        delivery_order=order,
        listing_source_id=f"LISTING-{contract}",
        listing_source_sha256=_hash(f"listing-{contract}"),
        inclusion_reason=f"LOCKED_{role.value}",
    )
    return replace(value, roster_record_id=_identity("ROSTER", value, "roster_record_id"))


def _roster() -> tuple[GCProspectiveContractRosterRecord, ...]:
    base = 2026 * 6
    return (
        _roster_record("GCQ26-COMEX", GCProspectiveAcquisitionSourceRole.PREDECESSOR_CONTEXT, base + 3),
        _roster_record("GCV26-COMEX", GCProspectiveAcquisitionSourceRole.COHORT_CANDIDATE, base + 4),
        _roster_record("GCZ26-COMEX", GCProspectiveAcquisitionSourceRole.SUCCESSOR_CONTEXT, base + 5),
    )


def _calendar() -> tuple[GCProspectiveCalendarEvidenceRecord, ...]:
    value = GCProspectiveCalendarEvidenceRecord(
        calendar_evidence_id="pending",
        calendar_version="CME-GC-2026-2027-V1",
        source_kind="CME_STRUCTURED_TRADING_HOURS",
        source_reference="CME_PUBLIC_SYNTHETIC_REFERENCE",
        source_sha256=_hash("calendar-source"),
        retrieval_timestamp=datetime(2027, 3, 2, 1, tzinfo=UTC),
        first_trade_date=date(2026, 8, 1),
        last_trade_date=date(2027, 3, 15),
        exchange_timezone="America/New_York",
        normalized_row_digest=_hash("calendar-rows"),
        authoritative=True,
    )
    return (replace(value, calendar_evidence_id=_identity("CALENDAR", value, "calendar_evidence_id")),)


def _provider_log(contract: str, first: datetime, last: datetime, count: int) -> GCProspectiveProviderLogRecord:
    value = GCProspectiveProviderLogRecord(
        provider_log_id="pending",
        provider="SIERRA_CHART_HISTORICAL_INTRADAY_DATA",
        contract=contract,
        requested_start_timestamp=first - timedelta(days=1),
        requested_end_timestamp=last + timedelta(minutes=5),
        received_start_timestamp=first,
        received_end_timestamp=last,
        received_record_count=count,
        completion_timestamp=datetime(2027, 3, 3, 2, tzinfo=UTC),
        completion_status="COMPLETE",
        log_artifact_sha256=_hash(f"provider-log-{contract}"),
    )
    return replace(value, provider_log_id=_identity("PROVIDER_LOG", value, "provider_log_id"))


def _source(
    roster: GCProspectiveContractRosterRecord,
    calendar_id: str,
    first_trade_date: date,
    last_trade_date: date,
) -> tuple[GCProspectiveAcquisitionSourceRecord, GCProspectiveProviderLogRecord]:
    first = datetime.combine(first_trade_date, datetime.min.time(), tzinfo=UTC)
    last = datetime.combine(last_trade_date, datetime.min.time(), tzinfo=UTC) + timedelta(hours=23, minutes=55)
    count = max(1, (last_trade_date - first_trade_date).days + 1) * 10
    log = _provider_log(roster.contract, first, last, count)
    value = GCProspectiveAcquisitionSourceRecord(
        source_id="pending",
        source_name=f"SYNTHETIC-{roster.contract}.txt",
        source_sha256=_hash(f"source-{roster.contract}"),
        byte_count=count * 64,
        row_count=count,
        contract=roster.contract,
        role=roster.role,
        capture_timestamp=datetime(2027, 3, 3, 3, tzinfo=UTC),
        acquisition_completed_timestamp=datetime(2027, 3, 3, 2, tzinfo=UTC),
        completed_data_cutoff_timestamp=datetime(2027, 3, 2, 23, 59, tzinfo=UTC),
        first_source_timestamp=first,
        last_source_timestamp=last,
        first_trade_date=first_trade_date,
        last_trade_date=last_trade_date,
        provider_log_id=log.provider_log_id,
        calendar_evidence_ids=(calendar_id,),
        chart_timezone="Asia/Tokyo",
        timeframe="5M",
        storage_time_unit="1 Tick",
        schema_id="GC_SIERRA_5M_TICK_EXPORT_V1",
        ordering_digest=_hash(f"ordering-{roster.contract}"),
        validation_status=SMCV2PrimitiveStatus.VALID,
        reasons=("SOURCE_METADATA_VALID",),
    )
    return replace(value, source_id=_identity("SOURCE", value, "source_id")), log


def _sources_and_logs(
    roster: tuple[GCProspectiveContractRosterRecord, ...],
    calendar_id: str,
) -> tuple[tuple[GCProspectiveAcquisitionSourceRecord, ...], tuple[GCProspectiveProviderLogRecord, ...]]:
    ranges = (
        (date(2026, 8, 1), date(2026, 8, 31)),
        (date(2026, 9, 1), date(2027, 2, 28)),
        (date(2027, 3, 1), date(2027, 3, 1)),
    )
    pairs = tuple(_source(record, calendar_id, *interval) for record, interval in zip(roster, ranges))
    return tuple(pair[0] for pair in pairs), tuple(pair[1] for pair in pairs)


def _contamination() -> tuple[GCProspectiveContaminationRecord, ...]:
    value = GCProspectiveContaminationRecord(
        contamination_record_id="pending",
        evidence_id="PRIOR-RESEARCH-REGISTRY-COMPLETE",
        evidence_kind="PRIOR_RESEARCH_PROGRAM",
        first_trade_date=date(2024, 1, 1),
        last_trade_date=date(2025, 12, 31),
        outcome_contacted=False,
        overlaps_cohort=False,
        exclusion_reason="NO_COHORT_OVERLAP",
        evidence_sha256=_hash("prior-research-registry"),
    )
    return (replace(value, contamination_record_id=_identity("CONTAMINATION", value, "contamination_record_id")),)


def _canonical_roster(records: tuple[GCProspectiveContractRosterRecord, ...]) -> tuple[GCProspectiveContractRosterRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.delivery_order, item.contract, item.roster_record_id)))


def _canonical_sources(
    records: tuple[GCProspectiveAcquisitionSourceRecord, ...],
    roster: tuple[GCProspectiveContractRosterRecord, ...],
) -> tuple[GCProspectiveAcquisitionSourceRecord, ...]:
    order = {item.contract: item.delivery_order for item in roster}
    return tuple(sorted(records, key=lambda item: (order.get(item.contract, 10**9), item.source_name, item.source_id)))


def _canonical_logs(records: tuple[GCProspectiveProviderLogRecord, ...]) -> tuple[GCProspectiveProviderLogRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.contract, item.provider_log_id)))


def _canonical_calendars(records: tuple[GCProspectiveCalendarEvidenceRecord, ...]) -> tuple[GCProspectiveCalendarEvidenceRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.first_trade_date, item.last_trade_date, item.source_kind, item.calendar_evidence_id)))


def _canonical_contamination(records: tuple[GCProspectiveContaminationRecord, ...]) -> tuple[GCProspectiveContaminationRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.first_trade_date, item.last_trade_date, item.evidence_id, item.contamination_record_id)))


def _manifest(
    config: GCProspectiveAcquisitionConfig,
    roster: tuple[GCProspectiveContractRosterRecord, ...],
    sources: tuple[GCProspectiveAcquisitionSourceRecord, ...],
    logs: tuple[GCProspectiveProviderLogRecord, ...],
    calendars: tuple[GCProspectiveCalendarEvidenceRecord, ...],
    contamination: tuple[GCProspectiveContaminationRecord, ...],
) -> GCProspectiveAcquisitionManifest:
    ordered_roster = _canonical_roster(roster)
    ordered_sources = _canonical_sources(sources, ordered_roster)
    ordered_logs = _canonical_logs(logs)
    ordered_calendars = _canonical_calendars(calendars)
    ordered_contamination = _canonical_contamination(contamination)
    config_id = make_gc_prospective_acquisition_id("CONFIG", config)
    roster_ids = tuple(item.roster_record_id for item in ordered_roster)
    source_ids = tuple(item.source_id for item in ordered_sources)
    log_ids = tuple(item.provider_log_id for item in ordered_logs)
    calendar_ids = tuple(item.calendar_evidence_id for item in ordered_calendars)
    contamination_ids = tuple(item.contamination_record_id for item in ordered_contamination)
    artifact_set = make_gc_prospective_acquisition_id(
        "ARTIFACT_SET",
        {
            "config_id": config_id,
            "roster_record_ids": roster_ids,
            "source_ids": source_ids,
            "provider_log_ids": log_ids,
            "calendar_evidence_ids": calendar_ids,
            "contamination_record_ids": contamination_ids,
        },
    )
    reason_counts: dict[str, int] = {}
    for source in ordered_sources:
        for reason in source.reasons:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    excluded = sum(item.role is GCProspectiveAcquisitionSourceRole.EXCLUDED for item in ordered_roster)
    value = GCProspectiveAcquisitionManifest(
        manifest_id="pending",
        version="GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1",
        program_id="GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1",
        cohort_id="GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1_20260901_20270301",
        purpose="PROSPECTIVE_RAW_ACQUISITION_ONLY",
        governing_commit="076d134785695b3b36f88910dbcdd5ea77866d5d",
        governing_hashes=GOVERNING_HASHES,
        config_id=config_id,
        roster_record_ids=roster_ids,
        source_ids=source_ids,
        provider_log_ids=log_ids,
        calendar_evidence_ids=calendar_ids,
        contamination_record_ids=contamination_ids,
        requested_source_count=len(ordered_roster),
        admitted_source_count=len(ordered_sources),
        excluded_source_count=excluded,
        reason_counts=tuple(sorted(reason_counts.items())),
        artifact_set_identity=artifact_set,
        outcome_contact_count=sum(item.outcome_contacted for item in ordered_contamination),
        final_oos_payload_access_count=0,
        candidate_build_allowed=False,
        feature_label_build_allowed=False,
        corpus_build_allowed=False,
        training_allowed=False,
        oos_evaluation_allowed=False,
        integration_allowed=False,
        trading_allowed=False,
    )
    return replace(value, manifest_id=_identity("MANIFEST", value, "manifest_id"))


def _bundle() -> dict[str, object]:
    config = _config()
    roster = _roster()
    calendars = _calendar()
    sources, logs = _sources_and_logs(roster, calendars[0].calendar_evidence_id)
    contamination = _contamination()
    return {
        "config": config,
        "contract_roster": roster,
        "sources": sources,
        "provider_logs": logs,
        "calendar_evidence": calendars,
        "contamination_records": contamination,
        "manifest": _manifest(config, roster, sources, logs, calendars, contamination),
    }


def _result(**updates: object):
    values = _bundle()
    values.update({key: value for key, value in updates.items() if value is not MISSING})
    if "sources" not in updates and "provider_logs" in updates:
        current_sources = values["sources"]
        current_logs = values["provider_logs"]
        if type(current_sources) is tuple and type(current_logs) is tuple and len(current_sources) == len(current_logs):
            rebound = []
            for source, log in zip(current_sources, current_logs):
                rebound.append(_replace_id("SOURCE", source, "source_id", provider_log_id=log.provider_log_id))
            values["sources"] = tuple(rebound)
    if "sources" not in updates and "calendar_evidence" in updates:
        current_sources = values["sources"]
        current_calendars = values["calendar_evidence"]
        if type(current_sources) is tuple and type(current_calendars) is tuple:
            calendar_ids = tuple(item.calendar_evidence_id for item in current_calendars)
            values["sources"] = tuple(
                _replace_id("SOURCE", source, "source_id", calendar_evidence_ids=calendar_ids)
                for source in current_sources
            )
    if updates.get("manifest", MISSING) is MISSING and any(
        key in updates for key in ("config", "contract_roster", "sources", "provider_logs", "calendar_evidence", "contamination_records")
    ):
        supplied = tuple(values[name] for name in ("config", "contract_roster", "sources", "provider_logs", "calendar_evidence", "contamination_records"))
        if all(value is not None and type(value) is tuple for value in supplied[1:]) and type(supplied[0]) is GCProspectiveAcquisitionConfig:
            values["manifest"] = _manifest(*supplied)  # type: ignore[arg-type]
    return validate_gc_prospective_acquisition_manifest(**values)  # type: ignore[arg-type]


def _replace_id(kind: str, value: object, id_field: str, **changes: object):
    changed = replace(value, **changes)
    return replace(changed, **{id_field: _identity(kind, changed, id_field)})


def test_case_01_exact_constants_and_boundaries_pass() -> None:
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION == "GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID == "GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_COHORT_ID.endswith("20260901_20270301")
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_INSTRUMENT == "GC"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_VENUE == "COMEX"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_TIMEFRAME == "5M"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT == "1 Tick"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE == "Asia/Tokyo"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE == "America/New_York"
    assert acquisition.GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD == 220
    assert _result().status is SMCV2PrimitiveStatus.VALID


def test_case_02_config_is_frozen_utc_exact_and_deterministic() -> None:
    config = _config()
    with pytest.raises(FrozenInstanceError):
        config.provider = "changed"  # type: ignore[misc]
    assert config.decision_timestamp.utcoffset() == timedelta(0)
    assert make_gc_prospective_acquisition_id("CONFIG", config) == make_gc_prospective_acquisition_id("CONFIG", config)


def test_case_03_missing_config_is_unknown_unless_other_evidence_invalid() -> None:
    assert _result(config=None).status is SMCV2PrimitiveStatus.UNKNOWN
    sources = _bundle()["sources"]
    broken = (replace(sources[0], source_sha256="bad"), *sources[1:])  # type: ignore[index]
    result = _result(config=None, sources=broken, manifest=None)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert "INVALID_SOURCE_METADATA" in result.reasons


def test_case_04_naive_or_non_utc_config_timestamp_is_invalid() -> None:
    for moment in (datetime(2026, 8, 31, 8, 17, 34), datetime(2026, 8, 31, 17, 17, 34, tzinfo=timezone(timedelta(hours=9)))):
        assert "INVALID_CONFIGURATION" in _result(config=replace(_config(), decision_timestamp=moment), manifest=None).reasons


def test_case_05_changed_cohort_or_capture_boundary_is_invalid() -> None:
    for change in (
        {"cohort_start_trade_date": date(2026, 9, 2)},
        {"cohort_end_trade_date": date(2027, 3, 2)},
        {"capture_window_start_timestamp": datetime(2027, 3, 2, 0, 0, 1, tzinfo=UTC)},
        {"capture_window_end_timestamp": datetime(2027, 3, 8, tzinfo=UTC)},
    ):
        assert _result(config=replace(_config(), **change), manifest=None).status is SMCV2PrimitiveStatus.INVALID


def test_case_06_retention_other_than_220_is_invalid() -> None:
    assert "INVALID_CONFIGURATION" in _result(config=replace(_config(), maximum_historical_days_to_download=219), manifest=None).reasons


def test_case_07_provider_instrument_venue_and_setting_drift_is_invalid() -> None:
    changes = (
        {"provider": "OTHER"}, {"instrument": "MGC"}, {"venue": "OTHER"}, {"timeframe": "1M"},
        {"storage_time_unit": "1 Second"}, {"chart_timezone": "UTC"}, {"exchange_timezone": "UTC"},
        {"timezone_data_version": "tzdata-2026b"},
    )
    for change in changes:
        assert _result(config=replace(_config(), **change), manifest=None).status is SMCV2PrimitiveStatus.INVALID


def test_case_08_governing_hash_malformed_or_wrong_is_invalid() -> None:
    for digest in ("bad", "0" * 64):
        result = _result(config=replace(_config(), governing_proposal_sha256=digest), manifest=None)
        assert "INVALID_CONFIGURATION" in result.reasons


def test_case_09_contract_regex_and_canonical_delivery_order_pass() -> None:
    assert _result().status is SMCV2PrimitiveStatus.VALID
    roster = _roster()
    assert [item.delivery_order for item in roster] == sorted(item.delivery_order for item in roster)


def test_case_10_duplicate_roster_identity_is_invalid() -> None:
    roster = _roster()
    variants = (
        (roster[0], replace(roster[1], contract=roster[0].contract), roster[2]),
        (roster[0], replace(roster[1], roster_record_id=roster[0].roster_record_id), roster[2]),
        (roster[0], replace(roster[1], delivery_order=roster[0].delivery_order), roster[2]),
        (roster[0], replace(roster[1], listing_source_id=roster[0].listing_source_id), roster[2]),
    )
    for changed in variants:
        assert "INVALID_ROSTER_EVIDENCE" in _result(contract_roster=changed, manifest=None).reasons


def test_case_11_missing_predecessor_is_unknown() -> None:
    bundle = _bundle()
    assert "UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE" in _result(
        contract_roster=bundle["contract_roster"][1:], sources=bundle["sources"][1:], provider_logs=bundle["provider_logs"][1:]  # type: ignore[index]
    ).reasons


def test_case_12_missing_candidate_is_unknown() -> None:
    bundle = _bundle()
    keep = (0, 2)
    assert "UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE" in _result(
        contract_roster=tuple(bundle["contract_roster"][i] for i in keep),  # type: ignore[index]
        sources=tuple(bundle["sources"][i] for i in keep),  # type: ignore[index]
        provider_logs=tuple(bundle["provider_logs"][i] for i in keep),  # type: ignore[index]
    ).reasons


def test_case_13_missing_successor_is_unknown() -> None:
    bundle = _bundle()
    assert "UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE" in _result(
        contract_roster=bundle["contract_roster"][:2], sources=bundle["sources"][:2], provider_logs=bundle["provider_logs"][:2]  # type: ignore[index]
    ).reasons


def test_case_14_excluded_roster_record_cannot_be_admitted() -> None:
    bundle = _bundle()
    roster = list(bundle["contract_roster"])  # type: ignore[arg-type]
    roster[1] = _replace_id("ROSTER", roster[1], "roster_record_id", role=GCProspectiveAcquisitionSourceRole.EXCLUDED)
    assert "INVALID_ROSTER_EVIDENCE" in _result(contract_roster=tuple(roster), manifest=None).reasons


def test_case_15_manual_or_reordered_manifest_roster_ids_are_invalid() -> None:
    bundle = _bundle()
    manifest = bundle["manifest"]
    assert "INVALID_IDENTITY_OR_CONSERVATION" in _result(manifest=replace(manifest, roster_record_ids=tuple(reversed(manifest.roster_record_ids)))).reasons  # type: ignore[union-attr]


def test_case_16_source_record_is_frozen_and_has_no_raw_bar_field() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        source.row_count = 1  # type: ignore[misc]
    names = {field.name for field in fields(GCProspectiveAcquisitionSourceRecord)}
    assert not names.intersection({"bars", "raw_bytes", "ohlc", "volume", "label", "outcome", "return_value"})


def test_case_17_malformed_source_metadata_or_identity_is_invalid() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    variants = (
        replace(source, source_sha256="BAD"), replace(source, ordering_digest="BAD"),
        replace(source, byte_count=-1), replace(source, first_source_timestamp=datetime(2026, 1, 1)),
        replace(source, source_id="manual"),
    )
    for changed in variants:
        sources = (changed, *_bundle()["sources"][1:])  # type: ignore[index]
        assert "INVALID_SOURCE_METADATA" in _result(sources=sources, manifest=None).reasons


def test_case_18_capture_outside_fixed_window_is_invalid() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    changed = _replace_id("SOURCE", source, "source_id", capture_timestamp=datetime(2027, 3, 9, tzinfo=UTC))
    assert "INVALID_SOURCE_METADATA" in _result(sources=(changed, *_bundle()["sources"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_19_source_time_or_date_inversion_is_invalid() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    changed = _replace_id("SOURCE", source, "source_id", first_source_timestamp=source.last_source_timestamp + timedelta(minutes=5))
    assert "INVALID_SOURCE_METADATA" in _result(sources=(changed, *_bundle()["sources"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_20_source_contract_or_role_absent_from_roster_is_invalid() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    for change in ({"contract": "GCG27-COMEX"}, {"role": GCProspectiveAcquisitionSourceRole.SUCCESSOR_CONTEXT}):
        changed = _replace_id("SOURCE", source, "source_id", **change)
        assert "INVALID_SOURCE_METADATA" in _result(sources=(changed, *_bundle()["sources"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_21_duplicate_source_name_id_or_hash_is_invalid() -> None:
    sources = _bundle()["sources"]
    for field_name in ("source_name", "source_id", "source_sha256"):
        changed = replace(sources[1], **{field_name: getattr(sources[0], field_name)})  # type: ignore[index]
        assert "INVALID_SOURCE_METADATA" in _result(sources=(sources[0], changed, sources[2]), manifest=None).reasons  # type: ignore[index]


def test_case_22_source_settings_and_schema_are_exact() -> None:
    source = _bundle()["sources"][0]  # type: ignore[index]
    for change in ({"chart_timezone": "UTC"}, {"timeframe": "1M"}, {"storage_time_unit": "1 Second"}, {"schema_id": "GC_OTHER_SCHEMA_V1"}):
        changed = _replace_id("SOURCE", source, "source_id", **change)
        assert "INVALID_SOURCE_METADATA" in _result(sources=(changed, *_bundle()["sources"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_23_each_source_requires_one_matching_provider_log() -> None:
    bundle = _bundle()
    assert "UNKNOWN_PROVIDER_LOG_INCOMPLETE" in _result(provider_logs=bundle["provider_logs"][1:]).reasons  # type: ignore[index]


def test_case_24_provider_status_is_unknown_or_invalid_by_form() -> None:
    bundle = _bundle()
    log = bundle["provider_logs"][0]  # type: ignore[index]
    pending = _replace_id("PROVIDER_LOG", log, "provider_log_id", completion_status="PENDING")
    assert "UNKNOWN_PROVIDER_LOG_INCOMPLETE" in _result(provider_logs=(pending, *bundle["provider_logs"][1:]), manifest=None).reasons  # type: ignore[index]
    malformed = replace(log, completion_status="")
    assert "INVALID_PROVIDER_LOG_EVIDENCE" in _result(provider_logs=(malformed, *bundle["provider_logs"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_25_provider_contract_or_count_contradiction_is_invalid() -> None:
    bundle = _bundle()
    log = bundle["provider_logs"][0]  # type: ignore[index]
    for change in ({"contract": "GCG27-COMEX"}, {"received_record_count": log.received_record_count + 1}):
        changed = _replace_id("PROVIDER_LOG", log, "provider_log_id", **change)
        assert "INVALID_PROVIDER_LOG_EVIDENCE" in _result(provider_logs=(changed, *bundle["provider_logs"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_26_provider_interval_or_completion_inversion_is_invalid() -> None:
    bundle = _bundle()
    log = bundle["provider_logs"][0]  # type: ignore[index]
    for change in (
        {"requested_end_timestamp": log.requested_start_timestamp},
        {"received_end_timestamp": log.received_start_timestamp - timedelta(seconds=1)},
        {"completion_timestamp": log.received_end_timestamp - timedelta(seconds=1)},
    ):
        changed = _replace_id("PROVIDER_LOG", log, "provider_log_id", **change)
        assert "INVALID_PROVIDER_LOG_EVIDENCE" in _result(provider_logs=(changed, *bundle["provider_logs"][1:]), manifest=None).reasons  # type: ignore[index]


def test_case_27_provider_log_excludes_sensitive_fields() -> None:
    names = {field.name for field in fields(GCProspectiveProviderLogRecord)}
    assert not names.intersection({"account", "balance", "credential", "token", "message", "payment_id"})


def test_case_28_allowed_official_calendar_kinds_and_timezone_pass() -> None:
    base = _calendar()[0]
    for kind in ("CME_STRUCTURED_TRADING_HOURS", "CME_OFFICIAL_NOTICE"):
        calendar = _replace_id("CALENDAR", base, "calendar_evidence_id", source_kind=kind)
        assert _result(calendar_evidence=(calendar,)).status is SMCV2PrimitiveStatus.VALID


def test_case_29_clarification_only_calendar_is_unknown() -> None:
    base = _calendar()[0]
    calendar = _replace_id("CALENDAR", base, "calendar_evidence_id", source_kind="CME_GCC_CLARIFICATION")
    assert "UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE" in _result(calendar_evidence=(calendar,)).reasons


def test_case_30_calendar_gap_is_unknown() -> None:
    base = _calendar()[0]
    calendar = _replace_id("CALENDAR", base, "calendar_evidence_id", last_trade_date=date(2026, 12, 31))
    assert "UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE" in _result(calendar_evidence=(calendar,)).reasons


def test_case_31_conflicting_overlapping_calendar_is_ambiguous() -> None:
    base = _calendar()[0]
    conflict = _replace_id(
        "CALENDAR", base, "calendar_evidence_id", calendar_version="CME-GC-CONFLICT",
        source_sha256=_hash("calendar-conflict-source"), normalized_row_digest=_hash("calendar-conflict-rows"),
    )
    result = _result(calendar_evidence=(base, conflict))
    assert result.status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert "AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY" in result.reasons


def test_case_32_false_calendar_authority_is_invalid() -> None:
    base = _calendar()[0]
    calendar = _replace_id("CALENDAR", base, "calendar_evidence_id", authoritative=False)
    assert "INVALID_CALENDAR_EVIDENCE" in _result(calendar_evidence=(calendar,)).reasons


def test_case_33_complete_nonoverlapping_contamination_registry_passes() -> None:
    assert _result().status is SMCV2PrimitiveStatus.VALID


def test_case_34_outcome_contacted_overlap_is_invalid() -> None:
    record = _contamination()[0]
    changed = _replace_id(
        "CONTAMINATION", record, "contamination_record_id", first_trade_date=date(2026, 9, 1),
        last_trade_date=date(2026, 9, 2), outcome_contacted=True, overlaps_cohort=True,
    )
    assert "INVALID_PRIOR_OUTCOME_CONTACT" in _result(contamination_records=(changed,)).reasons


def test_case_35_unknown_or_incomplete_contamination_is_unknown() -> None:
    assert "UNKNOWN_CONTAMINATION_HISTORY" in _result(contamination_records=()).reasons
    record = _contamination()[0]
    changed = _replace_id(
        "CONTAMINATION", record, "contamination_record_id", first_trade_date=date(2026, 9, 1),
        last_trade_date=date(2026, 9, 2), overlaps_cohort=False,
    )
    assert "UNKNOWN_CONTAMINATION_HISTORY" in _result(contamination_records=(changed,)).reasons


def test_case_36_manifest_purpose_and_authorities_are_exact() -> None:
    manifest = _bundle()["manifest"]
    assert "INVALID_AUTHORITY_OR_PURPOSE_DRIFT" in _result(manifest=replace(manifest, purpose="TRAINING")).reasons  # type: ignore[arg-type]
    for name in ("candidate_build_allowed", "feature_label_build_allowed", "corpus_build_allowed", "training_allowed", "oos_evaluation_allowed", "integration_allowed", "trading_allowed"):
        assert "INVALID_AUTHORITY_OR_PURPOSE_DRIFT" in _result(manifest=replace(manifest, **{name: True})).reasons  # type: ignore[arg-type]


def test_case_37_access_counts_must_be_zero() -> None:
    manifest = _bundle()["manifest"]
    for name in ("outcome_contact_count", "final_oos_payload_access_count"):
        assert "INVALID_AUTHORITY_OR_PURPOSE_DRIFT" in _result(manifest=replace(manifest, **{name: 1})).reasons  # type: ignore[arg-type]


def test_case_38_counts_and_reason_counts_conserve() -> None:
    manifest = _bundle()["manifest"]
    for change in (
        {"requested_source_count": manifest.requested_source_count + 1},
        {"admitted_source_count": manifest.admitted_source_count - 1},
        {"excluded_source_count": 1},
        {"reason_counts": (("SOURCE_METADATA_VALID", 99),)},
    ):
        assert "INVALID_IDENTITY_OR_CONSERVATION" in _result(manifest=replace(manifest, **change)).reasons


def test_case_39_ordered_member_ids_must_match_recomputation() -> None:
    manifest = _bundle()["manifest"]
    fields_to_change = ("roster_record_ids", "source_ids", "provider_log_ids", "calendar_evidence_ids", "contamination_record_ids")
    for name in fields_to_change:
        values = getattr(manifest, name)
        changed = tuple(reversed(values)) if len(values) > 1 else ("0" * 64,)
        assert "INVALID_IDENTITY_OR_CONSERVATION" in _result(manifest=replace(manifest, **{name: changed})).reasons


def test_case_40_config_manifest_and_artifact_ids_recompute() -> None:
    manifest = _bundle()["manifest"]
    for change in ({"config_id": "0" * 64}, {"artifact_set_identity": "0" * 64}, {"manifest_id": "0" * 64}):
        assert "INVALID_IDENTITY_OR_CONSERVATION" in _result(manifest=replace(manifest, **change)).reasons


def test_case_41_malformed_evidence_outranks_missing_context() -> None:
    source = replace(_bundle()["sources"][0], source_sha256="bad")  # type: ignore[index]
    result = _result(config=None, sources=(source,), provider_logs=None, calendar_evidence=None, contamination_records=None, manifest=None)
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.reasons.index("INVALID_SOURCE_METADATA") < result.reasons.index("MISSING_TOP_LEVEL_CONTEXT")


def test_case_42_status_precedence_is_exact() -> None:
    base = _calendar()[0]
    conflict = _replace_id("CALENDAR", base, "calendar_evidence_id", calendar_version="CONFLICT", normalized_row_digest=_hash("conflict"), source_sha256=_hash("conflict-source"))
    assert _result(calendar_evidence=(base, conflict), contamination_records=()).status is SMCV2PrimitiveStatus.AMBIGUOUS
    assert _result(contamination_records=()).status is SMCV2PrimitiveStatus.UNKNOWN
    manifest = replace(_bundle()["manifest"], trading_allowed=True)  # type: ignore[arg-type]
    assert _result(calendar_evidence=(base, conflict), contamination_records=(), manifest=manifest).status is SMCV2PrimitiveStatus.INVALID


def test_case_43_reasons_are_unique_and_ordered() -> None:
    source = replace(_bundle()["sources"][0], source_sha256="bad")  # type: ignore[index]
    result = _result(config=None, sources=(source,), provider_logs=None, calendar_evidence=None, contamination_records=None, manifest=None)
    assert len(result.reasons) == len(set(result.reasons))
    expected_order = [
        "INVALID_SOURCE_METADATA", "MISSING_TOP_LEVEL_CONTEXT", "UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE",
        "UNKNOWN_PROVIDER_LOG_INCOMPLETE", "UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE", "UNKNOWN_CONTAMINATION_HISTORY",
    ]
    assert [reason for reason in expected_order if reason in result.reasons] == list(result.reasons)
    assert result.blocking_reasons == result.reasons


def test_case_44_valid_result_returns_manifest_without_research_authority() -> None:
    result = _result()
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.manifest is not None
    assert result.reasons == ("VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY",)
    assert result.blocking_reasons == ()
    assert not any((result.manifest.candidate_build_allowed, result.manifest.feature_label_build_allowed, result.manifest.corpus_build_allowed, result.manifest.training_allowed, result.manifest.oos_evaluation_allowed, result.manifest.integration_allowed, result.manifest.trading_allowed))


def test_case_45_repeated_and_reordered_independent_inputs_are_identical() -> None:
    bundle = _bundle()
    first = validate_gc_prospective_acquisition_manifest(**bundle)  # type: ignore[arg-type]
    second = validate_gc_prospective_acquisition_manifest(**bundle)  # type: ignore[arg-type]
    reordered = validate_gc_prospective_acquisition_manifest(
        **{
            **bundle,
            "contract_roster": tuple(reversed(bundle["contract_roster"])),  # type: ignore[arg-type]
            "sources": tuple(reversed(bundle["sources"])),  # type: ignore[arg-type]
            "provider_logs": tuple(reversed(bundle["provider_logs"])),  # type: ignore[arg-type]
        }
    )
    assert first == second == reordered


def test_case_46_module_has_no_io_clock_randomness_or_mutation_work() -> None:
    source = inspect.getsource(acquisition)
    forbidden = ("open(", "Path(", "requests", "urllib", "socket", "subprocess", "time.time", "datetime.now", "random", "private_data")
    assert not any(token in source for token in forbidden)
    assert "frozen=True" in source


def test_case_47_public_surface_and_exact_three_path_scope_are_locked() -> None:
    assert acquisition.__all__ == (
        "GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION", "GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID",
        "GC_PROSPECTIVE_ACQUISITION_COHORT_ID", "GC_PROSPECTIVE_ACQUISITION_INSTRUMENT",
        "GC_PROSPECTIVE_ACQUISITION_VENUE", "GC_PROSPECTIVE_ACQUISITION_TIMEFRAME",
        "GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT", "GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE",
        "GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE", "GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD",
        "GCProspectiveAcquisitionSourceRole", "GCProspectiveAcquisitionConfig",
        "GCProspectiveContractRosterRecord", "GCProspectiveAcquisitionSourceRecord",
        "GCProspectiveProviderLogRecord", "GCProspectiveCalendarEvidenceRecord",
        "GCProspectiveContaminationRecord", "GCProspectiveAcquisitionManifest",
        "GCProspectiveAcquisitionResult", "make_gc_prospective_acquisition_id",
        "validate_gc_prospective_acquisition_manifest",
    )
    root = Path(__file__).resolve().parents[1]
    assert (root / "analysis/gc_prospective_acquisition_manifest.py").is_file()
    assert (root / "tests/test_gc_prospective_acquisition_manifest.py").is_file()
    assert (root / "docs/gc_futures_prospective_independent_development_cohort_acquisition_manifest_checkpoint.md").is_file()


def test_case_48_public_regression_boundary_has_zero_private_oos_or_trading_contact() -> None:
    parameters = inspect.signature(validate_gc_prospective_acquisition_manifest).parameters
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values())
    assert set(parameters) == {"config", "contract_roster", "sources", "provider_logs", "calendar_evidence", "contamination_records", "manifest"}
    result = _result()
    assert result.manifest is not None
    assert result.manifest.final_oos_payload_access_count == 0
    assert result.manifest.outcome_contact_count == 0
    assert result.manifest.training_allowed is result.manifest.oos_evaluation_allowed is result.manifest.integration_allowed is result.manifest.trading_allowed is False
