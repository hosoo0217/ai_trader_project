# AI Trader Project

This project is a beginner-friendly research and backtesting example for XAUUSD / Gold.
It is designed to stay research-first, with no live execution and no broker connection at this stage.

## What it does
- Loads candle data from a CSV file
- Calculates EMA20 and EMA50 crossover signals
- Generates simple buy/sell/hold decisions
- Runs a very simple backtest with a 1% risk placeholder
- Prints a final result summary

## Planned research direction
The project will grow in stages toward more advanced market analysis:
- Candle-based backtesting and performance review
- Smart Money Concepts and CRT signal research
- Order-flow and footprint analysis for Sierra Chart-style CSV exports
- Beginner-friendly explanations of market context and trade ideas
- An AI Trading Mentor that teaches the user through every decision

## Core concept: AI Trading Mentor
The system will not only generate trade signals. It will act like a mentor by explaining every decision in plain language.

### AI brain modules
1. Market Analyst
- Multi-timeframe analysis: Weekly, Daily, 4H, 1H, 15M, 5M
- SMC
- CRT
- Order Flow / Footprint
- Market bias

2. Risk Manager
- Entry validation
- Stop loss explanation
- Take profit logic
- Risk per trade
- Daily loss limit
- No-trade conditions

3. Trading Coach
- Explain why a trade was taken
- Explain why a trade hit SL
- Explain why a trade hit TP
- Identify mistakes such as early entry, weak confirmation, bad session, and poor risk
- Give a short lesson after each trade
- Create a trade grade: A+, A, B, C, D

### Example outputs
- Winning trade explanation
- Losing trade explanation
- No-trade recommendation
- Daily lesson

## Upcoming major phase
Phase 5 - Order Flow / Footprint Engine

This phase will focus on research-only order-flow analysis using exported data, not live trading. It will include:
- Footprint data import from CSV
- Bid volume and ask volume analysis
- Delta and cumulative delta (CVD)
- Imbalance, absorption, and exhaustion detection
- Volume profile, Point of Control (POC), and Value Area High/Low
- Session volume analysis
- Integration with SMC and CRT signals
- AI explanations of order-flow context

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

## Development philosophy
- Backtesting first
- Paper trading first
- Research before execution
- No live trading yet
- No broker connection yet
- Beginner-friendly explanations
