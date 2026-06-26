from pathlib import Path

from src.backtester import run_backtest
from src.data_loader import load_candles
from src.strategy import generate_signals


def test_backtest_flow(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "time,open,high,low,close\n"
        "2024-01-01 00:00:00,10,10.5,9.8,10.0\n"
        "2024-01-01 01:00:00,10.0,10.6,9.9,10.1\n"
        "2024-01-01 02:00:00,10.1,10.7,10.0,10.2\n"
        "2024-01-01 03:00:00,10.2,10.8,10.1,10.3\n"
        "2024-01-01 04:00:00,10.3,10.9,10.2,10.4\n"
        "2024-01-01 05:00:00,10.4,11.0,10.3,10.5\n"
        "2024-01-01 06:00:00,10.5,11.1,10.4,10.6\n"
        "2024-01-01 07:00:00,10.6,11.2,10.5,10.7\n"
        "2024-01-01 08:00:00,10.7,11.3,10.6,10.8\n"
        "2024-01-01 09:00:00,10.8,11.4,10.7,10.9\n"
        "2024-01-01 10:00:00,10.9,11.5,10.8,11.0\n"
        "2024-01-01 11:00:00,11.0,11.6,10.9,11.1\n"
        "2024-01-01 12:00:00,11.1,11.7,11.0,11.2\n"
        "2024-01-01 13:00:00,11.2,11.8,11.1,11.3\n"
        "2024-01-01 14:00:00,11.3,11.9,11.2,11.4\n"
        "2024-01-01 15:00:00,11.4,12.0,11.3,11.5\n"
        "2024-01-01 16:00:00,11.5,12.1,11.4,11.6\n"
        "2024-01-01 17:00:00,11.6,12.2,11.5,11.7\n"
        "2024-01-01 18:00:00,11.7,12.3,11.6,11.8\n"
        "2024-01-01 19:00:00,11.8,12.4,11.7,11.9\n",
        encoding="utf-8",
    )

    candles = load_candles(csv_path)
    assert len(candles) == 20

    signals = generate_signals(candles)
    assert any(signal["action"] != "hold" for signal in signals)

    result = run_backtest(candles)
    assert result["trades"] >= 1
    assert result["final_equity"] > 0
