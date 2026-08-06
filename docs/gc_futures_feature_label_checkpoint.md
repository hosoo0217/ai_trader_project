# GC Futures Phase A Feature/Label Builder Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `GC-FUTURES-PHASE-A-FEATURE-LABEL-CHECKPOINT-2026-08-06`.
- Formal decision commit:
  `9a989e612c95bb7d69540704e76ecd15ddeabf46`.
- Formal decision record SHA-256:
  `7C162FBC56044C44E86D646BC41CFA84B7501FD063AE986EA4ADCC8850FB3E2D`.
- Builder version: `GC-FEATURE-LABEL-V1`.
- Feature schema: `GC_AI_FEATURE_SCHEMA_V1`.
- Label schema: `GC_AI_LABEL_SCHEMA_V1`.
- Fixed label horizon: `12` closed five-minute bars.
- Task classification: bounded offline research feature/label implementation.
- Training status: `NOT_STARTED`.
- OOS opening status: `NOT_AUTHORIZED`.
- Strategy, execution, and integration status: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three paths are in scope:

- `analysis/gc_feature_label_builder.py`
- `tests/test_gc_feature_label_builder.py`
- `docs/gc_futures_feature_label_checkpoint.md`

No external fixture, market-data, calendar, holiday, timezone, model, feature
store, label store, dataset, or generated artifact was created. No existing
dataset builder, detector, shared primitive, package export, configuration,
strategy, risk, execution, trace, importer, runtime, or integration file was
changed.

The pre-existing untracked files
`docs/gc_futures_real_data_input_binding_change_proposal.md` and
`docs/smc_v2_diagnostic_context_integration_change_proposal.md` remain outside
this task and were not edited, staged, or promoted.

## 3. Test-First Evidence

The first focused run failed during collection because
`analysis.gc_feature_label_builder` did not exist. The test suite was therefore
RED before implementation. The bounded source was then implemented and every
subsequent finding was corrected within the exact three-path scope.

The correction evidence includes:

- canonical Dealing Range EVENT and SNAPSHOT identity recomputation using the
  dependency's exact required/forbidden schema;
- acceptance of an external target's actual immutable source kind rather than
  rewriting it as a range boundary;
- deterministic identity canonicalization for nested mappings;
- signed, direction-aware range and FVG midpoint offsets without invalidating
  otherwise canonical evidence;
- Decimal-context isolation at the public builder boundary;
- future-bar changes leaving the 17 feature values unchanged while dataset
  provenance remains identity-bearing;
- per-effective-group static validation so a determinably later malformed group
  returns `INVALID` without erasing strictly prior promoted evidence.
- byte-exact reconciliation of detached external/internal classification
  references against the immutable classifications carried by the Liquidity
  Map snapshot;
- ACTIVE Dealing Range transition membership, transition identity, state-chain,
  and creation first-known moment reconciliation;
- strict pre-sweep eligibility for the Liquidity Map and at-or-before-sweep
  eligibility for the ACTIVE range;
- Liquidity Map `MAP`, `SNAPSHOT`, and supplied `RECLASSIFICATION` identity and
  membership reconciliation;
- Equal Liquidity first-known provenance, lifecycle-chain, terminal sweep
  moment, side, boundary, and source-index reconciliation;
- Fair Value Gap transition/snapshot one-to-one causal mirroring through the
  confirmation moment;
- independently determinable malformed dataset evidence outranking missing
  calendar or candidate collections;
- hard rejection of any dataset manifest or segment exposing sealed
  `OOS_HOLDOUT` evidence before reading or producing rows.
- exact separation of otherwise well-formed incomplete label coverage from
  malformed evidence: missing, duplicate, timestamp-substituted, non-closed,
  and discontinuous horizon observations yield `INCOMPLETE` with no later
  rescue;
- calendar-bound horizon completeness, including early-close truncation and
  unavailable trade-date coverage, without rejecting an otherwise canonical
  early-close confirmation context;
- mirrored bullish/bearish target equality, invalidation, pool-boundary
  equality, first-event precedence, and same-bar collision behavior;
- complete-group strictly-later prefix preservation, same-effective opposing
  atomicity, reorder/version-mutation rejection, and deterministic
  multi-candidate output independent of identity hash order;
- exhaustive public signature/default, frozen dataclass, enum, constant,
  export, required/forbidden identity-field, sensitivity, malformed-hash, and
  exception-containment coverage.

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_feature_label_builder.py`
- `56 passed in 1.45s`
- exact logical cases: `48`
- additional parameterized executions: `8`

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`
- `2135 passed in 12.41s`
- pre-task full-regression baseline: `2079 passed`
- net new collected executions: `56`

## 4. Exact Public Surface

The module exports exactly these `14` names:

- `GC_FEATURE_LABEL_VERSION`
- `GC_AI_FEATURE_SCHEMA_ID`
- `GC_AI_LABEL_SCHEMA_ID`
- `GC_AI_LABEL_HORIZON_BARS`
- `GCLabelOutcome`
- `GCFeatureLabelIdentityKind`
- `GCFeatureLabelConfig`
- `GCFeatureLabelCandidateEvidence`
- `GCFeatureRow`
- `GCResearchLabel`
- `GCFeatureLabelManifest`
- `GCFeatureLabelResult`
- `make_gc_feature_label_id`
- `build_gc_feature_labels`

Both public functions are exact keyword-only APIs. Every public dataclass is
frozen and has the locked field order, annotations, and defaults. The module
does not expose filesystem, network, model-provider, training, strategy,
signal, confidence, order, risk, position, entry, exit, or PnL authority.

## 5. Immutable Input Boundary

The builder accepts only caller-supplied immutable evidence:

- canonical `GCDatasetBuildConfig` and `GCDatasetBuildResult`;
- version-consistent `KillZoneCalendarEntry` tuples;
- `GCFeatureLabelCandidateEvidence` binding canonical Inducement, Inducement
  snapshot, active external Dealing Range, Liquidity Map snapshot and exact
  classifications, swept internal Equal Liquidity pool, confirmed Structure
  Event, canonical FVG with complete transition/snapshot history, verified New
  York AM context/snapshot, and the exact canonical confirmation bar.

The implementation recomputes every available public dependency identity. It
does not recompute detector outputs, mutate them, enrich them, repair missing
history, silently sort caller tuples, or infer unavailable foreign identities.
Missing top-level context is `UNKNOWN` only after every independently
determinable supplied counterpart has passed fail-closed validation. This
includes dataset segment identities, counts, conservation, histories, and the
sealed-OOS boundary even when the calendar or candidate collection is absent.

## 6. Exact Feature Contract

Each `GCFeatureRow.feature_values` tuple contains exactly `17` values in this
order:

1. candidate direction;
2. structure-event type;
3. confirmation offset bars;
4. pool side;
5. pool width ticks;
6. pool member count;
7. sweep penetration ticks;
8. reclaim boundary distance ticks;
9. external-target source kind;
10. external-target distance ticks;
11. range direction;
12. range width ticks;
13. direction-aware range midpoint offset in half-tick units;
14. FVG width ticks;
15. direction-aware FVG midpoint offset in half-tick units;
16. minutes from New York AM start;
17. minutes to New York AM end.

All feature values are available at the immutable confirmation moment. Outcome
bars, label result, later range, later FVG, later liquidity, trade outcome,
entry, exit, risk, PnL, and OOS evidence are absent from the feature tuple.
Changing only post-confirmation bars cannot change these feature values.

## 7. Exact Label Contract

The label begins strictly after the confirmation bar and examines exactly the
next `12` closed, contiguous five-minute bars. The immutable thresholds are the
selected external-target boundary and the adverse one-tick close-through of
the swept internal pool.

Exact outcomes are:

- `TARGET_FIRST`;
- `INVALIDATION_FIRST`;
- `TIMEOUT`;
- `SAME_BAR_AMBIGUOUS`;
- `INCOMPLETE`;
- `INVALID`.

Target equality is reached by wick. Invalidation requires close-through at the
locked adverse one-tick threshold; pool-boundary equality alone does not
invalidate. A bar reaching both thresholds is
`SAME_BAR_AMBIGUOUS`, never silently resolved. A truncated or non-contiguous
horizon is `INCOMPLETE` and makes the result `UNKNOWN`.

## 8. Deterministic Identity Schemas

`make_gc_feature_label_id()` implements exhaustive required/forbidden schemas:

- `FEATURE_ROW` binds normalized instrument/timeframe, exact tick size,
  timezone-data and calendar versions, dataset/candidate/contract/trade-date
  provenance, ordered source and lineage histories, ordered detector versions,
  feature schema, exact 17-value tuple, and confirmation moment;
- `LABEL` binds the same common provenance plus label schema, fixed horizon,
  target/invalidation ticks, outcome, first-outcome moment when applicable, and
  horizon-end moment when applicable;
- `MANIFEST` binds the common provenance, both schemas, fixed horizon, and
  ordered unique paired feature-row and label histories.

Unknown kinds, missing required fields, supplied forbidden fields, malformed
hashes, wrong history order, non-UTC-equivalent timestamps, boolean integers,
non-finite Decimal values, and contradictory outcome moments raise only
`TypeError` or `ValueError` from the identity builder.

## 9. Atomicity, Status, and Prefix Invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Candidates are processed in caller-supplied nondecreasing confirmation order.
Same-effective candidates form one atomic group. Exact duplicates are
deterministic; valid opposing directions in one group are `AMBIGUOUS`; malformed
evidence is `INVALID` and outranks ambiguity. A failing group promotes nothing
from that group or any later group, while strictly prior complete evidence is
preserved byte-for-byte.

Complete-prefix invariance applies only at a completed effective-group boundary
with strictly later appended evidence. Same-effective appends, historical
insertion, repair, reorder, dataset identity mutation, calendar mutation, and
timezone-data mutation are not eligible prefix extensions.

## 10. Exact 48-Case Matrix Reconciliation

The suite contains exactly one sequentially named function for each logical
case `01` through `48`. Parameterization expands malformed-field, manifest,
outcome, horizon, calendar-boundary, lifecycle, and identity-schema coverage to
`56` collected tests without changing the logical-case count.

The matrix covers missing/empty context, bullish/bearish mirrors, verified New
York AM bounds, exact first-known reconciliation, malformed immutable inputs,
manifest drift, sealed-OOS rejection, no-silent-sort, side/scope roles,
detached-reference rejection, Dealing Range/Liquidity Map/Equal Liquidity/FVG
history reconciliation, event/FVG positional suffix, opaque displacement
binding, duplicates/opposition, every feature geometry, Decimal and DST
determinism, no-look-ahead, all six label outcomes, chronological cutoff,
prefix invariance, all three identity schemas, exact public signatures, frozen
dataclasses, constants, enums, exports, reason tokens, and forbidden integration
surface.

## 11. Data, Training, and OOS Stop State

This implementation consumes no private Sierra file and creates no feature or
label dataset on disk. It does not authorize the 2024-2025 dataset promotion,
model fitting, hyperparameter search, checkpoint loading, OOS inspection,
strategy selection, paper trading, or live trading.

The builder is deterministic offline research infrastructure only. A later
separately reviewed task must bind an accepted immutable dataset and calendar
artifact before any real-data feature/label build. A separate promotion gate is
required before training, and OOS remains sealed until the precommitted
development protocol is complete.

## 12. Artifact Evidence

- `analysis/gc_feature_label_builder.py`
  - SHA-256:
    `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`
  - bytes: `71477`
  - physical lines: `1287`
- `tests/test_gc_feature_label_builder.py`
  - SHA-256:
    `EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B`
  - bytes: `81401`
  - physical lines: `2011`
- `docs/gc_futures_feature_label_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes: `13874`
  - physical lines: `309`

All three artifacts must be UTF-8 without BOM, use LF line endings, contain no
tabs or trailing whitespace, and pass exact-scope diff checking before audit.

## 13. Promotion, Rollback, and Stop Conditions

This checkpoint does not authorize staging, commit, push, integration,
real-data feature/label construction, training, OOS opening, strategy changes,
paper trading, or live progression. Promotion requires a fresh independent
exact-scope code/test/checkpoint audit and explicit staging authorization.

Before commit, rollback is removal of exactly the three new task artifacts and
requires explicit authorization. After a future commit, rollback must use a
bounded revert rather than history rewriting.

Stop immediately on dependency/API drift, scope expansion, dataset/calendar or
tzdata mismatch, source or identity failure, event/FVG causal mismatch,
look-ahead evidence, cross-partition contamination, exception leakage,
nondeterminism, exact 48-case mismatch, focused/full regression failure, or any
request to grant model, strategy, execution, risk, order, or PnL authority.

The global code freeze remains active outside the exact three-path bounded
implementation scope.
