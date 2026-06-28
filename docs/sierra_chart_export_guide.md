# Sierra Chart CSV Export Guide

This project uses exported Sierra Chart CSV files first. It does not connect to
Sierra Chart live data, CME live data, brokers, or any live trading system.

The goal is to validate footprint and Order Flow logic in a research/backtesting
workflow before any future live-data work is considered.

## Why CSV Export Is Needed

Order Flow analysis needs footprint data: bid volume and ask volume at each
price level inside a candle. Standard OHLC candles do not contain that level of
detail.

For now, Sierra Chart should be used only to export historical footprint data to
CSV. The CSV can then be loaded by this project with `SierraChartImporter`.

## Required Normalized Fields

The importer maps CSV headers into these normalized fields:

- `time`
- `open`
- `high`
- `low`
- `close`
- `price`
- `bid_volume`
- `ask_volume`

Some common header variants are supported, such as `Date Time`, `Last`,
`Level`, `Bid Volume`, and `Ask Volume`.

## Field Meanings

- `time`: candle time. Rows with the same time are grouped into one candle.
- `open`: candle open price.
- `high`: candle high price.
- `low`: candle low price.
- `close`: candle close price.
- `price`: footprint price level inside the candle.
- `bid_volume`: traded volume at the bid for that price level.
- `ask_volume`: traded volume at the ask for that price level.

## Row Structure

One candle can have many rows.

The same `time` value groups rows into one `FootprintCandle`. Each row becomes
one `FootprintLevel`.

Example:

```csv
time,open,high,low,close,price,bid_volume,ask_volume
2026-06-26T14:00:00Z,2300.0,2301.0,2299.5,2300.8,2299.5,20,35
2026-06-26T14:00:00Z,2300.0,2301.0,2299.5,2300.8,2300.0,25,45
2026-06-26T14:00:00Z,2300.0,2301.0,2299.5,2300.8,2300.5,30,55
```

Those three rows become one footprint candle with three price levels.

## Safe Blocking

Bad or missing columns will block Order Flow safely. If required fields cannot
be resolved, the importer returns no candles and the data-quality gate keeps
Order Flow inactive.

This protects the demo from treating incomplete CSV data as useful market
context.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv data/sierra_chart_footprint_template.csv --show-trace
```

## Research First

This is research/backtesting first, not live trading. The CSV path is a safe way
to test Order Flow Context before any future Sierra Chart export variant or
workflow is added.
