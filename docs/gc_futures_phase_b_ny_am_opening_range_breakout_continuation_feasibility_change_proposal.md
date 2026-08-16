# GC Futures Phase B NY AM Opening Range Breakout Continuation Feasibility Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-OPENING-RANGE-BREAKOUT-CONTINUATION-FEASIBILITY-PROPOSAL-V1`
- Status: `DOCUMENTATION_ONLY_FREEZE_LIFT_PROPOSED`
- Decision date: `2026-08-16`
- Selected hypothesis: `GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1`
- Current repository commit: `c07704c3f832bd951e3e41a15759fffdc798cc45`
- Parent remote baseline: `7e23163b21a77f86ac1b27075bf44c92617f5957`
- Intended use: deterministic development-only occurrence and outcome-feasibility measurement.
- Forbidden use: feature production, model fitting, OOS evaluation, PnL estimation, strategy promotion, paper trading, live trading, or execution.

This record is the only file authorized by the current bounded exception. It
does not implement the hypothesis and does not grant authority to run it on
private data.

## 2. Decision summary

Phase A is accepted as `CLOSED_NEGATIVE`; its V1 setup and continuity rescue are
retired. The next hypothesis is a distinct, fixed-rule GC five-minute opening
range continuation study. The first implementation, if separately authorized,
may answer only whether the locked candidate and outcome sequence is
sufficiently populated and reproducible for a later experiment proposal.

The proposed implementation is a pure, reference-only analyzer. It consumes
immutable canonical dataset, calendar, observation, and Kill-zone evidence. It
does not rebuild the dataset, change a detector output, choose parameters after
seeing outcomes, or create trading decisions.

## 3. Binding repository and decision baseline

The proposal is bound to these exact committed artifacts:

| Artifact | SHA-256 |
|---|---|
| `docs/gc_futures_phase_a_closure_and_phase_b_research_direction_decision.md` | `B3F2FCAEAC3C2FA87CFFF8D85ED43A9DE883033FDF242389FF17BDD2DD59B0CE` |
| `docs/gc_futures_phase_a_cross_segment_continuity_feasibility_negative_outcome_decision.md` | `624E615255019A5F5B6C2F5D11B77594B62493D6ED1E636941B178B29F27704F` |
| `docs/gc_futures_ai_strategy_training_decision.md` | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| `docs/gc_futures_phase_a_next_hypothesis_selection_decision.md` | `77554406D75B81E279409D1D46F3AC44C89FAD6FC08D010D98DA543016B4181E` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

Any dependency, baseline, public-contract, or evidence drift is a STOP
condition. Existing untracked proposals are outside scope and remain frozen.

## 4. Intended use and evidence-fitness gate

The analyzer may measure only:

- requested and eligible trade-date counts;
- exact exclusion and blocking reasons;
- complete candidate count and direction balance;
- contract-month representation;
- deterministic structural outcome counts; and
- exact-prefix and fresh-run reproducibility.

Passing the feasibility gate establishes only that a later feature/label
experiment may be proposed. It does not establish an edge, profitability,
generalization, model readiness, or trading fitness. Structural outcomes are
not trades and have no entry, exit, slippage, commission, risk, or PnL meaning.

## 5. Exact documentation-only scope

This task may create or edit only:

`docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_feasibility_change_proposal.md`

No source, test, fixture, private artifact, requirement, configuration, package
export, runtime, strategy, engine, storage, trace, model, or integration file is
authorized. Before a local commit, rollback is deletion of this one file. After
a local commit, rollback is a bounded revert; history rewriting is forbidden.

## 6. Authority, global freeze, and no-trading boundary

The global code freeze remains active. This proposal grants no implementation,
private-run, training, OOS, integration, stage, commit, push, paper, live, or
execution authority. A later implementation exception must name exactly the
three paths in Section 22.

No AI, local language model, human reviewer, or downstream caller may create,
remove, rank, relabel, or alter candidates. AI may later assist with offline
code review and evidence summarization only under the existing no-trading-
authority provider boundary.

## 7. Exact accepted private input binding

A later separately authorized private feasibility run may read only immutable
copies derived from:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

The accepted development binding is:

- binding version:
  `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID:
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- private input artifact-set identity:
  `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`;
- accepted continuity output artifact-set identity:
  `5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`;
- `17,404` development bars, `133` canonical segments, zero OOS bars;
- first/last development trade dates: `2026-02-23` / `2026-05-22`;
- calendar version:
  `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`;
- split-session calendar digest:
  `5f70052e27655a95fdad6aa69f546a6c84a28743bb6635ca4f55d015c39cad6d`;
- Kill-zone calendar digest:
  `dd16b5734f4dfe54a54c47aa1889302abf92102e6478459b98a8e642732f88f3`;
- timezone-data version: `2026.2`; and
- instrument/timeframe/tick size: `GC` / `5M` / exact `0.1`.

Official calendar source hashes remain exactly
`233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`,
`CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`,
and `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.
The implementation must receive public objects from a caller; it must not read
these paths or discover files implicitly.

## 8. Immutable dependency and import boundary

Allowed direct imports are limited to:

- `GCDatasetBuildConfig`, `GCDatasetBuildResult`, and
  `GCSplitSessionCalendarEntry` from `analysis.gc_dataset_builder`;
- `KillZoneCalendarEntry`, `KillZoneContext`, `KillZoneResult`,
  `KillZoneSnapshot`, and `make_kill_zone_id` from `smc.kill_zones`; and
- `SMCV2Direction` and `SMCV2PrimitiveStatus` from
  `smc.smc_v2_primitives`.

Imported types are not re-exported. Imports from strategy, engine, execution,
storage, decision trace, model, training, order-flow, legacy SMC, FVG,
structure, Volume Profile, Premium/Discount, or other detector modules are
forbidden. The analyzer may validate foreign Kill-zone identities from supplied
public fields but may not rerun, enrich, or mutate the detector.

## 9. Exact enums, constants, and frozen public dataclasses

The future module constant is exactly:

```python
GC_NY_AM_OPENING_RANGE_BREAKOUT_VERSION = "GC-NY-AM-OPENING-RANGE-BREAKOUT-V1"
```

Exact enum values are:

```text
GCNYAMIdentityKind: OBSERVATION, OPENING_RANGE, CANDIDATE, OUTCOME, MANIFEST
GCNYAMOutcomeType: EXTENSION_FIRST, INVALIDATION_FIRST, TIMEOUT,
  SAME_BAR_AMBIGUOUS, INCOMPLETE, INVALID
```

All public dataclasses are frozen and have exactly these fields:

```text
GCNYAMOpeningRangeObservation:
  observation_id: str
  segment_ordinal: int
  segment_id: str
  contract: str
  trade_date: date
  index: int
  bar_open_timestamp: datetime
  bar_close_timestamp: datetime
  open_tick: int
  high_tick: int
  low_tick: int
  close_tick: int
  volume: int
  is_closed: bool
  kill_zone_context_id: str
  kill_zone_snapshot_id: str

GCNYAMOpeningRange:
  range_id: str
  segment_ordinal: int
  segment_id: str
  contract: str
  trade_date: date
  source_observation_ids: tuple[str, ...]
  source_context_ids: tuple[str, ...]
  source_snapshot_ids: tuple[str, ...]
  first_known_index: int
  first_known_timestamp: datetime
  high_tick: int
  low_tick: int
  width_ticks: int

GCNYAMOpeningRangeCandidate:
  candidate_id: str
  range_id: str
  segment_ordinal: int
  segment_id: str
  contract: str
  trade_date: date
  direction: SMCV2Direction
  formation_observation_id: str
  formation_context_id: str
  formation_snapshot_id: str
  formation_index: int
  first_known_timestamp: datetime
  broken_boundary_tick: int
  target_tick: int
  invalidation_tick: int
  width_ticks: int

GCNYAMOpeningRangeOutcome:
  outcome_id: str
  candidate_id: str
  outcome: GCNYAMOutcomeType
  first_known_index: int
  first_known_timestamp: datetime
  horizon_observation_ids: tuple[str, ...]
  event_observation_id: str | None

GCNYAMOpeningRangeManifest:
  manifest_id: str
  version: str
  instrument: str
  timeframe: str
  dataset_id: str
  calendar_version: str
  split_session_calendar_digest: str
  kill_zone_calendar_digest: str
  timezone_name: str
  timezone_data_version: str
  requested_trade_dates: tuple[date, ...]
  opening_range_ids: tuple[str, ...]
  candidate_ids: tuple[str, ...]
  outcome_ids: tuple[str, ...]
  count_funnel: tuple[tuple[str, int], ...]
  reason_counts: tuple[tuple[str, int], ...]

GCNYAMOpeningRangeResult:
  status: SMCV2PrimitiveStatus
  opening_ranges: tuple[GCNYAMOpeningRange, ...] = ()
  candidates: tuple[GCNYAMOpeningRangeCandidate, ...] = ()
  outcomes: tuple[GCNYAMOpeningRangeOutcome, ...] = ()
  manifest: GCNYAMOpeningRangeManifest | None = None
  reasons: tuple[str, ...] = ()
  blocking_reasons: tuple[str, ...] = ()
```

## 10. Exact public exports

The future module export list is exactly:

```python
__all__ = (
    "GC_NY_AM_OPENING_RANGE_BREAKOUT_VERSION",
    "GCNYAMIdentityKind",
    "GCNYAMOutcomeType",
    "GCNYAMOpeningRangeObservation",
    "GCNYAMOpeningRange",
    "GCNYAMOpeningRangeCandidate",
    "GCNYAMOpeningRangeOutcome",
    "GCNYAMOpeningRangeManifest",
    "GCNYAMOpeningRangeResult",
    "make_gc_ny_am_opening_range_breakout_id",
    "analyze_gc_ny_am_opening_range_breakout",
)
```

There is no package-root export, compatibility alias, filesystem loader,
private-data helper, mutable wrapper, configuration object, or convenience
overload in this phase.

## 11. Exact keyword-only public API

The future implementation may expose only:

```python
make_gc_ny_am_opening_range_breakout_id(
    *,
    identity_kind: GCNYAMIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    split_session_calendar_digest: str,
    kill_zone_calendar_digest: str,
    timezone_name: str,
    timezone_data_version: str,
    tick_size: Decimal,
    segment_ordinal: int | None = None,
    segment_id: str | None = None,
    contract: str | None = None,
    trade_date: date | None = None,
    index: int | None = None,
    bar_open_timestamp: datetime | None = None,
    bar_close_timestamp: datetime | None = None,
    open_tick: int | None = None,
    high_tick: int | None = None,
    low_tick: int | None = None,
    close_tick: int | None = None,
    volume: int | None = None,
    is_closed: bool | None = None,
    kill_zone_context_id: str | None = None,
    kill_zone_snapshot_id: str | None = None,
    source_observation_ids: tuple[str, ...] = (),
    source_context_ids: tuple[str, ...] = (),
    source_snapshot_ids: tuple[str, ...] = (),
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    range_id: str | None = None,
    direction: SMCV2Direction | None = None,
    formation_observation_id: str | None = None,
    formation_context_id: str | None = None,
    formation_snapshot_id: str | None = None,
    formation_index: int | None = None,
    broken_boundary_tick: int | None = None,
    target_tick: int | None = None,
    invalidation_tick: int | None = None,
    width_ticks: int | None = None,
    candidate_id: str | None = None,
    outcome: GCNYAMOutcomeType | None = None,
    horizon_observation_ids: tuple[str, ...] = (),
    event_observation_id: str | None = None,
    requested_trade_dates: tuple[date, ...] = (),
    opening_range_ids: tuple[str, ...] = (),
    candidate_ids: tuple[str, ...] = (),
    outcome_ids: tuple[str, ...] = (),
    count_funnel: tuple[tuple[str, int], ...] = (),
    reason_counts: tuple[tuple[str, int], ...] = (),
) -> str

analyze_gc_ny_am_opening_range_breakout(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    observations: tuple[GCNYAMOpeningRangeObservation, ...] | None,
    split_session_calendar_entries: tuple[GCSplitSessionCalendarEntry, ...] | None,
    kill_zone_calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    kill_zone_result: KillZoneResult | None,
    requested_trade_dates: tuple[date, ...] | None,
) -> GCNYAMOpeningRangeResult
```

Positional arguments, alternate names/defaults, hidden inputs, caller-selected
thresholds, caller-selected windows, or an `as_of` added after evidence
selection are forbidden.

## 12. Canonical dataset and observation reconciliation

`dataset_config` must be exact GC / 5M / Asia-Tokyo source /
America-New_York exchange / `0.1` tick evidence and its timezone-data version
must match runtime and every calendar/context identity. The dataset must be
`VALID`, have a non-null manifest and dataset ID, contain development segments
only for requested dates, and contain no contacted OOS bars.

Observations are a caller-supplied immutable projection, not an alternative
price source. Every observation must map one-to-one to the canonical
`GCChronologicalBar` at its exact segment ordinal, segment ID, contract, index,
UTC close timestamp, OHLC integer ticks, volume, and fully closed state. Its
open timestamp is exactly close minus five minutes. Segment ordinals, bar
indices, and both normalized timestamps are strictly increasing in accepted
dataset order. Duplicate, reordered, missing, forked, cross-segment, or
unreconciled observations are `INVALID`; nothing is silently sorted.

OHLC must satisfy `low_tick <= open_tick, close_tick <= high_tick`, boolean
ticks are forbidden, volume is an integer greater than or equal to zero, and
all timestamps are timezone-aware. An observation ID must recompute from its
complete supplied public payload.

## 13. Split-session calendar and Kill-zone reconciliation

The split-session calendar and Kill-zone calendar are separate ordered tuples.
Each independently uses unique increasing trade dates and one exact calendar
version. Their complete canonical tuple digests are identity-bearing and must
match Section 7 for the accepted private run.

For every requested trade date, the split-session interval containing the six
source bars, candidate window, and complete twelve-bar horizon must exist. A
holiday or session-closed date is ineligible with an exact reason. An early
close that prevents complete source or outcome coverage is ineligible, not
silently truncated. Missing calendar evidence is `UNKNOWN`; determinably
malformed supplied evidence is `INVALID` and outranks missing context.

Every source, formation, and future-horizon observation must reference a
canonical `NEW_YORK_AM`, `VERIFIED`, matching-trade-date `KillZoneContext` and a
`KillZoneSnapshot` whose ordered context IDs include that exact context.
The context's `observation_index` equals the bar index and its
`observation_timestamp` equals the bar-open timestamp; this lets the exact
`09:55` horizon bar remain start-inclusive/end-exclusive New York AM evidence
even though that bar becomes closed at `10:00`. The corresponding snapshot has
the same effective index and timestamp. Context and snapshot IDs are
recomputed with `make_kill_zone_id`. Equal-moment snapshot order mirrors
observation order; hash lexical order is not a causal tie-break. The analyzer
does not synthesize missing contexts.

## 14. Exact opening-range construction

For one eligible trade date, exactly six fully closed bars with New York local
open times `07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and `07:25` form the
range. They must be consecutive observations in one canonical segment,
contract, trade date, split-session interval, and verified New York AM context.

The range becomes first-known at exact `07:30:00 America/New_York`, equal to
the sixth source bar close. Its high is the maximum source `high_tick`, low is
the minimum source `low_tick`, and width is `high_tick - low_tick`. Width must
be a positive integer. Source observation, context, and snapshot ID tuples are
ordered, length six, unique, immutable, and identity-bearing.

A missing, duplicate, substituted, cross-date, cross-contract, nonconsecutive,
non-closed, context-invalid, calendar-ineligible, or zero-width source group
promotes no range.

## 15. Exact candidate eligibility and deterministic selection

Candidate bars have New York local open timestamps in start-inclusive,
end-exclusive `[07:30, 09:00)`. The first canonical qualifying close wins:

- bullish: `close_tick >= range.high_tick + 1`;
- bearish: `close_tick <= range.low_tick - 1`.

Boundary equality and wick-only breaks do not qualify. At most one candidate
exists per requested trade date; later breakouts cannot replace or rank above
the first. Candidate first-known time is the formation bar close.

The formation bar is rejected as `FORMATION_OUTCOME_COLLISION` if bullish
`high_tick >= target_tick` or `low_tick <= invalidation_tick`, or bearish
`low_tick <= target_tick` or `high_tick >= invalidation_tick`. No later evidence
may rehabilitate that formation.

Output order is exact `(trade_date, segment_ordinal, formation_index,
normalized first_known_timestamp, direction.value)`. Exact duplicates collapse
only after complete payload equality. Same-effective distinct candidates,
opposing qualifying interpretations, or forked observations are fail-closed;
hash order never selects a winner.

## 16. Immutable candidate geometry

Bullish geometry is:

- broken boundary: range high;
- target: `range high + width`;
- invalidation: range low.

Bearish geometry is:

- broken boundary: range low;
- target: `range low - width`;
- invalidation: range high.

Range ID, direction, segment, contract, trade date, formation observation and
context, formation index, first-known moment, broken boundary, width, target,
and invalidation are immutable. Candidate identity contains no future bar,
outcome, feature, score, PnL, or model evidence.

## 17. Exact outcome and first-known contract

The horizon is exactly twelve fully closed, consecutive observations strictly
after formation, in the same canonical segment, contract, trade date, eligible
session, and verified context. The formation bar is never evaluated as an
outcome bar.

- `EXTENSION_FIRST`: target touch occurs before invalidation close;
- `INVALIDATION_FIRST`: opposite range-boundary close occurs before target;
- `TIMEOUT`: neither occurs through the twelfth future bar;
- `SAME_BAR_AMBIGUOUS`: both occur in the same future bar;
- `INCOMPLETE`: twelve future bars are not yet supplied; and
- `INVALID`: future evidence is malformed or unreconciled.

Target touch is bullish `high_tick >= target_tick` and bearish
`low_tick <= target_tick`. Invalidation is bullish
`close_tick <= invalidation_tick` and bearish
`close_tick >= invalidation_tick`. First-known time for an event is that event
bar close; `TIMEOUT` is first-known at the twelfth bar close.

Only the four complete terminal outcomes are promoted as
`GCNYAMOpeningRangeOutcome`. `INCOMPLETE` and `INVALID` remain exact count/reason
classifications and promote no outcome object, preventing later appends from
rewriting an immutable prior outcome.

## 18. Exhaustive deterministic identity schemas

All IDs are lowercase SHA-256 over canonical typed JSON with sorted keys,
compact separators, UTC-normalized timestamps, ISO dates, canonical Decimal
tick size, ordered arrays, and no float coercion. Every kind requires the common
instrument, timeframe, dataset ID, calendar version, both calendar digests,
timezone name, timezone-data version, and tick size.

`OBSERVATION` additionally requires segment ordinal/ID, contract, trade date,
index, bar open/close timestamps, OHLC ticks, volume, exact `is_closed=True`,
and context/snapshot IDs. It forbids every range, candidate, outcome, and
manifest field.

`OPENING_RANGE` requires segment ordinal/ID, contract, trade date, exact six
source observation/context/snapshot IDs, first-known index/timestamp, high,
low, and positive width. The builder validates hash shape, tuple lengths,
uniqueness, exact first-known and range geometry available in this payload. The
analyzer, which has the complete public observations, recomputes every source
observation ID before calling the builder. It forbids standalone observation
fields and every candidate, outcome, and manifest field.

`CANDIDATE` requires range ID, segment ordinal/ID, contract, trade date,
direction, formation observation/context/snapshot IDs, formation index,
first-known timestamp, broken boundary, target, invalidation, and width. It
validates hash shape and exact direction-specific geometry available in this
payload. The analyzer recomputes the referenced range, formation observation,
context, and snapshot IDs from complete public objects before calling the
builder. It forbids range source arrays, standalone bar fields, outcome fields,
and manifest fields.

`OUTCOME` requires candidate ID, one of the four promotable terminal outcome
values, first-known index/timestamp, one-to-twelve ordered unique horizon
observation IDs, and event observation ID exactly when the outcome is not
`TIMEOUT`. `TIMEOUT` requires exactly twelve horizon IDs and forbids an event
ID. The builder validates hash shape, tuple shape, terminal-kind requirements,
and available first-known fields. The analyzer recomputes candidate and horizon
observation identities and validates event/horizon/first-known reconciliation
before calling the builder. It rejects `INCOMPLETE` and `INVALID` identity
creation.

`MANIFEST` requires unique increasing requested trade dates, exact ordered
range/candidate/outcome IDs, deterministic count funnel, and deterministic
reason counts. The analyzer recomputes every ID from supplied public objects
and requires each to occur once in output order before calling the builder. The
builder validates hash shape, uniqueness, ordering, counts, and the supplied
manifest payload. It forbids all object-specific fields.

Unknown kinds, absent required fields, present forbidden fields, malformed
hashes, bool-as-int values, naive timestamps, bad enum types, duplicate arrays,
noncanonical Decimal, nested malformed values, or impossible reconciliation
raise only `TypeError` or `ValueError` without exception leakage.

## 19. Chronology, atomic processing, cutoff, and prefix invariance

Inputs are complete tuples and are never silently sorted. Processing is by
complete `(trade_date, segment_ordinal, index, normalized close timestamp)`
groups. No object is promoted from a partial or failing group.

A determinably later malformed group produces final `INVALID`, preserves every
strictly prior valid public object byte-for-byte, and promotes nothing from the
failing group onward. An unknowable malformed effective moment requires no
trustworthy prefix. Same-effective append, historical insertion, correction,
reordering, calendar change, dataset change, or contract remap is not a valid
prefix comparison.

For any valid prefix ending on a complete effective-group boundary and any
strictly later complete append, prior ranges, candidates, and complete outcomes
are byte-equal. Full-history extraction equals exact-prefix extraction for each
promoted object. Pending `INCOMPLETE` evidence promotes no outcome and cannot be
misrepresented as a complete prefix result.

## 20. Status precedence, reporting, and feasibility gate

Exact result precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Malformed supplied counterpart evidence outranks a missing top-level tuple.
Independent valid objects remain preserved when a later pending group produces
`UNKNOWN`; pending evidence promotes no outcome. `AMBIGUOUS` is used only when
multiple nonidentical fully canonical segment interpretations remain for the
same requested trade date and effective moment after all available foreign
identities validate; supplied duplicate IDs, forks, contradictions, or bad
ordering are `INVALID`, not `AMBIGUOUS`.

`UNKNOWN` means required dataset, calendar, Kill-zone, source-range, or complete
future-horizon evidence is unavailable without independently determinable
invalid evidence. `VALID` requires at least one complete candidate with one
promoted terminal outcome and no higher status. `NONE` means a nonempty
explicitly requested, fully covered scope has no calendar-eligible trade date
or contains complete range assessments but no qualifying breakout. Empty
`requested_trade_dates=()` is also `NONE` only when every other supplied
evidence tuple is exactly empty; unrequested supplied evidence is `INVALID`.
`requested_trade_dates=None` is missing context and therefore `UNKNOWN` unless
a malformed supplied counterpart raises `INVALID`.

The manifest count-funnel keys and order are exactly:
`REQUESTED_TRADE_DATES`, `CALENDAR_ELIGIBLE_TRADE_DATES`,
`COMPLETE_OPENING_RANGES`, `NO_BREAKOUT_TRADE_DATES`,
`FORMATION_OUTCOME_COLLISIONS`, `COMPLETE_CANDIDATES`,
`BULLISH_CANDIDATES`, `BEARISH_CANDIDATES`, `COMPLETE_OUTCOMES`,
`INCOMPLETE_HORIZONS`, `INVALID_GROUPS`, `AMBIGUOUS_GROUPS`.

The only result reason tokens are:
`MISSING_TOP_LEVEL_CONTEXT`, `INVALID_DATASET`, `OOS_CONTACT`,
`UNREQUESTED_EVIDENCE`, `INVALID_OBSERVATION`,
`MISSING_SPLIT_SESSION_CALENDAR`, `INVALID_SPLIT_SESSION_CALENDAR`,
`MISSING_KILL_ZONE_CALENDAR`, `INVALID_KILL_ZONE_CALENDAR`,
`MISSING_KILL_ZONE_EVIDENCE`, `INVALID_KILL_ZONE_EVIDENCE`,
`SESSION_INELIGIBLE`, `INCOMPLETE_OPENING_RANGE`,
`INVALID_OPENING_RANGE`, `NO_BREAKOUT`, `FORMATION_OUTCOME_COLLISION`,
`INCOMPLETE_OUTCOME_HORIZON`, `INVALID_OUTCOME_EVIDENCE`, and
`AMBIGUOUS_CANONICAL_INTERPRETATION`. Reason counts are unique and ordered by
this vocabulary, not lexical or discovery order; free-text variation is
forbidden.

A manifest is promoted only for a complete final `VALID` or `NONE` result. A
final `INVALID`, `AMBIGUOUS`, or `UNKNOWN` result has `manifest=None`, retains
strictly prior valid public objects as required by Section 19, and reports its
deterministic reason/blocking tokens without presenting a partial funnel as a
complete run.

Private feasibility PASS requires at least `40` complete candidates on at least
`40` distinct eligible dates, at least `10` bullish and `10` bearish complete
candidates, at least `3` canonical GC contracts, `100%` identity/count/status/
reason/byte reproducibility across two fresh runs, zero silent exclusion, and a
complete requested-date funnel. PASS authorizes only a later feature/label
proposal. FAIL retires this V1 without threshold, window, geometry, horizon, or
gate rescue.

## 21. Inline synthetic exact 48-case acceptance matrix

Future tests must preserve exactly these logical cases; parameterization may
increase collected tests without changing the logical count:

1. Missing bars and missing calendar produce fail-closed `UNKNOWN` with no range.
2. A malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
3. Non-tuple, duplicate, reordered, or same-index forked observations are rejected.
4. Boolean, fractional, non-finite, negative-volume, or malformed values fail closed.
5. Naive timestamps and timezone/version mismatch fail closed.
6. Non-GC, spot, CFD, option, micro, or ambiguous contract inputs are rejected.
7. Non-5m, non-closed, pseudo-MTF, or cross-contract source bars are rejected.
8. Missing, holiday, session-closed, or inapplicable calendar evidence is fail-closed.
9. An early close preventing complete source or horizon coverage is ineligible with an exact reason.
10. Exact six source bars at `07:00` through `07:25` form one range at `07:30`.
11. Five bars are insufficient and a seventh bar cannot enter the source tuple.
12. Missing middle source, timestamp substitution, or nonconsecutive index is invalid.
13. Cross-trade-date, cross-segment, or cross-session source membership is invalid.
14. Positive one-tick width is valid and zero width is invalid.
15. Integer extrema and width remain exact under arbitrary Decimal context.
16. Strictly pre-`07:30` breakout evidence cannot create a candidate.
17. Exact `07:30` candidate-window start is eligible.
18. Exact `09:00` bar-open timestamp is ineligible.
19. Exact `10:00` New York AM end is never a candidate or label bar.
20. Bullish exact one-tick close breakout qualifies.
21. Bearish exact one-tick close breakout qualifies.
22. Boundary-equality close is not a breakout.
23. Wick-only breakout without qualifying close is not a candidate.
24. Earliest qualifying bar wins and later bars cannot replace it.
25. One candidate maximum per trade date and multi-date ordering are deterministic.
26. Formation-bar target touch is rejected as `FORMATION_OUTCOME_COLLISION`.
27. Formation-bar opposite-boundary traversal is rejected as `FORMATION_OUTCOME_COLLISION`.
28. Bullish target, invalidation, and width geometry reconcile exactly.
29. Bearish target, invalidation, and width geometry reconcile exactly.
30. Observation, range, and candidate identities cover every required, forbidden, and sensitive field.
31. Outcome and manifest identities cover every required, forbidden, ordered-history, and sensitive field.
32. Strictly later bullish target touch produces `EXTENSION_FIRST`.
33. Strictly later bearish target touch produces `EXTENSION_FIRST`.
34. Bullish opposite-boundary close produces `INVALIDATION_FIRST`.
35. Bearish opposite-boundary close produces `INVALIDATION_FIRST`.
36. Twelve complete bars without either boundary produce `TIMEOUT`.
37. Fewer than twelve later bars produce `INCOMPLETE` without outcome promotion or relabeling.
38. Same-bar target and invalidation produce `SAME_BAR_AMBIGUOUS`.
39. Formation bar is excluded and event first-known moment is exact.
40. Full-history and exact-prefix promoted object bytes are equal.
41. Strictly later complete append preserves prior evidence byte-for-byte.
42. Same-effective append, historical repair, reorder, calendar mutation, or dataset mutation is prefix-ineligible.
43. Determinably later malformed evidence preserves only strictly prior valid evidence.
44. `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence is exact.
45. Kill-zone IDs, snapshot mirroring, both calendar digests, and dataset bars reconcile completely.
46. Diagnostic/OFF/baseline detector evidence cannot create, remove, rank, or relabel a candidate.
47. Two fresh executions reproduce identities, counts, statuses, reasons, manifests, and bytes.
48. Exact frozen API/exports, three-path scope, forbidden imports, rollback, and no private run/training/OOS/integration pass.

## 22. Reserved future implementation and private-run scope

Only a separate explicit authorization may lift the freeze for exactly:

- `analysis/gc_ny_am_opening_range_breakout.py`
- `tests/test_gc_ny_am_opening_range_breakout.py`
- `docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_checkpoint.md`

No external fixture is permitted; tests use inline synthetic records. The
private accepted artifacts remain outside Git and cannot be copied into source,
tests, docs, checkpoints, commits, or remote storage. Implementation does not
authorize a private run. A later private-run proposal must bind exact committed
implementation hashes, private input identities, output directory, atomic
temporary-to-final publication, two fresh runs, and independent audit before
execution.

## 23. Acceptance, promotion, rollback, and STOP conditions

Documentation acceptance requires exactly 24 sequential numbered sections,
exactly 48 sequential logical cases, exhaustive immutable/API/identity/status/
chronology contracts, exact one-file scope, zero formatting error, baseline
regression PASS, and an exact SHA-256 recorded at staging.

Fresh cache-disabled baseline-preservation evidence on `2026-08-16` is:

- focused `tests/test_gc_cross_segment_continuity.py`:
  `48 passed in 0.62s`; and
- full explicit `tests` suite: `2346 passed in 13.59s`.

These regressions do not test the proposed Phase B analyzer; they prove only
that this documentation-only task did not alter the accepted code baseline.

Implementation promotion requires test-first coverage of all 48 logical cases,
focused and full regression PASS with pytest cache disabled, exact three-path
scope, artifact hashes and byte/line counts, no external fixture, and an
independent final audit. It still grants no private run.

STOP on baseline or dependency drift, ambiguous public contract, unavailable
canonical observation/calendar/context proof, data mutation, silent sorting or
exclusion, non-determinism, Phase A V1 rescue, more than one setup, parameter
revision after outcomes, private evidence publication, OOS contact, feature or
label table production, PnL, training, model dependency, integration, execution,
test failure, scope drift, or remote publication without exact authority.

Before implementation commit, rollback is removal of only the reserved three
paths. After commit, rollback requires a bounded revert; source evidence,
negative results, and history may not be deleted or rewritten.

## 24. Final decision and next single task

The exact proposal decision is:

`PROPOSE_PHASE_B_GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1_FEASIBILITY_IMPLEMENTATION`

This document specifies one deterministic feasibility analyzer and nothing
else. It neither implements nor runs it. If this document passes independent
semantic/structural audit and is separately accepted, the next single task is
test-first implementation within the exact three paths in Section 22. No
private run, feature/label experiment, training, OOS evaluation, integration,
paper trading, or live trading may begin from this decision alone.
