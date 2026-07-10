# Capital Protection Manual Pause and Emergency Stop Policy

## Scope

Documentation-only policy for manual pause and emergency stop behavior before any future control surface, persistence layer, broker integration, live data integration, or execution change.

## Purpose

Define trigger and reset authority, scope, priority, persistence, audit requirements, and new-entry behavior for manual pause and emergency stop decisions.

## Current implementation checkpoint

The capital protection engine currently treats emergency stop as the highest-priority block and manual pause as a separate high-priority block. Both return a blocked decision for new trading attempts, but no runtime trigger interface, reset interface, persistent state store, or dedicated audit trail is currently implemented.

## Resolved policy

Emergency stop remains the highest-priority capital protection state. Manual pause remains below emergency stop and explicit trading-disabled status, but above ordinary loss, target, and position-limit checks.

Emergency stop may be activated only by an explicitly authorized human operator or by a separately approved deterministic safety rule. External services, inferred conditions, and unreviewed automated agents must not activate it.

Emergency stop may be reset only by an explicitly authorized human operator after deliberate confirmation and a recorded reason. Automatic, time-based, restart-based, or agent-initiated reset is not approved.

Manual pause may be activated or resumed only by an explicitly authorized human operator through an explicit control surface. Silence, process restart, transient errors, and unreviewed automated agents must not change the pause state.

Emergency stop has platform-wide scope and blocks every new entry decision. Manual pause also blocks all new entries by default; strategy-specific, account-specific, or subsystem-specific pause scopes require explicit configuration, documentation, and tests.

Future implementations must persist active emergency-stop and manual-pause states across process restarts until an authorized reset or resume occurs. Every state change must record the timestamp, authorized actor, previous state, new state, scope, and stated reason.

Emergency stop and manual pause block new entry and re-entry decisions only. They must not automatically close, reduce, reverse, or otherwise modify existing positions; any separate protective exit behavior requires its own approved policy and tests.

Persisted control state must be loaded before any new entry evaluation. If required state is missing, unreadable, inconsistent, or cannot be authenticated, new entries must remain blocked until an authorized human resolves the condition.

Until an authenticated control surface, persistent state store, and audit trail are implemented and tested, the existing boolean fields remain research and test inputs only and must not be represented as production-ready operator controls.

## Not approved

This policy does not approve a production control interface, remote unauthenticated controls, automatic reset or resume, broker connectivity, live execution, MT5 integration, Sierra live integration, CME live data, external APIs, real orders, automatic liquidation, or automatic modification of existing positions.

## Test implications

Tests must verify emergency-stop priority, manual-pause blocking, explicit protection statuses, new-entry-only behavior, authorized trigger and reset rules, platform-wide default scope, persistence across restarts, fail-closed handling of invalid persisted state, complete audit records, and the absence of broker, live execution, or external API dependencies.

## Recommended next step

Review, index, and commit this documentation-only policy, then complete the remaining news policy before considering any authenticated control surface, persistence implementation, or offline integration tests.
