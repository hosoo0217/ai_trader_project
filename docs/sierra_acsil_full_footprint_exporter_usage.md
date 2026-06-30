# Sierra ACSIL Full Footprint Exporter Usage

This document explains how to use the AI Trader Sierra Chart ACSIL full footprint CSV exporter.

The exporter is data export only. It does not change Python strategy logic, change Order Flow rules, implement Order Flow confirmation, place orders, connect a broker, or enable live trading.

## 1. Purpose

The purpose of the ACSIL exporter is to create full price-level footprint CSV data from loaded Sierra Chart bars.

Manual Sierra exports tested so far produced `BAR_SUMMARY` / study-summary data with one row per candle. The Order Flow engine needs full footprint data with multiple rows per candle, one row per price level.

## 2. Where The C++ File Is Located

The source file is:

```text
sierra_acsil/ai_trader_full_footprint_export.cpp
```

The exporter writes to:

```text
C:\Users\hosoo\Desktop\ai_trader_project\private_data\sierra_chart\gc_full_footprint_acsil_export.csv
```

The output path is under `private_data` and must not be committed.

The AI Trader Order Flow importer now supports this ACSIL CSV format directly.

## 3. How To Copy And Build It In Sierra Chart

1. Open the project folder.
2. Copy this file:

```text
sierra_acsil/ai_trader_full_footprint_export.cpp
```

3. Paste it into Sierra Chart's `ACS_Source` folder.
4. In Sierra Chart, open:

```text
Analysis > Build Custom Studies DLL
```

5. Select `ai_trader_full_footprint_export.cpp`.
6. Build the custom study DLL.

If the local Sierra Chart ACSIL version has slightly different member names for Volume-at-Price fields, adjust the comments marked in the C++ file before rebuilding.

Expected ACSIL members:

- `sc.MaintainVolumeAtPriceData`
- `sc.VolumeAtPriceForBars`
- `GetSizeAtBarIndex`
- `GetVAPElementAtIndex`
- `sc.TickSize`
- `sc.BaseDateTimeIn`

## 4. How To Add The Study To A Chart

1. Open a Sierra Chart chart with the desired GC data loaded.
2. Make sure the chart has enough loaded history for the validation run.
3. Open:

```text
Analysis > Studies
```

4. Add:

```text
AI Trader Full Footprint CSV Exporter
```

5. Apply the study to the chart.

The study sets `sc.MaintainVolumeAtPriceData = 1` so Sierra maintains Volume-at-Price data for loaded bars.

## 5. How To Trigger Export

The study has an input:

```text
Export Now
```

To export:

1. Open the study settings.
2. Set `Export Now` to `Yes`.
3. Apply the settings.
4. Check Sierra Chart's message log for the export completion message.
5. After export, set `Export Now` back to `No` if you do not want repeated rewrites.

The exporter writes a local CSV file only. It does not place trades or call external services.

## 6. Expected CSV Format

The expected CSV header is:

```text
DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
```

This exact header is recognized by the Order Flow importer as `ACSIL_FULL_FOOTPRINT`.

Expected row fields:

- `DateTime`: chart bar timestamp.
- `BarIndex`: Sierra chart bar index.
- `Price`: price level inside the bar.
- `BidVolume`: bid volume at that price.
- `AskVolume`: ask volume at that price.
- `TotalVolume`: total volume at that price.
- `Delta`: `AskVolume - BidVolume`.
- `NumTrades`: trade count when available, otherwise `0`.

One bar should produce multiple rows when multiple price levels exist.

That repeated `DateTime` / `BarIndex` pattern is what makes this full footprint data instead of OHLC summary data.

## 7. How To Validate The CSV

The export is valid only if:

- the file exists under `private_data/sierra_chart`,
- the header matches the expected format,
- `Price` column exists,
- `BidVolume` column exists,
- `AskVolume` column exists,
- `TotalVolume` column exists,
- `Delta` column exists,
- one timestamp appears on multiple rows,
- one `BarIndex` appears on multiple rows,
- row count is greater than candle count.

If each candle has only one row, the file is still summary data and should not be used as full footprint data.

When imported successfully, data quality should show:

- candle count equal to the number of unique loaded bars,
- total levels equal to the number of price-level rows,
- source format `ACSIL_FULL_FOOTPRINT`.

## 8. Safety Confirmation

- No live trading.
- No broker connection.
- No order placement.
- No real execution.
- No MT5 login.
- No CME live execution.
- No external API calls.
- No strategy logic changed.
- No Order Flow rules changed.
- No Order Flow confirmation rule implemented.
- No `private_data` committed.

This exporter only reads loaded Sierra Chart Volume-at-Price data and writes a local CSV file.

## 9. Beginner Summary

The usual Sierra exports gave only one row per candle, which is not enough for real footprint analysis.

This ACSIL study exports every price level inside every loaded chart bar. That means one candle can create many rows: one row for each price level, with bid volume, ask volume, total volume, delta, and trade count.

The output file is private research data. It should stay in `private_data` and should not be committed.
