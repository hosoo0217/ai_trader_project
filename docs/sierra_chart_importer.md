# Sierra Chart Footprint CSV Importer v1

This document explains the first Sierra Chart-style footprint CSV importer used by this project.

This importer is offline only.
It does not connect to Sierra Chart live data, CME, brokers, or any external API.

## Purpose

The importer converts historical CSV rows into in-memory footprint objects for research and backtesting.

The output objects are:
- FootprintCandle
- FootprintLevel

These can be analyzed by FootprintAnalyzer.

## Expected CSV Columns (v1)

The v1 importer expects these columns:
- time
- open
- high
- low
- close
- price
- bid_volume
- ask_volume

Column names can be remapped with SierraChartImportConfig.

## Mapping Rules

Rows are grouped by time.

For each time group:
- one FootprintCandle is created
- each row becomes one FootprintLevel

OHLC mapping per grouped candle:
- open: first open value
- high: max high value
- low: min low value
- close: last close value

Footprint level mapping per row:
- price -> FootprintLevel.price
- bid_volume -> FootprintLevel.bid_volume
- ask_volume -> FootprintLevel.ask_volume

Safety handling:
- negative bid or ask volume is converted to 0
- missing required columns returns empty list
- empty CSV/DataFrame returns empty list
- invalid rows are skipped safely where needed

## Why v1 Is Simplified

Real Sierra Chart exports can contain richer formats and additional structure.

This v1 importer intentionally focuses on a small and stable subset so the project can:
- validate data mapping logic
- test footprint analytics reliably
- keep implementation beginner-friendly

## Future Plan

Future versions can add broader support for real Sierra Chart export variants, including:
- additional column naming patterns
- multiple export schemas
- richer timestamp parsing
- validation/reporting diagnostics

The scope should remain research/backtesting focused unless explicitly designed otherwise.
