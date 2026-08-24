"""Deterministic, non-training GC pretraining-corpus assembly.

This module only reconciles already-built immutable evidence.  It performs no
file, network, clock, model, training, OOS-payload, or execution work.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re
from typing import Final

from analysis.gc_candidate_evidence_builder import (
    GC_CANDIDATE_EVIDENCE_VERSION,
    GCCandidateEvidenceIdentityKind,
    GCCandidateEvidenceManifest,
    GCCandidateEvidenceResult,
    GCSegmentCandidateEvidence,
    make_gc_candidate_evidence_id,
)
from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCSegmentPartition,
    GCSplitSessionCalendarEntry,
    make_gc_dataset_id,
)
from analysis.gc_feature_label_builder import (
    GC_AI_FEATURE_SCHEMA_ID,
    GC_AI_LABEL_HORIZON_BARS,
    GC_AI_LABEL_SCHEMA_ID,
    GC_FEATURE_LABEL_VERSION,
    GCFeatureLabelIdentityKind,
    GCFeatureLabelManifest,
    GCFeatureLabelResult,
    GCFeatureRow,
    GCLabelOutcome,
    GCResearchLabel,
    make_gc_feature_label_id,
)
from smc.inducement import Inducement
from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


GC_PRETRAINING_CORPUS_VERSION: Final = "GC-PRETRAINING-CORPUS-V1"
GC_PRETRAINING_INSTRUMENT: Final = "GC"
GC_PRETRAINING_TIMEFRAME: Final = "5M"
GC_PRETRAINING_TICK_SIZE: Final = Decimal("0.1")
GC_PRETRAINING_LABEL_HORIZON_BARS: Final = 12
GC_PRETRAINING_MINIMUM_EMBARGO_BARS: Final = 12

_UTC = timezone.utc
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_FINAL_OOS_SHA256 = "15e2f672457176749c4143baa4bb00c30d1ae913c82333cb8e8e8f79592ff46e"
_DEVELOPMENT_CONTRACTS = frozenset({"GCJ25", "GCM25", "GCQ25", "GCV25", "GCZ25"})
_CLOSED_CONTRACTS = frozenset({"GCG26", "GCJ26", "GCM26"})
_PARTITION_ORDER = {
    "TRAIN": 0,
    "VALIDATION": 1,
    "CALIBRATION": 2,
}
_REASON_ORDER = (
    "INVALID_PRETRAINING_CORPUS_EVIDENCE",
    "AMBIGUOUS_PRETRAINING_CORPUS_EVIDENCE",
    "MISSING_TOP_LEVEL_CONTEXT",
    "INDEPENDENCE_UNVERIFIED",
    "INSUFFICIENT_PARTITION_EVIDENCE",
    "PRETRAINING_CORPUS_VALID",
    "NO_ELIGIBLE_PRETRAINING_EVIDENCE",
)


class GCPretrainingSourceRole(str, Enum):
    PRETRAINING_DEVELOPMENT_CANDIDATE = "PRETRAINING_DEVELOPMENT_CANDIDATE"
    CLOSED_RESEARCH_ONLY = "CLOSED_RESEARCH_ONLY"
    SEALED_FINAL_OOS_CANDIDATE = "SEALED_FINAL_OOS_CANDIDATE"
    REFERENCE_ONLY = "REFERENCE_ONLY"
    SUPERSEDED_REFERENCE = "SUPERSEDED_REFERENCE"


class GCPretrainingPartition(str, Enum):
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    CALIBRATION = "CALIBRATION"
    FINAL_OOS = "FINAL_OOS"


@dataclass(frozen=True)
class GCPretrainingSourceRecord:
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCPretrainingSourceRole
    dataset_id: str
    first_trade_date: date
    last_trade_date: date
    acquisition_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    prior_run_manifest_ids: tuple[str, ...]
    contaminated_evidence_ids: tuple[str, ...]
    contamination_audit_complete: bool
    final_oos_payload_accessed: bool


@dataclass(frozen=True)
class GCPretrainingPartitionPlan:
    train_start_trade_date: date
    train_end_trade_date: date
    validation_start_trade_date: date
    validation_end_trade_date: date
    calibration_start_trade_date: date
    calibration_end_trade_date: date
    final_oos_start_trade_date: date
    final_oos_end_trade_date: date
    label_horizon_bars: int = GC_PRETRAINING_LABEL_HORIZON_BARS
    minimum_embargo_bars: int = GC_PRETRAINING_MINIMUM_EMBARGO_BARS


@dataclass(frozen=True)
class GCPretrainingCorpusRecord:
    record_id: str
    partition: GCPretrainingPartition
    direction: SMCV2Direction
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    dataset_id: str
    candidate_id: str
    feature_row_id: str
    label_id: str
    outcome: GCLabelOutcome
    feature_values: tuple[object, ...]
    source_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCPretrainingPartitionSummary:
    partition_id: str
    partition: GCPretrainingPartition
    start_trade_date: date
    end_trade_date: date
    record_ids: tuple[str, ...]
    contracts: tuple[str, ...]
    session_count: int
    candidate_count: int
    bullish_count: int
    bearish_count: int
    target_first_count: int
    invalidation_first_count: int
    timeout_count: int


@dataclass(frozen=True)
class GCPretrainingCorpusManifest:
    manifest_id: str
    corpus_id: str
    version: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_manifest_id: str
    feature_label_manifest_id: str
    feature_schema_id: str
    label_schema_id: str
    label_horizon_bars: int
    calendar_version: str
    timezone_data_version: str
    partition_plan_id: str
    source_ids: tuple[str, ...]
    prior_run_manifest_ids: tuple[str, ...]
    partition_ids: tuple[str, ...]
    record_ids: tuple[str, ...]
    exclusion_counts: tuple[tuple[str, int], ...]
    excluded_record_count: int
    contaminated_record_count: int
    admitted_record_count: int
    final_oos_source_sha256: str
    final_oos_start_trade_date: date
    final_oos_end_trade_date: date
    final_oos_payload_access_count: int
    training_allowed: bool
    oos_evaluation_allowed: bool
    integration_allowed: bool
    trading_allowed: bool


@dataclass(frozen=True)
class GCPretrainingCorpusResult:
    status: SMCV2PrimitiveStatus
    records: tuple[GCPretrainingCorpusRecord, ...] = ()
    partitions: tuple[GCPretrainingPartitionSummary, ...] = ()
    manifest: GCPretrainingCorpusManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


_EXACT_PLAN = GCPretrainingPartitionPlan(
    date(2024, 11, 4),
    date(2025, 6, 2),
    date(2025, 6, 16),
    date(2025, 8, 25),
    date(2025, 9, 8),
    date(2025, 11, 24),
    date(2026, 7, 6),
    date(2026, 8, 1),
)


def _text(value: object, name: str, *, upper: bool = False) -> str:
    if type(value) is not str or not value.strip():
        raise TypeError(f"{name} must be a nonempty str")
    normalized = value.strip()
    return normalized.upper() if upper else normalized


def _hash(value: object, name: str) -> str:
    if type(value) is not str or _HASH_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _integer(value: object, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be int")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} is below its minimum")
    return value


def _day(value: object, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be date")
    return value


def _moment(value: object, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be a timezone-aware datetime")
    return value.astimezone(_UTC)


def _decimal(value: object, name: str) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        raise TypeError(f"{name} must be a finite Decimal")
    return value


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    output = format(value, "f")
    if "." in output:
        output = output.rstrip("0").rstrip(".")
    return output if "." in output else output + ".0"


def _timestamp_text(value: datetime) -> str:
    return _moment(value, "timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonical(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if type(value) is Decimal:
        return _decimal_text(_decimal(value, "Decimal"))
    if type(value) is datetime:
        return _timestamp_text(value)
    if type(value) is date:
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("canonical mapping keys must be str")
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported canonical value {type(value).__name__}")


def _sha(value: object) -> str:
    encoded = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reason_result(
    status: SMCV2PrimitiveStatus,
    reason: str,
    *,
    records: tuple[GCPretrainingCorpusRecord, ...] = (),
    partitions: tuple[GCPretrainingPartitionSummary, ...] = (),
    manifest: GCPretrainingCorpusManifest | None = None,
) -> GCPretrainingCorpusResult:
    if reason not in _REASON_ORDER:
        raise ValueError("unknown pretraining corpus reason")
    blocking = (reason,) if status in {
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    } else ()
    return GCPretrainingCorpusResult(status, records, partitions, manifest, (reason,), blocking)


def _validate_plan(value: object) -> GCPretrainingPartitionPlan:
    if type(value) is not GCPretrainingPartitionPlan:
        raise TypeError("partition_plan must be GCPretrainingPartitionPlan")
    for field in fields(GCPretrainingPartitionPlan):
        actual = getattr(value, field.name)
        expected = getattr(_EXACT_PLAN, field.name)
        if type(expected) is date:
            _day(actual, field.name)
        else:
            _integer(actual, field.name, minimum=1)
        if actual != expected:
            raise ValueError(f"{field.name} does not match the locked plan")
    return value


def _partition_for(day: date, plan: GCPretrainingPartitionPlan) -> GCPretrainingPartition | None:
    if plan.train_start_trade_date <= day < plan.train_end_trade_date:
        return GCPretrainingPartition.TRAIN
    if plan.validation_start_trade_date <= day < plan.validation_end_trade_date:
        return GCPretrainingPartition.VALIDATION
    if plan.calibration_start_trade_date <= day < plan.calibration_end_trade_date:
        return GCPretrainingPartition.CALIBRATION
    if plan.final_oos_start_trade_date <= day < plan.final_oos_end_trade_date:
        return GCPretrainingPartition.FINAL_OOS
    return None


def _bar_digest(segment: GCCanonicalContractSegment) -> str:
    bars: list[dict[str, object]] = []
    previous: tuple[int, datetime] | None = None
    for bar in segment.bars:
        if type(bar.index) is not int or type(bar.volume) is not int or type(bar.is_closed) is not bool:
            raise TypeError("malformed canonical bar")
        if not bar.is_closed or bar.volume < 0:
            raise ValueError("canonical bars must be closed with nonnegative volume")
        current = (bar.index, _moment(bar.timestamp, "bar.timestamp"))
        if previous is not None and current <= previous:
            raise ValueError("canonical bars must be strictly ordered")
        previous = current
        if any(type(getattr(bar, name)) is not int for name in ("open_tick", "high_tick", "low_tick", "close_tick")):
            raise TypeError("bar ticks must be int")
        if bar.low_tick > min(bar.open_tick, bar.close_tick) or bar.high_tick < max(bar.open_tick, bar.close_tick):
            raise ValueError("invalid OHLC geometry")
        bars.append({
            "index": bar.index,
            "timestamp": _timestamp_text(bar.timestamp),
            "open_tick": bar.open_tick,
            "high_tick": bar.high_tick,
            "low_tick": bar.low_tick,
            "close_tick": bar.close_tick,
            "volume": bar.volume,
            "is_closed": bar.is_closed,
        })
    return _sha(tuple(bars))


def _normalize_calendar(
    entries: object,
) -> tuple[tuple[dict[str, object], ...], str]:
    if type(entries) is not tuple:
        raise TypeError("dataset_calendar_entries must be tuple")
    normalized: list[dict[str, object]] = []
    previous: date | None = None
    version: str | None = None
    for item in entries:
        if type(item) not in (KillZoneCalendarEntry, GCSplitSessionCalendarEntry):
            raise TypeError("calendar entry has an invalid type")
        trade_date = _day(item.trade_date, "calendar.trade_date")
        if previous is not None and trade_date <= previous:
            raise ValueError("calendar entries must be strictly ordered")
        previous = trade_date
        calendar_version = _text(item.calendar_version, "calendar_version")
        if version is not None and calendar_version != version:
            raise ValueError("calendar versions conflict")
        version = calendar_version
        if type(item) is KillZoneCalendarEntry:
            if type(item.session_status) is not KillZoneSessionStatus:
                raise TypeError("session_status must be KillZoneSessionStatus")
            if item.session_status is KillZoneSessionStatus.SESSION_CLOSED:
                if item.session_open_timestamp is not None or item.session_close_timestamp is not None:
                    raise ValueError("closed session cannot have bounds")
                intervals: tuple[dict[str, str], ...] = ()
            else:
                opening = _moment(item.session_open_timestamp, "session_open_timestamp")
                closing = _moment(item.session_close_timestamp, "session_close_timestamp")
                if opening >= closing or closing - opening > timedelta(hours=24):
                    raise ValueError("invalid calendar interval")
                intervals = ({"start_timestamp": _timestamp_text(opening), "end_timestamp": _timestamp_text(closing)},)
            normalized.append({
                "calendar_kind": "SINGLE_INTERVAL",
                "calendar_version": calendar_version,
                "trade_date": trade_date.isoformat(),
                "session_status": item.session_status.value,
                "intervals": intervals,
                "source_artifact_ids": (),
                "source_artifact_sha256s": (),
            })
        else:
            if type(item.intervals) is not tuple or not item.intervals:
                raise ValueError("split session requires intervals")
            intervals_list: list[dict[str, str]] = []
            last_end: datetime | None = None
            for interval in item.intervals:
                start = _moment(interval.start_timestamp, "interval.start_timestamp")
                end = _moment(interval.end_timestamp, "interval.end_timestamp")
                if start >= end or (last_end is not None and start < last_end):
                    raise ValueError("invalid split session interval")
                last_end = end
                intervals_list.append({"start_timestamp": _timestamp_text(start), "end_timestamp": _timestamp_text(end)})
            source_ids = tuple(_hash(value, "source_artifact_id") for value in item.source_artifact_ids)
            source_hashes = tuple(_hash(value, "source_artifact_sha256") for value in item.source_artifact_sha256s)
            if not source_ids or len(source_ids) != len(source_hashes):
                raise ValueError("split-session provenance must be paired")
            normalized.append({
                "calendar_kind": "SPLIT_SESSION",
                "calendar_version": calendar_version,
                "trade_date": trade_date.isoformat(),
                "session_status": KillZoneSessionStatus.OPEN.value,
                "intervals": tuple(intervals_list),
                "source_artifact_ids": source_ids,
                "source_artifact_sha256s": source_hashes,
            })
    return tuple(normalized), version or ""


def _dataset_evidence_digest(manifest: GCDatasetManifest) -> str:
    evidence = {
        "version": manifest.version,
        "source_ids": manifest.source_ids,
        "coverage_ids": manifest.coverage_ids,
        "coverage_digest": manifest.coverage_digest,
        "segment_ids": manifest.segment_ids,
        "calendar_version": manifest.calendar_version,
        "timezone_data_version": manifest.timezone_data_version,
        "raw_start_timestamp": _timestamp_text(manifest.raw_start_timestamp),
        "raw_end_timestamp": _timestamp_text(manifest.raw_end_timestamp),
        "usable_start_timestamp": None if manifest.usable_start_timestamp is None else _timestamp_text(manifest.usable_start_timestamp),
        "usable_end_timestamp": None if manifest.usable_end_timestamp is None else _timestamp_text(manifest.usable_end_timestamp),
        "parsed_row_count": manifest.parsed_row_count,
        "eligible_row_count": manifest.eligible_row_count,
        "development_bar_count": manifest.development_bar_count,
        "oos_bar_count": manifest.oos_bar_count,
        "excluded_row_count": manifest.excluded_row_count,
        "missing_bar_count": manifest.missing_bar_count,
        "attested_no_trade_interval_count": manifest.attested_no_trade_interval_count,
        "raw_volume": manifest.raw_volume,
        "eligible_volume": manifest.eligible_volume,
        "excluded_volume": manifest.excluded_volume,
        "completed_session_volumes": tuple((contract, day.isoformat(), volume) for contract, day, volume in manifest.completed_session_volumes),
        "exclusion_counts": manifest.exclusion_counts,
        "roll_trade_dates": tuple(day.isoformat() for day in manifest.roll_trade_dates),
    }
    return _sha(evidence)


def _validate_dataset(
    config: object,
    calendar_entries: object,
    result: object,
) -> tuple[GCDatasetBuildConfig, tuple[GCCanonicalContractSegment, ...], GCDatasetManifest | None]:
    if type(config) is not GCDatasetBuildConfig:
        raise TypeError("dataset_config must be GCDatasetBuildConfig")
    if config.instrument != GC_PRETRAINING_INSTRUMENT or config.timeframe != GC_PRETRAINING_TIMEFRAME:
        raise ValueError("dataset instrument/timeframe mismatch")
    if _decimal(config.tick_size, "dataset tick_size") != GC_PRETRAINING_TICK_SIZE:
        raise ValueError("dataset tick size mismatch")
    normalized_calendar, calendar_version = _normalize_calendar(calendar_entries)
    if type(result) is not GCDatasetBuildResult or type(result.status) is not GCDatasetBuildStatus:
        raise TypeError("dataset_result must be GCDatasetBuildResult")
    if type(result.segments) is not tuple:
        raise TypeError("dataset segments must be tuple")
    if result.status is GCDatasetBuildStatus.NONE:
        if result.dataset_id is not None or result.segments or result.manifest is not None:
            raise ValueError("NONE dataset result carries evidence")
        return config, (), None
    if result.status is not GCDatasetBuildStatus.VALID:
        raise ValueError(f"dataset status is {result.status.value}")
    if type(result.manifest) is not GCDatasetManifest:
        raise TypeError("VALID dataset requires a manifest")
    manifest = result.manifest
    if result.dataset_id != manifest.dataset_id:
        raise ValueError("dataset result and manifest IDs differ")
    if manifest.version != GC_DATASET_BUILDER_VERSION:
        raise ValueError("dataset version mismatch")
    if manifest.calendar_version != calendar_version or manifest.timezone_data_version != config.timezone_data_version:
        raise ValueError("dataset calendar/timezone mismatch")
    if type(manifest.source_ids) is not tuple or type(manifest.coverage_ids) is not tuple:
        raise TypeError("dataset identity histories must be tuples")
    for value in (*manifest.source_ids, *manifest.coverage_ids):
        _hash(value, "dataset history")
    _hash(manifest.coverage_digest, "coverage_digest")
    previous_segment: tuple[date, str, str] | None = None
    for segment in result.segments:
        if type(segment) is not GCCanonicalContractSegment:
            raise TypeError("segment has an invalid type")
        if type(segment.partition) is not GCSegmentPartition:
            raise TypeError("segment partition is invalid")
        _day(segment.first_trade_date, "segment.first_trade_date")
        _day(segment.last_trade_date, "segment.last_trade_date")
        if segment.first_trade_date > segment.last_trade_date:
            raise ValueError("segment date range is invalid")
        current = (segment.first_trade_date, segment.contract, segment.segment_id)
        if previous_segment is not None and current <= previous_segment:
            raise ValueError("segments must be canonically ordered")
        previous_segment = current
        expected = make_gc_dataset_id(
            identity_kind="SEGMENT",
            config=config,
            contract=segment.contract,
            first_trade_date=segment.first_trade_date,
            last_trade_date=segment.last_trade_date,
            source_ids=segment.source_ids,
            bar_digest=_bar_digest(segment),
            preceding_missing_bar_count=segment.preceding_missing_bar_count,
            partition=segment.partition,
        )
        if segment.segment_id != expected:
            raise ValueError("segment identity mismatch")
    if manifest.segment_ids != tuple(segment.segment_id for segment in result.segments):
        raise ValueError("dataset segment history mismatch")
    if manifest.parsed_row_count != manifest.eligible_row_count + manifest.excluded_row_count:
        raise ValueError("dataset row conservation failed")
    if manifest.raw_volume != manifest.eligible_volume + manifest.excluded_volume:
        raise ValueError("dataset volume conservation failed")
    expected_dataset_id = make_gc_dataset_id(
        identity_kind="DATASET",
        config=config,
        source_ids=manifest.source_ids,
        coverage_ids=manifest.coverage_ids,
        segment_ids=manifest.segment_ids,
        calendar_digest=_sha(normalized_calendar),
        coverage_digest=manifest.coverage_digest,
        evidence_digest=_dataset_evidence_digest(manifest),
        roll_trade_dates=manifest.roll_trade_dates,
    )
    if manifest.dataset_id != expected_dataset_id:
        raise ValueError("dataset identity mismatch")
    return config, result.segments, manifest


def _validate_candidate(
    value: object,
    *,
    dataset_id: str | None,
    segment_ids: tuple[str, ...],
) -> tuple[tuple[GCSegmentCandidateEvidence, ...], GCCandidateEvidenceManifest | None]:
    if type(value) is not GCCandidateEvidenceResult:
        raise TypeError("candidate_result must be GCCandidateEvidenceResult")
    if type(value.status) is not SMCV2PrimitiveStatus:
        raise TypeError("candidate status is invalid")
    if type(value.candidates) is not tuple or type(value.segment_results) is not tuple:
        raise TypeError("candidate histories must be tuples")
    if value.status is SMCV2PrimitiveStatus.NONE:
        if value.candidates or value.segment_results or value.manifest is not None:
            raise ValueError("NONE candidate result carries evidence")
        return (), None
    if value.status is not SMCV2PrimitiveStatus.VALID:
        raise ValueError(f"candidate status is {value.status.value}")
    if type(value.manifest) is not GCCandidateEvidenceManifest:
        raise TypeError("VALID candidate result requires a manifest")
    manifest = value.manifest
    if manifest.version != GC_CANDIDATE_EVIDENCE_VERSION or manifest.dataset_id != dataset_id:
        raise ValueError("candidate manifest dependency mismatch")
    if manifest.instrument != GC_PRETRAINING_INSTRUMENT or manifest.timeframe != GC_PRETRAINING_TIMEFRAME or manifest.tick_size != GC_PRETRAINING_TICK_SIZE:
        raise ValueError("candidate market contract mismatch")
    bundle_id = make_gc_candidate_evidence_id(
        identity_kind=GCCandidateEvidenceIdentityKind.BUNDLE,
        instrument=manifest.instrument,
        timeframe=manifest.timeframe,
        tick_size=manifest.tick_size,
        dataset_id=manifest.dataset_id,
        calendar_version=manifest.calendar_version,
        timezone_data_version=manifest.timezone_data_version,
        seed_id=manifest.seed_id,
        config=manifest.config,
        detector_versions=manifest.detector_versions,
        segment_result_ids=manifest.segment_result_ids,
        candidate_references=manifest.candidate_references,
    )
    if manifest.bundle_id != bundle_id:
        raise ValueError("candidate bundle identity mismatch")
    expected_manifest = make_gc_candidate_evidence_id(
        identity_kind=GCCandidateEvidenceIdentityKind.MANIFEST,
        instrument=manifest.instrument,
        timeframe=manifest.timeframe,
        tick_size=manifest.tick_size,
        dataset_id=manifest.dataset_id,
        calendar_version=manifest.calendar_version,
        timezone_data_version=manifest.timezone_data_version,
        seed_id=manifest.seed_id,
        config=manifest.config,
        detector_versions=manifest.detector_versions,
        segment_result_ids=manifest.segment_result_ids,
        candidate_references=manifest.candidate_references,
        bundle_id=bundle_id,
    )
    if manifest.manifest_id != expected_manifest:
        raise ValueError("candidate manifest identity mismatch")
    references: list[tuple[str, str]] = []
    previous: tuple[int, str, str] | None = None
    for item in value.candidates:
        if type(item) is not GCSegmentCandidateEvidence or type(item.evidence.inducement) is not Inducement:
            raise TypeError("candidate evidence is malformed")
        if item.segment_id not in segment_ids:
            raise ValueError("candidate references an unavailable segment")
        current = (item.segment_ordinal, item.segment_id, item.evidence.inducement.inducement_id)
        if previous is not None and current <= previous:
            raise ValueError("candidates must be strictly ordered")
        previous = current
        references.append((item.segment_id, _hash(item.evidence.inducement.inducement_id, "candidate_id")))
    if tuple(references) != manifest.candidate_references:
        raise ValueError("candidate reference history mismatch")
    if tuple(segment_id for segment_id, _ in manifest.segment_result_ids) != tuple(item.segment_id for item in value.segment_results):
        raise ValueError("candidate segment-result history mismatch")
    return value.candidates, manifest


def _validate_feature_labels(
    value: object,
    *,
    dataset_id: str | None,
) -> tuple[tuple[GCFeatureRow, ...], tuple[GCResearchLabel, ...], GCFeatureLabelManifest | None]:
    if type(value) is not GCFeatureLabelResult:
        raise TypeError("feature_label_result must be GCFeatureLabelResult")
    if type(value.status) is not SMCV2PrimitiveStatus or type(value.rows) is not tuple or type(value.labels) is not tuple:
        raise TypeError("feature-label result is malformed")
    if value.status is SMCV2PrimitiveStatus.NONE:
        if value.rows or value.labels or value.manifest is not None:
            raise ValueError("NONE feature-label result carries evidence")
        return (), (), None
    if value.status is not SMCV2PrimitiveStatus.VALID:
        raise ValueError(f"feature-label status is {value.status.value}")
    if type(value.manifest) is not GCFeatureLabelManifest:
        raise TypeError("VALID feature-label result requires a manifest")
    manifest = value.manifest
    if manifest.dataset_id != dataset_id or manifest.feature_schema_id != GC_AI_FEATURE_SCHEMA_ID or manifest.label_schema_id != GC_AI_LABEL_SCHEMA_ID or manifest.horizon_bars != GC_AI_LABEL_HORIZON_BARS:
        raise ValueError("feature-label manifest contract mismatch")
    if len(value.rows) != len(value.labels):
        raise ValueError("feature and label histories must be paired")
    for row, label in zip(value.rows, value.labels):
        if type(row) is not GCFeatureRow or type(label) is not GCResearchLabel:
            raise TypeError("feature-label item has an invalid type")
        expected_row = make_gc_feature_label_id(
            identity_kind=GCFeatureLabelIdentityKind.FEATURE_ROW,
            instrument=row.instrument,
            timeframe=row.timeframe,
            tick_size=row.tick_size,
            timezone_data_version=row.timezone_data_version,
            calendar_version=row.calendar_version,
            dataset_id=row.dataset_id,
            candidate_id=row.candidate_id,
            contract=row.contract,
            trade_date=row.trade_date,
            source_ids=row.source_ids,
            lineage_ids=row.lineage_ids,
            detector_versions=row.detector_versions,
            feature_schema_id=row.feature_schema_id,
            feature_values=row.feature_values,
            effective_index=row.effective_index,
            effective_timestamp=row.effective_timestamp,
        )
        if row.row_id != expected_row:
            raise ValueError("feature-row identity mismatch")
        expected_label = make_gc_feature_label_id(
            identity_kind=GCFeatureLabelIdentityKind.LABEL,
            instrument=label.instrument,
            timeframe=label.timeframe,
            tick_size=label.tick_size,
            timezone_data_version=label.timezone_data_version,
            calendar_version=label.calendar_version,
            dataset_id=label.dataset_id,
            candidate_id=label.candidate_id,
            contract=label.contract,
            trade_date=label.trade_date,
            label_schema_id=label.label_schema_id,
            horizon_bars=label.horizon_bars,
            target_tick=label.target_tick,
            invalidation_tick=label.invalidation_tick,
            outcome=label.outcome,
            effective_index=label.effective_index,
            effective_timestamp=label.effective_timestamp,
            first_outcome_index=label.first_outcome_index,
            first_outcome_timestamp=label.first_outcome_timestamp,
            horizon_end_index=label.horizon_end_index,
            horizon_end_timestamp=label.horizon_end_timestamp,
        )
        if label.label_id != expected_label:
            raise ValueError("label identity mismatch")
    expected_manifest = make_gc_feature_label_id(
        identity_kind=GCFeatureLabelIdentityKind.MANIFEST,
        instrument=manifest.instrument,
        timeframe=manifest.timeframe,
        tick_size=manifest.tick_size,
        timezone_data_version=manifest.timezone_data_version,
        calendar_version=manifest.calendar_version,
        dataset_id=manifest.dataset_id,
        feature_schema_id=manifest.feature_schema_id,
        label_schema_id=manifest.label_schema_id,
        horizon_bars=manifest.horizon_bars,
        feature_row_ids=manifest.feature_row_ids,
        label_ids=manifest.label_ids,
    )
    if manifest.manifest_id != expected_manifest or manifest.feature_row_ids != tuple(row.row_id for row in value.rows) or manifest.label_ids != tuple(label.label_id for label in value.labels):
        raise ValueError("feature-label manifest identity mismatch")
    return value.rows, value.labels, manifest


def _validate_sources(
    value: object,
    *,
    dataset_id: str | None,
    calendar_version: str,
    timezone_data_version: str,
) -> tuple[GCPretrainingSourceRecord, ...]:
    if type(value) is not tuple:
        raise TypeError("source_registry must be tuple")
    previous: tuple[str, date, date, str, str, str] | None = None
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    sealed_count = 0
    for item in value:
        if type(item) is not GCPretrainingSourceRecord:
            raise TypeError("source registry item has an invalid type")
        source_id = _hash(item.source_id, "source_id")
        source_hash = _hash(item.source_sha256, "source_sha256")
        if source_id in seen_ids or source_hash in seen_hashes:
            raise ValueError("source IDs and hashes must be unique")
        seen_ids.add(source_id)
        seen_hashes.add(source_hash)
        if type(item.role) is not GCPretrainingSourceRole:
            raise TypeError("source role is invalid")
        first = _day(item.first_trade_date, "first_trade_date")
        last = _day(item.last_trade_date, "last_trade_date")
        if first > last:
            raise ValueError("source date range is invalid")
        _moment(item.acquisition_timestamp, "acquisition_timestamp")
        if item.dataset_id != dataset_id or item.calendar_version != calendar_version or item.timezone_data_version != timezone_data_version:
            raise ValueError("source registry dependency mismatch")
        if type(item.prior_run_manifest_ids) is not tuple or type(item.contaminated_evidence_ids) is not tuple:
            raise TypeError("source audit histories must be tuples")
        for identity in (*item.prior_run_manifest_ids, *item.contaminated_evidence_ids):
            _hash(identity, "source audit identity")
        if type(item.contamination_audit_complete) is not bool or type(item.final_oos_payload_accessed) is not bool:
            raise TypeError("source audit flags must be bool")
        if item.final_oos_payload_accessed:
            raise ValueError("final OOS payload was accessed")
        if item.role is GCPretrainingSourceRole.PRETRAINING_DEVELOPMENT_CANDIDATE and item.contract not in _DEVELOPMENT_CONTRACTS:
            raise ValueError("invalid development source contract")
        if item.contract in _CLOSED_CONTRACTS and item.role is not GCPretrainingSourceRole.CLOSED_RESEARCH_ONLY:
            raise ValueError("closed research contract has the wrong role")
        if item.role is GCPretrainingSourceRole.SEALED_FINAL_OOS_CANDIDATE:
            sealed_count += 1
            if item.contract != "GCQ26" or source_hash != _FINAL_OOS_SHA256:
                raise ValueError("sealed final-OOS source mismatch")
        current = (item.role.value, first, last, item.contract, item.source_name, source_id)
        if previous is not None and current <= previous:
            raise ValueError("source registry must be canonically ordered")
        previous = current
    if value and sealed_count != 1:
        raise ValueError("complete registry requires exactly one sealed final-OOS source")
    return value


def _record_identity(
    partition: GCPretrainingPartition,
    direction: SMCV2Direction,
    row: GCFeatureRow,
    label: GCResearchLabel,
) -> str:
    return _sha({
        "version": GC_PRETRAINING_CORPUS_VERSION,
        "identity_kind": "RECORD",
        "partition": partition,
        "direction": direction,
        "contract": row.contract,
        "trade_date": row.trade_date,
        "effective_index": row.effective_index,
        "effective_timestamp": row.effective_timestamp,
        "dataset_id": row.dataset_id,
        "candidate_id": row.candidate_id,
        "feature_row_id": row.row_id,
        "label_id": label.label_id,
        "outcome": label.outcome,
        "feature_values": row.feature_values,
        "source_ids": row.source_ids,
        "lineage_ids": row.lineage_ids,
    })


def _partition_bounds(partition: GCPretrainingPartition, plan: GCPretrainingPartitionPlan) -> tuple[date, date]:
    if partition is GCPretrainingPartition.TRAIN:
        return plan.train_start_trade_date, plan.train_end_trade_date
    if partition is GCPretrainingPartition.VALIDATION:
        return plan.validation_start_trade_date, plan.validation_end_trade_date
    if partition is GCPretrainingPartition.CALIBRATION:
        return plan.calibration_start_trade_date, plan.calibration_end_trade_date
    return plan.final_oos_start_trade_date, plan.final_oos_end_trade_date


def _partition_summary(partition: GCPretrainingPartition, records: tuple[GCPretrainingCorpusRecord, ...], plan: GCPretrainingPartitionPlan) -> GCPretrainingPartitionSummary:
    start, end = _partition_bounds(partition, plan)
    contracts = tuple(sorted({record.contract for record in records}))
    material = {
        "version": GC_PRETRAINING_CORPUS_VERSION,
        "identity_kind": "PARTITION",
        "partition": partition,
        "start_trade_date": start,
        "end_trade_date": end,
        "record_ids": tuple(record.record_id for record in records),
        "contracts": contracts,
        "session_count": len({record.trade_date for record in records}),
        "candidate_count": len(records),
        "bullish_count": sum(record.direction is SMCV2Direction.BULLISH for record in records),
        "bearish_count": sum(record.direction is SMCV2Direction.BEARISH for record in records),
        "target_first_count": sum(record.outcome is GCLabelOutcome.TARGET_FIRST for record in records),
        "invalidation_first_count": sum(record.outcome is GCLabelOutcome.INVALIDATION_FIRST for record in records),
        "timeout_count": sum(record.outcome is GCLabelOutcome.TIMEOUT for record in records),
    }
    return GCPretrainingPartitionSummary(_sha(material), partition, start, end, material["record_ids"], contracts, material["session_count"], material["candidate_count"], material["bullish_count"], material["bearish_count"], material["target_first_count"], material["invalidation_first_count"], material["timeout_count"])


def _adequate(summary: GCPretrainingPartitionSummary) -> bool:
    threshold = {
        GCPretrainingPartition.TRAIN: (100, 2, 150, 30),
        GCPretrainingPartition.VALIDATION: (40, 1, 50, 10),
        GCPretrainingPartition.CALIBRATION: (40, 1, 50, 10),
    }[summary.partition]
    sessions, contracts, candidates, class_minimum = threshold
    negative = summary.invalidation_first_count + summary.timeout_count
    return (
        summary.session_count >= sessions
        and len(summary.contracts) >= contracts
        and summary.candidate_count >= candidates
        and summary.bullish_count >= class_minimum
        and summary.bearish_count >= class_minimum
        and summary.target_first_count >= class_minimum
        and negative >= class_minimum
    )


def build_gc_pretraining_corpus(
    *,
    dataset_config: GCDatasetBuildConfig | None,
    dataset_calendar_entries: tuple[KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...] | None,
    dataset_result: GCDatasetBuildResult | None,
    candidate_result: GCCandidateEvidenceResult | None,
    feature_label_result: GCFeatureLabelResult | None,
    source_registry: tuple[GCPretrainingSourceRecord, ...] | None,
    partition_plan: GCPretrainingPartitionPlan,
) -> GCPretrainingCorpusResult:
    """Reconcile immutable upstream evidence into a non-authoritative corpus."""

    try:
        plan = _validate_plan(partition_plan)
    except (TypeError, ValueError):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")

    supplied = (dataset_config, dataset_calendar_entries, dataset_result, candidate_result, feature_label_result, source_registry)
    missing = any(value is None for value in supplied)
    try:
        # Independently determinable evidence is validated even if a counterpart is absent.
        if dataset_result is not None and (dataset_config is None or dataset_calendar_entries is None):
            if type(dataset_result) is not GCDatasetBuildResult:
                raise TypeError("dataset_result has an invalid type")
            if dataset_result.status is not GCDatasetBuildStatus.NONE:
                raise ValueError("supplied dataset lacks identity-proof context")
        if dataset_config is not None:
            if type(dataset_config) is not GCDatasetBuildConfig:
                raise TypeError("dataset_config has an invalid type")
            if dataset_config.instrument != GC_PRETRAINING_INSTRUMENT or dataset_config.timeframe != GC_PRETRAINING_TIMEFRAME or dataset_config.tick_size != GC_PRETRAINING_TICK_SIZE:
                raise ValueError("dataset config contract mismatch")
        if dataset_calendar_entries is not None:
            _normalize_calendar(dataset_calendar_entries)
        if candidate_result is not None:
            if type(candidate_result) is not GCCandidateEvidenceResult:
                raise TypeError("candidate_result has an invalid type")
            inferred_dataset = None if candidate_result.manifest is None else candidate_result.manifest.dataset_id
            inferred_segments = tuple(item.segment_id for item in candidate_result.candidates) if type(candidate_result.candidates) is tuple else ()
            _validate_candidate(candidate_result, dataset_id=inferred_dataset, segment_ids=inferred_segments)
        if feature_label_result is not None:
            if type(feature_label_result) is not GCFeatureLabelResult:
                raise TypeError("feature_label_result has an invalid type")
            inferred_dataset = None if feature_label_result.manifest is None else feature_label_result.manifest.dataset_id
            _validate_feature_labels(feature_label_result, dataset_id=inferred_dataset)
        if source_registry is not None:
            if type(source_registry) is not tuple:
                raise TypeError("source_registry has an invalid type")
            if source_registry:
                first_source = source_registry[0]
                if type(first_source) is not GCPretrainingSourceRecord:
                    raise TypeError("source registry item has an invalid type")
                _validate_sources(source_registry, dataset_id=first_source.dataset_id, calendar_version=first_source.calendar_version, timezone_data_version=first_source.timezone_data_version)
    except (TypeError, ValueError):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    except Exception:
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    if missing:
        return _reason_result(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_TOP_LEVEL_CONTEXT")

    try:
        config, segments, dataset_manifest = _validate_dataset(dataset_config, dataset_calendar_entries, dataset_result)
        dataset_id = None if dataset_manifest is None else dataset_manifest.dataset_id
        candidates, candidate_manifest = _validate_candidate(candidate_result, dataset_id=dataset_id, segment_ids=tuple(segment.segment_id for segment in segments))
        rows, labels, feature_manifest = _validate_feature_labels(feature_label_result, dataset_id=dataset_id)
        calendar_version = "" if dataset_manifest is None else dataset_manifest.calendar_version
        timezone_version = config.timezone_data_version
        sources = _validate_sources(source_registry, dataset_id=dataset_id, calendar_version=calendar_version, timezone_data_version=timezone_version)
    except (TypeError, ValueError):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    except Exception:
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")

    if dataset_manifest is None:
        if candidates or rows or labels or sources or candidate_manifest is not None or feature_manifest is not None:
            return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
        return _reason_result(SMCV2PrimitiveStatus.NONE, "NO_ELIGIBLE_PRETRAINING_EVIDENCE")
    if candidate_manifest is None or feature_manifest is None:
        if candidates or rows or labels:
            return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
        return _reason_result(SMCV2PrimitiveStatus.NONE, "NO_ELIGIBLE_PRETRAINING_EVIDENCE")
    if candidate_manifest.calendar_version != dataset_manifest.calendar_version or candidate_manifest.timezone_data_version != dataset_manifest.timezone_data_version or feature_manifest.calendar_version != dataset_manifest.calendar_version or feature_manifest.timezone_data_version != dataset_manifest.timezone_data_version:
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    if len(candidates) != len(rows) or len(rows) != len(labels):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")

    source_map = {source.source_id: source for source in sources}
    emitted: list[GCPretrainingCorpusRecord] = []
    exclusions: dict[str, int] = {}
    contaminated = 0
    independence_unknown = False
    try:
        for candidate, row, label in zip(candidates, rows, labels):
            inducement = candidate.evidence.inducement
            if row.candidate_id != inducement.inducement_id or label.candidate_id != row.candidate_id:
                raise ValueError("candidate identity mismatch")
            if any((row.dataset_id != dataset_manifest.dataset_id, label.dataset_id != row.dataset_id, row.contract != label.contract, row.trade_date != label.trade_date, row.effective_index != label.effective_index, _moment(row.effective_timestamp, "row moment") != _moment(label.effective_timestamp, "label moment"))):
                raise ValueError("row/label correspondence mismatch")
            if inducement.confirmation_index != row.effective_index or _moment(inducement.confirmation_timestamp, "confirmation moment") != _moment(row.effective_timestamp, "row moment"):
                raise ValueError("candidate/row moment mismatch")
            if type(inducement.direction) is not SMCV2Direction:
                raise TypeError("candidate direction is invalid")
            partition = _partition_for(row.trade_date, plan)
            if partition is GCPretrainingPartition.FINAL_OOS:
                exclusions["FINAL_OOS_QUARANTINE"] = exclusions.get("FINAL_OOS_QUARANTINE", 0) + 1
                continue
            if partition is None:
                exclusions["EXCLUDED_DATE_INTERVAL"] = exclusions.get("EXCLUDED_DATE_INTERVAL", 0) + 1
                continue
            if label.outcome not in {GCLabelOutcome.TARGET_FIRST, GCLabelOutcome.INVALIDATION_FIRST, GCLabelOutcome.TIMEOUT}:
                exclusions[f"LABEL_{label.outcome.value}"] = exclusions.get(f"LABEL_{label.outcome.value}", 0) + 1
                continue
            if any(source_id not in source_map for source_id in row.source_ids):
                raise ValueError("row references an unavailable source")
            row_sources = tuple(source_map[source_id] for source_id in row.source_ids)
            if not row_sources or any(source.role is not GCPretrainingSourceRole.PRETRAINING_DEVELOPMENT_CANDIDATE for source in row_sources):
                exclusions["NON_DEVELOPMENT_SOURCE"] = exclusions.get("NON_DEVELOPMENT_SOURCE", 0) + 1
                continue
            if any(not (source.first_trade_date <= row.trade_date <= source.last_trade_date) or source.contract != row.contract for source in row_sources):
                raise ValueError("source coverage mismatch")
            evidence_ids = {row.candidate_id, row.row_id, label.label_id, *row.lineage_ids}
            if any(evidence_ids.intersection(source.contaminated_evidence_ids) for source in row_sources):
                contaminated += 1
                exclusions["CONTAMINATED_EVIDENCE"] = exclusions.get("CONTAMINATED_EVIDENCE", 0) + 1
                continue
            if any(not source.contamination_audit_complete for source in row_sources):
                independence_unknown = True
                exclusions["INDEPENDENCE_UNVERIFIED"] = exclusions.get("INDEPENDENCE_UNVERIFIED", 0) + 1
                continue
            record_id = _record_identity(partition, inducement.direction, row, label)
            emitted.append(GCPretrainingCorpusRecord(record_id, partition, inducement.direction, row.contract, row.trade_date, row.effective_index, _moment(row.effective_timestamp, "effective_timestamp"), row.dataset_id, row.candidate_id, row.row_id, label.label_id, label.outcome, row.feature_values, row.source_ids, row.lineage_ids))
    except (TypeError, ValueError):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    except Exception:
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")

    emitted.sort(key=lambda record: (_PARTITION_ORDER[record.partition.value], record.trade_date, record.effective_index, record.effective_timestamp, record.contract, record.direction.value, record.candidate_id, record.feature_row_id, record.label_id))
    if len({record.record_id for record in emitted}) != len(emitted):
        return _reason_result(SMCV2PrimitiveStatus.INVALID, "INVALID_PRETRAINING_CORPUS_EVIDENCE")
    records = tuple(emitted)
    summaries = tuple(_partition_summary(partition, tuple(record for record in records if record.partition is partition), plan) for partition in (GCPretrainingPartition.TRAIN, GCPretrainingPartition.VALIDATION, GCPretrainingPartition.CALIBRATION))
    plan_id = _sha({"version": GC_PRETRAINING_CORPUS_VERSION, "identity_kind": "PARTITION_PLAN", **{field.name: getattr(plan, field.name) for field in fields(plan)}})
    source_ids = tuple(source.source_id for source in sources)
    prior_ids = tuple(dict.fromkeys(identity for source in sources for identity in source.prior_run_manifest_ids))
    exclusion_counts = tuple(sorted(exclusions.items()))
    corpus_material = {
        "version": GC_PRETRAINING_CORPUS_VERSION,
        "identity_kind": "CORPUS",
        "dataset_id": dataset_manifest.dataset_id,
        "candidate_manifest_id": candidate_manifest.manifest_id,
        "feature_label_manifest_id": feature_manifest.manifest_id,
        "partition_plan_id": plan_id,
        "source_ids": source_ids,
        "prior_run_manifest_ids": prior_ids,
        "partition_ids": tuple(summary.partition_id for summary in summaries),
        "record_ids": tuple(record.record_id for record in records),
        "exclusion_counts": exclusion_counts,
        "excluded_record_count": sum(exclusions.values()),
        "contaminated_record_count": contaminated,
        "admitted_record_count": len(records),
        "final_oos_source_sha256": _FINAL_OOS_SHA256,
        "final_oos_start_trade_date": plan.final_oos_start_trade_date,
        "final_oos_end_trade_date": plan.final_oos_end_trade_date,
        "final_oos_payload_access_count": 0,
        "training_allowed": False,
        "oos_evaluation_allowed": False,
        "integration_allowed": False,
        "trading_allowed": False,
    }
    corpus_id = _sha(corpus_material)
    manifest_material = {
        **corpus_material,
        "identity_kind": "MANIFEST",
        "corpus_id": corpus_id,
        "instrument": GC_PRETRAINING_INSTRUMENT,
        "timeframe": GC_PRETRAINING_TIMEFRAME,
        "tick_size": GC_PRETRAINING_TICK_SIZE,
        "feature_schema_id": feature_manifest.feature_schema_id,
        "label_schema_id": feature_manifest.label_schema_id,
        "label_horizon_bars": feature_manifest.horizon_bars,
        "calendar_version": dataset_manifest.calendar_version,
        "timezone_data_version": dataset_manifest.timezone_data_version,
    }
    manifest = GCPretrainingCorpusManifest(_sha(manifest_material), corpus_id, GC_PRETRAINING_CORPUS_VERSION, GC_PRETRAINING_INSTRUMENT, GC_PRETRAINING_TIMEFRAME, GC_PRETRAINING_TICK_SIZE, dataset_manifest.dataset_id, candidate_manifest.manifest_id, feature_manifest.manifest_id, feature_manifest.feature_schema_id, feature_manifest.label_schema_id, feature_manifest.horizon_bars, dataset_manifest.calendar_version, dataset_manifest.timezone_data_version, plan_id, source_ids, prior_ids, corpus_material["partition_ids"], corpus_material["record_ids"], exclusion_counts, corpus_material["excluded_record_count"], contaminated, len(records), _FINAL_OOS_SHA256, plan.final_oos_start_trade_date, plan.final_oos_end_trade_date, 0, False, False, False, False)
    if independence_unknown:
        return _reason_result(SMCV2PrimitiveStatus.UNKNOWN, "INDEPENDENCE_UNVERIFIED", records=records, partitions=summaries, manifest=manifest)
    if not records:
        return _reason_result(SMCV2PrimitiveStatus.NONE, "NO_ELIGIBLE_PRETRAINING_EVIDENCE", partitions=summaries, manifest=manifest)
    if not all(_adequate(summary) for summary in summaries) or len({record.contract for record in records}) < 4:
        return _reason_result(SMCV2PrimitiveStatus.UNKNOWN, "INSUFFICIENT_PARTITION_EVIDENCE", records=records, partitions=summaries, manifest=manifest)
    return _reason_result(SMCV2PrimitiveStatus.VALID, "PRETRAINING_CORPUS_VALID", records=records, partitions=summaries, manifest=manifest)


__all__ = (
    "GC_PRETRAINING_CORPUS_VERSION",
    "GC_PRETRAINING_INSTRUMENT",
    "GC_PRETRAINING_TIMEFRAME",
    "GC_PRETRAINING_TICK_SIZE",
    "GC_PRETRAINING_LABEL_HORIZON_BARS",
    "GC_PRETRAINING_MINIMUM_EMBARGO_BARS",
    "GCPretrainingSourceRole",
    "GCPretrainingPartition",
    "GCPretrainingSourceRecord",
    "GCPretrainingPartitionPlan",
    "GCPretrainingCorpusRecord",
    "GCPretrainingPartitionSummary",
    "GCPretrainingCorpusManifest",
    "GCPretrainingCorpusResult",
    "build_gc_pretraining_corpus",
)
