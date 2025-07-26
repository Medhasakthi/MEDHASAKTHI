@echo off
echo ========================================
echo Starting MEDHASAKTHI Frontend
echo ========================================

echo Checking if dependencies are installed...
cd frontend

if not exist node_modules (
    echo Installing dependencies...
    echo This may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo Failed to install dependencies
        echo.
        echo Try running this in Command Prompt instead of PowerShell
        echo Or run: npm install manually in the frontend folder
        pause
        exit /b 1
    )
)

echo.
echo Starting frontend development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Note: If you see any warnings about deprecated packages,
echo they have been updated in package.json and will be resolved
echo after the next npm install.
echo.
call npm start
