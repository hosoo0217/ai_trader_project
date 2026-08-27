# GC Futures Phase A UNKNOWN Continuity Manifest Preservation Checkpoint

## 1. Checkpoint identity

- Checkpoint ID:
  `GC-PHASE-A-CROSS-SEGMENT-CONTINUITY-UNKNOWN-MANIFEST-PRESERVATION-2026-08-27`.
- Governing proposal:
  `docs/gc_futures_phase_a_cross_segment_continuity_unknown_manifest_preservation_change_proposal.md`.
- Governing proposal commit:
  `e075a203287351b2f472ffe36adc292e80ca07e8`.
- Governing proposal SHA-256:
  `8FDDE1B108F2D5987DB699E7A94C3BF0816FDA2F0411A95AA1CE905F653D38F6`.
- Implementation version remains `GC-CROSS-SEGMENT-CONTINUITY-V1`.
- Independent implementation audit: `PASS`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact authorized scope

Only these three paths were changed:

- `analysis/gc_cross_segment_continuity.py`;
- `tests/test_gc_cross_segment_continuity.py`;
- `docs/gc_futures_phase_a_cross_segment_continuity_unknown_manifest_preservation_checkpoint.md`.

No private artifact, dataset, calendar, corpus, feature, label, model, training
output, final-OOS payload, package export, configuration, runtime, strategy,
risk, execution, trace, or integration path was read for promotion or changed.

## 3. Corrected terminal rule

After complete input validation, boundary construction, receiving-group
construction, and canonical manifest construction, terminal canonical-control
`UNKNOWN` now returns:

```text
status = UNKNOWN
boundaries = exact validated tuple
receiving_groups = exact validated tuple
manifest = exact manifest constructed by that run
reasons = ("CANONICAL_CONTROL_UNKNOWN",)
blocking_reasons = ("CANONICAL_CONTROL_UNKNOWN",)
```

The non-null manifest is immutable diagnostic provenance only. It does not
promote a candidate, feature, label, corpus row, model input, or trading
decision, and it does not change the `UNKNOWN` status.

## 4. Minimal source correction

The private `_blocked(...)` helper gained one optional keyword-only
`manifest` argument with default `None`. Every existing call therefore retains
its prior null-manifest behavior. Only the final
`CANONICAL_CONTROL_UNKNOWN` branch supplies the already constructed manifest.

No public class, function, parameter, enum, version constant, identity kind,
field, default, return annotation, or export changed.

## 5. Manifest identity invariants

The corrected result preserves the existing exact 13-field
`GCCrossSegmentContinuityManifest` schema. Its `boundary_ids` and
`receiving_group_ids` mirror the returned tuples in order. The existing public
`MANIFEST` builder recomputes `manifest_id` exactly.

`canonical_control_digest` binds the complete object-equal `UNKNOWN`
Candidate Evidence control supplied to that run. Consequently, a comparison
with an otherwise equivalent `VALID` control changes only the control digest
and the derived manifest ID; all other manifest fields remain object-equal.
No private hash helper or new public identity surface was introduced.

## 6. Null-manifest fail-closed preservation

The strengthened tests retain `manifest=None` for missing top-level context
with exact `MISSING_TOP_LEVEL_CONTEXT` reason and blocking token. Terminal
canonical-control `INVALID` and `AMBIGUOUS` also remain null-manifest results.
All earlier fail-closed paths remain unchanged because none supplies the new
internal helper argument.

## 7. Boundary and group immutability

The terminal `UNKNOWN` result returns boundary and receiving-group tuples
object-equal to those produced from the same validated evidence. Boundary
identity payloads, decisions, reason tokens, dependency references, receiving
references, and ordering are unchanged. No failing-group or synthetic
candidate evidence is promoted.

## 8. Test-first RED evidence

The focused target was executed after the test correction and before the
source correction:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider \
  tests/test_gc_cross_segment_continuity.py -k "case_02 or case_37 or case_38"
```

Result: `2 failed, 1 passed, 45 deselected in 1.21s`. Cases 37 and 38 failed
only because terminal `CANONICAL_CONTROL_UNKNOWN` returned `manifest=None`;
Case 2 confirmed the earlier missing-context null-manifest boundary.

## 9. Test audit correction

The first post-source target run exposed an invalid test comparison:
`2 failed, 1 passed, 45 deselected in 0.90s`. The test had compared a manifest
bound to an `UNKNOWN` control with a manifest bound to a `VALID` control even
though `canonical_control_digest` is identity-bearing. The test was corrected
to require the exact digest of the supplied `UNKNOWN` control, exact public
manifest-ID recomputation, object-equality of all non-digest fields, and
repeatability. Production identity semantics were not weakened.

## 10. Targeted GREEN evidence

After the test audit correction, the same target command returned:

```text
3 passed, 45 deselected in 0.71s
```

This proves the intended terminal preservation, earlier null-manifest
boundary, deterministic identity, and repeated-run object equality.

## 11. Exact logical-case reconciliation

The test module still contains exactly 48 sequential logical functions named
`test_case_01` through `test_case_48`. No logical case was added or removed.
Cases 2, 37, and 38 were strengthened in place. Parameterization was not
needed, so focused collection remains exactly 48 executions.

## 12. Focused regression evidence

- Command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_cross_segment_continuity.py`.
- Result: `48 passed in 0.85s`.
- Exact logical cases: `48`.
- Collected focused executions: `48`.

## 13. Full regression evidence

- Command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`.
- Result: `2581 passed in 41.72s`.
- Pre-correction accepted full total: `2581`.
- Regression delta: `0`.

Explicit `tests` collection is the accepted full public suite. It avoids
repository-root traversal of ACL-protected private-data directories that are
outside this bounded task.

## 14. Artifact evidence

- `analysis/gc_cross_segment_continuity.py`
  - SHA-256:
    `FD7688D88930A86CA005DF89A750B94D4A5748EE50F7EC95A288B9B4987AA826`;
  - bytes: `58414`;
  - physical lines: `1132`.
- `tests/test_gc_cross_segment_continuity.py`
  - SHA-256:
    `70C307AAC85FD242950A3D56C66A35AEDA5D62EABCBB2A7A6515AA700B533FC5`;
  - bytes: `51804`;
  - physical lines: `1147`.

The checkpoint hash, byte count, and line count are computed after its final
bytes are fixed and verified during cached and committed artifact audits.

## 15. Scope and formatting audit

- `git diff --check`: `PASS` before checkpoint construction and required again
  before staging and commit.
- Exact logical-case count: `48`.
- Source correction is limited to the internal helper and terminal target
  branch.
- The three pre-existing unrelated untracked proposal documents remain
  outside scope and untouched.
- No broad pathspec is authorized for staging.

## 16. Rollback, promotion, and STOP conditions

Rollback before commit is removal of this checkpoint and reversal of only the
source/test edits in the exact scope. Promotion to local commit requires exact
three-path staging, full cached-content inspection, cached `diff --check`,
staged artifact hash verification, focused/full PASS, and no tracked change
outside scope.

This correction is `PASS` for exact three-path local staging and commit. STOP
remains mandatory before push, private execution, training, final-OOS payload
access, dataset/corpus/feature/label build, package/runtime integration,
strategy, risk, execution, trace, or any scope expansion. Those actions remain
separately gated and are not authorized by this checkpoint.
