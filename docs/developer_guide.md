# Guide Développeur - LeZelote Toolkit

## 🏗️ Architecture du Projet

### Vue d'Ensemble
Le LeZelote Toolkit suit une architecture modulaire en couches permettant extensibilité et maintenabilité. Le système est conçu autour d'un orchestrateur central qui coordonne les modules fonctionnels.

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACES UTILISATEUR                    │
│  ┌─────────────────────┐    ┌─────────────────────────────┐  │
│  │    CLI Interface    │    │      Web Interface          │  │
│  │   (run_cli.py)     │    │   (interfaces/web/app.py)  │  │
│  └─────────────────────┘    └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      ORCHESTRATEUR CENTRAL                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           PentestOrchestrator                           │ │
│  │  - Gestion des workflows                                │ │
│  │  - Coordination des modules                             │ │
│  │  - Gestion des états                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    MODULES FONCTIONNELS                     │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │Reconnaissance│Vulnerability │ Exploitation │Post-Exploit│ │
│  │   Module     │   Module     │   Module     │   Module   │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      COUCHE CORE                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐│
│  │  Engine  │ Security │   API    │  Utils   │  Database    ││
│  │  - Orch. │ - Consent│ - Tools  │ - Logs   │ - SQLite     ││
│  │  - Tasks │ - Crypto │ - Cloud  │ - Files  │ - Models     ││
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘│
├─────────────────────────────────────────────────────────────┤
│                    OUTILS ET DONNÉES                        │
│  ┌─────────────────────┬─────────────────────────────────┐   │
│  │    Tools Layer      │       Data Layer                │   │
│  │  - Binaires natifs  │  - Wordlists                    │   │
│  │  - Containers       │  - Templates                    │   │
│  │  - Scripts Python   │  - Bases de données             │   │
│  └─────────────────────┴─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Structure des Dossiers
```
LeZelote-Toolkit/
├── core/                          # Couche centrale
│   ├── engine/                    # Moteur d'orchestration
│   │   ├── orchestrator.py        # Orchestrateur principal
│   │   ├── task_scheduler.py      # Planificateur de tâches
│   │   ├── parallel_executor.py   # Exécution parallèle
│   │   └── resource_manager.py    # Gestion des ressources
│   ├── security/                  # Modules de sécurité
│   │   ├── consent_manager.py     # Gestion des autorisations
│   │   ├── stealth_engine.py      # Moteur furtif
│   │   ├── evasion_tactics.py     # Tactiques d'évasion
│   │   └── crypto_handler.py      # Cryptographie
│   ├── api/                       # Interfaces outils externes
│   │   ├── nmap_api.py           # Interface Nmap
│   │   ├── metasploit_api.py     # Interface Metasploit
│   │   ├── zap_api.py            # Interface OWASP ZAP
│   │   └── [autres_apis].py
│   ├── utils/                     # Utilitaires communs
│   │   ├── logging_handler.py     # Gestion des logs
│   │   ├── error_handler.py       # Gestion d'erreurs
│   │   ├── file_ops.py           # Opérations fichiers
│   │   ├── network_utils.py       # Utilitaires réseau
│   │   └── data_parser.py         # Parsing de données
│   └── db/                        # Base de données
│       ├── sqlite_manager.py      # Gestionnaire SQLite
│       ├── models.py             # Modèles de données
│       └── knowledge_base.db      # Base de connaissances
│
├── modules/                       # Modules fonctionnels
│   ├── reconnaissance/            # Module de reconnaissance
│   ├── vulnerability/             # Module vulnérabilités
│   ├── exploitation/              # Module d'exploitation
│   ├── post_exploit/             # Module post-exploitation
│   └── reporting/                 # Module de reporting
│
├── interfaces/                    # Interfaces utilisateur
│   ├── cli/                      # Interface en ligne de commande
│   └── web/                      # Interface web
│
├── tools/                        # Outils intégrés
├── data/                         # Données et ressources
├── config/                       # Configuration
├── scripts/                      # Scripts utilitaires
├── logs/                         # Journaux
├── outputs/                      # Résultats bruts
├── reports/                      # Rapports générés
└── tests/                        # Suite de tests
```

## 🔧 Standards de Développement

### Convention de Nommage
```python
# Classes : PascalCase
class PentestOrchestrator:
    pass

# Fonctions et variables : snake_case  
def execute_scan_task():
    scan_results = []

# Constantes : UPPER_SNAKE_CASE
MAX_CONCURRENT_SCANS = 10

# Fichiers : snake_case.py
# network_scanner.py, vulnerability_manager.py
```

### Structure d'un Module
```python
"""
Module de reconnaissance réseau.

Ce module orchestre les outils de scanning réseau (Nmap, RustScan, Masscan)
pour découverte d'hôtes, énumération de ports et détection de services.
"""

import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError
from ...core.security.consent_manager import ConsentManager
from ...core.api.nmap_api import NmapAPI

logger = get_logger(__name__)

class NetworkScanner:
    """
    Scanner réseau unifié utilisant multiple outils.
    
    Attributes:
        nmap_api: Interface vers Nmap
        consent_manager: Gestionnaire d'autorisations
        config: Configuration du scanner
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialise le scanner réseau.
        
        Args:
            config: Configuration optionnelle du scanner
            
        Raises:
            PentestError: Si initialisation échoue
        """
        logger.info("Initializing NetworkScanner")
        
        self.config = config or {}
        self.nmap_api = NmapAPI()
        self.consent_manager = ConsentManager()
        
        self._validate_configuration()
        
    def scan_network(self, target: str, scan_type: str = "quick") -> Dict:
        """
        Effectue un scan réseau sur la cible spécifiée.
        
        Args:
            target: Cible à scanner (IP, CIDR, plage)
            scan_type: Type de scan (quick, full, stealth, custom)
            
        Returns:
            Dictionnaire contenant les résultats du scan
            
        Raises:
            PentestError: Si scan échoue ou cible non autorisée
        """
        logger.info(f"Starting network scan: {target} ({scan_type})")
        
        # Vérification autorisation
        if not self.consent_manager.verify_consent(target):
            raise PentestError(f"Target {target} not authorized for scanning")
        
        try:
            # Logique de scan...
            results = self._execute_scan(target, scan_type)
            logger.info(f"Scan completed: {len(results.get('hosts', []))} hosts found")
            return results
            
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            raise PentestError(f"Network scan failed: {str(e)}")
            
    def _execute_scan(self, target: str, scan_type: str) -> Dict:
        """Exécute le scan selon le type spécifié."""
        # Implémentation privée...
        pass
        
    def _validate_configuration(self):
        """Valide la configuration du scanner."""
        # Validation...
        pass
```

### Gestion d'Erreurs
```python
# core/utils/error_handler.py
class PentestError(Exception):
    """Exception de base pour le toolkit."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()

class ConsentError(PentestError):
    """Erreur liée aux autorisations."""
    pass

class ToolError(PentestError):
    """Erreur d'exécution d'outil."""
    pass

# Usage dans les modules
try:
    result = self.nmap_api.scan_host(target)
except Exception as e:
    raise ToolError(f"Nmap scan failed: {str(e)}", "NMAP_001")
```

### Logging
```python
# Obtenir un logger
from core.utils.logging_handler import get_logger
logger = get_logger(__name__)

# Niveaux de logging
logger.debug("Détail technique pour debugging")
logger.info("Information générale d'exécution")
logger.warning("Situation anormale mais non critique")
logger.error("Erreur nécessitant attention")
logger.critical("Erreur critique compromettant fonctionnalité")

# Logging structuré
logger.info(
    "Scan completed",
    extra={
        "target": target,
        "duration": scan_duration,
        "hosts_found": len(hosts),
        "scan_type": scan_type
    }
)
```

## 🔌 Développement de Nouveaux Modules

### Créer un Module Fonctionnel

#### 1. Structure de Base
```bash
# Créer la structure
mkdir -p modules/my_module
touch modules/my_module/__init__.py
touch modules/my_module/my_scanner.py
touch modules/my_module/my_analyzer.py
```

#### 2. Implémentation du Module
```python
# modules/my_module/my_scanner.py
from typing import Dict, List
from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError

logger = get_logger(__name__)

class MyScanner:
    """Scanner personnalisé pour cas d'usage spécifique."""
    
    def __init__(self):
        logger.info("Initializing MyScanner")
        
    def scan(self, target: str) -> Dict:
        """Effectue le scan personnalisé."""
        logger.info(f"Starting custom scan on {target}")
        
        try:
            # Logique de scan personnalisée
            results = self._perform_scan(target)
            return {
                "target": target,
                "status": "completed",
                "findings": results
            }
        except Exception as e:
            logger.error(f"Custom scan failed: {e}")
            raise PentestError(f"MyScanner failed: {str(e)}")
            
    def _perform_scan(self, target: str) -> List[Dict]:
        """Implémentation du scan."""
        # Votre logique ici
        return []
```

#### 3. Intégration avec l'Orchestrateur
```python
# core/engine/orchestrator.py (modification)
from modules.my_module.my_scanner import MyScanner

class PentestOrchestrator:
    def __init__(self, target: str):
        # ... autres initialisations
        self.my_scanner = MyScanner()
        
    def run_custom_module(self, target: str) -> Dict:
        """Exécute le module personnalisé."""
        return self.my_scanner.scan(target)
```

#### 4. Interface CLI
```python
# interfaces/cli/module_cli/my_module_cli.py
from typing import Dict
from ....modules.my_module.my_scanner import MyScanner
from ...utils import display_results, get_user_input

class MyModuleCLI:
    """Interface CLI pour le module personnalisé."""
    
    def __init__(self):
        self.scanner = MyScanner()
        
    def show_menu(self):
        """Affiche le menu du module."""
        print("\n=== My Custom Module ===")
        print("1. Run Custom Scan")
        print("2. View Configuration")
        print("0. Return to Main Menu")
        
    def handle_menu_choice(self, choice: str):
        """Gère les choix du menu."""
        if choice == "1":
            self._run_scan()
        elif choice == "2":
            self._show_config()
            
    def _run_scan(self):
        """Lance un scan via l'interface."""
        target = get_user_input("Enter target: ")
        
        try:
            results = self.scanner.scan(target)
            display_results(results)
        except Exception as e:
            print(f"Scan failed: {e}")
```

### Intégrer un Outil Externe

#### 1. Créer une Interface API
```python
# core/api/my_tool_api.py
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path

from ..utils.logging_handler import get_logger
from ..utils.error_handler import ToolError

logger = get_logger(__name__)

class MyToolAPI:
    """Interface Python pour MyTool externe."""
    
    def __init__(self, tool_path: Optional[str] = None):
        self.tool_path = tool_path or self._find_tool_path()
        self._verify_installation()
        
    def _find_tool_path(self) -> str:
        """Trouve le chemin vers l'outil."""
        # Recherche dans PATH système
        import shutil
        tool_path = shutil.which("mytool")
        if tool_path:
            return tool_path
            
        # Recherche dans binaires intégrés
        binary_paths = [
            "tools/binaries/linux/mytool",
            "tools/binaries/windows/mytool.exe", 
            "tools/binaries/macos/mytool"
        ]
        
        for path in binary_paths:
            if Path(path).exists():
                return str(Path(path).absolute())
                
        raise ToolError("MyTool not found in system PATH or integrated binaries")
        
    def _verify_installation(self):
        """Vérifie que l'outil fonctionne."""
        try:
            result = subprocess.run(
                [self.tool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                raise ToolError(f"MyTool verification failed: {result.stderr}")
                
            logger.info(f"MyTool verified: {result.stdout.strip()}")
            
        except subprocess.TimeoutExpired:
            raise ToolError("MyTool verification timeout")
        except Exception as e:
            raise ToolError(f"MyTool verification failed: {str(e)}")
            
    def scan_target(self, target: str, options: Optional[Dict] = None) -> Dict:
        """Exécute un scan avec MyTool."""
        logger.info(f"Running MyTool scan on {target}")
        
        # Construction de la commande
        cmd = [self.tool_path, "scan", target]
        
        # Ajout des options
        if options:
            if options.get("verbose"):
                cmd.append("-v")
            if options.get("output_format"):
                cmd.extend(["-f", options["output_format"]])
                
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise ToolError(f"MyTool failed: {result.stderr}")
                
            # Parser la sortie (supposons JSON)
            try:
                output_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                # Fallback vers parsing texte
                output_data = {"raw_output": result.stdout}
                
            logger.info("MyTool scan completed successfully")
            return output_data
            
        except subprocess.TimeoutExpired:
            raise ToolError("MyTool scan timeout")
        except Exception as e:
            raise ToolError(f"MyTool execution failed: {str(e)}")
```

#### 2. Configuration de l'Outil
```yaml
# config/tool_profiles.yaml
tools:
  mytool:
    name: "My Custom Tool"
    version: "1.0.0"
    path: "auto"  # ou chemin spécifique
    enabled: true
    timeout: 300
    options:
      default_format: "json"
      max_threads: 10
      verbose: false
    profiles:
      quick:
        timeout: 60
        options: ["-f", "brief"]
      detailed:
        timeout: 600
        options: ["-f", "detailed", "-v"]
```

## 🧪 Tests et Qualité

### Tests Unitaires
```python
# tests/unit/test_modules/test_my_module.py
import unittest
from unittest.mock import Mock, patch
import pytest

from modules.my_module.my_scanner import MyScanner
from core.utils.error_handler import PentestError

class TestMyScanner(unittest.TestCase):
    """Tests unitaires pour MyScanner."""
    
    def setUp(self):
        """Préparation avant chaque test."""
        self.scanner = MyScanner()
        
    def test_scanner_initialization(self):
        """Test initialisation du scanner."""
        self.assertIsInstance(self.scanner, MyScanner)
        
    def test_scan_valid_target(self):
        """Test scan avec cible valide."""
        target = "192.168.1.1"
        
        with patch.object(self.scanner, '_perform_scan') as mock_scan:
            mock_scan.return_value = [{"host": "192.168.1.1", "status": "up"}]
            
            result = self.scanner.scan(target)
            
            self.assertEqual(result["target"], target)
            self.assertEqual(result["status"], "completed")
            self.assertIn("findings", result)
            
    def test_scan_invalid_target(self):
        """Test scan avec cible invalide."""
        with patch.object(self.scanner, '_perform_scan') as mock_scan:
            mock_scan.side_effect = Exception("Invalid target")
            
            with self.assertRaises(PentestError):
                self.scanner.scan("invalid_target")
                
    @patch('modules.my_module.my_scanner.get_logger')
    def test_logging(self, mock_logger):
        """Test que les logs sont générés."""
        self.scanner.scan("192.168.1.1")
        mock_logger.return_value.info.assert_called()
```

### Tests d'Intégration
```python
# tests/integration/test_my_module_integration.py
import unittest
from pathlib import Path

from core.engine.orchestrator import PentestOrchestrator
from modules.my_module.my_scanner import MyScanner

class TestMyModuleIntegration(unittest.TestCase):
    """Tests d'intégration pour MyModule."""
    
    def setUp(self):
        """Préparation tests d'intégration."""
        self.test_config = {
            "target": "127.0.0.1",
            "test_mode": True
        }
        
    def test_module_orchestrator_integration(self):
        """Test intégration avec orchestrateur."""
        orchestrator = PentestOrchestrator("127.0.0.1")
        
        # Test que le module est accessible
        self.assertTrue(hasattr(orchestrator, 'my_scanner'))
        
        # Test exécution via orchestrateur
        result = orchestrator.run_custom_module("127.0.0.1")
        self.assertIsInstance(result, dict)
        
    def test_end_to_end_workflow(self):
        """Test workflow complet."""
        scanner = MyScanner()
        
        # Test scan simple
        result = scanner.scan("127.0.0.1")
        
        # Vérifier structure résultat
        self.assertIn("target", result)
        self.assertIn("status", result)
        self.assertIn("findings", result)
```

### Couverture de Tests
```bash
# Installation coverage
pip install pytest-cov

# Exécution avec couverture
pytest tests/ --cov=modules/my_module --cov-report=html

# Voir rapport
# firefox htmlcov/index.html
```

## 📊 Profilage et Optimisation

### Profilage Performance
```python
# Utiliser cProfile pour identifier goulots d'étranglement
import cProfile
import pstats

def profile_scan():
    """Profile un scan pour optimisations."""
    scanner = MyScanner()
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code à profiler
    scanner.scan("192.168.1.0/24")
    
    profiler.disable()
    
    # Analyse résultats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 fonctions

# Utiliser memory_profiler pour mémoire
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Fonction analysée pour consommation mémoire."""
    # Code à analyser
    pass
```

### Optimisations Communes
```python
# 1. Utiliser générateurs pour gros datasets
def process_large_results():
    """Traite résultats volumineux efficacement."""
    for result in scan_generator():  # Au lieu de charger tout en mémoire
        yield process_result(result)

# 2. Cache pour résultats fréquents
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_lookup(target):
    """Cache résultats de lookups coûteux."""
    return perform_expensive_operation(target)

# 3. Pool de connexions
import threading
from queue import Queue

class ConnectionPool:
    """Pool de connexions réutilisables."""
    
    def __init__(self, max_connections=10):
        self.pool = Queue()
        for _ in range(max_connections):
            self.pool.put(self.create_connection())
            
    def get_connection(self):
        return self.pool.get()
        
    def return_connection(self, conn):
        self.pool.put(conn)
```

## 🔧 Configuration et Personnalisation

### Système de Configuration
```python
# core/config/config_manager.py
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Gestionnaire centralisé de configuration."""
    
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self._config_cache = {}
        
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Récupère configuration par nom."""
        if config_name not in self._config_cache:
            config_path = self.config_dir / f"{config_name}.yaml"
            
            if not config_path.exists():
                raise FileNotFoundError(f"Config file {config_path} not found")
                
            with open(config_path, 'r') as f:
                self._config_cache[config_name] = yaml.safe_load(f)
                
        return self._config_cache[config_name]
        
    def update_config(self, config_name: str, updates: Dict[str, Any]):
        """Met à jour configuration."""
        config = self.get_config(config_name)
        config.update(updates)
        
        config_path = self.config_dir / f"{config_name}.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        # Invalider cache
        self._config_cache.pop(config_name, None)
```

### Configuration Personnalisée
```yaml
# config/my_module.yaml
my_module:
  enabled: true
  scan_profiles:
    quick:
      timeout: 60
      threads: 5
      depth: 1
    thorough:
      timeout: 300
      threads: 20
      depth: 3
  
  tool_settings:
    mytool:
      path: "/opt/mytool/bin/mytool"
      options:
        - "--format=json"
        - "--timeout=30"
        
  output:
    format: "json"
    compression: true
    encryption: false
```

## 🔒 Sécurité et Autorisations

### Gestion des Autorisations
```python
# Extension du ConsentManager pour module personnalisé
from core.security.consent_manager import ConsentManager
from datetime import datetime, timedelta

class MyModuleConsentManager(ConsentManager):
    """Gestionnaire autorisations spécialisé."""
    
    def verify_custom_consent(self, target: str, operation: str) -> bool:
        """Vérifie autorisation pour opération spécifique."""
        base_consent = self.verify_consent(target)
        if not base_consent:
            return False
            
        # Vérifications additionnelles pour le module
        consent_details = self.get_consent_details(target)
        
        # Vérifier scope d'opération
        allowed_operations = consent_details.get("allowed_operations", [])
        if operation not in allowed_operations:
            self.logger.warning(f"Operation {operation} not authorized for {target}")
            return False
            
        return True
        
    def request_temporary_consent(self, target: str, duration_hours: int = 24):
        """Demande autorisation temporaire."""
        expiry = datetime.utcnow() + timedelta(hours=duration_hours)
        
        consent_data = {
            "target": target,
            "scope": "temporary_testing",
            "authorized_by": "auto_system",
            "expiry_date": expiry.isoformat(),
            "temporary": True
        }
        
        return self.add_consent(consent_data)
```

### Audit et Traçabilité
```python
# Extension du logging pour audit
class AuditLogger:
    """Logger spécialisé pour audit de sécurité."""
    
    def __init__(self):
        self.audit_logger = get_logger("audit")
        
    def log_security_event(self, event_type: str, details: Dict):
        """Enregistre événement de sécurité."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user": self._get_current_user(),
            "details": details,
            "severity": self._calculate_severity(event_type)
        }
        
        self.audit_logger.info(
            f"SECURITY_EVENT: {event_type}",
            extra=audit_entry
        )
        
    def _get_current_user(self) -> str:
        """Identifie utilisateur actuel."""
        import getpass
        return getpass.getuser()
        
    def _calculate_severity(self, event_type: str) -> str:
        """Calcule sévérité de l'événement."""
        high_severity = ["unauthorized_access", "consent_violation"]
        medium_severity = ["failed_authentication", "tool_execution"]
        
        if event_type in high_severity:
            return "HIGH"
        elif event_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
```

## 📚 Documentation et Standards

### Documentation du Code
```python
"""
Module de scanning personnalisé pour infrastructure IoT.

Ce module étend les capacités de reconnaissance standard pour cibler
spécifiquement les dispositifs IoT et systèmes embarqués.

Examples:
    Basic usage:
        >>> scanner = IoTScanner()
        >>> results = scanner.scan_iot_network("192.168.1.0/24")
        
    Advanced usage:
        >>> scanner = IoTScanner(config={"deep_scan": True})
        >>> results = scanner.scan_iot_network(
        ...     target="10.0.0.0/16",
        ...     protocols=["mqtt", "coap", "zigbee"]
        ... )

Todo:
    * Ajouter support protocole LoRaWAN
    * Implémenter détection firmware vulnérable
    * Optimiser scan pour réseaux de grande taille
"""

class IoTScanner:
    """
    Scanner spécialisé pour dispositifs IoT.
    
    Ce scanner utilise des techniques spécialisées pour identifier
    et analyser les dispositifs IoT dans un réseau.
    
    Attributes:
        protocols (List[str]): Protocoles IoT supportés
        config (Dict): Configuration du scanner
        
    Note:
        Nécessite autorisations spécifiques pour scan IoT
        car peut perturber dispositifs critiques.
    """
    
    def scan_iot_network(self, target: str, protocols: List[str] = None) -> Dict:
        """
        Scanne réseau pour dispositifs IoT.
        
        Effectue une reconnaissance spécialisée pour identifier
        dispositifs IoT utilisant protocoles standards et propriétaires.
        
        Args:
            target (str): Réseau cible au format CIDR
            protocols (List[str], optional): Protocoles à scanner.
                Defaults to ["mqtt", "coap", "modbus"].
                
        Returns:
            Dict: Résultats structurés du scan IoT
                {
                    "devices_found": int,
                    "protocols_detected": List[str],
                    "devices": List[Dict],
                    "vulnerabilities": List[Dict]
                }
                
        Raises:
            ConsentError: Si cible non autorisée pour scan IoT
            ToolError: Si échec d'exécution des outils IoT
            
        Example:
            >>> scanner = IoTScanner()
            >>> results = scanner.scan_iot_network("192.168.1.0/24")
            >>> print(f"Found {results['devices_found']} IoT devices")
        """
```

### README pour Module
```markdown
# My Custom Module

## Description
Module personnalisé pour [description spécifique].

## Installation
```bash
# Dépendances supplémentaires
pip install custom-dependency>=1.0.0

# Configuration
cp config/my_module.yaml.example config/my_module.yaml
```

## Configuration
```yaml
# config/my_module.yaml
my_module:
  enabled: true
  api_key: "your_api_key_here"
  scan_profiles:
    quick:
      timeout: 60
```

## Usage
```python
from modules.my_module import MyScanner

scanner = MyScanner()
results = scanner.scan("target.com")
```

## Testing
```bash
pytest tests/unit/test_modules/test_my_module.py -v
```

## Contributing
Voir [CONTRIBUTING.md](../CONTRIBUTING.md) pour guidelines.
```

## 🚀 Déploiement et Distribution

### Packaging
```python
# setup.py pour module standalone
from setuptools import setup, find_packages

setup(
    name="lezelote-my-module",
    version="1.0.0",
    author="Your Name",
    description="Custom module for LeZelote Toolkit",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=6.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
```

### Docker pour Module
```dockerfile
# Dockerfile.my-module
FROM python:3.11-slim

# Installation dépendances système
RUN apt-get update && apt-get install -y \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Installation module
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY modules/my_module/ /app/modules/my_module/
WORKDIR /app

CMD ["python", "-m", "modules.my_module"]
```

### CI/CD Pipeline
```yaml
# .github/workflows/my-module.yml
name: My Module CI/CD

on:
  push:
    paths:
      - 'modules/my_module/**'
  pull_request:
    paths:
      - 'modules/my_module/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        pytest tests/unit/test_modules/test_my_module.py -v --cov=modules/my_module
        
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 🔍 Débogage et Troubleshooting

### Outils de Debug
```python
# Debugging avec pdb
import pdb

def problematic_function():
    # Insérer breakpoint
    pdb.set_trace()
    
    # Code à déboguer
    result = complex_operation()
    return result

# Logging de debug détaillé
logger.setLevel(logging.DEBUG)
logger.debug("Variable state: %s", repr(complex_variable))

# Assert pour vérifications
assert isinstance(result, dict), f"Expected dict, got {type(result)}"
```

### Monitoring Runtime
```python
# Monitoring performance en temps réel
import time
from functools import wraps

def monitor_performance(func):
    """Décorateur pour monitoring performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed",
                extra={
                    "duration": duration,
                    "success": success,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
            )
    return wrapper

@monitor_performance
def my_scan_function(target):
    # Fonction monitorée
    return perform_scan(target)
```

## 📞 Support et Contribution

### Contribuer au Projet
1. Fork du repository
2. Créer branche feature (`git checkout -b feature/ma-fonctionnalite`)
3. Commit des modifications (`git commit -am 'Add nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Créer Pull Request

### Guidelines de Contribution
- Suivre standards de code (PEP 8)
- Ajouter tests pour nouvelles fonctionnalités
- Maintenir couverture de tests >80%
- Documenter APIs publiques
- Mettre à jour CHANGELOG.md

### Ressources Développeur
- **Issues** : https://github.com/LeZelote01/LeZelote-Toolkit/issues
- **Discussions** : https://github.com/LeZelote01/LeZelote-Toolkit/discussions
- **Wiki** : https://github.com/LeZelote01/LeZelote-Toolkit/wiki
- **API Docs** : `docs/api_reference.md`

---

**Ce guide vous donne les bases pour développer et étendre le LeZelote Toolkit. Pour questions spécifiques, consultez la documentation API ou créez un issue GitHub.**