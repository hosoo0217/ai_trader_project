from contextlib import redirect_stdout
from io import StringIO

from analysis.spread_filter import SpreadFilter
from config.trading_profiles import TradingProfileFactory, to_spread_filter_config
import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_apex_profile_creates_spread_filter() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    config = to_spread_filter_config(profile)

    assert config.enabled is True
    assert config.max_spread == 3.0
    assert config.block_if_spread_unknown is False


def test_spot_profile_creates_spread_filter() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()
    config = to_spread_filter_config(profile)

    assert config.enabled is True
    assert config.max_spread == 3.0
    assert config.block_if_spread_unknown is True


def test_safe_profile_blocks_spread_safely() -> None:
    profile = TradingProfileFactory.create_safe_default_profile()
    config = to_spread_filter_config(profile)
    result = SpreadFilter().evaluate(0.1, config)

    assert config.enabled is True
    assert config.max_spread == 0.0
    assert config.block_if_spread_unknown is True
    assert result.allowed is False


def test_demo_mode_with_normal_spread_runs_without_crashing() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--session-time",
        "2026-06-24T14:00:00Z",
        "--spread",
        "2.0",
    )

    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_demo_mode_with_high_spread_blocks_safely() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--session-time",
        "2026-06-24T14:00:00Z",
        "--spread",
        "10.0",
    )

    assert "Spread filter status: SPREAD_TOO_HIGH" in output
    assert "Spread allowed: False" in output
    assert "Trade executed or blocked: Blocked / No trade" in output


def test_demo_mode_with_unknown_spread_uses_profile_behavior() -> None:
    apex_output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T14:00:00Z",
    )
    spot_output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--session-time",
        "2026-06-24T14:00:00Z",
    )

    assert "Spread filter status: SPREAD_UNKNOWN" in apex_output
    assert "Spread allowed: True" in apex_output
    assert "Spread filter status: SPREAD_UNKNOWN" in spot_output
    assert "Spread allowed: False" in spot_output


def test_backtest_mode_with_spread_runs_without_crashing() -> None:
    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--spread",
        "1.5",
    )

    assert "AI Trader Backtest" in output
    assert "Scenario: bullish" in output


def test_output_contains_spread_filter_information() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--session-time",
        "2026-06-24T14:00:00Z",
        "--spread",
        "2.0",
    )

    assert "Spread filter status" in output
    assert "Current spread" in output
    assert "Spread allowed" in output


def test_invalid_spread_does_not_crash() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--spread",
        "not-a-number",
    )

    assert "Warning" in output
    assert "Invalid --spread value" in output
    assert "AI Trader Paper Trading Demo" in output
