# Source notes — GC AI Training Readiness

## Reporting job

- Question: Is the GC project ready to start AI training, and what is the
  smallest evidence-safe next direction?
- Audience: technical.
- Scope: committed public contracts and decision records plus private artifact
  presence/manifest metadata only, as of 2026-08-31.
- Excluded: raw private market rows, final-OOS payloads/outcomes, PnL, model
  fitting, private analyzer reruns, and trading activity.
- Decision-useful outcome: training readiness state, blocking gate, and one
  bounded next direction.

## Evidence inventory

1. `docs/gc_futures_independent_pretraining_post_resolver_readiness_decision.md`
   - current project-level reconciliation;
   - SHA-256 `F344B32A9B3B923EC79F4F96519501D93BF00E4F67EDA1012C8F382991366296`.
2. `docs/gc_futures_phase_a_cross_segment_candidate_resolver_terminal_outcome_decision.md`
   - terminal deterministic resolver result;
   - SHA-256 `107DF12717C0AFC60BA89D1721C02A77E1BD2631BB3C19FA5FFBEEF7330EB67D`.
3. `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_closure_decision.md`
   - closes further setup-family search on the accepted development sample;
   - SHA-256 `5166E0D14BAA65A2AAFC8E17BE2E1740EC92AFCFCCC4CCED4B60CFF964E36F75`.
4. `docs/gc_futures_ai_strategy_training_decision.md`
   - long-term authority separation and no-trading boundary.
5. `analysis/gc_pretraining_corpus.py` and
   `tests/test_gc_pretraining_corpus.py`
   - public fail-closed corpus contract and focused regression surface.
6. Private metadata-only checks
   - `gc_independent_pretraining_corpus_v1` absent;
   - terminal resolver root present and immutable;
   - final-OOS contact count remains zero in the accepted decision records.

## Definitions

- Training ready: an accepted immutable feature matrix, target vector,
  TRAIN/VALIDATION/CALIBRATION partitions, purge/embargo evidence,
  preprocessing-fit population, and accepted corpus manifest all exist.
- Candidate ready: one promoted canonical candidate population exists under a
  preregistered hypothesis and immutable point-in-time evidence.
- Acquisition first: freeze a new independent development cohort and its
  calendar/contract/partition metadata before selecting or running another
  setup hypothesis.
- Final OOS: sealed evidence that may not be read, profiled, relabelled, or used
  for rule selection in this report.

## Checks performed

- Repository baseline and local/remote synchronization.
- Decision-record and implementation SHA-256 reconciliation.
- Final corpus root presence.
- Terminal resolver manifest/result status and authority metadata.
- Candidate, feature/label, partition, corpus, training, OOS, integration, and
  trading gate reconciliation.
- Focused pretraining-corpus regression: 66 passed.
- Full public regression: 2674 passed.

## Report spine

- Answer: AI training is not ready and has not started.
- Primary blocker: no promoted candidate population, so feature/label,
  partitions, and corpus do not exist.
- Validation: public implementations are regression-clean; the blocker is
  evidence availability, not a failing builder.
- Recommendation: acquisition-first independent cohort, then one
  preregistered hypothesis; do not rerun or relax closed Phase A/B contracts.

## Visualization decision

A compact gate-state bar chart is used because the ordered break in the
evidence chain is materially easier to see than in prose alone. Its values are
an explicit ordinal encoding—1 complete, 0.5 partial, 0 unavailable—not a
performance metric, probability, trend, or model score. Exact decision tables
remain the authoritative detail.

## Limitations

- Raw rows and outcome distributions were deliberately not profiled.
- The assessment does not estimate edge, sample size for a future model, class
  balance, profitability, or live readiness.
- Acquisition requirements must be fixed in a separate proposal before any
  new private data transaction.
