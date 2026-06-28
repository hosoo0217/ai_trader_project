"""Unit tests for the Order Flow replay AI Coach."""

from __future__ import annotations

from ai.orderflow_replay_coach import OrderFlowReplayCoach, OrderFlowReplayCoachConfig
from orderflow.replay_report import OrderFlowReplayReport


def _report(
    total_steps: int = 3,
    bullish_steps: int = 3,
    bearish_steps: int = 0,
    neutral_steps: int = 0,
    unknown_steps: int = 0,
    average_confidence: float = 75.0,
    final_bias: str = "BULLISH",
    final_cvd: float = 120.0,
    dominant_bias: str = "BULLISH",
    warnings: list[str] | None = None,
) -> OrderFlowReplayReport:
    return OrderFlowReplayReport(
        total_steps=total_steps,
        bullish_steps=bullish_steps,
        bearish_steps=bearish_steps,
        neutral_steps=neutral_steps,
        unknown_steps=unknown_steps,
        average_confidence=average_confidence,
        max_confidence=average_confidence,
        min_confidence=average_confidence,
        final_bias=final_bias,
        final_confidence=average_confidence,
        final_cvd=final_cvd,
        dominant_bias=dominant_bias,
        reasons=["Replay report generated"],
        warnings=warnings or [],
    )


def test_bullish_replay_report_produces_bullish_coach_review() -> None:
    review = OrderFlowReplayCoach().review(_report(), OrderFlowReplayCoachConfig())

    assert review.status == "STRONG_ORDERFLOW"
    assert review.grade == "A"
    assert "buyers were more aggressive" in review.market_read.lower()
    assert "Order Flow supports bullish context" in review.strengths


def test_bearish_replay_report_produces_bearish_coach_review() -> None:
    report = _report(
        bullish_steps=0,
        bearish_steps=3,
        final_bias="BEARISH",
        final_cvd=-150.0,
        dominant_bias="BEARISH",
    )

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert review.status == "STRONG_ORDERFLOW"
    assert review.grade == "A"
    assert "sellers were more aggressive" in review.market_read.lower()
    assert "Order Flow supports bearish context" in review.strengths


def test_neutral_mixed_report_produces_mixed_review() -> None:
    report = _report(
        bullish_steps=1,
        bearish_steps=1,
        neutral_steps=1,
        average_confidence=55.0,
        final_bias="NEUTRAL",
        final_cvd=0.0,
        dominant_bias="UNKNOWN",
    )

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert review.status == "MIXED_ORDERFLOW"
    assert review.grade == "C"
    assert "unclear or mixed" in review.market_read.lower()


def test_empty_report_produces_no_usable_orderflow() -> None:
    report = _report(total_steps=0, bullish_steps=0, average_confidence=0.0, dominant_bias="UNKNOWN")

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert review.status == "NO_USABLE_ORDERFLOW"
    assert review.grade == "F"
    assert "no useful replay data" in review.summary.lower() or "no usable" in review.summary.lower()


def test_low_confidence_creates_warning() -> None:
    report = _report(average_confidence=25.0)

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert review.grade == "D"
    assert any("Low average confidence" in warning for warning in review.warnings)
    assert "Average Order Flow confidence is low" in review.risks


def test_high_confidence_creates_stronger_grade() -> None:
    report = _report(average_confidence=85.0)

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert review.grade == "A"
    assert "Average Order Flow confidence is strong" in review.strengths


def test_warnings_from_report_are_preserved() -> None:
    report = _report(warnings=["CSV had minor warnings"])

    review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    assert "CSV had minor warnings" in review.warnings
    assert "CSV had minor warnings" in review.risks


def test_explain_returns_readable_text() -> None:
    review = OrderFlowReplayCoach().review(_report(), OrderFlowReplayCoachConfig())

    text = OrderFlowReplayCoach().explain(review)

    assert "Status:" in text
    assert "Grade:" in text
    assert "Market read:" in text
    assert "SMC" in text
