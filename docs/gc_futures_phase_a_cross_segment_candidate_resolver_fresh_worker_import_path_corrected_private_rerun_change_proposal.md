# GC Futures Phase-A Cross-Segment Candidate Resolver Fresh-Worker Import-Path Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-FRESH-WORKER-IMPORT-PATH-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Current repository baseline: `0fa83438ed9639252349391176a98cc9d1d69802`.
- Pushed resolver implementation: `8432341201e9d96d07483052dc8892ecae1b551b`.
- Parent private-rerun proposal: `0fa83438ed9639252349391176a98cc9d1d69802`.
- Parent proposal SHA-256: `F799EB434192E7857488816E43672E6EB6C59873D1DB0A703DB83FB397C5D687`.
- Classification: documentation-only, fail-closed rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This document binds a possible future corrected private diagnostic transaction.
Creating or committing it grants no authority to open private payloads, rerun
the diagnostic, build features or labels, access final OOS, train, integrate,
predict, execute, or trade.

## 2. Observed failed transaction

The transaction authorized against the parent proposal stopped in the first
fresh worker before any private payload deserialization. The ephemeral harness
was launched from `private_data/sierra_chart/`, so Python selected that script
directory as `sys.path[0]`. The worker had not explicitly inserted the
repository root before importing project modules and failed with:

`ModuleNotFoundError: No module named 'analysis'`

The parent process honored the parent proposal's exception and no-retry gates.
It did not start a second diagnostic attempt or adaptively alter the failed
worker.

The post-failure audit established:

- the final diagnostic root remained absent;
- both task-owned worker roots and the ephemeral harness were removed;
- the accepted eight-file input scope retained every locked byte length and
  SHA-256 value;
- private dataset, structural-seed, Candidate Evidence, and calendar payloads
  were not deserialized;
- local `HEAD` and `origin/main` remained
  `0fa83438ed9639252349391176a98cc9d1d69802`;
- the Git index and tracked worktree remained unchanged; and
- no training, OOS access, feature/label build, integration, commit, push, or
  trading action occurred.

The failed authorization is consumed and cannot be reused.

## 3. Root cause and exact correction

The defect is confined to ephemeral fresh-worker bootstrap. It is not a data,
calendar, structural, Candidate Evidence, continuity, resolver, or public
source defect.

A future harness must calculate its repository root from its own immutable
location and prepend that exact absolute directory before the first project
module import:

```python
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
```

The authorized ephemeral harness location remains directly under
`private_data/sierra_chart/`, making `parents[2]` the repository root. The
worker must then import the exact bound project modules and verify their public
versions and file hashes before private deserialization.

The harness must not depend on ambient `PYTHONPATH`, the caller's current
directory, package installation, editable installation, site customization,
network access, module aliasing, monkey patching, or a copied project package.
It must reject a computed root that does not contain the exact proposal and
dependency paths bound below.

## 4. Public-only correction proof

Before this proposal was created, a fresh Python process performed an
import-only proof with the exact repository root explicitly prepended. It
imported:

- `analysis.gc_cross_segment_continuity`; and
- `analysis.gc_cross_segment_candidate_resolver`.

The process returned exactly:

```text
FRESH_IMPORT_PASS GC-CROSS-SEGMENT-CONTINUITY-V1 GC-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1
```

The proof opened no private payload, called no analyzer or resolver, wrote no
artifact, and changed no tracked or staged file. It proves only the bootstrap
mechanism, not a future private outcome.

## 5. Exact documentation-only scope

This proposal task may create and commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_fresh_worker_import_path_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, runtime,
integration, strategy, risk, execution, trace, or other documentation file may
change. Three unrelated pre-existing untracked documentation files remain out
of scope and must stay untouched.

## 6. Exact public implementation bindings

A future transaction must bind the pushed implementation commit
`8432341201e9d96d07483052dc8892ecae1b551b` and these exact bytes:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `D0BBB35F6D6A32CD012996867E56EDCDDC031B75790A19A11684E66290BFE68D` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_structural_seed_evidence.py` | `49C0C9E86D04C072F4B3EBF420FC9B23BF58B3BDCD958E8F80F0DD74058ADD94` |
| `tests/test_gc_candidate_evidence_builder.py` | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `tests/test_gc_cross_segment_continuity.py` | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |
| structural compatibility proposal | `15E902AED5B73244F5F9D801716F0CFF91FF24C53DB742795C54C81CA2A11C79` |
| structural compatibility checkpoint | `676926902722B820A9825A9DA989729A03A45DC240407F1B2FDC0B273CAB5B3B` |
| parent private-rerun proposal | `F799EB434192E7857488816E43672E6EB6C59873D1DB0A703DB83FB397C5D687` |

Any commit, path, dependency, version, signature, or hash drift is a STOP
condition requiring a new proposal. The future harness must not patch, wrap,
replace, or bypass a bound dependency.

## 7. Exact accepted private input binding

The only admissible private input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Before payload deserialization it must contain exactly:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | `2337` | `D0774ACB1ECBB1D99F6BCFA4532447859886925D4FB8332BAC67B522BF862B1D` |
| `candidate_evidence_DEVELOPMENT_ONLY.json` | `74660911` | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | `2802555` | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| `input_binding_DEVELOPMENT_ONLY.json` | `5179` | `E7982293EDB42CC784B85C5047D06FEC86BCDBB5992C5E847171DD78252A43E4` |
| `normalized_calendar_DEVELOPMENT_ONLY.json` | `4149` | `CCB8BC4034BBC02922278F560BF1AFAC8282A05D3B26611A7EECF6202686F5FC` |
| `README_DEVELOPMENT_ONLY.md` | `344` | `7260B5DE117EB845758CC908DF5B40AC553AC9F6BBF7535F57A5B6D4733AD559` |
| `structural_seed_DEVELOPMENT_ONLY.json` | `3080278` | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |
| `validation_report_DEVELOPMENT_ONLY.md` | `858` | `28AE9108A9A6801FF9634E1FDF95121CADC1AEBA32F9CE225ACC12D15FA15ECB` |

The exact artifact-set identity remains
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Scope, order, length, hash, or identity drift stops before payload
deserialization. Embargo and final-OOS payloads remain outside scope.

## 8. Exact output and temporary roots

The only final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored at preflight. A future transaction may create
only two new task-owned worker roots directly under the same private parent and
one ephemeral harness. Pre-existing roots may not be opened, deleted, repaired,
or replaced.

The final root may contain only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw row, source export, candidate payload, feature, label, outcome, model,
backtest, prompt, cache, strategy, risk, or execution artifact is allowed.

## 9. Corrected fresh-worker preflight order

Each of two independent fresh workers must execute this order exactly once:

1. derive the repository root from the ephemeral harness path and prepend it
   to `sys.path` exactly as Section 3 specifies;
2. import the bound public modules and verify exact paths, versions, signatures,
   implementation ancestry, proposal bytes, and dependency hashes;
3. verify runtime `tzdata 2026.2`, `America/New_York`, and `Asia/Tokyo`;
4. verify the absent, Git-ignored final root;
5. verify exact private root scope, member order, byte lengths, SHA-256 values,
   and artifact-set identity before payload deserialization;
6. deserialize new frozen accepted development objects with no object sharing;
7. require exact manifest version
   `GC-DATASET-BUILDER-V3-SPLIT-SESSION` and all 133 archived segment
   identities through only the bound V3 validation branches;
8. reconstruct the two independently proven calendar tuples;
9. call `analyze_gc_cross_segment_continuity()` exactly once and require exact
   `UNKNOWN / CANONICAL_CONTROL_UNKNOWN` with a canonical non-null manifest;
10. construct only authentic public pending-horizon and receiving-group
    wrappers from the same immutable accepted evidence;
11. call `resolve_gc_cross_segment_candidates()` exactly once;
12. validate status/reason precedence, identities, order, lineage,
    three-closed-bar arithmetic, counts, and permanent non-promotion flags; and
13. serialize only the exact five-file diagnostic scope.

Workers must compare complete canonical object-graph digests and every output
byte before atomic publication. An exception, import mismatch, `INVALID`
result, null continuity manifest, malformed wrapper, nondeterminism, hash drift,
unexpected file, or repository drift fails the whole transaction.

There is no subset retry, adaptive repair, fallback import, alternate path,
evidence mutation, or third worker. A failed corrected authorization is
consumed and requires another proposal.

## 10. Authentic Inducement contract

Only the public producer result below is eligible:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

Token-only synthetic reasons, aliases, inference, widened horizons, missing
blockers, altered direction, moved ownership, or more-than-adjacent resolution
is invalid.

## 11. Determinism and atomic publication

Machine-readable artifacts use UTF-8 without BOM, LF endings, one terminal
newline, sorted keys, compact separators, and `ensure_ascii=True`. Canonical
timestamp, date, Decimal, enum, tuple, and hash rules remain those in the parent
proposal.

Only after object equality, byte equality, identity recomputation, exact scope,
unchanged accepted inputs, unchanged `HEAD`/index/tracked worktree, and all STOP
gates pass may one validated worker directory be atomically moved to the absent
final root. The other worker root and ephemeral harness must then be removed.

On failure, remove only transaction-owned worker roots and the ephemeral
harness. The final root must remain absent. Accepted evidence and any
pre-existing root must never be deleted, overwritten, renamed, or repaired.

## 12. Independent audit matrix

A future authorized post-run audit must prove:

1. exact proposal, implementation, dependency, runtime, input, root, and
   Git-ignore bindings;
2. the corrected explicit repository bootstrap occurred before project import;
3. both fresh workers imported modules from the exact repository paths;
4. rejection before payload deserialization for bootstrap or preflight drift;
5. exact V3 selection and all 133 archived segment reconciliations;
6. canonical Candidate Evidence byte-semantic preservation;
7. one continuity and one resolver call per worker;
8. exact eligible continuity branch with non-null canonical manifest;
9. authentic pending producer reason and blocker enforcement;
10. boundary, group, horizon, lineage, direction, count, order, and identity
    reconciliation;
11. complete two-run object and byte equality;
12. exact five-file atomic publication only after every gate passes;
13. failure cleanup limited to task-owned residue;
14. accepted input, source, tests, `HEAD`, index, and tracked worktree remain
    unchanged; and
15. no private row enters logs, tracked output, prompts, or a language model.

## 13. Permanent authority boundary

Every admissible future result remains `NON_PROMOTABLE_DIAGNOSTIC`. It cannot
reopen Phase A, rescue the retired V1 control, enter a corpus, become a feature,
label, target, model input, expose final OOS, or authorize training,
integration, prediction, execution, or trading.

This proposal does not authorize a private run, stage, commit, push, or any
external export by itself.

## 14. Later execution gates

Before any corrected private execution, this exact proposal must:

1. pass an exact one-file documentation audit;
2. be committed locally as the only staged path;
3. receive separate exact GitHub privacy/export authorization;
4. be pushed and independently verified at `origin/main`; and
5. receive separate exact private two-run authorization naming the pushed
   proposal commit, final proposal SHA-256, implementation commit, and locked
   transaction.

Earlier broad trust statements, the consumed failed-run authorization, or the
public import proof do not satisfy these gates.
