"""Integration tests for VolatilityFilter + PaperTradingFlow behavior."""

from datetime import datetime, timedelta, timezone

import pandas as pd

from analysis.news_filter import NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
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
    volatility_config: VolatilityFilterConfig | None = None,
    journal: TradeJournal | None = None,
):
    return PaperTradingFlow().run_single_timeframe(
        candles=candles,
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=PaperBrokerState(),
        journal=journal,
        risk_config=RiskEngineConfig(),
        session_config=SessionFilterConfig(enabled=False),
        current_time=datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        news_config=NewsFilterConfig(),
        volatility_config=volatility_config,
    )


def test_normal_volatility_allows_trade_flow_to_continue() -> None:
    result = _run_flow(
        _make_candles(base_range=2.0),
        VolatilityFilterConfig(min_atr=0.5, max_atr=5.0),
    )

    assert result.volatility_checked is True
    assert result.volatility_allowed is True
    assert result.volatility_status == "VOLATILITY_ALLOWED"


def test_too_low_volatility_blocks_trade() -> None:
    result = _run_flow(
        _make_candles(base_range=0.02),
        VolatilityFilterConfig(min_atr=0.1, max_atr=5.0),
    )

    assert result.volatility_checked is True
    assert result.volatility_allowed is False
    assert result.volatility_status == "VOLATILITY_TOO_LOW"
    assert result.decision_action == "NO_TRADE"
    assert result.trade_executed is False
    assert result.risk_checked is False


def test_too_high_volatility_blocks_trade() -> None:
    result = _run_flow(
        _make_candles(base_range=12.0),
        VolatilityFilterConfig(min_atr=0.1, max_atr=5.0),
    )

    assert result.volatility_checked is True
    assert result.volatility_allowed is False
    assert result.volatility_status == "VOLATILITY_TOO_HIGH"
    assert result.trade_executed is False


def test_abnormal_last_candle_blocks_trade() -> None:
    candles = _make_candles(base_range=2.0)
    candles.loc[candles.index[-1], "high"] = candles.loc[candles.index[-1], "close"] + 20.0
    candles.loc[candles.index[-1], "low"] = candles.loc[candles.index[-1], "close"] - 20.0

    result = _run_flow(
        candles,
        VolatilityFilterConfig(min_atr=0.1, max_atr=100.0, max_last_candle_range_multiplier=3.0),
    )

    assert result.volatility_checked is True
    assert result.volatility_allowed is False
    assert result.volatility_status == "ABNORMAL_LAST_CANDLE"
    assert result.trade_executed is False


def test_volatility_blocked_trade_is_recorded_in_journal() -> None:
    journal = TradeJournal()
    result = _run_flow(
        _make_candles(base_range=0.02),
        VolatilityFilterConfig(min_atr=0.1, max_atr=5.0),
        journal,
    )

    entries = journal.get_all_entries()
    assert result.journal_recorded is True
    assert len(entries) == 1
    assert entries[0].executed is False
    assert entries[0].action == "NO_TRADE"
    assert entries[0].status == "BLOCKED"
    assert any("Volatility status" in reason for reason in entries[0].reasons)
    assert len(entries[0].blocking_reasons) > 0


def test_volatility_blocked_trade_does_not_execute_paper_order() -> None:
    broker_state = PaperBrokerState()
    result = PaperTradingFlow().run_single_timeframe(
        candles=_make_candles(base_range=0.02),
        flow_config=PaperTradingFlowConfig(),
        market_config=MarketAnalyzerConfig(),
        mtf_config=MultiTimeframeConfig(minimum_confidence=0.0),
        capital_config=CapitalProtectionConfig(),
        capital_state=CapitalProtectionState(),
        broker_config=PaperBrokerConfig(),
        broker_state=broker_state,
        risk_config=RiskEngineConfig(),
        session_config=SessionFilterConfig(enabled=False),
        current_time=datetime(2026, 6, 24, 14, 0, tzinfo=timezone.utc),
        news_config=NewsFilterConfig(),
        volatility_config=VolatilityFilterConfig(min_atr=0.1, max_atr=5.0),
    )

    assert result.trade_executed is False
    assert len(broker_state.open_positions) == 0


def test_flow_still_works_when_volatility_config_not_provided() -> None:
    result = _run_flow(_make_candles(base_range=2.0), volatility_config=None)

    assert result.completed is True
    assert result.volatility_checked is True
    assert result.volatility_status is not None
