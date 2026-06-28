from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO

from analysis.session_filter import SessionFilter
from config.trading_profiles import TradingProfileFactory, to_session_filter_config
import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_apex_profile_creates_enabled_session_filter() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    session_config = to_session_filter_config(profile)

    assert session_config.enabled is True
    assert session_config.block_weekends is True
    assert any(session.name == "London" and session.enabled for session in session_config.allowed_sessions)


def test_spot_profile_creates_enabled_session_filter() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()
    session_config = to_session_filter_config(profile)

    assert session_config.enabled is True
    assert session_config.block_weekends is True
    assert any(session.name == "New York" and session.enabled for session in session_config.allowed_sessions)


def test_safe_profile_blocks_sessions_safely() -> None:
    profile = TradingProfileFactory.create_safe_default_profile()
    session_config = to_session_filter_config(profile)

    result = SessionFilter().evaluate(
        datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        session_config,
    )

    assert result.allowed is False
    assert result.status == "SESSION_BLOCKED"


def test_demo_mode_with_apex_and_valid_london_time_runs_without_crashing() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T14:00:00Z",
    )

    assert "AI Trader Paper Trading Demo" in output
    assert "Session filter status" in output


def test_demo_mode_with_apex_and_asian_time_blocks_safely() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T02:00:00Z",
    )

    assert "Session filter status" in output
    assert "Session allowed: False" in output
    assert "Trade executed or blocked: Blocked / No trade" in output


def test_backtest_mode_runs_without_crashing_with_session_filter_enabled() -> None:
    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
    )

    assert "AI Trader Backtest" in output
    assert "Session filter status" in output


def test_output_contains_session_filter_information() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T14:00:00Z",
    )

    assert "Session filter status" in output
    assert "Active session" in output
    assert "Session allowed" in output


def test_invalid_session_time_does_not_crash() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "invalid-time",
    )

    assert "Warning" in output
    assert "AI Trader Paper Trading Demo" in output
