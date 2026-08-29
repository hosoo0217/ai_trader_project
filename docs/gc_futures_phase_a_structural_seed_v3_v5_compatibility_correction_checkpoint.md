# GC Futures Phase-A Structural Seed V3/V5 Compatibility Correction Checkpoint

## 1. Checkpoint record

- Checkpoint ID: `GC-PHASE-A-STRUCTURAL-SEED-V3-V5-COMPATIBILITY-CORRECTION-CHECKPOINT-V1`.
- Decision date: `2026-08-30`.
- Proposal commit: `f4ddb25f0f15bbf19cfd5466ecec39c7a0c175fc`.
- Proposal SHA-256: `15E902AED5B73244F5F9D801716F0CFF91FF24C53DB742795C54C81CA2A11C79`.
- Classification: public test-first implementation checkpoint.
- Implementation status: `PUBLIC_IMPLEMENTATION_PASS_PRIVATE_RERUN_NOT_AUTHORIZED`.

## 2. Exact implementation scope

Exactly these three paths belong to this implementation transaction:

1. `analysis/gc_structural_seed_evidence.py`;
2. `tests/test_gc_structural_seed_evidence.py`; and
3. `docs/gc_futures_phase_a_structural_seed_v3_v5_compatibility_correction_checkpoint.md`.

No private artifact, accepted evidence, dataset, calendar, candidate, feature,
label, model, configuration, runtime, integration, strategy, risk, or execution
path changed.

## 3. Implemented contract

The structural-seed consumer now accepts exactly two manifest-selected segment
identity versions:

- exact `GC-DATASET-BUILDER-V3-SPLIT-SESSION` uses a local deterministic
  historical V3 segment-ID recomputation; and
- exact current `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION` retains the existing
  `make_gc_dataset_id(identity_kind="SEGMENT", ...)` path.

Every other version fails closed. One manifest version controls every segment;
there is no hash probing, fallback, mixed-version rescue, aliasing, or
normalization. The helper remains private and is not exported as a construction
API.

All pre-existing manifest, provenance, chronology, bar, partition, row, volume,
timezone, immutable-object, and exception-containment checks remain active.

## 4. Test-first evidence

Before the source correction, the new focused matrix produced the expected
result:

```text
2 failed, 5 passed, 69 deselected
```

The two failing tests both returned exact `INVALID_STRUCTURAL_EVIDENCE` for
otherwise valid synthetic V3 inputs. This reproduced the diagnosed compatibility
barrier without opening private evidence.

After the minimal source correction:

```text
7 passed, 69 deselected
```

The matrix proves exact V3 acceptance, deterministic seed revalidation,
multi-segment verification without mutation, strict V3/V5 branch selection,
mixed-ID rejection, and unsupported-version rejection.

## 5. Public regression evidence

Focused structural, Candidate Evidence, and continuity suites:

```text
188 passed in 2.03s
```

Complete public suite using the task-owned workspace pytest base temp:

```text
2666 passed in 39.80s
```

`py_compile` passed for the changed source and focused test module.

The first two full-suite attempts produced only environment setup errors:

- the host default pytest temp root was inaccessible; and
- the first bounded base-temp attempt lacked its parent directory.

In both attempts, `2493` non-temp-dependent tests passed and `173` tests failed
only during `tmp_path` setup. Creating the bounded task-owned parent and rerunning
the same complete suite resolved all `173` setup errors. The task-owned temp
root and its empty parent were then removed. These were environment failures,
not source or assertion failures.

## 6. Exact post-implementation hashes

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_structural_seed_evidence.py` | `D0BBB35F6D6A32CD012996867E56EDCDDC031B75790A19A11684E66290BFE68D` |
| `tests/test_gc_structural_seed_evidence.py` | `49C0C9E86D04C072F4B3EBF420FC9B23BF58B3BDCD958E8F80F0DD74058ADD94` |
| proposal | `15E902AED5B73244F5F9D801716F0CFF91FF24C53DB742795C54C81CA2A11C79` |

The checkpoint hash and resulting local commit are recorded only after exact
staging and cached-diff audit.

## 7. Independent audit gates

Before local commit, audit must prove:

- exactly the three reserved paths are staged;
- `git diff --cached --check` passes;
- no unrelated untracked file is staged;
- no task-owned pytest temp residue remains;
- no private final output root was created;
- repository source and tests contain no private path, accepted artifact hash,
  or private payload shortcut;
- no package export or runtime wiring changed; and
- no training, OOS, feature/label build, integration, prediction, order, or
  trading authority was added.

Any failure is a STOP condition.

## 8. Remaining authority boundary

This checkpoint authorizes no private rerun. The implementation only removes the
specific structural validator's V3/V5 compatibility mismatch. It does not
predict the next continuity or resolver status and does not rescue any future
failure.

GitHub push is a separate privacy/export gate requiring the exact local commit
identifier. Even after push, a private transaction requires separate exact
authority binding unchanged accepted inputs, absent final root, two fresh
workers, deterministic byte equality, atomic publication, independent audit,
cleanup, and mandatory STOP.

Training, final-OOS access, feature/label build, integration, prediction,
execution, and trading remain forbidden.
