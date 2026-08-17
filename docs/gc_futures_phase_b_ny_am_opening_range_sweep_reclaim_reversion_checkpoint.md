# GC Futures Phase B NY AM Opening Range Sweep/Reclaim Reversion Checkpoint

## 1. Checkpoint identity

- Checkpoint ID:
  `GC-PHASE-B-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-CHECKPOINT-2026-08-17`.
- Governing proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md`.
- Governing proposal commit:
  `1031c330713193af4f7c7fbcea39c969dc0dbd17`.
- Governing proposal SHA-256:
  `FEDBE60FFC5E984692EEDA41BAB5C131377E7578EC7E9EB56063D35B0A80883D`.
- Governing terminal-alignment correction proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_complete_kill_zone_alignment_correction_proposal.md`.
- Governing terminal-alignment correction commit:
  `acbe282934fa72fd22dec920c1a8bcf260fd5d2b`.
- Governing terminal-alignment correction SHA-256:
  `BEDB0596321A8A00D3B093E1BBF87A9A3437E4B49AF8A5978375E49246FAB772`.
- Governing attested-no-trade coverage correction proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_attested_no_trade_coverage_correction_proposal.md`.
- Governing attested-no-trade coverage correction commit:
  `c3f8d5b7c21f8cc5e1375e6468805c06b2cc6064`.
- Governing attested-no-trade coverage correction SHA-256:
  `6A1DE55F8597A17512B55D3F5E89186455C01CFEEFEA36742C6AA91114F6F9EA`.
- Implementation version:
  `GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V2`.
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

- canonical dataset bars remain complete input evidence, while the expected
  observation stream is exactly the intersection of bar-open and fully closed
  bar-close membership in `[07:00, 10:00) America/New_York`, yielding the
  five-minute bar-open projection `[07:00, 09:55)`;
- valid pre-NY-AM and post-NY-AM dataset bars require no observation, context,
  or snapshot and cannot be relabeled as `NEW_YORK_AM`;
- expected observations, contexts, and snapshots reconcile one-to-one in
  canonical dataset order, with `07:00` open included, `09:50` open / `09:55`
  close the final admissible member, and the canonical `09:55` open / `10:00`
  close bar retained in the dataset but excluded from Phase B observations;
- missing, extra, duplicate, reordered, or non-NY-AM projection members fail
  closed without rejecting the canonical non-NY-AM dataset bar itself;
- a complete synthetic dependency preserves native `VALID` and `NONE`
  statuses, while an incomplete retained projection is `UNKNOWN`, promotes no
  manifest, and preserves complete prior range/candidate/outcome bytes;
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

The terminal-alignment correction began with public failing tests. Before the
source fix, Cases 17, 45, and 46 rejected the correctly shortened projection:

```text
3 failed, 56 passed in 6.83s
```

The minimal source correction made expected membership require both canonical
bar-open and fully closed bar-close inclusion. It did not shift timestamps,
synthesize Kill-zone evidence, mutate the upstream detector, or remove the
terminal canonical dataset bar.

The attested-no-trade coverage correction also began with public failing
tests. Before the source fix, Cases 9, 11, 12, 39, 42, 43, 44, and 47 exposed
the former short-range collapse:

```text
7 failed, 52 passed
```

The minimal V2 correction validates canonical adjacent segment-gap lineage,
five-minute arithmetic, missing-member counts, manifest missing-bar counts,
and attested interval counts before classifying a qualified opening-range gap
as `NONE` with `ATTESTED_NO_TRADE_OPENING_RANGE`. Corrupted or contradictory
attestation remains `INVALID_OPENING_RANGE`; truly unavailable or truncated
coverage remains `INCOMPLETE_OPENING_RANGE`. A mixed complete plus attested
input preserves the complete group's byte-exact range, candidate, and outcome
evidence and retains the status earned by that complete group.

The final independent ordering audit found that the V2 implementation had
placed the new attested-no-trade funnel key after `COMPLETE_OPENING_RANGES` and
the new reason token after `INCOMPLETE_OPENING_RANGE`, contrary to the
governing proposal's exact insertion points. Public Cases 39, 41, and 43 were
locked first and reproduced the defect:

```text
3 failed, 56 passed in 7.05s
```

The minimal correction moves
`ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES` immediately after
`CALENDAR_ELIGIBLE_TRADE_DATES` and `ATTESTED_NO_TRADE_OPENING_RANGE`
immediately after `SESSION_INELIGIBLE`. Case 39 now distinguishes both reason
tokens in one public analyzer result, while Cases 41 and 43 lock exact manifest
funnel order for ordinary and attested inputs. No count, status, identity
field, version, or public API changed.

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
chronology, calendar versions, calendar digests, NY-AM observation-to-bar
projection,
and Kill-zone foreign identities fail closed. Evidence is visible only at its
normalized first-known effective moment. No outcome bar can participate in
formation, and no later bar can relabel an earlier nonqualifying sweep.

Every canonical bar is validated before projection. Exactly one observation,
one `NEW_YORK_AM` context, and one mirrored snapshot are expected only when both
the bar-open moment and fully closed bar-close moment are within
`[07:00, 10:00) America/New_York`. For canonical five-minute bars, this is the
exact bar-open intersection `[07:00, 09:55)`. The `09:55` open / `10:00` close
bar remains immutable dataset evidence but cannot enter Phase B observation,
formation, or outcome logic.

An absent opening-range member is never synthesized. V2 may classify the
group as an attested no-trade `NONE` only when the canonical dataset manifest
and immediately adjacent source segments prove every missing expected member
with exact same-lineage five-minute gap arithmetic. Failed proof falls through
to the locked `UNKNOWN` or `INVALID` boundary.

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

If canonical lineage proves that one or more of those six expected members
did not trade, the date increments
`ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES`, emits
`ATTESTED_NO_TRADE_OPENING_RANGE`, and promotes no opening range, candidate,
or outcome. This is a coverage classification, not a synthetic range.

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
collected executions. The corrected matrix covers full-session dataset input,
exact fully-closed NY-AM projection membership including terminal-bar
exclusion, one-to-one observation/context/snapshot reconciliation,
retained-prefix dependency rejection, native complete dependency statuses,
qualified versus corrupted attested-no-trade gaps, mixed complete plus
attested groups, and the immutable private-run boundary. It also covers
input binding, missing/malformed
precedence, OOS rejection, immutable observation/calendar/context contracts,
exact six-bar range, candidate boundaries and selection, mirrored geometry,
formation exclusion, twelve-bar outcomes, ambiguity, incomplete horizons,
final status precedence, atomic cutoff, immutable prior evidence, exhaustive
identity schemas, ordered history, malformed nested values, exact
keyword-only API/defaults, all frozen dataclass contracts, enums, exports,
repeatability, UTC equivalence, prefix invariance, three-path scope, rollback,
and forbidden private-run/training/integration authority.

Logical case count: `48`; focused collected executions: `59`.

## 13. Focused and full regression evidence

Commands were executed with pytest cache disabled:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py
59 passed in 7.13s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 23.77s
```

Repository-root discovery is not the accepted regression surface because
ACL-protected private-data directories deny collection access. The explicit
public `tests` suite is complete and PASS; no ACL was changed and no private
file was accessed or mutated.

## 14. Artifact evidence

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `84,232` | `1,648` | `75FFD671FE09FB3BF91D31658E3D990BAA0418578AD3EB503BC417ED4601AF28` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `82,397` | `1,537` | `578A2F0E733ADDE0698E6782621A89B6644C3AC4B66486EA3C205D10440DAF91` |

The checkpoint is intentionally excluded from its own self-referential hash
table. Its final hash, byte count, and line count must be captured by staging
and commit audits.

## 15. Promotion, rollback, and STOP conditions

This checkpoint promotes only the bounded implementation to a local commit
after exact-scope staging, cached-content audit, hash verification, diff-check,
and commit preflight. It does not promote a hypothesis, dataset, candidate
table, experiment, feature/label build, model, strategy, or trade.

The accepted immutable Kill-zone dependency covers all `133` canonical
segments, but the Phase B private run remains outside this implementation
authority. A refreshed documentation-only private-run proposal must first bind
the final committed implementation and dependency hashes; only a later exact
authorization may permit that atomic private run.

Before commit, rollback restores exactly the three implementation paths to
their pre-correction committed bytes. After commit, rollback is a bounded
revert; history rewriting is forbidden. Preserve all test, regression, and
audit evidence.

STOP on dependency or proposal drift, test failure, formatting error, scope
drift, ambiguous public contract, unavailable runtime tzdata, private-data or
OOS access, feature/label or PnL construction, model/training work,
integration, execution authority, or remote publication without separate
exact approval. The next push is explicitly not authorized by this
implementation task.
