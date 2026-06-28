# Main Order Flow Coach Output

When `--orderflow-replay-csv` is used, `main.py` prints an AI Coach style review
below the Order Flow Replay Report.

This review is educational only. It does not call OpenAI, use external APIs,
connect to Sierra Chart live data, connect to CME, connect to brokers, or place
orders.

## How It Appears

Example:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv
```

The output includes:

- Status
- Grade
- Summary
- Market read
- Strengths
- Risks
- Lessons
- Next steps
- Warnings
- Reasons

## Educational Only

The coach explains what the replay report suggests. It may say that Order Flow
supports bullish context, supports bearish context, is mixed, or has weak
confidence.

It does not say to take a trade. It does not create entry signals or exit
signals.

## Why It Helps

The coach turns replay metrics into plain language so the user can learn from
backtesting and replay work. It highlights confidence, dominant bias, CVD, and
warnings in a way that is easier to review.

## Future Plan

Future versions can combine this Order Flow coach review with SMC, CRT, risk,
session, news, and spread review so the user can study the whole decision
framework together.
