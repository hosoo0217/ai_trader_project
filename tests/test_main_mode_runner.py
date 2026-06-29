from contextlib import redirect_stdout
from io import StringIO

import pytest

import main
from core.backtest_runner import BacktestResult


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


def test_help_includes_backtest_max_iterations() -> None:
    help_text = main._build_parser().format_help()

    assert "--backtest-max-iterations" in help_text
    assert "rolling backtest iterations" in help_text


def test_backtest_max_iterations_is_passed_to_config(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, int | None] = {}

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        seen["max_iterations"] = backtest_config.max_iterations
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=3,
            trades_executed=0,
            trades_blocked=3,
            final_balance=10000.0,
            total_pnl=0.0,
            reasons=["Backtest completed"],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--backtest-max-iterations", "3")

    assert "AI Trader Backtest" in output
    assert seen["max_iterations"] == 3


def test_backtest_max_iterations_rejects_zero() -> None:
    with pytest.raises(SystemExit):
        main.main(["--mode", "backtest", "--backtest-max-iterations", "0"])


def test_backtest_max_iterations_rejects_negative() -> None:
    with pytest.raises(SystemExit):
        main.main(["--mode", "backtest", "--backtest-max-iterations", "-1"])
