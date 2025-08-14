# Training Service Main Module
"""
Training Service for CyberSec Toolkit Pro 2025
Manages courses and training sessions with progress tracking
"""

from .routes import router

# Export the router for import in server.py
training_router = router

# Service metadata
SERVICE_INFO = {
    "name": "Training",
    "description": "Course and Training Management",
    "version": "1.0.0",
    "endpoints": {
        "courses": "/api/training/courses",
        "sessions": "/api/training/sessions",
        "progress": "/api/training/session/{id}/progress",
        "status": "/api/training/status"
    }
}