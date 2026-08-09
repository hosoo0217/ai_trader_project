# GC Futures Phase A Structural Seed Evidence Change Proposal

## 1. Decision status

**Decision:** `CONTRACT_LOCKED_IMPLEMENTATION_STOPPED`

This record locks a deterministic, no-look-ahead contract for deriving the
structural seed evidence required by the accepted GC Futures Phase A candidate
evidence design. It authorizes no implementation, dataset mutation, training,
integration, staging, commit, or push.

The downstream candidate-evidence proposal has been corrected to respect
segment-local bar indices through per-segment analyzer calls, segment-qualified
aggregation, and segment-aware ordering. This structural contract remains
implementation-stopped until the two proposals pass one independent
documentation-only cross-audit. Section 23 records that mandatory gate and the
remaining stop conditions.

## 2. Bounded objective

The only objective of this bounded change is to specify how an accepted,
immutable `GCDatasetBuildResult` can produce one immutable
`GCCanonicalSeedEvidence` value containing:

- confirmed `DealingRangeSwing` values;
- one-to-one mirrored `EqualLiquiditySwing` values;
- confirmed `DealingRangeStructureEvent` values; and
- formation-time `FairValueGapContextLink` values.

The seed is diagnostic evidence. It is not a trade signal, label, prediction,
confidence score, position, order, entry, exit, risk instruction, or PnL input.

## 3. Scope and freeze boundary

The future implementation scope is reserved to exactly:

- `analysis/gc_structural_seed_evidence.py`
- `tests/test_gc_structural_seed_evidence.py`
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`

No external fixture is authorized. A future private output root may be proposed
separately as:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence/`

It is not authorized by this record.

The following remain frozen:

- dataset acquisition and accepted private manifests;
- `analysis/gc_dataset_builder.py` and feature/label code;
- all `smc/` detector modules and shared primitives;
- package exports, configuration, engines, runtime, decision trace, and `main.py`;
- training, model fitting, hyperparameter search, backtest promotion, and live use;
- Git staging, commit, push, branch, and pull-request operations.

## 4. Normative dependencies

The future module may import only immutable public contracts and public identity
builders needed from these accepted dependencies:

- `analysis.gc_dataset_builder`;
- `smc.smc_v2_primitives`;
- `smc.equal_liquidity`;
- `smc.dealing_range`;
- `smc.fair_value_gap`.

The following legacy paths are explicitly prohibited:

- `smc.market_structure`;
- `smc.bos_choch`;
- mutable runtime context or execution code;
- any code path that recomputes or rewrites the accepted dataset.

Dependency SHA-256 values locked for this proposal are:

- `analysis/gc_dataset_builder.py`:
  `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121`
- `analysis/gc_feature_label_builder.py`:
  `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`
- `smc/smc_v2_primitives.py`:
  `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `smc/equal_liquidity.py`:
  `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`
- `smc/dealing_range.py`:
  `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `smc/fair_value_gap.py`:
  `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`
Any dependency hash change requires a new read-only compatibility audit before
implementation.

The candidate-evidence proposal is a downstream workflow consumer, not a
normative source-code dependency of this structural derivation module. This
proposal therefore does not content-hash-bind that mutable downstream document.
The independent cross-audit binds it by exact path, proposal ID
`GC-PHASE-A-CANDIDATE-EVIDENCE-PROPOSAL-V1`, and semantic compatibility. The
candidate proposal may bind this structural proposal's final SHA-256 in the
one-way dependency direction. Mutual document content-hash binding is forbidden
because it creates an irresolvable circular identity.

## 5. Immutable dataset input contract

`build_gc_structural_seed_evidence()` accepts an immutable
`GCDatasetBuildResult | None` plus the exact `GCDatasetBuildConfig` used to bind
its identity. The supplied dataset is never sorted, repaired, filtered,
reindexed, normalized in place, or enriched.

An eligible dataset must have exact `GCDatasetBuildStatus.VALID` and satisfy all
existing canonical validation, including:

- accepted status and exact `dataset_id` reconciliation;
- immutable ordered `segments`;
- exact segment, partition, source, and manifest provenance;
- fully closed integer-tick/integer-volume bars;
- strictly increasing normalized timestamps inside each segment;
- segment-local contiguous indices beginning at zero;
- exact in-sample/development/OOS partition boundaries;
- no overlap, duplicate source rows, or source digest mismatch.

Only development-partition bars are eligible. Validation and OOS bars are never
used to discover or confirm a seed member. A missing dataset is `UNKNOWN`; a
supplied malformed or noncanonical dataset is `INVALID`. Supplied dataset
statuses map without downgrade: `INVALID`, `AMBIGUOUS`, and `UNKNOWN` retain
their same semantic status; dataset `NONE` returns seed result `NONE` with
`seed is None` because no dataset ID or segment scope exists.

## 6. Segment-local chronology boundary

Every detector-compatible derivation runs independently inside one canonical
`GCCanonicalContractSegment`. State, lookback, confirmation, displacement, and
candidate selection never cross a segment boundary.

The canonical combined order is:

- the accepted dataset's immutable segment tuple order; then
- the detector-specific causal order inside that segment.

Local integer indices are meaningful only with their segment identity and exact
normalized timestamps. They are never treated as dataset-global indices. Hash
lexical order, direction lexical order, or identity lexical order is never a
chronology tie-break.

No-silent-sort is mandatory. Caller-supplied tuples that do not already follow
the locked segment-aware causal order are `INVALID`.

## 7. Exact structural seed configuration

The public version constant is exactly:

```python
GC_STRUCTURAL_SEED_VERSION = "GC-STRUCTURAL-SEED-V1"
```

The only V1 configuration is the frozen value:

```python
@dataclass(frozen=True)
class GCStructuralSeedConfig:
    swing_left_bars: int = 2
    swing_right_bars: int = 2
    break_buffer_ticks: int = 1
```

All three values must be exact non-boolean positive integers and must equal
`(2, 2, 1)`. V1 does not expose tunable discovery parameters. Any alternative
lookback or break buffer requires a new decision record and version.

## 8. Deterministic swing discovery

For source bar position `i` inside one eligible segment, exactly two preceding
and two following fully closed bars are required.

A HIGH swing qualifies only when the source `high_tick` is strictly greater
than the `high_tick` of all four neighbors. A LOW swing qualifies only when the
source `low_tick` is strictly lower than the `low_tick` of all four neighbors.
Equality or a plateau does not qualify that side.

If one outside bar qualifies both sides, calculate exact integer prominence:

- HIGH prominence = source high minus the maximum neighbor high;
- LOW prominence = minimum neighbor low minus the source low.

The greater prominence wins. An exact prominence tie deterministically selects
LOW. This is a membership rule, not a chronology rule.

The swing becomes first-known only at the close of the second right-hand bar.
Its provenance is single-source:

- `source_indices == (i,)`;
- `source_timestamps == (source.timestamp,)`;
- `confirmation_index == i + 2`;
- `confirmation_timestamp == second_right.timestamp`.

No future bar beyond the confirmation bar may affect the decision.

## 9. Mirrored swing objects and identity ownership

Every selected swing creates exactly one `EqualLiquiditySwing` and exactly one
`DealingRangeSwing`. The HIGH/LOW `.value`, integer tick, provenance, and
`swing_id` must be byte-for-byte equivalent. The side instances use their exact
respective public enum classes: `EqualLiquiditySide` and
`DealingRangeSwingSide`.

The ID is not owned by the future seed module. It must be the exact public
Equal Liquidity SWING identity recomputed by `make_equal_liquidity_id()` with:

- normalized instrument and timeframe;
- selected HIGH/LOW side;
- the exact single source index;
- `reference_tick == lower_tick == upper_tick == price_tick`.

That exact ID is reused by the mirrored `DealingRangeSwing`. A private swing ID
schema is forbidden.

Inside one segment, source indices are unique, selected swing IDs are unique,
and causal order is exactly:

`(confirmation_index, normalized_confirmation_timestamp, source_index,
side.value, swing_id)`.

The same hash may theoretically recur in a different segment because indices
are segment-local. Validation therefore binds each member to its segment using
exact timestamps and canonical segment membership; it never builds an
unqualified dataset-global dictionary keyed only by `swing_id`.

Every source and confirmation moment must match exactly one canonical segment.
No match or more than one possible segment match is `INVALID`.

## 10. Exact one-tick structural break

Structure discovery is performed at each fully closed bar `j` in a segment.
Only swings whose confirmation moment is strictly earlier than bar `j` are
eligible.

A bullish close break requires:

`close_tick >= broken HIGH price_tick + 1`.

A bearish close break requires:

`close_tick <= broken LOW price_tick - 1`.

Wick-only contact, close equality, a zero-tick pass, an unconfirmed swing, or a
break on the swing's own confirmation bar does not qualify.

Event provenance is the exact singleton confirmation bar:

- `source_indices == (j,)`;
- `source_timestamps == (bar_j.timestamp,)`;
- `confirmation_index == j`;
- `confirmation_timestamp == bar_j.timestamp`.

This satisfies contiguous provenance and makes the final source moment exactly
equal to the event confirmation moment.

## 11. Broken-swing and event-type selection

At one close, all newly crossed, previously unretired eligible levels in a
direction are evaluated as one atomic group.

For bullish selection, choose the highest crossed HIGH price; ties choose the
latest source index, then latest confirmation moment, then the already-canonical
swing order. For bearish selection, choose the lowest crossed LOW price with
the same recency tie rules. All levels crossed in that direction at that close
are retired together so an inner level cannot generate a redundant later event.

The first valid structural event in a segment is BOS. A subsequent event in the
same active direction is BOS. A direction reversal is CHOCH only when the exact
active protected swing is the selected broken swing.

After every complete bar group, active direction and protected-swing state must
be reconciled with the public `analyze_dealing_ranges()` contract, or with an
implementation independently proven byte-equivalent to that public result.
State may not be guessed from a future range or repaired retroactively.

If the exact event type or protected swing cannot be determined from the valid
prefix, the current and later group is `UNKNOWN` and no evidence from that group
is promoted. Malformed or contradictory evidence is `INVALID`.

## 12. Structure Event identity and ordering

Every emitted `DealingRangeStructureEvent` must use the public
`make_dealing_range_id(identity_kind="EVENT", ...)` contract with its exact
direction, BOS/CHOCH type, selected `broken_swing_id`, singleton provenance,
confirmation index, and zero-width `SMCV2TickRange` equal to the broken swing's
price tick. The public EVENT identity does not contain a timestamp; timestamp
reconciliation remains mandatory in event provenance validation.

The event ID must be recomputable from snapshot-local supplied evidence. Hash
shape alone is insufficient. The broken swing must exist in the same segment,
have HIGH side for bullish or LOW side for bearish, and be confirmed strictly
before displacement begins.

Per-segment order is exactly:

`(confirmation_index, normalized_confirmation_timestamp, direction.value,
event_type.value, event_id)`.

Bullish and bearish selected event candidates are evaluated before atomic group
promotion. A close can cross historically separated HIGH and LOW levels in the
same group. If both opposing candidates remain valid after active
direction/protected-swing reconciliation, the complete group is `AMBIGUOUS`;
neither event is promoted and no later group is analyzed. Hash or direction
lexical order must never select one side.

## 13. Qualifying Fair Value Gap formation

A potential Fair Value Gap is evaluated from exact consecutive segment-local
bars `(i, i + 1, i + 2)`.

Bullish formation requires:

`third.low_tick - first.high_tick >= 2`.

Its exact boundaries are `lower_tick == first.high_tick` and
`upper_tick == third.low_tick`.

Bearish formation requires:

`first.low_tick - third.high_tick >= 2`.

Its exact boundaries are `lower_tick == third.high_tick` and
`upper_tick == first.low_tick`.

The middle candle must have nonzero full range and exact integer displacement
ratio:

`5 * abs(close_tick - open_tick) >= 3 * (high_tick - low_tick)`.

Its first-known moment is the close of the third candle. Formation sequences do
not cross segment boundaries. Arithmetic is integer-exact and independent of
ambient Decimal precision.

## 14. Event/FVG causal binding and context link

A `FairValueGapContextLink` is emitted only when all conditions hold:

- a qualifying three-candle FVG ends at bar `i + 2`;
- a generated Structure Event has the same confirmation index and normalized
  timestamp;
- event direction equals FVG direction;
- every source moment reconciles to the immutable segment bars; and
- the event singleton source sequence is the exact positional suffix of the
  three-candle FVG source sequence.

The link fields are exact:

- formation end index and timestamp = third candle moment;
- `structure_event_id` and `structure_event_type` = bound event;
- `displacement_id` = exact non-null V1 DISPLACEMENT identity.

A qualifying FVG without a matching event emits no link. An event without a
qualifying FVG emits no link. A dangling, multiple-distinct, mismatched, or
cross-segment link is `INVALID`; no retroactive enrichment is allowed.

Inside one segment, links are already in independently nondecreasing
`(formation_end_index, normalized_formation_end_timestamp)` order. Atomic event
rules permit at most one promoted link at one segment-local moment. Combined
link order is segment ordinal followed by that moment; link hashes are identity
validation only and never chronology tie-breaks.

## 15. Opaque displacement boundary

The dependency API exposes no public displacement object or foreign identity
builder. V1 therefore treats `displacement_id` as deterministic, opaque,
formation-time metadata owned only by the future seed module.

It binds the exact segment, three ordered source moments, direction, FVG
boundaries, bound Structure Event ID, dataset ID, seed version, configuration,
and source-bar digest. It does not claim proof of a separate displacement
entity. Requiring stronger foreign displacement identity is a STOP condition;
the public API must not be silently expanded.

## 16. Canonical source and segment digests

`source_bar_digest` is SHA-256 over canonical typed JSON containing, in accepted
order:

- dataset identity and configuration binding;
- every canonical segment identity, contract, partition, trade-date bounds,
  source IDs, and preceding-missing count;
- every immutable bar field in tuple order.

No member is sorted, rounded, omitted, or serialized through locale-dependent
text.

Each segment evidence digest is independently recomputed from the exact full
selected swing pairs, events, links, and all nested provenance belonging to that
segment. It is not a digest of IDs alone. The combined seed identity contains an
ordered tuple of `(segment_id, segment_evidence_digest)` for every accepted
segment, including segments with no members.

Swing or event hashes may recur across distinct segments because their public
foreign schemas use segment-local indices and omit segment ID. Such members are
not duplicates when their exact segment-qualified moments differ. Full segment
digests prevent that allowed recurrence, deletion, insertion, reordering, or
history repair from preserving the same seed identity.

## 17. Deterministic identity schemas

The exact public enum is:

```python
class GCStructuralSeedIdentityKind(str, Enum):
    DISPLACEMENT = "DISPLACEMENT"
    SEED = "SEED"
```

Common required fields for both kinds are normalized instrument, normalized
timeframe, exact positive `Decimal` tick size, 64-hex dataset ID, exact seed
version, exact V1 config, and 64-hex source-bar digest.

`DISPLACEMENT` additionally requires and permits only:

- `segment_id`;
- bullish or bearish direction;
- exactly three ordered source indices and timestamps;
- exact two-tick-or-greater FVG boundaries;
- one canonical Structure Event ID.

It forbids `segment_evidence_digests`.

`SEED` additionally requires and permits only the complete ordered nonempty
`segment_evidence_digests`. It forbids segment ID, direction, source moments,
boundaries, and Structure Event ID.

Unknown kinds, missing required fields, supplied forbidden fields, booleans as
integers, naive timestamps, non-UTC-equivalent normalization, malformed hashes,
impossible geometry, duplicate segments, or noncanonical ordering raise only
`TypeError` or `ValueError`. Nested library exceptions must not leak.

## 18. Exact frozen public dataclasses

The public dataclass contracts are exactly:

```python
@dataclass(frozen=True)
class GCStructuralSeedConfig:
    swing_left_bars: int = 2
    swing_right_bars: int = 2
    break_buffer_ticks: int = 1

@dataclass(frozen=True)
class GCCanonicalSeedEvidence:
    seed_id: str
    seed_version: str
    instrument: str
    timeframe: str
    dataset_id: str
    source_bar_digest: str
    dealing_range_swings: tuple[DealingRangeSwing, ...]
    equal_liquidity_swings: tuple[EqualLiquiditySwing, ...]
    structure_events: tuple[DealingRangeStructureEvent, ...]
    fair_value_gap_context_links: tuple[FairValueGapContextLink, ...]

@dataclass(frozen=True)
class GCStructuralSeedResult:
    status: SMCV2PrimitiveStatus
    seed: GCCanonicalSeedEvidence | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

`GCCanonicalSeedEvidence` has no defaults. Every tuple is immutable and in the
locked segment-aware causal order.

## 19. Exact keyword-only public API

The future public signatures are exactly:

```python
def make_gc_structural_seed_id(
    *,
    identity_kind: GCStructuralSeedIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    seed_version: str,
    config: GCStructuralSeedConfig,
    source_bar_digest: str,
    segment_id: str | None = None,
    direction: SMCV2Direction | None = None,
    source_indices: tuple[int, ...] = (),
    source_timestamps: tuple[datetime, ...] = (),
    boundaries: SMCV2TickRange | None = None,
    structure_event_id: str | None = None,
    segment_evidence_digests: tuple[tuple[str, str], ...] = (),
) -> str: ...

def build_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult: ...

def validate_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult: ...
```

The exact public exports are:

- `GC_STRUCTURAL_SEED_VERSION`;
- `GCStructuralSeedIdentityKind`;
- `GCStructuralSeedConfig`;
- `GCCanonicalSeedEvidence`;
- `GCStructuralSeedResult`;
- `make_gc_structural_seed_id`;
- `build_gc_structural_seed_evidence`;
- `validate_gc_structural_seed_evidence`.

No positional arguments, aliases, convenience overloads, package re-exports,
or hidden mutable defaults are allowed.

Both public operations validate `dataset_config` and seed config before any
missing-dataset shortcut. `validate_gc_structural_seed_evidence()` then derives
the expected result through the exact same pure causal contract and requires the
supplied seed to be object-equal to that expected canonical seed. With a valid
dataset, `structural_seed is None` is `UNKNOWN`; a supplied noncanonical or
non-equal seed is `INVALID`. It never accepts hash shape or partial field
equality as validation.

## 20. Result status and atomic promotion

Final status precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

- `INVALID`: malformed, contradictory, noncanonical, or unrecomputable supplied
  evidence; `seed is None`.
- `AMBIGUOUS`: opposing valid event candidates survive in the same complete
  effective group; `seed is None`.
- `UNKNOWN`: required dataset or causal state cannot be established from the
  valid supplied prefix; `seed is None`.
- `VALID`: at least one structural member exists and the complete seed validates.
- `NONE`: dataset status `NONE` returns no seed because there is no identity
  scope; an eligible `VALID` dataset containing no selected member returns a
  canonical empty `GCCanonicalSeedEvidence` bound to all of its segments.

Promotion is atomic at each complete effective bar group and at final seed
construction. A failing group and all later groups promote nothing. Higher
precedence findings cannot be hidden by earlier `NONE`, `VALID`, or `UNKNOWN`.
The builder never returns a partially valid seed under `INVALID`, `AMBIGUOUS`,
or `UNKNOWN`.

Exact top-level reason tokens are:

- `MISSING_DATASET`;
- `DATASET_NONE`;
- `DATASET_UNKNOWN`;
- `DATASET_AMBIGUOUS`;
- `INVALID_DATASET`;
- `INVALID_CONFIG`;
- `MISSING_STRUCTURAL_SEED`;
- `STRUCTURE_UNKNOWN`;
- `OPPOSING_STRUCTURE_EVENTS`;
- `INVALID_STRUCTURAL_EVIDENCE`;
- `NO_STRUCTURAL_EVIDENCE`;
- `STRUCTURAL_EVIDENCE_VALID`.

`blocking_reasons` equals `reasons` for `INVALID`, `AMBIGUOUS`, and `UNKNOWN`,
and is empty for `VALID` and `NONE`. Free-form exception text is never an
identity input or public reason token.

## 21. No-look-ahead and prefix invariance

For every complete canonical segment prefix, output evidence through that
prefix must be byte-for-byte immutable when strictly later complete bars or
segments are appended.

A swing discovered later is first-known at its confirmation bar and is appended
at that causal moment; it does not rewrite the source-bar past. Events and FVG
links are first-known only at their exact confirmation/formation close. No
future range, future FVG state, future candidate outcome, label, return, entry,
exit, or PnL may influence seed membership or identity.

Prefix comparison is eligible only at a complete effective-group and segment
boundary. Same-effective append, partial segment, historical insertion,
reordering, source repair, partition mutation, dataset-ID change, or seed-version
change is not a valid prefix-invariance comparison and must fail closed.

## 22. Inline synthetic exact 48-case matrix

The future unit-test matrix uses inline synthetic immutable values only. Logical
case numbering is exact and sequential; parameterization may expand collected
test count without changing the 48 logical cases.

1. Missing dataset returns `UNKNOWN` with no seed.
2. Malformed supplied dataset returns `INVALID` without exception leakage.
3. Dataset ID/config/source digest mismatch returns `INVALID`.
4. Validation/OOS bars are excluded and cannot confirm development evidence.
5. Segment tuple order and segment-local zero-based contiguous indices validate.
6. Cross-segment lookback, confirmation, event, or FVG formation is forbidden.
7. Exact two-left/two-right strict HIGH swing qualifies.
8. Exact two-left/two-right strict LOW swing qualifies.
9. Equal neighbor high/low plateau does not qualify that side.
10. Insufficient left or right bars produce no swing and no look-ahead.
11. Dual-side outside bar selects greater integer prominence.
12. Exact dual-side prominence tie deterministically selects LOW.
13. Swing confirmation is exact second-right close and single-source provenance.
14. Equal Liquidity public SWING ID recomputes exactly.
15. Dealing Range swing mirrors side, tick, provenance, and exact swing ID.
16. Per-segment swing source/ID uniqueness and causal order reject reordering.
17. Same swing hash in different segments remains segment-bound, not merged.
18. Bullish exact one-tick close-through qualifies; equality/wick-only does not.
19. Bearish exact one-tick close-through qualifies; equality/wick-only does not.
20. Unconfirmed or same-confirmation-moment swing cannot be broken.
21. Bullish multiple-cross selection uses highest level then locked recency ties.
22. Bearish multiple-cross selection uses lowest level then locked recency ties.
23. All levels crossed in one direction at one close retire atomically.
24. First valid event is BOS and same-direction continuation remains BOS.
25. Reverse event is CHOCH only for exact active protected swing.
26. Indeterminable protected state produces `UNKNOWN` with no later promotion.
27. Event singleton provenance reconciles exactly to the confirmation bar.
28. Event public identity, side-specific broken swing, and one-tick rule recompute.
29. Event nondecreasing composite order rejects hash/direction-order substitution.
30. Valid simultaneous opposing event candidates are atomic `AMBIGUOUS` without lexical selection.
31. Exact bullish two-tick three-candle FVG and 0.60 integer ratio qualify.
32. Exact bearish two-tick three-candle FVG and 0.60 integer ratio qualify.
33. One-tick gap, zero range, or below-0.60 middle body does not qualify.
34. FVG source sequence is exact three contiguous same-segment bar moments.
35. Matching event and FVG direction/end create one context link.
36. Event singleton sequence is exact suffix of FVG sequence; mismatch is invalid.
37. Unmatched FVG/event emits no link; dangling or multiple link is invalid.
38. Opaque DISPLACEMENT ID is deterministic and claims no foreign proof.
39. DISPLACEMENT required/forbidden schema and geometry are exhaustive.
40. Canonical source-bar digest changes on any ordered source/segment mutation.
41. Segment evidence digest binds full nested members, including empty segments.
42. SEED required/forbidden schema, segment order, and hash validation are exhaustive.
43. Exact keyword-only names/defaults, enum values, version, and exports validate.
44. Every public dataclass field, annotation, default, tuple type, and frozen state validates.
45. Dataset `NONE` has no seed; valid empty evidence returns a bound empty seed; `VALID` requires a member.
46. Status/reason precedence, atomic cutoff, nested containment, and no partial seed validate.
47. Repeatability and complete-boundary strictly-later prefix invariance are byte-exact.
48. Corrected per-segment downstream orchestration is compatible; any regression to once-per-dataset calls, global local-index ordering, or unqualified IDs is a STOP condition.

## 23. Promotion, rollback, and stop conditions

Implementation promotion requires all of the following:

- the corrected candidate-evidence proposal independently passes cross-audit
  for per-segment analyzer invocation, segment-aware aggregation, and one-way
  structural-proposal hash binding;
- only the exact three reserved implementation paths change;
- the exact 48 logical cases reconcile with focused test collection;
- focused and full regression suites pass with cache provider disabled;
- checkpoint hashes, byte/line counts, timings, and exact scope evidence reconcile;
- no private acquisition, dataset, training, integration, or runtime surface changes;
- independent code, test, scope, hash, checkpoint, and diff audit passes.

Rollback is deletion of only the three reserved future implementation artifacts,
provided they remain uncommitted and no dependent work has been promoted.
Committed work must be reverted by a new explicit commit; history rewriting is
forbidden.

Immediate STOP conditions include:

- any request to use dataset-global local indices;
- cross-segment detector state or silent sorting;
- inability to reproduce public swing or event identities;
- need for a stronger foreign displacement identity not present in dependencies;
- any detector mutation, enrichment, output rewriting, or look-ahead;
- any label, outcome, prediction, trading, risk, PnL, or training dependency;
- any scope expansion, dependency hash drift, external fixture, or integration wiring;
- any contradiction between this contract and the corrected parent proposal.

## 24. Final bounded conclusion and next single task

The deterministic structural-seed contract and corrected downstream
candidate-evidence orchestration are segment-compatible, but implementation is
not yet authorized. The accepted dataset's local index reset requires the
locked per-segment boundary and makes any once-per-dataset regression unsafe.

The next and only authorized task is an independent documentation-only
cross-audit of exactly:

- `docs/gc_futures_phase_a_structural_seed_evidence_change_proposal.md`;
- `docs/gc_futures_phase_a_candidate_evidence_change_proposal.md`.

That audit must prove segment partitioning, analyzer invocation, aggregation,
foreign-ID recurrence, no-silent-sort behavior, status cutoff, identities,
exact matrices, reserved scopes, one-way document hash binding, and downstream
STOP boundaries. PASS may authorize staging only those exact documentation
files. It must not begin Python, tests, private execution, training, OOS access,
integration, commit, or push. The global code freeze remains active.
