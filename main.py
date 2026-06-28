from pathlib import Path

import pandas as pd

from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig


def main() -> None:
    """Run the paper trading flow on the sample Gold data file."""
    data_path = Path("data/sample_xauusd.csv")
    candles = pd.read_csv(data_path)

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
    )

    print("=== AI Trader Paper Flow ===")
    print(f"Market bias: {result.market_bias}")
    print(f"Final decision: {result.decision_action}")
    print(f"Trade executed: {result.trade_executed}")
    print(f"Paper balance: {result.balance}")
    print(flow.explain(result))


if __name__ == "__main__":
    main()
