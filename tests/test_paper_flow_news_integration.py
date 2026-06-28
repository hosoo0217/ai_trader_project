"""Integration tests for NewsFilter + PaperTradingFlow behavior."""

from datetime import datetime, timezone

import pandas as pd

from analysis.news_filter import NewsEvent, NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.trade_journal import TradeJournal


def _make_candles(rows: int = 80) -> pd.DataFrame:
    closes = [100 + index for index in range(rows)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": closes,
            "high": [value + 1 for value in closes],
            "low": [value - 1 for value in closes],
            "close": closes,
        }
    )


def _run_flow(
    current_time: datetime,
    news_config: NewsFilterConfig | None = None,
    session_config: SessionFilterConfig | None = None,
    journal: TradeJournal | None = None,
):
    flow = PaperTradingFlow()
    return flow.run_single_timeframe(
        candles=_make_candles(),
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=PaperBrokerState(),
        journal=journal,
        risk_config=RiskEngineConfig(),
        session_config=session_config or SessionFilterConfig(enabled=False),
        current_time=current_time,
        news_config=news_config,
    )


def test_no_news_events_allows_trade_flow_to_continue() -> None:
    result = _run_flow(datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc))

    assert result.news_checked is True
    assert result.news_allowed is True
    assert result.news_status == "NEWS_ALLOWED"


def test_high_impact_news_blocks_trade() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(
        events=[NewsEvent(name="FOMC", event_time_utc=event_time, impact="HIGH")]
    )

    result = _run_flow(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), news_config=config)

    assert result.news_checked is True
    assert result.news_allowed is False
    assert result.news_status == "NEWS_BLOCKED"
    assert result.decision_action == "NO_TRADE"
    assert result.trade_executed is False
    assert result.risk_checked is False


def test_medium_impact_news_does_not_block_by_default() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(
        events=[NewsEvent(name="PMI", event_time_utc=event_time, impact="MEDIUM")]
    )

    result = _run_flow(datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc), news_config=config)

    assert result.news_checked is True
    assert result.news_allowed is True
    assert result.news_status == "NEWS_ALLOWED"


def test_news_blocked_trade_is_recorded_in_journal() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(
        events=[NewsEvent(name="FOMC", event_time_utc=event_time, impact="HIGH")]
    )
    journal = TradeJournal()

    result = _run_flow(
        datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc),
        news_config=config,
        journal=journal,
    )

    entries = journal.get_all_entries()
    assert result.journal_recorded is True
    assert len(entries) == 1
    assert entries[0].executed is False
    assert entries[0].action == "NO_TRADE"
    assert entries[0].status == "BLOCKED"
    assert any("News status" in reason for reason in entries[0].reasons)
    assert len(entries[0].blocking_reasons) > 0


def test_news_blocked_trade_does_not_execute_paper_order() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    config = NewsFilterConfig(
        events=[NewsEvent(name="FOMC", event_time_utc=event_time, impact="HIGH")]
    )
    flow = PaperTradingFlow()
    broker_state = PaperBrokerState()

    result = flow.run_single_timeframe(
        candles=_make_candles(),
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=broker_state,
        risk_config=RiskEngineConfig(),
        session_config=SessionFilterConfig(enabled=False),
        current_time=datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc),
        news_config=config,
    )

    assert result.trade_executed is False
    assert len(broker_state.open_positions) == 0


def test_flow_still_works_when_news_config_not_provided() -> None:
    result = _run_flow(datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc), news_config=None)

    assert result.completed is True
    assert result.news_checked is True
    assert result.news_status is not None


def test_existing_session_filter_behavior_still_works() -> None:
    result = _run_flow(
        datetime(2026, 6, 24, 2, 0, tzinfo=timezone.utc),
        session_config=SessionFilterConfig(),
    )

    assert result.session_checked is True
    assert result.session_allowed is False
    assert result.session_status == "SESSION_BLOCKED"
    assert result.news_checked is False
