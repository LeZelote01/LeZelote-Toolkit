"""
Routes FastAPI pour Audit Automatisé
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date

from .models import (
    AuditStatusResponse, Audit, Asset, AuditScope, Finding, RemediationPlan, ComplianceSnapshot,
    AuditFramework, AuditType, AuditStatus, FindingSeverity, FindingStatus, RemediationStatus, AssetType,
    CreateAuditRequest, UpdateAuditRequest, CreateAssetRequest, CreateScopeRequest,
    CreateFindingRequest, UpdateFindingRequest, CreateRemediationPlanRequest,
    AuditSearchRequest, FindingSearchRequest, AuditStatistics, FindingStatistics
)
from .audit_engine import AuditEngine

router = APIRouter(prefix="/api/audit", tags=["Audit Automatisé"])

# Instance globale du moteur
engine = AuditEngine()

@router.get("/", response_model=dict)
async def audit_status():
    """Status du service Audit Automatisé"""
    try:
        status = engine.get_engine_status()
        
        return {
            "status": "operational",
            "service": "Audit Automatisé",
            "version": "1.0.0-portable",
            "description": "Audits multi-frameworks automatisés avec compliance continue",
            "features": {
                "multi_framework_audits": True,
                "automated_testing": True,
                "compliance_monitoring": True,
                "finding_management": True,
                "remediation_planning": True,
                "risk_assessment": True,
                "report_generation": True,
                "continuous_compliance": True
            },
            "engine_status": status,
            "supported_frameworks": [
                "ISO 27001:2022", "NIST Cybersecurity Framework", 
                "CIS Controls v8", "PCI DSS v4.0"
            ],
            "capabilities": {
                "audit_types": ["External", "Internal", "Compliance", "Risk Assessment"],
                "test_methods": ["Automated Scan", "Configuration Check", "Document Review", "Manual Review"],
                "finding_severities": ["Critical", "High", "Medium", "Low", "Informational"],
                "asset_types": ["Server", "Workstation", "Network Device", "Database", "Application"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur status Audit: {str(e)}")

@router.post("/engine/start")
async def start_audit_engine():
    """Démarre le moteur d'audit"""
    try:
        result = await engine.start_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage moteur: {str(e)}")

@router.post("/engine/stop")
async def stop_audit_engine():
    """Arrête le moteur d'audit"""
    try:
        result = await engine.stop_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt moteur: {str(e)}")

# === GESTION DES AUDITS ===

@router.post("/audits", response_model=Audit)
async def create_audit(request: CreateAuditRequest):
    """Crée un nouvel audit"""
    try:
        audit = await engine.create_audit(request)
        return audit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création audit: {str(e)}")

@router.get("/audits", response_model=dict)
async def search_audits(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    type: Optional[List[str]] = Query(None, description="Types d'audit"),
    status: Optional[List[str]] = Query(None, description="Statuts d'audit"),
    frameworks: Optional[List[str]] = Query(None, description="Frameworks de compliance"),
    lead_auditor: Optional[str] = Query(None, description="Auditeur principal"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des audits"""
    try:
        search_request = AuditSearchRequest(
            query=query,
            type=AuditType(type[0]) if type and len(type) > 0 else None,
            status=[AuditStatus(s) for s in status] if status else None,
            frameworks=[AuditFramework(f) for f in frameworks] if frameworks else None,
            lead_auditor=lead_auditor,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        audits, total = await engine.search_audits(search_request)
        
        return {
            "audits": audits,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche audits: {str(e)}")

@router.get("/audits/{audit_id}", response_model=Audit)
async def get_audit(audit_id: str):
    """Récupère un audit spécifique"""
    try:
        if audit_id not in engine.audits:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
        return engine.audits[audit_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération audit: {str(e)}")

@router.put("/audits/{audit_id}", response_model=Audit)
async def update_audit(audit_id: str, request: UpdateAuditRequest):
    """Met à jour un audit"""
    try:
        audit = await engine.update_audit(audit_id, request)
        return audit
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour audit: {str(e)}")

@router.post("/audits/{audit_id}/execute")
async def execute_audit(audit_id: str):
    """Lance l'exécution d'un audit"""
    try:
        if audit_id not in engine.audits:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
        
        audit = engine.audits[audit_id]
        if audit.status != AuditStatus.PLANNED:
            raise HTTPException(status_code=400, detail="L'audit ne peut pas être exécuté dans son état actuel")
        
        # Programmer l'exécution immédiate
        audit.planned_start_date = datetime.now()
        audit.status = AuditStatus.SCHEDULED
        
        return {
            "message": "Exécution de l'audit programmée",
            "audit_id": audit_id,
            "scheduled_time": audit.planned_start_date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur exécution audit: {str(e)}")

@router.delete("/audits/{audit_id}")
async def delete_audit(audit_id: str):
    """Supprime un audit"""
    try:
        if audit_id not in engine.audits:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
        
        del engine.audits[audit_id]
        return {"message": "Audit supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression audit: {str(e)}")

# === GESTION DES ASSETS ===

@router.post("/assets", response_model=Asset)
async def create_asset(request: CreateAssetRequest):
    """Crée un nouvel asset"""
    try:
        asset = await engine.create_asset(request)
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création asset: {str(e)}")

@router.get("/assets", response_model=List[Asset])
async def get_assets():
    """Récupère tous les assets"""
    try:
        return list(engine.assets.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération assets: {str(e)}")

@router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    """Récupère un asset spécifique"""
    try:
        if asset_id not in engine.assets:
            raise HTTPException(status_code=404, detail="Asset non trouvé")
        return engine.assets[asset_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération asset: {str(e)}")

# === GESTION DES SCOPES ===

@router.post("/scopes", response_model=AuditScope)
async def create_scope(request: CreateScopeRequest):
    """Crée un nouveau scope d'audit"""
    try:
        scope = await engine.create_scope(request)
        return scope
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création scope: {str(e)}")

@router.get("/scopes", response_model=List[AuditScope])
async def get_scopes():
    """Récupère tous les scopes"""
    try:
        return list(engine.scopes.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération scopes: {str(e)}")

@router.get("/scopes/{scope_id}", response_model=AuditScope)
async def get_scope(scope_id: str):
    """Récupère un scope spécifique"""
    try:
        if scope_id not in engine.scopes:
            raise HTTPException(status_code=404, detail="Scope non trouvé")
        return engine.scopes[scope_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération scope: {str(e)}")

# === GESTION DES FINDINGS ===

@router.post("/findings", response_model=Finding)
async def create_finding(request: CreateFindingRequest):
    """Crée un nouveau finding"""
    try:
        finding = await engine.create_finding(request)
        return finding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création finding: {str(e)}")

@router.get("/findings", response_model=dict)
async def search_findings(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    severity: Optional[List[str]] = Query(None, description="Niveaux de sévérité"),
    status: Optional[List[str]] = Query(None, description="Statuts de finding"),
    audit_id: Optional[str] = Query(None, description="ID d'audit"),
    control_id: Optional[str] = Query(None, description="ID de contrôle"),
    assigned_to: Optional[str] = Query(None, description="Assigné à"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des findings"""
    try:
        search_request = FindingSearchRequest(
            query=query,
            severity=[FindingSeverity(s) for s in severity] if severity else None,
            status=[FindingStatus(s) for s in status] if status else None,
            audit_id=audit_id,
            control_id=control_id,
            assigned_to=assigned_to,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        findings, total = await engine.search_findings(search_request)
        
        return {
            "findings": findings,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche findings: {str(e)}")

@router.get("/findings/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    """Récupère un finding spécifique"""
    try:
        if finding_id not in engine.findings:
            raise HTTPException(status_code=404, detail="Finding non trouvé")
        return engine.findings[finding_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération finding: {str(e)}")

@router.put("/findings/{finding_id}", response_model=Finding)
async def update_finding(finding_id: str, request: UpdateFindingRequest):
    """Met à jour un finding"""
    try:
        finding = await engine.update_finding(finding_id, request)
        return finding
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour finding: {str(e)}")

@router.post("/findings/{finding_id}/assign/{assignee}")
async def assign_finding(finding_id: str, assignee: str):
    """Assigne un finding à une personne"""
    try:
        if finding_id not in engine.findings:
            raise HTTPException(status_code=404, detail="Finding non trouvé")
        
        finding = engine.findings[finding_id]
        finding.assigned_to = assignee
        finding.assigned_date = datetime.now()
        finding.status = FindingStatus.IN_PROGRESS
        finding.updated_at = datetime.now()
        
        return {"message": f"Finding assigné à {assignee}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur assignation finding: {str(e)}")

# === PLANS DE REMÉDIATION ===

@router.post("/remediation-plans", response_model=RemediationPlan)
async def create_remediation_plan(request: CreateRemediationPlanRequest):
    """Crée un nouveau plan de remédiation"""
    try:
        plan = await engine.create_remediation_plan(request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création plan remédiation: {str(e)}")

@router.get("/remediation-plans", response_model=List[RemediationPlan])
async def get_remediation_plans():
    """Récupère tous les plans de remédiation"""
    try:
        return list(engine.remediation_plans.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération plans: {str(e)}")

@router.get("/remediation-plans/{plan_id}", response_model=RemediationPlan)
async def get_remediation_plan(plan_id: str):
    """Récupère un plan de remédiation spécifique"""
    try:
        if plan_id not in engine.remediation_plans:
            raise HTTPException(status_code=404, detail="Plan non trouvé")
        return engine.remediation_plans[plan_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération plan: {str(e)}")

# === FRAMEWORKS ET CONTRÔLES ===

@router.get("/frameworks")
async def get_frameworks():
    """Récupère les frameworks supportés"""
    try:
        return {
            "frameworks": engine.framework_definitions,
            "supported": list(engine.framework_definitions.keys()),
            "total": len(engine.framework_definitions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération frameworks: {str(e)}")

@router.get("/frameworks/{framework_id}/controls")
async def get_framework_controls(framework_id: str):
    """Récupère les contrôles d'un framework"""
    try:
        if framework_id not in engine.control_libraries:
            raise HTTPException(status_code=404, detail="Framework non trouvé")
        
        controls = engine.control_libraries[framework_id]
        return {
            "framework": framework_id,
            "controls": controls,
            "total": len(controls)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération contrôles: {str(e)}")

@router.get("/controls/{control_id}")
async def get_control(control_id: str):
    """Récupère un contrôle spécifique"""
    try:
        if control_id not in engine.controls:
            raise HTTPException(status_code=404, detail="Contrôle non trouvé")
        return engine.controls[control_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération contrôle: {str(e)}")

# === COMPLIANCE ET SNAPSHOTS ===

@router.get("/compliance/snapshots", response_model=List[ComplianceSnapshot])
async def get_compliance_snapshots():
    """Récupère les snapshots de compliance"""
    try:
        return list(engine.compliance_snapshots.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération snapshots: {str(e)}")

@router.post("/compliance/snapshots/generate")
async def generate_compliance_snapshot():
    """Génère un snapshot de compliance immédiat"""
    try:
        await engine._generate_compliance_snapshots()
        return {"message": "Snapshots de compliance générés avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération snapshots: {str(e)}")

# === STATISTIQUES ET ANALYTICS ===

@router.get("/statistics/audits", response_model=AuditStatistics)
async def get_audit_statistics():
    """Statistiques des audits"""
    try:
        return engine.get_audit_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques audits: {str(e)}")

@router.get("/statistics/findings", response_model=FindingStatistics)
async def get_finding_statistics():
    """Statistiques des findings"""
    try:
        return engine.get_finding_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques findings: {str(e)}")

@router.get("/dashboard")
async def get_audit_dashboard():
    """Dashboard d'audit avec métriques temps réel"""
    try:
        audit_stats = engine.get_audit_statistics()
        finding_stats = engine.get_finding_statistics()
        engine_status = engine.get_engine_status()
        
        # Activité récente
        recent_audits = sorted(
            engine.audits.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        recent_findings = sorted(
            engine.findings.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        recent_plans = sorted(
            engine.remediation_plans.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:5]
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "engine": engine_status,
            "audits": {
                "total": audit_stats.total_audits,
                "by_status": audit_stats.by_status,
                "by_type": audit_stats.by_type,
                "by_framework": audit_stats.by_framework,
                "average_compliance": audit_stats.average_compliance_score,
                "recent": recent_audits
            },
            "findings": {
                "total": finding_stats.total_findings,
                "by_severity": finding_stats.by_severity,
                "by_status": finding_stats.by_status,
                "by_framework": finding_stats.by_framework,
                "remediation_rate": finding_stats.remediation_rate,
                "avg_resolution_time": finding_stats.avg_resolution_time_days,
                "open_critical": finding_stats.open_critical_findings,
                "overdue": finding_stats.overdue_findings,
                "recent": recent_findings
            },
            "compliance": {
                "frameworks_monitored": len(engine.framework_definitions),
                "controls_loaded": len(engine.controls),
                "snapshots": len(engine.compliance_snapshots),
                "baselines": engine.compliance_baselines["minimum_compliance_scores"]
            },
            "remediation": {
                "plans_total": len(engine.remediation_plans),
                "plans_progress": finding_stats.remediation_progress,
                "recent": recent_plans
            },
            "automation": {
                "templates_available": len(engine.automation_templates),
                "automated_controls": len([c for c in engine.controls.values() if c.is_automated]),
                "manual_controls": len([c for c in engine.controls.values() if not c.is_automated])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dashboard audit: {str(e)}")

# === RAPPORTS ===

@router.post("/reports/audit/{audit_id}")
async def generate_audit_report(audit_id: str):
    """Génère un rapport d'audit"""
    try:
        if audit_id not in engine.audits:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
        
        audit = engine.audits[audit_id]
        findings = [f for f in engine.findings.values() if f.audit_id == audit_id]
        
        # Statistiques audit
        total_findings = len(findings)
        findings_by_severity = {}
        for finding in findings:
            severity = finding.severity.value
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1
        
        report = {
            "audit": audit,
            "findings": findings,
            "statistics": {
                "total_findings": total_findings,
                "by_severity": findings_by_severity,
                "compliance_score": audit.overall_compliance_score,
                "framework_scores": audit.framework_scores
            },
            "controls_tested": audit.controls_tested,
            "recommendations": audit.recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")

@router.get("/templates")
async def get_automation_templates():
    """Liste des templates d'automatisation disponibles"""
    try:
        return {
            "templates": engine.automation_templates,
            "categories": list(engine.automation_templates.keys()),
            "total_templates": len(engine.automation_templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération templates: {str(e)}")

# Démarrer le moteur au chargement du module
import asyncio

# Initialiser le moteur de manière asynchrone
async def init_audit():
    try:
        await engine.start_engine()
    except Exception as e:
        print(f"Erreur initialisation Audit: {e}")

# Démarrer en arrière-plan
try:
    loop = asyncio.get_event_loop()
    loop.create_task(init_audit())
except RuntimeError:
    # Si pas de loop, on démarre plus tard
    pass