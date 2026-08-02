"""Isolated deterministic GC strict-chronology research backtest.

This module consumes only immutable caller-supplied bars, calendar entries, and
research candidates.  It performs no strategy discovery, model scoring, file or
network I/O, risk sizing, broker action, or integration registration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
from enum import Enum
import hashlib
from importlib import metadata
import json
import re
from zoneinfo import ZoneInfo

from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus


GC_CHRONOLOGICAL_BACKTEST_VERSION = "GC-CHRONOLOGICAL-BACKTEST-V1"
GC_CHRONOLOGICAL_TIMEFRAME = "5M"
GC_CHRONOLOGICAL_TIMEZONE = "America/New_York"

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_CONTRACT_PATTERN = re.compile(r"^GC[A-Z0-9]{2,}$")
_IDENTITY_KINDS = frozenset({"RUN", "DECISION", "TRADE", "SNAPSHOT"})
_FIVE_MINUTES = timedelta(minutes=5)


class GCBacktestDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class GCBacktestRunStatus(str, Enum):
    COMPLETE = "COMPLETE"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"


class GCCandidateDecisionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_POSITION_OPEN = "REJECTED_POSITION_OPEN"
    REJECTED_AMBIGUOUS_GROUP = "REJECTED_AMBIGUOUS_GROUP"
    REJECTED_SESSION = "REJECTED_SESSION"
    REJECTED_ENTRY_GEOMETRY = "REJECTED_ENTRY_GEOMETRY"
    PENDING_ENTRY = "PENDING_ENTRY"


class GCTradeExitReason(str, Enum):
    STOP_LOSS = "STOP_LOSS"
    TARGET = "TARGET"
    EXPIRY_CLOSE = "EXPIRY_CLOSE"
    SESSION_CLOSE = "SESSION_CLOSE"


@dataclass(frozen=True)
class GCChronologicalBar:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    volume: int
    is_closed: bool


@dataclass(frozen=True)
class GCBacktestCandidate:
    candidate_id: str
    direction: GCBacktestDirection
    decision_index: int
    decision_timestamp: datetime
    stop_tick: int
    target_tick: int
    max_holding_bars: int
    contracts: int


@dataclass(frozen=True)
class GCChronologicalBacktestConfig:
    instrument: str
    timeframe: str
    timezone_data_version: str
    tick_size: Decimal
    tick_value: Decimal
    starting_balance: Decimal
    entry_slippage_ticks: int
    exit_slippage_ticks: int
    commission_per_side_per_contract: Decimal
    exchange_fee_per_side_per_contract: Decimal
    maximum_contracts: int


@dataclass(frozen=True)
class GCCandidateDecision:
    decision_id: str
    candidate_id: str
    status: GCCandidateDecisionStatus
    index: int
    timestamp: datetime
    reason: str


@dataclass(frozen=True)
class GCBacktestTrade:
    trade_id: str
    candidate_id: str
    direction: GCBacktestDirection
    contracts: int
    entry_index: int
    entry_timestamp: datetime
    entry_tick: int
    stop_tick: int
    target_tick: int
    exit_index: int
    exit_timestamp: datetime
    exit_tick: int
    exit_reason: GCTradeExitReason
    gross_ticks: int
    gross_pnl: Decimal
    total_cost: Decimal
    net_pnl: Decimal


@dataclass(frozen=True)
class GCEquitySnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    balance: Decimal
    completed_trade_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCChronologicalBacktestResult:
    status: GCBacktestRunStatus
    run_id: str | None
    candidate_decisions: tuple[GCCandidateDecision, ...] = ()
    trades: tuple[GCBacktestTrade, ...] = ()
    equity_snapshots: tuple[GCEquitySnapshot, ...] = ()
    final_balance: Decimal | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _NormalizedConfig:
    instrument: str
    timeframe: str
    timezone_data_version: str
    tick_size: Decimal
    tick_value: Decimal
    starting_balance: Decimal
    entry_slippage_ticks: int
    exit_slippage_ticks: int
    commission_per_side_per_contract: Decimal
    exchange_fee_per_side_per_contract: Decimal
    maximum_contracts: int


@dataclass(frozen=True)
class _Issue:
    status: GCBacktestRunStatus
    timestamp: datetime | None
    reason: str
    unknowable: bool = False


@dataclass(frozen=True)
class _Scan:
    values: tuple[object, ...]
    issue: _Issue | None


@dataclass(frozen=True)
class _Pending:
    candidate: GCBacktestCandidate
    decision_timestamp: datetime
    calendar_trade_date: date


@dataclass(frozen=True)
class _Position:
    candidate: GCBacktestCandidate
    entry_index: int
    entry_timestamp: datetime
    entry_tick: int
    holding_bars: int
    calendar_trade_date: date


_DECISION_REASON = {
    GCCandidateDecisionStatus.PENDING_ENTRY: "NEXT_BAR_ENTRY_PENDING",
    GCCandidateDecisionStatus.ACCEPTED: "CANDIDATE_ACCEPTED_NEXT_BAR",
    GCCandidateDecisionStatus.REJECTED_POSITION_OPEN: "POSITION_ALREADY_OPEN",
    GCCandidateDecisionStatus.REJECTED_AMBIGUOUS_GROUP: (
        "AMBIGUOUS_SAME_MOMENT_CANDIDATES"
    ),
    GCCandidateDecisionStatus.REJECTED_SESSION: "SESSION_NOT_ELIGIBLE",
    GCCandidateDecisionStatus.REJECTED_ENTRY_GEOMETRY: (
        "ENTRY_GEOMETRY_INVALID_AFTER_SLIPPAGE"
    ),
}


def make_gc_chronological_backtest_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    config: GCChronologicalBacktestConfig,
    bar_digest: str | None = None,
    calendar_digest: str | None = None,
    candidate_digest: str | None = None,
    candidate_id: str | None = None,
    candidate_status: GCCandidateDecisionStatus | None = None,
    reason: str | None = None,
    direction: GCBacktestDirection | None = None,
    contracts: int | None = None,
    entry_index: int | None = None,
    entry_timestamp: datetime | None = None,
    entry_tick: int | None = None,
    stop_tick: int | None = None,
    target_tick: int | None = None,
    exit_index: int | None = None,
    exit_timestamp: datetime | None = None,
    exit_tick: int | None = None,
    exit_reason: GCTradeExitReason | None = None,
    gross_ticks: int | None = None,
    gross_pnl: Decimal | None = None,
    total_cost: Decimal | None = None,
    net_pnl: Decimal | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    balance: Decimal | None = None,
    completed_trade_ids: tuple[str, ...] = (),
) -> str:
    """Build one deterministic kind-specific strict-backtest identity."""

    try:
        return _make_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            config=config,
            bar_digest=bar_digest,
            calendar_digest=calendar_digest,
            candidate_digest=candidate_digest,
            candidate_id=candidate_id,
            candidate_status=candidate_status,
            reason=reason,
            direction=direction,
            contracts=contracts,
            entry_index=entry_index,
            entry_timestamp=entry_timestamp,
            entry_tick=entry_tick,
            stop_tick=stop_tick,
            target_tick=target_tick,
            exit_index=exit_index,
            exit_timestamp=exit_timestamp,
            exit_tick=exit_tick,
            exit_reason=exit_reason,
            gross_ticks=gross_ticks,
            gross_pnl=gross_pnl,
            total_cost=total_cost,
            net_pnl=net_pnl,
            effective_index=effective_index,
            effective_timestamp=effective_timestamp,
            balance=balance,
            completed_trade_ids=completed_trade_ids,
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        raise ValueError("invalid chronological-backtest identity evidence") from exc


def _make_id(
    *,
    identity_kind: object,
    instrument: object,
    timeframe: object,
    config: object,
    bar_digest: object,
    calendar_digest: object,
    candidate_digest: object,
    candidate_id: object,
    candidate_status: object,
    reason: object,
    direction: object,
    contracts: object,
    entry_index: object,
    entry_timestamp: object,
    entry_tick: object,
    stop_tick: object,
    target_tick: object,
    exit_index: object,
    exit_timestamp: object,
    exit_tick: object,
    exit_reason: object,
    gross_ticks: object,
    gross_pnl: object,
    total_cost: object,
    net_pnl: object,
    effective_index: object,
    effective_timestamp: object,
    balance: object,
    completed_trade_ids: object,
) -> str:
    if type(identity_kind) is not str or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked identity kind")
    normalized = _validate_config(config)
    normalized_instrument = _normalize_instrument(instrument)
    normalized_timeframe = _normalize_timeframe(timeframe)
    if normalized_instrument != normalized.instrument:
        raise ValueError("instrument does not match config")
    if normalized_timeframe != normalized.timeframe:
        raise ValueError("timeframe does not match config")

    payload: dict[str, object] = {
        "config": _config_payload(normalized),
        "identity_kind": identity_kind,
        "instrument": normalized_instrument,
        "timeframe": normalized_timeframe,
        "version": GC_CHRONOLOGICAL_BACKTEST_VERSION,
    }

    if identity_kind == "RUN":
        for name, value in (
            ("bar_digest", bar_digest),
            ("calendar_digest", calendar_digest),
            ("candidate_digest", candidate_digest),
        ):
            payload[name] = _validate_hash(value, name=name)
        _require_forbidden(
            candidate_id,
            candidate_status,
            reason,
            direction,
            contracts,
            entry_index,
            entry_timestamp,
            entry_tick,
            stop_tick,
            target_tick,
            exit_index,
            exit_timestamp,
            exit_tick,
            exit_reason,
            gross_ticks,
            gross_pnl,
            total_cost,
            net_pnl,
            effective_index,
            effective_timestamp,
            balance,
        )
        _require_empty_tuple(completed_trade_ids, name="completed_trade_ids")
    elif identity_kind == "DECISION":
        _forbid_source_digests(bar_digest, calendar_digest, candidate_digest)
        normalized_candidate = _validate_hash(candidate_id, name="candidate_id")
        if type(candidate_status) is not GCCandidateDecisionStatus:
            raise TypeError("candidate_status must be a GCCandidateDecisionStatus")
        if type(reason) is not str or reason != _DECISION_REASON[candidate_status]:
            raise ValueError("decision status/reason mismatch")
        index_value = _validate_nonnegative_int(effective_index, name="effective_index")
        timestamp_value = _normalize_timestamp(
            effective_timestamp, name="effective_timestamp"
        )
        _require_forbidden(
            direction,
            contracts,
            entry_index,
            entry_timestamp,
            entry_tick,
            stop_tick,
            target_tick,
            exit_index,
            exit_timestamp,
            exit_tick,
            exit_reason,
            gross_ticks,
            gross_pnl,
            total_cost,
            net_pnl,
            balance,
        )
        _require_empty_tuple(completed_trade_ids, name="completed_trade_ids")
        payload.update(
            candidate_id=normalized_candidate,
            candidate_status=candidate_status.value,
            effective_index=index_value,
            effective_timestamp=_timestamp_text(timestamp_value),
            reason=reason,
        )
    elif identity_kind == "TRADE":
        _forbid_source_digests(bar_digest, calendar_digest, candidate_digest)
        if candidate_status is not None or reason is not None:
            raise ValueError("TRADE forbids decision fields")
        if effective_index is not None or effective_timestamp is not None:
            raise ValueError("TRADE forbids snapshot effective fields")
        if balance is not None:
            raise ValueError("TRADE forbids balance")
        _require_empty_tuple(completed_trade_ids, name="completed_trade_ids")
        normalized_candidate = _validate_hash(candidate_id, name="candidate_id")
        if type(direction) is not GCBacktestDirection:
            raise TypeError("direction must be a GCBacktestDirection")
        contract_count = _validate_positive_int(contracts, name="contracts")
        if contract_count > normalized.maximum_contracts:
            raise ValueError("contracts exceed configured maximum")
        normalized_entry_index = _validate_nonnegative_int(
            entry_index, name="entry_index"
        )
        normalized_exit_index = _validate_nonnegative_int(exit_index, name="exit_index")
        if normalized_exit_index < normalized_entry_index:
            raise ValueError("exit_index cannot precede entry_index")
        normalized_entry_time = _normalize_timestamp(
            entry_timestamp, name="entry_timestamp"
        )
        normalized_exit_time = _normalize_timestamp(exit_timestamp, name="exit_timestamp")
        if normalized_exit_time < normalized_entry_time:
            raise ValueError("exit_timestamp cannot precede entry_timestamp")
        entry_value = _validate_int(entry_tick, name="entry_tick")
        stop_value = _validate_int(stop_tick, name="stop_tick")
        target_value = _validate_int(target_tick, name="target_tick")
        exit_value = _validate_int(exit_tick, name="exit_tick")
        _validate_position_geometry(direction, stop_value, entry_value, target_value)
        if type(exit_reason) is not GCTradeExitReason:
            raise TypeError("exit_reason must be a GCTradeExitReason")
        expected_ticks = (
            exit_value - entry_value
            if direction is GCBacktestDirection.BUY
            else entry_value - exit_value
        )
        if _validate_int(gross_ticks, name="gross_ticks") != expected_ticks:
            raise ValueError("gross_ticks mismatch")
        expected_gross = _multiply_decimal_int_exact(
            normalized.tick_value, expected_ticks * contract_count
        )
        expected_cost = _round_trip_cost(normalized, contract_count)
        expected_net = _subtract_decimal_exact(expected_gross, expected_cost)
        if _require_decimal(gross_pnl, name="gross_pnl") != expected_gross:
            raise ValueError("gross_pnl mismatch")
        if _require_decimal(total_cost, name="total_cost") != expected_cost:
            raise ValueError("total_cost mismatch")
        if _require_decimal(net_pnl, name="net_pnl") != expected_net:
            raise ValueError("net_pnl mismatch")
        if exit_reason is GCTradeExitReason.TARGET:
            expected_target_exit = (
                target_value - normalized.exit_slippage_ticks
                if direction is GCBacktestDirection.BUY
                else target_value + normalized.exit_slippage_ticks
            )
            if exit_value != expected_target_exit:
                raise ValueError("target exit geometry mismatch")
        if exit_reason is GCTradeExitReason.STOP_LOSS:
            if (
                direction is GCBacktestDirection.BUY
                and exit_value > stop_value - normalized.exit_slippage_ticks
            ):
                raise ValueError("BUY stop exit cannot improve beyond stop")
            if (
                direction is GCBacktestDirection.SELL
                and exit_value < stop_value + normalized.exit_slippage_ticks
            ):
                raise ValueError("SELL stop exit cannot improve beyond stop")
        payload.update(
            candidate_id=normalized_candidate,
            contracts=contract_count,
            direction=direction.value,
            entry_index=normalized_entry_index,
            entry_tick=entry_value,
            entry_timestamp=_timestamp_text(normalized_entry_time),
            exit_index=normalized_exit_index,
            exit_reason=exit_reason.value,
            exit_tick=exit_value,
            exit_timestamp=_timestamp_text(normalized_exit_time),
            gross_pnl=_decimal_text(expected_gross),
            gross_ticks=expected_ticks,
            net_pnl=_decimal_text(expected_net),
            stop_tick=stop_value,
            target_tick=target_value,
            total_cost=_decimal_text(expected_cost),
        )
    else:
        _forbid_source_digests(bar_digest, calendar_digest, candidate_digest)
        _require_forbidden(
            candidate_id,
            candidate_status,
            reason,
            direction,
            contracts,
            entry_index,
            entry_timestamp,
            entry_tick,
            stop_tick,
            target_tick,
            exit_index,
            exit_timestamp,
            exit_tick,
            exit_reason,
            gross_ticks,
            gross_pnl,
            total_cost,
            net_pnl,
        )
        normalized_index = _validate_nonnegative_int(
            effective_index, name="effective_index"
        )
        normalized_timestamp = _normalize_timestamp(
            effective_timestamp, name="effective_timestamp"
        )
        normalized_balance = _require_decimal(balance, name="balance")
        history = _validate_hash_tuple(
            completed_trade_ids,
            name="completed_trade_ids",
            allow_empty=False,
        )
        payload.update(
            balance=_decimal_text(normalized_balance),
            completed_trade_ids=list(history),
            effective_index=normalized_index,
            effective_timestamp=_timestamp_text(normalized_timestamp),
        )

    return _payload_hash(payload)


def run_gc_chronological_backtest(
    *,
    bars: tuple[GCChronologicalBar, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    candidates: tuple[GCBacktestCandidate, ...] | None,
    config: GCChronologicalBacktestConfig,
) -> GCChronologicalBacktestResult:
    """Run one isolated strict chronological single-position simulation."""

    try:
        return _run(
            bars=bars,
            calendar_entries=calendar_entries,
            candidates=candidates,
            config=config,
        )
    except Exception as exc:
        return GCChronologicalBacktestResult(
            status=GCBacktestRunStatus.INVALID,
            run_id=None,
            reasons=("MALFORMED_INPUT",),
            blocking_reasons=(type(exc).__name__,),
        )


def _run(
    *,
    bars: object,
    calendar_entries: object,
    candidates: object,
    config: object,
) -> GCChronologicalBacktestResult:
    try:
        normalized = _validate_config(config)
    except (TypeError, ValueError):
        return GCChronologicalBacktestResult(
            status=GCBacktestRunStatus.INVALID,
            run_id=None,
            reasons=("INVALID_CONFIG",),
            blocking_reasons=("INVALID_CONFIG",),
        )

    bar_scan = _scan_bars(bars) if bars is not None else None
    calendar_scan = (
        _scan_calendars(calendar_entries) if calendar_entries is not None else None
    )
    candidate_scan = (
        _scan_candidates(candidates, normalized) if candidates is not None else None
    )

    scans = tuple(
        scan for scan in (bar_scan, calendar_scan, candidate_scan) if scan is not None
    )
    scan_issues = tuple(scan.issue for scan in scans if scan.issue is not None)

    if bars is None or calendar_entries is None or candidates is None:
        if scan_issues:
            return GCChronologicalBacktestResult(
                status=GCBacktestRunStatus.INVALID,
                run_id=None,
                reasons=("MALFORMED_SUPPLIED_COUNTERPART",),
                blocking_reasons=tuple(issue.reason for issue in scan_issues),
            )
        return GCChronologicalBacktestResult(
            status=GCBacktestRunStatus.UNKNOWN,
            run_id=None,
            reasons=("MISSING_TOP_LEVEL_CONTEXT",),
            blocking_reasons=("MISSING_TOP_LEVEL_CONTEXT",),
        )

    assert bar_scan is not None and calendar_scan is not None and candidate_scan is not None
    valid_bars = tuple(bar_scan.values)
    valid_calendars = tuple(calendar_scan.values)
    valid_candidates = tuple(candidate_scan.values)

    if any(issue.unknowable for issue in scan_issues):
        return GCChronologicalBacktestResult(
            status=GCBacktestRunStatus.INVALID,
            run_id=None,
            reasons=("UNKNOWABLE_MALFORMED_EFFECTIVE_MOMENT",),
            blocking_reasons=tuple(issue.reason for issue in scan_issues),
        )

    run_id: str | None = None
    if not scan_issues:
        run_id = make_gc_chronological_backtest_id(
            identity_kind="RUN",
            instrument=normalized.instrument,
            timeframe=normalized.timeframe,
            config=config,
            bar_digest=_bar_digest(valid_bars),
            calendar_digest=_calendar_digest(valid_calendars),
            candidate_digest=_candidate_digest(valid_candidates),
        )

    relationship_issues, bar_calendar = _relationship_issues(
        valid_bars,
        valid_calendars,
        valid_candidates,
    )
    issues = scan_issues + relationship_issues
    forced_status: GCBacktestRunStatus | None = None
    if any(issue.status is GCBacktestRunStatus.INVALID for issue in issues):
        forced_status = GCBacktestRunStatus.INVALID
    elif issues:
        forced_status = GCBacktestRunStatus.UNKNOWN

    known_issue_times = tuple(
        issue.timestamp for issue in issues if issue.timestamp is not None
    )
    cutoff = min(known_issue_times) if known_issue_times else None
    if issues and not known_issue_times:
        return GCChronologicalBacktestResult(
            status=forced_status or GCBacktestRunStatus.INVALID,
            run_id=run_id,
            reasons=tuple(issue.reason for issue in issues),
            blocking_reasons=tuple(issue.reason for issue in issues),
        )

    return _simulate(
        bars=valid_bars,
        calendars=valid_calendars,
        candidates=valid_candidates,
        bar_calendar=bar_calendar,
        original_config=config,
        config=normalized,
        run_id=run_id,
        cutoff=cutoff,
        forced_status=forced_status,
        issue_reasons=tuple(issue.reason for issue in issues),
    )


def _simulate(
    *,
    bars: tuple[object, ...],
    calendars: tuple[object, ...],
    candidates: tuple[object, ...],
    bar_calendar: dict[tuple[int, datetime], KillZoneCalendarEntry],
    original_config: GCChronologicalBacktestConfig,
    config: _NormalizedConfig,
    run_id: str | None,
    cutoff: datetime | None,
    forced_status: GCBacktestRunStatus | None,
    issue_reasons: tuple[str, ...],
) -> GCChronologicalBacktestResult:
    usable_bars = tuple(
        value
        for value in bars
        if isinstance(value, GCChronologicalBar)
        and (cutoff is None or value.timestamp < cutoff)
        and (value.index, value.timestamp) in bar_calendar
    )
    usable_candidates = tuple(
        value
        for value in candidates
        if isinstance(value, GCBacktestCandidate)
        and (cutoff is None or value.decision_timestamp < cutoff)
    )
    groups: dict[tuple[int, datetime], list[GCBacktestCandidate]] = {}
    for candidate in usable_candidates:
        groups.setdefault(
            (candidate.decision_index, candidate.decision_timestamp), []
        ).append(candidate)

    decisions: list[GCCandidateDecision] = []
    trades: list[GCBacktestTrade] = []
    snapshots: list[GCEquitySnapshot] = []
    balance = config.starting_balance
    pending: _Pending | None = None
    position: _Position | None = None
    ambiguous = False

    for bar in usable_bars:
        calendar = bar_calendar[(bar.index, bar.timestamp)]
        pre_decision_count = len(decisions)
        pre_trade_count = len(trades)
        pre_snapshot_count = len(snapshots)
        pre_balance = balance
        pre_pending = pending
        pre_position = position

        if pending is not None:
            entry_time = _normalize_timestamp(
                bar.timestamp - _FIVE_MINUTES,
                name="entry_timestamp",
            )
            if (
                calendar.trade_date != pending.calendar_trade_date
                or entry_time != pending.decision_timestamp
                or calendar.session_close_timestamp is None
                or entry_time >= calendar.session_close_timestamp
            ):
                decisions.append(
                    _decision(
                        pending.candidate,
                        GCCandidateDecisionStatus.REJECTED_SESSION,
                        bar.index,
                        entry_time,
                        original_config,
                        config,
                    )
                )
                pending = None
            else:
                fill = (
                    bar.open_tick + config.entry_slippage_ticks
                    if pending.candidate.direction is GCBacktestDirection.BUY
                    else bar.open_tick - config.entry_slippage_ticks
                )
                if not _position_geometry_valid(
                    pending.candidate.direction,
                    pending.candidate.stop_tick,
                    fill,
                    pending.candidate.target_tick,
                ):
                    decisions.append(
                        _decision(
                            pending.candidate,
                            GCCandidateDecisionStatus.REJECTED_ENTRY_GEOMETRY,
                            bar.index,
                            entry_time,
                            original_config,
                            config,
                        )
                    )
                    pending = None
                else:
                    decisions.append(
                        _decision(
                            pending.candidate,
                            GCCandidateDecisionStatus.ACCEPTED,
                            bar.index,
                            entry_time,
                            original_config,
                            config,
                        )
                    )
                    position = _Position(
                        candidate=pending.candidate,
                        entry_index=bar.index,
                        entry_timestamp=entry_time,
                        entry_tick=fill,
                        holding_bars=0,
                        calendar_trade_date=calendar.trade_date,
                    )
                    pending = None

        if position is not None:
            position = _Position(
                candidate=position.candidate,
                entry_index=position.entry_index,
                entry_timestamp=position.entry_timestamp,
                entry_tick=position.entry_tick,
                holding_bars=position.holding_bars + 1,
                calendar_trade_date=position.calendar_trade_date,
            )
            exit_data = _exit_for_bar(position, bar, calendar, config)
            if exit_data is not None:
                exit_tick, exit_reason = exit_data
                trade = _trade(
                    position,
                    bar,
                    exit_tick,
                    exit_reason,
                    original_config,
                    config,
                )
                trades.append(trade)
                balance = _add_decimal_exact(balance, trade.net_pnl)
                snapshots.append(
                    _snapshot(
                        bar=bar,
                        balance=balance,
                        trade_ids=tuple(item.trade_id for item in trades),
                        original_config=original_config,
                        config=config,
                    )
                )
                position = None

        group = groups.get((bar.index, bar.timestamp), [])
        if len(group) > 1:
            decisions[:] = decisions[:pre_decision_count]
            trades[:] = trades[:pre_trade_count]
            snapshots[:] = snapshots[:pre_snapshot_count]
            balance = pre_balance
            pending = pre_pending
            position = pre_position
            for candidate in sorted(group, key=lambda item: item.candidate_id):
                decisions.append(
                    _decision(
                        candidate,
                        GCCandidateDecisionStatus.REJECTED_AMBIGUOUS_GROUP,
                        bar.index,
                        bar.timestamp,
                        original_config,
                        config,
                    )
                )
            ambiguous = True
            break
        if len(group) == 1:
            candidate = group[0]
            if (
                calendar.session_close_timestamp is None
                or bar.timestamp >= calendar.session_close_timestamp
            ):
                decisions.append(
                    _decision(
                        candidate,
                        GCCandidateDecisionStatus.REJECTED_SESSION,
                        bar.index,
                        bar.timestamp,
                        original_config,
                        config,
                    )
                )
            elif position is not None or pending is not None:
                decisions.append(
                    _decision(
                        candidate,
                        GCCandidateDecisionStatus.REJECTED_POSITION_OPEN,
                        bar.index,
                        bar.timestamp,
                        original_config,
                        config,
                    )
                )
            else:
                pending = _Pending(
                    candidate=candidate,
                    decision_timestamp=bar.timestamp,
                    calendar_trade_date=calendar.trade_date,
                )
                decisions.append(
                    _decision(
                        candidate,
                        GCCandidateDecisionStatus.PENDING_ENTRY,
                        bar.index,
                        bar.timestamp,
                        original_config,
                        config,
                    )
                )

    local_unknown: list[str] = []
    if pending is not None:
        local_unknown.append("NEXT_ELIGIBLE_BAR_UNAVAILABLE")
    if position is not None:
        local_unknown.append("OPEN_POSITION_REQUIRES_SESSION_FINAL_BAR")

    if forced_status is GCBacktestRunStatus.INVALID:
        status = GCBacktestRunStatus.INVALID
    elif forced_status is GCBacktestRunStatus.UNKNOWN or local_unknown:
        status = GCBacktestRunStatus.UNKNOWN
    elif ambiguous:
        status = GCBacktestRunStatus.AMBIGUOUS
    elif usable_candidates or decisions or trades:
        status = GCBacktestRunStatus.COMPLETE
    else:
        status = GCBacktestRunStatus.NONE

    return GCChronologicalBacktestResult(
        status=status,
        run_id=run_id,
        candidate_decisions=tuple(decisions),
        trades=tuple(trades),
        equity_snapshots=tuple(snapshots),
        final_balance=balance,
        reasons=issue_reasons,
        blocking_reasons=issue_reasons + tuple(local_unknown),
    )


def _scan_bars(values: object) -> _Scan:
    if type(values) is not tuple:
        return _Scan((), _Issue(GCBacktestRunStatus.INVALID, None, "BARS_NOT_TUPLE", True))
    valid: list[GCChronologicalBar] = []
    previous_index: int | None = None
    previous_time: datetime | None = None
    for value in values:
        moment = _safe_timestamp(value, "timestamp")
        try:
            if type(value) is not GCChronologicalBar:
                raise TypeError("bar must be a GCChronologicalBar")
            index = _validate_nonnegative_int(value.index, name="bar.index")
            timestamp = _normalize_timestamp(value.timestamp, name="bar.timestamp")
            open_tick = _validate_int(value.open_tick, name="bar.open_tick")
            high_tick = _validate_int(value.high_tick, name="bar.high_tick")
            low_tick = _validate_int(value.low_tick, name="bar.low_tick")
            close_tick = _validate_int(value.close_tick, name="bar.close_tick")
            _validate_nonnegative_int(value.volume, name="bar.volume")
            if value.is_closed is not True:
                raise ValueError("bar must be fully closed")
            if low_tick > high_tick or not (
                low_tick <= open_tick <= high_tick and low_tick <= close_tick <= high_tick
            ):
                raise ValueError("bar OHLC geometry is invalid")
            if previous_index is not None and index <= previous_index:
                raise ValueError("bar indices must be strictly increasing")
            if previous_time is not None and timestamp <= previous_time:
                raise ValueError("bar timestamps must be strictly increasing")
        except Exception:
            return _Scan(
                tuple(valid),
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    moment,
                    "MALFORMED_BAR",
                    moment is None,
                ),
            )
        valid.append(value)
        previous_index, previous_time = index, timestamp
    return _Scan(tuple(valid), None)


def _scan_candidates(values: object, config: _NormalizedConfig) -> _Scan:
    if type(values) is not tuple:
        return _Scan(
            (),
            _Issue(GCBacktestRunStatus.INVALID, None, "CANDIDATES_NOT_TUPLE", True),
        )
    valid: list[GCBacktestCandidate] = []
    previous_key: tuple[datetime, int] | None = None
    seen: set[str] = set()
    for value in values:
        moment = _safe_timestamp(value, "decision_timestamp")
        try:
            if type(value) is not GCBacktestCandidate:
                raise TypeError("candidate must be a GCBacktestCandidate")
            candidate_id = _validate_hash(value.candidate_id, name="candidate_id")
            if candidate_id in seen:
                raise ValueError("candidate IDs must be unique")
            if type(value.direction) is not GCBacktestDirection:
                raise TypeError("candidate direction is invalid")
            index = _validate_nonnegative_int(
                value.decision_index, name="candidate.decision_index"
            )
            timestamp = _normalize_timestamp(
                value.decision_timestamp, name="candidate.decision_timestamp"
            )
            _validate_int(value.stop_tick, name="candidate.stop_tick")
            _validate_int(value.target_tick, name="candidate.target_tick")
            _validate_positive_int(
                value.max_holding_bars, name="candidate.max_holding_bars"
            )
            contracts = _validate_positive_int(value.contracts, name="candidate.contracts")
            if contracts > config.maximum_contracts:
                raise ValueError("candidate contracts exceed configured maximum")
            key = (timestamp, index)
            if previous_key is not None and key < previous_key:
                raise ValueError("candidate tuple is not chronological")
        except Exception:
            return _Scan(
                tuple(valid),
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    moment,
                    "MALFORMED_CANDIDATE",
                    moment is None,
                ),
            )
        valid.append(value)
        previous_key = key
        seen.add(candidate_id)
    return _Scan(tuple(valid), None)


def _scan_calendars(values: object) -> _Scan:
    if type(values) is not tuple:
        return _Scan(
            (),
            _Issue(GCBacktestRunStatus.INVALID, None, "CALENDAR_NOT_TUPLE", True),
        )
    zone = _load_timezone()
    if zone is None:
        return _Scan(
            (),
            _Issue(GCBacktestRunStatus.INVALID, None, "TIMEZONE_UNAVAILABLE", True),
        )
    valid: list[KillZoneCalendarEntry] = []
    previous_date: date | None = None
    version: str | None = None
    for value in values:
        trade_date = _safe_date(value, "trade_date")
        issue_time = _trade_date_open(trade_date, zone) if trade_date is not None else None
        try:
            if type(value) is not KillZoneCalendarEntry:
                raise TypeError("calendar entry must be a KillZoneCalendarEntry")
            normalized_version = _normalize_text(
                value.calendar_version, name="calendar_version"
            )
            current_date = _validate_date(value.trade_date, name="trade_date")
            if previous_date is not None and current_date <= previous_date:
                raise ValueError("calendar trade dates must be strictly increasing")
            if version is not None and normalized_version != version:
                raise ValueError("calendar versions must match")
            if type(value.session_status) is not KillZoneSessionStatus:
                raise TypeError("session_status must be a KillZoneSessionStatus")
            expected_open = _trade_date_open(current_date, zone)
            standard_close = datetime.combine(
                current_date, time(17), tzinfo=zone
            ).astimezone(timezone.utc)
            if value.session_status is KillZoneSessionStatus.SESSION_CLOSED:
                if (
                    value.session_open_timestamp is not None
                    or value.session_close_timestamp is not None
                ):
                    raise ValueError("SESSION_CLOSED forbids timestamps")
            else:
                opening = _normalize_timestamp(
                    value.session_open_timestamp, name="session_open_timestamp"
                )
                closing = _normalize_timestamp(
                    value.session_close_timestamp, name="session_close_timestamp"
                )
                if opening != expected_open:
                    raise ValueError("session open mismatch")
                if not opening < closing <= standard_close:
                    raise ValueError("session close mismatch")
                if (
                    value.session_status is KillZoneSessionStatus.OPEN
                    and closing != standard_close
                ):
                    raise ValueError("OPEN requires standard close")
                if current_date.weekday() >= 5:
                    raise ValueError("tradable sessions require a weekday trade date")
        except Exception:
            return _Scan(
                tuple(valid),
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    issue_time,
                    "MALFORMED_CALENDAR_ENTRY",
                    issue_time is None,
                ),
            )
        valid.append(value)
        previous_date = current_date
        version = normalized_version
    return _Scan(tuple(valid), None)


def _relationship_issues(
    bars: tuple[object, ...],
    calendars: tuple[object, ...],
    candidates: tuple[object, ...],
) -> tuple[tuple[_Issue, ...], dict[tuple[int, datetime], KillZoneCalendarEntry]]:
    issues: list[_Issue] = []
    mapping: dict[tuple[int, datetime], KillZoneCalendarEntry] = {}
    if not bars and not candidates and calendars:
        first = calendars[0]
        assert isinstance(first, KillZoneCalendarEntry)
        zone = _load_timezone()
        issue_time = (
            _trade_date_open(first.trade_date, zone) if zone is not None else None
        )
        return (
            (
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    issue_time,
                    "UNREQUESTED_CALENDAR_ENTRY",
                    issue_time is None,
                ),
            ),
            mapping,
        )
    previous_bar: GCChronologicalBar | None = None
    previous_calendar: KillZoneCalendarEntry | None = None
    for value in bars:
        assert isinstance(value, GCChronologicalBar)
        matches = [
            entry
            for entry in calendars
            if isinstance(entry, KillZoneCalendarEntry)
            and _bar_in_calendar(value, entry)
        ]
        if len(matches) != 1:
            issues.append(
                _Issue(
                    GCBacktestRunStatus.UNKNOWN,
                    value.timestamp,
                    "MISSING_CALENDAR_COVERAGE",
                )
            )
            break
        entry = matches[0]
        mapping[(value.index, value.timestamp)] = entry
        if (
            previous_bar is not None
            and previous_calendar is not None
            and entry.trade_date == previous_calendar.trade_date
            and value.timestamp - previous_bar.timestamp != _FIVE_MINUTES
        ):
            issues.append(
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    value.timestamp,
                    "IN_SESSION_BAR_GAP",
                )
            )
            break
        if (
            previous_bar is not None
            and previous_calendar is not None
            and entry.trade_date != previous_calendar.trade_date
        ):
            previous_close = previous_calendar.session_close_timestamp
            current_open = entry.session_open_timestamp
            if (
                previous_close is None
                or current_open is None
                or previous_bar.timestamp != previous_close
                or value.timestamp - _FIVE_MINUTES != current_open
            ):
                issues.append(
                    _Issue(
                        GCBacktestRunStatus.INVALID,
                        value.timestamp,
                        "UNEXPLAINED_CROSS_SESSION_GAP",
                    )
                )
                break
        previous_bar, previous_calendar = value, entry

    bar_by_key = {
        (value.index, value.timestamp): value
        for value in bars
        if isinstance(value, GCChronologicalBar)
    }
    for value in candidates:
        assert isinstance(value, GCBacktestCandidate)
        bar = bar_by_key.get((value.decision_index, value.decision_timestamp))
        if bar is None:
            issues.append(
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    value.decision_timestamp,
                    "CANDIDATE_BAR_MISMATCH",
                )
            )
            break
        if not _position_geometry_valid(
            value.direction, value.stop_tick, bar.close_tick, value.target_tick
        ):
            issues.append(
                _Issue(
                    GCBacktestRunStatus.INVALID,
                    value.decision_timestamp,
                    "CANDIDATE_BOUNDARY_MISMATCH",
                )
            )
            break
    return tuple(issues), mapping


def _decision(
    candidate: GCBacktestCandidate,
    status: GCCandidateDecisionStatus,
    index: int,
    timestamp: datetime,
    original_config: GCChronologicalBacktestConfig,
    config: _NormalizedConfig,
) -> GCCandidateDecision:
    reason = _DECISION_REASON[status]
    normalized_timestamp = _normalize_timestamp(timestamp, name="decision.timestamp")
    decision_id = make_gc_chronological_backtest_id(
        identity_kind="DECISION",
        instrument=config.instrument,
        timeframe=config.timeframe,
        config=original_config,
        candidate_id=candidate.candidate_id,
        candidate_status=status,
        reason=reason,
        effective_index=index,
        effective_timestamp=normalized_timestamp,
    )
    return GCCandidateDecision(
        decision_id=decision_id,
        candidate_id=candidate.candidate_id,
        status=status,
        index=index,
        timestamp=normalized_timestamp,
        reason=reason,
    )


def _exit_for_bar(
    position: _Position,
    bar: GCChronologicalBar,
    calendar: KillZoneCalendarEntry,
    config: _NormalizedConfig,
) -> tuple[int, GCTradeExitReason] | None:
    candidate = position.candidate
    if candidate.direction is GCBacktestDirection.BUY:
        stop_touched = bar.low_tick <= candidate.stop_tick
        target_touched = bar.high_tick >= candidate.target_tick
    else:
        stop_touched = bar.high_tick >= candidate.stop_tick
        target_touched = bar.low_tick <= candidate.target_tick

    if stop_touched:
        raw = (
            min(bar.open_tick, candidate.stop_tick)
            if candidate.direction is GCBacktestDirection.BUY
            else max(bar.open_tick, candidate.stop_tick)
        )
        final = (
            raw - config.exit_slippage_ticks
            if candidate.direction is GCBacktestDirection.BUY
            else raw + config.exit_slippage_ticks
        )
        return final, GCTradeExitReason.STOP_LOSS
    if target_touched:
        final = (
            candidate.target_tick - config.exit_slippage_ticks
            if candidate.direction is GCBacktestDirection.BUY
            else candidate.target_tick + config.exit_slippage_ticks
        )
        return final, GCTradeExitReason.TARGET
    if position.holding_bars >= candidate.max_holding_bars:
        final = (
            bar.close_tick - config.exit_slippage_ticks
            if candidate.direction is GCBacktestDirection.BUY
            else bar.close_tick + config.exit_slippage_ticks
        )
        return final, GCTradeExitReason.EXPIRY_CLOSE
    if (
        calendar.session_close_timestamp is not None
        and bar.timestamp == calendar.session_close_timestamp
    ):
        final = (
            bar.close_tick - config.exit_slippage_ticks
            if candidate.direction is GCBacktestDirection.BUY
            else bar.close_tick + config.exit_slippage_ticks
        )
        return final, GCTradeExitReason.SESSION_CLOSE
    return None


def _trade(
    position: _Position,
    bar: GCChronologicalBar,
    exit_tick: int,
    exit_reason: GCTradeExitReason,
    original_config: GCChronologicalBacktestConfig,
    config: _NormalizedConfig,
) -> GCBacktestTrade:
    candidate = position.candidate
    normalized_exit_timestamp = _normalize_timestamp(
        bar.timestamp,
        name="exit_timestamp",
    )
    gross_ticks = (
        exit_tick - position.entry_tick
        if candidate.direction is GCBacktestDirection.BUY
        else position.entry_tick - exit_tick
    )
    gross_pnl = _multiply_decimal_int_exact(
        config.tick_value, gross_ticks * candidate.contracts
    )
    total_cost = _round_trip_cost(config, candidate.contracts)
    net_pnl = _subtract_decimal_exact(gross_pnl, total_cost)
    trade_id = make_gc_chronological_backtest_id(
        identity_kind="TRADE",
        instrument=config.instrument,
        timeframe=config.timeframe,
        config=original_config,
        candidate_id=candidate.candidate_id,
        direction=candidate.direction,
        contracts=candidate.contracts,
        entry_index=position.entry_index,
        entry_timestamp=position.entry_timestamp,
        entry_tick=position.entry_tick,
        stop_tick=candidate.stop_tick,
        target_tick=candidate.target_tick,
        exit_index=bar.index,
        exit_timestamp=normalized_exit_timestamp,
        exit_tick=exit_tick,
        exit_reason=exit_reason,
        gross_ticks=gross_ticks,
        gross_pnl=gross_pnl,
        total_cost=total_cost,
        net_pnl=net_pnl,
    )
    return GCBacktestTrade(
        trade_id=trade_id,
        candidate_id=candidate.candidate_id,
        direction=candidate.direction,
        contracts=candidate.contracts,
        entry_index=position.entry_index,
        entry_timestamp=position.entry_timestamp,
        entry_tick=position.entry_tick,
        stop_tick=candidate.stop_tick,
        target_tick=candidate.target_tick,
        exit_index=bar.index,
        exit_timestamp=normalized_exit_timestamp,
        exit_tick=exit_tick,
        exit_reason=exit_reason,
        gross_ticks=gross_ticks,
        gross_pnl=gross_pnl,
        total_cost=total_cost,
        net_pnl=net_pnl,
    )


def _snapshot(
    *,
    bar: GCChronologicalBar,
    balance: Decimal,
    trade_ids: tuple[str, ...],
    original_config: GCChronologicalBacktestConfig,
    config: _NormalizedConfig,
) -> GCEquitySnapshot:
    normalized_timestamp = _normalize_timestamp(
        bar.timestamp,
        name="snapshot.timestamp",
    )
    snapshot_id = make_gc_chronological_backtest_id(
        identity_kind="SNAPSHOT",
        instrument=config.instrument,
        timeframe=config.timeframe,
        config=original_config,
        effective_index=bar.index,
        effective_timestamp=normalized_timestamp,
        balance=balance,
        completed_trade_ids=trade_ids,
    )
    return GCEquitySnapshot(
        snapshot_id=snapshot_id,
        index=bar.index,
        timestamp=normalized_timestamp,
        balance=balance,
        completed_trade_ids=trade_ids,
    )


def _validate_config(value: object) -> _NormalizedConfig:
    if type(value) is not GCChronologicalBacktestConfig:
        raise TypeError("config must be a GCChronologicalBacktestConfig")
    instrument = _normalize_instrument(value.instrument)
    timeframe = _normalize_timeframe(value.timeframe)
    timezone_data_version = _normalize_text(
        value.timezone_data_version, name="timezone_data_version"
    )
    runtime = _runtime_timezone_data_version()
    if (
        runtime is None
        or _normalize_text(runtime, name="runtime_timezone_data_version")
        != timezone_data_version
    ):
        raise ValueError("timezone-data version mismatch")
    if _load_timezone() is None:
        raise ValueError("America/New_York is unavailable")
    tick_size = _require_decimal(value.tick_size, name="tick_size")
    tick_value = _require_decimal(value.tick_value, name="tick_value")
    starting_balance = _require_decimal(value.starting_balance, name="starting_balance")
    commission = _require_decimal(
        value.commission_per_side_per_contract,
        name="commission_per_side_per_contract",
    )
    fee = _require_decimal(
        value.exchange_fee_per_side_per_contract,
        name="exchange_fee_per_side_per_contract",
    )
    if tick_size <= 0 or tick_value <= 0 or starting_balance <= 0:
        raise ValueError("tick and balance values must be positive")
    if commission < 0 or fee < 0:
        raise ValueError("costs cannot be negative")
    return _NormalizedConfig(
        instrument=instrument,
        timeframe=timeframe,
        timezone_data_version=timezone_data_version,
        tick_size=tick_size,
        tick_value=tick_value,
        starting_balance=starting_balance,
        entry_slippage_ticks=_validate_nonnegative_int(
            value.entry_slippage_ticks, name="entry_slippage_ticks"
        ),
        exit_slippage_ticks=_validate_nonnegative_int(
            value.exit_slippage_ticks, name="exit_slippage_ticks"
        ),
        commission_per_side_per_contract=commission,
        exchange_fee_per_side_per_contract=fee,
        maximum_contracts=_validate_positive_int(
            value.maximum_contracts, name="maximum_contracts"
        ),
    )


def _config_payload(config: _NormalizedConfig) -> dict[str, object]:
    return {
        "commission_per_side_per_contract": _decimal_text(
            config.commission_per_side_per_contract
        ),
        "entry_slippage_ticks": config.entry_slippage_ticks,
        "exchange_fee_per_side_per_contract": _decimal_text(
            config.exchange_fee_per_side_per_contract
        ),
        "exit_slippage_ticks": config.exit_slippage_ticks,
        "instrument": config.instrument,
        "maximum_contracts": config.maximum_contracts,
        "starting_balance": _decimal_text(config.starting_balance),
        "tick_size": _decimal_text(config.tick_size),
        "tick_value": _decimal_text(config.tick_value),
        "timeframe": config.timeframe,
        "timezone_data_version": config.timezone_data_version,
    }


def _bar_digest(values: tuple[object, ...]) -> str:
    payload = [
        [
            value.index,
            _timestamp_text(value.timestamp),
            value.open_tick,
            value.high_tick,
            value.low_tick,
            value.close_tick,
            value.volume,
            value.is_closed,
        ]
        for value in values
        if isinstance(value, GCChronologicalBar)
    ]
    return _payload_hash(payload)


def _calendar_digest(values: tuple[object, ...]) -> str:
    payload = [
        [
            value.calendar_version.strip(),
            value.trade_date.isoformat(),
            value.session_status.value,
            None
            if value.session_open_timestamp is None
            else _timestamp_text(value.session_open_timestamp),
            None
            if value.session_close_timestamp is None
            else _timestamp_text(value.session_close_timestamp),
        ]
        for value in values
        if isinstance(value, KillZoneCalendarEntry)
    ]
    return _payload_hash(payload)


def _candidate_digest(values: tuple[object, ...]) -> str:
    grouped: dict[tuple[int, datetime], list[GCBacktestCandidate]] = {}
    for value in values:
        if isinstance(value, GCBacktestCandidate):
            grouped.setdefault((value.decision_index, value.decision_timestamp), []).append(value)
    payload: list[list[object]] = []
    for key in sorted(grouped, key=lambda item: (item[1], item[0])):
        for value in sorted(grouped[key], key=lambda item: item.candidate_id):
            payload.append(
                [
                    value.candidate_id,
                    value.direction.value,
                    value.decision_index,
                    _timestamp_text(value.decision_timestamp),
                    value.stop_tick,
                    value.target_tick,
                    value.max_holding_bars,
                    value.contracts,
                ]
            )
    return _payload_hash(payload)


def _bar_in_calendar(bar: GCChronologicalBar, entry: KillZoneCalendarEntry) -> bool:
    if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
        return False
    opening = entry.session_open_timestamp
    closing = entry.session_close_timestamp
    if opening is None or closing is None:
        return False
    bar_open = bar.timestamp - _FIVE_MINUTES
    return opening <= bar_open < closing and opening < bar.timestamp <= closing


def _position_geometry_valid(
    direction: GCBacktestDirection,
    stop_tick: int,
    entry_tick: int,
    target_tick: int,
) -> bool:
    return (
        stop_tick < entry_tick < target_tick
        if direction is GCBacktestDirection.BUY
        else target_tick < entry_tick < stop_tick
    )


def _validate_position_geometry(
    direction: GCBacktestDirection,
    stop_tick: int,
    entry_tick: int,
    target_tick: int,
) -> None:
    if not _position_geometry_valid(direction, stop_tick, entry_tick, target_tick):
        raise ValueError("directional position geometry is invalid")


def _normalize_instrument(value: object) -> str:
    normalized = _normalize_text(value, name="instrument").upper()
    if not _CONTRACT_PATTERN.fullmatch(normalized):
        raise ValueError("instrument must be one exact GC contract token")
    return normalized


def _normalize_timeframe(value: object) -> str:
    normalized = _normalize_text(value, name="timeframe").upper()
    if normalized != GC_CHRONOLOGICAL_TIMEFRAME:
        raise ValueError("timeframe must be exactly 5M")
    return normalized


def _normalize_text(value: object, *, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _normalize_timestamp(value: object, *, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _timestamp_text(value: object) -> str:
    normalized = _normalize_timestamp(value, name="timestamp")
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_date(value: object, *, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be a date")
    return value


def _validate_int(value: object, *, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    return value


def _validate_nonnegative_int(value: object, *, name: str) -> int:
    normalized = _validate_int(value, name=name)
    if normalized < 0:
        raise ValueError(f"{name} cannot be negative")
    return normalized


def _validate_positive_int(value: object, *, name: str) -> int:
    normalized = _validate_int(value, name=name)
    if normalized <= 0:
        raise ValueError(f"{name} must be positive")
    return normalized


def _require_decimal(value: object, *, name: str) -> Decimal:
    if type(value) is not Decimal:
        raise TypeError(f"{name} must be a Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    return value


def _decimal_text(value: Decimal) -> str:
    normalized = _require_decimal(value, name="decimal")
    if normalized.is_zero():
        return "0.0"
    sign, raw_digits, exponent = normalized.as_tuple()
    digits = list(raw_digits)
    while exponent < 0 and digits and digits[-1] == 0:
        digits.pop()
        exponent += 1
    text = "".join(str(digit) for digit in digits) or "0"
    if exponent >= 0:
        rendered = text + ("0" * exponent) + ".0"
    else:
        point = len(text) + exponent
        if point <= 0:
            rendered = "0." + ("0" * (-point)) + text
        else:
            rendered = text[:point] + "." + text[point:]
    return ("-" if sign else "") + rendered


def _decimal_precision(*values: Decimal | int) -> int:
    total = 32
    for value in values:
        if isinstance(value, Decimal):
            digits = len(value.as_tuple().digits)
            exponent = abs(value.as_tuple().exponent)
            total += digits + exponent
        else:
            total += len(str(abs(value)))
    return max(total, 64)


def _multiply_decimal_int_exact(value: Decimal, multiplier: int) -> Decimal:
    with localcontext() as context:
        context.prec = _decimal_precision(value, multiplier)
        return value * multiplier


def _add_decimal_exact(left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = _decimal_precision(left, right)
        return left + right


def _subtract_decimal_exact(left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = _decimal_precision(left, right)
        return left - right


def _round_trip_cost(config: _NormalizedConfig, contracts: int) -> Decimal:
    per_side = _add_decimal_exact(
        config.commission_per_side_per_contract,
        config.exchange_fee_per_side_per_contract,
    )
    return _multiply_decimal_int_exact(per_side, 2 * contracts)


def _payload_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_hash(value: object, *, name: str) -> str:
    if type(value) is not str or _HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 hash")
    return value


def _validate_hash_tuple(
    value: object,
    *,
    name: str,
    allow_empty: bool,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    normalized = tuple(_validate_hash(item, name=name) for item in value)
    if not allow_empty and not normalized:
        raise ValueError(f"{name} cannot be empty")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must contain unique hashes")
    return normalized


def _require_forbidden(*values: object) -> None:
    if any(value is not None for value in values):
        raise ValueError("identity kind received a forbidden parameter")


def _require_empty_tuple(value: object, *, name: str) -> None:
    if type(value) is not tuple or value:
        raise ValueError(f"{name} is forbidden for this identity kind")


def _forbid_source_digests(*values: object) -> None:
    if any(value is not None for value in values):
        raise ValueError("source digests are RUN-only")


def _safe_timestamp(value: object, name: str) -> datetime | None:
    try:
        return _normalize_timestamp(getattr(value, name), name=name)
    except Exception:
        return None


def _safe_date(value: object, name: str) -> date | None:
    try:
        return _validate_date(getattr(value, name), name=name)
    except Exception:
        return None


def _trade_date_open(value: date | None, zone: ZoneInfo) -> datetime | None:
    if value is None:
        return None
    return datetime.combine(
        value - timedelta(days=1), time(18), tzinfo=zone
    ).astimezone(timezone.utc)


def _runtime_timezone_data_version() -> str | None:
    try:
        return metadata.version("tzdata")
    except Exception:
        return None


def _load_timezone() -> ZoneInfo | None:
    try:
        return ZoneInfo(GC_CHRONOLOGICAL_TIMEZONE)
    except Exception:
        return None


__all__ = (
    "GC_CHRONOLOGICAL_BACKTEST_VERSION",
    "GC_CHRONOLOGICAL_TIMEFRAME",
    "GC_CHRONOLOGICAL_TIMEZONE",
    "GCBacktestDirection",
    "GCBacktestRunStatus",
    "GCCandidateDecisionStatus",
    "GCTradeExitReason",
    "GCChronologicalBar",
    "GCBacktestCandidate",
    "GCChronologicalBacktestConfig",
    "GCCandidateDecision",
    "GCBacktestTrade",
    "GCEquitySnapshot",
    "GCChronologicalBacktestResult",
    "make_gc_chronological_backtest_id",
    "run_gc_chronological_backtest",
)
