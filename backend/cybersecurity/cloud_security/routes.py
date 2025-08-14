# Routes API pour le service Cloud Security
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
import uuid
import asyncio
from datetime import datetime, timedelta

from .models import CloudAuditRequest, CloudAuditResult, CloudFinding, CloudProvider, SeverityLevel
from .scanner import CloudSecurityScanner
from database import get_database

router = APIRouter(prefix="/api/cloud-security", tags=["cloud-security"])

# Cache des audits en cours et terminés
active_audits: Dict[str, Dict] = {}
completed_audits: Dict[str, CloudAuditResult] = {}

@router.get("/")
async def cloud_security_status():
    """Status du service Cloud Security"""
    return {
        "status": "operational",
        "service": "Cloud Security",
        "version": "1.0.0-portable",
        "features": {
            "aws_audit": True,
            "azure_audit": True,
            "gcp_audit": True,
            "multi_cloud_audit": True,
            "compliance_frameworks": True,
            "automated_remediation": False,
            "real_time_monitoring": False
        },
        "supported_providers": ["aws", "azure", "gcp", "multi"],
        "compliance_frameworks": [
            "CIS-AWS", "CIS-Azure", "CIS-GCP", 
            "NIST", "SOC2", "GDPR", "HIPAA"
        ],
        "active_audits": len(active_audits),
        "completed_audits": len(completed_audits)
    }

@router.post("/audit/config", response_model=Dict)
async def start_cloud_audit(audit_request: CloudAuditRequest, background_tasks: BackgroundTasks):
    """Démarre un audit de configuration cloud"""
    try:
        # Générer un ID unique pour l'audit
        audit_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not audit_request.account_id:
            raise HTTPException(status_code=400, detail="Account ID requis")
            
        if audit_request.provider not in [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP, CloudProvider.MULTI]:
            raise HTTPException(status_code=400, detail="Provider non supporté")
        
        # Initialiser l'audit
        audit_info = {
            "audit_id": audit_id,
            "provider": audit_request.provider,
            "account_id": audit_request.account_id,
            "scope": audit_request.scope,
            "status": "starting",
            "start_time": datetime.now(),
            "options": audit_request.options or {}
        }
        
        active_audits[audit_id] = audit_info
        
        # Démarrer l'audit en arrière-plan
        background_tasks.add_task(
            execute_cloud_audit, 
            audit_id, 
            audit_request.provider, 
            audit_request.account_id,
            audit_request.scope or [],
            audit_request.options or {}
        )
        
        return {
            "audit_id": audit_id,
            "status": "started",
            "message": f"Audit {audit_request.provider.value} démarré pour le compte {audit_request.account_id}",
            "estimated_duration": "3-10 minutes",
            "check_status_url": f"/api/cloud-security/audit/{audit_id}/status"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage de l'audit: {str(e)}")

@router.get("/audit/{audit_id}/status")
async def get_audit_status(audit_id: str):
    """Récupère le statut d'un audit"""
    
    # Vérifier dans les audits actifs
    if audit_id in active_audits:
        audit_info = active_audits[audit_id]
        duration = (datetime.now() - audit_info["start_time"]).total_seconds()
        
        return {
            "audit_id": audit_id,
            "status": audit_info["status"],
            "provider": audit_info["provider"],
            "account_id": audit_info["account_id"],
            "duration": round(duration, 2),
            "progress": _estimate_progress(audit_info["status"], duration),
            "message": _get_status_message(audit_info["status"])
        }
    
    # Vérifier dans les audits terminés
    elif audit_id in completed_audits:
        audit_result = completed_audits[audit_id]
        
        return {
            "audit_id": audit_id,
            "status": "completed",
            "provider": audit_result.provider,
            "account_id": audit_result.account_id,
            "duration": audit_result.duration,
            "progress": 100,
            "findings_count": len(audit_result.findings),
            "compliance_score": audit_result.compliance_score,
            "summary": audit_result.summary
        }
    
    else:
        raise HTTPException(status_code=404, detail="Audit non trouvé")

@router.get("/audit/{audit_id}/findings")
async def get_audit_findings(audit_id: str, severity: str = None, page: int = 1, page_size: int = 20):
    """Récupère les findings d'un audit"""
    
    if audit_id not in completed_audits:
        if audit_id in active_audits:
            raise HTTPException(status_code=202, detail="Audit en cours, findings pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    audit_result = completed_audits[audit_id]
    findings = audit_result.findings
    
    # Filtrer par sévérité si spécifiée
    if severity:
        try:
            severity_filter = SeverityLevel(severity.lower())
            findings = [f for f in findings if f.severity == severity_filter]
        except ValueError:
            raise HTTPException(status_code=400, detail="Sévérité invalide")
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_findings = findings[start_idx:end_idx]
    
    return {
        "audit_id": audit_id,
        "findings": [finding.dict() for finding in paginated_findings],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_findings": len(findings),
            "total_pages": (len(findings) + page_size - 1) // page_size
        },
        "summary": audit_result.summary,
        "compliance_score": audit_result.compliance_score
    }

@router.get("/findings")
async def list_findings(
    provider: str = None, 
    severity: str = None, 
    service: str = None, 
    page: int = 1, 
    page_size: int = 20
):
    """Liste tous les findings avec filtres"""
    
    all_findings = []
    
    # Collecter tous les findings des audits terminés
    for audit_result in completed_audits.values():
        for finding in audit_result.findings:
            finding_dict = finding.dict()
            finding_dict["audit_id"] = audit_result.audit_id
            finding_dict["provider"] = audit_result.provider
            all_findings.append(finding_dict)
    
    # Appliquer les filtres
    filtered_findings = all_findings
    
    if provider:
        filtered_findings = [f for f in filtered_findings if f["provider"].lower() == provider.lower()]
    
    if severity:
        filtered_findings = [f for f in filtered_findings if f["severity"].lower() == severity.lower()]
    
    if service:
        filtered_findings = [f for f in filtered_findings if service.lower() in f["service"].lower()]
    
    # Trier par sévérité et date
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    filtered_findings.sort(
        key=lambda x: (severity_order.get(x["severity"], 0), x["detected_at"]), 
        reverse=True
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_findings = filtered_findings[start_idx:end_idx]
    
    return {
        "findings": paginated_findings,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_findings": len(filtered_findings),
            "total_pages": (len(filtered_findings) + page_size - 1) // page_size
        },
        "filters_applied": {
            "provider": provider,
            "severity": severity,
            "service": service
        }
    }

@router.get("/audits")
async def list_audits(limit: int = 20, offset: int = 0):
    """Liste les audits récents"""
    
    all_audits = []
    
    # Ajouter les audits actifs
    for audit_id, audit_info in active_audits.items():
        all_audits.append({
            "audit_id": audit_id,
            "provider": audit_info["provider"],
            "account_id": audit_info["account_id"],
            "status": audit_info["status"],
            "start_time": audit_info["start_time"],
            "duration": (datetime.now() - audit_info["start_time"]).total_seconds()
        })
    
    # Ajouter les audits terminés
    for audit_id, audit_result in completed_audits.items():
        all_audits.append({
            "audit_id": audit_id,
            "provider": audit_result.provider,
            "account_id": audit_result.account_id,
            "status": "completed",
            "start_time": audit_result.start_time,
            "duration": audit_result.duration,
            "findings_count": len(audit_result.findings),
            "compliance_score": audit_result.compliance_score
        })
    
    # Trier par date de début (plus récent en premier)
    all_audits.sort(key=lambda x: x["start_time"], reverse=True)
    
    # Pagination
    paginated_audits = all_audits[offset:offset + limit]
    
    return {
        "audits": paginated_audits,
        "total": len(all_audits),
        "limit": limit,
        "offset": offset,
        "active_count": len(active_audits),
        "completed_count": len(completed_audits)
    }

@router.delete("/audit/{audit_id}")
async def delete_audit(audit_id: str):
    """Supprime un audit et ses résultats"""
    
    deleted = False
    
    if audit_id in active_audits:
        del active_audits[audit_id]
        deleted = True
    
    if audit_id in completed_audits:
        del completed_audits[audit_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    return {"message": f"Audit {audit_id} supprimé avec succès"}

# Fonctions utilitaires privées

async def execute_cloud_audit(audit_id: str, provider: CloudProvider, account_id: str, scope: List[str], options: Dict):
    """Exécute l'audit cloud en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_audits[audit_id]["status"] = "running"
        
        # Exécuter l'audit
        async with CloudSecurityScanner() as scanner:
            findings = await scanner.audit_cloud_config(provider, account_id, scope, options)
        
        # Créer le résultat
        end_time = datetime.now()
        start_time = active_audits[audit_id]["start_time"]
        duration = (end_time - start_time).total_seconds()
        
        # Calculer le résumé des findings
        summary = {
            "critical": len([f for f in findings if f.severity == SeverityLevel.CRITICAL]),
            "high": len([f for f in findings if f.severity == SeverityLevel.HIGH]),
            "medium": len([f for f in findings if f.severity == SeverityLevel.MEDIUM]),
            "low": len([f for f in findings if f.severity == SeverityLevel.LOW]),
            "info": len([f for f in findings if f.severity == SeverityLevel.INFO]),
            "total": len(findings)
        }
        
        # Calculer le score de compliance (0-100)
        total_checks = 50  # Nombre total de vérifications possibles
        failed_checks = len(findings)
        compliance_score = max(0, ((total_checks - failed_checks) / total_checks) * 100)
        
        audit_result = CloudAuditResult(
            audit_id=audit_id,
            provider=provider,
            account_id=account_id,
            status="completed",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            findings=findings,
            summary=summary,
            compliance_score=round(compliance_score, 2),
            metadata={
                "scanner_version": "1.0.0",
                "audit_scope": scope,
                "audit_options": options
            }
        )
        
        # Déplacer vers les audits terminés
        completed_audits[audit_id] = audit_result
        del active_audits[audit_id]
        
        # Sauvegarder en base de données si possible
        try:
            db = await get_database()
            await db.save_audit_result(audit_result.dict())
        except:
            pass  # Continuer même si la sauvegarde échoue
            
    except Exception as e:
        # Marquer l'audit comme échoué
        active_audits[audit_id]["status"] = "failed"
        active_audits[audit_id]["error"] = str(e)
        print(f"Erreur lors de l'audit {audit_id}: {e}")

def _estimate_progress(status: str, duration: float) -> int:
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

def _get_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation de l'audit cloud...",
        "running": "Audit en cours - Vérification des configurations...",
        "completed": "Audit terminé avec succès",
        "failed": "Erreur lors de l'audit"
    }
    return messages.get(status, "Statut inconnu")