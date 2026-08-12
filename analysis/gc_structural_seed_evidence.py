"""Deterministic, segment-local structural seed evidence for GC Phase A.

This module is deliberately standalone.  It consumes the immutable canonical
dataset result and emits only public SMC v2 evidence objects; it does not alter
the dataset, package exports, runtime strategy behaviour, or candidate logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import hashlib
import importlib.metadata
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GC_DATASET_EXCHANGE_TIMEZONE,
    GC_DATASET_INSTRUMENT,
    GC_DATASET_SOURCE_TIMEZONE,
    GC_DATASET_TICK_SIZE,
    GC_DATASET_TIMEFRAME,
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
    DealingRangeEventType,
    DealingRangeStructureEvent,
    DealingRangeSwing,
    DealingRangeSwingSide,
    make_dealing_range_id,
)
from smc.equal_liquidity import (
    EqualLiquiditySide,
    EqualLiquiditySwing,
    make_equal_liquidity_id,
)
from smc.fair_value_gap import FairValueGapContextLink
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2EventProvenance,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


GC_STRUCTURAL_SEED_VERSION = "GC-STRUCTURAL-SEED-V1"
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")


class GCStructuralSeedIdentityKind(str, Enum):
    DISPLACEMENT = "DISPLACEMENT"
    SEED = "SEED"


@dataclass(frozen=True)
class GCStructuralSeedConfig:
    swing_left_bars: int = 2
    swing_right_bars: int = 2
    break_buffer_ticks: int = 1

    def __post_init__(self) -> None:
        values = (self.swing_left_bars, self.swing_right_bars, self.break_buffer_ticks)
        if any(type(value) is not int for value in values):
            raise TypeError("structural seed configuration values must be integers")
        if any(value <= 0 for value in values):
            raise ValueError("structural seed configuration values must be positive")
        if values != (2, 2, 1):
            raise ValueError("this structural seed version requires the locked 2/2/1 configuration")


@dataclass(frozen=True)
class GCCanonicalSeedEvidence:
    seed_id: str
    seed_version: str
    instrument: str
    timeframe: str
    dataset_id: str
    source_bar_digest: str
    dealing_range_swings: tuple[DealingRangeSwing, ...]
    equal_liquidity_swings: tuple[EqualLiquiditySwing, ...]
    structure_events: tuple[DealingRangeStructureEvent, ...]
    fair_value_gap_context_links: tuple[FairValueGapContextLink, ...]


@dataclass(frozen=True)
class GCStructuralSeedResult:
    status: SMCV2PrimitiveStatus
    seed: GCCanonicalSeedEvidence | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _SegmentEvidence:
    segment: GCCanonicalContractSegment
    dealing_swings: tuple[DealingRangeSwing, ...]
    equal_swings: tuple[EqualLiquiditySwing, ...]
    events: tuple[DealingRangeStructureEvent, ...]
    links: tuple[FairValueGapContextLink, ...]


class _StructuralUnknown(ValueError):
    pass


def _invalid(reason: str = "INVALID_STRUCTURAL_EVIDENCE") -> GCStructuralSeedResult:
    return GCStructuralSeedResult(
        SMCV2PrimitiveStatus.INVALID,
        reasons=(reason,),
        blocking_reasons=(reason,),
    )


def _blocked(status: SMCV2PrimitiveStatus, reason: str) -> GCStructuralSeedResult:
    return GCStructuralSeedResult(status, reasons=(reason,), blocking_reasons=(reason,))


def _required_text(value: object, name: str, *, uppercase: bool = False) -> str:
    if type(value) is not str or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    normalized = value.strip()
    return normalized.upper() if uppercase else normalized


def _require_hash(value: object, name: str) -> str:
    if type(value) is not str or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _normalize_timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TypeError(f"{name} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _timestamp_text(value: datetime) -> str:
    return _normalize_timestamp(value, "timestamp").isoformat(timespec="microseconds").replace("+00:00", "Z")


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TypeError("decimal value must be finite")
    if value == 0:
        return "0.0"
    text = format(value, "f")
    if "." not in text:
        text += ".0"
    return text


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _config_payload(config: GCStructuralSeedConfig) -> dict[str, int]:
    if type(config) is not GCStructuralSeedConfig:
        raise TypeError("config must be a GCStructuralSeedConfig")
    GCStructuralSeedConfig(
        swing_left_bars=config.swing_left_bars,
        swing_right_bars=config.swing_right_bars,
        break_buffer_ticks=config.break_buffer_ticks,
    )
    return {
        "swing_left_bars": config.swing_left_bars,
        "swing_right_bars": config.swing_right_bars,
        "break_buffer_ticks": config.break_buffer_ticks,
    }


def make_gc_structural_seed_id(
    *,
    identity_kind: GCStructuralSeedIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    seed_version: str,
    config: GCStructuralSeedConfig,
    source_bar_digest: str,
    segment_id: str | None = None,
    direction: SMCV2Direction | None = None,
    source_indices: tuple[int, ...] = (),
    source_timestamps: tuple[datetime, ...] = (),
    boundaries: SMCV2TickRange | None = None,
    structure_event_id: str | None = None,
    segment_evidence_digests: tuple[tuple[str, str], ...] = (),
) -> str:
    """Build one exact kind-specific deterministic structural identity."""

    try:
        if not isinstance(identity_kind, GCStructuralSeedIdentityKind):
            raise TypeError("identity_kind must be a GCStructuralSeedIdentityKind")
        kind = identity_kind
        normalized_instrument = _required_text(instrument, "instrument", uppercase=True)
        normalized_timeframe = _required_text(timeframe, "timeframe", uppercase=True)
        if not isinstance(tick_size, Decimal) or not tick_size.is_finite() or tick_size <= 0:
            raise ValueError("tick_size must be a positive finite Decimal")
        normalized_dataset_id = _require_hash(dataset_id, "dataset_id")
        if seed_version != GC_STRUCTURAL_SEED_VERSION:
            raise ValueError("seed_version does not match the locked version")
        common = {
            "identity_kind": kind.value,
            "instrument": normalized_instrument,
            "timeframe": normalized_timeframe,
            "tick_size": _decimal_text(tick_size),
            "dataset_id": normalized_dataset_id,
            "seed_version": seed_version,
            "config": _config_payload(config),
            "source_bar_digest": _require_hash(source_bar_digest, "source_bar_digest"),
        }
        if kind is GCStructuralSeedIdentityKind.DISPLACEMENT:
            if segment_evidence_digests != ():
                raise ValueError("segment_evidence_digests is forbidden for DISPLACEMENT")
            normalized_segment_id = _require_hash(segment_id, "segment_id")
            if direction not in (SMCV2Direction.BULLISH, SMCV2Direction.BEARISH):
                raise ValueError("direction must be BULLISH or BEARISH")
            if type(source_indices) is not tuple or len(source_indices) != 3:
                raise ValueError("DISPLACEMENT requires exactly three source indices")
            if any(type(item) is not int or item < 0 for item in source_indices):
                raise TypeError("source_indices must contain non-negative integers")
            if any(left >= right for left, right in zip(source_indices, source_indices[1:])):
                raise ValueError("source_indices must be strictly increasing")
            if type(source_timestamps) is not tuple or len(source_timestamps) != 3:
                raise ValueError("DISPLACEMENT requires exactly three source timestamps")
            normalized_timestamps = tuple(
                _normalize_timestamp(item, "source_timestamp") for item in source_timestamps
            )
            if any(left >= right for left, right in zip(normalized_timestamps, normalized_timestamps[1:])):
                raise ValueError("source_timestamps must be strictly increasing")
            if type(boundaries) is not SMCV2TickRange:
                raise TypeError("boundaries must be an SMCV2TickRange")
            if boundaries.upper_tick - boundaries.lower_tick < 2:
                raise ValueError("displacement boundaries must span at least two ticks")
            payload = {
                **common,
                "segment_id": normalized_segment_id,
                "direction": direction.value,
                "source_indices": source_indices,
                "source_timestamps": tuple(_timestamp_text(item) for item in normalized_timestamps),
                "boundaries": {
                    "lower_tick": boundaries.lower_tick,
                    "upper_tick": boundaries.upper_tick,
                },
                "structure_event_id": _require_hash(structure_event_id, "structure_event_id"),
            }
        else:
            if any(value is not None for value in (segment_id, direction, boundaries, structure_event_id)):
                raise ValueError("DISPLACEMENT-only fields are forbidden for SEED")
            if source_indices != () or source_timestamps != ():
                raise ValueError("source moment fields are forbidden for SEED")
            if type(segment_evidence_digests) is not tuple or not segment_evidence_digests:
                raise ValueError("SEED requires non-empty segment evidence digests")
            normalized_pairs: list[tuple[str, str]] = []
            seen: set[str] = set()
            for item in segment_evidence_digests:
                if type(item) is not tuple or len(item) != 2:
                    raise TypeError("segment evidence entries must be two-member tuples")
                segment_hash = _require_hash(item[0], "segment_id")
                evidence_hash = _require_hash(item[1], "segment_evidence_digest")
                if segment_hash in seen:
                    raise ValueError("segment evidence identities must be unique")
                seen.add(segment_hash)
                normalized_pairs.append((segment_hash, evidence_hash))
            payload = {**common, "segment_evidence_digests": tuple(normalized_pairs)}
        return _canonical_hash(payload)
    except (TypeError, ValueError):
        raise
    except (InvalidOperation, ArithmeticError) as exc:
        raise ValueError("malformed structural identity decimal evidence") from exc
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError("malformed structural identity evidence") from exc


def _validate_dataset_config(value: object) -> GCDatasetBuildConfig:
    if type(value) is not GCDatasetBuildConfig:
        raise TypeError("dataset_config must be a GCDatasetBuildConfig")
    instrument = _required_text(value.instrument, "instrument", uppercase=True)
    timeframe = _required_text(value.timeframe, "timeframe", uppercase=True)
    if instrument != GC_DATASET_INSTRUMENT or timeframe != GC_DATASET_TIMEFRAME:
        raise ValueError("dataset instrument/timeframe does not match GC/5M")
    if value.source_timezone != GC_DATASET_SOURCE_TIMEZONE:
        raise ValueError("source timezone mismatch")
    if value.exchange_timezone != GC_DATASET_EXCHANGE_TIMEZONE:
        raise ValueError("exchange timezone mismatch")
    try:
        ZoneInfo(GC_DATASET_SOURCE_TIMEZONE)
        ZoneInfo(GC_DATASET_EXCHANGE_TIMEZONE)
        runtime_tzdata = importlib.metadata.version("tzdata")
    except (ZoneInfoNotFoundError, importlib.metadata.PackageNotFoundError) as exc:
        raise ValueError("runtime timezone evidence is unavailable") from exc
    if _required_text(value.timezone_data_version, "timezone_data_version") != runtime_tzdata:
        raise ValueError("timezone data version mismatch")
    if not isinstance(value.tick_size, Decimal) or value.tick_size != GC_DATASET_TICK_SIZE:
        raise ValueError("dataset tick size mismatch")
    _required_text(value.initial_contract, "initial_contract", uppercase=True)
    if type(value.initial_trade_date) is not date:
        raise TypeError("initial_trade_date must be a date")
    if type(value.roll_confirmation_sessions) is not int or value.roll_confirmation_sessions != 3:
        raise ValueError("roll_confirmation_sessions must be exactly 3")
    if type(value.oos_start_trade_date) is not date or type(value.oos_end_trade_date) is not date:
        raise TypeError("OOS bounds must be dates")
    if value.oos_start_trade_date > value.oos_end_trade_date:
        raise ValueError("OOS date range is impossible")
    return value


def _bar_payload(bar: object) -> dict[str, object]:
    required = ("index", "timestamp", "open_tick", "high_tick", "low_tick", "close_tick", "volume", "is_closed")
    if any(not hasattr(bar, name) for name in required):
        raise TypeError("bar is missing required fields")
    values = tuple(getattr(bar, name) for name in required)
    index, timestamp, open_tick, high_tick, low_tick, close_tick, volume, is_closed = values
    if type(index) is not int or index < 0:
        raise TypeError("bar index must be a non-negative integer")
    normalized_timestamp = _normalize_timestamp(timestamp, "bar timestamp")
    ticks = (open_tick, high_tick, low_tick, close_tick)
    if any(type(item) is not int for item in ticks):
        raise TypeError("OHLC ticks must be integers")
    if high_tick < low_tick or not (low_tick <= open_tick <= high_tick) or not (low_tick <= close_tick <= high_tick):
        raise ValueError("bar OHLC geometry is invalid")
    if type(volume) is not int or volume < 0:
        raise TypeError("bar volume must be a non-negative integer")
    if is_closed is not True:
        raise ValueError("all structural bars must be fully closed")
    return {
        "index": index,
        "timestamp": _timestamp_text(normalized_timestamp),
        "open_tick": open_tick,
        "high_tick": high_tick,
        "low_tick": low_tick,
        "close_tick": close_tick,
        "volume": volume,
        "is_closed": True,
    }


def _bar_digest(bars: tuple[object, ...]) -> str:
    return _canonical_hash(tuple(_bar_payload(bar) for bar in bars))


def _dataset_config_payload(config: GCDatasetBuildConfig) -> dict[str, object]:
    return {
        "instrument": config.instrument.upper(),
        "timeframe": config.timeframe.upper(),
        "source_timezone": config.source_timezone,
        "exchange_timezone": config.exchange_timezone,
        "timezone_data_version": config.timezone_data_version,
        "tick_size": _decimal_text(config.tick_size),
        "initial_contract": config.initial_contract.upper(),
        "initial_trade_date": config.initial_trade_date.isoformat(),
        "roll_confirmation_sessions": config.roll_confirmation_sessions,
        "oos_start_trade_date": config.oos_start_trade_date.isoformat(),
        "oos_end_trade_date": config.oos_end_trade_date.isoformat(),
    }


def _validate_manifest(manifest: object, dataset: GCDatasetBuildResult) -> GCDatasetManifest:
    if type(manifest) is not GCDatasetManifest:
        raise TypeError("VALID dataset requires a GCDatasetManifest")
    if manifest.dataset_id != dataset.dataset_id:
        raise ValueError("manifest dataset identity mismatch")
    _require_hash(manifest.dataset_id, "dataset_id")
    if manifest.version != GC_DATASET_BUILDER_VERSION:
        raise ValueError("dataset builder version mismatch")
    if type(manifest.source_ids) is not tuple or not manifest.source_ids:
        raise ValueError("manifest source_ids must be non-empty")
    if type(manifest.coverage_ids) is not tuple or not manifest.coverage_ids:
        raise ValueError("manifest coverage_ids must be non-empty")
    for name, members in (("source_ids", manifest.source_ids), ("coverage_ids", manifest.coverage_ids)):
        if len(set(members)) != len(members):
            raise ValueError(f"{name} must be unique")
        for member in members:
            _require_hash(member, name)
    _require_hash(manifest.coverage_digest, "coverage_digest")
    if manifest.segment_ids != tuple(segment.segment_id for segment in dataset.segments):
        raise ValueError("manifest segment order mismatch")
    if manifest.timezone_data_version != importlib.metadata.version("tzdata"):
        raise ValueError("manifest timezone version mismatch")
    raw_start = _normalize_timestamp(manifest.raw_start_timestamp, "raw_start_timestamp")
    raw_end = _normalize_timestamp(manifest.raw_end_timestamp, "raw_end_timestamp")
    if raw_start > raw_end:
        raise ValueError("manifest raw timestamp range is impossible")
    if manifest.usable_start_timestamp is not None:
        _normalize_timestamp(manifest.usable_start_timestamp, "usable_start_timestamp")
    if manifest.usable_end_timestamp is not None:
        _normalize_timestamp(manifest.usable_end_timestamp, "usable_end_timestamp")
    count_fields = (
        manifest.parsed_row_count,
        manifest.eligible_row_count,
        manifest.development_bar_count,
        manifest.oos_bar_count,
        manifest.excluded_row_count,
        manifest.missing_bar_count,
        manifest.attested_no_trade_interval_count,
        manifest.raw_volume,
        manifest.eligible_volume,
        manifest.excluded_volume,
    )
    if any(type(item) is not int or item < 0 for item in count_fields):
        raise TypeError("manifest count and volume fields must be non-negative integers")
    if manifest.development_bar_count + manifest.oos_bar_count != manifest.eligible_row_count:
        raise ValueError("manifest partition counts do not reconcile")
    if manifest.eligible_row_count + manifest.excluded_row_count != manifest.parsed_row_count:
        raise ValueError("manifest row counts do not reconcile")
    if manifest.eligible_volume + manifest.excluded_volume != manifest.raw_volume:
        raise ValueError("manifest volume totals do not reconcile")
    if type(manifest.completed_session_volumes) is not tuple or type(manifest.exclusion_counts) is not tuple:
        raise TypeError("manifest nested evidence must be tuples")
    if type(manifest.roll_trade_dates) is not tuple or any(type(item) is not date for item in manifest.roll_trade_dates):
        raise TypeError("roll_trade_dates must be a tuple of dates")
    return manifest


def _validate_valid_dataset(config: GCDatasetBuildConfig, dataset: GCDatasetBuildResult) -> None:
    if dataset.status is not GCDatasetBuildStatus.VALID:
        raise ValueError("dataset is not VALID")
    _require_hash(dataset.dataset_id, "dataset_id")
    if type(dataset.segments) is not tuple:
        raise TypeError("dataset segments must be a tuple")
    if type(dataset.reasons) is not tuple or type(dataset.blocking_reasons) is not tuple:
        raise TypeError("dataset reason fields must be tuples")
    manifest = _validate_manifest(dataset.manifest, dataset)
    prior_end: datetime | None = None
    total_count = development_count = oos_count = total_volume = 0
    for segment in dataset.segments:
        if type(segment) is not GCCanonicalContractSegment:
            raise TypeError("segments must be canonical contract segments")
        _require_hash(segment.segment_id, "segment_id")
        contract = _required_text(segment.contract, "contract", uppercase=True)
        if not isinstance(segment.partition, GCSegmentPartition):
            raise TypeError("segment partition is invalid")
        if type(segment.first_trade_date) is not date or type(segment.last_trade_date) is not date:
            raise TypeError("segment trade-date bounds must be dates")
        if segment.last_trade_date < segment.first_trade_date:
            raise ValueError("segment trade-date range is impossible")
        if type(segment.source_ids) is not tuple or not segment.source_ids:
            raise ValueError("segment source_ids must be non-empty")
        for source_id in segment.source_ids:
            _require_hash(source_id, "source_id")
        if len(set(segment.source_ids)) != len(segment.source_ids):
            raise ValueError("segment source_ids must be unique")
        if type(segment.preceding_missing_bar_count) is not int or segment.preceding_missing_bar_count < 0:
            raise TypeError("preceding_missing_bar_count must be a non-negative integer")
        if type(segment.bars) is not tuple or not segment.bars:
            raise ValueError("canonical segments must contain bars")
        bar_payloads = tuple(_bar_payload(bar) for bar in segment.bars)
        indices = tuple(item["index"] for item in bar_payloads)
        if indices != tuple(range(len(segment.bars))):
            raise ValueError("segment bar indices must be contiguous and local")
        moments = tuple(_normalize_timestamp(bar.timestamp, "bar timestamp") for bar in segment.bars)
        if any(left >= right for left, right in zip(moments, moments[1:])):
            raise ValueError("segment bar timestamps must be strictly increasing")
        if prior_end is not None and prior_end >= moments[0]:
            raise ValueError("segment timestamps must be globally ordered and non-overlapping")
        prior_end = moments[-1]
        expected_segment_id = make_gc_dataset_id(
            identity_kind="SEGMENT",
            config=config,
            contract=contract,
            partition=segment.partition,
            first_trade_date=segment.first_trade_date,
            last_trade_date=segment.last_trade_date,
            source_ids=segment.source_ids,
            bar_digest=_bar_digest(segment.bars),
            preceding_missing_bar_count=segment.preceding_missing_bar_count,
        )
        if segment.segment_id != expected_segment_id:
            raise ValueError("segment_id does not match canonical segment evidence")
        total_count += len(segment.bars)
        total_volume += sum(bar.volume for bar in segment.bars)
        if segment.partition is GCSegmentPartition.DEVELOPMENT:
            development_count += len(segment.bars)
        else:
            oos_count += len(segment.bars)
    if total_count != manifest.eligible_row_count:
        raise ValueError("manifest eligible count does not match segments")
    if development_count != manifest.development_bar_count or oos_count != manifest.oos_bar_count:
        raise ValueError("manifest partition count mismatch")
    if total_volume != manifest.eligible_volume:
        raise ValueError("manifest volume does not match segment bars")
    if dataset.segments:
        first = _normalize_timestamp(dataset.segments[0].bars[0].timestamp, "first bar")
        last = _normalize_timestamp(dataset.segments[-1].bars[-1].timestamp, "last bar")
        if manifest.usable_start_timestamp is None or manifest.usable_end_timestamp is None:
            raise ValueError("non-empty dataset requires usable timestamp bounds")
        if first != _normalize_timestamp(manifest.usable_start_timestamp, "usable start"):
            raise ValueError("usable start timestamp mismatch")
        if last != _normalize_timestamp(manifest.usable_end_timestamp, "usable end"):
            raise ValueError("usable end timestamp mismatch")


def _source_bar_digest(config: GCDatasetBuildConfig, dataset: GCDatasetBuildResult) -> str:
    return _canonical_hash(
        {
            "dataset_id": dataset.dataset_id,
            "dataset_config": _dataset_config_payload(config),
            "segments": tuple(
                {
                    "segment_id": segment.segment_id,
                    "contract": segment.contract.upper(),
                    "partition": segment.partition.value,
                    "first_trade_date": segment.first_trade_date.isoformat(),
                    "last_trade_date": segment.last_trade_date.isoformat(),
                    "source_ids": segment.source_ids,
                    "preceding_missing_bar_count": segment.preceding_missing_bar_count,
                    "bars": tuple(_bar_payload(bar) for bar in segment.bars),
                }
                for segment in dataset.segments
            ),
        }
    )


def _swing_key(swing: DealingRangeSwing) -> tuple[object, ...]:
    return (
        swing.provenance.confirmation_index,
        swing.provenance.confirmation_timestamp,
        swing.provenance.source_indices[0],
        swing.side.value,
        swing.swing_id,
    )


def _discover_swings(
    segment: GCCanonicalContractSegment,
    instrument: str,
    timeframe: str,
) -> tuple[tuple[DealingRangeSwing, ...], tuple[EqualLiquiditySwing, ...]]:
    dealing: list[DealingRangeSwing] = []
    equal: list[EqualLiquiditySwing] = []
    bars = segment.bars
    for index in range(2, len(bars) - 2):
        center = bars[index]
        neighbors = bars[index - 2 : index] + bars[index + 1 : index + 3]
        is_high = all(center.high_tick > item.high_tick for item in neighbors)
        is_low = all(center.low_tick < item.low_tick for item in neighbors)
        if not is_high and not is_low:
            continue
        if is_high and is_low:
            high_prominence = center.high_tick - max(item.high_tick for item in neighbors)
            low_prominence = min(item.low_tick for item in neighbors) - center.low_tick
            side = DealingRangeSwingSide.HIGH if high_prominence > low_prominence else DealingRangeSwingSide.LOW
        else:
            side = DealingRangeSwingSide.HIGH if is_high else DealingRangeSwingSide.LOW
        price_tick = center.high_tick if side is DealingRangeSwingSide.HIGH else center.low_tick
        confirmation = bars[index + 2]
        provenance = SMCV2EventProvenance(
            source_indices=(index,),
            source_timestamps=(center.timestamp,),
            confirmation_index=index + 2,
            confirmation_timestamp=confirmation.timestamp,
        )
        equal_side = EqualLiquiditySide(side.value)
        swing_id = make_equal_liquidity_id(
            identity_kind="SWING",
            instrument=instrument,
            timeframe=timeframe,
            side=equal_side,
            source_indices=(index,),
            reference_tick=price_tick,
            lower_tick=price_tick,
            upper_tick=price_tick,
        )
        dealing.append(DealingRangeSwing(side, price_tick, provenance, swing_id))
        equal.append(EqualLiquiditySwing(equal_side, price_tick, provenance, swing_id))
    pairs = sorted(zip(dealing, equal), key=lambda item: _swing_key(item[0]))
    return tuple(item[0] for item in pairs), tuple(item[1] for item in pairs)


def _latest_protected(
    swings: tuple[DealingRangeSwing, ...],
    direction: SMCV2Direction,
    index: int,
    timestamp: datetime,
) -> DealingRangeSwing | None:
    required_side = DealingRangeSwingSide.LOW if direction is SMCV2Direction.BULLISH else DealingRangeSwingSide.HIGH
    eligible = tuple(
        swing
        for swing in swings
        if swing.side is required_side
        and swing.provenance.confirmation_index < index
        and swing.provenance.confirmation_timestamp < timestamp
    )
    return max(eligible, key=_swing_key) if eligible else None


def _source_index(swing: DealingRangeSwing) -> int:
    return swing.provenance.source_indices[0]


def _replacement_protected(
    swings: tuple[DealingRangeSwing, ...],
    *,
    direction: SMCV2Direction,
    construction_index: int,
    event_index: int,
    low_tick: int,
    high_tick: int,
) -> DealingRangeSwing | None:
    required_side = (
        DealingRangeSwingSide.LOW
        if direction is SMCV2Direction.BULLISH
        else DealingRangeSwingSide.HIGH
    )
    eligible = tuple(
        swing
        for swing in swings
        if swing.side is required_side
        and _source_index(swing) > construction_index
        and swing.provenance.confirmation_index > construction_index
        and swing.provenance.confirmation_index < event_index
        and low_tick < swing.price_tick < high_tick
    )
    if not eligible:
        return None
    greatest_source = max(_source_index(swing) for swing in eligible)
    latest = tuple(
        swing for swing in eligible if _source_index(swing) == greatest_source
    )
    greatest_confirmation = max(
        swing.provenance.confirmation_index for swing in latest
    )
    latest = tuple(
        swing
        for swing in latest
        if swing.provenance.confirmation_index == greatest_confirmation
    )
    return min(latest, key=lambda swing: swing.swing_id)


def _active_boundaries(
    bars_by_index: dict[int, GCChronologicalBar],
    *,
    direction: SMCV2Direction,
    protected_swing: DealingRangeSwing,
    event_index: int,
) -> tuple[int, int]:
    start_index = _source_index(protected_swing)
    rows = tuple(
        bars_by_index[index]
        for index in range(start_index, event_index + 1)
        if index in bars_by_index
    )
    if len(rows) != event_index - start_index + 1:
        raise ValueError("active range source interval is incomplete")
    if direction is SMCV2Direction.BULLISH:
        low_tick = protected_swing.price_tick
        high_tick = max(row.high_tick for row in rows)
    else:
        low_tick = min(row.low_tick for row in rows)
        high_tick = protected_swing.price_tick
    if low_tick >= high_tick:
        raise ValueError("active range must have positive width")
    return low_tick, high_tick


def _select_crossed(
    crossed: tuple[DealingRangeSwing, ...], direction: SMCV2Direction
) -> DealingRangeSwing:
    if direction is SMCV2Direction.BULLISH:
        price = max(item.price_tick for item in crossed)
    else:
        price = min(item.price_tick for item in crossed)
    same_price = tuple(item for item in crossed if item.price_tick == price)
    return max(
        same_price,
        key=lambda item: (
            item.provenance.source_indices[0],
            item.provenance.confirmation_index,
            item.provenance.confirmation_timestamp,
            _swing_key(item),
        ),
    )


def _fvg_boundaries(bars: tuple[object, ...], end_index: int, direction: SMCV2Direction) -> SMCV2TickRange | None:
    if end_index < 2:
        return None
    first, middle, third = bars[end_index - 2 : end_index + 1]
    middle_range = middle.high_tick - middle.low_tick
    if middle_range <= 0 or 5 * abs(middle.close_tick - middle.open_tick) < 3 * middle_range:
        return None
    if direction is SMCV2Direction.BULLISH:
        if third.low_tick - first.high_tick < 2:
            return None
        return SMCV2TickRange(first.high_tick, third.low_tick)
    if first.low_tick - third.high_tick < 2:
        return None
    return SMCV2TickRange(third.high_tick, first.low_tick)


def _discover_events_and_links(
    *,
    segment: GCCanonicalContractSegment,
    swings: tuple[DealingRangeSwing, ...],
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    source_bar_digest: str,
    config: GCStructuralSeedConfig,
) -> tuple[tuple[DealingRangeStructureEvent, ...], tuple[FairValueGapContextLink, ...]]:
    events: list[DealingRangeStructureEvent] = []
    links: list[FairValueGapContextLink] = []
    retired_high: set[str] = set()
    retired_low: set[str] = set()
    active_direction: SMCV2Direction | None = None
    protected_swing: DealingRangeSwing | None = None
    active_construction_index: int | None = None
    active_low_tick: int | None = None
    active_high_tick: int | None = None
    bars_by_index = {bar.index: bar for bar in segment.bars}
    for bar in segment.bars:
        confirmed = tuple(
            swing
            for swing in swings
            if swing.provenance.confirmation_index < bar.index
            and swing.provenance.confirmation_timestamp < bar.timestamp
        )
        crossed_high = tuple(
            swing
            for swing in confirmed
            if swing.side is DealingRangeSwingSide.HIGH
            and swing.swing_id not in retired_high
            and bar.close_tick >= swing.price_tick + 1
        )
        crossed_low = tuple(
            swing
            for swing in confirmed
            if swing.side is DealingRangeSwingSide.LOW
            and swing.swing_id not in retired_low
            and bar.close_tick <= swing.price_tick - 1
        )
        if crossed_high and crossed_low:
            # A canonical raw bar cannot retain two independently valid opposing
            # breaks at one complete effective moment.  If upstream causal
            # retirement did not already remove one side, the evidence is
            # contradictory rather than a candidate-selection ambiguity.
            raise ValueError("contradictory opposing structural breaks")
        if not crossed_high and not crossed_low:
            continue
        direction = SMCV2Direction.BULLISH if crossed_high else SMCV2Direction.BEARISH
        crossed = crossed_high if crossed_high else crossed_low
        latest = _latest_protected(swings, direction, bar.index, bar.timestamp)
        if active_direction is None:
            if latest is None:
                if direction is SMCV2Direction.BULLISH:
                    retired_high.update(item.swing_id for item in crossed)
                else:
                    retired_low.update(item.swing_id for item in crossed)
                continue
            selected = _select_crossed(crossed, direction)
            event_type = DealingRangeEventType.BOS
            next_protected = latest
            next_construction_index = bar.index
            next_low_tick, next_high_tick = _active_boundaries(
                bars_by_index,
                direction=direction,
                protected_swing=next_protected,
                event_index=bar.index,
            )
        elif direction is active_direction:
            if (
                protected_swing is None
                or active_construction_index is None
                or active_low_tick is None
                or active_high_tick is None
            ):
                raise _StructuralUnknown("initialized active range state is incomplete")
            selected = _select_crossed(crossed, direction)
            event_type = DealingRangeEventType.BOS
            replacement = _replacement_protected(
                swings,
                direction=direction,
                construction_index=active_construction_index,
                event_index=bar.index,
                low_tick=active_low_tick,
                high_tick=active_high_tick,
            )
            if replacement is not None:
                next_protected = replacement
                next_construction_index = bar.index
                next_low_tick, next_high_tick = _active_boundaries(
                    bars_by_index,
                    direction=direction,
                    protected_swing=replacement,
                    event_index=bar.index,
                )
            else:
                next_protected = protected_swing
                next_construction_index = active_construction_index
                interval_low, interval_high = _active_boundaries(
                    bars_by_index,
                    direction=direction,
                    protected_swing=protected_swing,
                    event_index=bar.index,
                )
                if direction is SMCV2Direction.BULLISH:
                    next_low_tick = active_low_tick
                    next_high_tick = max(active_high_tick, interval_high)
                else:
                    next_low_tick = min(active_low_tick, interval_low)
                    next_high_tick = active_high_tick
        else:
            if protected_swing is None:
                raise _StructuralUnknown("an initialized direction has no active protected swing")
            protected_matches = tuple(
                item for item in crossed if item.swing_id == protected_swing.swing_id
            )
            if not protected_matches:
                if direction is SMCV2Direction.BULLISH:
                    retired_high.update(item.swing_id for item in crossed)
                else:
                    retired_low.update(item.swing_id for item in crossed)
                continue
            if len(protected_matches) != 1:
                raise ValueError("duplicate active protected swing in crossed group")
            if latest is None:
                raise _StructuralUnknown("a required protected swing is not yet confirmed")
            selected = protected_matches[0]
            event_type = DealingRangeEventType.CHOCH
            next_protected = latest
            next_construction_index = bar.index
            next_low_tick, next_high_tick = _active_boundaries(
                bars_by_index,
                direction=direction,
                protected_swing=next_protected,
                event_index=bar.index,
            )
        if direction is SMCV2Direction.BULLISH:
            retired_high.update(item.swing_id for item in crossed)
        else:
            retired_low.update(item.swing_id for item in crossed)
        provenance = SMCV2EventProvenance(
            source_indices=(bar.index,),
            source_timestamps=(bar.timestamp,),
            confirmation_index=bar.index,
            confirmation_timestamp=bar.timestamp,
        )
        event_id = make_dealing_range_id(
            identity_kind="EVENT",
            instrument=instrument,
            timeframe=timeframe,
            direction=direction,
            source_indices=(bar.index,),
            event_type=event_type,
            broken_swing_id=selected.swing_id,
            confirmation_index=bar.index,
            boundaries=SMCV2TickRange(selected.price_tick, selected.price_tick),
        )
        event = DealingRangeStructureEvent(direction, event_type, selected.swing_id, provenance, event_id)
        events.append(event)
        active_direction = direction
        protected_swing = next_protected
        active_construction_index = next_construction_index
        active_low_tick = next_low_tick
        active_high_tick = next_high_tick
        boundaries = _fvg_boundaries(segment.bars, bar.index, direction)
        if boundaries is not None:
            source_indices = (bar.index - 2, bar.index - 1, bar.index)
            source_timestamps = tuple(segment.bars[item].timestamp for item in source_indices)
            displacement_start = segment.bars[source_indices[0]]
            if (
                selected.provenance.confirmation_index >= displacement_start.index
                or selected.provenance.confirmation_timestamp >= displacement_start.timestamp
            ):
                boundaries = None
        if boundaries is not None:
            displacement_id = make_gc_structural_seed_id(
                identity_kind=GCStructuralSeedIdentityKind.DISPLACEMENT,
                instrument=instrument,
                timeframe=timeframe,
                tick_size=tick_size,
                dataset_id=dataset_id,
                seed_version=GC_STRUCTURAL_SEED_VERSION,
                config=config,
                source_bar_digest=source_bar_digest,
                segment_id=segment.segment_id,
                direction=direction,
                source_indices=source_indices,
                source_timestamps=source_timestamps,
                boundaries=boundaries,
                structure_event_id=event_id,
            )
            links.append(
                FairValueGapContextLink(
                    bar.index,
                    _normalize_timestamp(bar.timestamp, "formation timestamp"),
                    displacement_id,
                    event_id,
                    event_type,
                )
            )
    return tuple(events), tuple(links)


def _provenance_payload(value: SMCV2EventProvenance) -> dict[str, object]:
    return {
        "source_indices": value.source_indices,
        "source_timestamps": tuple(_timestamp_text(item) for item in value.source_timestamps),
        "confirmation_index": value.confirmation_index,
        "confirmation_timestamp": _timestamp_text(value.confirmation_timestamp),
    }


def _segment_evidence_digest(evidence: _SegmentEvidence) -> str:
    return _canonical_hash(
        {
            "segment_id": evidence.segment.segment_id,
            "dealing_range_swings": tuple(
                {
                    "side": item.side.value,
                    "price_tick": item.price_tick,
                    "provenance": _provenance_payload(item.provenance),
                    "swing_id": item.swing_id,
                }
                for item in evidence.dealing_swings
            ),
            "equal_liquidity_swings": tuple(
                {
                    "side": item.side.value,
                    "price_tick": item.price_tick,
                    "provenance": _provenance_payload(item.provenance),
                    "swing_id": item.swing_id,
                }
                for item in evidence.equal_swings
            ),
            "structure_events": tuple(
                {
                    "direction": item.direction.value,
                    "event_type": item.event_type.value,
                    "broken_swing_id": item.broken_swing_id,
                    "provenance": _provenance_payload(item.provenance),
                    "event_id": item.event_id,
                }
                for item in evidence.events
            ),
            "fair_value_gap_context_links": tuple(
                {
                    "formation_end_index": item.formation_end_index,
                    "formation_end_timestamp": _timestamp_text(item.formation_end_timestamp),
                    "displacement_id": item.displacement_id,
                    "structure_event_id": item.structure_event_id,
                    "structure_event_type": item.structure_event_type.value if item.structure_event_type else None,
                }
                for item in evidence.links
            ),
        }
    )


def build_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult:
    """Derive immutable segment-local public structural evidence."""

    try:
        normalized_dataset_config = _validate_dataset_config(dataset_config)
        _config_payload(config)
    except (TypeError, ValueError):
        return _invalid("INVALID_CONFIG")
    if dataset is None:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_DATASET")
    if type(dataset) is not GCDatasetBuildResult or not isinstance(dataset.status, GCDatasetBuildStatus):
        return _invalid("INVALID_DATASET")
    mapped = {
        GCDatasetBuildStatus.INVALID: (SMCV2PrimitiveStatus.INVALID, "INVALID_DATASET"),
        GCDatasetBuildStatus.AMBIGUOUS: (SMCV2PrimitiveStatus.AMBIGUOUS, "DATASET_AMBIGUOUS"),
        GCDatasetBuildStatus.UNKNOWN: (SMCV2PrimitiveStatus.UNKNOWN, "DATASET_UNKNOWN"),
        GCDatasetBuildStatus.NONE: (SMCV2PrimitiveStatus.NONE, "DATASET_NONE"),
    }
    if dataset.status in mapped:
        status, reason = mapped[dataset.status]
        return _invalid(reason) if status is SMCV2PrimitiveStatus.INVALID else _blocked(status, reason) if status in (SMCV2PrimitiveStatus.AMBIGUOUS, SMCV2PrimitiveStatus.UNKNOWN) else GCStructuralSeedResult(status, reasons=(reason,))
    try:
        _validate_valid_dataset(normalized_dataset_config, dataset)
        source_digest = _source_bar_digest(normalized_dataset_config, dataset)
        instrument = normalized_dataset_config.instrument.upper()
        timeframe = normalized_dataset_config.timeframe.upper()
        evidence_by_segment: list[_SegmentEvidence] = []
        all_dealing: list[DealingRangeSwing] = []
        all_equal: list[EqualLiquiditySwing] = []
        all_events: list[DealingRangeStructureEvent] = []
        all_links: list[FairValueGapContextLink] = []
        for segment in dataset.segments:
            if segment.partition is GCSegmentPartition.DEVELOPMENT:
                dealing, equal = _discover_swings(segment, instrument, timeframe)
                events, links = _discover_events_and_links(
                    segment=segment,
                    swings=dealing,
                    instrument=instrument,
                    timeframe=timeframe,
                    tick_size=normalized_dataset_config.tick_size,
                    dataset_id=dataset.dataset_id,
                    source_bar_digest=source_digest,
                    config=config,
                )
            else:
                dealing = equal = events = links = ()
            item = _SegmentEvidence(segment, dealing, equal, events, links)
            evidence_by_segment.append(item)
            all_dealing.extend(dealing)
            all_equal.extend(equal)
            all_events.extend(events)
            all_links.extend(links)
        segment_digests = tuple(
            (item.segment.segment_id, _segment_evidence_digest(item)) for item in evidence_by_segment
        )
        if not segment_digests:
            # A VALID manifest may be empty only as a deliberately empty canonical
            # scope.  Bind that state without inventing a pseudo segment.
            segment_digests = ((dataset.dataset_id, _canonical_hash(())),)
        seed_id = make_gc_structural_seed_id(
            identity_kind=GCStructuralSeedIdentityKind.SEED,
            instrument=instrument,
            timeframe=timeframe,
            tick_size=normalized_dataset_config.tick_size,
            dataset_id=dataset.dataset_id,
            seed_version=GC_STRUCTURAL_SEED_VERSION,
            config=config,
            source_bar_digest=source_digest,
            segment_evidence_digests=segment_digests,
        )
        seed = GCCanonicalSeedEvidence(
            seed_id,
            GC_STRUCTURAL_SEED_VERSION,
            instrument,
            timeframe,
            dataset.dataset_id,
            source_digest,
            tuple(all_dealing),
            tuple(all_equal),
            tuple(all_events),
            tuple(all_links),
        )
        has_evidence = bool(all_dealing or all_equal or all_events or all_links)
        if has_evidence:
            return GCStructuralSeedResult(
                SMCV2PrimitiveStatus.VALID,
                seed,
                ("STRUCTURAL_EVIDENCE_VALID",),
            )
        return GCStructuralSeedResult(
            SMCV2PrimitiveStatus.NONE,
            seed,
            ("NO_STRUCTURAL_EVIDENCE",),
        )
    except _StructuralUnknown:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "STRUCTURE_UNKNOWN")
    except (TypeError, ValueError, InvalidOperation, ArithmeticError):
        return _invalid()
    except Exception:  # pragma: no cover - containment boundary
        return _invalid()


def validate_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult:
    """Re-derive and byte-for-byte validate one supplied canonical seed."""

    expected = build_gc_structural_seed_evidence(
        dataset_config=dataset_config,
        dataset=dataset,
        config=config,
    )
    if expected.status in (
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    ):
        return expected
    if dataset is not None and isinstance(dataset, GCDatasetBuildResult) and dataset.status is GCDatasetBuildStatus.NONE:
        return expected
    if structural_seed is None:
        return _blocked(SMCV2PrimitiveStatus.UNKNOWN, "MISSING_STRUCTURAL_SEED")
    if type(structural_seed) is not GCCanonicalSeedEvidence or structural_seed != expected.seed:
        return _invalid()
    return expected


__all__ = [
    "GC_STRUCTURAL_SEED_VERSION",
    "GCStructuralSeedIdentityKind",
    "GCStructuralSeedConfig",
    "GCCanonicalSeedEvidence",
    "GCStructuralSeedResult",
    "make_gc_structural_seed_id",
    "build_gc_structural_seed_evidence",
    "validate_gc_structural_seed_evidence",
]
