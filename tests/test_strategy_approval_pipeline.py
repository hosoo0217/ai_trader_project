from __future__ import annotations

from ai.strategy_approval_pipeline import (
    StrategyApprovalPipeline,
    StrategyApprovalPipelineConfig,
)
from ai.strategy_improvement import StrategyImprovementResult, StrategyImprovementSuggestion


def _suggestion(priority: str = "HIGH") -> StrategyImprovementSuggestion:
    return StrategyImprovementSuggestion(
        category="RISK_MANAGEMENT",
        priority=priority,
        suggestion="Review drawdown and risk reports before changing any strategy rule.",
        reason="Risk review protects strategy research from weak pass-rate assumptions.",
        risk="Changing rules without review can expose capital to poor conditions.",
        human_approval_required=True,
    )


def _improvement_result(*suggestions: StrategyImprovementSuggestion) -> StrategyImprovementResult:
    return StrategyImprovementResult(
        status="HAS_SUGGESTIONS" if suggestions else "NO_SUGGESTIONS",
        suggestions=list(suggestions),
        summary="Strategy improvement result for tests",
        reasons=["Suggestions are research notes"],
    )


def test_creates_approval_requests_from_strategy_suggestions() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(_suggestion("HIGH"), _suggestion("MEDIUM")),
        StrategyApprovalPipelineConfig(),
    )

    assert result.status == "REQUESTS_CREATED"
    assert len(result.created_requests) == 2
    assert result.created_requests[0].suggestion_category == "RISK_MANAGEMENT"
    assert result.created_requests[0].human_approval_required is True


def test_all_requests_start_as_pending() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(_suggestion("HIGH"), _suggestion("MEDIUM")),
        StrategyApprovalPipelineConfig(),
    )

    assert all(request.status == "PENDING" for request in result.created_requests)


def test_total_suggestions_count_is_correct() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(_suggestion("HIGH"), _suggestion("MEDIUM"), _suggestion("LOW")),
        StrategyApprovalPipelineConfig(),
    )

    assert result.total_suggestions == 3


def test_pending_requests_count_is_correct() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(_suggestion("HIGH"), _suggestion("MEDIUM")),
        StrategyApprovalPipelineConfig(),
    )

    assert result.pending_requests == 2


def test_no_suggestions_returns_no_suggestions() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(),
        StrategyApprovalPipelineConfig(),
    )

    assert result.status == "NO_SUGGESTIONS"
    assert result.created_requests == []
    assert result.pending_requests == 0


def test_missing_improvement_result_returns_unknown_safely() -> None:
    result = StrategyApprovalPipeline().create_requests(None, StrategyApprovalPipelineConfig())

    assert result.status == "UNKNOWN"
    assert result.created_requests == []
    assert result.pending_requests == 0
    assert result.blocking_reasons


def test_low_priority_suggestions_can_be_skipped() -> None:
    result = StrategyApprovalPipeline().create_requests(
        _improvement_result(_suggestion("HIGH"), _suggestion("LOW")),
        StrategyApprovalPipelineConfig(include_low_priority_suggestions=False),
    )

    assert result.status == "REQUESTS_CREATED"
    assert result.total_suggestions == 2
    assert len(result.created_requests) == 1
    assert len(result.skipped_suggestions) == 1
    assert any("LOW priority" in reason for reason in result.blocking_reasons)


def test_allow_auto_apply_stays_false_by_default() -> None:
    config = StrategyApprovalPipelineConfig()

    assert config.allow_auto_apply is False


def test_explain_returns_readable_text() -> None:
    pipeline = StrategyApprovalPipeline()
    result = pipeline.create_requests(_improvement_result(_suggestion()), StrategyApprovalPipelineConfig())

    text = pipeline.explain(result)

    assert "Strategy approval pipeline status:" in text
    assert "PENDING human approval requests" in text
    assert "does not apply strategy changes" in text


def test_output_does_not_contain_direct_trade_commands() -> None:
    pipeline = StrategyApprovalPipeline()
    result = pipeline.create_requests(_improvement_result(_suggestion()), StrategyApprovalPipelineConfig())
    text = pipeline.explain(result).lower()

    forbidden = ["buy now", "sell now", "enter trade", "open position", "guaranteed signal"]
    assert all(phrase not in text for phrase in forbidden)
