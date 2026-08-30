# GC Phase-A Cross-Segment Candidate Resolver Event-Identity Correction Checkpoint

## 1. Checkpoint record

- Checkpoint ID: `GC-PHASE-A-CROSS-SEGMENT-RESOLVER-EVENT-IDENTITY-CORRECTION-CHECKPOINT-V1`.
- Implementation date: `2026-08-30`.
- Pushed proposal commit: `b031b6dd3c7290e0febc7fbf33c86361376cbeb6`.
- Proposal SHA-256: `0A80F10D29465E4C62F8D522AC8644A057996FEAF797D87F41553FC4AE3D5C16`.
- Implementation baseline: `b031b6dd3c7290e0febc7fbf33c86361376cbeb6`.
- Classification: public, test-first, fail-closed implementation checkpoint.
- Decision: `IMPLEMENTED_LOCALLY_NOT_AUTHORIZED_FOR_PRIVATE_RERUN_OR_PUSH`.

## 2. Exact implementation scope

The implementation changed exactly the three paths reserved by the pushed
proposal:

1. `analysis/gc_cross_segment_candidate_resolver.py`;
2. `tests/test_gc_cross_segment_candidate_resolver.py`;
3. `docs/gc_futures_phase_a_cross_segment_candidate_resolver_event_identity_correction_checkpoint.md`.

No public dataclass or function signature changed. No detector, dataset,
calendar, structural seed, candidate/frontier builder, feature/label builder,
training, OOS, integration, strategy, risk, order, or execution path changed.

## 3. RED evidence

Synthetic public-only tests added canonical multi-tick event identities for
both directions. Their event IDs bind an explicit broken-swing boundary three
ticks beyond the confirmation close rather than the resolver's former
one-tick assumption. A separate adversarial case changes the continuity event
object digest while retaining the event object.

Before the source correction:

```text
3 failed, 67 deselected
```

The failures proved:

- canonical bullish multi-tick identity returned `INVALID`;
- canonical bearish multi-tick identity returned `INVALID`; and
- a changed continuity event-object digest incorrectly returned `VALID`.

The bearish fixture initially exposed a synthetic sweep-geometry setup error.
The fixture was corrected to use direction-valid sweep geometry, and the clean
three-failure RED run above was repeated before any source edit.

## 4. Minimal correction

The resolver no longer reconstructs a structure-event ID from an unavailable
broken-swing price by assuming `confirmation close +/- 1 tick`.

It now retains exact public validation of:

- event type and direction enums;
- broken-swing and event hash shape;
- ordered provenance indices and timestamps;
- confirmation as the final provenance moment;
- presence of every provenance moment in closed receiving observations;
- event/reference object ID equality; and
- canonical event-object digest equality with the continuity reference.

All FVG identity, event binding, transition, snapshot, lifecycle, history,
group, continuity, pending-horizon, precedence, and resolver-result checks
remain unchanged.

## 5. GREEN and regression evidence

Targeted new cases:

```text
3 passed, 67 deselected
```

Focused resolver plus continuity suite:

```text
131 passed in 1.96s
```

Full public test suite, explicitly bounded to `tests/`:

```text
2674 passed in 53.00s
```

An initial repository-root `pytest -q` command was not used as acceptance
evidence. Pytest attempted to discover permission-locked private directories
and stopped with three `PermissionError` collection errors before reading any
private payload or running tests. The corrected public-only `pytest tests -q`
command then passed completely. No private file bytes, final-OOS payload, or
private diagnostic result were read by the implementation or test run.

## 6. Exact post-implementation hashes

| Path | SHA-256 |
|---|---|
| `analysis/gc_cross_segment_candidate_resolver.py` | `DA5193AFEE2B501D28FEE2303EBCF7C345A1D853063472D5C336B4F4506BF72F` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `D34B4D480AA34FEFB4AC65F4D1272706C40555F3EC967804A9A860AF801720E9` |
| governing proposal | `0A80F10D29465E4C62F8D522AC8644A057996FEAF797D87F41553FC4AE3D5C16` |

The checkpoint's own hash and the resulting local commit are recorded by the
post-commit audit because a file cannot contain its own final digest.

## 7. Private-rerun and promotion boundary

This correction does not revive the consumed transaction. It does not permit
a private run, retry, dataset/corpus build, feature/label build, final-OOS
access, training, integration, prediction, promotion, strategy, risk, order,
execution, or trading action.

A future GitHub push is a separate informed export decision. Only after an
exact pushed implementation exists may a new documentation-only private-rerun
proposal bind that implementation and its hashes. That later proposal and an
additional exact authorization are both required before any private rerun.
