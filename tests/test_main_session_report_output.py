"""Tests for Full Trading Session Report output in main.py."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
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


def test_main_saves_session_history_when_flag_is_used(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--save-session-history",
        "--session-history-dir",
        str(history_dir),
    )

    assert "Backtest Session History" in output
    assert "- Saved: True" in output
    assert (history_dir / "session_history.json").exists()


def test_session_history_json_is_created(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"

    _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--save-session-history",
        "--session-history-dir",
        str(history_dir),
    )

    history_path = history_dir / "session_history.json"
    assert history_path.exists()
    with history_path.open(encoding="utf-8") as file:
        history = json.load(file)
    assert len(history) == 1


def test_multiple_runs_append_multiple_session_reports(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    args = (
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--save-session-history",
        "--session-history-dir",
        str(history_dir),
    )

    _run_main(*args)
    _run_main(*args)

    with (history_dir / "session_history.json").open(encoding="utf-8") as file:
        history = json.load(file)
    assert len(history) == 2


def test_session_history_output_contains_heading(tmp_path: Path) -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--save-session-history",
        "--session-history-dir",
        str(tmp_path / "history"),
    )

    assert "Backtest Session History" in output
    assert "- History path:" in output


def test_existing_demo_command_without_history_still_works() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Backtest Session History" not in output


def test_invalid_history_json_does_not_crash(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text("{not valid json", encoding="utf-8")

    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--save-session-history",
        "--show-session-history-summary",
        "--session-history-dir",
        str(history_dir),
    )

    assert "Backtest Session History" in output
    assert "- Saved: True" in output
    assert "- Total sessions: 1" in output


def test_blocked_trade_can_still_be_saved_to_history(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"

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
        "--save-session-history",
        "--show-session-history-summary",
        "--session-history-dir",
        str(history_dir),
    )

    assert "Backtest Session History" in output
    assert "- Saved: True" in output
    assert "- Blocked sessions:" in output
    assert "spread" in output.lower()


def test_main_prints_session_history_trend_when_requested(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps(
            [
                {"trade_executed": True, "market_bias": "BULLISH"},
                {"trade_executed": False, "market_bias": "BEARISH", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "NEUTRAL", "blocked_reasons": ["Spread too high"]},
            ]
        ),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "Session History Trend" in output
    assert "- Trend status:" in output
    assert "AI Coach Session Trend Review" in output
    assert "Strategy Improvement Suggestions" in output
    assert "Human Approval Requests" in output
    assert "- Pending requests:" in output


def test_session_history_trend_output_contains_total_sessions(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "- Total sessions: 1" in output
    assert "- Status:" in output
    assert "- Grade:" in output
    assert "- Summary:" in output
    assert "Human approval required" in output
    assert "Human Approval Requests" in output


def test_session_trend_coach_output_contains_trend_read(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps(
            [
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["News block"]},
            ]
        ),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "AI Coach Session Trend Review" in output
    assert "- Trend read:" in output


def test_missing_history_file_does_not_crash_session_trend(tmp_path: Path) -> None:
    output = _run_main("--show-session-trend", "--session-history-dir", str(tmp_path / "missing_history"))

    assert "Session History Trend" in output
    assert "- Total sessions: 0" in output
    assert "- Trend status: NOT_ENOUGH_DATA" in output
    assert "AI Coach Session Trend Review" in output
    assert "Strategy Improvement Suggestions" in output
    assert "Human Approval Requests" in output
    assert "- Status: REQUESTS_CREATED" in output


def test_invalid_history_json_does_not_crash_session_trend(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text("{not valid json", encoding="utf-8")

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "Session History Trend" in output
    assert "- Total sessions: 0" in output
    assert "- Trend status: NOT_ENOUGH_DATA" in output
    assert "AI Coach Session Trend Review" in output
    assert "Strategy Improvement Suggestions" in output
    assert "Human Approval Requests" in output
    assert "- Status: REQUESTS_CREATED" in output


def test_session_trend_with_no_suggestions_prints_no_suggestion_approval_status(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps(
            [
                {"trade_executed": True, "market_bias": "BULLISH"},
                {"trade_executed": False, "market_bias": "BEARISH", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "NEUTRAL", "blocked_reasons": ["News block"]},
            ]
        ),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "Strategy Improvement Suggestions" in output
    assert "Human Approval Requests" in output
    assert "- Status: NO_SUGGESTIONS" in output
    assert "- Pending requests: 0" in output


def test_not_enough_data_shows_not_enough_data_status(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir))

    assert "- Trend status: NOT_ENOUGH_DATA" in output
    assert "NOT_ENOUGH_DATA" in output
    assert "Save more session history" in output


def test_session_trend_coach_output_has_no_direct_trade_commands(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps(
            [
                {"trade_executed": True, "market_bias": "BULLISH"},
                {"trade_executed": True, "market_bias": "BULLISH"},
                {"trade_executed": True, "market_bias": "BULLISH"},
            ]
        ),
        encoding="utf-8",
    )

    output = _run_main("--show-session-trend", "--session-history-dir", str(history_dir)).lower()

    forbidden_phrases = [
        "buy now",
        "sell now",
        "enter trade",
        "open position",
        "guaranteed signal",
        "automatically change strategy",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in output


def test_main_records_approve_human_approval_decision(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    log_dir = tmp_path / "approval_logs"
    proposal_dir = tmp_path / "proposals"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps(
            [
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
                {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["News block"]},
            ]
        ),
        encoding="utf-8",
    )

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "APPROVE",
        "--approval-decided-by",
        "Hosoo",
        "--approval-notes",
        "Review later before changing rules",
        "--approval-log-dir",
        str(log_dir),
        "--proposal-dir",
        str(proposal_dir),
    )

    log_path = log_dir / "human_approval_log.json"
    proposals_path = proposal_dir / "change_proposals.json"
    records = json.loads(log_path.read_text(encoding="utf-8"))
    proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
    assert "Human Approval Decision" in output
    assert "Approved Change Proposal" in output
    assert "- Decision: APPROVE" in output
    assert "- Created: True" in output
    assert "- No strategy rule was changed." in output
    assert "- No trade signal was created." in output
    assert "Proposal is saved for future human review only" in output
    assert "Final human review is still required" in output
    assert log_path.exists()
    assert proposals_path.exists()
    assert records[0]["decision"] == "APPROVE"
    assert proposals[0]["auto_implementation_allowed"] is False
    assert proposals[0]["human_review_required"] is True


def test_main_records_reject_human_approval_decision(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    log_dir = tmp_path / "approval_logs"
    proposal_dir = tmp_path / "proposals"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "REJECT",
        "--approval-decided-by",
        "Hosoo",
        "--approval-notes",
        "Not enough data yet",
        "--approval-log-dir",
        str(log_dir),
        "--proposal-dir",
        str(proposal_dir),
    )

    records = json.loads((log_dir / "human_approval_log.json").read_text(encoding="utf-8"))
    assert "Human Approval Decision" in output
    assert "Approved Change Proposal" in output
    assert "- Decision: REJECT" in output
    assert "No change proposal created because decision was not approved" in output
    assert records[0]["decision"] == "REJECT"
    assert records[0]["approved"] is False
    assert not (proposal_dir / "change_proposals.json").exists()


def test_main_records_needs_review_human_approval_decision(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    log_dir = tmp_path / "approval_logs"
    proposal_dir = tmp_path / "proposals"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "NEEDS_REVIEW",
        "--approval-decided-by",
        "Hosoo",
        "--approval-notes",
        "Need more backtest sessions",
        "--approval-log-dir",
        str(log_dir),
        "--proposal-dir",
        str(proposal_dir),
    )

    records = json.loads((log_dir / "human_approval_log.json").read_text(encoding="utf-8"))
    assert "Human Approval Decision" in output
    assert "Approved Change Proposal" in output
    assert "- Decision: NEEDS_REVIEW" in output
    assert "No change proposal created because decision was not approved" in output
    assert records[0]["decision"] == "NEEDS_REVIEW"
    assert records[0]["approved"] is False
    assert not (proposal_dir / "change_proposals.json").exists()


def test_approval_decision_without_session_trend_does_not_crash() -> None:
    output = _run_main("--approval-decision", "APPROVE")

    assert "Session trend is required to create approval requests" in output
    assert "No strategy rule was changed" in output


def test_out_of_range_approval_request_index_does_not_crash(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    log_dir = tmp_path / "approval_logs"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "APPROVE",
        "--approval-request-index",
        "99",
        "--approval-log-dir",
        str(log_dir),
    )

    assert "Human Approval Decision" in output
    assert "No approval requests available at that index" in output
    assert "- Log saved: False" in output


def test_invalid_approval_decision_does_not_crash(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    log_dir = tmp_path / "approval_logs"
    history_dir.mkdir(parents=True)
    (history_dir / "session_history.json").write_text(
        json.dumps([{"trade_executed": True, "market_bias": "BULLISH"}]),
        encoding="utf-8",
    )

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "MAYBE",
        "--approval-log-dir",
        str(log_dir),
    )

    records = json.loads((log_dir / "human_approval_log.json").read_text(encoding="utf-8"))
    assert "Human Approval Decision" in output
    assert "- Decision: UNKNOWN" in output
    assert records[0]["decision"] == "UNKNOWN"
    assert records[0]["approved"] is False


def test_approve_change_proposal_with_missing_history_does_not_crash(tmp_path: Path) -> None:
    history_dir = tmp_path / "missing_history"
    log_dir = tmp_path / "approval_logs"
    proposal_dir = tmp_path / "proposals"

    output = _run_main(
        "--show-session-trend",
        "--session-history-dir",
        str(history_dir),
        "--approval-decision",
        "APPROVE",
        "--approval-log-dir",
        str(log_dir),
        "--proposal-dir",
        str(proposal_dir),
    )

    proposals_path = proposal_dir / "change_proposals.json"
    assert "Session History Trend" in output
    assert "Approved Change Proposal" in output
    assert "- Created: True" in output
    assert proposals_path.exists()


def _write_saved_change_proposal(proposal_dir: Path) -> Path:
    proposal_dir.mkdir(parents=True)
    proposals_path = proposal_dir / "change_proposals.json"
    proposals_path.write_text(
        json.dumps(
            [
                {
                    "proposal_id": "proposal-risk-management-12345678",
                    "source_request_id": "approval-risk-management-12345678",
                    "category": "RISK_MANAGEMENT",
                    "priority": "HIGH",
                    "title": "Review proposed RISK_MANAGEMENT change",
                    "description": "Review drawdown limits before changing any strategy rule.",
                    "reason": "A human approved this future reviewed change proposal",
                    "risk": "Risk must be reviewed again before any implementation.",
                    "proposed_change": "Prepare a human-reviewed change proposal.",
                    "status": "PROPOSED",
                    "human_review_required": True,
                    "auto_implementation_allowed": False,
                    "reasons": ["Change proposals are planning records only"],
                    "blocking_reasons": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    return proposals_path


def test_main_records_accept_change_proposal_review(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    review_log_dir = tmp_path / "review_logs"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "ACCEPT",
        "--change-proposal-index",
        "0",
        "--proposal-reviewed-by",
        "Hosoo",
        "--proposal-review-notes",
        "Accepted for future work only",
        "--proposal-dir",
        str(proposal_dir),
        "--proposal-review-log-dir",
        str(review_log_dir),
    )

    review_log_path = review_log_dir / "change_proposal_reviews.json"
    records = json.loads(review_log_path.read_text(encoding="utf-8"))
    assert "Change Proposal Review" in output
    assert "- Decision: ACCEPT" in output
    assert "- Status: ACCEPTED_FOR_FUTURE_WORK" in output
    assert "- Implementation allowed: False" in output
    assert "- No strategy rule was changed." in output
    assert review_log_path.exists()
    assert records[0]["review_decision"] == "ACCEPT"
    assert records[0]["implementation_allowed"] is False


def test_main_records_reject_change_proposal_review(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    review_log_dir = tmp_path / "review_logs"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "REJECT",
        "--proposal-dir",
        str(proposal_dir),
        "--proposal-review-log-dir",
        str(review_log_dir),
    )

    records = json.loads((review_log_dir / "change_proposal_reviews.json").read_text(encoding="utf-8"))
    assert "Change Proposal Review" in output
    assert "- Decision: REJECT" in output
    assert "- Status: REJECTED" in output
    assert records[0]["review_decision"] == "REJECT"
    assert records[0]["accepted"] is False


def test_main_records_needs_more_data_change_proposal_review(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    review_log_dir = tmp_path / "review_logs"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "NEEDS_MORE_DATA",
        "--proposal-dir",
        str(proposal_dir),
        "--proposal-review-log-dir",
        str(review_log_dir),
    )

    records = json.loads((review_log_dir / "change_proposal_reviews.json").read_text(encoding="utf-8"))
    assert "Change Proposal Review" in output
    assert "- Decision: NEEDS_MORE_DATA" in output
    assert records[0]["review_status"] == "NEEDS_MORE_DATA"


def test_main_records_needs_backtest_change_proposal_review(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    review_log_dir = tmp_path / "review_logs"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "NEEDS_BACKTEST",
        "--proposal-dir",
        str(proposal_dir),
        "--proposal-review-log-dir",
        str(review_log_dir),
    )

    records = json.loads((review_log_dir / "change_proposal_reviews.json").read_text(encoding="utf-8"))
    assert "Change Proposal Review" in output
    assert "- Decision: NEEDS_BACKTEST" in output
    assert records[0]["review_status"] == "NEEDS_BACKTEST"


def test_review_change_proposal_missing_file_does_not_crash(tmp_path: Path) -> None:
    output = _run_main(
        "--review-change-proposal",
        "ACCEPT",
        "--proposal-dir",
        str(tmp_path / "missing_proposals"),
    )

    assert "Change Proposal Review" in output
    assert "No saved change proposals available" in output
    assert "- No strategy rule was changed." in output


def test_review_change_proposal_out_of_range_does_not_crash(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "ACCEPT",
        "--change-proposal-index",
        "99",
        "--proposal-dir",
        str(proposal_dir),
    )

    assert "Change Proposal Review" in output
    assert "Change proposal index is out of range" in output
    assert "- Log saved: False" in output


def test_review_change_proposal_output_has_no_direct_trade_commands(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"
    review_log_dir = tmp_path / "review_logs"
    _write_saved_change_proposal(proposal_dir)

    output = _run_main(
        "--review-change-proposal",
        "ACCEPT",
        "--proposal-dir",
        str(proposal_dir),
        "--proposal-review-log-dir",
        str(review_log_dir),
    ).lower()

    forbidden_phrases = [
        "buy now",
        "sell now",
        "enter trade",
        "open position",
        "guaranteed signal",
        "strategy changed automatically",
        "auto implemented",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in output


def test_existing_demo_command_still_works_without_session_trend() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Session History Trend" not in output
