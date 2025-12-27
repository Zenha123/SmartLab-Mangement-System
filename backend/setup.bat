@echo off
cd /d "%~dp0"
set PYTHON="c:\Users\Admin\Desktop\new - Copy\lab\env\Scripts\python.exe"
echo Installing packages... > setup_log.txt
%PYTHON% -m pip install django djangorestframework django-channels["daphne"] channels_redis psycopg2-binary pyjwt >> setup_log.txt 2>&1
if %errorlevel% neq 0 (
    echo Install Failed >> setup_log.txt
    exit /b %errorlevel%
)
echo Install Success. Starting project... >> setup_log.txt
%PYTHON% -m django startproject config . >> setup_log.txt 2>&1
if %errorlevel% neq 0 (
    echo Version check failed or Start Project Failed >> setup_log.txt
) else (
    echo Project Created >> setup_log.txt
)
