# Spread Filter

## Purpose
The Spread Filter is a safety layer for research, paper trading, and backtesting.

It prevents low-quality entries when transaction cost is likely too high.

If spread conditions are unsafe, the system should block new entries and report the reason clearly.

## Why This Filter Exists
Spread is part of real trading cost.

When spread gets wider, the trade starts with a larger disadvantage.

A setup that looks profitable on chart may become unprofitable after spread cost.

This filter is designed to keep behavior conservative:
- unknown spread can be blocked
- invalid spread is blocked
- high spread is blocked

## Why High Spread Is Dangerous
High spread can cause:
- worse entry price
- tighter stop loss getting hit faster
- lower reward-to-risk quality
- inflated backtest optimism if ignored

A high-spread entry can fail even when direction is correct.

## Spot Gold Spread Risk
Spot Gold instruments such as XAUUSD can have variable spread.

Spread often widens during:
- rollover windows
- low-liquidity periods
- high-impact news

Because of this, spread filtering is important even for paper trading and backtests.

## Futures Slippage and Tick Cost Note
Futures products often have tighter quoted spread than spot products.

However, futures still include execution friction:
- slippage
- commission
- tick-size cost

So spread checks should be used together with execution cost modeling in later versions.

## Current v1 Behavior
The filter returns one status per evaluation:
- SPREAD_ALLOWED
- SPREAD_TOO_HIGH
- SPREAD_UNKNOWN
- FILTER_DISABLED
- INVALID_SPREAD

Safe defaults in v1:
- filter is enabled
- max spread is 3.0
- unknown spread is blocked by default

## Future Plan
Future versions can improve spread handling with:
- instrument-specific thresholds
- session-specific thresholds
- separate spot and futures presets
- broker-specific spread adapters for simulation only
- combined spread + slippage cost gates before entry

## Scope and Safety
This module is research-only.

It does not place live orders, connect to brokers, or consume external market APIs.
