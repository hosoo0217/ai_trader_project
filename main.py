import argparse
from pathlib import Path

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.backtest_runner import BacktestConfig, BacktestRunner
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.performance_report import PerformanceReporter
from storage.trade_journal import TradeJournal


def _load_candles(path: Path) -> pd.DataFrame:
    """Load sample candles and fall back to a safe empty frame if needed."""
    try:
        candles = pd.read_csv(path)
    except Exception:
        candles = pd.DataFrame(columns=["time", "open", "high", "low", "close"])

    required_columns = {"time", "open", "high", "low", "close"}
    if not required_columns.issubset(candles.columns):
        for column in required_columns:
            if column not in candles.columns:
                candles[column] = 0.0

    return candles


def _build_parser() -> argparse.ArgumentParser:
    """Create a small CLI parser for demo and backtest modes."""
    parser = argparse.ArgumentParser(description="Run the AI Trader paper-trading and backtest modes")
    parser.add_argument(
        "--mode",
        default="demo",
        help="Choose execution mode: demo or backtest",
    )
    parser.add_argument(
        "--scenario",
        default="weak",
        help="Choose which sample scenario to run (bullish, bearish, weak, or all)",
    )
    return parser


def _get_scenario_data_path(name: str) -> Path:
    """Resolve scenario name to a sample data file path."""
    scenario_files = {
        "bullish": "bullish_sample_xauusd.csv",
        "bearish": "bearish_sample_xauusd.csv",
        "weak": "weak_sample_xauusd.csv",
    }
    return Path(__file__).resolve().parent / "data" / scenario_files.get(name, "weak_sample_xauusd.csv")


def _print_performance_report(journal: TradeJournal) -> None:
    """Print a readable performance report from journal entries."""
    performance = PerformanceReporter().generate_report(journal)

    print("\nPerformance Report")
    print(f"- Total trades: {performance.total_trades}")
    print(f"- Executed trades: {performance.executed_trades}")
    print(f"- Blocked trades: {performance.blocked_trades}")
    print(f"- Wins: {performance.wins}")
    print(f"- Losses: {performance.losses}")
    print(f"- Win rate: {performance.win_rate:.2f}%")
    print(f"- Total PnL: {performance.total_pnl:.2f}")
    if performance.profit_factor == float("inf"):
        print("- Profit factor: INF")
    else:
        print(f"- Profit factor: {performance.profit_factor:.2f}")
    print(f"- Max drawdown: {performance.max_drawdown:.2f}")


def _run_demo_scenario(name: str) -> None:
    """Run one demo scenario and print the results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    data_path = _get_scenario_data_path(name)
    if not data_path.exists():
        print(f"- File not found: {data_path.name}")
        print("- Safe fallback: no trade")
        return

    candles = _load_candles(data_path)

    journal = TradeJournal()
    reviewer = TradeReviewer()
    flow = PaperTradingFlow()
    flow_config = PaperTradingFlowConfig()

    result = flow.run_single_timeframe(
        candles,
        flow_config,
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        PaperBrokerState(),
        journal,
    )

    print("\nMarket result")
    print(f"- Market bias: {result.market_bias}")
    print(f"- Final decision: {result.decision_action}")
    print(f"- Trade executed or blocked: {'Executed' if result.trade_executed else 'Blocked / No trade'}")
    print(f"- Paper balance: {result.balance if result.balance is not None else 'N/A'}")

    if result.reasons:
        print(f"- Reasons: {'; '.join(result.reasons)}")

    print("\nJournal summary")
    summary = journal.summarize()
    print(f"- Entries: {summary['total_entries']}")
    print(f"- Executed trades: {summary['executed_trades']}")
    print(f"- Blocked trades: {summary['blocked_trades']}")
    print(f"- Total PnL: {summary['total_pnl']:.2f}")

    print("\nAI Coach review")
    if journal.get_all_entries():
        for review in reviewer.review_journal(journal):
            print(f"- {review.trade_id}: {review.grade}")
            print(f"  Summary: {review.summary}")
            print(f"  Lesson: {review.lesson}")
    else:
        print("- No journal entries were recorded.")

    _print_performance_report(journal)

    print("\nFlow explanation")
    print(f"- {flow.explain(result)}")


def _run_backtest_scenario(name: str) -> None:
    """Run one backtest scenario and print aggregate results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    data_path = _get_scenario_data_path(name)
    if not data_path.exists():
        print(f"- File not found: {data_path.name}")
        print("- Safe fallback: no backtest run")
        return

    candles = _load_candles(data_path)
    journal = TradeJournal()
    broker_state = PaperBrokerState()
    runner = BacktestRunner()
    result = runner.run(
        candles,
        BacktestConfig(symbol="XAUUSD", timeframe="M5", window_size=60, step_size=5),
        PaperTradingFlowConfig(simulate_exit=True),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        CapitalProtectionConfig(),
        CapitalProtectionState(),
        PaperBrokerConfig(),
        broker_state,
        RiskEngineConfig(account_balance=broker_state.balance),
        journal,
    )

    print("\nAI Trader Backtest")
    print(f"- Scenario: {name}")
    print(f"- Total iterations: {result.total_iterations}")
    print(f"- Trades executed: {result.trades_executed}")
    print(f"- Trades blocked: {result.trades_blocked}")
    print(f"- Final balance: {result.final_balance:.2f}")
    print(f"- Total PnL: {result.total_pnl:.2f}")

    _print_performance_report(journal)

    print("\nBacktest explanation")
    print(f"- {runner.explain(result)}")


def main(args: list[str] | None = None) -> None:
    """Run demo or backtest mode using research-only modules."""
    parser = _build_parser()
    if args is None:
        parsed_args, _ = parser.parse_known_args()
    else:
        parsed_args, _ = parser.parse_known_args(args)

    mode = parsed_args.mode.lower().strip() if parsed_args.mode else "demo"
    scenario = parsed_args.scenario.lower().strip() if parsed_args.scenario else "weak"

    if mode not in {"demo", "backtest"}:
        print(f"Invalid mode: {mode}")
        print("Safe fallback: choose --mode demo or --mode backtest")
        return

    if mode == "demo":
        print("AI Trader Paper Trading Demo")
        print("=" * 32)
    else:
        print("AI Trader Backtest")
        print("=" * 18)

    if scenario not in {"bullish", "bearish", "weak", "all"}:
        print(f"Invalid scenario: {scenario}")
        print("Safe fallback: choose bullish, bearish, weak, or all")
        return

    if scenario == "all":
        for scenario_name in ["bullish", "bearish", "weak"]:
            if mode == "demo":
                _run_demo_scenario(scenario_name)
            else:
                _run_backtest_scenario(scenario_name)
            print("\n" + "=" * 40)
            print()
        return

    if mode == "demo":
        _run_demo_scenario(scenario)
    else:
        _run_backtest_scenario(scenario)


if __name__ == "__main__":
    main()
