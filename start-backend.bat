@echo off
echo ========================================
echo Starting MEDHASAKTHI Backend
echo ========================================

echo Checking Python dependencies...
cd backend

echo Installing/updating Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)

echo Setting up local environment...
copy .env.local .env

echo Creating uploads directory...
if not exist uploads mkdir uploads

echo Starting backend development server...
echo This will set up SQLite database and start the server
echo.
python start_local.py
