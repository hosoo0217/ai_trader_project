# Main Strategy Improvement Output

`main.py` prints Strategy Improvement Suggestions whenever `--show-session-trend`
is used.

This is education and research output only. It does not connect to live data,
Sierra Chart, CME, a broker, OpenAI, or any external API. It does not create
orders or trade signals.

## Example Command

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend
```

To read session history from another folder:

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --session-history-dir reports/history_tests
```

## Output

Below the `AI Coach Session Trend Review` section, `main.py` prints:

```text
Strategy Improvement Suggestions
- Status
- Summary
- Suggestions
  - Category
  - Priority
  - Suggestion
  - Reason
  - Risk
  - Human approval required
- Warnings
- Reasons
```

## Why These Suggestions Exist

Session trend data can reveal repeated patterns. A common blocking reason may
show which part of the research system deserves more review.

Examples:

- Review common blocking reasons
- Save more session history
- Check session filter settings
- Improve SMC sample data quality
- Check Order Flow CSV data quality
- Review spread, news, and risk settings

## Human Approval

Human approval is required before changing rules. The suggestions are research
notes that point to possible review areas, not instructions to trade.

## Future Plan

Future versions can turn these notes into human-approved strategy change
proposals, with tests and review before any decision logic is updated.
