# Main Implementation Readiness Output

`main.py` can check whether a saved Implementation Plan is ready for future human-reviewed work.

Example command:

```powershell
.\venv\Scripts\python.exe main.py --check-implementation-readiness --implementation-plan-index 0
```

The command loads saved plans from `reports/implementation_plans.json`, selects the plan by `--implementation-plan-index`, loads final review records from `reports/implementation_final_reviews.json`, finds the latest review for the selected plan, and prints an `Implementation Readiness` section.

`READY_FOR_HUMAN_WORK` means the checklist is complete enough for a separate human-reviewed coding task. It does not mean automatic implementation, live trading, or strategy rule changes.

Readiness does not implement strategy changes. It does not edit config, create orders, create trade signals, connect to live systems, or apply code automatically.

The checklist matters because final review alone is not enough. A plan still needs backtest evidence, defined tests, risk checks, and a rollback plan before future work is considered.

This protects capital by keeping final review, readiness, coding, testing, risk review, rollback planning, and manual approval as separate gates.

Future plan: add a project health audit and MVP checklist that summarizes all safety gates in one place.
