"""
Routes API pour le Mode Stealth - CyberSec Toolkit Pro 2025
Interface REST pour les fonctionnalités de furtivité avancée
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import asyncio

from .stealth_core import StealthCore, StealthConfig, StealthLevel
from .network_obfuscation import NetworkObfuscator
from .signature_evasion import SignatureEvasion
from .anti_forensics import AntiForensics

# Instance globale du gestionnaire stealth
stealth_manager = StealthCore()

# Router pour les endpoints stealth
stealth_router = APIRouter(prefix="/api/stealth-mode", tags=["Stealth Mode"])


# ============================================================================
# MODÈLES PYDANTIC POUR L'API
# ============================================================================

class StealthConfigRequest(BaseModel):
    """Modèle de requête pour la configuration stealth"""
    level: str = Field(default="medium", description="Niveau de furtivité (low, medium, high, ghost)")
    tor_enabled: bool = Field(default=True, description="Activer Tor")
    vpn_chaining: bool = Field(default=False, description="Activer chaînage VPN")
    signature_evasion: bool = Field(default=True, description="Activer évasion de signatures")
    anti_forensics: bool = Field(default=True, description="Activer protection anti-forensique")
    decoy_traffic: bool = Field(default=False, description="Générer trafic decoy")
    mac_spoofing: bool = Field(default=False, description="Activer spoofing MAC")
    process_hiding: bool = Field(default=True, description="Masquer les processus")
    memory_cleaning: bool = Field(default=True, description="Nettoyage mémoire automatique")
    log_anonymization: bool = Field(default=True, description="Anonymisation des logs")
    dns_over_https: bool = Field(default=True, description="DNS over HTTPS")
    custom_user_agents: Optional[List[str]] = Field(default=None, description="User agents personnalisés")
    timing_variation_min: float = Field(default=1.0, description="Délai minimum (secondes)")
    timing_variation_max: float = Field(default=30.0, description="Délai maximum (secondes)")


class StealthOperationRequest(BaseModel):
    """Modèle de requête pour une opération stealth"""
    operation_type: str = Field(..., description="Type d'opération (scan, test, crawl, etc.)")
    target: str = Field(..., description="Cible de l'opération")
    session_id: str = Field(..., description="ID de la session stealth")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Paramètres spécifiques")


class WAFEvasionRequest(BaseModel):
    """Modèle de requête pour l'évasion WAF"""
    payload: str = Field(..., description="Payload à transformer")
    waf_type: str = Field(default="generic", description="Type de WAF (cloudflare, aws, generic)")


class EvasionProfileRequest(BaseModel):
    """Modèle de requête pour configuration d'évasion"""
    profile_name: str = Field(default="browser_standard", description="Profil d'évasion")
    custom_user_agents: Optional[List[str]] = Field(default=None, description="User agents custom")
    timing_min: Optional[float] = Field(default=None, description="Délai minimum")
    timing_max: Optional[float] = Field(default=None, description="Délai maximum")


# ============================================================================
# ENDPOINTS PRINCIPAUX
# ============================================================================

@stealth_router.get("/", summary="Status du service Stealth Mode")
async def get_stealth_status():
    """Récupère le statut général du service Stealth Mode"""
    try:
        stats = stealth_manager.get_stealth_stats()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "operational",
                "service": "Stealth Mode",
                "version": "1.0.0-advanced",
                "description": "Mode furtif avancé avec obfuscation réseau, évasion de signatures et anti-forensique",
                "features": {
                    "network_obfuscation": True,
                    "tor_integration": True,
                    "vpn_chaining": True,
                    "signature_evasion": True,
                    "anti_forensics": True,
                    "decoy_traffic": True,
                    "memory_cleaning": True,
                    "log_anonymization": True,
                    "process_hiding": True
                },
                "stealth_levels": ["low", "medium", "high", "ghost"],
                "evasion_profiles": ["browser_standard", "mobile", "api_client", "stealth_max"],
                "supported_operations": ["port_scan", "vulnerability_scan", "web_crawl", "api_test"],
                "active_sessions": stats.get("active_sessions", 0),
                "total_operations": stats.get("total_active_operations", 0),
                "uptime": stats.get("uptime", "0:00:00"),
                "components_status": stats.get("components_status", {})
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut: {str(e)}")


@stealth_router.post("/sessions", summary="Créer une session stealth")
async def create_stealth_session(config: StealthConfigRequest):
    """
    Crée une nouvelle session stealth avec la configuration spécifiée
    """
    try:
        # Validation du niveau
        try:
            stealth_level = StealthLevel(config.level.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Niveau invalide: {config.level}")
        
        # Création de la configuration stealth
        stealth_config = StealthConfig(
            level=stealth_level,
            tor_enabled=config.tor_enabled,
            vpn_chaining=config.vpn_chaining,
            signature_evasion=config.signature_evasion,
            anti_forensics=config.anti_forensics,
            decoy_traffic=config.decoy_traffic,
            mac_spoofing=config.mac_spoofing,
            process_hiding=config.process_hiding,
            memory_cleaning=config.memory_cleaning,
            log_anonymization=config.log_anonymization,
            dns_over_https=config.dns_over_https,
            custom_user_agents=config.custom_user_agents,
            timing_variation_range=(config.timing_variation_min, config.timing_variation_max)
        )
        
        # Création de la session
        session_id = await stealth_manager.create_stealth_session(stealth_config)
        
        # Récupération des détails de la session
        session_details = await stealth_manager.get_session_status(session_id)
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "created",
                "session_id": session_id,
                "message": "Session stealth créée avec succès",
                "configuration": {
                    "level": config.level,
                    "tor_enabled": config.tor_enabled,
                    "vpn_chaining": config.vpn_chaining,
                    "signature_evasion": config.signature_evasion,
                    "anti_forensics": config.anti_forensics
                },
                "session_details": session_details,
                "next_steps": [
                    f"Utilisez session_id '{session_id}' pour vos opérations",
                    "Configurez l'évasion de signatures avec /evasion/configure",
                    "Lancez vos opérations avec /operations/execute"
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création session: {str(e)}")


@stealth_router.get("/sessions/{session_id}", summary="Status d'une session stealth")
async def get_session_status(session_id: str):
    """Récupère le statut détaillé d'une session stealth"""
    try:
        session_status = await stealth_manager.get_session_status(session_id)
        
        if 'error' in session_status:
            raise HTTPException(status_code=404, detail=session_status['error'])
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "active",
                "session_status": session_status,
                "available_operations": [
                    "port_scan - Scan de ports furtif",
                    "vulnerability_scan - Scan de vulnérabilités",
                    "web_crawl - Exploration web anonyme",
                    "api_test - Tests API sécurisés"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération session: {str(e)}")


@stealth_router.post("/operations/execute", summary="Exécuter une opération stealth")
async def execute_stealth_operation(operation: StealthOperationRequest):
    """
    Exécute une opération en mode stealth
    """
    try:
        # Validation des paramètres
        supported_operations = ["port_scan", "vulnerability_scan", "web_crawl", "api_test"]
        if operation.operation_type not in supported_operations:
            raise HTTPException(
                status_code=400, 
                detail=f"Opération non supportée. Types supportés: {supported_operations}"
            )
        
        # Exécution de l'opération stealth
        result = await stealth_manager.execute_stealth_operation(
            session_id=operation.session_id,
            operation_type=operation.operation_type,
            target=operation.target,
            params=operation.params or {}
        )
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=400, detail=result.get('error', 'Erreur inconnue'))
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "completed",
                "operation_result": result,
                "security_assessment": {
                    "detection_risk": result.get('detection_risk', 'unknown'),
                    "stealth_level": result.get('stealth_level', 'unknown'),
                    "traces_cleaned": True,
                    "anonymity_maintained": True
                },
                "recommendations": [
                    "Vérifiez les résultats de détection",
                    "Considérez attendre avant la prochaine opération",
                    "Surveillez les logs pour détecter toute activité suspecte"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur exécution opération: {str(e)}")


@stealth_router.delete("/sessions/{session_id}", summary="Terminer une session stealth")
async def terminate_stealth_session(session_id: str, background_tasks: BackgroundTasks):
    """
    Termine une session stealth et effectue le nettoyage complet
    """
    try:
        # Terminaison de la session avec nettoyage
        termination_result = await stealth_manager.terminate_stealth_session(session_id)
        
        if 'error' in termination_result:
            raise HTTPException(status_code=404, detail=termination_result['error'])
        
        # Nettoyage anti-forensique en arrière-plan
        background_tasks.add_task(
            _background_deep_cleanup,
            session_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "terminated",
                "session_id": session_id,
                "termination_result": termination_result,
                "cleanup_status": {
                    "traces_cleaned": True,
                    "identity_restored": True,
                    "deep_cleanup_scheduled": True,
                    "forensic_risk": "minimal"
                },
                "message": "Session terminée et nettoyage effectué avec succès"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur terminaison session: {str(e)}")


@stealth_router.post("/evasion/configure", summary="Configurer l'évasion de signatures")
async def configure_signature_evasion(config: EvasionProfileRequest):
    """Configure le module d'évasion de signatures"""
    try:
        # Configuration du module d'évasion
        await stealth_manager.signature_evasion.configure(
            profile_name=config.profile_name,
            user_agents=config.custom_user_agents,
            timing_range=(config.timing_min, config.timing_max) if config.timing_min and config.timing_max else None,
            enabled=True
        )
        
        # Récupération des informations du profil actif
        profile_info = stealth_manager.signature_evasion.get_active_profile_info()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "configured",
                "message": "Évasion de signatures configurée avec succès",
                "active_profile": profile_info,
                "capabilities": {
                    "user_agent_rotation": True,
                    "header_randomization": True,
                    "payload_transformation": True,
                    "timing_variation": True,
                    "waf_evasion": True
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur configuration évasion: {str(e)}")


@stealth_router.post("/evasion/waf", summary="Test d'évasion WAF")
async def test_waf_evasion(request: WAFEvasionRequest):
    """Teste l'évasion d'un Web Application Firewall (WAF)"""
    try:
        # Test d'évasion WAF
        evasion_result = await stealth_manager.signature_evasion.evade_waf_detection(
            payload=request.payload,
            waf_type=request.waf_type
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "analyzed",
                "evasion_analysis": evasion_result,
                "recommendations": [
                    "Testez les payloads transformés un par un",
                    "Variez les délais entre les tentatives",
                    "Surveillez les réponses pour détecter la détection"
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur test évasion WAF: {str(e)}")


@stealth_router.get("/network/identity", summary="Identité réseau actuelle")
async def get_network_identity():
    """Récupère l'identité réseau obfusquée actuelle"""
    try:
        identity_info = stealth_manager.network_obfuscator.get_current_identity_info()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "active" if identity_info.get('ip_address') else "inactive",
                "network_identity": identity_info,
                "obfuscation_active": identity_info.get('tor_active', False) or 
                                    identity_info.get('proxy_chain_length', 0) > 0,
                "anonymity_level": identity_info.get('security_level', 'unknown')
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération identité: {str(e)}")


@stealth_router.get("/stats", summary="Statistiques complètes")
async def get_complete_stealth_statistics():
    """Récupère les statistiques complètes du mode stealth"""
    try:
        # Statistiques générales
        general_stats = stealth_manager.get_stealth_stats()
        
        # Statistiques d'évasion
        evasion_stats = stealth_manager.signature_evasion.get_evasion_statistics()
        
        # Évaluation forensique
        forensic_assessment = stealth_manager.anti_forensics.get_forensic_risk_assessment()
        
        # Identité réseau
        network_identity = stealth_manager.network_obfuscator.get_current_identity_info()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "general_statistics": general_stats,
                "evasion_statistics": evasion_stats,
                "forensic_assessment": forensic_assessment,
                "network_status": network_identity,
                "overall_security_score": _calculate_overall_security_score(
                    network_identity, evasion_stats, forensic_assessment
                )
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques: {str(e)}")


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

async def _background_deep_cleanup(session_id: str):
    """Tâche de nettoyage approfondi en arrière-plan"""
    try:
        await stealth_manager.anti_forensics.deep_clean_session(session_id)
    except Exception as e:
        print(f"Erreur nettoyage arrière-plan {session_id}: {str(e)}")


def _calculate_overall_security_score(
    network_identity: Dict[str, Any],
    evasion_stats: Dict[str, Any], 
    forensic_assessment: Dict[str, Any]
) -> int:
    """Calcule un score de sécurité global (0-100)"""
    score = 0
    
    # Score réseau (0-40 points)
    anonymity_score = network_identity.get('anonymity_score', 0)
    score += min(40, int(anonymity_score * 0.4))
    
    # Score évasion (0-30 points)
    active_profile = evasion_stats.get('active_profile')
    if active_profile:
        score += 25
    if evasion_stats.get('encoding_techniques_available'):
        score += 5
    
    # Score anti-forensique (0-30 points)
    risk_level = forensic_assessment.get('overall_risk_level', 'high')
    risk_scores = {
        'very_low': 30,
        'low': 25,
        'medium': 15,
        'high': 5,
        'very_high': 0
    }
    score += risk_scores.get(risk_level, 0)
    
    return min(100, score)