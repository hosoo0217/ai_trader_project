from src.codex_panel import build_codex_panel


def test_build_codex_panel_contains_key_sections():
    panel = build_codex_panel()

    assert "Codex Panel" in panel
    assert "Status" in panel
    assert "Modules" in panel
    assert "data loader" in panel
