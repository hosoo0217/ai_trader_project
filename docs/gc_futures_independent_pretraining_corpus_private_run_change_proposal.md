# GC Futures Independent Pretraining Corpus Conditional Private-Run Change Proposal

## 1. Proposal Record

- Proposal date: `2026-08-24`.
- Repository baseline: `8a76e4aea8dd7b1fafd326027fba6705eddd4039`.
- Baseline publication state: local-only; `origin/main` remains
  `f84d418e22cd3162d7cbc5c09c686187b61898d6`.
- Decision:
  `PRIVATE_RUN_NOT_READY_REQUIRE_CANONICAL_UPSTREAM_INPUT_BUILD_NO_EXECUTION_NO_TRAINING_NO_OOS`.
- Authority granted by this document: documentation-only design authority.
- Global code freeze: active outside this exact document.

This proposal locks the only admissible route from the accepted private raw intake to an
independent pretraining corpus. It does not execute that route and does not claim that a corpus,
feature table, label table, model, trading edge, or profitability result exists.

## 2. Exact Documentation Scope

The only path created by this task is:

- `docs/gc_futures_independent_pretraining_corpus_private_run_change_proposal.md`.

No Python, tests, fixtures, private artifacts, manifests, calendar evidence, configuration,
package exports, integration, model, or other documentation may change. The three pre-existing
untracked documents are unrelated user state and remain untouched. Acceptance permits exact-path
staging and one local documentation commit only. It does not authorize push or execution.

## 3. Readiness Finding

The standalone corpus assembler is implemented and tested, but its required accepted private
inputs do not yet coexist:

1. no accepted independent `GCDatasetBuildResult` spans the locked development partitions;
2. no accepted independent `GCCandidateEvidenceResult` is `VALID` with a nonempty manifest;
3. no accepted independent `GCFeatureLabelResult` is `VALID` with complete labels;
4. calendar coverage for every requested 2024-2025 trade date is not yet normalized and proved;
5. minimum partition, direction, and class thresholds therefore cannot yet be evaluated.

Closed Phase A and Phase B outputs remain immutable negative or insufficient evidence. They may
not be promoted, repaired, or relabelled as these missing inputs.

## 4. Governing Tracked Evidence

| Evidence | SHA-256 |
|---|---|
| acquisition and partition proposal | `A9AC9A55D0C24E6825CCD6E0B56C09AD4F5370CBF3D9092D6E7048F30F2C4DF9` |
| corpus freeze-lift decision | `556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303` |
| dataset builder | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| candidate-evidence builder | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| feature/label builder | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| corrected corpus builder | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |
| corrected corpus tests | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` |
| corrected corpus checkpoint | `62020104661C8A5206A98E87D4628886B4009281FF9DDC83819E81B26B7AE58A` |

Any drift is a STOP condition, not an implicit refresh. The corrected local baseline must receive
separate exact push authorization and post-push verification before any private execution proposal
can become effective.

## 5. Exact Private Input Manifests

Only metadata was inspected; the sealed OOS payload was not opened. The locked input-manifest
paths and hashes are:

| Input | Exact ignored path | SHA-256 |
|---|---|---|
| raw intake | `private_data/sierra_chart/gc_20260803_raw_intake/intake_manifest.csv` | `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164` |
| raw intake README | `private_data/sierra_chart/gc_20260803_raw_intake/README.md` | `63AFFCACF182C0987D28A1C6361E48D6FC0E59D0D0DAC71763097C92E3D0950F` |
| raw acquisition checkpoint | `private_data/sierra_chart/gc_20260803_raw_intake/acquisition_checkpoint_20260804.md` | `59B1AB12BFDDDAD7DBAF5E3375DBA19C0F342EAD1E475AFE23E3D75676E89CED` |
| calendar artifact manifest | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/raw_artifact_manifest.csv` | `684F9EAAEAB41BFC4D09C4E4FE7E4B7672D5B246A3F9F251656A8D07068A0575` |
| calendar README | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/README.md` | `BA537533C46E082144973FC50D2385DB5F3E374B352848BB1F650EEEF1312721` |
| calendar checkpoint | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/acquisition_checkpoint_20260808.md` | `8F3BBAFFE2D1A3996E597EE67745B996F5CB1FB07246332F717A067E0A12C6EA` |

These are evidence inputs, not permission to decode every file. Calendar evidence must first be
normalized into complete versioned rows for the exact requested dates.

## 6. Exact Source Registry

The only development-candidate raw sources are the following immutable manifest rows:

| Contract | File | Rows | SHA-256 | Role |
|---|---|---:|---|---|
| `GCJ25` | `GCJ25_COMEX_5m_186d_reacquired_20260804.txt` | 25,126 | `19A05B41A6EA9F9F59F7A6937A38C5EF68C618C4A3BE8727AE702B980BDBD759` | candidate |
| `GCM25` | `GCM25_COMEX_5m_186d_reacquired_20260804.txt` | 25,712 | `E72DE09B55D46AF2774DE9582FFF457584A298C7725B21339D21ACCC0ED2D12B` | candidate |
| `GCQ25` | `GCQ25_COMEX_5m_186d_export_20260803.txt` | 26,093 | `1FECFD8C97C6346EEB62BBC302E677FA52C2A3D8F3D40AA5C578E87F1F3B6F23` | candidate |
| `GCV25` | `GCV25_COMEX_5m_186d_export_20260803.txt` | 23,472 | `B1C3F8691D9256AB02112ACF7FF61D1CD5AD60DEAC60B685F795C0F072DE70D5` | conditional diagnostic |
| `GCZ25` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | 29,100 | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` | candidate |

`GCV25` is admitted only if the canonical prior-completed-session roll rule selects it. GCG26,
GCJ26, GCM26, GCQ26 full exports, both superseded exports, and every Phase A/B derivative are
`CLOSED_RESEARCH_ONLY` or `REFERENCE_ONLY`; they cannot increase development evidence.

## 7. Sealed OOS Boundary

The sole final-OOS record is metadata-only:

- file: `GCQ26_COMEX_5m_30d_export_20260803.txt`;
- rows: `5,263`;
- SHA-256: `15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`;
- interval: `[2026-07-06, 2026-08-01)` by canonical trade date;
- payload access counter: `0`;
- outcome access counter: `0`.

Only these manifest fields may be reconciled. Opening bars, producing labels, viewing outcomes,
computing statistics, or using the full GCQ26 export to reconstruct this interval is forbidden.

## 8. Locked Chronological Partitions

The half-open canonical trade-date intervals remain:

- TRAIN `[2024-11-04, 2025-06-02)`;
- VALIDATION `[2025-06-16, 2025-08-25)`;
- CALIBRATION `[2025-09-08, 2025-11-24)`;
- FINAL_OOS metadata `[2026-07-06, 2026-08-01)`.

All other dates are excluded or embargoed as already committed. Dates cannot move after parsing,
candidate discovery, labels, class balance, metrics, or outcomes are observed.

## 9. Calendar and Time Contract

Every development trade date requires one authoritative normalized GC calendar entry, exact
America/New_York conversion, runtime tzdata-version match, split-session intervals, maintenance
break, holiday status, early close, and source-artifact lineage. Raw emails, screenshots, web pages,
or manifest rows do not themselves satisfy the runtime calendar dataclass contract.

Missing coverage is `UNKNOWN`; contradictory or malformed coverage is `INVALID`. Neither may be
filled with a weekday default, inferred from neighboring years, or repaired after candidate or
label inspection.

## 10. Exact Prospective Private Output Root

If and only if a later execution authority passes all preflight gates, both clean runs must use
temporary sibling directories under:

`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`

The final ignored publication directory is:

`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/accepted/`

No existing output may be overwritten. Temporary output is deleted only after exact resolved-path
verification that it remains inside the named root. Failure leaves evidence quarantined and no
`accepted` directory is published.

## 11. Prospective Atomic Build Order

One later authorized run must execute this immutable sequence:

1. reconcile manifests, source bytes, roles, and access counters;
2. normalize and validate the complete development calendar;
3. call `build_gc_futures_dataset()` once;
4. validate the complete `GCDatasetBuildResult` before promotion;
5. build required immutable structural seed evidence from that dataset only;
6. call `build_gc_candidate_evidence()` once;
7. validate the complete candidate result and thresholds before promotion;
8. call `build_gc_feature_labels()` once;
9. validate complete features, labels, purge, embargo, and conservation;
10. call `build_gc_pretraining_corpus()` once;
11. validate the entire corpus manifest and authority flags;
12. repeat from immutable inputs in an independent clean directory.

No downstream step runs after an upstream `INVALID`, `AMBIGUOUS`, `UNKNOWN`, `NONE`, exception,
threshold failure, or hash drift.

## 12. Upstream Result Boundary

The corpus builder accepts only caller-supplied frozen canonical results. It must not parse raw
files, call detectors, create candidates, recompute features or labels, repair histories, infer
calendar rows, select a contract from filename, or enrich provenance. Each upstream result must be
`VALID`, nonempty, identity-valid, version-matched, ordered, and internally complete.

Partial outputs and closed prior-run outputs are never adapted into the required result types.

## 13. Candidate Evidence Gate

Candidate evidence must arise from the independent dataset and its causally complete detector
evidence only. The accepted builder's exact status precedence and atomic no-promotion semantics
remain unchanged. Simultaneous opposing evidence may be `AMBIGUOUS` and therefore blocks the group.

At least `150/50/50` complete candidates are required in TRAIN/VALIDATION/CALIBRATION, including
at least `30/10/10` candidates in each direction. Failure closes the attempt without adjusting
dates, detector settings, setup definitions, or thresholds.

## 14. Feature and Label Gate

Only `GC_AI_FEATURE_SCHEMA_V1` and `GC_AI_LABEL_SCHEMA_V1` are admissible. Every accepted candidate
maps to exactly one feature row and one complete `H=12` strictly-later label, or to one explicit
exclusion. Features use evidence known no later than the candidate moment. Labels remain within the
same contract and partition.

At least `30/10/10` positive and `30/10/10` negative complete labels are required in
TRAIN/VALIDATION/CALIBRATION. Future return, outcome, MFE/MAE, PnL, partition membership, source
filename, and model output are forbidden features.

## 15. Purge, Embargo, and Contamination

Any source or label interval crossing a partition boundary is purged atomically. At least 12
eligible five-minute bars are embargoed after fitting boundaries, while the longer locked date
gaps control where applicable. Same-effective groups and overlapping label horizons cannot split
across partitions.

Every candidate is joined to prior-run lineage and outcome-access records. A collision is
`CLOSED_RESEARCH_ONLY`; missing audit evidence is `UNKNOWN`; contradiction is `INVALID`. Exclusion
cannot reduce a threshold or move a date.

## 16. Exact Source and Volume Conservation

Two-run evidence must prove raw-row to canonical-bar, canonical-bar to session, session to
partition, candidate to feature, and candidate to label conservation. Integer source volume,
canonical volume, complete-session volume, admitted volume, and excluded volume must reconcile.

Duplicates, missing source IDs, malformed integer values, unexplained gaps, overlapping source
moments, unordered moments, or a source assigned to more than one role stop the run.

## 17. Identity and Manifest Contract

The existing deterministic identities remain authoritative: source coverage, dataset/segment,
candidate/manifest, feature row/label/manifest, PARTITION_PLAN, RECORD, PARTITION, CORPUS, and
MANIFEST. Required and forbidden fields are those of their committed public builders.

The final manifest binds every code hash, input hash, calendar/tzdata version, role, partition,
ordered ID, count, exclusion reason, roll decision, interval extremum, conservation total, OOS
metadata hash, and access counter. Reordering identity-bearing tuples changes identity or fails
closed; dictionary or filesystem enumeration order cannot affect output.

## 18. Two-Run Determinism Procedure

Run A and Run B must start from the same immutable inputs and fresh empty directories. No result
from Run A may seed, cache, repair, or configure Run B. Each run records input hashes before read,
output hashes after atomic completion, normalized result equality, ordered manifest equality, and
access counters.

Promotion requires dataclass-equal results, byte-identical canonical serialized manifests, equal
counts and exclusions, and identical SHA-256 digests. A difference is `INVALID`, not an invitation
to select the better run.

## 19. Status and Authority

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Even a `VALID` corpus result has `training_authorized=False`, `oos_authorized=False`,
`integration_authorized=False`, and `trading_authorized=False`. It is research data readiness
evidence only. No model selection, fitting, calibration, backtest promotion, paper/live trading,
or order authority follows automatically.

## 20. Failure and Prior-Evidence Semantics

Each effective group is fully validated before promotion. Determinably later malformed evidence
returns the highest applicable failure while preserving strictly prior accepted immutable evidence.
The failing group and all causally later groups promote nothing. An unknowable effective moment
does not create a trustworthy prefix obligation.

No exception, partial manifest, temporary row, or stale output may leak as accepted evidence.

## 21. Exact 48-Case Verification Matrix

1. Exact baseline and all tracked dependency hashes reconcile.
2. Local-only corrected baseline cannot authorize execution.
3. Raw intake manifest exact path and hash reconcile.
4. Calendar manifest, README, and checkpoint hashes reconcile.
5. Each of five development source names, contracts, row counts, and hashes reconciles.
6. Superseded GCM26 and GCQ26 sources are rejected.
7. GCG26/GCJ26/GCM26/GCQ26 full sources remain closed or reference only.
8. Frozen OOS metadata reconciles without payload access.
9. Nonzero OOS payload access stops the plan.
10. Nonzero OOS outcome access stops the plan.
11. Exact TRAIN interval assignment is half-open.
12. Exact VALIDATION interval assignment is half-open.
13. Exact CALIBRATION interval assignment is half-open.
14. Boundary-crossing source or label group is purged atomically.
15. Minimum 12-bar embargo is enforced without shortening date gaps.
16. Missing calendar coverage returns UNKNOWN with no promotion.
17. Contradictory calendar evidence returns INVALID over UNKNOWN.
18. Runtime tzdata mismatch fails closed.
19. GCV25 requires exact prior-completed-session roll selection.
20. Filename or price continuity cannot select a contract.
21. Dataset result must be VALID, nonempty, frozen, ordered, and identity-valid.
22. Candidate result must be VALID, nonempty, frozen, ordered, and identity-valid.
23. Feature/label result must be VALID, nonempty, frozen, ordered, and identity-valid.
24. Missing candidate input cannot be synthesized by the corpus builder.
25. Missing feature/label input cannot be recomputed by the corpus builder.
26. Closed Phase A evidence cannot be relabelled as independent input.
27. Closed Phase B evidence cannot be relabelled as independent input.
28. Candidate thresholds are exact for all three partitions.
29. Bullish and bearish minimums are exact for all three partitions.
30. Positive and negative class minimums are exact for all three partitions.
31. Threshold failure stops without date or rule tuning.
32. Every candidate maps to one feature and one label or one exclusion.
33. Feature moment never follows its candidate effective moment.
34. Label horizon uses exactly 12 strictly-later eligible bars.
35. Label cannot cross contract or partition boundaries.
36. Raw/canonical/session/partition integer volumes conserve exactly.
37. Duplicate canonical moments fail closed.
38. Prior-run contamination collision is closed research only.
39. Missing contamination audit is UNKNOWN; contradiction is INVALID.
40. Run A cannot seed, cache, or configure Run B.
41. Two runs require equal normalized results and byte-identical manifests.
42. Hash, count, exclusion, or ordering drift is INVALID.
43. Determinably later failure preserves strictly prior immutable evidence.
44. Failing and later groups promote no evidence.
45. Final status precedence is exact.
46. A VALID corpus grants no training, OOS, integration, or trading authority.
47. Exact ignored output root is collision-safe and no existing output is overwritten.
48. Exact scope, formatting, hashes, tests, cached diff, and rollback evidence pass before commit.

## 22. Promotion Gates

This document can be promoted only as a documentation record. Private execution remains blocked
until all of the following are separately evidenced after this proposal is published:

1. local correction and this proposal are on the verified live remote main;
2. repository and private-manifest hashes match Sections 4-6;
3. complete normalized 2024-2025 calendar coverage passes independent audit;
4. one later exact execution authorization names the unchanged output root and procedure;
5. OOS access counters remain zero;
6. preflight confirms no conflicting private output exists.

Passing these gates permits one bounded private two-run attempt only. It does not guarantee a
`VALID` result and does not authorize training.

## 23. Rollback and Stop Conditions

Before local commit, rollback is deletion of this one new proposal only. After commit, rollback is
a normal forward revert of that exact commit, never a destructive reset. Existing raw, calendar,
closed research, code, tests, and private artifacts remain immutable.

STOP before execution if any required source, calendar row, hash, version, ordering, identity,
coverage, roll, contamination, threshold, purge, embargo, conservation, output-path, determinism,
or access-counter fact cannot be proved. STOP on any request to open OOS payload, tune after label
inspection, reuse closed evidence, overwrite output, change public APIs, touch integration, train a
model, or expand scope without another prospective decision.

Fresh cache-disabled verification for this documentation task is:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 0.61s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2519 passed in 24.35s
```

The matrix contains exactly 48 sequential cases, the document contains exactly 24 numbered
sections, and pre-stage formatting inspection reports no whitespace error. Final artifact hash,
byte count, line count, and cached-diff evidence are measured after staging rather than embedded
as self-referential content.

## 24. Final Decision and Resume Boundary

The correct next state is not training and not a private corpus run. It is a committed,
independently audited specification of the missing canonical-input build and the conditional
two-run procedure.

After this document passes semantic, structural, hash, formatting, scope, staged-content, and
commit audits, work must STOP. A later turn needs exact GitHub export authorization before push.
After a successful push and post-push audit, an exact private execution authorization may be
considered. Until then, private run, training, OOS, feature/label execution, integration, and all
other files remain frozen.
