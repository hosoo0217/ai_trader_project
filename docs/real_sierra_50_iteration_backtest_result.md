# Real Sierra 50-Iteration Backtest Result

This document records the 50-iteration real Sierra Chart CSV backtest smoke result for `ai_trader_project`.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect Sierra Chart live, connect CME live data, connect MT5, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

This document records a local 50-iteration backtest smoke test using a private weekday-only Sierra Chart `BAR_SUMMARY` CSV as both:

- backtest market candles through `--backtest-market-csv`,
- Order Flow context through `--orderflow-csv`.

The goal was to confirm that real Sierra CSV data can run through a larger local backtest loop safely and produce conservative quality warnings when the result is not reliable enough.

This was not a profitability validation.

## 2. Tested Local File

The private local CSV file tested was:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

This file was created locally from a Sierra Chart export.

This private CSV must not be committed to GitHub.

Keep all real Sierra Chart exports, broker exports, account data, and private trading files out of GitHub unless they have been explicitly reviewed and sanitized.

## 3. Commands Tested

The tested commands were similar to:

```powershell
python main.py --mode backtest --scenario bullish --profile apex --backtest-market-csv private_data/sierra_chart/gc_weekday_test.csv --orderflow-csv private_data/sierra_chart/gc_weekday_test.csv --backtest-max-iterations 50
```

```powershell
python main.py --mode backtest --scenario bearish --profile apex --backtest-market-csv private_data/sierra_chart/gc_weekday_test.csv --orderflow-csv private_data/sierra_chart/gc_weekday_test.csv --backtest-max-iterations 50
```

Both commands used local CSV data only.

## 4. Bullish Result

Observed bullish result:

- Total iterations: `50`
- Trades executed: `8`
- Trades blocked: `42`
- Final balance: `49920.00`
- Total PnL: `-80.00`
- Wins: `0`
- Losses: `8`
- Win rate: `0.00%`
- Profit factor: `0.00`
- Max drawdown: `80.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Failure: `Not enough executed trades for reliable evaluation`

The bullish path completed, but all 8 executed trades lost in this smoke test.

## 5. Bearish Result

Observed bearish result:

- Total iterations: `50`
- Trades executed: `8`
- Trades blocked: `42`
- Final balance: `49920.00`
- Total PnL: `-80.00`
- Wins: `0`
- Losses: `8`
- Win rate: `0.00%`
- Profit factor: `0.00`
- Max drawdown: `80.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Failure: `Not enough executed trades for reliable evaluation`

The bearish path completed, but all 8 executed trades lost in this smoke test.

## 6. Order Flow Result

Observed Order Flow result:

- Import source: `BAR_SUMMARY`
- Mapping: positional OHLC
- Candle count: `864`
- Total levels: `864`
- Data quality: `PASSED`
- Order Flow bias: `NEUTRAL`

`BAR_SUMMARY` Order Flow uses one synthetic close-price level per candle. It is useful for early validation, but it is not full price-level footprint data.

## 7. Backtest Quality Interpretation

The backtest quality was `INSUFFICIENT_DATA` for both scenarios.

This is the correct conservative interpretation because only 8 trades executed per scenario. That is not enough to evaluate:

- win rate,
- profit factor,
- expectancy,
- drawdown behavior,
- losing streak behavior,
- session robustness,
- market-condition robustness.

The result should be read as a local smoke test, not as a reliable performance study.

The 8 executed trades all lost in this smoke test, so the executed-trade behavior needs diagnosis before any paper trading discussion.

The system also blocked 42 out of 50 opportunities in each scenario. That is useful safety behavior because the strategy did not force trades on most iterations.

## 8. What This Proves

This test proves:

- Real Sierra `BAR_SUMMARY` CSV data can be used as backtest market candles.
- The same local Sierra CSV can also be used as Order Flow context.
- `--backtest-market-csv` and `--orderflow-csv` can run together.
- `--backtest-max-iterations 50` can complete locally.
- Bullish and bearish scenario paths can complete without crashing.
- The system can block most trades instead of forcing entries.
- The system can report `INSUFFICIENT_DATA` instead of overclaiming reliability.
- Order Flow data quality can pass on this weekday-only Sierra export.

## 9. What This Does Not Prove

This test does not prove:

- The system is profitable.
- The system is ready for paper trading.
- The system is ready for live trading.
- The strategy has a reliable win rate.
- The strategy has a reliable profit factor.
- The drawdown profile is acceptable.
- `BAR_SUMMARY` data is equivalent to full price-level footprint data.
- Filters should be weakened to force more trades.
- Broker integration or live data integration should begin.

This result is not enough for paper trading.

This result is not enough for live trading.

## 10. Safety Confirmation

- No Sierra live connection.
- No CME live data connection.
- No MT5 login.
- No broker connection.
- No real order execution.
- No live trading.
- No `private_data` committed.

The test stayed local, offline, and research-only.

## 11. Next Validation Steps

1. Diagnose why the executed trades lost.
2. Review decision traces for the executed trades.
3. Test more weekday sessions.
4. Test full price-level footprint export later.
5. Do not weaken filters just to force trades.
6. Do not start paper trading from this result.
7. Do not start live trading from this result.

More data, more sessions, and better validation are required before considering any trading deployment.

## 12. Beginner Summary

This test ran a real Sierra Chart weekday CSV through 50 backtest iterations for both bullish and bearish scenarios.

Both scenarios finished safely. In each scenario, the system blocked most trades, executed 8 trades, and all 8 executed trades lost. The final result was `-80.00` PnL per scenario.

The Order Flow CSV loaded successfully and passed data quality, but it was `BAR_SUMMARY` data, not full footprint data.

The most important takeaway is caution: the plumbing worked, but the trade results were not good enough and not statistically reliable. This does not justify paper trading or live trading. The next step is to inspect the losing trades, test more data, and keep the safety filters intact.
