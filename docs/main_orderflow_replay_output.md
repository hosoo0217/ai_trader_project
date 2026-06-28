# Main Order Flow Replay Output

`main.py` can print standalone Order Flow Replay output from a footprint CSV.
This is research/backtesting only. It does not connect to Sierra Chart live
data, CME, brokers, or any external API, and it does not place trades.

## Run Replay

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sierra_chart_footprint_template.csv
```

To include each replay step:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sierra_chart_footprint_template.csv --show-orderflow-replay-steps
```

## Replay Output

The summary shows:

- Active
- Passed
- Data quality status
- Step count
- Final bias
- Final confidence
- Final CVD
- Reasons
- Blocking reasons

When `--show-orderflow-replay-steps` is provided, each step also prints:

- Index
- Time
- Candle delta
- Cumulative delta
- Delta direction
- Imbalance bias
- Absorption bias
- Order Flow bias
- Confidence

## Replay vs Context

`--orderflow-csv` builds one Order Flow Context and can pass it into
`PaperTradingFlow` as optional decision context.

`--orderflow-replay-csv` only prints a replay report. It processes the footprint
CSV candle by candle and does not affect `PaperTradingFlow`.

You can use both flags together, but they do different jobs.

## Future Plan

Replay output can later feed a report view, backtest diagnostics, or AI coach
review. For v1 it stays readable, standalone, and safe.
