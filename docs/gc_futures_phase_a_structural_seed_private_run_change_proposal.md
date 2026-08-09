# GC Futures Phase-A Structural-Seed Private-Run Change Proposal

## 1. Proposal Record

- Proposal ID: `GC-PHASE-A-STRUCTURAL-SEED-PRIVATE-RUN-PROPOSAL-V1`.
- Date: `2026-08-09`.
- Baseline commit: `2edbcf7b0c6ca70f856c8d0e200c5d82f8c0466e`.
- Baseline subject: `feat(analysis): add GC Candidate Evidence builder`.
- Classification: documentation-only private-execution boundary and readiness record.
- Current decision: `BLOCKED_PENDING_V3_PILOT_REBUILD`.

This record defines the only admissible future path from an accepted immutable Phase-A GC dataset
to private canonical structural-seed evidence. It deliberately does not authorize that execution.
The currently stored pilot was built by dataset builder V2, while the committed public dataset
builder and structural validator are V3. That version and identity mismatch is a mandatory
fail-closed prerequisite, not a formatting difference.

## 2. Decision Summary

The standalone structural-seed source, focused tests, checkpoint, and downstream candidate builder
are committed. The accepted private pilot is present, Git-ignored, non-promotable, and contains no
OOS bars. The structural private output root is absent.

However, the private pilot manifest binds:

- builder version `GC-DATASET-BUILDER-V2`;
- builder source SHA-256
  `9A3519DA97C0AA526EC4A5A8C867B5BF14AE514BA156F6A11ADDD410B66C1858`;
- builder-test SHA-256
  `DFCE06D6C9B8EECD10504F35D092D6A0652434D7A995C846E8A797F08919F9C3`;
- dataset ID `81e40b6bfc397caf859226ebf16328562a9b8cc148a1cafae9075dc0f82140d8`.

The committed builder now binds:

- version `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- source SHA-256
  `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121`;
- builder-test SHA-256
  `4D179ED76198DA44263535FA497B2E2B8D67F2FAFEA4C3F8A6DC63A32F267974`.

`validate_gc_structural_seed_evidence()` calls the committed structural builder, whose manifest
validator requires `manifest.version == GC_DATASET_BUILDER_VERSION` and recomputes every segment
identity under the current builder contract. Direct JSON-to-dataclass reconstruction, accepting the
old dataset ID, or relabeling V2 bytes as V3 would violate the accepted identity boundary.

Therefore the structural private run is not ready. A separate deterministic V3 pilot rebuild must
produce and independently accept a new private dataset identity before this proposal can be revised
or execution can be authorized.

## 3. Verified Repository Baseline

At the baseline:

- `HEAD`, local `origin/main`, and the pushed implementation commit equal
  `2edbcf7b0c6ca70f856c8d0e200c5d82f8c0466e`;
- the tracked worktree and index are clean;
- three pre-existing untracked documentation files are outside this proposal and remain untouched;
- the accepted private pilot root exists at
  `private_data/sierra_chart/gc_2026_phase_a_pilot/` and is ignored by Git;
- `private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence/` is absent;
- `private_data/sierra_chart/gc_2026_phase_a_candidate_evidence/` is absent;
- structural private execution, candidate private execution, feature/label execution, training,
  model fitting, OOS evaluation, strategy integration, and trading have not begun.

Historical test evidence remains evidence only and is not rerun by this documentation task:

- structural seed: `62` focused executions, `2218` full regression executions, exact `48` logical
  cases;
- candidate evidence: `52` focused executions, `2270` full regression executions, exact `48`
  logical cases.

## 4. Exact Documentation-Only Scope

This task may create and correct only:

`docs/gc_futures_phase_a_structural_seed_private_run_change_proposal.md`

It may read committed source, tests, documentation, Git metadata, and immutable private manifest
metadata. It must not modify Python, tests, fixtures, private data, manifests, calendars,
requirements, configuration, package exports, integration wiring, or any other documentation.

After independent audit, exact-path staging and one local documentation commit are allowed for this
file only. Push and private execution remain separately gated.

## 5. Authority and Global Freeze

The global code freeze remains active. This record grants no authority to:

- rebuild or mutate the pilot;
- invoke the structural builder on private evidence;
- create, overwrite, repair, rename, or delete private evidence;
- invoke the candidate builder or feature/label builder;
- train, tune, fit, select, backtest for promotion, inspect OOS outcomes, or claim edge;
- change strategy, risk, broker, execution, trace, engine, runtime, or integration behavior;
- send private data to a local or remote language model;
- stage, commit, or push anything except this exact documentation file under separately confirmed
  local Git authority.

No future permission is inferred from a reserved path, committed implementation, passing unit
tests, or the existence of private V2 evidence.

## 6. Accepted Private Pilot Evidence

The present private root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

Its immutable recorded identity is:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- build-manifest SHA-256:
  `55CA87E55988F9FF27C7C177DBB16813ACFD9096DCB37C370F70A936EDBA4F4C`;
- calendar SHA-256:
  `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- timezone: `America/New_York`;
- timezone-data version: `2026.2`;
- development bars: `7103`;
- OOS bars: `0`;
- canonical segments: `54`;
- acquisition-attested missing parent slots: `73`;
- roll trade dates: `()`.

These facts remain accepted as historical V2 engineering evidence. They do not authorize reuse as
a V3 runtime object, training data, final 2024-2025 research evidence, or production data.

## 7. Mandatory V2-to-V3 Rebuild Boundary

Builder version is identity-bearing. The V3 split-session implementation intentionally separates
V3 dataset, segment, source, and coverage identities from V2. A V2 manifest cannot pass the current
structural validator because:

1. `manifest.version` is V2 instead of `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
2. current segment and dataset identities are recomputed with the V3 version constant;
3. current public builder bytes differ from the V2 bytes recorded by the private manifest;
4. current public tests differ from the V2 tests recorded by the private manifest;
5. the accepted split-session contract forbids silently treating identity mutation as compatible
   reconstruction.

The V3 rebuild must start from the same immutable bounded derivative sources, coverage evidence,
calendar bytes, and locked configuration. It must call the current public builder exactly once and
must publish under a new private immutable root. It must not overwrite or relabel the V2 root.

Any assumption that V3 will retain dataset ID, segment IDs, counts, reasons, or manifest bytes is
forbidden. Those values must be observed, validated, and independently accepted after the rebuild.

## 8. Accepted Committed Dependency Bytes

Any future readiness revision or private execution must stop on drift from these audited artifacts:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121` |
| `tests/test_gc_dataset_builder.py` | `4D179ED76198DA44263535FA497B2E2B8D67F2FAFEA4C3F8A6DC63A32F267974` |
| `analysis/gc_feature_label_builder.py` | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `analysis/gc_structural_seed_evidence.py` | `B799EE739ECE289A57680007D85566645EE1615B0E20F87C99A4278217AE9AAE` |
| `tests/test_gc_structural_seed_evidence.py` | `CFD789AE272B621EC04CC463A5EE506C22B3221A3F18EA6C737999042420958E` |
| `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md` | `75C0D52D58BF2C8168806893FF68B0F567F19401FFA0DABE3EC0DB8A970094E1` |
| `analysis/gc_candidate_evidence_builder.py` | `B0D361A1C0F19AEB6D49627D00599CBDF6E4A06E6F70C10F0A9A2EB467783A68` |
| `tests/test_gc_candidate_evidence_builder.py` | `090668870F4AD4C49AB540D9E64D2E53BD07657D743FAE391C48CF73C5584116` |
| `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md` | `DA7F657FFB2D787E343E37E69571315D97128389F2594F007FEE9BD87574C5EC` |
| `docs/gc_futures_split_session_calendar_change_proposal.md` | `D2B6968527F3A19423B3535FA19AB57C008691CFFFF2B07863D1FC2BC2710923` |
| `docs/gc_futures_split_session_calendar_checkpoint.md` | `D7F9261347C931FC5C897CA8330016C9AA974A69199A181D29F02CD519BC7760` |

Hash equality is necessary but not sufficient. Exact public signatures, version constants,
dataclass fields, enum values, deterministic identities, and status semantics must also pass.

## 9. Exact Future Dataset Reconstruction Contract

After a separately accepted V3 rebuild, the private structural run must reconstruct the runtime
`GCDatasetBuildResult` once through only these public APIs:

- `parse_sierra_chart_gc_export()`;
- `build_gc_futures_dataset()`.

The exact future dataset call remains keyword-only:

```python
build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult
```

The exact configuration remains:

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

No JSON-to-dataclass shortcut, pickle, `eval`, private helper, partial equality, filesystem-order
inference, silent sort, repair, or V2 identity carry-forward is allowed.

## 10. Exact Future Structural Public API

Only these committed public operations may be used:

```python
build_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult

validate_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult
```

The exact structural configuration is the frozen `GCStructuralSeedConfig` with public fields
`swing_left_bars=2`, `swing_right_bars=2`, and `break_buffer_ticks=1`. The structural builder and
validator accept that configuration only through their keyword-only public function boundary. The
seed version is `GC-STRUCTURAL-SEED-V1`. No adapter, monkeypatch, subclass, package re-export,
manual identity, or altered configuration is allowed.

## 11. Dataset Admissibility Gate

Before any structural derivation, the rebuilt dataset must independently prove all of the following:

1. status is exactly `GCDatasetBuildStatus.VALID`;
2. the manifest version is exactly `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
3. dataset ID and every segment ID recompute under current public identities;
4. source, coverage, calendar, timezone-data, row, volume, segment, partition, and reason evidence
   exactly match the accepted V3 rebuild checkpoint;
5. development bars, OOS bars, segment count, missing-slot count, and roll dates reconcile to the
   new V3 manifest without assuming the old V2 values;
6. OOS bar count is exactly zero;
7. frozen OOS outcomes were not opened or used;
8. no private input or manifest was modified after acceptance.

Any mismatch stops before `build_gc_structural_seed_evidence()` is called.

## 12. Structural Result Admissibility Gate

The private run calls `build_gc_structural_seed_evidence()` exactly once, then calls
`validate_gc_structural_seed_evidence()` exactly once with the same runtime dataset, exact config,
and returned seed.

Only these complete outcomes are admissible for private diagnostic publication:

- `VALID` with non-null canonical seed and reason `STRUCTURAL_EVIDENCE_VALID`;
- `NONE` with non-null dataset-bound canonical empty seed and reason
  `NO_STRUCTURAL_EVIDENCE`.

`INVALID`, `AMBIGUOUS`, or `UNKNOWN`, a null seed, differing build/validation result, exception,
unrecognized reason, nonempty blocking reasons on `VALID` or `NONE`, or partial result is a failed
run. A failed result publishes no accepted structural artifact.

## 13. Segment, Chronology, and No-Look-Ahead Boundary

The structural builder may consume only development-partition bars inside each canonical segment in
the exact supplied segment and bar tuple order. Local bar indices restart within each segment and
must never be flattened into a dataset-global chronology.

No state, lookback, swing, confirmation, displacement, event, or FVG formation crosses a segment
boundary. Validation/OOS bars cannot discover, confirm, retire, enrich, or invalidate development
evidence. A swing is first known at its exact confirmation bar; an event and context link are first
known only at their exact causal closing moment.

No future outcome, candidate, label, return, entry, exit, PnL, strategy choice, or later segment may
influence structural membership or identity.

## 14. Exact Future Private Output Root

After all prerequisites and a separate explicit execution authorization, the only private output
root is reserved as:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`

The `_v3` suffix is mandatory and prevents overwrite or confusion with the earlier reserved but
unused V2-era path. The old absent path remains unused:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence/`

The V3 root must be Git-ignored. No output may be copied into tests, fixtures, tracked docs,
training, model, backtest, integration, or runtime directories.

## 15. Exact Future Output Artifact Set

The future V3 private root may contain only:

1. `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
2. `structural_seed_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
3. `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
4. `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
5. `README_NON_PROMOTABLE_ENGINEERING_PILOT.md`.

The structural output references accepted dataset source and calendar hashes; it does not duplicate
raw exports, bounded derivatives, coverage sidecars, calendars, or full dataset manifests. No
external fixture, cache, notebook, image, model prompt, or ad hoc log is allowed in the output root.

## 16. Deterministic Serialization Contract

Machine-readable artifacts use UTF-8 without BOM, LF endings, exactly one terminal newline, and
canonical JSON with lexically sorted object keys, compact separators `(",", ":")`, and
`ensure_ascii=True`. Dataclass tuples serialize as ordered JSON arrays. Dictionaries may not encode
causal order.

Canonical value representations are:

- UTC timestamps: ISO-8601 microseconds with terminal `Z`;
- dates: ISO `YYYY-MM-DD`;
- finite Decimals: canonical fixed text, zero as `0.0`;
- enums: exact `.value`;
- identities: lowercase 64-hex strings;
- artifact SHA-256 values: uppercase 64-hex strings;
- booleans: JSON booleans, never integers or text.

Python `repr`, pickle, object addresses, hostnames, absolute paths, filesystem timestamps, current
clock time, random values, insertion-order accidents, or environment-specific exception text are
forbidden identity inputs. README and validation-report bytes are hashed by the manifest but do not
change the structural seed identity.

## 17. Input-Binding and Manifest Contract

`input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind at least:

- proposal ID and proposal-file SHA-256;
- exact source commit;
- all Section 8 dependency hashes;
- accepted V3 pilot root purpose and accepted V3 build-manifest SHA-256;
- V3 dataset ID, builder version, calendar version, timezone-data version, exact dataset config,
  counts, segments, partitions, missing slots, roll dates, reasons, and blocking reasons;
- structural version and exact structural config;
- explicit `frozen_oos_outcome_accessed=false`, `training_allowed=false`,
  `integration_allowed=false`, and `promotion_allowed=false`.

`manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind the SHA-256 and byte length of each other
artifact, exact build and validation statuses/reasons, seed ID, source-bar digest, ordered member
counts, exact public call counts `1/1`, and an overall deterministic artifact-set identity.

A matching seed ID without matching nested evidence and file hashes is insufficient.

## 18. Atomic Publication and Immutable Failure Handling

All machine-readable bytes are built in a new task-specific temporary directory inside the private
parent, validated there, and moved into the final V3 root only after every gate passes. The final
root must be absent before publication. No file is written incrementally into an accepted root.

On failure:

- the final V3 root remains absent;
- the temporary output is quarantined under a unique nonaccepted name or removed only under the
  exact rollback authority of the future execution task;
- the V2 pilot and any accepted V3 pilot remain immutable;
- no failed artifact is repaired, overwritten, or relabeled successful;
- no downstream operation begins.

Partial structural members are never promoted under a failed final status.

## 19. Repeatability and Prefix Contract

Two independent future runs with identical accepted V3 dataset bytes, committed dependencies,
configuration, and proposal bytes must produce object-equal results and byte-identical machine
artifacts. README and validation report must also be deterministic under the locked evidence set.

The V3 private run is not an append operation to the V2 dataset. V2-to-V3 version mutation requires a
full rebuild and new identities. Structural prefix comparison is eligible only after acceptance of a
separately rebuilt dataset formed by a strictly later complete canonical segment append; same-moment
append, partial segment, historical insertion, source repair, calendar mutation, version mutation,
or reordered evidence is ineligible and requires full revalidation.

Eligible later-segment reconstruction preserves prior foreign structural facts semantically while
dataset-bound digests and seed identities deterministically rebind as specified by the committed
structural contract.

## 20. Independent Validation Evidence

The future private checkpoint must record and independently verify:

- exact accepted V3 dataset identity and all input hashes;
- exact dependency and proposal hashes;
- current runtime tzdata version and `America/New_York` availability;
- exact public API signatures and call counts;
- result and validator object equality;
- status, reasons, blocking reasons, seed ID, source-bar digest, and ordered member counts;
- every public nested foreign identity and source/confirmation moment against the accepted dataset;
- no cross-segment member, no OOS member, no future-dependent member, and no synthetic evidence;
- canonical JSON round-trip without type or ordering loss;
- byte-identical repeat execution;
- exact output scope and Git-ignore evidence;
- unchanged source, tests, other private roots, index, HEAD, and origin/main;
- `PRIVATE_RUN_PERFORMED=true` only after successful publication;
- `CANDIDATE_RUN_PERFORMED=false`, `TRAINING_STARTED=false`,
  `OOS_OUTCOME_ACCESSED=false`, and `INTEGRATION_STARTED=false`.

The report must not claim profitability, model quality, strategy edge, generalization, production
readiness, or trading authority.

## 21. Inline Synthetic Exact 48-Case Future Matrix

The future V3 rebuild proposal and later structural private-run tooling/tests must preserve this
exact sequential logical matrix. Parameterization may expand collection without changing the 48
logical cases.

1. Missing accepted V3 pilot root stops before private execution.
2. Existing final structural V3 root stops without overwrite.
3. V2 manifest version is rejected as a V3 runtime dataset.
4. V2 dataset or segment ID carry-forward is rejected.
5. Builder source/test hash drift stops before reconstruction.
6. Structural source/test/checkpoint hash drift stops before reconstruction.
7. Proposal or accepted V3 pilot-manifest hash drift stops before reconstruction.
8. Malformed, missing, reordered, extra, or duplicate private input file stops.
9. Current public parser reconstructs every bounded export exactly once.
10. Coverage evidence and calendar entries preserve exact accepted tuple order.
11. Exact dataset config and runtime tzdata reconcile.
12. Public dataset builder is called exactly once.
13. Non-`VALID` dataset status blocks structural derivation.
14. Dataset manifest, counts, reasons, segments, and identities match accepted V3 evidence.
15. OOS bar count is zero and frozen OOS outcome remains unopened.
16. Structural builder exact keyword-only signature/default is locked.
17. Structural validator exact keyword-only signature/default is locked.
18. Structural builder is called exactly once with exact default config.
19. Structural validator is called exactly once with the same runtime objects.
20. Build/validation status, reasons, blocking reasons, and seed match exactly.
21. `VALID` requires a nonempty canonical seed and exact valid reason.
22. Dataset-bound `NONE` requires a non-null canonical empty seed and exact none reason.
23. `INVALID`, `AMBIGUOUS`, or `UNKNOWN` publishes no accepted output.
24. Exception containment leaves final root absent and upstream evidence unchanged.
25. Development-only segment selection excludes validation/OOS bars.
26. Cross-segment swing lookback or confirmation is rejected.
27. Cross-segment event or FVG formation is rejected.
28. Dealing Range swing identities and confirmation moments reconcile.
29. Equal Liquidity swings mirror Dealing Range swings one-to-one.
30. Structure Event identities, broken swings, provenance, and causal order reconcile.
31. FVG context-link formation moments and bound events reconcile.
32. Opaque displacement IDs are retained without invented foreign proof.
33. Source-bar and segment-evidence digests recompute exactly.
34. Seed identity recomputes from ordered exact nested evidence.
35. Nested tuple order is identity-sensitive and never silently sorted.
36. Determinably malformed later evidence promotes no failing or later group.
37. Immutable strictly prior complete evidence remains unchanged on later failure.
38. Input binding contains every required dependency and dataset field.
39. Structural JSON preserves exact fields, enums, timestamps, Decimals, tuples, and hashes.
40. Manifest binds every output byte length and SHA-256 exactly once.
41. Required/forbidden artifact names and exact five-file scope are exhaustive.
42. Temporary publication is atomic and cannot expose partial final output.
43. Repeat execution is object-equal and machine-byte-identical.
44. Host path, clock, locale, filesystem order, and hash iteration do not affect bytes.
45. V2 root and accepted V3 pilot root remain byte-immutable.
46. Git status, index, HEAD, and origin/main remain unchanged by private execution.
47. Candidate, feature/label, training, OOS, strategy, risk, and integration surfaces remain unused.
48. A passing private structural artifact authorizes only a separate candidate-run readiness audit,
    never automatic downstream execution or promotion.

## 22. Rollback and Quarantine

This documentation task rolls back by deleting only this uncommitted proposal. After commit,
rollback requires a bounded revert commit; history rewriting is forbidden.

A future V3 pilot rebuild rolls back only its newly reserved private rebuild root. A future
structural run rolls back only its new V3 structural root or quarantined temporary output. Neither
operation may delete, modify, or reuse the accepted V2 root, immutable acquisition artifacts,
calendar evidence, or any accepted V3 predecessor.

Private rollback never changes Git-tracked source and never creates a training or integration path.

## 23. Promotion and Immediate Stop Conditions

Structural private execution requires all of the following before a new explicit run authorization:

1. a separate V3 pilot rebuild proposal is independently accepted and committed;
2. the V3 pilot rebuild is explicitly authorized, executed, independently audited, and accepted;
3. a new immutable V3 dataset ID, manifest hash, counts, reasons, segment IDs, and dependency hashes
   are recorded;
4. this proposal is corrected to bind those exact accepted V3 values and independently re-audited;
5. the exact private V3 structural output scope remains absent;
6. source, test, proposal, checkpoint, API, timezone, and private-input bytes remain unchanged;
7. explicit private-run authority is granted for only that exact bound evidence.

Stop immediately on V2/V3 identity reuse, dependency drift, private input mutation, manifest
mismatch, runtime tzdata mismatch, non-`VALID` dataset, OOS contact, cross-segment state, silent sort,
identity mismatch, nondeterminism, exception leakage, partial publication, scope expansion, external
fixture, model or language-model access to private data, candidate/feature-label execution, training,
profitability, strategy, risk, execution, integration, stage, commit, or push without exact separate
authority.

There is no automatic promotion path. A successful engineering structural run would prove only
deterministic plumbing against one post-hoc, non-promotable pilot.

## 24. Final Decision and Next Single Task

The exact future structural private-run contract is now specified, but present readiness is
`BLOCKED_PENDING_V3_PILOT_REBUILD`. Executing against the stored V2 pilot would correctly return
`INVALID` under the current structural validator and would violate builder-version identity
separation if bypassed.

The next single task is documentation-only creation and independent audit of exactly:

`docs/gc_futures_phase_a_pilot_v3_split_session_rebuild_change_proposal.md`

That proposal must bind the immutable V2 source/coverage/calendar inputs, current V3 builder/API and
hashes, a new non-overwriting private V3 output root, exact reconstruction and comparison rules,
expected identity rebasing, validation matrix, rollback, quarantine, and STOP conditions. It must
not perform the rebuild, modify source/tests, access OOS outcomes, begin structural execution,
training, integration, stage, commit, or push without later exact authority.

This proposal itself authorizes only its documentation acceptance workflow. The global code freeze
remains active.
