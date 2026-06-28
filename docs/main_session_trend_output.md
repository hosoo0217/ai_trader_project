# Main Session History Trend Output

`main.py` can show a Session History Trend from saved `session_history.json` data.

This is reporting/analysis only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

By default, this reads:

```text
reports/session_history.json
```

To read a different folder:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --session-history-dir reports/history_tests
```

## Output

The terminal prints:

```text
Session History Trend
- Total sessions
- Executed sessions
- Blocked sessions
- Execution rate
- Block rate
- Bullish sessions
- Bearish sessions
- Neutral sessions
- Unknown sessions
- Most common blocking reason
- Blocking reason counts
- Trend status
- Reasons
- Warnings
```

## Execution Rate

Execution rate means:

```text
executed sessions / total sessions * 100
```

It shows how often the paper/demo/backtest system allowed a trade.

## Block Rate

Block rate means:

```text
blocked sessions / total sessions * 100
```

It shows how often the system avoided a trade.

## Most Common Blocking Reason

The most common blocking reason is the blocker that appears most often in saved session reports. This can help reveal repeated issues such as high spread, session timing, news risk, weak alignment, or invalid risk.

## Research Only

Session History Trend is not a trade signal. It only summarizes saved paper/demo/backtest reports.

## Future Plan

Future versions can connect session trends to dashboard views, performance trend charts, and AI improvement review.
