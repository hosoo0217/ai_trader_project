"""Unit tests for JSON-backed trading session history."""

from __future__ import annotations

from pathlib import Path

from storage.session_history import SessionHistoryConfig, SessionHistoryStore
from storage.session_report import TradingSessionReport


def _config(tmp_path: Path) -> SessionHistoryConfig:
    return SessionHistoryConfig(output_dir=str(tmp_path / "reports"))


def _report(
    session_id: str = "session-1",
    trade_executed: bool = True,
    market_bias: str = "BULLISH",
    blocked_reasons: list[str] | None = None,
) -> TradingSessionReport:
    return TradingSessionReport(
        session_id=session_id,
        mode="demo",
        scenario="bullish",
        profile="Apex",
        final_action="BUY" if trade_executed else "NO_TRADE",
        trade_executed=trade_executed,
        market_bias=market_bias,
        smc_bias=None,
        crt_bias=None,
        orderflow_bias=None,
        safety_status="PASSED" if trade_executed else "BLOCKED",
        safety_passed=trade_executed,
        blocked_reasons=blocked_reasons or [],
        journal_summary={},
        performance_summary={},
        ai_coach_summary=None,
        decision_trace_id=None,
        reasons=["Session report generated"],
        warnings=[],
    )


def test_append_report_creates_history_file(tmp_path: Path) -> None:
    config = _config(tmp_path)

    saved = SessionHistoryStore().append_report(_report(), config)

    assert saved is True
    assert (Path(config.output_dir) / config.history_filename).exists()


def test_append_report_adds_one_report(tmp_path: Path) -> None:
    config = _config(tmp_path)

    SessionHistoryStore().append_report(_report(), config)
    history = SessionHistoryStore().load_history(config)

    assert len(history) == 1
    assert history[0]["session_id"] == "session-1"


def test_multiple_reports_are_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = SessionHistoryStore()

    store.append_report(_report(session_id="session-1"), config)
    store.append_report(_report(session_id="session-2", trade_executed=False, market_bias="BEARISH"), config)
    history = store.load_history(config)

    assert len(history) == 2
    assert history[0]["session_id"] == "session-1"
    assert history[1]["session_id"] == "session-2"


def test_load_history_returns_saved_reports(tmp_path: Path) -> None:
    config = _config(tmp_path)
    store = SessionHistoryStore()
    store.append_report(_report(session_id="session-abc"), config)

    history = store.load_history(config)

    assert history[0]["session_id"] == "session-abc"


def test_summarize_counts_total_sessions(tmp_path: Path) -> None:
    history = [
        _report(session_id="1").__dict__,
        _report(session_id="2", trade_executed=False).__dict__,
    ]

    summary = SessionHistoryStore().summarize(history)

    assert summary.total_sessions == 2


def test_summarize_counts_executed_and_blocked_sessions() -> None:
    history = [
        {"trade_executed": True, "market_bias": "BULLISH"},
        {"trade_executed": False, "market_bias": "BEARISH"},
        {"trade_executed": False, "market_bias": "NEUTRAL"},
    ]

    summary = SessionHistoryStore().summarize(history)

    assert summary.executed_sessions == 1
    assert summary.blocked_sessions == 2


def test_summarize_counts_common_blocking_reasons() -> None:
    history = [
        {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]},
        {"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high", "News block"]},
    ]

    summary = SessionHistoryStore().summarize(history)

    assert summary.common_blocking_reasons["Spread too high"] == 2
    assert summary.common_blocking_reasons["News block"] == 1


def test_summarize_counts_bias_groups() -> None:
    history = [
        {"trade_executed": True, "market_bias": "BULLISH"},
        {"trade_executed": False, "market_bias": "BEARISH"},
        {"trade_executed": False, "market_bias": "NEUTRAL"},
        {"trade_executed": False, "market_bias": None, "final_action": "NO_TRADE"},
    ]

    summary = SessionHistoryStore().summarize(history)

    assert summary.bullish_sessions == 1
    assert summary.bearish_sessions == 1
    assert summary.neutral_sessions == 1
    assert summary.unknown_sessions == 1


def test_invalid_json_does_not_crash(tmp_path: Path) -> None:
    config = _config(tmp_path)
    path = Path(config.output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / config.history_filename).write_text("{not valid json", encoding="utf-8")

    history = SessionHistoryStore().load_history(config)

    assert history == []


def test_explain_returns_readable_text() -> None:
    summary = SessionHistoryStore().summarize(
        [{"trade_executed": False, "market_bias": "UNKNOWN", "blocked_reasons": ["Spread too high"]}]
    )

    text = SessionHistoryStore().explain(summary)

    assert "Session history summary" in text
    assert "total_sessions=1" in text
    assert "Spread too high=1" in text
