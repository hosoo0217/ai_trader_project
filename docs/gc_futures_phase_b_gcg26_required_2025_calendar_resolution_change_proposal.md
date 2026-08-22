# GC Futures Phase B GCG26 Required 2025 Calendar Evidence-Resolution Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-B-GCG26-REQUIRED-2025-CALENDAR-RESOLUTION-PROPOSAL-V1`.
- Classification: documentation-only, bounded, fail-closed evidence-resolution proposal.
- Decision: `READY_FOR_DOCUMENTATION_ACCEPTANCE_ONLY`.
- Training readiness: `NOT_READY`.
- Current task scope: this one proposal file only.

This record defines one minimum evidence-resolution question raised by the accepted
three-contract feasibility V2 `UNKNOWN` decision. It does not normalize calendar
evidence, execute a private run, rebuild feasibility evidence, select a configuration,
construct features or labels, inspect OOS data, train a model, integrate a strategy, or
authorize trading.

## 2. Controlling baseline and terminal evidence

The immutable repository baseline is commit
`76435efec7d69c1ed2c83c9742e439cc1bd27051`, with parent
`3f296840b3463161b05c1556d50cc768c29c28dd` and subject
`docs: record prospective three-contract feasibility V2 UNKNOWN`.

The controlling decision document is
`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v2_unknown_decision.md`,
SHA-256
`4D9CBC66AF764A669DA78F7F63C8F96FC647C85F4163147454A67FD4C11804D9`.
Its exact final decision remains
`V2_EXECUTION_ACCEPTED_RESEARCH_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

Any baseline, decision-document, builder, calendar-contract, or immutable evidence
hash drift is a STOP requiring a new reviewed proposal.

## 3. Exact current scope and global freeze

This task may create only:

`docs/gc_futures_phase_b_gcg26_required_2025_calendar_resolution_change_proposal.md`

It must not modify source, tests, fixtures, private evidence, manifests, calendar
workbooks, EMLs, normalization drafts, package exports, configuration, engines,
integration, models, or training artifacts. The three pre-existing unrelated
untracked documentation files remain outside scope and untouched. The global code
freeze remains active everywhere else.

## 4. Exact minimum-resolution question

The sole future question is:

> Can immutable, authoritative, already-acquired CME evidence be normalized into the
> exact canonical calendar entries required for the GCG26 portion of the accepted V2
> feasibility window from trade date `2025-12-17` through `2025-12-30`, without
> changing the candidate hypothesis, dates, source order, roll rule, builder, or
> status semantics?

This proposal does not presume the answer is PASS. A separately authorized private
resolution may end `INVALID`, `AMBIGUOUS`, `UNKNOWN`, `PASS`, or `NONE` under the
locked precedence below.

## 5. Explicitly excluded predecessor question

The independent GCZ25 predecessor question is not part of this proposal. The existing
canonical GCV25 diagnostic export ends at observed JST `2025-10-29 00:00`, while the
accepted GCZ25 candidates begin `2025-12-22` through `2026-01-30` and require the
three eligible completed sessions immediately preceding each initial trade date.
Therefore that file cannot establish the required predecessor window.

This proposal must not add GCV25 to the five-source feasibility binding, substitute a
different predecessor, alter `_previous_contract()`, move candidate dates, or claim
that the 27 GCZ25 `INITIAL_PREDECESSOR_COVERAGE_MISSING` outcomes have been resolved.
Those outcomes remain immutable `UNKNOWN` evidence.

## 6. Immutable V2 private evidence

The accepted private evidence root remains:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v2/`

| File | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 3,101,510 | `A2CF163A1ADF681B261B13C4CC194E1A18F03FBB6F533E237DC1696DE9288B5C` |
| `feasibility_result.json` | 333 | `B8C26C77E1F3DFC3E47161AB924A4B330E19A171DCE1F903E6993A746B46D368` |
| `input_binding.json` | 6,069 | `E9165216B809BBA0D65010E7927382C62EEADEFF5187198250B593C55D63F03E` |
| `scope_audit.json` | 566 | `3995384742BBD15352D8715D1A5F663FE6A8E04B3775723E4D7A14A9F868B3C5` |
| `two_run_reproducibility.json` | 601 | `2073D81045FCAE4F1F8E2513AFCA695709BCB7BEF43BFE706EB9FD44EFCB5A73` |

All five artifacts remain byte-for-byte immutable. A later resolution may cite but
must not edit, overwrite, merge, relabel, or promote them.

## 7. Exact V2 unresolved evidence split

The 54 ordered V2 configurations ended `UNKNOWN`, selected configuration `null`, and
training readiness `NOT_READY`:

- 27 GCZ25 configurations: `INITIAL_PREDECESSOR_COVERAGE_MISSING`;
- 6 GCG26 configurations dated `2025-12-22`, `2025-12-23`, `2025-12-24`,
  `2025-12-26`, `2025-12-29`, and `2025-12-30`:
  `UNRESOLVED_REQUIRED_2025_CALENDAR_BINDING`;
- 21 later GCG26 configurations: `CALENDAR_COVERAGE_MISSING` in the unchanged public
  builder after the available 2026 calendar binding was supplied.

This proposal addresses only the second bullet's bounded source calendar prerequisite.
It does not promise that resolving it will change any candidate or final status.

## 8. Immutable authoritative calendar sources

The future resolution may read only these accepted raw artifacts:

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| CME GCC historical GC schedule response, case `04687271`, `2026-08-05` | 289,129 | `867CA4472E96D128AFADB0238A1F62C26C66EF97B8E456E3395788223AE0DB34` |
| CME GCC clarification response, case `04687271`, `2026-08-06` | 128,570 | `DC21CA057A0CACEC3EE1455221455A160C78A37F16234BBA7CDD0B4FAF8C5FA1` |
| CME GCC final clarification response, case `04687271`, `2026-08-07` | 138,143 | `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2` |
| `Trading-Hours-Holiday.xlsx` | 11,000 | `ED300BF142C47C83A9FCCB7D8EFC8FFC18527D8DFD059D210279A604E87A7B2F` |
| `Trading-Hours-Holiday (1).xlsx` | 10,956 | `8013F1A02B5096C69EF195B5678E1789C89B37ABAB91184CC3A4F525F508EDD0` |
| `Trading-Hours-Holiday (2).xlsx` | 10,956 | `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11` |
| `Trading-Hours-Holiday (3).xlsx` | 11,022 | `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7` |

The raw artifact manifest SHA-256 is
`684F9EAAEAB41BFC4D09C4E4FE7E4B7672D5B246A3F9F251656A8D07068A0575`.
The intake README SHA-256 is
`BA537533C46E082144973FC50D2385DB5F3E374B352848BB1F650EEEF1312721`.
No webpage screenshot, observed price gap, LLM statement, inferred schedule, or
unmanifested file may replace authoritative evidence.

## 9. Prior normalization STOP remains immutable

The prior source-to-row normalization audit remains
`FAIL_CLOSED_STOP_FULL_NORMALIZATION`, with SHA-256
`4BE171CA54A647EAE3DF6BD358F63319AD13AC8E17F66FC3EE0288EB3869E6AF`.
Its header-only `normalization_draft.csv` remains 138 bytes with SHA-256
`A68372E7D556C665F66F0C90700F15BC1AD248A05D23247F27B3F2DF15314884`.

That audit rejected full `2024-10-21..2026-08-04` normalization because multiple
exceptional trade-date bindings and 2026 internal-testing weekend events were not
fully resolved. This proposal neither reverses that decision nor broadens this task to
full-calendar normalization. It asks only the narrower GCG26 2025 bounded question.

## 10. Exact bounded trade-date set

The future resolution may emit or classify only these weekday trade dates:

`2025-12-17`, `2025-12-18`, `2025-12-19`, `2025-12-22`, `2025-12-23`,
`2025-12-24`, `2025-12-25`, `2025-12-26`, `2025-12-29`, `2025-12-30`.

Weekend calendar dates are not separate trade-date rows. Trade date `2025-12-31` is
outside this resolution because its New Year's boundary is already bound by the
accepted 2026 evidence set in V2. A date before `2025-12-17` or after `2025-12-30`,
an omitted required weekday, a duplicate, or a reordered row is `INVALID`.

## 11. Timezone, session, and interval contract

All source-local times use IANA `America/New_York` and runtime tzdata version
`2026.2`. Fixed offsets are forbidden. Every timestamp is timezone-aware and then
normalized deterministically to UTC.

The standard completed GC trade-date interval is prior-calendar-day `18:00`
inclusive through trade-date `17:00` exclusive. Daily maintenance is
`[17:00,18:00)`. A normal weekday entry uses `OPEN`; an exceptional shortened entry
uses `EARLY_CLOSE`; a no-session trade date uses `SESSION_CLOSED`. Start must precede
end, and no two emitted intervals may overlap.

If runtime tzdata version or `America/New_York` is unavailable, the result is
`INVALID`. No source-local timestamp may be converted by a manually supplied fixed
offset.

## 12. Christmas evidence boundary

The historical CME GCC response explicitly states:

- `2025-12-24` Christmas Eve: early close at `13:45 ET`;
- `2025-12-25` Christmas Day: closed and reopen `2025-12-25 18:00 ET`.

The final clarification states that no GC trading occurs after a stated closed time,
that GC reopens at `18:00 ET`, and that the reopened session belongs to the next
eligible business trade date.

The future resolver must determine from these exact bytes whether the following rows
are fully authoritative: an `EARLY_CLOSE` trade date `2025-12-24`, a
`SESSION_CLOSED` trade date `2025-12-25`, and the session beginning
`2025-12-25 18:00 ET` assigned to trade date `2025-12-26`. If exact source-to-row
binding is still not provable, it must return `UNKNOWN`; it must not infer by analogy.

## 13. Standard-date evidence boundary

For `2025-12-17`, `18`, `19`, `22`, `23`, `26`, `29`, and `30`, the historical CME
GCC response's exact standard operating-hours statement and its stated coverage
through `2025-12-30` are the only permitted schedule basis, subject to the Christmas
exception in Section 12.

The resolver must prove each date's business-day eligibility, exact interval, absence
of a conflicting exception, source coverage, and deterministic source-to-row binding.
It may not treat absence from a holiday list alone as proof, infer from bar presence,
or reuse a 2026 workbook row as 2025 evidence. Unresolved proof remains `UNKNOWN`.

## 14. Exact normalized calendar-row contract

Each resolved row has exactly:

- `calendar_version: str`;
- `trade_date: date`;
- `session_status: KillZoneSessionStatus`;
- `session_open_timestamp: datetime | None`;
- `session_close_timestamp: datetime | None`;
- `source_artifact_ids: tuple[str, ...]`;
- `source_artifact_sha256s: tuple[str, ...]`.

Rows are immutable value records. Artifact ID and SHA tuples are nonempty,
equal-length, unique paired tuples in canonical lexical artifact-ID order. SHA values
are canonical 64-hex values normalized lowercase for identity payloads. `OPEN` and
`EARLY_CLOSE` require aware open and close timestamps. `SESSION_CLOSED` forbids both.
No field is defaulted, guessed, enriched, or mutated after creation.

## 15. Calendar version and deterministic identity

The bounded output calendar version is derived from:

- resolver schema version;
- exact ordered trade-date rows;
- normalized UTC boundaries and status values;
- ordered artifact IDs and hashes;
- `America/New_York`;
- runtime tzdata `2026.2`; and
- this accepted proposal identity and SHA-256.

Equivalent aware timestamp representations that normalize to the same UTC instants
are identity-equivalent. Date order, status, boundary, evidence order or hash,
timezone, tzdata version, proposal hash, or schema version changes must change the
calendar identity. Hash lexical order is never a chronology tie-break.

## 16. Exact future private artifact set

A separately authorized resolution must use fresh temporary roots and the absent final
root:

- run A: `private_data/sierra_chart/.tmp-gc_phase_b_gcg26_required_2025_calendar_resolution_v1-run-a/`;
- run B: `private_data/sierra_chart/.tmp-gc_phase_b_gcg26_required_2025_calendar_resolution_v1-run-b/`;
- final: `private_data/sierra_chart/gc_phase_b_gcg26_required_2025_calendar_resolution_v1/`.

The final root may contain exactly:

- `input_binding.json`;
- `calendar_entries.jsonl`;
- `resolution_result.json`;
- `scope_audit.json`;
- `two_run_reproducibility.json`.

All roots must be absent before execution. No raw-source copy, price bar, feature,
label, candidate, model input, outcome, PnL, screenshot, or log may remain there.

## 17. Input binding and source authentication

`input_binding.json` must bind the repository baseline, controlling V2 decision,
immutable V2 artifact set, resolver schema, exact source path/name/bytes/SHA-256,
manifest identity, source retrieval metadata, MIME type, sender authentication where
available, bounded date set, timezone, tzdata version, and forbidden operations.

Before parsing content, every raw artifact must reconcile against its manifest record
and exact on-disk hash. A missing file, byte/hash drift, duplicate identity, ambiguous
supersession, unsupported content type, or authentication failure is `INVALID`.
Evidence may be unused when outside the minimum question, but every used claim must
cite at least one exact bound source artifact.

## 18. Deterministic resolution algorithm

The future resolver must:

1. validate all top-level inputs and hashes before row promotion;
2. decode only the exact relevant plain-text/workbook cells without modifying bytes;
3. normalize source timestamps with `America/New_York` and tzdata `2026.2`;
4. reconcile each exact required date against standard and exceptional evidence;
5. reject contradictory byte-distinct interpretations as `AMBIGUOUS`;
6. retain unresolved but nonmalformed proof as `UNKNOWN`;
7. validate the complete ordered tuple before promotion;
8. compute deterministic row and calendar identities; and
9. emit only after run-A/run-B equality and scope audit pass.

It must not silently sort, fill, repair, interpolate, deduplicate, infer from market
bars, access the network, or modify the header-only normalization draft.

## 19. Atomic processing and immutable prior evidence

Resolution is atomic by trade-date group. A determinably later malformed group returns
`INVALID` while preserving only strictly prior completed diagnostic evidence. Nothing
from the failing group or any later group may promote. An unresolved group returns
`UNKNOWN`; no row from that group or later group is promoted as canonical.

Run A and run B are fresh independent reconstructions. The four core artifacts
`input_binding.json`, `calendar_entries.jsonl`, `resolution_result.json`, and
`scope_audit.json` must be object-, identity-, ordered-record-, and byte-equal before
run A may be atomically renamed to the absent final root. Cleanup uncertainty is a
STOP without overwrite.

## 20. Status precedence and exact terminal meanings

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`

- `INVALID`: malformed, hash-drifted, impossible, unordered, overlapping, or
  exception-leaking evidence.
- `AMBIGUOUS`: two or more distinct authoritative canonical interpretations remain.
- `UNKNOWN`: required proof is missing or insufficient without malformed evidence.
- `PASS`: all ten exact dates reconcile into one complete deterministic tuple and two
  runs reproduce byte-for-byte.
- `NONE`: the authorized required-date set is empty; unreachable for this locked
  nonempty request and retained only as vocabulary completeness.

PASS is calendar-resolution evidence only. It is not feasibility PASS, configuration
selection, dataset validity, training readiness, strategy authority, or trading
authority.

## 21. Prefix invariance and anti-rescue boundary

Strictly later authoritative calendar evidence after `2025-12-30` cannot change the
bounded resolved tuple. Same-date repair, historical insertion, source replacement,
reorder, timezone/tzdata mutation, or evidence revision is not an eligible prefix
append and requires a new proposal and new identities.

The resolver must not inspect feasibility outcomes to choose evidence, weaken a rule,
or manufacture PASS. It must not change candidate dates, include GCV25, remove GCZ25,
alter source order, adjust roll confirmation, add a setup, or select a candidate. If
the minimum question cannot be resolved exactly, `UNKNOWN` remains terminal.

## 22. Exact 48-case future acceptance matrix

1. Exact baseline commit, parent, subject, and controlling decision hash reconcile.
2. Exact five-file V2 artifact set, bytes, hashes, and UNKNOWN decision reconcile.
3. Exact raw manifest, README, audit, and header-only draft hashes reconcile.
4. Historical, clarification, and final-clarification EML bytes/hashes reconcile.
5. Only manifest-bound authoritative CME evidence may support a row.
6. Screenshot, bar-gap, LLM, inferred, and unmanifested evidence reject.
7. Exact required weekday set contains ten ordered dates.
8. Date before `2025-12-17` or after `2025-12-30` rejects.
9. Missing, duplicate, or reordered required date rejects.
10. Weekend dates are never emitted as separate trade-date rows.
11. `America/New_York` and runtime tzdata `2026.2` reconcile.
12. Missing zone/version or fixed-offset conversion rejects INVALID.
13. Standard interval is prior-day 18:00 inclusive to trade-date 17:00 exclusive.
14. Maintenance interval is exactly 17:00 through 18:00 local.
15. Standard dates 17, 18, 19, 22, 23, 26, 29, and 30 are individually proved.
16. Absence from a holiday list alone is not accepted proof.
17. Christmas Eve `2025-12-24` exact 13:45 ET early close is reconciled.
18. Christmas Day `2025-12-25` exact closed status is reconciled.
19. `2025-12-25 18:00 ET` reopen is bound only to next eligible trade date 26.
20. No post-close trading is inferred for the closed date.
21. Unresolved Christmas trade-date binding returns UNKNOWN, not guessed PASS.
22. OPEN and EARLY_CLOSE require aware valid open/close timestamps.
23. SESSION_CLOSED forbids open and close timestamps.
24. Every emitted interval has start strictly before end.
25. Emitted intervals are globally nonoverlapping.
26. Exact row field names, types, and no-default contract reconcile.
27. Evidence ID/hash tuples are nonempty, equal-length, paired, unique, and ordered.
28. Malformed hash, identity drift, MIME drift, or supersession ambiguity is INVALID.
29. Equivalent normalized UTC timestamps produce the same identity.
30. Date, status, boundary, evidence, timezone, or version change changes identity.
31. Hash order is never a chronology tie-break.
32. All top-level evidence validates before row promotion.
33. Determinably later malformed evidence preserves strictly prior diagnostics only.
34. Failing or unresolved group and later groups promote no canonical rows.
35. Contradictory distinct authoritative interpretations return AMBIGUOUS.
36. Missing sufficient proof without malformed evidence returns UNKNOWN.
37. Complete ten-row deterministic evidence is required for PASS.
38. PASS cannot be relabeled as feasibility, dataset, training, or strategy PASS.
39. Fresh run A and run B use exact absent temporary roots.
40. Core artifacts are object-, identity-, order-, and byte-equal across runs.
41. Atomic promotion occurs only after equality, allowed-file, hash, and scope PASS.
42. Pre-existing output path or cleanup uncertainty stops without overwrite.
43. Strictly later post-`2025-12-30` evidence preserves the exact prefix.
44. Same-date repair, insertion, replacement, reorder, or version mutation is ineligible.
45. GCZ25/GCV25 predecessor evidence and all 27 UNKNOWN outcomes remain untouched.
46. Candidate dates, source order, hypothesis, builder, and roll rule remain unchanged.
47. OOS, private feasibility rerun, feature/label, model, training, and integration contact are zero.
48. Exact output set, Git-ignore boundary, global freeze, rollback, and STOP evidence reconcile.

## 23. Promotion, rollback, and STOP conditions

Documentation promotion requires independent semantic and structural audit, exact
24-section and 48-case reconciliation, full regression PASS, exact one-file diff,
cached-content/hash audit, commit preflight, and a local documentation commit. A push
requires a separate explicit authorization.

Current documentation acceptance evidence on `2026-08-19` is:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 0.97s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 22.16s
```

Independent read-only review also reconciled the exact baseline and V2 hashes, the
three authoritative EML hashes, manifest/README/audit/draft hashes, the immutable V2
`27/6/21` UNKNOWN split, exactly 24 numbered sections, exactly 48 sequential logical
cases, and the one-file documentation scope. These checks authorize only local
documentation promotion.

A future private resolution requires a new explicit authorization after this proposal
is published and its live remote identity is verified. It may promote its private
artifact root only when all hashes, all ten rows, status, two-run reproducibility,
allowed files, Git-ignore scope, and no-contact counters pass.

Rollback of this documentation uses a bounded revert of its future commit, never
history rewriting. Private raw and V2 evidence remain immutable. STOP immediately on
hash drift, missing authoritative evidence, contradictory interval interpretation,
timezone/version mismatch, scope expansion, OOS access, candidate rescue, builder or
hypothesis change, non-ignored private output, test failure, or any inferred training
or trading authority.

## 24. Final bounded decision and next single task

This proposal locks one minimum evidence-resolution question and nothing else: the
exact GCG26-required 2025 calendar tuple for trade dates `2025-12-17..2025-12-30`.
It deliberately preserves the GCZ25 predecessor UNKNOWN boundary and the accepted V2
terminal result.

After this one-file proposal is independently audited, locally committed, separately
authorized for push, pushed, and live-remote verified, the next single task may be the
exact private calendar-resolution run described here. Until then, and regardless of
its future result, private feasibility rerun, dataset build, feature/label build,
training, OOS access, integration, paper trading, and live trading remain prohibited.
