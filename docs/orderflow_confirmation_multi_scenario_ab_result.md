# Order Flow Confirmation Multi-Scenario A/B Result

This document records the research-only multi-scenario A/B diagnostic result for the simulated Order Flow confirmation proposal.

It is documentation only. It does not edit Python code, change strategy logic, implement the Order Flow confirmation rule, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record the bullish and bearish A/B diagnostic results for the Order Flow confirmation proposal.

The A/B diagnostic compared:

- A: current strategy behavior,
- B: simulated Order Flow confirmation behavior.

B was diagnostic only. It did not change actual execution decisions.

## 2. Test Setup

The research-only diagnostic was run for both bullish and bearish scenarios using:

```text
--simulate-orderflow-confirmation-ab
```

The local private Sierra Chart test file was:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

The file was used as:

- backtest market candles through `--backtest-market-csv`,
- Order Flow context through `--orderflow-csv`.

The run also used:

- `--backtest-max-iterations 50`

The private Sierra CSV must not be committed.

Important scenario-label limitation:

- Because an explicit `--backtest-market-csv` was supplied, both commands used the same historical candles.
- `--scenario bullish` and `--scenario bearish` changed the printed scenario label only.
- The flag did not transform the CSV, force market direction, or create independent bullish and bearish datasets.
- These two outputs must not be counted as separate directional confirmation.

## 3. Bullish A/B Result

### A Current Behavior

Observed bullish A result:

- Total iterations: `50`
- A executed trades: `8`
- A blocked trades: `42`
- A PnL: `-80.00`
- A win rate: `0.00%`
- A max drawdown: `80.00`

### B Simulated Behavior

Observed bullish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- Trades B would block by Order Flow confirmation: `8`
- Trades B would block because Order Flow was `NEUTRAL`: `8`
- Simulated B PnL: `0.00`
- Simulated B win rate: `0.00%`
- Simulated B max drawdown: `0.00`
- Warning: `B blocked every A executed trade`

In the bullish scenario, B would have blocked all 8 losing A trades.

## 4. Bearish A/B Result

### A Current Behavior

Observed bearish A result:

- Total iterations: `50`
- A executed trades: `8`
- A blocked trades: `42`
- A PnL: `-80.00`
- A win rate: `0.00%`
- A max drawdown: `80.00`

### B Simulated Behavior

Observed bearish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- Trades B would block by Order Flow confirmation: `8`
- Trades B would block because Order Flow was `NEUTRAL`: `8`
- Simulated B PnL: `0.00`
- Simulated B win rate: `0.00%`
- Simulated B max drawdown: `0.00`
- Warning: `B blocked every A executed trade`

In the bearish scenario, B would also have blocked all 8 losing A trades.

## 5. Shared Pattern

The two scenario-labeled runs produced the same A/B result because both used the same explicit historical market CSV.

Shared pattern:

- A executed 8 SELL trades.
- All 8 A executed trades were losses.
- Order Flow was `NEUTRAL`.
- B would block all 8 losing trades.
- B also leaves zero executed trades in this dataset.

The repeated result strengthens the observation that neutral Order Flow was unsafe in this limited `BAR_SUMMARY` test.

## 6. What This Supports

This result supports further research into the Order Flow confirmation proposal.

It supports these points:

- Neutral Order Flow was present on the losing executed trades.
- The proposed B diagnostic would have avoided the known losing trades.
- The matching scenario-labeled outputs came from the same historical candles and are not independent directional evidence.
- The single-dataset result is sufficient to continue diagnostic A/B testing, but not because it was independently repeated across market directions.

This is useful evidence for research.

It is not enough evidence for implementation.

## 7. What Remains Unproven

This result does not prove:

- The proposed Order Flow confirmation rule is profitable.
- The proposed rule should be implemented.
- B can find winning trades.
- B will preserve enough valid trades.
- B will work across more Sierra sessions.
- B will work on full price-level footprint data.
- The strategy is ready for paper trading.
- The strategy is ready for live trading.

B blocked every executed trade in this dataset, so there is still no evidence that B can produce profitable executions.

## 8. Main Warning

Main warning:

```text
B blocked every A executed trade
```

This is a major warning.

Blocking every losing trade is helpful in this limited sample, but blocking every executed trade can also hide risk and make the system impossible to evaluate.

More data is required before deciding whether the Order Flow confirmation rule should be implemented.

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

The multi-scenario A/B diagnostic stayed local, offline, and research-only.

## 10. Next Validation Steps

1. Test more Sierra weekday sessions.
2. Run bullish and bearish A/B diagnostics on additional data.
3. Test larger iteration counts.
4. Track whether B continues to block everything.
5. Track whether B preserves valid trades when Order Flow becomes directional.
6. Export full price-level footprint data later.
7. Compare `BAR_SUMMARY` results against full footprint results.
8. Do not implement the Order Flow confirmation rule yet.
9. Do not start paper trading from this evidence.
10. Do not start live trading from this evidence.

The next goal is to determine whether B can reduce bad trades without eliminating all trades.

## 11. Beginner Summary

The bullish-labeled and bearish-labeled A/B runs produced the same result because both used the same explicit historical CSV.

The same historical run showed 8 SELL trades, all losing while Order Flow was neutral. Re-running it under the other scenario label produced the same output; this was not a second independent directional test.

That is useful, but there is a catch: the simulated rule blocked every trade. A rule that blocks everything may avoid losses, but it also gives no proof that the strategy can still find good trades.

This result supports more research, not implementation. Its value comes from the observed single-dataset behavior, not from duplicated bullish and bearish labels. More Sierra sessions and later full footprint data are still required.
