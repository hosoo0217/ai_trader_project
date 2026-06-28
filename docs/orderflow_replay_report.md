# Order Flow Replay Report

The Order Flow Replay Report summarizes an `OrderFlowReplayResult` into simple
research metrics. It is reporting-only and does not create trade signals,
broker orders, or live data connections.

## Why It Exists

Replay output can contain many steps. A report makes it easier to see the overall
shape of the replay without reading every candle one by one.

## Step Counts

The report counts how many replay steps ended with each Order Flow bias:

- bullish steps
- bearish steps
- neutral steps
- unknown steps

These counts describe replay context only. They are not entries, exits, or trade
signals.

## Dominant Bias

Dominant bias is the bias with the highest step count. If there is a tie, or no
steps exist, the dominant bias is `UNKNOWN`.

This keeps the report conservative when the replay evidence is mixed.

## Confidence

Average confidence shows the typical confidence level across replay steps.
Maximum and minimum confidence show the range.

This helps identify whether the replay was consistently strong or only had one
high-confidence moment.

## Failed Replays

If replay failed or had no steps, the report returns safe zero values and
`UNKNOWN` bias. Blocking reasons from the replay are copied into report warnings.

## Future Plan

Replay reports can later feed:

- AI coach review
- backtest diagnostics
- CSV quality summaries
- Order Flow research dashboards

For v1, the report remains simple, readable, and research-only.
