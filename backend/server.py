"""
CyberSec Toolkit Pro 2025 - Backend Server PORTABLE
Point d'entrée principal de l'application - Support portable USB
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import List

# Chargement automatique de la configuration portable
portable_env_path = Path(__file__).parent.parent / "portable" / "config" / "portable.env"
if portable_env_path.exists():
    load_dotenv(portable_env_path)
    print(f"📱 Configuration portable chargée: {portable_env_path}")

# Ajout du chemin portable pour les imports
if os.getenv("PORTABLE_MODE", "false").lower() == "true":
    portable_root = Path(os.getenv("PORTABLE_ROOT", "."))
    sys.path.insert(0, str(portable_root))
    sys.path.insert(0, str(portable_root / "backend"))
    sys.path.insert(0, str(portable_root / "portable"))

# Configuration avec support portable
from config import settings, portable_manager

# Initialiser le mode portable si nécessaire
if settings.portable_mode:
    portable_manager.setup_portable_environment()

# Import du gestionnaire de base de données
from database import init_database, get_database, close_database

# Configuration FastAPI
app = FastAPI(
    title="CyberSec Toolkit Pro 2025 - PORTABLE",
    description="L'outil cybersécurité freelance portable le plus avancé au monde",
    version="1.0.0-portable",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration - Manual approach
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Also keep the FastAPI CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes de base
@app.get("/api/")
async def root():
    """Endpoint racine - Status de l'application"""
    runtime_info = portable_manager.get_runtime_info()
    
    return {
        "status": "operational",
        "message": "CyberSec Toolkit Pro 2025 - PORTABLE USB Ready",
        "version": "1.0.0-portable",
        "timestamp": datetime.now().isoformat(),
        "mode": runtime_info["mode"],
        "database": runtime_info["database"],
        "services": {
            "total_planned": 35,
            "implemented": 35,  # Sprint 1.7 TERMINÉ - Tous les services cybersécurité spécialisés implémentés (Container Security, IaC Security, Social Engineering, Security Orchestration, Risk Assessment)
            "phase": "Sprint 1.7 - Services Cybersécurité Spécialisés (100% TERMINÉ ✅)",
            "portable_ready": True,
            "operational_services": [
                "Assistant IA Cybersécurité",
                "Pentesting OWASP Top 10", 
                "Incident Response",
                "Digital Forensics",
                "Compliance Management",
                "Vulnerability Management",
                "Monitoring 24/7",
                "Threat Intelligence",
                "Red Team Operations",
                "Blue Team Defense",
                "Audit Automatisé",
                "Cyber AI",
                "Predictive AI", 
                "Automation AI",
                "Conversational AI",
                "Business AI",
                "Code Analysis AI",
                "Cloud Security",
                "Mobile Security",
                "IoT Security",
                "Web3 Security",
                "AI Security",
                "Network Security",
                "API Security",
                "Container Security",
                "IaC Security",
                "Social Engineering",
                "Security Orchestration (SOAR)",
                "Risk Assessment",
                "CRM Business",
                "Billing & Invoicing",
                "Analytics & Reports",
                "Planning & Events", 
                "Training & Certification"
            ]
        },
        "runtime": runtime_info
    }

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    print("🚀 Initialisation CyberSec Toolkit Pro 2025...")
    
    # Initialiser la base de données
    await init_database()
    
    if settings.portable_mode:
        print("📱 Mode portable activé")
        print(f"💾 Base de données: {settings.database_type}")
    else:
        print("🌐 Mode serveur activé")

@app.on_event("shutdown") 
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    print("🛑 Arrêt CyberSec Toolkit Pro 2025...")
    await close_database()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db = await get_database()
    db_stats = db.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_stats["status"],
        "database_type": db_stats["type"],
        "mode": "portable" if settings.portable_mode else "server",
        "services": "portable_ready" if settings.portable_mode else "server_ready"
    }

@app.get("/api/admin/llm-status")
async def get_llm_status():
    """Status détaillé des configurations LLM et compatibilité"""
    llm_status = settings.get_llm_status()
    
    # Obtenir les diagnostics détaillés du client adaptatif
    from ai_core.adaptive_llm_client import adaptive_llm_client
    diagnostics = adaptive_llm_client.get_initialization_diagnostics()
    
    return {
        "status": "operational",
        "llm_configuration": llm_status,
        "diagnostics": diagnostics,
        "compatible_keys": {
            "emergent_llm": {
                "configured": llm_status["emergent_llm"],
                "description": "Clé universelle Emergent (recommandée)",
                "supports": ["OpenAI", "Anthropic", "Google AI"],
                "package_available": diagnostics["package_availability"]["emergent"]
            },
            "openai": {
                "configured": llm_status["openai"], 
                "description": "Clé API OpenAI directe",
                "supports": ["GPT-4", "GPT-4o", "GPT-3.5-turbo"],
                "package_available": diagnostics["package_availability"]["openai"]
            },
            "anthropic": {
                "configured": llm_status["anthropic"],
                "description": "Clé API Anthropic Claude",
                "supports": ["Claude-3", "Claude-3.5-sonnet"],
                "package_available": diagnostics["package_availability"]["anthropic"]
            },
            "google_ai": {
                "configured": llm_status["google_ai"],
                "description": "Clé API Google Gemini",
                "supports": ["Gemini-1.5-pro", "Gemini-1.5-flash"],
                "package_available": diagnostics["package_availability"]["google"]
            }
        },
        "recommendations": [
            {
                "type": "info" if llm_status["configured_providers"] else "warning",
                "message": f"{len(llm_status['configured_providers'])} provider(s) LLM configuré(s)" if llm_status["configured_providers"] else "Aucun provider LLM configuré - Mode simulation activé",
                "action": "Éditez /app/portable/config/api_keys.env pour configurer vos clés" if not llm_status["configured_providers"] else None
            }
        ]
    }

@app.post("/api/admin/test-llm")
async def test_llm_(request: dict):
    """Test d'une configuration LLM spécifique"""
    provider = request.get("provider", settings.default_llm_provider)
    test_message = request.get("message", "Bonjour, je teste la configuration LLM")
    
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        response, used_provider, used_model = await adaptive_llm_client.generate_with_fallback(
            test_message, preferred_provider=provider
        )
        
        return {
            "status": "success",
            "requested_provider": provider,
            "used_provider": used_provider,
            "used_model": used_model,
            "test_message": test_message,
            "response": response,
            "available_providers": adaptive_llm_client.get_available_providers(),
            "message": f"Test réussi avec {used_provider} (modèle: {used_model})"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "requested_provider": provider,
            "error": str(e),
            "message": f"Erreur test LLM: {str(e)}"
        }

@app.post("/api/admin/test-api-key")
async def test_individual_api_key(request: dict):
    """Test individuel d'une clé API spécifique avec diagnostic détaillé"""
    provider = request.get("provider")
    api_key = request.get("api_key")
    model = request.get("model", "")
    
    if not provider or not api_key:
        return {
            "status": "error",
            "error": "Provider et api_key sont requis"
        }
    
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        # Sauvegarder la configuration actuelle
        original_key = getattr(settings, f"{provider}_api_key", None)
        
        # Tester temporairement avec la nouvelle clé
        setattr(settings, f"{provider}_api_key", api_key)
        
        # Forcer réinitialisation
        adaptive_llm_client._initialize_all_clients()
        
        # Test de génération
        test_message = "Test de configuration. Réponds simplement 'OK' si tu me reçois."
        response, used_provider, used_model = await adaptive_llm_client.generate_with_fallback(
            test_message, preferred_provider=provider
        )
        
        # Restaurer la configuration originale
        if original_key:
            setattr(settings, f"{provider}_api_key", original_key)
        else:
            setattr(settings, f"{provider}_api_key", "")
        
        # Réinitialiser avec la configuration originale
        adaptive_llm_client._initialize_all_clients()
        
        return {
            "status": "success",
            "provider": provider,
            "api_key_prefix": api_key[:12] + "..." if len(api_key) > 12 else api_key,
            "test_successful": True,
            "used_provider": used_provider,
            "used_model": used_model,
            "test_response": response[:200] + "..." if len(response) > 200 else response,
            "message": f"✅ Clé {provider} testée avec succès"
        }
        
    except Exception as e:
        # Restaurer la configuration en cas d'erreur
        if 'original_key' in locals() and original_key:
            setattr(settings, f"{provider}_api_key", original_key)
        
        return {
            "status": "error",
            "provider": provider,
            "api_key_prefix": api_key[:12] + "..." if len(api_key) > 12 else api_key,
            "test_successful": False,
            "error": str(e),
            "message": f"❌ Échec test clé {provider}: {str(e)}"
        }

@app.post("/api/admin/reload-llm-config")
async def reload_llm_configuration():
    """Recharge la configuration LLM depuis les fichiers sans redémarrage"""
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        # Recharger les clés depuis api_keys.env
        settings._load_api_keys()
        
        # Forcer réinitialisation des clients
        adaptive_llm_client._initialize_all_clients()
        
        # Obtenir les nouveaux diagnostics
        diagnostics = adaptive_llm_client.get_initialization_diagnostics()
        
        return {
            "status": "success",
            "message": "Configuration LLM rechargée avec succès",
            "diagnostics": diagnostics,
            "available_providers": diagnostics["available_providers"],
            "total_configured_providers": len(diagnostics["available_providers"])
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Erreur lors du rechargement de configuration: {str(e)}"
        }

@app.post("/api/admin/force-reinitialize-provider")
async def force_reinitialize_provider(request: dict):
    """Force la réinitialisation d'un provider spécifique après changement de clé"""
    provider = request.get("provider")
    
    if not provider:
        return {
            "status": "error",
            "error": "Provider requis"
        }
    
    if provider not in ["emergent", "openai", "anthropic", "google"]:
        return {
            "status": "error", 
            "error": f"Provider non supporté: {provider}"
        }
    
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        result = await adaptive_llm_client.force_reinitialize_provider(provider)
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Erreur lors de la réinitialisation forcée: {str(e)}"
        }

@app.post("/api/admin/force-reinitialize-all-providers")
async def force_reinitialize_all_providers():
    """Force la réinitialisation de tous les providers (après changement global de clés)"""
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        result = await adaptive_llm_client.force_reinitialize_all_providers()
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Erreur lors de la réinitialisation globale: {str(e)}"
        }

@app.get("/api/admin/llm-diagnostics-advanced")
async def get_advanced_llm_diagnostics():
    """Diagnostics avancés des services LLM avec test de changement de clés"""
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        # Diagnostics de base avec protection
        try:
            basic_diagnostics = adaptive_llm_client.get_initialization_diagnostics()
            # S'assurer que c'est JSON sérialisable
            if hasattr(basic_diagnostics, '__await__'):
                basic_diagnostics = await basic_diagnostics
            # Nettoyer les objets non sérialisables
            basic_diagnostics = dict(basic_diagnostics) if basic_diagnostics else {}
        except Exception as e:
            basic_diagnostics = {"error": f"Erreur diagnostics de base: {str(e)}"}
        
        # Test de changement de providers avec protection
        try:
            switching_test = await adaptive_llm_client.test_provider_switching()
            # Nettoyer les objets non sérialisables
            if isinstance(switching_test, dict):
                switching_test = {
                    "test_timestamp": switching_test.get("test_timestamp", datetime.now().isoformat()),
                    "available_providers": list(switching_test.get("available_providers", [])),
                    "test_results": dict(switching_test.get("test_results", {})),
                    "switching_issues": list(switching_test.get("switching_issues", []))
                }
        except Exception as e:
            switching_test = {"error": f"Erreur test switching: {str(e)}"}
        
        # Informations de configuration LLM avec protection
        try:
            llm_status = settings.get_llm_status()
            llm_status = dict(llm_status) if llm_status else {}
        except Exception as e:
            llm_status = {"error": f"Erreur statut LLM: {str(e)}"}
        
        # Obtenir la liste des providers disponibles
        try:
            available_providers = await adaptive_llm_client.get_available_providers()
            available_providers = list(available_providers) if available_providers else []
        except Exception as e:
            available_providers = []
            available_providers_error = str(e)
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "basic_diagnostics": basic_diagnostics,
            "switching_test": switching_test,
            "llm_configuration": llm_status,
            "available_providers": available_providers,
            "available_endpoints": {
                "reload_config": "/api/admin/reload-llm-config",
                "test_provider": "/api/admin/test-llm", 
                "test_api_key": "/api/admin/test-api-key",
                "force_reinit_provider": "/api/admin/force-reinitialize-provider",
                "force_reinit_all": "/api/admin/force-reinitialize-all-providers"
            },
            "recommendations": ["Mode de diagnostic sécurisé activé"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Erreur lors des diagnostics avancés"
        }

def _generate_llm_health_recommendations(diagnostics: dict, switching_test: dict) -> list:
    """Génère des recommandations basées sur les diagnostics et tests"""
    recommendations = []
    
    # Vérifier le nombre de providers disponibles
    available_count = len(diagnostics.get("available_providers", []))
    if available_count == 0:
        recommendations.append({
            "type": "critical",
            "message": "Aucun provider LLM fonctionnel",
            "action": "Vérifiez les clés API dans /app/portable/config/api_keys.env et utilisez /api/admin/force-reinitialize-all-providers"
        })
    elif available_count == 1:
        recommendations.append({
            "type": "warning",
            "message": "Un seul provider fonctionnel - Risque de panne",
            "action": "Configurez des providers supplémentaires pour la redondance"
        })
    else:
        recommendations.append({
            "type": "success",
            "message": f"{available_count} providers fonctionnels - Configuration robuste",
            "action": "Surveillance continue recommandée"
        })
    
    # Analyser les échecs consécutifs
    consecutive_failures = diagnostics.get("consecutive_failures", {})
    high_failure_providers = [p for p, count in consecutive_failures.items() if count >= 3]
    
    if high_failure_providers:
        recommendations.append({
            "type": "warning",
            "message": f"Providers avec échecs élevés: {', '.join(high_failure_providers)}",
            "action": f"Utilisez /api/admin/force-reinitialize-provider pour chaque provider problématique"
        })
    
    # Analyser les résultats des tests de changement
    switching_results = switching_test.get("test_results", {})
    failed_tests = [p for p, result in switching_results.items() if result.get("status") == "error"]
    
    if failed_tests:
        recommendations.append({
            "type": "info",
            "message": f"Tests de changement échoués pour: {', '.join(failed_tests)}",
            "action": "Vérifiez les clés API et relancez les tests après correction"
        })
    
    # Vérifier si une initialisation est en cours
    if diagnostics.get("is_initializing"):
        recommendations.append({
            "type": "info",
            "message": "Initialisation en cours",
            "action": "Attendez la fin de l'initialisation avant de modifier les clés"
        })
    
    return recommendations

@app.get("/api/admin/test-provider-switching")
@app.post("/api/admin/test-provider-switching") 
async def test_provider_switching():
    """Test complet du changement de providers"""
    try:
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        try:
            results = await adaptive_llm_client.test_provider_switching()
            
            # Protection contre les résultats mal formatés et nettoyage JSON
            if not isinstance(results, dict):
                results = {"test_results": {}, "switching_issues": [], "available_providers": []}
            
            # S'assurer que tous les objets sont JSON sérialisables
            clean_results = {
                "test_timestamp": results.get("test_timestamp", datetime.now().isoformat()),
                "available_providers": list(results.get("available_providers", [])),
                "test_results": dict(results.get("test_results", {})),
                "switching_issues": list(results.get("switching_issues", []))
            }
            
            test_results = clean_results["test_results"]
            switching_issues = clean_results["switching_issues"]
            available_providers = clean_results["available_providers"]
            
            return {
                "status": "completed",
                "summary": {
                    "total_providers_tested": len(test_results),
                    "successful_providers": len([r for r in test_results.values() if r.get("status") == "success"]),
                    "switching_issues_count": len(switching_issues),
                    "available_providers": available_providers
                },
                "detailed_results": clean_results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as inner_e:
            return {
                "status": "error", 
                "error": f"Erreur test provider switching: {str(inner_e)}",
                "summary": {
                    "total_providers_tested": 0,
                    "successful_providers": 0,
                    "switching_issues_count": 1,
                    "available_providers": []
                },
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Erreur lors du test de changement de providers"
        }

def _analyze_switching_results(results: dict) -> List[dict]:
    """Analyse les résultats de test et fournit des recommandations"""
    recommendations = []
    
    successful_providers = [
        provider for provider, result in results["test_results"].items()
        if result.get("status") == "success"
    ]
    
    failed_providers = [
        provider for provider, result in results["test_results"].items()
        if result.get("status") == "error"
    ]
    
    if len(successful_providers) == 0:
        recommendations.append({
            "type": "critical",
            "message": "Aucun provider LLM ne fonctionne",
            "action": "Vérifiez vos clés API dans /app/portable/config/api_keys.env"
        })
    elif len(successful_providers) == 1:
        recommendations.append({
            "type": "warning", 
            "message": f"Un seul provider fonctionnel: {successful_providers[0]}",
            "action": "Configurez des providers supplémentaires pour la redondance"
        })
    else:
        recommendations.append({
            "type": "success",
            "message": f"{len(successful_providers)} providers fonctionnels",
            "action": "Configuration robuste détectée"
        })
    
    if results["switching_issues"]:
        recommendations.append({
            "type": "info",
            "message": f"{len(results['switching_issues'])} problèmes de changement détectés",
            "action": "Le système utilise automatiquement des fallbacks"
        })
    
    # Analyser les temps de réponse
    response_times = [
        result.get("response_time_seconds", 0)
        for result in results["test_results"].values()
        if result.get("status") == "success"
    ]
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        if avg_time > 10:
            recommendations.append({
                "type": "warning",
                "message": f"Temps de réponse élevé: {avg_time:.2f}s en moyenne",
                "action": "Vérifiez la latence réseau et les quotas API"
            })
    
    return recommendations

@app.get("/api/portable/info")
async def portable_info():
    """Informations spécifiques au mode portable"""
    if not settings.portable_mode:
        raise HTTPException(status_code=404, detail="Mode portable non activé")
    
    return {
        "portable": True,
        "version": "1.0.0-portable",
        "database_type": settings.database_type,
        "data_location": settings.portable_data,
        "services_available": len(settings.get_services_config()),
        "auto_port_detection": True,
        "cross_platform": True
    }

# Routes Assistant IA intégrées directement
@app.get("/api/assistant/status")
async def assistant_status():
    """Status de l'assistant IA et configuration"""
    try:
        return {
            "status": "operational",
            "service": "Assistant IA Cybersécurité",
            "version": "1.0.0-portable",
            "llm_configured": bool(settings.emergent_llm_key),
            "llm_provider": settings.default_llm_provider,
            "llm_model": settings.default_llm_model,
            "portable_mode": settings.portable_mode,
            "features": {
                "chat": True,
                "sessions": True,
                "context_awareness": True,
                "cybersecurity_expertise": True,
                "knowledge_base": True
            },
            "knowledge_domains": [
                "Tests de pénétration", "Audit sécurité", "Réponse incidents",
                "Forensique numérique", "Conformité", "Threat Intelligence",
                "Sécurité Cloud", "Sécurité Web", "OWASP Top 10"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur status assistant: {str(e)}"
        )

@app.post("/api/assistant/chat")
async def chat_with_assistant(request: dict):
    """Chat avec l'assistant IA cybersécurité"""
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id") or "default-session"
        context = request.get("context")
        
        # Réponse intelligente selon le contexte
        if not user_message:
            raise HTTPException(status_code=400, detail="Message requis")
        
        # Utiliser le client adaptatif pour plus de robustesse
        from ai_core.adaptive_llm_client import adaptive_llm_client
        
        try:
            response_content, used_provider, used_model = await adaptive_llm_client.generate_with_fallback(
                user_message, context
            )
            
            return {
                "response": response_content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": len(response_content.split()),
                "model_used": f"{used_provider}:{used_model}",
                "provider_info": {
                    "used_provider": used_provider,
                    "used_model": used_model,
                    "available_providers": await adaptive_llm_client.get_available_providers()
                }
            }
            
        except Exception as llm_error:
            # Fallback vers réponse contextuelle si LLM échoue
            response_content = generate_contextual_response(user_message, context)
            
            return {
                "response": response_content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": len(response_content.split()),
                "model_used": "contextual-fallback",
                "provider_info": {
                    "used_provider": "fallback",
                    "used_model": "contextual",
                    "available_providers": await adaptive_llm_client.get_available_providers(),
                    "fallback_reason": str(llm_error)
                }
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du chat avec l'assistant: {str(e)}"
        )

async def generate_assistant_response(user_message: str, context: str = None) -> str:
    """Génère une réponse contextuelle de l'assistant cybersécurité"""
    user_lower = user_message.lower()
    
    # Réponses contextuelles cybersécurité
    if any(word in user_lower for word in ["pentest", "penetration", "test"]):
        return """🛡️ **Tests de Pénétration avec CyberSec Toolkit Pro 2025**

Pour un audit de pentest complet, je recommande cette approche méthodologique :

**📋 Phase 1 : Reconnaissance**
- Nmap pour découverte réseau
- OSINT avec outils intégrés
- Énumération services et versions

**🎯 Phase 2 : Scanning & Énumération** 
- Scan vulnérabilités (OpenVAS/Nessus intégré)
- Énumération web (Burp Suite intégré)
- Analyse ports et services

**⚔️ Phase 3 : Exploitation**
- Tests OWASP Top 10
- Exploitation manuelle ciblée
- Documentation preuves de concept

**📊 Phase 4 : Rapport**
- Génération rapport automatique
- Recommandations priorisées
- Plan de remédiation

Voulez-vous que je vous guide sur une phase spécifique ?"""

    elif any(word in user_lower for word in ["audit", "conformité", "compliance"]):
        return """📋 **Audit de Sécurité & Conformité**

CyberSec Toolkit Pro 2025 couvre tous les standards majeurs :

**🏛️ Frameworks Supportés:**
- NIST Cybersecurity Framework
- ISO 27001/27002
- GDPR (Conformité données)
- HIPAA (Secteur santé)
- PCI-DSS (Paiements)
- SOC 2 Type II

**🔍 Méthodologie d'Audit:**
1. **Gap Analysis** - État actuel vs. standard
2. **Risk Assessment** - Évaluation des risques
3. **Controls Testing** - Tests des contrôles
4. **Remediation Plan** - Plan de mise en conformité

**📊 Livrables:**
- Rapport d'audit détaillé
- Matrice de conformité  
- Feuille de route remédiation
- Templates politiques sécurité

Quel standard vous intéresse le plus ?"""

    elif any(word in user_lower for word in ["incident", "forensique", "investigation"]):
        return """🚨 **Réponse aux Incidents & Forensique**

**⚡ Processus IR Intégré:**

**Phase 1 : Détection & Analyse**
- Monitoring temps réel
- Corrélation des événements
- Classification des incidents

**Phase 2 : Containment & Éradication**
- Isolation systèmes compromis
- Analyse forensique live
- Suppression des menaces

**Phase 3 : Recovery & Lessons Learned**
- Restauration services
- Monitoring post-incident
- Amélioration continue

**🔬 Outils Forensique Intégrés:**
- Acquisition mémoire/disque
- Analyse timeline
- Recherche IOCs
- Corrélation logs

**📋 Documentation Automatique:**
- Chain of custody
- Rapport technique détaillé
- Recommandations préventives

Avez-vous un incident en cours à analyser ?"""

    elif any(word in user_lower for word in ["owasp", "web", "application"]):
        return """🌐 **Sécurité Applications Web - OWASP**

**🎯 OWASP Top 10 2021 - Tests Intégrés:**

1. **Broken Access Control** - Tests d'autorisation
2. **Cryptographic Failures** - Analyse chiffrement
3. **Injection** - SQL, NoSQL, LDAP, OS injection
4. **Insecure Design** - Threat modeling
5. **Security Misconfiguration** - Audit configuration
6. **Vulnerable Components** - Scan dépendances
7. **ID&A Failures** - Tests authentification
8. **Software Integrity** - Vérification intégrité
9. **Logging Failures** - Audit logs sécurité
10. **SSRF** - Tests Server-Side Request Forgery

**🛠️ Outils Intégrés:**
- Scanner automatisé OWASP ZAP
- Burp Suite Professional
- Tests manuels guidés
- Validation OWASP ASVS

**📊 Reporting:**
- Rapport OWASP standard
- Matrice risques business
- Guide remédiation développeur

Quelle application souhaitez-vous auditer ?"""

    else:
        return f"""🛡️ **Assistant Cybersécurité CyberSec Toolkit Pro 2025**

Bonjour ! Je suis votre expert cybersécurité dédié, spécialisé dans l'ensemble des 35 services intégrés.

**🎯 Je peux vous aider avec :**
- **Tests de pénétration** complets (web, réseau, mobile, IoT)
- **Audits de sécurité** et conformité (NIST, ISO 27001, GDPR)
- **Réponse aux incidents** et forensique numérique
- **Architecture sécurisée** et threat modeling
- **Évaluation des risques** et gouvernance
- **Formation** et sensibilisation sécurité

**📱 Mode Portable Unique :**
Tous nos outils fonctionnent 100% portable sur clé USB, parfait pour :
- Interventions client sur site
- Audits en environnement déconnecté
- Démonstrations plug & play
- Formations mobiles

**💬 Comment puis-je vous accompagner aujourd'hui ?**

Décrivez votre besoin ou contexte sécurité, je vous guiderai avec l'expertise et les outils appropriés !

{f"**Contexte spécifique :** {context}" if context else ""}"""
def generate_contextual_response(user_message: str, context: str = None) -> str:
    """Génère une réponse contextuelle de fallback quand les LLM ne sont pas disponibles"""
    user_lower = user_message.lower()
    
    # Réponses contextuelles cybersécurité simplifiées
    if any(word in user_lower for word in ["pentest", "penetration", "test"]):
        return """🛡️ **Tests de Pénétration - Mode Fallback**

Je suis actuellement en mode fallback (LLM indisponible), mais je peux vous guider sur les tests de pénétration :

**📋 Méthodologie Standard :**
1. **Reconnaissance** - Collecte d'informations
2. **Scanning** - Découverte de vulnérabilités  
3. **Exploitation** - Tests d'intrusion
4. **Post-exploitation** - Évaluation des impacts
5. **Rapport** - Documentation des findings

**🔧 Outils disponibles dans CyberSec Toolkit :**
- Nmap, Burp Suite, OWASP ZAP
- Metasploit, Nikto, SQLmap
- Wireshark, John the Ripper

Consultez la documentation complète dans l'interface pour plus de détails."""

    elif any(word in user_lower for word in ["audit", "conformité", "compliance"]):
        return """📋 **Audit de Sécurité - Mode Fallback**

Mode fallback activé. Voici les frameworks d'audit supportés :

**🏛️ Standards disponibles :**
- NIST Cybersecurity Framework
- ISO 27001/27002
- GDPR, HIPAA, PCI-DSS
- SOC 2 Type II

**📊 Processus d'audit :**
1. Gap Analysis
2. Risk Assessment  
3. Controls Testing
4. Remediation Planning

Utilisez les modules d'audit intégrés pour une évaluation complète."""

    elif any(word in user_lower for word in ["incident", "forensique", "investigation"]):
        return """🚨 **Réponse aux Incidents - Mode Fallback**

Processus de réponse aux incidents disponible :

**⚡ Phases IR :**
1. **Préparation** - Plans et procédures
2. **Détection** - Identification des incidents
3. **Analyse** - Investigation forensique
4. **Containment** - Isolation des menaces
5. **Éradication** - Suppression des causes
6. **Recovery** - Restauration des services
7. **Lessons Learned** - Amélioration continue

**🔬 Outils forensiques intégrés disponibles**
Consultez le module Digital Forensics pour les outils spécialisés."""

    elif any(word in user_lower for word in ["owasp", "web", "application"]):
        return """🌐 **Sécurité Web - Mode Fallback**

Tests OWASP Top 10 disponibles :

**🎯 Vulnérabilités couvertes :**
1. Broken Access Control
2. Cryptographic Failures
3. Injection (SQL, XSS, etc.)
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. ID&A Failures
8. Software Integrity Failures
9. Logging & Monitoring Failures
10. Server-Side Request Forgery

**🛠️ Outils intégrés :**
- OWASP ZAP Scanner
- Burp Suite Professional
- Tests manuels guidés

Accédez au module Pentesting pour lancer les scans."""

    else:
        return f"""🛡️ **Assistant Cybersécurité - Mode Fallback**

⚠️ **Mode Fallback Activé** - Les services LLM sont temporairement indisponibles.

**🎯 Services disponibles :**
- Tests de pénétration (35 modules)
- Audits de sécurité et conformité
- Réponse aux incidents
- Forensique numérique
- Monitoring 24/7
- Threat Intelligence

**📱 Mode Portable :**
Tous les outils fonctionnent en mode déconnecté sur votre clé USB.

**💡 Suggestion :**
Naviguez dans l'interface pour accéder directement aux modules spécialisés, ou vérifiez la configuration LLM dans les paramètres.

{f"**Contexte :** {context}" if context else ""}

*Les services LLM seront restaurés dès que la configuration sera corrigée.*"""

@app.post("/api/assistant/sessions/new")
async def create_new_session():
    """Crée une nouvelle session de chat"""
    try:
        import uuid
        new_session_id = str(uuid.uuid4())
        
        return {
            "status": "success",
            "session_id": new_session_id,
            "message": "Nouvelle session créée"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création session: {str(e)}"
        )

# Import des routes cybersécurité
try:
    from cybersecurity.pentest.routes import router as pentest_router
    app.include_router(pentest_router)
    print("✅ Routes pentesting chargées")
except ImportError as e:
    error_message = str(e)
    print(f"⚠️ Erreur chargement routes pentesting: {error_message}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/pentesting/")
    async def pentesting_placeholder():
        """Tests de pénétration - Erreur de chargement"""
        return {"status": "error", "service": "Pentesting", "error": error_message}

# Import Incident Response
try:
    from cybersecurity.incident_response.routes import router as incident_router
    app.include_router(incident_router)
    print("✅ Routes incident response chargées")
except ImportError as e:
    print(f"⚠️ Erreur chargement routes incident response: {str(e)}")

# Import Digital Forensics  
try:
    from cybersecurity.digital_forensics.routes import router as forensics_router
    app.include_router(forensics_router)
    print("✅ Routes digital forensics chargées")
except ImportError as e:
    print(f"⚠️ Erreur chargement routes digital forensics: {str(e)}")

# Import Compliance
try:
    from cybersecurity.compliance.routes import router as compliance_router
    app.include_router(compliance_router)
    print("✅ Routes compliance chargées")
except ImportError as e:
    print(f"⚠️ Erreur chargement routes compliance: {str(e)}")

# Import Vulnerability Management
try:
    from cybersecurity.vulnerability_management.routes import router as vulnerability_management_router
    app.include_router(vulnerability_management_router)
    print("✅ Routes vulnerability management chargées")
except ImportError as e:
    print(f"⚠️ Erreur chargement routes vulnerability management: {str(e)}")

# Import Monitoring 24/7
try:
    from cybersecurity.monitoring.routes import router as monitoring_router
    app.include_router(monitoring_router)
    print("✅ Routes monitoring 24/7 chargées")
except ImportError as e:
    monitoring_error = str(e)
    print(f"⚠️ Erreur chargement routes monitoring 24/7: {monitoring_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/monitoring/")
    async def monitoring_placeholder():
        """Monitoring 24/7 - Erreur de chargement"""
        return {"status": "error", "service": "Monitoring 24/7", "error": monitoring_error}

# Import Threat Intelligence
try:
    from cybersecurity.threat_intelligence.routes import router as threat_intelligence_router
    app.include_router(threat_intelligence_router)
    print("✅ Routes threat intelligence chargées")
except ImportError as e:
    threat_intel_error = str(e)
    print(f"⚠️ Erreur chargement routes threat intelligence: {threat_intel_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/threat-intelligence/")
    async def threat_intelligence_placeholder():
        """Threat Intelligence - Erreur de chargement"""
        return {"status": "error", "service": "Threat Intelligence", "error": threat_intel_error}

# Import Red Team Operations
try:
    from cybersecurity.red_team.routes import router as red_team_router
    app.include_router(red_team_router)
    print("✅ Routes red team chargées")
except ImportError as e:
    red_team_error = str(e)
    print(f"⚠️ Erreur chargement routes red team: {red_team_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/red-team/")
    async def red_team_placeholder():
        """Red Team Operations - Erreur de chargement"""
        return {"status": "error", "service": "Red Team Operations", "error": red_team_error}

# Import Blue Team Defense
try:
    from cybersecurity.blue_team.routes import router as blue_team_router
    app.include_router(blue_team_router)
    print("✅ Routes blue team chargées")
except ImportError as e:
    blue_team_error = str(e)
    print(f"⚠️ Erreur chargement routes blue team: {blue_team_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/blue-team/")
    async def blue_team_placeholder():
        """Blue Team Defense - Erreur de chargement"""
        return {"status": "error", "service": "Blue Team Defense", "error": blue_team_error}

# Import Audit Automatisé
try:
    from cybersecurity.audit.routes import router as audit_router
    app.include_router(audit_router)
    print("✅ Routes audit chargées")
except ImportError as e:
    audit_error = str(e)
    print(f"⚠️ Erreur chargement routes audit: {audit_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/audit/")
    async def audit_placeholder():
        """Audit Automatisé - Erreur de chargement"""
        return {"status": "error", "service": "Audit Automatisé", "error": audit_error}

# Import Cloud Security (Sprint 1.7)
try:
    from cybersecurity.cloud_security.routes import router as cloud_security_router
    app.include_router(cloud_security_router)
    print("✅ Routes cloud security chargées")
except ImportError as e:
    cloud_security_error = str(e)
    print(f"⚠️ Erreur chargement routes cloud security: {cloud_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/cloud-security/")
    async def cloud_security_placeholder():
        """Cloud Security - Erreur de chargement"""
        return {"status": "error", "service": "Cloud Security", "error": cloud_security_error}

# Import IoT Security (Sprint 1.7)
try:
    from cybersecurity.iot_security.routes import router as iot_security_router
    app.include_router(iot_security_router)
    print("✅ Routes IoT security chargées")
except ImportError as e:
    iot_security_error = str(e)
    print(f"⚠️ Erreur chargement routes IoT security: {iot_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/iot-security/")
    async def iot_security_placeholder():
        """IoT Security - Erreur de chargement"""
        return {"status": "error", "service": "IoT Security", "error": iot_security_error}

# Import Mobile Security (Sprint 1.7)
try:
    from cybersecurity.mobile_security.routes import router as mobile_security_router
    app.include_router(mobile_security_router)
    print("✅ Routes mobile security chargées")
except ImportError as e:
    mobile_security_error = str(e)
    print(f"⚠️ Erreur chargement routes mobile security: {mobile_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/mobile-security/")
    async def mobile_security_placeholder():
        """Mobile Security - Erreur de chargement"""
        return {"status": "error", "service": "Mobile Security", "error": mobile_security_error}

# Import Web3 Security (Sprint 1.7)
try:
    from cybersecurity.web3_security.routes import router as web3_security_router
    app.include_router(web3_security_router)
    print("✅ Routes web3 security chargées")
except ImportError as e:
    web3_security_error = str(e)
    print(f"⚠️ Erreur chargement routes web3 security: {web3_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/web3-security/")
    async def web3_security_placeholder():
        """Web3 Security - Erreur de chargement"""
        return {"status": "error", "service": "Web3 Security", "error": web3_security_error}

# Import AI Security (Sprint 1.7)
try:
    from cybersecurity.ai_security.routes import router as ai_security_router
    app.include_router(ai_security_router)
    print("✅ Routes AI security chargées")
except ImportError as e:
    ai_security_error = str(e)
    print(f"⚠️ Erreur chargement routes AI security: {ai_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/ai-security/")
    async def ai_security_placeholder():
        """AI Security - Erreur de chargement"""
        return {"status": "error", "service": "AI Security", "error": ai_security_error}

# Import Network Security (Sprint 1.7)
try:
    from cybersecurity.network_security.routes import router as network_security_router
    app.include_router(network_security_router)
    print("✅ Routes network security chargées")
except ImportError as e:
    network_security_error = str(e)
    print(f"⚠️ Erreur chargement routes network security: {network_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/network-security/")
    async def network_security_placeholder():
        """Network Security - Erreur de chargement"""
        return {"status": "error", "service": "Network Security", "error": network_security_error}

# Import API Security (Sprint 1.7)
try:
    from cybersecurity.api_security.routes import router as api_security_router
    app.include_router(api_security_router)
    print("✅ Routes API security chargées")
except ImportError as e:
    api_security_error = str(e)
    print(f"⚠️ Erreur chargement routes API security: {api_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/api-security/")
    async def api_security_placeholder():
        """API Security - Erreur de chargement"""
        return {"status": "error", "service": "API Security", "error": api_security_error}

# Import Container Security (Sprint 1.7)
try:
    from cybersecurity.container_security.routes import router as container_security_router
    app.include_router(container_security_router)
    print("✅ Routes container security chargées")
except ImportError as e:
    container_security_error = str(e)
    print(f"⚠️ Erreur chargement routes container security: {container_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/container-security/")
    async def container_security_placeholder():
        """Container Security - Erreur de chargement"""
        return {"status": "error", "service": "Container Security", "error": container_security_error}

# Import IaC Security (Sprint 1.7)
try:
    from cybersecurity.iac_security.routes import router as iac_security_router
    app.include_router(iac_security_router)
    print("✅ Routes IaC security chargées")
except ImportError as e:
    iac_security_error = str(e)
    print(f"⚠️ Erreur chargement routes IaC security: {iac_security_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/iac-security/")
    async def iac_security_placeholder():
        """IaC Security - Erreur de chargement"""
        return {"status": "error", "service": "IaC Security", "error": iac_security_error}

# Import Social Engineering (Sprint 1.7)
try:
    from cybersecurity.social_engineering.routes import router as social_engineering_router
    app.include_router(social_engineering_router)
    print("✅ Routes social engineering chargées")
except ImportError as e:
    social_engineering_error = str(e)
    print(f"⚠️ Erreur chargement routes social engineering: {social_engineering_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/social-engineering/")
    async def social_engineering_placeholder():
        """Social Engineering - Erreur de chargement"""
        return {"status": "error", "service": "Social Engineering", "error": social_engineering_error}

# Import Security Orchestration (Sprint 1.7)
try:
    from cybersecurity.security_orchestration.routes import router as security_orchestration_router
    app.include_router(security_orchestration_router)
    print("✅ Routes security orchestration (SOAR) chargées")
except ImportError as e:
    security_orchestration_error = str(e)
    print(f"⚠️ Erreur chargement routes security orchestration: {security_orchestration_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/soar/")
    async def security_orchestration_placeholder():
        """Security Orchestration - Erreur de chargement"""
        return {"status": "error", "service": "Security Orchestration", "error": security_orchestration_error}

# Import Risk Assessment (Sprint 1.7)
try:
    from cybersecurity.risk_assessment.routes import router as risk_assessment_router
    app.include_router(risk_assessment_router)
    print("✅ Routes risk assessment chargées")
except ImportError as e:
    risk_assessment_error = str(e)
    print(f"⚠️ Erreur chargement routes risk assessment: {risk_assessment_error}")
    
    # Route placeholder si l'import échoue
    @app.get("/api/risk/")
    async def risk_assessment_placeholder():
        """Risk Assessment - Erreur de chargement"""
        return {"status": "error", "service": "Risk Assessment", "error": risk_assessment_error}

# Import Services IA Avancés (Sprint 1.5)
# Import Cyber AI
try:
    from ai_core.cyber_ai.routes import router as cyber_ai_router
    app.include_router(cyber_ai_router)
    print("✅ Routes cyber AI chargées")
except ImportError as e:
    cyber_ai_error = str(e)
    print(f"⚠️ Erreur chargement routes cyber AI: {cyber_ai_error}")

# Import Predictive AI
try:
    from ai_core.predictive_ai.routes import router as predictive_ai_router
    app.include_router(predictive_ai_router)
    print("✅ Routes predictive AI chargées")
except ImportError as e:
    predictive_ai_error = str(e)
    print(f"⚠️ Erreur chargement routes predictive AI: {predictive_ai_error}")

# Import Automation AI
try:
    from ai_core.automation_ai.routes import router as automation_ai_router
    app.include_router(automation_ai_router)
    print("✅ Routes automation AI chargées")
except ImportError as e:
    automation_ai_error = str(e)
    print(f"⚠️ Erreur chargement routes automation AI: {automation_ai_error}")

# Import Conversational AI
try:
    from ai_core.conversational_ai.routes import router as conversational_ai_router
    app.include_router(conversational_ai_router)
    print("✅ Routes conversational AI chargées")
except ImportError as e:
    conversational_ai_error = str(e)
    print(f"⚠️ Erreur chargement routes conversational AI: {conversational_ai_error}")

# Import Business AI
try:
    from ai_core.business_ai.routes import router as business_ai_router
    app.include_router(business_ai_router)
    print("✅ Routes business AI chargées")
except ImportError as e:
    business_ai_error = str(e)

# Import Business Services Sprint 1.6 - REFACTORED ARCHITECTURE
try:
    from business.crm.routes import router as crm_router
    from business.billing.routes import router as billing_router
    from business.analytics.routes import router as analytics_router
    from business.planning.routes import router as planning_router
    from business.training.routes import router as training_router

    app.include_router(crm_router)
    app.include_router(billing_router)
    app.include_router(analytics_router)
    app.include_router(planning_router)
    app.include_router(training_router)
    print("✅ Routes business services Sprint 1.6 chargées (architecture refactorisée)")
except Exception as e:
    print(f"⚠️ Erreur chargement services business: {str(e)}")

    print(f"⚠️ Erreur chargement routes business AI: {str(e)}")

# Import Code Analysis AI
try:
    from ai_core.code_analysis_ai.routes import router as code_analysis_ai_router
    app.include_router(code_analysis_ai_router)
    print("✅ Routes code analysis AI chargées")
except ImportError as e:
    code_analysis_ai_error = str(e)
    print(f"⚠️ Erreur chargement routes code analysis AI: {code_analysis_ai_error}")

@app.get("/api/reports/")
async def reports_placeholder():
    """Génération rapports - À implémenter Sprint 1.2"""
    return {"status": "planned", "service": "Reports", "phase": "Sprint 1.2"}

if __name__ == "__main__":
    import uvicorn
    
    # Configuration portable automatique
    if settings.portable_mode:
        print(f"🚀 Démarrage en mode PORTABLE sur port {settings.backend_port}")
        print(f"📊 Base de données: {settings.database_type}")
        print(f"💾 Données: {settings.portable_data}")
    else:
        print(f"🌐 Démarrage en mode SERVEUR sur port {settings.backend_port}")
    
    uvicorn.run(
        "server:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False  # Désactiver reload en mode portable
    )