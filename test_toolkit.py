#!/usr/bin/env python3
"""
Test script pour analyser l'état du toolkit LeZelote
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test des imports principaux"""
    print("=== TEST DES IMPORTS ===")
    
    try:
        from core.engine.orchestrator import PentestOrchestrator
        print("✅ Core orchestrator importé")
    except ImportError as e:
        print(f"❌ Erreur orchestrator: {e}")
    
    try:
        from core.utils.logging_handler import get_logger
        print("✅ Logging handler importé")
    except ImportError as e:
        print(f"❌ Erreur logging: {e}")
    
    try:
        from interfaces.cli.dashboard import Dashboard
        print("✅ Dashboard importé")
    except ImportError as e:
        print(f"❌ Erreur dashboard: {e}")

def analyze_structure():
    """Analyser la structure du projet"""
    print("\n=== ANALYSE DE LA STRUCTURE ===")
    
    directories = [
        "core", "modules", "interfaces", "tools", "data",
        "config", "logs", "outputs", "reports", "runtime",
        "scripts", "tests", "docs"
    ]
    
    for directory in directories:
        path = project_root / directory
        if path.exists():
            py_files = list(path.rglob("*.py"))
            yaml_files = list(path.rglob("*.yaml")) + list(path.rglob("*.yml"))
            print(f"✅ {directory:12} | {len(py_files):3} fichiers .py | {len(yaml_files):2} fichiers YAML")
        else:
            print(f"❌ {directory:12} | MANQUANT")

def count_files():
    """Compter les fichiers du projet"""
    print("\n=== COMPTAGE DES FICHIERS ===")
    
    py_files = list(project_root.rglob("*.py"))
    yaml_files = list(project_root.rglob("*.yaml")) + list(project_root.rglob("*.yml"))
    md_files = list(project_root.rglob("*.md"))
    
    print(f"Fichiers Python (.py): {len(py_files)}")
    print(f"Fichiers YAML: {len(yaml_files)}")
    print(f"Fichiers Markdown (.md): {len(md_files)}")
    print(f"Total fichiers analysés: {len(py_files) + len(yaml_files) + len(md_files)}")

if __name__ == "__main__":
    print("🔍 ANALYSE DU TOOLKIT LEZELOTE")
    print("=" * 50)
    
    analyze_structure()
    count_files()
    test_imports()