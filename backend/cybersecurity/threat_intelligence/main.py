# Point d'entrée principal du service Threat Intelligence
from fastapi import APIRouter
from .routes import router as threat_intelligence_router

def get_threat_intelligence_router():
    """Retourne le router du service Threat Intelligence"""
    return threat_intelligence_router
