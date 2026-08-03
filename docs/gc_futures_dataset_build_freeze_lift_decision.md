# GC Futures Canonical Dataset Build Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `GC-FUTURES-CANONICAL-DATASET-BUILD-2026-08-03`.
- Decision version: `1`.
- Baseline branch: `main`.
- Baseline Git commit:
  `42d16e54ef3e2ed8f3f3434a3b0e3ba393ef5d86`.
- Baseline full regression: `1861 passed in 11.09s` with
  `-p no:cacheprovider`.
- Work type: documentation-only bounded freeze-lift decision.
- Status: `READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`.
- Global code freeze: `ACTIVE`.
- Python implementation, tests, fixtures, calendar acquisition, dataset
  generation, feature extraction, labeling, model training, integration, paper,
  broker, and live authorization: `NOT GRANTED`.

This record locks one deterministic, offline, price-only path from caller-read
Sierra Chart GC contract exports to immutable canonical contract segments. It
does not accept the current private intake as a training dataset, claim calendar
coverage, silently construct a continuous contract, define model features or
labels, train a model, or claim strategy profitability.

## 2. Problem Statement and Selected Direction

Eight GC exports have been copied without overwrite into an ignored private
intake and reconciled by SHA-256. Their bar-level structure is suitable for
further validation, but they are not yet a canonical research dataset because:

- the exported timestamps are in the chart timezone, not UTC;
- the chart used a fixed `07:00:00` to `06:59:59` Tokyo session boundary, while
  the canonical GC session must be interpreted through DST-aware
  `America/New_York` rules;
- the repository contains no versioned historical GC holiday/early-close
  calendar artifact or calendar-library dependency;
- overlapping individual contracts cannot be silently stitched;
- the earliest raw interval lacks earlier adjacent 2025 GC delivery contracts;
- the full `GCQ26` export overlaps the separately preserved 30-day OOS snapshot;
- Sierra Chart omits empty chart columns when `Include Columns With No Data` is
  disabled, so an absent five-minute timestamp is not automatically a verified
  zero-volume bar;
- the strict chronological runner accepts one exact contract per run and cannot
  consume a disguised multi-contract continuous series.

The selected direction is an isolated offline builder that parses exact
caller-supplied bytes, validates source provenance, converts timestamps, binds a
caller-supplied versioned calendar, selects contract regimes using only prior
completed-session volume, and emits separate non-price-adjusted contract
segments. It never mutates raw files and never fills missing market data.

## 3. Locked Baseline and Evidence Preservation

The following committed artifacts remain frozen dependencies:

- `docs/gc_futures_ai_strategy_training_decision.md`
  - SHA-256:
    `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688`;
- `docs/gc_futures_strict_chronological_backtest_freeze_lift_decision.md`
  - SHA-256:
    `97FCE19809855514A20ACFBA3CDB975DBF748BFADC91ED9879F6B3A86C3DAFAA`;
- `core/gc_chronological_backtest.py`
  - SHA-256:
    `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A`;
- `tests/test_gc_chronological_backtest.py`
  - SHA-256:
    `1C5D7588163B2DB340CEA59370A38F1789E3BF38BE7F036EF448E0A6E0BD343E`;
- `docs/gc_futures_strict_chronological_backtest_checkpoint.md`
  - SHA-256:
    `AF23956FDBB8477F9B99CDC434ED4F7769F4F3495C4DA20D661259E6A8C9EE8D`;
- `smc/kill_zones.py`
  - SHA-256:
    `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21`.

The ignored private intake remains immutable source evidence:

- intake manifest SHA-256:
  `A453840868EF85759979F70D5AC3C4B0FCCAF9A63EDEED7CCD85A264EB5A0E13`;
- intake README SHA-256:
  `EB9ACB14F8CD1C714DC0A4BDD62B09BADD9E64B81786075074DE6AE8DC3DC838`;
- eight copied export files, eight source/destination hash matches, and zero
  copy-audit issues;
- seven full exports totaling `173550` rows across `446` union dates;
- the `GCQ26` 30-day snapshot is an exact unchanged subset of the full `GCQ26`
  export with zero missing and zero changed rows.

These observations establish transport integrity only. They do not establish
calendar correctness, session completeness, roll correctness, feature safety,
label safety, or OOS validity. Existing failed OOS and temporal-overlap evidence
remains immutable and may not be weakened or relabeled.

## 4. Exact Documentation-Only Change

The only authorized changed path for this decision task is:

- `docs/gc_futures_dataset_build_freeze_lift_decision.md`.

No Python, test, fixture, dependency, configuration, package export, private
data, generated dataset, calendar, other documentation, strategy, model, or
integration path is authorized. The pre-existing untracked
`docs/smc_v2_diagnostic_context_integration_change_proposal.md` is outside this
task and must remain untouched.

## 5. Reserved Future Implementation Scope

If this record passes independent audit, human acceptance, post-push readiness,
and a later bounded implementation authorization, the first implementation
scope is reserved to exactly:

- `analysis/gc_dataset_builder.py`;
- `tests/test_gc_dataset_builder.py`;
- `docs/gc_futures_dataset_checkpoint.md`.

No external fixture is reserved. Tests use inline synthetic export bytes,
calendar entries, and configuration. Private source files may be used only in a
later separately authorized read-only dataset run after implementation passes.

Forbidden paths include:

- `orderflow/sierra_chart_importer.py` and `orderflow/footprint.py`;
- `core/gc_chronological_backtest.py` and every legacy backtest/paper runner;
- all SMC, CRT, Order Flow, strategy, feature, label, model, risk, broker,
  storage, report, main, configuration, requirements, and package-export files;
- the existing SMC V2 integration proposal;
- raw private files, failed evidence, and the preserved OOS snapshot.

## 6. Capability Boundary and Non-Goals

The future builder will:

- parse exact Sierra Chart bar-and-study export bytes supplied by the caller;
- validate exact schema, provenance, contract identity, prices, and volumes;
- normalize chart-local bar-start moments to UTC bar-close moments;
- bind every usable row to one canonical caller-supplied GC calendar session;
- compute completed-session volume without future-session evidence;
- select monotonic contract regimes without price adjustment;
- split output at contract rolls, missing-bar gaps, and partition boundaries;
- emit immutable canonical bars, contract segments, manifest evidence, and
  fail-closed diagnostics.

It will not:

- read directories, discover files, download data, or call an external API;
- infer holidays, early closes, or no-trade bars from timestamp absence;
- use mutable `orderflow.footprint.FootprintCandle` as canonical input;
- construct footprint, delta, bid/ask imbalance, DOM, or market-depth features;
- forward-fill, interpolate, deduplicate, resample, or price-adjust contracts;
- create one cross-contract `GCChronologicalBar` stream for one backtest run;
- generate candidates, features, labels, trades, PnL, thresholds, or models;
- inspect validation/OOS outcomes to choose roll, calendar, or cleaning rules;
- authorize training, paper, broker, or live behavior.

## 7. Exact Constants, Enums, and Contract Normalization

Future constants are locked to:

```python
GC_DATASET_BUILDER_VERSION = "GC-DATASET-BUILDER-V1"
GC_DATASET_INSTRUMENT = "GC"
GC_DATASET_TIMEFRAME = "5M"
GC_DATASET_SOURCE_TIMEZONE = "Asia/Tokyo"
GC_DATASET_EXCHANGE_TIMEZONE = "America/New_York"
GC_DATASET_TICK_SIZE = Decimal("0.1")
GC_ROLL_CONFIRMATION_SESSIONS = 3
GC_DELIVERY_MONTH_CODES = ("G", "J", "M", "Q", "V", "Z")
```

Exact enums are:

```python
class GCDatasetBuildStatus(str, Enum):
    VALID = "VALID"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"

class GCSourceRole(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    OOS_HOLDOUT = "OOS_HOLDOUT"

class GCSegmentPartition(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    OOS_HOLDOUT = "OOS_HOLDOUT"
```

Contract tokens normalize to exact `GC<delivery-code><two-digit-year>-COMEX`.
Delivery codes outside the locked six-code cycle, generic `GC`, `[M]` suffixes,
continuous aliases, spread/options tokens, XAUUSD, and other instruments are
invalid. Contract ordering is chronological by decoded delivery year then the
locked delivery-code order; lexical hash or filename order is never chronology.

## 8. Immutable Raw Export Provenance Contract

Every parsed source is a complete immutable value:

```python
@dataclass(frozen=True)
class GCSierraChartExport:
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCSourceRole
    capture_timestamp: datetime
    chart_timezone: str
    timeframe: str
    rows: tuple[GCSierraChartBarRow, ...]
```

Rules:

- `source_name` is a nonempty basename with no directory traversal and is
  lineage only, never a model feature;
- `source_sha256` is recomputed from the exact supplied bytes before decoding;
- bytes decode as strict UTF-8 with an optional leading UTF-8 BOM only;
- `capture_timestamp` is aware UTC and supplied from immutable intake evidence,
  never current wall clock;
- chart timezone is exact `Asia/Tokyo`; timeframe is exact `5M`;
- role is explicit and immutable; the same source hash cannot appear under two
  roles or contracts;
- a full development export and overlapping OOS snapshot may coexist as source
  evidence, but no row may enter both output partitions;
- source tuple order is canonical decoded contract order, then role value, then
  source hash; no silent sort is permitted.

The exact export command is Sierra Chart `Edit -> Export Bar and Study Data to
Text File`. Official Sierra Chart documentation states that this export uses the
chart timezone and that chart times are not UTC. Official session documentation
states that a chart bar Date-Time is its starting time. These facts are input
contract evidence, not implementation guesses.

Authoritative references:

- Sierra Chart Edit Menu, `Export Bar and Study Data to Text File`:
  <https://www.sierrachart.com/index.php?page=doc%2FEditMenu.html>;
- Sierra Chart Session Times, `Bar Starting Times`:
  <https://www.sierrachart.com/index.php?page=doc%2FSessionTimes.php>.

## 9. Exact Raw Row and Schema Contract

The future row model is:

```python
@dataclass(frozen=True)
class GCSierraChartBarRow:
    source_row_number: int
    bar_start_timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    number_of_trades: int
    bid_volume: int
    ask_volume: int
```

The input header is exactly, after surrounding-space normalization:

```text
Date, Time, Open, High, Low, Last, Volume, # of Trades,
OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume
```

Rules:

- blank, duplicate, missing, reordered, or extra columns are invalid;
- each nonblank line has exactly 13 comma-separated fields;
- source row number starts at `2` for the first data row and is strictly
  increasing;
- Date and Time combine into one naive chart-local start moment before exact
  `Asia/Tokyo` attachment; explicit offsets in raw fields are invalid;
- OHLC values use finite Decimal text and align exactly to tick size `0.1`;
- `low <= open, close <= high` and `low <= high`;
- volume, trade count, bid volume, and ask volume are nonnegative exact integers;
- `volume == bid_volume + ask_volume` exactly;
- the three exported average columns must be finite Decimal text but are not
  canonical fields, features, roll evidence, or identity inputs beyond the raw
  source SHA-256;
- booleans, floats, NaN, infinity, fractional integer fields, locale-formatted
  numbers, malformed dates, and exception leakage are invalid;
- rows are independently strictly increasing and unique by local timestamp;
- no silent sort, duplicate collapse, or fallback parser is permitted.

## 10. Bar Start, Close, Timezone, and Tick Semantics

The raw timestamp is the start of a fixed five-minute chart bar. Canonical
conversion is exactly:

1. parse the raw naive start in `Asia/Tokyo`;
2. attach IANA `Asia/Tokyo` under the runtime timezone database;
3. convert the aware start to UTC;
4. compute canonical close as `start_utc + timedelta(minutes=5)`;
5. require canonical close `<= capture_timestamp`;
6. convert prices to exact integer ticks by `price / Decimal("0.1")` and reject
   any nonintegral result.

The builder must also load IANA `America/New_York` from the same runtime timezone
database and require the supplied normalized timezone-data version to match the
runtime version exactly. Unavailable zones, unavailable runtime version, version
mismatch, ambiguous fallback, wall-clock use, or treating raw JST as UTC is
`INVALID`.

The final export row is not automatically incomplete. It is usable only when its
canonical close is no later than its immutable capture timestamp and all other
session/partition rules pass. A currently open bar is excluded with explicit
evidence and cannot become a completed row retroactively under the same source
identity.

## 11. Versioned Calendar and Canonical GC Session Contract

The only calendar input is a caller-supplied tuple of frozen
`smc.kill_zones.KillZoneCalendarEntry` values using exact
`smc.kill_zones.KillZoneSessionStatus`. No calendar is generated from bars.

Rules:

- entries are strictly increasing and unique by trade date;
- one nonempty `calendar_version` applies to the complete build;
- timestamps are aware UTC and reconcile through the configured runtime
  `America/New_York` rules;
- standard `OPEN` trade date `D` is local `D - 1 calendar day 18:00:00`
  inclusive through local `D 17:00:00` exclusive;
- `EARLY_CLOSE` uses the same open and one explicit close after open and no later
  than local `D 17:00:00`;
- local `17:00:00` through `18:00:00` is maintenance and never eligible;
- `SESSION_CLOSED` has no tradable interval;
- Monday-Friday is not sufficient evidence by itself; holidays and early closes
  require the versioned calendar;
- rows outside a canonical open interval never enter a segment;
- a positive-volume row inside a calendar-declared maintenance or closed period
  is contradictory and `INVALID`, not silently dropped;
- missing required calendar coverage is `UNKNOWN` only after all independently
  determinable supplied evidence is validated;
- malformed, conflicting, in-horizon mismatched, duplicate, or version-mismatched
  evidence is `INVALID`.

The current repository has no accepted historical GC calendar artifact.
Implementation may proceed with synthetic inline calendars; a private real-data
build must stop until an authoritative versioned caller-supplied calendar is
separately acquired and audited.

## 12. Contract Coverage and Completed-Session Volume Eligibility

Roll evidence uses completed canonical session volume, not row count, price,
filename, expiration intuition, or future volume.

For contract `C` and trade date `D`:

- every included row must map to `D` under Section 11;
- session volume is the exact integer sum of row volume in the eligible interval;
- the source must have immutable capture coverage beyond the session close;
- a partial first/last source session is ineligible roll evidence;
- duplicate source coverage for the same contract/moment must reconcile
  byte-for-byte after canonical parsing or is `INVALID`;
- a missing five-minute timestamp is reported as a gap and never synthesized;
- absence alone cannot prove zero volume or a complete session;
- the current contract and every later contract considered for one roll decision
  require comparable completed-session evidence for each confirmation date;
- missing an intermediate canonical delivery contract required by the selected
  initial boundary is `UNKNOWN`; the builder may not infer its volume.

The present raw intake does not prove a canonical start in February 2025 because
`GCJ25-COMEX` and `GCM25-COMEX` are not supplied. Those earlier dates cannot be
rescued by declaring `GCQ25-COMEX` dominant among an incomplete contract set.
The future configuration must choose an initial contract and initial trade date
only where required adjacent coverage is independently proved.

## 13. Locked Prior-Session Three-Confirmation Roll Policy

The exact V1 roll policy is `PRIOR_SESSION_VOLUME_DOMINANCE_3`:

1. the configuration supplies one canonical `initial_contract` and
   `initial_trade_date`; no automatic seed is allowed;
2. the active contract for `initial_trade_date` is the supplied initial contract;
3. after each completed eligible trade date, compare exact completed-session
   volume of the current contract with later canonical contracts having complete
   comparable evidence;
4. a later contract becomes a roll candidate only after its volume is strictly
   greater than the current contract on three consecutive eligible completed
   trade dates;
5. the three dates must be consecutive in the supplied calendar's eligible
   trade-date sequence; closed dates neither count nor break the sequence;
6. if multiple later contracts qualify on the same third date, choose the one
   with greatest volume on that third date, then the nearer decoded delivery
   month; distinct canonical contracts are therefore fully ordered;
7. the roll becomes effective only at the next eligible canonical session open;
8. the immutable caller-supplied calendar known before the decision moment may
   identify that next eligible session and its scheduled open; no bar, volume,
   price, calendar revision, or calendar fact first learned at or after the
   effective session may select the contract or alter the already scheduled
   roll;
9. contract order is monotonic; reverse rolls are forbidden;
10. skipped delivery months remain recorded in manifest evidence and are never
    silently deleted merely because they were not selected;
11. there is no price back-adjustment, ratio adjustment, synthetic spread, or
    cross-contract OHLC splice;
12. a candidate, label horizon, feature window, or backtest position may not
    cross a roll boundary.

The earlier same-day volume-dominance inspection is diagnostic only and is not
accepted as the V1 roll plan. Real-data output remains blocked until the
initial boundary and required coverage pass this prospective rule.

## 14. Immutable Canonical Bars and Contract Segments

The builder reuses frozen `core.gc_chronological_backtest.GCChronologicalBar`
as the canonical price bar and emits it only inside an exact-contract segment:

```python
@dataclass(frozen=True)
class GCCanonicalContractSegment:
    segment_id: str
    contract: str
    partition: GCSegmentPartition
    first_trade_date: date
    last_trade_date: date
    source_ids: tuple[str, ...]
    bars: tuple[GCChronologicalBar, ...]
    preceding_missing_bar_count: int
```

Rules:

- each bar index is reassigned deterministically from zero within the segment;
- timestamp is the aware UTC close moment from Section 10;
- OHLC ticks and volume reconcile exactly to one source row;
- bars are independently strictly increasing by index and timestamp;
- adjacent bars inside one contiguous run are exactly five minutes apart;
- a calendar boundary, contract roll, partition boundary, or missing timestamp
  ends the current segment; it never creates a synthetic bar;
- `preceding_missing_bar_count` is zero for the first segment and otherwise
  records the exact number of expected eligible five-minute slots between the
  prior segment's final close and this segment's first start when a missing-data
  gap caused the boundary; calendar, roll, and partition boundaries use zero;
- no missing slot lies inside a segment and no missing count is interpreted as a
  zero-volume row;
- source IDs are ordered unique complete lineage;
- one segment contains exactly one contract and one partition;
- segment tuples are ordered by first bar close, decoded contract order, then
  segment ID only as a final identity-stability tie-break;
- the strict chronological backtest must be invoked separately per segment; no
  dataset builder output pretends that separate contracts are one run.

## 15. Development/OOS Isolation and Partition Boundary

Source role and output partition are immutable. The current
`GCQ26_COMEX_5m_30d_export_20260803.txt` source is reserved as
`OOS_HOLDOUT`. The overlapping full `GCQ26` source may provide raw hash
reconciliation, but rows whose canonical trade dates fall in the locked OOS
interval cannot enter development output.

`OOS_HOLDOUT` is a quarantine role, not a claim that final OOS acceptance has
already passed. The file and charts have been opened for transport and basic
data-quality review, although no frozen strategy/model outcome evaluation has
been authorized. A later numerical experiment decision must record that access
boundary and may reject this interval as final OOS, in which case only strictly
future data can replace it. It may never be recycled into development merely
because final-OOS acceptance fails.

The future configuration must explicitly supply `oos_start_trade_date` and
`oos_end_trade_date`. For the current intake, a later numerical experiment
decision may accept `2026-07-06` as the proposed start only after calendar
normalization proves that boundary. No date is inferred from a filename.

Rules:

- development and OOS trade-date intervals are disjoint and chronological;
- one canonical moment may appear in at most one partition;
- duplicated 30-day/full-file rows must match exactly and are emitted only from
  the source role assigned to their partition;
- incomplete `2026-08-03` source evidence cannot enter a completed-session OOS
  result merely because it exists in the full file;
- partition boundaries are complete session and complete effective-group
  boundaries;
- feature/label windows crossing development, calibration, OOS, roll, missing
  bar, or source-repair boundaries are later purged, never truncated;
- the builder reports partition evidence but does not open, score, or evaluate
  the OOS partition;
- any outcome-guided boundary change creates a new hypothesis and invalidates
  affected OOS claims.

## 16. Manifest, Conservation, and Data-Quality Evidence

The future manifest model is:

```python
@dataclass(frozen=True)
class GCDatasetManifest:
    dataset_id: str
    version: str
    source_ids: tuple[str, ...]
    segment_ids: tuple[str, ...]
    calendar_version: str
    timezone_data_version: str
    raw_start_timestamp: datetime
    raw_end_timestamp: datetime
    usable_start_timestamp: datetime | None
    usable_end_timestamp: datetime | None
    parsed_row_count: int
    eligible_row_count: int
    development_bar_count: int
    oos_bar_count: int
    excluded_row_count: int
    missing_bar_count: int
    raw_volume: int
    eligible_volume: int
    excluded_volume: int
    completed_session_volumes: tuple[tuple[str, date, int], ...]
    exclusion_counts: tuple[tuple[str, int], ...]
    roll_trade_dates: tuple[date, ...]
```

The manifest and result must reconcile:

- exact source SHA-256 and ordered SOURCE IDs;
- exact raw and usable ranges;
- row counts by parsed, eligible, excluded, development, and OOS state, with
  `parsed_row_count == eligible_row_count + excluded_row_count` and
  `eligible_row_count == development_bar_count + oos_bar_count`;
- exact aggregate volume before and after eligible-session filtering, with
  `raw_volume == eligible_volume + excluded_volume`;
- `completed_session_volumes` ordered uniquely by decoded contract then trade
  date, binding every nonnegative exact completed-session volume used by a roll
  comparison;
- `exclusion_counts` ordered uniquely by exact uppercase reason token, using
  positive integer counts whose sum equals `excluded_row_count`;
- duplicate, ordering, OHLC, tick, volume, calendar, session, gap, incomplete-bar,
  overlap, partition, and roll evidence;
- ordered segment IDs, source IDs, and roll dates;
- no unexplained row loss and no double counting.

A promoted `VALID` or `NONE` manifest contains only reconciled evidence and has
no invalid-row bucket. Any malformed or contradictory row makes the result
`INVALID`; the failing group and later evidence are not promoted, and no partial
manifest is relabeled as successful evidence. Deterministic blocking reasons
identify that failure outside the unpromoted manifest.

Private raw data and generated bar tables remain ignored and uncommitted. A
sanitized checkpoint may record hashes, counts, reasons, and commands only after
separate review confirms that no proprietary row data is exported.

## 17. Exact Frozen Configuration and Result Models

The future configuration and result are exactly:

```python
@dataclass(frozen=True)
class GCDatasetBuildConfig:
    instrument: str
    timeframe: str
    source_timezone: str
    exchange_timezone: str
    timezone_data_version: str
    tick_size: Decimal
    initial_contract: str
    initial_trade_date: date
    roll_confirmation_sessions: int
    oos_start_trade_date: date
    oos_end_trade_date: date

@dataclass(frozen=True)
class GCDatasetBuildResult:
    status: GCDatasetBuildStatus
    dataset_id: str | None
    segments: tuple[GCCanonicalContractSegment, ...] = ()
    manifest: GCDatasetManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

Configuration normalization must equal the constants in Section 7.
`roll_confirmation_sessions` must equal exact `3`. Initial and OOS dates are
explicit, ordered, and contain no hidden default. OOS starts strictly after the
initial trade date. Decimal values are finite and context-independent. All
dataclasses are frozen; mutable collections, dataframes, paths, callbacks,
models, strategies, and execution fields are forbidden.

## 18. Exact Keyword-Only Public API

The future public API is exactly:

```python
def parse_sierra_chart_gc_export(
    *,
    source_name: str,
    contract: str,
    role: GCSourceRole,
    capture_timestamp: datetime,
    chart_timezone: str,
    timeframe: str,
    raw_bytes: bytes,
) -> GCSierraChartExport:
    ...

def make_gc_dataset_id(
    *,
    identity_kind: str,
    config: GCDatasetBuildConfig | None = None,
    source_name: str | None = None,
    source_sha256: str | None = None,
    contract: str | None = None,
    role: GCSourceRole | None = None,
    capture_timestamp: datetime | None = None,
    source_timezone: str | None = None,
    timeframe: str | None = None,
    first_trade_date: date | None = None,
    last_trade_date: date | None = None,
    source_ids: tuple[str, ...] = (),
    bar_digest: str | None = None,
    preceding_missing_bar_count: int | None = None,
    partition: GCSegmentPartition | None = None,
    segment_ids: tuple[str, ...] = (),
    calendar_digest: str | None = None,
    evidence_digest: str | None = None,
    roll_trade_dates: tuple[date, ...] = (),
) -> str:
    ...

def build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult:
    ...
```

All parameters are keyword-only. No permissive `**kwargs`, positional alias,
mutable default, filesystem path, dataframe, iterator, external API, importer,
strategy, model, or callback parameter is permitted. Parsing raises only
TypeError or ValueError for malformed supplied bytes. Dataset analysis contains
malformed evidence in the fail-closed result contract.

The only allowed direct repository imports are:

- `core.gc_chronological_backtest.GCChronologicalBar`;
- `smc.kill_zones.KillZoneCalendarEntry`;
- `smc.kill_zones.KillZoneSessionStatus`.

Standard-library parsing, datetime, Decimal, enum, hashing, canonical JSON,
regular-expression, and `zoneinfo` imports are allowed. Third-party data,
calendar, dataframe, ML, and optimization imports are forbidden.

The module's exact public export surface is:

```python
__all__ = [
    "GC_DATASET_BUILDER_VERSION",
    "GC_DATASET_INSTRUMENT",
    "GC_DATASET_TIMEFRAME",
    "GC_DATASET_SOURCE_TIMEZONE",
    "GC_DATASET_EXCHANGE_TIMEZONE",
    "GC_DATASET_TICK_SIZE",
    "GC_ROLL_CONFIRMATION_SESSIONS",
    "GC_DELIVERY_MONTH_CODES",
    "GCDatasetBuildStatus",
    "GCSourceRole",
    "GCSegmentPartition",
    "GCSierraChartBarRow",
    "GCSierraChartExport",
    "GCCanonicalContractSegment",
    "GCDatasetManifest",
    "GCDatasetBuildConfig",
    "GCDatasetBuildResult",
    "parse_sierra_chart_gc_export",
    "make_gc_dataset_id",
    "build_gc_futures_dataset",
]
```

No package initializer is changed and imported dependency classes are not
re-exported.

## 19. Deterministic SOURCE, SEGMENT, and DATASET Identities

Identity kinds are exactly `SOURCE`, `SEGMENT`, and `DATASET`. Every identity
uses canonical JSON, sorted keys, compact separators, exact enum values,
uppercase normalized contracts, UTC microsecond timestamps as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`, canonical Decimal text, and lowercase SHA-256.

`identity_kind` is common and required. Remaining fields are exact
required/forbidden:

- `SOURCE` requires `source_name`, `source_sha256`, `contract`, `role`, and
  `capture_timestamp`, `source_timezone`, and `timeframe`; `config` and every
  segment/data-set-only parameter are forbidden. This keeps immutable raw source
  identity stable across later roll, initial-boundary, and OOS configurations.
- `SEGMENT` requires `config`, `contract`, `partition`, `first_trade_date`,
  `last_trade_date`, nonempty ordered unique `source_ids`, `bar_digest`, and
  nonnegative `preceding_missing_bar_count` reconciled exactly to Section 14;
  source name/hash/role/capture/timezone and DATASET-only fields are forbidden.
- `DATASET` requires `config`, ordered unique `source_ids`, ordered unique
  `segment_ids`, `calendar_digest`, `evidence_digest`, and ordered unique
  `roll_trade_dates`;
  source-local and segment-local fields are forbidden.

`bar_digest` binds every complete normalized `GCChronologicalBar` field in
caller order. `calendar_digest` binds the complete normalized versioned calendar
tuple. `evidence_digest` binds every manifest field except `dataset_id`, including
version, timestamp ranges, all row/gap counts, all aggregate volumes, ordered
completed-session volumes, ordered exclusion counts, ordered source/segment IDs,
calendar/timezone versions, and roll dates. SEGMENT and DATASET bind every
configuration field, including initial boundary, roll confirmation count, and
OOS interval. SOURCE identity binds its own exact timezone/timeframe provenance,
is recomputed by the parser, and must match the immutable export value. SEGMENT
and DATASET identities are recomputed by the analyzer. Changing gap provenance
or manifest conservation evidence therefore cannot preserve the prior identity.

Unknown kinds, missing required fields, supplied forbidden fields, malformed
hashes, duplicate histories, impossible date ranges, config mismatch, invalid
contract order, malformed nested values, Decimal errors, or timezone errors
raise only TypeError or ValueError from the public identity builder.

## 20. Atomic Processing, Status Precedence, and Prefix Invariance

Processing is atomic by complete canonical trade-date group. Each group is
validated against immutable pre-group state before volume, roll, segment, or
manifest evidence is promoted. A failing group and every later group promote no
bars, segment revisions, roll decision, or manifest count. Strictly prior
complete segments and evidence remain byte-for-byte unchanged. An unknowable
malformed effective moment permits no trustworthy chronological cutoff.

Final precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

- `INVALID`: malformed, contradictory, duplicated, or identity-inconsistent
  supplied evidence;
- `AMBIGUOUS`: retained in the shared fail-closed status vocabulary, but V1 has
  no reachable valid branch because distinct roll candidates are fully ordered;
  duplicate/forked/contradictory same-contract evidence is `INVALID`, and no
  artificial ambiguity branch may be added;
- `UNKNOWN`: required calendar, source coverage, initial boundary, completed
  session, or comparable roll evidence is unavailable;
- `VALID`: all emitted segments and manifest evidence are canonical;
- `NONE`: valid empty exports and calendar scope produce no segment.

Prefix invariance applies only to a valid prefix ending on a complete canonical
session with no pending three-session roll sequence, no partial source session,
no partial same-date group, and no partition boundary under construction.
Appending strictly later complete source sessions and calendar entries may add
later evidence but cannot alter prior bars, segments, identities, rolls, counts,
or reasons.

Same-effective append, historical insertion, source replacement, calendar
repair, timezone-version mutation, role mutation, initial-boundary change, OOS
boundary change, or added missing intermediate contract is not prefix extension
and requires a new DATASET identity and a new audit. No silent sorting is used.

## 21. Inline Synthetic Exact 48-Case Unit-Test Matrix

Future implementation must preserve exactly these numbered logical cases;
parameterization may increase collected executions without changing the count:

1. Missing exports/calendar and malformed supplied counterpart obey available-
   evidence precedence.
2. Valid empty exports/calendar returns `NONE` with no segment or manifest row.
3. Exact GC contract token and six delivery codes; generic/continuous/other
   instrument rejection.
4. Exact source and exchange timezone, runtime tzdata version, and unavailable
   zone/version fail-closed behavior.
5. Exact `5M`, `0.1` tick, instrument, and roll-confirmation constants.
6. Strict UTF-8/BOM decoding and exact 13-column header/order.
7. Blank, short, long, reordered, duplicate, and extra column rejection.
8. Raw date/time parsing as naive chart-local start, not UTC or close.
9. Asia/Tokyo start -> UTC close conversion and five-minute addition.
10. Capture-boundary completed versus still-open final bar.
11. Decimal OHLC integer-tick conversion and exact geometry.
12. Boolean, float, NaN, infinity, fractional tick, locale, and malformed price
    rejection without Decimal exception leakage.
13. Integer volume/trades/bid/ask validation and exact volume conservation.
14. Finite ignored average columns cannot affect canonical bars except through
    raw SOURCE hash.
15. Strictly increasing unique row number and local timestamp; no silent sort.
16. Source SHA-256 recomputation and raw-byte sensitivity.
17. Source name basename/path-traversal, role, capture, contract, and tuple-order
    validation.
18. Duplicate source hash under conflicting contract/role is `INVALID`.
19. Standard DST and standard-time conversions through both IANA zones.
20. Calendar standard OPEN session and exact inclusive-open/exclusive-close.
21. EARLY_CLOSE exact boundary and no later eligible row.
22. SESSION_CLOSED and maintenance positive-volume contradiction.
23. Missing calendar `UNKNOWN` versus malformed/version mismatch `INVALID`.
24. Bar-to-trade-date assignment around midnight, weekend, DST, and maintenance.
25. Completed-session volume exact sum and partial first/last session exclusion.
26. Duplicate overlapping source rows exact reconciliation versus conflict.
27. Missing five-minute timestamp is counted, never synthesized or forward-filled.
28. Missing adjacent delivery coverage blocks initial-boundary acceptance.
29. Explicit initial contract/date required; no automatic dominant seed.
30. One/two qualifying prior sessions do not roll.
31. Exact third consecutive prior-session dominance schedules next-session roll.
32. Closed calendar dates neither count nor break roll confirmation.
33. Confirmation broken by non-dominance resets the candidate sequence.
34. Multiple later candidates use third-day volume then nearer-delivery tie-break;
    hash order is irrelevant and duplicate/forked evidence is `INVALID`, not
    `AMBIGUOUS`.
35. An immutable pre-decision calendar schedules the next eligible effective
    session, while effective/later market evidence and later calendar revisions
    cannot select or alter the roll; the roll never reverses.
36. Skipped nonselected contract retained in manifest lineage.
37. No price/ratio adjustment and no cross-contract OHLC splice.
38. Segment ends on roll, missing bar, partition, and calendar boundaries.
39. Canonical bar index/UTC close/OHLC/volume reconciliation and exact one-
    contract segment rule.
40. Development/OOS overlap is emitted once under immutable role; mismatch is
    `INVALID`.
41. Proposed OOS date requires calendar proof; incomplete capture is excluded.
42. Manifest typed parsed/eligible/development/OOS/excluded counts, raw/eligible/
    excluded volume, completed-session volume, exclusion-reason, gap, roll, and
    segment conservation; `evidence_digest` sensitivity; no silent loss or
    double count; invalid evidence promotes no partial manifest.
43. Exhaustive SOURCE identity required/forbidden fields and sensitivities.
44. Exhaustive SEGMENT identity required/forbidden fields, bar digest, exact
    `preceding_missing_bar_count`, lineage, partition, contract, moment, and
    order sensitivities.
45. Exhaustive DATASET identity required/forbidden fields, calendar/config/roll/
    source/segment/OOS and complete manifest `evidence_digest` sensitivities.
46. Exact keyword-only signatures/defaults, frozen dataclasses, annotations,
    enums, constants, and exports.
47. Later determinably malformed group preserves strictly prior immutable
    evidence; complete-prefix invariance and historical-repair ineligibility.
48. Exact three-path scope, direct dependency/import allowlist, deterministic
    repeatability, no filesystem/network/wall-clock use, rollback, and global
    freeze preservation.

## 22. Verification and Promotion Gates

Before future implementation promotion:

1. tests are written before production behavior;
2. all 48 logical cases reconcile exactly;
3. focused tests pass with `-p no:cacheprovider`;
4. the full regression suite passes with `-p no:cacheprovider`;
5. source, tests, and checkpoint receive SHA-256, byte, line, and formatting
   evidence;
6. an independent code/test/scope/hash/diff audit passes;
7. exact-path staging and full cached-content audit pass;
8. local commit and push require separate explicit authorization;
9. no raw private row, proprietary dataset, or OOS outcome is committed;
10. a real-data build requires a separately accepted calendar artifact,
    initial-boundary evidence, and private execution authorization;
11. feature/label generation, model training, backtest orchestration, and
    integration remain separately frozen.

Passing implementation tests proves only the deterministic parser/builder
contract. It does not accept the private data, prove session completeness,
establish an experiment manifest, create an AI, or prove profitability.

## 23. Rollback and Mandatory Stop Conditions

Rollback means discarding only the unaccepted bounded implementation and
returning to its exact parent. Raw intake, historical failures, committed
decisions, and independent evidence are never rewritten.

Work must stop if:

- an authoritative versioned GC holiday/early-close calendar is unavailable;
- source chart timezone, bar-start semantics, capture time, timeframe, tick size,
  or exact contract identity is unproved;
- the initial contract/date or required adjacent contract coverage is absent;
- roll selection would require same-session/future evidence, price outcomes,
  filename order, or silent contract skipping;
- an absent timestamp would need to be fabricated as a zero-volume bar;
- a feature, label, candidate, trade, PnL, or model is needed to build bars;
- development and OOS overlap cannot be isolated exactly;
- a roll, missing-data, partition, or label horizon must cross a forbidden
  boundary;
- implementation requires modifying the footprint importer, strict backtest,
  SMC modules, dependencies, configuration, runtime, or another forbidden path;
- public API, identities, matrix count, or three-path scope must broaden;
- any focused/full test, hash, formatting, audit, staging, freeze, provenance,
  or reproducibility gate fails.

## 24. Final Decision and Resume Checkpoint

The decision is:

`READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`

Locked state:

- the eight-file intake is transport-integrity evidence, not an accepted
  training dataset;
- Sierra timestamps are chart-local bar starts and require exact UTC close-time
  normalization;
- calendar/session truth is caller-supplied, versioned, and non-inferential;
- V1 uses prospective prior-session three-confirmation volume rolls;
- output is separate, unadjusted, contiguous exact-contract segments;
- development/OOS overlap is isolated without opening OOS outcomes;
- the current OOS-named snapshot is quarantined candidate evidence, not yet an
  accepted untouched final-OOS claim;
- missing calendar and incomplete adjacent contract coverage currently block a
  real-data build;
- future implementation is limited to the exact reserved three paths;
- feature/label extraction, AI training, integration, paper, broker, and live
  work remain unauthorized.

The next permitted action is an independent read-only audit of this exact
document. No stage, commit, push, Python, tests, fixtures, calendar acquisition,
private-data build, feature/label work, model training, integration, paper, or
live action is implied.

Global code freeze remains active.
