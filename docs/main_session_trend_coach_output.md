# Main AI Coach Session Trend Review Output

`main.py` prints an AI Coach Session Trend Review whenever `--show-session-trend` is used.

This is education/reporting only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

The command reads:

```text
reports/session_history.json
```

You can choose another folder:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --session-history-dir reports/history_tests
```

## Output

Below the `Session History Trend` section, `main.py` prints:

```text
AI Coach Session Trend Review
- Status
- Grade
- Summary
- Trend read
- Strengths
- Risks
- Lessons
- Next steps
- Warnings
- Reasons
```

## Why It Helps

The trend section shows numbers. The coach review explains those numbers in plain language.

It can explain:

- The system is conservative
- Many sessions are blocked
- More saved sessions are needed
- Common blocking reasons should be reviewed
- Execution rate alone does not prove profitability

## Educational Only

The coach review does not create trade signals. It does not tell the user to buy, sell, or open a position.

SMC, CRT, Order Flow, risk, session, news, and spread filters still matter.

## Future Plan

Future versions can turn the review into strategy-quality improvement suggestions, dashboard notes, and profile comparison summaries.
