"""Diagnostic-only bulk Sierra backtest runner.

This module is a wrapper around the existing ``main.py --mode backtest`` path.
It does not implement strategy logic, risk logic, broker behavior, live trading,
paper trading, or Order Flow confirmation enforcement.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any


RunCommand = Callable[..., CompletedProcess]


@dataclass(frozen=True)
class BulkSierraBacktestConfig:
    """Explicit inputs for a diagnostic bulk Sierra backtest run."""

    market_csv: str | Path
    footprint_csv: str | Path
    timeframe: str
    max_iterations: int
    profile: str
    side: str
    output_dir: str | Path


@dataclass(frozen=True)
class BulkSierraBacktestRunResult:
    """Summary for one side-specific diagnostic run."""

    side: str
    output_dir: str
    returncode: int
    command: list[str]
    stdout_path: str
    stderr_path: str
    total_iterations: int | None = None
    trades_executed: int | None = None
    total_pnl: float | None = None


@dataclass(frozen=True)
class BulkSierraBacktestReport:
    """Summary report for a diagnostic bulk Sierra backtest run."""

    market_csv: str
    footprint_csv: str
    timeframe: str
    max_iterations: int
    profile: str
    side: str
    output_dir: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    diagnostic_only: bool
    orderflow_ab_diagnostic_requested: bool
    runs: list[BulkSierraBacktestRunResult]


def build_backtest_commands(config: BulkSierraBacktestConfig) -> list[list[str]]:
    """Build supported existing CLI commands without running them."""
    sides = _sides_for(config.side)
    profile = _validate_profile(config.profile)
    commands: list[list[str]] = []
    main_path = str(_main_py_path())

    for side in sides:
        side_output_dir = str(_side_output_dir(config.output_dir, side))
        commands.append(
            [
                sys.executable,
                main_path,
                "--mode",
                "backtest",
                "--scenario",
                side,
                "--profile",
                profile,
                "--backtest-market-csv",
                str(config.market_csv),
                "--orderflow-csv",
                str(config.footprint_csv),
                "--backtest-max-iterations",
                str(config.max_iterations),
                "--backtest-trace-dir",
                side_output_dir,
                "--simulate-orderflow-confirmation-ab",
            ]
        )

    return commands


def run_bulk_sierra_backtests(
    config: BulkSierraBacktestConfig,
    run_command: RunCommand = subprocess.run,
) -> BulkSierraBacktestReport:
    """Run existing backtest CLI commands and write diagnostic summaries."""
    market_path = Path(config.market_csv)
    footprint_path = Path(config.footprint_csv)
    output_dir = Path(config.output_dir)
    profile = _validate_profile(config.profile)

    _require_existing_file(market_path)
    _require_existing_file(footprint_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_results: list[BulkSierraBacktestRunResult] = []
    for command in build_backtest_commands(config):
        side = _command_value(command, "--scenario") or "unknown"
        side_output_dir = _side_output_dir(output_dir, side)
        side_output_dir.mkdir(parents=True, exist_ok=True)
        completed = run_command(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        stdout_path = side_output_dir / f"bulk_sierra_backtest_{config.timeframe}_{side}_stdout.txt"
        stderr_path = side_output_dir / f"bulk_sierra_backtest_{config.timeframe}_{side}_stderr.txt"
        stdout_path.write_text(stdout)
        stderr_path.write_text(stderr)

        run_results.append(
            BulkSierraBacktestRunResult(
                side=side,
                output_dir=str(side_output_dir),
                returncode=int(completed.returncode),
                command=list(command),
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
                total_iterations=_parse_int_metric(stdout, "Total iterations"),
                trades_executed=_parse_int_metric(stdout, "Trades executed"),
                total_pnl=_parse_float_metric(stdout, "Total PnL"),
            )
        )

    report = BulkSierraBacktestReport(
        market_csv=str(market_path),
        footprint_csv=str(footprint_path),
        timeframe=str(config.timeframe),
        max_iterations=int(config.max_iterations),
        profile=profile,
        side=str(config.side),
        output_dir=str(output_dir),
        total_runs=len(run_results),
        completed_runs=sum(1 for result in run_results if result.returncode == 0),
        failed_runs=sum(1 for result in run_results if result.returncode != 0),
        diagnostic_only=True,
        orderflow_ab_diagnostic_requested=True,
        runs=run_results,
    )

    (output_dir / "bulk_sierra_backtest_summary.json").write_text(
        json.dumps(report_to_dict(report), indent=2)
    )
    (output_dir / "bulk_sierra_backtest_summary.md").write_text(format_bulk_backtest_text(report))
    return report


def format_bulk_backtest_text(report: BulkSierraBacktestReport) -> str:
    """Format a Markdown summary for human review."""
    lines = [
        "# Bulk Sierra Backtest Diagnostic Summary",
        "",
        "Diagnostic-only wrapper around the existing backtest CLI.",
        "No strategy, risk, broker, live, or paper trading behavior was changed.",
        "",
        f"- Market CSV: {report.market_csv}",
        f"- Footprint CSV: {report.footprint_csv}",
        f"- Timeframe: {report.timeframe}",
        f"- Max iterations: {report.max_iterations}",
        f"- Profile: {report.profile}",
        f"- Requested side: {report.side}",
        f"- Total runs: {report.total_runs}",
        f"- Completed runs: {report.completed_runs}",
        f"- Failed runs: {report.failed_runs}",
        f"- Order Flow A/B diagnostic requested: {report.orderflow_ab_diagnostic_requested}",
        "",
        "| Side | Return code | Iterations | Trades executed | Total PnL | Output dir | Stdout | Stderr |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]

    for result in report.runs:
        lines.append(
            "| "
            f"{result.side} | "
            f"{result.returncode} | "
            f"{_metric_text(result.total_iterations)} | "
            f"{_metric_text(result.trades_executed)} | "
            f"{_metric_text(result.total_pnl)} | "
            f"{result.output_dir} | "
            f"{result.stdout_path} | "
            f"{result.stderr_path} |"
        )

    lines.append("")
    lines.append("This report does not approve live trading, paper trading, or strategy enforcement.")
    lines.append("")
    return "\n".join(lines)


def report_to_dict(report: BulkSierraBacktestReport) -> dict[str, Any]:
    """Convert a report to JSON-friendly primitives."""
    return asdict(report)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for explicit diagnostic bulk Sierra backtests."""
    parser = argparse.ArgumentParser(description="Diagnostic-only bulk Sierra backtest runner.")
    parser.add_argument("--market-csv", required=True)
    parser.add_argument("--footprint-csv", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--max-iterations", type=_positive_int, required=True)
    parser.add_argument("--profile", choices=["apex", "spot", "safe"], required=True)
    parser.add_argument("--side", choices=["bullish", "bearish", "both"], required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)

    report = run_bulk_sierra_backtests(
        BulkSierraBacktestConfig(
            market_csv=args.market_csv,
            footprint_csv=args.footprint_csv,
            timeframe=args.timeframe,
            max_iterations=args.max_iterations,
            profile=args.profile,
            side=args.side,
            output_dir=args.output_dir,
        )
    )
    print(format_bulk_backtest_text(report))
    return 0 if report.failed_runs == 0 else 1


def _sides_for(side: str) -> list[str]:
    normalized = str(side or "").strip().lower()
    if normalized == "both":
        return ["bullish", "bearish"]
    if normalized in {"bullish", "bearish"}:
        return [normalized]
    raise ValueError("side must be bullish, bearish, or both")


def _validate_profile(profile: str) -> str:
    normalized = str(profile or "").strip().lower()
    if normalized in {"apex", "spot", "safe"}:
        return normalized
    raise ValueError("profile must be apex, spot, or safe")


def _side_output_dir(output_dir: str | Path, side: str) -> Path:
    return Path(output_dir) / str(side).strip().lower()


def _require_existing_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Explicit CSV path not found: {path}")


def _main_py_path() -> Path:
    return Path(__file__).resolve().parents[1] / "main.py"


def _command_value(command: list[str], flag: str) -> str | None:
    try:
        index = command.index(flag)
    except ValueError:
        return None
    value_index = index + 1
    if value_index >= len(command):
        return None
    return command[value_index]


def _parse_int_metric(text: str, label: str) -> int | None:
    value = _parse_metric(text, label)
    if value is None:
        return None
    return int(float(value))


def _parse_float_metric(text: str, label: str) -> float | None:
    value = _parse_metric(text, label)
    if value is None:
        return None
    return float(value)


def _parse_metric(text: str, label: str) -> str | None:
    pattern = rf"- {re.escape(label)}:\s*(-?\d+(?:\.\d+)?)"
    match = re.search(pattern, text)
    if match is None:
        return None
    return match.group(1)


def _metric_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
