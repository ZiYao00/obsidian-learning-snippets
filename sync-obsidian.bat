@echo off
setlocal EnableExtensions

set "REPO_ROOT=%~dp0"
set "VAULT_ROOT=%~1"

if not defined VAULT_ROOT if exist "%REPO_ROOT%config\vault.local.txt" (
  set /p VAULT_ROOT=<"%REPO_ROOT%config\vault.local.txt"
)

if not defined VAULT_ROOT if defined OBSIDIAN_VAULT (
  set "VAULT_ROOT=%OBSIDIAN_VAULT%"
)

if not defined VAULT_ROOT (
  echo [ERROR] No Obsidian Vault path is configured.
  echo.
  echo Create this local file:
  echo   %REPO_ROOT%config\vault.local.txt
  echo.
  echo Put one line in it, for example:
  echo   D:\Notes\MyVault
  echo.
  echo Or run:
  echo   sync-obsidian.bat "D:\Notes\MyVault"
  echo.
  pause
  exit /b 2
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%scripts\sync-snippets.ps1" -VaultRoot "%VAULT_ROOT%"
set "SYNC_EXIT=%ERRORLEVEL%"

if not "%SYNC_EXIT%"=="0" (
  echo.
  echo [ERROR] Obsidian snippet sync failed with exit code %SYNC_EXIT%.
  pause
  exit /b %SYNC_EXIT%
)

echo.
echo [OK] Obsidian snippets synced to:
echo   %VAULT_ROOT%\.obsidian\snippets
echo.
pause
exit /b 0
