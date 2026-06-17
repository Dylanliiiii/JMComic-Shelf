@echo off
setlocal
chcp 65001 >nul

set "OPTION_PATH=%~dp0jmcomic-option.yml"
set "JMCOMIC_EXE=%APPDATA%\Python\Python314\Scripts\jmcomic.exe"

if not exist "%JMCOMIC_EXE%" (
  echo Could not find jmcomic.exe:
  echo %JMCOMIC_EXE%
  echo.
  echo Try running:
  echo python -m jmcomic --help
  pause
  exit /b 1
)

echo Input album ids, separated by spaces.
echo Example: 211899 123456 p456
set /p "JM_ID=> "

if "%JM_ID%"=="" (
  echo No id entered.
  pause
  exit /b 1
)

"%JMCOMIC_EXE%" %JM_ID% --option="%OPTION_PATH%"
echo.
pause
