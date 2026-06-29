"""Unit tests for Sierra Chart footprint CSV importer."""

from __future__ import annotations

from io import StringIO

import pandas as pd

from orderflow.data_quality import OrderFlowDataQualityChecker, OrderFlowDataQualityConfig
from orderflow.delta_cvd import DeltaCVDAnalyzer, DeltaCVDConfig
from orderflow.footprint import FootprintAnalyzer
from orderflow.sierra_chart_importer import (
    SierraChartImportConfig,
    SierraChartImporter,
    build_resolved_column_map,
    normalize_column_name,
    resolve_column,
)


BAR_SUMMARY_CSV = """Date, Time, Open, High, Low, Last, Volume, # of Trades, OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume, Open, High, Low, Last, Delta, Finish, Volume, Volume / Sec
2026-6-21, 18:00:00.000000, 4163.9, 4174.7, 4151.4, 4173.2, 821, 647, 4165.8, 4166.4, 4163.0, 405, 416, 4163.9, 4174.7, 4151.4, 4173.2, 11, -20, 821, 3
2026-6-21, 18:05:00.000000, 4173.2, 4176.0, 4168.0, 4170.9, 300, 262, 4172.0, 4171.6, 4172.0, 138, 162, 4173.2, 4176.0, 4168.0, 4170.9, 24, -16, 300, 1
"""


def _bar_summary_dataframe() -> pd.DataFrame:
    return pd.read_csv(StringIO(BAR_SUMMARY_CSV))


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


def test_existing_sample_csv_still_imports_correctly() -> None:
    path = "data/sample_footprint_bullish.csv"

    candles = SierraChartImporter().load_csv(path, SierraChartImportConfig())

    assert len(candles) == 1
    assert len(candles[0].levels) == 4
    assert candles[0].delta() > 0.0


def test_uppercase_column_names_import_correctly() -> None:
    dataframe = _sample_dataframe().rename(
        columns={
            "time": "TIMESTAMP",
            "open": "OPEN",
            "high": "HIGH",
            "low": "LOW",
            "close": "CLOSE",
            "price": "PRICE",
            "bid_volume": "BID_VOLUME",
            "ask_volume": "ASK_VOLUME",
        }
    )

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[0].delta() == 40.0


def test_sierra_style_column_names_import_correctly() -> None:
    dataframe = _sample_dataframe().rename(
        columns={
            "time": "Date Time",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Last",
            "price": "Price",
            "bid_volume": "Bid Volume",
            "ask_volume": "Ask Volume",
        }
    )

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[0].close == 101.0
    assert candles[1].delta() == -30.0


def test_mixed_case_columns_import_correctly() -> None:
    dataframe = _sample_dataframe().rename(
        columns={
            "time": "DateTime",
            "open": "Open",
            "high": "HIGH",
            "low": "low",
            "close": "last",
            "price": "Level",
            "bid_volume": "Bid",
            "ask_volume": "ask_vol",
        }
    )

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[0].levels[0].price == 100.0
    assert candles[0].levels[0].bid_volume == 10.0
    assert candles[0].levels[0].ask_volume == 20.0


def test_missing_required_alias_columns_returns_empty_list() -> None:
    dataframe = _sample_dataframe().drop(columns=["ask_volume"])

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert candles == []


def test_normalization_ignores_spaces_and_underscores() -> None:
    assert normalize_column_name(" Bid Volume ") == "bidvolume"
    assert normalize_column_name("bid_volume") == "bidvolume"
    assert normalize_column_name("BID VOLUME") == "bidvolume"


def test_resolve_column_ignores_spaces_underscores_and_case() -> None:
    resolved = resolve_column(["Date Time", "Bid Volume"], ["date_time"])

    assert resolved == "Date Time"


def test_build_resolved_column_map_returns_normalized_fields() -> None:
    dataframe = _sample_dataframe().rename(columns={"time": "Date Time", "bid_volume": "Bid Volume"})

    column_map = build_resolved_column_map(dataframe, SierraChartImportConfig())

    assert column_map["time"] == "Date Time"
    assert column_map["bid_volume"] == "Bid Volume"
    assert column_map["ask_volume"] == "ask_volume"


def test_sierra_chart_template_csv_imports_successfully() -> None:
    candles = SierraChartImporter().load_csv(
        "data/sierra_chart_footprint_template.csv",
        SierraChartImportConfig(),
    )

    assert len(candles) == 2
    assert len(candles[0].levels) == 3
    assert len(candles[1].levels) == 3


def test_sierra_chart_template_csv_passes_data_quality() -> None:
    candles = SierraChartImporter().load_csv(
        "data/sierra_chart_footprint_template.csv",
        SierraChartImportConfig(),
    )

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    assert result.passed is True
    assert result.status == "PASSED"
    assert result.candle_count == 2
    assert result.total_levels == 6


def test_sierra_chart_bar_summary_csv_imports_candles() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[0].time == "2026-6-21 18:00:00.000000"
    assert candles[0].open == 4163.9
    assert candles[0].high == 4174.7
    assert candles[0].low == 4151.4
    assert candles[0].close == 4173.2
    assert candles[0].source_format == "BAR_SUMMARY"


def test_sierra_chart_bar_summary_creates_one_synthetic_close_level() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    assert len(candles[0].levels) == 1
    assert candles[0].levels[0].price == 4173.2
    assert "not full price-level footprint data" in str(candles[0].source_note)


def test_sierra_chart_bar_summary_reads_bid_and_ask_volume() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    assert candles[0].levels[0].bid_volume == 405.0
    assert candles[0].levels[0].ask_volume == 416.0
    assert candles[1].levels[0].bid_volume == 138.0
    assert candles[1].levels[0].ask_volume == 162.0
    assert candles[0].reported_volume == 821.0
    assert candles[0].reported_delta == 11.0


def test_sierra_chart_bar_summary_duplicate_ohlc_headers_do_not_crash() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    assert len(candles) == 2
    assert candles[1].open == 4173.2
    assert candles[1].high == 4176.0
    assert candles[1].low == 4168.0
    assert candles[1].close == 4170.9


def test_sierra_chart_bar_summary_delta_cvd_can_be_calculated() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig(strong_delta_threshold=10.0))

    assert result.final_cvd == 35.0
    assert result.latest_delta == 24.0
    assert result.latest_direction == "BUYING_PRESSURE"


def test_sierra_chart_bar_summary_data_quality_notes_limited_format() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())

    assert result.passed is True
    assert result.status == "PASSED"
    assert any("BAR_SUMMARY" in reason for reason in result.reasons)


def test_sierra_chart_bar_summary_missing_required_columns_fails_safely() -> None:
    dataframe = _bar_summary_dataframe()
    bid_columns = [column for column in dataframe.columns if normalize_column_name(column) == "bidvolume"]
    dataframe = dataframe.drop(columns=bid_columns)

    candles = SierraChartImporter().from_dataframe(dataframe, SierraChartImportConfig())

    assert candles == []


def test_sierra_chart_bar_summary_explain_import_mentions_limited_format() -> None:
    candles = SierraChartImporter().from_dataframe(_bar_summary_dataframe(), SierraChartImportConfig())

    text = SierraChartImporter().explain_import(candles)

    assert "source=BAR_SUMMARY" in text
    assert "not full price-level footprint data" in text
