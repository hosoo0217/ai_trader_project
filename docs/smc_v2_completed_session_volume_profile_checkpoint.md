# SMC V2 Completed-Session Volume Profile Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-IMPLEMENTATION-CHECKPOINT-2026-08-01`.
- Formal decision commit:
  `eae65e2ad9cddfd5bce56db20067074b4089be08`.
- Formal decision record SHA-256:
  `25C28258F579791D828760D0C01F895F22B29424779DEA7E043A310B43E654FF`.
- Detector version:
  `SMC-V2-COMPLETED-SESSION-VOLUME-PROFILE-1`.
- Task classification: bounded standalone diagnostic implementation.
- Integration status: `NOT_STARTED`.
- Global code-freeze status outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `orderflow/volume_profile.py`
- `tests/test_volume_profile.py`
- `docs/smc_v2_completed_session_volume_profile_checkpoint.md`

No external fixture, calendar, holiday, timezone, market-data, or generated file
was created. No existing source, test, fixture, importer, footprint model,
dependency manifest, package initializer, configuration, runtime, strategy,
risk, execution, exporter, or integration file changed.

## 3. Test-First and Correction Evidence

The exact `48` numbered logical cases were written before the production module.
The first collection exposed one test-only syntax defect: OHLC keyword overrides
were placed outside the `_bar(...)` helper call in eight assertions. The defect
was corrected only in the new test file. No production file yet existed.

The intended RED phase then produced:

- `ModuleNotFoundError: No module named 'orderflow.volume_profile'`

The first bounded production implementation produced:

- `89 passed in 0.68s`

A semantic self-audit then identified a fail-closed precedence gap: an earlier
missing-calendar or missing-data `UNKNOWN` could return before independently
determinable later malformed or unrequested evidence produced the locked higher
precedence `INVALID`. It also identified that a later unrequested calendar entry
should retain strictly prior immutable profile/snapshot evidence.

Tests were added inside existing logical Cases 20, 23, and 47. The source was
corrected to retain pending `UNKNOWN`, continue deterministic validation, apply
`INVALID > UNKNOWN`, suppress uncertain/later promotion, and preserve only
strictly prior promoted evidence. The focused result remained:

- `89 passed in 0.73s`

The final matrix audit expanded existing logical Cases 23, 28, 41-46, and 48
without changing the locked case count. It added:

- all missing-top-level permutations with malformed-counterpart precedence;
- non-dividing session-grid rejection;
- exhaustive PROFILE required and forbidden parameters;
- exhaustive SNAPSHOT required and forbidden parameters;
- exact builder/analyzer keyword-only names and every default;
- every public dataclass field list, default set, and frozen state;
- exact enum values, exports, and absence of transition/HVN/LVN surface;
- duplicate, reorder, historical insertion, and same-effective prefix
  ineligibility;
- AST-based forbidden importer/footprint dependency checks.

The independent final audit then reproduced three additional public-API defects:

- an empty requested-session tuple silently ignored supplied bars or calendar
  entries instead of rejecting them as unrequested evidence;
- PROFILE identity construction accepted a `trade_date` that did not reconcile
  with the supplied America/New_York session provenance;
- PROFILE identity construction accepted aggregate price levels lying outside
  every supplied source-bar OHLC range.

Tests were added first inside existing logical Cases 20, 27, and 41. The RED run
produced `4 failed, 105 passed in 0.93s`. The bounded source correction now emits
`UNREQUESTED_BAR` or `UNREQUESTED_CALENDAR_ENTRY`, binds PROFILE session open and
close to the supplied weekday trade date while retaining valid early closes, and
requires every canonical aggregate price level to fall inside at least one
source-bar OHLC range.

The next independent re-audit found one remaining ordering defect inside the
known-empty request boundary: a valid supplied bar with `calendar_entries=None`,
or a valid supplied calendar entry with `bars=None`, returned generic
`MISSING_TOP_LEVEL_CONTEXT` before the independently determinable unrequested
evidence was classified. Public analyzer assertions were added first inside
existing logical Cases 20 and 27. The RED run produced
`2 failed, 107 passed in 0.87s`.

The bounded correction now evaluates a known-empty `trade_dates=()` scope before
the generic missing-top-level return. Supplied valid or malformed evidence retains
`INVALID` precedence, emits no PROFILE/SNAPSHOT, empty supplied tuples still
produce `NONE / NO_REQUESTED_SESSIONS`, and the genuinely absent
`bars=None, calendar_entries=None` case remains `UNKNOWN`.

The final focused result is:

- `109 passed in 0.68s`
- exactly `48` sequential logical cases
- `61` additional collected tests from locked parameterization

The final full regression result is:

- `1778 passed in 10.13s`

Every focused and full run used `-p no:cacheprovider`.

## 4. Locked Public Surface Implemented

The module exports exactly:

- `COMPLETED_SESSION_VOLUME_PROFILE_VERSION`
- `COMPLETED_SESSION_VOLUME_PROFILE_TIMEZONE`
- `COMPLETED_SESSION_VOLUME_PROFILE_SOURCE`
- `CompletedSessionVolumeProfileCompleteness`
- `CompletedSessionVolumeProfileDataQuality`
- `CompletedSessionVolumeLevel`
- `CompletedSessionVolumeBar`
- `CompletedSessionVolumeAtPrice`
- `CompletedSessionVolumeProfile`
- `CompletedSessionVolumeProfileSnapshot`
- `CompletedSessionVolumeProfileResult`
- `make_volume_profile_id`
- `analyze_completed_session_volume_profiles`

Both functions are exactly keyword-only and match the formal decision. All six
public dataclasses are frozen with the exact locked fields and result defaults.
No public adapter, transition, mutable lifecycle, registry, runtime hook, or
integration entry point exists.

## 5. Immutable Canonical Input Boundary

The analyzer accepts only exact tuples of frozen
`CompletedSessionVolumeLevel`, `CompletedSessionVolumeBar`, and the committed
versioned `KillZoneCalendarEntry` dependency.

Price, OHLC, bid, ask, reported total, index, and duration evidence is exact
integer data; boolean-as-integer values fail closed. Input levels are strictly
increasing by tick inside each bar, OHLC geometry contains every level, every bar
is fully closed, and normalized bar opens and indices are independently strictly
increasing. Reordering, duplicate indices/opens/levels, overlap, off-grid timing,
naive timestamps, malformed nested dataclasses, negative/fractional/non-finite
volume, and exception leakage are rejected.

Legacy mutable float-bearing `orderflow.footprint.FootprintCandle` is not imported
or accepted. The only admitted source token is `ACSIL_FULL_FOOTPRINT`.
`BAR_SUMMARY`, unknown, mixed, legacy, and unreviewed equivalent sources are
`INVALID`; no volume is clamped, rounded, distributed, or approximated.

## 6. Timezone, Calendar, and Session Semantics

The fixed timezone is exactly `America/New_York`. The current runtime provides
`tzdata 2026.2`. Supplied timezone-data version evidence must normalize to an
exact runtime match. A supplied mismatch is `INVALID`; unavailable runtime
timezone/version authority is `UNKNOWN` only after independently supplied
evidence is checked for higher-precedence deterministic defects.

GC session boundaries are database-derived:

- open: prior calendar day local `18:00`, inclusive;
- close: trade date local `17:00`, exclusive;
- maintenance: local `[17:00, 18:00)`, outside the session.

`OPEN` requires exact standard boundaries. `EARLY_CLOSE` requires the standard
open and a strictly earlier valid close. `SESSION_CLOSED` requires absent
timestamps. Missing weekday calendar coverage is `UNKNOWN` with
`CALENDAR_UNVERIFIED`; holidays and weekends produce `NONE` unless contradictory
open evidence or bars make the result `INVALID`. Spring-forward and fall-back
sessions use IANA conversion rather than a fixed offset.

No profile is emitted before the exact close. The analyzer accepts only bars
wholly attributable to one requested eligible session. Boundary straddles,
maintenance bars, bars from unrequested sessions, calendar forks, calendar
version mismatch, and impossible intervals fail closed.

An empty requested-session tuple produces `NONE / NO_REQUESTED_SESSIONS` only
when both supplied bar and calendar tuples are present and empty. Any supplied
bar or calendar entry is unrequested evidence and produces `INVALID` with no
promotion even when its counterpart collection is `None`. When both evidence
collections are genuinely absent, the result remains
`UNKNOWN / MISSING_TOP_LEVEL_CONTEXT`.

## 7. Conservation, Completeness, and Quality

Conservation is exact at all three levels:

```text
level reported total = bid + ask
bar reported total = sum(level reported totals)
profile total = sum(bar totals) = sum(aggregated price-level totals)
```

No tolerance or rounding is used. The exact session-open-derived bar grid must
be divisible by `bar_duration_seconds`. Exact grid coverage emits
`COMPLETE/QUALIFIED`. Canonical non-overlapping missing cells emit a reportable
immutable `INCOMPLETE/UNQUALIFIED` profile. Empty required session evidence is
`UNKNOWN`; canonical zero total volume is `NONE` and creates no identity.

## 8. Deterministic POC and Value Area

The session volume-weighted mean is stored as a reduced exact integer fraction.
POC selection is deterministic:

1. maximum aggregate total volume;
2. minimum exact distance to the volume-weighted mean;
3. lower tick if still tied.

Every maximum-volume candidate is retained in sorted `poc_tied_ticks`.

Value Area starts at POC and expands one adjacent integer tick at a time until
`covered_volume * 10 >= total_volume * 7`. The greater-volume side is chosen;
an exact tie chooses the lower-price side. Sparse untraded ticks contribute zero
without fabricating source rows. Covered volume and percentage are exact reduced
fractions and may exceed 70% after the final whole-tick expansion.

Negative and arbitrary-magnitude ticks use unbounded integer arithmetic. No
binary float, Decimal context, interpolation, two-level expansion, HVN, or LVN
participates.

## 9. Deterministic Identity and Immutable Output

`make_volume_profile_id` supports exactly `PROFILE` and `SNAPSHOT`.

Both identities bind detector version, normalized instrument/timeframe,
calendar version, fixed timezone, and runtime-matching timezone-data version.
They use canonical UTF-8 JSON, sorted keys, compact separators, exact UTC
microsecond timestamps, exact integers/fractions, and lowercase SHA-256.

`PROFILE` validates every required field and forbids snapshot-only fields. It
recomputes and reconciles total volume, weighted mean, all POC candidates,
canonical POC, Value Area, covered fraction, grid completeness, quality pairing,
source bar moments, OHLC geometry, and session provenance. Its standard open is
the prior calendar day at America/New_York 18:00, its close is no later than the
weekday trade-date 17:00 standard close, and valid earlier closes remain
representable. Every aggregate price level must lie within at least one supplied
source-bar OHLC range.

`SNAPSHOT` requires an ordered unique nonempty well-formed PROFILE-ID history and
an aware effective timestamp. It forbids every PROFILE-only field. Unknown kinds,
malformed hashes, forbidden/missing parameters, nested malformed values, and
runtime timezone mismatch expose only `TypeError` or `ValueError`.

One immutable PROFILE is formed at completed-session close. One cumulative
immutable SNAPSHOT promotes atomically with it. There is no transition,
reclassification, developing value, expiry, rolling profile, anchored profile,
HVN, LVN, direction, bias, score, signal, trade action, or PnL dependency.

## 10. Status Precedence, Cutoff, and Prefix Invariance

Final status precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Version 1 has no reachable valid `AMBIGUOUS` branch. Duplicate or forked evidence
is `INVALID`, not synthetic ambiguity.

A determinably later invalid bar/calendar/session group returns final `INVALID`,
preserves byte-identical PROFILE/SNAPSHOT evidence strictly before the failing
effective group, and promotes nothing at or after it. A pending missing-calendar
or missing-data `UNKNOWN` cannot suppress later deterministic `INVALID` evidence
and cannot promote its own or later session output. An unknowable malformed
effective moment claims no trustworthy prefix.

Repeating complete input is byte-stable. A strictly later complete session append
preserves every prior profile, profile ID, snapshot, and history prefix.
Same-session/same-effective append, partial group, historical insertion, repair,
deletion, reorder, source/calendar/tzdata/duration mutation, or as-of
reinterpretation is ineligible and never silently normalized.

## 11. Exact Logical Test Matrix

`tests/test_volume_profile.py` retains exact sequential comments:

`Logical case 1` through `Logical case 48`

The matrix covers exact immutable types, malformed nested evidence, all source
qualification boundaries, three-level conservation, timestamps/OHLC/grid/bar
ordering, timezone availability/version/DST, standard and early-close sessions,
maintenance/weekend/holiday/missing calendar behavior, as-of completion,
empty-request unrequested-evidence rejection, session attribution,
completeness/quality, aggregation, all POC/Value Area tie rules,
arbitrary-magnitude integers, exhaustive PROFILE/SNAPSHOT schemas including
trade-date/session and aggregate-level/OHLC reconciliation, exact public
reflection, status precedence, atomic cutoff, prefix invariance, repeatability,
deterministic multi-session output, and forbidden dependency and integration
surfaces.

## 12. Isolation and Regression Evidence

The production module imports only deterministic standard-library utilities,
the committed Kill-zone calendar types, and `SMCV2PrimitiveStatus` plus UTC
normalization from shared primitives. It does not import legacy footprint or
Sierra importer code and performs no pandas, CSV, broker, external API, calendar
download, file, network, config, strategy, risk, execution, package registration,
or integration work.

The full suite grew from `1669` passing tests at the formal decision checkpoint
to `1778` passing tests. Existing behavior outside the exact bounded capability
remained unchanged.

## 13. Artifact Evidence

- `orderflow/volume_profile.py`
  - SHA-256:
    `6395C7DF9D9DD237CD5D68FE21F562739970AB3AE2AFEAB74A832A34BC853044`
  - bytes: `57639`
  - physical lines: `1430`
- `tests/test_volume_profile.py`
  - SHA-256:
    `BFDEA4B808EF49FF50624287DC2B0E960EE8B0AFAD04A5CD1E2ACC5C766C1922`
  - bytes: `44342`
  - physical lines: `1024`
- `docs/smc_v2_completed_session_volume_profile_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes: `16667`
  - physical lines: `364`

All three artifacts are UTF-8 without BOM, use LF line endings, and contain no
tabs or trailing whitespace.

## 14. Promotion, Rollback, Stop, and Freeze State

This checkpoint does not authorize integration, staging, commit, push, paper
progression, live progression, tuning, or runtime use. Promotion requires an
independent exact-scope code/test/checkpoint audit and separate explicit staging
authorization.

Before commit, rollback is deletion of exactly the three untracked task artifacts
and requires explicit authorization. After commit, rollback must use a bounded
revert rather than history rewriting.

Stop immediately on dependency drift, scope expansion, source-equivalence claim,
legacy/importer mutation need, calendar/tzdata uncertainty, conservation failure,
float/rounding requirement, unspecified POC/Value Area tie, public API mismatch,
identity nondeterminism, uncontained exception, exact 48-case reconciliation
failure, focused/full regression failure, or integration request outside a
separately approved freeze-lift decision.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`
- `EXACT_CHANGED_PATHS=3`
- `LOGICAL_CASES=48`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_COLLECTED=109`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=1778`
- `EXTERNAL_FIXTURE_CREATED=False`
- `EXTERNAL_CALENDAR_CREATED=False`
- `EXTERNAL_TIMEZONE_FILE_CREATED=False`
- `FOOTPRINT_CHANGED=False`
- `IMPORTER_CHANGED=False`
- `REQUIREMENTS_CHANGED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_PERFORMED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`
