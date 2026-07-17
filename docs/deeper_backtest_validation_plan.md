# Deeper Backtest Validation Plan

This document defines the next safe validation plan for deeper historical backtesting in `ai_trader_project`.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect Sierra Chart live, connect CME live data, connect MT5, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

The next phase is deeper backtest validation.

This is not live trading. It is also not broker integration, MT5 integration, Sierra Chart live integration, or paper trading yet.

The goal is to prove that the existing research/backtest system can be tested across enough historical examples before any paper-trading decision is considered.

## 2. Current Proven Status

The project has completed these cleanup and validation checkpoints:

- MVP cleanup checkpoint.
- Real Sierra Chart `BAR_SUMMARY` CSV import support.
- Real Sierra CSV demo validation.
- Real Sierra CSV backtest smoke test.
- Real Sierra CSV bullish/bearish multi-scenario smoke test.
- Git tag: `real-sierra-validation-checkpoint`.

Current proven real-data status:

- Real Sierra `BAR_SUMMARY` CSV can be imported.
- `1393` candles were imported.
- `1393` synthetic levels were created.
- Order Flow data quality passed.
- Bullish smoke test completed.
- Bearish smoke test completed.
- Order Flow stayed neutral safely.
- No live connection exists.

## 3. Current Limitation

The current real Sierra CSV backtest runs only `1` iteration and reports:

- Backtest Quality Grade: `INSUFFICIENT_DATA`
- Reason: `Not enough iterations for reliable evaluation`

This is expected and correct.

One iteration is not enough to judge performance, win rate, drawdown, profit factor, expectancy, or robustness.

Earlier real Sierra testing used `BAR_SUMMARY` data, which creates one synthetic close-price level per bar. Complete 1m, 5m, and 10m Market OHLC/full-footprint pairs are now preserved for the accepted independent candidate; `BAR_SUMMARY` remains diagnostic-only evidence.

The canonical baseline and its 1m, 5m, and 10m representations still cover the same calendar window and must not be treated as independent evidence. A separate non-overlapping `GC-202608-COMEX` candidate received Full Independent-Period Acceptance on `2026-07-16`.
The independent-dataset intake classification blocker is closed for the accepted candidate. Its first frozen 5m independent-period `weak` / no-Order-Flow baseline completed on `2026-07-17` and failed reproducibly with `69` executed trades, `-800.00` total PnL, `0.82` profit factor, and `4.60%` maximum drawdown. Additional independent periods, out-of-sample, regime-separated, and robustness validation remain pending, and code freeze remains active.

The `-10.00` PnL from one smoke test does not prove the strategy is good or bad.

For deeper research-only validation, the CLI can run more rolling backtest iterations with:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --backtest-max-iterations 25
```

Using more iterations can help reduce `INSUFFICIENT_DATA` when enough historical candles exist. It is still backtesting only, not paper trading or live trading.

To use a local historical OHLC CSV as the backtest market candle source, use:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --profile apex --backtest-market-csv private_data/sierra_chart/gc_footprint_test.csv --backtest-max-iterations 25
```

`--backtest-market-csv` provides the market candles for rolling backtests. `--orderflow-csv` provides Order Flow context. During early Sierra `BAR_SUMMARY` validation, the same local Sierra CSV can be passed to both options:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --profile apex --backtest-market-csv private_data/sierra_chart/gc_footprint_test.csv --orderflow-csv private_data/sierra_chart/gc_footprint_test.csv --backtest-max-iterations 25
```

This still reads local historical CSV files only. It does not connect to Sierra Chart live, CME live data, MT5, a broker, or any external API.

For Sierra `BAR_SUMMARY` market candles, duplicate headers are handled positionally. The first price OHLC group is used as market data: `Date`, `Time`, `Open`, `High`, `Low`, `Last`, and `Volume`. Later duplicate study columns do not overwrite the price OHLC values.

When executed trades lose during a research-only backtest, use the diagnostic trace export:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --profile apex --backtest-market-csv private_data/sierra_chart/gc_footprint_test.csv --orderflow-csv private_data/sierra_chart/gc_footprint_test.csv --backtest-max-iterations 50 --export-backtest-trade-traces
```

This creates `reports/backtest_trade_traces.json` and `reports/backtest_trade_traces.txt` by default. These files are for diagnosing executed trade decisions and simulated exits. They are not trading approval, do not weaken filters, and do not connect to live systems.

## 4. Minimum Deeper Backtest Requirements

Future deeper validation should include:

- Multiple iterations.
- Multiple sessions.
- Multiple market regimes.
- Bullish conditions.
- Bearish conditions.
- Choppy/range conditions.
- Winning examples.
- Losing examples.
- Data quality checks.
- Performance report review.
- Drawdown review.
- Risk rule review.
- Capital protection review.
- Safety gate review.

The goal is not to force good results. The goal is to understand whether the system behaves safely and consistently across enough examples.

## 5. Suggested Validation Stages

### Stage 1: One-Session BAR_SUMMARY Backtest

- Use a small one-session Sierra Chart `BAR_SUMMARY` export.
- Confirm import, data quality, Order Flow context, and backtest output.
- Confirm no crash and no live connection.
- Record the result clearly.

### Stage 2: Multi-Session BAR_SUMMARY Backtest

- Use multiple sessions from Sierra Chart `BAR_SUMMARY` exports.
- Treat any BAR_SUMMARY subset, re-export, resample, or alternate-timeframe representation of the canonical baseline window as non-independent diagnostic evidence only; it cannot close the independent historical validation blocker.
- Run bullish, bearish, and range/choppy scenarios.
- Use `--backtest-max-iterations` to run more rolling research-only iterations when enough candles exist.
- Use `--backtest-market-csv` when the Sierra export should provide the OHLC market candles.
- Use `--orderflow-csv` separately when the Sierra export should also provide Order Flow context.
- Confirm Sierra `BAR_SUMMARY` market candles use the first price OHLC group, not later duplicate study columns.
- Review total trades, blocked trades, risk behavior, and backtest quality grade.
- Use `--export-backtest-trade-traces` to review executed losing trades before considering any rule changes.
- Confirm quality grade improves beyond `INSUFFICIENT_DATA` only when enough iterations exist.

### Stage 3: Full Price-Level Footprint CSV Backtest

- Export true price-level footprint CSV data when available.
- Before assigning any evidence classification, follow `docs/independent_historical_dataset_intake.md` for non-overlap, complete Market OHLC/full-footprint pairs, exact schema, metadata, matching, gap, overwrite-protection, traceability, and safety requirements.
- Confirm each candle has real bid/ask volume across price levels.
- Compare output against `BAR_SUMMARY` behavior.
- Prefer full footprint data for serious Order Flow validation.

### Stage 4: Paper Trading Simulation Preparation

- Paper-trading simulation preparation is not approved in the current phase; improved backtest evidence alone is insufficient to authorize it.
- Do not connect a broker.
- Do not use MT5 login.
- Do not enable real execution.
- Keep human review in control before any next phase.

## 6. Metrics To Track

Track these metrics for every deeper validation run:

- Total trades.
- Win rate.
- Total PnL.
- Profit factor.
- Max drawdown as a descriptive metric only; no numerical drawdown threshold is approved.
- Average win.
- Average loss.
- Blocked trades.
- Safety gate blocks.
- Order Flow bias distribution.
- Data quality pass/fail.
- Backtest quality grade.
- Failure or blocking reasons.

Each run should be documented with the data source, scenario, profile, date range, result, and safety notes.

## 7. Safety Rules

- No Sierra Chart live connection.
- No CME live data connection.
- No MT5 login.
- No broker connection.
- No real order execution.
- No live trading.
- No external API connection.
- No `private_data` files committed.
- No account numbers, broker credentials, API keys, or secrets committed.

All validation should remain local, offline, and research/backtest only.

## 8. Exit Criteria Before Paper Trading

Paper trading is not approved in the current phase. Future consideration must remain blocked unless every item below is satisfied and a separate documented approval explicitly lifts the applicable freeze:

- Backtest has enough iterations.
- Backtest quality grade is no longer `INSUFFICIENT_DATA`.
- Full Independent-Period Acceptance remains valid for `GC-202608-COMEX`, but its first frozen 5m independent-period baseline failed reproducibly on `2026-07-17`; this negative performance evidence and the remaining validation requirements keep paper progression blocked.
- Risk behavior is reviewed.
- Capital protection behavior is reviewed.
- Safety gate behavior is reviewed.
- Data quality results are documented.
- Performance results are documented.
- Weaknesses and failure cases are documented.
- Human review records whether every prerequisite is satisfied; human review alone does not authorize paper-trading preparation.

Passing a single smoke test is not enough.

## 9. Beginner Summary

The system can now read real Sierra Chart data, but it still needs many more tests before it can be trusted even for paper trading.

So far, the project has proven that real `BAR_SUMMARY` CSV data can enter the system and run through demo and backtest smoke tests without crashing.

The next job is deeper offline validation: more sessions, scenarios, iterations, reports, and risk review, plus intake of a genuinely independent non-overlapping dataset under `docs/independent_historical_dataset_intake.md`.

Live trading is not part of this phase.
