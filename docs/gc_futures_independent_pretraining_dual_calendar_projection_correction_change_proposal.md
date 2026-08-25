# GC Futures Independent Pretraining Dual-Calendar Projection Correction Change Proposal

## 1. Proposal Record

- Date: `2026-08-25`.
- Capability: development-only GC independent-pretraining calendar projection correction.
- Proposal status: `PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED`.
- Decision: `READY_FOR_INDEPENDENT_DOCUMENT_AUDIT_ONLY`.
- Authority: documentation-only; no private rerun, dataset/corpus publication, training, final-OOS
  access, integration, or trading.

This record corrects the missing boundary between exchange-business-date calendar evidence and the
New York civil-date calendar consumed by the Kill-zone detector. It does not change accepted
calendar facts, source bars, detector semantics, labels, corpus authority, or a public Python API.

## 2. Exact Documentation Scope

This task may create only:

- `docs/gc_futures_independent_pretraining_dual_calendar_projection_correction_change_proposal.md`.

No Python, test, fixture, package export, private source, normalized calendar, transaction artifact,
manifest, configuration, integration file, or existing documentation file may change. The three
pre-existing user-owned untracked proposals remain untouched.

## 3. Governing Baseline

The proposal is based on:

- `HEAD` and local `origin/main`:
  `6944b35876a1027459f6bd0800d5ddbf3b8b7297`;
- subject: `docs: propose independent pretraining calendar adapter correction`;
- atomic upstream proposal:
  `docs/gc_futures_independent_pretraining_atomic_upstream_build_change_proposal.md`;
- atomic upstream proposal SHA-256:
  `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44`;
- first calendar-adapter proposal:
  `docs/gc_futures_independent_pretraining_calendar_adapter_correction_change_proposal.md`;
- first calendar-adapter proposal SHA-256:
  `11DC4FF7521A20FA414779C3BC6296B1AE533F828484AF1208E1D61379EAE4A0`.

The earlier records remain authoritative except where this proposal separates their previously
underspecified calendar view into the two exact projections below.

## 4. Current Private Transaction Evidence

The retained private transaction root is exactly:

`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`.

At proposal time it contains only `.run_a` and the four permitted empty directories `dataset`,
`candidate_evidence`, `feature_labels`, and `corpus`. It contains zero files. Run B,
`.accepted_pending`, and `accepted` are absent. No persisted root receipt proves an exact runtime
status or gate; therefore this record does not claim that the corrected run reached candidate,
feature/label, or corpus execution.

## 5. Verified Contract Mismatch

The following committed contracts are independently verifiable:

1. `build_gc_futures_dataset()` accepts a calendar tuple containing either
   `KillZoneCalendarEntry` or `GCSplitSessionCalendarEntry`.
2. `build_gc_candidate_evidence()` accepts only exact `KillZoneCalendarEntry` values and rejects a
   `GCSplitSessionCalendarEntry`.
3. `analyze_kill_zones()` classifies its calendar `trade_date` as the New York civil date of the
   Asia-following-date, London, New York AM, or New York PM window.
4. `build_gc_pretraining_corpus()` binds the mixed dataset calendar, not a synthetic Kill-zone
   projection.
5. Existing cross-segment continuity already keeps boundary and candidate calendars as distinct
   supplied tuples and forbids silently inferring one from the other.

Passing the same tuple to every builder is therefore not an exact contract and is forbidden.

## 6. Root Cause and Correction Boundary

The normalized calendar is keyed by CME exchange business date. A Kill-zone calendar is keyed by
New York civil date. They usually coincide but are not equivalent on exchange-holiday sequences.

For Thanksgiving 2024, exchange business date `2024-11-29` contains two verified intervals:

- `[2024-11-27T23:00:00Z, 2024-11-28T19:30:00Z)`;
- `[2024-11-28T23:00:00Z, 2024-11-29T19:45:00Z)`.

The normalized exchange row `2024-11-28` is `SESSION_CLOSED`, while the first interval above
contains real trading on New York civil date `2024-11-28`. Treating the closed exchange row as the
Kill-zone civil-date row would falsely suppress that trading. Merging both intervals would insert a
verified halt and exceed the single-session contract. Both shortcuts are forbidden.

## 7. Immutable Calendar Source

The sole admissible calendar source remains:

`private_data/sierra_chart/gc_independent_pretraining_calendar_2024_2025_v1/normalized_calendar.jsonl`

with required SHA-256
`EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED`, version
`GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`, tzdata `2026.2`, `255` rows,
`252` intervals, and partitions `150/50/55`. Byte, version, count, partition, or timezone drift is a
STOP condition.

## 8. Two Immutable Calendar Projections

One parse of the immutable JSONL produces two independent frozen tuples before any raw source bar
is opened:

- `dataset_calendar_entries`: exchange-business-date geometry for dataset and corpus builders;
- `candidate_calendar_entries`: New York civil-date session geometry for the candidate builder and
  Kill-zone detector.

Neither tuple is derived from the other. Both are independently derived from the same normalized
rows and bound to the source byte hash and row-level lineage. Later bars, detector output, candidate
count, labels, partitions, or outcomes cannot alter either projection.

## 9. Dataset Projection

The dataset projection retains the first adapter proposal exactly:

- closed row with zero intervals -> `KillZoneCalendarEntry(SESSION_CLOSED, None, None)`;
- eligible row with one interval -> `KillZoneCalendarEntry(OPEN|EARLY_CLOSE, start, end)`;
- eligible row with two or more intervals -> `GCSplitSessionCalendarEntry` with every exact interval
  and canonically paired provenance;
- every other shape -> `INVALID`.

It contains exactly `255` strictly exchange-business-date-ordered entries, including exactly one
split entry for `2024-11-29`. This tuple alone is passed to `build_gc_futures_dataset()` and
`build_gc_pretraining_corpus()`.

## 10. Candidate Projection Date Rule

Each supplied trading interval independently maps to a candidate civil date equal to its exclusive
end instant converted through runtime `America/New_York`. The interval start must convert to exactly
`18:00` on the preceding New York calendar date. The end must be later than the start and no later
than `17:00` on the candidate civil date.

- end exactly `17:00` -> `KillZoneSessionStatus.OPEN`;
- end earlier than `17:00` -> `KillZoneSessionStatus.EARLY_CLOSE`;
- wrong start, end after `17:00`, reversed interval, naive timestamp, wrong timezone conversion, or
  duration above 24 hours -> `INVALID`.

The candidate entry uses the unchanged normalized calendar version and exact UTC endpoints.

## 11. Candidate Closed-Date Rule

A normalized `SESSION_CLOSED` exchange row proposes a closed candidate civil date only when no
verified trading interval from any normalized row maps to that civil date. If an interval does map
to the same date, the interval-derived candidate geometry is authoritative for Kill-zone context;
the closed exchange row remains authoritative in the separate dataset projection.

This is not silent precedence. The collision, both source row IDs, their lineage, and the exact
interval ordinal are included in the projection digest. More than one interval mapping to the same
candidate civil date, duplicate closed rows, an unexplained closed/interval collision, or any
conflicting geometry is `INVALID`.

## 12. Exact Thanksgiving 2024 Projection

The only permitted closed/interval civil-date collision is source-verified `2024-11-28`:

- candidate `2024-11-28`: `EARLY_CLOSE`,
  `[2024-11-27T23:00:00Z, 2024-11-28T19:30:00Z)`;
- candidate `2024-11-29`: `EARLY_CLOSE`,
  `[2024-11-28T23:00:00Z, 2024-11-29T19:45:00Z)`.

The exchange-business-date `2024-11-28 SESSION_CLOSED` row is retained only in the dataset
projection. The two intervals retain their source exchange business date `2024-11-29` as
transaction-level lineage metadata; neither is relabeled in the normalized source.

## 13. Exact Candidate Projection Reconciliation

The candidate projection contains exactly `255` strictly increasing, unique civil-date entries:

- `244` `OPEN`;
- `8` `EARLY_CLOSE`;
- `3` `SESSION_CLOSED`.

It contains `252` interval-derived dates, four closed-row dates, and exactly one verified
closed/interval collision (`2024-11-28`), yielding `255` unique dates. Its first date is
`2024-11-04`; its last date is `2025-11-21`. Any count, status, boundary date, or collision drift is
`INVALID`.

## 14. Candidate Projection Special Dates

The non-ordinary candidate entries reconcile exactly to:

- early close: `2024-11-28 14:30 ET`, `2024-11-29 14:45 ET`,
  `2024-12-24 13:45 ET`, `2025-01-20 14:30 ET`, `2025-02-17 14:30 ET`,
  `2025-05-26 14:30 ET`, `2025-06-19 14:30 ET`, and `2025-07-04 13:00 ET`;
- closed: `2024-12-25`, `2025-01-01`, and `2025-04-18`.

All other candidate entries are `OPEN` and end at `17:00 America/New_York`. ET instants are
resolved by IANA timezone conversion and runtime tzdata `2026.2`, never a fixed UTC offset.

## 15. Provenance and Identity Binding

Because `KillZoneCalendarEntry` has no provenance fields, the private transaction manifest binds
two separate deterministic digests:

1. dataset projection digest over exchange date, dataclass kind, status or exact interval sequence,
   normalized row ID, and canonically paired source artifact ID/SHA-256 lineage;
2. candidate projection digest over civil date, status, exact interval or closure, originating
   normalized row ID, source exchange date, interval ordinal, collision disposition, and the same
   paired lineage.

Both digests bind the source JSONL SHA-256, calendar version, tzdata version, exact counts, and
ordered projection bytes. Dataset, candidate, feature/label, or corpus identity cannot replace
these transaction-level proofs.

## 16. Exact Builder Call Binding

The clean transaction must use the projections only as follows:

| Builder | Calendar argument |
| --- | --- |
| `build_gc_futures_dataset()` | `dataset_calendar_entries` |
| structural-seed builder/validator | canonical dataset result; no calendar substitution |
| `build_gc_candidate_evidence()` | `candidate_calendar_entries` |
| feature/label builder | canonical dataset and candidate results; no calendar substitution |
| `build_gc_pretraining_corpus()` | `dataset_calendar_entries` |

Passing the mixed dataset tuple to candidate analysis, passing the civil-date tuple to dataset or
corpus construction, reusing a builder result under another calendar digest, or relying on a
positional argument is `INVALID`.

## 17. No Public API or Tracked Adapter Change

The projection uses only committed frozen dataclasses and exact keyword-only builders. No public
signature, annotation, default, enum, dataclass, identity payload, package export, detector,
tracked adapter, test, or checkpoint may change under this proposal.

If the exact candidate projection cannot pass the existing candidate contract, if a segment slice
omits a required civil date, or if a public change is required, STOP. A later exact three-path,
test-first implementation proposal is then mandatory; this proposal grants no implementation
authority.

## 18. Failed-Root Rollback Preflight

Before any later authorized rerun, a read-only audit must prove that the resolved retained root is
exactly the path in Section 4, contains only the four named empty stage directories below `.run_a`,
contains zero files, and has no symlink, junction, mount point, or reparse point. Only then may the
empty failed root be removed as rollback.

Unexpected content, missing audit evidence, path drift, file content, Run B, pending, accepted, or
reparse metadata causes STOP and preserves the root unchanged.

## 19. Corrected Clean Run A

After separately authorized rollback, the transaction root and all prospective children must be
absent. Run A independently reopens original calendar and five development-source bytes, validates
both projections and both digests before parsing raw bars, and follows the atomic upstream proposal.

`build_gc_futures_dataset()` is called exactly once with the dataset projection. Only a complete
`VALID` dataset permits structural seed and then exactly one candidate call with the candidate
projection. Any non-`VALID` result stops downstream calls and publication. No failed-run object or
byte may be reused.

## 20. Corrected Run B and Atomic Publication

Run B starts only after the entire Run A in-memory dataset, structural, candidate, feature/label,
and corpus chain is `VALID`. It uses freshly reopened original bytes, fresh objects, and a separate
directory. Both calendar projections, digests, normalized objects, serialized bytes, IDs, counts,
volumes, exclusions, partitions, and authority flags must be byte-for-byte deterministic.

Only two complete equal runs may create `.accepted_pending`; one same-volume atomic rename may then
publish `accepted`. `training_authorized`, `oos_authorized`, `integration_authorized`, and
`trading_authorized` remain `False`.

## 21. Exact Sequential 48-Case Verification Matrix

1. HEAD and origin/main equal the recorded baseline.
2. Both governing proposal hashes match.
3. Exact one-file documentation scope holds.
4. Three pre-existing untracked proposal bytes remain unchanged.
5. Retained private root resolves to the exact permitted path.
6. Retained root contains only Run A's four empty stage directories.
7. Retained root contains zero files and no reparse metadata.
8. No exact runtime gate is claimed without a persisted receipt.
9. Normalized calendar SHA-256 matches.
10. Calendar version, tzdata, row, interval, and partition counts match.
11. Source rows are strictly exchange-date ordered and unique.
12. Dataset projection contains exactly 255 entries.
13. Dataset closed rows map to exact closed entries.
14. Dataset single intervals map to exact open/early-close entries.
15. Dataset split rows map only to exact split entries.
16. Dataset projection has exactly one split row, `2024-11-29`.
17. Candidate interval date equals New York local exclusive-end date.
18. Candidate interval starts at prior-local-day 18:00.
19. Candidate interval ends no later than local 17:00.
20. Standard close maps to OPEN.
21. Earlier valid close maps to EARLY_CLOSE.
22. Invalid candidate interval geometry is rejected.
23. Candidate closed row is emitted only without an interval collision.
24. Unexplained or multiple same-date interval collisions are rejected.
25. Exact permitted collision is `2024-11-28`.
26. Thanksgiving first interval maps to candidate `2024-11-28` early close.
27. Thanksgiving second interval maps to candidate `2024-11-29` early close.
28. Candidate projection has exactly 255 unique ordered dates.
29. Candidate projection counts are exactly 244/8/3.
30. Candidate projection range is exactly 2024-11-04 through 2025-11-21.
31. All eight early-close dates and times reconcile.
32. All three closed dates reconcile.
33. Runtime America/New_York and tzdata 2026.2 reconcile.
34. Dataset projection digest covers every normalized row and lineage pair.
35. Candidate projection digest covers every civil-date mapping and collision.
36. Lineage pairs remain associated and canonically ordered.
37. Builder calls receive only their locked calendar projection.
38. Existing public API, identities, exports, and tests remain unchanged.
39. Failed-root rollback requires exact empty-root proof.
40. Corrected preflight requires an absent transaction root.
41. Run A validates both projections before opening source bars.
42. Run A calls dataset and candidate builders at most once each.
43. Any non-VALID stage prevents all later calls and publication.
44. Run B starts only after the complete Run A chain is VALID.
45. Run B uses fresh source bytes, objects, and directories.
46. Both runs reconcile projections, digests, objects, bytes, and counts.
47. Atomic publication retains all authority flags false.
48. This proposal grants no private rerun, training, OOS, integration, push, or trading authority.

## 22. Verification and Promotion Requirements

This documentation file may be locally committed only after full-content, exact 24-section,
exact 48-case, hash, formatting, scope, cached-content, and cached-diff audits pass. Fresh focused
dataset, candidate, and corpus tests plus the full cache-disabled canonical repository suite must
pass before commit.

Push requires separate exact GitHub privacy/export authorization. Failed-root rollback and a clean
two-run private transaction require a later authorization naming this unchanged proposal and exact
transaction root.

## 23. Rollback and Stop Conditions

Before local commit, rollback is deletion of this new documentation file only. After commit,
rollback is a normal forward revert. STOP on baseline or hash drift, unexpected private-root
content, projection ambiguity, candidate-date collision beyond Section 12, count drift, provenance
loss, public API need, builder non-`VALID` status, nondeterminism, regression failure, scope
expansion, OOS contact, training, integration, or trading authority.

## 24. Final Decision and Resume Boundary

The exact state after this proposal is:

`DUAL_CALENDAR_PROJECTION_CORRECTION_PROPOSED_NO_IMPLEMENTATION_NO_PRIVATE_RERUN_NO_TRAINING_NO_OOS`.

After independent audit and local commit, STOP before push. After a separately authorized push and
post-push audit, a later exact authorization may permit only the failed-root audit, empty-root
rollback, and corrected clean two-run private transaction locked here. That execution must
independently audit its result and stop before training, final-OOS access, integration, or further
Git actions.
