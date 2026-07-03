"""Tests for the diagnostic-only bulk Sierra backtest runner."""

from __future__ import annotations

import json
from subprocess import CompletedProcess

from analysis.bulk_sierra_backtest_runner import (
    BulkSierraBacktestConfig,
    build_backtest_commands,
    format_bulk_backtest_text,
    run_bulk_sierra_backtests,
)


def _completed(command: list[str]) -> CompletedProcess:
    stdout = "\n".join(
        [
            "AI Trader Backtest",
            "- Total iterations: 6",
            "- Trades executed: 0",
            "- Total PnL: 0.00",
            "Order Flow Confirmation A/B Diagnostic",
        ]
    )
    return CompletedProcess(command, 0, stdout=stdout, stderr="")


def test_builds_existing_backtest_cli_commands_for_both_sides(tmp_path) -> None:
    config = BulkSierraBacktestConfig(
        market_csv=tmp_path / "market.csv",
        footprint_csv=tmp_path / "footprint.csv",
        timeframe="10m",
        max_iterations=6,
        profile="apex",
        side="both",
        output_dir=tmp_path / "out",
    )

    commands = build_backtest_commands(config)

    assert len(commands) == 2
    assert "--mode" in commands[0]
    assert "backtest" in commands[0]
    assert "--scenario" in commands[0]
    assert "bullish" in commands[0]
    assert "--profile" in commands[0]
    assert "apex" in commands[0]
    assert "--backtest-market-csv" in commands[0]
    assert str(config.market_csv) in commands[0]
    assert "--orderflow-csv" in commands[0]
    assert str(config.footprint_csv) in commands[0]
    assert "--backtest-max-iterations" in commands[0]
    assert "6" in commands[0]
    assert "--simulate-orderflow-confirmation-ab" in commands[0]
    assert "--backtest-trace-dir" in commands[0]
    assert str(config.output_dir / "bullish") in commands[0]
    assert "bearish" in commands[1]
    assert str(config.output_dir / "bearish") in commands[1]


def test_runner_writes_json_and_text_summary_under_output_dir(tmp_path) -> None:
    market_csv = tmp_path / "market.csv"
    footprint_csv = tmp_path / "footprint.csv"
    output_dir = tmp_path / "bulk_out"
    market_csv.write_text("Date,Time,Open,High,Low,Last\n")
    footprint_csv.write_text("DateTime,BarIndex,Price,BidVolume,AskVolume\n")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> CompletedProcess:
        calls.append(command)
        return _completed(command)

    report = run_bulk_sierra_backtests(
        BulkSierraBacktestConfig(
            market_csv=market_csv,
            footprint_csv=footprint_csv,
            timeframe="5m",
            max_iterations=24,
            profile="spot",
            side="both",
            output_dir=output_dir,
        ),
        run_command=fake_run,
    )

    payload = json.loads((output_dir / "bulk_sierra_backtest_summary.json").read_text())
    text = (output_dir / "bulk_sierra_backtest_summary.md").read_text()

    assert len(calls) == 2
    assert report.total_runs == 2
    assert report.completed_runs == 2
    assert payload["timeframe"] == "5m"
    assert payload["max_iterations"] == 24
    assert payload["profile"] == "spot"
    assert payload["total_runs"] == 2
    assert payload["runs"][0]["side"] == "bullish"
    assert payload["runs"][0]["output_dir"].endswith("bullish")
    assert payload["runs"][1]["output_dir"].endswith("bearish")
    assert "# Bulk Sierra Backtest Diagnostic Summary" in text
    assert "- Timeframe: 5m" in text
    assert "- Profile: spot" in text
    assert "| bullish | 0 |" in text
    assert (output_dir / "bullish" / "bulk_sierra_backtest_5m_bullish_stdout.txt").exists()
    assert (output_dir / "bearish" / "bulk_sierra_backtest_5m_bearish_stdout.txt").exists()


def test_runner_supports_single_side_without_running_other_side(tmp_path) -> None:
    market_csv = tmp_path / "market.csv"
    footprint_csv = tmp_path / "footprint.csv"
    output_dir = tmp_path / "bulk_out"
    market_csv.write_text("Date,Time,Open,High,Low,Last\n")
    footprint_csv.write_text("DateTime,BarIndex,Price,BidVolume,AskVolume\n")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> CompletedProcess:
        calls.append(command)
        return _completed(command)

    report = run_bulk_sierra_backtests(
        BulkSierraBacktestConfig(
            market_csv=market_csv,
            footprint_csv=footprint_csv,
            timeframe="1m",
            max_iterations=50,
            profile="safe",
            side="bearish",
            output_dir=output_dir,
        ),
        run_command=fake_run,
    )

    assert len(calls) == 1
    assert "bearish" in calls[0]
    assert "--profile" in calls[0]
    assert "safe" in calls[0]
    assert str(output_dir / "bearish") in calls[0]
    assert report.runs[0].side == "bearish"
    assert report.runs[0].output_dir.endswith("bearish")


def test_runner_rejects_missing_explicit_input_paths(tmp_path) -> None:
    config = BulkSierraBacktestConfig(
        market_csv=tmp_path / "missing_market.csv",
        footprint_csv=tmp_path / "missing_footprint.csv",
        timeframe="10m",
        max_iterations=6,
        profile="apex",
        side="bullish",
        output_dir=tmp_path / "out",
    )

    try:
        run_bulk_sierra_backtests(config, run_command=lambda command, **kwargs: _completed(command))
    except FileNotFoundError as exc:
        assert "missing_market.csv" in str(exc)
    else:
        raise AssertionError("Expected missing explicit CSV path to fail safely")


def test_format_bulk_backtest_text_states_diagnostic_only(tmp_path) -> None:
    market_csv = tmp_path / "market.csv"
    footprint_csv = tmp_path / "footprint.csv"
    output_dir = tmp_path / "bulk_out"
    market_csv.write_text("Date,Time,Open,High,Low,Last\n")
    footprint_csv.write_text("DateTime,BarIndex,Price,BidVolume,AskVolume\n")

    report = run_bulk_sierra_backtests(
        BulkSierraBacktestConfig(
            market_csv=market_csv,
            footprint_csv=footprint_csv,
            timeframe="10m",
            max_iterations=6,
            profile="apex",
            side="bullish",
            output_dir=output_dir,
        ),
        run_command=lambda command, **kwargs: _completed(command),
    )

    text = format_bulk_backtest_text(report)

    assert "Diagnostic-only" in text
    assert "No strategy, risk, broker, live, or paper trading behavior was changed." in text


def test_runner_rejects_invalid_profile(tmp_path) -> None:
    config = BulkSierraBacktestConfig(
        market_csv=tmp_path / "market.csv",
        footprint_csv=tmp_path / "footprint.csv",
        timeframe="10m",
        max_iterations=6,
        profile="aggressive",
        side="bullish",
        output_dir=tmp_path / "out",
    )

    try:
        build_backtest_commands(config)
    except ValueError as exc:
        assert "profile must be apex, spot, or safe" in str(exc)
    else:
        raise AssertionError("Expected invalid profile to fail safely")
