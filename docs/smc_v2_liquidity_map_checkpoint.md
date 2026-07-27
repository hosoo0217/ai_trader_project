# SMC V2 Internal and External Liquidity Map Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-LIQUIDITY-MAP-IMPLEMENTATION-CHECKPOINT-2026-07-20`.
- Parent decision ID:
  `SMC-V2-LIQUIDITY-MAP-FREEZE-LIFT-DECISION-2026-07-20`.
- Implementation parent commit:
  `a7958746ebedabff38093c8fd88cc8d8b6b57faf`.
- Formal decision record SHA-256:
  `EB47FBA188618B1A0E88129736D255C45678B9C26ABA9941FE9775ABF8C20B7F`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/liquidity_map.py`
- `tests/test_liquidity_map.py`
- `docs/smc_v2_liquidity_map_checkpoint.md`

No external fixture was created. Every task-specific synthetic fixture is inline
in the dedicated test module. No existing Python, test, fixture, configuration,
package initializer, documentation, runtime, strategy, risk, or execution file
was changed.

## 3. Test-First Evidence

The dedicated test module was created before the production module. The first
focused collection failed with the expected red-phase error:

- `ModuleNotFoundError: No module named 'smc.liquidity_map'`

No Liquidity Map production behavior existed when that result was captured. The
standalone module was then implemented against the locked numbered matrix.

One focused fixture correction was required after implementation: upstream Equal
Liquidity analysis exposes the final current pool snapshot, while Case 27 must
exercise an immutable tuple containing two same-effective snapshots of one
lineage. The test was corrected to construct both canonical immutable upstream
snapshots directly. Production semantics were not weakened or changed for this
fixture correction.

The independent final audit then found two fail-closed gaps before staging:

- a lone initial or replacement `ACTIVE` range could claim an effective moment
  later than its `None -> ACTIVE` construction transition, and
- the non-protected target source of an external range was not reconciled to the
  direction-specific target swing side.

Correction tests were added first within the existing numbered matrix. The
focused red phase produced exactly the expected result:

- `5 failed, 52 passed in 0.85s`

Those failures covered the lone initial mismatch, both bullish and bearish
target-role conflicts, and both late replacement directions. The source
validators were then corrected without changing the public API or identity
payloads.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `LIQUIDITY_MAP_DETECTOR_VERSION`
- `LiquiditySide`
- `LiquidityScope`
- `LiquiditySourceKind`
- `LiquidityClassification`
- `LiquidityReclassification`
- `LiquidityMapSnapshot`
- `LiquidityMapResult`
- `make_liquidity_map_id`
- `analyze_liquidity_map`

Both public functions are keyword-only and exactly match the formal decision
record. Every public data model is frozen. Version 1 contains no public config,
raw detector, runtime registration, or integration entry point.

## 5. Immutable Input and Fail-Closed Contracts

The analyzer consumes only:

- immutable confirmed `DealingRangeSwing` tuples,
- immutable `EqualLiquidityPool` snapshot tuples, and
- immutable `DealingRangeSnapshot` tuples.

Implemented fail-closed behavior includes:

- missing top-level context returns `UNKNOWN`,
- complete empty context returns `NONE`,
- malformed present context returns `INVALID`,
- dangling or cross-source-conflicting identities return `INVALID`,
- an initial or replacement `ACTIVE` range effective moment must exactly equal
  its construction transition moment,
- only a prior supplied same-lineage immutable `ACTIVE` snapshot can establish a
  later transition-less extension,
- bullish external-range non-protected sources must be `HIGH`, and bearish
  external-range non-protected sources must be `LOW`,
- required nested provenance, lifecycle, transition, tick, enum, and identity
  fields do not leak attribute, key, index, decimal, or enum exceptions,
- booleans and floats are rejected where exact integer ticks or indices are
  required, and
- supplied tuples are never silently sorted, repaired, coerced, or backfilled.

Strictly earlier immutable map snapshots remain available when a determinable
later input moment fails. Nothing from the failing effective group is promoted.

## 6. Side, Scope, and Boundary Semantics

- Confirmed High and Equal High evidence maps to `BUY_SIDE`.
- Confirmed Low and Equal Low evidence maps to `SELL_SIDE`.
- Canonical range high and low boundaries are always External.
- A source is Internal only when its entire tick or band is strictly inside the
  active external range.
- Boundary-touching, boundary-crossing, and outside pools are omitted.
- A range-defining swing identity at its matching boundary is External.
- An unrelated same-price swing is never promoted through price equality alone.
- Boundary records and linked swings remain distinct source kinds and do not
  estimate liquidity size.

## 7. Deterministic Effective Ordering

Swing effective moments use confirmation provenance. Equal Liquidity pool
effective moments use the latest member confirmation for `ACTIVE` snapshots and
the later of latest member confirmation or terminal lifecycle evidence for
`SWEPT` or `BROKEN` snapshots. Dealing Range snapshots use their first-known
provenance; terminal snapshots must exactly match their final transition moment.

Input moments are nondecreasing. Same-effective pool membership revisions require
increasing member count and exact prior member/source-index prefix extension;
snapshot hashes are not chronology tie-breakers. Same-effective range reversal
requires old `SUPERSEDED` or `INVALIDATED` evidence before new `ACTIVE` evidence,
in either direction and independently of lineage or snapshot hash order.

An initial or replacement range cannot masquerade as a transition-less
extension: without an earlier supplied snapshot of the same lineage, the
effective moment must equal the construction transition exactly.

Same-index groups are validated atomically. Two unrelated valid active-range
candidates at one effective moment return `AMBIGUOUS` without partial same-index
promotion.

## 8. Identity Contract

The exact identity kinds are:

- `MAP`
- `BOUNDARY`
- `CLASSIFICATION`
- `SNAPSHOT`
- `RECLASSIFICATION`

Every optional parameter is enforced as required or forbidden per identity kind.
Instrument and timeframe normalization is exactly `value.strip().upper()`.
Canonical payloads use sorted-key compact ASCII JSON, UTC timestamps serialized
as `YYYY-MM-DDTHH:MM:SS.ffffffZ`, detector version, and lowercase SHA-256.

Boundary identity is stable by range lineage and side. Classification identity
contains immutable creation context. Snapshot identity contains the current
active-range snapshot plus ordered classification and event-local
reclassification identities. Reclassification accepts only the two locked exact
reason tokens.

## 9. Immutable Classification and Reclassification

History is keyed by `(source_kind, source_id)`. Active range snapshot identity
alone is not a material classification change. If side, scope, source indices,
boundaries, source identity, and range lineage are unchanged, the classification
retains its prior ID, version, creation moment, and creation-context range
snapshot ID.

A material change creates the next version and links the exact prior
classification. Omission followed by re-entry creates a new version. Only swing
scope changes create a reclassification:

- `INTERNAL_TO_EXTERNAL_RANGE_DEFINING`
- `EXTERNAL_TO_INTERNAL_SUBORDINATE`

The top-level reclassification tuple is the ordered union of reclassifications
actually present in emitted map snapshots.

## 10. Snapshot, Replacement, and Prefix Invariance

Each active range snapshot emits two canonical boundaries even without
subordinate sources. Same-lineage transition-less extension preserves map ID and
unchanged protected-boundary classification identity while versioning only
materially changed evidence. Replacement creates a new map ID and boundary
source identities while retaining immutable prior map snapshots.

Repeated analysis is byte-deterministic at the public object level. Appending
valid later evidence preserves the earlier snapshot prefix. A later malformed
input with a determinable effective moment returns `INVALID` while preserving
strictly prior evidence and promoting nothing from the failing group.

## 11. Exact Logical Test Matrix Reconciliation

The dedicated module contains exactly `40` distinctly numbered logical cases.
Parameterization expands them to `57` collected focused tests.

Coverage includes:

- both range directions, both liquidity sides, and both scopes,
- boundary identity sensitivity and strict-inside pool-band handling,
- all missing, malformed, dangling, conflict, duplicate, and ordering families,
- initial and replacement construction-moment mismatches in both reversal
  directions,
- bullish and bearish external target-source role conflicts,
- ACTIVE and terminal pool/range lifecycle behavior,
- same-effective pool prefix revisions with decreasing valid snapshot hashes,
- same-index atomicity, both reversal directions, and ambiguity,
- transition-less extension and unchanged-classification reuse,
- replacement, omission, re-entry, and both scope-change directions,
- all five exhaustive required/forbidden identity schemas, side/scope/version
  awareness, exact reason tokens, and equivalent-UTC normalization,
- repeatability, appended-future prefix invariance, and later-invalid evidence
  preservation, and
- frozen public signatures, dataclass fields, immutability, and forbidden
  integration/dependency checks.

## 12. Test Results

Focused command:

`venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_liquidity_map.py`

Focused result: `57 passed in 0.58s`.

Full regression command:

`venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp <Codex-writable-temp-root>/liquidity-map-pytest-temp`

The explicit `--basetemp` isolated pytest-generated temporary files outside the
repository after the default sandbox temp location produced environment-only
permission setup errors. No test assertion failed in that interrupted attempt.

Full regression result: `1118 passed in 8.87s`.

## 13. Locked Artifact Identities

Physical line counts include blank physical lines.

- `smc/liquidity_map.py`
  - bytes: `68509`
  - physical lines: `1677`
  - SHA-256:
    `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`
- `tests/test_liquidity_map.py`
  - bytes: `58655`
  - physical lines: `1616`
  - SHA-256:
    `16EC3414C037938C353F6E421FC3D024F50F9EE93DA8C7BE616D781721935DFA`

Frozen direct dependency identities remained unchanged:

- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `smc/equal_liquidity.py`:
  `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`
- `smc/dealing_range.py`:
  `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`

## 14. Isolation and Safety Evidence

- No import or edit connects the new module to current runtime paths.
- No package export, registration, config, CLI, main, strategy, decision, risk,
  backtest, report, or execution path changed.
- No pandas, file-loading, network, broker, credential, account, private data,
  candidate data, or OOS evidence dependency was added.
- Legacy `smc/liquidity_sweep.py` was not read by the implementation and was not
  changed.
- No external fixture, staging, commit, push, paper progression, live
  progression, broker access, or real execution was performed.

## 15. Completion, Rollback, and Next Gate

The bounded implementation is complete only as a standalone diagnostic
candidate pending independent final code, test, scope, hash, checkpoint, and
diff audit.

Rollback before commit remains limited to the exact three new paths and requires
explicit instruction before destructive removal. Any need for another project
path, external fixture, shared dependency amendment, integration, public API
change, matrix reduction, lifecycle weakening, or failing regression is a stop
condition rather than authorization to expand scope.

- `EXACT_THREE_PATH_SCOPE_PASS=True`
- `TEST_FIRST_EVIDENCE_PASS=True`
- `LOCKED_40_CASE_MATRIX_PASS=True`
- `FOCUSED_TESTS_PASS=True`
- `FULL_REGRESSION_PASS=True`
- `EXTERNAL_FIXTURE_CREATED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE_OUTSIDE_TASK=True`
