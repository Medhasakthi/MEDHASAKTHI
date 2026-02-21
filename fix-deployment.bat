@echo off
REM MEDHASAKTHI Deployment Fix Script for Windows
REM This script fixes common deployment issues

echo.
echo 🔧 MEDHASAKTHI Deployment Fix
echo ==================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo ℹ️  Step 1: Stopping existing containers...
docker-compose down

echo ℹ️  Step 2: Removing old images...
docker-compose down --rmi all --volumes --remove-orphans

echo ℹ️  Step 3: Building fresh images...
docker-compose build --no-cache

echo ℹ️  Step 4: Starting services...
docker-compose up -d

echo ℹ️  Step 5: Waiting for services to start...
timeout /t 30 /nobreak >nul

echo ℹ️  Step 6: Checking service status...
docker-compose ps

echo ℹ️  Step 7: Checking frontend container...
docker-compose exec frontend ls -la /usr/share/nginx/html/

echo ℹ️  Step 8: Testing endpoints...
echo Testing main frontend...
curl -f http://localhost:3000/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Frontend not responding directly
) else (
    echo ✅ Frontend is responding
)

echo Testing through nginx proxy...
curl -f http://localhost/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Nginx proxy not responding
) else (
    echo ✅ Nginx proxy is working
)

echo Testing backend...
curl -f http://localhost:8080/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend not responding
) else (
    echo ✅ Backend is responding
)

echo.
echo ℹ️  Step 9: Showing recent logs...
echo Frontend logs:
docker-compose logs --tail=10 frontend

echo Nginx logs:
docker-compose logs --tail=10 nginx

echo Backend logs:
docker-compose logs --tail=10 backend

echo.
echo ✅ Deployment fix completed!
echo.
echo ℹ️  Access your application at:
echo   🌐 Main site: http://localhost
echo   🌐 Frontend direct: http://localhost:3000
echo   🌐 Backend API: http://localhost:8080
echo   📚 API docs: http://localhost:8080/docs
echo.
echo ℹ️  If you're still seeing file listings instead of the app:
echo   1. Check if the React build completed successfully
echo   2. Verify nginx is serving from the correct directory
echo   3. Ensure index.html exists in the build output
echo   4. Check browser console for JavaScript errors
echo.
pause
