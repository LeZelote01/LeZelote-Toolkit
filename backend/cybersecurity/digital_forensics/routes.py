"""
Routes API pour le service Digital Forensics
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from .models import (
    ForensicsCase, DigitalEvidence, AnalysisTask, ForensicsReport,
    EvidenceType, AnalysisStatus, AnalysisRequest, ForensicsSearchRequest, CustodyTransfer
)
from .forensics_engine import ForensicsEngine
from database import get_database

router = APIRouter(prefix="/api/digital-forensics", tags=["digital-forensics"])

# Instance du moteur forensique
forensics_engine = ForensicsEngine()

# Cache des dossiers et preuves actifs
active_cases: Dict[str, ForensicsCase] = {}
active_evidence: Dict[str, DigitalEvidence] = {}
active_tasks: Dict[str, AnalysisTask] = {}


@router.get("/")
async def forensics_status():
    """Status du service Digital Forensics"""
    return {
        "status": "operational",
        "service": "Digital Forensics",
        "version": "1.0.0-portable",
        "features": {
            "evidence_acquisition": True,
            "chain_of_custody": True,
            "automated_analysis": True,
            "timeline_reconstruction": True,
            "hash_verification": True,
            "keyword_search": True,
            "metadata_extraction": True,
            "report_generation": True
        },
        "supported_evidence_types": [et.value for et in EvidenceType],
        "analysis_modules": list(forensics_engine.analysis_modules.keys()),
        "active_cases": len(active_cases),
        "active_evidence": len(active_evidence),
        "running_analyses": len([t for t in active_tasks.values() if t.status == AnalysisStatus.IN_PROGRESS])
    }


@router.post("/case")
async def create_forensics_case(case_data: Dict[str, Any]):
    """Crée un nouveau dossier d'enquête forensique"""
    try:
        # Valider les données requises
        required_fields = ['title', 'description', 'investigator', 'client']
        for field in required_fields:
            if field not in case_data:
                raise HTTPException(status_code=400, detail=f"Champ requis manquant: {field}")
        
        # Créer le dossier
        case = await forensics_engine.create_case(case_data)
        
        # Stocker en cache
        active_cases[case.id] = case
        
        return {
            "status": "success",
            "message": f"Dossier forensique '{case.title}' créé avec succès",
            "case": {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "created_at": case.created_at.isoformat(),
                "investigator": case.created_by,
                "status": case.status
            },
            "next_steps": [
                "1. Ajouter les preuves numériques au dossier",
                "2. Définir les analyses à effectuer",
                "3. Lancer les analyses forensiques",
                "4. Documenter les découvertes"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création dossier: {str(e)}")


@router.get("/case/{case_id}")
async def get_case(case_id: str):
    """Récupère les détails d'un dossier forensique"""
    if case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    case = active_cases[case_id]
    
    # Compter les preuves associées
    case_evidence = [e for e in active_evidence.values() if e.case_id == case_id]
    case_tasks = [t for t in active_tasks.values() if t.case_id == case_id]
    
    return {
        "case": case.dict(),
        "evidence_count": len(case_evidence),
        "analysis_tasks": len(case_tasks),
        "completed_analyses": len([t for t in case_tasks if t.status == AnalysisStatus.COMPLETED]),
        "running_analyses": len([t for t in case_tasks if t.status == AnalysisStatus.IN_PROGRESS]),
        "chain_of_custody_entries": len(case.custody_chain),
        "last_activity": max([e.acquired_at for e in case_evidence] + [case.updated_at]).isoformat() if case_evidence else case.updated_at.isoformat()
    }


@router.post("/case/{case_id}/evidence")
async def add_evidence(case_id: str, evidence_data: Dict[str, Any]):
    """Ajoute une preuve numérique au dossier"""
    if case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    try:
        # Valider les données
        required_fields = ['name', 'description', 'evidence_type', 'source', 'acquired_by']
        for field in required_fields:
            if field not in evidence_data:
                raise HTTPException(status_code=400, detail=f"Champ requis manquant: {field}")
        
        # Créer la preuve
        evidence = await forensics_engine.add_evidence(case_id, evidence_data)
        
        # Stocker en cache
        active_evidence[evidence.id] = evidence
        
        return {
            "status": "success",
            "message": f"Preuve '{evidence.name}' ajoutée au dossier",
            "evidence": {
                "id": evidence.id,
                "name": evidence.name,
                "type": evidence.evidence_type.value,
                "acquired_at": evidence.acquired_at.isoformat(),
                "acquired_by": evidence.acquired_by,
                "hash_verification": len(evidence.hashes) > 0,
                "file_size": evidence.file_size
            },
            "recommendations": [
                "Vérifier l'intégrité de la preuve avec /evidence/{evidence_id}/verify",
                "Lancer des analyses appropriées selon le type de preuve",
                "Maintenir la chaîne de custody pour toute manipulation"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ajout preuve: {str(e)}")


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Récupère les détails d'une preuve"""
    if evidence_id not in active_evidence:
        raise HTTPException(status_code=404, detail="Preuve non trouvée")
    
    evidence = active_evidence[evidence_id]
    
    # Récupérer les analyses associées
    evidence_tasks = [t for t in active_tasks.values() if t.evidence_id == evidence_id]
    
    return {
        "evidence": evidence.dict(),
        "analysis_count": len(evidence_tasks),
        "completed_analyses": [t.task_type for t in evidence_tasks if t.status == AnalysisStatus.COMPLETED],
        "pending_analyses": [t.task_type for t in evidence_tasks if t.status in [AnalysisStatus.PENDING, AnalysisStatus.IN_PROGRESS]],
        "custody_entries": len(evidence.custody_log),
        "integrity_hashes": list(evidence.hashes.keys())
    }


@router.post("/evidence/{evidence_id}/verify")
async def verify_evidence_integrity(evidence_id: str):
    """Vérifie l'intégrité d'une preuve"""
    if evidence_id not in active_evidence:
        raise HTTPException(status_code=404, detail="Preuve non trouvée")
    
    evidence = active_evidence[evidence_id]
    
    try:
        verification_result = await forensics_engine.verify_evidence_integrity(evidence)
        
        return {
            "verification": verification_result,
            "status": "verified" if verification_result["verified"] else "integrity_compromised",
            "message": "Intégrité vérifiée avec succès" if verification_result["verified"] else "ALERTE: Intégrité compromise!",
            "recommendations": [
                "Documenter la vérification dans la chaîne de custody",
                "En cas de compromission, enquêter sur les causes"
            ] if verification_result["verified"] else [
                "🚨 URGENT: Arrêter toute analyse sur cette preuve",
                "🚨 Enquêter immédiatement sur la cause de la compromission",
                "🚨 Notifier le responsable du dossier",
                "🚨 Réévaluer la validité de toutes les analyses précédentes"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur vérification intégrité: {str(e)}")


@router.post("/analysis/start")
async def start_analysis(analysis_request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Lance une ou plusieurs analyses forensiques"""
    
    # Vérifier que le dossier et la preuve existent
    if analysis_request.case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    if analysis_request.evidence_id not in active_evidence:
        raise HTTPException(status_code=404, detail="Preuve non trouvée")
    
    try:
        # Lancer les analyses
        tasks = await forensics_engine.start_analysis(
            analysis_request.case_id,
            analysis_request.evidence_id,
            analysis_request.analysis_types,
            analysis_request.assigned_to,
            analysis_request.parameters
        )
        
        # Stocker les tâches en cache
        for task in tasks:
            active_tasks[task.id] = task
        
        return {
            "status": "success",
            "message": f"{len(tasks)} analyses lancées avec succès",
            "analyses": [
                {
                    "task_id": task.id,
                    "analysis_type": task.task_type,
                    "status": task.status.value,
                    "estimated_duration": f"{task.estimated_duration or 'variable'} minutes"
                }
                for task in tasks
            ],
            "monitoring": {
                "check_status_endpoint": "/analysis/{task_id}/status",
                "list_all_analyses": f"/case/{analysis_request.case_id}/analyses"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lancement analyses: {str(e)}")


@router.get("/analysis/{task_id}/status")
async def get_analysis_status(task_id: str):
    """Récupère le statut d'une analyse"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    task = active_tasks[task_id]
    
    # Calculer la durée
    duration = None
    if task.started_at:
        end_time = task.completed_at or datetime.now()
        duration = (end_time - task.started_at).total_seconds() / 60  # en minutes
    
    return {
        "task": {
            "id": task.id,
            "analysis_type": task.task_type,
            "status": task.status.value,
            "progress": f"{int(task.progress * 100)}%",
            "duration_minutes": round(duration, 2) if duration else None,
            "assigned_to": task.assigned_to
        },
        "results": task.results if task.status == AnalysisStatus.COMPLETED else None,
        "artifacts_found": len(task.artifacts_found),
        "error": task.error_message if task.status == AnalysisStatus.FAILED else None,
        "next_actions": _get_analysis_next_actions(task)
    }


@router.get("/analysis/{task_id}/results")
async def get_analysis_results(task_id: str):
    """Récupère les résultats détaillés d'une analyse"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    task = active_tasks[task_id]
    
    if task.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Analyse pas encore terminée (statut: {task.status.value})")
    
    return {
        "task_id": task.id,
        "analysis_type": task.task_type,
        "results": task.results,
        "artifacts": task.artifacts_found,
        "completed_at": task.completed_at.isoformat(),
        "duration_minutes": round((task.completed_at - task.started_at).total_seconds() / 60, 2),
        "summary": task.results.get('summary', 'Analyse terminée avec succès')
    }


@router.post("/search")
async def search_evidence(search_request: ForensicsSearchRequest):
    """Effectue une recherche dans les preuves"""
    if search_request.case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    try:
        results = await forensics_engine.search_evidence(
            search_request.case_id,
            search_request.search_terms,
            search_request.evidence_ids
        )
        
        return {
            "search": {
                "case_id": search_request.case_id,
                "terms": search_request.search_terms,
                "type": search_request.search_type,
                "case_sensitive": search_request.case_sensitive
            },
            "results": results,
            "recommendations": [
                "Examiner attentivement chaque correspondance trouvée",
                "Documenter les découvertes importantes dans le dossier",
                "Considérer des recherches complémentaires selon les résultats"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {str(e)}")


@router.post("/evidence/{evidence_id}/custody/transfer")
async def transfer_custody(evidence_id: str, transfer: CustodyTransfer):
    """Effectue un transfert de custody d'une preuve"""
    if evidence_id not in active_evidence:
        raise HTTPException(status_code=404, detail="Preuve non trouvée")
    
    try:
        result = await forensics_engine.transfer_custody(
            evidence_id,
            transfer.from_person,
            transfer.to_person,
            transfer.transfer_reason,
            transfer.location,
            transfer.witness
        )
        
        # Mettre à jour la preuve
        evidence = active_evidence[evidence_id]
        evidence.custody_log.append(result["transfer_record"])
        
        return {
            "status": "success",
            "message": f"Transfert de custody effectué: {transfer.from_person} → {transfer.to_person}",
            "transfer": result,
            "custody_chain_length": len(evidence.custody_log),
            "recommendations": [
                "Vérifier que le transfert a été correctement documenté",
                "S'assurer que le destinataire a confirmé la réception",
                "Maintenir la sécurité physique de la preuve"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur transfert custody: {str(e)}")


@router.get("/case/{case_id}/custody-chain")
async def get_custody_chain(case_id: str):
    """Récupère la chaîne de custody complète d'un dossier"""
    if case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    case = active_cases[case_id]
    case_evidence = [e for e in active_evidence.values() if e.case_id == case_id]
    
    custody_summary = []
    
    # Custody du dossier
    custody_summary.append({
        "type": "case",
        "id": case.id,
        "name": case.title,
        "custody_entries": case.custody_chain
    })
    
    # Custody de chaque preuve
    for evidence in case_evidence:
        custody_summary.append({
            "type": "evidence",
            "id": evidence.id,
            "name": evidence.name,
            "custody_entries": evidence.custody_log
        })
    
    return {
        "case_id": case_id,
        "custody_chain_summary": custody_summary,
        "total_entries": sum(len(item["custody_entries"]) for item in custody_summary),
        "chain_verified": all(len(item["custody_entries"]) > 0 for item in custody_summary)
    }


@router.get("/case/{case_id}/timeline")
async def get_case_timeline(case_id: str):
    """Récupère la timeline reconstructed d'un dossier"""
    if case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    # Récupérer tous les événements temporels du dossier
    timeline_events = []
    
    # Événements du dossier
    case = active_cases[case_id]
    timeline_events.append({
        "timestamp": case.created_at.isoformat(),
        "event_type": "case_created",
        "description": f"Dossier créé: {case.title}",
        "source": "case_management"
    })
    
    # Événements des preuves
    case_evidence = [e for e in active_evidence.values() if e.case_id == case_id]
    for evidence in case_evidence:
        timeline_events.append({
            "timestamp": evidence.acquired_at.isoformat(),
            "event_type": "evidence_acquired",
            "description": f"Preuve acquise: {evidence.name}",
            "source": evidence.source,
            "evidence_id": evidence.id
        })
    
    # Événements des analyses
    case_tasks = [t for t in active_tasks.values() if t.case_id == case_id]
    for task in case_tasks:
        if task.completed_at:
            timeline_events.append({
                "timestamp": task.completed_at.isoformat(),
                "event_type": "analysis_completed",
                "description": f"Analyse terminée: {task.task_type}",
                "source": "forensics_analysis",
                "task_id": task.id
            })
    
    # Trier par timestamp
    timeline_events.sort(key=lambda x: x["timestamp"])
    
    return {
        "case_id": case_id,
        "timeline": timeline_events,
        "total_events": len(timeline_events),
        "time_span": {
            "start": timeline_events[0]["timestamp"] if timeline_events else None,
            "end": timeline_events[-1]["timestamp"] if timeline_events else None
        }
    }


@router.post("/case/{case_id}/report")
async def generate_case_report(case_id: str, include_technical: bool = True):
    """Génère un rapport forensique complet"""
    if case_id not in active_cases:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    try:
        report = await forensics_engine.generate_forensics_report(case_id, include_technical)
        
        return {
            "status": "success",
            "message": "Rapport forensique généré avec succès",
            "report": report.dict(),
            "export_options": {
                "pdf": f"/reports/pdf/{report.id}",
                "html": f"/reports/html/{report.id}",
                "json": "included_in_response"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")


@router.get("/cases")
async def list_cases(status: Optional[str] = None, investigator: Optional[str] = None):
    """Liste les dossiers forensiques"""
    
    cases_list = []
    for case in active_cases.values():
        # Appliquer les filtres
        if status and case.status != status:
            continue
        if investigator and case.created_by != investigator:
            continue
        
        # Compter les preuves et analyses
        case_evidence_count = len([e for e in active_evidence.values() if e.case_id == case.id])
        case_tasks = [t for t in active_tasks.values() if t.case_id == case.id]
        
        cases_list.append({
            "id": case.id,
            "case_number": case.case_number,
            "title": case.title,
            "status": case.status,
            "created_at": case.created_at.isoformat(),
            "investigator": case.created_by,
            "client": case.client,
            "evidence_count": case_evidence_count,
            "completed_analyses": len([t for t in case_tasks if t.status == AnalysisStatus.COMPLETED]),
            "priority": case.priority
        })
    
    # Trier par date de création
    cases_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "cases": cases_list,
        "total": len(cases_list),
        "filters": {"status": status, "investigator": investigator}
    }


@router.get("/statistics")
async def get_forensics_statistics():
    """Statistiques du service forensique"""
    
    total_evidence = len(active_evidence)
    total_analyses = len(active_tasks)
    completed_analyses = len([t for t in active_tasks.values() if t.status == AnalysisStatus.COMPLETED])
    
    # Statistiques par type de preuve
    evidence_by_type = {}
    for evidence in active_evidence.values():
        evidence_type = evidence.evidence_type.value
        evidence_by_type[evidence_type] = evidence_by_type.get(evidence_type, 0) + 1
    
    # Statistiques par type d'analyse
    analyses_by_type = {}
    for task in active_tasks.values():
        analysis_type = task.task_type
        analyses_by_type[analysis_type] = analyses_by_type.get(analysis_type, 0) + 1
    
    return {
        "summary": {
            "active_cases": len(active_cases),
            "total_evidence": total_evidence,
            "total_analyses": total_analyses,
            "completion_rate": round((completed_analyses / total_analyses * 100), 2) if total_analyses > 0 else 0
        },
        "evidence_by_type": evidence_by_type,
        "analyses_by_type": analyses_by_type,
        "currently_running": len([t for t in active_tasks.values() if t.status == AnalysisStatus.IN_PROGRESS])
    }


# Fonctions utilitaires

def _get_analysis_next_actions(task: AnalysisTask) -> List[str]:
    """Détermine les prochaines actions selon le statut de l'analyse"""
    if task.status == AnalysisStatus.COMPLETED:
        return [
            "Examiner les résultats détaillés",
            "Documenter les découvertes importantes",
            "Considérer des analyses complémentaires",
            "Mettre à jour la timeline du dossier"
        ]
    elif task.status == AnalysisStatus.IN_PROGRESS:
        return [
            "Surveillance en cours - vérifier le statut périodiquement",
            "Préparer l'analyse des résultats",
            "S'assurer que l'analyste est disponible pour interpréter"
        ]
    elif task.status == AnalysisStatus.FAILED:
        return [
            "🚨 Examiner les logs d'erreur",
            "🚨 Vérifier l'intégrité de la preuve",
            "🚨 Contacter le support technique si nécessaire",
            "🚨 Envisager une approche d'analyse alternative"
        ]
    else:
        return ["Analyse en attente - sera lancée automatiquement"]