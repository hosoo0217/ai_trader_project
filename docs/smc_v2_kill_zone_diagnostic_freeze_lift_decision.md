# SMC v2 Kill-zone Context Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision date: `2026-07-28`.
- Repository: `ai_trader_project`.
- Clean implementation parent: `4dda2a7768583478d996af7bf732d09ccf82a42e`.
- Parent subject: `feat(smc): add Breaker Block diagnostics`.
- Tenth bounded capability: Kill-zone context.
- Decision type: documentation-only bounded diagnostic freeze-lift decision.
- Current global code-freeze state: `ACTIVE`.
- Python implementation authorized by this record: `NO`.
- Integration authorized by this record: `NO`.
- Paper or live use authorized by this record: `NO`.

This record defines one future standalone time-context classifier. It does not
authorize Python implementation, tests, fixtures, staging, commit, push,
integration, configuration, runtime registration, strategy use, paper use, or
live use.

The accepted implementation order places Kill-zone context after Shared
Primitives, Equal Liquidity, Dealing Range, Liquidity Map,
Premium/Equilibrium/Discount, Fair Value Gap, Order Block, Mitigation Block, and
Breaker Block. Completion of those capabilities removes the implementation-order
blocker only. It does not transfer their freeze-lift authority to this task.

## 2. Effective-State Interpretation

A Kill-zone context is an immutable historical label derived from a fully closed
observation's timestamp, a fixed New York local-time window, and caller-supplied
versioned exchange-session calendar evidence.

It is:

- time-context metadata;
- non-directional;
- not an independent BUY or SELL signal;
- not a confidence score;
- not a trade filter;
- not a replacement for Market Structure, SMC, CRT, Order Flow, or session
  validation;
- not permission to alter an entry, exit, stop, target, size, risk, or execution
  decision.

The standalone version-1 classifier does not consume or summarize SMC events.
Contemporaneous SMC aggregation is integration and remains outside this task.

The effective interpretation of this record is:

1. classify only fully closed caller-supplied observation moments;
2. convert aware UTC timestamps through IANA `America/New_York` timezone rules;
3. apply fixed start-inclusive and end-exclusive time windows;
4. derive the applicable trade date deterministically;
5. reconcile that trade date against immutable caller-supplied calendar entries;
6. emit immutable context and complete-history snapshot evidence;
7. fail closed on missing, malformed, conflicting, or unreproducible required
   evidence.

## 3. Locked Decision Inputs and Dependency Evidence

This decision is grounded in:

- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`;
- `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256:
    `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`;
- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`
  - SHA-256:
    `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`;
- `docs/smc_v2_breaker_block_checkpoint.md`
  - SHA-256:
    `0ACC348203764FC9AA501DAB5DDB25971B97A301BA73C6AD81579243F4A19E3F`;
- `smc/smc_v2_primitives.py`
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`;
- `smc/breaker_block.py`
  - SHA-256:
    `03E2559C99F62826E87C435C3102A5B5B069FE3BE4BF234A8A3C89DFCBB2D45D`.

Verified dependency state at decision time:

- `HEAD = origin/main =
  4dda2a7768583478d996af7bf732d09ccf82a42e`;
- live remote `main` matched that commit;
- worktree status entries: `0`;
- Breaker Block focused evidence: `54 passed`;
- full regression evidence: `1424 passed`;
- current integration changes: `0`;
- `zoneinfo.ZoneInfo("America/New_York")`: available;
- installed package-backed timezone database: `tzdata 2026.2`;
- timezone dependency declaration in `requirements.txt` or
  `requirements-dev.txt`: absent.

The unpinned timezone-data dependency is not silently waived. The future
standalone implementation must record and reconcile a caller-supplied
`timezone_data_version`. If the runtime cannot establish the required timezone
or timezone-data version without guessing, analysis fails closed under the
status rules below. Editing requirements is not authorized by this record.

## 4. Exact Change Authorized in This Documentation Task

The only authorized change in this documentation task is creation of:

- `docs/smc_v2_kill_zone_diagnostic_freeze_lift_decision.md`

No existing file may be edited. This task does not authorize creation of the
reserved implementation files.

The decision file must be independently audited before any staging
authorization. Staging, commit, and push require separate explicit gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If and only if this decision record completes every documentation promotion gate
and a later post-push readiness audit passes, one possible bounded
implementation task may reserve exactly:

- `smc/kill_zones.py`
- `tests/test_kill_zones.py`
- `docs/smc_v2_kill_zone_checkpoint.md`

These targets were absent at decision time. A future target collision is a stop
condition, not overwrite authorization.

No external fixture, calendar file, holiday file, timezone file, or generated
artifact is reserved. All future fixtures must be inline and synthetic in
`tests/test_kill_zones.py`.

The future exception may not include:

- `smc/smc_v2_primitives.py`;
- `smc/breaker_block.py`;
- any other completed SMC v2 module;
- `requirements.txt` or `requirements-dev.txt`;
- configuration, runtime, CLI, strategy, risk, execution, exporter, report, or
  integration files;
- package export or registration files.

## 6. Exact Functional Boundary

The future standalone classifier may:

- normalize an instrument and timeframe for identity construction;
- validate immutable fully closed observation moments;
- validate immutable caller-supplied calendar entries;
- convert aware UTC moments using `America/New_York`;
- derive a fixed Kill-zone candidate and trade date;
- reconcile the candidate with verified, early-close, or closed-session
  calendar evidence;
- emit deterministic immutable context and snapshot records;
- return fail-closed status, reason, and blocking-reason evidence.

It may not:

- fetch, infer, scrape, download, or update a calendar;
- call an external API or network;
- read a calendar, holiday, market, configuration, credential, or private-data
  file;
- use a fixed UTC offset;
- accept naive timestamps;
- silently substitute the machine-local timezone;
- reconstruct bars, swings, structure, liquidity, FVG, Order Blocks, Mitigation
  Blocks, or Breaker Blocks;
- summarize or aggregate SMC events;
- emit direction, bias, signal, score, confidence, trade eligibility, or
  execution advice;
- mutate or register itself in any existing runtime path.

Allowed future imports are limited to:

- Python standard-library deterministic utilities, including `datetime`,
  `zoneinfo`, `enum`, `dataclasses`, `hashlib`, and `json`;
- the exact shared status and timestamp-normalization primitives required from
  `smc.smc_v2_primitives`.

## 7. Locked Input Contracts

### 7.1 Top-level container and text contract

The public analyzer accepts:

- `instrument: str`;
- `timeframe: str`;
- `observations: tuple[KillZoneObservation, ...] | None`;
- `calendar_entries: tuple[KillZoneCalendarEntry, ...] | None`;
- `calendar_version: str`;
- `timezone_data_version: str`.

Rules:

- `None` for either top-level tuple means missing context and returns `UNKNOWN`;
- a non-tuple supplied for either tuple returns `INVALID`;
- empty tuples are valid complete inputs;
- instrument and timeframe are stripped and uppercased;
- calendar and timezone-data versions are stripped and uppercased;
- empty or non-string text returns `INVALID`;
- no caller-supplied timezone name, window, offset, holiday source, or fallback
  calendar is accepted.

### 7.2 Immutable fully closed KillZoneObservation

`KillZoneObservation` is an exact frozen dataclass with:

- `index: int`;
- `timestamp: datetime`;
- `is_closed: bool`.

Validation:

- `index` is an exact non-negative integer; boolean is invalid;
- `timestamp` is timezone-aware and is normalized to UTC;
- naive datetime, non-datetime, invalid offset, or timestamp conversion failure
  returns `INVALID`;
- `is_closed` is exact boolean `True`;
- `False`, integer `1`, missing, or malformed closed-state evidence returns
  `INVALID`;
- the observation moment is the fully closed observation's effective moment;
- no bar open, high, low, close, volume, outcome, PnL, entry, or exit field is
  accepted.

The observation tuple is caller-ordered. Both index and normalized timestamp
must be independently strictly increasing. Duplicate, decreasing, or crossed
index/timestamp order returns `INVALID`; the analyzer never sorts silently.

### 7.3 Immutable versioned KillZoneCalendarEntry

`KillZoneCalendarEntry` is an exact frozen dataclass with:

- `calendar_version: str`;
- `trade_date: date`;
- `session_status: KillZoneSessionStatus`;
- `session_open_timestamp: datetime | None`;
- `session_close_timestamp: datetime | None`.

Validation:

- `calendar_version` is stripped, uppercased, non-empty, and exactly matches the
  analyzer's normalized `calendar_version`;
- `trade_date` is exact `datetime.date`, not `datetime`;
- calendar entries are strictly increasing by trade date and unique;
- every entry uses the same normalized calendar version;
- `session_status` is exactly one locked enum member;
- `OPEN` and `EARLY_CLOSE` require aware open and close timestamps;
- `SESSION_CLOSED` requires both timestamps to be `None`;
- open and close timestamps are forbidden when status is `SESSION_CLOSED`;
- missing open or close timestamp is invalid for `OPEN` or `EARLY_CLOSE`;
- normalized open timestamp must be strictly earlier than normalized close
  timestamp;
- the elapsed interval must not exceed `24` hours;
- converted New York open local date must be the trade date or its immediately
  preceding calendar date;
- converted New York close local date must equal the trade date;
- a Saturday or Sunday trade date may only be `SESSION_CLOSED`;
- duplicate, forked, contradictory, malformed, or silently reordered entries
  return `INVALID`.

The analyzer validates only supplied calendar evidence. It does not claim that a
caller-supplied holiday or early close is an official exchange fact beyond the
recorded calendar version.

### 7.4 Time authority and version binding

The only time authority is:

- internal effective moments: timezone-aware UTC;
- exchange-local interpretation: exact IANA key `America/New_York`;
- daylight-saving conversion: installed timezone-database rules;
- offset fallback: forbidden.

`KILL_ZONE_TIMEZONE` is exactly `"America/New_York"` and is not configurable.

`timezone_data_version` is identity-bearing evidence. It must be non-empty and
must exactly reconcile with the runtime timezone-data version used for
conversion.

- malformed supplied version -> `INVALID`;
- supplied/runtime version mismatch -> `INVALID`;
- `America/New_York` unavailable -> `UNKNOWN`;
- runtime timezone-data version unknowable -> `UNKNOWN`;
- fixed-offset, machine-local, or caller-substituted timezone -> `INVALID`.

Equivalent aware timestamps that normalize to the same UTC microsecond must
produce identical results and identities under the same timezone-data version.

### 7.5 Calendar foreign-validation boundary

The future analyzer may validate:

- exact dataclass type and fields;
- version equality;
- trade-date order and uniqueness;
- status-specific required and forbidden fields;
- UTC normalization;
- session interval ordering and duration;
- New York local-date reconciliation;
- weekend closure;
- coverage for a derived trade date.

It may not:

- query an exchange, broker, CME, Sierra Chart, website, API, or operating-system
  holiday calendar;
- compare supplied entries with an unsupplied official calendar;
- infer a missing holiday or early close;
- create a favorable calendar repair;
- read a local file as an implicit fallback.

## 8. Locked Kill-zone Windows and Trade-Date Assignment

All windows use New York local wall time after deterministic UTC-to-zone
conversion. All starts are inclusive and all ends are exclusive.

Exact version-1 windows:

- `ASIA`: `20:00:00.000000` through, but not including, local midnight;
- `LONDON`: `02:00:00.000000` through, but not including, `05:00:00.000000`;
- `NEW_YORK_AM`: `07:00:00.000000` through, but not including,
  `10:00:00.000000`;
- `NEW_YORK_PM`: `13:00:00.000000` through, but not including,
  `16:00:00.000000`.

The four windows are fixed and non-overlapping. An observation outside every
window has no Kill-zone candidate.

Trade-date assignment:

- an `ASIA` observation uses local calendar date plus one day;
- every other candidate uses its local calendar date;
- only Monday through Friday derived trade dates are eligible;
- Sunday `20:00` New York time derives Monday's trade date;
- Friday `20:00` derives Saturday and is ineligible;
- local midnight is not part of `ASIA`;
- no later session outcome or bar changes the assigned trade date.

Window membership is computed from the fully closed observation timestamp. The
future module must not inspect the observation's unsupplied opening interval.

## 9. Locked Calendar, Session, Holiday, and Early-Close Semantics

For an observation inside a fixed window:

1. derive its trade date;
2. apply the Monday-through-Friday eligibility rule;
3. locate exactly one calendar entry for that trade date;
4. reconcile the observation against that entry's session interval;
5. classify context only after the complete group is known.

Exact results:

- ineligible weekend trade date -> one `VERIFIED` context with `zone=None` and
  `session_status=SESSION_CLOSED`, no active Kill-zone, and no calendar entry is
  required;
- matching `SESSION_CLOSED` entry -> one `VERIFIED` context with `zone=None` and
  `session_status=SESSION_CLOSED`, no active Kill-zone;
- matching `OPEN` or `EARLY_CLOSE` entry with observation inside the exact
  start-inclusive/end-exclusive session interval -> one `VERIFIED` context with
  the fixed non-`None` Kill-zone and the matching session status;
- matching open entry with observation before session open or at/after session
  close -> one `VERIFIED` context with `zone=None` and
  `session_status=SESSION_CLOSED`, no active Kill-zone;
- early close truncates any overlapping Kill-zone at the exact supplied close
  timestamp;
- observation exactly at session open is eligible;
- observation exactly at session close is closed and ineligible;
- missing trade-date entry -> emit one context retaining the deterministic
  candidate label with `CALENDAR_UNVERIFIED`, set session status to `None`, and
  return `UNKNOWN`;
- conflicting or malformed in-horizon entry -> `INVALID`;
- later calendar coverage must not retroactively relabel an earlier run.

Every valid observation inside a fixed window emits exactly one context and one
corresponding snapshot after its calendar group is completely classified.

An observation outside all fixed windows does not require calendar coverage and
does not emit a context record. Complete inputs containing only such
observations return `NONE`.

## 10. Locked Non-Directional Context Semantics

Kill-zone context has no bullish or bearish value.

The public surface contains no:

- `SMCV2Direction`;
- side;
- bias;
- long/short;
- BUY/SELL;
- confidence;
- score;
- signal;
- allow/block;
- trade-action field.

A valid context says only that one fully closed historical observation belongs
to one verified named time window under one calendar and timezone-data version.

The initial standalone module does not accept SMC event IDs, block IDs, range
IDs, liquidity IDs, FVG IDs, trace IDs, trade IDs, order IDs, or execution IDs.

## 11. Locked Atomic Processing and Chronological Cutoff

Observation processing is chronological and atomic.

For each observation effective moment:

1. start from the immutable pre-observation state;
2. validate the complete observation;
3. derive local time, candidate zone, and trade date;
4. validate the required calendar group;
5. create zero or one context;
6. create the corresponding complete-history snapshot when a context exists;
7. promote the context and snapshot together.

No half-created group may be promoted.

If malformed evidence has a safely determinable effective moment:

- return final `INVALID`;
- preserve byte-for-byte contexts and snapshots strictly earlier than that
  moment;
- promote nothing from the failing moment or any later moment.

If a required malformed field prevents trustworthy effective-moment
determination, return `INVALID` without claiming a trustworthy prefix.

Calendar-entry defects use the earliest observation moment whose derived trade
date requires the defective entry. A malformed unused future calendar entry is
still invalid complete supplied evidence; its cutoff is the first observation
whose derived trade date is at or after that entry when determinable. No silent
calendar truncation is permitted.

## 12. Locked Immutable Point Lifecycle

Version 1 has no mutable zone lifecycle and no transition record.

Each emitted `KillZoneContext` is:

- created once at the observation effective moment;
- terminal immediately;
- immutable;
- never enriched;
- never invalidated, expired, replaced, reopened, merged, or reclassified.

Each emitted `KillZoneSnapshot` is an immutable complete ordered prefix of
context IDs through its effective moment.

The only allowed causal progression is append-only:

`prior complete context prefix -> one later context -> one later snapshot`

There is no:

- `from_state`;
- `to_state`;
- transition ID;
- transition reason;
- lifecycle alias;
- retroactive calendar verification.

A rerun with repaired historical calendar coverage is a different complete
input, not a lifecycle transition and not an eligible prefix comparison.

## 13. Locked Public API

The public surface is exactly:

- `KILL_ZONE_DETECTOR_VERSION`;
- `KILL_ZONE_TIMEZONE`;
- `KillZoneName`;
- `KillZoneSessionStatus`;
- `KillZoneQuality`;
- `KillZoneObservation`;
- `KillZoneCalendarEntry`;
- `KillZoneContext`;
- `KillZoneSnapshot`;
- `KillZoneResult`;
- `make_kill_zone_id`;
- `analyze_kill_zones`.

Exact public constants:

```python
KILL_ZONE_DETECTOR_VERSION = "SMC-V2-KILL-ZONE-1"
KILL_ZONE_TIMEZONE = "America/New_York"
```

Exact enum values:

```python
class KillZoneName(str, Enum):
    ASIA = "ASIA"
    LONDON = "LONDON"
    NEW_YORK_AM = "NEW_YORK_AM"
    NEW_YORK_PM = "NEW_YORK_PM"


class KillZoneSessionStatus(str, Enum):
    OPEN = "OPEN"
    EARLY_CLOSE = "EARLY_CLOSE"
    SESSION_CLOSED = "SESSION_CLOSED"


class KillZoneQuality(str, Enum):
    VERIFIED = "VERIFIED"
    CALENDAR_UNVERIFIED = "CALENDAR_UNVERIFIED"
```

Exact analyzer signature:

```python
def analyze_kill_zones(
    *,
    instrument: str,
    timeframe: str,
    observations: tuple[KillZoneObservation, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
    timezone_data_version: str,
) -> KillZoneResult:
    ...
```

Exact identity-builder signature:

```python
def make_kill_zone_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    calendar_version: str,
    timezone_name: str,
    timezone_data_version: str,
    observation_index: int | None = None,
    observation_timestamp: datetime | None = None,
    trade_date: date | None = None,
    zone: KillZoneName | None = None,
    session_status: KillZoneSessionStatus | None = None,
    quality: KillZoneQuality | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    context_ids: tuple[str, ...] = (),
) -> str:
    ...
```

Both functions are keyword-only. No positional compatibility alias, overload,
`**kwargs`, or alternate function name is authorized.

### 13.1 Exact public frozen dataclass fields

```python
@dataclass(frozen=True)
class KillZoneObservation:
    index: int
    timestamp: datetime
    is_closed: bool


@dataclass(frozen=True)
class KillZoneCalendarEntry:
    calendar_version: str
    trade_date: date
    session_status: KillZoneSessionStatus
    session_open_timestamp: datetime | None
    session_close_timestamp: datetime | None


@dataclass(frozen=True)
class KillZoneContext:
    context_id: str
    observation_index: int
    observation_timestamp: datetime
    trade_date: date
    zone: KillZoneName | None
    session_status: KillZoneSessionStatus | None
    quality: KillZoneQuality
    calendar_version: str
    timezone_name: str
    timezone_data_version: str


@dataclass(frozen=True)
class KillZoneSnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    context_ids: tuple[str, ...]


@dataclass(frozen=True)
class KillZoneResult:
    status: SMCV2PrimitiveStatus
    contexts: tuple[KillZoneContext, ...] = ()
    snapshots: tuple[KillZoneSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

No additional public field or default is permitted. Every public dataclass is
frozen. All fields except the four tuple fields following `status` in
`KillZoneResult` have no default.

## 14. Locked Deterministic Identity Contract

### 14.1 Common identity rules

`make_kill_zone_id` supports exactly:

- `CONTEXT`;
- `SNAPSHOT`.

Unknown identity kinds return `ValueError`.

Canonical identity construction uses:

- lowercase hexadecimal SHA-256;
- canonical UTF-8 JSON;
- sorted object keys;
- compact separators;
- stripped uppercase instrument and timeframe;
- stripped uppercase calendar and timezone-data versions;
- exact timezone token `America/New_York`;
- exact enum `.value` tokens;
- trade date serialized as `YYYY-MM-DD`;
- timestamps normalized to UTC and serialized as
  `YYYY-MM-DDTHH:MM:SS.ffffffZ`;
- ordered tuple serialization without set or dictionary iteration;
- explicit identity-kind token in every payload.

Malformed nested dataclass values, booleans used as integers, naive timestamps,
invalid dates, malformed hashes, unsupported enums, and non-tuple histories
must raise only `TypeError` or `ValueError` from the public builder. Internal
`AttributeError`, `KeyError`, timezone exceptions, or serialization exceptions
must not leak.

### 14.2 CONTEXT schema

Required common parameters:

- `identity_kind="CONTEXT"`;
- `instrument`;
- `timeframe`;
- `calendar_version`;
- `timezone_name="America/New_York"`;
- `timezone_data_version`.

Required context parameters:

- `observation_index`;
- `observation_timestamp`;
- `trade_date`;
- `quality`.

Context parameters whose `None` value has locked meaning:

- `zone`;
- `session_status`.

Forbidden parameters:

- `effective_index`;
- `effective_timestamp`;
- non-empty `context_ids`.

Cross-field rules:

- `VERIFIED` plus `OPEN` or `EARLY_CLOSE` requires a non-`None` zone;
- `VERIFIED` plus `SESSION_CLOSED` requires `zone=None`;
- `CALENDAR_UNVERIFIED` requires `session_status=None` and a non-`None`
  deterministic candidate zone;
- `CALENDAR_UNVERIFIED` is forbidden outside a fixed window;
- `SESSION_CLOSED` is forbidden with a non-`None` zone;
- observation index is non-negative exact integer;
- the context identity is sensitive to every common and required field and to
  the locked `None` values;
- equivalent UTC timestamps and identical version evidence produce the same ID.

### 14.3 SNAPSHOT schema

Required common parameters:

- `identity_kind="SNAPSHOT"`;
- `instrument`;
- `timeframe`;
- `calendar_version`;
- `timezone_name="America/New_York"`;
- `timezone_data_version`.

Required snapshot parameters:

- `effective_index`;
- `effective_timestamp`;
- `context_ids`.

Forbidden parameters:

- `observation_index`;
- `observation_timestamp`;
- `trade_date`;
- `zone`;
- `session_status`;
- `quality`.

Rules:

- `context_ids` is an exact non-empty tuple;
- every member is a lowercase SHA-256 string;
- members are unique;
- order is identity-bearing;
- the analyzer recomputes every supplied context ID from the corresponding
  context before constructing a snapshot;
- snapshot effective moment equals the last context's observation moment;
- a snapshot contains the complete ordered context history, not a delta;
- reordering, omission, duplication, truncation, or foreign context IDs return
  `INVALID` in analyzer input validation and `TypeError` or `ValueError` in the
  public builder.

## 15. Locked Output Ordering and Snapshot Contract

Contexts are ordered strictly by:

`(observation_index, normalized observation_timestamp, context_id)`

Because observations have independently strictly increasing indices and
timestamps, `context_id` validates identity only and is not a chronology
tie-break.

Snapshots are ordered by:

`(index, normalized timestamp)`

Each snapshot:

- corresponds one-to-one with the newly emitted context at that moment;
- contains the exact complete context-ID prefix;
- has the same effective moment as that context;
- is promoted atomically with that context.

Direction, hash lexical order, calendar-entry tuple position, dictionary order,
and set order are not chronology tie-breaks.

## 16. Locked Result Status Semantics

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

### 16.1 INVALID

Return `INVALID` for:

- malformed top-level text or non-tuple containers;
- malformed or non-exact input dataclasses;
- observation order, timestamp, or closed-state failure;
- calendar version mismatch;
- malformed, duplicate, forked, contradictory, or out-of-order calendar entry;
- invalid session interval or trade-date reconciliation;
- supplied/runtime timezone-data version mismatch;
- fixed-offset or unauthorized timezone substitution;
- identity mismatch;
- impossible context cross-field geometry;
- malformed required or forbidden identity parameter;
- any exception that would otherwise escape locked fail-closed handling.

Final `INVALID` cannot be downgraded by an earlier or later `UNKNOWN`, `VALID`,
or `NONE`.

### 16.2 AMBIGUOUS

`AMBIGUOUS` remains part of the shared `SMCV2PrimitiveStatus` vocabulary.

There is no reachable valid version-1 `AMBIGUOUS` branch because:

- the four fixed windows do not overlap;
- one observation has one local timestamp;
- one trade date may have at most one calendar entry;
- duplicate or conflicting windows or calendar evidence are `INVALID`.

The future implementation must not invent an opposing-candidate or
score-selection branch merely to emit `AMBIGUOUS`.

### 16.3 UNKNOWN

Return `UNKNOWN` when:

- either required top-level tuple is `None`;
- `America/New_York` is unavailable;
- the runtime timezone-data version cannot be established;
- an observation inside a fixed window has no matching calendar entry;
- another required context is genuinely unavailable without contradictory
  supplied evidence.

Missing calendar coverage emits a `CALENDAR_UNVERIFIED` context and its
snapshot. That context is diagnostic evidence only and cannot be used for
decision research.

If a later determinable supplied defect exists, final status is `INVALID`, not
`UNKNOWN`.

### 16.4 VALID

Return `VALID` only when:

- every supplied input passes integrity validation;
- at least one context is inside a fixed window;
- every emitted active-zone context has matching verified `OPEN` or
  `EARLY_CLOSE` calendar evidence;
- no higher-precedence status applies.

`VALID` means deterministic standalone context evidence only.

### 16.5 NONE

Return `NONE` for complete valid inputs when:

- observation tuples are empty;
- every observation is outside all four fixed windows;
- every candidate observation derives an ineligible weekend trade date;
- every candidate is closed by verified calendar or exact session boundaries;
- no `CALENDAR_UNVERIFIED` context exists.

`SESSION_CLOSED` is a non-signal context result and does not make the overall
result `VALID`.

## 17. Locked DST, Calendar-Coverage, and Failure Precedence

The analyzer processes timestamps as UTC instants. DST conversion is therefore
unambiguous even when a New York local wall-clock hour repeats or does not exist.

Locked rules:

- winter and summer offsets follow the installed timezone database;
- no hard-coded `UTC-5` or `UTC-4` branch is allowed;
- equivalent UTC instants yield identical local membership;
- spring-forward and fall-back boundaries are tested explicitly;
- caller-supplied local naive datetimes are never accepted;
- calendar entries use UTC session-boundary instants and therefore do not rely
  on ambiguous local `fold` inference;
- adding a future calendar entry cannot alter a prior verified context;
- adding a calendar entry for an already analyzed trade date is historical
  repair and is not eligible prefix extension;
- missing calendar coverage yields `UNKNOWN`;
- contradictory supplied calendar evidence yields `INVALID`;
- `INVALID` has precedence even when an earlier missing calendar entry already
  established `UNKNOWN`.

## 18. Locked Prefix-Invariance Contract

A prefix comparison is eligible only when:

- the earlier observations are an exact complete tuple prefix;
- every calendar entry required by the earlier observations is identical;
- calendar and timezone-data versions are identical;
- the prefix ends after a complete atomic observation group;
- appended observations have strictly later indices and timestamps;
- appended calendar entries cover only strictly later derived trade dates;
- no historical insertion, repair, reorder, mutation, or replacement occurs.

For an eligible prefix:

- prior contexts remain byte-for-byte identical;
- prior snapshot IDs remain byte-for-byte identical;
- prior context-ID prefixes remain identical;
- only strictly later contexts and snapshots may append.

Ineligible changes include:

- same-effective-moment append;
- duplicate observation;
- historical observation insertion;
- historical calendar entry insertion or repair;
- calendar-version change;
- timezone-data-version change;
- calendar-entry reorder;
- partial atomic group;
- malformed-evidence repair.

Ineligible input is validated normally and may return `INVALID`, `UNKNOWN`, or
`NONE`. It must not be silently reordered or reinterpreted as an eligible
prefix.

## 19. Locked Inline Synthetic 44-Case Unit-Test Matrix

The future test module must retain exactly the following sequential logical case
numbers. Parameterization may increase physical collection but may not add,
remove, skip, rename, or merge away logical case numbers.

1. Missing `observations` or `calendar_entries` top-level context returns
   `UNKNOWN`; malformed top-level text still has `INVALID` precedence.
2. Complete empty tuples return `NONE` with empty contexts and snapshots.
3. Instrument, timeframe, calendar version, timezone-data version, and
   equivalent UTC timestamp normalization are deterministic.
4. `KillZoneObservation` exact type, fields, aware timestamp, non-negative
   non-boolean index, and exact `is_closed=True` are enforced fail closed.
5. Observation indices and timestamps are independently strictly increasing;
   duplicate, decreasing, crossed, and non-tuple evidence is not sorted.
6. `KillZoneCalendarEntry` exact frozen fields, calendar-version equality, exact
   trade-date type, and exact enum membership are enforced.
7. Calendar entries are strictly increasing and unique; duplicate, reordered,
   forked, conflicting-version, and weekend-open entries are `INVALID`.
8. `OPEN` and `EARLY_CLOSE` require exact aware open/close timestamps;
   `SESSION_CLOSED` requires both absent; impossible interval, duration, and
   local-date reconciliation are `INVALID`.
9. `America/New_York` is the only accepted timezone; a fixed offset,
   caller-supplied alias, or machine-local fallback is rejected.
10. Runtime timezone unavailability or unknowable timezone-data version returns
    `UNKNOWN`; supplied/runtime version mismatch returns `INVALID`.
11. Exact `ASIA` start at `20:00` is included in winter and summer.
12. Exact local midnight is excluded from `ASIA`.
13. Exact `LONDON` start `02:00` is included and exact end `05:00` is excluded.
14. Exact `NEW_YORK_AM` start `07:00` is included and exact end `10:00` is
    excluded.
15. Exact `NEW_YORK_PM` start `13:00` is included and exact end `16:00` is
    excluded.
16. One microsecond before each start and at/after each end is outside that
    window; the four windows never overlap.
17. `ASIA` assigns the following local calendar date as trade date.
18. Sunday `20:00` derives Monday and may qualify; Friday `20:00` derives
    Saturday and is `SESSION_CLOSED`.
19. London, New York AM, and New York PM retain their local calendar date as
    trade date.
20. Complete observations outside every fixed window return `NONE` without
    requiring calendar coverage.
21. Verified `OPEN` session boundaries are start-inclusive and end-exclusive.
22. Verified `SESSION_CLOSED` holiday evidence emits no active zone and cannot
    return `VALID`.
23. Verified `EARLY_CLOSE` permits pre-close membership and truncates an
    overlapping window exactly at the close instant.
24. Candidate before session open or at/after session close is effectively
    `SESSION_CLOSED`.
25. Missing candidate trade-date calendar entry emits exact
    `CALENDAR_UNVERIFIED` context plus snapshot and returns `UNKNOWN`.
26. Missing calendar coverage never relabels a later observation as the first
    verified occurrence and cannot be used for decision research.
27. Winter UTC-to-New-York conversion uses the database winter offset and
    produces exact window membership.
28. Summer UTC-to-New-York conversion uses the database daylight offset and
    produces exact window membership.
29. Spring-forward conversion, nonexistent local wall time, and exact window
    boundaries remain deterministic from UTC input.
30. Fall-back conversion, repeated local wall time, and exact window boundaries
    remain deterministic from UTC input.
31. Naive timestamps, invalid offsets, malformed timezone objects, and nested
    conversion exceptions are contained as `INVALID`.
32. Kill-zone context is non-directional; no direction, bias, signal, score,
    confidence, or trade field exists or is inferred.
33. Multiple observations across zones, local dates, and instruments produce
    deterministic chronological contexts independent of hash, set, or
    dictionary order.
34. Later determinable malformed observation preserves strictly prior contexts
    and snapshots, promotes no failing or later group, and returns `INVALID`;
    unknowable moment claims no prefix.
35. Later determinable malformed calendar evidence preserves strictly prior
    contexts and snapshots, promotes no failing or later group, and returns
    `INVALID`.
36. Final precedence is exactly
    `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`; version 1 has no reachable
    valid `AMBIGUOUS` branch.
37. `CONTEXT` identity enforces every required/forbidden parameter, all locked
    cross-field combinations, normalization, field sensitivity, and exact
    timezone token.
38. `SNAPSHOT` identity enforces every required/forbidden parameter, ordered
    unique non-empty complete context history, effective-moment sensitivity, and
    malformed-hash containment.
39. Identity builder rejects unknown kinds, booleans as indices, naive
    timestamps, invalid dates, invalid enums, unexpected aliases, and nested
    exceptions using only `TypeError` or `ValueError`.
40. Analyzer and builder exact keyword-only parameter names and defaults are
    locked; every public dataclass has exact fields, annotations, defaults, and
    frozen state; enum values, constants, version, and exports are exact.
41. Repeating identical inputs is byte-stable and deterministic across winter,
    summer, open, early-close, closed, and unverified evidence.
42. Strictly later complete append preserves every prior context and snapshot;
    same-effective append, historical observation/calendar insertion, repair,
    reorder, or version change is not an eligible prefix.
43. Atomic context/snapshot promotion, no transition lifecycle, no retroactive
    verification, and immutable complete-history snapshots are enforced.
44. The standalone module has no file I/O, external calendar/API, external
    fixture, SMC-event aggregation, config, runtime, strategy, risk, execution,
    registration, network, or integration dependency; focused and full
    regression suites pass.

The matrix contains exactly `44` logical cases.

## 20. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing file;
- creation of any file other than the future reserved paths after later gates;
- external fixtures, calendars, holiday files, timezone files, or market data;
- requirements or dependency-manifest edits;
- edits to completed SMC v2 dependencies;
- legacy SMC imports or modifications;
- SMC event, signal, trace, or context aggregation;
- Inducement or Volume Profile code;
- runtime flags, CLI, configuration, package exports, adapters, or registration;
- calendar download, network, exchange, broker, CME, Sierra, or external API;
- fixed UTC offsets or machine-local timezone fallback;
- signal, bias, confidence, score, filter, trade, risk, paper, broker, or live
  semantics;
- tuning from backtest, OOS, PnL, entry, exit, or outcome evidence;
- paper or live progression.

## 21. Mandatory Pre-Implementation Gates

Python work remains blocked until all of the following occur:

1. this decision record passes an independent final documentation audit;
2. staging is explicitly authorized for this one documentation file;
3. cached diff and scope audit pass;
4. a documentation-only commit is explicitly authorized and created;
5. push preflight passes;
6. remote export risk is explicitly accepted and the documentation commit is
   pushed;
7. post-push audit confirms `HEAD`, local `origin/main`, and live remote `main`;
8. all four reserved target paths remain absent;
9. calendar and timezone-data version behavior is accepted exactly as written;
10. focused/full baseline and dependency hashes remain unchanged;
11. an explicit human decision operationally activates only the exact future
    three-path implementation exception.

No gate may be inferred from completion of an earlier capability.

## 22. Implementation Stop Conditions

The future task must stop without fallback if:

- any reserved target already exists;
- any path outside the exact three-path scope changes;
- dependency hash or commit evidence changes unexpectedly;
- `America/New_York` or a reproducible timezone-data version is unavailable;
- implementation requires a requirements edit, external calendar, external
  fixture, file read, network, API, or calendar download;
- trade-date assignment, DST conversion, session interval, early-close, or
  calendar coverage cannot be evaluated without guessing;
- a fixed UTC offset or machine-local timezone appears necessary;
- observation or calendar chronology cannot be validated without silent sort;
- context or snapshot identity schemas cannot be enforced exactly;
- malformed required fields leak exceptions;
- atomic promotion, chronological cutoff, or prefix invariance fails;
- a directional, score, signal, trade, or integration field appears necessary;
- focused tests or full regression fail;
- implementation appears necessary to resolve ambiguity in this decision.

A stop condition freezes the task. It does not authorize widened scope, silent
coercion, silent sorting, relaxed validation, timezone fallback, calendar repair,
tuning, or favorable reinterpretation.

## 23. Completion, Rollback, Promotion, and Global-Freeze Gates

Later implementation completion requires:

- test-first evidence;
- independent review of every changed line;
- exact three-path reconciliation;
- exact public API reflection evidence;
- exact `44` logical-case reconciliation;
- focused Kill-zone tests passing;
- full regression suite passing;
- artifact SHA-256, bytes, lines, and formatting evidence;
- proof that no current production import or execution path changed;
- proof that no sensitive, generated, calendar, or external evidence was added;
- a completed Kill-zone checkpoint;
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created implementation
paths and requires explicit instruction before destructive removal. After
commit, rollback must use a bounded revert of the task commit rather than
history rewriting. Every rollback requires focused tests, full regression, and
clean-scope audit.

Successful implementation would prove only standalone deterministic Kill-zone
context conformance. It would not prove trading edge, OOS improvement, strategy
value, readiness, threshold approval, paper approval, live approval, or
permission for Inducement, Volume Profile, context aggregation, trace
integration, decision integration, or execution work.

The global code freeze remains active outside the exact future task. No later
module inherits authorization from this record.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `CAPABILITY=KILL_ZONE_CONTEXT`
- `IMPLEMENTATION_ORDER_POSITION=10`
- `DOCUMENTATION_ONLY=True`
- `EXACT_DOCUMENTATION_PATHS_CHANGED=1`
- `FUTURE_IMPLEMENTATION_PATHS_RESERVED=3`
- `INLINE_SYNTHETIC_LOGICAL_CASES=44`
- `IDENTITY_KINDS=CONTEXT,SNAPSHOT`
- `EXTERNAL_FIXTURE_AUTHORIZED=False`
- `EXTERNAL_CALENDAR_AUTHORIZED=False`
- `EXTERNAL_API_AUTHORIZED=False`
- `FIXED_UTC_OFFSET_AUTHORIZED=False`
- `DIRECTIONAL_SEMANTICS_AUTHORIZED=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `PAPER_PROGRESSION_AUTHORIZED=False`
- `LIVE_PROGRESSION_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`

This is a documentation decision only. The next permitted action is an
independent final audit of this one file.
