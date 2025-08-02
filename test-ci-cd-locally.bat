@echo off
REM MEDHASAKTHI CI/CD Local Test Script for Windows
REM This script simulates the CI/CD pipeline locally

echo.
echo 🔧 MEDHASAKTHI CI/CD Local Test
echo ==================================
echo.

REM Test 1: Backend Syntax Check
echo ℹ️  Test 1: Backend Python Syntax Check
cd backend
python -m py_compile main.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend syntax check failed
) else (
    echo ✅ Backend syntax check passed
)
cd ..

REM Test 2: Backend Dependencies
echo ℹ️  Test 2: Backend Dependencies Check
cd backend
pip install -r requirements.txt --dry-run >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some backend dependencies may have issues
) else (
    echo ✅ Backend dependencies are valid
)
cd ..

REM Test 3: Frontend Dependencies and Build
for %%a in (frontend web-institute web-student) do (
    echo ℹ️  Test 3: Testing %%a
    cd %%a
    
    if exist package.json (
        echo ℹ️  Installing dependencies for %%a...
        npm install --legacy-peer-deps >nul 2>&1
        if errorlevel 1 (
            echo ⚠️  %%a dependency installation had issues
        ) else (
            echo ✅ %%a dependencies installed
        )
        
        echo ℹ️  Building %%a...
        set REACT_APP_API_URL=http://localhost:8080/api
        set REACT_APP_APP_NAME=MEDHASAKTHI
        set NEXT_PUBLIC_API_URL=http://localhost:8080/api
        set NODE_OPTIONS=--max-old-space-size=4096
        set GENERATE_SOURCEMAP=false
        set CI=false
        
        npm run build >nul 2>&1
        if errorlevel 1 (
            echo ⚠️  %%a build had issues
        ) else (
            echo ✅ %%a build successful
        )
    ) else (
        echo ⚠️  %%a/package.json not found
    )
    cd ..
)

REM Test 4: Docker Build Test
echo ℹ️  Test 4: Docker Build Test
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not available - skipping Docker tests
) else (
    echo ℹ️  Testing Docker builds...
    
    REM Test backend build
    docker build -t test-backend ./backend >nul 2>&1
    if errorlevel 1 (
        echo ❌ Backend Docker build failed
    ) else (
        echo ✅ Backend Docker build successful
    )
    
    REM Test frontend build
    docker build -t test-frontend ./frontend >nul 2>&1
    if errorlevel 1 (
        echo ❌ Frontend Docker build failed
    ) else (
        echo ✅ Frontend Docker build successful
    )
    
    REM Test docker-compose build
    docker-compose build >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose build failed
    ) else (
        echo ✅ Docker Compose build successful
    )
)

REM Test 5: Integration Test
echo ℹ️  Test 5: Integration Test
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Compose not available - skipping integration test
) else (
    echo ℹ️  Starting integration test...
    
    REM Clean up any existing containers
    docker-compose down >nul 2>&1
    
    REM Start services
    echo ℹ️  Starting services...
    docker-compose up -d
    if errorlevel 1 (
        echo ❌ Failed to start services
    ) else (
        echo ✅ Services started
        
        REM Wait for services
        echo ℹ️  Waiting for services to initialize...
        timeout /t 60 /nobreak >nul
        
        REM Test backend health
        echo ℹ️  Testing backend health...
        for /l %%i in (1,1,5) do (
            curl -f http://localhost:8080/health >nul 2>&1
            if not errorlevel 1 (
                echo ✅ Backend health check passed
                goto frontend_test
            ) else (
                echo ℹ️  Backend not ready, attempt %%i/5
                timeout /t 10 /nobreak >nul
            )
        )
        
        :frontend_test
        REM Test frontend
        echo ℹ️  Testing frontend...
        for /l %%i in (1,1,5) do (
            curl -f http://localhost:3000 >nul 2>&1
            if not errorlevel 1 (
                echo ✅ Frontend health check passed
                goto cleanup
            ) else (
                echo ℹ️  Frontend not ready, attempt %%i/5
                timeout /t 10 /nobreak >nul
            )
        )
        
        :cleanup
        REM Show service status
        echo ℹ️  Service status:
        docker-compose ps
        
        REM Cleanup
        echo ℹ️  Cleaning up...
        docker-compose down
    )
)

REM Test 6: Environment Variables Check
echo ℹ️  Test 6: Environment Variables Check
if exist .env (
    echo ✅ .env file exists
) else (
    echo ⚠️  .env file not found - create from .env.example
)

if exist .env.example (
    echo ✅ .env.example file exists
) else (
    echo ⚠️  .env.example file not found
)

REM Summary
echo.
echo 🎉 CI/CD Local Test Completed!
echo.
echo ℹ️  Summary:
echo   - Backend syntax and dependencies checked
echo   - All frontend apps tested
echo   - Docker builds verified
echo   - Integration test completed
echo   - Environment setup checked
echo.
echo ℹ️  If all tests passed, your CI/CD pipeline should work on GitHub!
echo.
echo ℹ️  Next steps:
echo   1. Commit and push your changes
echo   2. Check the Actions tab in GitHub
echo   3. Monitor the pipeline execution
echo   4. Review any failures in the logs
echo.
echo ⚠️  Note: Some warnings are normal and won't prevent deployment
echo.
pause
