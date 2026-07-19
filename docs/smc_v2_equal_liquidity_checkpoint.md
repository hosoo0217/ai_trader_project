# SMC V2 Equal Liquidity Standalone Diagnostic Checkpoint

- Checkpoint ID: `SMC-V2-EQUAL-LIQUIDITY-CHECKPOINT-2026-07-19`
- Review date: `2026-07-19`
- Implementation parent: `2f42c4500a34de1982d9ff803b46647e12021a61`
- Formal decision record:
  `docs/smc_v2_equal_liquidity_diagnostic_freeze_lift_decision.md`
- Formal decision SHA-256:
  `4BEE737E6F447FD86B25918E3F2D43934961B8660F9B556AF296E8C4E0497DDE`
- Status: bounded Equal High and Equal Low standalone implementation completed
  and locally validated; not integrated or promoted.

## 1. Bounded Exception and Global Freeze

- The explicit bounded exception became operationally effective only for this
  Equal Liquidity implementation task.
- The exception did not lift the global code freeze for any unrelated file or
  capability.
- Integration into current SMC, CRT, decision, backtest, risk, execution,
  reporting, configuration, or package-export paths is not authorized.
- Staging, commit, push, paper progression, live progression, broker access, and
  real execution are not authorized.
- The global code freeze remains active outside the exact three-path scope below.

## 2. Exact Three-Path Scope

The only created paths in this task are:

1. `smc/equal_liquidity.py`
2. `tests/test_equal_liquidity.py`
3. `docs/smc_v2_equal_liquidity_checkpoint.md`

No existing Python, test, fixture, configuration, package initializer, or
documentation file changed. The optional
`tests/fixtures/equal_liquidity_cases.json` path remains absent because inline
synthetic fixtures are sufficient.

## 3. Implemented Public API

The standalone module exposes exactly:

- `EQUAL_LIQUIDITY_DETECTOR_VERSION`
- `EqualLiquiditySide`
- `EqualLiquidityConfig`
- `EqualLiquiditySwing`
- `EqualLiquidityObservation`
- `EqualLiquidityPool`
- `EqualLiquidityResult`
- `make_equal_liquidity_id`
- `analyze_equal_liquidity`

The side enum contains only `HIGH` and `LOW`. Config, swing, observation, pool,
and result models are frozen public dataclasses. The locked configuration is
exactly `tolerance_ticks=2`, `minimum_members=2`, and
`minimum_separation_bars=3`.

## 4. Confirmed-Swing and Status Contract

- The detector accepts immutable tuples of already-confirmed swings and fully
  closed observations represented in integer ticks.
- It performs no raw swing detection and does not import the existing float and
  dataframe-based v1 SMC implementation.
- Each swing must have exactly one source event and a first-known confirmation
  no earlier than source index plus `2`.
- Supplied swing IDs are recomputed and must match the reviewed side, source,
  price boundary, instrument, and timeframe.
- Top-level missing `swings` or `observations` context returns `UNKNOWN` without
  partial promotion.
- Missing, wrong-type, or malformed required swing provenance returns `INVALID`,
  never `UNKNOWN`.
- Valid input without a completed two-member pool returns `NONE`.
- A completed deterministic pool returns `VALID`; unresolved final ranking would
  return `AMBIGUOUS` rather than selecting a favorable result.

## 5. Identity and Median Invariants

- Identities use canonical UTF-8 JSON with sorted keys, compact separators, and
  SHA-256.
- All identity payloads contain detector version, normalized instrument,
  normalized timeframe, and explicit liquidity side.
- Exactly four identity kinds are accepted: `SWING`, `CANDIDATE`, `LINEAGE`, and
  `SNAPSHOT`.
- Pending candidate identity is derived from side, first-member swing ID, and
  first-member source index.
- The first two qualifying swings found a stable lineage ID. Later joins and
  lifecycle changes retain lineage and create new immutable snapshot IDs.
- Odd medians use the central tick. Even medians use integer arithmetic with the
  locked half-even tie rule and do not depend on float or Decimal context.

## 6. Chronological Assignment and Containment

- High and Low candidates are independent and processed in supplied confirmed
  chronology.
- A later swing must be at least `3` source bars after the candidate's latest
  member and within `2` ticks of its current reference.
- Before ranking or joining, the detector tentatively appends the swing,
  recomputes median and band, and requires every existing and new member to stay
  within the new inclusive two-tick band.
- Multiple eligible candidates rank by current-reference distance, oldest
  first-member confirmation tuple, and assignment identity.
- Pending candidates use `candidate_id`; active pools use `lineage_id`.
- Pending-member reservation converts to one lineage on activation. A member is
  never reused for another candidate or lineage, including after consumption.
- The locked chain-drift sequence `100, 102, 103, 104, 104` rejects the fifth
  member because the recomputed band would exclude the founding `100` member.

## 7. Lifecycle and Snapshot Invariants

- A pool becomes active only when its second qualifying swing is confirmed.
- Existing active pools evaluate a same-index observation against the immutable
  pre-confirmation snapshot before processing new swing confirmations.
- A newly formed pool cannot consume its founding confirmation bar. Its first
  eligible lifecycle observation has a strictly later index and cannot precede
  first-known time.
- Equal High and Equal Low use mirrored one-tick `SWEPT` and close-through
  `BROKEN` rules.
- `BROKEN` is checked before `SWEPT`. Both states are terminal, reject later
  joins, and cannot reactivate.
- Later valid member joins and terminal transitions append immutable snapshots;
  earlier snapshots are never mutated.
- Appended future inputs preserve the complete earlier snapshot prefix.

## 8. Test-First Evidence

- The dedicated test module was created before the implementation module.
- Expected RED gate: collection failed only because `smc.equal_liquidity` did
  not yet exist.
- The first implementation run produced `38 passed, 1 failed`; the only failure
  was an over-broad static test that counted Python's `__builtins__` dictionary
  and locked `__all__` list as mutable domain state.
- The assertion was narrowed to domain globals without weakening any detector
  invariant.
- Independent final audit then identified that internally malformed provenance,
  swing, and observation instances could leak `AttributeError` instead of
  returning `INVALID`, while the original case covered only `None` and a
  wrong-type object.
- Correction RED gate: the three new malformed-required-field cases failed with
  `AttributeError` while the prior `39` cases passed.
- Validators now normalize every required swing, provenance, and observation
  field explicitly and convert absence into the fail-closed invalid-analysis
  path without broadly hiding unrelated implementation errors.
- Corrected focused result: `42 passed`.
- Corrected full regression result: `1006 passed`.
- The regression total consists of the prior `964` tests plus `42` dedicated
  Equal Liquidity cases.

## 9. Locked Unit-Test Matrix Coverage

The `33` numbered inline synthetic cases cover:

- Equal High and Equal Low formation, tolerance boundaries, separation
  boundaries, near misses, and one-member `NONE`.
- Missing top-level context, missing or internally malformed required
  provenance, swing, and observation fields, wrong types, float and boolean
  ticks, duplicate and unordered indices, naive timestamps, and invalid OHLC.
- Founding first-known time, confirmation-bar non-consumption, observation-first
  same-index precedence, terminal no-join behavior, and immutable later joins.
- Closest-cluster assignment, candidate and lineage identity tie-breaking,
  pending reservation, reservation conversion, and post-consumption no-reuse.
- Tentative all-member containment, inclusive boundaries, chain-drift rejection,
  odd median, integer median, and both half-even parity cases.
- Mirrored `SWEPT` and `BROKEN` behavior, exact-boundary non-consumption,
  terminal precedence, stable lineage, snapshot versioning, repeatability,
  prefix invariance, normalized-tick scaling, frozen models, exact public API,
  and static isolation.

## 10. Isolation and Non-Integration Evidence

- `smc/__init__.py` remains unchanged with SHA-256
  `C8FE33277193D142CF975D1B56AED5432D495A0B01F17F7AD155BDA3DE3FEE0B`.
- The detector imports only Python standard-library modules and the reviewed
  `smc.smc_v2_primitives` foundation.
- Static checks found no pandas, v1 market-structure, DecisionContext, runner,
  network, filesystem, process, configuration, or registration dependency.
- No current production module imports or calls `smc.equal_liquidity`.
- The detector reads no candidate OOS or private market data and produces no
  signal, confidence, action, risk, order, PnL, or readiness decision.

## 11. Artifact Identities Before Checkpoint Audit

- `smc/equal_liquidity.py`
  - bytes: `33690`
  - physical lines: `937`
  - SHA-256: `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`
- `tests/test_equal_liquidity.py`
  - bytes: `21777`
  - physical lines: `592`
  - SHA-256: `3AA7AFF377FCCFEBB463615E6B16952B025FBB99432A7F9C2888AC96531B3E83`
- The checkpoint document identity is calculated only after this record is
  written and is not self-embedded.

## 12. Rollback

The task remains untracked, unintegrated, and unpromoted. Before commit, bounded
rollback is limited to the exact three newly created paths and requires explicit
instruction before destructive removal. No existing source or documentation
requires restoration. After any future commit, rollback must use a bounded revert
instead of history rewriting and must be followed by focused and full regression
tests plus exact-scope audit.

## 13. Stop Conditions

Stop without integration or promotion if:

- any path outside the exact three-path scope changes,
- the optional fixture or another path becomes necessary,
- shared primitives or `smc/__init__.py` require modification,
- any focused or full-regression test fails,
- identity, median, assignment, reservation, containment, lifecycle, or prefix
  behavior cannot remain exactly deterministic,
- a private, generated, performance-derived, candidate, or external fixture is
  requested,
- a current public interface, import path, default output, or execution path
  changes, or
- integration appears necessary to validate the standalone detector.

A stop condition does not authorize a workaround, fallback behavior, parameter
relaxation, or scope expansion.

## 14. Checkpoint State

- `BOUNDED_EXCEPTION_OPERATIONALLY_EFFECTIVE=True`
- `EQUAL_LIQUIDITY_IMPLEMENTATION_COMPLETED=True`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_TOTAL=42`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_TOTAL=1006`
- `OPTIONAL_FIXTURE_CREATED=False`
- `INTEGRATION_PERFORMED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
- `PAPER_PROGRESSION_REMAINS_BLOCKED=True`
- `LIVE_PROGRESSION_REMAINS_BLOCKED=True`

## 15. Next Gate

The next permissible action is an independent final code, test, scope, and diff
audit of these exact three paths. A passing audit may authorize a later staging
request, but this checkpoint does not authorize staging, commit, push, or
integration.
