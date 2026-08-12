# GC Futures Phase A Corrected Structural and Candidate Private Rerun Proposal

## 1. Decision record

- Proposal ID: `GC-PHASE-A-CORRECTED-EVIDENCE-PRIVATE-RERUN-PROPOSAL-V1`.
- Classification: documentation-only bounded execution authorization.
- Decision: `READY_FOR_EXPLICIT_CORRECTED_PRIVATE_RERUN`.

This record authorizes one corrected structural-seed reconstruction followed by
one Candidate Evidence reconstruction. It creates no training, feature, label,
outcome, model, strategy, execution, integration, or trading authority.

## 2. Reason for the rerun

The accepted V3 structural root predates two independently reproduced and
test-first corrected production defects: structural protected-swing state could
diverge from the public Dealing Range lifecycle, and Inducement could reject an
unclassified canonical pool outside an active range. The old V3 roots remain
historical immutable evidence and cannot be repaired or relabelled.

## 3. Exact tracked correction commits

The correction chain is exact and ordered:

1. `e4ebc30693083f06213eaff38d16495529b84111` — correction decision record;
2. `5b252021bfe2bedbe3c8dc0ae032ed1cd5941890` — Inducement correction;
3. `458366395c61589215009e7ac881e85bc0dbaf5d` — structural correction.

Execution must occur from this proposal's committed descendant with no tracked
working-tree modification.

## 4. Exact correction artifact hashes

| Artifact | SHA-256 |
|---|---|
| `smc/inducement.py` | `57DA49BE7C99DF9385610749446566323865676817FF8C44D8F8D3868C8C633F` |
| `tests/test_inducement.py` | `129B5751BFB00E78AC4B8D4C71811A35AFB2D55EDEB356A668FC098F5201D850` |
| `docs/smc_v2_inducement_checkpoint.md` | `BC828918611DA7F426BE6A9639E17809BA9E1F6F4C330A1B6CFAE1749B4C17E3` |
| `analysis/gc_structural_seed_evidence.py` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| `tests/test_gc_structural_seed_evidence.py` | `26AA31863AD07B71D0480F0789199D7791BD16FA736E6D2A86B060B928509B35` |
| `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md` | `24EE6564BBBE5E4266400B30512381F69A5D4D0A5FA2713224B7D9305AF0A42E` |

## 5. Regression acceptance evidence

The corrected structural suite passes `69` tests and the corrected Inducement
suite passes `164` tests. The final full regression passes `2298` tests with
`-p no:cacheprovider`. The logical matrices remain exactly `48` structural cases
and `48` Inducement cases. Any later failure or hash drift stops execution.

## 6. Immutable accepted dataset input

The only dataset root is:

`private_data/sierra_chart/gc_2026_phase_a_pilot_v3_split_session/`

It must contain exactly its accepted six files, remain byte-immutable, reconstruct
through the public parser and dataset builder, and bind dataset ID
`a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`,
`54` development segments, `7103` development bars, and zero OOS bars.

## 7. Immutable historical structural input

The historical root
`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v3/`
must remain byte-identical. It binds historical seed ID
`e741a230d961cda290f5d20d4fd5a0b4b1bd2cb54795c1d0c009a2e17148e8f0`.
It is comparison evidence only and is not an admissible corrected candidate input.

## 8. Runtime source reconstruction

The harness reads only the three accepted bounded derivative export byte streams,
their three provenance sidecars, and the accepted pilot calendar. It calls the
public Sierra parser exactly three times in `GCG26`, `GCJ26`, `GCM26` order and
the public V3 dataset builder exactly once with the accepted configuration.
Filesystem discovery, sorting, repair, synthetic substitution, pickle, `eval`,
or JSON-to-result shortcuts are forbidden.

## 9. Calendar and timezone binding

The exact calendar is
`private_data/sierra_chart/gc_2026_phase_a_pilot/calendar_20260218_20260330_NON_PROMOTABLE_ENGINEERING_PILOT.json`.
Its SHA-256 is
`F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`.
Runtime tzdata must equal `2026.2`, and `America/New_York` plus `Asia/Tokyo`
must be available. Calendar inference or external network access is forbidden.

## 10. Dataset configuration

The configuration remains instrument `GC`, timeframe `5M`, tick size `0.1`,
source timezone `Asia/Tokyo`, exchange timezone `America/New_York`, initial
contract `GCJ26-COMEX`, initial trade date `2026-02-23`, roll confirmation
sessions `3`, and OOS interval `[2026-03-31, 2026-03-31)`. The empty OOS interval
is identity-bearing and may not be widened.

## 11. Corrected structural reconstruction

The harness calls `build_gc_structural_seed_evidence()` exactly once with
`GCStructuralSeedConfig(swing_left_bars=2, swing_right_bars=2,
break_buffer_ticks=1)`, then calls `validate_gc_structural_seed_evidence()`
exactly once. Build and validation must be object-equal, `VALID`, and reasoned
exactly `STRUCTURAL_EVIDENCE_VALID` before publication.

## 12. Corrected structural output root

The only new structural root is:

`private_data/sierra_chart/gc_2026_phase_a_structural_seed_evidence_v4/`

It must be absent before execution and contain only input binding, structural
artifact, manifest, validation report, and README files named with the existing
`NON_PROMOTABLE_ENGINEERING_PILOT` suffix. The V3 root may not be overwritten.

## 13. Corrected candidate reconstruction

After the V4 structural artifact passes independent reconstruction and byte audit,
the harness calls `build_gc_candidate_evidence()` exactly once with the accepted
dataset, calendar, corrected V4 structural object, and default frozen candidate
configuration. The builder-owned structural validation remains mandatory.

## 14. Candidate analyzer chain

Each complete segment executes Equal Liquidity, Dealing Range, Liquidity Map,
Fair Value Gap, Inducement, and Kill Zone in committed order. All analyzers for
one segment complete atomically before the next. Detector outputs are immutable
references; the candidate builder may not mutate, enrich, or repair them.

## 15. Candidate acceptance gate

Only complete aggregate `VALID` with nonempty candidates or complete aggregate
`NONE` with zero candidates is publishable. All `54` segment results must be
present. `INVALID`, `AMBIGUOUS`, `UNKNOWN`, exception, partial coverage, or an
unrecognized reason publishes no candidate root.

## 16. Corrected candidate output root

The only new candidate root is:

`private_data/sierra_chart/gc_2026_phase_a_candidate_evidence_v4/`

It must be absent before execution and contain only input binding, candidate
artifact, manifest, validation report, and README files named with the existing
`NON_PROMOTABLE_ENGINEERING_PILOT` suffix. Earlier candidate paths remain absent
or immutable and are never reused.

## 17. Atomic publication

Each result is first serialized to a unique temporary sibling directory. All
identity, schema, hash, byte-count, call-count, status, and scope gates are checked
there. Only a fully passing directory is atomically renamed to its final root.
Failure removes or quarantines only the new temporary directory and leaves all
accepted roots unchanged.

## 18. Deterministic serialization

Machine artifacts use UTF-8 without BOM, LF endings, one terminal newline,
sorted JSON object keys, compact separators, and `ensure_ascii=True`. Aware
timestamps normalize to UTC microsecond `Z`, dates to ISO text, finite Decimals
to canonical fixed text, enums to exact values, and identities to lowercase
64-hex. Host paths, wall-clock time, object addresses, locale, randomness, and
filesystem timestamps are forbidden payload inputs.

## 19. Independent audit

After each atomic publication, a separate read-only pass verifies exact file set,
hashes, manifest self-exclusion, artifact-set identity, object/status evidence,
dataset/seed lineage, counts, reasons, blocking reasons, call counts, zero OOS,
and byte immutability of every V3 input. A second reconstruction must be object
equal and its machine-readable bytes must be deterministic before acceptance.

## 20. No-look-ahead boundary

OOS bars and outcomes remain unopened. No future segment, label, return, entry,
exit, PnL, or model output may influence structural or candidate evidence. A
failing group promotes nothing from that group or any later group; only strictly
prior complete evidence may remain.

## 21. Exact scope and freeze

This authorization changes only Git-ignored private V4 output roots after this
single proposal is committed. It authorizes no tracked source/test/checkpoint
change during execution. The three unrelated pre-existing untracked documents
remain untouched. Global code freeze remains active everywhere else.

## 22. Explicit prohibitions

Feature/label generation, training, model loading, local-LLM access, OOS access,
backtesting, strategy selection, risk calculation, execution authority,
integration, package exports, stage, additional commit, and push are forbidden
during the private execution. Raw private evidence may not leave the machine.

## 23. Rollback, promotion, and STOP conditions

Stop before execution on tracked drift, hash mismatch, missing/extra input,
runtime mismatch, nonzero OOS, existing final V4 root, public API drift, or test
failure. Stop without publication on nondeterminism, noncanonical status, partial
history, identity mismatch, or audit failure. Promotion beyond private diagnostic
evidence requires a separate proposal and explicit authorization.

## 24. Bounded conclusion

This record authorizes only a non-overwriting corrected structural V4 private
reconstruction, its independent audit, then a corrected Candidate Evidence V4
private reconstruction and audit. On completion the workflow stops. No training,
feature/label build, OOS use, integration, remote push, or trading action follows.
