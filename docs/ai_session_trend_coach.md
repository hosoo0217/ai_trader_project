# AI Session Trend Coach

The AI Session Trend Coach explains Session History Performance Trend results in beginner-friendly language.

This is education/reporting only. It does not call OpenAI, connect to live data, connect to a broker, or create trade signals.

## Why It Exists

Session Trend gives numbers. The coach turns those numbers into a plain-language review.

It helps explain:

- Whether there is enough saved history
- Whether most sessions are blocked
- Whether most sessions are executed
- Whether behavior is mixed
- Which repeated blocker deserves review

## Block Rate

Block rate shows how often the system avoided a trade:

```text
blocked sessions / total sessions * 100
```

A high block rate can mean the system is conservative. That may be good if it protects capital, but it may also show that filters are too strict or that the test scenarios are poor.

## Execution Rate

Execution rate shows how often sessions passed filters:

```text
executed sessions / total sessions * 100
```

A high execution rate means more setups are passing. It does not prove profitability. Risk, PnL, drawdown, session timing, spread, news, SMC, CRT, and Order Flow still matter.

## Blocked Sessions Are Useful

Blocked sessions are not wasted data. They explain when the system protected the account from bad conditions.

## Common Blocking Reasons

Common blocking reasons show repeated problems, such as:

- Spread too high
- Weekend trading blocked
- News block
- Risk plan invalid
- Weak alignment

Repeated blockers can guide future research.

## Not A Trade Signal

The coach does not tell the user to trade. It reviews saved session history for education and research only.

## Future Plan

Future versions can turn coach reviews into improvement suggestions for strategy quality, dashboard summaries, and profile comparison reports.
