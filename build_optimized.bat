@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Building Optimized SnapTrace Portable
echo ========================================

echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
if exist "src\core\__pycache__" rmdir /s /q "src\core\__pycache__"
if exist "src\ui\__pycache__" rmdir /s /q "src\ui\__pycache__"

echo Installing/updating requirements...
pip install -r requirements.txt

echo Building optimized executable...
pyinstaller --clean SnapTrace.spec

if exist "dist\SnapTrace.exe" (
    echo Copying external data files...
    copy "defect_feedbacks.csv" "dist\defect_feedbacks.csv" >nul
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    for %%A in ("dist\SnapTrace.exe") do (
        set /a "sizeMB=%%~zA / 1024 / 1024"
        echo Executable size: %%~zA bytes (approximately !sizeMB! MB)
    )
    echo Location: dist\SnapTrace.exe
    echo.
    echo Optimizations applied:
    echo - Removed pandas dependency (replaced with native CSV)
    echo - Excluded unnecessary libraries
    echo - Enabled UPX compression
    echo - External CSV file for easy customization
    echo.
    echo Distribution folder structure:
    echo   dist/
    echo     SnapTrace.exe
    echo     defect_feedbacks.csv
    echo.
    echo You can now distribute the entire 'dist' folder as a portable application.
    echo Users can customize defect_feedbacks.csv without rebuilding the executable.
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed! Check the output above for errors.
    echo ========================================
)

pause
