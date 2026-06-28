"""Tests for Order Flow visibility in main.py output."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

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


def test_main_works_without_replay_csv() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Order Flow Replay" not in output


def test_orderflow_replay_works_with_bullish_sample_csv() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
    )

    assert "Order Flow Replay" in output
    assert "- Active: True" in output
    assert "- Passed: True" in output
    assert "- Final bias: BULLISH" in output
    assert "- Final CVD:" in output
    assert "Order Flow Replay Report" in output
    assert "- Total steps: 1" in output
    assert "- Bullish steps: 1" in output
    assert "- Dominant bias: BULLISH" in output
    assert "- Average confidence:" in output
    assert "AI Coach Order Flow Replay Review" in output
    assert "- Status:" in output
    assert "- Grade:" in output
    assert "- Market read:" in output
    assert "Order Flow supports bullish context" in output


def test_orderflow_replay_works_with_bearish_sample_csv() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bearish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bearish.csv",
    )

    assert "Order Flow Replay" in output
    assert "- Active: True" in output
    assert "- Passed: True" in output
    assert "- Final bias: BEARISH" in output
    assert "Order Flow Replay Report" in output
    assert "- Bearish steps: 1" in output
    assert "- Dominant bias: BEARISH" in output
    assert "AI Coach Order Flow Replay Review" in output
    assert "- Status:" in output
    assert "- Grade:" in output
    assert "- Market read:" in output
    assert "Order Flow supports bearish context" in output


def test_orderflow_replay_steps_print_when_requested() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sierra_chart_footprint_template.csv",
        "--show-orderflow-replay-steps",
    )

    assert "Order Flow Replay" in output
    assert "- Replay steps:" in output
    assert "  - Index: 0" in output
    assert "    Candle delta:" in output
    assert "    Cumulative delta:" in output
    assert "    Order Flow bias:" in output


def test_missing_orderflow_replay_csv_path_does_not_crash() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/missing_replay.csv",
    )

    assert "Order Flow Replay" in output
    assert "- Active: False" in output
    assert "- Passed: False" in output
    assert "- Data quality status: INVALID" in output
    assert "Order Flow replay CSV path does not exist" in output
    assert "Order Flow Replay Report" in output
    assert "- Total steps: 0" in output
    assert "- Dominant bias: UNKNOWN" in output
    assert "- Warnings: Order Flow replay CSV path does not exist" in output
    assert "AI Coach Order Flow Replay Review" in output
    assert "- Status: NO_USABLE_ORDERFLOW" in output
    assert "- Grade: F" in output


def test_invalid_orderflow_replay_csv_does_not_crash(tmp_path) -> None:
    invalid_csv = tmp_path / "invalid_replay.csv"
    invalid_csv.write_text("not,a,footprint\n1,2,3\n", encoding="utf-8")

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        str(invalid_csv),
    )

    assert "Order Flow Replay" in output
    assert "- Active: False" in output
    assert "- Passed: False" in output
    assert "- Data quality status: EMPTY" in output
    assert "Order Flow Replay Report" in output
    assert "- Total steps: 0" in output
    assert "- Dominant bias: UNKNOWN" in output
    assert "AI Coach Order Flow Replay Review" in output
    assert "- Status: NO_USABLE_ORDERFLOW" in output


def test_orderflow_replay_coach_output_has_no_direct_trade_commands() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
    ).lower()

    forbidden_phrases = [
        "buy now",
        "sell now",
        "enter trade",
        "open position",
        "guaranteed signal",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in output


def test_main_exports_orderflow_replay_report_when_flag_is_used(tmp_path) -> None:
    report_dir = tmp_path / "reports"

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(report_dir),
    )

    assert "Order Flow Replay Export" in output
    assert "- Exported: True" in output
    assert (report_dir / "orderflow_replay_report.txt").exists()
    assert (report_dir / "orderflow_replay_report.json").exists()


def test_exported_orderflow_replay_txt_file_is_created(tmp_path) -> None:
    report_dir = tmp_path / "reports"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(report_dir),
    )

    text_path = report_dir / "orderflow_replay_report.txt"
    assert text_path.exists()
    assert "Order Flow Replay Report" in text_path.read_text(encoding="utf-8")


def test_exported_orderflow_replay_json_file_is_created(tmp_path) -> None:
    report_dir = tmp_path / "reports"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(report_dir),
    )

    json_path = report_dir / "orderflow_replay_report.json"
    assert json_path.exists()
    assert "BULLISH" in json_path.read_text(encoding="utf-8")


def test_export_flag_without_replay_csv_does_not_crash(tmp_path) -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(tmp_path / "reports"),
    )

    assert "Order Flow Replay Export" in output
    assert "- Exported: False" in output
    assert "Order Flow replay CSV is required to export report" in output


def test_export_with_invalid_replay_csv_does_not_crash(tmp_path) -> None:
    invalid_csv = tmp_path / "invalid_replay_export.csv"
    invalid_csv.write_text("not,a,footprint\n1,2,3\n", encoding="utf-8")
    report_dir = tmp_path / "reports"

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        str(invalid_csv),
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(report_dir),
    )

    assert "Order Flow Replay Export" in output
    assert "- Exported: True" in output
    assert (report_dir / "orderflow_replay_report.txt").exists()
    assert (report_dir / "orderflow_replay_report.json").exists()


def test_no_orderflow_report_steps_excludes_steps_from_export(tmp_path) -> None:
    report_dir = tmp_path / "reports"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-replay-csv",
        "data/sample_footprint_bullish.csv",
        "--export-orderflow-report",
        "--orderflow-report-dir",
        str(report_dir),
        "--no-orderflow-report-steps",
    )

    text = Path(report_dir / "orderflow_replay_report.txt").read_text(encoding="utf-8")
    assert "Replay Steps" not in text
