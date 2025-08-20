import glob
import os
from typing import List

import pandas as pd

__all__ = ["find_excel_files", "scan_columns_from_first_file"]


def find_excel_files(selected_files, selected_folder: str, recursive: bool) -> List[str]:
    """Return a de-duplicated list of .xlsx files from inputs.

    selected_files: list/tuple of explicit paths (e.g., from file dialog)
    selected_folder: base folder to search for xlsx files
    recursive: whether to search subdirectories
    """
    files: list[str] = []

    if selected_files:
        files.extend([p for p in selected_files if str(p).lower().endswith(".xlsx")])

    if selected_folder:
        pattern = "**/*.xlsx" if recursive else "*.xlsx"
        folder_glob = glob.glob(os.path.join(selected_folder, pattern), recursive=recursive)
        files.extend(folder_glob)

    seen = set()
    unique: list[str] = []
    for p in files:
        if p not in seen:
            unique.append(p)
            seen.add(p)
    return unique


def scan_columns_from_first_file(file_paths: list[str]) -> list[str]:
    """Read the first file's first sheet columns as the default column set."""
    if not file_paths:
        return []
    try:
        df = pd.read_excel(file_paths[0], sheet_name=0)
        return list(df.columns)
    except Exception:
        return []
