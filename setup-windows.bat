@echo off
echo.
echo ===============================================
echo   MEDHASAKTHI Windows Setup
echo ===============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo ERROR: This script must be run as Administrator
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if WSL is available
wsl --version >nul 2>&1
if %errorLevel% == 0 (
    echo WSL detected - Using Linux environment
    echo.
    echo Starting MEDHASAKTHI setup in WSL...
    wsl bash -c "cd /mnt/c/Users/vboxuser/Desktop/MEDHASAKTHI && chmod +x *.sh && ./setup-medhasakthi.sh"
) else (
    echo WSL not detected. Installing WSL first...
    echo.
    echo Installing WSL (Windows Subsystem for Linux)...
    wsl --install -d Ubuntu
    echo.
    echo WSL installation completed.
    echo Please restart your computer and run this script again.
    pause
)

echo.
echo Setup completed!
pause
