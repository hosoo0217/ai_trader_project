from storage.trade_journal import TradeJournal, TradeJournalEntry
from ai.trade_reviewer import TradeReviewer


def make_entry(
    trade_id: str,
    executed: bool,
    confidence: float,
    reasons: list[str] | None = None,
    blocking_reasons: list[str] | None = None,
    pnl: float | None = None,
) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id=trade_id,
        symbol="XAUUSD",
        action="BUY",
        executed=executed,
        entry_price=2000.0,
        volume=1.0,
        stop_loss=1980.0,
        take_profit=2050.0,
        decision_confidence=confidence,
        reasons=reasons or [],
        blocking_reasons=blocking_reasons or [],
        status="EXECUTED" if executed else "BLOCKED",
        pnl=pnl,
    )


def test_high_confidence_executed_trade_gets_a_grade() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(make_entry("t1", True, 90.0, reasons=["Trend aligned"], pnl=25.0))

    assert review.grade == "A"
    assert "strong confidence" in review.summary.lower()
    assert "Trend aligned" in review.strengths


def test_medium_confidence_executed_trade_gets_b_grade() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(make_entry("t2", True, 75.0, reasons=["Acceptable setup"], pnl=10.0))

    assert review.grade == "B"
    assert "acceptable confidence" in review.summary.lower()
    assert "Acceptable setup" in review.strengths


def test_low_confidence_executed_trade_gets_c_grade() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(make_entry("t3", True, 60.0, reasons=["Weak confirmation"], pnl=-5.0))

    assert review.grade == "C"
    assert "weak confidence" in review.summary.lower()
    assert "Weak confirmation" in review.strengths


def test_blocked_trade_gets_no_trade_grade() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(
        make_entry(
            "t4",
            False,
            80.0,
            blocking_reasons=["Capital protection blocked trading"],
        )
    )

    assert review.grade == "NO_TRADE"
    assert "no trade" in review.summary.lower()
    assert "Capital protection blocked trading" in review.weaknesses


def test_blocking_reasons_appear_in_review() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(
        make_entry(
            "t5",
            True,
            78.0,
            reasons=["Good structure"],
            blocking_reasons=["Confidence below threshold"],
            pnl=None,
        )
    )

    assert "Confidence below threshold" in review.risk_notes
    assert "Confidence below threshold" in review.weaknesses


def test_review_journal_returns_review_list() -> None:
    reviewer = TradeReviewer()
    journal = TradeJournal()
    journal.add_entry(make_entry("t6", True, 88.0, reasons=["Clean trend"], pnl=20.0))
    journal.add_entry(make_entry("t7", False, 85.0, blocking_reasons=["Risk filters blocked the setup"]))

    reviews = reviewer.review_journal(journal)

    assert len(reviews) == 2
    assert reviews[0].trade_id == "t6"
    assert reviews[1].grade == "NO_TRADE"


def test_explain_review_returns_readable_text() -> None:
    reviewer = TradeReviewer()
    review = reviewer.review_entry(make_entry("t8", True, 92.0, reasons=["Excellent setup"], pnl=30.0))

    text = reviewer.explain_review(review)

    assert "Grade: A" in text
    assert "Excellent setup" in text
    assert review.lesson in text
