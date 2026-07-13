# MVP Code Freeze

This document marks the `ai_trader_project` MVP as moving from feature-building into cleanup, testing, and validation mode.

It is documentation only. It does not edit Python code, add features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

The code freeze exists to protect the current MVP from expanding too quickly before it has been validated.

The project already has many research, backtest, paper-trading, Order Flow, reporting, approval, proposal, and readiness workflows. The next job is to prove that the existing system works safely, not to keep adding major features.

The freeze helps keep the project focused on:

- fixing clear bugs,
- improving documentation,
- keeping tests passing,
- validating existing commands,
- checking real exported CSV data safely,
- preparing for deeper backtest and paper-trading validation.

## 2. Current Status

- [x] Research / backtest / paper-trading MVP is close to complete.
- [x] Final cleanup mode is active.
- [x] Documentation cleanup is underway.
- [x] End-to-end demo validation checklist exists.
- [x] Backtest validation checklist exists.
- [x] Real Sierra Chart CSV test guide exists.
- [x] Reports / `.gitignore` safety review exists.
- [ ] Deeper validation is still required.

Safety status:

- Live trading is not implemented.
- Broker execution is not implemented.
- Real order execution is not implemented.
- Real trade signal execution is not implemented.
- The project remains research / backtest / paper-trading only.

## 3. What Is Allowed During Freeze

Allowed work:

- Bug fixes.
- Documentation cleanup.
- Test fixes.
- Validation checklists.
- Real exported CSV testing.
- Backtest validation preparation.
- Paper-trading preparation.
- Small safety clarifications.
- Cleanup of generated files after explicit review.
- README and docs updates that explain existing behavior.

Allowed work should be small, easy to review, and covered by tests when code changes are involved.

## 4. What Is Not Allowed During Freeze

Not allowed during this freeze:

- New major strategy features.
- Live trading implementation.
- Broker connection.
- MT5 login integration.
- Sierra Chart live connection.
- CME live data connection.
- Real order execution.
- Automatic strategy rule changes.
- External API calls without explicit future approval.
- Bypassing safety gates.
- Adding broker credentials, API keys, account numbers, or secrets.
- Treating backtest output as live-trading approval.

If a requested change touches live execution, broker connectivity, external live data, or automatic strategy changes, it belongs in a later separately approved phase.

## 5. Required Checks Before Any Future Feature Work

Before any future feature work is considered:

- [x] Full pytest passing (881 passed).
- [x] End-to-end demo validation done.
- [x] Backtest validation checklist reviewed.
- [x] Real Sierra Chart CSV test completed safely.
- [x] Reports / `.gitignore` safety reviewed.
- [x] Generated report snapshots selected for untracking were reviewed for private data.
- [x] Human approval is required before any strategy change; no strategy implementation is approved.
- [ ] Risk and capital-protection impact reviewed.
- [x] Codebase review confirms no live-trading behavior was added.

Recommended baseline test command:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

## 6. Next Phase

The next phase is validation.

Order of work:

1. Finish cleanup documentation.
2. Run end-to-end demo validation.
3. Run backtest validation checks.
4. Test real exported Sierra Chart CSV files safely.
5. Review generated reports and ignored files.
6. Prepare paper-trading validation.

Real data testing comes next.

Paper trading comes after validation.

Live trading is a later separate phase. It should require a new design, explicit human approval, strong safety rules, and separate implementation review.

## 7. Beginner Summary

Code freeze means: stop building new big things and prove the current system works safely.

The project is not being shut down. It is being protected. The next work should make the MVP easier to trust by testing it, documenting it, fixing bugs, and reviewing safety.

No live trading, broker connection, real order execution, or automatic strategy changes should happen during this freeze.
