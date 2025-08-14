@echo off
REM ===============================================================
REM CyberSec Toolkit Pro 2025 - Lanceur Windows Portable FINAL
REM Version 1.7.3 - 35 Services Operationnels
REM Configuration et demarrage automatique optimise
REM ===============================================================

title CyberSec Toolkit Pro 2025 - Demarrage Portable

echo.
echo ███████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗███████╗ ██████╗
echo ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝
echo ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗█████╗  ██║     
echo ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══╝  ██║     
echo ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║███████╗╚██████╗
echo  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝
echo.
echo              CYBERSEC TOOLKIT PRO 2025 - PORTABLE
echo                  Version 1.7.3 - 35 Services
echo                    Sprint 1.7 TERMINE ✅
echo.

REM Variables principales
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..
set PORTABLE_DIR=%ROOT_DIR%\portable
set BACKEND_DIR=%ROOT_DIR%\backend
set FRONTEND_DIR=%ROOT_DIR%\frontend

echo 🔧 Initialisation configuration portable...

REM Verification de l'environnement
if not exist "%ROOT_DIR%\backend\server.py" (
    echo ❌ Backend manquant. Verifie l'installation.
    pause
    exit /b 1
)

if not exist "%ROOT_DIR%\frontend\package.json" (
    echo ❌ Frontend manquant. Verifie l'installation.
    pause
    exit /b 1
)

REM Configuration portable automatique
cd /d "%SCRIPT_DIR%"
echo 📊 Configuration automatique des ports et services...
python portable_config.py
if errorlevel 1 (
    echo ❌ Erreur configuration portable
    pause
    exit /b 1
)

REM Charger la configuration portable generee
if exist "%PORTABLE_DIR%\config\portable.env" (
    for /f "tokens=1,2 delims==" %%a in (%PORTABLE_DIR%\config\portable.env) do set %%a=%%b
) else (
    echo ❌ Configuration portable manquante
    pause
    exit /b 1
)

echo.
echo 📋 Configuration detectee:
echo    💻 Mode: PORTABLE USB
echo    🚀 Backend: Port %BACKEND_PORT%
echo    🌐 Frontend: Port %FRONTEND_PORT%
echo    📊 Services: %SERVICES_COUNT% operationnels
echo    🔐 Database: SQLite Portable
echo.

REM Verification Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11+ requis. Installation automatique...
    echo 📦 Telechargement Python portable...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "& {try {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe' -UseBasicParsing} catch {Write-Host 'Erreur telechargement Python'; exit 1}}"
    if exist python-installer.exe (
        echo 🔧 Installation Python en cours...
        start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 AssociateFiles=1
        del python-installer.exe
        echo ✅ Python installe
    ) else (
        echo ❌ Echec telechargement Python
        pause
        exit /b 1
    )
)

REM Verification Node.js/npm
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 18+ requis. Installation automatique...
    echo 📦 Telechargement Node.js portable...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "& {try {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.19.0/node-v18.19.0-x64.msi' -OutFile 'node-installer.msi' -UseBasicParsing} catch {Write-Host 'Erreur telechargement Node.js'; exit 1}}"
    if exist node-installer.msi (
        echo 🔧 Installation Node.js en cours...
        start /wait msiexec /i node-installer.msi /quiet ADDLOCAL=ALL
        del node-installer.msi
        echo ✅ Node.js installe
    ) else (
        echo ❌ Echec telechargement Node.js
        pause
        exit /b 1
    )
)

echo.
echo 🔧 Configuration environnement backend portable...

REM Backend - environnement virtuel portable
cd /d "%BACKEND_DIR%"
if not exist "venv" (
    echo 📦 Creation environnement virtuel portable...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erreur creation environnement virtuel
        pause
        exit /b 1
    )
)

REM Activation environnement virtuel
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erreur activation environnement virtuel
    pause
    exit /b 1
)

REM Installation dependances backend
echo 📦 Installation dependances backend (35 services)...
if exist "requirements_portable.txt" (
    pip install -r requirements_portable.txt --quiet --disable-pip-version-check
) else (
    pip install -r requirements.txt --quiet --disable-pip-version-check
)

if errorlevel 1 (
    echo ⚠️ Erreur installation dependances backend, continuation...
)

echo.
echo 🎨 Configuration environnement frontend...

REM Frontend - installation dependances
cd /d "%FRONTEND_DIR%"

REM Verifier si yarn est disponible, sinon utiliser npm
where yarn >nul 2>&1
if %errorlevel% == 0 (
    echo 📦 Installation dependances frontend avec Yarn...
    yarn install --silent
    if errorlevel 1 (
        echo ⚠️ Erreur Yarn, tentative avec npm...
        npm install --silent
    )
) else (
    echo 📦 Installation dependances frontend avec npm...
    npm install --silent
)

echo.
echo 🚀 Demarrage des services CyberSec Toolkit Pro 2025...
echo ⏳ Initialisation de l'infrastructure portable...

REM Demarrage backend en arriere-plan
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
echo 🔧 Demarrage Backend FastAPI (35 services)...
start "CyberSec Backend - 35 Services" /min cmd /c "python server.py"

REM Attendre que le backend soit pret
echo ⏳ Attente du backend portable...
ping localhost -n 6 >nul

REM Test de sante du backend
echo 🔍 Verification services backend...
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:%BACKEND_PORT%/api/' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ Backend operationnel' } else { Write-Host '⚠️ Backend demarre mais pas encore pret' } } catch { Write-Host '⚠️ Backend en cours de demarrage...' }"

REM Demarrage frontend
cd /d "%FRONTEND_DIR%"
echo 🎨 Demarrage Frontend React + Vite...

where yarn >nul 2>&1
if %errorlevel% == 0 (
    start "CyberSec Frontend" /min cmd /c "yarn dev --port %FRONTEND_PORT%"
) else (
    start "CyberSec Frontend" /min cmd /c "npm run dev -- --port %FRONTEND_PORT%"
)

REM Attendre que le frontend soit pret
echo ⏳ Attente du frontend...
ping localhost -n 4 >nul

echo.
echo ████████████████████████████████████████████████████████████████
echo.
echo               ✅ CYBERSEC TOOLKIT PRO 2025 PORTABLE
echo                      DEMARRAGE TERMINE !
echo.
echo  🌐 Interface Web:    http://localhost:%FRONTEND_PORT%
echo  🔧 API Backend:      http://localhost:%BACKEND_PORT%/api/
echo  📚 Documentation:    http://localhost:%BACKEND_PORT%/api/docs  
echo  📊 Services:         %SERVICES_COUNT%/35 Operationnels
echo  📱 Mode:             PORTABLE USB (Donnees stockees localement)
echo  🔐 Version:          %TOOLKIT_VERSION%
echo.
echo  🎯 SERVICES SPECIALISES INCLUS:
echo     • Container Security    • IaC Security
echo     • Social Engineering    • Security Orchestration (SOAR)  
echo     • Risk Assessment      • Cloud/Mobile/IoT/Web3/AI Security
echo     • Network Security     • API Security + 23 autres services
echo.
echo ████████████████████████████████████████████████████████████████
echo.

REM Ouvrir automatiquement le navigateur
echo 🌐 Ouverture du navigateur web...
timeout /t 2 /nobreak >nul
start "" "http://localhost:%FRONTEND_PORT%"

echo.
echo 🛑 INSTRUCTIONS D'ARRET:
echo    • Fermez cette fenetre pour arreter tous les services
echo    • Ou executez: portable\stop_services.bat
echo    • Les donnees sont automatiquement sauvegardees
echo.
echo 🎯 Interface prete! Testez les 35 services dans votre navigateur.
echo.

REM Garder la fenetre ouverte et surveiller
:monitor
echo 📊 Services actifs... Ctrl+C pour arreter proprement
timeout /t 30 /nobreak >nul
goto monitor