@echo off
echo Checking for remaining Grid item usage in frontend files...
echo.

findstr /s /c:"Grid item" frontend\src\*.tsx | findstr /v "node_modules" > remaining_grid_files.txt

echo Files still containing Grid item usage:
type remaining_grid_files.txt

echo.
echo Total files with Grid item issues:
findstr /c:"Grid item" remaining_grid_files.txt | find /c "Grid item"
