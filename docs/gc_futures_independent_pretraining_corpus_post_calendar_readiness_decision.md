# GC Futures Independent Pretraining Corpus Post-Calendar Readiness Decision

## 1. Decision Record

- Date: `2026-08-25`.
- Capability: independent GC Futures pretraining-corpus private-run readiness.
- Decision: `NOT_READY_REQUIRE_PROSPECTIVE_UPSTREAM_BUILD_PROPOSAL`.
- Authority: documentation-only; no private execution, training, OOS, integration, or trading.

This record reconciles the newly completed development-calendar gate with the already committed
corpus contract. It does not reinterpret missing upstream results as evidence and does not authorize
the conditional private run.

## 2. Exact Change Scope

The only tracked path created by this task is:

- `docs/gc_futures_independent_pretraining_corpus_post_calendar_readiness_decision.md`.

No Python, tests, fixtures, package exports, requirements, configuration, private artifacts,
manifests, integration files, training files, or existing untracked documents may change.

## 3. Repository Baseline

The audited repository baseline is:

- `HEAD`: `c076a64cf49f8942b5607e6cf129f7728559c443`;
- local `origin/main`: `c076a64cf49f8942b5607e6cf129f7728559c443`;
- live remote `main`: `c076a64cf49f8942b5607e6cf129f7728559c443`.

The worktree contains three pre-existing untracked user-owned proposals. They are outside this
task and remain untouched.

## 4. Governing Tracked Contracts

The following immutable hashes were reconciled:

| Artifact | SHA-256 |
| --- | --- |
| corpus freeze-lift decision | `556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303` |
| dataset builder | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| candidate-evidence builder | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| feature/label builder | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| corpus builder | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |
| corpus tests | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` |
| corpus checkpoint | `62020104661C8A5206A98E87D4628886B4009281FF9DDC83819E81B26B7AE58A` |

Any future drift requires a new prospective decision before private execution.

## 5. Completed Calendar Gate

The private development calendar result is `VALID` under version
`GC_INDEPENDENT_PRETRAINING_DEVELOPMENT_CALENDAR_V1_20260825`. It contains 255 requested trade
dates, 252 trading intervals, partition counts `150/50/55` for
`TRAIN/VALIDATION/CALIBRATION`, and no created FINAL_OOS or embargo rows.

Its normalized calendar SHA-256 is
`EA9F48F60459A459A52EEA6B27261757691BA25404FB6EC5FE89474E396FF0ED`.
The result grants calendar-evidence authority only.

## 6. Calendar Lineage Evidence

The calendar audit recorded:

- official CME notice SHA-256
  `DFD86332F4F71516AE2E12D3773B2D11D4771DE6EA35DDB2EA09FE17EB980C15`;
- runtime tzdata version `2026.2`;
- identical normalized bytes across two clean runs;
- lineage, coverage, interval, timezone-equivalence, and conservation audits `PASS`;
- admitted source bars and integer volume `0 / 0` because calendar-only execution did not
  authorize bar ingestion.

Calendar success therefore cannot be promoted as dataset, candidate, feature, label, or corpus
success.

## 7. Current Private Control Hashes

Current private control hashes are:

| Artifact | SHA-256 |
| --- | --- |
| raw intake manifest | `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164` |
| calendar raw artifact manifest | `1DCBB499EBF49CE7BF66B94FE8F97D344C234F7775D366A2D0C6104A41760C74` |
| calendar README | `680DFB2C7C8E09D51C432F3B329B14A2FB0760E671BC6F6874FF55BC7848000F` |
| calendar acquisition checkpoint | `EE8BC8C47F2A935E7D65918ECC620DF044C68DF05E890934835AB70AF6C34ED8` |

These values supersede the older private-control values embedded in the conditional corpus
private-run proposal. That proposal cannot be executed unchanged.

## 8. Raw-Source Availability

The private intake manifest contains canonical five-minute GC contract files spanning the
development horizon, including `GCJ25`, `GCM25`, `GCQ25`, `GCV25`, `GCZ25`, and later contracts.
Availability in a manifest is acquisition evidence only. It does not prove canonical parsing,
roll selection, deduplication, session assignment, conservation, or acceptable candidate coverage.

The frozen FINAL_OOS source remains metadata-only and must not be opened.

## 9. Missing Canonical Dataset Result

No accepted independent 2024-2025 `GCDatasetBuildResult` output root exists. Existing 2026 Phase A
and Phase B private artifacts are development or non-promotable research evidence and cannot be
relabelled as the independent pretraining dataset.

The dataset builder must later run prospectively against the locked raw sources and normalized
calendar. Until then, dataset status is `MISSING`, not `VALID`.

## 10. Missing Candidate-Evidence Result

No accepted independent 2024-2025 candidate-evidence output root exists. Existing Phase A
candidate artifacts are closed research evidence and are forbidden as independent corpus input.

Candidate discovery must occur only after a complete canonical dataset passes. Candidate thresholds,
selection rules, ordering, and atomic no-promotion behavior remain unchanged.

## 11. Missing Feature and Label Result

No accepted independent 2024-2025 `GCFeatureLabelResult` output root exists. Consequently no
candidate has a proved one-to-one feature row and complete strictly-later `H=12` label under the
independent corpus contract.

No class-balance, purge, embargo, or label-conservation claim may be made before that result exists.

## 12. Missing Corpus Result

The reserved root
`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/` is absent. No accepted corpus,
partition manifest, record manifest, or two-run corpus reproducibility proof exists.

The absence is an expected fail-closed state and must not be repaired by copying prior artifacts.

## 13. Exact Readiness Status

The calendar prerequisite is `VALID`, but the complete readiness result is `UNKNOWN/NOT_READY`
because required canonical upstream results are missing. A calendar `VALID` result cannot outrank
independently missing dataset, candidate, feature, and label evidence.

No contradictory supplied evidence was found that would raise the result to `INVALID`; hash drift
in the old execution proposal instead makes that proposal non-executable.

## 14. Status Precedence

Any later readiness analyzer or manual gate must preserve:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Malformed supplied evidence is `INVALID` even when another required collection is missing. Missing
required evidence is `UNKNOWN`. `VALID` is reachable only after every required result and lineage
link passes. Empty requested scope alone may be `NONE`.

## 15. No-Look-Ahead Boundary

FINAL_OOS payload and outcomes remain sealed. No 2026 OOS bars, result, metric, class balance, or
future event may influence 2024-2025 parsing, roll choice, candidate selection, features, labels,
purge, embargo, or partition assignment.

Every future effective group must be validated before promotion; later evidence cannot rewrite a
strictly prior accepted group.

## 16. Exact Next Prospective Scope

The next permitted task is one new documentation-only proposal that binds the current hashes and
specifies an atomic private build of these four stages:

1. canonical 2024-2025 dataset;
2. independent candidate evidence;
3. feature/label result with purge and embargo;
4. pretraining corpus with two-run reproducibility.

It must name exact input and output paths, reject collisions, preserve the existing public APIs,
and stop before execution. It may not edit the three pre-existing untracked proposals.

## 17. Future Atomic Build Order

Only after that prospective proposal is independently audited, committed, pushed with explicit
export consent, and separately authorized may execution proceed:

1. reconcile repository and private hashes;
2. verify OOS access counters remain zero;
3. build and fully validate dataset Run A and Run B;
4. build and fully validate candidate Run A and Run B;
5. build and fully validate feature/label Run A and Run B;
6. build and fully validate corpus Run A and Run B;
7. compare canonical bytes and result objects;
8. atomically publish only complete PASS artifacts;
9. audit the published root;
10. stop before training.

## 18. Determinism and Conservation Gates

Both clean runs must prove equal ordered identities, byte-identical manifests, equal exclusions,
equal session and partition assignments, raw-row-to-bar conservation, bar-to-session conservation,
candidate-to-feature/label conservation, integer volume conservation, and identical authority flags.

Timestamp, source, calendar, roll, identity, count, volume, or byte drift is a STOP condition.

## 19. Authority Boundary

Neither this readiness record nor any future `VALID` corpus authorizes:

- model fitting, fine-tuning, calibration, or hyperparameter search;
- final OOS access or evaluation;
- strategy selection, BUY/SELL output, execution, or PnL claims;
- runtime integration, package exports, configuration, or trading.

Those require later separately scoped decisions and independent validation.

## 20. Exact 48-Case Audit Matrix

1. HEAD equals local origin/main.
2. Live remote main equals HEAD.
3. Exact one-file documentation scope holds.
4. Pre-existing untracked proposals remain untouched.
5. Corpus freeze-lift hash matches.
6. Dataset-builder hash matches.
7. Candidate-builder hash matches.
8. Feature/label-builder hash matches.
9. Corpus-builder hash matches.
10. Corpus-test hash matches.
11. Corpus-checkpoint hash matches.
12. Calendar result status is VALID.
13. Calendar version is exact and nonempty.
14. Calendar requested-date count is 255.
15. Calendar interval count is 252.
16. Partition counts are exactly 150/50/55.
17. Normalized calendar hash matches.
18. Official CME notice hash matches.
19. Runtime tzdata version is recorded.
20. Two-run normalized calendar bytes are identical.
21. OOS and embargo rows were not synthesized.
22. Calendar admitted no source bars or volume.
23. Raw intake manifest hash matches current bytes.
24. Calendar manifest hash matches current bytes.
25. Calendar README hash matches current bytes.
26. Calendar checkpoint hash matches current bytes.
27. Old proposal private-control hashes are detected as stale.
28. Canonical raw contract rows are present.
29. Frozen OOS row remains metadata-only.
30. Independent dataset output root is absent.
31. Independent candidate output root is absent.
32. Independent feature/label output root is absent.
33. Independent corpus output root is absent.
34. Closed Phase A evidence is not relabelled.
35. Closed Phase B evidence is not relabelled.
36. Calendar VALID does not imply dataset VALID.
37. Missing upstream evidence yields UNKNOWN/NOT_READY.
38. Malformed evidence would outrank UNKNOWN as INVALID.
39. No candidate or label statistics are inferred.
40. No final OOS payload is opened.
41. No private artifact is created or mutated.
42. No existing untracked document is changed.
43. Focused corpus tests pass cache-disabled.
44. Full `tests` suite passes cache-disabled.
45. Bare-root pytest ACL collection distinction is recorded, not hidden.
46. Diff formatting and exact scope pass.
47. No training, integration, execution, or trading authority is granted.
48. Rollback, promotion, and STOP conditions are explicit.

## 21. Verification Evidence

Fresh cache-disabled verification on `2026-08-25`:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 1.91s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2519 passed in 23.17s
```

A bare-root invocation attempted to collect protected private evidence directories and stopped
with three `PermissionError` collection errors. The explicit repository suite is `tests`; private
ACLs were not weakened and no test failure was concealed.

## 22. Promotion Gates

This decision may be staged and locally committed only after semantic, structural, hash, scope,
formatting, full-content, and cached-diff audits pass. Push requires a new exact GitHub export
authorization.

Publication of this record authorizes only the next documentation proposal in Section 16, never
private execution.

## 23. Rollback and Stop Conditions

Before commit, rollback is deletion of this new file only. After commit, rollback is a normal
forward revert of its exact commit. No destructive reset or private-evidence deletion is allowed.

STOP on dependency or private-control drift, missing or malformed calendar rows, source ambiguity,
output collision, OOS contact, insufficient candidate or label evidence, partition leakage,
conservation failure, non-determinism, regression failure, scope expansion, training, integration,
or trading authority.

## 24. Final Decision and Resume Boundary

The calendar blocker is resolved, but independent pretraining-corpus execution is not yet ready.
The exact state is:

`POST_CALENDAR_PASS_UPSTREAM_RESULTS_MISSING_REQUIRE_PROSPECTIVE_ATOMIC_BUILD_PROPOSAL_NO_EXECUTION_NO_TRAINING_NO_OOS`.

After independent audit and local commit of this record, stop before push. The next single task is
the Section 16 documentation-only proposal. No private run, corpus build, feature/label execution,
training, OOS, integration, or trading operation is authorized here.
