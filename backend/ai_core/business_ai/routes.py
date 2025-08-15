"""
Routes FastAPI pour Business AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - IA décisions business et optimisation stratégique
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from .main import (
    business_ai_service,
    BusinessAnalysisRequest, 
    BusinessAnalysisResult,
    BusinessOptimizationRequest,
    BusinessMetric,
    BusinessRecommendation,
    ROICalculation
)

# Configuration du router
router = APIRouter(
    prefix="/api/business-ai",
    tags=["business-ai"],
    responses={404: {"description": "Business AI service not found"}}
)

# Modèles de réponse pour l'API
class BusinessAIStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    analytics_ready: bool
    llm_configured: bool

class BusinessAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    analysis: BusinessAnalysisResult
    execution_time_ms: int

class OptimizationResponse(BaseModel):
    success: bool
    optimization_id: str
    recommendations: List[BusinessRecommendation]
    estimated_savings: Dict[str, float]
    implementation_roadmap: List[str]

class BusinessMetricsResponse(BaseModel):
    success: bool
    metrics: List[BusinessMetric]
    benchmark_comparison: Dict[str, Any]
    trends: Dict[str, str]

@router.get("/", response_model=BusinessAIStatusResponse)
async def business_ai_status():
    """Status du service Business AI"""
    return BusinessAIStatusResponse(
        status="operational",
        service="Business AI - Décisions Stratégiques",
        version="1.0.0-portable",
        features={
            "business_analysis": True,
            "roi_calculation": True,
            "strategic_recommendations": True,
            "risk_assessment": True,
            "growth_opportunities": True,
            "optimization_algorithms": True,
            "industry_benchmarks": True,
            "predictive_insights": True
        },
        analytics_ready=True,
        llm_configured=business_ai_service.llm_client is not None
    )

@router.post("/analyze", response_model=BusinessAnalysisResponse)
async def analyze_business(request: BusinessAnalysisRequest):
    """Analyse business complète avec IA stratégique"""
    try:
        start_time = datetime.now()
        
        # Validation des paramètres
        if not request.business_context:
            raise HTTPException(status_code=400, detail="Contexte business requis")
        
        if request.analysis_type not in ["performance", "roi", "risk_business", "optimization"]:
            raise HTTPException(
                status_code=400, 
                detail="Type d'analyse invalide. Options: performance, roi, risk_business, optimization"
            )
        
        # Exécution de l'analyse business
        analysis_result = await business_ai_service.analyze_business(request)
        
        # Calcul du temps d'exécution
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BusinessAnalysisResponse(
            success=True,
            analysis_id=analysis_result.analysis_id,
            analysis=analysis_result,
            execution_time_ms=int(execution_time)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse business: {str(e)}"
        )

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_business(request: BusinessOptimizationRequest):
    """Optimisation business avec recommandations IA"""
    try:
        # Validation des paramètres
        if not request.current_situation:
            raise HTTPException(status_code=400, detail="Situation actuelle requise")
        
        if request.optimization_area not in ["costs", "processes", "security_spending", "resource_allocation"]:
            raise HTTPException(
                status_code=400,
                detail="Zone d'optimisation invalide. Options: costs, processes, security_spending, resource_allocation"
            )
        
        # Génération des recommandations d'optimisation
        recommendations = await business_ai_service._generate_optimization_recommendations(request)
        
        # Calcul des économies estimées
        estimated_savings = await business_ai_service._calculate_optimization_savings(request, recommendations)
        
        # Génération du roadmap d'implémentation
        implementation_roadmap = await business_ai_service._generate_implementation_roadmap(recommendations)
        
        return OptimizationResponse(
            success=True,
            optimization_id=f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            recommendations=recommendations,
            estimated_savings=estimated_savings,
            implementation_roadmap=implementation_roadmap
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'optimisation business: {str(e)}"
        )

@router.get("/metrics", response_model=BusinessMetricsResponse)
async def get_business_metrics():
    """Récupère les métriques business actuelles avec benchmarks"""
    try:
        # Collecte des métriques actuelles
        current_metrics = await business_ai_service._collect_business_metrics(
            BusinessAnalysisRequest(
                analysis_type="performance",
                business_context={"type": "metrics_only"}
            )
        )
        
        # Comparaison avec benchmarks industrie
        benchmark_comparison = business_ai_service._compare_with_benchmarks(current_metrics)
        
        # Analyse des tendances
        trends = business_ai_service._analyze_metric_trends(current_metrics)
        
        return BusinessMetricsResponse(
            success=True,
            metrics=current_metrics,
            benchmark_comparison=benchmark_comparison,
            trends=trends
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.get("/roi-scenarios")
async def get_roi_scenarios():
    """Calcule différents scénarios ROI pour investissements"""
    try:
        # Création d'une requête factice pour les calculs ROI
        dummy_request = BusinessAnalysisRequest(
            analysis_type="roi",
            business_context={"type": "roi_scenarios"}
        )
        
        # Récupération des métriques pour les calculs
        metrics = await business_ai_service._collect_business_metrics(dummy_request)
        
        # Calcul des scénarios ROI
        roi_scenarios = await business_ai_service._calculate_roi_scenarios(dummy_request, metrics)
        
        return {
            "success": True,
            "roi_scenarios": [scenario.dict() for scenario in roi_scenarios],
            "total_scenarios": len(roi_scenarios),
            "best_roi": max(roi_scenarios, key=lambda x: x.roi_percentage).dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des scénarios ROI: {str(e)}"
        )

@router.get("/growth-opportunities")
async def get_growth_opportunities():
    """Identifie les opportunités de croissance business"""
    try:
        # Création d'une requête pour l'analyse de croissance
        growth_request = BusinessAnalysisRequest(
            analysis_type="performance",
            business_context={"focus": "growth_opportunities"}
        )
        
        metrics = await business_ai_service._collect_business_metrics(growth_request)
        growth_opportunities = await business_ai_service._identify_growth_opportunities(growth_request, metrics)
        
        return {
            "success": True,
            "opportunities": growth_opportunities,
            "total_opportunities": len(growth_opportunities),
            "priority_opportunities": growth_opportunities[:3]  # Top 3
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'identification des opportunités: {str(e)}"
        )

@router.get("/risk-assessment")
async def get_risk_assessment():
    """Évaluation des risques business avec recommandations"""
    try:
        # Création d'une requête pour l'évaluation des risques
        risk_request = BusinessAnalysisRequest(
            analysis_type="risk_business",
            business_context={"focus": "risk_assessment"}
        )
        
        metrics = await business_ai_service._collect_business_metrics(risk_request)
        risk_assessment = await business_ai_service._assess_business_risks(risk_request, metrics)
        
        return {
            "success": True,
            "risk_assessment": risk_assessment,
            "critical_risks": [risk for risk in risk_assessment["key_risks"] if risk["severity"] == "high"],
            "mitigation_priority": risk_assessment["recommended_actions"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'évaluation des risques: {str(e)}"
        )

@router.get("/benchmarks/{category}")
async def get_industry_benchmarks(category: str):
    """Récupère les benchmarks industrie pour une catégorie"""
    try:
        valid_categories = ["cybersecurity_consulting", "security_auditing", "incident_response", "training_services"]
        
        if category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Catégorie invalide. Options: {', '.join(valid_categories)}"
            )
        
        benchmarks = business_ai_service.industry_benchmarks.get(category, {})
        
        return {
            "success": True,
            "category": category,
            "benchmarks": benchmarks,
            "last_updated": "2025-01-01"  # Date de référence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des benchmarks: {str(e)}"
        )

@router.post("/insights/generate")
async def generate_custom_insights(
    context: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Génère des insights business personnalisés"""
    try:
        # Validation du contexte
        if not context or "focus_area" not in context:
            raise HTTPException(
                status_code=400,
                detail="Contexte avec focus_area requis"
            )
        
        # Création d'une requête d'analyse personnalisée
        custom_request = BusinessAnalysisRequest(
            analysis_type="performance",
            business_context=context
        )
        
        metrics = await business_ai_service._collect_business_metrics(custom_request)
        
        # Calcul du score de santé business
        risk_assessment = await business_ai_service._assess_business_risks(custom_request, metrics)
        health_score = business_ai_service._calculate_business_health_score(metrics, risk_assessment)
        
        # Génération des insights personnalisés
        custom_insights = await business_ai_service._generate_business_insights(
            custom_request, metrics, health_score
        )
        
        return {
            "success": True,
            "insights": custom_insights,
            "health_score": health_score,
            "context": context,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération d'insights: {str(e)}"
        )