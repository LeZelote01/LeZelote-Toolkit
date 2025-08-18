#!/usr/bin/env python3
"""
Script pour corriger les imports relatifs dans les modules.
"""

import os
import re

def fix_relative_imports(file_path):
    """Corrige les imports relatifs dans un fichier."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour détecter les imports relatifs de type "from ...core"
    pattern = r'from \.\.\.core\.'
    
    if re.search(pattern, content):
        print(f"Correction des imports dans {file_path}")
        
        # Ajouter les imports système si pas déjà présents
        if 'import sys' not in content or 'import os' not in content:
            # Trouver la première ligne d'import
            lines = content.split('\n')
            first_import_idx = -1
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    first_import_idx = i
                    break
            
            if first_import_idx > -1:
                # Insérer les imports système
                sys_imports = [
                    'import sys',
                    'import os',
                    '',
                    '# Add the project root to Python path',
                    'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))',
                    ''
                ]
                
                # Insérer avant le premier import existant
                for j, sys_import in enumerate(sys_imports):
                    lines.insert(first_import_idx + j, sys_import)
        
        # Remplacer tous les imports relatifs
        content = '\n'.join(lines)
        content = re.sub(r'from \.\.\.core\.', 'from core.', content)
        
        # Écrire le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def main():
    """Parcourt tous les fichiers .py dans les modules et corrige les imports."""
    modules_dir = '/app/modules'
    fixed_count = 0
    
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(root, file)
                if fix_relative_imports(file_path):
                    fixed_count += 1
    
    print(f"✅ {fixed_count} fichiers corrigés")

if __name__ == "__main__":
    main()