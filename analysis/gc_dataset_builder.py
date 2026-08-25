"""Deterministic offline GC Sierra-export canonical dataset builder.

The module is intentionally isolated.  It accepts immutable caller-supplied
bytes, calendar values, and configuration; it performs no filesystem, network,
strategy, model, execution, or integration work.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import hashlib
from importlib import metadata
import io
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from core.gc_chronological_backtest import GCChronologicalBar
from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus


GC_DATASET_BUILDER_VERSION = "GC-DATASET-BUILDER-V4-SOURCE-DOMAIN"
_GC_DATASET_SOURCE_COVERAGE_IDENTITY_VERSION = "GC-DATASET-BUILDER-V2"
GC_DATASET_INSTRUMENT = "GC"
GC_DATASET_TIMEFRAME = "5M"
GC_DATASET_SOURCE_TIMEZONE = "Asia/Tokyo"
GC_DATASET_EXCHANGE_TIMEZONE = "America/New_York"
GC_DATASET_TICK_SIZE = Decimal("0.1")
GC_ROLL_CONFIRMATION_SESSIONS = 3
GC_DELIVERY_MONTH_CODES = ("G", "J", "M", "Q", "V", "Z")

_UTC = timezone.utc
_FIVE_MINUTES = timedelta(minutes=5)
_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_CONTRACT_PATTERN = re.compile(r"^GC([GJMQVZ])(\d{2})-COMEX$")
_DATE_PATTERN = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
_TIME_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{6}$")
_NONNEGATIVE_INTEGER_PATTERN = re.compile(r"^(0|[1-9]\d*)$")
_IDENTITY_KINDS = frozenset({"SOURCE", "COVERAGE", "SEGMENT", "DATASET"})
_HEADER = (
    "Date",
    "Time",
    "Open",
    "High",
    "Low",
    "Last",
    "Volume",
    "# of Trades",
    "OHLC Avg",
    "HLC Avg",
    "HL Avg",
    "Bid Volume",
    "Ask Volume",
)


class GCDatasetBuildStatus(str, Enum):
    VALID = "VALID"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"


class GCSourceRole(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    OOS_HOLDOUT = "OOS_HOLDOUT"


class GCSegmentPartition(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    OOS_HOLDOUT = "OOS_HOLDOUT"


@dataclass(frozen=True)
class GCDatasetSessionInterval:
    start_timestamp: datetime
    end_timestamp: datetime


@dataclass(frozen=True)
class GCSplitSessionCalendarEntry:
    calendar_version: str
    trade_date: date
    intervals: tuple[GCDatasetSessionInterval, ...]
    source_artifact_ids: tuple[str, ...]
    source_artifact_sha256s: tuple[str, ...]


@dataclass(frozen=True)
class GCSierraChartBarRow:
    source_row_number: int
    bar_start_timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    number_of_trades: int
    bid_volume: int
    ask_volume: int


@dataclass(frozen=True)
class GCSierraChartExport:
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCSourceRole
    capture_timestamp: datetime
    chart_timezone: str
    timeframe: str
    rows: tuple[GCSierraChartBarRow, ...]


@dataclass(frozen=True)
class GCSierraChartCoverageEvidence:
    coverage_id: str
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCSourceRole
    capture_timestamp: datetime
    chart_timezone: str
    timeframe: str
    coverage_start_timestamp: datetime
    coverage_end_timestamp: datetime
    acquisition_completed_timestamp: datetime
    acquisition_evidence_sha256: str


@dataclass(frozen=True)
class GCCanonicalContractSegment:
    segment_id: str
    contract: str
    partition: GCSegmentPartition
    first_trade_date: date
    last_trade_date: date
    source_ids: tuple[str, ...]
    bars: tuple[GCChronologicalBar, ...]
    preceding_missing_bar_count: int


@dataclass(frozen=True)
class GCDatasetManifest:
    dataset_id: str
    version: str
    source_ids: tuple[str, ...]
    coverage_ids: tuple[str, ...]
    coverage_digest: str
    segment_ids: tuple[str, ...]
    calendar_version: str
    timezone_data_version: str
    raw_start_timestamp: datetime
    raw_end_timestamp: datetime
    usable_start_timestamp: datetime | None
    usable_end_timestamp: datetime | None
    parsed_row_count: int
    eligible_row_count: int
    development_bar_count: int
    oos_bar_count: int
    excluded_row_count: int
    missing_bar_count: int
    attested_no_trade_interval_count: int
    raw_volume: int
    eligible_volume: int
    excluded_volume: int
    completed_session_volumes: tuple[tuple[str, date, int], ...]
    exclusion_counts: tuple[tuple[str, int], ...]
    roll_trade_dates: tuple[date, ...]


@dataclass(frozen=True)
class GCDatasetBuildConfig:
    instrument: str
    timeframe: str
    source_timezone: str
    exchange_timezone: str
    timezone_data_version: str
    tick_size: Decimal
    initial_contract: str
    initial_trade_date: date
    roll_confirmation_sessions: int
    oos_start_trade_date: date
    oos_end_trade_date: date


@dataclass(frozen=True)
class GCDatasetBuildResult:
    status: GCDatasetBuildStatus
    dataset_id: str | None
    segments: tuple[GCCanonicalContractSegment, ...] = ()
    manifest: GCDatasetManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _NormalizedCalendar:
    calendar_version: str
    trade_date: date
    session_status: KillZoneSessionStatus
    intervals: tuple[tuple[datetime, datetime], ...]
    source_artifact_ids: tuple[str, ...]
    source_artifact_sha256s: tuple[str, ...]
    kind: str

    @property
    def opening(self) -> datetime | None:
        return self.intervals[0][0] if self.intervals else None

    @property
    def closing(self) -> datetime | None:
        return self.intervals[-1][1] if self.intervals else None


@dataclass(frozen=True)
class _NormalizedCoverage:
    coverage_id: str
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCSourceRole
    capture_timestamp: datetime
    chart_timezone: str
    timeframe: str
    start: datetime
    end: datetime
    acquisition_completed: datetime
    acquisition_evidence_sha256: str


@dataclass(frozen=True)
class _InputRow:
    source: GCSierraChartExport
    row: GCSierraChartBarRow
    start_utc: datetime
    close_utc: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int


@dataclass(frozen=True)
class _MergedRow:
    contract: str
    start_utc: datetime
    close_utc: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    volume: int
    number_of_trades: int
    bid_volume: int
    ask_volume: int
    source_ids: tuple[str, ...]
    source_row_numbers: tuple[int, ...]
    roles: tuple[GCSourceRole, ...]
    capture_timestamps: tuple[datetime, ...]
    instance_count: int


@dataclass(frozen=True)
class _UsableRow:
    merged: _MergedRow
    trade_date: date
    partition: GCSegmentPartition
    selected_source_ids: tuple[str, ...]
    selected_coverage_ids: tuple[str, ...]


@dataclass(frozen=True)
class _Issue:
    status: GCDatasetBuildStatus
    reason: str
    moment: datetime | None


@dataclass(frozen=True)
class _Assembly:
    segments: tuple[GCCanonicalContractSegment, ...]
    manifest: GCDatasetManifest | None
    dataset_id: str | None
    status: GCDatasetBuildStatus
    reasons: tuple[str, ...]


class _ValidationError(ValueError):
    def __init__(self, reason: str, moment: datetime | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.moment = moment


def parse_sierra_chart_gc_export(
    *,
    source_name: str,
    contract: str,
    role: GCSourceRole,
    capture_timestamp: datetime,
    chart_timezone: str,
    timeframe: str,
    raw_bytes: bytes,
) -> GCSierraChartExport:
    """Parse one exact immutable Sierra Chart bar-and-study export."""

    try:
        normalized_name = _normalize_source_name(source_name)
        normalized_contract = _normalize_contract(contract)
        normalized_role = _require_enum(role, GCSourceRole, "role")
        normalized_capture = _normalize_aware_timestamp(
            capture_timestamp, name="capture_timestamp"
        )
        normalized_source_timezone = _normalize_exact_text(
            chart_timezone,
            expected=GC_DATASET_SOURCE_TIMEZONE,
            name="chart_timezone",
            uppercase=False,
        )
        normalized_timeframe = _normalize_exact_text(
            timeframe,
            expected=GC_DATASET_TIMEFRAME,
            name="timeframe",
        )
        if type(raw_bytes) is not bytes:
            raise TypeError("raw_bytes must be exact bytes")
        source_hash = hashlib.sha256(raw_bytes).hexdigest()
        try:
            decoded = raw_bytes.decode("utf-8-sig", errors="strict")
        except (UnicodeDecodeError, UnicodeError) as exc:
            raise ValueError("raw bytes must be strict UTF-8 with optional BOM") from exc
        parsed = list(csv.reader(io.StringIO(decoded), skipinitialspace=True))
        if not parsed:
            raise ValueError("export header is required")
        header = tuple(value.strip() for value in parsed[0])
        if header != _HEADER:
            raise ValueError("export header/order must match the exact 13-column schema")
        rows: list[GCSierraChartBarRow] = []
        prior_timestamp: datetime | None = None
        source_zone = _load_zone(normalized_source_timezone)
        for row_number, values in enumerate(parsed[1:], start=2):
            if len(values) != 13 or all(not value.strip() for value in values):
                raise ValueError("each nonblank data row must contain exactly 13 fields")
            fields_ = tuple(value.strip() for value in values)
            local_start = _parse_raw_start(fields_[0], fields_[1])
            if prior_timestamp is not None and local_start <= prior_timestamp:
                raise ValueError("raw timestamps must be independently strictly increasing")
            prior_timestamp = local_start
            open_price = _parse_price(fields_[2], "open")
            high_price = _parse_price(fields_[3], "high")
            low_price = _parse_price(fields_[4], "low")
            close_price = _parse_price(fields_[5], "close")
            _validate_price_geometry(open_price, high_price, low_price, close_price)
            volume = _parse_nonnegative_integer(fields_[6], "volume")
            trades = _parse_nonnegative_integer(fields_[7], "number_of_trades")
            for index, label in ((8, "ohlc_average"), (9, "hlc_average"), (10, "hl_average")):
                _parse_finite_decimal(fields_[index], label)
            bid_volume = _parse_nonnegative_integer(fields_[11], "bid_volume")
            ask_volume = _parse_nonnegative_integer(fields_[12], "ask_volume")
            if volume != bid_volume + ask_volume:
                raise ValueError("volume must equal bid_volume plus ask_volume")
            if volume == 0 and trades == 0:
                raise ValueError("synthetic no-data row")
            close_utc = local_start.replace(tzinfo=source_zone).astimezone(_UTC) + _FIVE_MINUTES
            if close_utc > normalized_capture:
                raise ValueError("bar close exceeds immutable capture timestamp")
            rows.append(
                GCSierraChartBarRow(
                    source_row_number=row_number,
                    bar_start_timestamp=local_start,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    number_of_trades=trades,
                    bid_volume=bid_volume,
                    ask_volume=ask_volume,
                )
            )
        source_id = make_gc_dataset_id(
            identity_kind="SOURCE",
            source_name=normalized_name,
            source_sha256=source_hash,
            contract=normalized_contract,
            role=normalized_role,
            capture_timestamp=normalized_capture,
            source_timezone=normalized_source_timezone,
            timeframe=normalized_timeframe,
        )
        return GCSierraChartExport(
            source_id=source_id,
            source_name=normalized_name,
            source_sha256=source_hash,
            contract=normalized_contract,
            role=normalized_role,
            capture_timestamp=normalized_capture,
            chart_timezone=normalized_source_timezone,
            timeframe=normalized_timeframe,
            rows=tuple(rows),
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError("malformed Sierra Chart export") from exc


def make_gc_dataset_id(
    *,
    identity_kind: str,
    config: GCDatasetBuildConfig | None = None,
    source_id: str | None = None,
    source_name: str | None = None,
    source_sha256: str | None = None,
    contract: str | None = None,
    role: GCSourceRole | None = None,
    capture_timestamp: datetime | None = None,
    source_timezone: str | None = None,
    timeframe: str | None = None,
    coverage_start_timestamp: datetime | None = None,
    coverage_end_timestamp: datetime | None = None,
    acquisition_completed_timestamp: datetime | None = None,
    acquisition_evidence_sha256: str | None = None,
    first_trade_date: date | None = None,
    last_trade_date: date | None = None,
    source_ids: tuple[str, ...] = (),
    coverage_ids: tuple[str, ...] = (),
    bar_digest: str | None = None,
    preceding_missing_bar_count: int | None = None,
    partition: GCSegmentPartition | None = None,
    segment_ids: tuple[str, ...] = (),
    calendar_digest: str | None = None,
    coverage_digest: str | None = None,
    evidence_digest: str | None = None,
    roll_trade_dates: tuple[date, ...] = (),
) -> str:
    """Build one exact kind-specific deterministic identity."""

    try:
        kind = _normalize_identity_kind(identity_kind)
        identity_version = (
            _GC_DATASET_SOURCE_COVERAGE_IDENTITY_VERSION
            if kind in {"SOURCE", "COVERAGE"}
            else GC_DATASET_BUILDER_VERSION
        )
        common = {"version": identity_version, "identity_kind": kind}
        if kind == "SOURCE":
            _require_none(config, "config")
            _require_none(source_id, "source_id")
            _forbid_coverage_fields(
                coverage_start_timestamp,
                coverage_end_timestamp,
                acquisition_completed_timestamp,
                acquisition_evidence_sha256,
            )
            _require_none(first_trade_date, "first_trade_date")
            _require_none(last_trade_date, "last_trade_date")
            _require_empty(source_ids, "source_ids")
            _require_empty(coverage_ids, "coverage_ids")
            _require_none(bar_digest, "bar_digest")
            _require_none(preceding_missing_bar_count, "preceding_missing_bar_count")
            _require_none(partition, "partition")
            _require_empty(segment_ids, "segment_ids")
            _require_none(calendar_digest, "calendar_digest")
            _require_none(coverage_digest, "coverage_digest")
            _require_none(evidence_digest, "evidence_digest")
            _require_empty(roll_trade_dates, "roll_trade_dates")
            payload = {
                **common,
                "source_name": _normalize_source_name(_required(source_name, "source_name")),
                "source_sha256": _require_hash(_required(source_sha256, "source_sha256"), "source_sha256"),
                "contract": _normalize_contract(_required(contract, "contract")),
                "role": _require_enum(_required(role, "role"), GCSourceRole, "role").value,
                "capture_timestamp": _timestamp_text(
                    _normalize_aware_timestamp(_required(capture_timestamp, "capture_timestamp"), name="capture_timestamp")
                ),
                "source_timezone": _normalize_exact_text(
                    _required(source_timezone, "source_timezone"),
                    expected=GC_DATASET_SOURCE_TIMEZONE,
                    name="source_timezone",
                    uppercase=False,
                ),
                "timeframe": _normalize_exact_text(
                    _required(timeframe, "timeframe"),
                    expected=GC_DATASET_TIMEFRAME,
                    name="timeframe",
                ),
            }
        elif kind == "COVERAGE":
            _require_none(config, "config")
            _require_none(first_trade_date, "first_trade_date")
            _require_none(last_trade_date, "last_trade_date")
            _require_empty(source_ids, "source_ids")
            _require_empty(coverage_ids, "coverage_ids")
            _require_none(bar_digest, "bar_digest")
            _require_none(preceding_missing_bar_count, "preceding_missing_bar_count")
            _require_none(partition, "partition")
            _require_empty(segment_ids, "segment_ids")
            _require_none(calendar_digest, "calendar_digest")
            _require_none(coverage_digest, "coverage_digest")
            _require_none(evidence_digest, "evidence_digest")
            _require_empty(roll_trade_dates, "roll_trade_dates")
            normalized_name = _normalize_source_name(_required(source_name, "source_name"))
            normalized_source_hash = _require_hash(
                _required(source_sha256, "source_sha256"), "source_sha256"
            )
            normalized_contract = _normalize_contract(_required(contract, "contract"))
            normalized_role = _require_enum(
                _required(role, "role"), GCSourceRole, "role"
            )
            normalized_capture = _normalize_aware_timestamp(
                _required(capture_timestamp, "capture_timestamp"),
                name="capture_timestamp",
            )
            normalized_timezone = _normalize_exact_text(
                _required(source_timezone, "source_timezone"),
                expected=GC_DATASET_SOURCE_TIMEZONE,
                name="source_timezone",
                uppercase=False,
            )
            normalized_timeframe = _normalize_exact_text(
                _required(timeframe, "timeframe"),
                expected=GC_DATASET_TIMEFRAME,
                name="timeframe",
            )
            normalized_source_id = _require_hash(
                _required(source_id, "source_id"), "source_id"
            )
            expected_source_id = make_gc_dataset_id(
                identity_kind="SOURCE",
                source_name=normalized_name,
                source_sha256=normalized_source_hash,
                contract=normalized_contract,
                role=normalized_role,
                capture_timestamp=normalized_capture,
                source_timezone=normalized_timezone,
                timeframe=normalized_timeframe,
            )
            if normalized_source_id != expected_source_id:
                raise ValueError("source_id does not match canonical SOURCE identity")
            start = _normalize_aware_timestamp(
                _required(coverage_start_timestamp, "coverage_start_timestamp"),
                name="coverage_start_timestamp",
            )
            end = _normalize_aware_timestamp(
                _required(coverage_end_timestamp, "coverage_end_timestamp"),
                name="coverage_end_timestamp",
            )
            completed = _normalize_aware_timestamp(
                _required(
                    acquisition_completed_timestamp,
                    "acquisition_completed_timestamp",
                ),
                name="acquisition_completed_timestamp",
            )
            if start >= end:
                raise ValueError("coverage range must be start-inclusive/end-exclusive")
            if completed < end or completed > normalized_capture:
                raise ValueError("acquisition completion must be between coverage end and capture")
            payload = {
                **common,
                "source_id": normalized_source_id,
                "source_name": normalized_name,
                "source_sha256": normalized_source_hash,
                "contract": normalized_contract,
                "role": normalized_role.value,
                "capture_timestamp": _timestamp_text(normalized_capture),
                "source_timezone": normalized_timezone,
                "timeframe": normalized_timeframe,
                "coverage_start_timestamp": _timestamp_text(start),
                "coverage_end_timestamp": _timestamp_text(end),
                "acquisition_completed_timestamp": _timestamp_text(completed),
                "acquisition_evidence_sha256": _require_hash(
                    _required(
                        acquisition_evidence_sha256,
                        "acquisition_evidence_sha256",
                    ),
                    "acquisition_evidence_sha256",
                ),
            }
        elif kind == "SEGMENT":
            normalized_config = _normalize_config(_required(config, "config"))
            _require_none(source_id, "source_id")
            _forbid_source_fields(
                source_name, source_sha256, role, capture_timestamp, source_timezone, timeframe
            )
            _forbid_coverage_fields(
                coverage_start_timestamp,
                coverage_end_timestamp,
                acquisition_completed_timestamp,
                acquisition_evidence_sha256,
            )
            _require_empty(coverage_ids, "coverage_ids")
            _require_empty(segment_ids, "segment_ids")
            _require_none(calendar_digest, "calendar_digest")
            _require_none(coverage_digest, "coverage_digest")
            _require_none(evidence_digest, "evidence_digest")
            _require_empty(roll_trade_dates, "roll_trade_dates")
            first = _require_date(_required(first_trade_date, "first_trade_date"), "first_trade_date")
            last = _require_date(_required(last_trade_date, "last_trade_date"), "last_trade_date")
            if last < first:
                raise ValueError("segment date range is impossible")
            payload = {
                **common,
                "config": _config_payload(normalized_config),
                "contract": _normalize_contract(_required(contract, "contract")),
                "partition": _require_enum(
                    _required(partition, "partition"), GCSegmentPartition, "partition"
                ).value,
                "first_trade_date": first.isoformat(),
                "last_trade_date": last.isoformat(),
                "source_ids": _normalize_hash_tuple(source_ids, "source_ids", nonempty=True),
                "bar_digest": _require_hash(_required(bar_digest, "bar_digest"), "bar_digest"),
                "preceding_missing_bar_count": _require_nonnegative_int(
                    _required(preceding_missing_bar_count, "preceding_missing_bar_count"),
                    "preceding_missing_bar_count",
                ),
            }
        else:
            normalized_config = _normalize_config(_required(config, "config"))
            _require_none(source_id, "source_id")
            _forbid_source_fields(
                source_name, source_sha256, role, capture_timestamp, source_timezone, timeframe
            )
            _forbid_coverage_fields(
                coverage_start_timestamp,
                coverage_end_timestamp,
                acquisition_completed_timestamp,
                acquisition_evidence_sha256,
            )
            _require_none(contract, "contract")
            _require_none(first_trade_date, "first_trade_date")
            _require_none(last_trade_date, "last_trade_date")
            _require_none(bar_digest, "bar_digest")
            _require_none(preceding_missing_bar_count, "preceding_missing_bar_count")
            _require_none(partition, "partition")
            payload = {
                **common,
                "config": _config_payload(normalized_config),
                "source_ids": _normalize_hash_tuple(source_ids, "source_ids", nonempty=True),
                "coverage_ids": _normalize_hash_tuple(
                    coverage_ids, "coverage_ids", nonempty=True
                ),
                "segment_ids": _normalize_hash_tuple(segment_ids, "segment_ids", nonempty=False),
                "calendar_digest": _require_hash(
                    _required(calendar_digest, "calendar_digest"), "calendar_digest"
                ),
                "coverage_digest": _require_hash(
                    _required(coverage_digest, "coverage_digest"), "coverage_digest"
                ),
                "evidence_digest": _require_hash(
                    _required(evidence_digest, "evidence_digest"), "evidence_digest"
                ),
                "roll_trade_dates": tuple(
                    item.isoformat()
                    for item in _normalize_date_tuple(roll_trade_dates, "roll_trade_dates")
                ),
            }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError("malformed GC dataset identity evidence") from exc


def build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
    calendar_entries: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult:
    """Build immutable exact-contract GC segments without file or network I/O."""

    try:
        normalized_config = _normalize_config(config)
    except (TypeError, ValueError) as exc:
        return _result(GCDatasetBuildStatus.INVALID, "INVALID_CONFIG", str(exc))
    try:
        export_rows, normalized_exports, export_issues = _scan_exports(exports)
        normalized_coverage, coverage_issues = _scan_coverage_evidence(
            coverage_evidence
        )
        calendars, calendar_issues = _scan_calendars(calendar_entries, normalized_config)
    except Exception as exc:  # pragma: no cover - containment boundary
        return _result(GCDatasetBuildStatus.INVALID, "MALFORMED_INPUT", str(exc))

    issues = list(export_issues) + list(coverage_issues) + list(calendar_issues)
    if exports is None or coverage_evidence is None or calendar_entries is None:
        invalid = [issue for issue in issues if issue.status is GCDatasetBuildStatus.INVALID]
        if invalid:
            return _issues_result(invalid, segments=())
        return _result(
            GCDatasetBuildStatus.UNKNOWN,
            "MISSING_TOP_LEVEL_CONTEXT",
            "exports, coverage_evidence, and calendar_entries must all be supplied",
        )
    if (
        type(exports) is not tuple
        or type(coverage_evidence) is not tuple
        or type(calendar_entries) is not tuple
    ):
        return _result(
            GCDatasetBuildStatus.INVALID,
            "NON_TUPLE_TOP_LEVEL_INPUT",
            "exports, coverage_evidence, and calendar_entries must be exact tuples or None",
        )
    if not exports and not coverage_evidence and not calendar_entries:
        return _result(GCDatasetBuildStatus.NONE, "NO_SOURCE_SCOPE", "no exports or calendar entries")
    if not exports and coverage_evidence:
        return _result(
            GCDatasetBuildStatus.INVALID,
            "UNREQUESTED_COVERAGE_EVIDENCE",
            "coverage evidence was supplied without export scope",
        )
    if not exports and calendar_entries:
        return _result(
            GCDatasetBuildStatus.INVALID,
            "UNREQUESTED_CALENDAR_ENTRY",
            "calendar evidence was supplied without export scope",
        )
    linked_coverage, reconciliation_issues = _reconcile_coverage(
        exports=normalized_exports,
        coverage=normalized_coverage,
        rows=export_rows,
    )
    issues.extend(reconciliation_issues)
    invalid = [issue for issue in issues if issue.status is GCDatasetBuildStatus.INVALID]
    if invalid:
        cutoff = _earliest_issue_moment(issues)
        prior_rows = tuple(row for row in export_rows if cutoff is not None and row.close_utc < cutoff)
        prior_calendars = tuple(
            item
            for item in calendars
            if cutoff is not None
            and item.opening is not None
            and item.opening < cutoff
        )
        prior_coverage = tuple(
            item
            for item in linked_coverage
            if cutoff is not None and item.end <= cutoff
        )
        prior = _assemble(
            rows=prior_rows,
            exports=normalized_exports,
            coverage=prior_coverage,
            calendars=prior_calendars,
            config=normalized_config,
            allow_manifest=False,
        )
        return _issues_result(invalid, segments=prior.segments)

    assembly = _assemble(
        rows=export_rows,
        exports=normalized_exports,
        coverage=linked_coverage,
        calendars=calendars,
        config=normalized_config,
        allow_manifest=True,
        initial_issues=tuple(issues),
    )
    return GCDatasetBuildResult(
        status=assembly.status,
        dataset_id=assembly.dataset_id,
        segments=assembly.segments,
        manifest=assembly.manifest,
        reasons=assembly.reasons,
        blocking_reasons=() if assembly.status in {GCDatasetBuildStatus.VALID, GCDatasetBuildStatus.NONE} else assembly.reasons,
    )


def _assemble(
    *,
    rows: tuple[_InputRow, ...],
    exports: tuple[GCSierraChartExport, ...],
    coverage: tuple[_NormalizedCoverage, ...],
    calendars: tuple[_NormalizedCalendar, ...],
    config: GCDatasetBuildConfig,
    allow_manifest: bool,
    initial_issues: tuple[_Issue, ...] = (),
) -> _Assembly:
    merged, merge_issues = _merge_rows(rows, exports)
    calendar_map = {entry.trade_date: entry for entry in calendars}
    usable: list[_UsableRow] = []
    volume_usable: list[_UsableRow] = []
    issues = list(initial_issues) + list(merge_issues)
    base_exclusions: dict[tuple[str, datetime], str] = {}
    source_rank = {source.source_id: index for index, source in enumerate(exports)}
    coverage_rank = {
        item.coverage_id: index for index, item in enumerate(coverage)
    }
    coverage_by_source: dict[str, tuple[_NormalizedCoverage, ...]] = {
        source.source_id: tuple(
            item for item in coverage if item.source_id == source.source_id
        )
        for source in exports
    }
    outer_domain = _calendar_outer_domain(calendars)
    if merged and outer_domain is None:
        issues.append(
            _Issue(
                GCDatasetBuildStatus.INVALID,
                "CALENDAR_OUTER_DOMAIN_EMPTY",
                merged[0].close_utc,
            )
        )

    for item in merged:
        if outer_domain is None:
            continue
        domain_start, domain_end = outer_domain
        if item.close_utc <= domain_start:
            base_exclusions[(item.contract, item.start_utc)] = (
                "BEFORE_CALENDAR_DOMAIN"
            )
            continue
        if item.start_utc >= domain_end:
            base_exclusions[(item.contract, item.start_utc)] = (
                "AFTER_CALENDAR_DOMAIN"
            )
            continue
        if (
            item.start_utc < domain_start < item.close_utc
            or item.start_utc < domain_end < item.close_utc
        ):
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "CALENDAR_DOMAIN_BOUNDARY_STRADDLE",
                    item.close_utc,
                )
            )
            continue
        interval_matches = tuple(
            (entry, interval_start)
            for entry in calendars
            for interval_start, interval_end in entry.intervals
            if interval_start <= item.start_utc
            and item.close_utc <= interval_end
        )
        if len(interval_matches) > 1:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "CALENDAR_INTERVAL_OVERLAP",
                    item.close_utc,
                )
            )
            continue
        if interval_matches:
            entry, interval_start = interval_matches[0]
            trade_date = entry.trade_date
        else:
            outer_matches = tuple(
                entry
                for entry in calendars
                if entry.opening is not None
                and entry.closing is not None
                and entry.opening <= item.start_utc
                and item.close_utc <= entry.closing
            )
            if len(outer_matches) > 1:
                issues.append(
                    _Issue(
                        GCDatasetBuildStatus.INVALID,
                        "CALENDAR_INTERVAL_OVERLAP",
                        item.close_utc,
                    )
                )
                continue
            trade_date = _trade_date_for_start(item.start_utc)
            entry = (
                outer_matches[0]
                if outer_matches
                else calendar_map.get(trade_date)
            )
            interval_start = None
        if entry is None:
            issues.append(_Issue(GCDatasetBuildStatus.UNKNOWN, "CALENDAR_COVERAGE_MISSING", item.close_utc))
            continue
        if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
            if item.volume > 0:
                issues.append(_Issue(GCDatasetBuildStatus.INVALID, "ROW_IN_SESSION_CLOSED", item.close_utc))
            else:
                base_exclusions[(item.contract, item.start_utc)] = "SESSION_CLOSED_ZERO_VOLUME"
            continue
        if entry.opening is None or entry.closing is None:
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, "CALENDAR_BOUNDARY_MISSING", item.close_utc))
            continue
        if interval_start is None:
            if item.volume > 0:
                issues.append(_Issue(GCDatasetBuildStatus.INVALID, "ROW_OUTSIDE_DECLARED_SESSION", item.close_utc))
            else:
                base_exclusions[(item.contract, item.start_utc)] = "OUTSIDE_SESSION_ZERO_VOLUME"
            continue
        offset = item.start_utc - interval_start
        if offset.total_seconds() % _FIVE_MINUTES.total_seconds() != 0:
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, "ROW_OFF_FIVE_MINUTE_GRID", item.close_utc))
            continue
        scoped_partition = _partition_for_trade_date(trade_date, config)
        partition = scoped_partition or GCSegmentPartition.DEVELOPMENT
        required_role = (
            GCSourceRole.OOS_HOLDOUT
            if partition is GCSegmentPartition.OOS_HOLDOUT
            else GCSourceRole.DEVELOPMENT
        )
        matching_ids = tuple(
            source_id
            for source_id, role in zip(item.source_ids, item.roles, strict=True)
            if role is required_role
        )
        if not matching_ids:
            status = (
                GCDatasetBuildStatus.INVALID
                if required_role is GCSourceRole.DEVELOPMENT
                else GCDatasetBuildStatus.UNKNOWN
            )
            reason = "SOURCE_ROLE_CONTRADICTS_DEVELOPMENT" if status is GCDatasetBuildStatus.INVALID else "OOS_SOURCE_COVERAGE_MISSING"
            issues.append(_Issue(status, reason, item.close_utc))
            continue
        matching_coverage_ids = tuple(
            coverage_item.coverage_id
            for source_id in matching_ids
            for coverage_item in coverage_by_source.get(source_id, ())
            if coverage_item.start <= item.start_utc
            and item.close_utc <= coverage_item.end
        )
        if not matching_coverage_ids:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.UNKNOWN,
                    "COVERAGE_UNVERIFIED",
                    item.close_utc,
                )
            )
            continue
        candidate = _UsableRow(
            merged=item,
            trade_date=trade_date,
            partition=partition,
            selected_source_ids=tuple(
                sorted(matching_ids, key=source_rank.__getitem__)
            ),
            selected_coverage_ids=tuple(
                sorted(set(matching_coverage_ids), key=coverage_rank.__getitem__)
            ),
        )
        volume_usable.append(candidate)
        if trade_date < config.initial_trade_date:
            base_exclusions[(item.contract, item.start_utc)] = "BEFORE_INITIAL_BOUNDARY"
            continue
        if trade_date > config.oos_end_trade_date:
            base_exclusions[(item.contract, item.start_utc)] = "AFTER_OOS_BOUNDARY"
            continue
        usable.append(candidate)

    if issues:
        cutoff = _earliest_issue_moment(issues)
        usable = [item for item in usable if cutoff is not None and item.merged.close_utc < cutoff]
        volume_usable = [
            item
            for item in volume_usable
            if cutoff is not None and item.merged.close_utc < cutoff
        ]

    contracts = tuple(dict.fromkeys(source.contract for source in exports))
    completed_volumes, completed_missing_counts = _completed_session_volumes(
        volume_usable,
        calendars,
        exports,
        coverage,
        config,
    )
    initial_issue = _initial_contract_issue(
        contracts=contracts,
        calendars=calendars,
        completed_volumes={
            (contract, trade_date): volume
            for contract, trade_date, volume in completed_volumes
        },
        config=config,
    )
    if initial_issue is not None:
        issues.append(initial_issue)
    active_by_date, roll_dates, roll_issues = _roll_plan(
        contracts=contracts,
        calendars=calendars,
        completed_volumes={
            (contract, trade_date): volume
            for contract, trade_date, volume in completed_volumes
        },
        config=config,
    )
    issues.extend(roll_issues)
    initial_position = next(
        (
            index
            for index, entry in enumerate(calendars)
            if entry.trade_date == config.initial_trade_date
        ),
        None,
    )
    accepted_volume_keys: set[tuple[str, date]] = set()
    if initial_position is not None:
        prior_entries = tuple(
            entry
            for entry in calendars[:initial_position]
            if entry.session_status is not KillZoneSessionStatus.SESSION_CLOSED
        )[-GC_ROLL_CONFIRMATION_SESSIONS:]
        predecessor = _previous_contract(config.initial_contract)
        accepted_volume_keys.update(
            (contract, entry.trade_date)
            for entry in prior_entries
            for contract in (predecessor, config.initial_contract)
        )
    accepted_volume_keys.update(
        (contract, trade_date)
        for trade_date, active in active_by_date.items()
        for contract in (active, _next_contract(active))
    )
    promoted_completed_volumes = tuple(
        item
        for item in completed_volumes
        if (item[0], item[1]) in accepted_volume_keys
    )
    cutoff = _earliest_issue_moment(issues)
    selected: list[_UsableRow] = []
    for item in usable:
        if cutoff is not None and item.merged.close_utc >= cutoff:
            continue
        active = active_by_date.get(item.trade_date)
        if active == item.merged.contract:
            selected.append(item)
        else:
            base_exclusions[(item.merged.contract, item.merged.start_utc)] = "ROLL_EVIDENCE_ONLY"

    segments = _make_segments(
        tuple(selected), config, source_rank, calendar_map
    )
    if issues or not allow_manifest:
        status = _highest_status(issues) if issues else GCDatasetBuildStatus.VALID
        reasons = tuple(issue.reason for issue in _ordered_issues(issues))
        return _Assembly(segments, None, None, status, reasons)

    parsed_row_count = sum(item.instance_count for item in merged)
    raw_volume = sum(item.volume * item.instance_count for item in merged)
    eligible_row_count = len(selected)
    eligible_volume = sum(item.merged.volume for item in selected)
    duplicate_count = sum(item.instance_count - 1 for item in merged)
    exclusion_counter: dict[str, int] = {}
    if duplicate_count:
        exclusion_counter["DUPLICATE_RECONCILED"] = duplicate_count
    selected_keys = {(item.merged.contract, item.merged.start_utc) for item in selected}
    for item in merged:
        key = (item.contract, item.start_utc)
        if key not in selected_keys:
            reason = base_exclusions.get(key, "ROLL_EVIDENCE_ONLY")
            exclusion_counter[reason] = exclusion_counter.get(reason, 0) + 1
    excluded_row_count = parsed_row_count - eligible_row_count
    exclusion_counts = tuple(sorted(exclusion_counter.items()))
    if sum(count for _, count in exclusion_counts) != excluded_row_count:
        raise _ValidationError("manifest exclusion conservation failed")
    source_ids = tuple(source.source_id for source in exports)
    coverage_ids = tuple(item.coverage_id for item in coverage)
    segment_ids = tuple(segment.segment_id for segment in segments)
    calendar_digest = _digest_calendar(calendars)
    coverage_digest = _digest_coverage(coverage)
    raw_moments = tuple(item.close_utc for item in merged)
    usable_moments = tuple(item.merged.close_utc for item in selected)
    completed_missing_map = {
        (contract, trade_date): count
        for contract, trade_date, count in completed_missing_counts
    }
    missing_count = sum(
        completed_missing_map.get((active, trade_date), 0)
        for trade_date, active in active_by_date.items()
        if config.initial_trade_date <= trade_date <= config.oos_end_trade_date
    )
    attested_no_trade_count = missing_count + _attested_official_gap_count(
        tuple(selected), calendar_map
    )
    exclusion_ledger: list[tuple[object, ...]] = []
    for item in merged:
        key = (item.contract, item.start_utc)
        selected_item = key in selected_keys
        primary_reason = base_exclusions.get(key, "ROLL_EVIDENCE_ONLY")
        for member_index, (source_id, source_row_number) in enumerate(
            zip(item.source_ids, item.source_row_numbers, strict=True)
        ):
            if selected_item and member_index == 0:
                continue
            reason = (
                primary_reason
                if member_index == 0
                else "DUPLICATE_RECONCILED"
            )
            exclusion_ledger.append(
                (
                    source_id,
                    source_row_number,
                    item.contract,
                    _timestamp_text(item.start_utc),
                    _timestamp_text(item.close_utc),
                    item.volume,
                    reason,
                )
            )
    if len(exclusion_ledger) != excluded_row_count:
        raise _ValidationError("manifest exclusion ledger conservation failed")
    dev_count = sum(len(segment.bars) for segment in segments if segment.partition is GCSegmentPartition.DEVELOPMENT)
    oos_count = sum(len(segment.bars) for segment in segments if segment.partition is GCSegmentPartition.OOS_HOLDOUT)
    evidence = {
        "version": GC_DATASET_BUILDER_VERSION,
        "source_ids": source_ids,
        "coverage_ids": coverage_ids,
        "coverage_digest": coverage_digest,
        "segment_ids": segment_ids,
        "calendar_version": calendars[0].calendar_version if calendars else "",
        "timezone_data_version": config.timezone_data_version,
        "calendar_domain_start_timestamp": _timestamp_text(outer_domain[0]),
        "calendar_domain_end_timestamp": _timestamp_text(outer_domain[1]),
        "raw_start_timestamp": _timestamp_text(min(raw_moments)),
        "raw_end_timestamp": _timestamp_text(max(raw_moments)),
        "usable_start_timestamp": _timestamp_text(min(usable_moments)) if usable_moments else None,
        "usable_end_timestamp": _timestamp_text(max(usable_moments)) if usable_moments else None,
        "parsed_row_count": parsed_row_count,
        "eligible_row_count": eligible_row_count,
        "development_bar_count": dev_count,
        "oos_bar_count": oos_count,
        "excluded_row_count": excluded_row_count,
        "missing_bar_count": missing_count,
        "attested_no_trade_interval_count": attested_no_trade_count,
        "raw_volume": raw_volume,
        "eligible_volume": eligible_volume,
        "excluded_volume": raw_volume - eligible_volume,
        "completed_session_volumes": tuple(
            (contract, trade_date.isoformat(), volume)
            for contract, trade_date, volume in promoted_completed_volumes
        ),
        "exclusion_counts": exclusion_counts,
        "exclusion_ledger": tuple(exclusion_ledger),
        "roll_trade_dates": tuple(item.isoformat() for item in roll_dates),
    }
    evidence_digest = _hash_payload(evidence)
    dataset_id = make_gc_dataset_id(
        identity_kind="DATASET",
        config=config,
        source_ids=source_ids,
        coverage_ids=coverage_ids,
        segment_ids=segment_ids,
        calendar_digest=calendar_digest,
        coverage_digest=coverage_digest,
        evidence_digest=evidence_digest,
        roll_trade_dates=roll_dates,
    )
    manifest = GCDatasetManifest(
        dataset_id=dataset_id,
        version=GC_DATASET_BUILDER_VERSION,
        source_ids=source_ids,
        coverage_ids=coverage_ids,
        coverage_digest=coverage_digest,
        segment_ids=segment_ids,
        calendar_version=calendars[0].calendar_version if calendars else "",
        timezone_data_version=config.timezone_data_version,
        raw_start_timestamp=min(raw_moments),
        raw_end_timestamp=max(raw_moments),
        usable_start_timestamp=min(usable_moments) if usable_moments else None,
        usable_end_timestamp=max(usable_moments) if usable_moments else None,
        parsed_row_count=parsed_row_count,
        eligible_row_count=eligible_row_count,
        development_bar_count=dev_count,
        oos_bar_count=oos_count,
        excluded_row_count=excluded_row_count,
        missing_bar_count=missing_count,
        attested_no_trade_interval_count=attested_no_trade_count,
        raw_volume=raw_volume,
        eligible_volume=eligible_volume,
        excluded_volume=raw_volume - eligible_volume,
        completed_session_volumes=promoted_completed_volumes,
        exclusion_counts=exclusion_counts,
        roll_trade_dates=roll_dates,
    )
    status = GCDatasetBuildStatus.VALID if segments else GCDatasetBuildStatus.NONE
    return _Assembly(segments, manifest, dataset_id, status, ("CANONICAL_DATASET_BUILT",))


def _scan_exports(
    exports: tuple[GCSierraChartExport, ...] | None,
) -> tuple[tuple[_InputRow, ...], tuple[GCSierraChartExport, ...], tuple[_Issue, ...]]:
    if exports is None:
        return (), (), ()
    if type(exports) is not tuple:
        return (), (), (_Issue(GCDatasetBuildStatus.INVALID, "EXPORTS_NOT_TUPLE", None),)
    rows: list[_InputRow] = []
    valid_exports: list[GCSierraChartExport] = []
    issues: list[_Issue] = []
    keys: list[tuple[tuple[int, int], str, str]] = []
    hash_roles: dict[str, tuple[str, GCSourceRole]] = {}
    for item in exports:
        try:
            normalized, normalized_rows = _validate_export(item)
            key = (_contract_key(normalized.contract), normalized.role.value, normalized.source_sha256)
            keys.append(key)
            prior = hash_roles.get(normalized.source_sha256)
            if prior is not None and prior != (normalized.contract, normalized.role):
                raise _ValidationError("SOURCE_HASH_ROLE_OR_CONTRACT_CONFLICT", _export_first_moment(normalized))
            hash_roles[normalized.source_sha256] = (normalized.contract, normalized.role)
            valid_exports.append(normalized)
            rows.extend(normalized_rows)
        except _ValidationError as exc:
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, exc.reason, exc.moment))
        except (TypeError, ValueError):
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "MALFORMED_EXPORT",
                    _export_first_moment(item),
                )
            )
    if len(keys) > 1 and any(right <= left for left, right in zip(keys, keys[1:])):
        issues.append(_Issue(GCDatasetBuildStatus.INVALID, "EXPORT_TUPLE_OUT_OF_ORDER", None))
    return tuple(rows), tuple(valid_exports), tuple(issues)


def _validate_export(item: object) -> tuple[GCSierraChartExport, tuple[_InputRow, ...]]:
    if not isinstance(item, GCSierraChartExport):
        raise _ValidationError("MALFORMED_EXPORT_TYPE")
    moment = _export_first_moment(item)
    source_name = _normalize_source_name(item.source_name)
    source_hash = _require_hash(item.source_sha256, "source_sha256")
    contract = _normalize_contract(item.contract)
    role = _require_enum(item.role, GCSourceRole, "role")
    capture = _normalize_aware_timestamp(item.capture_timestamp, name="capture_timestamp")
    source_timezone = _normalize_exact_text(
        item.chart_timezone,
        expected=GC_DATASET_SOURCE_TIMEZONE,
        name="chart_timezone",
        uppercase=False,
    )
    timeframe = _normalize_exact_text(
        item.timeframe, expected=GC_DATASET_TIMEFRAME, name="timeframe"
    )
    expected_id = make_gc_dataset_id(
        identity_kind="SOURCE",
        source_name=source_name,
        source_sha256=source_hash,
        contract=contract,
        role=role,
        capture_timestamp=capture,
        source_timezone=source_timezone,
        timeframe=timeframe,
    )
    if _require_hash(item.source_id, "source_id") != expected_id:
        raise _ValidationError("SOURCE_ID_MISMATCH", moment)
    if type(item.rows) is not tuple:
        raise _ValidationError("EXPORT_ROWS_NOT_TUPLE", moment)
    source_zone = _load_zone(source_timezone)
    normalized_rows: list[_InputRow] = []
    prior_number: int | None = None
    prior_start: datetime | None = None
    for row in item.rows:
        row_moment = _row_effective_moment(row, source_zone)
        try:
            normalized = _validate_row(row, source_zone, capture)
        except (TypeError, ValueError) as exc:
            raise _ValidationError("MALFORMED_EXPORT_ROW", row_moment) from exc
        if (
            normalized.row.volume == 0
            and normalized.row.number_of_trades == 0
            and normalized.row.bid_volume == 0
            and normalized.row.ask_volume == 0
            and normalized.open_tick
            == normalized.high_tick
            == normalized.low_tick
            == normalized.close_tick
        ):
            raise _ValidationError("SYNTHETIC_NO_DATA_ROW", normalized.close_utc)
        if prior_number is not None and normalized.row.source_row_number <= prior_number:
            raise _ValidationError("SOURCE_ROW_NUMBER_OUT_OF_ORDER", normalized.close_utc)
        if prior_start is not None and normalized.start_utc <= prior_start:
            raise _ValidationError("SOURCE_ROW_TIMESTAMP_OUT_OF_ORDER", normalized.close_utc)
        prior_number = normalized.row.source_row_number
        prior_start = normalized.start_utc
        normalized_rows.append(
            _InputRow(
                source=GCSierraChartExport(
                    item.source_id,
                    source_name,
                    source_hash,
                    contract,
                    role,
                    capture,
                    source_timezone,
                    timeframe,
                    item.rows,
                ),
                row=normalized.row,
                start_utc=normalized.start_utc,
                close_utc=normalized.close_utc,
                open_tick=normalized.open_tick,
                high_tick=normalized.high_tick,
                low_tick=normalized.low_tick,
                close_tick=normalized.close_tick,
            )
        )
    normalized_export = GCSierraChartExport(
        expected_id,
        source_name,
        source_hash,
        contract,
        role,
        capture,
        source_timezone,
        timeframe,
        item.rows,
    )
    return normalized_export, tuple(normalized_rows)


@dataclass(frozen=True)
class _ValidatedRow:
    row: GCSierraChartBarRow
    start_utc: datetime
    close_utc: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int


def _validate_row(row: object, source_zone: ZoneInfo, capture: datetime) -> _ValidatedRow:
    if not isinstance(row, GCSierraChartBarRow):
        raise TypeError("row type")
    row_number = _require_nonnegative_int(row.source_row_number, "source_row_number")
    if row_number < 2:
        raise ValueError("source_row_number must be at least two")
    local_start = _normalize_naive_timestamp(row.bar_start_timestamp, "bar_start_timestamp")
    prices = tuple(
        _require_decimal(value, name)
        for value, name in (
            (row.open_price, "open_price"),
            (row.high_price, "high_price"),
            (row.low_price, "low_price"),
            (row.close_price, "close_price"),
        )
    )
    _validate_price_geometry(*prices)
    ticks = tuple(_decimal_to_ticks(value, GC_DATASET_TICK_SIZE) for value in prices)
    volume = _require_nonnegative_int(row.volume, "volume")
    trades = _require_nonnegative_int(row.number_of_trades, "number_of_trades")
    bid = _require_nonnegative_int(row.bid_volume, "bid_volume")
    ask = _require_nonnegative_int(row.ask_volume, "ask_volume")
    if volume != bid + ask:
        raise ValueError("volume conservation")
    if volume == 0 and trades == 0:
        raise ValueError("synthetic no-data row")
    start_utc = local_start.replace(tzinfo=source_zone).astimezone(_UTC)
    close_utc = start_utc + _FIVE_MINUTES
    if close_utc > capture:
        raise ValueError("bar after capture")
    normalized_row = GCSierraChartBarRow(
        row_number, local_start, prices[0], prices[1], prices[2], prices[3], volume, trades, bid, ask
    )
    return _ValidatedRow(normalized_row, start_utc, close_utc, *ticks)


def _scan_coverage_evidence(
    entries: tuple[GCSierraChartCoverageEvidence, ...] | None,
) -> tuple[tuple[_NormalizedCoverage, ...], tuple[_Issue, ...]]:
    if entries is None:
        return (), ()
    if type(entries) is not tuple:
        return (), (_Issue(GCDatasetBuildStatus.INVALID, "COVERAGE_NOT_TUPLE", None),)
    normalized: list[_NormalizedCoverage] = []
    issues: list[_Issue] = []
    keys: list[tuple[datetime, datetime, tuple[int, int], str, str]] = []
    ids: set[str] = set()
    for item in entries:
        moment = _coverage_first_moment(item)
        try:
            if not isinstance(item, GCSierraChartCoverageEvidence):
                raise _ValidationError("MALFORMED_COVERAGE_TYPE", moment)
            source_id = _require_hash(item.source_id, "coverage.source_id")
            source_name = _normalize_source_name(item.source_name)
            source_sha256 = _require_hash(
                item.source_sha256, "coverage.source_sha256"
            )
            contract = _normalize_contract(item.contract)
            role = _require_enum(item.role, GCSourceRole, "coverage.role")
            capture = _normalize_aware_timestamp(
                item.capture_timestamp, name="coverage.capture_timestamp"
            )
            chart_timezone = _normalize_exact_text(
                item.chart_timezone,
                expected=GC_DATASET_SOURCE_TIMEZONE,
                name="coverage.chart_timezone",
                uppercase=False,
            )
            timeframe = _normalize_exact_text(
                item.timeframe,
                expected=GC_DATASET_TIMEFRAME,
                name="coverage.timeframe",
            )
            start = _normalize_aware_timestamp(
                item.coverage_start_timestamp,
                name="coverage_start_timestamp",
            )
            end = _normalize_aware_timestamp(
                item.coverage_end_timestamp,
                name="coverage_end_timestamp",
            )
            completed = _normalize_aware_timestamp(
                item.acquisition_completed_timestamp,
                name="acquisition_completed_timestamp",
            )
            evidence_hash = _require_hash(
                item.acquisition_evidence_sha256,
                "acquisition_evidence_sha256",
            )
            expected_id = make_gc_dataset_id(
                identity_kind="COVERAGE",
                source_id=source_id,
                source_name=source_name,
                source_sha256=source_sha256,
                contract=contract,
                role=role,
                capture_timestamp=capture,
                source_timezone=chart_timezone,
                timeframe=timeframe,
                coverage_start_timestamp=start,
                coverage_end_timestamp=end,
                acquisition_completed_timestamp=completed,
                acquisition_evidence_sha256=evidence_hash,
            )
            coverage_id = _require_hash(item.coverage_id, "coverage_id")
            if coverage_id != expected_id:
                raise _ValidationError("COVERAGE_ID_MISMATCH", start)
            if coverage_id in ids:
                raise _ValidationError("DUPLICATE_COVERAGE_ID", start)
            ids.add(coverage_id)
            normalized_item = _NormalizedCoverage(
                coverage_id,
                source_id,
                source_name,
                source_sha256,
                contract,
                role,
                capture,
                chart_timezone,
                timeframe,
                start,
                end,
                completed,
                evidence_hash,
            )
            normalized.append(normalized_item)
            keys.append((start, end, _contract_key(contract), role.value, coverage_id))
        except _ValidationError as exc:
            issues.append(
                _Issue(GCDatasetBuildStatus.INVALID, exc.reason, exc.moment or moment)
            )
        except (TypeError, ValueError):
            issues.append(
                _Issue(GCDatasetBuildStatus.INVALID, "MALFORMED_COVERAGE_EVIDENCE", moment)
            )
    if len(keys) > 1 and any(right <= left for left, right in zip(keys, keys[1:])):
        issues.append(
            _Issue(GCDatasetBuildStatus.INVALID, "COVERAGE_TUPLE_OUT_OF_ORDER", None)
        )
    by_source: dict[str, list[_NormalizedCoverage]] = {}
    for item in normalized:
        by_source.setdefault(item.source_id, []).append(item)
    for members in by_source.values():
        ordered = sorted(members, key=lambda item: (item.start, item.end, item.coverage_id))
        for left, right in zip(ordered, ordered[1:]):
            if right.start < left.end:
                issues.append(
                    _Issue(
                        GCDatasetBuildStatus.INVALID,
                        "OVERLAPPING_COVERAGE_EVIDENCE",
                        right.start,
                    )
                )
    return tuple(normalized), tuple(issues)


def _reconcile_coverage(
    *,
    exports: tuple[GCSierraChartExport, ...],
    coverage: tuple[_NormalizedCoverage, ...],
    rows: tuple[_InputRow, ...],
) -> tuple[tuple[_NormalizedCoverage, ...], tuple[_Issue, ...]]:
    source_map = {item.source_id: item for item in exports}
    by_source: dict[str, list[_NormalizedCoverage]] = {}
    linked: list[_NormalizedCoverage] = []
    issues: list[_Issue] = []
    for item in coverage:
        source = source_map.get(item.source_id)
        if source is None:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "COVERAGE_SOURCE_MISSING",
                    item.start,
                )
            )
            continue
        if (
            item.source_name != source.source_name
            or item.source_sha256 != source.source_sha256
            or item.contract != source.contract
            or item.role is not source.role
            or item.capture_timestamp != source.capture_timestamp
            or item.chart_timezone != source.chart_timezone
            or item.timeframe != source.timeframe
        ):
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "COVERAGE_SOURCE_MISMATCH",
                    item.start,
                )
            )
            continue
        by_source.setdefault(item.source_id, []).append(item)
        linked.append(item)
    for source in exports:
        members = by_source.get(source.source_id, [])
        if not members:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.UNKNOWN,
                    "COVERAGE_UNVERIFIED",
                    _export_first_moment(source),
                )
            )
    for item in rows:
        members = by_source.get(item.source.source_id, [])
        if members and not any(
            member.start <= item.start_utc and item.close_utc <= member.end
            for member in members
        ):
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "COVERAGE_MISMATCH",
                    item.close_utc,
                )
            )
    return tuple(linked), tuple(issues)


def _scan_calendars(
    entries: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ] | None,
    config: GCDatasetBuildConfig,
) -> tuple[tuple[_NormalizedCalendar, ...], tuple[_Issue, ...]]:
    if entries is None:
        return (), ()
    if type(entries) is not tuple:
        return (), (_Issue(GCDatasetBuildStatus.INVALID, "CALENDAR_NOT_TUPLE", None),)
    normalized: list[_NormalizedCalendar] = []
    issues: list[_Issue] = []
    prior_date: date | None = None
    version: str | None = None
    for item in entries:
        moment: datetime | None = None
        try:
            if not isinstance(
                item, (KillZoneCalendarEntry, GCSplitSessionCalendarEntry)
            ):
                raise _ValidationError("MALFORMED_CALENDAR_TYPE")
            trade_date = _require_date(item.trade_date, "calendar.trade_date")
            calendar_version = _normalize_nonempty_text(item.calendar_version, "calendar_version")
            expected_open, standard_close = _standard_bounds(trade_date)
            moment = expected_open
            if prior_date is not None and trade_date <= prior_date:
                raise _ValidationError("CALENDAR_OUT_OF_ORDER", expected_open)
            if version is not None and calendar_version != version:
                raise _ValidationError("CALENDAR_VERSION_MISMATCH", expected_open)
            if isinstance(item, KillZoneCalendarEntry):
                status = _require_enum(
                    item.session_status, KillZoneSessionStatus, "session_status"
                )
                if status is KillZoneSessionStatus.SESSION_CLOSED:
                    if (
                        item.session_open_timestamp is not None
                        or item.session_close_timestamp is not None
                    ):
                        raise _ValidationError(
                            "CLOSED_SESSION_HAS_TIMESTAMPS", expected_open
                        )
                    intervals: tuple[tuple[datetime, datetime], ...] = ()
                else:
                    opening = _normalize_aware_timestamp(
                        _required(
                            item.session_open_timestamp,
                            "session_open_timestamp",
                        ),
                        name="session_open_timestamp",
                    )
                    closing = _normalize_aware_timestamp(
                        _required(
                            item.session_close_timestamp,
                            "session_close_timestamp",
                        ),
                        name="session_close_timestamp",
                    )
                    if opening != expected_open:
                        raise _ValidationError(
                            "CALENDAR_OPEN_MISMATCH", expected_open
                        )
                    if (
                        status is KillZoneSessionStatus.OPEN
                        and closing != standard_close
                    ):
                        raise _ValidationError(
                            "STANDARD_CLOSE_MISMATCH", expected_open
                        )
                    if status is KillZoneSessionStatus.EARLY_CLOSE and not (
                        opening < closing <= standard_close
                    ):
                        raise _ValidationError(
                            "EARLY_CLOSE_GEOMETRY_INVALID", expected_open
                        )
                    intervals = ((opening, closing),)
                source_artifact_ids: tuple[str, ...] = ()
                source_artifact_sha256s: tuple[str, ...] = ()
                kind = "SINGLE_INTERVAL"
            else:
                status = KillZoneSessionStatus.OPEN
                intervals = _normalize_split_intervals(item.intervals, expected_open)
                source_artifact_ids, source_artifact_sha256s = (
                    _normalize_split_provenance(
                        item.source_artifact_ids,
                        item.source_artifact_sha256s,
                        expected_open,
                    )
                )
                kind = "SPLIT_SESSION"
            normalized.append(
                _NormalizedCalendar(
                    calendar_version,
                    trade_date,
                    status,
                    intervals,
                    source_artifact_ids,
                    source_artifact_sha256s,
                    kind,
                )
            )
            prior_date = trade_date
            version = calendar_version
        except _ValidationError as exc:
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, exc.reason, exc.moment or moment))
        except (TypeError, ValueError):
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, "MALFORMED_CALENDAR_ENTRY", moment))
    ordered_intervals = sorted(
        (
            start,
            end,
            entry.trade_date,
        )
        for entry in normalized
        for start, end in entry.intervals
    )
    for left, right in zip(ordered_intervals, ordered_intervals[1:]):
        if right[0] < left[1]:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.INVALID,
                    "CALENDAR_INTERVAL_OVERLAP",
                    right[0],
                )
            )
            break
    return tuple(normalized), tuple(issues)


def _normalize_split_intervals(
    value: object, moment: datetime
) -> tuple[tuple[datetime, datetime], ...]:
    if type(value) is not tuple:
        raise _ValidationError("SPLIT_SESSION_INTERVALS_NOT_TUPLE", moment)
    if len(value) < 2:
        raise _ValidationError("SPLIT_SESSION_REQUIRES_MULTIPLE_INTERVALS", moment)
    output: list[tuple[datetime, datetime]] = []
    prior_start: datetime | None = None
    prior_end: datetime | None = None
    width = int(_FIVE_MINUTES.total_seconds())
    for member in value:
        if not isinstance(member, GCDatasetSessionInterval):
            raise _ValidationError("MALFORMED_SPLIT_SESSION_INTERVAL", moment)
        start = _normalize_aware_timestamp(
            member.start_timestamp, name="interval.start_timestamp"
        )
        end = _normalize_aware_timestamp(
            member.end_timestamp, name="interval.end_timestamp"
        )
        if start >= end:
            raise _ValidationError("SPLIT_SESSION_INTERVAL_GEOMETRY_INVALID", start)
        if (
            start.second
            or start.microsecond
            or start.minute % 5
            or end.second
            or end.microsecond
            or end.minute % 5
            or int((end - start).total_seconds()) % width
        ):
            raise _ValidationError("SPLIT_SESSION_INTERVAL_OFF_GRID", start)
        if prior_end is not None:
            if prior_start is not None and start <= prior_start:
                raise _ValidationError(
                    "SPLIT_SESSION_INTERVALS_OUT_OF_ORDER", start
                )
            if start < prior_end:
                raise _ValidationError("SPLIT_SESSION_INTERVAL_OVERLAP", start)
            if start == prior_end:
                raise _ValidationError("SPLIT_SESSION_INTERVALS_TOUCH", start)
        output.append((start, end))
        prior_start = start
        prior_end = end
    return tuple(output)


def _normalize_split_provenance(
    ids_value: object,
    hashes_value: object,
    moment: datetime,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if type(ids_value) is not tuple or type(hashes_value) is not tuple:
        raise _ValidationError("SOURCE_ARTIFACT_PROVENANCE_NOT_TUPLE", moment)
    if not ids_value or len(ids_value) != len(hashes_value):
        raise _ValidationError("CALENDAR_SOURCE_ARTIFACT_LENGTH_MISMATCH", moment)
    ids = tuple(
        _normalize_nonempty_text(item, "source_artifact_id")
        for item in ids_value
    )
    if len(set(ids)) != len(ids):
        raise _ValidationError("DUPLICATE_CALENDAR_SOURCE_ARTIFACT", moment)
    if any(right < left for left, right in zip(ids, ids[1:])):
        raise _ValidationError("CALENDAR_SOURCE_ARTIFACTS_OUT_OF_ORDER", moment)
    hashes = tuple(
        _require_hash(
            _normalize_nonempty_text(item, "source_artifact_sha256").lower(),
            "source_artifact_sha256",
        )
        for item in hashes_value
    )
    if len(set(zip(ids, hashes, strict=True))) != len(ids):
        raise _ValidationError("SOURCE_ARTIFACT_PROVENANCE_DUPLICATE", moment)
    return ids, hashes


def _merge_rows(
    rows: tuple[_InputRow, ...],
    exports: tuple[GCSierraChartExport, ...],
) -> tuple[tuple[_MergedRow, ...], tuple[_Issue, ...]]:
    rank = {source.source_id: index for index, source in enumerate(exports)}
    groups: dict[tuple[str, datetime], list[_InputRow]] = {}
    for item in rows:
        groups.setdefault((item.source.contract, item.start_utc), []).append(item)
    merged: list[_MergedRow] = []
    issues: list[_Issue] = []
    for (contract, _), members in sorted(
        groups.items(), key=lambda pair: (pair[0][1], _contract_key(pair[0][0]))
    ):
        reference = members[0]
        reference_value = _row_value(reference)
        if any(_row_value(member) != reference_value for member in members[1:]):
            issues.append(_Issue(GCDatasetBuildStatus.INVALID, "OVERLAPPING_ROW_CONFLICT", reference.close_utc))
            continue
        ordered_members = sorted(members, key=lambda member: rank[member.source.source_id])
        merged.append(
            _MergedRow(
                contract=contract,
                start_utc=reference.start_utc,
                close_utc=reference.close_utc,
                open_tick=reference.open_tick,
                high_tick=reference.high_tick,
                low_tick=reference.low_tick,
                close_tick=reference.close_tick,
                volume=reference.row.volume,
                number_of_trades=reference.row.number_of_trades,
                bid_volume=reference.row.bid_volume,
                ask_volume=reference.row.ask_volume,
                source_ids=tuple(member.source.source_id for member in ordered_members),
                source_row_numbers=tuple(
                    member.row.source_row_number for member in ordered_members
                ),
                roles=tuple(member.source.role for member in ordered_members),
                capture_timestamps=tuple(member.source.capture_timestamp for member in ordered_members),
                instance_count=len(members),
            )
        )
    return tuple(merged), tuple(issues)


def _calendar_outer_domain(
    calendars: tuple[_NormalizedCalendar, ...],
) -> tuple[datetime, datetime] | None:
    intervals = tuple(
        interval
        for calendar in calendars
        for interval in calendar.intervals
    )
    if not intervals:
        return None
    domain_start = min(start for start, _ in intervals)
    domain_end = max(end for _, end in intervals)
    if domain_start >= domain_end:
        return None
    return domain_start, domain_end


def _completed_session_volumes(
    rows: list[_UsableRow],
    calendars: tuple[_NormalizedCalendar, ...],
    exports: tuple[GCSierraChartExport, ...],
    coverage: tuple[_NormalizedCoverage, ...],
    config: GCDatasetBuildConfig,
) -> tuple[tuple[tuple[str, date, int], ...], tuple[tuple[str, date, int], ...]]:
    source_by_id = {source.source_id: source for source in exports}
    coverage_by_contract_role: dict[
        tuple[str, GCSourceRole], list[_NormalizedCoverage]
    ] = {}
    for item in coverage:
        coverage_by_contract_role.setdefault((item.contract, item.role), []).append(item)
    grouped: dict[tuple[str, date], list[_UsableRow]] = {}
    for item in rows:
        grouped.setdefault((item.merged.contract, item.trade_date), []).append(item)
    output: list[tuple[str, date, int]] = []
    missing_output: list[tuple[str, date, int]] = []
    contracts = tuple(dict.fromkeys(source.contract for source in exports))
    for contract in contracts:
        for entry in calendars:
            trade_date = entry.trade_date
            if entry.opening is None or entry.closing is None:
                continue
            partition = _partition_for_trade_date(trade_date, config)
            if partition is None:
                required_role = GCSourceRole.DEVELOPMENT
            else:
                required_role = (
                    GCSourceRole.DEVELOPMENT
                    if partition is GCSegmentPartition.DEVELOPMENT
                    else GCSourceRole.OOS_HOLDOUT
                )
            accepted = tuple(
                item
                for item in coverage_by_contract_role.get(
                    (contract, required_role), ()
                )
                if item.capture_timestamp > entry.closing
                and (
                    item.acquisition_completed > entry.closing
                    if entry.kind == "SPLIT_SESSION"
                    else item.acquisition_completed >= entry.closing
                )
            )
            if not accepted:
                continue
            expected: list[datetime] = []
            for interval_start, interval_end in entry.intervals:
                cursor = interval_start
                while cursor + _FIVE_MINUTES <= interval_end:
                    expected.append(cursor)
                    cursor += _FIVE_MINUTES
            if not all(
                any(
                    item.start <= slot
                    and slot + _FIVE_MINUTES <= item.end
                    for item in accepted
                )
                for slot in expected
            ):
                continue
            members = grouped.get((contract, trade_date), [])
            observed_by_start = {
                member.merged.start_utc: member
                for member in members
                if any(
                    source_by_id[source_id].role is required_role
                    for source_id in member.selected_source_ids
                )
            }
            if any(start not in expected for start in observed_by_start):
                continue
            missing = sum(1 for slot in expected if slot not in observed_by_start)
            if entry.kind == "SPLIT_SESSION" and missing:
                continue
            output.append(
                (
                    contract,
                    trade_date,
                    sum(
                        item.merged.volume
                        for item in observed_by_start.values()
                    ),
                )
            )
            missing_output.append((contract, trade_date, missing))
    output.sort(key=lambda item: (_contract_key(item[0]), item[1]))
    missing_output.sort(key=lambda item: (_contract_key(item[0]), item[1]))
    return tuple(output), tuple(missing_output)


def _initial_contract_issue(
    *,
    contracts: tuple[str, ...],
    calendars: tuple[_NormalizedCalendar, ...],
    completed_volumes: dict[tuple[str, date], int],
    config: GCDatasetBuildConfig,
) -> _Issue | None:
    moment = _calendar_open_for(config.initial_trade_date, calendars)
    predecessor = _previous_contract(config.initial_contract)
    if config.initial_contract not in contracts or predecessor not in contracts:
        return _Issue(
            GCDatasetBuildStatus.UNKNOWN,
            "INITIAL_PREDECESSOR_COVERAGE_MISSING",
            moment,
        )
    eligible = tuple(
        entry
        for entry in calendars
        if entry.session_status is not KillZoneSessionStatus.SESSION_CLOSED
    )
    positions = [
        index
        for index, entry in enumerate(eligible)
        if entry.trade_date == config.initial_trade_date
    ]
    if len(positions) != 1 or positions[0] < GC_ROLL_CONFIRMATION_SESSIONS:
        return _Issue(
            GCDatasetBuildStatus.UNKNOWN,
            "INITIAL_CONFIRMATION_CALENDAR_MISSING",
            moment,
        )
    position = positions[0]
    confirmation = eligible[position - GC_ROLL_CONFIRMATION_SESSIONS : position]
    for entry in confirmation:
        previous_volume = completed_volumes.get((predecessor, entry.trade_date))
        current_volume = completed_volumes.get(
            (config.initial_contract, entry.trade_date)
        )
        if previous_volume is None or current_volume is None:
            return _Issue(
                GCDatasetBuildStatus.UNKNOWN,
                "INITIAL_CONFIRMATION_VOLUME_MISSING",
                entry.closing,
            )
        if current_volume <= previous_volume:
            return _Issue(
                GCDatasetBuildStatus.INVALID,
                "INITIAL_CONTRACT_DOMINANCE_CONTRADICTION",
                entry.closing,
            )
    return None


def _roll_plan(
    *,
    contracts: tuple[str, ...],
    calendars: tuple[_NormalizedCalendar, ...],
    completed_volumes: dict[tuple[str, date], int],
    config: GCDatasetBuildConfig,
) -> tuple[dict[date, str], tuple[date, ...], tuple[_Issue, ...]]:
    if config.initial_contract not in contracts:
        opening = _calendar_open_for(config.initial_trade_date, calendars)
        return {}, (), (_Issue(GCDatasetBuildStatus.UNKNOWN, "INITIAL_CONTRACT_COVERAGE_MISSING", opening),)
    active = config.initial_contract
    eligible = tuple(
        entry
        for entry in calendars
        if entry.session_status is not KillZoneSessionStatus.SESSION_CLOSED
        and config.initial_trade_date <= entry.trade_date <= config.oos_end_trade_date
    )
    active_by_date: dict[date, str] = {}
    scheduled: dict[date, str] = {}
    dominance_count = 0
    roll_dates: list[date] = []
    issues: list[_Issue] = []
    for position, entry in enumerate(eligible):
        if entry.trade_date in scheduled:
            active = scheduled[entry.trade_date]
            dominance_count = 0
            roll_dates.append(entry.trade_date)
        active_by_date[entry.trade_date] = active
        adjacent = _next_contract(active)
        if adjacent not in contracts:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.UNKNOWN,
                    "ADJACENT_CONTRACT_COVERAGE_MISSING",
                    entry.closing,
                )
            )
            dominance_count = 0
            continue
        current_volume = completed_volumes.get((active, entry.trade_date))
        adjacent_volume = completed_volumes.get((adjacent, entry.trade_date))
        if current_volume is None or adjacent_volume is None:
            issues.append(
                _Issue(
                    GCDatasetBuildStatus.UNKNOWN,
                    "COMPARABLE_COMPLETED_VOLUME_MISSING",
                    entry.closing,
                )
            )
            dominance_count = 0
            continue
        dominance_count = dominance_count + 1 if adjacent_volume > current_volume else 0
        if dominance_count >= GC_ROLL_CONFIRMATION_SESSIONS:
            if position + 1 >= len(eligible):
                issues.append(
                    _Issue(
                        GCDatasetBuildStatus.UNKNOWN,
                        "ROLL_EFFECTIVE_SESSION_MISSING",
                        entry.closing,
                    )
                )
            else:
                scheduled[eligible[position + 1].trade_date] = adjacent
    return active_by_date, tuple(roll_dates), tuple(issues)


def _make_segments(
    rows: tuple[_UsableRow, ...],
    config: GCDatasetBuildConfig,
    source_rank: dict[str, int],
    calendar_map: dict[date, _NormalizedCalendar],
) -> tuple[GCCanonicalContractSegment, ...]:
    ordered = sorted(rows, key=lambda item: (item.merged.close_utc, _contract_key(item.merged.contract)))
    groups: list[tuple[list[_UsableRow], int]] = []
    current: list[_UsableRow] = []
    current_preceding_missing = 0
    prior: _UsableRow | None = None
    for item in ordered:
        split = False
        preceding_missing = 0
        if prior is None:
            entry = calendar_map.get(item.trade_date)
            interval = _calendar_interval_for_bar(
                entry, item.merged.start_utc, item.merged.close_utc
            )
            if interval is not None:
                preceding_missing = _missing_slot_count(
                    interval[0], item.merged.start_utc
                )
                current_preceding_missing = preceding_missing
        else:
            same_context = (
                item.merged.contract == prior.merged.contract
                and item.partition is prior.partition
                and item.trade_date == prior.trade_date
                and item.selected_coverage_ids == prior.selected_coverage_ids
            )
            delta = item.merged.start_utc - prior.merged.start_utc
            if not same_context or delta != _FIVE_MINUTES:
                split = True
                if same_context and delta > _FIVE_MINUTES:
                    entry = calendar_map.get(item.trade_date)
                    if not _is_official_calendar_gap(
                        entry,
                        prior.merged.start_utc,
                        item.merged.start_utc,
                    ):
                        preceding_missing = _missing_slot_count(
                            prior.merged.start_utc + _FIVE_MINUTES,
                            item.merged.start_utc,
                        )
                elif item.trade_date != prior.trade_date:
                    entry = calendar_map.get(item.trade_date)
                    interval = _calendar_interval_for_bar(
                        entry, item.merged.start_utc, item.merged.close_utc
                    )
                    if interval is not None:
                        preceding_missing = _missing_slot_count(
                            interval[0], item.merged.start_utc
                        )
        if split and current:
            groups.append((current, current_preceding_missing))
            current = []
            current_preceding_missing = preceding_missing
        current.append(item)
        prior = item
    if current:
        groups.append((current, current_preceding_missing))

    output: list[GCCanonicalContractSegment] = []
    for members, missing_before in groups:
        bars = tuple(
            GCChronologicalBar(
                index=index,
                timestamp=item.merged.close_utc,
                open_tick=item.merged.open_tick,
                high_tick=item.merged.high_tick,
                low_tick=item.merged.low_tick,
                close_tick=item.merged.close_tick,
                volume=item.merged.volume,
                is_closed=True,
            )
            for index, item in enumerate(members)
        )
        source_ids = tuple(
            sorted(
                {source_id for item in members for source_id in item.selected_source_ids},
                key=source_rank.__getitem__,
            )
        )
        digest = _digest_bars(bars)
        first = members[0]
        last = members[-1]
        segment_id = make_gc_dataset_id(
            identity_kind="SEGMENT",
            config=config,
            contract=first.merged.contract,
            partition=first.partition,
            first_trade_date=first.trade_date,
            last_trade_date=last.trade_date,
            source_ids=source_ids,
            bar_digest=digest,
            preceding_missing_bar_count=missing_before,
        )
        output.append(
            GCCanonicalContractSegment(
                segment_id,
                first.merged.contract,
                first.partition,
                first.trade_date,
                last.trade_date,
                source_ids,
                bars,
                missing_before,
            )
        )
    return tuple(output)


def _calendar_interval_for_bar(
    entry: _NormalizedCalendar | None,
    start: datetime,
    close: datetime,
) -> tuple[datetime, datetime] | None:
    if entry is None:
        return None
    matches = tuple(
        interval
        for interval in entry.intervals
        if interval[0] <= start and close <= interval[1]
    )
    return matches[0] if len(matches) == 1 else None


def _is_official_calendar_gap(
    entry: _NormalizedCalendar | None,
    prior_start: datetime,
    next_start: datetime,
) -> bool:
    if entry is None or len(entry.intervals) < 2:
        return False
    return any(
        prior_start + _FIVE_MINUTES == left[1]
        and next_start == right[0]
        for left, right in zip(entry.intervals, entry.intervals[1:])
    )


def _missing_slot_count(start: datetime, end: datetime) -> int:
    delta = end - start
    seconds = int(delta.total_seconds())
    width = int(_FIVE_MINUTES.total_seconds())
    if seconds < 0 or seconds % width:
        raise _ValidationError("nonintegral missing-bar gap")
    return seconds // width


def _attested_official_gap_count(
    rows: tuple[_UsableRow, ...],
    calendar_map: dict[date, _NormalizedCalendar],
) -> int:
    starts_by_scope: dict[tuple[str, date], set[datetime]] = {}
    for row in rows:
        starts_by_scope.setdefault(
            (row.merged.contract, row.trade_date), set()
        ).add(row.merged.start_utc)
    count = 0
    for (_, trade_date), starts in starts_by_scope.items():
        entry = calendar_map.get(trade_date)
        if entry is None or len(entry.intervals) < 2:
            continue
        represented = tuple(
            any(interval_start <= start < interval_end for start in starts)
            for interval_start, interval_end in entry.intervals
        )
        count += sum(
            1
            for left_present, right_present in zip(
                represented, represented[1:]
            )
            if left_present and right_present
        )
    return count


def _normalize_config(value: object) -> GCDatasetBuildConfig:
    if not isinstance(value, GCDatasetBuildConfig):
        raise TypeError("config must be GCDatasetBuildConfig")
    runtime_version = _runtime_timezone_data_version()
    if runtime_version is None:
        raise ValueError("runtime timezone-data version is unavailable")
    _load_zone(GC_DATASET_SOURCE_TIMEZONE)
    _load_zone(GC_DATASET_EXCHANGE_TIMEZONE)
    instrument = _normalize_exact_text(value.instrument, expected=GC_DATASET_INSTRUMENT, name="instrument")
    timeframe = _normalize_exact_text(value.timeframe, expected=GC_DATASET_TIMEFRAME, name="timeframe")
    source_timezone = _normalize_exact_text(
        value.source_timezone,
        expected=GC_DATASET_SOURCE_TIMEZONE,
        name="source_timezone",
        uppercase=False,
    )
    exchange_timezone = _normalize_exact_text(
        value.exchange_timezone,
        expected=GC_DATASET_EXCHANGE_TIMEZONE,
        name="exchange_timezone",
        uppercase=False,
    )
    timezone_version = _normalize_nonempty_text(value.timezone_data_version, "timezone_data_version")
    if timezone_version != runtime_version:
        raise ValueError("timezone-data version mismatch")
    tick_size = _require_decimal(value.tick_size, "tick_size")
    if tick_size != GC_DATASET_TICK_SIZE:
        raise ValueError("tick_size mismatch")
    initial_contract = _normalize_contract(value.initial_contract)
    initial_date = _require_date(value.initial_trade_date, "initial_trade_date")
    confirmation = _require_nonnegative_int(value.roll_confirmation_sessions, "roll_confirmation_sessions")
    if confirmation != GC_ROLL_CONFIRMATION_SESSIONS:
        raise ValueError("roll confirmation count mismatch")
    oos_start = _require_date(value.oos_start_trade_date, "oos_start_trade_date")
    oos_end = _require_date(value.oos_end_trade_date, "oos_end_trade_date")
    if not (initial_date < oos_start <= oos_end):
        raise ValueError("OOS date range must follow initial trade date")
    return GCDatasetBuildConfig(
        instrument,
        timeframe,
        source_timezone,
        exchange_timezone,
        timezone_version,
        tick_size,
        initial_contract,
        initial_date,
        confirmation,
        oos_start,
        oos_end,
    )


def _config_payload(config: GCDatasetBuildConfig) -> dict[str, object]:
    return {
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
    }


def _runtime_timezone_data_version() -> str | None:
    try:
        value = metadata.version("tzdata")
    except metadata.PackageNotFoundError:
        return None
    return value.strip() or None


def _load_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise ValueError(f"timezone unavailable: {name}") from exc


def _standard_bounds(trade_date: date) -> tuple[datetime, datetime]:
    zone = _load_zone(GC_DATASET_EXCHANGE_TIMEZONE)
    opening = datetime.combine(
        trade_date - timedelta(days=1), time(18), tzinfo=zone
    ).astimezone(_UTC)
    closing = datetime.combine(trade_date, time(17), tzinfo=zone).astimezone(_UTC)
    return opening, closing


def _trade_date_for_start(start_utc: datetime) -> date:
    local = start_utc.astimezone(_load_zone(GC_DATASET_EXCHANGE_TIMEZONE))
    if local.time() >= time(18):
        return local.date() + timedelta(days=1)
    return local.date()


def _partition_for_trade_date(
    trade_date: date, config: GCDatasetBuildConfig
) -> GCSegmentPartition | None:
    if trade_date < config.initial_trade_date or trade_date > config.oos_end_trade_date:
        return None
    if trade_date >= config.oos_start_trade_date:
        return GCSegmentPartition.OOS_HOLDOUT
    return GCSegmentPartition.DEVELOPMENT


def _normalize_contract(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("contract must be str")
    normalized = value.strip().upper()
    if _CONTRACT_PATTERN.fullmatch(normalized) is None:
        raise ValueError("contract must be exact GC delivery token")
    return normalized


def _contract_key(contract: str) -> tuple[int, int]:
    match = _CONTRACT_PATTERN.fullmatch(_normalize_contract(contract))
    if match is None:  # pragma: no cover
        raise ValueError("invalid contract")
    year = 2000 + int(match.group(2))
    return year, GC_DELIVERY_MONTH_CODES.index(match.group(1))


def _next_contract(contract: str) -> str:
    match = _CONTRACT_PATTERN.fullmatch(_normalize_contract(contract))
    if match is None:  # pragma: no cover
        raise ValueError("invalid contract")
    code = match.group(1)
    year = int(match.group(2))
    position = GC_DELIVERY_MONTH_CODES.index(code)
    if position + 1 == len(GC_DELIVERY_MONTH_CODES):
        position = 0
        year = (year + 1) % 100
    else:
        position += 1
    return f"GC{GC_DELIVERY_MONTH_CODES[position]}{year:02d}-COMEX"


def _previous_contract(contract: str) -> str:
    match = _CONTRACT_PATTERN.fullmatch(_normalize_contract(contract))
    if match is None:  # pragma: no cover
        raise ValueError("invalid contract")
    code = match.group(1)
    year = int(match.group(2))
    position = GC_DELIVERY_MONTH_CODES.index(code)
    if position == 0:
        position = len(GC_DELIVERY_MONTH_CODES) - 1
        year = (year - 1) % 100
    else:
        position -= 1
    return f"GC{GC_DELIVERY_MONTH_CODES[position]}{year:02d}-COMEX"


def _parse_raw_start(day: str, clock: str) -> datetime:
    if _DATE_PATTERN.fullmatch(day) is None or _TIME_PATTERN.fullmatch(clock) is None:
        raise ValueError("raw Date/Time format is invalid")
    try:
        year_text, month_text, day_text = day.split("-")
        hour_text, minute_text, second_text = clock.split(":")
        second, microsecond = second_text.split(".")
        value = datetime(
            int(year_text),
            int(month_text),
            int(day_text),
            int(hour_text),
            int(minute_text),
            int(second),
            int(microsecond),
        )
    except ValueError as exc:
        raise ValueError("raw Date/Time value is invalid") from exc
    if value.tzinfo is not None:
        raise ValueError("raw Date/Time must be naive")
    return value


def _parse_price(value: str, name: str) -> Decimal:
    number = _parse_finite_decimal(value, name)
    _decimal_to_ticks(number, GC_DATASET_TICK_SIZE)
    return number


def _parse_finite_decimal(value: object, name: str) -> Decimal:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{name} must be canonical Decimal text")
    if value.lower() in {"true", "false", "nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity"}:
        raise ValueError(f"{name} must be finite Decimal text")
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be finite Decimal text") from exc
    if not number.is_finite():
        raise ValueError(f"{name} must be finite")
    return number


def _parse_nonnegative_integer(value: str, name: str) -> int:
    if _NONNEGATIVE_INTEGER_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a nonnegative exact integer")
    return int(value)


def _validate_price_geometry(
    open_price: Decimal,
    high_price: Decimal,
    low_price: Decimal,
    close_price: Decimal,
) -> None:
    if low_price > high_price or not (low_price <= open_price <= high_price) or not (
        low_price <= close_price <= high_price
    ):
        raise ValueError("OHLC geometry is invalid")


def _decimal_to_ticks(value: Decimal, tick: Decimal) -> int:
    numerator, denominator = value.as_integer_ratio()
    tick_numerator, tick_denominator = tick.as_integer_ratio()
    combined_numerator = numerator * tick_denominator
    combined_denominator = denominator * tick_numerator
    if combined_denominator == 0 or combined_numerator % combined_denominator:
        raise ValueError("price is not aligned to tick size")
    return combined_numerator // combined_denominator


def _decimal_text(value: Decimal) -> str:
    number = _require_decimal(value, "decimal")
    if number.is_zero():
        return "0.0"
    text = format(number, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text + ".0" if "." not in text else text


def _normalize_source_name(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("source_name must be str")
    normalized = value.strip()
    if not normalized or normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise ValueError("source_name must be a nonempty basename")
    return normalized


def _normalize_identity_kind(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("identity_kind must be str")
    normalized = value.strip().upper()
    if normalized not in _IDENTITY_KINDS:
        raise ValueError("unknown identity kind")
    return normalized


def _normalize_exact_text(
    value: object,
    *,
    expected: str,
    name: str,
    uppercase: bool = True,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")
    normalized = value.strip().upper() if uppercase else value.strip()
    if normalized != expected:
        raise ValueError(f"{name} must equal {expected}")
    return expected


def _normalize_nonempty_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must be nonempty")
    return normalized


def _normalize_aware_timestamp(value: object, *, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(_UTC)


def _normalize_naive_timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be datetime")
    if value.tzinfo is not None:
        raise ValueError(f"{name} must be naive")
    return value


def _timestamp_text(value: datetime) -> str:
    return _normalize_aware_timestamp(value, name="timestamp").strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _require_decimal(value: object, name: str) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TypeError(f"{name} must be finite Decimal")
    return value


def _require_nonnegative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise TypeError(f"{name} must be nonnegative int")
    return value


def _require_date(value: object, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be date")
    return value


def _require_enum(value: object, enum_type: type[Enum], name: str):
    if not isinstance(value, enum_type):
        raise TypeError(f"{name} must be {enum_type.__name__}")
    return value


def _require_hash(value: object, name: str) -> str:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _required(value: object, name: str):
    if value is None:
        raise ValueError(f"{name} is required")
    return value


def _require_none(value: object, name: str) -> None:
    if value is not None:
        raise ValueError(f"{name} is forbidden")


def _require_empty(value: object, name: str) -> None:
    if type(value) is not tuple or value:
        raise ValueError(f"{name} is forbidden")


def _forbid_source_fields(*values: object) -> None:
    if any(value is not None for value in values):
        raise ValueError("source-local field is forbidden")


def _forbid_coverage_fields(*values: object) -> None:
    if any(value is not None for value in values):
        raise ValueError("coverage-local field is forbidden")


def _normalize_hash_tuple(value: object, name: str, *, nonempty: bool) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be tuple")
    output = tuple(_require_hash(item, name) for item in value)
    if nonempty and not output:
        raise ValueError(f"{name} must be nonempty")
    if len(set(output)) != len(output):
        raise ValueError(f"{name} must be unique")
    return output


def _normalize_date_tuple(value: object, name: str) -> tuple[date, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be tuple")
    output = tuple(_require_date(item, name) for item in value)
    if any(right <= left for left, right in zip(output, output[1:])):
        raise ValueError(f"{name} must be strictly increasing and unique")
    return output


def _digest_bars(bars: tuple[GCChronologicalBar, ...]) -> str:
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


def _digest_calendar(entries: tuple[_NormalizedCalendar, ...]) -> str:
    return _hash_payload(
        tuple(
            {
                "calendar_kind": item.kind,
                "calendar_version": item.calendar_version,
                "trade_date": item.trade_date.isoformat(),
                "session_status": item.session_status.value,
                "intervals": tuple(
                    {
                        "start_timestamp": _timestamp_text(start),
                        "end_timestamp": _timestamp_text(end),
                    }
                    for start, end in item.intervals
                ),
                "source_artifact_ids": item.source_artifact_ids,
                "source_artifact_sha256s": item.source_artifact_sha256s,
            }
            for item in entries
        )
    )


def _digest_coverage(entries: tuple[_NormalizedCoverage, ...]) -> str:
    return _hash_payload(
        tuple(
            {
                "source_id": item.source_id,
                "source_name": item.source_name,
                "source_sha256": item.source_sha256,
                "contract": item.contract,
                "role": item.role.value,
                "capture_timestamp": _timestamp_text(item.capture_timestamp),
                "chart_timezone": item.chart_timezone,
                "timeframe": item.timeframe,
                "coverage_start_timestamp": _timestamp_text(item.start),
                "coverage_end_timestamp": _timestamp_text(item.end),
                "acquisition_completed_timestamp": _timestamp_text(
                    item.acquisition_completed
                ),
                "acquisition_evidence_sha256": item.acquisition_evidence_sha256,
            }
            for item in entries
        )
    )


def _hash_payload(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _row_value(item: _InputRow) -> tuple[object, ...]:
    return (
        item.start_utc,
        item.open_tick,
        item.high_tick,
        item.low_tick,
        item.close_tick,
        item.row.volume,
        item.row.number_of_trades,
        item.row.bid_volume,
        item.row.ask_volume,
    )


def _row_effective_moment(row: object, zone: ZoneInfo) -> datetime | None:
    try:
        if not isinstance(row, GCSierraChartBarRow):
            return None
        local = _normalize_naive_timestamp(row.bar_start_timestamp, "bar_start_timestamp")
        return local.replace(tzinfo=zone).astimezone(_UTC) + _FIVE_MINUTES
    except (TypeError, ValueError):
        return None


def _export_first_moment(item: object) -> datetime | None:
    try:
        if not isinstance(item, GCSierraChartExport) or not item.rows:
            return _normalize_aware_timestamp(item.capture_timestamp, name="capture_timestamp") if isinstance(item, GCSierraChartExport) else None
        zone = _load_zone(GC_DATASET_SOURCE_TIMEZONE)
        return _row_effective_moment(item.rows[0], zone)
    except (TypeError, ValueError):
        return None


def _coverage_first_moment(item: object) -> datetime | None:
    try:
        if not isinstance(item, GCSierraChartCoverageEvidence):
            return None
        return _normalize_aware_timestamp(
            item.coverage_start_timestamp,
            name="coverage_start_timestamp",
        )
    except (TypeError, ValueError):
        try:
            return _normalize_aware_timestamp(
                item.capture_timestamp,
                name="capture_timestamp",
            )
        except (TypeError, ValueError):
            return None


def _calendar_open_for(
    trade_date: date, entries: tuple[_NormalizedCalendar, ...]
) -> datetime | None:
    for entry in entries:
        if entry.trade_date == trade_date:
            return entry.opening or _standard_bounds(trade_date)[0]
    try:
        return _standard_bounds(trade_date)[0]
    except (TypeError, ValueError):
        return None


def _earliest_issue_moment(issues: list[_Issue] | tuple[_Issue, ...]) -> datetime | None:
    if any(issue.moment is None for issue in issues):
        return None
    moments = [issue.moment for issue in issues if issue.moment is not None]
    return min(moments) if moments else None


def _highest_status(issues: list[_Issue] | tuple[_Issue, ...]) -> GCDatasetBuildStatus:
    precedence = {
        GCDatasetBuildStatus.INVALID: 5,
        GCDatasetBuildStatus.AMBIGUOUS: 4,
        GCDatasetBuildStatus.UNKNOWN: 3,
        GCDatasetBuildStatus.VALID: 2,
        GCDatasetBuildStatus.NONE: 1,
    }
    return max((issue.status for issue in issues), key=precedence.__getitem__)


def _ordered_issues(issues: list[_Issue] | tuple[_Issue, ...]) -> tuple[_Issue, ...]:
    return tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.moment is None,
                issue.moment or datetime.max.replace(tzinfo=_UTC),
                issue.reason,
            ),
        )
    )


def _issues_result(
    issues: list[_Issue] | tuple[_Issue, ...],
    *,
    segments: tuple[GCCanonicalContractSegment, ...],
) -> GCDatasetBuildResult:
    ordered = _ordered_issues(issues)
    status = _highest_status(ordered)
    reasons = tuple(item.reason for item in ordered)
    return GCDatasetBuildResult(status, None, segments, None, reasons, reasons)


def _result(status: GCDatasetBuildStatus, reason: str, detail: str) -> GCDatasetBuildResult:
    reasons = (reason, detail) if detail and detail != reason else (reason,)
    blocking = reasons if status in {GCDatasetBuildStatus.INVALID, GCDatasetBuildStatus.UNKNOWN} else ()
    return GCDatasetBuildResult(status, None, (), None, reasons, blocking)


__all__ = [
    "GC_DATASET_BUILDER_VERSION",
    "GC_DATASET_INSTRUMENT",
    "GC_DATASET_TIMEFRAME",
    "GC_DATASET_SOURCE_TIMEZONE",
    "GC_DATASET_EXCHANGE_TIMEZONE",
    "GC_DATASET_TICK_SIZE",
    "GC_ROLL_CONFIRMATION_SESSIONS",
    "GC_DELIVERY_MONTH_CODES",
    "GCDatasetBuildStatus",
    "GCSourceRole",
    "GCSegmentPartition",
    "GCDatasetSessionInterval",
    "GCSplitSessionCalendarEntry",
    "GCSierraChartBarRow",
    "GCSierraChartExport",
    "GCSierraChartCoverageEvidence",
    "GCCanonicalContractSegment",
    "GCDatasetManifest",
    "GCDatasetBuildConfig",
    "GCDatasetBuildResult",
    "parse_sierra_chart_gc_export",
    "make_gc_dataset_id",
    "build_gc_futures_dataset",
]
