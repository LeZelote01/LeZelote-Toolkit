"""
Utilitaires pour Code Analysis AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Fonctions d'aide pour l'analyse de code
"""
import re
import ast
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

def calculate_cyclomatic_complexity(code: str, language: str) -> float:
    """Calcule la complexité cyclomatique du code"""
    if language == "python":
        return _calculate_python_complexity(code)
    elif language in ["javascript", "typescript"]:
        return _calculate_js_complexity(code)
    else:
        # Approximation basique pour autres langages
        return _calculate_generic_complexity(code)

def _calculate_python_complexity(code: str) -> float:
    """Complexité cyclomatique pour Python"""
    try:
        tree = ast.parse(code)
        complexity = 1  # Base complexity
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1
            
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_ExceptHandler(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_BoolOp(self, node):
                # AND/OR operators add complexity
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return float(visitor.complexity)
        
    except SyntaxError:
        return 1.0  # Default pour code invalide

def _calculate_js_complexity(code: str) -> float:
    """Complexité cyclomatique approximative pour JavaScript"""
    complexity = 1
    
    # Patterns pour JavaScript/TypeScript
    patterns = [
        r'\bif\s*\(',
        r'\belse\s*if\s*\(',
        r'\bwhile\s*\(',
        r'\bfor\s*\(',
        r'\bswitch\s*\(',
        r'\bcase\s+',
        r'\bcatch\s*\(',
        r'\&\&',
        r'\|\|',
        r'\?.*:'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)
        complexity += len(matches)
    
    return float(complexity)

def _calculate_generic_complexity(code: str) -> float:
    """Complexité approximative générique"""
    complexity = 1
    
    # Patterns génériques pour structures de contrôle
    control_patterns = [
        r'\bif\b', r'\belse\b', r'\bwhile\b', r'\bfor\b',
        r'\bswitch\b', r'\bcase\b', r'\btry\b', r'\bcatch\b'
    ]
    
    for pattern in control_patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)
        complexity += len(matches)
    
    return float(complexity)

def calculate_maintainability_index(loc: int, complexity: float, halstead_volume: float = None) -> float:
    """Calcule l'index de maintenabilité"""
    if halstead_volume is None:
        # Estimation basique si pas de volume Halstead
        halstead_volume = max(loc * 4.7, 1)  # Approximation
    
    # Formule standard de maintenabilité
    try:
        mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * complexity - 16.2 * math.log(loc)
        return max(0, min(100, mi))  # Normalise entre 0-100
    except:
        return 50.0  # Valeur par défaut

def extract_functions_and_classes(code: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extrait les fonctions et classes du code"""
    if language == "python":
        return _extract_python_structures(code)
    elif language in ["javascript", "typescript"]:
        return _extract_js_structures(code)
    else:
        return {"functions": [], "classes": []}

def _extract_python_structures(code: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extrait structures Python"""
    functions = []
    classes = []
    
    try:
        tree = ast.parse(code)
        
        class StructureVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                functions.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "args_count": len(node.args.args),
                    "docstring": ast.get_docstring(node)
                })
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node):
                functions.append({
                    "name": node.name + " (async)",
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "args_count": len(node.args.args),
                    "docstring": ast.get_docstring(node)
                })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                classes.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                    "docstring": ast.get_docstring(node)
                })
                self.generic_visit(node)
        
        visitor = StructureVisitor()
        visitor.visit(tree)
        
    except SyntaxError:
        pass  # Code invalide, retourner listes vides
    
    return {"functions": functions, "classes": classes}

def _extract_js_structures(code: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extrait structures JavaScript (approximatif)"""
    functions = []
    classes = []
    
    # Patterns pour fonctions JavaScript
    function_patterns = [
        r'function\s+(\w+)\s*\([^)]*\)\s*{',
        r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{',
        r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
        r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
        r'var\s+(\w+)\s*=\s*function\s*\([^)]*\)\s*{'
    ]
    
    # Patterns pour classes JavaScript
    class_patterns = [
        r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
    ]
    
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Recherche de fonctions
        for pattern in function_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                functions.append({
                    "name": match.group(1),
                    "line_start": line_num,
                    "line_end": line_num,  # Approximation
                    "type": "function"
                })
        
        # Recherche de classes
        for pattern in class_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                classes.append({
                    "name": match.group(1),
                    "line_start": line_num,
                    "line_end": line_num,  # Approximation
                    "extends": match.group(2) if match.lastindex > 1 else None
                })
    
    return {"functions": functions, "classes": classes}

def calculate_code_duplication(code: str) -> float:
    """Calcule le pourcentage de duplication approximatif"""
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    if len(lines) < 10:
        return 0.0
    
    # Recherche de séquences dupliquées de 3+ lignes
    duplicated_lines = set()
    
    for i in range(len(lines) - 2):
        sequence = '\n'.join(lines[i:i+3])
        sequence_hash = hashlib.md5(sequence.encode()).hexdigest()
        
        for j in range(i + 3, len(lines) - 2):
            compare_sequence = '\n'.join(lines[j:j+3])
            compare_hash = hashlib.md5(compare_sequence.encode()).hexdigest()
            
            if sequence_hash == compare_hash:
                # Trouvé une duplication
                duplicated_lines.update(range(i, i+3))
                duplicated_lines.update(range(j, j+3))
    
    duplication_percentage = (len(duplicated_lines) / len(lines)) * 100
    return min(duplication_percentage, 100.0)

def detect_security_patterns(code: str, language: str, custom_patterns: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Détecte les patterns de sécurité dans le code"""
    detected_patterns = []
    
    # Patterns de base par langage (déjà définis dans main.py)
    base_patterns = {
        "python": [
            {"pattern": r"eval\s*\(", "type": "code_injection", "severity": "critical"},
            {"pattern": r"exec\s*\(", "type": "code_injection", "severity": "critical"},
            {"pattern": r"subprocess\.call\s*\([^)]*shell\s*=\s*True", "type": "command_injection", "severity": "high"},
        ],
        "javascript": [
            {"pattern": r"eval\s*\(", "type": "code_injection", "severity": "critical"},
            {"pattern": r"innerHTML\s*=", "type": "xss", "severity": "high"},
            {"pattern": r"document\.write\s*\(", "type": "xss", "severity": "high"},
        ]
    }
    
    patterns_to_check = base_patterns.get(language, [])
    if custom_patterns:
        patterns_to_check.extend(custom_patterns)
    
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for pattern_info in patterns_to_check:
            matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
            
            for match in matches:
                detected_patterns.append({
                    "pattern": pattern_info["pattern"],
                    "type": pattern_info["type"],
                    "severity": pattern_info["severity"],
                    "line": line_num,
                    "column": match.start() + 1,
                    "matched_text": match.group(),
                    "full_line": line.strip()
                })
    
    return detected_patterns

def generate_code_hash(code: str) -> str:
    """Génère un hash unique pour le code"""
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def normalize_code_for_analysis(code: str, language: str) -> str:
    """Normalise le code pour l'analyse"""
    # Suppression des commentaires et espaces superflus
    if language == "python":
        return _normalize_python_code(code)
    elif language in ["javascript", "typescript"]:
        return _normalize_js_code(code)
    else:
        return code.strip()

def _normalize_python_code(code: str) -> str:
    """Normalise le code Python"""
    lines = []
    for line in code.split('\n'):
        # Supprime les commentaires Python
        line = re.sub(r'#.*$', '', line)
        # Supprime les espaces en fin de ligne
        line = line.rstrip()
        if line:  # Ne garde que les lignes non vides
            lines.append(line)
    return '\n'.join(lines)

def _normalize_js_code(code: str) -> str:
    """Normalise le code JavaScript"""
    # Supprime les commentaires // et /* */
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    lines = []
    for line in code.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    
    return '\n'.join(lines)

def extract_dependencies_from_code(code: str, language: str) -> List[str]:
    """Extrait les dépendances du code"""
    dependencies = []
    
    if language == "python":
        # Patterns pour imports Python
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code)
            dependencies.extend(matches)
    
    elif language in ["javascript", "typescript"]:
        # Patterns pour imports/requires JavaScript
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code)
            dependencies.extend(matches)
    
    elif language == "java":
        # Patterns pour imports Java
        import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        matches = re.findall(import_pattern, code)
        dependencies.extend(matches)
    
    # Supprime les doublons et retourne
    return list(set(dependencies))

def estimate_performance_impact(code: str, language: str) -> Dict[str, Any]:
    """Estime l'impact performance du code"""
    impact = {
        "potential_bottlenecks": [],
        "memory_issues": [],
        "optimization_opportunities": []
    }
    
    lines = code.split('\n')
    
    # Patterns problématiques communs
    bottleneck_patterns = {
        "nested_loops": r'for\s+.*:\s*\n\s*for\s+.*:',
        "inefficient_search": r'in\s+.*\[.*\]',  # Recherche linéaire dans liste
        "string_concatenation": r'\+\=\s*[\'"].*[\'"]'  # Concaténation de strings
    }
    
    for line_num, line in enumerate(lines, 1):
        for issue_type, pattern in bottleneck_patterns.items():
            if re.search(pattern, line):
                impact["potential_bottlenecks"].append({
                    "type": issue_type,
                    "line": line_num,
                    "suggestion": _get_performance_suggestion(issue_type)
                })
    
    return impact

def _get_performance_suggestion(issue_type: str) -> str:
    """Retourne une suggestion d'optimisation"""
    suggestions = {
        "nested_loops": "Considérer l'optimisation algorithmique ou la vectorisation",
        "inefficient_search": "Utiliser des structures de données optimisées (set, dict)",
        "string_concatenation": "Utiliser join() ou f-strings pour de meilleures performances"
    }
    return suggestions.get(issue_type, "Optimisation recommandée")

# Import pour math (utilisé dans calculate_maintainability_index)
import math