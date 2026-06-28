"""Simple performance reporting for paper-trading journal entries.

This module computes beginner-friendly performance metrics from in-memory
journal entries. It is for paper trading and backtesting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from storage.trade_journal import TradeJournal


@dataclass
class PerformanceReport:
    """Aggregated performance metrics for journaled trades."""

    total_trades: int
    executed_trades: int
    blocked_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    profit_factor: float
    best_trade: float | None
    worst_trade: float | None
    max_drawdown: float
    notes: list[str] = field(default_factory=list)


class PerformanceReporter:
    """Generate simple deterministic performance reports from a trade journal."""

    def generate_report(self, journal: TradeJournal) -> PerformanceReport:
        """Compute all report fields from journal entries."""
        entries = journal.get_all_entries()
        executed = [entry for entry in entries if entry.executed]
        blocked = [entry for entry in entries if not entry.executed]
        realized = [entry for entry in executed if entry.pnl is not None]

        pnls = [float(entry.pnl) for entry in realized]
        wins_list = [value for value in pnls if value > 0]
        losses_list = [value for value in pnls if value < 0]
        breakeven_list = [value for value in pnls if value == 0]

        wins = len(wins_list)
        losses = len(losses_list)
        breakeven = len(breakeven_list)

        win_rate = (wins / len(realized) * 100.0) if realized else 0.0
        total_pnl = float(sum(pnls))
        average_win = float(sum(wins_list) / wins) if wins else 0.0
        average_loss = float(sum(losses_list) / losses) if losses else 0.0

        gross_profit = float(sum(wins_list))
        gross_loss_abs = float(abs(sum(losses_list)))
        if gross_loss_abs == 0.0:
            profit_factor = float("inf") if gross_profit > 0.0 else 0.0
        else:
            profit_factor = float(gross_profit / gross_loss_abs)

        best_trade = max(pnls) if pnls else None
        worst_trade = min(pnls) if pnls else None
        max_drawdown = self._compute_max_drawdown(pnls)

        notes = self._build_notes(realized_count=len(realized), total_pnl=total_pnl, win_rate=win_rate)

        return PerformanceReport(
            total_trades=len(entries),
            executed_trades=len(executed),
            blocked_trades=len(blocked),
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate=float(win_rate),
            total_pnl=total_pnl,
            average_win=average_win,
            average_loss=average_loss,
            profit_factor=profit_factor,
            best_trade=best_trade,
            worst_trade=worst_trade,
            max_drawdown=max_drawdown,
            notes=notes,
        )

    def explain_report(self, report: PerformanceReport) -> str:
        """Return a readable text summary of the performance report."""
        profit_factor_text = "INF" if report.profit_factor == float("inf") else f"{report.profit_factor:.2f}"
        notes_text = " ".join(report.notes) if report.notes else "No notes"

        return (
            f"Performance report | total trades: {report.total_trades} | "
            f"executed: {report.executed_trades} | blocked: {report.blocked_trades} | "
            f"win rate: {report.win_rate:.2f}% | total pnl: {report.total_pnl:.2f} | "
            f"profit factor: {profit_factor_text} | max drawdown: {report.max_drawdown:.2f} | "
            f"note: {notes_text}"
        )

    def _compute_max_drawdown(self, pnls: list[float]) -> float:
        """Compute max drawdown from a cumulative pnl curve."""
        if not pnls:
            return 0.0

        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0

        for pnl in pnls:
            equity += pnl
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return float(max_drawdown)

    def _build_notes(self, realized_count: int, total_pnl: float, win_rate: float) -> list[str]:
        """Create simple coaching notes for report interpretation."""
        if realized_count == 0:
            return ["No closed trades yet. More testing is needed before judging performance."]

        if total_pnl > 0 and win_rate >= 50.0:
            return ["Performance looks promising, but continue testing for stability."]

        return ["Performance needs more testing and refinement before stronger conclusions."]
