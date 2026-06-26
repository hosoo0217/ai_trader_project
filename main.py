from pathlib import Path

from src.backtester import run_backtest
from src.data_loader import load_candles


def main() -> None:
    """Run a simple backtest on the sample Gold data file."""
    data_path = Path("data/sample_xauusd.csv")
    candles = load_candles(data_path)
    result = run_backtest(candles)

    print("=== AI Trader Backtest ===")
    print(f"Trades: {result['trades']}")
    print(f"Final Equity: {result['final_equity']}")


if __name__ == "__main__":
    main()
