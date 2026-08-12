# GC Futures Phase A Candidate V4 NONE Diagnosis

## 1. Record status

- Record ID: `GC-PHASE-A-CANDIDATE-V4-NONE-DIAGNOSIS-V1`.
- Classification: documentation-only, read-only outcome diagnosis.
- Decision: `VALID_NEGATIVE_ENGINEERING_EVIDENCE`.
- Training readiness: `NOT_READY`.

This record explains why the corrected Candidate Evidence V4 result contains no
candidates. It does not authorize a criterion change, another private build,
feature or label generation, model fitting, OOS access, integration, or trading.

## 2. Repository and evidence binding

The diagnosis was performed with tracked source at commit
`756dcfd0136c467bb65176fcf55d63df2a13881d`. The accepted immutable inputs are:

- dataset ID
  `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- corrected structural seed ID
  `d0940d67677a15124b44fdb4d91f00614cf0ebed27b3d1168e593ee9758f90aa`;
- corrected structural artifact-set identity
  `1be011a6179eda0629b97f0aa371379e09eba78d5654d23b934f121344d5d618`;
- corrected candidate artifact-set identity
  `579ad45043b50dedb58a518ea2bbc9705d99481db89729652879ed3b08400317`.

The accepted structural artifact SHA-256 values are:

| Artifact | SHA-256 |
|---|---|
| `README_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `DE0BAFF1869F8CF0E3F81005AB44619951E1BBEEF4267E8B8573B33EE97FA0D9` |
| `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `3E279EA33CD6EE7AFFD8321D4FE7D01BF465B6944D1E9196942BC4121A67DE41` |
| `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `3A0C4AB8ACED463E7226098D3CE95577D861773E854014268A8F18E61164432D` |
| `structural_seed_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `F632F081918A5A204C84E305F34B8C28574B47F5F5DC355394CD592ACD1491B7` |
| `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `FF066B6645763692869CEEF2600039CF7E9437E8BB03EDE67C689E2A477F20B6` |

The accepted candidate artifact SHA-256 values are:

| Artifact | SHA-256 |
|---|---|
| `README_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `695A1D38F58D22672C2FA3CCA511E6A27C165C271333986C5C81B0F732D4500F` |
| `candidate_evidence_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `046C0A4C995C395CF131AD60C35492B889353CBAB5CE817F3DE48645F13A56AA` |
| `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `691234C14491C9650DCCC2B730D6E7C5041CAB42D0A6BC34CC71F4725FB03694` |
| `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `E2963B5D484FC44E0DEBE442D3B5EB5B5A25E16E73F8EE6F2D49526BEA3AE0B4` |
| `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `4224F936281483DEBBD80E6F9925FEFE69451B88B45775102834F885E5115E45` |

The accepted dataset contains `54` development segments, `7103` development
bars, and zero opened OOS bars. No input bytes were changed by this diagnosis.

## 3. Candidate V4 result

The exact aggregate result is deterministic `NONE`, with:

- `54` complete segment results;
- `0` candidates;
- reason `NO_QUALIFYING_CANDIDATE_EVIDENCE`;
- no blocking reasons;
- no manifest, because a zero-candidate bundle is not promoted.

An independent reconstruction was object-equal to the accepted build. The
result is therefore not an exception, partial run, `UNKNOWN`, `AMBIGUOUS`, or
`INVALID` failure.

## 4. Detector coverage

All six detector stages completed on all `54` segments. Their segment-level
status distribution is:

| Detector | `VALID` segments | `NONE` segments |
|---|---:|---:|
| Equal Liquidity | 26 | 28 |
| Dealing Range | 31 | 23 |
| Liquidity Map | 31 | 23 |
| Fair Value Gap | 36 | 18 |
| Inducement | 0 | 54 |
| Kill Zone | 42 | 12 |

The terminal bottleneck is Inducement. Candidate assembly was correctly not
entered because it requires emitted immutable Inducement evidence.

## 5. Exact Inducement funnel

The read-only diagnostic reconstructed the accepted dataset and V4 structural
seed through the public parser and builders, then repeated the exact detector
chain without writing an artifact. It found:

| Gate | Count passing | Count rejected at gate |
|---|---:|---:|
| Equal-liquidity `SWEPT` pool revisions | 66 | - |
| Latest directional external range is present and `ACTIVE` | 20 | 46 |
| Pre-group map reconciles the internal pool and external target | 10 | 10 |
| Strictly later same-direction event in the next three closed bars | 2 | 8 |
| Event has the required causally linked displacement FVG | 1 | 1 |
| External range remains active through confirmation | 0 | 1 |

The `46` range rejections comprise `37` terminal/non-active latest ranges and
`9` cases with no prior external range. The ten map rejections have no exact
internal-pool classification at the sweep moment.

## 6. Final ten sweep outcomes

The ten pool sweeps that passed both range and map gates ended as follows:

- `8`: no same-direction confirmed structure event in the next three closed
  bars;
- `1`: a structure event exists, but no exact causally linked displacement FVG
  exists at that confirmation moment;
- `1`: the event and linked FVG exist, but the active external range terminates
  before confirmation;
- `0`: complete confirmed Inducement sequences.

These are direct consequences of the locked causal contract. Relabelling any of
them as an Inducement would change the method rather than fix an implementation
defect.

## 7. Chronology and horizon sufficiency

The ten accepted sweep moments occur in segment ordinals `0`, `2`, `4`, `5`,
`8`, `17`, `21`, and `23`. Their segments contain either `229` or `276` bars,
and each sweep has between `44` and `204` strictly later bars in its segment.

Therefore the zero-candidate result is not caused by a truncated next-three-bar
horizon for these ten sweeps. No pending group was incorrectly converted to
`NONE`.

## 8. Segment completeness context

The dataset segment-length distribution is:

| Bars per segment | Segment count |
|---:|---:|
| 276 | 24 |
| 229 | 1 |
| 56 | 1 |
| 38 | 1 |
| 27 | 2 |
| 13 | 2 |
| 12 | 1 |
| 10 | 2 |
| 6 | 1 |
| 5 | 1 |
| 4 | 1 |
| 3 | 5 |
| 2 | 2 |
| 1 | 10 |

The `29` short fragments reduce the pilot's opportunity count and prevent this
small engineering sample from supporting a training-readiness claim. They do
not directly explain the ten fully evaluated sweep failures, which occur only
in the `229`/`276`-bar segments.

## 9. Cross-segment observation

There are `23` active pool lineages at segment ends. A non-promoting geometric
screen found `5` instances where the first three bars of the next same-contract
segment would cross and reclaim an adjacent active pool boundary.

This screen does not establish a canonical Inducement. It does not validate the
required external range, map classification, next-three-bar structure event,
linked FVG, confirmation retention, or identity chain across the boundary.
Current contracts explicitly reset detector state at every segment and prohibit
cross-segment carry. The five observations are only a research question.

## 10. No source defect finding

The diagnosis found no source defect in the corrected V4 path:

- all accepted detector calls completed without exception leakage;
- all `54` segment results were promoted atomically;
- all rejection reasons match the locked public semantics;
- no failing or uncertain group emitted candidate evidence;
- repeated reconstruction is deterministic;
- no OOS, outcome, label, PnL, or future-segment evidence influenced a gate.

Changing the next-three-bar window, accepting an unlinked FVG, retaining a
terminal range, inventing an internal classification, or carrying state across
a segment would be a material methodology change and is forbidden here.

## 11. Data-quality decision

For the intended use of validating the current deterministic candidate builder,
the V4 evidence is adequate and trustworthy as negative engineering evidence.
For the intended use of fitting or selecting an AI model, it is inadequate:

- candidate rows: `0`;
- eligible labels: `0`;
- positive/negative class distribution: undefined;
- temporal coverage: a small engineering window;
- independent OOS coverage: `0` bars and intentionally unopened.

`NONE` must not be described as strategy failure or absence of market edge. It
only states that this bounded sample contains no sequence satisfying every
locked Candidate Evidence criterion.

## 12. Training and feature/label boundary

Training remains stopped. The feature/label builder must not be called because
there is no accepted nonempty candidate bundle. Synthetic balancing, manual
candidate insertion, weak labels, local-LLM labels, chart interpretation, or
criterion relaxation is prohibited.

All currently inspected Phase A data is engineering development evidence. It
cannot later be relabelled as an independent untouched OOS sample. A future OOS
period must be designated prospectively and remain inaccessible until a
separate promotion gate is satisfied.

## 13. Next recommended bounded task

The next single task is a documentation-only Development Candidate Coverage
Expansion proposal. It must define, before any new build:

1. the exact immutable development acquisition set and authoritative calendar;
2. an exact prospective OOS boundary outside all previously inspected evidence;
3. unchanged detector configurations and causal criteria;
4. unchanged no-look-ahead, atomicity, identity, and failure precedence;
5. whether state remains segment-local or whether a separately justified
   continuity model is researched without changing canonical output;
6. minimum evidence-sufficiency gates before feature/label construction;
7. exact private output scope, independent audit, rollback, and STOP rules.

The proposal may study more development data. It may not guarantee candidates,
optimize criteria against outcomes, or authorize training.

## 14. Continuity research boundary

Any future continuity study must be shadow-only and reference the same immutable
bars. Before implementation it must specify canonical index rebasing, official
session/maintenance gaps, contract-roll boundaries, state expiry, identity
versioning, prefix invariance, and comparison against the segment-local
baseline. It must never overwrite or reinterpret V4.

A continuity study that cannot preserve no-look-ahead and deterministic replay
must stop. A geometric cross-boundary sweep alone is not enough to justify the
change.

## 15. Promotion requirements

Candidate evidence may advance toward feature/label construction only after a
separately accepted development build produces a nonempty deterministic bundle
and an independent audit confirms exact source lineage, complete histories,
closed-bar causality, stable identities, and zero OOS contact.

Model training additionally requires a separate feature/label acceptance gate,
leakage audit, fixed evaluation protocol, prospective OOS boundary, and explicit
training authorization. None of those gates is open now.

## 16. Exact scope and freeze

This task creates only:

`docs/gc_futures_phase_a_candidate_v4_none_diagnosis.md`

It changes no Python, tests, fixtures, private artifacts, calendar, dataset,
configuration, integration, package export, model, or training output. The
three pre-existing unrelated untracked documents remain untouched. Global code
freeze remains active everywhere else.

## 17. Rollback and STOP conditions

Before commit, rollback is deletion of only this new documentation file. After
commit, rollback requires a bounded revert; history rewriting is forbidden.

Stop on evidence-hash drift, inability to reconstruct the accepted V4 result,
nonzero OOS contact, outcome or PnL inspection, criterion weakening, synthetic
evidence, cross-segment promotion, source/test/private-artifact mutation,
training, integration, or remote publication without separate authorization.

## 18. Conclusion

Candidate V4 `NONE` is a valid deterministic negative result, not a pipeline
failure. The current sample is sufficient to validate fail-closed orchestration
but insufficient for AI training. The correct direction is to expand and
pre-register development evidence while preserving all causal criteria and a
future untouched OOS period.
