# Main Full Trading Session Report Export Output

`main.py` can export a Full Trading Session Report to text and JSON files.

This is export/reporting only. It does not connect to live data, Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create trade signals or real orders.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --session-time 2026-06-26T14:00:00Z --show-session-report --export-session-report
```

## Output Folder

By default, files are saved in:

```text
reports/
```

The default filenames are:

```text
reports/trading_session_report.txt
reports/trading_session_report.json
```

You can choose another folder:

```powershell
.\venv\Scripts\python.exe main.py --mode demo --scenario bullish --profile apex --export-session-report --session-report-dir reports/session_001
```

## Terminal Output

When export is enabled, the terminal prints:

```text
Full Trading Session Report Export
- Exported: True or False
- Text path: ...
- JSON path: ...
- Reasons: ...
- Blocking reasons: ...
```

The terminal output is a quick status check. The exported text and JSON files are the saved report.

## Research Only

Exported session reports are for review and research. They summarize what the paper/demo/backtest system already did. They are not instructions to trade.

Blocked trades are especially useful because they show which safety or context checks protected the paper account.

## Future Plan

Future versions can build a full backtest session history by saving many session reports over time. That history can help compare scenarios, profiles, blocked reasons, and performance quality.
