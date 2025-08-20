import re
from typing import Any

try:  # optional dependency guard
    from deep_translator import GoogleTranslator  # type: ignore
except Exception:  # pragma: no cover - exercised only when missing
    GoogleTranslator = None  # type: ignore[assignment]


__all__ = ["is_symbolic_only", "translate_preserving_brackets"]


def is_symbolic_only(text: Any) -> bool:
    """Return True if the text has no alphanumerics after removing placeholders.

    This helps avoid translating strings that are only punctuation or placeholders.
    Non-strings are treated as symbolic-only to avoid unnecessary translation.
    """
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r"\{[^}]+\}", "", text)
    cleaned = re.sub(r"[^\w]", "", cleaned)
    return len(cleaned.strip()) == 0


def translate_preserving_brackets(text: Any, target_lang: str) -> Any:
    """Translate text to target_lang while preserving {a}, {b} ... placeholders.

    On translator errors, returns the original text.
    Non-strings or symbolic-only strings are returned unchanged.
    """
    if not isinstance(text, str) or is_symbolic_only(text):
        return text
    try:
        placeholders = re.findall(r"\{[^}]+\}", text)
        masked_text = text
        for i, ph in enumerate(placeholders):
            masked_text = masked_text.replace(ph, f"___PLACEHOLDER_{i}___")

        if GoogleTranslator is None:
            return text

        translated = GoogleTranslator(source="en", target=target_lang).translate(masked_text)

        for i, ph in enumerate(placeholders):
            translated = translated.replace(f"___PLACEHOLDER_{i}___", ph)
        return translated
    except Exception:
        # On any error, return original text
        return text
