# GC Futures Phase B NY-AM Opening-Range Sweep-Reclaim Reversion Private-Run Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-PRIVATE-RUN-PROPOSAL-V1`.
- Decision date: `2026-08-16`.
- Binding implementation commit: `c16065b3149454c4b71585573a1f731507336aef`.
- Binding parent proposal commit: `83c7309bb532ca29bbfd2c3d27fb484a1dd53c45`.
- Classification: documentation-only private-run preflight contract.
- Current decision: `READY_FOR_EXPLICIT_PHASE_B_SWEEP_RECLAIM_PRIVATE_RUN_AUTHORIZATION`.

This record does not execute or authorize the private run. It binds the exact
accepted development input, committed analyzer, reconstruction procedure,
prospective private output, atomic publication, validation gates, and STOP
conditions. It grants no feature, label, model, OOS, integration, execution,
or remote-publication authority.

## 2. Decision summary

The committed V1 analyzer is regression-clean and implements the exact locked
New York AM opening-range sweep, same-bar reclaim, and midpoint-reversion
feasibility hypothesis. The accepted development bundle is immutable,
Git-ignored, `VALID`, and contains `17,404` bars in `133` canonical segments,
with zero OOS bars.

Unlike the retired breakout-continuation V1, this hypothesis requires both
accepted canonical contracts rather than three contracts. The immutable
dataset contains exactly `GCJ26-COMEX` and `GCM26-COMEX`, so no pre-run gate is
already impossible. Candidate, date, direction, per-contract, funnel, and
repeatability gates remain unknown until execution. The next possible action
is therefore one separately authorized, development-only, non-promotable
private feasibility run under this document; it is not authorized now.

## 3. Verified repository baseline

At this proposal's baseline:

- `HEAD`, local `origin/main`, and live remote `main` equal
  `c16065b3149454c4b71585573a1f731507336aef`;
- the subject is `feat(analysis): add GC NY-AM sweep-reclaim feasibility`;
- the exact parent is `83c7309bb532ca29bbfd2c3d27fb484a1dd53c45`;
- focused cache-disabled evidence is `59 passed in 7.11s`;
- full explicit public regression evidence is `2453 passed in 29.27s`;
- the accepted private input root in Section 6 exists and is Git-ignored;
- the prospective private output root in Section 15 is absent;
- no sweep-reclaim private run, feature/label build, training, OOS access,
  integration, model use, or trading action has occurred; and
- these three unrelated untracked documents remain outside scope and untouched:
  `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`,
  `docs/gc_futures_real_data_input_binding_change_proposal.md`, and
  `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Any baseline drift before acceptance is a STOP condition and does not authorize
repair, refresh, or reinterpretation.

## 4. Exact documentation-only scope

The only path authorized by this task is:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_change_proposal.md`

Only this file may be audited, corrected, staged by exact path, and committed
locally. Broad pathspecs, source/test/private-data writes, external fixtures,
run outputs, integration, and push are forbidden. Every other tracked and
untracked path remains frozen.

## 5. Authority, global freeze, and no-trading boundary

This proposal grants no authority to run private data, inspect OOS, tune a
parameter, produce a feature or label, fit or invoke a model, estimate PnL,
select a strategy, wire runtime behavior, alert, order, or manage a position.
The analyzer remains standalone and diagnostic-only.

No local or remote language model may read raw private market rows, alter
candidate selection, infer a missing input, waive a gate, or treat structural
outcomes as trades. AI assistance is limited to public-code review and
manifest-level evidence summarization. The global freeze remains active
outside Section 4.

## 6. Exact immutable private input bundle

The accepted input root is exactly:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Its complete accepted eight-file scope is:

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

The private input artifact-set identity is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Missing, extra, renamed, duplicated, reordered-manifest, byte-drifted, or
hash-drifted evidence is `INVALID`. Filesystem order is never evidence.

## 7. Dataset, seed, continuity, and requested-date binding

The accepted binding is exactly:

- version
  `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural-seed ID
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- continuity artifact-set identity
  `5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`;
- dataset status `VALID`, `17,404` development bars, `133` development
  segments, and zero OOS bars;
- first/last trade dates `2026-02-23` / `2026-05-22`;
- exact increasing tuple of `64` unique accepted development trade dates;
- roll trade date `2026-04-01`;
- instrument/timeframe/tick size `GC` / `5M` / Decimal `0.1`; and
- canonical contracts exactly `{GCJ26-COMEX, GCM26-COMEX}`.

Candidate Evidence remains `UNKNOWN`, has `113` segment results and zero
candidates, with exact reason and blocking reason
`a swept pool has a truncated confirmation horizon`. That is upstream lineage,
not this analyzer's feasibility result, candidate source, or reason to inspect
OOS. Raw-only contracts cannot become canonical evidence.

## 8. Calendar, timezone, partition, and no-look-ahead binding

The accepted calendar binding is exactly:

- calendar version
  `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`;
- split-session digest
  `5f70052e27655a95fdad6aa69f546a6c84a28743bb6635ca4f55d015c39cad6d`;
- Kill-zone digest
  `dd16b5734f4dfe54a54c47aa1889302abf92102e6478459b98a8e642732f88f3`;
- runtime timezone-data version `2026.2`;
- exchange/source zones `America/New_York` / `Asia/Tokyo`; and
- official evidence hashes
  `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`,
  `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`,
  and `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

All evidence remains `DEVELOPMENT`. OOS partitions, future rows, current-year
calendar substitution, inferred holiday repair, broker evidence, timezone
fallback, and wall-clock-derived dates are forbidden.

## 9. Exact committed implementation and dependency hashes

The private run stops unless every bound tracked artifact matches:

| Artifact | SHA-256 |
|---|---|
| governing feasibility proposal | `EEC03B71A19FFF8EDC786FB1D20210F98F40FCB9314BCEE705FA0C6B93FDE2AD` |
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `3F9E64C277A1F00453585EFD66371B81D10DDA14E73FDAFE111AD1A213CAC477` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `7F49D1015CC0F8D2DD469E428DB2A9D78FF3D95933FE4540B3FE8502ED43BDA9` |
| implementation checkpoint | `3BBCC23245693629E03A7352D50596330DFB4596A6BB8C13D5EB81855147490A` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

This proposal's own hash is computed after final audit and bound by its local
commit. No mismatch is waivable.

## 10. Exact public API, types, exports, and version

The committed version is exactly
`GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1`. Exact public exports, in
order, are the version constant, `GCNYAMSweepReclaimIdentityKind`,
`GCNYAMSweepReclaimOutcomeType`, `GCNYAMSweepReclaimObservation`,
`GCNYAMSweepReclaimOpeningRange`, `GCNYAMSweepReclaimCandidate`,
`GCNYAMSweepReclaimOutcome`, `GCNYAMSweepReclaimManifest`,
`GCNYAMSweepReclaimResult`, `make_gc_ny_am_sweep_reclaim_id`, and
`analyze_gc_ny_am_opening_range_sweep_reclaim_reversion`.

Identity kinds are exactly `OBSERVATION`, `OPENING_RANGE`, `CANDIDATE`,
`OUTCOME`, and `MANIFEST`. Outcome types are exactly `MIDPOINT_REACHED`,
`INVALIDATED`, `TIMEOUT`, `SAME_BAR_AMBIGUOUS`, `INCOMPLETE`, and `INVALID`.
All six public dataclasses remain frozen with committed fields, annotations,
order, and defaults.

The analyzer signature is exact and keyword-only:

```python
analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(
    *,
    instrument: str,
    timeframe: str,
    dataset_config: GCDatasetBuildConfig,
    dataset_result: GCDatasetBuildResult | None,
    requested_trade_dates: tuple[date, ...] | None,
    split_session_calendar: tuple[GCSplitSessionCalendarEntry, ...] | None,
    kill_zone_calendar: tuple[KillZoneCalendarEntry, ...] | None,
    observations: tuple[GCNYAMSweepReclaimObservation, ...] | None,
    kill_zone_contexts: tuple[KillZoneContext, ...] | None,
    kill_zone_snapshots: tuple[KillZoneSnapshot, ...] | None,
    kill_zone_result: KillZoneResult | None,
) -> GCNYAMSweepReclaimResult
```

The identity-builder signature and defaults remain exactly those in the
committed source and governing proposal. Positional calls, extra parameters,
filesystem discovery, caller-selected thresholds, and hidden inputs stop.

## 11. Exact prospective reconstruction contract

Each of two fresh executions must reconstruct all public objects independently
from the same eight immutable input files:

1. validate exact names, sizes, hashes, manifest order, and artifact-set ID;
2. reconstruct the immutable `GCDatasetBuildResult` and nested segments/bars;
3. reconstruct split-session and Kill-zone calendar tuples independently;
4. reconstruct canonical Kill-zone contexts, snapshots, and result from
   accepted Candidate Evidence without rerunning or enriching detection;
5. derive the requested-date tuple from all `64` canonical development trade
   dates, never from wall clock, filenames, or calendar-only rows;
6. project exactly one observation per canonical bar, preserving segment
   ordinal/ID/contract/index, integer-tick OHLC, integer volume, UTC close,
   exact close-minus-five-minutes open, and context/snapshot IDs;
7. recompute every available foreign and public identity; and
8. call the exact analyzer once.

No input or observation may be sorted silently, excluded, filled, duplicated,
interpolated, relabeled, or repaired from a raw export.

## 12. Dataset and observation admissibility gate

Execution requires a `VALID` dataset with non-null manifest, exact dataset ID,
development-only evidence, zero OOS contact, canonical segment ordering, and
complete one-to-one observation reconciliation. Every bar is fully closed,
timezone-aware, integer-tick, has nonnegative integer volume, and satisfies
canonical OHLC geometry; booleans are forbidden as integers.

Segment ordinals, bar indices, and normalized open/close moments preserve
accepted order. Duplicate, missing, reordered, cross-segment, cross-contract,
unrequested, or malformed evidence is `INVALID`. Determinably later malformed
evidence preserves only strictly prior immutable objects and promotes nothing
from the failing group or later.

## 13. Calendar, Kill-zone, and session admissibility gate

Every requested date requires exact split-session and Kill-zone coverage.
Opening-range, formation, and horizon observations reference canonical
`NEW_YORK_AM`, `VERIFIED`, matching-trade-date contexts and snapshots with
recomputed identities. Context moments equal bar-open moments and snapshot
order mirrors observation order.

The range uses exactly six bars opened at `07:00`, `07:05`, `07:10`, `07:15`,
`07:20`, and `07:25 America/New_York`. Candidate opens are restricted to
`[07:30, 09:00)`. Outcomes use only the next exact twelve later closed bars in
the same segment, contract, trade date, and context. Formation is not outcome
evidence. Missing context is `UNKNOWN` only after independently determinable
supplied evidence validates; malformed evidence is `INVALID` first.

## 14. Deterministic preflight and feasibility decision gate

Before creating a temporary output directory, an authorized runner must prove:

1. repository, dependency, private-input, calendar, timezone, and API bindings
   exactly match Sections 3 and 6–10;
2. the final output root is absent;
3. the input root has exactly the accepted eight immutable members;
4. reconstruction needs no OOS, network, inference, repair, or parameter choice;
5. both accepted contracts are available as canonical dataset segments; and
6. every required runtime dependency and IANA timezone is available.

Private feasibility PASS after two fresh runs requires all of:

- at least `30` complete candidates;
- at least `24` distinct eligible development trade dates;
- at least `10` bullish and `10` bearish complete candidates;
- both accepted contracts represented with at least `8` candidates each;
- `100%` public object, identity, count, status, reason, and artifact-byte
  reproducibility across the two runs;
- a complete requested-date funnel and zero silent exclusion; and
- zero OOS, feature, label, PnL, risk, entry/exit, model, or trading contact.

The run is publication-eligible only when both analyzer calls return the same
complete `VALID` or `NONE` result with a non-null public manifest and every
integrity gate passes. `INVALID`, `AMBIGUOUS`, or `UNKNOWN` is an incomplete or
untrustworthy run, publishes no final root, and requires STOP. For a
publication-eligible run, the conjunctive count/coverage predicates above
produce the separate hypothesis decision `PASS` or `FAIL`. A valid `FAIL`
result is still published as immutable negative evidence and retires this
final setup family on the current dataset without rescue. `PASS` authorizes
only a later documentation proposal for a feature/label experiment, not that
experiment. No threshold is predeclared PASS or FAIL now.

## 15. Prospective private output root

After separate exact execution authorization, the only output root is:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v1/`

It is currently absent. It must be absent at start and must not be nested in,
overwrite, or mutate the accepted input root. Unexpected existence stops
without reading, merging, deleting, or replacing it.

## 16. Prospective output artifact set

The final root may contain exactly five files:

1. `input_binding_NON_PROMOTABLE_FEASIBILITY.json`;
2. `sweep_reclaim_result_NON_PROMOTABLE_FEASIBILITY.json`;
3. `artifact_manifest_NON_PROMOTABLE_FEASIBILITY.json`;
4. `validation_report_NON_PROMOTABLE_FEASIBILITY.md`; and
5. `README_NON_PROMOTABLE_FEASIBILITY.md`.

Raw rows, source exports, input copies, charts, prompts, notebooks, caches,
features, labels, train/validation/OOS splits, models, entry/exit, PnL, and risk
artifacts are forbidden.

## 17. Deterministic serialization contract

Machine-readable output uses UTF-8 without BOM, LF endings, one terminal
newline, sorted JSON object keys, compact separators `(",", ":")`, and
`ensure_ascii=True`. Ordered tuples are ordered arrays; mappings never encode
causal order. Timestamps use UTC ISO-8601 microseconds with terminal `Z`, dates
use `YYYY-MM-DD`, finite Decimals use canonical fixed text with every zero as
`0.0`, enums use exact `.value`, inner identities are lowercase 64-hex, and
outer member hashes are uppercase 64-hex.

Clock time, host path, file timestamp, locale, random value, object address,
Python `repr`, pickle, hash iteration, exception text, and enumeration order are
forbidden content and identity inputs.

## 18. Prospective input binding and artifact manifest

The input binding records proposal ID/hash, implementation commit and hashes,
the exact eight input members, artifact-set/dataset/seed/continuity identities,
calendar versions/digests, timezone evidence, config, exact signatures,
requested dates, contracts, analyzer call count, and explicit false flags for
OOS, feature/label, training, model, integration, promotion, and trading.

The artifact manifest excludes itself from its member list and binds the other
four names, byte lengths, hashes, exact five-file scope, public status/reasons/
funnel counts, the exact `PASS` or `FAIL` hypothesis decision, two-run equality,
and deterministic artifact-set identity. The second run is validation evidence
only; only one byte-identical validated set may be published.

## 19. Atomic publication, rollback, and failure preservation

An authorized run creates two new task-specific temporary directories beneath
the private parent. Each run reconstructs from immutable bytes and calls the
analyzer exactly once. Object equality, identity recomputation, machine-byte
equality, manifest completeness, and every publication-integrity gate are
validated before one temporary directory is atomically moved to the absent
final root. The hypothesis decision may be either `PASS` or valid `FAIL`;
publication never converts `FAIL` into promotion authority.

On any failure, neither temporary result is promoted. Temporary directories
created by this task are removed only after exact-path verification; accepted
input bytes and unrelated state are never modified. A published final root is
immutable. Any correction requires a new reviewed proposal and new output root,
not in-place repair or overwrite.

## 20. Independent validation, status, and prefix boundary

Public status precedence remains
`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`. `SAME_BAR_AMBIGUOUS` is a
terminal structural outcome, not permission to hide invalid evidence. A public
manifest exists only for complete final `VALID` or `NONE`, never for
`INVALID`, `AMBIGUOUS`, or `UNKNOWN`.

Independent audit recomputes input scope/hashes, tracked hashes, runtime
version, signatures, requested dates, contract set, identities, counts,
statuses, reason order, both run bytes, output scope, and Git exclusion.
Prefix invariance applies only at a complete requested-date boundary with a
strictly later complete append. Same-effective append, partial horizon,
historical insertion, repair, reorder, roll, calendar/version mutation, or
contract-set mutation is ineligible.

## 21. Inline synthetic exact 48-case private-run matrix

This record locks exactly these sequential logical cases. Parameterization may
expand collected tests but not the count of `48` logical cases.

1. Missing accepted input root stops before deserialization.
2. Existing final output root stops without opening or overwrite.
3. Exact eight names, sizes, hashes, manifest order, and artifact-set ID pass.
4. Missing, extra, duplicate, renamed, reordered, or drifted member stops.
5. Commit, proposal, source, test, checkpoint, or dependency drift stops.
6. Runtime tzdata is `2026.2` and both IANA zones are available.
7. Dataset, seed, continuity, calendar, and binding identities reconcile.
8. Dataset is `VALID`, manifest-backed, development-only, and zero-OOS.
9. Dataset has exactly `17,404` bars and `133` canonical segments.
10. Date span, `64` requested dates, and `2026-04-01` roll reconcile.
11. Candidate Evidence remains upstream `UNKNOWN` and is not relabeled.
12. Exact `GC` / `5M` / Decimal `0.1` configuration reconciles.
13. Split-session calendar version, digest, order, and sources reconcile.
14. Kill-zone calendar reconstructs independently with exact digest/version.
15. Calendar repair, broker substitution, or timezone fallback stops.
16. Bars reconstruct as immutable closed integer-tick/integer-volume evidence.
17. Observations project one-to-one with exact five-minute open/close moments.
18. Missing, duplicate, reordered, forked, or unreconciled observation is invalid.
19. Kill-zone contexts/snapshots recompute and preserve causal order.
20. Six exact `07:00`–`07:25` source bars create a positive-width range.
21. Partial, substituted, cross-date/contract, or zero-width range promotes none.
22. Candidate window is exact start-inclusive/end-exclusive `[07:30, 09:00)`.
23. Upper one-tick sweep and same-bar upper-half reclaim creates bearish.
24. Lower one-tick sweep and same-bar lower-half reclaim creates bullish.
25. Midpoint equality, boundary miss, or sub-one-tick excursion is noncandidate.
26. Outside-range close cannot be relabeled by a later reclaim.
27. Both-boundary sweep in one group is `AMBIGUOUS` with no candidate.
28. Earliest canonical qualifying candidate wins without replacement.
29. Bullish and bearish boundary/invalidation geometry mirrors exactly.
30. Formation is excluded; horizon is next exact twelve compatible bars.
31. Midpoint-first and invalidation-first use earliest canonical event.
32. Same-bar midpoint/invalidation emits exact `SAME_BAR_AMBIGUOUS`.
33. Twelve complete no-hit bars emit exact `TIMEOUT`.
34. Truncated horizon is `UNKNOWN` and promotes no outcome.
35. Final precedence is INVALID over AMBIGUOUS over UNKNOWN over VALID over NONE.
36. Later malformed evidence preserves only strictly prior immutable objects.
37. Every OBSERVATION, OPENING_RANGE, CANDIDATE, OUTCOME, and MANIFEST ID recomputes.
38. Only equal complete `VALID`/`NONE` results with manifests are publication-eligible.
39. Ordered funnel and reason vocabulary reject free text and reordering.
40. Canonical contracts are exactly `GCJ26-COMEX` and `GCM26-COMEX`.
41. Raw-only, synthetic, merged-roll, spot, CFD, option, or micro evidence stops.
42. Both canonical contracts must have at least eight complete candidates.
43. Total/date/direction gates remain `30` / `24` / `10` and `10`.
44. Two fresh reconstructions produce equal objects, identities, bytes, and PASS/FAIL decision.
45. Threshold/window/geometry/horizon/gate change or V1 rescue stops.
46. Failure publishes nothing and preserves all accepted private bytes.
47. Exact one-doc Git scope, output-root absence, and no-push boundary reconcile.
48. Feature, label, PnL, model, training, OOS, integration, push, and trading
    surfaces remain unused.

## 22. No feature, model, promotion, or trading authority

Candidate and outcome evidence are research diagnostics, not trades or labels.
PASS cannot become a feature table, model input, confidence score, strategy
rule, backtest result, alert, risk rule, or execution instruction under this
proposal. FAIL is preserved and retires the setup on this dataset; it cannot be
rescued by tuning or selective exclusion.

Even PASS does not authorize training. Training remains blocked until a
separate prospective data/partition decision supplies at least three canonical
contract months and all no-look-ahead, validation, and OOS controls. Private
payloads remain outside Git and language-model context.

## 23. Acceptance, promotion, rollback, and STOP conditions

Documentation acceptance requires exactly `24` sequential numbered sections,
exactly `48` sequential cases, exact one-file scope, zero formatting error,
exact staged SHA-256, cache-disabled focused/full regression PASS, and an
independent semantic/structural/cached-diff audit.

This document may be promoted only to a local documentation commit. Before
commit, rollback is deletion of this exact file. After commit, rollback is a
bounded revert; history rewriting and evidence deletion are forbidden.

STOP on any input, hash, identity, API, version, baseline, calendar, timezone,
partition, result, count, reason, serialization, output-root, or scope drift;
private mutation; OOS contact; nondeterminism; exception leakage; silent
sorting/exclusion; parameter or gate change; feature/label/model/training/PnL/
integration/trading work; unrelated staging; private execution without exact
later authority; or push without exact later authority.

## 24. Final decision and next single task

The exact decision is:

`READY_FOR_EXPLICIT_PHASE_B_SWEEP_RECLAIM_PRIVATE_RUN_AUTHORIZATION`

After this document passes independent audit and is committed locally, STOP
before push and before private execution. The next single task, only under a
separate exact authorization, is push preflight/publication of this one-file
documentation commit. Only after that publication and another exact execution
authorization may the two-run atomic private feasibility procedure in Sections
11–20 execute. Training, OOS, integration, and trading remain forbidden.
