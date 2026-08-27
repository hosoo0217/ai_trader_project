# GC Futures Phase A Candidate Cross-Session Confirmation-Horizon Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CANDIDATE-CROSS-SESSION-CONFIRMATION-HORIZON-V1`.
- Proposal date: `2026-08-27`.
- Proposal status: `DOCUMENTATION_ONLY / CONTRACT_GAP_CONFIRMED / IMPLEMENTATION_NOT_AUTHORIZED`.
- Current canonical arm: `SEGMENT_LOCAL_INDUCEMENT_V1`.
- Proposed first bounded arm: `ADDITIVE_PENDING_HORIZON_DIAGNOSTIC_V1`.
- Candidate promotion, feature/label build, model training, final-OOS access,
  integration, paper trading, broker routing, and live authority: `NOT GRANTED`.

This proposal records one verified orchestration defect and the smallest safe
contract change required before any cross-session resolver may be designed. It
does not change detector output, execute private data, or claim trading edge.

## 2. Decision summary

The accepted Phase A dataset contains a terminal sweep in one complete GCM26
session and strictly later observations in the immediately following complete
same-contract session. The canonical candidate builder nevertheless returns
`UNKNOWN` because it invokes the Inducement analyzer separately for each
segment. The standalone Inducement analyzer is behaving correctly for the
tuple it receives: its next-three-closed-bar horizon is incomplete.

The defect therefore is not established as missing raw data and is not a
defect in the locked V1 Inducement result semantics. It is a missing immutable
pending-horizon evidence boundary between the standalone detector and a future
cross-session candidate resolver.

The first safe change is additive only: expose exact pending sweep/horizon
evidence through a new versioned diagnostic API while preserving the existing
`analyze_inducements()` signature and byte-level result semantics. A later,
separately proposed resolver may consume that evidence; this proposal does not
authorize it.

## 3. Binding repository baseline

This proposal binds to repository commit
`1a6b164cbd989ef30b8c1d87451a2069ac4d899c`. Local `HEAD` and
`origin/main` both matched that commit when the proposal began.

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `tests/test_gc_candidate_evidence_builder.py` | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `analysis/gc_cross_segment_continuity.py` | `1F59432FD738699015DDD92DC8AEB437D1B3DADE7EF96B1BB816245F05DB34D7` |
| `tests/test_gc_cross_segment_continuity.py` | `9E666DE295F7F538E81CFE772A1B436E625F5D9644E5136C045C049E458205C4` |
| `smc/inducement.py` | `57DA49BE7C99DF9385610749446566323865676817FF8C44D8F8D3868C8C633F` |
| `tests/test_inducement.py` | `129B5751BFB00E78AC4B8D4C71811A35AFB2D55EDEB356A668FC098F5201D850` |
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| accepted candidate proposal | `A0E35BF5A7F4EC451DF7898223FA0467C3FA36AA2F775008C0FB7C4D62F38941` |
| accepted continuity proposal | `90130C122C1D07C861B24E350BA8D294E79287E0FE02C4D1ADC01EC49CD15F82` |

Dependency or baseline drift before implementation is a STOP condition.

## 4. Intended use and data-quality gate

The intended use is development-only diagnosis of an incomplete positional
confirmation horizon. The evidence grain is one qualifying sweep plus the zero
to two strictly later closed observations already supplied to the analyzer.

| Quality dimension | Required evidence | Failure risk |
|---|---|---|
| Completeness | Exact sweep dependencies and every supplied post-sweep observation are present | A true missing dependency could be mislabeled as a boundary gap |
| Uniqueness | Canonical source IDs and the pending-horizon identity are unique | Forked evidence could be silently selected |
| Validity | Types, identities, lifecycles, moments, prices, and ordering reconcile | Malformed evidence could become candidate authority |
| Integrity | Pending evidence references only canonical immutable inputs | A resolver could enrich or rewrite detector history |
| Timeliness | Evidence is first-known only at the final supplied observation | Future bars could leak into an earlier decision |
| Leakage | Outcomes, labels, returns, MFE/MAE, OOS, LLM judgment, and PnL are unavailable | Research selection could become outcome-conditioned |

Failure of any determinable quality dimension is explicit `INVALID`; it is not
repaired, dropped, or converted to `UNKNOWN` to improve coverage.

## 5. Exact documentation-only scope

This change creates only:

`docs/gc_futures_phase_a_candidate_cross_session_confirmation_horizon_change_proposal.md`

No Python, test, fixture, private artifact, dataset, manifest, dependency,
configuration, package export, runtime, trace, strategy, risk, execution, or
integration file is changed. The three pre-existing unrelated untracked
proposal files remain outside scope and untouched.

## 6. Authority and global freeze

Global code freeze remains active. This document authorizes no implementation.
Its only effect is to define a future bounded exception that still requires a
separate explicit implementation authorization.

The future first implementation may add diagnostic evidence only. It may not:

- change `Inducement`, `InducementSnapshot`, or `InducementResult`;
- change the signature or behavior of `analyze_inducements()` or
  `make_inducement_id()`;
- concatenate or renumber dataset segments;
- recompute, mutate, enrich, or reclassify accepted detector outputs;
- emit a GC candidate, feature, label, score, order, or trading decision; or
- read final-OOS payloads or execute a private run.

## 7. Verified defect evidence

The accepted development-only source result contains 133 canonical segments.
The candidate result stops after 113 promoted segment results with status
`UNKNOWN`, zero candidates, reason
`a swept pool has a truncated confirmation horizon`, and blocking reason
`next three closed bars are incomplete`.

The failing source segment is ordinal 113, GCM26 trade date `2026-04-27`.
Its final three observations are:

| Segment-local index | UTC timestamp | Role |
|---:|---|---|
| segment index 273 | `2026-04-27T20:50:00Z` | pre-sweep observation |
| segment index 274 | `2026-04-27T20:55:00Z` | qualifying sweep/reclaim observation |
| segment index 275 | `2026-04-27T21:00:00Z` | first available confirmation-horizon observation |

The immediately following source segment is ordinal 114 with the same GCM26
contract/source domain. Its first three observations are `22:05Z`, `22:10Z`,
and `22:15Z`. Thus strictly later observations exist in the accepted source;
the current analyzer call does not receive them.

The private evidence hashes used only for this diagnosis are:

| Private artifact | SHA-256 |
|---|---|
| accepted dataset build result | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| candidate evidence result | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| continuity feasibility result | `347564415B12B1ABFCF24CFA6024BC78F504725FFFE876963926ABBCB56351FD` |

These facts establish one exact boundary case only; they do not establish
general cross-session candidate validity.

## 8. Root-cause classification

`analysis/gc_candidate_evidence_builder.py` deliberately projects and analyzes
each segment independently. On the failing segment it supplies only one closed
bar after the sweep. `smc/inducement.py` correctly treats fewer than three
supplied strictly later positions as pending and returns `UNKNOWN`.

The existing cross-segment continuity layer is reference-only feasibility
evidence. It preserves the canonical control result and is not authorized to
reclassify it. It also does not expose the private `_Sweep` object needed to
bind a later confirmation horizon.

Root cause: `MISSING_IMMUTABLE_PENDING_HORIZON_CONTRACT`.

Not established as root cause:

- `RAW_BAR_MISSING`;
- `CALENDAR_COVERAGE_MISSING`;
- `INDUCEMENT_V1_SEMANTIC_DEFECT`;
- `FVG_IDENTITY_DEFECT`; or
- `CANDIDATE_SELECTION_DEFECT`.

## 9. Immutable accepted input contracts

The future diagnostic analyzer accepts the same exact top-level evidence
collections as `analyze_inducements()`:

- immutable canonical `DealingRangeSnapshot` tuple;
- immutable canonical `LiquidityMapSnapshot` tuple;
- immutable canonical `EqualLiquidityPool` tuple;
- immutable confirmed `DealingRangeStructureEvent` tuple;
- immutable canonical `FairValueGap`, `FairValueGapTransition`, and
  `FairValueGapSnapshot` tuples; and
- immutable fully closed integer-tick `InducementObservation` tuple.

All existing foreign identity, lifecycle, provenance, event/FVG suffix,
ordering, timestamp-awareness, integer-tick, and malformed-input validation
remains authoritative. Inputs are exact tuples or `None`; silent coercion,
sorting, repair, deduplication, or truncation is forbidden.

## 10. Exact pending-horizon eligibility and ineligibility

A pending horizon is eligible for diagnostic emission only when all of these
conditions hold:

1. the complete supplied evidence validates canonically;
2. an exact qualifying sweep/reclaim exists under the locked bullish or bearish
   mirror semantics;
3. no qualifying same-direction Structure Event plus causally linked FVG is
   found in the supplied strictly later positions;
4. the supplied tuple contains zero, one, or two positions after that sweep;
5. the missing positional count is exactly `3 - available_count`; and
6. the first-known moment is the final supplied observation moment.

It is ineligible when three later positions are already supplied, the sweep is
not qualifying, the evidence is malformed, or the relevant sequence is already
confirmed. A completed no-confirmation horizon is `NONE`, not pending. A valid
confirmed sequence remains solely within the existing V1 analyzer.

## 11. Missing public evidence boundary

The current public `InducementResult` intentionally exposes only confirmed
`Inducement` objects, snapshots, reasons, and blocking reasons. It does not
expose the pending sweep identity, its canonical dependency references, the
available horizon prefix, or the first-known moment. The internal `_Sweep`
dataclass is private and must not be imported by an analysis module.

Therefore a cross-session resolver cannot safely infer the missing state from
reason strings or reconstruct it by scanning bars. Reason-string parsing,
private-class imports, duplicated sweep logic, and fabricated identities are
forbidden. If the additive contract below cannot be implemented without
changing V1 output, implementation must STOP.

## 12. Exact proposed additive public contract

The first future implementation adds these module-level public names only:

- `SMC_V2_INDUCEMENT_PENDING_HORIZON_VERSION` with exact value
  `"SMC_V2_INDUCEMENT_PENDING_HORIZON_V1"`;
- frozen `InducementPendingHorizon`;
- frozen `InducementPendingHorizonResult`;
- `make_inducement_pending_horizon_id()`; and
- `analyze_inducement_pending_horizons()`.

`InducementPendingHorizon` exact fields, in order, are:

| Field | Type |
|---|---|
| `pending_horizon_id` | `str` |
| `direction` | `SMCV2Direction` |
| `active_range_lineage_id` | `str` |
| `active_range_snapshot_id` | `str` |
| `liquidity_map_snapshot_id` | `str` |
| `external_target_classification_id` | `str` |
| `internal_pool_classification_id` | `str` |
| `internal_pool_id` | `str` |
| `sweep_index` | `int` |
| `sweep_timestamp` | `datetime` |
| `sweep_extreme_tick` | `int` |
| `reclaim_close_tick` | `int` |
| `available_confirmation_indices` | `tuple[int, ...]` |
| `available_confirmation_timestamps` | `tuple[datetime, ...]` |
| `missing_confirmation_bar_count` | `int` |
| `first_known_index` | `int` |
| `first_known_timestamp` | `datetime` |
| `reason_token` | `str` |

No field has a default. `reason_token` has the only accepted value
`"NEXT_THREE_CLOSED_BARS_INCOMPLETE"`. Available index and timestamp tuples
have equal length zero through two, preserve supplied positional order, and
contain every observation after the sweep. Missing count is one through three
and must equal three minus tuple length.

`InducementPendingHorizonResult` exact fields, types, and defaults are:

| Field | Type | Default |
|---|---|---|
| `status` | `SMCV2PrimitiveStatus` | required |
| `pending_horizons` | `tuple[InducementPendingHorizon, ...]` | `()` |
| `reasons` | `tuple[str, ...]` | `()` |
| `blocking_reasons` | `tuple[str, ...]` | `()` |

The evidence is immutable point evidence with no lifecycle, transition, or
reclassification API.

## 13. V1 compatibility and no semantic reclassification

For every accepted or malformed input, existing calls to
`analyze_inducements()` and `make_inducement_id()` must produce exactly the same
return value or exception type before and after the future implementation.

The new analyzer may share internal validation and sweep discovery only if the
refactor is behavior-preserving. It must not add fields to existing public
dataclasses, change existing enum values, change reason strings, alter ordering,
or expose `_Sweep`.

An emitted pending horizon remains `UNKNOWN` evidence. It is not a confirmed
Inducement, a candidate, or permission to inspect future segments.

## 14. Exact keyword-only public API

```python
def make_inducement_pending_horizon_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction | None = None,
    active_range_lineage_id: str | None = None,
    active_range_snapshot_id: str | None = None,
    liquidity_map_snapshot_id: str | None = None,
    external_target_classification_id: str | None = None,
    internal_pool_classification_id: str | None = None,
    internal_pool_id: str | None = None,
    sweep_index: int | None = None,
    sweep_timestamp: datetime | None = None,
    sweep_extreme_tick: int | None = None,
    reclaim_close_tick: int | None = None,
    available_confirmation_indices: tuple[int, ...] | None = None,
    available_confirmation_timestamps: tuple[datetime, ...] | None = None,
    missing_confirmation_bar_count: int | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    reason_token: str | None = None,
) -> str:
    ...

def analyze_inducement_pending_horizons(
    *,
    instrument: str,
    timeframe: str,
    dealing_range_snapshots: tuple[DealingRangeSnapshot, ...] | None,
    liquidity_map_snapshots: tuple[LiquidityMapSnapshot, ...] | None,
    equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    fair_value_gaps: tuple[FairValueGap, ...] | None,
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...] | None,
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] | None,
    observations: tuple[InducementObservation, ...] | None,
) -> InducementPendingHorizonResult:
    ...
```

All parameters are exact keyword-only parameters. The analyzer parameters have
no defaults. The builder accepts only `identity_kind="PENDING_HORIZON"`; any
other kind raises only `TypeError` or `ValueError`.

## 15. Exact identity schema and exports

The pending-horizon identity payload contains exactly:

`version`, `identity_kind`, normalized uppercase `instrument`, normalized
uppercase `timeframe`, `direction.value`, all six canonical source identity
fields, `sweep_index`, normalized UTC `sweep_timestamp`, `sweep_extreme_tick`,
`reclaim_close_tick`, ordered `available_confirmation_indices`, ordered
normalized UTC `available_confirmation_timestamps`,
`missing_confirmation_bar_count`, `first_known_index`, normalized UTC
`first_known_timestamp`, and `reason_token`.

The ID is lowercase SHA-256 over canonical compact ASCII JSON with sorted keys.
Booleans are rejected as integers. Timestamps must be timezone-aware. Hashes
must be canonical lowercase 64-character hexadecimal strings. Nested malformed
values fail with only `TypeError` or `ValueError`; no exception leaks.

The five names in Section 12 are included in `smc.inducement.__all__`. Package
root exports and all other modules remain unchanged.

## 16. Deterministic discovery and ordering

Pending horizons are discovered from the same validated sweep groups and exact
bullish/bearish mirror rules used by V1. No second, weaker sweep definition is
allowed.

Output order is exact:

`(first_known_index, normalized first_known_timestamp, sweep_index, normalized sweep_timestamp, direction.value, internal_pool_id, pending_horizon_id)`.

Distinct independent horizons are emitted deterministically. Exact duplicate
identity evidence is `INVALID`. Opposing distinct pending horizons with the
same first-known moment are `AMBIGUOUS`; earlier immutable horizons are
preserved and the ambiguous group is not promoted.

## 17. Atomic processing and immutable prior evidence

One equal effective-moment group is validated and promoted atomically. A
determinably later malformed group returns `INVALID` while preserving strictly
prior valid pending-horizon evidence byte-for-byte. The failing group and all
later evidence are not promoted. A malformed required field whose effective
moment cannot be trusted returns `INVALID` without requiring a trustworthy
prefix.

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

For this diagnostic API, emitted pending horizons normally produce `UNKNOWN`;
complete valid inputs with no pending horizon produce `NONE`. `VALID` is
reserved by the shared status vocabulary and has no reachable V1 branch.

## 18. First-known, no-look-ahead, and prefix invariance

`first_known_index` and `first_known_timestamp` equal the final supplied
observation moment at which the positional shortfall is determinable. They may
not be backdated to the sweep.

Appending a complete group with an effective moment strictly later than every
existing effective moment must preserve all earlier pending-horizon bytes and
IDs. Same-effective append, historical insertion, reordering, repair, source
identity mutation, or collection replacement is not an eligible prefix
comparison.

The analyzer may inspect only supplied evidence. It may not open the next
dataset segment, infer future bars from timestamps, or consult outcomes, OOS,
labels, models, humans, or an LLM.

## 19. Exact cross-session boundary required later

A future resolver, under a separate proposal, may consider a pending horizon
only when all of these are proven by immutable references:

- immediately adjacent canonical source segments;
- same instrument, timeframe, contract, source domain, calendar version, and
  development partition;
- both segments complete and valid;
- the receiving first observation is strictly later than the source final
  observation;
- no raw source interval required by the canonical calendar is missing;
- the existing boundary feasibility assessment is `ELIGIBLE`;
- exactly the first missing positional observations are consumed; and
- receiving Structure Event/FVG evidence reconciles to those exact observation
  moments under the existing causal suffix rules.

Segment-local indices must never be treated as globally monotonic. Timestamps,
source segment IDs, and immutable identities must bind the boundary.

## 20. Forbidden resolver shortcuts

This proposal does not authorize a resolver. Any later resolver is forbidden
to:

- concatenate, renumber, or silently sort segment bars;
- parse V1 reason text to reconstruct a sweep;
- import private `_Sweep` or duplicate its logic in `analysis/`;
- turn every terminal `UNKNOWN` into an eligible boundary;
- reuse confirmation evidence from a non-adjacent or different-contract
  segment;
- recompute or rewrite accepted detector objects;
- promote evidence when the required Structure Event/FVG source moments cross
  an unproven boundary; or
- replace the canonical segment-local control arm.

If a future resolver requires a stronger state-carry, index normalization, or
foreign-identity contract than specified here, that requirement is a new STOP
condition and requires a new documentation-only proposal.

## 21. Exact 48-case future acceptance matrix

The future first implementation keeps exactly 48 numbered logical cases.
Parameterization may increase collected tests without changing this count.

| Case | Locked coverage |
|---:|---|
| 1 | Exact empty complete inputs return `NONE` with no pending evidence |
| 2 | Any required top-level tuple `None` returns `UNKNOWN` after independently determinable supplied evidence validates |
| 3 | Malformed supplied counterpart outranks missing-context `UNKNOWN` with `INVALID` |
| 4 | Bullish qualifying sweep with zero later bars emits one pending horizon and missing count three |
| 5 | Bearish qualifying sweep with zero later bars mirrors Case 4 |
| 6 | Bullish sweep with one later bar emits exact ordered available prefix and missing count two |
| 7 | Bearish sweep with one later bar mirrors Case 6 |
| 8 | Two later bars emit exact ordered prefix and missing count one |
| 9 | Three later bars with no confirmation are complete and produce no pending horizon |
| 10 | Existing valid confirmed sequence produces no pending horizon and leaves V1 confirmed output unchanged |
| 11 | Non-qualifying sweep produces no pending horizon |
| 12 | Boundary-equality reclaim and exact one-tick sweep remain locked |
| 13 | Proximal-only or wrong-side liquidity evidence does not create pending evidence |
| 14 | Active external target and confirmed internal opposite-side pool remain required |
| 15 | Latest pre-group range and liquidity-map selection remains exact |
| 16 | Pool lineage, lifecycle, classification, and snapshot identities reconcile canonically |
| 17 | Structure Event identity/type/provenance validation remains fail-closed |
| 18 | FVG GAP/TRANSITION/SNAPSHOT history remains complete and canonical |
| 19 | Event/FVG source observations reconcile exactly and shorter sequence is a positional suffix |
| 20 | Opaque non-null displacement ID is preserved without claiming unavailable recomputation |
| 21 | Available index/timestamp tuples reject unequal lengths |
| 22 | Available tuples reject length three or greater and non-tuple values |
| 23 | Missing count rejects zero, four, booleans, fractions, and mismatch with available length |
| 24 | First-known moment equals final supplied observation moment |
| 25 | Backdated, future-dated, naive, or mismatched first-known timestamp is rejected |
| 26 | Sweep moment, extreme tick, and reclaim tick reconcile exactly to source observation |
| 27 | Every pending-horizon identity required field is individually required |
| 28 | Unknown or non-`PENDING_HORIZON` identity kinds are rejected; the builder exposes no second schema |
| 29 | Common instrument, timeframe, version, and identity-kind sensitivity is exact |
| 30 | Direction and all six canonical source-ID sensitivities are exact |
| 31 | Sweep moment/geometry and available-prefix sensitivities are exact |
| 32 | Missing-count, first-known-moment, and exact reason-token sensitivities are exact |
| 33 | Hash shape, lowercase hexadecimal validation, nested malformed values, and exception containment are exhaustive |
| 34 | Repeated identical inputs produce identical pending objects, order, and IDs |
| 35 | Distinct independent same-direction horizons have deterministic output ordering |
| 36 | Exact duplicate or forked same-source pending evidence is `INVALID` |
| 37 | Opposing distinct same-first-known group is `AMBIGUOUS` with atomic no-promotion |
| 38 | Determinably later malformed observation preserves strictly prior pending evidence and returns `INVALID` |
| 39 | Determinably later malformed range/map/pool evidence preserves strictly prior evidence when its moment is trustworthy |
| 40 | Determinably later malformed event/FVG/history evidence preserves strictly prior evidence when its moment is trustworthy |
| 41 | Unknowable malformed effective moment returns `INVALID` without a trustworthy-prefix requirement |
| 42 | Exact analyzer and builder keyword-only names, kinds, annotations, and defaults are asserted |
| 43 | Exact public frozen dataclass fields, order, annotations, defaults, constant, and module exports are asserted |
| 44 | Existing V1 dataclasses, signatures, enum values, reason strings, and exports remain byte-for-byte compatible |
| 45 | Strictly later complete append preserves prior pending bytes and IDs |
| 46 | Same-effective append, historical insertion, reorder, repair, and source mutation are explicitly prefix-ineligible |
| 47 | No package export, candidate builder import, private `_Sweep` export, resolver, integration, OOS, or trading surface is added |
| 48 | Focused/full regression, exact scope, artifact hashes, line/byte counts, formatting, and checkpoint reconciliation pass |

## 22. Reserved first implementation exact 3-path scope

After a separate explicit authorization, the first implementation scope is
reserved to exactly:

- `smc/inducement.py`
- `tests/test_inducement.py`
- `docs/smc_v2_inducement_pending_confirmation_horizon_checkpoint.md`

No external fixture is allowed. `analysis/gc_candidate_evidence_builder.py`,
the continuity module, shared primitives, other SMC modules, package exports,
private data, configuration, and integration files remain frozen.

The future cross-session resolver is not part of this reservation. It requires
a later documentation-only proposal after the pending contract passes its own
independent audit.

## 23. Rollback, promotion, and STOP conditions

Rollback is exact removal of the additive pending-horizon names and restoration
of the three reserved paths to their pre-task bytes. No migration or accepted
artifact rewrite is allowed.

Promotion from documentation to implementation requires:

- unchanged baseline hashes or an independently reviewed rebase;
- exact test-first implementation within the three reserved paths;
- all 48 logical cases and full regression passing;
- byte-identical V1 behavior demonstrated by differential tests;
- exact scope, identity, formatting, and checkpoint audits; and
- explicit user authorization.

STOP immediately if implementation requires changing V1 results, importing a
private class outside the module, fabricating source identities, weakening
validation, reading private/OOS data, adding a candidate resolver, changing
package exports, or touching any fourth path.

Even a passing pending-horizon implementation grants no authority for private
runs, candidate promotion, feature/label build, training, OOS, integration, or
trading.

## 24. Final decision and next single task

Decision: the verified terminal `UNKNOWN` is an orchestration contract gap, not
proof of missing raw data and not authority to alter the standalone Inducement
semantics. The safe next step is the additive pending-horizon diagnostic
contract defined here.

Next single task, only after explicit authorization: test-first implementation
and independent audit of the exact three paths in Section 22. No later resolver
or research stage may start in the same task.
