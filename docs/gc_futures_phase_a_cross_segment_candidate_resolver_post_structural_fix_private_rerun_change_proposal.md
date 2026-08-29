# GC Futures Phase-A Cross-Segment Candidate Resolver Post-Structural-Fix Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-POST-STRUCTURAL-FIX-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Pushed implementation commit: `8432341201e9d96d07483052dc8892ecae1b551b`.
- Parent proposal commit: `f4ddb25f0f15bbf19cfd5466ecec39c7a0c175fc`.
- GitHub parity at proposal start: local `HEAD`, `origin/main`, and remote
  `refs/heads/main` all equal the pushed implementation commit.
- Classification: documentation-only, fail-closed private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This document binds a possible future corrected diagnostic transaction after
the structural-seed V3/V5 compatibility correction. Creating or committing this
proposal does not authorize opening private payloads, executing the transaction,
building datasets or corpora, training, final-OOS access, feature or label work,
integration, prediction, execution, or trading.

## 2. Why a new proposal is required

The prior corrected private-rerun transaction stopped before the resolver. Its
canonical Candidate Evidence rebuild called structural-seed revalidation, which
accepted only the current V5 manifest version and rejected the exact accepted
V3 archived manifest as `INVALID_STRUCTURAL_EVIDENCE`. The rebuilt candidate was
therefore `INVALID` with zero segment results instead of the accepted `UNKNOWN`
control with 113 segment results. Continuity then failed closed through
`CANONICAL_CONTROL_DRIFT`.

Commit `8432341201e9d96d07483052dc8892ecae1b551b` corrects only that consumer
compatibility barrier. It selects exact historical V3 or current V5 segment
identity verification from the manifest version, rejects every other version,
and preserves all outer structural validation. Public evidence passed:

- test-first expected failure before correction;
- the new V3/V5 matrix `7/7`;
- structural, Candidate Evidence, and continuity regression `188/188`; and
- complete public suite `2666/2666`.

The correction does not establish the future continuity or resolver outcome.
The transaction must observe the next result and fail closed on any unbound
status, reason, identity, exception, or nondeterminism.

## 3. Exact documentation-only scope

This proposal task may create and commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_post_structural_fix_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, runtime, integration,
strategy, risk, execution, trace, or other documentation file may change.

## 4. Global freeze and authority boundary

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. This proposal grants no authority to:

- read or deserialize the private root before separate exact execution approval;
- mutate, relabel, normalize, replace, or delete accepted evidence;
- access the embargo interval or sealed final-OOS payload;
- create or promote canonical Candidate Evidence;
- build a dataset, corpus, feature, label, target, split, model, or outcome;
- call a local or remote language model with private market evidence;
- add exports, runtime hooks, package wiring, or integration;
- produce BUY/SELL, confidence, risk, entry, exit, PnL, order, or execution
  authority; or
- push this proposal without a separate exact privacy/export authorization.

Passing this proposal audit, public tests, or a later diagnostic result cannot
lift these restrictions.

## 5. Exact public implementation bindings

A future transaction must start from exact pushed commit
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

Any commit, hash, source, test, version, or public contract drift is a STOP
condition requiring a fresh proposal. A future harness must not patch, monkey
patch, wrap, substitute, or bypass these dependencies.

## 6. Exact accepted private input binding

The only admissible future private input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Before deserialization it must contain exactly these eight files in canonical
name order, with exact byte lengths and SHA-256 values:

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

The artifact-set identity remains
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Missing, extra, renamed, reordered, length-drifted, hash-drifted, or
manifest-member-drifted evidence stops before deserialization. The embargo and
sealed final-OOS payloads remain outside authorized scope.

This documentation task does not open, enumerate, hash, deserialize, or modify
the private root.

## 7. Exact output root and preflight

The only future final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored at future execution preflight. If it exists,
the transaction stops without opening, deleting, replacing, or repairing it.

The final root may contain only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw rows, source export, candidate payload, feature, label, outcome, model,
backtest, prompt, cache, strategy, risk, or execution artifact is allowed.

## 8. Exact post-structural-fix two-run transaction

Only after separate exact private-run authorization may two independent fresh
workers execute. Each worker must perform this fixed order exactly once:

1. verify exact commit, proposal hash, dependency hashes, Git-ignore state,
   runtime timezone, and timezone-data version;
2. verify the exact private root, eight-file scope, lengths, hashes, canonical
   member order, and artifact-set identity before deserialization;
3. deserialize fresh immutable development dataset, structural seed, canonical
   Candidate Evidence control, normalized calendar, and binding metadata with
   no object sharing between workers;
4. validate exact manifest version `GC-DATASET-BUILDER-V3-SPLIT-SESSION` and
   require all 133 archived segment identities to reconcile through only the
   local V3 structural and continuity verifier branches;
5. reconstruct the independently proven boundary and candidate calendar tuples;
6. call `analyze_gc_cross_segment_continuity()` exactly once;
7. require exact `UNKNOWN` / `CANONICAL_CONTROL_UNKNOWN`, a non-null canonical
   continuity manifest, and exact accepted-control preservation;
8. construct pending-horizon and receiving-group wrappers only from the same
   immutable evidence and authentic public Inducement contract;
9. call `resolve_gc_cross_segment_candidates()` exactly once;
10. validate exact public status/reason precedence, identities, order, counts,
    lineage, direction, three-closed-bar arithmetic, and non-promotion flags;
11. serialize only the exact five-file diagnostic scope; and
12. compare complete worker object graphs and bytes before publication.

An `INVALID` continuity result, null manifest, canonical-control drift,
ineligible status or reason, exception, nondeterminism, hash drift, malformed
wrapper, unexpected file, or output-scope drift fails the complete transaction.
No subset retry, evidence repair, fallback version, or adaptive rerun is allowed.

## 9. Authentic pending-result contract

Only this exact public Inducement incomplete-horizon contract is eligible:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

Token-only synthetic reasons, aliases, normalization, substring matching,
reason inference, missing blockers, widened horizons, or multiple receiving
segments are invalid.

## 10. Determinism and atomic publication

Workers use separate newly created task-owned temporary directories under the
private parent. Machine-readable outputs use UTF-8 without BOM, LF endings, one
terminal newline, sorted keys, compact JSON separators, and
`ensure_ascii=True`.

Only after object equality, byte equality, identity recomputation, exact
five-file scope, unchanged input hashes, unchanged repository state, and every
STOP gate passes may one validated directory be atomically moved to the absent
final root.

On failure, remove only the two task-owned temporary directories and the
ephemeral harness. Never delete, overwrite, rename, normalize, or repair an
accepted input or pre-existing final root.

## 11. Minimum independent verification matrix

A future authorized harness and post-run audit must prove:

1. exact commit, proposal, dependency, input, root, and ignore bindings;
2. rejection before deserialization for input scope, order, length, or hash drift;
3. exact V3 selection in both structural and continuity consumers;
4. all 133 archived segment identities reconcile without mutation;
5. V3/V5 mismatch, mixed identity, unsupported version, or fallback is rejected;
6. canonical Candidate Evidence rebuild equals the accepted control exactly;
7. exact eligible continuity UNKNOWN branch with non-null manifest;
8. authentic Inducement human reason plus exact blocker-token enforcement;
9. exact boundary, group, horizon, lineage, direction, count, and identity
   reconciliation;
10. exactly one continuity and one resolver call per worker;
11. two fresh worker objects and serialized bytes are identical;
12. exact five-file publication occurs only after all gates pass;
13. failure leaves the final root absent and removes only task-owned residue;
14. accepted inputs, source, tests, `HEAD`, index, and tracked worktree remain
    unchanged; and
15. no private rows enter logs, tracked output, prompts, or any language model.

## 12. Outcome semantics remain non-promotional

The transaction observes rather than optimizes:

- `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is admissible only when its exact
  public status, reasons, blockers, identities, order, and manifest semantics
  pass; and
- `INVALID`, exception leakage, nondeterminism, or contract drift fails the
  transaction and leaves the final root absent.

Every admissible output is permanently `NON_PROMOTABLE_DIAGNOSTIC`. It cannot
reopen Phase A, rescue its negative control, enter a corpus, become a feature,
label, target, or model input, expose OOS, or authorize training, integration,
prediction, execution, or trading.

## 13. Later execution and Git gates

Before any private execution, this exact proposal must:

1. pass an exact one-file documentation audit;
2. be committed locally as the only staged path;
3. receive separate exact GitHub privacy/export authorization;
4. be pushed and independently verified at `origin/main`; and
5. receive separate exact private two-run authorization naming the pushed
   proposal commit and this locked transaction.

No broad trust statement, earlier failed-run authorization, prior proposal, or
successful public test grants those later permissions.
