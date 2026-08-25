# GC Futures Independent Pretraining Calendar Adapter Correction Change Proposal

## 1. Proposal Record

- Date: `2026-08-25`.
- Capability: development-only GC Futures independent pretraining calendar adaptation correction.
- Proposal status: `PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED`.
- Decision: `READY_FOR_INDEPENDENT_DOCUMENT_AUDIT_ONLY`.
- Authority: documentation-only; no private rerun, dataset publication, training, final-OOS access,
  integration, or trading.

This record corrects the deterministic in-memory mapping from the accepted normalized calendar to
the existing dataset-builder calendar dataclasses. It does not change calendar facts, source bars,
detector semantics, labels, corpus authority, or any public Python contract.

## 2. Exact Documentation Scope

This task may create only:

- `docs/gc_futures_independent_pretraining_calendar_adapter_correction_change_proposal.md`.

No Python, test, fixture, package export, private source, calendar, transaction artifact, manifest,
configuration, integration file, existing documentation file, or Git-excluded evidence may change.
The three pre-existing user-owned untracked proposals remain untouched.

## 3. Governing Baseline

The proposal is based on:

- `HEAD` and local `origin/main`:
  `7fa634c5563f3caf72fea3fbf42c6b8e8921a324`;
- subject: `docs: propose atomic independent pretraining upstream build`;
- governing proposal:
  `docs/gc_futures_independent_pretraining_atomic_upstream_build_change_proposal.md`;
- governing proposal SHA-256:
  `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44`.

Sections 1-11 and 16-24 of the governing proposal remain authoritative except where this record
adds the exact calendar-view mapping and clean-rerun procedure.

## 4. Failed Run A Evidence

The authorized private transaction reached only the Run A dataset gate:

- five permitted development sources parsed: `129,503` rows;
- normalized calendar materialized: `255` rows;
- dataset status: `INVALID`;
- `SPLIT_SESSION_REQUIRES_MULTIPLE_INTERVALS`: `250`;
- `CALENDAR_SOURCE_ARTIFACTS_OUT_OF_ORDER`: `1`;
- segments: `0`;
- dataset manifest: absent;
- serialized files: `0`;
- Run B, `.accepted_pending`, and `accepted`: absent.

Candidate, feature/label, and corpus builders were not called. The failure therefore preserved the
governing proposal's atomic no-downstream rule.

## 5. Root Cause

The failed orchestration mapped every eligible normalized row to
`GCSplitSessionCalendarEntry`. That type intentionally requires at least two non-touching intervals;
250 eligible rows contained exactly one interval. The sole multi-interval row retained source
lineage in normalized-file order rather than the builder's required ascending artifact-ID order.

This is an adapter defect, not evidence of malformed raw bars, incorrect calendar facts, or a
dataset-builder defect. Retrying the same mapping is forbidden.

## 6. No Public API Change

The correction may use only existing frozen dataclasses:

- `KillZoneCalendarEntry`;
- `GCDatasetSessionInterval`;
- `GCSplitSessionCalendarEntry`.

It may call the existing keyword-only builders exactly as committed. No new dataclass, enum,
parameter, default, identity field, package export, tracked adapter, or semantic relaxation is
authorized. If the exact mapping below cannot be performed without a public change, STOP and open
a new test-first proposal.

## 7. Immutable Calendar Source

The sole admissible calendar input remains:

`private_data/sierra_chart/gc_independent_pretraining_calendar_2024_2025_v1/normalized_calendar.jsonl`

Its required SHA-256 is
`EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED`.
The version remains
`GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`, with `255` rows, `252`
intervals, partitions `150/50/55`, and tzdata `2026.2`. Byte or count drift is a STOP condition.

## 8. Exact Row Classification

Each JSONL row is independently classified before dataclass construction:

1. `session_status == SESSION_CLOSED` and zero intervals: closed single-session view;
2. `session_status == ELIGIBLE` and exactly one interval: open or early-close single-session view;
3. `session_status == ELIGIBLE` and two or more intervals: split-session view;
4. every other combination: `INVALID`.

Classification uses only that immutable row. Later bars, candidates, labels, partitions, and roll
outcomes cannot influence it.

## 9. Closed-Session Mapping

A closed row maps exactly to:

```python
KillZoneCalendarEntry(
    calendar_version,
    trade_date,
    KillZoneSessionStatus.SESSION_CLOSED,
    None,
    None,
)
```

Any interval, open timestamp, close timestamp, or inferred reopen attached to this view is
`INVALID`. The original normalized row and lineage remain externally bound under Section 13.

## 10. Single-Interval Mapping

An eligible row with exactly one interval maps to `KillZoneCalendarEntry`. The supplied UTC start
must equal the canonical prior-calendar-day `18:00 America/New_York` instant. The supplied end must
be later than the start and no later than trade-date `17:00 America/New_York`.

- end equal to canonical `17:00` maps to `KillZoneSessionStatus.OPEN`;
- an earlier end maps to `KillZoneSessionStatus.EARLY_CLOSE`;
- a later end, wrong open, reversed geometry, or off-grid instant is `INVALID`.

No interval may be split, padded, shortened, or synthesized to satisfy another dataclass.

## 11. Multi-Interval Mapping

An eligible row with at least two intervals maps to `GCSplitSessionCalendarEntry`. Every interval
must preserve the exact supplied UTC endpoints and order. Intervals must be aware, strictly ordered,
five-minute aligned, non-overlapping, and non-touching. A generic single-session prior-calendar-day
`18:00` to trade-date `17:00 America/New_York` containment rule is not imposed on this exceptional
exchange-business-date view: a source-verified holiday sequence may begin earlier and span an
intervening halt. Its exact normalized interval sequence and lineage are authoritative. The adapter
may not merge a maintenance gap, truncate the verified span, or manufacture a second interval.

## 12. Exact Provenance Ordering

For a multi-interval row, each `(artifact_id, sha256)` association is preserved. The artifact ID is
not changed. Its source SHA must be exactly 64 hexadecimal characters and is canonicalized to
lowercase for the existing builder view; the exact source spelling remains bound by the normalized
calendar byte hash. Pairs are then sorted by ascending normalized `artifact_id`. IDs must be
nonempty and unique; hashes in the materialized view must be exact lowercase SHA-256 values; equal
IDs with different hashes, duplicate pairs, length mismatch, or pair reassociation is `INVALID`.

Hash lexical order is never an independent tie-break. Sorting the IDs and hashes separately is
forbidden because it can break their association.

## 13. Lineage Preservation Boundary

`KillZoneCalendarEntry` has no provenance fields. Therefore its use is only a geometry/status view
for the existing dataset builder and is not proof that lineage disappeared. The corrected private
transaction manifest must additionally bind:

- the exact normalized-calendar byte hash;
- one deterministic ordered digest over every row's `trade_date`, `calendar_row_id`, interval
  sequence, and ordered `(artifact_id, canonical-lowercase-sha256)` lineage pairs;
- the calendar version, row count, interval count, partition counts, and tzdata version.

The digest is computed before raw bars are parsed and compared between Run A and Run B. Dataset
identity does not replace this transaction-level lineage binding.

## 14. Round-Trip Equivalence Gate

Before `build_gc_futures_dataset()` is called, each materialized view must round-trip to the source
row's calendar version, trade date, session closure or exact interval sequence. The external
lineage digest must also reconcile. A view that changes any timestamp, status, interval count,
artifact-ID/hash association, canonical hash value, or row order is `INVALID` and prevents the
dataset call.

## 15. Canonical Tuple Ordering

Calendar views are emitted in strictly increasing `trade_date` order. The adapter performs no
silent date sort: the source JSONL itself must already be strictly ordered and unique. Equal dates,
historical insertion, missing rows, repair, reorder, or version mutation fails before raw parsing.

## 16. Failed Transaction Disposition

The current failed root may be removed only after a read-only audit proves that its resolved path is
exactly
`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`, it contains only `.run_a` and
the four permitted empty stage directories, contains zero files, and has no symlink, junction, or
reparse point. Removal is rollback of the failed empty transaction, not deletion of evidence.

If any file or unexpected child exists, STOP and retain the root unchanged.

## 17. Corrected Clean-Run Preflight

After authorized rollback, the transaction root and all prospective children must again be absent.
All governing tracked/private hashes, calendar counts, five development-source hashes and row
counts, runtime tzdata, and OOS metadata-only counters must reconcile. The final-OOS payload must
not be opened, hashed, parsed, copied, summarized, or reconstructed.

## 18. Corrected Run A

Run A independently opens immutable calendar and development-source bytes. It builds and validates
the exact calendar views and lineage digest before raw parsing, then follows governing proposal
Section 14. `build_gc_futures_dataset()` is called exactly once. Any non-`VALID` result prevents
structural-seed, candidate, feature/label, corpus, and serialization calls.

No result from the failed attempt may be reused.

## 19. Corrected Run B and Comparison

Run B starts only after the entire Run A in-memory chain is `VALID`. It repeats from original bytes
with fresh objects and directories. Run B may not read failed-attempt or Run A output. Comparison
includes materialized calendar views, external lineage digest, normalized result objects, canonical
serialized bytes, IDs, counts, volumes, exclusions, partitions, and authority flags.

Any difference is `NON_DETERMINISTIC` and blocks publication.

## 20. Atomic Publication and Authority

Only two complete `VALID` runs may create `.accepted_pending`. Exact Run A bytes are copied there,
and one same-volume atomic rename publishes `accepted`. The accepted transaction manifest binds
both run hashes, all governing input hashes, the normalized-calendar hash, and the lineage digest.

Even after publication, `training_authorized`, `oos_authorized`, `integration_authorized`, and
`trading_authorized` remain `False`.

## 21. Exact Sequential 48-Case Verification Matrix

1. HEAD and origin/main match the recorded baseline.
2. Governing proposal hash matches.
3. Exact one-file documentation scope holds.
4. Pre-existing untracked proposal bytes are unchanged.
5. Failed Run A parsed exactly five permitted sources.
6. Failed Run A parsed exactly 129,503 source rows.
7. Failed Run A materialized exactly 255 calendar rows.
8. Failed Run A stopped at dataset status INVALID.
9. Failed Run A reasons reconcile exactly.
10. Failed Run A serialized zero files.
11. Run B, pending, and accepted remained absent.
12. No downstream builder was called after failure.
13. Calendar JSONL hash matches.
14. Calendar version, tzdata, row, interval, and partition counts match.
15. Source JSONL dates are strictly increasing and unique.
16. Closed rows have zero intervals.
17. Closed rows map to SESSION_CLOSED with null timestamps.
18. Eligible single-interval rows map to KillZoneCalendarEntry.
19. Canonical single-session open equals prior-day 18:00 New York.
20. Standard close maps to OPEN.
21. Earlier valid close maps to EARLY_CLOSE.
22. Invalid single-session geometry fails before dataset execution.
23. Multi-interval rows map only to GCSplitSessionCalendarEntry.
24. Multi-interval endpoints remain byte-equivalent after normalization.
25. Split intervals preserve exceptional source geometry and are ordered, non-touching, and
    non-overlapping.
26. No fake interval or gap repair is introduced.
27. Provenance IDs are nonempty and unique.
28. Provenance source hashes validate as SHA-256 and builder-view hashes are canonical
    lowercase.
29. Provenance pairs sort by artifact ID without reassociation.
30. Pair duplication, mismatch, or conflict is INVALID.
31. Calendar view tuple preserves source trade-date order.
32. Every view passes exact round-trip geometry reconciliation.
33. External lineage digest covers every normalized row.
34. Run A and Run B lineage digests are identical.
35. Existing public signatures and dataclasses are unchanged.
36. No tracked adapter or package export is introduced.
37. Failed-root audit proves exact resolved target and zero files.
38. Unexpected failed-root content blocks rollback.
39. Corrected preflight requires a fully absent transaction root.
40. Final-OOS metadata counters remain zero without payload access.
41. Corrected Run A calls dataset builder exactly once.
42. Any Run A non-VALID status prevents all downstream calls.
43. Run B starts only after complete Run A VALID.
44. Run B uses fresh inputs, objects, and directories.
45. Two-run objects, bytes, hashes, lineage, and counts reconcile.
46. Pending is created only after every gate passes.
47. One atomic rename publishes accepted with all authorities false.
48. This proposal grants no private rerun, training, OOS, integration, push, or trading authority.

## 22. Verification and Promotion Requirements

This documentation file may be locally committed only after full-content, exact 24-section,
exact 48-case, hash, formatting, scope, cached-content, and cached-diff audits pass. Fresh focused
dataset tests and the full cache-disabled repository suite must pass before commit.

Push requires separate exact GitHub privacy/export authorization. Corrected private rollback and
rerun require a later authorization naming this unchanged proposal and transaction root.

## 23. Rollback and Stop Conditions

Before local commit, rollback is deletion of this new documentation file only. After commit,
rollback is a normal forward revert. STOP on baseline drift, calendar/source hash drift, unexpected
failed-root content, mapping ambiguity, round-trip mismatch, provenance loss, need for a public API
change, OOS contact, non-`VALID` builder status, nondeterminism, regression failure, scope expansion,
training, integration, or trading authority.

## 24. Final Decision and Resume Boundary

The exact state after this proposal is:

`CALENDAR_ADAPTER_CORRECTION_PROPOSED_NO_IMPLEMENTATION_NO_PRIVATE_RERUN_NO_TRAINING_NO_OOS`.

After independent audit and local commit, STOP before push. After separately authorized push and
post-push audit, a later exact authorization may permit read-only failed-root audit, empty-root
rollback, and one corrected clean two-run private transaction. That execution must independently
audit its result and stop before training, final-OOS access, integration, or further Git actions.
