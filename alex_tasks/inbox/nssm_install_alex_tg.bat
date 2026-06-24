@echo off
REM Установка AlexTelegramBot как Windows-сервис через NSSM
REM Запусти от администратора

set TOKEN=8583862768:***nssm install AlexTelegramBot "C:\Python311\python.exe" "C:\matryoshka\alex_telegram_bot.py"
if %ERRORLEVEL% NEQ 0 (
    echo NSSM install failed. Is NSSM in PATH?
    exit /b 1
)

nssm set AlexTelegramBot AppDirectory "C:\matryoshka"
nssm set AlexTelegramBot DisplayName "Alex Telegram Bot (opencode bridge)"
nssm set AlexTelegramBot Description "Мост Telegram ↔ opencode на ПК Олега"
nssm set AlexTelegramBot Start SERVICE_AUTO_START
nssm set AlexTelegramBot AppStdout "C:\matryoshka\logs\alex_telegram_bot.out.log"
nssm set AlexTelegramBot AppStderr "C:\matryoshka\logs\alex_telegram_bot.err.log"
nssm set AlexTelegramBot AppRotateFiles 1
nssm set AlexTelegramBot AppRotateBytes 1048576

echo Service installed. Starting...
nssm start AlexTelegramBot
timeout /t 3
nssm status AlexTelegramBot
