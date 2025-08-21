@echo off
REM Route Screenshot Generator Startup Script for Windows
REM This script helps you start the application easily

echo 🚀 Starting Route Screenshot Generator...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://docker.com
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is ready

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "screenshots" mkdir screenshots
if not exist "chrome_profile" mkdir chrome_profile

REM Set environment variables if not set
if "%SECRET_KEY%"=="" (
    set SECRET_KEY=your-super-secret-key-change-this-in-production
    echo 🔑 Using default SECRET_KEY (change this in production)
)

REM Start the application
echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Failed to start services. Check logs with:
    echo    docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Application is running!
    echo.
    echo 🌐 Access your application at:
    echo    http://localhost:5000
    echo.
    echo 📊 Monitor logs with:
    echo    docker-compose logs -f
    echo.
    echo 🛑 Stop the application with:
    echo    docker-compose down
    echo.
    echo 🔄 Restart the application with:
    echo    start.bat
    echo.
    pause
) 