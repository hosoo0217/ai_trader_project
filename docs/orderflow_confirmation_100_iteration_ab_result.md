# Order Flow Confirmation 100-Iteration A/B Result

This document records the research-only 100-iteration A/B diagnostic result for the simulated Order Flow confirmation proposal.

It is documentation only. It does not edit Python code, change strategy logic, implement the Order Flow confirmation rule, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record the bullish and bearish 100-iteration A/B diagnostic results for the Order Flow confirmation proposal.

The A/B diagnostic compared:

- A: current strategy behavior,
- B: simulated Order Flow confirmation behavior.

B was diagnostic only. It did not change actual execution decisions or strategy logic.

## 2. Test Setup

The research-only diagnostic was run for both bullish and bearish scenarios using:

```text
--simulate-orderflow-confirmation-ab
--backtest-max-iterations 100
```

The local private Sierra Chart test file was:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

The file was used as:

- backtest market candles through `--backtest-market-csv`,
- Order Flow context through `--orderflow-csv`.

The private Sierra CSV must not be committed.

Important scenario-label limitation:

- Because an explicit `--backtest-market-csv` was supplied, both commands used the same historical candles.
- `--scenario bullish` and `--scenario bearish` changed the printed scenario label only.
- The flag did not transform the CSV, force market direction, or create independent bullish and bearish datasets.
- These two outputs must not be counted as separate directional confirmation.

## 3. Bullish 100-Iteration Result

### A Current Behavior

Observed bullish A result:

- Total iterations: `100`
- A executed trades: `21`
- A blocked trades: `79`
- A PnL: `-210.00`
- A win rate: `0.00%`
- A max drawdown: `210.00`
- Backtest grade: `FAILED`
- Failures: `Total PnL is negative; Win rate is below required minimum; Max drawdown exceeds allowed threshold; Profit factor is below required minimum`

### B Simulated Behavior

Observed bullish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `100`
- Trades B would block by Order Flow confirmation: `21`
- Trades B would block because Order Flow was `NEUTRAL`: `21`
- Simulated B PnL: `0.00`
- Simulated B win rate: `0.00%`
- Simulated B max drawdown: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

In the bullish 100-iteration test, B would have blocked all 21 losing A trades.

## 4. Bearish 100-Iteration Result

### A Current Behavior

Observed bearish A result:

- Total iterations: `100`
- A executed trades: `21`
- A blocked trades: `79`
- A PnL: `-210.00`
- A win rate: `0.00%`
- A max drawdown: `210.00`
- Backtest grade: `FAILED`
- Failures: `Total PnL is negative; Win rate is below required minimum; Max drawdown exceeds allowed threshold; Profit factor is below required minimum`

### B Simulated Behavior

Observed bearish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `100`
- Trades B would block by Order Flow confirmation: `21`
- Trades B would block because Order Flow was `NEUTRAL`: `21`
- Simulated B PnL: `0.00`
- Simulated B win rate: `0.00%`
- Simulated B max drawdown: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

In the bearish 100-iteration test, B would also have blocked all 21 losing A trades.

## 5. Shared Pattern

The two scenario-labeled runs produced the same result because both used the same explicit historical market CSV.

Shared pattern:

- A executed 21 SELL trades.
- All 21 A executed trades were losses.
- All B-blocked trades had Order Flow `NEUTRAL`.
- B would avoid `-210.00` simulated loss.
- B leaves zero executed trades in this dataset.

This is one historical dataset result repeated under two output labels, not independent directional confirmation. It supports continued diagnosis of neutral Order Flow behavior, but it does not strengthen the evidence through replication.

## 6. What This Supports

This result supports continued research into Order Flow confirmation.

It supports these points:

- Current A behavior failed on this 100-iteration `BAR_SUMMARY` test.
- Neutral Order Flow execution remained associated with losing trades.
- B would have avoided every known losing A trade in this dataset.
- The matching bullish and bearish labels are duplicate evidence from the same historical candles, not independent directional validation.
- The proposed rule is worth testing on more data.

This result supports more validation.

It does not support implementation yet.

## 7. What Remains Unproven

This result does not prove:

- B is profitable.
- The Order Flow confirmation rule should be implemented.
- B can find winning trades.
- B will preserve enough valid trade opportunities.
- B will work across more Sierra sessions.
- B will work on full price-level footprint data.
- `BAR_SUMMARY` is enough for final Order Flow validation.
- The system is ready for paper trading.
- The system is ready for live trading.

B simulated zero executed trades, so there is no evidence yet that B can produce profitable executions.

## 8. Main Warning

Main warning:

```text
B simulated behavior blocks every A executed trade
```

This is a major warning.

Avoiding 21 losing trades is useful, but blocking every executed trade can hide risk and prevent meaningful performance evaluation.

The next validation must determine whether B can preserve valid directional-Order-Flow trades on richer data.

## 9. Safety Confirmation

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection.
- No CME live data connection.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No strategy rule implemented.

The 100-iteration A/B diagnostic stayed local, offline, and research-only.

## 10. Next Validation Steps

1. Test more Sierra weekday sessions.
2. Run bullish and bearish A/B diagnostics on additional data.
3. Test larger iteration counts when enough data exists.
4. Track whether B continues to block every executed trade.
5. Track whether B preserves valid trades when Order Flow becomes directional.
6. Export full price-level footprint data later.
7. Compare `BAR_SUMMARY` behavior against full footprint behavior.
8. Do not implement the Order Flow confirmation rule yet.
9. Do not start paper trading from this evidence.
10. Do not start live trading from this evidence.

The next goal is to determine whether B can reduce bad trades without eliminating all trades.

## 11. Beginner Summary

The 100-iteration test made the problem clearer.

In both bullish and bearish scenarios, the current system took 21 SELL trades, and all 21 lost while Order Flow was neutral. The current behavior failed the backtest quality check.

The simulated Order Flow confirmation rule would have blocked all 21 losing trades and avoided `-210.00` of simulated loss.

But there is still a serious warning: the simulated rule blocked every trade. That means it avoided losses, but it did not prove it can find winners.

So the evidence supports more research, not implementation. More Sierra sessions and full footprint data are required before changing strategy logic.
