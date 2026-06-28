"""Simple trade journal for paper trading research.

This module stores trade decisions and outcomes in memory so they can be
reviewed later for experimentation and learning. It does not connect to a live
broker or any external service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TradeJournalEntry:
    """A single recorded decision or trade event."""

    trade_id: str
    symbol: str
    action: str
    executed: bool
    entry_price: Optional[float]
    volume: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    decision_confidence: float
    reasons: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    status: str = "RECORD"
    pnl: Optional[float] = None


class TradeJournal:
    """Store and summarize paper-trading decisions and outcomes."""

    def __init__(self) -> None:
        """Initialize an empty journal."""
        self._entries: List[TradeJournalEntry] = []

    def add_entry(self, entry: TradeJournalEntry) -> None:
        """Add a new entry to the journal."""
        self._entries.append(entry)

    def get_all_entries(self) -> List[TradeJournalEntry]:
        """Return all recorded entries."""
        return list(self._entries)

    def get_executed_trades(self) -> List[TradeJournalEntry]:
        """Return only entries that were executed."""
        return [entry for entry in self._entries if entry.executed]

    def get_blocked_trades(self) -> List[TradeJournalEntry]:
        """Return only entries that were blocked or rejected."""
        return [entry for entry in self._entries if not entry.executed]

    def summarize(self) -> Dict[str, float]:
        """Return a simple performance summary for the journal."""
        executed = self.get_executed_trades()
        blocked = self.get_blocked_trades()
        wins = sum(1 for entry in executed if entry.pnl is not None and entry.pnl > 0)
        losses = sum(1 for entry in executed if entry.pnl is not None and entry.pnl < 0)
        total_pnl = sum(float(entry.pnl or 0.0) for entry in executed)

        return {
            "total_entries": len(self._entries),
            "executed_trades": len(executed),
            "blocked_trades": len(blocked),
            "wins": wins,
            "losses": losses,
            "total_pnl": float(total_pnl),
        }

    def explain_summary(self) -> str:
        """Return a readable explanation of the current journal summary."""
        summary = self.summarize()
        return (
            "Trade journal summary: "
            f"total_entries={summary['total_entries']}, "
            f"executed_trades={summary['executed_trades']}, "
            f"blocked_trades={summary['blocked_trades']}, "
            f"wins={summary['wins']}, losses={summary['losses']}, "
            f"total_pnl={summary['total_pnl']:.2f}"
        )
