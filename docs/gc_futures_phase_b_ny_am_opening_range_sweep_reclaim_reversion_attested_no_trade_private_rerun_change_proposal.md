# GC Futures Phase B NY-AM Sweep/Reclaim Attested-No-Trade Private-Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-B-NY-AM-SWEEP-RECLAIM-ATTESTED-NO-TRADE-PRIVATE-RERUN-V4`.
- Decision date: `2026-08-17`.
- Binding repository baseline and corrected implementation commit:
  `d72e80eaea77af7449dc07db90a374a0ca7af6b0`.
- Governing attested-no-trade proposal:
  `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_attested_no_trade_coverage_correction_proposal.md`,
  SHA-256 `6A1DE55F8597A17512B55D3F5E89186455C01CFEEFEA36742C6AA91114F6F9EA`.
- Corrected implementation version:
  `GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V2`.
- Classification: documentation-only corrected private-rerun contract.
- Decision: `READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_SEPARATE_PRIVATE_RERUN_AUTHORIZATION`.

This record authorizes no execution by itself. It supersedes the stale V3
refreshed-run contract only for future execution selection; historical
proposals and failed evidence remain immutable.

## 2. Corrected implementation outcome

The V2 implementation distinguishes canonical attested no-trade opening-range
gaps from malformed and unavailable evidence. A qualified known gap emits
`NONE` with `ATTESTED_NO_TRADE_OPENING_RANGE`, increments
`ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES`, and promotes no range,
candidate, or outcome from that date. Malformed evidence remains `INVALID`;
unprovable or truncated evidence remains `UNKNOWN`.

The final ordering correction places the new funnel key immediately after
`CALENDAR_ELIGIBLE_TRADE_DATES` and the new reason token immediately after
`SESSION_INELIGIBLE`. It changes no count, status, identity field, public API,
or V2 version. Accepted evidence is `59 passed in 7.13s` focused and `2453
passed in 23.77s` full regression. This proposal's cache-disabled acceptance
audit independently reproduced `59 passed in 6.87s` focused and `2453 passed
in 23.94s` full regression.

## 3. Historical failed-run preservation

The preceding V2 private execution was deterministic and byte-identical but
failed closed as `INVALID`: `63` complete opening ranges from `64` requested
dates, `54` candidates, `54` outcomes, and reasons including
`INVALID_OPENING_RANGE`, `NO_SWEEP_RECLAIM`, and
`AMBIGUOUS_SWEEP_RECLAIM`. It is diagnostic failure evidence, not a result to
rewrite, relabel, merge, or promote.

The V2 temporary and final roots are absent. Their absence does not erase the
committed correction-proposal record. The corrected execution uses new V3
roots so no V2 result can be mistaken for corrected V2-code evidence.

## 4. Exact documentation-only scope

The present task may create and accept only:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_attested_no_trade_private_rerun_change_proposal.md`

Only this exact path may be corrected, independently audited, staged,
cached-audited, and locally committed. Source, tests, private artifacts,
fixtures, integration, and broad pathspecs are forbidden. Push and private
execution require later, separate exact authorization.

## 5. Authority and no-trading boundary

A later authorized run is a development-only structural-feasibility
measurement. It may read the exact immutable roots below, reconstruct public
frozen dataclasses, call the committed analyzer once per fresh run, and write
only the locked V3 temporary/final roots.

It may not tune a threshold, select favorable dates, access OOS, create
features or labels, fit or invoke a model, calculate PnL, risk, entry, or exit,
integrate runtime behavior, emit a trading decision, or place an order. No
local or remote language model may receive raw private market rows.

## 6. Exact immutable Phase A input root

The accepted root is:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

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

The ordered artifact-set identity is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
Candidate Evidence is lineage-only and cannot replace the complete Kill-zone
dependency.

## 7. Exact complete Kill-zone dependency root

The only admissible downstream root is:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1/`

| File | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | `1486` | `7768A255FEB5F3981CD3D43CC7CBFD517CA66C43F7E6927300F2FE5B12DAE4E9` |
| `input_binding_DEVELOPMENT_ONLY.json` | `4231` | `A6045EF6379E95CD749E31710FDA4D5293D61EBF879CAF0AB4F0FE9B978B22B9` |
| `kill_zone_dependency_DEVELOPMENT_ONLY.json` | `56515215` | `8E3494BEE9BEBB8EA42E8880F87DED9603D6011AC84719867F21CC5974720112` |
| `README_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `387` | `77C99B29646B65A3C1507AA9A94697E65B2E1EBA40B0781E2C7339559D0D6B31` |
| `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `643` | `6CB7062EBECF85F84F6C3072277D4646507107E01C5491BF66E312F2E18BDFB6` |

Its artifact-set identity is
`089e38c945f679674853282b6b730a038d936f3ed2eeaa2f23fe123636df6f05`.
It remains `COMPLETED_NON_PROMOTABLE`, `complete=true`, with `133` segments,
`17,404` bars, `64` requested dates, status counts `101 VALID` / `32 NONE`,
`9,839` contexts, `9,839` snapshots, `2,276` `NEW_YORK_AM` contexts, and zero
OOS access.

## 8. Dataset, calendar, and partition binding

Both roots must reconcile to dataset ID
`2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`,
structural-seed ID
`73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`,
and continuity identity
`5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`.

The immutable partition has `17,404` bars, `133` ordered segments, and exact
`64` requested dates from `2026-02-23` through `2026-05-22`. Contracts are
exactly `GCJ26-COMEX` and `GCM26-COMEX`; roll date is `2026-04-01`;
instrument/timeframe/tick size are `GC` / `5M` / `0.1`; source/exchange zones
are `Asia/Tokyo` / `America/New_York`; runtime tzdata normalizes to `2026.2`;
OOS membership and access are zero.

## 9. Exact tracked implementation hashes

Execution is admissible only at baseline
`d72e80eaea77af7449dc07db90a374a0ca7af6b0` with these bytes:

| Path | SHA-256 |
|---|---|
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `75FFD671FE09FB3BF91D31658E3D990BAA0418578AD3EB503BC417ED4601AF28` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `578A2F0E733ADDE0698E6782621A89B6644C3AC4B66486EA3C205D10440DAF91` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md` | `5F5E340CAC396A4053F0D3231F1ABB931F748C3E24F068EF655B803DE589EE96` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |

Any commit, tracked-byte, API, export, enum, dataclass, or V2-version drift is
a hard `STOP` requiring a new reviewed proposal.

## 10. Exact public analyzer boundary

Each fresh execution makes exactly one semantic call to:

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
`make_gc_ny_am_sweep_reclaim_id()`. No repair, exclusion, attestation override,
threshold, window, or filesystem parameter may be introduced.

## 11. Exact reconstruction boundary

The runner reconstructs immutable bars, split-session calendar, complete
Kill-zone results, contexts, and snapshots in canonical segment order. It
projects an observation only for a closed five-minute bar whose New York open
is in `[07:00, 09:55)` and close is in `[07:00, 10:00)`. The `09:55` open /
`10:00` close bar stays dataset evidence but is not an observation.

Every projected member reconciles one-to-one at its close moment to a
`NEW_YORK_AM`, `VERIFIED`, same-trade-date context and mirrored snapshot. No
missing bar is synthesized; no retained incomplete Candidate Evidence object
may fill, filter, or replace complete dependency evidence.

## 12. Attested-no-trade provenance gate

An absent opening-range member qualifies only through the committed V2 gate:
canonical dataset/manifest/raw binding, exact six expected New York moments,
complete reconciliation of supplied members, canonical adjacent gap lineage,
exact five-minute arithmetic, and no duplicate, fork, substitution,
cross-lineage evidence, or OOS need.

Trade date `2026-03-31`, segment ordinal `74`, segment ID
`09c8048907719ffe99a3de7c6402dcf36e88561eff20a6589b7fc8384b591b6`,
is the locked discriminator: only the `07:20` opening-range member exists and
five members are acquisition-attested absent. It must be counted as known
non-evaluable; it cannot become a synthetic range or an exclusion from the
requested-date denominator.

## 13. Identity, funnel, and reason reconciliation

Every public identity is recomputed with the V2 builder and exhaustive
required/forbidden schemas. The count funnel includes
`ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES` immediately after
`CALENDAR_ELIGIBLE_TRADE_DATES`. The reason vocabulary includes
`ATTESTED_NO_TRADE_OPENING_RANGE` immediately after `SESSION_INELIGIBLE`.

Ordered funnel/reason tuples, occurrence counts, object histories, effective
moments, exact uppercase-kind/lowercase-hash IDs, manifest ID, and serialized
bytes must reconcile. Hash order is never used as chronology.

## 14. Structural and status semantics

The opening range is exactly six observations opened at `07:00` through
`07:25`, first known at `07:30`. Candidate opens are `[07:30, 09:00)`.
One-tick sweep, same-bar reclaim, midpoint equality, earliest selection,
mirror direction, and both-boundary ambiguity remain locked.

Formation is excluded from outcome evidence. Outcome is the next exact twelve
later compatible observations. Earliest midpoint reach, close-through
invalidation, `SAME_BAR_AMBIGUOUS`, `TIMEOUT`, and truncated-horizon `UNKNOWN`
remain unchanged. Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

## 15. Deterministic execution and decision gates

Before output creation, the runner proves the baseline, all hashes, exact root
members, cross-root identities, public API/version, runtime timezone, V3-root
absence, Git exclusion, and zero OOS/network/repair need. Run A and run B each
reconstruct independently and call the analyzer exactly once.

Publication eligibility requires object-equal and byte-identical complete
public `VALID` or `NONE` results. `INVALID`, `AMBIGUOUS`, or `UNKNOWN` publishes
no final root. For an eligible result, hypothesis `PASS` additionally requires
at least `30` complete candidates, `24` eligible dates, `10` candidates in
each direction, `8` candidates for each contract, a complete requested-date
funnel with zero silent exclusion, and zero forbidden authority contact.
Failure of any conjunct publishes immutable hypothesis `FAIL`; no rescue or
tuning is permitted.

## 16. Exact V3 temporary and final roots

Only these absent paths may be created by a later authorized execution:

- `private_data/sierra_chart/.tmp-gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v3-run-a/`;
- `private_data/sierra_chart/.tmp-gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v3-run-b/`;
- `private_data/sierra_chart/gc_2026_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_v3/`.

All three are absent at proposal time and must be absent at execution start.
V1/V2 roots remain historical/reserved and unusable. Unexpected existence,
reparse/symlink ambiguity, nesting, or path drift stops without overwrite,
merge, deletion, or repair.

## 17. Exact five-file output scope

Each fresh run may write exactly:

- `input_binding_NON_PROMOTABLE_FEASIBILITY.json`;
- `sweep_reclaim_result_NON_PROMOTABLE_FEASIBILITY.json`;
- `artifact_manifest_NON_PROMOTABLE_FEASIBILITY.json`;
- `validation_report_NON_PROMOTABLE_FEASIBILITY.md`;
- `README_NON_PROMOTABLE_FEASIBILITY.md`.

Raw rows, copied inputs, charts, prompts, notebooks, caches, features, labels,
splits, models, PnL, risk, and integration artifacts are forbidden. The
manifest excludes itself and binds the other four names, bytes, hashes,
result/status/reasons/counts, hypothesis decision, two-run equality, and
artifact-set identity.

## 18. Serialization and input-binding schema

Machine files use UTF-8 without BOM, LF, one terminal newline, sorted keys,
compact JSON separators, and `ensure_ascii=True`. Tuples remain causal arrays;
datetimes are UTC `Z`; dates are ISO; integers are decimal; Decimal midpoint is
canonical `.0`/`.5` with zero as `0.0`; enums use `.value`.

The input binding records every governing proposal/commit/hash, both immutable
roots and artifact-set identities, historical failed-run lineage, dataset,
seed, continuity, calendar, timezone, partition and analyzer contracts, exact
requested dates/contracts, call counts, and explicit false flags for OOS,
features, labels, training, models, PnL, integration, promotion, network, and
trading.

## 19. Atomic publication and rollback

Run A and run B use fresh independent deserialization. A separate validation
pass recomputes all identities, counts, reasons, serialized bytes, hashes, and
scope. Only two byte-identical validated sets are eligible; one temporary root
may be atomically renamed to the absent final root after every gate passes.

On failure, no final root is promoted. A task-created temporary root may be
removed only after exact absolute-path and parent-containment verification.
Inputs and unrelated state are never modified. A published final root is
immutable; correction requires a new proposal and new root.

## 20. Atomicity, prior evidence, and prefix invariance

A complete trade-date group promotes atomically. A malformed group promotes
nothing from itself or later; strictly prior complete public evidence remains
byte-exact. An attested no-trade group promotes no range/candidate/outcome but
does not erase independent complete groups. Pending evidence cannot promote.

Prefix invariance applies only at a complete requested-date boundary followed
by strictly later complete append across both roots. Same-effective append,
partial horizon, historical insertion, repair, reorder, roll/calendar/tzdata
mutation, attestation mutation, or dependency replacement is ineligible.

## 21. Inline synthetic exact 48-case execution matrix

1. Missing Phase A root stops before deserialization.
2. Missing complete Kill-zone root stops before deserialization.
3. Existing V3 temporary or final root stops without mutation.
4. Missing, extra, renamed, reordered-manifest, size-, or hash-drifted Phase A member stops.
5. Missing, extra, renamed, reordered-manifest, size-, or hash-drifted dependency member stops.
6. Baseline, proposal, tracked hash, API, export, dataclass, enum, or V2-version drift stops.
7. Cross-root dataset, calendar, timezone, segment, date, contract, or OOS mismatch stops.
8. Dataset remains `VALID`, development-only, `17,404` bars and `133` segments.
9. Requested dates remain exact `64`, ordered, and span `2026-02-23` through `2026-05-22`.
10. Contracts and roll remain `GCJ26-COMEX`, `GCM26-COMEX`, and `2026-04-01`.
11. Retained incomplete Candidate Evidence remains lineage-only and never substitutes.
12. Complete dependency contains all `133` unique segment results in canonical order.
13. Dependency counts remain `101 VALID`, `32 NONE`, `9,839` contexts/snapshots, `2,276` NY-AM.
14. Dependency `INVALID`, `AMBIGUOUS`, `UNKNOWN`, missing suffix, or count drift stops.
15. Every context/snapshot identity and ordered mirrored history recomputes.
16. Split-session and Kill-zone calendars reconcile exact versions, digests, dates, and statuses.
17. Runtime timezone and normalized tzdata `2026.2` must be available exactly.
18. Observations are exactly closed five-minute opens in `[07:00, 09:55)` with closes before `10:00`.
19. The `09:55` open / `10:00` close bar remains dataset-only evidence.
20. Every projection reconciles one-to-one to same-moment NY-AM context/snapshot evidence.
21. Duplicate, missing, extra, reordered, cross-segment, cross-contract, or wrong-date projection is `INVALID`.
22. Six exact `07:00` through `07:25` observations create a positive-width range.
23. The canonical 2026-03-31 five-member gap emits attested no-trade `NONE` and no range.
24. Corrupt, contradictory, or substituted gap lineage remains `INVALID_OPENING_RANGE`.
25. Unavailable or truncated unproved gap remains `INCOMPLETE_OPENING_RANGE` `UNKNOWN`.
26. Attested date stays in the denominator and exact funnel/reason occurrence counts reconcile.
27. Funnel key order places attestation immediately after calendar eligibility.
28. Reason order places attestation immediately after session ineligibility.
29. Candidate window remains exact `[07:30, 09:00)`.
30. Bullish and bearish one-tick sweep/reclaim geometry mirrors exactly.
31. Equality qualifies; wick-only, insufficient, outside, and delayed reclaim do not.
32. Both-boundary formation is atomic `AMBIGUOUS`; earliest valid candidate wins otherwise.
33. Formation observation is excluded and horizon is the next exact twelve observations.
34. Earliest midpoint and close-through events use exact mirrored geometry.
35. Same-bar target/invalidation emits `SAME_BAR_AMBIGUOUS`.
36. Twelve no-event observations emit `TIMEOUT`; truncation remains `UNKNOWN`.
37. Final precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
38. Failing-group no-promotion preserves strictly prior complete bytes.
39. Public manifest exists only for complete final `VALID` or `NONE`.
40. Both executions call the analyzer once and are object- and byte-identical.
41. Serialization covers UTC, dates, enums, integers, Decimal `.0`/`.5`, zero, and IDs.
42. Output contains exactly five locked files and manifest excludes itself.
43. Candidate/date gates require at least `30` and `24` respectively.
44. Direction/contract gates require `10` each direction and `8` each contract.
45. Eligible gate failure publishes immutable hypothesis `FAIL` without rescue.
46. Eligible gate success records `PASS` but grants no downstream authority.
47. Strictly later complete append is prefix-invariant; repair/reorder/version/attestation mutation is ineligible.
48. OOS, feature, label, model, training, PnL, integration, network, push, and trading contact remain forbidden.

Parameterization may expand instances but cannot alter this exact logical count
or add a decision gate.

## 22. Independent post-run audit

An independent audit must reread disk bytes and recompute proposal/baseline
bindings, both input roots, public identities, ordered funnel/reasons, object
counts, result status, serialization, artifact hashes, two-run equality,
hypothesis decision, exact output scope, Git exclusion, and all zero-authority
claims without reusing runner memory.

It must prove that no private input, raw row, failed historical evidence,
requested date, tracked file, OOS path, or unrelated untracked path changed.

## 23. Acceptance, promotion, and STOP conditions

Documentation acceptance requires exact one-file scope, exactly `24`
sequential numbered sections, exactly `48` sequential cases, formatting PASS,
full-content and cached-diff audit, exact hash, cache-disabled focused/full
regression PASS, independent semantic audit, exact-path staging, and local
commit. This task promotes only the proposal, not the private hypothesis.

STOP on any input, hash, API, version, calendar, timezone, partition, count,
status, reason, identity, serialization, or root drift; private mutation; OOS
contact; nondeterminism; exception leakage; silent sort/exclusion/repair;
parameter/gate change; feature/label/model/training/PnL/integration/trading;
broad staging; execution without separate authority; or push without separate
explicit privacy/export authorization.

## 24. Final bounded decision and next single task

The final decision is:

`READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_EXPLICIT_V3_PRIVATE_RERUN_AUTHORIZATION`

After independent audit and local commit of this exact document, `STOP` before
push and execution. The next single task is push preflight/publication of the
one-file proposal commit under separate GitHub privacy/export authority. Only
after publication may a separate exact authorization permit the atomic V3
two-run procedure. Training, OOS, feature/label build, integration, and trading
remain forbidden.
