from pathlib import Path

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
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


def main() -> None:
    """Run a simple paper-trading demo using the research-only modules."""
    print("AI Trader Paper Trading Demo")
    print("=" * 32)

    data_path = Path(__file__).resolve().parent / "data" / "sample_xauusd.csv"
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

    print("\nFlow explanation")
    print(f"- {flow.explain(result)}")


if __name__ == "__main__":
    main()
