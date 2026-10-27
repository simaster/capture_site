@echo off
chcp 65001 > nul
echo ===================================================
echo [웹사이트 화면 자동 캡처 도구 (Web Capture Tool)]
echo ===================================================

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py
) else (
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        "%LOCALAPPDATA%\Python\bin\python.exe" run.py
    ) else (
        echo [오류] Python 실행 파일을 찾을 수 없습니다.
        pause
    )
)
