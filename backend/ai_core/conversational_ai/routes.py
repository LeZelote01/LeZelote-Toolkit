"""
Routes API pour Conversational AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Endpoints REST pour l'IA conversationnelle
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel

from .main import conversational_ai_service, ConversationMessage, ConversationResponse, ConversationContext, ConversationFlow
from backend.config import settings

router = APIRouter(prefix="/api/conversational-ai", tags=["Conversational AI"])

class StartConversationRequest(BaseModel):
    user_id: str
    conversation_type: str = "general"
    user_profile: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ConversationResponse)
async def chat_conversation(message: ConversationMessage):
    try:
        response = await conversational_ai_service.process_message(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chat conversationnel: {str(e)}")

@router.post("/start-conversation")
async def start_conversation(request: StartConversationRequest):
    try:
        session_id = str(uuid.uuid4())
        context = ConversationContext(
            user_id=request.user_id,
            session_id=session_id,
            conversation_type=request.conversation_type,
            user_profile=request.user_profile or {}
        )
        welcome_message = ConversationMessage(
            content="Bonjour! Comment puis-je vous aider aujourd'hui?",
            message_type="welcome",
            context=context
        )
        welcome_response = await conversational_ai_service.process_message(welcome_message)
        return {
            "status": "started",
            "session_id": session_id,
            "conversation_type": request.conversation_type,
            "welcome_message": welcome_response.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage conversation: {str(e)}")


@router.get("/status")
async def conv_status():
    try:
        return {
            "status": "operational",
            "service": "Conversational AI",
            "version": "1.0.0-portable",
            "llm_configured": conversational_ai_service.llm_client is not None,
            "flows": list(conversational_ai_service.conversation_flows.keys()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur status Conversational AI: {str(e)}")

@router.get("/conversation-flows")
async def list_conversation_flows():
    try:
        return {"flows": {fid: {
            "flow_id": flow.flow_id,
            "flow_name": flow.flow_name,
            "description": flow.description,
            "triggers": flow.triggers,
            "steps": len(flow.steps),
            "is_active": flow.is_active
        } for fid, flow in conversational_ai_service.conversation_flows.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération flows: {str(e)}")

@router.get("/active-conversations")
async def list_active_conversations():
    try:
        return {"active_conversations": list(conversational_ai_service.active_conversations.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération conversations: {str(e)}")

# Les autres endpoints restent inchangés