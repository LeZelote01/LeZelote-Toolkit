"""
Routes API pour le service Compliance
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, date, timedelta

from .models import (
    ComplianceAssessment, ComplianceControl, ComplianceGap, ComplianceReport,
    ComplianceFramework, ComplianceStatus, AssessmentType, ControlCategory,
    RiskLevel, ComplianceRequest, AuditEvidence, RemediationAction
)
from .compliance_engine import ComplianceEngine
from database import get_database

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

# Instance du moteur de conformité
compliance_engine = ComplianceEngine()

# Cache des évaluations et contrôles actifs
active_assessments: Dict[str, ComplianceAssessment] = {}
active_controls: Dict[str, ComplianceControl] = {}
active_gaps: Dict[str, ComplianceGap] = {}


@router.get("/")
async def compliance_status():
    """Status du service Compliance"""
    return {
        "status": "operational",
        "service": "Compliance Management",
        "version": "1.0.0-portable",
        "features": {
            "multi_framework_assessment": True,
            "automated_evaluation": True,
            "gap_analysis": True,
            "remediation_planning": True,
            "continuous_monitoring": True,
            "report_generation": True,
            "evidence_management": True,
            "regulatory_updates": True
        },
        "supported_frameworks": [fw.value for fw in ComplianceFramework],
        "assessment_types": [at.value for at in AssessmentType],
        "active_assessments": len(active_assessments),
        "tracked_controls": len(active_controls),
        "open_gaps": len([g for g in active_gaps.values() if g.status == "open"])
    }


@router.get("/frameworks")
async def list_frameworks():
    """Liste les frameworks de conformité supportés"""
    
    frameworks_info = {
        ComplianceFramework.GDPR: {
            "name": "Règlement Général sur la Protection des Données",
            "version": "2018",
            "scope": "Protection des données personnelles",
            "jurisdiction": "Union Européenne",
            "control_count": 50,
            "assessment_frequency": "Annual"
        },
        ComplianceFramework.ISO27001: {
            "name": "ISO/IEC 27001",
            "version": "2013",
            "scope": "Systèmes de management de la sécurité de l'information",
            "jurisdiction": "International",
            "control_count": 114,
            "assessment_frequency": "Annual"
        },
        ComplianceFramework.NIST: {
            "name": "NIST Cybersecurity Framework",
            "version": "1.1",
            "scope": "Cybersécurité organisationnelle",
            "jurisdiction": "États-Unis",
            "control_count": 108,
            "assessment_frequency": "Continuous"
        },
        ComplianceFramework.SOC2: {
            "name": "SOC 2 Type II",
            "version": "2017",
            "scope": "Contrôles de sécurité pour les services",
            "jurisdiction": "États-Unis",
            "control_count": 64,
            "assessment_frequency": "Annual"
        },
        ComplianceFramework.PCI_DSS: {
            "name": "Payment Card Industry Data Security Standard",
            "version": "4.0",
            "scope": "Sécurité des données de cartes de paiement",
            "jurisdiction": "Global",
            "control_count": 300,
            "assessment_frequency": "Annual"
        }
    }
    
    return {
        "frameworks": {fw.value: info for fw, info in frameworks_info.items()},
        "total_frameworks": len(frameworks_info),
        "recommended_combinations": [
            {"name": "GDPR + ISO 27001", "use_case": "Organisations européennes"},
            {"name": "NIST + SOC 2", "use_case": "Fournisseurs de services US"},
            {"name": "ISO 27001 + PCI DSS", "use_case": "E-commerce et paiements"}
        ]
    }


@router.post("/assessment")
async def create_assessment(assessment_request: ComplianceRequest, background_tasks: BackgroundTasks):
    """Crée une nouvelle évaluation de conformité"""
    try:
        # Convertir les données de la requête
        assessment_data = {
            'name': assessment_request.name,
            'description': f"Évaluation {', '.join([fw.value for fw in assessment_request.frameworks])}",
            'frameworks': [fw.value for fw in assessment_request.frameworks],
            'assessment_type': assessment_request.assessment_type.value,
            'scope': assessment_request.scope,
            'start_date': assessment_request.planned_start,
            'planned_completion': assessment_request.planned_completion,
            'lead_assessor': assessment_request.lead_assessor,
            'team_members': []
        }
        
        # Créer l'évaluation
        assessment = await compliance_engine.create_assessment(assessment_data)
        
        # Stocker en cache
        active_assessments[assessment.id] = assessment
        
        # Générer les contrôles en arrière-plan
        background_tasks.add_task(generate_controls_for_assessment, assessment.id)
        
        return {
            "status": "success",
            "message": f"Évaluation '{assessment.name}' créée avec succès",
            "assessment": {
                "id": assessment.id,
                "name": assessment.name,
                "frameworks": [fw.value for fw in assessment.frameworks],
                "assessment_type": assessment.assessment_type.value,
                "start_date": assessment.start_date.isoformat(),
                "planned_completion": assessment.planned_completion.isoformat(),
                "estimated_controls": len(assessment.controls_assessed)
            },
            "next_steps": [
                "1. Les contrôles sont en cours de génération",
                "2. Lancer l'évaluation avec /assessment/{assessment_id}/start",
                "3. Surveiller le progrès avec /assessment/{assessment_id}/status",
                "4. Générer le rapport final une fois terminé"
            ],
            "recommendations": [
                f"Prévoir {len(assessment.frameworks) * 5} jours pour l'évaluation complète",
                "Rassembler la documentation des politiques existantes",
                "Coordonner avec les équipes techniques concernées"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création évaluation: {str(e)}")


@router.get("/assessment/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Récupère les détails d'une évaluation"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    assessment = active_assessments[assessment_id]
    
    # Récupérer les contrôles associés
    assessment_controls = [c for c in active_controls.values() 
                          if c.id in assessment.controls_assessed]
    
    # Calculer les statistiques
    total_controls = len(assessment_controls)
    assessed_controls = len([c for c in assessment_controls 
                           if c.status != ComplianceStatus.NOT_ASSESSED])
    compliant_controls = len([c for c in assessment_controls 
                            if c.status == ComplianceStatus.COMPLIANT])
    
    return {
        "assessment": assessment.dict(),
        "progress": {
            "total_controls": total_controls,
            "assessed_controls": assessed_controls,
            "compliant_controls": compliant_controls,
            "assessment_progress": f"{assessed_controls}/{total_controls}",
            "compliance_rate": f"{compliant_controls}/{total_controls}" if total_controls > 0 else "0/0"
        },
        "statistics": {
            "frameworks_count": len(assessment.frameworks),
            "average_compliance_score": assessment.overall_score if assessment.overall_score else 0,
            "estimated_completion": assessment.planned_completion.isoformat(),
            "days_remaining": (assessment.planned_completion - date.today()).days
        }
    }


@router.post("/assessment/{assessment_id}/start")
async def start_assessment(assessment_id: str, background_tasks: BackgroundTasks):
    """Lance l'évaluation automatisée"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    assessment = active_assessments[assessment_id]
    
    if assessment.status != "planning":
        raise HTTPException(status_code=400, detail=f"Évaluation déjà en cours (statut: {assessment.status})")
    
    try:
        # Récupérer les contrôles
        assessment_controls = [c for c in active_controls.values() 
                              if c.id in assessment.controls_assessed]
        
        if not assessment_controls:
            raise HTTPException(status_code=400, detail="Aucun contrôle trouvé pour cette évaluation")
        
        # Lancer l'évaluation en arrière-plan
        background_tasks.add_task(run_automated_assessment, assessment_id, assessment_controls)
        
        return {
            "status": "started",
            "message": f"Évaluation '{assessment.name}' lancée avec succès",
            "details": {
                "assessment_id": assessment_id,
                "controls_to_assess": len(assessment_controls),
                "estimated_duration": f"{len(assessment_controls) * 2} minutes",
                "frameworks": [fw.value for fw in assessment.frameworks]
            },
            "monitoring": {
                "status_endpoint": f"/assessment/{assessment_id}/status",
                "progress_endpoint": f"/assessment/{assessment_id}/progress",
                "results_endpoint": f"/assessment/{assessment_id}/results"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lancement évaluation: {str(e)}")


@router.get("/assessment/{assessment_id}/progress")
async def get_assessment_progress(assessment_id: str):
    """Récupère le progrès de l'évaluation en temps réel"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    assessment = active_assessments[assessment_id]
    
    # Récupérer les contrôles et leur statut
    assessment_controls = [c for c in active_controls.values() 
                          if c.id in assessment.controls_assessed]
    
    by_status = {}
    by_framework = {}
    
    for control in assessment_controls:
        # Par statut
        status = control.status.value
        by_status[status] = by_status.get(status, 0) + 1
        
        # Par framework
        framework = control.framework.value
        if framework not in by_framework:
            by_framework[framework] = {'total': 0, 'assessed': 0, 'compliant': 0}
        
        by_framework[framework]['total'] += 1
        if control.status != ComplianceStatus.NOT_ASSESSED:
            by_framework[framework]['assessed'] += 1
        if control.status == ComplianceStatus.COMPLIANT:
            by_framework[framework]['compliant'] += 1
    
    return {
        "assessment_id": assessment_id,
        "status": assessment.status,
        "progress_percentage": int(assessment.progress_percentage * 100),
        "overall_score": assessment.overall_score,
        "control_statistics": by_status,
        "framework_breakdown": by_framework,
        "current_phase": _determine_assessment_phase(assessment),
        "estimated_completion": assessment.planned_completion.isoformat(),
        "last_updated": assessment.updated_at.isoformat()
    }


@router.get("/assessment/{assessment_id}/results")
async def get_assessment_results(assessment_id: str):
    """Récupère les résultats détaillés de l'évaluation"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    assessment = active_assessments[assessment_id]
    
    if assessment.status != "completed":
        raise HTTPException(status_code=400, detail=f"Évaluation pas encore terminée (statut: {assessment.status})")
    
    # Récupérer tous les contrôles évalués
    assessment_controls = [c for c in active_controls.values() 
                          if c.id in assessment.controls_assessed]
    
    # Organiser les résultats
    results_by_framework = {}
    critical_findings = []
    
    for control in assessment_controls:
        framework = control.framework.value
        if framework not in results_by_framework:
            results_by_framework[framework] = {
                'controls': [],
                'compliance_rate': 0,
                'average_score': 0
            }
        
        control_result = {
            'control_id': control.control_id,
            'title': control.title,
            'status': control.status.value,
            'score': control.compliance_score,
            'gaps': control.gaps_identified,
            'remediation_priority': control.remediation_priority.value if control.remediation_priority else 'low'
        }
        
        results_by_framework[framework]['controls'].append(control_result)
        
        # Identifier les découvertes critiques
        if control.remediation_priority in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            critical_findings.append({
                'framework': framework,
                'control_id': control.control_id,
                'title': control.title,
                'priority': control.remediation_priority.value,
                'gaps': control.gaps_identified
            })
    
    # Calculer les moyennes par framework
    for framework_data in results_by_framework.values():
        controls = framework_data['controls']
        compliant_count = len([c for c in controls if c['status'] == 'compliant'])
        total_score = sum(c['score'] for c in controls)
        
        framework_data['compliance_rate'] = (compliant_count / len(controls)) * 100 if controls else 0
        framework_data['average_score'] = (total_score / len(controls)) * 100 if controls else 0
    
    return {
        "assessment_summary": {
            "id": assessment_id,
            "name": assessment.name,
            "status": assessment.status,
            "overall_score": int(assessment.overall_score * 100) if assessment.overall_score else 0,
            "compliance_percentage": int(assessment.compliance_percentage * 100) if assessment.compliance_percentage else 0,
            "completion_date": assessment.end_date.isoformat() if assessment.end_date else None
        },
        "results_by_framework": results_by_framework,
        "critical_findings": critical_findings,
        "key_recommendations": assessment.recommendations,
        "next_actions": [
            "Examiner en détail les découvertes critiques",
            "Créer un plan de remédiation prioritaire",
            "Planifier les actions correctives",
            "Programmer la prochaine évaluation"
        ]
    }


@router.post("/assessment/{assessment_id}/report")
async def generate_compliance_report(assessment_id: str, format: str = "json", include_details: bool = True):
    """Génère un rapport de conformité"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    assessment = active_assessments[assessment_id]
    assessment_controls = [c for c in active_controls.values() 
                          if c.id in assessment.controls_assessed]
    
    try:
        report = await compliance_engine.generate_compliance_report(assessment, assessment_controls)
        
        if format.lower() == "json":
            return {
                "status": "success",
                "message": "Rapport de conformité généré",
                "report": report.dict(),
                "export_options": {
                    "pdf": f"/reports/compliance/{report.id}.pdf",
                    "html": f"/reports/compliance/{report.id}.html",
                    "xlsx": f"/reports/compliance/{report.id}.xlsx"
                }
            }
        
        return {
            "status": "success",
            "message": f"Rapport généré au format {format}",
            "report_id": report.id,
            "download_url": f"/reports/compliance/{report.id}.{format}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")


@router.get("/controls")
async def list_controls(
    framework: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Liste les contrôles de conformité avec filtres"""
    
    controls_list = []
    
    for control in list(active_controls.values())[:limit]:
        # Appliquer les filtres
        if framework and control.framework.value != framework:
            continue
        if status and control.status.value != status:
            continue
        if category and control.category.value != category:
            continue
        
        controls_list.append({
            "id": control.id,
            "control_id": control.control_id,
            "title": control.title,
            "framework": control.framework.value,
            "category": control.category.value,
            "status": control.status.value,
            "compliance_score": int(control.compliance_score * 100),
            "last_assessment": control.last_assessment_date.isoformat() if control.last_assessment_date else None,
            "remediation_priority": control.remediation_priority.value if control.remediation_priority else None,
            "gaps_count": len(control.gaps_identified)
        })
    
    return {
        "controls": controls_list,
        "total_returned": len(controls_list),
        "filters_applied": {
            "framework": framework,
            "status": status,
            "category": category,
            "limit": limit
        },
        "summary": {
            "total_controls": len(active_controls),
            "by_framework": _get_controls_by_framework(),
            "by_status": _get_controls_by_status()
        }
    }


@router.get("/control/{control_id}")
async def get_control_details(control_id: str):
    """Récupère les détails d'un contrôle spécifique"""
    if control_id not in active_controls:
        raise HTTPException(status_code=404, detail="Contrôle non trouvé")
    
    control = active_controls[control_id]
    
    return {
        "control": control.dict(),
        "assessment_history": [
            {
                "date": control.last_assessment_date.isoformat() if control.last_assessment_date else None,
                "assessor": control.assessor,
                "status": control.status.value,
                "score": int(control.compliance_score * 100)
            }
        ],
        "remediation_info": {
            "gaps_identified": len(control.gaps_identified),
            "priority": control.remediation_priority.value if control.remediation_priority else "low",
            "deadline": control.remediation_deadline.isoformat() if control.remediation_deadline else None,
            "actions_suggested": len(control.remediation_actions)
        },
        "related_info": {
            "framework_requirements": f"Voir documentation {control.framework.value}",
            "implementation_guidance": "Consulter les bonnes pratiques du framework",
            "similar_controls": "Rechercher contrôles similaires avec /controls"
        }
    }


@router.post("/control/{control_id}/assess")
async def assess_control(control_id: str, assessment_data: Dict[str, Any]):
    """Évalue manuellement un contrôle spécifique"""
    if control_id not in active_controls:
        raise HTTPException(status_code=404, detail="Contrôle non trouvé")
    
    control = active_controls[control_id]
    
    try:
        # Mettre à jour le contrôle avec les données d'évaluation
        updated_control = await compliance_engine.assess_control(control, assessment_data)
        active_controls[control_id] = updated_control
        
        return {
            "status": "success",
            "message": f"Contrôle {control.control_id} évalué avec succès",
            "results": {
                "control_id": control.control_id,
                "new_status": updated_control.status.value,
                "compliance_score": int(updated_control.compliance_score * 100),
                "gaps_identified": len(updated_control.gaps_identified),
                "remediation_priority": updated_control.remediation_priority.value if updated_control.remediation_priority else "low"
            },
            "next_steps": updated_control.remediation_actions if updated_control.remediation_actions else [
                "Contrôle conforme - maintenir l'état actuel",
                "Programmer la prochaine évaluation",
                "Documenter les bonnes pratiques"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur évaluation contrôle: {str(e)}")


@router.get("/gaps")
async def list_compliance_gaps(priority: Optional[str] = None, framework: Optional[str] = None):
    """Liste les lacunes de conformité"""
    
    gaps_list = []
    
    for gap in active_gaps.values():
        # Appliquer les filtres
        if priority and gap.risk_level.value != priority:
            continue
        if framework and gap.framework.value != framework:
            continue
        
        gaps_list.append({
            "id": gap.id,
            "title": gap.title,
            "control_id": gap.control_id,
            "framework": gap.framework.value,
            "risk_level": gap.risk_level.value,
            "status": gap.status,
            "assigned_to": gap.assigned_to,
            "target_date": gap.target_resolution_date.isoformat() if gap.target_resolution_date else None,
            "days_overdue": (date.today() - gap.target_resolution_date).days if gap.target_resolution_date and gap.target_resolution_date < date.today() else 0
        })
    
    # Trier par priorité et date
    gaps_list.sort(key=lambda x: (
        {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['risk_level'], 4),
        x['days_overdue']
    ), reverse=True)
    
    return {
        "gaps": gaps_list,
        "summary": {
            "total_gaps": len(gaps_list),
            "by_priority": _get_gaps_by_priority(),
            "overdue_gaps": len([g for g in gaps_list if g['days_overdue'] > 0])
        },
        "urgent_actions": [
            f"{len([g for g in gaps_list if g['risk_level'] == 'critical'])} lacunes critiques à traiter immédiatement",
            f"{len([g for g in gaps_list if g['days_overdue'] > 0])} lacunes en retard nécessitent une attention",
            "Prioriser les lacunes par risque et impact business"
        ]
    }


@router.get("/dashboard")
async def get_compliance_dashboard():
    """Tableau de bord de conformité"""
    
    # Statistiques globales
    total_controls = len(active_controls)
    compliant_controls = len([c for c in active_controls.values() 
                            if c.status == ComplianceStatus.COMPLIANT])
    critical_gaps = len([g for g in active_gaps.values() 
                        if g.risk_level == RiskLevel.CRITICAL])
    
    # Conformité par framework
    framework_compliance = {}
    for control in active_controls.values():
        framework = control.framework.value
        if framework not in framework_compliance:
            framework_compliance[framework] = {'total': 0, 'compliant': 0}
        
        framework_compliance[framework]['total'] += 1
        if control.status == ComplianceStatus.COMPLIANT:
            framework_compliance[framework]['compliant'] += 1
    
    # Calcul des pourcentages
    for framework_data in framework_compliance.values():
        framework_data['percentage'] = int(
            (framework_data['compliant'] / framework_data['total']) * 100
        ) if framework_data['total'] > 0 else 0
    
    # Prochaines échéances
    upcoming_assessments = []
    for control in active_controls.values():
        if control.next_assessment_due and control.next_assessment_due <= date.today() + timedelta(days=30):
            upcoming_assessments.append({
                'control_id': control.control_id,
                'title': control.title,
                'due_date': control.next_assessment_due.isoformat(),
                'days_until_due': (control.next_assessment_due - date.today()).days
            })
    
    return {
        "overview": {
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "compliance_percentage": int((compliant_controls / total_controls) * 100) if total_controls > 0 else 0,
            "critical_gaps": critical_gaps,
            "active_assessments": len([a for a in active_assessments.values() if a.status == "in_progress"])
        },
        "framework_compliance": framework_compliance,
        "upcoming_assessments": sorted(upcoming_assessments, key=lambda x: x['days_until_due'])[:10],
        "priority_actions": [
            f"Traiter {critical_gaps} lacunes critiques" if critical_gaps > 0 else "Aucune lacune critique",
            f"{len(upcoming_assessments)} évaluations dues dans les 30 prochains jours",
            "Maintenir la documentation de conformité à jour"
        ],
        "recommendations": [
            "Planifier des revues trimestrielles de conformité",
            "Automatiser la collecte de preuves quand possible",
            "Former les équipes sur les exigences réglementaires"
        ]
    }


@router.get("/statistics")
async def get_compliance_statistics():
    """Statistiques détaillées de conformité"""
    
    # Calculs des statistiques
    controls_by_framework = _get_controls_by_framework()
    controls_by_status = _get_controls_by_status()
    gaps_by_priority = _get_gaps_by_priority()
    
    assessments_stats = {
        'total': len(active_assessments),
        'completed': len([a for a in active_assessments.values() if a.status == "completed"]),
        'in_progress': len([a for a in active_assessments.values() if a.status == "in_progress"]),
        'planned': len([a for a in active_assessments.values() if a.status == "planning"])
    }
    
    return {
        "controls_statistics": {
            "total": len(active_controls),
            "by_framework": controls_by_framework,
            "by_status": controls_by_status,
            "by_category": _get_controls_by_category()
        },
        "assessments_statistics": assessments_stats,
        "gaps_statistics": {
            "total": len(active_gaps),
            "by_priority": gaps_by_priority,
            "by_status": _get_gaps_by_status()
        },
        "trends": {
            "compliance_trend": "stable",  # À implémenter avec des données historiques
            "gap_resolution_rate": 65,    # Pourcentage moyen de résolution
            "average_assessment_duration": 14  # Jours moyens
        }
    }


# Tâches en arrière-plan

async def generate_controls_for_assessment(assessment_id: str):
    """Génère les contrôles pour une évaluation (tâche en arrière-plan)"""
    try:
        assessment = active_assessments[assessment_id]
        
        # Générer les contrôles pour chaque framework
        all_controls = []
        for framework in assessment.frameworks:
            controls = await compliance_engine._get_framework_controls(framework, assessment.scope)
            all_controls.extend(controls)
        
        # Stocker les contrôles
        for control in all_controls:
            active_controls[control.id] = control
        
        # Mettre à jour l'évaluation
        assessment.controls_assessed = [c.id for c in all_controls]
        assessment.updated_at = datetime.now()
        
    except Exception as e:
        print(f"Erreur génération contrôles pour évaluation {assessment_id}: {e}")


async def run_automated_assessment(assessment_id: str, controls: List[ComplianceControl]):
    """Exécute une évaluation automatisée (tâche en arrière-plan)"""
    try:
        assessment = active_assessments[assessment_id]
        
        # Lancer l'évaluation
        updated_assessment = await compliance_engine.run_assessment(assessment, controls)
        
        # Mettre à jour les contrôles
        for control in controls:
            active_controls[control.id] = control
        
        # Mettre à jour l'évaluation
        active_assessments[assessment_id] = updated_assessment
        
        # Créer des lacunes pour les contrôles non conformes
        await create_gaps_from_controls(controls, assessment_id)
        
    except Exception as e:
        print(f"Erreur évaluation automatisée {assessment_id}: {e}")
        # Marquer l'évaluation comme échouée
        assessment = active_assessments[assessment_id]
        assessment.status = "failed"
        assessment.updated_at = datetime.now()


async def create_gaps_from_controls(controls: List[ComplianceControl], assessment_id: str):
    """Crée des lacunes basées sur les contrôles non conformes"""
    for control in controls:
        if control.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
            gap_id = str(uuid.uuid4())
            
            gap = ComplianceGap(
                id=gap_id,
                control_id=control.control_id,
                framework=control.framework,
                title=f"Lacune - {control.title}",
                description=f"Le contrôle {control.control_id} n'est pas en conformité",
                gap_type="implementation_gap",
                risk_level=control.remediation_priority,
                impact_description=f"Non-conformité au contrôle {control.control_id}",
                likelihood="probable",
                remediation_plan="\n".join(control.remediation_actions),
                assigned_to="compliance_team",
                identified_by="automated_assessment"
            )
            
            active_gaps[gap_id] = gap


# Fonctions utilitaires

def _determine_assessment_phase(assessment: ComplianceAssessment) -> str:
    """Détermine la phase actuelle de l'évaluation"""
    if assessment.status == "planning":
        return "Planification et préparation"
    elif assessment.status == "in_progress":
        if assessment.progress_percentage < 0.3:
            return "Évaluation des contrôles techniques"
        elif assessment.progress_percentage < 0.7:
            return "Évaluation des contrôles administratifs"
        else:
            return "Finalisation et synthèse"
    elif assessment.status == "completed":
        return "Évaluation terminée"
    else:
        return "Phase inconnue"


def _get_controls_by_framework() -> Dict[str, int]:
    """Compte les contrôles par framework"""
    by_framework = {}
    for control in active_controls.values():
        framework = control.framework.value
        by_framework[framework] = by_framework.get(framework, 0) + 1
    return by_framework


def _get_controls_by_status() -> Dict[str, int]:
    """Compte les contrôles par statut"""
    by_status = {}
    for control in active_controls.values():
        status = control.status.value
        by_status[status] = by_status.get(status, 0) + 1
    return by_status


def _get_controls_by_category() -> Dict[str, int]:
    """Compte les contrôles par catégorie"""
    by_category = {}
    for control in active_controls.values():
        category = control.category.value
        by_category[category] = by_category.get(category, 0) + 1
    return by_category


def _get_gaps_by_priority() -> Dict[str, int]:
    """Compte les lacunes par priorité"""
    by_priority = {}
    for gap in active_gaps.values():
        priority = gap.risk_level.value
        by_priority[priority] = by_priority.get(priority, 0) + 1
    return by_priority


def _get_gaps_by_status() -> Dict[str, int]:
    """Compte les lacunes par statut"""
    by_status = {}
    for gap in active_gaps.values():
        status = gap.status
        by_status[status] = by_status.get(status, 0) + 1
    return by_status