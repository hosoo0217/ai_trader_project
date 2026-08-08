# GC Futures Split-Session Calendar Change Proposal

## 1. Proposal Record

- Status: `ACCEPTED_IMPLEMENTED_COMMITTED_AND_PUSHED`
- Change class: documentation-only acceptance correction for a completed bounded,
  fail-closed implementation
- Instrument: COMEX Gold futures (`GC`)
- Dataset timeframe: five-minute closed bars
- Original proposal version: `GC-SPLIT-SESSION-PROPOSAL-V1`
- Acceptance revision:
  `GC-SPLIT-SESSION-PROPOSAL-V1-ACCEPTANCE-ADDENDUM-1`
- Original proposed bytes SHA-256:
  `8E1DC59F84C9699BD57C5397667AEC630C5182CF11D6CB667DFEB3CDBA73445D`
- Prepared from repository baseline:
  `f7e8a1b25a40ff5148c31bcb1a8d1d27647f60cc`
- Accepted implementation commit:
  `14b7e1aa5031cea4c1e997831e47fd8fd41d2ed3`
- Accepted implementation parent:
  `f7e8a1b25a40ff5148c31bcb1a8d1d27647f60cc`
- Accepted implementation subject:
  `feat(analysis): add GC split-session calendar support`
- Accepted checkpoint SHA-256:
  `D7F9261347C931FC5C897CA8330016C9AA974A69199A181D29F02CD519BC7760`
- Remote promotion evidence: local `HEAD`, local `origin/main`, and live remote
  `main` were all verified at the accepted implementation commit.
- Global code freeze: active outside this one documentation correction

The original proposed bytes did not themselves authorize implementation or Git
promotion. Subsequent explicit user authorizations activated only the exact
three-path exception in Section 22. That implementation passed its independent
scope, hash, semantic, structural, focused, and full-regression gates before exact
local commit and remote promotion.

This acceptance correction records that completed history. It grants no new
authority for private-data normalization, dataset construction, feature or label
generation, training, integration, strategy selection, paper trading, or live
execution. Historical future-tense wording below is retained as the locked contract
that governed implementation; it describes the state at original proposal time and
does not imply that implementation is still pending.

## 2. Selected Decision

The selected direction is to add a dataset-builder-local, versioned split-session
calendar input while preserving the existing shared `KillZoneCalendarEntry` contract.
The builder will accept either a canonical single-interval entry or a canonical
split-session entry for each trade date. A split-session trade date is one logical
completed session made from two or more ordered, disjoint trading intervals.

The following alternatives are rejected:

- forcing a split session into one continuous open/close interval;
- treating an authoritative halt as missing market data;
- deleting the exceptional trade date from the calendar;
- assigning bars by the current prior-day-18:00 heuristic when an explicit interval
  says otherwise;
- changing `smc.kill_zones.KillZoneCalendarEntry` for a dataset-only requirement;
- silently ignoring the exceptional session during roll confirmation.

## 3. Why a Change Is Required

The current builder accepts only `KillZoneCalendarEntry`, whose non-closed form has
one open timestamp and one close timestamp. The current scanner also requires the open
to equal trade-date-minus-one-calendar-day at 18:00 America/New_York. That model cannot
represent the authoritative 2024 and 2025 Thanksgiving GC sequences.

Read-only code audit also proves that omission is unsafe:

- a bar whose inferred trade date has no calendar entry produces
  `CALENDAR_COVERAGE_MISSING` and a chronological UNKNOWN cutoff;
- roll confirmation iterates the remaining non-closed calendar entries, so deleting
  an exceptional date can make nonadjacent sessions appear consecutive;
- segment construction treats an unmodelled intraday halt as missing five-minute
  slots instead of an attested no-trade interval.

Therefore final 2024-2025 dataset promotion remains blocked until the split-session
model is implemented and independently validated.

## 4. Exact Documentation-Only Scope

The original proposal and this acceptance correction affect only:

- `docs/gc_futures_split_session_calendar_change_proposal.md`

No other tracked or private file may change in this correction task. In particular,
this correction does not alter the accepted source, tests, checkpoint, calendar
intake README, normalization draft, fixtures, requirements, configuration,
integration wiring, or private evidence. Staging, commit, and push of this exact
documentation correction require their normal bounded audits and authorization.

## 5. Locked Baseline and Dependency Hashes

The proposal is based on these exact artifacts:

- `analysis/gc_dataset_builder.py`
  - SHA-256:
    `9A3519DA97C0AA526EC4A5A8C867B5BF14AE514BA156F6A11ADDD410B66C1858`
- `tests/test_gc_dataset_builder.py`
  - SHA-256:
    `DFCE06D6C9B8EECD10504F35D092D6A0652434D7A995C846E8A797F08919F9C3`
- `docs/gc_futures_dataset_build_freeze_lift_decision.md`
  - SHA-256:
    `6C6E323D4327377D007219F3E5A5877DD076BB947FFA002BC30184684277A466`
- `docs/gc_futures_2026_pilot_dataset_change_proposal.md`
  - SHA-256:
    `F39D3E256153262A1584B98DFE7B6F4588A06F2EABDFFD05AA0C9996F4B5B421`
- `smc/kill_zones.py`
  - SHA-256:
    `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21`

Any implementation against different dependency bytes requires a fresh preflight.

The accepted V3 implementation was subsequently audited at these exact artifact
bytes:

- `analysis/gc_dataset_builder.py`
  - SHA-256:
    `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121`
- `tests/test_gc_dataset_builder.py`
  - SHA-256:
    `4D179ED76198DA44263535FA497B2E2B8D67F2FAFEA4C3F8A6DC63A32F267974`
- `docs/gc_futures_split_session_calendar_checkpoint.md`
  - SHA-256:
    `D7F9261347C931FC5C897CA8330016C9AA974A69199A181D29F02CD519BC7760`

Final implementation evidence was exact `48` logical cases, `239` focused tests
passed, and `2156` full-regression tests passed. These accepted implementation
hashes do not replace the original baseline hashes; they record the completed
transition from that baseline.

## 6. Authoritative Evidence Boundary

The controlling disputed-field evidence is the byte-preserved CME Global Command
Center response in case `04687271`:

- SHA-256:
  `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`
- sender authentication: DKIM, SPF, and DMARC passed in the preserved EML;
- source timezone: Eastern Time, normalized only with IANA
  `America/New_York`;
- semantic role: additive clarification that supersedes only the previously disputed
  Thanksgiving and closed-date fields.

Earlier EMLs and official workbooks remain immutable provenance. The final
clarification does not erase them. Sierra Chart bars may corroborate activity, but
bar presence or absence is not authoritative proof of an official open, halt, close,
or trade-date assignment.

The pure builder performs no filesystem or network I/O and therefore validates only
the supplied artifact-ID/hash shapes and their deterministic binding. A separate
private preflight must rehash the raw artifacts and reconcile those supplied values
before a real dataset call. The builder must not claim that it independently opened or
authenticated a foreign artifact.

## 7. Locked Confirmed Thanksgiving Sequences

All intervals below are start-inclusive and end-exclusive in
`America/New_York` before UTC normalization.

For trade date `2024-11-29`, the authoritative logical session is:

1. `[2024-11-27 18:00:00 ET, 2024-11-28 14:30:00 ET)`;
2. `[2024-11-28 18:00:00 ET, 2024-11-29 14:45:00 ET)`.

The gap `[2024-11-28 14:30:00 ET, 2024-11-28 18:00:00 ET)` is an attested no-trade
interval. The next session opens `2024-12-01 18:00:00 ET` for trade date
`2024-12-02`.

For trade date `2025-11-28`, the authoritative logical session is:

1. `[2025-11-27 18:00:00 ET, 2025-11-27 21:40:00 ET)`;
2. `[2025-11-28 08:30:00 ET, 2025-11-28 17:00:00 ET)`.

The gap `[2025-11-27 21:40:00 ET, 2025-11-28 08:30:00 ET)` is an attested no-trade
interval. Trading after the 08:30 reopen belongs to trade date `2025-11-28`.

No alternative floor, TAS, inferred, or approximate time is accepted.

## 8. Selected Calendar Model

A normalized calendar stream contains exactly one entry per represented trade date.
Each entry is exactly one of:

- the existing single-interval `KillZoneCalendarEntry`; or
- the new dataset-local `GCSplitSessionCalendarEntry`.

The tuple is caller supplied and is never silently sorted, repaired, deduplicated, or
enriched. Entries must be strictly increasing by `trade_date`, share one exact
`calendar_version`, and have globally nonoverlapping trading intervals.

A split-session entry represents one completed trade date, not multiple sessions for
roll or partition purposes. Its gaps are official no-trade intervals, not missing
bars and not zero-volume synthetic bars.

## 9. Exact New Frozen Dataclass Contracts

The future implementation may add exactly these public frozen dataclasses:

```python
@dataclass(frozen=True)
class GCDatasetSessionInterval:
    start_timestamp: datetime
    end_timestamp: datetime


@dataclass(frozen=True)
class GCSplitSessionCalendarEntry:
    calendar_version: str
    trade_date: date
    intervals: tuple[GCDatasetSessionInterval, ...]
    source_artifact_ids: tuple[str, ...]
    source_artifact_sha256s: tuple[str, ...]
```

There are no defaults. Boolean values are invalid wherever an integer or date-like
scalar is required. Timestamps must be timezone-aware `datetime` instances.

`source_artifact_ids` and `source_artifact_sha256s` must be nonempty, equal-length,
unique paired tuples. Artifact IDs must be strictly lexicographically increasing;
hashes must be lowercase or uppercase canonical 64-hex values normalized to lowercase
for identity payloads. Hash order is evidence-pair order and is never a chronology
tie-break.

## 10. Split-Entry Structural Validation

`intervals` must be an exact tuple with at least two members. For every interval:

- both timestamps are aware and normalize deterministically to UTC;
- start is strictly earlier than end;
- start and end lie on the exact five-minute grid;
- duration is a positive integral multiple of five minutes;
- the tuple is strictly increasing by normalized start;
- the previous end is strictly earlier than the next start;
- no interval overlaps any interval belonging to another calendar entry.

An exact duplicate entry, duplicate trade date, overlapping interval, touching
intervals that should have been merged, out-of-order member, empty evidence tuple,
malformed hash, or inconsistent version is INVALID. The builder never guesses the
intended correction.

## 11. Single-Interval Compatibility Contract

Existing `KillZoneCalendarEntry` behavior remains exact:

- `OPEN` is prior-calendar-day 18:00 through trade-date 17:00;
- `EARLY_CLOSE` begins at that same canonical open and ends strictly after open and no
  later than trade-date 17:00;
- `SESSION_CLOSED` has no open or close timestamps;
- existing valid V2 callers that supply only single-interval entries produce the same
  bars, segments, roll dates, counts, and status under V3 before the required version
  and identity changes are considered.

The shared Kill-zone module, its enums, identities, and analyzer are not modified.

## 12. Timezone and tzdata Binding

Every local schedule timestamp is interpreted with IANA `America/New_York`, including
DST database rules. Fixed offsets such as `UTC-5` or `UTC-4` are forbidden.

The supplied `GCDatasetBuildConfig.timezone_data_version` must still equal the runtime
tzdata version. If the runtime version or `America/New_York` is unavailable, the build
is INVALID. Equivalent aware timestamps that normalize to the same UTC instant are
identity-equivalent; naive timestamps and nonexistent/ambiguous local-time
representations without an unambiguous UTC instant are INVALID.

## 13. Deterministic Row-to-Trade-Date Assignment

The implementation must build one normalized interval index from all calendar entries
before processing rows. A bar belongs to a trade date only when its complete
start-inclusive/end-exclusive bar interval is contained in exactly one declared
trading interval.

- exactly one match: use that entry's explicit `trade_date`;
- zero matches with positive volume: INVALID `ROW_OUTSIDE_DECLARED_SESSION`;
- zero matches with zero volume: exclude as `OUTSIDE_SESSION_ZERO_VOLUME`;
- more than one match: INVALID `CALENDAR_INTERVAL_OVERLAP`.

For split entries, `_trade_date_for_start()` is not authoritative and must not
override explicit interval membership. This rule is essential for the first interval
of trade date `2024-11-29`.

## 14. Completed-Session Volume and Coverage

One split entry contributes one completed-session volume per contract and trade date.
Expected five-minute slots are the ordered concatenation of all declared intervals.
No slot is expected inside an attested gap.

Completed volume is eligible only when:

- every declared interval is completely covered by accepted source-role evidence;
- capture and acquisition-completion timestamps are strictly after the final interval
  end;
- every observed positive-volume row is inside a declared interval;
- no required slot is missing unless the source's locked no-trade evidence explicitly
  permits it under the existing contract.

Volume is summed once across all interval members. A partial split session cannot
contribute roll evidence and produces UNKNOWN, not a silently smaller completed total.

## 15. Roll Confirmation Semantics

Each complete split-session trade date counts as exactly one eligible session in the
prior-session three-confirmation rule. Individual intervals never increment the
dominance counter separately.

The dominance counter resets when comparable completed volume is unavailable. A
quarantined, missing, partial, or malformed calendar date cannot be skipped and cannot
make the sessions on either side appear consecutive. A roll discovered on a complete
split session still becomes effective only on the next complete eligible calendar
entry under the existing policy.

Historical calendar insertion, repair, or version mutation requires a full rebuild;
it is not a prefix append.

## 16. Segment and Gap Semantics

Every official gap between split-session intervals forces a new canonical segment even
when contract, partition, trade date, source IDs, and coverage IDs are unchanged.

For the first segment after an attested gap:

- `preceding_missing_bar_count` is exactly `0` for that official gap;
- the gap contributes one to `attested_no_trade_interval_count`;
- the gap duration is not added to `missing_bar_count`;
- no lag, feature, label, lifecycle, or model context may bridge the segment boundary.

An unexplained five-minute discontinuity inside a declared trading interval remains
missing-data evidence under the existing rules. Attested and unexplained gaps must not
share the same counter.

## 17. Manifest Conservation and Data Quality

The V3 `GCDatasetManifest` retains its existing exact public field names, order, types,
and frozen state. It must preserve row and volume conservation:

```text
parsed_row_count = eligible_row_count + excluded_row_count
raw_volume = eligible_volume + excluded_volume
```

Its existing fields receive these exact V3 meanings:

- `attested_no_trade_interval_count` is the exact number of official gaps between
  promoted split-session intervals;
- `missing_bar_count` excludes every slot inside those official gaps;
- `completed_session_volumes` contains one combined value per promoted split trade
  date and contract;
- the DATASET identity's `calendar_digest` binds interval boundaries and evidence
  hashes even though the digest is not exposed as a separate manifest field.

No new manifest field is added in this bounded change. V2 and V3 meanings are not
mixed because the manifest `version` is incremented and every V3 dataset identity
binds that version.

## 18. Versioning and Deterministic Identity

The future implementation must increment the builder version from V2 to
`GC-DATASET-BUILDER-V3-SPLIT-SESSION`.

The calendar digest payload for every entry contains a type discriminator:

- `SINGLE_INTERVAL` plus the existing status/open/close payload; or
- `SPLIT_SESSION` plus trade date, ordered normalized UTC intervals, artifact IDs, and
  artifact SHA-256 values.

SOURCE and COVERAGE identities remain unchanged. SEGMENT and DATASET identities retain
their existing field names, but V3 dataset evidence and the V3 calendar digest make
V2 and V3 outputs intentionally nonidentical. Equivalent UTC interval representations
must hash identically; interval order, boundary, trade date, evidence hash, calendar
version, or tzdata version changes must change the digest and dataset identity.

## 19. Exact Public API and Compatibility Boundary

The future builder signature remains keyword-only with the same parameter names and
defaults:

```python
def build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
    calendar_entries: tuple[
        KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...
    ] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult:
    ...
```

`parse_sierra_chart_gc_export()` and `make_gc_dataset_id()` keep their existing exact
signatures. The only new exports are:

- `GCDatasetSessionInterval`
- `GCSplitSessionCalendarEntry`

No package `__init__`, engine, strategy, execution, training, configuration, CLI, or
main-module export is added in this bounded change.

## 20. Atomic Processing, Status, and Prefix Invariance

Status precedence remains:

```text
INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE
```

Calendar validation occurs before promotion. A determinably later malformed entry
produces INVALID while preserving only strictly prior immutable complete evidence.
Nothing from the failing trade-date group or any later group may promote.

Prefix invariance applies only to a complete valid prefix followed by strictly later
complete calendar, coverage, and export evidence. Same-trade-date repair, interval
insertion, historical calendar insertion, reorder, evidence-hash change, or calendar
version mutation is not an eligible append and requires a full rebuild with new
identities.

## 21. No-Look-Ahead and Private Normalization Boundary

The CME email was acquired after the historical sessions. Its retrieval time and hash
remain provenance; it may define historical exchange-session boundaries but may not
introduce price, outcome, entry, exit, risk, or PnL information.

Raw EML and workbook bytes remain outside Git. A later private normalization must be
derived without mutating raw artifacts and must record the exact source hashes. V3
implementation acceptance is now satisfied, but private normalization still requires
a separately bounded authorization and immutable acquisition audit. No dataset,
feature, label, model, or training promotion may use a hand-edited continuous
interval in place of the locked split intervals.

## 22. Authorized and Realized Exact Implementation Scope and 48-Case Matrix

The implementation exception was authorized and realized at exactly:

- `analysis/gc_dataset_builder.py`
- `tests/test_gc_dataset_builder.py`
- `docs/gc_futures_split_session_calendar_checkpoint.md`

No external fixture was created; tests use inline synthetic evidence. The exact
logical matrix remains 48 numbered cases:

1. existing valid OPEN single interval;
2. existing valid EARLY_CLOSE single interval;
3. existing valid SESSION_CLOSED entry;
4. mixed single and split entries with one version;
5. exact 2024-11-29 two-interval sequence;
6. exact 2025-11-28 two-interval sequence;
7. equivalent UTC timestamp determinism;
8. runtime tzdata mismatch or zone unavailable;
9. naive split timestamp;
10. non-tuple intervals;
11. fewer than two intervals;
12. zero/negative/non-grid interval duration;
13. out-of-order intervals;
14. overlapping intervals;
15. touching intervals requiring canonical merge rejection;
16. cross-entry global overlap;
17. duplicate trade date or exact duplicate entry;
18. calendar version mismatch;
19. empty/unequal evidence tuples;
20. duplicate/out-of-order artifact IDs or malformed hash;
21. row in first 2024 interval maps to trade date 2024-11-29;
22. row in second 2024 interval maps to trade date 2024-11-29;
23. row in first 2025 interval maps to trade date 2025-11-28;
24. row in second 2025 interval maps to trade date 2025-11-28;
25. positive-volume row inside attested gap is INVALID;
26. zero-volume row inside attested gap is excluded;
27. row matching no calendar interval;
28. row matching multiple calendar intervals;
29. complete coverage across every split interval;
30. missing coverage for first interval is UNKNOWN;
31. missing coverage for later interval is UNKNOWN with prior preservation;
32. acquisition completion before final interval end is ineligible;
33. exact combined completed-session volume;
34. incomplete required slot cannot supply roll volume;
35. one split trade date counts once for dominance;
36. three complete logical sessions confirm roll;
37. missing/quarantined date resets confirmation;
38. roll becomes effective on next complete eligible session;
39. official gap creates two segments;
40. official gap is not a missing-bar count;
41. unexplained in-interval gap remains missing-data evidence;
42. row/volume conservation with split session;
43. calendar digest type/boundary/evidence sensitivity;
44. V2 single-only semantic compatibility apart from V3 identity;
45. exact keyword-only signatures, frozen fields, version, and exports;
46. malformed nested values and exception containment;
47. complete-prefix strictly-later append invariance;
48. same-date repair/reorder/version mutation rejection and forbidden integration
    surface.

## 23. Verification, Promotion, Rollback, and Stop Conditions

The original end-to-end dataset-promotion plan required all of the following:

- independent semantic and structural review of this proposal;
- test-first implementation only within the reserved three paths;
- exact 48-case reconciliation;
- focused and full regression PASS with cache provider disabled;
- artifact hashes, byte/line counts, signatures, exports, and diff scope recorded in
  the checkpoint;
- private normalization independently reconciled to all accepted raw hashes before
  any private dataset promotion;
- exact source-to-row audit for every split interval before any private dataset
  promotion;
- no look-ahead, partition leakage, or continuity across attested gaps;
- explicit later authorization before stage, commit, and push, with separate future
  authorization still required for private dataset build or training.

The builder implementation gate required the proposal review, exact three-path
scope, 48-case reconciliation, focused and full-regression PASS, artifact audit,
staging audit, commit preflight, local commit, push preflight, exact push, and
live-remote verification. Those steps are complete. This closes only the builder
implementation promotion gate; it does not claim that the private normalization or
end-to-end dataset-promotion requirements above were completed. Private
normalization, private dataset construction, feature/label execution, training,
integration, paper trading, and live execution remain stopped.

Rollback of the accepted implementation must use a bounded revert of commit
`14b7e1aa5031cea4c1e997831e47fd8fd41d2ed3`, never history rewriting. Existing
raw evidence remains immutable and outside Git.

STOP immediately if authoritative intervals conflict, an interval cannot be assigned
to exactly one trade date, source hashes fail, required calendar coverage is missing,
roll evidence would cross an incomplete session, the shared Kill-zone contract would
need mutation, implementation escapes the three paths, or any strategy/training
authority is inferred from this diagnostic data change.

## 24. Final Decision and Next Single Task

The authoritative CME clarification resolved the source dispute and the accepted V3
implementation now resolves the corresponding builder schema limitation. The project
must not force these sessions into the V2 single-interval model and must not reopen
the accepted deterministic contract without new contradictory authoritative
evidence.

The next single task, only after this acceptance correction is independently audited
and promoted, is a read-only private normalization and final-dataset build-readiness
audit. That audit must reconcile the immutable raw CME artifact hashes, Sierra export
hashes, acquisition coverage, calendar versions, exact split intervals, and current
builder API without changing private evidence or running a build. It must produce an
exact separately authorized scope before any normalization or dataset construction.

Final 2024-2025 dataset construction, feature/label execution, training, OOS
inspection, integration, paper trading, and live execution remain blocked until their
own later gates are satisfied.
