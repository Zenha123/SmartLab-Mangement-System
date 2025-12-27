@echo off
echo ========================================
echo RESET DATABASE AND RUN MIGRATIONS
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Deleting old database...
if exist db.sqlite3 (
    del db.sqlite3
    echo Database deleted!
) else (
    echo No existing database found.
)

echo.
echo Step 2: Running migrations...
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
echo Login credentials:
echo   test / test
echo   admin / admin
echo   FAC001 / password123
echo.
echo To start the server:
echo   python manage.py runserver
echo.
pause
