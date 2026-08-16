# GC Futures Phase A Cross-Segment Continuity Bounded Implementation Checkpoint

## 1. Checkpoint identity

- Checkpoint ID: `GC-PHASE-A-CROSS-SEGMENT-CONTINUITY-CHECKPOINT-2026-08-16`.
- Governing proposal:
  `docs/gc_futures_phase_a_cross_segment_continuity_feasibility_change_proposal.md`.
- Governing proposal commit:
  `ad70be419a5dfc361be06d512e6d8fe8749b2a56`.
- Governing proposal SHA-256:
  `90130C122C1D07C861B24E350BA8D294E79287E0FE02C4D1ADC01EC49CD15F82`.
- Implementation version: `GC-CROSS-SEGMENT-CONTINUITY-V1`.
- Task classification: offline, reference-only continuity feasibility diagnostics.
- Independent semantic audit status: `PASS`.
- Private-data execution: two separately authorized feasibility attempts were
  performed and stopped atomically before publication. The first exposed the
  corrected first-known causality defect; the second exposed the partial-
  boundary classification defect corrected in this revision. A further
  corrected private rerun is `NOT_PERFORMED` and remains separately gated.
- OOS access, candidate/feature/label construction, model work, and training:
  `NOT_PERFORMED` and `NOT_AUTHORIZED`.
- Strategy, risk, execution, trace, runtime, and integration authority:
  `NOT_GRANTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact authorized scope

Exactly these three paths are in scope:

- `analysis/gc_cross_segment_continuity.py`;
- `tests/test_gc_cross_segment_continuity.py`;
- `docs/gc_futures_phase_a_cross_segment_continuity_checkpoint.md`.

No external fixture, private artifact, dataset, calendar, generated candidate,
feature, label, model, training output, package export, configuration, runtime,
trace, strategy, risk, execution, or integration file was created or changed.
The three pre-existing unrelated untracked proposal documents remain outside
scope and untouched.

## 3. Locked dependency evidence

The implementation uses the accepted public dependency surface. The governing
proposal hashes still match exactly:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_structural_seed_evidence.py` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `F2D6754A7456D39C6BCC5EE312024F8C538CFDBD43474BC76957D44B62EBCE0E` |
| `smc/liquidity_map.py` | `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `smc/inducement.py` | `57DA49BE7C99DF9385610749446566323865676817FF8C44D8F8D3868C8C633F` |

The new analyzer imports no filesystem, network, subprocess, training, model,
strategy, risk, execution, or runtime-integration authority.

## 4. Test-first evidence and corrections

The exact 48 numbered public acceptance cases were added before the module.
The initial focused run failed at collection with
`ModuleNotFoundError: analysis.gc_cross_segment_continuity`, establishing the
RED gate before source construction.

The implementation was then brought to GREEN inside the exact scope. During
the independent audit, the synthetic fixture was corrected to use the accepted
`Asia/Tokyo` source timezone, runtime `tzdata` version, canonical GC contract
names, and the exact three-session roll confirmation contract. These are test
contract corrections, not dependency changes.

The first semantic audit reached `47 passed, 1 failed`. Case 45 exposed that a
boundary identity changed when a strictly later complete receiving group
changed the complete canonical-control result. The implementation then bound
each boundary and receiving group to the exact canonical-control prefix
available at its effective moment, while the manifest retained the digest of
the complete object-equal canonical result.

The governing proposal was corrected and independently re-audited in commit
`ad70be419a5dfc361be06d512e6d8fe8749b2a56`. Sections 10, 16, 19, 21, and 24 now
lock the same coherent point-in-time contract without changing public field
names or API. `BOUNDARY` uses the ordered canonical `segment_results` prefix
through its source position; `RECEIVING_GROUP` uses the prefix through its
receiving position; and `MANIFEST` uses the complete object-equal control
digest. The source and Cases 39--41/45 match this accepted contract exactly.

The final independent implementation audit found no source defect, but found
that Cases 38--44 did not yet prove every claim in the locked matrix. The tests
were strengthened in place without changing the exact 48 logical cases:
determinably later `INVALID` atomic failure now proves prior boundary
preservation and no group promotion; final `INVALID`/`AMBIGUOUS`/`UNKNOWN`
states prove byte-exact prior boundary/group preservation; all common,
kind-required, and forbidden identity fields are exercised; nested malformed
dependency/receiving references are contained; and exact function annotations,
defaults, dataclass fields, annotations, defaults, frozen state, enums, version,
and exports are asserted directly. The strengthened suite remained GREEN, so no
production correction was required.

A later separately authorized private feasibility attempt stopped with
`INVALID_BOUNDARY_EVIDENCE` before creating any final root, temporary runner,
or promoted artifact. The exact failure was an ACTIVE same-lineage Dealing
Range extension whose immutable construction transition preceded the
snapshot's later first-known provenance. The continuity adapter had selected
the last transition moment unconditionally, which backdated the carried
reference before the canonical snapshot was knowable.

Case 21 was strengthened test-first without increasing the exact 48 logical
cases. The RED run reproduced the defect through the public analyzer as
`1 failed, 47 passed`. The minimal source correction now defines the carried
Dealing Range reference effective moment as the later of first-known
provenance and the final transition moment. It preserves the exact ordered
transition IDs and full object digest; it does not rewrite, infer, or enrich
the foreign snapshot. The corrected focused and full suites are GREEN. No
corrected private rerun, training, OOS access, or integration was performed.

The separately authorized corrected private attempt then stopped atomically
with `INVALID_BOUNDARY_EVIDENCE`; its final output root remained absent and all
eight accepted private inputs remained byte-immutable. Aggregate metadata
profiling found `70` dataset segments with nonzero
`preceding_missing_bar_count`, all inside the first `113` canonical-control
segment results. The analyzer encountered the first such adjacent pair after
preserving two strictly prior boundaries.

The governing proposal Sections 8--9 explicitly make a partial or missing-bar
boundary ineligible, not globally invalid. Case 12 was therefore strengthened
test-first without changing the exact 48 logical cases. The RED run was
`1 failed, 47 passed`: a canonical partial segment returned
`INVALID_BOUNDARY_EVIDENCE`. The minimal source correction now returns an
`INELIGIBLE` boundary with exact reason `PARTIAL_SEGMENT_BOUNDARY`, empty
dependency references, and no receiving-group promotion. A genuinely malformed
or open bar remains `INVALID`. This does not repair, filter, synthesize, or
promote partial evidence; it records the proposal-locked valid ineligibility
decision and continues causal assessment of later accepted boundaries.

## 5. Input and control-arm validation

The analyzer accepts only the locked immutable dataset config/result, split
session calendar, Kill Zone calendar, structural seed, candidate result, and
candidate config. Supplied counterparts undergo independently determinable
validation before a missing input can return `UNKNOWN`.

Dataset, manifest, segment, bar, partition, instrument, timeframe, tick size,
calendar version, timezone-data version, seed ID, segment order, and zero-OOS
contracts are fail-closed. The canonical candidate builder is called exactly
once with the distinct candidate-calendar stream. The rebuilt result must be
object-equal to the supplied canonical control; no repair, enrichment, or
silent sorting is allowed.

## 6. Boundary eligibility and ineligibility

Only adjacent accepted development segments are assessed. Eligibility requires
same contract, complete closed five-minute sessions, exact local index and UTC
chronology, no preceding missing bars, exact authoritative split-session close
and next-open reconciliation, unchanged lineage/version context, and the next
eligible business trade date.

Contract roll, OOS or purge boundaries, closed or early-close sessions,
non-adjacent segments, and canonically identified partial/missing-bar segments
are deterministically `INELIGIBLE`. A partial boundary carries exact reason
`PARTIAL_SEGMENT_BOUNDARY`, empty dependency references, and no receiving
group. Malformed/open/reordered bars and provenance or version drift remain
fail-closed `INVALID`. No carried state is attached to an ineligible boundary.

## 7. Reference-only dependency closure

Eligible boundaries preserve immutable references only to complete ACTIVE
Equal Liquidity, Dealing Range, and latest Liquidity Map evidence. Every
reference binds its canonical object ID, owning segment, first-known/effective
moments, final state, ordered history IDs, source-moment digest, and full object
digest. Terminal, dangling, incomplete, foreign, forked, or pool/range/map-only
closure is rejected.

The analyzer creates no lifecycle transition at a segment boundary and never
recomputes, mutates, enriches, merges, replaces, or reactivates foreign
detector evidence.

For an ACTIVE Dealing Range extension, the immutable history can contain an
older construction transition while the extension snapshot becomes knowable
strictly later. Its carried effective moment is therefore the later of the
snapshot first-known provenance and final transition moment. This forbids
backdating while preserving the complete upstream lifecycle history.

## 8. Receiving-group causal binding

Receiving Structure Event and FVG facts remain receiving-segment evidence and
are visible only at their canonical effective moment. All source moments must
reconcile to exact receiving bars. Event and FVG source sequences must
co-terminate, and the shorter sequence must be the exact positional suffix of
the longer. The non-null FVG `displacement_id` remains opaque metadata rather
than a claimed foreign proof.

Complete groups promote atomically. A partial or malformed group promotes
nothing from that group or later groups while strictly prior immutable evidence
is preserved.

## 9. Exact public API and immutable types

The module exports exactly:

- `GC_CROSS_SEGMENT_CONTINUITY_VERSION`;
- `GCCrossSegmentContinuityIdentityKind`;
- `GCCrossSegmentContinuityDecision`;
- `GCContinuityDependencyReference`;
- `GCContinuityReceivingReference`;
- `GCCrossSegmentBoundary`;
- `GCContinuityReceivingGroup`;
- `GCCrossSegmentContinuityManifest`;
- `GCCrossSegmentContinuityResult`;
- `make_gc_cross_segment_continuity_id`;
- `analyze_gc_cross_segment_continuity`.

Both public functions use the exact locked keyword-only names and defaults. All
six public dataclasses are frozen with exact fields and immutable tuple
members. Enum values, version, annotations, defaults, and exports are directly
covered by Case 44.

## 10. Deterministic identities and ordering

The identity builder enforces exhaustive `BOUNDARY`, `RECEIVING_GROUP`, and
`MANIFEST` required/forbidden schemas. It validates normalized scope, hashes,
calendar digests, source/receiving segment pairing, trade dates, UTC moments,
decision/reason fields, reference tuples, ordered group history, and nested
values without leaking library exceptions.

Ordering is dataset order first and upstream lifecycle order within the owning
scope. Direction or hash lexical order is not used as a chronology substitute.
Equivalent UTC timestamps and repeat execution produce object-equal results.

## 11. Status, atomicity, and prefix invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Invalid, ambiguous, and unknown terminal conditions cannot promote evidence
from their failing group or later groups. A strictly later complete receiving
group leaves all prior boundary bytes unchanged. Same-effective append,
historical calendar insertion, repair, mutation, or reorder is not eligible for
prefix comparison.

The accepted implementation uses the exact identity-kind-specific contract:
canonical-control source prefix for `BOUNDARY`, receiving prefix for
`RECEIVING_GROUP`, and complete object-equal digest for `MANIFEST`. Complete
canonical rebuild and object equality remain mandatory before any promotion;
the point-in-time prefixes do not weaken canonical validation or permit a
projection reconstructed from foreign IDs.

## 12. Exact 48-case matrix reconciliation

`tests/test_gc_cross_segment_continuity.py` contains exact sequential logical
Cases 1 through 48 and exactly 48 collected executions. Coverage includes input
binding, missing/malformed precedence, canonical rebuild equality, adjacent
segment and calendar eligibility, roll/closed/early-close ineligibility,
canonical partial-boundary ineligibility, malformed/open-bar invalidity,
timezone normalization, dependency closure, terminal-state rejection, immutable
foreign objects, ACTIVE Dealing Range extension first-known causality,
receiving event/FVG reconciliation, suffix mismatch, atomic
cutoff and prior-evidence preservation, full status precedence, exhaustive
common/required/forbidden schemas for all three identity kinds, field
sensitivity, nested exception containment, exact public parameter names,
annotations, kinds and defaults, exact frozen dataclass fields/annotations/
defaults, complete-group prefix invariance, deterministic reporting, and
forbidden authority/import surface.

## 13. Focused and full regression evidence

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_cross_segment_continuity.py`;
- result: `48 passed in 0.68s`;
- exact logical cases: `48`;
- collected focused executions: `48`.

Final full public regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`;
- result: `2346 passed in 13.74s`;
- preceding accepted baseline: `2298`;
- net new executions: `48`.

Repository-root discovery was not used as the acceptance command because it
also traverses ACL-protected private-data directories that are explicitly
outside this task. Explicit `tests` collection covers the complete tracked
public regression suite without reading private evidence. A diagnostic
repository-root invocation confirmed the same private-directory ACL boundary
and stopped during collection; it produced no assertion or product-code
failure. The accepted focused and explicit `tests` commands completed without
opening or changing private evidence.

## 14. Artifact evidence

- `analysis/gc_cross_segment_continuity.py`
  - SHA-256:
    `1F59432FD738699015DDD92DC8AEB437D1B3DADE7EF96B1BB816245F05DB34D7`;
  - bytes: `58251`;
  - physical lines: `1124`.
- `tests/test_gc_cross_segment_continuity.py`
  - SHA-256:
    `9E666DE295F7F538E81CFE772A1B436E625F5D9644E5136C045C049E458205C4`;
  - bytes: `49354`;
  - physical lines: `1094`.

The checkpoint hash is intentionally computed only after its final bytes are
fixed and is verified during cached/committed artifact audit.

## 15. Scope, rollback, promotion, and STOP conditions

`git diff --check`, exact-scope inspection, full cached-content inspection, and
staged artifact hashes are required before local commit. Rollback is deletion
of only the three exact task paths before promotion; no dependency or private
artifact rollback is required.

Local commit promotion is allowed only after focused/full PASS, semantic and
structural audit PASS, exact staged scope, and a clean tracked worktree outside
the three paths. These gates are now satisfied for local staging and commit.
Push still requires separate explicit authorization after the accepted
implementation commit.

STOP remains mandatory before any private run, OOS access, candidate/feature/
label build, model or training work, package export, configuration, strategy,
risk, execution, trace, runtime integration, or push. Any dependency hash drift,
calendar contradiction, unverifiable identity, scope expansion, nondeterminism,
look-ahead, partial-group promotion, or failed regression blocks promotion.

## 16. Final implementation decision

The bounded implementation is `PASS` and is ready for exact three-path local
staging and commit. Focused and full regressions are GREEN; the governing
point-in-time identity contract, source, tests, and checkpoint are consistent.
Two separately authorized private feasibility attempts exposed two in-scope
continuity-adapter defects. Cases 21 and 12 and the source were corrected
test-first. The next corrected private rerun remains unperformed and separately
gated.

After local commit, STOP remains mandatory before push, private execution, OOS
access, candidate/feature/label work, model or training work, package export,
configuration, strategy, risk, execution, trace, runtime integration, or any
scope expansion. Those are separate future decisions and are not authorized by
this checkpoint.
