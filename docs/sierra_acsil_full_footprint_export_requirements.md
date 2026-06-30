# Sierra ACSIL Full Footprint Export Requirements

This document defines the requirements for a future Sierra Chart ACSIL full footprint exporter for `ai_trader_project`.

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

- one chart bar should have multiple rows,
- each row should represent one price level inside the bar,
- each row should include Bid Volume,
- each row should include Ask Volume,
- each row should include Total Volume,
- each row should include Delta.

Without this structure, Order Flow can load a safe early context, but it cannot evaluate true price-level footprint behavior.

## 4. ACSIL Direction

The future exporter should use a Sierra Chart ACSIL custom study.

Official Sierra Chart ACSIL direction:

- `sc.MaintainVolumeAtPriceData = 1`
- `sc.VolumeAtPriceForBars`
- `GetSizeAtBarIndex`
- `GetVAPElementAtIndex`

The custom study should read Volume At Price data from loaded chart bars and write a local CSV file.

## 5. Required CSV Output Format

The required CSV header is:

```text
DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
```

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

The future ACSIL exporter should:

- export loaded chart bars only,
- write to `private_data/sierra_chart/gc_full_footprint_acsil_export.csv`,
- write one row per bar per price level,
- include a header row,
- preserve repeated `DateTime` values when a bar has multiple price levels,
- preserve repeated `BarIndex` values when a bar has multiple price levels,
- write only local CSV data,
- avoid tracked data folders.

The output file must stay under `private_data`.

Do not commit `private_data` files.

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

If each candle has only one row, the file is still summary data and should not be treated as full footprint data.

## 8. Safety Requirements

The ACSIL exporter must remain data-export only.

Safety requirements:

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection beyond reading loaded chart data.
- No CME live execution.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No trading logic.
- No order placement.

The exporter should only read loaded chart data and write a local CSV file.

## 9. Next Implementation Step

The next implementation step, later, is to create an ACSIL C++ custom study exporter file, likely:

```text
sierra_acsil/ai_trader_full_footprint_export.cpp
```

That future implementation should follow this document and remain data-export only.

It should not change Python strategy logic.

It should not change Order Flow rules.

It should not implement the Order Flow confirmation rule.

## 10. Beginner Summary

The Sierra exports tested so far only gave one row per candle. That is not enough for real footprint analysis.

A real footprint export needs many rows per candle: one row for each price level traded inside that candle.

The future ACSIL exporter should read Sierra Chart Volume At Price data and save it to a private CSV with price, bid volume, ask volume, total volume, delta, and trade count.

This is only for better research data. It is not trading logic and must not place orders or connect to a broker.
