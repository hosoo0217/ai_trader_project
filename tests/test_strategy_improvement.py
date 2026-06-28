from ai.session_trend_coach import SessionTrendCoachReview
from ai.strategy_improvement import (
    StrategyImprovementConfig,
    StrategyImprovementEngine,
)
from storage.session_trend import SessionTrendResult


def _trend(
    *,
    trend_status: str = "MIXED",
    total_sessions: int = 5,
    execution_rate: float = 40.0,
    block_rate: float = 60.0,
    most_common_blocking_reason: str | None = None,
) -> SessionTrendResult:
    return SessionTrendResult(
        total_sessions=total_sessions,
        executed_sessions=int(total_sessions * execution_rate / 100.0),
        blocked_sessions=int(total_sessions * block_rate / 100.0),
        execution_rate=execution_rate,
        block_rate=block_rate,
        bullish_sessions=0,
        bearish_sessions=0,
        neutral_sessions=0,
        unknown_sessions=total_sessions,
        most_common_blocking_reason=most_common_blocking_reason,
        blocking_reason_counts={most_common_blocking_reason: 2} if most_common_blocking_reason else {},
        trend_status=trend_status,
        reasons=["Trend analyzed"],
        warnings=[],
    )


def _coach() -> SessionTrendCoachReview:
    return SessionTrendCoachReview(
        status="MIXED_TREND",
        grade="C",
        summary="Coach summary",
        trend_read="Mixed behavior",
        warnings=[],
        reasons=["Coach reviewed trend"],
    )


def test_missing_trend_result_returns_unknown_safely():
    result = StrategyImprovementEngine().suggest(None, _coach(), StrategyImprovementConfig())

    assert result.status == "UNKNOWN"
    assert result.suggestions == []
    assert result.warnings


def test_not_enough_data_creates_save_more_history_suggestion():
    result = StrategyImprovementEngine().suggest(
        _trend(trend_status="NOT_ENOUGH_DATA", total_sessions=1),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert result.status == "NOT_ENOUGH_DATA"
    assert any("more session history" in suggestion.suggestion.lower() for suggestion in result.suggestions)


def test_high_block_rate_creates_high_priority_suggestion():
    result = StrategyImprovementEngine().suggest(
        _trend(trend_status="MOSTLY_BLOCKED", block_rate=80.0, execution_rate=20.0),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert result.status == "HAS_SUGGESTIONS"
    assert any(suggestion.priority == "HIGH" for suggestion in result.suggestions)


def test_session_blocking_reason_creates_session_filter_suggestion():
    result = StrategyImprovementEngine().suggest(
        _trend(
            trend_status="MOSTLY_BLOCKED",
            block_rate=80.0,
            most_common_blocking_reason="SESSION filter blocked weekend data",
        ),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert any(suggestion.category == "SESSION_FILTER" for suggestion in result.suggestions)


def test_smc_blocking_reason_creates_smc_suggestion():
    result = StrategyImprovementEngine().suggest(
        _trend(
            trend_status="MOSTLY_BLOCKED",
            block_rate=80.0,
            most_common_blocking_reason="SMC bias was unknown",
        ),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert any(suggestion.category == "SMC" for suggestion in result.suggestions)


def test_order_flow_blocking_reason_creates_order_flow_suggestion():
    result = StrategyImprovementEngine().suggest(
        _trend(
            trend_status="MOSTLY_BLOCKED",
            block_rate=80.0,
            most_common_blocking_reason="ORDER_FLOW alignment conflict",
        ),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert any(suggestion.category == "ORDER_FLOW" for suggestion in result.suggestions)


def test_high_execution_rate_creates_risk_warning():
    result = StrategyImprovementEngine().suggest(
        _trend(trend_status="MOSTLY_EXECUTED", execution_rate=80.0, block_rate=20.0),
        _coach(),
        StrategyImprovementConfig(),
    )

    assert any("does not automatically mean" in warning for warning in result.warnings)
    assert any(suggestion.category == "RISK_MANAGEMENT" for suggestion in result.suggestions)


def test_all_suggestions_require_human_approval():
    result = StrategyImprovementEngine().suggest(
        _trend(trend_status="MOSTLY_BLOCKED", block_rate=80.0),
        _coach(),
        StrategyImprovementConfig(require_human_approval=False),
    )

    assert result.suggestions
    assert all(suggestion.human_approval_required for suggestion in result.suggestions)


def test_explain_returns_readable_text():
    engine = StrategyImprovementEngine()
    result = engine.suggest(
        _trend(trend_status="MOSTLY_BLOCKED", block_rate=80.0),
        _coach(),
        StrategyImprovementConfig(),
    )

    text = engine.explain(result)

    assert "Status:" in text
    assert "Suggestions:" in text


def test_output_does_not_contain_direct_trade_commands():
    engine = StrategyImprovementEngine()
    result = engine.suggest(
        _trend(trend_status="MOSTLY_BLOCKED", block_rate=80.0),
        _coach(),
        StrategyImprovementConfig(),
    )
    text = engine.explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
