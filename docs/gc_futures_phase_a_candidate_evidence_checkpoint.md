# GC Futures Phase A Candidate Evidence Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `GC-FUTURES-PHASE-A-CANDIDATE-EVIDENCE-CHECKPOINT-2026-08-09`.
- Governing proposal:
  `docs/gc_futures_phase_a_candidate_evidence_change_proposal.md`.
- Governing proposal commit:
  `42b45fc9d983798d994753edddf2acf1a8ed3bb8`.
- Governing proposal SHA-256:
  `A0E35BF5A7F4EC451DF7898223FA0467C3FA36AA2F775008C0FB7C4D62F38941`.
- Parent implementation baseline:
  `11c38e11c6ca978a7d7af563e1afdf8d24b906df`.
- Candidate-evidence version: `GC-CANDIDATE-EVIDENCE-V1`.
- Task classification: bounded offline reference-only candidate aggregation.
- Private-data execution: `PERFORMED_FAILED_CLOSED`.
- Training and OOS opening: `NOT_STARTED` and `NOT_AUTHORIZED`.
- Strategy, execution, and integration: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three paths are in scope:

- `analysis/gc_candidate_evidence_builder.py`;
- `tests/test_gc_candidate_evidence_builder.py`;
- `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md`.

No external fixture, private output, market-data file, calendar file, generated
dataset, structural-seed output, feature/label output, model, training artifact,
package export, configuration, runtime, risk, execution, trace, or integration
file was created or changed. The accepted private V3 input, dataset, structural
seed, and calendar artifacts were read only for the authorized structural run.
Pre-existing untracked documentation outside this task remained untouched.

## 3. Locked Dependency Evidence

The implementation imports only the accepted immutable public dependency
surface. Unchanged dependency hashes remain bound to the governing proposal.
The Dealing Range and Inducement hashes below bind the separately tested
fail-closed corrections required by the authorized private run. The Dealing
Range correction is committed at
`507b46e436501c4e4b00b17d9b9acf817992158a`; the Inducement correction is
committed at `4064483840426e67e44847200f679e0f9028279b`:

- `analysis/gc_dataset_builder.py`:
  `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121`;
- `analysis/gc_feature_label_builder.py`:
  `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`;
- `core/gc_chronological_backtest.py`:
  `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A`;
- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`;
- `smc/equal_liquidity.py`:
  `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`;
- `smc/dealing_range.py`:
  `F2D6754A7456D39C6BCC5EE312024F8C538CFDBD43474BC76957D44B62EBCE0E`;
- `smc/liquidity_map.py`:
  `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`;
- `smc/fair_value_gap.py`:
  `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`;
- `smc/inducement.py`:
  `D1A3E99A83BB9B6003B8B6682229B9E43F0DE4DDE9A1D02B705D12CF98B7443A`;
- `smc/kill_zones.py`:
  `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21`;
- `analysis/gc_structural_seed_evidence.py`:
  `B799EE739ECE289A57680007D85566645EE1615B0E20F87C99A4278217AE9AAE`;
- `tests/test_gc_structural_seed_evidence.py`:
  `CFD789AE272B621EC04CC463A5EE506C22B3221A3F18EA6C737999042420958E`;
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`:
  `75C0D52D58BF2C8168806893FF68B0F567F19401FFA0DABE3EC0DB8A970094E1`.

Legacy structure modules, runtime context, filesystem output, network,
training, strategy, execution, and downstream feature/label execution imports
are absent.

## 4. Test-First Correction Evidence

The initial expanded focused audit produced `8 failed, 31 passed in 0.93s`.
The RED failures demonstrated that the source still:

- masked determinably malformed calendar evidence behind missing context;
- continued downstream after upstream `UNKNOWN`, `AMBIGUOUS`, or `INVALID`;
- accepted malformed FVG transition/snapshot mirroring;
- accepted map/range and pool-role contradictions; and
- allowed a `BUNDLE` identity with no candidate references.

The source was corrected only after those public tests were locked. A first
GREEN pass reached `39 passed in 0.67s`. Additional semantic and structural
tests then locked exact schemas, API metadata, exception containment,
same-ID fork rejection, duplicate collapse, status precedence, and no-authority
boundaries. The private-run audit then exposed a dependency-boundary defect:
Candidate Evidence passed internal Dealing Range objects and FVGs without a
formation-time `displacement_id` to the public Inducement analyzer even though
those objects are outside the Inducement input contract. A public analyzer-spy
test now locks exact filtering to EXTERNAL ranges and displacement-qualified
FVGs together with only their matching transition/snapshot histories. The
final focused suite passed without relaxing any assertion.

## 5. Immutable Dataset and Seed Boundary

The builder accepts only caller-supplied frozen `GCDatasetBuildConfig`, exact
`GCDatasetBuildResult`, `GCStructuralSeedConfig`, and
`GCStructuralSeedResult` values. Before analyzer execution it validates the
dataset identity and histories, the accepted seed identity and exact segment
evidence, segment-local closed-bar chronology, timezone-data version, and the
sealed OOS boundary.

Missing top-level context never suppresses independently determinable invalid
counterpart evidence. OOS members are rejected before seed or detector
promotion. No private path, serialized approximation, silent repair, sort,
resample, float projection, or cross-segment state is accepted.

## 6. Exact Per-Segment Analyzer Chain

Every accepted segment is projected without information loss and analyzed in
this exact order:

1. Equal Liquidity;
2. Dealing Range;
3. Liquidity Map;
4. Fair Value Gap;
5. Inducement;
6. Kill Zone.

Each detector result must be its exact frozen public result type with a valid
status and immutable nonempty reason tokens. `INVALID`, `AMBIGUOUS`, or
`UNKNOWN` stops that segment and all later processing immediately. Detector
exceptions, wrong result types, malformed reasons, or nested identity failures
are contained as fail-closed `INVALID` results. No later analyzer is called
after a blocked detector.

## 7. Candidate Assembly and Causal Binding

Candidate assembly uses the latest strictly pre-sweep active external range,
an exactly range-bound Liquidity Map, and the direction-mirrored external
target/internal Equal Liquidity pool roles. Classification scope, side, source,
range references, pool lineage, member sides, and boundaries are reconciled
before promotion.

Structure Event and qualifying FVG source moments must exist in the exact
segment observation tuple, end at the same confirmation moment, and satisfy the
locked shorter-sequence positional-suffix relationship. The formation-time
non-null `displacement_id` is preserved as opaque metadata; no unavailable
foreign displacement proof is claimed. Complete FVG transition/snapshot
histories must be one-to-one, causally ordered, and exactly mirrored.

The final reference set binds the confirmed Inducement, its snapshot, the
qualifying Kill Zone context/snapshot, and the exact confirmation bar. It does
not calculate confidence, direction authority, entry, exit, risk, PnL, feature,
label, or strategy decisions.

## 8. Exact Public Surface

The module exports exactly these nine names:

- `GC_CANDIDATE_EVIDENCE_VERSION`;
- `GCCandidateEvidenceIdentityKind`;
- `GCCandidateEvidenceConfig`;
- `GCFeatureLabelCandidateEvidence`;
- `GCSegmentCandidateEvidence`;
- `GCCandidateEvidenceBundle`;
- `GCCandidateEvidenceResult`;
- `make_gc_candidate_evidence_id`;
- `build_gc_candidate_evidence`.

Both public functions are exact keyword-only APIs. Every public dataclass is
frozen with the locked field order, annotations, defaults, and immutable tuple
members. No package re-export or mutable default was added.

## 9. Deterministic Identity Schemas

`make_gc_candidate_evidence_id()` implements exhaustive `CANDIDATE`, `SEGMENT`,
`BUNDLE`, and `MANIFEST` required/forbidden schemas. It validates normalized
instrument/timeframe, positive exact Decimal tick size, dataset and seed hashes,
exact versions/configs, segment order, source references, candidate order,
duplicate segments, duplicate candidates, signed zero, nested canonical values,
and malformed hashes without leaking library exceptions.

Candidate references are identity-bearing and never silently sorted. Exact
duplicates collapse deterministically; byte-different evidence sharing an ID is
an invalid fork. A bundle requires at least one candidate reference, and the
manifest recomputes from the exact accepted bundle and dataset/seed bindings.

## 10. Status, Atomicity, and Prefix Invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

A failing detector or candidate group promotes nothing from that group or any
later group. Strictly prior complete segment evidence remains byte-for-byte
immutable. Same-effective append, partial segment, historical insertion,
reorder, repair, dependency/config mutation, or OOS contact is not eligible for
prefix equivalence. Only strictly later complete accepted segment extension may
preserve the prior reference prefix while dataset-bound bundle and manifest
identities deterministically rebind.

## 11. Exact 48-Case Matrix Reconciliation

The focused module covers exact sequential logical Cases 1 through 48 from the
governing proposal. Parameterization expands the total collected executions to
`53` without changing the exact 48 logical-case set.

Coverage includes immutable inputs, missing-counterpart precedence, dataset and
seed validation, segment-local projections, exact analyzer order, detector
blocking and exception containment, range/map/pool reconciliation, both
directional role mirrors, stale-range rejection, event/FVG observation and
positional-suffix binding, complete FVG histories, opaque displacement,
duplicate collapse, same-ID fork rejection, deterministic selection,
exhaustive four-kind identities, manifest reconstruction, exact API/defaults,
frozen dataclasses, enum values, exports, status precedence, atomicity, prefix
invariance, repeatability, and forbidden downstream authority.

## 12. Focused and Full Regression Evidence

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_candidate_evidence_builder.py`;
- result: `53 passed in 0.96s`;
- exact logical cases: `48`;
- collected focused executions: `53`.

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`;
- result: `2294 passed in 12.54s`;
- committed pre-task baseline: `2218 passed`;
- current net new collected executions: `76`.

Pytest cache creation was disabled for both runs.

## 13. Authorized Private Structural Run Evidence

The authorized read-only V3 run reconstructed the accepted dataset through the
three public Sierra Chart parsers and the public dataset builder, then required
exact object equality with the accepted V3 build result. It also rebuilt and
externally validated the structural seed through the two public structural
operations and required exact object equality with the accepted V3 structural
artifact.

Preflight evidence passed exactly:

- dataset ID:
  `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- seed ID:
  `e741a230d961cda290f5d20d4fd5a0b4b1bd2cb54795c1d0c009a2e17148e8f0`;
- canonical segments: `54`;
- development bars: `7103`;
- OOS bars opened: `0`;
- private Candidate output written: `False`.

The Candidate result failed closed:

- status: `UNKNOWN`;
- exact reason and blocking reason:
  `initial CHOCH lacks prior external range context`;
- completed segment results: `1` of `54`;
- candidates: `0`;
- manifest and bundle: `None`;
- measured analyzer time on the reporting retry: `0.941354s`.

This is consistent with the locked boundaries rather than a source exception.
The first accepted segment starts with CHOCH evidence but has no prior external
range inside that segment. Dealing Range correctly returns `UNKNOWN`, while the
Candidate proposal forbids carrying range state across segment boundaries and
requires any analyzer `UNKNOWN` to stop all later segments. Inventing or
backfilling prior context would violate no-look-ahead and segment isolation.

The initial reporting wrapper completed the analyzer call but then referenced
a nonexistent convenience field named `candidate_id`; no output was written.
The corrected read-only reporting retry used the public
`manifest.manifest_id` field and produced the evidence above. This operational
retry is disclosed and no accepted private run is claimed.

## 14. Artifact Evidence

- `analysis/gc_candidate_evidence_builder.py`
  - SHA-256:
    `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F`;
  - bytes: `50867`;
  - physical lines: `1202`.
- `tests/test_gc_candidate_evidence_builder.py`
  - SHA-256:
    `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F`;
  - bytes: `41189`;
  - physical lines: `1159`.
- `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md`
  - SHA-256: self-referential and intentionally not embedded;
  - byte and physical-line counts are reported by final external audit.

All three artifacts must be UTF-8 without BOM, use LF line endings, contain no
tabs or trailing whitespace, and pass exact-scope diff checking before staging.

## 15. Promotion, Rollback, and Stop State

The authorized private structural execution is complete and failed closed. This
checkpoint does not authorize another private execution, feature/label
execution, training, model fitting, OOS access, strategy selection, backtest
promotion, paper/live trading, or integration.

Promotion is currently blocked by the failed private result. Any future
corrected outcome would still require exact three-path cached-content audit and
local commit preflight. Before commit, rollback is deletion of only the three
new task artifacts. After commit, rollback must use a bounded revert; history
rewriting is forbidden.

Stop immediately on scope expansion, dependency hash drift, private-data
access, dataset/seed mutation, cross-segment state, silent sorting, identity
mismatch, nondeterminism, test failure, OOS contact, training,
strategy/risk/execution authority, integration wiring, or any downstream
feature/label builder call.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_COMMIT=False`;
- `EXACT_AUTHORIZED_PATHS=3`;
- `LOGICAL_CASES=48`;
- `FOCUSED_TESTS=53`;
- `FULL_REGRESSION_TESTS=2294`;
- `PRIVATE_RUN_PERFORMED=True`;
- `PRIVATE_RUN_ACCEPTED=False`;
- `PRIVATE_OUTPUT_WRITTEN=False`;
- `OOS_BARS_OPENED=0`;
- `TRAINING_STARTED=False`;
- `INTEGRATION_STARTED=False`.
