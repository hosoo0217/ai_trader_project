# SMC V2 Completed-Session Volume Profile Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-FREEZE-LIFT-2026-08-01`
- Capability: completed-session GC Volume Profile diagnostic
- Detector version: `SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-1`
- Decision state: `ACCEPT_FOR_BOUNDED_IMPLEMENTATION_REVIEW`
- Change class: documentation-only formal freeze-lift decision
- Global code-freeze state: `ACTIVE`
- Integration state: `NOT_AUTHORIZED`
- Trading-decision effect: `NONE`

This record authorizes no Python change by itself. It locks the contract that a
later, separately authorized bounded implementation must follow. The capability
is diagnostic-only, completed-session-only, and isolated from entries, exits,
risk, sizing, scoring, PnL, paper progression, and live progression.

## 2. Effective State and Preconditions

The first eleven bounded SMC V2 diagnostic capabilities are committed before
this twelfth-task decision. The repository baseline for this record is:

- parent `HEAD`: `ace125089323e956b9b6b7ad5bad66cd39d87c6f`;
- local `origin/main`: `ace125089323e956b9b6b7ad5bad66cd39d87c6f`;
- worktree before this record: clean;
- integration changes: none;
- global freeze: active outside an explicitly authorized exact path.

Implementation cannot begin until this record has passed an independent final
audit, been committed as a documentation checkpoint, been pushed only with a
separate explicit export authorization, and passed a read-only post-push
readiness audit.

## 3. Locked Authorities and Dependency Evidence

The following files are the controlling local authorities for this decision.
Their SHA-256 values at decision preparation time are locked:

| Authority | SHA-256 |
|---|---|
| `docs/smc_v2_volume_profile_recommended_specification.md` | `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9` |
| `docs/smc_v2_volume_profile_implementation_plan.md` | `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D` |
| `docs/smc_v2_volume_profile_change_proposal.md` | `3089BA1CDACCC4353D16D8B3A6BC28D0D21219C1C7AFE2D88B6F0F2936D2E210` |
| `docs/smc_v2_volume_profile_change_proposal_review.md` | `C94DDD8843DC849D1F3C141DAA8942F94C11F23CC189B99AFD7E45A4898762FA` |
| `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md` | `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4` |
| `docs/smc_v2_volume_profile_diagnostic_freeze_lift_readiness_audit.md` | `B61BB39E832A94BB4C1C671DBE2AF90AFAF616EC17DC564BFF5E7A68E63C5427` |
| `docs/smc_v2_volume_profile_diagnostic_freeze_lift_decision.md` | `E6A68EA0A5BFC3815D04705E362E013BABE53A90951C0AB86EC0B323B5B9759C` |
| `docs/smc_v2_volume_profile_shared_primitives_checkpoint.md` | `4E80F40431A708BFC641DA3EC664722BDD20EDAE642843D9634D5B37DDB7679B` |
| `docs/smc_v2_kill_zone_diagnostic_freeze_lift_decision.md` | `72D9EA42B464F7C2233C9B7ACA4BFA7BEFD3A5ABADD7E31B7EA3F2B202CFE5BB` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `orderflow/footprint.py` | `4CFF600A7C447D95B58E91A3B9675C30A3AB08401E2FB327A5A69DAEF8BC30FA` |

A mismatch before implementation is a mandatory STOP pending a new read-only
dependency audit. The shared `SMCV2PrimitiveStatus`, UTC normalization behavior,
and committed `KillZoneCalendarEntry` / `KillZoneSessionStatus` contract are
dependencies; they are not authorized for modification by this task.

## 4. Exact Documentation-Only Change

This decision task may create and correct only:

- `docs/smc_v2_completed_session_volume_profile_diagnostic_freeze_lift_decision.md`

It must not stage or modify Python, tests, fixtures, importers, footprint models,
requirements, configuration, integration wiring, or any other documentation.

## 5. Reserved Future Implementation Scope

A later bounded implementation may reserve exactly these three paths:

- `orderflow/volume_profile.py`
- `tests/test_volume_profile.py`
- `docs/smc_v2_completed_session_volume_profile_checkpoint.md`

All three must be absent at this decision checkpoint. Creating them requires a
separate post-push readiness audit and explicit bounded implementation approval.
No external fixture, calendar file, holiday file, timezone file, importer change,
or `orderflow/footprint.py` change is included.

## 6. Capability Boundary

Version 1 computes an immutable Volume Profile only for a completed eligible GC
session. It emits exact POC, VAL, VAH, total volume, covered volume, covered
percentage, completeness, and data-quality evidence.

It does not compute or expose:

- a developing profile;
- a rolling profile;
- a manually anchored profile;
- HVN or LVN;
- an entry, exit, stop, target, size, bias, score, or confidence change;
- a current-bar or future-aware value;
- a fallback approximation from bar-summary volume.

Any request for those behaviors is a new specification and STOP condition.

## 7. Immutable Canonical Input Contracts

All public dataclasses below are `@dataclass(frozen=True)`. Required values must
be exact instances of their stated types; `bool` is rejected where `int` is
required. Attribute access, enum conversion, timestamp conversion, and nested
validation must not leak exceptions other than the public builder's locked
`TypeError` or `ValueError` contract.

```python
@dataclass(frozen=True)
class CompletedSessionVolumeLevel:
    price_tick: int
    bid_volume: int
    ask_volume: int
    reported_total_volume: int


@dataclass(frozen=True)
class CompletedSessionVolumeBar:
    index: int
    open_timestamp: datetime
    close_timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    is_closed: bool
    source_format: str
    reported_total_volume: int
    levels: tuple[CompletedSessionVolumeLevel, ...]
```

Level rules:

- `price_tick`, bid, ask, and reported volume are exact integers;
- bid, ask, and reported volume are nonnegative;
- `reported_total_volume == bid_volume + ask_volume`;
- levels within one bar are strictly increasing by `price_tick`;
- duplicate ticks within one bar are `INVALID`;
- the same tick in different bars is valid and is aggregated exactly.

Bar rules:

- `index` is a nonnegative exact integer;
- timestamps are timezone-aware and normalize to UTC;
- `open_timestamp < close_timestamp`;
- OHLC ticks are exact integers with
  `low_tick <= open_tick, close_tick <= high_tick` and `low_tick <= high_tick`;
- every level `price_tick` lies inclusively between `low_tick` and `high_tick`;
- `is_closed` is exactly `True`;
- `source_format` is exactly `ACSIL_FULL_FOOTPRINT` in v1;
- `reported_total_volume` is nonnegative and exactly equals the sum of all
  level reported totals;
- `levels` is a nonempty tuple;
- the bar duration equals `bar_duration_seconds` exactly;
- bar open and close moments lie on the exact session-open-derived duration
  grid; off-grid bars are `INVALID` rather than rounded.

The calendar input is the already committed frozen dependency:

```python
@dataclass(frozen=True)
class KillZoneCalendarEntry:
    calendar_version: str
    trade_date: date
    session_status: KillZoneSessionStatus
    session_open_timestamp: datetime | None
    session_close_timestamp: datetime | None
```

Calendar entries are validated locally under the exact Section 9 boundary.

## 8. Source Qualification and Legacy Boundary

`orderflow.footprint.FootprintCandle` and `FootprintLevel` are legacy mutable,
float-bearing models. Their `_safe_volume()` behavior clamps negative values.
They are therefore not the official canonical input for this capability and may
not be passed directly to the public analyzer.

The only admitted v1 source token is `ACSIL_FULL_FOOTPRINT`, represented after
an explicit lossless adapter boundary by the immutable integer contracts in
Section 7. The adapter is not in this task. A different full price-level source
is admitted only after a separate equivalence review, version change, and formal
decision; it is not silently treated as equivalent in v1.

`BAR_SUMMARY` is explicitly rejected as `INVALID`. Synthetic allocation of a
bar total to its close, across its price range, or by any weighting scheme is
forbidden. Unknown source tokens, mixed source tokens, legacy objects, floats,
fractional volumes, NaN, infinity, negative values, and bool-as-int values are
`INVALID`.

## 9. Timezone, Calendar, and Completed GC Session

The timezone name is exactly `America/New_York`. The supplied normalized
`timezone_data_version` must exactly match the runtime package-backed tzdata
version. `ZoneInfo("America/New_York")` and the runtime version must be available.
A supplied mismatch is `INVALID`; runtime timezone or version unavailability is
`UNKNOWN` with a blocking environment reason and no new output.

For eligible trade date `D`, the standard GC session is:

- open: local `18:00:00` on calendar date `D - 1`, inclusive;
- close: local `17:00:00` on `D`, exclusive;
- maintenance: local `[17:00:00, 18:00:00)` and outside the session.

IANA database conversion, not a fixed UTC offset, determines the UTC instants.
The `trade_date` must be Monday through Friday.

Calendar semantics:

- `OPEN`: entry open and close must exactly match the standard IANA-derived
  session boundaries;
- `EARLY_CLOSE`: open must match the standard open and close must be strictly
  after open and strictly before the standard close;
- `SESSION_CLOSED`: both timestamps must be `None`; holiday and explicit closure
  produce `NONE` and no profile;
- a weekend requested date with no entry or an exact `SESSION_CLOSED` entry
  produces `NONE`; an `OPEN` or `EARLY_CLOSE` weekend entry is contradictory and
  `INVALID`;
- missing required calendar entry or `calendar_entries=None` produces `UNKNOWN`
  with `CALENDAR_UNVERIFIED`, after independently supplied evidence is validated;
- duplicate, forked, version-mismatched, out-of-order, impossible, or overlapping
  calendar evidence is `INVALID`;
- every supplied calendar entry corresponds to exactly one requested trade date;
  an unrequested entry is `INVALID`, not silently ignored.

`as_of_timestamp` must be timezone-aware; a naive or malformed supplied value is
`INVALID`. An eligible session is completed only when normalized `as_of_timestamp` is at
or after its exact session close. An as-of time before close produces `NONE`
with `SESSION_NOT_COMPLETED`; no developing profile is emitted.

Every supplied bar must lie wholly inside exactly one requested eligible session:
`session_open <= bar.open < bar.close <= session_close`. A bar straddling a
boundary, falling in maintenance, belonging to an unrequested session, or being
attributable to multiple sessions is `INVALID`.

## 10. Input Ordering and Atomic Processing

`trade_dates` is a tuple of unique dates in strictly increasing order.
`calendar_entries` is a tuple in strictly increasing `trade_date` order.
`bars` is a tuple ordered by the composite key:

```text
(normalized open_timestamp, normalized close_timestamp, index)
```

The key must be strictly increasing. Bar indices and open timestamps are each
independently strictly increasing; duplicate indices, duplicate opens, overlap,
or caller-supplied reordering is `INVALID`. The analyzer performs no silent sort.

Requested sessions are processed atomically by:

```text
(normalized session_close_timestamp, trade_date)
```

All input evidence attributable to one session is validated before its PROFILE
and cumulative SNAPSHOT are promoted. An `INVALID`, `AMBIGUOUS`, or `UNKNOWN`
session group promotes nothing from that group or any later group. Byte-identical
strictly prior valid profiles and snapshots remain in the result if the failing
effective moment is determinable. If a malformed required field prevents a
trustworthy effective moment, no prior-prefix guarantee is claimed and the
result fails closed as `INVALID`.

## 11. Exact Conservation, Completeness, and Data Quality

For every admitted level:

```text
level_total = bid_volume + ask_volume = reported_total_volume
```

For every admitted bar:

```text
bar_total = sum(level.reported_total_volume) = bar.reported_total_volume
```

For every profile:

```text
profile_total
  = sum(bar.reported_total_volume)
  = sum(aggregate.bid_volume + aggregate.ask_volume)
  = sum(aggregate.total_volume)
```

Any mismatch is `INVALID`; no tolerance, rounding, coercion, clamping, or dropped
remainder is permitted.

The expected closed-bar grid is generated exactly from session open through
session close using `bar_duration_seconds`. The duration is a positive exact
integer, the session length in seconds must be exactly divisible by it, and every
bar interval must equal one grid cell. A gap in that grid, while all supplied
records remain canonical and non-overlapping, produces:

- completeness `INCOMPLETE`;
- data quality `UNQUALIFIED`;
- a reportable partial completed-session profile if total volume is positive.

Complete exact grid coverage produces `COMPLETE` and `QUALIFIED`. An empty
session evidence tuple is `UNKNOWN` with `DATA_UNAVAILABLE`. A canonical fully
covered or partial session whose exact total volume is zero produces `NONE` with
`ZERO_SESSION_VOLUME`; division and identity construction are not attempted.

```python
class CompletedSessionVolumeProfileCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class CompletedSessionVolumeProfileDataQuality(str, Enum):
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
```

## 12. Deterministic POC

Aggregate exact integer total volume by `price_tick`. Let:

```text
V = sum(volume_at_tick)
N = sum(price_tick * volume_at_tick)
session_volume_weighted_mean_tick = N / V
```

`N/V` is stored as reduced exact integer numerator and positive denominator; no
binary float or Decimal context participates.

POC selection is:

1. retain every tick having maximum aggregate total volume;
2. minimize exact distance to `N/V`, compared as `abs(tick * V - N)`;
3. if still tied, choose the lower tick.

`poc_tied_ticks` contains every maximum-volume candidate in strictly increasing
tick order. Its chosen `poc_tick` must be a member. Negative and arbitrary-
magnitude ticks and volumes use exact Python integer arithmetic.

## 13. Exact 70% Value Area

The Value Area algorithm is versioned and deterministic:

1. start with the canonical POC tick included;
2. set `covered_volume` to volume at POC;
3. while `covered_volume * 10 < total_volume * 7`, inspect the immediately
   adjacent unused integer tick below VAL and above VAH;
4. missing price ticks inside the observed minimum/maximum tick span are exact
   zero-volume adjacency levels, not invented source evidence;
5. add exactly one adjacent tick: the side with greater aggregate volume;
6. on equal adjacent volume, add the lower-price side;
7. if only one side remains inside the observed span, add that side;
8. stop immediately when the exact integer inequality reaches or exceeds 70%.

`VAL` and `VAH` are the final inclusive bounds. Covered volume equals the exact
sum over every integer tick from VAL through VAH, using zero for absent ticks.
Covered percentage is stored as the reduced exact fraction
`covered_volume / total_volume` and may exceed 70% because one whole tick is
added at a time. No two-level expansion, interpolation, float threshold, or
post-hoc smallest-range optimization is permitted.

## 14. Exact Public API and Frozen Outputs

The later implementation must export exactly:

```python
COMPLETED_SESSION_VOLUME_PROFILE_VERSION = (
    "SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-1"
)
COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE = "America/New_York"
COMPLETED_SESSION_VOLUME_PROFILE_SOURCE = "ACSIL_FULL_FOOTPRINT"


class CompletedSessionVolumeProfileCompleteness(str, Enum): ...
class CompletedSessionVolumeProfileDataQuality(str, Enum): ...


@dataclass(frozen=True)
class CompletedSessionVolumeLevel:
    price_tick: int
    bid_volume: int
    ask_volume: int
    reported_total_volume: int


@dataclass(frozen=True)
class CompletedSessionVolumeBar:
    index: int
    open_timestamp: datetime
    close_timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    is_closed: bool
    source_format: str
    reported_total_volume: int
    levels: tuple[CompletedSessionVolumeLevel, ...]


@dataclass(frozen=True)
class CompletedSessionVolumeAtPrice:
    price_tick: int
    bid_volume: int
    ask_volume: int
    total_volume: int


@dataclass(frozen=True)
class CompletedSessionVolumeProfile:
    profile_id: str
    trade_date: date
    session_open_timestamp: datetime
    session_close_timestamp: datetime
    first_known_timestamp: datetime
    source_format: str
    timezone_name: str
    timezone_data_version: str
    calendar_version: str
    bar_duration_seconds: int
    source_bar_indices: tuple[int, ...]
    source_bar_open_timestamps: tuple[datetime, ...]
    source_bar_close_timestamps: tuple[datetime, ...]
    source_bar_ohlc_ticks: tuple[tuple[int, int, int, int], ...]
    price_levels: tuple[CompletedSessionVolumeAtPrice, ...]
    poc_tick: int
    poc_tied_ticks: tuple[int, ...]
    volume_weighted_mean_numerator: int
    volume_weighted_mean_denominator: int
    val_tick: int
    vah_tick: int
    total_volume: int
    covered_volume: int
    covered_percentage_numerator: int
    covered_percentage_denominator: int
    completeness: CompletedSessionVolumeProfileCompleteness
    data_quality: CompletedSessionVolumeProfileDataQuality


@dataclass(frozen=True)
class CompletedSessionVolumeProfileSnapshot:
    snapshot_id: str
    effective_timestamp: datetime
    profile_ids: tuple[str, ...]


@dataclass(frozen=True)
class CompletedSessionVolumeProfileResult:
    status: SMCV2PrimitiveStatus
    profiles: tuple[CompletedSessionVolumeProfile, ...] = ()
    snapshots: tuple[CompletedSessionVolumeProfileSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

The exact keyword-only builder signature is:

```python
def make_volume_profile_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    calendar_version: str,
    timezone_name: str,
    timezone_data_version: str,
    trade_date: date | None = None,
    session_open_timestamp: datetime | None = None,
    session_close_timestamp: datetime | None = None,
    first_known_timestamp: datetime | None = None,
    source_format: str | None = None,
    bar_duration_seconds: int | None = None,
    source_bar_indices: tuple[int, ...] = (),
    source_bar_open_timestamps: tuple[datetime, ...] = (),
    source_bar_close_timestamps: tuple[datetime, ...] = (),
    source_bar_ohlc_ticks: tuple[tuple[int, int, int, int], ...] = (),
    price_levels: tuple[CompletedSessionVolumeAtPrice, ...] = (),
    poc_tick: int | None = None,
    poc_tied_ticks: tuple[int, ...] = (),
    volume_weighted_mean_numerator: int | None = None,
    volume_weighted_mean_denominator: int | None = None,
    val_tick: int | None = None,
    vah_tick: int | None = None,
    total_volume: int | None = None,
    covered_volume: int | None = None,
    covered_percentage_numerator: int | None = None,
    covered_percentage_denominator: int | None = None,
    completeness: CompletedSessionVolumeProfileCompleteness | None = None,
    data_quality: CompletedSessionVolumeProfileDataQuality | None = None,
    effective_timestamp: datetime | None = None,
    profile_ids: tuple[str, ...] = (),
) -> str:
    ...
```

The exact keyword-only analyzer signature is:

```python
def analyze_completed_session_volume_profiles(
    *,
    instrument: str,
    timeframe: str,
    bar_duration_seconds: int,
    trade_dates: tuple[date, ...] | None,
    bars: tuple[CompletedSessionVolumeBar, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
    timezone_data_version: str,
    as_of_timestamp: datetime,
) -> CompletedSessionVolumeProfileResult:
    ...
```

No positional parameters, optional fixture parameter, clock read, calendar API,
or hidden global default is permitted.

The exact `__all__` tuple, in this order, is:

```python
(
    "COMPLETED_SESSION_VOLUME_PROFILE_VERSION",
    "COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE",
    "COMPLETED_SESSION_VOLUME_PROFILE_SOURCE",
    "CompletedSessionVolumeProfileCompleteness",
    "CompletedSessionVolumeProfileDataQuality",
    "CompletedSessionVolumeLevel",
    "CompletedSessionVolumeBar",
    "CompletedSessionVolumeAtPrice",
    "CompletedSessionVolumeProfile",
    "CompletedSessionVolumeProfileSnapshot",
    "CompletedSessionVolumeProfileResult",
    "make_volume_profile_id",
    "analyze_completed_session_volume_profiles",
)
```

Imported calendar/status dependencies and private normalization helpers are not
re-exported.

## 15. Deterministic PROFILE and SNAPSHOT Identities

All identities are SHA-256 over canonical JSON with sorted keys, compact
separators, UTF-8, and no NaN. Instrument and timeframe are stripped then
uppercased. Calendar and timezone-data versions are stripped without case
folding. Timestamps normalize to UTC and serialize exactly as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`. Exact ratios serialize as integer numerator and
positive denominator. Hashes must be 64 lowercase hexadecimal characters.

### 15.1 Common identity parameters

Both identity kinds require:

- `identity_kind`;
- normalized `instrument`;
- normalized `timeframe`;
- normalized `calendar_version`;
- `timezone_name="America/New_York"`;
- normalized runtime-matching `timezone_data_version`;
- detector version.

### 15.2 PROFILE schema

`identity_kind="PROFILE"` requires every one of:

- `trade_date`;
- `session_open_timestamp`;
- `session_close_timestamp`;
- `first_known_timestamp` equal to normalized session close;
- `source_format="ACSIL_FULL_FOOTPRINT"`;
- positive exact `bar_duration_seconds`;
- nonempty, strictly increasing `source_bar_indices`;
- nonempty `source_bar_open_timestamps` and `source_bar_close_timestamps`, each
  equal in length to `source_bar_indices`, normalized in causal order, grid-
  aligned, and pairwise reconciled to exact duration/session boundaries;
- nonempty `source_bar_ohlc_ticks`, equal in length and position to the source
  bar tuples, with each `(open, high, low, close)` satisfying exact bar geometry;
- nonempty, strictly increasing canonical `price_levels` with exact conservation;
- `poc_tick`, sorted nonempty `poc_tied_ticks`, and POC reconciliation;
- reduced weighted-mean numerator and positive denominator;
- `val_tick <= poc_tick <= vah_tick`;
- positive `total_volume`, exact `covered_volume`, and reduced covered fraction;
- exact completeness/data-quality pairing.

It forbids non-`None` `effective_timestamp` and nonempty `profile_ids`.

### 15.3 SNAPSHOT schema

`identity_kind="SNAPSHOT"` requires:

- `effective_timestamp`;
- nonempty, ordered, unique, well-formed `profile_ids`.

It forbids every PROFILE-only parameter: `trade_date`, session timestamps,
first-known timestamp, source format, bar duration, source indices, price levels,
source bar open/close timestamps, source-bar OHLC ticks, POC fields,
weighted-mean fields, VAL/VAH, volume fields, percentage fields, completeness,
and data quality. Their exact forbidden values are respectively `None` for
nullable scalars and `()` for tuple parameters.

Unknown identity kinds, missing required parameters, supplied forbidden
parameters, impossible ratios, malformed nested dataclasses, inconsistent
geometry, or runtime timezone mismatch raise only `TypeError` or `ValueError`.

## 16. Immutable Output and Point-in-Time Model

One canonical PROFILE is formed once per supplied completed eligible session.
There is no transition or reclassification lifecycle. No later bar may mutate,
replace, enrich, or repair that profile within the same evidence history.

Profiles are ordered by `(session_close_timestamp, trade_date, profile_id)`.
After each promoted profile, one cumulative SNAPSHOT is emitted at that profile's
`first_known_timestamp`. Its `profile_ids` are the complete ordered PROFILE ID
prefix. Snapshot order is strictly increasing by normalized effective timestamp;
the tuple must mirror profile causal order and never use hash lexical order as a
chronology tie-break.

An incomplete profile is immutable evidence about the supplied completed-session
dataset. Historical repair requires a new complete run/version and is outside
prefix-invariance comparison; it is not a same-history lifecycle transition.

## 17. Status and Reason Semantics

Final status precedence is exact:

```text
INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE
```

- `INVALID`: malformed supplied evidence, conservation failure, forbidden source,
  ordering failure, calendar contradiction, identity inconsistency, or impossible
  geometry. Failing/later groups do not promote.
- `AMBIGUOUS`: retained in the shared vocabulary. Version 1 has no reachable
  valid ambiguity branch; duplicate/forked sources or calendars are `INVALID`,
  not synthetic ambiguity.
- `UNKNOWN`: required top-level context, calendar coverage, runtime timezone
  capability, or session data is unavailable after independently supplied
  evidence is validated. Prior profiles may remain.
- `VALID`: at least one positive-volume completed-session PROFILE was promoted.
  Both `QUALIFIED/COMPLETE` and reportable `UNQUALIFIED/INCOMPLETE` profiles use
  `VALID`, with their quality fields preserving the distinction.
- `NONE`: complete evidence proves no profile: session not completed, weekend or
  closed session, or canonical zero-volume session.

Missing top-level input never suppresses independently determinable malformed
counterpart evidence. Exceptions from malformed nested values are contained.
Reasons and blocking reasons are deterministic, ordered, and duplicate-free.

## 18. Complete-Session Prefix Invariance

Prefix invariance applies only when a valid prefix ends after a complete atomic
session group and the appended inputs contain strictly later requested trade
dates, calendar entries, bars, and as-of evidence without changing any prior
value or version.

Under an eligible append:

- every prior PROFILE is byte-identical and retains its ID;
- every prior SNAPSHOT is byte-identical and retains its ID;
- new profiles and snapshots append in causal order;
- prior incomplete profiles are not silently repaired.

Same-session append, same-effective append, partial group, historical insertion,
repair, deletion, reorder, source mutation, calendar mutation, timezone-data
version mutation, bar-duration mutation, or as-of reinterpretation is ineligible
for the prefix claim and must not be silently normalized.

## 19. Inline Synthetic Exact 48-Case Unit-Test Matrix

The future test file must contain inline synthetic data only and reconcile to
exactly 48 numbered logical cases. Parameterization may expand collected tests
without changing the logical-case count.

1. Exact public constants, detector version, and allowed source token.
2. Fully closed immutable integer level/OHLC bar happy path and geometry.
3. Exact type rejection: bool ticks/volumes/indices and non-tuple collections.
4. Negative, float, fractional, NaN, infinity, and malformed required fields.
5. Level conservation success and bid-plus-ask/reported-total mismatch failure.
6. Bar conservation success and level-sum/reported-total mismatch failure.
7. Strict level ordering, within-bar duplicate rejection, and cross-bar aggregation.
8. Bar timestamp awareness, OHLC/level reconciliation, exact duration/grid alignment, and `is_closed=True`.
9. Strict independent bar index/open ordering, composite order, overlap, and no sort.
10. `ACSIL_FULL_FOOTPRINT` acceptance and exact `BAR_SUMMARY` rejection.
11. Unknown, mixed, and legacy `FootprintCandle` source rejection.
12. Equivalent-source boundary remains STOP without separate review/version.
13. America/New_York availability and exact timezone-name enforcement.
14. Runtime tzdata availability, normalization, match, and mismatch behavior.
15. Standard prior-day 18:00 inclusive to trade-date 17:00 exclusive session.
16. Spring-forward session conversion through the IANA database.
17. Fall-back session conversion through the IANA database and repeatability.
18. Maintenance `[17:00,18:00)` exclusion and boundary-straddling rejection.
19. Monday-Friday eligibility, weekend NONE, and contradictory weekend-open rejection.
20. OPEN calendar exact-boundary validation and unrequested-entry rejection.
21. EARLY_CLOSE exact open, shortened close, and impossible close rejection.
22. SESSION_CLOSED holiday semantics and required `None` timestamps.
23. Missing calendar coverage and `calendar_entries=None` produce UNKNOWN.
24. Duplicate, forked, version-mismatched, out-of-order calendar entries INVALID.
25. Before-close as-of produces NONE and no developing profile.
26. At-close and after-close as-of admit completed-session analysis.
27. Bar attribution to one requested session and unrequested/overlapping rejection.
28. Exact divisible expected-grid COMPLETE/QUALIFIED classification and off-grid rejection.
29. Missing expected bar yields reportable INCOMPLETE/UNQUALIFIED profile.
30. Empty session data UNKNOWN and canonical zero-volume session NONE.
31. Exact aggregation and profile-level conservation across bars and ticks.
32. Unique maximum-volume POC.
33. POC volume tie resolved by exact distance to weighted mean.
34. Remaining POC tie resolved to lower tick; all tied ticks reported sorted.
35. Negative and arbitrary-magnitude ticks/volumes with exact rational mean.
36. Value Area starts at POC and stops on exact `covered*10 >= total*7`.
37. Value Area greater-adjacent-volume selection and one-level expansion.
38. Value Area equal-adjacent-volume lower-price tie rule.
39. Sparse tick gaps as zero adjacency, one-side exhaustion, VAL/VAH reconciliation.
40. Covered volume and reduced covered-percentage exactness, including overshoot.
41. PROFILE exhaustive schema, source moment/OHLC binding, and every field sensitivity.
42. SNAPSHOT exhaustive required/forbidden schema, ordered history, and sensitivity.
43. Identity normalization, UTC equivalence, repeatability, malformed hash containment.
44. Builder exact keyword-only names/defaults and unknown identity-kind rejection.
45. Analyzer exact keyword-only names/no defaults; public dataclass fields/defaults/frozen and exact exports.
46. Exact enum values, exports, no transition types, and forbidden HVN/LVN surface.
47. Final status precedence, missing-counterpart validation, atomic cutoff, prior evidence.
48. Complete-session prefix invariance, same-session ineligibility, deterministic multi-session output, and forbidden integration/import surface.

Each case must exercise the public API where behavior is externally observable.
Private-helper-only proof is insufficient.

## 20. Forbidden Scope and Integration Isolation

The bounded implementation must not:

- edit `orderflow/footprint.py` or `orderflow/sierra_chart_importer.py`;
- edit shared primitives, Kill-zone, SMC detectors, main entry points, strategy,
  broker, risk, configuration, requirements, or existing tests;
- import the new analyzer from existing production modules;
- add feature flags or default-on behavior;
- create external data, fixture, calendar, holiday, or timezone files;
- fetch an external calendar or timezone service;
- add rolling, anchored, developing, HVN, or LVN behavior;
- stage with `git add .` or a broad pathspec.

The future module may directly import only standard-library utilities,
`SMCV2PrimitiveStatus` and UTC normalization from the committed shared
primitives, and the committed Kill-zone calendar types. Any additional direct
dependency requires STOP and formal scope review.

## 21. Pre-Implementation and Verification Gates

Implementation readiness requires all of:

1. this decision is independently audited and committed;
2. the commit is pushed only after explicit privacy/export authorization;
3. local `HEAD`, local `origin/main`, and live remote main match;
4. worktree is clean;
5. authority hashes in Section 3 remain unchanged or are re-audited;
6. the three reserved implementation paths remain absent;
7. a read-only exact 3-path preflight is PASS;
8. an explicit human decision activates only that bounded exception;
9. tests are written before production behavior;
10. focused and full regression suites use `-p no:cacheprovider`;
11. an independent final code/test/scope/hash/checkpoint/diff audit is PASS.

No test count is predicted here. The future checkpoint must record actual
collected and passed totals, timings, SHA-256, bytes, lines, logical-case
reconciliation, and exact scope evidence.

## 22. Mandatory Stop Conditions

STOP without expanding scope if any of the following occurs:

- an authority hash or repository baseline conflicts with the checkpoint;
- implementation needs a fourth path;
- legacy footprint or importer mutation appears necessary;
- full price-level integer conservation cannot be established;
- `BAR_SUMMARY` would need acceptance or approximation;
- a source-equivalence claim lacks separate review;
- session, DST, holiday, early-close, or calendar evidence is indeterminate;
- POC or Value Area would require float rounding or an unspecified tie rule;
- runtime timezone/version binding cannot be reproduced;
- public API or identity payload must change;
- a failing test requires changing an existing dependency module;
- exact 48-case reconciliation, focused tests, or full regression tests fail;
- integration, performance claims, paper progression, or live progression are
  requested without separate authorization.

## 23. Rollback, Promotion, and Commit Boundary

Before a local commit, rollback is deletion of only the new untracked decision
file after verifying its exact resolved path. After a documentation commit,
rollback is a separately authorized bounded revert of that exact commit; history
must not be rewritten.

Promotion sequence is exact:

1. independent semantic/structural audit;
2. documentation-only corrections and re-audit until PASS;
3. stage this exact file only;
4. cached full-content, scope, formatting, and SHA-256 audit;
5. commit preflight;
6. local commit with subject
   `docs: record bounded Completed Session Volume Profile freeze-lift decision`;
7. STOP before push;
8. separate explicit export authorization before any push;
9. post-push completion/readiness audit before implementation;
10. separate exact 3-path implementation authorization.

Implementation promotion later requires an exact-scope final audit, clean tests,
staging authorization, cached audit, commit preflight, local commit, a separate
push authorization, and a post-push audit. Integration remains a still-later
independent decision.

## 24. Final Decision State

The Completed-Session Volume Profile v1 specification is sufficiently bounded
for documentation-checkpoint promotion. The only current freeze exception is
this decision file. Python implementation, external fixtures, importer and
footprint changes, integration, staging of other paths, and push are not
authorized by this record.

Global code freeze remains active everywhere else. Paper and live progression
remain blocked. No readiness approval or trading-performance claim is granted.
