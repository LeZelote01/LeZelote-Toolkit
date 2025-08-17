#!/usr/bin/env python3
"""
LeZelote-Toolkit - Configuration FINALE et COMPLÈTE de TOUS les Outils
Étape 4.3 - Intégration des Outils et Binaires - TERMINÉE
Total: 390 outils configurés (Objectif: 390) ✅

GÉNÉRÉE AUTOMATIQUEMENT - Configuration consolidée
"""

# Import from consolidated configuration
from .tools_config_consolidated import (
    TOOLS_CONFIG_390 as COMPLETE_TOOLS_CONFIG,
    get_tools_by_category,
    get_all_categories,
    get_priority_tools,
    get_total_tool_count,
    get_license_info,
    has_license_upgrade
)

# Keep backward compatibility
__all__ = [
    "COMPLETE_TOOLS_CONFIG",
    "get_tools_by_category",
    "get_all_categories", 
    "get_priority_tools",
    "get_total_tool_count",
    "get_license_info",
    "has_license_upgrade"
]
