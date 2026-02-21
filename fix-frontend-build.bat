@echo off
echo ========================================
echo MEDHASAKTHI Frontend Build Fix Script
echo ========================================

cd frontend

echo Step 1: Cleaning up...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist build rmdir /s /q build

echo Step 2: Setting environment variables...
echo REACT_APP_API_URL=/api > .env.local
echo REACT_APP_APP_NAME=MEDHASAKTHI >> .env.local
echo REACT_APP_STUDENT_URL=https://student.medhasakthi.com >> .env.local
echo REACT_APP_TEACHER_URL=https://teacher.medhasakthi.com >> .env.local
echo REACT_APP_ADMIN_URL=https://admin.medhasakthi.com >> .env.local
echo REACT_APP_LEARN_URL=https://learn.medhasakthi.com >> .env.local

echo Step 3: Installing dependencies...
npm cache clean --force
npm install --legacy-peer-deps --no-audit --no-fund

echo Step 4: Building application...
set GENERATE_SOURCEMAP=false
set NODE_OPTIONS=--max-old-space-size=4096
npm run build

if errorlevel 1 (
    echo ========================================
    echo BUILD FAILED - Trying alternative approach
    echo ========================================
    
    echo Checking TypeScript errors...
    npm run type-check
    
    echo Checking for linting issues...
    npm run lint:fix
    
    echo Retrying build...
    npm run build
)

if exist build (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Build output is in the 'build' folder
    dir build
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Please check the error messages above
)

pause
