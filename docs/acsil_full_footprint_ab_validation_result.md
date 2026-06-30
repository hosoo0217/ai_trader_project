# ACSIL Full Footprint A/B Validation Result

This document records the research-only A/B validation result using a real Sierra Chart ACSIL full price-level footprint CSV.

It is documentation only. It does not edit Python code, change strategy logic, implement Order Flow confirmation, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record the first A/B validation result after importing real ACSIL full price-level footprint data.

This validation checks whether the project can use full footprint Order Flow data, not only `BAR_SUMMARY` data, while comparing:

- A: current strategy behavior,
- B: simulated Order Flow confirmation behavior.

B remained diagnostic only. It did not change actual execution decisions.

## 2. Test Setup

Private ACSIL full footprint file:

```text
private_data/sierra_chart/gc_full_footprint_acsil_export.csv
```

The private file must not be committed.

Backtest market candles used:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

Market candles were loaded using Sierra `BAR_SUMMARY` positional OHLC.

Order Flow context used:

```text
private_data/sierra_chart/gc_full_footprint_acsil_export.csv
```

Order Flow source was `ACSIL_FULL_FOOTPRINT`.

The A/B diagnostic used `--simulate-orderflow-confirmation-ab`.

## 3. ACSIL Full Footprint Import Validation

Importer result:

- Source: `ACSIL_FULL_FOOTPRINT`
- Data quality: `PASSED`
- Invalid levels: `0`
- Invalid level ratio: `0.00`

This confirms that the ACSIL full footprint CSV was imported successfully.

This is no longer `BAR_SUMMARY`-only Order Flow validation.

The imported data contains many price levels per candle, which is the required structure for full footprint analysis.

## 4. Bullish A/B Result

### Bullish Setup

- Backtest market candles: `gc_weekday_test.csv` using `BAR_SUMMARY` positional OHLC
- Order Flow CSV: `gc_full_footprint_acsil_export.csv` using `ACSIL_FULL_FOOTPRINT`

### A Current Behavior

Observed bullish A result:

- Total iterations: `50`
- A executed trades: `8`
- A blocked trades: `42`
- A PnL: `-80.00`
- A win rate: `0.00%`
- A max drawdown: `80.00`

Observed bullish Order Flow context:

- Order Flow bias: `NEUTRAL`
- Order Flow confidence: `0.0`
- Delta direction: `NEUTRAL`
- Imbalance bias: `NEUTRAL`
- Absorption bias: `NEUTRAL`
- Final CVD: `-2862.00`
- Candle count: `2199`
- Total levels: `43320`

### B Simulated Behavior

Observed bullish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- B would block `8` trades by Order Flow confirmation.
- B would block `8` trades because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B blocked every A executed trade`

In the bullish full footprint validation, B would have blocked the 8 losing A trades.

## 5. Bearish A/B Result

### Bearish Setup

- Backtest market candles: `gc_weekday_test.csv` using `BAR_SUMMARY` positional OHLC
- Order Flow CSV: `gc_full_footprint_acsil_export.csv` using `ACSIL_FULL_FOOTPRINT`

### A Current Behavior

Observed bearish A result:

- Total iterations: `50`
- A executed trades: `8`
- A blocked trades: `42`
- A PnL: `-80.00`
- A win rate: `0.00%`
- A max drawdown: `80.00`

Observed bearish Order Flow context:

- Order Flow bias: `NEUTRAL`
- Order Flow confidence: `0.0`
- Delta direction: `NEUTRAL`
- Imbalance bias: `NEUTRAL`
- Absorption bias: `NEUTRAL`
- Final CVD: `-69.00`
- Candle count: `907`
- Total levels: `16032`

### B Simulated Behavior

Observed bearish B result:

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- B would block `8` trades by Order Flow confirmation.
- B would block `8` trades because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B blocked every A executed trade`

In the bearish full footprint validation, B would also have blocked the 8 losing A trades.

## 6. Shared Pattern

Shared pattern across bullish and bearish runs:

- ACSIL full footprint import worked.
- Data quality passed.
- Order Flow still evaluated as `NEUTRAL`.
- Current A behavior still executed 8 losing trades.
- Simulated B would block those 8 neutral Order Flow losing trades.
- B simulated zero executed trades.
- B blocked every A executed trade.

The full footprint data strengthens the validation because Order Flow was no longer based on one synthetic `BAR_SUMMARY` level per candle.

## 7. What This Proves

This validation proves:

- The ACSIL full footprint CSV importer works.
- The importer can load many price levels per candle.
- Data quality can pass on real ACSIL full footprint exports.
- The Order Flow pipeline can consume `ACSIL_FULL_FOOTPRINT` data.
- The A/B diagnostic can run with full footprint Order Flow context.
- In this dataset, simulated B would have blocked the known losing neutral-Order-Flow trades.

This is important infrastructure and validation progress.

## 8. What Remains Unproven

This validation does not prove:

- B is profitable.
- The Order Flow confirmation rule should be implemented.
- B can find winning trades.
- B will preserve enough valid trades.
- B will work on more full footprint sessions.
- Neutral Order Flow should always block all trades.
- The strategy is ready for paper trading.
- The strategy is ready for live trading.

More full footprint sessions are required before any strategy implementation decision.

## 9. Main Warning

Main warning:

```text
B blocked every A executed trade
```

This remains a major warning.

B avoided the known losing trades in this dataset, but it also left zero simulated executed trades. A rule that blocks every trade may reduce losses, but it does not prove that profitable trades can still be found.

## 10. Safety Confirmation

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live order connection.
- No CME live execution.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No strategy rule implemented.

The validation stayed local, offline, and research-only.

## 11. Next Validation Steps

1. Test more ACSIL full footprint Sierra sessions.
2. Run bullish and bearish A/B diagnostics on additional full footprint exports.
3. Compare full footprint behavior against previous `BAR_SUMMARY` behavior.
4. Track whether Order Flow remains neutral or becomes directional on richer data.
5. Track whether B continues to block every A executed trade.
6. Confirm B can preserve valid trades before considering implementation.
7. Do not implement Order Flow confirmation yet.
8. Do not start paper trading from this evidence.
9. Do not start live trading from this evidence.
10. Require final human review before any implementation plan.

The next goal is to determine whether full footprint data can produce useful directional Order Flow confirmation across more sessions.

## 12. Beginner Summary

The project can now import real full footprint data from Sierra Chart ACSIL. That is a big step because the data has many price levels per candle instead of just one summary row.

Even with full footprint data, Order Flow was still neutral in both the bullish and bearish 50-iteration tests. The current system still took 8 losing trades, and the simulated Order Flow confirmation rule would have blocked them.

That is useful, but it is not enough to implement the rule. The simulated rule still blocked every trade, so it has not proven it can find winners. More full footprint sessions are required before changing strategy logic.
