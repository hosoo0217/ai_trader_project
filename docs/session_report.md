# Trading Session Report

The Trading Session Report summarizes one paper/demo/backtest run in a beginner-readable format.

This is reporting only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Why It Exists

The AI Trader has many safety and context layers:

- Market bias
- SMC bias
- CRT bias
- Order Flow bias
- Safety gate status
- Risk checks
- Journal outcome
- Performance summary
- Decision trace
- AI Coach review

A full session report puts the important parts into one object so the user can review what happened without digging through every module.

## What It Summarizes

The report includes:

- Mode, such as demo or backtest
- Scenario and profile
- Final action
- Whether a paper trade was executed
- Market, SMC, CRT, and Order Flow bias
- Safety status and whether safety passed
- Blocking reasons
- Journal summary, if available
- Performance summary, if available
- AI Coach summary, if available
- Decision trace id, if available
- Reasons and warnings

## Why Blocked Trades Matter

Blocked trades are useful learning data. A blocked trade can show that the system protected the account from poor conditions, such as high spread, invalid risk, bad session timing, weak context, or missing confirmation.

The report keeps blocked reasons visible so the user can understand why the system avoided a trade.

## How It Helps Review Behavior

The report helps answer:

- What did the system decide?
- Was the trade executed or blocked?
- Which context sources agreed or disagreed?
- Did safety pass?
- What should be reviewed next?

This makes paper trading and backtesting easier to study.

## Not A Trade Signal

The session report is not an entry signal. It only summarizes what the paper/research system already did.

SMC, CRT, Order Flow, risk, session, news, spread, volatility, and execution rules still matter.

## Future Plan

Future versions can export full session reports to text and JSON, similar to the Order Flow Replay Exporter.
