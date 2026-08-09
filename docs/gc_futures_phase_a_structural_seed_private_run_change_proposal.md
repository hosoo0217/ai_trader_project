# GC Futures Phase-A Structural-Seed Private-Run Change Proposal

## 1. Proposal Record

- Proposal ID: `GC-PHASE-A-STRUCTURAL-SEED-PRIVATE-RUN-PROPOSAL-V1`.
- Date: `2026-08-09`.
- Baseline commit: `dba0322116b5c174bc5a318ea03747f39f0d9a07`.
- Baseline subject: `fix(analysis): preserve GC no-trade attestation count`.
- Classification: documentation-only private-execution boundary and readiness record.
- Current decision: `READY_FOR_EXPLICIT_V3_STRUCTURAL_PRIVATE_RUN_AUTHORIZATION`.

This record defines the only admissible future path from an accepted immutable Phase-A GC dataset
to private canonical structural-seed evidence. It deliberately does not authorize that execution.
The immutable V2 pilot remains historical evidence, and a separate immutable V3 split-session pilot
has now been reconstructed and independently accepted. This correction binds that exact V3 evidence
without mutating either private root or granting downstream authority.

## 2. Decision Summary

The standalone dataset, structural-seed, and candidate-evidence implementations and checkpoints are
committed. The accepted V3 pilot is present, Git-ignored, non-promotable, contains no OOS bars, and
has passed two object-equal and machine-byte-identical reconstructions. The exact V3 structural
private output root remains absent.

The accepted V3 pilot binds:

- builder version `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- builder source SHA-256
  `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`;
- builder-test SHA-256
  `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878`;
- dataset ID `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- artifact-manifest SHA-256
  `077D1FF1E62E97E005F019CEDED3B0CE0AC22B4CA9DFB273904E41618AD05658`;
- artifact-set identity
  `2a752b2c68eeb1a1dc9d56c36d10fce584fde4c94ae89641ff09f8234c62f6eb`.

`validate_gc_structural_seed_evidence()` still requires the current V3 manifest version and
recomputes every segment identity. The V2 root therefore remains inadmissible as a runtime object,
but the accepted V3 root now satisfies the previously blocking version and identity prerequisite.
Readiness authorizes only a separately approved private structural run; it does not authorize
candidate evidence, feature/label generation, training, OOS access, integration, or trading.

## 3. Verified Repository Baseline

At the corrected baseline:

- `HEAD`, local `origin/main`, and the pushed implementation commit equal
  `dba0322116b5c174bc5a318ea03747f39f0d9a07`;
- the tracked worktree and index are clean;
- three pre-existing untracked documentation files are outside this proposal and remain untouched;
- the immutable historical V2 pilot root exists at
  `private_data/sierra_chart/gc_2026_phase_a_pilot/` and is ignored by Git;
- the accepted V3 pilot root exists at
  `private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`, contains exactly six files,
  and is ignored by Git;
- `private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence/` is absent;
- `private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/` is absent;
- `private_data/sierra_chart/gc_2026_phase_a_candidate_evidence/` is absent;
- structural private execution, candidate private execution, feature/label execution, training,
  model fitting, OOS evaluation, strategy integration, and trading have not begun.

Historical test evidence remains evidence only and is not rerun by this documentation task:

- structural seed: `62` focused executions, `2218` full regression executions, exact `48` logical
  cases;
- candidate evidence: `52` focused executions, `2270` full regression executions, exact `48`
  logical cases.

The corrected dataset-builder evidence is `245` focused passes and `2276` full-regression passes,
with exact `48` logical cases. Those passing tests and the deterministic V3 rebuild prove bounded
engineering consistency only; they do not prove research validity, edge, or promotion readiness.

## 4. Exact Documentation-Only Scope

This task may create and correct only:

`docs/gc_futures_phase_a_structural_seed_private_run_change_proposal.md`

It may read committed source, tests, documentation, Git metadata, and immutable private manifest
metadata. It must not modify Python, tests, fixtures, private data, manifests, calendars,
requirements, configuration, package exports, integration wiring, or any other documentation.

After independent audit, exact-path staging and one local documentation commit are allowed for this
file only. Push and private execution remain separately gated.

## 5. Authority and Global Freeze

The global code freeze remains active. This record grants no authority to:

- rebuild or mutate the pilot;
- invoke the structural builder on private evidence;
- create, overwrite, repair, rename, or delete private evidence;
- invoke the candidate builder or feature/label builder;
- train, tune, fit, select, backtest for promotion, inspect OOS outcomes, or claim edge;
- change strategy, risk, broker, execution, trace, engine, runtime, or integration behavior;
- send private data to a local or remote language model;
- stage, commit, or push anything except this exact documentation file under separately confirmed
  local Git authority.

No future permission is inferred from a reserved path, committed implementation, passing unit
tests, or the existence of private V2/V3 evidence.

## 6. Accepted V2 History and V3 Pilot Evidence

The present private root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

Its immutable recorded identity is:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- build-manifest SHA-256:
  `55CA87E55988F9FF27C7C177DBB16813ACFD9096DCB37C370F70A936EDBA4F4C`;
- calendar SHA-256:
  `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- timezone: `America/New_York`;
- timezone-data version: `2026.2`;
- development bars: `7103`;
- OOS bars: `0`;
- canonical segments: `54`;
- acquisition-attested missing parent slots: `73`;
- roll trade dates: `()`.

These facts remain accepted as historical V2 engineering evidence. They do not authorize reuse as
a V3 runtime object, training data, final 2024-2025 research evidence, or production data.

The accepted non-overwriting V3 root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`

Its external acceptance binding is:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- status: `PASS` with dataset status `VALID`;
- exact reason tuple: `("CANONICAL_DATASET_BUILT",)`;
- blocking reasons: `()`;
- proposal ID: `GC-PHASE-A-PILOT-V3-SPLIT-SESSION-REBUILD-PROPOSAL-V1`;
- proposal SHA-256:
  `FEF0D8E96C37B261ACF2B252B59FE7F6ACD9B635E1C9A4656117509DCD73E0AD`;
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
- dataset ID: `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- builder version: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- timezone and timezone-data version: `America/New_York`, `2026.2`;
- ordered source IDs:
  `("1a8c876a57852d07c9bcd068c36c0c2244057ca13cc9e737d0909962e7c2cac1",`
  `"863aaff9e97cd8448a3edb008639e00be4bd0e35bcb72af8e9ed3a083a661a5e",`
  `"84a5b8e5599c6dce1bf06599c6cdefad7d27118a13ea86b856c1c9427d6c8918")`;
- ordered coverage IDs:
  `("c0a728eec42ca9cc692e3776ce83e95e99884ce3bfaad84d96adda6ef4505290",`
  `"35092c5d8e97251a6cf2afa323ae8195cfb4ba9675b51c8cd784c3ce75bb92c6",`
  `"1030b2cb66bf3154deeed18528d94f8fc5ba7357563dc9c6e00fe50c25eba205")`;
- coverage digest:
  `002734838874446ce4305f7d73664187400556b6b161ebb34d0e7b64b50b43d6`;
- raw UTC bounds: `2026-02-17T23:05:00.000000Z` through
  `2026-03-30T21:00:00.000000Z`;
- usable UTC bounds: `2026-02-22T23:05:00.000000Z` through
  `2026-03-30T21:00:00.000000Z`;
- source rows: `15412` parsed, `7103` eligible, `8309` excluded;
- volumes: `4742010` raw, `3829577` eligible, `912433` excluded;
- excluded rows: `1523` `BEFORE_INITIAL_BOUNDARY` and `6786` `ROLL_EVIDENCE_ONLY`;
- development bars: `7103`;
- OOS bars: `0`;
- canonical segments: `54`;
- missing parent slots: `73`;
- acquisition-attested no-trade intervals: `73`;
- roll trade dates: `()`;
- public parser/builder calls per reconstruction: `3/1`;
- independent reconstructions: `2`, object-equal and machine-byte-identical;
- `oos_outcome_accessed=false`, `structural_run_performed=false`,
  `training_started=false`, and `integration_started=false`.

The exact ordered V3 segment IDs are:

```text
22128c48a1fd066eb3e2f05db6edf8e04078b147de548256f7a9c634bfdbd72a
b4a6b226e2684c40d3ca5d11fa58ec779b3d9e440620ecc1437b93ff397228f4
96a2534525780bd95395c2128b0125b61dbbaca6788c0c94c251098337b52ac0
f04384b29c60a4c2a4f6da5c6cc03999d01520d170670a1db848f03b84989232
d132a5f39d3aeda2799e116af069d69d099b5516372105d3c217984fcee300a7
6f51c3c73d64639cc0d8e86391eb2c68ae596b80e1c96c6c857cea1d48d1fd8c
2f012cc0567bf5ec19716aa8e617ada16298900ac8f4c364da9c6d19fa711d6a
41c673ee6ab46e721d908256b462765956f060f97c1cebecd844ee9c9dd5f11f
3fc5d8302dfa006d2819ab8464704b972c42d04879f6e20a144769328dcd7e67
0bf69ff5c705ab9ebde43db67d8df954b0508d4dcc054d74942a73bacdd26fe0
22ed6c8e9f9f5b1fae036732255e5d8be3a4e11b57149cd8357a358cc5b253e0
e1d4f06409b0183ccc06ad2a5b9a680ad0978d7b9aba6443743e3f04b2ddb069
059c3350307d7822b7e2ab10b014fc8901218c8058ca4db633fe66e09f6864db
ed1b1bf51468e6b5c89aca6bf9c05291dc24b7944ad81c74ba10d8fd39bfbe28
44c34edec25ff5ac18f8da064a9a1cbc5b8f574fdb3e632f313ed6d0195a42f8
d500fde98a38bea2a8ffe96c5760c8e47080e4f7546b5a9498af04478c3397b8
79db5bb9021a551f74d3aa926cefecb2920cf551c8af71386056095358bfb028
26db8a7064318c040df66f5d1cc3e041c034556661354c54bc3968a9d2848c0f
c26c2880fe0fe33725967734b0feaee3a93f44a7cfcfa3630c72017bca8cd7fe
126f93b048071ae097aee9ae8b5eed3c0c775508708406f37f7e9e6d6a754622
34b15a2e12ecbaba30e4f5fa8b2e47132d48e383fa7ed47287ce8689450700ec
58bbe5e8a48245d151275aa6b9ea4ceeaac4561b67d075e1dd46aebc7c8059ae
6fc49150144808bc5cc5f410a9275f0f059819d7102b37f3e644c15b9a5db702
55ae0c2f3b6b148056c434a6ea4640f6c46ef7f3b8764a71e8e5d15a125c5860
e5bc42c8d74e8476556e3f5d867a8d4ceb15e44c8185d7f27f079912bbe414a9
b4ddf84e05c36a2ecb870d949e7bb66b2704588bfb5aeed27d2ca711c894f8e2
95002c047408dfc13fbe0ef100924565a6b76dfd9d7e23e9e74002afc0f8acd5
041a607d66ff8af4faf2540f8b56955f1a7ecf04eea8a293d4dd5da6584f7fb8
abe2ca7d22ab29b6e09dcb788fb0cbdfe07d7a0a740dcfbe6eeb9e548901ba60
1853860322a3b09dd090c993cff02e6ebb55df57c5f76577f817ab55f53e153d
ae62f594137bbff20ac3c2aa37573e9bf13c9e9dbf274ceaf65a4d2e8b6552bc
0947a0cf75bee1059ea1253ddfef32e377790de760e743b60c45996ab6797acc
5d5de18ce4bed5522ae4f2a22ca60ab7734c504567f4eed3bb6d6f873277cff4
fae4f5e600b58abb63f6c60fe4857b7f9dc7d2f16dc11d2cdb6f42931661115a
95301f0e09ea7aec412b99c388fda41f2174a1c57be1c3cf675a451f877648ca
6a6fd3c1dd0fd28bba040c24de05b09922567f6dd5c6efc5167444b1d8488fd2
c9aacbc990d3ecaeee329acbf5afe9b47aef1779f65dfb915578beec47979d17
434ff48821d42d4563c306a2747494881186930ba48f0e904ac1ece05ccc1a07
07f7f1e7e2251f1a65c02e19d411867f619662c51a84835ada30f1ff8891b9c1
f8d64585d63eacb922d38074b0bab173a39034a0cccb0ecd0854bb8908bef20e
171560c112c7bb2fec429e46c30db4792f83b44b01ed8f17d60081e92390093a
deca61f241b9f43eeffe5ba9b2f2fc9671ecc844cb9da2b1218825963f253aec
ab66f2671ed56c12c4d7e7dd3e4999f44650d05719c865f0317dfff8217b1caf
19c17a2287fd77a58a2f13cecd738ee35e94f53d8a23b778ecd50fd26748c393
23e8cff42113624d71ec1580abf40814719a7a135a06758ba03bad2b801a9dbf
31859725a9bce47e4ae841486c6af5fd0351bb32680bac27ed40e3b45a7301f1
f15d9ab3d263c05fc328972c59f2dbc3af9167a4c0428343ae4a3e98856200c9
f08d917d048d7aefa0ea3e6bf79f06b9b082f48252ed3e92cde4135200ab982b
cfbb6c878d36a32056945d799dadf34fa4c5ba8569e3d9a2da9a490d948e5bfd
8952c033a027473cd873d8289df67c96b609adb9b21a40cb939848eac51ff8c8
a4890163aea0c355f8cb18654b3b1c3fb13bc12aca08c0c1049e96d06e83eaa3
5f62c3d49005b4614a49b1ebfda1ff4b62ad9d3dac47689f3834a44a719fc1e7
859732ddad2c37a70b8dc2ec11fe95a9f5b28f1d6e68d64eb6cac6513643ecc4
0dbdf5627f39ad33a893a62cceaf23084d7a2b17a8e594589b9a6817e89ba1bc
```

The V3 input binding records execution commit `02700c78afb74225c0e3a4b09e06bb8f7af60df9`
and the exact corrected dependency bytes later committed and pushed by
`dba0322116b5c174bc5a318ea03747f39f0d9a07`. This provenance distinction is explicit: acceptance
depends on exact bytes and repeatability, while the later commit is the durable Git acceptance of
those bytes. The V3 input also records predecessor structural-proposal SHA-256
`6117863D6874B7DA34A81EECADCA68654BBFDE89D1A966299DB20BF3FDCEAD20`;
this documentation-only readiness correction necessarily changes that proposal byte hash without
mutating the already accepted V3 root. A future structural input binding must bind the corrected
proposal's committed hash separately.

## 7. Satisfied V2-to-V3 Rebuild Boundary

Builder version is identity-bearing. The V3 split-session implementation intentionally separates
V3 dataset, segment, source, and coverage identities from V2. A V2 manifest cannot pass the current
structural validator because:

1. `manifest.version` is V2 instead of `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
2. current segment and dataset identities are recomputed with the V3 version constant;
3. current public builder bytes differ from the V2 bytes recorded by the private manifest;
4. current public tests differ from the V2 tests recorded by the private manifest;
5. the accepted split-session contract forbids silently treating identity mutation as compatible
   reconstruction.

The accepted V3 rebuild was required to start from the same immutable bounded derivative sources,
coverage evidence, calendar bytes, and locked configuration. It called the current public builder
exactly once per reconstruction, published under a new private immutable root, and did not overwrite
or relabel the V2 root.

The V3 root was rebuilt from those exact immutable inputs without overwriting V2. Dataset and all
segment identities rebased, while the accepted semantic comparison proved status, reason, source,
coverage, counts, partitions, bars, and manifest semantics equal under the locked comparison
contract. No identity was copied forward. The exact observed V3 values are externally bound in
Section 6 and must be revalidated before any structural call.

## 8. Accepted Committed Dependency Bytes

Any future readiness revision or private execution must stop on drift from these audited artifacts:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `tests/test_gc_dataset_builder.py` | `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878` |
| `analysis/gc_feature_label_builder.py` | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `analysis/gc_structural_seed_evidence.py` | `B799EE739ECE289A57680007D85566645EE1615B0E20F87C99A4278217AE9AAE` |
| `tests/test_gc_structural_seed_evidence.py` | `CFD789AE272B621EC04CC463A5EE506C22B3221A3F18EA6C737999042420958E` |
| `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md` | `75C0D52D58BF2C8168806893FF68B0F567F19401FFA0DABE3EC0DB8A970094E1` |
| `analysis/gc_candidate_evidence_builder.py` | `B0D361A1C0F19AEB6D49627D00599CBDF6E4A06E6F70C10F0A9A2EB467783A68` |
| `tests/test_gc_candidate_evidence_builder.py` | `090668870F4AD4C49AB540D9E64D2E53BD07657D743FAE391C48CF73C5584116` |
| `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md` | `DA7F657FFB2D787E343E37E69571315D97128389F2594F007FEE9BD87574C5EC` |
| `docs/gc_futures_split_session_calendar_change_proposal.md` | `D2B6968527F3A19423B3535FA19AB57C008691CFFFF2B07863D1FC2BC2710923` |
| `docs/gc_futures_split_session_calendar_checkpoint.md` | `730332BD2CE71BA9E6FEB2DD29F9100CD6125300E3563B700734CEE3F2BC6087` |
| `docs/gc_futures_phase_a_pilot_v3_split_session_rebuild_change_proposal.md` | `FEF0D8E96C37B261ACF2B252B59FE7F6ACD9B635E1C9A4656117509DCD73E0AD` |

Hash equality is necessary but not sufficient. Exact public signatures, version constants,
dataclass fields, enum values, deterministic identities, and status semantics must also pass.

## 9. Exact Future Dataset Reconstruction Contract

The future private structural run must reconstruct the accepted V3 runtime
`GCDatasetBuildResult` once through only these public APIs:

- `parse_sierra_chart_gc_export()`;
- `build_gc_futures_dataset()`.

The exact future dataset call remains keyword-only:

```python
build_gc_futures_dataset(
    *,
    exports: tuple[GCSierraChartExport, ...] | None,
    coverage_evidence: tuple[GCSierraChartCoverageEvidence, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry | GCSplitSessionCalendarEntry, ...] | None,
    config: GCDatasetBuildConfig,
) -> GCDatasetBuildResult
```

The exact configuration remains:

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

No JSON-to-dataclass shortcut, pickle, `eval`, private helper, partial equality, filesystem-order
inference, silent sort, repair, or V2 identity carry-forward is allowed.

## 10. Exact Future Structural Public API

Only these committed public operations may be used:

```python
build_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult

validate_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult
```

The exact structural configuration is the frozen `GCStructuralSeedConfig` with public fields
`swing_left_bars=2`, `swing_right_bars=2`, and `break_buffer_ticks=1`. The structural builder and
validator accept that configuration only through their keyword-only public function boundary. The
seed version is `GC-STRUCTURAL-SEED-V1`. No adapter, monkeypatch, subclass, package re-export,
manual identity, or altered configuration is allowed.

## 11. Dataset Admissibility Gate

Before any structural derivation, the rebuilt dataset must independently prove all of the following:

1. status is exactly `GCDatasetBuildStatus.VALID`;
2. the manifest version is exactly `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
3. dataset ID and every segment ID recompute under current public identities;
4. source, coverage, calendar, timezone-data, row, volume, segment, partition, and reason evidence
   exactly match the Section 6 external V3 acceptance binding and all six accepted artifact hashes;
5. development bars, OOS bars, segment count, missing-slot count, and roll dates reconcile to the
   accepted V3 manifest without assuming the old V2 values;
6. OOS bar count is exactly zero;
7. frozen OOS outcomes were not opened or used;
8. no private input or manifest was modified after acceptance.

Any mismatch stops before `build_gc_structural_seed_evidence()` is called.

## 12. Structural Result Admissibility Gate

The private run calls `build_gc_structural_seed_evidence()` exactly once, then calls
`validate_gc_structural_seed_evidence()` exactly once with the same runtime dataset, exact config,
and returned seed.

Only these complete outcomes are admissible for private diagnostic publication:

- `VALID` with non-null canonical seed and reason `STRUCTURAL_EVIDENCE_VALID`;
- `NONE` with non-null dataset-bound canonical empty seed and reason
  `NO_STRUCTURAL_EVIDENCE`.

`INVALID`, `AMBIGUOUS`, or `UNKNOWN`, a null seed, differing build/validation result, exception,
unrecognized reason, nonempty blocking reasons on `VALID` or `NONE`, or partial result is a failed
run. A failed result publishes no accepted structural artifact.

## 13. Segment, Chronology, and No-Look-Ahead Boundary

The structural builder may consume only development-partition bars inside each canonical segment in
the exact supplied segment and bar tuple order. Local bar indices restart within each segment and
must never be flattened into a dataset-global chronology.

No state, lookback, swing, confirmation, displacement, event, or FVG formation crosses a segment
boundary. Validation/OOS bars cannot discover, confirm, retire, enrich, or invalidate development
evidence. A swing is first known at its exact confirmation bar; an event and context link are first
known only at their exact causal closing moment.

No future outcome, candidate, label, return, entry, exit, PnL, strategy choice, or later segment may
influence structural membership or identity.

## 14. Exact Future Private Output Root

After all prerequisites and a separate explicit execution authorization, the only private output
root is reserved as:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`

The `_v3` suffix is mandatory and prevents overwrite or confusion with the earlier reserved but
unused V2-era path. The old absent path remains unused:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence/`

The V3 root must be Git-ignored. No output may be copied into tests, fixtures, tracked docs,
training, model, backtest, integration, or runtime directories.

## 15. Exact Future Output Artifact Set

The future V3 private root may contain only:

1. `input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
2. `structural_seed_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
3. `manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json`;
4. `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
5. `README_NON_PROMOTABLE_ENGINEERING_PILOT.md`.

The structural output references accepted dataset source and calendar hashes; it does not duplicate
raw exports, bounded derivatives, coverage sidecars, calendars, or full dataset manifests. No
external fixture, cache, notebook, image, model prompt, or ad hoc log is allowed in the output root.

## 16. Deterministic Serialization Contract

Machine-readable artifacts use UTF-8 without BOM, LF endings, exactly one terminal newline, and
canonical JSON with lexically sorted object keys, compact separators `(",", ":")`, and
`ensure_ascii=True`. Dataclass tuples serialize as ordered JSON arrays. Dictionaries may not encode
causal order.

Canonical value representations are:

- UTC timestamps: ISO-8601 microseconds with terminal `Z`;
- dates: ISO `YYYY-MM-DD`;
- finite Decimals: canonical fixed text, zero as `0.0`;
- enums: exact `.value`;
- identities: lowercase 64-hex strings;
- artifact SHA-256 values: uppercase 64-hex strings;
- booleans: JSON booleans, never integers or text.

Python `repr`, pickle, object addresses, hostnames, absolute paths, filesystem timestamps, current
clock time, random values, insertion-order accidents, or environment-specific exception text are
forbidden identity inputs. README and validation-report bytes are hashed by the manifest but do not
change the structural seed identity.

## 17. Input-Binding and Manifest Contract

`input_binding_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind at least:

- proposal ID and proposal-file SHA-256;
- exact source commit;
- all Section 8 dependency hashes;
- accepted V3 pilot root purpose, artifact-manifest SHA-256, build-result SHA-256, and artifact-set
  identity;
- V3 dataset ID, builder version, calendar version, timezone-data version, exact dataset config,
  counts, segments, partitions, missing slots, roll dates, reasons, and blocking reasons;
- structural version and exact structural config;
- explicit `frozen_oos_outcome_accessed=false`, `training_allowed=false`,
  `integration_allowed=false`, and `promotion_allowed=false`.

`manifest_NON_PROMOTABLE_ENGINEERING_PILOT.json` must bind the SHA-256 and byte length of each other
artifact, exact build and validation statuses/reasons, seed ID, source-bar digest, ordered member
counts, exact public call counts `1/1`, and an overall deterministic artifact-set identity.

A matching seed ID without matching nested evidence and file hashes is insufficient.

## 18. Atomic Publication and Immutable Failure Handling

All machine-readable bytes are built in a new task-specific temporary directory inside the private
parent, validated there, and moved into the final V3 root only after every gate passes. The final
root must be absent before publication. No file is written incrementally into an accepted root.

On failure:

- the final V3 root remains absent;
- the temporary output is quarantined under a unique nonaccepted name or removed only under the
  exact rollback authority of the future execution task;
- the V2 pilot and any accepted V3 pilot remain immutable;
- no failed artifact is repaired, overwritten, or relabeled successful;
- no downstream operation begins.

Partial structural members are never promoted under a failed final status.

## 19. Repeatability and Prefix Contract

Two independent future runs with identical accepted V3 dataset bytes, committed dependencies,
configuration, and proposal bytes must produce object-equal results and byte-identical machine
artifacts. README and validation report must also be deterministic under the locked evidence set.

The V3 private run is not an append operation to the V2 dataset. V2-to-V3 version mutation requires a
full rebuild and new identities. Structural prefix comparison is eligible only after acceptance of a
separately rebuilt dataset formed by a strictly later complete canonical segment append; same-moment
append, partial segment, historical insertion, source repair, calendar mutation, version mutation,
or reordered evidence is ineligible and requires full revalidation.

Eligible later-segment reconstruction preserves prior foreign structural facts semantically while
dataset-bound digests and seed identities deterministically rebind as specified by the committed
structural contract.

## 20. Independent Validation Evidence

The future private checkpoint must record and independently verify:

- exact accepted V3 dataset identity and all input hashes;
- exact dependency and proposal hashes;
- current runtime tzdata version and `America/New_York` availability;
- exact public API signatures and call counts;
- result and validator object equality;
- status, reasons, blocking reasons, seed ID, source-bar digest, and ordered member counts;
- every public nested foreign identity and source/confirmation moment against the accepted dataset;
- no cross-segment member, no OOS member, no future-dependent member, and no synthetic evidence;
- canonical JSON round-trip without type or ordering loss;
- byte-identical repeat execution;
- exact output scope and Git-ignore evidence;
- unchanged source, tests, other private roots, index, HEAD, and origin/main;
- `PRIVATE_RUN_PERFORMED=true` only after successful publication;
- `CANDIDATE_RUN_PERFORMED=false`, `TRAINING_STARTED=false`,
  `OOS_OUTCOME_ACCESSED=false`, and `INTEGRATION_STARTED=false`.

The report must not claim profitability, model quality, strategy edge, generalization, production
readiness, or trading authority.

## 21. Inline Synthetic Exact 48-Case Future Matrix

The accepted V3 rebuild evidence and future structural private-run tooling/tests must preserve this
exact sequential logical matrix. Parameterization may expand collection without changing the 48
logical cases.

1. Missing accepted V3 pilot root stops before private execution.
2. Existing final structural V3 root stops without overwrite.
3. V2 manifest version is rejected as a V3 runtime dataset.
4. V2 dataset or segment ID carry-forward is rejected.
5. Builder source/test hash drift stops before reconstruction.
6. Structural source/test/checkpoint hash drift stops before reconstruction.
7. Proposal or accepted V3 artifact-manifest/build-result hash drift stops before reconstruction.
8. Malformed, missing, reordered, extra, or duplicate private input file stops.
9. Current public parser reconstructs every bounded export exactly once.
10. Coverage evidence and calendar entries preserve exact accepted tuple order.
11. Exact dataset config and runtime tzdata reconcile.
12. Public dataset builder is called exactly once.
13. Non-`VALID` dataset status blocks structural derivation.
14. Dataset manifest, counts, reasons, ordered segments, and identities match the Section 6 binding.
15. OOS bar count is zero and frozen OOS outcome remains unopened.
16. Structural builder exact keyword-only signature/default is locked.
17. Structural validator exact keyword-only signature/default is locked.
18. Structural builder is called exactly once with exact default config.
19. Structural validator is called exactly once with the same runtime objects.
20. Build/validation status, reasons, blocking reasons, and seed match exactly.
21. `VALID` requires a nonempty canonical seed and exact valid reason.
22. Dataset-bound `NONE` requires a non-null canonical empty seed and exact none reason.
23. `INVALID`, `AMBIGUOUS`, or `UNKNOWN` publishes no accepted output.
24. Exception containment leaves final root absent and upstream evidence unchanged.
25. Development-only segment selection excludes validation/OOS bars.
26. Cross-segment swing lookback or confirmation is rejected.
27. Cross-segment event or FVG formation is rejected.
28. Dealing Range swing identities and confirmation moments reconcile.
29. Equal Liquidity swings mirror Dealing Range swings one-to-one.
30. Structure Event identities, broken swings, provenance, and causal order reconcile.
31. FVG context-link formation moments and bound events reconcile.
32. Opaque displacement IDs are retained without invented foreign proof.
33. Source-bar and segment-evidence digests recompute exactly.
34. Seed identity recomputes from ordered exact nested evidence.
35. Nested tuple order is identity-sensitive and never silently sorted.
36. Determinably malformed later evidence promotes no failing or later group.
37. Immutable strictly prior complete evidence remains unchanged on later failure.
38. Input binding contains every required dependency and dataset field.
39. Structural JSON preserves exact fields, enums, timestamps, Decimals, tuples, and hashes.
40. Manifest binds every output byte length and SHA-256 exactly once.
41. Required/forbidden artifact names and exact five-file scope are exhaustive.
42. Temporary publication is atomic and cannot expose partial final output.
43. Repeat execution is object-equal and machine-byte-identical.
44. Host path, clock, locale, filesystem order, and hash iteration do not affect bytes.
45. V2 root and accepted V3 pilot root remain byte-immutable.
46. Git status, index, HEAD, and origin/main remain unchanged by private execution.
47. Candidate, feature/label, training, OOS, strategy, risk, and integration surfaces remain unused.
48. A passing private structural artifact authorizes only a separate candidate-run readiness audit,
    never automatic downstream execution or promotion.

## 22. Rollback and Quarantine

This documentation task rolls back by deleting only this uncommitted proposal. After commit,
rollback requires a bounded revert commit; history rewriting is forbidden.

The accepted V3 pilot root is immutable. Any separately authorized future reconstruction may roll
back only its new task-specific temporary or output root. A future structural run rolls back only
its new V3 structural root or quarantined temporary output. Neither operation may delete, modify,
or reuse the accepted V2 root, immutable acquisition artifacts, calendar evidence, or any accepted
V3 predecessor.

Private rollback never changes Git-tracked source and never creates a training or integration path.

## 23. Promotion and Immediate Stop Conditions

Structural private execution requires all of the following before a new explicit run authorization:

1. the separate V3 pilot rebuild proposal is independently accepted and committed: satisfied;
2. the V3 pilot rebuild is explicitly authorized, executed, independently audited, and accepted:
   satisfied;
3. the immutable V3 dataset ID, artifact hashes, counts, reasons, ordered segment IDs, and dependency
   hashes are recorded: satisfied by Section 6;
4. this proposal binds those exact accepted V3 values and passes independent re-audit: required by
   this documentation task before commit;
5. the exact private V3 structural output scope remains absent: satisfied at this baseline;
6. source, tests, checkpoint, APIs, timezone runtime, and private-input bytes remain unchanged:
   must be rechecked immediately before execution;
7. explicit private-run authority is granted for only that exact bound evidence: not granted by this
   proposal and remains the sole authorization gate after documentation acceptance.

Stop immediately on V2/V3 identity reuse, dependency drift, private input mutation, manifest
mismatch, runtime tzdata mismatch, non-`VALID` dataset, OOS contact, cross-segment state, silent sort,
identity mismatch, nondeterminism, exception leakage, partial publication, scope expansion, external
fixture, model or language-model access to private data, candidate/feature-label execution, training,
profitability, strategy, risk, execution, integration, stage, commit, or push without exact separate
authority.

There is no automatic promotion path. A successful engineering structural run would prove only
deterministic plumbing against one post-hoc, non-promotable pilot.

## 24. Final Decision and Next Single Task

The exact V3 structural private-run contract is specified and the accepted V3 pilot prerequisite is
satisfied. After this corrected one-file proposal passes independent audit and is committed, present
readiness is `READY_FOR_EXPLICIT_V3_STRUCTURAL_PRIVATE_RUN_AUTHORIZATION`.

The next single task after documentation acceptance is an exact private run limited to:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`

That future task must perform the Section 9 reconstruction and Section 10 structural build/validation
once each, publish only the exact five Section 15 artifacts atomically, independently re-audit them,
and stop. It must not invoke candidate evidence, feature/label generation, training, OOS outcomes,
strategy evaluation, integration, stage, commit, or push.

This proposal itself authorizes only its one-file documentation acceptance workflow. The private run
still requires separate exact execution authority, and the global code freeze remains active.
