@echo off
REM MEDHASAKTHI Simple Deployment Script for Windows

echo 🚀 MEDHASAKTHI Deployment
echo ================================

REM Check prerequisites
echo ℹ️  Checking prerequisites...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Check .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    if exist "backend\.env.example" (
        copy "backend\.env.example" ".env" >nul
        echo ⚠️  Please update the .env file with your actual values before continuing.
        echo ℹ️  Edit .env file and run this script again.
        pause
        exit /b 1
    ) else (
        echo ❌ No .env template found. Please create .env file manually.
        pause
        exit /b 1
    )
)

echo ✅ .env file found

REM Create necessary directories
echo ℹ️  Creating application directories...
if not exist "uploads" mkdir uploads
if not exist "certificates" mkdir certificates
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
echo ✅ Directories created

REM Build and start services
echo ℹ️  Building and starting MEDHASAKTHI services...

REM Stop any existing containers
docker-compose down --remove-orphans

REM Build images
docker-compose build --no-cache

REM Start services
docker-compose up -d

echo ✅ Services started successfully

REM Wait for services to be ready
echo ℹ️  Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Health checks
echo ℹ️  Running health checks...

REM Check backend
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend service is healthy
) else (
    echo ⚠️  Backend service may not be ready yet
)

REM Check frontend
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend service is healthy
) else (
    echo ⚠️  Frontend service may not be ready yet
)

echo.
echo 🎉 MEDHASAKTHI Deployment Complete!
echo.
echo Access your application:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8080
echo   API Docs: http://localhost:8080/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
echo ℹ️  Make sure to update your .env file with production values!
echo.
pause
