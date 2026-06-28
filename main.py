import argparse
from pathlib import Path

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
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
    """Create a small CLI parser for demo scenarios."""
    parser = argparse.ArgumentParser(description="Run the AI Trader paper-trading demo")
    parser.add_argument(
        "--scenario",
        default="weak",
        help="Choose which sample scenario to run (bullish, bearish, weak, or all)",
    )
    return parser


def _run_single_scenario(name: str) -> None:
    """Run one demo scenario and print the results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    scenario_files = {
        "bullish": "bullish_sample_xauusd.csv",
        "bearish": "bearish_sample_xauusd.csv",
        "weak": "weak_sample_xauusd.csv",
    }

    data_path = Path(__file__).resolve().parent / "data" / scenario_files.get(name, "weak_sample_xauusd.csv")
    if not data_path.exists():
        print(f"- File not found: {data_path.name}")
        print("- Safe fallback: no trade")
        return

    candles = _load_candles(data_path)

    journal = TradeJournal()
    reviewer = TradeReviewer()
    reporter = PerformanceReporter()
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

    print("\nPerformance Report")
    performance = reporter.generate_report(journal)
    print(f"- Total trades: {performance.total_trades}")
    print(f"- Executed trades: {performance.executed_trades}")
    print(f"- Blocked trades: {performance.blocked_trades}")
    print(f"- Wins: {performance.wins}")
    print(f"- Losses: {performance.losses}")
    print(f"- Win rate: {performance.win_rate:.2f}%")
    print(f"- Total PnL: {performance.total_pnl:.2f}")
    if performance.profit_factor == float('inf'):
        print("- Profit factor: INF")
    else:
        print(f"- Profit factor: {performance.profit_factor:.2f}")
    print(f"- Max drawdown: {performance.max_drawdown:.2f}")

    print("\nFlow explanation")
    print(f"- {flow.explain(result)}")


def main(args: list[str] | None = None) -> None:
    """Run a simple paper-trading demo using the research-only modules."""
    parser = _build_parser()
    if args is None:
        parsed_args, _ = parser.parse_known_args()
    else:
        parsed_args, _ = parser.parse_known_args(args)

    print("AI Trader Paper Trading Demo")
    print("=" * 32)

    scenario = parsed_args.scenario.lower().strip() if parsed_args.scenario else "weak"
    if scenario == "all":
        for scenario_name in ["bullish", "bearish", "weak"]:
            _run_single_scenario(scenario_name)
            print()
        return

    if scenario not in {"bullish", "bearish", "weak"}:
        print(f"Invalid scenario: {scenario}")
        print("Safe fallback: no trade")
        return

    _run_single_scenario(scenario)


if __name__ == "__main__":
    main()
