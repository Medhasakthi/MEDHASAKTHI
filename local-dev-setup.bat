@echo off
echo ========================================
echo MEDHASAKTHI Local Development Setup
echo (No Docker Required)
echo ========================================

echo.
echo [1/5] Checking prerequisites...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
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

echo ✓ Python found
python --version
echo ✓ Node.js found  
node --version

echo.
echo [2/5] Installing root dependencies...
npm install

echo.
echo [3/5] Installing frontend dependencies...
cd frontend
npm install
cd ..

echo.
echo [4/5] Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [5/5] Setup complete!
echo.
echo ========================================
echo 🚀 LOCAL DEVELOPMENT READY
echo ========================================
echo.
echo To start development:
echo   Frontend only: npm run dev:frontend-only
echo   Backend only:  npm run dev:backend
echo   Frontend:      npm run dev:frontend
echo.
echo Available URLs (when running):
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo Note: You'll need to set up a database separately
echo or use SQLite for local development.
echo ========================================

pause
