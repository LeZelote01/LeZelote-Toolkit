"""
AI Security Routes
API endpoints pour la sécurité des modèles IA
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from .models import (
    AISecurityRequest, AISecurityEvaluation, AIVulnerability,
    AISecurityStatus, AISecurityMetrics, TestType, AIModelType, Severity
)
from .scanner import AISecurityScanner
from database import get_database

router = APIRouter(prefix="/api/ai-security", tags=["AI Security"])

# Cache des évaluations et métriques
active_evaluations: Dict[str, Dict] = {}
completed_evaluations: Dict[str, AISecurityEvaluation] = {}
# metrics_storage = AISecurityMetrics()  # Commenté pour éviter les erreurs d'initialisation

@router.get("/")
async def ai_security_status():
    """Status du service AI Security"""
    
    # Calculer les métriques actuelles
    active_evaluations_count = len([e for e in active_evaluations.values() if e.get("status") in ["pending", "running"]])
    completed_evaluations_count = len(completed_evaluations)
    
    # Stats par type de modèle
    model_type_stats = {}
    for evaluation in completed_evaluations.values():
        model_type = evaluation.model_type.value
        model_type_stats[model_type] = model_type_stats.get(model_type, 0) + 1
    
    # Stats par type de test
    test_type_stats = {}
    for evaluation in completed_evaluations.values():
        for test_type in evaluation.tests_performed:
            test_type_stats[test_type.value] = test_type_stats.get(test_type.value, 0) + 1
    
    # Stats par sévérité
    severity_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for evaluation in completed_evaluations.values():
        for vuln in evaluation.vulnerabilities:
            severity_stats[vuln.severity.value] = severity_stats.get(vuln.severity.value, 0) + 1
    
    # Scores moyens
    avg_security_score = 0
    avg_robustness_score = 0
    avg_fairness_score = 0
    if completed_evaluations:
        avg_security_score = sum(e.security_score for e in completed_evaluations.values()) / len(completed_evaluations)
        avg_robustness_score = sum(e.robustness_score for e in completed_evaluations.values()) / len(completed_evaluations)
        avg_fairness_score = sum(e.fairness_score for e in completed_evaluations.values()) / len(completed_evaluations)
    
    return {
        "status": "operational",
        "service": "AI Security",
        "version": "1.0.0-portable",
        "features": {
            "prompt_injection_testing": True,
            "adversarial_attack_testing": True,
            "bias_evaluation": True,
            "robustness_testing": True,
            "privacy_leakage_testing": True,
            "data_poisoning_testing": True,
            "fairness_analysis": True,
            "model_extraction_testing": True
        },
        "supported_models": [
            "llm", "image_classification", "nlp", "computer_vision",
            "recommendation", "decision_tree", "neural_network", "ensemble"
        ],
        "supported_tests": [
            "prompt_injection", "adversarial_attack", "data_poisoning",
            "model_extraction", "bias_evaluation", "fairness_testing",
            "robustness_testing", "privacy_leakage"
        ],
        "security_frameworks": [
            "OWASP ML Top 10", "NIST AI Framework", "ISO 23053", "IEEE 2857"
        ],
        "active_evaluations": active_evaluations_count,
        "completed_evaluations": completed_evaluations_count,
        "model_type_stats": model_type_stats,
        "test_type_stats": test_type_stats,
        "severity_stats": severity_stats,
        "average_scores": {
            "security": round(avg_security_score, 1),
            "robustness": round(avg_robustness_score, 1),
            "fairness": round(avg_fairness_score, 1)
        }
    }

@router.post("/evaluate")
async def start_ai_evaluation(evaluation_request: AISecurityRequest, background_tasks: BackgroundTasks):
    """Lance une évaluation de sécurité IA"""
    try:
        # Générer un ID unique pour l'évaluation
        evaluation_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not evaluation_request.model_endpoint and not evaluation_request.model_file and not evaluation_request.model_name:
            raise HTTPException(
                status_code=400,
                detail="Au moins un identificateur de modèle est requis (endpoint, fichier ou nom)"
            )
        
        if not evaluation_request.test_suite:
            raise HTTPException(
                status_code=400,
                detail="Au moins un test doit être spécifié"
            )
        
        # Initialiser l'évaluation
        evaluation_info = {
            "evaluation_id": evaluation_id,
            "model_type": evaluation_request.model_type,
            "model_name": evaluation_request.model_name,
            "test_suite": evaluation_request.test_suite,
            "status": "starting",
            "start_time": datetime.now(),
            "options": evaluation_request.evaluation_options
        }
        
        active_evaluations[evaluation_id] = evaluation_info
        
        # Démarrer l'évaluation en arrière-plan
        background_tasks.add_task(
            execute_ai_evaluation,
            evaluation_id,
            evaluation_request.dict()
        )
        
        return {
            "evaluation_id": evaluation_id,
            "status": "started",
            "message": f"Évaluation de sécurité IA démarrée ({evaluation_request.model_type})",
            "model_name": evaluation_request.model_name,
            "model_type": evaluation_request.model_type,
            "test_suite": [test.value for test in evaluation_request.test_suite],
            "estimated_duration": "5-15 minutes",
            "check_status_url": f"/api/ai-security/evaluation/{evaluation_id}/status"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du démarrage de l'évaluation: {str(e)}"
        )

@router.get("/evaluation/{evaluation_id}/status")
async def get_evaluation_status(evaluation_id: str):
    """Récupère le statut d'une évaluation"""
    
    # Vérifier dans les évaluations actives
    if evaluation_id in active_evaluations:
        evaluation_info = active_evaluations[evaluation_id]
        duration = (datetime.now() - evaluation_info["start_time"]).total_seconds()
        
        return {
            "evaluation_id": evaluation_id,
            "status": evaluation_info["status"],
            "model_type": evaluation_info["model_type"],
            "model_name": evaluation_info.get("model_name"),
            "test_suite": [test.value for test in evaluation_info["test_suite"]],
            "duration": round(duration, 2),
            "progress": _estimate_evaluation_progress(evaluation_info["status"], duration),
            "message": _get_evaluation_status_message(evaluation_info["status"])
        }
    
    # Vérifier dans les évaluations terminées
    elif evaluation_id in completed_evaluations:
        evaluation_result = completed_evaluations[evaluation_id]
        
        return {
            "evaluation_id": evaluation_id,
            "status": evaluation_result.status,
            "model_type": evaluation_result.model_type,
            "model_name": evaluation_result.model_name,
            "duration": evaluation_result.duration,
            "progress": 100,
            "security_score": evaluation_result.security_score,
            "robustness_score": evaluation_result.robustness_score,
            "fairness_score": evaluation_result.fairness_score,
            "privacy_score": evaluation_result.privacy_score,
            "vulnerabilities_found": len(evaluation_result.vulnerabilities),
            "critical_vulnerabilities": evaluation_result.critical_vulnerabilities,
            "high_vulnerabilities": evaluation_result.high_vulnerabilities,
            "tests_performed": [test.value for test in evaluation_result.tests_performed]
        }
    
    else:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")

@router.get("/evaluation/{evaluation_id}/vulnerabilities")
async def get_evaluation_vulnerabilities(
    evaluation_id: str,
    test_type: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """Récupère les vulnérabilités d'une évaluation"""
    
    if evaluation_id not in completed_evaluations:
        if evaluation_id in active_evaluations:
            raise HTTPException(status_code=202, detail="Évaluation en cours, vulnérabilités pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    evaluation_result = completed_evaluations[evaluation_id]
    vulnerabilities = evaluation_result.vulnerabilities
    
    # Filtres
    if test_type:
        vulnerabilities = [v for v in vulnerabilities if v.test_type.value == test_type]
    
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity.value == severity]
    
    # Trier par sévérité et score de risque
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    vulnerabilities.sort(
        key=lambda x: (severity_order.get(x.severity.value, 0), x.risk_score),
        reverse=True
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_vulns = vulnerabilities[start_idx:end_idx]
    
    return {
        "evaluation_id": evaluation_id,
        "vulnerabilities": [vuln.dict() for vuln in paginated_vulns],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_vulnerabilities": len(vulnerabilities),
            "total_pages": (len(vulnerabilities) + page_size - 1) // page_size
        },
        "summary": {
            "critical": len([v for v in vulnerabilities if v.severity == Severity.CRITICAL]),
            "high": len([v for v in vulnerabilities if v.severity == Severity.HIGH]),
            "medium": len([v for v in vulnerabilities if v.severity == Severity.MEDIUM]),
            "low": len([v for v in vulnerabilities if v.severity == Severity.LOW]),
            "info": len([v for v in vulnerabilities if v.severity == Severity.INFO])
        },
        "filters_applied": {
            "test_type": test_type,
            "severity": severity
        }
    }

@router.get("/evaluation/{evaluation_id}/metrics")
async def get_evaluation_metrics(evaluation_id: str):
    """Récupère les métriques détaillées d'une évaluation"""
    
    if evaluation_id not in completed_evaluations:
        if evaluation_id in active_evaluations:
            raise HTTPException(status_code=202, detail="Évaluation en cours, métriques pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    evaluation_result = completed_evaluations[evaluation_id]
    
    return {
        "evaluation_id": evaluation_id,
        "scores": {
            "security_score": evaluation_result.security_score,
            "robustness_score": evaluation_result.robustness_score,
            "fairness_score": evaluation_result.fairness_score,
            "privacy_score": evaluation_result.privacy_score
        },
        "bias_metrics": evaluation_result.bias_metrics.dict() if evaluation_result.bias_metrics else None,
        "robustness_metrics": evaluation_result.robustness_metrics.dict() if evaluation_result.robustness_metrics else None,
        "privacy_metrics": evaluation_result.privacy_metrics.dict() if evaluation_result.privacy_metrics else None,
        "test_results": evaluation_result.test_results,
        "ml_security_standards": evaluation_result.ml_security_standards,
        "compliance_frameworks": evaluation_result.compliance_frameworks
    }

@router.get("/evaluation/{evaluation_id}/report")
async def get_evaluation_report(evaluation_id: str, format: str = "json"):
    """Génère le rapport complet d'évaluation"""
    
    if evaluation_id not in completed_evaluations:
        if evaluation_id in active_evaluations:
            raise HTTPException(status_code=202, detail="Évaluation en cours, rapport pas encore disponible")
        else:
            raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    evaluation_result = completed_evaluations[evaluation_id]
    
    if format == "json":
        return {
            "evaluation_info": {
                "evaluation_id": evaluation_id,
                "model_type": evaluation_result.model_type,
                "model_name": evaluation_result.model_name,
                "evaluation_date": evaluation_result.started_at.isoformat(),
                "duration": evaluation_result.duration,
                "tests_performed": [test.value for test in evaluation_result.tests_performed]
            },
            "security_summary": {
                "security_score": evaluation_result.security_score,
                "robustness_score": evaluation_result.robustness_score,
                "fairness_score": evaluation_result.fairness_score,
                "privacy_score": evaluation_result.privacy_score,
                "total_vulnerabilities": evaluation_result.total_vulnerabilities,
                "critical_vulnerabilities": evaluation_result.critical_vulnerabilities,
                "high_vulnerabilities": evaluation_result.high_vulnerabilities
            },
            "vulnerabilities": [vuln.dict() for vuln in evaluation_result.vulnerabilities],
            "detailed_metrics": {
                "bias_metrics": evaluation_result.bias_metrics.dict() if evaluation_result.bias_metrics else None,
                "robustness_metrics": evaluation_result.robustness_metrics.dict() if evaluation_result.robustness_metrics else None,
                "privacy_metrics": evaluation_result.privacy_metrics.dict() if evaluation_result.privacy_metrics else None
            },
            "test_results": evaluation_result.test_results,
            "recommendations": evaluation_result.recommendations,
            "mitigation_priority": evaluation_result.mitigation_priority,
            "compliance": {
                "ml_security_standards": evaluation_result.ml_security_standards,
                "compliance_frameworks": evaluation_result.compliance_frameworks
            }
        }
    
    elif format == "pdf":
        # En production, générer un PDF avec ReportLab
        raise HTTPException(status_code=501, detail="Export PDF pas encore implémenté")
    
    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json' ou 'pdf'")

@router.get("/evaluations")
async def list_evaluations(
    model_type: Optional[str] = None,
    test_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste les évaluations avec filtres"""
    
    all_evaluations = []
    
    # Ajouter les évaluations actives
    for evaluation_id, evaluation_info in active_evaluations.items():
        evaluation_data = {
            "evaluation_id": evaluation_id,
            "model_type": evaluation_info["model_type"].value,
            "model_name": evaluation_info.get("model_name"),
            "status": evaluation_info["status"],
            "start_time": evaluation_info["start_time"],
            "test_suite": [test.value for test in evaluation_info["test_suite"]],
            "duration": (datetime.now() - evaluation_info["start_time"]).total_seconds()
        }
        all_evaluations.append(evaluation_data)
    
    # Ajouter les évaluations terminées
    for evaluation_id, evaluation_result in completed_evaluations.items():
        evaluation_data = {
            "evaluation_id": evaluation_id,
            "model_type": evaluation_result.model_type.value,
            "model_name": evaluation_result.model_name,
            "status": evaluation_result.status,
            "start_time": evaluation_result.started_at,
            "test_suite": [test.value for test in evaluation_result.tests_performed],
            "duration": evaluation_result.duration,
            "security_score": evaluation_result.security_score,
            "vulnerabilities_found": len(evaluation_result.vulnerabilities)
        }
        all_evaluations.append(evaluation_data)
    
    # Filtres
    if model_type:
        all_evaluations = [e for e in all_evaluations if e["model_type"] == model_type]
    
    if test_type:
        all_evaluations = [e for e in all_evaluations if test_type in e["test_suite"]]
    
    if status:
        all_evaluations = [e for e in all_evaluations if e["status"] == status]
    
    # Trier par date de début (plus récent en premier)
    all_evaluations.sort(key=lambda x: x["start_time"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_evaluations = all_evaluations[start_idx:end_idx]
    
    return {
        "evaluations": paginated_evaluations,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_evaluations": len(all_evaluations),
            "total_pages": (len(all_evaluations) + page_size - 1) // page_size
        },
        "filters_applied": {
            "model_type": model_type,
            "test_type": test_type,
            "status": status
        },
        "summary": {
            "active_evaluations": len(active_evaluations),
            "completed_evaluations": len(completed_evaluations)
        }
    }

@router.get("/stats")
async def get_ai_security_stats():
    """Statistiques détaillées AI Security"""
    
    if not completed_evaluations:
        return {
            "total_evaluations": 0,
            "total_models": 0,
            "model_types": {},
            "test_types": {},
            "vulnerabilities": {},
            "average_scores": {}
        }
    
    # Stats générales
    total_models = len(set(e.model_name for e in completed_evaluations.values() if e.model_name))
    total_vulnerabilities = sum(len(e.vulnerabilities) for e in completed_evaluations.values())
    
    # Stats par type de modèle
    model_types_stats = {}
    test_types_stats = {}
    vulnerability_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    
    security_scores = []
    robustness_scores = []
    fairness_scores = []
    privacy_scores = []
    
    for evaluation in completed_evaluations.values():
        # Types de modèles
        model_types_stats[evaluation.model_type.value] = model_types_stats.get(evaluation.model_type.value, 0) + 1
        
        # Types de tests
        for test_type in evaluation.tests_performed:
            test_types_stats[test_type.value] = test_types_stats.get(test_type.value, 0) + 1
        
        # Vulnérabilités par sévérité
        for vuln in evaluation.vulnerabilities:
            vulnerability_stats[vuln.severity.value] = vulnerability_stats.get(vuln.severity.value, 0) + 1
        
        # Scores
        security_scores.append(evaluation.security_score)
        robustness_scores.append(evaluation.robustness_score)
        fairness_scores.append(evaluation.fairness_score)
        privacy_scores.append(evaluation.privacy_score)
    
    avg_security_score = sum(security_scores) / len(security_scores) if security_scores else 0
    avg_robustness_score = sum(robustness_scores) / len(robustness_scores) if robustness_scores else 0
    avg_fairness_score = sum(fairness_scores) / len(fairness_scores) if fairness_scores else 0
    avg_privacy_score = sum(privacy_scores) / len(privacy_scores) if privacy_scores else 0
    
    return {
        "total_evaluations": len(completed_evaluations),
        "total_models": total_models,
        "total_vulnerabilities": total_vulnerabilities,
        "model_types": model_types_stats,
        "test_types": test_types_stats,
        "vulnerabilities": vulnerability_stats,
        "average_scores": {
            "security": round(avg_security_score, 1),
            "robustness": round(avg_robustness_score, 1),
            "fairness": round(avg_fairness_score, 1),
            "privacy": round(avg_privacy_score, 1)
        },
        "security_score_distribution": {
            "excellent": len([s for s in security_scores if s >= 90]),
            "good": len([s for s in security_scores if 70 <= s < 90]),
            "average": len([s for s in security_scores if 50 <= s < 70]),
            "poor": len([s for s in security_scores if s < 50])
        }
    }

@router.delete("/evaluation/{evaluation_id}")
async def delete_evaluation(evaluation_id: str):
    """Supprime une évaluation et ses résultats"""
    
    deleted = False
    
    if evaluation_id in active_evaluations:
        del active_evaluations[evaluation_id]
        deleted = True
    
    if evaluation_id in completed_evaluations:
        del completed_evaluations[evaluation_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    return {"message": f"Évaluation {evaluation_id} supprimée avec succès"}

# Fonctions utilitaires

async def execute_ai_evaluation(evaluation_id: str, evaluation_request: Dict[str, Any]):
    """Exécute l'évaluation de sécurité IA en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_evaluations[evaluation_id]["status"] = "running"
        
        # Exécuter l'évaluation
        scanner = AISecurityScanner()
        result = await scanner.evaluate_model_security(evaluation_request)
        
        # Mettre à jour l'ID du résultat
        result.id = evaluation_id
        
        # Mettre à jour les IDs des vulnérabilités
        for vuln in result.vulnerabilities:
            vuln.evaluation_id = evaluation_id
        
        # Déplacer vers les évaluations terminées
        completed_evaluations[evaluation_id] = result
        del active_evaluations[evaluation_id]
        
        # Sauvegarder en base de données si possible
        try:
            db = await get_database()
            await db.save_evaluation_result(result.dict())
        except:
            pass  # Continuer même si la sauvegarde échoue
            
    except Exception as e:
        # Marquer l'évaluation comme échouée
        active_evaluations[evaluation_id]["status"] = "failed"
        active_evaluations[evaluation_id]["error"] = str(e)
        print(f"Erreur lors de l'évaluation {evaluation_id}: {e}")

def _estimate_evaluation_progress(status: str, duration: float) -> int:
    """Estime le pourcentage de progression"""
    if status == "starting":
        return 5
    elif status == "running":
        # Progression basée sur le temps (estimation 10 minutes max)
        return min(95, 10 + int((duration / 600) * 85))
    elif status == "completed":
        return 100
    elif status == "failed":
        return 0
    else:
        return 0

def _get_evaluation_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation de l'évaluation...",
        "running": "Évaluation en cours - Tests de sécurité IA...",
        "completed": "Évaluation terminée avec succès",
        "failed": "Erreur lors de l'évaluation"
    }
    return messages.get(status, "Statut inconnu")