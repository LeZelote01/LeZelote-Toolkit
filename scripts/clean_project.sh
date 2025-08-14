#!/bin/bash
# Script de nettoyage du projet CyberSec Toolkit Pro 2025
# Supprime tous les éléments qui ne font pas partie de l'architecture

echo "🧹 NETTOYAGE DU PROJET"
echo "======================"

cd /app

echo "🗑️ Suppression des caches et fichiers temporaires..."

# Suppression des caches Node.js et Yarn
rm -rf v8-compile-cache-*/ 
rm -rf yarn--*/
rm -rf node-jiti/
rm -rf core-js-banners/
rm -f core-js-banners

# Suppression des sockets et fichiers temporaires
rm -f mongodb-*.sock
rm -f .env.example
rm -f .gitconfig

# Suppression du yarn.lock dans le dossier racine (doit être seulement dans frontend)
rm -f yarn.lock

# Nettoyage des dossiers temporaires Node.js
find . -name "node_modules" -type d -not -path "./frontend/node_modules" -exec rm -rf {} + 2>/dev/null || true
find . -name "dist" -type d -not -path "./frontend/dist" -exec rm -rf {} + 2>/dev/null || true
find . -name ".next" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Nettoyage des caches Python
find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo
echo "✅ NETTOYAGE TERMINÉ"
echo "Éléments supprimés :"
echo "  • Caches Node.js et Yarn temporaires"
echo "  • Sockets MongoDB temporaires" 
echo "  • Fichiers de configuration temporaires"
echo "  • Caches Python (__pycache__, *.pyc)"
echo
echo "📁 STRUCTURE FINALE PROPRE :"
ls -1 /app | grep -v "^\." | sort