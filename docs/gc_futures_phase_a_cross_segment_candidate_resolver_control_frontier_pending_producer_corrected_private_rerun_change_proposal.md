# GC Futures Phase-A Cross-Segment Candidate Resolver Control-Frontier Pending-Producer Corrected Private Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-CONTROL-FRONTIER-PENDING-PRODUCER-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Current pushed baseline: `58e4409a11edef5e0f9b2c156ac2e3da4c099703`.
- Pushed resolver implementation: `8432341201e9d96d07483052dc8892ecae1b551b`.
- Parent private-rerun proposal commit: `58e4409a11edef5e0f9b2c156ac2e3da4c099703`.
- Parent proposal SHA-256: `257E29DA049AF9B9023CB5949D476C03C0F2109B83FBD55E0F5FAD866F4C06B7`.
- Classification: documentation-only, fail-closed, non-promotional private-rerun proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_EXECUTION`.

This proposal records one harness-only producer-selection correction. It does
not authorize private execution, source or test changes, dataset or corpus
builds, features, labels, final-OOS access, training, integration, prediction,
orders, execution, trading, staging, committing, or pushing.

## 2. Consumed failed transaction

The exact transaction authorized against the parent proposal passed its public
and private byte preflight, preserved the accepted `UNKNOWN` Candidate Evidence
control with a null manifest, selected the committed public default Candidate
Evidence configuration by omitting the `candidate_config` keyword, deserialized
the accepted graph, and reached authentic pending-evidence construction in the
first fresh worker.

The worker then stopped at the ephemeral harness guard:

```text
ineligible pending producer status
```

The worker-2 execution, resolver invocation, output serialization, equality
comparison, and atomic publication did not occur. The parent honored the
no-retry rule. The final root and both worker roots remained absent, the
ephemeral harness was removed, the eight accepted members retained their exact
lengths and SHA-256 values, tracked and staged diffs remained empty, and
`HEAD == origin/main == 58e4409a11edef5e0f9b2c156ac2e3da4c099703`.

That authorization is consumed and must not be reused.

## 3. Exact failure classification

The accepted canonical control has this immutable shape:

```text
status = UNKNOWN
reasons = ("a swept pool has a truncated confirmation horizon",)
blocking_reasons = ("a swept pool has a truncated confirmation horizon",)
candidates = ()
segment_result_count = 113
segment_result_ordinals = 0..112
manifest = null
```

The first dataset segment not represented by the preserved control prefix is
therefore determined before any pending-producer call:

```text
frontier ordinal = len(control.segment_results) = 113
source segment ID = d26efed86441a98dc505694f8f35a5ad09087df91079e0618ee6f04656d13aa7
contract = GCM26-COMEX
trade date = 2026-04-27
partition = DEVELOPMENT
bar count = 276
first bar = 2026-04-26T22:05:00.000000Z
last bar = 2026-04-27T21:00:00.000000Z
```

The exact adjacent receiving segment is:

```text
receiving ordinal = 114
receiving segment ID = 90952af1d7cd08d8b3558256e1bca862937fd662bf51412cc913cf8f7719a44b
contract = GCM26-COMEX
trade date = 2026-04-28
partition = DEVELOPMENT
bar count = 276
first bar = 2026-04-27T22:05:00.000000Z
last bar = 2026-04-28T21:00:00.000000Z
```

The committed earlier cross-session diagnosis established that source ordinal
113 contains the qualifying sweep/reclaim at segment-local index 274, followed
by only one available confirmation observation at index 275. The public
Inducement pending-horizon contract therefore owns the incomplete three-closed-
bar horizon at this exact control frontier.

The failed ephemeral harness applied the `UNKNOWN` producer requirement across
a broader continuity-source set. A complete source segment with no incomplete
horizon legitimately produces `NONE`; it is not malformed. Treating every
continuity source as if it were the preserved control frontier made a valid
non-frontier status fatal before the exact frontier evidence was isolated.

Root cause:

`HARNESS_PENDING_PRODUCER_SCOPE_NOT_BOUND_TO_CANONICAL_CONTROL_FRONTIER`.

This does not establish a defect in `smc/inducement.py`, continuity, the
resolver, the accepted dataset, the structural seed, or the canonical control.

## 4. Exact correction boundary

A future separately authorized harness must derive the producer source before
calling an analyzer:

1. require exact canonical-control `UNKNOWN` shape from Section 3;
2. compute `frontier_ordinal = len(control.segment_results)`;
3. require `frontier_ordinal == 113`;
4. require control result ordinals to be exactly `range(frontier_ordinal)` and
   their segment IDs to match the first 113 accepted dataset segment IDs;
5. bind accepted dataset segment 113 to the exact source metadata in Section 3;
6. bind dataset segment 114 to the exact adjacent receiving metadata in
   Section 3;
7. locate exactly one eligible continuity boundary whose source ordinal and ID
   equal the locked frontier source and whose receiving ordinal and ID equal
   the locked adjacent receiving segment; and
8. fail before pending analysis if that exact boundary is absent, duplicated,
   ineligible, reordered, cross-contract, non-adjacent, or identity-drifted.

The worker must call `analyze_inducement_pending_horizons()` exactly once, only
for accepted source ordinal 113. It must not iterate all continuity boundaries,
call the producer speculatively, observe statuses and filter afterward, retry
with another segment, or select a segment because it happens to return the
desired status.

## 5. Exact authentic pending contract

The single producer result is admissible only when it has this exact public
shape:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon_count >= 1
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

Every emitted horizon must preserve the producer's public identity, direction,
lineage, sweep moment, available confirmation prefix, first-known moment, and
exact arithmetic:

```text
0 <= available_count < 3
missing_confirmation_bar_count = 3 - available_count
```

`NONE`, `VALID`, `AMBIGUOUS`, `INVALID`, a null field, an empty pending tuple,
an alias reason, a normalized token, a widened horizon, a moved sweep, or an
identity mismatch fails the transaction. No pending ID or object may be
synthesized by the harness.

## 6. Receiving evidence restriction

Only canonical receiving groups owned by the single exact frontier boundary
may be wrapped. Each group must remain in the continuity manifest order and
must bind exact accepted ordinal-114 public detector evidence:

- one matching Dealing Range structure event;
- one matching Fair Value Gap;
- their exact transition and snapshot histories; and
- the immutable fully closed ordinal-114 observations.

The harness must not wrap groups from any other boundary, search farther than
the immediately adjacent receiving segment, concatenate segments, renumber
bars, modify timestamps or integer ticks, infer identities, or repair missing
evidence. Complete but insufficient exact receiving evidence may lead to the
resolver's public `UNKNOWN`; malformed evidence must fail closed.

## 7. Immutable accepted input binding

The only private input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

It must contain exactly these eight members before and after any future run:

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

The locked input artifact-set identity is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
No accepted member may be edited, renamed, replaced, normalized, repaired, or
deleted.

## 8. Exact public dependency binding

Before a future run, exact dependency bytes must match:

| Path | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `D0BBB35F6D6A32CD012996867E56EDCDDC031B75790A19A11684E66290BFE68D` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_cross_segment_continuity.py` | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |
| `tests/test_inducement.py` | `791567124B3ABA381A4FB84CBB4B37125E9404AF1AFE276717A3042B268EF8FE` |

The runtime timezone-data version remains `2026.2`. The implementation commit
must remain an ancestor of the future exact baseline. The repository root must
be inserted explicitly into each fresh worker's `sys.path` before any project
import. No fallback import, monkey patch, package install, network call, or
environment-dependent discovery is allowed.

## 9. Continuity call and default-config preservation

Each fresh worker must call `analyze_gc_cross_segment_continuity()` exactly
once. The `candidate_config` keyword must remain omitted so the audited public
`GCCandidateEvidenceConfig()` default is selected. The accepted control must
remain exact `UNKNOWN` with a null Candidate Evidence manifest.

The continuity result must be exact:

```text
status = UNKNOWN
reasons = ("CANONICAL_CONTROL_UNKNOWN",)
blocking_reasons = ("CANONICAL_CONTROL_UNKNOWN",)
manifest = non-null canonical GCCrossSegmentContinuityManifest
```

Any other status, reason, blocker, null manifest, configuration drift,
identity mismatch, or malformed ordering fails before pending construction.

## 10. Resolver call and observational outcomes

After exact frontier-only wrapper construction, each fresh worker must call
`resolve_gc_cross_segment_candidates()` exactly once with keyword-only
arguments. No subset retry or alternative evidence set is permitted.

The transaction is observational and must not optimize for a status. A public
`VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` resolver result may be serialized
only after complete identity and precedence validation. `INVALID`, an
exception, an unexpected reason, malformed identity, non-determinism, or
scope drift fails the transaction and publishes nothing.

Every admissible serialized result remains
`NON_PROMOTABLE_DIAGNOSTIC` and carries explicit false flags for promotion,
training, feature/label build, OOS use, integration, prediction, execution,
and trading.

## 11. Exact output and atomic transaction

The final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent before any future transaction. Each of two fresh workers
must use a separate absent ignored temp root and may serialize only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw bars, accepted payload copies, detector payloads, features, labels,
outcomes, models, prompts, caches, backtests, risk, strategy, or execution
artifacts may be written.

Each worker independently verifies, deserializes, validates, reconstructs,
analyzes, resolves, and serializes. The complete canonical object-graph
digests and all five serialized byte streams must be equal. Only then may
worker 1 be atomically moved to the absent final root. Worker 2 and the
ephemeral harness must be removed.

Any failure consumes the authorization: no third worker, retry, adaptive
repair, alternate frontier, alternate configuration, fallback, or partial
publication is allowed. The final root must remain absent and only task-owned
residue may be removed.

## 12. Independent audit and STOP boundary

An independent post-transaction audit must prove:

- exact proposal, baseline, implementation, dependency, runtime, input, and
  artifact-set bindings;
- explicit pre-import repository bootstrap;
- exact `UNKNOWN / 113 / null-manifest` control preservation;
- pre-bound source ordinal 113 and receiving ordinal 114 identities;
- exactly one frontier pending-producer call per worker;
- exact authentic pending reason, blocker, horizon identity, and arithmetic;
- exactly one continuity and one resolver call per worker;
- only frontier-bound receiving groups;
- two fresh executions with object and byte equality;
- exact five-file atomic scope or, on failure, an absent final root;
- unchanged accepted input, source, tests, staged state, and tracked worktree;
- cleanup of task-owned temp roots and harness; and
- zero training, final-OOS, feature/label, integration, prediction, execution,
  or trading access.

The audit must then STOP. It cannot authorize promotion or another run.

## 13. Authorization gate

This proposal may be staged and committed locally only after a cached-diff
audit proving it is the sole staged path. Publishing the proposal to a remote
requires separate informed GitHub privacy/export authorization.

Even after a pushed exact commit and recorded SHA-256 exist, the private
two-worker transaction requires a separate exact authorization naming the
pushed proposal commit and its SHA-256. General continuation language is not
private-run authority. Source/test changes, training, final-OOS access,
feature/label build, integration, prediction, execution, and trading remain
forbidden.
