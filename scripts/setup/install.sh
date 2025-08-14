#!/bin/bash
# Script d'installation CyberSec Toolkit Pro 2025

echo "🚀 Installation CyberSec Toolkit Pro 2025"
echo "========================================="

# Vérification des prérequis
echo "📋 Vérification des prérequis..."

command -v docker >/dev/null 2>&1 || { 
    echo "❌ Docker requis mais non installé. Aborting." >&2; 
    exit 1; 
}

command -v docker-compose >/dev/null 2>&1 || { 
    echo "❌ Docker Compose requis mais non installé. Aborting." >&2; 
    exit 1; 
}

echo "✅ Docker et Docker Compose trouvés"

# Copie des fichiers d'environnement
echo "⚙️ Configuration des variables d'environnement..."

if [ ! -f backend/.env ]; then
    cp .env.example backend/.env
    echo "✅ backend/.env créé depuis .env.example"
fi

if [ ! -f frontend/.env ]; then
    echo "REACT_APP_BACKEND_URL=http://localhost:8001" > frontend/.env
    echo "✅ frontend/.env créé"
fi

# Installation des dépendances
echo "📦 Installation des dépendances..."
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install

# Démarrage des services
echo "🐳 Démarrage des services..."
docker-compose up -d

# Attente que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 10

# Vérification
echo "🔍 Vérification des services..."
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ Backend opérationnel"
else
    echo "⚠️ Backend non accessible"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend opérationnel"
else
    echo "⚠️ Frontend non accessible"
fi

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "🌐 Accès aux services :"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001/api/"
echo "   Documentation API: http://localhost:8001/api/docs"
echo ""
echo "📚 Consultez README.md pour plus d'informations"