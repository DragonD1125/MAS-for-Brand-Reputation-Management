@echo off
REM Clean startup script for Brand Reputation Management System
echo ========================================
echo Starting Brand Reputation Management System
echo ========================================
echo.

cd /d "%~dp0"

REM Use the root .venv
set PYTHON_PATH=..\venv\Scripts\python.exe

echo Checking Python environment...
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python virtual environment not found at %PYTHON_PATH%
    echo Please run: python -m venv ..\.venv
    pause
    exit /b 1
)

echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

"%PYTHON_PATH%" main.py

pause
