"""Integration tests for SafetyGate + PaperTradingFlow behavior."""

from datetime import datetime, timedelta, timezone

import pandas as pd

from analysis.news_filter import NewsEvent, NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBrokerConfig, PaperBrokerState
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.trade_journal import TradeJournal


def _make_candles(rows: int = 80, base_range: float = 2.0) -> pd.DataFrame:
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    price = 100.0
    data: list[dict[str, float | datetime]] = []

    for index in range(rows):
        open_price = price
        high = open_price + (base_range / 2.0)
        low = open_price - (base_range / 2.0)
        close = open_price + 0.1
        data.append(
            {
                "time": start + timedelta(minutes=index),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
            }
        )
        price = close

    return pd.DataFrame(data)


def _run_flow(
    candles: pd.DataFrame,
    session_config: SessionFilterConfig | None = None,
    current_time: datetime | None = None,
    news_config: NewsFilterConfig | None = None,
    volatility_config: VolatilityFilterConfig | None = None,
    spread_config: SpreadFilterConfig | None = None,
    current_spread: float | None = 1.0,
    capital_config: CapitalProtectionConfig | None = None,
    capital_state: CapitalProtectionState | None = None,
    journal: TradeJournal | None = None,
    broker_state: PaperBrokerState | None = None,
):
    return PaperTradingFlow().run_single_timeframe(
        candles=candles,
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
        capital_config=capital_config or CapitalProtectionConfig(),
        capital_state=capital_state or CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=broker_state or PaperBrokerState(),
        journal=journal,
        risk_config=RiskEngineConfig(),
        session_config=session_config or SessionFilterConfig(enabled=False),
        current_time=current_time or datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        news_config=news_config or NewsFilterConfig(),
        volatility_config=volatility_config or VolatilityFilterConfig(min_atr=0.1, max_atr=100.0),
        spread_config=spread_config or SpreadFilterConfig(max_spread=3.0),
        current_spread=current_spread,
    )


def test_all_safety_checks_passed_allows_flow_to_continue() -> None:
    result = _run_flow(_make_candles(base_range=2.0))

    assert result.safety_checked is True
    assert result.safety_allowed is True
    assert result.safety_status == "SAFETY_PASSED"


def test_session_blocked_causes_safety_gate_block() -> None:
    result = _run_flow(
        _make_candles(base_range=2.0),
        session_config=SessionFilterConfig(),
        current_time=datetime(2026, 6, 24, 2, 0, tzinfo=timezone.utc),
    )

    assert result.safety_checked is True
    assert result.safety_allowed is False
    assert result.safety_status == "SAFETY_BLOCKED"
    assert "SESSION" in result.safety_failed_checks


def test_news_blocked_causes_safety_gate_block() -> None:
    event_time = datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc)
    result = _run_flow(
        _make_candles(base_range=2.0),
        news_config=NewsFilterConfig(events=[NewsEvent(name="FOMC", event_time_utc=event_time, impact="HIGH")]),
        current_time=datetime(2026, 6, 24, 13, 45, tzinfo=timezone.utc),
    )

    assert result.safety_allowed is False
    assert "NEWS" in result.safety_failed_checks


def test_volatility_blocked_causes_safety_gate_block() -> None:
    result = _run_flow(
        _make_candles(base_range=0.02),
        volatility_config=VolatilityFilterConfig(min_atr=0.1, max_atr=5.0),
    )

    assert result.safety_allowed is False
    assert "VOLATILITY" in result.safety_failed_checks


def test_spread_blocked_causes_safety_gate_block() -> None:
    result = _run_flow(
        _make_candles(base_range=2.0),
        spread_config=SpreadFilterConfig(max_spread=2.0),
        current_spread=4.0,
    )

    assert result.safety_allowed is False
    assert "SPREAD" in result.safety_failed_checks


def test_capital_protection_blocked_causes_safety_gate_block() -> None:
    result = _run_flow(
        _make_candles(base_range=2.0),
        capital_config=CapitalProtectionConfig(max_daily_loss=1.0),
        capital_state=CapitalProtectionState(realized_daily_pnl=-1.0),
    )

    assert result.safety_allowed is False
    assert "CAPITAL_PROTECTION" in result.safety_failed_checks


def test_safety_blocked_trade_is_recorded_in_journal() -> None:
    journal = TradeJournal()
    result = _run_flow(
        _make_candles(base_range=2.0),
        spread_config=SpreadFilterConfig(max_spread=2.0),
        current_spread=4.0,
        journal=journal,
    )

    entries = journal.get_all_entries()
    assert result.journal_recorded is True
    assert len(entries) == 1
    assert entries[0].executed is False
    assert entries[0].action == "NO_TRADE"
    assert entries[0].status == "BLOCKED"
    assert len(entries[0].blocking_reasons) > 0


def test_safety_blocked_trade_does_not_execute_paper_order() -> None:
    broker_state = PaperBrokerState()
    result = _run_flow(
        _make_candles(base_range=2.0),
        spread_config=SpreadFilterConfig(max_spread=2.0),
        current_spread=4.0,
        broker_state=broker_state,
    )

    assert result.trade_executed is False
    assert len(broker_state.open_positions) == 0
