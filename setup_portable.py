#!/usr/bin/env python3
"""
Script de configuration portable pour CyberSec Toolkit Pro 2025
Prépare l'environnement pour le déploiement sur clé USB
"""
import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path

class PortableSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.portable_dir = self.root_dir / "portable"
        self.system = platform.system().lower()
        
    def create_structure(self):
        """Crée la structure portable complète"""
        print("🏗️ Création de la structure portable...")
        
        directories = [
            "portable/logs",
            "portable/runtime", 
            "portable/config",
            "portable/assets",
            "portable/executables",
            "portable/dependencies",
            "portable/database/data",
            "portable/database/backups"
        ]
        
        for directory in directories:
            (self.root_dir / directory).mkdir(parents=True, exist_ok=True)
            
        print("✅ Structure portable créée")
    
    def setup_database(self):
        """Configure la base de données portable"""
        print("📊 Configuration de la base de données portable...")
        
        # Créer la base SQLite vide
        db_path = self.portable_dir / "database" / "data" / "cybersec_toolkit.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialiser avec le script de migration
        import sys
        sys.path.append(str(self.portable_dir))
        
        try:
            from portable.database.migrations import setup_portable_database
            import asyncio
            asyncio.run(setup_portable_database())
        except ImportError:
            # Si pas encore créé, créer base simple
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT, collection TEXT, document TEXT)")
            conn.commit()
            conn.close()
        
        print(f"✅ Base de données SQLite créée : {db_path}")
    
    def create_portable_requirements(self):
        """Crée les requirements optimisés pour la portabilité"""
        print("📦 Optimisation des dépendances pour la portabilité...")
        
        portable_requirements = """# Core Framework - Portable
fastapi>=0.110.0
uvicorn[standard]>=0.25.0

# Base de données portable
aiosqlite>=0.19.0               # SQLite async (remplace motor)
sqlite3                         # SQLite standard library

# IA et LLM (conservés)
emergentintegrations            # Emergent LLM key
openai>=1.10.0                 # OpenAI API (optionnel)
anthropic>=0.18.0              # Anthropic API (optionnel)

# Génération de rapports (conservés)
reportlab>=4.0.0               # PDF generation
jinja2>=3.1.0                  # Templates

# Sécurité et authentification (conservés)
python-jose[cryptography]      # JWT tokens
passlib[bcrypt]               # Password hashing
python-multipart              # Form data

# HTTP et API (conservés)
httpx>=0.26.0                 # HTTP client
requests>=2.31.0              # HTTP requests
aiofiles>=23.2.1              # Async file operations

# Utilitaires (conservés)
python-dotenv>=1.0.0          # Environment variables
pydantic>=2.5.0               # Data validation
pydantic-settings>=2.1.0      # Settings management

# Portabilité spécifique
psutil>=5.9.0                 # System utilities
portalocker>=2.7.0           # File locking portable"""

        with open(self.root_dir / "backend" / "requirements_portable.txt", 'w') as f:
            f.write(portable_requirements)
            
        print("✅ Requirements portable créés")
    
    def create_launcher_scripts(self):
        """Crée les scripts de lancement pour tous les OS"""
        print("🚀 Création des scripts de lancement...")
        
        # Le script principal déjà créé via bulk_file_writer
        
        # Rendre les scripts exécutables sur Unix
        if self.system != "windows":
            scripts = [
                "START_TOOLKIT.sh",
                "portable/launcher/start_linux.sh",
                "portable/launcher/start_macos.sh"
            ]
            
            for script in scripts:
                script_path = self.root_dir / script
                if script_path.exists():
                    os.chmod(script_path, 0o755)
                    
        print("✅ Scripts de lancement créés")
    
    def create_config_files(self):
        """Crée les fichiers de configuration portable"""
        print("⚙️ Configuration portable...")
        
        # Configuration des services disponibles
        services_config = {
            "cybersecurity": {
                "enabled": True,
                "services": [
                    "audit", "pentest", "incident_response", "digital_forensics",
                    "vulnerability_management", "compliance", "monitoring",
                    "red_team", "blue_team", "cloud_security", "mobile_security",
                    "iot_security", "web3_security", "ai_security", "network_security",
                    "api_security", "container_security", "iac_security",
                    "social_engineering", "threat_intelligence", "security_orchestration",
                    "risk_assessment", "security_training"
                ]
            },
            "ai_core": {
                "enabled": True,
                "services": [
                    "assistant", "cyber_ai", "conversational_ai", "predictive_ai",
                    "business_ai", "automation_ai", "code_analysis_ai"
                ]
            },
            "business": {
                "enabled": True,
                "services": ["crm", "billing", "analytics", "planning", "training"]
            }
        }
        
        with open(self.portable_dir / "config" / "services.json", 'w') as f:
            json.dump(services_config, f, indent=2)
            
        # Configuration des ports par défaut
        ports_config = {
            "backend_start": 8000,
            "frontend_start": 3000,
            "database_start": 27000,
            "scan_range": 100
        }
        
        with open(self.portable_dir / "config" / "ports.json", 'w') as f:
            json.dump(ports_config, f, indent=2)
            
        print("✅ Configuration portable créée")
    
    def create_readme_portable(self):
        """Crée un README spécifique pour la version portable"""
        readme_content = """# 🛡️ CyberSec Toolkit Pro 2025 - PORTABLE USB

## 🚀 DÉMARRAGE RAPIDE

### Windows
Double-cliquez sur `START_TOOLKIT.bat`

### Linux/macOS  
Exécutez `./START_TOOLKIT.sh`

## 📋 PRÉREQUIS

### Windows
- Python 3.8+ (auto-détecté ou utilise la version portable)
- Navigateur web moderne

### Linux/macOS
- Python 3.8+ 
- Node.js 16+
- Yarn

## 🔧 FONCTIONNALITÉS PORTABLES

✅ **Base de données SQLite portable** (pas besoin de MongoDB)
✅ **Détection automatique de ports libres**
✅ **Configuration automatique selon l'OS**
✅ **Tous les 35 services cybersécurité conservés**
✅ **Interface web moderne identique**
✅ **Données entièrement portables sur clé USB**

## 🛠️ DÉPANNAGE

Si l'application ne démarre pas :
1. Vérifiez que Python est installé
2. Lancez `python setup_portable.py` 
3. Redémarrez avec le script approprié

## 📚 DOCUMENTATION COMPLÈTE

Consultez les fichiers de documentation pour l'architecture complète :
- `ARCHITECTURE.md` - Architecture technique
- `ROADMAP.md` - Plan de développement  
- `DEPLOYMENT.md` - Guide de déploiement
"""
        
        with open(self.root_dir / "README_PORTABLE.md", 'w') as f:
            f.write(readme_content)
            
        print("✅ README portable créé")
    
    def run_setup(self):
        """Exécute la configuration complète"""
        print("🎯 Configuration portable de CyberSec Toolkit Pro 2025")
        print("=" * 50)
        
        self.create_structure()
        self.setup_database()
        self.create_portable_requirements()
        self.create_launcher_scripts()
        self.create_config_files()
        self.create_readme_portable()
        
        print("")
        print("✅ CONFIGURATION PORTABLE TERMINÉE")
        print("🚀 Utilisez START_TOOLKIT.bat (Windows) ou START_TOOLKIT.sh (Linux/macOS)")
        print("📱 L'application sera portable sur n'importe quelle clé USB")

if __name__ == "__main__":
    setup = PortableSetup()
    setup.run_setup()