# Implementation Readiness Checklist

Implementation Readiness Checklist v1 reviews whether an Implementation Plan is ready for future human-reviewed coding work.

It is a checklist only. It does not change strategy rules, edit config, write code, create orders, create trade signals, connect to live systems, or allow live trading changes.

## Why Readiness Exists

Final approval alone is not enough. A plan can be approved for future work and still be missing evidence, tests, risk checks, or rollback detail. The readiness checklist makes those requirements visible before any separate manual implementation task begins.

## Required Items

The checklist reviews:

- final review approval
- backtest evidence
- required tests
- risk checks
- rollback plan
- automatic implementation disabled
- live trading changes disabled
- final human work still required

## Why Evidence And Safeguards Matter

Backtest evidence helps confirm that a proposed change was tested against historical conditions before a person considers implementation.

Defined tests help catch regressions and keep behavior understandable.

Risk checks help protect capital by reviewing drawdown, filters, and safety gates before any future code work.

A rollback plan matters because every change should have a clear way back to the previous behavior if testing fails.

## Status Meanings

- `READY_FOR_HUMAN_WORK`: The checklist is complete enough for future human-reviewed coding work.
- `NOT_READY`: A required item is missing, such as final approval or rollback safety.
- `NEEDS_BACKTEST`: Backtest evidence is required before the plan can move forward.
- `NEEDS_TESTS`: Required tests are missing.
- `NEEDS_RISK_REVIEW`: Risk checks are missing.
- `UNKNOWN`: The plan could not be read safely.

## Readiness Does Not Implement Strategy Changes

`READY_FOR_HUMAN_WORK` does not mean automatic implementation. It only means the plan appears ready for a separate human-reviewed coding task. Manual review, coding, testing, and approval are still required.

## Capital Protection

This protects capital by keeping implementation work behind multiple gates: proposal approval, plan creation, final review, readiness checks, tests, risk review, rollback planning, and manual human work.

## Future Plan

Future versions can add main.py readiness output and connect readiness results to an implementation readiness report.
