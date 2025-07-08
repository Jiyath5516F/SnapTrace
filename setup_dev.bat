@echo off
echo ========================================
echo SnapTrace Development Setup
echo ========================================

echo Setting up development environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10 or higher is required
    python --version
    pause
    exit /b 1
)

echo Creating virtual environment...
if exist "venv" rmdir /s /q "venv"
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Development environment ready!
echo ========================================
echo.
echo To start development:
echo 1. Activate the environment: venv\Scripts\activate
echo 2. Run the application: python main.py
echo 3. Make your changes
echo 4. Build portable version: build_optimized.bat
echo.
echo To deactivate the environment: deactivate
echo.

pause
