@echo off
echo ========================================
echo MEDHASAKTHI Local Development Setup
echo ========================================

echo.
echo [1/6] Checking prerequisites...
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Docker found
echo ✓ Node.js found

echo.
echo [2/6] Starting database services...
docker-compose -f docker-compose.dev.yml up -d postgres redis

echo.
echo [3/6] Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [4/6] Installing frontend dependencies...
cd frontend
if not exist node_modules (
    echo Installing frontend packages...
    npm install
) else (
    echo Frontend packages already installed
)
cd ..

echo.
echo [5/6] Installing backend dependencies (if needed)...
echo Backend dependencies will be installed in Docker container

echo.
echo [6/6] Setup complete!
echo.
echo ========================================
echo 🚀 DEVELOPMENT ENVIRONMENT READY
echo ========================================
echo.
echo To start development:
echo   1. Backend:  npm run dev:backend
echo   2. Frontend: npm run dev:frontend
echo.
echo Available URLs:
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo To stop services: npm run dev:stop
echo ========================================

pause
