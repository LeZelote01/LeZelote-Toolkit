# 🛡️ **GUIDE COMPLET - TESTER CYBERSEC TOOLKIT PRO 2025 SUR UBUNTU 22**

## 📋 **PRÉREQUIS SYSTÈME**

### **Configuration Minimale Recommandée**
```bash
OS: Ubuntu 22.04 LTS
RAM: 8GB minimum, 16GB recommandé
CPU: Dual-core minimum, Quad-core recommandé
Stockage: 10GB d'espace libre
Réseau: Connexion Internet pour téléchargement initial
```

### **Vérification Version Ubuntu**
```bash
lsb_release -a
# Doit afficher Ubuntu 22.04 LTS
```

---

## 🔧 **INSTALLATION DES DÉPENDANCES SYSTÈME**

### **1. Mise à jour du système**
```bash
sudo apt update && sudo apt upgrade -y
```

### **2. Installation Python 3.11+**
```bash
# Vérifier la version Python
python3 --version

# Si Python < 3.11, installer via deadsnakes PPA
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# Créer un alias (optionnel)
echo 'alias python=python3.11' >> ~/.bashrc
source ~/.bashrc
```

### **3. Installation Node.js et Yarn**
```bash
# Installation Node.js 18+ via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Vérification version
node --version  # Doit être >= 18.x
npm --version

# Installation Yarn
npm install -g yarn
yarn --version
```

### **4. Installation Git**
```bash
sudo apt install git -y
git --version
```

### **5. Installation outils de développement**
```bash
sudo apt install curl wget build-essential -y
```

---

## 📦 **RÉCUPÉRATION ET INSTALLATION DU PROJET**

### **1. Clonage du repository**
```bash
# Créer un dossier de travail
mkdir -p ~/cybersec-toolkit
cd ~/cybersec-toolkit

# Cloner le projet
git clone https://github.com/LeZelote01/Toolkit.git .

# Vérifier le contenu
ls -la
# Vous devriez voir: backend/, frontend/, README.md, etc.
```

### **2. Installation Backend (FastAPI + Python)**
```bash
cd ~/cybersec-toolkit/backend

# Créer un environnement virtuel Python
python3.11 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier l'activation (le prompt doit afficher (venv))
which python  # Doit pointer vers venv/bin/python

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements_portable.txt

# Vérification installation
pip list | grep fastapi
pip list | grep uvicorn
```

### **3. Installation Frontend (React + Vite)**
```bash
cd ~/cybersec-toolkit/frontend

# Installer les dépendances avec Yarn
yarn install

# Vérifier l'installation
yarn list --depth=0 | grep react
yarn list --depth=0 | grep vite
```

---

## 🚀 **DÉMARRAGE DE L'APPLICATION**

### **1. Préparation de l'environnement**
```bash
# Créer les dossiers nécessaires pour la base portable
mkdir -p ~/cybersec-toolkit/portable/database/data
mkdir -p ~/cybersec-toolkit/portable/logs
mkdir -p ~/cybersec-toolkit/portable/config
```

### **2. Vérification configuration**
```bash
# Vérifier la config backend
cat ~/cybersec-toolkit/backend/.env

# La config doit contenir:
# BACKEND_PORT=8000
# FRONTEND_PORT=8002
# PORTABLE_MODE=true
# DATABASE_TYPE=sqlite
```

### **3. Démarrage Backend (Terminal 1)**
```bash
cd ~/cybersec-toolkit/backend

# Activer l'environnement virtuel
source venv/bin/activate

# Démarrer le serveur FastAPI
python server.py

# Vous devriez voir:
# 🚀 Démarrage en mode PORTABLE sur port 8000
# INFO: Started server process
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### **4. Démarrage Frontend (Terminal 2)**
```bash
cd ~/cybersec-toolkit/frontend

# Définir l'URL du backend
export VITE_BACKEND_URL=http://localhost:8000

# Démarrer le serveur de développement Vite
yarn start

# Vous devriez voir:
# Local:   http://localhost:8002/
# Network: http://192.168.x.x:8002/
```

---

## ✅ **TESTS ET VALIDATIONS**

### **1. Vérification Backend (Terminal 3)**
```bash
# Test endpoint principal
curl http://localhost:8000/api/

# Réponse attendue (JSON):
# {
#   "status": "operational",
#   "message": "CyberSec Toolkit Pro 2025 - PORTABLE USB Ready",
#   "version": "1.0.0-portable",
#   "services": {
#     "total_planned": 35,
#     "implemented": 8,
#     "phase": "Sprint 1.4 - Services Cybersécurité Avancés (87.5% terminé)"
#   }
# }

# Test health check
curl http://localhost:8000/api/health

# Test services opérationnels
curl http://localhost:8000/api/assistant/status
curl http://localhost:8000/api/pentesting/
curl http://localhost:8000/api/monitoring/
```

### **2. Vérification Frontend**
```bash
# Test accessibilité frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002
# Doit retourner: 200

# Ouvrir dans le navigateur
firefox http://localhost:8002 &
# ou
google-chrome http://localhost:8002 &
# ou
xdg-open http://localhost:8002
```

### **3. Vérification Navigation Web**

**Dans votre navigateur, allez sur `http://localhost:8002`**

Vous devriez voir :
- ✅ **Titre** : "🛡️ CyberSec Toolkit Pro 2025"
- ✅ **Sidebar** : Navigation avec 8 services
- ✅ **État du Projet** : Status operational, 35 services planifiés
- ✅ **Services Opérationnels** : Liste des 8+ services avec badges verts

### **4. Test des Services Fonctionnels**

**Testez chaque service via la navigation sidebar :**

1. **Dashboard** (`/`) - Doit afficher l'état général
2. **Assistant IA** (`/assistant`) - Interface de chat
3. **Pentesting** (`/pentest`) - Scanner OWASP
4. **Incident Response** (`/incident-response`) - Gestion incidents
5. **Digital Forensics** (`/digital-forensics`) - Investigation
6. **Compliance** (`/compliance`) - Conformité multi-standards
7. **Vulnerability Management** (`/vulnerability-management`) - Dashboard CVSS
8. **Business** (`/business`) - Services business

---

## 🔍 **TESTS AVANCÉS ET API**

### **1. Tests API Backend Complets**
```bash
# Créer un script de test
cat > ~/test_api.sh << 'EOF'
#!/bin/bash
echo "🧪 Tests API CyberSec Toolkit Pro 2025"
echo "======================================="

BASE_URL="http://localhost:8000"

# Test endpoints principaux
echo "📡 Test API Status..."
curl -s $BASE_URL/api/ | jq .status

echo "🏥 Test Health Check..."
curl -s $BASE_URL/api/health | jq .status

echo "🤖 Test Assistant IA..."
curl -s $BASE_URL/api/assistant/status | jq .status

echo "🛡️ Test Pentesting..."
curl -s $BASE_URL/api/pentesting/ | jq .status

echo "🚨 Test Incident Response..."
curl -s $BASE_URL/api/incident-response/ | jq .status

echo "🔬 Test Digital Forensics..."
curl -s $BASE_URL/api/digital-forensics/ | jq .status

echo "📋 Test Compliance..."
curl -s $BASE_URL/api/compliance/ | jq .status

echo "🔍 Test Vulnerability Management..."
curl -s $BASE_URL/api/vulnerability-management/ | jq .status

echo "📊 Test Monitoring..."
curl -s $BASE_URL/api/monitoring/ | jq .status

echo "🎯 Test Threat Intelligence..."
curl -s $BASE_URL/api/threat-intelligence/ | jq .status

echo "🔴 Test Red Team..."
curl -s $BASE_URL/api/red-team/ | jq .status

echo "🔵 Test Blue Team..."
curl -s $BASE_URL/api/blue-team/ | jq .status

echo "✅ Tests terminés!"
EOF

chmod +x ~/test_api.sh
~/test_api.sh
```

### **2. Test Intégration Frontend-Backend**
```bash
# Test avec session de chat Assistant IA
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, peux-tu m'aider avec un audit sécurité?",
    "session_id": "test-session"
  }' | jq .
```

### **3. Monitoring des Logs**
```bash
# Terminal 4 - Surveiller les logs backend
tail -f ~/cybersec-toolkit/backend.log

# Terminal 5 - Surveiller les logs frontend
tail -f ~/cybersec-toolkit/frontend.log
```

---

## 📊 **VÉRIFICATION DES PERFORMANCES**

### **1. Test de charge simple**
```bash
# Installer Apache Bench (optionnel)
sudo apt install apache2-utils -y

# Test de charge léger sur API
ab -n 100 -c 10 http://localhost:8000/api/

# Test de charge sur frontend
ab -n 50 -c 5 http://localhost:8002/
```

### **2. Vérification mémoire et CPU**
```bash
# Surveiller l'utilisation des ressources
htop

# Ou avec des outils système
ps aux | grep python  # Processus backend
ps aux | grep node     # Processus frontend

# Utilisation mémoire
free -h

# Utilisation disque
df -h
```

---

## 🐛 **DÉPANNAGE COURANT**

### **Problème : Backend ne démarre pas**
```bash
# Vérifier les logs
cd ~/cybersec-toolkit/backend
source venv/bin/activate
python server.py

# Erreurs courantes et solutions:
# - Port 8000 déjà utilisé: sudo lsof -i :8000
# - Dépendances manquantes: pip install -r requirements_portable.txt
# - Permissions SQLite: mkdir -p portable/database/data
```

### **Problème : Frontend ne se connecte pas au backend**
```bash
# Vérifier la variable d'environnement
echo $VITE_BACKEND_URL  # Doit être http://localhost:8000

# Redémarrer avec la bonne config
cd ~/cybersec-toolkit/frontend
VITE_BACKEND_URL=http://localhost:8000 yarn start
```

### **Problème : Erreurs CORS**
```bash
# Vérifier la config CORS dans backend/.env
grep CORS ~/cybersec-toolkit/backend/.env
# Doit contenir: CORS_ORIGINS=http://localhost:8002
```

### **Problème : Base de données SQLite**
```bash
# Vérifier les permissions
ls -la ~/cybersec-toolkit/portable/database/data/

# Recréer si nécessaire
rm -rf ~/cybersec-toolkit/portable/database/data/*
mkdir -p ~/cybersec-toolkit/portable/database/data
```

---

## 📸 **CAPTURES D'ÉCRAN ATTENDUES**

### **Dashboard Principal**
- Titre : "🛡️ CyberSec Toolkit Pro 2025"
- Status : operational  
- Services planifiés : 35
- Services implémentés : 8
- Phase : Sprint 1.4

### **Services Fonctionnels**
- Assistant IA : Interface de chat
- Pentesting : Scanner OWASP avec options
- Digital Forensics : Interface investigation
- Compliance : Frameworks multiples
- Vulnerability Management : Dashboard CVSS

---

## 🎯 **VALIDATION FINALE**

### **Checklist de Validation ✅**
```bash
# Cochez chaque élément après test

□ Backend répond sur http://localhost:8000/api/
□ Frontend accessible sur http://localhost:8002
□ Navigation sidebar fonctionnelle (8 liens)
□ Assistant IA répond aux messages
□ Pages services se chargent sans erreur
□ API backends intégrées fonctionnent
□ Aucune erreur console critique
□ Interface responsive (mobile/desktop)
□ Temps de chargement < 3 secondes
□ Base SQLite créée automatiquement
```

### **Tests Supplémentaires (Optionnel)**
```bash
# Test de robustesse
# Redémarrer le backend plusieurs fois
# Tester la navigation rapide entre pages
# Vérifier la persistence des données
# Tester avec différents navigateurs (Firefox, Chrome, Edge)
```

---

## 🚀 **UTILISATION AVANCÉE**

### **Mode Développement Continu**
```bash
# Terminal 1 - Backend avec reload automatique
cd ~/cybersec-toolkit/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend avec hot reload
cd ~/cybersec-toolkit/frontend
VITE_BACKEND_URL=http://localhost:8000 yarn dev
```

### **Customisation et Tests**
```bash
# Modifier la configuration
nano ~/cybersec-toolkit/backend/.env

# Tester de nouvelles fonctionnalités
# Les modifications sont appliquées automatiquement
```

---

## 📞 **SUPPORT ET RESSOURCES**

### **Documentation Technique**
- **Architecture** : `~/cybersec-toolkit/ARCHITECTURE.md`
- **Guide Développeur** : `~/cybersec-toolkit/GUIDE_DEVELOPPEUR.md`
- **Status Projet** : `~/cybersec-toolkit/PROJECT_STATUS.md`
- **API Documentation** : http://localhost:8000/api/docs (Swagger)

### **Logs et Debugging**
```bash
# Logs détaillés backend
tail -f ~/cybersec-toolkit/backend.log

# Logs frontend
tail -f ~/cybersec-toolkit/frontend.log

# Console navigateur (F12) pour errors frontend
```

---

## ✅ **RÉSUMÉ COMMANDES RAPIDES**

```bash
# Démarrage rapide complet
cd ~/cybersec-toolkit

# Terminal 1 - Backend
cd backend && source venv/bin/activate && python server.py

# Terminal 2 - Frontend  
cd frontend && VITE_BACKEND_URL=http://localhost:8000 yarn start

# Test rapide
curl http://localhost:8000/api/
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002

# Ouvrir navigateur
xdg-open http://localhost:8002
```

**🎉 Félicitations ! Vous avez maintenant CyberSec Toolkit Pro 2025 fonctionnel sur Ubuntu 22 !**

Le projet devrait afficher **11 services cybersécurité opérationnels** avec une interface moderne et des intégrations API complètes. Profitez de cette suite cybersécurité portable avancée ! 🛡️