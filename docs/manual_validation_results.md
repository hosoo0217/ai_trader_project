# Manual Validation Results

This document records the current manual validation results for `ai_trader_project`.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

This document records the manual checks completed during cleanup, final CLI validation, real Sierra CSV validation, and deeper historical backtest validation.

The goal is to keep a clear record of what has been tested, what behaved safely, and what still requires research before paper-trading preparation or any future live-trading discussion.

## 2. Current Validation Status

- Full pytest passed.
- Current known result: `881 passed`.
- Final end-to-end CLI validation passed.
- Real Sierra Chart exported CSV validation has been completed.
- The current 1m, 5m, and 10m historical baselines were reproduced after the simulated PnL `point_value` fix.
- Git working tree was clean after committed validation checkpoints.
- The project remains research and local simulation only.
- The project is not live-trading ready.

## 3. CLI Validation Results

Validated terminal workflows include:

- default safe demo
- all built-in demo scenarios
- bullish and bearish Apex demo labels
- Apex and Spot built-in backtests
- local Order Flow CSV context
- local Order Flow replay
- saved session trend output
- implementation readiness output

Observed behavior:

- commands completed without crashing
- safe and weekend filters blocked trades where expected
- no live broker order was created
- no real trade execution occurred
- implementation readiness returned `NEEDS_BACKTEST`
- no strategy rule was implemented automatically

## 4. Real Sierra CSV Validation

Validated local Sierra Chart historical data includes:

- `BAR_SUMMARY` market candle imports
- duplicate-header positional OHLC handling
- full footprint CSV imports
- timestamp and session alignment audits
- multiple historical sessions
- 1m, 5m, and 10m datasets
- Order Flow data-quality checks
- rolling historical backtests

The validated bulk dataset contains 22 matched sessions with no mismatched sessions and no bad timestamp rows.

All private Sierra files remain under ignored `private_data` and must not be committed.

## 5. Deeper Historical Baseline

Current authoritative 200-iteration Apex baseline:

| Timeframe | Executed | Wins | Losses | Win rate | Total PnL | Profit factor | Max drawdown | Quality |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1m | 18 | 8 | 10 | 44.44% | 200.00 | 1.20 | 600.00 | INSUFFICIENT_DATA |
| 5m | 38 | 26 | 12 | 68.42% | 2700.00 | 3.25 | 300.00 | FAILED |
| 10m | 46 | 19 | 27 | 41.30% | 150.00 | 1.06 | 1100.00 | FAILED |

Interpretation:

- 1m still lacks enough executed trades for reliable evaluation.
- 5m has positive performance metrics but remains fail-closed because the drawdown-percentage threshold is not configured.
- 10m fails win-rate and profit-factor requirements.
- Positive PnL does not override failed or insufficient quality status.
- None of these results approve paper trading or live trading.

Detailed current results are recorded in:

`docs/deeper_historical_backtest_current_baseline.md`

## 6. Scenario-Label Limitation

When an explicit `--backtest-market-csv` is supplied:

- bullish and bearish scenario labels use the same historical candles
- the flag does not force historical market direction
- the labels do not create independent datasets
- matching outputs must not be counted as independent directional confirmation

Older Order Flow documents were corrected where duplicate scenario labels had been interpreted as repeated evidence.

## 7. Order Flow / Readiness Validation

- Order Flow CSV commands were tested.
- Order Flow replay commands were tested.
- Full footprint data quality passed for the current 1m, 5m, and 10m datasets.
- Global full-file Order Flow context remained neutral or inactive.
- Order Flow remains diagnostic-only.
- Order Flow confirmation enforcement is not approved.
- Implementation readiness returned `NEEDS_BACKTEST`.
- Readiness output did not change strategy rules or implement any plan automatically.

## 8. Safety Confirmation

- No live trading was implemented.
- No broker connection was used.
- No MT5 login was used.
- No Sierra Chart live connection was used.
- No CME live data connection was used.
- No real trade execution occurred.
- No external API connection was added.
- No automatic strategy rule change occurred.
- No `private_data` file was committed.

## 9. Remaining Validation

Remaining research includes:

- more independent historical periods
- true bullish, bearish, range, and volatility regime separation
- configured and reviewed drawdown thresholds
- losing-trade trace review
- out-of-sample validation
- conditional cooldown robustness validation
- tracked generated-report keep-or-untrack decision
- MVP code-freeze review

Paper-trading preparation must not begin until the required historical, risk, robustness, and human-review evidence is complete.

## 10. Beginner Summary

The project can run local demo, Order Flow, Sierra CSV, and deeper historical backtest workflows safely.

The current historical results are mixed:

- 1m does not have enough executed trades
- 5m looks stronger but still fails the configured quality process
- 10m does not meet important performance requirements

This is research evidence only. It does not approve real money, broker connection, paper-trading progression, or live trading.
