# Main Implementation Final Review Output

`main.py` can final-review saved Implementation Plans from `reports/implementation_plans.json`.

Use `--final-review-implementation-plan` to load saved plans, select one by index, record the final review decision, save the review log, and print an `Implementation Final Review` section.

## APPROVE_FOR_WORK Example

```powershell
.\venv\Scripts\python.exe main.py --final-review-implementation-plan APPROVE_FOR_WORK --implementation-plan-index 0 --implementation-reviewed-by Hosoo --implementation-review-notes "Approved for future work only, no automatic implementation"
```

`APPROVE_FOR_WORK` means the plan is approved for future human-reviewed implementation work only. It does not apply code, edit strategy rules, or allow immediate implementation.

## REJECT Example

```powershell
.\venv\Scripts\python.exe main.py --final-review-implementation-plan REJECT --implementation-plan-index 0 --implementation-reviewed-by Hosoo --implementation-review-notes "Rejected because more evidence is needed"
```

`REJECT` records that the implementation plan should not move forward.

## NEEDS_BACKTEST Example

```powershell
.\venv\Scripts\python.exe main.py --final-review-implementation-plan NEEDS_BACKTEST --implementation-plan-index 0 --implementation-reviewed-by Hosoo --implementation-review-notes "Needs more backtest evidence"
```

`NEEDS_BACKTEST` records that more backtest evidence is required before the plan can move forward.

## NEEDS_MORE_REVIEW Example

```powershell
.\venv\Scripts\python.exe main.py --final-review-implementation-plan NEEDS_MORE_REVIEW --implementation-plan-index 0 --implementation-reviewed-by Hosoo --implementation-review-notes "Needs another human review before implementation work"
```

`NEEDS_MORE_REVIEW` records that the plan needs more human review before any future work.

## Saved Log

By default, final review decisions are saved here:

```text
reports/implementation_final_reviews.json
```

The output includes the plan ID, decision, status, approval flag, implementation safety flag, reviewer, notes, log path, reasons, and blocking reasons.

## Safety

Final review does not implement anything. `APPROVE_FOR_WORK` does not change strategy rules, create trade signals, create orders, or connect to live systems. It only records permission for future human-reviewed work.

This protects capital by keeping planning, final approval, implementation, testing, and deployment as separate steps. Future work can add an implementation readiness checklist that verifies backtest evidence, risk checks, rollback steps, and final manual sign-off.
