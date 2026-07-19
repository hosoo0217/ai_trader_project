# SMC V2 Equal Liquidity Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-EQUAL-LIQUIDITY-FREEZE-LIFT-DECISION-2026-07-19`.
- Decision date: `2026-07-19`.
- Documentation parent: `b6ff9f940ebe0b088164482e9623bb3ef73ded4b`.
- Requested module: standalone Equal High and Equal Low liquidity diagnostics.
- Global project code freeze: `ACTIVE`.
- Current task type: documentation-only formal decision record.
- Python implementation status: `NOT_AUTHORIZED IN THIS TASK`.
- Integration status: `NOT_AUTHORIZED`.

Final decision classification:

`APPROVED — BOUNDED EQUAL-LIQUIDITY FREEZE-LIFT DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`

## 2. Effective-State Interpretation

The shared-primitives task is completed, independently audited, committed, and
present on local and live `main`. The next dependency in the accepted order is
Equal High and Equal Low. Neither the shared-primitives exception nor this file
silently authorizes Python work.

The bounded Equal Liquidity exception becomes operational only after all of the
following later gates pass:

1. this record receives an independent final audit,
2. this documentation checkpoint is committed and pushed separately from code,
3. local `HEAD`, local `origin/main`, and live remote `main` are reconciled,
4. the worktree is clean and the full regression baseline passes,
5. an exact implementation preflight confirms the reserved paths and API below,
6. every optional fixture decision is resolved before file creation, and
7. HOSOO explicitly authorizes that bounded Python implementation task.

Until all seven gates pass, the decision is recorded but non-operational. The
global code freeze remains active for every Python, test, fixture, configuration,
integration, and unrelated documentation path.

## 3. Locked Decision Inputs

- Recommended specification:
  `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256: `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`
- Implementation plan:
  `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256: `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`
- Shared-primitives freeze-lift decision:
  `docs/smc_v2_volume_profile_diagnostic_freeze_lift_decision.md`
  - SHA-256: `E6A68EA0A5BFC3815D04705E362E013BABE53A90951C0AB86EC0B323B5B9759C`
- Completed shared-primitives checkpoint:
  `docs/smc_v2_volume_profile_shared_primitives_checkpoint.md`
  - SHA-256: `4E80F40431A708BFC641DA3EC664722BDD20EDAE642843D9634D5B37DDB7679B`
- Shared-primitives implementation commit:
  `b6ff9f940ebe0b088164482e9623bb3ef73ded4b`.
- Post-push focused result: `83 passed`.
- Post-push full regression result: `964 passed`.

These inputs establish the accepted dependency order and shared vocabulary.
They do not provide performance evidence or trading-readiness approval.

## 4. Exact Change Authorized in This Documentation Task

The only repository path authorized for creation or modification now is:

- `docs/smc_v2_equal_liquidity_diagnostic_freeze_lift_decision.md`

No Python, test, fixture, configuration, package export, existing documentation,
external evidence, or generated report may change in this task. Staging, commit,
push, detector execution, and integration are separate later gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If the later implementation preflight and explicit authorization pass, the task
is reserved to exactly these paths:

- production module: `smc/equal_liquidity.py`
- dedicated unit tests: `tests/test_equal_liquidity.py`
- implementation checkpoint: `docs/smc_v2_equal_liquidity_checkpoint.md`
- optional synthetic fixture, only if inline fixtures are proven insufficient:
  `tests/fixtures/equal_liquidity_cases.json`

Inline synthetic fixtures are required by default. The optional JSON path must
remain absent unless the preflight records a concrete, reviewed need for it.

The later task must not edit `smc/__init__.py`. Direct test imports are sufficient
for a standalone module. Any need for another path is a stop condition requiring
a new scope review and explicit human approval before that edit occurs.

## 6. Exact Functional Boundary

The later module may implement only:

- immutable, already-confirmed swing inputs,
- deterministic Equal High and Equal Low candidate clustering,
- active pool membership and immutable snapshot versioning,
- the locked `SWEPT` and `BROKEN` terminal lifecycle events,
- explicit valid, invalid, unknown, none, and ambiguous results,
- deterministic side-aware lineage and snapshot identifiers, and
- pure, prefix-invariant analysis over immutable synthetic or caller-supplied
  tuples.

The module must not detect raw swings from OHLC data. It must not implement swing
hierarchy, Dealing Range, Internal or External liquidity mapping, Premium or
Discount, FVG, Order Block, Mitigation Block, Breaker Block, Inducement, kill
zones, Volume Profile, confidence, signals, trade filtering, or execution.

## 7. Locked Confirmed-Swing and Observation Input Contract

The future public input model is locked as follows:

- `EqualLiquiditySide` is a string enum with exactly `HIGH` and `LOW`.
- `EqualLiquiditySwing` is a frozen dataclass containing:
  - `side: EqualLiquiditySide`,
  - `price_tick: int`,
  - `provenance: SMCV2EventProvenance`, and
  - `swing_id: str`.
- Each swing provenance contains one source event index and timestamp plus a
  separate first-known confirmation index and timestamp.
- The source index is the swing-price event bar. The confirmation index is the
  first closed bar at which the compatible `swing_lookback=2` process could know
  that swing, and therefore cannot precede source index plus `2`.
- `EqualLiquidityObservation` is a frozen dataclass containing:
  - `index: int`,
  - `timestamp: datetime`,
  - `high_tick: int`,
  - `low_tick: int`, and
  - `close_tick: int`.
- Observations represent fully closed bars only and must satisfy
  `low_tick <= close_tick <= high_tick`.
- Swing and observation tuples must be strictly chronological by index and
  non-decreasing by normalized UTC timestamp. Duplicate indices are invalid.
- All price values are integer ticks. Floats and unnormalized prices are not
  accepted by this module.
- The top-level `swings` and `observations` inputs each accept an immutable tuple
  or `None`. `None` means that the caller did not supply that complete top-level
  context and deterministically returns `UNKNOWN` without partial analysis.
- An empty supplied tuple is valid context. An empty swing tuple can produce
  `NONE`; an empty observation tuple leaves an otherwise valid pool active.
- Once a swing tuple is supplied, every `EqualLiquiditySwing` must contain valid
  required provenance. Missing, `None`, wrong-type, or internally malformed
  provenance deterministically returns `INVALID`, never `UNKNOWN`.

The module must not import the mutable float-based v1 `SwingPoint`, pandas, or a
current production analyzer. A later compatibility adapter is an integration
task and is explicitly outside this decision.

## 8. Locked Public API

The later module's proposed public surface is limited to:

- `EQUAL_LIQUIDITY_DETECTOR_VERSION`
- `EqualLiquiditySide`
- `EqualLiquidityConfig`
- `EqualLiquiditySwing`
- `EqualLiquidityObservation`
- `EqualLiquidityPool`
- `EqualLiquidityResult`
- `make_equal_liquidity_id`
- `analyze_equal_liquidity`

`EqualLiquidityConfig` is a frozen dataclass with these locked defaults:

- `tolerance_ticks=2`
- `minimum_members=2`
- `minimum_separation_bars=3`

All three values must be real integers and booleans must be rejected. Tolerance
must be non-negative, while member and separation minimums must be positive.
This detector version must reject values other than the locked `2`, `2`, and `3`
combination. Any parameter variant requires a separately versioned specification
and must not be selected from observed performance.
No runtime enable flag is introduced because no runtime import or integration is
authorized. The module remains inert unless directly imported and called.

`EqualLiquidityPool` and `EqualLiquidityResult` must be frozen. Pool snapshots
must expose side, stable lineage ID, immutable snapshot ID, ordered member swing
IDs, ordered source indices, reference tick, tolerance band, first-known
provenance, lifecycle state, and lifecycle events. Results must expose an
`SMCV2PrimitiveStatus`, immutable pool snapshots, reasons, and blocking reasons.

## 9. Locked Side-Aware Deterministic Identity

Equal High and Equal Low are liquidity sides, not bullish or bearish trading
directions. The implementation must not map `HIGH` to `BEARISH`, map `LOW` to
`BULLISH`, or use `SMCV2Direction.UNKNOWN` to erase side identity.

`make_equal_liquidity_id` must use canonical UTF-8 JSON and SHA-256 with sorted
keys and compact separators. It must support exactly four identity kinds:
`SWING`, `CANDIDATE`, `LINEAGE`, and `SNAPSHOT`.

Every identity payload must include:

- identity kind,
- detector version,
- normalized uppercase instrument,
- normalized uppercase timeframe,
- explicit `HIGH` or `LOW` side.

A `SWING` identity additionally includes:

- the one source event index, and
- the point boundary where `lower_tick = upper_tick = price_tick`.

A `CANDIDATE` identity additionally includes:

- exactly the first-member source index, and
- exactly the first-member swing ID.

The candidate ID is created when one unassigned swing begins a pending
candidate. It is stable for that pending candidate and cannot be used as an
active pool lineage ID.

A `LINEAGE` identity additionally includes:

- exactly the two ordered founding source indices,
- exactly the two ordered founding swing IDs,
- the founding reference tick, and
- the founding lower and upper tolerance ticks.

A `SNAPSHOT` identity additionally includes:

- the stable lineage ID,
- ordered source indices,
- ordered swing IDs,
- integer reference tick,
- integer lower and upper tolerance ticks, and
- lifecycle state.

The stable lineage ID is founded by the first two qualifying swings and never
changes. A later member or lifecycle event creates a new immutable snapshot with
the same lineage ID and a new snapshot ID. Previous snapshots are never mutated
or retroactively replaced.

The analyzer must recompute each supplied `swing_id` from the reviewed swing
fields, instrument, and timeframe and reject any mismatch. Confirmation time is
validated and reported but does not alter the historical price-event identity.

Empty text, duplicate or unordered indices, duplicate swing IDs, wrong side or
state types, malformed hashes, and inconsistent boundaries fail closed. Hashes
must be lowercase 64-character hexadecimal strings. No outcome, performance,
future observation, mutable object address, local path, or current clock value
may enter any identity.

## 10. Locked Even-Member Median Tick Rule

Member price ticks are sorted numerically for reference calculation while member
identity order remains chronological.

- An odd member count uses the central sorted integer tick.
- An even member count uses the arithmetic mean of the two central ticks.
- If that mean is an integer tick, that integer is used.
- If that mean is exactly half a tick, it is rounded to the nearest even integer
  tick using deterministic half-even behavior.
- The calculation must use integer arithmetic and must not depend on binary
  float behavior or the process-wide Decimal context.

Examples locked by this rule:

- ticks `100, 101` produce reference tick `100`,
- ticks `101, 102` produce reference tick `102`, and
- ticks `100, 102` produce reference tick `101`.

The tolerance band is `[reference_tick - 2, reference_tick + 2]` using the
locked default configuration. This deterministic tie rule is a specification
choice and is not derived from observed OOS performance.

## 11. Locked Chronological Cluster Assignment and Member Reuse

The analyzer must process already-confirmed swings in the supplied chronological
order. It must reject unordered input rather than silently sorting and hiding a
caller defect. High and Low candidates are processed independently.

The assignment rules are:

1. An unassigned swing begins a pending same-side candidate, receives the locked
   deterministic candidate ID, and becomes reserved to that candidate.
2. A later same-side swing may join only when its source index is at least
   `3` bars after the candidate's latest member source index.
3. Its price must be within `2` ticks inclusive of the candidate's current
   deterministic reference tick.
4. Before ranking or joining, tentatively append the swing, recompute the locked
   median and tolerance band, and require every existing and new member price
   tick to remain inside that recomputed inclusive band. A candidate that fails
   this all-member containment check is ineligible for that swing.
5. A pending candidate becomes an emitted active pool only when its second
   qualifying member is confirmed.
6. First-known pool time is the later of the two founding confirmation events.
7. When a swing qualifies for multiple pending or active same-side candidates,
   choose the smallest absolute distance to current reference tick, then the
   oldest first-member confirmation tuple, then the lexicographically smallest
   assignment identity. The assignment identity is `candidate_id` for a pending
   candidate and `lineage_id` for an active pool.
8. A swing reserved to a pending candidate cannot be evaluated for, found, or
   join another pending candidate or active lineage of the same side.
9. When a pending candidate becomes active, every candidate reservation becomes
   a member assignment to that one lineage.
10. A swing assigned to an active lineage is never reused to found or join
   another candidate or lineage, including after the original pool is consumed.
11. Later qualifying swings may join an active unconsumed pool. Joining creates a
   new immutable snapshot, recomputes the median and tolerance band, and leaves
   all earlier snapshots unchanged.
12. A consumed pool accepts no later member and cannot reactivate.

Candidate eligibility, including tentative all-member containment, must be
computed before the multiple-candidate ranking rule. If a swing is ineligible
for one candidate, that candidate is excluded rather than ranked. If no
candidate remains eligible, the unassigned swing begins its own pending
candidate and receives its own deterministic candidate ID.

Pending one-member candidates are internal analysis state only. They are not
reported as valid liquidity pools. A valid input with no completed pool returns
`NONE`, not an invented result.

## 12. Locked Lifecycle Precedence

For a newly formed pool, a lifecycle observation is eligible only when
`observation.index > pool.first_known_confirmation_index`. Its timestamp also
cannot precede the normalized first-known confirmation timestamp. The founding
confirmation bar cannot consume its own newly knowable pool by reusing a wick or
close that occurred before confirmation. Exact tolerance-boundary touch without
a one-tick excursion does not consume a pool.

When an already active pool has both a closed-bar observation and one or more new
swing confirmations at the same index, ordering is locked as follows:

1. evaluate that observation against the immutable pool snapshot that existed
   before the same-index confirmation events,
2. if the observation consumes the pool, record the terminal event and reject
   all same-index and later member joins for that lineage, and
3. only if the pool remains active, process same-index swing confirmations in
   their locked chronological tie-break order and emit any updated snapshot.

A pool first created by those same-index confirmation events is not evaluated
against that index's already completed observation. Its earliest eligible
lifecycle observation is the next strictly later observation index.

For an active Equal High pool:

1. assign `BROKEN` when `close_tick >= upper_tick + 1`,
2. otherwise assign `SWEPT` when `high_tick >= upper_tick + 1` and
   `close_tick <= upper_tick`, and
3. otherwise keep the pool active.

For an active Equal Low pool:

1. assign `BROKEN` when `close_tick <= lower_tick - 1`,
2. otherwise assign `SWEPT` when `low_tick <= lower_tick - 1` and
   `close_tick >= lower_tick`, and
3. otherwise keep the pool active.

`BROKEN` is evaluated before `SWEPT` for deterministic precedence, although a
valid observation cannot satisfy both close conditions. `SWEPT` and `BROKEN`
are terminal and consume the pool. No default bar-count expiry exists. Lifecycle
events must use `SMCV2LifecycleEvent` and cannot rewrite lineage identity or a
prior snapshot.

## 13. Locked Result Status Semantics

- `VALID`: at least one deterministically valid pool snapshot is present.
- `NONE`: input is valid and sufficient to analyze, but no completed pool exists.
- `UNKNOWN`: a required top-level `swings` or `observations` context is explicitly
  `None`; no partial result is promoted.
- `AMBIGUOUS`: internally contradictory identities or equally ranked candidates
  remain after all locked tie-breakers.
- `INVALID`: malformed type, chronology, OHLC relationship, tick value,
  configuration, duplicate identity, impossible lifecycle, or missing or
  malformed required swing provenance is present.

The analyzer must fail closed with explicit reasons. It must not discard invalid
rows, silently coerce floats, infer timestamps, repair order, or select a
favorable candidate.

## 14. Locked Inline Synthetic Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
at least:

1. Equal High positive formation.
2. Equal Low positive formation.
3. Exactly `2` ticks inclusive equality.
4. A `3`-tick price near miss.
5. Exactly `3` bars inclusive member separation.
6. A `2`-bar separation rejection.
7. One-member insufficient result returning `NONE`.
8. Top-level `swings=None` returning `UNKNOWN` without partial analysis.
9. Top-level `observations=None` returning `UNKNOWN` without partial analysis.
10. Missing, `None`, wrong-type, and internally malformed required swing
    provenance returning `INVALID` and never `UNKNOWN`.
11. Invalid side, float tick, boolean tick, duplicate index, unordered index,
   naive timestamp, and invalid OHLC observations.
12. Founding second-member first-known timing.
13. Founding confirmation-bar non-consumption for both High and Low pools.
14. Observation-before-member ordering when an existing pool and a new swing
    confirmation share an index.
15. Terminal same-index observation preventing that swing and later joins.
16. Later member join without mutation of the earlier snapshot.
17. Multiple-cluster closest-reference assignment.
18. Deterministic pending candidate ID from side, first swing ID, and source
    index, including repeatability and side separation.
19. Mixed pending and active tie resolution using candidate ID and lineage ID as
    their respective assignment identities.
20. Pending-member reservation preventing evaluation by another candidate.
21. Reservation conversion to one lineage and no member reuse after consumption.
22. Tentative all-member containment at the inclusive tolerance boundary.
23. Chain-drift rejection using synthetic ticks `100, 102, 103, 104, 104` when
    the recomputed median band would exclude the founding `100` tick member.
24. Odd median, integer even median, and both half-even parity cases.
25. Equal High `SWEPT`, `BROKEN`, and exact-boundary non-consumption.
26. Mirrored Equal Low lifecycle cases.
27. `BROKEN` precedence and terminal-state rejection of later transitions.
28. Stable lineage ID and changing immutable snapshot ID.
29. Repeatability across identical runs.
30. Prefix invariance after appended future swings and observations.
31. Scaling relationships expressed through already-normalized integer ticks.
32. Public API and frozen-dataclass enforcement.
33. Proof that the module has no pandas, v1 SMC, I/O, network, configuration,
   registration, execution, or integration dependency.

The optional JSON fixture is not justified by this matrix and must remain absent
unless a later preflight demonstrates that inline fixtures are insufficient.
Fixtures must contain no private market data, candidate OOS values, accounts,
credentials, copied evidence, or outcome-derived parameters.

## 15. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py` or `smc/__init__.py`,
- raw swing detection or importing current `smc/market_structure.py`,
- pandas or external runtime dependencies,
- Dealing Range, liquidity-map, Premium or Discount, FVG, Order Block,
  Mitigation Block, Breaker Block, Inducement, kill-zone, or Volume Profile code,
- runtime feature flags, CLI, runner, context adapter, or diagnostic trace wiring,
- current SMC, CRT, Order Flow, DecisionContext, or confidence integration,
- action, allowed-status, risk, sizing, stop, target, entry, exit, balance, PnL,
  paper, broker, live, MT5, Sierra live, CME live, or external-API changes,
- tuning, optimization, favorable reruns, or use of saved OOS outcomes,
- private data, generated reports, external evidence, or Fibonacci analysis, and
- staging, committing, or pushing the later implementation without separate
  gates.

Any forbidden dependency is a stop condition and does not authorize a workaround.

## 16. Mandatory Pre-Implementation Gates

Before any later Python or test edit:

1. independently audit this record,
2. checkpoint this documentation record separately from code,
3. confirm this record on local and live `main`,
4. confirm a clean worktree and matching `HEAD = origin/main`,
5. run and record the full regression baseline,
6. verify all reserved targets are absent,
7. confirm inline fixtures remain sufficient or explicitly review the optional
   fixture path,
8. perform a read-only implementation preflight against the exact API,
   invariants, test matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only that implementation task.

Passing this documentation decision is insufficient to begin coding.

## 17. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved path collides unexpectedly,
- any additional path or package export appears necessary,
- the existing shared-primitives API appears insufficient or requires amendment,
- a raw swing detector or v1 adapter appears necessary,
- side identity, half-even median, assignment, reuse, or lifecycle behavior
  cannot follow this record exactly,
- a private, candidate, performance, generated, or external fixture appears
  necessary,
- deterministic identity or prefix invariance cannot be demonstrated,
- an existing public interface, default output, or execution path changes,
- focused tests or the full regression suite fail,
- unrelated staged, unstaged, ignored-generated, or untracked files appear, or
- integration appears necessary to test the standalone detector.

A stop condition freezes the task. It does not authorize scope expansion,
fallback semantics, silent coercion, or an implementation shortcut.

## 18. Completion, Rollback, and Promotion Gates

Later implementation completion requires:

- independent review of every changed line,
- exact reserved-path reconciliation,
- the complete inline unit-test matrix passing,
- the full regression suite passing,
- deterministic ID, half-even, lifecycle, and prefix-invariance evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed Equal Liquidity checkpoint record, and
- separate staging, commit, and push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and a clean-scope
audit. Existing v1 and shared-primitives files remain intact.

Successful implementation would prove only deterministic standalone detector
conformance. It would not prove trading edge, OOS improvement, strategy value,
paper readiness, live readiness, or approval for the next module.

## 19. Global Freeze and Next-Phase Boundary

The global code freeze remains active. This decision reserves one possible
future Equal High and Equal Low task only. It does not authorize Dealing Range,
Internal or External liquidity mapping, Premium or Discount, or any later phase.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 20. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=EQUAL_HIGH_EQUAL_LOW_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `OPERATIONAL_FREEZE_LIFT_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `TEST_CHANGES_AUTHORIZED=False`
- `FIXTURE_CHANGES_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
- `PAPER_PROGRESSION_REMAINS_BLOCKED=True`
- `LIVE_PROGRESSION_REMAINS_BLOCKED=True`

The next permissible action is an independent final audit of this one decision
record. A passing audit may authorize staging of this documentation file only.
