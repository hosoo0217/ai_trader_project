# GC Futures Independent Pretraining Calendar Coverage and Partition Eligibility Correction Change Proposal

## 1. Proposal Record

- Date: `2026-08-25`.
- Capability: development-only GC Futures independent-pretraining upstream build.
- Proposal status: `PROPOSED_NOT_IMPLEMENTED`.
- Decision: `READY_FOR_INDEPENDENT_DOCUMENT_AUDIT_ONLY`.
- Authority: documentation-only; no private run, training, final-OOS access, integration, or trading.

This proposal corrects one semantic collision: calendar coverage used to validate exchange sessions
must not be the same object as the partition plan used to admit examples. The correction supplies
calendar evidence for the two purge/embargo gaps while continuing to exclude every gap row from
dataset segments, candidates, features, labels, and corpus records.

## 2. Exact Documentation-Only Scope

This task may create only:

- `docs/gc_futures_independent_pretraining_calendar_coverage_partition_eligibility_correction_change_proposal.md`.

No Python, test, fixture, private artifact, calendar, manifest, requirement, configuration,
integration file, package export, or other documentation file may change. In particular, these
pre-existing untracked files remain user-owned and untouched:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`;
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

## 3. Governing Baseline and Dependency Binding

The proposal is bound to:

- `HEAD`: `c1a119c84ec3ea27d11f48395315ca60b493a5f4`;
- local `origin/main`: `c1a119c84ec3ea27d11f48395315ca60b493a5f4`;
- subject: `fix(data): enforce GC source-domain roll boundaries`.

| Artifact | SHA-256 |
| --- | --- |
| atomic upstream proposal | `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44` |
| dual-calendar projection proposal | `EE08ACF33E4BE57D42E5242EC771B0CCD56CBDA1FF062E219334C88873A2E1AA` |
| source-domain correction proposal | `C88C3D0A04A9160FD81EC01E8FE6F36595E90307A45000DFE843FB68D191A7DB` |
| source-domain checkpoint | `2F0F4A66BA74BDF32D99CE6FE97287F41084E93228A613926825B5ED262548F7` |
| dataset builder | `5B41BEAC0A2867DC398C7D1488A84E5191D2BFEBC499F7A79DC0B805800128DE` |
| dataset tests | `3FC36A80F4F6A7E3A48C4D6217A339235C5B6E4E957A80A65D67C6CABC3041CD` |
| normalized development calendar | `EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED` |

Any byte drift requires a fresh read-only audit before implementation.

## 4. Corrected Private Preflight Evidence

The source-domain-corrected private preflight stopped before target-root creation. It produced no
Run A serialization and did not start Run B. The exact terminal evidence was:

- source-registry prefixes `3..7`: all `UNKNOWN`;
- `11,503` in-domain bars blocked by `CALENDAR_COVERAGE_MISSING`;
- `55` terminal rows separately blocked by `COMPARABLE_COMPLETED_VOLUME_MISSING`;
- no candidate, feature, label, corpus, training, OOS, or integration output;
- `private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`: absent.

The `11,503` missing-calendar bars reconcile by source as:

| Contract | Bars |
| --- | ---: |
| `GCJ25` | 0 |
| `GCM25` | 357 |
| `GCQ25` | 2,818 |
| `GCV25` | 4,716 |
| `GCZ25` | 2,730 |
| `GCG26` | 882 |
| `GCJ26` | 0 |
| **Total** | **11,503** |

These counts are diagnostic evidence, not permission to promote any row.

## 5. Verified Root Cause

The accepted calendar currently contains the three eligible development partitions only. It
intentionally omits the two purge/embargo gaps. The dataset builder nevertheless requires calendar
coverage for every in-domain source bar so that completed-session volumes and roll decisions are
causal across the full source domain.

The current builder also converts a missing partition classification to
`GCSegmentPartition.DEVELOPMENT`. Therefore, merely adding gap calendar rows would silently admit
gap bars. The correction must change both calendar coverage and dataset admission together. A
calendar-only repair is forbidden.

## 6. Immutable Terminology and Authority Boundary

- **Eligibility calendar**: the unchanged 255-date projection used by downstream candidate and
  corpus contracts to describe admitted `TRAIN`, `VALIDATION`, and `CALIBRATION` evidence.
- **Coverage calendar**: the 275-date projection used by the dataset and candidate validators to
  reconcile every in-domain source moment and exchange session.
- **Partition plan**: the only authority for admitting a trade date to an output partition.
- **Purge/embargo gap**: a covered exchange date that is deliberately ineligible for output.

Calendar coverage proves when a session existed. It does not grant partition eligibility. The
builder must never infer training authority, candidate authority, OOS authority, integration
authority, or trading authority from coverage.

## 7. Immutable Source and Existing Calendar Evidence

The accepted private calendar root remains:

`private_data/sierra_chart/gc_independent_pretraining_calendar_2024_2025_v1/`

Its immutable baseline is:

- version `GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`;
- runtime tzdata version `2026.2`;
- 255 requested trade dates;
- 252 trading intervals;
- `TRAIN/VALIDATION/CALIBRATION` rows `150/50/55`;
- 251 eligible trading dates and 4 closed dates;
- one split session on `2024-11-29`;
- no gap, embargo, or final-OOS row synthesized.

The correction derives a separate coverage projection from accepted official CME evidence. It
does not rewrite the accepted 255 rows or mutate their provenance.

## 8. Exact Fixed Partition Plan

The immutable half-open plan remains:

- `TRAIN`: `[2024-11-04, 2025-06-02)`;
- purge/embargo gap 1: `[2025-06-02, 2025-06-16)`;
- `VALIDATION`: `[2025-06-16, 2025-08-25)`;
- purge/embargo gap 2: `[2025-08-25, 2025-09-08)`;
- `CALIBRATION`: `[2025-09-08, 2025-11-24)`;
- sealed final-OOS metadata only: `[2026-07-06, 2026-08-01)`.

Label horizon and minimum embargo remain `12` bars. The correction must not alter boundary dates,
assign either gap to `DEVELOPMENT`, or create a new public partition enum.

## 9. Exact Coverage-Calendar Domain and Added Dates

The full coverage projection contains exactly 275 dates: the immutable 255 eligibility rows plus
these exact 20 internal weekdays:

```text
2025-06-02  2025-06-03  2025-06-04  2025-06-05  2025-06-06
2025-06-09  2025-06-10  2025-06-11  2025-06-12  2025-06-13
2025-08-25  2025-08-26  2025-08-27  2025-08-28  2025-08-29
2025-09-01  2025-09-02  2025-09-03  2025-09-04  2025-09-05
```

The accepted outer timestamp domain remains
`[2024-11-03T23:00:00Z, 2025-11-21T22:00:00Z)`. No date before, after, or inside final OOS may be
added by this proposal.

## 10. Exact Added Session Geometry

All 20 added dates are America/New_York, timezone-data version `2026.2`, and use exact UTC-aware
timestamps. Nineteen are ordinary sessions:

- open: previous calendar day `18:00` America/New_York, inclusive;
- close: trade date `17:00` America/New_York, exclusive;
- daily maintenance remains the boundary between sessions.

`2025-09-01` is Labor Day and is an authenticated early-halt session:

- open: `2025-08-31 18:00` America/New_York, inclusive;
- close: `2025-09-01 14:30` America/New_York, exclusive.

All added dates fall in EDT: ordinary UTC bounds are prior day `22:00Z` to trade date `21:00Z`;
Labor Day closes at `18:30Z`. No synthetic full-day, inferred holiday, or zero-volume filler row is
allowed.

## 11. Exact Coverage Projection Reconciliation

The corrected coverage projection must reconcile to:

- 275 requested dates;
- 271 trading entries;
- 4 closed entries;
- 272 ordered non-overlapping session intervals;
- one split-session date, still `2024-11-29`;
- dataset session-class counts: 263 `ORDINARY`, 2 `EARLY_CLOSE`, 5 `EARLY_HALT`, 1
  `SPLIT_SESSION`, and 4 `CLOSED`;
- candidate civil-date status counts: 263 `OPEN`, 9 `EARLY_CLOSE`, and 3 `SESSION_CLOSED`;
- original 255 normalized rows byte-for-byte and provenance-for-provenance unchanged;
- added 20 rows bound to the official standard-hours and Labor Day evidence.

The dataset and candidate projections intentionally use their respective committed vocabularies.
They must not be conflated, and a count or semantic mismatch is a STOP condition.

## 12. Exact Projection and Builder Call Binding

One deterministic parse of accepted calendar evidence produces four immutable tuples:

1. unchanged 255-row dataset eligibility projection;
2. unchanged 255-row candidate eligibility projection;
3. corrected 275-row dataset coverage projection;
4. corrected 275-row candidate coverage projection.

`build_gc_futures_dataset()` receives the dataset coverage projection. The structural candidate
builder receives the candidate coverage projection so every source moment can reconcile. Corpus
partitioning continues to receive the unchanged eligibility projection and exact partition plan.
The 255-row projections remain immutable lineage evidence and are not silently replaced on disk.

No filesystem order, current date, model output, candidate outcome, volume dominance, or later
label may influence projection construction.

## 13. Exact Dataset Partition-Exclusion Semantics

For every valid covered row, the dataset builder must compute partition eligibility independently
from calendar coverage:

- eligible development date: preserve existing `DEVELOPMENT` behavior;
- sealed OOS date: preserve existing `OOS_HOLDOUT` behavior and access prohibition;
- purge/embargo date: record exact exclusion reason `PARTITION_EMBARGO` and do not append the row to
  output-eligible `usable` evidence;
- before initial boundary: `BEFORE_INITIAL_BOUNDARY`;
- after OOS boundary: `AFTER_OOS_BOUNDARY`.

The forbidden fallback `partition = scoped_partition or DEVELOPMENT` must not admit an uncovered
or ineligible date. No public enum or identity payload is changed.

## 14. Roll-Volume Continuity Across Excluded Dates

A valid purge/embargo row remains eligible only for completed-session volume computation. It is
appended to the internal `volume_usable` sequence after all source, coverage, calendar, timestamp,
role, and volume validations pass, but it is never appended to output `usable` evidence.

This separation is required so the canonical prior-completed-session roll rule can cross the two
gaps without hindsight, while the resulting gap bars remain absent from segments and all
downstream research records. Gap volume may influence a later roll decision; it may not become a
feature, label, candidate, corpus example, or target.

## 15. Calendar-Missing and Status Semantics

For an in-domain source moment:

- absent coverage remains `UNKNOWN / CALENDAR_COVERAGE_MISSING`;
- malformed, overlapping, contradictory, wrong-version, or wrong-timezone coverage is `INVALID`;
- a valid covered purge/embargo date is not `UNKNOWN`; it is deterministically excluded;
- the existing `55` terminal `COMPARABLE_COMPLETED_VOLUME_MISSING` condition remains visible and
  must not be relabeled as calendar coverage failure.

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The correction must not suppress a higher-precedence issue or promote evidence from its failing
same-effective group.

## 16. Exact Conservation and No Silent Filtering

The implementation checkpoint must reconcile, by source and trade date:

- parsed rows;
- calendar-covered rows;
- output-eligible rows;
- `PARTITION_EMBARGO` rows;
- boundary exclusions;
- closed/outside-session exclusions;
- completed-session volume inputs;
- emitted segment bars;
- all remaining blocking reasons.

For the corrected preflight, the prior `11,503` calendar-missing rows must become either validated
`PARTITION_EMBARGO` rows or another explicit higher-precedence failure. They may not disappear.
The exact `55` comparable-volume gap remains separately conserved unless a later proposal resolves
it.

## 17. Deterministic Identity and Version Binding

Coverage projection identity binds normalized calendar version, tzdata version, ordered trade
dates, ordered session intervals, statuses, timestamps, and source provenance. Dataset identities
continue to bind the existing calendar, coverage, evidence, source, segment, and roll digests.

The implementation must bump the appropriate internal builder/checkpoint version binding so old
and corrected semantics cannot share an identity. Repeated construction from identical inputs must
produce identical normalized objects, reasons, exclusions, IDs, canonical bytes, and SHA-256
values. Hash order is never a chronology tie-break.

## 18. Public API and Compatibility Boundary

The exact keyword-only APIs, parameters, annotations, defaults, frozen dataclasses, enums, result
reason tuple shape, and exports remain unchanged. The new internal exclusion token is the bounded
semantic correction, not a new public enum. In particular:

```python
build_gc_futures_dataset(
    *, exports, coverage_evidence, calendar_entries, config,
)
```

No package export, importer, CLI, config file, engine, runtime strategy, execution path, trace
wiring, training path, or final-OOS reader may change. Existing callers using only eligible dates
must remain output-equivalent except for the intentional internal version binding.

## 19. Future Implementation Exact Three-Path Scope

A later explicit implementation authorization may change only:

- `analysis/gc_dataset_builder.py`;
- `tests/test_gc_dataset_builder.py`;
- `docs/gc_futures_dataset_builder_calendar_coverage_partition_eligibility_checkpoint.md`.

The checkpoint path must be absent before implementation. Calendar private files, candidate,
feature/label, corpus, SMC, orderflow, integration, configuration, and package-export files are
outside scope. A required fourth path is an immediate STOP condition.

## 20. Test-First, Atomic Processing, and Prefix Invariance

Tests must be added before source correction. The builder validates an entire same-effective group
before promotion. A later malformed group preserves strictly prior immutable evidence and promotes
nothing from the failing group or after it.

Strictly-later complete coverage and source extensions must preserve the prior eligible prefix
byte-for-byte. Same-effective append, historical calendar insertion, repair, reorder, version
mutation, or partition-plan mutation is not a prefix-invariant extension. Two isolated executions
from immutable inputs must be object-, byte-, count-, reason-, identity-, and hash-equal before any
private accepted publication can later be considered.

## 21. Inline Synthetic Exact 48-Case Unit-Test Matrix

1. Recorded HEAD, origin/main, subject, and dependency hashes match.
2. Exact documentation-only one-file scope holds.
3. The three pre-existing untracked proposals remain byte-unchanged.
4. Corrected private preflight root remains absent and no output was promoted.
5. The seven per-source missing-calendar counts sum to exactly 11,503.
6. The separate 55-row comparable-volume failure remains visible.
7. Existing 255 eligibility rows and their ordered canonical bytes remain unchanged.
8. Existing eligibility counts remain 150/50/55 and four closed dates.
9. Full coverage contains exactly 275 dates and 272 intervals.
10. Full coverage contains exactly the listed 20 added weekdays.
11. No unlisted date is added to the coverage projection.
12. Outer calendar timestamp domain remains unchanged.
13. Nineteen added ordinary sessions use exact prior-day 18:00 to trade-date 17:00 ET bounds.
14. Added ordinary sessions normalize to exact EDT UTC bounds.
15. Labor Day 2025 uses exact prior-day 18:00 to 14:30 ET early-halt bounds, projected as candidate `EARLY_CLOSE`.
16. Labor Day UTC close is exactly 18:30Z.
17. Full projection status and trading/closed counts reconcile.
18. Existing split-session 2024-11-29 remains the sole split session.
19. Added provenance binds only accepted official CME evidence.
20. Dataset eligibility and coverage projections are independently immutable.
21. Candidate eligibility and coverage projections are independently immutable.
22. Dataset builder receives full coverage rather than the 255-row eligibility tuple.
23. Candidate builder receives full coverage for source-moment reconciliation.
24. Corpus builder receives unchanged eligibility evidence and exact partition plan.
25. Eligible TRAIN rows retain existing DEVELOPMENT admission.
26. Eligible VALIDATION rows retain existing DEVELOPMENT admission.
27. Eligible CALIBRATION rows retain existing DEVELOPMENT admission.
28. Gap-1 rows receive exact PARTITION_EMBARGO exclusion.
29. Gap-2 rows receive exact PARTITION_EMBARGO exclusion.
30. No gap row appears in an emitted dataset segment.
31. No gap row becomes candidate, feature, label, or corpus evidence.
32. Gap rows remain available to completed-session volume calculation.
33. Roll confirmation can cross gap 1 causally without gap output promotion.
34. Roll confirmation can cross gap 2 causally without gap output promotion.
35. The first eligible post-gap segment uses the canonical prior-session roll decision.
36. Missing in-domain coverage remains UNKNOWN/CALENDAR_COVERAGE_MISSING.
37. Malformed or contradictory coverage remains INVALID without exception leakage.
38. INVALID precedence is not suppressed by UNKNOWN or valid prior evidence.
39. Strictly prior immutable segments survive a determinably later failure byte-for-byte.
40. No evidence from a failing same-effective group or after it is promoted.
41. Parsed, covered, embargo, boundary, volume-input, and emitted counts conserve exactly.
42. The previous 11,503 blocked rows cannot silently disappear after correction.
43. The 55 comparable-volume rows are not relabeled as calendar failures.
44. Dataset public signature, annotations, dataclasses, enums, and exports remain exact.
45. Unknown identity kinds and malformed hashes continue to fail closed.
46. Strictly-later complete extension preserves the eligible prefix; historical repair does not.
47. Focused and full cache-disabled regression suites plus formatting/scope audits pass.
48. No private run, training, final-OOS access, integration, push, or trading authority is granted.

## 22. Independent Verification and Promotion Gates

Before a later implementation commit, an independent audit must verify full source and test
contents, exact three-path scope, exact 48-case reconciliation, signatures, frozen contracts,
reason tokens, hashes, byte/line counts, formatting, and cached contents. Required tests are:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
```

The documentation-only proposal may be locally committed after the same baseline tests pass. A
private corrected transaction requires a separate explicit authorization after implementation is
committed and pushed.

Fresh documentation-only baseline evidence captured on 2026-08-25:

- focused: `250 passed in 1.08s`;
- full: `2524 passed in 24.49s`;
- both commands used `-p no:cacheprovider` exactly as required;
- no source, test, private-data, OOS, integration, or training artifact was changed or created by
  this proposal task.

## 23. Rollback, Promotion, and Stop Conditions

Rollback for this documentation task is deletion of this one uncommitted file. Future source
rollback is the exact three-path commit only; private failure rollback removes only a newly created
failed transaction root after its resolved path is revalidated.

Promotion requires all of the following: test-first implementation, independent code audit, exact
scope, deterministic two-run equality, complete conservation, no final-OOS contact, and separate
explicit private-run authority. Stop immediately on dependency drift, evidence conflict, fourth
tracked path, public API change, missing official evidence, non-determinism, conservation failure,
unexpected private-root content, OOS access, or any request to train or integrate.

## 24. Final Decision and Resume Boundary

The exact decision is:

`CALENDAR_COVERAGE_PARTITION_ELIGIBILITY_CORRECTION_PROPOSED_NO_IMPLEMENTATION_NO_PRIVATE_RUN_NO_TRAINING_NO_OOS`

The project may next request an independent final audit of this document. If it passes, only this
file may be staged and locally committed. Implementation, private execution, training, final-OOS
access, integration, package wiring, and push remain frozen until separately and explicitly
authorized.
