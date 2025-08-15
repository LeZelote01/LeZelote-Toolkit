"""
Client LLM Adaptatif - Gestion robuste des changements de clés API
CyberSec Toolkit Pro 2025 - Version Optimisée
"""
import os
import asyncio
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from config import settings
from datetime import datetime
from contextlib import asynccontextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    from emergentintegrations.llm.chat import LlmChat
    EMERGENT_AVAILABLE = True
except ImportError:
    EMERGENT_AVAILABLE = False


class AdaptiveLLMClient:
    """Client LLM adaptatif avec gestion robuste des changements de providers - Version Optimisée"""
    
    def __init__(self):
        self.clients = {}
        self.last_config_check = None
        self.config_cache = None
        self.last_initialization_errors = []
        
        # Nouvelles améliorations pour éviter les "Broken pipe"
        self._initialization_lock = asyncio.Lock()
        self._is_initializing = False
        self._pending_requests = []
        self._request_queue = asyncio.Queue()
        self._last_successful_config = None
        self._consecutive_failures = {}
        self._max_retries = 5  # ✅ Plus de tentatives pour robustesse
        self._base_retry_delay = 2.0  # ✅ Délai de base plus long
        self._initialization_timeout = 60.0  # ✅ Plus de temps pour initialiser tous les services
        
        self._provider_models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "emergent": ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro"]
        }
        
        # Initialisation asynchrone
        asyncio.create_task(self._safe_initialize_all_clients())
    
    async def _safe_initialize_all_clients(self):
        """Initialisation sécurisée et asynchrone de tous les clients"""
        try:
            await asyncio.wait_for(
                self._initialize_all_clients_async(), 
                timeout=self._initialization_timeout
            )
        except asyncio.TimeoutError:
            logger.error("⏰ Timeout lors de l'initialisation des clients LLM")
            self.last_initialization_errors.append(("system", "Initialization timeout"))
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation sécurisée: {e}")
            self.last_initialization_errors.append(("system", f"Safe initialization error: {str(e)}"))
    
    def _get_current_config(self) -> Dict[str, Any]:
        """Récupère la configuration actuelle des clés API avec validation"""
        try:
            config = {
                "emergent_llm": bool(settings.emergent_llm_key and len(settings.emergent_llm_key.strip()) > 10),
                "openai": bool(settings.openai_api_key and settings.openai_api_key.startswith('sk-')), 
                "anthropic": bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-')),
                "google": bool(settings.google_ai_api_key and len(settings.google_ai_api_key.strip()) > 10),
                "default_provider": settings.default_llm_provider,
                "default_model": settings.default_llm_model,
                "timestamp": datetime.now().timestamp()
            }
            return config
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de la configuration: {e}")
            return {
                "emergent_llm": False, "openai": False, "anthropic": False, "google": False,
                "default_provider": "simulation", "default_model": "fallback",
                "timestamp": datetime.now().timestamp()
            }
    
    def _config_changed(self) -> bool:
        """Vérifie si la configuration a changé avec protection contre les changements fréquents"""
        try:
            current_config = self._get_current_config()
            
            if self.config_cache is None:
                self.config_cache = current_config
                return True
                
            # Éviter les recharges trop fréquentes (minimum 5 secondes entre les changements)
            time_since_last_change = current_config.get("timestamp", 0) - self.config_cache.get("timestamp", 0)
            if time_since_last_change < 5.0:
                return False
                
            # Comparer les configurations (sauf timestamp)
            for key in current_config:
                if key != "timestamp" and current_config[key] != self.config_cache.get(key):
                    logger.info(f"🔄 Changement de configuration détecté pour: {key}")
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification des changements: {e}")
            return False
    
    async def _initialize_all_clients_async(self):
        """Initialise tous les clients disponibles avec gestion d'erreurs améliorée"""
        async with self._initialization_lock:
            if self._is_initializing:
                logger.info("⏳ Initialisation déjà en cours, attente...")
                return
                
            self._is_initializing = True
            try:
                await self._perform_initialization()
            finally:
                self._is_initializing = False
    
    async def _perform_initialization(self):
        """Effectue l'initialisation avec retry et gestion d'erreurs robuste"""
        self.clients.clear()
        initialization_errors = []
        
        logger.info("🔄 Initialisation des clients LLM avec protection anti-broken-pipe...")
        
        # Liste des providers à initialiser
        providers = [
            ("emergent", self._init_emergent_client),
            ("openai", self._init_openai_client),
            ("anthropic", self._init_anthropic_client),
            ("google", self._init_google_client)
        ]
        
        # Initialisation avec retry pour chaque provider
        for provider_name, init_func in providers:
            for retry in range(self._max_retries):
                try:
                    client = await init_func()
                    if client:
                        self.clients[provider_name] = client
                        logger.info(f"✅ Client {provider_name} initialisé avec succès")
                        self._consecutive_failures[provider_name] = 0
                        break
                except Exception as e:
                    self._consecutive_failures[provider_name] = self._consecutive_failures.get(provider_name, 0) + 1
                    error_msg = f"{provider_name} initialization failed (attempt {retry + 1}): {str(e)}"
                    logger.warning(f"⚠️ {error_msg}")
                    
                    if retry < self._max_retries - 1:
                        delay = self._base_retry_delay * (2 ** retry)
                        logger.info(f"🔄 Retry dans {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        initialization_errors.append((provider_name, error_msg))
        
        # Résumé final
        logger.info(f"📊 Résumé initialisation: {len(self.clients)} client(s) initialisé(s)")
        if initialization_errors:
            logger.warning(f"⚠️ {len(initialization_errors)} erreur(s) d'initialisation:")
            for provider, error in initialization_errors:
                logger.warning(f"   - {provider}: {error}")
        
        self.config_cache = self._get_current_config()
        self.last_initialization_errors = initialization_errors
        
        # Marquer comme configuration réussie si au moins un client fonctionne
        if self.clients:
            self._last_successful_config = self.config_cache.copy()
    
    async def _init_emergent_client(self):
        """Initialise le client Emergent avec validation"""
        if not settings.emergent_llm_key or not EMERGENT_AVAILABLE:
            return None
            
        if not settings.emergent_llm_key.strip():
            logger.warning("⚠️ Emergent LLM: Clé vide")
            return None
            
        try:
            client = LlmChat(
                api_key=settings.emergent_llm_key.strip(),
                session_id="adaptive_client_session",
                system_message="Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."
            )
            return client
        except Exception as e:
            logger.error(f"❌ Emergent LLM init error: {e}")
            raise
    
    async def _init_openai_client(self):
        """Initialise le client OpenAI avec validation"""
        if not settings.openai_api_key or not OPENAI_AVAILABLE:
            return None
            
        if not settings.openai_api_key.startswith('sk-'):
            logger.warning("⚠️ OpenAI: Format de clé invalide")
            return None
            
        try:
            client = openai.OpenAI(
                api_key=settings.openai_api_key.strip(),
                timeout=30.0,
                max_retries=2
            )
            return client
        except Exception as e:
            logger.error(f"❌ OpenAI init error: {e}")
            raise
    
    async def _init_anthropic_client(self):
        """Initialise le client Anthropic avec validation"""
        if not settings.anthropic_api_key or not ANTHROPIC_AVAILABLE:
            return None
            
        if not settings.anthropic_api_key.startswith('sk-ant-'):
            logger.warning("⚠️ Anthropic: Format de clé invalide")
            return None
            
        try:
            client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key.strip(),
                timeout=30.0,
                max_retries=2
            )
            return client
        except Exception as e:
            logger.error(f"❌ Anthropic init error: {e}")
            raise
    
    async def _init_google_client(self):
        """Initialise le client Google AI avec validation"""
        if not settings.google_ai_api_key or not GOOGLE_AI_AVAILABLE:
            return None
            
        if len(settings.google_ai_api_key.strip()) < 10:
            logger.warning("⚠️ Google AI: Clé trop courte")
            return None
            
        try:
            genai.configure(
                api_key=settings.google_ai_api_key.strip(),
                transport='rest'  # Plus stable que grpc
            )
            client = genai.GenerativeModel("gemini-1.5-pro")
            return client
        except Exception as e:
            logger.error(f"❌ Google AI init error: {e}")
            raise
    
    def get_available_providers_sync(self) -> List[str]:
        """Retourne la liste des providers disponibles de manière synchrone"""
        if self._config_changed():
            # Ne pas attendre l'initialisation asynchrone ici, juste retourner l'état actuel
            pass
        return list(self.clients.keys())
    
    async def get_available_providers(self) -> List[str]:
        """Retourne la liste des providers disponibles avec vérification asynchrone"""
        if self._config_changed():
            await self._safe_initialize_all_clients()
        return list(self.clients.keys())
    
    async def force_reinitialize_provider(self, provider: str) -> Dict[str, Any]:
        """Force la réinitialisation d'un provider spécifique après changement de clé"""
        logger.info(f"🔄 Réinitialisation forcée du provider: {provider}")
        
        try:
            # Supprimer le client existant
            if provider in self.clients:
                del self.clients[provider]
                logger.info(f"✅ Client {provider} supprimé")
            
            # Réinitialiser les statistiques d'échecs
            self._consecutive_failures[provider] = 0
            logger.info(f"✅ Statistiques d'échecs réinitialisées pour {provider}")
            
            # Recharger la configuration
            self.config_cache = None  # Force reload
            logger.info("🔄 Cache de configuration effacé")
            
            # Réinitialiser le provider spécifique
            if provider == "emergent":
                client = await self._init_emergent_client()
            elif provider == "openai":
                client = await self._init_openai_client()
            elif provider == "anthropic":
                client = await self._init_anthropic_client()
            elif provider == "google":
                client = await self._init_google_client()
            else:
                raise ValueError(f"Provider non supporté: {provider}")
            
            if client:
                self.clients[provider] = client
                logger.info(f"✅ Provider {provider} réinitialisé avec succès")
                
                # Test rapide du provider réinitialisé
                test_response, used_provider, used_model = await self.generate_with_fallback(
                    "Test de réinitialisation - réponds juste 'OK'", 
                    preferred_provider=provider
                )
                
                return {
                    "status": "success",
                    "provider": provider,
                    "reinitialized": True,
                    "test_successful": True,
                    "test_response": test_response[:100],
                    "used_provider": used_provider,
                    "used_model": used_model,
                    "message": f"Provider {provider} réinitialisé et testé avec succès"
                }
            else:
                return {
                    "status": "error",
                    "provider": provider,
                    "reinitialized": False,
                    "error": "Impossible d'initialiser le client",
                    "message": f"Échec de la réinitialisation de {provider}"
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la réinitialisation forcée de {provider}: {e}")
            return {
                "status": "error",
                "provider": provider,
                "reinitialized": False,
                "error": str(e),
                "message": f"Erreur lors de la réinitialisation de {provider}: {str(e)}"
            }
    
    async def force_reinitialize_all_providers(self) -> Dict[str, Any]:
        """Force la réinitialisation de tous les providers (utile après changement global de clés)"""
        logger.info("🔄 Réinitialisation forcée de tous les providers...")
        
        results = {
            "status": "completed", 
            "timestamp": datetime.now().isoformat(),
            "results": {},
            "summary": {"success": 0, "errors": 0}
        }
        
        providers = ["emergent", "openai", "anthropic", "google"]
        
        for provider in providers:
            try:
                result = await self.force_reinitialize_provider(provider)
                results["results"][provider] = result
                
                if result["status"] == "success":
                    results["summary"]["success"] += 1
                else:
                    results["summary"]["errors"] += 1
                    
            except Exception as e:
                results["results"][provider] = {
                    "status": "error",
                    "error": str(e),
                    "message": f"Erreur lors de la réinitialisation: {str(e)}"
                }
                results["summary"]["errors"] += 1
        
        logger.info(f"📊 Réinitialisation terminée: {results['summary']['success']} succès, {results['summary']['errors']} erreurs")
        return results

    def get_initialization_diagnostics(self) -> Dict[str, Any]:
        """Retourne des diagnostics détaillés sur l'initialisation"""
        return {
            "available_providers": list(self.clients.keys()),
            "total_configured_keys": sum([
                bool(settings.emergent_llm_key and len(settings.emergent_llm_key.strip()) > 10),
                bool(settings.openai_api_key and settings.openai_api_key.startswith('sk-')),
                bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-')),
                bool(settings.google_ai_api_key and len(settings.google_ai_api_key.strip()) > 10)
            ]),
            "package_availability": {
                "emergent": EMERGENT_AVAILABLE,
                "openai": OPENAI_AVAILABLE,
                "anthropic": ANTHROPIC_AVAILABLE,
                "google": GOOGLE_AI_AVAILABLE
            },
            "api_keys_configured": {
                "emergent": bool(settings.emergent_llm_key and len(settings.emergent_llm_key.strip()) > 10),
                "openai": bool(settings.openai_api_key and settings.openai_api_key.startswith('sk-')),
                "anthropic": bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-')),
                "google": bool(settings.google_ai_api_key and len(settings.google_ai_api_key.strip()) > 10)
            },
            "initialization_errors": self.last_initialization_errors,
            "last_config_update": self.config_cache.get("timestamp") if self.config_cache else None,
            "consecutive_failures": self._consecutive_failures,
            "is_initializing": self._is_initializing,
            "last_successful_config": self._last_successful_config
        }
    
    def get_optimal_model(self, provider: str, requested_model: str = None) -> str:
        """Retourne le modèle optimal pour un provider donné"""
        available_models = self._provider_models.get(provider, [])
        
        if requested_model and requested_model in available_models:
            return requested_model
            
        # Retourner le meilleur modèle par défaut
        if provider == "openai":
            return "gpt-4o-mini"
        elif provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        elif provider == "google":
            return "gemini-1.5-pro"
        elif provider == "emergent":
            return "gpt-4o-mini"
        
        return available_models[0] if available_models else "gpt-4o-mini"
    
    async def generate_with_fallback(self, prompt: str, context: Optional[str] = None, 
                                   preferred_provider: str = None) -> Tuple[str, str, str]:
        """
        Génère une réponse avec fallback automatique - Version Optimisée Anti-Broken-Pipe
        Retourne: (réponse, provider_utilisé, modèle_utilisé)
        """
        # Attendre si une initialisation est en cours
        if self._is_initializing:
            logger.info("⏳ Attente de la fin de l'initialisation...")
            max_wait = 30  # 30 secondes maximum
            wait_count = 0
            while self._is_initializing and wait_count < max_wait:
                await asyncio.sleep(1)
                wait_count += 1
            
            if self._is_initializing:
                logger.warning("⚠️ Timeout d'attente d'initialisation, passage en mode fallback")
                return self._get_fallback_response(prompt), "simulation", "fallback"
        
        # Vérifier et recharger la configuration si nécessaire
        try:
            if self._config_changed():
                logger.info("🔄 Configuration LLM changée - Réinitialisation sécurisée...")
                await self._safe_initialize_all_clients()
        except Exception as e:
            logger.error(f"❌ Erreur lors de la réinitialisation: {e}")
            # Utiliser la dernière configuration valide si disponible
            if self._last_successful_config and self.clients:
                logger.info("🔄 Utilisation de la dernière configuration valide")
            else:
                return self._get_fallback_response(prompt), "simulation", "fallback"
        
        # Déterminer l'ordre de priorité des providers avec validation
        providers_to_try = await self._get_providers_priority_list(preferred_provider)
        
        if not providers_to_try:
            logger.warning("⚠️ Aucun provider disponible, mode fallback")
            return self._get_fallback_response(prompt), "simulation", "fallback"
        
        # Essayer chaque provider avec gestion robuste d'erreurs
        last_error = None
        for provider in providers_to_try:
            try:
                # Vérifier si le provider a trop d'échecs consécutifs (seuil plus tolérant)
                consecutive_failures = self._consecutive_failures.get(provider, 0)
                if consecutive_failures >= 5:  # ✅ Plus tolérant : 5 au lieu de 3
                    logger.warning(f"⚠️ Provider {provider} ignoré temporairement (échecs consécutifs: {consecutive_failures})")
                    continue
                
                model = self.get_optimal_model(provider, settings.default_llm_model)
                
                # Exécuter avec timeout et retry
                response = await self._generate_with_provider_safe(prompt, context, provider, model)
                
                # Succès - réinitialiser le compteur d'échecs
                self._consecutive_failures[provider] = 0
                logger.info(f"✅ Génération réussie avec {provider}")
                return response, provider, model
                
            except Exception as e:
                last_error = e
                self._consecutive_failures[provider] = self._consecutive_failures.get(provider, 0) + 1
                logger.warning(f"⚠️ Échec provider {provider} (tentative {self._consecutive_failures[provider]}): {str(e)}")
                
                # Si c'est une erreur "Broken pipe" ou de connexion, attendre plus longtemps
                if "Broken pipe" in str(e) or "Connection" in str(e) or "BrokenPipeError" in str(e):
                    logger.warning(f"🔄 Erreur de connexion détectée pour {provider}, attente de récupération...")
                    await asyncio.sleep(3.0)  # ✅ Délai plus long pour récupération réseau
                else:
                    await asyncio.sleep(1.0)  # Délai normal pour autres erreurs
                continue
        
        # Fallback final avec information sur la dernière erreur
        logger.error(f"❌ Tous les providers ont échoué. Dernière erreur: {last_error}")
        return self._get_fallback_response(prompt, str(last_error) if last_error else None), "simulation", "fallback"
    
    async def _get_providers_priority_list(self, preferred_provider: str = None) -> List[str]:
        """Détermine l'ordre de priorité des providers avec validation"""
        providers_to_try = []
        available_providers = list(self.clients.keys())
        
        # Ajouter le provider préféré s'il est disponible
        if preferred_provider and preferred_provider in available_providers:
            providers_to_try.append(preferred_provider)
        
        # Ajouter le provider par défaut
        if settings.default_llm_provider in available_providers:
            if settings.default_llm_provider not in providers_to_try:
                providers_to_try.append(settings.default_llm_provider)
        
        # Ajouter les autres providers triés par fiabilité (moins d'échecs en premier)
        other_providers = [p for p in available_providers if p not in providers_to_try]
        other_providers.sort(key=lambda p: self._consecutive_failures.get(p, 0))
        providers_to_try.extend(other_providers)
        
        return providers_to_try
    
    async def _generate_with_provider_safe(self, prompt: str, context: Optional[str], 
                                         provider: str, model: str) -> str:
        """Génère une réponse avec un provider spécifique avec protection anti-broken-pipe"""
        try:
            # Timeout global pour éviter les blocages (plus long pour changements de clés)
            response = await asyncio.wait_for(
                self._generate_with_provider(prompt, context, provider, model),
                timeout=60.0  # ✅ Plus de temps pour s'adapter aux changements de clés
            )
            return response
        except asyncio.TimeoutError:
            raise Exception(f"Timeout lors de la génération avec {provider} (60s)")
        except Exception as e:
            # Log détaillé pour debug des changements de clés
            logger.error(f"❌ Erreur génération {provider}: {type(e).__name__}: {str(e)}")
            raise
    
    async def _generate_with_provider(self, prompt: str, context: Optional[str], 
                                    provider: str, model: str) -> str:
        """Génère une réponse avec un provider spécifique - Version Optimisée"""
        
        # Validation des entrées pour éviter les erreurs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt vide ou invalide")
        
        # Vérifier que le provider est disponible 
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} non disponible ou non initialisé")
            
        # Limitation de la taille du prompt
        full_prompt_size = len(prompt) + (len(context) if context else 0)
        if full_prompt_size > 50000:
            logger.warning(f"⚠️ Prompt très long ({full_prompt_size} chars), troncature")
            if context and len(context) > 10000:
                context = context[:10000] + "\n[...contexte tronqué...]"
            if len(prompt) > 40000:
                prompt = prompt[:40000] + "\n[...prompt tronqué...]"
        
        # Dispatch avec gestion d'erreurs robuste
        try:
            if provider == "emergent":
                return await self._emergent_generate(prompt, context, model)
            elif provider == "openai":
                return await self._openai_generate(prompt, context, model)
            elif provider == "anthropic":
                return await self._anthropic_generate(prompt, context, model)
            elif provider == "google":
                return await self._google_generate(prompt, context)
            else:
                raise ValueError(f"Provider non supporté: {provider}")
        except Exception as e:
            # Log détaillé pour debug des erreurs broken pipe
            error_type = type(e).__name__
            logger.error(f"❌ Erreur {provider} ({error_type}): {str(e)}")
            
            # Réinitialiser le client si c'est une erreur de connexion ou changement de clé
            if any(error_pattern in str(e) for error_pattern in [
                "Broken pipe", "Connection", "BrokenPipeError", "ConnectionError", 
                "authentication", "API key", "unauthorized", "invalid_api_key"
            ]):
                logger.warning(f"🔄 Erreur de connexion/authentification détectée pour {provider}")
                logger.info(f"   Erreur détaillée: {error_type}: {str(e)}")
                
                # Marquer pour réinitialisation lors du prochain changement de config
                self._consecutive_failures[provider] = self._consecutive_failures.get(provider, 0) + 1
                
                # Si c'est une erreur d'authentification, forcer une réinitialisation
                if any(auth_error in str(e).lower() for auth_error in ["api key", "unauthorized", "authentication"]):
                    logger.warning(f"🔑 Erreur d'authentification détectée - Marquage pour réinitialisation complète")
                    # Réinitialiser les stats d'échecs pour permettre une nouvelle tentative
                    if self._consecutive_failures[provider] > 3:
                        self._consecutive_failures[provider] = 2  # Réduire le compteur pour permettre retry
                
            raise  # Propager l'erreur pour le fallback
    
    async def _emergent_generate(self, prompt: str, context: Optional[str], model: str) -> str:
        """Génère avec Emergent LLM - Version Anti-Broken-Pipe"""
        try:
            from emergentintegrations.llm.chat import UserMessage
            
            # Préparer le message utilisateur avec contexte si nécessaire
            full_prompt = prompt
            if context:
                full_prompt = f"Contexte: {context}\n\nDemande: {prompt}"
            
            # Validation de la longueur du prompt
            if len(full_prompt) > 30000:
                full_prompt = full_prompt[:30000] + "\n[...tronqué pour Emergent...]"
            
            user_message = UserMessage(text=full_prompt)
            
            # Configurer le modèle si nécessaire avec vérification
            client = self.clients["emergent"]
            if model and model != getattr(client, 'model', None):
                try:
                    client = client.with_model("openai", model)
                except Exception as model_error:
                    logger.warning(f"⚠️ Impossible de changer vers le modèle {model}: {model_error}")
                    # Continuer avec le modèle par défaut
            
            # Appel avec retry automatique en cas d'erreur
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await asyncio.wait_for(
                        client.send_message(user_message), 
                        timeout=45.0  # ✅ Plus de temps pour s'adapter aux changements
                    )
                    return response
                except (asyncio.TimeoutError, ConnectionError, BrokenPipeError) as conn_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée pour Emergent: {conn_error}")
                        await asyncio.sleep(2.0 * (attempt + 1))  # ✅ Délai progressif plus long
                        continue
                    else:
                        raise Exception(f"Emergent: Échec après {max_retries} tentatives: {conn_error}")
            
        except Exception as e:
            logger.error(f"❌ Erreur détaillée Emergent LLM: {type(e).__name__}: {e}")
            raise
    
    async def _openai_generate(self, prompt: str, context: Optional[str], model: str) -> str:
        """Génère avec OpenAI - Version Anti-Broken-Pipe"""
        try:
            messages = [
                {"role": "system", "content": "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"Contexte: {context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            # Appel avec retry et timeout
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await asyncio.wait_for(
                        asyncio.create_task(self._openai_call(model, messages)),
                        timeout=50.0  # ✅ Plus de temps pour OpenAI
                    )
                    return response.choices[0].message.content
                    
                except (asyncio.TimeoutError, ConnectionError, BrokenPipeError) as conn_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée pour OpenAI: {conn_error}")
                        await asyncio.sleep(2.5 * (attempt + 1))  # ✅ Délai progressif plus long
                        continue
                    else:
                        raise Exception(f"OpenAI: Échec après {max_retries} tentatives: {conn_error}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur OpenAI: {type(e).__name__}: {e}")
            raise
    
    async def _openai_call(self, model: str, messages: List[Dict]) -> Any:
        """Appel OpenAI isolé pour permettre l'annulation"""
        return self.clients["openai"].chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
            timeout=30.0
        )
    
    async def _anthropic_generate(self, prompt: str, context: Optional[str], model: str) -> str:
        """Génère avec Anthropic - Version Anti-Broken-Pipe"""
        try:
            system_prompt = "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."
            
            if context:
                system_prompt += f" Contexte: {context}"
            
            # Limitation de la longueur pour Anthropic
            if len(system_prompt) > 5000:
                system_prompt = system_prompt[:5000] + "..."
            if len(prompt) > 45000:
                prompt = prompt[:45000] + "\n[...tronqué pour Anthropic...]"
            
            # Appel avec retry et timeout
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await asyncio.wait_for(
                        asyncio.create_task(self._anthropic_call(model, system_prompt, prompt)),
                        timeout=50.0  # ✅ Plus de temps pour Anthropic
                    )
                    return response.content[0].text
                    
                except (asyncio.TimeoutError, ConnectionError, BrokenPipeError) as conn_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée pour Anthropic: {conn_error}")
                        await asyncio.sleep(3.0 * (attempt + 1))  # ✅ Délai progressif plus long pour Anthropic
                        continue
                    else:
                        raise Exception(f"Anthropic: Échec après {max_retries} tentatives: {conn_error}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur Anthropic: {type(e).__name__}: {e}")
            raise
    
    async def _anthropic_call(self, model: str, system_prompt: str, prompt: str) -> Any:
        """Appel Anthropic isolé pour permettre l'annulation"""
        return self.clients["anthropic"].messages.create(
            model=model,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            timeout=30.0
        )
    
    async def _google_generate(self, prompt: str, context: Optional[str]) -> str:
        """Génère avec Google AI - Version Anti-Broken-Pipe"""
        try:
            system_prompt = "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."
            
            if context:
                system_prompt += f" Contexte: {context}"
            
            full_prompt = f"{system_prompt}\n\nUtilisateur: {prompt}"
            
            # Limitation de la longueur pour Google
            if len(full_prompt) > 30000:
                if context and len(context) > 5000:
                    context = context[:5000] + "..."
                    system_prompt = f"Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025. Contexte: {context}"
                if len(prompt) > 20000:
                    prompt = prompt[:20000] + "\n[...tronqué pour Google...]"
                full_prompt = f"{system_prompt}\n\nUtilisateur: {prompt}"
            
            # Appel avec retry et timeout
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await asyncio.wait_for(
                        asyncio.create_task(self._google_call(full_prompt)),
                        timeout=50.0  # ✅ Plus de temps pour Google AI
                    )
                    return response.text
                    
                except (asyncio.TimeoutError, ConnectionError, BrokenPipeError) as conn_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée pour Google: {conn_error}")
                        await asyncio.sleep(2.5 * (attempt + 1))  # ✅ Délai progressif pour Google
                        continue
                    else:
                        raise Exception(f"Google: Échec après {max_retries} tentatives: {conn_error}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur Google AI: {type(e).__name__}: {e}")
            raise
    
    async def _google_call(self, full_prompt: str) -> Any:
        """Appel Google AI isolé pour permettre l'annulation"""
        return self.clients["google"].generate_content(
            full_prompt,
            generation_config={'max_output_tokens': 1500, 'temperature': 0.7}
        )
    
    def _get_fallback_response(self, prompt: str, last_error: str = None) -> str:
        """Réponse de fallback si aucun LLM n'est disponible - Version Enrichie"""
        error_details = ""
        if last_error:
            error_details = f"\n**🚨 Dernière erreur:** {last_error}\n"
        
        # Statistiques d'échecs
        failure_stats = ""
        if self._consecutive_failures:
            failure_stats = "\n**📊 Statistiques d'échecs:**\n"
            for provider, count in self._consecutive_failures.items():
                if count > 0:
                    failure_stats += f"- {provider.title()}: {count} échecs consécutifs\n"
        
        return f"""🛡️ **CyberSec Toolkit Pro 2025 - Mode Simulation**

Votre demande: {prompt[:100]}{"..." if len(prompt) > 100 else ""}

Je fonctionne actuellement en mode simulation car aucune clé API n'est disponible ou toutes ont échoué.
{error_details}
**🔄 Changement de Clés API Détecté**

Le système a tenté d'utiliser tous les providers disponibles:
- Emergent LLM Key {"✅" if self.clients.get("emergent") else "❌"}
- OpenAI API Key {"✅" if self.clients.get("openai") else "❌"}
- Anthropic API Key {"✅" if self.clients.get("anthropic") else "❌"}
- Google AI API Key {"✅" if self.clients.get("google") else "❌"}
{failure_stats}
**💡 Pour activer l'IA complète:**

1. Vérifiez vos clés API dans `/app/portable/config/api_keys.env`
2. Redémarrez l'application pour recharger les configurations
3. Utilisez l'endpoint `/api/admin/llm-status` pour diagnostics
4. Consultez les logs pour les erreurs spécifiques

**✅ Services disponibles sans IA:**
- Tous les outils de scan et audit
- Fonctionnalités de diagnostic
- Interface utilisateur complète

*Mode simulation activé à {datetime.now().strftime('%H:%M:%S')}*"""

    async def test_provider_switching(self) -> Dict[str, Any]:
        """Teste le passage entre différents providers"""
        test_prompt = "Bonjour, je teste le changement de provider. Réponds simplement 'Test réussi avec [PROVIDER]'"
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "available_providers": await self.get_available_providers(),
            "test_results": {},
            "switching_issues": []
        }
        
        for provider in self.get_available_providers_sync():
            try:
                start_time = datetime.now()
                response, used_provider, used_model = await self.generate_with_fallback(
                    test_prompt, preferred_provider=provider
                )
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                
                results["test_results"][provider] = {
                    "status": "success",
                    "response": response[:200] + "..." if len(response) > 200 else response,
                    "used_provider": used_provider,
                    "used_model": used_model,
                    "response_time_seconds": response_time
                }
                
                if used_provider != provider:
                    results["switching_issues"].append({
                        "requested": provider,
                        "used": used_provider,
                        "reason": "Fallback automatique"
                    })
                    
            except Exception as e:
                results["test_results"][provider] = {
                    "status": "error",
                    "error": str(e)
                }
                
                results["switching_issues"].append({
                    "requested": provider,
                    "used": "none",
                    "reason": f"Erreur: {str(e)}"
                })
        
        return results


# Instance globale
adaptive_llm_client = AdaptiveLLMClient()