# GC Futures Phase A Structural Seed Evidence Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `GC-FUTURES-PHASE-A-STRUCTURAL-SEED-CHECKPOINT-2026-08-09`.
- Governing proposal:
  `docs/gc_futures_phase_a_structural_seed_evidence_change_proposal.md`.
- Governing proposal commit:
  `42b45fc9d983798d994753edddf2acf1a8ed3bb8`.
- Governing proposal SHA-256:
  `04DEF7C51D884CC64B9C3B89AD3A41492AAE53371B0DE937B7AAAEE4633E6A1E`.
- Cross-audited downstream proposal SHA-256:
  `A0E35BF5A7F4EC451DF7898223FA0467C3FA36AA2F775008C0FB7C4D62F38941`.
- Structural-seed version: `GC-STRUCTURAL-SEED-V1`.
- Task classification: bounded offline structural evidence derivation.
- Private-data execution: `NOT_PERFORMED`.
- Training and OOS opening: `NOT_STARTED` and `NOT_AUTHORIZED`.
- Strategy, execution, and integration: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three paths are in scope:

- `analysis/gc_structural_seed_evidence.py`;
- `tests/test_gc_structural_seed_evidence.py`;
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`.

No external fixture, private output, market-data file, calendar file, generated
dataset, candidate-evidence output, feature/label output, model, training
artifact, package export, configuration, runtime, risk, execution, trace, or
integration file was created or changed.

Pre-existing untracked paths outside this task remained untouched.

## 3. Locked Dependency Evidence

The implementation uses only the accepted immutable public dependency surface.
The final dependency hashes match the proposal exactly:

- `analysis/gc_dataset_builder.py`:
  `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121`;
- `analysis/gc_feature_label_builder.py`:
  `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`;
- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`;
- `smc/equal_liquidity.py`:
  `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`;
- `smc/dealing_range.py`:
  `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`;
- `smc/fair_value_gap.py`:
  `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`.

Legacy `smc.market_structure`, `smc.bos_choch`, runtime context, execution,
training, network, and filesystem-output imports are absent.

## 4. Test-First Correction Evidence

The existing untracked implementation was audited against the corrected
proposal before promotion. The first focused baseline produced
`61 passed, 1 failed`: Case 30 still expected a fabricated raw structural
`AMBIGUOUS` result even though the corrected proposal makes that branch
unreachable.

The test was corrected first to require:

- pathological raw bars resolve to `UNKNOWN` or `INVALID`, never a synthetic
  candidate-selection ambiguity;
- upstream `GCDatasetBuildStatus.AMBIGUOUS` still maps exactly to
  `DATASET_AMBIGUOUS`;
- the private `_StructuralAmbiguous` branch and obsolete
  `OPPOSING_STRUCTURE_EVENTS` token are absent;
- strictly later complete-segment extension preserves foreign swing/event/link
  semantics while dataset-bound source digest, displacement identity, and seed
  identity deterministically rebind.

That test failed RED against the stale source. The source was then corrected
inside the exact scope, after which the focused suite passed.

## 5. Immutable Dataset and Segment Boundary

The analyzer accepts only caller-supplied frozen `GCDatasetBuildConfig` and
`GCDatasetBuildResult` values. It validates the dataset identity, manifest,
source evidence, ordered segments, segment-local zero-based indices, closed-bar
state, timezone-data version, and sealed OOS boundary before deriving evidence.

Swing, structure-event, and FVG discovery resets at every accepted segment.
No lookback, confirmation, active structural state, event provenance, FVG
formation, or identity qualification crosses a segment boundary. OOS segments
cannot create development evidence.

## 6. Structural Discovery and Identity Contract

The implementation locks exact two-left/two-right strict swing discovery,
integer prominence with LOW tie selection, second-right first-known semantics,
and one mirrored Equal Liquidity/Dealing Range swing pair using the public Equal
Liquidity SWING identity.

Only confirmed strictly prior swings can be broken. Bullish and bearish
close-through require the exact one-tick rule. Crossed levels retire atomically;
BOS/CHOCH selection is deterministic and fail-closed when protected state is
unavailable. Public Dealing Range EVENT identities are recomputed from exact
singleton provenance and the selected broken swing.

Raw derivation has no reachable independent `AMBIGUOUS` branch. Contradictory
opposing raw breaks are invalid evidence; upstream dataset ambiguity remains a
pass-through status.

## 7. FVG and Opaque Displacement Boundary

Qualifying FVG evidence uses an exact contiguous three-bar same-segment source,
two-tick minimum gap, and integer `body/range >= 0.60` rule. Event and FVG
sequences end at the same confirmation moment and the singleton event sequence
is the exact positional suffix of the FVG sequence.

The deterministic `DISPLACEMENT` identity binds the normalized scope, accepted
dataset identity, ordered source digest, segment, direction, exact source
moments, boundaries, and canonical Structure Event ID. It is opaque local
formation metadata and does not claim unavailable foreign displacement proof.

## 8. Exact Public Surface

The module exports exactly these eight names:

- `GC_STRUCTURAL_SEED_VERSION`;
- `GCStructuralSeedIdentityKind`;
- `GCStructuralSeedConfig`;
- `GCCanonicalSeedEvidence`;
- `GCStructuralSeedResult`;
- `make_gc_structural_seed_id`;
- `build_gc_structural_seed_evidence`;
- `validate_gc_structural_seed_evidence`.

All three public functions are exact keyword-only APIs. Every public dataclass
is frozen with the locked field order, annotations, defaults, and immutable
tuple members. No package re-export or mutable default was added.

## 9. Deterministic Identity Schemas

`make_gc_structural_seed_id()` implements exhaustive `DISPLACEMENT` and `SEED`
required/forbidden schemas. It validates normalized instrument/timeframe,
positive exact Decimal tick size, dataset and source hashes, exact version and
config, source moments, geometry, segment evidence pair shape, duplicate
segments, and nested values without leaking library exceptions.

Supplied `SEED` segment-digest order is identity-bearing and never silently
sorted. Dataset-aware build and validation operations reconstruct that tuple in
the accepted dataset's exact segment order and require object-equal canonical
evidence rather than hash-shape or partial-field acceptance.

## 10. Status, Atomicity, and Prefix Invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Invalid, ambiguous, and unknown results contain no partial seed and have
`blocking_reasons == reasons`. A valid dataset with no selected member returns
a canonical empty seed and `NONE`; dataset status `NONE` has no seed because it
has no identity scope.

Promotion is atomic at complete bar groups and final seed construction. A
failing group promotes nothing from that group or later groups. Strictly later
complete-segment rebuilds preserve prior foreign facts and link semantics while
dataset-bound digest, displacement, and seed identities rebind. Historical
mutation, same-segment insertion, reorder, repair, or dependency/config drift is
not prefix-equivalent.

## 11. Exact 48-Case Matrix Reconciliation

The focused module covers exact sequential logical Cases 1 through 48. There
are `51` named test functions because Cases 42, 44, and 47 contain separately
named locked subcases; parameterization expands total collected executions to
`62` without changing the exact 48 logical-case set.

Coverage includes immutable inputs, segment order, cross-segment prohibition,
both swing sides, prominence ties, public swing/event identities, one-tick
breaks, retirement, BOS/CHOCH state, raw ambiguity prohibition, upstream
ambiguity pass-through, bullish/bearish FVGs, near misses, source suffix binding,
opaque displacement, digest sensitivity, exhaustive identity schemas, exact
API/defaults/exports, frozen dataclasses, status precedence, nested exception
containment, repeatability, dataset-bound rebasing, and downstream
segment-qualification compatibility.

## 12. Focused and Full Regression Evidence

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_structural_seed_evidence.py`;
- result: `62 passed in 1.06s`;
- exact logical cases: `48`;
- collected focused executions: `62`.

The first full-suite attempt reached test setup but the sandbox denied pytest's
default shared temporary root. This was an environment-only setup failure, not
a source or assertion failure. The suite was rerun with an isolated workspace
temporary root and that temporary directory was removed immediately afterward.

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-structural-seed`;
- result: `2218 passed in 13.73s`;
- committed pre-task baseline: `2156 passed`;
- net new collected executions: `62`.

## 13. Artifact Evidence

- `analysis/gc_structural_seed_evidence.py`
  - SHA-256:
    `B799EE739ECE289A57680007D85566645EE1615B0E20F87C99A4278217AE9AAE`;
  - bytes: `43375`;
  - physical lines: `958`.
- `tests/test_gc_structural_seed_evidence.py`
  - SHA-256:
    `CFD789AE272B621EC04CC463A5EE506C22B3221A3F18EA6C737999042420958E`;
  - bytes: `29831`;
  - physical lines: `625`.
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`
  - SHA-256: self-referential and intentionally not embedded;
  - byte and physical-line counts are reported by final external audit.

All three artifacts must be UTF-8 without BOM, use LF line endings, contain no
tabs or trailing whitespace, and pass exact-scope diff checking before staging.

## 14. Promotion, Rollback, and Stop State

This checkpoint does not authorize private execution, candidate-evidence
generation, feature/label execution, training, model fitting, OOS access,
strategy selection, backtest promotion, paper/live trading, or integration.

Promotion requires a fresh independent code, test, scope, hash, checkpoint, and
diff audit. Before commit, rollback is deletion of only the three new task
artifacts. After a later commit, rollback must use a bounded revert; history
rewriting is forbidden.

Stop immediately on scope expansion, dependency hash drift, dataset mutation,
cross-segment state, silent sorting, identity mismatch, nondeterminism, test
failure, private-data access, OOS contact, training, strategy/risk/execution
authority, integration wiring, or any attempt to call the downstream
feature/label builder before its separately documented segment-order correction.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`;
- `EXACT_AUTHORIZED_PATHS=3`;
- `LOGICAL_CASES=48`;
- `FOCUSED_TESTS=62`;
- `FULL_REGRESSION_TESTS=2218`;
- `PRIVATE_RUN_PERFORMED=False`;
- `TRAINING_STARTED=False`;
- `INTEGRATION_STARTED=False`.
