"""Offline, reference-only GC cross-segment candidate-resolution diagnostics.

The resolver does not create candidate evidence and has no training, strategy,
risk, execution, storage, network, or integration authority.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import re

from analysis.gc_cross_segment_continuity import (
    GCCrossSegmentBoundary,
    GCCrossSegmentContinuityDecision,
    GCCrossSegmentContinuityIdentityKind,
    GCCrossSegmentContinuityManifest,
    GCCrossSegmentContinuityResult,
    GCContinuityDependencyReference,
    GCContinuityReceivingGroup,
    GCContinuityReceivingReference,
    make_gc_cross_segment_continuity_id,
)
from smc.dealing_range import (
    DealingRangeEventType,
    DealingRangeStructureEvent,
)
from smc.fair_value_gap import (
    FairValueGap,
    FairValueGapSnapshot,
    FairValueGapState,
    FairValueGapTransition,
    make_fair_value_gap_id,
)
from smc.inducement import (
    InducementObservation,
    InducementPendingHorizon,
    InducementPendingHorizonResult,
    make_inducement_pending_horizon_id,
)
from smc.smc_v2_primitives import (
    SMCV2Direction,
    SMCV2PrimitiveStatus,
    SMCV2TickRange,
    normalize_utc_timestamp,
)


GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION = (
    "GC-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1"
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_PENDING_REASON = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
_PENDING_HUMAN_REASON = "one or more confirmation horizons are incomplete"
_RESOLUTION_REASON = "NEXT_THREE_CLOSED_BARS_CONFIRMED_ACROSS_ADJACENT_SEGMENT"
_VALID_REASON = "CROSS_SEGMENT_CONFIRMATION_RESOLVED"
_NONE_REASON = "NO_APPLICABLE_CROSS_SEGMENT_HORIZON"
_UNKNOWN_REASON = "CROSS_SEGMENT_CONFIRMATION_UNRESOLVED"
_AMBIGUOUS_REASON = "OPPOSING_CROSS_SEGMENT_CONFIRMATIONS"
_INVALID_REASON = "INVALID_CROSS_SEGMENT_RESOLVER_EVIDENCE"
_CONTINUITY_REASON = "CANONICAL_CONTROL_UNKNOWN"
_FORMATION_REASON = "FORMATION_CONFIRMED"


class GCCrossSegmentCandidateResolverIdentityKind(str, Enum):
    RESOLUTION = "RESOLUTION"
    MANIFEST = "MANIFEST"


@dataclass(frozen=True)
class GCSegmentPendingHorizonEvidence:
    segment_ordinal: int
    segment_id: str
    result: InducementPendingHorizonResult


@dataclass(frozen=True)
class GCSegmentReceivingGroupEvidence:
    segment_ordinal: int
    segment_id: str
    receiving_group_id: str
    observations: tuple[InducementObservation, ...]
    structure_event: DealingRangeStructureEvent
    fair_value_gap: FairValueGap
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...] = ()
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] = ()


@dataclass(frozen=True)
class GCCrossSegmentCandidateResolution:
    resolution_id: str
    boundary_id: str
    receiving_group_id: str
    pending_horizon_id: str
    direction: SMCV2Direction
    contract: str
    source_segment_ordinal: int
    source_segment_id: str
    receiving_segment_ordinal: int
    receiving_segment_id: str
    structure_event_id: str
    fair_value_gap_id: str
    sweep_index: int
    sweep_timestamp: datetime
    confirmation_index: int
    confirmation_timestamp: datetime
    first_known_index: int
    first_known_timestamp: datetime
    source_reference_ids: tuple[str, ...]
    receiving_reference_ids: tuple[str, ...]
    reason_token: str


@dataclass(frozen=True)
class GCCrossSegmentCandidateResolverManifest:
    manifest_id: str
    version: str
    instrument: str
    timeframe: str
    dataset_id: str
    calendar_version: str
    boundary_calendar_digest: str
    candidate_calendar_digest: str
    timezone_data_version: str
    seed_id: str
    canonical_control_digest: str
    continuity_manifest_id: str
    resolution_ids: tuple[str, ...]


@dataclass(frozen=True)
class GCCrossSegmentCandidateResolverResult:
    status: SMCV2PrimitiveStatus
    resolutions: tuple[GCCrossSegmentCandidateResolution, ...] = ()
    manifest: GCCrossSegmentCandidateResolverManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


def _text(value: object, name: str, *, upper: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized.upper() if upper else normalized


def _hash(value: object, name: str) -> str:
    normalized = _text(value, name)
    if _HASH.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return normalized


def _integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _timestamp(value: object, name: str) -> datetime:
    try:
        return normalize_utc_timestamp(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError(f"malformed {name}") from exc


def _hash_tuple(value: object, name: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    if nonempty and not value:
        raise ValueError(f"{name} cannot be empty")
    output = tuple(_hash(item, f"{name} member") for item in value)
    if len(set(output)) != len(output):
        raise ValueError(f"{name} cannot contain duplicates")
    return output


def _integer_tuple(value: object, name: str) -> tuple[int, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    output = tuple(_integer(item, f"{name} member") for item in value)
    if any(left >= right for left, right in zip(output, output[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return output


def _timestamp_tuple(value: object, name: str) -> tuple[datetime, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    output = tuple(_timestamp(item, f"{name} member") for item in value)
    if any(left >= right for left, right in zip(output, output[1:])):
        raise ValueError(f"{name} must be strictly increasing")
    return output


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TypeError("Decimal values must be finite")
    if value.is_zero():
        return "0.0"
    output = format(value, "f")
    if "." in output:
        output = output.rstrip("0").rstrip(".")
    return output if "." in output else output + ".0"


def _canonical(value: object) -> object:
    if isinstance(value, datetime):
        return _timestamp(value, "timestamp").isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, Decimal):
        return _decimal_text(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("canonical keys must be strings")
        return {key: _canonical(item) for key, item in value.items()}
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def _sha(value: object) -> str:
    encoded = json.dumps(
        _canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _forbidden(value: object, default: object, name: str) -> None:
    if value != default:
        raise ValueError(f"{name} is forbidden for this identity kind")


def make_gc_cross_segment_candidate_resolver_id(
    *,
    identity_kind: GCCrossSegmentCandidateResolverIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    boundary_calendar_digest: str,
    candidate_calendar_digest: str,
    timezone_data_version: str,
    seed_id: str,
    canonical_control_digest: str,
    continuity_manifest_id: str,
    boundary_id: str | None = None,
    receiving_group_id: str | None = None,
    pending_horizon_id: str | None = None,
    direction: SMCV2Direction | None = None,
    contract: str | None = None,
    source_segment_ordinal: int | None = None,
    source_segment_id: str | None = None,
    receiving_segment_ordinal: int | None = None,
    receiving_segment_id: str | None = None,
    structure_event_id: str | None = None,
    fair_value_gap_id: str | None = None,
    sweep_index: int | None = None,
    sweep_timestamp: datetime | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    source_reference_ids: tuple[str, ...] = (),
    receiving_reference_ids: tuple[str, ...] = (),
    reason_token: str | None = None,
    resolution_ids: tuple[str, ...] = (),
) -> str:
    """Return one deterministic resolver identity."""

    try:
        if type(identity_kind) is not GCCrossSegmentCandidateResolverIdentityKind:
            raise TypeError(
                "identity_kind must be GCCrossSegmentCandidateResolverIdentityKind"
            )
        common: dict[str, object] = {
            "version": GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION,
            "identity_kind": identity_kind.value,
            "instrument": _text(instrument, "instrument", upper=True),
            "timeframe": _text(timeframe, "timeframe", upper=True),
            "dataset_id": _hash(dataset_id, "dataset_id"),
            "calendar_version": _text(calendar_version, "calendar_version"),
            "boundary_calendar_digest": _hash(
                boundary_calendar_digest, "boundary_calendar_digest"
            ),
            "candidate_calendar_digest": _hash(
                candidate_calendar_digest, "candidate_calendar_digest"
            ),
            "timezone_data_version": _text(
                timezone_data_version, "timezone_data_version"
            ),
            "seed_id": _hash(seed_id, "seed_id"),
            "canonical_control_digest": _hash(
                canonical_control_digest, "canonical_control_digest"
            ),
            "continuity_manifest_id": _hash(
                continuity_manifest_id, "continuity_manifest_id"
            ),
        }
        resolution_fields = (
            ("boundary_id", boundary_id),
            ("receiving_group_id", receiving_group_id),
            ("pending_horizon_id", pending_horizon_id),
            ("direction", direction),
            ("contract", contract),
            ("source_segment_ordinal", source_segment_ordinal),
            ("source_segment_id", source_segment_id),
            ("receiving_segment_ordinal", receiving_segment_ordinal),
            ("receiving_segment_id", receiving_segment_id),
            ("structure_event_id", structure_event_id),
            ("fair_value_gap_id", fair_value_gap_id),
            ("sweep_index", sweep_index),
            ("sweep_timestamp", sweep_timestamp),
            ("confirmation_index", confirmation_index),
            ("confirmation_timestamp", confirmation_timestamp),
            ("first_known_index", first_known_index),
            ("first_known_timestamp", first_known_timestamp),
            ("source_reference_ids", source_reference_ids),
            ("receiving_reference_ids", receiving_reference_ids),
            ("reason_token", reason_token),
        )
        if identity_kind is GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION:
            _forbidden(resolution_ids, (), "resolution_ids")
            if type(direction) is not SMCV2Direction or direction not in {
                SMCV2Direction.BULLISH,
                SMCV2Direction.BEARISH,
            }:
                raise TypeError("direction must be a directional SMCV2Direction")
            payload = {
                **common,
                "boundary_id": _hash(boundary_id, "boundary_id"),
                "receiving_group_id": _hash(
                    receiving_group_id, "receiving_group_id"
                ),
                "pending_horizon_id": _hash(
                    pending_horizon_id, "pending_horizon_id"
                ),
                "direction": direction.value,
                "contract": _text(contract, "contract", upper=True),
                "source_segment_ordinal": _integer(
                    source_segment_ordinal, "source_segment_ordinal"
                ),
                "source_segment_id": _hash(source_segment_id, "source_segment_id"),
                "receiving_segment_ordinal": _integer(
                    receiving_segment_ordinal, "receiving_segment_ordinal"
                ),
                "receiving_segment_id": _hash(
                    receiving_segment_id, "receiving_segment_id"
                ),
                "structure_event_id": _hash(structure_event_id, "structure_event_id"),
                "fair_value_gap_id": _hash(fair_value_gap_id, "fair_value_gap_id"),
                "sweep_index": _integer(sweep_index, "sweep_index"),
                "sweep_timestamp": _timestamp(sweep_timestamp, "sweep_timestamp"),
                "confirmation_index": _integer(
                    confirmation_index, "confirmation_index"
                ),
                "confirmation_timestamp": _timestamp(
                    confirmation_timestamp, "confirmation_timestamp"
                ),
                "first_known_index": _integer(first_known_index, "first_known_index"),
                "first_known_timestamp": _timestamp(
                    first_known_timestamp, "first_known_timestamp"
                ),
                "source_reference_ids": _hash_tuple(
                    source_reference_ids, "source_reference_ids"
                ),
                "receiving_reference_ids": _hash_tuple(
                    receiving_reference_ids, "receiving_reference_ids", nonempty=True
                ),
                "reason_token": _text(reason_token, "reason_token", upper=True),
            }
            if payload["receiving_segment_ordinal"] != payload["source_segment_ordinal"] + 1:  # type: ignore[operator]
                raise ValueError("resolution segments must be adjacent")
            if payload["reason_token"] != _RESOLUTION_REASON:
                raise ValueError("unknown resolution reason token")
        else:
            for name, value in resolution_fields:
                _forbidden(value, () if name.endswith("_ids") else None, name)
            payload = {
                **common,
                "resolution_ids": _hash_tuple(
                    resolution_ids, "resolution_ids", nonempty=True
                ),
            }
        return _sha(payload)
    except (TypeError, ValueError):
        raise
    except Exception as exc:  # pragma: no cover - containment boundary
        raise ValueError("malformed resolver identity evidence") from exc


def _result(
    status: SMCV2PrimitiveStatus,
    reason: str,
    resolutions: tuple[GCCrossSegmentCandidateResolution, ...] = (),
    manifest: GCCrossSegmentCandidateResolverManifest | None = None,
) -> GCCrossSegmentCandidateResolverResult:
    blocking = (reason,) if status in {
        SMCV2PrimitiveStatus.INVALID,
        SMCV2PrimitiveStatus.AMBIGUOUS,
        SMCV2PrimitiveStatus.UNKNOWN,
    } else ()
    return GCCrossSegmentCandidateResolverResult(
        status, resolutions, manifest, (reason,), blocking
    )


def _common(manifest: GCCrossSegmentContinuityManifest) -> dict[str, object]:
    return {
        "instrument": manifest.instrument,
        "timeframe": manifest.timeframe,
        "dataset_id": manifest.dataset_id,
        "calendar_version": manifest.calendar_version,
        "boundary_calendar_digest": manifest.boundary_calendar_digest,
        "candidate_calendar_digest": manifest.candidate_calendar_digest,
        "timezone_data_version": manifest.timezone_data_version,
        "seed_id": manifest.seed_id,
        "canonical_control_digest": manifest.canonical_control_digest,
    }


def _validate_dependency(value: object) -> GCContinuityDependencyReference:
    if type(value) is not GCContinuityDependencyReference:
        raise TypeError("dependency reference has an invalid type")
    _text(value.detector_name, "detector_name", upper=True)
    _text(value.object_kind, "object_kind", upper=True)
    _hash(value.object_id, "object_id")
    _integer(value.owning_segment_ordinal, "owning_segment_ordinal")
    _hash(value.owning_segment_id, "owning_segment_id")
    first = (
        _integer(value.first_known_index, "first_known_index"),
        _timestamp(value.first_known_timestamp, "first_known_timestamp"),
    )
    effective = (
        _integer(value.effective_index, "effective_index"),
        _timestamp(value.effective_timestamp, "effective_timestamp"),
    )
    if effective < first:
        raise ValueError("effective moment precedes first-known moment")
    _text(value.state, "state", upper=True)
    _hash_tuple(value.history_ids, "history_ids")
    _hash(value.source_moment_digest, "source_moment_digest")
    _hash(value.object_digest, "object_digest")
    return value


def _validate_receiving_reference(value: object) -> GCContinuityReceivingReference:
    if type(value) is not GCContinuityReceivingReference:
        raise TypeError("receiving reference has an invalid type")
    detector = _text(value.detector_name, "detector_name", upper=True)
    kind = _text(value.object_kind, "object_kind", upper=True)
    if (detector, kind) not in {
        ("DEALING_RANGE", "STRUCTURE_EVENT"),
        ("FAIR_VALUE_GAP", "GAP"),
    }:
        raise ValueError("receiving reference kind is invalid")
    _hash(value.object_id, "object_id")
    _integer(value.owning_segment_ordinal, "owning_segment_ordinal")
    _hash(value.owning_segment_id, "owning_segment_id")
    first = (
        _integer(value.first_known_index, "first_known_index"),
        _timestamp(value.first_known_timestamp, "first_known_timestamp"),
    )
    effective = (
        _integer(value.effective_index, "effective_index"),
        _timestamp(value.effective_timestamp, "effective_timestamp"),
    )
    if effective < first:
        raise ValueError("effective moment precedes first-known moment")
    _text(value.semantic_discriminator, "semantic_discriminator", upper=True)
    _hash_tuple(value.history_ids, "history_ids")
    _hash(value.source_moment_digest, "source_moment_digest")
    _hash(value.object_digest, "object_digest")
    return value


def _validate_continuity(
    value: object, instrument: str, timeframe: str
) -> tuple[
    GCCrossSegmentContinuityResult,
    GCCrossSegmentContinuityManifest,
    dict[str, GCCrossSegmentBoundary],
    dict[str, GCContinuityReceivingGroup],
]:
    if type(value) is not GCCrossSegmentContinuityResult:
        raise TypeError("continuity_result has an invalid type")
    if value.status is not SMCV2PrimitiveStatus.UNKNOWN:
        raise ValueError("continuity result is outside the preserved UNKNOWN branch")
    if value.reasons != (_CONTINUITY_REASON,) or value.blocking_reasons != (
        _CONTINUITY_REASON,
    ):
        raise ValueError("continuity reasons do not identify the preserved branch")
    if type(value.boundaries) is not tuple or type(value.receiving_groups) is not tuple:
        raise TypeError("continuity collections must be tuples")
    if type(value.manifest) is not GCCrossSegmentContinuityManifest:
        raise TypeError("continuity manifest is required")
    manifest = value.manifest
    if manifest.version != "GC-CROSS-SEGMENT-CONTINUITY-V1":
        raise ValueError("continuity version mismatch")
    if _text(manifest.instrument, "manifest instrument", upper=True) != instrument:
        raise ValueError("instrument mismatch")
    if _text(manifest.timeframe, "manifest timeframe", upper=True) != timeframe:
        raise ValueError("timeframe mismatch")
    _hash(manifest.dataset_id, "dataset_id")
    _text(manifest.calendar_version, "calendar_version")
    _hash(manifest.boundary_calendar_digest, "boundary_calendar_digest")
    _hash(manifest.candidate_calendar_digest, "candidate_calendar_digest")
    _text(manifest.timezone_data_version, "timezone_data_version")
    _hash(manifest.seed_id, "seed_id")
    _hash(manifest.canonical_control_digest, "canonical_control_digest")
    if type(manifest.boundary_ids) is not tuple or type(manifest.receiving_group_ids) is not tuple:
        raise TypeError("continuity manifest lists must be tuples")
    if manifest.boundary_ids != tuple(item.boundary_id for item in value.boundaries):
        raise ValueError("boundary manifest list mismatch")
    if manifest.receiving_group_ids != tuple(
        item.group_id for item in value.receiving_groups
    ):
        raise ValueError("receiving-group manifest list mismatch")
    common = _common(manifest)
    boundary_map: dict[str, GCCrossSegmentBoundary] = {}
    prior_key: tuple[int, datetime, str] | None = None
    for boundary in value.boundaries:
        if type(boundary) is not GCCrossSegmentBoundary:
            raise TypeError("boundary has an invalid type")
        if boundary.receiving_segment_ordinal != boundary.source_segment_ordinal + 1:
            raise ValueError("boundary segments are not adjacent")
        _hash(boundary.source_segment_id, "source_segment_id")
        _hash(boundary.receiving_segment_id, "receiving_segment_id")
        if type(boundary.decision) is not GCCrossSegmentContinuityDecision:
            raise TypeError("boundary decision has an invalid type")
        if type(boundary.reason_tokens) is not tuple or not boundary.reason_tokens:
            raise ValueError("boundary reason_tokens must be nonempty")
        if type(boundary.dependency_references) is not tuple:
            raise TypeError("dependency_references must be a tuple")
        for reference in boundary.dependency_references:
            _validate_dependency(reference)
            if (
                reference.owning_segment_ordinal,
                reference.owning_segment_id,
            ) != (boundary.source_segment_ordinal, boundary.source_segment_id):
                raise ValueError("dependency ownership mismatch")
        # Boundary identities bind an opaque canonical-control *prefix* inside
        # the upstream continuity analyzer.  That prefix digest is deliberately
        # absent from this public result contract, so reconstructing it from the
        # manifest-wide digest would be both incorrect and a layering breach.
        # The upstream ID is therefore an immutable canonical reference here;
        # its shape, uniqueness, ownership, payload and manifest membership are
        # all checked, while the manifest identity itself is recomputed below.
        _hash(boundary.boundary_id, "boundary_id")
        if boundary.boundary_id in boundary_map:
            raise ValueError("duplicate boundary identity")
        key = (
            boundary.source_segment_ordinal,
            _timestamp(boundary.source_end_timestamp, "source_end_timestamp"),
            boundary.boundary_id,
        )
        if prior_key is not None and key <= prior_key:
            raise ValueError("boundaries are not in canonical order")
        prior_key = key
        boundary_map[boundary.boundary_id] = boundary
    group_map: dict[str, GCContinuityReceivingGroup] = {}
    prior_group_key: tuple[int, int, datetime, str] | None = None
    for group in value.receiving_groups:
        if type(group) is not GCContinuityReceivingGroup:
            raise TypeError("receiving group has an invalid type")
        if group.boundary_id not in boundary_map:
            raise ValueError("receiving group references an unknown boundary")
        boundary = boundary_map[group.boundary_id]
        if (group.receiving_segment_ordinal, group.receiving_segment_id) != (
            boundary.receiving_segment_ordinal,
            boundary.receiving_segment_id,
        ):
            raise ValueError("receiving group ownership mismatch")
        if type(group.references) is not tuple or len(group.references) != 2:
            raise ValueError("receiving group must contain exactly two references")
        references = tuple(_validate_receiving_reference(item) for item in group.references)
        if tuple((item.detector_name, item.object_kind) for item in references) != (
            ("DEALING_RANGE", "STRUCTURE_EVENT"),
            ("FAIR_VALUE_GAP", "GAP"),
        ):
            raise ValueError("receiving references are not in canonical order")
        moment = (
            _integer(group.effective_index, "group effective_index"),
            _timestamp(group.effective_timestamp, "group effective_timestamp"),
        )
        for reference in references:
            if (
                reference.owning_segment_ordinal,
                reference.owning_segment_id,
                reference.effective_index,
                _timestamp(reference.effective_timestamp, "reference effective_timestamp"),
            ) != (
                group.receiving_segment_ordinal,
                group.receiving_segment_id,
                moment[0],
                moment[1],
            ):
                raise ValueError("receiving reference does not mirror the group")
        # Receiving-group IDs have the same opaque prefix binding as boundary
        # IDs.  Treat them as upstream canonical references, never as digests
        # that this downstream resolver can reproduce from incomplete inputs.
        _hash(group.group_id, "group_id")
        if group.group_id in group_map:
            raise ValueError("duplicate receiving-group identity")
        key = (group.receiving_segment_ordinal, moment[0], moment[1], group.group_id)
        if prior_group_key is not None and key <= prior_group_key:
            raise ValueError("receiving groups are not in canonical order")
        prior_group_key = key
        group_map[group.group_id] = group
    expected_manifest = make_gc_cross_segment_continuity_id(
        identity_kind=GCCrossSegmentContinuityIdentityKind.MANIFEST,
        **common,
        boundary_ids=manifest.boundary_ids,
        receiving_group_ids=manifest.receiving_group_ids,
    )
    if expected_manifest != manifest.manifest_id:
        raise ValueError("continuity manifest identity mismatch")
    return value, manifest, boundary_map, group_map


def _validate_pending(
    value: object, instrument: str, timeframe: str
) -> tuple[InducementPendingHorizon, ...]:
    if type(value) is not InducementPendingHorizonResult:
        raise TypeError("pending result has an invalid type")
    if value.status is not SMCV2PrimitiveStatus.UNKNOWN:
        raise ValueError("pending result must be UNKNOWN")
    if type(value.pending_horizons) is not tuple:
        raise TypeError("pending_horizons must be a tuple")
    if type(value.reasons) is not tuple or type(value.blocking_reasons) is not tuple:
        raise TypeError("pending result reasons must be tuples")
    if value.reasons != (_PENDING_HUMAN_REASON,):
        raise ValueError("pending result reason mismatch")
    if value.blocking_reasons != (_PENDING_REASON,):
        raise ValueError("pending result blocker mismatch")
    output: list[InducementPendingHorizon] = []
    prior: tuple[datetime, int, str] | None = None
    for pending in value.pending_horizons:
        if type(pending) is not InducementPendingHorizon:
            raise TypeError("pending horizon has an invalid type")
        if type(pending.direction) is not SMCV2Direction or pending.direction not in {
            SMCV2Direction.BULLISH,
            SMCV2Direction.BEARISH,
        }:
            raise ValueError("pending direction must be directional")
        available_indices = _integer_tuple(
            pending.available_confirmation_indices, "available_confirmation_indices"
        )
        available_timestamps = _timestamp_tuple(
            pending.available_confirmation_timestamps,
            "available_confirmation_timestamps",
        )
        if len(available_indices) != len(available_timestamps) or len(available_indices) >= 3:
            raise ValueError("pending available confirmation evidence is invalid")
        if pending.missing_confirmation_bar_count != 3 - len(available_indices):
            raise ValueError("pending missing count mismatch")
        if pending.reason_token != _PENDING_REASON:
            raise ValueError("pending reason token mismatch")
        expected = make_inducement_pending_horizon_id(
            identity_kind="PENDING_HORIZON",
            instrument=instrument,
            timeframe=timeframe,
            direction=pending.direction,
            active_range_lineage_id=pending.active_range_lineage_id,
            active_range_snapshot_id=pending.active_range_snapshot_id,
            liquidity_map_snapshot_id=pending.liquidity_map_snapshot_id,
            external_target_classification_id=pending.external_target_classification_id,
            internal_pool_classification_id=pending.internal_pool_classification_id,
            internal_pool_id=pending.internal_pool_id,
            sweep_index=pending.sweep_index,
            sweep_timestamp=pending.sweep_timestamp,
            sweep_extreme_tick=pending.sweep_extreme_tick,
            reclaim_close_tick=pending.reclaim_close_tick,
            available_confirmation_indices=pending.available_confirmation_indices,
            available_confirmation_timestamps=pending.available_confirmation_timestamps,
            missing_confirmation_bar_count=pending.missing_confirmation_bar_count,
            first_known_index=pending.first_known_index,
            first_known_timestamp=pending.first_known_timestamp,
            reason_token=pending.reason_token,
        )
        if expected != pending.pending_horizon_id:
            raise ValueError("pending horizon identity mismatch")
        key = (
            _timestamp(pending.first_known_timestamp, "first_known_timestamp"),
            _integer(pending.sweep_index, "sweep_index"),
            pending.pending_horizon_id,
        )
        if prior is not None and key <= prior:
            raise ValueError("pending horizons are not in canonical order")
        prior = key
        output.append(pending)
    return tuple(output)


def _observations(value: object) -> tuple[InducementObservation, ...]:
    if type(value) is not tuple or not value:
        raise ValueError("observations must be a nonempty tuple")
    output: list[InducementObservation] = []
    prior: tuple[int, datetime] | None = None
    for observation in value:
        if type(observation) is not InducementObservation:
            raise TypeError("observation has an invalid type")
        index = _integer(observation.index, "observation index")
        timestamp = _timestamp(observation.timestamp, "observation timestamp")
        for name in ("open_tick", "high_tick", "low_tick", "close_tick"):
            if type(getattr(observation, name)) is not int:
                raise TypeError(f"observation {name} must be an integer")
        if type(observation.is_closed) is not bool or not observation.is_closed:
            raise ValueError("observations must be fully closed")
        if not (
            observation.low_tick <= observation.open_tick <= observation.high_tick
            and observation.low_tick <= observation.close_tick <= observation.high_tick
        ):
            raise ValueError("observation OHLC geometry is invalid")
        moment = (index, timestamp)
        if prior is not None and moment <= prior:
            raise ValueError("observations are not strictly chronological")
        prior = moment
        output.append(observation)
    return tuple(output)


def _validate_event_reference(
    event: DealingRangeStructureEvent,
    event_reference: GCContinuityReceivingReference,
    observation_by_moment: dict[tuple[int, datetime], InducementObservation],
) -> None:
    if type(event) is not DealingRangeStructureEvent:
        raise TypeError("structure_event has an invalid type")
    if type(event.direction) is not SMCV2Direction or type(event.event_type) is not DealingRangeEventType:
        raise TypeError("structure event enums are invalid")
    _hash(event.broken_swing_id, "broken_swing_id")
    _hash(event.event_id, "event_id")
    provenance = event.provenance
    source_indices = _integer_tuple(provenance.source_indices, "event source_indices")
    source_timestamps = _timestamp_tuple(
        provenance.source_timestamps, "event source_timestamps"
    )
    if len(source_indices) != len(source_timestamps):
        raise ValueError("event source moments mismatch")
    moments = tuple(zip(source_indices, source_timestamps))
    confirmation = (
        _integer(provenance.confirmation_index, "event confirmation_index"),
        _timestamp(provenance.confirmation_timestamp, "event confirmation_timestamp"),
    )
    if not moments or moments[-1] != confirmation:
        raise ValueError("event sequence must end at confirmation")
    if any(moment not in observation_by_moment for moment in moments):
        raise ValueError("event source moment is absent from observations")
    if (
        event_reference.object_id != event.event_id
        or event_reference.object_digest != _sha(event)
    ):
        raise ValueError("structure event does not match its continuity reference")


def _validate_receiving(
    wrapper: object,
    group: GCContinuityReceivingGroup,
    boundary: GCCrossSegmentBoundary,
    instrument: str,
    timeframe: str,
) -> tuple[
    GCSegmentReceivingGroupEvidence,
    tuple[InducementObservation, ...],
    DealingRangeStructureEvent,
    FairValueGap,
]:
    if type(wrapper) is not GCSegmentReceivingGroupEvidence:
        raise TypeError("receiving wrapper has an invalid type")
    if (
        _integer(wrapper.segment_ordinal, "wrapper segment_ordinal"),
        _hash(wrapper.segment_id, "wrapper segment_id"),
        _hash(wrapper.receiving_group_id, "receiving_group_id"),
    ) != (
        group.receiving_segment_ordinal,
        group.receiving_segment_id,
        group.group_id,
    ):
        raise ValueError("receiving wrapper ownership mismatch")
    observations = _observations(wrapper.observations)
    by_moment = {
        (item.index, _timestamp(item.timestamp, "observation timestamp")): item
        for item in observations
    }
    event_ref, gap_ref = group.references
    event = wrapper.structure_event
    _validate_event_reference(event, event_ref, by_moment)
    gap = wrapper.fair_value_gap
    if type(gap) is not FairValueGap:
        raise TypeError("fair_value_gap has an invalid type")
    if gap.direction is not event.direction:
        raise ValueError("event and gap directions mismatch")
    source_indices = _integer_tuple(gap.source_indices, "gap source_indices")
    source_timestamps = _timestamp_tuple(gap.source_timestamps, "gap source_timestamps")
    if len(source_indices) != 3 or len(source_timestamps) != 3:
        raise ValueError("gap must contain exactly three source moments")
    gap_moments = tuple(zip(source_indices, source_timestamps))
    if any(moment not in by_moment for moment in gap_moments):
        raise ValueError("gap source moment is absent from observations")
    group_moment = (
        group.effective_index,
        _timestamp(group.effective_timestamp, "group effective_timestamp"),
    )
    event_moments = tuple(
        zip(event.provenance.source_indices, event.provenance.source_timestamps)
    )
    event_moments = tuple((index, _timestamp(ts, "event source timestamp")) for index, ts in event_moments)
    if gap_moments[-1] != group_moment or event_moments[-1] != group_moment:
        raise ValueError("receiving sequences do not end at the group moment")
    shorter, longer = sorted((event_moments, gap_moments), key=len)
    if tuple(longer[-len(shorter) :]) != tuple(shorter):
        raise ValueError("event and gap sequences are not positional suffixes")
    if (
        gap.formation_end_index,
        _timestamp(gap.formation_end_timestamp, "formation_end_timestamp"),
    ) != group_moment:
        raise ValueError("gap formation moment mismatch")
    expected_gap_id = make_fair_value_gap_id(
        identity_kind="GAP",
        instrument=instrument,
        timeframe=timeframe,
        direction=gap.direction,
        source_indices=gap.source_indices,
        source_timestamps=gap.source_timestamps,
        boundaries=SMCV2TickRange(gap.lower_tick, gap.upper_tick),
        midpoint_tick=gap.midpoint_tick,
        formation_end_index=gap.formation_end_index,
        formation_end_timestamp=gap.formation_end_timestamp,
        displacement_id=gap.displacement_id,
        structure_event_id=gap.structure_event_id,
        structure_event_type=gap.structure_event_type,
    )
    if expected_gap_id != gap.gap_id or gap.structure_event_id != event.event_id:
        raise ValueError("gap identity or event binding mismatch")
    transitions = wrapper.fair_value_gap_transitions
    snapshots = wrapper.fair_value_gap_snapshots
    if type(transitions) is not tuple or type(snapshots) is not tuple:
        raise TypeError("gap histories must be tuples")
    if not transitions or not snapshots:
        raise ValueError("gap histories must be nonempty")
    prior_transition: tuple[int, datetime] | None = None
    transition_ids: list[str] = []
    transition_by_id: dict[str, FairValueGapTransition] = {}
    current_state: FairValueGapState | None = None
    for transition in transitions:
        if type(transition) is not FairValueGapTransition or transition.gap_id != gap.gap_id:
            raise TypeError("gap transition has an invalid type or owner")
        if type(transition.to_state) is not FairValueGapState:
            raise TypeError("gap transition state is invalid")
        moment = (
            _integer(transition.index, "transition index"),
            _timestamp(transition.timestamp, "transition timestamp"),
        )
        if prior_transition is not None and moment < prior_transition:
            raise ValueError("gap transitions are not nondecreasing")
        if transition.from_state is not current_state:
            raise ValueError("gap transition lifecycle is not causal")
        expected_transition_id = make_fair_value_gap_id(
            identity_kind="TRANSITION",
            instrument=instrument,
            timeframe=timeframe,
            direction=gap.direction,
            gap_id=gap.gap_id,
            from_state=transition.from_state,
            to_state=transition.to_state,
            effective_index=transition.index,
            effective_timestamp=transition.timestamp,
            reason=transition.reason,
        )
        if expected_transition_id != transition.transition_id or transition.transition_id in transition_by_id:
            raise ValueError("gap transition identity mismatch")
        current_state = transition.to_state
        prior_transition = moment
        transition_ids.append(transition.transition_id)
        transition_by_id[transition.transition_id] = transition
    prior_snapshot: tuple[int, datetime] | None = None
    snapshot_ids: list[str] = []
    for snapshot in snapshots:
        if type(snapshot) is not FairValueGapSnapshot or snapshot.gap_id != gap.gap_id:
            raise TypeError("gap snapshot has an invalid type or owner")
        if snapshot.direction is not gap.direction or type(snapshot.state) is not FairValueGapState:
            raise ValueError("gap snapshot semantics mismatch")
        moment = (
            _integer(snapshot.index, "snapshot index"),
            _timestamp(snapshot.timestamp, "snapshot timestamp"),
        )
        if prior_snapshot is not None and moment < prior_snapshot:
            raise ValueError("gap snapshots are not nondecreasing")
        history = _hash_tuple(snapshot.transition_ids, "snapshot transition_ids", nonempty=True)
        if history != tuple(transition_ids[: len(history)]):
            raise ValueError("gap snapshot history does not mirror transitions")
        last_transition = transition_by_id[history[-1]]
        if (
            snapshot.state,
            snapshot.index,
            _timestamp(snapshot.timestamp, "snapshot timestamp"),
        ) != (
            last_transition.to_state,
            last_transition.index,
            _timestamp(last_transition.timestamp, "transition timestamp"),
        ):
            raise ValueError("gap snapshot does not mirror its final transition")
        expected_snapshot_id = make_fair_value_gap_id(
            identity_kind="SNAPSHOT",
            instrument=instrument,
            timeframe=timeframe,
            direction=gap.direction,
            gap_id=gap.gap_id,
            state=snapshot.state,
            effective_index=snapshot.index,
            effective_timestamp=snapshot.timestamp,
            transition_ids=snapshot.transition_ids,
        )
        if expected_snapshot_id != snapshot.snapshot_id or snapshot.snapshot_id in snapshot_ids:
            raise ValueError("gap snapshot identity mismatch")
        prior_snapshot = moment
        snapshot_ids.append(snapshot.snapshot_id)
    if event_ref.object_id != event.event_id or gap_ref.object_id != gap.gap_id:
        raise ValueError("receiving reference IDs mismatch")
    if event_ref.semantic_discriminator != event.event_type.value:
        raise ValueError("structure-event semantic discriminator mismatch")
    if not snapshots or gap_ref.semantic_discriminator != snapshots[-1].state.value:
        raise ValueError("gap semantic discriminator mismatch")
    if gap_ref.history_ids != tuple(transition_ids + snapshot_ids):
        raise ValueError("gap reference history mismatch")
    if transitions[0].from_state is not None or transitions[0].to_state is not FairValueGapState.ACTIVE or transitions[0].reason != _FORMATION_REASON:
        raise ValueError("gap formation history is invalid")
    if prior_transition != group_moment or prior_snapshot != group_moment:
        raise ValueError("gap history is incomplete through group moment")
    return wrapper, observations, event, gap


def _manifest(
    continuity_manifest: GCCrossSegmentContinuityManifest,
    resolutions: tuple[GCCrossSegmentCandidateResolution, ...],
) -> GCCrossSegmentCandidateResolverManifest:
    common = _common(continuity_manifest)
    resolution_ids = tuple(item.resolution_id for item in resolutions)
    manifest_id = make_gc_cross_segment_candidate_resolver_id(
        identity_kind=GCCrossSegmentCandidateResolverIdentityKind.MANIFEST,
        **common,
        continuity_manifest_id=continuity_manifest.manifest_id,
        resolution_ids=resolution_ids,
    )
    return GCCrossSegmentCandidateResolverManifest(
        manifest_id,
        GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION,
        _text(continuity_manifest.instrument, "instrument", upper=True),
        _text(continuity_manifest.timeframe, "timeframe", upper=True),
        continuity_manifest.dataset_id,
        continuity_manifest.calendar_version,
        continuity_manifest.boundary_calendar_digest,
        continuity_manifest.candidate_calendar_digest,
        continuity_manifest.timezone_data_version,
        continuity_manifest.seed_id,
        continuity_manifest.canonical_control_digest,
        continuity_manifest.manifest_id,
        resolution_ids,
    )


def resolve_gc_cross_segment_candidates(
    *,
    instrument: str,
    timeframe: str,
    continuity_result: GCCrossSegmentContinuityResult | None,
    pending_horizon_evidence: tuple[GCSegmentPendingHorizonEvidence, ...] | None,
    receiving_group_evidence: tuple[GCSegmentReceivingGroupEvidence, ...] | None,
) -> GCCrossSegmentCandidateResolverResult:
    """Resolve only the preserved adjacent-segment incomplete-horizon branch."""

    resolutions: list[GCCrossSegmentCandidateResolution] = []
    try:
        normalized_instrument = _text(instrument, "instrument", upper=True)
        normalized_timeframe = _text(timeframe, "timeframe", upper=True)
        continuity: tuple[
            GCCrossSegmentContinuityResult,
            GCCrossSegmentContinuityManifest,
            dict[str, GCCrossSegmentBoundary],
            dict[str, GCContinuityReceivingGroup],
        ] | None = None
        if continuity_result is not None:
            continuity = _validate_continuity(
                continuity_result, normalized_instrument, normalized_timeframe
            )
        pending_wrappers: tuple[GCSegmentPendingHorizonEvidence, ...] | None = None
        if pending_horizon_evidence is not None:
            if type(pending_horizon_evidence) is not tuple:
                raise TypeError("pending_horizon_evidence must be a tuple")
            validated_pending: list[GCSegmentPendingHorizonEvidence] = []
            prior_owner: tuple[int, str] | None = None
            for wrapper in pending_horizon_evidence:
                if type(wrapper) is not GCSegmentPendingHorizonEvidence:
                    raise TypeError("pending wrapper has an invalid type")
                owner = (
                    _integer(wrapper.segment_ordinal, "pending segment_ordinal"),
                    _hash(wrapper.segment_id, "pending segment_id"),
                )
                if prior_owner is not None and owner <= prior_owner:
                    raise ValueError("pending wrappers are not in canonical order")
                prior_owner = owner
                _validate_pending(
                    wrapper.result, normalized_instrument, normalized_timeframe
                )
                validated_pending.append(wrapper)
            pending_wrappers = tuple(validated_pending)
        receiving_wrappers: tuple[GCSegmentReceivingGroupEvidence, ...] | None = None
        if receiving_group_evidence is not None:
            if type(receiving_group_evidence) is not tuple:
                raise TypeError("receiving_group_evidence must be a tuple")
            for wrapper in receiving_group_evidence:
                if type(wrapper) is not GCSegmentReceivingGroupEvidence:
                    raise TypeError("receiving wrapper has an invalid type")
                _integer(wrapper.segment_ordinal, "receiving segment_ordinal")
                _hash(wrapper.segment_id, "receiving segment_id")
                _hash(wrapper.receiving_group_id, "receiving_group_id")
                _observations(wrapper.observations)
            receiving_wrappers = receiving_group_evidence
        if continuity is None or pending_wrappers is None or receiving_wrappers is None:
            return _result(SMCV2PrimitiveStatus.UNKNOWN, _UNKNOWN_REASON)
        _, continuity_manifest, boundary_map, group_map = continuity
        if not pending_wrappers or not any(
            wrapper.result.pending_horizons for wrapper in pending_wrappers
        ):
            return _result(SMCV2PrimitiveStatus.NONE, _NONE_REASON)
        boundary_by_source = {
            (item.source_segment_ordinal, item.source_segment_id): item
            for item in boundary_map.values()
            if item.decision is GCCrossSegmentContinuityDecision.ELIGIBLE
        }
        group_order = {group_id: index for index, group_id in enumerate(continuity_manifest.receiving_group_ids)}
        wrappers_by_group: dict[str, GCSegmentReceivingGroupEvidence] = {}
        prior_group_order = -1
        observations_by_segment: dict[tuple[int, str], tuple[InducementObservation, ...]] = {}
        for wrapper in receiving_wrappers:
            if wrapper.receiving_group_id not in group_map:
                raise ValueError("receiving wrapper references an unknown group")
            order = group_order[wrapper.receiving_group_id]
            if order <= prior_group_order or wrapper.receiving_group_id in wrappers_by_group:
                raise ValueError("receiving wrappers are not in continuity group order")
            prior_group_order = order
            segment_key = (wrapper.segment_ordinal, wrapper.segment_id)
            if segment_key in observations_by_segment and observations_by_segment[segment_key] != wrapper.observations:
                raise ValueError("one receiving segment has divergent observations")
            observations_by_segment[segment_key] = wrapper.observations
            wrappers_by_group[wrapper.receiving_group_id] = wrapper
        unknown = False
        ambiguous = False
        seen_resolution_payloads: dict[str, GCCrossSegmentCandidateResolution] = {}
        for pending_wrapper in pending_wrappers:
            boundary = boundary_by_source.get(
                (pending_wrapper.segment_ordinal, pending_wrapper.segment_id)
            )
            if boundary is None:
                raise ValueError("pending wrapper does not own an eligible boundary")
            source_end = _timestamp(boundary.source_end_timestamp, "source_end_timestamp")
            for pending in pending_wrapper.result.pending_horizons:
                candidates: list[
                    tuple[
                        tuple[int, datetime, int, str, int, datetime, str],
                        InducementPendingHorizon,
                        GCContinuityReceivingGroup,
                        GCSegmentReceivingGroupEvidence,
                        tuple[InducementObservation, ...],
                        DealingRangeStructureEvent,
                        FairValueGap,
                    ]
                ] = []
                if _timestamp(pending.sweep_timestamp, "sweep_timestamp") > source_end or _timestamp(pending.first_known_timestamp, "first_known_timestamp") > source_end:
                    raise ValueError("pending evidence is not known by source-segment end")
                matched_any_group = False
                for group in group_map.values():
                    if group.boundary_id != boundary.boundary_id:
                        continue
                    wrapper = wrappers_by_group.get(group.group_id)
                    if wrapper is None:
                        continue
                    matched_any_group = True
                    try:
                        _, observations, event, gap = _validate_receiving(
                            wrapper,
                            group,
                            boundary,
                            normalized_instrument,
                            normalized_timeframe,
                        )
                    except (TypeError, ValueError):
                        prior = tuple(resolutions)
                        manifest = _manifest(continuity_manifest, prior) if prior else None
                        return _result(SMCV2PrimitiveStatus.INVALID, _INVALID_REASON, prior, manifest)
                    later = tuple(
                        item
                        for item in observations
                        if _timestamp(item.timestamp, "observation timestamp") > source_end
                    )
                    missing = pending.missing_confirmation_bar_count
                    prefix = later[:missing]
                    confirmation_moment = (
                        event.provenance.confirmation_index,
                        _timestamp(
                            event.provenance.confirmation_timestamp,
                            "event confirmation_timestamp",
                        ),
                    )
                    if confirmation_moment not in tuple(
                        (item.index, _timestamp(item.timestamp, "observation timestamp"))
                        for item in prefix
                    ):
                        continue
                    if event.direction is not pending.direction or gap.direction is not pending.direction:
                        continue
                    key = (
                        boundary.source_segment_ordinal,
                        _timestamp(pending.first_known_timestamp, "first_known_timestamp"),
                        pending.sweep_index,
                        pending.pending_horizon_id,
                        group.effective_index,
                        _timestamp(group.effective_timestamp, "group effective_timestamp"),
                        group.group_id,
                    )
                    candidates.append((key, pending, group, wrapper, observations, event, gap))
                if not matched_any_group or not candidates:
                    unknown = True
                    continue
                candidates.sort(key=lambda item: item[0])
                _, selected_pending, group, wrapper, _, event, gap = candidates[0]
                event_ref, gap_ref = group.references
                source_reference_ids = tuple(
                    item.object_id for item in boundary.dependency_references
                )
                receiving_reference_ids = (event_ref.object_id, gap_ref.object_id)
                identity_values: dict[str, object] = {
                    **_common(continuity_manifest),
                    "continuity_manifest_id": continuity_manifest.manifest_id,
                    "boundary_id": boundary.boundary_id,
                    "receiving_group_id": group.group_id,
                    "pending_horizon_id": selected_pending.pending_horizon_id,
                    "direction": selected_pending.direction,
                    "contract": boundary.contract,
                    "source_segment_ordinal": boundary.source_segment_ordinal,
                    "source_segment_id": boundary.source_segment_id,
                    "receiving_segment_ordinal": boundary.receiving_segment_ordinal,
                    "receiving_segment_id": boundary.receiving_segment_id,
                    "structure_event_id": event.event_id,
                    "fair_value_gap_id": gap.gap_id,
                    "sweep_index": selected_pending.sweep_index,
                    "sweep_timestamp": selected_pending.sweep_timestamp,
                    "confirmation_index": event.provenance.confirmation_index,
                    "confirmation_timestamp": event.provenance.confirmation_timestamp,
                    "first_known_index": selected_pending.first_known_index,
                    "first_known_timestamp": selected_pending.first_known_timestamp,
                    "source_reference_ids": source_reference_ids,
                    "receiving_reference_ids": receiving_reference_ids,
                    "reason_token": _RESOLUTION_REASON,
                }
                resolution_id = make_gc_cross_segment_candidate_resolver_id(
                    identity_kind=GCCrossSegmentCandidateResolverIdentityKind.RESOLUTION,
                    **identity_values,
                )
                resolution = GCCrossSegmentCandidateResolution(
                    resolution_id,
                    boundary.boundary_id,
                    group.group_id,
                    selected_pending.pending_horizon_id,
                    selected_pending.direction,
                    _text(boundary.contract, "contract", upper=True),
                    boundary.source_segment_ordinal,
                    boundary.source_segment_id,
                    boundary.receiving_segment_ordinal,
                    boundary.receiving_segment_id,
                    event.event_id,
                    gap.gap_id,
                    selected_pending.sweep_index,
                    _timestamp(selected_pending.sweep_timestamp, "sweep_timestamp"),
                    event.provenance.confirmation_index,
                    _timestamp(event.provenance.confirmation_timestamp, "confirmation_timestamp"),
                    selected_pending.first_known_index,
                    _timestamp(selected_pending.first_known_timestamp, "first_known_timestamp"),
                    source_reference_ids,
                    receiving_reference_ids,
                    _RESOLUTION_REASON,
                )
                existing = seen_resolution_payloads.get(resolution_id)
                if existing is not None and existing != resolution:
                    prior = tuple(resolutions)
                    manifest = _manifest(continuity_manifest, prior) if prior else None
                    return _result(SMCV2PrimitiveStatus.INVALID, _INVALID_REASON, prior, manifest)
                if existing is None:
                    seen_resolution_payloads[resolution_id] = resolution
                    resolutions.append(resolution)
        ordered = tuple(
            sorted(
                resolutions,
                key=lambda item: (
                    item.source_segment_ordinal,
                    _timestamp(item.first_known_timestamp, "first_known_timestamp"),
                    item.sweep_index,
                    item.pending_horizon_id,
                    item.confirmation_index,
                    _timestamp(item.confirmation_timestamp, "confirmation_timestamp"),
                    item.receiving_group_id,
                ),
            )
        )
        moments: dict[tuple[int, datetime], set[SMCV2Direction]] = {}
        for item in ordered:
            moments.setdefault(
                (
                    item.confirmation_index,
                    _timestamp(item.confirmation_timestamp, "confirmation_timestamp"),
                ),
                set(),
            ).add(item.direction)
        ambiguous = any(len(directions) > 1 for directions in moments.values())
        manifest = _manifest(continuity_manifest, ordered) if ordered else None
        if ambiguous:
            return _result(SMCV2PrimitiveStatus.AMBIGUOUS, _AMBIGUOUS_REASON, (), None)
        if unknown:
            return _result(SMCV2PrimitiveStatus.UNKNOWN, _UNKNOWN_REASON, ordered, manifest)
        if ordered:
            return _result(SMCV2PrimitiveStatus.VALID, _VALID_REASON, ordered, manifest)
        return _result(SMCV2PrimitiveStatus.NONE, _NONE_REASON)
    except (TypeError, ValueError):
        return _result(SMCV2PrimitiveStatus.INVALID, _INVALID_REASON, tuple(resolutions))
    except Exception:  # pragma: no cover - public exception-containment boundary
        return _result(SMCV2PrimitiveStatus.INVALID, _INVALID_REASON, tuple(resolutions))


__all__ = [
    "GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION",
    "GCCrossSegmentCandidateResolverIdentityKind",
    "GCSegmentPendingHorizonEvidence",
    "GCSegmentReceivingGroupEvidence",
    "GCCrossSegmentCandidateResolution",
    "GCCrossSegmentCandidateResolverManifest",
    "GCCrossSegmentCandidateResolverResult",
    "make_gc_cross_segment_candidate_resolver_id",
    "resolve_gc_cross_segment_candidates",
]
