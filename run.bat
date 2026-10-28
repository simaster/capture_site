@echo off
cd /d "%~dp0"

echo ===================================================
echo   Starting Web Capture Tool...
echo ===================================================

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    "%LOCALAPPDATA%\Python\bin\python.exe" run.py
) else (
    python run.py
)

if errorlevel 1 (
    echo.
    echo [Error] Program failed with exit code: %errorlevel%
    pause
)
