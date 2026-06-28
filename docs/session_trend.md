# Session Trend

Session Trend analyzes saved Trading Session History records and summarizes how the system has behaved over multiple demo, paper, or backtest sessions.

This is reporting/analysis only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Why Session Trend Exists

One session report explains one run. Session history stores many runs. Session trend turns that history into simple review metrics.

It helps answer:

- Are most sessions executing or being blocked?
- What percentage of sessions are blocked?
- Which market bias appears most often?
- Which blocking reason appears most often?
- Is there enough data to trust the trend?

## Execution Rate

Execution rate is:

```text
executed sessions / total sessions * 100
```

It shows how often the paper/demo/backtest system allowed a trade.

## Block Rate

Block rate is:

```text
blocked sessions / total sessions * 100
```

It shows how often the system avoided a trade.

## Why Blocked Sessions Are Useful

Blocked sessions are not failures by default. They may show that safety filters protected the account from bad conditions such as high spread, news risk, bad session timing, invalid risk, or weak alignment.

## Common Blocking Reasons

Common blocking reasons count repeated blockers across the history. If one reason appears often, it may deserve review.

Examples:

- Spread too high
- Weekend trading blocked
- News block
- Risk plan invalid

## Trend Status

The analyzer returns one simple status:

- `NOT_ENOUGH_DATA`
- `MOSTLY_BLOCKED`
- `MOSTLY_EXECUTED`
- `MIXED`
- `UNKNOWN`

## Not A Trade Signal

Session Trend is not trading logic. It does not decide whether to buy or sell. It only summarizes saved paper/demo/backtest reports.

## Future Plan

Future versions can connect session trend to:

- Dashboard views
- Performance trend charts
- AI improvement review
- Profile comparison
- Scenario comparison
