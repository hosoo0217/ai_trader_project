# GC Futures Phase-A Cross-Segment Private Diagnostic Dual-Contract Correction Checkpoint

## 1. Checkpoint record

- Checkpoint ID: `GC-PHASE-A-CROSS-SEGMENT-PRIVATE-DIAGNOSTIC-DUAL-CONTRACT-CORRECTION-CHECKPOINT-V1`.
- Verification date: `2026-08-29`.
- Parent commit: `53bed99a909e1bad6983b8c8640691124fba6efb`.
- Governing proposal commit: `53bed99a909e1bad6983b8c8640691124fba6efb`.
- Governing proposal SHA-256:
  `8475FA14319A59517296596861BED61151B125C3C411CE6F871FD92FD85B3305`.
- Classification: public, offline, reference-only implementation checkpoint.
- Decision: `IMPLEMENTED_PUBLIC_ONLY_READY_FOR_LOCAL_COMMIT`.

This checkpoint records an atomic correction of two consumer-side diagnostic
contracts. It is not private-run, dataset, corpus, training, final-OOS,
integration, prediction, execution, or trading authority.

## 2. Exact implementation scope

The completed implementation is limited to exactly five paths:

1. `analysis/gc_cross_segment_continuity.py`;
2. `tests/test_gc_cross_segment_continuity.py`;
3. `analysis/gc_cross_segment_candidate_resolver.py`;
4. `tests/test_gc_cross_segment_candidate_resolver.py`; and
5. `docs/gc_futures_phase_a_cross_segment_private_diagnostic_dual_contract_correction_checkpoint.md`.

No dataset builder, Inducement producer, package export, runtime,
configuration, integration, private artifact, model, strategy, risk, or
execution path changed.

## 3. Correction A: exact archived V3 segment verification

The continuity consumer now selects one exact segment-identity verification
branch from the dataset manifest version:

- `GC-DATASET-BUILDER-V3-SPLIT-SESSION` uses a local, private, deterministic
  reproduction of the historical V3 `SEGMENT` payload; and
- `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION` uses the unchanged public current
  `make_gc_dataset_id` path.

Every other manifest version fails closed. The consumer never retries another
version after mismatch and never chooses a branch by hash success. Mixed V3/V5
graphs fail closed.

The local V3 verifier binds the exact historical version, identity kind,
canonical config payload, contract, partition, trade-date bounds, ordered
source IDs, canonical bar digest, and preceding-missing-bar count. It uses the
same sorted compact ASCII JSON and lowercase SHA-256 identity scheme. The
helper is not exported and cannot construct or rewrite an accepted dataset.

The current V5 identity path, public builder API, builder version, archived
segment IDs, outer dataset ID, manifest ID equality, segment order, timezone
binding, OOS bar prohibition, and development-only partition gate remain
unchanged.

## 4. Correction B: exact pending reason alignment

The resolver now requires the exact public Inducement producer contract:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

The former synthetic token-only `reasons` tuple is rejected. Case shifts,
extra values, missing values, whitespace variants, wrong blockers, and nested
reason-token drift fail closed. No alias, dual acceptance, prose
normalization, substring matching, or blocker-to-reason inference was added.

`smc/inducement.py` is byte-identical to the proposal binding. The
three-closed-bar horizon, adjacent receiving-segment boundary, status
precedence, lineage, identity, chronology, and canonical ordering checks are
unchanged.

## 5. Test-first evidence

The exact two test files were changed before source implementation. The first
focused run produced the expected RED state:

- `98 passed`;
- `28 failed`;
- exact V3 acceptance/version-rejection cases failed because no legacy branch
  existed;
- authentic human-reason fixtures failed because the resolver required the
  token in `reasons`; and
- the token-only negative case unexpectedly passed.

After the bounded two-source correction, the same focused suite produced:

- `126 passed in 1.75s`.

The RED failures were resolved without changing the test expectations back to
the old contracts.

## 6. Acceptance matrix additions

The continuity suite now proves:

- exact two-segment V3 acceptance and input immutability;
- one-segment identity drift rejection;
- blank, V2, V4, and noncanonical version rejection;
- V3 manifest with V5 IDs rejection;
- V5 manifest with V3 IDs rejection;
- mixed V3/V5 graph rejection;
- unchanged current V5 acceptance; and
- OOS segment rejection under the legacy branch.

The resolver suite now uses the exact producer human reason in canonical
fixtures and proves rejection of token-only, lowercase-token, case-shifted
prose, extra-reason, and whitespace-drifted blocker variants.

## 7. Public verification results

- In-memory syntax compile: `4/4 PASS`.
- Continuity plus resolver focused suites: `126 passed in 1.75s`.
- Public Inducement producer plus continuity plus resolver suites:
  `344 passed in 2.41s`.
- Full cache-disabled public suite: `2659 passed in 48.43s`.
- Diff whitespace audit: PASS.
- No source or test attempted private-data access.
- No private transaction or final-root publication occurred.
- No training, final-OOS access, feature/label build, integration, or push
  occurred.

## 8. Exact post-implementation hashes

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_cross_segment_continuity.py` | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `tests/test_gc_cross_segment_continuity.py` | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |

Unchanged dependency bindings:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |

The checkpoint file's own hash is recorded by the exact commit audit after its
final bytes are staged.

## 9. Public API and authority audit

- No public function signature changed.
- No dataclass or enum changed.
- No `__all__` export changed.
- No current builder identity version or API changed.
- No Inducement producer behavior changed.
- No filesystem, network, clock, random, environment, or import-time I/O was
  added.
- No candidate, feature, label, model, score, backtest, order, or execution
  authority was added.
- Phase A remains `CLOSED_NEGATIVE` and Phase A V1 remains
  `RETIRED_NO_RESCUE`.

## 10. Private execution boundary

This checkpoint does not authorize a private rerun. Any later private
diagnostic requires a separate exact authorization binding the committed
implementation, unchanged accepted private input root, absent final root,
two fresh independent reconstructions, atomic publication, deterministic
comparison, independent audit, and cleanup.

The later transaction must still STOP before training, final-OOS access,
feature/label construction, integration, promotion, or trading.

## 11. Commit and rollback boundary

The only admissible local commit contains the five exact paths in Section 2
and uses subject:

`fix(data): reconcile GC cross-segment diagnostic contracts`

Before commit, any exact-scope, hash, test, or cached-diff failure requires
rollback of all task-owned changes. After commit, rollback requires a new
reviewed commit; reset, history rewriting, evidence replacement, and private
artifact mutation remain forbidden.

## 12. Final decision and mandatory STOP

Decision: `IMPLEMENTED_PUBLIC_ONLY_READY_FOR_LOCAL_COMMIT`.

After exact five-path staging, cached audit, local commit, and post-commit
audit, STOP. No push or private diagnostic is authorized by this checkpoint.
