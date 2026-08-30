# GC Phase-A Cross-Segment Candidate Resolver Calendar-Evidence-Name-Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-CALENDAR-EVIDENCE-NAME-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-31`.
- Exact pushed parent proposal: `908eb8219338ffa1a4329e0f356ee26db6e41905`.
- Parent proposal SHA-256: `D304012A6FD2C58584F51352C6B9D8760C8227B7750532877ED1B939A8DC0497`.
- Exact pushed resolver implementation: `2711e87bc19662408e66cf890b9ba2a1fdfe863a`.
- Classification: documentation-only, harness-only, fail-closed private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This proposal corrects one exact calendar-evidence member-name assertion in a
future ephemeral harness. It changes no accepted byte, evidence hash, source,
test, fixture, detector, identity, dataset, calendar semantics, candidate,
feature, label, model, runtime integration, strategy, risk, order, execution,
or trading contract.

## 2. Consumed transaction outcome

The exact transaction authorized against the pushed parent proposal stopped in
fresh worker 1 with:

```text
CALENDAR_EVIDENCE_DRIFT
```

The controller and worker had already passed exact repository, proposal,
implementation, public-dependency, runtime, Git-ignore, absent-root,
eight-member input length/hash, artifact-set, five-object purpose-consistency,
manifest-status, and authority-false gates. Fresh immutable accepted dataset,
structural-seed, and canonical-control objects were deserialized. The failure
then occurred while independently reconstructing the boundary calendar, before
any direct call to:

1. `build_gc_candidate_evidence()`;
2. `analyze_gc_candidate_frontier_evidence()`;
3. `analyze_gc_cross_segment_continuity()`; or
4. `resolve_gc_cross_segment_candidates()`.

Worker 2 did not run. No final or worker output root remained. The task-owned
ephemeral harness was removed. Independent audit proved all eight accepted
input lengths and SHA-256 values unchanged, local `HEAD` and `origin/main`
unchanged, index and tracked worktree clean, and the final root absent.

That authorization and transaction are consumed. They may not be retried or
reused.

## 3. Read-only failure diagnosis

The accepted normalized-calendar artifact is not corrupt. Its three ordered
`calendar_evidence` records are exactly:

| Ordinal | Exact serialized `name` | Exact SHA-256 |
|---:|---|---|
| 0 | `Trading-Hours-Holiday (2).xlsx` | `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11` |
| 1 | `Trading-Hours-Holiday (3).xlsx` | `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7` |
| 2 | `CME_GCC_case_04687271_final_clarification_20260807.eml` | `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2` |

The consumed harness correctly bound the third SHA-256 but incorrectly used
the human-facing description `final CME GCC clarification EML` as the exact
serialized `name`. That phrase is a display label in an earlier proposal
table, not the immutable member name stored in the accepted normalized-calendar
bytes.

The failure therefore proves a harness assertion defect only. It does not
authorize renaming the EML, rewriting the normalized calendar, changing a
hash, accepting an alias, or repairing accepted evidence.

## 4. Exact harness-only correction

A future fresh worker must retain every parent-proposal gate and replace only
the erroneous calendar-evidence-name assertion with all of these exact checks:

1. deserialize `calendar_evidence` only after the complete accepted eight-file
   scope, length, and SHA-256 preflight passes;
2. require `calendar_evidence` to be an exact three-member ordered list;
3. require every member to be an exact object with only `name` and `sha256`;
4. require ordinals 0 and 1 to equal the workbook names and hashes in Section
   3;
5. require ordinal 2 `name` to equal exactly
   `CME_GCC_case_04687271_final_clarification_20260807.eml`;
6. require ordinal 2 `sha256` to remain exactly
   `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`;
7. use the three exact accepted SHA-256 values, lowercased and in the same
   order, as both boundary-calendar `source_artifact_ids` and
   `source_artifact_sha256s`; and
8. retain the human description only as prose; never use it as a machine
   identity or accepted-byte assertion.

The harness must not trim, case-fold, basename-normalize, alias, substring
match, relabel, rename, copy, mutate, or rewrite any evidence member. This
correction is ephemeral harness logic only. It reserves no public source or
test path and changes no public API or identity.

## 5. Exact documentation-only scope

This proposal task may create and later commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_calendar_evidence_name_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, runtime,
integration, strategy, risk, execution, trace, or other documentation file may
change.

## 6. Inherited public implementation binding

Every public binding from the pushed parent proposal remains mandatory. A
future transaction must require exact pushed implementation
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
signature, version, runtime, or public-contract drift is a STOP condition. No
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
Missing, extra, renamed, reordered, length-drifted, hash-drifted,
purpose-drifted, calendar-evidence-drifted, or manifest-member-drifted evidence
must stop before analyzer invocation. Accepted input remains immutable and
final OOS remains outside scope.

This documentation task does not reopen, hash, deserialize, or modify the
private root.

## 8. Exact future corrected two-run transaction

Only after this exact proposal is separately committed, pushed, and receives a
new exact private-run authorization may two independent fresh workers execute.
Each worker must:

1. verify exact proposal commit and SHA-256, parent proposal, implementation,
   public dependency, runtime, Git-ignore, input, and absent-root bindings;
2. apply the parent proposal's five-object purpose-consistency and all-false
   authority gates;
3. apply only the exact calendar-evidence correction in Section 4;
4. deserialize fresh immutable accepted development objects with no object
   sharing between workers;
5. independently reconstruct boundary and candidate calendars from the same
   accepted normalized-calendar bytes using prior-day `18:00` inclusive to
   trade-date `17:00` exclusive `America/New_York` semantics;
6. directly rebuild Candidate Evidence exactly once and require exact equality
   with the accepted `UNKNOWN / 113 / null-manifest` control;
7. directly call `analyze_gc_candidate_frontier_evidence()` exactly once and
   require the authentic `VALID` frontier from source ordinal `113` to receiver
   ordinal `114`;
8. directly call `analyze_gc_cross_segment_continuity()` exactly once and
   require exact `UNKNOWN / CANONICAL_CONTROL_UNKNOWN`, a non-null manifest,
   unchanged legacy prefix, and exactly one appended eligible frontier
   boundary;
9. build pending and receiving wrappers only from that frontier, appended
   boundary, immediately adjacent receiving groups, and exact event/reference
   IDs and object digests;
10. directly call `resolve_gc_cross_segment_candidates()` exactly once;
11. validate exact status, reason, blocker, identity, precedence, ordering,
    lineage, direction, lifecycle, history, and three-bar arithmetic contracts;
12. serialize only the inherited exact five non-promotable diagnostic files;
    and
13. compare complete fresh-worker object-graph digests and all five byte
    streams before atomic publication.

Resolver `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is observationally
admissible only after all exact gates pass. `INVALID`, exception,
nondeterminism, metadata drift, identity drift, unexpected file, or
output-scope drift fails the transaction. No subset retry, altered assertion,
fallback, alternate label, second configuration, third worker, or evidence
repair is allowed.

## 9. Output, cleanup, and independent audit

The only future final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored. Two task-owned worker roots and one
ephemeral harness may exist only during the authorized transaction. Publication
may occur only by atomically moving one byte-verified worker directory to the
still-absent final root after complete equality.

On failure, remove only verified task-owned worker roots and the ephemeral
harness. Never delete, overwrite, rename, normalize, or repair accepted input
or a pre-existing final root.

The independent audit must prove exact calendar-evidence member identity,
purpose consistency, proposal and byte bindings, one direct call per public
stage per worker, event/reference identity, fresh-worker object and byte
equality, exact five-file output or absent final root, unchanged accepted
input, unchanged source/tests/Git state, complete task-owned cleanup, and zero
final-OOS, training, dataset/corpus, feature/label, integration, prediction,
strategy, risk, order, execution, or trading access.

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

## 11. Acceptance and later authorization gates

Before any private execution, this exact proposal must:

1. pass an exact one-file documentation audit, `git diff --check`, public hash
   recomputation, focused regression, and complete public regression;
2. receive a separate exact one-path stage/local-commit authorization;
3. be committed locally as the sole staged path;
4. receive separate informed GitHub privacy/export authorization;
5. be pushed and independently verified at remote `main`; and
6. receive a new exact private two-run authorization naming the pushed
   proposal commit, proposal SHA-256, and exact implementation commit.

General continuation language, the consumed transaction, its removed harness,
an earlier private-run authorization, or trust in the operator grants none of
these later permissions.
