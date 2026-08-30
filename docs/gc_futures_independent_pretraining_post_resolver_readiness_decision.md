# GC Futures Independent Pretraining Post-Resolver Readiness Decision

## 1. Decision status

- Record type: documentation-only project-readiness decision.
- Decision date: `2026-08-31`.
- Local baseline commit:
  `5e1a9f7a3d0ea0cc6421c2488a57cc334308096a`.
- Verified `origin/main` baseline:
  `d39fe7e8b478a4ab0a51c78248052dc0d38d7fed`.
- Readiness decision:
  `POST_RESOLVER_PRETRAINING_NOT_READY_TERMINAL_UPSTREAM_UNKNOWN_NO_TRAINING_NO_OOS`.
- Accepted independent pretraining corpus: `ABSENT`.
- AI training state: `NOT_STARTED`.
- Final-OOS authority: `NONE`.
- Integration and trading authority: `NONE`.
- Global code freeze: `ACTIVE`.

This record reconciles the completed terminal cross-segment resolver diagnostic
with the separately governed independent pretraining workstream. It does not
reinterpret either closed research phase and does not authorize a corpus
build, model run, or private evidence repair.

## 2. Governing evidence

The decision binds these committed records and public contracts:

| Evidence | SHA-256 |
|---|---|
| Phase-B sweep-reclaim closure decision | `5166E0D14BAA65A2AAFC8E17BE2E1740EC92AFCFCCC4CCED4B60CFF964E36F75` |
| Post-Phase-B pretraining partition-readiness decision | `2B4A2D1A660A65995D8C0A1189152A010EE219F259B4B6606E8550B04D2CD4BF` |
| Independent pretraining corpus freeze-lift decision | `556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303` |
| Post-calendar corpus readiness decision | `AD736DDC448AB79B53FC6A71DCC12691FCE3133E18F7F9B4AD867703CF2BD956` |
| GCG26 source-binding/corrected-rebuild proposal | `7E78B185D15323E724A0503E6ADDEC3B05044830EDF65A13A6808653C7EBA641` |
| Contract-domain reconciliation checkpoint | `82A60345CA57C7C0FC762C6BFD6D07836EC3BE49C82233DEC2D2F092BCFB1EF6` |
| Terminal cross-segment resolver outcome decision | `107DF12717C0AFC60BA89D1721C02A77E1BD2631BB3C19FA5FFBEEF7330EB67D` |
| Public pretraining corpus implementation | `F1D2454BD62C339CC6ED2BAAC1BE3BFFA3ED1E8D8A150D77BEE29F0A52F48400` |
| Public pretraining corpus tests | `122A4BEC229C708942A9374688390B43616ACCC4DA534C2510322AD4AA5BF046` |

Hash, baseline, evidence-purpose, or output-state drift invalidates this
decision rather than silently changing its conclusion.

## 3. Closed research phases

Phase A remains `CLOSED_NEGATIVE`. Its V1 Candidate Evidence hypothesis and
cross-segment rescue path are retired. The terminal resolver output is
deterministic archived evidence with:

- resolver status `UNKNOWN`;
- reason and blocker `CROSS_SEGMENT_CONFIRMATION_UNRESOLVED`;
- resolution count `0`;
- candidate promoted `false`;
- Phase A reopened `false`; and
- training, feature/label, integration, OOS, and trading authority all false.

Phase B remains `CLOSED_INSUFFICIENT_EVIDENCE`. Its diagnostic candidates and
UNKNOWN results cannot be promoted, relabelled, or merged into a training
corpus. Neither closed phase may be rescued through changed thresholds,
longer horizons, manual chart interpretation, later outcomes, or model output.

## 4. Public implementation readiness

The independent corpus implementation is retained as a valid public,
fail-closed engineering contract. The contract-domain reconciliation
checkpoint confirms exact unsuffixed/exchange-qualified GC comparison semantics
without changing public identities, source registry values, dataset IDs,
feature rows, labels, partitions, sealed-OOS behavior, or authority.

Implementation readiness is not data readiness. A working builder cannot
manufacture missing canonical candidate evidence, feature rows, labels, or
partition membership. It must return `UNKNOWN` or `INVALID` when its required
upstream evidence is absent or non-promotable.

## 5. Private output-state audit

The required final corpus root is:

`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`

It is absent at this decision baseline. No accepted artifact manifest, corpus
record table, partition table, source-registry binding, class-count table, or
corpus validation report exists at that root.

The archived diagnostic resolver root exists separately at:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

Its output artifact-set identity is:

`149212b76336e77f9c8a8a4d9b48c13a88d8a22e74575585b24bccc2aa438a98`.

That root is permanently `NON_PROMOTABLE_DIAGNOSTIC`. It is not the missing
corpus and cannot be copied, renamed, adapted, or treated as one.

## 6. Upstream chain reconciliation

The minimum promotable chain is:

```text
accepted development dataset
  -> accepted canonical candidate evidence
  -> accepted feature rows and H=12 labels
  -> leakage-safe chronological partitions
  -> accepted independent pretraining corpus
  -> later training-readiness decision
```

The current chain stops at canonical candidate evidence. The terminal
cross-segment resolver produced no resolution and cannot convert the closed
Phase-A control into an accepted candidate bundle. Consequently:

- no promoted candidate table exists;
- no accepted real-data feature table exists;
- no accepted H=12 target vector exists;
- no accepted TRAIN/VALIDATION/CALIBRATION assignment exists;
- no accepted preprocessing-fit population exists; and
- no accepted corpus manifest exists.

Downstream stages must remain uncalled. An absent downstream artifact is the
correct fail-closed result, not an artifact to backfill.

## 7. Data-quality decision

| Dimension | Finding | Readiness |
|---|---|---|
| Source acquisition | Substantial immutable GC evidence and calendar evidence exist. | Necessary but insufficient. |
| Public reproducibility | Dataset, candidate, feature/label, continuity, resolver, and corpus contracts have deterministic test coverage. | Engineering-ready. |
| Candidate completeness | Closed Phase A/Phase B evidence supplies no promotable canonical candidate population. | Not ready. |
| Label completeness | No accepted candidate population exists to evaluate the fixed H=12 label contract. | Not ready. |
| Partition integrity | No accepted records exist to assign while preserving purge, embargo, and sealed final OOS. | Not ready. |
| Corpus integrity | Final corpus root and manifest are absent. | Not ready. |
| Training fitness | No feature matrix, target vector, immutable split, or preprocessing fit population exists. | Not ready. |

The project has trustworthy engineering evidence for a negative readiness
decision. It does not have trustworthy evidence for model fitting.

## 8. Why another resolver rerun is not the next step

The final resolver transaction passed every locked byte, manifest, calendar,
identity, determinism, and atomic-publication gate. Its `UNKNOWN` result is an
authentic admissible output, not a failed process. Another run against the
same immutable inputs and implementation would repeat an already consumed
question and would not create new evidence.

The following are prohibited readiness repairs:

- widening or shifting the confirmation window;
- changing session or segment boundaries;
- weakening event/FVG direction or identity requirements;
- using later bars or final-OOS outcomes to choose a rule;
- converting UNKNOWN to NONE or VALID by convention;
- manually selecting chart patterns;
- using an LLM to infer missing candidate evidence; or
- copying diagnostic results into corpus records.

## 9. Training and model decision

Training readiness is exactly `NOT_READY`. AI training has not started.

No model may be fit, tuned, calibrated, compared, serialized, or used for
inference because all of the following are absent:

1. an accepted independent feature matrix;
2. an accepted target vector;
3. immutable TRAIN/VALIDATION/CALIBRATION assignments;
4. purge and embargo conservation evidence;
5. a preprocessing-fit boundary;
6. baseline and promotion metrics; and
7. an accepted untouched final-OOS contract for later use.

The local language model remains research-assistance only. It has no authority
to receive raw private market payloads, alter evidence, manufacture labels,
select trades, override gates, or execute orders.

## 10. Legitimate future choices

The current evidence permits only these bounded choices:

1. pause model-training work while retaining all immutable evidence and public
   engineering contracts; or
2. prepare one documentation-only, independently falsifiable development-data
   hypothesis that does not rescue Phase A or Phase B, does not use final OOS,
   and defines its candidate evidence before implementation or outcome access.

Neither choice grants a private run, source/test implementation, feature or
label build, corpus build, model training, OOS access, integration, or trading
authority. Acquiring data solely to force a positive result is prohibited.

## 11. Exact task scope and verification

The only new path in this task is:

`docs/gc_futures_independent_pretraining_post_resolver_readiness_decision.md`

The three pre-existing unrelated untracked proposal files remain outside
scope and untouched. No source, test, fixture, private artifact, accepted
evidence, configuration, dependency, runtime, integration, or other document
may change.

Required acceptance checks are:

- exact one-file task scope;
- `git diff --check` PASS;
- focused public pretraining corpus regression PASS;
- full explicit `tests/` regression PASS;
- committed terminal-decision byte/hash reconciliation;
- final corpus root absence;
- private diagnostic root presence without mutation;
- clean tracked worktree and Git index; and
- zero training, final-OOS, integration, execution, and trading contact.

Fresh cache-disabled verification on `2026-08-31` produced:

- focused pretraining corpus regression: `66 passed in 0.80s`;
- full explicit public regression: `2674 passed in 38.86s`;
- exact one-file scope and `git diff --check`: `PASS`;
- local baseline and committed terminal-decision hash reconciliation: `PASS`;
- absent final corpus root and present immutable resolver root: `PASS`; and
- tracked worktree and Git index before this untracked document: `CLEAN`.

## 12. Final decision and STOP boundary

The exact decision is:

`POST_RESOLVER_PRETRAINING_NOT_READY_TERMINAL_UPSTREAM_UNKNOWN_NO_TRAINING_NO_OOS`.

The project remains in evidence-governance and pretraining-data-readiness work.
The public corpus builder is retained, but there is no accepted independent
pretraining corpus and no authority to train an AI model.

This record stops before staging, commit, push, private rerun, source/test
change, candidate generation, feature/label build, dataset/corpus build,
training, final-OOS access, model evaluation, runtime integration, prediction,
strategy, risk, order, execution, or trading action.
