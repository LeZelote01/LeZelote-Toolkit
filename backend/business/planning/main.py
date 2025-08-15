# Planning Service Main Module
"""
Planning Service for CyberSec Toolkit Pro 2025
Manages events and scheduling with calendar features
"""

from .routes import router

# Export the router for import in server.py
planning_router = router

# Service metadata
SERVICE_INFO = {
    "name": "Planning",
    "description": "Event and Schedule Management",
    "version": "1.0.0",
    "endpoints": {
        "events": "/api/planning/events",
        "calendar": "/api/planning/events/calendar",
        "status": "/api/planning/status"
    }
}