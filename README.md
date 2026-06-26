# AI Trader Project

This project is being built as a professional AI trading platform for two distinct trading systems:
- System A: Apex Futures account trading Gold Futures (GC) on Sierra Chart with a professional scalping style and strict daily risk controls.
- System B: XAUUSD spot trading with a swing and intraday style focused on larger moves, runners, partial take profits, and trailing stops.

The current focus is research-first and paper-trading-first. The long-term goal is an autonomous AI trader that can analyze markets, protect capital, explain its decisions, and scale responsibly.

## Primary mission
- Protect capital above all else
- Never trade when market quality, confidence, or rules are weak
- Build a modular, understandable, testable, and expandable platform
- Teach the user through every decision and outcome

## Core principles
- Backtesting first
- Paper trading first
- Live trading only after validation
- No broker connection yet
- No trade is better than a bad trade
- Capital protection is more important than profit

## Market analysis framework
The system will analyze markets across multiple timeframes:
- Weekly: overall direction
- Daily: market bias
- 4H: structure
- 1H: setup
- 15M: confirmation
- 5M: execution

## Core analysis modules
- Higher timeframe analysis
- Smart Money Concepts (SMC)
- Candle Range Theory (CRT)
- Order Flow / Footprint analysis
- News filter
- Session filter
- Volatility analysis
- Market bias and execution context

## Decision engine
Every trade will pass through a validation pipeline:
Higher Timeframe -> SMC -> CRT -> Order Flow -> Risk -> Execution

If any mandatory validation fails, the system will skip the trade.

## Capital protection engine
The platform will include strict capital protection controls:
- Maximum daily loss
- Maximum daily profit
- Maximum consecutive losses
- Maximum open trades
- News protection
- Spread protection
- Session protection
- Emergency stop
- Trade lock

## AI Trading Mentor
The platform is designed to do more than generate signals. It will act as a mentor by explaining every decision in plain language.

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
- Explain why a trade hit stop loss
- Explain why a trade hit take profit
- Identify mistakes such as early entry, weak confirmation, poor session choice, and poor risk sizing
- Give a short lesson after each trade
- Create a trade grade: A+, A, B, C, or D

### Example outputs
- Winning trade explanation
- Losing trade explanation
- No-trade recommendation
- Daily lesson

## Development order
1. Foundation
2. Backtesting
3. Paper Trading
4. Small Live
5. Full Automation

Never skip phases.

## Architecture Sprint 2
The project now includes a clean modular package structure for future expansion without implementing trading logic yet.

### Package overview
- core/: orchestration for market analysis, decisions, execution, trade management, and capital protection
- analysis/: multi-timeframe analysis utilities
- smc/: Smart Money Concepts analysis modules
- crt/: Candle Range Theory analysis modules
- orderflow/: order-flow and footprint analysis modules
- risk/: risk validation and capital protection rules
- broker/: broker integration abstractions
- ai/: explainable AI modules for market analysis and coaching
- storage/: trade journal and persistence abstractions
- config/: configuration and settings
- utils/: shared helper modules such as logging

### Placeholder modules created
- core/market_analyzer.py
- core/decision_engine.py
- analysis/timeframe_analyzer.py
- smc/smc_engine.py
- crt/crt_engine.py
- orderflow/orderflow_engine.py
- risk/risk_manager.py
- broker/broker_adapter.py
- ai/trading_coach.py
- ai/market_analyst_ai.py
- storage/trade_journal.py
- config/settings.py
- utils/logger.py

Each module contains a docstring, a main class, type hints, and TODO comments describing future responsibilities.

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
