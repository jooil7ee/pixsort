@echo off
rem pixsort GUI 실행 래퍼 스크립트 (Windows)

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

where uv >nul 2>&1
if errorlevel 1 (
    echo 오류: uv 가 설치되어 있지 않습니다. https://docs.astral.sh/uv/
    pause
    exit /b 1
)

uv run python main.py gui
if errorlevel 1 (
    pause
)
