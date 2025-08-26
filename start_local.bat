@echo off
REM Route Screenshot Generator - Local Startup Script
REM This script starts the application locally without Docker

echo 🚀 Starting Route Screenshot Generator (Local Mode)...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist ".venv\Lib\site-packages\flask" (
    echo 📦 Installing dependencies...
    python -m pip install -r requirements.txt
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "screenshots" mkdir screenshots

REM Set environment variables
set SECRET_KEY=your-super-secret-key-change-this-in-production
echo 🔑 Using default SECRET_KEY

REM Start the application
echo 🚀 Starting application...
echo.
echo ⚠️  IMPORTANT: Chrome browser will open for cookie consent handling
echo    Please accept/reject cookies when prompted for the first route
echo.
python app.py

pause
