# Deeper Historical Backtest Current Baseline

Status: research-only historical validation completed on 2026-07-12.

This document records the current authoritative 200-iteration baseline after the simulated PnL `point_value` fix.

No strategy rule, risk rule, broker behavior, paper-trading permission, live-trading permission, or Order Flow enforcement was changed.

## 1. Data Source

Local ignored dataset:

`private_data/sierra_chart/bulk_30d_sc_delayed`

Source:

- Sierra Chart delayed historical exports
- 22 matched sessions
- 0 mismatched sessions
- 0 bad timestamp rows
- separate matched market OHLC and full footprint CSV files
- no live Sierra connection
- no CME live connection
- no broker or external API connection

Time ranges:

- 1m: 2026-06-03 18:00:00 to 2026-07-03 12:23:00
- 5m: 2026-06-03 18:00:00 to 2026-07-03 12:00:00
- 10m: 2026-06-03 18:00:00 to 2026-07-03 11:40:00

## 2. Validation Scope

Each timeframe was run with:

- Apex profile
- 200 maximum rolling iterations
- matched historical market CSV
- corresponding full footprint CSV
- current code after commit `4ec6c78 fix: apply point value to simulated pnl`
- diagnostic Order Flow A/B export enabled by the bulk runner
- outputs written only under ignored `private_data`

The existing bulk runner was used. No strategy or risk behavior was modified.

## 3. Current Authoritative Results

| Timeframe | Iterations | Executed | Blocked | Wins | Losses | Win rate | Total PnL | Profit factor | Max drawdown | Drawdown % | Quality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1m | 200 | 18 | 182 | 8 | 10 | 44.44% | 200.00 | 1.20 | 600.00 | 1.20% | INSUFFICIENT_DATA |
| 5m | 200 | 38 | 162 | 26 | 12 | 68.42% | 2700.00 | 3.25 | 300.00 | 0.60% | FAILED |
| 10m | 200 | 46 | 154 | 19 | 27 | 41.30% | 150.00 | 1.06 | 1100.00 | 2.20% | FAILED |

## 4. Quality Interpretation

### 1m

- Quality: `INSUFFICIENT_DATA`
- Executed trades were below the reliability requirement.
- Positive PnL does not override the insufficient sample.
- More executed examples are required.

### 5m

- Quality: `FAILED`
- Performance metrics were positive.
- The quality gate remained fail-closed because the maximum drawdown percentage threshold was not configured.
- This result is not deployment approval.

### 10m

- Quality: `FAILED`
- Win rate was below the required minimum.
- Profit factor was below the required minimum.
- The maximum drawdown percentage threshold was not configured.
- The thin positive PnL does not make this result acceptable.

## 5. Order Flow Data Quality

Order Flow footprint data quality passed for all three timeframes.

Observed imported data:

- 1m: 25,614 candles and 532,290 price levels
- 5m: 5,125 candles and 284,546 price levels
- 10m: 2,561 candles and 209,761 price levels
- invalid levels: 0
- invalid level ratio: 0.00

The global full-file Order Flow context remained neutral or inactive.

Order Flow remains diagnostic-only. These results do not justify enforcement.

## 6. Scenario-Label Limitation

The bulk runner executed both `--scenario bullish` and `--scenario bearish`.

Because an explicit `--backtest-market-csv` was supplied, both labels used the same historical candles and the same strategy path.

The scenario flag did not:

- transform the historical CSV
- force bullish or bearish market direction
- create independent directional datasets
- create a second independent validation sample

Therefore, matching bullish-labeled and bearish-labeled outputs must be treated as duplicate evidence from the same dataset, not directional replication.

The authoritative table above records each timeframe once.

## 7. Comparison With Older Reports

Older bulk diagnostic reports were generated before the `point_value` correction.

Their trade counts, wins, losses, win rates, and profit factors remain useful when unchanged.

Their monetary PnL and monetary max drawdown values are not authoritative under the current contract.

Current corrected monetary baseline:

- 1m PnL: 200.00; max drawdown: 600.00
- 5m PnL: 2700.00; max drawdown: 300.00
- 10m PnL: 150.00; max drawdown: 1100.00

## 8. Current Decision

The deeper historical baseline is now reproduced under the current monetary contract.

The project is not ready for live trading.

The evidence does not approve:

- Order Flow enforcement
- conditional cooldown enforcement
- automatic strategy changes
- paper-trading progression
- broker integration
- real order execution

Remaining research includes:

- more independent historical periods
- true regime-separated datasets
- configured and reviewed drawdown thresholds
- losing-trade trace review
- out-of-sample validation
- robustness validation before any paper-trading preparation
