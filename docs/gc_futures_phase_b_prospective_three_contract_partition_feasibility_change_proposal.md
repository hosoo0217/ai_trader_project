# GC Futures Phase B Prospective Three-Contract Partition Feasibility Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-B-PROSPECTIVE-THREE-CONTRACT-PARTITION-FEASIBILITY-PROPOSAL-V1`.
- Classification: documentation-only, bounded, fail-closed change proposal.
- Decision: `READY_FOR_SEPARATE_PRIVATE_FEASIBILITY_RUN_AUTHORIZATION`.
- Training readiness: `NOT_READY`.
- Current task scope: this one proposal file only.

This record closes further setup-family exploration on the accepted two-contract
development dataset and pre-registers one prospective data/partition feasibility
question. It does not declare that a three-contract dataset is buildable. It does
not authorize a private run, dataset publication, feature or label construction,
model fitting, OOS access, integration, trading, or remote publication.

## 2. Objective and non-objective

The objective is to determine whether the immutable acquired GC source and
calendar evidence can support a deterministic, development-only dataset whose
canonical emitted segments represent at least three delivery contracts before
any training partition is designed.

The objective is not to rescue a failed setup, search for a profitable rule,
increase candidate counts, optimize dates or roll thresholds, backfill missing
evidence, or train an AI. `PASS`, `UNKNOWN`, `AMBIGUOUS`, and `INVALID` are all
admissible feasibility outcomes. Only an exact `PASS` may support a later,
separately reviewed prospective partition decision.

## 3. Controlling decisions and dependency hashes

The immutable repository baseline is commit
`d20b586ad1574df9a84581b5284dee24d9123ce6`. The following tracked dependencies
are bound by SHA-256:

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| V3 sweep/reclaim failure decision | `853E8A472C5EEEBC131411999DE1AF05D059C15D7943F98CB309B8EE9228DD91` |
| next-hypothesis selection decision | `889CB2DA4FB107AC05A6D9B2395A9FB7E03595C40162339000731B5BAE113AC7` |
| GC AI strategy and training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| split-session calendar checkpoint | `730332BD2CE71BA9E6FEB2DD29F9100CD6125300E3563B700734CEE3F2BC6087` |

The governing selection and V3 failure records prohibit another setup family on
the current dataset. The training decision requires at least three canonical
contract months plus chronological partition, purge/embargo, validation, and
sealed final OOS controls. Dependency or baseline drift is a STOP.

## 4. Accepted current evidence and closure condition

The accepted V3 development dataset is immutable:

- `17,404` development-only bars;
- `133` canonical segments;
- trade dates `2026-02-23` through `2026-05-22` inclusive;
- canonical segment contracts exactly `GCJ26-COMEX` and `GCM26-COMEX`;
- zero opened OOS bars; and
- no accepted feature table, label table, model, training artifact, or strategy.

The final selected sweep/reclaim setup produced deterministic `AMBIGUOUS` with
`54` candidates and failed its pre-registered hypothesis. That result is
preserved. Re-running, tuning, relabeling, or replacing that setup on the same
two-contract sample is forbidden.

## 5. Exact current scope and global freeze

This task may create only:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_change_proposal.md`

It must not modify source, tests, private data, manifests, fixtures, calendar
artifacts, package exports, configuration, engines, integration, models, or
training outputs. Three pre-existing unrelated untracked documentation files
remain outside scope and untouched. The global freeze remains active everywhere
else.

## 6. Immutable raw acquisition set

A later feasibility run may read only the following canonical full-contract
exports and the immutable intake manifest:

| Contract | Canonical file | Rows | Observed JST range | SHA-256 |
|---|---|---:|---|---|
| GCZ25 | `GCZ25_COMEX_5m_186d_export_20260803.txt` | 29,100 | `2025-06-30 07:00` through `2025-12-29 23:30` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` |
| GCG26 | `GCG26_COMEX_5m_186d_export_20260803.txt` | 26,431 | `2025-08-27 09:45` through `2026-02-25 20:40` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| GCJ26 | `GCJ26_COMEX_5m_186d_export_20260803.txt` | 25,470 | `2025-10-27 09:00` through `2026-04-28 14:00` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| GCM26 | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | 27,369 | `2025-12-29 08:00` through `2026-06-25 22:30` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| GCQ26 | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | 27,528 | `2026-02-02 08:00` through `2026-08-04 01:15` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |

The intake manifest SHA-256 is
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
Superseded exports, screenshots, manually edited rows, local-LLM output, spot,
CFD, option, micro, continuous, and synthetic contracts are forbidden.

## 7. Frozen OOS and evidence quarantine

The frozen `GCQ26_COMEX_5m_30d_export_20260803.txt` snapshot has SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.
Its name and hash may be compared without opening its content. No future
feasibility run may read, parse, summarize, chart, label, infer from, or otherwise
contact that snapshot.

No raw row with normalized trade date after `2026-05-22` may enter feasibility
calculations. The interval after `2026-05-22` remains quarantine/embargo; it is
not development and cannot influence an initial date, roll, threshold, coverage
gate, partition, or feasibility status.

## 8. Calendar evidence and unresolved boundary

Calendar reasoning is bound to `America/New_York`, runtime tzdata `2026.2`, the
standard prior-calendar-day `18:00` inclusive through trade-date `17:00`
exclusive session, and the maintenance interval `[17:00,18:00)`.

Accepted calendar evidence includes the official 2026 President's Day workbook
SHA-256 `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`,
the official 2026 Good Friday workbook SHA-256
`CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`,
and final CME GCC case `04687271` clarification EML SHA-256
`8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

The private normalization audit remains
`FAIL_CLOSED_STOP_FULL_NORMALIZATION`: exact production intervals and trade-date
bindings are not yet normalized for every required 2025 exception. This proposal
does not silently lift that status.

## 9. Exact feasibility question

The sole question is:

> Does one deterministic configuration exist, using only Sections 6–8 evidence,
> that yields a `VALID` public builder result ending `2026-05-22`, contains at
> least three canonical delivery-contract segment values, and gives every counted
> contract at least ten complete eligible trade dates without OOS contact?

Ten dates approximate two full trading weeks and exceed the three-session roll
confirmation horizon; they prevent a fleeting boundary fragment from being
misrepresented as meaningful contract coverage. This is a feasibility floor,
not evidence of statistical adequacy or training readiness.

## 10. Exact bounded search interval

Calendar/source warm-up begins `2025-12-17`. Candidate initial emitted trade
dates are examined from `2025-12-22` through `2026-01-30` inclusive. Every
candidate result ends `2026-05-22` inclusive.

The lower bound provides three ordinary weekday observations before the first
candidate Monday. The upper bound is before the accepted 2026 pilot warm-up and
prevents an unbounded date search. A date outside this range, a different end
date, or a post-result adjustment requires a new proposal.

## 11. Deterministic calendar eligibility

For each required date, the future run must construct an exact ordered tuple of
`KillZoneCalendarEntry` or `GCSplitSessionCalendarEntry` values accepted by the
public builder. Standard dates may use only the locked standard rule. Holidays,
early closes, closed sessions, split sessions, or non-business trade-date
assignments require exact source-backed boundaries.

If any candidate needs a 2025 exceptional date whose session intervals or trade
date cannot be proved exactly from accepted artifacts, that candidate is
`UNKNOWN`; it cannot use a guessed standard session. If every candidate is so
blocked, the final feasibility result is `UNKNOWN`, not `PASS`.

## 12. Exact public builder contract

No new public API is authorized. The only dataset call is the existing
keyword-only function:

```python
build_gc_futures_dataset(
    *,
    exports,
    coverage_evidence,
    calendar_entries,
    config,
)
```

`config` is the frozen `GCDatasetBuildConfig` with exact fields:
`instrument`, `timeframe`, `source_timezone`, `exchange_timezone`,
`timezone_data_version`, `tick_size`, `initial_contract`,
`initial_trade_date`, `roll_confirmation_sessions`, `oos_start_trade_date`, and
`oos_end_trade_date`. Builder version is
`GC-DATASET-BUILDER-V3-SPLIT-SESSION`. Signature, field, version, or identity
drift is a STOP.

## 13. Source and coverage normalization

Every candidate uses integer-tick OHLC, integer volume, closed five-minute bars,
aware timestamps, exact contract identity, strict source order, uniqueness, and
the existing acquisition coverage sidecar contract. Raw bytes are immutable.

The future run may produce bounded in-memory or temporary private derivatives
only for dates needed by the candidate. It must stream-stop at `2026-05-22`,
must never normalize a source in place, and must delete the candidate's temporary
output on failure. Source hash, byte count, row count, and observed range must
reconcile before any candidate is evaluated.

## 14. Deterministic initial-contract enumeration

Candidate configurations are enumerated by increasing
`initial_trade_date`, then canonical delivery order. The allowed initial
contracts are exactly `GCG26-COMEX` and, only if the builder requires an emitted
predecessor segment to establish the earliest valid chain, `GCZ25-COMEX`.

`GCG26-COMEX` requires exact GCZ25 predecessor evidence and three immediately
preceding eligible sessions of strict completed-session volume dominance.
`GCZ25-COMEX` may be used only when its own predecessor requirement is already
provable by the immutable builder contract; missing earlier delivery evidence
is `UNKNOWN`, never inferred. All configurations at the earliest date having a
valid candidate are evaluated. Exactly one byte-distinct valid configuration is
selected; multiple byte-distinct valid configurations at that same earliest
date are `AMBIGUOUS`. Later dates are reported but cannot replace the earliest
date based on segment counts or outcomes.

## 15. Exact roll and segment rules

Roll policy remains `PRIOR_SESSION_VOLUME_DOMINANCE_3`:

- compare only completed prior-session integer volume for adjacent delivery
  contracts;
- require strict successor dominance for three consecutive eligible sessions;
- let non-dominance reset the streak while closed dates neither increment nor
  reset it;
- make a confirmed roll effective only on the next eligible session;
- permit monotonic adjacent rolls only, never a skip, reverse, or adjustment;
- keep bars, sessions, segments, identities, features, and labels from crossing
  a roll boundary.

No observed candidate count, price outcome, or setup result may influence roll
selection.

## 16. PASS, non-PASS, and precedence

`PASS` requires all of the following:

- one exact builder configuration returns `VALID`;
- canonical segment contracts contain at least three distinct allowed delivery
  months in monotonic order;
- each counted contract owns at least ten complete eligible emitted trade dates;
- source, calendar, coverage, roll, segment, manifest, and identity evidence
  reconcile;
- two fresh reconstructions produce equal objects, identities, ordered records,
  and bytes; and
- OOS, feature, label, outcome, PnL, model, training, integration, and trading
  contact are all zero.

Final status precedence is `INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.
Multiple byte-distinct valid earliest configurations are `AMBIGUOUS`. No valid
configuration is `NONE`. Malformed evidence or identity mismatch is `INVALID`.

## 17. Prospective partition boundary

A feasibility `PASS` does not create or approve train/validation/calibration/OOS
partitions. It records only the earliest valid source/calendar/roll configuration
and its canonical contract/date coverage.

A later partition proposal must pre-register chronological training,
validation, calibration, purge, embargo, and final OOS boundaries without using
future outcomes. It must also decide whether ten dates per contract is enough
for its statistical objective. No contract, date, or row is automatically a
training sample because this feasibility gate passed.

## 18. Exact private feasibility output contract

A separately authorized private run may create one new Git-ignored output root:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v1/`

The root may contain only:

- `input_binding.json`;
- `candidate_configurations.jsonl`;
- `feasibility_result.json`;
- `scope_audit.json`; and
- `two_run_reproducibility.json`.

It may not contain canonical dataset bars, features, labels, candidates, model
inputs, outcomes, PnL, charts, or copied OOS content. Private artifacts must
never be staged, committed, pushed, emailed, or sent to any local or remote AI.

## 19. Atomic execution and immutable prior evidence

The future run must use a fresh temporary sibling directory, validate every
input before promotion, write complete deterministic artifacts, verify hashes,
and rename atomically to the exact final root only after all gates pass.

On a failing candidate, no partial configuration or dataset evidence is
promoted. Strictly prior completed candidate diagnostics remain immutable in
memory for final reporting. If the final root already exists, if temporary
cleanup cannot be proven, or if any output escapes the exact root, STOP without
overwriting anything.

## 20. Prefix invariance and no-look-ahead

Appending strictly later complete source/calendar evidence after `2026-05-22`
must not change the selected configuration or any earlier diagnostic. A
same-effective append, historical insertion, source replacement, calendar
repair, reorder, timezone-version change, or roll-rule mutation is not an
eligible prefix comparison and requires a new proposal.

Candidate evaluation uses only evidence available through each effective
moment. Future volume, later contracts, detector results, labels, OOS rows,
screenshots, and LLM judgments are forbidden from resolving an earlier choice.

## 21. Exact 48-case future acceptance matrix

1. Baseline commit and every tracked dependency hash reconcile.
2. Exact five-file raw acquisition set and manifest hash reconcile.
3. Superseded, synthetic, continuous, spot, CFD, option, and micro sources reject.
4. Frozen GCQ26 30-day OOS snapshot content is never opened.
5. No normalized trade date after `2026-05-22` enters feasibility evidence.
6. Raw source mutation, replacement, reorder, truncation, or in-place repair stops.
7. Integer-tick OHLC and integer-volume validation is exception-safe.
8. Five-minute closed-bar timestamp order and uniqueness reconcile.
9. Coverage sidecars bind exact source hash, range, acquisition, and contract.
10. America/New_York and runtime tzdata `2026.2` reconcile exactly.
11. Standard session is prior-day 18:00 inclusive through trade-date 17:00 exclusive.
12. Maintenance `[17:00,18:00)` is never eligible.
13. Holiday, early-close, closed, and split-session dates require exact evidence.
14. Unproved 2025 exception is UNKNOWN and never replaced by a standard session.
15. Calendar warm-up begins exactly `2025-12-17`.
16. Initial-date enumeration is exact `2025-12-22` through `2026-01-30`.
17. Every candidate result ends exactly `2026-05-22`.
18. Candidate enumeration is date-first then canonical delivery order.
19. GCG26 initial selection requires exact GCZ25 predecessor identity.
20. Initial selection requires three prior eligible completed-session dominance dates.
21. Missing predecessor source or calendar proof is UNKNOWN, not inferred.
22. GCZ25 cannot bypass its own builder predecessor requirement.
23. Roll comparisons use only adjacent contract completed-session volume.
24. Strict dominance must hold for three consecutive eligible sessions.
25. Non-dominance resets while closed dates neither increment nor reset.
26. Roll becomes effective only on the next eligible session.
27. Roll order is monotonic, adjacent-only, non-reversing, and unadjusted.
28. No bar, segment, feature, label, or identity crosses a roll.
29. Builder version and exact keyword-only signature reconcile.
30. GCDatasetBuildConfig exact fields and constants reconcile.
31. VALID builder output has canonical source/calendar/coverage/roll identities.
32. PASS contains at least three distinct canonical emitted contract values.
33. Every counted contract contains at least ten complete eligible trade dates.
34. A fleeting under-ten-date contract fragment cannot satisfy PASS.
35. Multiple byte-distinct earliest valid configurations are AMBIGUOUS.
36. Malformed input, identity mismatch, or exception leakage is INVALID.
37. Status precedence is INVALID over AMBIGUOUS over UNKNOWN over PASS over NONE.
38. No valid configuration is deterministic NONE and promotes no dataset.
39. Failing candidate promotes no private dataset or partial result.
40. Strictly prior completed diagnostic evidence remains immutable.
41. Two fresh runs produce equal objects, identities, order, hashes, and bytes.
42. Strictly-later append after the cutoff preserves the exact prefix result.
43. Same-effective append, repair, insertion, reorder, or version mutation is ineligible.
44. Output is confined to the exact fresh Git-ignored feasibility root.
45. Output contains no canonical bars, features, labels, outcomes, PnL, or models.
46. Frozen OOS, integration, strategy, execution, broker, and trading surfaces remain unused.
47. PASS authorizes only a later documentation-only partition proposal.
48. Hash drift, calendar ambiguity, nondeterminism, test failure, or scope drift stops.

The logical matrix is exactly sequential `1..48`. Parameterization may expand
future test instances but cannot change the logical count without a new formal
proposal.

## 22. Independent audit requirements

Before any private feasibility run, an independent read-only audit must confirm:

- exact HEAD, tracked worktree state, and dependency hashes;
- exact raw manifest and source hashes without reading frozen OOS content;
- calendar authority, normalization status, and every required exceptional date;
- public builder version, signature, config, identity, and roll semantics;
- exact search bounds, status precedence, atomic output, and two-run contract;
- exact `24` numbered sections and sequential `48` logical cases; and
- canonical public regression tests pass with pytest cache disabled.

Audit findings may be corrected only in a separately authorized exact scope.
An audit does not authorize private execution.

Documentation acceptance audit on `2026-08-19` recorded:

- exact dataset-builder focused suite: `245 passed in 2.70s` with
  `pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`;
- full canonical public regression root: `2453 passed in 23.49s` with
  `pytest -q -p no:cacheprovider tests`; and
- exact `24` numbered sections, exact sequential `48`-case matrix, clean diff
  formatting, no tracked scope drift, and no private/OOS execution.

## 23. Rollback, promotion, and STOP conditions

Before this proposal is committed, rollback is deletion of only this new file.
After commit, rollback requires a bounded revert; history rewriting is
forbidden. A later private feasibility run rolls back by deleting only its fresh
temporary/output root after verifying the resolved path is exact.

STOP on baseline or hash drift, unresolved required calendar binding, missing
predecessor coverage, public API/version drift, fewer than three meaningful
contract segments, ambiguity, nondeterminism, exception leakage, test failure,
OOS or post-cutoff contact, private-source mutation, output-scope escape,
feature/label/outcome/PnL/model/training work, integration, execution, or remote
publication without exact authorization.

Promotion from a valid future run is limited to a new documentation-only
prospective partition proposal. It does not promote a dataset, setup, candidate,
feature, label, model, strategy, or trading decision.

## 24. Final decision and next single task

The current two-contract setup-selection phase is closed. Training remains
`NOT_READY`. The next single task, after independent acceptance and publication
of this record, is the exact private feasibility run specified here.

That run must answer whether present immutable evidence can support the required
three-contract development boundary. It may legitimately stop `UNKNOWN` if the
2025 calendar or predecessor chain is incomplete. No private run, dataset build,
feature/label construction, training, OOS access, integration, stage, commit,
push, or trading action is authorized by this document itself.
