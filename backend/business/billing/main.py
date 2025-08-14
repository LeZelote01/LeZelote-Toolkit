# Billing Service Main Module
"""
Billing Service for CyberSec Toolkit Pro 2025
Manages invoices with PDF generation capabilities
"""

from .routes import router

# Export the router for import in server.py
billing_router = router

# Service metadata
SERVICE_INFO = {
    "name": "Billing",
    "description": "Invoice and Payment Management",
    "version": "1.0.0",
    "endpoints": {
        "invoices": "/api/billing/invoices",
        "pdf_generation": "/api/billing/invoice/{id}/pdf",
        "status": "/api/billing/status"
    }
}