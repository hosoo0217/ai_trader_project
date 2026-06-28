"""Unit tests for the trade journal."""

from storage.trade_journal import TradeJournal, TradeJournalEntry


def make_entry(**overrides):
    """Create a simple journal entry with optional overrides."""
    entry = TradeJournalEntry(
        trade_id="trade-1",
        symbol="XAUUSD",
        action="BUY",
        executed=True,
        entry_price=100.0,
        volume=1.0,
        stop_loss=95.0,
        take_profit=105.0,
        decision_confidence=80.0,
        reasons=["Bullish"],
        blocking_reasons=[],
        status="EXECUTED",
        pnl=10.0,
    )
    for key, value in overrides.items():
        setattr(entry, key, value)
    return entry


def test_empty_journal_summary():
    """An empty journal should return safe zeroed values."""
    journal = TradeJournal()

    summary = journal.summarize()

    assert summary == {
        "total_entries": 0,
        "executed_trades": 0,
        "blocked_trades": 0,
        "wins": 0,
        "losses": 0,
        "total_pnl": 0.0,
    }


def test_add_entry():
    """Adding an entry should store it in the journal."""
    journal = TradeJournal()
    entry = make_entry()

    journal.add_entry(entry)

    assert journal.get_all_entries() == [entry]


def test_get_executed_trades():
    """The journal should return only executed trades."""
    journal = TradeJournal()
    journal.add_entry(make_entry(executed=True))
    journal.add_entry(make_entry(trade_id="trade-2", executed=False, status="BLOCKED"))

    executed = journal.get_executed_trades()

    assert len(executed) == 1
    assert executed[0].trade_id == "trade-1"


def test_get_blocked_trades():
    """The journal should return only blocked trades."""
    journal = TradeJournal()
    journal.add_entry(make_entry(executed=True))
    journal.add_entry(make_entry(trade_id="trade-2", executed=False, status="BLOCKED"))

    blocked = journal.get_blocked_trades()

    assert len(blocked) == 1
    assert blocked[0].trade_id == "trade-2"


def test_winning_trade_counted_correctly():
    """A positive PnL should count as a win."""
    journal = TradeJournal()
    journal.add_entry(make_entry(pnl=25.0))

    summary = journal.summarize()

    assert summary["wins"] == 1
    assert summary["losses"] == 0


def test_losing_trade_counted_correctly():
    """A negative PnL should count as a loss."""
    journal = TradeJournal()
    journal.add_entry(make_entry(pnl=-15.0))

    summary = journal.summarize()

    assert summary["losses"] == 1
    assert summary["wins"] == 0


def test_total_pnl_calculated_correctly():
    """The summary should total all trade PnL values."""
    journal = TradeJournal()
    journal.add_entry(make_entry(pnl=10.0))
    journal.add_entry(make_entry(trade_id="trade-2", pnl=-5.0))

    summary = journal.summarize()

    assert summary["total_pnl"] == 5.0


def test_explain_summary_returns_readable_text():
    """The explanation helper should return a readable summary."""
    journal = TradeJournal()
    journal.add_entry(make_entry(pnl=12.0))

    explanation = journal.explain_summary()

    assert "Trade journal summary" in explanation
    assert "total_entries" in explanation
    assert "total_pnl" in explanation
