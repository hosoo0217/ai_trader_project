"""Unit tests for the AI Coach session trend review."""

from __future__ import annotations

from ai.session_trend_coach import SessionTrendCoach, SessionTrendCoachConfig
from storage.session_trend import SessionTrendResult


def _trend(
    total_sessions: int = 5,
    executed_sessions: int = 2,
    blocked_sessions: int = 3,
    execution_rate: float = 40.0,
    block_rate: float = 60.0,
    trend_status: str = "MIXED",
    most_common_blocking_reason: str | None = None,
    warnings: list[str] | None = None,
) -> SessionTrendResult:
    return SessionTrendResult(
        total_sessions=total_sessions,
        executed_sessions=executed_sessions,
        blocked_sessions=blocked_sessions,
        execution_rate=execution_rate,
        block_rate=block_rate,
        bullish_sessions=1,
        bearish_sessions=1,
        neutral_sessions=1,
        unknown_sessions=0,
        most_common_blocking_reason=most_common_blocking_reason,
        blocking_reason_counts={most_common_blocking_reason: blocked_sessions} if most_common_blocking_reason else {},
        trend_status=trend_status,
        reasons=["Trend analyzed"],
        warnings=warnings or [],
    )


def test_not_enough_data_creates_not_enough_data_review() -> None:
    review = SessionTrendCoach().review(
        _trend(total_sessions=1, executed_sessions=1, blocked_sessions=0, execution_rate=100.0, block_rate=0.0, trend_status="NOT_ENOUGH_DATA"),
        SessionTrendCoachConfig(),
    )

    assert review.status == "NOT_ENOUGH_DATA"
    assert review.grade in {"D", "F"}
    assert "More saved sessions" in review.trend_read


def test_mostly_blocked_trend_creates_blocked_coach_review() -> None:
    review = SessionTrendCoach().review(
        _trend(executed_sessions=1, blocked_sessions=4, execution_rate=20.0, block_rate=80.0, trend_status="MOSTLY_BLOCKED"),
        SessionTrendCoachConfig(),
    )

    assert review.status == "MOSTLY_BLOCKED"
    assert "conservative" in review.trend_read
    assert any("Blocked trades are useful" in lesson for lesson in review.lessons)


def test_mostly_executed_trend_creates_executed_coach_review() -> None:
    review = SessionTrendCoach().review(
        _trend(executed_sessions=4, blocked_sessions=1, execution_rate=80.0, block_rate=20.0, trend_status="MOSTLY_EXECUTED"),
        SessionTrendCoachConfig(),
    )

    assert review.status == "MOSTLY_EXECUTED"
    assert "passing filters" in review.trend_read


def test_mixed_trend_creates_mixed_coach_review() -> None:
    review = SessionTrendCoach().review(_trend(trend_status="MIXED"), SessionTrendCoachConfig())

    assert review.status == "MIXED_TREND"
    assert "mixed behavior" in review.trend_read


def test_high_block_rate_creates_warning() -> None:
    review = SessionTrendCoach().review(
        _trend(executed_sessions=1, blocked_sessions=4, execution_rate=20.0, block_rate=80.0, trend_status="MOSTLY_BLOCKED"),
        SessionTrendCoachConfig(),
    )

    assert "High block rate means common blocking reasons should be reviewed" in review.warnings
    assert "Many sessions are being blocked" in review.risks


def test_high_execution_rate_creates_strength_and_warning() -> None:
    review = SessionTrendCoach().review(
        _trend(executed_sessions=4, blocked_sessions=1, execution_rate=80.0, block_rate=20.0, trend_status="MOSTLY_EXECUTED"),
        SessionTrendCoachConfig(),
    )

    assert "Many sessions are passing filters" in review.strengths
    assert "High execution rate alone does not prove profitability" in review.warnings


def test_common_blocking_reason_appears_in_review() -> None:
    review = SessionTrendCoach().review(
        _trend(
            executed_sessions=1,
            blocked_sessions=4,
            execution_rate=20.0,
            block_rate=80.0,
            trend_status="MOSTLY_BLOCKED",
            most_common_blocking_reason="Spread too high",
        ),
        SessionTrendCoachConfig(),
    )

    assert "Spread too high" in review.trend_read
    assert "Most common blocking reason: Spread too high" in review.risks


def test_missing_trend_result_does_not_crash() -> None:
    review = SessionTrendCoach().review(None, SessionTrendCoachConfig())

    assert review.status == "UNKNOWN"
    assert review.grade == "F"
    assert "No usable session trend data" in review.summary


def test_explain_returns_readable_text() -> None:
    review = SessionTrendCoach().review(_trend(), SessionTrendCoachConfig())

    text = SessionTrendCoach().explain(review)

    assert "Status:" in text
    assert "Grade:" in text
    assert "Trend read:" in text


def test_review_does_not_contain_direct_trade_commands() -> None:
    review = SessionTrendCoach().review(
        _trend(executed_sessions=4, blocked_sessions=1, execution_rate=80.0, block_rate=20.0, trend_status="MOSTLY_EXECUTED"),
        SessionTrendCoachConfig(),
    )
    text = SessionTrendCoach().explain(review).lower()

    forbidden_phrases = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    for phrase in forbidden_phrases:
        assert phrase not in text
