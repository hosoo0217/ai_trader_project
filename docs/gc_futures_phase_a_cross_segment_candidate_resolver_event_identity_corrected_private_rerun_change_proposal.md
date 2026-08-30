# GC Phase-A Cross-Segment Candidate Resolver Event-Identity-Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-EVENT-IDENTITY-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Exact pushed implementation: `2711e87bc19662408e66cf890b9ba2a1fdfe863a`.
- Pushed correction proposal: `b031b6dd3c7290e0febc7fbf33c86361376cbeb6`.
- Correction proposal SHA-256: `0A80F10D29465E4C62F8D522AC8644A057996FEAF797D87F41553FC4AE3D5C16`.
- Correction checkpoint SHA-256: `631D7DEFAD4C0F9E278787F57BA530B6F3F896AB689EE9272E5C5033D0C77319`.
- Governing control-frontier proposal SHA-256: `D6276F36C3470704940D55F5A56BF0B480669B0DCAD6C247E70BB53DEDE06C2B`.
- GitHub parity at proposal start: local `HEAD`, `origin/main`, and remote
  `refs/heads/main` all equal the exact pushed implementation.
- Classification: documentation-only, fail-closed, non-promotional private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This record defines a possible new transaction after the resolver
event-identity correction. Creating or committing it does not authorize a
private run, private payload access, dataset or corpus build, feature or label
build, final-OOS access, training, integration, prediction, strategy, risk,
order, execution, trading, or remote push.

## 2. Consumed transaction and corrected defect

The transaction authorized under the earlier control-frontier proposal stopped
in fresh worker 1 when the resolver returned `INVALID`. Worker 2 did not run,
no retry occurred, and no final root was published. That authorization and its
transaction are consumed and may not be reused.

The failure was caused by a public resolver defect. Canonical structure events
bind their IDs to the actual broken-swing price, but the resolver did not
receive that price and reconstructed it as confirmation close plus or minus one
tick. Canonical multi-tick breaks therefore failed identity validation.

Exact pushed commit `2711e87bc19662408e66cf890b9ba2a1fdfe863a`
removes only that unavailable-boundary reconstruction. The resolver now keeps
its semantic, ownership, provenance, timing, observation, FVG, transition,
snapshot, lifecycle, history, continuity, pending-horizon, precedence, and
result checks while requiring:

1. `event.event_id == event_ref.object_id`; and
2. the canonical event-object SHA-256 equals `event_ref.object_digest`.

Public test-first evidence recorded by the checkpoint is:

- clean RED: `3 failed, 67 deselected`;
- targeted GREEN: `3 passed, 67 deselected`;
- resolver plus continuity regression: `131 passed`; and
- complete public suite: `2674 passed`.

These tests establish the public correction only. They do not predict or
promote any future private result.

## 3. Exact documentation-only scope

This proposal task may create and commit only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_event_identity_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, runtime, integration,
strategy, risk, execution, trace, or other documentation file may change.

## 4. Global freeze and authority boundary

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. This proposal grants no authority to:

- read, enumerate, hash, deserialize, copy, normalize, or modify a private root;
- access the embargo interval or sealed final-OOS payload;
- create or promote canonical Candidate Evidence;
- build a dataset, corpus, feature, label, target, split, model, or outcome;
- call a local or remote language model with private market evidence;
- add runtime hooks, exports, package wiring, or integration;
- emit BUY/SELL, confidence, position sizing, entry, exit, PnL, order, or
  execution authority; or
- push this proposal without a separate informed GitHub export authorization.

No public test, private diagnostic status, or documentation audit can lift
these restrictions.

## 5. Exact pushed public implementation binding

A future transaction must start from exact pushed commit
`2711e87bc19662408e66cf890b9ba2a1fdfe863a` and these exact public bytes:

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

Any commit, source, test, hash, signature, version, or contract drift is a STOP
condition requiring a fresh proposal. A future harness must not patch, monkey
patch, wrap, replace, bypass, or dynamically rewrite these dependencies.

Runtime `tzdata` must be exactly `2026.2`. Every fresh worker must explicitly
place the exact repository root on `sys.path` before project imports. Network,
package installation, fallback import, environment-dependent discovery, and
private helper access are forbidden.

## 6. Exact accepted private input binding

The only admissible future private input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Before deserialization it must contain exactly these eight immutable members:

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

The exact artifact-set identity is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Missing, extra, renamed, reordered, length-drifted, hash-drifted, or
manifest-member-drifted evidence must stop before deserialization. The accepted
input is immutable and cannot be repaired, relabeled, normalized, overwritten,
or copied into output. Final-OOS remains outside scope.

This documentation task does not access the private root.

## 7. Exact output and fresh-worker roots

The only future final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent and Git-ignored at future execution preflight. If present,
the transaction stops without opening, deleting, replacing, or repairing it.

Two separately absent, task-owned, Git-ignored worker roots must be created
under the same private parent only after all preflight gates pass. Each worker
may produce exactly:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw rows, source export, accepted payload copy, candidate payload, feature,
label, target, model, backtest, prompt, cache, strategy, risk, order, or
execution artifact is allowed.

## 8. Exact event-identity-corrected two-run transaction

Only after a separate exact private-run authorization may two independent
fresh workers execute. Each worker must perform this fixed sequence exactly
once:

1. verify the exact pushed proposal commit, proposal SHA-256, implementation
   commit, public dependency hashes, Git-ignore state, runtime timezone, and
   timezone-data version;
2. verify the exact eight-file private input scope, canonical order, lengths,
   hashes, manifest membership, and artifact-set identity before deserialization;
3. deserialize fresh immutable development dataset, normalized calendar,
   structural seed, canonical Candidate Evidence control, and binding metadata,
   with no object sharing between workers;
4. rebuild Candidate Evidence exactly once with committed default configuration
   and require exact equality with the accepted canonical control;
5. call `analyze_gc_candidate_frontier_evidence()` exactly once and require the
   authentic public frontier contract in Section 9;
6. call `analyze_gc_cross_segment_continuity()` exactly once with that frontier
   and require exact `UNKNOWN / CANONICAL_CONTROL_UNKNOWN`, a non-null canonical
   continuity manifest, unchanged legacy prefix, and exactly one appended
   frontier boundary from source ordinal `113` to receiver ordinal `114`;
7. construct resolver wrappers only from the exact frontier pending result and
   immediately adjacent receiving groups owned by that appended boundary;
8. call `resolve_gc_cross_segment_candidates()` exactly once;
9. validate exact public result status, reasons, blockers, precedence, ordering,
   counts, lineage, direction, lifecycle, three-closed-bar arithmetic,
   non-promotion flags, and complete identity graph;
10. require every receiving structure event to equal its continuity reference
    `object_id` and canonical `object_digest`, without reconstructing or
    inferring a broken-swing price;
11. serialize only the exact five-file diagnostic scope; and
12. compare complete worker object graphs and all five serialized byte streams
    before any publication.

An `INVALID` continuity or resolver result, null manifest, control drift,
ineligible status or reason, event/reference mismatch, exception,
nondeterminism, hash drift, malformed wrapper, unexpected file, or output-scope
drift fails the complete transaction. No subset retry, second configuration,
evidence repair, status-targeted retry, fallback version, or third worker is
allowed.

## 9. Authentic frontier and pending-result contract

The accepted canonical control must remain:

```text
candidate status = UNKNOWN
candidate candidates = ()
candidate segment-result count = 113
candidate segment-result ordinals = 0..112
candidate manifest = null
```

The frontier result must remain:

```text
status = VALID
reason = CONTROL_FRONTIER_CONTINUATION_EVIDENCE_COMPLETE
frontier ordinal = 113
source ordinal = 113
receiving ordinal = 114
source pending status = UNKNOWN
source pending reasons =
  ("one or more confirmation horizons are incomplete",)
source pending blockers =
  ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending horizon count >= 1
```

The authentic incomplete-horizon contract is exactly:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

Token-only synthetic reasons, aliases, normalization, substring matching,
inferred blockers, widened horizons, multiple receiving segments, concatenated
bars, renumbered observations, timestamp/tick repair, or fabricated event
identity are invalid.

The previously recorded source and receiving identities are preflight
assertions only and may never be selection constants:

```text
source segment ID = d26efed86441a98dc505694f8f35a5ad09087df91079e0618ee6f04656d13aa7
source contract / trade date = GCM26-COMEX / 2026-04-27
receiving segment ID = 90952af1d7cd08d8b3558256e1bca862937fd662bf51412cc913cf8f7719a44b
receiving contract / trade date = GCM26-COMEX / 2026-04-28
```

## 10. Determinism and atomic publication

Machine-readable output must use UTF-8 without BOM, LF endings, one terminal
newline, sorted keys, compact JSON separators, and `ensure_ascii=True`.

Only after complete object equality, byte equality, identity recomputation,
exact five-file scope, unchanged input hashes, unchanged repository state, and
all STOP gates pass may worker 1 be atomically moved to the absent final root.
Worker 2 and the ephemeral harness must then be removed.

On failure, only the two verified task-owned worker directories and ephemeral
harness may be removed. Accepted input, any pre-existing final root, tracked
files, staged state, unrelated untracked drafts, and other private roots must
remain untouched.

## 11. Minimum independent audit

The post-run audit must prove:

1. exact pushed proposal, proposal hash, implementation, public dependencies,
   runtime, input, artifact-set, root, and ignore bindings;
2. rejection before deserialization for input scope, order, length, hash, or
   manifest drift;
3. exactly one Candidate Evidence rebuild, frontier call, continuity call, and
   resolver call in each fresh worker;
4. canonical-control equality, authentic frontier evidence, exact adjacent
   boundary, and unchanged continuity prefix;
5. exact event/reference ID and object-digest equality without inferred
   broken-swing boundaries;
6. all remaining event, FVG, transition, snapshot, lifecycle, history, horizon,
   group, lineage, direction, precedence, and arithmetic gates remain active;
7. both worker object graphs and five output streams are byte-identical;
8. exact five-file atomic publication, or an absent final root on failure;
9. accepted inputs, source, tests, `HEAD`, index, and tracked worktree are
   unchanged;
10. task-owned temporary residue is removed; and
11. no private rows enter logs, tracked files, prompts, any language model, or
    network request.

The audit then stops. No result status authorizes another run or promotion.

## 12. Outcome semantics and mandatory STOP

Resolver `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is observationally
admissible only when its exact public status, reasons, blockers, identities,
order, manifest, and precedence semantics pass. `INVALID`, exception leakage,
nondeterminism, or contract drift fails the transaction and leaves the final
root absent.

Every admissible output remains permanently
`NON_PROMOTABLE_DIAGNOSTIC`. It cannot reopen Phase A, rescue a negative
control, enter a dataset or corpus, become a feature, label, target, split, or
model input, expose OOS, or authorize training, integration, prediction,
strategy, risk, order, execution, or trading.

## 13. Later execution and Git gates

Before any private execution, this exact proposal must:

1. pass an exact one-file documentation audit;
2. be committed locally as the sole staged path;
3. receive a separate informed GitHub privacy/export authorization;
4. be pushed and independently verified at remote `main`; and
5. receive a new exact private two-run authorization naming the pushed proposal
   commit, proposal SHA-256, and exact implementation commit.

General continuation language, the consumed failed-run authorization, an older
proposal, a public test pass, or trust in the operator grants none of these
later permissions.
