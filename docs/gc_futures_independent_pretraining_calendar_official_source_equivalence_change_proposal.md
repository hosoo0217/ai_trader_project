# GC Futures Independent Pretraining Calendar Official Source Equivalence Change Proposal

## 1. Proposal Record

- Proposal date: `2026-08-25`.
- Local repository baseline: `fbf06ac0796a46b74c5aa3e730371443cd8bba1d`.
- Baseline parent published on `origin/main`:
  `0aa93e5cc3e4ef726fbde811fc48e49055157b85`.
- Decision:
  `DOCUMENTATION_ONLY_ACCEPT_COMBINED_OFFICIAL_CME_SOURCE_EQUIVALENCE_FOR_LATER_PRIVATE_ACQUISITION_NO_EXECUTION`.
- Authority granted: documentation-only source-equivalence design authority.
- Global code freeze: active outside this exact document.

This proposal defines a narrow replacement for the unavailable historical CME Globex Reference
Guide. It does not acquire web bytes, mutate private evidence, normalize a calendar, build a
dataset, create features or labels, train a model, access OOS, integrate code, or authorize trading.

## 2. Exact Scope

The only path created by this task is:

- `docs/gc_futures_independent_pretraining_calendar_official_source_equivalence_change_proposal.md`.

No Python, tests, fixtures, private artifacts, manifests, calendar rows, package exports,
configuration, integration, or other documentation may change. The three pre-existing unrelated
untracked documents remain outside scope and must not be opened, edited, staged, or committed.

## 3. Governing Records

This proposal is subordinate to and must reconcile with:

- `docs/gc_futures_independent_pretraining_calendar_evidence_resolution_change_proposal.md`,
  SHA-256 `E51DBD41F77C221B68D0F3DF0E4C3209149A0571F75F16F7E264A30BA13601EC`;
- `docs/gc_futures_independent_pretraining_calendar_evidence_resolution_negative_outcome_decision.md`,
  SHA-256 `8D62454A0C9BA07A0FE7FBB7A06A047A61B9AE9AA687C4915720CB88CF20FBE2`;
- `docs/gc_futures_independent_pretraining_corpus_private_run_change_proposal.md`,
  SHA-256 `90C05E3CD296C9447CDE4778B8BED8EECB2FC4F4D14F45B881F0B7DFB6D48CDC`.

The negative outcome remains historically true: the locked Reference Guide PDF was not acquired.
This proposal does not rewrite that outcome. It establishes a separately reviewed replacement
source chain for a later bounded private operation.

## 4. Immutable Tracked Dependencies

The following tracked inputs must remain byte-identical:

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_feature_label_builder.py` | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `analysis/gc_pretraining_corpus.py` | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |

Any drift is a STOP condition. This proposal grants no implementation change to those files.

Fresh cache-disabled regression evidence at this proposal baseline is:

- focused `tests/test_gc_pretraining_corpus.py`: `66 passed in 0.57s`;
- full `tests`: `2519 passed in 23.66s`.

## 5. Existing Private Evidence Boundary

The accepted private intake remains immutable at:

`private_data/sierra_chart/gc_calendar_20260804_raw_intake/`

Its control artifacts remain:

| Artifact | SHA-256 |
|---|---|
| `raw_artifact_manifest.csv` | `684F9EAAEAB41BFC4D09C4E4FE7E4B7672D5B246A3F9F251656A8D07068A0575` |
| `README.md` | `BA537533C46E082144973FC50D2385DB5F3E374B352848BB1F650EEEF1312721` |
| `acquisition_checkpoint_20260808.md` | `8F3BBAFFE2D1A3996E597EE67745B996F5CB1FB07246332F717A067E0A12C6EA` |
| `normalization_audit_checkpoint_20260808.md` | `4BE171CA54A647EAE3DF6BD358F63319AD13AC8E17F66FC3EE0288EB3869E6AF` |
| `normalization_draft.csv` | `A68372E7D556C665F66F0C90700F15BC1AD248A05D23247F27B3F2DF15314884` |

The header-only normalization draft remains non-evidence. No private file changes in this task.

## 6. Authenticated GCC Evidence

The following original EML files are accepted product-specific evidence:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `CME_GCC_case_04687271_historical_GC_schedule_20260805.eml` | 289129 | `867CA4472E96D128AFADB0238A1F62C26C66EF97B8E456E3395788223AE0DB34` |
| `CME_GCC_case_04687271_clarification_20260806.eml` | 128570 | `DC21CA057A0CACEC3EE1455221455A160C78A37F16234BBA7CDD0B4FAF8C5FA1` |
| `CME_GCC_case_04687271_final_clarification_20260807.eml` | 138143 | `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2` |

The messages identify CME Global Command Center as sender, case `04687271`, COMEX Gold Futures
`GC`, and Eastern Time. Their original bytes, headers, quoted thread history, and body remain
immutable; extracted text is not a replacement artifact.

## 7. GCC Product-Specific Propositions

The accepted EML evidence establishes:

- ordinary electronic GC hours are Sunday `18:00 ET` through Friday `17:00 ET`;
- the daily maintenance break is `17:00-18:00 ET`;
- for a `Closed` state there is no GC trading after close;
- a closed-state `18:00 ET` reopen belongs to the next eligible business trade date;
- exact holiday, early-halt, early-close, reopen, and split-session facts are event-specific;
- the final clarification supplies exact Thanksgiving 2024 and 2025 exceptional sequences.

Only those propositions stated in the accepted messages may be used. Contradictory quoted thread
text is resolved only by a later explicit answer in the same authenticated case, never by guess.

## 8. Official CME Replacement Source

The replacement source candidate is the official CME notice:

- title: `CME Reference Data API Enhancements February 5`;
- notice ID: `20230202`;
- notice date: `2023-02-02`;
- canonical URL:
  `https://www.cmegroup.com/notices/reference-data-api/2023/20230202.html`;
- publisher: `CME Group`;
- required attributes: `exchBusinessDate`, `Exchange business date`;
- required rule: before `16:00 America/Chicago` the current exchange business date applies and
  after `16:00 America/Chicago` the next exchange business date applies;
- required example: effective Sunday February 5, trade date Monday February 6.

The current web page and browser rendering are discovery evidence only until immutable bytes are
acquired under Section 12.

## 9. Exact Equivalence Proof

The replacement is a combined-source proof, not a claim that either source is sufficient alone:

1. the official notice names `exchBusinessDate` as the exchange business date;
2. it states that moments after `16:00 CT` carry the next exchange business date;
3. it expressly pairs a Sunday effective date with the following Monday trade date;
4. the authenticated GCC evidence fixes the ordinary GC reopen at `18:00 ET`;
5. New York is exactly one civil hour ahead of Chicago for these IANA zones, including their
   coordinated DST regimes, so `18:00 ET` is `17:00 CT`;
6. `17:00 CT` is strictly after the notice's `16:00 CT` boundary;
7. therefore an ordinary GC `18:00 ET` reopen carries the next exchange business/trade date.

This inference is accepted only for the ordinary trade-date transition. It is not an independent
source for GC hours or holiday geometry.

## 10. Semantic Non-Overreach Boundary

The official notice may establish only the general exchange-business-date transition. It may not
establish GC product hours, maintenance, holiday eligibility, early halt, early close, closed
state, reopen time, split-session continuity, or specific holiday trade date.

The GCC EML records and accepted CME holiday workbooks remain mandatory for those product-specific
facts. Each normalized row must cite the notice artifact plus every applicable product-specific
artifact. Missing either source role is `UNKNOWN`; contradiction between accepted roles is
`INVALID`.

## 11. Timezone Equivalence Contract

The one-hour ET/CT relation must be computed with IANA `America/New_York` and `America/Chicago`,
not fixed offsets or abbreviations. For each source-local instant used in the proof:

- both zones must resolve through the same runtime timezone database version;
- the resulting UTC instants must prove the exact one-hour difference;
- ambiguous/nonexistent local moments, unavailable zones, version mismatch, or conversion
  exception fail closed;
- no daylight-saving rule may be copied from a neighboring year.

The normalized artifact records the exact runtime tzdata version.

## 12. Future Immutable Web Acquisition

A later separately authorized private task must acquire the official notice as immutable evidence:

1. retrieve only the exact CME HTTPS URL in Section 8;
2. record UTC retrieval time, requested URL, final URL, status, media type, byte count, and SHA-256;
3. preserve the unmodified response bytes under the existing private intake root using a
   collision-safe filename;
4. verify that the acquired body contains the notice ID, notice date, `exchBusinessDate`, both
   `16:00 CT` branches, and the Sunday/Monday trade-date example;
5. add one unique manifest row and append-only README/checkpoint evidence;
6. independently rehash every accepted control artifact.

Redirect outside an accepted CME host, error/interstitial body, missing proposition, empty bytes,
silent replacement, or non-additive manifest mutation is `INVALID`.

## 13. Exact Development Calendar Scope

The later normalization remains limited to requested trade dates in:

- TRAIN `[2024-11-04, 2025-06-02)`;
- VALIDATION `[2025-06-16, 2025-08-25)`;
- CALIBRATION `[2025-09-08, 2025-11-24)`.

Excluded gaps, embargoes, and FINAL_OOS are not normalized to create artificial continuity. The
unresolved 2026 Saturday internal-testing entries remain excluded and unresolved.

## 14. Ordinary Session Rule

For an eligible business trade date without an accepted exception:

- open: preceding eligible calendar day `18:00:00 America/New_York`, inclusive;
- close: trade date `17:00:00 America/New_York`, exclusive;
- maintenance: `[17:00:00, 18:00:00)`;
- assigned trade date: the next exchange business date carried by the preceding `18:00 ET` open.

This rule is admissible only after both the official notice bytes and authenticated GCC standard
hours are manifest-bound. Calendar arithmetic or observed bars alone is forbidden.

## 15. Exceptional and Closed Session Rules

An accepted GC-specific holiday fact overrides ordinary geometry only for its exact covered event.
Exact early halt, early close, pre-open, reopen, same-trade-date split, and final close remain
unaltered. The accepted Thanksgiving 2024/2025 clarifications take precedence over earlier
ambiguous summaries within the same case.

For a closed date, emit no synthetic trading interval. The next accepted `18:00 ET` reopen begins
the next eligible business trade date unless explicit accepted evidence proves a same-trade-date
split. Missing or conflicting exceptional evidence fails closed.

## 16. Normalized Row and Lineage Contract

Each requested trade date must produce exactly one immutable row with:

- nonempty deterministic calendar version and trade date;
- eligible, closed, or explicitly excluded status;
- ordered start-inclusive/end-exclusive UTC intervals;
- maintenance and attested no-trade gaps;
- ordered source IDs, SHA-256 values, source roles, and proposition identifiers;
- both IANA zones and the exact tzdata version used for equivalence;
- review status and exact blocking/exclusion reasons.

Rows are strictly ordered by trade date. Silent sorting, deduplication, repair, inference from file
order, retroactive enrichment, or source-role substitution is forbidden.

## 17. Coverage, Integrity, and Conservation

Every requested development trade date resolves exactly once. Every admitted source bar maps to
exactly one interval and one trade date. Bars in maintenance, closed intervals, attested no-trade
gaps, unrequested dates, embargoes, or FINAL_OOS are rejected or excluded with exact reasons.

Row counts, interval counts, source-bar counts, exclusions, and integer volumes must reconcile.
Partial coverage, overlapping intervals, orphan lineage, duplicate trade dates, or volume drift
prevents promotion.

## 18. Status Precedence and Atomicity

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The later private task is atomic: acquisition, manifest binding, equivalence audit, normalization,
and row audit must all pass before publication. A failing group and all later evidence are not
promoted; strictly prior accepted raw evidence remains byte-identical. `VALID` grants only a
calendar-evidence gate, no downstream authority.

## 19. Prefix Invariance and No Look-Ahead

A strictly later complete source append must not change earlier normalized rows or identities.
Same-effective append, historical insertion, reordered evidence, replacement bytes, repaired
quoted text, tzdata mutation, or changed source priority is not a prefix extension and requires a
new full audit.

The sealed OOS payload remains unopened. No observed 2026 bars, outcomes, future holiday schedule,
or later model result may infer or repair 2024-2025 calendar facts.

## 20. Exact 44-Case Verification Matrix

1. Local baseline and published parent reconcile exactly.
2. Governing proposal and negative-decision hashes reconcile.
3. Corpus private-run proposal hash reconciles.
4. Four tracked builder hashes reconcile.
5. Private control-artifact hashes remain exact.
6. Three authenticated GCC EML filenames, sizes, and hashes reconcile.
7. EML sender, case, product, timezone, and subject are present.
8. GCC ordinary open is exactly `18:00 ET`.
9. GCC ordinary close is exactly `17:00 ET`.
10. GCC daily maintenance is exactly `[17:00,18:00) ET`.
11. Closed-state no-trading proposition is preserved.
12. Closed-state reopen-to-next-business-trade-date proposition is preserved.
13. Official URL, notice ID, date, and publisher reconcile.
14. `exchBusinessDate` definition is present in acquired bytes.
15. Before-`16:00 CT` current-date rule is present.
16. After-`16:00 CT` next-date rule is present.
17. Sunday-effective/Monday-trade-date example is present.
18. Acquired response remains on an accepted CME host.
19. Error, interstitial, empty, or incomplete body fails closed.
20. Response metadata, byte count, and SHA-256 are immutable.
21. One unique additive manifest row is created.
22. `18:00 ET` converts exactly to `17:00 CT` under IANA zones.
23. Conversion uses one exact runtime tzdata version.
24. `17:00 CT` is strictly after the `16:00 CT` boundary.
25. Combined proof assigns ordinary reopen to the next exchange business date.
26. Notice is not used as a GC product-hours source.
27. GCC evidence is not used as a general cross-product rule.
28. Holiday workbook/EML evidence remains mandatory for exceptions.
29. Exact Thanksgiving split sessions remain unchanged.
30. Closed dates emit no synthetic trading interval.
31. TRAIN interval is exact and half-open.
32. VALIDATION interval is exact and half-open.
33. CALIBRATION interval is exact and half-open.
34. Excluded gaps, embargoes, and FINAL_OOS remain excluded.
35. 2026 Saturday ambiguity remains unresolved and isolated.
36. Each normalized row carries complete ordered source-role lineage.
37. Rows are unique and strictly ordered without silent sort.
38. Each source bar maps to at most one interval and trade date.
39. Counts and integer volume conserve exactly.
40. Missing source role yields UNKNOWN with no partial promotion.
41. Contradictory accepted evidence yields INVALID over UNKNOWN.
42. Strictly later complete append preserves prior row bytes and identities.
43. No dataset, feature/label, training, OOS, integration, or trading authority is granted.
44. Exact one-file scope, formatting, hashes, cached diff, rollback, and commit audits pass.

## 21. Future Atomic Procedure

After separate exact authorization, the only permitted private procedure is:

1. preflight repository and private control hashes;
2. acquire and manifest-bind the official notice bytes;
3. independently validate the exact propositions and combined-source proof;
4. normalize only the Section 13 development calendar;
5. independently validate lineage, ordering, timezone conversion, coverage, and conservation;
6. publish the normalized artifact only on complete PASS;
7. STOP before dataset or corpus build.

No partial normalized artifact may be accepted or reused.

## 22. Promotion Gates

This document may receive exact-path staging and one local documentation commit only after
semantic, structural, source, hash, formatting, scope, and regression audits pass. Push requires
separate exact GitHub export authorization.

After a verified push, the private operation in Section 21 still requires separate exact authority.
Only a separately audited normalized calendar may return to the corpus proposal preflight.

## 23. Rollback and Stop Conditions

Before commit, rollback is deletion of this one new file. After commit, rollback is a normal
forward revert of the exact commit, never a destructive reset. Existing private and unrelated
worktree evidence remains untouched.

STOP on dependency drift, unavailable or changed official bytes, non-CME resolution, missing
notice proposition, uncertain `exchBusinessDate` semantics, failed ET/CT reconciliation,
unsupported product or year scope, source contradiction, incomplete calendar coverage, timezone
version mismatch, ordering or conservation failure, OOS access, dataset/feature/label build,
training, integration, partial promotion, or trading authority.

## 24. Final Decision and Resume Boundary

The combined official source chain is semantically sufficient for a later bounded acquisition and
development-calendar normalization task, but no private execution has occurred. The exact current
state is:

`OFFICIAL_SOURCE_EQUIVALENCE_PROPOSED_NO_PRIVATE_MUTATION_NO_NORMALIZATION_NO_DOWNSTREAM_AUTHORITY`.

After this exact document passes audit and local commit, work must STOP before push. No private
acquisition, normalization, dataset build, training, OOS, integration, or trading operation is
authorized by this record.
