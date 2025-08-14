"""
Routes API pour le service Incident Response
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid
from datetime import datetime, timedelta

from .models import (
    Incident, IncidentRequest, IncidentResponse, IncidentSeverity, 
    IncidentStatus, IncidentCategory, Evidence, IncidentAction
)
from .incident_engine import IncidentResponseEngine
from database import get_database

router = APIRouter(prefix="/api/incident-response", tags=["incident-response"])

# Instance du moteur de réponse aux incidents
ir_engine = IncidentResponseEngine()

# Cache des incidents actifs
active_incidents: Dict[str, Incident] = {}


@router.get("/")
async def incident_response_status():
    """Status du service Incident Response"""
    return {
        "status": "operational",
        "service": "Incident Response",
        "version": "1.0.0-portable",
        "features": {
            "automated_response": True,
            "playbook_execution": True,
            "evidence_management": True,
            "threat_intelligence": True,
            "real_time_monitoring": True,
            "compliance_reporting": True
        },
        "incident_categories": [cat.value for cat in IncidentCategory],
        "severity_levels": [sev.value for sev in IncidentSeverity],
        "active_incidents": len(active_incidents),
        "playbooks_available": len(ir_engine.playbooks)
    }


@router.post("/incident", response_model=IncidentResponse)
async def create_incident(incident_request: IncidentRequest, background_tasks: BackgroundTasks):
    """Crée un nouvel incident et lance la réponse automatisée"""
    try:
        # Créer l'incident avec le moteur
        incident = await ir_engine.create_incident(incident_request)
        
        # Stocker en cache
        active_incidents[incident.id] = incident
        
        # Sauvegarder en base de données en arrière-plan
        background_tasks.add_task(save_incident_to_db, incident)
        
        # Déterminer les recommandations initiales
        recommendations = _generate_initial_recommendations(incident)
        next_steps = _generate_initial_next_steps(incident)
        
        return IncidentResponse(
            incident_id=incident.id,
            status="created",
            message=f"Incident '{incident.title}' créé avec succès. Réponse automatisée démarrée.",
            details={
                "severity": incident.severity.value,
                "category": incident.category.value,
                "affected_systems": len(incident.affected_systems),
                "playbook_selected": "auto-selected",
                "estimated_response_time": "15-45 minutes"
            },
            recommendations=recommendations,
            next_steps=next_steps
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'incident: {str(e)}")


@router.get("/incident/{incident_id}")
async def get_incident(incident_id: str):
    """Récupère les détails d'un incident"""
    
    # Vérifier dans le cache
    if incident_id in active_incidents:
        incident = active_incidents[incident_id]
        
        return {
            "incident": incident.dict(),
            "summary": {
                "actions_performed": len(incident.actions),
                "evidence_collected": len(incident.evidence),
                "threat_indicators": len(incident.threat_indicators),
                "duration": _calculate_incident_duration(incident),
                "last_activity": max([action.timestamp for action in incident.actions]).isoformat() if incident.actions else incident.created_at.isoformat()
            },
            "status_details": await ir_engine.get_incident_status(incident_id)
        }
    
    # Si pas en cache, essayer de récupérer depuis la base
    # (dans une vraie implémentation)
    raise HTTPException(status_code=404, detail="Incident non trouvé")


@router.get("/incident/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str):
    """Récupère la timeline détaillée d'un incident"""
    
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    
    incident = active_incidents[incident_id]
    
    # Construire la timeline
    timeline = []
    
    # Ajouter la création de l'incident
    timeline.append({
        "timestamp": incident.created_at.isoformat(),
        "event_type": "incident_created",
        "title": "Incident Créé",
        "description": f"Incident '{incident.title}' signalé par {incident.reporter}",
        "severity": incident.severity.value,
        "actor": incident.reporter
    })
    
    # Ajouter toutes les actions
    for action in sorted(incident.actions, key=lambda x: x.timestamp):
        timeline.append({
            "timestamp": action.timestamp.isoformat(),
            "event_type": action.action_type,
            "title": action.action_type.replace("_", " ").title(),
            "description": action.description,
            "results": action.results,
            "actor": action.performed_by
        })
    
    # Ajouter les changements de statut
    if incident.contained_at:
        timeline.append({
            "timestamp": incident.contained_at.isoformat(),
            "event_type": "incident_contained",
            "title": "Incident Confiné",
            "description": "L'incident a été confiné avec succès",
            "actor": "system"
        })
    
    if incident.resolved_at:
        timeline.append({
            "timestamp": incident.resolved_at.isoformat(),
            "event_type": "incident_resolved",
            "title": "Incident Résolu",
            "description": "L'incident a été résolu",
            "actor": "system"
        })
    
    # Trier par timestamp
    timeline.sort(key=lambda x: x["timestamp"])
    
    return {
        "incident_id": incident_id,
        "timeline": timeline,
        "total_events": len(timeline),
        "current_status": incident.status.value
    }


@router.post("/incident/{incident_id}/action")
async def add_incident_action(incident_id: str, action_data: Dict[str, Any]):
    """Ajoute une action manuelle à un incident"""
    
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    
    incident = active_incidents[incident_id]
    
    # Créer la nouvelle action
    action = IncidentAction(
        id=str(uuid.uuid4()),
        action_type=action_data.get("action_type", "manual_action"),
        performed_by=action_data.get("performed_by", "analyst"),
        description=action_data.get("description", ""),
        results=action_data.get("results")
    )
    
    # Ajouter à l'incident
    incident.actions.append(action)
    incident.updated_at = datetime.now()
    
    # Mettre à jour le statut si nécessaire
    if action_data.get("status_update"):
        try:
            new_status = IncidentStatus(action_data["status_update"])
            incident.status = new_status
            
            if new_status == IncidentStatus.CONTAINED:
                incident.contained_at = datetime.now()
            elif new_status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now()
        except ValueError:
            pass
    
    return {
        "status": "success",
        "message": "Action ajoutée avec succès",
        "action_id": action.id,
        "incident_status": incident.status.value
    }


@router.post("/incident/{incident_id}/evidence")
async def add_evidence(incident_id: str, evidence_data: Dict[str, Any]):
    """Ajoute une preuve à un incident"""
    
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    
    incident = active_incidents[incident_id]
    
    # Créer la preuve
    evidence = Evidence(
        id=str(uuid.uuid4()),
        type=evidence_data.get("type", "manual"),
        source=evidence_data.get("source", "analyst"),
        collected_by=evidence_data.get("collected_by", "analyst"),
        description=evidence_data.get("description", ""),
        file_path=evidence_data.get("file_path"),
        metadata=evidence_data.get("metadata", {})
    )
    
    # Ajouter à l'incident
    incident.evidence.append(evidence)
    incident.updated_at = datetime.now()
    
    # Ajouter une action correspondante
    evidence_action = IncidentAction(
        id=str(uuid.uuid4()),
        action_type="evidence_added",
        performed_by=evidence.collected_by,
        description=f"Preuve ajoutée: {evidence.description}",
        results=f"Preuve de type '{evidence.type}' collectée"
    )
    incident.actions.append(evidence_action)
    
    return {
        "status": "success",
        "message": "Preuve ajoutée avec succès",
        "evidence_id": evidence.id,
        "total_evidence": len(incident.evidence)
    }


@router.get("/incident/{incident_id}/report")
async def generate_incident_report(incident_id: str, format: str = "json"):
    """Génère un rapport détaillé de l'incident"""
    
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    
    incident = active_incidents[incident_id]
    
    try:
        # Générer le rapport avec le moteur
        report = await ir_engine.generate_incident_report(incident)
        
        if format.lower() == "json":
            return {
                "incident_id": incident_id,
                "report": report,
                "generated_at": datetime.now().isoformat()
            }
        
        # Pour d'autres formats (PDF, HTML), on pourrait utiliser un générateur de rapports
        # comme celui du service pentest
        
        return {
            "status": "success",
            "message": f"Rapport généré au format {format}",
            "report_data": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")


@router.get("/incidents")
async def list_incidents(
    status: str = None,
    severity: str = None,
    category: str = None,
    limit: int = 20,
    offset: int = 0
):
    """Liste les incidents avec filtres optionnels"""
    
    incidents_list = []
    
    for incident in active_incidents.values():
        # Appliquer les filtres
        if status and incident.status.value != status:
            continue
        if severity and incident.severity.value != severity:
            continue
        if category and incident.category.value != category:
            continue
        
        # Ajouter le résumé de l'incident
        incidents_list.append({
            "id": incident.id,
            "title": incident.title,
            "category": incident.category.value,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "created_at": incident.created_at.isoformat(),
            "updated_at": incident.updated_at.isoformat(),
            "affected_systems": len(incident.affected_systems),
            "actions_count": len(incident.actions),
            "evidence_count": len(incident.evidence),
            "reporter": incident.reporter,
            "assigned_to": incident.assigned_to
        })
    
    # Trier par date de création (plus récent en premier)
    incidents_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Pagination
    paginated_incidents = incidents_list[offset:offset + limit]
    
    return {
        "incidents": paginated_incidents,
        "total": len(incidents_list),
        "limit": limit,
        "offset": offset,
        "filters_applied": {
            "status": status,
            "severity": severity,
            "category": category
        }
    }


@router.get("/playbooks")
async def list_playbooks():
    """Liste les playbooks disponibles"""
    
    playbooks_summary = []
    for playbook in ir_engine.playbooks.values():
        playbooks_summary.append({
            "id": playbook.id,
            "name": playbook.name,
            "description": playbook.description,
            "incident_types": [cat.value for cat in playbook.incident_types],
            "severity_levels": [sev.value for sev in playbook.severity_levels],
            "steps_count": len(playbook.steps),
            "automated_steps": len([step for step in playbook.steps if step.automated]),
            "estimated_duration": playbook.estimated_total_duration
        })
    
    return {
        "playbooks": playbooks_summary,
        "total_playbooks": len(playbooks_summary)
    }


@router.get("/statistics")
async def get_incident_statistics():
    """Statistiques des incidents"""
    
    if not active_incidents:
        return {
            "total_incidents": 0,
            "by_status": {},
            "by_severity": {},
            "by_category": {},
            "average_response_time": None,
            "containment_rate": 0
        }
    
    # Calculer les statistiques
    by_status = {}
    by_severity = {}
    by_category = {}
    
    contained_count = 0
    total_response_times = []
    
    for incident in active_incidents.values():
        # Par statut
        by_status[incident.status.value] = by_status.get(incident.status.value, 0) + 1
        
        # Par sévérité
        by_severity[incident.severity.value] = by_severity.get(incident.severity.value, 0) + 1
        
        # Par catégorie
        by_category[incident.category.value] = by_category.get(incident.category.value, 0) + 1
        
        # Taux de confinement
        if incident.contained_at:
            contained_count += 1
            response_time = (incident.contained_at - incident.created_at).total_seconds() / 60  # en minutes
            total_response_times.append(response_time)
    
    avg_response_time = sum(total_response_times) / len(total_response_times) if total_response_times else None
    containment_rate = (contained_count / len(active_incidents)) * 100 if active_incidents else 0
    
    return {
        "total_incidents": len(active_incidents),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_category": by_category,
        "average_response_time_minutes": round(avg_response_time, 2) if avg_response_time else None,
        "containment_rate_percent": round(containment_rate, 2),
        "contained_incidents": contained_count
    }


# Fonctions utilitaires

async def save_incident_to_db(incident: Incident):
    """Sauvegarde un incident en base de données"""
    try:
        db = await get_database()
        collection = await db.get_collection("incidents")
        await collection.insert_one(incident.dict())
    except Exception as e:
        print(f"Erreur sauvegarde incident {incident.id}: {e}")


def _generate_initial_recommendations(incident: Incident) -> List[str]:
    """Génère les recommandations initiales"""
    recommendations = []
    
    if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
        recommendations.append("🚨 Escalader immédiatement selon la procédure d'urgence")
        recommendations.append("📞 Notifier l'équipe de direction et les parties prenantes")
    
    if incident.category == IncidentCategory.DATA_BREACH:
        recommendations.append("📋 Vérifier les obligations de notification réglementaire (GDPR)")
        recommendations.append("🔒 Évaluer les données potentiellement exposées")
    
    if incident.category in [IncidentCategory.MALWARE, IncidentCategory.RANSOMWARE]:
        recommendations.append("🔌 Isoler immédiatement les systèmes affectés du réseau")
        recommendations.append("💾 Vérifier l'état des sauvegardes avant toute action")
    
    recommendations.append("📝 Documenter toutes les actions dans cet incident")
    recommendations.append("🔍 Préserver les preuves pour l'analyse forensique")
    
    return recommendations


def _generate_initial_next_steps(incident: Incident) -> List[str]:
    """Génère les prochaines étapes initiales"""
    return [
        "1. Surveiller les actions automatisées du playbook",
        "2. Collecter des informations supplémentaires si nécessaire",
        "3. Coordonner avec les équipes techniques concernées",
        "4. Préparer la communication vers les parties prenantes",
        "5. Planifier les actions de récupération post-incident"
    ]


def _calculate_incident_duration(incident: Incident) -> str:
    """Calcule la durée de l'incident"""
    end_time = incident.resolved_at or datetime.now()
    duration = end_time - incident.created_at
    
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"