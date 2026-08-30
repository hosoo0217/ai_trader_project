"""Deterministic, offline GC Phase A candidate-evidence aggregation.

This module is intentionally reference-only.  It validates an immutable
canonical dataset and structural seed, runs the locked standalone diagnostics
segment by segment, and assembles research candidate evidence.  It performs no
filesystem, network, model, training, OOS, strategy, risk, or execution work.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
import hashlib
from importlib import metadata
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from analysis.gc_dataset_builder import (
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCSegmentPartition,
)
from analysis.gc_feature_label_builder import GCFeatureLabelCandidateEvidence
from analysis.gc_structural_seed_evidence import (
    GCStructuralSeedConfig,
    GCCanonicalSeedEvidence,
    validate_gc_structural_seed_evidence,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.dealing_range import (
    DEALING_RANGE_DETECTOR_VERSION,
    DealingRangeConfig,
    DealingRangeKind,
    DealingRangeObservation,
    DealingRangeResult,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    analyze_dealing_ranges,
)
from smc.equal_liquidity import (
    EQUAL_LIQUIDITY_DETECTOR_VERSION,
    EqualLiquidityConfig,
    EqualLiquidityObservation,
    EqualLiquidityPool,
    EqualLiquidityResult,
    EqualLiquiditySide,
    EqualLiquiditySwing,
    analyze_equal_liquidity,
)
from smc.fair_value_gap import (
    FAIR_VALUE_GAP_DETECTOR_VERSION,
    FairValueGap,
    FairValueGapCandle,
    FairValueGapContextLink,
    FairValueGapResult,
    analyze_fair_value_gaps,
)
from smc.inducement import (
    INDUCEMENT_DETECTOR_VERSION,
    Inducement,
    InducementObservation,
    InducementPendingHorizon,
    InducementPendingHorizonResult,
    InducementResult,
    analyze_inducement_pending_horizons,
    analyze_inducements,
)
from smc.kill_zones import (
    KILL_ZONE_DETECTOR_VERSION,
    KILL_ZONE_TIMEZONE,
    KillZoneCalendarEntry,
    KillZoneName,
    KillZoneObservation,
    KillZoneQuality,
    KillZoneResult,
    KillZoneSessionStatus,
    analyze_kill_zones,
)
from smc.liquidity_map import (
    LIQUIDITY_MAP_DETECTOR_VERSION,
    LiquidityScope,
    LiquiditySide,
    LiquiditySourceKind,
    LiquidityMapResult,
    LiquidityMapSnapshot,
    analyze_liquidity_map,
)
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


GC_CANDIDATE_EVIDENCE_VERSION = "GC-CANDIDATE-EVIDENCE-V1"
GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION = "GC-CANDIDATE-FRONTIER-EVIDENCE-V1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_UTC = timezone.utc
_DETECTOR_VERSIONS = (
    ("EQUAL_LIQUIDITY", EQUAL_LIQUIDITY_DETECTOR_VERSION),
    ("DEALING_RANGE", DEALING_RANGE_DETECTOR_VERSION),
    ("LIQUIDITY_MAP", LIQUIDITY_MAP_DETECTOR_VERSION),
    ("FAIR_VALUE_GAP", FAIR_VALUE_GAP_DETECTOR_VERSION),
    ("INDUCEMENT", INDUCEMENT_DETECTOR_VERSION),
    ("KILL_ZONE", KILL_ZONE_DETECTOR_VERSION),
)


class GCCandidateEvidenceIdentityKind(str, Enum):
    BUNDLE = "BUNDLE"
    MANIFEST = "MANIFEST"


class GCCandidateFrontierIdentityKind(str, Enum):
    FRONTIER = "FRONTIER"


@dataclass(frozen=True)
class GCCandidateEvidenceConfig:
    equal_liquidity_config: EqualLiquidityConfig = EqualLiquidityConfig()
    dealing_range_config: DealingRangeConfig = DealingRangeConfig()

    def __post_init__(self) -> None:
        if type(self.equal_liquidity_config) is not EqualLiquidityConfig:
            raise TypeError("equal_liquidity_config must be EqualLiquidityConfig")
        if type(self.dealing_range_config) is not DealingRangeConfig:
            raise TypeError("dealing_range_config must be DealingRangeConfig")
        EqualLiquidityConfig(
            self.equal_liquidity_config.tolerance_ticks,
            self.equal_liquidity_config.minimum_members,
            self.equal_liquidity_config.minimum_separation_bars,
        )
        DealingRangeConfig(
            self.dealing_range_config.swing_confirmation_bars,
            self.dealing_range_config.break_buffer_ticks,
        )


@dataclass(frozen=True)
class GCSegmentCandidateEvidence:
    segment_ordinal: int
    segment_id: str
    evidence: GCFeatureLabelCandidateEvidence


@dataclass(frozen=True)
class GCCandidateEvidenceSegmentResult:
    segment_ordinal: int
    segment_id: str
    equal_liquidity_result: EqualLiquidityResult
    dealing_range_result: DealingRangeResult
    liquidity_map_result: LiquidityMapResult
    fair_value_gap_result: FairValueGapResult
    inducement_result: InducementResult
    kill_zone_result: KillZoneResult
    result_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCCandidateEvidenceManifest:
    manifest_id: str
    bundle_id: str
    version: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    calendar_version: str
    timezone_data_version: str
    seed_id: str
    config: GCCandidateEvidenceConfig
    detector_versions: tuple[tuple[str, str], ...]
    segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...]
    candidate_references: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class GCCandidateEvidenceResult:
    status: SMCV2PrimitiveStatus
    candidates: tuple[GCSegmentCandidateEvidence, ...] = ()
    segment_results: tuple[GCCandidateEvidenceSegmentResult, ...] = ()
    manifest: GCCandidateEvidenceManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class GCCandidateFrontierSegmentEvidence:
    segment_ordinal: int
    segment_id: str
    equal_liquidity_result: EqualLiquidityResult
    dealing_range_result: DealingRangeResult
    liquidity_map_result: LiquidityMapResult
    fair_value_gap_result: FairValueGapResult
    result_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCCandidateFrontierEvidence:
    frontier_id: str
    version: str
    instrument: str
    timeframe: str
    dataset_id: str
    seed_id: str
    canonical_control_digest: str
    frontier_ordinal: int
    source_segment: GCCandidateFrontierSegmentEvidence
    source_pending_result: InducementPendingHorizonResult
    receiving_segment: GCCandidateFrontierSegmentEvidence


@dataclass(frozen=True)
class GCCandidateFrontierEvidenceResult:
    status: SMCV2PrimitiveStatus
    frontier: GCCandidateFrontierEvidence | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


def _text(value: object, name: str, *, upper: bool = False) -> str:
    if type(value) is not str or not value.strip():
        raise TypeError(f"{name} must be a nonempty str")
    normalized = value.strip()
    return normalized.upper() if upper else normalized


def _hash(value: object, name: str) -> str:
    if type(value) is not str or _HASH.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be a timezone-aware datetime")
    return value.astimezone(_UTC)


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TypeError("Decimal values must be finite")
    if value.is_zero():
        return "0.0"
    output = format(value, "f")
    if "." in output:
        output = output.rstrip("0").rstrip(".")
    return output if "." in output else output + ".0"


def _canonical(value: object) -> object:
    if isinstance(value, datetime):
        return _timestamp(value, "timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return _decimal_text(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _canonical(getattr(value, item.name)) for item in fields(value)}
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("canonical object keys must be strings")
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) is list:
        return [_canonical(item) for item in value]
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def _sha(value: object) -> str:
    encoded = json.dumps(_canonical(value), ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _config_payload(config: GCCandidateEvidenceConfig) -> dict[str, object]:
    if type(config) is not GCCandidateEvidenceConfig:
        raise TypeError("config must be GCCandidateEvidenceConfig")
    GCCandidateEvidenceConfig(config.equal_liquidity_config, config.dealing_range_config)
    return {
        "equal_liquidity": _canonical(config.equal_liquidity_config),
        "dealing_range": _canonical(config.dealing_range_config),
    }


def _identity_material(
    *,
    identity_kind: GCCandidateEvidenceIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    calendar_version: str,
    timezone_data_version: str,
    seed_id: str,
    config: GCCandidateEvidenceConfig,
    detector_versions: tuple[tuple[str, str], ...],
    segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...],
    candidate_references: tuple[tuple[str, str], ...],
    bundle_id: str | None,
) -> dict[str, object]:
    if not isinstance(identity_kind, GCCandidateEvidenceIdentityKind):
        raise TypeError("identity_kind must be GCCandidateEvidenceIdentityKind")
    normalized_instrument = _text(instrument, "instrument", upper=True)
    normalized_timeframe = _text(timeframe, "timeframe", upper=True)
    if not isinstance(tick_size, Decimal) or not tick_size.is_finite() or tick_size <= 0:
        raise ValueError("tick_size must be a positive finite Decimal")
    normalized_dataset = _hash(dataset_id, "dataset_id")
    normalized_seed = _hash(seed_id, "seed_id")
    calendar = _text(calendar_version, "calendar_version")
    tzdata = _text(timezone_data_version, "timezone_data_version")
    _config_payload(config)
    if type(detector_versions) is not tuple or detector_versions != _DETECTOR_VERSIONS:
        raise ValueError("detector_versions do not match the locked detector chain")
    for item in detector_versions:
        if type(item) is not tuple or len(item) != 2:
            raise TypeError("detector_versions entries must be pairs")
        _text(item[0], "detector name")
        _text(item[1], "detector version")
    if type(segment_result_ids) is not tuple:
        raise TypeError("segment_result_ids must be a tuple")
    seen_segments: set[str] = set()
    for item in segment_result_ids:
        if type(item) is not tuple or len(item) != 2:
            raise TypeError("segment_result_ids entries must be pairs")
        segment_id = _hash(item[0], "segment_id")
        if segment_id in seen_segments:
            raise ValueError("segment_result_ids contain a duplicate segment")
        seen_segments.add(segment_id)
        if type(item[1]) is not tuple or len(item[1]) != len(_DETECTOR_VERSIONS):
            raise ValueError("each segment must bind exactly six detector result IDs")
        for result_id in item[1]:
            _hash(result_id, "detector result id")
    if type(candidate_references) is not tuple:
        raise TypeError("candidate_references must be a tuple")
    if not candidate_references:
        raise ValueError("candidate_references must be nonempty")
    seen_candidates: set[tuple[str, str]] = set()
    for item in candidate_references:
        if type(item) is not tuple or len(item) != 2:
            raise TypeError("candidate_references entries must be pairs")
        pair = (_hash(item[0], "candidate segment_id"), _hash(item[1], "inducement_id"))
        if pair[0] not in seen_segments or pair in seen_candidates:
            raise ValueError("candidate reference is dangling or duplicated")
        seen_candidates.add(pair)
    common = {
        "version": GC_CANDIDATE_EVIDENCE_VERSION,
        "identity_kind": identity_kind.value,
        "instrument": normalized_instrument,
        "timeframe": normalized_timeframe,
        "tick_size": _decimal_text(tick_size),
        "dataset_id": normalized_dataset,
        "calendar_version": calendar,
        "timezone_data_version": tzdata,
        "seed_id": normalized_seed,
        "config": _config_payload(config),
        "detector_versions": detector_versions,
        "segment_result_ids": segment_result_ids,
        "candidate_references": candidate_references,
    }
    if identity_kind is GCCandidateEvidenceIdentityKind.BUNDLE:
        if bundle_id is not None:
            raise ValueError("bundle_id is forbidden for BUNDLE")
    else:
        if bundle_id is None:
            raise ValueError("bundle_id is required for MANIFEST")
        expected = _sha({**common, "identity_kind": GCCandidateEvidenceIdentityKind.BUNDLE.value})
        if _hash(bundle_id, "bundle_id") != expected:
            raise ValueError("bundle_id does not match the canonical BUNDLE identity")
        common["bundle_id"] = bundle_id
    return common


def make_gc_candidate_evidence_id(
    *,
    identity_kind: GCCandidateEvidenceIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    calendar_version: str,
    timezone_data_version: str,
    seed_id: str,
    config: GCCandidateEvidenceConfig,
    detector_versions: tuple[tuple[str, str], ...],
    segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...],
    candidate_references: tuple[tuple[str, str], ...],
    bundle_id: str | None = None,
) -> str:
    """Return one exact kind-specific candidate-evidence identity."""

    return _sha(
        _identity_material(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            tick_size=tick_size,
            dataset_id=dataset_id,
            calendar_version=calendar_version,
            timezone_data_version=timezone_data_version,
            seed_id=seed_id,
            config=config,
            detector_versions=detector_versions,
            segment_result_ids=segment_result_ids,
            candidate_references=candidate_references,
            bundle_id=bundle_id,
        )
    )


def _frontier_segment_material(
    value: object,
    name: str,
) -> dict[str, object]:
    if type(value) is not GCCandidateFrontierSegmentEvidence:
        raise TypeError(f"{name} must be GCCandidateFrontierSegmentEvidence")
    if type(value.segment_ordinal) is not int or value.segment_ordinal < 0:
        raise ValueError(f"{name}.segment_ordinal must be a nonnegative integer")
    _hash(value.segment_id, f"{name}.segment_id")
    expected_types = (
        EqualLiquidityResult,
        DealingRangeResult,
        LiquidityMapResult,
        FairValueGapResult,
    )
    results = (
        value.equal_liquidity_result,
        value.dealing_range_result,
        value.liquidity_map_result,
        value.fair_value_gap_result,
    )
    if any(type(result) is not expected for result, expected in zip(results, expected_types, strict=True)):
        raise TypeError(f"{name} contains an invalid detector result")
    if type(value.result_ids) is not tuple or len(value.result_ids) != 4:
        raise ValueError(f"{name}.result_ids must contain exactly four identities")
    for item in value.result_ids:
        _hash(item, f"{name}.result_id")
    return {
        "segment_ordinal": value.segment_ordinal,
        "segment_id": value.segment_id,
        "equal_liquidity_result": value.equal_liquidity_result,
        "dealing_range_result": value.dealing_range_result,
        "liquidity_map_result": value.liquidity_map_result,
        "fair_value_gap_result": value.fair_value_gap_result,
        "result_ids": value.result_ids,
    }


def make_gc_candidate_frontier_evidence_id(
    *,
    identity_kind: GCCandidateFrontierIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    seed_id: str,
    canonical_control_digest: str,
    frontier_ordinal: int,
    source_segment: GCCandidateFrontierSegmentEvidence,
    source_pending_result: InducementPendingHorizonResult,
    receiving_segment: GCCandidateFrontierSegmentEvidence,
) -> str:
    """Return the deterministic identity of one validated control frontier."""

    if identity_kind is not GCCandidateFrontierIdentityKind.FRONTIER:
        raise TypeError("identity_kind must be GCCandidateFrontierIdentityKind.FRONTIER")
    normalized_instrument = _text(instrument, "instrument", upper=True)
    normalized_timeframe = _text(timeframe, "timeframe", upper=True)
    normalized_dataset = _hash(dataset_id, "dataset_id")
    normalized_seed = _hash(seed_id, "seed_id")
    normalized_control = _hash(canonical_control_digest, "canonical_control_digest")
    if type(frontier_ordinal) is not int or frontier_ordinal < 0:
        raise ValueError("frontier_ordinal must be a nonnegative integer")
    source = _frontier_segment_material(source_segment, "source_segment")
    receiving = _frontier_segment_material(receiving_segment, "receiving_segment")
    if source_segment.segment_ordinal != frontier_ordinal:
        raise ValueError("source segment ordinal must equal the frontier ordinal")
    if receiving_segment.segment_ordinal != frontier_ordinal + 1:
        raise ValueError("receiving segment ordinal must immediately follow the frontier")
    if type(source_pending_result) is not InducementPendingHorizonResult:
        raise TypeError("source_pending_result must be InducementPendingHorizonResult")
    return _sha(
        {
            "version": GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION,
            "identity_kind": identity_kind.value,
            "instrument": normalized_instrument,
            "timeframe": normalized_timeframe,
            "dataset_id": normalized_dataset,
            "seed_id": normalized_seed,
            "canonical_control_digest": normalized_control,
            "frontier_ordinal": frontier_ordinal,
            "source_segment": source,
            "source_pending_result": source_pending_result,
            "receiving_segment": receiving,
        }
    )


def _blocked(
    status: SMCV2PrimitiveStatus,
    reason: str,
    candidates: tuple[GCSegmentCandidateEvidence, ...] = (),
    segment_results: tuple[GCCandidateEvidenceSegmentResult, ...] = (),
) -> GCCandidateEvidenceResult:
    blocking = (reason,) if status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ) else ()
    return GCCandidateEvidenceResult(status, candidates, segment_results, None, (reason,), blocking)


def _prevalidate_calendar(value: object, expected_version: str | None) -> tuple[KillZoneCalendarEntry, ...]:
    if type(value) is not tuple:
        raise TypeError("calendar_entries must be a tuple")
    previous: date | None = None
    for item in value:
        if type(item) is not KillZoneCalendarEntry:
            raise TypeError("calendar entry has an invalid type")
        if expected_version is not None and item.calendar_version != expected_version:
            raise ValueError("calendar version mismatch")
        _text(item.calendar_version, "calendar_version")
        if type(item.trade_date) is not date:
            raise TypeError("trade_date must be a date")
        if previous is not None and item.trade_date <= previous:
            raise ValueError("calendar entries must be strictly ordered")
        previous = item.trade_date
        if type(item.session_status) is not KillZoneSessionStatus:
            raise TypeError("session_status must be KillZoneSessionStatus")
        if item.session_status is KillZoneSessionStatus.SESSION_CLOSED:
            if item.session_open_timestamp is not None or item.session_close_timestamp is not None:
                raise ValueError("closed calendar entries cannot carry session bounds")
        else:
            opening = _timestamp(item.session_open_timestamp, "session_open_timestamp")
            closing = _timestamp(item.session_close_timestamp, "session_close_timestamp")
            if opening >= closing:
                raise ValueError("calendar session bounds are not increasing")
            if closing - opening > timedelta(hours=24):
                raise ValueError("calendar session cannot exceed 24 hours")
            timezone_value = ZoneInfo(KILL_ZONE_TIMEZONE)
            opening_date = opening.astimezone(timezone_value).date()
            closing_date = closing.astimezone(timezone_value).date()
            if opening_date not in (item.trade_date - timedelta(days=1), item.trade_date):
                raise ValueError("calendar session open does not reconcile to trade_date")
            if closing_date != item.trade_date:
                raise ValueError("calendar session close does not reconcile to trade_date")
        if item.trade_date.weekday() >= 5 and item.session_status is not KillZoneSessionStatus.SESSION_CLOSED:
            raise ValueError("weekend trade dates must be closed")
    return value


def _runtime_tzdata() -> str | None:
    try:
        return metadata.version("tzdata")
    except metadata.PackageNotFoundError:
        return None


def _prevalidate_seed(value: object) -> GCCanonicalSeedEvidence:
    if type(value) is not GCCanonicalSeedEvidence:
        raise TypeError("structural_seed must be GCCanonicalSeedEvidence")
    _hash(value.seed_id, "seed_id")
    _text(value.seed_version, "seed_version")
    _text(value.instrument, "seed instrument")
    _text(value.timeframe, "seed timeframe")
    _hash(value.dataset_id, "seed dataset_id")
    _hash(value.source_bar_digest, "source_bar_digest")
    for name in (
        "dealing_range_swings",
        "equal_liquidity_swings",
        "structure_events",
        "fair_value_gap_context_links",
    ):
        if type(getattr(value, name)) is not tuple:
            raise TypeError(f"{name} must be a tuple")
    return value


def _moment_in_segment(index: int, timestamp: datetime, segment: GCCanonicalContractSegment) -> bool:
    normalized = _timestamp(timestamp, "evidence timestamp")
    return any(bar.index == index and _timestamp(bar.timestamp, "bar timestamp") == normalized for bar in segment.bars)


def _provenance_in_segment(value: object, segment: GCCanonicalContractSegment) -> bool:
    provenance = getattr(value, "provenance")
    return _moment_in_segment(
        provenance.confirmation_index,
        provenance.confirmation_timestamp,
        segment,
    )


def _link_in_segment(value: FairValueGapContextLink, segment: GCCanonicalContractSegment) -> bool:
    return _moment_in_segment(value.formation_end_index, value.formation_end_timestamp, segment)


def _bar_projections(segment: GCCanonicalContractSegment) -> tuple[
    tuple[EqualLiquidityObservation, ...],
    tuple[DealingRangeObservation, ...],
    tuple[FairValueGapCandle, ...],
    tuple[InducementObservation, ...],
]:
    equal: list[EqualLiquidityObservation] = []
    ranges: list[DealingRangeObservation] = []
    gaps: list[FairValueGapCandle] = []
    inducements: list[InducementObservation] = []
    previous: tuple[int, datetime] | None = None
    for bar in segment.bars:
        if type(bar) is not GCChronologicalBar:
            raise TypeError("segment bars must be GCChronologicalBar")
        moment = (bar.index, _timestamp(bar.timestamp, "bar timestamp"))
        if type(bar.index) is not int or bar.index < 0 or not bar.is_closed:
            raise ValueError("segment bars must be fully closed with nonnegative integer indices")
        if any(type(getattr(bar, name)) is not int for name in ("open_tick", "high_tick", "low_tick", "close_tick", "volume")):
            raise TypeError("bar ticks and volume must be integers")
        if bar.volume < 0 or not (bar.low_tick <= bar.open_tick <= bar.high_tick and bar.low_tick <= bar.close_tick <= bar.high_tick):
            raise ValueError("bar geometry or volume is invalid")
        if previous is not None and moment <= previous:
            raise ValueError("segment bars must be strictly chronological")
        previous = moment
        equal.append(EqualLiquidityObservation(bar.index, moment[1], bar.high_tick, bar.low_tick, bar.close_tick))
        ranges.append(DealingRangeObservation(bar.index, moment[1], bar.high_tick, bar.low_tick, bar.close_tick))
        gaps.append(FairValueGapCandle(bar.index, moment[1], bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick))
        inducements.append(InducementObservation(bar.index, moment[1], bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick, True))
    return tuple(equal), tuple(ranges), tuple(gaps), tuple(inducements)


def _calendar_slice(
    entries: tuple[KillZoneCalendarEntry, ...],
    segment: GCCanonicalContractSegment,
) -> tuple[KillZoneCalendarEntry, ...]:
    return tuple(item for item in entries if segment.first_trade_date <= item.trade_date <= segment.last_trade_date)


def _result_digest(
    segment_ordinal: int,
    segment_id: str,
    detector_name: str,
    detector_version: str,
    detector_config: object,
    result: object,
) -> str:
    return _sha(
        {
            "segment_ordinal": segment_ordinal,
            "segment_id": segment_id,
            "detector_name": detector_name,
            "detector_version": detector_version,
            "detector_config": detector_config,
            "result": result,
        }
    )


def _effective_range(value: DealingRangeSnapshot) -> tuple[int, datetime]:
    if value.transitions:
        transition = value.transitions[-1]
        return transition.index, _timestamp(transition.timestamp, "range transition timestamp")
    provenance = value.first_known_provenance
    return provenance.confirmation_index, _timestamp(provenance.confirmation_timestamp, "range timestamp")


def _effective_pool(value: EqualLiquidityPool) -> tuple[int, datetime]:
    if not value.lifecycle_events:
        provenance = value.first_known_provenance
        return provenance.confirmation_index, _timestamp(provenance.confirmation_timestamp, "pool timestamp")
    event = value.lifecycle_events[-1]
    return event.index, _timestamp(event.timestamp, "pool event timestamp")


def _one(values: tuple[object, ...], reason: str) -> object:
    if len(values) != 1:
        raise ValueError(reason)
    return values[0]


def _source_moments(
    indices: object,
    timestamps: object,
    segment: GCCanonicalContractSegment,
    name: str,
) -> tuple[tuple[int, datetime], ...]:
    if type(indices) is not tuple or type(timestamps) is not tuple or not indices:
        raise TypeError(f"{name} source moments must be nonempty tuples")
    if len(indices) != len(timestamps):
        raise ValueError(f"{name} source moment lengths do not match")
    moments: list[tuple[int, datetime]] = []
    for index, timestamp in zip(indices, timestamps, strict=True):
        if type(index) is not int or index < 0:
            raise TypeError(f"{name} source indices must be nonnegative integers")
        moment = (index, _timestamp(timestamp, f"{name} source timestamp"))
        if sum(
            bar.index == moment[0]
            and _timestamp(bar.timestamp, "segment bar timestamp") == moment[1]
            for bar in segment.bars
        ) != 1:
            raise ValueError(f"{name} source moment does not reconcile to the segment")
        moments.append(moment)
    if any(earlier >= later for earlier, later in zip(moments, moments[1:])):
        raise ValueError(f"{name} source moments must be strictly chronological")
    return tuple(moments)


def _blocked_detector_result(
    result: object,
    *,
    expected_type: type,
    candidates: tuple[GCSegmentCandidateEvidence, ...],
    segment_results: tuple[GCCandidateEvidenceSegmentResult, ...],
) -> GCCandidateEvidenceResult | None:
    if type(result) is not expected_type:
        raise TypeError("detector returned an invalid result type")
    status = getattr(result, "status", None)
    if type(status) is not SMCV2PrimitiveStatus:
        raise TypeError("detector result status must be SMCV2PrimitiveStatus")
    reasons = getattr(result, "reasons", None)
    blocking_reasons = getattr(result, "blocking_reasons", None)
    if (
        type(reasons) is not tuple
        or type(blocking_reasons) is not tuple
        or any(type(item) is not str or not item for item in reasons + blocking_reasons)
    ):
        raise TypeError("detector reasons must be tuples of nonempty strings")
    if status not in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ):
        return None
    reason = reasons[0] if type(reasons) is tuple and reasons else "DETECTOR_CHAIN_BLOCKED"
    return _blocked(status, reason, candidates, segment_results)


@dataclass(frozen=True)
class _GCBaseSegmentAnalysis:
    equal_liquidity_result: EqualLiquidityResult | None
    dealing_range_result: DealingRangeResult | None
    liquidity_map_result: LiquidityMapResult | None
    fair_value_gap_result: FairValueGapResult | None
    structure_events: tuple[DealingRangeStructureEvent, ...]
    inducement_observations: tuple[InducementObservation, ...]
    blocked_result: GCCandidateEvidenceResult | None = None


def _analyze_gc_base_segment(
    *,
    instrument: str,
    timeframe: str,
    segment: GCCanonicalContractSegment,
    structural_seed: GCCanonicalSeedEvidence,
    config: GCCandidateEvidenceConfig,
    candidates: tuple[GCSegmentCandidateEvidence, ...] = (),
    segment_results: tuple[GCCandidateEvidenceSegmentResult, ...] = (),
) -> _GCBaseSegmentAnalysis:
    equal_observations, range_observations, candles, inducement_observations = _bar_projections(segment)
    dealing_swings = tuple(
        item
        for item in structural_seed.dealing_range_swings
        if _provenance_in_segment(item, segment)
    )
    equal_swings = tuple(
        item
        for item in structural_seed.equal_liquidity_swings
        if _provenance_in_segment(item, segment)
    )
    events = tuple(
        item
        for item in structural_seed.structure_events
        if _provenance_in_segment(item, segment)
    )
    links = tuple(
        item
        for item in structural_seed.fair_value_gap_context_links
        if _link_in_segment(item, segment)
    )
    equal_result = analyze_equal_liquidity(
        instrument=instrument,
        timeframe=timeframe,
        swings=equal_swings,
        observations=equal_observations,
        config=config.equal_liquidity_config,
    )
    blocked = _blocked_detector_result(
        equal_result,
        expected_type=EqualLiquidityResult,
        candidates=candidates,
        segment_results=segment_results,
    )
    if blocked is not None:
        return _GCBaseSegmentAnalysis(None, None, None, None, events, inducement_observations, blocked)
    range_result = analyze_dealing_ranges(
        instrument=instrument,
        timeframe=timeframe,
        swings=dealing_swings,
        observations=range_observations,
        structure_events=events,
        config=config.dealing_range_config,
    )
    blocked = _blocked_detector_result(
        range_result,
        expected_type=DealingRangeResult,
        candidates=candidates,
        segment_results=segment_results,
    )
    if blocked is not None:
        return _GCBaseSegmentAnalysis(equal_result, None, None, None, events, inducement_observations, blocked)
    liquidity_result = analyze_liquidity_map(
        instrument=instrument,
        timeframe=timeframe,
        swings=dealing_swings,
        equal_liquidity_pools=equal_result.pools,
        dealing_ranges=range_result.ranges,
    )
    blocked = _blocked_detector_result(
        liquidity_result,
        expected_type=LiquidityMapResult,
        candidates=candidates,
        segment_results=segment_results,
    )
    if blocked is not None:
        return _GCBaseSegmentAnalysis(equal_result, range_result, None, None, events, inducement_observations, blocked)
    fvg_result = analyze_fair_value_gaps(
        instrument=instrument,
        timeframe=timeframe,
        candles=candles,
        context_links=links,
    )
    blocked = _blocked_detector_result(
        fvg_result,
        expected_type=FairValueGapResult,
        candidates=candidates,
        segment_results=segment_results,
    )
    if blocked is not None:
        return _GCBaseSegmentAnalysis(equal_result, range_result, liquidity_result, None, events, inducement_observations, blocked)
    return _GCBaseSegmentAnalysis(
        equal_result,
        range_result,
        liquidity_result,
        fvg_result,
        events,
        inducement_observations,
    )


def _assemble_candidate(
    *,
    segment_ordinal: int,
    segment: GCCanonicalContractSegment,
    inducement: Inducement,
    ranges: tuple[DealingRangeSnapshot, ...],
    pools: tuple[EqualLiquidityPool, ...],
    maps: tuple[LiquidityMapSnapshot, ...],
    events: tuple[DealingRangeStructureEvent, ...],
    gaps: tuple[FairValueGap, ...],
    fvg_result: FairValueGapResult,
    inducement_result: InducementResult,
    kill_zone_result: KillZoneResult,
) -> GCSegmentCandidateEvidence | None:
    confirmation = (inducement.confirmation_index, _timestamp(inducement.confirmation_timestamp, "confirmation timestamp"))
    sweep = (inducement.sweep_index, _timestamp(inducement.sweep_timestamp, "sweep timestamp"))
    eligible_ranges = tuple(
        item
        for item in ranges
        if item.kind is DealingRangeKind.EXTERNAL
        and item.state is DealingRangeState.ACTIVE
        and _effective_range(item) < sweep
    )
    if not eligible_ranges:
        raise ValueError("pre-sweep ACTIVE external range is missing")
    latest_range_moment = max(_effective_range(item) for item in eligible_ranges)
    latest_ranges = tuple(item for item in eligible_ranges if _effective_range(item) == latest_range_moment)
    active_range = _one(latest_ranges, "latest pre-sweep ACTIVE external range is ambiguous")
    if (
        active_range.lineage_id != inducement.active_range_lineage_id
        or active_range.snapshot_id != inducement.active_range_snapshot_id
    ):
        raise ValueError("inducement does not reference the latest pre-sweep ACTIVE external range")
    map_snapshot = _one(
        tuple(item for item in maps if item.snapshot_id == inducement.liquidity_map_snapshot_id),
        "inducement Liquidity Map reference is not exact",
    )
    external = _one(
        tuple(item for item in map_snapshot.classifications if item.classification_id == inducement.external_target_classification_id),
        "external target reference is not exact",
    )
    internal = _one(
        tuple(item for item in map_snapshot.classifications if item.classification_id == inducement.internal_pool_classification_id),
        "internal pool classification reference is not exact",
    )
    matching_pools = tuple(
        item for item in pools
        if item.lineage_id == inducement.internal_pool_id and _effective_pool(item) <= sweep
    )
    if not matching_pools:
        raise ValueError("internal pool reference is missing")
    internal_pool = _one(
        matching_pools,
        "internal pool lineage is missing, duplicated, or forked",
    )
    internal_side = (
        LiquiditySide.SELL_SIDE
        if inducement.direction is SMCV2Direction.BULLISH
        else LiquiditySide.BUY_SIDE
    )
    external_side = (
        LiquiditySide.BUY_SIDE
        if inducement.direction is SMCV2Direction.BULLISH
        else LiquiditySide.SELL_SIDE
    )
    pool_side = (
        EqualLiquiditySide.LOW
        if inducement.direction is SMCV2Direction.BULLISH
        else EqualLiquiditySide.HIGH
    )
    if inducement.direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
        raise ValueError("inducement direction must be directional")
    if (
        active_range.direction is not inducement.direction
        or map_snapshot.active_range_lineage_id != active_range.lineage_id
        or map_snapshot.active_range_snapshot_id != active_range.snapshot_id
        or internal_pool.side is not pool_side
        or not (active_range.low_tick < internal_pool.lower_tick <= internal_pool.upper_tick < active_range.high_tick)
        or internal.source_kind is not LiquiditySourceKind.EQUAL_LIQUIDITY_POOL
        or internal.source_id != internal_pool.lineage_id
        or internal.side is not internal_side
        or internal.scope is not LiquidityScope.INTERNAL
        or external.side is not external_side
        or external.scope is not LiquidityScope.EXTERNAL
        or internal.active_range_lineage_id != active_range.lineage_id
        or internal.active_range_snapshot_id != active_range.snapshot_id
        or external.active_range_lineage_id != active_range.lineage_id
        or external.active_range_snapshot_id != active_range.snapshot_id
    ):
        raise ValueError("candidate range, map, and liquidity roles do not reconcile")
    event = _one(tuple(item for item in events if item.event_id == inducement.structure_event_id), "structure event reference is not exact")
    gap = _one(tuple(item for item in gaps if item.gap_id == inducement.fair_value_gap_id), "FVG reference is not exact")
    event_moments = _source_moments(
        event.provenance.source_indices,
        event.provenance.source_timestamps,
        segment,
        "structure event",
    )
    gap_moments = _source_moments(gap.source_indices, gap.source_timestamps, segment, "FVG")
    event_confirmation = (
        event.provenance.confirmation_index,
        _timestamp(event.provenance.confirmation_timestamp, "event confirmation timestamp"),
    )
    gap_formation = (
        gap.formation_end_index,
        _timestamp(gap.formation_end_timestamp, "FVG formation timestamp"),
    )
    shorter, longer = (
        (event_moments, gap_moments)
        if len(event_moments) <= len(gap_moments)
        else (gap_moments, event_moments)
    )
    if (
        event_confirmation != confirmation
        or gap_formation != confirmation
        or event_moments[-1] != confirmation
        or gap_moments[-1] != confirmation
        or longer[-len(shorter):] != shorter
        or event.event_type is not inducement.structure_event_type
        or gap.structure_event_id != event.event_id
        or gap.structure_event_type is not event.event_type
        or gap.displacement_id is None
        or gap.displacement_id != inducement.displacement_id
    ):
        raise ValueError("event/FVG causal binding is invalid")
    fvg_transitions = tuple(
        item for item in fvg_result.transitions
        if item.gap_id == gap.gap_id and (item.index, _timestamp(item.timestamp, "FVG transition timestamp")) <= confirmation
    )
    fvg_snapshots = tuple(
        item for item in fvg_result.snapshots
        if item.gap_id == gap.gap_id and (item.index, _timestamp(item.timestamp, "FVG snapshot timestamp")) <= confirmation
    )
    if not fvg_transitions or len(fvg_transitions) != len(fvg_snapshots):
        raise ValueError("FVG history through confirmation is incomplete")
    transition_history: list[str] = []
    for transition, snapshot in zip(fvg_transitions, fvg_snapshots, strict=True):
        transition_history.append(transition.transition_id)
        if (
            transition.gap_id != gap.gap_id
            or snapshot.gap_id != gap.gap_id
            or snapshot.direction is not gap.direction
            or snapshot.state is not transition.to_state
            or (snapshot.index, _timestamp(snapshot.timestamp, "FVG snapshot timestamp"))
            != (transition.index, _timestamp(transition.timestamp, "FVG transition timestamp"))
            or snapshot.transition_ids != tuple(transition_history)
        ):
            raise ValueError("FVG transition/snapshot history does not mirror one-to-one")
    inducement_snapshot = _one(
        tuple(
            item for item in inducement_result.snapshots
            if item.index == confirmation[0]
            and _timestamp(item.timestamp, "inducement snapshot timestamp") == confirmation[1]
            and inducement.inducement_id in item.inducement_ids
        ),
        "inducement snapshot reference is not exact",
    )
    contexts = tuple(
        item for item in kill_zone_result.contexts
        if item.observation_index == confirmation[0]
        and _timestamp(item.observation_timestamp, "kill-zone timestamp") == confirmation[1]
    )
    if not contexts:
        raise ValueError("kill-zone context is missing at confirmation")
    eligible = tuple(
        item for item in contexts
        if item.zone is KillZoneName.NEW_YORK_AM
        and item.quality is KillZoneQuality.VERIFIED
        and item.session_status in (KillZoneSessionStatus.OPEN, KillZoneSessionStatus.EARLY_CLOSE)
    )
    if not eligible:
        return None
    kill_context = _one(eligible, "kill-zone context is ambiguous")
    kill_snapshot = _one(
        tuple(
            item for item in kill_zone_result.snapshots
            if item.index == confirmation[0]
            and _timestamp(item.timestamp, "kill-zone snapshot timestamp") == confirmation[1]
            and kill_context.context_id in item.context_ids
        ),
        "kill-zone snapshot reference is not exact",
    )
    confirmation_bar = _one(
        tuple(
            item for item in segment.bars
            if item.index == confirmation[0]
            and _timestamp(item.timestamp, "confirmation bar timestamp") == confirmation[1]
        ),
        "confirmation bar reference is not exact",
    )
    evidence = GCFeatureLabelCandidateEvidence(
        inducement=inducement,
        inducement_snapshot=inducement_snapshot,
        active_range=active_range,
        liquidity_map_snapshot=map_snapshot,
        external_target=external,
        internal_pool_classification=internal,
        internal_pool=internal_pool,
        structure_event=event,
        fair_value_gap=gap,
        fair_value_gap_transitions=fvg_transitions,
        fair_value_gap_snapshots=fvg_snapshots,
        kill_zone_context=kill_context,
        kill_zone_snapshot=kill_snapshot,
        confirmation_bar=confirmation_bar,
    )
    return GCSegmentCandidateEvidence(segment_ordinal, segment.segment_id, evidence)


def _segment_result(
    *,
    ordinal: int,
    segment: GCCanonicalContractSegment,
    equal: EqualLiquidityResult,
    ranges: DealingRangeResult,
    liquidity: LiquidityMapResult,
    gaps: FairValueGapResult,
    inducements: InducementResult,
    kill_zones: KillZoneResult,
    config: GCCandidateEvidenceConfig,
) -> GCCandidateEvidenceSegmentResult:
    results = (equal, ranges, liquidity, gaps, inducements, kill_zones)
    configs = (config.equal_liquidity_config, config.dealing_range_config, None, None, None, None)
    result_ids = tuple(
        _result_digest(ordinal, segment.segment_id, name, version, detector_config, result)
        for (name, version), detector_config, result in zip(_DETECTOR_VERSIONS, configs, results, strict=True)
    )
    return GCCandidateEvidenceSegmentResult(
        ordinal,
        segment.segment_id,
        equal,
        ranges,
        liquidity,
        gaps,
        inducements,
        kill_zones,
        result_ids,
    )


def build_gc_candidate_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCandidateEvidenceResult:
    """Build deterministic, segment-local GC research candidate evidence."""

    seed_validation = None
    try:
        if type(dataset_config) is not GCDatasetBuildConfig:
            raise TypeError("dataset_config must be GCDatasetBuildConfig")
        _config_payload(config)
        calendar_version = dataset.manifest.calendar_version if type(dataset) is GCDatasetBuildResult and dataset.manifest is not None else None
        if calendar_entries is not None:
            calendars = _prevalidate_calendar(calendar_entries, calendar_version)
        else:
            calendars = None
        if structural_seed is not None:
            _prevalidate_seed(structural_seed)
    except Exception:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_SUPPLIED_CONTEXT")

    if dataset is not None:
        if type(dataset) is not GCDatasetBuildResult or not isinstance(dataset.status, GCDatasetBuildStatus):
            return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_DATASET")
        if dataset.status is GCDatasetBuildStatus.INVALID:
            return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_DATASET")
        if dataset.status is GCDatasetBuildStatus.AMBIGUOUS:
            return _blocked(SMCV2PrimitiveStatus.AMBIGUOUS, "DATASET_AMBIGUOUS")
        if dataset.status is GCDatasetBuildStatus.UNKNOWN:
            return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "DATASET_UNKNOWN")
        oos_manifest_exposed = (
            dataset.manifest is not None
            and type(getattr(dataset.manifest, "oos_bar_count", None)) is int
            and dataset.manifest.oos_bar_count != 0
        )
        oos_segment_exposed = type(dataset.segments) is tuple and any(
            type(item) is GCCanonicalContractSegment
            and item.partition is GCSegmentPartition.OOS_HOLDOUT
            for item in dataset.segments
        )
        if oos_manifest_exposed or oos_segment_exposed:
            return _blocked(SMCV2PrimitiveStatus.INVALID, "OOS_ACCESS_FORBIDDEN")
        try:
            seed_validation = validate_gc_structural_seed_evidence(
                dataset_config=dataset_config,
                dataset=dataset,
                structural_seed=structural_seed,
                config=GCStructuralSeedConfig(),
            )
        except Exception:
            return _blocked(SMCV2PrimitiveStatus.INVALID, "STRUCTURAL_VALIDATION_EXCEPTION")
        if seed_validation.status in (
            SMCV2PrimitiveStatus.INVALID,
            SMCV2PrimitiveStatus.AMBIGUOUS,
        ):
            reason = seed_validation.reasons[0] if seed_validation.reasons else "STRUCTURAL_EVIDENCE_BLOCKED"
            return _blocked(seed_validation.status, reason)

    if dataset is None or calendar_entries is None or structural_seed is None:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_TOP_LEVEL_CONTEXT")
    if dataset.status is GCDatasetBuildStatus.NONE:
        return GCCandidateEvidenceResult(SMCV2PrimitiveStatus.NONE, reasons=("DATASET_NONE",))
    if dataset.manifest is None or dataset.dataset_id is None:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_DATASET")
    runtime_tzdata = _runtime_tzdata()
    try:
        ZoneInfo(KILL_ZONE_TIMEZONE)
    except ZoneInfoNotFoundError:
        runtime_tzdata = None
    if runtime_tzdata is None:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "TIMEZONE_DATA_UNAVAILABLE")
    if runtime_tzdata != dataset_config.timezone_data_version or runtime_tzdata != dataset.manifest.timezone_data_version:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "TIMEZONE_DATA_VERSION_MISMATCH")

    if seed_validation is None:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "STRUCTURAL_VALIDATION_MISSING")
    if seed_validation.status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ):
        reason = seed_validation.reasons[0] if seed_validation.reasons else "STRUCTURAL_EVIDENCE_BLOCKED"
        return _blocked(seed_validation.status, reason)
    if seed_validation.seed != structural_seed:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "STRUCTURAL_SEED_REPLACED")

    instrument = _text(dataset_config.instrument, "instrument", upper=True)
    timeframe = _text(dataset_config.timeframe, "timeframe", upper=True)
    promoted_candidates: list[GCSegmentCandidateEvidence] = []
    promoted_segments: list[GCCandidateEvidenceSegmentResult] = []
    try:
        for ordinal, segment in enumerate(dataset.segments):
            if type(segment) is not GCCanonicalContractSegment or segment.partition is not GCSegmentPartition.DEVELOPMENT:
                raise ValueError("candidate evidence accepts development segments only")
            _hash(segment.segment_id, "segment_id")
            base = _analyze_gc_base_segment(
                instrument=instrument,
                timeframe=timeframe,
                segment=segment,
                structural_seed=structural_seed,
                config=config,
                candidates=tuple(promoted_candidates),
                segment_results=tuple(promoted_segments),
            )
            if base.blocked_result is not None:
                return base.blocked_result
            equal_result = base.equal_liquidity_result
            range_result = base.dealing_range_result
            liquidity_result = base.liquidity_map_result
            fvg_result = base.fair_value_gap_result
            if not (
                type(equal_result) is EqualLiquidityResult
                and type(range_result) is DealingRangeResult
                and type(liquidity_result) is LiquidityMapResult
                and type(fvg_result) is FairValueGapResult
            ):
                raise TypeError("base detector chain did not return complete results")
            events = base.structure_events
            inducement_observations = base.inducement_observations
            inducement_ranges = tuple(
                item
                for item in range_result.ranges
                if item.kind is DealingRangeKind.EXTERNAL
            )
            inducement_gaps = tuple(
                item
                for item in fvg_result.gaps
                if item.displacement_id is not None
            )
            inducement_gap_ids = frozenset(item.gap_id for item in inducement_gaps)
            inducement_gap_transitions = tuple(
                item
                for item in fvg_result.transitions
                if item.gap_id in inducement_gap_ids
            )
            inducement_gap_snapshots = tuple(
                item
                for item in fvg_result.snapshots
                if item.gap_id in inducement_gap_ids
            )
            inducement_result = analyze_inducements(
                instrument=instrument,
                timeframe=timeframe,
                dealing_range_snapshots=inducement_ranges,
                liquidity_map_snapshots=liquidity_result.snapshots,
                equal_liquidity_pools=equal_result.pools,
                structure_events=events,
                fair_value_gaps=inducement_gaps,
                fair_value_gap_transitions=inducement_gap_transitions,
                fair_value_gap_snapshots=inducement_gap_snapshots,
                observations=inducement_observations,
            )
            blocked = _blocked_detector_result(
                inducement_result,
                expected_type=InducementResult,
                candidates=tuple(promoted_candidates),
                segment_results=tuple(promoted_segments),
            )
            if blocked is not None:
                return blocked
            kill_result = analyze_kill_zones(
                instrument=instrument,
                timeframe=timeframe,
                observations=tuple(KillZoneObservation(item.index, item.timestamp, True) for item in segment.bars),
                calendar_entries=_calendar_slice(calendars, segment),
                calendar_version=dataset.manifest.calendar_version,
                timezone_data_version=dataset.manifest.timezone_data_version,
            )
            blocked = _blocked_detector_result(
                kill_result,
                expected_type=KillZoneResult,
                candidates=tuple(promoted_candidates),
                segment_results=tuple(promoted_segments),
            )
            if blocked is not None:
                return blocked
            segment_candidates: list[GCSegmentCandidateEvidence] = []
            for inducement in inducement_result.inducements:
                candidate = _assemble_candidate(
                    segment_ordinal=ordinal,
                    segment=segment,
                    inducement=inducement,
                    ranges=range_result.ranges,
                    pools=equal_result.pools,
                    maps=liquidity_result.snapshots,
                    events=events,
                    gaps=fvg_result.gaps,
                    fvg_result=fvg_result,
                    inducement_result=inducement_result,
                    kill_zone_result=kill_result,
                )
                if candidate is not None:
                    existing = tuple(
                        item
                        for item in segment_candidates
                        if item.evidence.inducement.inducement_id
                        == candidate.evidence.inducement.inducement_id
                    )
                    if existing:
                        if len(existing) != 1 or existing[0] != candidate:
                            raise ValueError("same-segment candidate evidence is forked")
                        continue
                    segment_candidates.append(candidate)
            segment_result = _segment_result(
                ordinal=ordinal,
                segment=segment,
                equal=equal_result,
                ranges=range_result,
                liquidity=liquidity_result,
                gaps=fvg_result,
                inducements=inducement_result,
                kill_zones=kill_result,
                config=config,
            )
            promoted_segments.append(segment_result)
            promoted_candidates.extend(segment_candidates)
    except Exception:
        return _blocked(
            SMCV2PrimitiveStatus.INVALID,
            "INVALID_CANDIDATE_EVIDENCE",
            tuple(promoted_candidates),
            tuple(promoted_segments),
        )

    if not promoted_candidates:
        return GCCandidateEvidenceResult(
            SMCV2PrimitiveStatus.NONE,
            segment_results=tuple(promoted_segments),
            reasons=("NO_QUALIFYING_CANDIDATE_EVIDENCE",),
        )
    try:
        segment_result_ids = tuple((item.segment_id, item.result_ids) for item in promoted_segments)
        candidate_references = tuple((item.segment_id, item.evidence.inducement.inducement_id) for item in promoted_candidates)
        bundle_id = make_gc_candidate_evidence_id(
            identity_kind=GCCandidateEvidenceIdentityKind.BUNDLE,
            instrument=instrument,
            timeframe=timeframe,
            tick_size=dataset_config.tick_size,
            dataset_id=dataset.dataset_id,
            calendar_version=dataset.manifest.calendar_version,
            timezone_data_version=dataset.manifest.timezone_data_version,
            seed_id=structural_seed.seed_id,
            config=config,
            detector_versions=_DETECTOR_VERSIONS,
            segment_result_ids=segment_result_ids,
            candidate_references=candidate_references,
        )
        manifest_id = make_gc_candidate_evidence_id(
            identity_kind=GCCandidateEvidenceIdentityKind.MANIFEST,
            instrument=instrument,
            timeframe=timeframe,
            tick_size=dataset_config.tick_size,
            dataset_id=dataset.dataset_id,
            calendar_version=dataset.manifest.calendar_version,
            timezone_data_version=dataset.manifest.timezone_data_version,
            seed_id=structural_seed.seed_id,
            config=config,
            detector_versions=_DETECTOR_VERSIONS,
            segment_result_ids=segment_result_ids,
            candidate_references=candidate_references,
            bundle_id=bundle_id,
        )
        manifest = GCCandidateEvidenceManifest(
            manifest_id,
            bundle_id,
            GC_CANDIDATE_EVIDENCE_VERSION,
            instrument,
            timeframe,
            dataset_config.tick_size,
            dataset.dataset_id,
            dataset.manifest.calendar_version,
            dataset.manifest.timezone_data_version,
            structural_seed.seed_id,
            config,
            _DETECTOR_VERSIONS,
            segment_result_ids,
            candidate_references,
        )
    except Exception:
        return _blocked(
            SMCV2PrimitiveStatus.INVALID,
            "INVALID_CANDIDATE_MANIFEST",
            tuple(promoted_candidates),
            tuple(promoted_segments),
        )
    return GCCandidateEvidenceResult(
        SMCV2PrimitiveStatus.VALID,
        tuple(promoted_candidates),
        tuple(promoted_segments),
        manifest,
        ("CANDIDATE_EVIDENCE_VALID",),
    )


def _frontier_blocked(
    status: SMCV2PrimitiveStatus,
    reason: str,
) -> GCCandidateFrontierEvidenceResult:
    blocking = (reason,) if status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ) else ()
    return GCCandidateFrontierEvidenceResult(
        status,
        reasons=(reason,),
        blocking_reasons=blocking,
    )


def _frontier_segment_evidence(
    *,
    ordinal: int,
    segment: GCCanonicalContractSegment,
    base: _GCBaseSegmentAnalysis,
    config: GCCandidateEvidenceConfig,
) -> GCCandidateFrontierSegmentEvidence:
    equal = base.equal_liquidity_result
    ranges = base.dealing_range_result
    liquidity = base.liquidity_map_result
    gaps = base.fair_value_gap_result
    if not (
        type(equal) is EqualLiquidityResult
        and type(ranges) is DealingRangeResult
        and type(liquidity) is LiquidityMapResult
        and type(gaps) is FairValueGapResult
    ):
        raise TypeError("frontier base detector results are incomplete")
    results = (equal, ranges, liquidity, gaps)
    configs = (config.equal_liquidity_config, config.dealing_range_config, None, None)
    result_ids = tuple(
        _result_digest(ordinal, segment.segment_id, name, version, detector_config, result)
        for (name, version), detector_config, result in zip(
            _DETECTOR_VERSIONS[:4],
            configs,
            results,
            strict=True,
        )
    )
    return GCCandidateFrontierSegmentEvidence(
        ordinal,
        segment.segment_id,
        equal,
        ranges,
        liquidity,
        gaps,
        result_ids,
    )


def analyze_gc_candidate_frontier_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    canonical_candidate_evidence: GCCandidateEvidenceResult | None,
    config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCandidateFrontierEvidenceResult:
    """Build immutable base evidence for the first unpromoted control pair."""

    try:
        if type(dataset_config) is not GCDatasetBuildConfig:
            raise TypeError("dataset_config must be GCDatasetBuildConfig")
        _config_payload(config)
        if canonical_candidate_evidence is not None and type(canonical_candidate_evidence) is not GCCandidateEvidenceResult:
            raise TypeError("canonical_candidate_evidence must be GCCandidateEvidenceResult")
    except (TypeError, ValueError):
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_SUPPLIED_CONTEXT")
    except Exception:
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "VALIDATION_EXCEPTION")

    if any(
        item is None
        for item in (
            dataset,
            calendar_entries,
            structural_seed,
            canonical_candidate_evidence,
        )
    ):
        return _frontier_blocked(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_TOP_LEVEL_CONTEXT")
    assert dataset is not None
    assert calendar_entries is not None
    assert structural_seed is not None
    assert canonical_candidate_evidence is not None

    try:
        rebuilt = build_gc_candidate_evidence(
            dataset_config=dataset_config,
            dataset=dataset,
            calendar_entries=calendar_entries,
            structural_seed=structural_seed,
            config=config,
        )
    except Exception:
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_REBUILD_EXCEPTION")
    if rebuilt != canonical_candidate_evidence:
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_CONTROL_DRIFT")
    if canonical_candidate_evidence.status is SMCV2PrimitiveStatus.INVALID:
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_CONTROL_INVALID")
    if canonical_candidate_evidence.status is SMCV2PrimitiveStatus.AMBIGUOUS:
        return _frontier_blocked(SMCV2PrimitiveStatus.AMBIGUOUS, "CANONICAL_CONTROL_AMBIGUOUS")
    if canonical_candidate_evidence.status is not SMCV2PrimitiveStatus.UNKNOWN:
        return _frontier_blocked(SMCV2PrimitiveStatus.NONE, "CONTROL_FRONTIER_NOT_APPLICABLE")

    try:
        if canonical_candidate_evidence.candidates or canonical_candidate_evidence.manifest is not None:
            raise ValueError("UNKNOWN canonical control cannot contain candidates or a manifest")
        if type(dataset) is not GCDatasetBuildResult or dataset.status is not GCDatasetBuildStatus.VALID:
            raise ValueError("frontier analysis requires a VALID dataset")
        if dataset.manifest is None or dataset.dataset_id is None:
            raise ValueError("frontier dataset identity is incomplete")
        calendars = _prevalidate_calendar(calendar_entries, dataset.manifest.calendar_version)
        _prevalidate_seed(structural_seed)
        segment_results = canonical_candidate_evidence.segment_results
        if type(segment_results) is not tuple or not segment_results:
            raise ValueError("canonical control prefix must be nonempty")
        for ordinal, result in enumerate(segment_results):
            if type(result) is not GCCandidateEvidenceSegmentResult:
                raise TypeError("canonical control segment result has an invalid type")
            if result.segment_ordinal != ordinal or ordinal >= len(dataset.segments):
                raise ValueError("canonical control ordinals must be gapless and dataset-bound")
            if dataset.segments[ordinal].segment_id != result.segment_id:
                raise ValueError("canonical control segment identity mismatch")
        frontier_ordinal = len(segment_results)
        if frontier_ordinal + 1 >= len(dataset.segments):
            return _frontier_blocked(SMCV2PrimitiveStatus.NONE, "NO_ADJACENT_CONTROL_FRONTIER")
        source = dataset.segments[frontier_ordinal]
        receiving = dataset.segments[frontier_ordinal + 1]
        if type(source) is not GCCanonicalContractSegment or type(receiving) is not GCCanonicalContractSegment:
            raise TypeError("frontier dataset segments have an invalid type")
        if source.partition is not GCSegmentPartition.DEVELOPMENT or receiving.partition is not GCSegmentPartition.DEVELOPMENT:
            raise ValueError("frontier segments must be DEVELOPMENT only")
        if source.contract != receiving.contract:
            raise ValueError("frontier segments cross a contract boundary")
        if source.preceding_missing_bar_count or receiving.preceding_missing_bar_count:
            raise ValueError("frontier segments cannot be partial")
        _hash(source.segment_id, "source segment_id")
        _hash(receiving.segment_id, "receiving segment_id")
        calendar_dates = {item.trade_date for item in calendars}
        required_dates = {
            source.first_trade_date,
            source.last_trade_date,
            receiving.first_trade_date,
            receiving.last_trade_date,
        }
        if not required_dates.issubset(calendar_dates):
            return _frontier_blocked(SMCV2PrimitiveStatus.UNKNOWN, "FRONTIER_CALENDAR_UNAVAILABLE")
        instrument = _text(dataset_config.instrument, "instrument", upper=True)
        timeframe = _text(dataset_config.timeframe, "timeframe", upper=True)
        source_base = _analyze_gc_base_segment(
            instrument=instrument,
            timeframe=timeframe,
            segment=source,
            structural_seed=structural_seed,
            config=config,
        )
        if source_base.blocked_result is not None:
            reason = source_base.blocked_result.reasons[0] if source_base.blocked_result.reasons else "SOURCE_BASE_EVIDENCE_BLOCKED"
            return _frontier_blocked(source_base.blocked_result.status, reason)
        receiving_base = _analyze_gc_base_segment(
            instrument=instrument,
            timeframe=timeframe,
            segment=receiving,
            structural_seed=structural_seed,
            config=config,
        )
        if receiving_base.blocked_result is not None:
            reason = receiving_base.blocked_result.reasons[0] if receiving_base.blocked_result.reasons else "RECEIVING_BASE_EVIDENCE_BLOCKED"
            return _frontier_blocked(receiving_base.blocked_result.status, reason)
        source_evidence = _frontier_segment_evidence(
            ordinal=frontier_ordinal,
            segment=source,
            base=source_base,
            config=config,
        )
        receiving_evidence = _frontier_segment_evidence(
            ordinal=frontier_ordinal + 1,
            segment=receiving,
            base=receiving_base,
            config=config,
        )
        source_ranges = tuple(
            item
            for item in source_evidence.dealing_range_result.ranges
            if item.kind is DealingRangeKind.EXTERNAL
        )
        source_gaps = tuple(
            item
            for item in source_evidence.fair_value_gap_result.gaps
            if item.displacement_id is not None
        )
        source_gap_ids = frozenset(item.gap_id for item in source_gaps)
        pending = analyze_inducement_pending_horizons(
            instrument=instrument,
            timeframe=timeframe,
            dealing_range_snapshots=source_ranges,
            liquidity_map_snapshots=source_evidence.liquidity_map_result.snapshots,
            equal_liquidity_pools=source_evidence.equal_liquidity_result.pools,
            structure_events=source_base.structure_events,
            fair_value_gaps=source_gaps,
            fair_value_gap_transitions=tuple(
                item
                for item in source_evidence.fair_value_gap_result.transitions
                if item.gap_id in source_gap_ids
            ),
            fair_value_gap_snapshots=tuple(
                item
                for item in source_evidence.fair_value_gap_result.snapshots
                if item.gap_id in source_gap_ids
            ),
            observations=source_base.inducement_observations,
        )
        if type(pending) is not InducementPendingHorizonResult:
            raise TypeError("pending producer returned an invalid result type")
        if pending.status is SMCV2PrimitiveStatus.NONE:
            return _frontier_blocked(SMCV2PrimitiveStatus.NONE, "NO_PENDING_CONTROL_FRONTIER")
        if pending.status in (SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.AMBIGUOUS):
            reason = pending.reasons[0] if pending.reasons else "PENDING_CONTROL_FRONTIER_BLOCKED"
            return _frontier_blocked(pending.status, reason)
        expected_reasons = ("one or more confirmation horizons are incomplete",)
        expected_blockers = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
        if (
            pending.status is not SMCV2PrimitiveStatus.UNKNOWN
            or pending.reasons != expected_reasons
            or pending.blocking_reasons != expected_blockers
        ):
            return _frontier_blocked(SMCV2PrimitiveStatus.UNKNOWN, "UNRELATED_PENDING_CONTROL_FRONTIER")
        if not pending.pending_horizons:
            raise ValueError("pending frontier must contain at least one horizon")
        for horizon in pending.pending_horizons:
            if type(horizon) is not InducementPendingHorizon:
                raise TypeError("pending horizon has an invalid type")
            available_count = len(horizon.available_confirmation_indices)
            if (
                len(horizon.available_confirmation_timestamps) != available_count
                or not 0 <= available_count < 3
                or horizon.missing_confirmation_bar_count != 3 - available_count
                or horizon.reason_token != "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
            ):
                raise ValueError("pending horizon arithmetic is invalid")
        control_digest = _sha(canonical_candidate_evidence)
        frontier_id = make_gc_candidate_frontier_evidence_id(
            identity_kind=GCCandidateFrontierIdentityKind.FRONTIER,
            instrument=instrument,
            timeframe=timeframe,
            dataset_id=dataset.dataset_id,
            seed_id=structural_seed.seed_id,
            canonical_control_digest=control_digest,
            frontier_ordinal=frontier_ordinal,
            source_segment=source_evidence,
            source_pending_result=pending,
            receiving_segment=receiving_evidence,
        )
        frontier = GCCandidateFrontierEvidence(
            frontier_id,
            GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION,
            instrument,
            timeframe,
            dataset.dataset_id,
            structural_seed.seed_id,
            control_digest,
            frontier_ordinal,
            source_evidence,
            pending,
            receiving_evidence,
        )
    except (TypeError, ValueError, IndexError):
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_CONTROL_FRONTIER_EVIDENCE")
    except Exception:
        return _frontier_blocked(SMCV2PrimitiveStatus.INVALID, "CONTROL_FRONTIER_VALIDATION_EXCEPTION")
    return GCCandidateFrontierEvidenceResult(
        SMCV2PrimitiveStatus.VALID,
        frontier,
        ("CONTROL_FRONTIER_CONTINUATION_EVIDENCE_COMPLETE",),
    )


__all__ = (
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
