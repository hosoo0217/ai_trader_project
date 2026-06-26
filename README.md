# AI Trader Project

This project is a beginner-friendly backtesting example for XAUUSD / Gold.
It focuses on a backtest-only workflow with no real broker and no live trading.

## What it does
- Loads candle data from a CSV file
- Calculates EMA20 and EMA50 crossover signals
- Generates simple buy/sell/hold decisions
- Runs a very simple backtest with a 1% risk placeholder
- Prints a final result summary

## Project structure
- src/data_loader.py: loads OHLCV-style candle data from CSV
- src/strategy.py: generates EMA crossover signals
- src/backtester.py: runs a simple backtest
- src/risk_manager.py: stores basic risk logic
- main.py: runs the sample backtest

## Setup
1. Create and activate a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the sample backtest:
   ```bash
   python main.py
   ```

## Data format
The CSV should contain these columns:
- time
- open
- high
- low
- close
