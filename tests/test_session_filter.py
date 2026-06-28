from datetime import datetime, timezone

from analysis.session_filter import SessionFilter, SessionFilterConfig


def test_london_session_allowed() -> None:
    result = SessionFilter().evaluate(
        datetime(2026, 6, 24, 8, 0, tzinfo=timezone.utc),
        SessionFilterConfig(),
    )

    assert result.allowed is True
    assert result.status == "SESSION_ALLOWED"


def test_new_york_session_allowed() -> None:
    result = SessionFilter().evaluate(
        datetime(2026, 6, 24, 17, 0, tzinfo=timezone.utc),
        SessionFilterConfig(),
    )

    assert result.allowed is True
    assert result.status == "SESSION_ALLOWED"


def test_overlap_session_allowed() -> None:
    result = SessionFilter().evaluate(
        datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        SessionFilterConfig(),
    )

    assert result.allowed is True
    assert result.status == "SESSION_ALLOWED"


def test_asian_session_blocked_by_default() -> None:
    result = SessionFilter().evaluate(
        datetime(2026, 6, 24, 2, 0, tzinfo=timezone.utc),
        SessionFilterConfig(),
    )

    assert result.allowed is False
    assert result.status == "SESSION_BLOCKED"
    assert any("disabled session" in reason.lower() for reason in result.blocking_reasons)


def test_weekend_blocked() -> None:
    # 2026-06-27 is Saturday.
    result = SessionFilter().evaluate(
        datetime(2026, 6, 27, 14, 0, tzinfo=timezone.utc),
        SessionFilterConfig(),
    )

    assert result.allowed is False
    assert result.status == "WEEKEND_BLOCKED"


def test_filter_disabled_allows_trading() -> None:
    config = SessionFilterConfig(enabled=False)
    result = SessionFilter().evaluate(datetime(2026, 6, 27, 14, 0, tzinfo=timezone.utc), config)

    assert result.allowed is True
    assert result.status == "FILTER_DISABLED"
    assert "Session filter disabled" in result.reasons


def test_invalid_time_blocks_trading() -> None:
    result = SessionFilter().evaluate(None, SessionFilterConfig())

    assert result.allowed is False
    assert result.status == "INVALID_TIME"


def test_naive_datetime_handled_safely() -> None:
    naive_time = datetime(2026, 6, 24, 14, 0)
    result = SessionFilter().evaluate(naive_time, SessionFilterConfig())

    assert result.status in {"SESSION_ALLOWED", "SESSION_BLOCKED", "WEEKEND_BLOCKED"}
    assert any("naive datetime" in reason.lower() for reason in result.reasons)


def test_explain_returns_readable_text() -> None:
    filter_engine = SessionFilter()
    result = filter_engine.evaluate(datetime(2026, 6, 24, 8, 0, tzinfo=timezone.utc), SessionFilterConfig())
    explanation = filter_engine.explain(result)

    assert "Session filter status" in explanation
    assert "allowed" in explanation
    assert "active session" in explanation
