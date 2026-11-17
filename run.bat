@echo off
title JVVNL Bill Fetcher

echo ==========================================
echo        JVVNL Bill Fetcher Starting
echo ==========================================
echo.

:: Check input file
if not exist input.xlsx (
    echo ERROR: input.xlsx not found in this folder.
    pause
    exit /b
)

:: Check requirements file
if not exist requirements.txt (
    echo ERROR: requirements.txt not found in this folder.
    pause
    exit /b
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b
)

:: Create venv first time
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv

    call venv\Scripts\activate

    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo.
echo Running bill fetcher...
python bill_fetcher.py

echo.
echo ==========================================
echo Finished.
echo Output saved as output.xlsx
echo ==========================================
pause