# Main CLI Order Flow Output v1

This document explains why `main.py` now prints Order Flow status in demo and backtest output.

The CLI remains research-only.
It does not connect to live trading, brokers, Sierra Chart live data, CME live data, or external APIs.

## Why Order Flow Appears In CLI Output

Order Flow is now an optional context source for `PaperTradingFlow`.

Showing its status in the CLI helps users understand whether order flow evidence was part of the current run.

The output is intentionally simple:

```text
Order Flow Context
- Active: False
- Bias: UNKNOWN
- Confidence: 0.0
- Status: Not provided
- Reason: Order Flow context not provided
```

## Why It May Say Not Provided

Most current demo and backtest scenarios use standard OHLC candle data only.

Order Flow Context requires footprint-style bid/ask volume data. If that data has not been imported and converted into an `OrderFlowContextResult`, the CLI reports that Order Flow was not provided.

This is normal in v1.

## Why This Is Normal Before Sierra Chart CSV Data

The project does not use live Sierra Chart or CME data.

Before real footprint research can be shown in the CLI, historical footprint data needs to be exported from Sierra Chart as CSV and imported offline.

Until then, Order Flow can safely remain inactive without breaking existing demo or backtest commands.

## Detailed Output

Use:

```text
--show-orderflow
```

This prints extra diagnostic fields such as whether the flow checked Order Flow and any Order Flow blocking reasons.

## Future Plan

The planned workflow is:

1. Export historical footprint data from Sierra Chart as CSV.
2. Import the CSV into `FootprintCandle` objects.
3. Run Delta/CVD, Imbalance, and Absorption analyzers.
4. Combine those outputs into `OrderFlowContextResult`.
5. Pass that context into `PaperTradingFlow`.
6. Display the resulting Order Flow bias, confidence, status, and reasons in `main.py`.

This remains paper trading and backtesting only.
