from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

import main
from core.backtest_runner import BacktestResult


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def _write_sierra_bar_summary_csv(path: Path, rows: int = 75) -> None:
    lines = [
        "Date, Time, Open, High, Low, Last, Volume, # of Trades, OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume, Open, High, Low, Last, Delta, Finish, Volume, Volume / Sec"
    ]
    for index in range(rows):
        open_price = 4160.0 + index
        high_price = open_price + 4.0
        low_price = open_price - 3.0
        close_price = open_price + 1.5
        bid_volume = 100 + index
        ask_volume = 120 + index
        delta = ask_volume - bid_volume
        lines.append(
            "2026-6-21, "
            f"18:{index % 60:02d}:00.000000, "
            f"{open_price:.1f}, {high_price:.1f}, {low_price:.1f}, {close_price:.1f}, "
            f"{bid_volume + ask_volume}, 50, 0, 0, 0, {bid_volume}, {ask_volume}, "
            f"{open_price:.1f}, {high_price:.1f}, {low_price:.1f}, {close_price:.1f}, "
            f"{delta}, 0, {bid_volume + ask_volume}, 1"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


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


def test_help_includes_backtest_market_csv() -> None:
    help_text = main._build_parser().format_help()

    assert "--backtest-market-csv" in help_text
    assert "market candles" in help_text
    assert "research-only backtests" in help_text


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


def test_sierra_bar_summary_loads_as_backtest_market_candles(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=3)

    result = main._load_backtest_market_candles_from_csv(str(csv_path))

    assert result.candles is not None
    assert len(result.candles) == 3
    assert result.candles.iloc[0]["time"] == "2026-6-21 18:00:00.000000"
    assert result.candles.iloc[0]["open"] == 4160.0
    assert result.candles.iloc[0]["close"] == 4161.5
    assert "BAR_SUMMARY" in str(result.source)


def test_backtest_market_csv_can_produce_multiple_iterations(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=75)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--backtest-market-csv",
        str(csv_path),
        "--backtest-max-iterations",
        "3",
    )

    assert "- Backtest market candles:" in output
    assert "- Total iterations: 3" in output


def test_missing_backtest_market_csv_fails_safely(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"

    output = _run_main("--mode", "backtest", "--backtest-market-csv", str(missing_path))

    assert "Backtest market CSV not found" in output
    assert "Safe fallback: no backtest run" in output
    assert "- Total iterations:" not in output


def test_default_backtest_scenario_behavior_does_not_use_market_csv() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")

    assert "- Total iterations: 1" in output
    assert "- Backtest market candles:" not in output


def test_orderflow_csv_does_not_replace_backtest_market_candles(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=75)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        str(csv_path),
        "--backtest-max-iterations",
        "3",
    )

    assert "Order Flow Data Quality" in output
    assert "- Total iterations: 1" in output
    assert "- Backtest market candles:" not in output
