# SMC v2 Dealing Range Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `SMC-V2-DEALING-RANGE-IMPLEMENTATION-CHECKPOINT-2026-07-19`.
- Parent decision ID:
  `SMC-V2-DEALING-RANGE-FREEZE-LIFT-DECISION-2026-07-19`.
- Implementation parent commit:
  `a709c3c069725ef80bf1cbe836565e84c063097e`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/dealing_range.py`
- `tests/test_dealing_range.py`
- `docs/smc_v2_dealing_range_checkpoint.md`

The optional `tests/fixtures/dealing_range_cases.json` path remains absent.
All fixtures are obviously synthetic and inline in the dedicated test module.

No existing Python, test, fixture, configuration, package export, documentation,
runtime, strategy, risk, or execution path changed.

## 3. Test-First Evidence

The dedicated test module was created before the production module. The first
focused command failed during collection with the expected error:

- `ModuleNotFoundError: No module named 'smc.dealing_range'`

No production behavior existed when that red-phase result was captured. The
standalone module was then implemented against the locked test matrix.

This correction pass was also test-first: focused tests were expanded to assert
fail-closed malformed-boundary handling, immutable prior-snapshot preservation
under later-index malformed events, and public case-19 protected-identity
rejection before production fixes were applied.

The latest correction remained test-first: new Case-33 parameterized public-API
tests for missing and malformed later required event fields were added first,
then chronological per-event validation flow was updated to preserve immutable
prior evidence while rejecting the failing index as `INVALID`.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `DEALING_RANGE_DETECTOR_VERSION`
- `DealingRangeSwingSide`
- `DealingRangeEventType`
- `DealingRangeKind`
- `DealingRangeState`
- `DealingRangeConfig`
- `DealingRangeSwing`
- `DealingRangeObservation`
- `DealingRangeStructureEvent`
- `DealingRangeTransition`
- `DealingRangeSnapshot`
- `DealingRangeResult`
- `make_dealing_range_id`
- `analyze_dealing_ranges`

Both public functions are keyword-only and match the formal decision record.
Every public model is immutable.

## 5. Deterministic Input and Fail-Closed Behavior

The analyzer consumes only immutable confirmed swings, fully closed integer-tick
observations, caller-supplied confirmed structure events, and the locked config.

Implemented fail-closed rules include:

- top-level missing context returns `UNKNOWN`,
- malformed present context returns `INVALID`,
- dangling `broken_swing_id` returns `INVALID`,
- missing eligible protected context returns `UNKNOWN`,
- wrong, missing, or internally malformed required fields do not leak
  validation exceptions,
- malformed `SMCV2TickRange` required fields in `make_dealing_range_id()` fail
  closed as `TypeError` or `ValueError` (no `AttributeError` leakage),
- boolean and float ticks are rejected,
- observation, swing, provenance, and structure-event chronology is validated,
- event IDs are regenerated and must match, and
- invalid inputs are not silently sorted, repaired, or coerced.

## 6. Deterministic Event Ordering

Structure events are strictly ordered by:

`(confirmation_index, normalized_confirmation_timestamp, direction.value,
event_type.value, event_id)`

Semantic event validation, canonical identity checks, duplicate identity checks,
and strict composite-order checks are enforced during chronological processing
at each confirmation index. Future malformed events therefore do not erase
strictly earlier valid evidence.

The `_validate_events()` prepass is intentionally limited to immutable tuple
input shape, event object type, provenance object type, exact non-negative
`confirmation_index` required for grouping, and caller confirmation-index
nondecreasing order. All other provenance semantics are deferred to
chronological per-event validation.

Same-index groups allow at most one event per direction. Duplicate-direction
groups return `INVALID`. One valid bullish and one valid bearish event return
`AMBIGUOUS`. Group validation occurs before observation or lifecycle mutation,
so no same-index partial snapshot is promoted.

## 7. Protected Swing and Range Construction

The implementation locks:

- `HIGH` and `LOW` confirmed swing sides,
- `BULLISH` and `BEARISH` structure directions,
- `BOS` and `CHOCH` event types,
- exact one-tick close breaks,
- strictly pre-displacement broken and protected swing confirmation,
- deterministic most-recent protected-swing selection,
- inclusive protected-source-through-confirmation external extremes,
- exact integer or half-tick `Decimal` midpoint values, and
- no back-labeling before first-known confirmation.

## 8. Lifecycle and Identity Evidence

The exact external transition graph is implemented:

- `None -> ACTIVE`
- `ACTIVE -> SUPERSEDED`
- `ACTIVE -> INVALIDATED`

The only transition reason tokens are:

- `CONSTRUCTION_ACTIVE`
- `OBSERVATION_CLOSE_THROUGH_INVALIDATION`
- `CHOCH_CLOSE_THROUGH_INVALIDATION`
- `BOS_PULLBACK_REPLACEMENT`

Every transition ID is regenerated before snapshot construction. Transition
lineage, state chain, strict index and timestamp chronology, terminal behavior,
and duplicate identity rejection are checked before a snapshot is emitted.

The five canonical identity kinds are `EVENT`, `TRANSITION`, `LINEAGE`,
`SNAPSHOT`, and `INTERNAL_RANGE`. Instrument and timeframe normalization is
exactly `value.strip().upper()`. Transition timestamps are normalized to UTC and
serialized as `YYYY-MM-DDTHH:MM:SS.ffffffZ`.

## 9. Extension, Replacement, and Reverse CHOCH

Same-direction BOS can extend only the external target while preserving the
protected boundary and lineage. A non-extending event emits no duplicate
snapshot.

A confirmed eligible pullback plus a later BOS emits the old lineage as
`SUPERSEDED` before creating the linked replacement lineage. Pullback alone does
not replace a range.

A valid reverse CHOCH is evaluated against an immutable pre-index active range.
Observation and CHOCH evidence coalesce into exactly one old-lineage
`INVALIDATED` transition before a new reverse range is constructed. If new-range
context is incomplete, the old terminal snapshot remains and the result is
`UNKNOWN` without a partial new range.

## 10. Nested Internal Ranges

Chronologically adjacent opposing confirmed swings may form immutable internal
ranges only when both prices are strictly inside the active external range.
Boundary-equal or outside pairs are excluded. Internal ranges have no external
lineage or lifecycle fields and never replace, extend, invalidate, or relabel
the external range.

## 11. Exact Logical Test Matrix Reconciliation

The dedicated module contains exactly `36` distinctly numbered logical cases.
Parameterization expands them to `55` collected focused tests.

Coverage includes:

- bullish and bearish construction and exact close-break boundaries,
- missing, malformed, dangling, and contradictory input behavior,
- protected-swing timing and deterministic selection,
- inclusive extremes and exact midpoint values,
- all five identity kinds and all four reason tokens,
- normalization and UTC timestamp identity,
- extension, replacement, observation invalidation, and reverse CHOCH,
- same-index composite ordering and atomic ambiguity behavior,
- later-index malformed structure-event failure returning `INVALID` while
  preserving strictly earlier immutable snapshots and promoting nothing from the
  failing index, and
- Case-33 parameterized later-event required-field missing/malformed failures
  (`event_type`, `direction`, `broken_swing_id`, `event_id`) via public
  `analyze_dealing_ranges()` with immutable prior snapshots and no failing-index
  transition or snapshot promotion,
- malformed provenance without a determinable confirmation index remaining
  fail-closed `INVALID` instead of assumed chronological ordering,
- distinct confirmation-index valid event tuples in reverse caller order
  returning upfront `INVALID` with no silent sort/repair,
- later-event provenance required-field missing/malformed failures with valid
  confirmation index (`source_indices`, `source_timestamps`,
  `confirmation_timestamp`) returning `INVALID` while preserving strictly prior
  immutable snapshots and promoting nothing from the failing index,
- public `analyze_dealing_ranges()` verification that duplicate protected
  identities are rejected as `INVALID` with empty ranges (case 19),
- bullish and bearish nested internal ranges,
- repeatability and appended-future prefix invariance, and
- exact API, immutability, and forbidden-dependency checks.

## 12. Test Results

Focused command:

`venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_dealing_range.py`

Focused result: `55 passed in 0.48s`.

Full regression command:

`venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`

Full regression result: `1061 passed in 9.20s`.

## 13. Locked Artifact Identities

Physical line counts below are true physical lines including blank lines,
computed via newline-aware `ReadAllLines` counting (not `Measure-Object -Line`
nonblank counting).

- `smc/dealing_range.py`
  - bytes: `69385`
  - physical lines: `1806`
  - SHA-256:
    `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `tests/test_dealing_range.py`
  - bytes: `43101`
  - physical lines: `1242`
  - SHA-256:
    `A6DD0C03BEA9C6091F8E9EAC267930187C99B8F80C386EC52E2A0D91110B36CF`

## 14. Isolation and Safety Evidence

- No import or edit connects the module to current runtime paths.
- No package export or registration was added.
- No pandas, current structure analyzer, network, file I/O, or configuration
  dependency was added.
- No private, candidate, OOS, account, credential, or generated evidence was
  read or copied.
- No strategy, signal, confidence, risk, execution, or progression behavior
  changed.
- No staging, commit, or push was performed.
- Paper and live progression remain unauthorized.

## 15. Completion and Next Gate

The bounded implementation is complete only as a standalone diagnostic
candidate pending independent final code, test, scope, hash, and diff audit.

Rollback before commit remains limited to the exact three new paths and requires
explicit instruction before destructive removal. Any need for another path,
fixture, shared-primitives amendment, integration, or failing regression is a
stop condition rather than authorization to expand scope.

- `EXACT_THREE_PATH_SCOPE_PASS=True`
- `TEST_FIRST_EVIDENCE_PASS=True`
- `LOCKED_36_CASE_MATRIX_PASS=True`
- `FOCUSED_TESTS_PASS=True`
- `FULL_REGRESSION_PASS=True`
- `OPTIONAL_FIXTURE_CREATED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE_OUTSIDE_TASK=True`
