# GC Futures Phase A Structural Seed Downstream Causality Correction Proposal

## 1. Decision record

This documentation-only record authorizes one bounded correction to the accepted
GC Phase A structural-seed generator. The correction is required because a
same-direction BOS can observe a newly confirmed opposite-side swing that is
not eligible to replace the active Dealing Range protected swing. Promoting that
ineligible swing as generator state causes a later otherwise canonical CHOCH to
reference a different swing from the public Dealing Range analyzer.

No implementation, private rerun, training, OOS access, integration, stage,
commit, or push is authorized by this record alone.

## 2. Evidence and reproduced defect

An inline synthetic complete-bar sequence reproduces the defect without private
data. The first bullish BOS constructs a range with a protected LOW. A later LOW
is newer but lies outside the active range. A same-direction bullish BOS follows,
then a bearish close breaks both LOW levels. The current generator references
the newer outside-range LOW; `analyze_dealing_ranges()` rejects the sequence with
`reverse CHOCH must reference the protected swing`.

The prior private Candidate Evidence attempt independently exposed the same
class of mismatch. Private observations are supporting evidence only; the
public regression is the normative discriminator.

## 3. Exact implementation scope

Only these paths may change during the later implementation:

- `analysis/gc_structural_seed_evidence.py`
- `tests/test_gc_structural_seed_evidence.py`
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`

No dependency module, analyzer, dataset, fixture, configuration, package export,
runtime, training, execution, or integration path may change.

## 4. Existing public boundary

The public `smc.dealing_range` API is authoritative for active range construction,
same-direction replacement, boundary extension, and reverse-CHOCH protected-swing
validation. The structural generator may emit immutable canonical input evidence
for that analyzer; it may not invent a parallel protected-swing lifecycle.

## 5. Corrected active-state model

Within one canonical segment the generator tracks, at minimum, active direction,
protected swing, construction index, low boundary, and high boundary. This is
private derivation state only. It creates no new public dataclass, identity kind,
payload field, or output collection.

## 6. First BOS construction

For an uninitialized direction, the first eligible BOS continues to select the
latest confirmed required opposite-side swing before the event. That swing is
the protected swing. The construction index is the event index. Boundaries are
derived from the protected swing source through the event bar, inclusive, using
the existing public Dealing Range directional boundary rule.

## 7. Reverse CHOCH construction

For an accepted reverse CHOCH, `broken_swing_id` must equal the current active
protected swing ID. After the CHOCH is accepted atomically, the new direction is
constructed from the latest confirmed required opposite-side swing before the
event, with the same construction and boundary rule as Section 6.

## 8. Same-direction replacement eligibility

For a same-direction BOS, a replacement protected swing is eligible only when it:

- has the direction-required opposite side;
- has source and confirmation strictly after the active construction index;
- is confirmed strictly before the BOS source/effective index; and
- has price strictly inside the active low/high boundaries.

All conditions are mandatory. Newness alone is not replacement eligibility.

## 9. Deterministic replacement selection

Among eligible replacement swings, choose the greatest source index, then the
greatest confirmation index, then the lexically smallest canonical swing ID.
This mirrors the public Dealing Range deterministic selector. Hash order is only
the final duplicate-equivalent tie-break and never replaces chronology.

## 10. Same-direction replacement transition

When an eligible replacement exists, the same-direction BOS constructs a new
active range atomically: the selected replacement becomes protected, the event
index becomes the construction index, and boundaries are recomputed from the
replacement source through the event bar. No intermediate state may be emitted.

## 11. Same-direction boundary extension

When no eligible replacement exists, the protected swing and construction index
remain unchanged. Bullish continuation may extend only the high boundary;
bearish continuation may extend only the low boundary, using the complete closed
interval from the active protected source through the event bar. The opposite
protected boundary is immutable.

## 12. Outside-range swing rule

A newer required-side swing at or outside either active boundary is not a
replacement. It remains valid canonical swing evidence but cannot change active
protected state. Later CHOCH selection therefore continues to reference the
previous protected swing until a qualifying replacement or reversal occurs.

## 13. Event selection invariance

Existing first-BOS and same-direction crossed-level selection, exact one-tick
close-break semantics, atomic crossed-swing retirement, protected-only reversal
eligibility, and protected precedence within a multi-cross reversal group remain
unchanged.

## 14. FVG linkage invariance

Existing FVG detection, displacement identity, source sequence, event binding,
formation moment, and no-retroactivity rules remain unchanged. A structural
event is linked only after the complete corrected active-state group reconciles.

## 15. Identity invariance

No public identity schema or payload changes. Swing, EVENT, DISPLACEMENT, FVG
context-link, and structural-seed identities continue to use their accepted
builders and normalized values. Corrected event references may deterministically
change later derived artifact hashes; that is expected evidence, not schema drift.

## 16. Status and fail-closed behavior

Existing precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
Malformed or contradictory evidence remains fail-closed. Missing required
two-sided context remains subject to the accepted pre-eligibility/UNKNOWN
boundary. The correction may not turn malformed evidence into a candidate.

## 17. Atomic promotion and prior evidence

Protected state, boundaries, event, retirement, and optional FVG link for one
complete moment promote atomically. A failing group promotes nothing. Strictly
prior valid evidence remains immutable under the existing result contract.

## 18. Segment isolation and prefix invariance

All corrected state is segment-local and resets at each canonical segment
boundary. Complete valid prefixes extended only by strictly later complete
groups remain byte-for-byte invariant. Same-effective append, historical
insertion, reordering, or repair is not an eligible prefix comparison.

## 19. Public API invariance

The exact keyword-only public builder/analyzer signatures, frozen dataclasses,
enum values, constants, exports, and result shapes remain unchanged. No new
configuration option or compatibility mode is permitted.

## 20. Exact 48-case reconciliation

The logical matrix remains exactly 48 numbered cases. Case 48 is extended with
the inline synthetic discriminator from Section 2 and must prove:

- the outside-range newer LOW remains non-replacement;
- the later CHOCH references the original protected LOW;
- the emitted public tuples are accepted by `analyze_dealing_ranges()`; and
- bullish/bearish or qualifying-replacement mirrors may be parameterized without
  increasing the logical case count.

All existing 48-case assertions remain mandatory.

## 21. Test-first implementation gate

The new public downstream-compatibility assertion must fail against the current
source before correction. The minimal source correction follows only after that
RED evidence. Focused and full regression suites must run with
`-p no:cacheprovider`, and the checkpoint must record exact totals, timings,
hashes, bytes, lines, correction evidence, and exact scope.

## 22. Immutable private rerun boundary

Accepted prior dataset and structural/candidate roots are immutable. A corrected
structural rerun, if later separately authorized after code acceptance, must use
a new versioned private output root and bind exact source/config/dataset hashes.
A candidate rerun must likewise use a new root and bind the corrected structural
seed. Overwrite, repair-in-place, partial publication, or stale-proposal reuse is
forbidden.

## 23. Rollback, promotion, and STOP conditions

Before commit, rollback is removal of only the bounded new changes. After commit,
rollback requires an explicit revert commit; history rewriting is forbidden.
Promotion stops on scope drift, dependency drift, test failure, nondeterminism,
public API/schema change, private-root mutation, non-canonical downstream status,
or incomplete audit evidence.

Training, feature/label build, OOS access, execution authority, integration,
remote push, and any dataset promotion remain forbidden.

## 24. Bounded conclusion

The accepted correction is narrow: structural generator state must mirror public
Dealing Range construction, replacement, and extension semantics. The next
single task after independent acceptance of this record is the exact three-path
test-first implementation in Section 3. No other task is implied.
