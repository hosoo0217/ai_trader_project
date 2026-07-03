"""Tests for diagnostic-only Sierra Chart bulk validation helpers."""

from __future__ import annotations

from analysis.bulk_sierra_validation import (
    build_bulk_validation_summary,
    parse_sierra_footprint_csv,
    parse_sierra_market_csv,
    split_rows_by_session_date,
)


FOOTPRINT_CSV = """DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
2026-06-01 18:00:00,0,4100.0,1,2,3,1,2
2026-06-01 18:00:00,0,4100.1,2,3,5,1,3
2026-06-01 18:01:00,1,4100.2,3,4,7,1,4
2026-06-02 18:00:00,2,4101.0,1,1,2,0,1
"""


MARKET_CSV = """Date,Time,Open,High,Low,Last,Volume
2026-06-01,18:00:00.000000,4100.0,4101.0,4099.0,4100.5,100
2026-06-01,18:01:00.000000,4100.5,4101.5,4100.0,4101.0,120
2026-06-02,18:00:00.000000,4101.0,4102.0,4100.0,4101.5,90
"""


OVERNIGHT_FOOTPRINT_CSV = """DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades
2026-07-02 18:00:00,0,4200.0,1,2,3,1,2
2026-07-02 23:59:00,1,4200.5,2,3,5,1,3
2026-07-03 00:01:00,2,4201.0,3,4,7,1,4
2026-07-03 08:45:00,3,4201.5,1,1,2,0,1
"""


OVERNIGHT_MARKET_CSV = """Date,Time,Open,High,Low,Last,Volume
2026-07-02,18:00:00.000000,4200.0,4201.0,4199.0,4200.5,100
2026-07-02,23:59:00.000000,4200.5,4201.5,4200.0,4201.0,120
2026-07-03,00:01:00.000000,4201.0,4202.0,4200.5,4201.5,90
2026-07-03,08:45:00.000000,4201.5,4202.5,4201.0,4202.0,80
"""


def test_parses_sierra_footprint_rows_by_datetime() -> None:
    rows = parse_sierra_footprint_csv(FOOTPRINT_CSV)

    assert len(rows) == 4
    assert rows[0].timestamp.isoformat(sep=" ") == "2026-06-01 18:00:00"
    assert rows[0].raw["Price"] == "4100.0"


def test_parses_sierra_market_rows_by_date_and_time() -> None:
    rows = parse_sierra_market_csv(MARKET_CSV)

    assert len(rows) == 3
    assert rows[0].timestamp.isoformat(sep=" ") == "2026-06-01 18:00:00"
    assert rows[1].raw["Last"] == "4101.0"


def test_splits_rows_into_daily_session_groups() -> None:
    sessions = split_rows_by_session_date(parse_sierra_footprint_csv(FOOTPRINT_CSV))

    assert [session.session_date for session in sessions] == ["2026-06-01", "2026-06-02"]
    assert sessions[0].start.isoformat(sep=" ") == "2026-06-01 18:00:00"
    assert sessions[0].end.isoformat(sep=" ") == "2026-06-01 18:01:00"
    assert sessions[0].row_count == 3


def test_splits_overnight_futures_rows_into_one_session_by_default() -> None:
    sessions = split_rows_by_session_date(parse_sierra_footprint_csv(OVERNIGHT_FOOTPRINT_CSV))

    assert len(sessions) == 1
    assert sessions[0].session_date == "2026-07-02"
    assert sessions[0].start.isoformat(sep=" ") == "2026-07-02 18:00:00"
    assert sessions[0].end.isoformat(sep=" ") == "2026-07-03 08:45:00"
    assert sessions[0].row_count == 4


def test_supports_configurable_session_start_hour() -> None:
    csv_text = """DateTime,BarIndex,Price,BidVolume,AskVolume
2026-07-02 17:00:00,0,4200.0,1,2
2026-07-03 16:59:00,1,4201.0,2,3
2026-07-03 17:00:00,2,4202.0,3,4
"""

    sessions = split_rows_by_session_date(
        parse_sierra_footprint_csv(csv_text),
        session_start_hour=17,
    )

    assert [session.session_date for session in sessions] == ["2026-07-02", "2026-07-03"]
    assert sessions[0].row_count == 2
    assert sessions[1].row_count == 1


def test_matches_market_and_footprint_sessions_by_common_start_end() -> None:
    summaries = build_bulk_validation_summary(MARKET_CSV, FOOTPRINT_CSV)

    assert len(summaries) == 2
    assert summaries[0].session_date == "2026-06-01"
    assert summaries[0].status == "MATCHED"
    assert summaries[0].start.isoformat(sep=" ") == "2026-06-01 18:00:00"
    assert summaries[0].end.isoformat(sep=" ") == "2026-06-01 18:01:00"
    assert summaries[0].market_row_count == 2
    assert summaries[0].footprint_row_count == 3


def test_matches_overnight_market_and_footprint_as_one_session_by_default() -> None:
    summaries = build_bulk_validation_summary(OVERNIGHT_MARKET_CSV, OVERNIGHT_FOOTPRINT_CSV)

    assert len(summaries) == 1
    assert summaries[0].session_date == "2026-07-02"
    assert summaries[0].status == "MATCHED"
    assert summaries[0].start.isoformat(sep=" ") == "2026-07-02 18:00:00"
    assert summaries[0].end.isoformat(sep=" ") == "2026-07-03 08:45:00"
    assert summaries[0].market_row_count == 4
    assert summaries[0].footprint_row_count == 4


def test_detects_mismatched_session_time_window() -> None:
    market_csv = """Date,Time,Open,High,Low,Last
2026-06-01,18:00:00.000000,4100.0,4101.0,4099.0,4100.5
2026-06-01,18:02:00.000000,4100.5,4101.5,4100.0,4101.0
"""

    summaries = build_bulk_validation_summary(market_csv, FOOTPRINT_CSV)

    assert summaries[0].status == "MISMATCHED"
    assert "Session start/end differ" in summaries[0].reasons


def test_detects_missing_market_or_footprint_session() -> None:
    market_csv = """Date,Time,Open,High,Low,Last
2026-06-03,18:00:00.000000,4100.0,4101.0,4099.0,4100.5
"""

    summaries = build_bulk_validation_summary(market_csv, FOOTPRINT_CSV)
    statuses = {summary.session_date: summary.status for summary in summaries}

    assert statuses["2026-06-01"] == "MISSING_MARKET"
    assert statuses["2026-06-02"] == "MISSING_MARKET"
    assert statuses["2026-06-03"] == "MISSING_FOOTPRINT"


def test_detects_bad_unparseable_rows_without_private_data() -> None:
    bad_footprint_csv = """DateTime,BarIndex,Price,BidVolume,AskVolume
not-a-date,0,4100.0,1,2
2026-06-01 18:00:00,1,4100.1,2,3
"""

    summaries = build_bulk_validation_summary(MARKET_CSV, bad_footprint_csv)

    assert summaries[0].status == "MISMATCHED"
    assert summaries[0].footprint_bad_row_count == 1
    assert "Footprint CSV has 1 bad timestamp row" in summaries[0].reasons
