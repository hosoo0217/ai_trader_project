"""Unit tests for session history trend analysis."""

from __future__ import annotations

from storage.session_trend import SessionTrendAnalyzer, SessionTrendConfig


def _analyze(history, min_sessions: int = 3):
    return SessionTrendAnalyzer().analyze(history, SessionTrendConfig(min_sessions_for_trend=min_sessions))


def test_empty_history_returns_not_enough_data() -> None:
    result = _analyze([])

    assert result.trend_status == "NOT_ENOUGH_DATA"
    assert result.total_sessions == 0


def test_trend_counts_total_sessions() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": False, "market_bias": "BEARISH"},
        ],
        min_sessions=1,
    )

    assert result.total_sessions == 2


def test_trend_counts_executed_sessions() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": False, "market_bias": "BEARISH"},
        ],
        min_sessions=1,
    )

    assert result.executed_sessions == 2


def test_trend_counts_blocked_sessions() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": False, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
        ],
        min_sessions=1,
    )

    assert result.blocked_sessions == 2


def test_execution_rate_calculation() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": False, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
        ],
        min_sessions=1,
    )

    assert result.execution_rate == 50.0


def test_block_rate_calculation() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": False, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
            {"trade_executed": False, "market_bias": "UNKNOWN"},
        ],
        min_sessions=1,
    )

    assert result.block_rate == 75.0


def test_mostly_blocked_status() -> None:
    result = _analyze(
        [
            {"trade_executed": False, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
            {"trade_executed": False, "market_bias": "UNKNOWN"},
            {"trade_executed": True, "market_bias": "BULLISH"},
        ],
        min_sessions=3,
    )

    assert result.trend_status == "MOSTLY_BLOCKED"


def test_mostly_executed_status() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
        ],
        min_sessions=3,
    )

    assert result.trend_status == "MOSTLY_EXECUTED"


def test_mixed_status() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BEARISH"},
            {"trade_executed": False, "market_bias": "NEUTRAL"},
            {"trade_executed": False, "market_bias": "UNKNOWN"},
        ],
        min_sessions=3,
    )

    assert result.trend_status == "MIXED"


def test_most_common_blocking_reason() -> None:
    result = _analyze(
        [
            {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
            {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
            {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["News block"]},
        ],
        min_sessions=1,
    )

    assert result.most_common_blocking_reason == "Spread too high"
    assert result.blocking_reason_counts["Spread too high"] == 2


def test_invalid_history_item_does_not_crash() -> None:
    result = _analyze(
        [
            {"trade_executed": True, "market_bias": "BULLISH"},
            "bad item",
            None,
        ],
        min_sessions=1,
    )

    assert result.total_sessions == 1
    assert result.warnings == ["Ignored 2 invalid history item(s)"]


def test_explain_returns_readable_text() -> None:
    result = _analyze(
        [
            {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
            {"trade_executed": True, "market_bias": "BULLISH"},
            {"trade_executed": True, "market_bias": "BULLISH"},
        ],
        min_sessions=1,
    )

    text = SessionTrendAnalyzer().explain(result)

    assert "Session trend" in text
    assert "execution_rate=" in text
    assert "most_common_blocking_reason=Spread too high" in text
