# Busya Translate .env File Creation Script (PowerShell)
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   Creating .env file for Busya Translate" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

if (Test-Path ".env") {
    Write-Host "[WARNING] .env file already exists! Overwriting..." -ForegroundColor Yellow
    Write-Host ""
}

$envContent = @"
# Yandex API Key (Api-Key or Service Account Key)
YANDEX_API_KEY=AQVN0Y80GM2fuu_iKIb9vN4lhtZ7c16lEV5GC7IF

# Yandex Folder ID (optional, if required by Yandex API)
# Get it from: https://console.cloud.yandex.ru/cloud?section=overview
YANDEX_FOLDER_ID=

# Yandex IAM Token (optional, alternative to Api-Key)
# Use IAM token OR Api-Key, not both
YANDEX_IAM_TOKEN=

# Server Port
PORT=8000

# Auto open browser on start (true/false)
AUTO_OPEN_BROWSER=true

# Note: AI Chat uses Puter.js with OpenRouter models (no API key needed)
# Available models: openrouter:deepseek/deepseek-v3.2-exp, openrouter:openai/gpt-5, 
# openrouter:qwen/qwen-3-max, openrouter:openai/o3-pro
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] .env file created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host "  - Yandex API Key: Configured" -ForegroundColor Cyan
    Write-Host "  - Server Port: 8000" -ForegroundColor Cyan
    Write-Host "  - AI Chat: Using Puter.js with OpenRouter" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run start.bat or start.ps1 to start the server!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[ERROR] Failed to create .env file." -ForegroundColor Red
    Write-Host "Please check permissions or try creating it manually." -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
