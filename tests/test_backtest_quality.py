"""Unit tests for backtest quality checks."""

from core.backtest_runner import BacktestResult
from storage.backtest_quality import BacktestQualityChecker, BacktestQualityConfig
from storage.performance_report import PerformanceReport


def make_backtest_result(**overrides) -> BacktestResult:
    base = BacktestResult(
        completed=True,
        status="COMPLETED",
        total_iterations=40,
        trades_executed=25,
        trades_blocked=15,
        final_balance=10020.0,
        total_pnl=20.0,
        reasons=["ok"],
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def make_performance_report(**overrides) -> PerformanceReport:
    base = PerformanceReport(
        total_trades=40,
        executed_trades=25,
        blocked_trades=15,
        wins=14,
        losses=8,
        breakeven=3,
        win_rate=56.0,
        total_pnl=20.0,
        average_win=4.0,
        average_loss=-2.0,
        profit_factor=1.5,
        best_trade=8.0,
        worst_trade=-4.0,
        max_drawdown=6.0,
        notes=["ok"],
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_insufficient_iterations_returns_insufficient_data() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(total_iterations=10),
        make_performance_report(),
        BacktestQualityConfig(min_iterations=30),
    )

    assert result.grade == "INSUFFICIENT_DATA"
    assert result.passed is False


def test_insufficient_trades_returns_insufficient_data() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(executed_trades=5),
        BacktestQualityConfig(min_executed_trades=20),
    )

    assert result.grade == "INSUFFICIENT_DATA"
    assert result.passed is False


def test_negative_pnl_fails() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(total_pnl=-5.0),
        make_performance_report(total_pnl=-5.0),
        BacktestQualityConfig(require_positive_pnl=True),
    )

    assert result.grade == "FAILED"
    assert any("Total PnL" in failure for failure in result.failures)


def test_low_win_rate_fails() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(win_rate=40.0),
        BacktestQualityConfig(min_win_rate=50.0),
    )

    assert result.grade == "FAILED"
    assert any("Win rate" in failure for failure in result.failures)


def test_high_drawdown_fails() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(max_drawdown=12.0),
        BacktestQualityConfig(max_drawdown_allowed=10.0),
    )

    assert result.grade == "FAILED"
    assert any("drawdown" in failure.lower() for failure in result.failures)


def test_low_profit_factor_fails() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(profit_factor=1.0),
        BacktestQualityConfig(min_profit_factor=1.2),
    )

    assert result.grade == "FAILED"
    assert any("Profit factor" in failure for failure in result.failures)


def test_good_report_passes() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(),
        BacktestQualityConfig(),
    )

    assert result.passed is True
    assert result.grade in {"GOOD", "EXCELLENT"}
    assert 0.0 <= result.score <= 100.0


def test_explain_returns_readable_text() -> None:
    checker = BacktestQualityChecker()
    result = checker.evaluate(
        make_backtest_result(),
        make_performance_report(),
        BacktestQualityConfig(),
    )

    text = checker.explain(result)

    assert "grade" in text.lower()
    assert "score" in text.lower()
    assert "recommendation" in text.lower()
