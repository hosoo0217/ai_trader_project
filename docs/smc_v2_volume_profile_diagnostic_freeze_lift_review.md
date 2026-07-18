# SMC v2 and Volume Profile Diagnostic Code-Freeze-Lift Review

## 1. Review Status

- Review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Status: `READY FOR FINAL HUMAN DECISION AFTER DOCUMENTATION CHECKPOINT`.
- Requested lift type: `BOUNDED DIAGNOSTIC-ONLY`.
- Current code-freeze status: `ACTIVE`.
- Freeze lifted by this review: `False`.
- Python implementation allowed now: `False`.
- Strategy or execution change allowed: `False`.
- Paper or live progression allowed: `False`.

This review evaluates a possible narrow exception to the active code freeze. It
does not grant the exception. A later explicit human decision must name this
review ID and the exact approved scope.

## 2. Inputs Reviewed

- `docs/smc_v2_volume_profile_implementation_plan.md`
- `docs/smc_v2_volume_profile_recommended_specification.md`
- `docs/smc_v2_volume_profile_change_proposal.md`
- `docs/smc_v2_volume_profile_change_proposal_review.md`
- current SMC v1 module boundaries,
- current historical full-footprint import and Order Flow boundaries,
- active MVP code-freeze and final-cleanup rules,
- verified regression baseline of `881 passed`.

## 3. Purpose of the Requested Exception

The requested exception would permit small standalone historical-analysis
modules and their direct tests. It would not connect those modules to the current
runner, DecisionContext, SMC confidence, Order Flow confidence, trade decisions,
risk rules, entry, exit, paper trading, or live systems.

The purpose is to test whether each detector can be made deterministic,
look-ahead-safe, and auditable before any integration is considered.

## 4. Exact Proposed Allowed Scope

If a later decision grants the bounded lift, the initial implementation task may
create only the following production modules:

- `smc/smc_v2_primitives.py`
- `smc/equal_liquidity.py`
- `smc/dealing_range.py`
- `smc/liquidity_map.py`
- `smc/fair_value_gap.py`
- `smc/order_block.py`
- `smc/mitigation_block.py`
- `smc/breaker_block.py`
- `smc/kill_zones.py`
- `smc/inducement.py`
- `orderflow/volume_profile.py`

It may create matching dedicated test files and synthetic public fixtures under
`tests/` that contain no private or copied candidate market data.

Minimal edits may be made to:

- `smc/__init__.py`
- `orderflow/__init__.py`

Those two existing files may expose new standalone result, config, and analyzer
types only. They may not enable execution, instantiate detectors automatically,
or change existing exports incompatibly.

Related documentation and checkpoint files may be updated.

## 5. Exact Forbidden Scope

The bounded lift would not authorize edits to:

- `main.py`
- `core/decision_engine.py`
- `core/decision_context.py`
- `core/context_alignment.py`
- `core/paper_trading_flow.py`
- current `smc/market_structure.py`
- current `smc/bos_choch.py`
- current `smc/liquidity_sweep.py`
- current `smc/smc_context.py`
- current Order Flow analysis, importer, replay, or context modules
- `risk/`
- `broker/`
- `config/`
- `sierra_acsil/`
- `private_data/`
- external OOS evidence or generated validation reports.

It would also forbid:

- CLI flags or runner wiring,
- DecisionContext integration,
- SMC/CRT/Order Flow confidence changes,
- trade filtering or action changes,
- risk, sizing, stop, target, entry, or exit changes,
- parameter optimization against observed OOS performance,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- Fibonacci.

Any need to edit a forbidden file is a stop condition requiring a new review.

## 6. Required Implementation Order

The proposed lift is phased even within its bounded scope:

1. Shared primitives and test helpers.
2. Equal High/Equal Low.
3. Dealing Range.
4. Internal/External liquidity mapping.
5. Premium/Equilibrium/Discount output within Dealing Range.
6. FVG.
7. Order Block.
8. Mitigation Block event.
9. Breaker Block.
10. Kill-zone context.
11. Inducement.
12. Completed-session Volume Profile.

One phase must pass focused and full regression tests before the next begins.
Inducement cannot move ahead of its dependencies. Volume Profile must reject
`BAR_SUMMARY` as official profile input.

## 7. Required Test and Review Gates

Before each module is promoted:

- positive, negative, boundary, insufficient, ambiguous, and invalid fixtures,
- prefix-invariance and first-known-time tests,
- lifecycle and deterministic-ID tests,
- tick and floating-point normalization tests,
- full existing pytest suite,
- documentation update,
- review of changed-file scope,
- confirmation that no private/generated evidence was added.

Additional Volume Profile gates:

- exact volume conservation,
- POC and Value Area tie behavior,
- session, DST, holiday, and incomplete-data cases,
- source-type qualification,
- explicit `BAR_SUMMARY` rejection.

## 8. Default-off and Isolation Proof

The standalone modules must not be imported or invoked by current execution
paths. Their config objects must default to disabled diagnostic behavior where
an enabled field exists.

Required isolation evidence:

- no current action, allowed status, risk plan, entry, exit, balance, PnL, or
  iteration-count change,
- no current CLI output change,
- no current report-schema change,
- no current SMC or Order Flow confidence change,
- no current public constructor break.

The first bounded lift does not authorize diagnostic trace wiring. That is a
later separate proposal after standalone evidence is complete.

## 9. Git and Checkpoint Requirements

Before Python work:

1. Independently validate all accepted documentation.
2. Commit the documentation package separately from code.
3. Confirm `HEAD = origin/main` or record the intentionally unpushed checkpoint.
4. Confirm a clean worktree.
5. Record the new documentation commit as the implementation parent.
6. Run the full pytest baseline from that clean parent.
7. Record exact allowed files for the first module task.

During implementation:

- use small phase-specific commits,
- never mix docs-only approval state with detector code in one commit,
- stop on unexpected worktree changes,
- do not stage private or generated artifacts,
- update the resume checkpoint after each accepted phase.

## 10. Rollback Requirements

- Each detector must be removable through a bounded revert.
- Existing v1 modules remain intact.
- No destructive configuration or evidence migration is allowed.
- A failed focused or full test stops promotion.
- Unexpected default output changes require reverting the affected phase.
- Rollback must be followed by the full pytest suite and clean-scope audit.

## 11. Risk Review

Residual risks remain:

- specification or implementation mistakes,
- hidden look-ahead leakage,
- state lifecycle inconsistencies,
- timezone and calendar defects,
- correlated evidence being mistaken for independent confirmation,
- later pressure to tune definitions against known failed outcomes.

The narrow standalone scope, immutable histories, prefix tests, synthetic
fixtures, and lack of decision integration reduce these risks. They do not prove
profitability or eliminate all defects.

## 12. Readiness Findings

- Ten technical decisions accepted: `PASS`.
- Formal proposal review: `PASS` for bounded freeze-lift review.
- Fibonacci exclusion: `PASS`.
- Diagnostic-only default-off boundary: `PASS`.
- Allowed and forbidden file scope: `DEFINED`.
- Test and rollback requirements: `DEFINED`.
- Existing regression baseline: `881 passed`.
- Documentation checkpoint commit: `PENDING`.
- Clean implementation parent commit: `PENDING`.
- Explicit final freeze-lift decision: `PENDING`.
- Python implementation authorization: `NOT YET GRANTED`.

## 13. Review Recommendation

Recommendation:
`READY_FOR_FINAL_HUMAN_DECISION_AFTER_DOCUMENTATION_CHECKPOINT`

The technical and safety scope is sufficiently bounded for a final human
freeze-lift decision after the accepted documentation package is independently
validated and committed. The first implementation authorization, if later
granted, should be limited to shared primitives and their direct tests. Later
detectors should advance one phase at a time.

## 14. Decision Required

This review does not lift the freeze. After the documentation checkpoint and
remaining readiness validation, HOSOO must explicitly decide whether to grant or
reject review ID `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.

Until that later decision is recorded:

- code freeze remains active,
- Python changes remain prohibited,
- strategy and execution remain unchanged,
- paper and live progression remain blocked.
