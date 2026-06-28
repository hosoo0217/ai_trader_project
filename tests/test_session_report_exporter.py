"""Unit tests for exporting full trading session reports."""

from __future__ import annotations

import json
from pathlib import Path

from storage.session_report import TradingSessionReport
from storage.session_report_exporter import SessionReportExportConfig, SessionReportExporter


def _sample_report() -> TradingSessionReport:
    return TradingSessionReport(
        session_id="session-1",
        mode="demo",
        scenario="bullish",
        profile="Apex Futures Scalper",
        final_action="BUY",
        trade_executed=True,
        market_bias="BULLISH",
        smc_bias="BULLISH",
        crt_bias="BULLISH",
        orderflow_bias="BULLISH",
        safety_status="PASSED",
        safety_passed=True,
        blocked_reasons=[],
        journal_summary={"total_entries": 1, "executed_trades": 1},
        performance_summary={"total_pnl": 25.0, "win_rate": 100.0},
        ai_coach_summary="Paper trade followed the rules.",
        decision_trace_id="trace-1",
        reasons=["Session report generated"],
        warnings=[],
    )


def _config(tmp_path: Path) -> SessionReportExportConfig:
    return SessionReportExportConfig(output_dir=str(tmp_path / "reports"))


def test_export_text_creates_txt_file(tmp_path: Path) -> None:
    text_path = SessionReportExporter().export_text(_sample_report(), _config(tmp_path))

    assert text_path is not None
    assert Path(text_path).exists()


def test_export_json_creates_json_file(tmp_path: Path) -> None:
    json_path = SessionReportExporter().export_json(_sample_report(), _config(tmp_path))

    assert json_path is not None
    assert Path(json_path).exists()


def test_export_all_creates_both_files(tmp_path: Path) -> None:
    result = SessionReportExporter().export_all(_sample_report(), _config(tmp_path))

    assert result.exported is True
    assert result.text_path is not None
    assert result.json_path is not None
    assert Path(result.text_path).exists()
    assert Path(result.json_path).exists()


def test_output_directory_is_created(tmp_path: Path) -> None:
    output_dir = tmp_path / "new_session_reports"
    config = SessionReportExportConfig(output_dir=str(output_dir))

    result = SessionReportExporter().export_all(_sample_report(), config)

    assert result.exported is True
    assert output_dir.exists()


def test_text_file_contains_full_trading_session_report(tmp_path: Path) -> None:
    text_path = SessionReportExporter().export_text(_sample_report(), _config(tmp_path))

    assert text_path is not None
    text = Path(text_path).read_text(encoding="utf-8")
    assert "Full Trading Session Report" in text
    assert "Decision Summary" in text


def test_json_file_can_be_loaded(tmp_path: Path) -> None:
    json_path = SessionReportExporter().export_json(_sample_report(), _config(tmp_path))

    assert json_path is not None
    with Path(json_path).open(encoding="utf-8") as file:
        payload = json.load(file)

    assert payload["session_id"] == "session-1"
    assert payload["final_action"] == "BUY"


def test_missing_report_does_not_crash(tmp_path: Path) -> None:
    result = SessionReportExporter().export_all(None, _config(tmp_path))

    assert result.exported is True
    assert result.text_path is not None
    assert result.json_path is not None


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    result = SessionReportExporter().export_all(_sample_report(), _config(tmp_path))

    text = SessionReportExporter().explain(result)

    assert "Trading session report export" in text
    assert "exported=True" in text
