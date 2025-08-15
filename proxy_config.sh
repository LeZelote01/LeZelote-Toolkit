#!/bin/bash

# Configuration du proxy pour adapter l'environnement Kubernetes aux ports natifs du projet
# Backend: 8001 -> 8000 (port natif du projet)
# Frontend: 3000 -> 8002 (port natif du projet)

echo "🔧 Configuration du proxy pour CyberSec Toolkit Pro 2025..."

# Arrêter les services supervisord existants
sudo supervisorctl stop all 2>/dev/null || true

# Configurer le proxy inverse pour le backend
echo "📡 Configuration proxy backend (8001 -> 8000)..."
sudo tee /etc/nginx/sites-available/cybersec-backend-proxy > /dev/null <<EOF
server {
    listen 8001;
    server_name localhost;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
    }
}
EOF

# Configurer le proxy inverse pour le frontend
echo "🌐 Configuration proxy frontend (3000 -> 8002)..."
sudo tee /etc/nginx/sites-available/cybersec-frontend-proxy > /dev/null <<EOF
server {
    listen 3000;
    server_name localhost;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        
        # WebSocket support pour Vite HMR
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Activer les sites
sudo ln -sf /etc/nginx/sites-available/cybersec-backend-proxy /etc/nginx/sites-enabled/ 2>/dev/null || true
sudo ln -sf /etc/nginx/sites-available/cybersec-frontend-proxy /etc/nginx/sites-enabled/ 2>/dev/null || true

# Redémarrer nginx
sudo nginx -t && sudo systemctl reload nginx 2>/dev/null || true

echo "✅ Proxy configuré:"
echo "   Backend: http://localhost:8001 -> http://localhost:8000"
echo "   Frontend: http://localhost:3000 -> http://localhost:8002"
echo ""
echo "🎯 Les outils Emergent peuvent maintenant utiliser les ports standards"
echo "   tout en respectant la configuration native du projet (8000/8002)"