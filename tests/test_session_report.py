"""Unit tests for full trading session reports."""

from __future__ import annotations

from types import SimpleNamespace

from core.paper_trading_flow import PaperTradingFlowResult
from storage.session_report import TradingSessionReportGenerator


def test_report_is_created_from_normal_paper_flow_result() -> None:
    flow_result = PaperTradingFlowResult(
        completed=True,
        status="NO_TRADE",
        market_bias="BULLISH",
        decision_action="NO_TRADE",
        trade_executed=False,
        reasons=["Flow completed"],
        safety_status="PASSED",
        safety_allowed=True,
    )

    report = TradingSessionReportGenerator().generate_from_flow_result(
        flow_result,
        mode="demo",
        scenario="bullish",
        profile="apex",
    )

    assert report.mode == "demo"
    assert report.scenario == "bullish"
    assert report.profile == "apex"
    assert report.final_action == "NO_TRADE"
    assert report.market_bias == "BULLISH"


def test_blocked_trade_report_includes_blocking_reasons() -> None:
    flow_result = PaperTradingFlowResult(
        decision_action="NO_TRADE",
        trade_executed=False,
        safety_status="BLOCKED",
        safety_allowed=False,
        safety_blocking_reasons=["Daily loss limit hit"],
        risk_blocking_reasons=["Risk plan invalid"],
    )

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert "Daily loss limit hit" in report.blocked_reasons
    assert "Risk plan invalid" in report.blocked_reasons


def test_executed_trade_report_marks_trade_executed_true_if_available() -> None:
    flow_result = PaperTradingFlowResult(
        status="EXECUTED",
        market_bias="BULLISH",
        decision_action="BUY",
        trade_executed=True,
        safety_status="PASSED",
        safety_allowed=True,
    )

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.trade_executed is True
    assert report.final_action == "BUY"


def test_missing_orderflow_does_not_crash() -> None:
    flow_result = PaperTradingFlowResult(orderflow_bias=None)

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.orderflow_bias is None
    assert "Order Flow bias was not available" in report.warnings


def test_missing_smc_crt_does_not_crash() -> None:
    flow_result = PaperTradingFlowResult(smc_bias=None, crt_bias=None)

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.smc_bias is None
    assert report.crt_bias is None
    assert "SMC bias was not available" in report.warnings
    assert "CRT bias was not available" in report.warnings


def test_safety_status_appears_in_report() -> None:
    flow_result = PaperTradingFlowResult(safety_status="PASSED", safety_allowed=True)

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.safety_status == "PASSED"
    assert report.safety_passed is True


def test_decision_trace_id_appears_when_available() -> None:
    flow_result = PaperTradingFlowResult(trace_id="trace-123")

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.decision_trace_id == "trace-123"
    assert report.session_id == "trace-123"


def test_attached_journal_performance_and_ai_coach_are_included() -> None:
    flow_result = SimpleNamespace(
        decision_action="BUY",
        trade_executed=True,
        market_bias="BULLISH",
        smc_bias="BULLISH",
        crt_bias="BULLISH",
        orderflow_bias="BULLISH",
        safety_status="PASSED",
        safety_allowed=True,
        reasons=["Executed"],
        journal_summary={"total_entries": 1, "executed_trades": 1},
        performance_summary={"total_pnl": 25.0},
        ai_coach_summary="Good paper-trading discipline.",
    )

    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    assert report.journal_summary["total_entries"] == 1
    assert report.performance_summary["total_pnl"] == 25.0
    assert report.ai_coach_summary == "Good paper-trading discipline."


def test_explain_returns_readable_text() -> None:
    flow_result = PaperTradingFlowResult(
        decision_action="SELL",
        trade_executed=False,
        market_bias="BEARISH",
        safety_status="BLOCKED",
        safety_allowed=False,
        safety_blocking_reasons=["Spread too high"],
    )
    report = TradingSessionReportGenerator().generate_from_flow_result(flow_result)

    text = TradingSessionReportGenerator().explain(report)

    assert "Trading session report" in text
    assert "final_action=SELL" in text
    assert "Spread too high" in text


def test_missing_flow_result_returns_safe_unknown_style_report() -> None:
    report = TradingSessionReportGenerator().generate_from_flow_result(
        None,
        mode="demo",
        scenario="weak",
        profile="safe",
    )

    assert report.final_action == "UNKNOWN"
    assert report.trade_executed is False
    assert report.market_bias == "UNKNOWN"
    assert report.safety_passed is False
    assert "No flow result provided" in report.blocked_reasons
