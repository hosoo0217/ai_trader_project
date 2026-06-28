from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_demo_mode_with_apex_profile_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")
    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_demo_mode_with_spot_profile_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bearish", "--profile", "spot")
    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bearish" in output


def test_backtest_mode_with_apex_profile_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")
    assert "AI Trader Backtest" in output
    assert "Scenario: bullish" in output


def test_backtest_mode_with_spot_profile_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bearish", "--profile", "spot")
    assert "AI Trader Backtest" in output
    assert "Scenario: bearish" in output


def test_safe_profile_blocks_trading_safely() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "safe")
    assert "Safe profile" in output
    assert "Trade executed or blocked: Blocked / No trade" in output


def test_output_contains_selected_profile_name() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")
    assert "Selected Trading Profile" in output
    assert "Profile name: Apex Futures Scalper" in output


def test_invalid_profile_is_rejected_safely() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "invalid")
    assert "Invalid profile" in output
    assert "Safe fallback" in output
