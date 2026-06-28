# Order Flow Replay Exporter

The Order Flow Replay Exporter saves replay results, replay report summaries, and AI Coach reviews to files for later study.

This is reporting only. It does not connect to a broker, Sierra Chart live data, CME live data, OpenAI, or any external API. It does not create trade signals or real orders.

## Why Export Replay Reports

Saving replay reports makes it easier to review what happened after a backtest or CSV replay session. A trader can compare replay context, confidence, CVD, warnings, and the AI Coach review without needing to rerun the command immediately.

This is useful for:

- Studying how Order Flow bias changed during replay
- Reviewing data quality and blocking reasons
- Comparing bullish, bearish, neutral, and unknown replay behavior
- Building a history of research reports

## Text Export

The text export is designed for humans. It includes readable sections:

- Order Flow Replay Summary
- Order Flow Replay Report
- AI Coach Order Flow Replay Review
- Replay Steps, when enabled
- Warnings
- Blocking reasons

Use the text file when you want to quickly read what happened.

## JSON Export

The JSON export is designed for tools and future reporting. It stores structured data:

- Replay result summary
- Replay steps
- Replay report
- AI Coach review
- Warnings
- Blocking reasons

Use the JSON file when another script or report builder needs to read the replay output.

## Missing Data

The exporter is safe if replay result, report, or coach review is missing. It writes a simple UNKNOWN or empty section instead of crashing.

## Not A Trade Signal

Exported reports are educational and research-focused. They can say that Order Flow supports bullish or bearish context, but they are not instructions to trade. SMC, CRT, risk, session, news, spread, and execution rules still matter.

## Future Plan

Future versions can export full backtest session reports that combine:

- Order Flow Replay
- Paper trading results
- Risk checks
- Session filters
- News/spread safety checks
- AI Coach review
