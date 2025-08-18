# Guide de Dépannage - LeZelote Toolkit

## 🔍 Diagnostic Rapide

### Script de Vérification Automatique
```bash
# Diagnostic complet du système
python scripts/maintenance/system_check.py

# Options de diagnostic
python scripts/maintenance/system_check.py --component resources    # Vérif ressources
python scripts/maintenance/system_check.py --component tools       # Vérif outils
python scripts/maintenance/system_check.py --component network     # Vérif réseau
python scripts/maintenance/system_check.py --component database    # Vérif BDD
```

### Logs de Débogage
```bash
# Analyser les logs principaux
tail -f logs/system.log          # Log système général
tail -f logs/error.log           # Erreurs seulement  
tail -f logs/debug.log           # Debug détaillé
tail -f logs/audit_trail.log     # Journal d'audit

# Recherche d'erreurs spécifiques
grep -i "error" logs/system.log
grep -i "failed" logs/*.log
grep -A5 -B5 "CRITICAL" logs/error.log
```

## ❌ Problèmes d'Installation

### Erreur: "Module not found"
**Symptôme** : `ImportError: No module named 'xyz'`

**Solutions** :
```bash
# 1. Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# 2. Vérifier l'environnement Python
python --version
pip list | grep -i problematic_module

# 3. Corriger le PYTHONPATH
export PYTHONPATH="/path/to/LeZelote-Toolkit:$PYTHONPATH"

# 4. Utiliser un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Erreur: Permissions refusées (Linux/macOS)
**Symptôme** : `PermissionError: [Errno 13] Permission denied`

**Solutions** :
```bash
# 1. Donner permissions d'exécution
chmod +x launch.sh
chmod +x scripts/install/setup.sh
chmod -R 755 scripts/

# 2. Correction propriétaire
sudo chown -R $USER:$USER /path/to/LeZelote-Toolkit

# 3. Installation système (si nécessaire)
sudo python scripts/install/setup.sh

# 4. Utiliser sudo pour certains outils
sudo apt install nmap aircrack-ng  # Linux
```

### Problème: Antivirus Windows
**Symptôme** : Fichiers supprimés automatiquement, exécution bloquée

**Solutions** :
```bash
# 1. Ajouter exception Windows Defender
# Ouvrir Windows Security > Protection contre virus et menaces
# > Paramètres de protection contre virus et menaces
# > Ajouter ou supprimer des exclusions
# Ajouter : C:\path\to\LeZelote-Toolkit\

# 2. Désactiver temporairement (pour installation)
# Windows Security > Protection en temps réel : Désactivé

# 3. Alternative WSL (recommandée)
wsl --install
wsl
git clone https://github.com/LeZelote01/LeZelote-Toolkit.git
cd LeZelote-Toolkit
./scripts/install/setup.sh
```

## 🔧 Problèmes de Configuration

### Base de Données Corrompue
**Symptôme** : `database is locked`, `corrupted database`

**Solutions** :
```bash
# 1. Vérifier processus utilisant la BDD
lsof +D core/db/  # Linux/macOS
# Tuer processus si nécessaire

# 2. Réparation automatique
python scripts/maintenance/repair_database.py

# 3. Recréation BDD
rm core/db/knowledge_base.db
python core/db/models.py  # Recréer structure

# 4. Restauration depuis sauvegarde
python scripts/maintenance/backup.py --restore backup_file.tar.gz
```

### Configuration Réseau
**Symptôme** : Timeouts, erreurs de connexion

**Solutions** :
```bash
# 1. Test connectivité
ping 8.8.8.8
nslookup google.com

# 2. Configuration proxy
# Éditer config/network_config.yaml
proxy:
  http_proxy: "http://proxy.company.com:8080"
  https_proxy: "https://proxy.company.com:8080"

# 3. Firewall
sudo ufw allow 8080  # Linux
# Windows: Windows Firewall > Autoriser application

# 4. DNS
# Éditer /etc/resolv.conf (Linux)
nameserver 8.8.8.8
nameserver 1.1.1.1
```

### Outils Manquants
**Symptôme** : `Tool 'nmap' not found`, erreurs d'exécution

**Solutions** :
```bash
# 1. Installation outils système
# Linux
sudo apt update
sudo apt install nmap sqlmap aircrack-ng hashcat nikto

# macOS
brew install nmap sqlmap aircrack-ng hashcat

# Windows (utiliser binaires intégrés)
# Les outils sont dans tools/binaries/windows/

# 2. Vérifier PATH
echo $PATH
which nmap

# 3. Configuration manuelle
# Éditer config/tool_profiles.yaml
tools:
  nmap:
    path: "/usr/bin/nmap"
    enabled: true
```

## 🚀 Problèmes de Performance

### Consommation Mémoire Élevée
**Symptôme** : Système lent, out of memory

**Solutions** :
```bash
# 1. Monitorer utilisation
python scripts/maintenance/system_check.py --component resources

# 2. Optimiser configuration
# Éditer config/main_config.yaml
performance:
  max_threads: 10          # Réduire threads
  memory_limit: "2GB"      # Limiter mémoire
  cache_size: "256MB"      # Réduire cache

# 3. Nettoyer données temporaires
python scripts/maintenance/clean_logs.py
python scripts/maintenance/optimize_storage.py

# 4. Ajuster profils de scan
# Utiliser profils "light" au lieu de "comprehensive"
```

### Scans Lents
**Symptôme** : Scans prennent trop de temps

**Solutions** :
```bash
# 1. Optimiser paramètres réseau
# config/scan_profiles.yaml
scan_settings:
  timeout: 30              # Réduire timeout
  parallel_hosts: 50       # Augmenter parallélisme
  threads_per_host: 10     # Équilibrer threads

# 2. Utiliser profils rapides
quick_scan.json au lieu de full_audit.json

# 3. Segmenter les cibles
192.168.1.0/26 au lieu de 192.168.1.0/24

# 4. Horaires optimaux
# Planifier scans lourds hors heures de pointe
```

### Saturation CPU
**Symptôme** : CPU à 100%, système non réactif

**Solutions** :
```bash
# 1. Limiter processus
# config/main_config.yaml
resource_limits:
  max_cpu_percent: 70
  max_processes: 20

# 2. Priorisation
nice -n 10 python run_cli.py  # Réduire priorité

# 3. Surveillance
htop
python scripts/maintenance/health_monitor.py

# 4. Refroidissement système
# Vérifier ventilateurs, température CPU
```

## 🔌 Problèmes d'Intégration Outils

### Metasploit Non Fonctionnel
**Symptôme** : `msfconsole not found`, erreurs MSF

**Solutions** :
```bash
# 1. Installation Metasploit
# Linux
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall

# 2. Initialisation base de données
msfdb init
msfconsole -q -x "db_status"

# 3. Configuration dans le toolkit
# config/tool_profiles.yaml
metasploit:
  msfconsole_path: "/usr/bin/msfconsole"
  database_enabled: true
  api_enabled: true
```

### Burp Suite Professional
**Symptôme** : Licence invalide, erreurs d'activation

**Solutions** :
```bash
# 1. Vérifier licence
# Burp Suite > License > Check for updates

# 2. Configuration API
# config/tool_profiles.yaml
burpsuite:
  jar_path: "/path/to/burpsuite_pro.jar"
  api_enabled: true
  api_key: "your_api_key"
  headless: true

# 3. Alternative Community Edition
# Utiliser Burp Community (limité mais gratuit)
burpsuite:
  edition: "community"
  jar_path: "/path/to/burpsuite_community.jar"
```

### ZAP Proxy Issues
**Symptôme** : ZAP ne démarre pas, erreurs GUI

**Solutions** :
```bash
# 1. Mode headless
# config/tool_profiles.yaml
zap:
  headless: true
  daemon_mode: true
  api_key: "your_zap_api_key"

# 2. Java configuration
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk"
java -version

# 3. Port conflicts
# Changer port par défaut (8080 -> 8081)
zap:
  port: 8081
  host: "localhost"
```

## 📡 Problèmes Réseau et Connectivité

### Erreurs de Timeout
**Symptôme** : `Connection timeout`, scans échouent

**Solutions** :
```bash
# 1. Ajuster timeouts
# config/network_config.yaml
timeouts:
  connect: 10
  read: 30
  scan: 300

# 2. Test connectivité manuelle
telnet target_ip port
nc -zv target_ip port

# 3. Configuration interface réseau
# S'assurer d'utiliser la bonne interface
ip route show  # Linux
route print    # Windows
```

### Problèmes DNS
**Symptôme** : `Name resolution failed`

**Solutions** :
```bash
# 1. Test résolution DNS
nslookup target.com
dig target.com

# 2. Configuration DNS locale
# /etc/resolv.conf (Linux)
nameserver 8.8.8.8
nameserver 1.1.1.1

# 3. Cache DNS
# Linux
sudo systemctl flush-dns
# Windows
ipconfig /flushdns
# macOS
sudo dscacheutil -flushcache
```

### Firewall et IDS/IPS
**Symptôme** : Scans bloqués, détection

**Solutions** :
```bash
# 1. Mode furtif
# config/scan_profiles.yaml
stealth_scan:
  timing: "T1"             # Très lent
  fragmentation: true      # Fragmenter paquets
  decoy_scans: true       # Scans leurre
  randomize_hosts: true    # Ordre aléatoire

# 2. Évasion IDS
evasion:
  source_port: 53          # Port DNS
  max_rate: 100           # Limiter taux
  delay_between_probes: 1  # Délai entre sondes

# 3. Techniques avancées
# Utiliser proxies, VPN, Tor si autorisé
```

## 📊 Problèmes de Rapports

### Génération PDF Échoue
**Symptôme** : `Failed to generate PDF`, erreurs ReportLab

**Solutions** :
```bash
# 1. Vérifier dépendances
pip install reportlab pillow

# 2. Permissions fichiers
chmod 755 reports/
chmod 644 data/templates/reports/*

# 3. Mémoire insuffisante
# Réduire taille rapport ou augmenter mémoire système

# 4. Alternative formats
# Générer en HTML puis convertir manuellement
```

### Templates Corrompus
**Symptôme** : Rapports mal formatés, erreurs template

**Solutions** :
```bash
# 1. Restaurer templates par défaut
cp data/templates/reports/default.html.bak data/templates/reports/default.html

# 2. Validation templates
python -c "
import jinja2
env = jinja2.Environment()
template = env.from_string(open('data/templates/reports/default.html').read())
print('Template valid')
"

# 3. Réinitialiser templates
python scripts/maintenance/reset_configs.py --templates-only
```

## 🔒 Problèmes de Sécurité et Autorisations

### Consent Manager Erreurs
**Symptôme** : `Target not authorized`, erreurs de consentement

**Solutions** :
```bash
# 1. Ajouter autorisation manuelle
# CLI: Configuration > Consent Management > Add Consent
# Ou éditer directement data/databases/project_db.sqlite

# 2. Vérifier format cibles
# Utiliser CIDR: 192.168.1.0/24
# Ou plages: 192.168.1.1-254

# 3. Debug consent manager
python -c "
from core.security.consent_manager import ConsentManager
cm = ConsentManager()
print(cm.list_consents())
"
```

### Erreurs Cryptographiques
**Symptôme** : Erreurs SSL/TLS, échecs crypto

**Solutions** :
```bash
# 1. Mettre à jour certificats
# Linux
sudo apt update && sudo apt install ca-certificates

# 2. Configuration SSL
# config/main_config.yaml
ssl:
  verify_certificates: false  # Si certificats auto-signés
  tls_version: "1.2"         # Forcer version TLS

# 3. Debugging SSL
openssl s_client -connect target:443 -servername target
```

## 🧪 Tests et Validation

### Tests Unitaires Échouent
**Symptôme** : Tests pytest en erreur

**Solutions** :
```bash
# 1. Exécuter tests avec détails
python -m pytest tests/ -v --tb=long

# 2. Tests spécifiques
python -m pytest tests/unit/test_core/ -v
python -m pytest tests/integration/ -k "not external"

# 3. Ignorer tests problématiques temporairement
python -m pytest tests/ --ignore=tests/performance/

# 4. Réinitialiser environnement test
rm -rf .pytest_cache/
rm -rf tests/__pycache__/
```

### Validation Configuration
**Symptôme** : Configuration invalide, erreurs parsing

**Solutions** :
```bash
# 1. Valider YAML
python -c "
import yaml
with open('config/main_config.yaml') as f:
    config = yaml.safe_load(f)
    print('Config valid')
"

# 2. Restaurer configuration par défaut
cp config/main_config.yaml.default config/main_config.yaml

# 3. Validation schema
python scripts/maintenance/system_check.py --component config
```

## 📞 Support et Ressources

### Collecte d'Informations pour Support
```bash
# 1. Générer rapport diagnostic complet
python scripts/maintenance/system_check.py --full-report > diagnostic_report.txt

# 2. Collecter logs essentiels
tar -czf logs_backup.tar.gz logs/

# 3. Information système
uname -a                    # Linux/macOS
python --version
pip list > installed_packages.txt

# Windows
systeminfo > system_info.txt
```

### Contacts Support
- **Issues GitHub** : https://github.com/LeZelote01/LeZelote-Toolkit/issues
- **Discussions** : https://github.com/LeZelote01/LeZelote-Toolkit/discussions
- **Documentation** : `/docs/` dans le toolkit
- **Email sécurité** : security@pentestusb.dev

### Ressources Utiles
- **Installation Guide** : `docs/installation.md`
- **User Guide** : `docs/user_guide.md`
- **Developer Guide** : `docs/developer_guide.md`
- **API Reference** : `docs/api_reference.md`
- **Changelog** : `docs/changelog.md`

## 🔍 FAQ

### Q: Le toolkit peut-il fonctionner sans connexion internet ?
**R**: Oui, partiellement. Les scans locaux fonctionnent, mais OSINT et mises à jour nécessitent internet.

### Q: Comment changer la langue de l'interface ?
**R**: Actuellement anglais/français. Éditer `config/user_preferences.yaml` :
```yaml
localization:
  language: "fr"  # ou "en"
```

### Q: Puis-je ajouter mes propres outils ?
**R**: Oui, consultez `docs/developer_guide.md` section "Custom Tools Integration".

### Q: Le toolkit fonctionne-t-il sur ARM/M1 Mac ?
**R**: Oui, mais certains outils binaires peuvent nécessiter Rosetta 2.

### Q: Comment sauvegarder ma configuration ?
**R**: 
```bash
python scripts/maintenance/backup.py --config-only
```

### Q: Puis-je utiliser le toolkit en mode cloud ?
**R**: Possible avec Docker, mais attention aux aspects légaux et de sécurité.

---

## ⚡ Actions de Dépannage Rapides

```bash
# Reset complet (en cas de problème majeur)
python scripts/maintenance/reset_configs.py --full-reset
python scripts/install/verify_installation.py

# Nettoyage système
python scripts/maintenance/clean_logs.py
python scripts/maintenance/optimize_storage.py

# Réparation base de données
python scripts/maintenance/repair_database.py --auto-fix

# Check santé système
python scripts/maintenance/health_monitor.py --alerts-only
```

---

**Si le problème persiste après avoir suivi ce guide, n'hésitez pas à créer un issue GitHub avec les détails du diagnostic et les logs pertinents.**