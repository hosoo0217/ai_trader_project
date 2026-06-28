# Main Full Trading Session Report Output

`main.py` can print a Full Trading Session Report for one demo or backtest run.

This is reporting only. It does not connect to a live broker, Sierra Chart live data, CME live data, OpenAI, or any external API. It does not create trade signals or real orders.

## How To Show It

Use:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --show-session-report
```

For backtest mode:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --show-session-report
```

The report is optional so normal demo and backtest output stays familiar.

## What It Shows

The Full Trading Session Report includes:

- Session ID
- Mode
- Scenario
- Profile
- Final action
- Whether a paper trade executed
- Market bias
- SMC bias
- CRT bias
- Order Flow bias
- Safety status
- Safety passed
- Blocked reasons
- Journal summary
- Performance summary
- AI Coach summary
- Decision trace ID
- Reasons
- Warnings

## Why It Helps

The report gives one clean review point for the run. Instead of reading every module section separately, the user can quickly see what the system decided, whether it executed or blocked, and which safety/context fields mattered.

## Why Blocked Trades Matter

Blocked trades are important study data. A blocked setup can show that risk, spread, session, news, volatility, SMC, CRT, or Order Flow checks protected the paper account from poor conditions.

## Reporting Only

The session report does not tell the user to trade. It only summarizes what the paper/demo/backtest system already did.

SMC, CRT, Order Flow, risk, session, news, spread, volatility, and execution rules still matter.

## Future Plan

Future versions can export the Full Trading Session Report to text and JSON files, similar to the Order Flow Replay Exporter.
