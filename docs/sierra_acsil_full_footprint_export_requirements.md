# Sierra ACSIL Full Footprint Export Requirements

This document defines the requirements for the current data-only Sierra Chart ACSIL full footprint exporter for `ai_trader_project`.

It is documentation only. It does not implement Python strategy logic, change Order Flow rules, implement the Order Flow confirmation rule, connect a broker, place orders, or enable live trading.

## 1. Purpose

The purpose of this document is to define the required Sierra Chart export format for true price-level footprint data.

Manual Sierra Chart exports tested so far produced `BAR_SUMMARY` or study-summary style data. That data is useful for early import validation, but it is not full footprint data.

The AI Trader Order Flow engine needs one row per price level inside each chart bar.

## 2. Manual Exports Tested So Far

The following manual Sierra Chart exports were tested:

- Export Intraday Data to Text File
- Export Bar and Study Data to Text File

These exports produced bar-level data such as:

- one row per candle,
- `Date`,
- `Time`,
- `Open`,
- `High`,
- `Low`,
- `Last`,
- `Volume`,
- bar-level `Bid Volume`,
- bar-level `Ask Volume`,
- bar-level `Delta`.

This is `BAR_SUMMARY` / study-summary style data.

It is not full price-level footprint data.

## 3. Problem

The current manual exports summarize each candle into one row.

Full footprint data requires multiple rows per candle:

- one chart bar must have multiple rows,
- each row must represent one price level inside the bar,
- each row must include Bid Volume,
- each row must include Ask Volume,
- each row must include Total Volume,
- each row must include Delta.

Without this structure, Order Flow can load a safe early context, but it cannot evaluate true price-level footprint behavior.

## 4. ACSIL Direction

The current data-only exporter is implemented as a Sierra Chart ACSIL custom study.

Official Sierra Chart ACSIL direction:

- `sc.MaintainVolumeAtPriceData = 1`
- `sc.VolumeAtPriceForBars`
- `GetSizeAtBarIndex`
- `GetVAPElementAtIndex`

The custom study must read Volume At Price data from loaded chart bars and write a local CSV file.

## 5. Required CSV Output Format

The required CSV header is:

```text
DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
```

The AI Trader Order Flow importer supports this ACSIL full footprint header and marks imported candles as `ACSIL_FULL_FOOTPRINT`.

Required columns:

- `DateTime`: timestamp for the chart bar.
- `BarIndex`: Sierra chart bar index.
- `Price`: price level inside the bar.
- `BidVolume`: bid volume at that price level.
- `AskVolume`: ask volume at that price level.
- `TotalVolume`: total volume at that price level.
- `Delta`: ask volume minus bid volume.
- `NumTrades`: trade count at that price level when available.

## 6. Required Export Behavior

The current data-only ACSIL exporter must:

- export loaded chart bars only,
- write to the fixed, truncating output path `private_data/sierra_chart/gc_full_footprint_acsil_export.csv`, which must be preserved under a unique filename before another export starts,
- write one row per bar per price level,
- include a header row,
- preserve repeated `DateTime` values when a bar has multiple price levels,
- preserve repeated `BarIndex` values when a bar has multiple price levels,
- write only local CSV data,
- avoid tracked data folders.

The output file must stay under `private_data`.

Do not commit `private_data` files.

Before another export starts, record the exact header, first and last timestamps, unique-bar count, total data-row count, file size, and SHA-256 hash, then verify that the preserved copy has the same hash.

## 7. Validation Requirements

The exported file is valid only if:

- one timestamp appears on multiple rows,
- `Price` column exists,
- `BidVolume` column exists,
- `AskVolume` column exists,
- `TotalVolume` column exists,
- `Delta` column exists,
- `BarIndex` repeats across multiple price levels,
- row count is greater than candle count.
- `DateTime` is parseable and `BarIndex` and `Price` are numeric.
- `BidVolume`, `AskVolume`, `TotalVolume`, and `NumTrades` are numeric and non-negative.
- `Delta` equals `AskVolume - BidVolume` on every row.

If each candle has only one row, the file is still summary data and must not be treated as full footprint data.

For a valid ACSIL full footprint import, Order Flow data quality must pass, candle count must equal the number of unique bars, and total levels must equal the number of price-level rows.

A passing importer or Order Flow data-quality result does not establish an evidence classification. Any candidate for independent validation must satisfy `docs/independent_historical_dataset_intake.md`, including non-overlap, complete timeframe-matched Market OHLC/full-footprint pairs, metadata, gaps, matching, traceability, and overwrite protection.

## 8. Safety Requirements

The ACSIL exporter must remain data-export only.

Safety requirements:

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live integration; loaded chart data may be read only for local offline export.
- No CME live execution.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No trading logic.
- No order placement.

The exporter must only read loaded chart data and write a local CSV file.

## 9. Current Implementation and Code Freeze

The current data-only ACSIL C++ custom study exporter is:

```text
sierra_acsil/ai_trader_full_footprint_export.cpp
```

The current implementation must remain data-export only. Code freeze is active, and this contract does not authorize changes to exporter source code.

It must not change Python strategy logic.

It must not change Order Flow rules.

It must not implement the Order Flow confirmation rule.

## 10. Beginner Summary

The Sierra exports tested so far only gave one row per candle. That is not enough for real footprint analysis.

A real footprint export needs many rows per candle: one row for each price level traded inside that candle.

The current data-only ACSIL exporter must read Sierra Chart Volume At Price data and save it to a private CSV with price, bid volume, ask volume, total volume, delta, and trade count.

This is only for better research data. It is not trading logic and must not place orders or connect to a broker.
