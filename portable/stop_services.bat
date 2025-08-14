@echo off
REM CyberSec Toolkit Pro 2025 - Arrêt des services portables
REM Script d'arrêt propre pour Windows

echo 🛑 Arrêt CyberSec Toolkit Pro 2025 Portable...

REM Variables  
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..

REM Charger la configuration pour récupérer les ports
if exist "%SCRIPT_DIR%config\portable.env" (
    for /f "tokens=1,2 delims==" %%a in (%SCRIPT_DIR%config\portable.env) do set %%a=%%b
)

REM Arrêter les processus Python (backend)
echo 🔧 Arrêt du backend...
taskkill /f /im python.exe 2>nul || echo Process non trouvé
taskkill /f /im uvicorn.exe 2>nul || echo Process non trouvé

REM Arrêter les processus Node.js (frontend) 
echo 🎨 Arrêt du frontend...
taskkill /f /im node.exe 2>nul || echo Process non trouvé
taskkill /f /im yarn.exe 2>nul || echo Process non trouvé

REM Arrêter par ports si définis
if defined BACKEND_PORT (
    netstat -ano | findstr :%BACKEND_PORT% | for /f "tokens=5" %%a in ('more') do taskkill /f /pid %%a 2>nul
)

if defined FRONTEND_PORT (
    netstat -ano | findstr :%FRONTEND_PORT% | for /f "tokens=5" %%a in ('more') do taskkill /f /pid %%a 2>nul
)

REM Attendre le nettoyage
timeout /t 2 /nobreak >nul

echo ✅ Services portables arrêtés
echo 📱 Données sauvegardées sur USB

pause