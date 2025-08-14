# Analytics Service Main Module
"""
Analytics Service for CyberSec Toolkit Pro 2025
Provides business intelligence and metrics
"""

from .routes import router

# Export the router for import in server.py
analytics_router = router

# Service metadata
SERVICE_INFO = {
    "name": "Analytics",
    "description": "Business Intelligence and Metrics",
    "version": "1.0.0",
    "endpoints": {
        "metrics": "/api/analytics/metrics",
        "daily_metrics": "/api/analytics/metrics/daily",
        "status": "/api/analytics/status"
    }
}