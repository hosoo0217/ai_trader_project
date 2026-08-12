# GC Futures Phase-A Candidate-Evidence V3 Private-Run Change Proposal

## 1. Proposal Record

- Proposal ID: `GC-PHASE-A-CANDIDATE-EVIDENCE-PRIVATE-RUN-PROPOSAL-V4`.
- Date: `2026-08-12`.
- Baseline commit: `d9a4d488fdaa4e4e6e17b77f75c56f9d2f61c7cc`.
- Baseline subject: `fix(smc): preserve Inducement range causality`.
- Classification: documentation-only private-execution boundary and readiness record.
- Current decision: `READY_FOR_EXPLICIT_V3_CANDIDATE_PRIVATE_RERUN_AUTHORIZATION`.

This record defines the only admissible future path from the accepted immutable Phase-A V3 GC
dataset and its accepted immutable V3 structural seed to private Candidate Evidence. It does not
authorize that execution. It grants no feature/label, training, OOS, model, integration, strategy,
risk, execution, or trading authority.

## 2. Decision Summary

The required public dataset, structural-seed, and Candidate Evidence implementations are committed.
The accepted V3 dataset and accepted V3 structural-seed private roots are present, Git-ignored,
non-promotable, and independently validated. The first separately authorized Candidate Evidence
run failed closed after one of `54` segments, returned `UNKNOWN`, created zero candidates, and
published no output. The exact V3 Candidate Evidence output root therefore remains absent.

That failed-closed evidence exposed bounded dependency-contract defects. Dealing Range now
preserves canonical terminal same-lineage history, Inducement treats a range terminated before
confirmation as an ineligible sequence rather than malformed evidence, and Candidate Evidence
passes only external ranges and displacement-linked FVGs with their matching histories into
Inducement. A subsequent long-timeout rerun remained fail closed and published no output; it
exposed recursive malformed-evidence recovery and rejection of canonical Equal Liquidity
membership-only revision ordering. Inducement now bounds malformed recovery to one result and
uses only the later member's safe confirmation-index lower bound when an exact revision timestamp
is not present in the immutable pool. The four correction commits are
`507b46e436501c4e4b00b17d9b9acf817992158a`,
`4064483840426e67e44847200f679e0f9028279b`, and
`b57d4c671d2589e2028d4a31eaf56a60f637eb2b`, followed by
`7ecc1d3d298dc9729dd083e3e1a599bb4f3fa324` for the final two Inducement corrections.

A later bounded diagnosis reproduced the remaining range/map mismatch without publishing private
output. A same-lineage ACTIVE Dealing Range boundary revision retained its original construction
transition, allowing the revision to be selected before its own immutable first-known provenance.
Inducement now defines each range revision's effective moment as the causal maximum of that
first-known provenance and its final lifecycle transition. The fifth correction commit is
`d9a4d488fdaa4e4e6e17b77f75c56f9d2f61c7cc`.

The readiness chain is exact and one-way:

1. accepted V3 dataset ID
   `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
2. accepted structural seed ID
   `e741a230d961cda290f5d20d4fd5a0b4b1bd2cb54795c1d0c009a2e17148e8f0`;
3. committed Candidate Evidence version `GC-CANDIDATE-EVIDENCE-V1`;
4. future private Candidate Evidence output under a new non-overwriting `_v3` root.

Current verification evidence is `285` focused passes in `1.46s` across the structural, candidate,
and Inducement modules and `2297` full-regression passes in `11.79s`. These tests and the accepted engineering artifacts prove bounded
deterministic plumbing only. They do not establish an edge, model quality, profitability,
generalization, production readiness, or permission to train.

## 3. Verified Repository Baseline

At this proposal baseline:

- `HEAD` equals `d9a4d488fdaa4e4e6e17b77f75c56f9d2f61c7cc`; local `origin/main` and live
  remote `main` remain `7ecc1d3d298dc9729dd083e3e1a599bb4f3fa324` pending a separately authorized
  export of the reviewed local commit chain;
- the tracked worktree and index are clean;
- exactly three pre-existing untracked documentation files are outside this task and remain
  untouched;
- the accepted V3 dataset root exists at
  `private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`;
- the accepted V3 structural root exists at
  `private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`;
- `private_data/sierra_chart/gc_2026_phase_a_candidate_evidence/` is absent;
- `private_data/sierra_chart/gc_2026_phase_a_candidate_evidence_v3/` is absent;
- feature/label private execution, training, model fitting, OOS outcome access, strategy
  integration, and trading have not begun.

The focused verification command covered
`tests/test_gc_candidate_evidence_builder.py` and
`tests/test_gc_structural_seed_evidence.py` plus `tests/test_inducement.py` and passed `285` tests in
`1.46s`. The full command passed `2297` tests in `11.79s`.
Both used `-p no:cacheprovider`; neither accessed private data or changed Git state.

## 4. Exact Documentation-Only Scope

This task may create and correct only:

`docs/gc_futures_phase_a_candidate_evidence_private_run_change_proposal.md`

It may read committed source, tests, documentation, Git metadata, and the bounded acceptance
metadata already recorded in accepted private manifests and checkpoints: artifact names, hashes,
byte lengths, identities, counts, statuses, reasons, configuration, and call counts. It must not
inspect or expose raw market rows, full nested dataset/structural payloads, or any future candidate
payload to a language model. It must not modify Python, tests, fixtures, private data, calendars,
requirements, configuration, package exports, integration wiring, or any other documentation.

After independent audit, exact-path staging and one local documentation commit are allowed for this
file only. Push and private execution remain separately gated.

## 5. Authority and Global Freeze

The global code freeze remains active. This proposal grants no authority to:

- create, overwrite, repair, rename, or delete accepted private inputs;
- invoke `build_gc_candidate_evidence()` on private evidence;
- create Candidate Evidence private output;
- call the feature/label builder or flatten segment-qualified candidates;
- create features, labels, splits, fitted models, scores, predictions, backtests, or OOS results;
- select a strategy, change risk, open trades, or modify execution/runtime behavior;
- send raw private market data, full nested private payloads, or future candidate evidence to a
  local or remote language model;
- stage, commit, or push anything except this exact documentation file under the accepted local Git
  workflow.

No future permission is inferred from an existing implementation, passing tests, an accepted
upstream artifact, or a reserved private path.

## 6. Accepted V3 Dataset Binding

The only admissible dataset input is the immutable root:

`private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`

Its external acceptance binding is:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- dataset status: `VALID`;
- exact reason tuple: `("CANONICAL_DATASET_BUILT",)`;
- blocking reasons: `()`;
- builder version: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- builder source SHA-256:
  `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`;
- dataset ID: `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- artifact-manifest SHA-256:
  `077D1FF1E62E97E005F019CEDED3B0CE0AC22B4CA9DFB273904E41618AD05658`;
- build-result SHA-256:
  `3A5F28D47B2D1A7662E5D6EC581E04F1BCFC6E79CD20AE3BE99127756C307FA9`;
- input-binding SHA-256:
  `99E7356985C6C6BFC7A23BF6250DE0B13274732788570FF37BCD8AEF7219DFFA`;
- V2/V3-comparison SHA-256:
  `AFA155619348985D07255D432B9B77FF79529ECFD5B2A917CDDEE0BED43285AD`;
- validation-report SHA-256:
  `02A80C77B169C8E691569C847BB9F50B233C90E843A005CD395BAAB25A29FF85`;
- README SHA-256:
  `B7DD64CE871AD673F43B79A06E91EB1EC9204A3BE7D328DD0EABE53CD1E024DC`;
- artifact-set identity:
  `2a752b2c68eeb1a1dc9d56c36d10fce584fde4c94ae89641ff09f8234c62f6eb`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- timezone and timezone-data version: `America/New_York`, `2026.2`;
- development bars: `7103`;
- OOS bars: `0`;
- canonical segments: `54`;
- acquisition-attested missing parent slots: `73`;
- acquisition-attested no-trade intervals: `73`;
- roll trade dates: `()`.

The V2 root and identities are historical evidence only and are not valid runtime substitutes.

## 7. Accepted V3 Structural-Seed Binding

The only admissible structural input is the immutable root:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`

It contains exactly five accepted files:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `8873` | `245A34857E6E2D6161186226B882FA9B70DD01809811C92A8C10199E9D704AFA` |
| `structural_seed_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2557118` | `E1F1BCA786040FADDA73798F80ADF96BFDA3A0D37384FBEFC56EEA1B77271E61` |
| `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `1740` | `AD6AD0A58C60906ED595052C19180173BBEC21D79920C43D8297C8FB23B9D32C` |
| `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `1092` | `E9E9DA10E8B91889C31713896F1B132BE19B2B5C56B08EC2A7E89E113CD89889` |
| `README_NON_PROMOTABLE_ENGINEERING_PILOT.md` | `770` | `E8DB00E86D15E213BC27BFBCD266D5A58C99DFDFFEE985962664EE84DA4F9DE7` |

The structural manifest binds:

- status `VALID`, reason `STRUCTURAL_EVIDENCE_VALID`, and blocking reasons `()`;
- artifact-set identity
  `fd5fd0867ab86f68d4cd773784bf5ca7d817498babab62e3dfbfcef9fa5f2cb3`;
- seed ID `e741a230d961cda290f5d20d4fd5a0b4b1bd2cb54795c1d0c009a2e17148e8f0`;
- source-bar digest
  `d741a821e5b84b5ca08582a431d2eaf738db73a381bd35ae0dccc4662a8722f6`;
- `1789` Dealing Range swings;
- `1789` Equal Liquidity swings;
- `624` Structure Events;
- `124` Fair Value Gap context links;
- exact object equality between build and validation results;
- `training_allowed=false`, `promotion_allowed=false`, and `integration_allowed=false`.

A matching seed ID without matching nested evidence and all five file hashes is insufficient.

## 8. Calendar and Runtime Binding

Candidate Kill Zone analysis uses the exact immutable calendar source:

`private_data/sierra_chart/gc_2026_phase_a_pilot/calendar_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.json`

Its SHA-256 is
`F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`. It contains exactly `29`
strictly increasing `KillZoneCalendarEntry` records from trade date `2026-02-18` through
`2026-03-30`, all with status `OPEN`, exact aware UTC session bounds, calendar version
`GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`,
timezone `America/New_York`, and timezone-data version `2026.2`.

The future harness reconstructs those exact frozen entries in file order. It does not infer a
holiday, repair a timestamp, substitute split-session entries, fetch an external calendar, or use a
filesystem/locale sort. Runtime tzdata must report exact version `2026.2`, and both
`America/New_York` and `Asia/Tokyo` must be available. A mismatch stops before Candidate Evidence.

## 9. Accepted Committed Dependency Bytes

Any future readiness revision or private execution must stop on drift from these audited artifacts:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `tests/test_gc_dataset_builder.py` | `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878` |
| `analysis/gc_structural_seed_evidence.py` | `17F74A8D856FB31CBC0B2602AC8B4466D66582B744282AB400BEA5F3110F31A7` |
| `tests/test_gc_structural_seed_evidence.py` | `8444424B03749E6DEB89E586041151FEFAB63433AA5A32D8798CC2A429853D54` |
| `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md` | `69F82FF403FBD8FB5A380441389341F977CB79D6BA2E4278F677490432AAEA66` |
| `docs/gc_futures_phase_a_structural_seed_private_run_change_proposal.md` | `9B6C8E55754FC1488719031070858F74E0CB681D26C5B65AA929735C773945F5` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `tests/test_gc_candidate_evidence_builder.py` | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md` | `7DBA87A6D19734450A4AE70B978005763D6C1B90C7EB58721D9B413FFC857ADB` |
| `docs/gc_futures_phase_a_candidate_evidence_change_proposal.md` | `A0E35BF5A7F4EC451DF7898223FA0467C3FA36AA2F775008C0FB7C4D62F38941` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `F2D6754A7456D39C6BCC5EE312024F8C538CFDBD43474BC76957D44B62EBCE0E` |
| `smc/liquidity_map.py` | `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `smc/inducement.py` | `A7B7E4499AA29E4077CD93537A2967364EA6925A65138B4C88027F9C9B04261B` |
| `tests/test_inducement.py` | `9E9188ACFFB562AD01E968652240081312A837A66B9198E1A2BAA504726D25BB` |
| `docs/smc_v2_inducement_checkpoint.md` | `961DEC27FE3F03E28CD3ECF99A3ADC804625058871DD8B4732AE32C55D4A080A` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |

Hash equality is necessary but not sufficient. Exact signatures, frozen dataclasses, enum values,
version constants, identity schemas, chronology, and status semantics must also pass.

## 10. Exact Future Reconstruction Contract

The future private Candidate Evidence run reconstructs the accepted runtime inputs only through the
committed public path:

The exact immutable acquisition root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

The reconstruction consumes exactly these seven runtime input files in the stated role order:

| Role | Artifact | Bytes | SHA-256 |
|---|---|---:|---|
| calendar | `calendar_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `8811` | `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED` |
| GCG26 export | `GCG26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `3104` | `27552A778ABF2FB158D7107EFF9232396C9AAE5E489A55B50259923C379BE839` |
| GCG26 coverage | `GCG26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2627` | `C49B4BA7CD03ECD649E8A13DDF7D0CD2AA2393838CD5C6D810256DFE7ED3C941` |
| GCJ26 export | `GCJ26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `818320` | `6E0419AF7E85BF5C31A5F79AA36ADEED1A9B1D8BF3123CBB8DDA7AF1313EED3A` |
| GCJ26 coverage | `GCJ26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2991` | `D2A64844EF65B8E8B11D643FB553AB4A70BDF16C96E78F8E98CBEAE75573E79A` |
| GCM26 export | `GCM26_COMEX_5m_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.txt` | `733413` | `30ABDCBC2F41498EF36C734EA28780B62E7338882543D41A6FDDB33472036F3D` |
| GCM26 coverage | `GCM26_COMEX_5m_20260218_20260330_provenance_NON_PROMOTABLE_ENGINEERING_PILOT.json` | `2963` | `D84B9E8297B21CE47C1188B637FF67886AC1BFE72A1C5DE8981EF957A7D3F52B` |

No other file in that root is a runtime input. The three exports are parsed in exact
`GCG26`, `GCJ26`, `GCM26` order; their three coverage sidecars and the calendar are reconstructed
from their bound bytes without filename discovery or directory enumeration.

1. call `parse_sierra_chart_gc_export()` exactly once for each of the three accepted bounded export
   byte streams;
2. reconstruct the exact accepted coverage and calendar tuples from their immutable bound bytes;
3. call `build_gc_futures_dataset()` exactly once with the locked V3 split-session configuration;
4. require object and identity equality with the accepted V3 dataset;
5. call `build_gc_structural_seed_evidence()` exactly once with the exact default structural config;
6. call `validate_gc_structural_seed_evidence()` exactly once as an external preflight;
7. require build/validation object equality and exact equality with the accepted V3 structural
   evidence;
8. call `build_gc_candidate_evidence()` exactly once.

`build_gc_candidate_evidence()` itself must perform its committed internal call to
`validate_gc_structural_seed_evidence()` before analyzer execution. The external harness call count
and the builder-owned internal validation are recorded separately; neither may be omitted or
misreported.

The exact dataset configuration remains:

```text
instrument="GC"
timeframe="5M"
source_timezone="Asia/Tokyo"
exchange_timezone="America/New_York"
timezone_data_version="2026.2"
tick_size=Decimal("0.1")
initial_contract="GCJ26-COMEX"
initial_trade_date=date(2026, 2, 23)
roll_confirmation_sessions=3
oos_start_trade_date=date(2026, 3, 31)
oos_end_trade_date=date(2026, 3, 31)
```

No JSON-to-result shortcut, pickle, `eval`, private helper, partial equality, silent repair, manual
foreign ID, filesystem-order inference, V2 carry-forward, or synthetic replacement is allowed.

## 11. Exact Candidate Public API and Configuration

The only future candidate operation is:

```python
build_gc_candidate_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCandidateEvidenceResult
```

The identity operation remains exact and keyword-only:

```python
make_gc_candidate_evidence_id(
    *,
    identity_kind: GCCandidateEvidenceIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    calendar_version: str,
    timezone_data_version: str,
    seed_id: str,
    config: GCCandidateEvidenceConfig,
    detector_versions: tuple[tuple[str, str], ...],
    segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...],
    candidate_references: tuple[tuple[str, str], ...],
    bundle_id: str | None = None,
) -> str
```

The exact identity kinds are `BUNDLE` and `MANIFEST`. The exact candidate configuration is frozen
with `EqualLiquidityConfig(2, 2, 3)` and `DealingRangeConfig(2, 1)`. The fixed detector chain is:

```text
EQUAL_LIQUIDITY / SMC-V2-EQUAL-LIQUIDITY-1
DEALING_RANGE / SMC-V2-DEALING-RANGE-1
LIQUIDITY_MAP / SMC-V2-LIQUIDITY-MAP-1
FAIR_VALUE_GAP / SMC-V2-FAIR-VALUE-GAP-1
INDUCEMENT / SMC-V2-INDUCEMENT-1
KILL_ZONE / SMC-V2-KILL-ZONE-1
```

No adapter, alternate config, positional call, monkeypatch, subclass, package re-export, manual
identity, or extra detector is allowed.

## 12. Input Admissibility Gate

Before the candidate call, the future harness must prove all of the following:

1. the V3 dataset root contains exactly its accepted six files with exact hashes;
2. the V3 dataset reconstructs as `VALID`, binds the exact dataset ID, contains `54` development
   segments, `7103` development bars, and zero OOS bars;
3. the structural root contains exactly its accepted five files with exact hashes;
4. the structural public build and validation are object-equal, `VALID`, reasoned exactly
   `STRUCTURAL_EVIDENCE_VALID`, and bind the accepted seed ID and member counts;
5. every structural source/confirmation moment belongs to exactly one accepted development segment;
6. the exact `29` Kill Zone calendar entries reconstruct in strictly increasing trade-date order
   with the accepted version and UTC bounds;
7. runtime timezone evidence matches Section 8;
8. every Section 9 tracked dependency and this proposal's committed byte hash matches;
9. the exact final private Candidate Evidence root is absent;
10. OOS outcomes, labels, returns, PnL, model state, and integration state remain unopened.

Any mismatch stops before `build_gc_candidate_evidence()` is called.

## 13. Analyzer Chain and Status Gate

For every reached canonical segment, the candidate builder calls exactly once, in order:

1. Equal Liquidity;
2. Dealing Range;
3. Liquidity Map;
4. Fair Value Gap;
5. Inducement;
6. Kill Zone.

All six complete before the next segment. No bar, seed member, detector output, history, state, or
lookback crosses a segment boundary. A detector `INVALID`, `AMBIGUOUS`, or `UNKNOWN` stops the
current chain and every later segment, preserves only complete prior segment evidence, and cannot
publish an accepted private result.

Only these complete aggregate outcomes are admissible for private diagnostic publication:

- `VALID` with at least one candidate, non-null canonical candidate manifest, reason
  `CANDIDATE_EVIDENCE_VALID`, and all `54` complete segment results;
- `NONE` with zero candidates, null candidate manifest, reason
  `NO_QUALIFYING_CANDIDATE_EVIDENCE`, and all `54` complete segment results.

`INVALID`, `AMBIGUOUS`, `UNKNOWN`, exception, partial segment history, unrecognized reason, or
incomplete segment coverage is a failed run. A failed run publishes no accepted candidate root.

## 14. Candidate Assembly and No-Look-Ahead Boundary

Candidates are reference-only assemblies of already validated same-segment detector outputs. The
builder may not recompute, mutate, enrich, repair, or reinterpret a detector result. Before the
Inducement call it passes only canonical `EXTERNAL` Dealing Range snapshots and only FVGs with a
non-null formation-time `displacement_id`, together with exactly the transition and snapshot
histories belonging to those eligible FVG IDs. Internal ranges, unlinked FVGs, and their histories
remain valid upstream diagnostic evidence but are not admissible Inducement dependencies. Exact
eligibility requires the accepted Inducement, range/map context, internal liquidity pool, external
target, Structure Event, causally linked FVG with complete history, exact confirmation bar, and
verified `NEW_YORK_AM` Kill Zone context. A canonical external range that terminates at or before
confirmation makes only that sequence ineligible and promotes no candidate; malformed range
identity or history remains fail-closed `INVALID` evidence.

Canonical Equal Liquidity membership-only revisions retain upstream tuple order when the immutable
pool does not carry the new member's exact confirmation timestamp. The last source index supplies
only the committed confirmation-delay lower bound; unavailable timestamp provenance is never
invented. A demonstrably impossible interleaving remains `INVALID`. Malformed dependency recovery
is bounded to one fail-closed result and cannot recursively re-enter itself.

Candidate order is exact dataset segment ordinal followed by exact public Inducement tuple order.
Local bar indices may repeat across segments and never form a dataset-global chronology. Hash,
direction, filename, or filesystem order is not a chronology tie-break.

Only evidence known at confirmation close may be used. Future target outcomes, returns, labels,
entry/exit, PnL, risk, model scores, language-model output, OOS roles, later segments, or a favorable
downstream result are forbidden inputs. The current feature/label builder is not called.

## 15. Candidate Identity and Result Contract

`BUNDLE` identity binds normalized instrument/timeframe, exact tick size, dataset ID, calendar
version, timezone-data version, seed ID, full frozen config, fixed detector-version order, ordered
segment-result IDs, and ordered segment-qualified candidate references. `MANIFEST` additionally
requires the exact recomputed bundle ID.

Every complete `GCCandidateEvidenceSegmentResult` contains six full-result digests in detector-chain
order. Every `GCSegmentCandidateEvidence` binds exact segment ordinal/ID and the byte-equivalent
`GCFeatureLabelCandidateEvidence`. Candidate references are exact `(segment_id, inducement_id)`
pairs in public candidate order. Foreign IDs may recur across different segments but cannot be
matched or deduplicated without segment provenance.

The aggregate status precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

A non-`VALID` result never synthesizes a candidate `BUNDLE` or candidate `MANIFEST`. The separate
private artifact manifest in Section 17 is an output-byte manifest, not a replacement candidate
identity and may describe an accepted complete `NONE` result.

## 16. Exact Future Private Output Root

After a separate explicit execution authorization, the only private output root is:

`private_data/sierra_chart/gc_2026_phase_a_candidate_evidence_v3/`

The `_v3` suffix is mandatory. It prevents overwrite or confusion with the earlier V2-era reserved
path, which remains absent and unused:

`private_data/sierra_chart/gc_2026_phase_a_candidate_evidence/`

The V3 root must be Git-ignored. No output may be copied into tests, fixtures, tracked docs,
features, labels, training, models, backtests, integration, or runtime directories.

## 17. Exact Future Output Artifact Set

The future V3 Candidate Evidence root may contain only:

1. `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
2. `candidate_evidence_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
3. `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
4. `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
5. `README_NON_PROMOTABLE_ENGINEERING_PILOT.md`.

The candidate artifact contains the exact aggregate result, candidates, complete segment results,
and candidate manifest when status is `VALID`. It contains no raw exports, duplicate dataset,
duplicate structural seed, feature, label, outcome, trade, model, prompt, cache, notebook, image, or
external fixture.

## 18. Deterministic Serialization Contract

Machine-readable artifacts use UTF-8 without BOM, LF endings, one terminal newline, lexically
sorted JSON object keys, compact separators `(",", ":")`, and `ensure_ascii=True`. Ordered tuples
serialize as ordered JSON arrays; dictionaries never encode causal order.

Canonical representations are:

- aware timestamps normalized to UTC ISO-8601 microseconds with terminal `Z`;
- dates as `YYYY-MM-DD`;
- finite Decimals as fixed canonical text with zero `0.0`;
- enums as exact `.value`;
- identities as lowercase 64-hex;
- artifact SHA-256 as uppercase 64-hex;
- booleans as JSON booleans.

Host paths, object addresses, current clock time, locale, filesystem timestamps, random values,
Python `repr`, pickle, hash iteration, and environment-specific exception text are forbidden
identity inputs.

## 19. Input-Binding and Artifact-Manifest Contract

`input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind at least:

- proposal ID, committed proposal-file SHA-256, exact source commit, and all Section 9 hashes;
- exact V3 dataset root purpose, six artifact hashes, artifact-set identity, builder version,
  dataset ID, config, calendar/tzdata, counts, reasons, blocking reasons, and segment order;
- exact V3 structural root purpose, five artifact hashes, artifact-set identity, seed ID,
  source-bar digest, config, counts, reasons, blocking reasons, and object-equality evidence;
- exact calendar source hash, entry count/order/version, and runtime timezone evidence;
- candidate version/config, exact public signatures, and fixed detector versions;
- explicit `oos_outcome_accessed=false`, `feature_label_run_performed=false`,
  `training_allowed=false`, `integration_allowed=false`, and `promotion_allowed=false`.

`manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind every other artifact's exact name,
SHA-256, and byte length; aggregate status/reasons/blocking reasons; complete segment-result count;
candidate count; candidate manifest/bundle IDs when present; exact external public call counts; the
builder-owned structural validation boundary; and a deterministic artifact-set identity.

Matching high-level counts without matching full ordered evidence and every artifact hash is
insufficient.

## 20. Atomic Publication, Repeatability, and Prefix Boundary

All output bytes are created in a new task-specific temporary directory inside the private parent,
validated there, and moved to the final V3 root only after every gate passes. The final root must be
absent before publication. No accepted root is incrementally written, repaired, or overwritten.

Two independent executions with identical accepted inputs, committed dependencies, configuration,
and proposal bytes must produce object-equal candidate results and byte-identical machine-readable
artifacts. README and validation-report bytes must also be deterministic under the locked evidence.

Candidate prefix invariance applies only at complete segment boundaries within one validated run.
Same-effective append, partial segment, historical insertion, source/calendar repair, reorder,
dataset/seed/version mutation, or dependency drift is ineligible and requires full revalidation.
No failed/current segment candidate or partial segment result is promoted; strictly prior complete
evidence remains immutable in memory but a failed aggregate still publishes no accepted root.

## 21. Inline Synthetic Exact 48-Case Future Matrix

The future private-run harness and audit preserve this exact sequential logical matrix.
Parameterization may expand collected executions without changing the `48` logical cases.

1. Missing accepted V3 dataset root stops before private execution.
2. Missing accepted V3 structural root stops before private execution.
3. Existing final Candidate Evidence V3 root stops without overwrite.
4. V2 dataset, V2 seed, or V2 output-root substitution is rejected.
5. Dataset, structural, candidate, detector, test, checkpoint, or proposal hash drift stops,
   including drift from the five exact correction commits bound by this V4 proposal.
6. Missing, extra, duplicate, reordered, or malformed private input file stops.
7. Runtime tzdata/version/zone mismatch stops before reconstruction.
8. Exact three source exports parse once each and preserve accepted order.
9. Exact coverage and split-session calendar evidence reconstruct without repair.
10. Public V3 dataset builder is called exactly once with the locked config.
11. Rebuilt dataset is object/identity equal to accepted `VALID` evidence.
12. Nonzero OOS bars or OOS outcome access stops before structural/candidate calls.
13. Structural builder is called exactly once with exact default config.
14. External structural validator is called exactly once with the same runtime objects.
15. Structural build/validation object equality and accepted seed equality pass.
16. Candidate builder's internal structural validation remains mandatory and exact.
17. Structural status/reason/count/digest/identity mismatch stops before analyzers.
18. Exact `29` Kill Zone calendar entries reconstruct in source order.
19. Calendar entry type, field, order, bound, version, or status mismatch is rejected.
20. Candidate builder exact keyword-only signature/default/config is locked.
21. Candidate identity builder exact kinds, parameters, defaults, and schemas are locked.
22. Every public candidate dataclass field/default/frozen state and export is exact.
23. Each reached segment consumes only its exact development bars and seed members.
24. Equal Liquidity is called once per reached segment with exact projected evidence.
25. Dealing Range is called second with exact swings/events and local observations.
26. Liquidity Map is called third with exact upstream canonical results.
27. Fair Value Gap is called fourth with exact candles and context links.
28. Inducement is called fifth with only external ranges and displacement-linked FVGs plus their
    complete matching same-segment histories; canonical membership-only pool revisions preserve
    causal tuple order without an invented confirmation timestamp.
29. Kill Zone is called sixth with exact bounded calendar entries.
30. All six analyzers complete atomically before the next segment begins.
31. Cross-segment state, lookback, seed matching, or output reuse is rejected.
32. Candidate reference roles, event/FVG suffix binding, and confirmation moment reconcile;
    terminal-before-confirmation external range evidence makes the sequence ineligible without
    candidate promotion, while malformed dependency recovery returns one bounded `INVALID` result.
33. Exact verified `NEW_YORK_AM` OPEN/EARLY_CLOSE context is required.
34. Candidate order is segment ordinal then public Inducement tuple ordinal.
35. Same local index in different segments remains independently segment-qualified.
36. Same-group opposition remains atomic `AMBIGUOUS` and promotes no current group.
37. Final precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
38. Later determinable failure preserves only complete prior in-memory evidence.
39. No partial/failing/later segment candidate or result is promoted.
40. Complete `VALID` binds nonempty candidates, `54` results, bundle, and manifest.
41. Complete `NONE` binds zero candidates, `54` results, null candidate manifest, and exact reason.
42. `BUNDLE` identity exhaustively binds ordered segment/result/reference evidence.
43. `MANIFEST` identity recomputes exact `BUNDLE` and rejects all schema drift.
44. Candidate JSON round-trips exact nested types, tuples, timestamps, Decimals, enums, and order.
45. Artifact manifest binds exact five-file scope, hashes, lengths, calls, and status.
46. Repeat execution is object-equal and machine-byte-identical without clock/path influence.
47. Atomic failure leaves final root absent and accepted upstream roots byte-immutable.
48. Feature/label, training, OOS outcomes, model, strategy, risk, execution, integration, Git, and
    trading surfaces remain unused.

## 22. Independent Validation Evidence

The future private validation report must independently verify:

- exact Section 6, 7, 8, and 9 hashes, correction commits, and identities;
- exact public signatures, constants, frozen fields, enum values, and exports;
- exact reconstruction and public call counts;
- object-equal dataset and structural evidence;
- complete candidate status/reasons/blocking reasons and all `54` segment results;
- every result digest, candidate reference, candidate bundle/manifest identity when present;
- no cross-segment, OOS, future-dependent, synthetic, or model-derived evidence;
- canonical JSON round-trip and independent byte-identical repeat;
- exact output scope and Git-ignore evidence;
- unchanged accepted private inputs, source, tests, index, HEAD, and `origin/main`;
- `PRIVATE_CANDIDATE_RUN_PERFORMED=true` only after successful atomic publication;
- `FEATURE_LABEL_RUN_PERFORMED=false`, `TRAINING_STARTED=false`,
  `OOS_OUTCOME_ACCESSED=false`, and `INTEGRATION_STARTED=false`.

The report must not claim strategy edge, profitability, generalization, production readiness, or
trading authority.

## 23. Rollback, Promotion, and Immediate Stop Conditions

This documentation task rolls back by deleting only this uncommitted proposal. After commit,
rollback requires a bounded revert commit; history rewriting is forbidden.

A separately authorized private run may roll back only its new task-specific temporary directory or
new V3 Candidate Evidence root. It may not delete, alter, reuse, or relabel the accepted dataset,
structural seed, acquisition evidence, calendar, V2 history, or any tracked file.

Stop immediately on dependency/API drift, private input mutation, V2/V3 identity reuse, manifest
mismatch, timezone mismatch, reconstruction inequality, OOS contact, structural inequality,
calendar repair, analyzer higher status, incomplete segment chain, identity mismatch,
nondeterminism, exception leakage, partial publication, unexpected file, external fixture, local or
remote language-model access to private data, feature/label execution, training, model selection,
profitability analysis, strategy/risk/execution changes, integration, stage, commit, or push without
the exact separate authority.

Promotion is forbidden. A passing private Candidate Evidence artifact would remain a post-hoc,
non-promotable engineering result and would authorize only a separate downstream readiness audit.

## 24. Final Decision and Next Single Task

The final-rebound exact V4 Candidate Evidence private-rerun contract is specified. The accepted V3
dataset, accepted V3 structural seed, required calendar, committed dependency corrections, and
regression evidence satisfy the technical prerequisites. After this one-file proposal passes
independent audit and is committed, readiness is
`READY_FOR_EXPLICIT_V3_CANDIDATE_PRIVATE_RERUN_AUTHORIZATION`.

The next single task after documentation acceptance is a private run limited to:

`private_data/sierra_chart/gc_2026_phase_a_candidate_evidence_v3/`

That future task must execute the exact Section 10 chain, publish only the exact five Section 17
artifacts atomically, independently re-audit them, and stop. It must not invoke feature/label
generation, training, OOS outcomes, model fitting, strategy evaluation, integration, stage, commit,
or push.

This proposal authorizes only its exact one-file documentation acceptance workflow. Candidate
private execution and any remote export remain separately gated, and the global code freeze remains
active.
