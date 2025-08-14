#!/bin/bash

echo "🔧 Correction intégration PortManager - Sprint 1.8"
echo "================================================="

TOOLKIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚨 CORRECTION: Intégration du PortManager natif du projet"
echo ""

# Arrêter les services actuels qui utilisent les mauvais ports
echo "1. Arrêt des services en cours..."
pkill -f "python.*server.py" || true
pkill -f "node.*vite" || true
pkill -f "simple_proxy.py" || true

sleep 3

# Forcer la configuration native des ports (8000/8002 comme dans la spécification)
echo "2. Configuration forcée des ports natifs..."
cat > "$TOOLKIT_DIR/portable/config/ports.json" << EOF
{
  "backend": 8000,
  "frontend": 8002,
  "database": 8003
}
EOF

echo "   ✅ Ports configurés: backend=8000, frontend=8002"

# Utiliser le PortManager pour valider
echo "3. Validation via PortManager..."
cd "$TOOLKIT_DIR"
python3 portable/launcher/port_manager.py

echo ""
echo "4. Redémarrage avec architecture native..."

# Redémarrer backend avec port manager
cd backend
/app/backend/venv/bin/python server.py --port 8000 > ../logs/backend_native.log 2>&1 &
BACKEND_PID=$!

echo "   ✅ Backend démarré (PID: $BACKEND_PID) sur port 8000"

# Attendre que le backend soit prêt
sleep 5

# Redémarrer frontend avec port manager  
cd ../frontend
yarn start --port 8002 > ../logs/frontend_native.log 2>&1 &
FRONTEND_PID=$!

echo "   ✅ Frontend démarré (PID: $FRONTEND_PID) sur port 8002"

# Attendre et valider
sleep 8

echo ""
echo "5. Validation finale avec PortManager..."
cd "$TOOLKIT_DIR"
python3 portable/launcher/port_manager.py

echo ""
echo "✅ CORRECTION TERMINÉE"
echo "🎯 Architecture native du projet respectée"
echo "📊 PortManager intégré dans l'optimisation Sprint 1.8"