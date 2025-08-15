"""
Routes FastAPI pour Red Team Operations
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date

from .models import (
    RedTeamStatusResponse, Campaign, Operation, Target, PurpleTeamExercise,
    CreateCampaignRequest, UpdateCampaignRequest, CreateOperationRequest,
    UpdateOperationRequest, CreateTargetRequest, CreatePurpleTeamExerciseRequest,
    CampaignSearchRequest, OperationSearchRequest, CampaignStatistics,
    OperationStatistics, RedTeamInsight, CampaignStatus, OperationStatus
)
from .red_team_engine import RedTeamEngine

router = APIRouter(prefix="/api/red-team", tags=["Red Team Operations"])

# Instance globale du moteur
engine = RedTeamEngine()

@router.get("/", response_model=dict)
async def red_team_status():
    """Status du service Red Team Operations"""
    try:
        status = engine.get_engine_status()
        
        return {
            "status": "operational",
            "service": "Red Team Operations",
            "version": "1.0.0-portable",
            "description": "Tests intrusion avancés et opérations Red Team",
            "features": {
                "campaign_management": True,
                "operation_execution": True,
                "mitre_attack_ttps": True,
                "purple_team_collaboration": True,
                "automated_reporting": True,
                "real_time_monitoring": True,
                "asset_management": True,
                "technique_library": True
            },
            "engine_status": status,
            "capabilities": {
                "attack_phases": [
                    "Reconnaissance", "Initial Access", "Execution", 
                    "Persistence", "Privilege Escalation", "Defense Evasion",
                    "Credential Access", "Discovery", "Lateral Movement",
                    "Collection", "Command and Control", "Exfiltration", "Impact"
                ],
                "target_types": ["Network", "Application", "Email", "Physical", "Social", "Wireless"],
                "operation_types": ["APT Simulation", "Ransomware", "Insider Threat", "Purple Team"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur status Red Team: {str(e)}")

@router.post("/engine/start")
async def start_red_team_engine():
    """Démarre le moteur Red Team"""
    try:
        result = await engine.start_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage moteur: {str(e)}")

@router.post("/engine/stop")
async def stop_red_team_engine():
    """Arrête le moteur Red Team"""
    try:
        result = await engine.stop_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt moteur: {str(e)}")

# === GESTION DES CAMPAGNES ===

@router.post("/campaigns", response_model=Campaign)
async def create_campaign(request: CreateCampaignRequest):
    """Crée une nouvelle campagne Red Team"""
    try:
        campaign = await engine.create_campaign(request)
        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création campagne: {str(e)}")

@router.get("/campaigns", response_model=dict)
async def search_campaigns(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    status: Optional[List[str]] = Query(None, description="Filtrer par statut"),
    red_team_lead: Optional[str] = Query(None, description="Lead de l'équipe Red Team"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des campagnes Red Team"""
    try:
        search_request = CampaignSearchRequest(
            query=query,
            status=[CampaignStatus(s) for s in status] if status else None,
            red_team_lead=red_team_lead,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        campaigns, total = await engine.search_campaigns(search_request)
        
        return {
            "campaigns": campaigns,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche campagnes: {str(e)}")

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Récupère une campagne spécifique"""
    try:
        if campaign_id not in engine.campaigns:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        return engine.campaigns[campaign_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération campagne: {str(e)}")

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, request: UpdateCampaignRequest):
    """Met à jour une campagne"""
    try:
        campaign = await engine.update_campaign(campaign_id, request)
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour campagne: {str(e)}")

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Supprime une campagne"""
    try:
        if campaign_id not in engine.campaigns:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        
        del engine.campaigns[campaign_id]
        return {"message": "Campagne supprimée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression campagne: {str(e)}")

# === GESTION DES OPÉRATIONS ===

@router.post("/operations", response_model=Operation)
async def create_operation(request: CreateOperationRequest):
    """Crée une nouvelle opération Red Team"""
    try:
        operation = await engine.create_operation(request)
        return operation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création opération: {str(e)}")

@router.get("/operations", response_model=dict)
async def search_operations(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    status: Optional[List[str]] = Query(None, description="Filtrer par statut"),
    campaign_id: Optional[str] = Query(None, description="ID de campagne"),
    technique: Optional[str] = Query(None, description="Technique MITRE"),
    operator: Optional[str] = Query(None, description="Opérateur"),
    success: Optional[bool] = Query(None, description="Filtrer par succès"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des opérations Red Team"""
    try:
        search_request = OperationSearchRequest(
            query=query,
            status=[OperationStatus(s) for s in status] if status else None,
            campaign_id=campaign_id,
            technique=technique,
            operator=operator,
            success=success,
            limit=limit,
            offset=offset
        )
        
        operations, total = await engine.search_operations(search_request)
        
        return {
            "operations": operations,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche opérations: {str(e)}")

@router.get("/operations/{operation_id}", response_model=Operation)
async def get_operation(operation_id: str):
    """Récupère une opération spécifique"""
    try:
        if operation_id not in engine.operations:
            raise HTTPException(status_code=404, detail="Opération non trouvée")
        return engine.operations[operation_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération opération: {str(e)}")

@router.put("/operations/{operation_id}", response_model=Operation)
async def update_operation(operation_id: str, request: UpdateOperationRequest):
    """Met à jour une opération"""
    try:
        operation = await engine.update_operation(operation_id, request)
        return operation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour opération: {str(e)}")

@router.post("/operations/{operation_id}/execute")
async def execute_operation(operation_id: str):
    """Lance l'exécution d'une opération"""
    try:
        if operation_id not in engine.operations:
            raise HTTPException(status_code=404, detail="Opération non trouvée")
        
        operation = engine.operations[operation_id]
        if operation.status != OperationStatus.PLANNED:
            raise HTTPException(status_code=400, detail="L'opération ne peut pas être exécutée dans son état actuel")
        
        # Programmer l'exécution immédiate
        operation.start_time = datetime.now()
        
        return {
            "message": "Exécution de l'opération programmée",
            "operation_id": operation_id,
            "scheduled_time": operation.start_time.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur exécution opération: {str(e)}")

# === GESTION DES CIBLES ===

@router.post("/targets", response_model=Target)
async def create_target(request: CreateTargetRequest):
    """Crée une nouvelle cible"""
    try:
        target = await engine.create_target(request)
        return target
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création cible: {str(e)}")

@router.get("/targets", response_model=List[Target])
async def get_targets():
    """Récupère toutes les cibles"""
    try:
        return list(engine.targets.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération cibles: {str(e)}")

@router.get("/targets/{target_id}", response_model=Target)
async def get_target(target_id: str):
    """Récupère une cible spécifique"""
    try:
        if target_id not in engine.targets:
            raise HTTPException(status_code=404, detail="Cible non trouvée")
        return engine.targets[target_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération cible: {str(e)}")

# === TECHNIQUES ET TTPs ===

@router.get("/techniques")
async def get_techniques():
    """Récupère toutes les techniques disponibles"""
    try:
        return {
            "techniques": list(engine.techniques.values()),
            "total": len(engine.techniques),
            "mitre_techniques": len([t for t in engine.techniques.values() if t.tactic == "mitre_attck"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération techniques: {str(e)}")

@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str):
    """Récupère une technique spécifique"""
    try:
        technique = None
        for t in engine.techniques.values():
            if t.technique_id == technique_id:
                technique = t
                break
        
        if not technique:
            raise HTTPException(status_code=404, detail="Technique non trouvée")
        
        return technique
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération technique: {str(e)}")

# === PURPLE TEAM ===

@router.post("/purple-team/exercises", response_model=PurpleTeamExercise)
async def create_purple_team_exercise(request: CreatePurpleTeamExerciseRequest):
    """Crée un exercice Purple Team"""
    try:
        exercise = PurpleTeamExercise(
            name=request.name,
            description=request.description,
            campaign_id=request.campaign_id,
            scenario_description=request.scenario_description,
            red_team_members=request.red_team_members,
            blue_team_members=request.blue_team_members
        )
        
        engine.purple_team_exercises[exercise.id] = exercise
        return exercise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création exercice Purple Team: {str(e)}")

@router.get("/purple-team/exercises", response_model=List[PurpleTeamExercise])
async def get_purple_team_exercises():
    """Récupère tous les exercices Purple Team"""
    try:
        return list(engine.purple_team_exercises.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération exercices Purple Team: {str(e)}")

# === STATISTIQUES ET ANALYTICS ===

@router.get("/statistics/campaigns", response_model=CampaignStatistics)
async def get_campaign_statistics():
    """Statistiques des campagnes"""
    try:
        return engine.get_campaign_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques campagnes: {str(e)}")

@router.get("/statistics/operations", response_model=OperationStatistics)
async def get_operation_statistics():
    """Statistiques des opérations"""
    try:
        return engine.get_operation_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques opérations: {str(e)}")

@router.get("/dashboard")
async def get_red_team_dashboard():
    """Dashboard Red Team avec métriques temps réel"""
    try:
        campaign_stats = engine.get_campaign_statistics()
        operation_stats = engine.get_operation_statistics()
        engine_status = engine.get_engine_status()
        
        # Activité récente
        recent_operations = sorted(
            engine.operations.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        recent_campaigns = sorted(
            engine.campaigns.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:5]
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "engine": engine_status,
            "campaigns": {
                "total": campaign_stats.total_campaigns,
                "active": campaign_stats.active_campaigns,
                "completed": campaign_stats.completed_campaigns,
                "success_rate": campaign_stats.success_rate,
                "recent": recent_campaigns
            },
            "operations": {
                "total": operation_stats.total_operations,
                "success_rate": operation_stats.success_rate,
                "detection_rate": operation_stats.detection_rate,
                "avg_duration": operation_stats.avg_duration_minutes,
                "by_status": operation_stats.by_status,
                "recent": recent_operations
            },
            "techniques": {
                "total_loaded": len(engine.techniques),
                "mitre_techniques": len([t for t in engine.techniques.values() if t.tactic == "mitre_attck"]),
                "most_used": operation_stats.by_technique
            },
            "purple_team": {
                "exercises": len(engine.purple_team_exercises),
                "active": len([e for e in engine.purple_team_exercises.values() if e.status == OperationStatus.RUNNING])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dashboard Red Team: {str(e)}")

# === RAPPORTS ===

@router.post("/reports/campaign/{campaign_id}")
async def generate_campaign_report(campaign_id: str):
    """Génère un rapport de campagne"""
    try:
        if campaign_id not in engine.campaigns:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        
        campaign = engine.campaigns[campaign_id]
        operations = [op for op in engine.operations.values() if op.campaign_id == campaign_id]
        
        # Statistiques campagne
        total_ops = len(operations)
        successful_ops = len([op for op in operations if op.success])
        detected_ops = len([op for op in operations if op.detection_triggered])
        
        report = {
            "campaign": campaign,
            "operations": operations,
            "statistics": {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "detection_rate": (detected_ops / max(total_ops, 1)) * 100,
                "success_rate": (successful_ops / max(total_ops, 1)) * 100
            },
            "techniques_used": list(set(op.technique.technique_id for op in operations)),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")

# === OUTILS ===

@router.get("/tools")
async def get_red_team_tools():
    """Liste des outils Red Team disponibles"""
    try:
        return {
            "tools": engine.red_team_tools,
            "categories": list(engine.red_team_tools.keys()),
            "total_tools": sum(len(tools) for tools in engine.red_team_tools.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération outils: {str(e)}")

# Démarrer le moteur au chargement du module
import asyncio

# Initialiser le moteur de manière asynchrone
async def init_red_team():
    try:
        await engine.start_engine()
    except Exception as e:
        print(f"Erreur initialisation Red Team: {e}")

# Démarrer en arrière-plan
try:
    loop = asyncio.get_event_loop()
    loop.create_task(init_red_team())
except RuntimeError:
    # Si pas de loop, on démarre plus tard
    pass