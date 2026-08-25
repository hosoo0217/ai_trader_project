# GC Futures Independent Pretraining Atomic Upstream Build Change Proposal

## 1. Proposal Record

- Date: `2026-08-25`.
- Capability: development-only GC Futures independent pretraining upstream build.
- Proposal status: `PROPOSED_NOT_EXECUTED`.
- Decision: `READY_FOR_INDEPENDENT_DOCUMENT_AUDIT_ONLY`.
- Authority: documentation-only; no private build, training, final OOS access, integration, or trading.

This prospective record defines one collision-safe transaction that may later construct the four
missing canonical upstream results. It does not treat the completed calendar normalization as bar,
candidate, feature, label, corpus, model, or profitability evidence.

## 2. Exact Change Scope

This task may create only:

- `docs/gc_futures_independent_pretraining_atomic_upstream_build_change_proposal.md`.

No Python, test, fixture, package export, requirement, configuration, private artifact, manifest,
calendar, integration file, training file, or existing documentation file may change. In
particular, these pre-existing user-owned untracked files remain untouched:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`;
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

## 3. Repository and Decision Baseline

The proposal was prepared from:

- `HEAD`: `1550760b892cd4d72d7480c33e56ae85ca5ba420`;
- local `origin/main`: `1550760b892cd4d72d7480c33e56ae85ca5ba420`;
- subject: `docs: record post-calendar corpus readiness`;
- post-calendar readiness decision SHA-256:
  `AD736DDC448AB79B53FC6A71DCC12691FCE3133E18F7F9B4AD867703CF2BD956`.

The governing readiness state is
`POST_CALENDAR_PASS_UPSTREAM_RESULTS_MISSING_REQUIRE_PROSPECTIVE_ATOMIC_BUILD_PROPOSAL_NO_EXECUTION_NO_TRAINING_NO_OOS`.
This proposal resolves only the prospective-procedure requirement.

## 4. Immutable Tracked Dependency Binding

| Artifact | SHA-256 |
| --- | --- |
| corpus freeze-lift decision | `556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303` |
| dataset builder | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| candidate-evidence builder | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| feature/label builder | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| corpus builder | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |
| dataset tests | `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878` |
| candidate tests | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| feature/label tests | `EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B` |
| corpus tests | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` |

Any byte drift is a STOP condition. A later run must not silently refresh these bindings.

## 5. Immutable Private Control Binding

Only control metadata, not final-OOS payload, was used to prepare this record.

| Artifact | Exact private path | SHA-256 |
| --- | --- | --- |
| raw intake manifest | `private_data/sierra_chart/gc_20260803_raw_intake/intake_manifest.csv` | `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164` |
| raw intake README | `private_data/sierra_chart/gc_20260803_raw_intake/README.md` | `63AFFCACF182C0987D28A1C6361E48D6FC0E59D0D0DAC71763097C92E3D0950F` |
| raw acquisition checkpoint | `private_data/sierra_chart/gc_20260803_raw_intake/acquisition_checkpoint_20260804.md` | `59B1AB12BFDDDAD7DBAF5E3375DBA19C0F342EAD1E475AFE23E3D75676E89CED` |
| calendar artifact manifest | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/raw_artifact_manifest.csv` | `1DCBB499EBF49CE7BF66B94FE8F97D344C234F7775D366A2D0C6104A41760C74` |
| calendar README | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/README.md` | `680DFB2C7C8E09D51C432F3B329B14A2FB0760E671BC6F6874FF55BC7848000F` |
| calendar acquisition checkpoint | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/acquisition_checkpoint_20260808.md` | `EE8BC8C47F2A935E7D65918ECC620DF044C68DF05E890934835AB70AF6C34ED8` |
| official CME notice | `private_data/sierra_chart/gc_calendar_20260804_raw_intake/CME_NOTICE_20230202_exchange_business_date_retrieved_20260825.html` | `DFD86332F4F71516AE2E12D3773B2D11D4771DE6EA35DDB2EA09FE17EB980C15` |

The raw files remain private and ignored. Their presence is not permission to copy them into Git.

## 6. Accepted Calendar Input Contract

The only admissible development-calendar root is:

`private_data/sierra_chart/gc_independent_pretraining_calendar_2024_2025_v1/`

The following exact evidence must reconcile before any raw bar is parsed:

- result status `VALID`;
- calendar version `GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`;
- normalized calendar `normalized_calendar.jsonl` SHA-256
  `EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED`;
- 255 requested trade dates and 252 trading intervals;
- `TRAIN/VALIDATION/CALIBRATION` date counts `150/50/55`;
- runtime tzdata version `2026.2`;
- independent two-run normalized bytes identical;
- final-OOS and embargo rows not synthesized;
- source bars and volume admitted by the calendar-only run exactly `0 / 0`.

Calendar rows are immutable caller-supplied evidence. The build may not infer missing weekdays,
repair holidays, change split sessions, or reinterpret source notices after seeing candidates or
labels.

## 7. Exact Development Source Registry

Only these raw-intake rows may supply development bars:

| Contract | Exact file under `gc_20260803_raw_intake/` | Rows | SHA-256 | Role |
| --- | --- | ---: | --- | --- |
| `GCJ25` | `GCJ25_COMEX_5m_186d_reacquired_20260804.txt` | 25,126 | `19A05B41A6EA9F9F59F7A6937A38C5EF68C618C4A3BE8727AE702B980BDBD759` | candidate |
| `GCM25` | `GCM25_COMEX_5m_186d_reacquired_20260804.txt` | 25,712 | `E72DE09B55D46AF2774DE9582FFF457584A298C7725B21339D21ACCC0ED2D12B` | candidate |
| `GCQ25` | `GCQ25_COMEX_5m_186d_export_20260803.txt` | 26,093 | `1FECFD8C97C6346EEB62BBC302E677FA52C2A3D8F3D40AA5C578E87F1F3B6F23` | candidate |
| `GCV25` | `GCV25_COMEX_5m_186d_export_20260803.txt` | 23,472 | `B1C3F8691D9256AB02112ACF7FF61D1CD5AD60DEAC60B685F795C0F072DE70D5` | conditional diagnostic |
| `GCZ25` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | 29,100 | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` | candidate |

All are strict UTF-8 Sierra Chart 13-column exports in `Asia/Tokyo`, timeframe `5M`, tick size
`0.1`. `GCV25` may enter accepted segments only if the builder's prior-completed-session roll rule
selects it. Later contracts, superseded exports, and Phase A/B derivatives are reference-only and
cannot increase evidence.

## 8. Sealed Final-OOS Boundary

The sole final-OOS record remains metadata-only:

- `GCQ26_COMEX_5m_30d_export_20260803.txt`;
- rows `5,263`;
- SHA-256 `15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`;
- canonical interval `[2026-07-06, 2026-08-01)`;
- payload access counter `0`;
- outcome access counter `0`.

The later build may reconcile only those manifest fields. It must not open, hash, parse, copy,
summarize, label, or reconstruct the OOS payload, including from the full GCQ26 export. Any OOS
contact terminates the transaction before publication.

## 9. Locked Chronological Partitions

The half-open trade-date plan is immutable:

- `TRAIN`: `[2024-11-04, 2025-06-02)`;
- `VALIDATION`: `[2025-06-16, 2025-08-25)`;
- `CALIBRATION`: `[2025-09-08, 2025-11-24)`;
- `FINAL_OOS` metadata only: `[2026-07-06, 2026-08-01)`.

The gaps between development partitions are purge/embargo regions. The corpus plan fixes label
horizon `12` and minimum embargo `12` bars. Same-effective groups, overlapping label horizons, and
strictly-later label bars cannot cross a partition boundary.

## 10. Exact Existing Public API Boundary

No public signature, dataclass, enum, identity payload, default, or export may change. The later
private orchestration may call only these existing keyword-only functions:

```python
parse_sierra_chart_gc_export(
    *, source_name, contract, role, capture_timestamp,
    chart_timezone, timeframe, raw_bytes,
)

build_gc_futures_dataset(
    *, exports, coverage_evidence, calendar_entries, config,
)

build_gc_candidate_evidence(
    *, dataset_config, dataset, calendar_entries, structural_seed,
    config=GCCandidateEvidenceConfig(),
)

build_gc_feature_labels(
    *, dataset_config, dataset, calendar_entries, candidates,
    config=GCFeatureLabelConfig(),
)

build_gc_pretraining_corpus(
    *, dataset_config, dataset_calendar_entries, dataset_result,
    candidate_result, feature_label_result, source_registry, partition_plan,
)
```

The parsers and builders remain pure in-memory contract boundaries. If execution requires a new
tracked adapter, importer, API parameter, or semantic correction, this proposal stops and a new
test-first change decision is required.

## 11. Exact Configuration Contract

The dataset configuration must bind `GC`, `5M`, `Asia/Tokyo`, `America/New_York`, tzdata `2026.2`,
tick size `Decimal("0.1")`, initial contract `GCJ25`, initial trade date `2024-11-04`, roll
confirmation `3` completed sessions, and the sealed final-OOS bounds from Section 9.

Candidate configuration remains the committed default `GCCandidateEvidenceConfig`. Feature/label
configuration remains `GC_AI_FEATURE_SCHEMA_V1`, `GC_AI_LABEL_SCHEMA_V1`, and `H=12`. The corpus
partition plan uses the exact Section 9 dates, label horizon `12`, and minimum embargo `12`.
Configuration is frozen before Run A and reused byte-for-byte for Run B.

## 12. Exact Transaction and Output Topology

The single ignored transaction root is:

`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`

Before execution, that root and every child below must be absent. The only prospective children are:

```text
.run_a/dataset/
.run_a/candidate_evidence/
.run_a/feature_labels/
.run_a/corpus/
.run_b/dataset/
.run_b/candidate_evidence/
.run_b/feature_labels/
.run_b/corpus/
.accepted_pending/dataset/
.accepted_pending/candidate_evidence/
.accepted_pending/feature_labels/
.accepted_pending/corpus/
accepted/
```

The four canonical accepted outputs are respectively
`accepted/dataset/`, `accepted/candidate_evidence/`, `accepted/feature_labels/`, and
`accepted/corpus/`. No other path is promotable. Existing path, symlink, junction, reparse point,
case-fold collision, unresolved parent, or output outside this exact resolved root is `INVALID`.

## 13. Collision, Isolation, and Clean-Run Rules

Run A and Run B start from separately opened immutable input bytes and separately materialized
calendar dataclasses. They share no mutable object, cache, output file, iterator, temporary
directory, or result object. Filesystem enumeration order is never an input.

No existing output is overwritten, merged, repaired, renamed into place, or deleted. An unexpected
file anywhere under the transaction root stops execution. Failure artifacts may be retained under
an explicitly non-promotable quarantine outside `accepted`, but they may never be consumed by the
second run or a future attempt.

## 14. Run A Exact Build Order

Run A must perform, in order:

1. reconcile repository, control, calendar, and source hashes;
2. prove OOS payload/outcome counters remain zero;
3. parse the five permitted raw sources with exact manifest metadata;
4. validate rows, timestamps, prices, integer volume, and source conservation;
5. call `build_gc_futures_dataset()` once and fully validate its result;
6. construct the required immutable structural seed solely from accepted dataset bars;
7. call `build_gc_candidate_evidence()` once and fully validate its result;
8. adapt only the result's canonical candidate evidence tuple to the locked feature input type;
9. call `build_gc_feature_labels()` once and fully validate its result;
10. create the exact source registry and partition plan from locked evidence;
11. call `build_gc_pretraining_corpus()` once and fully validate its result;
12. serialize canonical manifests and content only after the complete in-memory chain passes.

No downstream call occurs after an upstream non-`VALID` status, exception, threshold failure, or
conservation failure.

## 15. Run B and Two-Run Reproducibility

Run B repeats every Section 14 step from original immutable inputs in `.run_b`. It must not read
Run A output. The audit compares:

- normalized result objects and status/reason tuples;
- ordered IDs, segments, candidates, features, labels, corpus records, and exclusions;
- canonical JSON/JSONL/CSV bytes and SHA-256 values;
- row, bar, session, candidate, label, partition, direction, outcome, and volume counts;
- roll decisions, source registry, calendar lineage, purge, embargo, and authority flags.

Any difference is `NON_DETERMINISTIC` and blocks `.accepted_pending` creation.

## 16. Dataset Acceptance Gate

The dataset result must be `VALID`, nonempty, frozen, identity-valid, canonically ordered, and bound
to every accepted source and calendar row. The audit must prove raw-row-to-bar, integer-volume,
trade-date, session, roll, source, contract, timestamp, and exclusion conservation.

Duplicate coverage, ambiguous roll selection, missing calendar coverage, malformed source rows,
out-of-order timestamps, wrong timezone/tzdata, synthetic no-data rows, volume mismatch, or OOS
overlap blocks the entire chain. A conditional `GCV25` parse is not equivalent to admission.

## 17. Candidate Acceptance Gate

The candidate result must be `VALID`, nonempty, frozen, identity-valid, canonically ordered, and
derived only from accepted dataset segments plus the exact calendar. Its immutable structural seed
must reconcile with the same dataset and may not contain hindsight enrichment.

Minimum complete candidates are `150/50/50` in `TRAIN/VALIDATION/CALIBRATION`, with at least
`30/10/10` per direction. `UNKNOWN`, `AMBIGUOUS`, `INVALID`, insufficient coverage, dangling
lineage, cross-segment mutation, or a candidate whose effective moment is outside its source
segment stops the chain without feature promotion.

## 18. Feature and Label Acceptance Gate

Every accepted candidate must map to exactly one feature row and one complete strictly-later
`H=12` research label, or exactly one explicit exclusion. Feature values may use only evidence
known no later than the candidate effective moment. Labels remain inside the candidate's contract,
dataset segment, and partition.

The audit must prove candidate-to-feature, candidate-to-label, horizon, outcome, exclusion, schema,
identity, ordering, purge, embargo, and class-balance conservation. Positive and negative complete
labels must each reach at least `30/10/10` by `TRAIN/VALIDATION/CALIBRATION`. PnL, future return,
MFE/MAE, source filename, partition membership, model output, and OOS information are forbidden
features.

## 19. Corpus Acceptance and Authority Gate

The corpus builder receives only the fully validated frozen results from Sections 16-18. It must
not parse raw files, call detectors, create candidates, recompute features or labels, repair
histories, infer calendar rows, or select contracts.

The corpus result must be `VALID`, nonempty, identity-valid, canonically ordered, byte-stable across
runs, and exactly conserve the accepted source registry, records, partitions, directions,
outcomes, exclusions, and lineage. Even `VALID` must retain
`training_authorized=False`, `oos_authorized=False`, `integration_authorized=False`, and
`trading_authorized=False`.

## 20. Status, Atomic Promotion, and Prior Evidence

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Every same-effective group is validated before promotion. A later malformed or uncertain group
cannot mutate strictly prior immutable evidence, but any non-`VALID` final result blocks the whole
transaction's accepted publication.

Only after both complete runs and every gate pass may exact Run A canonical bytes be copied into
`.accepted_pending`. Its manifest must bind both run hashes and all input hashes. The sole
publication action is one same-volume atomic directory rename from `.accepted_pending` to
`accepted`. No stage-level accepted directory is exposed and Run B bytes are proof, not a second
accepted corpus.

## 21. Exact Sequential 48-Case Verification Matrix

1. HEAD and local origin/main match the recorded baseline.
2. Exact one-file documentation scope holds.
3. The three pre-existing untracked proposals are byte-unchanged.
4. Post-calendar readiness hash matches.
5. Corpus freeze-lift hash matches.
6. Dataset builder and test hashes match.
7. Candidate builder and test hashes match.
8. Feature/label builder and test hashes match.
9. Corpus builder and test hashes match.
10. Private control-manifest hashes match current bytes.
11. Calendar result is VALID with exact version and tzdata.
12. Calendar counts are exactly 255 dates, 252 intervals, and 150/50/55 partitions.
13. Normalized calendar hash and two-run equality match.
14. Source registry contains exactly the five permitted rows.
15. Every source byte hash and data-row count matches.
16. Superseded and later-contract sources remain forbidden.
17. GCV25 remains conditional on canonical roll selection.
18. Final-OOS metadata fields match without payload access.
19. OOS payload/outcome counters remain zero.
20. Partition intervals remain exact and half-open.
21. Purge and embargo gaps are immutable.
22. Transaction root and all prospective children are absent at preflight.
23. Resolved output paths remain inside the exact transaction root.
24. Run A and Run B use isolated objects and directories.
25. Raw parse uses exact UTF-8, 13-column, timezone, and volume rules.
26. Dataset public signature and configuration remain exact.
27. Dataset status, identity, order, roll, calendar, row, and volume gates pass.
28. Dataset failure prevents candidate execution.
29. Structural seed uses accepted dataset evidence only.
30. Candidate public signature and default remain exact.
31. Candidate status, identity, lineage, order, and minimum-count gates pass.
32. Candidate failure prevents feature/label execution.
33. Feature/label public signature, schemas, and H=12 remain exact.
34. Every candidate maps to one feature/label pair or one exclusion.
35. Feature moments and label horizons contain no look-ahead leakage.
36. Purge, embargo, partition, direction, and class thresholds pass.
37. Feature/label failure prevents corpus execution.
38. Corpus public signature and partition plan remain exact.
39. Corpus receives caller-supplied canonical results only.
40. Corpus identities, records, lineage, exclusions, and authority flags pass.
41. Run A and Run B normalized objects are equal.
42. Run A and Run B canonical bytes and hashes are equal.
43. Count, identity, timestamp, partition, and volume conservation pass.
44. `.accepted_pending` is created only after the entire two-run chain passes.
45. One atomic rename publishes the complete accepted bundle.
46. Focused four-module tests pass cache-disabled.
47. Full repository `tests` suite and formatting/scope audits pass.
48. No private run, training, OOS, integration, push, or trading authority is granted by this file.

## 22. Verification and Promotion Requirements

This proposal may be locally committed only after full-content review, exact section/case counts,
hash reconciliation, formatting, exact-scope, cached-content, and cached-diff audits pass, plus:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider \
  tests/test_gc_dataset_builder.py \
  tests/test_gc_candidate_evidence_builder.py \
  tests/test_gc_feature_label_builder.py \
  tests/test_gc_pretraining_corpus.py

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
```

Fresh cache-disabled verification on `2026-08-25`:

```text
420 passed in 3.93s
2519 passed in 24.18s
```

The structural audit found exactly 24 sequential numbered sections and exactly 48 sequential cases
inside Section 21. All four prospective private output roots were absent, bound source/test hashes
matched current bytes, and the three pre-existing untracked documents retained hashes
`CA2C1CE2178450F4E9D20A1BEC9883805089520F93B933A374667B841B70BFD0`,
`FC068B5B089CC8B5D1862C1C26454371E8C9ADFFC6120FA08541D47B6926FF13`, and
`C073117D83945CB362D8CC9C9DFFA34EE1898D533A81EB3D06DA355FB4D7D87D`, respectively.

Push requires fresh exact GitHub privacy/export authorization. Private execution requires a later
separate authorization naming this unchanged proposal and transaction root. Passing execution may
publish only the accepted private bundle and its private audit; it must stop before training.

## 23. Rollback and Stop Conditions

Before commit, rollback is deletion of this new documentation file only. After commit, rollback is
a normal forward revert of its exact commit. No destructive reset, raw-source deletion, private
artifact deletion, or OOS access is allowed.

STOP on any tracked or private hash drift, missing input, calendar mismatch, source ambiguity,
output collision, path escape, API mismatch, new implementation requirement, OOS contact,
non-`VALID` result, insufficient counts or class balance, purge/embargo leakage, conservation
failure, nondeterminism, regression failure, scope expansion, training, integration, or trading
authority.

## 24. Final Decision and Resume Boundary

The prospective procedure is fully specified but not operationally active. The exact state is:

`PROPOSAL_READY_FOR_AUDIT_COMMIT_AND_EXPLICIT_PUSH_NO_PRIVATE_EXECUTION_NO_TRAINING_NO_OOS`.

After independent audit and local commit, stop before push. After a separately authorized push and
post-push audit, one later exact authorization may activate the Section 12-20 private transaction.
That transaction must perform two clean runs, publish only a complete PASS bundle, independently
audit it, and stop. Training, feature-policy changes, final OOS access, model selection,
integration, execution, BUY/SELL decisions, and PnL claims remain forbidden.
