# GC Futures Phase-A Cross-Segment Candidate Resolver Null-Manifest Default-Config Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-NULL-MANIFEST-DEFAULT-CONFIG-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Current pushed baseline: `95911ee89a81f96f129a57adf9e1f0637f75c009`.
- Pushed resolver implementation: `8432341201e9d96d07483052dc8892ecae1b551b`.
- Parent correction proposal commit: `95911ee89a81f96f129a57adf9e1f0637f75c009`.
- Parent proposal SHA-256: `A29E44658A4E5CD6A630248FCD21689A2F8694DA586E9C454D693DE590084ABC`.
- Classification: documentation-only, fail-closed private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This proposal binds a possible future diagnostic rerun after a harness-only
canonical-control shape correction. It grants no authority to open private
payloads, execute a private run, build features or labels, access final OOS,
train, integrate, predict, execute, or trade.

## 2. Consumed failed transaction

The private transaction authorized against the parent correction proposal
successfully applied the explicit fresh-worker repository bootstrap. The first
worker imported the exact project modules, passed the public and private byte
preflight, and deserialized the accepted development graph. It then stopped at
the ephemeral harness gate:

`accepted graph incomplete`

The gate incorrectly required `canonical_candidate_evidence.manifest` to be
non-null before calling continuity. The accepted immutable Candidate Evidence
control is intentionally an incomplete-prefix negative control with this exact
shape:

```text
status = UNKNOWN
reasons = ("a swept pool has a truncated confirmation horizon",)
blocking_reasons = ("a swept pool has a truncated confirmation horizon",)
candidates = ()
segment_result_count = 113
manifest = None
```

The second worker, structural revalidation, continuity analyzer, and resolver
were not started. The parent process honored the no-retry gate. The final root
remained absent; both worker roots and the ephemeral harness were removed; all
eight accepted input files retained their locked lengths and SHA-256 values;
`HEAD` and `origin/main` remained
`95911ee89a81f96f129a57adf9e1f0637f75c009`; and no training, OOS,
feature/label, integration, Git, or trading action occurred.

That private authorization is consumed and cannot be reused.

## 3. Public contract finding

The committed continuity validator `_validate_result_shape()` requires a
Candidate Evidence manifest only when the canonical control status is
`VALID`. It explicitly accepts a shape-valid `UNKNOWN` canonical control with
a null manifest after validating the ordered detector segment results. The
future harness must preserve this public status-dependent contract and must
not impose a stronger synthetic manifest requirement.

The public continuity signature supplies this audited default:

```python
candidate_config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig()
```

The exact default is:

```text
EqualLiquidityConfig(
    tolerance_ticks=2,
    minimum_members=2,
    minimum_separation_bars=3,
)
DealingRangeConfig(
    swing_confirmation_bars=2,
    break_buffer_ticks=1,
)
```

A public-only proof confirmed that the function signature default equals a
fresh `GCCandidateEvidenceConfig()` and that the accepted metadata has exact
`UNKNOWN / 113 / null-manifest` shape. The proof did not call an analyzer,
resolver, training, OOS, feature/label, integration, or trading function.

## 4. Exact harness-only correction

After exact input-byte verification and fresh deserialization, a future worker
must require:

- a non-null valid dataset manifest;
- a non-null accepted structural seed;
- exact Candidate Evidence status `UNKNOWN`;
- exact reason and blocker from Section 2;
- zero candidates;
- exactly 113 ordered segment results;
- exact null Candidate Evidence manifest; and
- dataset/seed/control outer bindings equal the accepted private bytes.

The worker must not dereference `canonical_candidate_evidence.manifest.config`,
construct a replacement Candidate Evidence manifest, infer configuration from
the 113 results, or mutate the accepted control.

The future continuity call must omit the `candidate_config` keyword entirely:

```python
analyze_gc_cross_segment_continuity(
    dataset_config=dataset_config,
    dataset=dataset,
    boundary_calendar_entries=boundary_calendar_entries,
    candidate_calendar_entries=candidate_calendar_entries,
    structural_seed=structural_seed,
    canonical_candidate_evidence=canonical_candidate_evidence,
)
```

Omission selects the exact committed public `GCCandidateEvidenceConfig()`
default. Passing `None`, a decoded config, an inferred config, positional
arguments, a wrapper, monkey patch, or any alternative is forbidden.

## 5. Documentation-only scope

This proposal task may create and commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_null_manifest_default_config_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, runtime, integration, strategy,
risk, execution, trace, or other documentation file may change. Three
pre-existing unrelated untracked documentation files remain outside scope.

## 6. Exact public bindings

A future transaction must bind implementation commit
`8432341201e9d96d07483052dc8892ecae1b551b` and exact bytes:

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
| post-structural-fix parent proposal | `F799EB434192E7857488816E43672E6EB6C59873D1DB0A703DB83FB397C5D687` |
| fresh-worker import correction proposal | `A29E44658A4E5CD6A630248FCD21689A2F8694DA586E9C454D693DE590084ABC` |

Any commit, path, hash, version, signature, default, or public contract drift
is a STOP condition. No dependency may be patched, wrapped, replaced, copied,
or bypassed.

## 7. Exact accepted private input

The only admissible input root remains:

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

The ordered artifact-set identity remains
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Missing, extra, renamed, reordered, length-drifted, hash-drifted, or
manifest-member-drifted evidence stops before payload deserialization. Embargo
and final-OOS payloads remain forbidden.

## 8. Exact output root and scope

The only final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored. The future transaction may create only two
new task-owned worker roots and one ephemeral harness under the private parent.

The final root may contain only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw rows, source exports, Candidate Evidence payloads, features, labels,
outcomes, models, prompts, caches, backtests, strategy, risk, or execution
artifacts may be written.

## 9. Exact corrected two-run transaction

After separate exact authorization, each of two fresh workers must execute once:

1. apply the pushed explicit repository bootstrap before project imports;
2. verify exact repository, proposal, implementation, dependency, signature,
   default-config, runtime timezone, and Git-ignore bindings;
3. verify exact private scope, member order, lengths, hashes, and artifact-set
   identity before payload deserialization;
4. deserialize new frozen accepted development objects without cross-worker
   sharing;
5. require the exact status-dependent canonical-control shape in Section 4;
6. validate the accepted V3 structural graph and all 133 segment identities;
7. reconstruct the independently proven boundary and candidate calendars;
8. call `analyze_gc_cross_segment_continuity()` exactly once while omitting
   `candidate_config` and require exact
   `UNKNOWN / CANONICAL_CONTROL_UNKNOWN` with a non-null canonical continuity
   manifest;
9. construct authentic pending-horizon and receiving-group wrappers only from
   the same immutable accepted evidence;
10. call `resolve_gc_cross_segment_candidates()` exactly once;
11. validate status/reason precedence, identities, order, counts, lineage,
    direction, three-closed-bar arithmetic, and non-promotion flags; and
12. serialize only the exact five-file diagnostic scope.

The two complete canonical object-graph digests and all serialized bytes must
be equal before atomic publication. Any exception, `INVALID`, null continuity
manifest, default drift, malformed wrapper, nondeterminism, unexpected file,
hash drift, or repository drift fails the transaction. No subset retry,
adaptive repair, alternative config, fallback import, evidence mutation, or
third worker is allowed.

## 10. Authentic pending-result boundary

Only this public Inducement contract is eligible:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

Aliases, inferred reasons, missing blockers, widened horizons, modified
direction, altered ownership, or non-adjacent resolution is invalid.

## 11. Atomicity and independent audit

Machine-readable outputs use UTF-8 without BOM, LF endings, one terminal
newline, sorted keys, compact separators, and `ensure_ascii=True`. Canonical
timestamp, date, Decimal, enum, tuple, and identity rules remain locked by the
parent proposals.

Only after object equality, byte equality, identity recomputation, exact
five-file scope, unchanged accepted inputs, and unchanged repository state may
one validated worker root be atomically moved to the absent final root. The
other worker root and ephemeral harness must be removed.

The independent audit must prove exact bindings, explicit bootstrap, exact
`UNKNOWN + null Candidate Evidence manifest` preservation, omission of the
`candidate_config` keyword, one continuity and one resolver call per worker,
all 133 V3 segment validations, authentic pending evidence, deterministic
outputs, exact atomic scope, unchanged inputs/source/tests/Git, task-only
cleanup, and zero OOS/training/feature-label/integration/trading access.

On failure, the final root remains absent and only task-owned residue may be
removed. Accepted inputs and pre-existing roots must never be modified,
deleted, renamed, replaced, or repaired.

## 12. Permanent non-promotion boundary

Every admissible result remains `NON_PROMOTABLE_DIAGNOSTIC`. It cannot reopen
Phase A, rescue the retired V1 control, enter a corpus, become a feature,
label, target, or model input, expose final OOS, or authorize training,
integration, prediction, execution, or trading.

This proposal alone authorizes no private execution, stage, commit, push, or
external export.

## 13. Later gates

Before any corrected private execution, this exact proposal must:

1. pass an exact one-file documentation audit;
2. be committed locally as the only staged path;
3. receive separate exact GitHub privacy/export authorization;
4. be pushed and independently verified at `origin/main`; and
5. receive separate exact private two-run authorization naming the pushed
   proposal commit, final proposal SHA-256, implementation commit, and locked
   transaction.

Earlier broad trust statements and both consumed failed-run authorizations do
not satisfy these gates.
