# Final Cleanup Index

This document is the final cleanup index for `ai_trader_project`.

It links together the current cleanup documents and explains the safest next validation phase.

## 1. Purpose

This index gives a beginner-readable map of where the project stands now, which cleanup documents exist, and what order to follow before deeper validation.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 2. Current Status

- Project is in FINAL CLEANUP MODE.
- Research and backtest capabilities exist, and `GC-202608-COMEX` has Full Independent-Period Acceptance; independent-period performance validation remains pending and paper trading is not approved.
- Live trading is not implemented.
- Broker execution is not implemented.
- Real order execution is not implemented.
- The next authorized work is documentation, independent-period offline performance validation, reproducible testing, and safety review; code freeze remains active.

The project must stay focused on cleanup, testing, documentation, independent-period offline validation, and safety review; no feature work is authorized while code freeze remains active.

## 3. Completed Cleanup Documents

- [MVP Completion Checklist](mvp_completion_checklist.md): Shows what is complete, partially complete, missing, and unsafe to start.
- [Project Health Audit](project_health_audit.md): Reviews folder health, safety health, testing health, documentation health, generated reports, and known gaps.
- [Capital Protection Status Gap Audit](capital_protection_status_gap_audit.md): Documents the gap between generic capital protection statuses and the specific protection statuses listed in the spec.
- [Capital Protection Status Compatibility Plan](capital_protection_status_compatibility_plan.md): Defines the backward-compatible plan for adding optional specific protection metadata while preserving the existing generic capital protection status contract.
- [Capital Protection TODO Resolution Audit](capital_protection_todo_resolution_audit.md): Audits the TODO items in the capital protection spec against the current research-only capital, session, news, spread, and volatility protection implementations.
- [Capital Protection Policy Decision Plan](capital_protection_policy_decision_plan.md): Defines the safe order for resolving remaining capital protection policy decisions before any future enforcement or integration change.
- [Capital Protection Daily State Policy](capital_protection_daily_state_policy.md): Defines the UTC daily reset, realized PnL basis, daily loss/profit checks, loss-streak reset, and persistence guardrails for daily capital protection state.
- [Capital Protection Loss Counting Policy](capital_protection_loss_counting_policy.md): Defines closed-trade outcome classification, loss streak updates, breakeven handling, partial-exit handling, and reset behavior for capital protection loss streak logic.
- [Capital Protection Profit Target Policy](capital_protection_profit_target_policy.md): Defines realized-PnL profit target triggering, new-entry hard stop behavior, open-position handling, trailing-target restrictions, and UTC reset behavior.
- [Capital Protection Position Limit Policy](capital_protection_position_limit_policy.md): Defines global default max position scope, MAX_POSITIONS trigger behavior, pending-order exclusion, and new-entry blocking behavior.
- [Capital Protection Session Policy](capital_protection_session_policy.md): Defines UTC session schedule defaults, weekend blocking, timezone and daylight saving guardrails, instrument-specific restrictions, and new-entry behavior.
- [Capital Protection Spread Policy](capital_protection_spread_policy.md): Defines conservative spread threshold behavior, unknown-spread handling, instrument/session threshold guardrails, account/data-source restrictions, and new-entry behavior.
- [Capital Protection Volatility Policy](capital_protection_volatility_policy.md): Defines ATR-based v1 measurement, authoritative input timeframe guardrails, profile thresholds, abnormal-candle blocking, and new-entry behavior.
- [Capital Protection News Policy](capital_protection_news_policy.md): Defines manual-only v1 news-event sourcing, UTC normalization, source/update/audit rules, impact-level blocking, event windows, invalid-time handling, and new-entry-only behavior.
- [Capital Protection Manual Pause and Emergency Stop Policy](capital_protection_manual_pause_emergency_stop_policy.md): Defines control authority, priority, platform-wide default scope, persistence, audit trail requirements, and new-entry-only blocking behavior.
- [End-to-End Demo Validation](end_to_end_demo_validation.md): Lists the manual CLI commands for safely validating existing demo/research flows.
- [Backtest Validation Checklist](backtest_validation_checklist.md): Defines offline backtest review checks; it does not approve paper progression.
- [Real Sierra Chart CSV Test Guide](real_sierra_chart_csv_test_guide.md): Explains how to test real exported Sierra Chart CSV files without live connections.
- [Independent Historical Dataset Intake Contract](independent_historical_dataset_intake.md): Defines non-overlap, complete 1m/5m/10m Market OHLC/full-footprint pairs, metadata, matching, overwrite protection, evidence classification, and safety requirements.
- [ACSIL Matching Day2 Multi-Timeframe Validation Result](acsil_matching_day2_multitimeframe_validation_result.md): Records day2 matching OHLC plus ACSIL full footprint validation across 1m, 5m, and 10m.
- [ACSIL Day3 1-Day 1m Validation Result](acsil_day3_1day_1m_validation_result.md): Records one-session (1-day chart load) day3 1m ACSIL validation after A/B semantics fixes, including neutral-blocking and trade-side label checks.
- [ACSIL Day3 1-Day 10m Validation Result](acsil_day3_1day_10m_validation_result.md): Records one-session (1-day chart load) day3 matching OHLC plus ACSIL full footprint validation for 10m, including A/B diagnostic safety results.
- [ACSIL Day3 1-Day 5m Validation Logic Gap](acsil_day3_1day_5m_validation_logic_gap.md): Records one-session (1-day chart load) day3 5m ACSIL validation and documents the A/B diagnostic opposite-bias blocking logic gap as an implementation-readiness stop.
- [Day3 One-Session Order Flow Validation Summary](day3_one_session_orderflow_validation_summary.md): Consolidates Day3 1m/5m/10m one-session ACSIL findings after A/B diagnostic fixes and defines the next independent-session validation step.
- [Order Flow Confirmation Blocking Semantics Audit](orderflow_confirmation_blocking_semantics_audit.md): Audits current A/B diagnostic blocking semantics, documents required decision-matrix behavior, and marks implementation readiness as STOP pending design/test approval.
- [Order Flow Confirmation Design Approval Checklist](orderflow_confirmation_design_approval_checklist.md): Defines the required human-approved blocking semantics, data-quality behavior, and pre-merge test requirements before any future Order Flow confirmation implementation.
- [Order Flow A/B Diagnostic Semantics Post-Fix Validation](orderflow_ab_diagnostic_semantics_postfix_validation.md): Records post-fix validation that neutral/opposite-bias blocking and bearish/bullish trade-side labels are correctly represented in the research-only A/B diagnostic.
- [Order Flow Footprint Implementation Gap Audit](orderflow_footprint_implementation_gap_audit.md): Audits current Footprint / Order Flow capabilities, limitations, safety status, and the next validation phase.
- [Order Flow Confirmation Implementation Readiness Plan](orderflow_confirmation_implementation_readiness_plan.md): Defines the documentation-only approval, test, rollback, and safety checklist before any future Order Flow confirmation implementation.
- [Reports / .gitignore Safety Review](reports_gitignore_safety.md): Explains generated report safety, secrets safety, and ignore rules.
- [MVP Code Freeze Note](mvp_code_freeze.md): Explains that the project is moving from feature-building into cleanup, testing, and validation mode.
- [MVP Code-Freeze Final Review](mvp_code_freeze_final_review.md): Records the completed final review, active freeze status, remaining validation blockers, and unchanged deployment restrictions.

## 4. Validation Order

Follow this safest order:

1. Full pytest.
2. End-to-end CLI demo validation.
3. Order Flow CSV sample validation.
4. Real Sierra Chart exported CSV validation.
5. Backtest validation.
6. Independent historical dataset intake under `docs/independent_historical_dataset_intake.md`.
7. Full independent-period validation only after full acceptance; limited diagnostic intake does not close the blocker.

Do not skip ahead. Paper trading, broker integration, and live trading remain unauthorized; each step must pass before moving to the next, and any failed intake stops the sequence.

## 5. Not Allowed Yet

These are not allowed in the current phase:

- No live trading.
- No paper-trading preparation or simulation.
- No broker connection.
- No MT5 login integration yet.
- No external API integration or calls.
- No Sierra Chart live connection.
- No CME live data connection.
- No real order execution.
- No strategy, risk, numerical drawdown-threshold, Python, Order Flow, or exporter source changes while code freeze is active.
- No real-money trading.
- No bypassing safety gates.

## 6. Human Approval Rule

Future strategy changes remain unauthorized unless a separate documented decision first lifts the applicable code freeze and then completes this full human-reviewed workflow:

- Proposal.
- Review.
- Implementation plan.
- Final review.
- Readiness check.
- Human approval.

A suggestion, proposal, readiness result, or human approval alone does not change strategy rules, lift a freeze, or authorize paper, broker, or live progression; all recorded prerequisites and separate approvals must pass.

## 7. Beginner Summary

The project is now being cleaned and validated before any real trading work.

Think of this phase as offline evidence review: run tests, validate demos and CSVs, review backtests, then intake a genuinely independent non-overlapping dataset under the intake contract. Paper trading remains blocked and requires a separate documented approval after all prerequisites pass.

Live trading, broker connections, and external APIs remain unauthorized; this index does not schedule or approve those phases.

- [Day4 SC delayed orderflow validation summary](day4_sc_delayed_orderflow_validation_summary.md)

- [Day4 SC delayed 1m extended validation addendum](day4_sc_delayed_1m_extended_validation_addendum.md)

- [Order Flow confirmation validation evidence review](orderflow_confirmation_validation_evidence_review.md)

- [Day3 5m aligned Order Flow loss audit](day3_5m_aligned_orderflow_loss_audit.md)

- [Backtest-only context alignment research plan](context_alignment_research_plan.md)

- [Context alignment diagnostic implementation checklist](context_alignment_diagnostic_implementation_checklist.md)

- [Backtest quality drawdown unit contract](backtest_quality_drawdown_unit_contract.md)

- [Research drawdown acceptance criteria](research_drawdown_acceptance_criteria.md)

- [Backtest quality loss cluster diagnostic plan](backtest_quality_loss_cluster_diagnostic_plan.md)

- [Backtest quality loss cluster diagnostic report](backtest_quality_loss_cluster_diagnostic_report.md)

- [Backtest quality post-loss cooldown candidate diagnostic](backtest_quality_post_loss_cooldown_candidate_diagnostic.md)

- [Backtest quality cooldown robustness diagnostic](backtest_quality_cooldown_robustness_diagnostic.md)

- [Backtest quality conditional cooldown A/B diagnostic plan](backtest_quality_conditional_cooldown_ab_diagnostic_plan.md)

- [Backtest quality conditional cooldown A/B diagnostic summary](backtest_quality_conditional_cooldown_ab_diagnostic_summary.md)

- [Backtest quality conditional cooldown A/B research module checklist](backtest_quality_conditional_cooldown_ab_research_module_checklist.md)

- [Backtest quality conditional cooldown private report interpretation](backtest_quality_conditional_cooldown_private_report_interpretation.md)
