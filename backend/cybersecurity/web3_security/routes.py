"""
Web3 Security Routes
API endpoints pour la sécurité Web3 et smart contracts
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime

from .models import (
    SmartContractRequest, ContractAuditResult, ContractVulnerability,
    Web3SecurityStatus, Web3SecurityMetrics
)
from .scanner import Web3SecurityScanner
from database import get_database

router = APIRouter(prefix="/api/web3-security", tags=["Web3 Security"])

# Cache des audits et métriques
active_audits: Dict[str, Dict] = {}
completed_audits: Dict[str, ContractAuditResult] = {}
metrics_storage = Web3SecurityMetrics()

@router.get("/")
async def web3_security_status():
    """Status du service Web3 Security"""
    
    # Calculer les métriques actuelles
    active_audits_count = len([a for a in active_audits.values() if a.get("status") in ["pending", "running"]])
    completed_audits_count = len(completed_audits)
    
    # Stats par chaîne
    chains_stats = {}
    for audit in completed_audits.values():
        chain = audit.chain
        chains_stats[chain] = chains_stats.get(chain, 0) + 1
    
    # Stats par sévérité
    severity_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for audit in completed_audits.values():
        for vuln in audit.vulnerabilities:
            severity_stats[vuln.severity] = severity_stats.get(vuln.severity, 0) + 1
    
    # Score de sécurité moyen
    avg_security_score = 0
    if completed_audits:
        avg_security_score = sum(audit.security_score for audit in completed_audits.values()) / len(completed_audits)
    
    return {
        "status": "operational",
        "service": "Web3 Security",
        "version": "1.0.0-portable",
        "features": {
            "smart_contract_audit": True,
            "solidity_analysis": True,
            "gas_optimization": True,
            "vulnerability_detection": True,
            "standards_compliance": True,
            "multi_chain_support": True,
            "defi_protocols": True,
            "nft_analysis": True
        },
        "supported_chains": [
            "Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Avalanche"
        ],
        "vulnerability_categories": [
            "reentrancy", "overflow", "access_control", "front_running",
            "time_manipulation", "denial_of_service", "unchecked_calls",
            "integer_issues", "race_conditions", "tx_origin"
        ],
        "standards_supported": [
            "ERC-20", "ERC-721", "ERC-1155", "OpenZeppelin", "DeFi"
        ],
        "active_audits": active_audits_count,
        "completed_audits": completed_audits_count,
        "chains_stats": chains_stats,
        "severity_stats": severity_stats,
        "average_security_score": round(avg_security_score, 1)
    }

@router.post("/audit/contract")
async def start_contract_audit(audit_request: SmartContractRequest, background_tasks: BackgroundTasks):
    """Lance un audit de smart contract"""
    try:
        # Générer un ID unique pour l'audit
        audit_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not audit_request.contract_address and not audit_request.source_code:
            raise HTTPException(
                status_code=400,
                detail="Adresse de contrat ou code source requis"
            )
        
        # Initialiser l'audit
        audit_info = {
            "audit_id": audit_id,
            "chain": audit_request.chain,
            "contract_address": audit_request.contract_address,
            "contract_type": audit_request.contract_type,
            "status": "starting",
            "start_time": datetime.now(),
            "audit_scope": audit_request.audit_scope
        }
        
        active_audits[audit_id] = audit_info
        
        # Démarrer l'audit en arrière-plan
        background_tasks.add_task(
            execute_contract_audit,
            audit_id,
            audit_request.dict()
        )
        
        return {
            "audit_id": audit_id,
            "status": "started", 
            "message": f"Audit de smart contract démarré ({audit_request.chain})",
            "contract_address": audit_request.contract_address,
            "contract_type": audit_request.contract_type,
            "audit_scope": audit_request.audit_scope,
            "estimated_duration": "3-8 minutes",
            "check_status_url": f"/api/web3-security/audit/{audit_id}/status"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du démarrage de l'audit: {str(e)}"
        )

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
            "chain": audit_info["chain"],
            "contract_address": audit_info.get("contract_address"),
            "contract_type": audit_info.get("contract_type"),
            "duration": round(duration, 2),
            "progress": _estimate_audit_progress(audit_info["status"], duration),
            "message": _get_audit_status_message(audit_info["status"])
        }
    
    # Vérifier dans les audits terminés
    elif audit_id in completed_audits:
        audit_result = completed_audits[audit_id]
        
        return {
            "audit_id": audit_id,
            "status": audit_result.status,
            "chain": audit_result.chain,
            "contract_address": audit_result.contract_address,
            "contract_type": audit_result.contract_type,
            "duration": audit_result.duration,
            "progress": 100,
            "vulnerabilities_found": len(audit_result.vulnerabilities),
            "critical_vulnerabilities": audit_result.critical_vulnerabilities,
            "high_vulnerabilities": audit_result.high_vulnerabilities,
            "security_score": audit_result.security_score,
            "standards_compliance": audit_result.standards_compliance
        }
    
    else:
        raise HTTPException(status_code=404, detail="Audit non trouvé")

@router.get("/audit/{audit_id}/vulnerabilities")
async def get_audit_vulnerabilities(
    audit_id: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """Récupère les vulnérabilités d'un audit"""
    
    if audit_id not in completed_audits:
        if audit_id in active_audits:
            raise HTTPException(status_code=202, detail="Audit en cours, vulnérabilités pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    audit_result = completed_audits[audit_id]
    vulnerabilities = audit_result.vulnerabilities
    
    # Filtres
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity == severity]
    
    if category:
        vulnerabilities = [v for v in vulnerabilities if v.category == category]
    
    # Trier par sévérité
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    vulnerabilities.sort(
        key=lambda x: (severity_order.get(x.severity, 0), x.detected_at),
        reverse=True
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_vulns = vulnerabilities[start_idx:end_idx]
    
    return {
        "audit_id": audit_id,
        "vulnerabilities": [vuln.dict() for vuln in paginated_vulns],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_vulnerabilities": len(vulnerabilities),
            "total_pages": (len(vulnerabilities) + page_size - 1) // page_size
        },
        "summary": {
            "critical": len([v for v in vulnerabilities if v.severity == "critical"]),
            "high": len([v for v in vulnerabilities if v.severity == "high"]),
            "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
            "low": len([v for v in vulnerabilities if v.severity == "low"])
        },
        "filters_applied": {
            "severity": severity,
            "category": category
        }
    }

@router.get("/audit/{audit_id}/gas-analysis")
async def get_gas_analysis(audit_id: str):
    """Récupère l'analyse de gas d'un audit"""
    
    if audit_id not in completed_audits:
        if audit_id in active_audits:
            raise HTTPException(status_code=202, detail="Audit en cours, analyse gas pas encore disponible")
        else:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    audit_result = completed_audits[audit_id]
    
    return {
        "audit_id": audit_id,
        "gas_analysis": [analysis.dict() for analysis in audit_result.gas_analysis],
        "total_functions": len(audit_result.gas_analysis),
        "average_optimization_potential": round(
            sum(a.optimization_potential for a in audit_result.gas_analysis) / max(1, len(audit_result.gas_analysis)), 1
        ) if audit_result.gas_analysis else 0
    }

@router.get("/audit/{audit_id}/report")
async def get_audit_report(audit_id: str, format: str = "json"):
    """Génère le rapport complet d'audit"""
    
    if audit_id not in completed_audits:
        if audit_id in active_audits:
            raise HTTPException(status_code=202, detail="Audit en cours, rapport pas encore disponible")
        else:
            raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    audit_result = completed_audits[audit_id]
    
    if format == "json":
        return {
            "audit_info": {
                "audit_id": audit_id,
                "chain": audit_result.chain,
                "contract_address": audit_result.contract_address,
                "contract_type": audit_result.contract_type,
                "audit_date": audit_result.started_at.isoformat(),
                "duration": audit_result.duration
            },
            "security_summary": {
                "security_score": audit_result.security_score,
                "total_vulnerabilities": audit_result.total_vulnerabilities,
                "critical_vulnerabilities": audit_result.critical_vulnerabilities,
                "high_vulnerabilities": audit_result.high_vulnerabilities
            },
            "vulnerabilities": [vuln.dict() for vuln in audit_result.vulnerabilities],
            "gas_analysis": [analysis.dict() for analysis in audit_result.gas_analysis],
            "standards_compliance": audit_result.standards_compliance,
            "best_practices": audit_result.best_practices,
            "recommendations": _generate_recommendations(audit_result)
        }
    
    elif format == "pdf":
        # En production, générer un PDF avec ReportLab
        raise HTTPException(status_code=501, detail="Export PDF pas encore implémenté")
    
    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json' ou 'pdf'")

@router.get("/audits")
async def list_audits(
    chain: Optional[str] = None,
    contract_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste les audits avec filtres"""
    
    all_audits = []
    
    # Ajouter les audits actifs
    for audit_id, audit_info in active_audits.items():
        audit_data = {
            "audit_id": audit_id,
            "chain": audit_info["chain"],
            "contract_address": audit_info.get("contract_address"),
            "contract_type": audit_info.get("contract_type"),
            "status": audit_info["status"],
            "start_time": audit_info["start_time"],
            "duration": (datetime.now() - audit_info["start_time"]).total_seconds()
        }
        all_audits.append(audit_data)
    
    # Ajouter les audits terminés
    for audit_id, audit_result in completed_audits.items():
        audit_data = {
            "audit_id": audit_id,
            "chain": audit_result.chain,
            "contract_address": audit_result.contract_address,
            "contract_type": audit_result.contract_type,
            "status": audit_result.status,
            "start_time": audit_result.started_at,
            "duration": audit_result.duration,
            "security_score": audit_result.security_score,
            "vulnerabilities_found": len(audit_result.vulnerabilities)
        }
        all_audits.append(audit_data)
    
    # Filtres
    if chain:
        all_audits = [a for a in all_audits if a["chain"] == chain]
    
    if contract_type:
        all_audits = [a for a in all_audits if a.get("contract_type") == contract_type]
    
    if status:
        all_audits = [a for a in all_audits if a["status"] == status]
    
    # Trier par date de début (plus récent en premier)
    all_audits.sort(key=lambda x: x["start_time"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_audits = all_audits[start_idx:end_idx]
    
    return {
        "audits": paginated_audits,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_audits": len(all_audits),
            "total_pages": (len(all_audits) + page_size - 1) // page_size
        },
        "filters_applied": {
            "chain": chain,
            "contract_type": contract_type,
            "status": status
        },
        "summary": {
            "active_audits": len(active_audits),
            "completed_audits": len(completed_audits)
        }
    }

@router.get("/stats")
async def get_web3_security_stats():
    """Statistiques détaillées Web3 Security"""
    
    if not completed_audits:
        return {
            "total_audits": 0,
            "total_contracts": 0,
            "chains": {},
            "contract_types": {},
            "vulnerabilities": {},
            "average_security_score": 0
        }
    
    # Stats générales
    total_contracts = len(completed_audits)
    total_vulnerabilities = sum(len(audit.vulnerabilities) for audit in completed_audits.values())
    
    # Stats par chaîne
    chains_stats = {}
    contract_types_stats = {}
    vulnerability_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    security_scores = []
    
    for audit in completed_audits.values():
        # Chaînes
        chains_stats[audit.chain] = chains_stats.get(audit.chain, 0) + 1
        
        # Types de contrats
        contract_types_stats[audit.contract_type] = contract_types_stats.get(audit.contract_type, 0) + 1
        
        # Vulnérabilités par sévérité
        for vuln in audit.vulnerabilities:
            vulnerability_stats[vuln.severity] = vulnerability_stats.get(vuln.severity, 0) + 1
        
        # Scores de sécurité
        security_scores.append(audit.security_score)
    
    avg_security_score = sum(security_scores) / len(security_scores) if security_scores else 0
    
    return {
        "total_audits": len(completed_audits),
        "total_contracts": total_contracts,
        "total_vulnerabilities": total_vulnerabilities,
        "chains": chains_stats,
        "contract_types": contract_types_stats,
        "vulnerabilities": vulnerability_stats,
        "average_security_score": round(avg_security_score, 1),
        "security_score_distribution": {
            "excellent": len([s for s in security_scores if s >= 90]),
            "good": len([s for s in security_scores if 70 <= s < 90]),
            "average": len([s for s in security_scores if 50 <= s < 70]),
            "poor": len([s for s in security_scores if s < 50])
        }
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

# Fonctions utilitaires

async def execute_contract_audit(audit_id: str, audit_request: Dict[str, Any]):
    """Exécute l'audit de contrat en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_audits[audit_id]["status"] = "running"
        
        # Exécuter l'audit
        scanner = Web3SecurityScanner()
        result = await scanner.audit_smart_contract(audit_request)
        
        # Mettre à jour l'ID du résultat
        result.id = audit_id
        
        # Mettre à jour les IDs des vulnérabilités
        for vuln in result.vulnerabilities:
            vuln.audit_id = audit_id
        
        # Déplacer vers les audits terminés
        completed_audits[audit_id] = result
        del active_audits[audit_id]
        
        # Sauvegarder en base de données si possible
        try:
            db = await get_database()
            await db.save_audit_result(result.dict())
        except:
            pass  # Continuer même si la sauvegarde échoue
            
    except Exception as e:
        # Marquer l'audit comme échoué
        active_audits[audit_id]["status"] = "failed"
        active_audits[audit_id]["error"] = str(e)
        print(f"Erreur lors de l'audit {audit_id}: {e}")

def _estimate_audit_progress(status: str, duration: float) -> int:
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

def _get_audit_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation de l'audit...",
        "running": "Audit en cours - Analyse du code source...",
        "completed": "Audit terminé avec succès",
        "failed": "Erreur lors de l'audit"
    }
    return messages.get(status, "Statut inconnu")

def _generate_recommendations(audit_result: ContractAuditResult) -> List[str]:
    """Génère des recommandations basées sur les résultats d'audit"""
    recommendations = []
    
    if audit_result.critical_vulnerabilities > 0:
        recommendations.append("🚨 CRITIQUE: Corriger immédiatement les vulnérabilités critiques avant déploiement")
    
    if audit_result.high_vulnerabilities > 0:
        recommendations.append("⚠️ HIGH: Traiter les vulnérabilités haute priorité")
    
    if audit_result.security_score < 70:
        recommendations.append("📊 Score de sécurité faible - Révision complète recommandée")
    
    # Recommandations basées sur les standards
    if not audit_result.standards_compliance.get("OpenZeppelin", False):
        recommendations.append("🔧 Utiliser OpenZeppelin pour les contrats standards")
    
    if not audit_result.best_practices.get("uses_require", False):
        recommendations.append("✅ Ajouter des validations avec require()")
    
    if not audit_result.best_practices.get("has_events", False):
        recommendations.append("📝 Ajouter des événements pour la traçabilité")
    
    # Recommandations gas
    avg_optimization = sum(a.optimization_potential for a in audit_result.gas_analysis) / max(1, len(audit_result.gas_analysis))
    if avg_optimization > 20:
        recommendations.append("⛽ Optimiser la consommation de gas (potentiel d'économie significatif)")
    
    return recommendations[:5]  # Limiter à 5 recommandations principales