# End-to-End Demo Validation

This document is a manual validation checklist for `ai_trader_project`.

It is documentation only. It does not add trading features, edit Python code, connect to a broker, call external APIs, create trade signals, place orders, or implement live trading.

## Purpose

End-to-end validation checks whether the current research / backtest / paper-trading MVP can be run safely from the command line.

The goal is to confirm:

- `main.py` demo mode runs.
- Backtest mode runs.
- Order Flow CSV context runs.
- Order Flow replay runs.
- Session reports and session trend run.
- Approval, proposal, final review, and implementation readiness flows run.
- Generated reports are created only as local files.
- No live trading, broker connection, external API call, or real order execution occurs.

## Before You Start

Use Windows PowerShell from the project root.

Recommended baseline:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Current known test status from the MVP cleanup pass: `793 tests passed`.

## Demo Mode Commands

Run the default demo:

```powershell
.\venv\Scripts\python.exe main.py
```

Expected safe behavior:

- Program runs locally.
- Output is beginner-readable.
- Uses demo/paper-trading simulation behavior.
- Does not connect to a broker.
- Does not place a real order.

Run all built-in scenarios:

```powershell
.\venv\Scripts\python.exe main.py --scenario all
```

Expected safe behavior:

- Bullish, bearish, and weak scenarios run.
- Results stay local.
- Any trade action is paper/simulated only.

Run a focused Apex demo:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex
```

Expected safe behavior:

- Apex profile settings are used for simulation.
- Risk and safety checks appear in output.
- No broker credentials are needed.

## Backtest Mode Commands

Run a focused Apex backtest:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex
```

Expected safe behavior:

- Backtest summary prints.
- Output should clearly remain research-only.
- Result should not be treated as live-trading readiness.

Run all scenarios in backtest mode:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario all --profile apex
```

Expected safe behavior:

- Multiple scenarios run locally.
- No live data is requested.
- No real execution occurs.

## Order Flow CSV Commands

Run demo mode with sample Order Flow CSV context:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-csv data/sample_footprint_bullish.csv --show-trace
```

Expected safe behavior:

- Local CSV is read from `data/`.
- Order Flow context appears in the output.
- Decision trace appears if available.
- No Sierra Chart live connection is used.
- No CME, broker, or external API connection is used.

Run backtest mode with sample Order Flow CSV context:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --orderflow-csv data/sample_footprint_bullish.csv --show-trace
```

Expected safe behavior:

- Backtest uses local Order Flow context.
- Output remains research/backtest only.
- No live market data is used.

## Order Flow Replay Commands

Run Order Flow replay with step output:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --show-orderflow-replay-steps
```

Expected safe behavior:

- Replay steps print from the local CSV.
- Replay is educational/research-only.
- No real trade signals are created.
- No orders are placed.

Run Order Flow replay and export a local report:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --export-orderflow-report
```

Expected safe behavior:

- Local report files may be written under `reports/`.
- Generated files should be reviewed before committing.
- No live systems are contacted.

## Session Report / Trend Commands

Show a session report:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --show-session-report
```

Expected safe behavior:

- Session report prints locally.
- Report is for review only.
- It does not create live signals or orders.

Export a session report:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --show-session-report --export-session-report
```

Expected safe behavior:

- Local report files may be written under `reports/`.
- Review generated files before committing.

Save session history and show summary:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --save-session-history --show-session-history-summary
```

Expected safe behavior:

- Local `session_history.json` may be updated under `reports/`.
- History is for review and trend analysis only.

Show session trend:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

Expected safe behavior:

- Trend analysis prints from saved local session history if available.
- Trend output is educational/reporting only.
- No trade signals are created.

## Approval / Proposal / Implementation Readiness Commands

Show session trend and pending approval requests:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

Expected safe behavior:

- Improvement suggestions may appear as review items.
- Suggestions require human approval.
- Suggestions do not change strategy rules automatically.

Record a human approval decision for a generated request:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --approval-decision APPROVE --approval-request-index 0 --approval-decided-by "Manual Reviewer" --approval-notes "Demo validation only"
```

Expected safe behavior:

- A local approval log may be written under `reports/`.
- An approved request may create a saved change proposal.
- No implementation happens automatically.

Review a saved change proposal:

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal ACCEPT --change-proposal-index 0 --proposal-reviewed-by "Manual Reviewer" --proposal-review-notes "Demo validation only"
```

Expected safe behavior:

- A local proposal review log may be written under `reports/`.
- An accepted proposal may create a saved implementation plan.
- No code or strategy rule changes happen automatically.

Final-review a saved implementation plan:

```powershell
.\venv\Scripts\python.exe main.py --final-review-implementation-plan APPROVE_FOR_WORK --implementation-plan-index 0 --implementation-reviewed-by "Manual Reviewer" --implementation-review-notes "Demo validation only"
```

Expected safe behavior:

- A local implementation final review log may be written under `reports/`.
- Approval means future human-reviewed work may be considered.
- It does not implement the plan.

Check implementation readiness:

```powershell
.\venv\Scripts\python.exe main.py --check-implementation-readiness --implementation-plan-index 0
```

Expected safe behavior:

- Readiness output prints locally.
- Readiness is a checklist only.
- It does not edit config, code, strategy rules, broker logic, or execution logic.

## Validation Results Checklist

Use this checklist while running the commands:

- [ ] Full pytest passes.
- [ ] Default demo runs.
- [ ] All scenarios run.
- [ ] Focused Apex demo runs.
- [ ] Focused Apex backtest runs.
- [ ] Order Flow CSV context runs.
- [ ] Order Flow replay steps run.
- [ ] Order Flow replay report export runs.
- [ ] Session report output runs.
- [ ] Session report export runs.
- [ ] Session history save/summary runs.
- [ ] Session trend runs.
- [ ] Approval request output runs.
- [ ] Approval decision logging runs.
- [ ] Change proposal review runs.
- [ ] Implementation final review runs.
- [ ] Implementation readiness check runs.
- [ ] Generated `reports/` files are reviewed.
- [ ] No API keys, broker credentials, account numbers, or secrets are present in generated files.
- [ ] No live trading code is used.
- [ ] No real broker connection is used.
- [ ] No real order execution occurs.

## No Live Trading Safety Reminder

This project is not a live trading bot.

- No live trading is implemented.
- No real broker connection is implemented.
- No real order execution exists.
- No live Sierra Chart or CME connection is used.
- No external API call is required for the demo validation checklist.
- Backtesting and paper trading are required before any future live-trading discussion.

If a command ever appears to require credentials, connect to a live service, or place a real order, stop validation and investigate before continuing.

## Beginner Summary

This checklist helps you prove that the project can run from start to finish in a safe demo mode.

You are checking that the system can run demos, backtests, Order Flow CSV analysis, Order Flow replay, session reports, session trends, approval records, proposal review, final review, and readiness checks.

Everything should stay local and simulated. The goal is confidence in the MVP workflow, not live trading.
