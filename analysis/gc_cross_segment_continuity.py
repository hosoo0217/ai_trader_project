"""Deterministic GC cross-segment continuity feasibility diagnostics.

This module is deliberately offline and reference-only.  It never reads files,
uses network services, exposes OOS bars, constructs candidates/features/labels,
or grants strategy, risk, or execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from analysis.gc_candidate_evidence_builder import (
    GCCandidateEvidenceConfig,
    GCCandidateEvidenceResult,
    GCCandidateEvidenceSegmentResult,
    GCCandidateFrontierEvidenceResult,
    GCCandidateFrontierSegmentEvidence,
    analyze_gc_candidate_frontier_evidence,
    build_gc_candidate_evidence,
)
from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetSessionInterval,
    GCSegmentPartition,
    GCSplitSessionCalendarEntry,
    make_gc_dataset_id,
)
from analysis.gc_structural_seed_evidence import GCCanonicalSeedEvidence
from core.gc_chronological_backtest import GCChronologicalBar
from smc.dealing_range import (
    DealingRangeResult,
    DealingRangeSnapshot,
    DealingRangeState,
    DealingRangeStructureEvent,
)
from smc.equal_liquidity import EqualLiquidityPool, EqualLiquidityResult
from smc.fair_value_gap import (
    FairValueGap,
    FairValueGapResult,
    FairValueGapSnapshot,
    FairValueGapTransition,
)
from smc.inducement import InducementResult
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneResult,
    KillZoneSessionStatus,
)
from smc.liquidity_map import LiquidityMapResult, LiquidityMapSnapshot
from smc.smc_v2_primitives import (
    SMCV2LifecycleState,
    SMCV2PrimitiveStatus,
    normalize_utc_timestamp,
)


GC_CROSS_SEGMENT_CONTINUITY_VERSION = "GC-CROSS-SEGMENT-CONTINUITY-V1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_UTC = timezone.utc
_FIVE_MINUTES = timedelta(minutes=5)
_STANDARD_SESSION = timedelta(hours=23)
_DETECTOR_ORDER = {"EQUAL_LIQUIDITY": 0, "DEALING_RANGE": 1, "LIQUIDITY_MAP": 2}
_LEGACY_V3_SEGMENT_IDENTITY_VERSION = "GC-DATASET-BUILDER-V3-SPLIT-SESSION"
_SUPPORTED_SEGMENT_IDENTITY_VERSIONS = (
    _LEGACY_V3_SEGMENT_IDENTITY_VERSION,
    GC_DATASET_BUILDER_VERSION,
)


class GCCrossSegmentContinuityIdentityKind(str, Enum):
    BOUNDARY = "BOUNDARY"
    RECEIVING_GROUP = "RECEIVING_GROUP"
    MANIFEST = "MANIFEST"


class GCCrossSegmentContinuityDecision(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


@dataclass(frozen=True)
class GCContinuityDependencyReference:
    detector_name: str
    object_kind: str
    object_id: str
    owning_segment_ordinal: int
    owning_segment_id: str
    first_known_index: int
    first_known_timestamp: datetime
    effective_index: int
    effective_timestamp: datetime
    state: str
    history_ids: tuple[str, ...]
    source_moment_digest: str
    object_digest: str


@dataclass(frozen=True)
class GCContinuityReceivingReference:
    detector_name: str
    object_kind: str
    object_id: str
    owning_segment_ordinal: int
    owning_segment_id: str
    first_known_index: int
    first_known_timestamp: datetime
    effective_index: int
    effective_timestamp: datetime
    semantic_discriminator: str
    history_ids: tuple[str, ...]
    source_moment_digest: str
    object_digest: str


@dataclass(frozen=True)
class GCCrossSegmentBoundary:
    boundary_id: str
    source_segment_ordinal: int
    source_segment_id: str
    receiving_segment_ordinal: int
    receiving_segment_id: str
    contract: str
    source_trade_date: date
    receiving_trade_date: date
    source_end_timestamp: datetime
    receiving_start_timestamp: datetime
    decision: GCCrossSegmentContinuityDecision
    reason_tokens: tuple[str, ...]
    dependency_references: tuple[GCContinuityDependencyReference, ...]


@dataclass(frozen=True)
class GCContinuityReceivingGroup:
    group_id: str
    boundary_id: str
    receiving_segment_ordinal: int
    receiving_segment_id: str
    effective_index: int
    effective_timestamp: datetime
    references: tuple[GCContinuityReceivingReference, ...]


@dataclass(frozen=True)
class GCCrossSegmentContinuityManifest:
    manifest_id: str
    version: str
    instrument: str
    timeframe: str
    dataset_id: str
    calendar_version: str
    boundary_calendar_digest: str
    candidate_calendar_digest: str
    timezone_data_version: str
    seed_id: str
    canonical_control_digest: str
    boundary_ids: tuple[str, ...]
    receiving_group_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCCrossSegmentContinuityResult:
    status: SMCV2PrimitiveStatus
    boundaries: tuple[GCCrossSegmentBoundary, ...] = ()
    receiving_groups: tuple[GCContinuityReceivingGroup, ...] = ()
    manifest: GCCrossSegmentContinuityManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


def _text(value: object, name: str, *, upper: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized.upper() if upper else normalized


def _hash(value: object, name: str) -> str:
    normalized = _text(value, name)
    if _HASH.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return normalized


def _integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _timestamp(value: object, name: str) -> datetime:
    try:
        return normalize_utc_timestamp(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError(f"malformed {name}") from exc


def _date(value: object, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be a date")
    return value


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
    if type(value) is date:
        return value.isoformat()
    if isinstance(value, Decimal):
        return _decimal_text(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) is list:
        return [_canonical(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("canonical keys must be strings")
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def _sha(value: object) -> str:
    encoded = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _hash_tuple(value: object, name: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    if nonempty and not value:
        raise ValueError(f"{name} cannot be empty")
    normalized = tuple(_hash(item, f"{name} member") for item in value)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} cannot contain duplicates")
    return normalized


def _validate_dependency_reference(value: object) -> GCContinuityDependencyReference:
    if type(value) is not GCContinuityDependencyReference:
        raise TypeError("dependency reference has an invalid type")
    detector = _text(value.detector_name, "detector_name", upper=True)
    if detector not in _DETECTOR_ORDER:
        raise ValueError("unknown dependency detector")
    _text(value.object_kind, "object_kind", upper=True)
    _hash(value.object_id, "object_id")
    _integer(value.owning_segment_ordinal, "owning_segment_ordinal")
    _hash(value.owning_segment_id, "owning_segment_id")
    first_index = _integer(value.first_known_index, "first_known_index")
    effective_index = _integer(value.effective_index, "effective_index")
    first_timestamp = _timestamp(value.first_known_timestamp, "first_known_timestamp")
    effective_timestamp = _timestamp(value.effective_timestamp, "effective_timestamp")
    if (effective_index, effective_timestamp) < (first_index, first_timestamp):
        raise ValueError("effective moment precedes first-known moment")
    _text(value.state, "state", upper=True)
    _hash_tuple(value.history_ids, "history_ids")
    _hash(value.source_moment_digest, "source_moment_digest")
    _hash(value.object_digest, "object_digest")
    return value


def _validate_receiving_reference(value: object) -> GCContinuityReceivingReference:
    if type(value) is not GCContinuityReceivingReference:
        raise TypeError("receiving reference has an invalid type")
    detector = _text(value.detector_name, "detector_name", upper=True)
    if detector not in {"DEALING_RANGE", "FAIR_VALUE_GAP"}:
        raise ValueError("unknown receiving detector")
    _text(value.object_kind, "object_kind", upper=True)
    _hash(value.object_id, "object_id")
    _integer(value.owning_segment_ordinal, "owning_segment_ordinal")
    _hash(value.owning_segment_id, "owning_segment_id")
    first_index = _integer(value.first_known_index, "first_known_index")
    effective_index = _integer(value.effective_index, "effective_index")
    first_timestamp = _timestamp(value.first_known_timestamp, "first_known_timestamp")
    effective_timestamp = _timestamp(value.effective_timestamp, "effective_timestamp")
    if (effective_index, effective_timestamp) < (first_index, first_timestamp):
        raise ValueError("effective moment precedes first-known moment")
    _text(value.semantic_discriminator, "semantic_discriminator", upper=True)
    _hash_tuple(value.history_ids, "history_ids")
    _hash(value.source_moment_digest, "source_moment_digest")
    _hash(value.object_digest, "object_digest")
    return value


def _forbidden(value: object, default: object, name: str) -> None:
    if value != default:
        raise ValueError(f"{name} is forbidden for this identity kind")


def make_gc_cross_segment_continuity_id(
    *,
    identity_kind: GCCrossSegmentContinuityIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    boundary_calendar_digest: str,
    candidate_calendar_digest: str,
    timezone_data_version: str,
    seed_id: str,
    canonical_control_digest: str,
    source_segment_ordinal: int | None = None,
    source_segment_id: str | None = None,
    receiving_segment_ordinal: int | None = None,
    receiving_segment_id: str | None = None,
    contract: str | None = None,
    source_trade_date: date | None = None,
    receiving_trade_date: date | None = None,
    source_end_timestamp: datetime | None = None,
    receiving_start_timestamp: datetime | None = None,
    decision: GCCrossSegmentContinuityDecision | None = None,
    reason_tokens: tuple[str, ...] = (),
    dependency_references: tuple[GCContinuityDependencyReference, ...] = (),
    boundary_id: str | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    receiving_references: tuple[GCContinuityReceivingReference, ...] = (),
    boundary_ids: tuple[str, ...] = (),
    receiving_group_ids: tuple[str, ...] = (),
) -> str:
    """Return one exact kind-specific continuity identity."""

    try:
        if type(identity_kind) is not GCCrossSegmentContinuityIdentityKind:
            raise TypeError("identity_kind must be GCCrossSegmentContinuityIdentityKind")
        common: dict[str, object] = {
            "version": GC_CROSS_SEGMENT_CONTINUITY_VERSION,
            "identity_kind": identity_kind.value,
            "instrument": _text(instrument, "instrument", upper=True),
            "timeframe": _text(timeframe, "timeframe", upper=True),
            "dataset_id": _hash(dataset_id, "dataset_id"),
            "calendar_version": _text(calendar_version, "calendar_version"),
            "boundary_calendar_digest": _hash(boundary_calendar_digest, "boundary_calendar_digest"),
            "candidate_calendar_digest": _hash(candidate_calendar_digest, "candidate_calendar_digest"),
            "timezone_data_version": _text(timezone_data_version, "timezone_data_version"),
            "seed_id": _hash(seed_id, "seed_id"),
            "canonical_control_digest": _hash(canonical_control_digest, "canonical_control_digest"),
        }
        if identity_kind is GCCrossSegmentContinuityIdentityKind.BOUNDARY:
            _forbidden(boundary_id, None, "boundary_id")
            _forbidden(effective_index, None, "effective_index")
            _forbidden(effective_timestamp, None, "effective_timestamp")
            _forbidden(receiving_references, (), "receiving_references")
            _forbidden(boundary_ids, (), "boundary_ids")
            _forbidden(receiving_group_ids, (), "receiving_group_ids")
            if type(decision) is not GCCrossSegmentContinuityDecision:
                raise TypeError("decision must be GCCrossSegmentContinuityDecision")
            if type(reason_tokens) is not tuple:
                raise TypeError("reason_tokens must be a tuple")
            reasons = tuple(_text(item, "reason token", upper=True) for item in reason_tokens)
            if not reasons or len(set(reasons)) != len(reasons):
                raise ValueError("reason_tokens must be nonempty and unique")
            if type(dependency_references) is not tuple:
                raise TypeError("dependency_references must be a tuple")
            references = tuple(_validate_dependency_reference(item) for item in dependency_references)
            expected_order = tuple(sorted(references, key=lambda item: (_DETECTOR_ORDER[item.detector_name], dependency_references.index(item))))
            if references != expected_order:
                raise ValueError("dependency_references are not in canonical detector order")
            payload = {
                **common,
                "source_segment_ordinal": _integer(source_segment_ordinal, "source_segment_ordinal"),
                "source_segment_id": _hash(source_segment_id, "source_segment_id"),
                "receiving_segment_ordinal": _integer(receiving_segment_ordinal, "receiving_segment_ordinal"),
                "receiving_segment_id": _hash(receiving_segment_id, "receiving_segment_id"),
                "contract": _text(contract, "contract", upper=True),
                "source_trade_date": _date(source_trade_date, "source_trade_date"),
                "receiving_trade_date": _date(receiving_trade_date, "receiving_trade_date"),
                "source_end_timestamp": _timestamp(source_end_timestamp, "source_end_timestamp"),
                "receiving_start_timestamp": _timestamp(receiving_start_timestamp, "receiving_start_timestamp"),
                "decision": decision.value,
                "reason_tokens": reasons,
                "dependency_references": references,
            }
        elif identity_kind is GCCrossSegmentContinuityIdentityKind.RECEIVING_GROUP:
            for name, value, default in (
                ("source_segment_ordinal", source_segment_ordinal, None),
                ("source_segment_id", source_segment_id, None),
                ("contract", contract, None),
                ("source_trade_date", source_trade_date, None),
                ("receiving_trade_date", receiving_trade_date, None),
                ("source_end_timestamp", source_end_timestamp, None),
                ("receiving_start_timestamp", receiving_start_timestamp, None),
                ("decision", decision, None),
                ("reason_tokens", reason_tokens, ()),
                ("dependency_references", dependency_references, ()),
                ("boundary_ids", boundary_ids, ()),
                ("receiving_group_ids", receiving_group_ids, ()),
            ):
                _forbidden(value, default, name)
            if type(receiving_references) is not tuple or not receiving_references:
                raise ValueError("receiving_references must be a nonempty tuple")
            references = tuple(_validate_receiving_reference(item) for item in receiving_references)
            if len({(item.detector_name, item.object_id) for item in references}) != len(references):
                raise ValueError("receiving_references contain duplicates")
            payload = {
                **common,
                "boundary_id": _hash(boundary_id, "boundary_id"),
                "receiving_segment_ordinal": _integer(receiving_segment_ordinal, "receiving_segment_ordinal"),
                "receiving_segment_id": _hash(receiving_segment_id, "receiving_segment_id"),
                "effective_index": _integer(effective_index, "effective_index"),
                "effective_timestamp": _timestamp(effective_timestamp, "effective_timestamp"),
                "receiving_references": references,
            }
            if any(
                (item.owning_segment_ordinal, item.owning_segment_id, item.effective_index, _timestamp(item.effective_timestamp, "effective_timestamp"))
                != (payload["receiving_segment_ordinal"], payload["receiving_segment_id"], payload["effective_index"], payload["effective_timestamp"])
                for item in references
            ):
                raise ValueError("receiving references do not reconcile to the group")
        else:
            for name, value, default in (
                ("source_segment_ordinal", source_segment_ordinal, None),
                ("source_segment_id", source_segment_id, None),
                ("receiving_segment_ordinal", receiving_segment_ordinal, None),
                ("receiving_segment_id", receiving_segment_id, None),
                ("contract", contract, None),
                ("source_trade_date", source_trade_date, None),
                ("receiving_trade_date", receiving_trade_date, None),
                ("source_end_timestamp", source_end_timestamp, None),
                ("receiving_start_timestamp", receiving_start_timestamp, None),
                ("decision", decision, None),
                ("reason_tokens", reason_tokens, ()),
                ("dependency_references", dependency_references, ()),
                ("boundary_id", boundary_id, None),
                ("effective_index", effective_index, None),
                ("effective_timestamp", effective_timestamp, None),
                ("receiving_references", receiving_references, ()),
            ):
                _forbidden(value, default, name)
            payload = {
                **common,
                "boundary_ids": _hash_tuple(boundary_ids, "boundary_ids"),
                "receiving_group_ids": _hash_tuple(receiving_group_ids, "receiving_group_ids"),
            }
        return _sha(payload)
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError("malformed continuity identity evidence") from exc


def _blocked(
    status: SMCV2PrimitiveStatus,
    reason: str,
    boundaries: tuple[GCCrossSegmentBoundary, ...] = (),
    groups: tuple[GCContinuityReceivingGroup, ...] = (),
    *,
    manifest: GCCrossSegmentContinuityManifest | None = None,
) -> GCCrossSegmentContinuityResult:
    blocking = (reason,) if status in {
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    } else ()
    return GCCrossSegmentContinuityResult(status, boundaries, groups, manifest, (reason,), blocking)


def _validate_bar(value: object, prior: tuple[int, datetime] | None) -> tuple[int, datetime]:
    if type(value) is not GCChronologicalBar:
        raise TypeError("segment bar has an invalid type")
    index = _integer(value.index, "bar index")
    timestamp = _timestamp(value.timestamp, "bar timestamp")
    for name in ("open_tick", "high_tick", "low_tick", "close_tick", "volume"):
        if type(getattr(value, name)) is not int:
            raise TypeError(f"bar {name} must be an integer")
    if not value.is_closed or value.volume < 0:
        raise ValueError("segment bars must be fully closed with nonnegative volume")
    if not (value.low_tick <= value.open_tick <= value.high_tick and value.low_tick <= value.close_tick <= value.high_tick):
        raise ValueError("bar geometry is invalid")
    moment = (index, timestamp)
    if prior is not None and moment <= prior:
        raise ValueError("segment bars are not strictly chronological")
    return moment


def _bar_digest(bars: tuple[GCChronologicalBar, ...]) -> str:
    return _sha(
        tuple(
            {
                "index": bar.index,
                "timestamp": _timestamp(bar.timestamp, "bar timestamp"),
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


def _legacy_v3_segment_id(
    *,
    config: GCDatasetBuildConfig,
    contract: str,
    partition: GCSegmentPartition,
    first_trade_date: date,
    last_trade_date: date,
    source_ids: tuple[str, ...],
    bar_digest: str,
    preceding_missing_bar_count: int,
) -> str:
    config_payload = {
        "instrument": _text(config.instrument, "config instrument", upper=True),
        "timeframe": _text(config.timeframe, "config timeframe", upper=True),
        "source_timezone": _text(config.source_timezone, "config source_timezone"),
        "exchange_timezone": _text(config.exchange_timezone, "config exchange_timezone"),
        "timezone_data_version": _text(
            config.timezone_data_version,
            "config timezone_data_version",
        ),
        "tick_size": _decimal_text(config.tick_size),
        "initial_contract": _text(
            config.initial_contract,
            "config initial_contract",
            upper=True,
        ),
        "initial_trade_date": _date(
            config.initial_trade_date,
            "config initial_trade_date",
        ).isoformat(),
        "roll_confirmation_sessions": _integer(
            config.roll_confirmation_sessions,
            "config roll_confirmation_sessions",
        ),
        "oos_start_trade_date": _date(
            config.oos_start_trade_date,
            "config oos_start_trade_date",
        ).isoformat(),
        "oos_end_trade_date": _date(
            config.oos_end_trade_date,
            "config oos_end_trade_date",
        ).isoformat(),
    }
    payload = {
        "version": _LEGACY_V3_SEGMENT_IDENTITY_VERSION,
        "identity_kind": "SEGMENT",
        "config": config_payload,
        "contract": _text(contract, "segment contract", upper=True),
        "partition": partition.value,
        "first_trade_date": _date(
            first_trade_date,
            "segment first_trade_date",
        ).isoformat(),
        "last_trade_date": _date(
            last_trade_date,
            "segment last_trade_date",
        ).isoformat(),
        "source_ids": source_ids,
        "bar_digest": _hash(bar_digest, "segment bar_digest"),
        "preceding_missing_bar_count": _integer(
            preceding_missing_bar_count,
            "segment preceding_missing_bar_count",
        ),
    }
    return _sha(payload)


def _validate_segment(
    value: object,
    ordinal: int,
    config: GCDatasetBuildConfig,
    identity_version: str,
) -> GCCanonicalContractSegment:
    if type(value) is not GCCanonicalContractSegment:
        raise TypeError("segment has an invalid type")
    _hash(value.segment_id, "segment_id")
    _text(value.contract, "contract", upper=True)
    if type(value.partition) is not GCSegmentPartition:
        raise TypeError("segment partition has an invalid type")
    _date(value.first_trade_date, "first_trade_date")
    _date(value.last_trade_date, "last_trade_date")
    if value.first_trade_date > value.last_trade_date:
        raise ValueError("segment trade-date range is inverted")
    source_ids = _hash_tuple(value.source_ids, "source_ids", nonempty=True)
    if type(value.bars) is not tuple or not value.bars:
        raise ValueError("segment bars must be a nonempty tuple")
    prior: tuple[int, datetime] | None = None
    for position, bar in enumerate(value.bars):
        prior = _validate_bar(bar, prior)
        if bar.index != position:
            raise ValueError("segment bar indices must start at zero and be contiguous")
    missing = _integer(value.preceding_missing_bar_count, "preceding_missing_bar_count")
    bar_digest = _bar_digest(value.bars)
    current_expected = make_gc_dataset_id(
        identity_kind="SEGMENT",
        config=config,
        contract=value.contract,
        partition=value.partition,
        first_trade_date=value.first_trade_date,
        last_trade_date=value.last_trade_date,
        source_ids=source_ids,
        bar_digest=bar_digest,
        preceding_missing_bar_count=missing,
    )
    if identity_version == _LEGACY_V3_SEGMENT_IDENTITY_VERSION:
        expected = _legacy_v3_segment_id(
            config=config,
            contract=value.contract,
            partition=value.partition,
            first_trade_date=value.first_trade_date,
            last_trade_date=value.last_trade_date,
            source_ids=source_ids,
            bar_digest=bar_digest,
            preceding_missing_bar_count=missing,
        )
    elif identity_version == GC_DATASET_BUILDER_VERSION:
        expected = current_expected
    else:  # pragma: no cover - guarded once per dataset
        raise ValueError("unsupported segment identity version")
    if value.segment_id != expected:
        raise ValueError(f"segment {ordinal} identity mismatch")
    return value


def _validate_boundary_calendar(value: object, expected_version: str) -> tuple[GCSplitSessionCalendarEntry, ...]:
    if type(value) is not tuple:
        raise TypeError("boundary_calendar_entries must be a tuple")
    previous: date | None = None
    for entry in value:
        if type(entry) is not GCSplitSessionCalendarEntry:
            raise TypeError("boundary calendar entry has an invalid type")
        if _text(entry.calendar_version, "calendar_version") != expected_version:
            raise ValueError("boundary calendar version mismatch")
        trade_date = _date(entry.trade_date, "trade_date")
        if previous is not None and trade_date <= previous:
            raise ValueError("boundary calendar must be strictly ordered")
        previous = trade_date
        if type(entry.intervals) is not tuple:
            raise TypeError("calendar intervals must be a tuple")
        prior_end: datetime | None = None
        for interval in entry.intervals:
            if type(interval) is not GCDatasetSessionInterval:
                raise TypeError("calendar interval has an invalid type")
            start = _timestamp(interval.start_timestamp, "interval start")
            end = _timestamp(interval.end_timestamp, "interval end")
            if start >= end or (prior_end is not None and start < prior_end):
                raise ValueError("calendar intervals overlap or are inverted")
            prior_end = end
        ids = _hash_tuple(entry.source_artifact_ids, "source_artifact_ids", nonempty=True)
        hashes = _hash_tuple(entry.source_artifact_sha256s, "source_artifact_sha256s", nonempty=True)
        if len(ids) != len(hashes):
            raise ValueError("calendar artifact provenance lengths differ")
    return value


def _validate_candidate_calendar(value: object, expected_version: str) -> tuple[KillZoneCalendarEntry, ...]:
    if type(value) is not tuple:
        raise TypeError("candidate_calendar_entries must be a tuple")
    previous: date | None = None
    for entry in value:
        if type(entry) is not KillZoneCalendarEntry:
            raise TypeError("candidate calendar entry has an invalid type")
        if _text(entry.calendar_version, "calendar_version") != expected_version:
            raise ValueError("candidate calendar version mismatch")
        trade_date = _date(entry.trade_date, "trade_date")
        if previous is not None and trade_date <= previous:
            raise ValueError("candidate calendar must be strictly ordered")
        previous = trade_date
        if type(entry.session_status) is not KillZoneSessionStatus:
            raise TypeError("candidate calendar status has an invalid type")
        if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
            if entry.session_open_timestamp is not None or entry.session_close_timestamp is not None:
                raise ValueError("closed candidate calendar entry carries bounds")
        else:
            opening = _timestamp(entry.session_open_timestamp, "session_open_timestamp")
            closing = _timestamp(entry.session_close_timestamp, "session_close_timestamp")
            if opening >= closing:
                raise ValueError("candidate calendar session bounds are inverted")
    return value


def _validate_result_shape(value: object) -> GCCandidateEvidenceResult:
    if type(value) is not GCCandidateEvidenceResult:
        raise TypeError("canonical_candidate_evidence has an invalid type")
    if type(value.status) is not SMCV2PrimitiveStatus:
        raise TypeError("canonical candidate status has an invalid type")
    for name in ("candidates", "segment_results", "reasons", "blocking_reasons"):
        if type(getattr(value, name)) is not tuple:
            raise TypeError(f"canonical candidate {name} must be a tuple")
    prior = -1
    seen: set[str] = set()
    for segment in value.segment_results:
        if type(segment) is not GCCandidateEvidenceSegmentResult:
            raise TypeError("candidate segment result has an invalid type")
        ordinal = _integer(segment.segment_ordinal, "candidate segment ordinal")
        segment_id = _hash(segment.segment_id, "candidate segment_id")
        if ordinal <= prior or segment_id in seen:
            raise ValueError("candidate segment results are reordered or duplicated")
        prior = ordinal
        seen.add(segment_id)
        if type(segment.result_ids) is not tuple or len(segment.result_ids) != 6:
            raise ValueError("candidate segment must bind six result IDs")
        _hash_tuple(segment.result_ids, "result_ids", nonempty=True)
        for result, expected in (
            (segment.equal_liquidity_result, EqualLiquidityResult),
            (segment.dealing_range_result, DealingRangeResult),
            (segment.liquidity_map_result, LiquidityMapResult),
            (segment.fair_value_gap_result, FairValueGapResult),
            (segment.inducement_result, InducementResult),
            (segment.kill_zone_result, KillZoneResult),
        ):
            if type(result) is not expected or type(result.status) is not SMCV2PrimitiveStatus:
                raise TypeError("candidate detector result has an invalid type")
    if value.status is SMCV2PrimitiveStatus.VALID and value.manifest is None:
        raise ValueError("VALID canonical candidate control requires a manifest")
    if value.manifest is not None:
        _hash(value.manifest.manifest_id, "candidate manifest_id")
        _hash(value.manifest.bundle_id, "candidate bundle_id")
    return value


def _validate_dataset(value: object, config: GCDatasetBuildConfig) -> GCDatasetBuildResult:
    if type(value) is not GCDatasetBuildResult:
        raise TypeError("dataset has an invalid type")
    if type(value.status) is not GCDatasetBuildStatus:
        raise TypeError("dataset status has an invalid type")
    if type(value.segments) is not tuple or type(value.reasons) is not tuple or type(value.blocking_reasons) is not tuple:
        raise TypeError("dataset collections must be tuples")
    if value.status is not GCDatasetBuildStatus.VALID:
        return value
    if value.manifest is None or value.dataset_id is None:
        raise ValueError("VALID dataset requires identity and manifest")
    dataset_id = _hash(value.dataset_id, "dataset_id")
    if _hash(value.manifest.dataset_id, "manifest dataset_id") != dataset_id:
        raise ValueError("dataset identity mismatch")
    identity_version = value.manifest.version
    if (
        type(identity_version) is not str
        or identity_version not in _SUPPORTED_SEGMENT_IDENTITY_VERSIONS
    ):
        raise ValueError("unsupported dataset segment identity version")
    if value.manifest.oos_bar_count != 0:
        raise ValueError("OOS exposure is forbidden")
    if value.manifest.calendar_version.strip() == "" or value.manifest.timezone_data_version != config.timezone_data_version:
        raise ValueError("dataset version binding mismatch")
    if type(value.manifest.segment_ids) is not tuple or value.manifest.segment_ids != tuple(item.segment_id for item in value.segments):
        raise ValueError("manifest segment order mismatch")
    for ordinal, segment in enumerate(value.segments):
        _validate_segment(segment, ordinal, config, identity_version)
        if segment.partition is not GCSegmentPartition.DEVELOPMENT:
            raise ValueError("OOS segment exposure is forbidden")
    return value


def _bar_for_moment(segment: GCCanonicalContractSegment, index: int, timestamp: datetime) -> GCChronologicalBar:
    normalized = _timestamp(timestamp, "source timestamp")
    matches = tuple(bar for bar in segment.bars if bar.index == index and _timestamp(bar.timestamp, "bar timestamp") == normalized)
    if len(matches) != 1:
        raise ValueError("source moment does not resolve exactly once")
    return matches[0]


def _source_digest(segment: GCCanonicalContractSegment, indices: tuple[int, ...], timestamps: tuple[datetime, ...]) -> str:
    if type(indices) is not tuple or type(timestamps) is not tuple or len(indices) != len(timestamps) or not indices:
        raise ValueError("source provenance is incomplete")
    bars = tuple(_bar_for_moment(segment, index, timestamp) for index, timestamp in zip(indices, timestamps, strict=True))
    return _sha({"indices": indices, "timestamps": timestamps, "bars": bars})


def _dependency_references(
    segment_result: GCCandidateEvidenceSegmentResult | GCCandidateFrontierSegmentEvidence,
    segment: GCCanonicalContractSegment,
) -> tuple[GCContinuityDependencyReference, ...]:
    references: list[GCContinuityDependencyReference] = []
    for pool in segment_result.equal_liquidity_result.pools:
        if type(pool) is not EqualLiquidityPool:
            raise TypeError("equal-liquidity pool has an invalid type")
        if pool.lifecycle_state is not SMCV2LifecycleState.ACTIVE:
            continue
        provenance = pool.first_known_provenance
        source_digest = _source_digest(segment, provenance.source_indices, provenance.source_timestamps)
        effective_index = provenance.confirmation_index
        effective_timestamp = provenance.confirmation_timestamp
        history_ids = tuple(_sha(event) for event in pool.lifecycle_events)
        if pool.lifecycle_events:
            effective_index = pool.lifecycle_events[-1].index
            effective_timestamp = pool.lifecycle_events[-1].timestamp
        references.append(
            GCContinuityDependencyReference(
                "EQUAL_LIQUIDITY", "POOL", pool.snapshot_id,
                segment_result.segment_ordinal, segment.segment_id,
                provenance.confirmation_index, _timestamp(provenance.confirmation_timestamp, "first-known timestamp"),
                effective_index, _timestamp(effective_timestamp, "effective timestamp"),
                pool.lifecycle_state.value, history_ids, source_digest, _sha(pool),
            )
        )
    for snapshot in segment_result.dealing_range_result.ranges:
        if type(snapshot) is not DealingRangeSnapshot:
            raise TypeError("dealing-range snapshot has an invalid type")
        if snapshot.state is not DealingRangeState.ACTIVE:
            continue
        provenance = snapshot.first_known_provenance
        source_digest = _source_digest(segment, provenance.source_indices, provenance.source_timestamps)
        effective_index = provenance.confirmation_index
        effective_timestamp = _timestamp(
            provenance.confirmation_timestamp,
            "first-known timestamp",
        )
        if snapshot.transitions:
            transition = snapshot.transitions[-1]
            transition_timestamp = _timestamp(
                transition.timestamp,
                "transition timestamp",
            )
            if (transition.index, transition_timestamp) > (
                effective_index,
                effective_timestamp,
            ):
                effective_index = transition.index
                effective_timestamp = transition_timestamp
        if snapshot.transition_ids != tuple(item.transition_id for item in snapshot.transitions):
            raise ValueError("dealing-range transition history mismatch")
        references.append(
            GCContinuityDependencyReference(
                "DEALING_RANGE", "RANGE", snapshot.snapshot_id,
                segment_result.segment_ordinal, segment.segment_id,
                provenance.confirmation_index, _timestamp(provenance.confirmation_timestamp, "first-known timestamp"),
                effective_index, effective_timestamp,
                snapshot.state.value, snapshot.transition_ids, source_digest, _sha(snapshot),
            )
        )
    active_ranges = tuple(item for item in segment_result.dealing_range_result.ranges if item.state is DealingRangeState.ACTIVE)
    if (references or active_ranges) and not segment_result.liquidity_map_result.snapshots:
        raise ValueError("active dependency closure requires a liquidity-map snapshot")
    if segment_result.liquidity_map_result.snapshots:
        latest = segment_result.liquidity_map_result.snapshots[-1]
        if type(latest) is not LiquidityMapSnapshot:
            raise TypeError("liquidity-map snapshot has an invalid type")
        _bar_for_moment(segment, latest.index, latest.timestamp)
        if latest.classification_ids != tuple(item.classification_id for item in latest.classifications):
            raise ValueError("liquidity classification history mismatch")
        if latest.reclassification_ids != tuple(item.reclassification_id for item in latest.reclassifications):
            raise ValueError("liquidity reclassification history mismatch")
        references.append(
            GCContinuityDependencyReference(
                "LIQUIDITY_MAP", "MAP", latest.snapshot_id,
                segment_result.segment_ordinal, segment.segment_id,
                latest.index, _timestamp(latest.timestamp, "map timestamp"),
                latest.index, _timestamp(latest.timestamp, "map timestamp"),
                "ACTIVE", latest.classification_ids + latest.reclassification_ids,
                _sha({"index": latest.index, "timestamp": latest.timestamp, "bar": _bar_for_moment(segment, latest.index, latest.timestamp)}),
                _sha(latest),
            )
        )
    return tuple(references)


def _calendar_by_date(entries: tuple[object, ...]) -> dict[date, object]:
    return {getattr(item, "trade_date"): item for item in entries}


def _boundary_decision(
    source: GCCanonicalContractSegment,
    receiving: GCCanonicalContractSegment,
    boundary_entries: tuple[GCSplitSessionCalendarEntry, ...],
    candidate_entries: tuple[KillZoneCalendarEntry, ...],
) -> tuple[GCCrossSegmentContinuityDecision, tuple[str, ...]]:
    if source.partition is not GCSegmentPartition.DEVELOPMENT or receiving.partition is not GCSegmentPartition.DEVELOPMENT:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("PARTITION_BOUNDARY",)
    if source.contract != receiving.contract:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("CONTRACT_BOUNDARY",)
    if source.preceding_missing_bar_count or receiving.preceding_missing_bar_count:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("PARTIAL_SEGMENT_BOUNDARY",)
    split = _calendar_by_date(boundary_entries)
    control = _calendar_by_date(candidate_entries)
    source_entry = split.get(source.last_trade_date)
    receiver_entry = split.get(receiving.first_trade_date)
    source_control = control.get(source.last_trade_date)
    receiver_control = control.get(receiving.first_trade_date)
    if None in (source_entry, receiver_entry, source_control, receiver_control):
        raise LookupError("boundary calendar coverage unavailable")
    assert isinstance(source_entry, GCSplitSessionCalendarEntry)
    assert isinstance(receiver_entry, GCSplitSessionCalendarEntry)
    assert isinstance(source_control, KillZoneCalendarEntry)
    assert isinstance(receiver_control, KillZoneCalendarEntry)
    if source_control.session_status is KillZoneSessionStatus.SESSION_CLOSED or receiver_control.session_status is KillZoneSessionStatus.SESSION_CLOSED:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("SESSION_CLOSED",)
    if len(source_entry.intervals) != 1 or len(receiver_entry.intervals) != 1:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("SPLIT_SESSION",)
    source_interval = source_entry.intervals[0]
    receiver_interval = receiver_entry.intervals[0]
    source_open = _timestamp(source_interval.start_timestamp, "source interval open")
    source_close = _timestamp(source_interval.end_timestamp, "source interval close")
    receiver_open = _timestamp(receiver_interval.start_timestamp, "receiving interval open")
    receiver_close = _timestamp(receiver_interval.end_timestamp, "receiving interval close")
    if source_control.session_open_timestamp is None or source_control.session_close_timestamp is None or receiver_control.session_open_timestamp is None or receiver_control.session_close_timestamp is None:
        raise ValueError("calendar streams contradict")
    if (
        _timestamp(source_control.session_open_timestamp, "control open") != source_open
        or _timestamp(source_control.session_close_timestamp, "control close") != source_close
        or _timestamp(receiver_control.session_open_timestamp, "control open") != receiver_open
        or _timestamp(receiver_control.session_close_timestamp, "control close") != receiver_close
    ):
        raise ValueError("calendar streams contradict")
    if source_control.session_status is KillZoneSessionStatus.EARLY_CLOSE or receiver_control.session_status is KillZoneSessionStatus.EARLY_CLOSE:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("EARLY_CLOSE",)
    if source_close - source_open != _STANDARD_SESSION or receiver_close - receiver_open != _STANDARD_SESSION:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("NONSTANDARD_SESSION",)
    if _timestamp(source.bars[-1].timestamp, "source end") != source_close:
        raise ValueError("source close does not reconcile to the calendar")
    if _timestamp(receiving.bars[0].timestamp, "receiving start") != receiver_open + _FIVE_MINUTES:
        raise ValueError("receiving first bar does not reconcile to the calendar")
    open_dates = tuple(item.trade_date for item in boundary_entries if item.intervals and item.trade_date > source.last_trade_date)
    if not open_dates or open_dates[0] != receiving.first_trade_date:
        return GCCrossSegmentContinuityDecision.INELIGIBLE, ("NONADJACENT_TRADE_DATE",)
    return GCCrossSegmentContinuityDecision.ELIGIBLE, ("ELIGIBLE_STANDARD_BOUNDARY",)


def _receiving_groups(
    *,
    boundary: GCCrossSegmentBoundary,
    segment: GCCanonicalContractSegment,
    segment_result: GCCandidateEvidenceSegmentResult | GCCandidateFrontierSegmentEvidence,
    events: tuple[DealingRangeStructureEvent, ...],
    common: dict[str, object],
) -> tuple[GCContinuityReceivingGroup, ...]:
    gaps = segment_result.fair_value_gap_result.gaps
    transitions = segment_result.fair_value_gap_result.transitions
    snapshots = segment_result.fair_value_gap_result.snapshots
    groups: list[GCContinuityReceivingGroup] = []
    for event in events:
        if type(event) is not DealingRangeStructureEvent:
            raise TypeError("structure event has an invalid type")
        matching = tuple(gap for gap in gaps if gap.structure_event_id == event.event_id)
        if not matching:
            continue
        if len(matching) != 1:
            raise ValueError("multiple FVGs claim one event role")
        gap = matching[0]
        if type(gap) is not FairValueGap or gap.displacement_id is None:
            raise ValueError("receiving FVG is incomplete")
        event_indices = event.provenance.source_indices
        event_timestamps = event.provenance.source_timestamps
        gap_indices = gap.source_indices
        gap_timestamps = gap.source_timestamps
        if (event_indices[-1], _timestamp(event_timestamps[-1], "event source timestamp")) != (gap_indices[-1], _timestamp(gap_timestamps[-1], "gap source timestamp")):
            raise ValueError("event and FVG do not co-terminate")
        shorter_i, longer_i = (event_indices, gap_indices) if len(event_indices) <= len(gap_indices) else (gap_indices, event_indices)
        shorter_t, longer_t = (event_timestamps, gap_timestamps) if len(event_timestamps) <= len(gap_timestamps) else (gap_timestamps, event_timestamps)
        if shorter_i != longer_i[-len(shorter_i):] or tuple(map(_timestamp_for_compare, shorter_t)) != tuple(map(_timestamp_for_compare, longer_t[-len(shorter_t):])):
            raise ValueError("event/FVG positional suffix mismatch")
        event_digest = _source_digest(segment, event_indices, event_timestamps)
        gap_digest = _source_digest(segment, gap_indices, gap_timestamps)
        event_effective = (event.provenance.confirmation_index, _timestamp(event.provenance.confirmation_timestamp, "event confirmation"))
        gap_effective = (gap.formation_end_index, _timestamp(gap.formation_end_timestamp, "gap formation"))
        if event_effective != gap_effective:
            raise ValueError("event/FVG effective moments differ")
        gap_transitions = tuple(item for item in transitions if item.gap_id == gap.gap_id and (item.index, _timestamp(item.timestamp, "transition timestamp")) <= gap_effective)
        gap_snapshots = tuple(item for item in snapshots if item.gap_id == gap.gap_id and (item.index, _timestamp(item.timestamp, "snapshot timestamp")) <= gap_effective)
        if any(type(item) is not FairValueGapTransition for item in gap_transitions) or any(type(item) is not FairValueGapSnapshot for item in gap_snapshots):
            raise TypeError("FVG history has an invalid type")
        history = tuple(item.transition_id for item in gap_transitions) + tuple(item.snapshot_id for item in gap_snapshots)
        state = gap_snapshots[-1].state.value if gap_snapshots else "ACTIVE"
        references = (
            GCContinuityReceivingReference(
                "DEALING_RANGE", "STRUCTURE_EVENT", event.event_id,
                segment_result.segment_ordinal, segment.segment_id,
                event_effective[0], event_effective[1], event_effective[0], event_effective[1],
                event.event_type.value, (), event_digest, _sha(event),
            ),
            GCContinuityReceivingReference(
                "FAIR_VALUE_GAP", "GAP", gap.gap_id,
                segment_result.segment_ordinal, segment.segment_id,
                gap_effective[0], gap_effective[1], gap_effective[0], gap_effective[1],
                state, history, gap_digest, _sha(gap),
            ),
        )
        group_id = make_gc_cross_segment_continuity_id(
            identity_kind=GCCrossSegmentContinuityIdentityKind.RECEIVING_GROUP,
            **common,
            boundary_id=boundary.boundary_id,
            receiving_segment_ordinal=segment_result.segment_ordinal,
            receiving_segment_id=segment.segment_id,
            effective_index=event_effective[0],
            effective_timestamp=event_effective[1],
            receiving_references=references,
        )
        groups.append(GCContinuityReceivingGroup(group_id, boundary.boundary_id, segment_result.segment_ordinal, segment.segment_id, event_effective[0], event_effective[1], references))
    return tuple(groups)


def _timestamp_for_compare(value: datetime) -> datetime:
    return _timestamp(value, "source timestamp")


def analyze_gc_cross_segment_continuity(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    boundary_calendar_entries: tuple[GCSplitSessionCalendarEntry, ...] | None,
    candidate_calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    canonical_candidate_evidence: GCCandidateEvidenceResult | None,
    frontier_evidence: GCCandidateFrontierEvidenceResult | None = None,
    candidate_config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCrossSegmentContinuityResult:
    """Assess immutable continuity references without creating trading evidence."""

    try:
        if type(dataset_config) is not GCDatasetBuildConfig:
            raise TypeError("dataset_config must be GCDatasetBuildConfig")
        if type(candidate_config) is not GCCandidateEvidenceConfig:
            raise TypeError("candidate_config must be GCCandidateEvidenceConfig")
        GCCandidateEvidenceConfig(candidate_config.equal_liquidity_config, candidate_config.dealing_range_config)
        if _text(dataset_config.instrument, "instrument", upper=True) != "GC" or _text(dataset_config.timeframe, "timeframe", upper=True) != "5M":
            raise ValueError("continuity V1 requires GC/5M")
        if dataset_config.tick_size != Decimal("0.1"):
            raise ValueError("continuity V1 requires exact 0.1 tick size")
        if dataset is not None:
            validated_dataset = _validate_dataset(dataset, dataset_config)
        else:
            validated_dataset = None
        expected_calendar_version = validated_dataset.manifest.calendar_version if validated_dataset is not None and validated_dataset.manifest is not None else None
        if boundary_calendar_entries is not None:
            boundary_calendar = _validate_boundary_calendar(boundary_calendar_entries, expected_calendar_version or boundary_calendar_entries[0].calendar_version if boundary_calendar_entries else "")
        else:
            boundary_calendar = None
        if candidate_calendar_entries is not None:
            candidate_calendar = _validate_candidate_calendar(candidate_calendar_entries, expected_calendar_version or candidate_calendar_entries[0].calendar_version if candidate_calendar_entries else "")
        else:
            candidate_calendar = None
        if structural_seed is not None:
            if type(structural_seed) is not GCCanonicalSeedEvidence:
                raise TypeError("structural_seed has an invalid type")
            _hash(structural_seed.seed_id, "seed_id")
            _hash(structural_seed.dataset_id, "seed dataset_id")
            _hash(structural_seed.source_bar_digest, "source_bar_digest")
            for name in ("dealing_range_swings", "equal_liquidity_swings", "structure_events", "fair_value_gap_context_links"):
                if type(getattr(structural_seed, name)) is not tuple:
                    raise TypeError(f"seed {name} must be a tuple")
        if canonical_candidate_evidence is not None:
            canonical_control = _validate_result_shape(canonical_candidate_evidence)
        else:
            canonical_control = None
        if frontier_evidence is not None and type(frontier_evidence) is not GCCandidateFrontierEvidenceResult:
            raise TypeError("frontier_evidence has an invalid type")
    except (TypeError, ValueError, IndexError):
        return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_SUPPLIED_CONTEXT")
    except Exception:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "VALIDATION_EXCEPTION")

    if any(item is None for item in (validated_dataset, boundary_calendar, candidate_calendar, structural_seed, canonical_control)):
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_TOP_LEVEL_CONTEXT")
    assert validated_dataset is not None
    assert boundary_calendar is not None
    assert candidate_calendar is not None
    assert structural_seed is not None
    assert canonical_control is not None
    if validated_dataset.status is GCDatasetBuildStatus.INVALID:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_DATASET")
    if validated_dataset.status is GCDatasetBuildStatus.AMBIGUOUS:
        return _blocked(SMCV2PrimitiveStatus.AMBIGUOUS, "DATASET_AMBIGUOUS")
    if validated_dataset.status is GCDatasetBuildStatus.UNKNOWN:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "DATASET_UNKNOWN")
    if validated_dataset.status is GCDatasetBuildStatus.NONE:
        return _blocked(SMCV2PrimitiveStatus.NONE, "NO_DATASET_SEGMENTS")
    assert validated_dataset.manifest is not None and validated_dataset.dataset_id is not None
    if structural_seed.dataset_id != validated_dataset.dataset_id or structural_seed.instrument.upper() != "GC" or structural_seed.timeframe.upper() != "5M":
        return _blocked(SMCV2PrimitiveStatus.INVALID, "SEED_BINDING_MISMATCH")

    try:
        rebuilt = build_gc_candidate_evidence(
            dataset_config=dataset_config,
            dataset=validated_dataset,
            calendar_entries=candidate_calendar,
            structural_seed=structural_seed,
            config=candidate_config,
        )
    except Exception:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_REBUILD_EXCEPTION")
    if rebuilt != canonical_control:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_CONTROL_DRIFT")

    validated_frontier = None
    if frontier_evidence is not None:
        try:
            recomputed_frontier = analyze_gc_candidate_frontier_evidence(
                dataset_config=dataset_config,
                dataset=validated_dataset,
                calendar_entries=candidate_calendar,
                structural_seed=structural_seed,
                canonical_candidate_evidence=canonical_control,
                config=candidate_config,
            )
        except Exception:
            return _blocked(SMCV2PrimitiveStatus.INVALID, "FRONTIER_REBUILD_EXCEPTION")
        if recomputed_frontier != frontier_evidence:
            return _blocked(SMCV2PrimitiveStatus.INVALID, "FRONTIER_EVIDENCE_DRIFT")
        if (
            frontier_evidence.status is not SMCV2PrimitiveStatus.VALID
            or frontier_evidence.frontier is None
        ):
            return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_FRONTIER_EVIDENCE")
        validated_frontier = frontier_evidence.frontier
        if (
            validated_frontier.canonical_control_digest != _sha(canonical_control)
            or validated_frontier.dataset_id != validated_dataset.dataset_id
            or validated_frontier.seed_id != structural_seed.seed_id
            or validated_frontier.frontier_ordinal != len(canonical_control.segment_results)
            or validated_frontier.source_segment.segment_ordinal != validated_frontier.frontier_ordinal
            or validated_frontier.receiving_segment.segment_ordinal != validated_frontier.frontier_ordinal + 1
        ):
            return _blocked(SMCV2PrimitiveStatus.INVALID, "FRONTIER_BINDING_MISMATCH")

    boundary_digest = _sha(boundary_calendar)
    candidate_digest = _sha(candidate_calendar)
    control_digest = _sha(canonical_control)
    common: dict[str, object] = {
        "instrument": dataset_config.instrument,
        "timeframe": dataset_config.timeframe,
        "dataset_id": validated_dataset.dataset_id,
        "calendar_version": validated_dataset.manifest.calendar_version,
        "boundary_calendar_digest": boundary_digest,
        "candidate_calendar_digest": candidate_digest,
        "timezone_data_version": dataset_config.timezone_data_version,
        "seed_id": structural_seed.seed_id,
        "canonical_control_digest": control_digest,
    }
    boundaries: list[GCCrossSegmentBoundary] = []
    groups: list[GCContinuityReceivingGroup] = []
    segment_results = canonical_control.segment_results
    try:
        for position in range(len(segment_results) - 1):
            source_result = segment_results[position]
            receiving_result = segment_results[position + 1]
            if source_result.segment_ordinal + 1 != receiving_result.segment_ordinal:
                raise ValueError("candidate segment results are non-adjacent")
            if source_result.segment_ordinal >= len(validated_dataset.segments) or receiving_result.segment_ordinal >= len(validated_dataset.segments):
                raise ValueError("candidate segment ordinal is outside dataset")
            source = validated_dataset.segments[source_result.segment_ordinal]
            receiving = validated_dataset.segments[receiving_result.segment_ordinal]
            if source.segment_id != source_result.segment_id or receiving.segment_id != receiving_result.segment_id:
                raise ValueError("candidate segment identity mismatch")
            decision, reason_tokens = _boundary_decision(source, receiving, boundary_calendar, candidate_calendar)
            dependencies = _dependency_references(source_result, source) if decision is GCCrossSegmentContinuityDecision.ELIGIBLE else ()
            boundary_common = {
                **common,
                # Boundary evidence is first-known at the source close.  Bind
                # only the canonical control prefix available at that moment
                # so a strictly later complete receiving group cannot rewrite
                # an already emitted boundary identity.
                "canonical_control_digest": _sha(segment_results[: position + 1]),
            }
            boundary_id = make_gc_cross_segment_continuity_id(
                identity_kind=GCCrossSegmentContinuityIdentityKind.BOUNDARY,
                **boundary_common,
                source_segment_ordinal=source_result.segment_ordinal,
                source_segment_id=source.segment_id,
                receiving_segment_ordinal=receiving_result.segment_ordinal,
                receiving_segment_id=receiving.segment_id,
                contract=source.contract,
                source_trade_date=source.last_trade_date,
                receiving_trade_date=receiving.first_trade_date,
                source_end_timestamp=source.bars[-1].timestamp,
                receiving_start_timestamp=receiving.bars[0].timestamp,
                decision=decision,
                reason_tokens=reason_tokens,
                dependency_references=dependencies,
            )
            boundary = GCCrossSegmentBoundary(
                boundary_id, source_result.segment_ordinal, source.segment_id,
                receiving_result.segment_ordinal, receiving.segment_id, source.contract,
                source.last_trade_date, receiving.first_trade_date,
                _timestamp(source.bars[-1].timestamp, "source end"), _timestamp(receiving.bars[0].timestamp, "receiving start"),
                decision, reason_tokens, dependencies,
            )
            boundaries.append(boundary)
            if decision is GCCrossSegmentContinuityDecision.ELIGIBLE:
                receiving_events = tuple(
                    event for event in structural_seed.structure_events
                    if any(
                        bar.index == event.provenance.confirmation_index
                        and _timestamp(bar.timestamp, "bar timestamp") == _timestamp(event.provenance.confirmation_timestamp, "event timestamp")
                        for bar in receiving.bars
                    )
                )
                group_common = {
                    **common,
                    "canonical_control_digest": _sha(segment_results[: position + 2]),
                }
                groups.extend(_receiving_groups(boundary=boundary, segment=receiving, segment_result=receiving_result, events=receiving_events, common=group_common))
        if validated_frontier is not None:
            source_result = validated_frontier.source_segment
            receiving_result = validated_frontier.receiving_segment
            if source_result.segment_ordinal >= len(validated_dataset.segments) or receiving_result.segment_ordinal >= len(validated_dataset.segments):
                raise ValueError("frontier segment ordinal is outside dataset")
            source = validated_dataset.segments[source_result.segment_ordinal]
            receiving = validated_dataset.segments[receiving_result.segment_ordinal]
            if source.segment_id != source_result.segment_id or receiving.segment_id != receiving_result.segment_id:
                raise ValueError("frontier segment identity mismatch")
            decision, reason_tokens = _boundary_decision(
                source,
                receiving,
                boundary_calendar,
                candidate_calendar,
            )
            dependencies = (
                _dependency_references(source_result, source)
                if decision is GCCrossSegmentContinuityDecision.ELIGIBLE
                else ()
            )
            frontier_boundary_common = {
                **common,
                "canonical_control_digest": _sha(
                    {
                        "canonical_control_digest": control_digest,
                        "frontier_id": validated_frontier.frontier_id,
                        "source_segment_evidence_digest": _sha(source_result),
                    }
                ),
            }
            boundary_id = make_gc_cross_segment_continuity_id(
                identity_kind=GCCrossSegmentContinuityIdentityKind.BOUNDARY,
                **frontier_boundary_common,
                source_segment_ordinal=source_result.segment_ordinal,
                source_segment_id=source.segment_id,
                receiving_segment_ordinal=receiving_result.segment_ordinal,
                receiving_segment_id=receiving.segment_id,
                contract=source.contract,
                source_trade_date=source.last_trade_date,
                receiving_trade_date=receiving.first_trade_date,
                source_end_timestamp=source.bars[-1].timestamp,
                receiving_start_timestamp=receiving.bars[0].timestamp,
                decision=decision,
                reason_tokens=reason_tokens,
                dependency_references=dependencies,
            )
            boundary = GCCrossSegmentBoundary(
                boundary_id,
                source_result.segment_ordinal,
                source.segment_id,
                receiving_result.segment_ordinal,
                receiving.segment_id,
                source.contract,
                source.last_trade_date,
                receiving.first_trade_date,
                _timestamp(source.bars[-1].timestamp, "source end"),
                _timestamp(receiving.bars[0].timestamp, "receiving start"),
                decision,
                reason_tokens,
                dependencies,
            )
            boundaries.append(boundary)
            if decision is GCCrossSegmentContinuityDecision.ELIGIBLE:
                receiving_events = tuple(
                    event
                    for event in structural_seed.structure_events
                    if any(
                        bar.index == event.provenance.confirmation_index
                        and _timestamp(bar.timestamp, "bar timestamp")
                        == _timestamp(event.provenance.confirmation_timestamp, "event timestamp")
                        for bar in receiving.bars
                    )
                )
                frontier_group_common = {
                    **frontier_boundary_common,
                    "canonical_control_digest": _sha(
                        {
                            "frontier_boundary_digest": frontier_boundary_common[
                                "canonical_control_digest"
                            ],
                            "receiving_segment_evidence_digest": _sha(receiving_result),
                        }
                    ),
                }
                groups.extend(
                    _receiving_groups(
                        boundary=boundary,
                        segment=receiving,
                        segment_result=receiving_result,
                        events=receiving_events,
                        common=frontier_group_common,
                    )
                )
    except LookupError:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "BOUNDARY_CALENDAR_UNAVAILABLE", tuple(boundaries), tuple(groups))
    except (TypeError, ValueError):
        return _blocked(SMCV2PrimitiveStatus.INVALID, "INVALID_BOUNDARY_EVIDENCE", tuple(boundaries), tuple(groups))
    except Exception:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "BOUNDARY_VALIDATION_EXCEPTION", tuple(boundaries), tuple(groups))

    boundary_ids = tuple(item.boundary_id for item in boundaries)
    group_ids = tuple(item.group_id for item in groups)
    manifest_id = make_gc_cross_segment_continuity_id(
        identity_kind=GCCrossSegmentContinuityIdentityKind.MANIFEST,
        **common,
        boundary_ids=boundary_ids,
        receiving_group_ids=group_ids,
    )
    manifest = GCCrossSegmentContinuityManifest(
        manifest_id, GC_CROSS_SEGMENT_CONTINUITY_VERSION,
        dataset_config.instrument.upper(), dataset_config.timeframe.upper(), validated_dataset.dataset_id,
        validated_dataset.manifest.calendar_version, boundary_digest, candidate_digest,
        dataset_config.timezone_data_version, structural_seed.seed_id, control_digest,
        boundary_ids, group_ids,
    )
    has_eligible = any(item.decision is GCCrossSegmentContinuityDecision.ELIGIBLE for item in boundaries)
    if canonical_control.status is SMCV2PrimitiveStatus.INVALID:
        return _blocked(SMCV2PrimitiveStatus.INVALID, "CANONICAL_CONTROL_INVALID", tuple(boundaries), tuple(groups))
    if canonical_control.status is SMCV2PrimitiveStatus.AMBIGUOUS:
        return _blocked(SMCV2PrimitiveStatus.AMBIGUOUS, "CANONICAL_CONTROL_AMBIGUOUS", tuple(boundaries), tuple(groups))
    if canonical_control.status is SMCV2PrimitiveStatus.UNKNOWN:
        return _blocked(
            SMCV2PrimitiveStatus.UNKNOWN,
            "CANONICAL_CONTROL_UNKNOWN",
            tuple(boundaries),
            tuple(groups),
            manifest=manifest,
        )
    status = SMCV2PrimitiveStatus.VALID if has_eligible else SMCV2PrimitiveStatus.NONE
    reason = "ELIGIBLE_BOUNDARY_PRESENT" if has_eligible else "NO_ELIGIBLE_BOUNDARY"
    return GCCrossSegmentContinuityResult(status, tuple(boundaries), tuple(groups), manifest, (reason,), ())


__all__ = (
    "GC_CROSS_SEGMENT_CONTINUITY_VERSION",
    "GCCrossSegmentContinuityIdentityKind",
    "GCCrossSegmentContinuityDecision",
    "GCContinuityDependencyReference",
    "GCContinuityReceivingReference",
    "GCCrossSegmentBoundary",
    "GCContinuityReceivingGroup",
    "GCCrossSegmentContinuityManifest",
    "GCCrossSegmentContinuityResult",
    "make_gc_cross_segment_continuity_id",
    "analyze_gc_cross_segment_continuity",
)
