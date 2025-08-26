@echo off
REM Full Route Screenshot Generator Startup Script
REM This script starts Redis, Celery worker, and the Flask application

echo 🚀 Starting Route Screenshot Generator (Full Version)...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo.
    echo 📋 Steps to start Docker Desktop:
    echo    1. Open Docker Desktop from Start Menu
    echo    2. Wait for Docker to start (you'll see the whale icon in taskbar)
    echo    3. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Start Redis container
echo 📦 Starting Redis...
docker run -d --name redis-server -p 6379:6379 redis:7-alpine
if errorlevel 1 (
    echo ⚠️  Redis container already exists, starting it...
    docker start redis-server
)

echo ✅ Redis started on localhost:6379

REM Wait a moment for Redis to be ready
echo ⏳ Waiting for Redis to be ready...
timeout /t 3 /nobreak >nul

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "screenshots" mkdir screenshots

REM Start Celery worker in background
echo 🔄 Starting Celery worker...
start "Celery Worker" cmd /k "cd /d %CD% && .venv\Scripts\activate && celery -A app_with_celery.celery worker --loglevel=info --pool=solo"

REM Wait for worker to start
echo ⏳ Waiting for Celery worker to start...
timeout /t 5 /nobreak >nul

REM Start Flask application
echo 🌐 Starting Flask application...
echo.
echo 🎯 Your application will be available at: http://localhost:5000
echo 📊 Redis is running on: localhost:6379
echo 🔄 Celery worker is running in background
echo.
echo 🛑 To stop everything:
echo    - Press Ctrl+C to stop Flask
echo    - Close the Celery worker window
echo    - Run: docker stop redis-server
echo.

.venv\Scripts\activate
python app_with_celery.py
