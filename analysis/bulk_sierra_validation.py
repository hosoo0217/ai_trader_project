"""Diagnostic-only helpers for future Sierra Chart bulk validation.

This module only parses exported CSV text and summarizes daily/session
alignment. It does not run backtests, change strategy behavior, connect to
brokers, or approve paper/live trading.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from io import StringIO


@dataclass(frozen=True)
class TimestampedCsvRow:
    """One CSV row with a parsed Sierra timestamp."""

    timestamp: datetime
    raw: dict[str, str]


@dataclass(frozen=True)
class SierraSessionRows:
    """Rows grouped by session date."""

    session_date: str
    start: datetime
    end: datetime
    rows: list[TimestampedCsvRow]

    @property
    def row_count(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class SierraBulkSessionSummary:
    """Lightweight diagnostic summary for one matched or bad session."""

    session_date: str
    status: str
    start: datetime | None
    end: datetime | None
    market_row_count: int
    footprint_row_count: int
    market_bad_row_count: int = 0
    footprint_bad_row_count: int = 0
    reasons: list[str] = field(default_factory=list)


def parse_sierra_footprint_csv(csv_text: str) -> list[TimestampedCsvRow]:
    """Parse ACSIL footprint rows using the DateTime column."""
    rows, _bad_row_count = _parse_timestamped_csv(csv_text, _footprint_timestamp)
    return rows


def parse_sierra_market_csv(csv_text: str) -> list[TimestampedCsvRow]:
    """Parse Sierra market rows using Date + Time columns."""
    rows, _bad_row_count = _parse_timestamped_csv(csv_text, _market_timestamp)
    return rows


def split_rows_by_session_date(
    rows: list[TimestampedCsvRow],
    session_start_hour: int = 18,
) -> list[SierraSessionRows]:
    """Split timestamped rows into futures-style session groups."""
    grouped: dict[str, list[TimestampedCsvRow]] = {}
    for row in sorted(rows, key=lambda item: item.timestamp):
        session_date = _session_date(row.timestamp, session_start_hour)
        grouped.setdefault(session_date, []).append(row)

    sessions: list[SierraSessionRows] = []
    for session_date in sorted(grouped):
        session_rows = grouped[session_date]
        sessions.append(
            SierraSessionRows(
                session_date=session_date,
                start=session_rows[0].timestamp,
                end=session_rows[-1].timestamp,
                rows=session_rows,
            )
        )
    return sessions


def build_bulk_validation_summary(
    market_csv_text: str,
    footprint_csv_text: str,
    session_start_hour: int = 18,
) -> list[SierraBulkSessionSummary]:
    """Build per-session diagnostic summaries without running backtests."""
    market_rows, market_bad_row_count = _parse_timestamped_csv(market_csv_text, _market_timestamp)
    footprint_rows, footprint_bad_row_count = _parse_timestamped_csv(
        footprint_csv_text,
        _footprint_timestamp,
    )

    market_sessions = {
        session.session_date: session
        for session in split_rows_by_session_date(market_rows, session_start_hour)
    }
    footprint_sessions = {
        session.session_date: session
        for session in split_rows_by_session_date(footprint_rows, session_start_hour)
    }

    summaries: list[SierraBulkSessionSummary] = []
    for session_date in sorted(set(market_sessions) | set(footprint_sessions)):
        market_session = market_sessions.get(session_date)
        footprint_session = footprint_sessions.get(session_date)
        reasons = _bad_row_reasons(market_bad_row_count, footprint_bad_row_count)

        if market_session is None:
            reasons.append("Market session is missing")
            summaries.append(
                SierraBulkSessionSummary(
                    session_date=session_date,
                    status="MISSING_MARKET",
                    start=footprint_session.start if footprint_session else None,
                    end=footprint_session.end if footprint_session else None,
                    market_row_count=0,
                    footprint_row_count=footprint_session.row_count if footprint_session else 0,
                    market_bad_row_count=market_bad_row_count,
                    footprint_bad_row_count=footprint_bad_row_count,
                    reasons=reasons,
                )
            )
            continue

        if footprint_session is None:
            reasons.append("Footprint session is missing")
            summaries.append(
                SierraBulkSessionSummary(
                    session_date=session_date,
                    status="MISSING_FOOTPRINT",
                    start=market_session.start,
                    end=market_session.end,
                    market_row_count=market_session.row_count,
                    footprint_row_count=0,
                    market_bad_row_count=market_bad_row_count,
                    footprint_bad_row_count=footprint_bad_row_count,
                    reasons=reasons,
                )
            )
            continue

        common_start = max(market_session.start, footprint_session.start)
        common_end = min(market_session.end, footprint_session.end)
        status = "MATCHED"
        if market_session.start != footprint_session.start or market_session.end != footprint_session.end:
            status = "MISMATCHED"
            reasons.append("Session start/end differ")

        summaries.append(
            SierraBulkSessionSummary(
                session_date=session_date,
                status=status,
                start=common_start,
                end=common_end,
                market_row_count=market_session.row_count,
                footprint_row_count=footprint_session.row_count,
                market_bad_row_count=market_bad_row_count,
                footprint_bad_row_count=footprint_bad_row_count,
                reasons=reasons,
            )
        )

    return summaries


def _parse_timestamped_csv(
    csv_text: str,
    timestamp_parser: Callable[[dict[str, str]], datetime | None],
) -> tuple[list[TimestampedCsvRow], int]:
    rows: list[TimestampedCsvRow] = []
    bad_row_count = 0

    reader = csv.DictReader(StringIO(csv_text.strip()))
    for raw_row in reader:
        cleaned_row = {
            str(key).strip(): "" if value is None else str(value).strip()
            for key, value in raw_row.items()
            if key is not None
        }
        timestamp = timestamp_parser(cleaned_row)
        if timestamp is None:
            bad_row_count += 1
            continue
        rows.append(TimestampedCsvRow(timestamp=timestamp, raw=cleaned_row))

    return rows, bad_row_count


def _footprint_timestamp(row: dict[str, str]) -> datetime | None:
    return _parse_datetime(row.get("DateTime", ""))


def _market_timestamp(row: dict[str, str]) -> datetime | None:
    date_text = row.get("Date", "")
    time_text = row.get("Time", "")
    return _parse_datetime(f"{date_text} {time_text}".strip())


def _parse_datetime(value: str) -> datetime | None:
    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for datetime_format in formats:
        try:
            return datetime.strptime(text, datetime_format)
        except ValueError:
            continue
    return None


def _session_date(timestamp: datetime, session_start_hour: int) -> str:
    start_hour = int(session_start_hour)
    if start_hour < 0 or start_hour > 23:
        start_hour = 18

    session_day = timestamp.date()
    if timestamp.hour < start_hour:
        session_day = (timestamp - timedelta(days=1)).date()
    return session_day.isoformat()


def _bad_row_reasons(market_bad_row_count: int, footprint_bad_row_count: int) -> list[str]:
    reasons: list[str] = []
    if market_bad_row_count:
        reasons.append(f"Market CSV has {market_bad_row_count} bad timestamp row")
    if footprint_bad_row_count:
        reasons.append(f"Footprint CSV has {footprint_bad_row_count} bad timestamp row")
    return reasons
