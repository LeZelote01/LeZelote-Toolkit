# Guide Utilisateur - LeZelote Toolkit

## Introduction

Le **LeZelote Toolkit** est un framework complet de tests de pénétration qui unifie plus de 100 outils de sécurité dans une interface cohérente. Ce guide vous apprend à utiliser efficacement toutes les fonctionnalités.

## 🚀 Démarrage Rapide

### Lancement du Toolkit
```bash
# Interface CLI (recommandée)
python run_cli.py

# Interface Web
cd interfaces/web && python app.py
# Puis naviguer vers http://localhost:8080

# Scripts de lancement
./launch.sh        # Linux/macOS
launch.bat         # Windows
```

### Premier Scan Rapide
```bash
# Depuis l'interface CLI
1. Sélectionner "1 - Reconnaissance"
2. Choisir "Network Scanner"
3. Entrer la cible : 192.168.1.0/24
4. Sélectionner profil "Quick Scan"
5. Démarrer le scan
```

## 🎯 Interface CLI Principale

### Menu Principal
```
╭────────┬──────────────────────────┬──────────────────────────────────────╮
│   1    │ Reconnaissance           │ Network scanning and OSINT gathering │
│   2    │ Vulnerability Assessment │ Scan for security vulnerabilities    │
│   3    │ Exploitation             │ Execute exploits and gain access     │
│   4    │ Post-Exploitation        │ Privilege escalation and persistence │
│   5    │ Reporting                │ Generate comprehensive reports       │
│   6    │ Project Management       │ Manage scan projects and sessions    │
│   7    │ Configuration            │ Tool settings and preferences        │
│   8    │ Dashboard                │ Real-time monitoring dashboard       │
│   9    │ Help & Documentation     │ View help and documentation          │
│   0    │ Exit                     │ Exit the application                 │
╰────────┴──────────────────────────┴──────────────────────────────────────╯
```

## 🔍 Module 1: Reconnaissance

### Scan Réseau
**Outils intégrés** : Nmap, RustScan, Masscan, Netdiscover

```bash
# Navigation CLI
Menu Principal > 1 (Reconnaissance) > 1 (Network Scanner)

# Options de scan
- Quick Scan     : Scan rapide des ports courants
- Full Scan      : Scan complet tous ports
- Stealth Scan   : Scan furtif évitant la détection
- Custom Scan    : Configuration personnalisée

# Exemples de cibles
192.168.1.1           # IP unique
192.168.1.0/24        # Réseau complet
10.0.0.1-50          # Plage d'IP
example.com          # Nom de domaine
```

### Énumération de Domaines
**Outils intégrés** : Amass, Subfinder, Sublist3r, Certificate Transparency

```bash
# Types d'énumération
- Subdomain Discovery    : Découverte sous-domaines
- DNS Enumeration       : Énumération DNS complète
- Certificate Analysis   : Analyse certificats SSL
- Domain Takeover Check : Vérification de prise de contrôle

# Techniques utilisées
- Brute force DNS
- Certificate Transparency logs
- Search engine dorking
- Passive DNS analysis
```

### Collecte OSINT
**Outils intégrés** : theHarvester, SpiderFoot, Recon-ng, Maltego

```bash
# Types de collecte
- Email Harvesting      : Collecte d'emails
- Social Media Intel    : Intelligence réseaux sociaux
- Metadata Analysis     : Analyse de métadonnées
- Public Records        : Recherche registres publics

# Sources utilisées
- Moteurs de recherche
- Réseaux sociaux
- Bases de données publiques
- Archives web
```

## 🛡️ Module 2: Évaluation des Vulnérabilités

### Scan d'Applications Web
**Outils intégrés** : OWASP ZAP, Nuclei, Nikto, Burp Suite

```bash
# Types de scan
- OWASP Top 10         : Vulnérabilités critiques web
- Full Web Assessment  : Évaluation complète
- API Security Test    : Tests sécurité API
- Custom Payloads      : Charges utiles personnalisées

# Vulnérabilités détectées
- SQL Injection
- Cross-Site Scripting (XSS)
- CSRF, SSRF, XXE
- Authentication flaws
- Authorization issues
```

### Scan de Vulnérabilités Réseau
**Outils intégrés** : Nessus, OpenVAS, Nmap Scripts

```bash
# Profils de scan
- Critical Only        : Vulnérabilités critiques uniquement
- Compliance Scan     : Scan de conformité
- Full Assessment     : Évaluation complète
- Custom Profile      : Profil personnalisé

# Types de vulnérabilités
- CVE récents
- Configurations par défaut
- Services non sécurisés
- Certificats expirés
```

### Audit Cloud
**Outils intégrés** : Prowler, ScoutSuite, CloudMapper

```bash
# Plateformes supportées
- AWS Security Assessment
- Azure Security Review  
- Google Cloud Audit
- Kubernetes Security

# Vérifications
- IAM Policies
- Storage Buckets
- Network Security
- Compliance Standards
```

## ⚔️ Module 3: Exploitation

### Exploitation Web
**Outils intégrés** : SQLMap, XSStrike, Commix

```bash
# Types d'exploitation
- SQL Injection        : Exploitation SQLi automatique
- XSS Exploitation     : Exploitation Cross-Site Scripting
- Command Injection    : Injection de commandes
- File Upload Bypass   : Contournement upload fichiers

# Techniques avancées
- Blind SQL injection
- Time-based attacks
- Second-order injection
- WAF bypass techniques
```

### Exploitation Réseau
**Outils intégrés** : Metasploit, Impacket, CrackMapExec

```bash
# Types d'attaques
- Service Exploitation : Exploitation services réseau
- SMB Attacks         : Attaques protocole SMB
- Brute Force        : Attaques par force brute
- Pass-the-Hash      : Attaques de hachage

# Protocoles ciblés
- SMB/CIFS
- RDP
- SSH
- FTP/FTPS
```

### Ingénierie Sociale
**Outils intégrés** : Gophish, King Phisher, Social-Engineer Toolkit

```bash
# Campagnes de phishing
- Email Templates     : Templates d'emails
- Landing Pages      : Pages de capture
- SMS Phishing       : Campagnes SMS
- Voice Phishing     : Attaques téléphoniques

# Métriques suivies
- Taux d'ouverture
- Taux de clics
- Taux de soumission
- Temps de réaction
```

## 🔓 Module 4: Post-Exploitation

### Accès aux Identifiants
**Outils intégrés** : Mimikatz, LaZagne, Pypykatz

```bash
# Techniques d'extraction
- Windows Credentials  : Identifiants Windows
- Browser Passwords   : Mots de passe navigateurs
- Hash Dumping       : Extraction de hachages
- Token Manipulation  : Manipulation de tokens

# Types d'identifiants
- Plaintext passwords
- NTLM hashes  
- Kerberos tickets
- SSH keys
```

### Mouvement Latéral
**Outils intégrés** : PsExec, WMIExec, Evil-WinRM

```bash
# Techniques de mouvement
- SMB Lateral Movement : Mouvement via SMB
- WMI Execution       : Exécution via WMI
- PowerShell Remoting : Remoting PowerShell
- SSH Tunneling      : Tunneling SSH

# Reconnaissance interne
- Network mapping
- Service enumeration
- User enumeration
- Share discovery
```

### Persistance
**Outils intégrés** : Empire, Sliver, Metasploit

```bash
# Mécanismes de persistance
- Registry Modification : Modification registre
- Scheduled Tasks      : Tâches planifiées
- Service Installation : Installation services
- DLL Hijacking       : Détournement DLL

# Techniques furtives
- Living off the land
- Memory-only execution
- Fileless persistence
- Process injection
```

## 📊 Module 5: Reporting

### Génération de Rapports
**Formats disponibles** : PDF, DOCX, HTML, JSON, CSV

```bash
# Types de rapports
- Executive Summary   : Résumé exécutif
- Technical Report   : Rapport technique détaillé
- Compliance Report  : Rapport de conformité
- Vulnerability List : Liste des vulnérabilités

# Personnalisation
- Custom templates
- Company branding
- Risk scoring
- Remediation priorities
```

### Analyse des Données
```bash
# Métriques calculées
- Risk scoring automatique
- Trend analysis
- Vulnerability correlation
- Attack path mapping

# Visualisations
- Risk matrix
- Timeline attacks
- Network topology
- Compliance status
```

## 🗂️ Module 6: Gestion de Projets

### Organisation des Projets
```bash
# Structure de projet
- Project metadata
- Target scope
- Timeline planning
- Resource allocation

# Gestion des sessions
- Session recording
- Progress tracking
- Evidence collection
- Report versioning
```

### Collaboration
```bash
# Fonctionnalités équipe
- Multi-user projects
- Role-based access
- Comment system
- Review process

# Synchronisation
- Real-time updates
- Conflict resolution
- Version control
- Backup/restore
```

## ⚙️ Module 7: Configuration

### Paramètres Généraux
```bash
# Configuration système
config/
├── main_config.yaml        # Configuration principale
├── tool_profiles.yaml      # Profils d'outils
├── network_config.yaml     # Configuration réseau
├── api_keys.yaml          # Clés API
├── user_preferences.yaml   # Préférences utilisateur
└── scan_profiles.yaml     # Profils de scan
```

### Gestion des Autorisations
**CRITIQUE** : Toujours configurer avant utilisation

```bash
# Ajout d'autorisation
1. Menu Configuration > Consent Management
2. Add New Consent
3. Remplir les détails :
   - Target: 192.168.1.0/24
   - Scope: Network scanning, web testing
   - Expiry: 2024-12-31
   - Authorized by: John Doe <john@company.com>

# Vérification des autorisations
- List Active Consents
- Verify Target Authorization
- Revoke Expired Consents
```

### Profils de Scan
```bash
# Profils prédéfinis
- quick_scan.json         # Scan rapide (15 min)
- full_audit.json        # Audit complet (4-8h)
- web_app.json           # Application web (2-4h)
- network.json           # Scan réseau (1-2h)
- compliance.json        # Vérification conformité (2-3h)

# Création profil custom
{
  "name": "custom_web_scan",
  "modules": ["reconnaissance", "vulnerability"],
  "tools": ["nmap", "zap", "nikto"],
  "parameters": {
    "intensity": "aggressive",
    "timeout": 3600,
    "threads": 20
  }
}
```

## 📈 Module 8: Dashboard

### Surveillance en Temps Réel
```bash
# Métriques affichées
- System resources (CPU, RAM, Disk)
- Active scans progress
- Recent findings
- Tool status

# Alertes automatiques
- High-severity findings
- System resource alerts
- Tool failures
- Scan completion
```

### Historique des Activités
```bash
# Journaux d'activité
- User actions
- Scan progress
- Finding discoveries
- System events

# Analyse des tendances
- Scan frequency
- Finding types
- Performance metrics
- Success rates
```

## 🔍 Workflows Recommandés

### Workflow Standard de Pentest
```bash
1. PRÉPARATION
   - Créer nouveau projet
   - Configurer autorisations
   - Définir scope et objectifs

2. RECONNAISSANCE
   - Network discovery
   - Service enumeration
   - OSINT gathering
   - Domain enumeration

3. SCANNING & ENUMERATION
   - Port scanning
   - Service version detection
   - Web application discovery
   - Vulnerability scanning

4. VULNERABILITY ASSESSMENT
   - Automated scanning
   - Manual verification
   - Risk assessment
   - Exploitation feasibility

5. EXPLOITATION
   - Proof of concept
   - Privilege escalation
   - Lateral movement
   - Persistence (si autorisé)

6. POST-EXPLOITATION
   - Data gathering
   - Network mapping
   - Additional targets
   - Evidence collection

7. REPORTING
   - Generate technical report
   - Create executive summary
   - Provide recommendations
   - Schedule presentation
```

### Workflow Audit de Conformité
```bash
1. PRÉPARATION
   - Identifier standards (PCI-DSS, HIPAA, etc.)
   - Configurer profils conformité
   - Préparer checklist

2. DISCOVERY
   - Asset inventory
   - Service identification
   - Configuration review

3. COMPLIANCE TESTING
   - Policy verification
   - Control testing
   - Gap analysis

4. DOCUMENTATION
   - Compliance matrix
   - Gap analysis report
   - Remediation roadmap

5. VALIDATION
   - Re-testing après corrections
   - Compliance certification
   - Continuous monitoring
```

## 🔧 Commandes Avancées

### Interface CLI Avancée
```bash
# Commandes directes
python run_cli.py --scan --target 192.168.1.0/24 --profile quick
python run_cli.py --report --project "audit_2024" --format pdf
python run_cli.py --config --show-consents

# Batch operations
python run_cli.py --batch scan_list.txt --output results/
python run_cli.py --import findings.json --merge-project "main_audit"
```

### API REST
```python
import requests

# Démarrer un scan
response = requests.post('http://localhost:8080/api/scan', json={
    'target': '192.168.1.100',
    'profile': 'network_comprehensive',
    'project': 'my_pentest'
})

# Vérifier le statut
scan_id = response.json()['scan_id']
status = requests.get(f'http://localhost:8080/api/scan/{scan_id}/status')

# Récupérer les résultats
results = requests.get(f'http://localhost:8080/api/scan/{scan_id}/results')
```

## ⚠️ Bonnes Pratiques

### Sécurité Opérationnelle
```bash
# Avant chaque engagement
1. Vérifier les autorisations écrites
2. Confirmer le scope exacte
3. Établir les canaux de communication
4. Planifier les fenêtres d'intervention

# Pendant l'engagement
1. Respecter les limites de scope
2. Documenter toutes les actions
3. Éviter les disruptions
4. Communiquer les découvertes critiques

# Après l'engagement
1. Nettoyer les traces (si demandé)
2. Sécuriser les données sensibles
3. Livrer les rapports de manière sécurisée
4. Suivre la remediation
```

### Performance et Ressources
```bash
# Optimisation des scans
- Utiliser profils adaptés à l'environnement
- Ajuster threads selon ressources
- Planifier scans lourds hors heures
- Monitorer impact réseau

# Gestion des données
- Nettoyer régulièrement /outputs/
- Archiver anciens projets
- Optimiser bases de données
- Sauvegarder configurations importantes
```

## 🆘 Résolution de Problèmes

### Erreurs Courantes
```bash
# "Target not in authorized scope"
Solution: Ajouter cible dans Consent Management

# "Tool execution failed"  
Solution: Vérifier installation outil dans system_check.py

# "Insufficient permissions"
Solution: Vérifier permissions fichiers et sudo si nécessaire

# "Database locked"
Solution: Redémarrer application, vérifier processus concurrent
```

### Diagnostics
```bash
# Vérification système complète
python scripts/maintenance/system_check.py

# Analyse des logs
tail -f logs/system.log
grep ERROR logs/error.log

# Test de connectivité
python -c "from core.utils.network_utils import check_network_connectivity; print(check_network_connectivity('8.8.8.8'))"
```

### Support
- **Documentation complète** : `/docs/`
- **Dépannage** : `docs/troubleshooting.md`
- **API Reference** : `docs/api_reference.md`
- **Issues** : GitHub Issues
- **Discussions** : GitHub Discussions

---

## 📖 Ressources Complémentaires

- **Developer Guide** : `docs/developer_guide.md`
- **API Reference** : `docs/api_reference.md`  
- **Troubleshooting** : `docs/troubleshooting.md`
- **Changelog** : `docs/changelog.md`

---

**🎯 Vous êtes maintenant prêt à utiliser efficacement le LeZelote Toolkit ! Consultez les autres guides pour approfondir vos connaissances.**