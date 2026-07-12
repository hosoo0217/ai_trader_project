# ai_trader_project

`ai_trader_project` is an AI Trading Platform / Trading Operating System for research, backtesting, paper trading, reporting, and human-reviewed strategy improvement planning.

It is not a live trading bot yet.

## What This Project Is

This project is built to help study trading ideas safely before any live-trading work is considered. The current focus is:

- Research
- Backtesting
- Paper-trading simulation
- Local CSV-based Order Flow / footprint analysis
- Sierra Chart CSV import and replay
- Risk and capital-protection validation
- Session reports, history, trend review, and coaching output
- Human approval, change proposal, implementation plan, and readiness workflows

The long-term idea is a professional trading operating system, but the current MVP is intentionally offline and simulation-first.

## Safety Warning

Do not use this project for real-money trading yet.

- No live trading is implemented.
- No broker connection is implemented.
- No real order execution exists.
- No real trade signals should be used for live trading.
- No external broker or market-data API is connected.
- Backtesting and paper trading are required first.

Capital protection comes before profit, speed, automation, or new features.

## Current MVP Status

The Research / Backtest / Paper Trading MVP is close to completion.

Completed or mostly complete areas:

- Core decision flow
- Safety gate
- Risk engine
- Paper broker simulation
- Smart Money Concepts (SMC)
- Candle Range Theory (CRT)
- Order Flow / footprint CSV analysis
- Sierra Chart CSV importer and replay workflow
- Session, news, spread, and volatility filters
- Session reports, export, history, and trend review
- AI coach / review output for educational use
- Strategy improvement suggestions
- Human approval workflow
- Change proposal workflow
- Implementation plan workflow
- Implementation final review workflow
- Implementation readiness checklist

Still needed before any future live-trading discussion:

- Refresh the project health audit with current test and validation results
- Final end-to-end CLI validation rerun and result update
- Deeper historical backtest validation
- Real Sierra Chart exported CSV validation
- Reports / `.gitignore` safety review
- MVP code freeze note

See [docs/mvp_completion_checklist.md](docs/mvp_completion_checklist.md) for the detailed MVP checklist.

## Setup

Use Windows PowerShell from the project root.

Create a virtual environment if needed:

```powershell
py -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install runtime and test requirements:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Run the test suite:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

## Common Commands

Run all tests:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Run the default demo:

```powershell
.\venv\Scripts\python.exe main.py
```

Run all built-in scenarios:

```powershell
.\venv\Scripts\python.exe main.py --scenario all
```

Run a bullish Apex paper-trading demo:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex
```

Run a bullish Apex backtest:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex
```

Run a demo with Order Flow CSV context and decision trace:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-csv data/sample_footprint_bullish.csv --show-trace
```

Run an Order Flow replay with replay steps:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --show-orderflow-replay-steps
```

Show session trend from saved session history:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

Check implementation readiness for a saved implementation plan:

```powershell
.\venv\Scripts\python.exe main.py --check-implementation-readiness --implementation-plan-index 0
```

## Project Structure

- `main.py`: CLI entry point for demo, backtest, Order Flow, reports, session trend, approval, proposal, and readiness workflows.
- `core/`: decision flow, backtest runner, paper-trading flow, safety gate, capital protection, trade manager, and decision context.
- `analysis/`: session, news, spread, volatility, and timeframe analysis helpers.
- `risk/`: risk validation logic.
- `broker/`: paper broker simulation and broker abstraction placeholders.
- `smc/`: Smart Money Concepts modules.
- `crt/`: Candle Range Theory modules.
- `orderflow/`: footprint, Delta/CVD, imbalance, absorption, Order Flow context, replay, reports, and Sierra Chart CSV importer.
- `ai/`: educational review, strategy improvement, human approval, proposal, plan, final review, and readiness logic.
- `storage/`: journals, reports, history, logs, proposal stores, and export helpers.
- `docs/`: design notes, CLI output notes, safety notes, and MVP cleanup checklists.
- `tests/`: unit and integration tests.
- `data/`: local sample CSV files for demo, backtest, and Order Flow testing.

## Development Rules

- Work one small step at a time.
- Run `.\venv\Scripts\python.exe -m pytest -q` after every code change.
- Commit only after tests pass.
- Keep changes easy to review.
- Do not add live trading work.
- Do not add broker credentials.
- Do not add API credentials.
- Do not connect to live broker or market-data services.
- Do not create real order execution.
- Do not create real trade signals for live use.
- Do not make automatic strategy rule changes.
- Keep human approval required for strategy changes.

## Final Cleanup Mode

The project is now in cleanup mode.

Current cleanup focus:

- Documentation
- Tests
- Bug fixes
- Validation
- Safer examples
- Clearer beginner usage
- Reports and generated-file review

No new major features should be added during cleanup. Live trading, broker connections, external APIs, and real execution are outside the current MVP.

## Next Recommended Cleanup Steps

1. Refresh the Project Health Audit
2. Run the final End-to-End CLI Validation
3. Complete the Backtest Validation Checklist
4. Validate real Sierra Chart exported CSV data
5. Review reports and `.gitignore` safety
6. Review the MVP code freeze note

## Beginner Summary

This project is a safe practice environment for building and testing trading-system ideas. It can run demos, backtests, paper-trading simulations, Order Flow CSV analysis, reports, trend reviews, and human-reviewed improvement planning.

It is not ready for real money. The next phase is cleanup and validation, not live trading.
