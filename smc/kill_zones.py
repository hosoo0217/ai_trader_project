"""Deterministic standalone Kill-zone context diagnostics.

This module performs no file, network, configuration, strategy, risk, or
execution integration. Calendar evidence is immutable and caller supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
import hashlib
from importlib import metadata
import json
import re
from zoneinfo import ZoneInfo

from smc.smc_v2_primitives import SMCV2PrimitiveStatus, normalize_utc_timestamp


KILL_ZONE_DETECTOR_VERSION = "SMC-V2-KILL-ZONE-1"
KILL_ZONE_TIMEZONE = "America/New_York"

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY_KINDS = frozenset({"CONTEXT", "SNAPSHOT"})
_MAX_SESSION_DURATION = timedelta(hours=24)


class KillZoneName(str, Enum):
    ASIA = "ASIA"
    LONDON = "LONDON"
    NEW_YORK_AM = "NEW_YORK_AM"
    NEW_YORK_PM = "NEW_YORK_PM"


class KillZoneSessionStatus(str, Enum):
    OPEN = "OPEN"
    EARLY_CLOSE = "EARLY_CLOSE"
    SESSION_CLOSED = "SESSION_CLOSED"


class KillZoneQuality(str, Enum):
    VERIFIED = "VERIFIED"
    CALENDAR_UNVERIFIED = "CALENDAR_UNVERIFIED"


@dataclass(frozen=True)
class KillZoneObservation:
    index: int
    timestamp: datetime
    is_closed: bool


@dataclass(frozen=True)
class KillZoneCalendarEntry:
    calendar_version: str
    trade_date: date
    session_status: KillZoneSessionStatus
    session_open_timestamp: datetime | None
    session_close_timestamp: datetime | None


@dataclass(frozen=True)
class KillZoneContext:
    context_id: str
    observation_index: int
    observation_timestamp: datetime
    trade_date: date
    zone: KillZoneName | None
    session_status: KillZoneSessionStatus | None
    quality: KillZoneQuality
    calendar_version: str
    timezone_name: str
    timezone_data_version: str


@dataclass(frozen=True)
class KillZoneSnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    context_ids: tuple[str, ...]


@dataclass(frozen=True)
class KillZoneResult:
    status: SMCV2PrimitiveStatus
    contexts: tuple[KillZoneContext, ...] = ()
    snapshots: tuple[KillZoneSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _CalendarValidation:
    entries: dict[date, KillZoneCalendarEntry]
    issue_date: date | None
    issue_reason: str | None
    unknowable_issue: bool


def make_kill_zone_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    calendar_version: str,
    timezone_name: str,
    timezone_data_version: str,
    observation_index: int | None = None,
    observation_timestamp: datetime | None = None,
    trade_date: date | None = None,
    zone: KillZoneName | None = None,
    session_status: KillZoneSessionStatus | None = None,
    quality: KillZoneQuality | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    context_ids: tuple[str, ...] = (),
) -> str:
    """Build one canonical kind-specific Kill-zone identity."""

    try:
        return _make_kill_zone_id(
            identity_kind=identity_kind,
            instrument=instrument,
            timeframe=timeframe,
            calendar_version=calendar_version,
            timezone_name=timezone_name,
            timezone_data_version=timezone_data_version,
            observation_index=observation_index,
            observation_timestamp=observation_timestamp,
            trade_date=trade_date,
            zone=zone,
            session_status=session_status,
            quality=quality,
            effective_index=effective_index,
            effective_timestamp=effective_timestamp,
            context_ids=context_ids,
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        raise ValueError("invalid Kill-zone identity evidence") from exc


def _make_kill_zone_id(
    *,
    identity_kind: object,
    instrument: object,
    timeframe: object,
    calendar_version: object,
    timezone_name: object,
    timezone_data_version: object,
    observation_index: object,
    observation_timestamp: object,
    trade_date: object,
    zone: object,
    session_status: object,
    quality: object,
    effective_index: object,
    effective_timestamp: object,
    context_ids: object,
) -> str:
    if type(identity_kind) is not str or identity_kind not in _IDENTITY_KINDS:
        raise ValueError("identity_kind is not a locked Kill-zone identity kind")

    normalized_instrument = _normalize_text(instrument, name="instrument")
    normalized_timeframe = _normalize_text(timeframe, name="timeframe")
    normalized_calendar_version = _normalize_text(
        calendar_version,
        name="calendar_version",
    )
    normalized_timezone_data_version = _normalize_text(
        timezone_data_version,
        name="timezone_data_version",
    )
    if type(timezone_name) is not str or timezone_name != KILL_ZONE_TIMEZONE:
        raise ValueError("timezone_name must be exactly America/New_York")
    runtime_version = _runtime_timezone_data_version()
    if runtime_version is None:
        raise ValueError("runtime timezone-data version is unavailable")
    normalized_runtime_version = _normalize_text(
        runtime_version,
        name="runtime_timezone_data_version",
    )
    if normalized_timezone_data_version != normalized_runtime_version:
        raise ValueError("timezone-data version mismatch")
    timezone_value = _load_timezone()
    if timezone_value is None:
        raise ValueError("America/New_York is unavailable")

    payload: dict[str, object] = {
        "calendar_version": normalized_calendar_version,
        "detector_version": KILL_ZONE_DETECTOR_VERSION,
        "identity_kind": identity_kind,
        "instrument": normalized_instrument,
        "timeframe": normalized_timeframe,
        "timezone_data_version": normalized_timezone_data_version,
        "timezone_name": KILL_ZONE_TIMEZONE,
    }

    if identity_kind == "CONTEXT":
        _validate_non_negative_int(observation_index, name="observation_index")
        normalized_observation = _normalize_timestamp(
            observation_timestamp,
            name="observation_timestamp",
        )
        normalized_trade_date = _validate_date(trade_date, name="trade_date")
        if type(quality) is not KillZoneQuality:
            raise TypeError("quality must be a KillZoneQuality")
        if zone is not None and type(zone) is not KillZoneName:
            raise TypeError("zone must be a KillZoneName or None")
        if session_status is not None and type(session_status) is not KillZoneSessionStatus:
            raise TypeError(
                "session_status must be a KillZoneSessionStatus or None"
            )
        if effective_index is not None or effective_timestamp is not None:
            raise ValueError("CONTEXT forbids snapshot effective parameters")
        if type(context_ids) is not tuple:
            raise TypeError("context_ids must be a tuple")
        if context_ids:
            raise ValueError("CONTEXT forbids non-empty context_ids")
        _validate_context_geometry(
            zone=zone,
            session_status=session_status,
            quality=quality,
        )
        candidate = _candidate_for_timestamp(
            normalized_observation,
            timezone_value=timezone_value,
        )
        if candidate is None:
            raise ValueError("Kill-zone context requires a fixed-window observation")
        candidate_zone, candidate_trade_date = candidate
        if normalized_trade_date != candidate_trade_date:
            raise ValueError("trade_date does not match the observation window")
        if zone is not None and zone is not candidate_zone:
            raise ValueError("zone does not match the observation window")
        payload.update(
            {
                "observation_index": observation_index,
                "observation_timestamp": _timestamp_text(normalized_observation),
                "quality": quality.value,
                "session_status": (
                    None if session_status is None else session_status.value
                ),
                "trade_date": normalized_trade_date.isoformat(),
                "zone": None if zone is None else zone.value,
            }
        )
    else:
        if any(
            value is not None
            for value in (
                observation_index,
                observation_timestamp,
                trade_date,
                zone,
                session_status,
                quality,
            )
        ):
            raise ValueError("SNAPSHOT forbids context parameters")
        _validate_non_negative_int(effective_index, name="effective_index")
        normalized_effective = _normalize_timestamp(
            effective_timestamp,
            name="effective_timestamp",
        )
        normalized_context_ids = _validate_hash_tuple(
            context_ids,
            name="context_ids",
        )
        payload.update(
            {
                "context_ids": list(normalized_context_ids),
                "effective_index": effective_index,
                "effective_timestamp": _timestamp_text(normalized_effective),
            }
        )

    canonical_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def analyze_kill_zones(
    *,
    instrument: str,
    timeframe: str,
    observations: tuple[KillZoneObservation, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
    timezone_data_version: str,
) -> KillZoneResult:
    """Classify immutable fully closed observation moments fail closed."""

    try:
        normalized_instrument = _normalize_text(instrument, name="instrument")
        normalized_timeframe = _normalize_text(timeframe, name="timeframe")
        normalized_calendar_version = _normalize_text(
            calendar_version,
            name="calendar_version",
        )
        normalized_timezone_version = _normalize_text(
            timezone_data_version,
            name="timezone_data_version",
        )
    except Exception as exc:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason=_exception_reason(exc),
        )

    if observations is not None and type(observations) is not tuple:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason="observations must be a tuple or None",
        )
    if calendar_entries is not None and type(calendar_entries) is not tuple:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason="calendar_entries must be a tuple or None",
        )

    try:
        runtime_version = _runtime_timezone_data_version()
    except Exception:
        runtime_version = None
    if runtime_version is None:
        unavailable_issue = _prevalidate_without_timezone(
            observations=observations,
            calendar_entries=calendar_entries,
            calendar_version=normalized_calendar_version,
        )
        if unavailable_issue is not None:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                reason=unavailable_issue,
            )
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            reason="runtime timezone-data version is unavailable",
        )
    try:
        normalized_runtime_version = _normalize_text(
            runtime_version,
            name="runtime_timezone_data_version",
        )
    except Exception:
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            reason="runtime timezone-data version is unavailable",
        )
    if normalized_timezone_version != normalized_runtime_version:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason="timezone-data version mismatch",
        )

    try:
        timezone_value = _load_timezone()
    except Exception:
        timezone_value = None
    if timezone_value is None:
        unavailable_issue = _prevalidate_without_timezone(
            observations=observations,
            calendar_entries=calendar_entries,
            calendar_version=normalized_calendar_version,
        )
        if unavailable_issue is not None:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                reason=unavailable_issue,
            )
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            reason="America/New_York is unavailable",
        )

    if observations is None or calendar_entries is None:
        supplied_issue = _prevalidate_without_timezone(
            observations=observations,
            calendar_entries=calendar_entries,
            calendar_version=normalized_calendar_version,
        )
        if supplied_issue is not None:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                reason=supplied_issue,
            )
        if calendar_entries is not None:
            try:
                supplied_calendar = _validate_calendar_entries(
                    calendar_entries,
                    calendar_version=normalized_calendar_version,
                    timezone_value=timezone_value,
                )
            except Exception as exc:
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    reason=_exception_reason(exc),
                )
            if (
                supplied_calendar.unknowable_issue
                or supplied_calendar.issue_reason is not None
            ):
                return _result(
                    SMCV2PrimitiveStatus.INVALID,
                    reason=(
                        supplied_calendar.issue_reason
                        or "malformed calendar evidence"
                    ),
                )
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            reason="required top-level context is missing",
        )

    try:
        calendar_validation = _validate_calendar_entries(
            calendar_entries,
            calendar_version=normalized_calendar_version,
            timezone_value=timezone_value,
        )
    except Exception as exc:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason=_exception_reason(exc),
        )
    if calendar_validation.unknowable_issue:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            reason=calendar_validation.issue_reason or "malformed calendar evidence",
        )

    contexts: list[KillZoneContext] = []
    snapshots: list[KillZoneSnapshot] = []
    previous_index = -1
    previous_timestamp: datetime | None = None
    missing_calendar = False

    for raw_observation in observations:
        safe_moment = _safe_observation_moment(raw_observation)
        if safe_moment is None:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=(),
                snapshots=(),
                reason="observation effective moment is unknowable",
            )
        index, normalized_timestamp = safe_moment

        if (
            index <= previous_index
            or (
                previous_timestamp is not None
                and normalized_timestamp <= previous_timestamp
            )
        ):
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=tuple(contexts),
                snapshots=tuple(snapshots),
                reason="observation chronology is not strictly increasing",
            )

        try:
            _validate_observation(
                raw_observation,
                expected_index=index,
                expected_timestamp=normalized_timestamp,
            )
        except Exception as exc:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=tuple(contexts),
                snapshots=tuple(snapshots),
                reason=_exception_reason(exc),
            )

        previous_index = index
        previous_timestamp = normalized_timestamp

        try:
            candidate = _candidate_for_timestamp(
                normalized_timestamp,
                timezone_value=timezone_value,
            )
        except Exception as exc:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=tuple(contexts),
                snapshots=tuple(snapshots),
                reason=_exception_reason(exc),
            )
        if candidate is None:
            continue
        candidate_zone, trade_date_value = candidate

        if (
            calendar_validation.issue_date is not None
            and trade_date_value >= calendar_validation.issue_date
        ):
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=tuple(contexts),
                snapshots=tuple(snapshots),
                reason=(
                    calendar_validation.issue_reason
                    or "malformed calendar evidence"
                ),
            )

        try:
            zone, session_status, quality = _classify_candidate(
                candidate_zone=candidate_zone,
                trade_date_value=trade_date_value,
                timestamp=normalized_timestamp,
                entries=calendar_validation.entries,
            )
            context_id = make_kill_zone_id(
                identity_kind="CONTEXT",
                instrument=normalized_instrument,
                timeframe=normalized_timeframe,
                calendar_version=normalized_calendar_version,
                timezone_name=KILL_ZONE_TIMEZONE,
                timezone_data_version=normalized_timezone_version,
                observation_index=index,
                observation_timestamp=normalized_timestamp,
                trade_date=trade_date_value,
                zone=zone,
                session_status=session_status,
                quality=quality,
            )
            context = KillZoneContext(
                context_id=context_id,
                observation_index=index,
                observation_timestamp=normalized_timestamp,
                trade_date=trade_date_value,
                zone=zone,
                session_status=session_status,
                quality=quality,
                calendar_version=normalized_calendar_version,
                timezone_name=KILL_ZONE_TIMEZONE,
                timezone_data_version=normalized_timezone_version,
            )
            next_context_ids = tuple(
                item.context_id for item in (*contexts, context)
            )
            snapshot_id = make_kill_zone_id(
                identity_kind="SNAPSHOT",
                instrument=normalized_instrument,
                timeframe=normalized_timeframe,
                calendar_version=normalized_calendar_version,
                timezone_name=KILL_ZONE_TIMEZONE,
                timezone_data_version=normalized_timezone_version,
                effective_index=index,
                effective_timestamp=normalized_timestamp,
                context_ids=next_context_ids,
            )
            snapshot = KillZoneSnapshot(
                snapshot_id=snapshot_id,
                index=index,
                timestamp=normalized_timestamp,
                context_ids=next_context_ids,
            )
        except Exception as exc:
            return _result(
                SMCV2PrimitiveStatus.INVALID,
                contexts=tuple(contexts),
                snapshots=tuple(snapshots),
                reason=_exception_reason(exc),
            )

        contexts.append(context)
        snapshots.append(snapshot)
        if quality is KillZoneQuality.CALENDAR_UNVERIFIED:
            missing_calendar = True

    if calendar_validation.issue_reason is not None:
        return _result(
            SMCV2PrimitiveStatus.INVALID,
            contexts=tuple(contexts),
            snapshots=tuple(snapshots),
            reason=calendar_validation.issue_reason,
        )
    if missing_calendar:
        return _result(
            SMCV2PrimitiveStatus.UNKNOWN,
            contexts=tuple(contexts),
            snapshots=tuple(snapshots),
            reason="calendar coverage is missing",
        )
    if any(
        context.quality is KillZoneQuality.VERIFIED and context.zone is not None
        for context in contexts
    ):
        return _result(
            SMCV2PrimitiveStatus.VALID,
            contexts=tuple(contexts),
            snapshots=tuple(snapshots),
            reason="verified Kill-zone context exists",
        )
    return _result(
        SMCV2PrimitiveStatus.NONE,
        contexts=tuple(contexts),
        snapshots=tuple(snapshots),
        reason=None,
    )


def _validate_calendar_entries(
    entries: tuple[KillZoneCalendarEntry, ...],
    *,
    calendar_version: str,
    timezone_value: ZoneInfo,
) -> _CalendarValidation:
    validated: dict[date, KillZoneCalendarEntry] = {}
    issue_date: date | None = None
    issue_reason: str | None = None
    unknowable_issue = False
    previous_date: date | None = None

    for raw_entry in entries:
        safe_date = _safe_calendar_date(raw_entry)
        if safe_date is None:
            unknowable_issue = True
            issue_reason = issue_reason or "calendar trade date is unknowable"
            continue

        ordering_invalid = previous_date is not None and safe_date <= previous_date
        if previous_date is None or safe_date > previous_date:
            previous_date = safe_date

        try:
            entry = _validate_calendar_entry(
                raw_entry,
                calendar_version=calendar_version,
                timezone_value=timezone_value,
            )
            if ordering_invalid or safe_date in validated:
                raise ValueError(
                    "calendar entries must be unique and strictly increasing"
                )
            validated[safe_date] = entry
        except Exception as exc:
            if issue_date is None or safe_date < issue_date:
                issue_date = safe_date
                issue_reason = _exception_reason(exc)

    return _CalendarValidation(
        entries=validated,
        issue_date=issue_date,
        issue_reason=issue_reason,
        unknowable_issue=unknowable_issue,
    )


def _validate_calendar_entry(
    value: object,
    *,
    calendar_version: str,
    timezone_value: ZoneInfo | None,
) -> KillZoneCalendarEntry:
    if type(value) is not KillZoneCalendarEntry:
        raise TypeError("calendar entries must be exact KillZoneCalendarEntry values")
    try:
        normalized_version = _normalize_text(
            value.calendar_version,
            name="calendar entry version",
        )
        trade_date_value = _validate_date(value.trade_date, name="trade_date")
        status = value.session_status
        opening = value.session_open_timestamp
        closing = value.session_close_timestamp
    except Exception as exc:
        raise ValueError("malformed calendar entry") from exc

    if normalized_version != calendar_version:
        raise ValueError("calendar entry version mismatch")
    if type(status) is not KillZoneSessionStatus:
        raise TypeError("session_status must be a KillZoneSessionStatus")
    if (
        trade_date_value.weekday() >= 5
        and status is not KillZoneSessionStatus.SESSION_CLOSED
    ):
        raise ValueError("weekend trade dates must be SESSION_CLOSED")

    if status is KillZoneSessionStatus.SESSION_CLOSED:
        if opening is not None or closing is not None:
            raise ValueError("SESSION_CLOSED forbids session timestamps")
        return value

    if opening is None or closing is None:
        raise ValueError("OPEN and EARLY_CLOSE require session timestamps")
    normalized_open = _normalize_timestamp(opening, name="session_open_timestamp")
    normalized_close = _normalize_timestamp(closing, name="session_close_timestamp")
    if normalized_open >= normalized_close:
        raise ValueError("session open must precede session close")
    if normalized_close - normalized_open > _MAX_SESSION_DURATION:
        raise ValueError("session duration cannot exceed 24 hours")

    if timezone_value is not None:
        open_local_date = normalized_open.astimezone(timezone_value).date()
        close_local_date = normalized_close.astimezone(timezone_value).date()
        if open_local_date not in (
            trade_date_value,
            trade_date_value - timedelta(days=1),
        ):
            raise ValueError("session open local date does not reconcile")
        if close_local_date != trade_date_value:
            raise ValueError("session close local date does not reconcile")
    return value


def _prevalidate_without_timezone(
    *,
    observations: tuple[KillZoneObservation, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
) -> str | None:
    if observations is not None:
        previous_index = -1
        previous_timestamp: datetime | None = None
        for value in observations:
            safe_moment = _safe_observation_moment(value)
            if safe_moment is None:
                return "observation effective moment is unknowable"
            index, timestamp = safe_moment
            if index <= previous_index or (
                previous_timestamp is not None and timestamp <= previous_timestamp
            ):
                return "observation chronology is not strictly increasing"
            try:
                _validate_observation(
                    value,
                    expected_index=index,
                    expected_timestamp=timestamp,
                )
            except Exception as exc:
                return _exception_reason(exc)
            previous_index = index
            previous_timestamp = timestamp

    if calendar_entries is not None:
        previous_date: date | None = None
        for value in calendar_entries:
            safe_date = _safe_calendar_date(value)
            if safe_date is None:
                return "calendar trade date is unknowable"
            if previous_date is not None and safe_date <= previous_date:
                return "calendar entries must be unique and strictly increasing"
            try:
                _validate_calendar_entry(
                    value,
                    calendar_version=calendar_version,
                    timezone_value=None,
                )
            except Exception as exc:
                return _exception_reason(exc)
            previous_date = safe_date
    return None


def _validate_observation(
    value: object,
    *,
    expected_index: int,
    expected_timestamp: datetime,
) -> None:
    if type(value) is not KillZoneObservation:
        raise TypeError("observations must be exact KillZoneObservation values")
    try:
        index = value.index
        timestamp = value.timestamp
        is_closed = value.is_closed
    except Exception as exc:
        raise ValueError("malformed observation") from exc
    _validate_non_negative_int(index, name="observation index")
    normalized = _normalize_timestamp(timestamp, name="observation timestamp")
    if index != expected_index or normalized != expected_timestamp:
        raise ValueError("observation moment changed during validation")
    if type(is_closed) is not bool or not is_closed:
        raise ValueError("observation must be fully closed")


def _safe_observation_moment(value: object) -> tuple[int, datetime] | None:
    try:
        index = value.index
        timestamp = value.timestamp
        _validate_non_negative_int(index, name="observation index")
        normalized = _normalize_timestamp(timestamp, name="observation timestamp")
        return index, normalized
    except Exception:
        return None


def _safe_calendar_date(value: object) -> date | None:
    try:
        return _validate_date(value.trade_date, name="trade_date")
    except Exception:
        return None


def _candidate_for_timestamp(
    timestamp: datetime,
    *,
    timezone_value: ZoneInfo,
) -> tuple[KillZoneName, date] | None:
    local = timestamp.astimezone(timezone_value)
    local_time = local.timetz().replace(tzinfo=None)
    if time(20, 0) <= local_time:
        return KillZoneName.ASIA, local.date() + timedelta(days=1)
    if time(2, 0) <= local_time < time(5, 0):
        return KillZoneName.LONDON, local.date()
    if time(7, 0) <= local_time < time(10, 0):
        return KillZoneName.NEW_YORK_AM, local.date()
    if time(13, 0) <= local_time < time(16, 0):
        return KillZoneName.NEW_YORK_PM, local.date()
    return None


def _classify_candidate(
    *,
    candidate_zone: KillZoneName,
    trade_date_value: date,
    timestamp: datetime,
    entries: dict[date, KillZoneCalendarEntry],
) -> tuple[
    KillZoneName | None,
    KillZoneSessionStatus | None,
    KillZoneQuality,
]:
    if trade_date_value.weekday() >= 5:
        return (
            None,
            KillZoneSessionStatus.SESSION_CLOSED,
            KillZoneQuality.VERIFIED,
        )

    entry = entries.get(trade_date_value)
    if entry is None:
        return candidate_zone, None, KillZoneQuality.CALENDAR_UNVERIFIED
    if entry.session_status is KillZoneSessionStatus.SESSION_CLOSED:
        return (
            None,
            KillZoneSessionStatus.SESSION_CLOSED,
            KillZoneQuality.VERIFIED,
        )

    opening = _normalize_timestamp(
        entry.session_open_timestamp,
        name="session_open_timestamp",
    )
    closing = _normalize_timestamp(
        entry.session_close_timestamp,
        name="session_close_timestamp",
    )
    if opening <= timestamp < closing:
        return candidate_zone, entry.session_status, KillZoneQuality.VERIFIED
    return (
        None,
        KillZoneSessionStatus.SESSION_CLOSED,
        KillZoneQuality.VERIFIED,
    )


def _validate_context_geometry(
    *,
    zone: object,
    session_status: object,
    quality: KillZoneQuality,
) -> None:
    if quality is KillZoneQuality.CALENDAR_UNVERIFIED:
        if zone is None or session_status is not None:
            raise ValueError(
                "CALENDAR_UNVERIFIED requires a zone and no session status"
            )
        return
    if session_status in (
        KillZoneSessionStatus.OPEN,
        KillZoneSessionStatus.EARLY_CLOSE,
    ):
        if zone is None:
            raise ValueError("open verified context requires a zone")
        return
    if session_status is KillZoneSessionStatus.SESSION_CLOSED:
        if zone is not None:
            raise ValueError("closed verified context forbids a zone")
        return
    raise ValueError("VERIFIED context requires a session status")


def _runtime_timezone_data_version() -> str | None:
    try:
        return metadata.version("tzdata")
    except metadata.PackageNotFoundError:
        return None


def _load_timezone() -> ZoneInfo | None:
    try:
        return ZoneInfo(KILL_ZONE_TIMEZONE)
    except Exception:
        return None


def _normalize_text(value: object, *, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be text")
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    return normalized


def _normalize_timestamp(value: object, *, name: str) -> datetime:
    try:
        return normalize_utc_timestamp(value)  # type: ignore[arg-type]
    except Exception as exc:
        raise ValueError(f"{name} must be a valid aware timestamp") from exc


def _timestamp_text(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_non_negative_int(value: object, *, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


def _validate_date(value: object, *, name: str) -> date:
    if type(value) is not date:
        raise TypeError(f"{name} must be an exact date")
    return value


def _validate_hash_tuple(value: object, *, name: str) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    if not value:
        raise ValueError(f"{name} cannot be empty")
    if any(type(item) is not str or _HASH_PATTERN.fullmatch(item) is None for item in value):
        raise ValueError(f"{name} must contain lowercase SHA-256 values")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must contain unique values")
    return value


def _exception_reason(exc: Exception) -> str:
    text = str(exc).strip()
    return text or type(exc).__name__


def _result(
    status: SMCV2PrimitiveStatus,
    *,
    contexts: tuple[KillZoneContext, ...] = (),
    snapshots: tuple[KillZoneSnapshot, ...] = (),
    reason: str | None,
) -> KillZoneResult:
    reasons = () if reason is None else (reason,)
    blocking = (
        reasons
        if status in (SMCV2PrimitiveStatus.INVALID, SMCV2PrimitiveStatus.UNKNOWN)
        else ()
    )
    return KillZoneResult(
        status=status,
        contexts=contexts,
        snapshots=snapshots,
        reasons=reasons,
        blocking_reasons=blocking,
    )


__all__ = [
    "KILL_ZONE_DETECTOR_VERSION",
    "KILL_ZONE_TIMEZONE",
    "KillZoneName",
    "KillZoneSessionStatus",
    "KillZoneQuality",
    "KillZoneObservation",
    "KillZoneCalendarEntry",
    "KillZoneContext",
    "KillZoneSnapshot",
    "KillZoneResult",
    "make_kill_zone_id",
    "analyze_kill_zones",
]
