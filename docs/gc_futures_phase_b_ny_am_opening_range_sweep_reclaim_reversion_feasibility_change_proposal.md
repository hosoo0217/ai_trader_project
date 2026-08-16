# GC Futures Phase B NY AM Opening Range Sweep-Reclaim Reversion Feasibility Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-FEASIBILITY-PROPOSAL-V1`
- Status: `DOCUMENTATION_ONLY_FREEZE_LIFT_PROPOSED`
- Decision date: `2026-08-16`
- Selected hypothesis: `GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_V1`
- Current repository commit: `11d36df20627bc613396bc00b192a53720183f49`
- Parent remote baseline: `24eddfe44b4b8d7e379bdcc3f302d3c8b30b9906`
- Intended use: deterministic development-only occurrence and structural-outcome feasibility measurement.
- Forbidden use: feature or label production, model fitting, OOS evaluation, PnL estimation, strategy promotion, paper trading, live trading, or execution.

This record is the only file authorized by the current bounded exception. It
does not implement the hypothesis and does not grant authority to run it on
private data.

## 2. Decision summary

The opening-range breakout-continuation V1 feasibility run is accepted as a
preserved negative result and is not eligible for rescue. The selected next and
final setup family on the current accepted dataset is a fixed-rule New York AM
opening-range sweep, same-bar reclaim, and midpoint-reversion study.

The first implementation, if separately authorized, may answer only whether
the locked sequence is sufficiently populated, directionally represented, and
reproducible for a later experiment proposal. It is a pure reference-only
analyzer: it consumes immutable canonical dataset, split-session calendar,
observation, and Kill-zone evidence and does not rebuild data, mutate detector
outputs, tune rules after outcomes, or produce trading decisions.

## 3. Binding repository and decision baseline

The proposal is bound to these exact artifacts:

| Artifact | SHA-256 |
|---|---|
| `docs/gc_futures_phase_b_next_hypothesis_selection_decision.md` | `889CB2DA4FB107AC05A6D9B2395A9FB7E03595C40162339000731B5BAE113AC7` |
| `docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_private_run_stop_record.md` | `5A22CA6DFABD0722B71643FE6E9470D7AB10030CA3C117246E0A67739C6B2A52` |
| `docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_feasibility_change_proposal.md` | `75A049329783501E779AFBA1F198A7BA2BA7C25C7986C601F9D64A7A5BDCA291` |
| `docs/gc_futures_ai_strategy_training_decision.md` | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

Any dependency, baseline, public-contract, or evidence drift is a STOP
condition. Existing unrelated untracked proposals are outside scope and remain
frozen.

## 4. Intended use and evidence-fitness gate

The analyzer may measure only:

- requested, eligible, and fully assessed trade-date counts;
- exact exclusion, blocking, ambiguity, and invalidity reasons;
- complete candidate count, bullish/bearish balance, and contract representation;
- deterministic midpoint, invalidation, same-bar ambiguity, and timeout outcomes;
- chronological cutoff and immutable prior-evidence behavior; and
- exact-prefix and fresh-run reproducibility.

Passing the feasibility gate establishes only that a later feature/label
experiment may be proposed. It does not establish edge, profitability,
generalization, model readiness, or trading fitness. Structural outcomes are
not trades and have no entry, exit, slippage, commission, risk, or PnL meaning.

## 5. Exact documentation-only scope

This task may create or edit only:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_change_proposal.md`

No source, test, fixture, private artifact, requirement, configuration, package
export, runtime, strategy, engine, storage, trace, model, training, or
integration file is authorized. Before a local commit, rollback is deletion of
this one file. After a local commit, rollback is a bounded revert; history
rewriting is forbidden.

## 6. Authority, global freeze, and no-trading boundary

The global code freeze remains active. This proposal grants no implementation,
private-run, feature/label build, training, OOS, integration, push, paper, live,
or execution authority. A later implementation exception must name exactly the
three paths in Section 22.

No AI, local language model, human reviewer, or downstream caller may create,
remove, rank, relabel, or alter candidates. AI may assist only with offline code
review and evidence summarization under the existing no-trading-authority
provider boundary.

## 7. Exact accepted private input binding

A later separately authorized private feasibility run may read only immutable
copies derived from:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

The accepted development binding is exactly:

- binding version:
  `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID:
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- private input artifact-set identity:
  `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`;
- accepted continuity output artifact-set identity:
  `5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`;
- `17,404` development bars, `133` canonical segments, and zero OOS bars;
- first/last development trade dates: `2026-02-23` / `2026-05-22`;
- exact contracts: `GCJ26-COMEX` and `GCM26-COMEX` only;
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
The implementation receives public objects from its caller; it must not read
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
public fields but may not rerun, enrich, or mutate that detector.

## 9. Exact enums, constants, and frozen public dataclasses

The future module constant is exactly:

```python
GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION = "GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1"
```

Exact enum values are:

```text
GCNYAMSweepReclaimIdentityKind: OBSERVATION, OPENING_RANGE, CANDIDATE,
  OUTCOME, MANIFEST
GCNYAMSweepReclaimOutcomeType: MIDPOINT_REACHED, INVALIDATED, TIMEOUT,
  SAME_BAR_AMBIGUOUS, INCOMPLETE, INVALID
```

All public dataclasses are frozen and have exactly these fields:

```text
GCNYAMSweepReclaimObservation:
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

GCNYAMSweepReclaimOpeningRange:
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
  midpoint_tick: Decimal
  width_ticks: int

GCNYAMSweepReclaimCandidate:
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
  swept_boundary_tick: int
  sweep_extreme_tick: int
  reclaim_close_tick: int
  midpoint_tick: Decimal
  invalidation_tick: int
  width_ticks: int

GCNYAMSweepReclaimOutcome:
  outcome_id: str
  candidate_id: str
  outcome: GCNYAMSweepReclaimOutcomeType
  first_known_index: int
  first_known_timestamp: datetime
  horizon_observation_ids: tuple[str, ...]
  event_observation_id: str | None

GCNYAMSweepReclaimManifest:
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

GCNYAMSweepReclaimResult:
  status: SMCV2PrimitiveStatus
  opening_ranges: tuple[GCNYAMSweepReclaimOpeningRange, ...] = ()
  candidates: tuple[GCNYAMSweepReclaimCandidate, ...] = ()
  outcomes: tuple[GCNYAMSweepReclaimOutcome, ...] = ()
  manifest: GCNYAMSweepReclaimManifest | None = None
  reasons: tuple[str, ...] = ()
  blocking_reasons: tuple[str, ...] = ()
```

No public field, default, mutable collection, alias, optional enrichment, or
unversioned payload is permitted.

## 10. Exact public exports

`__all__` is exact and ordered:

```text
GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_VERSION
GCNYAMSweepReclaimIdentityKind
GCNYAMSweepReclaimOutcomeType
GCNYAMSweepReclaimObservation
GCNYAMSweepReclaimOpeningRange
GCNYAMSweepReclaimCandidate
GCNYAMSweepReclaimOutcome
GCNYAMSweepReclaimManifest
GCNYAMSweepReclaimResult
make_gc_ny_am_sweep_reclaim_id
analyze_gc_ny_am_opening_range_sweep_reclaim_reversion
```

There is no package-root re-export, compatibility alias, strategy hook, or
runtime registration in this bounded task.

## 11. Exact keyword-only public API

The deterministic identity builder is exactly keyword-only:

```python
make_gc_ny_am_sweep_reclaim_id(
    *,
    identity_kind,
    instrument,
    timeframe,
    dataset_id,
    calendar_version,
    split_session_calendar_digest,
    kill_zone_calendar_digest,
    timezone_name,
    timezone_data_version,
    segment_ordinal=None,
    segment_id=None,
    contract=None,
    trade_date=None,
    index=None,
    bar_open_timestamp=None,
    bar_close_timestamp=None,
    open_tick=None,
    high_tick=None,
    low_tick=None,
    close_tick=None,
    volume=None,
    is_closed=None,
    kill_zone_context_id=None,
    kill_zone_snapshot_id=None,
    source_observation_ids=None,
    source_context_ids=None,
    source_snapshot_ids=None,
    first_known_index=None,
    first_known_timestamp=None,
    midpoint_tick=None,
    width_ticks=None,
    range_id=None,
    direction=None,
    formation_observation_id=None,
    formation_context_id=None,
    formation_snapshot_id=None,
    formation_index=None,
    swept_boundary_tick=None,
    sweep_extreme_tick=None,
    reclaim_close_tick=None,
    invalidation_tick=None,
    candidate_id=None,
    outcome=None,
    horizon_observation_ids=None,
    event_observation_id=None,
    version=None,
    requested_trade_dates=None,
    opening_range_ids=None,
    candidate_ids=None,
    outcome_ids=None,
    count_funnel=None,
    reason_counts=None,
)
```

The analyzer is exactly keyword-only:

```python
analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(
    *,
    instrument,
    timeframe,
    dataset_config,
    dataset_result,
    requested_trade_dates,
    split_session_calendar,
    kill_zone_calendar,
    observations,
    kill_zone_contexts,
    kill_zone_snapshots,
    kill_zone_result,
)
```

All supplied collections are `tuple[...] | None`; no iterable coercion, silent
sort, default data discovery, `**kwargs`, positional parameter, or hidden global
state is permitted. Unknown identity kinds and noncanonical optional-field
combinations raise only `TypeError` or `ValueError`.

## 12. Canonical dataset and observation reconciliation

`dataset_config` and `dataset_result` must exactly bind Section 7: instrument,
timeframe, tick size, calendar version, timezone-data version, development-only
partition, dataset identity, requested dates, accepted contracts, canonical
segments, and zero OOS contact. Dataset-builder foreign identities are
recomputed only from available public fields.

Observations are immutable, fully closed integer-tick/integer-volume summaries.
Booleans are invalid integers. Required strings and hashes are nonempty and
canonical; timestamps are timezone-aware, normalized to UTC for identity, and
obey `bar_open_timestamp < bar_close_timestamp` with exact five-minute length.
OHLC geometry is `low <= open,close <= high`; volume is nonnegative. Index and
normalized open timestamp are each independently strictly increasing.

Canonical observation order is exactly
`(segment_ordinal, index, normalized bar_open_timestamp, observation_id)`.
The caller must supply that order; the analyzer does not sort. Segment IDs,
contract, trade date, and calendar membership reconcile to the dataset result.
Exact duplicates may collapse only after byte-equivalent canonical payload
comparison; duplicate IDs with different content, same-index forks, or
cross-segment substitutions are `INVALID`.

## 13. Split-session calendar and Kill-zone reconciliation

The split-session calendar and Kill-zone calendar are separate ordered tuples.
Each independently uses unique increasing trade dates and one exact calendar
version. Their complete canonical tuple digests are identity-bearing and must
match Section 7.

For every requested trade date, the split-session interval containing the six
source bars, formation window, and complete twelve-bar horizon must exist. A
holiday or session-closed date is ineligible with an exact reason. An early
close preventing complete source or outcome coverage is ineligible, not
silently truncated. Missing calendar evidence is `UNKNOWN`; determinably
malformed supplied evidence is `INVALID` and outranks missing context.

Every source, formation, and future-horizon observation must reference a
canonical `NEW_YORK_AM`, `VERIFIED`, matching-trade-date `KillZoneContext` and a
`KillZoneSnapshot` whose ordered context IDs include that exact context. The
context `observation_index` equals the bar index and its
`observation_timestamp` equals the bar-open timestamp. The corresponding
snapshot has the same effective index and timestamp. Context and snapshot IDs
are recomputed with `make_kill_zone_id`. Equal-moment snapshot order mirrors
observation order; hash lexical order is not a causal tie-break. Missing
contexts are never synthesized.

## 14. Exact opening-range construction

For one eligible trade date, exactly six fully closed bars with New York local
open times `07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and `07:25` form the
range. They are consecutive observations in one canonical segment, contract,
trade date, split-session interval, and verified New York AM context.

The range becomes first-known at exact `07:30:00 America/New_York`, equal to
the sixth source bar close. Its high is the maximum source `high_tick`, its low
is the minimum source `low_tick`, width is `high_tick - low_tick`, and midpoint
is mathematically exact `(high_tick + low_tick) / 2` as a `Decimal` serialized
canonically as integer `.0` or half-tick `.5`. Any zero is `0.0`. Decimal
context precision and signed zero cannot affect values or identities. Width
must be a positive integer.

Source observation, context, and snapshot ID tuples are ordered, unique,
immutable, equal-length, and exactly six members. A missing, duplicate,
substituted, cross-date, cross-contract, nonconsecutive, non-closed,
context-invalid, calendar-ineligible, or zero-width source group promotes no
range.

## 15. Exact candidate eligibility and deterministic selection

Formation bars have New York local open timestamps in start-inclusive,
end-exclusive `[07:30, 09:00)`. A qualifying upper sweep requires both:

- `high_tick >= range.high_tick + 1`; and
- `range.midpoint_tick < close_tick <= range.high_tick`.

It creates a bearish candidate. A qualifying lower sweep requires both:

- `low_tick <= range.low_tick - 1`; and
- `range.low_tick <= close_tick < range.midpoint_tick`.

It creates a bullish candidate. Midpoint equality is a noncandidate. Closing
outside the range is a noncandidate, and a later bar may not relabel that prior
sweep as a delayed reclaim. Proximal touch, wick-only evidence without same-bar
reclaim, and excursion smaller than one tick do not qualify.

If one complete same-effective bar sweeps both boundaries, the group is
`AMBIGUOUS_SWEEP_RECLAIM`, promotes no candidate, and hash/direction ordering
cannot choose a side. Otherwise the earliest qualifying formation bar wins.
At most one candidate exists per requested trade date. Once selected, later
bars are outcome evidence only and cannot replace the candidate or create a
candidate conflict. Candidate first-known time is the formation bar close.

Exact duplicate evidence collapses only after complete payload equality.
Distinct same-index forks, contradictory context evidence, or multiple
nonidentical canonical interpretations that are not the locked both-boundary
case are `INVALID`.

## 16. Immutable candidate geometry

For a bearish candidate:

- `swept_boundary_tick == range.high_tick`;
- `sweep_extreme_tick == formation.high_tick` and is at least boundary `+ 1`;
- `midpoint_tick < reclaim_close_tick <= swept_boundary_tick`;
- the implied opposite boundary is `swept_boundary_tick - width_ticks`;
- `midpoint_tick` exactly bisects the implied boundaries; and
- `invalidation_tick == sweep_extreme_tick + 1`.

For a bullish candidate:

- `swept_boundary_tick == range.low_tick`;
- `sweep_extreme_tick == formation.low_tick` and is at most boundary `- 1`;
- `swept_boundary_tick <= reclaim_close_tick < midpoint_tick`;
- the implied opposite boundary is `swept_boundary_tick + width_ticks`;
- `midpoint_tick` exactly bisects the implied boundaries; and
- `invalidation_tick == sweep_extreme_tick - 1`.

Range and candidate geometry are immutable after first-known time. The public
builder validates these relationships without foreign object lookup, handles
arbitrary-magnitude positive/negative ticks independent of Decimal context, and
raises only `TypeError` or `ValueError` for impossible geometry.

## 17. Exact outcome and first-known contract

The formation bar never participates in outcome measurement. The outcome
horizon is the next exact twelve fully closed, consecutive observations from
the same canonical segment, contract, trade date, split-session interval, and
verified New York AM context.

For a bearish candidate:

- target evidence is `low_tick <= candidate.midpoint_tick`; and
- invalidation evidence is `close_tick >= candidate.invalidation_tick`.

For a bullish candidate:

- target evidence is `high_tick >= candidate.midpoint_tick`; and
- invalidation evidence is `close_tick <= candidate.invalidation_tick`.

The earliest terminal evidence wins. Target-only produces `MIDPOINT_REACHED`;
invalidation-only produces `INVALIDATED`. If both occur on the same earliest
bar, the deterministic structural result is `SAME_BAR_AMBIGUOUS`; no intrabar
ordering is inferred. If twelve complete bars contain neither event, the
twelfth close produces `TIMEOUT`. If fewer than twelve later bars exist and no
terminal event occurred, the assessment is `INCOMPLETE`, final status is
`UNKNOWN`, and no public outcome is promoted.

`horizon_observation_ids` is the exact ordered prefix through the terminal bar,
or all twelve IDs for `TIMEOUT`. `event_observation_id` is exact for
`MIDPOINT_REACHED`, `INVALIDATED`, and `SAME_BAR_AMBIGUOUS`; it is `None` only
for `TIMEOUT`. `INCOMPLETE` and `INVALID` are internal assessment vocabulary and
never promoted as public outcome objects. Outcome first-known moment is the
event-bar close or twelfth close.

## 18. Exhaustive deterministic identity schemas

All identities are uppercase kind prefix plus lowercase SHA-256 of canonical
JSON with sorted keys, UTF-8 encoding, normalized UTC timestamps ending `Z`,
canonical enum values, ordered tuples as arrays, integer ticks/volumes, and
canonical Decimal `.0`/`.5` text. No `repr`, locale, float, object address,
implicit timezone, dict insertion order, or ambient Decimal context is allowed.

Common required fields for every kind are exactly: `identity_kind`,
`instrument`, `timeframe`, `dataset_id`, `calendar_version`,
`split_session_calendar_digest`, `kill_zone_calendar_digest`, `timezone_name`,
and `timezone_data_version`.

- `OBSERVATION` additionally requires exactly all observation fields in Section
  9 and forbids every range/candidate/outcome/manifest-only field.
- `OPENING_RANGE` additionally requires `segment_ordinal`, `segment_id`,
  `contract`, `trade_date`, the three ordered six-member source-ID tuples,
  `first_known_index`, `first_known_timestamp`, `high_tick`, `low_tick`,
  `midpoint_tick`, and `width_ticks`; the builder validates internal high/low,
  width, midpoint, tuple-length, and uniqueness consistency and forbids every
  other field. The analyzer alone validates extrema against supplied source
  observations before recomputing the identity.
- `CANDIDATE` additionally requires `range_id`, segment/contract/trade-date
  provenance, `direction`, the formation observation/context/snapshot IDs,
  `formation_index`, `first_known_timestamp`, `swept_boundary_tick`,
  `sweep_extreme_tick`, `reclaim_close_tick`, `midpoint_tick`,
  `invalidation_tick`, and `width_ticks`; it validates Section 16 and forbids
  every other field.
- `OUTCOME` additionally requires `candidate_id`, `outcome`,
  `first_known_index`, `first_known_timestamp`, ordered nonempty
  `horizon_observation_ids`, and the conditionally required or forbidden
  `event_observation_id`; only the four promoted terminal outcome values are
  identity-eligible, and every other field is forbidden.
- `MANIFEST` additionally requires exact `version`, ordered
  `requested_trade_dates`, `opening_range_ids`, `candidate_ids`, `outcome_ids`,
  `count_funnel`, and `reason_counts`; it forbids every observation/range/
  candidate/outcome-only field and rejects duplicate or noncanonical history.

The analyzer recomputes every supplied or created identity and requires exact
match. Hash shape alone is insufficient. Required/forbidden-field exhaustion,
ordered-history sensitivity, common-field sensitivity, malformed nested values,
and unknown kinds are fail-closed with no exception leakage beyond the public
builder's `TypeError`/`ValueError` contract.

## 19. Chronology, atomic processing, cutoff, and prefix invariance

Processing order is requested trade date, canonical segment order, observation
index, then normalized bar-open timestamp. Direction and hash lexical order are
never chronology tie-breaks. One same-effective group is validated and resolved
atomically before any range, candidate, outcome, or manifest promotion.

Malformed evidence with a trustworthy effective moment yields final `INVALID`,
preserves strictly prior complete public evidence byte-for-byte, and promotes
nothing from the failing group or later evidence. Evidence whose required
effective moment cannot be trusted is `INVALID` without a guaranteed prefix.
An ambiguous both-boundary group preserves only strictly prior complete
evidence and promotes no candidate or outcome for that trade date.

Prefix invariance applies only when the prefix ends on a complete effective
group and every appended dataset, calendar, context, snapshot, and observation
record is strictly later. Already promoted range/candidate/outcome bytes and IDs
must remain identical. Same-effective append, partial history, historical
insertion, repair, reorder, calendar mutation, version mutation, contract
substitution, dataset mutation, or OOS append is prefix-ineligible and must not
be presented as an invariance comparison.

## 20. Status precedence, reporting, and feasibility gate

Exact result precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Malformed supplied counterpart evidence outranks missing top-level context.
Independent strictly prior valid objects remain preserved when a later pending
group produces `UNKNOWN`; pending evidence promotes no candidate or outcome.
`AMBIGUOUS` is reachable only from the locked same-bar both-boundary qualifying
group or multiple nonidentical fully canonical same-effective interpretations
remaining after all available identities validate. Duplicate IDs, forks,
contradictions, and bad ordering are `INVALID`, not `AMBIGUOUS`.

`UNKNOWN` means required dataset, calendar, Kill-zone, source-range, or complete
future-horizon evidence is unavailable without independently determinable
invalid evidence. `VALID` requires at least one complete candidate with one
promoted terminal outcome and no higher status. `NONE` means a nonempty
explicitly requested, fully covered scope has no calendar-eligible trade date
or has complete range assessments but no qualifying sweep-reclaim candidate.
Empty `requested_trade_dates=()` is `NONE` only when every other evidence tuple
is exactly empty; unrequested supplied evidence is `INVALID`.
`requested_trade_dates=None` is `UNKNOWN` unless malformed supplied counterpart
evidence raises `INVALID`.

The manifest count-funnel keys and exact order are:
`REQUESTED_TRADE_DATES`, `CALENDAR_ELIGIBLE_TRADE_DATES`,
`COMPLETE_OPENING_RANGES`, `NO_SWEEP_RECLAIM_TRADE_DATES`,
`AMBIGUOUS_SWEEP_GROUPS`, `COMPLETE_CANDIDATES`, `BULLISH_CANDIDATES`,
`BEARISH_CANDIDATES`, `MIDPOINT_REACHED_OUTCOMES`,
`INVALIDATED_OUTCOMES`, `SAME_BAR_AMBIGUOUS_OUTCOMES`, `TIMEOUT_OUTCOMES`,
`COMPLETE_OUTCOMES`, `INCOMPLETE_HORIZONS`, and `INVALID_GROUPS`.

The only result reason tokens are:
`MISSING_TOP_LEVEL_CONTEXT`, `INVALID_DATASET`, `OOS_CONTACT`,
`UNREQUESTED_EVIDENCE`, `INVALID_OBSERVATION`,
`MISSING_SPLIT_SESSION_CALENDAR`, `INVALID_SPLIT_SESSION_CALENDAR`,
`MISSING_KILL_ZONE_CALENDAR`, `INVALID_KILL_ZONE_CALENDAR`,
`MISSING_KILL_ZONE_EVIDENCE`, `INVALID_KILL_ZONE_EVIDENCE`,
`SESSION_INELIGIBLE`, `INCOMPLETE_OPENING_RANGE`,
`INVALID_OPENING_RANGE`, `NO_SWEEP_RECLAIM`,
`AMBIGUOUS_SWEEP_RECLAIM`, `INCOMPLETE_OUTCOME_HORIZON`,
`INVALID_OUTCOME_EVIDENCE`, and `AMBIGUOUS_CANONICAL_INTERPRETATION`.
Reason counts are unique and ordered by this vocabulary; free-text variation is
forbidden.

A manifest is promoted only for complete final `VALID` or `NONE`. Final
`INVALID`, `AMBIGUOUS`, or `UNKNOWN` has `manifest=None`, preserves strictly
prior public evidence where Section 19 permits, and does not present a partial
funnel as a complete run.

Private feasibility PASS requires all of:

- at least `30` complete candidates;
- at least `24` distinct eligible development trade dates;
- at least `10` bullish and `10` bearish complete candidates;
- both accepted contracts represented with at least `8` candidates each;
- `100%` identity/count/status/reason/byte reproducibility across two fresh runs;
- a complete requested-date funnel and zero silent exclusion; and
- zero OOS, feature, label, PnL, risk, entry/exit, or model contact.

PASS authorizes only a later feature/label experiment proposal. It does not
authorize training: training remains blocked until a separate prospective
data/partition decision supplies at least three canonical contract months and
all existing no-look-ahead gates. FAIL retires this final setup family on the
current dataset without threshold, window, geometry, horizon, gate, or
candidate rescue and moves research to prospective data expansion.

## 21. Inline synthetic exact 48-case acceptance matrix

Future tests preserve exactly these logical cases; parameterization may increase
collected tests without changing the logical count:

1. Missing bars and missing calendar produce fail-closed `UNKNOWN` with no range.
2. A malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
3. Non-tuple, duplicate, reordered, or same-index forked observations are rejected.
4. Boolean, fractional, non-finite, negative-volume, or malformed values fail closed.
5. Naive timestamps and timezone/version mismatch fail closed.
6. Non-GC, spot, CFD, option, micro, or ambiguous contract inputs are rejected.
7. Non-5m, non-closed, pseudo-MTF, or cross-contract source bars are rejected.
8. Missing, holiday, session-closed, or inapplicable calendar evidence is fail-closed.
9. Early close preventing complete source or horizon coverage is ineligible exactly.
10. Six source bars at `07:00` through `07:25` form one range at `07:30`.
11. Five bars are insufficient and a seventh cannot enter the source tuple.
12. Missing middle source, timestamp substitution, or nonconsecutive index is invalid.
13. Cross-trade-date, cross-segment, or cross-session source membership is invalid.
14. Positive one-tick width is valid and zero width is invalid.
15. Even/odd, signed-zero, and arbitrary-magnitude midpoints remain exact across Decimal contexts.
16. Exact `07:30` formation-window start is eligible and pre-start evidence is not.
17. Exact `09:00` bar-open timestamp and later evidence are formation-ineligible.
18. Upper one-tick sweep plus same-bar upper-half reclaim creates a bearish candidate.
19. Lower one-tick sweep plus same-bar lower-half reclaim creates a bullish candidate.
20. Sub-one-tick excursion, boundary miss, or midpoint-equality close is a noncandidate.
21. Closing at the swept range boundary qualifies, while closing outside does not.
22. Outside-range close followed by later reclaim cannot be relabeled as a candidate.
23. One bar sweeping both boundaries is `AMBIGUOUS` with no candidate promotion.
24. Earliest qualifying formation wins and later bars become outcome evidence only.
25. Exact duplicates collapse; forked or contradictory same-effective evidence is invalid.
26. Bullish/bearish mirror geometry and implied opposite boundary reconcile exactly.
27. Bearish boundary, extreme, close, midpoint, invalidation, provenance, and identity are sensitive and immutable.
28. Bullish boundary, extreme, close, midpoint, invalidation, provenance, and identity are sensitive and immutable.
29. The formation bar is excluded from target and invalidation assessment.
30. The horizon is the next exact twelve same-segment/contract/date/context bars.
31. Bearish midpoint equality by low produces `MIDPOINT_REACHED` first-known at bar close.
32. Bullish midpoint equality by high produces `MIDPOINT_REACHED` first-known at bar close.
33. Bearish close at exact formation-high-plus-one produces `INVALIDATED`.
34. Bullish close at exact formation-low-minus-one produces `INVALIDATED`.
35. Target and invalidation on the same earliest bar produce `SAME_BAR_AMBIGUOUS`.
36. Twelve complete bars without either terminal event produce `TIMEOUT`.
37. Truncated horizon produces `UNKNOWN`, no outcome, and no later-relabel repair.
38. Determinably later malformed evidence preserves only strictly prior complete evidence.
39. `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence is exact.
40. Every identity kind exhausts all common, required, forbidden, nested, and sensitive fields.
41. Ordered horizon/history, effective moment, reason vocabulary, and malformed hashes fail closed.
42. Exact keyword-only signatures/defaults, frozen dataclasses, enums, version, and exports pass.
43. Two fresh executions reproduce identities, counts, statuses, reasons, manifests, order, and bytes.
44. A complete-group strictly-later append preserves all prior promoted bytes and identities.
45. Same-effective append, repair, insertion, reorder, calendar/version/dataset mutation is prefix-ineligible.
46. Exact `30`/`24`/`10+10`/`8+8` feasibility thresholds and complete funnel are discriminated.
47. Feasibility FAIL retires this final setup family and permits only prospective data expansion.
48. Three-path scope, forbidden imports, rollback, and no private run/feature/label/training/OOS/integration pass.

## 22. Reserved future implementation and private-run scope

Only a separate explicit authorization may lift the freeze for exactly:

- `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py`
- `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py`
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md`

No external fixture is permitted; tests use inline synthetic records. Private
accepted artifacts remain outside Git and cannot be copied into source, tests,
docs, checkpoints, commits, or remote storage. Implementation does not
authorize a private run. A later private-run proposal must bind exact committed
implementation hashes, private input identities, output directory, atomic
temporary-to-final publication, two fresh runs, and independent audit before
execution.

## 23. Acceptance, promotion, rollback, and STOP conditions

Documentation acceptance requires exactly 24 sequential numbered sections,
exactly 48 sequential logical cases, exhaustive immutable/API/identity/status/
chronology contracts, exact one-file scope, zero formatting error, baseline
regression PASS, and exact staged SHA-256 verification.

Fresh cache-disabled baseline-preservation evidence on `2026-08-16` is:

- focused `tests/test_gc_cross_segment_continuity.py`:
  `48 passed in 0.85s`; and
- full explicit `tests` suite: `2394 passed in 22.25s`.

A repository-root discovery attempt was not accepted as regression evidence:
pytest encountered two ACL-protected private artifact directories during
collection before running tests. The explicit `tests` invocation is the locked
public regression surface and passed completely. These regressions do not test
the proposed analyzer; they prove only that this documentation-only task did
not alter the accepted code baseline.

Implementation promotion requires test-first coverage of all 48 logical cases,
focused and full regression PASS with pytest cache disabled, exact three-path
scope, artifact hashes and byte/line counts, no external fixture, and an
independent final audit. It still grants no private run.

STOP on baseline or dependency drift, ambiguous public contract, unavailable
canonical observation/calendar/context proof, data mutation, silent sorting or
exclusion, non-determinism, continuation-V1 rescue, more than one setup,
parameter revision after outcomes, private evidence publication, OOS contact,
feature or label table production, PnL, training, model dependency, integration,
execution, test failure, scope drift, or remote publication without exact
authority.

Before implementation commit, rollback is removal of only the reserved three
paths. After commit, rollback requires a bounded revert; source evidence,
negative results, and history may not be deleted or rewritten.

## 24. Final decision and next single task

The exact proposal decision is:

`PROPOSE_PHASE_B_GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_V1_FEASIBILITY_IMPLEMENTATION`

This document specifies one deterministic feasibility analyzer and nothing
else. It neither implements nor runs it. If this document passes independent
semantic/structural audit and is separately accepted, the next single task is
test-first implementation within the exact three paths in Section 22. No
private run, feature/label experiment, training, OOS evaluation, integration,
paper trading, or live trading may begin from this decision alone.
