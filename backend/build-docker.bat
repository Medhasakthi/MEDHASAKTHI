@echo off
echo ========================================
echo Building MEDHASAKTHI Backend Docker Image
echo ========================================

echo.
echo 🔍 Checking Docker availability...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop and ensure it's running
    pause
    exit /b 1
)
echo ✅ Docker is available

echo.
echo 🧹 Cleaning up old images...
docker rmi medhasakthi-backend:latest 2>nul
docker system prune -f >nul 2>&1

echo.
echo 🔨 Building Docker image...
echo This may take several minutes...

docker build -t medhasakthi-backend:latest .
if errorlevel 1 (
    echo.
    echo ❌ Docker build failed!
    echo.
    echo 🔧 Trying alternative build with minimal requirements...
    
    REM Create temporary Dockerfile with minimal requirements
    echo FROM python:3.12-slim > Dockerfile.minimal
    echo WORKDIR /app >> Dockerfile.minimal
    echo RUN apt-get update ^&^& apt-get install -y gcc libpq-dev ^&^& rm -rf /var/lib/apt/lists/* >> Dockerfile.minimal
    echo COPY requirements-minimal.txt . >> Dockerfile.minimal
    echo RUN pip install --no-cache-dir --upgrade pip ^&^& pip install --no-cache-dir -r requirements-minimal.txt >> Dockerfile.minimal
    echo COPY . . >> Dockerfile.minimal
    echo EXPOSE 8000 >> Dockerfile.minimal
    echo CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] >> Dockerfile.minimal
    
    docker build -f Dockerfile.minimal -t medhasakthi-backend:minimal .
    if errorlevel 1 (
        echo ❌ Minimal build also failed
        echo.
        echo 📋 Troubleshooting steps:
        echo 1. Check your internet connection
        echo 2. Ensure Docker has enough memory allocated (4GB+)
        echo 3. Try running: docker system prune -a
        echo 4. Check the error messages above for specific package conflicts
        echo.
        del Dockerfile.minimal 2>nul
        pause
        exit /b 1
    ) else (
        echo ✅ Minimal build successful!
        echo 🏷️  Image tagged as: medhasakthi-backend:minimal
        del Dockerfile.minimal 2>nul
    )
) else (
    echo ✅ Full build successful!
    echo 🏷️  Image tagged as: medhasakthi-backend:latest
)

echo.
echo 📊 Docker images:
docker images | findstr medhasakthi-backend

echo.
echo 🚀 To run the container:
echo docker run -p 8000:8000 --env-file .env medhasakthi-backend:latest
echo.
echo ✅ Build completed successfully!
pause
