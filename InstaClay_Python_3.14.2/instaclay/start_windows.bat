@echo off
setlocal
cd /d "%~dp0"
title InstaClay - Streamlit
if exist ".venv314\Scripts\python.exe" goto setup
py -3.14 -c "import sys; assert sys.version_info[:2] == (3,14)" >nul 2>nul
if not errorlevel 1 (
  py -3.14 -m venv .venv314
  if errorlevel 1 goto fail
  goto setup
)
python -c "import sys; assert sys.version_info[:2] == (3,14)" >nul 2>nul
if not errorlevel 1 (
  python -m venv .venv314
  if errorlevel 1 goto fail
  goto setup
)
echo Python 3.14 was not found. Install 64-bit Python 3.14 from python.org.
echo Enable Add python.exe to PATH during installation, then run this file again.
goto fail
:setup
".venv314\Scripts\python.exe" -c "import sys; assert sys.version_info[:2] == (3,14), 'This project requires Python 3.14. Rename .venv314 and run again.'"
if errorlevel 1 goto fail
".venv314\Scripts\python.exe" bootstrap.py %*
if errorlevel 1 goto fail
exit /b 0
:fail
echo.
echo InstaClay could not start. Read the error above and WINDOWS_SETUP.md.
pause
exit /b 1
