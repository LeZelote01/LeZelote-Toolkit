# Endpoint principal du service cloud_security - Implémentation complète Sprint 1.7
from fastapi import APIRouter
from .routes import router as cloud_security_routes

# Export du router principal
cloud_security_router = cloud_security_routes