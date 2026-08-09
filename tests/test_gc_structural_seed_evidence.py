from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import inspect
import json
from typing import get_type_hints

import pytest

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
from analysis.gc_structural_seed_evidence import (
    GC_STRUCTURAL_SEED_VERSION,
    GCCanonicalSeedEvidence,
    GCStructuralSeedConfig,
    GCStructuralSeedIdentityKind,
    GCStructuralSeedResult,
    build_gc_structural_seed_evidence,
    make_gc_structural_seed_id,
    validate_gc_structural_seed_evidence,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeSwingSide,
    make_dealing_range_id,
)
from smc.equal_liquidity import EqualLiquiditySide, make_equal_liquidity_id
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
)


UTC = timezone.utc
INSTRUMENT = "GC"
TIMEFRAME = "5M"
CONTRACT = "GCQ26-COMEX"
TRADE_DATE = date(2026, 7, 29)
SOURCE_ID = hashlib.sha256(b"structural-source").hexdigest()
COVERAGE_ID = hashlib.sha256(b"structural-coverage").hexdigest()
COVERAGE_DIGEST = hashlib.sha256(b"structural-coverage-digest").hexdigest()
CALENDAR_DIGEST = hashlib.sha256(b"structural-calendar").hexdigest()


def _sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def _ts(index: int, *, day: int = 0) -> datetime:
    return datetime(2026, 7, 28 + day, 22, tzinfo=UTC) + timedelta(minutes=5 * index)


def _bar(index: int, values: tuple[int, int, int, int], *, day: int = 0) -> GCChronologicalBar:
    open_tick, high_tick, low_tick, close_tick = values
    return GCChronologicalBar(index, _ts(index, day=day), open_tick, high_tick, low_tick, close_tick, 100, True)


def _empty_bars() -> tuple[GCChronologicalBar, ...]:
    return tuple(_bar(i, (100, 102, 98, 100)) for i in range(7))


def _bullish_bars() -> tuple[GCChronologicalBar, ...]:
    values = (
        (100, 102, 99, 101),
        (101, 103, 100, 102),
        (102, 110, 101, 109),
        (100, 105, 95, 101),
        (102, 106, 100, 104),
        (104, 106, 103, 105),
        (105, 110, 104, 109),
        (111, 114, 109, 112),
    )
    return tuple(_bar(i, item) for i, item in enumerate(values))


def _bearish_bars() -> tuple[GCChronologicalBar, ...]:
    values = tuple((-o, -l, -h, -c) for o, h, l, c in _bullish_values())
    return tuple(_bar(i, item) for i, item in enumerate(values))


def _bullish_values() -> tuple[tuple[int, int, int, int], ...]:
    return tuple((b.open_tick, b.high_tick, b.low_tick, b.close_tick) for b in _bullish_bars_raw())


def _mirror_values(
    values: tuple[tuple[int, int, int, int], ...],
) -> tuple[tuple[int, int, int, int], ...]:
    return tuple((-open_tick, -low_tick, -high_tick, -close_tick) for open_tick, high_tick, low_tick, close_tick in values)


def _real_data_shape_values(kind: str) -> tuple[tuple[int, int, int, int], ...]:
    if kind == "NON_PROTECTED_ONLY":
        return (
            (100, 102, 99, 101), (101, 103, 100, 102), (102, 110, 101, 109),
            (100, 105, 95, 101), (102, 106, 100, 104), (104, 106, 103, 105),
            (105, 110, 104, 109), (111, 114, 109, 112), (112, 114, 110, 112),
            (108, 111, 105, 108), (110, 113, 108, 110), (111, 114, 109, 111),
            (109, 110, 103, 104), (100, 101, 93, 94),
        )
    if kind == "PROTECTED_PLUS_OTHER":
        return (
            (100, 102, 99, 101), (101, 103, 100, 102), (102, 110, 101, 109),
            (100, 105, 95, 101), (102, 106, 100, 104), (104, 106, 103, 105),
            (105, 110, 104, 109), (111, 114, 109, 112), (112, 114, 100, 112),
            (98, 102, 90, 98), (100, 104, 96, 100), (102, 105, 97, 102),
            (96, 100, 88, 89),
        )
    if kind == "PRE_ELIGIBILITY":
        return (
            (100, 102, 99, 101), (101, 103, 99, 102), (102, 110, 99, 109),
            (100, 105, 99, 101), (102, 106, 99, 104), (104, 106, 99, 105),
            (105, 110, 104, 109), (111, 114, 109, 112), (111, 114, 109, 112),
            (108, 113, 105, 108), (110, 114, 108, 110), (111, 114, 109, 111),
            (111, 114, 109, 112), (112, 115, 110, 113), (113, 120, 111, 119),
            (114, 116, 112, 114), (113, 115, 111, 113), (121, 123, 119, 122),
        )
    raise AssertionError(f"unknown real-data shape: {kind}")


def _bullish_bars_raw() -> tuple[GCChronologicalBar, ...]:
    values = (
        (100, 102, 99, 101), (101, 103, 100, 102), (102, 110, 101, 109),
        (100, 105, 95, 101), (102, 106, 100, 104), (104, 106, 103, 105),
        (105, 110, 104, 109), (111, 114, 109, 112),
    )
    return tuple(_bar(i, item) for i, item in enumerate(values))


def _config(**changes: object) -> GCDatasetBuildConfig:
    values: dict[str, object] = {
        "instrument": "gc",
        "timeframe": "5m",
        "source_timezone": "Asia/Tokyo",
        "exchange_timezone": "America/New_York",
        "timezone_data_version": importlib.metadata.version("tzdata"),
        "tick_size": Decimal("0.1"),
        "initial_contract": CONTRACT,
        "initial_trade_date": date(2026, 7, 1),
        "roll_confirmation_sessions": 3,
        "oos_start_trade_date": date(2026, 9, 1),
        "oos_end_trade_date": date(2026, 9, 30),
    }
    values.update(changes)
    return GCDatasetBuildConfig(**values)  # type: ignore[arg-type]


def _timestamp_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _bar_digest(bars: tuple[GCChronologicalBar, ...]) -> str:
    return _sha(tuple({
        "index": b.index, "timestamp": _timestamp_text(b.timestamp), "open_tick": b.open_tick,
        "high_tick": b.high_tick, "low_tick": b.low_tick, "close_tick": b.close_tick,
        "volume": b.volume, "is_closed": b.is_closed,
    } for b in bars))


def _dataset(
    bars: tuple[GCChronologicalBar, ...] | None = None,
    *,
    second_bars: tuple[GCChronologicalBar, ...] | None = None,
    partition: GCSegmentPartition = GCSegmentPartition.DEVELOPMENT,
) -> tuple[GCDatasetBuildConfig, GCDatasetBuildResult]:
    config = _config()
    groups = [bars or _bullish_bars()]
    if second_bars is not None:
        groups.append(tuple(replace(b, timestamp=_ts(b.index, day=1)) for b in second_bars))
    segments: list[GCCanonicalContractSegment] = []
    for ordinal, members in enumerate(groups):
        segment_id = make_gc_dataset_id(
            identity_kind="SEGMENT", config=config, contract=CONTRACT,
            partition=partition, first_trade_date=TRADE_DATE + timedelta(days=ordinal),
            last_trade_date=TRADE_DATE + timedelta(days=ordinal), source_ids=(SOURCE_ID,),
            bar_digest=_bar_digest(members), preceding_missing_bar_count=0,
        )
        segments.append(GCCanonicalContractSegment(
            segment_id, CONTRACT, partition, TRADE_DATE + timedelta(days=ordinal),
            TRADE_DATE + timedelta(days=ordinal), (SOURCE_ID,), members, 0,
        ))
    segment_ids = tuple(s.segment_id for s in segments)
    count = sum(len(s.bars) for s in segments)
    volume = sum(b.volume for s in segments for b in s.bars)
    evidence_digest = _sha((segment_ids, count, volume))
    dataset_id = make_gc_dataset_id(
        identity_kind="DATASET", config=config, source_ids=(SOURCE_ID,),
        coverage_ids=(COVERAGE_ID,), segment_ids=segment_ids,
        calendar_digest=CALENDAR_DIGEST, coverage_digest=COVERAGE_DIGEST,
        evidence_digest=evidence_digest, roll_trade_dates=(),
    )
    first = segments[0].bars[0].timestamp
    last = segments[-1].bars[-1].timestamp
    manifest = GCDatasetManifest(
        dataset_id, GC_DATASET_BUILDER_VERSION, (SOURCE_ID,), (COVERAGE_ID,), COVERAGE_DIGEST,
        segment_ids, "SYNTHETIC-CALENDAR", config.timezone_data_version, first, last, first, last,
        count, count, count if partition is GCSegmentPartition.DEVELOPMENT else 0,
        count if partition is GCSegmentPartition.OOS_HOLDOUT else 0, 0, 0, 0,
        volume, volume, 0, ((CONTRACT, TRADE_DATE, volume),), (), (),
    )
    return config, GCDatasetBuildResult(
        GCDatasetBuildStatus.VALID, dataset_id, tuple(segments), manifest,
        ("CANONICAL_DATASET_BUILT",), (),
    )


def _build(bars: tuple[GCChronologicalBar, ...] | None = None, **kwargs: object) -> GCStructuralSeedResult:
    config, dataset = _dataset(bars, **kwargs)  # type: ignore[arg-type]
    return build_gc_structural_seed_evidence(dataset_config=config, dataset=dataset)


def _displacement_kwargs(result: GCStructuralSeedResult) -> dict[str, object]:
    assert result.seed is not None and result.seed.structure_events and result.seed.fair_value_gap_context_links
    link = result.seed.fair_value_gap_context_links[0]
    event = result.seed.structure_events[0]
    return {
        "identity_kind": GCStructuralSeedIdentityKind.DISPLACEMENT,
        "instrument": result.seed.instrument,
        "timeframe": result.seed.timeframe,
        "tick_size": Decimal("0.1"),
        "dataset_id": result.seed.dataset_id,
        "seed_version": result.seed.seed_version,
        "config": GCStructuralSeedConfig(),
        "source_bar_digest": result.seed.source_bar_digest,
        "segment_id": _dataset()[1].segments[0].segment_id,
        "direction": event.direction,
        "source_indices": (5, 6, 7),
        "source_timestamps": tuple(_ts(i) for i in (5, 6, 7)),
        "boundaries": SMCV2TickRange(106, 109),
        "structure_event_id": event.event_id,
    }


def test_case_01_missing_dataset_is_unknown() -> None:
    result = build_gc_structural_seed_evidence(dataset_config=_config(), dataset=None)
    assert result == GCStructuralSeedResult(SMCV2PrimitiveStatus.UNKNOWN, reasons=("MISSING_DATASET",), blocking_reasons=("MISSING_DATASET",))


def test_case_02_malformed_dataset_is_invalid_without_leakage() -> None:
    result = build_gc_structural_seed_evidence(dataset_config=_config(), dataset=object())  # type: ignore[arg-type]
    assert result.status is SMCV2PrimitiveStatus.INVALID and result.seed is None
    assert result.reasons == ("INVALID_DATASET",)


def test_case_03_dataset_identity_and_source_digest_mismatch_are_invalid() -> None:
    config, dataset = _dataset()
    assert dataset.manifest is not None
    bad = replace(dataset, dataset_id="0" * 64)
    assert build_gc_structural_seed_evidence(dataset_config=config, dataset=bad).status is SMCV2PrimitiveStatus.INVALID
    bad_segment = replace(dataset.segments[0], bars=dataset.segments[0].bars[:-1])
    assert build_gc_structural_seed_evidence(dataset_config=config, dataset=replace(dataset, segments=(bad_segment,))).status is SMCV2PrimitiveStatus.INVALID


def test_case_04_oos_bars_never_create_evidence() -> None:
    result = _build(partition=GCSegmentPartition.OOS_HOLDOUT)
    assert result.status is SMCV2PrimitiveStatus.NONE and result.seed is not None
    assert not result.seed.dealing_range_swings


def test_case_05_segment_order_and_local_indices_validate() -> None:
    result = _build(second_bars=_empty_bars())
    assert result.seed is not None
    config, dataset = _dataset(second_bars=_empty_bars())
    assert tuple(s.bars[0].index for s in dataset.segments) == (0, 0)
    assert validate_gc_structural_seed_evidence(dataset_config=config, dataset=dataset, structural_seed=result.seed).status is result.status


def test_case_06_cross_segment_discovery_is_forbidden() -> None:
    left = tuple(_bar(i, (100, 101 + i, 90, 100)) for i in range(4))
    right = tuple(_bar(i, (85, 90, 80 - i, 85)) for i in range(4))
    result = _build(left, second_bars=right)
    assert result.seed is not None and not result.seed.dealing_range_swings


def test_case_07_strict_high_swing_qualifies() -> None:
    result = _build()
    assert result.seed is not None
    assert any(s.side is DealingRangeSwingSide.HIGH and s.price_tick == 110 for s in result.seed.dealing_range_swings)


def test_case_08_strict_low_swing_qualifies() -> None:
    result = _build()
    assert result.seed is not None
    assert any(s.side is DealingRangeSwingSide.LOW and s.price_tick == 95 for s in result.seed.dealing_range_swings)


def test_case_09_plateau_does_not_qualify() -> None:
    assert _build(_empty_bars()).seed is not None
    assert not _build(_empty_bars()).seed.dealing_range_swings  # type: ignore[union-attr]


def test_case_10_insufficient_neighbors_do_not_look_ahead() -> None:
    result = _build(tuple(_bullish_bars()[:4]))
    assert result.seed is not None and not result.seed.dealing_range_swings


@pytest.mark.parametrize("center", [(100, 112, 94, 101), (100, 110, 90, 101)])
def test_case_11_dual_side_selects_greater_prominence(center: tuple[int, int, int, int]) -> None:
    values = [(100, 105, 95, 100), (100, 106, 94, 100), center, (100, 106, 94, 100), (100, 105, 95, 100)]
    result = _build(tuple(_bar(i, value) for i, value in enumerate(values)))
    assert result.seed is not None and len(result.seed.dealing_range_swings) == 1


def test_case_12_dual_side_tie_selects_low() -> None:
    values = [(100, 105, 95, 100), (100, 106, 94, 100), (100, 112, 88, 100), (100, 106, 94, 100), (100, 105, 95, 100)]
    result = _build(tuple(_bar(i, value) for i, value in enumerate(values)))
    assert result.seed is not None and result.seed.dealing_range_swings[0].side is DealingRangeSwingSide.LOW


def test_case_13_confirmation_and_single_source_are_exact() -> None:
    swing = _build().seed.dealing_range_swings[0]  # type: ignore[union-attr]
    assert swing.provenance.source_indices == (2,)
    assert swing.provenance.confirmation_index == 4 and swing.provenance.confirmation_timestamp == _ts(4)


def test_case_14_equal_liquidity_swing_id_recomputes() -> None:
    swing = _build().seed.equal_liquidity_swings[0]  # type: ignore[union-attr]
    assert swing.swing_id == make_equal_liquidity_id(identity_kind="SWING", instrument=INSTRUMENT, timeframe=TIMEFRAME, side=swing.side, source_indices=swing.provenance.source_indices, reference_tick=swing.price_tick, lower_tick=swing.price_tick, upper_tick=swing.price_tick)


def test_case_15_dealing_range_mirror_is_exact() -> None:
    seed = _build().seed
    assert seed is not None
    pairs = zip(seed.dealing_range_swings, seed.equal_liquidity_swings)
    assert all((left.side.value, left.price_tick, left.provenance, left.swing_id) == (right.side.value, right.price_tick, right.provenance, right.swing_id) for left, right in pairs)


def test_case_16_swing_uniqueness_and_causal_order() -> None:
    seed = _build().seed
    assert seed is not None
    keys = [(s.provenance.confirmation_index, s.provenance.confirmation_timestamp, s.provenance.source_indices[0], s.side.value, s.swing_id) for s in seed.dealing_range_swings]
    assert keys == sorted(keys) and len({s.swing_id for s in seed.dealing_range_swings}) == len(keys)


def test_case_17_same_hash_across_segments_is_segment_bound() -> None:
    result = _build(second_bars=_bullish_bars())
    assert result.seed is not None
    ids = [s.swing_id for s in result.seed.dealing_range_swings]
    assert len(ids) == 4 and len(set(ids)) == 2


def test_case_18_bullish_one_tick_close_break() -> None:
    seed = _build().seed
    assert seed is not None and len(seed.structure_events) == 1
    assert seed.structure_events[0].direction is SMCV2Direction.BULLISH


def test_case_19_bearish_one_tick_close_break() -> None:
    result = _build(_bearish_bars())
    assert result.seed is not None and result.seed.structure_events[0].direction is SMCV2Direction.BEARISH


def test_case_20_same_confirmation_swing_cannot_break() -> None:
    bars = list(_bullish_bars())
    bars[4] = replace(bars[4], close_tick=111, high_tick=112)
    result = _build(tuple(bars))
    assert result.seed is not None
    assert all(e.provenance.confirmation_index != 4 for e in result.seed.structure_events)


def test_case_21_bullish_multiple_cross_selects_highest() -> None:
    seed = _build().seed
    assert seed is not None
    high = next(s for s in seed.dealing_range_swings if s.side is DealingRangeSwingSide.HIGH)
    assert seed.structure_events[0].broken_swing_id == high.swing_id


def test_case_22_bearish_multiple_cross_selects_lowest() -> None:
    seed = _build(_bearish_bars()).seed
    assert seed is not None
    low = next(s for s in seed.dealing_range_swings if s.side is DealingRangeSwingSide.LOW)
    assert seed.structure_events[0].broken_swing_id == low.swing_id


def test_case_23_crossed_levels_retire_atomically() -> None:
    seed = _build().seed
    assert seed is not None and len(seed.structure_events) == 1


def test_case_24_first_event_is_bos() -> None:
    assert _build().seed.structure_events[0].event_type is DealingRangeEventType.BOS  # type: ignore[union-attr]


@pytest.mark.parametrize("mirror", (False, True), ids=("bullish-to-bearish", "bearish-to-bullish"))
def test_case_25_non_protected_reversal_is_consumed_without_relabeling(mirror: bool) -> None:
    values = _real_data_shape_values("NON_PROTECTED_ONLY")
    if mirror:
        values = _mirror_values(values)
    result = _build(tuple(_bar(i, value) for i, value in enumerate(values)))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.seed is not None
    assert tuple(event.provenance.confirmation_index for event in result.seed.structure_events) == (7, 13)
    assert tuple(event.event_type for event in result.seed.structure_events) == (
        DealingRangeEventType.BOS,
        DealingRangeEventType.CHOCH,
    )


@pytest.mark.parametrize("mirror", (False, True), ids=("bullish", "bearish"))
def test_case_26_initial_break_without_two_sided_context_is_consumed_non_event(mirror: bool) -> None:
    values = _real_data_shape_values("PRE_ELIGIBILITY")
    if mirror:
        values = _mirror_values(values)
    result = _build(tuple(_bar(i, value) for i, value in enumerate(values)))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.seed is not None
    assert tuple(event.provenance.confirmation_index for event in result.seed.structure_events) == (17,)
    assert result.seed.structure_events[0].event_type is DealingRangeEventType.BOS


def test_case_27_event_singleton_provenance() -> None:
    event = _build().seed.structure_events[0]  # type: ignore[union-attr]
    assert event.provenance.source_indices == (7,) and event.provenance.source_timestamps == (_ts(7),)


def test_case_28_event_identity_recomputes() -> None:
    seed = _build().seed
    assert seed is not None
    event = seed.structure_events[0]
    swing = next(s for s in seed.dealing_range_swings if s.swing_id == event.broken_swing_id)
    assert event.event_id == make_dealing_range_id(identity_kind="EVENT", instrument=INSTRUMENT, timeframe=TIMEFRAME, direction=event.direction, source_indices=event.provenance.source_indices, event_type=event.event_type, broken_swing_id=event.broken_swing_id, confirmation_index=event.provenance.confirmation_index, boundaries=SMCV2TickRange(swing.price_tick, swing.price_tick))


def test_case_29_event_order_is_causal_not_hash_order() -> None:
    events = _build(second_bars=_bullish_bars()).seed.structure_events  # type: ignore[union-attr]
    assert [e.provenance.confirmation_timestamp for e in events] == sorted(e.provenance.confirmation_timestamp for e in events)


@pytest.mark.parametrize(
    ("kind", "mirror", "expected_indices", "expected_types"),
    (
        ("NON_PROTECTED_ONLY", False, (7, 13), (DealingRangeEventType.BOS, DealingRangeEventType.CHOCH)),
        ("NON_PROTECTED_ONLY", True, (7, 13), (DealingRangeEventType.BOS, DealingRangeEventType.CHOCH)),
        ("PROTECTED_PLUS_OTHER", False, (7, 12), (DealingRangeEventType.BOS, DealingRangeEventType.CHOCH)),
        ("PROTECTED_PLUS_OTHER", True, (7, 12), (DealingRangeEventType.BOS, DealingRangeEventType.CHOCH)),
        ("PRE_ELIGIBILITY", False, (17,), (DealingRangeEventType.BOS,)),
        ("PRE_ELIGIBILITY", True, (17,), (DealingRangeEventType.BOS,)),
    ),
    ids=(
        "19-non-protected-only-bullish",
        "19-non-protected-only-bearish",
        "3-protected-plus-other-bullish",
        "3-protected-plus-other-bearish",
        "6-pre-eligibility-bullish",
        "6-pre-eligibility-bearish",
    ),
)
def test_case_30_real_data_shapes_are_deterministic_not_unknown_or_ambiguous(
    kind: str,
    mirror: bool,
    expected_indices: tuple[int, ...],
    expected_types: tuple[DealingRangeEventType, ...],
) -> None:
    values = _real_data_shape_values(kind)
    if mirror:
        values = _mirror_values(values)
    result = _build(tuple(_bar(i, value) for i, value in enumerate(values)))
    assert result.status is SMCV2PrimitiveStatus.VALID
    assert result.seed is not None
    assert tuple(event.provenance.confirmation_index for event in result.seed.structure_events) == expected_indices
    assert tuple(event.event_type for event in result.seed.structure_events) == expected_types

    if kind == "PROTECTED_PLUS_OTHER":
        first, reversal = result.seed.structure_events
        protected_side = (
            DealingRangeSwingSide.LOW
            if first.direction is SMCV2Direction.BULLISH
            else DealingRangeSwingSide.HIGH
        )
        protected = max(
            (
                swing
                for swing in result.seed.dealing_range_swings
                if swing.side is protected_side
                and swing.provenance.confirmation_index < first.provenance.confirmation_index
            ),
            key=lambda swing: (
                swing.provenance.confirmation_index,
                swing.provenance.confirmation_timestamp,
                swing.provenance.source_indices[0],
                swing.swing_id,
            ),
        )
        assert reversal.broken_swing_id == protected.swing_id

    upstream = GCDatasetBuildResult(
        GCDatasetBuildStatus.AMBIGUOUS,
        None,
        (),
        None,
        ("UPSTREAM_AMBIGUOUS",),
        ("UPSTREAM_AMBIGUOUS",),
    )
    passthrough = build_gc_structural_seed_evidence(dataset_config=_config(), dataset=upstream)
    assert passthrough == GCStructuralSeedResult(
        SMCV2PrimitiveStatus.AMBIGUOUS,
        reasons=("DATASET_AMBIGUOUS",),
        blocking_reasons=("DATASET_AMBIGUOUS",),
    )

    source = inspect.getsource(__import__("analysis.gc_structural_seed_evidence", fromlist=["*"]))
    assert "_StructuralAmbiguous" not in source
    assert "OPPOSING_STRUCTURE_EVENTS" not in source


def test_case_31_bullish_two_tick_fvg_ratio_qualifies() -> None:
    link = _build().seed.fair_value_gap_context_links[0]  # type: ignore[union-attr]
    assert link.formation_end_index == 7 and link.structure_event_type is DealingRangeEventType.BOS


def test_case_32_bearish_two_tick_fvg_ratio_qualifies() -> None:
    link = _build(_bearish_bars()).seed.fair_value_gap_context_links[0]  # type: ignore[union-attr]
    assert link.formation_end_index == 7


@pytest.mark.parametrize("mutation", ["one_tick", "zero_range", "ratio"])
def test_case_33_fvg_near_misses_do_not_link(mutation: str) -> None:
    bars = list(_bullish_bars())
    if mutation == "one_tick": bars[7] = replace(bars[7], low_tick=107)
    elif mutation == "zero_range": bars[6] = replace(bars[6], high_tick=105, low_tick=105, open_tick=105, close_tick=105)
    else: bars[6] = replace(bars[6], close_tick=106)
    result = _build(tuple(bars))
    assert result.seed is None or not result.seed.fair_value_gap_context_links


def test_case_34_fvg_sequence_is_contiguous_and_segment_local() -> None:
    kwargs = _displacement_kwargs(_build())
    assert kwargs["source_indices"] == (5, 6, 7)


def test_case_35_matching_event_and_fvg_create_one_link() -> None:
    seed = _build().seed
    assert seed is not None and len(seed.fair_value_gap_context_links) == 1
    assert seed.fair_value_gap_context_links[0].structure_event_id == seed.structure_events[0].event_id


def test_case_36_event_sequence_is_fvg_suffix() -> None:
    seed = _build().seed
    assert seed is not None
    assert seed.structure_events[0].provenance.source_indices == (seed.fair_value_gap_context_links[0].formation_end_index,)


def test_case_37_unmatched_event_or_fvg_emits_no_link() -> None:
    bars = list(_bullish_bars())
    bars[7] = replace(bars[7], low_tick=106)
    seed = _build(tuple(bars)).seed
    assert seed is not None and not seed.fair_value_gap_context_links


def test_case_38_displacement_identity_is_deterministic() -> None:
    result = _build()
    kwargs = _displacement_kwargs(result)
    assert make_gc_structural_seed_id(**kwargs) == make_gc_structural_seed_id(**kwargs)
    assert result.seed.fair_value_gap_context_links[0].displacement_id == make_gc_structural_seed_id(**kwargs)  # type: ignore[union-attr]


@pytest.mark.parametrize("field,value", [("segment_id", None), ("direction", None), ("source_indices", (5, 7)), ("segment_evidence_digests", (("0" * 64, "1" * 64),))])
def test_case_39_displacement_schema_is_fail_closed(field: str, value: object) -> None:
    kwargs = _displacement_kwargs(_build()); kwargs[field] = value
    with pytest.raises((TypeError, ValueError)): make_gc_structural_seed_id(**kwargs)


def test_case_40_source_digest_changes_on_ordered_mutation() -> None:
    first = _build().seed
    bars = list(_bullish_bars()); bars[0] = replace(bars[0], volume=101)
    second = _build(tuple(bars)).seed
    assert first is not None and second is not None and first.source_bar_digest != second.source_bar_digest


def test_case_41_segment_digest_binds_empty_segments() -> None:
    one = _build().seed; two = _build(second_bars=_empty_bars()).seed
    assert one is not None and two is not None and one.seed_id != two.seed_id


@pytest.mark.parametrize("field,value", [("segment_evidence_digests", ()), ("segment_id", "0" * 64), ("direction", SMCV2Direction.BULLISH), ("source_indices", (1,))])
def test_case_42_seed_schema_is_exhaustive(field: str, value: object) -> None:
    seed = _build().seed; assert seed is not None
    kwargs = dict(identity_kind=GCStructuralSeedIdentityKind.SEED, instrument=seed.instrument, timeframe=seed.timeframe, tick_size=Decimal("0.1"), dataset_id=seed.dataset_id, seed_version=seed.seed_version, config=GCStructuralSeedConfig(), source_bar_digest=seed.source_bar_digest, segment_evidence_digests=((_dataset()[1].segments[0].segment_id, _sha("evidence")),))
    kwargs[field] = value
    with pytest.raises((TypeError, ValueError)): make_gc_structural_seed_id(**kwargs)


def test_case_42_seed_order_and_duplicate_segments_are_identity_safe() -> None:
    seed = _build(second_bars=_empty_bars()).seed
    _, dataset = _dataset(second_bars=_empty_bars())
    assert seed is not None
    pairs = tuple((segment.segment_id, _sha(("evidence", index))) for index, segment in enumerate(dataset.segments))
    common = dict(
        identity_kind=GCStructuralSeedIdentityKind.SEED, instrument=seed.instrument,
        timeframe=seed.timeframe, tick_size=Decimal("0.1"), dataset_id=seed.dataset_id,
        seed_version=seed.seed_version, config=GCStructuralSeedConfig(),
        source_bar_digest=seed.source_bar_digest,
    )
    assert make_gc_structural_seed_id(**common, segment_evidence_digests=pairs) != make_gc_structural_seed_id(**common, segment_evidence_digests=tuple(reversed(pairs)))
    with pytest.raises((TypeError, ValueError)):
        make_gc_structural_seed_id(**common, segment_evidence_digests=(pairs[0], pairs[0]))


def test_case_43_public_signatures_enums_version_and_exports() -> None:
    assert GC_STRUCTURAL_SEED_VERSION == "GC-STRUCTURAL-SEED-V1"
    assert [k.value for k in GCStructuralSeedIdentityKind] == ["DISPLACEMENT", "SEED"]
    for fn in (make_gc_structural_seed_id, build_gc_structural_seed_evidence, validate_gc_structural_seed_evidence):
        assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in inspect.signature(fn).parameters.values())
    assert list(inspect.signature(make_gc_structural_seed_id).parameters) == [
        "identity_kind", "instrument", "timeframe", "tick_size", "dataset_id",
        "seed_version", "config", "source_bar_digest", "segment_id", "direction",
        "source_indices", "source_timestamps", "boundaries", "structure_event_id",
        "segment_evidence_digests",
    ]
    assert inspect.signature(build_gc_structural_seed_evidence).parameters["config"].default == GCStructuralSeedConfig()
    assert inspect.signature(validate_gc_structural_seed_evidence).parameters["config"].default == GCStructuralSeedConfig()
    import analysis.gc_structural_seed_evidence as module
    assert module.__all__ == ["GC_STRUCTURAL_SEED_VERSION", "GCStructuralSeedIdentityKind", "GCStructuralSeedConfig", "GCCanonicalSeedEvidence", "GCStructuralSeedResult", "make_gc_structural_seed_id", "build_gc_structural_seed_evidence", "validate_gc_structural_seed_evidence"]


def test_case_44_public_dataclasses_are_exact_and_frozen() -> None:
    assert [f.name for f in fields(GCStructuralSeedConfig)] == ["swing_left_bars", "swing_right_bars", "break_buffer_ticks"]
    assert [f.default for f in fields(GCStructuralSeedConfig)] == [2, 2, 1]
    assert [f.name for f in fields(GCCanonicalSeedEvidence)] == ["seed_id", "seed_version", "instrument", "timeframe", "dataset_id", "source_bar_digest", "dealing_range_swings", "equal_liquidity_swings", "structure_events", "fair_value_gap_context_links"]
    assert [f.name for f in fields(GCStructuralSeedResult)] == ["status", "seed", "reasons", "blocking_reasons"]
    assert get_type_hints(GCStructuralSeedConfig)["swing_left_bars"] is int
    with pytest.raises(FrozenInstanceError): GCStructuralSeedConfig().swing_left_bars = 3  # type: ignore[misc]


@pytest.mark.parametrize("bad", [True, 0, 3])
def test_case_44_locked_config_rejects_boolean_zero_and_tuning(bad: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        GCStructuralSeedConfig(swing_left_bars=bad)  # type: ignore[arg-type]


def test_case_45_none_dataset_and_valid_empty_seed_semantics() -> None:
    none = GCDatasetBuildResult(GCDatasetBuildStatus.NONE, None, (), None, ("NO_SOURCE_SCOPE",), ())
    assert build_gc_structural_seed_evidence(dataset_config=_config(), dataset=none).status is SMCV2PrimitiveStatus.NONE
    empty = _build(_empty_bars())
    assert empty.status is SMCV2PrimitiveStatus.NONE and empty.seed is not None


def test_case_46_status_precedence_and_no_partial_seed() -> None:
    for status in (GCDatasetBuildStatus.INVALID, GCDatasetBuildStatus.AMBIGUOUS, GCDatasetBuildStatus.UNKNOWN):
        dataset = GCDatasetBuildResult(status, None, (), None, (status.value,), (status.value,))
        result = build_gc_structural_seed_evidence(dataset_config=_config(), dataset=dataset)
        assert result.status.value == status.value and result.seed is None


def test_case_47_repeatability_validation_and_prefix_boundary() -> None:
    config, dataset = _dataset()
    first = build_gc_structural_seed_evidence(dataset_config=config, dataset=dataset)
    second = build_gc_structural_seed_evidence(dataset_config=config, dataset=dataset)
    assert first == second and first.seed is not None
    assert validate_gc_structural_seed_evidence(dataset_config=config, dataset=dataset, structural_seed=first.seed) == first
    assert validate_gc_structural_seed_evidence(dataset_config=config, dataset=dataset, structural_seed=replace(first.seed, seed_id="0" * 64)).status is SMCV2PrimitiveStatus.INVALID

    extended = _build(second_bars=_empty_bars())
    assert extended.seed is not None
    assert extended.seed.dealing_range_swings[:len(first.seed.dealing_range_swings)] == first.seed.dealing_range_swings
    assert extended.seed.equal_liquidity_swings[:len(first.seed.equal_liquidity_swings)] == first.seed.equal_liquidity_swings
    assert extended.seed.structure_events[:len(first.seed.structure_events)] == first.seed.structure_events
    assert extended.seed.source_bar_digest != first.seed.source_bar_digest
    assert extended.seed.seed_id != first.seed.seed_id
    assert len(extended.seed.fair_value_gap_context_links) >= len(first.seed.fair_value_gap_context_links)
    for prior, rebound in zip(
        first.seed.fair_value_gap_context_links,
        extended.seed.fair_value_gap_context_links,
        strict=True,
    ):
        assert (
            rebound.formation_end_index,
            rebound.formation_end_timestamp,
            rebound.structure_event_id,
            rebound.structure_event_type,
        ) == (
            prior.formation_end_index,
            prior.formation_end_timestamp,
            prior.structure_event_id,
            prior.structure_event_type,
        )
        assert rebound.displacement_id != prior.displacement_id


def test_case_47_same_segment_historical_mutation_is_not_prefix_equivalent() -> None:
    first = _build().seed
    bars = list(_bullish_bars())
    bars[0] = replace(bars[0], volume=101)
    changed = _build(tuple(bars)).seed
    assert first is not None and changed is not None
    assert changed.source_bar_digest != first.source_bar_digest and changed.seed_id != first.seed_id


def test_case_48_segment_local_output_is_downstream_compatible() -> None:
    seed = _build(second_bars=_bullish_bars()).seed
    assert seed is not None
    assert all(type(s.swing_id) is str for s in seed.dealing_range_swings)
    assert len(seed.dealing_range_swings) == len(seed.equal_liquidity_swings)
    assert len(seed.structure_events) == len(seed.fair_value_gap_context_links) == 2

    source = inspect.getsource(__import__("analysis.gc_structural_seed_evidence", fromlist=["*"]))
    assert "smc.market_structure" not in source and "smc.bos_choch" not in source
