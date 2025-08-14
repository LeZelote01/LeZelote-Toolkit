#!/bin/bash
# CyberSec Toolkit Pro 2025 - Lanceur macOS portable
# Configuration et démarrage automatique pour macOS

echo "🍎 Configuration macOS portable..."

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PORTABLE_DIR="$ROOT_DIR/portable"

# Configuration portable
python3 "$PORTABLE_DIR/launcher/portable_config.py"

# Charger la configuration
source "$PORTABLE_DIR/config/portable.env"

echo "📦 Installation des dépendances portable..."

# Vérifier Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 requis. Installez avec: brew install python@3.11"
    exit 1
fi

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

# Frontend - vérifier Node.js et Yarn
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js requis. Installez avec: brew install node"
    exit 1
fi

if ! command -v yarn >/dev/null 2>&1; then
    echo "📦 Installation de Yarn..."
    npm install -g yarn
fi

# Installation des dépendances frontend
echo "📦 Installation dépendances frontend..."
cd "$ROOT_DIR/frontend"
yarn install

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
yarn dev &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
sleep 3

echo ""
echo "✅ CyberSec Toolkit Pro 2025 PORTABLE démarré sur macOS !"
echo ""
echo "🌐 Interface : http://localhost:$FRONTEND_PORT"
echo "🔧 API Backend : http://localhost:$BACKEND_PORT/api/"
echo "📚 Documentation : http://localhost:$BACKEND_PORT/api/docs"
echo ""
echo "📱 Mode PORTABLE activé - Données stockées sur USB"
echo ""
echo "🛑 Pour arrêter : Ctrl+C ou ./portable/stop_services.sh"

# Ouvrir le navigateur
open "http://localhost:$FRONTEND_PORT"

# Attendre les processus
wait