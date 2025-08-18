# Référence API - LeZelote Toolkit

## Vue d'Ensemble

Le LeZelote Toolkit expose ses fonctionnalités via plusieurs interfaces API:
- **API REST** - Interface HTTP/JSON pour intégration externe
- **API Python** - Interface programmatique directe
- **CLI API** - Interface en ligne de commande
- **WebSocket API** - Temps réel et notifications

## 🌐 API REST

### Configuration de Base
```
Base URL: http://localhost:8080/api/v1
Content-Type: application/json
Authentication: API Key (Header: X-API-Key)
```

### Authentification
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}

Response:
{
  "token": "jwt_token_here",
  "expires_in": 3600
}
```

### Endpoints Principaux

#### Gestion des Projets

##### Lister les Projets
```http
GET /api/v1/projects
Authorization: Bearer {jwt_token}

Response:
{
  "projects": [
    {
      "id": "proj_123",
      "name": "Audit Website 2024",
      "created_at": "2024-08-17T10:30:00Z",
      "status": "active",
      "target_count": 5
    }
  ]
}
```

##### Créer un Projet
```http
POST /api/v1/projects
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "New Pentest Project",
  "description": "Security audit for example.com",
  "targets": ["example.com", "192.168.1.0/24"],
  "scope": {
    "modules": ["reconnaissance", "vulnerability"],
    "exclude_paths": ["/admin", "/private"]
  }
}

Response:
{
  "project_id": "proj_456",
  "status": "created",
  "message": "Project created successfully"
}
```

##### Obtenir Détails Projet
```http
GET /api/v1/projects/{project_id}
Authorization: Bearer {jwt_token}

Response:
{
  "id": "proj_123",
  "name": "Audit Website 2024",
  "description": "Comprehensive security audit",
  "targets": ["example.com"],
  "status": "active",
  "created_at": "2024-08-17T10:30:00Z",
  "updated_at": "2024-08-17T15:45:00Z",
  "scans": [
    {
      "id": "scan_789",
      "type": "reconnaissance",
      "status": "completed",
      "started_at": "2024-08-17T11:00:00Z",
      "completed_at": "2024-08-17T11:15:00Z"
    }
  ]
}
```

#### Gestion des Scans

##### Démarrer un Scan
```http
POST /api/v1/scans
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "project_id": "proj_123",
  "scan_type": "network_reconnaissance",
  "targets": ["192.168.1.0/24"],
  "profile": "quick",
  "options": {
    "threads": 20,
    "timeout": 300,
    "stealth_mode": false
  }
}

Response:
{
  "scan_id": "scan_789",
  "status": "started",
  "estimated_duration": 900,
  "message": "Scan initiated successfully"
}
```

##### Statut du Scan
```http
GET /api/v1/scans/{scan_id}
Authorization: Bearer {jwt_token}

Response:
{
  "scan_id": "scan_789",
  "status": "running",
  "progress": 65,
  "current_phase": "port_scanning",
  "targets_completed": 150,
  "targets_total": 254,
  "started_at": "2024-08-17T11:00:00Z",
  "estimated_completion": "2024-08-17T11:15:00Z",
  "findings_count": 12
}
```

##### Arrêter un Scan
```http
POST /api/v1/scans/{scan_id}/stop
Authorization: Bearer {jwt_token}

Response:
{
  "scan_id": "scan_789",
  "status": "stopped",
  "message": "Scan stopped successfully"
}
```

##### Résultats du Scan
```http
GET /api/v1/scans/{scan_id}/results
Authorization: Bearer {jwt_token}

Query Parameters:
- format: json|xml|csv (default: json)
- filter: severity level (critical|high|medium|low)
- limit: number of results (default: 100)
- offset: pagination offset (default: 0)

Response:
{
  "scan_id": "scan_789",
  "status": "completed",
  "summary": {
    "hosts_discovered": 45,
    "services_identified": 123,
    "vulnerabilities_found": 8,
    "critical_findings": 2
  },
  "findings": [
    {
      "id": "finding_001",
      "type": "vulnerability",
      "severity": "high",
      "title": "SQL Injection in Login Form",
      "description": "SQLi vulnerability detected",
      "target": "example.com:443",
      "cve_id": "CVE-2024-1234",
      "cvss_score": 8.5,
      "evidence": {
        "url": "https://example.com/login",
        "parameter": "username",
        "payload": "admin' OR '1'='1"
      }
    }
  ]
}
```

#### Modules Spécialisés

##### Reconnaissance
```http
POST /api/v1/modules/reconnaissance/network-scan
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "target": "192.168.1.0/24",
  "scan_type": "comprehensive",
  "options": {
    "port_range": "1-65535",
    "service_detection": true,
    "os_detection": true,
    "script_scan": false
  }
}

Response:
{
  "task_id": "task_456",
  "status": "queued",
  "estimated_duration": 1800
}
```

##### Vulnérabilités Web
```http
POST /api/v1/modules/vulnerability/web-scan
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "target": "https://example.com",
  "scan_profile": "owasp_top10",
  "options": {
    "authentication": {
      "type": "form",
      "login_url": "https://example.com/login",
      "username": "testuser",
      "password": "testpass"
    },
    "scope": {
      "include_paths": ["/app", "/api"],
      "exclude_paths": ["/logout", "/admin"]
    }
  }
}

Response:
{
  "task_id": "task_789",
  "status": "started",
  "spider_urls_found": 0,
  "current_phase": "spidering"
}
```

#### Rapports

##### Génération de Rapport
```http
POST /api/v1/reports/generate
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "project_id": "proj_123",
  "report_type": "executive_summary",
  "format": "pdf",
  "options": {
    "include_charts": true,
    "include_raw_data": false,
    "branding": {
      "company_name": "My Security Company",
      "logo_url": "https://example.com/logo.png"
    }
  }
}

Response:
{
  "report_id": "report_456",
  "status": "generating",
  "estimated_completion": "2024-08-17T12:05:00Z"
}
```

##### Télécharger Rapport
```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer {jwt_token}

Response:
Content-Type: application/pdf
Content-Disposition: attachment; filename="pentest-report-2024-08-17.pdf"
[Binary PDF data]
```

### Codes d'Erreur HTTP

| Code | Nom | Description |
|------|-----|-------------|
| 400 | Bad Request | Paramètres invalides |
| 401 | Unauthorized | Token manquant/invalide |
| 403 | Forbidden | Permissions insuffisantes |
| 404 | Not Found | Ressource non trouvée |
| 409 | Conflict | Conflit avec ressource existante |
| 429 | Rate Limit | Trop de requêtes |
| 500 | Internal Error | Erreur serveur |

### Format des Erreurs
```json
{
  "error": {
    "code": "INVALID_TARGET",
    "message": "Target format is invalid",
    "details": "Expected IP address or CIDR notation",
    "timestamp": "2024-08-17T12:00:00Z"
  }
}
```

## 🐍 API Python

### Installation
```python
# Import des classes principales
from core.engine.orchestrator import PentestOrchestrator
from core.security.consent_manager import ConsentManager
from modules.reconnaissance.network_scanner import NetworkScanner
from modules.vulnerability.web_scanner import WebScanner
```

### Orchestrateur Principal

#### Classe PentestOrchestrator
```python
class PentestOrchestrator:
    """Orchestrateur principal pour workflows de pentest."""
    
    def __init__(self, target: str, config: Optional[Dict] = None):
        """
        Initialise l'orchestrateur.
        
        Args:
            target: Cible principale du pentest
            config: Configuration optionnelle
        """
```

##### Méthodes Principales
```python
# Initialisation
orchestrator = PentestOrchestrator(
    target="example.com",
    config={
        "stealth_mode": True,
        "max_threads": 20,
        "timeout": 300
    }
)

# Démarrage workflow complet
results = orchestrator.run_full_pentest(
    phases=["reconnaissance", "vulnerability", "exploitation"],
    options={
        "skip_confirmation": False,
        "generate_report": True
    }
)

# Exécution par phase
recon_results = orchestrator.run_reconnaissance_phase(
    target="192.168.1.0/24",
    scan_type="comprehensive"
)

vuln_results = orchestrator.run_vulnerability_phase(
    targets=recon_results["active_hosts"],
    scan_profiles=["web_owasp", "network_critical"]
)

# Gestion d'état
status = orchestrator.get_status()
orchestrator.pause_workflow()
orchestrator.resume_workflow()
orchestrator.stop_workflow()
```

### Modules Reconnaissance

#### NetworkScanner
```python
from modules.reconnaissance.network_scanner import NetworkScanner

# Initialisation
scanner = NetworkScanner(config={
    "nmap_path": "/usr/bin/nmap",
    "stealth_mode": False,
    "max_threads": 50
})

# Scan réseau basique
results = scanner.scan_network(
    target="192.168.1.0/24",
    scan_type="quick"
)

# Scan personnalisé
results = scanner.scan_network(
    target="10.0.0.0/16", 
    scan_type="custom",
    options={
        "ports": "22,80,443,8080",
        "service_detection": True,
        "os_detection": False,
        "script_categories": ["default", "safe"]
    }
)

# Scan de ports spécifiques
port_results = scanner.scan_ports(
    target="example.com",
    ports=[22, 80, 443, 8080, 8443],
    timeout=10
)

# Détection de services
service_results = scanner.detect_services(
    target="192.168.1.100",
    ports=port_results["open_ports"]
)
```

#### DomainEnumerator
```python
from modules.reconnaissance.domain_enum import DomainEnumerator

# Initialisation
enumerator = DomainEnumerator()

# Découverte sous-domaines
subdomains = enumerator.enumerate_subdomains(
    domain="example.com",
    methods=["passive", "active", "brute_force"],
    wordlist="data/wordlists/dns/subdomains.txt"
)

# Analyse DNS
dns_info = enumerator.analyze_dns(
    domain="example.com",
    record_types=["A", "AAAA", "MX", "TXT", "CNAME"]
)

# Vérification de prise de contrôle
takeover_check = enumerator.check_subdomain_takeover(
    subdomains=subdomains["active_subdomains"]
)
```

### Modules Vulnérabilités

#### WebScanner
```python
from modules.vulnerability.web_scanner import WebScanner

# Initialisation
web_scanner = WebScanner(config={
    "zap_api_key": "your_zap_key",
    "proxy_port": 8080,
    "user_agent": "LeZelote-Toolkit/1.0"
})

# Scan web compréhensif
results = web_scanner.scan_web_application(
    url="https://example.com",
    scan_profile="comprehensive",
    authentication={
        "type": "form",
        "login_url": "https://example.com/login",
        "username_field": "email",
        "password_field": "password",
        "username": "test@example.com",
        "password": "testpass123"
    }
)

# Scan OWASP Top 10
owasp_results = web_scanner.scan_owasp_top10(
    url="https://example.com",
    options={
        "sql_injection": True,
        "xss": True,
        "csrf": True,
        "file_inclusion": True
    }
)

# Test spécifique
sqli_results = web_scanner.test_sql_injection(
    url="https://example.com/search",
    parameters=["q", "category", "sort"],
    payloads="data/payloads/sql_injection.txt"
)
```

#### NetworkVulnerabilityScanner
```python
from modules.vulnerability.network_vuln import NetworkVulnerabilityScanner

# Initialisation
vuln_scanner = NetworkVulnerabilityScanner()

# Scan vulnérabilités réseau
results = vuln_scanner.scan_network_vulnerabilities(
    targets=["192.168.1.1", "192.168.1.100-110"],
    scan_profile="critical_only",
    options={
        "safe_checks": True,
        "skip_dos_tests": True,
        "max_hosts_parallel": 10
    }
)

# Scan SSL/TLS
ssl_results = vuln_scanner.scan_ssl_configuration(
    targets=["https://example.com:443"],
    checks=["weak_ciphers", "certificate_validation", "protocol_support"]
)
```

### Gestion de Sécurité

#### ConsentManager
```python
from core.security.consent_manager import ConsentManager

# Initialisation
consent_manager = ConsentManager()

# Ajouter autorisation
consent_id = consent_manager.add_consent({
    "target": "192.168.1.0/24",
    "scope": "network_scanning,web_testing",
    "authorized_by": "john.doe@company.com",
    "expiry_date": "2024-12-31T23:59:59Z",
    "notes": "Quarterly security audit"
})

# Vérifier autorisation
is_authorized = consent_manager.verify_consent("192.168.1.100")

# Lister autorisations
active_consents = consent_manager.list_consents(active_only=True)

# Révoquer autorisation
consent_manager.revoke_consent(consent_id)
```

### Utilitaires

#### LoggingHandler
```python
from core.utils.logging_handler import get_logger, setup_logging

# Configuration logging
setup_logging(
    log_level="INFO",
    log_file="logs/custom.log",
    console_output=True
)

# Obtenir logger
logger = get_logger(__name__)

# Utilisation
logger.info("Starting custom scan")
logger.warning("Potential security issue detected")
logger.error("Scan failed", extra={"target": "example.com", "error_code": "CONN_001"})
```

#### FileOperations
```python
from core.utils.file_ops import FileOperations

# Initialisation
file_ops = FileOperations()

# Opérations sécurisées
data = file_ops.read_secure(
    file_path="config/sensitive.yaml",
    encryption_key="your_encryption_key"
)

file_ops.write_secure(
    file_path="results/scan_data.json",
    data=scan_results,
    encryption=True,
    backup=True
)

# Compression
file_ops.compress_directory(
    source_dir="outputs/scan_20240817",
    output_file="archives/scan_20240817.tar.gz"
)
```

## 💻 CLI API

### Commandes Principales

#### Scan Commands
```bash
# Scan réseau rapide
python run_cli.py scan network --target 192.168.1.0/24 --profile quick

# Scan web compréhensif
python run_cli.py scan web --url https://example.com --profile comprehensive --auth-form

# Scan vulnérabilités spécifique
python run_cli.py scan vuln --target example.com --type ssl,web,network --output json
```

#### Project Commands
```bash
# Créer projet
python run_cli.py project create --name "Audit 2024" --target example.com

# Lister projets
python run_cli.py project list --status active

# Exporter projet
python run_cli.py project export --id proj_123 --format json --output /tmp/project.json
```

#### Report Commands
```bash
# Générer rapport PDF
python run_cli.py report generate --project proj_123 --format pdf --type executive

# Générer rapport technique
python run_cli.py report generate --scan scan_789 --format html --include-raw-data
```

#### Configuration Commands
```bash
# Ajouter autorisation
python run_cli.py consent add --target "192.168.1.0/24" --scope "full_audit" --expires "2024-12-31"

# Vérifier configuration
python run_cli.py config check --component all

# Mettre à jour outils
python run_cli.py tools update --tool nmap,zap --check-signatures
```

### Options Globales
```bash
# Toutes les commandes supportent :
--config CONFIG_FILE        # Fichier de configuration custom
--log-level LEVEL           # Niveau de logging (DEBUG, INFO, WARNING, ERROR)
--output-format FORMAT      # Format de sortie (json, yaml, table, csv)
--quiet                     # Mode silencieux
--verbose                   # Mode verbose
--dry-run                   # Simulation sans exécution
```

## 📡 WebSocket API

### Connexion WebSocket
```javascript
// Connexion WebSocket pour temps réel
const ws = new WebSocket('ws://localhost:8080/ws');

// Authentification
ws.onopen = function() {
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your_jwt_token'
    }));
};

// Gestion des messages
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleWebSocketMessage(data);
};
```

### Types de Messages

#### Notifications de Scan
```json
{
  "type": "scan_update",
  "scan_id": "scan_789",
  "status": "running",
  "progress": 45,
  "current_phase": "vulnerability_scanning",
  "new_findings": 3,
  "timestamp": "2024-08-17T12:30:00Z"
}
```

#### Nouvelles Découvertes
```json
{
  "type": "new_finding",
  "scan_id": "scan_789",
  "finding": {
    "id": "finding_123",
    "severity": "critical",
    "type": "vulnerability",
    "title": "Remote Code Execution",
    "target": "example.com:80",
    "timestamp": "2024-08-17T12:30:15Z"
  }
}
```

#### Alertes Système
```json
{
  "type": "system_alert",
  "alert_level": "warning",
  "message": "High CPU usage detected",
  "details": {
    "cpu_percent": 85.5,
    "active_scans": 3,
    "recommended_action": "Consider reducing concurrent scans"
  },
  "timestamp": "2024-08-17T12:30:30Z"
}
```

## 📊 SDK et Intégrations

### SDK Python Complet
```python
# Installation
pip install lezelote-toolkit-sdk

# Usage
from lezelote_sdk import LeZeloteClient

# Initialisation
client = LeZeloteClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

# Workflow complet
project = client.projects.create(
    name="Automated Pentest",
    targets=["example.com"]
)

scan = client.scans.start(
    project_id=project.id,
    scan_type="comprehensive",
    options={"stealth_mode": True}
)

# Attendre completion
client.scans.wait_for_completion(scan.id, timeout=3600)

# Générer rapport
report = client.reports.generate(
    project_id=project.id,
    format="pdf"
)

# Télécharger
report_data = client.reports.download(report.id)
```

### Intégration Jenkins
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Security Scan') {
            steps {
                script {
                    // Démarrer scan LeZelote
                    def scanResult = sh(
                        script: """
                            python -c "
                            from lezelote_sdk import LeZeloteClient
                            client = LeZeloteClient('http://pentest-server:8080', '${env.LEZELOTE_API_KEY}')
                            scan = client.scans.start_and_wait('${env.TARGET_URL}', 'web_owasp')
                            print(f'Critical: {scan.findings.critical_count}')
                            exit(1 if scan.findings.critical_count > 0 else 0)
                            "
                        """,
                        returnStatus: true
                    )
                    
                    if (scanResult != 0) {
                        currentBuild.result = 'FAILURE'
                        error('Critical security vulnerabilities found')
                    }
                }
            }
        }
    }
}
```

## 🔧 Configuration API

### Format de Configuration
```yaml
# API Configuration (config/api_config.yaml)
api:
  host: "0.0.0.0"
  port: 8080
  debug: false
  
  # Rate limiting
  rate_limit:
    requests_per_minute: 100
    burst_size: 20
    
  # Authentication
  auth:
    type: "jwt"
    secret_key: "your_secret_key"
    token_expiry: 3600
    
  # CORS
  cors:
    allow_origins: ["http://localhost:3000"]
    allow_methods: ["GET", "POST", "PUT", "DELETE"]
    allow_headers: ["Content-Type", "Authorization"]
    
  # WebSocket
  websocket:
    enabled: true
    path: "/ws"
    heartbeat_interval: 30
```

### Configuration par Environnement
```bash
# Variables d'environnement
export LEZELOTE_API_HOST="0.0.0.0"
export LEZELOTE_API_PORT="8080"
export LEZELOTE_API_KEY="your-api-key-here"
export LEZELOTE_DB_URL="sqlite:///data/lezelote.db"
export LEZELOTE_LOG_LEVEL="INFO"
```

## 🔒 Sécurité API

### Authentification JWT
```python
# Génération token
import jwt
from datetime import datetime, timedelta

def generate_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'iss': 'lezelote-toolkit'
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

# Validation token
def validate_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
```

### Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuration rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Application sur endpoints
@app.route('/api/v1/scans', methods=['POST'])
@limiter.limit("10 per minute")
def create_scan():
    # Logic here
    pass
```

## 📋 Exemples d'Utilisation

### Scan Automatisé Complet
```python
#!/usr/bin/env python3
"""
Script d'automatisation complète avec LeZelote Toolkit.
"""

from lezelote_sdk import LeZeloteClient
import time
import json

def automated_pentest(target_url):
    """Effectue un pentest automatisé complet."""
    
    # Initialisation
    client = LeZeloteClient("http://localhost:8080", "your_api_key")
    
    # 1. Créer projet
    project = client.projects.create(
        name=f"Automated Audit {time.strftime('%Y%m%d_%H%M%S')}",
        description=f"Automated security audit for {target_url}",
        targets=[target_url]
    )
    
    print(f"✅ Project created: {project.id}")
    
    # 2. Phase reconnaissance
    print("🔍 Starting reconnaissance...")
    recon_scan = client.scans.start(
        project_id=project.id,
        scan_type="reconnaissance",
        profile="comprehensive"
    )
    
    # Attendre completion
    recon_results = client.scans.wait_for_completion(recon_scan.id)
    print(f"✅ Reconnaissance completed: {len(recon_results.hosts)} hosts found")
    
    # 3. Phase vulnérabilités
    print("🛡️ Starting vulnerability assessment...")
    vuln_scan = client.scans.start(
        project_id=project.id,
        scan_type="vulnerability",
        profile="owasp_top10"
    )
    
    vuln_results = client.scans.wait_for_completion(vuln_scan.id)
    
    # 4. Analyse résultats
    critical_vulns = [f for f in vuln_results.findings if f.severity == "critical"]
    high_vulns = [f for f in vuln_results.findings if f.severity == "high"]
    
    print(f"🚨 Found {len(critical_vulns)} critical and {len(high_vulns)} high vulnerabilities")
    
    # 5. Génération rapport
    print("📊 Generating report...")
    report = client.reports.generate(
        project_id=project.id,
        format="pdf",
        type="executive"
    )
    
    # 6. Sauvegarde
    report_data = client.reports.download(report.id)
    filename = f"pentest_report_{target_url.replace('https://', '').replace('http://', '')}.pdf"
    
    with open(filename, 'wb') as f:
        f.write(report_data)
    
    print(f"✅ Report saved: {filename}")
    
    return {
        "project_id": project.id,
        "critical_vulnerabilities": len(critical_vulns),
        "high_vulnerabilities": len(high_vulns),
        "report_file": filename
    }

if __name__ == "__main__":
    result = automated_pentest("https://example.com")
    print(f"🎉 Pentest completed: {json.dumps(result, indent=2)}")
```

### Intégration CI/CD
```python
#!/usr/bin/env python3
"""
Intégration LeZelote dans pipeline CI/CD.
"""

import sys
import os
from lezelote_sdk import LeZeloteClient

def security_gate_check(target_url, max_critical=0, max_high=2):
    """
    Vérifie seuils de sécurité pour CI/CD.
    Échoue si vulnérabilités dépassent seuils.
    """
    
    client = LeZeloteClient(
        base_url=os.environ["LEZELOTE_URL"],
        api_key=os.environ["LEZELOTE_API_KEY"]
    )
    
    # Scan sécurisé rapide
    scan = client.scans.start_quick_security_check(target_url)
    results = client.scans.wait_for_completion(scan.id, timeout=1800)
    
    # Compter vulnérabilités par sévérité
    critical = len([f for f in results.findings if f.severity == "critical"])
    high = len([f for f in results.findings if f.severity == "high"])
    medium = len([f for f in results.findings if f.severity == "medium"])
    
    # Affichage résultats
    print(f"Security Check Results for {target_url}:")
    print(f"  Critical: {critical} (max allowed: {max_critical})")
    print(f"  High: {high} (max allowed: {max_high})")
    print(f"  Medium: {medium}")
    
    # Vérification seuils
    if critical > max_critical:
        print(f"❌ SECURITY GATE FAILED: {critical} critical vulnerabilities found (max: {max_critical})")
        return False
        
    if high > max_high:
        print(f"❌ SECURITY GATE FAILED: {high} high vulnerabilities found (max: {max_high})")
        return False
    
    print("✅ SECURITY GATE PASSED")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: security_gate_check.py <target_url>")
        sys.exit(1)
    
    target = sys.argv[1]
    passed = security_gate_check(target)
    
    sys.exit(0 if passed else 1)
```

---

**Cette documentation API couvre les principales interfaces du LeZelote Toolkit. Pour des exemples spécifiques ou des questions techniques, consultez les autres guides ou créez un issue GitHub.**