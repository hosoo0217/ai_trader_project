# SMC V2 Kill-zone Context Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-KILL-ZONE-IMPLEMENTATION-CHECKPOINT-2026-07-28`.
- Formal decision commit:
  `0d42cc1a599521157d3dbf64a3e00148076a0eb9`.
- Formal decision record SHA-256:
  `72D9EA42B464F7C2233C9B7ACA4BFA7BEFD3A5ABADD7E31B7EA3F2B202CFE5BB`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/kill_zones.py`
- `tests/test_kill_zones.py`
- `docs/smc_v2_kill_zone_checkpoint.md`

No external fixture, calendar, holiday, timezone, market-data, or generated file
was created. Synthetic evidence is inline in the dedicated test module. No
existing source, test, fixture, dependency manifest, package initializer,
configuration, runtime, strategy, risk, execution, exporter, or integration file
changed.

## 3. Test-First and Correction Evidence

The exact `44` numbered logical cases were written before the production module.
The first focused collection produced the expected RED phase:

- `ModuleNotFoundError: No module named 'smc.kill_zones'`

After the first production implementation, the focused run produced:

- `79 passed, 1 failed in 0.59s`

The one failure was a test-only lexical false positive: Case 44 treated the word
`risk` in the module's explicit no-risk docstring as if it were a forbidden
import. The test was corrected to inspect the Python AST for actual imports and
file-open calls. No production semantic was relaxed. The next focused run was:

- `80 passed in 0.55s`

A specification self-audit then added fail-closed assertions to existing logical
Cases 10 and 37 without changing the locked case count. The new assertions
proved:

- malformed supplied observation/calendar evidence has `INVALID` precedence
  when runtime timezone context is unavailable;
- `CONTEXT` identity validates fixed-window membership;
- supplied zone and trade date reconcile exactly with the observation's
  `America/New_York` conversion.

The correction RED phase produced:

- `79 passed, 4 failed in 0.70s`

The bounded source correction added validation-only preflight for unavailable
timezone context and exact context observation/zone/trade-date reconciliation.
That audit baseline was:

- `83 passed in 0.50s`
- exactly `44` sequential logical cases
- `39` additional collected tests from locked parameterization

An independent audit then exposed three coverage/semantic gaps without changing
the locked `44`-case matrix:

- a missing top-level tuple returned `UNKNOWN` before validating a malformed
  supplied counterpart;
- public identity construction did not bind its supplied timezone-data version
  to the runtime version used by the timezone database;
- public reflection, identity sensitivity, prefix eligibility, and fall-back
  repeated-hour evidence were incomplete or partly tautological.

Tests were added first. The correction RED phase was:

- `84 passed, 2 failed in 0.71s`

The two failures exactly reproduced the missing-context precedence defect and
the missing builder version reconciliation. The bounded source correction now
validates any supplied counterpart before the missing-tuple `UNKNOWN` result,
and both identity kinds require an available `America/New_York` database plus
an exact normalized runtime timezone-data version match.

The final focused result is:

- `86 passed in 0.64s`
- exactly `44` sequential logical cases
- `42` additional collected tests from locked parameterization

The final full regression result is:

- `1510 passed in 9.46s`

Every focused and full run used `-p no:cacheprovider`.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `KILL_ZONE_DETECTOR_VERSION`
- `KILL_ZONE_TIMEZONE`
- `KillZoneName`
- `KillZoneSessionStatus`
- `KillZoneQuality`
- `KillZoneObservation`
- `KillZoneCalendarEntry`
- `KillZoneContext`
- `KillZoneSnapshot`
- `KillZoneResult`
- `make_kill_zone_id`
- `analyze_kill_zones`

Both functions are keyword-only and match the formal decision. All five public
dataclasses are frozen with the exact locked fields and defaults. No public
configuration, adapter, registry, lifecycle transition, runtime hook, or
integration entry point exists.

## 5. Immutable Input and Time Authority

The analyzer accepts only exact immutable tuples of fully closed
`KillZoneObservation` and versioned `KillZoneCalendarEntry` evidence. Observation
indices and normalized UTC timestamps are independently strictly increasing.
Calendar trade dates are strictly increasing and unique. Boolean indices, naive
timestamps, non-tuples, malformed internal dataclass fields, invalid session
intervals, conflicting versions, and silent sorting fail closed.

The fixed timezone authority is exactly `America/New_York`. The current runtime
provides `tzdata 2026.2`; the caller-supplied normalized timezone-data version
must match it exactly. No fixed UTC offset, machine-local fallback, requirements
edit, timezone file, or external calendar is used. Unavailable reproducible
timezone context returns `UNKNOWN` only after supplied evidence is checked for a
higher-precedence determinable `INVALID` defect.

Missing `observations` or `calendar_entries` likewise returns `UNKNOWN` only
after the supplied counterpart passes deterministic fail-closed validation.
Malformed supplied evidence returns `INVALID` and promotes no context or
snapshot.

## 6. Window and Trade-Date Semantics

The implementation uses database-backed UTC-to-New-York conversion and exact
start-inclusive/end-exclusive windows:

- Asia: `20:00` through local midnight;
- London: `02:00` through `05:00`;
- New York AM: `07:00` through `10:00`;
- New York PM: `13:00` through `16:00`.

Asia uses the following local calendar date as trade date. Other windows retain
their local date. Only Monday through Friday derived dates are eligible. Sunday
Asia may derive Monday; Friday Asia derives Saturday and emits verified closed
context. Winter, summer, spring-forward, fall-back, exact starts, exact ends, and
microsecond near-boundaries are covered with inline synthetic observations.

## 7. Calendar and Session Semantics

`OPEN` and `EARLY_CLOSE` require aware open and close timestamps with a positive
interval no longer than 24 hours and exact New York local-date reconciliation.
`SESSION_CLOSED` requires both timestamps absent. Weekend entries cannot be open.

Open and early-close session bounds are start-inclusive and end-exclusive.
Holiday closure, pre-open, at-close, post-close, and early-close truncation emit
verified `SESSION_CLOSED` context with no active zone. Missing weekday calendar
coverage emits an immutable `CALENDAR_UNVERIFIED` candidate context and returns
`UNKNOWN`; it is never retroactively enriched.

## 8. Context, Snapshot, and Status Semantics

Each fixed-window observation creates zero or one immutable context and, when a
context exists, exactly one immutable complete-history snapshot. Context and
snapshot promote atomically. There is no transition, mutable lifecycle,
reclassification, expiry, direction, bias, score, confidence, signal, filter,
trade action, or execution advice.

Final status precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Version 1 has no reachable valid `AMBIGUOUS` branch. Verified active-zone
evidence may return `VALID`; missing calendar evidence returns `UNKNOWN`; empty,
outside-window, weekend, holiday, or out-of-session complete evidence returns
`NONE` when no higher status applies.

## 9. Deterministic Identities

`make_kill_zone_id` supports exactly `CONTEXT` and `SNAPSHOT`. Both use canonical
UTF-8 JSON, sorted keys, compact separators, normalized uppercase text, exact
enum tokens, UTC microsecond timestamps, ordered tuple history, explicit identity
kind, and lowercase SHA-256.

`CONTEXT` validates every required/forbidden parameter and reconciles quality,
session status, zone, fixed-window membership, trade date, and equivalent UTC
timestamps. `SNAPSHOT` requires an ordered, unique, non-empty lowercase SHA-256
context history and forbids every context-only field. Unknown kinds, malformed
hashes, booleans as indices, invalid dates/enums, naive timestamps, and nested
exceptions expose only `TypeError` or `ValueError`.

Both identity kinds bind the identity-bearing normalized timezone-data version
to the exact normalized runtime version and require the fixed
`America/New_York` database to be available. A mismatch or unavailable runtime
authority creates no identity and fails closed with only `TypeError` or
`ValueError`.

## 10. Chronological Cutoff and Prefix Invariance

A determinably later malformed observation or calendar group returns final
`INVALID`, preserves byte-for-byte contexts and snapshots strictly before the
failing effective group, and promotes nothing at or after that group. An
unknowable effective moment claims no trustworthy prefix.

Repeating identical complete input is byte-stable. A strictly later complete
observation/calendar append preserves every prior context, context ID, snapshot,
and complete-history prefix. Duplicate or same-effective observations,
historical insertion, repair, reorder, version mutation, or partial atomic
groups are not eligible prefix extensions and are never silently normalized.
Strictly later calendar-only extension also preserves prior evidence, while
calendar repair, reverse ordering, and version mutation are explicitly covered
as ineligible or invalid histories.

## 11. Exact Logical Test Matrix

`tests/test_kill_zones.py` retains exact sequential comments:

`Logical case 1` through `Logical case 44`

The matrix covers missing/malformed context, exact input types, ordering,
timezone authority and version failure, all four windows, Asia trade-date
assignment, weekday/weekend behavior, open/closed/early-close sessions, missing
calendar coverage, DST boundaries, non-directional public shape, deterministic
multi-zone ordering, causal cutoff, exhaustive identity schemas, exact public
reflection, repeatability, prefix invariance, atomic snapshots, and forbidden
dependency/import surface.

The final matrix additionally proves malformed-counterpart `INVALID` precedence
over missing top-level `UNKNOWN`; runtime timezone-version/database binding for
both identity kinds; common, context, snapshot, effective-moment, and ordered
history identity sensitivity; exact keyword-only kinds/defaults; exact frozen
dataclass fields, annotations, defaults, enum values, constants, and exports;
and real fall-back repeated-local-hour behavior using two distinct UTC instants,
different offsets/folds, and repeatability.

## 12. Isolation and Regression Evidence

The production module imports only deterministic Python standard-library
utilities and `SMCV2PrimitiveStatus` plus `normalize_utc_timestamp` from
`smc.smc_v2_primitives`. It performs no pandas, CSV, broker, Sierra, external
API, calendar download, config, strategy, risk, execution, package registration,
file, network, or integration work.

The full suite grew from the committed Breaker Block checkpoint's `1424` passing
tests to `1510` passing tests. Existing behavior remained unchanged.

## 13. Artifact Evidence

- `smc/kill_zones.py`
  - SHA-256:
    `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21`
  - bytes: `33894`
  - physical lines: `997`
- `tests/test_kill_zones.py`
  - SHA-256:
    `4D576213BAEB2168B5A68FC369062C9D11B12D6BAAE5995A8BADC51041527636`
  - bytes: `42396`
  - physical lines: `1150`
- `docs/smc_v2_kill_zone_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes and physical lines are reported by the final scope audit

All three artifacts are UTF-8 without BOM, use LF line endings, and contain no
tabs or trailing whitespace.

## 14. Promotion, Rollback, Stop, and Freeze State

This checkpoint does not authorize integration, staging, commit, push, paper
progression, live progression, tuning, or runtime use. Promotion requires an
independent exact-scope code/test/checkpoint audit and a separate explicit
staging instruction.

Before commit, rollback is deletion of exactly the three untracked task
artifacts and requires explicit authorization. After commit, rollback must use a
bounded revert rather than history rewriting. Stop immediately on dependency
drift, scope expansion, timezone/version uncertainty, public API mismatch,
identity nondeterminism, uncontained exception, calendar ambiguity, focused/full
regression failure, or integration request outside a separately approved
freeze-lift decision.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`
- `EXACT_CHANGED_PATHS=3`
- `LOGICAL_CASES=44`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_COLLECTED=86`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=1510`
- `EXTERNAL_FIXTURE_CREATED=False`
- `EXTERNAL_CALENDAR_CREATED=False`
- `REQUIREMENTS_CHANGED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_PERFORMED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`
