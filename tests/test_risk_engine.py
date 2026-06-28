"""Unit tests for the simple risk engine."""

from risk.risk_engine import RiskEngine, RiskEngineConfig


def test_buy_plan_calculates_sl_below_and_tp_above_entry() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("BUY", 2000.0, RiskEngineConfig())

    assert plan.allowed is True
    assert plan.stop_loss is not None and plan.stop_loss < plan.entry_price
    assert plan.take_profit is not None and plan.take_profit > plan.entry_price


def test_sell_plan_calculates_sl_above_and_tp_below_entry() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("SELL", 2000.0, RiskEngineConfig())

    assert plan.allowed is True
    assert plan.stop_loss is not None and plan.stop_loss > plan.entry_price
    assert plan.take_profit is not None and plan.take_profit < plan.entry_price


def test_invalid_side_blocks_trade() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("HOLD", 2000.0, RiskEngineConfig())

    assert plan.allowed is False
    assert plan.blocking_reasons


def test_invalid_entry_price_blocks_trade() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("BUY", 0.0, RiskEngineConfig())

    assert plan.allowed is False
    assert any("Entry price" in reason for reason in plan.blocking_reasons)


def test_invalid_account_balance_blocks_trade() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("BUY", 2000.0, RiskEngineConfig(account_balance=0.0))

    assert plan.allowed is False
    assert any("Account balance" in reason for reason in plan.blocking_reasons)


def test_invalid_risk_percent_blocks_trade() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("BUY", 2000.0, RiskEngineConfig(risk_per_trade_percent=0.0))

    assert plan.allowed is False
    assert any("Risk per trade percent" in reason for reason in plan.blocking_reasons)


def test_volume_calculation_works() -> None:
    engine = RiskEngine()
    config = RiskEngineConfig(
        account_balance=10000.0,
        risk_per_trade_percent=1.0,
        default_stop_distance=10.0,
        point_value=1.0,
        min_volume=0.01,
        max_volume=20.0,
    )

    plan = engine.create_plan("BUY", 2000.0, config)

    assert plan.allowed is True
    assert plan.risk_amount == 100.0
    assert plan.risk_per_unit == 10.0
    assert plan.volume == 10.0


def test_volume_is_capped_by_max_volume() -> None:
    engine = RiskEngine()
    config = RiskEngineConfig(
        account_balance=100000.0,
        risk_per_trade_percent=5.0,
        default_stop_distance=10.0,
        point_value=1.0,
        min_volume=0.01,
        max_volume=10.0,
    )

    plan = engine.create_plan("BUY", 2000.0, config)

    assert plan.allowed is True
    assert plan.volume == 10.0
    assert any("max_volume" in reason for reason in plan.reasons)


def test_explain_returns_readable_text() -> None:
    engine = RiskEngine()
    plan = engine.create_plan("BUY", 2000.0, RiskEngineConfig())
    text = engine.explain(plan)

    assert "Risk plan" in text
    assert "side=BUY" in text
