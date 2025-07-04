@echo off
title SRT Format Fixer

echo ========================================
echo    SRT FORMAT FIXER
echo    Fix SRT file format errors
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found
echo [INFO] Starting SRT Fixer...
echo.

REM Run Python script
python fix_srt.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Error occurred while running script!
    pause
    exit /b 1
)

echo.
echo [INFO] Script completed
pause
