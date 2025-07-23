@echo off
REM MEDHASAKTHI Local Windows PC Deployment Script
REM Deploy on your Windows computer with domain pointing to your public IP

setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🏠 MEDHASAKTHI Local Windows Deployment
echo Domain: medhasakthi.com
echo ========================================
echo.

REM Configuration
set DOMAIN=medhasakthi.com
set EMAIL=admin@medhasakthi.com

REM Check if Docker Desktop is installed
echo 📋 Checking Docker Installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo Make sure Docker Desktop is running before continuing
    pause
    exit /b 1
)
echo ✅ Docker is installed

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Get public IP
echo.
echo 📋 Network Configuration...
for /f "delims=" %%i in ('curl -s ifconfig.me 2^>nul') do set PUBLIC_IP=%%i
if "%PUBLIC_IP%"=="" (
    for /f "delims=" %%i in ('curl -s ipinfo.io/ip 2^>nul') do set PUBLIC_IP=%%i
)
if "%PUBLIC_IP%"=="" set PUBLIC_IP=Unable to detect

REM Get local IP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set LOCAL_IP=%%i
    set LOCAL_IP=!LOCAL_IP: =!
    goto :found_ip
)
:found_ip

echo ℹ️  Public IP: %PUBLIC_IP%
echo ℹ️  Local IP: %LOCAL_IP%

REM Create application directories
echo.
echo 📋 Directory Setup...
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "uploads" mkdir uploads
if not exist "certificates" mkdir certificates
if not exist "static" mkdir static
echo ✅ Application directories created

REM Generate environment configuration
echo.
echo 📋 Environment Configuration...
if not exist ".env" (
    copy "backend\.env.example" ".env" >nul
    
    REM Generate secure secrets using PowerShell
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(64, 0)"') do set SECRET_KEY=%%i
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(64, 0)"') do set JWT_SECRET=%%i
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(64, 0)"') do set CSRF_SECRET=%%i
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(32, 0)"') do set BACKUP_KEY=%%i
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(32, 0)"') do set POSTGRES_PASSWORD=%%i
    for /f "delims=" %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(32, 0)"') do set REDIS_PASSWORD=%%i
    
    REM Update environment file using PowerShell
    powershell -command "(Get-Content .env) -replace 'your-secret-key-here', '%SECRET_KEY%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'your-jwt-secret-here', '%JWT_SECRET%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'your-csrf-secret-key-here', '%CSRF_SECRET%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'your-backup-encryption-key-here', '%BACKUP_KEY%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'secure_password_change_me', '%POSTGRES_PASSWORD%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'redis_password_change_me', '%REDIS_PASSWORD%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'development', 'production' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'admin@medhasakthi.com', '%EMAIL%' | Set-Content .env"
    powershell -command "(Get-Content .env) -replace 'your-domain.com', '%DOMAIN%' | Set-Content .env"
    
    echo ✅ Environment configuration generated
) else (
    echo ℹ️  Using existing environment configuration
)

REM Create local nginx configuration
echo.
echo 📋 Nginx Configuration...
(
echo server {
echo     listen 80;
echo     server_name %DOMAIN% www.%DOMAIN% localhost;
echo     return 301 https://$server_name$request_uri;
echo }
echo.
echo server {
echo     listen 443 ssl http2;
echo     server_name %DOMAIN% www.%DOMAIN% localhost;
echo.
echo     # SSL configuration ^(self-signed for local^)
echo     ssl_certificate /etc/nginx/ssl/medhasakthi.crt;
echo     ssl_certificate_key /etc/nginx/ssl/medhasakthi.key;
echo     ssl_protocols TLSv1.2 TLSv1.3;
echo.
echo     # Security headers
echo     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
echo     add_header X-Content-Type-Options nosniff always;
echo     add_header X-Frame-Options DENY always;
echo.
echo     # Frontend
echo     location / {
echo         proxy_pass http://frontend:3000;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo.
echo     # Backend API
echo     location /api/ {
echo         proxy_pass http://backend:8000/api/;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo }
) > nginx-local.conf

echo ✅ Nginx configuration created

REM Create Windows-specific docker-compose
echo.
echo 📋 Docker Compose Configuration...
(
echo version: '3.8'
echo.
echo services:
echo   postgres:
echo     image: postgres:15-alpine
echo     container_name: medhasakthi-postgres-local
echo     environment:
echo       POSTGRES_DB: medhasakthi
echo       POSTGRES_USER: medhasakthi_user
echo       POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
echo     volumes:
echo       - postgres_data:/var/lib/postgresql/data
echo     ports:
echo       - "5432:5432"
echo     restart: unless-stopped
echo.
echo   redis:
echo     image: redis:7-alpine
echo     container_name: medhasakthi-redis-local
echo     command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
echo     volumes:
echo       - redis_data:/data
echo     ports:
echo       - "6379:6379"
echo     restart: unless-stopped
echo.
echo   backend:
echo     build:
echo       context: ./backend
echo       dockerfile: Dockerfile
echo     container_name: medhasakthi-backend-local
echo     environment:
echo       - DATABASE_URL=postgresql://medhasakthi_user:${POSTGRES_PASSWORD}@postgres:5432/medhasakthi
echo       - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
echo       - SECRET_KEY=${SECRET_KEY}
echo       - DEBUG=false
echo       - ENVIRONMENT=production
echo     volumes:
echo       - ./uploads:/app/uploads
echo       - ./logs:/app/logs
echo     ports:
echo       - "8000:8000"
echo     depends_on:
echo       - postgres
echo       - redis
echo     restart: unless-stopped
echo.
echo   frontend:
echo     build:
echo       context: ./frontend
echo       dockerfile: Dockerfile
echo     container_name: medhasakthi-frontend-local
echo     environment:
echo       - REACT_APP_API_URL=https://%DOMAIN%/api
echo     ports:
echo       - "3000:3000"
echo     restart: unless-stopped
echo.
echo   nginx:
echo     image: nginx:alpine
echo     container_name: medhasakthi-nginx-local
echo     volumes:
echo       - ./nginx-local.conf:/etc/nginx/conf.d/default.conf
echo     ports:
echo       - "80:80"
echo       - "443:443"
echo     depends_on:
echo       - backend
echo       - frontend
echo     restart: unless-stopped
echo.
echo volumes:
echo   postgres_data:
echo   redis_data:
) > docker-compose.local.yml

echo ✅ Local Docker Compose configuration created

REM Deploy application
echo.
echo 📋 Application Deployment...
echo ℹ️  Building and starting MEDHASAKTHI...

REM Start database services first
docker-compose -f docker-compose.local.yml up -d postgres redis
echo ℹ️  Waiting for database to start...
timeout /t 30 /nobreak >nul

REM Build and start all services
docker-compose -f docker-compose.local.yml build --no-cache
docker-compose -f docker-compose.local.yml up -d

echo ✅ MEDHASAKTHI deployed successfully

REM Create backup script
echo.
echo 📋 Backup Configuration...
(
echo @echo off
echo echo Creating local backup...
echo docker-compose -f docker-compose.local.yml exec -T backend python -c "import asyncio; from app.services.backup_service import backup_service; asyncio.run(backup_service.create_full_backup())"
echo echo Backup completed!
echo pause
) > backup-local.bat

echo ✅ Local backup script created

REM Final health checks
echo.
echo 📋 Health Checks...
echo ℹ️  Waiting for services to start...
timeout /t 60 /nobreak >nul

REM Check if services are running
docker-compose -f docker-compose.local.yml ps

echo.
echo ========================================
echo 🎉 MEDHASAKTHI LOCAL DEPLOYMENT COMPLETED!
echo ========================================
echo.
echo 📋 Local Access URLs:
echo    🏠 Main Site: http://localhost:3000
echo    🔧 Backend API: http://localhost:8000
echo    🔧 API Docs: http://localhost:8000/docs
echo.
echo 🌐 Network Configuration:
echo    📡 Public IP: %PUBLIC_IP%
echo    🏠 Local IP: %LOCAL_IP%
echo    🌍 Domain: %DOMAIN%
echo.
echo 🔧 Router Port Forwarding Required:
echo    📝 Forward port 80 to %LOCAL_IP%:80
echo    📝 Forward port 443 to %LOCAL_IP%:443
echo    📝 Forward port 3000 to %LOCAL_IP%:3000 (temporary)
echo.
echo 📝 Next Steps:
echo    1. Configure port forwarding on your router
echo    2. Point %DOMAIN% DNS to %PUBLIC_IP%
echo    3. Test access from external network
echo    4. Run backup-local.bat for backups
echo.
echo 🔄 Useful Commands:
echo    • View logs: docker-compose -f docker-compose.local.yml logs
echo    • Stop services: docker-compose -f docker-compose.local.yml down
echo    • Start services: docker-compose -f docker-compose.local.yml up -d
echo.
echo 🚀 MEDHASAKTHI is now running on your Windows PC!
echo.
pause
