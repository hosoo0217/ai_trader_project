# Order Flow CSV Demo

This demo lets `main.py` activate Order Flow Context from a local footprint CSV file.
It is research and backtesting only. It does not connect to Sierra Chart live data,
CME, a broker, or any external API.

## How It Works

Use `--orderflow-csv` with a CSV that has these columns:

- `time`
- `open`
- `high`
- `low`
- `close`
- `price`
- `bid_volume`
- `ask_volume`

The CLI loads the file with `SierraChartImporter`, builds footprint candles, then runs:

- `OrderFlowDataQualityChecker`
- `DeltaCVDAnalyzer`
- `ImbalanceAnalyzer`
- `AbsorptionAnalyzer`
- `OrderFlowContextCombiner`

If data quality is `PASSED` or `WARNING`, the analyzers continue and Order Flow
Context can become active. If quality is `FAILED`, `EMPTY`, or `INVALID`, Order
Flow stays inactive and the rest of the demo keeps running safely.

The resulting `OrderFlowContextResult` is passed into `PaperTradingFlow` as an
optional context source.

## Example

```bash
python main.py --mode demo --scenario bullish --profile apex --orderflow-csv data/sample_footprint_bullish.csv
```

```bash
python main.py --mode demo --scenario bearish --profile apex --orderflow-csv data/sample_footprint_bearish.csv
```

When no CSV is provided, the program keeps the old behavior and prints Order Flow
as not provided.

## Why This Is Still Demo Only

The sample files are static CSV data. They are useful for testing the pipeline,
but they are not live market data. No real orders are created and no live data
connection is used.

## Future Plan

The next step is to support real Sierra Chart exported footprint CSV files:

1. Export footprint data from Sierra Chart to CSV.
2. Load the CSV with `SierraChartImporter`.
3. Convert it into Order Flow Context.
4. Pass that context into `PaperTradingFlow` for paper trading and backtesting.
