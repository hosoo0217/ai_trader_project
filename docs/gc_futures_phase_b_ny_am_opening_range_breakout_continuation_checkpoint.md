# GC Futures Phase B NY AM Opening Range Breakout Continuation Checkpoint

## 1. Checkpoint identity

- Checkpoint ID:
  `GC-PHASE-B-NY-AM-OPENING-RANGE-BREAKOUT-CONTINUATION-CHECKPOINT-2026-08-16`.
- Governing proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_feasibility_change_proposal.md`.
- Governing proposal commit:
  `3e4bff17a03131f6ed02c923a0e55e8d49326875`.
- Governing proposal SHA-256:
  `75A049329783501E779AFBA1F198A7BA2BA7C25C7986C601F9D64A7A5BDCA291`.
- Implementation version: `GC-NY-AM-OPENING-RANGE-BREAKOUT-V1`.
- Task classification: development-only, deterministic occurrence and
  structural-outcome feasibility diagnostics.
- Independent semantic, structural, scope, and regression audit: `PASS`.
- Private-data execution, feature/label production, model fitting, training,
  OOS access, PnL analysis, strategy promotion, and integration:
  `NOT_PERFORMED` and `NOT_AUTHORIZED`.
- Strategy, risk, execution, persistence, network, and trading authority:
  `NOT_GRANTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact authorized scope

Exactly these three paths are in scope:

- `analysis/gc_ny_am_opening_range_breakout.py`;
- `tests/test_gc_ny_am_opening_range_breakout.py`;
- `docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_checkpoint.md`.

No external fixture, private artifact, dataset, calendar, candidate table,
feature, label, model, training output, package export, configuration, runtime,
trace, strategy, risk, execution, or integration file was created or changed.
The three pre-existing unrelated untracked proposal documents remain outside
scope and untouched.

## 3. Locked dependency evidence

The accepted dependencies remain byte-exact:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

The analyzer directly imports only the proposal-allowed immutable dataset,
calendar, Kill-zone, direction, and primitive-status contracts. It imports no
filesystem, network, subprocess, model, training, strategy, risk, execution,
storage, trace, order-flow, or runtime-integration authority.

## 4. Test-first and independent-correction evidence

The exact 48 numbered public cases were created before the source module. The
first focused collection failed with
`ModuleNotFoundError: analysis.gc_ny_am_opening_range_breakout`, establishing
the RED gate before implementation.

The first GREEN implementation passed all 48 cases. Independent audit then
strengthened the existing numbered cases without changing the logical-case
count. The strengthened tests exposed and locked these corrections:

- candidate invalidation geometry is the exact direction mirror of target
  geometry and cannot accept an internally inconsistent width;
- the public export surface is the exact accepted tuple and internal reason or
  count constants are not public exports;
- complete no-breakout evidence returns `NONE`, while a calendar-ineligible
  requested session is reported separately;
- a missing top-level dependency cannot hide independently determinable
  malformed observations or Kill-zone evidence;
- later malformed observation or Kill-zone evidence stops atomically while
  preserving byte-exact strictly prior promoted evidence;
- supplied Kill-zone contexts and snapshots have canonical identities,
  one-to-one mirrored moments, and exact-prefix reference reconciliation;
- candidate and its twelve-bar outcome horizon remain within the same segment;
- candidate-horizon indices and normalized timestamps are independently
  consecutive and strictly increasing;
- dataset bar indices/timestamps and supplied observation indices/open/close
  timestamps are independently strictly increasing rather than accepted by a
  composite-key shortcut; and
- missing split-session and missing Kill-zone calendar coverage report only
  their own exact reason token.

Every correction remained inside the locked public API, identity payload,
status, chronology, and exact three-path boundary.

## 5. Immutable input and no-look-ahead boundary

The analyzer accepts only caller-supplied canonical `GCDatasetBuildConfig`,
`GCDatasetBuildResult`, split-session calendar entries, Kill-zone calendar
entries, Kill-zone result, requested trade dates, and immutable fully closed
five-minute observations. It performs no file discovery or detector rerun.

Dataset identity, manifest, development partition, GC/5M scope,
`Asia/Tokyo` source timezone, `America/New_York` exchange timezone, runtime
tzdata version, exact `Decimal("0.1")` tick size, zero OOS contact, segment/bar
chronology, calendar versions, calendar digests, observation-to-bar mapping,
and Kill-zone foreign identities fail closed. Evidence is visible only at its
normalized first-known effective moment. No outcome bar can participate in
formation, and no later bar can relabel an earlier incomplete prefix.

## 6. Calendar and session semantics

Each requested trade date requires both authoritative split-session and
Kill-zone calendar coverage. Missing streams produce their exact independent
`UNKNOWN` reason. Malformed, reordered, foreign-version, unrequested, or
contradictory calendar evidence is `INVALID`.

Only sessions whose two calendar streams cover the complete possible analysis
window are eligible. A valid but ineligible date produces deterministic
`SESSION_INELIGIBLE` evidence without candidate or outcome promotion. Calendar
streams are never silently sorted, repaired, inferred, or enriched.

## 7. Opening range and candidate semantics

The opening range uses exactly six closed source bars whose local opens are
`07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and `07:25` in
`America/New_York`. It becomes first known at `07:30`. Its low, high, positive
width, ordered source observation IDs, indices, and timestamps are immutable.

The candidate window is start-inclusive at `07:30` and end-exclusive at
`09:00`. The earliest exact one-tick close beyond the range selects the
direction. Bullish target/invalidation are `range_high + width` and
`range_high - width`; bearish geometry is the exact mirror around
`range_low`. A formation bar that also reaches an outcome boundary is rejected
as `FORMATION_OUTCOME_COLLISION`. Exact duplicates collapse; distinct valid
same-effective interpretations are `AMBIGUOUS` rather than hash-selected.

## 8. Outcome semantics

Only the next twelve strictly later, consecutive closed bars in the same
segment form the outcome horizon. Extension-first and close-through
invalidation-first are directional mirrors. If both boundaries occur in the
same bar, the structural result is `SAME_BAR_AMBIGUOUS`; if neither occurs in
twelve bars, it is `TIMEOUT`; fewer than twelve bars remain `INCOMPLETE` with
no outcome promotion.

These are immutable structural observations only. They are not entries,
exits, trades, recommendations, confidence, risk, reward, return, slippage,
commission, or PnL labels.

## 9. Exact public API and immutable types

The module exports exactly:

- `GC_NY_AM_OPENING_RANGE_BREAKOUT_VERSION`;
- `GCNYAMIdentityKind`;
- `GCNYAMOutcomeType`;
- `GCNYAMOpeningRangeObservation`;
- `GCNYAMOpeningRange`;
- `GCNYAMOpeningRangeCandidate`;
- `GCNYAMOpeningRangeOutcome`;
- `GCNYAMOpeningRangeManifest`;
- `GCNYAMOpeningRangeResult`;
- `make_gc_ny_am_opening_range_breakout_id`;
- `analyze_gc_ny_am_opening_range_breakout`.

Both public functions use the exact locked keyword-only parameter names and
defaults. All six public dataclasses are frozen with exact fields, annotations,
defaults, and immutable tuple members. Enum values, version, signatures,
dataclass contracts, and exports are asserted directly in Cases 42--43.

## 10. Deterministic identities and ordering

All IDs are lowercase SHA-256 over canonical typed JSON. The public builder
enforces exhaustive common and kind-specific required/forbidden schemas for
`OBSERVATION`, `OPENING_RANGE`, `CANDIDATE`, `OUTCOME`, and `MANIFEST`.
It validates hash shape, UTC normalization, tuple shape and uniqueness,
direction-specific geometry, effective moments, outcome terminality, ordered
history, counts, reasons, and nested values without leaking dependency-library
exceptions.

Ordering follows accepted dataset order, then bar index and normalized
timestamp. Direction or hash lexical order is never a chronology tie-break.
Equivalent UTC representations and repeat execution produce identical IDs and
object-equal results.

## 11. Status, atomicity, and prefix invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Malformed or contradictory evidence promotes nothing from its failing group
or any later group. Strictly prior complete evidence is byte-exact immutable.
A pending or incomplete group cannot promote a range, candidate, or outcome.
Strictly later complete-session append preserves the complete earlier prefix;
same-effective append, historical insertion, repair, reorder, calendar-version
mutation, or partial-session append is not eligible for prefix comparison.

## 12. Exact 48-case matrix reconciliation

`tests/test_gc_ny_am_opening_range_breakout.py` contains exact sequential
logical Cases 1 through 48 and exactly 48 collected executions. The matrix
covers all input bindings, missing/malformed precedence, OOS rejection,
observation and calendar contracts, session eligibility, exact six-bar range,
candidate boundaries and selection, mirrored outcome behavior, collision,
incomplete horizon, final status precedence, atomic cutoff, prior-evidence
preservation, exhaustive identity schemas and sensitivities, nested exception
containment, exact keyword-only API/defaults, frozen dataclasses, enums,
exports, repeatability, UTC equivalence, prefix invariance, exact scope,
forbidden imports, rollback, and no-private-run/training/integration boundary.

Logical case count: `48`.

## 13. Focused and full regression evidence

Commands were executed with pytest cache disabled:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_ny_am_opening_range_breakout.py
48 passed in 5.76s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2394 passed in 23.81s
```

Repository-root discovery was intentionally not used as the final public
regression command because protected private-data directories deny collection
access. The explicit public `tests` suite is complete and PASS; no ACL was
changed and no private file was accessed or mutated.

## 14. Artifact evidence

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `analysis/gc_ny_am_opening_range_breakout.py` | `67,205` | `1,277` | `6515964B6F8A0C76CD48D9F8E6071947600FA939DC6FAFBD85C000C9A2B478F8` |
| `tests/test_gc_ny_am_opening_range_breakout.py` | `47,302` | `971` | `654ED7080B0F07FF16FAE38366C0C2274EEC24C6EA3C20368D6D831EAE606BD0` |

The checkpoint itself is intentionally excluded from its own self-referential
hash table. Its final hash, byte count, and line count must be captured by the
staging and commit audits.

## 15. Promotion, rollback, and STOP conditions

This checkpoint promotes only the bounded implementation to a local commit
after exact-scope staging, cached-content audit, hash verification, diff-check,
and commit preflight. It does not promote a hypothesis, dataset, candidate
table, experiment, feature/label build, model, strategy, or trade.

Before commit, rollback is deletion of exactly the three reserved paths. After
commit, rollback is a bounded revert; history rewriting is forbidden. Preserve
all RED/GREEN, regression, and audit evidence.

STOP on dependency or proposal drift, test failure, formatting error, scope
drift, ambiguous public contract, unavailable runtime tzdata, private-data or
OOS access, feature/label or PnL construction, model/training work, integration,
execution authority, or remote publication without separate exact approval.
The next push is explicitly not authorized by this implementation task.
