# Main Order Flow Replay Export Output

`main.py` can export Order Flow Replay output to text and JSON files for later study.

This is export/reporting only. It does not connect to live Sierra Chart data, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --export-orderflow-report
```

## Required Replay CSV

Exporting only works when replay data exists. That means `--export-orderflow-report` should be used with:

```powershell
--orderflow-replay-csv PATH
```

If the export flag is used without a replay CSV, the app does not crash. It prints:

```text
Order Flow replay CSV is required to export report
```

## Output Files

By default, files are saved in:

```text
reports/
```

The default filenames are:

```text
reports/orderflow_replay_report.txt
reports/orderflow_replay_report.json
```

You can choose another folder:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --orderflow-replay-csv data/sample_footprint_bullish.csv --export-orderflow-report --orderflow-report-dir reports/my_session
```

## Export Without Replay Steps

Detailed replay steps are included by default. To export only the summary, report, and AI Coach review:

```powershell
--no-orderflow-report-steps
```

## Terminal Output vs Exported Report

Terminal output is a quick view while the command runs. The exported report is saved for later review.

The text report is best for reading. The JSON report is best for future tools, dashboards, or full backtest report builders.

## Research Only

Exported reports are for study and backtesting. They can help review Order Flow context, confidence, CVD, warnings, and the AI Coach review, but they are not trade signals.

SMC, CRT, risk, session, news, spread, and execution rules still matter.

## Future Plan

Future versions can export full backtest session reports that combine:

- Order Flow Replay
- Paper trading results
- Paper Flow exit simulation
- Risk checks
- Session, news, spread, and volatility filters
- AI Coach review
