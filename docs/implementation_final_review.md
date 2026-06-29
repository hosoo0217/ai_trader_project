# Implementation Final Review

Implementation Final Review v1 is the last human review step before any future implementation work can be considered.

It reviews an existing Implementation Plan and records whether the plan is ready to move into separate, human-controlled implementation work. It does not change strategy rules, edit config, create orders, create trade signals, connect to live systems, or write code automatically.

## Why Final Review Exists

Implementation plans still require final approval because a plan can look reasonable but still be missing evidence, tests, risk checks, or rollback clarity. The final review gives a human one more checkpoint before any separate implementation task begins.

## Decision Meanings

- `APPROVE_FOR_WORK`: The plan is approved for future human-reviewed implementation work only.
- `REJECT`: The plan should not move forward.
- `NEEDS_BACKTEST`: Backtest evidence is required before the plan can move forward.
- `NEEDS_MORE_REVIEW`: More human review is required before the plan can move forward.
- `UNKNOWN`: The decision or plan could not be read safely.

## Approval Does Not Implement Anything

`APPROVE_FOR_WORK` does not apply code, change strategy rules, or allow immediate implementation. It only records that a human approved the plan for future reviewed work.

Implementation must still be separate, reviewed, tested, and committed manually. `implementation_allowed_now` remains `False`, and `allow_auto_implementation` defaults to `False`.

## Backtest Evidence

Backtest evidence is required because strategy changes can affect drawdown, session behavior, news sensitivity, spread behavior, and capital protection. A final review should not approve work that has not been tested against realistic historical scenarios.

## Capital Protection

This workflow protects capital by keeping final review separate from implementation. It makes sure a human decision never becomes an automatic strategy change and keeps the system offline, review-based, and audit-friendly.

## Future Plan

Future versions can add:

- final review log storage
- implementation readiness checklist
- links to backtest evidence
- manual implementation ticket output
