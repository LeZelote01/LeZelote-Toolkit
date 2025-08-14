# 🔧 GUIDE D'ADAPTATION EMERGENT - CYBERSEC TOOLKIT PRO 2025

**Objectif:** Adapter les outils Emergent pour utiliser les ports natifs du projet CyberSec Toolkit Pro 2025

---

## 🎯 CONFIGURATION PORTS

### Ports Natifs du Projet (À RESPECTER)
- **Backend FastAPI:** Port 8000
- **Frontend React/Vite:** Port 8002
- **Base de données:** SQLite portable (pas de port)

### Ports Emergent Standard
- **Backend:** Port 8001
- **Frontend:** Port 3000
- **MongoDB:** Port 27017

---

## 🔄 SYSTÈME DE PROXY CONFIGURÉ

Un système de proxy Nginx a été mis en place pour assurer la compatibilité:

```bash
# Backend: 8001 -> 8000
http://localhost:8001/api/* -> http://localhost:8000/api/*

# Frontend: 3000 -> 8002  
http://localhost:3000/* -> http://localhost:8002/*
```

### Fichiers de Configuration

#### Backend Proxy (`/etc/nginx/sites-available/cybersec-backend-proxy`)
```nginx
server {
    listen 8001;
    server_name localhost;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

#### Frontend Proxy (`/etc/nginx/sites-available/cybersec-frontend-proxy`)
```nginx
server {
    listen 3000;
    server_name localhost;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        
        # WebSocket support pour Vite HMR
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🚀 COMMANDES DE GESTION

### Démarrage du Projet
```bash
# 1. Démarrer le backend (port natif 8000)
cd /app/backend
python server.py &

# 2. Démarrer le frontend (port natif 8002)
cd /app/frontend
yarn start &

# 3. Démarrer les proxies Nginx
sudo systemctl start nginx
```

### Arrêt du Projet
```bash
# Arrêter les processus Python et Node
pkill -f "python.*server.py"
pkill -f "node.*vite"

# Redémarrer Nginx pour nettoyer les proxies
sudo systemctl restart nginx
```

### Vérification des Services
```bash
# Services natifs du projet
curl http://localhost:8000/api/          # Backend natif
curl http://localhost:8002               # Frontend natif

# Services via proxy (compatibilité Emergent)
curl http://localhost:8001/api/          # Backend via proxy
curl http://localhost:3000               # Frontend via proxy
```

---

## 📡 UTILISATION AVEC LES OUTILS EMERGENT

### Pour les Tests Backend
```bash
# Utiliser le port proxy 8001 au lieu de 8000
deep_testing_backend_v2 --backend-url http://localhost:8001
```

### Pour les Tests Frontend
```bash
# Utiliser le port proxy 3000 au lieu de 8002
auto_frontend_testing_agent --frontend-url http://localhost:3000
```

### Pour les Screenshots
```python
# Dans les scripts Playwright, utiliser le port proxy 3000
await page.goto('http://localhost:3000')
```

---

## ⚙️ VARIABLES D'ENVIRONNEMENT

### Backend (`/app/backend/.env`)
```env
# CONFIGURATION NATIVE - NE PAS MODIFIER
BACKEND_PORT=8000
FRONTEND_PORT=8002
CORS_ORIGINS=http://localhost:8002

# Configuration base de données
DATABASE_TYPE=sqlite
MONGO_URL=sqlite:///portable/database/data/cybersec_toolkit.db

# Configuration IA
EMERGENT_LLM_KEY=sk-emergent-26d9350AaE6796a692
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini
```

### Frontend (`/app/frontend/.env`)
```env
# CONFIGURATION NATIVE - NE PAS MODIFIER
REACT_APP_BACKEND_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8000

# Configuration interface
REACT_APP_TITLE=CyberSec Toolkit Pro 2025 PORTABLE
REACT_APP_VERSION=1.0.0-portable
```

---

## 🛠️ SCRIPTS UTILITAIRES

### Script de Configuration Proxy (`/app/proxy_config.sh`)
```bash
#!/bin/bash
# Configure automatiquement les proxies Nginx
chmod +x /app/proxy_config.sh
/app/proxy_config.sh
```

### Script de Démarrage Complet
```bash
#!/bin/bash
# Démarrage complet avec proxies
cd /app

# 1. Configuration des proxies
./proxy_config.sh

# 2. Démarrage backend
cd backend && python server.py &
BACKEND_PID=$!

# 3. Démarrage frontend  
cd ../frontend && yarn start &
FRONTEND_PID=$!

echo "✅ CyberSec Toolkit Pro 2025 démarré"
echo "   Backend natif: http://localhost:8000"
echo "   Frontend natif: http://localhost:8002"
echo "   Backend proxy: http://localhost:8001"
echo "   Frontend proxy: http://localhost:3000"
```

---

## 🔍 MONITORING ET DEBUG

### Vérification des Processus
```bash
# Services natifs
ps aux | grep -E "(python.*server|node.*vite)"

# Ports utilisés
netstat -tlnp | grep -E "(8000|8002|8001|3000)"

# Status Nginx
sudo systemctl status nginx
sudo nginx -t
```

### Logs Debug
```bash
# Logs backend
tail -f /app/backend/server.log

# Logs frontend
tail -f /app/frontend/frontend.log

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## ⚠️ POINTS D'ATTENTION

### À Respecter Absolument
1. **NE JAMAIS modifier les ports 8000/8002** dans les fichiers de configuration
2. **Utiliser les ports proxy 8001/3000** pour les outils Emergent
3. **Maintenir les scripts de démarrage natifs** du projet
4. **Respecter l'architecture SQLite portable** (pas de MongoDB)

### Base de Données
- **Type:** SQLite portable (adaptateur Mongo-like)
- **Localisation:** `/app/portable/database/data/cybersec_toolkit.db`
- **Pas de port réseau** (fichier local)
- **Collections:** Compatibles syntaxe MongoDB mais stockage SQLite

### Services Supervisor
- **Désactivés:** Les services supervisor Emergent sont arrêtés
- **Gestion manuelle:** Démarrage via scripts natifs du projet
- **Nginx:** Utilisé uniquement pour les proxies

---

## 🎯 RÉSUMÉ CONFIGURATION

| Service | Port Natif | Port Proxy | URL Emergent |
|---------|------------|------------|--------------|
| Backend | 8000 | 8001 | http://localhost:8001 |
| Frontend | 8002 | 3000 | http://localhost:3000 |
| API Docs | 8000/api/docs | 8001/api/docs | http://localhost:8001/api/docs |

**Configuration optimale pour maintenir la compatibilité native du projet tout en permettant l'utilisation des outils Emergent.**

---

*📝 Guide d'adaptation réalisé par E1 Agent - Emergent*  
*🔄 Version: 1.0.0*  
*⚡ Date: 14 Août 2025*  
*🎯 Objectif: Compatibilité parfaite entre CyberSec Toolkit Pro 2025 et outils Emergent*