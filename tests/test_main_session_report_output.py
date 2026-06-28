"""Tests for Full Trading Session Report output in main.py."""

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


def test_main_exports_session_report_when_flag_is_used(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--export-session-report",
        "--session-report-dir",
        str(report_dir),
    )

    assert "Full Trading Session Report Export" in output
    assert "- Exported: True" in output
    assert (report_dir / "trading_session_report.txt").exists()
    assert (report_dir / "trading_session_report.json").exists()


def test_exported_session_report_txt_file_is_created(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--export-session-report",
        "--session-report-dir",
        str(report_dir),
    )

    text_path = report_dir / "trading_session_report.txt"
    assert text_path.exists()
    assert "Full Trading Session Report" in text_path.read_text(encoding="utf-8")


def test_exported_session_report_json_file_is_created(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--export-session-report",
        "--session-report-dir",
        str(report_dir),
    )

    json_path = report_dir / "trading_session_report.json"
    assert json_path.exists()
    assert "final_action" in json_path.read_text(encoding="utf-8")


def test_existing_demo_command_without_export_still_works() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Full Trading Session Report Export" not in output


def test_blocked_trade_can_still_export_session_report(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-26T14:00:00Z",
        "--spread",
        "10.0",
        "--export-session-report",
        "--session-report-dir",
        str(report_dir),
    )

    assert "Full Trading Session Report Export" in output
    assert "- Exported: True" in output
    text = Path(report_dir / "trading_session_report.txt").read_text(encoding="utf-8")
    assert "Blocked Reasons" in text
    assert "spread" in text.lower()
