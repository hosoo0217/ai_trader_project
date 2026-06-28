# Order Flow Imbalance Analyzer v1

This document explains the first order flow imbalance analyzer used by this project.

This module is research-only.
It does not connect to live trading systems, brokers, Sierra Chart live feeds, CME live feeds, or external APIs.

## What Imbalance Means

Imbalance describes one-sided aggression at a specific price level inside a footprint candle.

At each level, we compare ask volume and bid volume using a ratio threshold.
If one side is much larger than the other, that level is flagged as an imbalance.

## Ask Imbalance

Ask imbalance means buy-side aggression is dominant at that level.

v1 detection rule:
- ask_volume / bid_volume >= imbalance_ratio_threshold
- total level volume >= min_volume

Special strong case:
- bid_volume is 0
- ask_volume >= min_volume

This is treated as a strong ask imbalance.

## Bid Imbalance

Bid imbalance means sell-side aggression is dominant at that level.

v1 detection rule:
- bid_volume / ask_volume >= imbalance_ratio_threshold
- total level volume >= min_volume

Special strong case:
- ask_volume is 0
- bid_volume >= min_volume

This is treated as a strong bid imbalance.

## Why Imbalance Can Show Aggressive Buyers or Sellers

Imbalance highlights where one side consumed more liquidity than the other at a specific price.

Clusters of ask imbalances can suggest aggressive buying pressure.
Clusters of bid imbalances can suggest aggressive selling pressure.

In v1, candle bias is summarized by comparing counts:
- more ask imbalances -> BULLISH
- more bid imbalances -> BEARISH
- equal counts -> NEUTRAL

## Why Imbalance Alone Is Not a Trade Signal

Imbalance analysis only describes order flow behavior.

It does not execute trades and does not generate direct entry signals.
It should be treated as one piece of evidence alongside broader context.

## Future Plan

Future versions can combine imbalance context with:
- Delta / CVD trend behavior
- SMC structure context
- CRT context

The long-term goal is better context quality for research and backtesting while staying safe and modular.
