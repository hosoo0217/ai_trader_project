"""Tests for the diagnostic-only bulk Sierra audit runner."""

from __future__ import annotations

import json

from analysis.bulk_sierra_audit_runner import (
    audit_bulk_sierra_files,
    format_audit_markdown,
)


MARKET_CSV = """Date,Time,Open,High,Low,Last,Volume
2026-07-02,18:00:00.000000,4200.0,4201.0,4199.0,4200.5,100
2026-07-03,08:45:00.000000,4200.5,4201.5,4200.0,4201.0,120
2026-07-03,18:00:00.000000,4210.0,4211.0,4209.0,4210.5,90
2026-07-04,08:45:00.000000,4210.5,4211.5,4210.0,4211.0,80
2026-07-04,18:00:00.000000,4220.0,4221.0,4219.0,4220.5,70
"""


FOOTPRINT_CSV = """DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
2026-07-02 18:00:00,0,4200.0,1,2,3,1,2
2026-07-03 08:45:00,1,4201.0,2,3,5,1,3
2026-07-03 18:00:00,2,4210.0,3,4,7,1,4
2026-07-04 08:44:00,3,4211.0,1,1,2,0,1
bad-date,4,4220.0,1,1,2,0,1
2026-07-05 18:00:00,5,4230.0,1,2,3,1,2
"""


def test_audit_runner_counts_sessions_and_statuses(tmp_path) -> None:
    market_path = tmp_path / "market.csv"
    footprint_path = tmp_path / "footprint.csv"
    market_path.write_text(MARKET_CSV)
    footprint_path.write_text(FOOTPRINT_CSV)

    report = audit_bulk_sierra_files(market_path, footprint_path)

    assert report.totals.total_sessions == 4
    assert report.totals.matched_sessions == 1
    assert report.totals.mismatched_sessions == 1
    assert report.totals.missing_market_sessions == 1
    assert report.totals.missing_footprint_sessions == 1
    assert report.totals.total_bad_timestamp_rows == 1
    assert report.session_start_hour == 18


def test_audit_runner_writes_json_and_markdown_when_paths_are_provided(tmp_path) -> None:
    market_path = tmp_path / "market.csv"
    footprint_path = tmp_path / "footprint.csv"
    json_path = tmp_path / "audit.json"
    text_path = tmp_path / "audit.md"
    market_path.write_text(MARKET_CSV)
    footprint_path.write_text(FOOTPRINT_CSV)

    report = audit_bulk_sierra_files(
        market_path,
        footprint_path,
        output_json_path=json_path,
        output_text_path=text_path,
    )

    payload = json.loads(json_path.read_text())
    markdown = text_path.read_text()

    assert payload["totals"]["total_sessions"] == report.totals.total_sessions
    assert payload["totals"]["total_bad_timestamp_rows"] == 1
    assert payload["sessions"][0]["status"] == "MATCHED"
    assert "# Bulk Sierra Audit Summary" in markdown
    assert "- Total sessions: 4" in markdown
    assert "| 2026-07-02 | MATCHED |" in markdown


def test_audit_runner_does_not_write_outputs_by_default(tmp_path) -> None:
    market_path = tmp_path / "market.csv"
    footprint_path = tmp_path / "footprint.csv"
    market_path.write_text(MARKET_CSV)
    footprint_path.write_text(FOOTPRINT_CSV)

    audit_bulk_sierra_files(market_path, footprint_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["footprint.csv", "market.csv"]


def test_audit_runner_passes_configurable_session_start_hour(tmp_path) -> None:
    market_path = tmp_path / "market.csv"
    footprint_path = tmp_path / "footprint.csv"
    market_path.write_text(
        """Date,Time,Open,High,Low,Last
2026-07-02,17:00:00.000000,4200.0,4201.0,4199.0,4200.5
2026-07-03,16:59:00.000000,4200.5,4201.5,4200.0,4201.0
"""
    )
    footprint_path.write_text(
        """DateTime,BarIndex,Price,BidVolume,AskVolume
2026-07-02 17:00:00,0,4200.0,1,2
2026-07-03 16:59:00,1,4201.0,2,3
"""
    )

    report = audit_bulk_sierra_files(market_path, footprint_path, session_start_hour=17)

    assert report.session_start_hour == 17
    assert report.totals.total_sessions == 1
    assert report.sessions[0].session_date == "2026-07-02"
    assert report.sessions[0].status == "MATCHED"


def test_format_audit_markdown_is_human_readable(tmp_path) -> None:
    market_path = tmp_path / "market.csv"
    footprint_path = tmp_path / "footprint.csv"
    market_path.write_text(MARKET_CSV)
    footprint_path.write_text(FOOTPRINT_CSV)
    report = audit_bulk_sierra_files(market_path, footprint_path)

    markdown = format_audit_markdown(report)

    assert "Diagnostic-only audit" in markdown
    assert "- Session start hour: 18" in markdown
    assert "- Matched sessions: 1" in markdown
