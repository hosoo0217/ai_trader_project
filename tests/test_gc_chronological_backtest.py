from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
from enum import Enum
import importlib.metadata
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest
from zoneinfo import ZoneInfo

import core.gc_chronological_backtest as gc_backtest
from core.gc_chronological_backtest import (
    GC_CHRONOLOGICAL_BACKTEST_VERSION,
    GC_CHRONOLOGICAL_TIMEFRAME,
    GC_CHRONOLOGICAL_TIMEZONE,
    GCBacktestCandidate,
    GCBacktestDirection,
    GCBacktestRunStatus,
    GCBacktestTrade,
    GCCandidateDecision,
    GCCandidateDecisionStatus,
    GCChronologicalBacktestConfig,
    GCChronologicalBacktestResult,
    GCChronologicalBar,
    GCEquitySnapshot,
    GCTradeExitReason,
    make_gc_chronological_backtest_id,
    run_gc_chronological_backtest,
)
from smc.kill_zones import KillZoneCalendarEntry, KillZoneSessionStatus


UTC = timezone.utc
NY = ZoneInfo("America/New_York")
TRADE_DATE = date(2026, 1, 6)
CALENDAR_VERSION = "CME-SYNTHETIC-1"
TZDATA_VERSION = importlib.metadata.version("tzdata")
HASH_A = "a" * 64
HASH_B = "b" * 64


def _session_bounds(
    trade_date: date = TRADE_DATE,
) -> tuple[datetime, datetime]:
    opening = datetime.combine(
        trade_date - timedelta(days=1), time(18), tzinfo=NY
    ).astimezone(UTC)
    closing = datetime.combine(trade_date, time(17), tzinfo=NY).astimezone(UTC)
    return opening, closing


def _calendar(
    trade_date: date = TRADE_DATE,
    *,
    status: KillZoneSessionStatus = KillZoneSessionStatus.OPEN,
    opening: datetime | None = None,
    closing: datetime | None = None,
    version: str = CALENDAR_VERSION,
) -> KillZoneCalendarEntry:
    if status is KillZoneSessionStatus.SESSION_CLOSED:
        return KillZoneCalendarEntry(version, trade_date, status, None, None)
    expected_open, expected_close = _session_bounds(trade_date)
    return KillZoneCalendarEntry(
        version,
        trade_date,
        status,
        expected_open if opening is None else opening,
        expected_close if closing is None else closing,
    )


def _bar(
    position: int,
    *,
    index: int | None = None,
    open_tick: int = 100,
    high_tick: int = 105,
    low_tick: int = 95,
    close_tick: int = 100,
    volume: int = 10,
    is_closed: bool = True,
    timestamp: datetime | None = None,
) -> GCChronologicalBar:
    opening, _ = _session_bounds()
    return GCChronologicalBar(
        index=position if index is None else index,
        timestamp=timestamp or opening + timedelta(minutes=5 * (position + 1)),
        open_tick=open_tick,
        high_tick=high_tick,
        low_tick=low_tick,
        close_tick=close_tick,
        volume=volume,
        is_closed=is_closed,
    )


def _candidate(
    bar: GCChronologicalBar,
    *,
    candidate_id: str = HASH_A,
    direction: GCBacktestDirection = GCBacktestDirection.BUY,
    stop_tick: int | None = None,
    target_tick: int | None = None,
    max_holding_bars: int = 3,
    contracts: int = 1,
) -> GCBacktestCandidate:
    if direction is GCBacktestDirection.BUY:
        selected_stop = 90 if stop_tick is None else stop_tick
        selected_target = 110 if target_tick is None else target_tick
    else:
        selected_stop = 110 if stop_tick is None else stop_tick
        selected_target = 90 if target_tick is None else target_tick
    return GCBacktestCandidate(
        candidate_id=candidate_id,
        direction=direction,
        decision_index=bar.index,
        decision_timestamp=bar.timestamp,
        stop_tick=selected_stop,
        target_tick=selected_target,
        max_holding_bars=max_holding_bars,
        contracts=contracts,
    )


def _config(**changes: object) -> GCChronologicalBacktestConfig:
    values: dict[str, object] = {
        "instrument": "GCZ26",
        "timeframe": "5M",
        "timezone_data_version": TZDATA_VERSION,
        "tick_size": Decimal("0.1"),
        "tick_value": Decimal("10"),
        "starting_balance": Decimal("100000"),
        "entry_slippage_ticks": 1,
        "exit_slippage_ticks": 1,
        "commission_per_side_per_contract": Decimal("2"),
        "exchange_fee_per_side_per_contract": Decimal("1"),
        "maximum_contracts": 5,
    }
    values.update(changes)
    return GCChronologicalBacktestConfig(**values)  # type: ignore[arg-type]


def _run(
    *,
    bars: tuple[GCChronologicalBar, ...] | None = None,
    calendars: tuple[KillZoneCalendarEntry, ...] | None = None,
    candidates: tuple[GCBacktestCandidate, ...] | None = None,
    config: GCChronologicalBacktestConfig | None = None,
) -> GCChronologicalBacktestResult:
    return run_gc_chronological_backtest(
        bars=(_bar(0),) if bars is None else bars,
        calendar_entries=(_calendar(),) if calendars is None else calendars,
        candidates=() if candidates is None else candidates,
        config=_config() if config is None else config,
    )


def _completed_buy_run() -> GCChronologicalBacktestResult:
    decision_bar = _bar(0)
    entry_and_target = _bar(1, open_tick=100, high_tick=111, low_tick=95, close_tick=108)
    return _run(
        bars=(decision_bar, entry_and_target),
        candidates=(_candidate(decision_bar),),
    )


# Case 1
@pytest.mark.parametrize("missing", ["bars", "calendar_entries", "candidates"])
def test_case_01_missing_top_level_context_is_unknown(missing: str) -> None:
    kwargs: dict[str, object] = {
        "bars": (_bar(0),),
        "calendar_entries": (_calendar(),),
        "candidates": (),
        "config": _config(),
    }
    kwargs[missing] = None
    result = run_gc_chronological_backtest(**kwargs)  # type: ignore[arg-type]
    assert result.status is GCBacktestRunStatus.UNKNOWN
    assert result.run_id is None


@pytest.mark.parametrize("missing,malformed_key", [("bars", "candidates"), ("candidates", "calendar_entries")])
def test_case_01_malformed_supplied_counterpart_overrides_missing_unknown(
    missing: str,
    malformed_key: str,
) -> None:
    malformed_calendar = replace(_calendar(), session_close_timestamp=None)
    kwargs: dict[str, object] = {
        "bars": (_bar(0),),
        "calendar_entries": (_calendar(),),
        "candidates": (),
        "config": _config(),
    }
    kwargs[missing] = None
    kwargs[malformed_key] = (
        (replace(_candidate(_bar(0)), candidate_id="bad"),)
        if malformed_key == "candidates"
        else (malformed_calendar,)
    )
    result = run_gc_chronological_backtest(**kwargs)  # type: ignore[arg-type]
    assert result.status is GCBacktestRunStatus.INVALID
    assert result.candidate_decisions == result.trades == result.equity_snapshots == ()


# Case 2
def test_case_02_complete_empty_inputs_are_none() -> None:
    result = _run(bars=(), calendars=(), candidates=())
    assert result.status is GCBacktestRunStatus.NONE
    assert result.run_id is not None
    assert result.final_balance == Decimal("100000")
    unrequested = _run(bars=(), calendars=(_calendar(),), candidates=())
    assert unrequested.status is GCBacktestRunStatus.INVALID
    assert unrequested.candidate_decisions == ()


# Case 3
@pytest.mark.parametrize("instrument", ["", "GC", "XAUUSD", "GC1!", "GC_CONT"])
def test_case_03_contract_identity_rejects_generic_or_aliases(instrument: str) -> None:
    result = _run(config=_config(instrument=instrument))
    assert result.status is GCBacktestRunStatus.INVALID


def test_case_03_contract_normalization_is_deterministic() -> None:
    assert _run(config=_config(instrument="  gcz26  ")).run_id == _run().run_id


# Case 4
@pytest.mark.parametrize("timeframe", ["1M", "M5", "15M", ""])
def test_case_04_only_exact_normalized_5m_is_valid(timeframe: str) -> None:
    assert _run(config=_config(timeframe=timeframe)).status is GCBacktestRunStatus.INVALID


def test_case_04_case_and_space_normalization_preserves_5m() -> None:
    assert _run(config=_config(timeframe=" 5m ")).status is GCBacktestRunStatus.NONE


# Case 5
def test_case_05_bar_is_frozen_and_requires_aware_closed_timestamp() -> None:
    with pytest.raises(FrozenInstanceError):
        _bar(0).close_tick = 1  # type: ignore[misc]
    naive = replace(_bar(0), timestamp=datetime(2026, 1, 5, 18, 5))
    assert _run(bars=(naive,)).status is GCBacktestRunStatus.INVALID
    assert _run(bars=(replace(_bar(0), is_closed=False),)).status is GCBacktestRunStatus.INVALID


# Case 6
@pytest.mark.parametrize(
    "bar",
    [
        replace(_bar(0), low_tick=106),
        replace(_bar(0), high_tick=94),
        replace(_bar(0), volume=-1),
        replace(_bar(0), open_tick=True),
        replace(_bar(0), volume=True),
    ],
)
def test_case_06_bar_geometry_and_integer_volume_fail_closed(
    bar: GCChronologicalBar,
) -> None:
    assert _run(bars=(bar,)).status is GCBacktestRunStatus.INVALID


# Case 7
def test_case_07_bar_order_is_not_silently_sorted() -> None:
    assert _run(bars=(_bar(1), _bar(0))).status is GCBacktestRunStatus.INVALID
    assert _run(bars=(_bar(0), replace(_bar(1), index=0))).status is GCBacktestRunStatus.INVALID


# Case 8
def test_case_08_in_session_gap_is_invalid() -> None:
    assert _run(bars=(_bar(0), _bar(2))).status is GCBacktestRunStatus.INVALID

    next_date = date(2026, 1, 7)
    next_open, _ = _session_bounds(next_date)
    incomplete_previous = _bar(0)
    next_first = _bar(1, timestamp=next_open + timedelta(minutes=5))
    assert _run(
        bars=(incomplete_previous, next_first),
        calendars=(_calendar(), _calendar(next_date)),
    ).status is GCBacktestRunStatus.INVALID

    _, first_close = _session_bounds()
    valid_previous_final = _bar(0, timestamp=first_close)
    valid_next_first = _bar(1, timestamp=next_open + timedelta(minutes=5))
    assert _run(
        bars=(valid_previous_final, valid_next_first),
        calendars=(_calendar(), _calendar(next_date)),
    ).status is GCBacktestRunStatus.NONE


# Case 9
def test_case_09_calendar_and_runtime_timezone_are_bound() -> None:
    assert _run(config=_config(timezone_data_version="WRONG")).status is GCBacktestRunStatus.INVALID
    malformed = replace(_calendar(), session_close_timestamp=None)
    assert _run(calendars=(malformed,)).status is GCBacktestRunStatus.INVALID


@pytest.mark.parametrize("attribute", ["_runtime_timezone_data_version", "_load_timezone"])
def test_case_09_runtime_timezone_unavailability_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    attribute: str,
) -> None:
    monkeypatch.setattr(gc_backtest, attribute, lambda: None)
    assert _run().status is GCBacktestRunStatus.INVALID
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(**_run_identity_kwargs())


# Case 10
def test_case_10_missing_calendar_is_unknown_but_malformed_is_invalid() -> None:
    unknown = run_gc_chronological_backtest(
        bars=(_bar(0),), calendar_entries=None, candidates=(), config=_config()
    )
    assert unknown.status is GCBacktestRunStatus.UNKNOWN
    invalid = run_gc_chronological_backtest(
        bars=(replace(_bar(0), high_tick=90),),
        calendar_entries=None,
        candidates=(),
        config=_config(),
    )
    assert invalid.status is GCBacktestRunStatus.INVALID


# Case 11
def test_case_11_candidate_must_reconcile_to_bar_and_hash_shape() -> None:
    bar = _bar(0)
    assert _run(candidates=(replace(_candidate(bar), candidate_id="bad"),)).status is GCBacktestRunStatus.INVALID
    missing = replace(_candidate(bar), decision_index=99)
    assert _run(candidates=(missing,)).status is GCBacktestRunStatus.INVALID


# Case 12
@pytest.mark.parametrize(
    "candidate",
    [
        _candidate(_bar(0), stop_tick=100),
        _candidate(_bar(0), target_tick=100),
        _candidate(_bar(0), direction=GCBacktestDirection.SELL, stop_tick=100),
        _candidate(_bar(0), direction=GCBacktestDirection.SELL, target_tick=100),
    ],
)
def test_case_12_directional_boundary_geometry(candidate: GCBacktestCandidate) -> None:
    assert _run(candidates=(candidate,)).status is GCBacktestRunStatus.INVALID


# Case 13
@pytest.mark.parametrize("holding,contracts", [(0, 1), (1, 0), (1, 6)])
def test_case_13_positive_holding_and_contract_limit(holding: int, contracts: int) -> None:
    bar = _bar(0)
    candidate = _candidate(bar, max_holding_bars=holding, contracts=contracts)
    assert _run(candidates=(candidate,)).status is GCBacktestRunStatus.INVALID


# Case 14
def test_case_14_same_moment_group_is_atomic_and_permutation_independent() -> None:
    bar = _bar(0)
    a = _candidate(bar, candidate_id=HASH_A)
    b = _candidate(bar, candidate_id=HASH_B)
    first = _run(candidates=(a, b))
    second = _run(candidates=(b, a))
    assert first == second
    assert first.status is GCBacktestRunStatus.AMBIGUOUS
    assert tuple(item.candidate_id for item in first.candidate_decisions) == (HASH_A, HASH_B)


# Case 15
def test_case_15_duplicate_candidate_is_invalid_not_ambiguous() -> None:
    candidate = _candidate(_bar(0))
    result = _run(candidates=(candidate, candidate))
    assert result.status is GCBacktestRunStatus.INVALID
    assert result.candidate_decisions == ()


# Case 16
def test_case_16_candidate_at_session_close_is_rejected() -> None:
    _, closing = _session_bounds()
    bar = _bar(0, timestamp=closing)
    result = _run(bars=(bar,), candidates=(_candidate(bar),))
    assert result.status is GCBacktestRunStatus.COMPLETE
    assert result.candidate_decisions[0].status is GCCandidateDecisionStatus.REJECTED_SESSION


# Case 17
def test_case_17_candidate_never_enters_on_decision_bar() -> None:
    bar = _bar(0)
    result = _run(candidates=(_candidate(bar),))
    assert result.status is GCBacktestRunStatus.UNKNOWN
    assert result.trades == ()
    assert result.candidate_decisions[0].status is GCCandidateDecisionStatus.PENDING_ENTRY


# Case 18
def test_case_18_buy_enters_next_open_with_adverse_slippage() -> None:
    result = _completed_buy_run()
    assert result.status is GCBacktestRunStatus.COMPLETE
    assert result.trades[0].entry_tick == 101
    assert [d.status for d in result.candidate_decisions[:2]] == [
        GCCandidateDecisionStatus.PENDING_ENTRY,
        GCCandidateDecisionStatus.ACCEPTED,
    ]
    offset = timezone(timedelta(hours=9))
    shifted = tuple(
        replace(bar, timestamp=bar.timestamp.astimezone(offset))
        for bar in (_bar(0), _bar(1, high_tick=111))
    )
    shifted_candidate = replace(_candidate(shifted[0]), decision_timestamp=shifted[0].timestamp)
    shifted_result = _run(bars=shifted, candidates=(shifted_candidate,))
    assert shifted_result.trades[0].entry_timestamp.tzinfo is UTC
    assert shifted_result.trades[0].exit_timestamp.tzinfo is UTC
    assert shifted_result.equity_snapshots[0].timestamp.tzinfo is UTC


# Case 19
def test_case_19_sell_enters_next_open_with_adverse_slippage() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=105, low_tick=89, close_tick=92)
    result = _run(
        bars=(bar0, bar1),
        candidates=(_candidate(bar0, direction=GCBacktestDirection.SELL),),
    )
    assert result.trades[0].entry_tick == 99
    assert result.trades[0].exit_reason is GCTradeExitReason.TARGET


# Case 20
def test_case_20_post_slippage_entry_geometry_rejects_without_rescue() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=109, high_tick=109, low_tick=100, close_tick=105)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    assert result.status is GCBacktestRunStatus.COMPLETE
    assert result.candidate_decisions[-1].status is GCCandidateDecisionStatus.REJECTED_ENTRY_GEOMETRY
    assert result.trades == ()


# Case 21
def test_case_21_missing_next_bar_is_unknown() -> None:
    result = _run(candidates=(_candidate(_bar(0)),))
    assert result.status is GCBacktestRunStatus.UNKNOWN
    assert "NEXT_ELIGIBLE_BAR_UNAVAILABLE" in result.blocking_reasons


# Case 22
def test_case_22_candidate_while_open_is_rejected_and_not_queued() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=105, low_tick=95)
    bar2 = _bar(2, high_tick=111, low_tick=95)
    result = _run(
        bars=(bar0, bar1, bar2),
        candidates=(_candidate(bar0), _candidate(bar1, candidate_id=HASH_B)),
    )
    assert any(d.status is GCCandidateDecisionStatus.REJECTED_POSITION_OPEN for d in result.candidate_decisions)
    assert len(result.trades) == 1


# Case 23
def test_case_23_close_and_new_decision_waits_for_following_bar() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95, close_tick=108)
    bar2 = _bar(2, open_tick=100, high_tick=111, low_tick=95, close_tick=108)
    result = _run(
        bars=(bar0, bar1, bar2),
        candidates=(_candidate(bar0), _candidate(bar1, candidate_id=HASH_B)),
    )
    assert len(result.trades) == 2
    assert result.trades[1].entry_index == bar2.index


# Case 24
@pytest.mark.parametrize("target", [False, True])
def test_case_24_buy_stop_and_target_lifecycle(target: bool) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=111 if target else 105, low_tick=95 if target else 89)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    assert result.trades[0].exit_reason is (GCTradeExitReason.TARGET if target else GCTradeExitReason.STOP_LOSS)


# Case 25
@pytest.mark.parametrize("target", [False, True])
def test_case_25_sell_stop_and_target_lifecycle(target: bool) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=105 if target else 111, low_tick=89 if target else 95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, direction=GCBacktestDirection.SELL),))
    assert result.trades[0].exit_reason is (GCTradeExitReason.TARGET if target else GCTradeExitReason.STOP_LOSS)


# Case 26
@pytest.mark.parametrize("direction", list(GCBacktestDirection))
def test_case_26_both_boundaries_choose_stop(direction: GCBacktestDirection) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=111, low_tick=89)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, direction=direction),))
    assert result.trades[0].exit_reason is GCTradeExitReason.STOP_LOSS


# Case 27
@pytest.mark.parametrize(
    "direction,opening,expected",
    [(GCBacktestDirection.BUY, 85, 84), (GCBacktestDirection.SELL, 115, 116)],
)
def test_case_27_gap_through_stop_uses_worse_open(
    direction: GCBacktestDirection,
    opening: int,
    expected: int,
) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=105, low_tick=95)
    bar2 = _bar(2, open_tick=opening, high_tick=max(105, opening), low_tick=min(95, opening), close_tick=100)
    result = _run(bars=(bar0, bar1, bar2), candidates=(_candidate(bar0, direction=direction),))
    assert result.trades[0].exit_tick == expected


# Case 28
@pytest.mark.parametrize(
    "direction,opening,expected",
    [(GCBacktestDirection.BUY, 115, 109), (GCBacktestDirection.SELL, 85, 91)],
)
def test_case_28_target_gap_has_no_favorable_improvement(
    direction: GCBacktestDirection,
    opening: int,
    expected: int,
) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=105, low_tick=95)
    bar2 = _bar(2, open_tick=opening, high_tick=max(115, opening), low_tick=min(85, opening), close_tick=100)
    if direction is GCBacktestDirection.BUY:
        bar2 = replace(bar2, low_tick=111, close_tick=112)
    else:
        bar2 = replace(bar2, high_tick=89, close_tick=88)
    result = _run(bars=(bar0, bar1, bar2), candidates=(_candidate(bar0, direction=direction),))
    assert result.trades[0].exit_tick == expected


# Case 29
def test_case_29_entry_bar_counts_as_holding_bar_one() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=105, low_tick=95, close_tick=103)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, max_holding_bars=1),))
    assert result.trades[0].exit_reason is GCTradeExitReason.EXPIRY_CLOSE


# Case 30
def test_case_30_stop_target_precede_expiry() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, max_holding_bars=1),))
    assert result.trades[0].exit_reason is GCTradeExitReason.TARGET


# Case 31
def test_case_31_stop_target_precede_session_close() -> None:
    _, closing = _session_bounds()
    bar0 = _bar(0, timestamp=closing - timedelta(minutes=5))
    bar1 = _bar(1, timestamp=closing, high_tick=111, low_tick=95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    assert result.trades[0].exit_reason is GCTradeExitReason.TARGET


# Case 32
def test_case_32_missing_final_session_bar_with_open_position_is_unknown() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=105, low_tick=95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, max_holding_bars=20),))
    assert result.status is GCBacktestRunStatus.UNKNOWN


def test_case_32_unknown_overrides_prior_complete_but_preserves_it() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    bar2 = _bar(2)
    result = _run(
        bars=(bar0, bar1, bar2),
        candidates=(_candidate(bar0), _candidate(bar2, candidate_id=HASH_B)),
    )
    assert result.status is GCBacktestRunStatus.UNKNOWN
    assert len(result.trades) == 1
    assert result.final_balance == result.equity_snapshots[-1].balance


# Case 33
def test_case_33_data_end_never_synthesizes_a_close() -> None:
    result = _run(
        bars=(_bar(0), _bar(1, high_tick=105, low_tick=95)),
        candidates=(_candidate(_bar(0), max_holding_bars=20),),
    )
    assert result.trades == ()
    assert result.equity_snapshots == ()


# Case 34
def test_case_34_slippage_is_applied_once_and_can_be_large() -> None:
    config = _config(entry_slippage_ticks=2, exit_slippage_ticks=20)
    bar0 = _bar(0)
    bar1 = _bar(1, open_tick=100, high_tick=111, low_tick=95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),), config=config)
    assert result.trades[0].entry_tick == 102
    assert result.trades[0].exit_tick == 90


# Case 35
def test_case_35_round_trip_cost_is_exact_for_multiple_contracts() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    result = _run(bars=(bar0, bar1), candidates=(_candidate(bar0, contracts=2),))
    assert result.trades[0].total_cost == Decimal("12")


# Case 36
def test_case_36_decimal_pnl_reconciles_exactly() -> None:
    result = _completed_buy_run()
    trade = result.trades[0]
    assert trade.gross_ticks == 8
    assert trade.gross_pnl == Decimal("80")
    assert trade.net_pnl == Decimal("74")
    assert result.final_balance == Decimal("100074")


# Case 37
def test_case_37_identity_is_decimal_context_independent_and_signed_zero_stable() -> None:
    kwargs = {
        **_run_identity_kwargs(),
        "config": _config(commission_per_side_per_contract=Decimal("0")),
    }
    with localcontext() as context:
        context.prec = 3
        first = make_gc_chronological_backtest_id(**kwargs)
    with localcontext() as context:
        context.prec = 50
        second = make_gc_chronological_backtest_id(**kwargs)
    assert first == second
    zero = replace(kwargs["config"], commission_per_side_per_contract=Decimal("-0.0"))
    assert make_gc_chronological_backtest_id(
        **{**kwargs, "config": zero}
    ) == make_gc_chronological_backtest_id(**kwargs)


# Case 38
def test_case_38_multiple_trades_have_ordered_equity_history() -> None:
    bar0, bar1, bar2 = _bar(0), _bar(1, high_tick=111, low_tick=95), _bar(2, high_tick=111, low_tick=95)
    result = _run(bars=(bar0, bar1, bar2), candidates=(_candidate(bar0), _candidate(bar1, candidate_id=HASH_B)))
    assert len(result.equity_snapshots) == 2
    assert result.equity_snapshots[-1].completed_trade_ids == tuple(t.trade_id for t in result.trades)


# Case 39
def test_case_39_public_outputs_are_frozen() -> None:
    result = _completed_buy_run()
    for value in (result, result.candidate_decisions[0], result.trades[0], result.equity_snapshots[0]):
        with pytest.raises(FrozenInstanceError):
            value.status = None  # type: ignore[attr-defined,misc]


def _run_identity_kwargs() -> dict[str, object]:
    return {
        "identity_kind": "RUN",
        "instrument": "GCZ26",
        "timeframe": "5M",
        "config": _config(),
        "bar_digest": "1" * 64,
        "calendar_digest": "2" * 64,
        "candidate_digest": "3" * 64,
    }


# Case 40
def test_case_40_run_identity_schema_and_sensitivity() -> None:
    base = _run_identity_kwargs()
    identity = make_gc_chronological_backtest_id(**base)
    assert len(identity) == 64
    for field_name in ("bar_digest", "calendar_digest", "candidate_digest"):
        broken = dict(base)
        broken[field_name] = None
        with pytest.raises((TypeError, ValueError)):
            make_gc_chronological_backtest_id(**broken)
    assert make_gc_chronological_backtest_id(**{**base, "bar_digest": "4" * 64}) != identity
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(**{**base, "candidate_id": HASH_A})
    for forbidden_name, forbidden_value in (
        ("reason", "NEXT_BAR_ENTRY_PENDING"),
        ("effective_index", 0),
        ("completed_trade_ids", (HASH_A,)),
    ):
        with pytest.raises((TypeError, ValueError)):
            make_gc_chronological_backtest_id(
                **{**base, forbidden_name: forbidden_value}
            )


# Case 41
def test_case_41_decision_identity_schema_and_reason_pairing() -> None:
    kwargs = {
        "identity_kind": "DECISION",
        "instrument": "GCZ26",
        "timeframe": "5M",
        "config": _config(),
        "candidate_id": HASH_A,
        "candidate_status": GCCandidateDecisionStatus.PENDING_ENTRY,
        "reason": "NEXT_BAR_ENTRY_PENDING",
        "effective_index": 0,
        "effective_timestamp": _bar(0).timestamp,
    }
    assert len(make_gc_chronological_backtest_id(**kwargs)) == 64
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(**{**kwargs, "reason": "POSITION_ALREADY_OPEN"})


# Case 42
def test_case_42_trade_identity_recomputes_pnl_and_lifecycle() -> None:
    trade = _completed_buy_run().trades[0]
    kwargs = _trade_identity_kwargs(trade)
    assert make_gc_chronological_backtest_id(**kwargs) == trade.trade_id
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(**{**kwargs, "net_pnl": Decimal("999")})
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(
            **{
                **kwargs,
                "exit_tick": trade.stop_tick,
                "exit_reason": GCTradeExitReason.STOP_LOSS,
                "gross_ticks": trade.stop_tick - trade.entry_tick,
                "gross_pnl": Decimal(trade.stop_tick - trade.entry_tick) * Decimal("10"),
                "net_pnl": Decimal(trade.stop_tick - trade.entry_tick) * Decimal("10") - Decimal("6"),
            }
        )


def _trade_identity_kwargs(trade: GCBacktestTrade) -> dict[str, object]:
    return {
        "identity_kind": "TRADE",
        "instrument": "GCZ26",
        "timeframe": "5M",
        "config": _config(),
        "candidate_id": trade.candidate_id,
        "direction": trade.direction,
        "contracts": trade.contracts,
        "entry_index": trade.entry_index,
        "entry_timestamp": trade.entry_timestamp,
        "entry_tick": trade.entry_tick,
        "stop_tick": trade.stop_tick,
        "target_tick": trade.target_tick,
        "exit_index": trade.exit_index,
        "exit_timestamp": trade.exit_timestamp,
        "exit_tick": trade.exit_tick,
        "exit_reason": trade.exit_reason,
        "gross_ticks": trade.gross_ticks,
        "gross_pnl": trade.gross_pnl,
        "total_cost": trade.total_cost,
        "net_pnl": trade.net_pnl,
    }


# Case 43
def test_case_43_snapshot_identity_requires_ordered_unique_history() -> None:
    snapshot = _completed_buy_run().equity_snapshots[0]
    kwargs = {
        "identity_kind": "SNAPSHOT",
        "instrument": "GCZ26",
        "timeframe": "5M",
        "config": _config(),
        "effective_index": snapshot.index,
        "effective_timestamp": snapshot.timestamp,
        "balance": snapshot.balance,
        "completed_trade_ids": snapshot.completed_trade_ids,
    }
    assert make_gc_chronological_backtest_id(**kwargs) == snapshot.snapshot_id
    with pytest.raises((TypeError, ValueError)):
        make_gc_chronological_backtest_id(**{**kwargs, "completed_trade_ids": (snapshot.completed_trade_ids[0],) * 2})


# Case 44
def test_case_44_exact_public_api_fields_enums_and_exports() -> None:
    assert GC_CHRONOLOGICAL_BACKTEST_VERSION == "GC-CHRONOLOGICAL-BACKTEST-V1"
    assert GC_CHRONOLOGICAL_TIMEFRAME == "5M"
    assert GC_CHRONOLOGICAL_TIMEZONE == "America/New_York"
    assert [item.value for item in GCBacktestDirection] == ["BUY", "SELL"]
    assert [item.value for item in GCBacktestRunStatus] == ["COMPLETE", "NONE", "UNKNOWN", "AMBIGUOUS", "INVALID"]
    assert all(
        issubclass(item, Enum)
        for item in (
            GCBacktestDirection,
            GCBacktestRunStatus,
            GCCandidateDecisionStatus,
            GCTradeExitReason,
        )
    )
    analyzer_parameters = inspect.signature(
        run_gc_chronological_backtest
    ).parameters
    assert tuple(analyzer_parameters) == (
        "bars",
        "calendar_entries",
        "candidates",
        "config",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in analyzer_parameters.values()
    )
    assert [field.name for field in fields(GCChronologicalBar)] == [
        "index", "timestamp", "open_tick", "high_tick", "low_tick",
        "close_tick", "volume", "is_closed",
    ]
    assert [field.name for field in fields(GCBacktestCandidate)] == [
        "candidate_id", "direction", "decision_index", "decision_timestamp",
        "stop_tick", "target_tick", "max_holding_bars", "contracts",
    ]
    assert [field.name for field in fields(GCChronologicalBacktestConfig)] == [
        "instrument", "timeframe", "timezone_data_version", "tick_size",
        "tick_value", "starting_balance", "entry_slippage_ticks",
        "exit_slippage_ticks", "commission_per_side_per_contract",
        "exchange_fee_per_side_per_contract", "maximum_contracts",
    ]
    assert [field.name for field in fields(GCCandidateDecision)] == [
        "decision_id", "candidate_id", "status", "index", "timestamp", "reason",
    ]
    assert [field.name for field in fields(GCBacktestTrade)] == [
        "trade_id", "candidate_id", "direction", "contracts", "entry_index",
        "entry_timestamp", "entry_tick", "stop_tick", "target_tick", "exit_index",
        "exit_timestamp", "exit_tick", "exit_reason", "gross_ticks", "gross_pnl",
        "total_cost", "net_pnl",
    ]
    assert [field.name for field in fields(GCEquitySnapshot)] == [
        "snapshot_id", "index", "timestamp", "balance", "completed_trade_ids",
    ]
    assert [field.name for field in fields(GCChronologicalBacktestResult)] == [
        "status", "run_id", "candidate_decisions", "trades", "equity_snapshots",
        "final_balance", "reasons", "blocking_reasons",
    ]
    builder_parameters = inspect.signature(make_gc_chronological_backtest_id).parameters
    assert tuple(builder_parameters) == (
        "identity_kind", "instrument", "timeframe", "config", "bar_digest",
        "calendar_digest", "candidate_digest", "candidate_id", "candidate_status",
        "reason", "direction", "contracts", "entry_index", "entry_timestamp",
        "entry_tick", "stop_tick", "target_tick", "exit_index", "exit_timestamp",
        "exit_tick", "exit_reason", "gross_ticks", "gross_pnl", "total_cost",
        "net_pnl", "effective_index", "effective_timestamp", "balance",
        "completed_trade_ids",
    )
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in builder_parameters.values())
    assert set(gc_backtest.__all__) == {
        "GC_CHRONOLOGICAL_BACKTEST_VERSION", "GC_CHRONOLOGICAL_TIMEFRAME", "GC_CHRONOLOGICAL_TIMEZONE",
        "GCBacktestDirection", "GCBacktestRunStatus", "GCCandidateDecisionStatus", "GCTradeExitReason",
        "GCChronologicalBar", "GCBacktestCandidate", "GCChronologicalBacktestConfig", "GCCandidateDecision",
        "GCBacktestTrade", "GCEquitySnapshot", "GCChronologicalBacktestResult",
        "make_gc_chronological_backtest_id", "run_gc_chronological_backtest",
    }


# Case 45
def test_case_45_later_malformed_bar_preserves_prior_completed_evidence() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    malformed = replace(_bar(2), high_tick=90)
    prefix = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    result = _run(bars=(bar0, bar1, malformed), candidates=(_candidate(bar0),))
    assert result.status is GCBacktestRunStatus.INVALID
    assert result.candidate_decisions == prefix.candidate_decisions
    assert result.trades == prefix.trades
    assert result.equity_snapshots == prefix.equity_snapshots

    internally_malformed = object.__new__(GCChronologicalBar)
    object.__setattr__(internally_malformed, "index", 2)
    object.__setattr__(internally_malformed, "timestamp", _bar(2).timestamp)
    result_internal = _run(
        bars=(bar0, bar1, internally_malformed),  # type: ignore[arg-type]
        candidates=(_candidate(bar0),),
    )
    assert result_internal.status is GCBacktestRunStatus.INVALID
    assert result_internal.trades == prefix.trades


@pytest.mark.parametrize("kind", ["candidate", "calendar"])
def test_case_45_later_malformed_dependency_preserves_prior_evidence(kind: str) -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    prefix = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    next_date = date(2026, 1, 7)
    if kind == "candidate":
        bar2 = _bar(2)
        result = _run(
            bars=(bar0, bar1, bar2),
            candidates=(
                _candidate(bar0),
                replace(_candidate(bar2, candidate_id=HASH_B), candidate_id="bad"),
            ),
        )
    else:
        malformed = replace(_calendar(next_date), session_close_timestamp=None)
        result = _run(
            bars=(bar0, bar1),
            calendars=(_calendar(), malformed),
            candidates=(_candidate(bar0),),
        )
    assert result.status is GCBacktestRunStatus.INVALID
    assert result.candidate_decisions == prefix.candidate_decisions
    assert result.trades == prefix.trades
    assert result.equity_snapshots == prefix.equity_snapshots


def test_case_45_invalid_precedence_over_earlier_ambiguity() -> None:
    bar0 = _bar(0)
    malformed = replace(_bar(1), high_tick=90)
    result = _run(
        bars=(bar0, malformed),
        candidates=(
            _candidate(bar0, candidate_id=HASH_A),
            _candidate(bar0, candidate_id=HASH_B),
        ),
    )
    assert result.status is GCBacktestRunStatus.INVALID
    assert all(
        decision.status is GCCandidateDecisionStatus.REJECTED_AMBIGUOUS_GROUP
        for decision in result.candidate_decisions
    )


# Case 46
def test_case_46_complete_prefix_is_immutable_but_open_prefix_is_not_claimed() -> None:
    bar0 = _bar(0)
    bar1 = _bar(1, high_tick=111, low_tick=95)
    prefix = _run(bars=(bar0, bar1), candidates=(_candidate(bar0),))
    extended = _run(bars=(bar0, bar1, _bar(2)), candidates=(_candidate(bar0),))
    assert extended.candidate_decisions[: len(prefix.candidate_decisions)] == prefix.candidate_decisions
    assert extended.trades[: len(prefix.trades)] == prefix.trades
    assert extended.equity_snapshots[: len(prefix.equity_snapshots)] == prefix.equity_snapshots


# Case 47
def test_case_47_repeatability_is_byte_for_byte() -> None:
    assert _completed_buy_run() == _completed_buy_run()


# Case 48
def test_case_48_scope_and_import_surface_are_isolated() -> None:
    source_path = Path(gc_backtest.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imported & {"core.backtest_runner", "core.paper_trading_flow", "core.exit_simulator"} == set()
    smc_imports = {name for name in imported if name.startswith("smc")}
    assert smc_imports == {"smc.kill_zones"}
    assert Path("core/gc_chronological_backtest.py").exists()
    assert not Path("core/backtest_runner.py").read_text(encoding="utf-8").startswith("CHANGED")


def test_exact_48_logical_case_reconciliation() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    markers = [int(value) for value in __import__("re").findall(r"^# Case (\d+)$", source, __import__("re").MULTILINE)]
    assert markers == list(range(1, 49))


def test_public_type_hints_are_resolvable() -> None:
    for value in (
        GCChronologicalBar,
        GCBacktestCandidate,
        GCChronologicalBacktestConfig,
        GCCandidateDecision,
        GCBacktestTrade,
        GCEquitySnapshot,
        GCChronologicalBacktestResult,
        make_gc_chronological_backtest_id,
        run_gc_chronological_backtest,
    ):
        assert get_type_hints(value)
