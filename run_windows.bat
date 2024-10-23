@echo off

REM Check if Python is installed and retrieve its version
python --version 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed on your system.
    echo Please download Python 3.12 from the following link:
    echo https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    pause
    exit /b
) ELSE (
    for /f "tokens=2 delims= " %%a in ('python --version') do set PY_VERSION=%%a
    echo Python version detected: %PY_VERSION%

    REM Check if the installed Python version is 3.12
    echo %PY_VERSION% | findstr /r "^3\.12" >nul
    IF %ERRORLEVEL% NEQ 0 (
        echo You have Python installed, but it is not version 3.12.
        echo Please update Python to version 3.12 from the following link:
        echo https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
        pause
        exit /b
    ) ELSE (
        echo Python 3.12 is installed and ready.
    )
)

REM Install dependencies
pip install -r requirements.txt

REM Run the GUI script
python GUI.py

REM Prevent the script from closing immediately
pause
