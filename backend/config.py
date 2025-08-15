"""
Configuration pour CyberSec Toolkit Pro 2025
Support mode portable et serveur
"""
import os
import json
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

class Settings:
    """Configuration application avec support portable"""
    
    def __init__(self):
        # Charger le fichier des clés API en priorité
        self._load_api_keys()
        
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
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.google_ai_api_key = os.getenv("GOOGLE_AI_API_KEY", "")
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
        
        # Autres API keys
        self.stripe_api_key = os.getenv("STRIPE_API_KEY", "")
        
        # Sécurité
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))
        
        # Cache
        self.cache_type = os.getenv("CACHE_TYPE", "redis")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Logs
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def _load_api_keys(self):
        """Charge les clés API depuis le fichier de configuration"""
        api_keys_file = Path("/app/portable/config/api_keys.env")
        if api_keys_file.exists():
            load_dotenv(api_keys_file, override=True)
            # Recharger les valeurs dans l'instance
            self.emergent_llm_key = os.getenv("EMERGENT_LLM_KEY", "")
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "") 
            self.google_ai_api_key = os.getenv("GOOGLE_AI_API_KEY", "")
            self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
            self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
            print(f"✅ Clés API rechargées depuis {api_keys_file}")
        else:
            print(f"⚠️ Fichier de clés API non trouvé: {api_keys_file}")
    
    def reload_api_keys(self):
        """Méthode publique pour recharger les clés API"""
        self._load_api_keys()
    
    def get_configured_llm_providers(self) -> List[str]:
        """Retourne la liste des providers LLM configurés"""
        providers = []
        if self.emergent_llm_key:
            providers.append("emergent")
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_ai_api_key:
            providers.append("google")
        return providers
    
    def get_llm_status(self) -> dict:
        """Retourne le statut des configurations LLM"""
        return {
            "emergent_llm": bool(self.emergent_llm_key),
            "openai": bool(self.openai_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "google_ai": bool(self.google_ai_api_key),
            "default_provider": self.default_llm_provider,
            "default_model": self.default_llm_model,
            "configured_providers": self.get_configured_llm_providers()
        }
    
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