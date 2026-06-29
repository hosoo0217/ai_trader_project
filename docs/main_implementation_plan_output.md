# Main Implementation Plan Output

`main.py` can create a safe future Implementation Plan when a saved Change Proposal is reviewed as `ACCEPT`.

Example command:

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal ACCEPT --change-proposal-index 0 --proposal-reviewed-by Hosoo --proposal-review-notes "Accepted for future work only, create implementation plan"
```

This flow loads saved proposals from `reports/change_proposals.json`, picks the proposal by `--change-proposal-index`, records the proposal review, creates an Implementation Plan, saves the plan, and prints an `Implementation Plan` section.

Plans are saved here by default:

```text
reports/implementation_plans.json
```

The output shows whether the plan was created, the plan ID, source proposal ID, title, category, priority, objective, proposed steps, required tests, risk checks, rollback plan, status, safety flags, save status, path, reasons, and blocking reasons.

`REJECT`, `NEEDS_MORE_DATA`, and `NEEDS_BACKTEST` do not create implementation plans. For those decisions, `main.py` prints that no implementation plan was created because the proposal was not accepted.

Implementation plans do not automatically change strategy rules. They are planning records for future human-reviewed work only. They do not connect to a broker, create orders, create trade signals, or apply implementation automatically.

Final human approval is still required before any separate implementation work. This protects capital by keeping strategy changes behind review, testing, risk checks, and rollback planning instead of allowing a review decision to become an immediate rule change.
