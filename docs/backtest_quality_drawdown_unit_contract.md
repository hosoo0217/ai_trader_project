# Backtest Quality Drawdown Unit Contract

## Purpose

Define one explicit unit contract for backtest max drawdown evaluation after simulated PnL was corrected to include instrument point value.

This policy is research-only. It does not approve paper trading, broker integration, live data, or live trading.

## Raw performance metric

`PerformanceReport.max_drawdown` remains an absolute monetary peak-to-trough amount calculated from the cumulative realized-PnL sequence.

The raw metric is not a percentage and is not measured in R.

## Quality normalization

Backtest quality converts the raw monetary drawdown into account percentage:

`drawdown_percent = max_drawdown / account_balance * 100`

A positive account balance is required for this calculation.

This makes drawdown evaluation comparable across profiles with different account balances and point values.

## Threshold policy

No universal maximum drawdown percentage has been approved.

Therefore:

- `max_drawdown_percent_allowed` defaults to `None`
- sufficient-data quality evaluation fails closed when the threshold is not configured
- the output reports `NOT_CONFIGURED`
- an explicit positive percentage threshold is required before drawdown can pass
- an arbitrary value must not be inferred from old raw-PnL reports

## Daily loss is separate

`max_daily_loss` is a realized-PnL limit for one UTC trading day.

Backtest max drawdown is a peak-to-trough metric across the full realized trade sequence.

The daily loss limit must not be reused automatically as the total backtest drawdown threshold.

## Point-value correction impact

After monetary PnL began including point value:

- trade count remained unchanged
- win rate remained unchanged
- profit factor remained unchanged
- monetary PnL and monetary max drawdown scaled consistently with point value

Historical reports produced before that correction may use the earlier smaller monetary scale and must not be treated as directly comparable threshold evidence.

## Fail-closed requirements

Backtest quality must fail rather than silently pass when:

- account balance is missing or non-positive
- drawdown percentage threshold is missing
- drawdown percentage threshold is non-positive
- calculated drawdown percentage exceeds the configured threshold

## Current Apex diagnostic checkpoint

For the matched 5m, 200-iteration Apex diagnostic:

- executed trades: 38
- total monetary PnL: 2700
- monetary max drawdown: 300
- starting balance: 50000
- normalized max drawdown: 0.60%
- approved threshold: not configured
- quality result: failed closed

This result describes accounting and quality-gate behavior only. It does not approve a strategy rule or trading deployment.
