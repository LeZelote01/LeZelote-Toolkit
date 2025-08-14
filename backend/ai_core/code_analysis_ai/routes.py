"""
Routes FastAPI pour Code Analysis AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Analyse statique sécurisée du code source
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import tempfile
import os
import uuid

from .main import (
    code_analysis_ai_service,
    CodeAnalysisRequest,
    CodeAnalysisResult,
    VulnerabilityFinding,
    QualityIssue,
    DependencyAnalysis,
    CodeMetrics
)

# Configuration du router
router = APIRouter(
    prefix="/api/code-analysis-ai",
    tags=["code-analysis-ai"],
    responses={404: {"description": "Code Analysis AI service not found"}}
)

# Modèles de réponse pour l'API
class CodeAnalysisAIStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    supported_languages: List[str]
    analysis_types: List[str]
    llm_configured: bool

class CodeAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    analysis: CodeAnalysisResult
    execution_time_ms: int
    recommendations_count: int

class VulnerabilityScanResponse(BaseModel):
    success: bool
    scan_id: str
    vulnerabilities: List[VulnerabilityFinding]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    security_score: float

class QualityAssessmentResponse(BaseModel):
    success: bool
    assessment_id: str
    quality_issues: List[QualityIssue]
    quality_score: float
    code_metrics: CodeMetrics
    recommendations: List[str]

class DependencyAuditResponse(BaseModel):
    success: bool
    audit_id: str
    dependencies: List[DependencyAnalysis]
    vulnerable_packages: int
    outdated_packages: int
    security_recommendations: List[str]

@router.get("/", response_model=CodeAnalysisAIStatusResponse)
async def code_analysis_ai_status():
    """Status du service Code Analysis AI"""
    return CodeAnalysisAIStatusResponse(
        status="operational",
        service="Code Analysis AI - Analyse Sécurisée du Code",
        version="1.0.0-portable",
        features={
            "security_analysis": True,
            "quality_assessment": True,
            "dependency_audit": True,
            "performance_analysis": True,
            "ast_parsing": True,
            "pattern_matching": True,
            "ai_recommendations": True,
            "multi_language": True,
            "vulnerability_database": True,
            "custom_rules": True
        },
        supported_languages=["python", "javascript", "java", "c", "cpp", "go", "rust", "php"],
        analysis_types=["security", "quality", "performance", "dependency", "full"],
        llm_configured=code_analysis_ai_service.llm_client is not None
    )

@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyse complète du code source avec IA"""
    try:
        start_time = datetime.now()
        
        # Validation des paramètres
        if not any([request.code_content, request.file_path, request.repository_url]):
            raise HTTPException(
                status_code=400, 
                detail="Code source, chemin de fichier ou URL repository requis"
            )
        
        supported_languages = ["python", "javascript", "java", "c", "cpp", "go", "rust", "php"]
        if request.language not in supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Langage non supporté. Langages disponibles: {', '.join(supported_languages)}"
            )
        
        analysis_types = ["security", "quality", "performance", "dependency", "full"]
        if request.analysis_type not in analysis_types:
            raise HTTPException(
                status_code=400,
                detail=f"Type d'analyse invalide. Types disponibles: {', '.join(analysis_types)}"
            )
        
        # Exécution de l'analyse
        analysis_result = await code_analysis_ai_service.analyze_code(request)
        
        # Calcul du temps d'exécution
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Comptage des recommandations
        total_recommendations = (
            len(analysis_result.ai_recommendations) +
            len(analysis_result.security_recommendations) +
            len(analysis_result.performance_recommendations)
        )
        
        return CodeAnalysisResponse(
            success=True,
            analysis_id=analysis_result.analysis_id,
            analysis=analysis_result,
            execution_time_ms=int(execution_time),
            recommendations_count=total_recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du code: {str(e)}"
        )

@router.post("/scan-vulnerabilities", response_model=VulnerabilityScanResponse)
async def scan_vulnerabilities(request: CodeAnalysisRequest):
    """Scan de sécurité spécialisé pour vulnérabilités"""
    try:
        # Forcer le type d'analyse à security
        request.analysis_type = "security"
        
        # Exécution du scan
        analysis_result = await code_analysis_ai_service.analyze_code(request)
        
        # Comptage par sévérité
        vulnerabilities = analysis_result.vulnerability_findings
        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        medium_count = len([v for v in vulnerabilities if v.severity == "medium"])
        low_count = len([v for v in vulnerabilities if v.severity == "low"])
        
        return VulnerabilityScanResponse(
            success=True,
            scan_id=f"vuln_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            vulnerabilities=vulnerabilities,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            security_score=analysis_result.overall_security_score
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scan de vulnérabilités: {str(e)}"
        )

@router.post("/assess-quality", response_model=QualityAssessmentResponse)
async def assess_quality(request: CodeAnalysisRequest):
    """Évaluation de la qualité du code"""
    try:
        # Forcer le type d'analyse à quality
        request.analysis_type = "quality"
        
        # Exécution de l'évaluation
        analysis_result = await code_analysis_ai_service.analyze_code(request)
        
        return QualityAssessmentResponse(
            success=True,
            assessment_id=f"quality_assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            quality_issues=analysis_result.quality_issues,
            quality_score=analysis_result.overall_quality_score,
            code_metrics=analysis_result.code_metrics,
            recommendations=analysis_result.ai_recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'évaluation qualité: {str(e)}"
        )

@router.post("/audit-dependencies", response_model=DependencyAuditResponse)
async def audit_dependencies(request: CodeAnalysisRequest):
    """Audit des dépendances pour vulnérabilités"""
    try:
        # Forcer l'analyse des dépendances
        request.analysis_type = "dependency"
        request.include_dependencies = True
        
        # Exécution de l'audit
        analysis_result = await code_analysis_ai_service.analyze_code(request)
        
        dependencies = analysis_result.dependency_analysis
        vulnerable_packages = len([d for d in dependencies if len(d.vulnerabilities) > 0])
        outdated_packages = len([d for d in dependencies if d.outdated])
        
        return DependencyAuditResponse(
            success=True,
            audit_id=f"dep_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            dependencies=dependencies,
            vulnerable_packages=vulnerable_packages,
            outdated_packages=outdated_packages,
            security_recommendations=analysis_result.security_recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'audit des dépendances: {str(e)}"
        )

@router.post("/upload-file")
async def upload_and_analyze(
    file: UploadFile = File(...),
    analysis_type: str = "full",
    language: Optional[str] = None
):
    """Upload et analyse d'un fichier source"""
    try:
        # Validation du fichier
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier requis")
        
        # Détection automatique du langage si non spécifié
        if not language:
            extension = os.path.splitext(file.filename)[1].lower()
            language_mapping = {
                '.py': 'python',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.ts': 'javascript',
                '.tsx': 'javascript',
                '.java': 'java',
                '.c': 'c',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.go': 'go',
                '.rs': 'rust',
                '.php': 'php'
            }
            language = language_mapping.get(extension)
            
            if not language:
                raise HTTPException(
                    status_code=400,
                    detail=f"Impossible de détecter le langage pour l'extension {extension}"
                )
        
        # Lecture du contenu
        content = await file.read()
        code_content = content.decode('utf-8')
        
        # Création de la requête d'analyse
        request = CodeAnalysisRequest(
            analysis_type=analysis_type,
            code_content=code_content,
            file_path=file.filename,
            language=language
        )
        
        # Exécution de l'analyse
        analysis_result = await code_analysis_ai_service.analyze_code(request)
        
        return {
            "success": True,
            "filename": file.filename,
            "language_detected": language,
            "analysis": analysis_result
        }
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Fichier non lisible - encodage non supporté"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du fichier: {str(e)}"
        )

@router.get("/vulnerability-patterns/{language}")
async def get_vulnerability_patterns(language: str):
    """Récupère les patterns de vulnérabilité pour un langage"""
    try:
        patterns = code_analysis_ai_service.security_patterns.get(language, [])
        
        if not patterns:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun pattern disponible pour le langage: {language}"
            )
        
        return {
            "success": True,
            "language": language,
            "patterns": patterns,
            "total_patterns": len(patterns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des patterns: {str(e)}"
        )

@router.get("/quality-rules/{language}")
async def get_quality_rules(language: str):
    """Récupère les règles de qualité pour un langage"""
    try:
        rules = code_analysis_ai_service.quality_rules.get(language, [])
        
        if not rules:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune règle disponible pour le langage: {language}"
            )
        
        return {
            "success": True,
            "language": language,
            "rules": rules,
            "total_rules": len(rules)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des règles: {str(e)}"
        )

@router.get("/cwe-database")
async def get_cwe_database():
    """Récupère la base de données CWE intégrée"""
    try:
        cwe_db = code_analysis_ai_service.vulnerability_database.get("cwe_database", [])
        
        return {
            "success": True,
            "cwe_entries": cwe_db,
            "total_entries": len(cwe_db),
            "last_updated": "2025-01-01"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la base CWE: {str(e)}"
        )

@router.post("/custom-analysis")
async def custom_analysis(
    code_content: str,
    custom_patterns: List[Dict[str, Any]],
    language: str,
    background_tasks: BackgroundTasks
):
    """Analyse personnalisée avec patterns custom"""
    try:
        # Validation des patterns personnalisés
        required_fields = ["pattern", "type", "severity", "description", "remediation"]
        for pattern in custom_patterns:
            for field in required_fields:
                if field not in pattern:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Champ requis manquant dans pattern: {field}"
                    )
        
        # Ajout temporaire des patterns personnalisés
        original_patterns = code_analysis_ai_service.security_patterns.get(language, [])
        code_analysis_ai_service.security_patterns[language] = original_patterns + custom_patterns
        
        try:
            # Création de la requête d'analyse
            request = CodeAnalysisRequest(
                analysis_type="security",
                code_content=code_content,
                language=language
            )
            
            # Exécution de l'analyse
            analysis_result = await code_analysis_ai_service.analyze_code(request)
            
            return {
                "success": True,
                "custom_patterns_used": len(custom_patterns),
                "analysis": analysis_result
            }
            
        finally:
            # Restauration des patterns originaux
            code_analysis_ai_service.security_patterns[language] = original_patterns
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse personnalisée: {str(e)}"
        )

@router.get("/analysis-history")
async def get_analysis_history(limit: int = 10):
    """Récupère l'historique des analyses récentes"""
    try:
        # Cette fonction nécessiterait une vraie base de données
        # Pour la démo, retour d'un historique simulé
        
        history = []
        for i in range(min(limit, 5)):  # Max 5 pour la démo
            history.append({
                "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                "timestamp": (datetime.now().replace(hour=datetime.now().hour-i)).isoformat(),
                "language": ["python", "javascript", "java"][i % 3],
                "analysis_type": ["security", "quality", "full"][i % 3],
                "security_score": round(7.5 + i * 0.3, 1),
                "vulnerabilities_found": max(0, 5 - i),
                "quality_score": round(8.2 + i * 0.2, 1)
            })
        
        return {
            "success": True,
            "history": history,
            "total_analyses": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )