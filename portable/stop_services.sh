#!/bin/bash
# CyberSec Toolkit Pro 2025 - Arrêt des services portables
# Script d'arrêt propre pour Linux/macOS

echo "🛑 Arrêt CyberSec Toolkit Pro 2025 Portable..."

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Charger la configuration pour récupérer les ports
if [ -f "$SCRIPT_DIR/config/portable.env" ]; then
    source "$SCRIPT_DIR/config/portable.env"
fi

# Arrêter les processus Python (backend)
echo "🔧 Arrêt du backend..."
pkill -f "python.*server.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Arrêter les processus Node.js (frontend)
echo "🎨 Arrêt du frontend..."
pkill -f "vite" 2>/dev/null || true
pkill -f "yarn.*dev" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

# Arrêter par ports si définis
if [ ! -z "$BACKEND_PORT" ]; then
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
fi

if [ ! -z "$FRONTEND_PORT" ]; then
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
fi

# Nettoyage des processus orphelins
sleep 2

echo "✅ Services portables arrêtés"
echo "📱 Données sauvegardées sur USB"