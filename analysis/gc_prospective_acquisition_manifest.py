"""Pure validation for prospective GC raw-acquisition metadata.

The module accepts immutable caller-supplied metadata only.  It has no file,
network, current-clock, model, training, OOS, integration, or trading behavior.
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

from smc.smc_v2_primitives import SMCV2PrimitiveStatus


GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION: Final = "GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1"
GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID: Final = "GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1"
GC_PROSPECTIVE_ACQUISITION_COHORT_ID: Final = "GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1_20260901_20270301"
GC_PROSPECTIVE_ACQUISITION_INSTRUMENT: Final = "GC"
GC_PROSPECTIVE_ACQUISITION_VENUE: Final = "COMEX"
GC_PROSPECTIVE_ACQUISITION_TIMEFRAME: Final = "5M"
GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT: Final = "1 Tick"
GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE: Final = "Asia/Tokyo"
GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE: Final = "America/New_York"
GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD: Final = 220

_UTC = timezone.utc
_DECISION_TIMESTAMP = datetime(2026, 8, 31, 8, 17, 34, tzinfo=_UTC)
_COHORT_START = date(2026, 9, 1)
_COHORT_END = date(2027, 3, 1)
_CAPTURE_START = datetime(2027, 3, 2, tzinfo=_UTC)
_CAPTURE_END = datetime(2027, 3, 9, tzinfo=_UTC)
_PROVIDER = "SIERRA_CHART_HISTORICAL_INTRADAY_DATA"
_TIMEZONE_DATA_VERSION = "tzdata-2026a"
_SOURCE_SCHEMA_ID = "GC_SIERRA_5M_TICK_EXPORT_V1"
_GOVERNING_DECISION_COMMIT = "076d134785695b3b36f88910dbcdd5ea77866d5d"
_GOVERNING_PROPOSAL_SHA256 = "fa4af7ddd77d5e75ae82988aebd5fe98a55b514c2d063c8012ad95ca4335f3b5"
_GOVERNING_HASHES = (
    ("prospective_acquisition_manifest_schedule_proposal", _GOVERNING_PROPOSAL_SHA256),
    ("prospective_acquisition_first_decision", "966521b3fd0e945c8b5dc524fce2752324d4ec968e4e09c10284851cf3e8455b"),
    ("post_resolver_pretraining_readiness_decision", "f344b32a9b3b923ec79f4f96519501d93bf00e4f67eda1012c8f382991366296"),
    ("terminal_cross_segment_resolver_outcome", "107df12717c0afc60ba89d1721c02a77e1bd2631bb3c19fa5ffbeef7330eb67d"),
    ("gc_ai_strategy_and_training_decision", "237655d31c54133e6e3ae49db59cd3ec32d5b5d3fc436ee476fa00dcd4629688"),
)
_PURPOSE = "PROSPECTIVE_RAW_ACQUISITION_ONLY"
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_CONTRACT_RE = re.compile(r"^GC([GJMQVZ])(\d{2})-COMEX$")
_MONTH_ORDER = {code: index for index, code in enumerate(("G", "J", "M", "Q", "V", "Z"))}
_IDENTITY_KINDS = frozenset({"CONFIG", "ROSTER", "SOURCE", "PROVIDER_LOG", "CALENDAR", "CONTAMINATION", "MANIFEST", "ARTIFACT_SET"})
_OFFICIAL_CALENDAR_KINDS = frozenset({"CME_STRUCTURED_TRADING_HOURS", "CME_OFFICIAL_NOTICE"})
_ALLOWED_CALENDAR_KINDS = _OFFICIAL_CALENDAR_KINDS | {"CME_GCC_CLARIFICATION"}
_REASON_ORDER = (
    "INVALID_AUTHORITY_OR_PURPOSE_DRIFT",
    "INVALID_CONFIGURATION",
    "INVALID_ROSTER_EVIDENCE",
    "INVALID_SOURCE_METADATA",
    "INVALID_PROVIDER_LOG_EVIDENCE",
    "INVALID_CALENDAR_EVIDENCE",
    "INVALID_PRIOR_OUTCOME_CONTACT",
    "INVALID_IDENTITY_OR_CONSERVATION",
    "AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY",
    "MISSING_TOP_LEVEL_CONTEXT",
    "UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE",
    "UNKNOWN_PROVIDER_LOG_INCOMPLETE",
    "UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE",
    "UNKNOWN_CONTAMINATION_HISTORY",
    "UNKNOWN_ACQUISITION_WINDOW_EXPIRED",
    "VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY",
)
_INVALID_REASONS = frozenset(_REASON_ORDER[:8])
_AMBIGUOUS_REASONS = frozenset({_REASON_ORDER[8]})
_UNKNOWN_REASONS = frozenset(_REASON_ORDER[9:15])


class GCProspectiveAcquisitionSourceRole(str, Enum):
    PREDECESSOR_CONTEXT = "PREDECESSOR_CONTEXT"
    COHORT_CANDIDATE = "COHORT_CANDIDATE"
    SUCCESSOR_CONTEXT = "SUCCESSOR_CONTEXT"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class GCProspectiveAcquisitionConfig:
    decision_timestamp: datetime
    cohort_start_trade_date: date
    cohort_end_trade_date: date
    capture_window_start_timestamp: datetime
    capture_window_end_timestamp: datetime
    provider: str
    instrument: str
    venue: str
    timeframe: str
    storage_time_unit: str
    maximum_historical_days_to_download: int
    chart_timezone: str
    exchange_timezone: str
    timezone_data_version: str
    governing_proposal_sha256: str


@dataclass(frozen=True)
class GCProspectiveContractRosterRecord:
    roster_record_id: str
    contract: str
    role: GCProspectiveAcquisitionSourceRole
    delivery_order: int
    listing_source_id: str
    listing_source_sha256: str
    inclusion_reason: str


@dataclass(frozen=True)
class GCProspectiveAcquisitionSourceRecord:
    source_id: str
    source_name: str
    source_sha256: str
    byte_count: int
    row_count: int
    contract: str
    role: GCProspectiveAcquisitionSourceRole
    capture_timestamp: datetime
    acquisition_completed_timestamp: datetime
    completed_data_cutoff_timestamp: datetime
    first_source_timestamp: datetime
    last_source_timestamp: datetime
    first_trade_date: date
    last_trade_date: date
    provider_log_id: str
    calendar_evidence_ids: tuple[str, ...]
    chart_timezone: str
    timeframe: str
    storage_time_unit: str
    schema_id: str
    ordering_digest: str
    validation_status: SMCV2PrimitiveStatus
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class GCProspectiveProviderLogRecord:
    provider_log_id: str
    provider: str
    contract: str
    requested_start_timestamp: datetime
    requested_end_timestamp: datetime
    received_start_timestamp: datetime
    received_end_timestamp: datetime
    received_record_count: int
    completion_timestamp: datetime
    completion_status: str
    log_artifact_sha256: str


@dataclass(frozen=True)
class GCProspectiveCalendarEvidenceRecord:
    calendar_evidence_id: str
    calendar_version: str
    source_kind: str
    source_reference: str
    source_sha256: str
    retrieval_timestamp: datetime
    first_trade_date: date
    last_trade_date: date
    exchange_timezone: str
    normalized_row_digest: str
    authoritative: bool


@dataclass(frozen=True)
class GCProspectiveContaminationRecord:
    contamination_record_id: str
    evidence_id: str
    evidence_kind: str
    first_trade_date: date
    last_trade_date: date
    outcome_contacted: bool
    overlaps_cohort: bool
    exclusion_reason: str
    evidence_sha256: str


@dataclass(frozen=True)
class GCProspectiveAcquisitionManifest:
    manifest_id: str
    version: str
    program_id: str
    cohort_id: str
    purpose: str
    governing_commit: str
    governing_hashes: tuple[tuple[str, str], ...]
    config_id: str
    roster_record_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    provider_log_ids: tuple[str, ...]
    calendar_evidence_ids: tuple[str, ...]
    contamination_record_ids: tuple[str, ...]
    requested_source_count: int
    admitted_source_count: int
    excluded_source_count: int
    reason_counts: tuple[tuple[str, int], ...]
    artifact_set_identity: str
    outcome_contact_count: int
    final_oos_payload_access_count: int
    candidate_build_allowed: bool
    feature_label_build_allowed: bool
    corpus_build_allowed: bool
    training_allowed: bool
    oos_evaluation_allowed: bool
    integration_allowed: bool
    trading_allowed: bool


@dataclass(frozen=True)
class GCProspectiveAcquisitionResult:
    status: SMCV2PrimitiveStatus
    manifest: GCProspectiveAcquisitionManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


def _text(value: object, name: str) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise TypeError(f"{name} must be a nonempty canonical str")
    return value


def _integer(value: object, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise TypeError(f"{name} must be an int at or above its minimum")
    return value


def _boolean(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be bool")
    return value


def _hash(value: object, name: str) -> str:
    if type(value) is not str or _HASH_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _day(value: object, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be date")
    return value


def _moment(value: object, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be an aware datetime")
    if value.utcoffset() != timedelta(0):
        raise ValueError(f"{name} must be UTC")
    return value.astimezone(_UTC)


def _tuple(value: object, name: str) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be tuple")
    return value


def _decimal_text(value: Decimal) -> str:
    if not value.is_finite():
        raise TypeError("Decimal must be finite")
    output = format(value, "f")
    if "." in output:
        output = output.rstrip("0").rstrip(".")
    return output or "0"


def _canonical(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if type(value) is Decimal:
        return _decimal_text(value)
    if type(value) is datetime:
        return _moment(value, "identity timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")
    if type(value) is date:
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("identity mapping keys must be str")
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported identity value {type(value).__name__}")


def make_gc_prospective_acquisition_id(kind: str, payload: object) -> str:
    """Return a namespaced deterministic identity for public metadata."""

    if type(kind) is not str or kind not in _IDENTITY_KINDS:
        raise ValueError("unknown prospective acquisition identity kind")
    material = {
        "version": GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION,
        "identity_kind": kind,
        "payload": _canonical(payload),
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _without_id(value: object, omitted: str) -> dict[str, object]:
    return {field.name: getattr(value, field.name) for field in fields(value) if field.name != omitted}


def _record_identity(kind: str, value: object, omitted: str) -> str:
    return make_gc_prospective_acquisition_id(kind, _without_id(value, omitted))


def _contract_order(contract: object) -> int:
    text = _text(contract, "contract")
    match = _CONTRACT_RE.fullmatch(text)
    if match is None:
        raise ValueError("contract does not match the GC outright domain")
    return (2000 + int(match.group(2))) * 6 + _MONTH_ORDER[match.group(1)]


def _ordered_reasons(reasons: set[str]) -> tuple[str, ...]:
    return tuple(reason for reason in _REASON_ORDER if reason in reasons)


def _has_duplicates(values: tuple[object, ...]) -> bool:
    return len(values) != len(set(values))


def _dates_covered(start: date, end_inclusive: date, evidence: tuple[GCProspectiveCalendarEvidenceRecord, ...]) -> bool:
    current = start
    while current <= end_inclusive:
        if not any(item.first_trade_date <= current <= item.last_trade_date for item in evidence):
            return False
        current += timedelta(days=1)
    return True


def _result(reasons: set[str], manifest: GCProspectiveAcquisitionManifest | None) -> GCProspectiveAcquisitionResult:
    ordered = _ordered_reasons(reasons)
    if any(reason in _INVALID_REASONS for reason in ordered):
        status = SMCV2PrimitiveStatus.INVALID
    elif any(reason in _AMBIGUOUS_REASONS for reason in ordered):
        status = SMCV2PrimitiveStatus.AMBIGUOUS
    elif any(reason in _UNKNOWN_REASONS for reason in ordered):
        status = SMCV2PrimitiveStatus.UNKNOWN
    else:
        status = SMCV2PrimitiveStatus.VALID
        ordered = ("VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY",)
    returned_manifest = manifest if status is SMCV2PrimitiveStatus.VALID else None
    blocking = () if status is SMCV2PrimitiveStatus.VALID else ordered
    return GCProspectiveAcquisitionResult(status, returned_manifest, ordered, blocking)


def validate_gc_prospective_acquisition_manifest(
    *,
    config: GCProspectiveAcquisitionConfig | None,
    contract_roster: tuple[GCProspectiveContractRosterRecord, ...] | None,
    sources: tuple[GCProspectiveAcquisitionSourceRecord, ...] | None,
    provider_logs: tuple[GCProspectiveProviderLogRecord, ...] | None,
    calendar_evidence: tuple[GCProspectiveCalendarEvidenceRecord, ...] | None,
    contamination_records: tuple[GCProspectiveContaminationRecord, ...] | None,
    manifest: GCProspectiveAcquisitionManifest | None,
) -> GCProspectiveAcquisitionResult:
    """Validate one immutable raw-acquisition metadata graph fail-closed."""

    reasons: set[str] = set()
    if any(value is None for value in (config, contract_roster, sources, provider_logs, calendar_evidence, contamination_records, manifest)):
        reasons.add("MISSING_TOP_LEVEL_CONTEXT")

    valid_config: GCProspectiveAcquisitionConfig | None = None
    if config is None:
        pass
    elif type(config) is not GCProspectiveAcquisitionConfig:
        reasons.add("INVALID_CONFIGURATION")
    else:
        try:
            if any(
                (
                    _moment(config.decision_timestamp, "decision_timestamp") != _DECISION_TIMESTAMP,
                    _day(config.cohort_start_trade_date, "cohort_start_trade_date") != _COHORT_START,
                    _day(config.cohort_end_trade_date, "cohort_end_trade_date") != _COHORT_END,
                    _moment(config.capture_window_start_timestamp, "capture_window_start_timestamp") != _CAPTURE_START,
                    _moment(config.capture_window_end_timestamp, "capture_window_end_timestamp") != _CAPTURE_END,
                    _text(config.provider, "provider") != _PROVIDER,
                    _text(config.instrument, "instrument") != GC_PROSPECTIVE_ACQUISITION_INSTRUMENT,
                    _text(config.venue, "venue") != GC_PROSPECTIVE_ACQUISITION_VENUE,
                    _text(config.timeframe, "timeframe") != GC_PROSPECTIVE_ACQUISITION_TIMEFRAME,
                    _text(config.storage_time_unit, "storage_time_unit") != GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT,
                    _integer(config.maximum_historical_days_to_download, "maximum_historical_days_to_download", minimum=1) != GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD,
                    _text(config.chart_timezone, "chart_timezone") != GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE,
                    _text(config.exchange_timezone, "exchange_timezone") != GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE,
                    _text(config.timezone_data_version, "timezone_data_version") != _TIMEZONE_DATA_VERSION,
                    _hash(config.governing_proposal_sha256, "governing_proposal_sha256") != _GOVERNING_PROPOSAL_SHA256,
                )
            ):
                raise ValueError("configuration drift")
            valid_config = config
        except (TypeError, ValueError):
            reasons.add("INVALID_CONFIGURATION")

    roster_items: list[GCProspectiveContractRosterRecord] = []
    if contract_roster is None:
        reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
    elif type(contract_roster) is not tuple:
        reasons.add("INVALID_ROSTER_EVIDENCE")
    else:
        for item in contract_roster:
            try:
                if type(item) is not GCProspectiveContractRosterRecord:
                    raise TypeError("roster item type")
                expected_order = _contract_order(item.contract)
                if type(item.role) is not GCProspectiveAcquisitionSourceRole:
                    raise TypeError("roster role")
                if _integer(item.delivery_order, "delivery_order") != expected_order:
                    raise ValueError("delivery order")
                _text(item.listing_source_id, "listing_source_id")
                _hash(item.listing_source_sha256, "listing_source_sha256")
                _text(item.inclusion_reason, "inclusion_reason")
                if _hash(item.roster_record_id, "roster_record_id") != _record_identity("ROSTER", item, "roster_record_id"):
                    raise ValueError("roster identity")
                roster_items.append(item)
            except (TypeError, ValueError):
                reasons.add("INVALID_ROSTER_EVIDENCE")
        if roster_items:
            for values in (
                tuple(item.contract for item in roster_items),
                tuple(item.roster_record_id for item in roster_items),
                tuple(item.delivery_order for item in roster_items),
                tuple(item.listing_source_id for item in roster_items),
                tuple(item.listing_source_sha256 for item in roster_items),
            ):
                if _has_duplicates(values):
                    reasons.add("INVALID_ROSTER_EVIDENCE")
        roles = {item.role for item in roster_items}
        if not {
            GCProspectiveAcquisitionSourceRole.PREDECESSOR_CONTEXT,
            GCProspectiveAcquisitionSourceRole.COHORT_CANDIDATE,
            GCProspectiveAcquisitionSourceRole.SUCCESSOR_CONTEXT,
        }.issubset(roles):
            reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
    ordered_roster = tuple(sorted(roster_items, key=lambda item: (item.delivery_order, item.contract, item.roster_record_id)))
    roster_by_contract = {item.contract: item for item in ordered_roster}

    calendar_items: list[GCProspectiveCalendarEvidenceRecord] = []
    if calendar_evidence is None:
        reasons.add("UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE")
    elif type(calendar_evidence) is not tuple:
        reasons.add("INVALID_CALENDAR_EVIDENCE")
    else:
        for item in calendar_evidence:
            try:
                if type(item) is not GCProspectiveCalendarEvidenceRecord:
                    raise TypeError("calendar item type")
                _text(item.calendar_version, "calendar_version")
                if _text(item.source_kind, "source_kind") not in _ALLOWED_CALENDAR_KINDS:
                    raise ValueError("calendar kind")
                _text(item.source_reference, "source_reference")
                _hash(item.source_sha256, "source_sha256")
                _moment(item.retrieval_timestamp, "retrieval_timestamp")
                first = _day(item.first_trade_date, "first_trade_date")
                last = _day(item.last_trade_date, "last_trade_date")
                if first > last:
                    raise ValueError("calendar interval")
                if _text(item.exchange_timezone, "exchange_timezone") != GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE:
                    raise ValueError("calendar timezone")
                _hash(item.normalized_row_digest, "normalized_row_digest")
                if not _boolean(item.authoritative, "authoritative"):
                    raise ValueError("calendar authority")
                if _hash(item.calendar_evidence_id, "calendar_evidence_id") != _record_identity("CALENDAR", item, "calendar_evidence_id"):
                    raise ValueError("calendar identity")
                calendar_items.append(item)
            except (TypeError, ValueError):
                reasons.add("INVALID_CALENDAR_EVIDENCE")
        if _has_duplicates(tuple(item.calendar_evidence_id for item in calendar_items)):
            reasons.add("INVALID_CALENDAR_EVIDENCE")
        for index, left in enumerate(calendar_items):
            for right in calendar_items[index + 1 :]:
                overlaps = left.first_trade_date <= right.last_trade_date and right.first_trade_date <= left.last_trade_date
                conflicts = (
                    left.source_kind == right.source_kind
                    and (left.calendar_version, left.normalized_row_digest, left.exchange_timezone)
                    != (right.calendar_version, right.normalized_row_digest, right.exchange_timezone)
                )
                if overlaps and conflicts:
                    reasons.add("AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY")
    ordered_calendars = tuple(sorted(calendar_items, key=lambda item: (item.first_trade_date, item.last_trade_date, item.source_kind, item.calendar_evidence_id)))
    calendar_by_id = {item.calendar_evidence_id: item for item in ordered_calendars}
    official_calendars = tuple(item for item in ordered_calendars if item.source_kind in _OFFICIAL_CALENDAR_KINDS and item.authoritative)
    if not official_calendars or not _dates_covered(_COHORT_START, _COHORT_END - timedelta(days=1), official_calendars):
        reasons.add("UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE")

    source_items: list[GCProspectiveAcquisitionSourceRecord] = []
    if sources is None:
        reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
    elif type(sources) is not tuple:
        reasons.add("INVALID_SOURCE_METADATA")
    else:
        for item in sources:
            try:
                if type(item) is not GCProspectiveAcquisitionSourceRecord:
                    raise TypeError("source item type")
                _text(item.source_name, "source_name")
                _hash(item.source_sha256, "source_sha256")
                _integer(item.byte_count, "byte_count")
                _integer(item.row_count, "row_count")
                _contract_order(item.contract)
                if type(item.role) is not GCProspectiveAcquisitionSourceRole or item.role is GCProspectiveAcquisitionSourceRole.EXCLUDED:
                    raise TypeError("source role")
                capture = _moment(item.capture_timestamp, "capture_timestamp")
                completed = _moment(item.acquisition_completed_timestamp, "acquisition_completed_timestamp")
                cutoff = _moment(item.completed_data_cutoff_timestamp, "completed_data_cutoff_timestamp")
                first_moment = _moment(item.first_source_timestamp, "first_source_timestamp")
                last_moment = _moment(item.last_source_timestamp, "last_source_timestamp")
                first_day = _day(item.first_trade_date, "first_trade_date")
                last_day = _day(item.last_trade_date, "last_trade_date")
                if not (_CAPTURE_START <= capture < _CAPTURE_END):
                    raise ValueError("capture window")
                if not (first_moment <= last_moment <= cutoff <= completed <= capture) or first_day > last_day:
                    raise ValueError("source ordering")
                if not (_CAPTURE_START <= completed < _CAPTURE_END):
                    reasons.add("UNKNOWN_ACQUISITION_WINDOW_EXPIRED")
                roster_item = roster_by_contract.get(item.contract)
                if roster_item is not None and roster_item.role is GCProspectiveAcquisitionSourceRole.EXCLUDED:
                    reasons.add("INVALID_ROSTER_EVIDENCE")
                    raise ValueError("excluded roster source")
                if roster_item is None or roster_item.role is not item.role:
                    raise ValueError("roster membership")
                _hash(item.provider_log_id, "provider_log_id")
                calendar_ids = _tuple(item.calendar_evidence_ids, "calendar_evidence_ids")
                if not calendar_ids or _has_duplicates(calendar_ids) or any(type(identity) is not str or _HASH_RE.fullmatch(identity) is None for identity in calendar_ids):
                    raise ValueError("calendar identities")
                if _text(item.chart_timezone, "chart_timezone") != GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE:
                    raise ValueError("chart timezone")
                if _text(item.timeframe, "timeframe") != GC_PROSPECTIVE_ACQUISITION_TIMEFRAME:
                    raise ValueError("timeframe")
                if _text(item.storage_time_unit, "storage_time_unit") != GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT:
                    raise ValueError("storage unit")
                if _text(item.schema_id, "schema_id") != _SOURCE_SCHEMA_ID:
                    raise ValueError("source schema")
                _hash(item.ordering_digest, "ordering_digest")
                if type(item.validation_status) is not SMCV2PrimitiveStatus:
                    raise TypeError("validation status")
                source_reasons = _tuple(item.reasons, "reasons")
                if any(type(reason) is not str or not reason for reason in source_reasons) or _has_duplicates(source_reasons) or source_reasons != tuple(sorted(source_reasons)):
                    raise ValueError("source reasons")
                if _hash(item.source_id, "source_id") != _record_identity("SOURCE", item, "source_id"):
                    raise ValueError("source identity")
                source_items.append(item)
                if item.byte_count == 0 or item.row_count == 0:
                    reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
                if item.validation_status is SMCV2PrimitiveStatus.INVALID:
                    reasons.add("INVALID_SOURCE_METADATA")
                elif item.validation_status is SMCV2PrimitiveStatus.AMBIGUOUS:
                    reasons.add("AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY")
                elif item.validation_status in {SMCV2PrimitiveStatus.UNKNOWN, SMCV2PrimitiveStatus.NONE}:
                    reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
            except (TypeError, ValueError):
                reasons.add("INVALID_SOURCE_METADATA")
        for values in (
            tuple(item.source_name for item in source_items),
            tuple(item.source_id for item in source_items),
            tuple(item.source_sha256 for item in source_items),
        ):
            if _has_duplicates(values):
                reasons.add("INVALID_SOURCE_METADATA")
    roster_order = {item.contract: item.delivery_order for item in ordered_roster}
    ordered_sources = tuple(sorted(source_items, key=lambda item: (roster_order.get(item.contract, 10**9), item.source_name, item.source_id)))
    source_contracts = {item.contract for item in ordered_sources}
    for roster_item in ordered_roster:
        if roster_item.role is GCProspectiveAcquisitionSourceRole.EXCLUDED:
            if roster_item.contract in source_contracts:
                reasons.add("INVALID_ROSTER_EVIDENCE")
        elif roster_item.contract not in source_contracts:
            reasons.add("UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE")
    for source in ordered_sources:
        referenced = tuple(calendar_by_id[identity] for identity in source.calendar_evidence_ids if identity in calendar_by_id)
        if len(referenced) != len(source.calendar_evidence_ids):
            reasons.add("UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE")
        official_referenced = tuple(item for item in referenced if item.source_kind in _OFFICIAL_CALENDAR_KINDS and item.authoritative)
        if not official_referenced or not _dates_covered(source.first_trade_date, source.last_trade_date, official_referenced):
            reasons.add("UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE")

    log_items: list[GCProspectiveProviderLogRecord] = []
    if provider_logs is None:
        reasons.add("UNKNOWN_PROVIDER_LOG_INCOMPLETE")
    elif type(provider_logs) is not tuple:
        reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")
    else:
        for item in provider_logs:
            try:
                if type(item) is not GCProspectiveProviderLogRecord:
                    raise TypeError("provider log item type")
                if _text(item.provider, "provider") != _PROVIDER:
                    raise ValueError("provider")
                _contract_order(item.contract)
                requested_start = _moment(item.requested_start_timestamp, "requested_start_timestamp")
                requested_end = _moment(item.requested_end_timestamp, "requested_end_timestamp")
                received_start = _moment(item.received_start_timestamp, "received_start_timestamp")
                received_end = _moment(item.received_end_timestamp, "received_end_timestamp")
                completion = _moment(item.completion_timestamp, "completion_timestamp")
                _integer(item.received_record_count, "received_record_count")
                status = _text(item.completion_status, "completion_status")
                _hash(item.log_artifact_sha256, "log_artifact_sha256")
                if not (requested_start < requested_end and requested_start <= received_start <= received_end <= requested_end and received_end <= completion):
                    raise ValueError("provider interval")
                if _hash(item.provider_log_id, "provider_log_id") != _record_identity("PROVIDER_LOG", item, "provider_log_id"):
                    raise ValueError("provider log identity")
                log_items.append(item)
                if not (_CAPTURE_START <= completion < _CAPTURE_END):
                    reasons.add("UNKNOWN_ACQUISITION_WINDOW_EXPIRED")
                if status != "COMPLETE":
                    reasons.add("UNKNOWN_PROVIDER_LOG_INCOMPLETE")
            except (TypeError, ValueError):
                reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")
        if _has_duplicates(tuple(item.provider_log_id for item in log_items)):
            reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")
    ordered_logs = tuple(sorted(log_items, key=lambda item: (item.contract, item.provider_log_id)))
    logs_by_id = {item.provider_log_id: item for item in ordered_logs}
    bound_logs: list[str] = []
    for source in ordered_sources:
        log = logs_by_id.get(source.provider_log_id)
        if log is None:
            reasons.add("UNKNOWN_PROVIDER_LOG_INCOMPLETE")
            continue
        bound_logs.append(log.provider_log_id)
        if any(
            (
                log.contract != source.contract,
                log.received_record_count != source.row_count,
                log.received_start_timestamp != source.first_source_timestamp,
                log.received_end_timestamp != source.last_source_timestamp,
                log.completion_timestamp != source.acquisition_completed_timestamp,
            )
        ):
            reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")
    if len(bound_logs) != len(set(bound_logs)):
        reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")
    if sources is not None and type(sources) is tuple and set(logs_by_id) - set(bound_logs):
        reasons.add("INVALID_PROVIDER_LOG_EVIDENCE")

    contamination_items: list[GCProspectiveContaminationRecord] = []
    if contamination_records is None:
        reasons.add("UNKNOWN_CONTAMINATION_HISTORY")
    elif type(contamination_records) is not tuple:
        reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
    elif not contamination_records:
        reasons.add("UNKNOWN_CONTAMINATION_HISTORY")
    else:
        for item in contamination_records:
            try:
                if type(item) is not GCProspectiveContaminationRecord:
                    raise TypeError("contamination item type")
                _text(item.evidence_id, "evidence_id")
                _text(item.evidence_kind, "evidence_kind")
                first = _day(item.first_trade_date, "first_trade_date")
                last = _day(item.last_trade_date, "last_trade_date")
                contacted = _boolean(item.outcome_contacted, "outcome_contacted")
                declared_overlap = _boolean(item.overlaps_cohort, "overlaps_cohort")
                _text(item.exclusion_reason, "exclusion_reason")
                _hash(item.evidence_sha256, "evidence_sha256")
                if first > last:
                    raise ValueError("contamination interval")
                actual_overlap = first < _COHORT_END and last >= _COHORT_START
                if actual_overlap and not declared_overlap:
                    reasons.add("UNKNOWN_CONTAMINATION_HISTORY")
                elif declared_overlap and not actual_overlap:
                    raise ValueError("contamination overlap contradiction")
                if contacted and (declared_overlap or actual_overlap):
                    reasons.add("INVALID_PRIOR_OUTCOME_CONTACT")
                if _hash(item.contamination_record_id, "contamination_record_id") != _record_identity("CONTAMINATION", item, "contamination_record_id"):
                    raise ValueError("contamination identity")
                contamination_items.append(item)
            except (TypeError, ValueError):
                reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
        if _has_duplicates(tuple(item.contamination_record_id for item in contamination_items)) or _has_duplicates(tuple(item.evidence_id for item in contamination_items)):
            reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
    ordered_contamination = tuple(sorted(contamination_items, key=lambda item: (item.first_trade_date, item.last_trade_date, item.evidence_id, item.contamination_record_id)))

    valid_manifest: GCProspectiveAcquisitionManifest | None = None
    if manifest is None:
        pass
    elif type(manifest) is not GCProspectiveAcquisitionManifest:
        reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
    else:
        try:
            authority_values = (
                manifest.candidate_build_allowed,
                manifest.feature_label_build_allowed,
                manifest.corpus_build_allowed,
                manifest.training_allowed,
                manifest.oos_evaluation_allowed,
                manifest.integration_allowed,
                manifest.trading_allowed,
            )
            if any(type(value) is not bool or value for value in authority_values):
                reasons.add("INVALID_AUTHORITY_OR_PURPOSE_DRIFT")
            if any(
                (
                    manifest.version != GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION,
                    manifest.program_id != GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID,
                    manifest.cohort_id != GC_PROSPECTIVE_ACQUISITION_COHORT_ID,
                    manifest.purpose != _PURPOSE,
                    type(manifest.outcome_contact_count) is not int or manifest.outcome_contact_count != 0,
                    type(manifest.final_oos_payload_access_count) is not int or manifest.final_oos_payload_access_count != 0,
                )
            ):
                reasons.add("INVALID_AUTHORITY_OR_PURPOSE_DRIFT")
            if (
                type(manifest.governing_commit) is not str
                or _COMMIT_RE.fullmatch(manifest.governing_commit) is None
                or manifest.governing_commit != _GOVERNING_DECISION_COMMIT
            ):
                reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
            if manifest.governing_hashes != _GOVERNING_HASHES:
                reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
            for identity in (
                manifest.config_id,
                manifest.artifact_set_identity,
                manifest.manifest_id,
                *manifest.roster_record_ids,
                *manifest.source_ids,
                *manifest.provider_log_ids,
                *manifest.calendar_evidence_ids,
                *manifest.contamination_record_ids,
            ):
                _hash(identity, "manifest identity")
            for count in (
                manifest.requested_source_count,
                manifest.admitted_source_count,
                manifest.excluded_source_count,
                manifest.outcome_contact_count,
                manifest.final_oos_payload_access_count,
            ):
                _integer(count, "manifest count")
            _tuple(manifest.governing_hashes, "governing_hashes")
            _tuple(manifest.roster_record_ids, "roster_record_ids")
            _tuple(manifest.source_ids, "source_ids")
            _tuple(manifest.provider_log_ids, "provider_log_ids")
            _tuple(manifest.calendar_evidence_ids, "calendar_evidence_ids")
            _tuple(manifest.contamination_record_ids, "contamination_record_ids")
            reason_counts = _tuple(manifest.reason_counts, "reason_counts")
            if any(type(item) is not tuple or len(item) != 2 or type(item[0]) is not str or type(item[1]) is not int or item[1] < 0 for item in reason_counts):
                raise ValueError("reason counts")
            if (
                tuple(sorted(reason_counts)) != reason_counts
                or _has_duplicates(tuple(item[0] for item in reason_counts))
                or any(item[1] == 0 for item in reason_counts)
                or any(
                    _has_duplicates(getattr(manifest, name))
                    for name in (
                        "roster_record_ids",
                        "source_ids",
                        "provider_log_ids",
                        "calendar_evidence_ids",
                        "contamination_record_ids",
                    )
                )
                or manifest.requested_source_count
                != manifest.admitted_source_count + manifest.excluded_source_count
            ):
                raise ValueError("manifest conservation")
            if _hash(manifest.manifest_id, "manifest_id") != _record_identity("MANIFEST", manifest, "manifest_id"):
                reasons.add("INVALID_IDENTITY_OR_CONSERVATION")
            valid_manifest = manifest
        except (TypeError, ValueError):
            reasons.add("INVALID_IDENTITY_OR_CONSERVATION")

    if valid_manifest is not None and all(value is not None for value in (valid_config, contract_roster, sources, provider_logs, calendar_evidence, contamination_records)):
        expected_config_id = make_gc_prospective_acquisition_id("CONFIG", valid_config)
        expected_roster_ids = tuple(item.roster_record_id for item in ordered_roster)
        expected_source_ids = tuple(item.source_id for item in ordered_sources)
        expected_log_ids = tuple(item.provider_log_id for item in ordered_logs)
        expected_calendar_ids = tuple(item.calendar_evidence_id for item in ordered_calendars)
        expected_contamination_ids = tuple(item.contamination_record_id for item in ordered_contamination)
        expected_artifact_set = make_gc_prospective_acquisition_id(
            "ARTIFACT_SET",
            {
                "config_id": expected_config_id,
                "roster_record_ids": expected_roster_ids,
                "source_ids": expected_source_ids,
                "provider_log_ids": expected_log_ids,
                "calendar_evidence_ids": expected_calendar_ids,
                "contamination_record_ids": expected_contamination_ids,
            },
        )
        reason_count_map: dict[str, int] = {}
        for source in ordered_sources:
            for source_reason in source.reasons:
                reason_count_map[source_reason] = reason_count_map.get(source_reason, 0) + 1
        expected_reason_counts = tuple(sorted(reason_count_map.items()))
        expected_excluded = sum(item.role is GCProspectiveAcquisitionSourceRole.EXCLUDED for item in ordered_roster)
        expected_outcome_contact = sum(item.outcome_contacted for item in ordered_contamination)
        if any(
            (
                valid_manifest.config_id != expected_config_id,
                valid_manifest.roster_record_ids != expected_roster_ids,
                valid_manifest.source_ids != expected_source_ids,
                valid_manifest.provider_log_ids != expected_log_ids,
                valid_manifest.calendar_evidence_ids != expected_calendar_ids,
                valid_manifest.contamination_record_ids != expected_contamination_ids,
                valid_manifest.requested_source_count != len(ordered_roster),
                valid_manifest.admitted_source_count != len(ordered_sources),
                valid_manifest.excluded_source_count != expected_excluded,
                valid_manifest.requested_source_count != valid_manifest.admitted_source_count + valid_manifest.excluded_source_count,
                valid_manifest.reason_counts != expected_reason_counts,
                valid_manifest.artifact_set_identity != expected_artifact_set,
                valid_manifest.outcome_contact_count != expected_outcome_contact,
            )
        ):
            reasons.add("INVALID_IDENTITY_OR_CONSERVATION")

    return _result(reasons, valid_manifest)


__all__ = (
    "GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION",
    "GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID",
    "GC_PROSPECTIVE_ACQUISITION_COHORT_ID",
    "GC_PROSPECTIVE_ACQUISITION_INSTRUMENT",
    "GC_PROSPECTIVE_ACQUISITION_VENUE",
    "GC_PROSPECTIVE_ACQUISITION_TIMEFRAME",
    "GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT",
    "GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE",
    "GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE",
    "GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD",
    "GCProspectiveAcquisitionSourceRole",
    "GCProspectiveAcquisitionConfig",
    "GCProspectiveContractRosterRecord",
    "GCProspectiveAcquisitionSourceRecord",
    "GCProspectiveProviderLogRecord",
    "GCProspectiveCalendarEvidenceRecord",
    "GCProspectiveContaminationRecord",
    "GCProspectiveAcquisitionManifest",
    "GCProspectiveAcquisitionResult",
    "make_gc_prospective_acquisition_id",
    "validate_gc_prospective_acquisition_manifest",
)
