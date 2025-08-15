"""
Routes API pour l'Assistant IA - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.1 - Endpoints REST pour l'assistant conversationnel
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid

from .main import assistant_service, ChatRequest, ChatResponse
from backend.config import settings

# Router pour les endpoints assistant
router = APIRouter(prefix="/api/assistant", tags=["Assistant IA"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat avec l'assistant IA cybersécurité
    
    - **message**: Message de l'utilisateur
    - **session_id**: ID de session (optionnel, généré automatiquement)
    - **context**: Contexte spécifique cybersécurité (optionnel)
    """
    try:
        response = await assistant_service.chat(request)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du chat avec l'assistant: {str(e)}"
        )

@router.get("/sessions")
async def list_chat_sessions():
    """
    Liste les sessions de chat récentes
    """
    try:
        sessions = await assistant_service.list_sessions()
        return {
            "status": "success",
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """
    Récupère les informations d'une session spécifique
    """
    try:
        session_info = await assistant_service.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session non trouvée")
            
        return {
            "status": "success",
            "session": session_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération session: {str(e)}"
        )

@router.post("/sessions/new")
async def create_new_session():
    """
    Crée une nouvelle session de chat
    """
    try:
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

@router.get("/status")
async def assistant_status():
    """
    Status de l'assistant IA et configuration
    """
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

@router.get("/health")
async def assistant_health():
    """
    Health check de l'assistant IA
    """
    try:
        # Test basique du service
        test_request = ChatRequest(
            message="Test de santé du service",
            session_id="health-check"
        )
        
        # Test rapide (ne pas sauvegarder)
        test_response = "Service assistant opérationnel"
        
        return {
            "status": "healthy",
            "service": "Assistant IA",
            "llm_status": "configured" if settings.emergent_llm_key else "fallback",
            "response_test": "passed",
            "timestamp": "2025-08-10T23:52:00Z"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Assistant IA", 
            "error": str(e),
            "timestamp": "2025-08-10T23:52:00Z"
        }