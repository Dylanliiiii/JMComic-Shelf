@echo off
setlocal
chcp 65001 >nul

set "PROJECT_DIR=%~dp0"
set "PYTHONPATH=%PROJECT_DIR%src"
set "JMCOMIC_SHELF_PROJECT_DIR=%PROJECT_DIR%"

python -m jmcomic_shelf.app

if errorlevel 1 (
  echo.
  echo Failed to start JMComic Shelf desktop app.
  echo Current directory:
  echo %PROJECT_DIR%
  echo.
  echo Try running:
  echo python -m pip install -e "%PROJECT_DIR%"
  echo.
  pause
  exit /b 1
)
