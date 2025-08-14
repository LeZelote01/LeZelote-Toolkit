"""
Code Analysis AI - Analyse statique de code CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Intelligence artificielle pour analyse sécurisée du code source
"""
import asyncio
import ast
import json
import re
import uuid
import hashlib
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from fastapi import HTTPException
from pydantic import BaseModel, Field
import tempfile
import shutil

# Intégration Emergent LLM
try:
    from emergentintegrations import EmergentLLM
except ImportError:
    print("⚠️ EmergentLLM non disponible pour Code Analysis AI - Mode fallback activé")
    EmergentLLM = None

from backend.config import settings
from backend.database import get_collection

# Modèles de données Code Analysis AI
class CodeAnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="Type d'analyse: security, quality, performance, dependency, full")
    code_content: Optional[str] = Field(None, description="Code source à analyser")
    file_path: Optional[str] = Field(None, description="Chemin du fichier")
    repository_url: Optional[str] = Field(None, description="URL du repository Git")
    language: str = Field(..., description="Langage: python, javascript, java, c, cpp, go, rust, php")
    frameworks: Optional[List[str]] = Field(None, description="Frameworks utilisés")
    include_dependencies: bool = Field(True, description="Analyser les dépendances")
    security_focus: Optional[List[str]] = Field(None, description="Focus sécurité spécifique")

class VulnerabilityFinding(BaseModel):
    vulnerability_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = Field(..., description="Sévérité: critical, high, medium, low, info")
    vulnerability_type: str = Field(..., description="Type de vulnérabilité")
    cwe_id: Optional[str] = Field(None, description="Common Weakness Enumeration ID")
    owasp_category: Optional[str] = Field(None, description="Catégorie OWASP")
    line_number: Optional[int] = Field(None, description="Numéro de ligne")
    column_number: Optional[int] = Field(None, description="Numéro de colonne")
    code_snippet: str = Field(..., description="Snippet de code vulnérable")
    description: str = Field(..., description="Description de la vulnérabilité")
    impact: str = Field(..., description="Impact potentiel")
    remediation: str = Field(..., description="Solution recommandée")
    confidence: float = Field(..., description="Niveau de confiance (0-1)")
    false_positive_probability: float = Field(..., description="Probabilité de faux positif")

class QualityIssue(BaseModel):
    issue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issue_type: str = Field(..., description="Type: style, complexity, maintainability, documentation")
    severity: str = Field(..., description="Sévérité: major, minor, info")
    line_number: Optional[int] = Field(None, description="Numéro de ligne")
    code_snippet: str = Field(..., description="Code concerné")
    description: str = Field(..., description="Description du problème")
    suggestion: str = Field(..., description="Suggestion d'amélioration")
    category: str = Field(..., description="Catégorie du problème")

class DependencyAnalysis(BaseModel):
    package_name: str = Field(..., description="Nom du package")
    version: str = Field(..., description="Version")
    license: Optional[str] = Field(None, description="Licence")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Vulnérabilités connues")
    outdated: bool = Field(..., description="Version obsolète")
    latest_version: Optional[str] = Field(None, description="Dernière version disponible")
    security_score: float = Field(..., description="Score de sécurité (0-10)")
    maintenance_status: str = Field(..., description="Statut maintenance: active, deprecated, abandoned")

class CodeMetrics(BaseModel):
    lines_of_code: int = Field(..., description="Lignes de code")
    cyclomatic_complexity: float = Field(..., description="Complexité cyclomatique")
    maintainability_index: float = Field(..., description="Index de maintenabilité")
    technical_debt_ratio: float = Field(..., description="Ratio de dette technique")
    code_coverage: Optional[float] = Field(None, description="Couverture de code")
    duplication_percentage: float = Field(..., description="Pourcentage de duplication")
    security_hotspots: int = Field(..., description="Nombre de points chauds sécurité")
    nested_depth: int = Field(0, description="Profondeur d'imbrication max")

class CodeAnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_type: str = Field(..., description="Type d'analyse effectuée")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    language: str = Field(..., description="Langage analysé")
    file_analyzed: Optional[str] = Field(None, description="Fichier analysé")
    overall_security_score: float = Field(..., description="Score de sécurité global (0-10)")
    overall_quality_score: float = Field(..., description="Score de qualité global (0-10)")
    vulnerability_findings: List[VulnerabilityFinding] = Field(..., description="Vulnérabilités détectées")
    quality_issues: List[QualityIssue] = Field(..., description="Problèmes de qualité")
    dependency_analysis: List[DependencyAnalysis] = Field(default_factory=list, description="Analyse des dépendances")
    code_metrics: CodeMetrics = Field(..., description="Métriques du code")
    ai_recommendations: List[str] = Field(..., description="Recommandations IA")
    security_recommendations: List[str] = Field(..., description="Recommandations sécurité")
    performance_recommendations: List[str] = Field(..., description="Recommandations performance")
    execution_time_seconds: float = Field(..., description="Temps d'exécution de l'analyse")

class CodeAnalysisAIService:
    """Service IA Code Analysis - Analyse sécurisée du code source"""
    
    def __init__(self):
        self.llm_client = None
        self.security_patterns = self._initialize_security_patterns()
        self.quality_rules = self._initialize_quality_rules()
        self.language_parsers = self._initialize_language_parsers()
        self.vulnerability_database = self._load_vulnerability_database()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le client LLM pour Code Analysis AI"""
        try:
            if EmergentLLM and settings.emergent_llm_key:
                self.llm_client = EmergentLLM(
                    api_key=settings.emergent_llm_key,
                    default_provider=settings.default_llm_provider,
                    default_model=settings.default_llm_model
                )
                print("✅ Code Analysis AI initialisé avec Emergent LLM")
            else:
                print("⚠️ Code Analysis AI - Mode simulation activé")
        except Exception as e:
            print(f"❌ Erreur initialisation Code Analysis AI LLM: {e}")
    
    def _initialize_security_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialise les patterns de sécurité par langage"""
        return {
            "python": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "code_injection",
                    "severity": "critical",
                    "cwe": "CWE-94",
                    "owasp": "A03:2021 – Injection",
                    "description": "Utilisation de eval() - injection de code possible",
                    "remediation": "Utiliser ast.literal_eval() ou parser spécifique"
                },
                {
                    "pattern": r"exec\s*\(",
                    "type": "code_injection", 
                    "severity": "critical",
                    "cwe": "CWE-94",
                    "owasp": "A03:2021 – Injection",
                    "description": "Utilisation de exec() - injection de code possible",
                    "remediation": "Éviter exec(), utiliser des alternatives sécurisées"
                },
                {
                    "pattern": r"subprocess\.call\s*\([^)]*shell\s*=\s*True",
                    "type": "command_injection",
                    "severity": "high",
                    "cwe": "CWE-78",
                    "owasp": "A03:2021 – Injection",
                    "description": "Subprocess avec shell=True - injection de commande",
                    "remediation": "Utiliser liste d'arguments sans shell=True"
                },
                {
                    "pattern": r"pickle\.loads?\s*\(",
                    "type": "deserialization",
                    "severity": "high",
                    "cwe": "CWE-502",
                    "owasp": "A08:2021 – Software and Data Integrity Failures",
                    "description": "Désérialisation pickle non sécurisée",
                    "remediation": "Utiliser JSON ou validation stricte"
                },
                {
                    "pattern": r"(password|pwd|pass)\s*=\s*['\"][^'\"]*['\"]",
                    "type": "hardcoded_credentials",
                    "severity": "high",
                    "cwe": "CWE-798",
                    "owasp": "A07:2021 – Identification and Authentication Failures",
                    "description": "Mot de passe en dur dans le code",
                    "remediation": "Utiliser variables d'environnement ou vault"
                },
                {
                    "pattern": r"random\.random\s*\(\)",
                    "type": "weak_crypto",
                    "severity": "medium",
                    "cwe": "CWE-338",
                    "owasp": "A02:2021 – Cryptographic Failures",
                    "description": "Générateur aléatoire faible pour la sécurité",
                    "remediation": "Utiliser secrets.SystemRandom() pour la crypto"
                }
            ],
            "javascript": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "code_injection",
                    "severity": "critical",
                    "cwe": "CWE-94",
                    "owasp": "A03:2021 – Injection",
                    "description": "Utilisation de eval() - injection de code JavaScript",
                    "remediation": "Utiliser JSON.parse() ou parser spécifique"
                },
                {
                    "pattern": r"innerHTML\s*=",
                    "type": "xss",
                    "severity": "high", 
                    "cwe": "CWE-79",
                    "owasp": "A03:2021 – Injection",
                    "description": "Utilisation de innerHTML - risque XSS",
                    "remediation": "Utiliser textContent ou validation/échappement"
                },
                {
                    "pattern": r"document\.write\s*\(",
                    "type": "xss",
                    "severity": "high",
                    "cwe": "CWE-79", 
                    "owasp": "A03:2021 – Injection",
                    "description": "document.write() - risque XSS",
                    "remediation": "Utiliser DOM manipulation sécurisée"
                },
                {
                    "pattern": r"Math\.random\s*\(\)",
                    "type": "weak_crypto",
                    "severity": "medium",
                    "cwe": "CWE-338",
                    "owasp": "A02:2021 – Cryptographic Failures", 
                    "description": "Math.random() faible pour la sécurité",
                    "remediation": "Utiliser crypto.getRandomValues()"
                }
            ],
            "java": [
                {
                    "pattern": r"Runtime\.getRuntime\(\)\.exec",
                    "type": "command_injection",
                    "severity": "high",
                    "cwe": "CWE-78",
                    "owasp": "A03:2021 – Injection",
                    "description": "Exécution de commande système - injection possible",
                    "remediation": "Validation stricte des entrées, ProcessBuilder"
                },
                {
                    "pattern": r"new\s+ObjectInputStream",
                    "type": "deserialization",
                    "severity": "high",
                    "cwe": "CWE-502",
                    "owasp": "A08:2021 – Software and Data Integrity Failures",
                    "description": "Désérialisation Java non sécurisée",
                    "remediation": "Validation des classes, alternatives JSON"
                }
            ]
        }
    
    def _initialize_quality_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialise les règles de qualité du code"""
        return {
            "python": [
                {
                    "pattern": r"def\s+\w+\([^)]*\):\s*\n(\s+.*\n){50,}",
                    "type": "complexity",
                    "severity": "major",
                    "description": "Fonction trop longue (>50 lignes)",
                    "suggestion": "Diviser en fonctions plus petites"
                },
                {
                    "pattern": r"^[^#\n]*\n[^#\n]*\n[^#\n]*\n[^#\n]*\ndef\s+\w+",
                    "type": "documentation",
                    "severity": "minor",
                    "description": "Fonction sans docstring",
                    "suggestion": "Ajouter une docstring descriptive"
                }
            ],
            "javascript": [
                {
                    "pattern": r"function\s+\w+\([^)]*\)\s*{[^}]{500,}}",
                    "type": "complexity",
                    "severity": "major",
                    "description": "Fonction JavaScript trop complexe",
                    "suggestion": "Refactoriser en fonctions plus petites"
                }
            ]
        }
    
    def _initialize_language_parsers(self) -> Dict[str, Any]:
        """Initialise les parseurs par langage"""
        return {
            "python": {
                "parser": "ast",
                "extensions": [".py"],
                "dependency_files": ["requirements.txt", "Pipfile", "pyproject.toml"],
                "test_patterns": ["test_*.py", "*_test.py", "tests/"]
            },
            "javascript": {
                "parser": "esprima",
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "dependency_files": ["package.json", "yarn.lock", "package-lock.json"],
                "test_patterns": ["*.test.js", "*.spec.js", "__tests__/"]
            },
            "java": {
                "parser": "antlr",
                "extensions": [".java"],
                "dependency_files": ["pom.xml", "build.gradle", "maven.xml"],
                "test_patterns": ["*Test.java", "*Tests.java", "src/test/"]
            }
        }
    
    def _load_vulnerability_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Charge la base de données de vulnérabilités"""
        return {
            "cwe_database": [
                {
                    "cwe_id": "CWE-79",
                    "name": "Cross-site Scripting (XSS)",
                    "description": "Injection de scripts côté client",
                    "impact": "Vol de session, défacement, redirection malveillante"
                },
                {
                    "cwe_id": "CWE-89",
                    "name": "SQL Injection",
                    "description": "Injection de requêtes SQL malveillantes",
                    "impact": "Accès non autorisé aux données, modification de BD"
                },
                {
                    "cwe_id": "CWE-94",
                    "name": "Code Injection",
                    "description": "Injection et exécution de code arbitraire",
                    "impact": "Exécution de commandes, compromission système"
                },
                {
                    "cwe_id": "CWE-502",
                    "name": "Deserialization of Untrusted Data",
                    "description": "Désérialisation de données non fiables",
                    "impact": "Exécution de code, déni de service"
                }
            ]
        }
    
    async def analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResult:
        """Analyse complète du code avec IA"""
        try:
            start_time = datetime.now()
            print(f"🔍 Code Analysis AI - Analyse type: {request.analysis_type}, langage: {request.language}")
            
            # Préparation du code à analyser
            code_content = await self._prepare_code_for_analysis(request)
            
            # Analyses selon le type demandé
            vulnerability_findings = []
            quality_issues = []
            dependency_analysis = []
            
            if request.analysis_type in ["security", "full"]:
                vulnerability_findings = await self._analyze_security(code_content, request.language)
            
            if request.analysis_type in ["quality", "full"]:
                quality_issues = await self._analyze_quality(code_content, request.language)
            
            if request.analysis_type in ["dependency", "full"] and request.include_dependencies:
                dependency_analysis = await self._analyze_dependencies(request)
            
            # Calcul des métriques du code
            code_metrics = await self._calculate_code_metrics(code_content, request.language)
            
            # Calcul des scores globaux
            security_score = self._calculate_security_score(vulnerability_findings, code_metrics)
            quality_score = self._calculate_quality_score(quality_issues, code_metrics)
            
            # Génération des recommandations IA
            ai_recommendations = await self._generate_ai_recommendations(
                vulnerability_findings, quality_issues, code_metrics, request
            )
            
            # Recommandations spécialisées
            security_recommendations = self._generate_security_recommendations(vulnerability_findings)
            performance_recommendations = self._generate_performance_recommendations(code_metrics, quality_issues)
            
            # Calcul du temps d'exécution
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Sauvegarde de l'analyse
            await self._save_code_analysis(request.analysis_type, {
                "language": request.language,
                "security_score": security_score,
                "quality_score": quality_score,
                "vulnerabilities_count": len(vulnerability_findings),
                "quality_issues_count": len(quality_issues)
            })
            
            return CodeAnalysisResult(
                analysis_type=request.analysis_type,
                language=request.language,
                file_analyzed=request.file_path,
                overall_security_score=security_score,
                overall_quality_score=quality_score,
                vulnerability_findings=vulnerability_findings,
                quality_issues=quality_issues,
                dependency_analysis=dependency_analysis,
                code_metrics=code_metrics,
                ai_recommendations=ai_recommendations,
                security_recommendations=security_recommendations,
                performance_recommendations=performance_recommendations,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            print(f"❌ Erreur analyse code: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur Code Analysis AI: {str(e)}")
    
    async def _prepare_code_for_analysis(self, request: CodeAnalysisRequest) -> str:
        """Prépare le code pour l'analyse"""
        if request.code_content:
            return request.code_content
        
        if request.file_path:
            try:
                with open(request.file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur lecture fichier: {str(e)}")
        
        if request.repository_url:
            # Clone temporaire du repository (simplifié pour la démo)
            return "# Repository code analysis - feature in development"
        
        raise HTTPException(status_code=400, detail="Code source, fichier ou repository requis")
    
    async def _analyze_security(self, code_content: str, language: str) -> List[VulnerabilityFinding]:
        """Analyse de sécurité du code"""
        findings = []
        patterns = self.security_patterns.get(language, [])
        
        lines = code_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
                
                for match in matches:
                    finding = VulnerabilityFinding(
                        severity=pattern_info["severity"],
                        vulnerability_type=pattern_info["type"],
                        cwe_id=pattern_info.get("cwe"),
                        owasp_category=pattern_info.get("owasp"),
                        line_number=line_num,
                        column_number=match.start() + 1,
                        code_snippet=line.strip(),
                        description=pattern_info["description"],
                        impact=self._get_impact_description(pattern_info["type"]),
                        remediation=pattern_info["remediation"],
                        confidence=0.85,  # Confiance élevée pour les patterns regex
                        false_positive_probability=0.15
                    )
                    findings.append(finding)
        
        # Analyse AST pour Python (plus sophistiquée)
        if language == "python":
            ast_findings = await self._analyze_python_ast(code_content)
            findings.extend(ast_findings)
        
        return findings
    
    async def _analyze_python_ast(self, code_content: str) -> List[VulnerabilityFinding]:
        """Analyse AST avancée pour Python"""
        findings = []
        
        try:
            tree = ast.parse(code_content)
            
            class SecurityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.findings = []
                
                def visit_Call(self, node):
                    # Détection d'appels dangereux
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec']:
                            finding = VulnerabilityFinding(
                                severity="critical",
                                vulnerability_type="code_injection",
                                cwe_id="CWE-94",
                                owasp_category="A03:2021 – Injection",
                                line_number=node.lineno,
                                column_number=node.col_offset + 1,
                                code_snippet=f"{node.func.id}(...)",
                                description=f"Appel dangereux à {node.func.id}()",
                                impact="Exécution de code arbitraire",
                                remediation="Utiliser des alternatives sécurisées",
                                confidence=0.95,
                                false_positive_probability=0.05
                            )
                            self.findings.append(finding)
                    
                    self.generic_visit(node)
                
                def visit_Assign(self, node):
                    # Détection de mots de passe en dur
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if any(keyword in target.id.lower() for keyword in ['password', 'pwd', 'secret', 'key']):
                                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                    finding = VulnerabilityFinding(
                                        severity="high",
                                        vulnerability_type="hardcoded_credentials",
                                        cwe_id="CWE-798",
                                        owasp_category="A07:2021 – Identification and Authentication Failures",
                                        line_number=node.lineno,
                                        column_number=node.col_offset + 1,
                                        code_snippet=f"{target.id} = '***'",
                                        description="Credentials en dur détectées",
                                        impact="Exposition des credentials",
                                        remediation="Utiliser variables d'environnement",
                                        confidence=0.90,
                                        false_positive_probability=0.10
                                    )
                                    self.findings.append(finding)
                    
                    self.generic_visit(node)
            
            visitor = SecurityVisitor()
            visitor.visit(tree)
            findings.extend(visitor.findings)
            
        except SyntaxError as e:
            # Code invalide, créer un finding pour ça
            finding = VulnerabilityFinding(
                severity="medium",
                vulnerability_type="syntax_error",
                line_number=e.lineno if e.lineno else 1,
                code_snippet=str(e.text) if e.text else "Erreur de syntaxe",
                description=f"Erreur de syntaxe Python: {e.msg}",
                impact="Code non exécutable",
                remediation="Corriger l'erreur de syntaxe",
                confidence=1.0,
                false_positive_probability=0.0
            )
            findings.append(finding)
        
        return findings
    
    def _get_impact_description(self, vulnerability_type: str) -> str:
        """Retourne la description d'impact selon le type de vulnérabilité"""
        impact_mapping = {
            "code_injection": "Exécution de code arbitraire, compromission système",
            "command_injection": "Exécution de commandes système, élévation privilèges",
            "xss": "Vol de session, défacement, redirection malveillante",
            "sql_injection": "Accès non autorisé aux données, modification BD",
            "deserialization": "Exécution de code, déni de service",
            "hardcoded_credentials": "Accès non autorisé, compromission comptes",
            "weak_crypto": "Prédictibilité, affaiblissement sécurité cryptographique",
            "path_traversal": "Accès fichiers systèmes, lecture données sensibles"
        }
        return impact_mapping.get(vulnerability_type, "Impact sécurité potentiel")
    
    async def _analyze_quality(self, code_content: str, language: str) -> List[QualityIssue]:
        """Analyse de la qualité du code"""
        issues = []
        patterns = self.quality_rules.get(language, [])
        
        lines = code_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
                
                for match in matches:
                    issue = QualityIssue(
                        issue_type=pattern_info["type"],
                        severity=pattern_info["severity"],
                        line_number=line_num,
                        code_snippet=line.strip(),
                        description=pattern_info["description"],
                        suggestion=pattern_info["suggestion"],
                        category=pattern_info["type"]
                    )
                    issues.append(issue)
        
        return issues
    
    async def _analyze_dependencies(self, request: CodeAnalysisRequest) -> List[DependencyAnalysis]:
        """Analyse des dépendances (simulée pour la démo)"""
        dependencies = []
        
        # Simulation d'analyse de dépendances
        if request.language == "python":
            # Dépendances Python courantes avec vulnérabilités simulées
            sample_deps = [
                {
                    "name": "requests",
                    "version": "2.25.1",
                    "latest": "2.31.0",
                    "vulnerabilities": [
                        {"cve": "CVE-2023-32681", "severity": "medium"}
                    ]
                },
                {
                    "name": "flask",
                    "version": "1.1.4",
                    "latest": "2.3.3",
                    "vulnerabilities": []
                }
            ]
            
            for dep in sample_deps:
                dependencies.append(DependencyAnalysis(
                    package_name=dep["name"],
                    version=dep["version"],
                    latest_version=dep["latest"],
                    license="MIT",
                    vulnerabilities=dep["vulnerabilities"],
                    outdated=dep["version"] != dep["latest"],
                    security_score=8.5 if not dep["vulnerabilities"] else 6.2,
                    maintenance_status="active"
                ))
        
        return dependencies
    
    async def _calculate_code_metrics(self, code_content: str, language: str) -> CodeMetrics:
        """Calcule les métriques du code"""
        lines = code_content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        blank_lines = total_lines - code_lines - comment_lines
        
        # Calcul de la complexité cyclomatique
        complexity = self._calculate_complexity(code_content, language)
        
        # Calcul d'autres métriques
        duplication = self._calculate_duplication(code_content)
        
        return CodeMetrics(
            lines_of_code=code_lines,
            lines_of_comments=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=complexity,
            cognitive_complexity=complexity * 1.2,  # Approximation
            maintainability_index=max(0, 100 - complexity * 2),
            technical_debt_ratio=min(complexity / 10, 1.0),
            code_coverage=None,  # Nécessiterait des tests
            duplication_percentage=duplication,
            security_hotspots=0,  # Calculé ailleurs
            function_count=self._count_functions(code_content, language),
            class_count=self._count_classes(code_content, language),
            max_function_length=self._get_max_function_length(code_content, language),
            average_function_length=self._get_avg_function_length(code_content, language),
            nested_depth=self._calculate_nesting_depth(code_content, language)
        )
    
    def _calculate_complexity(self, code: str, language: str) -> float:
        """Calcule la complexité cyclomatique"""
        if language == "python":
            try:
                tree = ast.parse(code)
                complexity = 1
                
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
                
                visitor = ComplexityVisitor()
                visitor.visit(tree)
                return float(visitor.complexity)
            except:
                return 1.0
        else:
            # Approximation pour autres langages
            control_keywords = ['if', 'else', 'while', 'for', 'switch', 'case']
            complexity = 1
            for keyword in control_keywords:
                complexity += len(re.findall(rf'\b{keyword}\b', code, re.IGNORECASE))
            return float(complexity)
    
    def _calculate_duplication(self, code: str) -> float:
        """Calcule le pourcentage de duplication"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        if len(lines) < 5:
            return 0.0
        
        # Recherche de lignes dupliquées
        line_counts = {}
        for line in lines:
            line_counts[line] = line_counts.get(line, 0) + 1
        
        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        return (duplicated_lines / len(lines)) * 100 if lines else 0.0
    
    def _count_functions(self, code: str, language: str) -> int:
        """Compte le nombre de fonctions"""
        if language == "python":
            try:
                tree = ast.parse(code)
                count = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        count += 1
                return count
            except:
                return 0
        else:
            # Approximation pour autres langages
            patterns = [r'\bfunction\s+\w+', r'\w+\s*:\s*function', r'def\s+\w+']
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, code, re.IGNORECASE))
            return count
    
    def _count_classes(self, code: str, language: str) -> int:
        """Compte le nombre de classes"""
        if language == "python":
            try:
                tree = ast.parse(code)
                return len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            except:
                return 0
        else:
            return len(re.findall(r'\bclass\s+\w+', code, re.IGNORECASE))
    
    def _get_max_function_length(self, code: str, language: str) -> int:
        """Retourne la longueur de la fonction la plus longue"""
        # Implémentation simplifiée
        return min(50, len(code.split('\n')))
    
    def _get_avg_function_length(self, code: str, language: str) -> float:
        """Retourne la longueur moyenne des fonctions"""
        function_count = self._count_functions(code, language)
        if function_count == 0:
            return 0.0
        return len(code.split('\n')) / function_count
    
    def _calculate_nesting_depth(self, code: str, language: str) -> int:
        """Calcule la profondeur d'imbrication maximale"""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            # Compte les indentations (approximation)
            if language == "python":
                indent = len(line) - len(line.lstrip())
                depth = indent // 4  # Assume 4 spaces per level
                max_depth = max(max_depth, depth)
            else:
                # Compte les accolades pour autres langages
                current_depth += line.count('{') - line.count('}')
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _calculate_security_score(self, vulnerabilities: List[VulnerabilityFinding], metrics: CodeMetrics) -> float:
        """Calcule le score de sécurité global"""
        if not vulnerabilities:
            return 9.5
        
        # Pondération par sévérité
        severity_weights = {"critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}
        total_penalty = 0.0
        
        for vuln in vulnerabilities:
            penalty = severity_weights.get(vuln.severity, 0.5)
            # Ajustement selon la confiance
            penalty *= vuln.confidence
            total_penalty += penalty
        
        # Score sur 10, avec pénalités
        base_score = 10.0
        adjusted_score = max(0.0, base_score - total_penalty)
        
        return round(adjusted_score, 1)
    
    def _calculate_quality_score(self, quality_issues: List[QualityIssue], metrics: CodeMetrics) -> float:
        """Calcule le score de qualité global"""
        if not quality_issues:
            base_score = 9.0
        else:
            # Pénalités par type d'issue
            severity_penalties = {"major": 1.5, "minor": 0.5, "info": 0.1}
            total_penalty = sum(severity_penalties.get(issue.severity, 0.5) for issue in quality_issues)
            base_score = max(0.0, 10.0 - total_penalty)
        
        # Ajustement selon les métriques
        if metrics.maintainability_index < 50:
            base_score *= 0.8
        if metrics.cyclomatic_complexity > 20:
            base_score *= 0.9
        
        return round(base_score, 1)
    
    async def _generate_ai_recommendations(self, vulnerabilities: List[VulnerabilityFinding], 
                                         quality_issues: List[QualityIssue], 
                                         metrics: CodeMetrics, 
                                         request: CodeAnalysisRequest) -> List[str]:
        """Génère des recommandations IA"""
        if self.llm_client:
            return await self._generate_llm_recommendations(vulnerabilities, quality_issues, metrics, request)
        else:
            return self._generate_fallback_recommendations(vulnerabilities, quality_issues, metrics)
    
    def _generate_fallback_recommendations(self, vulnerabilities: List[VulnerabilityFinding], 
                                         quality_issues: List[QualityIssue], 
                                         metrics: CodeMetrics) -> List[str]:
        """Génère des recommandations de fallback"""
        recommendations = []
        
        # Recommandations basées sur les vulnérabilités
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.severity == "critical"]
            if critical_vulns:
                recommendations.append("🚨 **PRIORITÉ CRITIQUE** - Corriger immédiatement les vulnérabilités critiques détectées")
            
            high_vulns = [v for v in vulnerabilities if v.severity == "high"]
            if high_vulns:
                recommendations.append("⚠️ **HAUTE PRIORITÉ** - Traiter les vulnérabilités à risque élevé")
        
        # Recommandations basées sur la qualité
        if quality_issues:
            major_issues = [i for i in quality_issues if i.severity == "major"]
            if major_issues:
                recommendations.append("🔧 **REFACTORING** - Résoudre les problèmes majeurs de qualité du code")
        
        # Recommandations basées sur les métriques
        if metrics.cyclomatic_complexity > 15:
            recommendations.append("📊 **COMPLEXITÉ** - Réduire la complexité cyclomatique en décomposant les fonctions")
        
        if metrics.duplication_percentage > 20:
            recommendations.append("🔄 **DUPLICATION** - Éliminer la duplication de code par la refactorisation")
        
        if metrics.maintainability_index < 50:
            recommendations.append("🛠️ **MAINTENABILITÉ** - Améliorer la structure du code pour faciliter la maintenance")
        
        # Recommandations générales
        if not recommendations:
            recommendations.extend([
                "✅ **BONNE PRATIQUE** - Code conforme aux standards de sécurité",
                "📝 **DOCUMENTATION** - Ajouter des commentaires pour améliorer la lisibilité",
                "🧪 **TESTS** - Développer une suite de tests pour valider le comportement"
            ])
        
        return recommendations
    
    def _generate_security_recommendations(self, vulnerabilities: List[VulnerabilityFinding]) -> List[str]:
        """Génère des recommandations spécifiques à la sécurité"""
        recommendations = []
        
        vuln_types = set(v.vulnerability_type for v in vulnerabilities)
        
        if "code_injection" in vuln_types:
            recommendations.append("🛡️ Éviter eval() et exec() - Utiliser des parseurs sécurisés")
        
        if "command_injection" in vuln_types:
            recommendations.append("⚡ Valider et échapper les entrées pour les commandes système")
        
        if "hardcoded_credentials" in vuln_types:
            recommendations.append("🔐 Externaliser les credentials vers des variables d'environnement")
        
        if "weak_crypto" in vuln_types:
            recommendations.append("🔒 Utiliser des générateurs cryptographiquement sécurisés")
        
        if not recommendations and vulnerabilities:
            recommendations.append("🔍 Effectuer une revue de sécurité approfondie du code")
        
        return recommendations
    
    def _generate_performance_recommendations(self, metrics: CodeMetrics, quality_issues: List[QualityIssue]) -> List[str]:
        """Génère des recommandations de performance"""
        recommendations = []
        
        if metrics.cyclomatic_complexity > 20:
            recommendations.append("⚡ Optimiser les algorithmes complexes pour améliorer les performances")
        
        if metrics.nested_depth > 5:
            recommendations.append("🔄 Réduire l'imbrication pour améliorer la lisibilité et les performances")
        
        if metrics.duplication_percentage > 25:
            recommendations.append("🚀 Éliminer la duplication pour réduire la taille du code")
        
        complexity_issues = [i for i in quality_issues if i.issue_type == "complexity"]
        if complexity_issues:
            recommendations.append("📈 Décomposer les fonctions complexes en sous-fonctions")
        
        if not recommendations:
            recommendations.append("✨ Code performant - Continuer les bonnes pratiques")
        
        return recommendations
    
    async def _save_code_analysis(self, analysis_type: str, analysis_data: Dict[str, Any]):
        """Sauvegarde l'analyse en base de données"""
        try:
            collection = await get_collection("code_analysis_history")
            
            analysis_record = {
                "analysis_type": analysis_type,
                "timestamp": datetime.now(timezone.utc),
                "language": analysis_data.get("language"),
                "security_score": analysis_data.get("security_score"),
                "quality_score": analysis_data.get("quality_score"),
                "vulnerabilities_count": analysis_data.get("vulnerabilities_count", 0),
                "quality_issues_count": analysis_data.get("quality_issues_count", 0)
            }
            
            await collection.insert_one(analysis_record)
            print(f"✅ Analyse Code Analysis AI sauvegardée: {analysis_type}")
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde Code Analysis AI: {e}")

# Instance globale du service Code Analysis AI
code_analysis_ai_service = CodeAnalysisAIService()