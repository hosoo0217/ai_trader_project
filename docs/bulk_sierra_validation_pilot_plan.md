# Bulk Sierra Validation Pilot Plan

## Purpose

This note documents preparation for a future 30-day Sierra Chart bulk validation pilot.

The pilot goal is to split larger historical Sierra Chart exports into daily/session groups, compare market OHLC rows with footprint rows, and identify clean or bad sessions before any manual or automated diagnostic backtest is run.

## Safety scope

This tooling is diagnostic-only.

It does not change strategy execution behavior.  
It does not change strategy rules.  
It does not change risk rules.  
It does not change broker code.  
It does not change live trading code.  
It does not add broker, API, live trading, or paper trading connections.  
It does not approve strategy enforcement.  
It does not approve paper trading.  
It does not approve live trading.

## Prepared helper

The helper in `analysis/bulk_sierra_validation.py` can:

- parse Sierra footprint CSV rows using `DateTime`,
- parse Sierra market OHLC CSV rows using `Date` + `Time`,
- split parsed rows into futures-style session groups,
- compare market and footprint sessions by start/end timestamps,
- flag missing or mismatched sessions,
- include bad timestamp row counts,
- return lightweight per-session summaries.

By default, grouping uses an 18:00 session start for GC-style futures validation. Timestamps at or after 18:00 belong to that date's session, while timestamps before 18:00 belong to the previous date's session. This keeps an overnight session such as `2026-07-02 18:00` through `2026-07-03 08:45` together as one validation session.

## Audit runner

The runner in `analysis/bulk_sierra_audit_runner.py` is a diagnostic wrapper around the helper.

It reads explicitly provided market and footprint CSV paths, calls the bulk Sierra validation helper, counts session statuses, and can write JSON or Markdown summaries when output paths are supplied.

The runner is intended to be used before any real 30-day bulk backtesting. Its job is to identify whether the exported market and footprint sessions line up, whether sessions are missing, and whether bad timestamp rows exist.

## Pilot boundary

The helper and runner do not run real backtests. They do not load private Sierra files by themselves. They do not write reports by default. They do not modify existing validation results.

Synthetic unit tests cover the current behavior. Real 30-day export validation should remain a separate, explicitly reviewed step.
