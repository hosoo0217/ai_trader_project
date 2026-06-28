"""Unit tests for performance report generation."""

from storage.performance_report import PerformanceReporter
from storage.trade_journal import TradeJournal, TradeJournalEntry


def make_entry(
    trade_id: str,
    executed: bool,
    pnl: float | None,
) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id=trade_id,
        symbol="XAUUSD",
        action="BUY",
        executed=executed,
        entry_price=100.0,
        volume=1.0,
        stop_loss=95.0,
        take_profit=110.0,
        decision_confidence=80.0,
        reasons=["test"],
        blocking_reasons=[] if executed else ["blocked"],
        status="EXECUTED" if executed else "BLOCKED",
        pnl=pnl,
    )


def test_empty_journal_report() -> None:
    journal = TradeJournal()
    report = PerformanceReporter().generate_report(journal)

    assert report.total_trades == 0
    assert report.executed_trades == 0
    assert report.blocked_trades == 0
    assert report.wins == 0
    assert report.losses == 0
    assert report.breakeven == 0
    assert report.win_rate == 0.0
    assert report.total_pnl == 0.0


def test_winning_trade_counted() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 10.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.wins == 1
    assert report.losses == 0


def test_losing_trade_counted() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, -5.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.losses == 1
    assert report.wins == 0


def test_breakeven_trade_counted() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 0.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.breakeven == 1


def test_blocked_trade_counted() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", False, None))

    report = PerformanceReporter().generate_report(journal)

    assert report.blocked_trades == 1
    assert report.executed_trades == 0


def test_win_rate_calculation() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 10.0))
    journal.add_entry(make_entry("t2", True, -2.0))
    journal.add_entry(make_entry("t3", True, 0.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.win_rate == (1 / 3) * 100.0


def test_total_pnl_calculation() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 10.0))
    journal.add_entry(make_entry("t2", True, -2.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.total_pnl == 8.0


def test_profit_factor_calculation() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 10.0))
    journal.add_entry(make_entry("t2", True, -5.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.profit_factor == 2.0


def test_max_drawdown_calculation() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 5.0))
    journal.add_entry(make_entry("t2", True, -3.0))
    journal.add_entry(make_entry("t3", True, -4.0))

    report = PerformanceReporter().generate_report(journal)

    assert report.max_drawdown == 7.0


def test_explain_report_returns_readable_text() -> None:
    journal = TradeJournal()
    journal.add_entry(make_entry("t1", True, 10.0))

    reporter = PerformanceReporter()
    report = reporter.generate_report(journal)
    text = reporter.explain_report(report)

    assert "total trades" in text
    assert "win rate" in text
    assert "total pnl" in text
    assert "profit factor" in text
    assert "max drawdown" in text
