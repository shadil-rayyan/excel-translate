from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from excel_translate.files import find_excel_files, scan_columns_from_first_file


def make_xlsx(path: Path, cols: list[str]) -> None:
    df = pd.DataFrame([{c: f"val_{i}_{c}" for c in cols} for i in range(2)])
    df.to_excel(path, index=False)


def test_find_excel_files_and_scan_columns(tmp_path: Path):
    # Create files and non-xlsx files
    d = tmp_path / "in"
    d.mkdir()
    f1 = d / "a.xlsx"
    f2 = d / "b.xlsx"
    f3 = d / "c.txt"

    make_xlsx(f1, ["col1", "col2"])
    make_xlsx(f2, ["colA"])
    f3.write_text("ignore")

    # Explicit files + folder recursive False
    res = find_excel_files([str(f1), str(f3)], str(d), recursive=False)
    assert str(f1) in res
    assert str(f2) in res  # discovered via folder
    assert str(f3) not in res

    # Columns from first file
    cols = scan_columns_from_first_file(res)
    assert cols == ["col1", "col2"]
