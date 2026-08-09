# GC Futures Phase-A Pilot V3 Split-Session Rebuild Change Proposal

## 1. Proposal Record

- Proposal ID: `GC-PHASE-A-PILOT-V3-SPLIT-SESSION-REBUILD-PROPOSAL-V1`.
- Date: `2026-08-09`.
- Baseline commit: `d49a28fcf6161e8abee518938e06050c5ce6a0b6`.
- Baseline parent: `2edbcf7b0c6ca70f856c8d0e200c5d82f8c0466e`.
- Baseline subject: `docs: propose Phase A structural seed private run`.
- Classification: documentation-only deterministic rebuild and correction-gate record.
- Current decision: `BLOCKED_PENDING_SOURCE_COVERAGE_IDENTITY_CONTRACT_CORRECTION`.

This record defines the intended non-overwriting V3 rebuild of the accepted Phase-A engineering
pilot. It also records a fail-closed discrepancy discovered before private execution: the accepted
split-session decision requires SOURCE and COVERAGE identities to remain unchanged from V2, but the
committed V3 identity builder includes the V3 builder version in every identity kind. The rebuild is
therefore specified but not authorized until that discrepancy is corrected and independently
accepted.

## 2. Decision Summary

The accepted private pilot is a valid, Git-ignored, non-promotable V2 engineering artifact. The
current committed builder is `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. Its single-interval calendar
semantics are intended to remain compatible with the V2 pilot, while SEGMENT and DATASET identities
must rebase to V3.

The accepted split-session proposal explicitly locks SOURCE and COVERAGE identities as unchanged.
Read-only inspection proves the current implementation instead constructs a common identity payload
containing `"version":"GC-DATASET-BUILDER-V3-SPLIT-SESSION"` for SOURCE, COVERAGE, SEGMENT, and
DATASET. The V2 implementation used `"version":"GC-DATASET-BUILDER-V2"` for those same kinds.
Public identity-builder evaluation against immutable provenance metadata therefore produces
different SOURCE and COVERAGE IDs for all three contracts.

This is a semantic contract defect, not an acceptable expected-output difference. No V3 private
rebuild may begin, no V2 ID may be relabeled, and no accepted proposal may be silently revised by
execution. The exact next prerequisite is a bounded, test-first correction preserving V2 SOURCE and
COVERAGE identity vectors while retaining V3 SEGMENT/DATASET identity rebasing.

## 3. Verified Repository Baseline

At this proposal baseline:

- `HEAD` is `d49a28fcf6161e8abee518938e06050c5ce6a0b6`;
- local `origin/main` is `2edbcf7b0c6ca70f856c8d0e200c5d82f8c0466e`;
- `HEAD` is one local documentation commit ahead of `origin/main`;
- the tracked worktree and index are clean;
- three pre-existing untracked documentation files remain outside scope and untouched;
- the accepted V2 root exists at
  `private_data/sierra_chart/gc_2026_phase_a_pilot/`;
- the reserved V3 rebuild root
  `private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/` is absent;
- the structural V3 private root is absent;
- private V3 rebuild, structural execution, candidate execution, feature/label execution, training,
  OOS evaluation, integration, and trading have not begun.

Historical committed test evidence is not rerun by this documentation task: the split-session
builder checkpoint records exact `48` logical cases, `239` focused passes, and `2156` full-regression
passes. Later repository regression evidence exists, but it does not repair the missing V2-to-V3
identity-vector assertion.

## 4. Exact Documentation-Only Scope

This task may create and correct only:

`docs/gc_futures_phase_a_pilot_v3_split_session_rebuild_change_proposal.md`

It may read committed source, tests, documentation, Git metadata, and immutable private metadata.
It may evaluate public deterministic identity builders read-only against metadata. It must not parse
private derivative rows, call `build_gc_futures_dataset()`, create private output, modify source or
tests, access OOS outcomes, train, integrate, stage another path, or push.

After independent audit, exact-path staging and one local documentation commit are allowed for this
file only. Push, source correction, and private execution remain separately gated.

## 5. Authority and Global Freeze

The global code freeze remains active. This proposal grants no authority to:

- modify the accepted V2 root or any acquisition artifact;
- create the V3 root or invoke the dataset builder on private exports;
- change identity code, tests, checkpoint, exports, requirements, or configuration;
- run structural, candidate, feature/label, model, training, backtest-promotion, OOS, strategy,
  execution, risk, broker, trace, or integration workflows;
- upload private evidence to a local or remote model;
- stage, commit, or push any path other than this exact documentation file under its bounded local
  acceptance workflow.

A reserved path, passing historical tests, or deterministic projected identity is not execution
authority.

## 6. Accepted Immutable V2 Pilot

The accepted historical root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

Its locked V2 evidence includes:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- builder version: `GC-DATASET-BUILDER-V2`;
- builder source SHA-256:
  `9A3519DA97C0AA526EC4A5A8C867B5BF14AE514BA156F6A11ADDD410B66C1858`;
- builder-test SHA-256:
  `DFCE06D6C9B8EECD10504F35D092D6A0652434D7A995C846E8A797F08919F9C3`;
- build-manifest SHA-256:
  `55CA87E55988F9FF27C7C177DBB16813ACFD9096DCB37C370F70A936EDBA4F4C`;
- dataset ID: `81e40b6bfc397caf859226ebf16328562a9b8cc148a1cafae9075dc0f82140d8`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- calendar SHA-256:
  `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`;
- status `VALID`, reason `CANONICAL_DATASET_BUILT`, and no blocking reasons;
- parsed rows `15412`, eligible rows/development bars `7103`, OOS bars `0`, excluded rows `8309`;
- raw volume `4742010`, eligible volume `3829577`, excluded volume `912433`;
- segments `54`, missing bars `73`, completed-session volume members `58`, roll dates `()`;
- raw range `2026-02-17T23:05:00.000000Z` through
  `2026-03-30T21:00:00.000000Z`;
- usable range `2026-02-22T23:05:00.000000Z` through
  `2026-03-30T21:00:00.000000Z`;
- coverage digest `002734838874446ce4305f7d73664187400556b6b161ebb34d0e7b64b50b43d6`;
- `frozen_oos_outcome_accessed=false`, `training_allowed=false`,
  `integration_allowed=false`, and `promotion_allowed=false`.

These values are comparison evidence only. They are not a V3 manifest and must never be copied into
a V3 result without public recomputation.

## 7. Exact Immutable Runtime Inputs

Only seven accepted private files may become runtime inputs after all prerequisites pass. Their
bytes remain in the V2 root and are referenced, not copied or changed:

| Runtime input | Bytes | SHA-256 |
|---|---:|---|
| `calendar_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `8811` | `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED` |
| `GCG26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `3104` | `27552A778ABF2FB158D7107EFF9232396C9AAE5E489A55B50259923C379BE839` |
| `GCG26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2627` | `C49B4BA7CD03ECD649E8A13DDF7D0CD2AA2393838CD5C6D810256DFE7ED3C941` |
| `GCJ26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `818320` | `6E0419AF7E85BF5C31A5F79AA36ADEED1A9B1D8BF3123CBB8DDA7AF1313EED3A` |
| `GCJ26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2991` | `D2A64844EF65B8E8B11D643FB553AB4A70BDF16C96E78F8E98CBEAE75573E79A` |
| `GCM26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `733413` | `30ABDCBC2F41498EF36C734EA28780B62E7338882543D41A6FDDB33472036F3D` |
| `GCM26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2963` | `D84B9E8297B21CE47C1188B637FF67886AC1BFE72A1C5DE8981EF957A7D3F52B` |

The V2 build manifest, validation report, README, audits, and checkpoints are historical comparison
evidence only and are forbidden as runtime dataclass substitutes.

## 8. Accepted Current Dependency Bytes

Any future correction, readiness audit, or private rebuild stops on unreviewed drift from:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121` |
| `tests/test_gc_dataset_builder.py` | `4D179ED76198DA44263535FA497B2E2B8D67F2FAFEA4C3F8A6DC63A32F267974` |
| `docs/gc_futures_split_session_calendar_change_proposal.md` | `D2B6968527F3A19423B3535FA19AB57C008691CFFFF2B07863D1FC2BC2710923` |
| `docs/gc_futures_split_session_calendar_checkpoint.md` | `D7F9261347C931FC5C897CA8330016C9AA974A69199A181D29F02CD519BC7760` |
| `docs/gc_futures_phase_a_structural_seed_private_run_change_proposal.md` | `6117863D6874B7DA34A81EECADCA68654BBFDE89D1A966299DB20BF3FDCEAD20` |

The accepted formal statement in the split-session proposal is authoritative: SOURCE and COVERAGE
identities remain unchanged; SEGMENT and DATASET identities intentionally rebase under V3 calendar
and version evidence.

## 9. Proven SOURCE/COVERAGE Identity Defect

Read-only use of the committed public `make_gc_dataset_id()` against exact provenance metadata
produced these diagnostic vectors:

| Contract | Accepted V2 SOURCE | Current V3-projected SOURCE | Equal |
|---|---|---|---|
| `GCG26-COMEX` | `1a8c876a57852d07c9bcd068c36c0c2244057ca13cc9e737d0909962e7c2cac1` | `0dc1a8c9c0cf882ec16675a967b4bcd3194596771c3d1276a082cbd341b95584` | `false` |
| `GCJ26-COMEX` | `863aaff9e97cd8448a3edb008639e00be4bd0e35bcb72af8e9ed3a083a661a5e` | `ceb64f3eb6d5a298a8679d9c3dfbf83c51255f3e009db3dddd843a0e941c135e` | `false` |
| `GCM26-COMEX` | `84a5b8e5599c6dce1bf06599c6cdefad7d27118a13ea86b856c1c9427d6c8918` | `c4693938f24c2b9e2ad355f021516845715893b15d31bb55d7558a5b6730da2b` | `false` |

| Contract | Accepted V2 COVERAGE | Current V3-projected COVERAGE | Equal |
|---|---|---|---|
| `GCG26-COMEX` | `c0a728eec42ca9cc692e3776ce83e95e99884ce3bfaad84d96adda6ef4505290` | `85945722c3b5d4822b017944818b14a2ec137b030de8caf8622ca2905b236bbf` | `false` |
| `GCJ26-COMEX` | `35092c5d8e97251a6cf2afa323ae8195cfb4ba9675b51c8cd784c3ce75bb92c6` | `4ca40bb13c0fc70b341b30a763866fdf93bc2099c72a4d7ca24f5d532f44104e` | `false` |
| `GCM26-COMEX` | `1030b2cb66bf3154deeed18528d94f8fc5ba7357563dc9c6e00fe50c25eba205` | `375745d010e90d1a857f506f40adac986db7d5c891c6b3995918da3b0f82f9ff` | `false` |

The difference is deterministic and caused by the builder version inside the common identity
payload. These projected values are diagnostics, not accepted V3 source or coverage identities.
Running the full builder with this known mismatch is forbidden.

## 10. Required Bounded Correction Contract

Before private rebuild authority, a separate exact three-path, test-first correction must be
accepted for only:

- `analysis/gc_dataset_builder.py`;
- `tests/test_gc_dataset_builder.py`;
- `docs/gc_futures_split_session_calendar_checkpoint.md`.

The correction must:

1. preserve all six accepted V2 SOURCE/COVERAGE regression vectors exactly under V3;
2. retain the exact public API and export list;
3. keep SEGMENT and DATASET identities bound to `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
4. keep the V3 manifest version unchanged;
5. preserve the split-session calendar discriminator and digest behavior;
6. add explicit cross-version tests so the boundary cannot regress;
7. prove all focused and full regressions pass;
8. update only the exact checkpoint evidence and hashes;
9. perform no private rebuild, training, OOS, or integration.

Changing the accepted proposal to permit SOURCE/COVERAGE rebasing is not authorized by this record.
If preservation is technically impossible without a broader contract change, execution stops for a
new documentation decision rather than silently widening scope.

## 11. Exact Future Public Reconstruction API

After correction acceptance, the rebuild may use only:

```python
parse_sierra_chart_gc_export(
    *,
    source_name: str,
    contract: str,
    role: GCSourceRole,
    capture_timestamp: datetime,
    chart_timezone: str,
    timeframe: str,
    raw_bytes: bytes,
) -> GCSierraChartExport

build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
    calendar_entries: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult
```

Each derivative is parsed exactly once. Each provenance object is reconstructed into the exact
frozen `GCSierraChartCoverageEvidence` fields. Each calendar member is reconstructed into the exact
frozen `KillZoneCalendarEntry` fields. The builder is called exactly once. No private helper,
JSON-to-result shortcut, pickle, `eval`, monkeypatch, manual identity, silent sort, row repair, or V2
manifest deserialization is allowed.

## 12. Exact Future Frozen Input Contracts

The reconstruction must use these exact public frozen contracts:

```text
GCSierraChartCoverageEvidence(
  coverage_id, source_id, source_name, source_sha256, contract, role,
  capture_timestamp, chart_timezone, timeframe, coverage_start_timestamp,
  coverage_end_timestamp, acquisition_completed_timestamp,
  acquisition_evidence_sha256
)

KillZoneCalendarEntry(
  calendar_version, trade_date, session_status,
  session_open_timestamp, session_close_timestamp
)

GCDatasetBuildConfig(
  instrument, timeframe, source_timezone, exchange_timezone,
  timezone_data_version, tick_size, initial_contract, initial_trade_date,
  roll_confirmation_sessions, oos_start_trade_date, oos_end_trade_date
)
```

The pilot calendar has exactly `29` `OPEN` single-interval members, from trade date `2026-02-18`
through `2026-03-30`. It must remain represented by `KillZoneCalendarEntry`, not converted into
synthetic split-session entries merely to exercise the new type.

## 13. Exact Future Build Configuration

The only admissible future configuration is:

```text
instrument="GC"
timeframe="5M"
source_timezone="Asia/Tokyo"
exchange_timezone="America/New_York"
timezone_data_version="2026.2"
tick_size=Decimal("0.1")
initial_contract="GCJ26-COMEX"
initial_trade_date=date(2026, 2, 23)
roll_confirmation_sessions=3
oos_start_trade_date=date(2026, 3, 31)
oos_end_trade_date=date(2026, 3, 31)
```

Runtime tzdata must report exact normalized version `2026.2`, and `America/New_York` and
`Asia/Tokyo` must load successfully. Config drift, runtime timezone drift, or calendar-version drift
stops before parsing any private derivative.

## 14. Ordering, Coverage, and Calendar Contract

Runtime tuples must preserve canonical contract order `GCG26-COMEX`, `GCJ26-COMEX`,
`GCM26-COMEX`. Coverage evidence mirrors the same order. Calendar members are independently
strictly increasing by trade date and use their existing ordered tuple bytes.

Coverage remains:

- GCG: `[2026-02-17T23:00:00Z, 2026-02-25T11:45:00Z)`, with only the already authorized
  acquisition-attested initial no-trade interval `[23:00,23:20)`;
- GCJ: `[2026-02-17T23:00:00Z, 2026-03-30T21:00:00Z)`;
- GCM: `[2026-02-17T23:00:00Z, 2026-03-30T21:00:00Z)`.

No interval may be inferred from filesystem timestamps or observed rows. No missing slot may be
filled. No calendar member may be inserted, deleted, widened, split, merged, or repaired.

## 15. V2-to-V3 Compatibility and Identity Expectations

After the correction, V3 single-interval compatibility must prove:

- SOURCE IDs equal the accepted V2 SOURCE IDs;
- COVERAGE IDs equal the accepted V2 COVERAGE IDs;
- parsed rows, eligible rows, development bars, OOS bars, excluded rows, volumes, completed-session
  volumes, missing count, roll dates, segment membership, partitions, and boundaries equal V2;
- every SEGMENT ID differs from its corresponding V2 segment ID because the SEGMENT identity is
  V3-bound;
- DATASET ID differs from the V2 dataset ID because V3 version, V3 segment IDs, and the
  type-discriminated calendar digest are identity-bearing;
- manifest version equals `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- status remains `VALID`, reason remains `CANONICAL_DATASET_BUILT`, and blocking reasons remain
  empty.

Semantic equality must be independently compared field-by-field. It may not be inferred from equal
counts or from the formal proposal. Any unexpected difference stops and publishes no accepted V3
root.

## 16. Exact Future Private Output Root

After correction, post-push readiness, and a new explicit private execution authorization, the only
future root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`

It must be absent before execution, Git-ignored, and sibling to the immutable V2 root. The V2 root
must never be renamed, moved, overwritten, or used as the V3 destination. No output enters source,
tests, fixtures, docs, model, training, backtest, or integration directories.

## 17. Exact Future Output Artifact Set

The future V3 root may contain only:

1. `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
2. `build_result_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
3. `v2_v3_comparison_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
4. `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
5. `README_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
6. `artifact_manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json`.

No derivative, provenance sidecar, calendar, raw export, notebook, script, cache, fixture, prompt,
model artifact, or ad hoc log is duplicated into the V3 root. The artifact manifest binds the other
five files; its own hash is recorded later by an external private checkpoint, avoiding circular
self-hashing.

## 18. Deterministic Serialization and Binding

Machine artifacts use UTF-8 without BOM, LF, exactly one terminal newline, lexically sorted object
keys, `separators=(",", ":")`, and `ensure_ascii=True`. Tuples remain ordered arrays.

Values serialize as:

- UTC timestamps: ISO-8601 microseconds with terminal `Z`;
- dates: `YYYY-MM-DD`;
- finite Decimal values: canonical fixed text;
- enums: exact `.value`;
- identities: lowercase 64-hex;
- artifact hashes: uppercase 64-hex;
- booleans: JSON booleans.

Input binding records this proposal ID/hash, execution commit, corrected builder/test/checkpoint
hashes, every Section 7 input hash/byte length, V2 comparison-manifest hash, exact config, calendar
version, runtime tzdata, API signatures, and exact parser/builder call counts `3/1`.

The build result serializes the complete public V3 result, manifest, ordered segments, and bars.
The comparison artifact binds every Section 15 equality/difference assertion. The artifact manifest
binds exact names, hashes, byte lengths, status, V3 dataset ID, ordered segment IDs, and an overall
deterministic artifact-set identity.

## 19. Atomic Publication and Immutable Failure Handling

All six artifacts are assembled in a new task-specific temporary directory inside the private
parent. The final V3 root is created only by one atomic move after all checks pass. The final root is
never partially populated.

On any failure:

- the final V3 root remains absent;
- temporary output is quarantined as explicitly nonaccepted or removed only under the future
  execution task's exact rollback authority;
- the V2 root remains byte-immutable;
- no result is repaired, overwritten, relabeled, or partially promoted;
- no structural or downstream operation starts.

An exception, non-`VALID` status, mismatched comparison, extra file, identity discrepancy,
nondeterminism, or scope drift is a failed run.

## 20. Independent Validation and Repeatability

Future acceptance must independently verify:

- all input, dependency, proposal, and output hashes;
- exact public signatures, frozen dataclasses, enums, constants, and exports;
- exact parser call count `3` and builder call count `1`;
- V3 identity recomputation for every source, coverage item, segment, and dataset;
- all V2/V3 comparison assertions in Section 15;
- row, volume, exclusion, partition, completed-session, missing-slot, and roll conservation;
- zero OOS bars and unopened OOS outcomes;
- canonical JSON lossless round-trip;
- a separately authorized independent repeat producing object-equal results and byte-identical
  machine artifacts;
- exact six-file output scope and Git-ignore evidence;
- unchanged V2 root, source, tests, unrelated private roots, index, HEAD, and origin/main;
- `TRAINING_STARTED=false`, `STRUCTURAL_RUN_PERFORMED=false`,
  `OOS_OUTCOME_ACCESSED=false`, and `INTEGRATION_STARTED=false`.

This rebuild proves only deterministic builder compatibility on one non-promotable pilot. It cannot
claim strategy edge, profitability, model quality, generalization, or trading readiness.

## 21. Inline Synthetic Exact 48-Case Future Matrix

The bounded correction and later private rebuild must cover this exact sequential logical matrix.
Parameterization may expand test executions without changing the `48` logical cases.

1. Current V3 SOURCE identity differs from the locked V2 vector before correction.
2. Current V3 COVERAGE identity differs from the locked V2 vector before correction.
3. Corrected GCG SOURCE identity equals its exact V2 vector.
4. Corrected GCJ SOURCE identity equals its exact V2 vector.
5. Corrected GCM SOURCE identity equals its exact V2 vector.
6. Corrected GCG COVERAGE identity equals its exact V2 vector.
7. Corrected GCJ COVERAGE identity equals its exact V2 vector.
8. Corrected GCM COVERAGE identity equals its exact V2 vector.
9. SEGMENT identity remains V3-version-sensitive.
10. DATASET identity remains V3-version/calendar-sensitive.
11. V3 manifest version remains exact.
12. Split-session calendar digest remains type-discriminator-sensitive.
13. Public builder signatures and exports remain unchanged.
14. Existing focused and full regressions pass after correction.
15. Missing corrected dependency acceptance blocks private parsing.
16. Missing or existing final V3 root blocks execution.
17. Any immutable input hash or byte-length drift blocks execution.
18. Extra, missing, duplicate, renamed, or reordered runtime input blocks execution.
19. Runtime timezone/tzdata/config mismatch blocks execution.
20. Every derivative is parsed exactly once in canonical contract order.
21. Parser output SOURCE IDs equal accepted V2 vectors.
22. Coverage dataclasses fully reconcile and equal accepted V2 vectors.
23. All 29 calendar members remain ordered single-interval `OPEN` entries.
24. Calendar conversion to synthetic split entries is rejected.
25. Public builder is called exactly once with exact tuple order and config.
26. Non-`VALID` result publishes no accepted V3 root.
27. `VALID` requires exact reason and empty blocking reasons.
28. Parsed, eligible, development, OOS, and excluded counts equal V2.
29. Raw, eligible, excluded, and completed-session volumes equal V2.
30. Missing-slot, attested no-trade, roll-date, and exclusion evidence equal V2.
31. Segment count, membership, boundaries, partition, and order equal V2.
32. Every V3 segment ID differs from the corresponding V2 ID and recomputes exactly.
33. V3 dataset ID differs from V2 and recomputes exactly.
34. Unexpected semantic difference stops rather than being normalized.
35. V2 manifest is comparison evidence, never a runtime dataclass shortcut.
36. No row sort, fill, repair, aggregation, mutation, or filesystem inference occurs.
37. Canonical serialization preserves exact nested types and order.
38. Input binding contains every required proposal/dependency/input/config field.
39. Comparison artifact exhaustively records expected equalities and differences.
40. Artifact manifest binds each other output exactly once.
41. Exact six-file scope rejects every extra or forbidden artifact.
42. Temporary publication is atomic and exposes no partial final root.
43. Failure preserves immutable V2 bytes and leaves final V3 root absent.
44. Independent repeat is object-equal and machine-byte-identical.
45. Clock, host path, locale, filesystem order, and hash iteration do not affect bytes.
46. OOS, structural, candidate, feature/label, training, and integration surfaces remain unused.
47. Git index, HEAD, origin/main, source, tests, and unrelated private roots remain unchanged.
48. Accepted V3 pilot authorizes only a separate structural-run proposal revision/readiness audit,
    never automatic structural execution or downstream promotion.

## 22. Rollback and Quarantine

This documentation task rolls back by deleting only this uncommitted file. After commit, rollback
requires a bounded revert commit; history rewriting is forbidden.

The future code correction rolls back only through a bounded revert of its exact three files. The
future private rebuild rolls back only its newly created V3 root or quarantined temporary directory.
Neither rollback may alter the accepted V2 root, acquisition evidence, calendar, other private
roots, or unrelated Git state.

No rollback path permits training, integration, OOS access, or broad deletion.

## 23. Promotion and Immediate Stop Conditions

Private rebuild requires all of the following:

1. this proposal is independently accepted, committed, and pushed;
2. the exact three-path SOURCE/COVERAGE correction is explicitly authorized, implemented
   test-first, independently audited, committed, and pushed;
3. corrected dependency hashes and cross-version vectors are recorded;
4. a post-push rebuild-readiness audit passes;
5. the V3 private root remains absent and all seven input hashes remain exact;
6. a new explicit private rebuild authority binds exact input/dependency/proposal bytes and output
   scope.

Stop immediately on identity-contract ambiguity, proposal/source mismatch, failed regression,
private input drift, root collision, timezone drift, malformed evidence, silent sort or repair,
unexpected semantic change, non-`VALID` result, OOS contact, nondeterminism, exception leakage,
partial publication, scope expansion, model access, training, structural/candidate/feature-label
execution, integration, stage, commit, or push without exact authority.

There is no automatic promotion path.

## 24. Final Decision and Next Single Task

The deterministic V3 private rebuild contract is fully specified, but execution readiness is
`BLOCKED_PENDING_SOURCE_COVERAGE_IDENTITY_CONTRACT_CORRECTION`.

The next single technical task, after this documentation acceptance and push workflow, is the exact
three-path test-first correction reserved in Section 10. It must preserve all accepted V2 SOURCE and
COVERAGE vectors while retaining V3 SEGMENT/DATASET behavior. Private rebuild remains forbidden
until that correction is independently accepted and a separate readiness audit passes.

For this turn, the only authorized terminal action is local acceptance of this one documentation
file. Stop before push, Python/source/test correction, private rebuild, structural execution,
training, OOS, or integration. The global code freeze remains active everywhere else.
