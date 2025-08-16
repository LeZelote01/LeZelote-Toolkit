#!/usr/bin/env python3
"""
Utilitaire pour gérer les imports dans le projet LeZelote-Toolkit
================================================================

Fonction pour fixer les chemins d'imports et permettre l'utilisation
des modules sans problèmes d'imports relatifs.
"""

import sys
import os
from pathlib import Path

def fix_imports():
    """Ajouter le répertoire racine du projet au sys.path"""
    # Obtenir le répertoire racine du projet
    current_file = Path(__file__)
    project_root = current_file.parent
    
    # Ajouter au sys.path si pas déjà présent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    return project_root

# Auto-fix lors de l'import
fix_imports()