# GC Futures Independent Pretraining Contract-Domain Reconciliation Change Proposal

## 1. Proposal record

- Status: `PROPOSED`; documentation-only bounded freeze-lift request.
- Repository baseline: `acb90cd536896b12911fadd0a16295768577528c`.
- Parent remote baseline: local `HEAD` and `origin/main` both equal the repository baseline.
- Purpose: reconcile the deliberately different contract-name domains used by the canonical GC
  dataset/feature evidence and by the immutable pretraining source registry.
- This proposal does not authorize implementation, private execution, corpus promotion, training,
  final-OOS access, integration, staging of implementation files, or push.

## 2. Exact documentation-only scope

This task may create and later stage/commit only:

- `docs/gc_futures_independent_pretraining_contract_domain_reconciliation_change_proposal.md`

The three pre-existing untracked documentation files are user-owned and out of scope. No source,
test, private-data, configuration, package-export, training, execution, or integration file may be
modified by this task.

## 3. Verified governing baseline

The verified dependency artifacts at the proposal baseline are:

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `analysis/gc_dataset_builder.py` | 109,258 | 2,820 | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `tests/test_gc_dataset_builder.py` | 106,345 | 2,934 | `4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971` |
| `analysis/gc_feature_label_builder.py` | 71,477 | 1,287 | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `tests/test_gc_feature_label_builder.py` | 81,401 | 2,011 | `EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B` |
| `analysis/gc_pretraining_corpus.py` | 53,683 | 1,069 | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |
| `tests/test_gc_pretraining_corpus.py` | 14,339 | 342 | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` |
| `docs/gc_futures_independent_pretraining_corpus_checkpoint.md` | 5,316 | 103 | `62020104661C8A5206A98E87D4628886B4009281FF9DDC83819E81B26B7AE58A` |

The governing freeze-lift decision has SHA-256
`556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303`.
The corrected-corpus rebuild proposal has SHA-256
`7E78B185D15323E724A0503E6ADDEC3B05044830EDF65A13A6808653C7EBA641`.

## 4. Confirmed defect and bounded diagnosis

The canonical dataset builder accepts only exchange-qualified contracts matching
`^GC([GJMQVZ])(\d{2})-COMEX$`. Dataset segments and feature rows/labels therefore carry values such
as `GCJ25-COMEX`.

The immutable source registry accepts development contracts only from the unsuffixed source-domain
set `GCJ25`, `GCM25`, `GCQ25`, `GCV25`, and `GCZ25`. The corpus currently compares
`source.contract != row.contract` directly. Consequently, canonical upstream evidence and a
canonical source registry cannot pass the final source-coverage reconciliation even though they
refer to the same delivery month.

This is a contract-domain adapter defect at corpus ingress. It is not evidence that either upstream
domain is malformed, and it does not authorize mutation of either domain.

## 5. Domain ownership boundary

Three domains remain distinct and immutable:

1. Source registry domain: exact unsuffixed delivery-month symbols such as `GCJ25`.
2. Dataset/feature domain: exact exchange-qualified symbols such as `GCJ25-COMEX`.
3. Corpus output domain: the exact upstream row contract, therefore `GCJ25-COMEX`.

The reconciliation adapter is comparison-only. It must not normalize stored objects in place,
rewrite evidence, enrich upstream outputs, or expose a new public representation.

## 6. Exact immutable source-registry contract

For a source record that participates in source-to-row coverage reconciliation,
`GCPretrainingSourceRecord.contract` remains an exact, case-sensitive, unsuffixed source-domain
symbol matching `^GC([GJMQVZ])(\d{2})$`. The accepted development set remains exactly `GCJ25`,
`GCM25`, `GCQ25`, `GCV25`, and `GCZ25`; the closed, sealed-final-OOS, reference-only, and
superseded-reference role rules remain unchanged. This proposal does not add a new global contract
restriction to non-participating reference metadata.

At that comparison boundary an exchange suffix, whitespace, lowercase text, aliases, continuous
contracts, composite symbols, non-string values, or unsupported month/year values are `INVALID`.
No source record, source ID, source SHA-256, role, coverage range, acquisition timestamp, audit
history, or ordering field may be altered.

## 7. Exact immutable upstream contract

Dataset segments, feature rows, and labels continue to require exact exchange-qualified contracts
matching `^GC([GJMQVZ])(\d{2})-COMEX$`. Unsuffixed upstream contracts, other exchanges, aliases,
continuous/composite symbols, whitespace, lowercase text, and malformed values remain `INVALID`.

Dataset, segment, candidate, feature-row, label, and manifest identities remain computed from their
existing raw fields. This proposal does not change `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`, the
feature/label version, or any upstream API or export.

## 8. Private exact comparison-key adapter

The future corpus implementation may add only private, pure helpers equivalent to:

- source key: validate exact unsuffixed source syntax, then append literal `-COMEX`;
- upstream key: validate exact exchange-qualified upstream syntax, then return it unchanged.

Thus `source_key("GCJ25") == upstream_key("GCJ25-COMEX") == "GCJ25-COMEX"`.
Cross-month or cross-year pairs do not compare equal. There is no permissive stripping, case folding,
trimming, substring matching, alias table, or fallback parsing. Helper exceptions must be contained
by the existing fail-closed analyzer boundary.

## 9. Exact reconciliation rule

For every source referenced by a feature row, corpus ingress must require both:

1. `source.first_trade_date <= row.trade_date <= source.last_trade_date`; and
2. exact equality of the validated source comparison key and validated upstream comparison key.

The existing raw `source.contract == row.contract` comparison is replaced only at this boundary.
All source-ID availability, role, dataset-ID, calendar-version, timezone-version, contamination,
independence, and source-coverage checks remain required and retain their current order.

## 10. Fail-closed validation and status precedence

All supplied counterparts are independently validated before a missing-context result. Any
determinable malformed source or upstream contract returns `INVALID_PRETRAINING_CORPUS_EVIDENCE`
without record, partition, or manifest promotion.

The locked final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Genuine unavailable top-level context remains `UNKNOWN / MISSING_TOP_LEVEL_CONTEXT`; an empty but
complete eligible result remains governed by existing `NONE` semantics. The adapter creates no new
status, reason token, or ambiguity branch.

## 11. Deterministic identity non-mutation

The adapter key is validation-only and must never enter an identity payload. The following remain
byte-stable for identical previously valid raw evidence:

- source IDs and source-registry ordering material;
- dataset, segment, candidate, feature-row, and label identities;
- corpus record contract and record identity material;
- partition IDs, corpus ID, manifest ID, and ordered history fields.

`GC_PRETRAINING_CORPUS_VERSION` remains exactly `GC-PRETRAINING-CORPUS-V1`. A version bump or any
identity preimage change is a STOP condition because this correction proves equivalence between two
already-locked representations rather than introducing a new output representation.

## 12. Ordering, duplicates, and no-silent-sort behavior

Source registry canonical order remains
`(role.value, first_trade_date, last_trade_date, contract, source_name, source_id)` using the raw
unsuffixed contract. Candidate, feature-row, label, record, partition, and manifest ordering remain
unchanged.

The implementation must not silently sort any supplied tuple. Equal source IDs/hashes, duplicate or
forked evidence, reordering, historical insertion, or same-effective repair remains fail-closed under
the governing contracts. Hash lexical order is not a causal chronology substitute.

## 13. Candidate, row, and label reconciliation

Candidate, feature row, and label must continue to reconcile exact dataset ID, candidate ID,
delivery-month contract, trade date, effective index/timestamp, lineage, and label horizon. Row and
label contracts remain raw exchange-qualified strings and must be exactly equal to each other.

The source adapter is used only after canonical upstream validation and only for source-to-row
delivery-month equality. It may not weaken candidate/row/label identity or moment reconciliation.

## 14. Multi-contract and roll-boundary invariants

Each row may reconcile only to source records for the same exact delivery month and year. No adapter
may bridge `GCJ25` to `GCM25-COMEX`, infer a nearby contract, or cross a source-domain roll boundary.
Existing chronological partitions, calendar coverage, roll eligibility, purges, embargoes, and
minimum-evidence gates remain immutable.

Multiple valid contracts retain deterministic output order and distinct identities. The correction
does not create, merge, split, or replace any contract segment.

## 15. Atomic processing and immutable prior evidence

Processing remains same-group atomic. A malformed comparison key or mismatch invalidates the
failing group and prevents promotion of that group and all later dependent evidence. Strictly prior
fully reconciled immutable records, partitions, and manifest evidence must be preserved exactly when
the existing chronological-cutoff contract makes their effective boundary determinable.

There is no partial object mutation and no exception leakage.

## 16. Complete-group prefix invariance

Appending a strictly later, complete, valid group must leave all prior record and identity bytes
unchanged. Same-effective appends, historical insertions, reordering, source-registry repairs,
contract-domain mutation, and version mutation are not eligible prefix extensions.

The comparison adapter must be deterministic across repeated runs and independent of locale,
filesystem order, hash iteration order, and process state.

## 17. Final-OOS, training, and authority boundary

The sealed `GCQ26` source remains metadata-only and inaccessible as payload. The adapter does not
authorize final-OOS file opening, hashing beyond already-locked metadata, row generation, corpus
promotion, model fitting, tuning, calibration, inference, order authority, risk authority, or PnL
authority.

No private transaction may be run until a later implementation commit is independently audited,
pushed under separate explicit authorization, and followed by a separate exact private-run approval.

## 18. Exact public API, frozen contracts, and exports

The exact public analyzer remains:

```python
build_gc_pretraining_corpus(
    *,
    dataset_config,
    dataset_calendar_entries,
    dataset_result,
    candidate_result,
    feature_label_result,
    source_registry,
    partition_plan,
)
```

All seven parameters remain keyword-only and required with no defaults. Return type remains
`GCPretrainingCorpusResult`. All public frozen dataclass fields, annotations, defaults, enum values,
constants, and the current 15-name `__all__` tuple remain exact. No public adapter or identity builder
is introduced.

## 19. Reserved future exact three-path implementation scope

A later, separately authorized test-first implementation may modify only:

- `analysis/gc_pretraining_corpus.py`
- `tests/test_gc_pretraining_corpus.py`
- `docs/gc_futures_independent_pretraining_contract_domain_reconciliation_checkpoint.md`

Dataset, feature/label, candidate, calendar, source acquisition, package exports, configuration,
private data, requirements, training, runtime, engine, execution, and integration files remain frozen.
External fixtures are forbidden; tests must use inline synthetic evidence.

## 20. Inline synthetic exact 48-case unit-test matrix

The logical case count is exactly `48`; parameterization may increase collected pytest items without
changing this reconciliation:

1. Exact three-path implementation scope is enforced.
2. Governing dependency hashes and versions reconcile.
3. Analyzer signature retains seven exact keyword-only required parameters.
4. Exact public exports remain unchanged.
5. All public dataclasses retain exact frozen fields, annotations, and defaults.
6. Exact development source-domain `GCJ25` is valid comparison syntax.
7. Development source-domain `GCJ25-COMEX` is `INVALID` at comparison ingress.
8. Exact upstream `GCJ25-COMEX` is valid upstream syntax.
9. Upstream `GCJ25` is `INVALID`.
10. `GCJ25` and `GCJ25-COMEX` reconcile to one exact comparison key.
11. `GCJ25` and `GCM25-COMEX` mismatch is `INVALID`.
12. Year mismatch is `INVALID`.
13. Non-COMEX upstream exchange is `INVALID`.
14. Lowercase and mixed-case variants are `INVALID`.
15. Leading or trailing whitespace is `INVALID`.
16. Continuous and composite symbols are `INVALID`.
17. Non-string and boolean contract values are contained as `INVALID`.
18. Empty contract is `INVALID`.
19. Malformed year width is `INVALID`.
20. Unsupported month code is `INVALID`.
21. Source ID remains byte-stable after comparison.
22. Source registry canonical ordering remains raw-domain and unchanged.
23. Dataset and segment identities remain byte-stable.
24. Feature-row identity remains byte-stable.
25. Label identity remains byte-stable.
26. Record identity retains the raw exchange-qualified row contract.
27. Partition identity schema remains unchanged.
28. Corpus/manifest identity schemas remain unchanged.
29. Source dataset-ID mismatch is `INVALID`.
30. Source date-coverage mismatch is `INVALID`.
31. Multiple delivery months reconcile and emit deterministically.
32. Unsorted supplied evidence is rejected; no silent sort occurs.
33. Exact duplicate source identity/hash is rejected.
34. Forked or contradictory source evidence is `INVALID`.
35. Malformed supplied evidence outranks missing-context `UNKNOWN`.
36. Genuine missing top-level context remains `UNKNOWN`.
37. Final-OOS payload remains sealed and excluded.
38. Final-OOS source metadata retains unsuffixed source-domain contract.
39. Closed, reference-only, and superseded roles remain unchanged.
40. Contamination and independence semantics remain unchanged.
41. Failing group promotes no record, partition, or manifest.
42. Strictly prior determinable immutable evidence is preserved.
43. Strictly-later complete append satisfies prefix invariance.
44. Same-effective append and historical repair are prefix-ineligible.
45. Malformed nested values and adapter exceptions do not leak.
46. No dependency import, API, export, or identity expansion occurs.
47. Focused/full regressions, hashes, byte/line counts, and checkpoint reconcile.
48. Rollback, privacy, freeze, no-run, no-training, no-OOS, no-integration, and STOP conditions reconcile.

## 21. Verification evidence and required commands

The proposal baseline passed:

- focused dataset/feature/corpus suite: `375 passed in 3.62s`;
- full repository `tests/` suite: `2527 passed in 52.88s`.

The unscoped repository-root pytest command also demonstrated why full verification must target
`tests/`: pytest attempted to collect three ACL-protected private-data roots and stopped with three
`PermissionError` collection errors. This was not a source/test failure and accessed no payload.

Future implementation verification must use cache-disabled focused and full `tests/` commands,
record exact totals/timings, artifact hashes, bytes/lines, API/export probes, diff-check, and exact
scope evidence in the reserved checkpoint.

## 22. Rollback conditions

Before staging, rollback means removing only the exact future implementation changes and restoring
the three reserved paths to their pre-task state. No broad reset, checkout, clean, or deletion is
allowed. User-owned tracked/untracked files and all private roots remain untouched.

If implementation cannot preserve public contracts, identities, and upstream artifacts exactly, the
bounded exception is revoked and the global freeze resumes without private execution.

## 23. Promotion and STOP conditions

Promotion requires all 48 logical cases, focused/full regression PASS, exact three-path scope, clean
diff-check, checkpoint/hash consistency, and independent audit PASS. A later local implementation
commit still requires separate push authorization. A pushed implementation still requires a new
read-only post-push audit and an explicit private-run authorization.

STOP immediately for any public API/dataclass/export/version/identity change; dataset or feature
modification; permissive symbol normalization; ambiguous alias; cross-month mapping; OOS payload
access; private-root mutation; unexpected fourth path; regression failure; exception leakage;
training/integration request; or any need to weaken governing evidence.

## 24. Final bounded decision

The exact defect is ready for a later test-first correction solely at corpus ingress. The accepted
design is an exact, private comparison-key adapter that preserves the unsuffixed source-registry
domain, the exchange-qualified upstream/output domain, every public contract, and every identity
preimage. This document authorizes no implementation or execution. Global code freeze remains active
outside a future explicitly approved exact three-path task.
