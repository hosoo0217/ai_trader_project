# Final Cleanup Index

This document is the final cleanup index for `ai_trader_project`.

It links together the current cleanup documents and explains the safest next validation phase.

## 1. Purpose

This index gives a beginner-readable map of where the project stands now, which cleanup documents exist, and what order to follow before deeper validation.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 2. Current Status

- Project is in FINAL CLEANUP MODE.
- Research / backtest / paper-trading MVP is close to complete.
- Live trading is not implemented.
- Broker execution is not implemented.
- Real order execution is not implemented.
- The next phase is validation.

The project should stay focused on cleanup, testing, documentation, and validation before any future feature work.

## 3. Completed Cleanup Documents

- [MVP Completion Checklist](mvp_completion_checklist.md): Shows what is complete, partially complete, missing, and unsafe to start.
- [Project Health Audit](project_health_audit.md): Reviews folder health, safety health, testing health, documentation health, generated reports, and known gaps.
- [End-to-End Demo Validation](end_to_end_demo_validation.md): Lists the manual CLI commands for safely validating existing demo/research flows.
- [Backtest Validation Checklist](backtest_validation_checklist.md): Defines what must be checked before trusting backtest results for paper validation.
- [Real Sierra Chart CSV Test Guide](real_sierra_chart_csv_test_guide.md): Explains how to test real exported Sierra Chart CSV files without live connections.
- [ACSIL Matching Day2 Multi-Timeframe Validation Result](acsil_matching_day2_multitimeframe_validation_result.md): Records day2 matching OHLC plus ACSIL full footprint validation across 1m, 5m, and 10m.
- [ACSIL Day3 1-Day 10m Validation Result](acsil_day3_1day_10m_validation_result.md): Records one-session (1-day chart load) day3 matching OHLC plus ACSIL full footprint validation for 10m, including A/B diagnostic safety results.
- [ACSIL Day3 1-Day 5m Validation Logic Gap](acsil_day3_1day_5m_validation_logic_gap.md): Records one-session (1-day chart load) day3 5m ACSIL validation and documents the A/B diagnostic opposite-bias blocking logic gap as an implementation-readiness stop.
- [Order Flow Confirmation Blocking Semantics Audit](orderflow_confirmation_blocking_semantics_audit.md): Audits current A/B diagnostic blocking semantics, documents required decision-matrix behavior, and marks implementation readiness as STOP pending design/test approval.
- [Order Flow Confirmation Design Approval Checklist](orderflow_confirmation_design_approval_checklist.md): Defines the required human-approved blocking semantics, data-quality behavior, and pre-merge test requirements before any future Order Flow confirmation implementation.
- [Order Flow A/B Diagnostic Semantics Post-Fix Validation](orderflow_ab_diagnostic_semantics_postfix_validation.md): Records post-fix validation that neutral/opposite-bias blocking and bearish/bullish trade-side labels are correctly represented in the research-only A/B diagnostic.
- [Order Flow Footprint Implementation Gap Audit](orderflow_footprint_implementation_gap_audit.md): Audits current Footprint / Order Flow capabilities, limitations, safety status, and the next validation phase.
- [Order Flow Confirmation Implementation Readiness Plan](orderflow_confirmation_implementation_readiness_plan.md): Defines the documentation-only approval, test, rollback, and safety checklist before any future Order Flow confirmation implementation.
- [Reports / .gitignore Safety Review](reports_gitignore_safety.md): Explains generated report safety, secrets safety, and ignore rules.
- [MVP Code Freeze Note](mvp_code_freeze.md): Explains that the project is moving from feature-building into cleanup, testing, and validation mode.

## 4. Validation Order

Follow this safest order:

1. Full pytest.
2. End-to-end CLI demo validation.
3. Order Flow CSV sample validation.
4. Real Sierra Chart exported CSV validation.
5. Backtest validation.
6. Paper trading preparation.
7. Future broker integration planning only.

Do not skip ahead to live trading. Each step should be reviewed before moving to the next.

## 5. Not Allowed Yet

These are not allowed in the current phase:

- No live trading.
- No broker connection.
- No MT5 login integration yet.
- No Sierra Chart live connection.
- No CME live data connection.
- No real order execution.
- No automatic strategy rule changes.
- No real-money trading.
- No bypassing safety gates.

## 6. Human Approval Rule

Future strategy changes require a full human-reviewed workflow:

- Proposal.
- Review.
- Implementation plan.
- Final review.
- Readiness check.
- Human approval.

A suggestion, proposal, or readiness result does not automatically change strategy rules. Human review stays in control.

## 7. Beginner Summary

The project is now being cleaned and validated before any real trading work.

Think of this phase as proving the current system works safely. First run tests, then run demo validation, then check sample CSVs, then test real exported CSVs, then validate backtests, and only after that prepare paper trading.

Live trading and broker connections are later separate phases, not part of this cleanup stage.
