"""Unit tests for exporting Order Flow replay reports."""

from __future__ import annotations

import json
from pathlib import Path

from ai.orderflow_replay_coach import OrderFlowReplayCoach, OrderFlowReplayCoachConfig
from orderflow.replay import OrderFlowReplayConfig, OrderFlowReplayEngine, OrderFlowReplayResult
from orderflow.replay_report import OrderFlowReplayReportGenerator
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter
from storage.orderflow_replay_exporter import OrderFlowReplayExportConfig, OrderFlowReplayExporter


def _sample_export_inputs(path: str = "data/sample_footprint_bullish.csv"):
    candles = SierraChartImporter().load_csv(path, SierraChartImportConfig())
    replay_result = OrderFlowReplayEngine().replay(candles, OrderFlowReplayConfig())
    report = OrderFlowReplayReportGenerator().generate(replay_result)
    coach_review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())
    return replay_result, report, coach_review


def _config(tmp_path: Path, include_steps: bool = True) -> OrderFlowReplayExportConfig:
    return OrderFlowReplayExportConfig(output_dir=str(tmp_path / "reports"), include_steps=include_steps)


def test_export_text_creates_txt_file(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()

    text_path = OrderFlowReplayExporter().export_text(replay_result, report, coach_review, _config(tmp_path))

    assert text_path is not None
    assert Path(text_path).exists()


def test_export_json_creates_json_file(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()

    json_path = OrderFlowReplayExporter().export_json(replay_result, report, coach_review, _config(tmp_path))

    assert json_path is not None
    assert Path(json_path).exists()


def test_export_all_creates_both_files(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()

    result = OrderFlowReplayExporter().export_all(replay_result, report, coach_review, _config(tmp_path))

    assert result.exported is True
    assert result.text_path is not None
    assert result.json_path is not None
    assert Path(result.text_path).exists()
    assert Path(result.json_path).exists()


def test_output_directory_is_created(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    output_dir = tmp_path / "new_reports_folder"
    config = OrderFlowReplayExportConfig(output_dir=str(output_dir))

    result = OrderFlowReplayExporter().export_all(replay_result, report, coach_review, config)

    assert result.exported is True
    assert output_dir.exists()


def test_exported_text_contains_replay_report_section(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    text_path = OrderFlowReplayExporter().export_text(replay_result, report, coach_review, _config(tmp_path))

    assert text_path is not None
    text = Path(text_path).read_text(encoding="utf-8")
    assert "Order Flow Replay Report" in text


def test_exported_text_contains_ai_coach_section(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    text_path = OrderFlowReplayExporter().export_text(replay_result, report, coach_review, _config(tmp_path))

    assert text_path is not None
    text = Path(text_path).read_text(encoding="utf-8")
    assert "AI Coach" in text


def test_json_file_can_be_loaded(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    json_path = OrderFlowReplayExporter().export_json(replay_result, report, coach_review, _config(tmp_path))

    assert json_path is not None
    with Path(json_path).open(encoding="utf-8") as file:
        payload = json.load(file)

    assert payload["replay_result"]["final_bias"] == "BULLISH"
    assert "coach_review" in payload


def test_include_steps_false_excludes_detailed_steps_from_text(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    text_path = OrderFlowReplayExporter().export_text(
        replay_result,
        report,
        coach_review,
        _config(tmp_path, include_steps=False),
    )

    assert text_path is not None
    text = Path(text_path).read_text(encoding="utf-8")
    assert "Replay Steps" not in text
    assert "Index:" not in text


def test_missing_inputs_do_not_crash(tmp_path: Path) -> None:
    result = OrderFlowReplayExporter().export_all(None, None, None, _config(tmp_path))

    assert result.exported is True
    assert result.text_path is not None
    assert result.json_path is not None


def test_failed_replay_can_still_be_exported(tmp_path: Path) -> None:
    replay_result = OrderFlowReplayResult(
        passed=False,
        final_bias="UNKNOWN",
        blocking_reasons=["Replay was blocked by data quality"],
    )
    report = OrderFlowReplayReportGenerator().generate(replay_result)
    coach_review = OrderFlowReplayCoach().review(report, OrderFlowReplayCoachConfig())

    result = OrderFlowReplayExporter().export_all(replay_result, report, coach_review, _config(tmp_path))

    assert result.exported is True
    assert result.blocking_reasons == []


def test_explain_returns_readable_text(tmp_path: Path) -> None:
    replay_result, report, coach_review = _sample_export_inputs()
    result = OrderFlowReplayExporter().export_all(replay_result, report, coach_review, _config(tmp_path))

    text = OrderFlowReplayExporter().explain(result)

    assert "Order Flow replay export" in text
    assert "exported=True" in text
