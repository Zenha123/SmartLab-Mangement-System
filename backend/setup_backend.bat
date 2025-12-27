@echo off
echo ========================================
echo Smart Lab Management - Backend Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [2/5] Running migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo.

echo [3/5] Creating faculty users...
python manage.py create_faculty
echo.

echo [4/5] Loading mock data...
python manage.py loaddata fixtures/initial_data.json
if %errorlevel% neq 0 (
    echo WARNING: Failed to load fixtures (may already exist)
)
echo.

echo [5/5] Setup complete!
echo.
echo ========================================
echo Faculty Login Credentials:
echo ========================================
echo FAC001 / password123 (Shireen)
echo FAC002 / admin123 (John Doe)
echo admin / admin (Admin User)
echo test / test (Test User)
echo ========================================
echo.
echo To start the server, run: python manage.py runserver
echo.
pause
