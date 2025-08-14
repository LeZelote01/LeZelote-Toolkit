#!/bin/bash
# CyberSec Toolkit Pro 2025 - Lanceur Linux portable
# Configuration et démarrage automatique pour Linux

echo "🐧 Configuration Linux portable..."

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PORTABLE_DIR="$ROOT_DIR/portable"

# Configuration portable
python3 "$PORTABLE_DIR/launcher/portable_config.py" --production

# Charger la configuration portable avec priorité
source "$PORTABLE_DIR/config/portable.env"

# Export des variables portable pour les sous-processus
export $(cat "$PORTABLE_DIR/config/portable.env" | xargs)

echo "📦 Installation des dépendances portable..."

# Backend - environnement virtuel portable
if [ ! -d "$ROOT_DIR/backend/venv" ]; then
    echo "🔧 Création environnement virtuel portable..."
    cd "$ROOT_DIR/backend"
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source "$ROOT_DIR/backend/venv/bin/activate"

# Installation des dépendances portables
echo "📦 Installation dépendances backend portable..."
pip install -r "$ROOT_DIR/backend/requirements_portable.txt"

# Frontend - installation des dépendances
echo "📦 Installation dépendances frontend..."
cd "$ROOT_DIR/frontend"
if command -v yarn >/dev/null 2>&1; then
    yarn install
else
    npm install
fi

echo "🚀 Démarrage des services portable..."

# Démarrage backend en arrière-plan
cd "$ROOT_DIR/backend"
source venv/bin/activate
python server.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du backend portable..."
sleep 5

# Démarrage frontend
cd "$ROOT_DIR/frontend"
if command -v yarn >/dev/null 2>&1; then
    yarn dev &
else
    npm run dev &
fi
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
sleep 3

echo ""
echo "✅ CyberSec Toolkit Pro 2025 PORTABLE démarré !"
echo ""
echo "🌐 Interface : http://localhost:$FRONTEND_PORT"
echo "🔧 API Backend : http://localhost:$BACKEND_PORT/api/"
echo "📚 Documentation : http://localhost:$BACKEND_PORT/api/docs"
echo ""
echo "📱 Mode PORTABLE activé - Données stockées sur USB"
echo ""
echo "🛑 Pour arrêter : Ctrl+C ou ./portable/stop_services.sh"

# Ouvrir le navigateur
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$FRONTEND_PORT"
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:$FRONTEND_PORT"
fi

# Attendre les processus
wait