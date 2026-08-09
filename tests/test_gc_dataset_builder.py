from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
from enum import Enum
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
from typing import Callable, get_type_hints

import pytest
from zoneinfo import ZoneInfo

import analysis.gc_dataset_builder as dataset
from analysis.gc_dataset_builder import (
    GC_DATASET_BUILDER_VERSION,
    GC_DATASET_EXCHANGE_TIMEZONE,
    GC_DATASET_INSTRUMENT,
    GC_DATASET_SOURCE_TIMEZONE,
    GC_DATASET_TICK_SIZE,
    GC_DATASET_TIMEFRAME,
    GC_DELIVERY_MONTH_CODES,
    GC_ROLL_CONFIRMATION_SESSIONS,
    GCCanonicalContractSegment,
    GCDatasetBuildConfig,
    GCDatasetBuildResult,
    GCDatasetBuildStatus,
    GCDatasetManifest,
    GCDatasetSessionInterval,
    GCSplitSessionCalendarEntry,
    GCSegmentPartition,
    GCSierraChartBarRow,
    GCSierraChartCoverageEvidence,
    GCSierraChartExport,
    GCSourceRole,
    build_gc_futures_dataset,
    make_gc_dataset_id,
    parse_sierra_chart_gc_export,
)
from core.gc_chronological_backtest import GCChronologicalBar
from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TOKYO = ZoneInfo("Asia/Tokyo")
TZDATA_VERSION = importlib.metadata.version("tzdata")
CALENDAR_VERSION = "GC-SYNTHETIC-CALENDAR-1"
HEADER = (
    "Date, Time, Open, High, Low, Last, Volume, # of Trades, "
    "OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume"
)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
AUTHENTICATED_CME_EMAIL_SHA256 = (
    "8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2"
)
D1 = date(2026, 1, 6)
D2 = date(2026, 1, 7)
D3 = date(2026, 1, 8)
D4 = date(2026, 1, 9)
D5 = date(2026, 1, 12)

_ACCEPTED_V2_PILOT_IDENTITY_VECTORS = (
    {
        "source_name": (
            "GCG26_COMEX_5m_20260218_20260330_"
            "NON_PROMOTABLE_ENGINEERING_PILOT.txt"
        ),
        "source_sha256": (
            "27552a778abf2fb158d7107eff9232396c9aae5e489a55b50259923c379be839"
        ),
        "contract": "GCG26-COMEX",
        "capture_timestamp": datetime.fromisoformat(
            "2026-08-03T11:29:40.822000+00:00"
        ),
        "coverage_start_timestamp": datetime.fromisoformat(
            "2026-02-17T23:00:00+00:00"
        ),
        "coverage_end_timestamp": datetime.fromisoformat(
            "2026-02-25T11:45:00+00:00"
        ),
        "acquisition_completed_timestamp": datetime.fromisoformat(
            "2026-08-03T11:27:13.925000+00:00"
        ),
        "acquisition_evidence_sha256": (
            "19ffa3b0c8459455d6f7d546770e802b5fb902a7c1fcfa47128640f62be584e0"
        ),
        "source_id": (
            "1a8c876a57852d07c9bcd068c36c0c2244057ca13cc9e737d0909962e7c2cac1"
        ),
        "coverage_id": (
            "c0a728eec42ca9cc692e3776ce83e95e99884ce3bfaad84d96adda6ef4505290"
        ),
    },
    {
        "source_name": (
            "GCJ26_COMEX_5m_20260218_20260330_"
            "NON_PROMOTABLE_ENGINEERING_PILOT.txt"
        ),
        "source_sha256": (
            "6e0419af7e85bf5c31a5f79aa36adeed1a9b1d8bf3123cbb8dda7af1313eed3a"
        ),
        "contract": "GCJ26-COMEX",
        "capture_timestamp": datetime.fromisoformat(
            "2026-08-03T10:56:37.481000+00:00"
        ),
        "coverage_start_timestamp": datetime.fromisoformat(
            "2026-02-17T23:00:00+00:00"
        ),
        "coverage_end_timestamp": datetime.fromisoformat(
            "2026-03-30T21:00:00+00:00"
        ),
        "acquisition_completed_timestamp": datetime.fromisoformat(
            "2026-08-03T10:51:36.388000+00:00"
        ),
        "acquisition_evidence_sha256": (
            "19ffa3b0c8459455d6f7d546770e802b5fb902a7c1fcfa47128640f62be584e0"
        ),
        "source_id": (
            "863aaff9e97cd8448a3edb008639e00be4bd0e35bcb72af8e9ed3a083a661a5e"
        ),
        "coverage_id": (
            "35092c5d8e97251a6cf2afa323ae8195cfb4ba9675b51c8cd784c3ce75bb92c6"
        ),
    },
    {
        "source_name": (
            "GCM26_COMEX_5m_20260218_20260330_"
            "NON_PROMOTABLE_ENGINEERING_PILOT.txt"
        ),
        "source_sha256": (
            "30abdcbc2f41498ef36c734ea28780b62e7338882543d41a6fddb33472036f3d"
        ),
        "contract": "GCM26-COMEX",
        "capture_timestamp": datetime.fromisoformat(
            "2026-08-03T16:19:49.186000+00:00"
        ),
        "coverage_start_timestamp": datetime.fromisoformat(
            "2026-02-17T23:00:00+00:00"
        ),
        "coverage_end_timestamp": datetime.fromisoformat(
            "2026-03-30T21:00:00+00:00"
        ),
        "acquisition_completed_timestamp": datetime.fromisoformat(
            "2026-08-03T16:16:27.882000+00:00"
        ),
        "acquisition_evidence_sha256": (
            "6689ce0a8387a64174756b3d0f44b8d7cbcd6ebf3dfc7c0a5550c2af173e49ff"
        ),
        "source_id": (
            "84a5b8e5599c6dce1bf06599c6cdefad7d27118a13ea86b856c1c9427d6c8918"
        ),
        "coverage_id": (
            "1030b2cb66bf3154deeed18528d94f8fc5ba7357563dc9c6e00fe50c25eba205"
        ),
    },
)


def _bounds(
    trade_date: date,
    *,
    close_minutes: int = 10,
) -> tuple[datetime, datetime]:
    opening = datetime.combine(
        trade_date - timedelta(days=1), time(18), tzinfo=NY
    ).astimezone(UTC)
    return opening, opening + timedelta(minutes=close_minutes)


def _calendar(
    trade_date: date,
    *,
    status: KillZoneSessionStatus = KillZoneSessionStatus.EARLY_CLOSE,
    close_minutes: int = 10,
    version: str = CALENDAR_VERSION,
) -> KillZoneCalendarEntry:
    if status is KillZoneSessionStatus.SESSION_CLOSED:
        return KillZoneCalendarEntry(version, trade_date, status, None, None)
    opening, short_close = _bounds(trade_date, close_minutes=close_minutes)
    standard_close = datetime.combine(trade_date, time(17), tzinfo=NY).astimezone(UTC)
    return KillZoneCalendarEntry(
        version,
        trade_date,
        status,
        opening,
        standard_close if status is KillZoneSessionStatus.OPEN else short_close,
    )


def _split_calendar(
    trade_date: date,
    *,
    intervals: tuple[GCDatasetSessionInterval, ...] | None = None,
    version: str = CALENDAR_VERSION,
    source_artifact_ids: tuple[str, ...] = ("CME-GCC-04687271-FINAL",),
    source_artifact_sha256s: tuple[str, ...] = (
        AUTHENTICATED_CME_EMAIL_SHA256,
    ),
) -> GCSplitSessionCalendarEntry:
    opening, _ = _bounds(trade_date)
    selected_intervals = intervals or (
        GCDatasetSessionInterval(opening, opening + timedelta(minutes=10)),
        GCDatasetSessionInterval(
            opening + timedelta(minutes=20),
            opening + timedelta(minutes=30),
        ),
    )
    return GCSplitSessionCalendarEntry(
        version,
        trade_date,
        selected_intervals,
        source_artifact_ids,
        source_artifact_sha256s,
    )


def _calendar_intervals(
    item: KillZoneCalendarEntry | GCSplitSessionCalendarEntry,
) -> tuple[tuple[datetime, datetime], ...]:
    if isinstance(item, GCSplitSessionCalendarEntry):
        return tuple(
            (interval.start_timestamp, interval.end_timestamp)
            for interval in item.intervals
        )
    if (
        item.session_open_timestamp is None
        or item.session_close_timestamp is None
    ):
        return ()
    return ((item.session_open_timestamp, item.session_close_timestamp),)


def _calendar_status(
    item: KillZoneCalendarEntry | GCSplitSessionCalendarEntry,
) -> KillZoneSessionStatus:
    return (
        KillZoneSessionStatus.OPEN
        if isinstance(item, GCSplitSessionCalendarEntry)
        else item.session_status
    )


def _raw_starts(
    starts: tuple[datetime, ...],
    volumes: tuple[int, ...],
    *,
    price: Decimal = Decimal("4000.0"),
) -> bytes:
    if len(starts) != len(volumes):
        raise ValueError("starts and volumes must have equal length")
    lines = [HEADER]
    for start, volume in zip(starts, volumes, strict=True):
        local = start.astimezone(TOKYO).replace(tzinfo=None)
        bid = volume // 2
        ask = volume - bid
        lines.append(
            ", ".join(
                (
                    f"{local.year}-{local.month}-{local.day}",
                    local.strftime("%H:%M:%S.%f"),
                    str(price),
                    str(price + Decimal("0.2")),
                    str(price - Decimal("0.2")),
                    str(price),
                    str(volume),
                    str(max(volume, 1)),
                    str(price),
                    str(price),
                    str(price),
                    str(bid),
                    str(ask),
                )
            )
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _raw(
    sessions: tuple[tuple[date, int], ...],
    *,
    price: Decimal = Decimal("4000.0"),
    second_offset_minutes: int = 5,
    average_suffix: str = "",
) -> bytes:
    lines = [HEADER]
    for trade_date, total_volume in sessions:
        opening, _ = _bounds(trade_date)
        starts = (opening, opening + timedelta(minutes=second_offset_minutes))
        volumes = (total_volume // 2, total_volume - total_volume // 2)
        for start, volume in zip(starts, volumes, strict=True):
            local = start.astimezone(TOKYO).replace(tzinfo=None)
            day = f"{local.year}-{local.month}-{local.day}"
            clock = local.strftime("%H:%M:%S.%f")
            high = price + Decimal("0.2")
            low = price - Decimal("0.2")
            bid = volume // 2
            ask = volume - bid
            avg = f"{price}{average_suffix}"
            lines.append(
                ", ".join(
                    [
                        day,
                        clock,
                        str(price),
                        str(high),
                        str(low),
                        str(price),
                        str(volume),
                        str(max(volume, 1)),
                        avg,
                        avg,
                        avg,
                        str(bid),
                        str(ask),
                    ]
                )
            )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _export(
    contract: str = "GCG26-COMEX",
    sessions: tuple[tuple[date, int], ...] = ((D1, 10),),
    *,
    role: GCSourceRole = GCSourceRole.DEVELOPMENT,
    source_name: str | None = None,
    raw_bytes: bytes | None = None,
    capture_timestamp: datetime | None = None,
) -> GCSierraChartExport:
    contract_price = {
        "GCZ25-COMEX": Decimal("3900.0"),
        "GCG26-COMEX": Decimal("4000.0"),
        "GCJ26-COMEX": Decimal("4100.0"),
        "GCM26-COMEX": Decimal("4200.0"),
    }.get(contract, Decimal("4300.0"))
    selected_raw = (
        _raw(sessions, price=contract_price)
        if raw_bytes is None
        else raw_bytes
    )
    latest = max(day for day, _ in sessions) if sessions else D1
    _, closing = _bounds(latest)
    return parse_sierra_chart_gc_export(
        source_name=(
            f"{contract}_{role.value}.txt"
            if source_name is None
            else source_name
        ),
        contract=contract,
        role=role,
        capture_timestamp=capture_timestamp or closing + timedelta(minutes=1),
        chart_timezone="Asia/Tokyo",
        timeframe="5m",
        raw_bytes=selected_raw,
    )


def _prior_eligible_dates(trade_date: date) -> tuple[date, date, date]:
    output: list[date] = []
    cursor = trade_date - timedelta(days=1)
    while len(output) < 3:
        if cursor.weekday() < 5:
            output.append(cursor)
        cursor -= timedelta(days=1)
    return tuple(reversed(output))  # type: ignore[return-value]


def _coverage(
    export: GCSierraChartExport,
    calendars: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ],
) -> GCSierraChartCoverageEvidence:
    starts = tuple(
        row.bar_start_timestamp.replace(tzinfo=TOKYO).astimezone(UTC)
        for row in export.rows
    )
    trade_dates = {
        (start.astimezone(NY).date() + timedelta(days=1))
        if start.astimezone(NY).time() >= time(18)
        else start.astimezone(NY).date()
        for start in starts
    }
    relevant = tuple(
        (item, _calendar_intervals(item))
        for item in calendars
        if item.trade_date in trade_dates and _calendar_intervals(item)
    )
    if not relevant:
        raise ValueError("coverage requires at least one matching open calendar")
    start = min(intervals[0][0] for _, intervals in relevant)
    end = max(intervals[-1][1] for _, intervals in relevant)
    evidence_hash = hashlib.sha256(
        f"{export.source_id}:{start.isoformat()}:{end.isoformat()}".encode()
    ).hexdigest()
    coverage_id = make_gc_dataset_id(
        identity_kind="COVERAGE",
        source_id=export.source_id,
        source_name=export.source_name,
        source_sha256=export.source_sha256,
        contract=export.contract,
        role=export.role,
        capture_timestamp=export.capture_timestamp,
        source_timezone=export.chart_timezone,
        timeframe=export.timeframe,
        coverage_start_timestamp=start,
        coverage_end_timestamp=end,
        acquisition_completed_timestamp=end,
        acquisition_evidence_sha256=evidence_hash,
    )
    return GCSierraChartCoverageEvidence(
        coverage_id,
        export.source_id,
        export.source_name,
        export.source_sha256,
        export.contract,
        export.role,
        export.capture_timestamp,
        export.chart_timezone,
        export.timeframe,
        start,
        end,
        end,
        evidence_hash,
    )


def _coverage_per_session(
    export: GCSierraChartExport,
    calendars: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ],
) -> tuple[GCSierraChartCoverageEvidence, ...]:
    output: list[GCSierraChartCoverageEvidence] = []
    starts = {
        row.bar_start_timestamp.replace(tzinfo=TOKYO).astimezone(UTC)
        for row in export.rows
    }
    for calendar in calendars:
        intervals = _calendar_intervals(calendar)
        if not intervals:
            continue
        opening = intervals[0][0]
        closing = intervals[-1][1]
        completed = (
            closing + timedelta(minutes=1)
            if isinstance(calendar, GCSplitSessionCalendarEntry)
            else closing
        )
        if closing > export.capture_timestamp:
            continue
        if not any(
            interval_start <= start < interval_end
            for start in starts
            for interval_start, interval_end in intervals
        ):
            continue
        evidence_hash = hashlib.sha256(
            f"{export.source_id}:{opening.isoformat()}:{closing.isoformat()}".encode()
        ).hexdigest()
        coverage_id = make_gc_dataset_id(
            identity_kind="COVERAGE",
            source_id=export.source_id,
            source_name=export.source_name,
            source_sha256=export.source_sha256,
            contract=export.contract,
            role=export.role,
            capture_timestamp=export.capture_timestamp,
            source_timezone=export.chart_timezone,
            timeframe=export.timeframe,
            coverage_start_timestamp=opening,
            coverage_end_timestamp=closing,
            acquisition_completed_timestamp=completed,
            acquisition_evidence_sha256=evidence_hash,
        )
        output.append(
            GCSierraChartCoverageEvidence(
                coverage_id,
                export.source_id,
                export.source_name,
                export.source_sha256,
                export.contract,
                export.role,
                export.capture_timestamp,
                export.chart_timezone,
                export.timeframe,
                opening,
                closing,
                completed,
                evidence_hash,
            )
        )
    return tuple(output)


def _reidentify_coverage(
    item: GCSierraChartCoverageEvidence,
    **changes: object,
) -> GCSierraChartCoverageEvidence:
    values: dict[str, object] = {
        "source_id": item.source_id,
        "source_name": item.source_name,
        "source_sha256": item.source_sha256,
        "contract": item.contract,
        "role": item.role,
        "capture_timestamp": item.capture_timestamp,
        "chart_timezone": item.chart_timezone,
        "timeframe": item.timeframe,
        "coverage_start_timestamp": item.coverage_start_timestamp,
        "coverage_end_timestamp": item.coverage_end_timestamp,
        "acquisition_completed_timestamp": item.acquisition_completed_timestamp,
        "acquisition_evidence_sha256": item.acquisition_evidence_sha256,
    }
    values.update(changes)
    coverage_id = make_gc_dataset_id(
        identity_kind="COVERAGE",
        source_id=values["source_id"],
        source_name=values["source_name"],
        source_sha256=values["source_sha256"],
        contract=values["contract"],
        role=values["role"],
        capture_timestamp=values["capture_timestamp"],
        source_timezone=values["chart_timezone"],
        timeframe=values["timeframe"],
        coverage_start_timestamp=values["coverage_start_timestamp"],
        coverage_end_timestamp=values["coverage_end_timestamp"],
        acquisition_completed_timestamp=values["acquisition_completed_timestamp"],
        acquisition_evidence_sha256=values["acquisition_evidence_sha256"],
    )
    return GCSierraChartCoverageEvidence(
        coverage_id=coverage_id,
        **values,  # type: ignore[arg-type]
    )


def _sorted_exports(
    exports: tuple[GCSierraChartExport, ...],
) -> tuple[GCSierraChartExport, ...]:
    def key(item: GCSierraChartExport) -> tuple[object, ...]:
        try:
            contract_key: tuple[int, int] = dataset._contract_key(item.contract)
        except (TypeError, ValueError):
            contract_key = (9999, 9999)
        role = item.role.value if isinstance(item.role, GCSourceRole) else "~"
        source_hash = item.source_sha256 if isinstance(item.source_sha256, str) else "~"
        return contract_key, role, source_hash

    return tuple(
        sorted(exports, key=key)
    )


def _sorted_coverage(
    coverage: tuple[GCSierraChartCoverageEvidence, ...],
) -> tuple[GCSierraChartCoverageEvidence, ...]:
    return tuple(
        sorted(
            coverage,
            key=lambda item: (
                item.coverage_start_timestamp.astimezone(UTC),
                item.coverage_end_timestamp.astimezone(UTC),
                dataset._contract_key(item.contract),
                item.role.value,
                item.coverage_id,
            ),
        )
    )


def _config(**changes: object) -> GCDatasetBuildConfig:
    values: dict[str, object] = {
        "instrument": "gc",
        "timeframe": "5m",
        "source_timezone": "Asia/Tokyo",
        "exchange_timezone": "America/New_York",
        "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
        "initial_contract": "GCG26-COMEX",
        "initial_trade_date": D1,
        "roll_confirmation_sessions": 3,
        "oos_start_trade_date": date(2026, 2, 2),
        "oos_end_trade_date": date(2026, 2, 27),
    }
    values.update(changes)
    return GCDatasetBuildConfig(**values)  # type: ignore[arg-type]


def _build(
    *,
    exports: tuple[GCSierraChartExport, ...] | None = None,
    coverage: tuple[GCSierraChartCoverageEvidence, ...] | None = None,
    calendars: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ] | None = None,
    config: GCDatasetBuildConfig | None = None,
    auto_dependencies: bool = True,
    coverage_mutator: Callable[
        [tuple[GCSierraChartCoverageEvidence, ...]],
        tuple[GCSierraChartCoverageEvidence, ...],
    ]
    | None = None,
) -> GCDatasetBuildResult:
    selected_config = _config() if config is None else config
    selected_calendars = (_calendar(D1),) if calendars is None else calendars
    selected_exports = (_export(),) if exports is None else exports
    if auto_dependencies and selected_exports and selected_calendars:
        prior_dates = _prior_eligible_dates(selected_config.initial_trade_date)
        prior_calendars = tuple(_calendar(day) for day in prior_dates)
        calendar_map = {item.trade_date: item for item in prior_calendars + selected_calendars}
        selected_calendars = tuple(calendar_map[key] for key in sorted(calendar_map))
        if any(item.contract == selected_config.initial_contract for item in selected_exports):
            predecessor = dataset._previous_contract(selected_config.initial_contract)
            proof_current = _export(
                selected_config.initial_contract,
                tuple((day, 20) for day in prior_dates),
                source_name="initial_current_proof.txt",
            )
            proof_predecessor = _export(
                predecessor,
                tuple((day, 10) for day in prior_dates),
                source_name="initial_predecessor_proof.txt",
            )
            additions = [proof_current, proof_predecessor]
            adjacent = dataset._next_contract(selected_config.initial_contract)
            if not any(item.contract == adjacent for item in selected_exports):
                active_dates = tuple(
                    item.trade_date
                    for item in selected_calendars
                    if _calendar_status(item)
                    is not KillZoneSessionStatus.SESSION_CLOSED
                    and selected_config.initial_trade_date
                    <= item.trade_date
                    <= selected_config.oos_end_trade_date
                )
                if active_dates:
                    active_closes = tuple(
                        _calendar_intervals(item)[-1][1]
                        for item in selected_calendars
                        if item.trade_date in active_dates
                        and _calendar_intervals(item)
                    )
                    if active_closes:
                        active_entries = tuple(
                            item
                            for item in selected_calendars
                            if item.trade_date in active_dates
                            and _calendar_intervals(item)
                        )
                        if any(
                            isinstance(item, GCSplitSessionCalendarEntry)
                            for item in active_entries
                        ):
                            starts = tuple(
                                start
                                for item in active_entries
                                for interval_start, interval_end in _calendar_intervals(item)
                                for start in (
                                    interval_start
                                    + offset * timedelta(minutes=5)
                                    for offset in range(
                                        int(
                                            (interval_end - interval_start)
                                            / timedelta(minutes=5)
                                        )
                                    )
                                )
                            )
                            additions.append(
                                _export(
                                    adjacent,
                                    tuple((day, 5) for day in active_dates),
                                    source_name="adjacent_roll_evidence.txt",
                                    raw_bytes=_raw_starts(
                                        starts,
                                        tuple(1 for _ in starts),
                                        price=Decimal("4100.0"),
                                    ),
                                    capture_timestamp=max(active_closes)
                                    + timedelta(minutes=1),
                                )
                            )
                        else:
                            additions.append(
                                _export(
                                    adjacent,
                                    tuple((day, 5) for day in active_dates),
                                    source_name="adjacent_roll_evidence.txt",
                                    capture_timestamp=max(active_closes)
                                    + timedelta(minutes=1),
                                )
                            )
            selected_exports = _sorted_exports(selected_exports + tuple(additions))
    if coverage is None:
        generated: list[GCSierraChartCoverageEvidence] = []
        for item in selected_exports:
            try:
                generated.extend(_coverage_per_session(item, selected_calendars))
            except (TypeError, ValueError):
                continue
        selected_coverage = _sorted_coverage(tuple(generated))
    else:
        selected_coverage = coverage
    if coverage_mutator is not None:
        selected_coverage = coverage_mutator(selected_coverage)
    return build_gc_futures_dataset(
        exports=selected_exports,
        coverage_evidence=selected_coverage,
        calendar_entries=selected_calendars,
        config=selected_config,
    )


def _manual_scope(
    *,
    current_prior_volumes: tuple[int, int, int] = (20, 20, 20),
    predecessor_prior_volumes: tuple[int, int, int] = (10, 10, 10),
    current_dates: tuple[date, ...] = (D1,),
    current_volumes: tuple[int, ...] = (10,),
    adjacent_volumes: tuple[int, ...] = (5,),
    include_predecessor: bool = True,
    include_adjacent: bool = True,
    config: GCDatasetBuildConfig | None = None,
) -> tuple[
    tuple[GCSierraChartExport, ...],
    tuple[GCSierraChartCoverageEvidence, ...],
    tuple[KillZoneCalendarEntry, ...],
    GCDatasetBuildConfig,
]:
    selected_config = _config() if config is None else config
    prior_dates = _prior_eligible_dates(selected_config.initial_trade_date)
    calendars = tuple(
        _calendar(day) for day in prior_dates + current_dates
    )
    current_sessions = tuple(
        zip(prior_dates, current_prior_volumes, strict=True)
    ) + tuple(zip(current_dates, current_volumes, strict=True))
    current = _export(
        selected_config.initial_contract,
        current_sessions,
        source_name="manual_current.txt",
    )
    exports: list[GCSierraChartExport] = [current]
    if include_predecessor:
        exports.append(
            _export(
                dataset._previous_contract(selected_config.initial_contract),
                tuple(zip(prior_dates, predecessor_prior_volumes, strict=True)),
                source_name="manual_predecessor.txt",
            )
        )
    if include_adjacent:
        exports.append(
            _export(
                dataset._next_contract(selected_config.initial_contract),
                tuple(zip(current_dates, adjacent_volumes, strict=True)),
                source_name="manual_adjacent.txt",
            )
        )
    ordered_exports = _sorted_exports(tuple(exports))
    coverage = _sorted_coverage(
        tuple(
            evidence
            for export in ordered_exports
            for evidence in _coverage_per_session(export, calendars)
        )
    )
    return ordered_exports, coverage, calendars, selected_config


def _segment_id(**changes: object) -> str:
    values: dict[str, object] = {
        "identity_kind": "SEGMENT",
        "config": _config(),
        "contract": "GCG26-COMEX",
        "partition": GCSegmentPartition.DEVELOPMENT,
        "first_trade_date": D1,
        "last_trade_date": D1,
        "source_ids": (HASH_A,),
        "bar_digest": HASH_B,
        "preceding_missing_bar_count": 0,
    }
    values.update(changes)
    return make_gc_dataset_id(**values)  # type: ignore[arg-type]


def _dataset_id(**changes: object) -> str:
    values: dict[str, object] = {
        "identity_kind": "DATASET",
        "config": _config(),
        "source_ids": (HASH_A,),
        "coverage_ids": (HASH_B,),
        "segment_ids": (HASH_B,),
        "calendar_digest": HASH_C,
        "coverage_digest": "e" * 64,
        "evidence_digest": "d" * 64,
        "roll_trade_dates": (),
    }
    values.update(changes)
    return make_gc_dataset_id(**values)  # type: ignore[arg-type]


def _coverage_id(**changes: object) -> str:
    export = _export()
    opening, closing = _bounds(D1)
    values: dict[str, object] = {
        "identity_kind": "COVERAGE",
        "source_id": export.source_id,
        "source_name": export.source_name,
        "source_sha256": export.source_sha256,
        "contract": export.contract,
        "role": export.role,
        "capture_timestamp": export.capture_timestamp,
        "source_timezone": export.chart_timezone,
        "timeframe": export.timeframe,
        "coverage_start_timestamp": opening,
        "coverage_end_timestamp": closing,
        "acquisition_completed_timestamp": closing,
        "acquisition_evidence_sha256": HASH_A,
    }
    values.update(changes)
    return make_gc_dataset_id(**values)  # type: ignore[arg-type]


# Case 1
@pytest.mark.parametrize(
    "missing", ["exports", "coverage_evidence", "calendar_entries"]
)
def test_case_01_missing_context_is_unknown(missing: str) -> None:
    export = _export()
    calendar = _calendar(D1)
    kwargs: dict[str, object] = {
        "exports": (export,),
        "coverage_evidence": (_coverage(export, (calendar,)),),
        "calendar_entries": (calendar,),
        "config": _config(),
    }
    kwargs[missing] = None
    result = build_gc_futures_dataset(**kwargs)  # type: ignore[arg-type]
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert result.segments == () and result.manifest is None


def test_case_01_malformed_counterpart_overrides_missing_unknown() -> None:
    malformed = replace(_export(), source_sha256="bad")
    result = build_gc_futures_dataset(
        exports=(malformed,),
        coverage_evidence=(),
        calendar_entries=None,
        config=_config(),
    )
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.segments == () and result.manifest is None


@pytest.mark.parametrize("missing", ["exports", "calendar_entries"])
def test_case_01_malformed_coverage_overrides_missing_unknown(
    missing: str,
) -> None:
    export = _export()
    calendar = _calendar(D1)
    malformed = replace(
        _coverage(export, (calendar,)),
        acquisition_evidence_sha256="not-a-sha256",
    )
    kwargs: dict[str, object] = {
        "exports": (export,),
        "coverage_evidence": (malformed,),
        "calendar_entries": (calendar,),
        "config": _config(),
    }
    kwargs[missing] = None
    result = build_gc_futures_dataset(**kwargs)  # type: ignore[arg-type]
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.segments == () and result.manifest is None


# Case 2
def test_case_02_valid_empty_scope_is_none() -> None:
    result = _build(exports=(), coverage=(), calendars=())
    assert result.status is GCDatasetBuildStatus.NONE
    assert result.dataset_id is None
    assert result.segments == () and result.manifest is None


# Case 3
@pytest.mark.parametrize(
    "contract",
    ["GC", "GC[M]", "GCQ26-CME", "XAUUSD", "GCX26-COMEX", "GCQ2026-COMEX"],
)
def test_case_03_contract_tokens_fail_closed(contract: str) -> None:
    with pytest.raises((TypeError, ValueError)):
        _export(contract=contract)


# Case 4
def test_case_04_runtime_timezone_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    mismatch = _build(config=_config(timezone_data_version="wrong"))
    assert mismatch.status is GCDatasetBuildStatus.INVALID
    monkeypatch.setattr(dataset, "_runtime_timezone_data_version", lambda: None)
    unavailable = _build()
    assert unavailable.status is GCDatasetBuildStatus.INVALID


# Case 5
def test_case_05_exact_constants() -> None:
    assert (
        GC_DATASET_BUILDER_VERSION
        == "GC-DATASET-BUILDER-V3-SPLIT-SESSION"
    )
    assert GC_DATASET_INSTRUMENT == "GC"
    assert GC_DATASET_TIMEFRAME == "5M"
    assert GC_DATASET_SOURCE_TIMEZONE == "Asia/Tokyo"
    assert GC_DATASET_EXCHANGE_TIMEZONE == "America/New_York"
    assert GC_DATASET_TICK_SIZE == Decimal("0.1")
    assert GC_ROLL_CONFIRMATION_SESSIONS == 3
    assert GC_DELIVERY_MONTH_CODES == ("G", "J", "M", "Q", "V", "Z")


def test_case_05_synthetic_zero_trade_zero_volume_row_is_rejected() -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    parts = [part.strip() for part in lines[1].split(",")]
    parts[6] = "0"
    parts[7] = "0"
    parts[11] = "0"
    parts[12] = "0"
    lines[1] = ", ".join(parts)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


# Case 6
@pytest.mark.parametrize(
    "header",
    ["bad", HEADER + ", Extra", HEADER.replace("Open, High", "High, Open")],
)
def test_case_06_exact_header(header: str) -> None:
    body = _raw(((D1, 10),)).decode().splitlines()
    body[0] = header
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(body) + "\n").encode())


def test_case_06_absent_interval_never_emits_inferred_bar() -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    export = _export(raw_bytes=("\n".join(lines[:2]) + "\n").encode())
    result = _build(exports=(export,))
    assert result.status is GCDatasetBuildStatus.VALID
    assert sum(len(segment.bars) for segment in result.segments) == 1
    assert result.manifest is not None
    assert result.manifest.missing_bar_count == 1
    assert result.manifest.attested_no_trade_interval_count == 0


# Case 7
@pytest.mark.parametrize("mutation", ["blank", "short", "long"])
def test_case_07_row_field_count_and_blank_rejection(mutation: str) -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    if mutation == "blank":
        lines.insert(2, "")
    elif mutation == "short":
        lines[1] = ",".join(lines[1].split(",")[:-1])
    else:
        lines[1] += ", extra"
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


def test_case_07_coverage_contract_is_frozen_and_utc_normalized() -> None:
    export = _export()
    evidence = _coverage(export, (_calendar(D1),))
    equivalent = _reidentify_coverage(
        evidence,
        coverage_start_timestamp=evidence.coverage_start_timestamp.astimezone(TOKYO),
        coverage_end_timestamp=evidence.coverage_end_timestamp.astimezone(TOKYO),
        acquisition_completed_timestamp=evidence.acquisition_completed_timestamp.astimezone(TOKYO),
    )
    assert equivalent.coverage_id == evidence.coverage_id
    assert GCSierraChartCoverageEvidence.__dataclass_params__.frozen is True
    with pytest.raises(FrozenInstanceError):
        evidence.contract = "GCJ26-COMEX"  # type: ignore[misc]


# Case 8
def test_case_08_raw_timestamp_is_naive_bar_start() -> None:
    export = _export()
    assert export.rows[0].bar_start_timestamp.tzinfo is None
    assert export.rows[0].bar_start_timestamp.hour == 8


def test_case_08_coverage_source_identity_must_reconcile() -> None:
    export = _export()
    evidence = _coverage(export, (_calendar(D1),))
    malformed = replace(evidence, source_id=HASH_A)
    result = _build(
        exports=(export,),
        coverage=(malformed,),
        calendars=(_calendar(D1),),
        auto_dependencies=False,
    )
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.manifest is None


# Case 9
def test_case_09_tokyo_start_converts_to_utc_close() -> None:
    result = _build()
    opening, _ = _bounds(D1)
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.segments[0].bars[0].timestamp == opening + timedelta(minutes=5)


@pytest.mark.parametrize(
    "changes",
    [
        {"coverage_end_timestamp": _bounds(D1)[0]},
        {"acquisition_completed_timestamp": _bounds(D1)[0]},
        {"acquisition_completed_timestamp": _bounds(D1)[1] + timedelta(minutes=2)},
    ],
)
def test_case_09_coverage_range_and_completion_ordering(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(**changes)


# Case 10
def test_case_10_capture_boundary() -> None:
    opening, _ = _bounds(D1)
    assert _export(capture_timestamp=opening + timedelta(minutes=10))
    with pytest.raises((TypeError, ValueError)):
        _export(capture_timestamp=opening + timedelta(minutes=9, seconds=59))


@pytest.mark.parametrize(
    "evidence_hash", [None, True, "screenshot.png", "10 rows", "1.2s"]
)
def test_case_10_only_sha256_proves_acquisition(
    evidence_hash: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(acquisition_evidence_sha256=evidence_hash)


# Case 11
def test_case_11_decimal_tick_and_ohlc_geometry() -> None:
    bad_tick = _raw(((D1, 10),), price=Decimal("4000.05"))
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=bad_tick)
    lines = _raw(((D1, 10),)).decode().splitlines()
    fields = [part.strip() for part in lines[1].split(",")]
    fields[3], fields[4] = "3999.0", "4001.0"
    lines[1] = ", ".join(fields)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


def test_case_11_coverage_order_and_overlap_are_fail_closed() -> None:
    export = _export(capture_timestamp=_bounds(D1)[1] + timedelta(minutes=5))
    base = _coverage(export, (_calendar(D1),))
    opening, closing = _bounds(D1)
    first = _reidentify_coverage(
        base,
        coverage_end_timestamp=opening + timedelta(minutes=5),
        acquisition_completed_timestamp=opening + timedelta(minutes=5),
    )
    second = _reidentify_coverage(
        base,
        coverage_start_timestamp=opening + timedelta(minutes=5),
        coverage_end_timestamp=closing,
        acquisition_completed_timestamp=closing,
    )
    out_of_order = _build(
        exports=(export,), coverage=(second, first), calendars=(_calendar(D1),),
        auto_dependencies=False,
    )
    assert out_of_order.status is GCDatasetBuildStatus.INVALID
    overlapping = _reidentify_coverage(
        base,
        coverage_start_timestamp=opening + timedelta(minutes=4),
        acquisition_completed_timestamp=closing,
    )
    overlap = _build(
        exports=(export,), coverage=_sorted_coverage((base, overlapping)),
        calendars=(_calendar(D1),), auto_dependencies=False,
    )
    assert overlap.status is GCDatasetBuildStatus.INVALID


# Case 12
@pytest.mark.parametrize("value", ["True", "nan", "inf", "1,000.0"])
def test_case_12_malformed_decimal_does_not_leak(value: str) -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    fields = [part.strip() for part in lines[1].split(",")]
    fields[2] = value
    lines[1] = ", ".join(fields)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


def test_case_12_export_row_outside_coverage_is_invalid() -> None:
    export = _export(capture_timestamp=_bounds(D1)[1] + timedelta(minutes=1))
    evidence = _coverage(export, (_calendar(D1),))
    opening, _ = _bounds(D1)
    first_slot_only = _reidentify_coverage(
        evidence,
        coverage_end_timestamp=opening + timedelta(minutes=5),
        acquisition_completed_timestamp=opening + timedelta(minutes=5),
    )
    result = _build(
        exports=(export,), coverage=(first_slot_only,),
        calendars=(_calendar(D1),), auto_dependencies=False,
    )
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.manifest is None


# Case 13
@pytest.mark.parametrize("field,value", [(6, "-1"), (7, "1.5"), (11, "True"), (12, "-2")])
def test_case_13_integer_volume_contract(field: int, value: str) -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    parts = [part.strip() for part in lines[1].split(",")]
    parts[field] = value
    lines[1] = ", ".join(parts)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


def test_case_13_volume_conservation() -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    parts = [part.strip() for part in lines[1].split(",")]
    parts[12] = str(int(parts[12]) + 1)
    lines[1] = ", ".join(parts)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


# Case 14
def test_case_14_ignored_averages_only_change_source_hash() -> None:
    first = _export(raw_bytes=_raw(((D1, 10),)))
    second = _export(
        source_name="second.txt",
        raw_bytes=_raw(((D1, 10),), average_suffix="0"),
    )
    assert first.rows == second.rows
    assert first.source_sha256 != second.source_sha256


# Case 15
def test_case_15_no_silent_row_sort() -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    lines[1], lines[2] = lines[2], lines[1]
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode())


def test_case_15_unattested_required_session_volume_is_unknown() -> None:
    result = _build(coverage=())
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert "COVERAGE_UNVERIFIED" in result.blocking_reasons
    assert result.manifest is None


# Case 16
def test_case_16_source_hash_recomputed_from_exact_bytes() -> None:
    raw = _raw(((D1, 10),))
    export = _export(raw_bytes=raw)
    assert export.source_sha256 == hashlib.sha256(raw).hexdigest()
    assert _export(source_name="changed.txt", raw_bytes=raw).source_id != export.source_id


# Case 17
@pytest.mark.parametrize("name", ["", "../bad.txt", "folder/bad.txt", "folder\\bad.txt"])
def test_case_17_source_name_is_basename(name: str) -> None:
    with pytest.raises((TypeError, ValueError)):
        _export(source_name=name)


# Case 18
def test_case_18_conflicting_duplicate_source_hash_is_invalid() -> None:
    first = _export()
    conflicting = replace(first, role=GCSourceRole.OOS_HOLDOUT)
    result = _build(exports=(first, conflicting))
    assert result.status is GCDatasetBuildStatus.INVALID


# Case 19
@pytest.mark.parametrize("trade_date", [date(2026, 1, 6), date(2026, 7, 6)])
def test_case_19_timezone_conversion_is_dst_aware(trade_date: date) -> None:
    export = _export(sessions=((trade_date, 10),))
    result = _build(
        exports=(export,),
        calendars=(_calendar(trade_date),),
        config=_config(
            initial_trade_date=trade_date,
            oos_start_trade_date=trade_date + timedelta(days=20),
            oos_end_trade_date=trade_date + timedelta(days=40),
        ),
    )
    opening, _ = _bounds(trade_date)
    assert result.segments[0].bars[0].timestamp == opening + timedelta(minutes=5)


# Case 20
def test_case_20_calendar_boundaries_are_start_inclusive_end_exclusive() -> None:
    result = _build()
    assert result.status is GCDatasetBuildStatus.VALID
    assert len(result.segments[0].bars) == 2


def test_case_20_split_session_maps_both_intervals_to_one_trade_date() -> None:
    opening, _ = _bounds(D1)
    starts = tuple(
        opening + timedelta(minutes=offset)
        for offset in (0, 5, 20, 25)
    )
    export = _export(
        source_name="split-session.txt",
        raw_bytes=_raw_starts(starts, (10, 20, 30, 40)),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    result = _build(exports=(export,), calendars=(_split_calendar(D1),))
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    session_segments = tuple(
        segment
        for segment in result.segments
        if segment.first_trade_date == D1
    )
    assert len(session_segments) == 2
    assert sum(len(segment.bars) for segment in session_segments) == 4
    assert session_segments[1].preceding_missing_bar_count == 0
    assert ("GCG26-COMEX", D1, 100) in (
        result.manifest.completed_session_volumes
    )
    assert result.manifest.missing_bar_count == 0
    assert result.manifest.attested_no_trade_interval_count == 1


def test_case_20_positive_row_in_official_gap_is_invalid() -> None:
    opening, _ = _bounds(D1)
    export = _export(
        source_name="gap-positive.txt",
        raw_bytes=_raw_starts(
            (opening, opening + timedelta(minutes=15)),
            (10, 10),
        ),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    result = _build(exports=(export,), calendars=(_split_calendar(D1),))
    assert result.status is GCDatasetBuildStatus.INVALID
    assert "ROW_OUTSIDE_DECLARED_SESSION" in result.blocking_reasons
    assert result.manifest is None


def test_case_20_zero_volume_row_in_official_gap_is_excluded() -> None:
    opening, _ = _bounds(D1)
    export = _export(
        source_name="gap-zero.txt",
        raw_bytes=_raw_starts(
            (
                opening,
                opening + timedelta(minutes=5),
                opening + timedelta(minutes=15),
                opening + timedelta(minutes=20),
                opening + timedelta(minutes=25),
            ),
            (10, 10, 0, 10, 10),
        ),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    result = _build(exports=(export,), calendars=(_split_calendar(D1),))
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    assert ("OUTSIDE_SESSION_ZERO_VOLUME", 1) in (
        result.manifest.exclusion_counts
    )


# Case 21
def test_case_21_early_close_rejects_later_positive_row() -> None:
    export = _export(
        raw_bytes=_raw(((D1, 10),), second_offset_minutes=10),
        capture_timestamp=_bounds(D1)[1] + timedelta(minutes=6),
    )
    result = _build(exports=(export,))
    assert result.status is GCDatasetBuildStatus.INVALID


# Case 22
def test_case_22_closed_or_maintenance_positive_volume_is_invalid() -> None:
    closed = _build(calendars=(_calendar(D1, status=KillZoneSessionStatus.SESSION_CLOSED),))
    assert closed.status is GCDatasetBuildStatus.INVALID
    opening, closing = _bounds(D1)
    maintenance_start = datetime.combine(D1, time(17), tzinfo=NY).astimezone(UTC)
    local = maintenance_start.astimezone(TOKYO).replace(tzinfo=None)
    raw = _raw(((D1, 10),))
    lines = raw.decode().splitlines()
    parts = [x.strip() for x in lines[1].split(",")]
    parts[0], parts[1] = f"{local.year}-{local.month}-{local.day}", local.strftime("%H:%M:%S.%f")
    lines[1] = ", ".join(parts)
    with pytest.raises((TypeError, ValueError)):
        _export(raw_bytes=("\n".join(lines) + "\n").encode(), capture_timestamp=closing + timedelta(days=1))


def test_case_22_initial_contract_requires_exact_three_session_proof() -> None:
    exports, coverage, calendars, config = _manual_scope()
    result = build_gc_futures_dataset(
        exports=exports,
        coverage_evidence=coverage,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    prior_dates = _prior_eligible_dates(config.initial_trade_date)
    assert all(
        (config.initial_contract, day, 20)
        in result.manifest.completed_session_volumes
        for day in prior_dates
    )


# Case 23
def test_case_23_missing_calendar_unknown_malformed_calendar_invalid() -> None:
    missing = _build(calendars=())
    assert missing.status is GCDatasetBuildStatus.UNKNOWN
    malformed = replace(_calendar(D1), session_close_timestamp=None)
    invalid = _build(calendars=(malformed,))
    assert invalid.status is GCDatasetBuildStatus.INVALID


def test_case_23_authoritative_2024_and_2025_split_session_moments() -> None:
    entry_2024 = GCSplitSessionCalendarEntry(
        CALENDAR_VERSION,
        date(2024, 11, 29),
        (
            GCDatasetSessionInterval(
                datetime(2024, 11, 27, 18, tzinfo=NY),
                datetime(2024, 11, 28, 14, 30, tzinfo=NY),
            ),
            GCDatasetSessionInterval(
                datetime(2024, 11, 28, 18, tzinfo=NY),
                datetime(2024, 11, 29, 14, 45, tzinfo=NY),
            ),
        ),
        ("CME-GCC-04687271-FINAL",),
        (AUTHENTICATED_CME_EMAIL_SHA256,),
    )
    entry_2025 = GCSplitSessionCalendarEntry(
        CALENDAR_VERSION,
        date(2025, 11, 28),
        (
            GCDatasetSessionInterval(
                datetime(2025, 11, 27, 18, tzinfo=NY),
                datetime(2025, 11, 27, 21, 40, tzinfo=NY),
            ),
            GCDatasetSessionInterval(
                datetime(2025, 11, 28, 8, 30, tzinfo=NY),
                datetime(2025, 11, 28, 17, tzinfo=NY),
            ),
        ),
        ("CME-GCC-04687271-FINAL",),
        (AUTHENTICATED_CME_EMAIL_SHA256,),
    )
    normalized, issues = dataset._scan_calendars(
        (entry_2024, entry_2025), _config()
    )
    assert issues == ()
    assert normalized[0].trade_date == date(2024, 11, 29)
    assert normalized[0].intervals[0][1] == datetime(
        2024, 11, 28, 14, 30, tzinfo=NY
    ).astimezone(UTC)
    assert normalized[1].intervals[1][0] == datetime(
        2025, 11, 28, 8, 30, tzinfo=NY
    ).astimezone(UTC)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("one_interval", "SPLIT_SESSION_REQUIRES_MULTIPLE_INTERVALS"),
        ("touching", "SPLIT_SESSION_INTERVALS_TOUCH"),
        ("out_of_order", "SPLIT_SESSION_INTERVALS_OUT_OF_ORDER"),
        ("overlap", "SPLIT_SESSION_INTERVAL_OVERLAP"),
        ("off_grid", "SPLIT_SESSION_INTERVAL_OFF_GRID"),
        ("naive", "MALFORMED_CALENDAR_ENTRY"),
        ("non_tuple", "SPLIT_SESSION_INTERVALS_NOT_TUPLE"),
        ("source_order", "CALENDAR_SOURCE_ARTIFACTS_OUT_OF_ORDER"),
        ("source_lengths", "CALENDAR_SOURCE_ARTIFACT_LENGTH_MISMATCH"),
        ("source_duplicate", "DUPLICATE_CALENDAR_SOURCE_ARTIFACT"),
        ("bad_hash", "MALFORMED_CALENDAR_ENTRY"),
    ],
)
def test_case_23_split_calendar_malformed_shapes_fail_closed(
    mutation: str,
    reason: str,
) -> None:
    opening, _ = _bounds(D1)
    intervals = (
        GCDatasetSessionInterval(opening, opening + timedelta(minutes=10)),
        GCDatasetSessionInterval(
            opening + timedelta(minutes=20),
            opening + timedelta(minutes=30),
        ),
    )
    ids = ("A", "B")
    hashes = (HASH_A, HASH_B)
    if mutation == "one_interval":
        intervals = intervals[:1]
    elif mutation == "touching":
        intervals = (
            intervals[0],
            GCDatasetSessionInterval(
                intervals[0].end_timestamp,
                intervals[0].end_timestamp + timedelta(minutes=10),
            ),
        )
    elif mutation == "overlap":
        intervals = (
            intervals[0],
            GCDatasetSessionInterval(
                opening + timedelta(minutes=5),
                opening + timedelta(minutes=15),
            ),
        )
    elif mutation == "out_of_order":
        intervals = (intervals[1], intervals[0])
    elif mutation == "off_grid":
        intervals = (
            intervals[0],
            GCDatasetSessionInterval(
                opening + timedelta(minutes=21),
                opening + timedelta(minutes=31),
            ),
        )
    elif mutation == "naive":
        intervals = (
            intervals[0],
            GCDatasetSessionInterval(
                (opening + timedelta(minutes=20)).replace(tzinfo=None),
                opening + timedelta(minutes=30),
            ),
        )
    elif mutation == "source_order":
        ids = ("B", "A")
    elif mutation == "source_lengths":
        hashes = (HASH_A,)
    elif mutation == "source_duplicate":
        ids = ("A", "A")
    elif mutation == "bad_hash":
        hashes = (HASH_A, "bad")
    item = _split_calendar(
        D1,
        intervals=intervals,
        source_artifact_ids=ids,
        source_artifact_sha256s=hashes,
    )
    if mutation == "non_tuple":
        item = replace(item, intervals=list(intervals))  # type: ignore[arg-type]
    _, issues = dataset._scan_calendars((item,), _config())
    assert any(issue.reason == reason for issue in issues)


def test_case_23_split_calendar_global_interval_overlap_is_invalid() -> None:
    opening, _ = _bounds(D1)
    first = _split_calendar(D1)
    second = _split_calendar(
        D2,
        intervals=(
            GCDatasetSessionInterval(
                opening + timedelta(minutes=25),
                opening + timedelta(minutes=35),
            ),
            GCDatasetSessionInterval(
                opening + timedelta(minutes=40),
                opening + timedelta(minutes=50),
            ),
        ),
    )
    _, issues = dataset._scan_calendars((first, second), _config())
    assert any(issue.reason == "CALENDAR_INTERVAL_OVERLAP" for issue in issues)


def test_case_23_missing_exact_predecessor_blocks_initial_acceptance() -> None:
    exports, coverage, calendars, config = _manual_scope(
        include_predecessor=False
    )
    result = build_gc_futures_dataset(
        exports=exports,
        coverage_evidence=coverage,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert "INITIAL_PREDECESSOR_COVERAGE_MISSING" in result.blocking_reasons
    assert result.manifest is None


# Case 24
def test_case_24_trade_date_assignment_uses_new_york_session() -> None:
    export = _export()
    result = _build(exports=(export,))
    assert result.manifest is not None
    assert result.segments[0].first_trade_date == D1


def test_case_24_later_start_is_not_auto_accepted_without_predecessor_proof() -> None:
    config = _config(initial_contract="GCJ26-COMEX")
    exports, coverage, calendars, config = _manual_scope(
        config=config,
        include_predecessor=False,
    )
    result = build_gc_futures_dataset(
        exports=exports,
        coverage_evidence=coverage,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert "INITIAL_PREDECESSOR_COVERAGE_MISSING" in result.blocking_reasons


# Case 25
def test_case_25_attested_sparse_session_is_completed_without_synthetic_bar() -> None:
    raw = _raw(((D1, 10),)).decode().splitlines()
    export = _export(raw_bytes=("\n".join(raw[:2]) + "\n").encode())
    result = _build(exports=(export,))
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    assert ("GCG26-COMEX", D1, 5) in result.manifest.completed_session_volumes
    assert len(result.segments[0].bars) == 1
    assert result.manifest.missing_bar_count == 1
    assert result.manifest.attested_no_trade_interval_count == 0


# Case 26
def test_case_26_overlapping_rows_reconcile_or_fail() -> None:
    first = _export(source_name="a.txt")
    equal = _export(source_name="b.txt", raw_bytes=_raw(((D1, 10),), average_suffix="0"))
    ordered_equal = tuple(sorted((first, equal), key=lambda item: item.source_sha256))
    assert _build(exports=ordered_equal).status is GCDatasetBuildStatus.VALID
    conflict = _export(source_name="c.txt", sessions=((D1, 12),))
    ordered_conflict = tuple(sorted((first, conflict), key=lambda item: item.source_sha256))
    assert _build(exports=ordered_conflict).status is GCDatasetBuildStatus.INVALID


# Case 27
def test_case_27_missing_bar_splits_and_is_counted() -> None:
    export = _export(
        raw_bytes=_raw(((D1, 10),), second_offset_minutes=10),
        capture_timestamp=_bounds(D1)[1] + timedelta(minutes=6),
    )
    calendar = _calendar(D1, close_minutes=15)
    result = _build(exports=(export,), calendars=(calendar,))
    assert result.status is GCDatasetBuildStatus.VALID
    assert len(result.segments) == 2
    assert result.segments[1].preceding_missing_bar_count == 1
    assert result.manifest is not None and result.manifest.missing_bar_count == 1


# Case 28
def test_case_28_farther_contract_does_not_block_exact_adjacent_comparison() -> None:
    exports = (
        _export("GCG26-COMEX"),
        _export("GCM26-COMEX", source_name="m.txt"),
    )
    result = _build(exports=exports)
    assert result.status is GCDatasetBuildStatus.VALID


def test_case_28_missing_adjacent_completed_coverage_is_unknown() -> None:
    exports, coverage, calendars, config = _manual_scope(
        include_adjacent=False
    )
    result = build_gc_futures_dataset(
        exports=exports,
        coverage_evidence=coverage,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert "ADJACENT_CONTRACT_COVERAGE_MISSING" in result.blocking_reasons


# Case 29
def test_case_29_initial_contract_must_be_supplied() -> None:
    result = _build(config=_config(initial_contract="GCJ26-COMEX"))
    assert result.status is GCDatasetBuildStatus.UNKNOWN


def _roll_inputs(
    later_volumes: tuple[int, ...],
    *,
    current_volumes: tuple[int, ...] | None = None,
    dates: tuple[date, ...] = (D1, D2, D3, D4),
) -> tuple[tuple[GCSierraChartExport, ...], tuple[KillZoneCalendarEntry, ...]]:
    current = current_volumes or tuple(10 for _ in dates)
    g = _export("GCG26-COMEX", tuple(zip(dates, current, strict=True)), source_name="g.txt")
    j = _export("GCJ26-COMEX", tuple(zip(dates, later_volumes, strict=True)), source_name="j.txt")
    m = _export(
        "GCM26-COMEX",
        tuple((day, 1) for day in dates),
        source_name="m_after_roll.txt",
    )
    return (g, j, m), tuple(_calendar(day) for day in dates)


# Case 30
@pytest.mark.parametrize("later", [(20, 20, 5, 5), (20, 5, 20, 5)])
def test_case_30_one_or_two_dominance_sessions_do_not_roll(later: tuple[int, ...]) -> None:
    exports, calendars = _roll_inputs(later)
    result = _build(exports=exports, calendars=calendars)
    assert result.manifest is not None
    assert result.manifest.roll_trade_dates == ()


# Case 31
def test_case_31_third_confirmation_rolls_next_session() -> None:
    exports, calendars = _roll_inputs((20, 20, 20, 1))
    result = _build(exports=exports, calendars=calendars)
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    assert result.manifest.roll_trade_dates == (D4,)
    assert any(segment.contract == "GCJ26-COMEX" for segment in result.segments)


# Case 32
def test_case_32_closed_dates_neither_count_nor_break_confirmation() -> None:
    evidence_dates = (D1, D2, D4, D5)
    exports, _ = _roll_inputs((20, 20, 20, 1), dates=evidence_dates)
    calendars = (
        _calendar(D1),
        _calendar(D2),
        _calendar(D3, status=KillZoneSessionStatus.SESSION_CLOSED),
        _calendar(D4),
        _calendar(D5),
    )
    result = _build(exports=exports, calendars=calendars)
    assert result.manifest is not None
    assert result.manifest.roll_trade_dates == (D5,)


def test_case_32_split_acquisition_must_finish_strictly_after_final_close() -> None:
    opening, _ = _bounds(D1)
    closing = opening + timedelta(minutes=30)
    export = _export(
        source_name="split-acquisition-boundary.txt",
        raw_bytes=_raw_starts(
            tuple(
                opening + timedelta(minutes=offset)
                for offset in (0, 5, 20, 25)
            ),
            (10, 10, 10, 10),
        ),
        capture_timestamp=closing + timedelta(minutes=1),
    )
    baseline = _build(exports=(export,), calendars=(_split_calendar(D1),))
    assert baseline.status is GCDatasetBuildStatus.VALID

    def acquisition_at_close(
        entries: tuple[GCSierraChartCoverageEvidence, ...],
    ) -> tuple[GCSierraChartCoverageEvidence, ...]:
        return tuple(
            _reidentify_coverage(
                item,
                acquisition_completed_timestamp=closing,
            )
            if item.coverage_start_timestamp == opening
            and item.coverage_end_timestamp == closing
            else item
            for item in entries
        )

    ineligible = _build(
        exports=(export,),
        calendars=(_split_calendar(D1),),
        coverage_mutator=acquisition_at_close,
    )
    assert ineligible.status is GCDatasetBuildStatus.UNKNOWN
    assert "COMPARABLE_COMPLETED_VOLUME_MISSING" in ineligible.blocking_reasons
    assert ineligible.manifest is None


# Case 33
def test_case_33_non_dominance_resets_confirmation() -> None:
    dates = (D1, D2, D3, D4, D5)
    exports, calendars = _roll_inputs((20, 20, 5, 20, 20), dates=dates)
    result = _build(exports=exports, calendars=calendars)
    assert result.manifest is not None
    assert result.manifest.roll_trade_dates == ()


# Case 34
def test_case_34_multiple_candidates_use_volume_then_nearer_delivery() -> None:
    dates = (D1, D2, D3, D4)
    g = _export("GCG26-COMEX", tuple((day, 10) for day in dates), source_name="g.txt")
    j = _export("GCJ26-COMEX", tuple((day, 20) for day in dates), source_name="j.txt")
    m = _export("GCM26-COMEX", tuple((day, 20) for day in dates), source_name="m.txt")
    result = _build(exports=(g, j, m), calendars=tuple(_calendar(day) for day in dates))
    assert result.manifest is not None and result.manifest.roll_trade_dates == (D4,)
    rolled = [segment for segment in result.segments if segment.first_trade_date == D4]
    assert rolled and rolled[0].contract == "GCJ26-COMEX"


def test_case_34_incomplete_split_session_cannot_supply_roll_volume() -> None:
    opening, _ = _bounds(D1)
    export = _export(
        source_name="partial-split-session.txt",
        raw_bytes=_raw_starts(
            (opening, opening + timedelta(minutes=5)),
            (10, 10),
        ),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    result = _build(exports=(export,), calendars=(_split_calendar(D1),))
    assert result.status is GCDatasetBuildStatus.UNKNOWN
    assert "COMPARABLE_COMPLETED_VOLUME_MISSING" in result.blocking_reasons
    assert result.manifest is None


def test_case_34_farther_volume_cannot_skip_exact_adjacent_delivery() -> None:
    dates = (D1, D2, D3, D4)
    exports, _, calendars, config = _manual_scope(
        current_dates=dates,
        current_volumes=(10, 10, 10, 10),
        adjacent_volumes=(20, 20, 20, 20),
    )
    farther = _export(
        "GCM26-COMEX",
        tuple((day, 1000) for day in dates),
        source_name="farther.txt",
    )
    all_exports = _sorted_exports(exports + (farther,))
    coverage = _sorted_coverage(
        tuple(
            item
            for export in all_exports
            for item in _coverage_per_session(export, calendars)
        )
    )
    result = build_gc_futures_dataset(
        exports=all_exports,
        coverage_evidence=coverage,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.VALID
    assert result.manifest is not None
    assert result.manifest.roll_trade_dates == (D4,)
    assert any(
        segment.contract == "GCJ26-COMEX"
        and segment.first_trade_date == D4
        for segment in result.segments
    )
    assert not any(
        segment.contract == "GCM26-COMEX"
        and segment.first_trade_date == D4
        for segment in result.segments
    )


# Case 35
def test_case_35_effective_session_volume_cannot_change_scheduled_roll() -> None:
    exports, calendars = _roll_inputs((20, 20, 20, 0), current_volumes=(10, 10, 10, 100))
    result = _build(exports=exports, calendars=calendars)
    assert result.manifest is not None and result.manifest.roll_trade_dates == (D4,)
    assert any(s.contract == "GCJ26-COMEX" and s.first_trade_date == D4 for s in result.segments)


# Case 36
def test_case_36_skipped_contract_remains_in_manifest_lineage() -> None:
    dates = (D1, D2, D3, D4)
    g = _export("GCG26-COMEX", tuple((d, 10) for d in dates), source_name="g.txt")
    j = _export("GCJ26-COMEX", tuple((d, 15) for d in dates), source_name="j.txt")
    m = _export("GCM26-COMEX", tuple((d, 30) for d in dates), source_name="m.txt")
    result = _build(exports=(g, j, m), calendars=tuple(_calendar(d) for d in dates))
    assert result.manifest is not None
    assert {g.source_id, j.source_id, m.source_id}.issubset(
        set(result.manifest.source_ids)
    )


# Case 37
def test_case_37_prices_are_not_adjusted_across_contracts() -> None:
    dates = (D1, D2, D3, D4)
    g = _export("GCG26-COMEX", tuple((d, 10) for d in dates), source_name="g.txt")
    j = _export(
        "GCJ26-COMEX",
        tuple((d, 20) for d in dates),
        source_name="j.txt",
        raw_bytes=_raw(tuple((d, 20) for d in dates), price=Decimal("5000.0")),
    )
    result = _build(exports=(g, j), calendars=tuple(_calendar(d) for d in dates))
    j_segment = next(s for s in result.segments if s.contract == "GCJ26-COMEX")
    assert j_segment.bars[0].open_tick == 50000


# Case 38
def test_case_38_roll_partition_and_gap_create_distinct_segments() -> None:
    exports, calendars = _roll_inputs((20, 20, 20, 1))
    result = _build(exports=exports, calendars=calendars)
    assert len(result.segments) >= 2
    assert len({segment.segment_id for segment in result.segments}) == len(result.segments)


# Case 39
def test_case_39_canonical_bar_contract() -> None:
    bar = _build().segments[0].bars[0]
    assert isinstance(bar, GCChronologicalBar)
    assert bar.index == 0 and bar.is_closed is True
    assert (bar.open_tick, bar.high_tick, bar.low_tick, bar.close_tick) == (40000, 40002, 39998, 40000)


# Case 40
def test_case_40_oos_partition_is_disjoint() -> None:
    oos_start = D2
    export = _export(
        sessions=((D1, 10), (D2, 10)),
        role=GCSourceRole.OOS_HOLDOUT,
    )
    result = _build(
        exports=(export,),
        calendars=(_calendar(D1), _calendar(D2)),
        config=_config(oos_start_trade_date=oos_start, oos_end_trade_date=D3),
    )
    assert result.status is GCDatasetBuildStatus.INVALID


def test_case_40_v2_manifest_binds_coverage_and_conserves_sparse_evidence() -> None:
    lines = _raw(((D1, 10),)).decode().splitlines()
    export = _export(raw_bytes=("\n".join(lines[:2]) + "\n").encode())
    result = _build(exports=(export,))
    manifest = result.manifest
    assert manifest is not None
    assert manifest.version == "GC-DATASET-BUILDER-V3-SPLIT-SESSION"
    assert manifest.coverage_ids
    assert len(manifest.coverage_digest) == 64
    assert manifest.attested_no_trade_interval_count == 0
    assert manifest.parsed_row_count == (
        manifest.eligible_row_count + manifest.excluded_row_count
    )
    assert manifest.raw_volume == manifest.eligible_volume + manifest.excluded_volume
    assert all(
        reason not in {"COVERAGE_UNVERIFIED", "COVERAGE_MISMATCH"}
        for reason, _ in manifest.exclusion_counts
    )


# Case 41
def test_case_41_incomplete_final_capture_is_rejected_by_parser() -> None:
    opening, _ = _bounds(D1)
    with pytest.raises((TypeError, ValueError)):
        _export(capture_timestamp=opening + timedelta(minutes=5))


def test_case_41_source_identity_is_v2_separated() -> None:
    export = _export()
    v2 = make_gc_dataset_id(
        identity_kind="SOURCE",
        source_name=export.source_name,
        source_sha256=export.source_sha256,
        contract=export.contract,
        role=export.role,
        capture_timestamp=export.capture_timestamp,
        source_timezone=export.chart_timezone,
        timeframe=export.timeframe,
    )
    v1_payload = {
        "version": "GC-DATASET-BUILDER-V1",
        "identity_kind": "SOURCE",
        "source_name": export.source_name,
        "source_sha256": export.source_sha256,
        "contract": export.contract,
        "role": export.role.value,
        "capture_timestamp": export.capture_timestamp.astimezone(UTC).isoformat(
            timespec="microseconds"
        ),
        "source_timezone": export.chart_timezone,
        "timeframe": export.timeframe,
    }
    v1 = hashlib.sha256(
        json.dumps(
            v1_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    ).hexdigest()
    assert v2 == export.source_id
    assert v2 != v1


@pytest.mark.parametrize("vector", _ACCEPTED_V2_PILOT_IDENTITY_VECTORS)
def test_case_41_v3_preserves_accepted_v2_source_identity_vectors(
    vector: dict[str, object],
) -> None:
    assert make_gc_dataset_id(
        identity_kind="SOURCE",
        source_name=vector["source_name"],
        source_sha256=vector["source_sha256"],
        contract=vector["contract"],
        role=GCSourceRole.DEVELOPMENT,
        capture_timestamp=vector["capture_timestamp"],
        source_timezone="Asia/Tokyo",
        timeframe="5M",
    ) == vector["source_id"]


# Case 42
def test_case_42_manifest_conservation_and_evidence_digest() -> None:
    result = _build()
    manifest = result.manifest
    assert manifest is not None
    assert manifest.parsed_row_count == manifest.eligible_row_count + manifest.excluded_row_count
    assert manifest.eligible_row_count == manifest.development_bar_count + manifest.oos_bar_count
    assert manifest.raw_volume == manifest.eligible_volume + manifest.excluded_volume
    assert sum(count for _, count in manifest.exclusion_counts) == manifest.excluded_row_count
    assert _dataset_id(evidence_digest="e" * 64) != _dataset_id()


def test_case_42_split_calendar_digest_binds_intervals_and_provenance() -> None:
    first, first_issues = dataset._scan_calendars(
        (_split_calendar(D1),), _config()
    )
    changed, changed_issues = dataset._scan_calendars(
        (
            _split_calendar(
                D1,
                source_artifact_ids=("CME-GCC-04687271-OTHER",),
            ),
        ),
        _config(),
    )
    opening, _ = _bounds(D1)
    boundary_changed, boundary_issues = dataset._scan_calendars(
        (
            _split_calendar(
                D1,
                intervals=(
                    GCDatasetSessionInterval(
                        opening, opening + timedelta(minutes=10)
                    ),
                    GCDatasetSessionInterval(
                        opening + timedelta(minutes=20),
                        opening + timedelta(minutes=35),
                    ),
                ),
            ),
        ),
        _config(),
    )
    lowercase_hash, lowercase_issues = dataset._scan_calendars(
        (
            _split_calendar(
                D1,
                source_artifact_sha256s=(
                    AUTHENTICATED_CME_EMAIL_SHA256.lower(),
                ),
            ),
        ),
        _config(),
    )
    assert (
        first_issues
        == changed_issues
        == boundary_issues
        == lowercase_issues
        == ()
    )
    assert dataset._digest_calendar(first) != dataset._digest_calendar(changed)
    assert (
        dataset._digest_calendar(first)
        != dataset._digest_calendar(boundary_changed)
    )
    assert dataset._digest_calendar(first) == dataset._digest_calendar(
        lowercase_hash
    )


@pytest.mark.parametrize(
    "required_field",
    [
        "source_id", "source_name", "source_sha256", "contract", "role",
        "capture_timestamp", "source_timezone", "timeframe",
        "coverage_start_timestamp", "coverage_end_timestamp",
        "acquisition_completed_timestamp", "acquisition_evidence_sha256",
    ],
)
def test_case_42_coverage_identity_requires_every_field(
    required_field: str,
) -> None:
    replacement: object = None
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(**{required_field: replacement})


@pytest.mark.parametrize(
    ("forbidden_field", "forbidden_value"),
    [
        ("config", _config()),
        ("first_trade_date", D1),
        ("last_trade_date", D1),
        ("source_ids", (HASH_A,)),
        ("coverage_ids", (HASH_A,)),
        ("bar_digest", HASH_A),
        ("preceding_missing_bar_count", 0),
        ("partition", GCSegmentPartition.DEVELOPMENT),
        ("segment_ids", (HASH_A,)),
        ("calendar_digest", HASH_A),
        ("coverage_digest", HASH_A),
        ("evidence_digest", HASH_A),
        ("roll_trade_dates", (D1,)),
    ],
)
def test_case_42_coverage_identity_forbids_other_kind_fields(
    forbidden_field: str,
    forbidden_value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(**{forbidden_field: forbidden_value})


def test_case_42_coverage_identity_recomputes_source_and_binds_payload() -> None:
    baseline = _coverage_id()
    opening, closing = _bounds(D1)
    assert _coverage_id(
        coverage_start_timestamp=opening.astimezone(TOKYO),
        coverage_end_timestamp=closing.astimezone(TOKYO),
        acquisition_completed_timestamp=closing.astimezone(TOKYO),
    ) == baseline
    assert _coverage_id(
        acquisition_evidence_sha256=HASH_C
    ) != baseline
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(source_id=HASH_C)
    with pytest.raises((TypeError, ValueError)):
        _coverage_id(coverage_start_timestamp=closing)


@pytest.mark.parametrize("vector", _ACCEPTED_V2_PILOT_IDENTITY_VECTORS)
def test_case_42_v3_preserves_accepted_v2_coverage_identity_vectors(
    vector: dict[str, object],
) -> None:
    assert make_gc_dataset_id(
        identity_kind="COVERAGE",
        source_id=vector["source_id"],
        source_name=vector["source_name"],
        source_sha256=vector["source_sha256"],
        contract=vector["contract"],
        role=GCSourceRole.DEVELOPMENT,
        capture_timestamp=vector["capture_timestamp"],
        source_timezone="Asia/Tokyo",
        timeframe="5M",
        coverage_start_timestamp=vector["coverage_start_timestamp"],
        coverage_end_timestamp=vector["coverage_end_timestamp"],
        acquisition_completed_timestamp=vector[
            "acquisition_completed_timestamp"
        ],
        acquisition_evidence_sha256=vector[
            "acquisition_evidence_sha256"
        ],
    ) == vector["coverage_id"]


# Case 43
def test_case_43_source_identity_schema_and_sensitivity() -> None:
    export = _export()
    identity = make_gc_dataset_id(
        identity_kind="SOURCE",
        source_name=export.source_name,
        source_sha256=export.source_sha256,
        contract=export.contract,
        role=export.role,
        capture_timestamp=export.capture_timestamp,
        source_timezone=export.chart_timezone,
        timeframe=export.timeframe,
    )
    assert identity == export.source_id
    with pytest.raises((TypeError, ValueError)):
        make_gc_dataset_id(
            identity_kind="SOURCE",
            config=_config(),
            source_name=export.source_name,
            source_sha256=export.source_sha256,
            contract=export.contract,
            role=export.role,
            capture_timestamp=export.capture_timestamp,
            source_timezone=export.chart_timezone,
            timeframe=export.timeframe,
        )


@pytest.mark.parametrize(
    "required_field",
    [
        "source_name",
        "source_sha256",
        "contract",
        "role",
        "capture_timestamp",
        "source_timezone",
        "timeframe",
    ],
)
def test_case_43_source_identity_requires_every_field(required_field: str) -> None:
    export = _export()
    values: dict[str, object] = {
        "identity_kind": "SOURCE",
        "source_name": export.source_name,
        "source_sha256": export.source_sha256,
        "contract": export.contract,
        "role": export.role,
        "capture_timestamp": export.capture_timestamp,
        "source_timezone": export.chart_timezone,
        "timeframe": export.timeframe,
    }
    values[required_field] = None
    with pytest.raises((TypeError, ValueError)):
        make_gc_dataset_id(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("forbidden_field", "forbidden_value"),
    [
        ("source_id", HASH_A),
        ("config", _config()),
        ("coverage_start_timestamp", datetime(2026, 1, 1, tzinfo=UTC)),
        ("coverage_end_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_completed_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_evidence_sha256", HASH_A),
        ("first_trade_date", D1),
        ("last_trade_date", D1),
        ("source_ids", (HASH_A,)),
        ("coverage_ids", (HASH_A,)),
        ("bar_digest", HASH_A),
        ("preceding_missing_bar_count", 0),
        ("partition", GCSegmentPartition.DEVELOPMENT),
        ("segment_ids", (HASH_A,)),
        ("calendar_digest", HASH_A),
        ("coverage_digest", HASH_A),
        ("evidence_digest", HASH_A),
        ("roll_trade_dates", (D1,)),
    ],
)
def test_case_43_source_identity_forbids_non_source_fields(
    forbidden_field: str,
    forbidden_value: object,
) -> None:
    export = _export()
    values: dict[str, object] = {
        "identity_kind": "SOURCE",
        "source_name": export.source_name,
        "source_sha256": export.source_sha256,
        "contract": export.contract,
        "role": export.role,
        "capture_timestamp": export.capture_timestamp,
        "source_timezone": export.chart_timezone,
        "timeframe": export.timeframe,
        forbidden_field: forbidden_value,
    }
    with pytest.raises((TypeError, ValueError)):
        make_gc_dataset_id(**values)  # type: ignore[arg-type]


# Case 44
def test_case_44_segment_identity_binds_gap_and_forbidden_fields() -> None:
    assert _segment_id() == (
        "a16b6df9b3650b83cb8621878bb696694cf7f27221e52bc1ff09ea0bf68157b2"
    )
    assert _segment_id(preceding_missing_bar_count=1) != _segment_id()
    with pytest.raises((TypeError, ValueError)):
        _segment_id(calendar_digest=HASH_C)
    with pytest.raises((TypeError, ValueError)):
        _segment_id(preceding_missing_bar_count=-1)


@pytest.mark.parametrize(
    "required_field",
    [
        "config",
        "contract",
        "partition",
        "first_trade_date",
        "last_trade_date",
        "source_ids",
        "bar_digest",
        "preceding_missing_bar_count",
    ],
)
def test_case_44_segment_identity_requires_every_field(required_field: str) -> None:
    replacement: object = () if required_field == "source_ids" else None
    with pytest.raises((TypeError, ValueError)):
        _segment_id(**{required_field: replacement})


@pytest.mark.parametrize(
    ("forbidden_field", "forbidden_value"),
    [
        ("source_id", HASH_A),
        ("source_name", "source.txt"),
        ("source_sha256", HASH_C),
        ("role", GCSourceRole.DEVELOPMENT),
        ("capture_timestamp", datetime(2026, 1, 1, tzinfo=UTC)),
        ("source_timezone", "Asia/Tokyo"),
        ("timeframe", "5M"),
        ("coverage_start_timestamp", datetime(2026, 1, 1, tzinfo=UTC)),
        ("coverage_end_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_completed_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_evidence_sha256", HASH_A),
        ("coverage_ids", (HASH_A,)),
        ("segment_ids", (HASH_C,)),
        ("calendar_digest", HASH_C),
        ("coverage_digest", HASH_C),
        ("evidence_digest", HASH_C),
        ("roll_trade_dates", (D2,)),
    ],
)
def test_case_44_segment_identity_forbids_other_kind_fields(
    forbidden_field: str,
    forbidden_value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _segment_id(**{forbidden_field: forbidden_value})


@pytest.mark.parametrize(
    "changes",
    [
        {"config": _config(oos_end_trade_date=date(2026, 3, 31))},
        {"contract": "GCJ26-COMEX"},
        {"partition": GCSegmentPartition.OOS_HOLDOUT},
        {"first_trade_date": D2, "last_trade_date": D2},
        {"last_trade_date": D2},
        {"source_ids": (HASH_C,)},
        {"bar_digest": HASH_C},
        {"preceding_missing_bar_count": 1},
    ],
)
def test_case_44_segment_identity_is_sensitive_to_every_payload_axis(
    changes: dict[str, object],
) -> None:
    assert _segment_id(**changes) != _segment_id()


# Case 45
def test_case_45_dataset_identity_schema_and_sensitivity() -> None:
    assert _dataset_id() == (
        "8846dcb65451269afc1b4b46d13bd0f7e65ee05dbe63ce7c0cd3dff2496f384b"
    )
    assert _dataset_id(calendar_digest="e" * 64) != _dataset_id()
    assert _dataset_id(roll_trade_dates=(D2,)) != _dataset_id()
    with pytest.raises((TypeError, ValueError)):
        _dataset_id(contract="GCG26-COMEX")


@pytest.mark.parametrize(
    ("required_field", "replacement"),
    [
        ("config", None),
        ("source_ids", ()),
        ("coverage_ids", ()),
        ("calendar_digest", None),
        ("coverage_digest", None),
        ("evidence_digest", None),
    ],
)
def test_case_45_dataset_identity_requires_every_field(
    required_field: str,
    replacement: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _dataset_id(**{required_field: replacement})


@pytest.mark.parametrize(
    ("forbidden_field", "forbidden_value"),
    [
        ("source_id", HASH_A),
        ("source_name", "source.txt"),
        ("source_sha256", HASH_C),
        ("contract", "GCG26-COMEX"),
        ("role", GCSourceRole.DEVELOPMENT),
        ("capture_timestamp", datetime(2026, 1, 1, tzinfo=UTC)),
        ("source_timezone", "Asia/Tokyo"),
        ("timeframe", "5M"),
        ("coverage_start_timestamp", datetime(2026, 1, 1, tzinfo=UTC)),
        ("coverage_end_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_completed_timestamp", datetime(2026, 1, 2, tzinfo=UTC)),
        ("acquisition_evidence_sha256", HASH_A),
        ("first_trade_date", D1),
        ("last_trade_date", D1),
        ("bar_digest", HASH_C),
        ("preceding_missing_bar_count", 0),
        ("partition", GCSegmentPartition.DEVELOPMENT),
    ],
)
def test_case_45_dataset_identity_forbids_other_kind_fields(
    forbidden_field: str,
    forbidden_value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _dataset_id(**{forbidden_field: forbidden_value})


@pytest.mark.parametrize(
    "changes",
    [
        {"config": _config(oos_end_trade_date=date(2026, 3, 31))},
        {"source_ids": (HASH_C,)},
        {"coverage_ids": (HASH_C,)},
        {"segment_ids": (HASH_C,)},
        {"calendar_digest": "e" * 64},
        {"coverage_digest": "f" * 64},
        {"evidence_digest": "f" * 64},
        {"roll_trade_dates": (D2,)},
    ],
)
def test_case_45_dataset_identity_is_sensitive_to_every_payload_axis(
    changes: dict[str, object],
) -> None:
    assert _dataset_id(**changes) != _dataset_id()


# Case 46
def test_case_46_exact_public_surface_signatures_and_frozen_models() -> None:
    assert dataset.__all__ == [
        "GC_DATASET_BUILDER_VERSION", "GC_DATASET_INSTRUMENT", "GC_DATASET_TIMEFRAME",
        "GC_DATASET_SOURCE_TIMEZONE", "GC_DATASET_EXCHANGE_TIMEZONE", "GC_DATASET_TICK_SIZE",
        "GC_ROLL_CONFIRMATION_SESSIONS", "GC_DELIVERY_MONTH_CODES", "GCDatasetBuildStatus",
        "GCSourceRole", "GCSegmentPartition", "GCDatasetSessionInterval",
        "GCSplitSessionCalendarEntry", "GCSierraChartBarRow", "GCSierraChartExport",
        "GCSierraChartCoverageEvidence", "GCCanonicalContractSegment", "GCDatasetManifest", "GCDatasetBuildConfig",
        "GCDatasetBuildResult", "parse_sierra_chart_gc_export", "make_gc_dataset_id",
        "build_gc_futures_dataset",
    ]
    for function in (parse_sierra_chart_gc_export, make_gc_dataset_id, build_gc_futures_dataset):
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(function).parameters.values()
        )
    expected_fields = {
        GCDatasetSessionInterval: 2,
        GCSplitSessionCalendarEntry: 5,
        GCSierraChartBarRow: 10,
        GCSierraChartExport: 9,
        GCSierraChartCoverageEvidence: 13,
        GCCanonicalContractSegment: 8,
        GCDatasetManifest: 25,
        GCDatasetBuildConfig: 11,
        GCDatasetBuildResult: 6,
    }
    for model, count in expected_fields.items():
        assert len(fields(model)) == count
        assert model.__dataclass_params__.frozen is True
        assert get_type_hints(model)
    expected_names = {
        GCDatasetSessionInterval: (
            "start_timestamp", "end_timestamp",
        ),
        GCSplitSessionCalendarEntry: (
            "calendar_version", "trade_date", "intervals",
            "source_artifact_ids", "source_artifact_sha256s",
        ),
        GCSierraChartBarRow: (
            "source_row_number", "bar_start_timestamp", "open_price",
            "high_price", "low_price", "close_price", "volume",
            "number_of_trades", "bid_volume", "ask_volume",
        ),
        GCSierraChartExport: (
            "source_id", "source_name", "source_sha256", "contract", "role",
            "capture_timestamp", "chart_timezone", "timeframe", "rows",
        ),
        GCSierraChartCoverageEvidence: (
            "coverage_id", "source_id", "source_name", "source_sha256",
            "contract", "role", "capture_timestamp", "chart_timezone",
            "timeframe", "coverage_start_timestamp", "coverage_end_timestamp",
            "acquisition_completed_timestamp", "acquisition_evidence_sha256",
        ),
        GCCanonicalContractSegment: (
            "segment_id", "contract", "partition", "first_trade_date",
            "last_trade_date", "source_ids", "bars",
            "preceding_missing_bar_count",
        ),
        GCDatasetManifest: (
            "dataset_id", "version", "source_ids", "coverage_ids",
            "coverage_digest", "segment_ids",
            "calendar_version", "timezone_data_version",
            "raw_start_timestamp", "raw_end_timestamp",
            "usable_start_timestamp", "usable_end_timestamp",
            "parsed_row_count", "eligible_row_count", "development_bar_count",
            "oos_bar_count", "excluded_row_count", "missing_bar_count",
            "attested_no_trade_interval_count",
            "raw_volume", "eligible_volume", "excluded_volume",
            "completed_session_volumes", "exclusion_counts", "roll_trade_dates",
        ),
        GCDatasetBuildConfig: (
            "instrument", "timeframe", "source_timezone", "exchange_timezone",
            "timezone_data_version", "tick_size", "initial_contract",
            "initial_trade_date", "roll_confirmation_sessions",
            "oos_start_trade_date", "oos_end_trade_date",
        ),
        GCDatasetBuildResult: (
            "status", "dataset_id", "segments", "manifest", "reasons",
            "blocking_reasons",
        ),
    }
    for model, names in expected_names.items():
        assert tuple(item.name for item in fields(model)) == names
        assert tuple(get_type_hints(model)) == names
    result_fields = {item.name: item for item in fields(GCDatasetBuildResult)}
    assert result_fields["segments"].default == ()
    assert result_fields["manifest"].default is None
    assert result_fields["reasons"].default == ()
    assert result_fields["blocking_reasons"].default == ()
    with pytest.raises(FrozenInstanceError):
        _config().instrument = "OTHER"  # type: ignore[misc]
    assert [item.value for item in GCDatasetBuildStatus] == ["VALID", "NONE", "UNKNOWN", "AMBIGUOUS", "INVALID"]
    assert [item.value for item in GCSourceRole] == ["DEVELOPMENT", "OOS_HOLDOUT"]
    assert [item.value for item in GCSegmentPartition] == ["DEVELOPMENT", "OOS_HOLDOUT"]
    assert GC_DELIVERY_MONTH_CODES == ("G", "J", "M", "Q", "V", "Z")
    assert GC_DATASET_BUILDER_VERSION == "GC-DATASET-BUILDER-V3-SPLIT-SESSION"
    assert issubclass(GCDatasetBuildStatus, (str, Enum))


def test_case_46_exact_keyword_only_names_and_defaults() -> None:
    parse_signature = inspect.signature(parse_sierra_chart_gc_export)
    assert tuple(parse_signature.parameters) == (
        "source_name", "contract", "role", "capture_timestamp",
        "chart_timezone", "timeframe", "raw_bytes",
    )
    assert all(
        item.default is inspect.Parameter.empty
        for item in parse_signature.parameters.values()
    )
    builder_signature = inspect.signature(make_gc_dataset_id)
    assert tuple(builder_signature.parameters) == (
        "identity_kind", "config", "source_id", "source_name", "source_sha256", "contract",
        "role", "capture_timestamp", "source_timezone", "timeframe",
        "coverage_start_timestamp", "coverage_end_timestamp",
        "acquisition_completed_timestamp", "acquisition_evidence_sha256",
        "first_trade_date", "last_trade_date", "source_ids", "coverage_ids", "bar_digest",
        "preceding_missing_bar_count", "partition", "segment_ids",
        "calendar_digest", "coverage_digest", "evidence_digest", "roll_trade_dates",
    )
    for name, parameter in builder_signature.parameters.items():
        if name == "identity_kind":
            assert parameter.default is inspect.Parameter.empty
        elif name in {"source_ids", "coverage_ids", "segment_ids", "roll_trade_dates"}:
            assert parameter.default == ()
        else:
            assert parameter.default is None
    analyzer_signature = inspect.signature(build_gc_futures_dataset)
    assert tuple(analyzer_signature.parameters) == (
        "exports", "coverage_evidence", "calendar_entries", "config",
    )
    assert all(
        item.default is inspect.Parameter.empty
        for item in analyzer_signature.parameters.values()
    )
    analyzer_hints = get_type_hints(build_gc_futures_dataset)
    assert analyzer_hints["calendar_entries"] == (
        tuple[
            KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
        ]
        | None
    )


def test_case_46_later_malformed_coverage_preserves_only_prior_segments() -> None:
    exports, coverage, calendars, config = _manual_scope(
        current_dates=(D1, D2),
        current_volumes=(10, 10),
        adjacent_volumes=(5, 5),
    )
    current = next(
        item for item in exports if item.contract == config.initial_contract
    )
    later = next(
        item
        for item in coverage
        if item.source_id == current.source_id
        and item.coverage_start_timestamp == _bounds(D2)[0]
    )
    malformed = replace(later, acquisition_evidence_sha256="bad")
    changed = tuple(
        malformed if item.coverage_id == later.coverage_id else item
        for item in coverage
    )
    result = build_gc_futures_dataset(
        exports=exports,
        coverage_evidence=changed,
        calendar_entries=calendars,
        config=config,
    )
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.manifest is None
    assert result.segments
    assert all(segment.last_trade_date < D2 for segment in result.segments)


# Case 47
@pytest.mark.parametrize(
    ("malformed_field", "malformed_value"),
    [
        ("rows", "malformed_row"),
        ("source_name", 7),
        ("contract", "GC-BAD"),
        ("capture_timestamp", datetime(2026, 1, 7, 0, 0)),
    ],
)
def test_case_47_later_malformed_group_preserves_prior_evidence(
    malformed_field: str,
    malformed_value: object,
) -> None:
    valid = _export(sessions=((D1, 10),))
    later = _export(sessions=((D2, 10),), source_name="later.txt")
    if malformed_value == "malformed_row":
        bad_row = replace(later.rows[0], volume=True)  # type: ignore[arg-type]
        malformed = replace(later, rows=(bad_row,) + later.rows[1:])
    else:
        malformed = replace(later, **{malformed_field: malformed_value})
    ordered = tuple(sorted((valid, malformed), key=lambda item: item.source_sha256))
    result = _build(
        exports=ordered,
        calendars=(_calendar(D1), _calendar(D2)),
    )
    assert result.status is GCDatasetBuildStatus.INVALID
    assert result.segments
    assert all(segment.last_trade_date < D2 for segment in result.segments)
    assert result.manifest is None


def test_case_47_complete_strictly_later_prefix_is_invariant() -> None:
    first_export = _export(sessions=((D1, 10),), source_name="first.txt")
    later_export = _export(sessions=((D2, 10),), source_name="later.txt")
    prefix = _build(exports=(first_export,), calendars=(_calendar(D1),))
    ordered = tuple(
        sorted(
            (first_export, later_export),
            key=lambda item: (
                item.contract,
                item.role.value,
                item.source_sha256,
            ),
        )
    )
    extended = _build(
        exports=ordered,
        calendars=(_calendar(D1), _calendar(D2)),
    )
    assert prefix.status is GCDatasetBuildStatus.VALID
    assert extended.status is GCDatasetBuildStatus.VALID
    assert extended.segments[0] == prefix.segments[0]


def test_case_47_complete_split_session_prefix_is_invariant() -> None:
    opening, _ = _bounds(D1)
    split_export = _export(
        source_name="split-prefix.txt",
        raw_bytes=_raw_starts(
            tuple(
                opening + timedelta(minutes=offset)
                for offset in (0, 5, 20, 25)
            ),
            (10, 10, 10, 10),
        ),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    prefix = _build(
        exports=(split_export,),
        calendars=(_split_calendar(D1),),
    )
    later = _export(sessions=((D2, 10),), source_name="later-prefix.txt")
    extended = _build(
        exports=_sorted_exports((split_export, later)),
        calendars=(_split_calendar(D1), _calendar(D2)),
    )
    assert prefix.status is GCDatasetBuildStatus.VALID
    assert extended.status is GCDatasetBuildStatus.VALID
    assert extended.segments[:2] == prefix.segments[:2]


def test_case_47_split_session_historical_provenance_mutation_is_not_prefix() -> None:
    opening, _ = _bounds(D1)
    export = _export(
        source_name="split-mutation.txt",
        raw_bytes=_raw_starts(
            tuple(
                opening + timedelta(minutes=offset)
                for offset in (0, 5, 20, 25)
            ),
            (10, 10, 10, 10),
        ),
        capture_timestamp=opening + timedelta(minutes=31),
    )
    first = _build(exports=(export,), calendars=(_split_calendar(D1),))
    changed = _build(
        exports=(export,),
        calendars=(
            _split_calendar(
                D1,
                source_artifact_ids=("CME-GCC-04687271-REVISED",),
            ),
        ),
    )
    assert first.status is changed.status is GCDatasetBuildStatus.VALID
    assert first.dataset_id != changed.dataset_id


def test_case_47_historical_repair_is_not_prefix_extension() -> None:
    partial = _export(
        source_name="partial.txt",
        raw_bytes=_raw(((D1, 10),), second_offset_minutes=10),
        capture_timestamp=_bounds(D1)[1] + timedelta(minutes=6),
    )
    repaired = _export(source_name="repaired.txt")
    partial_result = _build(
        exports=(partial,),
        calendars=(_calendar(D1, close_minutes=15),),
    )
    repaired_result = _build(exports=(repaired,), calendars=(_calendar(D1),))
    assert partial_result.status is GCDatasetBuildStatus.VALID
    assert repaired_result.status is GCDatasetBuildStatus.VALID
    assert partial_result.dataset_id != repaired_result.dataset_id
    assert partial_result.segments != repaired_result.segments


# Case 48
def test_case_48_scope_imports_repeatability_and_no_io_surface() -> None:
    first = _build()
    second = _build()
    assert first == second
    source = Path(dataset.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(name.startswith(("pandas", "numpy", "requests", "sklearn")) for name in imports)
    assert "orderflow.footprint" not in imports
    assert "orderflow.sierra_chart_importer" not in imports
    assert not any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open"
        for node in ast.walk(tree)
    )
