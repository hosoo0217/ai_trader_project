# GC Futures Real-Data Compatibility Change Proposal

## 1. Proposal Record

- Proposal ID: GC-FUTURES-REAL-DATA-COMPATIBILITY-2026-08-03.
- Proposal version: 1.
- Baseline branch: main.
- Baseline Git commit:
  f1ec91cb4153a84101a3db876e1a376636dbfec3.
- Baseline builder version: GC-DATASET-BUILDER-V1.
- Change class: documentation-only semantic correction proposal.
- Global code freeze outside this exact documentation path: ACTIVE.
- Real private-data build: NOT AUTHORIZED.
- Feature, label, model, strategy, backtest, OOS scoring, paper, broker, and live
  progression: NOT AUTHORIZED.

This proposal does not revise or erase the committed V1 decision, source,
tests, checkpoint, failed-build evidence, or raw intake. It records the exact
compatibility correction required before the current private Sierra Chart
exports can be considered for a canonical GC dataset.

## 2. Decision Summary

The current V1 implementation is correct against its synthetic locked contract,
but that contract is not compatible with the observed real-data shape.

V1 requires every expected five-minute timestamp to exist before a session may
contribute comparable completed-session volume. The real GC exports contain
many legitimate sparse intervals with no exported bar. Enabling Sierra Chart's
Include Columns With No Data option is not an acceptable repair because Sierra
Chart documents that it inserts bars and sets OHLC to the prior close. The text
export does not carry a canonical provenance field that would let the builder
distinguish such inserted rows from observed trade bars.

The selected correction is:

1. never fabricate, forward-fill, or promote an absent interval as a price bar;
2. separate source-coverage completeness from observed-bar continuity;
3. require immutable hash-bound acquisition coverage evidence before an absent
   interval can be interpreted as no recorded trade for session-volume
   aggregation;
4. keep every absent interval as an observed-stream discontinuity, so no
   feature, label, candidate, or backtest window may cross it;
5. compare the active contract only with its exact next canonical delivery
   contract for roll confirmation;
6. keep the real build stopped until both authoritative calendar evidence and
   sufficient adjacent-contract boundary evidence are available.

The future corrected builder version is:

    GC-DATASET-BUILDER-V2

V1 remains historical evidence and must not silently change meaning.

## 3. Exact Documentation-Only Scope

This turn may create only:

- docs/gc_futures_real_data_compatibility_change_proposal.md

It must not edit, stage, commit, or push any file. In particular it must not
touch:

- the eight private raw exports;
- analysis/gc_dataset_builder.py;
- tests/test_gc_dataset_builder.py;
- docs/gc_futures_dataset_checkpoint.md;
- docs/gc_futures_dataset_build_freeze_lift_decision.md;
- the pre-existing untracked
  docs/smc_v2_diagnostic_context_integration_change_proposal.md;
- any calendar, feature, label, model, strategy, backtest, risk, execution,
  configuration, requirements, importer, footprint, runtime, or integration
  path.

## 4. Preserved Baseline and Evidence

The following facts remain authoritative baseline evidence:

- V1 source, tests, and checkpoint are committed and pushed;
- V1 has 48 exact logical cases and 143 focused collected tests;
- its checkpoint records 2004 full-regression tests passing;
- the private real-data build was not performed by that checkpoint;
- the current OOS-named GCQ26 snapshot is quarantine evidence, not an accepted
  untouched final OOS result;
- GCJ25-COMEX and GCM25-COMEX are not present in the current intake;
- no accepted historical GC holiday and early-close calendar artifact is
  currently in the repository;
- no model training, feature extraction, label construction, strategy
  selection, or runtime integration has been authorized.

No later correction may rewrite these statements as though V1 had already
accepted the real dataset.

## 5. Read-Only Real-Data Finding

A read-only audit of the eight files under the ignored Sierra Chart data
directory found:

- 178813 total data rows;
- exact expected 13-column headers;
- zero malformed-width or nonnumeric rows;
- zero OHLC geometry violations;
- zero negative volumes;
- zero bid-volume plus ask-volume conservation failures;
- zero duplicate or non-increasing timestamps inside a file;
- zero exported zero-volume rows.

The observed source SHA-256 values are:

| Source | SHA-256 |
|---|---|
| GCG26_COMEX_5m_186d_export_20260803.txt | FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719 |
| GCJ26_COMEX_5m_186d_export_20260803.txt | B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85 |
| GCM26_COMEX_5m_186d_export_20260803.txt | A9FA27C5E4C29520409826D23696AE7231F3CB7AE52202F6DDD74F1B94BB6C83 |
| GCQ25_COMEX_5m_186d_export_20260803.txt | 1FECFD8C97C6346EEB62BBC302E677FA52C2A3D8F3D40AA5C578E87F1F3B6F23 |
| GCQ26_COMEX_5m_186d_export_20260803.txt | 3B66A676B93F459FF62EE01735956F4281619858646946595326B1B8517EC4DA |
| GCQ26_COMEX_5m_30d_export_20260803.txt | 15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111 |
| GCV25_COMEX_5m_186d_export_20260803.txt | B1C3F8691D9256AB02112ACF7FF61D1CD5AD60DEAC60B685F795C0F072DE70D5 |
| GCZ25_COMEX_5m_186d_export_20260803.txt | 7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6 |

A diagnostic standard-session grid check, explicitly not a holiday-qualified
acceptance test, found exact full five-minute grids for only:

- GCG26: 43 of 129 inspected weekday sessions;
- GCJ26: 47 of 129;
- GCM26: 46 of 74;
- GCQ25: 46 of 129;
- GCQ26: 45 of 131;
- GCV25: 0 of 131;
- GCZ25: 88 of 130.

This does not prove corruption. It proves that row-grid completeness cannot be
used as the same fact as source-download completeness.

## 6. Official Source Boundary

The correction relies on these external source boundaries:

- Sierra Chart Chart Settings documents that Include Columns With No Data
  inserts bars at intervals with no data and sets their OHLC values to the
  prior close:
  https://www.sierrachart.com/index.php?page=doc%2FChartSettings.html
- Sierra Chart Chart Data documentation likewise describes inserted no-data
  bars:
  https://www.sierrachart.com/index.php?page=doc%2FChartDataFiles.html
- CME's GC fact card records Sunday-Friday 17:00-16:00 Central Time trading
  with a daily 60-minute break and a 0.10 minimum price fluctuation:
  https://www.cmegroup.com/market-regulation/files/gold-futures-and-options-fact-card.pdf
- CME publishes current trading-hour and holiday resources and warns that
  holiday schedules can change:
  https://www.cmegroup.com/trading-hours.html
- CME states that trading hours and holiday schedules are available through
  versioned reference-data services:
  https://www.cmegroup.com/notices/electronic-trading/2024/09/20240923.html

These references define acquisition and calendar authority only. They do not
authorize downloading, committing, exporting, or redistributing proprietary
market data.

## 7. Non-Negotiable No-Synthetic-Bar Rule

An absent five-minute interval is never converted into a canonical
GCChronologicalBar.

The corrected builder must reject:

- prior-close OHLC rows inserted only to fill an empty chart column;
- forward-filled, interpolated, resampled, or manually constructed rows;
- caller assertions that an absent row had an inferred open, high, low, close,
  trade count, bid volume, or ask volume;
- any row with zero trades and zero volume presented as an observed trade bar;
- any identity or manifest that hides synthetic construction inside a digest.

Observed bars remain exact immutable trade-derived rows. An absent interval may
contribute zero only to a session-volume sum after Section 9 coverage evidence
proves that the source completed the requested interval. It still emits no bar.

## 8. V2 Constants, Existing Types, and Compatibility

All current constants and enums remain unchanged except:

    GC_DATASET_BUILDER_VERSION = "GC-DATASET-BUILDER-V2"

These V1 public models retain their exact fields and frozen behavior:

- GCSierraChartBarRow;
- GCSierraChartExport;
- GCCanonicalContractSegment;
- GCDatasetBuildConfig;
- GCDatasetBuildResult.

GCDatasetManifest is extended only as specified in Section 16. Existing SOURCE,
SEGMENT, and DATASET identities are version-separated by the V2 constant and
therefore cannot collide with V1 identities.

No package initializer or existing consumer changes in the first future
implementation. V1 callers cannot be silently routed into V2 real-data
semantics.

## 9. Immutable Coverage Evidence Contract

V2 adds exactly one frozen public input model:

    @dataclass(frozen=True)
    class GCSierraChartCoverageEvidence:
        coverage_id: str
        source_id: str
        source_name: str
        source_sha256: str
        contract: str
        role: GCSourceRole
        capture_timestamp: datetime
        chart_timezone: str
        timeframe: str
        coverage_start_timestamp: datetime
        coverage_end_timestamp: datetime
        acquisition_completed_timestamp: datetime
        acquisition_evidence_sha256: str

Exact rules:

- every timestamp is timezone-aware and normalized to UTC;
- coverage is start-inclusive and end-exclusive;
- coverage start is strictly earlier than coverage end;
- acquisition completion is no earlier than coverage end and no later than
  source capture;
- source fields recompute the exact SOURCE identity and must match source_id;
- source SHA-256, name, contract, role, capture, timezone, and timeframe match
  the referenced GCSierraChartExport exactly;
- acquisition_evidence_sha256 binds immutable bytes from an independently
  reviewed Sierra Chart historical-download completion record;
- a screenshot, filename, row range, caller boolean, elapsed time, or chart
  appearance alone is insufficient coverage proof;
- coverage tuples are exact unique, ordered by normalized start, normalized
  end, decoded contract, role value, then coverage_id;
- overlapping evidence for one source must agree exactly or is INVALID;
- an export row outside its accepted coverage interval is INVALID;
- coverage evidence cannot enlarge the source capture boundary;
- a missing, malformed, mismatched, unverifiable, or unavailable acquisition
  record produces UNKNOWN or INVALID under Section 20, never inferred
  completeness.

The current screenshots show successful download messages, but no accepted
immutable acquisition evidence artifact has yet been audited. Therefore this
proposal does not claim that the current eight exports already satisfy this
contract.

## 10. Sparse Interval, Gap, and Session-Volume Semantics

V2 separates three facts:

1. observed bar: a canonical non-synthetic source row;
2. attested no-recorded-trade interval: no row exists, but accepted coverage
   spans the complete interval;
3. unattested interval: neither a row nor accepted coverage proves the interval.

For a completed session:

- exact session volume is the sum of observed positive integer row volumes;
- an attested no-recorded-trade interval adds zero to that sum but emits no bar;
- an unattested interval makes that contract/session volume UNKNOWN;
- contradictory duplicate rows or synthetic filler make the evidence INVALID;
- coverage must extend through the exclusive canonical session close and the
  immutable capture must be after that close;
- a partial first or last source interval remains ineligible.

Every absent observed-bar slot, including an attested no-trade interval, ends a
canonical segment. The next observed bar starts a new segment with exact
preceding_missing_bar_count. No feature, label, candidate, backtest state, or
model sequence may cross that boundary.

## 11. Versioned Calendar Contract

The only calendar input remains caller-supplied frozen
KillZoneCalendarEntry evidence. V2 does not generate a calendar from bars,
weekdays, filenames, exchange intuition, or current wall clock.

Before a private real-data build:

- the evidence must be GC/CME-specific, authoritative, versioned, and
  independently audited;
- its source URI or provider identifier, retrieval moment, immutable content
  SHA-256, normalized calendar version, and runtime timezone-data version must
  be recorded outside the pure builder;
- America/New_York conversion must use the exact runtime IANA database;
- standard, early-close, holiday, session-closed, and maintenance boundaries
  must reconcile exactly;
- calendar coverage must include every requested development, quarantine, and
  roll-confirmation trade date;
- a later calendar repair is a new dataset hypothesis and identity, not a
  prefix append.

No calendar artifact is created by this documentation task.

## 12. Initial Contract Boundary

V2 retains explicit initial_contract and initial_trade_date configuration, but
the pair is no longer trusted merely because the named contract has rows.

To accept initial contract C on initial trade date D:

- the exact previous canonical delivery contract P must be identified by the
  six-code delivery cycle;
- P and C need accepted completed-session coverage for the three immediately
  preceding eligible calendar sessions;
- C volume must be strictly greater than P volume on all three sessions;
- D must be the next eligible session after the third confirmation;
- no farther contract, same-session evidence, price outcome, filename, or
  expiration intuition may establish the seed;
- any missing predecessor, confirmation session, calendar boundary, or
  acquisition coverage is UNKNOWN;
- contradictory evidence is INVALID.

GCQ25 cannot be accepted as the current intake's first active contract because
the required prior adjacent GCJ25/GCM25 boundary evidence is absent. A later
starting point, including GCV25, is only a candidate until the exact predecessor
and three-session proof pass. The builder must not choose a convenient later
start automatically.

## 13. Exact Adjacent-Only Roll Policy

V2 keeps prospective prior-session three-confirmation volume dominance but
corrects the comparison set.

For active contract C:

1. derive exactly next_contract(C) from the six-code delivery cycle;
2. compare only C and next_contract(C);
3. require accepted completed-session volume for both on the same eligible
   trade date;
4. the next contract must be strictly greater for three consecutive eligible
   completed sessions;
5. a closed calendar date neither counts nor breaks the sequence;
6. non-dominance resets the sequence;
7. missing active or adjacent evidence is UNKNOWN;
8. farther-contract absence, sparsity, or larger volume is irrelevant until
   that contract becomes the exact adjacent successor;
9. roll effective time is the next eligible canonical session open known from
   the already accepted calendar;
10. roll order is monotonic and cannot reverse;
11. one effective session cannot skip multiple delivery contracts;
12. no same-session, future-session, price, return, label, or outcome evidence
   participates.

The V1 greatest-volume/nearer-delivery tie across every later contract is
retired for V2 real-data construction. No AMBIGUOUS branch is introduced:
valid adjacent evidence has one candidate; duplicate or forked evidence is
INVALID.

## 14. Canonical Segment and Continuity Boundary

GCCanonicalContractSegment remains an exact-contract, exact-partition,
observed-bar-only value.

V2 rules:

- bars are strictly increasing by index and aware UTC close timestamp;
- each bar reconciles to one non-synthetic source row;
- a session/calendar boundary, contract roll, partition boundary, source
  coverage boundary, or absent observed slot ends the segment;
- source IDs and coverage IDs used for the segment are fully bound through the
  manifest and DATASET identity;
- preceding_missing_bar_count records absent expected slots before the segment,
  even when those slots are attested no-trade intervals;
- a segment never contains an inferred row;
- strict backtest and later feature extraction operate separately by segment;
- a training example, label horizon, rolling statistic, state machine, or
  position may not bridge segments.

This boundary permits sparse session-volume evidence without pretending that
sparse price paths are continuous.

## 15. Development, Quarantine, and OOS Boundary

The existing role enum remains DEVELOPMENT and OOS_HOLDOUT, but OOS_HOLDOUT
means quarantine only until a later numerical-experiment decision accepts an
untouched interval.

V2 must preserve:

- no row in both partitions;
- no development evidence sourced only from OOS_HOLDOUT;
- exact overlap reconciliation without double counting;
- no outcome-guided boundary repair;
- no inspection of quarantine outcomes during data cleaning or roll selection;
- no reuse of a rejected final-OOS interval as development evidence;
- no feature or label crossing a partition, roll, calendar, source-repair, or
  missing-observation boundary.

The current GCQ26 30-day export remains quarantined and must not be described as
accepted final OOS merely because its bytes and overlap reconcile.

## 16. V2 Manifest and Conservation Evidence

The exact V2 manifest field order and annotations are:

    @dataclass(frozen=True)
    class GCDatasetManifest:
        dataset_id: str
        version: str
        source_ids: tuple[str, ...]
        coverage_ids: tuple[str, ...]
        coverage_digest: str
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
        attested_no_trade_interval_count: int
        raw_volume: int
        eligible_volume: int
        excluded_volume: int
        completed_session_volumes: tuple[tuple[str, date, int], ...]
        exclusion_counts: tuple[tuple[str, int], ...]
        roll_trade_dates: tuple[date, ...]

Exact rules:

- coverage_ids are ordered unique accepted COVERAGE identities;
- coverage_digest binds the complete normalized coverage tuple, including every
  Section 9 field except coverage_id, in caller order;
- missing_bar_count counts absent expected observed-bar slots;
- attested_no_trade_interval_count counts the subset covered by accepted
  acquisition evidence;
- a promoted VALID manifest requires:
  attested_no_trade_interval_count <= missing_bar_count;
- any absent slot needed for session volume but not attested prevents promotion;
- parsed, eligible, excluded, development, OOS, and volume conservation remain
  exact;
- completed_session_volumes include only fully calendar- and coverage-qualified
  active/adjacent sessions;
- exclusion_counts contains only actual supplied source rows that are valid
  input rows but canonically excluded from eligible output, and the sum of its
  positive counts equals excluded_row_count exactly;
- OBSERVED_STREAM_GAP is represented only through missing_bar_count, while an
  accepted absent interval is additionally represented through
  attested_no_trade_interval_count; neither is an excluded row;
- SYNTHETIC_NO_DATA_ROW and COVERAGE_MISMATCH are INVALID result reasons, while
  COVERAGE_UNVERIFIED and CALENDAR_UNVERIFIED are UNKNOWN blocking reasons after
  all independently determinable evidence passes validation;
- INVALID and UNKNOWN reason tokens live only in GCDatasetBuildResult reasons or
  blocking_reasons and never enter a promoted manifest exclusion_counts tuple;
- no partial manifest or DATASET identity is promoted on UNKNOWN or INVALID.

DATASET evidence_digest binds every V2 manifest field except dataset_id.

## 17. Exact Public Surface and Frozen Contracts

The V2 module exports exactly these 21 names:

1. GC_DATASET_BUILDER_VERSION
2. GC_DATASET_INSTRUMENT
3. GC_DATASET_TIMEFRAME
4. GC_DATASET_SOURCE_TIMEZONE
5. GC_DATASET_EXCHANGE_TIMEZONE
6. GC_DATASET_TICK_SIZE
7. GC_ROLL_CONFIRMATION_SESSIONS
8. GC_DELIVERY_MONTH_CODES
9. GCDatasetBuildStatus
10. GCSourceRole
11. GCSegmentPartition
12. GCSierraChartBarRow
13. GCSierraChartExport
14. GCSierraChartCoverageEvidence
15. GCCanonicalContractSegment
16. GCDatasetManifest
17. GCDatasetBuildConfig
18. GCDatasetBuildResult
19. parse_sierra_chart_gc_export
20. make_gc_dataset_id
21. build_gc_futures_dataset

Every public dataclass is frozen. Existing field order, annotations, and result
defaults remain exact except the explicit V2 additions in Sections 9 and 16.
No filesystem, network, clock, training, prediction, strategy, signal, order,
risk, execution, or PnL API is added.

## 18. Exact Keyword-Only Public API

The parser signature remains:

    def parse_sierra_chart_gc_export(
        *,
        source_name: str,
        contract: str,
        role: GCSourceRole,
        capture_timestamp: datetime,
        chart_timezone: str,
        timeframe: str,
        raw_bytes: bytes,
    ) -> GCSierraChartExport

The exact V2 identity-builder signature, including parameter order and defaults,
is:

    def make_gc_dataset_id(
        *,
        identity_kind: str,
        config: GCDatasetBuildConfig | None = None,
        source_id: str | None = None,
        source_name: str | None = None,
        source_sha256: str | None = None,
        contract: str | None = None,
        role: GCSourceRole | None = None,
        capture_timestamp: datetime | None = None,
        source_timezone: str | None = None,
        timeframe: str | None = None,
        coverage_start_timestamp: datetime | None = None,
        coverage_end_timestamp: datetime | None = None,
        acquisition_completed_timestamp: datetime | None = None,
        acquisition_evidence_sha256: str | None = None,
        first_trade_date: date | None = None,
        last_trade_date: date | None = None,
        source_ids: tuple[str, ...] = (),
        coverage_ids: tuple[str, ...] = (),
        bar_digest: str | None = None,
        preceding_missing_bar_count: int | None = None,
        partition: GCSegmentPartition | None = None,
        segment_ids: tuple[str, ...] = (),
        calendar_digest: str | None = None,
        coverage_digest: str | None = None,
        evidence_digest: str | None = None,
        roll_trade_dates: tuple[date, ...] = (),
    ) -> str

Its identity_kind accepts exactly SOURCE, COVERAGE, SEGMENT, and DATASET.

The analyzer becomes:

    def build_gc_futures_dataset(
        *,
        exports: tuple[GCSierraChartExport, ...] | None,
        coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
        calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
        config: GCDatasetBuildConfig,
    ) -> GCDatasetBuildResult

Missing top-level context is UNKNOWN only after all independently determinable
supplied counterpart evidence has been validated. Malformed supplied evidence
has INVALID precedence. No default silently supplies coverage.

## 19. Exhaustive V2 Identity Schemas

All identities use canonical JSON, sorted keys, compact separators, exact enum
values, UTC microsecond timestamps, canonical Decimal text, and lowercase
SHA-256. Every identity includes GC-DATASET-BUILDER-V2 and identity_kind.

SOURCE is unchanged from V1 and requires:

- source_name;
- source_sha256;
- contract;
- role;
- capture_timestamp;
- source_timezone;
- timeframe.

SOURCE forbids source_id, every coverage-local parameter, first_trade_date,
last_trade_date, source_ids, coverage_ids, bar_digest,
preceding_missing_bar_count, partition, segment_ids, calendar_digest,
coverage_digest, evidence_digest, roll_trade_dates, and config.

COVERAGE requires:

- source_id;
- source_name;
- source_sha256;
- contract;
- role;
- capture_timestamp;
- source_timezone;
- timeframe;
- coverage_start_timestamp;
- coverage_end_timestamp;
- acquisition_completed_timestamp;
- acquisition_evidence_sha256.

COVERAGE recomputes SOURCE from the complete source fields and requires equality
with source_id. COVERAGE forbids config, first_trade_date, last_trade_date,
source_ids, coverage_ids, bar_digest, preceding_missing_bar_count, partition,
segment_ids, calendar_digest, coverage_digest, evidence_digest, and
roll_trade_dates.

SEGMENT requires config, contract, partition, first_trade_date,
last_trade_date, nonempty ordered unique source_ids, bar_digest, and
preceding_missing_bar_count. It forbids source_id, source_name, source_sha256,
role, capture_timestamp, source_timezone, timeframe, every coverage-local
timestamp/hash parameter, coverage_ids, segment_ids, calendar_digest,
coverage_digest, evidence_digest, and roll_trade_dates. Coverage identity is
not added directly to the segment payload because complete accepted coverage
lineage is bound by the V2 manifest and DATASET identity; segment bars remain
source-row identities.

DATASET requires config, ordered unique source_ids, nonempty ordered unique
coverage_ids, ordered unique segment_ids, calendar_digest, coverage_digest,
evidence_digest, and ordered unique roll_trade_dates. It forbids source_id,
source_name, source_sha256, contract, role, capture_timestamp, source_timezone,
timeframe, every coverage-local timestamp/hash parameter, first_trade_date,
last_trade_date, bar_digest, preceding_missing_bar_count, and partition.

Unknown kinds, missing required fields, supplied forbidden fields, malformed
hashes, duplicate histories, impossible time ranges, source/coverage mismatch,
malformed nested values, or timezone errors raise only TypeError or ValueError
from make_gc_dataset_id.

## 20. Status, Atomicity, and Prefix Invariance

Final precedence remains:

    INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE

- INVALID: malformed, contradictory, synthetic, duplicate-forked, identity-
  inconsistent, calendar-inconsistent, or coverage-inconsistent evidence.
- AMBIGUOUS: retained in the vocabulary but unreachable in V2 because exact
  adjacent roll selection is total; no artificial branch is permitted.
- UNKNOWN: required authoritative calendar, acquisition coverage, predecessor,
  adjacent contract, completed session, or effective-session evidence is
  unavailable after supplied evidence passes validation.
- VALID: every emitted observed bar, segment, roll, manifest field, source,
  coverage, and calendar fact is canonical.
- NONE: valid requested empty scope with no unrequested evidence.

Processing remains atomic by complete canonical trade-date group. A failing or
pending group and every later group promote no bars, segments, roll, manifest,
or dataset identity. Strictly prior complete evidence remains byte-for-byte
unchanged. An unknowable malformed effective moment permits no claimed prefix.

Prefix invariance applies only to a valid prefix ending at:

- a complete calendar session;
- complete accepted coverage;
- a complete observed-bar group;
- no pending adjacent three-session roll;
- no segment or partition boundary under construction.

Only strictly later calendar, source, and matching coverage append qualifies.
Same-effective append, historical insertion, acquisition repair, source
replacement, calendar repair, timezone mutation, role mutation, initial-boundary
change, OOS-boundary change, or added predecessor/adjacent coverage is not a
prefix extension and requires a new DATASET identity and audit.

## 21. Inline Synthetic Exact 48-Case Unit-Test Matrix

Future V2 implementation must preserve exactly these numbered logical cases.
Parameterization may add collected executions without changing the count.

1. Missing export, coverage, or calendar context validates every determinable
   supplied counterpart before UNKNOWN.
2. Exact valid empty requested scope returns NONE; unrequested supplied evidence
   is INVALID.
3. Existing GC contract token, delivery cycle, instrument, timeframe, tick, and
   timezone constants remain exact under V2 version separation.
4. Existing strict UTF-8, header, raw timestamp, Decimal OHLC, integer volume,
   bid/ask conservation, capture, row ordering, and SOURCE identity behavior.
5. Zero-trade/zero-volume inserted no-data row is rejected as synthetic.
6. No absent interval is emitted as a canonical bar or assigned inferred OHLC.
7. Exact GCSierraChartCoverageEvidence fields, annotations, frozen state, and
   aware timestamp normalization.
8. COVERAGE source fields recompute SOURCE and match source_id exactly.
9. Coverage start-inclusive/end-exclusive range and completion/capture ordering.
10. Acquisition evidence hash required; boolean, screenshot name, filename, row
    span, or elapsed time alone cannot prove completeness.
11. Coverage tuple exact causal ordering, overlap reconciliation, and hash-order
    independence.
12. Export row outside accepted coverage is INVALID with no promotion.
13. Sparse interval inside accepted coverage adds zero only to session-volume
    aggregation and emits no bar.
14. Same sparse interval ends the observed-bar segment and increments exact
    missing and attested-no-trade counts.
15. Sparse interval without accepted coverage makes required session volume
    UNKNOWN.
16. Conflicting duplicate or synthetic filler evidence is INVALID, not UNKNOWN.
17. Standard OPEN completed-session volume from observed positive rows plus
    attested absent intervals.
18. EARLY_CLOSE and SESSION_CLOSED coverage/calendar reconciliation.
19. Maintenance/outside-session positive-volume contradiction remains INVALID.
20. Authoritative calendar missing is UNKNOWN; malformed/version-mismatched
    supplied calendar is INVALID.
21. Runtime America/New_York, Asia/Tokyo, and timezone-data version fail-closed
    behavior remains exact.
22. Initial contract requires previous adjacent delivery and three immediately
    preceding eligible completed-session confirmations.
23. Missing GCJ25/GCM25 boundary prevents GCQ25 initial acceptance.
24. A later apparent start is not accepted without its exact predecessor proof.
25. Active contract compares only with exact next_contract(active).
26. Farther-contract absence does not block an otherwise complete active/next
    comparison.
27. Farther-contract greater volume cannot skip the adjacent delivery.
28. Missing active or adjacent completed-session coverage is UNKNOWN.
29. One or two adjacent dominance sessions do not roll.
30. Exact third consecutive adjacent dominance schedules the next eligible
    session roll.
31. Closed calendar date neither counts nor breaks confirmation.
32. Adjacent non-dominance resets confirmation.
33. Effective roll is prospective, monotonic, and independent of future price,
    volume, label, return, and outcome evidence.
34. No same-effective multi-contract jump, reverse roll, or lexical/hash-order
    chronology.
35. Observed-bar segment ends on sparse slot, coverage boundary, calendar
    boundary, roll, and partition boundary.
36. preceding_missing_bar_count reconciles exact absent slots without creating
    rows.
37. No candidate, feature, label, rolling statistic, backtest state, or position
    may cross a segment boundary.
38. Development/quarantine overlap exact reconciliation and no double counting.
39. GCQ26 30-day source remains quarantine, not accepted final OOS.
40. V2 manifest exact source/coverage/segment IDs, coverage digest, row/volume
    conservation, row-only exclusion_counts sum, missing count,
    attested-no-trade subset reconciliation, gap-versus-row separation, and
    UNKNOWN/INVALID result-reason exclusion from promoted manifest evidence.
41. Exhaustive SOURCE required/forbidden schema and V1/V2 identity separation.
42. Exhaustive COVERAGE required/forbidden schema, source recomputation, range,
    completion, evidence-hash, and payload sensitivity.
43. Exhaustive SEGMENT required/forbidden schema and observed-bar-only digest.
44. Exhaustive DATASET required/forbidden schema, coverage IDs/digest, calendar,
    config, roll, OOS, manifest, source, and segment sensitivities.
45. Exact keyword-only names/defaults, frozen public dataclasses, field order,
    annotations, enums, constants, version, and 21 exports.
46. Later determinably malformed calendar/source/coverage group preserves only
    strictly prior immutable evidence; failing and later groups do not promote.
47. Complete strictly-later prefix invariance; acquisition/calendar/source
    repair, same-effective append, insertion, reorder, or version mutation is
    ineligible.
48. Exact three-path future scope, direct dependency allowlist, deterministic
    repeatability, TypeError/ValueError containment, no external I/O, rollback,
    stop conditions, and global freeze preservation.

## 22. Reserved Future Implementation Scope and Gates

Only a later explicit approval may open exactly:

- analysis/gc_dataset_builder.py
- tests/test_gc_dataset_builder.py
- docs/gc_futures_dataset_checkpoint.md

No external fixture is part of that code task. Inline synthetic evidence must be
written first. The corrected implementation must then pass:

1. exact 48 logical-case reconciliation;
2. focused tests with -p no:cacheprovider;
3. full regression with -p no:cacheprovider;
4. independent source/test/checkpoint semantic audit;
5. exact public API, frozen-field, identity-schema, formatting, hash, and
   three-path scope audit;
6. proof that the existing integration proposal and every unrelated file remain
   untouched.

Even after code passes, a private real-data build requires a separate read-only
intake audit for authoritative calendar and acquisition coverage evidence.

## 23. Rollback, Promotion, and Mandatory Stop Conditions

This documentation proposal authorizes no promotion.

For a future V2 implementation, rollback before commit means removing only the
three newly authorized bounded changes with explicit approval. After commit,
rollback uses a bounded revert and never rewrites history or deletes prior
evidence.

Stop immediately if:

- accepted immutable acquisition coverage evidence is unavailable;
- an authoritative versioned GC holiday/early-close calendar is unavailable;
- a synthetic or prior-close-filled row would be required;
- an absent observed interval would need inferred price or trade fields;
- an initial predecessor or adjacent roll contract is unavailable;
- a farther delivery must substitute for the exact adjacent contract;
- a roll depends on same-session or future information;
- a feature, label, candidate, strategy, model, PnL, or OOS outcome is needed to
  decide data cleaning, calendar, coverage, initial boundary, or roll;
- a window must cross a sparse, roll, calendar, partition, source-repair, or
  quarantine boundary;
- coverage evidence cannot be tied to exact source bytes and capture time;
- the V2 public API, identity kinds, exact 48-case count, or three-path scope
  must broaden;
- filesystem, network, external calendar download, importer modification,
  requirements change, package export, runtime, or integration work becomes
  necessary inside the bounded code task;
- any focused/full test, reproducibility, formatting, hash, scope, freeze, or
  independent audit gate fails.

## 24. Final Proposal State and Next Permission Boundary

The documentation decision is:

    READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT

Locked result:

- V1 remains preserved historical implementation evidence;
- current real exports are structurally clean but sparse;
- source completeness and observed-bar continuity are separate V2 facts;
- synthetic no-data bars are forbidden;
- accepted hash-bound acquisition coverage may qualify sparse session volume
  but never create a price bar;
- sparse intervals always split observed-bar segments;
- initial acceptance requires predecessor proof;
- rolls compare only active versus exact adjacent delivery;
- current GCQ26 snapshot remains quarantine;
- authoritative calendar and accepted coverage evidence remain external
  blockers to a private real-data build;
- future V2 code scope is exactly three paths;
- training, features, labels, strategy, backtest, OOS evaluation, integration,
  stage, commit, and push remain unauthorized;
- global code freeze remains active.

The next action, if explicitly authorized, is an independent final audit of this
one documentation file. No V2 implementation or private-data build begins from
this proposal alone.
