# Order Flow Footprint Data Model

This document explains the first version of the footprint data model used by the research and backtesting system.

This is not live trading infrastructure. It does not connect to a broker, Sierra Chart, CME, or any external market data API.

## What Footprint Data Means

Footprint data breaks one candle into price levels and shows how much volume traded at each level.

Instead of only looking at open, high, low, and close, a footprint candle can answer:

- where most volume traded inside the candle
- whether bid-side or ask-side activity was stronger
- which price level had the most participation
- whether pressure looked more buy-sided or sell-sided

## Bid Volume

Bid volume is volume traded at the bid side of the market.

In this project, bid volume is modeled as selling pressure for simple research calculations. Higher bid volume can suggest stronger aggressive selling activity inside the candle.

## Ask Volume

Ask volume is volume traded at the ask side of the market.

In this project, ask volume is modeled as buying pressure for simple research calculations. Higher ask volume can suggest stronger aggressive buying activity inside the candle.

## Delta

Delta measures the difference between ask volume and bid volume:

```text
delta = ask volume - bid volume
```

Positive delta means ask volume was greater than bid volume. Negative delta means bid volume was greater than ask volume.

This is a simple model for research. Delta does not guarantee direction by itself; it should eventually be combined with market context, structure, risk, and other evidence.

## Point of Control

Point of Control, often shortened to POC, is the price level with the highest total volume.

In this model:

```text
total volume = bid volume + ask volume
```

The footprint analyzer finds the level with the largest total volume and stores that price as the point of control.

## Why This Is Data Modeling v1

This version only defines basic Python dataclasses and summary calculations:

- `FootprintLevel`
- `FootprintCandle`
- `FootprintSummary`
- `FootprintAnalyzer`

It is intentionally small so the project can test the meaning of footprint data before using it in any decision flow.

This version does not:

- import Sierra Chart files
- connect to live data
- connect to CME
- connect to a broker
- place trades
- change `PaperTradingFlow`

## Future Plan: Sierra Chart CSV Import

A future version can add a CSV importer for exported Sierra Chart footprint or numbers-bars data.

The planned workflow is:

1. Export historical footprint data from Sierra Chart as CSV.
2. Load that CSV from disk during research or backtesting.
3. Convert rows into `FootprintCandle` and `FootprintLevel` objects.
4. Run `FootprintAnalyzer` summaries.
5. Later, feed summarized order flow evidence into `DecisionContext`.

That future importer should remain offline and file-based unless live integration is explicitly designed and approved later.
