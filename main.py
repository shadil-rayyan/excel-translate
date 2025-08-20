import os
import re
import glob
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from excel_translate.gui import launch_gui as _launch_gui
import pandas as pd
# deep_translator is imported lazily in excel_translate.gui/utils; not needed here

# -----------------------------
# Utilities
# -----------------------------

def is_symbolic_only(text: str) -> bool:
    """Return True if the text has no alphanumerics after removing placeholders.
    This helps avoid translating strings that are only punctuation or placeholders.
    """
    if not isinstance(text, str):
        return True
    cleaned = re.sub(r"\{[^}]+\}", "", text)
    cleaned = re.sub(r"[^\w]", "", cleaned)
    return len(cleaned.strip()) == 0


def translate_preserving_brackets(text: str, target_lang: str) -> str:
    """Translate text to target_lang while preserving {a}, {b} ... placeholders."""
    if not isinstance(text, str) or is_symbolic_only(text):
        return text
    try:
        placeholders = re.findall(r"\{[^}]+\}", text)
        masked_text = text
        for i, ph in enumerate(placeholders):
            masked_text = masked_text.replace(ph, f"___PLACEHOLDER_{i}___")

        translated = GoogleTranslator(source='en', target=target_lang).translate(masked_text)

        for i, ph in enumerate(placeholders):
            translated = translated.replace(f"___PLACEHOLDER_{i}___", ph)
        return translated
    except Exception:
        # On any error, return original text
        return text


def find_excel_files(selected_files, selected_folder, recursive: bool) -> list:
    """Return a de-duplicated list of .xlsx files from inputs."""
    files = []
    # Explicit files (tuple from askopenfilenames)
    if selected_files:
        files.extend([p for p in selected_files if p.lower().endswith('.xlsx')])

    # From folder
    if selected_folder:
        pattern = "**/*.xlsx" if recursive else "*.xlsx"
        folder_glob = glob.glob(os.path.join(selected_folder, pattern), recursive=recursive)
        files.extend(folder_glob)

    # De-duplicate preserving order
    seen = set()
    unique = []
    for p in files:
        if p not in seen:
            unique.append(p)
            seen.add(p)
    return unique


def scan_columns_from_first_file(file_paths: list) -> list:
    """Read the first file's first sheet columns as the default column set."""
    if not file_paths:
        return []
    try:
        # Read first sheet only to keep it quick
        df = pd.read_excel(file_paths[0], sheet_name=0)
        return list(df.columns)
    except Exception:
        return []


def translate_dataframe_columns(df: pd.DataFrame, columns: list, lang_codes: list) -> dict:
    """Translate selected columns in df into each language and return basic stats.

    Returns stats dict with totals.
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
                if isinstance(val, str) and not is_symbolic_only(val):
                    attempted += 1
                    t = translate_preserving_brackets(val, lang)
                    if t != val:
                        changed += 1
                    return t
                return val
            df[out_col] = df[col].apply(_tx)
    return {"attempted": attempted, "changed": changed}


# -----------------------------
# GUI
# -----------------------------

launch_gui = _launch_gui

if __name__ == "__main__":
    launch_gui()
