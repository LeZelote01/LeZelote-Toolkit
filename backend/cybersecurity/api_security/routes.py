"""
API Security Routes
API endpoints pour la sécurité des APIs
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from .models import (
    APISecurityRequest, APITestResult, APIVulnerability,
    APISecurityStatus, APISecurityMetrics, TestType, Severity, APIType
)
from .scanner import APISecurityScanner
from database import get_database

router = APIRouter(prefix="/api/api-security", tags=["API Security"])

# Cache des tests et métriques
active_tests: Dict[str, Dict] = {}
completed_tests: Dict[str, APITestResult] = {}
metrics_storage = APISecurityMetrics(
    security_score=0.0,
    authentication_score=0.0,
    authorization_score=0.0,
    data_protection_score=0.0,
    rate_limiting_score=0.0
)

@router.get("/")
async def api_security_status():
    """Status du service API Security"""
    
    # Calculer les métriques actuelles
    active_tests_count = len([t for t in active_tests.values() if t.get("status") in ["pending", "running"]])
    completed_tests_count = len(completed_tests)
    
    # Stats par type d'API
    api_type_stats = {}
    for test in completed_tests.values():
        api_type = test.api_type.value
        api_type_stats[api_type] = api_type_stats.get(api_type, 0) + 1
    
    # Stats par type de test
    test_type_stats = {}
    for test in completed_tests.values():
        for test_type in test.tests_performed:
            test_type_stats[test_type.value] = test_type_stats.get(test_type.value, 0) + 1
    
    # Stats par sévérité
    severity_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for test in completed_tests.values():
        for vuln in test.vulnerabilities:
            severity_stats[vuln.severity.value] = severity_stats.get(vuln.severity.value, 0) + 1
    
    # Stats OWASP
    owasp_stats = {}
    for test in completed_tests.values():
        if test.security_metrics and test.security_metrics.owasp_compliance:
            for category, compliant in test.security_metrics.owasp_compliance.items():
                if category not in owasp_stats:
                    owasp_stats[category] = {"total": 0, "compliant": 0}
                owasp_stats[category]["total"] += 1
                if compliant:
                    owasp_stats[category]["compliant"] += 1
    
    # Scores moyens
    avg_security_score = 0
    avg_auth_score = 0
    if completed_tests:
        scores = [t.security_metrics.security_score for t in completed_tests.values() if t.security_metrics]
        avg_security_score = sum(scores) / len(scores) if scores else 0
        
        auth_scores = [t.security_metrics.authentication_score for t in completed_tests.values() if t.security_metrics]
        avg_auth_score = sum(auth_scores) / len(auth_scores) if auth_scores else 0
    
    return {
        "status": "operational",
        "service": "API Security",
        "version": "1.0.0-portable",
        "features": {
            "owasp_api_top10_testing": True,
            "authentication_testing": True,
            "authorization_testing": True,
            "injection_testing": True,
            "rate_limiting_testing": True,
            "cors_testing": True,
            "ssl_tls_testing": True,
            "openapi_discovery": True,
            "custom_endpoint_testing": True
        },
        "supported_api_types": [
            "rest", "graphql", "soap", "grpc", "webhook"
        ],
        "supported_tests": [
            "owasp_api_top10", "authentication", "authorization", 
            "injection", "rate_limiting", "data_validation",
            "cors", "ssl_tls", "error_handling", "logging_monitoring"
        ],
        "owasp_categories_supported": [
            "API1:2023", "API2:2023", "API3:2023", "API4:2023", "API5:2023",
            "API6:2023", "API7:2023", "API8:2023", "API9:2023", "API10:2023"
        ],
        "active_tests": active_tests_count,
        "completed_tests": completed_tests_count,
        "api_type_stats": api_type_stats,
        "test_type_stats": test_type_stats,
        "severity_stats": severity_stats,
        "owasp_compliance_stats": owasp_stats,
        "average_scores": {
            "security": round(avg_security_score, 1),
            "authentication": round(avg_auth_score, 1)
        }
    }

@router.post("/test")
async def start_api_test(test_request: APISecurityRequest, background_tasks: BackgroundTasks):
    """Lance un test de sécurité API"""
    try:
        # Générer un ID unique pour le test
        test_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not test_request.base_url:
            raise HTTPException(
                status_code=400,
                detail="URL de base de l'API requise"
            )
        
        if not test_request.test_suite:
            raise HTTPException(
                status_code=400,
                detail="Au moins un test doit être spécifié"
            )
        
        # Initialiser le test
        test_info = {
            "test_id": test_id,
            "base_url": test_request.base_url,
            "api_type": test_request.api_type,
            "test_suite": test_request.test_suite,
            "status": "starting",
            "start_time": datetime.now(),
            "options": test_request.test_options
        }
        
        active_tests[test_id] = test_info
        
        # Démarrer le test en arrière-plan
        background_tasks.add_task(
            execute_api_test,
            test_id,
            test_request.dict()
        )
        
        return {
            "test_id": test_id,
            "status": "started",
            "message": f"Test de sécurité API démarré ({test_request.api_type})",
            "base_url": test_request.base_url,
            "api_type": test_request.api_type,
            "test_suite": [test.value for test in test_request.test_suite],
            "estimated_duration": _estimate_test_duration(test_request),
            "check_status_url": f"/api/api-security/test/{test_id}/status"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du démarrage du test: {str(e)}"
        )

@router.get("/test/{test_id}/status")
async def get_test_status(test_id: str):
    """Récupère le statut d'un test"""
    
    # Vérifier dans les tests actifs
    if test_id in active_tests:
        test_info = active_tests[test_id]
        duration = (datetime.now() - test_info["start_time"]).total_seconds()
        
        return {
            "test_id": test_id,
            "status": test_info["status"],
            "api_type": test_info["api_type"],
            "base_url": test_info["base_url"],
            "test_suite": [test.value for test in test_info["test_suite"]],
            "duration": round(duration, 2),
            "progress": _estimate_test_progress(test_info["status"], duration),
            "message": _get_test_status_message(test_info["status"])
        }
    
    # Vérifier dans les tests terminés
    elif test_id in completed_tests:
        test_result = completed_tests[test_id]
        
        return {
            "test_id": test_id,
            "status": test_result.status,
            "api_type": test_result.api_type,
            "base_url": test_result.base_url,
            "duration": test_result.duration,
            "progress": 100,
            "endpoints_tested": len(test_result.endpoints_tested),
            "endpoints_discovered": len(test_result.endpoints_discovered),
            "vulnerabilities_found": len(test_result.vulnerabilities),
            "critical_vulnerabilities": test_result.critical_vulnerabilities,
            "high_vulnerabilities": test_result.high_vulnerabilities,
            "security_score": test_result.security_metrics.security_score if test_result.security_metrics else 0,
            "tests_performed": [test.value for test in test_result.tests_performed]
        }
    
    else:
        raise HTTPException(status_code=404, detail="Test non trouvé")

@router.get("/test/{test_id}/vulnerabilities")
async def get_test_vulnerabilities(
    test_id: str,
    test_type: Optional[str] = None,
    severity: Optional[str] = None,
    owasp_category: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """Récupère les vulnérabilités d'un test"""
    
    if test_id not in completed_tests:
        if test_id in active_tests:
            raise HTTPException(status_code=202, detail="Test en cours, vulnérabilités pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Test non trouvé")
    
    test_result = completed_tests[test_id]
    vulnerabilities = test_result.vulnerabilities
    
    # Filtres
    if test_type:
        vulnerabilities = [v for v in vulnerabilities if v.test_type.value == test_type]
    
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity.value == severity]
    
    if owasp_category:
        vulnerabilities = [v for v in vulnerabilities if v.owasp_category == owasp_category]
    
    # Trier par sévérité et confidence
    severity_order = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
    vulnerabilities.sort(
        key=lambda x: (severity_order.get(x.severity.value, 0), x.confidence),
        reverse=True
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_vulns = vulnerabilities[start_idx:end_idx]
    
    return {
        "test_id": test_id,
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
        "owasp_categories": {
            category: len([v for v in vulnerabilities if v.owasp_category == category])
            for category in set(v.owasp_category for v in vulnerabilities if v.owasp_category)
        },
        "filters_applied": {
            "test_type": test_type,
            "severity": severity,
            "owasp_category": owasp_category
        }
    }

@router.get("/test/{test_id}/endpoints")
async def get_test_endpoints(test_id: str):
    """Récupère les endpoints testés"""
    
    if test_id not in completed_tests:
        if test_id in active_tests:
            raise HTTPException(status_code=202, detail="Test en cours, endpoints pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Test non trouvé")
    
    test_result = completed_tests[test_id]
    
    # Calculer les statistiques par endpoint
    endpoint_stats = {}
    for endpoint in test_result.endpoints_tested:
        endpoint_key = f"{endpoint.method.value} {endpoint.path}"
        endpoint_vulns = [v for v in test_result.vulnerabilities if v.endpoint_path == endpoint.path and v.method == endpoint.method]
        
        endpoint_stats[endpoint_key] = {
            "endpoint": endpoint.dict(),
            "vulnerabilities_count": len(endpoint_vulns),
            "highest_severity": max([v.severity.value for v in endpoint_vulns] + ["info"]),
            "owasp_categories": list(set(v.owasp_category for v in endpoint_vulns if v.owasp_category))
        }
    
    return {
        "test_id": test_id,
        "endpoints_discovered": [ep.dict() for ep in test_result.endpoints_discovered],
        "endpoints_tested": [ep.dict() for ep in test_result.endpoints_tested],
        "endpoint_statistics": endpoint_stats,
        "summary": {
            "total_discovered": len(test_result.endpoints_discovered),
            "total_tested": len(test_result.endpoints_tested),
            "authenticated_endpoints": len([ep for ep in test_result.endpoints_tested if ep.authentication_required]),
            "rate_limited_endpoints": len([ep for ep in test_result.endpoints_tested if ep.rate_limited])
        }
    }

@router.get("/test/{test_id}/metrics")
async def get_test_metrics(test_id: str):
    """Récupère les métriques détaillées d'un test"""
    
    if test_id not in completed_tests:
        if test_id in active_tests:
            raise HTTPException(status_code=202, detail="Test en cours, métriques pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Test non trouvé")
    
    test_result = completed_tests[test_id]
    
    if not test_result.security_metrics:
        return {"test_id": test_id, "error": "Métriques non disponibles"}
    
    metrics = test_result.security_metrics
    
    return {
        "test_id": test_id,
        "security_scores": {
            "overall_security": metrics.security_score,
            "authentication": metrics.authentication_score,
            "authorization": metrics.authorization_score,
            "data_protection": metrics.data_protection_score,
            "rate_limiting": metrics.rate_limiting_score
        },
        "owasp_compliance": metrics.owasp_compliance,
        "endpoint_statistics": {
            "total_tested": metrics.total_endpoints_tested,
            "vulnerable": metrics.vulnerable_endpoints,
            "authenticated": metrics.authenticated_endpoints,
            "rate_limited": metrics.rate_limited_endpoints
        },
        "security_issues": {
            "error_disclosure": metrics.error_disclosure_count,
            "information_leakage": metrics.information_leakage_count,
            "insecure_direct_object_refs": metrics.insecure_direct_object_refs
        },
        "test_coverage": {
            "owasp_categories_tested": len([c for c, compliant in metrics.owasp_compliance.items()]),
            "owasp_compliance_percentage": (len([c for c, compliant in metrics.owasp_compliance.items() if compliant]) / max(1, len(metrics.owasp_compliance))) * 100
        }
    }

@router.get("/test/{test_id}/report")
async def get_test_report(test_id: str, format: str = "json"):
    """Génère le rapport complet de test"""
    
    if test_id not in completed_tests:
        if test_id in active_tests:
            raise HTTPException(status_code=202, detail="Test en cours, rapport pas encore disponible")
        else:
            raise HTTPException(status_code=404, detail="Test non trouvé")
    
    test_result = completed_tests[test_id]
    
    if format == "json":
        return {
            "test_info": {
                "test_id": test_id,
                "api_type": test_result.api_type,
                "base_url": test_result.base_url,
                "test_date": test_result.started_at.isoformat(),
                "duration": test_result.duration,
                "tests_performed": [test.value for test in test_result.tests_performed]
            },
            "executive_summary": {
                "security_score": test_result.security_metrics.security_score if test_result.security_metrics else 0,
                "total_vulnerabilities": test_result.total_vulnerabilities,
                "critical_vulnerabilities": test_result.critical_vulnerabilities,
                "high_vulnerabilities": test_result.high_vulnerabilities,
                "endpoints_tested": len(test_result.endpoints_tested),
                "api_documentation_found": test_result.api_documentation_found
            },
            "vulnerabilities": [vuln.dict() for vuln in test_result.vulnerabilities],
            "endpoints": {
                "discovered": [ep.dict() for ep in test_result.endpoints_discovered],
                "tested": [ep.dict() for ep in test_result.endpoints_tested]
            },
            "security_metrics": test_result.security_metrics.dict() if test_result.security_metrics else None,
            "test_results": test_result.test_results,
            "recommendations": test_result.recommendations,
            "technical_details": {
                "authentication_methods": test_result.authentication_methods,
                "rate_limiting_detected": test_result.rate_limiting_detected,
                "cors_configuration": test_result.cors_configuration,
                "ssl_configuration": test_result.ssl_configuration
            }
        }
    
    elif format == "pdf":
        # En production, générer un PDF avec ReportLab
        raise HTTPException(status_code=501, detail="Export PDF pas encore implémenté")
    
    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json' ou 'pdf'")

@router.get("/tests")
async def list_tests(
    api_type: Optional[str] = None,
    test_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste les tests avec filtres"""
    
    all_tests = []
    
    # Ajouter les tests actifs
    for test_id, test_info in active_tests.items():
        test_data = {
            "test_id": test_id,
            "api_type": test_info["api_type"].value,
            "base_url": test_info["base_url"],
            "status": test_info["status"],
            "start_time": test_info["start_time"],
            "test_suite": [test.value for test in test_info["test_suite"]],
            "duration": (datetime.now() - test_info["start_time"]).total_seconds()
        }
        all_tests.append(test_data)
    
    # Ajouter les tests terminés
    for test_id, test_result in completed_tests.items():
        test_data = {
            "test_id": test_id,
            "api_type": test_result.api_type.value,
            "base_url": test_result.base_url,
            "status": test_result.status,
            "start_time": test_result.started_at,
            "test_suite": [test.value for test in test_result.tests_performed],
            "duration": test_result.duration,
            "endpoints_tested": len(test_result.endpoints_tested),
            "vulnerabilities_found": len(test_result.vulnerabilities),
            "security_score": test_result.security_metrics.security_score if test_result.security_metrics else 0
        }
        all_tests.append(test_data)
    
    # Filtres
    if api_type:
        all_tests = [t for t in all_tests if t["api_type"] == api_type]
    
    if test_type:
        all_tests = [t for t in all_tests if test_type in t["test_suite"]]
    
    if status:
        all_tests = [t for t in all_tests if t["status"] == status]
    
    # Trier par date de début (plus récent en premier)
    all_tests.sort(key=lambda x: x["start_time"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_tests = all_tests[start_idx:end_idx]
    
    return {
        "tests": paginated_tests,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_tests": len(all_tests),
            "total_pages": (len(all_tests) + page_size - 1) // page_size
        },
        "filters_applied": {
            "api_type": api_type,
            "test_type": test_type,
            "status": status
        },
        "summary": {
            "active_tests": len(active_tests),
            "completed_tests": len(completed_tests)
        }
    }

@router.get("/stats")
async def get_api_security_stats():
    """Statistiques détaillées API Security"""
    
    if not completed_tests:
        return {
            "total_tests": 0,
            "total_apis": 0,
            "api_types": {},
            "test_types": {},
            "vulnerabilities": {},
            "owasp_compliance": {}
        }
    
    # Stats générales
    total_apis = len(set(test.base_url for test in completed_tests.values()))
    total_endpoints = sum(len(test.endpoints_tested) for test in completed_tests.values())
    total_vulnerabilities = sum(len(test.vulnerabilities) for test in completed_tests.values())
    
    # Stats par type d'API
    api_types_stats = {}
    test_types_stats = {}
    vulnerability_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    owasp_compliance_stats = {}
    
    security_scores = []
    
    for test in completed_tests.values():
        # Types d'API
        api_types_stats[test.api_type.value] = api_types_stats.get(test.api_type.value, 0) + 1
        
        # Types de tests
        for test_type in test.tests_performed:
            test_types_stats[test_type.value] = test_types_stats.get(test_type.value, 0) + 1
        
        # Vulnérabilités par sévérité
        for vuln in test.vulnerabilities:
            vulnerability_stats[vuln.severity.value] = vulnerability_stats.get(vuln.severity.value, 0) + 1
        
        # OWASP compliance
        if test.security_metrics and test.security_metrics.owasp_compliance:
            for category, compliant in test.security_metrics.owasp_compliance.items():
                if category not in owasp_compliance_stats:
                    owasp_compliance_stats[category] = {"total": 0, "compliant": 0}
                owasp_compliance_stats[category]["total"] += 1
                if compliant:
                    owasp_compliance_stats[category]["compliant"] += 1
        
        # Scores de sécurité
        if test.security_metrics:
            security_scores.append(test.security_metrics.security_score)
    
    avg_security_score = sum(security_scores) / len(security_scores) if security_scores else 0
    
    # Calculer le pourcentage de compliance OWASP
    owasp_compliance_percentage = {}
    for category, stats in owasp_compliance_stats.items():
        owasp_compliance_percentage[category] = (stats["compliant"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    return {
        "total_tests": len(completed_tests),
        "total_apis": total_apis,
        "total_endpoints": total_endpoints,
        "total_vulnerabilities": total_vulnerabilities,
        "api_types": api_types_stats,
        "test_types": test_types_stats,
        "vulnerabilities": vulnerability_stats,
        "owasp_compliance": owasp_compliance_percentage,
        "average_security_score": round(avg_security_score, 1),
        "security_score_distribution": {
            "excellent": len([s for s in security_scores if s >= 90]),
            "good": len([s for s in security_scores if 70 <= s < 90]),
            "average": len([s for s in security_scores if 50 <= s < 70]),
            "poor": len([s for s in security_scores if s < 50])
        },
        "testing_efficiency": {
            "avg_endpoints_per_test": round(total_endpoints / max(1, len(completed_tests)), 1),
            "avg_vulnerabilities_per_test": round(total_vulnerabilities / max(1, len(completed_tests)), 1),
            "avg_test_duration": round(sum(t.duration for t in completed_tests.values()) / max(1, len(completed_tests)), 1)
        }
    }

@router.delete("/test/{test_id}")
async def delete_test(test_id: str):
    """Supprime un test et ses résultats"""
    
    deleted = False
    
    if test_id in active_tests:
        del active_tests[test_id]
        deleted = True
    
    if test_id in completed_tests:
        del completed_tests[test_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Test non trouvé")
    
    return {"message": f"Test {test_id} supprimé avec succès"}

# Fonctions utilitaires

async def execute_api_test(test_id: str, test_request: Dict[str, Any]):
    """Exécute le test de sécurité API en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_tests[test_id]["status"] = "running"
        
        # Exécuter le test
        scanner = APISecurityScanner()
        result = await scanner.test_api_security(test_request)
        
        # Mettre à jour l'ID du résultat
        result.id = test_id
        
        # Mettre à jour les IDs des vulnérabilités
        for vuln in result.vulnerabilities:
            vuln.test_id = test_id
        
        # Déplacer vers les tests terminés
        completed_tests[test_id] = result
        del active_tests[test_id]
        
        # Sauvegarder en base de données si possible
        try:
            db = await get_database()
            await db.save_test_result(result.dict())
        except:
            pass  # Continuer même si la sauvegarde échoue
            
    except Exception as e:
        # Marquer le test comme échoué
        active_tests[test_id]["status"] = "failed"
        active_tests[test_id]["error"] = str(e)
        print(f"Erreur lors du test {test_id}: {e}")

def _estimate_test_duration(request: APISecurityRequest) -> str:
    """Estime la durée du test"""
    base_time = 120  # 2 minutes de base
    
    # Facteurs selon les tests
    time_factors = {
        TestType.OWASP_API_TOP10: 3.0,
        TestType.AUTHENTICATION: 1.5,
        TestType.AUTHORIZATION: 1.5,
        TestType.INJECTION: 2.0,
        TestType.RATE_LIMITING: 2.5,
        TestType.DATA_VALIDATION: 1.0,
        TestType.CORS: 0.5,
        TestType.SSL_TLS: 0.5
    }
    
    total_factor = sum(time_factors.get(test, 1.0) for test in request.test_suite)
    estimated = base_time * total_factor / len(request.test_suite)
    
    # Facteur selon le nombre d'endpoints
    endpoint_count = len(request.endpoints) if request.endpoints else 10
    estimated *= min(2.0, endpoint_count / 10)
    
    if estimated < 60:
        return f"{int(estimated)} secondes"
    elif estimated < 3600:
        return f"{int(estimated/60)} minutes"
    else:
        return f"{round(estimated/3600, 1)} heures"

def _estimate_test_progress(status: str, duration: float) -> int:
    """Estime le pourcentage de progression"""
    if status == "starting":
        return 5
    elif status == "running":
        # Progression basée sur le temps (estimation 5 minutes max)
        return min(95, 10 + int((duration / 300) * 85))
    elif status == "completed":
        return 100
    elif status == "failed":
        return 0
    else:
        return 0

def _get_test_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation du test API...",
        "running": "Test en cours - Analyse de sécurité...",
        "completed": "Test terminé avec succès",
        "failed": "Erreur lors du test"
    }
    return messages.get(status, "Statut inconnu")