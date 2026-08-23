# GC Futures Phase B GCG26 Required 2025 Calendar Resolution PASS Decision

## 1. Decision record

- Record ID: `GC-PHASE-B-GCG26-REQUIRED-2025-CALENDAR-RESOLUTION-PASS-V1`.
- Classification: documentation-only acceptance of a bounded private evidence-resolution run.
- Calendar-resolution decision: `PASS`.
- Feasibility decision: `UNCHANGED_UNKNOWN`.
- Training readiness: `NOT_READY`.
- Promotion authority: `PRIVATE_CALENDAR_RESOLUTION_ONLY`.
- Trading authority: `NONE`.

The exact private calendar-resolution execution is accepted as reproducible evidence.
This decision does not rerun feasibility, select a candidate, build a dataset, create
features or labels, access OOS, train a model, integrate a strategy, or authorize a
trade.

## 2. Repository and proposal binding

The execution baseline is commit
`7ad605d0f0cd0a9da242a8bbf2627b9a7b2ffa0c`, parent
`76435efec7d69c1ed2c83c9742e439cc1bd27051`, subject
`docs: propose bounded GCG26 calendar resolution`. Local `HEAD` and
`origin/main` reconciled to that exact commit before this record was created.

The governing proposal is
`docs/gc_futures_phase_b_gcg26_required_2025_calendar_resolution_change_proposal.md`,
22,033 bytes, SHA-256
`0BC17667041E9D30560795B5FF49168A3BA69A039CD23D5495C0B8F87B2462C9`.
Its 24 sections and exact 48-case acceptance matrix control this decision.

## 3. Exact documentation scope and global freeze

This decision changes only:

`docs/gc_futures_phase_b_gcg26_required_2025_calendar_resolution_pass_decision.md`

No source, test, fixture, private evidence, raw acquisition record, manifest,
calendar workbook, EML, package export, configuration, model, or integration file is
modified. Three pre-existing unrelated untracked documentation files remain outside
scope and untouched. The global code freeze remains active everywhere else.

## 4. Controlling V2 UNKNOWN evidence

The controlling feasibility decision remains
`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v2_unknown_decision.md`,
15,793 bytes, SHA-256
`4D9CBC66AF764A669DA78F7F63C8F96FC647C85F4163147454A67FD4C11804D9`.
Its terminal status is unchanged:
`V2_EXECUTION_ACCEPTED_RESEARCH_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

The immutable candidate split remains:

- 27 GCZ25 candidates: `INITIAL_PREDECESSOR_COVERAGE_MISSING`;
- 6 GCG26 candidates: `UNRESOLVED_REQUIRED_2025_CALENDAR_BINDING`;
- 21 later GCG26 candidates: public-builder `CALENDAR_COVERAGE_MISSING`.

No prior result was overwritten, relabeled, rescued, or promoted.

## 5. Exact private execution root

The accepted ignored private root is:

`private_data/sierra_chart/gc_phase_b_gcg26_required_2025_calendar_resolution_v1/`

Git ignore reconciliation is provided by `.gitignore` rule `private_data/`. The final
root contains exactly five allowed artifacts. Temporary run-A and run-B roots are
absent. No raw source copy, bar, feature, label, candidate, model input, outcome, PnL,
screenshot, or log was retained in the root.

## 6. Immutable private artifact set

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `calendar_entries.jsonl` | 4,843 | 10 | `9808145FAA305FD7F4FC12ACEC6F4C3802CE7919ABF2801CAC35F0C7EBC26617` |
| `input_binding.json` | 13,619 | 1 | `21DA5F63C0BE1FD392CFB8C52B972CD6F506E96ADF1A2102B6D92442E4513CB8` |
| `resolution_result.json` | 1,422 | 1 | `9B9AE65882B497ACA05645B3FAC2D82198CA89C47BE0B03B3002F247E58E4958` |
| `scope_audit.json` | 597 | 1 | `F060DC41FD1BC08D75C052E7975DA5DEA512D939E7645C92B1C57A855BB7F362` |
| `two_run_reproducibility.json` | 602 | 1 | `1B30BEBFDEF5F5234CB38159DE7080E378AC9E53AD102F6B200AEF3B4EDBE13E` |

These artifacts are now immutable evidence. A future task may cite their exact bytes
and identities but must not edit, overwrite, merge, or move them.

## 7. Input binding and source authentication

`input_binding.json` binds the execution and controlling baselines, proposal identity
and hash, V2 artifact set, raw manifest/README/audit/draft hashes, exact ten dates,
resolver schema, timezone, tzdata version, source claim fingerprints, and all
forbidden-operation counters.

The two row-bearing sources are authenticated original CME GCC EML artifacts:

| Artifact | Bytes | SHA-256 | Use |
|---|---:|---|---|
| historical response, 2026-08-05 | 289,129 | `867CA4472E96D128AFADB0238A1F62C26C66EF97B8E456E3395788223AE0DB34` | standard hours and 2025 Christmas exception |
| final clarification, 2026-08-07 | 138,143 | `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2` | closed-date and next-business-date interpretation |

DKIM, SPF, DMARC, sender, and Message-ID checks are true for both used EMLs. The
intermediate clarification remains immutable but is not used in row binding. The four
2026 CME workbooks are bound but not used to manufacture 2025 evidence.

## 8. Exact bounded date tuple

The accepted ordered trade-date tuple is exactly:

`2025-12-17`, `2025-12-18`, `2025-12-19`, `2025-12-22`, `2025-12-23`,
`2025-12-24`, `2025-12-25`, `2025-12-26`, `2025-12-29`, `2025-12-30`.

It contains ten unique weekday trade dates with no gap requiring a separate weekend
row. No date before `2025-12-17` or after `2025-12-30` was emitted. Trade date
`2025-12-31` remains supplied by the separately accepted 2026 calendar binding.

## 9. Timezone and session normalization

All conversions use IANA `America/New_York` and runtime tzdata version `2026.2`.
Standard sessions normalize from prior-calendar-day `18:00 ET` inclusive through
trade-date `17:00 ET` exclusive. The maintenance interval remains `[17:00,18:00)`.
No fixed-offset conversion was used.

For the December 2025 dates in scope, ET is UTC-5. Standard opens therefore normalize
to `23:00Z`, standard closes to `22:00Z`, and the Christmas Eve `13:45 ET` close to
`18:45Z`. Every emitted non-closed interval has start strictly before end and the
ordered interval set is nonoverlapping.

## 10. Standard-session rows

The eight standard `OPEN` rows are trade dates `17`, `18`, `19`, `22`, `23`, `26`,
`29`, and `30` December 2025. Their exact prior-day `23:00Z` opens and trade-date
`22:00Z` closes reconcile with the authoritative standard operating-hours claim.

Each standard row has the exact required field set, aware canonical timestamps,
nonempty paired source ID/hash tuples, and the common deterministic calendar version.
No row is inferred from bar presence or absence from a holiday list.

## 11. Christmas exception rows

Trade date `2025-12-24` is `EARLY_CLOSE`, opening
`2025-12-23T23:00:00.000000Z` and closing
`2025-12-24T18:45:00.000000Z`.

Trade date `2025-12-25` is `SESSION_CLOSED` and correctly has null open and close
timestamps. The `2025-12-25 18:00 ET` reopen is assigned to the next eligible business
trade date `2025-12-26`, normalized to `2025-12-25T23:00:00.000000Z`. Both the
historical response and final clarification are bound to the closed/reopen rows.

## 12. Deterministic identity result

The accepted calendar identity is:

`56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`

The accepted version is:

`GC-GCG26-REQUIRED-2025-CALENDAR-V1-56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`

All ten ordered row IDs are recorded in `resolution_result.json`. Date, status,
boundary, source ID/hash order, timezone, tzdata, proposal, or schema drift changes
identity. Hash lexical order is not used as a chronology tie-break.

## 13. Exact terminal result

`resolution_result.json` reports:

- `status: PASS`;
- `row_count: 10`;
- reasons `EXACT_TEN_ROW_CALENDAR_RESOLVED` and
  `AUTHORITATIVE_CME_EVIDENCE_RECONCILED`;
- no blocking reasons;
- `feasibility_status: UNCHANGED_UNKNOWN`;
- `training_readiness: NOT_READY`;
- `promotion_authority: PRIVATE_CALENDAR_RESOLUTION_ONLY`;
- `trading_authority: NONE`.

This is the only permitted interpretation of the result.

## 14. Two-run reproducibility

Run A and run B were independent fresh reconstructions. The four core artifacts
`input_binding.json`, `calendar_entries.jsonl`, `resolution_result.json`, and
`scope_audit.json` are object-equal, identity-equal, ordered-record-equal, and
byte-equal. `fresh_reconstruction_count` is exactly `2`.

The reproducibility record binds the exact four core artifact hashes shown in Section
6; atomic promotion occurred only after equality and scope checks passed.

## 15. Scope-audit result

`scope_audit.json` reports `PASS`, exactly ten resolved rows, zero unexpected output,
zero raw-source copies, and an ignored-private-output requirement of true.

Every forbidden counter is zero: candidate rescue, dataset build, feature build,
label build, training, OOS access, network access, price-bar access, integration
contact, and trading authority. The output set is therefore calendar-resolution-only.

## 16. Immutable prior-evidence preservation

All five V2 private artifacts retain their exact accepted bytes and hashes. The V2
candidate result remains 54 `UNKNOWN`, selected candidate remains null, training
readiness remains `NOT_READY`, and promotion remains `NONE`.

The 27 GCZ25 predecessor outcomes remain unresolved and outside this calendar task.
No GCV25 source was added, no predecessor was substituted, and no roll or candidate
rule changed. The resolution cannot retroactively mutate any V2 result.

## 17. Why the calendar PASS is materially useful

The bounded GCG26 export used by V2 spans parsed dates `2025-12-17` through
`2026-02-25`. Its accepted 2026 calendar contains 99 rows beginning with the
New-Year boundary. The new ten-row tuple supplies the previously absent 2025 segment
from `2025-12-17` through `2025-12-30`.

The public dataset builder validates calendar membership for merged source rows before
applying `initial_trade_date`; therefore the same missing 2025 segment caused both
the six explicit pre-check UNKNOWN outcomes and the 21 later public-builder
`CALENDAR_COVERAGE_MISSING` outcomes. The deterministic union of the ten-row calendar
with the immutable 99-row 2026 calendar is thus a justified input to a separately
authorized corrected feasibility rerun. This is a code-and-evidence inference, not a
claim that the rerun will PASS.

## 18. What remains unresolved

Calendar resolution does not answer whether any GCG26 candidate has complete
predecessor, roll, coverage, volume, or builder evidence. A corrected rerun may expose
a different `UNKNOWN`, `INVALID`, `AMBIGUOUS`, or `NONE` condition after the calendar
blocker is removed.

The independent GCZ25 predecessor question remains unresolved for all 27 GCZ25
candidates. No configuration is selected, no dataset is promoted, and no statistical
edge has been established.

## 19. Status precedence and fail-closed meaning

The accepted resolver precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

No malformed or contradictory evidence was found. Complete exact source-to-row proof,
two-run equality, and clean scope produced `PASS`. Any future hash drift, missing
source, contradictory interpretation, timezone/version mismatch, row mutation, or
output expansion invalidates reuse of this acceptance record.

## 20. Prefix invariance and anti-rescue boundary

Strictly later authoritative evidence after `2025-12-30` cannot change the accepted
ten-row tuple. Same-date repair, historical insertion, source replacement, reorder,
timezone/tzdata mutation, or evidence revision is not an eligible prefix append and
requires a new proposal and identities.

The calendar result may not be used to alter candidate dates, source order,
hypothesis, builder behavior, roll confirmation, partition boundaries, or status
precedence. A corrected rerun must report its actual result without rescue.

## 21. Exact next-task boundary

The next single task is documentation-only creation and review of:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v3_merged_calendar_rerun_change_proposal.md`

That future proposal must bind the immutable V2 five-source evidence, the accepted
99-row 2026 calendar, this exact ten-row calendar, their deterministic nonoverlapping
union and identities, the unchanged candidate matrix/hypothesis/roll rule, fresh
two-run private roots, and fail-closed status semantics. It must explicitly preserve
the 27 GCZ25 predecessor UNKNOWN outcomes and forbid OOS, training, features, labels,
integration, and trading.

## 22. Exact 48-case acceptance reconciliation

1. Execution baseline commit, parent, subject, and local remote-tracking ref reconcile.
2. Governing proposal bytes, hash, 24 sections, and 48 cases reconcile.
3. Controlling V2 UNKNOWN decision bytes and hash reconcile.
4. Exact five-file V2 private artifact set remains byte-identical.
5. Exact private final root is ignored and contains only five allowed files.
6. Temporary run-A and run-B roots are absent after atomic promotion.
7. `input_binding.json` binds both baselines and the proposal identity/hash.
8. Raw manifest, README, audit, and header-only draft hashes reconcile.
9. Both used EML artifacts reconcile by path, bytes, SHA-256, and authentication.
10. Intermediate clarification remains unused without being mutated or deleted.
11. Four 2026 workbooks remain bound but do not manufacture 2025 rows.
12. Exact ordered required-date tuple contains ten unique weekdays.
13. No date outside `2025-12-17..2025-12-30` is emitted.
14. Weekend dates are not separate trade-date rows.
15. `America/New_York` and runtime tzdata `2026.2` reconcile.
16. No fixed-offset conversion is present.
17. Standard open is prior-calendar-day 18:00 ET inclusive.
18. Standard close is trade-date 17:00 ET exclusive.
19. Eight exact standard OPEN rows reconcile independently.
20. Christmas Eve is EARLY_CLOSE at exact 13:45 ET.
21. Christmas Day is SESSION_CLOSED with null boundaries.
22. December 25 18:00 ET reopen binds to trade date December 26.
23. Every open interval has start strictly before end.
24. The complete ordered interval set is nonoverlapping.
25. Every row has the exact required field set and no hidden default.
26. Source artifact ID/hash tuples are paired, unique, nonempty, and ordered.
27. Exact ten row IDs and one calendar identity reconcile.
28. Calendar version embeds the exact accepted identity.
29. Resolution status is PASS with exactly two accepted reason tokens.
30. Blocking-reason tuple is empty.
31. Feasibility remains UNCHANGED_UNKNOWN.
32. Training readiness remains NOT_READY and trading authority NONE.
33. Run A and run B are fresh independent reconstructions.
34. Four core artifacts are object-, identity-, order-, and byte-equal.
35. Reproducibility record binds the exact four core hashes.
36. Scope audit is PASS with ten rows and zero unexpected outputs.
37. All ten forbidden-operation counters are zero.
38. No raw source, bar, feature, label, model, outcome, PnL, screenshot, or log is copied.
39. All 54 V2 candidates remain UNKNOWN with no selected configuration.
40. All 27 GCZ25 predecessor UNKNOWN outcomes remain untouched.
41. The ten-row tuple covers the exact missing 2025 portion of the GCG26 source.
42. Builder calendar validation before initial boundary explains the 6/21 shared blocker.
43. Calendar PASS is not relabeled as feasibility or dataset PASS.
44. Strictly later evidence preserves the exact bounded prefix.
45. Historical repair, reorder, replacement, or version mutation requires a new proposal.
46. The next task is one documentation-only merged-calendar rerun proposal.
47. Current source, tests, private evidence, OOS, training, and integration remain untouched.
48. Exact one-file documentation scope, regressions, rollback, promotion, and STOP rules reconcile.

## 23. Regression, promotion, rollback, and STOP conditions

Independent structural review must reconcile all 24 sections, all 48 sequential cases,
the five private artifact hashes, ten JSONL rows, deterministic identity, status,
two-run equality, scope audit, ignored-root boundary, and exact one-file Git diff.

Regression evidence for this documentation-only decision is recorded after execution:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 2.51s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 23.30s
```

Local promotion requires exact-path staging, full cached-content review, cached
`diff --check`, artifact SHA-256 audit, commit preflight, and a one-file local commit.
A push requires a separate explicit authorization. Rollback uses a bounded revert of
the future documentation commit, never history rewriting.

STOP on any baseline, proposal, V2, private-artifact, raw-source, identity, timezone,
date, ordering, test, Git-scope, or status drift; on any non-ignored private output;
or on any attempt to rerun feasibility, access OOS, build features/labels, train,
integrate, or trade without a separately accepted proposal and explicit authority.

## 24. Final bounded decision

The exact GCG26-required 2025 calendar-resolution execution is accepted as `PASS`.
It resolved one authoritative evidence question reproducibly and without scope
expansion. The controlling feasibility result remains `UNKNOWN`; no candidate is
selected and training remains prohibited.

After this one-file decision is independently audited and locally committed, work
must stop before push. The only recommended next task is the documentation-only
merged-calendar feasibility V3 rerun proposal named in Section 21. No private rerun,
dataset promotion, feature/label build, training, OOS access, integration, paper
trading, or live trading is authorized by this record.
