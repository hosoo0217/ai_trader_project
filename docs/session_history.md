# Session History

Session History stores many Full Trading Session Reports in one JSON file for later review.

This is reporting/history only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Why It Exists

One session report explains one demo, paper, or backtest run. Session history keeps many of those reports together so the user can review patterns over time.

This helps answer:

- How many sessions were executed?
- How many were blocked?
- Which market bias appeared most often?
- Which blocking reasons repeated?
- Are safety filters protecting the system consistently?

## Storage Format

The default history file is:

```text
reports/session_history.json
```

The file stores a JSON list. Each item is one saved `TradingSessionReport` converted to a dictionary.

If the folder or file is missing, the history store creates it safely.

## Blocked Sessions

Blocked sessions are useful because they show when the system avoided a setup. A blocked result may mean spread was too high, news was active, session timing was wrong, risk was invalid, or context was unclear.

Tracking blocked sessions helps improve the system without forcing trades.

## Common Blocking Reasons

`common_blocking_reasons` counts repeated reasons across saved reports. For example:

```text
Spread too high = 4
News block = 2
```

This helps identify the most common reasons trades are avoided.

## Reporting Only

Session history is not trading logic. It does not decide whether to buy or sell. It only stores and summarizes reports created by the paper/demo/backtest system.

## Future Plan

Future versions can use session history for:

- Dashboard views
- Performance trends
- Safety filter analysis
- Backtest session comparisons
- AI improvement review
