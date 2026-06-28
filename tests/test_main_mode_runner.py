from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_demo_bullish_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish")
    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_demo_all_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "all")
    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output


def test_backtest_bullish_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "AI Trader Backtest" in output
    assert "Scenario: bullish" in output


def test_backtest_bearish_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bearish")
    assert "AI Trader Backtest" in output
    assert "Scenario: bearish" in output


def test_backtest_weak_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "weak")
    assert "AI Trader Backtest" in output
    assert "Scenario: weak" in output


def test_backtest_mode_prints_backtest_title() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "AI Trader Backtest" in output


def test_demo_mode_prints_demo_title() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish")
    assert "AI Trader Paper Trading Demo" in output


def test_invalid_mode_is_rejected_safely() -> None:
    output = _run_main("--mode", "invalid", "--scenario", "bullish")
    assert "Invalid mode" in output


def test_invalid_scenario_is_rejected_safely() -> None:
    output = _run_main("--mode", "demo", "--scenario", "invalid")
    assert "Invalid scenario" in output
