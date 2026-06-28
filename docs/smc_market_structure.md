# SMC Market Structure v1

This document explains the first Smart Money Concepts (SMC) market structure module used in this project.

## Scope

This module is research-only and backtesting-only.

It does not:
- place live orders
- connect to real brokers
- use MT5 or Sierra live feeds
- generate final trade signals by itself

It only analyzes structure from OHLC candles.

## Swing High

A swing high is a candle whose high is greater than highs on both its left and right sides.

With swing_lookback = 2:
- current high must be greater than previous 2 highs
- current high must be greater than next 2 highs

## Swing Low

A swing low is a candle whose low is lower than lows on both its left and right sides.

With swing_lookback = 2:
- current low must be lower than previous 2 lows
- current low must be lower than next 2 lows

## Structure Bias Logic (v1)

The v1 logic compares the latest two swing highs and latest two swing lows.

- BULLISH:
  - latest swing high > previous swing high
  - latest swing low > previous swing low
- BEARISH:
  - latest swing high < previous swing high
  - latest swing low < previous swing low
- NEUTRAL:
  - mixed structure (one side up, one side down, or equal)
- UNKNOWN:
  - not enough valid data or swings to classify

## Why This Is v1 Only

This first version is intentionally simple.

It gives a clean baseline for testing and explainability before adding advanced structure logic.
It should not be treated as final trading logic.

## Future Plan

Planned improvements include:
- BOS (Break of Structure) detection
- CHOCH (Change of Character) detection
- stronger noise filtering and validation
- multi-timeframe structure alignment
- integration into richer SMC context scoring
