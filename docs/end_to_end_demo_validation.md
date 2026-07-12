# End-to-End Demo Validation

This document is a manual end-to-end validation checklist for `ai_trader_project`.

It is documentation only. It does not edit Python code, add trading features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

End-to-end validation checks whether the existing CLI flows work together safely from the terminal.

The goal is to confirm that the current research / backtest / paper-trading MVP can run its main paths:

- Demo mode
- Backtest mode
- Order Flow CSV context
- Order Flow replay
- Session trend output
- Implementation readiness output

This validation is not a live-trading test. It is only a safe local check before deeper backtest validation, real Sierra Chart CSV validation, and paper-trading validation.

## 2. Baseline Test

Run the full test suite first:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Expected result:

- Pytest should pass.
- Current known test status from cleanup mode: `881 tests passed`.
- If pytest fails, stop and fix or document the failure before running CLI validation.

## 3. Demo Mode Validation

Run the default demo:

```powershell
.\venv\Scripts\python.exe main.py
```

Run all built-in scenarios:

```powershell
.\venv\Scripts\python.exe main.py --scenario all
```

Run bullish Apex demo mode:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex
```

Run bearish Apex demo mode:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bearish --profile apex
```

Expected safe behavior:

- Commands run locally.
- Output may include analysis, safety checks, paper/demo decisions, and review text.
- Any trade-like behavior is paper/demo simulation only.
- No broker credentials are required.
- No real order is placed.

## 4. Backtest Mode Validation

Run bullish Apex backtest mode:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex
```

Run bullish Spot backtest mode:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile spot
```

Expected safe behavior:

- Commands run locally.
- Output may include backtest metrics, research summaries, and safety/risk context.
- Backtest output must not be treated as live-trading readiness.
- No live data is requested.
- No real execution occurs.

## 5. Order Flow CSV Validation

Run demo mode with local Order Flow CSV context and a fixed session time:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv data/sample_footprint_bullish.csv --show-trace
```

Expected safe behavior:

- Local CSV is read from `data/sample_footprint_bullish.csv`.
- Order Flow context may print in the output.
- Decision trace may print in the output.
- No Sierra Chart live connection is used.
- No CME, broker, or external API connection is used.

## 6. Order Flow Replay Validation

Run Order Flow replay with step output:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --show-orderflow-replay-steps
```

Expected safe behavior:

- Replay steps print from the local CSV.
- Replay is educational/research-only.
- Replay output is not a live trade signal.
- No real order is placed.

## 7. Session Trend Validation

Show session trend:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

Expected safe behavior:

- Session trend output may print from saved local session history.
- Output is reporting/review only.
- No strategy rules are changed.
- No trades are placed.

Optional later validation can add session report export commands after generated report handling is reviewed.

## 8. Implementation Readiness Validation

Check implementation readiness for saved implementation plan index `0`:

```powershell
.\venv\Scripts\python.exe main.py --check-implementation-readiness --implementation-plan-index 0
```

Expected safe behavior:

- Readiness status may print.
- Missing or incomplete plan data should be reported safely.
- Readiness output is a checklist only.
- It must not edit code, config, strategy rules, risk rules, broker logic, or execution logic.

## 9. Expected Safe Behavior

Across all commands:

- Commands may print trade analysis, paper/demo output, reports, warnings, or readiness status.
- Commands must not place real trades.
- Commands must not connect to a broker.
- Commands must not call external APIs.
- Commands must not change strategy rules automatically.
- Commands must not create live trading execution.
- Commands must not require broker credentials, API keys, account numbers, or secrets.

Generated files, if any, should remain local and should be reviewed before committing.

## 10. Failure Handling

If pytest fails:

- Stop validation.
- Record the failing command.
- Record the failing test names and error summary.
- Fix or understand the test failure before continuing.

If a CLI command crashes:

- Stop the current validation path.
- Record the exact command.
- Record the error output.
- Do not hide the failure.
- Do not continue validation until the failure is understood.

If a command appears to request credentials, connect to a live service, or place a real order:

- Stop immediately.
- Treat it as a safety issue.
- Do not continue until the behavior is reviewed.

## 11. Beginner Summary

This checklist proves that the project can run from start to finish in demo and research mode.

You are checking that the main terminal commands work before moving into deeper backtest validation, real Sierra Chart CSV testing, or paper-trading validation.

The project is not going live during this step. Everything should stay local, simulated, and safe.

## 12. Validation Result - 2026-07-12

Current result: **PASSED**

Validated commands:

- full pytest suite: `881 passed`
- default safe demo
- all built-in scenarios
- bullish and bearish Apex demo flows
- bullish Apex and Spot backtests
- local Order Flow CSV context with decision trace
- local Order Flow replay with step output
- saved session trend output
- implementation readiness check

Observed safety behavior:

- no command crashed
- safe and weekend filters blocked trades where expected
- built-in backtests reported insufficient data rather than deployment readiness
- missing drawdown threshold remained fail-closed
- Order Flow remained local and research-only
- implementation readiness returned `NEEDS_BACKTEST`
- no broker connection, external API, live data, or real order execution was used
- no strategy rule or code change was applied automatically
- Git working tree remained clean after validation

This result validates the current local CLI workflows only. It does not approve live trading, strategy deployment, or real-money use.
