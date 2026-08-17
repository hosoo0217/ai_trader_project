# GC Futures Phase B NY-AM Sweep-Reclaim Refreshed Private-Run Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REFRESHED-PRIVATE-RUN-V3`.
- Decision date: `2026-08-17`.
- Binding repository baseline: `4f33bf4414949d7b486af550a6e5145fe1172df5`.
- Corrected implementation commit: `4f33bf4414949d7b486af550a6e5145fe1172df5`.
- Governing correction proposal: `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md`, SHA-256 `FEDBE60FFC5E984692EEDA41BAB5C131377E7578EC7E9EB56063D35B0A80883D`.
- Complete Kill-zone dependency proposal: `docs/gc_futures_phase_b_complete_kill_zone_dependency_build_change_proposal.md`, SHA-256 `4AA736C38A6170CF4F0DEF4752A02C763945B6711C212BEE4F938A973EBBD360`.
- Complete Kill-zone alignment correction proposal: `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_complete_kill_zone_alignment_correction_proposal.md`, SHA-256 `BEDB0596321A8A00D3B093E1BBF87A9A3437E4B49AF8A5978375E49246FAB772`.
- Classification: documentation-only refreshed private-run preflight contract.
- Current decision: `READY_FOR_EXACT_REFRESHED_PRIVATE_RUN_ACCEPTANCE_WORKFLOW`.

This record does not execute the private run. It supersedes the non-executable
V1 and V2 run contracts for future execution purposes without rewriting or
deleting either historical record. It grants no training, OOS, feature, label,
model, PnL, integration, runtime, execution, trading, or remote-publication
authority.

## 2. Accepted correction and dependency outcome

The observation-grain and terminal-boundary defects are corrected in committed
code. The analyzer now intersects canonical Phase B five-minute bar-open
membership with public Kill-zone fully-closed bar-close membership: normalized
opens are exactly `[07:00:00, 09:55:00) America/New_York`, corresponding to
normalized closes in `[07:05:00, 10:00:00)`. The canonical `09:55` open / `10:00`
close bar remains immutable dataset evidence but is not a Phase B observation.
The full immutable dataset remains the source of dataset, segment, trade-date,
and chronological evidence.

The previously incomplete Candidate Evidence Kill-zone prefix remains immutable
`UNKNOWN` lineage evidence and is not repaired or relabeled. A separate complete
Kill-zone dependency has been built and independently audited over all `133`
canonical segments and all `64` requested development trade dates. Its status
counts are `101 VALID` and `32 NONE`; it contains `9,839` contexts, `9,839`
snapshots, and `2,276` `NEW_YORK_AM` contexts. This removes the dependency
completeness blocker only. It does not predetermine the feasibility result.

The final committed implementation evidence is `59 passed in 6.50s` focused and
`2453 passed in 23.10s` full regression, with the unchanged exact `48` logical
cases. This proposal's cache-disabled acceptance audit independently reproduced
`59 passed in 6.50s` focused and `2453 passed in 23.01s` full regression. No
private V2 feasibility run has been executed.

## 3. Verified repository and worktree baseline

At authoring time:

- `HEAD`, local `origin/main`, and the post-push live remote `main` all equal
  `4f33bf4414949d7b486af550a6e5145fe1172df5`, with local divergence `0/0`;
- the tracked index and tracked worktree are clean;
- the corrected current source, test, and checkpoint hashes match Section 9,
  while the complete dependency file hashes and its immutable construction-time
  provenance match Section 7;
- the V1 and V2 final feasibility roots are absent;
- no sweep-reclaim private feasibility result, feature/label artifact, training,
  OOS access, model fitting, integration, PnL, or trading action exists; and
- these three pre-existing unrelated untracked documents remain outside scope
  and untouched:
  `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`,
  `docs/gc_futures_real_data_input_binding_change_proposal.md`, and
  `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Tracked baseline drift before acceptance is a hard `STOP`.

## 4. Exact documentation-only scope

The only path authorized by this documentation task is:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_refreshed_private_run_change_proposal.md`

Only this file may be corrected, independently audited, staged with its exact
path, cached-audited, and committed locally. Broad pathspecs, source/test/private
artifact writes, external fixtures, integration, and push are forbidden by this
task. Every other tracked and untracked path remains frozen.

## 5. Authority and no-trading boundary

The future private run, if separately authorized after this proposal is accepted
and published, is a development-only structural feasibility measurement. It may
read only the exact private roots in Sections 6 and 7, reconstruct committed
public dataclasses, call the committed analyzer exactly once per fresh run, and
write only the exact temporary/final roots in Sections 16 and 17.

It may not tune thresholds, select favorable dates, inspect OOS, produce features
or labels, fit or invoke a model, compute entry/exit/risk/PnL, alter a detector,
mutate input evidence, integrate runtime behavior, emit a signal, or place an
order. No local or remote language model may read raw private market rows.

## 6. Exact immutable Phase A input root

The accepted private input root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Its exact eight-file scope and immutable hashes are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | `2337` | `D0774ACB1ECBB1D99F6BCFA4532447859886925D4FB8332BAC67B522BF862B1D` |
| `candidate_evidence_DEVELOPMENT_ONLY.json` | `74660911` | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | `2802555` | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| `input_binding_DEVELOPMENT_ONLY.json` | `5179` | `E7982293EDB42CC784B85C5047D06FEC86BCDBB5992C5E847171DD78252A43E4` |
| `normalized_calendar_DEVELOPMENT_ONLY.json` | `4149` | `CCB8BC4034BBC02922278F560BF1AFAC8282A05D3B26611A7EECF6202686F5FC` |
| `README_DEVELOPMENT_ONLY.md` | `344` | `7260B5DE117EB845758CC908DF5B40AC553AC9F6BBF7535F57A5B6D4733AD559` |
| `structural_seed_DEVELOPMENT_ONLY.json` | `3080278` | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |
| `validation_report_DEVELOPMENT_ONLY.md` | `858` | `28AE9108A9A6801FF9634E1FDF95121CADC1AEBA32F9CE225ACC12D15FA15ECB` |

The ordered input artifact-set identity is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
The Candidate Evidence member is read-only lineage evidence; its incomplete
Kill-zone prefix must not supply or override the complete dependency in Section
7. Missing, extra, renamed, reordered-manifest, or byte-drifted members stop.

## 7. Exact complete Kill-zone dependency root

The only admissible downstream Kill-zone dependency root is:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1/`

Its exact five-file scope is:

| File | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | `1486` | `7768A255FEB5F3981CD3D43CC7CBFD517CA66C43F7E6927300F2FE5B12DAE4E9` |
| `input_binding_DEVELOPMENT_ONLY.json` | `4231` | `A6045EF6379E95CD749E31710FDA4D5293D61EBF879CAF0AB4F0FE9B978B22B9` |
| `kill_zone_dependency_DEVELOPMENT_ONLY.json` | `56515215` | `8E3494BEE9BEBB8EA42E8880F87DED9603D6011AC84719867F21CC5974720112` |
| `README_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `387` | `77C99B29646B65A3C1507AA9A94697E65B2E1EBA40B0781E2C7339559D0D6B31` |
| `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `643` | `6CB7062EBECF85F84F6C3072277D4646507107E01C5491BF66E312F2E18BDFB6` |

Its artifact-set identity is
`089e38c945f679674853282b6b730a038d936f3ed2eeaa2f23fe123636df6f05`.
The manifest must remain `COMPLETED_NON_PROMOTABLE`, `complete=true`, with `133`
segments, `17,404` bars, `64` requested dates, zero OOS, and two independent
executions. The retained temporary run is audit evidence only and is not an
alternative dependency root.

The dependency's immutable input binding records these construction-time Phase
B provenance hashes: source
`270F9350C1CAAEB69DE87DD1079C876DAF0ADDF00C459F0CDDCE968BF208E39D`,
test `CAF35F41DBA99D4977A5E6827104A5BB961DA754408FA3CEC8156887AA4713FD`,
and checkpoint
`A21DA53852CBCC29ED12E5AA36D1D6E4A6C976438CBDC6FEB6C8ECB8639320C4`.
They remain exact historical construction provenance and must validate against
the immutable dependency bytes; they are not required to equal the corrected
current tracked hashes in Section 9. The authorized difference is bound only by
the alignment correction proposal and commit `4f33bf4`. Rewriting the dependency
to replace those historical hashes, or treating any unlisted difference as
authorized drift, is forbidden.

## 8. Immutable dataset, calendar, and partition binding

Both roots must reconcile to the same exact binding:

- binding version
  `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural-seed ID
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- continuity artifact-set identity
  `5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`;
- `VALID`, development-only dataset with `17,404` bars, `133` canonical
  segments, `64` strictly increasing requested trade dates from `2026-02-23`
  through `2026-05-22`, and zero OOS membership/access;
- contracts exactly `{GCJ26-COMEX, GCM26-COMEX}`, roll trade date
  `2026-04-01`, instrument/timeframe/tick size `GC` / `5M` / exact `0.1`;
- source/exchange timezones `Asia/Tokyo` / `America/New_York` and runtime
  tzdata version exact normalized `2026.2`; and
- calendar version
  `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`,
  `68` entries, `67 OPEN`, `1 SESSION_CLOSED`.

Any cross-root mismatch is `INVALID` and stops before output creation.

## 9. Exact tracked code and contract hashes

The refreshed run is admissible only when these tracked bytes match exactly:

| Path | SHA-256 |
|---|---|
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `FA78D5C978DD002D80363008A451FE4C8A5882D3AA7EC6F4979A038509C1FE7F` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `E52F37607FE3DFFC255617420CA47C5A9F38F70298458F15C386F950AA0BB872` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md` | `C32626B4E90B6684636387B79AFDEDB7635D8D9D9D5595A2E017091F31E3C5FD` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |

The analyzer version remains exactly
`GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1`; corrected observation
membership did not change the public API, identity payloads, version, enums,
frozen dataclasses, or exports.

These current hashes intentionally supersede only the three construction-time
Phase B provenance hashes recorded inside the immutable dependency binding in
Section 7. All unchanged Kill-zone/shared tracked dependency hashes must match
both the immutable construction record and this current repository. This
lineage-aware distinction is exact; it is not a general hash-drift waiver.

## 10. Exact public analyzer boundary

The future runner reconstructs public inputs and makes exactly one semantic call
per fresh run to the existing keyword-only function:

```python
analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(
    *,
    instrument,
    timeframe,
    dataset_config,
    dataset_result,
    requested_trade_dates,
    split_session_calendar,
    kill_zone_calendar,
    observations,
    kill_zone_contexts,
    kill_zone_snapshots,
    kill_zone_result,
)
```

Identity verification uses only the committed keyword-only
`make_gc_ny_am_sweep_reclaim_id()` contract. No filesystem path, threshold,
window, dependency selector, repair flag, or caller-defined gate may be added.

## 11. Exact reconstruction boundary

For each canonical segment in manifest order, the runner reconstructs immutable
dataset bars and the corresponding complete dependency segment result. It must
preserve source segment ordinal/ID, contract, trade date, bar index, timestamps,
OHLC ticks, volume, and closed state. It reconstructs split-session and Kill-zone
calendar entries from the accepted normalized calendar without network lookup,
inference, or timezone fallback.

It projects exactly one `GCNYAMSweepReclaimObservation` for each canonical bar
whose normalized open is in `[07:00:00, 09:55:00) America/New_York` and whose
normalized close is independently in `[07:00:00, 10:00:00)`. Thus `07:00`
through `09:50` opens are eligible, while the canonical `09:55` open / `10:00`
close bar is retained only as dataset evidence. Every projected observation
must reconcile one-to-one at its bar-close evidence moment with the
`NEW_YORK_AM`, `VERIFIED`, matching-trade-date context and corresponding
snapshot from the complete dependency. Other dataset bars remain required
dataset evidence but are not projected observations. The incomplete Candidate
Evidence prefix may not fill, filter, or replace any dependency object.

## 12. Complete dependency deserialization and identity gate

All `133` dependency segment results must appear exactly once in canonical
segment order. Per-segment status must be native `VALID` or `NONE`; all reasons,
blocking reasons, ordered contexts, ordered snapshots, and result digests must
match the dependency bytes. `NONE` is explicit complete evidence and must not be
dropped. `INVALID`, `AMBIGUOUS`, `UNKNOWN`, missing/extra/duplicate/reordered
segments, or count drift blocks the run.

Every Kill-zone context and snapshot identity is recomputed with public
`make_kill_zone_id()`. Snapshot history must be ordered, cumulative, unique, and
same-segment causal. The aggregate counts must reconcile exactly to `9,839`
contexts, `9,839` snapshots, `2,276` `NEW_YORK_AM` contexts, and status counts
`101 VALID` / `32 NONE`. No object may be synthesized outside the public output.

The dependency input binding is validated byte-for-byte with its recorded
construction-time provenance. The future runner must not compare its three
historical Phase B hashes directly to the corrected current bytes; instead it
must verify the exact authorized lineage mapping in Sections 1, 7, and 9. Any
other construction/current mismatch is `INVALID` and stops.

## 13. Observation, calendar, and no-look-ahead gate

Observations are ordered by canonical segment order and then strictly increasing
bar index and normalized timestamp. Each is fully closed, timezone-aware,
integer-tick, and has nonnegative integer volume; booleans are not integers.
Opening/closing moments are exact five-minute moments, and context/snapshot
moments equal the observation close, which is the public Kill-zone evidence
moment.

Each requested date must have complete split-session and Kill-zone calendar
coverage before analysis. The fixed New York window, runtime tzdata, trade-date
assignment, session status, and `NEW_YORK_AM` classification are never inferred
from future rows. Malformed independently determinable evidence is `INVALID`
before missing-context `UNKNOWN`. No OOS path may be opened or enumerated.

## 14. Locked hypothesis and structural outcome semantics

The opening range uses exactly six observations opened at `07:00`, `07:05`,
`07:10`, `07:15`, `07:20`, and `07:25 America/New_York`, first-known at the
`07:25` bar close. Candidate opens are exact start-inclusive/end-exclusive
`[07:30, 09:00)`. One-tick sweep, same-bar reclaim, midpoint equality, earliest
qualifying candidate, bullish/bearish mirror, and both-boundary ambiguity remain
unchanged.

Formation is not outcome evidence. Outcome uses the next exact twelve later
compatible observations in the same segment, contract, trade date, and context
grain. Earliest midpoint reach, earliest close-through invalidation,
`SAME_BAR_AMBIGUOUS`, `TIMEOUT`, and truncated-horizon `UNKNOWN` retain committed
semantics. Post-`10:00` evidence cannot repair a truncated NY-AM horizon.

## 15. Deterministic preflight and decision gates

Before either temporary root is created, a separate authorized runner must
prove the lineage-aware repository/hash/API/runtime bindings in Sections 1, 7,
and 9, both exact input roots and file sets, cross-root dataset/calendar
identity, output-root absence, Git exclusion, and zero
OOS/network/repair/parameter-choice need.

Publication eligibility requires two fresh calls returning byte-identical,
complete public `VALID` or `NONE` results with non-null manifests and 100%
identity/count/reason reconciliation. `INVALID`, `AMBIGUOUS`, or `UNKNOWN`
publishes no final root.

For an eligible structural result, hypothesis `PASS` requires all of:

- at least `30` complete candidates;
- at least `24` distinct eligible development trade dates;
- at least `10` bullish and `10` bearish complete candidates;
- both contracts represented by at least `8` candidates each;
- a complete requested-date funnel with zero silent exclusion; and
- zero OOS, feature, label, model, PnL, risk, entry/exit, or trading contact.

An eligible result failing any conjunct is published as immutable hypothesis
`FAIL` and retires this setup on the accepted dataset without rescue. No outcome
is predeclared.

## 16. Exact temporary and final output roots

The future run may create only:

- run A temporary root:
  `private_data/sierra_chart/.tmp-gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v2-run-a/`;
- run B temporary root:
  `private_data/sierra_chart/.tmp-gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v2-run-b/`; and
- final root:
  `private_data/sierra_chart/gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v2/`.

All three are absent at proposal time and must be absent at execution start.
The historical V1 root must remain absent and unused. Unexpected existence,
symlink/reparse ambiguity, nesting, or path drift stops without overwrite,
merge, delete, or repair.

## 17. Exact five-file output scope

Each fresh run may write exactly:

1. `input_binding_NON_PROMOTABLE_FEASIBILITY.json`;
2. `sweep_reclaim_result_NON_PROMOTABLE_FEASIBILITY.json`;
3. `artifact_manifest_NON_PROMOTABLE_FEASIBILITY.json`;
4. `validation_report_NON_PROMOTABLE_FEASIBILITY.md`; and
5. `README_NON_PROMOTABLE_FEASIBILITY.md`.

Raw rows, input copies, charts, prompts, notebooks, caches, features, labels,
splits, models, PnL, risk, and integration artifacts are forbidden. The manifest
excludes itself from its member list and binds the other four exact names,
lengths, hashes, public result identity/status/reasons/counts, hypothesis
decision, two-run equality, and deterministic artifact-set identity.

## 18. Deterministic serialization and binding schema

Machine-readable output is UTF-8 without BOM, LF-only, one terminal newline,
sorted object keys, compact JSON separators `(",", ":")`, and
`ensure_ascii=True`. Ordered tuples remain arrays in causal order; mappings do
not represent order. Datetimes use canonical UTC `Z`; dates use ISO format;
integers are decimal integers; Decimal midpoint uses canonical `.0`/`.5` with
all zero forms serialized as `0.0`; enums use exact `.value`; identities are
lowercase 64-hex in payloads and retain public kind prefixes externally.

The input binding records all governing proposal identities/hashes, baseline
and implementation commits, the exact historical-to-current Phase B provenance
mapping, every exact member of both roots, both artifact-set identities,
dataset/seed/continuity/calendar/timezone/config bindings, exact public
signatures, requested dates, contracts, analyzer call count, and explicit false
flags for OOS, features, labels, training, models, integration, promotion, PnL,
trading, and network access.

## 19. Atomic publication and immutable failure evidence

Run A and run B are reconstructed independently from immutable bytes. After
each analyzer call, a separate validation pass recomputes public identities,
object/count/status/reason reconciliation, serialization, file hashes, and
scope. Only byte-identical validated sets are publication-eligible. One
temporary root may be atomically renamed to the absent final root only after all
gates pass; the other remains validation evidence until the post-run audit.

On failure, nothing is promoted. A task-created temporary root may be removed
only after exact-path and parent containment verification. Inputs and unrelated
state are never modified. A published final root is immutable; correction
requires a new reviewed proposal and a new root, never in-place repair.

## 20. Status, atomicity, prefix invariance, and audit

Final public precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

A complete trade-date group promotes atomically. A failing group promotes no
range, candidate, outcome, or manifest from that group or later; strictly prior
complete public bytes remain immutable. `SAME_BAR_AMBIGUOUS` is a structural
outcome, not a waiver of invalid evidence.

Prefix invariance applies only to a valid prefix ending at a complete requested
trade-date boundary followed by a strictly later complete append across both
input roots. Same-effective append, partial session/horizon, missing dependency
segment, historical insertion, repair, reorder, roll/calendar/tzdata mutation,
or dependency replacement is ineligible. Independent post-run audit must
recompute all bindings, bytes, identities, counts, decisions, Git exclusion,
and zero-authority claims without reusing the runner's in-memory conclusions.

## 21. Inline synthetic exact 48-case private-run matrix

The refreshed procedure locks exactly these sequential logical cases:

1. Missing Phase A input root stops before deserialization.
2. Missing complete Kill-zone dependency root stops before deserialization.
3. Existing V2 temporary or final root stops without overwrite or deletion.
4. Phase A missing, extra, renamed, reordered-manifest, size-, or hash-drifted member stops.
5. Dependency missing, extra, renamed, reordered-manifest, size-, or hash-drifted member stops.
6. Repository/proposal/dependency drift or any hash mismatch outside the exact three-member historical-to-current Phase B lineage mapping stops.
7. Cross-root dataset, calendar, timezone, segment, date, contract, or OOS binding mismatch stops.
8. Dataset remains `VALID`, development-only, `17,404` bars, `133` segments, and zero OOS.
9. Requested dates are exact `64`, strictly increasing, and span `2026-02-23` through `2026-05-22`.
10. Contracts are exactly `GCJ26-COMEX` and `GCM26-COMEX`, with roll date `2026-04-01`.
11. Incomplete Candidate Evidence remains immutable `UNKNOWN` lineage and is never a dependency substitute.
12. Complete dependency has all `133` unique canonical segment results in order.
13. Dependency status counts are exactly `101 VALID` and `32 NONE`; `NONE` is retained.
14. Dependency aggregate counts are exactly `9,839` contexts, `9,839` snapshots, and `2,276` NY-AM contexts.
15. Dependency `INVALID`, `AMBIGUOUS`, `UNKNOWN`, missing suffix, or count drift stops.
16. Every context and snapshot identity recomputes and ordered history mirrors causality.
17. Split-session and Kill-zone calendars reconcile exact version, digest, trade date, and session status.
18. Runtime tzdata must normalize exactly to `2026.2`; unavailable timezone/version stops.
19. Canonical expected observations are exact five-minute opens in `[07:00, 09:55)` whose closes are in public Kill-zone `[07:00, 10:00)` evidence time.
20. Valid non-NY-AM dataset bars remain dataset evidence and do not cause observation rejection.
21. Every projected observation reconciles one-to-one at its bar-close moment to its NY-AM context and snapshot.
22. Duplicate, missing, extra, reordered, cross-segment, cross-contract, or wrong-date projection is `INVALID`.
23. Exact six `07:00` through `07:25` observations create a positive-width opening range.
24. Missing or malformed opening-range member follows locked `UNKNOWN`/`INVALID` precedence.
25. Candidate window is exact start-inclusive/end-exclusive `[07:30, 09:00)`.
26. Bullish upper-boundary one-tick sweep plus same-bar reclaim qualifies at equality.
27. Bearish lower-boundary one-tick sweep plus same-bar reclaim mirrors exactly.
28. Wick-only, insufficient sweep, outside close, doji ambiguity, and both-boundary cases preserve locked reasons.
29. Earliest qualifying candidate wins deterministically without hash-order selection.
30. Formation observation is excluded from outcome evidence.
31. Outcome horizon is the next exact twelve compatible NY-AM observations.
32. Earliest midpoint reach and close-through invalidation use exact mirrored geometry.
33. Same-bar midpoint and invalidation emits exact `SAME_BAR_AMBIGUOUS`.
34. Twelve complete no-hit observations emit exact `TIMEOUT`.
35. Truncated horizon is `UNKNOWN`; post-`10:00` evidence cannot repair it.
36. Final status precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
37. A failing trade-date group promotes nothing from itself or later and preserves strictly prior bytes.
38. Public manifest exists only for complete final `VALID` or `NONE`.
39. Both fresh executions make exactly one analyzer call and are object- and byte-identical.
40. Deterministic serialization covers UTC, dates, enums, integers, Decimal `.0`/`.5`, zero, and identities.
41. Output contains exactly the five locked files and manifest excludes itself.
42. Candidate count gate requires at least `30` and at least `24` eligible dates.
43. Direction gate requires at least `10` bullish and `10` bearish complete candidates.
44. Contract gate requires both contracts with at least `8` candidates each.
45. Eligible conjunctive gate failure publishes immutable hypothesis `FAIL` without rescue.
46. Eligible conjunctive gate success records `PASS` but grants no downstream authority.
47. Complete-boundary strictly-later prefix invariance passes; repair/reorder/version mutation is ineligible.
48. OOS, feature, label, model, training, PnL, integration, network, push, and trading contact remain forbidden.

Parameterization may expand test instances but must not change this exact logical
count or create a new gate.

## 22. No training, promotion, integration, or trading authority

Ranges, candidates, and structural outcomes are diagnostic evidence, not trades
or labels. `PASS` cannot become a feature table, confidence, strategy rule,
backtest result, risk instruction, alert, or order under this proposal. `FAIL`
must be preserved and cannot be rescued by tuning, date selection, threshold
change, or selective exclusion.

Even `PASS` does not authorize training. The accepted dataset has only two
canonical contract months, while the broader training gate requires a separate
prospective partition decision, sufficient canonical coverage, formal
feature/label contracts, no-look-ahead proof, validation, and untouched OOS.

## 23. Acceptance, rollback, promotion, and STOP conditions

Documentation acceptance requires exact one-file scope, exactly `24` sequential
numbered sections, exactly `48` sequential cases, formatting PASS, exact SHA-256,
full-content/cached-diff audit, cache-disabled focused and full regression PASS,
and an independent semantic/structural audit. Only exact-path staging and a local
documentation commit are authorized by the present workflow.

Before commit, rollback is restoration of this exact tracked document to its
accepted parent bytes; after commit it is a bounded revert. History rewriting
and accepted-evidence deletion are forbidden.
STOP on input/hash/API/version/calendar/timezone/partition/count/status/reason/
identity/serialization/output-root/scope drift; private mutation; OOS contact;
nondeterminism; exception leakage; silent sort/exclusion/repair; parameter or
gate change; feature/label/model/training/PnL/integration/trading work; broad
staging; private execution without separate exact authority; or push without
separate explicit privacy/export authorization.

## 24. Final bounded decision and next single task

The exact decision is:

`READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_EXPLICIT_REFRESHED_PRIVATE_RUN_AUTHORIZATION`

After independent audit and local commit of this exact document, `STOP` before
push and private execution. The next single task is push preflight/publication
of this one-file documentation commit under separate explicit GitHub
privacy/export authority. Only after publication may a separate exact execution
authorization permit the two-run atomic V2 feasibility procedure in Sections
10–20. Training, OOS, feature/label construction, integration, and trading
remain forbidden.
