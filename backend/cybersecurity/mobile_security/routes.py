"""
Mobile Security Routes
API endpoints pour l'analyse sécurité mobile
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

from .models import (
    MobileAppRequest, MobileAnalysisResult, MobileSecurityStatus,
    MobileSecurityMetrics
)
from .scanner import MobileSecurityScanner
from database import get_database

router = APIRouter(prefix="/api/mobile-security", tags=["Mobile Security"])

# Instance du scanner
scanner = MobileSecurityScanner()

# Stockage en mémoire pour la démo (à remplacer par la base de données)
analyses_storage = {}
metrics_storage = MobileSecurityMetrics()

@router.get("/")
async def mobile_security_status():
    """Status du service Mobile Security"""
    
    # Calculer les métriques actuelles (en mode simple pour commencer)
    active_analyses = len([a for a in analyses_storage.values() if a.status in ["pending", "running"]])
    completed_analyses = len([a for a in analyses_storage.values() if a.status == "completed"])
    
    return {
        "status": "operational",
        "service": "Mobile Security",
        "version": "1.0.0-portable",
        "features": {
            "android_analysis": True,
            "ios_analysis": True,
            "static_analysis": True,
            "dynamic_analysis": False,
            "owasp_masvs": True,
            "nist_mobile": True,
            "automated_reporting": True
        },
        "supported_platforms": ["android", "ios"],
        "supported_frameworks": ["OWASP_MASVS", "NIST_Mobile", "SANS_Mobile"],
        "active_analyses": active_analyses,
        "completed_analyses": completed_analyses,
        "total_analyses": len(analyses_storage)
    }

@router.post("/analyze/app", response_model=dict)
async def analyze_mobile_app(app_request: MobileAppRequest):
    """
    Lance l'analyse d'une application mobile
    """
    try:
        # Validation des paramètres
        if app_request.platform not in ["android", "ios"]:
            raise HTTPException(
                status_code=400,
                detail="Platform must be 'android' or 'ios'"
            )
        
        if app_request.source_type not in ["file", "url"]:
            raise HTTPException(
                status_code=400,
                detail="Source type must be 'file' or 'url'"
            )
        
        # Générer un ID unique pour l'analyse
        analysis_id = str(uuid.uuid4())
        
        # Créer l'analyse initiale
        analysis = MobileAnalysisResult(
            id=analysis_id,
            app_id=f"app_{analysis_id[:8]}",
            platform=app_request.platform,
            app_name="En cours d'analyse...",
            package_name="",
            status="pending"
        )
        
        # Stocker l'analyse
        analyses_storage[analysis_id] = analysis
        
        # Lancer l'analyse en arrière-plan
        asyncio.create_task(perform_analysis(analysis_id, app_request.dict()))
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "message": "Analyse lancée avec succès",
            "estimated_duration": "2-5 minutes",
            "platform": app_request.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du lancement de l'analyse: {str(e)}"
        )

@router.get("/analyses", response_model=List[dict])
async def list_analyses(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    Liste les analyses avec filtrage et pagination
    """
    try:
        # Filtrer les analyses
        filtered_analyses = list(analyses_storage.values())
        
        if platform:
            filtered_analyses = [a for a in filtered_analyses if a.platform == platform]
        
        if status:
            filtered_analyses = [a for a in filtered_analyses if a.status == status]
        
        # Trier par date de création (plus récent en premier)
        filtered_analyses.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_analyses = filtered_analyses[start_idx:end_idx]
        
        # Convertir en format API
        result = []
        for analysis in paginated_analyses:
            summary_data = {
                "id": analysis.id,
                "app_id": analysis.app_id,
                "app_name": analysis.app_name,
                "platform": analysis.platform,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat(),
                "summary": analysis.summary
            }
            
            if analysis.status == "completed":
                summary_data["compliance_scores"] = analysis.compliance_scores
                summary_data["vulnerabilities_count"] = len(analysis.vulnerabilities)
            
            result.append(summary_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des analyses: {str(e)}"
        )

@router.get("/analysis/{analysis_id}", response_model=MobileAnalysisResult)
async def get_analysis_details(analysis_id: str):
    """
    Récupère les détails complets d'une analyse
    """
    if analysis_id not in analyses_storage:
        raise HTTPException(
            status_code=404,
            detail="Analyse non trouvée"
        )
    
    return analyses_storage[analysis_id]

@router.get("/analysis/{analysis_id}/vulnerabilities", response_model=List[dict])
async def get_analysis_vulnerabilities(
    analysis_id: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """
    Récupère les vulnérabilités d'une analyse avec filtrage
    """
    if analysis_id not in analyses_storage:
        raise HTTPException(
            status_code=404,
            detail="Analyse non trouvée"
        )
    
    analysis = analyses_storage[analysis_id]
    vulnerabilities = analysis.vulnerabilities
    
    # Filtres
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity == severity]
    
    if category:
        vulnerabilities = [v for v in vulnerabilities if v.category == category]
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_vulns = vulnerabilities[start_idx:end_idx]
    
    return [v.dict() for v in paginated_vulns]

@router.get("/analysis/{analysis_id}/report")
async def get_analysis_report(analysis_id: str, format: str = "json"):
    """
    Génère un rapport d'analyse
    """
    if analysis_id not in analyses_storage:
        raise HTTPException(
            status_code=404,
            detail="Analyse non trouvée"
        )
    
    analysis = analyses_storage[analysis_id]
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="L'analyse n'est pas terminée"
        )
    
    if format.lower() == "pdf":
        # Génération PDF (simulée pour la démo)
        from fastapi.responses import Response
        
        pdf_content = generate_pdf_report(analysis)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=mobile_security_report_{analysis_id[:8]}.pdf"}
        )
    
    # Format JSON par défaut
    return {
        "analysis_id": analysis.id,
        "app_info": {
            "name": analysis.app_name,
            "platform": analysis.platform,
            "package_name": analysis.package_name
        },
        "analysis_info": {
            "started_at": analysis.started_at.isoformat(),
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            "frameworks_used": analysis.frameworks_used
        },
        "summary": analysis.summary,
        "compliance_scores": analysis.compliance_scores,
        "vulnerabilities": [
            {
                "severity": v.severity,
                "category": v.category,
                "title": v.title,
                "description": v.description,
                "owasp_category": v.owasp_category,
                "remediation": v.remediation,
                "file_path": v.file_path,
                "confidence": v.confidence
            }
            for v in analysis.vulnerabilities
        ],
        "recommendations": generate_recommendations(analysis)
    }

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Supprime une analyse
    """
    if analysis_id not in analyses_storage:
        raise HTTPException(
            status_code=404,
            detail="Analyse non trouvée"
        )
    
    del analyses_storage[analysis_id]
    
    return {
        "status": "success",
        "message": "Analyse supprimée avec succès"
    }

@router.get("/stats", response_model=dict)
async def get_mobile_security_stats():
    """
    Statistiques détaillées Mobile Security
    """
    
    total_analyses = len(analyses_storage)
    if total_analyses == 0:
        return {
            "total_analyses": 0,
            "platforms": {},
            "vulnerabilities": {},
            "compliance_scores": {}
        }
    
    # Stats par plateforme
    platforms_stats = {}
    for analysis in analyses_storage.values():
        platform = analysis.platform
        if platform not in platforms_stats:
            platforms_stats[platform] = {"count": 0, "completed": 0, "avg_score": 0}
        
        platforms_stats[platform]["count"] += 1
        if analysis.status == "completed":
            platforms_stats[platform]["completed"] += 1
            if analysis.compliance_scores.get("Overall", 0) > 0:
                platforms_stats[platform]["avg_score"] += analysis.compliance_scores["Overall"]
    
    # Calculer les moyennes
    for platform_data in platforms_stats.values():
        if platform_data["completed"] > 0:
            platform_data["avg_score"] = round(platform_data["avg_score"] / platform_data["completed"], 1)
    
    # Stats vulnérabilités
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    category_counts = {}
    
    for analysis in analyses_storage.values():
        if analysis.status == "completed":
            for vuln in analysis.vulnerabilities:
                severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
                category_counts[vuln.owasp_category] = category_counts.get(vuln.owasp_category, 0) + 1
    
    return {
        "total_analyses": total_analyses,
        "platforms": platforms_stats,
        "vulnerabilities": {
            "by_severity": severity_counts,
            "by_category": category_counts
        },
        "compliance_scores": {
            "avg_owasp_masvs": round(
                sum(a.compliance_scores.get("OWASP_MASVS", 0) for a in analyses_storage.values() if a.status == "completed") /
                max(1, len([a for a in analyses_storage.values() if a.status == "completed"])), 1
            )
        }
    }

# Fonctions utilitaires

async def perform_analysis(analysis_id: str, app_request: dict):
    """
    Effectue l'analyse en arrière-plan
    """
    try:
        # Récupérer l'analyse
        analysis = analyses_storage[analysis_id]
        analysis.status = "running"
        analysis.updated_at = datetime.now()
        
        # Lancer le scanner
        result = await scanner.analyze_mobile_app(app_request)
        
        # Mettre à jour l'analyse stockée
        analysis.app_name = result.app_name
        analysis.package_name = result.package_name
        analysis.app_version = result.app_version
        analysis.analysis_type = result.analysis_type
        analysis.frameworks_used = result.frameworks_used or ["OWASP_MASVS", "NIST_Mobile"]
        analysis.vulnerabilities = result.vulnerabilities
        analysis.summary = result.summary
        analysis.compliance_scores = result.compliance_scores
        analysis.status = result.status
        analysis.completed_at = result.completed_at
        analysis.updated_at = datetime.now()
        
    except Exception as e:
        # Marquer comme échoué
        analysis = analyses_storage[analysis_id]
        analysis.status = "failed"
        analysis.summary = {"error": str(e)}
        analysis.updated_at = datetime.now()

def generate_pdf_report(analysis: MobileAnalysisResult) -> bytes:
    """
    Génère un rapport PDF (simulé pour la démo)
    """
    # En production, utiliser reportlab ou weasyprint
    pdf_content = f"""
    RAPPORT D'ANALYSE DE SÉCURITÉ MOBILE
    
    Application: {analysis.app_name}
    Plateforme: {analysis.platform}
    Package: {analysis.package_name}
    
    RÉSUMÉ:
    - Vulnérabilités trouvées: {len(analysis.vulnerabilities)}
    - Score de conformité: {analysis.compliance_scores.get('Overall', 0)}/100
    
    VULNÉRABILITÉS:
    {chr(10).join([f"- {v.severity.upper()}: {v.title}" for v in analysis.vulnerabilities[:10]])}
    
    Rapport généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return pdf_content.encode('utf-8')

def generate_recommendations(analysis: MobileAnalysisResult) -> List[str]:
    """
    Génère des recommandations basées sur l'analyse
    """
    recommendations = []
    
    # Recommendations basées sur le score
    overall_score = analysis.compliance_scores.get("Overall", 0)
    
    if overall_score < 40:
        recommendations.append("🚨 Niveau de sécurité critique - Remédiation urgente requise")
        recommendations.append("Implémenter immédiatement les corrections pour les vulnérabilités critiques et hautes")
    elif overall_score < 60:
        recommendations.append("⚠️ Niveau de sécurité insuffisant - Améliorations nécessaires")
        recommendations.append("Prioriser la correction des vulnérabilités hautes et moyennes")
    elif overall_score < 80:
        recommendations.append("✅ Niveau de sécurité acceptable - Optimisations recommandées")
        recommendations.append("Corriger les vulnérabilités moyennes restantes")
    else:
        recommendations.append("🎉 Excellent niveau de sécurité - Maintenir les bonnes pratiques")
    
    # Recommendations spécifiques par plateforme
    if analysis.platform == "android":
        recommendations.extend([
            "Utiliser Android App Bundle pour la distribution",
            "Implémenter la vérification d'intégrité avec Play Integrity API",
            "Utiliser le chiffrement au niveau fichier Android"
        ])
    else:  # iOS
        recommendations.extend([
            "Utiliser App Transport Security (ATS)",
            "Implémenter la protection contre le jailbreak",
            "Utiliser le Keychain pour le stockage sécurisé"
        ])
    
    return recommendations