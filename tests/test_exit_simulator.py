import pandas as pd

from broker.paper_broker import PaperPosition
from core.exit_simulator import ExitSimulationConfig, ExitSimulator


def make_candles(rows: list[dict[str, float | str]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def make_position(side: str, entry_price: float, stop_loss: float | None = None, take_profit: float | None = None) -> PaperPosition:
    return PaperPosition(
        position_id="pos-1",
        symbol="XAUUSD",
        side=side,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        volume=1.0,
    )


def test_buy_take_profit_hit() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 110.0, "low": 99.0, "close": 109.0},
    ])
    position = make_position("BUY", 100.0, stop_loss=95.0, take_profit=110.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exited is True
    assert result.exit_reason == "TAKE_PROFIT"
    assert result.exit_price == 110.0
    assert result.pnl == 10.0
    assert result.candle_index == 0


def test_buy_stop_loss_hit() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 101.0, "low": 90.0, "close": 91.0},
    ])
    position = make_position("BUY", 100.0, stop_loss=95.0, take_profit=110.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "STOP_LOSS"
    assert result.exit_price == 95.0
    assert result.pnl == -5.0


def test_sell_take_profit_hit() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 101.0, "low": 89.0, "close": 90.0},
    ])
    position = make_position("SELL", 100.0, stop_loss=110.0, take_profit=90.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "TAKE_PROFIT"
    assert result.exit_price == 90.0
    assert result.pnl == 10.0


def test_sell_stop_loss_hit() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 115.0, "low": 99.0, "close": 114.0},
    ])
    position = make_position("SELL", 100.0, stop_loss=110.0, take_profit=90.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "STOP_LOSS"
    assert result.exit_price == 110.0
    assert result.pnl == -10.0


def test_same_candle_conservative_chooses_stop_loss() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 106.0, "low": 90.0, "close": 95.0},
    ])
    position = make_position("BUY", 100.0, stop_loss=95.0, take_profit=105.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "STOP_LOSS"
    assert result.exit_price == 95.0


def test_missing_candle_columns_returns_invalid_candles() -> None:
    simulator = ExitSimulator()
    candles = pd.DataFrame([{"time": "t1", "close": 100.0}])
    position = make_position("BUY", 100.0, stop_loss=95.0, take_profit=110.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "INVALID_CANDLES"
    assert result.exited is False


def test_position_without_sl_tp_remains_still_open() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0},
    ])
    position = make_position("BUY", 100.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())

    assert result.exit_reason == "STILL_OPEN"
    assert result.exited is False
    assert result.pnl is None


def test_close_at_final_candle_closes_position() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0},
    ])
    position = make_position("BUY", 100.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig(close_at_final_candle=True))

    assert result.exit_reason == "FINAL_CANDLE"
    assert result.exited is True
    assert result.exit_price == 100.0
    assert result.pnl == 0.0


def test_explain_returns_readable_text() -> None:
    simulator = ExitSimulator()
    candles = make_candles([
        {"time": "t1", "open": 100.0, "high": 110.0, "low": 99.0, "close": 109.0},
    ])
    position = make_position("BUY", 100.0, stop_loss=95.0, take_profit=110.0)

    result = simulator.simulate_exit(position, candles, ExitSimulationConfig())
    text = simulator.explain(result)

    assert "TAKE_PROFIT" in text
    assert "110.0" in text
