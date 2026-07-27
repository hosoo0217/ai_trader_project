# SMC V2 Premium, Equilibrium, and Discount Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-PREMIUM-DISCOUNT-IMPLEMENTATION-CHECKPOINT-2026-07-27`.
- Parent decision ID:
  `SMC-V2-PREMIUM-DISCOUNT-FREEZE-LIFT-DECISION-2026-07-27`.
- Implementation parent commit:
  `f103453dad72f16188243e4c8eea52061e663ee8`.
- Formal decision record SHA-256:
  `1406C9979FA040DF4A065131B48B7D444D8C1D7B49896C7CB2743AC905904DB5`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/premium_discount.py`
- `tests/test_premium_discount.py`
- `docs/smc_v2_premium_discount_checkpoint.md`

No external fixture was created. Every task-specific synthetic fixture is inline
in the dedicated test module. No existing Python, test, fixture, configuration,
package initializer, documentation, runtime, strategy, risk, or execution file
was changed.

## 3. Test-First Evidence

The complete dedicated test module was created before the production module. The
first focused collection failed with the expected red-phase error:

- `ModuleNotFoundError: No module named 'smc.premium_discount'`

No Premium/Discount production behavior existed when that result was captured.
The standalone module was then implemented against the locked numbered matrix.

The first green attempt produced:

- `2 failed, 55 passed in 0.71s`

Both failures exposed one synthetic-fixture contradiction rather than a
production defect. A byte-identical repeated canonical Dealing Range snapshot
necessarily has the same `snapshot_id`, while the locked duplicate-snapshot rule
requires such duplicate supplied evidence to be `INVALID`. Cases 19 and 21 were
corrected without weakening that rule:

- unchanged zone-set reuse is exercised across later observations under one
  canonical active snapshot, and
- material source-evidence change is exercised independently and creates the next
  version.

A subsequent manual semantic pass found one implementation gap before checkpoint
creation. The locked matrix requires a canonical terminal-only Dealing Range
snapshot to be valid historical input returning `NONE`; the first implementation
incorrectly required a separately supplied earlier ACTIVE snapshot. The public
test was tightened first and produced:

- `1 failed, 56 passed in 0.70s`

The analyzer was then corrected to accept a self-contained canonical terminal
history while still rejecting a second contradictory terminal transition after
an already terminated supplied lineage.

The independent final audit then found two additional fail-closed gaps before
staging:

- a canonical `SUPERSEDED` snapshot could identify one replacement lineage while
  its canonical final terminal transition identified another, and
- Decimal-context precision could round a mathematically exact midpoint or leak
  `decimal.InvalidOperation` while serializing a very large valid integer-tick
  range.

Correction assertions were added first inside existing Cases 11, 18, 27, 30, and
33 without adding or removing a numbered logical case. The focused red phase
produced:

- `6 failed, 51 passed in 0.85s`

Those failures covered both reversal directions, snapshot/terminal-transition
cross-field reconciliation, positive and negative arbitrary-magnitude integer
ticks, even and odd spans, low- and high-Decimal-context determinism, and public
builder exception containment. The source was then corrected without changing
the public API, identity fields, lifecycle graph, or terminal-only behavior.

The subsequent independent re-audit found that mathematically equivalent signed
zero `Decimal` values could serialize as either `0.0` or `-0.0` and therefore
produce different public identities. Assertions were added first inside existing
Cases 30 and 33 for `Decimal("0")`, `Decimal("-0")`, `Decimal("0.0")`, and
`Decimal("-0.0")`. The first red run exposed one duplicate-keyword defect in the
new Case 30 test harness as well as the intended Case 33 identity failure:

- `2 failed, 55 passed in 0.72s`

Only the test harness was corrected, after which the clean semantic red phase
still produced:

- `2 failed, 55 passed in 0.71s`

The serializer was then corrected so every zero-valued `Decimal` canonicalizes to
exact `0.0`. Non-zero integer and half-tick serialization, arbitrary-magnitude
arithmetic, Decimal-context independence, identity payload fields, and all public
contracts remained unchanged.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `PREMIUM_DISCOUNT_DETECTOR_VERSION`
- `PremiumDiscountZone`
- `PremiumDiscountObservation`
- `PremiumDiscountZoneSet`
- `PremiumDiscountClassification`
- `PremiumDiscountSnapshot`
- `PremiumDiscountResult`
- `make_premium_discount_id`
- `analyze_premium_discount`

Both public functions are keyword-only and exactly match the formal decision
record. Every public data model is frozen. Version 1 contains no public config,
raw detector, runtime registration, or integration entry point.

## 5. Immutable Input and Fail-Closed Contracts

The analyzer consumes only:

- immutable canonical `DealingRangeSnapshot` tuples, and
- immutable fully closed integer-tick `PremiumDiscountObservation` tuples.

Implemented fail-closed behavior includes:

- missing top-level context returns `UNKNOWN`,
- complete empty context returns `NONE`,
- malformed present context returns `INVALID`,
- observation indices and normalized timestamps are independently strictly
  increasing and unique,
- booleans and floats are rejected where exact integer ticks or indices are
  required,
- malformed snapshot-local hashes, source tuples, protected identity,
  provenance, midpoint, transition chain, transition identities, or snapshot
  identity return `INVALID`,
- canonical terminal-only and internal-only histories remain valid but ineligible
  and return `NONE`,
- a terminal snapshot replacement lineage must exactly match its final canonical
  transition replacement lineage,
- required nested fields do not leak attribute, key, index, Decimal, timestamp,
  or enum exceptions, and
- supplied tuples are never silently sorted, deduplicated, repaired, coerced, or
  backfilled.

Strictly earlier immutable zone sets, classifications, and snapshots remain
available when a determinable later effective group fails. Nothing from the
failing group is promoted.

## 6. Exact Zone and Direction Semantics

- Only `EXTERNAL` and `ACTIVE` Dealing Range snapshots are eligible.
- Equilibrium is exactly
  `(Decimal(low_tick) + Decimal(high_tick)) / Decimal(2)`.
- Inside prices below Equilibrium are `DISCOUNT`.
- Exact integer-tick midpoint equality is `EQUILIBRIUM`.
- Inside prices above Equilibrium are `PREMIUM`.
- Exact low and high boundaries remain inside and classify as Discount and
  Premium respectively.
- Outside-range observations emit no classification or snapshot.
- An odd tick span produces an exact half-tick Equilibrium without rounding.
- Arbitrary-magnitude positive and negative integer ticks preserve the same exact
  result independently of the active Decimal context precision.
- Direction is mandatory immutable context and never changes location labels.
- No zone is converted into BUY, SELL, bias, confidence, readiness, overbought,
  oversold, entry, target, or reversal output.

## 7. Deterministic Chronology and Same-Index Precedence

Range effective moments use canonical first-known provenance for ACTIVE and
internal snapshots and the final transition moment for terminal snapshots.
Caller-supplied range order must be nondecreasing and observation indices and
timestamps must each be strictly increasing.

Same-effective range evidence is processed atomically:

1. validate the complete group,
2. apply old-lineage `SUPERSEDED` or `INVALIDATED` evidence,
3. apply at most one causally resolvable new or revised ACTIVE external range,
4. resolve the immutable zone-set version, and
5. classify the same-group observation under the post-transition context.

Both reversal directions are covered. An observation at terminal-old plus
replacement-new evidence uses only the new range. Multiple unrelated active
external candidates return `AMBIGUOUS` with no same-group promotion. A malformed
group returns `INVALID` with no same-group promotion.

## 8. Immutable Zone-Set Versioning

Zone-set history is keyed by external range lineage.

- The first material zone set is version `1`.
- Identical material evidence reuses its zone-set ID, version, and immutable
  creation snapshot context.
- Material direction, ordered source identity, protected swing, construction
  event, boundaries, or Equilibrium change creates the next integer version.
- A new version links the exact prior zone-set ID.
- A new lineage begins an independent version-1 history.
- A current range snapshot ID is classification context and is not itself stored
  as mutable zone-set material.
- Past zone sets, classifications, and snapshots are never mutated or relabeled.

## 9. Deterministic Identity Contract

The exact identity kinds are:

- `ZONE_SET`
- `CLASSIFICATION`
- `SNAPSHOT`

Every builder parameter is enforced as required or forbidden per identity kind.
Instrument and timeframe normalization is exactly `value.strip().upper()`.
Canonical payloads use sorted-key compact ASCII JSON, UTC timestamps serialized
as `YYYY-MM-DDTHH:MM:SS.ffffffZ`, detector version, lowercase SHA-256, and exact
Decimal `.0` or `.5` Equilibrium serialization. Midpoint construction and
serialization use integer parity and fixed-point text and do not depend on
Decimal context precision or `quantize()`.

ZONE_SET identity binds immutable source evidence, boundaries, exact Equilibrium,
creation range snapshot, first-known index and timestamp, version, and prior
version link. CLASSIFICATION identity reconciles its price and zone against exact
boundaries and Equilibrium. SNAPSHOT identity recomputes and exact-matches the
referenced CLASSIFICATION identity before construction.

## 10. Prefix Invariance and Evidence Preservation

Repeated analysis of identical immutable inputs is dataclass-equal. A valid prefix
ending at a complete effective-group boundary remains byte-for-byte equal when
strictly later valid evidence is appended.

Later evidence may append zone-set versions, terminate a range, establish a new
lineage, or append classifications. It cannot rewrite a prior zone, attach an
earlier observation to a later range, rewrite creation context, or fill earlier
missing context with hindsight. A later invalid group preserves strictly earlier
output while promoting nothing from that group or after it.

## 11. Exact Logical Test Matrix Reconciliation

The dedicated module contains exactly `36` distinctly numbered logical cases.
Parameterization expands them to `57` collected focused tests.

Coverage includes:

- both range directions and all three location labels,
- exact low, high, integer midpoint, half-tick midpoint, negative, zero, and
  positive integer-tick arithmetic,
- outside omission and `NONE`,
- missing, empty, malformed, duplicate, contradictory, and independently
  non-increasing input families,
- canonical internal-only and terminal-only evidence,
- construction, termination, both replacement directions, unrelated-range
  ambiguity, and same-group atomic failure,
- exact snapshot/final-transition replacement-lineage reconciliation with
  immutable prior-evidence preservation,
- immutable reuse, boundary and source versioning, new-lineage history, and prior
  evidence preservation,
- arbitrary-magnitude positive and negative integer ticks, both span parities,
  Decimal-context independence, and no `decimal.InvalidOperation` leakage,
- signed-zero equivalence across `0`, `-0`, `0.0`, and `-0.0`, with exact `0.0`
  canonical serialization and deterministic public identities,
- all three exhaustive identity schemas and cross-object reconciliation,
- exact frozen dataclass fields, enum values, keyword-only functions, exports,
  normalization, timestamp determinism, and unknown-kind rejection,
- repeatability, complete-group prefix invariance, and later-invalid
  preservation, and
- forbidden dependency and integration checks.

## 12. Test Results

Focused command:

`venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_premium_discount.py`

Focused result: `57 passed in 0.54s`.

Full regression command:

`venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider`

The first sandboxed baseline attempt encountered only a Windows pytest temp-root
permission setup error before assertions. The suite was rerun with normal Windows
temp access, bytecode disabled, and pytest cache disabled.

Full regression result: `1175 passed in 8.65s`.

## 13. Locked Artifact Identities

Physical line counts include blank physical lines.

- `smc/premium_discount.py`
  - bytes: `54210`
  - physical lines: `1477`
  - SHA-256:
    `DC137E0FD66699E6B09A676DB63C17CF2F7AFB6BEC9EE5E01C53580902BC11A8`
- `tests/test_premium_discount.py`
  - bytes: `40412`
  - physical lines: `1090`
  - SHA-256:
    `A924383A255F51B7677EC7D11C066ABA870212600BCFDF1A4FB5B311C552D1ED`

Frozen direct dependency identities remained unchanged:

- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `smc/dealing_range.py`:
  `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `smc/liquidity_map.py`:
  `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`

## 14. Isolation and Safety Evidence

- No import or edit connects the new module to current runtime paths.
- No package export, registration, config, CLI, main, strategy, decision, risk,
  backtest, report, trace, or execution path changed.
- No Liquidity Map output, pandas, raw OHLC, v1 SMC, file-loading, network,
  broker, credential, account, private data, candidate data, or OOS evidence
  dependency was added.
- No external fixture, staging, commit, push, integration, paper progression,
  live progression, broker access, or real execution was performed.

## 15. Completion, Rollback, and Next Gate

The bounded implementation is complete only as a standalone diagnostic candidate
pending independent final code, test, scope, hash, checkpoint, and diff audit.

Rollback before commit remains limited to the exact three new paths and requires
explicit instruction before destructive removal. Any need for another project
path, external fixture, dependency amendment, integration, public API change,
matrix reduction, lifecycle weakening, or failing regression is a stop condition
rather than authorization to expand scope.

- `EXACT_THREE_PATH_SCOPE_PASS=True`
- `TEST_FIRST_EVIDENCE_PASS=True`
- `LOCKED_36_CASE_MATRIX_PASS=True`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_TOTAL=57`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_TOTAL=1175`
- `EXTERNAL_FIXTURE_CREATED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE_OUTSIDE_TASK=True`
