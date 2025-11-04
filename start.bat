@echo off
chcp 65001 >nul 2>&1
title Busya Translate Server
color 0A

echo.
echo ============================================================
echo    Busya Translate - Neural Network Translation
echo ============================================================
echo.

REM Check if .env file exists
echo [ACTION] Checking for .env file...
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo [INFO] Please create .env file from env.example
    echo [INFO] Copy env.example to .env and configure your API keys
    echo.
    pause
    exit /b 1
) else (
    echo [OK] .env file found
)
echo.

REM Check if Python is installed
echo [ACTION] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo [INFO] Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
) else (
    for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python found: %PYTHON_VERSION%
)
echo.

REM Check if virtual environment exists
echo [ACTION] Checking virtual environment...
if not exist venv (
    echo [INFO] Virtual environment not found
    echo [ACTION] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo [ERROR] Error code: %ERRORLEVEL%
        pause
        exit /b 1
    ) else (
        echo [OK] Virtual environment created successfully
    )
) else (
    echo [OK] Virtual environment found
)
echo.

REM Activate virtual environment
echo [ACTION] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    echo [ERROR] Error code: %ERRORLEVEL%
    pause
    exit /b 1
) else (
    echo [OK] Virtual environment activated
)
echo.

REM Check if requirements are installed
echo [ACTION] Checking Python dependencies...
python -c "import flask; import flask_cors" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dependencies not installed
    echo [ACTION] Installing dependencies...
    echo [INFO] This may take a moment...
    echo.
    pip install --upgrade pip >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Failed to upgrade pip, continuing...
    ) else (
        echo [OK] pip upgraded
    )
    echo.
    echo [ACTION] Installing from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Failed to install from requirements.txt
        echo [ERROR] Error code: %ERRORLEVEL%
        echo.
        echo [ACTION] Trying to install packages individually...
        pip install Flask
        if errorlevel 1 (
            echo [ERROR] Failed to install Flask
            echo [ERROR] Error code: %ERRORLEVEL%
        ) else (
            echo [OK] Flask installed
        )
        pip install flask-cors
        if errorlevel 1 (
            echo [ERROR] Failed to install flask-cors
            echo [ERROR] Error code: %ERRORLEVEL%
        ) else (
            echo [OK] flask-cors installed
        )
        pip install python-dotenv
        if errorlevel 1 (
            echo [ERROR] Failed to install python-dotenv
            echo [ERROR] Error code: %ERRORLEVEL%
        ) else (
            echo [OK] python-dotenv installed
        )
        pip install requests
        if errorlevel 1 (
            echo [ERROR] Failed to install requests
            echo [ERROR] Error code: %ERRORLEVEL%
            pause
            exit /b 1
        ) else (
            echo [OK] requests installed
        )
    ) else (
        echo [OK] All dependencies installed successfully
    )
    echo.
) else (
    echo [OK] All dependencies are installed
)
echo.

echo [ACTION] Starting Busya Translate server...
echo.

REM Check if port 8000 is in use
echo [ACTION] Checking if port 8000 is available...
netstat -ano | findstr :8000 >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use!
    echo.
    echo [ACTION] Attempting to free the port...
    echo.
    
    REM Find and kill process on port 8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        echo [INFO] Found process %%a using port 8000
        echo [ACTION] Terminating process %%a...
        taskkill /F /PID %%a >nul 2>&1
        if not errorlevel 1 (
            echo [OK] Process %%a terminated successfully
        ) else (
            echo [WARNING] Could not terminate process %%a (may require admin rights)
            echo [WARNING] Error code: %ERRORLEVEL%
        )
    )
    
    echo [ACTION] Waiting 2 seconds for port to be released...
    timeout /t 2 /nobreak >nul
    echo.
) else (
    echo [OK] Port 8000 is available
)
echo.

echo [INFO] Server will be available at: http://localhost:8000
echo [INFO] Browser will open automatically...
echo.
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ============================================================
echo [ACTION] Starting Python server...
echo ============================================================
echo.

REM Start the server (it will check port and show localhost addresses)
python server.py
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with error code: %ERRORLEVEL%
    echo [ERROR] Check the error messages above for details
    echo.
) else (
    echo.
    echo [INFO] Server stopped normally
    echo.
)

pause
