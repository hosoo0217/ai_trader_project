# GC Futures Phase B NY AM Opening Range Sweep/Reclaim Reversion Checkpoint

## 1. Checkpoint identity

- Checkpoint ID:
  `GC-PHASE-B-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-CHECKPOINT-2026-08-16`.
- Governing proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_change_proposal.md`.
- Governing proposal commit:
  `83c7309bb532ca29bbfd2c3d27fb484a1dd53c45`.
- Governing proposal SHA-256:
  `EEC03B71A19FFF8EDC786FB1D20210F98F40FCB9314BCEE705FA0C6B93FDE2AD`.
- Implementation version:
  `GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1`.
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

- `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py`;
- `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py`;
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md`.

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

The exact 48 numbered public logical cases were written and maintained as the
acceptance boundary for the source implementation. Parameterization expands
them to 59 focused collected executions without changing the logical-case
count.

Independent implementation and test audit locked the following corrections
inside the accepted contract:

- all five public identity kinds use their uppercase kind prefix plus exact
  lowercase SHA-256, and foreign own-type IDs are validated by kind as well as
  hash shape;
- ambiguous GC contract aliases, malformed OHLC, nonclosed bars, invalid
  timestamps, non-tuples, forked same-effective evidence, and reordered
  evidence fail closed;
- exact duplicate observations collapse only after complete equality;
- missing top-level evidence cannot hide independently determinable malformed
  observation, Kill-zone context, or Kill-zone snapshot evidence;
- a determinably later malformed observation preserves only byte-exact
  strictly prior promoted range, candidate, and outcome evidence;
- five truly truncated opening-range bars produce `UNKNOWN`, while later
  evidence after an incomplete source window makes the group `INVALID`;
- range and candidate Decimal integer/half-tick geometry is independent of the
  ambient Decimal context, including signed zero and arbitrary magnitudes;
- test fixtures distinguish midpoint equality, outside-close nonqualification,
  delayed-reclaim prohibition, and ordered outcome history; and
- Case 42 exhaustively asserts every public dataclass field, annotation,
  default, frozen state, enum value, exact version, ordered export, and exact
  keyword-only API/default contract.

No correction broadened the public API, identity payload, chronology, status,
or exact three-path boundary.

## 5. Immutable input and no-look-ahead boundary

The analyzer accepts only caller-supplied canonical `GCDatasetBuildConfig`,
`GCDatasetBuildResult`, split-session calendar entries, Kill-zone calendar
entries, Kill-zone result, requested trade dates, and immutable fully closed
five-minute observations. It performs no file discovery or detector rerun.

Dataset identity, manifest, development partition, `GC`/`5M` scope,
`Asia/Tokyo` source timezone, `America/New_York` exchange timezone, runtime
tzdata version, exact `Decimal("0.1")` tick size, zero OOS contact, segment/bar
chronology, calendar versions, calendar digests, observation-to-bar mapping,
and Kill-zone foreign identities fail closed. Evidence is visible only at its
normalized first-known effective moment. No outcome bar can participate in
formation, and no later bar can relabel an earlier nonqualifying sweep.

## 6. Calendar and session semantics

Each requested trade date requires authoritative split-session and Kill-zone
calendar coverage. Missing streams produce their exact independent `UNKNOWN`
reason. Malformed, reordered, foreign-version, unrequested, or contradictory
calendar evidence is `INVALID`.

Only a complete eligible session whose evidence covers the opening range and
candidate/outcome horizon is processed. Calendar streams are never silently
sorted, repaired, inferred, or enriched.

## 7. Opening range and candidate semantics

The opening range uses exactly six closed source bars whose local opens are
`07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and `07:25` in
`America/New_York`. It becomes first known at `07:30`. Its low, high, positive
width, exact Decimal midpoint, ordered source IDs, indices, and timestamps are
immutable.

The candidate window is start-inclusive at `07:30` and end-exclusive at
`09:00`. A bearish candidate requires an upper-boundary sweep of at least one
tick and a same-bar close in the range's upper half. A bullish candidate is the
exact lower-boundary mirror. Midpoint equality, an outside close, a wick-only
excursion, and a delayed reclaim are noncandidates. A bar sweeping both
boundaries is `AMBIGUOUS_SWEEP_RECLAIM`; otherwise the earliest qualifying bar
wins and later bars are outcome-only evidence.

## 8. Outcome semantics

The formation bar is excluded. Only the next twelve strictly later,
consecutive, same-lineage closed observations form the outcome horizon.
Direction-mirrored midpoint target and close-through invalidation are exact.
The earliest terminal bar wins; simultaneous target and invalidation is
`SAME_BAR_AMBIGUOUS`; twelve bars with neither event is `TIMEOUT`; a truncated
horizon is `UNKNOWN` with no public outcome promotion.

These outputs are immutable structural evidence only. They are not entries,
exits, trades, recommendations, confidence, risk, reward, return, slippage,
commission, or PnL labels.

## 9. Exact public API and immutable types

The module exports exactly:

- `GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION`;
- `GCNYAMSweepReclaimIdentityKind`;
- `GCNYAMSweepReclaimOutcomeType`;
- `GCNYAMSweepReclaimObservation`;
- `GCNYAMSweepReclaimOpeningRange`;
- `GCNYAMSweepReclaimCandidate`;
- `GCNYAMSweepReclaimOutcome`;
- `GCNYAMSweepReclaimManifest`;
- `GCNYAMSweepReclaimResult`;
- `make_gc_ny_am_sweep_reclaim_id`; and
- `analyze_gc_ny_am_opening_range_sweep_reclaim_reversion`.

Both public functions use the exact locked keyword-only parameter names and
defaults. All six public dataclasses are frozen with exact fields, annotations,
defaults, and immutable tuple members. Enum values, version, signatures,
dataclass contracts, and exports are asserted directly in Case 42.

## 10. Deterministic identities and ordering

All IDs are uppercase kind prefix plus lowercase SHA-256 over canonical typed
JSON. The public builder enforces exhaustive common and kind-specific
required/forbidden schemas for `OBSERVATION`, `OPENING_RANGE`, `CANDIDATE`,
`OUTCOME`, and `MANIFEST`. It validates hash and kind shape, UTC normalization,
tuple shape and uniqueness, exact geometry, effective moments, outcome
terminality, ordered history, counts, reasons, and nested values without
leaking dependency-library exceptions.

Ordering follows requested trade date, canonical segment order, observation
index, then normalized bar-open timestamp. Direction or hash lexical order is
never a chronology tie-break. Equivalent UTC representations and repeat
execution produce identical IDs and object-equal results.

## 11. Status, atomicity, and prefix invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Malformed or contradictory evidence promotes nothing from its failing group
or any later group. Strictly prior complete evidence is byte-exact immutable.
A pending group cannot promote a candidate or outcome. Strictly later
complete-group append preserves the complete earlier prefix; same-effective
append, historical insertion, repair, reorder, calendar-version mutation,
dataset mutation, or partial history is prefix-ineligible.

## 12. Exact 48-case matrix reconciliation

`tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` contains exact
sequential logical Cases 1 through 48. Parameterization yields 59 focused
collected executions. The matrix covers input binding, missing/malformed
precedence, OOS rejection, immutable observation/calendar/context contracts,
exact six-bar range, candidate boundaries and selection, mirrored geometry,
formation exclusion, twelve-bar outcomes, ambiguity, incomplete horizons,
final status precedence, atomic cutoff, immutable prior evidence, exhaustive
identity schemas, ordered history, malformed nested values, exact
keyword-only API/defaults, all frozen dataclass contracts, enums, exports,
repeatability, UTC equivalence, prefix invariance, promotion thresholds,
three-path scope, rollback, and forbidden private-run/training/integration
authority.

Logical case count: `48`; focused collected executions: `59`.

## 13. Focused and full regression evidence

Commands were executed with pytest cache disabled:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py
59 passed in 7.28s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 29.11s
```

Repository-root discovery is not the accepted regression surface because
ACL-protected private-data directories deny collection access. The explicit
public `tests` suite is complete and PASS; no ACL was changed and no private
file was accessed or mutated.

## 14. Artifact evidence

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `75,850` | `1,459` | `3F9E64C277A1F00453585EFD66371B81D10DDA14E73FDAFE111AD1A213CAC477` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `54,927` | `1,007` | `7F49D1015CC0F8D2DD469E428DB2A9D78FF3D95933FE4540B3FE8502ED43BDA9` |

The checkpoint is intentionally excluded from its own self-referential hash
table. Its final hash, byte count, and line count must be captured by staging
and commit audits.

## 15. Promotion, rollback, and STOP conditions

This checkpoint promotes only the bounded implementation to a local commit
after exact-scope staging, cached-content audit, hash verification, diff-check,
and commit preflight. It does not promote a hypothesis, dataset, candidate
table, experiment, feature/label build, model, strategy, or trade.

Before commit, rollback is deletion of exactly the three reserved paths. After
commit, rollback is a bounded revert; history rewriting is forbidden. Preserve
all test, regression, and audit evidence.

STOP on dependency or proposal drift, test failure, formatting error, scope
drift, ambiguous public contract, unavailable runtime tzdata, private-data or
OOS access, feature/label or PnL construction, model/training work,
integration, execution authority, or remote publication without separate
exact approval. The next push is explicitly not authorized by this
implementation task.
