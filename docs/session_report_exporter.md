# Trading Session Report Exporter

The Trading Session Report Exporter saves a Full Trading Session Report to text and JSON files for later study.

This is reporting/export only. It does not connect to a live broker, Sierra Chart live data, CME live data, OpenAI, or any external API. It does not create trade signals or real orders.

## Why Export Session Reports

Saving reports helps review AI Trader behavior after a demo, paper, or backtest run. The user can come back later and inspect what the system decided, whether the trade was executed or blocked, and which context or safety checks mattered.

This is useful for:

- Reviewing one paper/demo/backtest session
- Studying blocked trades
- Comparing market, SMC, CRT, and Order Flow context
- Keeping a record of safety and performance summaries

## Text Export

The text export is designed for humans. It includes readable sections:

- Full Trading Session Report
- Session Info
- Decision Summary
- Market Context
- SMC / CRT / Order Flow
- Safety Gate
- Blocked Reasons
- Journal Summary
- Performance Summary
- AI Coach Summary
- Decision Trace
- Warnings
- Reasons

Use the text file when you want to read the report directly.

## JSON Export

The JSON export is designed for tools and future automation. It stores the same session report fields in structured form so another script, dashboard, or report builder can read them safely.

## Missing Data

If a report is missing, the exporter writes a safe UNKNOWN-style report instead of crashing. Empty fields are exported as empty values, `None`, or readable fallback text.

## Not A Trade Signal

Exported session reports are for study and review only. They summarize what the paper/research system already did. They do not tell the user to trade.

SMC, CRT, Order Flow, risk, session, news, spread, volatility, and execution rules still matter.

## Future Plan

Future versions can build a full backtest session history from many exported session reports. That history can help compare scenarios, profiles, safety blocks, and performance over time.
