# SMC v2 and Volume Profile Diagnostic Change Proposal

## 1. Proposal Record

- Proposal ID: `SMC-V2-VP-DIAGNOSTIC-2026-07-19`.
- Category: `RESEARCH_ANALYSIS`.
- Priority: `HIGH`.
- Status: `ACCEPT_FOR_BOUNDED_FREEZE_LIFT_REVIEW`.
- Reviewed by: `HOSOO`.
- Review date: `2026-07-19`.
- Human review required: `True`.
- Auto-implementation allowed: `False`.
- Code implementation allowed now: `False`.
- Parent plan: `docs/smc_v2_volume_profile_implementation_plan.md`.
- Recommended specification:
  `docs/smc_v2_volume_profile_recommended_specification.md`.
- Baseline Git commit:
  `c8327f76d4e436520b5713c2a6ca33559a6b7c41`.
- Code-freeze status: `ACTIVE`.

This is a documentation-only formal proposal. It does not edit Python, config,
strategy, risk, Order Flow, exporter, broker, paper-trading, or live-trading
behavior. It does not lift the code freeze.

## 2. Purpose

Propose a future test-first, disabled-by-default, diagnostic-only SMC v2 and
historical Volume Profile research layer that expands analytical evidence while
preserving the current frozen system and all existing OOS evidence.

The proposal exists because the project documentation describes broader SMC and
Volume Profile intentions, while the current implementation provides only a
simpler SMC subset and partial Order Flow foundations.

## 3. Current Capability and Gap

Implemented SMC capability currently includes:

- swing highs and lows,
- basic bullish, bearish, neutral, or unknown market structure,
- BOS and CHOCH,
- simple high and low liquidity sweeps,
- a combined SMC bias and confidence result.

Implemented Order Flow foundations currently include:

- historical full-footprint import,
- `BAR_SUMMARY` fallback import,
- data-quality checks,
- Delta and CVD,
- basic price-level imbalance,
- basic absorption,
- Order Flow context and historical replay.

The proposed concepts are not currently complete production detectors:

- Fair Value Gap,
- Order Block,
- Breaker Block,
- Mitigation Block,
- Premium/Equilibrium/Discount,
- Equal High/Equal Low,
- Internal/External liquidity mapping,
- Inducement,
- Dealing Range,
- Kill-zone-specific SMC context,
- session POC, VAH, VAL, and later separately specified HVN/LVN.

## 4. Proposed Scope

The proposed future work is limited to standalone historical research detectors,
synthetic fixtures, tests, and documentation.

Initial work would:

1. Add shared tick-normalization, confirmation-time, lifecycle, and deterministic
   identity primitives.
2. Implement the detectors in the dependency order specified by
   `SMC-V2-VP-SPEC-2026-07-19`.
3. Keep every feature disabled by default.
4. Test modules directly without connecting them to current execution decisions.
5. Reject incomplete or ambiguous context rather than manufacturing a label.
6. Preserve existing public interfaces and default behavior.
7. Require a later separate proposal before diagnostic trace integration.
8. Require another later proposal before any decision-affecting experiment.

Fibonacci is explicitly excluded.

## 5. Proposed First Freeze-lift Boundary

This proposal recommends, but does not grant, a narrowly bounded diagnostic-only
freeze lift for a future implementation task.

Potentially allowed after separate approval:

- new standalone files in `smc/`,
- `orderflow/volume_profile.py`,
- dedicated tests,
- synthetic non-private fixtures,
- minimal module export updates required for direct test imports,
- related documentation.

Not allowed in the first implementation boundary:

- `main.py` wiring,
- Decision Engine changes,
- context-alignment changes,
- paper-trading-flow changes,
- SMC or Order Flow confidence changes,
- BUY, SELL, NO_TRADE, entry, exit, risk, or sizing changes,
- CLI behavior changes,
- private dataset edits or commits,
- generated evidence replacement,
- broker, MT5, Sierra live, CME live, or external-API work.

## 6. Expected Research Benefit

If implemented correctly, the diagnostic layer should provide:

- a more complete and auditable structural market description,
- explicit zone creation and lifecycle evidence,
- separation of internal and external liquidity,
- session-aware SMC event labels,
- true price-level session POC and Value Area from qualified footprint data,
- better visibility into whether advanced concepts add independent information or
  merely duplicate current SMC/CRT/Order Flow signals,
- a versioned base for later independent research.

These are analytical benefits, not profitability claims.

## 7. Risks and Possible Downsides

- SMC terminology is not universally standardized.
- Order Block, Mitigation Block, and Inducement can become hindsight labels.
- Future swing confirmation can create look-ahead leakage if event time and
  first-known time are confused.
- Too many correlated features can inflate confidence without new information.
- Stateful zones can introduce lifecycle and replay inconsistencies.
- Kill-zone errors can arise from timezone or daylight-saving mistakes.
- `BAR_SUMMARY` cannot support a true Volume Profile.
- More rules may reduce interpretability, coverage, or trade samples.
- Adding features after a failed OOS result can become outcome-driven tuning.
- Successful detector tests do not establish strategy improvement or readiness.

The proposed specification reduces these risks but cannot eliminate all software
defects or research uncertainty.

## 8. Evidence Boundary

The locked July OOS result remains:

`VALID_OOS_EVIDENCE — PERFORMANCE_FAILED`

It recorded `410` iterations, `58` realized trades, `0` unresolved trades,
`-2550.00` total PnL, and profit factor
`0.43333333333333335` for the frozen strategy.

That evidence may be used to verify reproduction and compatibility. It must not
be used to select profitable SMC v2 thresholds, rewrite labels, choose favorable
definitions, or justify a favorable rerun.

A later decision-affecting strategy version requires new untouched independent
data and a new pre-registered OOS sequence.

## 9. Required Tests

Before any detector promotion:

- focused unit tests,
- positive, negative, boundary, ambiguous, and invalid-data fixtures,
- prefix-invariance and confirmation-delay tests,
- lifecycle transition tests,
- tick-normalization and deterministic-ID tests,
- timezone, DST, overnight, holiday, and early-close tests,
- Volume Profile conservation, POC tie, Value Area tie, and completeness tests,
- explicit `BAR_SUMMARY` rejection for official Volume Profile,
- existing full pytest suite passing,
- default-mode compatibility checks,
- no decision, risk, entry, exit, PnL, or iteration-accounting change.

The verified pre-proposal regression baseline is `881 passed` using:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

## 10. Acceptance Criteria for Standalone Diagnostic Modules

The initial implementation package would be acceptable only when:

1. All ten specification decisions are explicitly approved.
2. The bounded freeze lift names exact allowed and forbidden files.
3. Every implemented detector passes its fixture matrix.
4. Prefix invariance proves no future-data leakage in tested paths.
5. Full-footprint volume is conserved exactly in Volume Profile tests.
6. All new feature flags remain false by default.
7. Existing tests remain passing.
8. No current decision or risk behavior changes.
9. No private or generated evidence is committed accidentally.
10. Documentation, hash, test result, and resume checkpoint are updated.

Passing these criteria would approve standalone diagnostic modules only. It would
not approve trace wiring, a new confidence score, a strategy change, paper
trading, or live trading.

## 11. Rollback Plan

- Create a clean pre-implementation Git checkpoint.
- Work in small module-specific commits.
- Keep tests and one detector together where practical.
- Keep current modules and public contracts intact.
- Disable one module through its independent default-false flag.
- Revert a bounded module commit if focused or regression tests fail.
- Re-run the full baseline after any revert.
- Never rewrite external OOS evidence or private source data.

## 12. Proposed Review Decisions

Available proposal-review outcomes:

- `ACCEPT_FOR_BOUNDED_FREEZE_LIFT_REVIEW`: specification may move to a separate
  freeze-lift decision and implementation-readiness review.
- `NEEDS_SPEC_CHANGES`: definitions or scope require revision.
- `NEEDS_MORE_DATA`: data-format or calendar evidence is insufficient even for
  standalone detector design.
- `REJECT`: proposal should not move forward.

Acceptance does not implement code and does not itself lift the freeze.

## 13. Required Human Review Checklist

- [x] Parent implementation plan reviewed.
- [x] Recommended specification reviewed in full.
- [x] Order Block semantics accepted.
- [x] Mitigation Block definition accepted.
- [x] Equal High/Equal Low rules accepted.
- [x] Swing hierarchy and Dealing Range rules accepted.
- [x] FVG rules accepted.
- [x] Breaker Block rules accepted.
- [x] Inducement sequence accepted.
- [x] Kill-zone timezone and calendar rules accepted.
- [x] Volume Profile POC and Value Area rules accepted.
- [x] Feature flags and bounded freeze-lift review scope accepted.
- [x] Fibonacci exclusion confirmed.
- [x] Diagnostic-only and disabled-by-default boundary confirmed.
- [x] July OOS non-tuning restriction confirmed.
- [x] No paper or live progression confirmed.
- [x] Rollback and test requirements confirmed.

## 14. Current Proposal Decision

Status: `ACCEPT_FOR_BOUNDED_FREEZE_LIFT_REVIEW`

The ten recommended technical decisions were explicitly accepted by HOSOO on
`2026-07-19`. This proposal is accepted only for a separate bounded
diagnostic-only freeze-lift review.

No registration command has been executed. No proposal-store record has been
created. No code-freeze-lift decision has been recorded. Python implementation
remains unauthorized.

The next correct step is to review the separate diagnostic-only freeze-lift
document, checkpoint the accepted documentation package, complete the remaining
final-review/readiness gates, and record an explicit narrowly bounded freeze-lift
decision before any Python implementation task.

## 15. Beginner Summary

This proposal prepares a careful way to add richer SMC and true historical
Volume Profile analysis without breaking the current trader.

It deliberately starts with standalone detectors and tests. The new analysis
would be off by default and would not change trades. Fibonacci is excluded. The
old failed OOS result stays unchanged and cannot be used to tune the new rules.

For now this is a proposal awaiting review, not permission to code.
