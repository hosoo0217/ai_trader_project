# Main Order Flow Replay Report Output

When `--orderflow-replay-csv` is used, `main.py` prints an Order Flow Replay
summary and then an Order Flow Replay Report.

This is research/backtesting/reporting only. It does not place trades, create
trade signals, connect to brokers, or connect to live Sierra Chart or CME data.

## Example

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sierra_chart_footprint_template.csv
```

## What The Report Shows

`Total steps` is the number of replay candles that were processed.

`Bullish steps`, `Bearish steps`, `Neutral steps`, and `Unknown steps` count how
many replay steps ended with each Order Flow bias.

`Dominant bias` is the bias with the highest step count. If the counts are tied
or there are no steps, the dominant bias is `UNKNOWN`.

`Average confidence` is the average Order Flow confidence across all replay
steps. Max and min confidence show the confidence range.

The report also repeats final bias, final confidence, final CVD, warnings, and
reasons.

## Not A Trade Signal

The report summarizes context only. A bullish dominant bias is not a buy signal,
and a bearish dominant bias is not a sell signal. It is meant to help review
Order Flow behavior in research and backtesting.

## Failed Replay

If replay fails because a CSV is missing, empty, or invalid, the report still
prints safely with zero steps, `UNKNOWN` dominant bias, and warnings.

## Future Plan

Future versions can use this report as input for AI coach review, replay
diagnostics, and richer backtest reporting.
