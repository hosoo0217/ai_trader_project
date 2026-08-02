# GC Futures Strict Chronological Backtest Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `GC-FUTURES-STRICT-CHRONOLOGICAL-BACKTEST-2026-08-02`.
- Decision version: `1`.
- Baseline branch: `main`.
- Baseline Git commit:
  `a2d05adf5a717ed4784ea9c93ca7bacef8eaeaa7`.
- Baseline full regression: `1778 passed` with `-p no:cacheprovider`.
- Work type: documentation-only bounded freeze-lift decision.
- Status: `READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`.
- Global code freeze: `ACTIVE`.
- Python implementation, tests, fixtures, integration, strategy, AI training,
  paper, broker, and live authorization: `NOT GRANTED`.

This record locks the first authoritative strict-chronology foundation for future
GC Futures research. It does not claim profitability, replace historical frozen
evidence, create a strategy, train a model, or authorize execution.

## 2. Problem Statement and Selected Direction

The legacy rolling `BacktestRunner` is preserved for historical comparability,
but it is not accepted as strict chronological single-position portfolio
evidence because:

- it schedules rolling decision windows independently of prior simulated exits;
- it supplies the full remaining suffix to each exit simulation;
- documented evidence found `44` of `68` realized outcomes exited after the next
  scheduled entry;
- timestamp parse failure may fall back to current wall-clock UTC;
- its paper-flow dependency reuses one candle table under multiple timeframe
  labels;
- its paper-flow context hardcodes CRT confirmation and other provisional state.

The selected direction is a new isolated GC-only event-driven runner. It will
consume immutable caller-supplied research candidates and canonical bars. It
will not call the legacy strategy, paper flow, detector stack, AI scorer, risk
engine, broker, journal, or report generators.

## 3. Locked Baseline and Evidence Preservation

The following exact baseline artifacts remain frozen comparator evidence:

- `core/backtest_runner.py`
  - SHA-256:
    `6596254199AEDB9AE16584D0228B511D5C50525A117F2932AD293A0B754A16E0`;
- `core/paper_trading_flow.py`
  - SHA-256:
    `B72F66692BE035E79CFFD2E6FE449397B845BB08D3610AE1A00A8C52669CEAB4`;
- `core/exit_simulator.py`
  - SHA-256:
    `852EC94DE37F28150DC83F64D978EBC447C8AD2FE9F3D8ACD468AF4591710285`;
- `docs/pre_registered_oos_regime_validation_plan.md`
  - SHA-256:
    `D858B66D03F49AD7149E38042F4C7430F3875ABFB246ABD4AE85CE6BDA932649`;
- `docs/independent_historical_dataset_intake.md`
  - SHA-256:
    `E1E04D9AE4C23A1AF0DFDF8F29A24C32E80C3BF486E2B4576DFC123C8BF8E461`;
- `docs/gc_futures_ai_strategy_training_decision.md`
  - SHA-256:
    `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688`.

The prior `VALID_OOS_EVIDENCE — PERFORMANCE_FAILED` classifications and temporal
overlap findings remain authoritative for their exact frozen runners. A future
strict runner creates a new evidence lineage and may not overwrite, relabel, or
retroactively replace those results.

## 4. Exact Documentation-Only Change

The only authorized changed path for this decision task is:

- `docs/gc_futures_strict_chronological_backtest_freeze_lift_decision.md`.

No Python, test, fixture, dependency, configuration, private data, report, model,
or other documentation path is authorized in this task. Stage, commit, push,
implementation, integration, paper, broker, and live actions require separate
explicit steps.

## 5. Reserved Future Implementation Scope

If this decision later passes independent audit, human acceptance, post-push
readiness, and a bounded implementation authorization, the first implementation
scope is reserved to exactly:

- `core/gc_chronological_backtest.py`;
- `tests/test_gc_chronological_backtest.py`;
- `docs/gc_futures_strict_chronological_backtest_checkpoint.md`.

No external fixture is reserved. Tests must use inline synthetic immutable data.

The following remain forbidden:

- `core/backtest_runner.py`, `core/paper_trading_flow.py`, and
  `core/exit_simulator.py`;
- `core/decision_engine.py`, risk, broker, storage, reporting, and main paths;
- SMC, CRT, Order Flow, AI, feature, label, model, and strategy paths;
- requirements, configuration, package exports, CLI, private data, generated
  evidence, paper, and live integration.

## 6. Capability Boundary and Non-Goals

The future V1 runner will:

- validate one canonical GC contract and one fully closed 5m bar stream;
- validate immutable caller-supplied research candidates;
- process every bar and candidate group in causal order;
- enforce at most one open simulated position;
- generate deterministic candidate decisions, trades, and equity snapshots;
- account exactly for tick PnL, commissions, fees, and slippage;
- return immutable diagnostic evidence and fail-closed statuses.

It will not:

- discover or score setups;
- call an analyzer or AI model;
- generate BUY/SELL direction;
- size risk from account state;
- optimize any parameter;
- resample or align multiple timeframes;
- download data or calendar evidence;
- model order-book queue, latency, partial fills, margin, funding rules, or taxes;
- replace a broker, paper system, or live simulator;
- establish strategy profitability or readiness.

## 7. Exact Constants, Enums, and Normalization

Future constants are locked to:

```python
GC_CHRONOLOGICAL_BACKTEST_VERSION = "GC-CHRONOLOGICAL-BACKTEST-V1"
GC_CHRONOLOGICAL_TIMEFRAME = "5M"
GC_CHRONOLOGICAL_TIMEZONE = "America/New_York"
```

Future exact enums are:

```python
class GCBacktestDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class GCBacktestRunStatus(str, Enum):
    COMPLETE = "COMPLETE"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"

class GCCandidateDecisionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_POSITION_OPEN = "REJECTED_POSITION_OPEN"
    REJECTED_AMBIGUOUS_GROUP = "REJECTED_AMBIGUOUS_GROUP"
    REJECTED_SESSION = "REJECTED_SESSION"
    REJECTED_ENTRY_GEOMETRY = "REJECTED_ENTRY_GEOMETRY"
    PENDING_ENTRY = "PENDING_ENTRY"

class GCTradeExitReason(str, Enum):
    STOP_LOSS = "STOP_LOSS"
    TARGET = "TARGET"
    EXPIRY_CLOSE = "EXPIRY_CLOSE"
    SESSION_CLOSE = "SESSION_CLOSE"
```

Instrument and contract tokens are stripped and uppercased. Timeframe must
normalize to exact `5M`. Empty, generic `GC` without an exact contract token,
`XAUUSD`, continuous-contract aliases, and silently roll-adjusted identities are
invalid.

## 8. Immutable Canonical Bar Contract

The future frozen input model is exactly:

```python
@dataclass(frozen=True)
class GCChronologicalBar:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    volume: int
    is_closed: bool
```

Rules:

- `index` is a nonnegative exact integer and is independently strictly
  increasing;
- `timestamp` is the bar-close moment, timezone-aware, UTC-normalized, unique,
  and independently strictly increasing;
- each adjacent in-session pair is exactly five minutes apart unless an exact
  calendar/session boundary explains the gap;
- OHLC values are exact integers, booleans are forbidden, and
  `low_tick <= open_tick, close_tick <= high_tick`;
- `volume` is a nonnegative exact integer; negative, fractional, boolean, or
  non-finite representations are invalid;
- `is_closed` is exactly `True`;
- duplicate, out-of-order, malformed, naive, open, or future-incomplete bars are
  invalid;
- no silent sorting, deduplication, interpolation, forward fill, or timestamp
  fallback is permitted.

The runner never calls `datetime.now()` and never infers a missing bar from wall
clock time.

## 9. Immutable Session Calendar Contract

The future runner directly consumes canonical frozen
`smc.kill_zones.KillZoneCalendarEntry` values and validates their exact
`smc.kill_zones.KillZoneSessionStatus` enum. These are the only allowed direct
SMC dependency imports. It does not call external calendar or timezone APIs.

Rules:

- the tuple is strictly increasing and unique by trade date;
- `calendar_version` is nonempty and identical for the complete run;
- timestamps are aware UTC and reconcile through exact IANA
  `America/New_York` runtime rules;
- a standard `OPEN` trade date `D` requires local open `D - 1 calendar day`
  at `18:00:00` inclusive and local close `D` at `17:00:00` exclusive;
- `EARLY_CLOSE` requires that same canonical open and an explicit calendar close
  strictly after open and no later than local `D 17:00:00`;
- the daily `17:00:00` to `18:00:00` maintenance interval is never eligible;
- `OPEN` and `EARLY_CLOSE` require exact open and close timestamps;
- `SESSION_CLOSED` forbids a tradable interval;
- open is earlier than close and the local dates reconcile with the trade date;
- every bar and candidate must map to exactly one supplied calendar state;
- missing required calendar coverage is `UNKNOWN` only when no supplied
  independently determinable malformed evidence exists;
- malformed, conflicting, duplicate, in-horizon missing, or version-mismatched
  calendar evidence is `INVALID`.

No new entry may be opened on a session-closed date or on/after the applicable
session close. An open position must be closed by the final eligible session bar
according to Section 14.

## 10. Immutable Research Candidate Contract

The future frozen input model is exactly:

```python
@dataclass(frozen=True)
class GCBacktestCandidate:
    candidate_id: str
    direction: GCBacktestDirection
    decision_index: int
    decision_timestamp: datetime
    stop_tick: int
    target_tick: int
    max_holding_bars: int
    contracts: int
```

Rules:

- `candidate_id` is one lowercase 64-character hexadecimal immutable foreign ID;
- direction is exact BUY or SELL and is never inferred by the runner;
- decision index/timestamp must exactly match one supplied fully closed bar;
- candidates are nondecreasing by normalized decision moment and same-moment
  groups are contiguous;
- within one same-moment group, tuple order has no chronological meaning;
- identical repeated candidate IDs are invalid;
- more than one distinct candidate in the same effective group is ambiguous and
  none is accepted;
- `max_holding_bars` and `contracts` are positive exact integers;
- BUY requires `stop_tick < decision close < target_tick`;
- SELL requires `target_tick < decision close < stop_tick`;
- stop and target are immutable candidate-time structural boundaries;
- the runner does not validate or recompute the foreign candidate identity from
  unavailable detector/model objects;
- missing candidate provenance needed for strategy approval is outside this
  runner and cannot be invented.

## 11. Immutable Configuration Contract

The future frozen configuration is exactly:

```python
@dataclass(frozen=True)
class GCChronologicalBacktestConfig:
    instrument: str
    timeframe: str
    timezone_data_version: str
    tick_size: Decimal
    tick_value: Decimal
    starting_balance: Decimal
    entry_slippage_ticks: int
    exit_slippage_ticks: int
    commission_per_side_per_contract: Decimal
    exchange_fee_per_side_per_contract: Decimal
    maximum_contracts: int
```

Rules:

- `timezone_data_version` is stripped, nonempty, and must exactly equal the
  normalized runtime timezone-data version used for `America/New_York`;
- unavailable runtime timezone data, unavailable `America/New_York`, or version
  mismatch is invalid and no run identity may be created;
- Decimal monetary values are finite, exact, and context-independent;
- `tick_size`, `tick_value`, and `starting_balance` are positive;
- costs are nonnegative;
- slippage ticks are nonnegative exact integers;
- `maximum_contracts` is a positive exact integer;
- candidate contracts cannot exceed the configured maximum;
- signed zero serializes as canonical `0.0`;
- floats, booleans, NaN, infinity, locale-formatted text, and implicit defaults
  are invalid;
- every exact numerical value is supplied by a later pre-registered experiment;
  the runner contains no profitable-looking default.

## 12. Exact Candidate Group and Entry Processing

Processing order for each fully closed bar group is:

1. validate the complete supplied bar/calendar/candidate evidence for the group;
2. at the bar open, resolve a strictly prior pending candidate against that
   immutable open and session evidence;
3. if accepted, record `ACCEPTED`, open the position at that bar open, and allow
   the same bar to be holding bar `1` without using its close for entry;
4. apply stop/target/expiry/session processing to the open position only after
   the pending-entry phase;
5. record any position-closing trade and equity snapshot;
6. evaluate the complete candidate group whose decision moment is this bar close;
7. if no position remains and exactly one valid candidate exists, record
   `PENDING_ENTRY` for the next chronological bar;
8. never enter on the candidate decision bar.

Pending entry rules:

- entry uses the next supplied eligible bar's open;
- that bar index is strictly greater and its bar-close timestamp is strictly
  later than the decision moment;
- BUY fill tick is `next_open_tick + entry_slippage_ticks`;
- SELL fill tick is `next_open_tick - entry_slippage_ticks`;
- after slippage, BUY requires `stop_tick < fill_tick < target_tick`;
- after slippage, SELL requires `target_tick < fill_tick < stop_tick`;
- failed geometry records `REJECTED_ENTRY_GEOMETRY` and opens no position;
- no later bar may rescue or relabel a rejected or missing next-bar entry;
- no next eligible bar before session/data end leaves a pending incomplete result
  and returns `UNKNOWN`.

One accepted candidate therefore has exactly two immutable decision events:
`PENDING_ENTRY` at its decision-bar close followed by `ACCEPTED` at the next
eligible bar open. A rejected candidate has exactly one rejection event unless a
prior `PENDING_ENTRY` had already been recorded, in which case the rejection is
its second and terminal event. Decision tuples are nondecreasing by normalized
timestamp; equal-time previous-close `PENDING_ENTRY` and next-open terminal
events preserve that causal order. Same-moment independent candidate rejection
records use ascending `candidate_id` only as an output-order tie-break, never as
market chronology.

Candidates arriving while a position or earlier pending entry exists are
validated, recorded as `REJECTED_POSITION_OPEN`, never queued, and never replayed
after the position closes.

Complete-group validation precedes position-state rejection: duplicate identity
remains `INVALID` and multiple distinct same-moment candidates remain
`AMBIGUOUS` even when a position is open. `REJECTED_POSITION_OPEN` applies only
to one otherwise-valid candidate in its effective group.

## 13. Strict Single-Position Lifecycle

At every causal moment the runner has exactly one of:

- no position and no pending entry;
- one pending entry;
- one open position.

There is never more than one open position. Pyramiding, scaling, reversal,
partial entry, partial exit, averaging, hedging, and simultaneous independent
positions are forbidden.

An accepted pending candidate becomes one immutable position at the exact next
eligible bar open. Its entry timestamp is exactly the next bar's normalized
close timestamp minus five minutes; stop/target exits are attributed to the
normalized close timestamp of the first bar proving the touch. Its direction,
fill, stop, target, contracts, entry moment, and expiry count never mutate.

Candidate decisions rejected while open do not affect the open position or its
expiry. A close and a new candidate decision may occur in the same bar group,
but any new accepted candidate remains pending until the following eligible bar.

## 14. Exact Exit, Collision, Expiry, and Session Precedence

For every open position bar, precedence is exactly:

1. validate bar and session evidence;
2. compute stop and target touches from the immutable boundaries;
3. if both are touched, choose stop loss conservatively;
4. otherwise choose the single touched boundary;
5. if neither is touched and the bar is the locked expiry bar, close at that
   bar's close;
6. if neither is touched and this is the final eligible session bar, close at
   that bar's close;
7. otherwise remain open.

The entry bar counts as holding bar `1`. Expiry occurs after processing stop and
target on holding bar `max_holding_bars`.

Adverse exit slippage is:

- BUY: final exit is the locked raw exit minus `exit_slippage_ticks`;
- SELL: final exit is the locked raw exit plus `exit_slippage_ticks`;
- a target raw exit is exactly the target boundary, so a target gap receives no
  favorable price improvement;
- a BUY gap-through stop raw exit is `min(open_tick, stop_tick)`;
- a SELL gap-through stop raw exit is `max(open_tick, stop_tick)`;
- expiry and session-close raw exits are the bar close.

There is no hidden clamp after adverse slippage. Pathological but valid large
slippage therefore remains visible in PnL instead of being silently improved.

Session close has no priority over a stop or target touched in the same final
bar. Missing the required final session bar while a position remains open is
`UNKNOWN`; the runner does not synthesize a close.

## 15. Exact Decimal PnL and Cost Accounting

All accounting uses Decimal and exact integer tick differences.

For one completed trade:

```text
BUY gross_ticks  = exit_tick - entry_tick
SELL gross_ticks = entry_tick - exit_tick
gross_pnl = gross_ticks * contracts * tick_value
round_trip_cost = 2 * contracts *
                  (commission_per_side_per_contract +
                   exchange_fee_per_side_per_contract)
net_pnl = gross_pnl - round_trip_cost
balance_after = balance_before + net_pnl
```

Slippage is already embedded in entry and exit ticks and is not subtracted a
second time. Costs are charged on both sides only after an entry is filled. A
rejected candidate has no fee or PnL.

Every trade and equity snapshot must reconcile exactly. When configuration and a
trustworthy prefix are canonical, final balance equals starting balance plus the
ordered sum of promoted completed net PnL even if a determinably later group
ends `INVALID`, `UNKNOWN`, or `AMBIGUOUS`. `final_balance` is `None` only when the
configuration itself is invalid or no trustworthy chronological prefix can be
established. No rounding, binary-float conversion, hidden financing, or
unreported cost is allowed.

## 16. Exact Frozen Output Models

The future public output models are exactly:

```python
@dataclass(frozen=True)
class GCCandidateDecision:
    decision_id: str
    candidate_id: str
    status: GCCandidateDecisionStatus
    index: int
    timestamp: datetime
    reason: str

@dataclass(frozen=True)
class GCBacktestTrade:
    trade_id: str
    candidate_id: str
    direction: GCBacktestDirection
    contracts: int
    entry_index: int
    entry_timestamp: datetime
    entry_tick: int
    stop_tick: int
    target_tick: int
    exit_index: int
    exit_timestamp: datetime
    exit_tick: int
    exit_reason: GCTradeExitReason
    gross_ticks: int
    gross_pnl: Decimal
    total_cost: Decimal
    net_pnl: Decimal

@dataclass(frozen=True)
class GCEquitySnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    balance: Decimal
    completed_trade_ids: tuple[str, ...]

@dataclass(frozen=True)
class GCChronologicalBacktestResult:
    status: GCBacktestRunStatus
    run_id: str | None
    candidate_decisions: tuple[GCCandidateDecision, ...] = ()
    trades: tuple[GCBacktestTrade, ...] = ()
    equity_snapshots: tuple[GCEquitySnapshot, ...] = ()
    final_balance: Decimal | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

No mutable list, dataframe, model score, confidence, detector result, risk plan,
order, journal, or live field appears in public outputs.

## 17. Exact Keyword-Only Public API

The future public functions are exactly:

```python
def make_gc_chronological_backtest_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    config: GCChronologicalBacktestConfig,
    bar_digest: str | None = None,
    calendar_digest: str | None = None,
    candidate_digest: str | None = None,
    candidate_id: str | None = None,
    candidate_status: GCCandidateDecisionStatus | None = None,
    reason: str | None = None,
    direction: GCBacktestDirection | None = None,
    contracts: int | None = None,
    entry_index: int | None = None,
    entry_timestamp: datetime | None = None,
    entry_tick: int | None = None,
    stop_tick: int | None = None,
    target_tick: int | None = None,
    exit_index: int | None = None,
    exit_timestamp: datetime | None = None,
    exit_tick: int | None = None,
    exit_reason: GCTradeExitReason | None = None,
    gross_ticks: int | None = None,
    gross_pnl: Decimal | None = None,
    total_cost: Decimal | None = None,
    net_pnl: Decimal | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    balance: Decimal | None = None,
    completed_trade_ids: tuple[str, ...] = (),
) -> str:
    ...

def run_gc_chronological_backtest(
    *,
    bars: tuple[GCChronologicalBar, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    candidates: tuple[GCBacktestCandidate, ...] | None,
    config: GCChronologicalBacktestConfig,
) -> GCChronologicalBacktestResult:
    ...
```

All parameters are keyword-only. No permissive `**kwargs`, positional alias,
mutable default, dataframe, callback, strategy, model, broker, or external API
parameter is permitted.

## 18. Deterministic RUN, DECISION, TRADE, and SNAPSHOT Identities

Identity kinds are exactly `RUN`, `DECISION`, `TRADE`, and `SNAPSHOT`. Every
identity uses canonical JSON with sorted keys, compact separators, exact enum
values, uppercase instrument/timeframe, UTC microsecond timestamps serialized as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`, canonical Decimal text, and lowercase SHA-256.

Before ID construction, the analyzer computes three lowercase SHA-256 source
digests from canonical JSON ordered tuples:

- `bar_digest` binds every normalized bar field in caller order;
- `calendar_digest` binds every normalized calendar field, including calendar
  version, status, and optional session moments, in caller order;
- `candidate_digest` binds every normalized candidate field, not merely its
  opaque foreign ID. Effective groups remain in caller-supplied chronological
  order, while members inside one same-moment group are canonically serialized
  by ascending `candidate_id` because their supplied tuple order has no
  chronological meaning.

The three digests are available only when their complete collections are
canonical. A missing or malformed collection cannot receive a fabricated digest
and the analyzer returns `run_id=None`. Valid empty tuples have deterministic
empty-tuple digests. This prevents two materially different inputs from sharing
one run identity.

Common required parameters for every identity kind are `identity_kind`,
`instrument`, `timeframe`, and `config`. Every remaining parameter is exactly
required or forbidden as follows:

- `RUN` requires `bar_digest`, `calendar_digest`, and `candidate_digest`; all
  candidate-decision, trade, and snapshot fields are forbidden.
- `DECISION` requires `candidate_id`, `candidate_status`, `reason`,
  `effective_index`, and `effective_timestamp`; all three source digests and all
  trade/snapshot-only fields are forbidden.
- `TRADE` requires `candidate_id`, `direction`, `contracts`, every entry,
  boundary, exit, exit-reason, gross-tick, PnL, and cost field; all three source
  digests, candidate-status/reason, snapshot moment/balance/history fields are
  forbidden.
- `SNAPSHOT` requires `effective_index`, `effective_timestamp`, `balance`, and
  `completed_trade_ids`; all three source digests and all candidate-decision and
  trade fields are forbidden.

The builder verifies config instrument/timeframe exact normalized equality with
the common arguments. RUN recomputes no opaque foreign candidate ID, but its
candidate digest binds the full supplied candidate evidence. DECISION validates
the exact status/reason pairing. TRADE recomputes exact geometry and accounting.
SNAPSHOT requires ordered unique complete trade-ID history.

Unknown kinds, missing required fields, supplied forbidden fields, malformed
hashes, impossible direction geometry, impossible lifecycle, incorrect PnL,
duplicate history, and nested malformed values raise only TypeError or
ValueError. No AttributeError, KeyError, IndexError, Decimal exception, or other
internal exception may leak.

Exact decision reason tokens are:

- `PENDING_ENTRY` -> `NEXT_BAR_ENTRY_PENDING`;
- `ACCEPTED` -> `CANDIDATE_ACCEPTED_NEXT_BAR`;
- `REJECTED_POSITION_OPEN` -> `POSITION_ALREADY_OPEN`;
- `REJECTED_AMBIGUOUS_GROUP` -> `AMBIGUOUS_SAME_MOMENT_CANDIDATES`;
- `REJECTED_SESSION` -> `SESSION_NOT_ELIGIBLE`;
- `REJECTED_ENTRY_GEOMETRY` ->
  `ENTRY_GEOMETRY_INVALID_AFTER_SLIPPAGE`.

`NEXT_ELIGIBLE_BAR_UNAVAILABLE` is an exact result blocking-reason token, not a
DECISION identity reason: the immutable pending event is never relabeled merely
because the supplied horizon ends.

## 19. Atomic Processing, Status Precedence, and Prior Evidence

Each bar effective group is processed atomically. Validation uses an immutable
pre-group state. An `INVALID` or `UNKNOWN` validation-failed group promotes no
candidate decision, trade, equity snapshot, pending entry, or position mutation
from that group or later groups. A canonical multi-candidate group is different:
it atomically promotes exactly one `REJECTED_AMBIGUOUS_GROUP` decision per
distinct candidate in ascending `candidate_id` order, promotes no pending entry,
trade, or snapshot from that group, and processes no later group. A duplicate
candidate identity is `INVALID`, not ambiguous, and promotes no rejection event.

Final status precedence is exactly:

`INVALID > UNKNOWN > AMBIGUOUS > COMPLETE > NONE`

- `INVALID`: malformed or contradictory supplied evidence;
- `UNKNOWN`: canonical evidence is insufficient to resolve a required pending
  entry, open position, calendar/session close, or label horizon;
- `AMBIGUOUS`: one or more otherwise-valid same-moment candidate groups contain
  multiple distinct candidates, with no higher-precedence issue;
- `COMPLETE`: all supplied evidence and lifecycles resolve deterministically;
- `NONE`: valid inputs contain no candidate and no trade.

Strictly prior completed decisions, trades, and equity snapshots are preserved
byte-for-byte when a determinably later group fails. An unknowable malformed
effective moment permits no trustworthy chronological cutoff.

## 20. Complete-Prefix Invariance and Repeatability

Prefix invariance applies only when a valid prefix ends at a complete effective
group with:

- no pending entry;
- no open position;
- complete calendar coverage through the prefix;
- no partial same-moment candidate group.

Appending strictly later complete bars, calendar dates, and candidate groups may
add later evidence but cannot alter any earlier decision, trade, equity snapshot,
ID, PnL, reason, or status contribution.

A prefix ending with a pending entry or open position is intentionally not a
complete comparable prefix. Same-effective append, historical insertion,
calendar repair, candidate repair, data reorder, cost/config change, or source
replacement is not prefix extension and requires a new run identity.

Equivalent inputs and configuration must produce byte-for-byte identical output
regardless of Decimal context precision, machine locale, current wall clock, or
hash lexical order.

## 21. Inline Synthetic Exact 48-Case Unit-Test Matrix

Future implementation must preserve exactly these numbered logical cases;
parameterization may increase collected tests without changing the count:

1. Missing bars, calendar, candidates, or malformed supplied counterpart obeys
   fail-closed available-evidence precedence.
2. Empty valid bars/candidates returns `NONE` only with complete empty calendar
   semantics and no promoted evidence.
3. Exact GC contract normalization and generic GC/XAUUSD/continuous alias
   rejection.
4. Exact 5M-only enforcement and pseudo-MTF/other timeframe rejection.
5. Bar exact frozen fields, aware UTC, close-time semantics, and closed flag.
6. Bar OHLC geometry, integer ticks/volume, boolean/fraction/non-finite rejection.
7. Independently strictly increasing unique index and timestamp; no silent sort.
8. Exact five-minute continuity, standard `18:00` open, `17:00` close,
   maintenance, weekend, and calendar-explained session-gap behavior.
9. Calendar tuple/version, runtime tzdata binding, America/New_York availability,
   open/early-close/closed validation.
10. Missing calendar `UNKNOWN` versus malformed/conflicting calendar `INVALID`.
11. Candidate exact frozen fields, hash shape, direction, and moment reconciliation.
12. BUY and SELL stop/decision-close/target geometry.
13. Positive max-holding/contracts and maximum-contract enforcement.
14. Same-moment candidate group atomicity and order independence.
15. Duplicate candidate identity is `INVALID`; multiple distinct candidates are
    `AMBIGUOUS` with canonical ordered rejection decisions and no pending entry.
16. Candidate on closed/out-of-session/on-close moment is rejected deterministically.
17. Candidate is never entered on its decision bar.
18. BUY next-bar-open adverse entry slippage, previous-close/equal-open causal
    decision ordering, and exact fill.
19. SELL next-bar-open adverse entry slippage, exact open timestamp, and exact
    pending-to-accepted decision lifecycle.
20. Post-slippage entry geometry rejection and no later rescue.
21. Missing next eligible bar leaves pending entry `UNKNOWN` with no trade.
22. Exactly one open position; candidate while open is recorded and never queued.
23. Close plus new decision in one bar still enters no earlier than the following bar.
24. Bullish stop-only and target-only lifecycle.
25. Bearish stop-only and target-only lifecycle.
26. Both boundaries touched chooses stop loss conservatively in both directions.
27. BUY and SELL gap-through stop use worse open geometry.
28. Target gap-through receives no favorable improvement.
29. Entry bar counts as holding bar one.
30. Expiry stop/target precedence, then adverse close fill.
31. Session-final-bar stop/target precedence, then adverse close fill.
32. Missing required session-final bar with open position returns `UNKNOWN`.
33. No forced close or synthetic fill at data end.
34. Exact entry/exit slippage applied once in the adverse direction, including
    unbounded visible adverse slippage without optimistic target clamping.
35. Exact per-side commission and exchange fees for multiple contracts.
36. Positive/negative/zero gross ticks and exact Decimal net PnL.
37. Arbitrary-magnitude values, signed zero, half-like Decimal text, and Decimal
    context independence.
38. Balance and ordered trade-history reconciliation after multiple trades.
39. Candidate decision, trade, and equity outputs are frozen and immutable.
40. Exhaustive RUN required/forbidden schema; full bar/calendar/candidate digest
    sensitivity, bar/calendar caller-order sensitivity, same-moment candidate
    permutation independence, valid empty digests, and malformed collection
    `run_id=None` behavior.
41. Exhaustive DECISION required/forbidden schema, exact status/reason pairing,
    and pending blocking-reason non-relabeling.
42. Exhaustive TRADE schema, geometry, lifecycle, PnL, and malformed nested values.
43. Exhaustive SNAPSHOT schema, ordered unique history, balance, and moment sensitivity.
44. Exact keyword-only signatures/defaults, including source digests and decision
    reason, enum values, constants, config tzdata field, annotations, frozen
    state, and exports.
45. Later determinably malformed bar/calendar/candidate preserves strictly prior
    completed evidence and promotes nothing from the failing group onward.
46. Complete-prefix invariance; pending/open/same-effective/historical repair is
    explicitly ineligible.
47. Deterministic repeatability, no wall-clock/locale/hash-order dependence, and
    exact multi-trade ordering.
48. Exact three-path scope; only `smc.kill_zones.KillZoneCalendarEntry` and
    `smc.kill_zones.KillZoneSessionStatus` are allowed SMC dependency imports;
    all other legacy/AI/SMC/risk/broker imports forbidden; no integration,
    rollback, and global-freeze preservation.

## 22. Verification and Promotion Gates

Before future implementation promotion:

1. tests must be written before production behavior;
2. all 48 logical cases must reconcile exactly;
3. focused tests must pass with `-p no:cacheprovider`;
4. the full regression suite must pass with `-p no:cacheprovider`;
5. source, tests, and checkpoint require SHA-256, byte, line, and format evidence;
6. an independent code/test/scope/diff audit must pass;
7. exact-path staging and cached audit must pass;
8. local commit and push require separate explicit authorization;
9. no historical runner or evidence hash may change;
10. no integration or model-training claim may be made.

Passing unit tests proves deterministic contract implementation only. It does not
prove realistic fills, profitable strategy behavior, data acceptance, model
quality, paper readiness, or live readiness.

## 23. Rollback and Mandatory Stop Conditions

Rollback means discarding only the bounded unaccepted three-path implementation
and returning to its exact parent. Historical source, failure evidence, and
committed decisions remain immutable.

Work must stop if:

- exact GC contract, tick value, tick size, 5m close-time semantics, calendar,
  costs, slippage, or session boundary is unspecified;
- a required behavior cannot be expressed using integer ticks and Decimal;
- strict one-position chronology or complete-prefix invariance cannot be proved;
- implementing the runner requires modifying a forbidden legacy/runtime path;
- a strategy, detector, AI score, feature, label, risk engine, broker, journal,
  report, private data, or external API becomes required;
- wall-clock fallback, silent sort, forced data-end close, optimistic same-bar
  order, or hidden default is requested;
- failed OOS or overlap evidence would be overwritten or reinterpreted;
- public API, identities, matrix count, or three-path scope must broaden;
- any focused/full test, hash, formatting, audit, staging, freeze, or
  reproducibility gate fails.

## 24. Final Decision and Resume Checkpoint

The decision is:

`READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`

Locked state:

- one new isolated strict chronological GC research runner is selected;
- legacy runner and failed evidence remain frozen comparators;
- future implementation is limited to the exact reserved three paths;
- no external fixture, strategy, SMC, AI, risk, broker, paper, or live integration
  is authorized;
- implementation cannot start before independent audit, human acceptance,
  post-push readiness, and a new bounded authorization.

The next permitted action is an independent read-only audit of this exact
document. No stage, commit, push, Python, tests, fixtures, integration, model
training, paper, or live work is implied.

Global code freeze remains active.
