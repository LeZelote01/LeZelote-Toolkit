"""
Modèles de données pour Code Analysis AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Intelligence artificielle pour analyse sécurisée du code source
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
import uuid

# Énumérations
class AnalysisType(str, Enum):
    SECURITY = "security"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    DEPENDENCY = "dependency"
    FULL = "full"
    CUSTOM = "custom"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"

class VulnerabilityType(str, Enum):
    CODE_INJECTION = "code_injection"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    DESERIALIZATION = "deserialization"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_RANDOM = "insecure_random"
    BUFFER_OVERFLOW = "buffer_overflow"
    RACE_CONDITION = "race_condition"
    PRIVILEGE_ESCALATION = "privilege_escalation"

# Modèles de base
class CodeLocation(BaseModel):
    file_path: Optional[str] = Field(None, description="Chemin du fichier")
    line_number: Optional[int] = Field(None, description="Numéro de ligne")
    column_number: Optional[int] = Field(None, description="Numéro de colonne")
    function_name: Optional[str] = Field(None, description="Nom de la fonction")
    class_name: Optional[str] = Field(None, description="Nom de la classe")

class CodeSnippet(BaseModel):
    content: str = Field(..., description="Contenu du snippet")
    context_before: Optional[str] = Field(None, description="Contexte avant")
    context_after: Optional[str] = Field(None, description="Contexte après")
    highlighted_range: Optional[Tuple[int, int]] = Field(None, description="Plage mise en évidence")

# Modèles de requête
class CodeAnalysisRequest(BaseModel):
    analysis_type: AnalysisType = Field(..., description="Type d'analyse à effectuer")
    code_content: Optional[str] = Field(None, description="Code source à analyser")
    file_path: Optional[str] = Field(None, description="Chemin du fichier")
    repository_url: Optional[str] = Field(None, description="URL du repository Git")
    language: ProgrammingLanguage = Field(..., description="Langage de programmation")
    frameworks: Optional[List[str]] = Field(None, description="Frameworks utilisés")
    include_dependencies: bool = Field(True, description="Analyser les dépendances")
    security_focus: Optional[List[VulnerabilityType]] = Field(None, description="Focus sécurité spécifique")
    custom_rules: Optional[List[Dict[str, Any]]] = Field(None, description="Règles personnalisées")
    exclude_patterns: Optional[List[str]] = Field(None, description="Patterns à exclure")
    confidence_threshold: float = Field(0.7, description="Seuil de confiance minimum")

class BulkAnalysisRequest(BaseModel):
    files: List[Dict[str, str]] = Field(..., description="Liste des fichiers à analyser")
    analysis_type: AnalysisType = Field(..., description="Type d'analyse")
    common_language: Optional[ProgrammingLanguage] = Field(None, description="Langage commun")
    parallel_execution: bool = Field(True, description="Exécution parallèle")
    summary_report: bool = Field(True, description="Générer rapport de synthèse")

# Modèles de vulnérabilités
class VulnerabilityFinding(BaseModel):
    vulnerability_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: SeverityLevel = Field(..., description="Niveau de sévérité")
    vulnerability_type: VulnerabilityType = Field(..., description="Type de vulnérabilité")
    cwe_id: Optional[str] = Field(None, description="Common Weakness Enumeration ID")
    cve_id: Optional[str] = Field(None, description="Common Vulnerabilities and Exposures ID")
    owasp_category: Optional[str] = Field(None, description="Catégorie OWASP Top 10")
    location: CodeLocation = Field(..., description="Localisation dans le code")
    code_snippet: CodeSnippet = Field(..., description="Snippet de code vulnérable")
    title: str = Field(..., description="Titre de la vulnérabilité")
    description: str = Field(..., description="Description détaillée")
    impact: str = Field(..., description="Impact potentiel")
    remediation: str = Field(..., description="Solution recommandée")
    remediation_effort: str = Field(..., description="Effort de remédiation: trivial, easy, medium, hard")
    confidence: float = Field(..., description="Niveau de confiance (0-1)")
    false_positive_probability: float = Field(..., description="Probabilité de faux positif")
    exploitability: str = Field(..., description="Facilité d'exploitation: low, medium, high")
    references: List[str] = Field(default_factory=list, description="Références externes")
    tags: List[str] = Field(default_factory=list, description="Tags de classification")

class SecurityHotspot(BaseModel):
    hotspot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Titre du hotspot")
    location: CodeLocation = Field(..., description="Localisation")
    security_category: str = Field(..., description="Catégorie de sécurité")
    risk_level: str = Field(..., description="Niveau de risque: low, medium, high")
    review_required: bool = Field(..., description="Révision manuelle requise")
    automated_fix_available: bool = Field(False, description="Correction automatique disponible")

# Modèles de qualité
class QualityIssue(BaseModel):
    issue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issue_type: str = Field(..., description="Type: style, complexity, maintainability, documentation, naming")
    severity: str = Field(..., description="Sévérité: blocker, critical, major, minor, info")
    location: CodeLocation = Field(..., description="Localisation dans le code")
    code_snippet: CodeSnippet = Field(..., description="Code concerné")
    rule_name: str = Field(..., description="Nom de la règle violée")
    title: str = Field(..., description="Titre du problème")
    description: str = Field(..., description="Description du problème")
    suggestion: str = Field(..., description="Suggestion d'amélioration")
    category: str = Field(..., description="Catégorie du problème")
    effort_minutes: Optional[int] = Field(None, description="Effort estimé en minutes")
    technical_debt: Optional[str] = Field(None, description="Dette technique: low, medium, high")

class CodeSmell(BaseModel):
    smell_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    smell_type: str = Field(..., description="Type de code smell")
    location: CodeLocation = Field(..., description="Localisation")
    description: str = Field(..., description="Description du smell")
    refactoring_suggestion: str = Field(..., description="Suggestion de refactoring")
    impact_on_maintainability: str = Field(..., description="Impact sur la maintenabilité")

# Modèles de métriques
class CodeMetrics(BaseModel):
    lines_of_code: int = Field(..., description="Lignes de code")
    lines_of_comments: int = Field(..., description="Lignes de commentaires")
    blank_lines: int = Field(..., description="Lignes vides")
    cyclomatic_complexity: float = Field(..., description="Complexité cyclomatique")
    cognitive_complexity: float = Field(..., description="Complexité cognitive")
    maintainability_index: float = Field(..., description="Index de maintenabilité (0-100)")
    technical_debt_ratio: float = Field(..., description="Ratio de dette technique")
    code_coverage: Optional[float] = Field(None, description="Couverture de code")
    duplication_percentage: float = Field(..., description="Pourcentage de duplication")
    security_hotspots: int = Field(..., description="Nombre de points chauds sécurité")
    function_count: int = Field(0, description="Nombre de fonctions")
    class_count: int = Field(0, description="Nombre de classes")
    max_function_length: int = Field(0, description="Longueur max de fonction")
    average_function_length: float = Field(0, description="Longueur moyenne de fonction")
    nested_depth: int = Field(0, description="Profondeur d'imbrication max")

class PerformanceMetrics(BaseModel):
    potential_bottlenecks: List[Dict[str, Any]] = Field(default_factory=list)
    memory_issues: List[Dict[str, Any]] = Field(default_factory=list)
    algorithmic_complexity: Dict[str, str] = Field(default_factory=dict)
    optimization_opportunities: List[str] = Field(default_factory=list)

# Modèles de dépendances
class DependencyVulnerability(BaseModel):
    vulnerability_id: str = Field(..., description="ID de la vulnérabilité")
    cve_id: Optional[str] = Field(None, description="CVE ID")
    severity: SeverityLevel = Field(..., description="Sévérité")
    description: str = Field(..., description="Description")
    affected_versions: List[str] = Field(..., description="Versions affectées")
    fixed_version: Optional[str] = Field(None, description="Version corrigée")
    published_date: Optional[datetime] = Field(None, description="Date de publication")

class DependencyAnalysis(BaseModel):
    package_name: str = Field(..., description="Nom du package")
    version: str = Field(..., description="Version actuelle")
    latest_version: Optional[str] = Field(None, description="Dernière version disponible")
    license: Optional[str] = Field(None, description="Licence")
    license_compatibility: Optional[str] = Field(None, description="Compatibilité de licence")
    vulnerabilities: List[DependencyVulnerability] = Field(default_factory=list)
    outdated: bool = Field(..., description="Version obsolète")
    security_score: float = Field(..., description="Score de sécurité (0-10)")
    maintenance_status: str = Field(..., description="Statut: active, deprecated, abandoned, unknown")
    download_stats: Optional[Dict[str, int]] = Field(None, description="Statistiques de téléchargement")
    repository_url: Optional[str] = Field(None, description="URL du repository")
    homepage_url: Optional[str] = Field(None, description="URL de la page d'accueil")
    dependencies: List[str] = Field(default_factory=list, description="Dépendances transitives")

class DependencyTree(BaseModel):
    root_package: str = Field(..., description="Package racine")
    tree_structure: Dict[str, Any] = Field(..., description="Structure arborescente")
    total_dependencies: int = Field(..., description="Nombre total de dépendances")
    direct_dependencies: int = Field(..., description="Dépendances directes")
    transitive_dependencies: int = Field(..., description="Dépendances transitives")
    circular_dependencies: List[List[str]] = Field(default_factory=list, description="Dépendances circulaires")

# Modèles de résultats
class CodeAnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_type: AnalysisType = Field(..., description="Type d'analyse effectuée")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    language: ProgrammingLanguage = Field(..., description="Langage analysé")
    file_analyzed: Optional[str] = Field(None, description="Fichier analysé")
    total_files_analyzed: int = Field(1, description="Nombre de fichiers analysés")
    
    # Scores globaux
    overall_security_score: float = Field(..., description="Score de sécurité global (0-10)")
    overall_quality_score: float = Field(..., description="Score de qualité global (0-10)")
    maintainability_score: float = Field(..., description="Score de maintenabilité (0-10)")
    reliability_score: float = Field(..., description="Score de fiabilité (0-10)")
    
    # Résultats détaillés
    vulnerability_findings: List[VulnerabilityFinding] = Field(default_factory=list)
    security_hotspots: List[SecurityHotspot] = Field(default_factory=list)
    quality_issues: List[QualityIssue] = Field(default_factory=list)
    code_smells: List[CodeSmell] = Field(default_factory=list)
    dependency_analysis: List[DependencyAnalysis] = Field(default_factory=list)
    dependency_tree: Optional[DependencyTree] = Field(None, description="Arbre des dépendances")
    
    # Métriques
    code_metrics: CodeMetrics = Field(..., description="Métriques du code")
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    
    # Recommandations
    ai_recommendations: List[str] = Field(default_factory=list, description="Recommandations IA")
    security_recommendations: List[str] = Field(default_factory=list, description="Recommandations sécurité")
    quality_recommendations: List[str] = Field(default_factory=list, description="Recommandations qualité")
    performance_recommendations: List[str] = Field(default_factory=list, description="Recommandations performance")
    
    # Métadonnées
    execution_time_seconds: float = Field(..., description="Temps d'exécution de l'analyse")
    confidence_level: float = Field(..., description="Niveau de confiance global")
    false_positive_estimate: float = Field(..., description="Estimation de faux positifs")
    
    # Résumé exécutif
    executive_summary: str = Field(..., description="Résumé exécutif")
    priority_issues: List[str] = Field(default_factory=list, description="Issues prioritaires")
    quick_wins: List[str] = Field(default_factory=list, description="Améliorations rapides")

class BulkAnalysisResult(BaseModel):
    bulk_analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_files: int = Field(..., description="Nombre total de fichiers")
    successfully_analyzed: int = Field(..., description="Fichiers analysés avec succès")
    failed_analyses: int = Field(..., description="Analyses échouées")
    
    individual_results: List[CodeAnalysisResult] = Field(..., description="Résultats individuels")
    aggregated_metrics: CodeMetrics = Field(..., description="Métriques agrégées")
    summary_report: str = Field(..., description="Rapport de synthèse")
    
    top_vulnerabilities: List[VulnerabilityFinding] = Field(default_factory=list)
    top_quality_issues: List[QualityIssue] = Field(default_factory=list)
    overall_recommendations: List[str] = Field(default_factory=list)

# Modèles de configuration
class AnalysisConfiguration(BaseModel):
    security_rules_enabled: bool = Field(True, description="Règles de sécurité activées")
    quality_rules_enabled: bool = Field(True, description="Règles de qualité activées")
    performance_rules_enabled: bool = Field(True, description="Règles de performance activées")
    custom_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Règles personnalisées")
    exclusion_patterns: List[str] = Field(default_factory=list, description="Patterns d'exclusion")
    confidence_threshold: float = Field(0.7, description="Seuil de confiance")
    max_issues_per_type: int = Field(100, description="Maximum d'issues par type")
    enable_ai_analysis: bool = Field(True, description="Analyse IA activée")
    language_specific_settings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

# Modèles de rapport
class AnalysisReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_result: CodeAnalysisResult = Field(..., description="Résultat d'analyse")
    report_format: str = Field("html", description="Format: html, pdf, json, xml")
    include_code_snippets: bool = Field(True, description="Inclure les snippets de code")
    include_recommendations: bool = Field(True, description="Inclure les recommandations")
    target_audience: str = Field("technical", description="Audience: technical, management, security")
    custom_branding: Optional[Dict[str, str]] = Field(None, description="Branding personnalisé")
    
class ComplianceReport(BaseModel):
    compliance_framework: str = Field(..., description="Framework: OWASP, CWE, SANS, PCI-DSS")
    compliance_score: float = Field(..., description="Score de conformité")
    compliant_rules: int = Field(..., description="Règles conformes")
    non_compliant_rules: int = Field(..., description="Règles non conformes")
    findings_by_category: Dict[str, int] = Field(default_factory=dict)
    remediation_roadmap: List[str] = Field(default_factory=list)