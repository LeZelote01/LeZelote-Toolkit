"""
Routes FastAPI pour Blue Team Defense
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date

from .models import (
    BlueTeamStatusResponse, IOC, DetectionRule, Alert, ThreatHunt, DefensiveAction,
    CreateIOCRequest, CreateDetectionRuleRequest, CreateAlertRequest, UpdateAlertRequest,
    CreateThreatHuntRequest, UpdateThreatHuntRequest, ExecuteDefensiveActionRequest,
    IOCSearchRequest, AlertSearchRequest, HuntSearchRequest, AlertStatistics,
    HuntStatistics, ThreatSeverity, AlertStatus, HuntStatus, DataSource, HuntTechnique
)
from .blue_team_engine import BlueTeamEngine

router = APIRouter(prefix="/api/blue-team", tags=["Blue Team Defense"])

# Instance globale du moteur
engine = BlueTeamEngine()

@router.get("/", response_model=dict)
async def blue_team_status():
    """Status du service Blue Team Defense"""
    try:
        status = engine.get_engine_status()
        
        return {
            "status": "operational",
            "service": "Blue Team Defense",
            "version": "1.0.0-portable",
            "description": "Threat hunting proactif et défense avancée",
            "features": {
                "threat_hunting": True,
                "alert_management": True,
                "ioc_management": True,
                "detection_rules": True,
                "defensive_actions": True,
                "threat_intelligence": True,
                "anomaly_detection": True,
                "behavioral_analysis": True
            },
            "engine_status": status,
            "capabilities": {
                "hunt_techniques": [
                    "Behavior Analysis", "IOC Hunting", "Anomaly Detection",
                    "Pattern Matching", "Baseline Deviation", "Correlation Analysis"
                ],
                "data_sources": [
                    "Logs", "Network", "Endpoint", "Email", "DNS", 
                    "Web Proxy", "Firewall", "IDS/IPS", "SIEM", "EDR"
                ],
                "response_actions": [
                    "Monitor", "Isolate", "Block", "Quarantine", 
                    "Patch", "Investigate", "Escalate"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur status Blue Team: {str(e)}")

@router.post("/engine/start")
async def start_blue_team_engine():
    """Démarre le moteur Blue Team"""
    try:
        result = await engine.start_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage moteur: {str(e)}")

@router.post("/engine/stop")
async def stop_blue_team_engine():
    """Arrête le moteur Blue Team"""
    try:
        result = await engine.stop_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt moteur: {str(e)}")

# === GESTION DES IOCs ===

@router.post("/iocs", response_model=IOC)
async def create_ioc(request: CreateIOCRequest):
    """Crée un nouvel IOC (Indicator of Compromise)"""
    try:
        ioc = await engine.create_ioc(request)
        return ioc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création IOC: {str(e)}")

@router.get("/iocs", response_model=dict)
async def search_iocs(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    ioc_type: Optional[str] = Query(None, description="Type d'IOC (ip, domain, hash, etc.)"),
    severity: Optional[List[str]] = Query(None, description="Niveaux de sévérité"),
    is_active: Optional[bool] = Query(None, description="IOCs actifs seulement"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des IOCs"""
    try:
        search_request = IOCSearchRequest(
            query=query,
            ioc_type=ioc_type,
            severity=[ThreatSeverity(s) for s in severity] if severity else None,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        iocs, total = await engine.search_iocs(search_request)
        
        return {
            "iocs": iocs,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche IOCs: {str(e)}")

@router.get("/iocs/{ioc_id}", response_model=IOC)
async def get_ioc(ioc_id: str):
    """Récupère un IOC spécifique"""
    try:
        if ioc_id not in engine.iocs:
            raise HTTPException(status_code=404, detail="IOC non trouvé")
        return engine.iocs[ioc_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération IOC: {str(e)}")

@router.put("/iocs/{ioc_id}/deactivate")
async def deactivate_ioc(ioc_id: str):
    """Désactive un IOC (marque comme faux positif)"""
    try:
        if ioc_id not in engine.iocs:
            raise HTTPException(status_code=404, detail="IOC non trouvé")
        
        ioc = engine.iocs[ioc_id]
        ioc.is_active = False
        ioc.false_positive = True
        ioc.updated_at = datetime.now()
        
        return {"message": "IOC désactivé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur désactivation IOC: {str(e)}")

# === GESTION DES RÈGLES DE DÉTECTION ===

@router.post("/detection-rules", response_model=DetectionRule)
async def create_detection_rule(request: CreateDetectionRuleRequest):
    """Crée une nouvelle règle de détection"""
    try:
        rule = await engine.create_detection_rule(request)
        return rule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création règle: {str(e)}")

@router.get("/detection-rules", response_model=List[DetectionRule])
async def get_detection_rules():
    """Récupère toutes les règles de détection"""
    try:
        return list(engine.detection_rules.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération règles: {str(e)}")

@router.get("/detection-rules/{rule_id}", response_model=DetectionRule)
async def get_detection_rule(rule_id: str):
    """Récupère une règle de détection spécifique"""
    try:
        if rule_id not in engine.detection_rules:
            raise HTTPException(status_code=404, detail="Règle non trouvée")
        return engine.detection_rules[rule_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération règle: {str(e)}")

@router.put("/detection-rules/{rule_id}/toggle")
async def toggle_detection_rule(rule_id: str):
    """Active/désactive une règle de détection"""
    try:
        if rule_id not in engine.detection_rules:
            raise HTTPException(status_code=404, detail="Règle non trouvée")
        
        rule = engine.detection_rules[rule_id]
        rule.is_enabled = not rule.is_enabled
        rule.updated_at = datetime.now()
        
        status = "activée" if rule.is_enabled else "désactivée"
        return {"message": f"Règle {status} avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur modification règle: {str(e)}")

# === GESTION DES ALERTES ===

@router.post("/alerts", response_model=Alert)
async def create_alert(request: CreateAlertRequest):
    """Crée une nouvelle alerte"""
    try:
        alert = await engine.create_alert(request)
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création alerte: {str(e)}")

@router.get("/alerts", response_model=dict)
async def search_alerts(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    status: Optional[List[str]] = Query(None, description="Statuts d'alerte"),
    severity: Optional[List[str]] = Query(None, description="Niveaux de sévérité"),
    assigned_to: Optional[str] = Query(None, description="Assigné à"),
    data_source: Optional[str] = Query(None, description="Source de données"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des alertes"""
    try:
        search_request = AlertSearchRequest(
            query=query,
            status=[AlertStatus(s) for s in status] if status else None,
            severity=[ThreatSeverity(s) for s in severity] if severity else None,
            assigned_to=assigned_to,
            data_source=DataSource(data_source) if data_source else None,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        alerts, total = await engine.search_alerts(search_request)
        
        return {
            "alerts": alerts,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche alertes: {str(e)}")

@router.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Récupère une alerte spécifique"""
    try:
        if alert_id not in engine.alerts:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        return engine.alerts[alert_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération alerte: {str(e)}")

@router.put("/alerts/{alert_id}", response_model=Alert)
async def update_alert(alert_id: str, request: UpdateAlertRequest):
    """Met à jour une alerte"""
    try:
        alert = await engine.update_alert(alert_id, request)
        return alert
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour alerte: {str(e)}")

@router.post("/alerts/{alert_id}/assign/{analyst}")
async def assign_alert(alert_id: str, analyst: str):
    """Assigne une alerte à un analyste"""
    try:
        if alert_id not in engine.alerts:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        
        alert = engine.alerts[alert_id]
        alert.assigned_to = analyst
        alert.status = AlertStatus.INVESTIGATING
        alert.updated_at = datetime.now()
        
        return {"message": f"Alerte assignée à {analyst}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur assignation alerte: {str(e)}")

# === THREAT HUNTING ===

@router.post("/hunts", response_model=ThreatHunt)
async def create_threat_hunt(request: CreateThreatHuntRequest):
    """Crée un nouveau threat hunt"""
    try:
        hunt = await engine.create_threat_hunt(request)
        return hunt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création hunt: {str(e)}")

@router.get("/hunts", response_model=dict)
async def search_hunts(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    status: Optional[List[str]] = Query(None, description="Statuts de hunt"),
    hunter: Optional[str] = Query(None, description="Hunter assigné"),
    hunt_technique: Optional[str] = Query(None, description="Technique de hunt"),
    date_from: Optional[date] = Query(None, description="Date de début"),
    date_to: Optional[date] = Query(None, description="Date de fin"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Recherche des threat hunts"""
    try:
        search_request = HuntSearchRequest(
            query=query,
            status=[HuntStatus(s) for s in status] if status else None,
            hunter=hunter,
            hunt_technique=HuntTechnique(hunt_technique) if hunt_technique else None,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        hunts, total = await engine.search_hunts(search_request)
        
        return {
            "hunts": hunts,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche hunts: {str(e)}")

@router.get("/hunts/{hunt_id}", response_model=ThreatHunt)
async def get_hunt(hunt_id: str):
    """Récupère un threat hunt spécifique"""
    try:
        if hunt_id not in engine.threat_hunts:
            raise HTTPException(status_code=404, detail="Hunt non trouvé")
        return engine.threat_hunts[hunt_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération hunt: {str(e)}")

@router.put("/hunts/{hunt_id}", response_model=ThreatHunt)
async def update_hunt(hunt_id: str, request: UpdateThreatHuntRequest):
    """Met à jour un threat hunt"""
    try:
        hunt = await engine.update_threat_hunt(hunt_id, request)
        return hunt
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour hunt: {str(e)}")

@router.post("/hunts/{hunt_id}/execute")
async def execute_hunt(hunt_id: str):
    """Lance l'exécution d'un hunt"""
    try:
        if hunt_id not in engine.threat_hunts:
            raise HTTPException(status_code=404, detail="Hunt non trouvé")
        
        hunt = engine.threat_hunts[hunt_id]
        if hunt.status != HuntStatus.PLANNED:
            raise HTTPException(status_code=400, detail="Le hunt ne peut pas être exécuté dans son état actuel")
        
        # Programmer l'exécution immédiate
        hunt.planned_start = datetime.now()
        
        return {
            "message": "Exécution du hunt programmée",
            "hunt_id": hunt_id,
            "scheduled_time": hunt.planned_start.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur exécution hunt: {str(e)}")

# === ACTIONS DÉFENSIVES ===

@router.post("/actions", response_model=DefensiveAction)
async def execute_defensive_action(request: ExecuteDefensiveActionRequest):
    """Exécute une action défensive"""
    try:
        action = await engine.execute_defensive_action(request)
        return action
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur action défensive: {str(e)}")

@router.get("/actions", response_model=List[DefensiveAction])
async def get_defensive_actions():
    """Récupère toutes les actions défensives"""
    try:
        return list(engine.defensive_actions.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération actions: {str(e)}")

@router.get("/actions/{action_id}", response_model=DefensiveAction)
async def get_defensive_action(action_id: str):
    """Récupère une action défensive spécifique"""
    try:
        if action_id not in engine.defensive_actions:
            raise HTTPException(status_code=404, detail="Action non trouvée")
        return engine.defensive_actions[action_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération action: {str(e)}")

# === PLAYBOOKS ET TEMPLATES ===

@router.get("/playbooks")
async def get_hunt_playbooks():
    """Récupère les playbooks de threat hunting disponibles"""
    try:
        return {
            "playbooks": engine.hunt_playbooks,
            "categories": list(engine.hunt_playbooks.keys()),
            "total": len(engine.hunt_playbooks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération playbooks: {str(e)}")

@router.get("/patterns")
async def get_detection_patterns():
    """Récupère les patterns de détection disponibles"""
    try:
        return {
            "patterns": engine.detection_patterns,
            "categories": list(engine.detection_patterns.keys()),
            "total": len(engine.detection_patterns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération patterns: {str(e)}")

# === STATISTIQUES ET ANALYTICS ===

@router.get("/statistics/alerts", response_model=AlertStatistics)
async def get_alert_statistics():
    """Statistiques des alertes"""
    try:
        return engine.get_alert_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques alertes: {str(e)}")

@router.get("/statistics/hunts", response_model=HuntStatistics)
async def get_hunt_statistics():
    """Statistiques des threat hunts"""
    try:
        return engine.get_hunt_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur statistiques hunts: {str(e)}")

@router.get("/dashboard")
async def get_blue_team_dashboard():
    """Dashboard Blue Team avec métriques temps réel"""
    try:
        alert_stats = engine.get_alert_statistics()
        hunt_stats = engine.get_hunt_statistics()
        engine_status = engine.get_engine_status()
        
        # Activité récente
        recent_alerts = sorted(
            engine.alerts.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        recent_hunts = sorted(
            engine.threat_hunts.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:5]
        
        recent_actions = sorted(
            engine.defensive_actions.values(),
            key=lambda x: x.executed_at,
            reverse=True
        )[:10]
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "engine": engine_status,
            "alerts": {
                "total": alert_stats.total_alerts,
                "by_status": alert_stats.by_status,
                "by_severity": alert_stats.by_severity,
                "true_positive_rate": alert_stats.true_positive_rate,
                "false_positive_rate": alert_stats.false_positive_rate,
                "avg_response_time": alert_stats.avg_response_time,
                "last_24h": alert_stats.alerts_last_24h,
                "recent": recent_alerts
            },
            "hunts": {
                "total": hunt_stats.total_hunts,
                "by_status": hunt_stats.by_status,
                "by_technique": hunt_stats.by_technique,
                "success_rate": hunt_stats.success_rate,
                "threats_identified": hunt_stats.threats_identified,
                "new_iocs": hunt_stats.new_iocs_discovered,
                "recent": recent_hunts
            },
            "iocs": {
                "total": len(engine.iocs),
                "active": len([i for i in engine.iocs.values() if i.is_active]),
                "by_type": {},  # TODO: Implémenter
                "high_confidence": len([i for i in engine.iocs.values() if i.confidence > 0.8])
            },
            "actions": {
                "total": len(engine.defensive_actions),
                "successful": len([a for a in engine.defensive_actions.values() if a.status == "success"]),
                "recent": recent_actions
            },
            "detection": {
                "rules_total": len(engine.detection_rules),
                "rules_enabled": len([r for r in engine.detection_rules.values() if r.is_enabled]),
                "patterns_loaded": len(engine.detection_patterns)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dashboard Blue Team: {str(e)}")

# === THREAT INTELLIGENCE ===

@router.get("/threat-intel")
async def get_threat_intelligence():
    """Récupère les informations de threat intelligence"""
    try:
        return {
            "feeds": engine.intel_feeds,
            "total_intel": len(engine.threat_intel),
            "active_threats": len([t for t in engine.threat_intel.values() 
                                 if not t.valid_until or t.valid_until > datetime.now()]),
            "sources": list(set(t.source for t in engine.threat_intel.values()))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur threat intelligence: {str(e)}")

# Démarrer le moteur au chargement du module
import asyncio

async def init_blue_team():
    try:
        await engine.start_engine()
    except Exception as e:
        print(f"Erreur initialisation Blue Team: {e}")

# Démarrer en arrière-plan
try:
    loop = asyncio.get_event_loop()
    loop.create_task(init_blue_team())
except RuntimeError:
    pass