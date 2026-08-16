# GC Futures Phase-B NY-AM Opening-Range Breakout Continuation Private-Run Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-OPENING-RANGE-BREAKOUT-CONTINUATION-PRIVATE-RUN-PROPOSAL-V1`.
- Decision date: `2026-08-16`.
- Binding implementation commit: `24eddfe44b4b8d7e379bdcc3f302d3c8b30b9906`.
- Binding parent proposal commit: `3e4bff17a03131f6ed02c923a0e55e8d49326875`.
- Classification: documentation-only private-run preflight and deterministic STOP record.
- Current decision: `STOP_PRIVATE_RUN__PREDETERMINED_THREE_CONTRACT_GATE_FAILURE`.

This record does not authorize or perform a private run. It binds the accepted private input,
committed analyzer, prospective publication contract, and governing feasibility gates, then records
that one mandatory PASS gate is already impossible on the immutable accepted dataset. No Python,
test, private-data, training, integration, execution, or remote publication authority follows.

## 2. Decision summary

The committed V1 analyzer and its exact `48` public logical cases are regression-clean. The accepted
private Phase-A development bundle is immutable, Git-ignored, reproducible, `VALID`, and contains
`17,404` development bars in `133` canonical segments with zero OOS bars. It is technically
sufficient to reconstruct observations and canonical Kill-zone evidence without reading OOS data.

The governing feasibility proposal nevertheless requires complete candidates from at least `3`
canonical GC contracts. Direct inspection of the accepted canonical dataset metadata proves that
all `133` segments contain only `GCJ26-COMEX` and `GCM26-COMEX`: exactly `2` contracts. The four raw
source exports do not override the canonical dataset boundary; `GCG26-COMEX` and `GCQ26-COMEX`
produce no accepted canonical segment in this dataset and cannot be counted or synthesized.

Therefore the maximum attainable contract count is `2`, which is below the immutable PASS minimum
of `3`. This is a predetermined feasibility FAIL. Running the analyzer cannot change that fact and
would create avoidable private artifacts. V1 is retired exactly as the governing proposal requires;
its threshold, window, geometry, horizon, and gate may not be revised to rescue it.

## 3. Verified repository baseline

At this record's baseline:

- `HEAD` and local `origin/main` equal
  `24eddfe44b4b8d7e379bdcc3f302d3c8b30b9906`;
- the commit subject is `feat(analysis): add GC NY-AM opening-range feasibility`;
- its exact parent is `3e4bff17a03131f6ed02c923a0e55e8d49326875`;
- the committed implementation scope is exactly the source, test, and checkpoint in Section 9;
- fresh focused evidence is `48 passed in 5.34s` and fresh full explicit public regression evidence
  is `2394 passed in 22.00s`, both with pytest cache disabled;
- the accepted private input root in Section 6 exists and remains Git-ignored;
- the prospective private output root in Section 15 is absent;
- no Phase-B private run, feature/label build, training, OOS access, integration, model use, or
  trading action has occurred; and
- three pre-existing unrelated untracked proposal documents remain outside this task and untouched:
  `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`,
  `docs/gc_futures_real_data_input_binding_change_proposal.md`, and
  `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Any baseline drift before acceptance is a STOP condition. It is not authority to edit an unrelated
file, refresh data, or reinterpret the gate.

## 4. Exact documentation-only scope

The only path authorized by this task is:

`docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_private_run_change_proposal.md`

This file may be audited, corrected, staged by its exact path, and committed locally. `git add .`, a
broad pathspec, source or test edits, private-data writes, external fixtures, run outputs, generated
cache, integration, and push are forbidden. Every other tracked and untracked path remains frozen.

## 5. Authority, global freeze, and no-trading boundary

The user authorized preparation of this proposal through a local commit only. That authorization
does not extend to private execution, data repair, parameter search, feature/label production,
training, model inference, OOS access, strategy selection, backtest promotion, package exports,
runtime wiring, alerts, orders, position management, stage of other files, or push.

The analyzer remains a standalone diagnostic. Neither Codex nor a local or remote language model
may inspect raw private market rows, change this decision, select trades, or treat this proposal as
trading authority. The global code freeze remains active outside the exact file in Section 4.

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
Missing, extra, renamed, duplicated, reordered manifest members, byte drift, or hash drift is
`INVALID` and cannot be repaired in place. Filesystem enumeration order is not evidence.

## 7. Dataset, seed, control, and contract-count binding

The accepted binding is exactly:

- binding version
  `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural seed ID
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- dataset status `VALID`, `17,404` development bars, `133` segments, and zero OOS bars;
- first/last trade dates `2026-02-23` / `2026-05-22`;
- exactly `64` unique accepted development trade dates;
- exact roll trade date `2026-04-01`;
- instrument/timeframe/tick size `GC` / `5M` / exact Decimal `0.1`;
- all `133` segment partitions exactly `DEVELOPMENT`;
- exact canonical segment contracts, in set form,
  `{GCJ26-COMEX, GCM26-COMEX}`; and
- Candidate Evidence status `UNKNOWN`, zero candidates, `113` segment results, with exact reason
  and blocking reason `a swept pool has a truncated confirmation horizon`.

The raw input binding names four source exports (`GCG26`, `GCJ26`, `GCM26`, and `GCQ26`), but raw
source presence is not canonical segment eligibility. Only contracts represented by immutable
accepted dataset segments may satisfy the Phase-B contract-count gate. No source-only contract,
empty contract, future segment, synthetic roll, or external export may be counted.

## 8. Accepted continuity lineage and calendar binding

The accepted cross-segment continuity output is lineage-only evidence with artifact-set identity
`5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`. It is not an analyzer input,
candidate source, outcome source, or substitute third contract. Its `UNKNOWN` result and
`CANONICAL_CONTROL_UNKNOWN` token cannot be upgraded or repaired here.

The accepted calendar binding is exactly:

- calendar version
  `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`;
- split-session calendar digest
  `5f70052e27655a95fdad6aa69f546a6c84a28743bb6635ca4f55d015c39cad6d`;
- Kill-zone calendar digest
  `dd16b5734f4dfe54a54c47aa1889302abf92102e6478459b98a8e642732f88f3`;
- runtime timezone-data version `2026.2`;
- exchange/source zones `America/New_York` / `Asia/Tokyo`; and
- official calendar evidence hashes
  `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`,
  `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`, and
  `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

The split-session and Kill-zone tuples remain independently reconstructed and ordered. Calendar
repair, current-year substitution, inferred holiday rules, broker evidence, or timezone fallback is
forbidden.

## 9. Exact committed implementation and dependency hashes

The decision stops unless every bound tracked artifact matches:

| Artifact | SHA-256 |
|---|---|
| governing feasibility proposal | `75A049329783501E779AFBA1F198A7BA2BA7C25C7986C601F9D64A7A5BDCA291` |
| `analysis/gc_ny_am_opening_range_breakout.py` | `6515964B6F8A0C76CD48D9F8E6071947600FA939DC6FAFBD85C000C9A2B478F8` |
| `tests/test_gc_ny_am_opening_range_breakout.py` | `654ED7080B0F07FF16FAE38366C0C2274EEC24C6EA3C20368D6D831EAE606BD0` |
| implementation checkpoint | `D6C61940A2FA5AA8993A75A6E0580C570B591432983CFE161DF91C133C554025` |
| Phase-A accepted-input proposal | `91E6E2A4983B1A1075FF5ED4AB6A5C05F312F4197F2A4FE52841922DA578FC07` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

The proposal-file hash for this record is computed after final semantic, structural, scope, and
formatting audit and is bound by its local commit. No hash mismatch may be waived.

## 10. Exact public API, types, exports, and version binding

The committed version is exactly `GC-NY-AM-OPENING-RANGE-BREAKOUT-V1`. Exact public exports are the
version constant, `GCNYAMIdentityKind`, `GCNYAMOutcomeType`,
`GCNYAMOpeningRangeObservation`, `GCNYAMOpeningRange`, `GCNYAMOpeningRangeCandidate`,
`GCNYAMOpeningRangeOutcome`, `GCNYAMOpeningRangeManifest`, `GCNYAMOpeningRangeResult`,
`make_gc_ny_am_opening_range_breakout_id`, and
`analyze_gc_ny_am_opening_range_breakout` in that order.

Identity kinds are exactly `OBSERVATION`, `OPENING_RANGE`, `CANDIDATE`, `OUTCOME`, and `MANIFEST`.
Outcome types are exactly `EXTENSION_FIRST`, `INVALIDATION_FIRST`, `TIMEOUT`,
`SAME_BAR_AMBIGUOUS`, `INCOMPLETE`, and `INVALID`. All six public dataclasses remain frozen with the
exact committed fields, annotations, order, and defaults.

The only analyzer call is keyword-only and exact:

```python
analyze_gc_ny_am_opening_range_breakout(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    observations: tuple[GCNYAMOpeningRangeObservation, ...] | None,
    split_session_calendar_entries: tuple[GCSplitSessionCalendarEntry, ...] | None,
    kill_zone_calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    kill_zone_result: KillZoneResult | None,
    requested_trade_dates: tuple[date, ...] | None,
) -> GCNYAMOpeningRangeResult
```

The identity builder remains the exact keyword-only signature and defaults locked in Section 11 of
the governing proposal and the committed implementation hash. A future validator, if ever separately
authorized, must compare `inspect.signature` against that literal contract before any invocation.
Alternate parameters, positional calls, filesystem discovery, hidden inputs, and caller-selected
thresholds or windows are forbidden.

## 11. Exact prospective reconstruction contract

Were a run otherwise eligible, each of two fresh executions would reconstruct all public objects
from the same eight immutable source files without shared mutable objects:

1. validate the exact input scope, bytes, hashes, manifest order, and artifact-set identity;
2. reconstruct `GCDatasetBuildResult` and its immutable nested segments/bars exactly;
3. reconstruct the split-session calendar from the accepted normalized-calendar bytes;
4. reconstruct the Kill-zone calendar and each segment's canonical `KillZoneResult` from accepted
   Candidate Evidence without rerunning, enriching, or mutating Kill-zone detection;
5. derive requested dates as the exact increasing tuple of all `64` unique accepted segment trade
   dates, never from wall clock, raw filenames, or calendar-only dates;
6. project exactly one `GCNYAMOpeningRangeObservation` per canonical dataset bar, preserving dataset
   order, exact segment ordinal/ID/contract/index, integer-tick OHLC, integer volume, UTC close,
   exact close-minus-five-minutes open, and canonical context/snapshot IDs;
7. recompute every foreign and public identity from available immutable fields; and
8. call the exact analyzer once.

No observation may be silently sorted, excluded, filled, duplicated, interpolated, relabeled, or
reconciled from a raw export outside the canonical dataset. In this accepted bundle, however,
Section 14 stops before these reconstruction and analyzer steps because the immutable contract gate
already fails.

## 12. Dataset and observation admissibility gate

An otherwise eligible execution would require a `VALID` dataset with non-null manifest, exact
dataset ID, development-only requested evidence, zero OOS contact, strict canonical ordering, and
complete one-to-one observation reconciliation. Every bar must be fully closed, timezone-aware,
integer-tick, and satisfy `low_tick <= open_tick, close_tick <= high_tick`; boolean ticks are
forbidden and volume must be a nonnegative integer.

Segment ordinals, bar indices, and normalized open/close timestamps must be strictly increasing in
accepted dataset order. Duplicate, missing, reordered, cross-segment, cross-contract, unreconciled,
or malformed evidence is `INVALID`. A determinably later malformed group preserves only strictly
prior immutable evidence and promotes nothing from the failing group or after it. None of these
rules can manufacture the missing third contract.

## 13. Calendar, Kill-zone, and no-look-ahead admissibility gate

Each requested date would require exact split-session and Kill-zone coverage. Source, formation,
and horizon observations must reference canonical `NEW_YORK_AM`, `VERIFIED`, matching-trade-date
contexts and snapshots with recomputed IDs. Context timestamps equal bar-open timestamps; snapshot
order mirrors observation order. Missing context is `UNKNOWN` only after all independently
determinable supplied evidence validates; malformed evidence is `INVALID` and has higher
precedence.

Exactly six bars opened at `07:00` through `07:25 America/New_York` form the range. Candidate opens
are restricted to `[07:30, 09:00)`. Outcomes use only the next exact `12` later closed bars in the
same canonical segment. The formation bar cannot be used as an outcome bar. No future bar, OOS row,
outcome, PnL, wall-clock `as_of`, or external calendar may affect an earlier identity or candidate.

## 14. Deterministic preflight feasibility decision gate

The immutable feasibility PASS predicate is conjunctive:

1. at least `40` complete candidates;
2. at least `40` distinct eligible dates;
3. at least `10` bullish and `10` bearish complete candidates;
4. at least `3` canonical GC contracts represented by complete candidates;
5. `100%` identity/count/status/reason/byte reproducibility across two fresh runs;
6. zero silent exclusion; and
7. a complete requested-date funnel.

The accepted canonical dataset's complete contract set has cardinality `2`. Candidate generation
cannot escape that set. Consequently predicate 4 is false before any analyzer execution, and the
conjunction cannot become true. This is an exact deterministic FAIL, not `UNKNOWN` and not a reason
to run parameter discovery.

Per the governing proposal, FAIL retires V1 without threshold, window, geometry, horizon, or gate
rescue. Reducing `3` to `2`, counting raw-only contracts, importing a different dataset, merging
rolls, adding a synthetic contract, or creating a V1.1 under this authority is forbidden.

## 15. Prospective private output root

The prospective root had been:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_opening_range_breakout_continuation_feasibility_v1/`

It is absent and must remain absent under this decision. No task-specific temporary directory may
be created. If the root appears, stop without opening, modifying, merging, or deleting it and report
the unexpected state. It may not be nested in or overwrite the accepted input root.

## 16. Prospective output artifact set

Had every preflight gate passed under a separate explicit execution authorization, the final root
would have contained only:

1. `input_binding_NON_PROMOTABLE_FEASIBILITY.json`;
2. `opening_range_result_NON_PROMOTABLE_FEASIBILITY.json`;
3. `artifact_manifest_NON_PROMOTABLE_FEASIBILITY.json`;
4. `validation_report_NON_PROMOTABLE_FEASIBILITY.md`; and
5. `README_NON_PROMOTABLE_FEASIBILITY.md`.

This five-file set is recorded solely to close the design contract; none may now be created. Raw
bars, source exports, dataset or Candidate Evidence copies, charts, prompts, notebooks, caches,
features, labels, outcomes for training, models, and PnL material were never permitted.

## 17. Deterministic serialization contract

The prospective machine-readable format is locked as UTF-8 without BOM, LF endings, one terminal
newline, sorted JSON object keys, compact separators `(",", ":")`, and `ensure_ascii=True`.
Ordered tuples serialize as ordered arrays; dictionaries never encode causal order. Timestamps are
UTC ISO-8601 microseconds with terminal `Z`, dates are `YYYY-MM-DD`, finite Decimals use canonical
fixed text with every zero as `0.0`, enums use exact `.value`, inner identities are lowercase
64-hex, and outer artifact-member SHA-256 values are uppercase 64-hex.

Clock time, host paths, file timestamps, locale, object addresses, random values, Python `repr`,
pickle, hash iteration, exception text, and filesystem enumeration order are forbidden content and
identity inputs. This contract creates no authority to serialize an artifact now.

## 18. Prospective input binding and artifact manifest

A prospective input binding would have recorded this proposal ID/hash, implementation commit and
hashes, exact eight input members, artifact-set/dataset/seed/continuity identities, all calendar
versions/digests, runtime timezone evidence, config, exact public signatures, requested-date tuple,
contract set, and explicit false flags for OOS, feature/label, training, integration, promotion, and
trading.

The artifact manifest would have excluded itself from its member list, bound the other four names,
byte lengths and hashes, exact five-file total scope, public result status/reasons/counts, analyzer
call count, independent-run equality, and a deterministic artifact-set identity. Because the
preflight gate fails, no input binding or manifest is created and no fabricated result is retained.

## 19. Atomic publication and rollback

An eligible future run would require two new task-specific temporary directories under the private
parent, two independent reconstructions from immutable bytes, exactly one analyzer call per run,
object equality, machine-byte equality, complete identity recomputation, and only then an atomic
move of one validated directory to an absent final root.

This proposal reaches STOP before temporary-directory creation. Rollback is therefore limited to
removing this documentation file before local commit. After local commit, rollback requires a
bounded revert commit; accepted private inputs, negative evidence, Git history, and unrelated
worktree state may not be deleted or rewritten.

## 20. Independent validation, status, and prefix boundary

Exact public status precedence remains
`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`. `SAME_BAR_AMBIGUOUS` is a terminal outcome type
inside an otherwise canonical result; it is not permission to downgrade an invalid run. A public
manifest may exist only for complete final `VALID` or `NONE`, never for `INVALID`, `AMBIGUOUS`, or
`UNKNOWN`.

The independent audit must recompute the accepted input scope/hashes, dataset contract set, bound
tracked hashes, public signatures, proposal structure, Git scope, and output-root absence. Prefix
invariance applies only at a complete requested-date boundary and a strictly later complete append.
Same-effective append, partial horizon, historical insertion, calendar repair, reorder, roll,
dataset mutation, or contract-set mutation is ineligible and requires a new reviewed hypothesis;
none can alter this V1 decision.

## 21. Inline synthetic exact 48-case preflight matrix

This record locks exactly these sequential logical cases. Parameterization may expand checks but
must not change the count of `48` logical cases.

1. Missing accepted input root stops before deserialization.
2. Unexpected prospective final root stops without opening or overwrite.
3. Exact eight-file input names, lengths, hashes, order, and artifact-set identity reconcile.
4. Missing, extra, duplicate, renamed, drifted, or reordered manifest member stops.
5. Binding commit, parent proposal, source, test, checkpoint, or dependency drift stops.
6. Runtime tzdata is exact `2026.2` and both required IANA zones are available.
7. Dataset, seed, and continuity artifact-set identities reconcile exactly.
8. Dataset is `VALID`, has a non-null manifest, and contains zero OOS bars.
9. Dataset has exactly `17,404` development bars and `133` development segments.
10. Dataset date span, `64` unique requested dates, and roll date reconcile exactly.
11. Candidate Evidence remains `UNKNOWN` with `113` segment results and zero candidates.
12. Candidate Evidence reason/blocking token drift is not repaired or suppressed.
13. Exact GC / 5M / Decimal `0.1` configuration and timezone fields reconcile.
14. Split-session calendar version, digest, order, and official source hashes reconcile.
15. Kill-zone calendar digest/version reconstructs independently from split-session entries.
16. Calendar repair, inferred holiday, broker substitution, or current-year substitution stops.
17. Dataset bars reconstruct as immutable, closed, integer-tick/integer-volume evidence.
18. Observations project one-to-one from canonical bars with exact five-minute open/close moments.
19. Missing, duplicate, reordered, forked, cross-segment, or unreconciled observation is invalid.
20. Kill-zone contexts and snapshots recompute exactly and preserve causal order.
21. Exact six source bars at `07:00` through `07:25` create one immutable positive-width range.
22. Missing, partial, substituted, cross-contract, or zero-width range promotes nothing.
23. Candidate window is start-inclusive/end-exclusive `[07:30, 09:00)`.
24. Bullish qualification requires close at least exactly one tick above range high.
25. Bearish qualification requires close at least exactly one tick below range low.
26. Boundary equality and wick-only breaks do not qualify.
27. Earliest canonical qualifying close wins; later breakouts cannot replace it.
28. Formation/outcome collision is rejected without later rehabilitation.
29. Bullish and bearish target/invalidation geometry mirrors exactly.
30. Outcome horizon uses only the next `12` later closed bars in the same segment.
31. Extension-first and invalidation-first outcomes use earliest canonical hit.
32. Same-bar target/invalidation hit emits exact `SAME_BAR_AMBIGUOUS` outcome.
33. No hit after all `12` bars emits exact `TIMEOUT`.
34. Truncated horizon is `UNKNOWN` and promotes no outcome.
35. Final precedence remains INVALID over AMBIGUOUS over UNKNOWN over VALID over NONE.
36. Later malformed evidence preserves only strictly prior immutable public objects.
37. Every OBSERVATION, OPENING_RANGE, CANDIDATE, OUTCOME, and MANIFEST ID recomputes.
38. Public manifest exists only for complete final VALID or NONE.
39. Exact ordered count funnel and reason vocabulary reject free-text or lexical reordering.
40. Accepted canonical segment contract set is exactly `{GCJ26-COMEX, GCM26-COMEX}`.
41. Raw-only `GCG26-COMEX` and `GCQ26-COMEX` are not counted as canonical candidate contracts.
42. Maximum attainable canonical contract count is exactly `2`.
43. Mandatory PASS minimum remains exactly `3` canonical contracts.
44. Two-contract maximum versus three-contract minimum deterministically fails before execution.
45. Threshold reduction, synthetic contract, cross-roll merge, alternate dataset, or V1 rescue stops.
46. Failure creates no temporary or final artifact and leaves all private input bytes immutable.
47. Exact one-file Git scope, unrelated untracked state, and no-push boundary reconcile.
48. Feature, label, outcome learning, PnL, model, training, OOS, integration, Git push, and trading
    surfaces remain unused.

## 22. No feature, model, promotion, or trading authority

The predetermined FAIL cannot become a candidate, feature, label, model input, confidence score,
strategy rule, backtest result, alert, risk rule, or trade. It does not authorize a local model to
inspect private payloads or decide a replacement hypothesis. No Phase-B feature/label proposal may
start from V1, because the governing PASS prerequisite is false.

Negative evidence is retained as research governance. It may be summarized at manifest level, but
the raw private bundle stays outside Git and outside any model context. The existing diagnostic
implementation remains committed and regression-tested as a falsifiable research artifact; it is
not integrated into runtime.

## 23. Acceptance, promotion, rollback, and STOP conditions

Documentation acceptance requires exactly `24` sequential numbered sections, exactly `48`
sequential logical cases, exact one-file scope, zero formatting error, exact SHA-256 at staging,
cache-disabled focused/full regression PASS, and independent semantic/structural/diff audit.

Promotion and private execution are forbidden. Stop immediately on any input, hash, identity,
version, API, baseline, contract-count, calendar, result, or scope drift; output-root appearance;
private-data mutation; OOS contact; nondeterminism; exception leakage; threshold/window/geometry/
horizon/gate change; feature/label/training/model/integration/trading work; unrelated staging; or push
without exact later authority.

No local code correction is authorized by this record. If an audit finds that the contract count is
not exactly two, this proposal fails and must be corrected or withdrawn within its exact one-file
scope; it does not silently switch to running the analyzer.

## 24. Final decision and next single task

The exact decision is:

`STOP_PHASE_B_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1_PRIVATE_RUN_AND_RETIRE_V1`

The immutable accepted dataset cannot satisfy the governing three-contract PASS gate, so the
private run is neither necessary nor authorized. After this exact document passes independent
audit and is committed locally, STOP before push and before any other work. The next single task,
only after separate user direction, is a documentation-only selection decision for a genuinely
testable next hypothesis using the already accepted development evidence; it must not weaken or
rescue V1 and must not begin training.
