import types

import pytest

import excel_translate.utils as utils


class FakeTranslator:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target

    def translate(self, text: str) -> str:
        # Pretend translation that prefixes and keeps placeholders intact
        return f"X {text}"


def test_is_symbolic_only_basic():
    assert utils.is_symbolic_only(None) is True
    assert utils.is_symbolic_only(123) is True
    assert utils.is_symbolic_only("") is True
    assert utils.is_symbolic_only("!!!") is True
    assert utils.is_symbolic_only("{a}{b}") is True
    assert utils.is_symbolic_only("Hello") is False
    assert utils.is_symbolic_only("{name}!") is True


def test_translate_preserving_brackets_preserves_placeholders(monkeypatch):
    monkeypatch.setattr(utils, "GoogleTranslator", FakeTranslator)
    text = "Hello {name}!"
    out = utils.translate_preserving_brackets(text, "hi")
    # Our fake adds a prefix, and placeholders should be restored
    assert out.startswith("X ")
    assert "{name}" in out


def test_translate_preserving_brackets_skips_symbolic(monkeypatch):
    monkeypatch.setattr(utils, "GoogleTranslator", FakeTranslator)
    assert utils.translate_preserving_brackets("!!!", "hi") == "!!!"
    assert utils.translate_preserving_brackets(None, "hi") is None
