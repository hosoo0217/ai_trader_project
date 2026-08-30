# GC Phase-A Cross-Segment Candidate Resolver Dataset-Purpose-Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-DATASET-PURPOSE-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Exact pushed parent proposal: `08ec978c734ade93bd81b03e94391635de802e45`.
- Parent proposal SHA-256: `EA75E715804166FB95FCB4B4FA81BD22D1A84FCC2F49B1819A21FA8EF165760E`.
- Exact pushed resolver implementation: `2711e87bc19662408e66cf890b9ba2a1fdfe863a`.
- Classification: documentation-only, harness-only, fail-closed private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This proposal corrects one extra harness metadata assertion discovered before
any analyzer call. It changes no accepted evidence, source, test, detector,
identity, dataset, calendar, feature, label, model, runtime integration,
strategy, risk, order, execution, or trading contract.

## 2. Consumed transaction outcome

The transaction authorized under the pushed parent proposal stopped in fresh
worker 1 with:

```text
DATASET_PURPOSE_DRIFT
```

The failure occurred after exact public and private byte preflight and during
accepted outer-metadata validation, before any direct call to:

1. `build_gc_candidate_evidence()`;
2. `analyze_gc_candidate_frontier_evidence()`;
3. `analyze_gc_cross_segment_continuity()`; or
4. `resolve_gc_cross_segment_candidates()`.

Worker 2 did not run. No final or worker output root was created. The task-owned
ephemeral harness was removed. All eight accepted input members retained their
exact lengths and SHA-256 values, the final root remained absent, and local
`HEAD`, `origin/main`, index, and tracked worktree remained unchanged.

That authorization and transaction are consumed. They may not be retried or
reused.

## 3. Read-only diagnosis

The accepted bundle is not corrupt. Exact SHA-bound top-level metadata in each
of these five JSON artifacts carries the same purpose value:

| Artifact | Exact `purpose` |
|---|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION` |
| `structural_seed_DEVELOPMENT_ONLY.json` | `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION` |
| `candidate_evidence_DEVELOPMENT_ONLY.json` | `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION` |
| `input_binding_DEVELOPMENT_ONLY.json` | `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION` |

The failed harness instead required the dataset outer object to equal the
literal string `DEVELOPMENT_ONLY`. That string is a filename classification
suffix, not the accepted bundle's purpose value. The assertion was not required
by the parent proposal and contradicted the exact accepted bytes already bound
by that proposal.

The accepted artifact manifest remains `COMPLETED_NON_PROMOTABLE`. Its training,
feature/label, integration, promotion, and trading authorities remain false.
The accepted input binding continues to record no training, feature/label run,
final-OOS access, or integration start.

## 4. Exact harness-only correction

A future fresh worker must retain every parent-proposal preflight and replace
only the erroneous purpose assertion with all of these exact checks:

1. deserialize only the five exact SHA-bound outer metadata objects listed in
   Section 3 after complete eight-file scope, length, and hash verification;
2. require each top-level `purpose` field to be a nonempty string;
3. require all five values to be exactly equal;
4. require the common value to be exactly
   `NON_PROMOTABLE_DEVELOPMENT_CANDIDATE_COVERAGE_EXPANSION`;
5. require the artifact manifest's `status` and `run_status` to remain exactly
   `COMPLETED_NON_PROMOTABLE`;
6. require every recorded training, feature/label, final-OOS, integration,
   promotion, and trading authority flag to remain false; and
7. continue typed immutable deserialization only after all checks pass.

The harness must not infer purpose from filenames, shorten it to
`DEVELOPMENT_ONLY`, normalize it, use substring or case-insensitive matching,
accept an alias, mutate an outer object, or rewrite any accepted byte.

This correction is ephemeral harness logic only. It reserves no source or test
path and does not alter any public API or identity.

## 5. Exact documentation-only scope

This proposal task may create and commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_dataset_purpose_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, runtime, integration,
strategy, risk, execution, trace, or other documentation file may change.

## 6. Inherited public implementation binding

Every public binding from the pushed parent proposal remains mandatory. A
future transaction must require exact pushed commit
`2711e87bc19662408e66cf890b9ba2a1fdfe863a` and these exact bytes:

| Path | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `D0BBB35F6D6A32CD012996867E56EDCDDC031B75790A19A11684E66290BFE68D` |
| `analysis/gc_candidate_evidence_builder.py` | `955D5B88953987D969530DFF16C39D8AF769EA7FECEE866E9BC684675B05482A` |
| `analysis/gc_cross_segment_continuity.py` | `E60DF0D3E16556A81B5CE9AE2F0FE739D3F02E9BC24D4788B76978C67F39571C` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `DA5193AFEE2B501D28FEE2303EBCF7C345A1D853063472D5C336B4F4506BF72F` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_structural_seed_evidence.py` | `49C0C9E86D04C072F4B3EBF420FC9B23BF58B3BDCD958E8F80F0DD74058ADD94` |
| `tests/test_gc_candidate_evidence_builder.py` | `C60D2F4A0C7220EF0488BB3776C65F933674E74ED96960E576891B17C2BAFDDC` |
| `tests/test_gc_cross_segment_continuity.py` | `8E03055B90FD35323F442A091E425D848561F8DAB5CF8390985BE37053D7B3A0` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `D34B4D480AA34FEFB4AC65F4D1272706C40555F3EC967804A9A860AF801720E9` |
| `tests/test_inducement.py` | `791567124B3ABA381A4FB84CBB4B37125E9404AF1AFE276717A3042B268EF8FE` |

Runtime `tzdata` must remain exactly `2026.2`. Any commit, source, test, hash,
signature, version, runtime, or public contract drift is a STOP condition. No
dependency may be patched, monkey patched, wrapped, substituted, copied, or
bypassed.

## 7. Inherited accepted private input binding

The only admissible future input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Before payload deserialization it must contain exactly:

| Member | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | 2337 | `D0774ACB1ECBB1D99F6BCFA4532447859886925D4FB8332BAC67B522BF862B1D` |
| `candidate_evidence_DEVELOPMENT_ONLY.json` | 74660911 | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | 2802555 | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| `input_binding_DEVELOPMENT_ONLY.json` | 5179 | `E7982293EDB42CC784B85C5047D06FEC86BCDBB5992C5E847171DD78252A43E4` |
| `normalized_calendar_DEVELOPMENT_ONLY.json` | 4149 | `CCB8BC4034BBC02922278F560BF1AFAC8282A05D3B26611A7EECF6202686F5FC` |
| `README_DEVELOPMENT_ONLY.md` | 344 | `7260B5DE117EB845758CC908DF5B40AC553AC9F6BBF7535F57A5B6D4733AD559` |
| `structural_seed_DEVELOPMENT_ONLY.json` | 3080278 | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |
| `validation_report_DEVELOPMENT_ONLY.md` | 858 | `28AE9108A9A6801FF9634E1FDF95121CADC1AEBA32F9CE225ACC12D15FA15ECB` |

The ordered artifact-set identity remains
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Missing, extra, renamed, reordered, length-drifted, hash-drifted, purpose-drifted,
or manifest-member-drifted evidence stops before typed payload deserialization.
Accepted input is immutable and final-OOS remains outside scope.

This documentation task does not reopen, hash, deserialize, or modify the
private root.

## 8. Exact future corrected two-run transaction

Only after this exact proposal is separately pushed and receives a new exact
private-run authorization may two independent fresh workers execute. Each
worker must:

1. verify exact proposal commit and SHA-256, parent proposal, implementation,
   public dependency, runtime, Git-ignore, input, and absent-root bindings;
2. apply the Section 4 five-object purpose consistency gate;
3. deserialize fresh immutable accepted development objects with no object
   sharing between workers;
4. reconstruct the boundary and candidate calendars independently from the
   accepted normalized-calendar bytes;
5. directly rebuild Candidate Evidence exactly once and require exact equality
   with the accepted `UNKNOWN / 113 / null-manifest` control;
6. directly call `analyze_gc_candidate_frontier_evidence()` exactly once and
   require the authentic `VALID` frontier from source ordinal `113` to receiver
   ordinal `114`;
7. directly call `analyze_gc_cross_segment_continuity()` exactly once and
   require exact `UNKNOWN / CANONICAL_CONTROL_UNKNOWN`, non-null manifest,
   unchanged legacy prefix, and exactly one appended frontier boundary;
8. build pending and receiving wrappers only from that frontier, appended
   boundary, immediately adjacent receiving groups, and exact event/reference
   object IDs and digests;
9. directly call `resolve_gc_cross_segment_candidates()` exactly once;
10. validate exact public status, reason, blocker, identity, precedence,
    ordering, lineage, direction, lifecycle, history, and arithmetic contracts;
11. serialize only the exact five non-promotable diagnostic files inherited
    from the parent proposal; and
12. compare complete fresh-worker object-graph digests and all five byte streams
    before atomic publication.

Resolver `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is observationally
admissible only after all exact gates pass. `INVALID`, an exception,
nondeterminism, metadata drift, identity drift, unexpected file, or output-scope
drift fails the transaction. No subset retry, altered assertion, fallback,
second configuration, third worker, or evidence repair is allowed.

## 9. Output, cleanup, and independent audit

The only future final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored. Two task-owned worker roots and one ephemeral
harness may exist only during the authorized transaction. Publication may occur
only by atomically moving one byte-verified worker directory to the still-absent
final root after complete equality.

On failure, remove only verified task-owned worker roots and the ephemeral
harness. Never delete, overwrite, rename, normalize, or repair accepted input or
a pre-existing final root.

The independent audit must prove exact purpose consistency, proposal and byte
bindings, one direct call per public stage per worker, event/reference identity,
fresh-worker object and byte equality, exact five-file output or absent final
root, unchanged accepted input, unchanged source/tests/Git state, complete
task-owned cleanup, and zero final-OOS, training, dataset/corpus, feature/label,
integration, prediction, strategy, risk, order, execution, or trading access.

The audit then stops. No result status grants promotion or another run.

## 10. Global freeze and non-authority

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. Every future output remains permanently
`NON_PROMOTABLE_DIAGNOSTIC`.

This proposal cannot reopen Phase A, rescue a negative control, enter a dataset
or corpus, become a feature, label, target, split, or model input, expose final
OOS, call a local or remote language model with private evidence, train or
integrate a model, produce a trading signal, size risk, submit an order, or
execute a trade.

## 11. Later authorization gates

Before any private execution, this exact proposal must:

1. pass an exact one-file documentation audit;
2. be committed locally as the sole staged path;
3. receive separate informed GitHub privacy/export authorization;
4. be pushed and independently verified at remote `main`; and
5. receive a new exact private two-run authorization naming the pushed proposal
   commit, proposal SHA-256, and exact implementation commit.

General continuation language, the consumed transaction, its removed harness,
an earlier private-run authorization, or trust in the operator grants none of
these later permissions.
