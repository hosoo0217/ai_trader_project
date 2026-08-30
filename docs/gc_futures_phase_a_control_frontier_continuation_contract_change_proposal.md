# GC Futures Phase-A Control-Frontier Continuation Contract Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CONTROL-FRONTIER-CONTINUATION-CONTRACT-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Current pushed baseline: `334bf6f67b9d283abf5e724e49203cb69329c84b`.
- Current pushed resolver implementation: `8432341201e9d96d07483052dc8892ecae1b551b`.
- Preflight-blocked rerun proposal commit: `334bf6f67b9d283abf5e724e49203cb69329c84b`.
- Preflight-blocked proposal SHA-256: `9337B6FF405C101CC15557060419A6F02C83935248BB0062D753BBDB5E2A5C24`.
- Classification: documentation-only, test-first additive public-contract proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_IMPLEMENTATION`.

This proposal defines the smallest public source/test change needed before a
future private resolver transaction can represent the preserved canonical
control frontier. It grants no implementation, private-run, dataset/corpus,
feature/label, final-OOS, training, integration, prediction, execution,
trading, staging, committing, or pushing authority.

## 2. Consumed preflight-blocked authorization

The private transaction authorized against commit `334bf6f...` did not start.
Exact preflight proved that its required continuity boundary was structurally
unreachable under the pushed public implementation:

```text
accepted canonical-control result count = 113
accepted canonical-control ordinals = 0..112
continuity loop = range(len(segment_results) - 1)
maximum emitted boundary = 111 -> 112
required control frontier boundary = 113 -> 114
```

No ephemeral harness or worker was created. No analyzer or resolver was called,
no output root was created, all eight accepted input hashes remained exact,
and Git remained clean apart from three pre-existing unrelated untracked draft
documents. That authorization is consumed and cannot be reused.

## 3. Root-cause classification

`build_gc_candidate_evidence()` analyzes segments in strict ordinal order. On
accepted source ordinal 113, `analyze_inducements()` correctly returns
`UNKNOWN` because a qualifying sweep/reclaim has fewer than three available
strictly later closed bars. `_blocked_detector_result()` returns immediately
before ordinal 113 is appended to `promoted_segments`.

`analyze_gc_cross_segment_continuity()` correctly validates and rebuilds the
canonical control, but its boundary loop is intentionally limited to adjacent
pairs already present in `canonical_control.segment_results`. It therefore has
no public source-result object for ordinal 113 and no public receiving-result
object for ordinal 114. A harness cannot legitimately fabricate either object,
call private helpers, parse reason strings, duplicate detector logic, or append
opaque identities.

Root cause:

`MISSING_PUBLIC_CANONICAL_CONTROL_FRONTIER_CONTINUATION_EVIDENCE_CONTRACT`.

Not established as defects:

- accepted dataset or calendar coverage;
- structural seed identity;
- detector semantics;
- Inducement pending-horizon semantics;
- existing continuity behavior over promoted results;
- resolver validation or resolution semantics; or
- raw-data completeness.

## 4. Verified private boundary facts

These facts are diagnosis bindings only and must never become production
constants or test fixtures:

```text
canonical control status = UNKNOWN
canonical control candidates = ()
canonical control segment results = 113, ordinals 0..112
canonical control manifest = null
frontier source ordinal = 113
frontier source segment ID = d26efed86441a98dc505694f8f35a5ad09087df91079e0618ee6f04656d13aa7
frontier source contract/trade date = GCM26-COMEX / 2026-04-27
frontier receiving ordinal = 114
frontier receiving segment ID = 90952af1d7cd08d8b3558256e1bca862937fd662bf51412cc913cf8f7719a44b
frontier receiving contract/trade date = GCM26-COMEX / 2026-04-28
```

The accepted control and dataset hashes remain:

| Artifact | SHA-256 |
|---|---|
| Candidate Evidence | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| Dataset build result | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| Structural seed | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |

No implementation branch may special-case these values.

## 5. Exact reserved implementation paths

A future separately authorized test-first implementation may change exactly:

1. `analysis/gc_candidate_evidence_builder.py`;
2. `analysis/gc_cross_segment_continuity.py`;
3. `tests/test_gc_candidate_evidence_builder.py`;
4. `tests/test_gc_cross_segment_continuity.py`; and
5. `docs/gc_futures_phase_a_control_frontier_continuation_contract_checkpoint.md`.

No resolver, Inducement, dataset, structural-seed, feature/label, training,
integration, package-export, runtime-wiring, broker, risk, strategy, order, or
execution path is reserved.

## 6. Exact baseline hashes

Before implementation, the baseline must match:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `analysis/gc_candidate_evidence_builder.py` | 50867 | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | 61983 | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `tests/test_gc_candidate_evidence_builder.py` | 41189 | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `tests/test_gc_cross_segment_continuity.py` | 62364 | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |

Required unchanged regression dependencies are:

| Path | SHA-256 |
|---|---|
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |

Hash drift requires a new proposal; it may not be normalized or accepted
implicitly.

## 7. Additive frontier segment evidence contract

`analysis/gc_candidate_evidence_builder.py` may add exactly these public names:

- `GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION`, exact value
  `"GC-CANDIDATE-FRONTIER-EVIDENCE-V1"`;
- `GCCandidateFrontierIdentityKind` with only `FRONTIER`;
- frozen `GCCandidateFrontierSegmentEvidence`;
- frozen `GCCandidateFrontierEvidence`;
- frozen `GCCandidateFrontierEvidenceResult`;
- `make_gc_candidate_frontier_evidence_id()`; and
- `analyze_gc_candidate_frontier_evidence()`.

`GCCandidateFrontierSegmentEvidence` fields, in exact order, are:

| Field | Type |
|---|---|
| `segment_ordinal` | `int` |
| `segment_id` | `str` |
| `equal_liquidity_result` | `EqualLiquidityResult` |
| `dealing_range_result` | `DealingRangeResult` |
| `liquidity_map_result` | `LiquidityMapResult` |
| `fair_value_gap_result` | `FairValueGapResult` |
| `result_ids` | `tuple[str, ...]` |

`result_ids` contains exactly four canonical detector-result identities in
this order: Equal Liquidity, Dealing Range, Liquidity Map, Fair Value Gap.
They use the existing detector versions, configurations, segment ordinal/ID,
and canonical result payloads. Inducement and Kill Zone results are deliberately
absent because they are not dependency or receiving-group inputs.

`GCCandidateFrontierEvidence` fields, in exact order, are:

| Field | Type |
|---|---|
| `frontier_id` | `str` |
| `version` | `str` |
| `instrument` | `str` |
| `timeframe` | `str` |
| `dataset_id` | `str` |
| `seed_id` | `str` |
| `canonical_control_digest` | `str` |
| `frontier_ordinal` | `int` |
| `source_segment` | `GCCandidateFrontierSegmentEvidence` |
| `source_pending_result` | `InducementPendingHorizonResult` |
| `receiving_segment` | `GCCandidateFrontierSegmentEvidence` |

`GCCandidateFrontierEvidenceResult` fields, in exact order, are:

| Field | Type | Default |
|---|---|---|
| `status` | `SMCV2PrimitiveStatus` | required |
| `frontier` | `GCCandidateFrontierEvidence | None` | `None` |
| `reasons` | `tuple[str, ...]` | `()` |
| `blocking_reasons` | `tuple[str, ...]` | `()` |

All dataclasses are frozen. Tuples remain tuples. Public APIs are keyword-only.
Identity uses deterministic lowercase internal SHA-256 over canonical typed
payloads. No filesystem, clock, randomness, environment, network, or private
value enters the module.

## 8. Frontier analyzer signature

The exact additive analyzer is:

```python
def analyze_gc_candidate_frontier_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    canonical_candidate_evidence: GCCandidateEvidenceResult | None,
    config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCandidateFrontierEvidenceResult:
```

The analyzer must validate the same dataset, OOS prohibition, calendar,
runtime-tzdata, structural seed, configuration, and canonical-control rebuild
as `build_gc_candidate_evidence()` before frontier analysis.

It derives, never accepts, the frontier:

```text
frontier_ordinal = len(canonical_control.segment_results)
source_ordinal = frontier_ordinal
receiving_ordinal = frontier_ordinal + 1
```

Eligibility requires:

1. canonical control status exactly `UNKNOWN`;
2. zero canonical candidates and null canonical manifest;
3. nonempty, ordered, gapless control ordinals beginning at zero;
4. every control segment ID matching the same dataset ordinal;
5. source and receiving ordinals both existing in DEVELOPMENT only;
6. exact adjacent ordinals, same contract, no missing-bar flag, and canonical
   calendar coverage;
7. exact source pending producer status/reason/blocker contract; and
8. exact public detector identities for source and receiving segments.

Missing top-level context returns `UNKNOWN`; no remaining adjacent pair returns
`NONE`; malformed input returns `INVALID`; conflicting evidence returns
`AMBIGUOUS`; and one complete immutable frontier bundle returns `VALID` with
reason `CONTROL_FRONTIER_CONTINUATION_EVIDENCE_COMPLETE`.

## 9. Single shared base-detector implementation

The implementation must not duplicate the detector chain. A new local pure
helper may compute the four base detector results from one validated segment,
structural seed, and config. Both the existing candidate builder and the new
frontier analyzer must use this helper.

Refactoring must preserve existing `build_gc_candidate_evidence()` outputs
object-for-object and identity-for-identity for every existing public fixture.
The existing candidate builder retains its current stop semantics and public
signature. It must not promote the pending frontier, alter candidates, append a
manifest, or change reasons or blockers.

The source pending result must be created only by the existing public
`analyze_inducement_pending_horizons()` API using the exact source segment's
base detector outputs, structural events, FVG histories, and fully closed
integer-tick observations. Private `_Sweep` access, reason parsing, ID
fabrication, bar concatenation, renumbering, and detector reimplementation are
forbidden.

## 10. Exact source pending contract

A `VALID` frontier bundle requires:

```text
source_pending_result.status = UNKNOWN
source_pending_result.reasons =
    ("one or more confirmation horizons are incomplete",)
source_pending_result.blocking_reasons =
    ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
len(source_pending_result.pending_horizons) >= 1
```

Every pending horizon must preserve its public identity and exact
`missing_confirmation_bar_count == 3 - available_count` arithmetic with
`0 <= available_count < 3`. `NONE` means no applicable frontier and returns a
frontier result of `NONE`; `AMBIGUOUS` and `INVALID` propagate; any other
`UNKNOWN` reason is contained as `UNKNOWN` without a bundle.

## 11. Additive continuity input

`analyze_gc_cross_segment_continuity()` may add one optional keyword-only
parameter immediately before `candidate_config`:

```python
frontier_evidence: GCCandidateFrontierEvidenceResult | None = None
```

`None` preserves the exact legacy signature behavior, result objects,
identities, boundary/group ordering, reasons, blockers, and manifests.

When non-null, continuity must require an exact `VALID` frontier result and
recompute its identity and all bindings. The frontier source ordinal must equal
`len(canonical_control.segment_results)`; the receiving ordinal must be exactly
source plus one; both IDs must match the validated dataset; and the full
control prefix must remain unchanged.

Continuity first emits all legacy boundaries/groups exactly as today, then
appends at most one frontier boundary and its canonical receiving groups. The
existing `_boundary_decision()`, dependency-reference construction, receiving-
group construction, calendar validation, and canonical ordering rules remain
authoritative.

Frontier boundary identity must bind the canonical-control digest plus the
validated `frontier_id` and source segment evidence digest. Frontier receiving-
group identity must additionally bind the receiving segment evidence digest.
The manifest remains the existing public
`GCCrossSegmentContinuityManifest`; its ordered boundary/group ID tuples bind
the additive objects without a schema change.

Canonical control `UNKNOWN` still produces continuity:

```text
status = UNKNOWN
reasons = ("CANONICAL_CONTROL_UNKNOWN",)
blocking_reasons = ("CANONICAL_CONTROL_UNKNOWN",)
manifest = non-null
```

The additive evidence never upgrades the control status and creates no
candidate, feature, label, score, outcome, or promotion authority.

## 12. Fail-closed precedence

Validation order is fixed:

1. public argument types and config;
2. dataset/OOS/calendar/runtime/seed validation;
3. canonical-control rebuild and exact equality;
4. frontier result type, status, identity, and control binding;
5. derived source/receiving ordinal and dataset identity binding;
6. source pending contract and arithmetic;
7. base detector result identities;
8. boundary eligibility and dependency closure;
9. receiving event/FVG group construction; and
10. final manifest identity and result status.

Malformed evidence is `INVALID`. Missing optional evidence retains the legacy
path. No exception may escape the public containment boundary. No fallback,
repair, alternate ordinal, status filtering, subset retry, or best-effort
manifest is allowed.

## 13. Test-first matrix: candidate frontier

Focused public in-memory tests must prove at least:

1. exact `UNKNOWN` control plus an authentic pending source and adjacent
   receiving segment returns one deterministic `VALID` frontier bundle;
2. frontier ordinal is derived from control length and cannot be supplied;
3. control ordinals must be gapless, ordered, zero-based, and dataset-bound;
4. wrong source or receiving segment ID is `INVALID`;
5. cross-contract, non-adjacent, OOS, partial, or missing segment is rejected;
6. authentic pending status/reason/blocker and horizon arithmetic are exact;
7. pending `NONE`, `AMBIGUOUS`, `INVALID`, and unrelated `UNKNOWN` have the
   fixed status mapping from Section 10;
8. detector-result identities recompute exactly and reject mutation;
9. two executions are object-equal with equal frontier IDs;
10. existing candidate-builder fixtures remain object- and identity-equal;
11. public signature, annotations, frozen dataclasses, tuple fields, and exports
    are exact; and
12. no filesystem, environment, private root, OOS payload, or integration path
    is accessed.

Tests must use synthetic public fixtures. Private accepted bytes, IDs, dates,
contracts, and reason histories must not enter tests.

## 14. Test-first matrix: continuity

Focused public in-memory tests must prove at least:

1. `frontier_evidence=None` is exactly backward compatible;
2. exact valid frontier evidence appends one and only one boundary after all
   legacy boundaries;
3. the appended boundary owns the derived source and adjacent receiver;
4. dependency references come only from frontier source base evidence;
5. receiving groups come only from frontier receiving base evidence and the
   existing structural seed;
6. boundary/group IDs and manifest identity recompute deterministically;
7. duplicate, reordered, wrong-control, wrong-dataset, wrong-seed, wrong-
   config, wrong-ordinal, or mutated evidence is `INVALID`;
8. ineligible calendar/contract/partition boundaries remain ineligible and do
   not create receiving groups;
9. canonical control remains `UNKNOWN / CANONICAL_CONTROL_UNKNOWN` with a
   non-null manifest;
10. two executions are object-equal and identity-equal;
11. existing continuity tests pass unchanged except explicit signature/export
    assertions updated for the additive input; and
12. resolver regressions pass without resolver source/test changes.

## 15. Verification gate

Before a future implementation commit, an independent audit must require:

1. exact baseline hashes from Section 6;
2. tests written before source changes;
3. exactly the five reserved paths changed;
4. `py_compile` PASS for both source files and focused tests;
5. focused candidate, continuity, resolver, and Inducement suites PASS with
   cache disabled;
6. full public suite PASS with cache disabled;
7. deterministic public proof of legacy object/identity equality;
8. no private root access and no private output;
9. no OOS, feature/label, training, integration, execution, or trading path;
10. staged diff containing exactly the five reserved paths; and
11. a checkpoint recording contracts, hashes, tests, and non-authority.

Test temp roots must be task-owned, verified inside the repository, and removed
afterward. Pre-existing unrelated untracked files remain untouched.

## 16. Permanent non-authority boundary

The frontier bundle and additive continuity objects are diagnostic structural
evidence only. They may not:

- reopen or promote Phase A;
- modify the canonical control;
- enter a dataset or pretraining corpus;
- become a feature, label, target, score, or model input;
- expose or influence final OOS;
- authorize training, integration, prediction, backtesting, risk, execution,
  orders, or trading; or
- grant a future private run implicitly.

Any later private resolver transaction requires a separately committed and
pushed exact private-run proposal plus separate exact execution authorization.

## 17. Authorization and sequencing

This proposal may be staged and committed locally only after a cached audit
proves it is the sole staged path. Remote push requires separate informed
GitHub privacy/export authorization.

Implementation requires a later explicit authorization naming the pushed
proposal commit. General continuation language does not authorize source/test
changes under this proposal. Implementation must be test-first, remain inside
the five reserved paths, end at a local commit, and STOP before push or private
execution.
