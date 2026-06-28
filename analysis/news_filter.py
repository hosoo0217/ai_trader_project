"""News-based safety filter for paper trading and backtesting.

This module blocks trading around manually configured news-event windows.
It is research-only and does not connect to any external calendar API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class NewsEvent:
    """One manually configured news event in UTC time."""

    name: str
    event_time_utc: datetime
    impact: str
    block_minutes_before: int = 30
    block_minutes_after: int = 30
    enabled: bool = True


@dataclass
class NewsFilterConfig:
    """Configuration for manual news-event blocking behavior."""

    enabled: bool = True
    block_high_impact: bool = True
    block_medium_impact: bool = False
    block_low_impact: bool = False
    events: list[NewsEvent] = field(default_factory=list)


@dataclass
class NewsFilterResult:
    """Outcome of one news filter evaluation."""

    allowed: bool
    status: str
    active_event: str | None
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class NewsFilter:
    """Evaluate whether trading is allowed around configured news windows."""

    def evaluate(self, current_time: datetime | None, config: NewsFilterConfig) -> NewsFilterResult:
        """Return a safe allow/block decision from manual news windows."""
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if not isinstance(current_time, datetime):
            return NewsFilterResult(
                allowed=False,
                status="INVALID_TIME",
                active_event=None,
                reasons=["Current time is missing or invalid"],
                blocking_reasons=["Current time is missing or invalid"],
            )

        effective_current = current_time
        if current_time.tzinfo is None:
            # Safe behavior: interpret naive timestamps as UTC and continue.
            effective_current = current_time.replace(tzinfo=timezone.utc)
            reasons.append("Naive datetime provided; treating it as UTC")
        else:
            effective_current = current_time.astimezone(timezone.utc)

        if not config.enabled:
            reasons.append("News filter disabled")
            return NewsFilterResult(
                allowed=True,
                status="FILTER_DISABLED",
                active_event=None,
                reasons=reasons,
                blocking_reasons=[],
            )

        for event in config.events:
            if not event.enabled:
                continue

            impact = (event.impact or "").upper().strip()
            if not self._impact_should_block(impact, config):
                continue

            if not isinstance(event.event_time_utc, datetime):
                reasons.append(f"Event '{event.name}' has invalid event_time_utc and was ignored")
                continue

            event_time = event.event_time_utc
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)
            else:
                event_time = event_time.astimezone(timezone.utc)

            before_minutes = max(0, int(event.block_minutes_before))
            after_minutes = max(0, int(event.block_minutes_after))

            window_start = event_time - timedelta(minutes=before_minutes)
            window_end = event_time + timedelta(minutes=after_minutes)

            if window_start <= effective_current <= window_end:
                blocking_reasons.append(
                    f"Blocking around {impact} impact event '{event.name}'"
                )
                return NewsFilterResult(
                    allowed=False,
                    status="NEWS_BLOCKED",
                    active_event=event.name,
                    reasons=reasons,
                    blocking_reasons=blocking_reasons,
                )

        reasons.append("No blocking news event is active")
        return NewsFilterResult(
            allowed=True,
            status="NEWS_ALLOWED",
            active_event=None,
            reasons=reasons,
            blocking_reasons=[],
        )

    def explain(self, result: NewsFilterResult) -> str:
        """Return a readable explanation for logs and console output."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        active_event = result.active_event if result.active_event is not None else "None"

        return (
            f"News filter status: {result.status} | "
            f"allowed: {result.allowed} | "
            f"active event: {active_event} | "
            f"reasons: {reasons_text} | "
            f"blocking reasons: {blocks_text}"
        )

    def _impact_should_block(self, impact: str, config: NewsFilterConfig) -> bool:
        """Return True when this impact level should block by configuration."""
        if impact == "HIGH":
            return bool(config.block_high_impact)
        if impact == "MEDIUM":
            return bool(config.block_medium_impact)
        if impact == "LOW":
            return bool(config.block_low_impact)

        return False
