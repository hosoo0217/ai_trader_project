# CRT Engine v1

This document explains the first Candle Range Theory (CRT) engine used in this project.

## What CRT Means In This Project

CRT is a research module that studies how price behaves around a reference candle range.

It helps describe context such as:
- manipulation beyond range edges
- expansion away from range boundaries

It does not execute trades.

## Reference Candle Range

By default, CRT v1 uses the previous candle as the reference range.

The reference includes:
- reference high
- reference low
- reference open
- reference close

Each new candle is evaluated against that reference.

## Manipulation

Manipulation means price briefly pushes beyond a reference boundary.

### Low Manipulation

Condition:
- current low < reference low - buffer
- if require_close_back_inside is True, current close > reference low

Interpretation:
- potential bullish liquidity grab behavior

### High Manipulation

Condition:
- current high > reference high + buffer
- if require_close_back_inside is True, current close < reference high

Interpretation:
- potential bearish liquidity grab behavior

## Expansion

Expansion means the market closes (or optionally wicks) beyond the reference range.

### Bullish Expansion

Condition:
- current close > reference high + buffer
- if require_expansion_close is False, high-based expansion is allowed

### Bearish Expansion

Condition:
- current close < reference low - buffer
- if require_expansion_close is False, low-based expansion is allowed

## Bullish CRT Example

- Reference low: 1980.0
- Current low: 1978.8
- Current close: 1981.2
- Result: LOW_MANIPULATION, bullish context

Or:
- Reference high: 2000.0
- Current close: 2002.3
- Result: BULLISH_EXPANSION, bullish context

## Bearish CRT Example

- Reference high: 2000.0
- Current high: 2002.1
- Current close: 1998.9
- Result: HIGH_MANIPULATION, bearish context

Or:
- Reference low: 1980.0
- Current close: 1977.5
- Result: BEARISH_EXPANSION, bearish context

## Why CRT Alone Is Not An Entry Signal

CRT is only context evidence.

It must not be treated as direct trade execution logic.
Risk, confirmation, and multi-module alignment are required before any final decision.

## Future Plan

Future versions should combine CRT with:
- SMC context (structure, BOS/CHOCH, liquidity sweeps)
- Order Flow pressure and confirmation
- higher-timeframe alignment and risk gates
