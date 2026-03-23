@echo off
chcp 65001 >nul
echo ==========================================
echo INICIANDO BOT PUBLIYA7
echo ==========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instale Python 3.8+
    pause
    exit /b 1
)

:: Crear directorios necesarios
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "database" mkdir database

:: Verificar .env
if not exist ".env" (
    echo [ADVERTENCIA] Archivo .env no encontrado
    echo Copie .env.example a .env y configure las variables
    pause
)

:: Iniciar el bot
echo [OK] Iniciando servidor...
echo.
python main.py

pause
