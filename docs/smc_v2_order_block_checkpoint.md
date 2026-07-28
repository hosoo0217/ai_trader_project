# SMC V2 Order Block Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-ORDER-BLOCK-IMPLEMENTATION-CHECKPOINT-2026-07-28`.
- Parent decision ID:
  `SMC-V2-ORDER-BLOCK-FREEZE-LIFT-DECISION-2026-07-28`.
- Implementation parent commit:
  `077a71f6a2b87644e980da4b3dae062e61311854`.
- Formal decision record SHA-256:
  `2E3608C1387C052004B97B45DFDC2EA363A51AB42425A916B894EFA8E4D60C69`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `smc/order_block.py`
- `tests/test_order_block.py`
- `docs/smc_v2_order_block_checkpoint.md`

No external fixture was created. Synthetic inputs are inline in the dedicated
test module. No existing source, test, fixture, package initializer,
configuration, runtime, strategy, risk, execution, or integration file changed.

## 3. Test-First Evidence

The dedicated numbered tests were created before the production module. The
first focused collection failed with the expected red-phase result:

- `ModuleNotFoundError: No module named 'smc.order_block'`

After the first production implementation, the focused run produced:

- `2 failed, 44 passed in 0.58s`

The failures identified:

- Decimal-context rounding in exact midpoint construction, and
- a synthetic doji source-selection fixture with no earlier opposite candle.

The midpoint implementation was corrected to construct exact integer or
half-tick Decimal values without ambient-context arithmetic. The synthetic
fixture was corrected to include an earlier eligible opposite candle. A later
manual lifecycle pass also prevented shallower observations from attempting a
regressive transition and made canonical Decimal text exact for negative
half-ticks.

Before checkpoint finalization, explicit Case 39 and Case 40 assertions were
tightened to prove distinct same-group candidates produce `AMBIGUOUS` and a
later invalid event group preserves strictly prior immutable evidence while
promoting nothing at the failing moment. The analyzer was correspondingly made
group-atomic for a determinable later event-validation failure.

The independent final audit then correctly withheld staging because later
malformed candles and confirmed swings were still validated as complete tuples
before chronological analysis, and several compound requirements inside the
44-case matrix were not explicit assertions.

Case 40 was extended first for later malformed candle, later malformed confirmed
swing, and unknowable-moment evidence. The semantic red phase produced:

- `2 failed, 1 passed, 45 deselected in 0.51s`

The analyzer was corrected to validate candles, swings, and structure events
through causal prefixes, determine the earliest safe failing moment, preserve
strictly prior immutable evidence, and promote nothing at or after the failing
group. Unknowable malformed moments remain fail-closed without claiming a
trustworthy prefix.

The exact numbered count remained 44 while parameterization expanded coverage
for history/median edges, non-suffix provenance, every mirrored lifecycle
boundary, malformed nested inputs, exhaustive identity-schema failures, public
contracts, prefix invariance, deterministic multi-block ordering, and forbidden
imports. The first expanded focused run exposed one first-group precedence bug:

- `2 failed, 76 passed in 0.66s`

Both failures showed that a malformed first candle with a safely known moment
was incorrectly reaching the complete-empty `NONE` branch. That ordering was
corrected so the known invalid first group returns `INVALID`.

The final re-audit then found that an earlier `AMBIGUOUS` or insufficient-history
`UNKNOWN` effective group could return before a determinably later malformed
candle was allowed to enforce the locked final-status precedence. Cases 39 and
40 were extended first. The targeted red run produced:

- `2 failed, 4 passed, 74 deselected in 0.59s`

The analyzer was corrected so `_AmbiguousGroup` and `_UnknownGroup` handling
cannot suppress an already prevalidated later `INVALID` issue. The candidate
state for the earlier non-promotable group remains discarded, evidence at and
after the failing group is not promoted, and only strictly prior immutable
evidence may survive.

Cases 15 and 18 were strengthened with result-discriminating median fixtures.
The 10–19 range proves all available members are used; the 25-bar fixture gives
different all-25 and latest-20 answers and proves the latest 20 are used.
Zero-body, exact even-member half-tick, arbitrary-magnitude positive integer
body, and low/high Decimal-context paths are explicitly asserted.

Cases 41–43 now exercise every required and forbidden identity field, complete
BLOCK sensitivity groups, every allowed lifecycle edge, impossible edges,
exact reason-token rejection, ordered unique transition history, malformed
hash containment, full snapshot sensitivity, exact keyword-only parameter
names/defaults, every public frozen dataclass field list, enum values, and
exports.

The final focused evidence is:

- `81 passed in 0.56s`
- exactly `44` numbered logical cases
- 37 additional collected tests from locked parameterization

The final full regression evidence is:

- `1322 passed in 8.85s`

Both runs used `-p no:cacheprovider`.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `ORDER_BLOCK_DETECTOR_VERSION`
- `OrderBlockState`
- `OrderBlockCandle`
- `OrderBlock`
- `OrderBlockTransition`
- `OrderBlockSnapshot`
- `OrderBlockResult`
- `make_order_block_id`
- `analyze_order_blocks`

Both functions are keyword-only and match the decision record. Every public
data model is frozen. There is no public configuration, file adapter, runtime
registration, or integration entry point.

## 5. Immutable Input and Fail-Closed Contracts

The analyzer consumes only immutable tuples of:

- fully closed integer-tick `OrderBlockCandle`,
- caller-confirmed `DealingRangeSwing`, and
- caller-confirmed `DealingRangeStructureEvent`.

Missing top-level context returns `UNKNOWN`. Complete empty or valid
no-formation context returns `NONE`. Malformed present input returns `INVALID`
without attribute, key, index, timestamp, enum, or nested-identity exception
leakage. Candle indices and timestamps are independently strictly increasing.
Supplied tuples are never silently sorted, repaired, coerced, or backfilled.

Confirmed swing provenance is single-source, candle-resolved, side/price
reconciled, and at least two closed bars before confirmation. Structure-event
provenance is non-empty, contiguous, candle-resolved, ends at confirmation, and
reproduces through public `make_dealing_range_id(identity_kind="EVENT", ...)`.

## 6. Structural Break and Displacement

- Bullish evidence requires a confirmed HIGH swing and bullish BOS or CHOCH
  close at least one tick above it.
- Bearish evidence is the exact LOW-swing mirror.
- A present confirmed event lacking that exact break is `INVALID`.
- Raw wick-only or close-equal evidence without a matching supplied event emits
  no block.
- Candidate displacement is an exact contiguous event-provenance suffix.
- Lengths are evaluated in deterministic `3`, `2`, `1` order.
- Every member is directional and at least one member passes both the exact
  `0.60` integer ratio and preceding-body median.

## 7. Median and Source Selection

The median uses the last up to 20 supplied candles strictly before candidate
displacement. Fewer than 10 is insufficient. Odd medians are exact integers;
even medians are exact integer or half-tick Decimal values without float or
ambient Decimal-context dependence.

The source is the most recent opposite-color candle in the exact preceding
10-candle window. Dojis and out-of-window candles are excluded. Source,
displacement, swing, and event linkage become immutable formation evidence.

## 8. Boundaries and Midpoint

Wick and body ranges reproduce the selected source OHLC. Bullish
proximal/distal orientation is high/low; bearish orientation is low/high. The
midpoint is the exact wick-range integer or half tick, supports arbitrary
positive and negative integer ticks, and canonicalizes signed zero to `0.0`.
Boundaries never mutate.

## 9. Lifecycle and Atomic Processing

The exact lifecycle is:

- `DETECTED`
- `ACTIVE`
- `TOUCHED`
- `PARTIALLY_MITIGATED`
- `MITIGATED`
- `FULLY_TRAVERSED`
- `INVALIDATED`

Formation emits `None -> DETECTED`. The first strictly later candle emits
`DETECTED -> ACTIVE` before any deeper same-candle transition. Formation candles
cannot mitigate their own block. Close-through invalidation has deepest
same-candle precedence. State progress is monotonic; shallower evidence never
regresses it. `INVALIDATED` is terminal, while `FULLY_TRAVERSED` may only remain
unchanged or later invalidate. There is no expiry or replacement.

Each effective group is validated and promoted atomically. Prior blocks update
before a new formation at the same moment. Ambiguous same-group candidates
promote no same-group evidence. On complete supplied evidence, a determinably
later malformed group has final `INVALID` precedence over an earlier
non-promotable `AMBIGUOUS` or insufficient-history `UNKNOWN` group.

## 10. Deterministic Identity Contract

The exact identity kinds are:

- `BLOCK`
- `TRANSITION`
- `SNAPSHOT`

Every kind enforces exact required and forbidden parameters. Canonical payloads
use normalized instrument/timeframe, detector version, sorted-key compact ASCII
JSON, UTC microsecond timestamps, enum values, exact ticks, ordered tuples, exact
Decimal text, and lowercase SHA-256.

BLOCK binds complete immutable formation evidence. TRANSITION binds block,
state edge, effective moment, and exact reason token. SNAPSHOT binds current
state and complete ordered transition-ID history.

## 11. Exact Logical Matrix

The dedicated test module contains exactly `44` sequentially numbered logical
cases and `81` collected tests. Coverage includes both directions, BOS/CHOCH,
event/swing reconciliation, displacement suffixes, ratio/median edges, finite
source selection, boundaries, Decimal midpoint behavior, every lifecycle state,
same-index precedence, fail-closed inputs, identity reproduction, frozen public
contracts, exhaustive kind-specific identity schemas, final status precedence,
ambiguity, scope, and regression safety.

All fixtures are obviously synthetic and inline. No private market, account,
credential, OOS, PnL, generated-report, or outcome-derived evidence is present.

## 12. Prefix Invariance and Integration Boundary

Repeated identical immutable inputs produce dataclass-equal results and stable
identities. Strictly later valid evidence appends lifecycle or new formation
evidence without rewriting prior blocks, transitions, snapshots, boundaries, or
IDs.

The module is not imported by current production Python paths. It performs no
pandas, CSV, broker, Sierra, API, config, signal, strategy, risk, execution, or
package-registration work. No integration was started.

## 13. Artifact Evidence

- `smc/order_block.py`
  - SHA-256:
    `C504A98DA82D154EEE03346A256159BA8854FF2FC56EC437E344781D8F0138C5`
  - bytes: `43573`
  - physical lines: `985`
- `tests/test_order_block.py`
  - SHA-256:
    `07749D3EDC3FCE85164DB011625336EA6ABE9D7FBFFFE746A52EE082D1280728`
  - bytes: `48020`
  - physical lines: `1320`

These values were captured after the final focused and full regression runs.

## 14. Rollback, Promotion, and Freeze State

Before commit, rollback is limited to these exact newly created paths and
requires explicit instruction before removal. After a future commit, rollback
must use a bounded revert rather than history rewriting, followed by focused
tests, full regression, and exact-scope audit.

This checkpoint does not authorize staging, commit, push, integration, tuning,
strategy use, paper use, or live use. Independent final code/test/scope/hash
audit and separate promotion gates remain required.

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`
- `EXACT_CHANGED_PATHS=3`
- `INLINE_SYNTHETIC_LOGICAL_CASES=44`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_COLLECTED=81`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=1322`
- `INTEGRATION_STARTED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE_OUTSIDE_TASK=True`
