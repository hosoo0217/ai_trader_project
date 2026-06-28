# Sierra Chart CSV Checklist

Use this checklist before running a Sierra Chart footprint CSV through the demo.

- Does it have a time column?
- Does it have OHLC columns?
- Does it have a price level column?
- Does it have bid volume?
- Does it have ask volume?
- Are bid and ask volumes non-negative?
- Are there multiple rows per candle?
- Does the data quality check pass?
- Does the CLI show `Order Flow Context` with `Active: True`?

Example command:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --orderflow-csv data/sierra_chart_footprint_template.csv --show-trace
```

If Order Flow is not active, check the `Order Flow Data Quality` section first.
Missing columns, empty data, or invalid levels should be fixed in the CSV export
before using it for research.
