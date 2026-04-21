import pytest


def test_latex_escape_ampersand():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("Hello & World") == r"Hello \& World"


def test_latex_escape_percent():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("50% off") == r"50\% off"


def test_latex_escape_dollar():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("$10") == r"\$10"


def test_latex_escape_hash():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("C#") == r"C\#"


def test_latex_escape_underscore():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("foo_bar") == r"foo\_bar"


def test_latex_escape_backslash():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("a\\b") == r"a\textbackslash{}b"


def test_latex_escape_empty_string():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("") == ""


def test_latex_escape_no_special_chars():
    from app.api.routes.resumes import _latex_escape
    assert _latex_escape("Hello World") == "Hello World"
