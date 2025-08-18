# Guide d'Installation - LeZelote Toolkit

## Vue d'Ensemble

Le **LeZelote Toolkit** est un framework complet de tests de pénétration conçu pour fonctionner directement depuis une clé USB. Ce guide vous guidera à travers le processus d'installation sur Windows, Linux et macOS.

## 🔧 Prérequis Système

### Configuration Minimale Requise
- **Stockage** : Clé USB 32GB+ (64GB+ recommandé)
- **RAM** : 8GB minimum (16GB+ recommandé)
- **Processeur** : 64-bit, 2+ cœurs
- **OS** : Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+

### Plateformes Supportées
- ✅ Windows (64-bit)
- ✅ Linux (64-bit) 
- ✅ macOS (64-bit Intel/Apple Silicon)

## 📥 Installation

### Option 1: Installation Automatique (Recommandée)

#### Windows
```powershell
# Télécharger le toolkit
git clone https://github.com/LeZelote01/LeZelote-Toolkit.git
cd LeZelote-Toolkit

# Lancer l'installation automatique
.\scripts\install\setup.ps1
```

#### Linux/macOS
```bash
# Télécharger le toolkit
git clone https://github.com/LeZelote01/LeZelote-Toolkit.git
cd LeZelote-Toolkit

# Rendre exécutable et lancer
chmod +x scripts/install/setup.sh
./scripts/install/setup.sh
```

### Option 2: Installation Manuelle

#### 1. Préparer l'Environnement

**Python 3.9+**
```bash
# Vérifier la version Python
python --version  # ou python3 --version

# Si nécessaire, installer Python 3.9+
# Windows: Télécharger depuis python.org
# Linux: sudo apt install python3.9 python3-pip
# macOS: brew install python@3.9
```

#### 2. Installer les Dépendances

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Dépendances système supplémentaires
# Linux:
sudo apt update
sudo apt install nmap sqlmap aircrack-ng hashcat

# macOS:
brew install nmap sqlmap aircrack-ng hashcat

# Windows: Les binaires sont inclus dans tools/binaries/windows/
```

#### 3. Configuration Initiale

```bash
# Configurer l'environnement
python scripts/install/setup_environment.py

# Vérifier l'installation
python scripts/install/verify_installation.py

# Configurer les outils
chmod +x scripts/install/configure_tools.sh
./scripts/install/configure_tools.sh
```

## 🐳 Installation Docker (Alternative)

Pour un environnement isolé :

```bash
# Déployer avec Docker
python scripts/install/deploy_docker.py

# Ou manuellement
docker-compose -f runtime/docker/docker-compose.yml up -d
```

## 🔐 Configuration Sécurisée

### 1. Configuration des API Keys

Éditez `/config/api_keys.yaml` :
```yaml
# Shodan API (optionnel)
shodan:
  api_key: "votre_cle_shodan"

# VirusTotal API (optionnel)  
virustotal:
  api_key: "votre_cle_virustotal"

# Autres services...
```

### 2. Configuration Réseau

Éditez `/config/network_config.yaml` :
```yaml
# Configuration proxy (si nécessaire)
proxy:
  http_proxy: "http://proxy.example.com:8080"
  https_proxy: "https://proxy.example.com:8080"
  no_proxy: "localhost,127.0.0.1"

# Paramètres de scan
scanning:
  max_threads: 50
  timeout: 300
  rate_limit: 1000
```

### 3. Gestion des Autorisations

**IMPORTANT** : Configurez toujours les autorisations avant utilisation :

```bash
# Démarrer l'interface CLI
python run_cli.py

# Suivre le menu : Configuration > Consent Management
# Ajouter les cibles autorisées
```

## 🚀 Premier Lancement

### Interface CLI
```bash
# Lancer l'interface en ligne de commande
python run_cli.py

# Ou utiliser les scripts de lancement
# Windows: launch.bat
# Linux/macOS: ./launch.sh
```

### Interface Web
```bash
# Démarrer l'interface web
cd interfaces/web
python app.py

# Accéder via navigateur : http://localhost:8080
```

## ✅ Vérification de l'Installation

### Tests Automatiques
```bash
# Vérification complète
python scripts/install/verify_installation.py

# Tests spécifiques
python -m pytest tests/unit/ -v
```

### Tests Manuels
1. **CLI** : `python run_cli.py` doit afficher le menu principal
2. **Modules** : Tester chaque module depuis le menu CLI
3. **Base de données** : Vérifier la création de `core/db/knowledge_base.db`
4. **Logging** : Vérifier les logs dans `/logs/`

## 🛠 Configuration pour Clé USB

### Préparation de la Clé USB
```bash
# Formater la clé USB (FAT32 ou exFAT pour compatibilité multi-OS)
# Copier l'intégralité du dossier LeZelote-Toolkit

# Rendre portable (Linux/macOS)
chmod +x launch.sh
chmod +x scripts/install/setup.sh

# Windows: Créer un raccourci vers launch.bat
```

### Structure Recommandée sur USB
```
USB-Drive/
├── LeZelote-Toolkit/         # Toolkit principal
├── Portable-Python/          # Runtime Python portable (optionnel)
├── Documentation/             # Guides et références
└── Results/                   # Dossier pour stocker les résultats
```

## 📁 Structure Post-Installation

Après installation réussie :
```
LeZelote-Toolkit/
├── core/                     # Moteur principal ✅
├── modules/                  # Modules fonctionnels ✅
├── tools/                    # Outils intégrés ✅
├── data/                     # Données et ressources ✅
├── interfaces/               # Interfaces CLI/Web ✅
├── logs/                     # Journaux système ✅
├── outputs/                  # Résultats de scans ✅
├── reports/                  # Rapports générés ✅
├── config/                   # Configuration ✅
└── runtime/                  # Environnement d'exécution ✅
```

## 🔧 Dépannage Installation

### Problèmes Courants

#### Erreur: "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier le PYTHONPATH
export PYTHONPATH="/chemin/vers/LeZelote-Toolkit:$PYTHONPATH"
```

#### Erreur: Permissions refusées (Linux/macOS)
```bash
# Donner les permissions d'exécution
chmod +x scripts/install/setup.sh
chmod +x launch.sh

# Si problème persistant, utiliser sudo pour l'installation système
sudo ./scripts/install/setup.sh
```

#### Erreur: Antivirus Windows
```bash
# Ajouter une exception antivirus pour le dossier LeZelote-Toolkit
# Désactiver temporairement Windows Defender pour l'installation

# Alternative: Utiliser Windows Subsystem for Linux (WSL)
wsl --install
# Puis installer dans WSL
```

#### Problème: Outils manquants
```bash
# Vérifier les outils installés
python scripts/maintenance/system_check.py

# Installer manuellement les outils manquants
# Consulter logs/system.log pour détails
```

### Support et Assistance

- **Documentation** : Consultez `/docs/` pour guides détaillés
- **FAQ** : Voir `docs/troubleshooting.md`
- **Logs** : Analyser `/logs/system.log` et `/logs/error.log`
- **Tests** : Lancer `python -m pytest tests/` pour diagnostics

### Contact

- **Issues** : GitHub Issues page
- **Discussion** : GitHub Discussions  
- **Sécurité** : security@pentestusb.dev

---

## ⚠️ Notes Légales

**IMPORTANT** : Ce toolkit est destiné uniquement aux tests autorisés. Assurez-vous d'avoir les permissions appropriées avant toute utilisation.

- Utilisez uniquement sur vos propres systèmes ou avec autorisation écrite
- Respectez les lois locales et réglementations
- Suivez les pratiques de divulgation responsable

---

**Installation terminée avec succès ! Consultez `docs/user_guide.md` pour commencer à utiliser le toolkit.**