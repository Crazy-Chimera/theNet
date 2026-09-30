from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "ui"


def test_basic_ui_files_exist():
    assert (UI / "index.html").is_file()
    assert (UI / "styles.css").is_file()
    assert (UI / "app.js").is_file()


def test_ui_shell_references_assets():
    html = (UI / "index.html").read_text(encoding="utf-8")
    assert 'href="./styles.css"' in html
    assert 'src="./app.js"' in html
    assert 'id="genesis-form"' in html
    assert 'id="relation-form"' in html
    assert 'id="closure-form"' in html


def test_ui_uses_foundational_terms():
    html = (UI / "index.html").read_text(encoding="utf-8")
    app = (UI / "app.js").read_text(encoding="utf-8")
    assert "Genesis" in html
    assert "Relation" in html
    assert "Agent Ω" in html
    assert "/v1/genesis" in app
    assert "/v1/relations" in app
    assert "/v1/closure" in app
    assert "/v1/state" in app


def test_ui_does_not_add_runtime_dependencies():
    html = (UI / "index.html").read_text(encoding="utf-8")
    assert "cdn." not in html
    assert "unpkg.com" not in html
    assert "jsdelivr.net" not in html
