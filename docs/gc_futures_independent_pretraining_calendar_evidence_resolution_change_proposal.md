# GC Futures Independent Pretraining Calendar Evidence Resolution Change Proposal

## 1. Proposal Record

- Proposal date: `2026-08-25`.
- Repository baseline: `20b32c03d09bc49ecc92b2f6e013b3fbf9afa431`.
- Baseline publication state: `HEAD`, local `origin/main`, and live remote `main` reconciled.
- Decision:
  `DOCUMENTATION_ONLY_ACCEPT_OFFICIAL_GLOBEX_TRADE_DATE_RULE_FOR_LATER_PRIVATE_ACQUISITION_NO_EXECUTION`.
- Authority granted by this document: documentation-only design authority.
- Global code freeze: active outside this exact document.

This proposal resolves the minimum evidence path needed before the independent pretraining
upstream-input build can be attempted. It does not download evidence, edit private manifests,
normalize calendar rows, build a dataset, run detectors, create labels, train a model, access OOS,
or authorize trading.

## 2. Exact Scope

The only path created by this task is:

- `docs/gc_futures_independent_pretraining_calendar_evidence_resolution_change_proposal.md`.

No Python, tests, fixtures, private artifacts, manifests, calendar rows, package exports,
configuration, integration, or other documentation may change. The three pre-existing untracked
documents remain unrelated user state and must not be opened, edited, staged, or committed.

## 3. Governing Decision

The committed conditional private-run proposal remains authoritative:

- path: `docs/gc_futures_independent_pretraining_corpus_private_run_change_proposal.md`;
- SHA-256: `90C05E3CD296C9447CDE4778B8BED8EECB2FC4F4D14F45B881F0B7DFB6D48CDC`;
- decision:
  `PRIVATE_RUN_NOT_READY_REQUIRE_CANONICAL_UPSTREAM_INPUT_BUILD_NO_EXECUTION_NO_TRAINING_NO_OOS`.

This document narrows only the calendar-evidence blocker. It does not alter source selection,
partitions, thresholds, identities, status precedence, no-look-ahead rules, or authority flags.

## 4. Verified Baseline

The following tracked dependencies are immutable inputs:

| Dependency | SHA-256 |
|---|---|
| dataset builder | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| candidate builder | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| feature/label builder | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| corpus builder | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |

Fresh cache-disabled verification at this baseline is `66 passed` focused and `2519 passed` full.
Any dependency drift is a STOP condition.

## 5. Existing Private Evidence Boundary

The existing accepted calendar intake remains immutable at:

`private_data/sierra_chart/gc_calendar_20260804_raw_intake/`

Its manifest, README, and latest acquisition checkpoint hashes remain:

- `684F9EAAEAB41BFC4D09C4E4FE7E4B7672D5B246A3F9F251656A8D07068A0575`;
- `BA537533C46E082144973FC50D2385DB5F3E374B352848BB1F650EEEF1312721`;
- `8F3BBAFFE2D1A3996E597EE67745B996F5CB1FB07246332F717A067E0A12C6EA`.

This proposal does not reinterpret, rewrite, or supersede those bytes.

## 6. Existing Normalization Finding

`normalization_audit_checkpoint_20260808.md` correctly stopped full normalization. It proved the
two exceptional Thanksgiving split sessions but lacked an accepted general Globex trade-date rule
for assigning ordinary post-maintenance and post-holiday evening sessions.

The header-only `normalization_draft.csv` remains non-evidence. No row may be promoted from that
file until the later acquisition and normalization procedure passes independently.

## 7. Official Primary Source Candidate

The only new evidence candidate is the official CME Globex Reference Guide:

- title: `CME Globex Reference Guide`;
- publisher: `CME Group`;
- canonical retrieval URL:
  `https://www.cmegroup.com/content/dam/cmegroup/globex/files/GlobexRefGd.pdf`;
- required proposition: Globex afternoon/evening sessions mark the beginning of the next trading
  day, including the stated Sunday-evening-to-Monday example.

The URL and search excerpt are discovery evidence only. They are not accepted bytes and cannot be
used by a runtime or normalization job.

## 8. Future Immutable Acquisition Contract

A later separately authorized private acquisition must:

1. retrieve the PDF directly from the exact CME HTTPS URL;
2. record retrieval timestamp in UTC, final resolved URL, HTTP status, media type, byte count, and
   SHA-256;
3. store the unmodified bytes under the existing private calendar intake root with a collision-safe
   filename;
4. add exactly one manifest row with a unique source-artifact ID;
5. update the private README and acquisition checkpoint without rewriting prior rows;
6. independently rehash all accepted calendar artifacts.

Redirect to a non-CME host, HTML error body, authentication interstitial, empty bytes, or mutable
in-place replacement is `INVALID`.

## 9. Source-Role Boundary

The Reference Guide may establish only the general trade-date transition rule. It may not supply
GC-specific holiday close, halt, reopen, split-session, or closed-state times.

Those exceptional times remain sourced only from the accepted CME holiday workbooks and the
authenticated GCC case `04687271` EML records. A normalized row must cite both the general-rule
artifact and every applicable exceptional artifact.

## 10. Exact Development Calendar Scope

Normalization for the independent pretraining attempt is limited to requested trade dates inside:

- TRAIN `[2024-11-04, 2025-06-02)`;
- VALIDATION `[2025-06-16, 2025-08-25)`;
- CALIBRATION `[2025-09-08, 2025-11-24)`.

Excluded gaps, embargo intervals, and the sealed FINAL_OOS interval are not added merely to make a
continuous calendar. No 2026 production-session row is required for this development-only build.

## 11. 2026 Saturday Finding Isolation

The unresolved 2026 Juneteenth and Independence Day Saturday internal-testing entries remain
unresolved evidence. They do not block the exact 2024-2025 development partitions in Section 10.

They remain a STOP condition for any future 2026 calendar, OOS, paper, live, or broader historical
promotion. This scope isolation must not be represented as a semantic resolution of those events.

## 12. Ordinary Session Rule

For an eligible business trade date without an accepted exception, the source-local GC session is:

- open: prior eligible calendar day at `18:00:00 America/New_York`;
- close: trade date at `17:00:00 America/New_York`;
- maintenance interval: `[17:00:00, 18:00:00)`;
- trade date: the trading day begun by the preceding afternoon/evening open.

This rule becomes admissible only after the Reference Guide bytes and the accepted GCC statement
of standard GC operating hours are both manifest-bound. Weekday inference alone is forbidden.

## 13. Exceptional Session Rule

An accepted GC-specific holiday record overrides ordinary interval geometry only for the exact
covered date. Exact early halt, early close, closed state, reopen, and split-session times are
preserved without rounding or analogy.

An evening reopen begins the next eligible trading day unless the accepted GC-specific evidence
explicitly binds a same-trade-date split session. The two already proven Thanksgiving split rows
remain exact and unchanged.

## 14. Closed-Date Rule

For an accepted `Closed` state:

- no GC trading occurs after the stated close;
- the next accepted `18:00 ET` reopen begins the next eligible business trade date;
- no synthetic zero-volume session is emitted for a non-trading date;
- source lineage must include the GCC closed-date clarification and the general trade-date rule.

Missing reopen time or conflicting business-date assignment returns `UNKNOWN` or `INVALID` under
the existing precedence; it is never filled from neighboring rows.

## 15. Timezone and Version Contract

All source-local moments use IANA `America/New_York` and are converted through the runtime timezone
database. The normalized artifact records the exact runtime tzdata version and rejects a consumer
whose normalized version differs.

Naive timestamps, fixed-offset substitutes, ambiguous local moments without a deterministic fold,
nonexistent local moments, or conversion exceptions fail closed. UTC ordering is checked after
conversion without changing the source-local evidence.

## 16. Normalized Row Contract

Each requested trade date has exactly one immutable row containing:

- deterministic nonempty `calendar_version`;
- `trade_date`;
- session status;
- one or more ordered start-inclusive/end-exclusive UTC intervals;
- maintenance and no-trade gaps where applicable;
- ordered source-artifact IDs and SHA-256 values;
- timezone name and tzdata version;
- review status and exact exclusion or blocking reasons.

Rows are strictly ordered by trade date. No silent sort, deduplication, repair, enrichment, or
filesystem-order dependence is allowed.

## 17. Coverage and Conservation

Every requested development trade date must resolve to exactly one eligible, closed, or explicitly
excluded row. Each admitted source bar must map to exactly one interval and one trade date. Bars in
maintenance, attested no-trade gaps, closed periods, or unrequested dates are rejected or excluded
with exact reasons.

Row counts, source-bar counts, interval counts, exclusions, and integer volumes must reconcile
before a `GCDatasetBuildResult` can be promoted.

## 18. OOS and Contamination Boundary

The sealed OOS payload remains unopened. Only its committed manifest metadata and zero access
counters may be checked. No 2026 full export may be used to infer calendar geometry, repair missing
development rows, inspect outcomes, or reconstruct the sealed interval.

Closed Phase A/B artifacts remain negative or insufficient evidence and cannot seed, cache, repair,
or configure this normalization.

## 19. Atomic Future Procedure

After separate exact authorization, the future operation must execute atomically:

1. acquire and manifest-bind the official Reference Guide;
2. independently audit its bytes and proposition;
3. normalize only the Section 10 development calendar from accepted sources;
4. independently validate every row, ordering rule, lineage, timezone conversion, and coverage;
5. publish the normalized artifact only after complete PASS;
6. stop before dataset build for a new preflight against the committed corpus-run proposal.

No partial normalized artifact is accepted. A failure leaves prior raw evidence immutable and the
new evidence quarantined.

## 20. Status and Authority

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Even a `VALID` normalized development calendar grants no dataset, candidate, feature/label,
corpus, training, OOS, integration, or trading authority. It clears one upstream evidence gate
only.

## 21. Exact 40-Case Verification Matrix

1. Exact repository baseline reconciles.
2. Governing proposal path and hash reconcile.
3. Four tracked builder hashes reconcile.
4. Existing private manifest, README, and checkpoint hashes reconcile.
5. Existing raw artifacts remain byte-identical.
6. Header-only normalization draft is not promoted.
7. Reference Guide is retrieved only from the exact CME HTTPS URL.
8. Final resolved host remains an accepted CME host.
9. HTTP failure, empty body, or non-PDF body fails closed.
10. Retrieved bytes receive immutable size and SHA-256 evidence.
11. One additive manifest row has a unique artifact ID.
12. General trade-date rule is extracted without extending its scope.
13. GCC standard GC hours remain the product-specific ordinary-hours source.
14. Holiday workbooks and EML records remain the exceptional-time sources.
15. TRAIN requested dates are exact and half-open.
16. VALIDATION requested dates are exact and half-open.
17. CALIBRATION requested dates are exact and half-open.
18. Excluded gaps and embargo dates are not silently requested.
19. FINAL_OOS payload is never opened.
20. 2026 Saturday ambiguity remains isolated and unresolved.
21. Ordinary evening open begins the next trading day.
22. Ordinary maintenance interval is excluded.
23. Accepted early halt or close overrides ordinary close exactly.
24. Accepted evening reopen changes trade date under the general rule.
25. Explicit same-trade-date split evidence overrides the general rule locally.
26. Both proven Thanksgiving split sessions remain exact.
27. Closed dates emit no synthetic trading interval.
28. Missing exceptional evidence returns UNKNOWN with no promotion.
29. Contradictory evidence returns INVALID over UNKNOWN.
30. America/New_York conversion is exact across DST regimes.
31. Runtime tzdata mismatch fails closed.
32. Every row preserves complete ordered source lineage.
33. Rows are strictly ordered without silent sorting.
34. Each source bar maps to at most one interval and trade date.
35. Maintenance, closed, and no-trade-gap bars cannot be admitted.
36. Counts and integer volume conserve exactly.
37. Partial normalization cannot be published.
38. A VALID calendar grants no downstream or trading authority.
39. Exact one-file scope and unrelated user state remain intact.
40. Formatting, hash, full-content, cached-diff, rollback, and commit audits pass.

## 22. Promotion Gates

This document may receive exact-path staging and one local documentation commit after independent
semantic, structural, hash, formatting, scope, and regression audit. Push requires separate exact
GitHub export authorization.

After verified push, a later exact private acquisition authorization must name the CME URL, the
existing private intake root, the additive manifest procedure, and the STOP-before-dataset boundary.
Only a separately accepted normalized calendar can reach the corpus proposal preflight.

## 23. Rollback and Stop Conditions

Before commit, rollback is deletion of this one new proposal only. After commit, rollback is a
normal forward revert of the exact commit, never a destructive reset. Existing private evidence,
tracked code, tests, and unrelated untracked files remain untouched.

STOP on dependency drift, non-CME resolution, uncertain bytes, missing product scope, incomplete
trade-date coverage, contradictory time, unsupported 2026 interpretation, timezone mismatch,
ordering error, conservation failure, OOS access, scope expansion, partial promotion, training,
integration, or trading authority.

## 24. Final Decision and Resume Boundary

The official primary source makes the calendar blocker prospectively resolvable, but no evidence
has yet been acquired or normalized under this contract. The correct current state is:

`CALENDAR_EVIDENCE_RESOLUTION_PROPOSED_NO_PRIVATE_MUTATION_NO_DATASET_NO_TRAINING_NO_OOS`.

After this exact document passes audit and local commit, work must STOP before push. Following an
exact authorized push and post-push audit, one bounded private acquisition-and-normalization task
may be considered. All downstream build, training, OOS, integration, and trading surfaces remain
frozen.
