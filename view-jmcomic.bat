@echo off
setlocal
chcp 65001 >nul

set "OPTION_PATH=%~dp0jmcomic-option.yml"
set "JMV_EXE=%APPDATA%\Python\Python314\Scripts\jmv.exe"

if not exist "%JMV_EXE%" (
  echo Could not find jmv.exe:
  echo %JMV_EXE%
  pause
  exit /b 1
)

echo Input album id, for example: 211899
set /p "JM_ID=> "

if "%JM_ID%"=="" (
  echo No id entered.
  pause
  exit /b 1
)

"%JMV_EXE%" %JM_ID% --option="%OPTION_PATH%"
echo.
pause
