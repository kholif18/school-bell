@echo off
setlocal

set APP_NAME=SchoolBell
set ENTRY_FILE=main.py

echo ======================================
echo BUILDING %APP_NAME% (PRODUCTION)
echo ======================================

REM =========================================================
REM 1. CLEAN OLD BUILD
REM =========================================================

echo Cleaning old build artifacts...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

del /q *.spec 2>nul

for /d /r %%i in (__pycache__) do (
    if exist "%%i" rmdir /s /q "%%i"
)

echo Clean completed

REM =========================================================
REM 2. ENSURE REQUIRED FOLDERS EXIST
REM =========================================================

echo Ensuring runtime folders exist...

if not exist db mkdir db
if not exist logs mkdir logs

REM =========================================================
REM 3. BUILD WITH PYINSTALLER
REM =========================================================

echo Running PyInstaller...

pyinstaller %ENTRY_FILE% ^
--name %APP_NAME% ^
--noconfirm ^
--clean ^
--windowed ^
--add-data "assets;assets" ^
--add-data "apps/desktop/styles;apps/desktop/styles" ^
--add-data "apps/web/templates;apps/web/templates" ^
--add-data "apps/web/static;apps/web/static" ^
--add-data "db;db" ^
--add-data "logs;logs"

REM =========================================================
REM 4. POST BUILD CHECK
REM =========================================================

echo Checking build output...

if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo ======================================
    echo BUILD SUCCESS!
    echo Output: dist\%APP_NAME%\
    echo ======================================
) else (
    echo BUILD FAILED!
    exit /b 1
)

pause