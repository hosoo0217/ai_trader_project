# SMC V2 and Volume Profile Shared-Primitives Checkpoint

- Checkpoint ID: `SMC-V2-SHARED-PRIMITIVES-CHECKPOINT-2026-07-19`
- Review date: `2026-07-19`
- Implementation parent: `03799c8f5fea1d8e9b36c86efd4ef919f7d4f539`
- Formal decision record: `docs/smc_v2_volume_profile_diagnostic_freeze_lift_decision.md`
- Formal decision SHA-256: `E6A68EA0A5BFC3815D04705E362E013BABE53A90951C0AB86EC0B323B5B9759C`
- Status: bounded shared-primitives first-task implementation completed and locally validated; not integrated or promoted.

## 1. Bounded Exception and Global Freeze

- The explicit bounded exception became operationally effective only for this shared-primitives first task.
- The exception did not lift the global code freeze for any unrelated file or capability.
- Integration into the existing SMC, CRT, decision, backtest, risk, execution, or reporting paths is not authorized.
- Staging, commit, push, paper progression, live progression, broker access, and real execution are not authorized.
- The global code freeze remains active outside the exact three-path scope recorded below.

## 2. Exact Three-Path Scope

The only created or changed paths in this task are:

1. `smc/smc_v2_primitives.py`
2. `tests/test_smc_v2_primitives.py`
3. `docs/smc_v2_volume_profile_shared_primitives_checkpoint.md`

No package initializer, existing Python source, configuration, fixture file, or existing documentation file was changed. Synthetic fixtures remain inline in the dedicated test module.

## 3. Implemented Public API

The standalone module provides the following shared vocabulary and deterministic helpers:

- Constant: `FLOAT_ALIGNMENT_TOLERANCE_TICKS` with exact decimal value `1e-9` ticks.
- Enum: `SMCV2PrimitiveStatus`.
- Enum: `SMCV2Direction`.
- Enum: `SMCV2LifecycleState`.
- Frozen dataclass: `SMCV2EventProvenance`.
- Frozen dataclass: `SMCV2TickRange`.
- Frozen dataclass: `SMCV2LifecycleEvent`.
- Function: `normalize_utc_timestamp`.
- Function: `validate_tick_size`.
- Function: `price_to_ticks`.
- Function: `ticks_to_price`.
- Function: `validate_lifecycle_history`.
- Function: `make_deterministic_id`.

The module uses only Python standard-library dependencies and performs no file, network, broker, environment, configuration, or application-registry access.

## 4. Numeric and Timestamp Invariants

- Tick size must be finite and strictly positive.
- Price and tick inputs must be finite numeric values and reject booleans.
- Price alignment is evaluated in tick space using the locked `1e-9`-tick tolerance.
- Aligned prices convert to integral tick indices without silent truncation.
- Tick-to-price conversion is deterministic through decimal arithmetic.
- Naive timestamps are rejected; timezone-aware timestamps normalize to UTC.
- Timezone-aware timestamps normalize to timezone-aware UTC `datetime` values without inventing a timezone.

## 5. Range and Lifecycle Invariants

- A tick range requires `lower_tick <= upper_tick`.
- Provenance requires non-negative source and decision indices and a normalized UTC decision timestamp.
- Source-event and first-known confirmation indices and timestamps remain separate in immutable provenance.
- A lifecycle event separately records its previous state, next state, index, timestamp, and reason.
- Lifecycle histories must be non-empty, chronological, and state-chain-consistent.
- Broken state chains and detector-specific invalid state transitions are rejected.
- Terminal lifecycle states cannot be followed by later transitions.
- Unknown or ambiguous states remain explicit and are never silently promoted to valid detections.

## 6. Deterministic Identity Invariants

- Deterministic identities use canonical JSON serialization of the reviewed identity fields and SHA-256.
- Detector version, instrument, and timeframe text use explicit case normalization.
- Source indices, direction, and immutable integer-tick boundaries are included as stable inputs.
- Empty text, invalid source indices, wrong direction types, and wrong boundary types fail closed.
- The locked golden-vector digest is `802b6904dd2583ccd69ffc809457644ba218a93eab8ee7a6ca21ac8a0fb1b180`.

## 7. Test-First Evidence

- The dedicated test module was created before the implementation module.
- Expected RED gate: collection failed only because `smc.smc_v2_primitives` did not yet exist.
- No production behavior was altered to obtain the RED gate.
- GREEN focused result: `83 passed`.
- Full regression result: `964 passed`.
- The regression total consists of the previous `881` tests plus `83` new shared-primitives cases.

## 8. Unit-Test Matrix

The inline synthetic test matrix covers:

- Exact enum values and public export surface.
- Frozen dataclass behavior and constructor validation.
- UTC normalization, offset conversion, and naive-time rejection.
- Tick-size validation, exact alignment, accepted boundary tolerance, rejected over-tolerance values, and negatives.
- Price-to-tick and tick-to-price round trips.
- Range ordering, point ranges, width, and immutable-boundary behavior.
- Provenance validation, event/confirmation separation, UTC normalization, and immutability.
- Allowed lifecycle transitions, state-chain continuity, chronological ordering, and terminal-state enforcement.
- Deterministic-ID repeatability, text canonicalization, input sensitivity, golden vector, and invalid-input rejection.
- Static isolation checks cover I/O, application wiring, configuration lookup, and import-time side effects.

## 9. Isolation and Non-Integration Evidence

- Direct import of the new module exists only in `tests/test_smc_v2_primitives.py` at this checkpoint.
- `smc/__init__.py` remains unchanged with SHA-256 `C8FE33277193D142CF975D1B56AED5432D495A0B01F17F7AD155BDA3DE3FEE0B`.
- The source imports only `collections.abc`, `dataclasses`, `datetime`, `decimal`, `enum`, `hashlib`, and `json`.
- No `main.py`, decision context, SMC engine, CRT engine, runner, profile, risk, execution, trace, or report path imports the module.
- The module does not read candidate data and does not produce trading signals, orders, PnL, readiness decisions, or external evidence.

## 10. Artifact Identities Before Checkpoint Audit

- `smc/smc_v2_primitives.py` SHA-256: `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`.
- `tests/test_smc_v2_primitives.py` SHA-256: `ADD1E6AB6F09FE1D4379F3C008B40F9D56F248FD654525782EE6A41D774CBE0E`.
- The checkpoint document identity is calculated only after this record is written and is not self-embedded.

## 11. Rollback

Because the work is untracked, unintegrated, and unpromoted, bounded rollback consists only of removing the exact three newly created paths after an explicit rollback instruction. No existing source or documentation needs restoration. Destructive rollback is not authorized by this checkpoint itself.

## 12. Stop Conditions

Stop without integration or promotion if any of the following occurs:

- Any path outside the exact three-path scope changes.
- A focused or full-regression test fails.
- The `1e-9`-tick tolerance changes or becomes float-dependent.
- Any import-time I/O, external dependency, application wiring, mutable global registry, configuration read, or hidden fallback appears.
- Timestamp, tick alignment, lifecycle, provenance, or identity validation becomes permissive or non-deterministic.
- The new API conflicts with the approved specification or requires an unapproved integration decision.
- The working tree contains an unexplained staged, modified, or untracked path.

## 13. Checkpoint State

- `BOUNDED_EXCEPTION_OPERATIONALLY_EFFECTIVE=True`
- `FIRST_TASK_IMPLEMENTATION_COMPLETED=True`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_TOTAL=83`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_TOTAL=964`
- `INTEGRATION_PERFORMED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_PERFORMED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
- `PAPER_PROGRESSION_REMAINS_BLOCKED=True`
- `LIVE_PROGRESSION_REMAINS_BLOCKED=True`

## 14. Next Gate

The next permissible action is an independent final code, test, scope, and diff audit of these exact three paths. A passing audit may authorize a later staging request, but this checkpoint does not itself authorize staging, commit, push, or integration.
