# Excel Translate

A small, polished Excel translation tool with a Tkinter GUI. Batch-translates selected columns in one or more `.xlsx` files into multiple languages using `deep-translator`, preserving `{placeholders}` like `{name}`.

## Features

- Minimal, clean code split into small modules under `excel_translate/`
- GUI workflow to select files/folder, scan columns, choose target languages, and export
- Placeholder-safe translation via `translate_preserving_brackets()`
- Preserves multiple sheets per workbook
- Tests with `pytest`

## Installation

Use Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional for development
pip install -r requirements-dev.txt
```

## Usage

Run the app:

```bash
python main.py
```

## Development

- Run tests: `pytest`
- Lint/format: `ruff check . && black .`

## Project Layout

- `excel_translate/utils.py` — text utils and translation wrapper
- `excel_translate/files.py` — input discovery and column scanning
- `excel_translate/translate.py` — DataFrame column translation
- `excel_translate/gui.py` — Tkinter UI wired to the helpers
- `tests/` — unit tests for key modules

## Notes

- Network connectivity is required for live translation via GoogleTranslator.
- If language list fetch fails, a small fallback set is used.
- Tkinter ships with CPython; you usually don't install a `tk` PyPI package. On Linux you may need system packages like `python3-tk`.
