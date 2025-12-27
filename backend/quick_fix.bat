@echo off
echo ========================================
echo QUICK FIX: Renaming sessions app
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Renaming directory...
if exist apps\sessions (
    if exist apps\lab_sessions (
        echo Removing old lab_sessions directory...
        rmdir /s /q apps\lab_sessions
    )
    ren apps\sessions lab_sessions
    echo Directory renamed successfully!
) else (
    echo Directory already renamed or not found.
)

echo.
echo Step 2: Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Step 3: Creating faculty users...
python manage.py create_faculty

echo.
echo Step 4: Loading fixtures...
python manage.py loaddata fixtures/initial_data.json

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo python manage.py runserver
echo.
pause
