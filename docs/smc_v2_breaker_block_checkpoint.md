# SMC V2 Breaker Block Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-BREAKER-BLOCK-IMPLEMENTATION-CHECKPOINT-2026-07-28`.
- Parent decision ID:
  `SMC-V2-BREAKER-BLOCK-FREEZE-LIFT-DECISION-2026-07-28`.
- Implementation parent commit:
  `ea22637f4fab1c98320ee30a7ba98a499f8ce6cd`.
- Formal decision record SHA-256:
  `5B1DE1E34A2108C432CFDFB38E5B377D5B1602A8C82C247E8E2C66E8AF27B51F`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/breaker_block.py`
- `tests/test_breaker_block.py`
- `docs/smc_v2_breaker_block_checkpoint.md`

No external fixture was created. Synthetic evidence is inline in the dedicated
test module. No existing source, test, fixture, package initializer,
configuration, runtime, strategy, risk, execution, or integration file changed.

## 3. Test-First Evidence

The numbered tests were created before the production module. The first focused
collection produced the expected red phase:

- `ModuleNotFoundError: No module named 'smc.breaker_block'`

The first implementation run then produced:

- `47 passed, 7 failed in 0.95s`

All seven failures belonged to two locked status boundaries: malformed
instrument text needed `INVALID` precedence over missing top-level context, and
an empty observation horizon needed pre-horizon `UNKNOWN` handling. After the
bounded correction, all focused tests passed.

A semantic self-audit then tightened source Order Block swing/event reference
reconciliation, source-side uniqueness, the committed two-bar
swing-confirmation delay, event provenance/observation binding, unrecorded
pre-invalidation close-through rejection, a truly canonical opposing-direction
ambiguity fixture, and arbitrary-magnitude Decimal midpoint identity
determinism.

The independent final audit then withheld staging after reproducing two
fail-closed defects: an in-horizon swing source observation could be absent
while the analyzer still returned `VALID`, and a determinably later malformed
event returned `INVALID` but discarded strictly prior Breaker evidence. Tests
for Cases 11, 12, and 37 were added first. The correction red phase produced:

- `52 passed, 2 failed in 0.96s`

The bounded correction now requires in-horizon swing source and confirmation
observations, contains source/confirmation timestamp mismatches, and routes
determinably later malformed block, history, swing, event, and observation
evidence through a causal cutoff. The cutoff replays only strictly prior
canonical evidence, promotes nothing from the failing group or later, and
claims no prefix for an unknowable malformed moment.

Cases 35 and 39 through 43 were expanded without changing the locked logical
case count. They now cover later ambiguity preservation, exhaustive
kind-specific identity fields, direct/impossible lifecycle edges, exact public
signatures/defaults, all frozen public dataclasses, no-silent-sort cases, and
multi-source repeatability. The final focused evidence is:

- `54 passed in 0.79s`
- exactly `44` numbered logical cases
- 10 additional collected tests from locked parameterization

The authoritative full regression evidence is:

- `1424 passed in 13.29s`

Both focused and full runs used `-p no:cacheprovider`.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `BREAKER_BLOCK_DETECTOR_VERSION`
- `BreakerBlockState`
- `BreakerBlockObservation`
- `BreakerBlock`
- `BreakerBlockTransition`
- `BreakerBlockSnapshot`
- `BreakerBlockResult`
- `make_breaker_block_id`
- `analyze_breaker_blocks`

Both functions are keyword-only and match the formal decision. All public data
models are frozen. There is no public configuration, adapter, registry, runtime
hook, or integration entry point.

## 5. Immutable Inputs and Foreign Validation

The analyzer accepts only exact immutable tuples of canonical `OrderBlock`,
`OrderBlockTransition`, `OrderBlockSnapshot`, `DealingRangeSwing`,
`DealingRangeStructureEvent`, and fully closed integer-tick
`BreakerBlockObservation` evidence.

Source Order Block, transition, snapshot, and Dealing Range event identities are
recomputed with their public dependency builders. Source blocks resolve their
supplied swing and event references exactly. Swing provenance, side, price,
two-bar confirmation delay, source/confirmation timestamps, uniqueness, and
composite order are checked. Missing in-horizon swing source or confirmation
observations are invalid; strictly pre-horizon unavailable evidence retains the
locked unknown boundary. Events bind canonical swing references, contiguous
provenance, final-source confirmation equality, observation close-break
geometry, identity, uniqueness, and supplied composite order.

No tuple is silently sorted, coerced, repaired, deduplicated, or enriched.
Malformed nested evidence is contained and returned as `INVALID`.

## 6. Source History and Invalidation

Order Block transitions and snapshots are separately nondecreasing, retain
upstream causal order at equal moments, and reconcile one-to-one through exact
ordered transition-ID prefixes. Snapshot direction, state, effective moment,
identity, and history must mirror the corresponding transition.

Only a final canonical `INVALIDATED` source state with
`CLOSE_THROUGH_INVALIDATION` qualifies. Bullish source close must be at or below
`distal - 1`; bearish source close must be at or above `distal + 1`. Missing
in-horizon or post-horizon invalidation evidence is invalid. A strictly
pre-horizon invalidation, including an empty observation tuple, is unknown.
Any earlier geometric close-through without its exact transition/snapshot, or
before a claimed later invalidation, is invalid.

## 7. Confirmation Window and Role Reversal

The confirmation window is positional: the invalidation observation is offset
0 and the next ten supplied closed observations are offsets 1 through 10.
Offset 10 qualifies and offset 11 does not. The earliest matching canonical BOS
or CHOCH wins.

A failed bullish Order Block becomes a bearish Breaker. A failed bearish Order
Block becomes a bullish Breaker. Original wick and body boundaries remain
immutable; only proximal/distal interpretation reverses. Formation binds the
source block, invalidation transition/snapshot, selected event, direction,
geometry, invalidation moment, and confirmation moment.

## 8. Decimal Geometry

Midpoints use exact integer or half-tick `Decimal` construction without float
conversion or ambient context rounding. Arbitrary-magnitude positive and
negative ticks remain deterministic. Every zero representation serializes as
`0.0`; nonzero midpoint text is exact `.0` or `.5`.

The public identity builder reconciles body containment, role-reversed
proximal/distal geometry, exact midpoint, causal invalidation/confirmation
moments, exact hash shapes, and kind-specific required/forbidden parameters.

## 9. Lifecycle and Atomic Processing

The exact lifecycle is:

- `None -> ACTIVE` with `ROLE_REVERSAL_CONFIRMED`
- forward-only touch/partial/midpoint transitions
- any live state `-> INVALIDATED` with
  `CLOSE_THROUGH_INVALIDATION`

The formation observation cannot retest or invalidate the new Breaker.
Strictly later observations use bullish/bearish mirrored geometry. Same-index
adverse close-through has precedence over touch or mitigation. Direct deeper
transitions are allowed, shallower observations do not regress state, and
`INVALIDATED` is terminal. There is no expiry, replacement, reactivation, or
boundary mutation.

Every effective observation group is cloned, fully validated, and promoted
atomically. A failing group promotes no partial evidence and preserves only
strictly prior immutable output. Determinably later malformed blocks, source
history records, swings, events, and observations share the same causal-cutoff
rule. A later opposing-direction ambiguous group also preserves strictly prior
output and promotes nothing from its own atomic group.

## 10. Deterministic Identity Contract

The exact identity kinds are:

- `BREAKER`
- `TRANSITION`
- `SNAPSHOT`

Each kind enforces exact required and forbidden fields. Canonical payloads bind
the detector version, stripped-uppercase instrument/timeframe, enum values,
source and event hashes, immutable geometry or lifecycle data, UTC microsecond
timestamps, and ordered transition history as applicable. Compact sorted-key
ASCII JSON is hashed with lowercase SHA-256.

Only locked lifecycle edges and exact reason tokens are accepted. Public
builder failures are contained as `TypeError` or `ValueError`.

## 11. Status and Ambiguity

Final status precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Repeated or same-direction forked events are invalid. One canonical bullish and
one canonical bearish event in a formation-relevant atomic group is ambiguous
and promotes no group evidence. Independent valid source blocks remain
deterministic and may produce multiple Breakers.

## 12. Exact Logical Matrix

The dedicated test module preserves exactly 44 sequential logical cases and
collects 54 tests. Coverage includes top-level status boundaries, canonical
source identities and complete histories, swing/event contracts, both source
directions, offsets 0/inside/10/11, BOS/CHOCH selection, role-reversed geometry,
formation non-retest, both lifecycle directions, invalidation precedence,
terminal behavior, ambiguity, multiple sources, later malformed-group
preservation across all six input streams, exhaustive identity schemas, every
allowed direct and representative impossible transition edge, exact API names
and defaults, exact public dataclass fields/annotations/defaults/frozen state,
repeatability, complete-prefix and ineligible-append behavior, and forbidden
integration surface.

All fixtures are inline and synthetic. No saved market data, PnL, OOS,
credential, account, external API, or outcome-derived evidence is used.

## 13. Prefix Invariance and Isolation

Repeated immutable input produces dataclass-equal output and stable identities.
A complete valid prefix remains unchanged when strictly later complete evidence
is appended. Same-effective append, insertion, partial history, or repaired
evidence is not an eligible prefix comparison and is validated normally.

The module imports only public Dealing Range, Order Block, and shared primitive
dependencies. It performs no pandas, CSV, broker, Sierra, API, config, signal,
strategy, risk, execution, package registration, file, network, or integration
work.

## 14. Artifact Evidence

- `smc/breaker_block.py`
  - SHA-256:
    `03E2559C99F62826E87C435C3102A5B5B069FE3BE4BF234A8A3C89DFCBB2D45D`
  - bytes: `74110`
  - physical lines: `1932`
- `tests/test_breaker_block.py`
  - SHA-256:
    `CC1A1031DFC0F3AC6A188F19437C99A21168E097A23DA09915189F0596CF36AD`
  - bytes: `64502`
  - physical lines: `1859`
- `docs/smc_v2_breaker_block_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes and physical lines are reported by the final scope audit

## 15. Promotion, Rollback, and Stop Conditions

This checkpoint does not authorize integration, staging, commit, push, paper
progression, live progression, threshold selection, tuning, or runtime use.
Promotion requires an independent exact-scope code/test/checkpoint audit and a
separate explicit staging instruction.

Rollback is deletion of exactly the three untracked task artifacts before any
promotion. Stop immediately on any dependency drift, scope expansion, public
API mismatch, identity nondeterminism, lifecycle ambiguity, uncontained
exception, focused/full regression failure, or integration request outside a
separately approved freeze-lift decision.
