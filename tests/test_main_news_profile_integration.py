from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO

from analysis.news_filter import NewsFilter
from config.trading_profiles import TradingProfileFactory, to_news_filter_config
import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_apex_profile_creates_enabled_news_filter() -> None:
    profile = TradingProfileFactory.create_apex_futures_profile()
    config = to_news_filter_config(profile)

    assert config.enabled is True
    assert config.block_high_impact is True
    assert config.block_medium_impact is False
    assert config.block_low_impact is False


def test_spot_profile_creates_enabled_news_filter() -> None:
    profile = TradingProfileFactory.create_spot_gold_profile()
    config = to_news_filter_config(profile)

    assert config.enabled is True
    assert config.block_high_impact is True
    assert config.block_medium_impact is False
    assert config.block_low_impact is False


def test_safe_profile_creates_conservative_news_filter() -> None:
    profile = TradingProfileFactory.create_safe_default_profile()
    config = to_news_filter_config(profile)

    assert config.enabled is True
    assert config.block_high_impact is True
    assert config.block_medium_impact is True
    assert config.block_low_impact is True

    result = NewsFilter().evaluate(
        datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        config,
    )
    assert result.status in {"NEWS_ALLOWED", "NEWS_BLOCKED"}


def test_demo_mode_with_high_impact_news_inside_window_blocks_trade_safely() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T14:20:00Z",
        "--news-event",
        "NFP:2026-06-24T14:30:00Z:HIGH",
    )

    assert "News filter status" in output
    assert "News allowed: False" in output
    assert "Trade executed or blocked: Blocked / No trade" in output


def test_demo_mode_with_high_impact_news_outside_window_runs_without_crashing() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T10:00:00Z",
        "--news-event",
        "NFP:2026-06-24T14:30:00Z:HIGH",
    )

    assert "AI Trader Paper Trading Demo" in output
    assert "News filter status" in output


def test_invalid_news_event_does_not_crash() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--news-event",
        "invalid-event",
    )

    assert "Warning" in output
    assert "AI Trader Paper Trading Demo" in output


def test_backtest_mode_runs_with_news_filter_enabled() -> None:
    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "spot",
        "--news-event",
        "FOMC:2026-06-24T18:00:00Z:HIGH",
    )

    assert "AI Trader Backtest" in output
    assert "News filter status" in output


def test_output_contains_news_filter_information() -> None:
    output = _run_main(
        "--mode",
        "demo",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--session-time",
        "2026-06-24T14:20:00Z",
        "--news-event",
        "NFP:2026-06-24T14:30:00Z:HIGH",
    )

    assert "News filter status" in output
    assert "Active news event" in output
    assert "News allowed" in output
