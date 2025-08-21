#!/bin/bash

# Route Screenshot Generator Startup Script
# This script helps you start the application easily

echo "🚀 Starting Route Screenshot Generator..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Download from: https://docker.com"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is ready"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads screenshots chrome_profile

# Set environment variables if not set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="your-super-secret-key-change-this-in-production"
    echo "🔑 Using default SECRET_KEY (change this in production)"
fi

# Start the application
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Application is running!"
    echo ""
    echo "🌐 Access your application at:"
    echo "   http://localhost:5000"
    echo ""
    echo "📊 Monitor logs with:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop the application with:"
    echo "   docker-compose down"
    echo ""
    echo "🔄 Restart the application with:"
    echo "   ./start.sh"
else
    echo "❌ Failed to start services. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi 