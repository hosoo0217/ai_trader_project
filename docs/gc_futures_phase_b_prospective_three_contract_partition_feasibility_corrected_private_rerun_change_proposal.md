# GC Futures Phase B Corrected Three-Contract Feasibility Private-Rerun Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-CORRECTED-PRIVATE-RERUN-PROPOSAL-V2`.
- Classification: documentation-only, bounded, fail-closed correction proposal.
- Decision: `READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_EXPLICIT_V2_PRIVATE_RERUN_AUTHORIZATION`.
- Training readiness: `NOT_READY`.
- Current task scope: this one proposal file only.

This record preserves the completed V1 private result as immutable `INVALID`
evidence and specifies one correction to the ephemeral private runner. It does
not change the public dataset builder, raw sources, calendar evidence, search
policy, pass gate, or training decision. It does not authorize the corrected
private rerun, dataset promotion, feature or label construction, model fitting,
OOS access, integration, trading, or remote publication.

## 2. Objective and non-objective

The objective is to make a future V2 private feasibility rerun answer the
already-approved three-contract question using structurally parsed Sierra Chart
dates instead of an invalid raw-byte lexical date comparison.

The objective is not to convert the V1 `INVALID` result into `PASS`, tune the
search, add a contract, repair source rows, weaken validation, select a setup,
or train an AI. The V2 result may legitimately be `INVALID`, `AMBIGUOUS`,
`UNKNOWN`, `PASS`, or `NONE`. Only the evidence produced by a separately
authorized V2 run may establish that result.

## 3. Controlling baseline and dependency hashes

The immutable repository baseline for this correction is commit
`dc0490b9bbcc1a73801317780345d60b135b04b9`. Its parent is
`d20b586ad1574df9a84581b5284dee24d9123ce6`, and its subject is
`docs: propose prospective three-contract feasibility`.

| Dependency | SHA-256 |
|---|---|
| Original V1 proposal | `531798D43DE6112EB1D743865A8E6BA24EEF794DC29CA09FA9E96811B5606DD9` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_v3_failure_decision.md` | `853E8A472C5EEEBC131411999DE1AF05D059C15D7943F98CB309B8EE9228DD91` |
| `docs/gc_futures_phase_b_next_hypothesis_selection_decision.md` | `889CB2DA4FB107AC05A6D9B2395A9FB7E03595C40162339000731B5BAE113AC7` |
| `docs/gc_futures_ai_strategy_training_decision.md` | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| `docs/gc_futures_split_session_calendar_checkpoint.md` | `730332BD2CE71BA9E6FEB2DD29F9100CD6125300E3563B700734CEE3F2BC6087` |

Any baseline, proposal, builder, public API, or dependency drift is a STOP and
requires a new reviewed record.

## 4. Immutable V1 failure evidence

The completed V1 root is permanently preserved at:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v1/`

It contains exactly:

| File | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 5,867 | `5F5470A64DF8405DD81595FEF284E6598D748D38A1B79DFC62DBC3BD942CAC48` |
| `feasibility_result.json` | 333 | `AB4C62328D5AE97A6F9B3FBD1C98ACE9383B97381642E5BE8D7CDE6DE35BD875` |
| `input_binding.json` | 1,294 | `343EE0F94C055BF4EAEE3D50B242529DF74081E0752AEE356CD25A427971A5DC` |
| `scope_audit.json` | 566 | `6527E90A9A01931FA262E9E9F6E920CF4F97D261C8D7A203B374CD4F5B17469B` |
| `two_run_reproducibility.json` | 601 | `BCC03DB03675F892438C390CF317F200BC43EE6178EAE00C86FEB8711DCBC433` |

V1 is deterministic: two fresh reconstructions were object-, identity-,
ordered-record-, and byte-equal. Its final status is `INVALID`, selected
candidate is null, training readiness is `NOT_READY`, OOS contact is zero, and
feature/label/model/training/integration contact is zero. These facts must never
be overwritten, deleted, merged with V2, relabeled, or promoted.

## 5. Exact V1 failure classification

V1 `input_binding.json` contains a calendar with `99` entries but an exact empty
`sources` tuple. The builder correctly rejected the resulting supplied calendar
evidence as `UNREQUESTED_CALENDAR_ENTRY`; it did not leak an exception or
promote a dataset.

The empty source tuple was created before the builder call by an ephemeral
runner defect: it compared the first ten raw bytes of Sierra dates such as
`2025-8-27` lexically with zero-padded bounds such as `2025-12-31`. The source
files use valid unpadded one- or two-digit month/day text. Lexical byte order is
not chronological date order for that representation, so all five accepted
sources were incorrectly excluded.

This is a private harness boundary defect. It is not evidence that the raw
sources, calendar, or public builder failed the three-contract feasibility
question. It also does not imply that feasibility will pass after correction.

## 6. Exact current scope and global freeze

This documentation task may create only:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_corrected_private_rerun_change_proposal.md`

It must not modify source, tests, private data, manifests, fixtures, calendar
artifacts, package exports, configuration, engines, models, integration, or
training outputs. The three pre-existing unrelated untracked documentation
files remain outside scope and untouched. The global freeze remains active
everywhere else.

## 7. Immutable raw acquisition set

A separately authorized V2 run may read only the following canonical full
exports plus the immutable intake manifest:

| Contract | Canonical file | Rows | Observed JST range | SHA-256 |
|---|---|---:|---|---|
| GCZ25 | `GCZ25_COMEX_5m_186d_export_20260803.txt` | 29,100 | `2025-06-30 07:00` through `2025-12-29 23:30` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` |
| GCG26 | `GCG26_COMEX_5m_186d_export_20260803.txt` | 26,431 | `2025-08-27 09:45` through `2026-02-25 20:40` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| GCJ26 | `GCJ26_COMEX_5m_186d_export_20260803.txt` | 25,470 | `2025-10-27 09:00` through `2026-04-28 14:00` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| GCM26 | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | 27,369 | `2025-12-29 08:00` through `2026-06-25 22:30` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| GCQ26 | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | 27,528 | `2026-02-02 08:00` through `2026-08-04 01:15` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |

The intake manifest SHA-256 is
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
Superseded exports, spot, CFD, option, micro, continuous, synthetic, manually
edited, screenshot-derived, and LLM-derived data are forbidden.

## 8. Frozen OOS and no-look-ahead boundary

The frozen `GCQ26_COMEX_5m_30d_export_20260803.txt` snapshot has SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.
Only its expected name and already-recorded hash may be compared. Its contents
must never be opened, read, parsed, summarized, charted, copied, or contacted.

For the five canonical full sources, complete-file hashing may read raw bytes
solely to reconcile the accepted source identity. Feasibility parsing is a
separate bounded stream. The structural first-field date is only a coarse JST
stream boundary; it is not a trade date. Raw dates `2025-12-17` through
`2026-05-23` inclusive may reach the existing full row parser because the New
York trade date `2026-05-22` can extend into JST `2026-05-23`. The existing aware
timestamp/session conversion must then exclude every row whose normalized New
York trade date is after `2026-05-22` before builder input, candidate
calculation, or diagnostics. The first row whose structural raw date is after
`2026-05-23` may be used only to stop streaming; none of its remaining fields
may be parsed or retained.

## 9. Calendar evidence and unchanged uncertainty rule

Calendar semantics remain bound to `America/New_York`, runtime tzdata `2026.2`,
the standard prior-calendar-day `18:00` inclusive through trade-date `17:00`
exclusive session, and maintenance `[17:00,18:00)`.

Accepted evidence hashes are:

- New Year's workbook: `ED300BF142C47C83A9FCCB7D8EFC8FFC18527D8DFD059D210279A604E87A7B2F`;
- MLK workbook: `8013F1A02B5096C69EF195B5678E1789C89B37ABAB91184CC3A4F525F508EDD0`;
- President's Day workbook: `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`;
- Good Friday workbook: `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`;
- final CME GCC case `04687271` EML: `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

An exceptional session that cannot be proved exactly remains `UNKNOWN`; the V2
date correction cannot replace missing calendar evidence with a standard day.

## 10. Sole authorized correction

The future V2 runner must parse the exact first CSV date field structurally:

1. decode the field as strict ASCII;
2. split on exactly two `-` characters into `year`, `month`, and `day`;
3. require every component to be non-empty ASCII decimal digits;
4. require four year digits and one or two month/day digits;
5. construct `datetime.date(int(year), int(month), int(day))`;
6. reject impossible dates, signs, whitespace, suffixes, extra delimiters, and
   non-ASCII bytes; and
7. compare the resulting `date` object with date-object bounds.

Both `2025-8-27` and `2025-08-27` are valid equivalent representations. Their
raw text is never used as a chronological ordering key. Malformed date evidence
is `INVALID`, not silently skipped.

## 11. Bounded source-stream algorithm

For each exact source in canonical delivery order, the future runner must:

- reconcile name, full-file SHA-256, bytes, row count, and accepted observed
  range before candidate evaluation;
- preserve the header and process data rows in source order;
- structurally parse only the first date field to test the coarse JST interval
  `2025-12-17..2026-05-23` inclusive;
- reject decreasing source dates, malformed rows, duplicates, or identity drift;
- pass each row inside that coarse interval to the unchanged full parser, then
  retain it only if its normalized New York trade date is no later than
  `2026-05-22` and it is otherwise required by the builder;
- stop at the first structural raw date strictly after `2026-05-23`; and
- never alter, sort, fill, deduplicate, repair, or rewrite source bytes.

The bounded derivative is temporary private input only. It must be non-empty
for every source whose accepted observed range intersects the interval. Before
the builder call, the input binding must contain exactly the five canonical
source identities in GCZ25, GCG26, GCJ26, GCM26, GCQ26 delivery order.

## 12. Exact unchanged feasibility question

The V2 run asks exactly the V1 question:

> Does one deterministic configuration exist, using only the locked evidence,
> that yields a `VALID` public builder result ending `2026-05-22`, contains at
> least three canonical delivery-contract segment values, and gives every
> counted contract at least ten complete eligible trade dates without OOS
> contact?

Search warm-up begins `2025-12-17`. Candidate initial dates remain exactly
`2025-12-22` through `2026-01-30` inclusive. Every result ends exactly
`2026-05-22`. No observed V1 or V2 outcome may change these bounds.

## 13. Exact public builder and configuration boundary

No public code or API change is authorized. The only dataset call remains:

```python
build_gc_futures_dataset(
    *,
    exports,
    coverage_evidence,
    calendar_entries,
    config,
)
```

Builder version remains `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. The frozen
`GCDatasetBuildConfig` fields remain `instrument`, `timeframe`,
`source_timezone`, `exchange_timezone`, `timezone_data_version`, `tick_size`,
`initial_contract`, `initial_trade_date`, `roll_confirmation_sessions`,
`oos_start_trade_date`, and `oos_end_trade_date`. Signature, field, constant,
identity, or version drift is a STOP.

## 14. Candidate enumeration and selection

Candidate configurations remain ordered by increasing `initial_trade_date`,
then canonical delivery order. Allowed initial contracts remain exactly
`GCG26-COMEX` and, only when public-builder predecessor semantics prove it,
`GCZ25-COMEX`.

All candidates at the earliest date having a valid candidate are evaluated.
Exactly one byte-distinct valid configuration is selected. Multiple
byte-distinct valid configurations at that earliest date are `AMBIGUOUS`.
Later dates are diagnostic only and cannot replace the earliest date based on
segment count, coverage, prices, outcomes, or setup results.

## 15. Roll, segment, and coverage invariants

Roll policy remains `PRIOR_SESSION_VOLUME_DOMINANCE_3`:

- completed prior-session integer volume only;
- adjacent delivery contracts only;
- strict successor dominance for three consecutive eligible sessions;
- non-dominance resets the streak; closed dates neither increment nor reset;
- effective roll on the next eligible session only;
- monotonic, adjacent, non-reversing, unadjusted rolls; and
- no bar, session, segment, identity, feature, or label crosses a roll.

Every counted contract must own at least ten complete eligible emitted trade
dates. Missing predecessor or calendar proof remains `UNKNOWN`, never inferred.

## 16. Exact status and PASS contract

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`

`PASS` requires one exact public-builder `VALID` configuration, at least three
distinct monotonic canonical segment contracts, at least ten complete eligible
dates per counted contract, fully reconciled source/calendar/coverage/roll and
identity evidence, byte-equal two-run reconstruction, and zero OOS,
post-cutoff-calculation, feature, label, outcome, PnL, model, training,
integration, execution, or trading contact.

Malformed input, impossible date, identity mismatch, or exception leakage is
`INVALID`. Multiple distinct earliest valid configurations are `AMBIGUOUS`.
Blocked proof is `UNKNOWN`. No valid configuration is `NONE`. V1's status has no
precedence effect on V2; it remains separate immutable evidence.

## 17. Exact V2 private output roots

A separately authorized V2 run must use exactly:

- run A temporary root:
  `private_data/sierra_chart/.tmp-gc_phase_b_three_contract_partition_feasibility_v2-run-a/`;
- run B temporary root:
  `private_data/sierra_chart/.tmp-gc_phase_b_three_contract_partition_feasibility_v2-run-b/`;
- final root:
  `private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v2/`.

All three paths must be absent before execution. The final root may contain only:

- `input_binding.json`;
- `candidate_configurations.jsonl`;
- `feasibility_result.json`;
- `scope_audit.json`; and
- `two_run_reproducibility.json`.

No canonical bars, bounded source copies, features, labels, candidates, model
inputs, outcomes, PnL, charts, screenshots, logs, or OOS content may remain in
the final root.

## 18. V2 input-binding and correction evidence

`input_binding.json` must record the V2 schema version, this proposal identity
and SHA-256, original proposal identity and SHA-256, immutable V1 root and all
five V1 artifact hashes, builder identity, manifest identity, calendar evidence,
search bounds, cutoff, timezone values, and exact five non-empty source records.

Each source record must include canonical name, contract, full-source hash,
accepted bytes/rows/range, bounded row count, bounded first/last parsed date,
and a deterministic bounded-byte hash. It must also record the date parser rule
identifier `SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2` and prove that at least one
accepted unpadded date was interpreted chronologically rather than lexically.

No input-binding field may claim that V1 was feasible, that V2 passed, or that a
temporary derivative is a canonical acquired source.

## 19. Atomic execution and two-run reproducibility

Run A and run B must be fresh, independent reconstructions. Every input is
validated before candidate processing. Each run writes only within its exact
temporary root. Candidate failure promotes no partial dataset or partial final
artifact; strictly prior completed diagnostics remain immutable for final
reporting.

The two temporary roots must produce equal objects, identities, ordered records,
and bytes for the four core artifacts. Only after complete equality, allowed
file verification, scope audit, and hash verification may run A be atomically
renamed to the absent final V2 root. Run B must then be deleted after its exact
resolved path is verified. Any cleanup uncertainty or pre-existing path is a
STOP without overwrite.

## 20. Prefix invariance and immutable history

Strictly later complete source/calendar evidence after `2026-05-22` must not
change any V2 candidate diagnostic or result. Same-effective append, historical
insertion, source replacement, calendar repair, reorder, timezone-version
change, parser-rule change, or roll-rule mutation is not a prefix comparison
and requires a new proposal.

V1 remains byte-for-byte immutable before, during, and after V2. V2 may cite V1
but must not read it as market evidence, merge its candidates, reuse its empty
source binding, or replace its result. The repository, accepted raw evidence,
calendar evidence, and any future V2 result form separate provenance layers.

## 21. Exact 48-case future acceptance matrix

1. Exact baseline commit and all tracked dependency hashes reconcile.
2. Original V1 proposal hash and immutable five-file V1 artifact set reconcile.
3. V1 remains deterministic INVALID with null selection and NOT_READY training.
4. V1 root is never overwritten, deleted, merged, relabeled, or promoted.
5. Exact five canonical raw sources and intake manifest hash reconcile.
6. Superseded, synthetic, continuous, spot, CFD, option, and micro sources reject.
7. Frozen GCQ26 30-day OOS content is never opened or contacted.
8. Full canonical-source hashing is separated from bounded feasibility parsing.
9. First CSV date field is strict ASCII with exactly two hyphens.
10. Year is four digits and month/day are one or two digits.
11. `2025-8-27` and `2025-08-27` resolve to the same exact date.
12. Impossible dates, signs, whitespace, suffixes, and non-ASCII reject INVALID.
13. Date-object comparison replaces raw-prefix lexical comparison completely.
14. Raw source dates are nondecreasing and source row order remains immutable.
15. Coarse JST bounds are exact `2025-12-17..2026-05-23`; the first later row only stops.
16. No normalized post-`2026-05-22` row enters builder input, calculation, or diagnostics.
17. Every intersecting canonical source yields a non-empty bounded stream.
18. Builder input binding contains exactly five canonical sources in delivery order.
19. Source names, contracts, bytes, rows, ranges, and full hashes reconcile.
20. Bounded counts, first/last dates, and bounded-byte hashes are recorded.
21. Temporary bounded derivatives never become canonical acquired sources.
22. Calendar timezone and runtime tzdata `2026.2` reconcile exactly.
23. Standard, maintenance, holiday, early-close, closed, and split rules remain locked.
24. Unproved exceptional calendar evidence remains UNKNOWN, never guessed.
25. Search warm-up begins exactly `2025-12-17`.
26. Initial-date enumeration is exact `2025-12-22` through `2026-01-30`.
27. Every candidate result ends exactly `2026-05-22`.
28. Candidate order is date-first then canonical delivery order.
29. GCG26 requires exact GCZ25 predecessor and three prior eligible dominance dates.
30. GCZ25 cannot bypass its own public-builder predecessor requirement.
31. Roll uses adjacent completed-session volume and three strict confirmations.
32. Roll is next-session effective, monotonic, adjacent, and non-reversing.
33. Public builder version, keyword-only signature, config, and identities reconcile.
34. PASS has at least three distinct monotonic canonical segment contracts.
35. Every counted contract has at least ten complete eligible emitted trade dates.
36. Multiple byte-distinct earliest valid configurations are AMBIGUOUS.
37. Malformed evidence, identity mismatch, or exception leakage is INVALID.
38. Precedence is INVALID over AMBIGUOUS over UNKNOWN over PASS over NONE.
39. A failing candidate promotes no dataset, segment, or partial final result.
40. Strictly prior completed candidate diagnostics remain immutable.
41. Two fresh runs match objects, identities, order, hashes, and exact bytes.
42. Strictly later append after cutoff preserves the exact result prefix.
43. Repair, insertion, reorder, replacement, or version mutation is ineligible.
44. Output is confined to the exact absent V2 temporary/final roots.
45. Final V2 output contains exactly five allowed files and no source copies.
46. Scope audit proves zero OOS, training, feature, label, integration, and Git contact.
47. PASS authorizes only a later documentation-only partition proposal.
48. Drift, ambiguity, nondeterminism, test failure, or scope escape stops.

The logical matrix is exactly sequential `1..48`. Parameterization may expand
future test instances but cannot change this logical count without a new formal
proposal.

## 22. Independent acceptance audit requirements

Before V2 private execution, an independent read-only audit must confirm:

- exact HEAD, clean tracked state, original proposal, and dependency hashes;
- immutable V1 root, exact five files, hashes, bytes, and deterministic INVALID result;
- absence of all three reserved V2 roots;
- raw manifest/source hashes without opening frozen OOS content;
- calendar authority and unresolved-evidence UNKNOWN boundary;
- exact structural date parser rule and bounded stream behavior;
- unchanged builder/search/selection/roll/status/PASS semantics;
- exact `24` numbered sections and sequential `48` logical cases; and
- focused builder and full public regression tests pass with cache disabled.

Audit findings may be corrected only in this proposal before acceptance. An
audit, stage, or commit does not authorize V2 execution.

Documentation acceptance audit on `2026-08-19` recorded:

- exact dataset-builder focused suite: `245 passed in 0.96s` with
  `pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`;
- full canonical public regression root: `2453 passed in 23.01s` with
  `pytest -q -p no:cacheprovider tests`;
- exact `24` numbered sections and exact sequential `48`-case matrix;
- absent run-A, run-B, and final V2 reserved roots; and
- clean formatting with no tracked scope drift or private V2 execution.

A bare repository-root pytest discovery was intentionally not used as public
regression evidence because it attempted to traverse two private immutable
junctions and stopped with Windows `PermissionError`. The explicit canonical
`tests` root above completed successfully; no production or test file was
changed to bypass the private evidence boundary.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this proposal file. After
commit, rollback requires a bounded revert; history rewriting is forbidden. A
future V2 run may roll back only its exact fresh V2 temporary/final roots after
resolved-path verification. V1 and raw evidence are never rollback targets.

STOP on baseline/hash/API drift, any reserved V2 path already existing,
inability to preserve V1, malformed or decreasing dates, empty intersecting
source, missing exact five-source binding, unresolved required calendar proof,
OOS/post-cutoff calculation contact, ambiguity, nondeterminism, exception
leakage, test failure, cleanup uncertainty, output escape, source mutation,
feature/label/outcome/PnL/model/training work, integration, execution, trading,
or unapproved remote publication.

Even a V2 `PASS` promotes only a later documentation-only prospective partition
proposal. It does not promote bars, features, labels, candidates, models,
strategy logic, or trading authority.

## 24. Final decision and next single task

The V1 private result remains valid evidence of a deterministic fail-closed
harness failure and remains `INVALID`. Training remains `NOT_READY`.

After independent acceptance and publication of this record, the next single
task is an explicitly authorized exact V2 private feasibility rerun using the
structural Sierra date parser and the roots in Section 17. This document itself
authorizes no private execution, source/test change, feature/label build,
training, OOS access, integration, stage, commit, push, or trading action.
