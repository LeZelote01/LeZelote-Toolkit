# CRM Service Main Module
"""
CRM Service for CyberSec Toolkit Pro 2025
Manages clients and projects with full CRUD operations
"""

from .routes import router

# Export the router for import in server.py
crm_router = router

# Service metadata
SERVICE_INFO = {
    "name": "CRM",
    "description": "Customer Relationship Management",
    "version": "1.0.0",
    "endpoints": {
        "clients": "/api/crm/clients",
        "projects": "/api/crm/projects",
        "status": "/api/crm/status"
    }
}