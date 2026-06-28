# Order Flow Delta / CVD Analyzer v1

This document explains the first Delta and Cumulative Volume Delta (CVD) analyzer used in this project.

This module is research-only.
It does not connect to live feeds, brokers, Sierra Chart live data, CME live data, or external APIs.

## What Delta Means

Delta measures buy-side minus sell-side aggressive volume within one footprint candle.

In this project:
- ask volume represents buying-side aggression
- bid volume represents selling-side aggression

Formula:
- delta = ask volume - bid volume

## What Cumulative Delta Means

Cumulative Delta (CVD) is a running sum of candle deltas across time.

If candle deltas are d1, d2, d3, then:
- cvd1 = d1
- cvd2 = d1 + d2
- cvd3 = d1 + d2 + d3

This helps track pressure build-up over multiple candles instead of only one candle at a time.

## Buying Pressure

A candle is classified as BUYING_PRESSURE when:
- delta > strong_delta_threshold

This means buy-side aggressive volume is clearly stronger than sell-side volume for that candle.

## Selling Pressure

A candle is classified as SELLING_PRESSURE when:
- delta < -strong_delta_threshold

This means sell-side aggressive volume is clearly stronger than buy-side volume for that candle.

## Neutral

A candle is classified as NEUTRAL when delta is inside threshold bounds.

This avoids overreacting to small differences in bid/ask volume.

## Why CVD Is Useful

CVD can help show whether pressure is building in one direction over time.

This can support research questions such as:
- is buying pressure persisting across multiple candles?
- is selling pressure fading or strengthening?
- does price move align with underlying aggressive volume trend?

## Why This Is Research Logic Only

This analyzer does not create orders and does not execute trades.

It is a context tool for backtesting and analysis only.
Any future decision use must still pass broader safety, risk, and context validation.

## Future Plan

Future versions may combine Delta/CVD context with:
- SMC structure context
- CRT context
- alignment gates and risk filters

The focus remains safe, testable research components.
