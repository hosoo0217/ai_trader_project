# SMC Liquidity Sweep v1

This document explains the first liquidity sweep analyzer in this project.

## Scope

This logic is research-only and backtesting-only.

It does not:
- execute live trades
- connect to live brokers
- use MT5 or Sierra Chart live feeds
- act as a standalone entry system

## What Liquidity Means

In SMC context, liquidity often sits around obvious highs and lows where many stop orders can collect.

A sweep happens when price pushes through those levels to grab liquidity before potentially reversing.

## What High Sweep Means

A high sweep means price moves above a prior swing high.

Rule:
- candle high > swing high + buffer
- if require_close_back_inside is True, candle close must be below that swing high

Interpretation:
- this can indicate a bearish liquidity grab
- v1 direction label: BEARISH

## What Low Sweep Means

A low sweep means price moves below a prior swing low.

Rule:
- candle low < swing low - buffer
- if require_close_back_inside is True, candle close must be above that swing low

Interpretation:
- this can indicate a bullish liquidity grab
- v1 direction label: BULLISH

## Why Close Back Inside Matters

A wick through a level can be noise.

Requiring close back inside helps filter weak moves and keeps focus on rejection behavior.

## Bullish Sweep Example

- Swing low: 1980.0
- Candle low: 1978.8 (sweep below)
- Candle close: 1981.2 (back above level)
- Result: LOW_SWEEP, BULLISH bias

## Bearish Sweep Example

- Swing high: 2000.0
- Candle high: 2002.1 (sweep above)
- Candle close: 1999.4 (back below level)
- Result: HIGH_SWEEP, BEARISH bias

## Why Sweep Alone Is Not an Entry Signal

A sweep can happen in many market conditions and may fail quickly.

This module only reports structure behavior. It does not apply full confirmation, risk control, or execution rules.

## Future Plan

Future versions should combine:
- liquidity sweep
- BOS/CHOCH confirmation
- CRT confirmation
- Order Flow evidence
- risk and context gating before any decision logic
