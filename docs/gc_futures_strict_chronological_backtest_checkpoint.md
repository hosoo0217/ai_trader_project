# GC Futures Strict Chronological Backtest Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `GC-FUTURES-STRICT-CHRONOLOGICAL-BACKTEST-CHECKPOINT-2026-08-02`.
- Formal decision commit:
  `5925d7410697ba4ffdb442500e0febf7cf23490b`.
- Formal decision SHA-256:
  `97FCE19809855514A20ACFBA3CDB975DBF748BFADC91ED9879F6B3A86C3DAFAA`.
- Task classification: isolated bounded research-backtest implementation.
- Strategy, AI, integration, paper, broker, and live status: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

This checkpoint proves deterministic contract implementation only. It does not
claim strategy quality, realistic execution, accepted historical data,
profitability, AI training, paper readiness, or live readiness.

## 2. Exact Authorized Scope

Exactly these three newly created paths are in scope:

- `core/gc_chronological_backtest.py`;
- `tests/test_gc_chronological_backtest.py`;
- `docs/gc_futures_strict_chronological_backtest_checkpoint.md`.

No external fixture was created. All market, calendar, candidate, lifecycle,
malformed-input, and identity evidence is inline in the dedicated test module.
No package initializer, legacy backtest, paper flow, exit simulator, strategy,
AI, SMC detector, risk, broker, configuration, requirement, private-data,
report, or integration path changed.

The pre-existing untracked
`docs/smc_v2_diagnostic_context_integration_change_proposal.md` is outside this
task and remained untouched.

## 3. Test-First Evidence

The dedicated tests were created before the production module. The first
focused run produced the expected RED collection result:

- `ModuleNotFoundError: No module named 'core.gc_chronological_backtest'`;
- `1 error in 2.07s`.

The first production pass collected `73` tests and produced:

- `71 passed, 2 failed in 0.81s`.

Both failures were test-fixture defects: target-gap bars had close ticks outside
their corrected OHLC boundaries. Correcting only the synthetic fixtures yielded:

- `73 passed in 0.65s`.

An independent semantic inspection then added tests first for:

- unrequested calendar evidence when the requested bar/candidate scope is empty;
- exact old-session-close to next-session-open causal continuity;
- UTC-normalized public trade and snapshot moments;
- stop-loss identity geometry after configured adverse slippage;
- internally malformed later bar fields with determinable cutoff and immutable
  prior evidence.

That RED correction run produced:

- `68 passed, 5 failed in 0.86s`.

The bounded source correction made all five cases pass without changing the
public API or 48-case matrix. A subsequent coverage audit expanded existing
logical cases for malformed supplied counterparts under missing top-level
context, positive normalization, runtime timezone unavailability, UNKNOWN over
prior COMPLETE evidence, identity forbidden fields, every public frozen model,
exact signatures, later malformed calendar/candidate cutoff, and final INVALID
over earlier AMBIGUOUS precedence.

The final focused result is:

- `83 passed in 0.70s`;
- exactly `48` sequential logical cases;
- `35` additional collected executions from parameterization and reflection.

The final full regression result is:

- `1861 passed in 10.66s`.

Every focused and full run used `-p no:cacheprovider`.

## 4. Locked Public Surface

The module exports exactly:

- `GC_CHRONOLOGICAL_BACKTEST_VERSION`;
- `GC_CHRONOLOGICAL_TIMEFRAME`;
- `GC_CHRONOLOGICAL_TIMEZONE`;
- `GCBacktestDirection`;
- `GCBacktestRunStatus`;
- `GCCandidateDecisionStatus`;
- `GCTradeExitReason`;
- `GCChronologicalBar`;
- `GCBacktestCandidate`;
- `GCChronologicalBacktestConfig`;
- `GCCandidateDecision`;
- `GCBacktestTrade`;
- `GCEquitySnapshot`;
- `GCChronologicalBacktestResult`;
- `make_gc_chronological_backtest_id`;
- `run_gc_chronological_backtest`.

Both public functions are exact keyword-only APIs. All seven public dataclasses
are frozen and have the exact decision-record fields and result defaults. No
adapter, registry, callback, strategy, model, broker, file, or external API is
publicly exposed.

## 5. Input and Configuration Contracts

The runner accepts exact tuples or `None` for:

- fully closed 5-minute `GCChronologicalBar` values;
- canonical versioned `KillZoneCalendarEntry` values;
- opaque-ID immutable `GCBacktestCandidate` values.

Bar indices and normalized UTC close timestamps are independently strictly
increasing. OHLC and volume use exact non-boolean integers. Bars must be closed,
have valid geometry, and remain exactly five minutes apart inside one session.
Cross-session adjacency is valid only when the earlier bar closes exactly at its
session close and the later bar opens exactly at the next canonical session
open. No sorting, filling, deduplication, wall-clock fallback, or synthesized bar
is used.

The exact GC contract token, normalized `5M`, runtime tzdata version, positive
Decimal tick size/value/balance, nonnegative Decimal costs, nonnegative integer
slippage, and positive contract cap are caller supplied. Generic GC, XAUUSD,
continuous aliases, floats, booleans, non-finite Decimals, and implicit defaults
fail closed.

## 6. GC Calendar and Time Authority

The only SMC dependency imports are the canonical immutable
`KillZoneCalendarEntry` and `KillZoneSessionStatus` types. The fixed timezone is
IANA `America/New_York`; the normalized caller version must match the available
runtime tzdata version exactly.

A standard trade date opens on the prior calendar date at local `18:00`
inclusive and closes at local `17:00` exclusive. Early close keeps the canonical
open and supplies a strictly earlier valid close. Session-closed entries forbid
timestamps. The daily maintenance interval is ineligible. Calendar trade dates
are strictly ordered and use one immutable version.

Unavailable timezone data, unavailable New York rules, malformed session
geometry, version conflict, duplicate dates, and unexplained gaps are invalid.
Canonical missing coverage is unknown only when no determinable malformed
evidence has higher precedence.

## 7. Candidate, Entry, and Position Chronology

Candidates carry a lowercase opaque SHA-256 identity, exact BUY or SELL
direction, a decision index/timestamp that matches one closed bar, immutable
stop/target boundaries, positive maximum holding bars, and bounded contracts.
The runner does not recompute unavailable strategy or model provenance.

One valid candidate is recorded pending at its decision-bar close and may enter
only at the next eligible bar open. BUY entry slippage adds ticks; SELL subtracts
ticks. The post-slippage fill must remain strictly between stop and target. A
missing next bar remains pending UNKNOWN, while invalid fill geometry is a
terminal rejection that no later bar may rescue.

At most one pending entry or one open position exists. Candidates received
while occupied are rejected and never queued. If a trade closes and a new
candidate is decided on the same bar, the new candidate still waits for the
following bar.

## 8. Exit and Accounting Semantics

Each holding bar uses exact precedence:

1. stop and target touches;
2. conservative stop when both touch;
3. the single touched boundary;
4. expiry close;
5. final eligible session close;
6. otherwise remain open.

The entry bar is holding bar one. BUY stop gaps use the worse of open and stop;
SELL mirrors it. Target gaps receive no favorable improvement. Configured exit
slippage is applied once and adversely with no hidden optimistic clamp. Missing
the required final session bar never synthesizes an exit and returns UNKNOWN.

Gross tick PnL, Decimal tick value, two-sided per-contract commission and fee,
net PnL, ordered balance, and snapshots reconcile exactly. Dynamic local Decimal
precision and canonical serialization make arbitrary magnitude, signed zero,
and current Decimal-context changes deterministic.

## 9. Atomicity and Status Precedence

Each closed-bar group uses immutable pre-group state. Determinable malformed
bars, calendars, or candidates preserve byte-for-byte decisions, trades, and
snapshots from strictly prior complete groups and promote nothing from or after
the failing group. An unknowable malformed effective moment claims no prefix and
leaks no nested exception.

A duplicate candidate identity is INVALID. Distinct same-moment candidates
atomically emit canonical ordered ambiguity rejections and no entry/trade/
snapshot from that group. Same-group tuple permutation cannot change the result
or run identity.

Final status precedence is exactly:

`INVALID > UNKNOWN > AMBIGUOUS > COMPLETE > NONE`

Tests explicitly cover final INVALID over earlier AMBIGUOUS and UNKNOWN over a
strictly prior completed trade while preserving that earlier evidence.

## 10. Deterministic Identities

The builder implements exactly `RUN`, `DECISION`, `TRADE`, and `SNAPSHOT`.
Canonical identity JSON uses sorted keys, compact separators, uppercase
instrument/timeframe, exact enum tokens, UTC microsecond timestamps, canonical
Decimal text, version binding, and lowercase SHA-256.

- RUN binds full ordered bar and calendar digests plus full candidate evidence;
  same-moment candidate members are serialized by candidate ID because supplied
  member order is not chronology.
- DECISION binds exact candidate, status/reason pair, and effective moment.
- TRADE binds direction, size, entry, boundaries, exit, lifecycle reason, exact
  ticks, PnL, and cost and recomputes locally provable geometry/accounting.
- SNAPSHOT binds effective moment, exact balance, and ordered unique complete
  trade-ID history.

Every optional builder field is kind-specific required or forbidden. Unknown
kinds, missing fields, forbidden fields, malformed hashes, impossible geometry,
wrong reason tokens, duplicate history, incorrect PnL, and malformed nested
values raise only TypeError or ValueError.

## 11. Prefix Invariance and Repeatability

A comparable prefix ends only after a complete bar group with no pending entry,
open position, partial candidate group, or missing calendar evidence. Strictly
later complete extension preserves every earlier decision, trade, snapshot,
identity, PnL, and balance byte-for-byte.

Pending/open prefixes, same-effective append, historical insertion, repair,
reorder, source replacement, or config/cost change are explicitly ineligible.
Equivalent normalized inputs produce identical results regardless of Decimal
context, timestamp offset representation, current wall clock, or hash lexical
order.

## 12. Exact 48-Case Reconciliation

The test file contains exact sequential `# Case 1` through `# Case 48` markers.
They reconcile one-for-one with Section 21 of the formal decision. Tests cover:

- missing/malformed precedence and empty-scope semantics;
- contract/timeframe/bar/calendar/candidate validation;
- entry, occupancy, mirrored exits, collision, gaps, expiry, and session close;
- exact costs, PnL, balances, and arbitrary Decimal evidence;
- exhaustive identity/public reflection and frozen output contracts;
- chronological cutoff, atomic no-promotion, status precedence, prefix
  invariance, repeatability, and forbidden integration/import surfaces.

Parameterization increases collected executions to `83` without changing the
locked logical-case count.

## 13. Artifact Evidence

Final bounded artifacts before staging are:

- `core/gc_chronological_backtest.py`
  - SHA-256:
    `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A`;
  - `62,493` bytes;
  - `1,772` lines.
- `tests/test_gc_chronological_backtest.py`
  - SHA-256:
    `1C5D7588163B2DB340CEA59370A38F1789E3BF38BE7F036EF448E0A6E0BD343E`;
  - `37,410` bytes;
  - `971` lines.

The checkpoint hash, byte count, and line count are intentionally measured by
the independent final audit after this self-referential document is complete.

## 14. Dependency and Freeze Evidence

Locked dependency hashes remain:

- `smc/kill_zones.py`:
  `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21`;
- `core/backtest_runner.py`:
  `6596254199AEDB9AE16584D0228B511D5C50525A117F2932AD293A0B754A16E0`;
- `core/paper_trading_flow.py`:
  `B72F66692BE035E79CFFD2E6FE449397B845BB08D3610AE1A00A8C52669CEAB4`;
- `core/exit_simulator.py`:
  `852EC94DE37F28150DC83F64D978EBC447C8AD2FE9F3D8ACD468AF4591710285`.

HEAD and local `origin/main` were both
`5925d7410697ba4ffdb442500e0febf7cf23490b` when final tests ran. The exact
three implementation files remain untracked and unstaged. No integration path
changed. Global freeze remains active everywhere outside the bounded exception.

## 15. Promotion and Rollback Boundary

Promotion requires all of:

- independent final code/test/scope/hash/diff audit PASS;
- exact three-path staging authorization;
- cached full-content and formatting audit;
- separate local commit authorization or bounded autonomous grant;
- separate privacy-aware push authorization;
- post-push completion/readiness audit.

Passing this checkpoint does not authorize strategy candidate generation,
historical-data acceptance, backtest execution on private data, AI training,
package exports, legacy-runner replacement, paper, broker, live, or integration.

Rollback is limited to discarding these exact three unaccepted paths and
returning to commit `5925d7410697ba4ffdb442500e0febf7cf23490b`. Any change to
the public API, four identity payloads, 48-case matrix, single-position
chronology, calendar authority, accounting rules, or three-path scope is a
mandatory stop requiring a new decision.

## 16. Final Checkpoint Status

Status:

`READY_FOR_INDEPENDENT_FINAL_CODE_TEST_SCOPE_HASH_DIFF_AUDIT`

No staging, commit, push, integration, strategy, AI training, paper, broker, or
live action has been performed. Global code freeze remains active.
