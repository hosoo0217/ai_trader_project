from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_demo_mode_with_show_trace_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-trace")

    assert "AI Trader Paper Trading Demo" in output
    assert "Decision Trace" in output


def test_demo_trace_output_contains_known_step_name() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex", "--show-trace")

    assert "Decision Trace" in output
    assert ("SAFETY_GATE" in output) or ("DECISION_ENGINE" in output)


def test_demo_mode_without_show_trace_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "apex")

    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_blocked_trade_trace_output_is_readable() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish", "--profile", "safe", "--show-trace")

    assert "Decision Trace" in output
    assert "Final action:" in output
    assert "Blocking reasons:" in output


def test_backtest_mode_with_show_trace_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex", "--show-trace")

    assert "AI Trader Backtest" in output
    assert "Decision Trace" in output
