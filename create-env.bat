@echo off
chcp 65001 >nul 2>&1
title Create .env file
color 0B

echo.
echo ============================================================
echo    Creating .env file for Busya Translate
echo ============================================================
echo.

if exist .env (
    echo [WARNING] .env file already exists! Overwriting...
    echo.
)

(
echo # Yandex API Key ^(Api-Key or Service Account Key^)
echo YANDEX_API_KEY=AQVN0Y80GM2fuu_iKIb9vN4lhtZ7c16lEV5GC7IF
echo.
echo # Yandex Folder ID ^(optional, if required by Yandex API^)
echo # Get it from: https://console.cloud.yandex.ru/cloud?section=overview
echo YANDEX_FOLDER_ID=
echo.
echo # Yandex IAM Token ^(optional, alternative to Api-Key^)
echo # Use IAM token OR Api-Key, not both
echo YANDEX_IAM_TOKEN=
echo.
echo # Server Port
echo PORT=8000
echo.
echo # Auto open browser on start ^(true/false^)
echo AUTO_OPEN_BROWSER=true
echo.
echo # Note: AI Chat uses Puter.js with OpenRouter models ^(no API key needed^)
echo # Available models: openrouter:deepseek/deepseek-v3.2-exp, openrouter:openai/gpt-5, 
echo # openrouter:qwen/qwen-3-max, openrouter:openai/o3-pro
) > .env

echo [OK] .env file created successfully!
echo.
echo Configuration:
echo   - Yandex API Key: Configured
echo   - Server Port: 8000
echo   - AI Chat: Using Puter.js with OpenRouter
echo.
echo You can now run start.bat to start the server!
echo.
pause
