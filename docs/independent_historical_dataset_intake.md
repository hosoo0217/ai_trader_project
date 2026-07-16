# Independent Historical Dataset Intake Contract

## Purpose
This document defines the mandatory intake contract for any genuinely independent historical dataset proposed for deeper offline validation of the AI Trader MVP. A candidate dataset must satisfy this contract before it may be classified as independent validation evidence.
This contract is documentation-only and does not approve strategy, risk, drawdown-threshold, paper-trading, live-trading, broker, or external-API implementation work.

## Current Authoritative Baseline
- Canonical dataset: `private_data/sierra_chart/bulk_30d_sc_delayed`
- Earliest authoritative timestamp: `2026-06-03 18:00:00`
- Latest authoritative market timestamp: `2026-07-03 12:26:00`
- Latest usable full-footprint timestamp: `2026-07-03 12:23:00`
- Conservative non-overlap boundary: `2026-06-03 18:00:00` through `2026-07-03 12:26:00`, inclusive
- Available timeframes: 1m, 5m, and 10m; these cover the same calendar window and are not independent historical periods
- Accepted independent-period candidate: `GC-202608-COMEX`, with declared usable session coverage from `2026-05-13 18:00:00` through the timeframe-specific final complete bars on `2026-06-02`
- Full Independent-Period Acceptance was recorded on `2026-07-16`; the independent-dataset intake blocker is closed for this candidate, while code freeze and all paper/live progression restrictions remain active

## Conservative Non-Overlap Requirement
A candidate dataset qualifies as a fully independent historical period only when its complete declared usable range has zero overlap with the conservative baseline boundary `2026-06-03 18:00:00` through `2026-07-03 12:26:00`, inclusive.
Any authoritative market bar or footprint bar timestamp inside that boundary disqualifies the candidate from full independent-period classification.
Strict subsets, near-duplicates, partial re-exports, resampled copies, and alternate-timeframe exports of the same calendar window are non-independent and must not be used as independent validation evidence.
Independence must be determined from parsed authoritative timestamps and verified content, not from filenames, folder names, export dates, or file modification times.

## Intake Acceptance Levels
### Full Independent-Period Acceptance
A dataset may receive full independent-period acceptance only when its complete declared usable range has zero overlap with the conservative baseline boundary and it supplies complete matching Market OHLC and ACSIL full-footprint pairs for 1m, 5m, and 10m.
Only this acceptance level may be considered for independent-period validation evidence, subject to all remaining schema, matching, metadata, and quality requirements in this contract.

### Limited Diagnostic Intake
A dataset may receive limited diagnostic intake only when its complete declared usable range has zero overlap with the conservative baseline boundary and it contains a valid Market OHLC and ACSIL full-footprint pair for only one or two timeframes; the intake is restricted to explicitly limited offline diagnostic work.
Limited diagnostic intake must not be classified as full independent-period evidence and must not be used to approve or complete robustness validation, out-of-sample validation, numerical drawdown thresholds, strategy changes, risk changes, paper trading, live trading, broker integration, or external-API work.
Every report produced from a limited diagnostic intake must clearly state the missing timeframes and the restricted evidence classification.

## Required Dataset Pairs
Full independent-period acceptance requires all six source files as three complete timeframe-matched pairs:
- 1m Market OHLC and 1m ACSIL full footprint
- 5m Market OHLC and 5m ACSIL full footprint
- 10m Market OHLC and 10m ACSIL full footprint
An OHLC-only file, a footprint-only file, or a pair assembled from different timeframes is incomplete and must be rejected for that timeframe.
Each pair must describe the same instrument, contract, timezone, session configuration, and declared historical period.
A limited diagnostic intake may contain one or two complete timeframe-matched pairs, but its classification remains restricted as defined above.

## Market OHLC Requirements
Each Market OHLC file must be a Sierra Chart CSV export with a header and the following authoritative market fields:
- `Date`
- `Time`
- The first `Open` column
- The first `High` column
- The first `Low` column
- The first `Last` column
- `Volume`
The first `Open`, `High`, `Low`, and `Last` price group is authoritative when additional or duplicate study-generated OHLC columns are present. `Last` is the authoritative close value; a column named `Close` is not required.
`Date` and `Time` must combine into parseable authoritative timestamps. Timestamps must be chronological and must contain no duplicate authoritative market timestamps.
Validation evidence must record the first authoritative timestamp, last authoritative timestamp, and total market data-row count.
All expected-interval gaps must be detected and reported. A gap may be accepted only when supported by a documented session break, weekend, exchange holiday, chart-loading boundary, or a verified no-trade interval that satisfies every requirement below.
Any unexplained gap blocks acceptance until it is resolved or the declared usable range is reduced and documented.
OHLC values must be numeric and internally valid, and `Volume` must be numeric and non-negative. Files must use UTF-8 or ASCII encoding; headerless files are rejected.

## Verified No-Trade Intervals
An expected timestamp with no bar may be accepted as a verified no-trade interval only when all of the following evidence is recorded:
- The exact missing interval boundaries and expected timestamps are listed.
- The chart used `Gap Fill: None`, `Include Columns With No Data: No`, the documented timezone and session configuration, and the declared timeframe.
- The authoritative Market OHLC export contains no row for every expected timestamp in the interval.
- The matching ACSIL full-footprint export contains no `DateTime` for every expected timestamp in the interval.
- For a missing 5m or 10m interval, every constituent expected 1m Market OHLC timestamp and every constituent expected 1m footprint timestamp are also absent.
- For a missing 1m interval, the surrounding retained 1m bars remain chronological and matched, and the absence is reproduced after a documented Sierra Chart reload or authoritative historical-data re-download with no unresolved download or loading error.
- The source-level verification method, review time, relevant Sierra Chart message-log result, and reviewer are recorded.
- No empty, previous-close, zero-volume, synthetic, interpolated, resampled, corrected, or manually inserted bar is used to fill the interval.

Sierra Chart documents that `Include Columns With No Data` creates bars for periods of no trading by setting OHLC to the previous close, while `Gap Fill: None` avoids filling price gaps and is required with Numbers Bars to prevent false price levels. This contract therefore preserves a source-verified absence instead of manufacturing a bar:
- https://www.sierrachart.com/index.php?page=doc/ChartSettings.html#IncludeColumnsWithNoData
- https://www.sierrachart.com/index.php?page=doc/ChartSettings.html#GapFill

Absence from Market OHLC and footprint exports alone is not sufficient because both exports may share the same missing source records. Any interval that lacks the required source-level reproduction or has a download, loading, timezone, session, or configuration ambiguity remains unexplained and blocks acceptance.

## ACSIL Full-Footprint Requirements
Each full-footprint file must be produced by the current data-only ACSIL exporter `sierra_acsil/ai_trader_full_footprint_export.cpp`.
The required header must match this exact schema and order:
`DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades`
Each row must represent one price level within one bar. A bar is expected to contain multiple price-level rows.
Repeated `DateTime` values and repeated `BarIndex` values are valid only when they represent distinct price-level rows belonging to the same bar.
`DateTime` must be parseable, `BarIndex` must be numeric, and `Price` must be numeric.
`BidVolume`, `AskVolume`, `TotalVolume`, and `NumTrades` must be numeric and non-negative.
For every row, `Delta` must equal `AskVolume - BidVolume`.
The footprint data-row count must be greater than the unique candle count for the declared usable range; a bar-summary-only export is rejected.
Validation evidence must record the first footprint timestamp, last footprint timestamp, unique candle count, and total price-level data-row count.
The exporter and exported file must contain data only. Trading signals, strategy decisions, order instructions, or execution logic are not permitted in the intake artifact.

## Market and Footprint Matching
Each timeframe pair must be matched using parsed authoritative timestamps after applying the documented timezone and session configuration.
The declared usable range must be a shared range fully covered by both the Market OHLC file and the corresponding ACSIL full-footprint file.
Within that declared usable range, every authoritative Market OHLC timestamp must have one or more corresponding footprint rows, and every unique footprint `DateTime` must match exactly one authoritative Market OHLC timestamp.
Footprint timestamps with no corresponding market bar are orphan bars and block acceptance. Market timestamps with no corresponding footprint rows inside the declared usable range also block acceptance.
Trailing or leading bars outside the shared coverage may be excluded only by reducing and recording the declared usable range; they must not be silently ignored.
Any incomplete final market bar or footprint bar must be detected and reported before the declared usable range is accepted.
Authoritative timestamps must not be silently corrected, and rows must not be deleted merely to make validation pass.
The matched pair must use the same timeframe, instrument, contract, timezone, and session configuration.
Unique market-bar count, unique footprint-bar count, matched-bar count, missing-bar count, orphan-bar count, first matched timestamp, and last matched timestamp must be recorded.
Any matched derivative file must remain traceable to its raw source files through recorded filenames and SHA-256 hashes.
Any unexplained timestamp, coverage, instrument, contract, timezone, session, or timeframe mismatch blocks acceptance.

## File Naming and Overwrite Protection
The current ACSIL exporter writes to the fixed output path `private_data/sierra_chart/gc_full_footprint_acsil_export.csv` and uses truncation behavior. Starting another export before preserving the current output may permanently overwrite it.
Immediately after every timeframe export, the operator must complete these steps before starting another export:
1. Confirm that the fixed output file exists.
2. Confirm that the exact required header is present and that at least one data row exists.
3. Parse and record the first and last footprint timestamps, unique bar count, total data-row count, file size, and SHA-256 hash.
4. Rename or copy the fixed output to a unique final filename containing the instrument, timeframe, and declared date range.
5. Confirm that the preserved file exists, contains data rows, and has the same SHA-256 hash as the fixed output captured for that export.
6. Only after the preserved file passes these checks may the next timeframe export begin.
Final Market OHLC and footprint filenames must identify their instrument, timeframe, and declared period. Generic, ambiguous, or reused final filenames are rejected.
An existing preserved dataset file must not be overwritten. Any filename collision must stop the intake operation until a new unique filename is selected.

## Required Metadata
A written metadata record must accompany every submitted timeframe pair and must include:
- Dataset source, acquisition method, and export date
- Instrument symbol, contract identifier, timeframe, timezone, and session configuration
- Final Market OHLC and full-footprint filenames and repository-external storage locations
- File size and SHA-256 hash for every submitted file
- Raw first and last timestamp for each file
- Declared usable first and last matched timestamp
- Market row count, footprint data-row count, unique market-bar count, and unique footprint-bar count
- Matched-bar count, missing-bar count, orphan-bar count, duplicate authoritative timestamp count, and detected-gap summary
- Every accepted gap, its documented explanation, and all required verification evidence for each accepted no-trade interval
- Requested classification: full independent-period acceptance or limited diagnostic intake
- Reviewer, review date, final classification, unresolved issues, and rejection reasons when applicable
Missing, ambiguous, or internally inconsistent metadata blocks acceptance until corrected.

## Independence Classification
Every intake review must assign exactly one of the following evidence classifications:
### Full Independent-Period Acceptance
Use this classification only when the complete declared usable range has zero overlap with the conservative baseline boundary, all 1m/5m/10m pairs are complete, and every contract requirement has passed.

### Limited Diagnostic Intake
Use this classification only when the declared usable range has zero overlap with the conservative baseline boundary but only one or two complete timeframe pairs are available. This classification remains diagnostic-only and is not full independent-period evidence.

### Non-Independent Dataset
Use this classification when any authoritative timestamp overlaps the conservative baseline boundary, or when the candidate is a subset, near-duplicate, re-export, resample, or alternate-timeframe representation of the existing baseline period. Schema validity does not make an overlapping dataset independent.

### Rejected Intake
Use this classification when a required timeframe pair is incomplete; required files, schema, metadata, matching evidence, integrity checks, or explained-gap evidence are missing or invalid; sensitive or private information is present; overwrite-protection evidence has been lost; or the recorded acceptance evidence is otherwise insufficient.
A rejected intake may be reviewed again only after the blocking defects are corrected and the full intake process is repeated.
Classification must be supported by recorded evidence. Filename, folder placement, export date, or operator assumption alone is insufficient.

## Validation Order
Validation must proceed in this order:
1. Preserve every raw source and fixed exporter output before another export, and record filenames, sizes, and SHA-256 hashes.
2. Verify all required metadata, instrument identity, contract, timeframe, timezone, session configuration, and declared usable range.
3. Parse authoritative timestamps and test the complete declared usable range against the conservative non-overlap boundary.
4. Validate Market OHLC schema, order, numeric integrity, timestamps, row counts, duplicates, and gaps; apply every source-level verification requirement before accepting a no-trade interval.
5. Validate ACSIL full-footprint schema, price-level structure, numeric integrity, delta equation, timestamps, and counts.
6. Match each timeframe pair, report missing, orphan, leading, trailing, and incomplete final bars, and verify raw-source traceability.
7. Apply overwrite-protection and safety checks, then assign exactly one evidence classification and record the decision.
Any failed step stops the sequence; later checks must not override or conceal an earlier failure.

## Stop Conditions
Intake and validation must stop immediately when any of the following conditions is found:
- Any authoritative timestamp overlaps the conservative baseline boundary; independent-period review stops and the dataset is classified as non-independent.
- A required timeframe pair is incomplete, or required schema, metadata, hash, numeric integrity, or matching evidence is missing or invalid.
- An unexplained or unverified gap, missing bar, orphan bar, incomplete final bar, timezone mismatch, session mismatch, contract mismatch, or timeframe mismatch remains unresolved.
- A preserved output would be overwritten, a filename collision occurs, or required overwrite-protection evidence cannot be verified.
- Sensitive or private information, trading signals, strategy decisions, order instructions, or execution logic is present in the intake artifacts.
- Raw-source traceability is lost, or timestamps or rows were silently corrected, deleted, or otherwise altered to obtain a pass.
A stopped intake remains non-independent or rejected unless its applicable blocking defects are corrected and the full validation order is repeated.

## Safety Boundary
- This contract authorizes documentation, dataset intake, and offline diagnostic validation only.
- Code freeze remains active. Python source code, strategy logic, risk logic, paper-trading behavior, Order Flow execution behavior, and exporter source code must not be changed under this contract.
- Live trading, broker connections, MT5, Sierra live integration, CME live integration, external APIs, and real orders are not authorized.
- No numerical drawdown threshold, strategy change, risk change, robustness completion, out-of-sample completion, or paper progression is approved by any intake classification.
- Files under `private_data`, candidate raw datasets, and generated private reports must not be staged or committed; only explicitly reviewed documentation paths may enter Git.
- Dataset acceptance records evidence classification only and must not be interpreted as deployment or trading approval.
- Missing, ambiguous, conflicting, or unverified evidence must fail closed with no progression.

## Acceptance Decision
Every completed review must record exactly one classification with the reviewed files and hashes, declared usable range, reasons, unresolved issues, reviewer, and review date.
Full acceptance requires zero overlap, all three complete timeframe pairs, and every check to pass; limited intake requires zero overlap, only one or two complete pairs, and diagnostic-only use.
Any overlap, subset, near-duplicate, re-export, resample, or alternate-timeframe baseline representation is non-independent; any incomplete, invalid, private, overwrite-unsafe, or untraceable intake is rejected.
One candidate completed this contract with Full Independent-Period Acceptance on `2026-07-16`, recorded in external review `intake_review_2026-07-16.md` with SHA-256 `5B8DCA92A95B221C83AEBEAC2AE90FBC7A73A17FFD1B45E000CE3098C2AC941A`; this evidence classification does not authorize strategy, risk, threshold, paper, broker, API, or live progression.
