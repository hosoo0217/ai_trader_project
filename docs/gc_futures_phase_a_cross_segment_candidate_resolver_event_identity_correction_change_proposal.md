# GC Phase-A Cross-Segment Candidate Resolver Event-Identity Correction Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-RESOLVER-EVENT-IDENTITY-CORRECTION-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Exact diagnosis baseline: `870c1fa6dbd784f2c11f1928884eeaeb866a6875`.
- Governing private-rerun proposal SHA-256: `D6276F36C3470704940D55F5A56BF0B480669B0DCAD6C247E70BB53DEDE06C2B`.
- Classification: documentation-only, test-first, fail-closed correction proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_IMPLEMENTATION`.

This record explains the deterministic `INVALID` result from the consumed
control-frontier resolver transaction. It authorizes no source/test change,
private rerun, dataset/corpus build, feature/label build, final-OOS access,
training, integration, prediction, strategy, risk, order, execution, stage,
commit, or push.

## 2. Consumed transaction outcome

The transaction bound to proposal commit
`870c1fa6dbd784f2c11f1928884eeaeb866a6875` stopped during fresh worker 1
because `resolve_gc_cross_segment_candidates()` returned `INVALID`. Worker 2
did not run, no retry occurred, and no final root was published. The task-owned
worker root, harness, and bytecode cache were removed. The eight accepted input
members remained byte-exact, the Git index remained empty, and
`HEAD == origin/main` remained the proposal commit.

That authorization is consumed and may not be reused.

## 3. Root cause

Canonical structural-seed events bind `DealingRangeStructureEvent.event_id`
to the exact broken swing price:

```python
boundaries=SMCV2TickRange(selected.price_tick, selected.price_tick)
```

The resolver does not receive the broken swing object or price. Nevertheless,
its `_event_id()` helper invents a boundary from the confirmation close:

```python
boundary_tick = close_tick - 1 if bullish else close_tick + 1
```

That formula is valid only when the confirmation close crosses the broken
swing by exactly one tick. A canonical multi-tick close break therefore fails
resolver validation even though the event was accepted by structural-seed and
continuity validation.

The current resolver test fixture masks this defect by replacing the fixture
event ID with an ID explicitly computed from `confirmation_bar.close_tick - 1`.
The test therefore proves the resolver's invented assumption rather than the
canonical structural-event contract.

## 4. Read-only evidence

The diagnosis used no analyzer, resolver, private transaction, write, retry,
or output publication. It read only the already accepted development dataset
and structural-seed JSON and joined canonical receiver bars to canonical seed
events by exact `(confirmation_index, confirmation_timestamp)`.

For the locked ordinal-114 receiving segment:

- receiver bars: `276`;
- canonical receiving structure events: `15`;
- events matching the resolver's `close +/- 1` assumption: `3`;
- events contradicting that assumption: `12`;
- structure events linked to accepted FVG context: `2`;
- linked events contradicting the assumption: `2`;
- observed absolute mismatch distances: `2, 4, 9, 15, 22, 24, 25, 26, 27, 31, 38, 52` ticks.

This evidence is sufficient to explain the observed `INVALID`: the receiving
events relevant to the FVG-backed continuation cannot pass `_event_id()` even
though their canonical identities are valid upstream.

## 5. Correct trust boundary

The resolver must not reconstruct a broken-swing boundary it does not receive.
It must instead validate the exact event object against the already validated
continuity receiving reference:

1. retain all public type, enum, provenance, observation-moment, direction,
   co-termination, and positional-suffix checks;
2. require `event.event_id == event_ref.object_id`;
3. require the resolver's canonical `_sha(event) == event_ref.object_digest`;
4. require the event semantic discriminator and owning segment fields to match;
5. retain the exact FVG ID, transition, snapshot, lifecycle, history, and
   event-binding checks; and
6. delete only the invented event-boundary reconstruction.

The continuity reference is not an untrusted opaque assertion. It is part of
the canonical continuity manifest path and already binds the exact event
object digest, source-moment digest, owner, first-known/effective moment,
semantic discriminator, and object ID. The resolver may verify the object it
receives against that immutable reference without recreating unavailable
upstream swing evidence.

## 6. Reserved exact implementation scope

A future implementation is limited to exactly three tracked paths:

1. `analysis/gc_cross_segment_candidate_resolver.py`;
2. `tests/test_gc_cross_segment_candidate_resolver.py`;
3. `docs/gc_futures_phase_a_cross_segment_candidate_resolver_event_identity_correction_checkpoint.md`.

No public dataclass, function signature, result status, precedence rule,
reason token, identity payload, continuity contract, detector, dataset,
calendar, structural seed, candidate/frontier builder, integration, training,
OOS, strategy, risk, order, or execution path may change.

## 7. Test-first implementation order

The future implementation must be atomic and test-first:

1. add a canonical multi-tick bullish close-break case whose event ID binds an
   explicit broken-swing tick different from `close_tick - 1`;
2. prove the current resolver returns `INVALID` for that otherwise canonical
   continuity/reference graph;
3. add the symmetric bearish case with a boundary different from
   `close_tick + 1`;
4. change event validation to reference-bound object identity as Section 5
   specifies;
5. require both canonical multi-tick cases to follow the same result branch as
   their one-tick equivalents;
6. add tamper cases proving that changed event fields, event ID, object digest,
   owner, provenance, or semantic discriminator remain `INVALID`;
7. retain all existing resolver and continuity tests; and
8. record exact hashes, focused/full test counts, and zero authority expansion
   in the reserved checkpoint.

Tests may use only synthetic public fixtures. No private value, event ID,
segment ID, bar, tick, timestamp, or outcome may enter source or test code.

## 8. Acceptance gates

Implementation is acceptable only if all gates pass:

- RED regression demonstrates the current one-tick assumption defect;
- GREEN regression accepts canonical multi-tick event identity only through
  the matching continuity object reference;
- adversarial object/reference drift remains `INVALID`;
- existing one-tick, UNKNOWN, NONE, AMBIGUOUS, INVALID, and precedence cases
  remain unchanged;
- focused resolver/continuity tests pass;
- the full public suite passes;
- the exact three-path diff contains no private values or unrelated changes;
- accepted private roots and final-OOS remain unopened during implementation;
- Git index scope is exact before any later commit; and
- no private rerun occurs under this proposal.

## 9. Future private-rerun boundary

Even after an exact implementation commit is reviewed and pushed, no private
run is implied. A new documentation-only corrected-rerun proposal must bind the
exact pushed implementation, exact hashes, accepted input root, fresh absent
worker/final roots, two-run byte equality, atomic publication, and mandatory
STOP. It then requires a new exact private-run authorization.

The failed authorization, removed harness, or any prior proposal may not be
reused.

## 10. Non-authority

This proposal grants no trading authority. Local AI, any model, and every
diagnostic remain unable to modify accepted data, build a training corpus,
create features or labels, access final OOS, train, promote, integrate,
predict, backtest a strategy, size risk, submit an order, or execute a trade.
