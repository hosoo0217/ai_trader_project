# SMC V2 Dealing Range Terminal-Context Correction Change Proposal

## 1. Decision Status

This documentation-only proposal is the sole freeze-lift candidate for correcting the
post-invalidation Dealing Range causal-context defect exposed by the accepted GC Phase A Candidate
Evidence private run. It authorizes no implementation, private output publication, feature/label
build, training, OOS access, integration, stage, commit, or push by itself.

The global code freeze remains active. A later explicit implementation authorization may lift it
only for the exact three paths in Section 5.

## 2. Evidence Boundary

The proposal is based only on read-only inspection of the accepted V3 development dataset, accepted
structural seed, current public detector code, current tests, and the failed Candidate Evidence run.
No private input or accepted artifact was modified.

The relevant deterministic evidence is:

- accepted dataset ID:
  `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- accepted structural seed ID:
  `e741a230d961cda290f5d20d4fd5a0b4b1bd2cb54795c1d0c009a2e17148e8f0`;
- `54` development segments and `0` opened OOS bars;
- Candidate Evidence result `UNKNOWN`, exact reason
  `initial CHOCH lacks prior external range context`, one complete segment result, zero candidates,
  and no private Candidate output;
- segment ordinal `0` is independently `VALID` for Dealing Range and emits `60` snapshots;
- segment ordinal `1` starts with a canonical bearish `BOS` at local index `12`, not with `CHOCH`;
- segment ordinal `1` contains `17` canonical structure events and reaches a bullish EXTERNAL
  `INVALIDATED` snapshot at local index `270` before the later bearish `CHOCH` at local index `274`;
- the public segment-1 Dealing Range result is `UNKNOWN`, preserves `42` snapshots, and stops at that
  later `CHOCH`.

Therefore the checkpoint wording that attributed the failure to the first accepted segment starting
with `CHOCH` is not accepted causal evidence and must be corrected during implementation.

## 3. Confirmed Root Cause

`analyze_dealing_ranges()` correctly constructs an ACTIVE range from the earlier same-segment BOS
history. When a later fully closed observation invalidates the active protected boundary without a
same-moment reversal event, the detector emits the canonical terminal `INVALIDATED` snapshot and
sets its mutable active pointer to `None`.

The immutable terminal lineage, terminal transition, prior direction, and causal moment remain in
the already-emitted snapshot history. However, `_validate_event_state_relationship()` currently
tests only the mutable active pointer. Any strictly later `CHOCH` therefore enters the same branch as
a truly initial or lone `CHOCH` and raises `UNKNOWN`, even though same-input prior external-range
context is available.

This is an internal lifecycle-context omission. It is not a missing cross-segment lookback, dataset
gap, structural-seed identity defect, Inducement defect, or Candidate aggregation defect.

## 4. Correction Objective

The detector must distinguish:

1. a genuinely initial or lone `CHOCH` with no same-input prior external-range history; from
2. a strictly later opposite-direction `CHOCH` following an immutable canonical terminal
   `INVALIDATED` external range in the same complete input tuple.

Only the second case may use terminal history as causal validation context and construct a new
ACTIVE lineage. The old terminal lineage is never reactivated, rewritten, replaced, enriched, or
removed.

## 5. Reserved Future Implementation Scope

Future implementation is reserved to exactly:

- `smc/dealing_range.py`;
- `tests/test_dealing_range.py`;
- `docs/smc_v2_dealing_range_checkpoint.md`.

No Candidate Evidence, structural-seed, dataset, private-data, shared-primitives, package-export,
configuration, feature/label, training, strategy, risk, execution, trace, or integration file is in
scope.

## 6. Explicit Non-Goals

The correction must not:

- carry bars, events, swings, snapshots, state, or lookback across a segment boundary;
- change structural-event generation or relabel BOS/CHOCH evidence;
- infer missing events or observations;
- reinterpret an initial CHOCH as BOS;
- weaken malformed-input, identity, chronology, or atomic-group validation;
- change public dataclasses, enums, signatures, defaults, constants, exports, or identity payloads;
- create a strategy signal, direction recommendation, confidence, trade, risk, entry, exit, PnL,
  feature, label, model, or training authority;
- read or write private data during unit tests.

## 7. Immutable Input Contracts

The existing frozen `DealingRangeSwing`, `DealingRangeObservation`, and
`DealingRangeStructureEvent` contracts remain exact. Supplied tuples remain caller-owned,
chronological, immutable evidence. The correction may retain only an internal reference to a
canonical terminal range already derived during the same public analyzer call.

No new input parameter, prior-snapshot parameter, warm-up parameter, segment parameter, or hidden
global cache is permitted.

## 8. Terminal Context Definition

An eligible terminal context is the single causally latest EXTERNAL lineage that:

- was constructed and validated during the current analyzer call;
- has a final canonical transition to `DealingRangeState.INVALIDATED`;
- has no later ACTIVE lineage at the event moment;
- has a terminal effective moment strictly earlier than the candidate CHOCH effective moment; and
- remains present byte-for-byte in the promoted snapshot prefix.

`SUPERSEDED` is not a free-standing eligible terminal context because its replacement ACTIVE
lineage is emitted atomically. INTERNAL ranges are never terminal context.

## 9. Exact Later-CHOCH Eligibility

When the mutable active pointer is `None`, event handling is locked as follows:

- canonical BOS behavior is unchanged and may construct a new ACTIVE range;
- CHOCH with no eligible same-input terminal context remains `UNKNOWN` with the existing exact
  reason `initial CHOCH lacks prior external range context`;
- CHOCH with an eligible terminal context must be strictly later and must have direction opposite
  to the terminal lineage direction;
- a same-direction CHOCH relative to the eligible terminal context is `INVALID` with the existing
  exact reason `same-direction event must be BOS`;
- malformed, noncanonical, duplicate, reordered, ambiguous, or non-strictly-later evidence remains
  fail-closed before construction.

No equality, grace interval, maximum delay, calendar assumption, hash order, or cross-segment
fallback is introduced.

## 10. New-Lineage Construction Semantics

An eligible later CHOCH is passed unchanged to the existing canonical range-construction path. The
new range receives a new lineage identity from its own direction, selected source swings,
boundaries, protected swing, event ID, and EXTERNAL kind.

The construction transition remains exactly `None -> ACTIVE` with reason
`CONSTRUCTION_ACTIVE`, and its effective moment and first-known provenance exactly match the CHOCH
confirmation moment. The old lineage remains terminal `INVALIDATED`; no transition connects,
reactivates, supersedes, or mutates it.

## 11. No Foreign Protected-Swing Invention

Terminal context proves only that prior external directional context exists in the same analyzer
history. It does not claim that the CHOCH `broken_swing_id` equals the old Dealing Range protected
swing ID. The supplied event's own swing reference, one-tick close break, provenance, and public
EVENT identity remain fully validated by the existing foreign-identity boundary.

The new range's protected swing is selected only by the existing canonical construction algorithm.
No unavailable structural-state object or stronger foreign identity proof may be invented.

## 12. Deterministic State Retention

Implementation may retain an internal terminal-context value only when emitting an EXTERNAL
`INVALIDATED` snapshot. A later successful BOS or eligible CHOCH construction makes the new ACTIVE
range the sole mutable active state. A later invalidation replaces the retained context with the new
causally latest terminal lineage.

The internal value is not public output, is not serialized, is not hashed independently, and cannot
outlive one analyzer call.

## 13. Same-Index Atomic Precedence

Existing same-index behavior is unchanged. If an opposite event occurs on the exact observation
that invalidates the active boundary, the existing close-through reversal path processes the old
terminal transition before the new ACTIVE construction at that same moment.

The retained-terminal correction applies only when `active is None` at a strictly later complete
effective group. It must not create a second same-index path or change event-group ambiguity rules.

## 14. Immutable Prior Evidence

Every snapshot and transition emitted before a later CHOCH or malformed group remains byte-for-byte
immutable. A successful later CHOCH appends only the new lineage evidence. A failing group promotes
nothing from that group or any later group while preserving the strictly prior complete prefix.

No prior snapshot ID, transition ID, state, boundary, midpoint, provenance, source tuple, or lineage
reference may change.

## 15. Status and Fail-Closed Precedence

The existing public precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The correction removes only the false `UNKNOWN` branch for an exactly eligible same-input later
CHOCH. Genuine missing context remains `UNKNOWN`. Contradictory or malformed terminal/event
relationships are `INVALID`; ambiguous complete same-moment groups remain `AMBIGUOUS`.

## 16. Identity and Public API Lock

`DEALING_RANGE_DETECTOR_VERSION`, every public enum value, every frozen dataclass field/default,
`make_dealing_range_id()`, `analyze_dealing_ranges()`, their exact keyword-only signatures, and
`__all__` remain unchanged.

EVENT, TRANSITION, LINEAGE, SNAPSHOT, and INTERNAL_RANGE required/forbidden schemas and payload
fields remain exact. The correction reuses existing identities; it adds no identity kind, field,
reason token, or version bump.

## 17. Ordering and Repeatability

Observation, swing, and structure-event tuple ordering contracts remain unchanged. Output order
remains causal transition order followed by snapshot order, never direction or hash lexical order.
Equivalent UTC timestamps must produce identical identities and outputs. Repeated analysis of the
same complete input must be byte-identical.

## 18. Prefix Invariance

Prefix invariance applies only to a valid prefix ending on a complete effective-group boundary and a
strictly later append. A terminal snapshot in the prefix remains identical when a later eligible
CHOCH constructs a new lineage. Same-effective append, partial group, historical insertion,
reorder, repair, or dependency/config mutation is ineligible for comparison.

## 19. Exact Test-First Logical Matrix

The future correction must preserve the existing logical-case numbering and total. Parameterization
inside existing cases is preferred. Before source modification, public tests must lock all of these
twenty subcases:

1. initial canonical BOS construction remains VALID;
2. lone/initial canonical CHOCH remains UNKNOWN with the exact existing reason;
3. bullish terminal invalidation followed strictly later by bearish CHOCH constructs a new ACTIVE lineage;
4. bearish terminal invalidation followed strictly later by bullish CHOCH mirrors exactly;
5. the old terminal snapshot and transition remain byte-for-byte unchanged;
6. the new lineage differs from the old lineage and never reactivates it;
7. new construction transition and first-known provenance exactly equal the CHOCH moment;
8. same-direction CHOCH after terminal context is INVALID with no current-group promotion;
9. equal/earlier terminal-event chronology is INVALID;
10. active-range same-direction BOS behavior remains unchanged;
11. active-range same-moment close-through CHOCH precedence remains unchanged;
12. multiple terminal cycles use only the causally latest eligible terminal direction;
13. malformed event/swing/observation evidence remains INVALID without exception leakage;
14. distinct opposing same-group events remain AMBIGUOUS and atomic;
15. determinably later invalid evidence preserves the strictly prior complete prefix;
16. valid complete-group strictly-later append satisfies prefix invariance;
17. same-effective append and historical repair are prefix-ineligible;
18. all public signatures, defaults, frozen fields, enums, constants, version, and exports are exact;
19. exhaustive identity schemas and canonical recomputation remain unchanged;
20. no cross-segment, Candidate, structural-seed, private-I/O, feature/label, training, OOS, or integration surface is introduced.

## 20. Validation Commands

After a separately authorized test-first implementation, validation must run with cache disabled:

```powershell
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_dealing_range.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_candidate_evidence_builder.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

The Candidate suite is regression evidence only; it does not expand implementation scope.

## 21. Private Re-Run Boundary

Implementation PASS does not authorize a private Candidate re-run. A later separately authorized
read-only/private run must reconstruct and object-equality validate the accepted V3 dataset and
structural seed, open zero OOS bars, and execute atomically under the already accepted Candidate
private-run proposal.

Only a complete `VALID` or complete `NONE` result covering all `54` segments may be considered for
private publication. `INVALID`, `AMBIGUOUS`, `UNKNOWN`, partial coverage, exception, or identity
drift remains a failed run with no accepted private output.

## 22. Rollback Conditions

Before implementation commit, rollback is deletion or reversal of only the exact in-scope changes.
After an authorized commit, rollback must use a bounded revert; history rewriting is forbidden.
Accepted private dataset/seed evidence and prior immutable detector evidence are never rollback
targets.

## 23. Promotion and Stop Conditions

Promotion requires all locked tests, focused tests, full regression, formatting, exact diff scope,
artifact hashes, checkpoint reconciliation, deterministic repeatability, and independent semantic
audit to PASS.

Stop immediately on public API or identity drift, new reason/version, cross-segment state, old
lineage mutation, non-strict chronology, invented protected-swing proof, private-data mutation,
unexpected I/O, OOS contact, nondeterminism, exception leakage, test failure, scope expansion,
feature/label execution, training, strategy/risk/execution authority, or integration wiring.

## 24. Final Bounded Decision

The evidence supports one narrow future correction: retain the causally latest same-input terminal
INVALIDATED external-range context solely to validate a strictly later opposite CHOCH and construct
a new independent ACTIVE lineage. It does not support cross-segment warm-up, dataset repair,
structural-event relabeling, or Candidate-level status downgrading.

Until separate implementation authorization is granted, this proposal changes documentation only,
the exact three future paths remain frozen, private Candidate output remains absent, and all
training, OOS, integration, stage, commit, and push gates remain closed.
