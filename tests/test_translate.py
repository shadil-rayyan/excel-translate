from __future__ import annotations

import pandas as pd
import excel_translate.utils as utils
from excel_translate.translate import translate_dataframe_columns


def test_translate_dataframe_columns_monkeypatched(monkeypatch):
    def fake_translate(text: str, target_lang: str) -> str:
        return f"X {text} ({target_lang})"

    monkeypatch.setattr(utils, "translate_preserving_brackets", fake_translate)

    df = pd.DataFrame({"a": ["Hello {name}", "!!!", None]})
    stats = translate_dataframe_columns(df, ["a"], ["xx"])  # type: ignore[arg-type]

    # Only the first row should be considered attempted (string and not symbolic-only)
    assert stats["attempted"] == 1
    assert stats["changed"] == 1

    out = df["a_xx"].tolist()
    assert out[0].startswith("X Hello {name}") and "{name}" in out[0]
    assert out[1] == "!!!"  # unchanged symbolic-only
    assert pd.isna(out[2])  # None remains None
