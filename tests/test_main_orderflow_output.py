"""Tests for Order Flow visibility in main.py output."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_demo_output_works_without_orderflow_data() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Order Flow Context" in output
    assert "- Status: Not provided" in output
    assert "Order Flow context not provided" in output


def test_output_includes_order_flow_text() -> None:
    output = _run_main("--mode", "demo", "--scenario", "weak")

    assert "Order Flow" in output
    assert "- Active: False" in output
    assert "- Bias: UNKNOWN" in output


def test_missing_orderflow_does_not_crash_backtest() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Backtest" in output
    assert "Order Flow Context" in output
    assert "Order Flow context not provided for this backtest run" in output


def test_existing_scenario_command_still_works() -> None:
    output = _run_main("--mode", "demo", "--scenario", "all", "--profile", "safe")

    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output


def test_show_orderflow_prints_detailed_fields() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-orderflow")

    assert "Order Flow Context" in output
    assert "- Order Flow checked:" in output
    assert "- Order Flow blocking reasons:" in output
