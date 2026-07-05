"""Research-only conditional cooldown A/B diagnostic.

This module reads existing per-entry replay diagnostic JSON files and writes
conditional cooldown A/B diagnostic reports.

It does not implement strategy logic, risk execution logic, broker behavior,
live trading, paper trading, MT5 login, Sierra live connections, CME live data
connections, external API calls, real orders, or Order Flow confirmation
enforcement.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConditionalCooldownConfig:
    """Explicit inputs for a research-only conditional cooldown diagnostic."""

    input_json: str | Path
    output_dir: str | Path
    dataset_name: str | None = None
    report_name: str = "conditional_cooldown_ab_diagnostic_report"


@dataclass(frozen=True)
class ConditionalCooldownABConfig:
    """Backward-compatible config alias for the research diagnostic."""

    input_json: str | Path
    output_dir: str | Path
    report_name: str = "conditional_cooldown_ab_diagnostic_report"


@dataclass(frozen=True)
class CooldownVariantMetrics:
    """Metrics for one diagnostic cooldown variant."""

    variant: str
    kept_trades: int
    blocked_trades: int
    wins: int
    losses: int
    total_pnl: float
    win_rate: float | None
    profit_factor: float | None
    max_drawdown: float
    removed_winners: int
    removed_losses: int
    removed_pnl: float
    largest_loss_cluster_count: int
    largest_loss_cluster_pnl: float


@dataclass(frozen=True)
class ConditionalCooldownReport:
    """Research-only A/B report for conditional cooldown variants."""

    input_json: str
    output_dir: str
    dataset_name: str
    report_name: str
    diagnostic_only: bool
    orderflow_enforcement: bool
    variants: list[CooldownVariantMetrics]


Selector = Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]


def run_conditional_cooldown_ab_diagnostic(
    config: ConditionalCooldownConfig,
) -> ConditionalCooldownReport:
    """Run a research-only conditional cooldown A/B diagnostic."""
    input_path = Path(config.input_json)
    output_dir = Path(config.output_dir)
    _require_existing_json(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    trades = _load_executed_trade_snapshots(payload)
    dataset_name = config.dataset_name or input_path.parent.name

    variants = [
        _variant_metrics("A baseline", trades, []),
        _evaluate_variant(
            "B1 global post-loss cooldown 3",
            trades,
            lambda source: _global_post_loss_cooldown(source, cooldown=3),
        ),
        _evaluate_variant(
            "B2 global post-loss cooldown 10",
            trades,
            lambda source: _global_post_loss_cooldown(source, cooldown=10),
        ),
        _evaluate_variant(
            "C1 cooldown after two nearby losses",
            trades,
            lambda source: _two_loss_cluster_cooldown(source, cluster_gap=5, cooldown=10),
        ),
        _evaluate_variant(
            "C2 cooldown after same-direction nearby losses",
            trades,
            lambda source: _same_direction_repeated_loss_cooldown(
                source,
                cluster_gap=5,
                cooldown=10,
            ),
        ),
        _evaluate_variant(
            "C3 detected loss-cluster-zone cooldown 10",
            trades,
            lambda source: _detected_loss_cluster_zone_cooldown(
                source,
                cluster_gap=5,
                min_cluster_losses=2,
                cooldown=10,
            ),
        ),
    ]

    report = ConditionalCooldownReport(
        input_json=str(input_path),
        output_dir=str(output_dir),
        dataset_name=dataset_name,
        report_name=config.report_name,
        diagnostic_only=True,
        orderflow_enforcement=False,
        variants=variants,
    )

    json_path = output_dir / f"{config.report_name}.json"
    md_path = output_dir / f"{config.report_name}.md"

    json_path.write_text(
        json.dumps(report_to_dict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(format_conditional_cooldown_report(report), encoding="utf-8")

    return report


def run_conditional_cooldown_ab(
    config: ConditionalCooldownABConfig,
) -> ConditionalCooldownReport:
    """Backward-compatible wrapper for the research-only diagnostic."""
    return run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(
            input_json=config.input_json,
            output_dir=config.output_dir,
            report_name=config.report_name,
        )
    )


def report_to_dict(report: ConditionalCooldownReport) -> dict[str, Any]:
    """Convert a report to JSON-friendly primitives."""
    return asdict(report)


def format_conditional_cooldown_report(report: ConditionalCooldownReport) -> str:
    """Format a research-only report as Markdown."""
    lines = [
        "# Conditional Cooldown A/B Diagnostic Report",
        "",
        "## Safety scope",
        "",
        "This report is generated under an explicit output directory and is research-only.",
        "",
        "No strategy rule is changed.",
        "No risk rule is changed.",
        "No broker code is changed.",
        "No live trading, paper trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.",
        "Order Flow confirmation remains diagnostic-only and is not enforced.",
        "Order Flow fields, when present in the input, are diagnostic labels only.",
        "",
        "## Source",
        "",
        f"- Input JSON: `{report.input_json}`",
        f"- Output directory: `{report.output_dir}`",
        f"- Dataset: `{report.dataset_name}`",
        f"- Diagnostic only: {report.diagnostic_only}",
        f"- Order Flow enforcement: {report.orderflow_enforcement}",
        "",
        "## Variant definitions",
        "",
        "- A baseline: current executed trades.",
        "- B1 global post-loss cooldown 3: skip trades within three iterations after a kept loss.",
        "- B2 global post-loss cooldown 10: skip trades within ten iterations after a kept loss.",
        "- C1 cooldown after two nearby losses: activate cooldown after two nearby kept losses.",
        "- C2 cooldown after same-direction nearby losses: activate cooldown after nearby same-direction kept losses.",
        "- C3 detected loss-cluster-zone cooldown 10: post-hoc diagnostic loss-cluster zone filter.",
        "",
        "## Variant metrics",
        "",
        "| Variant | Kept | Blocked | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown | Removed wins | Removed losses | Removed PnL | Largest loss cluster | Largest loss cluster PnL |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for metric in report.variants:
        lines.append(
            f"| {metric.variant} | {metric.kept_trades} | {metric.blocked_trades} | "
            f"{metric.wins} | {metric.losses} | {metric.total_pnl:.2f} | "
            f"{_percent_text(metric.win_rate)} | {_float_text(metric.profit_factor)} | "
            f"{metric.max_drawdown:.2f} | {metric.removed_winners} | "
            f"{metric.removed_losses} | {metric.removed_pnl:.2f} | "
            f"{metric.largest_loss_cluster_count} | {metric.largest_loss_cluster_pnl:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This report identifies research candidates only.",
            "",
            "Detected loss-cluster-zone filtering is post-hoc diagnostic evidence and is not directly approved for strategy implementation.",
            "",
        ]
    )
    return "\n".join(lines)


def format_conditional_cooldown_ab_markdown(
    report: ConditionalCooldownReport,
) -> str:
    """Backward-compatible Markdown formatter alias."""
    return format_conditional_cooldown_report(report)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for research-only conditional cooldown A/B diagnostics."""
    parser = argparse.ArgumentParser(
        description="Research-only conditional cooldown A/B diagnostic."
    )
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--dataset-name")
    parser.add_argument(
        "--report-name",
        default="conditional_cooldown_ab_diagnostic_report",
    )
    args = parser.parse_args(argv)

    report = run_conditional_cooldown_ab_diagnostic(
        ConditionalCooldownConfig(
            input_json=args.input_json,
            output_dir=args.output_dir,
            dataset_name=args.dataset_name,
            report_name=args.report_name,
        )
    )
    print(format_conditional_cooldown_report(report))
    return 0


def _evaluate_variant(
    variant: str,
    trades: list[dict[str, Any]],
    selector: Selector,
) -> CooldownVariantMetrics:
    kept, removed = selector(trades)
    return _variant_metrics(variant, kept, removed)


def _variant_metrics(
    variant: str,
    kept: list[dict[str, Any]],
    removed: list[dict[str, Any]],
) -> CooldownVariantMetrics:
    pnl_values = [_pnl(trade) for trade in kept]
    wins = sum(1 for value in pnl_values if value > 0)
    losses = sum(1 for value in pnl_values if value < 0)
    gross_win = sum(value for value in pnl_values if value > 0)
    gross_loss = -sum(value for value in pnl_values if value < 0)
    profit_factor = None if gross_loss == 0 else round(gross_win / gross_loss, 10)
    win_rate = None if not kept else round(wins / len(kept), 10)
    largest_loss_count, largest_loss_pnl = _largest_loss_cluster(kept)

    return CooldownVariantMetrics(
        variant=variant,
        kept_trades=len(kept),
        blocked_trades=len(removed),
        wins=wins,
        losses=losses,
        total_pnl=round(sum(pnl_values), 10),
        win_rate=win_rate,
        profit_factor=profit_factor,
        max_drawdown=_max_drawdown_from_values(pnl_values),
        removed_winners=sum(1 for trade in removed if _pnl(trade) > 0),
        removed_losses=sum(1 for trade in removed if _pnl(trade) < 0),
        removed_pnl=round(sum(_pnl(trade) for trade in removed), 10),
        largest_loss_cluster_count=largest_loss_count,
        largest_loss_cluster_pnl=largest_loss_pnl,
    )


def _global_post_loss_cooldown(
    trades: list[dict[str, Any]],
    cooldown: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    last_loss_iteration: int | None = None

    for trade in trades:
        iteration = _iteration(trade)
        if (
            last_loss_iteration is not None
            and iteration - last_loss_iteration <= cooldown
        ):
            removed.append(trade)
            continue

        kept.append(trade)
        if _pnl(trade) < 0:
            last_loss_iteration = iteration

    return kept, removed


def _two_loss_cluster_cooldown(
    trades: list[dict[str, Any]],
    cluster_gap: int,
    cooldown: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    last_loss_iteration: int | None = None
    cooldown_until: int | None = None

    for trade in trades:
        iteration = _iteration(trade)
        if cooldown_until is not None and iteration <= cooldown_until:
            removed.append(trade)
            continue

        kept.append(trade)
        if _pnl(trade) < 0:
            if (
                last_loss_iteration is not None
                and iteration - last_loss_iteration <= cluster_gap
            ):
                cooldown_until = iteration + cooldown
            last_loss_iteration = iteration

    return kept, removed


def _same_direction_repeated_loss_cooldown(
    trades: list[dict[str, Any]],
    cluster_gap: int,
    cooldown: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    last_loss_iteration: int | None = None
    last_loss_side: str | None = None
    cooldown_until: int | None = None

    for trade in trades:
        iteration = _iteration(trade)
        if cooldown_until is not None and iteration <= cooldown_until:
            removed.append(trade)
            continue

        kept.append(trade)
        if _pnl(trade) < 0:
            side = str(trade.get("final_action", ""))
            if (
                last_loss_iteration is not None
                and iteration - last_loss_iteration <= cluster_gap
                and side == last_loss_side
            ):
                cooldown_until = iteration + cooldown
            last_loss_iteration = iteration
            last_loss_side = side

    return kept, removed


def _detected_loss_cluster_zone_cooldown(
    trades: list[dict[str, Any]],
    cluster_gap: int,
    min_cluster_losses: int,
    cooldown: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    losses = [trade for trade in trades if _pnl(trade) < 0]
    clusters: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []

    for trade in losses:
        if not current or _iteration(trade) - _iteration(current[-1]) <= cluster_gap:
            current.append(trade)
        else:
            clusters.append(current)
            current = [trade]

    if current:
        clusters.append(current)

    zones: list[tuple[int, int]] = []
    for cluster in clusters:
        if len(cluster) >= min_cluster_losses:
            start = (_iteration(cluster[1]) + 1) if len(cluster) > 1 else (_iteration(cluster[0]) + 1)
            end = _iteration(cluster[-1]) + cooldown
            zones.append((start, end))

    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []

    for trade in trades:
        iteration = _iteration(trade)
        if any(start <= iteration <= end for start, end in zones):
            removed.append(trade)
        else:
            kept.append(trade)

    return kept, removed


def _load_executed_trade_snapshots(payload: dict[str, Any]) -> list[dict[str, Any]]:
    trades = payload.get("executed_trade_replay_snapshots")
    if not isinstance(trades, list):
        raise ValueError("Input JSON must contain executed_trade_replay_snapshots list")

    normalized: list[dict[str, Any]] = []
    for index, trade in enumerate(trades):
        if not isinstance(trade, dict):
            raise ValueError(f"Snapshot at index {index} must be an object")
        _require_trade_fields(trade, index)
        normalized.append(dict(trade))

    return sorted(normalized, key=_iteration)


def _require_trade_fields(trade: dict[str, Any], index: int) -> None:
    required = ["iteration_index", "final_action", "outcome", "simulated_pnl"]
    missing = [field for field in required if field not in trade]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Snapshot at index {index} is missing required field(s): {joined}")


def _iteration(trade: dict[str, Any]) -> int:
    return int(trade["iteration_index"])


def _pnl(trade: dict[str, Any]) -> float:
    return float(trade["simulated_pnl"])


def _max_drawdown_from_values(values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return round(max_drawdown, 10)


def _largest_loss_cluster(trades: list[dict[str, Any]]) -> tuple[int, float]:
    largest_count = 0
    largest_pnl = 0.0
    current_count = 0
    current_pnl = 0.0

    for trade in trades:
        value = _pnl(trade)
        if value < 0:
            current_count += 1
            current_pnl += value
            if current_count > largest_count or (
                current_count == largest_count and current_pnl < largest_pnl
            ):
                largest_count = current_count
                largest_pnl = current_pnl
        else:
            current_count = 0
            current_pnl = 0.0

    return largest_count, round(largest_pnl, 10)


def _percent_text(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value * 100:.2f}%"


def _float_text(value: float | None) -> str:
    if value is None:
        return "inf"
    return str(round(value, 2))


def _require_existing_json(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input diagnostic JSON not found: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
