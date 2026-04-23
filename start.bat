@echo off
echo ==================================
echo AI Mask Detection System
echo ==================================
echo.

echo Checking MongoDB status...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo MongoDB is running
) else (
    echo Starting MongoDB...
    net start MongoDB
)

echo.
echo Setting up virtual environment...
if not exist "venv" (
    py -3.11 -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment with Python 3.11.
        echo Install Python 3.11 and try again.
        exit /b 1
    )
    echo Virtual environment created
)

call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)
echo Virtual environment activated

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Stopping setup.
    exit /b 1
)

echo.
echo Running migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo Makemigrations failed. Stopping setup.
    exit /b 1
)
python manage.py migrate
if errorlevel 1 (
    echo Migrate failed. Stopping setup.
    exit /b 1
)

echo.
echo ==================================
echo Starting Django server...
echo ==================================
echo.
echo Access the application at:
echo http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
