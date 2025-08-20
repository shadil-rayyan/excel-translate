; NSIS installer for ExcelTranslate
!include "MUI2.nsh"

!define APP_NAME "ExcelTranslate"
!define APP_PUBLISHER "Your Company"
!define APP_VERSION "1.0.0"
!define APP_EXE "ExcelTranslate.exe"
!define INSTALL_DIR "$PROGRAMFILES\${APP_NAME}"
!define OUT_FILE "packaging\\windows\\Output\\ExcelTranslateSetup-NSIS.exe"

Name "${APP_NAME}"
OutFile "${OUT_FILE}"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  ; Include everything from PyInstaller output
  File /r "dist\ExcelTranslate\*"

  ; Create shortcuts
  CreateShortCut "$SMPROGRAMS\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"

  ; Write uninstall information
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"

SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd
