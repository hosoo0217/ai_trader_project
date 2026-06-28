from datetime import datetime, timezone

from analysis.news_filter import NewsEvent, NewsFilter, NewsFilterConfig


def _event(name: str, event_time: datetime, impact: str, enabled: bool = True) -> NewsEvent:
    return NewsEvent(
        name=name,
        event_time_utc=event_time,
        impact=impact,
        block_minutes_before=30,
        block_minutes_after=30,
        enabled=enabled,
    )


def test_high_impact_event_blocks_trading_inside_window() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("FOMC", event_time, "HIGH")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is False
    assert result.status == "NEWS_BLOCKED"
    assert result.active_event == "FOMC"


def test_high_impact_event_allows_trading_outside_window() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("CPI", event_time, "HIGH")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 12, 0, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "NEWS_ALLOWED"


def test_medium_impact_does_not_block_by_default() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("PMI", event_time, "MEDIUM")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "NEWS_ALLOWED"


def test_medium_impact_blocks_when_enabled() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(block_medium_impact=True, events=[_event("PMI", event_time, "MEDIUM")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is False
    assert result.status == "NEWS_BLOCKED"


def test_low_impact_does_not_block_by_default() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("Minor Data", event_time, "LOW")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "NEWS_ALLOWED"


def test_disabled_event_is_ignored() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("NFP", event_time, "HIGH", enabled=False)])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "NEWS_ALLOWED"


def test_filter_disabled_allows_trading() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(enabled=False, events=[_event("NFP", event_time, "HIGH")])

    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "FILTER_DISABLED"
    assert "News filter disabled" in result.reasons


def test_invalid_time_blocks_trading() -> None:
    result = NewsFilter().evaluate(None, NewsFilterConfig())

    assert result.allowed is False
    assert result.status == "INVALID_TIME"


def test_explain_returns_readable_text() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(events=[_event("NFP", event_time, "HIGH")])
    result = NewsFilter().evaluate(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), config)
    text = NewsFilter().explain(result)

    assert "News filter status" in text
    assert "allowed" in text
    assert "active event" in text
