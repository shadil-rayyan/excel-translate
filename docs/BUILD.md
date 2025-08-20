# Build & Release Guide

This project ships a desktop GUI (Tkinter). You can build standalone executables and production installers.

Two options:
- GitHub Actions (recommended): tag a release and fetch artifacts.
- Local build: use PyInstaller (and Inno Setup on Windows for an installer).

## Prerequisites

- Python 3.12+
- Virtualenv recommended
- OS-specific:
  - Windows: Inno Setup (for installer) — https://jrsoftware.org/isinfo.php
  - macOS: Xcode CLT (for signing/notarization if desired)
  - Linux: build-essential, patchelf optional

## 1) Local Build with PyInstaller

Create a venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

Build executables:

- Windows GUI exe (no console window):

```bash
pyinstaller --noconfirm --clean --windowed \
  --name ExcelTranslate \
  --hidden-import excel_translate \
  main.py
```

- macOS app bundle:

```bash
pyinstaller --noconfirm --clean --windowed \
  --name ExcelTranslate \
  --hidden-import excel_translate \
  main.py
# Result: dist/ExcelTranslate.app
```

- Linux binary:

```bash
pyinstaller --noconfirm --clean --windowed \
  --name ExcelTranslate \
  --hidden-import excel_translate \
  main.py
# Result: dist/ExcelTranslate/ExcelTranslate
```

## 2) Windows Installer (Inno Setup)

After PyInstaller (which produces `dist/ExcelTranslate/ExcelTranslate.exe`), run Inno Setup:

```powershell
"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" packaging\\windows\\installer.iss
```

This generates `packaging\\windows\\Output\\ExcelTranslateSetup.exe` with:
- Install dir in Program Files
- Start Menu and Desktop shortcuts
- Uninstaller

You can customize icons and metadata in `packaging/windows/installer.iss`.

## 3) GitHub Actions: CI and Release

- CI workflow: `.github/workflows/ci.yml` runs lint and tests on pushes/PRs.
- Release workflow: `.github/workflows/release.yml` builds binaries for Windows/macOS/Linux and a Windows installer on tag push.

Create a release tag to trigger:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then check the GitHub Actions run and download artifacts from the Release page.

## 4) CI Artifacts and Install Instructions

Artifacts produced on tag push (`vX.Y.Z`) by `.github/workflows/release.yml`:

- Windows
  - Portable EXE: `dist/ExcelTranslate/ExcelTranslate.exe`
  - Inno Setup installer: `packaging/windows/Output/ExcelTranslateSetup.exe`
  - NSIS installer: `packaging/windows/Output/ExcelTranslateSetup-NSIS.exe`
- macOS
  - App bundle: `dist/ExcelTranslate.app`
  - DMG image: `ExcelTranslate.dmg`
- Linux
  - AppImage: `ExcelTranslate-<version>-x86_64.AppImage`
  - Debian package: `pkg/excel-translate_<version>_amd64.deb`
  - RPM package: `pkg/excel-translate-<version>-1.x86_64.rpm`

Install per OS:

- Windows
  - Run `ExcelTranslateSetup.exe` (Inno) or `ExcelTranslateSetup-NSIS.exe` (NSIS).
  - Silent install: Inno `/VERYSILENT /NORESTART`, NSIS `/S`.
  - App installs to `C:\Program Files\ExcelTranslate`, Start Menu + Desktop shortcuts included, uninstaller present.
- macOS
  - Open `ExcelTranslate.dmg`, drag `ExcelTranslate.app` to Applications.
  - If unsigned: right-click → Open once to bypass Gatekeeper (or enable signing—see below).
- Linux
  - AppImage: `chmod +x ExcelTranslate-*.AppImage && ./ExcelTranslate-*.AppImage`
  - Debian: `sudo dpkg -i pkg/excel-translate_*_amd64.deb` (then `sudo apt -f install` if deps)
  - RPM: `sudo rpm -i pkg/excel-translate-*-1.x86_64.rpm`
  - Installed binary at `/opt/excel-translate/ExcelTranslate` and a symlink `excel-translate` in PATH; desktop entry and icon registered.

Versioning:
- Artifact versions derive from the git tag name (e.g., `v1.0.0` → `1.0.0`).

## 5) Code Signing (optional, recommended for production)

Windows (Authenticode):
- Provide GitHub Secrets:
  - `WINDOWS_CERT_PFX_BASE64`: base64 of your `.pfx` (export with private key).
  - `WINDOWS_CERT_PASSWORD`: password for the PFX.
- The workflow signs the EXE and installers with `signtool` (timestamped SHA-256).

macOS (codesign + notarize):
- Provide GitHub Secrets:
  - `APPLE_ID`: Apple ID email
  - `APPLE_TEAM_ID`: 10-char Team ID
  - `APPLE_APP_SPECIFIC_PASSWORD`: App-specific password
  - `APPLE_SIGN_IDENTITY`: e.g., `Developer ID Application: Your Name (TEAMID)`
- Workflow signs the `.app` (hardened runtime) and submits the `.dmg` to Notary service.

Linux package signing (optional):
- Not enabled by default. You can add `dpkg-sig` (Deb) and `rpm-sign` (RPM) with your GPG key if needed.

## 6) Local Packaging Extras

- NSIS (Windows):
  ```powershell
  choco install nsis -y
  makensis packaging\windows\installer.nsi
  ```
- DMG (macOS):
  ```bash
  brew install create-dmg
  create-dmg --overwrite --volname "ExcelTranslate" ExcelTranslate.dmg dist/ExcelTranslate.app
  ```
- Deb/RPM (Linux) with fpm from local PyInstaller output:
  ```bash
  sudo gem install fpm
  # Assemble pkgroot with /opt/excel-translate contents and .desktop/icon, then run fpm as in the CI workflow
  ```

## 7) Release Checklist (top-tier quality)

- Ensure tests pass locally: `pytest -q`
- Update docs/CHANGELOG (if you keep one) and README screenshots/icons.
- Prepare branding assets: `icons/exceltranslate.png` (used for AppImage and Linux packages; also usable in installers/DMG).
- Set signing secrets in repo (Windows/macOS) if you want signed artifacts.
- Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
- Verify GitHub Release artifacts and that installers run cleanly on fresh VMs.
- Smoke-test: open the app, run a simple translation, verify file dialogs and outputs.

## 8) Branding

- Place app icon at `icons/exceltranslate.png` (256x256 recommended).
- Windows installer icons can be customized in `packaging/windows/installer.iss` and `packaging/windows/installer.nsi`.
- DMG background and icon can be themed via `create-dmg` options.

## 5) Troubleshooting

- Missing UI on Windows? Ensure `--windowed` and no antivirus interference.
- `deep-translator` network errors: app will fallback gracefully for language list but translation needs connectivity.
- Tkinter not found on Linux: install `python3-tk` via your distro package manager.
 - AppImage won't start: ensure it is executable (`chmod +x`) and `libfuse` is present on older distros.
 - macOS "app is damaged or can't be opened": this is Gatekeeper for unsigned apps—enable signing/notarization or use right-click → Open.
 - Debian/RPM install warnings about desktop database: harmless; the post-install script tries to refresh caches if available.
