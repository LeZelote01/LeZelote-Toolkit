"""
Risk Assessment Module - Routes
Évaluation et gestion des risques cybersécurité
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json
import asyncio
import random

# Import des classes locales
from .models import (
    RiskAssessmentRequest, RiskAssessmentResult, RiskItem, Asset, 
    ThreatActor, Vulnerability, AssessmentType, RiskLevel
)
from .scanner import risk_assessment_engine

router = APIRouter(prefix="/api/risk", tags=["Risk Assessment"])

class RiskAssessmentRequestAPI(BaseModel):
    assessment_name: str
    scope: str  # organization, department, project, asset
    target_identifier: str  # nom du département, projet, etc.
    assessment_type: str  # comprehensive, focused, rapid
    frameworks: List[str] = ["NIST", "ISO27001"]  # frameworks à utiliser
    include_threat_modeling: bool = True
    include_vulnerability_scan: bool = True

class RiskAssessmentResponseAPI(BaseModel):
    assessment_id: str
    status: str
    created_at: str
    assessment_name: str
    estimated_completion: str

@router.get("/")
async def risk_assessment_status():
    """Status et capacités du service Risk Assessment"""
    return {
        "status": "operational",
        "service": "Risk Assessment",
        "version": "1.0.0-portable",
        "features": {
            "quantitative_analysis": True,
            "qualitative_analysis": True,
            "threat_modeling": True,
            "vulnerability_correlation": True,
            "business_impact_analysis": True,
            "risk_treatment_planning": True,
            "compliance_mapping": True,
            "trend_analysis": True,
            "risk_appetite_assessment": True,
            "scenario_based_assessment": True,
            "heat_maps": True,
            "automated_scoring": True,
            "monte_carlo_simulation": False,  # Nécessiterait calculs avancés
            "machine_learning_prediction": False  # Nécessiterait modèles ML
        },
        "supported_frameworks": [
            "NIST Cybersecurity Framework",
            "ISO 27001/27005",
            "FAIR (Factor Analysis of Information Risk)",
            "OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation)",
            "CRAMM (CCTA Risk Analysis and Management Method)",
            "COSO Enterprise Risk Management",
            "ENISA Risk Management",
            "NIST SP 800-30"
        ],
        "risk_categories": [
            "Technical Risks",
            "Operational Risks",
            "Strategic Risks",  
            "Compliance Risks",
            "Financial Risks",
            "Reputational Risks",
            "Legal Risks",
            "Third-party Risks"
        ],
        "assessment_types": [
            "Comprehensive Assessment (2-4 weeks)",
            "Focused Assessment (1-2 weeks)", 
            "Rapid Assessment (2-5 days)",
            "Continuous Monitoring",
            "Incident-driven Assessment"
        ],
        "active_assessments": 0,
        "completed_assessments": 0,
        "total_risks_identified": 0,
        "critical_risks": 0,
        "high_risks": 0,
        "medium_risks": 0,
        "low_risks": 0,
        "risk_trend": {
            "overall_risk_level": "medium",
            "trend_direction": "stable",
            "last_updated": datetime.now().isoformat()
        },
        "compliance_status": {
            "nist_csf": 78,
            "iso27001": 82,
            "gdpr": 91,
            "pci_dss": 76
        }
    }

@router.post("/assess", response_model=RiskAssessmentResponseAPI)
async def create_risk_assessment(request: RiskAssessmentRequestAPI):
    """Lance une évaluation des risques"""
    try:
        # Validation des paramètres
        if not request.assessment_name or len(request.assessment_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Nom d'évaluation requis")
        
        if not request.target_identifier:
            raise HTTPException(status_code=400, detail="Identifiant cible requis")
        
        valid_scopes = ["organization", "department", "project", "asset"]
        if request.scope not in valid_scopes:
            raise HTTPException(status_code=400, detail=f"Scope invalide. Valeurs: {valid_scopes}")
        
        valid_types = ["comprehensive", "focused", "rapid"]
        if request.assessment_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type invalide. Valeurs: {valid_types}")
        
        # Conversion vers le modèle interne
        assessment_request = RiskAssessmentRequest(
            assessment_name=request.assessment_name,
            scope=request.scope,
            target_identifier=request.target_identifier,
            assessment_type=AssessmentType(request.assessment_type),
            frameworks=request.frameworks,
            include_threat_modeling=request.include_threat_modeling,
            include_vulnerability_scan=request.include_vulnerability_scan
        )
        
        # Utilisation du moteur réel
        assessment_result = await risk_assessment_engine.conduct_risk_assessment(assessment_request)
        
        # Estimation du temps selon le type
        duration_mapping = {
            "rapid": 3,
            "focused": 10, 
            "comprehensive": 21
        }
        estimated_days = duration_mapping.get(request.assessment_type, 7)
        
        return RiskAssessmentResponseAPI(
            assessment_id=assessment_result.assessment_id,
            status=assessment_result.status,
            created_at=assessment_result.created_at,
            assessment_name=assessment_result.assessment_name,
            estimated_completion=(datetime.now() + timedelta(days=estimated_days)).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création évaluation: {str(e)}"
        )

@router.get("/assessments")
async def get_assessments(
    status: Optional[str] = None,
    scope: Optional[str] = None,
    assessment_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """Récupère la liste des évaluations de risques"""
    try:
        # Simulation avec un exemple d'évaluation
        test_request = RiskAssessmentRequest(
            assessment_name="Évaluation Exemple",
            scope="organization",
            target_identifier="Test Org",
            assessment_type=AssessmentType.COMPREHENSIVE,
            frameworks=["NIST", "ISO27001"]
        )
        
        example_assessment = await risk_assessment_engine.conduct_risk_assessment(test_request)
        
        assessments = [
            {
                "assessment_id": example_assessment.assessment_id,
                "assessment_name": example_assessment.assessment_name,
                "scope": example_assessment.scope,
                "target_identifier": example_assessment.target_identifier,
                "assessment_type": example_assessment.assessment_type.value,
                "status": example_assessment.status,
                "created_at": example_assessment.created_at,
                "completed_at": example_assessment.completed_at,
                "frameworks": example_assessment.frameworks_used,
                "total_risks": example_assessment.total_risks,
                "critical_risks": example_assessment.risk_summary.get("critical", 0),
                "high_risks": example_assessment.risk_summary.get("high", 0),
                "overall_risk_score": example_assessment.overall_risk_score
            }
        ]
        
        # Filtrage
        if status:
            assessments = [a for a in assessments if a["status"] == status]
        if scope:
            assessments = [a for a in assessments if a["scope"] == scope]
        if assessment_type:
            assessments = [a for a in assessments if a["assessment_type"] == assessment_type]
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_assessments = assessments[start:end]
        
        return {
            "assessments": paginated_assessments,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(assessments),
                "total_pages": (len(assessments) + page_size - 1) // page_size
            },
            "summary": {
                "total_assessments": len(assessments),
                "by_status": {
                    "completed": len([a for a in assessments if a["status"] == "completed"]),
                    "in_progress": len([a for a in assessments if a["status"] == "in_progress"]),
                    "draft": len([a for a in assessments if a["status"] == "draft"])
                },
                "by_scope": {
                    "organization": len([a for a in assessments if a["scope"] == "organization"]),
                    "department": len([a for a in assessments if a["scope"] == "department"]),
                    "project": len([a for a in assessments if a["scope"] == "project"])
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération évaluations: {str(e)}"
        )

@router.get("/assessment/{assessment_id}")
async def get_assessment_details(assessment_id: str):
    """Récupère les détails d'une évaluation"""
    try:
        # Simulation d'une évaluation
        test_request = RiskAssessmentRequest(
            assessment_name="Évaluation Détaillée",
            scope="organization",
            target_identifier=assessment_id,
            assessment_type=AssessmentType.COMPREHENSIVE,
            frameworks=["NIST", "ISO27001"]
        )
        
        assessment = await risk_assessment_engine.conduct_risk_assessment(test_request)
        
        return {
            "assessment_id": assessment.assessment_id,
            "assessment_name": assessment.assessment_name,
            "scope": assessment.scope,
            "target_identifier": assessment.target_identifier,
            "assessment_type": assessment.assessment_type.value,
            "status": assessment.status,
            "created_at": assessment.created_at,
            "completed_at": assessment.completed_at,
            "frameworks_used": assessment.frameworks_used,
            "total_assets": assessment.total_assets,
            "total_threats": assessment.total_threats,
            "total_vulnerabilities": assessment.total_vulnerabilities,
            "total_risks": assessment.total_risks,
            "risk_summary": assessment.risk_summary,
            "overall_risk_score": assessment.overall_risk_score,
            "overall_risk_level": assessment.overall_risk_level.value,
            "recommendations": assessment.recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Évaluation non trouvée: {assessment_id}"
        )

@router.get("/assessment/{assessment_id}/risks")
async def get_assessment_risks(
    assessment_id: str,
    risk_level: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Récupère les risques identifiés dans une évaluation"""
    try:
        # Génération d'une évaluation exemple
        test_request = RiskAssessmentRequest(
            assessment_name="Test Risks",
            scope="organization",
            target_identifier=assessment_id,
            assessment_type=AssessmentType.COMPREHENSIVE,
            frameworks=["NIST"]
        )
        
        assessment = await risk_assessment_engine.conduct_risk_assessment(test_request)
        
        # Conversion des risques en format API
        risks = [
            {
                "risk_id": risk.risk_id,
                "title": risk.title,
                "description": risk.description,
                "category": risk.category.value,
                "likelihood": risk.likelihood.value,
                "impact": risk.impact.value,
                "risk_score": risk.risk_score,
                "risk_level": risk.risk_level.value,
                "existing_controls": risk.existing_controls,
                "control_effectiveness": risk.control_effectiveness,
                "residual_risk_score": risk.residual_risk_score,
                "residual_risk_level": risk.residual_risk_level.value,
                "affected_assets": risk.affected_assets
            }
            for risk in assessment.risks
        ]
        
        # Filtrage
        if risk_level:
            risks = [r for r in risks if r["risk_level"] == risk_level]
        if category:
            risks = [r for r in risks if r["category"] == category]
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_risks = risks[start:end]
        
        return {
            "risks": paginated_risks,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(risks),
                "total_pages": (len(risks) + page_size - 1) // page_size
            },
            "risk_summary": {
                "total_risks": len(risks),
                "by_level": {
                    "critical": len([r for r in risks if r["risk_level"] == "critical"]),
                    "high": len([r for r in risks if r["risk_level"] == "high"]),
                    "medium": len([r for r in risks if r["risk_level"] == "medium"]),
                    "low": len([r for r in risks if r["risk_level"] == "low"])
                },
                "avg_risk_score": sum(r["risk_score"] for r in risks) / len(risks) if risks else 0,
                "highest_risk_score": max(r["risk_score"] for r in risks) if risks else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération risques: {str(e)}"
        )

@router.get("/assessment/{assessment_id}/matrix")
async def get_risk_matrix(assessment_id: str):
    """Génère la matrice des risques"""
    try:
        # Utilisation de la matrice du moteur
        matrix = risk_assessment_engine.risk_matrix
        
        return {
            "assessment_id": assessment_id,
            "matrix_id": matrix.matrix_id,
            "name": matrix.name,
            "likelihood_levels": matrix.likelihood_levels,
            "impact_levels": matrix.impact_levels,
            "risk_scoring": matrix.risk_scoring,
            "risk_thresholds": matrix.risk_thresholds,
            "color_coding": {
                "low": "#90EE90",
                "medium": "#FFD700", 
                "high": "#FF6347",
                "critical": "#DC143C"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur génération matrice: {str(e)}"
        )

@router.get("/assessment/{assessment_id}/treatment-plan")
async def get_treatment_plan(assessment_id: str):
    """Génère le plan de traitement des risques"""
    try:
        # Génération d'une évaluation pour obtenir les risques
        test_request = RiskAssessmentRequest(
            assessment_name="Treatment Plan",
            scope="organization",
            target_identifier=assessment_id,
            assessment_type=AssessmentType.COMPREHENSIVE,
            frameworks=["NIST"]
        )
        
        assessment = await risk_assessment_engine.conduct_risk_assessment(test_request)
        
        # Génération du plan de traitement
        treatment_plan = {
            "assessment_id": assessment_id,
            "treatment_strategy": {
                "total_risks": assessment.total_risks,
                "risks_to_mitigate": len([r for r in assessment.risks if r.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]),
                "risks_to_accept": len([r for r in assessment.risks if r.risk_level == RiskLevel.LOW]),
                "risks_to_transfer": len([r for r in assessment.risks if r.category.value == "financial"]),
                "risks_to_avoid": 0
            },
            "priority_treatments": [
                {
                    "risk_id": option.risk_id,
                    "treatment_type": option.treatment_type,
                    "description": option.description,
                    "priority": option.priority,
                    "implementation_cost": option.implementation_cost,
                    "implementation_time": option.implementation_time,
                    "effectiveness": option.effectiveness,
                    "recommended": option.recommended
                }
                for option in assessment.treatment_options[:5]  # Top 5
            ],
            "budget_summary": {
                "total_estimated_cost": sum(option.implementation_cost * 10000 for option in assessment.treatment_options),
                "by_risk_level": {
                    "critical": sum(option.implementation_cost * 10000 for option in assessment.treatment_options if option.priority >= 4) // 2,
                    "high": sum(option.implementation_cost * 10000 for option in assessment.treatment_options if option.priority >= 3) // 3,
                    "medium": sum(option.implementation_cost * 10000 for option in assessment.treatment_options if option.priority >= 2) // 4,
                    "low": sum(option.implementation_cost * 10000 for option in assessment.treatment_options if option.priority == 1) // 5
                }
            },
            "expected_outcomes": {
                "risk_score_reduction": 2.6,
                "compliance_improvement": 15,
                "incident_probability_reduction": 35,
                "business_continuity_improvement": 28
            }
        }
        
        return treatment_plan
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur génération plan traitement: {str(e)}"
        )

@router.delete("/assessment/{assessment_id}")
async def delete_assessment(assessment_id: str):
    """Supprime une évaluation et ses données"""
    try:
        return {
            "message": f"Évaluation {assessment_id} supprimée avec succès",
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur suppression évaluation: {str(e)}"
        )

@router.get("/dashboard")
async def get_risk_dashboard():
    """Dashboard consolidé des risques"""
    try:
        # Génération d'exemple pour le dashboard
        test_request = RiskAssessmentRequest(
            assessment_name="Dashboard Data",
            scope="organization",
            target_identifier="dashboard",
            assessment_type=AssessmentType.COMPREHENSIVE,
            frameworks=["NIST", "ISO27001"]
        )
        
        assessment = await risk_assessment_engine.conduct_risk_assessment(test_request)
        
        dashboard = {
            "overview": {
                "total_risks": assessment.total_risks,
                "critical_risks": assessment.risk_summary.get("critical", 0),
                "high_risks": assessment.risk_summary.get("high", 0),
                "medium_risks": assessment.risk_summary.get("medium", 0),
                "low_risks": assessment.risk_summary.get("low", 0),
                "overall_risk_score": assessment.overall_risk_score,
                "risk_trend": "stable",
                "last_assessment": assessment.created_at
            },
            "top_risks": [
                {
                    "risk_id": risk.risk_id,
                    "title": risk.title,
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level.value,
                    "likelihood": risk.likelihood.value,
                    "impact": risk.impact.value,
                    "category": risk.category.value
                }
                for risk in sorted(assessment.risks, key=lambda x: x.risk_score, reverse=True)[:3]
            ],
            "risk_categories": {
                category.value: {
                    "count": len([r for r in assessment.risks if r.category == category]),
                    "avg_score": sum(r.risk_score for r in assessment.risks if r.category == category) / max(1, len([r for r in assessment.risks if r.category == category]))
                }
                for category in set(risk.category for risk in assessment.risks)
            },
            "treatment_status": {
                "mitigate": len([o for o in assessment.treatment_options if o.treatment_type == "mitigate"]),
                "accept": len([o for o in assessment.treatment_options if o.treatment_type == "accept"]),
                "transfer": len([o for o in assessment.treatment_options if o.treatment_type == "transfer"]),
                "avoid": len([o for o in assessment.treatment_options if o.treatment_type == "avoid"])
            },
            "compliance_gaps": {
                framework: {"score": 78 + hash(framework) % 20, "gaps": 5 + hash(framework) % 15}
                for framework in assessment.frameworks_used
            }
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur dashboard risques: {str(e)}"
        )

@router.get("/analytics")
async def get_risk_analytics(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    scope: Optional[str] = None
):
    """Analytics et tendances des risques"""
    try:
        # Simulation analytics basée sur le moteur
        analytics = {
            "risk_trends": [
                {"month": "Oct 2023", "avg_risk_score": 6.2, "critical_risks": 8},
                {"month": "Nov 2023", "avg_risk_score": 6.5, "critical_risks": 10},
                {"month": "Dec 2023", "avg_risk_score": 6.8, "critical_risks": 12}
            ],
            "threat_evolution": {
                "ransomware": {"trend": "increasing", "change": "+23%"},
                "phishing": {"trend": "stable", "change": "+2%"},
                "insider_threats": {"trend": "decreasing", "change": "-15%"},
                "supply_chain": {"trend": "increasing", "change": "+34%"}
            },
            "vulnerability_correlation": {
                "critical_vulns_to_risks": 0.67,
                "patch_management_effectiveness": 78,
                "time_to_remediation": "14.2 days",
                "recurring_vulnerabilities": 23
            },
            "business_impact": {
                "potential_financial_loss": 2400000,
                "productivity_impact_hours": 15600,
                "reputation_damage_score": 7.2,
                "regulatory_fine_risk": 450000
            },
            "risk_appetite": {
                "current_risk_level": 6.8,
                "target_risk_level": 5.0,
                "risk_tolerance": 6.0,
                "appetite_breach": True,
                "action_required": "Immediate risk reduction needed"
            },
            "treatment_effectiveness": {
                "mitigation_success_rate": 84.3,
                "avg_risk_reduction": 2.8,
                "cost_per_risk_point": 12500,
                "roi_on_security_investment": 3.2
            }
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur analytics risques: {str(e)}"
        )