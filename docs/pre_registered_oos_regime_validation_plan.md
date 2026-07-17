# Pre-Registered Out-of-Sample and Regime-Separated Validation Plan

## 1. Record Identity

- Plan date: `2026-07-17`
- Repository baseline: `10cca9652abf3ad2389ca3a28f84ca02841ddff6`
- Record status: completed; candidate-specific locked addendum remains required before any future OOS performance execution
- Scope: future offline research validation using data whose performance outcomes have not been evaluated by this project
- Primary profile: `Apex Futures Scalper`
- Current code-freeze status: `ACTIVE`
- Paper-trading progression: `BLOCKED`

## 2. Existing Evidence Boundary

- The accepted `GC-202608-COMEX` period remains valid Full Independent-Period Acceptance evidence.
- Its accepted usable coverage begins at `2026-05-13 18:00:00` and ends at the timeframe-specific final complete bars on `2026-06-02`.
- Its frozen 5m `weak` / no-Order-Flow performance baseline has already been executed, reproduced, reviewed, and diagnosed.
- Therefore, no subset, resample, alternate timeframe, session slice, regime slice, or later reinterpretation of that accepted period may be classified as genuine out-of-sample evidence.
- The canonical baseline and its 1m, 5m, and 10m representations also remain development or diagnostic evidence and must not be reclassified as out-of-sample evidence.
- The temporal-overlap diagnostic remains a limitation of the frozen runner: overlapping official results remain comparable diagnostic evidence, while strict and inclusive non-overlap selections remain descriptive counterfactuals only.

## 3. Future Candidate Non-Overlap Rule

- Genuine out-of-sample evaluation requires a new historical period whose complete declared usable range has zero authoritative-timestamp overlap with every previously evaluated baseline and accepted independent-performance period.
- The future candidate must independently satisfy the complete intake contract in `docs/independent_historical_dataset_intake.md` before any performance run.
- Required evidence includes complete 1m, 5m, and 10m Market OHLC/full-footprint pairs, exact metadata, hashes, timestamp matching, gap classification, raw-source traceability, overwrite protection, privacy checks, and external storage.
- The exact instrument contract, chart timezone, session configuration, usable start, usable end, and source-file identities must be locked in a candidate-specific addendum before performance execution or outcome review.
- Dataset quality inspection and intake validation may occur before performance evaluation, but they must not inspect, calculate, select, or disclose strategy PnL, win rate, profit factor, drawdown, trade outcomes, or favorable regime results.
- Any overlap, ambiguous boundary, incomplete pair, unresolved gap, post-outcome date selection, or missing pre-registration evidence fails closed and blocks OOS classification.

## 4. Safety Boundary

- This plan authorizes documentation, future dataset intake, and offline read-only diagnostic validation only.
- It does not authorize Python, strategy, risk, Order Flow, exporter, threshold, broker, API, paper-trading, live-trading, or real-execution changes.
- Candidate datasets, derived private files, traces, and generated reports must remain outside Git.
- Dataset acceptance, OOS classification, or regime analysis must not be interpreted as deployment approval.
- Missing, conflicting, outcome-informed, or unverifiable evidence must fail closed.

## 5. Locked Evaluation Configuration

The following primary configuration is locked before any future candidate performance outcome is reviewed:

- Repository baseline: `10cca9652abf3ad2389ca3a28f84ca02841ddff6`.
- Trading profile: `Apex Futures Scalper` selected explicitly with the existing `apex` profile route.
- Scenario: `weak`.
- Primary evaluation timeframe: `5m`.
- Primary market input: the accepted-range UTC-normalized Market OHLC derivative created from the candidate's preserved 5m raw Market OHLC file.
- Order Flow input for the primary comparability run: not provided.
- Market-input interpretation: existing positional `BAR_SUMMARY` OHLC behavior; this is not full price-level Order Flow enforcement.
- Starting balance, point value, risk settings, session rules, capital-protection behavior, safety gates, and quality criteria: the unchanged values supplied by the locked repository and selected profile.
- Numerical maximum-drawdown threshold: `NOT_CONFIGURED` and `NOT_APPROVED`.
- Backtest window size: the unchanged frozen value of `60` candles.
- Backtest step size: the unchanged frozen value of `5` candles.
- Maximum iterations: the complete deterministic iteration count produced from the entire accepted 5m candidate range; manual early stopping or favorable truncation is prohibited.
- Terminal-position behavior: the unchanged frozen behavior, including `close_at_final_candle=False`; unresolved terminal positions must be reported separately and must not be silently deleted or assigned invented PnL.
- The exact repository HEAD, relevant source-file hashes, profile, command arguments, normalized input hash, row count, usable range, and expected iteration count must be recorded before execution.
- No setting may be changed after candidate performance output is observed. Any later configuration becomes a separately named future experiment and cannot replace this pre-registered result.
- The primary run must be repeated without configuration changes. Baseline and reproduction captures must match byte-for-byte or the reproduction check fails.

## 6. Evaluation Tracks and Interpretation

### Track A: Frozen-Runner Comparability

- Track A uses the locked existing runner without source changes.
- It preserves the current five-candle scheduling and may contain temporally overlapping simulated outcome horizons.
- Its result is the official frozen-runner comparability result for the new candidate.
- It must report total iterations, executed and blocked trades, realized and unresolved trades, wins, losses, PnL, profit factor, drawdown, quality grade, blocking reasons, and terminal-position status.
- It must also export read-only trade traces and report how many realized outcomes extend beyond the next scheduled entry.
- Track A must not be described as established strict chronological single-position portfolio performance.

### Track B: Strict Chronological Sensitivity

- Track B is not an authorized source-code or strategy change.
- Under the active freeze, it may only use deterministic read-only post-processing of Track A traces.
- Strict selection uses the earliest eligible executed trade whose entry index is greater than the prior selected realized exit index.
- Inclusive sensitivity uses the earliest eligible executed trade whose entry index is equal to or greater than the prior selected realized exit index.
- Both selections must report included and excluded trades, unresolved trades, win rate, gross profit, gross loss, net PnL, profit factor, maximum drawdown, and maximum loss streak.
- Selected and excluded realized PnL must reconcile exactly to the original Track A realized PnL.
- Track B results are descriptive counterfactual sensitivity evidence only. They do not replace Track A, select a strategy, approve a threshold, or authorize paper progression.
- Any future official strict chronological runner requires separate authorization, an explicit freeze decision, implementation review, tests, and a new pre-registration record.

## 7. Pre-Registered Market-Regime Definitions

Regime labels must be derived from market data only. Strategy decisions, trade outcomes, PnL, win rate, profit factor, drawdown, or favorable result selection must not influence a label or cutoff.

### Reference Data for Fixed Cutoffs

- Cutoff reference: the already evaluated accepted-range 5m UTC Market OHLC derivative for `GC-202608-COMEX`.
- Reference-file SHA-256: `B207173BE5DD5815C61F81D764CB7705B631357D9513094EFF8A97D341315DE9`.
- This reference is development or prior diagnostic evidence only; it is not part of the future OOS candidate.
- Regime cutoffs must be calculated from this reference without reading trade traces, outcomes, PnL, or performance reports.
- Exact calculated cutoff values and their calculation manifest must be recorded before the future candidate's performance run.
- The future OOS candidate must never be used to recalculate, normalize, rank, or optimize these cutoffs.

### Volatility Regime

- Calculate 14-bar Average True Range from 5m OHLC data using only the current bar and earlier bars.
- True Range is the maximum of `High-Low`, `abs(High-PreviousClose)`, and `abs(Low-PreviousClose)`.
- ATR14 is the arithmetic mean of the most recent 14 valid True Range values.
- Compute fixed 33rd-percentile and 67th-percentile ATR14 cutoffs from the reference data.
- Label candidate decision windows `LOW_VOLATILITY` when ATR14 is at or below the fixed 33rd percentile.
- Label them `NORMAL_VOLATILITY` when ATR14 is above the 33rd and at or below the 67th percentile.
- Label them `HIGH_VOLATILITY` when ATR14 is above the fixed 67th percentile.

### Directional-Efficiency Regime

- Use the most recent 60 completed 5m closes available at the decision-window end.
- Directional efficiency is `abs(last close - first close) / sum(abs(consecutive close changes))` across that 60-bar window.
- A zero denominator produces an explicit `UNCLASSIFIED_ZERO_MOVEMENT` label and must not be silently replaced.
- Compute fixed 33rd-percentile and 67th-percentile efficiency cutoffs from complete reference windows.
- Label candidate windows `RANGING` at or below the fixed 33rd percentile.
- Label them `TRANSITIONAL` above the 33rd and at or below the 67th percentile.
- Label them `DIRECTIONAL` above the fixed 67th percentile.

### Direction Label

- Label the same 60-bar net close movement `UP` when positive, `DOWN` when negative, and `FLAT` only when exactly zero.
- The combined pre-entry regime key is `volatility|efficiency|direction`.
- Regime labels must use information available at the decision-window end only; post-entry and exit candles are prohibited from regime assignment.

### Percentile Calculation Lock

- Sort valid reference values in ascending order.
- For percentile `p`, calculate zero-based position `(N-1)*p`.
- Use the exact value at an integer position; otherwise use linear interpolation between the surrounding lower and upper values.
- Use `p=0.33` and `p=0.67` exactly.
- Missing rolling-history rows remain explicitly unclassified and must be reported rather than removed without accounting.

### Regime Reporting Rules

- Report every observed combined regime, including losing, empty, unresolved, and insufficient-data groups.
- Report iterations, executed trades, realized trades, unresolved trades, wins, losses, win rate, gross profit, gross loss, net PnL, profit factor, maximum drawdown, and maximum loss streak for each observed regime.
- A regime with fewer than 20 realized trades is `INSUFFICIENT_DATA` for inference and must not be combined selectively after outcomes are known.
- Regime comparisons are evidence reports, not permission to enable, disable, tune, or select strategy logic.

## 8. Outcome-Blind Validation Order

The future candidate must follow this order without skipping or rearranging steps:

1. Complete and promote this general pre-registration plan.
2. Create a candidate-specific addendum that locks instrument, contract, timezone, sessions, usable range, file identities, reference cutoff values, and expected commands before performance execution.
3. Acquire and preserve the raw candidate outside Git without overwriting earlier evidence.
4. Complete the independent historical dataset intake contract and assign its evidence classification.
5. Create the accepted-range UTC derivative and normalization manifest without changing raw rows other than documented timestamp normalization and declared-range selection.
6. Verify the locked repository HEAD, source hashes, profile, arguments, input hash, row count, expected iteration count, and regime-cutoff manifest.
7. Assign market-only pre-entry regime labels without reading performance output.
8. Run Track A once and preserve the complete capture and traces.
9. Repeat Track A unchanged and require an exact byte-for-byte result match.
10. Produce the read-only Track B sensitivity report from the preserved Track A traces.
11. Report overall, regime-separated, temporal-overlap, unresolved-position, data-quality, and safety results, including every failure.
12. Assign one final OOS evidence classification without changing settings or rerunning a favorable alternative.

If any earlier step fails, later results must not override or conceal that failure. A failed or insufficient result remains valid evidence and must not be deleted, relabeled, or tuned away.

## 9. Pre-Registered Decision Rules

Every completed candidate review must assign exactly one overall OOS performance-evidence classification:

### `INVALID_OOS_EVIDENCE`

Assign this classification when intake acceptance, non-overlap, configuration locking, source or input hashes, normalization, expected iteration count, trace completeness, exact reproduction, or required safety evidence fails.

### `VALID_OOS_EVIDENCE — INSUFFICIENT_DATA`

Assign this classification when evidence integrity passes but the run has fewer than 30 iterations, fewer than 20 realized trades, or otherwise lacks the minimum sample required for performance inference.

### `VALID_OOS_EVIDENCE — PERFORMANCE_FAILED`

Assign this classification when evidence integrity and minimum sample requirements pass but total PnL is non-positive when positive PnL is required, win rate is below the locked quality minimum, profit factor is below the locked quality minimum, data quality fails, or another unchanged quality gate fails.

### `VALID_OOS_EVIDENCE — NON_DRAWDOWN_METRICS_MET; READINESS_NOT_APPROVED`

Assign this classification only when evidence integrity, minimum sample requirements, positive-PnL requirement, locked win-rate minimum, locked profit-factor minimum, data quality, and other unchanged non-drawdown quality gates pass.

Because no numerical drawdown threshold is configured or approved, this final classification is not a complete quality pass, threshold approval, readiness approval, or paper-progression approval.

### Overall Decision Rules

- Use the entire declared accepted candidate range. Favorable truncation, selective days, selective sessions, and post-outcome exclusions are prohibited.
- Record Track A exactly as produced, including temporal overlap, blocked trades, unresolved terminal positions, warnings, and failures.
- An exact reproduction mismatch invalidates the OOS performance evidence until the cause is resolved and the complete locked sequence is restarted.
- Track B cannot upgrade, downgrade, replace, or erase the official Track A classification.
- A positive Track B result alongside a failed Track A result is boundary-sensitivity evidence, not a strategy pass.
- A failed result must be preserved and reported. It must not trigger automatic tuning, threshold selection, strategy modification, risk modification, or a favorable rerun.
- A later candidate must receive its own addendum and independent review; results must not be pooled selectively after outcomes are known.
- Overall and regime-separated results must be reported together. A positive aggregate must not conceal a failed regime, and a positive regime must not override a failed aggregate.
- Drawdown remains descriptive until a separate profile-specific numerical threshold is supported, reviewed, explicitly approved, and configured.
- No classification in this plan authorizes paper trading, live trading, broker access, external APIs, or real execution.

## 10. Candidate-Specific Addendum Requirements

Before any future candidate performance execution, a separate addendum must record all of the following:

- General plan filename, SHA-256, completion date, and repository commit containing the plan.
- Addendum creation date, operator, reviewer, and status.
- Explicit declaration that candidate performance outcomes were not inspected before the addendum lock.
- Instrument symbol, exact contract identifier, data source, acquisition date, chart timezone, session configuration, and timeframe pairs.
- Raw candidate filenames, byte sizes, SHA-256 hashes, raw first and last timestamps, and declared usable first and last timestamps.
- Zero-overlap evidence against the canonical baseline, the accepted `GC-202608-COMEX` period, and every other previously evaluated candidate.
- Independent intake review filename, classification, SHA-256, and unresolved issues.
- UTC-normalized derivative filename, transformation rules, row count, usable range, byte size, and SHA-256.
- Fixed ATR14 percentile values, fixed directional-efficiency percentile values, reference-data hash, calculation manifest filename, and calculation-manifest hash.
- Locked repository HEAD and hashes of the runner, paper-flow, exit-simulator, profile/configuration, loader, and any other execution-relevant source files.
- Exact profile, scenario, timeframe, Order Flow status, command arguments, window size, step size, expected iterations, and terminal-position behavior.
- Collision-safe external output folder and confirmation that no existing evidence will be overwritten.
- Required Track A baseline, reproduction, trace, Track B sensitivity, regime report, safety report, and final-review filenames.
- Exactly one locked overall OOS classification rule from Section 9.

An addendum is not complete until its structure, hashes, boundaries, and outcome-blind declaration are validated before performance execution.

## 11. Stop Conditions

Stop immediately and preserve the current state when any of the following occurs:

- Candidate dates, contract, timezone, session, or usable range were selected or changed after viewing strategy outcomes.
- Any candidate authoritative timestamp overlaps previously evaluated evidence contrary to the locked non-overlap rule.
- Full dataset intake acceptance is absent, incomplete, rejected, or contradicted by later evidence.
- Raw, normalized, reference, source, plan, addendum, or evidence hashes do not match.
- The locked repository, profile, scenario, timeframe, Order Flow status, window, step, or terminal behavior differs from the addendum.
- Expected and actual iteration counts differ without a documented data-integrity explanation.
- Baseline and reproduction results are not exact byte-for-byte matches.
- Regime cutoffs were recalculated using candidate values or performance outcomes.
- Any losing, unresolved, insufficient, overlapping, or blocked evidence was silently removed.
- A target file already exists, overwrite protection fails, or raw-source traceability is lost.
- Sensitive information, credentials, account identifiers, private trading information, order instructions, or execution logic appears in an artifact intended for Git.
- Any step would require an unauthorized source, strategy, risk, Order Flow, exporter, threshold, paper, broker, API, live, or real-execution change.

A stopped run remains incomplete or invalid. Later checks must not override or conceal the original stop condition.

## 12. Completion and Safety Decision

- This document pre-registers a general future OOS and regime-separated validation framework.
- It does not claim that a future candidate currently exists or has passed intake.
- It does not classify the already evaluated `GC-202608-COMEX` period as OOS.
- It preserves Full Independent-Period Acceptance for the existing candidate and preserves its official reproducible 5m performance failure.
- It preserves the temporal-overlap limitation and the descriptive-only status of strict and inclusive counterfactual selections.
- A candidate-specific locked addendum remains mandatory before any future OOS performance execution.
- Paper-trading progression remains blocked.
- Numerical drawdown-threshold approval remains absent.
- Strategy, risk, Order Flow, source, and exporter changes remain unauthorized.
- Code freeze remains active.
- Live trading, broker connections, external APIs, and real execution remain prohibited.
