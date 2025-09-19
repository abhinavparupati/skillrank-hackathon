@echo off
echo Setting up Natural Language to SQL Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python detected: 
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
cd backend
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check for database
echo.
echo Checking for database...
if exist "..\retail_database.db" (
    echo ✓ Database found: retail_database.db
) else (
    echo ✗ Database not found: retail_database.db
    echo Please ensure the database file is in the project root directory
)

REM Setup environment file
echo.
echo Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo ✓ Created .env file from template
    echo Please edit .env file and add your GitHub token
) else (
    echo ✓ .env file already exists
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env file and add your GitHub token
echo 2. Run: cd backend ^&^& python app.py
echo 3. Open frontend\index.html in your web browser
echo.
pause