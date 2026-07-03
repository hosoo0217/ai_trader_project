"""Diagnostic-only runner for bulk Sierra session audits.

This module reads explicitly provided CSV paths, calls the bulk Sierra
validation helper, and optionally writes summary files. It does not run
backtests, import main.py, connect to brokers, or approve trading.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from analysis.bulk_sierra_validation import (
    SierraBulkSessionSummary,
    build_bulk_validation_summary,
)


@dataclass(frozen=True)
class BulkSierraAuditTotals:
    """Aggregate counts for a diagnostic bulk Sierra audit."""

    total_sessions: int
    matched_sessions: int
    mismatched_sessions: int
    missing_market_sessions: int
    missing_footprint_sessions: int
    total_bad_timestamp_rows: int


@dataclass(frozen=True)
class BulkSierraAuditReport:
    """Full diagnostic audit report."""

    session_start_hour: int
    totals: BulkSierraAuditTotals
    sessions: list[SierraBulkSessionSummary]


def audit_bulk_sierra_files(
    market_csv_path: str | Path,
    footprint_csv_path: str | Path,
    output_json_path: str | Path | None = None,
    output_text_path: str | Path | None = None,
    session_start_hour: int = 18,
) -> BulkSierraAuditReport:
    """Read explicit CSV files and produce a diagnostic session audit."""
    market_text = Path(market_csv_path).read_text()
    footprint_text = Path(footprint_csv_path).read_text()

    sessions = build_bulk_validation_summary(
        market_text,
        footprint_text,
        session_start_hour=session_start_hour,
    )
    report = BulkSierraAuditReport(
        session_start_hour=session_start_hour,
        totals=_build_totals(sessions),
        sessions=sessions,
    )

    if output_json_path is not None:
        Path(output_json_path).write_text(json.dumps(report_to_dict(report), indent=2))

    if output_text_path is not None:
        Path(output_text_path).write_text(format_audit_markdown(report))

    return report


def format_audit_markdown(report: BulkSierraAuditReport) -> str:
    """Format a human-readable Markdown audit summary."""
    lines = [
        "# Bulk Sierra Audit Summary",
        "",
        "Diagnostic-only audit. No backtests were run.",
        "",
        f"- Session start hour: {report.session_start_hour}",
        f"- Total sessions: {report.totals.total_sessions}",
        f"- Matched sessions: {report.totals.matched_sessions}",
        f"- Mismatched sessions: {report.totals.mismatched_sessions}",
        f"- Missing market sessions: {report.totals.missing_market_sessions}",
        f"- Missing footprint sessions: {report.totals.missing_footprint_sessions}",
        f"- Total bad timestamp rows: {report.totals.total_bad_timestamp_rows}",
        "",
        "| Session | Status | Start | End | Market rows | Footprint rows | Reasons |",
        "|---|---|---|---|---:|---:|---|",
    ]

    for session in report.sessions:
        reasons = "; ".join(session.reasons) if session.reasons else ""
        lines.append(
            "| "
            f"{session.session_date} | "
            f"{session.status} | "
            f"{_datetime_text(session.start)} | "
            f"{_datetime_text(session.end)} | "
            f"{session.market_row_count} | "
            f"{session.footprint_row_count} | "
            f"{reasons} |"
        )

    lines.append("")
    return "\n".join(lines)


def report_to_dict(report: BulkSierraAuditReport) -> dict[str, Any]:
    """Convert an audit report to a JSON-friendly dictionary."""
    payload = asdict(report)
    for session in payload["sessions"]:
        session["start"] = _datetime_text(session["start"])
        session["end"] = _datetime_text(session["end"])
    return payload


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for explicit diagnostic bulk Sierra audits."""
    parser = argparse.ArgumentParser(description="Diagnostic-only bulk Sierra session audit.")
    parser.add_argument("--market-csv", required=True)
    parser.add_argument("--footprint-csv", required=True)
    parser.add_argument("--output-json")
    parser.add_argument("--output-text")
    parser.add_argument("--session-start-hour", type=int, default=18)
    args = parser.parse_args(argv)

    report = audit_bulk_sierra_files(
        market_csv_path=args.market_csv,
        footprint_csv_path=args.footprint_csv,
        output_json_path=args.output_json,
        output_text_path=args.output_text,
        session_start_hour=args.session_start_hour,
    )
    print(format_audit_markdown(report))
    return 0


def _build_totals(sessions: list[SierraBulkSessionSummary]) -> BulkSierraAuditTotals:
    statuses = [session.status for session in sessions]
    market_bad_rows = max((session.market_bad_row_count for session in sessions), default=0)
    footprint_bad_rows = max((session.footprint_bad_row_count for session in sessions), default=0)

    return BulkSierraAuditTotals(
        total_sessions=len(sessions),
        matched_sessions=statuses.count("MATCHED"),
        mismatched_sessions=statuses.count("MISMATCHED"),
        missing_market_sessions=statuses.count("MISSING_MARKET"),
        missing_footprint_sessions=statuses.count("MISSING_FOOTPRINT"),
        total_bad_timestamp_rows=market_bad_rows + footprint_bad_rows,
    )


def _datetime_text(value: object) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ")
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
