"""Session-based safety filter for paper trading and backtesting.

This module decides whether trading is allowed for a given UTC time.
It is research-only and does not connect to any broker or external API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TradingSession:
    """One named UTC session window."""

    name: str
    start_hour_utc: int
    end_hour_utc: int
    enabled: bool


@dataclass
class SessionFilterConfig:
    """Configuration for session-time safety checks."""

    enabled: bool = True
    allowed_sessions: list[TradingSession] = field(default_factory=lambda: [
        TradingSession(name="London", start_hour_utc=7, end_hour_utc=16, enabled=True),
        TradingSession(name="New York", start_hour_utc=13, end_hour_utc=21, enabled=True),
        TradingSession(name="London New York Overlap", start_hour_utc=13, end_hour_utc=16, enabled=True),
        TradingSession(name="Asian", start_hour_utc=0, end_hour_utc=6, enabled=False),
    ])
    block_weekends: bool = True
    timezone_note: str = "All session times are UTC"


@dataclass
class SessionFilterResult:
    """Outcome of one session filter evaluation."""

    allowed: bool
    active_session: str | None
    status: str
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class SessionFilter:
    """Evaluate whether trading is allowed for the current session."""

    def evaluate(self, current_time: datetime | None, config: SessionFilterConfig) -> SessionFilterResult:
        """Return a safe allow/block decision based on session rules."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if not isinstance(current_time, datetime):
            return SessionFilterResult(
                allowed=False,
                active_session=None,
                status="INVALID_TIME",
                reasons=["Current time is missing or invalid"],
                blocking_reasons=["Current time is missing or invalid"],
            )

        effective_time = current_time
        if current_time.tzinfo is None:
            # Safe behavior: interpret naive timestamps as UTC and continue.
            effective_time = current_time.replace(tzinfo=timezone.utc)
            reasons.append("Naive datetime provided; treating it as UTC")
        else:
            effective_time = current_time.astimezone(timezone.utc)

        if not config.enabled:
            reasons.append("Session filter disabled")
            return SessionFilterResult(
                allowed=True,
                active_session=None,
                status="FILTER_DISABLED",
                reasons=reasons,
                blocking_reasons=[],
            )

        # Python weekday: Monday=0 ... Sunday=6
        weekday = effective_time.weekday()
        if config.block_weekends and weekday >= 5:
            blocking_reasons.append("Weekend trading is blocked")
            return SessionFilterResult(
                allowed=False,
                active_session=None,
                status="WEEKEND_BLOCKED",
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        current_hour = int(effective_time.hour)

        matching_sessions: list[TradingSession] = []
        enabled_matches: list[TradingSession] = []
        disabled_matches: list[TradingSession] = []

        for session in config.allowed_sessions:
            if self._hour_in_session(current_hour, session):
                matching_sessions.append(session)
                if session.enabled:
                    enabled_matches.append(session)
                else:
                    disabled_matches.append(session)

        if enabled_matches:
            active_session = enabled_matches[0].name
            reasons.append(f"Current time is inside enabled session: {active_session}")
            return SessionFilterResult(
                allowed=True,
                active_session=active_session,
                status="SESSION_ALLOWED",
                reasons=reasons,
                blocking_reasons=[],
            )

        if matching_sessions and disabled_matches:
            active_session = disabled_matches[0].name
            blocking_reasons.append(f"Current time is inside disabled session: {active_session}")
            return SessionFilterResult(
                allowed=False,
                active_session=active_session,
                status="SESSION_BLOCKED",
                reasons=reasons,
                blocking_reasons=blocking_reasons,
            )

        blocking_reasons.append("Current time is outside all allowed sessions")
        return SessionFilterResult(
            allowed=False,
            active_session=None,
            status="SESSION_BLOCKED",
            reasons=reasons,
            blocking_reasons=blocking_reasons,
        )

    def explain(self, result: SessionFilterResult) -> str:
        """Return a readable explanation for logs and console output."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        active_session = result.active_session if result.active_session is not None else "None"

        return (
            f"Session filter status: {result.status} | "
            f"allowed: {result.allowed} | "
            f"active session: {active_session} | "
            f"reasons: {reasons_text} | "
            f"blocking reasons: {blocks_text}"
        )

    def _hour_in_session(self, hour_utc: int, session: TradingSession) -> bool:
        """Check if an hour falls into one session window.

        Session windows are inclusive on both boundaries.
        """
        start = int(session.start_hour_utc)
        end = int(session.end_hour_utc)

        if start <= end:
            return start <= hour_utc <= end

        # Supports cross-midnight windows such as 22 -> 2.
        return hour_utc >= start or hour_utc <= end
