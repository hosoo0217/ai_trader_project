from io import StringIO
from contextlib import redirect_stdout

import main


def test_main_runs_and_prints_title() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main()

    output = buffer.getvalue()
    assert "AI Trader Paper Trading Demo" in output
    assert "Market result" in output
