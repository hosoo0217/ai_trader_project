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


def test_sample_bullish_csv_produces_active_orderflow() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        "data/sample_footprint_bullish.csv",
    )

    assert "Order Flow Context" in output
    assert "- Active: True" in output
    assert "- Bias: BULLISH" in output
    assert "Order Flow Data Quality" in output
    assert "- Status: PASSED" in output or "- Status: WARNING" in output
    assert "- Passed: True" in output
    assert "- Delta direction: BUYING_PRESSURE" in output
    assert "- Imbalance bias: BULLISH" in output
    assert "- Final CVD:" in output


def test_sample_bearish_csv_produces_active_orderflow() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bearish",
        "--profile",
        "apex",
        "--orderflow-csv",
        "data/sample_footprint_bearish.csv",
    )

    assert "Order Flow Context" in output
    assert "- Active: True" in output
    assert "- Bias: BEARISH" in output
    assert "Order Flow Data Quality" in output
    assert "- Status: PASSED" in output or "- Status: WARNING" in output
    assert "- Passed: True" in output
    assert "- Delta direction: SELLING_PRESSURE" in output
    assert "- Imbalance bias: BEARISH" in output


def test_missing_orderflow_csv_path_does_not_crash() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        "data/does_not_exist.csv",
    )

    assert "Order Flow Context" in output
    assert "- Active: False" in output
    assert "Order Flow CSV not found" in output
    assert "Order Flow Data Quality" in output
    assert "- Status: INVALID" in output
    assert "- Passed: False" in output


def test_invalid_orderflow_csv_does_not_crash(tmp_path) -> None:
    invalid_csv = tmp_path / "invalid_footprint.csv"
    invalid_csv.write_text("not,a,footprint\n1,2,3\n", encoding="utf-8")

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        str(invalid_csv),
    )

    assert "Order Flow Context" in output
    assert "- Active: False" in output
    assert "Order Flow CSV could not be imported" in output
    assert "Order Flow Data Quality" in output
    assert "- Status: EMPTY" in output
    assert "- Passed: False" in output


def test_empty_orderflow_csv_blocks_context(tmp_path) -> None:
    empty_csv = tmp_path / "empty_footprint.csv"
    empty_csv.write_text("time,open,high,low,close,price,bid_volume,ask_volume\n", encoding="utf-8")

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        str(empty_csv),
    )

    assert "Order Flow Context" in output
    assert "- Active: False" in output
    assert "Order Flow Data Quality" in output
    assert "- Status: EMPTY" in output
    assert "- Passed: False" in output


def test_decision_trace_includes_orderflow_data_quality_fields() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        "data/sample_footprint_bullish.csv",
        "--show-trace",
    )

    assert "Decision Trace" in output
    assert "orderflow_data_quality_status=PASSED" in output
    assert "orderflow_data_quality_passed=True" in output
    assert "orderflow_data_quality_blocking_reasons=None" in output
