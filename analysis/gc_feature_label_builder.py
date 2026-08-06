from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import importlib.metadata
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCSegmentPartition,
    make_gc_dataset_id,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.dealing_range import (
    DEALING_RANGE_DETECTOR_VERSION,
    DealingRangeEventType,
    DealingRangeKind,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
    DealingRangeTransition,
    make_dealing_range_id,
)
from smc.equal_liquidity import (
    EQUAL_LIQUIDITY_DETECTOR_VERSION,
    EqualLiquidityPool,
    EqualLiquiditySide,
    make_equal_liquidity_id,
)
from smc.fair_value_gap import (
    FAIR_VALUE_GAP_DETECTOR_VERSION,
    FairValueGap,
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    make_fair_value_gap_id,
)
from smc.inducement import (
    INDUCEMENT_DETECTOR_VERSION,
    Inducement,
    InducementSnapshot,
    make_inducement_id,
)
from smc.kill_zones import (
    KILL_ZONE_DETECTOR_VERSION,
    KillZoneCalendarEntry,
    KillZoneContext,
    KillZoneName,
    KillZoneQuality,
    KillZoneSessionStatus,
    KillZoneSnapshot,
    make_kill_zone_id,
)
from smc.liquidity_map import (
    LIQUIDITY_MAP_DETECTOR_VERSION,
    LiquidityClassification,
    LiquidityMapSnapshot,
    LiquidityReclassification,
    LiquidityScope,
    LiquiditySide,
    LiquiditySourceKind,
    make_liquidity_map_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2LifecycleEvent,
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    validate_lifecycle_history,
)


GC_FEATURE_LABEL_VERSION = "GC-FEATURE-LABEL-V1"
GC_AI_FEATURE_SCHEMA_ID = "GC_AI_FEATURE_SCHEMA_V1"
GC_AI_LABEL_SCHEMA_ID = "GC_AI_LABEL_SCHEMA_V1"
GC_AI_LABEL_HORIZON_BARS = 12

_UTC = timezone.utc
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_REASON_ORDER = (
    "INVALID_FEATURE_LABEL_EVIDENCE",
    "AMBIGUOUS_OPPOSING_CANDIDATES",
    "MISSING_TOP_LEVEL_CONTEXT",
    "INCOMPLETE_LABEL_HORIZON",
    "FEATURE_LABEL_VALID",
    "NO_ELIGIBLE_CANDIDATES",
)
_DETECTOR_VERSIONS = (
    ("gc_dataset_builder", GC_DATASET_BUILDER_VERSION),
    ("equal_liquidity", EQUAL_LIQUIDITY_DETECTOR_VERSION),
    ("dealing_range", DEALING_RANGE_DETECTOR_VERSION),
    ("liquidity_map", LIQUIDITY_MAP_DETECTOR_VERSION),
    ("fair_value_gap", FAIR_VALUE_GAP_DETECTOR_VERSION),
    ("inducement", INDUCEMENT_DETECTOR_VERSION),
    ("kill_zones", KILL_ZONE_DETECTOR_VERSION),
)


class GCLabelOutcome(str, Enum):
    TARGET_FIRST = "TARGET_FIRST"
    INVALIDATION_FIRST = "INVALIDATION_FIRST"
    TIMEOUT = "TIMEOUT"
    SAME_BAR_AMBIGUOUS = "SAME_BAR_AMBIGUOUS"
    INCOMPLETE = "INCOMPLETE"
    INVALID = "INVALID"


class GCFeatureLabelIdentityKind(str, Enum):
    FEATURE_ROW = "FEATURE_ROW"
    LABEL = "LABEL"
    MANIFEST = "MANIFEST"


@dataclass(frozen=True)
class GCFeatureLabelConfig:
    feature_schema_id: str = GC_AI_FEATURE_SCHEMA_ID
    label_schema_id: str = GC_AI_LABEL_SCHEMA_ID
    horizon_bars: int = GC_AI_LABEL_HORIZON_BARS


@dataclass(frozen=True)
class GCFeatureLabelCandidateEvidence:
    inducement: Inducement
    inducement_snapshot: InducementSnapshot
    active_range: DealingRangeSnapshot
    liquidity_map_snapshot: LiquidityMapSnapshot
    external_target: LiquidityClassification
    internal_pool_classification: LiquidityClassification
    internal_pool: EqualLiquidityPool
    structure_event: DealingRangeStructureEvent
    fair_value_gap: FairValueGap
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...]
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...]
    kill_zone_context: KillZoneContext
    kill_zone_snapshot: KillZoneSnapshot
    confirmation_bar: GCChronologicalBar


@dataclass(frozen=True)
class GCFeatureRow:
    row_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_id: str
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    source_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    detector_versions: tuple[tuple[str, str], ...]
    feature_schema_id: str
    feature_values: tuple[object, ...]


@dataclass(frozen=True)
class GCResearchLabel:
    label_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_id: str
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    label_schema_id: str
    horizon_bars: int
    target_tick: int
    invalidation_tick: int
    outcome: GCLabelOutcome
    first_outcome_index: int | None
    first_outcome_timestamp: datetime | None
    horizon_end_index: int | None
    horizon_end_timestamp: datetime | None


@dataclass(frozen=True)
class GCFeatureLabelManifest:
    manifest_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    timezone_data_version: str
    calendar_version: str
    dataset_id: str
    feature_schema_id: str
    label_schema_id: str
    horizon_bars: int
    feature_row_ids: tuple[str, ...]
    label_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCFeatureLabelResult:
    status: SMCV2PrimitiveStatus
    rows: tuple[GCFeatureRow, ...] = ()
    labels: tuple[GCResearchLabel, ...] = ()
    manifest: GCFeatureLabelManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


def _exact_str(value: object, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise TypeError(f"{name} must be a nonempty str")
    return value.strip()


def _exact_int(value: object, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be int")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} is below its minimum")
    return value


def _exact_date(value: object, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be date")
    return value


def _utc(value: object, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be a timezone-aware datetime")
    return value.astimezone(_UTC)


def _timestamp_text(value: datetime) -> str:
    return _utc(value, "timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")


def _hash_id(value: object, name: str) -> str:
    if type(value) is not str or _HASH_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _tuple(value: object, name: str) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be tuple")
    return value


def _decimal(value: object, name: str) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        raise TypeError(f"{name} must be a finite Decimal")
    return value


def _decimal_text(value: Decimal) -> str:
    if value.is_zero():
        return "0.0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if "." in text else f"{text}.0"


def _normalized_instrument(value: object) -> str:
    return _exact_str(value, "instrument").upper()


def _normalized_timeframe(value: object) -> str:
    return _exact_str(value, "timeframe").upper()


def _canonical(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if type(value) is Decimal:
        return _decimal_text(value)
    if type(value) is datetime:
        return _timestamp_text(value)
    if type(value) is date:
        return value.isoformat()
    if type(value) is tuple:
        return tuple(_canonical(item) for item in value)
    if type(value) is dict:
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) in (str, int) or value is None:
        return value
    raise TypeError("unsupported canonical identity value")


def _sha(payload: object) -> str:
    try:
        data = json.dumps(
            _canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
    except (TypeError, ValueError, ArithmeticError) as exc:
        raise ValueError("invalid identity payload") from exc


def make_gc_feature_label_id(
    *,
    identity_kind: GCFeatureLabelIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    timezone_data_version: str,
    calendar_version: str,
    dataset_id: str,
    candidate_id: str | None = None,
    contract: str | None = None,
    trade_date: date | None = None,
    source_ids: tuple[str, ...] = (),
    lineage_ids: tuple[str, ...] = (),
    detector_versions: tuple[tuple[str, str], ...] = (),
    feature_schema_id: str | None = None,
    label_schema_id: str | None = None,
    horizon_bars: int | None = None,
    feature_values: tuple[object, ...] = (),
    target_tick: int | None = None,
    invalidation_tick: int | None = None,
    outcome: GCLabelOutcome | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    first_outcome_index: int | None = None,
    first_outcome_timestamp: datetime | None = None,
    horizon_end_index: int | None = None,
    horizon_end_timestamp: datetime | None = None,
    feature_row_ids: tuple[str, ...] = (),
    label_ids: tuple[str, ...] = (),
) -> str:
    if type(identity_kind) is not GCFeatureLabelIdentityKind:
        raise TypeError("identity_kind must be GCFeatureLabelIdentityKind")
    common = {
        "version": GC_FEATURE_LABEL_VERSION,
        "kind": identity_kind.value,
        "instrument": _normalized_instrument(instrument),
        "timeframe": _normalized_timeframe(timeframe),
        "tick_size": _decimal_text(_decimal(tick_size, "tick_size")),
        "timezone_data_version": _exact_str(timezone_data_version, "timezone_data_version").upper(),
        "calendar_version": _exact_str(calendar_version, "calendar_version"),
        "dataset_id": _hash_id(dataset_id, "dataset_id"),
    }
    if identity_kind is GCFeatureLabelIdentityKind.FEATURE_ROW:
        if any(value is not None for value in (label_schema_id, horizon_bars, target_tick, invalidation_tick, outcome, first_outcome_index, first_outcome_timestamp, horizon_end_index, horizon_end_timestamp)) or feature_row_ids or label_ids:
            raise ValueError("forbidden FEATURE_ROW field")
        ids = _tuple(source_ids, "source_ids")
        lineages = _tuple(lineage_ids, "lineage_ids")
        versions = _tuple(detector_versions, "detector_versions")
        features = _tuple(feature_values, "feature_values")
        if not ids or not lineages or not versions or len(features) != 17:
            raise ValueError("incomplete FEATURE_ROW history")
        for item in (*ids, *lineages):
            _hash_id(item, "identity history")
        for item in versions:
            if type(item) is not tuple or len(item) != 2:
                raise TypeError("detector version entry must be a pair")
            _exact_str(item[0], "detector name")
            _exact_str(item[1], "detector version")
        payload = common | {
            "candidate_id": _hash_id(candidate_id, "candidate_id"),
            "contract": _exact_str(contract, "contract"),
            "trade_date": _exact_date(trade_date, "trade_date"),
            "source_ids": ids,
            "lineage_ids": lineages,
            "detector_versions": versions,
            "feature_schema_id": _exact_str(feature_schema_id, "feature_schema_id"),
            "feature_values": features,
            "effective_index": _exact_int(effective_index, "effective_index", minimum=0),
            "effective_timestamp": _utc(effective_timestamp, "effective_timestamp"),
        }
    elif identity_kind is GCFeatureLabelIdentityKind.LABEL:
        if source_ids or lineage_ids or detector_versions or feature_schema_id is not None or feature_values or feature_row_ids or label_ids:
            raise ValueError("forbidden LABEL field")
        if type(outcome) is not GCLabelOutcome:
            raise TypeError("outcome must be GCLabelOutcome")
        complete_first = outcome in (
            GCLabelOutcome.TARGET_FIRST,
            GCLabelOutcome.INVALIDATION_FIRST,
            GCLabelOutcome.SAME_BAR_AMBIGUOUS,
        )
        if (first_outcome_index is None) != (first_outcome_timestamp is None):
            raise ValueError("first outcome moment must be paired")
        if complete_first != (first_outcome_index is not None):
            raise ValueError("first outcome moment contradicts outcome")
        if (horizon_end_index is None) != (horizon_end_timestamp is None):
            raise ValueError("horizon end moment must be paired")
        if outcome not in (GCLabelOutcome.INCOMPLETE, GCLabelOutcome.INVALID) and horizon_end_index is None:
            raise ValueError("complete label requires horizon end")
        if outcome is GCLabelOutcome.INVALID and horizon_end_index is not None:
            raise ValueError("invalid label forbids horizon end")
        payload = common | {
            "candidate_id": _hash_id(candidate_id, "candidate_id"),
            "contract": _exact_str(contract, "contract"),
            "trade_date": _exact_date(trade_date, "trade_date"),
            "label_schema_id": _exact_str(label_schema_id, "label_schema_id"),
            "horizon_bars": _exact_int(horizon_bars, "horizon_bars", minimum=1),
            "target_tick": _exact_int(target_tick, "target_tick"),
            "invalidation_tick": _exact_int(invalidation_tick, "invalidation_tick"),
            "outcome": outcome,
            "effective_index": _exact_int(effective_index, "effective_index", minimum=0),
            "effective_timestamp": _utc(effective_timestamp, "effective_timestamp"),
            "first_outcome_index": None if first_outcome_index is None else _exact_int(first_outcome_index, "first_outcome_index", minimum=0),
            "first_outcome_timestamp": None if first_outcome_timestamp is None else _utc(first_outcome_timestamp, "first_outcome_timestamp"),
            "horizon_end_index": None if horizon_end_index is None else _exact_int(horizon_end_index, "horizon_end_index", minimum=0),
            "horizon_end_timestamp": None if horizon_end_timestamp is None else _utc(horizon_end_timestamp, "horizon_end_timestamp"),
        }
    else:
        forbidden = (candidate_id, contract, trade_date, target_tick, invalidation_tick, outcome, effective_index, effective_timestamp, first_outcome_index, first_outcome_timestamp, horizon_end_index, horizon_end_timestamp)
        if any(item is not None for item in forbidden) or source_ids or lineage_ids or detector_versions or feature_values:
            raise ValueError("forbidden MANIFEST field")
        row_ids = _tuple(feature_row_ids, "feature_row_ids")
        labels = _tuple(label_ids, "label_ids")
        if not row_ids or len(row_ids) != len(labels) or len(set(row_ids)) != len(row_ids) or len(set(labels)) != len(labels):
            raise ValueError("manifest histories must be nonempty, unique, and paired")
        for item in (*row_ids, *labels):
            _hash_id(item, "manifest history")
        payload = common | {
            "feature_schema_id": _exact_str(feature_schema_id, "feature_schema_id"),
            "label_schema_id": _exact_str(label_schema_id, "label_schema_id"),
            "horizon_bars": _exact_int(horizon_bars, "horizon_bars", minimum=1),
            "feature_row_ids": row_ids,
            "label_ids": labels,
        }
    return _sha(payload)


def _hash_payload(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _bar_digest(bars: tuple[GCChronologicalBar, ...]) -> str:
    return _hash_payload(tuple({
        "index": bar.index,
        "timestamp": _timestamp_text(bar.timestamp),
        "open_tick": bar.open_tick,
        "high_tick": bar.high_tick,
        "low_tick": bar.low_tick,
        "close_tick": bar.close_tick,
        "volume": bar.volume,
        "is_closed": bar.is_closed,
    } for bar in bars))


def _calendar_digest(entries: tuple[KillZoneCalendarEntry, ...]) -> str:
    return _hash_payload(tuple({
        "calendar_version": item.calendar_version,
        "trade_date": item.trade_date.isoformat(),
        "session_status": item.session_status.value,
        "opening": _timestamp_text(item.session_open_timestamp) if item.session_open_timestamp is not None else None,
        "closing": _timestamp_text(item.session_close_timestamp) if item.session_close_timestamp is not None else None,
    } for item in entries))


def _validate_bar(
    bar: object,
    *,
    require_closed: bool = True,
) -> GCChronologicalBar:
    if type(bar) is not GCChronologicalBar:
        raise TypeError("bar must be GCChronologicalBar")
    _exact_int(bar.index, "bar.index", minimum=0)
    _utc(bar.timestamp, "bar.timestamp")
    for name in ("open_tick", "high_tick", "low_tick", "close_tick"):
        _exact_int(getattr(bar, name), f"bar.{name}")
    _exact_int(bar.volume, "bar.volume", minimum=0)
    if type(bar.is_closed) is not bool or (require_closed and not bar.is_closed):
        raise ValueError("bar must be fully closed")
    if bar.low_tick > min(bar.open_tick, bar.close_tick) or bar.high_tick < max(bar.open_tick, bar.close_tick) or bar.low_tick > bar.high_tick:
        raise ValueError("invalid OHLC geometry")
    return bar


def _runtime_tzdata() -> str:
    try:
        ZoneInfo("America/New_York")
        return importlib.metadata.version("tzdata").strip().upper()
    except (ZoneInfoNotFoundError, importlib.metadata.PackageNotFoundError) as exc:
        raise ValueError("runtime timezone evidence unavailable") from exc


def _validate_dataset_config(value: object) -> GCDatasetBuildConfig:
    if type(value) is not GCDatasetBuildConfig:
        raise TypeError("dataset_config must be exact GCDatasetBuildConfig")
    if _normalized_instrument(value.instrument) != "GC" or _normalized_timeframe(value.timeframe) != "5M":
        raise ValueError("dataset instrument/timeframe mismatch")
    if value.source_timezone != "Asia/Tokyo" or value.exchange_timezone != "America/New_York":
        raise ValueError("dataset timezone mismatch")
    if _exact_str(value.timezone_data_version, "timezone_data_version").upper() != _runtime_tzdata():
        raise ValueError("runtime timezone-data mismatch")
    if _decimal(value.tick_size, "tick_size") != Decimal("0.1"):
        raise ValueError("tick size mismatch")
    _exact_str(value.initial_contract, "initial_contract")
    _exact_date(value.initial_trade_date, "initial_trade_date")
    _exact_int(value.roll_confirmation_sessions, "roll_confirmation_sessions", minimum=1)
    if _exact_date(value.oos_start_trade_date, "oos_start_trade_date") > _exact_date(value.oos_end_trade_date, "oos_end_trade_date"):
        raise ValueError("OOS bounds are reversed")
    return value


def _validate_calendar(entries: object, version: str) -> tuple[KillZoneCalendarEntry, ...]:
    values = _tuple(entries, "calendar_entries")
    previous: date | None = None
    ny = ZoneInfo("America/New_York")
    output: list[KillZoneCalendarEntry] = []
    for entry in values:
        if type(entry) is not KillZoneCalendarEntry:
            raise TypeError("calendar entry must be exact KillZoneCalendarEntry")
        if entry.calendar_version != version or type(entry.session_status) is not KillZoneSessionStatus:
            raise ValueError("calendar version/status mismatch")
        trade_date = _exact_date(entry.trade_date, "calendar.trade_date")
        if previous is not None and trade_date <= previous:
            raise ValueError("calendar order is not strictly increasing")
        previous = trade_date
        if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
            if entry.session_open_timestamp is not None or entry.session_close_timestamp is not None:
                raise ValueError("closed session must not have bounds")
        else:
            opening = _utc(entry.session_open_timestamp, "session_open_timestamp")
            closing = _utc(entry.session_close_timestamp, "session_close_timestamp")
            expected_open = datetime.combine(trade_date - timedelta(days=1), time(18), tzinfo=ny).astimezone(_UTC)
            latest_close = datetime.combine(trade_date, time(17), tzinfo=ny).astimezone(_UTC)
            if opening != expected_open or not opening < closing <= latest_close:
                raise ValueError("calendar session geometry mismatch")
        output.append(entry)
    return tuple(output)


def _validate_dataset(
    config: GCDatasetBuildConfig,
    value: object,
    calendars: tuple[KillZoneCalendarEntry, ...] | None,
) -> tuple[GCDatasetBuildResult, GCDatasetManifest]:
    if type(value) is not GCDatasetBuildResult or value.status is not GCDatasetBuildStatus.VALID:
        raise TypeError("dataset must be exact VALID GCDatasetBuildResult")
    if type(value.manifest) is not GCDatasetManifest or value.dataset_id is None:
        raise ValueError("dataset manifest is required")
    manifest = value.manifest
    dataset_id = _hash_id(value.dataset_id, "dataset_id")
    if manifest.dataset_id != dataset_id or manifest.version != GC_DATASET_BUILDER_VERSION:
        raise ValueError("dataset manifest identity mismatch")
    if manifest.timezone_data_version.upper() != config.timezone_data_version.upper():
        raise ValueError("dataset timezone-data mismatch")
    if calendars is not None and (
        not calendars
        or any(
            item.calendar_version != manifest.calendar_version
            for item in calendars
        )
    ):
        raise ValueError("dataset calendar mismatch")
    segments = _tuple(value.segments, "dataset.segments")
    if not segments or type(manifest.segment_ids) is not tuple or tuple(item.segment_id for item in segments) != manifest.segment_ids:
        raise ValueError("dataset segment history mismatch")
    if _exact_int(manifest.oos_bar_count, "manifest.oos_bar_count", minimum=0) != 0:
        raise ValueError("OOS holdout evidence remains sealed")
    total_bars = total_volume = dev = oos = 0
    for segment in segments:
        if type(segment) is not GCCanonicalContractSegment or type(segment.partition) is not GCSegmentPartition:
            raise TypeError("segment must be canonical")
        if segment.partition is GCSegmentPartition.OOS_HOLDOUT:
            raise ValueError("OOS holdout evidence remains sealed")
        _hash_id(segment.segment_id, "segment_id")
        _exact_str(segment.contract, "segment.contract")
        first = _exact_date(segment.first_trade_date, "segment.first_trade_date")
        last = _exact_date(segment.last_trade_date, "segment.last_trade_date")
        if first > last or type(segment.source_ids) is not tuple or not segment.source_ids:
            raise ValueError("segment provenance mismatch")
        for item in segment.source_ids:
            if _hash_id(item, "segment source") not in manifest.source_ids:
                raise ValueError("segment source is not manifest-bound")
        _exact_int(segment.preceding_missing_bar_count, "preceding_missing_bar_count", minimum=0)
        bars = _tuple(segment.bars, "segment.bars")
        if not bars:
            raise ValueError("empty canonical segment")
        previous: GCChronologicalBar | None = None
        for raw_bar in bars:
            bar = _validate_bar(raw_bar, require_closed=False)
            if previous is not None and (
                bar.index < previous.index
                or _utc(bar.timestamp, "bar.timestamp")
                < _utc(previous.timestamp, "bar.timestamp")
            ):
                raise ValueError("segment bars are causally out of order")
            previous = bar
            total_bars += 1
            total_volume += bar.volume
        expected_segment_id = make_gc_dataset_id(
            identity_kind="SEGMENT", config=config, contract=segment.contract,
            partition=segment.partition, first_trade_date=segment.first_trade_date,
            last_trade_date=segment.last_trade_date, source_ids=segment.source_ids,
            bar_digest=_bar_digest(bars), preceding_missing_bar_count=segment.preceding_missing_bar_count,
        )
        if expected_segment_id != segment.segment_id:
            raise ValueError("segment identity mismatch")
        if segment.partition is GCSegmentPartition.DEVELOPMENT:
            dev += len(bars)
        else:
            oos += len(bars)
    for item in (*manifest.source_ids, *manifest.coverage_ids, manifest.coverage_digest):
        _hash_id(item, "manifest provenance")
    counts = (manifest.parsed_row_count, manifest.eligible_row_count, manifest.development_bar_count, manifest.oos_bar_count, manifest.excluded_row_count, manifest.missing_bar_count, manifest.attested_no_trade_interval_count)
    for item in counts:
        _exact_int(item, "manifest count", minimum=0)
    volumes = (manifest.raw_volume, manifest.eligible_volume, manifest.excluded_volume)
    for item in volumes:
        _exact_int(item, "manifest volume", minimum=0)
    if manifest.parsed_row_count != manifest.eligible_row_count + manifest.excluded_row_count or manifest.raw_volume != manifest.eligible_volume + manifest.excluded_volume or manifest.eligible_row_count != total_bars or manifest.eligible_volume != total_volume or manifest.development_bar_count != dev or manifest.oos_bar_count != oos or manifest.missing_bar_count != manifest.attested_no_trade_interval_count:
        raise ValueError("manifest conservation mismatch")
    if type(manifest.completed_session_volumes) is not tuple or sum(item[2] for item in manifest.completed_session_volumes) > manifest.eligible_volume:
        raise ValueError("completed-session conservation mismatch")
    for contract, trade_date, volume in manifest.completed_session_volumes:
        _exact_str(contract, "completed contract"); _exact_date(trade_date, "completed trade_date"); _exact_int(volume, "completed volume", minimum=0)
    if type(manifest.exclusion_counts) is not tuple or sum(item[1] for item in manifest.exclusion_counts) != manifest.excluded_row_count:
        raise ValueError("exclusion count mismatch")
    evidence = {
        "version": manifest.version, "source_ids": manifest.source_ids,
        "coverage_ids": manifest.coverage_ids, "coverage_digest": manifest.coverage_digest,
        "segment_ids": manifest.segment_ids, "calendar_version": manifest.calendar_version,
        "timezone_data_version": manifest.timezone_data_version,
        "raw_start_timestamp": _timestamp_text(manifest.raw_start_timestamp),
        "raw_end_timestamp": _timestamp_text(manifest.raw_end_timestamp),
        "usable_start_timestamp": _timestamp_text(manifest.usable_start_timestamp) if manifest.usable_start_timestamp is not None else None,
        "usable_end_timestamp": _timestamp_text(manifest.usable_end_timestamp) if manifest.usable_end_timestamp is not None else None,
        "parsed_row_count": manifest.parsed_row_count, "eligible_row_count": manifest.eligible_row_count,
        "development_bar_count": manifest.development_bar_count, "oos_bar_count": manifest.oos_bar_count,
        "excluded_row_count": manifest.excluded_row_count, "missing_bar_count": manifest.missing_bar_count,
        "attested_no_trade_interval_count": manifest.attested_no_trade_interval_count,
        "raw_volume": manifest.raw_volume, "eligible_volume": manifest.eligible_volume,
        "excluded_volume": manifest.excluded_volume,
        "completed_session_volumes": tuple((a, b.isoformat(), c) for a, b, c in manifest.completed_session_volumes),
        "exclusion_counts": manifest.exclusion_counts,
        "roll_trade_dates": tuple(item.isoformat() for item in manifest.roll_trade_dates),
    }
    if calendars is not None:
        expected_dataset_id = make_gc_dataset_id(
            identity_kind="DATASET",
            config=config,
            source_ids=manifest.source_ids,
            coverage_ids=manifest.coverage_ids,
            segment_ids=manifest.segment_ids,
            calendar_digest=_calendar_digest(calendars),
            coverage_digest=manifest.coverage_digest,
            evidence_digest=_hash_payload(evidence),
            roll_trade_dates=manifest.roll_trade_dates,
        )
        if expected_dataset_id != dataset_id:
            raise ValueError("dataset identity mismatch")
    return value, manifest


def _validate_provenance(value: object) -> SMCV2EventProvenance:
    if type(value) is not SMCV2EventProvenance or type(value.source_indices) is not tuple or type(value.source_timestamps) is not tuple or not value.source_indices or len(value.source_indices) != len(value.source_timestamps):
        raise TypeError("invalid provenance")
    previous: tuple[int, datetime] | None = None
    for index, timestamp in zip(value.source_indices, value.source_timestamps):
        moment = (_exact_int(index, "source_index", minimum=0), _utc(timestamp, "source_timestamp"))
        if previous is not None and (moment[0] <= previous[0] or moment[1] <= previous[1]):
            raise ValueError("provenance is out of order")
        previous = moment
    confirmation = (_exact_int(value.confirmation_index, "confirmation_index", minimum=0), _utc(value.confirmation_timestamp, "confirmation_timestamp"))
    if previous is None or confirmation < previous:
        raise ValueError("confirmation predates source")
    return value


def _validate_candidate_static(candidate: object, instrument: str, timeframe: str) -> GCFeatureLabelCandidateEvidence:
    if type(candidate) is not GCFeatureLabelCandidateEvidence:
        raise TypeError("candidate must be exact GCFeatureLabelCandidateEvidence")
    i = candidate.inducement
    if type(i) is not Inducement or type(i.direction) is not SMCV2Direction or type(i.structure_event_type) is not DealingRangeEventType:
        raise TypeError("invalid inducement")
    expected_i = make_inducement_id(
        identity_kind="INDUCEMENT", instrument=instrument, timeframe=timeframe,
        direction=i.direction, active_range_lineage_id=i.active_range_lineage_id,
        active_range_snapshot_id=i.active_range_snapshot_id, liquidity_map_snapshot_id=i.liquidity_map_snapshot_id,
        external_target_classification_id=i.external_target_classification_id,
        internal_pool_classification_id=i.internal_pool_classification_id, internal_pool_id=i.internal_pool_id,
        sweep_index=i.sweep_index, sweep_timestamp=i.sweep_timestamp, sweep_extreme_tick=i.sweep_extreme_tick,
        reclaim_close_tick=i.reclaim_close_tick, structure_event_id=i.structure_event_id,
        structure_event_type=i.structure_event_type, confirmation_index=i.confirmation_index,
        confirmation_timestamp=i.confirmation_timestamp, confirmation_offset_bars=i.confirmation_offset_bars,
        fair_value_gap_id=i.fair_value_gap_id, displacement_id=i.displacement_id,
    )
    if expected_i != _hash_id(i.inducement_id, "inducement_id"):
        raise ValueError("inducement identity mismatch")
    snapshot = candidate.inducement_snapshot
    if type(snapshot) is not InducementSnapshot or i.inducement_id not in snapshot.inducement_ids:
        raise ValueError("inducement snapshot mismatch")
    expected_snapshot = make_inducement_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, effective_index=snapshot.index, effective_timestamp=snapshot.timestamp, inducement_ids=snapshot.inducement_ids)
    if expected_snapshot != snapshot.snapshot_id:
        raise ValueError("inducement snapshot identity mismatch")
    active_range = candidate.active_range
    if type(active_range) is not DealingRangeSnapshot or active_range.kind is not DealingRangeKind.EXTERNAL or active_range.state is not DealingRangeState.ACTIVE or active_range.direction is not i.direction:
        raise ValueError("active range mismatch")
    expected_range = make_dealing_range_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, direction=active_range.direction, source_indices=active_range.source_indices, swing_ids=active_range.source_swing_ids, boundaries=SMCV2TickRange(active_range.low_tick, active_range.high_tick), lineage_id=active_range.lineage_id, construction_event_id=active_range.construction_event_id, range_kind=active_range.kind, state=active_range.state, transition_ids=active_range.transition_ids, replacement_lineage_id=active_range.replacement_lineage_id)
    if expected_range != active_range.snapshot_id or i.active_range_snapshot_id != active_range.snapshot_id or i.active_range_lineage_id != active_range.lineage_id:
        raise ValueError("range identity/reference mismatch")
    if (
        type(active_range.transitions) is not tuple
        or type(active_range.transition_ids) is not tuple
        or not active_range.transitions
        or tuple(item.transition_id for item in active_range.transitions)
        != active_range.transition_ids
    ):
        raise ValueError("range transition membership mismatch")
    previous_range_state: DealingRangeState | None = None
    previous_range_moment: tuple[int, datetime] | None = None
    for transition in active_range.transitions:
        if type(transition) is not DealingRangeTransition:
            raise TypeError("range transition must be canonical")
        transition_moment = (
            _exact_int(transition.index, "range transition index", minimum=0),
            _utc(transition.timestamp, "range transition timestamp"),
        )
        if (
            transition.lineage_id != active_range.lineage_id
            or transition.from_state is not previous_range_state
            or (
                previous_range_moment is not None
                and (
                    transition_moment[0] <= previous_range_moment[0]
                    or transition_moment[1] < previous_range_moment[1]
                )
            )
        ):
            raise ValueError("range transition chain mismatch")
        expected_transition = make_dealing_range_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=active_range.direction,
            source_indices=(transition.index,),
            lineage_id=transition.lineage_id,
            transition_from_state=transition.from_state,
            transition_to_state=transition.to_state,
            transition_index=transition.index,
            transition_timestamp=transition.timestamp,
            transition_reason=transition.reason,
            related_event_id=transition.related_event_id,
            replacement_lineage_id=transition.replacement_lineage_id,
        )
        if expected_transition != transition.transition_id:
            raise ValueError("range transition identity mismatch")
        previous_range_state = transition.to_state
        previous_range_moment = transition_moment
    if previous_range_state is not active_range.state:
        raise ValueError("range snapshot state does not match transition history")
    range_provenance = _validate_provenance(active_range.first_known_provenance)
    sweep_moment = (
        _exact_int(i.sweep_index, "sweep_index", minimum=0),
        _utc(i.sweep_timestamp, "sweep_timestamp"),
    )
    range_effective_moment = (
        range_provenance.confirmation_index,
        _utc(range_provenance.confirmation_timestamp, "range effective timestamp"),
    )
    if previous_range_moment != range_effective_moment:
        raise ValueError("ACTIVE range creation moment does not match transition history")
    if range_effective_moment > sweep_moment:
        raise ValueError("active range was not effective by the sweep")
    map_snapshot = candidate.liquidity_map_snapshot
    if type(map_snapshot) is not LiquidityMapSnapshot or map_snapshot.snapshot_id != i.liquidity_map_snapshot_id or map_snapshot.active_range_snapshot_id != active_range.snapshot_id or map_snapshot.active_range_lineage_id != active_range.lineage_id:
        raise ValueError("liquidity-map reference mismatch")
    if type(map_snapshot.classifications) is not tuple or tuple(item.classification_id for item in map_snapshot.classifications) != map_snapshot.classification_ids:
        raise ValueError("liquidity-map classification history mismatch")
    expected_map_id = make_liquidity_map_id(
        identity_kind="MAP",
        instrument=instrument,
        timeframe=timeframe,
        active_range_lineage_id=map_snapshot.active_range_lineage_id,
    )
    if expected_map_id != map_snapshot.map_id:
        raise ValueError("liquidity-map identity mismatch")
    if (
        type(map_snapshot.reclassifications) is not tuple
        or type(map_snapshot.reclassification_ids) is not tuple
        or tuple(item.reclassification_id for item in map_snapshot.reclassifications)
        != map_snapshot.reclassification_ids
    ):
        raise ValueError("liquidity-map reclassification history mismatch")
    for reclassification in map_snapshot.reclassifications:
        if type(reclassification) is not LiquidityReclassification:
            raise TypeError("reclassification must be canonical")
        expected_reclassification = make_liquidity_map_id(
            identity_kind="RECLASSIFICATION",
            instrument=instrument,
            timeframe=timeframe,
            active_range_lineage_id=map_snapshot.active_range_lineage_id,
            source_kind=reclassification.source_kind,
            source_id=reclassification.source_id,
            side=reclassification.side,
            prior_classification_id=reclassification.prior_classification_id,
            new_classification_id=reclassification.new_classification_id,
            event_index=reclassification.index,
            event_timestamp=reclassification.timestamp,
            from_scope=reclassification.from_scope,
            to_scope=reclassification.to_scope,
            reason=reclassification.reason,
        )
        if (
            expected_reclassification != reclassification.reclassification_id
            or reclassification.new_classification_id
            not in map_snapshot.classification_ids
        ):
            raise ValueError("reclassification identity/reference mismatch")
    expected_map_snapshot = make_liquidity_map_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, active_range_lineage_id=map_snapshot.active_range_lineage_id, active_range_snapshot_id=map_snapshot.active_range_snapshot_id, classification_ids=map_snapshot.classification_ids, reclassification_ids=map_snapshot.reclassification_ids, event_index=map_snapshot.index, event_timestamp=map_snapshot.timestamp)
    if expected_map_snapshot != map_snapshot.snapshot_id:
        raise ValueError("liquidity-map snapshot identity mismatch")
    map_effective_moment = (
        _exact_int(map_snapshot.index, "liquidity-map index", minimum=0),
        _utc(map_snapshot.timestamp, "liquidity-map timestamp"),
    )
    if map_effective_moment >= sweep_moment:
        raise ValueError("liquidity map must be effective strictly before the sweep")
    if len(set(map_snapshot.classification_ids)) != len(map_snapshot.classification_ids):
        raise ValueError("liquidity-map classification identities are not unique")
    classifications_by_id: dict[str, LiquidityClassification] = {}
    for classification in map_snapshot.classifications:
        if type(classification) is not LiquidityClassification:
            raise TypeError("classification must be canonical")
        expected_classification = make_liquidity_map_id(identity_kind="CLASSIFICATION", instrument=instrument, timeframe=timeframe, active_range_lineage_id=classification.active_range_lineage_id, source_indices=classification.source_indices, source_kind=classification.source_kind, source_id=classification.source_id, side=classification.side, scope=classification.scope, boundaries=classification.boundaries, active_range_snapshot_id=classification.active_range_snapshot_id, version=classification.version, prior_classification_id=classification.prior_classification_id, event_index=classification.classification_index, event_timestamp=classification.classification_timestamp)
        if expected_classification != classification.classification_id:
            raise ValueError("classification identity mismatch")
        classifications_by_id[classification.classification_id] = classification
    external = candidate.external_target; internal = candidate.internal_pool_classification
    if type(external) is not LiquidityClassification or type(internal) is not LiquidityClassification:
        raise TypeError("classification references must be canonical")
    if (
        classifications_by_id.get(external.classification_id) != external
        or classifications_by_id.get(internal.classification_id) != internal
        or external.classification_id != i.external_target_classification_id
        or internal.classification_id != i.internal_pool_classification_id
    ):
        raise ValueError("classification reference mismatch")
    if external.scope is not LiquidityScope.EXTERNAL or internal.scope is not LiquidityScope.INTERNAL or internal.source_kind is not LiquiditySourceKind.EQUAL_LIQUIDITY_POOL:
        raise ValueError("classification role mismatch")
    pool = candidate.internal_pool
    if type(pool) is not EqualLiquidityPool or pool.lifecycle_state is not SMCV2LifecycleState.SWEPT or pool.lineage_id != i.internal_pool_id or internal.source_id != pool.lineage_id:
        raise ValueError("internal pool mismatch")
    expected_pool = make_equal_liquidity_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, side=pool.side, source_indices=pool.source_indices, swing_ids=pool.member_swing_ids, reference_tick=pool.reference_tick, lower_tick=pool.lower_tick, upper_tick=pool.upper_tick, lineage_id=pool.lineage_id, lifecycle_state=pool.lifecycle_state)
    if expected_pool != pool.snapshot_id:
        raise ValueError("pool identity mismatch")
    pool_provenance = _validate_provenance(pool.first_known_provenance)
    if pool_provenance.source_indices != pool.source_indices:
        raise ValueError("pool first-known source provenance mismatch")
    if type(pool.lifecycle_events) is not tuple or not pool.lifecycle_events:
        raise ValueError("pool lifecycle missing")
    for event in pool.lifecycle_events:
        if type(event) is not SMCV2LifecycleEvent:
            raise TypeError("pool lifecycle event invalid")
        _exact_int(event.index, "lifecycle index", minimum=0); _utc(event.timestamp, "lifecycle timestamp"); _exact_str(event.reason, "lifecycle reason")
    validate_lifecycle_history(
        pool.lifecycle_events,
        allowed_transitions={
            None: frozenset({SMCV2LifecycleState.ACTIVE}),
            SMCV2LifecycleState.ACTIVE: frozenset(
                {SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN}
            ),
            SMCV2LifecycleState.SWEPT: frozenset(),
            SMCV2LifecycleState.BROKEN: frozenset(),
        },
        terminal_states=frozenset(
            {SMCV2LifecycleState.SWEPT, SMCV2LifecycleState.BROKEN}
        ),
    )
    first_pool_event = pool.lifecycle_events[0]
    final_pool_event = pool.lifecycle_events[-1]
    if (
        (
            first_pool_event.index,
            _utc(first_pool_event.timestamp, "pool creation timestamp"),
        )
        != (
            pool_provenance.confirmation_index,
            _utc(
                pool_provenance.confirmation_timestamp,
                "pool first-known timestamp",
            ),
        )
        or final_pool_event.to_state is not pool.lifecycle_state
        or (
            final_pool_event.index,
            _utc(final_pool_event.timestamp, "pool terminal timestamp"),
        )
        != sweep_moment
        or internal.source_indices != pool.source_indices
        or internal.boundaries != SMCV2TickRange(pool.lower_tick, pool.upper_tick)
        or (
            pool.side is EqualLiquiditySide.LOW
            and internal.side is not LiquiditySide.SELL_SIDE
        )
        or (
            pool.side is EqualLiquiditySide.HIGH
            and internal.side is not LiquiditySide.BUY_SIDE
        )
    ):
        raise ValueError("pool lifecycle/classification reconciliation mismatch")
    event = candidate.structure_event
    if type(event) is not DealingRangeStructureEvent:
        raise TypeError("structure event invalid")
    provenance = _validate_provenance(event.provenance)
    broken_tick = active_range.high_tick if event.direction is SMCV2Direction.BULLISH else active_range.low_tick
    expected_event = make_dealing_range_id(identity_kind="EVENT", instrument=instrument, timeframe=timeframe, direction=event.direction, source_indices=provenance.source_indices, event_type=event.event_type, broken_swing_id=event.broken_swing_id, confirmation_index=provenance.confirmation_index, boundaries=SMCV2TickRange(broken_tick, broken_tick))
    if expected_event != event.event_id or event.event_id != i.structure_event_id or event.direction is not i.direction or event.event_type is not i.structure_event_type:
        raise ValueError("structure event mismatch")
    gap = candidate.fair_value_gap
    if type(gap) is not FairValueGap or gap.direction is not i.direction or gap.gap_id != i.fair_value_gap_id or gap.structure_event_id != event.event_id or gap.displacement_id != i.displacement_id:
        raise ValueError("FVG reference mismatch")
    expected_gap = make_fair_value_gap_id(identity_kind="GAP", instrument=instrument, timeframe=timeframe, direction=gap.direction, source_indices=gap.source_indices, source_timestamps=gap.source_timestamps, boundaries=SMCV2TickRange(gap.lower_tick, gap.upper_tick), midpoint_tick=gap.midpoint_tick, formation_end_index=gap.formation_end_index, formation_end_timestamp=gap.formation_end_timestamp, displacement_id=gap.displacement_id, structure_event_id=gap.structure_event_id, structure_event_type=gap.structure_event_type)
    if expected_gap != gap.gap_id:
        raise ValueError("FVG identity mismatch")
    if type(candidate.fair_value_gap_transitions) is not tuple or type(candidate.fair_value_gap_snapshots) is not tuple or len(candidate.fair_value_gap_transitions) != len(candidate.fair_value_gap_snapshots) or not candidate.fair_value_gap_transitions:
        raise ValueError("FVG history mismatch")
    transition_ids: list[str] = []
    previous_fvg_state: FairValueGapState | None = None
    previous_fvg_moment: tuple[int, datetime] | None = None
    confirmation_moment = (
        _exact_int(i.confirmation_index, "confirmation_index", minimum=0),
        _utc(i.confirmation_timestamp, "confirmation_timestamp"),
    )
    for transition, fvg_snapshot in zip(candidate.fair_value_gap_transitions, candidate.fair_value_gap_snapshots):
        if type(transition) is not FairValueGapTransition or type(fvg_snapshot) is not FairValueGapSnapshot or transition.gap_id != gap.gap_id or fvg_snapshot.gap_id != gap.gap_id:
            raise TypeError("FVG history type/reference mismatch")
        expected_transition = make_fair_value_gap_id(identity_kind="TRANSITION", instrument=instrument, timeframe=timeframe, direction=gap.direction, gap_id=gap.gap_id, from_state=transition.from_state, to_state=transition.to_state, effective_index=transition.index, effective_timestamp=transition.timestamp, reason=transition.reason)
        if expected_transition != transition.transition_id:
            raise ValueError("FVG transition identity mismatch")
        transition_moment = (
            _exact_int(transition.index, "FVG transition index", minimum=0),
            _utc(transition.timestamp, "FVG transition timestamp"),
        )
        snapshot_moment = (
            _exact_int(fvg_snapshot.index, "FVG snapshot index", minimum=0),
            _utc(fvg_snapshot.timestamp, "FVG snapshot timestamp"),
        )
        if (
            transition.from_state is not previous_fvg_state
            or fvg_snapshot.direction is not gap.direction
            or fvg_snapshot.state is not transition.to_state
            or snapshot_moment != transition_moment
            or transition_moment > confirmation_moment
            or (
                previous_fvg_moment is not None
                and transition_moment <= previous_fvg_moment
            )
        ):
            raise ValueError("FVG transition/snapshot causal history mismatch")
        transition_ids.append(transition.transition_id)
        expected_fvg_snapshot = make_fair_value_gap_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, direction=fvg_snapshot.direction, gap_id=gap.gap_id, state=fvg_snapshot.state, effective_index=fvg_snapshot.index, effective_timestamp=fvg_snapshot.timestamp, transition_ids=fvg_snapshot.transition_ids)
        if expected_fvg_snapshot != fvg_snapshot.snapshot_id or fvg_snapshot.transition_ids != tuple(transition_ids):
            raise ValueError("FVG snapshot identity/history mismatch")
        previous_fvg_state = transition.to_state
        previous_fvg_moment = transition_moment
    if previous_fvg_moment != confirmation_moment:
        raise ValueError("FVG history is incomplete through confirmation")
    context = candidate.kill_zone_context; kill_snapshot = candidate.kill_zone_snapshot
    if type(context) is not KillZoneContext or type(kill_snapshot) is not KillZoneSnapshot or context.context_id not in kill_snapshot.context_ids:
        raise TypeError("Kill Zone evidence mismatch")
    expected_context = make_kill_zone_id(identity_kind="CONTEXT", instrument=instrument, timeframe=timeframe, calendar_version=context.calendar_version, timezone_name=context.timezone_name, timezone_data_version=context.timezone_data_version, observation_index=context.observation_index, observation_timestamp=context.observation_timestamp, trade_date=context.trade_date, zone=context.zone, session_status=context.session_status, quality=context.quality)
    expected_kill_snapshot = make_kill_zone_id(identity_kind="SNAPSHOT", instrument=instrument, timeframe=timeframe, calendar_version=context.calendar_version, timezone_name=context.timezone_name, timezone_data_version=context.timezone_data_version, effective_index=kill_snapshot.index, effective_timestamp=kill_snapshot.timestamp, context_ids=kill_snapshot.context_ids)
    if expected_context != context.context_id or expected_kill_snapshot != kill_snapshot.snapshot_id:
        raise ValueError("Kill Zone identity mismatch")
    _validate_bar(candidate.confirmation_bar)
    return candidate


def _match_segment(dataset: GCDatasetBuildResult, bar: GCChronologicalBar) -> GCCanonicalContractSegment:
    matches = [segment for segment in dataset.segments if any(item == bar for item in segment.bars)]
    if len(matches) != 1 or matches[0].first_trade_date != matches[0].last_trade_date:
        raise ValueError("confirmation bar must match exactly one single-trade-date segment")
    return matches[0]


def _feature_values(candidate: GCFeatureLabelCandidateEvidence) -> tuple[object, ...]:
    i = candidate.inducement; pool = candidate.internal_pool; target = candidate.external_target
    active_range = candidate.active_range; gap = candidate.fair_value_gap; bar = candidate.confirmation_bar
    if i.direction is SMCV2Direction.BULLISH:
        penetration = pool.lower_tick - i.sweep_extreme_tick
        reclaim = i.reclaim_close_tick - pool.lower_tick
        distance = target.boundaries.lower_tick - i.reclaim_close_tick
        range_offset = 2 * bar.close_tick - active_range.low_tick - active_range.high_tick
        gap_offset = 2 * bar.close_tick - gap.lower_tick - gap.upper_tick
    else:
        penetration = i.sweep_extreme_tick - pool.upper_tick
        reclaim = pool.upper_tick - i.reclaim_close_tick
        distance = i.reclaim_close_tick - target.boundaries.upper_tick
        range_offset = active_range.low_tick + active_range.high_tick - 2 * bar.close_tick
        gap_offset = gap.lower_tick + gap.upper_tick - 2 * bar.close_tick
    if min(penetration, reclaim, distance) < 0:
        raise ValueError("impossible feature geometry")
    local = _utc(i.confirmation_timestamp, "confirmation_timestamp").astimezone(ZoneInfo("America/New_York"))
    minutes = local.hour * 60 + local.minute
    return (
        i.direction.value, i.structure_event_type.value, i.confirmation_offset_bars,
        pool.side.value, pool.upper_tick - pool.lower_tick, len(pool.member_swing_ids),
        penetration, reclaim, target.source_kind.value, distance, active_range.direction.value,
        active_range.high_tick - active_range.low_tick, range_offset,
        gap.upper_tick - gap.lower_tick, gap_offset, minutes - 7 * 60, 10 * 60 - minutes,
    )


def _bind_candidate(candidate: GCFeatureLabelCandidateEvidence, dataset: GCDatasetBuildResult, manifest: GCDatasetManifest, calendars: tuple[KillZoneCalendarEntry, ...], config: GCFeatureLabelConfig) -> tuple[GCFeatureRow, GCResearchLabel] | None:
    i = candidate.inducement; bar = candidate.confirmation_bar
    moment = (_exact_int(i.confirmation_index, "confirmation_index", minimum=0), _utc(i.confirmation_timestamp, "confirmation_timestamp"))
    if moment != (bar.index, _utc(bar.timestamp, "bar.timestamp")) or moment != (candidate.structure_event.provenance.confirmation_index, _utc(candidate.structure_event.provenance.confirmation_timestamp, "event confirmation")) or moment != (candidate.fair_value_gap.formation_end_index, _utc(candidate.fair_value_gap.formation_end_timestamp, "FVG formation")) or moment != (candidate.inducement_snapshot.index, _utc(candidate.inducement_snapshot.timestamp, "inducement snapshot")):
        raise ValueError("candidate first-known moments disagree")
    event_sequence = tuple(zip(candidate.structure_event.provenance.source_indices, map(lambda value: _utc(value, "event source"), candidate.structure_event.provenance.source_timestamps)))
    gap_sequence = tuple(zip(candidate.fair_value_gap.source_indices, map(lambda value: _utc(value, "FVG source"), candidate.fair_value_gap.source_timestamps)))
    shorter, longer = (event_sequence, gap_sequence) if len(event_sequence) <= len(gap_sequence) else (gap_sequence, event_sequence)
    if not shorter or tuple(longer[-len(shorter):]) != shorter or longer[-1] != moment:
        raise ValueError("event/FVG positional suffix mismatch")
    segment = _match_segment(dataset, bar)
    by_moment = {(item.index, _utc(item.timestamp, "bar.timestamp")): item for item in segment.bars}
    if any(source not in by_moment for source in set(event_sequence + gap_sequence)):
        raise ValueError("source moment is absent from canonical observations")
    context = candidate.kill_zone_context
    if context.observation_index != bar.index or _utc(context.observation_timestamp, "context timestamp") != moment[1] or context.trade_date != segment.first_trade_date or context.session_status not in (KillZoneSessionStatus.OPEN, KillZoneSessionStatus.EARLY_CLOSE) or context.quality is not KillZoneQuality.VERIFIED or context.timezone_name != "America/New_York" or context.calendar_version != manifest.calendar_version or context.timezone_data_version.upper() != manifest.timezone_data_version.upper():
        raise ValueError("candidate context reconciliation mismatch")
    local = moment[1].astimezone(ZoneInfo("America/New_York"))
    in_new_york_am = (
        context.zone is KillZoneName.NEW_YORK_AM
        and time(7) <= local.time().replace(tzinfo=None) < time(10)
    )
    external = candidate.external_target; internal = candidate.internal_pool_classification; pool = candidate.internal_pool
    if i.direction is SMCV2Direction.BULLISH:
        if internal.side is not LiquiditySide.SELL_SIDE or external.side is not LiquiditySide.BUY_SIDE or pool.side is not EqualLiquiditySide.LOW or bar.high_tick >= external.boundaries.lower_tick:
            raise ValueError("bullish role/target geometry mismatch")
    else:
        if internal.side is not LiquiditySide.BUY_SIDE or external.side is not LiquiditySide.SELL_SIDE or pool.side is not EqualLiquiditySide.HIGH or bar.low_tick <= external.boundaries.upper_tick:
            raise ValueError("bearish role/target geometry mismatch")
    if not in_new_york_am:
        return None
    values = _feature_values(candidate)
    lineage_ids = (i.inducement_id, candidate.inducement_snapshot.snapshot_id, candidate.active_range.snapshot_id, candidate.liquidity_map_snapshot.snapshot_id, external.classification_id, internal.classification_id, pool.snapshot_id, candidate.structure_event.event_id, candidate.fair_value_gap.gap_id, context.context_id, candidate.kill_zone_snapshot.snapshot_id)
    row_id = make_gc_feature_label_id(identity_kind=GCFeatureLabelIdentityKind.FEATURE_ROW, instrument="GC", timeframe="5M", tick_size=Decimal("0.1"), timezone_data_version=manifest.timezone_data_version, calendar_version=manifest.calendar_version, dataset_id=manifest.dataset_id, candidate_id=i.inducement_id, contract=segment.contract, trade_date=segment.first_trade_date, source_ids=segment.source_ids, lineage_ids=lineage_ids, detector_versions=_DETECTOR_VERSIONS, feature_schema_id=config.feature_schema_id, feature_values=values, effective_index=moment[0], effective_timestamp=moment[1])
    row = GCFeatureRow(row_id, "GC", "5M", Decimal("0.1"), manifest.dataset_id, i.inducement_id, segment.contract, segment.first_trade_date, moment[0], moment[1], manifest.calendar_version, manifest.timezone_data_version, segment.source_ids, lineage_ids, _DETECTOR_VERSIONS, config.feature_schema_id, values)
    label = _make_label(candidate, segment, manifest, calendars, config)
    return row, label


def _make_label(
    candidate: GCFeatureLabelCandidateEvidence,
    segment: GCCanonicalContractSegment,
    manifest: GCDatasetManifest,
    calendars: tuple[KillZoneCalendarEntry, ...],
    config: GCFeatureLabelConfig,
) -> GCResearchLabel:
    i = candidate.inducement; pool = candidate.internal_pool; target = candidate.external_target
    target_tick = target.boundaries.lower_tick if i.direction is SMCV2Direction.BULLISH else target.boundaries.upper_tick
    invalidation_tick = pool.lower_tick - 1 if i.direction is SMCV2Direction.BULLISH else pool.upper_tick + 1
    positions = [n for n, item in enumerate(segment.bars) if item == candidate.confirmation_bar]
    if len(positions) != 1:
        raise ValueError("confirmation bar position mismatch")
    start = positions[0] + 1
    future = segment.bars[start:start + config.horizon_bars]
    expected_end_index = candidate.confirmation_bar.index + config.horizon_bars
    expected_end_timestamp = _utc(candidate.confirmation_bar.timestamp, "confirmation timestamp") + timedelta(minutes=5 * config.horizon_bars)
    matching_calendars = tuple(
        item for item in calendars if item.trade_date == segment.first_trade_date
    )
    calendar_complete = (
        len(matching_calendars) == 1
        and matching_calendars[0].session_status
        is not KillZoneSessionStatus.SESSION_CLOSED
        and matching_calendars[0].session_open_timestamp is not None
        and matching_calendars[0].session_close_timestamp is not None
    )
    opening = (
        _utc(matching_calendars[0].session_open_timestamp, "session opening")
        if calendar_complete
        else None
    )
    closing = (
        _utc(matching_calendars[0].session_close_timestamp, "session closing")
        if calendar_complete
        else None
    )
    complete = len(future) == config.horizon_bars and calendar_complete
    previous = candidate.confirmation_bar
    for bar in future:
        timestamp = _utc(bar.timestamp, "horizon timestamp")
        if (
            type(bar) is not GCChronologicalBar
            or not bar.is_closed
            or bar.index != previous.index + 1
            or timestamp
            != _utc(previous.timestamp, "horizon timestamp")
            + timedelta(minutes=5)
            or opening is None
            or closing is None
            or not opening <= timestamp < closing
        ):
            complete = False
            break
        previous = bar
    first_index: int | None = None; first_timestamp: datetime | None = None
    if not complete:
        outcome = GCLabelOutcome.INCOMPLETE
        horizon_end_index: int | None = expected_end_index
        horizon_end_timestamp: datetime | None = expected_end_timestamp
    else:
        outcome = GCLabelOutcome.TIMEOUT
        for bar in future:
            target_hit = bar.high_tick >= target_tick if i.direction is SMCV2Direction.BULLISH else bar.low_tick <= target_tick
            invalid_hit = bar.close_tick <= invalidation_tick if i.direction is SMCV2Direction.BULLISH else bar.close_tick >= invalidation_tick
            if target_hit or invalid_hit:
                first_index, first_timestamp = bar.index, _utc(bar.timestamp, "outcome timestamp")
                outcome = GCLabelOutcome.SAME_BAR_AMBIGUOUS if target_hit and invalid_hit else (GCLabelOutcome.TARGET_FIRST if target_hit else GCLabelOutcome.INVALIDATION_FIRST)
                break
        horizon_end_index = future[-1].index
        horizon_end_timestamp = _utc(future[-1].timestamp, "horizon end")
    label_id = make_gc_feature_label_id(identity_kind=GCFeatureLabelIdentityKind.LABEL, instrument="GC", timeframe="5M", tick_size=Decimal("0.1"), timezone_data_version=manifest.timezone_data_version, calendar_version=manifest.calendar_version, dataset_id=manifest.dataset_id, candidate_id=i.inducement_id, contract=segment.contract, trade_date=segment.first_trade_date, label_schema_id=config.label_schema_id, horizon_bars=config.horizon_bars, target_tick=target_tick, invalidation_tick=invalidation_tick, outcome=outcome, effective_index=i.confirmation_index, effective_timestamp=i.confirmation_timestamp, first_outcome_index=first_index, first_outcome_timestamp=first_timestamp, horizon_end_index=horizon_end_index, horizon_end_timestamp=horizon_end_timestamp)
    return GCResearchLabel(label_id, "GC", "5M", Decimal("0.1"), manifest.dataset_id, i.inducement_id, segment.contract, segment.first_trade_date, i.confirmation_index, _utc(i.confirmation_timestamp, "confirmation timestamp"), manifest.calendar_version, manifest.timezone_data_version, config.label_schema_id, config.horizon_bars, target_tick, invalidation_tick, outcome, first_index, first_timestamp, horizon_end_index, horizon_end_timestamp)


def _result(
    status: SMCV2PrimitiveStatus,
    tokens: str | tuple[str, ...],
    rows: tuple[GCFeatureRow, ...] = (),
    labels: tuple[GCResearchLabel, ...] = (),
    manifest: GCFeatureLabelManifest | None = None,
) -> GCFeatureLabelResult:
    supplied = (tokens,) if type(tokens) is str else tokens
    if type(supplied) is not tuple or any(token not in _REASON_ORDER for token in supplied):
        raise ValueError("invalid result reason token")
    observed = set(supplied)
    reasons = tuple(token for token in _REASON_ORDER if token in observed)
    blocking = tuple(token for token in reasons if token in _REASON_ORDER[:4])
    return GCFeatureLabelResult(status, rows, labels, manifest, reasons, blocking)


def build_gc_feature_labels(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    candidates: tuple[GCFeatureLabelCandidateEvidence, ...] | None,
    config: GCFeatureLabelConfig = GCFeatureLabelConfig(),
) -> GCFeatureLabelResult:
    rows: list[GCFeatureRow] = []
    labels: list[GCResearchLabel] = []
    try:
        dataset_config = _validate_dataset_config(dataset_config)
        if type(config) is not GCFeatureLabelConfig or config.feature_schema_id != GC_AI_FEATURE_SCHEMA_ID or config.label_schema_id != GC_AI_LABEL_SCHEMA_ID or type(config.horizon_bars) is not int or config.horizon_bars != GC_AI_LABEL_HORIZON_BARS:
            raise ValueError("feature/label config mismatch")
        if candidates is not None:
            raw_candidates = _tuple(candidates, "candidates")
        else:
            raw_candidates = None
        if calendar_entries is not None:
            calendar_version = dataset.manifest.calendar_version if type(dataset) is GCDatasetBuildResult and type(dataset.manifest) is GCDatasetManifest else (calendar_entries[0].calendar_version if calendar_entries else "MISSING")
            calendars = _validate_calendar(calendar_entries, calendar_version)
        else:
            calendars = None
        manifest: GCDatasetManifest | None = None
        if dataset is not None:
            dataset, manifest = _validate_dataset(
                dataset_config,
                dataset,
                calendars,
            )
        if dataset is None or calendars is None or raw_candidates is None:
            if raw_candidates is not None:
                for item in raw_candidates:
                    _validate_candidate_static(item, "GC", "5M")
            return _result(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_TOP_LEVEL_CONTEXT")
        if manifest is None:
            raise ValueError("dataset manifest validation was not completed")
        if not raw_candidates:
            return _result(SMCV2PrimitiveStatus.NONE, "NO_ELIGIBLE_CANDIDATES")
        prior_key: tuple[int, datetime, str, str] | None = None
        deduped: list[GCFeatureLabelCandidateEvidence] = []
        for item in raw_candidates:
            i = item.inducement
            key = (i.confirmation_index, _utc(i.confirmation_timestamp, "confirmation_timestamp"), i.direction.value, i.inducement_id)
            if prior_key is not None and key < prior_key:
                raise ValueError("candidate order mismatch")
            prior_key = key
            if item not in deduped:
                deduped.append(item)
        index = 0
        incomplete = False
        while index < len(deduped):
            moment = (deduped[index].inducement.confirmation_index, _utc(deduped[index].inducement.confirmation_timestamp, "confirmation_timestamp"))
            group: list[GCFeatureLabelCandidateEvidence] = []
            while index < len(deduped) and (deduped[index].inducement.confirmation_index, _utc(deduped[index].inducement.confirmation_timestamp, "confirmation_timestamp")) == moment:
                group.append(deduped[index]); index += 1
            try:
                for item in group:
                    _validate_candidate_static(item, "GC", "5M")
                bound_group = [
                    _bind_candidate(item, dataset, manifest, calendars, config)
                    for item in group
                ]
                group_output = [item for item in bound_group if item is not None]
                eligible_candidates = [
                    item
                    for item, bound in zip(group, bound_group)
                    if bound is not None
                ]
                if len({item.inducement.direction for item in eligible_candidates}) > 1:
                    ambiguous_reasons = (
                        "AMBIGUOUS_OPPOSING_CANDIDATES",
                        *(("INCOMPLETE_LABEL_HORIZON",) if incomplete or any(
                            label.outcome is GCLabelOutcome.INCOMPLETE
                            for _, label in group_output
                        ) else ()),
                    )
                    return _result(
                        SMCV2PrimitiveStatus.AMBIGUOUS,
                        ambiguous_reasons,
                        tuple(rows),
                        tuple(labels),
                    )
            except (TypeError, ValueError, AttributeError, ArithmeticError):
                invalid_reasons = (
                    "INVALID_FEATURE_LABEL_EVIDENCE",
                    *(("INCOMPLETE_LABEL_HORIZON",) if incomplete else ()),
                )
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    invalid_reasons,
                    tuple(rows),
                    tuple(labels),
                )
            for row, label in group_output:
                rows.append(row); labels.append(label)
                incomplete = incomplete or label.outcome is GCLabelOutcome.INCOMPLETE
        if not rows:
            return _result(SMCV2PrimitiveStatus.NONE, "NO_ELIGIBLE_CANDIDATES")
        if incomplete:
            return _result(SMCV2PrimitiveStatus.UNKNOWN, "INCOMPLETE_LABEL_HORIZON", tuple(rows), tuple(labels))
        promotable = [(row, label) for row, label in zip(rows, labels) if label.outcome not in (GCLabelOutcome.SAME_BAR_AMBIGUOUS, GCLabelOutcome.INCOMPLETE, GCLabelOutcome.INVALID)]
        manifest_output: GCFeatureLabelManifest | None = None
        if promotable:
            row_ids = tuple(item[0].row_id for item in promotable); label_ids = tuple(item[1].label_id for item in promotable)
            manifest_id = make_gc_feature_label_id(identity_kind=GCFeatureLabelIdentityKind.MANIFEST, instrument="GC", timeframe="5M", tick_size=Decimal("0.1"), timezone_data_version=manifest.timezone_data_version, calendar_version=manifest.calendar_version, dataset_id=manifest.dataset_id, feature_schema_id=config.feature_schema_id, label_schema_id=config.label_schema_id, horizon_bars=config.horizon_bars, feature_row_ids=row_ids, label_ids=label_ids)
            manifest_output = GCFeatureLabelManifest(manifest_id, "GC", "5M", Decimal("0.1"), manifest.timezone_data_version, manifest.calendar_version, manifest.dataset_id, config.feature_schema_id, config.label_schema_id, config.horizon_bars, row_ids, label_ids)
        return _result(SMCV2PrimitiveStatus.VALID, "FEATURE_LABEL_VALID", tuple(rows), tuple(labels), manifest_output)
    except (TypeError, ValueError, AttributeError, ArithmeticError, ZoneInfoNotFoundError, importlib.metadata.PackageNotFoundError):
        invalid_reasons = (
            "INVALID_FEATURE_LABEL_EVIDENCE",
            *(("INCOMPLETE_LABEL_HORIZON",) if any(
                label.outcome is GCLabelOutcome.INCOMPLETE for label in labels
            ) else ()),
        )
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            invalid_reasons,
            tuple(rows),
            tuple(labels),
        )


__all__ = (
    "GC_FEATURE_LABEL_VERSION",
    "GC_AI_FEATURE_SCHEMA_ID",
    "GC_AI_LABEL_SCHEMA_ID",
    "GC_AI_LABEL_HORIZON_BARS",
    "GCLabelOutcome",
    "GCFeatureLabelIdentityKind",
    "GCFeatureLabelConfig",
    "GCFeatureLabelCandidateEvidence",
    "GCFeatureRow",
    "GCResearchLabel",
    "GCFeatureLabelManifest",
    "GCFeatureLabelResult",
    "make_gc_feature_label_id",
    "build_gc_feature_labels",
)
