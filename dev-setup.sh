#!/bin/bash

echo "========================================"
echo "MEDHASAKTHI Local Development Setup"
echo "========================================"

echo
echo "[1/6] Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✓ Docker found"
echo "✓ Node.js found"

echo
echo "[2/6] Starting database services..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

echo
echo "[3/6] Waiting for database to be ready..."
sleep 10

echo
echo "[4/6] Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend packages..."
    npm install
else
    echo "Frontend packages already installed"
fi
cd ..

echo
echo "[5/6] Installing backend dependencies (if needed)..."
echo "Backend dependencies will be installed in Docker container"

echo
echo "[6/6] Setup complete!"
echo
echo "========================================"
echo "🚀 DEVELOPMENT ENVIRONMENT READY"
echo "========================================"
echo
echo "To start development:"
echo "  1. Backend:  npm run dev:backend"
echo "  2. Frontend: npm run dev:frontend"
echo
echo "Available URLs:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8080"
echo "  - API Docs:  http://localhost:8080/docs"
echo
echo "To stop services: npm run dev:stop"
echo "========================================"
