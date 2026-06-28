"""Rule-based trade review and coaching for paper trading research.

This module turns journal entries into simple educational summaries. It does
not use external AI APIs or connect to any broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from storage.trade_journal import TradeJournal, TradeJournalEntry


@dataclass
class TradeReview:
    """A beginner-friendly review of a single trade decision."""

    trade_id: str
    summary: str
    grade: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    lesson: str = ""
    risk_notes: List[str] = field(default_factory=list)


class TradeReviewer:
    """Build simple rule-based trade feedback from the journal."""

    def review_entry(self, entry: TradeJournalEntry) -> TradeReview:
        """Create a review for one journal entry."""
        if entry.executed:
            confidence_text = self._confidence_note(entry.decision_confidence)
            strengths = list(entry.reasons) if entry.reasons else []
            weaknesses: List[str] = []
            risk_notes: List[str] = []

            if entry.blocking_reasons:
                weaknesses.extend(entry.blocking_reasons)
                risk_notes.extend(entry.blocking_reasons)

            if entry.pnl is None:
                summary = (
                    f"Trade {entry.trade_id} was executed with {confidence_text}. "
                    "The position is still open or has not been fully evaluated yet."
                )
            else:
                summary = (
                    f"Trade {entry.trade_id} was executed with {confidence_text}. "
                    f"The trade closed with PnL {entry.pnl:.2f}."
                )

            grade = self._grade_executed_trade(entry, weaknesses)
            lesson = self._lesson_for_executed_trade(entry, grade)
            return TradeReview(
                trade_id=entry.trade_id,
                summary=summary,
                grade=grade,
                strengths=strengths,
                weaknesses=weaknesses,
                lesson=lesson,
                risk_notes=risk_notes,
            )

        summary = (
            f"Trade {entry.trade_id} was not executed. "
            "No trade was taken because the setup did not pass the rules."
        )
        weaknesses = list(entry.blocking_reasons) if entry.blocking_reasons else ["No blocking reason recorded"]
        lesson = "No trade was the correct decision because risk filters blocked the setup."
        return TradeReview(
            trade_id=entry.trade_id,
            summary=summary,
            grade="NO_TRADE",
            strengths=[],
            weaknesses=weaknesses,
            lesson=lesson,
            risk_notes=list(entry.blocking_reasons),
        )

    def review_journal(self, journal: TradeJournal) -> List[TradeReview]:
        """Create a review for every entry in the journal."""
        return [self.review_entry(entry) for entry in journal.get_all_entries()]

    def explain_review(self, review: TradeReview) -> str:
        """Return a readable explanation for a trade review."""
        lines = [f"Trade ID: {review.trade_id}", f"Grade: {review.grade}", f"Summary: {review.summary}"]
        if review.strengths:
            lines.append("Strengths: " + "; ".join(review.strengths))
        if review.weaknesses:
            lines.append("Weaknesses: " + "; ".join(review.weaknesses))
        if review.risk_notes:
            lines.append("Risk notes: " + "; ".join(review.risk_notes))
        lines.append(f"Lesson: {review.lesson}")
        return "\n".join(lines)

    def _confidence_note(self, confidence: float) -> str:
        """Turn a numeric confidence into a plain-language note."""
        if confidence >= 85:
            return "strong confidence"
        if confidence >= 70:
            return "acceptable confidence"
        return "weak confidence"

    def _grade_executed_trade(self, entry: TradeJournalEntry, weaknesses: List[str]) -> str:
        """Assign a grade using the simple project rules."""
        if entry.decision_confidence >= 85 and not entry.blocking_reasons:
            return "A"
        if entry.decision_confidence >= 70 and not entry.blocking_reasons:
            return "B"
        return "C"

    def _lesson_for_executed_trade(self, entry: TradeJournalEntry, grade: str) -> str:
        """Create a short educational lesson."""
        if grade == "A":
            return "Good trade quality. Continue waiting for aligned conditions."
        if grade == "B":
            return "Good trade quality. Continue waiting for aligned conditions."
        if entry.decision_confidence < 70:
            return "Confidence was too low. Wait for stronger confirmation."
        return "Good trade quality. Continue waiting for aligned conditions."
