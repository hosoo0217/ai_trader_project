# GC Phase-A Control-Frontier Resolver Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CONTROL-FRONTIER-RESOLVER-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Exact pushed baseline: `3f6f308f54395365f4c5355c1475828712e93457`.
- Pushed frontier-contract proposal: `4d4c6c8d1959d2eb39673146d3b1d927da4c23da`.
- Pushed frontier implementation: `3f6f308f54395365f4c5355c1475828712e93457`.
- Frontier checkpoint SHA-256: `E7C61F0DD5E4B5CB162FAEAA7170B33765708DCD0EEBFFA609B2E1E3A0EA624C`.
- Classification: documentation-only, fail-closed, non-promotional private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This record defines the first private diagnostic transaction permitted to use
the pushed public control-frontier contract. It does not authorize the private
run, access any private root, build a dataset/corpus/feature/label, access final
OOS, train a model, integrate a component, predict, backtest, place an order,
execute a trade, stage, commit, or push anything.

## 2. Superseded and consumed transaction

The earlier control-frontier pending-producer private proposal was consumed by
its preflight-blocked transaction. At that baseline, the canonical control
contained promoted results only for ordinals `0..112`; the continuity analyzer
could therefore emit no public boundary for required ordinals `113 -> 114`.
Its ephemeral harness was never created and its output root remained absent.

The pushed additive implementation now provides a public, immutable solution:

- `analyze_gc_candidate_frontier_evidence()` derives ordinal `113` from the
  exact canonical-control prefix and obtains authentic pending evidence only
  from `analyze_inducement_pending_horizons()`;
- `analyze_gc_cross_segment_continuity(frontier_evidence=...)` appends at most
  one recomputed frontier boundary and canonical receiving groups; and
- canonical-control status remains `UNKNOWN` with a non-null continuity
  manifest and no candidate promotion.

The old proposal, hashes, authorization, and harness design may not be reused.
This proposal requires the pushed public contract directly and forbids a
harness-side detector reconstruction, private helper call, fabricated result,
reason parsing, ordinal constant as selection logic, retry, or fallback.

## 3. Immutable canonical-control and frontier binding

Each future fresh worker must deserialize and validate the accepted
development-only graph, rebuild Candidate Evidence exactly once, and require:

```text
candidate status = UNKNOWN
candidate candidates = ()
candidate segment-result count = 113
candidate segment-result ordinals = 0..112
candidate manifest = null
```

The worker then calls `analyze_gc_candidate_frontier_evidence()` exactly once
with the same dataset, calendar, seed, canonical control, and committed default
`GCCandidateEvidenceConfig()`. It accepts only:

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

Every control result ID must match the same dataset ordinal. Source and
receiving segment IDs, development partitions, contract, calendar coverage,
missing-bar flags, four base-detector results, four result IDs, pending-horizon
IDs, reason token, available prefix, and `missing == 3 - available` arithmetic
must remain exact. The frontier ID must recompute through the pushed public
identity function. No private value may be embedded in source code or tests.

The private diagnosis previously recorded these expected accepted identities;
they are preflight assertions, never selection constants:

```text
source segment ID = d26efed86441a98dc505694f8f35a5ad09087df91079e0618ee6f04656d13aa7
source contract / trade date = GCM26-COMEX / 2026-04-27
receiving segment ID = 90952af1d7cd08d8b3558256e1bca862937fd662bf51412cc913cf8f7719a44b
receiving contract / trade date = GCM26-COMEX / 2026-04-28
```

## 4. Exact continuity and resolver calls

Each worker calls `analyze_gc_cross_segment_continuity()` exactly once with the
same validated public inputs, exact canonical control, exact recomputed
frontier result, and default Candidate Evidence configuration. The result must
be:

```text
status = UNKNOWN
reasons = ("CANONICAL_CONTROL_UNKNOWN",)
blocking_reasons = ("CANONICAL_CONTROL_UNKNOWN",)
manifest = non-null canonical GCCrossSegmentContinuityManifest
```

All legacy boundaries/groups must remain their exact ordered prefix. Exactly
one frontier boundary owned by source ordinal `113` and receiver ordinal `114`
must follow them. Its IDs must bind the canonical-control digest, frontier ID,
and source evidence; its receiving groups must additionally bind receiving
evidence and preserve manifest order.

The worker creates resolver wrappers only from:

- `frontier.source_pending_result` owned by the exact frontier source; and
- continuity receiving groups owned by the exact frontier boundary, with
  exact ordinal-114 public Structure Event, Fair Value Gap, transition,
  snapshot, and closed-observation evidence.

It then calls `resolve_gc_cross_segment_candidates()` exactly once. No other
boundary, wider horizon, second receiving segment, concatenation, bar
renumbering, timestamp/tick repair, subset retry, alternate configuration, or
status-targeted retry is permitted.

Resolver `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is observationally
admissible after full identity and precedence validation. `INVALID`, an
exception, identity drift, malformed ordering, non-determinism, or unexpected
reason publishes nothing and consumes the authorization.

## 5. Exact accepted private input binding

The only future private input root is:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

It must contain exactly these immutable members before and after execution:

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

The locked input artifact-set identity remains
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
No input may be changed, copied into output, renamed, repaired, normalized, or
deleted. Final-OOS payload access is forbidden.

## 6. Exact pushed public dependency binding

The future preflight must require `HEAD == origin/main` at this proposal's
later exact pushed commit, with direct parent
`3f6f308f54395365f4c5355c1475828712e93457`, and these exact bytes:

| Path | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `D0BBB35F6D6A32CD012996867E56EDCDDC031B75790A19A11684E66290BFE68D` |
| `analysis/gc_candidate_evidence_builder.py` | `955D5B88953987D969530DFF16C39D8AF769EA7FECEE866E9BC684675B05482A` |
| `analysis/gc_cross_segment_continuity.py` | `E60DF0D3E16556A81B5CE9AE2F0FE739D3F02E9BC24D4788B76978C67F39571C` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_candidate_evidence_builder.py` | `C60D2F4A0C7220EF0488BB3776C65F933674E74ED96960E576891B17C2BAFDDC` |
| `tests/test_gc_cross_segment_continuity.py` | `8E03055B90FD35323F442A091E425D848561F8DAB5CF8390985BE37053D7B3A0` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |
| `tests/test_inducement.py` | `791567124B3ABA381A4FB84CBB4B37125E9404AF1AFE276717A3042B268EF8FE` |

Runtime `tzdata` must be exactly `2026.2`. Every fresh worker must insert the
repository root explicitly into `sys.path` before project imports. Network,
package installation, monkey patching, fallback imports, environment-dependent
discovery, filesystem search, and private helper access are forbidden.

## 7. Exact atomic two-run output transaction

The final root is unchanged:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent before execution. Two separately absent ignored worker roots
must each produce only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

Each worker independently verifies bytes, deserializes, validates, rebuilds,
analyzes the frontier, analyzes continuity, wraps exact evidence, resolves,
and serializes. Complete canonical object graphs and all five output byte
streams must be equal. Only then may worker 1 be atomically moved to the absent
final root. Worker 2 and the ephemeral harness must be removed.

Any failure permits no retry or third worker. The final root remains absent;
only verified task-owned temporary roots and harness may be removed. Accepted
input, tracked files, staged state, unrelated untracked drafts, and other
private roots remain untouched.

## 8. Independent audit and mandatory STOP

After an authorized transaction, an independent audit must prove:

- exact pushed proposal commit and proposal SHA-256;
- exact implementation, dependency, runtime, input, and artifact-set bindings;
- exact `UNKNOWN / 113 / null-manifest` canonical control;
- one exact `VALID` public frontier result per worker;
- exact source `113`, receiver `114`, IDs, contract, and calendar binding;
- authentic pending identity, reason, blocker, prefix, and arithmetic;
- exactly one candidate rebuild, frontier call, continuity call, and resolver
  call per worker;
- one appended frontier boundary after an unchanged legacy prefix;
- resolver wrappers only from the frontier pending result and its immediately
  adjacent receiving groups;
- two fresh object graphs and five output streams are byte-equal;
- exact five-file atomic output or an absent final root on failure;
- unchanged accepted inputs, source, tests, Git index, and tracked worktree;
- cleanup of task-owned temporary artifacts; and
- zero final-OOS, dataset/corpus, feature/label, training, model, integration,
  prediction, strategy, risk, order, execution, or trading access.

The audit then stops. No result status grants promotion or another run.

## 9. Proposal scope, authorization, and non-authority

This documentation-only step may create exactly this one tracked proposal:

`docs/gc_futures_phase_a_control_frontier_resolver_private_rerun_change_proposal.md`

It reserves no source/test changes. Staging and a local documentation commit
require a cached audit proving this is the sole staged path. Remote push is a
separate informed GitHub export decision.

Even after a pushed exact proposal commit exists, the private transaction
requires a new exact authorization naming that pushed commit and proposal
SHA-256. General continuation language is not private-run authority. Dataset or
corpus build, final-OOS access, feature/label build, training, integration,
prediction, backtesting, strategy, risk, orders, execution, and trading remain
forbidden.
