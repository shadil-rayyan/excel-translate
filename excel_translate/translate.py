from __future__ import annotations

from typing import Dict, List

import pandas as pd

from . import utils

__all__ = ["translate_dataframe_columns"]


def translate_dataframe_columns(df: pd.DataFrame, columns: List[str], lang_codes: List[str]) -> Dict[str, int]:
    """Translate selected columns in df into each language and return basic stats.

    Returns a dict with keys: attempted, changed
    """
    attempted = 0
    changed = 0

    for col in columns:
        if col not in df.columns:
            continue
        for lang in lang_codes:
            out_col = f"{col}_{lang}"

            def _tx(val):
                nonlocal attempted, changed
                if isinstance(val, str) and not utils.is_symbolic_only(val):
                    attempted += 1
                    t = utils.translate_preserving_brackets(val, lang)
                    if t != val:
                        changed += 1
                    return t
                return val

            df[out_col] = df[col].apply(_tx)

    return {"attempted": attempted, "changed": changed}
