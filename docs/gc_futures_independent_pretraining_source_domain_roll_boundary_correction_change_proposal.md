# GC Futures Independent Pretraining Source-Domain and Roll-Boundary Correction Change Proposal

## 1. Proposal Record

- Date: `2026-08-25`.
- Capability: development-only GC independent-pretraining dataset boundary correction.
- Proposal status: `PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED`.
- Decision: `READY_FOR_INDEPENDENT_DOCUMENT_AUDIT_ONLY`.
- Authority: documentation-only; no private rerun, dataset/corpus publication, feature/label build,
  training, final-OOS access, integration, or trading.

This record locks the minimum fail-closed correction required after the corrected dual-calendar
private transaction stopped at the dataset gate. It does not authorize suppressing a diagnostic,
filtering private input outside the builder, weakening calendar validation, or inventing missing
contract evidence.

## 2. Exact Documentation Scope

This task may create only:

- `docs/gc_futures_independent_pretraining_source_domain_roll_boundary_correction_change_proposal.md`.

No Python, test, fixture, package export, private source, normalized calendar, transaction artifact,
manifest, configuration, integration file, or existing documentation file may change. The three
pre-existing user-owned untracked proposals remain untouched.

## 3. Governing Baseline

The proposal is based on:

- `HEAD` and local `origin/main`:
  `0c4c020e4a78d82c29ff0ab91e3273cabcee7234`;
- subject: `docs: propose dual-calendar pretraining projection correction`;
- atomic upstream proposal SHA-256:
  `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44`;
- calendar-adapter proposal SHA-256:
  `11DC4FF7521A20FA414779C3BC6296B1AE533F828484AF1208E1D61379EAE4A0`;
- dual-calendar proposal SHA-256:
  `EE08ACF33E4BE57D42E5242EC771B0CCD56CBDA1FF062E219334C88873A2E1AA`;
- post-calendar readiness decision SHA-256:
  `AD736DDC448AB79B53FC6A71DCC12691FCE3133E18F7F9B4AD867703CF2BD956`.

Earlier records remain authoritative except where this proposal explicitly corrects dataset source
domain and finite roll-observation boundaries.

## 4. Failed Corrected Transaction Evidence

The separately authorized corrected two-run transaction stopped during Run A at
`build_gc_futures_dataset()` with `GCDatasetBuildStatus.UNKNOWN`. The repeated blocking reason was
`CALENDAR_COVERAGE_MISSING`; the result also exposed initial-predecessor and comparable-volume
boundary warnings. No Run B, `.accepted_pending`, accepted output, candidate evidence,
feature/label result, corpus, training, OOS access, or integration occurred.

The failed root contained zero files and five empty directories, had no reparse point, and was
removed only after a guarded empty-root rollback. The private transaction root is now absent. This
proposal does not reclassify that failed run as successful and does not reuse an object or byte from
it.

## 5. Root-Cause Split

Two independent issues are locked:

1. `analysis/gc_dataset_builder.py` attempts calendar matching before applying outer-boundary
   exclusions. Raw bars wholly before or after the accepted normalized calendar domain therefore
   become `CALENDAR_COVERAGE_MISSING` instead of conserved exclusions.
2. The attempted five-contract transaction does not bracket an independently provable continuous
   roll window: its first configured contract has no predecessor and its final active contract can
   lack an adjacent observation. This is a transaction binding defect, not authority to weaken roll
   validation.

Fixing only the first issue is insufficient. Hiding either issue by pre-filtering raw files,
fabricating contracts, or treating missing in-domain evidence as an exclusion is forbidden.

## 6. Immutable Inputs and Dependency Hashes

The correction is bound to these private control hashes:

- intake manifest:
  `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`;
- raw-intake README:
  `63AFFCACF182C0987D28A1C6361E48D6FC0E59D0D0DAC71763097C92E3D0950F`;
- acquisition checkpoint:
  `59B1AB12BFDDDAD7DBAF5E3375DBA19C0F342EAD1E475AFE23E3D75676E89CED`;
- calendar input binding:
  `493BC80D1991E0FAC505DC9675A7D2E795B2B7BFCB179CE3287A0930843756FC`;
- normalized calendar:
  `EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED`;
- normalization result:
  `90E96A017977CB0A2429F5315C8086CDBB6A3F108B87C6AAA8928AFD5D6AEA5B`;
- calendar two-run reproducibility:
  `5EF688CEE702CE2F9D01C64945FB7DFD6C96B63E57C19F9A55FF3EE9C6348B55`.

Any byte, version, source registry, timezone, or calendar drift is a STOP condition.

## 7. Exact Raw Source and Calendar Domain Evidence

The five immutable sources contain `129,503` rows and integer volume `43,716,706`. Their accepted
calendar outer domain is exactly:

`[2024-11-03T23:00:00Z, 2025-11-21T22:00:00Z)`.

The normalized calendar version is
`GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`, timezone data version `2026.2`, with
`255` rows, `252` trading intervals, and partition counts `150/50/55`.

| Source | Raw rows | Raw volume | Before-domain rows / volume | In-domain rows / volume | After-domain rows / volume |
| --- | ---: | ---: | ---: | ---: | ---: |
| `GCJ25` | 25,126 | 6,595,620 | 462 / 1,691 | 24,664 / 6,593,929 | 0 / 0 |
| `GCM25` | 25,712 | 9,713,851 | 0 / 0 | 25,712 / 9,713,851 | 0 / 0 |
| `GCQ25` | 26,093 | 7,597,945 | 0 / 0 | 26,093 / 7,597,945 | 0 / 0 |
| `GCV25` | 23,472 | 469,145 | 0 / 0 | 23,472 / 469,145 | 0 / 0 |
| `GCZ25` | 29,100 | 19,340,145 | 0 / 0 | 27,772 / 19,111,311 | 1,328 / 228,834 |
| **Total** | **129,503** | **43,716,706** | **462 / 1,691** | **127,713 / 43,486,181** | **1,328 / 228,834** |

There are zero boundary-straddling rows. These counts are read-only evidence, not an authorized
private transformation.

## 8. Canonical Outer Domain Derivation

The builder derives one immutable outer domain from the validated ordered dataset calendar before
classifying source rows:

- `domain_start` is the minimum inclusive start across every validated trading interval;
- `domain_end` is the maximum exclusive end across every validated trading interval;
- closed rows contribute no endpoint;
- empty, naive, non-UTC-normalizable, reversed, overlapping, unordered, or version-inconsistent
  calendar evidence is `INVALID` before a source row is promoted.

The domain is not inferred from raw-source minima/maxima, labels, detector outputs, partitions,
candidate counts, or outcomes.

## 9. Exact Source-Row Classification

After strict parsing and before trade-date calendar lookup, every fully closed source bar is
classified exactly once:

- `bar_close <= domain_start` -> exclusion reason `BEFORE_CALENDAR_DOMAIN`;
- `bar_start >= domain_end` -> exclusion reason `AFTER_CALENDAR_DOMAIN`;
- `bar_start < domain_start < bar_close` or `bar_start < domain_end < bar_close` -> `INVALID` with
  `CALENDAR_DOMAIN_BOUNDARY_STRADDLE`;
- otherwise -> unchanged existing calendar lookup and session validation.

Equality is unambiguous because source bars are start-inclusive/end-exclusive. Boolean, fractional,
non-finite, naive, reversed, duplicate, unordered, or malformed bar evidence remains fail-closed and
cannot be converted into an outer-domain exclusion.

## 10. Calendar Validation Preservation

Outer-domain classification does not weaken in-domain calendar rules. Every in-domain row must
still reconcile to exactly one accepted calendar interval and trade date. A gap, maintenance bar,
closed-session bar, mismatched exchange date, missing in-domain calendar row, split-session mismatch,
or timezone/version conflict remains `UNKNOWN` or `INVALID` under the committed semantics.

`CALENDAR_COVERAGE_MISSING` remains valid for an in-domain moment that lacks trustworthy calendar
coverage. It may not be replaced by an outer-domain exclusion.

## 11. Exact Conservation and Audit Evidence

The builder continues parsing the complete immutable source bytes. It must prove:

- `raw_rows = eligible_rows + excluded_rows`;
- `raw_volume = eligible_volume + excluded_volume`;
- the ordered exclusion ledger reconciles to exact source artifact, source row, timestamps, volume,
  and one reason token;
- `BEFORE_CALENDAR_DOMAIN` and `AFTER_CALENDAR_DOMAIN` counts/volumes reconcile to Section 7;
- no external filtered export, rewritten CSV, or unbound derivative source is accepted.

All source rows and integer volume remain identity-bearing. This is deterministic exclusion, not
silent deletion.

## 12. No Unproved Initial-Contract Bootstrap

The existing initial-contract proof remains mandatory. The configured initial contract must have
its canonical predecessor in the supplied registry and must exceed that predecessor's complete
session volume on each of the exact three eligible sessions immediately before the configured
initial trade date. The initial contract itself must have complete source/calendar coverage on the
initial date.

Missing predecessor evidence, fewer than three prior eligible calendar sessions, incomplete volume,
or a dominance contradiction remains `UNKNOWN` or `INVALID`. “The configured contract is probably
active,” delivery-month convention, later volume, price continuity, or absence of a predecessor file
is not proof. No bootstrap or left-censor reason token is introduced.

## 13. Deterministic Admissible Start Selection

Before a later private transaction, a read-only preflight enumerates only canonical contract/date
pairs already supported by immutable source and calendar bytes. A pair is start-admissible exactly
when it passes Section 12 under the unchanged public builder contract. The transaction selects the
earliest admissible trade date and, on an exact date tie, the canonical delivery-order contract.

The selected `initial_contract` and `initial_trade_date`, all rejected pair reason tokens, source
registry digest, and calendar digest are transaction-bound before Run A. No candidate, detector,
feature, label, partition result, PnL, or OOS evidence may influence selection. If zero or multiple
non-tie-resolvable starts exist, STOP.

## 14. Complete Finite Registry and Adjacent Coverage

For every eligible session from the selected start through the configured end, the active contract
and its canonical adjacent contract must both have complete, trusted, fully closed same-trade-date
volume. Zero is valid integer volume; missing, partial, malformed, negative, or cross-date volume is
not comparable.

The corrected transaction may expand the private development registry only with already acquired,
manifest-bound canonical full-contract sources. At minimum, terminal coverage must be tested with
the existing canonical `GCG26` source SHA-256
`FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` and, if `GCG26` can become
active before the end, the canonical `GCJ26` source SHA-256
`B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85`.

The exact minimal registry is determined before Run A by complete roll-proof coverage, not by
candidate output. Any newly bound source retains full raw-byte conservation and Section 9 outer
domain classification.

## 15. Normal Observable Roll Semantics

Across the entire admissible window, the existing locked roll semantics remain unchanged:

- compare complete active and adjacent session volumes on the same trade date;
- update the configured consecutive-dominance state deterministically;
- roll only at the exact precommitted confirmation boundary;
- reset the streak after a roll and advance only to the canonical next contract;
- preserve immutable earlier contract assignments and roll evidence.

Missing comparable volume, a skipped contract, nonconsecutive date, duplicate
volume, registry reorder, or conflicting roll evidence is `UNKNOWN` or `INVALID`; it cannot revert to
an inferred or censored comparison.

## 16. Exact Terminal Coverage and No Right Censor

The configured end is admissible only when Section 14 comparable coverage exists for every session
through that end. The end may be shortened only to the latest eligible date before the first
unresolvable comparable-coverage gap, and only if the resulting TRAIN/VALIDATION/CALIBRATION corpus
contract remains satisfiable. The shortened date and excluded calendar suffix are bound before
Run A and remain in the transaction audit.

If the accepted corpus partition contract requires dates beyond that boundary, STOP and acquire the
missing canonical adjacent source; do not shorten silently. There is no terminal right-censor reason
token, no assumption that the active contract remains economically correct, and no claim beyond the
last fully proved session.

## 17. Deterministic Version, Identity, and Status

The source-domain implementation requires a dataset algorithm/version increment. Dataset identity and manifest
evidence bind the new version, immutable source registry, all raw source hashes, calendar/projection
digests, configured initial contract/date, exact domain endpoints, exclusion ledger, and roll plan.

Public status precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`. The only new
exclusion reasons are `BEFORE_CALENDAR_DOMAIN` and `AFTER_CALENDAR_DOMAIN`; the straddle token is
blocking. No roll-proof requirement or result reason is relaxed. Repeat runs over identical bytes
must produce byte-identical identities and evidence.

## 18. Future Implementation Exact Three-Path Scope

A separately authorized implementation may modify only:

- `analysis/gc_dataset_builder.py`;
- `tests/test_gc_dataset_builder.py`;
- `docs/gc_futures_dataset_builder_source_domain_roll_boundary_checkpoint.md`.

No private source, calendar, fixture, package export, downstream candidate/feature/corpus builder,
SMC detector, strategy, engine, configuration, OOS artifact, integration file, or other documentation
file may change. Public function signatures, keyword-only parameter names/defaults, public frozen
dataclass fields, and existing identity payload field names remain unchanged.

## 19. Test-First Implementation Order

Implementation must begin with failing public-builder tests for Sections 8–16. Source changes may
follow only after the tests prove the current defect. Tests use inline synthetic frozen data and no
external fixture. Parameterization may preserve the exact logical matrix below.

After correction, run:

```powershell
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
```

The checkpoint records commands, totals, timings, hashes, byte/line counts, exact scope, and logical
case reconciliation. A source defect outside the exact three paths causes STOP.

## 20. Atomicity, Prefix Invariance, and Authority Boundary

Row classification, calendar validation, session aggregation, and roll evaluation promote one
complete causal group atomically. A failing group and every later group produce no promoted dataset
evidence; strictly prior immutable evidence is preserved when the effective moment is trustworthy.
An unknowable malformed moment requires no trustworthy prefix.

Strictly later complete source/calendar extension may append evidence but cannot alter earlier
classification, assignments, exclusions, roll plan, IDs, or status. Same-effective append,
historical insertion/repair, registry reorder, hash/version mutation, or calendar rewrite is not a
prefix comparison. No detector, candidate, label, feature, outcome, PnL, final OOS, local model, or
human discretionary selection participates in this correction.

## 21. Inline Synthetic Exact 48-Case Unit-Test Matrix

1. Empty validated calendar cannot derive an outer domain and is `INVALID`.
2. Naive, reversed, or non-normalizable calendar endpoints are `INVALID`.
3. Duplicate, overlapping, or unordered calendar intervals are `INVALID`.
4. Exact domain start/end derive from validated intervals, never raw extrema.
5. Bar closing exactly at `domain_start` is `BEFORE_CALENDAR_DOMAIN`.
6. Bar starting exactly at `domain_end` is `AFTER_CALENDAR_DOMAIN`.
7. Bar fully before the domain is conserved as a before-domain exclusion.
8. Bar fully after the domain is conserved as an after-domain exclusion.
9. Bar starting exactly at `domain_start` remains eligible for calendar lookup.
10. Bar closing exactly at `domain_end` remains eligible for calendar lookup.
11. Bar straddling `domain_start` is `INVALID`.
12. Bar straddling `domain_end` is `INVALID`.
13. Boolean/fractional/non-finite/malformed bar evidence is never an exclusion.
14. In-domain missing calendar coverage remains `UNKNOWN`.
15. In-domain maintenance or session-closed bar remains rejected.
16. Split-session and timezone/version reconciliation remains exact.
17. Exact Section 7 before/in/after row counts reconcile.
18. Exact Section 7 before/in/after integer volumes reconcile.
19. Raw row conservation includes every outer-domain exclusion.
20. Raw volume conservation includes every outer-domain exclusion.
21. Exclusion ledger is source-artifact/source-row/time/volume sensitive.
22. External prefiltered or hash-mismatched source is `INVALID`.
23. Initial proof requires canonical predecessor and initial contract in the supplied registry.
24. Exact three preceding eligible sessions are required.
25. Current volume must exceed predecessor volume on each proof session.
26. Missing predecessor or fewer than three sessions remains `UNKNOWN`.
27. Supplied contradictory predecessor evidence is `INVALID`.
28. Mismatched initial contract/date or incomplete opening coverage is fail-closed.
29. Start enumeration selects earliest admissible date then canonical delivery order.
30. Start selection is bound before Run A and is downstream/OOS independent.
31. Zero or non-tie-resolvable admissible starts cause STOP.
32. Canonical registry uniqueness and delivery order are required.
33. Every active/adjacent pair requires complete same-date volume.
34. Zero/zero and zero/positive complete integer-volume comparisons are deterministic.
35. Partial, negative, malformed, or cross-date comparison volume is fail-closed.
36. Manifest-bound GCG26/GCJ26 expansion is hash- and role-sensitive.
37. Expanded-source outer-domain rows remain fully conserved exclusions.
38. Consecutive dominance confirms exactly at the locked boundary.
39. Nonconsecutive dominance resets under the existing rule.
40. Roll advances only to the canonical next contract and resets streak.
41. Any comparable-volume gap in the admitted window remains `UNKNOWN`.
42. Terminal date requires complete active/adjacent coverage; no right censor exists.
43. End shortening is explicit, pre-Run-A, partition-safe, and audit-bound.
44. Required partition dates beyond proved coverage cause STOP/acquisition, not silent shortening.
45. Dataset version and identity are sensitive to domain/exclusions/roll-boundary evidence.
46. Repeatability and deterministic multi-contract ordering are byte-identical.
47. Strictly later complete extension preserves the complete prior prefix.
48. Same-effective append, repair, reorder, hash/version drift, downstream/OOS access, and forbidden
    integration surface are rejected or declared prefix-ineligible.

The logical case count is exactly `48`; parameterized pytest collection count may be higher.

## 22. Independent Verification and Promotion Gates

Documentation acceptance requires:

- exact one-file scope and clean diff formatting;
- exactly `24` numbered sections and sequential cases `1` through `48`;
- exact Section 6 dependency hashes and Section 7 conservation arithmetic;
- explicit in-domain calendar fail-closed preservation;
- explicit no-bootstrap, three-session initial proof, complete adjacent coverage, and no-right-censor
  boundaries;
- exact reserved three-path absence at proposal time;
- focused baseline: `245 passed in 1.06s` using
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`;
- full regression baseline: `2519 passed in 25.58s` using
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`;
- repository-root discovery without the explicit `tests` path was also attempted and stopped during
  collection with three `PermissionError` values at protected private-data directories. It executed
  no product tests and is not represented as a regression failure or pass. No private permission or
  content was changed to bypass that boundary.

Only after this document is independently audited, committed, pushed under separate authorization,
and post-push verified may the exact three-path test-first implementation be proposed. A corrected
private rerun requires a later committed checkpoint, clean worktree, exact immutable inputs, and
separate explicit authority.

## 23. Rollback, Promotion, and Stop Conditions

Rollback for this documentation task is removal of only this untracked proposal before staging, or
reversion by a later explicit commit after local commit. Existing user files and private inputs are
never rollback targets.

STOP on any semantic ambiguity, conservation mismatch, boundary-straddling row, dependency/hash
drift, required public API change, out-of-scope defect, test failure, dirty tracked state, unexpected
untracked file, private-root reappearance, or need to inspect final-OOS payload. Promotion is
forbidden on `UNKNOWN`, `AMBIGUOUS`, or `INVALID` evidence and never implies strategy/trading
authority.

## 24. Final Decision and Resume Point

The source-domain and finite roll-observation defects are reproducible and bounded, but no fix is
implemented by this record. The approved resume point is independent audit of this exact document,
fresh focused/full baselines, exact-path staging/cached audit, and a local documentation commit.

After local commit, STOP before push, implementation, private rerun, dataset/corpus publication,
feature/label build, training, OOS, integration, or trading. Global code freeze remains active for
every file except a later separately authorized exact three-path implementation.
