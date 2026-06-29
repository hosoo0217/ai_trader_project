# Real Sierra CSV Backtest Smoke Result

This document records the first backtest smoke test using a real Sierra Chart exported CSV file.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect Sierra Chart live, connect CME live data, connect MT5, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

This document records the first backtest-mode smoke result using a real Sierra Chart CSV export.

The goal was not to judge strategy performance. The goal was to confirm that real exported Sierra Chart data can flow through backtest mode safely without crashing.

## 2. Command Tested

The tested command was similar to:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv private_data/sierra_chart/gc_footprint_test.csv --show-trace
```

The CSV path was:

```text
private_data/sierra_chart/gc_footprint_test.csv
```

This file is private local data and must not be committed to GitHub.

## 3. Result Summary

- Backtest completed.
- Scenario: `bullish`
- Profile: `Apex Futures Scalper`
- Symbol: `GC`
- Starting balance: `50000.00`
- Daily profit target: `200.00`
- Max daily loss: `200.00`
- Risk per trade percent: `0.25%`
- Total iterations: `1`
- Trades executed: `1`
- Trades blocked: `0`
- Final balance: `49990.00`
- Total PnL: `-10.00`
- Backtest quality grade: `INSUFFICIENT_DATA`
- Backtest quality passed: `False`
- Failure reason: `Not enough iterations for reliable evaluation`
- Recommendation: `Needs more data`

Decision result:

- Final action: `BUY`
- Final allowed: `True`
- Trade was executed only in research/backtest simulation.
- Exit simulator exited at candle `4`.

## 4. Order Flow Validation

- Active: `False`
- Bias: `NEUTRAL`
- Confidence: `0.0`
- Data quality status: `PASSED`
- Candle count: `1393`
- Total levels: `1393`
- Invalid levels: `0`
- Invalid level ratio: `0.00`
- Import source: `BAR_SUMMARY`

The import used Sierra Chart `BAR_SUMMARY` data.

`BAR_SUMMARY` creates one synthetic close-price level per candle. It is not full price-level footprint data.

Order Flow stayed neutral instead of crashing or forcing a directional result.

## 5. Backtest Quality Interpretation

The `-10.00` PnL does not prove the strategy is bad.

This smoke test used only `1` iteration, so the backtest quality result `INSUFFICIENT_DATA` is expected and correct.

One iteration is not enough to evaluate win rate, drawdown, expectancy, profit factor, or strategy robustness.

The correct interpretation is:

- The backtest command completed.
- The real Sierra CSV did not crash the flow.
- The system correctly warned that more data is needed.
- Performance should not be judged from this result.

## 6. What This Proves

- A real Sierra Chart exported CSV can flow through backtest mode.
- The project can import `BAR_SUMMARY` data during a backtest smoke test.
- Order Flow data quality can pass on the real exported CSV.
- Order Flow can remain neutral safely.
- The backtest quality checker can flag insufficient data.
- The flow stayed local, offline, and research-only.

## 7. What This Does Not Prove

- It does not prove the strategy is profitable.
- It does not prove the strategy is ready for paper trading.
- It does not prove the strategy is ready for live trading.
- It does not validate performance across enough market conditions.
- It does not validate full price-level footprint data.
- It does not justify changing strategy rules.
- It does not justify connecting a broker.

## 8. Safety Confirmation

- No Sierra Chart live connection.
- No CME live data connection.
- No MT5 login.
- No broker connection.
- No real order execution.
- No live trading.
- No external API connection.
- No private data files committed.

The trade result was research/backtest simulation only.

## 9. Next Validation Steps

1. Run more than `1` iteration later.
2. Test multiple scenarios.
3. Test a smaller one-session CSV.
4. Test full price-level footprint export later.
5. Build deeper historical backtest validation before any paper trading decision.

Paper trading preparation should wait until more backtest evidence exists.

## 10. Beginner Summary

This smoke test proved that a real Sierra Chart CSV can go through backtest mode without crashing.

It did not prove whether the strategy is good or bad. The test only had one iteration, so the system correctly said there was not enough data.

The next step is more validation: smaller controlled CSV tests, true footprint exports, multiple scenarios, and deeper historical backtests. Live trading is still not part of this phase.
