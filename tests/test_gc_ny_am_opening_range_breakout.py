"""Exact 48-case acceptance matrix for GC NY-AM opening-range breakout feasibility."""

from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest
from zoneinfo import ZoneInfo

import analysis.gc_ny_am_opening_range_breakout as opening_range
from analysis.gc_dataset_builder import (
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCDatasetSessionInterval,
    GCSegmentPartition,
    GCSplitSessionCalendarEntry,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.kill_zones import (
    KillZoneCalendarEntry,
    KillZoneContext,
    KillZoneName,
    KillZoneQuality,
    KillZoneResult,
    KillZoneSessionStatus,
    KillZoneSnapshot,
    make_kill_zone_id,
)
from smc.smc_v2_primitives import SMCV2Direction, SMCV2PrimitiveStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TZDATA_VERSION = importlib.metadata.version("tzdata")
TRADE_DATE = date(2026, 1, 6)
CALENDAR_VERSION = "GC-CALENDAR-SYNTHETIC-V1"

EXPECTED_EXPORTS = (
    "GC_NY_AM_OPENING_RANGE_BREAKOUT_VERSION",
    "GCNYAMIdentityKind",
    "GCNYAMOutcomeType",
    "GCNYAMOpeningRangeObservation",
    "GCNYAMOpeningRange",
    "GCNYAMOpeningRangeCandidate",
    "GCNYAMOpeningRangeOutcome",
    "GCNYAMOpeningRangeManifest",
    "GCNYAMOpeningRangeResult",
    "make_gc_ny_am_opening_range_breakout_id",
    "analyze_gc_ny_am_opening_range_breakout",
)

COUNT_FUNNEL_KEYS = (
    "REQUESTED_TRADE_DATES", "CALENDAR_ELIGIBLE_TRADE_DATES", "COMPLETE_OPENING_RANGES",
    "NO_BREAKOUT_TRADE_DATES", "FORMATION_OUTCOME_COLLISIONS", "COMPLETE_CANDIDATES",
    "BULLISH_CANDIDATES", "BEARISH_CANDIDATES", "COMPLETE_OUTCOMES",
    "INCOMPLETE_HORIZONS", "INVALID_GROUPS", "AMBIGUOUS_GROUPS",
)

REASON_TOKENS = (
    "MISSING_TOP_LEVEL_CONTEXT", "INVALID_DATASET", "OOS_CONTACT", "UNREQUESTED_EVIDENCE",
    "INVALID_OBSERVATION", "MISSING_SPLIT_SESSION_CALENDAR", "INVALID_SPLIT_SESSION_CALENDAR",
    "MISSING_KILL_ZONE_CALENDAR", "INVALID_KILL_ZONE_CALENDAR", "MISSING_KILL_ZONE_EVIDENCE",
    "INVALID_KILL_ZONE_EVIDENCE", "SESSION_INELIGIBLE", "INCOMPLETE_OPENING_RANGE",
    "INVALID_OPENING_RANGE", "NO_BREAKOUT", "FORMATION_OUTCOME_COLLISION",
    "INCOMPLETE_OUTCOME_HORIZON", "INVALID_OUTCOME_EVIDENCE",
    "AMBIGUOUS_CANONICAL_INTERPRETATION",
)


def _h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), NY).astimezone(UTC)


def _config(**changes: object) -> GCDatasetBuildConfig:
    values: dict[str, object] = {
        "instrument": "GC",
        "timeframe": "5M",
        "source_timezone": "Asia/Tokyo",
        "exchange_timezone": "America/New_York",
        "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
        "initial_contract": "GCG26-COMEX",
        "initial_trade_date": TRADE_DATE,
        "roll_confirmation_sessions": 3,
        "oos_start_trade_date": date(2027, 1, 1),
        "oos_end_trade_date": date(2027, 6, 30),
    }
    values.update(changes)
    return GCDatasetBuildConfig(**values)  # type: ignore[arg-type]


def _prices(count: int = 22, *, direction: str = "bull", collision: bool = False) -> list[tuple[int, int, int, int]]:
    values = [(100, 102, 99, 101), (101, 103, 100, 102), (102, 104, 101, 103),
              (103, 105, 102, 104), (104, 106, 103, 105), (105, 107, 104, 106)]
    if direction == "bull":
        values.append((106, 115 if collision else 109, 106, 108))
        values.append((108, 115, 107, 114))
        values.extend([(108, 109, 107, 108)] * max(0, count - 8))
    elif direction == "bear":
        values.append((100, 100, 91 if collision else 97, 98))
        values.append((98, 99, 90, 91))
        values.extend([(98, 99, 97, 98)] * max(0, count - 8))
    else:
        values.extend([(106, 107, 100, 104)] * max(0, count - 6))
    return values[:count]


def _fixture(
    *,
    direction: str = "bull",
    count: int = 22,
    collision: bool = False,
    target_event: bool = True,
) -> dict[str, object]:
    opening = _utc(TRADE_DATE - timedelta(days=1), 18)
    session_close = _utc(TRADE_DATE, 17)
    first_open = _utc(TRADE_DATE, 7)
    prices = _prices(count, direction=direction, collision=collision)
    bars = tuple(
        GCChronologicalBar(
            index,
            first_open + timedelta(minutes=5 * (index + 1)),
            price[0], price[1], price[2], price[3], 10 + index, True,
        )
        for index, price in enumerate(prices)
    )
    if not target_event and len(bars) >= 8:
        bars = tuple(replace(bar, high_tick=min(bar.high_tick, 109), low_tick=max(bar.low_tick, 97), close_tick=108)
                     if bar.index >= 7 else bar for bar in bars)
    segment_id = _h("segment")
    segment = GCCanonicalContractSegment(
        segment_id, "GCG26-COMEX", GCSegmentPartition.DEVELOPMENT,
        TRADE_DATE, TRADE_DATE, (_h("source"),), bars, 0,
    )
    dataset_id = _h("dataset")
    manifest = GCDatasetManifest(
        dataset_id, "GC-DATASET-V1", (_h("source"),), (_h("coverage"),), _h("coverage-digest"),
        (segment_id,), CALENDAR_VERSION, TZDATA_VERSION, bars[0].timestamp, bars[-1].timestamp,
        bars[0].timestamp, bars[-1].timestamp, len(bars), len(bars), len(bars), 0, 0, 0, 0,
        sum(bar.volume for bar in bars), sum(bar.volume for bar in bars), 0,
        ((segment.contract, TRADE_DATE, sum(bar.volume for bar in bars)),), (), (),
    )
    dataset = GCDatasetBuildResult(GCDatasetBuildStatus.VALID, dataset_id, (segment,), manifest)
    split_calendar = (
        GCSplitSessionCalendarEntry(
            CALENDAR_VERSION, TRADE_DATE,
            (GCDatasetSessionInterval(opening, session_close),),
            (_h("calendar-source"),), (_h("calendar-sha"),),
        ),
    )
    kill_calendar = (
        KillZoneCalendarEntry(CALENDAR_VERSION, TRADE_DATE, KillZoneSessionStatus.OPEN, opening, session_close),
    )
    split_digest = opening_range._split_calendar_digest(split_calendar)
    kill_digest = opening_range._kill_calendar_digest(kill_calendar)
    observations: list[opening_range.GCNYAMOpeningRangeObservation] = []
    contexts: list[KillZoneContext] = []
    snapshots: list[KillZoneSnapshot] = []
    for bar in bars:
        bar_open = bar.timestamp - timedelta(minutes=5)
        context_id = make_kill_zone_id(
            identity_kind="CONTEXT",
            instrument="GC", timeframe="5M", calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York", timezone_data_version=TZDATA_VERSION,
            observation_index=bar.index, observation_timestamp=bar_open, trade_date=TRADE_DATE,
            zone=KillZoneName.NEW_YORK_AM, session_status=KillZoneSessionStatus.OPEN,
            quality=KillZoneQuality.VERIFIED,
        )
        snapshot_id = make_kill_zone_id(
            identity_kind="SNAPSHOT",
            instrument="GC", timeframe="5M", calendar_version=CALENDAR_VERSION,
            timezone_name="America/New_York", timezone_data_version=TZDATA_VERSION,
            effective_index=bar.index, effective_timestamp=bar_open, context_ids=(context_id,),
        )
        observation_id = opening_range.make_gc_ny_am_opening_range_breakout_id(
            identity_kind=opening_range.GCNYAMIdentityKind.OBSERVATION,
            instrument="GC", timeframe="5M", dataset_id=dataset_id,
            calendar_version=CALENDAR_VERSION, split_session_calendar_digest=split_digest,
            kill_zone_calendar_digest=kill_digest, timezone_name="America/New_York",
            timezone_data_version=TZDATA_VERSION, tick_size=Decimal("0.1"),
            segment_ordinal=0, segment_id=segment_id, contract=segment.contract,
            trade_date=TRADE_DATE, index=bar.index, bar_open_timestamp=bar_open,
            bar_close_timestamp=bar.timestamp, open_tick=bar.open_tick, high_tick=bar.high_tick,
            low_tick=bar.low_tick, close_tick=bar.close_tick, volume=bar.volume, is_closed=True,
            kill_zone_context_id=context_id, kill_zone_snapshot_id=snapshot_id,
        )
        observations.append(opening_range.GCNYAMOpeningRangeObservation(
            observation_id, 0, segment_id, segment.contract, TRADE_DATE, bar.index,
            bar_open, bar.timestamp, bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick,
            bar.volume, True, context_id, snapshot_id,
        ))
        contexts.append(KillZoneContext(
            context_id, bar.index, bar_open, TRADE_DATE, KillZoneName.NEW_YORK_AM,
            KillZoneSessionStatus.OPEN, KillZoneQuality.VERIFIED, CALENDAR_VERSION,
            "America/New_York", TZDATA_VERSION,
        ))
        snapshots.append(KillZoneSnapshot(snapshot_id, bar.index, bar_open, (context_id,)))
    return {
        "dataset_config": _config(), "dataset": dataset, "observations": tuple(observations),
        "split_session_calendar_entries": split_calendar,
        "kill_zone_calendar_entries": kill_calendar,
        "kill_zone_result": KillZoneResult(SMCV2PrimitiveStatus.VALID, tuple(contexts), tuple(snapshots)),
        "requested_trade_dates": (TRADE_DATE,),
    }


def _run(fixture: dict[str, object], **changes: object) -> opening_range.GCNYAMOpeningRangeResult:
    supplied = dict(fixture)
    supplied.update(changes)
    return opening_range.analyze_gc_ny_am_opening_range_breakout(**supplied)  # type: ignore[arg-type]


def _valid() -> opening_range.GCNYAMOpeningRangeResult:
    return _run(_fixture())


def _identity_common(fixture: dict[str, object]) -> dict[str, object]:
    dataset = fixture["dataset"]
    return {
        "instrument": "GC", "timeframe": "5M", "dataset_id": dataset.dataset_id,
        "calendar_version": CALENDAR_VERSION,
        "split_session_calendar_digest": opening_range._split_calendar_digest(fixture["split_session_calendar_entries"]),
        "kill_zone_calendar_digest": opening_range._kill_calendar_digest(fixture["kill_zone_calendar_entries"]),
        "timezone_name": "America/New_York", "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
    }


def _identity_payloads() -> dict[opening_range.GCNYAMIdentityKind, dict[str, object]]:
    fixture = _fixture()
    result = _run(fixture)
    observation = fixture["observations"][0]  # type: ignore[index]
    range_item = result.opening_ranges[0]
    candidate = result.candidates[0]
    outcome = result.outcomes[0]
    manifest = result.manifest
    assert manifest is not None
    common = _identity_common(fixture)
    return {
        opening_range.GCNYAMIdentityKind.OBSERVATION: {
            "identity_kind": opening_range.GCNYAMIdentityKind.OBSERVATION, **common,
            "segment_ordinal": observation.segment_ordinal, "segment_id": observation.segment_id,
            "contract": observation.contract, "trade_date": observation.trade_date,
            "index": observation.index, "bar_open_timestamp": observation.bar_open_timestamp,
            "bar_close_timestamp": observation.bar_close_timestamp, "open_tick": observation.open_tick,
            "high_tick": observation.high_tick, "low_tick": observation.low_tick,
            "close_tick": observation.close_tick, "volume": observation.volume,
            "is_closed": observation.is_closed, "kill_zone_context_id": observation.kill_zone_context_id,
            "kill_zone_snapshot_id": observation.kill_zone_snapshot_id,
        },
        opening_range.GCNYAMIdentityKind.OPENING_RANGE: {
            "identity_kind": opening_range.GCNYAMIdentityKind.OPENING_RANGE, **common,
            "segment_ordinal": range_item.segment_ordinal, "segment_id": range_item.segment_id,
            "contract": range_item.contract, "trade_date": range_item.trade_date,
            "source_observation_ids": range_item.source_observation_ids,
            "source_context_ids": range_item.source_context_ids,
            "source_snapshot_ids": range_item.source_snapshot_ids,
            "first_known_index": range_item.first_known_index,
            "first_known_timestamp": range_item.first_known_timestamp,
            "high_tick": range_item.high_tick, "low_tick": range_item.low_tick,
            "width_ticks": range_item.width_ticks,
        },
        opening_range.GCNYAMIdentityKind.CANDIDATE: {
            "identity_kind": opening_range.GCNYAMIdentityKind.CANDIDATE, **common,
            "range_id": candidate.range_id, "segment_ordinal": candidate.segment_ordinal,
            "segment_id": candidate.segment_id, "contract": candidate.contract,
            "trade_date": candidate.trade_date, "direction": candidate.direction,
            "formation_observation_id": candidate.formation_observation_id,
            "formation_context_id": candidate.formation_context_id,
            "formation_snapshot_id": candidate.formation_snapshot_id,
            "formation_index": candidate.formation_index,
            "first_known_timestamp": candidate.first_known_timestamp,
            "broken_boundary_tick": candidate.broken_boundary_tick,
            "target_tick": candidate.target_tick, "invalidation_tick": candidate.invalidation_tick,
            "width_ticks": candidate.width_ticks,
        },
        opening_range.GCNYAMIdentityKind.OUTCOME: {
            "identity_kind": opening_range.GCNYAMIdentityKind.OUTCOME, **common,
            "candidate_id": outcome.candidate_id, "outcome": outcome.outcome,
            "first_known_index": outcome.first_known_index,
            "first_known_timestamp": outcome.first_known_timestamp,
            "horizon_observation_ids": outcome.horizon_observation_ids,
            "event_observation_id": outcome.event_observation_id,
        },
        opening_range.GCNYAMIdentityKind.MANIFEST: {
            "identity_kind": opening_range.GCNYAMIdentityKind.MANIFEST, **common,
            "requested_trade_dates": manifest.requested_trade_dates,
            "opening_range_ids": manifest.opening_range_ids, "candidate_ids": manifest.candidate_ids,
            "outcome_ids": manifest.outcome_ids, "count_funnel": manifest.count_funnel,
            "reason_counts": manifest.reason_counts,
        },
    }


def _assert_required_and_forbidden_schema(
    kind: opening_range.GCNYAMIdentityKind,
    allowed_specific: set[str],
) -> None:
    payloads = _identity_payloads()
    payload = payloads[kind]
    common = {
        "identity_kind", "instrument", "timeframe", "dataset_id", "calendar_version",
        "split_session_calendar_digest", "kill_zone_calendar_digest", "timezone_name",
        "timezone_data_version", "tick_size",
    }
    for name in common:
        missing = dict(payload)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            opening_range.make_gc_ny_am_opening_range_breakout_id(**missing)  # type: ignore[arg-type]
    for name in allowed_specific:
        if kind is opening_range.GCNYAMIdentityKind.MANIFEST and name in {
            "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids", "reason_counts",
        }:
            continue
        if name not in payload or payload[name] in ((), None):
            continue
        missing = dict(payload)
        missing.pop(name)
        with pytest.raises((TypeError, ValueError)):
            opening_range.make_gc_ny_am_opening_range_breakout_id(**missing)  # type: ignore[arg-type]
    witnesses: dict[str, object] = {}
    for candidate_payload in payloads.values():
        witnesses.update(candidate_payload)
    witnesses["reason_counts"] = (("NO_BREAKOUT", 1),)
    builder_specific = set(inspect.signature(opening_range.make_gc_ny_am_opening_range_breakout_id).parameters) - common
    for name in builder_specific - allowed_specific:
        forbidden = dict(payload)
        forbidden[name] = witnesses[name]
        with pytest.raises((TypeError, ValueError)):
            opening_range.make_gc_ny_am_opening_range_breakout_id(**forbidden)  # type: ignore[arg-type]


def _with_prices(fixture: dict[str, object], position: int, **changes: int) -> dict[str, object]:
    dataset = fixture["dataset"]
    segment = dataset.segments[0]
    bars = list(segment.bars)
    bars[position] = replace(bars[position], **changes)
    updated_segment = replace(segment, bars=tuple(bars))
    updated_dataset = replace(dataset, segments=(updated_segment,))
    observations = list(fixture["observations"])
    item = replace(observations[position], **changes)
    common = _identity_common(fixture)
    observation_id = opening_range.make_gc_ny_am_opening_range_breakout_id(
        identity_kind=opening_range.GCNYAMIdentityKind.OBSERVATION,
        **common,
        segment_ordinal=item.segment_ordinal,
        segment_id=item.segment_id,
        contract=item.contract,
        trade_date=item.trade_date,
        index=item.index,
        bar_open_timestamp=item.bar_open_timestamp,
        bar_close_timestamp=item.bar_close_timestamp,
        open_tick=item.open_tick,
        high_tick=item.high_tick,
        low_tick=item.low_tick,
        close_tick=item.close_tick,
        volume=item.volume,
        is_closed=item.is_closed,
        kill_zone_context_id=item.kill_zone_context_id,
        kill_zone_snapshot_id=item.kill_zone_snapshot_id,
    )
    observations[position] = replace(item, observation_id=observation_id)
    updated = dict(fixture)
    updated["dataset"] = updated_dataset
    updated["observations"] = tuple(observations)
    return updated


def _with_calendars(
    fixture: dict[str, object],
    *,
    split_session_calendar_entries: tuple[GCSplitSessionCalendarEntry, ...] | None = None,
    kill_zone_calendar_entries: tuple[KillZoneCalendarEntry, ...] | None = None,
) -> dict[str, object]:
    """Rebind observation identities after an identity-bearing calendar change."""
    updated = dict(fixture)
    if split_session_calendar_entries is not None:
        updated["split_session_calendar_entries"] = split_session_calendar_entries
    if kill_zone_calendar_entries is not None:
        updated["kill_zone_calendar_entries"] = kill_zone_calendar_entries
    common = _identity_common(updated)
    observations: list[opening_range.GCNYAMOpeningRangeObservation] = []
    for item in fixture["observations"]:  # type: ignore[union-attr]
        observation_id = opening_range.make_gc_ny_am_opening_range_breakout_id(
            identity_kind=opening_range.GCNYAMIdentityKind.OBSERVATION,
            **common,
            segment_ordinal=item.segment_ordinal,
            segment_id=item.segment_id,
            contract=item.contract,
            trade_date=item.trade_date,
            index=item.index,
            bar_open_timestamp=item.bar_open_timestamp,
            bar_close_timestamp=item.bar_close_timestamp,
            open_tick=item.open_tick,
            high_tick=item.high_tick,
            low_tick=item.low_tick,
            close_tick=item.close_tick,
            volume=item.volume,
            is_closed=item.is_closed,
            kill_zone_context_id=item.kill_zone_context_id,
            kill_zone_snapshot_id=item.kill_zone_snapshot_id,
        )
        observations.append(replace(item, observation_id=observation_id))
    updated["observations"] = tuple(observations)
    return updated


# Logical cases 1-48.
def test_case_01_missing_top_level_context_and_invalid_precedence() -> None:
    fixture = _fixture()
    assert _run(fixture, dataset=None).status is SMCV2PrimitiveStatus.UNKNOWN
    bad = replace(fixture["observations"][0], observation_id="bad")  # type: ignore[index]
    assert _run(fixture, dataset=None, observations=(bad,)).status is SMCV2PrimitiveStatus.INVALID
    malformed_context = replace(fixture["kill_zone_result"].contexts[0], context_id="bad")  # type: ignore[union-attr]
    malformed_result = replace(
        fixture["kill_zone_result"],  # type: ignore[arg-type]
        contexts=(malformed_context,) + fixture["kill_zone_result"].contexts[1:],  # type: ignore[union-attr]
    )
    hidden = _run(fixture, dataset=None, kill_zone_result=malformed_result)
    assert hidden.status is SMCV2PrimitiveStatus.INVALID
    assert not hidden.opening_ranges and not hidden.candidates and not hidden.outcomes


def test_case_02_exact_dataset_binding() -> None:
    result = _valid()
    assert result.status is SMCV2PrimitiveStatus.VALID and result.manifest is not None
    assert result.manifest.dataset_id == _h("dataset")


def test_case_03_dataset_config_is_locked() -> None:
    for key, value in [("instrument", "MGC"), ("timeframe", "1M"), ("source_timezone", "UTC"),
                       ("exchange_timezone", "UTC"), ("tick_size", Decimal("1"))]:
        assert _run(_fixture(), dataset_config=_config(**{key: value})).status is SMCV2PrimitiveStatus.INVALID


def test_case_04_oos_contact_is_invalid() -> None:
    fixture = _fixture()
    segment = replace(fixture["dataset"].segments[0], partition=GCSegmentPartition.OOS_HOLDOUT)  # type: ignore[union-attr]
    dataset = replace(fixture["dataset"], segments=(segment,))  # type: ignore[arg-type]
    assert _run(fixture, dataset=dataset).status is SMCV2PrimitiveStatus.INVALID


def test_case_05_observation_maps_one_to_one_to_bar() -> None:
    fixture = _fixture()
    observation = replace(fixture["observations"][0], close_tick=999)  # type: ignore[index]
    assert _run(fixture, observations=(observation,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]


def test_case_06_observation_order_is_not_silently_sorted() -> None:
    fixture = _fixture()
    values = fixture["observations"]  # type: ignore[assignment]
    assert _run(fixture, observations=(values[1], values[0]) + values[2:]).status is SMCV2PrimitiveStatus.INVALID
    earlier = replace(
        values[1],
        bar_open_timestamp=values[0].bar_open_timestamp - timedelta(minutes=10),
        bar_close_timestamp=values[0].bar_close_timestamp - timedelta(minutes=10),
    )
    independently_invalid = _run(
        fixture,
        dataset=None,
        observations=(values[0], earlier) + values[2:],
    )
    assert independently_invalid.status is SMCV2PrimitiveStatus.INVALID
    assert independently_invalid.reasons == ("INVALID_OBSERVATION",)
    assert not independently_invalid.opening_ranges and not independently_invalid.candidates


def test_case_07_closed_integer_bar_contract() -> None:
    fixture = _fixture()
    for change in ({"is_closed": False}, {"high_tick": True}, {"volume": -1}, {"bar_close_timestamp": datetime(2026, 1, 1)}):
        bad = replace(fixture["observations"][0], **change)  # type: ignore[index]
        assert _run(fixture, observations=(bad,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]


def test_case_08_observation_identity_recomputation() -> None:
    fixture = _fixture()
    bad = replace(fixture["observations"][0], observation_id=_h("wrong"))  # type: ignore[index]
    assert _run(fixture, observations=(bad,) + fixture["observations"][1:]).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[index]


def test_case_09_split_calendar_missing_unknown_malformed_invalid() -> None:
    fixture = _fixture()
    assert _run(fixture, split_session_calendar_entries=None).status is SMCV2PrimitiveStatus.UNKNOWN
    missing = _run(fixture, split_session_calendar_entries=())
    assert missing.status is SMCV2PrimitiveStatus.UNKNOWN
    assert missing.reasons == ("MISSING_SPLIT_SESSION_CALENDAR",)
    assert missing.blocking_reasons == missing.reasons
    bad = replace(fixture["split_session_calendar_entries"][0], calendar_version="")  # type: ignore[index]
    assert _run(fixture, split_session_calendar_entries=(bad,)).status is SMCV2PrimitiveStatus.INVALID


def test_case_10_kill_calendar_missing_unknown_malformed_invalid() -> None:
    fixture = _fixture()
    assert _run(fixture, kill_zone_calendar_entries=None).status is SMCV2PrimitiveStatus.UNKNOWN
    missing = _run(fixture, kill_zone_calendar_entries=())
    assert missing.status is SMCV2PrimitiveStatus.UNKNOWN
    assert missing.reasons == ("MISSING_KILL_ZONE_CALENDAR",)
    assert missing.blocking_reasons == missing.reasons
    bad = replace(fixture["kill_zone_calendar_entries"][0], session_close_timestamp=None)  # type: ignore[index]
    assert _run(fixture, kill_zone_calendar_entries=(bad,)).status is SMCV2PrimitiveStatus.INVALID
    unknown_status = replace(fixture["kill_zone_calendar_entries"][0], session_status="UNSUPPORTED")  # type: ignore[index]
    assert _run(fixture, kill_zone_calendar_entries=(unknown_status,)).status is SMCV2PrimitiveStatus.INVALID


def test_case_11_calendar_order_and_version_are_exact() -> None:
    fixture = _fixture()
    other = replace(fixture["split_session_calendar_entries"][0], trade_date=date(2026, 1, 5))  # type: ignore[index]
    assert _run(fixture, split_session_calendar_entries=fixture["split_session_calendar_entries"] + (other,)).status is SMCV2PrimitiveStatus.INVALID  # type: ignore[operator]


def test_case_12_session_interval_contains_every_source_bar() -> None:
    fixture = _fixture(count=3)
    entry = fixture["split_session_calendar_entries"][0]  # type: ignore[index]
    bad = replace(entry, intervals=(GCDatasetSessionInterval(entry.intervals[0].start_timestamp, _utc(TRADE_DATE, 7, 20)),))
    ineligible = _run(_with_calendars(fixture, split_session_calendar_entries=(bad,)))
    assert ineligible.status is SMCV2PrimitiveStatus.NONE
    assert ineligible.reasons == ("SESSION_INELIGIBLE",)
    assert not ineligible.opening_ranges and ineligible.manifest is not None
    full_fixture = _fixture()
    kill_entry = full_fixture["kill_zone_calendar_entries"][0]  # type: ignore[index]
    early = replace(
        kill_entry,
        session_status=KillZoneSessionStatus.EARLY_CLOSE,
        session_close_timestamp=_utc(TRADE_DATE, 9, 30),
    )
    early_result = _run(_with_calendars(full_fixture, kill_zone_calendar_entries=(early,)))
    assert early_result.status is SMCV2PrimitiveStatus.NONE
    assert early_result.reasons == ("SESSION_INELIGIBLE",)


def test_case_13_kill_zone_context_and_snapshot_are_required() -> None:
    fixture = _fixture()
    assert _run(fixture, kill_zone_result=None).status is SMCV2PrimitiveStatus.UNKNOWN
    assert _run(fixture, kill_zone_result=KillZoneResult(SMCV2PrimitiveStatus.NONE)).status is SMCV2PrimitiveStatus.INVALID


def test_case_14_only_verified_new_york_am_context_is_valid() -> None:
    fixture = _fixture()
    context = replace(fixture["kill_zone_result"].contexts[0], zone=KillZoneName.LONDON)  # type: ignore[union-attr]
    result = replace(fixture["kill_zone_result"], contexts=(context,) + fixture["kill_zone_result"].contexts[1:])  # type: ignore[union-attr]
    assert _run(fixture, kill_zone_result=result).status is SMCV2PrimitiveStatus.INVALID


def test_case_15_context_and_snapshot_identity_recompute() -> None:
    fixture = _fixture()
    snapshot = replace(fixture["kill_zone_result"].snapshots[0], snapshot_id=_h("wrong"))  # type: ignore[union-attr]
    result = replace(fixture["kill_zone_result"], snapshots=(snapshot,) + fixture["kill_zone_result"].snapshots[1:])  # type: ignore[union-attr]
    assert _run(fixture, kill_zone_result=result).status is SMCV2PrimitiveStatus.INVALID


def test_case_16_opening_range_is_exact_six_bars() -> None:
    result = _valid()
    assert len(result.opening_ranges) == 1
    assert len(result.opening_ranges[0].source_observation_ids) == 6


def test_case_17_opening_range_geometry_and_first_known() -> None:
    item = _valid().opening_ranges[0]
    assert (item.low_tick, item.high_tick, item.width_ticks) == (99, 107, 8)
    assert item.first_known_index == 5 and item.first_known_timestamp == _utc(TRADE_DATE, 7, 30)


def test_case_18_incomplete_opening_range_is_unknown() -> None:
    fixture = _fixture(count=5)
    result = _run(fixture)
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN and not result.opening_ranges


def test_case_19_nonconsecutive_opening_range_is_invalid() -> None:
    fixture = _fixture()
    values = list(fixture["observations"])  # type: ignore[arg-type]
    values[2] = replace(values[2], index=99)
    assert _run(fixture, observations=tuple(values)).status is SMCV2PrimitiveStatus.INVALID


def test_case_20_bullish_exact_one_tick_breakout() -> None:
    result = _valid()
    assert result.candidates[0].direction is SMCV2Direction.BULLISH
    assert result.candidates[0].broken_boundary_tick == 107


def test_case_21_bearish_exact_one_tick_breakout() -> None:
    result = _run(_fixture(direction="bear"))
    assert result.candidates[0].direction is SMCV2Direction.BEARISH
    assert result.candidates[0].broken_boundary_tick == 99


def test_case_22_close_equal_boundary_is_no_breakout() -> None:
    fixture = _fixture(direction="none")
    result = _run(fixture)
    assert result.status is SMCV2PrimitiveStatus.NONE and not result.candidates
    assert result.manifest is not None
    assert "NO_BREAKOUT" in result.reasons


def test_case_23_candidate_window_is_start_inclusive_end_exclusive() -> None:
    fixture = _fixture(direction="none", count=30)
    fixture = _with_prices(fixture, 24, close_tick=108, high_tick=109)
    result = _run(fixture)
    assert not result.candidates


def test_case_24_earliest_candidate_wins() -> None:
    result = _valid()
    assert len(result.candidates) == 1 and result.candidates[0].formation_index == 6


def test_case_25_candidate_geometry_is_width_based() -> None:
    item = _valid().candidates[0]
    assert (item.target_tick, item.invalidation_tick, item.width_ticks) == (115, 99, 8)


def test_case_26_formation_outcome_collision_is_rejected() -> None:
    result = _run(_fixture(collision=True))
    assert not result.candidates and "FORMATION_OUTCOME_COLLISION" in result.reasons


def test_case_27_horizon_is_strictly_later_and_exact_twelve() -> None:
    outcome = _valid().outcomes[0]
    assert len(outcome.horizon_observation_ids) <= 12
    assert _valid().candidates[0].formation_observation_id not in outcome.horizon_observation_ids


def test_case_28_extension_first_is_terminal() -> None:
    assert _valid().outcomes[0].outcome is opening_range.GCNYAMOutcomeType.EXTENSION_FIRST


def test_case_29_invalidation_first_is_terminal() -> None:
    fixture = _fixture(target_event=False)
    fixture = _with_prices(fixture, 7, close_tick=99, low_tick=98)
    assert _run(fixture).outcomes[0].outcome is opening_range.GCNYAMOutcomeType.INVALIDATION_FIRST


def test_case_30_same_bar_touch_is_ambiguous_terminal_outcome() -> None:
    fixture = _fixture(target_event=False)
    fixture = _with_prices(fixture, 7, high_tick=115, low_tick=98, close_tick=99)
    assert _run(fixture).outcomes[0].outcome is opening_range.GCNYAMOutcomeType.SAME_BAR_AMBIGUOUS


def test_case_31_timeout_needs_exact_twelve_bars() -> None:
    result = _run(_fixture(target_event=False))
    outcome = result.outcomes[0]
    assert outcome.outcome is opening_range.GCNYAMOutcomeType.TIMEOUT
    assert len(outcome.horizon_observation_ids) == 12 and outcome.event_observation_id is None


def test_case_32_incomplete_horizon_promotes_no_outcome() -> None:
    result = _run(_fixture(count=12, target_event=False))
    assert result.status is SMCV2PrimitiveStatus.UNKNOWN and not result.outcomes


def test_case_33_outcome_first_known_is_event_close() -> None:
    result = _valid()
    event_id = result.outcomes[0].event_observation_id
    observation = next(item for item in _fixture()["observations"] if item.observation_id == event_id)  # type: ignore[union-attr]
    assert result.outcomes[0].first_known_timestamp == observation.bar_close_timestamp


def test_case_34_malformed_horizon_is_invalid_without_outcome() -> None:
    fixture = _fixture(target_event=False)
    values = list(fixture["observations"])  # type: ignore[arg-type]
    values[8] = replace(values[8], observation_id="bad")
    result = _run(fixture, observations=tuple(values))
    assert result.status is SMCV2PrimitiveStatus.INVALID and not result.outcomes


def test_case_35_later_invalid_preserves_strict_prior_range_candidate() -> None:
    fixture = _fixture()
    values = list(fixture["observations"])  # type: ignore[arg-type]
    values[-1] = replace(values[-1], observation_id="bad")
    result = _run(fixture, observations=tuple(values))
    assert result.status is SMCV2PrimitiveStatus.INVALID
    assert result.opening_ranges and result.candidates and result.outcomes


def test_case_36_status_precedence_and_manifest_promotion() -> None:
    valid = _valid()
    assert valid.manifest is not None
    unknown = _run(_fixture(count=12, target_event=False))
    assert unknown.status is SMCV2PrimitiveStatus.UNKNOWN and unknown.manifest is None


def test_case_37_observation_identity_schema_is_exhaustive() -> None:
    payload = _identity_payloads()[opening_range.GCNYAMIdentityKind.OBSERVATION]
    item = _fixture()["observations"][0]  # type: ignore[index]
    assert opening_range.make_gc_ny_am_opening_range_breakout_id(**payload) == item.observation_id
    _assert_required_and_forbidden_schema(
        opening_range.GCNYAMIdentityKind.OBSERVATION,
        {
            "segment_ordinal", "segment_id", "contract", "trade_date", "index",
            "bar_open_timestamp", "bar_close_timestamp", "open_tick", "high_tick", "low_tick",
            "close_tick", "volume", "is_closed", "kill_zone_context_id", "kill_zone_snapshot_id",
        },
    )


def test_case_38_range_identity_schema_and_sensitivity() -> None:
    item = _valid().opening_ranges[0]
    common = _identity_common(_fixture())
    first = opening_range.make_gc_ny_am_opening_range_breakout_id(
        identity_kind=opening_range.GCNYAMIdentityKind.OPENING_RANGE, **common,
        segment_ordinal=item.segment_ordinal, segment_id=item.segment_id, contract=item.contract,
        trade_date=item.trade_date, source_observation_ids=item.source_observation_ids,
        source_context_ids=item.source_context_ids, source_snapshot_ids=item.source_snapshot_ids,
        first_known_index=item.first_known_index, first_known_timestamp=item.first_known_timestamp,
        high_tick=item.high_tick, low_tick=item.low_tick, width_ticks=item.width_ticks,
    )
    assert first == item.range_id
    _assert_required_and_forbidden_schema(
        opening_range.GCNYAMIdentityKind.OPENING_RANGE,
        {
            "segment_ordinal", "segment_id", "contract", "trade_date", "source_observation_ids",
            "source_context_ids", "source_snapshot_ids", "first_known_index",
            "first_known_timestamp", "high_tick", "low_tick", "width_ticks",
        },
    )


def test_case_39_candidate_identity_schema_and_sensitivity() -> None:
    item = _valid().candidates[0]
    common = _identity_common(_fixture())
    payload = dict(
        identity_kind=opening_range.GCNYAMIdentityKind.CANDIDATE, **common,
        range_id=item.range_id, segment_ordinal=item.segment_ordinal, segment_id=item.segment_id,
        contract=item.contract, trade_date=item.trade_date, direction=item.direction,
        formation_observation_id=item.formation_observation_id, formation_context_id=item.formation_context_id,
        formation_snapshot_id=item.formation_snapshot_id, formation_index=item.formation_index,
        first_known_timestamp=item.first_known_timestamp, broken_boundary_tick=item.broken_boundary_tick,
        target_tick=item.target_tick, invalidation_tick=item.invalidation_tick, width_ticks=item.width_ticks,
    )
    assert opening_range.make_gc_ny_am_opening_range_breakout_id(**payload) == item.candidate_id
    impossible = dict(payload)
    impossible["invalidation_tick"] = item.invalidation_tick + 1
    assert impossible["invalidation_tick"] < item.broken_boundary_tick
    with pytest.raises((TypeError, ValueError)):
        opening_range.make_gc_ny_am_opening_range_breakout_id(**impossible)
    _assert_required_and_forbidden_schema(
        opening_range.GCNYAMIdentityKind.CANDIDATE,
        {
            "range_id", "segment_ordinal", "segment_id", "contract", "trade_date", "direction",
            "formation_observation_id", "formation_context_id", "formation_snapshot_id",
            "formation_index", "first_known_timestamp", "broken_boundary_tick", "target_tick",
            "invalidation_tick", "width_ticks",
        },
    )


def test_case_40_outcome_identity_schema_and_terminal_only_rule() -> None:
    item = _valid().outcomes[0]
    assert len(item.outcome_id) == 64
    with pytest.raises((TypeError, ValueError)):
        opening_range.make_gc_ny_am_opening_range_breakout_id(
            identity_kind=opening_range.GCNYAMIdentityKind.OUTCOME,
            **_identity_common(_fixture()), candidate_id=item.candidate_id,
            outcome=opening_range.GCNYAMOutcomeType.INCOMPLETE, first_known_index=item.first_known_index,
            first_known_timestamp=item.first_known_timestamp, horizon_observation_ids=item.horizon_observation_ids,
        )
    _assert_required_and_forbidden_schema(
        opening_range.GCNYAMIdentityKind.OUTCOME,
        {
            "candidate_id", "outcome", "first_known_index", "first_known_timestamp",
            "horizon_observation_ids", "event_observation_id",
        },
    )


def test_case_41_manifest_schema_count_order_and_identity() -> None:
    manifest = _valid().manifest
    assert manifest is not None and len(manifest.manifest_id) == 64
    assert tuple(key for key, _ in manifest.count_funnel) == COUNT_FUNNEL_KEYS
    fixture = _fixture(direction="none")
    common = _identity_common(fixture)
    counts = {key: 0 for key in COUNT_FUNNEL_KEYS}
    counts.update(
        REQUESTED_TRADE_DATES=3,
        CALENDAR_ELIGIBLE_TRADE_DATES=1,
        NO_BREAKOUT_TRADE_DATES=1,
    )
    counted = opening_range._make_manifest(
        common,
        (date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)),
        (),
        (),
        (),
        counts,
        ("SESSION_INELIGIBLE", "NO_BREAKOUT"),
    )
    assert counted.reason_counts == (("SESSION_INELIGIBLE", 2), ("NO_BREAKOUT", 1))
    _assert_required_and_forbidden_schema(
        opening_range.GCNYAMIdentityKind.MANIFEST,
        {
            "requested_trade_dates", "opening_range_ids", "candidate_ids", "outcome_ids",
            "count_funnel", "reason_counts",
        },
    )
    with pytest.raises((TypeError, ValueError)):
        opening_range.make_gc_ny_am_opening_range_breakout_id(
            **{
                **_identity_payloads()[opening_range.GCNYAMIdentityKind.MANIFEST],
                "requested_trade_dates": (date(2026, 1, 7), date(2026, 1, 6)),
            }
        )


def test_case_42_public_signatures_are_exact_keyword_only() -> None:
    builder = inspect.signature(opening_range.make_gc_ny_am_opening_range_breakout_id)
    analyzer = inspect.signature(opening_range.analyze_gc_ny_am_opening_range_breakout)
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in builder.parameters.values())
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in analyzer.parameters.values())
    assert tuple(analyzer.parameters) == (
        "dataset_config", "dataset", "observations", "split_session_calendar_entries",
        "kill_zone_calendar_entries", "kill_zone_result", "requested_trade_dates",
    )
    assert tuple(builder.parameters) == (
        "identity_kind", "instrument", "timeframe", "dataset_id", "calendar_version",
        "split_session_calendar_digest", "kill_zone_calendar_digest", "timezone_name",
        "timezone_data_version", "tick_size", "segment_ordinal", "segment_id", "contract",
        "trade_date", "index", "bar_open_timestamp", "bar_close_timestamp", "open_tick",
        "high_tick", "low_tick", "close_tick", "volume", "is_closed", "kill_zone_context_id",
        "kill_zone_snapshot_id", "source_observation_ids", "source_context_ids",
        "source_snapshot_ids", "first_known_index", "first_known_timestamp", "range_id",
        "direction", "formation_observation_id", "formation_context_id", "formation_snapshot_id",
        "formation_index", "broken_boundary_tick", "target_tick", "invalidation_tick",
        "width_ticks", "candidate_id", "outcome", "horizon_observation_ids",
        "event_observation_id", "requested_trade_dates", "opening_range_ids", "candidate_ids",
        "outcome_ids", "count_funnel", "reason_counts",
    )
    required = tuple(builder.parameters)[:10]
    assert all(builder.parameters[name].default is inspect.Parameter.empty for name in required)
    assert all(
        builder.parameters[name].default is None
        for name in tuple(builder.parameters)[10:25] + tuple(builder.parameters)[28:44]
        if name not in {"source_observation_ids", "source_context_ids", "source_snapshot_ids", "horizon_observation_ids"}
    )
    assert all(
        builder.parameters[name].default == ()
        for name in (
            "source_observation_ids", "source_context_ids", "source_snapshot_ids",
            "horizon_observation_ids", "requested_trade_dates", "opening_range_ids", "candidate_ids",
            "outcome_ids", "count_funnel", "reason_counts",
        )
    )


def test_case_43_frozen_dataclasses_fields_defaults_enums_and_exports() -> None:
    result = _valid()
    with pytest.raises(FrozenInstanceError):
        result.status = SMCV2PrimitiveStatus.NONE  # type: ignore[misc]
    assert [item.value for item in opening_range.GCNYAMIdentityKind] == [
        "OBSERVATION", "OPENING_RANGE", "CANDIDATE", "OUTCOME", "MANIFEST"
    ]
    assert opening_range.__all__ == EXPECTED_EXPORTS
    expected_fields = {
        opening_range.GCNYAMOpeningRangeObservation: (
            "observation_id", "segment_ordinal", "segment_id", "contract", "trade_date", "index",
            "bar_open_timestamp", "bar_close_timestamp", "open_tick", "high_tick", "low_tick",
            "close_tick", "volume", "is_closed", "kill_zone_context_id", "kill_zone_snapshot_id",
        ),
        opening_range.GCNYAMOpeningRange: (
            "range_id", "segment_ordinal", "segment_id", "contract", "trade_date",
            "source_observation_ids", "source_context_ids", "source_snapshot_ids",
            "first_known_index", "first_known_timestamp", "high_tick", "low_tick", "width_ticks",
        ),
        opening_range.GCNYAMOpeningRangeCandidate: (
            "candidate_id", "range_id", "segment_ordinal", "segment_id", "contract", "trade_date",
            "direction", "formation_observation_id", "formation_context_id", "formation_snapshot_id",
            "formation_index", "first_known_timestamp", "broken_boundary_tick", "target_tick",
            "invalidation_tick", "width_ticks",
        ),
        opening_range.GCNYAMOpeningRangeOutcome: (
            "outcome_id", "candidate_id", "outcome", "first_known_index", "first_known_timestamp",
            "horizon_observation_ids", "event_observation_id",
        ),
        opening_range.GCNYAMOpeningRangeManifest: (
            "manifest_id", "version", "instrument", "timeframe", "dataset_id", "calendar_version",
            "split_session_calendar_digest", "kill_zone_calendar_digest", "timezone_name",
            "timezone_data_version", "requested_trade_dates", "opening_range_ids", "candidate_ids",
            "outcome_ids", "count_funnel", "reason_counts",
        ),
        opening_range.GCNYAMOpeningRangeResult: (
            "status", "opening_ranges", "candidates", "outcomes", "manifest", "reasons",
            "blocking_reasons",
        ),
    }
    for data_type, names in expected_fields.items():
        assert tuple(item.name for item in fields(data_type)) == names
        assert data_type.__dataclass_params__.frozen is True
        if data_type is not opening_range.GCNYAMOpeningRangeResult:
            assert all(item.default is MISSING for item in fields(data_type))
    hints = get_type_hints(opening_range.GCNYAMOpeningRangeResult)
    assert hints["manifest"] == opening_range.GCNYAMOpeningRangeManifest | None
    defaults = {item.name: item.default for item in fields(opening_range.GCNYAMOpeningRangeResult)}
    assert defaults == {
        "status": MISSING, "opening_ranges": (), "candidates": (), "outcomes": (),
        "manifest": None, "reasons": (), "blocking_reasons": (),
    }


def test_case_44_repeatability_and_equivalent_utc_normalization() -> None:
    fixture = _fixture()
    assert _run(fixture) == _run(fixture)
    item = fixture["observations"][0]  # type: ignore[index]
    shifted = replace(item, bar_open_timestamp=item.bar_open_timestamp.astimezone(timezone(timedelta(hours=9))))
    assert shifted.bar_open_timestamp == item.bar_open_timestamp
    common = _identity_common(fixture)
    normalized_id = opening_range.make_gc_ny_am_opening_range_breakout_id(
        identity_kind=opening_range.GCNYAMIdentityKind.OBSERVATION,
        **common,
        segment_ordinal=item.segment_ordinal,
        segment_id=item.segment_id,
        contract=item.contract,
        trade_date=item.trade_date,
        index=item.index,
        bar_open_timestamp=shifted.bar_open_timestamp,
        bar_close_timestamp=item.bar_close_timestamp.astimezone(timezone(timedelta(hours=9))),
        open_tick=item.open_tick,
        high_tick=item.high_tick,
        low_tick=item.low_tick,
        close_tick=item.close_tick,
        volume=item.volume,
        is_closed=item.is_closed,
        kill_zone_context_id=item.kill_zone_context_id,
        kill_zone_snapshot_id=item.kill_zone_snapshot_id,
    )
    assert normalized_id == item.observation_id


def test_case_45_complete_strictly_later_prefix_is_invariant() -> None:
    fixture = _fixture(count=22)
    prefix = _run(fixture)
    extended = _fixture(count=23)
    later = _run(extended)
    assert later.opening_ranges[:1] == prefix.opening_ranges
    assert later.candidates[:1] == prefix.candidates
    assert later.outcomes[:1] == prefix.outcomes


def test_case_46_same_effective_or_historical_repair_is_not_prefix() -> None:
    fixture = _fixture()
    values = list(fixture["observations"])  # type: ignore[arg-type]
    values.insert(1, values[1])
    assert _run(fixture, observations=tuple(values)).status is SMCV2PrimitiveStatus.INVALID


def test_case_47_reason_order_and_reporting_are_deterministic_nonranking() -> None:
    result = _run(_fixture(direction="none"))
    assert result.reasons == tuple(token for token in REASON_TOKENS if token in result.reasons)
    assert not any(token in repr(result).upper() for token in ("CONFIDENCE", "BUY", "SELL", "PNL"))


def test_case_48_exact_scope_and_no_authority_surface() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "analysis/gc_ny_am_opening_range_breakout.py").exists()
    source = (root / "analysis/gc_ny_am_opening_range_breakout.py").read_text(encoding="utf-8")
    for forbidden in ("import main", "storage.decision_trace", "DECISION_CANDIDATE", "place_order", "execute_trade"):
        assert forbidden not in source
