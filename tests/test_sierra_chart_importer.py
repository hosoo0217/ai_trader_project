"""Unit tests for Sierra Chart footprint CSV importer."""

from __future__ import annotations

import pandas as pd

from orderflow.footprint import FootprintAnalyzer
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter


def _sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "time": "2026-01-01 10:00:00",
                "open": 100.0,
                "high": 102.0,
                "low": 99.0,
                "close": 100.5,
                "price": 100.0,
                "bid_volume": 10.0,
                "ask_volume": 20.0,
            },
            {
                "time": "2026-01-01 10:00:00",
                "open": 100.2,
                "high": 103.0,
                "low": 98.0,
                "close": 101.0,
                "price": 101.0,
                "bid_volume": 5.0,
                "ask_volume": 35.0,
            },
            {
                "time": "2026-01-01 10:05:00",
                "open": 101.0,
                "high": 102.0,
                "low": 100.0,
                "close": 100.8,
                "price": 100.5,
                "bid_volume": 30.0,
                "ask_volume": 10.0,
            },
            {
                "time": "2026-01-01 10:05:00",
                "open": 101.1,
                "high": 104.0,
                "low": 99.5,
                "close": 100.0,
                "price": 100.0,
                "bid_volume": 20.0,
                "ask_volume": 10.0,
            },
        ]
    )


def test_imports_one_candle_with_multiple_price_levels() -> None:
    dataframe = _sample_dataframe().iloc[:2].copy()

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert len(candles) == 1
    assert len(candles[0].levels) == 2
    assert candles[0].open == 100.0
    assert candles[0].high == 103.0
    assert candles[0].low == 98.0
    assert candles[0].close == 101.0


def test_imports_multiple_candles() -> None:
    candles = SierraChartImporter().from_dataframe(_sample_dataframe(), SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[0].time == "2026-01-01 10:00:00"
    assert candles[1].time == "2026-01-01 10:05:00"


def test_calculates_candle_delta_correctly_after_import() -> None:
    candles = SierraChartImporter().from_dataframe(_sample_dataframe(), SierraChartImportConfig())

    assert candles[0].delta() == 40.0
    assert candles[1].delta() == -30.0


def test_calculates_point_of_control_through_footprint_analyzer() -> None:
    candles = SierraChartImporter().from_dataframe(_sample_dataframe(), SierraChartImportConfig())
    summary = FootprintAnalyzer().summarize(candles[0])

    assert summary.point_of_control == 101.0


def test_missing_columns_returns_empty_list() -> None:
    dataframe = pd.DataFrame({"time": ["2026-01-01"], "open": [1.0]})

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert candles == []


def test_empty_dataframe_returns_empty_list() -> None:
    dataframe = pd.DataFrame(
        columns=["time", "open", "high", "low", "close", "price", "bid_volume", "ask_volume"]
    )

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert candles == []


def test_negative_volume_handled_safely() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "time": "2026-01-01 10:00:00",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "price": 100.0,
                "bid_volume": -10.0,
                "ask_volume": -20.0,
            }
        ]
    )

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert len(candles) == 1
    assert candles[0].levels[0].bid_volume == 0.0
    assert candles[0].levels[0].ask_volume == 0.0


def test_explain_import_returns_readable_text() -> None:
    candles = SierraChartImporter().from_dataframe(_sample_dataframe(), SierraChartImportConfig())

    text = SierraChartImporter().explain_import(candles)

    assert "Sierra footprint import" in text
    assert "candles=2" in text


def test_load_csv_imports_data(tmp_path) -> None:
    dataframe = _sample_dataframe()
    path = tmp_path / "footprint.csv"
    dataframe.to_csv(path, index=False)

    candles = SierraChartImporter().load_csv(str(path), SierraChartImportConfig())

    assert len(candles) == 2
