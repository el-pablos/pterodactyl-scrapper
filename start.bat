@echo off
title Advanced Pterodactyl Backup Bot
color 0a

echo.
echo ========================================
echo    Advanced Pterodactyl Backup Bot
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.7+ first.
    pause
    exit /b 1
)

REM Check if config.py exists
if not exist config.py (
    echo ❌ config.py not found!
    echo Please edit config.py with your settings first.
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist bot_data.json (
    echo 📦 Installing requirements...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install requirements!
        pause
        exit /b 1
    )
)

echo 🚀 Starting bot...
echo.

REM Run the bot
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Bot stopped with error!
    pause
)

echo.
echo Bot stopped.
pause