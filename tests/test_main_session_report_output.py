"""Tests for Full Trading Session Report output in main.py."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_main_prints_full_trading_session_report() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Session ID:" in output
    assert "- Mode: demo" in output


def test_blocked_trade_report_includes_blocking_reasons() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--spread",
        "10.0",
        "--show-session-report",
    )

    assert "Full Trading Session Report" in output
    assert "- Blocked reasons:" in output
    assert "spread" in output.lower()


def test_session_report_output_includes_final_action() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bearish", "--profile", "apex", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Final action:" in output


def test_session_report_output_includes_safety_status() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Safety status:" in output
    assert "- Safety passed:" in output


def test_session_report_wording_is_present() -> None:
    output = _run_main("--mode", "demo", "--scenario", "weak", "--profile", "safe", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Journal summary:" in output
    assert "- Performance summary:" in output
    assert "- AI Coach summary:" in output


def test_missing_orderflow_does_not_crash_session_report() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Order Flow bias:" in output
    assert "Order Flow bias was not available" in output or "UNKNOWN" in output


def test_existing_main_command_still_works_without_session_report() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Market result" in output
    assert "Full Trading Session Report" not in output


def test_backtest_can_print_session_report() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex", "--show-session-report")

    assert "Full Trading Session Report" in output
    assert "- Mode: backtest" in output
    assert "- Final action: BACKTEST" in output
