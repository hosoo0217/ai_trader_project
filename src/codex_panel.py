from __future__ import annotations


def build_codex_panel() -> str:
    """Return a simple text panel summarizing the project layout."""
    return "\n".join(
        [
            "========================",
            "Codex Panel",
            "========================",
            "Status: Ready",
            "Modules:",
            "- data loader",
            "- strategy",
            "- backtester",
            "========================",
        ]
    )
