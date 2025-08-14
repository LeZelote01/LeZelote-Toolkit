#!/bin/bash
echo "🔐 Renforcement sécurité production..."

# Permissions des fichiers sensibles
chmod 600 portable/config/*.env 2>/dev/null || true
chmod 600 backend/.env 2>/dev/null || true
chmod 600 frontend/.env 2>/dev/null || true

# Permissions des scripts
chmod +x scripts/*.sh
chmod +x START_TOOLKIT.*

# Sécurisation de la base de données
chmod 600 portable/database/data/*.db 2>/dev/null || true

echo "✅ Sécurité renforcée"
