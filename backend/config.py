"""
Configuration pour CyberSec Toolkit Pro 2025
Support mode portable et serveur
"""
import os
import json
from pathlib import Path
from typing import List, Optional

class Settings:
    """Configuration application avec support portable"""
    
    def __init__(self):
        # Mode portable
        self.portable_mode = os.getenv("PORTABLE_MODE", "false").lower() == "true"
        self.portable_root = os.getenv("PORTABLE_ROOT", "/app")
        self.portable_data = os.getenv("PORTABLE_DATA", "/app/portable/database/data")
        
        # Configuration base de données
        self.database_type = os.getenv("DATABASE_TYPE", "mongodb")
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "cybersec_toolkit")
        
        # Configuration serveur - CORRIGÉ POUR COHÉRENCE PORTABLE
        self.backend_host = "0.0.0.0"
        self.backend_port = int(os.getenv("BACKEND_PORT", "8000"))  # CORRIGÉ: 8000 au lieu de 8001
        self.frontend_port = int(os.getenv("FRONTEND_PORT", "8002"))  # CORRIGÉ: 8002 au lieu de 3000
        
        # CORS - CORRIGÉ POUR COHÉRENCE PORTABLE
        cors_env = os.getenv("CORS_ORIGINS", "http://localhost:8002")  # CORRIGÉ: 8002 au lieu de 3000
        self.cors_origins = [origin.strip() for origin in cors_env.split(",")] if cors_env else ["http://localhost:8002"]
        
        # IA et LLM
        self.emergent_llm_key = os.getenv("EMERGENT_LLM_KEY", "")
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
        
        # Sécurité
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))
        
        # Cache
        self.cache_type = os.getenv("CACHE_TYPE", "redis")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Logs
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def get_database_url(self) -> str:
        """Retourne l'URL de base de données selon le mode"""
        if self.portable_mode and self.database_type == "sqlite":
            db_path = Path(self.portable_data) / "cybersec_toolkit.db"
            return f"sqlite:///{db_path}"
        return self.mongo_url
    
    def get_services_config(self) -> dict:
        """Charge la configuration des services"""
        if self.portable_mode:
            config_path = Path(self.portable_root) / "portable" / "config" / "services.json"
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        return json.load(f)
                except:
                    pass
        
        # Configuration par défaut
        return {
            "cybersecurity": {"enabled": True, "services": []},
            "ai_core": {"enabled": True, "services": []},
            "business": {"enabled": True, "services": []}
        }
    
    def is_service_enabled(self, category: str, service: str) -> bool:
        """Vérifie si un service est activé"""
        config = self.get_services_config()
        if category in config:
            services = config[category].get("services", [])
            if isinstance(services, list) and len(services) > 0:
                # Si services est une liste d'objets
                if isinstance(services[0], dict):
                    return any(s.get("name") == service for s in services)
                # Si services est une liste de strings
                return service in services
        return True  # Par défaut, activer tous les services

# Instance globale des paramètres
settings = Settings()

# Configuration spécifique portable
class PortableManager:
    """Gestionnaire spécifique pour le mode portable"""
    
    def __init__(self):
        self.settings = settings
        self.portable_dir = Path(settings.portable_root) / "portable"
    
    def setup_portable_environment(self):
        """Configure l'environnement pour le mode portable"""
        if not self.settings.portable_mode:
            return
            
        print("🔧 Configuration mode portable activée")
        
        # Créer les dossiers nécessaires
        (self.portable_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.portable_dir / "runtime").mkdir(parents=True, exist_ok=True)
        (self.portable_dir / "database" / "data").mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Mode portable configuré dans {self.portable_dir}")
    
    def get_runtime_info(self) -> dict:
        """Retourne les informations d'exécution portable"""
        return {
            "mode": "portable" if self.settings.portable_mode else "server",
            "database": self.settings.database_type,
            "backend_port": self.settings.backend_port,
            "frontend_port": self.settings.frontend_port,
            "root_path": self.settings.portable_root,
            "data_path": self.settings.portable_data
        }

# Instance globale du gestionnaire portable
portable_manager = PortableManager()