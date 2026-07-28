# SMC V2 Fair Value Gap Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-FAIR-VALUE-GAP-IMPLEMENTATION-CHECKPOINT-2026-07-27`.
- Parent decision ID:
  `SMC-V2-FAIR-VALUE-GAP-FREEZE-LIFT-DECISION-2026-07-27`.
- Implementation parent commit:
  `8f9f5cec99c6a28e59ec69d2bbf11774509bc6c4`.
- Formal decision record SHA-256:
  `6B88A4E94EB6F063D0206765A55A36A6A9FB1E997D9DBE3FB7D58A823E403065`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/fair_value_gap.py`
- `tests/test_fair_value_gap.py`
- `docs/smc_v2_fair_value_gap_checkpoint.md`

No external fixture was created. Every task-specific synthetic fixture is inline
in the dedicated test module. No existing Python, test, fixture, configuration,
package initializer, documentation, runtime, strategy, risk, or execution file
was changed.

## 3. Test-First Evidence

The complete dedicated test module was created before the production module. The
first focused collection failed with the expected red-phase error:

- `ModuleNotFoundError: No module named 'smc.fair_value_gap'`

No Fair Value Gap production behavior existed when that result was captured.
The standalone module was then implemented against the locked numbered matrix.

The first green attempt produced:

- `2 failed, 62 passed in 0.61s`

Both failures exposed synthetic-test contradictions rather than production
defects:

- the Case 34 middle candle had a zero real body and therefore correctly failed
  the locked `0.60` displacement-ratio rule before the intended context-link
  ambiguity assertion, and
- the Case 40 source scan matched the word `execution` in the module safety
  docstring rather than an executable import or integration dependency.

Only those test fixtures/assertions were corrected. No detector, identity,
lifecycle, fail-closed, or public API rule was weakened.

The first independent final audit subsequently confirmed the implementation
semantics and all existing test results, but correctly stopped staging because
several compound sub-requirements inside locked Cases 27, 33, and 35 through 39
were not yet explicit assertions. Coverage was added test-first without changing
the exact 40-case logical count:

- old-effective context-link evidence is explicitly ineligible as a
  strictly-later prefix extension,
- causally out-of-order and non-tuple context-link collections fail closed,
- GAP, TRANSITION, and SNAPSHOT identity dimensions and exhaustive
  required/forbidden schemas are exercised,
- impossible lifecycle edges, exact reason tokens, ordered transition history,
  final state, effective moment, exact builder names/defaults, frozen public
  dataclasses, malformed hashes, and nested identity inputs are checked, and
- same-effective append ineligibility, deterministic multi-gap ordering, and
  `INVALID` precedence over an otherwise ambiguous group are explicit.

The first focused run after adding those assertions passed directly:

- `66 passed in 0.56s`

This established that the independent finding was a test/checkpoint evidence gap
rather than a production-source defect. `smc/fair_value_gap.py` therefore
remained byte-identical.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `FAIR_VALUE_GAP_DETECTOR_VERSION`
- `FairValueGapState`
- `FairValueGapCandle`
- `FairValueGapContextLink`
- `FairValueGap`
- `FairValueGapTransition`
- `FairValueGapSnapshot`
- `FairValueGapResult`
- `make_fair_value_gap_id`
- `analyze_fair_value_gaps`

Both public functions are keyword-only and exactly match the formal decision
record. Every public data model is frozen. Version 1 contains no public config,
runtime registration, or integration entry point.

## 5. Immutable Input and Fail-Closed Contracts

The analyzer consumes only:

- immutable fully closed integer-tick `FairValueGapCandle` tuples, and
- immutable caller-supplied `FairValueGapContextLink` tuples.

Implemented fail-closed behavior includes:

- missing top-level candle context returns `UNKNOWN`,
- complete empty candle context returns `NONE`,
- malformed present context returns `INVALID`,
- candle indices and normalized timestamps are independently strictly
  increasing and unique,
- booleans and floats are rejected where exact integer ticks or indices are
  required,
- OHLC relationships and closed-candle provenance are validated,
- malformed context links, dangling formation references, duplicate links,
  contradictory links, timestamps, enums, or required fields do not leak nested
  exceptions, and
- supplied tuples are never silently sorted, deduplicated, repaired, coerced, or
  backfilled.

Strictly earlier immutable gaps, transitions, and snapshots remain available
when a determinable later same-index group fails. Nothing from the failing group
or any later input is promoted.

## 6. Exact Three-Candle Detection

- A bullish gap forms only when candle 3 low is at least two ticks above candle
  1 high.
- A bearish gap forms only when candle 3 high is at least two ticks below candle
  1 low.
- A one-tick separation or overlap does not form a gap.
- The middle candle must satisfy
  `5 * abs(close_tick - open_tick) >= 3 * (high_tick - low_tick)`.
- The ratio uses exact integer cross multiplication and does not use float
  rounding.
- A zero-range middle candle is not eligible.
- Formation first-known index and timestamp are exactly candle 3 close.
- Direction and immutable lower and upper boundaries are fixed at formation.
- Multiple independently valid formations at one candle are retained in
  deterministic identity order rather than silently discarded.

## 7. Exact Consequent Encroachment

Consequent encroachment is the exact midpoint of immutable integer-tick
boundaries:

- even spans serialize as an exact integer `.0`,
- odd spans serialize as an exact half tick `.5`,
- signed zero canonicalizes to `0.0`, and
- arbitrary-magnitude positive and negative ticks remain independent of active
  Decimal-context precision.

No binary float arithmetic, tick rounding, mutable recalculation, or later
boundary rewriting is used.

## 8. Formation and Lifecycle Semantics

The exact lifecycle is:

- `ACTIVE`
- `TOUCHED`
- `PARTIALLY_FILLED`
- `MIDPOINT_FILLED`
- `FULLY_FILLED`
- `INVALIDATED`

Formation candles cannot touch, fill, midpoint-fill, fully fill, or invalidate
their own gap. Lifecycle evaluation starts only with strictly later candles.

For a bullish gap, progress is measured downward from the upper boundary; for a
bearish gap, progress is measured upward from the lower boundary. Exact
consequent-encroachment contact produces `MIDPOINT_FILLED`, and exact far-boundary
contact produces `FULLY_FILLED`.

A strict close through the far boundary produces `INVALIDATED`. When fill and
strict close-through invalidation occur on the same closed candle, invalidation
has precedence and exactly one terminal transition is emitted. Terminal states
never transition again. There is no default time, bar-count, or session expiry.

## 9. Optional Formation-Time Linkage

Optional displacement, BOS, and CHOCH metadata is accepted only through a
canonical `FairValueGapContextLink` whose formation end index and normalized
timestamp exactly match the gap's formation close.

- Linkage is immutable formation-time metadata.
- Missing optional linkage does not invalidate an otherwise valid gap.
- A later link cannot retroactively enrich an earlier gap.
- An exact duplicate link is invalid supplied evidence.
- Distinct valid links for one formation are `AMBIGUOUS`.
- Structure-event type is constrained to the locked BOS/CHOCH enum domain.
- No linked identifier is treated as a trade signal or execution authority.

## 10. Same-Index Atomic Processing and Chronology

Each effective candle group is processed atomically:

1. validate the complete closed-candle and applicable link group,
2. apply terminal close-through invalidations,
3. apply remaining non-terminal fill-state progress,
4. detect new three-candle formations,
5. bind formation-time optional metadata, and
6. emit immutable transitions and snapshots in canonical identity order.

Malformed or ambiguous same-index evidence promotes no gap, transition, or
snapshot from that group. Strictly prior valid output remains immutable. Caller
order is validated rather than silently sorted.

## 11. Deterministic Identity Contract

The exact identity kinds are:

- `GAP`
- `TRANSITION`
- `SNAPSHOT`

Every builder parameter is enforced as required or forbidden per identity kind.
Instrument and timeframe normalization is exactly `value.strip().upper()`.
Canonical payloads use sorted-key compact ASCII JSON, detector version, lowercase
SHA-256, UTC timestamps serialized as `YYYY-MM-DDTHH:MM:SS.ffffffZ`, and exact
Decimal `.0` or `.5` consequent-encroachment serialization.

GAP identity binds immutable direction, three formation indices, first-known
formation close, boundaries, consequent encroachment, and optional formation-time
metadata. TRANSITION identity binds gap lineage, prior and next states, effective
closed candle, and an exact locked reason token. SNAPSHOT identity binds the
current immutable gap state and the ordered transition-ID history.

Equivalent timezone representations and repeated valid input produce identical
identities. Unknown kinds, extra parameters, missing parameters, invalid reason
tokens, inconsistent state chains, or identity mismatches fail closed.

## 12. Prefix Invariance and Evidence Preservation

Repeated analysis of identical immutable inputs is dataclass-equal. A valid
prefix ending at a complete effective-group boundary remains byte-for-byte equal
when strictly later valid evidence is appended.

Later evidence may append transitions, snapshots, new gaps, or terminal states.
It cannot rewrite formation boundaries, first-known provenance, consequent
encroachment, metadata, prior lifecycle state, or prior identities. A later
invalid or ambiguous group preserves strictly earlier output while promoting
nothing from that group or after it.

## 13. Exact Logical Test Matrix Reconciliation

The dedicated module contains exactly `40` distinctly numbered logical cases.
Parameterization expands them to `66` collected focused tests.

Coverage includes:

- bullish and bearish detection, exact two-tick threshold, one-tick rejection,
  overlapping candles, and exact `0.60` displacement ratio,
- fully closed OHLC validation, malformed nested values, no silent sorting,
  independently ordered indices and timestamps, missing and empty context,
- formation-close first-known provenance, immutable boundaries, exact integer
  and half-tick consequent encroachment, negative and arbitrary-magnitude ticks,
- formation-candle non-fill behavior and every lifecycle state,
- bullish and bearish touch, partial fill, midpoint fill, full fill, strict
  close-through invalidation, same-candle invalidation precedence, terminal
  immutability, and no expiry,
- absent, valid, dangling, duplicate, contradictory, BOS, and CHOCH optional
  context links with no retroactive enrichment, explicit old-effective
  prefix-extension ineligibility, causal-order rejection, and non-tuple
  collection rejection,
- same-index multi-gap atomic processing, ambiguity, deterministic ordering,
  immutable prior-evidence preservation, and complete-group prefix invariance,
- exhaustive GAP, TRANSITION, and SNAPSHOT identity schemas, every required and
  forbidden field, impossible lifecycle edges, exact reason tokens, transition
  order, final-state and effective-moment sensitivity, timezone equivalence,
  normalization, signed-zero canonicalization, and public cross-object identity
  reconciliation,
- exact frozen dataclass fields, enum values, keyword-only signatures, exports,
  exact identity-builder names and defaults, repeatability, malformed hashes,
  and nested exception containment,
- same-effective append ineligibility, deterministic multi-gap ordering, and
  `INVALID` precedence over otherwise ambiguous same-group evidence, and
- forbidden dependency, integration, file-loading, network, broker, execution,
  and external-fixture checks.

## 14. Test Results

Focused command:

`venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_fair_value_gap.py`

Focused result: `66 passed in 0.56s`.

Full regression command:

`venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider`

The first sandboxed exact-command attempt encountered only Windows pytest
temp-root permission setup errors:

- `1066 passed, 173 errors in 38.15s`

All 173 errors were `PermissionError [WinError 5]` while pytest attempted to use
`C:\Users\hosoo\AppData\Local\Temp\pytest-of-hosoo`; they occurred during fixture
setup rather than application assertions. The identical command was rerun with
normal Windows temp access, bytecode disabled, and pytest cache disabled.

Full regression result: `1241 passed in 8.74s`.

## 15. Locked Artifact and Dependency Identities

Physical line counts include blank physical lines.

- `smc/fair_value_gap.py`
  - bytes: `44420`
  - physical lines: `1331`
  - SHA-256:
    `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`
- `tests/test_fair_value_gap.py`
  - bytes: `43034`
  - physical lines: `1424`
  - SHA-256:
    `5476A7D88E342890C3E2D2A403785DEBE961260DE6B53488842F80A33389DE22`

Frozen dependency and adjacent-capability identities remained unchanged:

- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `smc/dealing_range.py`:
  `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `smc/liquidity_map.py`:
  `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`
- `smc/premium_discount.py`:
  `DC137E0FD66699E6B09A676DB63C17CF2F7AFB6BEC9EE5E01C53580902BC11A8`

## 16. Isolation, Rollback, and Next Gate

- No import or edit connects the new module to current runtime paths.
- No package export, registration, config, CLI, main, strategy, decision, risk,
  backtest, report, trace, or execution path changed.
- No pandas, raw OHLC file-loading, v1 SMC, network, broker, credential, account,
  private data, candidate data, or OOS evidence dependency was added.
- No external fixture, staging, commit, push, integration, paper progression,
  live progression, broker access, or real execution was performed.

The bounded implementation is complete only as a standalone diagnostic candidate
pending independent final code, test, scope, hash, checkpoint, and diff audit.

Rollback before commit remains limited to the exact three new paths and requires
explicit instruction before destructive removal. Any need for another project
path, external fixture, dependency amendment, integration, public API change,
matrix reduction, lifecycle weakening, or failing regression is a stop condition
rather than authorization to expand scope.

- `EXACT_THREE_PATH_SCOPE_PASS=True`
- `TEST_FIRST_EVIDENCE_PASS=True`
- `LOCKED_40_CASE_MATRIX_PASS=True`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_TOTAL=66`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_TOTAL=1241`
- `EXTERNAL_FIXTURE_CREATED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE_OUTSIDE_TASK=True`
