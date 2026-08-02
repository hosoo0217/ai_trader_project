# GC Futures AI Strategy and Training Decision

## 1. Decision Record

- Decision ID: `GC-FUTURES-AI-STRATEGY-TRAINING-2026-08-02`.
- Decision version: `1`.
- Baseline branch: `main`.
- Baseline Git commit:
  `4ab62dcf3e5ecfe4e463bd07913a14a9f2d91125`.
- Baseline full regression: `1778 passed` with `-p no:cacheprovider`.
- Work type: documentation-only strategy and machine-learning research decision.
- Status: `READY_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`.
- Global code freeze: `ACTIVE`.
- Python, test, fixture, dependency, configuration, integration, training, model,
  paper, broker, and live authorization: `NOT GRANTED`.

This record selects one bounded GC Futures AI research direction. It does not
claim profitability, create a trading signal, approve a model, authorize model
training, or lift any existing freeze.

## 2. Purpose and Final System Direction

The long-term target is one explainable GC Futures research, backtest, and
validation system whose deterministic market-state analyzers feed a bounded
machine-learning decision layer. It is not an unrestricted trading bot and it
is not an autonomous self-modifying agent.

The selected umbrella strategy name is:

`GC_AI_CONTEXTUAL_SETUP_SELECTION`

Version 1 has exactly one learnable setup family:

`LIQUIDITY_SWEEP_RECLAIM_STRUCTURE_FVG`

The version-1 model may estimate the quality of a fully confirmed candidate and
may abstain. It may not invent a setup, change direction, change source evidence,
set risk, place an order, or learn from paper/live outcomes automatically.

The long-term possibility of selecting among additional setup families is not
accepted by this record. Mitigation and Breaker candidates may be considered
only after version 1 passes its complete independent evidence gates and a new
decision explicitly authorizes a broader action space.

## 3. Verified Repository Truth at the Baseline

The following baseline facts are locked:

1. No trainable machine-learning pipeline, model artifact, model registry,
   feature store, label builder, or inference service currently exists.
2. The existing `ai/` package contains deterministic review, coaching,
   proposal, approval, and placeholder workflows; its name does not establish
   machine learning.
3. `requirements.txt` contains pandas but no approved machine-learning library.
4. The SMC V2 and completed-session Volume Profile modules are immutable,
   deterministic, separately tested diagnostic components.
5. Those diagnostic components are not imported by `main.py`, the current paper
   flow, the current decision engine, risk execution, or decision-trace wiring.
6. The current runtime direction is driven primarily by EMA analysis and a
   legacy multi-timeframe combiner; it reuses one candle table for multiple
   timeframe labels and therefore is not accepted as true multi-timeframe
   evidence.
7. The frozen rolling backtest can contain overlapping simulated outcome
   horizons and is not accepted as strict chronological single-position
   portfolio evidence.
8. The frozen independent baseline is preserved as reproducible negative
   evidence. No prior failed OOS result may be renamed, deleted, tuned away, or
   treated as approval.
9. Spot `XAUUSD` configuration exists but is outside this decision.
10. Paper and live progression remain blocked.

## 4. Exact Documentation-Only Scope

The only authorized changed path for this task is:

- `docs/gc_futures_ai_strategy_training_decision.md`.

This record does not authorize creation or modification of:

- Python source or tests;
- model, notebook, feature, label, dataset, fixture, report, or binary artifacts;
- requirements or environment files;
- configuration, package exports, CLI, main, runtime, trace, risk, broker, paper,
  or live paths;
- private data or external review evidence;
- any other documentation file.

No implementation path is reserved by this decision. Every future phase must
receive its own exact-path proposal, independent audit, human authorization, and
bounded freeze exception.

## 5. Authority Separation

The future system must preserve four independent authorities:

1. `DETECTOR_AUTHORITY`
   - validates immutable point-in-time market evidence;
   - creates deterministic results and snapshots;
   - never reads model output.
2. `MODEL_AUTHORITY`
   - consumes an approved immutable feature vector;
   - returns a calibrated quality estimate or abstention;
   - never mutates detector evidence.
3. `POLICY_AUTHORITY`
   - applies a separately approved deterministic score threshold and candidate
     eligibility rules;
   - may return only a research decision candidate or no candidate.
4. `RISK_AND_EXECUTION_AUTHORITY`
   - remains deterministic and external to the model;
   - owns position limits, capital protection, stop/target policy, sizing,
     session shutdown, and any later simulated execution.

The model cannot override an effective-group detector `INVALID`, `AMBIGUOUS`, or
`UNKNOWN`, a calendar/session closure, a risk block, an unavailable feature, or
an abstention.

For candidate construction and feature-row promotion, dependency status
precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

- `INVALID`, `AMBIGUOUS`, and `UNKNOWN` produce no V1 feature row;
- `VALID` may produce one row only after every required dependency reconciles;
- `NONE` means no qualifying candidate and produces no row;
- an independently determinable later `INVALID` condition cannot be hidden by an
  earlier `AMBIGUOUS` or `UNKNOWN` condition;
- strictly prior valid immutable rows remain preserved when a determinably later
  group fails, while the failing group and every later group produce no row.

## 6. Instrument, Contract, Time, and Data Boundary

Version 1 is GC Futures only.

- `instrument` must normalize to `GC` plus an exact contract identity.
- `XAUUSD`, spot gold, CFDs, equities, crypto, options, and other futures are
  forbidden.
- Different GC contracts may not be silently stitched into one instrument.
- Any continuous-contract or roll-adjusted series requires a later explicit
  provenance and adjustment decision.
- The V1 research timeframe is exactly one fully closed `5m` bar stream.
- No higher-timeframe input or derived multi-timeframe feature is permitted in
  V1. Reusing the same 5m table under higher-timeframe labels is forbidden.
- Available 1m and 10m views of the same period remain separate diagnostic data;
  they may not be resampled, joined, pooled, or treated as independent evidence
  in the V1 dataset without a later versioned decision.
- Price inputs must use exact integer ticks with an explicit tick-size binding.
- Volume inputs, when approved for a feature, must be exact nonnegative integers.
- All observations must be fully closed and timezone-aware.
- UTC is the canonical stored time. Exchange-local interpretation must use IANA
  `America/New_York` and a reproducible runtime timezone-data version.
- Caller ordering must be validated; no training or inference layer may silently
  sort malformed input.
- Duplicate, conflicting, naive, non-finite, fractional-tick, future-known, or
  otherwise malformed evidence is fail-closed.

The exact GC contract, source schema, usable dates, tick size,
commission, exchange fees, and slippage assumptions must be locked in a future
experiment pre-registration before any label generation or model training.

## 7. Version-1 Candidate Contract

A candidate is created only from one canonical `Inducement` item and its
corresponding canonical `InducementSnapshot` in a fully valid, nonambiguous
effective group. The candidate direction is the immutable Inducement direction
and is not predicted by the model.

Eligibility is evaluated at the candidate effective group, not by requiring the
aggregate `InducementResult.status` to be `VALID`. A result may preserve strictly
prior canonical Inducement/Snapshot evidence while a determinably later group
makes the aggregate result `UNKNOWN`, `AMBIGUOUS`, or `INVALID`. Such strictly
prior evidence remains eligible if its own complete dependency prefix is valid;
the failing group and all later groups remain ineligible. An unknowable malformed
effective moment invalidates trust in any claimed cutoff and therefore permits no
prefix assumption.

The underlying mirrored sequence is:

1. a canonical active external Dealing Range and target;
2. a confirmed internal opposite-side Equal Liquidity pool;
3. an exact sweep and tolerance-boundary reclaim;
4. a strictly later BOS or CHOCH confirmation within the locked next-three
   fully closed observation positions;
5. one causally bound qualifying Fair Value Gap whose source sequence reconciles
   with the structure-event sequence;
6. the shared confirmation/FVG formation moment as the candidate first-known
   moment.

No candidate exists at the sweep moment. No later lifecycle event, target hit,
entry, exit, PnL, or label may backdate, enrich, remove, or relabel the candidate.

Exactly one canonical candidate ID must identify its immutable dependency IDs,
direction, sweep/reclaim geometry, confirmation moment, external target, and FVG
evidence. Duplicate/forked evidence is invalid. Simultaneous opposing valid
candidates in one effective group are ambiguous and are excluded from training
and scoring.

## 8. Version-1 Research Objective and Non-Execution Boundary

Version 1 answers one research question:

> Given only information known at a fully confirmed candidate's first-known
> moment, what is the calibrated probability that its locked external target is
> reached before its locked structural invalidation within a pre-registered
> future horizon?

This is a candidate-quality prediction, not an order instruction.

Version 1 does not determine:

- whether an order was fillable;
- entry price or order type;
- stop-loss or take-profit order placement;
- position size or account risk;
- realized PnL;
- portfolio allocation;
- trade management;
- paper or live execution.

An execution policy may be researched only after the candidate-quality model
passes its gates. That later work must define entry, fill, stop, target, cost,
and collision precedence separately and may not reuse version-1 outcome labels
as if they were realized trades.

## 9. Detector Role Lock

Version-1 roles are exactly:

| Capability | Role | Version-1 authority |
|---|---|---|
| SMC V2 shared primitives | `REQUIRED` | Canonical types, status, time, ticks, provenance |
| Equal Liquidity | `REQUIRED` | Internal pool and sweep lifecycle evidence |
| Dealing Range | `REQUIRED` | Active external range, structure event, target context |
| Liquidity Map | `REQUIRED` | Internal/external source classification |
| Fair Value Gap | `REQUIRED` | Causally bound formation evidence |
| Inducement | `REQUIRED` | Canonical candidate generator |
| Kill-zone context | `REQUIRED_CONTEXT` | Verified session/time context; never direction |
| Premium/Discount | `DIAGNOSTIC_ONLY` | Shadow reporting; excluded from V1 model features |
| Completed-session Volume Profile | `DIAGNOSTIC_ONLY` | Shadow reporting; excluded from V1 model features |
| Order Block | `OFF` | No V1 candidate or feature authority |
| Mitigation Block | `OFF` | No V1 candidate or feature authority |
| Breaker Block | `OFF` | No V1 candidate or feature authority |
| Legacy SMC/CRT/Order Flow | `BASELINE_ONLY` | Historical comparison; no V1 feature authority |

`DIAGNOSTIC_ONLY` values may be recorded in a physically separate shadow table,
but they may not enter feature fitting, hyperparameter selection, score
thresholds, labels, or model promotion in version 1.

`OFF` modules remain preserved and tested. They are not deleted, recomputed, or
silently enabled.

## 10. Kill-Zone and Session Eligibility

Candidate feature rows require canonical Kill-zone context with:

- exact `America/New_York` timezone and matching runtime timezone-data version;
- verified caller-supplied calendar coverage;
- an eligible open GC trade date;
- no holiday/session-closed state;
- no missing or conflicting calendar evidence.

Version 1 permits candidate rows only in `NEW_YORK_AM`, start inclusive and end
exclusive under the locked Kill-zone contract. Other valid windows remain
diagnostic-only negative context and are not silently pooled with version 1.

Early-close handling must follow the supplied canonical calendar/session
boundary. A candidate outside the eligible exchange session, on an unverified
calendar date, or at/after an applicable early close cannot become a V1 row.

This window selection is a research hypothesis, not evidence of profitability.
Any later window expansion is a new model version and requires new independent
validation.

## 11. Point-in-Time Feature Contract

Every model feature must be derivable solely from immutable evidence available
at the candidate first-known moment. Feature extraction is reference-only and
must not mutate or recompute foreign detector outputs.

The feature schema ID is exactly `GC_AI_FEATURE_SCHEMA_V1`. Its ordered learned
fields are exactly:

| Field | Type | Exact source/meaning |
|---|---|---|
| `candidate_direction` | enum string | Immutable Inducement direction |
| `structure_event_type` | enum string | Exact BOS or CHOCH token |
| `confirmation_offset_bars` | int | Locked value in `{1, 2, 3}` |
| `pool_side` | enum string | Canonical internal pool side |
| `pool_width_ticks` | int | `upper_tick - lower_tick`, nonnegative |
| `pool_member_count` | int | Length of canonical ordered member swing IDs |
| `sweep_penetration_ticks` | int | Direction-aware penetration beyond the swept pool boundary, at least one |
| `reclaim_boundary_distance_ticks` | int | Direction-aware close distance back inside/from the reclaim boundary, nonnegative |
| `target_source_kind` | enum string | Canonical external classification source kind |
| `external_target_distance_ticks` | int | Direction-aware distance from reclaim close to nearest target boundary, positive |
| `range_direction` | enum string | Active Dealing Range direction as mandatory non-signal context |
| `range_width_ticks` | int | External range upper tick minus lower tick, positive |
| `range_midpoint_offset_half_ticks` | int | Direction-normalized `2 * confirmation_close - (range_lower + range_upper)` |
| `fvg_width_ticks` | int | Immutable FVG upper tick minus lower tick, at least two |
| `fvg_midpoint_offset_half_ticks` | int | Direction-normalized `2 * confirmation_close - (fvg_lower + fvg_upper)` |
| `minutes_from_ny_am_start` | int | Exchange-local whole minutes from inclusive 07:00 start |
| `minutes_to_ny_am_end` | int | Exchange-local whole minutes to exclusive 10:00 end |

For both midpoint-offset fields, direction normalization uses multiplier `+1`
for bullish and `-1` for bearish. Integer half-tick representation avoids float
and Decimal-context ambiguity. The exact confirmation close is taken from the
canonical fully closed 5m observation matching the candidate confirmation
index/timestamp.

Candidate ID, source IDs, exact first-known UTC moment, trade date, calendar
version, contract ID, and detector/model versions remain mandatory lineage and
grouping evidence but are not learned feature columns.

Raw identity hashes, absolute row numbers, filenames, dataset names, contract
expiry labels, future session outcome, later lifecycle states, target hit, stop
hit, PnL, and any post-confirmation field are forbidden model features.

Categorical encoding, missing-value handling, scaling, and feature selection must
be fitted only on the training partition. No preprocessing may inspect validation
or OOS distributions.

## 12. Label and Outcome Contract

Every candidate receives exactly one immutable research outcome after a future
experiment manifest locks a positive integer horizon `H` in fully closed bars.
There is no default `H` in this decision and training must stop if it is absent.

The label schema ID is exactly `GC_AI_LABEL_SCHEMA_V1`.

Outcome states are exactly:

- `TARGET_FIRST`: the locked external target is reached before structural
  invalidation within `H` bars;
- `INVALIDATION_FIRST`: structural invalidation is reached before the target
  within `H` bars;
- `TIMEOUT`: neither boundary is reached within `H` bars;
- `SAME_BAR_AMBIGUOUS`: target and invalidation are both reachable in one bar
  and deterministic intrabar order is unavailable;
- `INCOMPLETE`: the complete label horizon is unavailable;
- `INVALID`: malformed, conflicting, noncanonical, or unreconciled evidence.

For the first binary research baseline:

- positive label: `TARGET_FIRST`;
- negative label: `INVALIDATION_FIRST` or `TIMEOUT`;
- excluded from fitting and score metrics: `SAME_BAR_AMBIGUOUS`, `INCOMPLETE`,
  and `INVALID`.

Excluded counts and reasons must still be reported. They may not be silently
dropped.

Target and invalidation boundaries must be frozen at candidate first-known time.
Later detector revisions cannot change them. The exact touch/close rule and
same-bar conservative precedence must be locked before labels are generated.

## 13. Dataset Manifest and Lineage

Each generated dataset must have one immutable manifest containing at least:

- dataset ID and schema version;
- exact GC contract identity and raw-source hashes;
- source format and exporter/importer hashes;
- inclusive raw-data start and end moments;
- usable closed-bar start and end moments;
- timezone name and runtime timezone-data version;
- timeframe and bar-construction rule;
- detector source hashes and configuration hashes;
- feature-schema hash;
- label-schema hash and exact `H`;
- commission/slippage assumptions when later trade simulation is performed;
- candidate, positive, negative, ambiguous, incomplete, and invalid counts;
- missing-bar, duplicate, ordering, and calendar-quality evidence;
- chronological partition boundaries;
- purge/embargo evidence;
- generation code commit and command;
- final serialized artifact SHA-256.

Private raw data and generated private feature/label tables must remain ignored
and must not be committed. A sanitized manifest may be committed only through a
separate documentation authorization that proves it contains no proprietary or
sensitive data.

## 14. Chronological Partition, Purge, and Embargo Rules

Random row splitting is forbidden.

The only permitted evaluation order is chronological:

1. training partition;
2. model-selection validation partition;
3. calibration/threshold partition when separately required;
4. locked final OOS partition.

Rules:

- complete same-effective candidate groups are atomic and never split;
- all source evidence and the complete label interval for a candidate must lie
  within its assigned partition;
- any candidate whose label interval crosses a partition boundary is purged;
- an embargo of at least the locked label horizon `H` bars follows every fitting
  boundary before evaluation candidates become eligible;
- overlapping label intervals must be grouped or purged according to a
  pre-registered deterministic rule;
- no contract or session may appear on both sides through duplicated/resampled
  representations of the same underlying period;
- 1m, 5m, and 10m views of the same dates are not independent periods;
- the final OOS partition is opened once for the frozen candidate and cannot be
  reused for model or threshold selection.

The previously failed frozen OOS evidence remains historical negative evidence.
It is not automatically a valid training partition and cannot become a new final
OOS partition.

## 15. Model Hierarchy and Training Boundary

Model development must proceed in this exact comparison hierarchy:

1. deterministic constant/base-rate predictor;
2. pre-registered deterministic rule-score baseline;
3. regularized logistic-regression candidate scorer;
4. at most one separately approved gradient-boosted tree candidate.

Each stage must beat the previous eligible baseline on pre-registered validation
and calibration criteria before the next stage is considered.

Version 1 forbids:

- reinforcement learning;
- neural networks or foundation-model fine-tuning;
- online learning;
- automatic retraining;
- automatic feature discovery from future/outcome columns;
- unrestricted hyperparameter search;
- genetic/evolutionary threshold search;
- OOS-driven feature, setup, or threshold selection;
- model-generated source evidence;
- language-model trade decisions.

No machine-learning dependency may be added until a later proposal locks the
exact library, version range, serialization format, security/reproducibility
review, and three-path implementation scope.

## 16. Model Output, Calibration, and Abstention

The future V1 scorer may return only:

- candidate ID;
- model ID and model version;
- feature-schema ID;
- calibrated `TARGET_FIRST` probability in `[0, 1]`;
- status `SCORED`, `ABSTAINED`, or `INVALID`;
- immutable reason codes;
- missing/out-of-domain feature reasons;
- inference effective moment equal to the candidate first-known moment.

It may not return BUY/SELL direction independently; direction is inherited from
the canonical candidate. It may not return quantity, risk, entry, stop, target,
PnL, or execution instructions.

Abstention is mandatory when:

- any required dependency is not `VALID`;
- candidate evidence is ambiguous or invalid;
- required calendar/session context is unavailable;
- feature schema or model schema mismatches;
- any required feature is missing, non-finite, malformed, or out of its locked
  validation domain;
- probability calibration is unavailable;
- model or artifact identity cannot be reproduced.

A later deterministic policy may use a threshold only if that threshold is
locked using training/validation evidence before final OOS. The threshold is not
defined by this decision.

## 17. Deterministic Risk and Execution Boundary

Machine learning never owns safety or capital authority.

Any future simulated or paper candidate must still pass deterministic controls
for:

- session and calendar eligibility;
- maximum concurrent positions;
- daily loss and capital-protection state;
- exact account and GC contract multiplier;
- maximum risk per trade;
- stop and target geometry;
- volume bounds;
- spread, commission, exchange fees, and slippage;
- unresolved prior position;
- emergency/global halt.

Model confidence cannot increase maximum risk, remove a stop, extend an expiry,
override a block, or authorize live trading. Model failure must degrade to
`NO_CANDIDATE`, never to a default trade.

## 18. Metrics and Model-Selection Rules

Primary predictive evaluation must include:

- candidate count and class balance;
- log loss;
- Brier score;
- calibration intercept/slope or equivalent calibration table;
- reliability by fixed probability bins;
- precision and recall at any pre-registered research threshold;
- abstention and invalid rates;
- performance by contract, month, session segment, direction, event type, and
  pre-registered volatility regime;
- uncertainty intervals where sample size permits.

ROC AUC or accuracy may be reported but cannot be the sole promotion metric.

Later hypothetical trade simulation must separately report:

- exact entry/fill policy;
- costs and slippage;
- chronological non-overlapping trade count;
- expectancy, profit factor, drawdown, loss streak, and unresolved outcomes;
- rule-baseline versus model-policy comparison;
- sensitivity to reasonable fixed cost and threshold changes.

No single favorable PnL, win rate, accuracy, or AUC result establishes success.
Regime slices with insufficient samples must be labeled insufficient rather than
combined or omitted opportunistically.

Exact numerical promotion thresholds are intentionally not set here. They must
be pre-registered before model fitting and may not be inferred from final OOS.

## 19. No-Look-Ahead and Leakage Controls

Mandatory controls are:

1. Every feature carries a point-in-time effective moment.
2. Every feature is reconstructed from the exact valid prefix ending at the
   candidate first-known group.
3. Full-history extraction must equal prefix extraction byte-for-byte for that
   candidate.
4. Later append, repair, lifecycle transition, session result, target hit, and
   label cannot modify a prior feature row.
5. Same-effective groups are atomic.
6. Detector order is caller-validated and never silently sorted.
7. Scaling, encoding, imputation, feature selection, calibration, and threshold
   fitting use training/validation partitions only.
8. Labels and label-derived aggregates are physically and logically excluded
   from feature inputs.
9. Outcome-dependent row filtering is forbidden except for explicit invalid,
   incomplete, and ambiguous exclusion reporting.
10. Feature names, missingness flags, IDs, filenames, and calendar boundaries
    must be reviewed for target leakage.
11. Every split is chronological with purge and embargo.
12. A deliberately leaked sentinel feature must be detected by a mandatory
    negative-control test before promotion.

Any leakage finding invalidates all affected model evidence and requires dataset
and model artifacts to be quarantined, not patched in place.

## 20. Reproducibility and Model Registry

Every future trained model must have an immutable registry record containing:

- model ID, family, and semantic version;
- training code commit and source hashes;
- exact dependency versions and Python version;
- deterministic seed or an explicit statement that determinism is unavailable;
- dataset-manifest and feature/label schema hashes;
- partition boundaries and purge/embargo evidence;
- preprocessing and hyperparameters;
- fitting command;
- training, validation, calibration, and OOS metrics;
- excluded candidate counts and reasons;
- serialized model hash;
- reproducibility result from a clean rerun;
- approval, rejection, rollback, and supersession state.

Models are immutable. Retraining creates a new model ID/version and cannot
overwrite an earlier artifact or its evidence. Automatic promotion is forbidden.

## 21. Validation and Promotion Sequence

The required future sequence is:

1. accept this documentation decision after independent audit;
2. define and validate a strict chronological GC backtest/data-time contract;
3. lock one exact dataset/feature/label manifest and numerical experiment plan;
4. implement point-in-time feature/label extraction test-first;
5. verify deterministic prefix equivalence and leakage negative controls;
6. train and reproduce the constant and rule baselines;
7. train and reproduce logistic regression;
8. evaluate only on the locked validation/calibration partitions;
9. freeze the selected candidate, preprocessing, and threshold;
10. run one untouched OOS evaluation;
11. perform an independent code, data, model, and evidence audit;
12. consider a separately authorized shadow/paper diagnostic phase.

Failure at any stage does not authorize adding another detector, setup family,
timeframe, model family, or data period to rescue the result. Such a change is a
new hypothesis and must restart from a new version with a new untouched OOS plan.

## 22. Inline Synthetic Exact 48-Case Future Test Matrix

Any future implementation proposal must preserve these exact logical cases;
parameterization may add collected tests without changing the count:

1. Missing top-level required dependency returns fail-closed unknown/invalid by
   available-evidence precedence and emits no feature row.
2. Non-tuple, malformed, duplicate, or out-of-order dependency inputs are
   invalid without exception leakage.
3. Instrument normalization accepts canonical GC identity and rejects XAUUSD or
   a missing/ambiguous contract.
4. Exact single-stream 5m, integer-tick, fully closed, aware-UTC input
   requirements are enforced; relabeled pseudo-MTF input is rejected.
5. Timezone name/version and `America/New_York` availability reconcile exactly.
6. Calendar missing, holiday, session-closed, and early-close boundaries are
   fail-closed.
7. Exact `NEW_YORK_AM` start is eligible and exact end is ineligible.
8. Non-New-York-AM valid Kill-zone contexts are excluded from V1 candidates.
9. Canonical active external range and target validation.
10. Canonical internal opposite-side Equal Liquidity pool validation.
11. Exact bullish sweep/reclaim candidate dependency sequence.
12. Exact bearish sweep/reclaim candidate dependency sequence.
13. Boundary-equality reclaim qualifies; wick-only/no-reclaim does not.
14. Same-bar and fourth-or-later structural confirmation do not qualify.
15. BOS and CHOCH confirmation variants reconcile.
16. Structure-event and FVG source sequences reconcile by the locked suffix rule.
17. FVG formation moment equals candidate confirmation moment.
18. Duplicate/forked pool, target, event, FVG, or candidate evidence is invalid.
19. Simultaneous opposing valid candidates are ambiguous and produce no row.
20. Candidate first-known moment cannot be backdated or retroactively enriched.
21. Required detector roles are accepted and OFF detector inputs have no V1
   authority.
22. Diagnostic-only Premium/Discount evidence is isolated from V1 features.
23. Diagnostic-only Volume Profile evidence is isolated from V1 features.
24. Exact allowed point-in-time feature names and types are enforced.
25. Identity hashes, filenames, row numbers, and future fields are rejected as
   learned features.
26. Bullish/bearish mirrored geometry yields deterministic signed features.
27. Missing, boolean, fractional, non-finite, overflow-like, and malformed
   feature values fail closed.
28. Full-history and exact-prefix feature rows are byte-for-byte equal.
29. Strictly later append preserves earlier rows; historical repair/reorder is
   ineligible.
30. Complete same-effective groups remain atomic.
31. Exact target-first label geometry within locked `H`.
32. Exact invalidation-first label geometry within locked `H`.
33. Timeout label after complete `H` without either boundary.
34. Same-bar target/invalidation collision becomes explicitly ambiguous.
35. Incomplete horizon is excluded and never relabeled from a later append.
36. Labels, post-confirmation lifecycle, outcome, entry, exit, and PnL cannot
   enter features.
37. Dataset manifest required fields, hashes, counts, and schema versions are
   exhaustive and immutable.
38. Chronological partition boundaries and same-group integrity are enforced.
39. Boundary-crossing labels are purged and exact `H` embargo is enforced.
40. Random split, duplicated multi-timeframe period, or cross-partition source
   overlap is rejected.
41. Constant/base-rate and deterministic rule baselines are reproducible.
42. Logistic preprocessing fits training only and inference schema matches.
43. Calibration and abstention are deterministic and fail closed when missing.
44. Model output contains no independent direction, risk, entry, stop, target,
   quantity, PnL, or order fields.
45. Model artifact, dataset, dependency, seed, or schema mismatch invalidates
   inference without fallback trading.
46. A leaked sentinel feature is detected by the mandatory negative control.
47. Metric, slice, insufficient-sample, exclusion, and status reporting is
   complete and deterministic.
48. Exact public/frozen contracts, exports, forbidden imports, scope isolation,
   repeatability, rollback, and no paper/live integration are verified.

## 23. Rollback, Promotion, and Stop Conditions

This decision is promoted only as a documentation contract after:

- exact one-file scope verification;
- independent semantic and structural audit;
- baseline/hash verification;
- human acceptance;
- no source, test, fixture, dependency, integration, or evidence mutation.

Future work must stop if:

- a canonical GC contract, timeframe, tick, session, or data source is absent;
- strict chronological and point-in-time behavior cannot be proved;
- label horizon, boundaries, collision rules, or costs are unspecified;
- required detector evidence cannot be reconstructed from the supplied prefix;
- data overlap, leakage, survivorship, timestamp, calendar, or roll ambiguity is
  found;
- sample size is insufficient for pre-registered evaluation;
- an OOS period has already influenced feature, model, or threshold selection;
- a requested change adds a setup family, timeframe, instrument, model family,
  dependency, online learning, or automatic retraining;
- a model is asked to control risk, execution, paper, broker, or live behavior;
- failed evidence would be deleted, overwritten, relabeled, or weakened;
- any test, hash, reproducibility check, audit, freeze, or scope gate fails.

Rollback means discarding only the unaccepted bounded change and restoring its
exact parent baseline. Historical evidence and immutable artifacts are never
rewritten.

## 24. Final Decision and Resume Boundary

The documentation decision is:

`GC_AI_CONTEXTUAL_SETUP_SELECTION_V1_SELECTED_FOR_INDEPENDENT_DOCUMENTATION_AUDIT`

Locked immediate direction:

- one instrument family: GC Futures;
- one umbrella AI strategy;
- one V1 setup family;
- deterministic candidate direction and evidence;
- offline calibrated candidate-quality scoring with abstention;
- deterministic external safety/risk authority;
- no model training or implementation authorization yet.

The next permitted action after this document is an independent read-only audit
of this exact file. No future Python, tests, fixtures, dependencies,
documentation, stage, commit, push, integration, training, paper, or live work is
implied.

Global code freeze remains active.
