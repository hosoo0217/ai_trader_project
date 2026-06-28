from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_backtest_bullish_output_contains_backtest_quality() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "Backtest Quality Check" in output


def test_backtest_weak_output_contains_insufficient_data_or_quality_result() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "weak")
    assert ("INSUFFICIENT_DATA" in output) or ("Backtest Quality Check" in output)


def test_backtest_all_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "all")
    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output


def test_output_contains_research_only() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "research-only" in output


def test_zero_trade_backtest_does_not_crash() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "weak")
    assert "AI Trader Backtest" in output
    assert "Backtest Quality Check" in output
