# GC Futures Phase A Closure and Phase B Research-Direction Decision

## 1. Decision status

- Record ID: `GC-PHASE-A-CLOSURE-PHASE-B-DIRECTION-V1`.
- Decision date: `2026-08-16`.
- Classification: documentation-only research-governance decision.
- Phase A state: `CLOSED_NEGATIVE`.
- Phase A V1 setup state: `RETIRED_NO_RESCUE`.
- Phase A training readiness: `NOT_READY`.
- Phase B direction: `SELECTED_NOT_IMPLEMENTED`.
- Phase B training readiness: `NOT_READY`.
- OOS access: forbidden.
- Runtime, paper, broker, risk, and execution authority: none.
- Global code freeze: active outside this exact file.

This record closes Phase A without erasing or weakening its negative evidence and
selects exactly one new Phase B research hypothesis. It does not claim a trading
edge and does not authorize Python, tests, fixtures, private-data mutation,
feature or label generation, model fitting, OOS access, integration, paper
trading, live trading, staging, commit, or push by itself.

## 2. Technical summary

Phase A completed its permitted engineering sequence. The accepted dataset and
detector evidence are reproducible, but the locked V1 Candidate Evidence
hypothesis produced zero canonical candidates. A separately authorized
cross-segment continuity feasibility run proved that reference-only dependency
continuity can be reconstructed deterministically across eligible standard
boundaries; it still produced no admissible Candidate Evidence and left the
canonical control `UNKNOWN`.

The correct conclusion is not to train on an empty candidate population and not
to weaken V1 after seeing the result. Phase A and its V1 setup are therefore
closed and retired.

Phase B selects one deliberately simpler and independently falsifiable setup:

`GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1`

The setup uses the first six fully closed five-minute bars of the New York AM
window to form an immutable opening range, then observes the first later
one-tick close breakout. It does not require Equal Liquidity, Dealing Range,
Liquidity Map, Inducement, FVG, Volume Profile, Order Block, Mitigation Block,
Breaker Block, CRT, or legacy order-flow evidence for candidate eligibility.
The reduced dependency surface is a prospective simplification, not a repair of
V1.

## 3. Exact repository and evidence baseline

This decision is prepared against repository baseline:

`7e23163b21a77f86ac1b27075bf44c92617f5957`

The exact evidence bindings are:

| Evidence | SHA-256 |
|---|---|
| Phase A cross-segment continuity negative-outcome decision | `624E615255019A5F5B6C2F5D11B77594B62493D6ED1E636941B178B29F27704F` |
| Phase A next-hypothesis selection decision | `77554406D75B81E279409D1D46F3AC44C89FAD6FC08D010D98DA543016B4181E` |
| GC AI strategy and training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| Cross-segment continuity implementation | `1F59432FD738699015DDD92DC8AEB437D1B3DADE7EF96B1BB816245F05DB34D7` |
| Kill-zone implementation | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |

The accepted private Phase A continuity artifact-set identity remains:

`5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`

Its source dataset ID remains:

`2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`

Private files remain Git-ignored and are neither copied nor summarized beyond
already accepted aggregate evidence.

## 4. Phase A result accepted as immutable negative evidence

The accepted Phase A development evidence contains:

- `17,404` fully closed development bars;
- `133` immutable segments;
- `113` promoted complete segment results in the canonical Candidate Evidence
  run;
- `0` canonical candidates;
- `112` assessed cross-segment boundaries;
- `40` eligible standard boundaries;
- `71` partial boundaries;
- `1` contract boundary;
- `162` immutable receiving groups in the continuity feasibility run;
- final continuity status `UNKNOWN`;
- exact reason and blocker `CANONICAL_CONTROL_UNKNOWN`;
- a null public continuity manifest; and
- `promotion_allowed=false`, `feature_label_allowed=false`,
  `training_allowed=false`, and `integration_allowed=false`.

Two fresh continuity executions were object-equal and byte-equal. These facts
establish reproducible engineering behavior. They do not establish
profitability, candidate sufficiency, or training readiness.

## 5. Phase A closure rationale

Phase A asked whether the locked
`LIQUIDITY_SWEEP_RECLAIM_STRUCTURE_FVG` setup could produce canonical,
point-in-time candidates from the accepted development coverage. The answer is
`NO`.

The final failure is methodological evidence, not an implementation crash:

- role-qualified internal-liquidity sweeps existed;
- a small number obtained strictly later structural confirmation;
- two obtained exact event/FVG causal linkage;
- neither retained the required active external range through confirmation;
- continuity did not make either sequence canonical; and
- the final higher-precedence `UNKNOWN` remained intact.

Further relaxation would select rules after observing failure. Phase A has
therefore reached its stop condition and is closed.

## 6. What the result does and does not establish

The result establishes that the exact V1 setup is not promotable on the accepted
Phase A development evidence. It also establishes that the continuity analyzer
is technically feasible and deterministic but not sufficient to rescue V1.

The result does not establish that:

- GC Futures has no exploitable structure;
- every SMC or order-flow diagnostic is useless;
- a different prospectively specified setup must fail;
- a profitable strategy exists;
- more complex models would solve candidate absence; or
- OOS, paper, or live evidence may be opened.

Zero candidates cannot be converted into positive or negative model labels, and
there is no valid Phase A training table.

## 7. Retired V1 boundary

The following V1 eligibility chain is retired on the accepted Phase A coverage:

1. active external Dealing Range target;
2. confirmed internal opposite-side Equal Liquidity pool;
3. exact sweep and reclaim;
4. strictly later BOS/CHOCH within the next three closed bars;
5. causally bound qualifying Fair Value Gap; and
6. external-range retention through confirmation.

The retirement is immutable. Phase B may not:

- drop only the failed active-range-retention condition;
- widen the three-bar confirmation window;
- carry V1 state across partial, roll, holiday, or contract boundaries;
- reinterpret a terminated range as active;
- add manual or language-model candidates;
- open OOS to find examples; or
- retain the V1 name while changing its semantics.

Any future audit must treat such a change as a prohibited V1 rescue.

This record supersedes only the V1 setup selection and its Phase A resume
direction in `GC_AI_CONTEXTUAL_SETUP_SELECTION`. It does not supersede the
general safety, point-in-time, chronological partition, purge/embargo,
reproducibility, model hierarchy, abstention, risk-separation, failed-evidence,
or no-trading-authority controls in the GC AI strategy and training decision.
Existing Phase A candidate and feature/label implementations remain immutable
historical diagnostics with no Phase B eligibility or training authority.

## 8. Selected Phase B hypothesis

The one selected hypothesis is:

`GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1`

Research statement:

> On an eligible GC trade date, after a complete six-bar New York AM opening
> range is known, the first strictly later fully closed five-minute bar that
> closes at least one tick beyond that range defines a continuation candidate.
> The hypothesis is that one full opening-range extension is reached before a
> close through the opposite opening-range boundary within the next twelve
> fully closed five-minute bars.

This is one setup family with mirrored bullish and bearish directions. It is not
a portfolio of SMC, CRT, order-flow, breakout, and mean-reversion strategies.

## 9. Independence from the retired V1 hypothesis

Phase B is a new hypothesis rather than a V1 rescue because:

- its source geometry is a fixed clock-defined opening range, not an internal
  liquidity pool;
- its target geometry is one opening-range extension, not an active external
  Dealing Range target;
- its candidate does not require Inducement, Liquidity Map, Dealing Range,
  Equal Liquidity, structure-event, or FVG eligibility;
- it has no cross-segment detector-state carry;
- it selects the first clock-bounded close breakout, not the earliest surviving
  member of the V1 causal chain; and
- it will receive a new identity, candidate, feature, label, dataset, and model
  schema family if later authorized.

Shared use of GC bars, UTC timestamps, `America/New_York`, deterministic
identities, chronological partitions, and no-look-ahead controls is governance
reuse, not hypothesis reuse.

## 10. Exact instrument, timeframe, and calendar scope

Phase B V1 is restricted to:

- instrument family: COMEX Gold Futures `GC` outright contracts only;
- timeframe: one canonical five-minute bar stream only;
- prices: exact integer ticks;
- timestamps: timezone-aware UTC, converted using fixed
  `America/New_York` rules and an exact recorded runtime timezone-data version;
- bars: fully closed only;
- trade dates: caller-supplied versioned canonical GC calendar evidence;
- eligible session state: explicitly open and not early-closed before required
  source or label completion;
- candidate window: New York AM only; and
- data purpose: development feasibility until separately promoted.

Spot gold, XAUUSD, CFDs, options, micro-gold, synthetic continuous prices,
multi-timeframe duplicates, developing bars, and bar-summary order-flow proxies
are forbidden.

## 11. Immutable required input boundary

A future proposal must define frozen caller-supplied records for:

- canonical GC five-minute observations containing at least contract identity,
  trade date, sequential index, UTC bar-open timestamp, UTC bar-close timestamp,
  integer-tick OHLC, integer nonnegative volume, and fully-closed state;
- versioned GC calendar entries containing trade date, canonical session open,
  canonical session close, session state, early-close state, timezone name, and
  timezone-data version; and
- immutable canonical Kill-zone context and snapshot evidence proving exact
  `NEW_YORK_AM` membership for every required source, candidate, and label bar.

Inputs must be tuples, ordered without silent sorting, unique, internally
reconciled, and complete for every effective group being assessed. Foreign
detector outputs are reference-only. No future builder may repair, enrich,
recompute, or mutate them.

## 12. Exact opening-range construction

For one eligible trade date, the opening range uses exactly six fully closed
bars whose local bar-open times are:

`07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and `07:25`

The range becomes first-known only at `07:30:00 America/New_York`, after all six
bars are closed.

Definitions:

- `opening_range_high_tick`: maximum source-bar `high_tick`;
- `opening_range_low_tick`: minimum source-bar `low_tick`;
- `opening_range_width_ticks`:
  `opening_range_high_tick - opening_range_low_tick`;
- width must be a positive integer; and
- the ordered six source identities and their exact timestamps are immutable
  identity evidence.

A missing, duplicate, malformed, nonconsecutive, cross-contract,
cross-trade-date, non-closed, session-ineligible, or zero-width source group is
fail-closed and produces no candidate.

## 13. Exact candidate sequence and direction

Candidate assessment begins with bars whose local bar-open timestamps are in
the start-inclusive/end-exclusive interval `[07:30, 09:00)`. This leaves twelve
strictly later five-minute bars available before the exact `10:00` New York AM
end when the calendar remains open.

The first qualifying bar in canonical order is selected:

- bullish: `close_tick >= opening_range_high_tick + 1`;
- bearish: `close_tick <= opening_range_low_tick - 1`.

The candidate is first-known at that bar's exact close timestamp. Later
qualifying breakouts on the same trade date are ignored, not ranked by outcome.
At most one candidate exists per trade date.

The formation bar is ineligible if it has already touched the locked extension
target or traversed the opposite opening-range boundary. Such a formation has
outcome information before candidate first-known time and is rejected as
`FORMATION_OUTCOME_COLLISION`, not relabeled from later evidence.

## 14. Immutable candidate geometry

For bullish candidates:

- broken boundary: `opening_range_high_tick`;
- target: `opening_range_high_tick + opening_range_width_ticks`;
- invalidation boundary: `opening_range_low_tick`.

For bearish candidates:

- broken boundary: `opening_range_low_tick`;
- target: `opening_range_low_tick - opening_range_width_ticks`;
- invalidation boundary: `opening_range_high_tick`.

Opening-range boundaries, width, target, invalidation boundary, direction,
source-bar identities, formation-bar identity, trade date, contract, instrument,
timeframe, timezone version, and first-known moment are immutable. No later bar,
detector state, label, price outcome, or model score may revise them.

## 15. Deterministic candidate selection and identity direction

A later proposal must define a new versioned `OPENING_RANGE` identity and a new
versioned `CANDIDATE` identity. Their payloads must contain every immutable field
needed to recompute Sections 12 through 14. Hash lexical order may never replace
chronology.

Required deterministic selection order is:

1. normalized trade date;
2. canonical contract order;
3. candidate bar index;
4. normalized candidate close timestamp; and
5. direction only after the effective moment is equal.

Exact duplicates collapse only after full payload equality. Same-effective
nonidentical source groups, contradictory directions, forked identities, or
multiple nonduplicate bars for one canonical index are `AMBIGUOUS` or `INVALID`
according to independently determinable evidence; they are never silently
chosen.

## 16. Point-in-time, atomicity, and prefix invariance

All evidence is evaluated in complete effective groups. No range or candidate is
promoted from a partial group.

Required invariants are:

- the range is unavailable before the sixth source bar closes;
- the candidate is unavailable before its formation bar closes;
- future target, invalidation, timeout, price path, PnL, and labels are absent
  from candidate identity and eligibility;
- strictly later complete append preserves every prior range and candidate
  byte-for-byte;
- same-effective append, historical insertion, correction, reordering,
  calendar-version mutation, or contract remapping is not a valid prefix test;
- a determinably later malformed group cannot mutate strictly prior valid
  evidence and promotes nothing from the failing group onward; and
- an unknowable malformed effective moment requires no trustworthy prefix.

Full-history extraction must equal exact-prefix extraction for every promoted
range and candidate.

## 17. Exact outcome and falsification contract

The outcome horizon is exactly twelve fully closed five-minute bars strictly
after candidate formation. The formation bar is never part of the label
horizon.

Outcome states are:

- `EXTENSION_FIRST`: target touched before invalidation within twelve bars;
- `INVALIDATION_FIRST`: a bar closes at or through the direction-specific
  opposite opening-range boundary before target touch;
- `TIMEOUT`: neither event occurs after all twelve bars close;
- `SAME_BAR_AMBIGUOUS`: target touch and invalidation close both occur in the
  same future bar and intrabar order is unavailable;
- `INCOMPLETE`: all twelve later bars are not supplied; and
- `INVALID`: malformed, conflicting, noncanonical, or unreconciled evidence.

Target touch is bullish `high_tick >= target_tick` and bearish
`low_tick <= target_tick`. Invalidation is bullish
`close_tick <= opening_range_low_tick` and bearish
`close_tick >= opening_range_high_tick`.

For a future binary baseline, `EXTENSION_FIRST` is positive;
`INVALIDATION_FIRST` and `TIMEOUT` are negative; `SAME_BAR_AMBIGUOUS`,
`INCOMPLETE`, and `INVALID` are excluded with exact counts and reasons. No
profitability inference follows from these structural labels.

## 18. Status precedence and fail-closed behavior

The exact result precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

- `INVALID`: malformed or contradictory evidence that is independently
  determinable from supplied inputs;
- `AMBIGUOUS`: two nonidentical canonical interpretations remain after all
  exact validation;
- `UNKNOWN`: required calendar, source-range, or complete future horizon is
  unavailable without independently determinable invalid evidence;
- `VALID`: at least one complete candidate or complete no-candidate trade-date
  assessment exists and no higher status applies; and
- `NONE`: an explicitly requested, fully covered scope contains no eligible
  trade date or no qualifying breakout.

Missing top-level context cannot suppress malformed supplied counterpart
evidence. Higher-precedence later evidence cannot delete strictly prior valid
ranges or candidates.

## 19. Detector and methodology role boundary

Phase B V1 roles are exactly:

| Role | Evidence |
|---|---|
| `REQUIRED` | canonical GC 5m bars and versioned calendar |
| `REQUIRED_CONTEXT` | exact New York AM eligibility/time proof |
| `DIAGNOSTIC_ONLY` | FVG, structure events, completed-session Volume Profile, Premium/Discount |
| `OFF` | Equal Liquidity, Dealing Range, Liquidity Map, Inducement, Order Block, Mitigation Block, Breaker Block |
| `BASELINE_ONLY` | legacy SMC, CRT, and order-flow strategy outputs |

`DIAGNOSTIC_ONLY`, `OFF`, and `BASELINE_ONLY` evidence cannot create, remove,
rank, relabel, or change a Phase B V1 candidate. The setup does not require a
new standalone market-concept detector. A future bounded builder may aggregate
only the required immutable bar/calendar context.

AI and local language models have no candidate, label, feature, risk, or trading
authority. They may later assist only with offline code review, evidence
summarization, or approved reproducibility checks under a separate provider
contract.

## 20. Data, partition, and training boundary

The accepted Phase A private dataset may be used only for a new explicitly
authorized development-only occurrence/label-feasibility run. Existing Phase A
artifacts are immutable and cannot be overwritten.

The failed historical OOS evidence remains negative historical evidence and is
not a new Phase B final OOS partition. No current period is silently declared
untouched. Before any Phase B model fitting, a later decision must lock:

- a promoted point-in-time dataset manifest;
- a new feature and label schema;
- chronological training and validation partitions;
- purge and twelve-bar embargo rules;
- a genuinely untouched future OOS period;
- deterministic baselines and numerical promotion thresholds; and
- exact model-library, serialization, reproducibility, and security contracts.

Random split, outcome-guided date selection, contract leakage, duplicated
multi-timeframe periods, online learning, automatic retraining, reinforcement
learning, neural-network/foundation-model fine-tuning, and OOS-driven threshold
selection remain forbidden.

## 21. Phase B feasibility and promotion gates

The first future private run may assess only deterministic candidate and label
feasibility. It may not estimate PnL or fit a model.

The exact minimum feasibility gate is:

- at least `40` complete candidates;
- candidates on at least `40` distinct eligible trade dates;
- at least `10` bullish and `10` bearish complete candidates;
- representation from at least `3` canonical GC contract months;
- `100%` candidate identity and exact-prefix reproducibility across two fresh
  executions;
- zero silent invalid, ambiguous, or incomplete exclusions; and
- a complete count/reason funnel over every requested trade date.

Passing this gate means only that the setup is sufficiently populated for a
separate feature/label experiment proposal. It does not authorize training.
Failure retires `GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1`; it does not
authorize changing six bars, the window, the one-tick close rule, the target,
the invalidation boundary, the twelve-bar horizon, or the minimum gate after
observing the result.

## 22. Inline synthetic exact 48-case future matrix

Any future implementation proposal must preserve these exact logical cases;
parameterization may increase collected tests without changing the logical
count:

1. Missing bars and missing calendar produce fail-closed `UNKNOWN` with no range.
2. A malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
3. Non-tuple, duplicate, reordered, or same-index forked bars are rejected.
4. Boolean, fractional, non-finite, negative-volume, or malformed values fail closed.
5. Naive timestamps and timezone/version mismatch fail closed.
6. Non-GC, spot, CFD, option, micro, or ambiguous contract inputs are rejected.
7. Non-5m, non-closed, pseudo-MTF, or cross-contract source bars are rejected.
8. Missing, holiday, session-closed, or inapplicable calendar evidence is fail-closed.
9. A canonical early close before complete source or label coverage is `NONE` with exact session-ineligible reason; malformed calendar evidence is `INVALID`.
10. Exact six source bars at `07:00` through `07:25` form one range at `07:30`.
11. Five bars are insufficient and seven bars do not alter the source tuple.
12. Missing middle source bar, timestamp substitution, or nonconsecutive index is invalid.
13. Cross-trade-date or cross-session source membership is invalid.
14. Positive one-tick width is valid and zero width is invalid.
15. Integer extrema and width are exact under arbitrary Decimal context.
16. Strictly pre-`07:30` breakout evidence cannot create a candidate.
17. Exact `07:30` candidate-window start is eligible.
18. Exact `09:00` bar-open timestamp is ineligible.
19. A bar opening at exact `10:00` New York AM end is never a candidate or label bar.
20. Bullish exact one-tick close breakout qualifies.
21. Bearish exact one-tick close breakout qualifies.
22. Boundary-equality close is not a breakout.
23. Wick-only breakout without qualifying close is not a candidate.
24. Earliest qualifying bar wins and later bars cannot replace it.
25. One candidate maximum per trade date is deterministic.
26. Formation-bar target touch is rejected as `FORMATION_OUTCOME_COLLISION`.
27. Formation-bar opposite-boundary traversal is rejected as `FORMATION_OUTCOME_COLLISION`.
28. Bullish target, invalidation, and width geometry reconcile exactly.
29. Bearish target, invalidation, and width geometry reconcile exactly.
30. Candidate identity is sensitive to source, direction, geometry, contract, trade date, and moment.
31. Identity required/forbidden fields and unknown identity kind are exhaustive.
32. Strictly later bullish target touch produces `EXTENSION_FIRST`.
33. Strictly later bearish target touch produces `EXTENSION_FIRST`.
34. Bullish opposite-boundary close produces `INVALIDATION_FIRST`.
35. Bearish opposite-boundary close produces `INVALIDATION_FIRST`.
36. Twelve complete bars without either boundary produce `TIMEOUT`.
37. Fewer than twelve later bars produce `INCOMPLETE` without relabeling.
38. Same-bar target and invalidation produce `SAME_BAR_AMBIGUOUS`.
39. The formation bar is excluded from all label evaluation.
40. Full-history and exact-prefix range/candidate bytes are equal.
41. Strictly later complete append preserves prior evidence byte-for-byte.
42. Same-effective append, historical repair, reordering, or calendar mutation is prefix-ineligible.
43. Determinably later malformed evidence preserves only strictly prior valid evidence.
44. `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence is exact.
45. FVG, structure, Volume Profile, and other diagnostic evidence cannot change eligibility.
46. OFF V1 detector evidence cannot create, remove, or relabel a candidate.
47. Two fresh executions reproduce identities, counts, statuses, reasons, and bytes.
48. Exact frozen contracts, exports, forbidden imports, scope isolation, rollback, and no training/OOS/integration are verified.

## 23. Exact next scope, rollback, promotion, and STOP conditions

The next single task is documentation-only preparation of:

`docs/gc_futures_phase_b_ny_am_opening_range_breakout_continuation_feasibility_change_proposal.md`

No future Python/tests/checkpoint three-path scope is reserved by this decision.
The proposal must independently lock public contracts, identities, exact private
input bindings, output scope, atomic publication, test totals, and private-run
authority before implementation can begin.

Before local commit, rollback is deletion of only this file. After local commit,
rollback requires a bounded revert; history rewriting and evidence deletion are
forbidden.

STOP on baseline/hash drift, changed Phase A evidence, V1 rescue, more than one
new setup, opening-range/window/geometry/horizon/gate ambiguity, unavailable
canonical calendar or 5m bars, non-determinism, source mutation, private-data
publication, OOS contact, outcome-guided rule revision, feature/label work,
training, model dependency, integration, paper/live behavior, test failure,
scope drift, or remote publication without exact authority.

Independent documentation acceptance evidence on `2026-08-16` is:

- exactly `24` sequential numbered sections;
- exactly `48` sequential logical future cases in Section 22;
- focused continuity regression:
  `48 passed in 0.60s` with pytest cache disabled; and
- full explicit `tests` regression:
  `2346 passed in 12.01s` with pytest cache disabled.

These regressions prove baseline preservation only. They do not test or
implement the newly selected Phase B hypothesis.

## 24. Final decision and resume boundary

The exact decision is:

`CLOSE_PHASE_A_RETIRED_V1_AND_SELECT_PHASE_B_GC_NY_AM_OPENING_RANGE_BREAKOUT_CONTINUATION_V1`

Phase A is complete as trustworthy negative development evidence. Its V1 setup
and continuity rescue path are closed. No Phase A candidate table, feature
table, label table, model, OOS result, strategy promotion, or trading authority
exists.

Phase B has one selected research direction, not an implemented strategy and
not a trained AI. Its next action is the one documentation-only feasibility
proposal in Section 23. No source, test, fixture, private artifact,
feature/label, model, OOS, runtime, integration, stage, commit, or push action is
implied by this record.

Global code freeze remains active.
