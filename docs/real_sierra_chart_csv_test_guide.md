# Real Sierra Chart CSV Test Guide

This guide explains how to test a real exported Sierra Chart footprint / Order Flow CSV file with the existing `ai_trader_project` CSV importer, data-quality checker, and replay tools.

It is documentation only. It does not add trading features, edit Python code, connect to Sierra Chart live data, connect to CME live data, connect to a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

This guide is for testing real exported Sierra Chart CSV files safely in research/demo mode.

The goal is to confirm that a real CSV export can be:

- loaded from disk,
- mapped into the project footprint format,
- checked for data quality,
- used for Order Flow context,
- replayed step by step,
- reviewed without connecting to any live system.

This is a validation step before deeper backtest or paper-trading validation. It is not live trading.

## 2. Important Safety Warning

- CSV export testing only.
- No Sierra Chart live connection is used.
- No CME live data connection is used.
- No broker connection is used.
- No real order execution exists.
- No live trading is implemented.
- No external API should be required.
- No broker credentials, API keys, account numbers, or secrets should be used.

If a workflow asks for live credentials or appears to place an order, stop immediately.

## 3. Before Exporting

Start with a small, easy-to-review export.

- [ ] Use a small sample first.
- [ ] Prefer one session/day first.
- [ ] Make sure the chart, instrument, date, session, and timezone are understood.
- [ ] Record the instrument, date, session, and timezone.
- [ ] Record the Sierra Chart study/export settings if possible.
- [ ] Do not include account credentials.
- [ ] Do not include private broker information.
- [ ] Do not include account numbers.
- [ ] Save the file with a clear local name, such as `data/your_real_sierra_export.csv`.

Keep the first file small so it is easier to inspect if something looks wrong.

## 4. Expected CSV Content

The importer maps real CSV headers into normalized footprint fields.

Expected fields generally include:

- `timestamp` / `datetime` / `time`
- price level
- bid volume
- ask volume
- candle open/high/low/close grouping if available
- volume or delta fields if exported

The project's normalized fields are:

- `time`
- `open`
- `high`
- `low`
- `close`
- `price`
- `bid_volume`
- `ask_volume`

Sierra Chart exports may use different column names. Column names may need mapping if Sierra Chart exports names that the importer does not already recognize.

Known supported examples include names like `Date Time`, `Last`, `Level`, `Bid Volume`, and `Ask Volume`.

## 5. Data Quality Checks

Before trusting the output, check the file and the program output.

- [ ] File opens.
- [ ] Rows are not empty.
- [ ] Timestamps are valid.
- [ ] Price levels are valid.
- [ ] Bid volume values are numeric.
- [ ] Ask volume values are numeric.
- [ ] No obvious duplicated rows.
- [ ] No missing key columns.
- [ ] Session time makes sense.
- [ ] Data quality checker should not crash.
- [ ] If quality fails, blocking reasons should be readable.

The data-quality checker may return statuses such as `PASSED`, `WARNING`, `FAILED`, `EMPTY`, or `INVALID`. Failed, empty, or invalid data should block Order Flow safely.

## 6. Example Command Using Sample CSV

Run the known sample first:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv data/sample_footprint_bullish.csv --show-trace
```

Expected result:

- The command runs locally.
- The sample CSV loads.
- Order Flow context and data-quality status may print.
- No live connection is used.

## 7. Example Command For Real Exported CSV

After the sample command works, replace the path with your real exported CSV:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv data/your_real_sierra_export.csv --show-trace
```

Use `data/your_real_sierra_export.csv` as a placeholder. Rename it to the real local file path you want to test.

Expected result:

- The file loads if the path and columns are valid.
- The system prints Order Flow context, data-quality status, or blocking reasons.
- Invalid CSV data should fail safely.

## 8. Replay Test Command

Run replay on the real exported CSV:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/your_real_sierra_export.csv --show-orderflow-replay-steps
```

Expected result:

- Replay processes footprint candles from the local CSV.
- Replay steps may print one by one.
- Data-quality status should appear in replay output.
- Failed, empty, or invalid data should block replay safely.

## 9. Expected Safe Output

The system should print one or more of:

- Order Flow context,
- data-quality status,
- replay steps,
- final replay bias/confidence,
- blocking reasons,
- readable import or validation issues.

The system should not:

- place trades,
- connect live,
- connect to Sierra Chart live data,
- connect to CME live data,
- connect to a broker,
- call external APIs,
- change strategy rules,
- create live trading execution.

If the CSV is invalid, the command should fail safely or print a readable issue.

## 10. Troubleshooting

Common problems:

- Column name mismatch.
- Timestamp format mismatch.
- Empty export.
- Wrong delimiter.
- Wrong timezone.
- Missing bid/ask volume.
- Missing price level.
- Missing OHLC columns.
- File path typo.
- File is too large for a first test.

What to do:

- Compare the export headers with `docs/sierra_chart_csv_format_mapping.md`.
- Try a smaller one-session CSV.
- Confirm the file path is correct.
- Confirm the file opens in a text editor or spreadsheet.
- Confirm bid/ask volumes are numeric and non-negative.
- Confirm session time and timezone match what you expect.

Do not change strategy logic to make a bad CSV pass. Fix or understand the CSV format first.

## 11. When To Stop

Stop validation if:

- Pytest fails.
- The importer crashes.
- Data quality is bad.
- Output is confusing.
- The file includes private account or broker data.
- The command appears to use live data.
- The command appears to require credentials.
- The command appears to place a real order.

Do not continue to paper validation until the CSV format is understood.

## 12. Beginner Summary

This guide helps test real Sierra Chart exported data without connecting to live trading or risking money.

You export a small CSV from Sierra Chart, place it locally, run the existing demo/replay commands, and check whether the importer and data-quality checker understand it.

Everything should stay local, offline, and research-only. The goal is to prove the CSV format is usable before trusting it in deeper backtest or paper-trading validation.
