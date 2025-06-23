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
    echo.
    echo Download Python from: https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if config.py exists
if not exist config.py (
    echo ❌ config.py not found!
    echo Please make sure config.py exists and is configured properly.
    echo.
    echo Run 'python setup.py' first to validate your setup.
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist bot_data.json (
    echo 📦 First time setup - Installing requirements...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install requirements!
        echo Please run 'python setup.py' for troubleshooting.
        pause
        exit /b 1
    )
    echo ✅ Requirements installed successfully!
    echo.
)

echo 🚀 Starting Advanced Pterodactyl Backup Bot...
echo ⏰ Started at: %date% %time%
echo 📁 Working directory: %cd%
echo.

REM Run the bot
python main.py

REM Handle exit status
if %errorlevel% neq 0 (
    echo.
    echo ❌ Bot stopped with error code: %errorlevel%
    echo 📞 For troubleshooting, check:
    echo    • bot_backup.log file for detailed logs
    echo    • Your internet connection
    echo    • API keys in config.py
    echo    • Pterodactyl panel accessibility
    pause
) else (
    echo.
    echo ✅ Bot stopped normally.
)

echo.
echo 📊 Bot session ended at: %date% %time%
pause