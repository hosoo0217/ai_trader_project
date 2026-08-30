# GC Phase-A Control-Frontier Continuation Contract Checkpoint

## Decision

- Checkpoint ID: `GC-PHASE-A-CONTROL-FRONTIER-CONTINUATION-CHECKPOINT-V1`.
- Decision date: `2026-08-30`.
- Governing proposal commit: `4d4c6c8d1959d2eb39673146d3b1d927da4c23da`.
- Governing proposal SHA-256: `D627AB858BC047F4529D69D31B5403FEFBFB9164178F17A0B9E1F671C18C5137`.
- Decision: `IMPLEMENTED_AND_PUBLICLY_VERIFIED_LOCAL_COMMIT_PENDING`.

The additive public contract now represents exactly one immutable canonical-
control frontier pair without promoting or changing the canonical candidate
control. The continuity analyzer accepts this evidence only through an
optional, recomputed, fail-closed input and retains `UNKNOWN /
CANONICAL_CONTROL_UNKNOWN` when the canonical control is unknown.

## Exact implementation scope

Exactly these five proposal-reserved paths comprise this implementation:

1. `analysis/gc_candidate_evidence_builder.py`;
2. `analysis/gc_cross_segment_continuity.py`;
3. `tests/test_gc_candidate_evidence_builder.py`;
4. `tests/test_gc_cross_segment_continuity.py`; and
5. `docs/gc_futures_phase_a_control_frontier_continuation_contract_checkpoint.md`.

Three pre-existing unrelated untracked proposal drafts were not opened,
changed, staged, or included.

## Implemented public contract

Candidate evidence adds:

- `GC_CANDIDATE_FRONTIER_EVIDENCE_VERSION`;
- `GCCandidateFrontierIdentityKind.FRONTIER`;
- frozen `GCCandidateFrontierSegmentEvidence`;
- frozen `GCCandidateFrontierEvidence`;
- frozen `GCCandidateFrontierEvidenceResult`;
- deterministic `make_gc_candidate_frontier_evidence_id()`; and
- `analyze_gc_candidate_frontier_evidence()`.

The analyzer derives the frontier from the exact canonical-control prefix,
rebuilds and compares that control, verifies dataset/seed/calendar bindings,
uses one shared four-detector base helper, and obtains source pending evidence
only from `analyze_inducement_pending_horizons()`. Exact pending reason,
blocker, horizon-count, and missing-bar arithmetic are fail-closed.

Continuity adds only:

```python
frontier_evidence: GCCandidateFrontierEvidenceResult | None = None
```

`None` preserves the legacy result path. A non-null value must recompute
object-for-object, bind the exact control/dataset/seed/frontier ordinal, and
may append at most one frontier boundary after all legacy boundaries. The
existing boundary decision, dependency-reference, receiving-group, ordering,
and manifest construction remain authoritative.

## Test-first evidence

The two focused suites were first changed before source implementation and
failed at collection with the expected missing public frontier symbols. After
implementation:

```text
python -m py_compile <two source files> <two focused test files>
PASS

python -m pytest -p no:cacheprovider \
  tests/test_gc_candidate_evidence_builder.py \
  tests/test_gc_cross_segment_continuity.py \
  tests/test_gc_cross_segment_candidate_resolver.py \
  tests/test_inducement.py -q
402 passed in 2.36s

python -m pytest -p no:cacheprovider tests -q
2671 passed in 41.23s
```

The public tests prove deterministic identity, frozen/exact public schemas,
derived frontier ordinals, one repeatable adjacent synthetic frontier pair,
legacy explicit-`None` object equality, additive boundary ordering, retained
unknown status, and unchanged resolver/Inducement behavior.

A bare repository-root pytest invocation was also attempted. Pytest tried to
collect three ACL-protected `private_data` directories and Windows rejected
the directory scans with `WinError 5` before any private payload was read or
test was run. The authoritative full public-suite command therefore targets
`tests/` explicitly as recorded above. No private analyzer, harness, output,
or transaction was executed or created.

## Final file hashes before staging

| Path | Bytes | SHA-256 |
|---|---:|---|
| `analysis/gc_candidate_evidence_builder.py` | 71671 | `955D5B88953987D969530DFF16C39D8AF769EA7FECEE866E9BC684675B05482A` |
| `analysis/gc_cross_segment_continuity.py` | 68607 | `E60DF0D3E16556A81B5CE9AE2F0FE739D3F02E9BC24D4788B76978C67F39571C` |
| `tests/test_gc_candidate_evidence_builder.py` | 50232 | `C60D2F4A0C7220EF0488BB3776C65F933674E74ED96960E576891B17C2BAFDDC` |
| `tests/test_gc_cross_segment_continuity.py` | 68948 | `8E03055B90FD35323F442A091E425D848561F8DAB5CF8390985BE37053D7B3A0` |

Required unchanged regression dependencies remain exact:

| Path | SHA-256 |
|---|---|
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |

## Permanent non-authority boundary

This checkpoint and its source objects are structural diagnostics only. They
do not authorize or perform a private run, dataset/corpus mutation, final-OOS
access, feature/label construction, training, model inference, integration,
strategy, risk, broker, order, execution, or trading action. They do not
promote the canonical control or lift any downstream freeze. Remote push and
any future private transaction require separate exact authorization.
