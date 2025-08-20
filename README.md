# Excel Translate
 
[![CI](https://github.com/shadil-rayyan/excel-translate/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/shadil-rayyan/excel-translate/actions/workflows/ci.yml)
[![Release build](https://github.com/shadil-rayyan/excel-translate/actions/workflows/release.yml/badge.svg)](https://github.com/shadil-rayyan/excel-translate/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/shadil-rayyan/excel-translate?sort=semver)](https://github.com/shadil-rayyan/excel-translate/releases)
[![Downloads](https://img.shields.io/github/downloads/shadil-rayyan/excel-translate/total)](https://github.com/shadil-rayyan/excel-translate/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](#installation)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-8A2BE2)](docs/BUILD.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint](https://img.shields.io/badge/lint-ruff-46A8F7)](https://github.com/astral-sh/ruff)

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

## Build & Distribution

- See `docs/BUILD.md` for production packaging details (Windows/macOS/Linux), including installers, DMG/AppImage, and optional code signing.
- CI builds artifacts on tag push. Create a release tag to publish installers and binaries:

```bash
git tag v1.0.0
git push origin v1.0.0
```

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
