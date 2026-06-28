"""Backtest quality checker for research safety.

This module evaluates whether a backtest result has enough quality to be
considered promising for further paper testing. It never approves live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.backtest_runner import BacktestResult
from storage.performance_report import PerformanceReport


@dataclass
class BacktestQualityConfig:
    """Thresholds used to evaluate backtest quality."""

    min_iterations: int = 30
    min_executed_trades: int = 20
    min_win_rate: float = 50.0
    max_drawdown_allowed: float = 10.0
    min_profit_factor: float = 1.2
    require_positive_pnl: bool = True


@dataclass
class BacktestQualityResult:
    """Outcome of quality validation for one backtest run."""

    passed: bool
    grade: str
    score: float
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class BacktestQualityChecker:
    """Apply conservative quality rules to backtest and performance outputs."""

    def evaluate(
        self,
        backtest_result: BacktestResult,
        performance_report: PerformanceReport,
        config: BacktestQualityConfig,
    ) -> BacktestQualityResult:
        """Evaluate backtest quality using safe minimum thresholds."""
        warnings: list[str] = []
        failures: list[str] = []
        notes: list[str] = []

        if backtest_result.total_iterations < config.min_iterations:
            failures.append("Not enough iterations for reliable evaluation")
            notes.append("Needs more data")
            return BacktestQualityResult(
                passed=False,
                grade="INSUFFICIENT_DATA",
                score=self._compute_score(warnings, failures),
                warnings=warnings,
                failures=failures,
                notes=notes,
            )

        if performance_report.executed_trades < config.min_executed_trades:
            failures.append("Not enough executed trades for reliable evaluation")
            notes.append("Needs more data")
            return BacktestQualityResult(
                passed=False,
                grade="INSUFFICIENT_DATA",
                score=self._compute_score(warnings, failures),
                warnings=warnings,
                failures=failures,
                notes=notes,
            )

        if config.require_positive_pnl and backtest_result.total_pnl < 0:
            failures.append("Total PnL is negative")

        if performance_report.win_rate < config.min_win_rate:
            failures.append("Win rate is below required minimum")

        if performance_report.max_drawdown > config.max_drawdown_allowed:
            failures.append("Max drawdown exceeds allowed threshold")

        if performance_report.profit_factor < config.min_profit_factor:
            failures.append("Profit factor is below required minimum")

        # Warnings capture near-threshold values even when checks pass.
        if performance_report.win_rate < config.min_win_rate + 5.0:
            warnings.append("Win rate is only slightly above minimum")

        if performance_report.profit_factor < config.min_profit_factor + 0.2:
            warnings.append("Profit factor margin is thin")

        if performance_report.max_drawdown > config.max_drawdown_allowed * 0.8:
            warnings.append("Drawdown is close to maximum allowed")

        score = self._compute_score(warnings, failures)

        if failures:
            notes.append("Not ready for live trading")
            grade = "FAILED"
            passed = False
        else:
            passed = True
            if score >= 90.0:
                grade = "EXCELLENT"
                notes.append("Good research result, still not live-ready")
            else:
                grade = "GOOD"
                notes.append("Promising but needs paper testing")

        if grade in {"GOOD", "EXCELLENT"} and warnings:
            notes.append("Risk controls should stay conservative")

        return BacktestQualityResult(
            passed=passed,
            grade=grade,
            score=score,
            warnings=warnings,
            failures=failures,
            notes=notes,
        )

    def explain(self, result: BacktestQualityResult) -> str:
        """Return a readable quality summary with recommendation."""
        failures_text = "; ".join(result.failures) if result.failures else "None"
        warnings_text = "; ".join(result.warnings) if result.warnings else "None"
        notes_text = "; ".join(result.notes) if result.notes else "None"

        recommendation = self._recommendation_from_result(result)

        return (
            f"Backtest quality | grade: {result.grade} | score: {result.score:.1f} | "
            f"passed: {result.passed} | failures: {failures_text} | "
            f"warnings: {warnings_text} | notes: {notes_text} | "
            f"recommendation: {recommendation}"
        )

    def _compute_score(self, warnings: list[str], failures: list[str]) -> float:
        """Compute a simple 0-100 score from warning/failure counts."""
        score = 100.0
        score -= float(len(warnings) * 8)
        score -= float(len(failures) * 25)
        return max(0.0, min(100.0, score))

    def _recommendation_from_result(self, result: BacktestQualityResult) -> str:
        """Map result to one required recommendation sentence."""
        if result.grade == "INSUFFICIENT_DATA":
            return "Needs more data"
        if not result.passed:
            return "Not ready for live trading"
        if result.grade == "GOOD":
            return "Promising but needs paper testing"
        return "Good research result, still not live-ready"
