# Bulk 30-day SC delayed audit summary

Status: diagnostic-only audit completed. No backtests were run.

## Data source

- Sierra Chart delayed data
- Instrument/session exported from Sierra Chart
- Bulk folder: private_data/sierra_chart/bulk_30d_sc_delayed
- Session start hour: 18

## 10m audit

- Footprint range: 2026-06-03 18:00:00 -> 2026-07-03 11:40:00
- BarIndex: 0 -> 2560
- Total sessions: 22
- Matched sessions: 22
- Mismatched sessions: 0
- Missing market sessions: 0
- Missing footprint sessions: 0
- Total bad timestamp rows: 0

## 5m audit

- Footprint range: 2026-06-03 18:00:00 -> 2026-07-03 12:00:00
- BarIndex: 0 -> 5124
- Total sessions: 22
- Matched sessions: 22
- Mismatched sessions: 0
- Missing market sessions: 0
- Missing footprint sessions: 0
- Total bad timestamp rows: 0

## 1m audit

- Footprint range: 2026-06-03 18:00:00 -> 2026-07-03 12:23:00
- BarIndex: 0 -> 25613
- Total sessions: 22
- Matched sessions: 22
- Mismatched sessions: 0
- Missing market sessions: 0
- Missing footprint sessions: 0
- Total bad timestamp rows: 0

## Notes

- The first attempted 1m footprint export was actually a suspected 5m export and was renamed to:
  private_data/sierra_chart/bulk_30d_sc_delayed/bulk_30d_1m_footprint_suspect_5m.csv
- Market CSVs initially extended slightly beyond footprint end on the latest live/delayed session.
- Matched market CSVs were created by trimming only the final extra live bars to the footprint end.
- This audit validates CSV/session alignment only.
- This does not prove strategy profitability.
- This does not approve live trading, paper trading, broker connection, or orderflow confirmation enforcement.
