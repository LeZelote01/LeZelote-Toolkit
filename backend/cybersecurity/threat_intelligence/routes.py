"""
Routes API pour le service Threat Intelligence
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, date, timedelta

from .models import (
    IOC, ThreatActor, Campaign, CTIFeed, ThreatIntelligenceReport, EnrichmentResult,
    IOCType, ThreatType, ThreatSeverity, IOCConfidence, TLPClassification, CTIFeedStatus,
    CreateIOCRequest, UpdateIOCRequest, IOCSearchRequest, CreateCTIFeedRequest,
    ThreatIntelligenceQuery, ThreatIntelligenceStatusResponse, IOCStatistics,
    ThreatIntelligenceInsight
)
from .threat_intelligence_engine import ThreatIntelligenceEngine
from database import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/threat-intelligence", tags=["threat-intelligence"])

# Instance du moteur de threat intelligence
ti_engine = ThreatIntelligenceEngine()

# Flag pour savoir si le moteur est démarré
engine_started = False

@router.get("/")
async def threat_intelligence_status():
    """Status du service Threat Intelligence"""
    status = ti_engine.get_engine_status()
    
    return ThreatIntelligenceStatusResponse(
        status="operational",
        service="Threat Intelligence",
        version="1.0.0-portable",
        features={
            "ioc_management": True,
            "cti_feeds": True,
            "automatic_enrichment": True,
            "threat_attribution": True,
            "correlation_engine": True,
            "misp_integration": True,
            "api_integrations": True,
            "threat_hunting": True
        },
        total_iocs=status["total_iocs"],
        active_iocs=status["active_iocs"],
        total_feeds=status["total_feeds"],
        active_feeds=status["active_feeds"],
        threat_actors=status["threat_actors"],
        campaigns=status["campaigns"],
        last_feed_update=None,  # TODO: calculer depuis les feeds
        enrichment_queue_size=status["enrichment_queue_size"],
        feeds_status=status["feeds_status"]
    )


@router.post("/start")
async def start_threat_intelligence():
    """Démarre le moteur de threat intelligence"""
    global engine_started
    
    if engine_started:
        return {
            "status": "already_running",
            "message": "Le moteur Threat Intelligence est déjà actif",
            "uptime": ti_engine.get_engine_status()["uptime_formatted"]
        }
    
    try:
        result = await ti_engine.start_engine()
        engine_started = True
        
        return {
            "status": "success",
            "message": "Moteur Threat Intelligence démarré avec succès",
            "details": result,
            "capabilities": [
                "Collecte automatique CTI via feeds",
                "Enrichissement IOCs en temps réel",
                "Corrélation et attribution des menaces",
                "Integration MISP et sources ouvertes"
            ],
            "next_steps": [
                "Configurer des feeds CTI personnalisés",
                "Importer des IOCs existants",
                "Activer l'enrichissement automatique"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage moteur TI: {str(e)}")


@router.post("/stop")
async def stop_threat_intelligence():
    """Arrête le moteur de threat intelligence"""
    global engine_started
    
    try:
        result = await ti_engine.stop_engine()
        engine_started = False
        
        return {
            "status": "success",
            "message": "Moteur Threat Intelligence arrêté avec succès",
            "details": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt moteur TI: {str(e)}")


@router.get("/dashboard")
async def get_threat_intelligence_dashboard():
    """Dashboard de threat intelligence"""
    try:
        stats = ti_engine.get_statistics()
        engine_status = ti_engine.get_engine_status()
        
        # Tendances et insights
        insights = await _generate_threat_insights()
        
        # Top menaces récentes
        recent_threats = await _get_recent_threats()
        
        # Activité feeds
        feed_activity = await _get_feed_activity()
        
        return {
            "overview": {
                "engine_status": "active" if engine_status["is_running"] else "inactive",
                "total_iocs": stats.total_iocs,
                "active_iocs": engine_status["active_iocs"],
                "feeds_active": engine_status["active_feeds"],
                "enrichment_queue": engine_status["enrichment_queue_size"],
                "last_update": datetime.now().isoformat()
            },
            "ioc_statistics": {
                "by_type": stats.by_type,
                "by_threat_type": stats.by_threat_type,
                "by_severity": stats.by_severity,
                "by_confidence": stats.by_confidence
            },
            "recent_activity": {
                "added_last_24h": stats.added_last_24h,
                "updated_last_24h": stats.updated_last_24h,
                "expiring_soon": stats.expiring_soon,
                "false_positives": stats.false_positives
            },
            "top_lists": {
                "threat_actors": stats.top_threat_actors,
                "campaigns": stats.top_campaigns,
                "malware_families": stats.top_malware_families
            },
            "threat_insights": insights,
            "recent_threats": recent_threats,
            "feed_activity": feed_activity,
            "recommendations": _generate_dashboard_recommendations(stats, engine_status)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération dashboard: {str(e)}")


@router.post("/iocs")
async def create_ioc(ioc_request: CreateIOCRequest, background_tasks: BackgroundTasks):
    """Crée un nouvel IOC"""
    try:
        ioc = await ti_engine.create_ioc(ioc_request)
        
        # Sauvegarder en base en arrière-plan
        background_tasks.add_task(save_ioc_to_db, ioc)
        
        return {
            "status": "success",
            "message": f"IOC '{ioc.value}' créé avec succès",
            "ioc": {
                "id": ioc.id,
                "value": ioc.value,
                "type": ioc.type.value,
                "threat_type": ioc.threat_type.value,
                "severity": ioc.severity.value,
                "confidence": ioc.confidence.value,
                "created_at": ioc.created_at.isoformat(),
                "tags": ioc.tags
            },
            "threat_context": await _build_ioc_context(ioc),
            "recommendations": _generate_ioc_recommendations(ioc),
            "next_steps": [
                "Enrichissement automatique programmé",
                "Corrélation avec IOCs existants",
                "Surveillance continue activée"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création IOC: {str(e)}")


@router.get("/iocs/{ioc_id}")
async def get_ioc(ioc_id: str, include_enrichment: bool = True, include_relations: bool = True):
    """Récupère les détails d'un IOC"""
    if ioc_id not in ti_engine.iocs:
        raise HTTPException(status_code=404, detail="IOC non trouvé")
    
    ioc = ti_engine.iocs[ioc_id]
    
    response = {
        "ioc": ioc.dict(),
        "metadata": {
            "age_days": (datetime.now() - ioc.created_at).days,
            "last_activity": ioc.last_seen.isoformat(),
            "detection_count": ioc.detection_count,
            "is_expired": ioc.expiry_date and ioc.expiry_date < datetime.now() if ioc.expiry_date else False
        }
    }
    
    # Enrichissement si demandé
    if include_enrichment and ioc.id in ti_engine.enrichment_cache:
        response["enrichment"] = ti_engine.enrichment_cache[ioc.id].dict()
    
    # Relations si demandées
    if include_relations:
        related_iocs = await ti_engine._find_related_iocs(ioc)
        response["related_iocs"] = [
            {
                "id": r.id,
                "value": r.value,
                "type": r.type.value,
                "severity": r.severity.value,
                "relationship_type": _determine_relationship_type(ioc, r)
            }
            for r in related_iocs
        ]
    
    # Contexte de menace
    response["threat_context"] = await ti_engine._build_threat_context(ioc)
    
    # Actions suggérées
    response["suggested_actions"] = _suggest_ioc_actions(ioc)
    
    return response


@router.put("/iocs/{ioc_id}")
async def update_ioc(ioc_id: str, update_request: UpdateIOCRequest):
    """Met à jour un IOC"""
    try:
        ioc = await ti_engine.update_ioc(ioc_id, update_request)
        
        return {
            "status": "success",
            "message": "IOC mis à jour avec succès",
            "ioc": {
                "id": ioc.id,
                "value": ioc.value,
                "severity": ioc.severity.value,
                "confidence": ioc.confidence.value,
                "is_active": ioc.is_active,
                "false_positive": ioc.false_positive,
                "updated_at": ioc.updated_at.isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour IOC: {str(e)}")


@router.post("/iocs/search")
async def search_iocs(search_request: IOCSearchRequest):
    """Recherche des IOCs selon des critères"""
    try:
        results, total = await ti_engine.search_iocs(search_request)
        
        iocs_data = []
        for ioc in results:
            ioc_data = {
                "id": ioc.id,
                "value": ioc.value,
                "type": ioc.type.value,
                "threat_type": ioc.threat_type.value,
                "severity": ioc.severity.value,
                "confidence": ioc.confidence.value,
                "is_active": ioc.is_active,
                "false_positive": ioc.false_positive,
                "first_seen": ioc.first_seen.isoformat(),
                "last_seen": ioc.last_seen.isoformat(),
                "tags": ioc.tags,
                "source": ioc.source,
                "threat_actor": ioc.threat_actor,
                "campaign": ioc.campaign,
                "detection_count": ioc.detection_count
            }
            iocs_data.append(ioc_data)
        
        return {
            "iocs": iocs_data,
            "total_results": total,
            "search_criteria": search_request.dict(),
            "summary": _generate_search_summary(results),
            "facets": _generate_search_facets(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche IOCs: {str(e)}")


@router.post("/query")
async def query_threat_intelligence(query_request: ThreatIntelligenceQuery):
    """Interroge la threat intelligence pour un IOC spécifique"""
    try:
        results = await ti_engine.query_threat_intelligence(query_request)
        
        # Ajouter contexte enrichi
        if results["found"]:
            results["risk_assessment"] = _assess_ioc_risk(results["ioc_data"])
            results["timeline_analysis"] = _analyze_ioc_timeline(results["ioc_data"])
            results["attribution_confidence"] = _calculate_attribution_confidence(results["ioc_data"])
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur requête TI: {str(e)}")


@router.post("/feeds")
async def create_cti_feed(feed_request: CreateCTIFeedRequest, background_tasks: BackgroundTasks):
    """Crée un nouveau feed CTI"""
    try:
        feed = await ti_engine.create_cti_feed(feed_request)
        
        # Sauvegarder en base en arrière-plan
        background_tasks.add_task(save_feed_to_db, feed)
        
        return {
            "status": "success",
            "message": f"Feed CTI '{feed.name}' créé avec succès",
            "feed": {
                "id": feed.id,
                "name": feed.name,
                "provider": feed.provider,
                "feed_type": feed.feed_type,
                "status": feed.status.value,
                "update_frequency": feed.update_frequency,
                "enabled": feed.enabled,
                "created_at": feed.created_at.isoformat()
            },
            "configuration": {
                "ioc_types": [t.value for t in feed.ioc_types] if feed.ioc_types else "all",
                "min_confidence": feed.min_confidence.value,
                "max_age_days": feed.max_age_days
            },
            "next_steps": [
                "Premier import programmé dans les prochaines minutes",
                "Surveillance automatique des mises à jour",
                "Validation manuelle recommandée des premiers IOCs"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création feed CTI: {str(e)}")


@router.get("/feeds")
async def list_cti_feeds():
    """Liste tous les feeds CTI"""
    feeds_summary = []
    
    for feed in ti_engine.cti_feeds.values():
        feed_data = {
            "id": feed.id,
            "name": feed.name,
            "description": feed.description,
            "provider": feed.provider,
            "feed_type": feed.feed_type,
            "status": feed.status.value,
            "enabled": feed.enabled,
            "update_frequency": feed.update_frequency,
            "last_update": feed.last_update.isoformat() if feed.last_update else None,
            "last_success": feed.last_success.isoformat() if feed.last_success else None,
            "last_error": feed.last_error,
            "iocs_imported": feed.iocs_imported,
            "iocs_updated": feed.iocs_updated,
            "tags": feed.tags,
            "created_at": feed.created_at.isoformat()
        }
        feeds_summary.append(feed_data)
    
    # Statistiques globales des feeds
    total_feeds = len(feeds_summary)
    active_feeds = len([f for f in feeds_summary if f["enabled"]])
    error_feeds = len([f for f in feeds_summary if f["status"] == "error"])
    
    return {
        "feeds": feeds_summary,
        "summary": {
            "total_feeds": total_feeds,
            "active_feeds": active_feeds,
            "error_feeds": error_feeds,
            "success_rate": ((total_feeds - error_feeds) / max(total_feeds, 1)) * 100
        }
    }


@router.get("/feeds/{feed_id}")
async def get_cti_feed(feed_id: str):
    """Récupère les détails d'un feed CTI"""
    if feed_id not in ti_engine.cti_feeds:
        raise HTTPException(status_code=404, detail="Feed CTI non trouvé")
    
    feed = ti_engine.cti_feeds[feed_id]
    
    # Calculer métriques
    time_since_update = None
    if feed.last_update:
        time_since_update = (datetime.now() - feed.last_update).total_seconds()
    
    next_update = None
    if feed.last_update:
        next_update = feed.last_update + timedelta(seconds=feed.update_frequency)
    
    return {
        "feed": feed.dict(),
        "metrics": {
            "time_since_last_update": time_since_update,
            "next_update_scheduled": next_update.isoformat() if next_update else None,
            "import_rate": feed.iocs_imported / max((datetime.now() - feed.created_at).days, 1),
            "update_rate": feed.iocs_updated / max((datetime.now() - feed.created_at).days, 1)
        },
        "health_status": _assess_feed_health(feed),
        "recommendations": _generate_feed_recommendations(feed)
    }


@router.post("/feeds/{feed_id}/update")
async def trigger_feed_update(feed_id: str, background_tasks: BackgroundTasks):
    """Déclenche une mise à jour manuelle d'un feed"""
    if feed_id not in ti_engine.cti_feeds:
        raise HTTPException(status_code=404, detail="Feed CTI non trouvé")
    
    try:
        feed = ti_engine.cti_feeds[feed_id]
        
        # Déclencher mise à jour en arrière-plan
        background_tasks.add_task(ti_engine._update_feed, feed)
        
        return {
            "status": "success",
            "message": f"Mise à jour du feed '{feed.name}' déclenchée",
            "feed_id": feed_id,
            "triggered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur déclenchement mise à jour feed: {str(e)}")


@router.get("/statistics")
async def get_threat_intelligence_statistics():
    """Statistiques détaillées de threat intelligence"""
    try:
        stats = ti_engine.get_statistics()
        engine_status = ti_engine.get_engine_status()
        
        # Calculs additionnels
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # IOCs par période
        iocs_last_week = 0
        iocs_last_month = 0
        
        for ioc in ti_engine.iocs.values():
            if ioc.created_at >= week_ago:
                iocs_last_week += 1
            if ioc.created_at >= month_ago:
                iocs_last_month += 1
        
        # Tendances
        growth_rate = (stats.added_last_24h * 365) / max(stats.total_iocs, 1) * 100
        
        return {
            "overview": stats.dict(),
            "engine_performance": engine_status,
            "temporal_analysis": {
                "iocs_last_week": iocs_last_week,
                "iocs_last_month": iocs_last_month,
                "growth_rate_percent": round(growth_rate, 2)
            },
            "quality_metrics": {
                "false_positive_rate": (stats.false_positives / max(stats.total_iocs, 1)) * 100,
                "high_confidence_ratio": (stats.by_confidence.get("high", 0) / max(stats.total_iocs, 1)) * 100,
                "critical_severity_ratio": (stats.by_severity.get("critical", 0) / max(stats.total_iocs, 1)) * 100
            },
            "recommendations": _generate_statistics_recommendations(stats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques: {str(e)}")


@router.get("/insights")
async def get_threat_insights():
    """Génère des insights de threat intelligence"""
    try:
        insights = await _generate_detailed_threat_insights()
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "insights_count": len(insights),
            "categories": list(set([insight["insight_type"] for insight in insights]))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération insights: {str(e)}")


@router.get("/attribution/{actor_name}")
async def get_threat_actor_profile(actor_name: str):
    """Récupère le profil d'un threat actor"""
    # Chercher IOCs associés
    related_iocs = []
    for ioc in ti_engine.iocs.values():
        if ioc.threat_actor and actor_name.lower() in ioc.threat_actor.lower():
            related_iocs.append({
                "id": ioc.id,
                "value": ioc.value,
                "type": ioc.type.value,
                "severity": ioc.severity.value,
                "first_seen": ioc.first_seen.isoformat()
            })
    
    if not related_iocs:
        raise HTTPException(status_code=404, detail="Threat actor non trouvé dans les IOCs")
    
    # Analyser patterns
    profile = _analyze_threat_actor_patterns(actor_name, related_iocs)
    
    return {
        "threat_actor": actor_name,
        "profile": profile,
        "related_iocs_count": len(related_iocs),
        "related_iocs": related_iocs[:20],  # Limiter à 20 pour la réponse
        "generated_at": datetime.now().isoformat()
    }


# Fonctions utilitaires privées

async def save_ioc_to_db(ioc: IOC):
    """Sauvegarde un IOC en base de données"""
    try:
        db = await get_database()
        collection = await db.get_collection("threat_intelligence_iocs")
        await collection.insert_one(ioc.dict())
    except Exception as e:
        logger.error(f"Erreur sauvegarde IOC {ioc.id}: {e}")


async def save_feed_to_db(feed: CTIFeed):
    """Sauvegarde un feed CTI en base de données"""
    try:
        db = await get_database()
        collection = await db.get_collection("threat_intelligence_feeds")
        await collection.insert_one(feed.dict())
    except Exception as e:
        logger.error(f"Erreur sauvegarde feed {feed.id}: {e}")


async def _generate_threat_insights() -> List[Dict[str, Any]]:
    """Génère des insights de menaces basiques"""
    insights = []
    
    # Analyse de tendance
    if ti_engine.get_statistics().added_last_24h > 10:
        insights.append({
            "type": "trend",
            "title": "Augmentation d'activité IOCs",
            "description": f"{ti_engine.get_statistics().added_last_24h} nouveaux IOCs ajoutés dans les dernières 24h",
            "severity": "medium",
            "confidence": "high"
        })
    
    # Top menaces
    stats = ti_engine.get_statistics()
    if stats.top_threat_actors:
        top_actor = stats.top_threat_actors[0]
        insights.append({
            "type": "attribution",
            "title": f"Threat Actor le plus actif: {top_actor['name']}",
            "description": f"{top_actor['ioc_count']} IOCs associés",
            "severity": "high",
            "confidence": "medium"
        })
    
    return insights


async def _get_recent_threats() -> List[Dict[str, Any]]:
    """Récupère les menaces récentes"""
    recent = []
    now = datetime.now()
    
    for ioc in sorted(ti_engine.iocs.values(), key=lambda x: x.created_at, reverse=True)[:10]:
        recent.append({
            "ioc_value": ioc.value,
            "type": ioc.type.value,
            "severity": ioc.severity.value,
            "threat_type": ioc.threat_type.value,
            "created_at": ioc.created_at.isoformat(),
            "age_hours": (now - ioc.created_at).total_seconds() / 3600
        })
    
    return recent


async def _get_feed_activity() -> Dict[str, Any]:
    """Récupère l'activité des feeds"""
    return {
        "last_updates": [
            {
                "feed_name": feed.name,
                "last_update": feed.last_update.isoformat() if feed.last_update else None,
                "status": feed.status.value,
                "iocs_imported": feed.iocs_imported
            }
            for feed in sorted(ti_engine.cti_feeds.values(), 
                              key=lambda x: x.last_update or datetime.min, reverse=True)[:5]
        ]
    }


def _generate_dashboard_recommendations(stats: IOCStatistics, engine_status: Dict) -> List[str]:
    """Génère des recommandations pour le dashboard"""
    recommendations = []
    
    if not engine_status["is_running"]:
        recommendations.append("⚠️ Démarrer le moteur de threat intelligence")
    
    if stats.false_positives / max(stats.total_iocs, 1) > 0.1:
        recommendations.append("🔍 Réviser les IOCs marqués comme faux positifs")
    
    if stats.expiring_soon > 0:
        recommendations.append(f"⏰ {stats.expiring_soon} IOCs expirent bientôt - revalidation nécessaire")
    
    if engine_status["active_feeds"] == 0:
        recommendations.append("📡 Configurer des feeds CTI pour automatiser la collecte")
    
    recommendations.extend([
        "🔄 Réviser régulièrement les attributions de menaces",
        "📊 Analyser les tendances pour optimiser la détection",
        "🤝 Partager l'intelligence avec l'équipe SOC"
    ])
    
    return recommendations


async def _build_ioc_context(ioc: IOC) -> Dict[str, Any]:
    """Construit le contexte d'un IOC"""
    return {
        "threat_level": ioc.severity.value,
        "confidence_level": ioc.confidence.value,
        "attribution": {
            "threat_actor": ioc.threat_actor,
            "campaign": ioc.campaign,
            "malware_family": ioc.malware_family
        },
        "temporal": {
            "first_seen": ioc.first_seen.isoformat(),
            "last_seen": ioc.last_seen.isoformat(),
            "age_days": (datetime.now() - ioc.first_seen).days
        }
    }


def _generate_ioc_recommendations(ioc: IOC) -> List[str]:
    """Génère des recommandations pour un IOC"""
    recommendations = []
    
    if ioc.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH]:
        recommendations.append("🚨 IOC haute priorité - surveillance immédiate requise")
        recommendations.append("🔍 Vérifier la présence dans les logs réseau et système")
    
    if ioc.type == IOCType.IP_ADDRESS:
        recommendations.append("🛡️ Bloquer l'adresse IP dans le firewall")
        recommendations.append("🌐 Vérifier la géolocalisation et l'ASN")
    elif ioc.type == IOCType.DOMAIN:
        recommendations.append("🔒 Bloquer le domaine dans le DNS")
        recommendations.append("📋 Vérifier les sous-domaines associés")
    elif ioc.type == IOCType.FILE_HASH:
        recommendations.append("🦠 Scanner les systèmes pour ce hash")
        recommendations.append("🛡️ Ajouter à la signature antivirus")
    
    return recommendations


def _determine_relationship_type(ioc1: IOC, ioc2: IOC) -> str:
    """Détermine le type de relation entre deux IOCs"""
    if ioc1.threat_actor and ioc1.threat_actor == ioc2.threat_actor:
        return "same_threat_actor"
    if ioc1.campaign and ioc1.campaign == ioc2.campaign:
        return "same_campaign"
    if ioc1.malware_family and ioc1.malware_family == ioc2.malware_family:
        return "same_malware_family"
    if len(set(ioc1.tags) & set(ioc2.tags)) >= 2:
        return "common_tags"
    return "related"


def _suggest_ioc_actions(ioc: IOC) -> List[str]:
    """Suggère des actions pour un IOC"""
    actions = []
    
    if not ioc.is_active:
        actions.append("Réactiver l'IOC si encore pertinent")
    
    if ioc.confidence == IOCConfidence.LOW:
        actions.append("Enrichir l'IOC pour améliorer la confiance")
    
    if not ioc.threat_actor and not ioc.campaign:
        actions.append("Analyser l'attribution potentielle")
    
    if (datetime.now() - ioc.last_seen).days > 30:
        actions.append("Vérifier la pertinence - dernière détection ancienne")
    
    return actions


def _generate_search_summary(results: List[IOC]) -> Dict[str, Any]:
    """Génère un résumé des résultats de recherche"""
    if not results:
        return {"message": "Aucun IOC trouvé"}
    
    by_severity = {}
    by_type = {}
    
    for ioc in results:
        by_severity[ioc.severity.value] = by_severity.get(ioc.severity.value, 0) + 1
        by_type[ioc.type.value] = by_type.get(ioc.type.value, 0) + 1
    
    return {
        "total_found": len(results),
        "by_severity": by_severity,
        "by_type": by_type,
        "most_common_severity": max(by_severity, key=by_severity.get) if by_severity else "N/A",
        "most_common_type": max(by_type, key=by_type.get) if by_type else "N/A"
    }


def _generate_search_facets(results: List[IOC]) -> Dict[str, Any]:
    """Génère des facettes pour la recherche"""
    facets = {
        "sources": {},
        "threat_actors": {},
        "campaigns": {},
        "tags": {}
    }
    
    for ioc in results:
        # Sources
        facets["sources"][ioc.source] = facets["sources"].get(ioc.source, 0) + 1
        
        # Threat actors
        if ioc.threat_actor:
            facets["threat_actors"][ioc.threat_actor] = facets["threat_actors"].get(ioc.threat_actor, 0) + 1
        
        # Campaigns
        if ioc.campaign:
            facets["campaigns"][ioc.campaign] = facets["campaigns"].get(ioc.campaign, 0) + 1
        
        # Tags
        for tag in ioc.tags:
            facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
    
    return facets


def _assess_ioc_risk(ioc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Évalue le risque d'un IOC"""
    severity = ioc_data.get("severity", "low")
    confidence = ioc_data.get("confidence", "low") 
    is_active = ioc_data.get("is_active", True)
    
    risk_score = 0
    if severity == "critical":
        risk_score += 40
    elif severity == "high":
        risk_score += 30
    elif severity == "medium":
        risk_score += 20
    elif severity == "low":
        risk_score += 10
    
    if confidence == "high":
        risk_score += 30
    elif confidence == "medium":
        risk_score += 20
    elif confidence == "low":
        risk_score += 10
    
    if not is_active:
        risk_score = risk_score * 0.5
    
    risk_level = "low"
    if risk_score >= 60:
        risk_level = "critical"
    elif risk_score >= 45:
        risk_level = "high"
    elif risk_score >= 30:
        risk_level = "medium"
    
    return {
        "risk_score": min(risk_score, 100),
        "risk_level": risk_level,
        "factors": {
            "severity_weight": severity,
            "confidence_weight": confidence,
            "active_status": is_active
        }
    }


def _analyze_ioc_timeline(ioc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse la timeline d'un IOC"""
    first_seen = datetime.fromisoformat(ioc_data["first_seen"].replace("Z", "+00:00"))
    last_seen = datetime.fromisoformat(ioc_data["last_seen"].replace("Z", "+00:00"))
    now = datetime.now()
    
    age_days = (now - first_seen).days
    activity_span = (last_seen - first_seen).days
    
    return {
        "age_days": age_days,
        "activity_span_days": activity_span,
        "last_activity_days_ago": (now - last_seen).days,
        "activity_frequency": "continuous" if activity_span > 7 else "sporadic",
        "lifecycle_stage": "emerging" if age_days < 30 else "established" if age_days < 90 else "mature"
    }


def _calculate_attribution_confidence(ioc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule la confiance d'attribution"""
    confidence_score = 0
    factors = []
    
    if ioc_data.get("threat_actor"):
        confidence_score += 30
        factors.append("threat_actor_identified")
    
    if ioc_data.get("campaign"):
        confidence_score += 25
        factors.append("campaign_associated")
    
    if ioc_data.get("malware_family"):
        confidence_score += 20
        factors.append("malware_family_known")
    
    if len(ioc_data.get("tags", [])) >= 3:
        confidence_score += 15
        factors.append("rich_tagging")
    
    attribution_level = "low"
    if confidence_score >= 70:
        attribution_level = "high"
    elif confidence_score >= 40:
        attribution_level = "medium"
    
    return {
        "attribution_confidence": confidence_score,
        "attribution_level": attribution_level,
        "confidence_factors": factors
    }


def _assess_feed_health(feed: CTIFeed) -> Dict[str, Any]:
    """Évalue la santé d'un feed"""
    health_score = 100
    issues = []
    
    if feed.status == CTIFeedStatus.ERROR:
        health_score -= 50
        issues.append("feed_error")
    
    if not feed.enabled:
        health_score -= 30
        issues.append("feed_disabled")
    
    if feed.last_update:
        hours_since_update = (datetime.now() - feed.last_update).total_seconds() / 3600
        expected_hours = feed.update_frequency / 3600
        
        if hours_since_update > expected_hours * 2:
            health_score -= 20
            issues.append("outdated")
    
    if feed.iocs_imported == 0:
        health_score -= 15
        issues.append("no_imports")
    
    health_level = "excellent"
    if health_score < 50:
        health_level = "poor"
    elif health_score < 70:
        health_level = "fair"
    elif health_score < 85:
        health_level = "good"
    
    return {
        "health_score": max(health_score, 0),
        "health_level": health_level,
        "issues": issues
    }


def _generate_feed_recommendations(feed: CTIFeed) -> List[str]:
    """Génère des recommandations pour un feed"""
    recommendations = []
    
    if feed.status == CTIFeedStatus.ERROR:
        recommendations.append("🔧 Vérifier la configuration et l'URL du feed")
        recommendations.append("🔑 Valider les credentials d'authentification")
    
    if not feed.enabled:
        recommendations.append("⚡ Activer le feed pour commencer la collecte")
    
    if feed.iocs_imported == 0:
        recommendations.append("📊 Vérifier le format des données du feed")
        recommendations.append("🔍 Tester manuellement l'URL du feed")
    
    if feed.update_frequency > 7200:
        recommendations.append("⏰ Considérer une fréquence de mise à jour plus élevée")
    
    return recommendations


def _generate_statistics_recommendations(stats: IOCStatistics) -> List[str]:
    """Génère des recommandations basées sur les statistiques"""
    recommendations = []
    
    fp_rate = (stats.false_positives / max(stats.total_iocs, 1)) * 100
    if fp_rate > 10:
        recommendations.append(f"⚠️ Taux de faux positifs élevé ({fp_rate:.1f}%) - réviser les IOCs")
    
    if stats.by_confidence.get("low", 0) > stats.total_iocs * 0.3:
        recommendations.append("🔍 Beaucoup d'IOCs à faible confiance - enrichissement recommandé")
    
    if stats.expiring_soon > 0:
        recommendations.append(f"⏰ {stats.expiring_soon} IOCs expirent bientôt")
    
    return recommendations


async def _generate_detailed_threat_insights() -> List[Dict[str, Any]]:
    """Génère des insights détaillés de threat intelligence"""
    insights = []
    
    # Analyse des tendances temporelles
    stats = ti_engine.get_statistics()
    
    if stats.added_last_24h > stats.total_iocs * 0.1:
        insights.append({
            "id": str(uuid.uuid4()),
            "title": "Pic d'activité IOCs détecté",
            "description": f"Augmentation significative: {stats.added_last_24h} nouveaux IOCs en 24h",
            "insight_type": "trend",
            "severity": "medium",
            "confidence": "high",
            "data": {"increase_rate": (stats.added_last_24h / max(stats.total_iocs, 1)) * 100},
            "recommendations": [
                "Analyser les sources de ces nouveaux IOCs",
                "Vérifier s'il s'agit d'une campagne coordonnée",
                "Renforcer la surveillance"
            ]
        })
    
    # Analyse d'attribution
    if stats.top_threat_actors:
        top_actor = stats.top_threat_actors[0]
        insights.append({
            "id": str(uuid.uuid4()),
            "title": f"Activité soutenue: {top_actor['name']}",
            "description": f"Threat actor le plus actif avec {top_actor['ioc_count']} IOCs",
            "insight_type": "attribution",
            "severity": "high",
            "confidence": "medium",
            "data": {"actor_name": top_actor['name'], "ioc_count": top_actor['ioc_count']},
            "recommendations": [
                "Analyser les TTPs de ce threat actor",
                "Renforcer les défenses contre ses techniques",
                "Surveiller ses IOCs prioritairement"
            ]
        })
    
    # Analyse de qualité
    fp_rate = (stats.false_positives / max(stats.total_iocs, 1)) * 100
    if fp_rate > 15:
        insights.append({
            "id": str(uuid.uuid4()),
            "title": "Qualité des IOCs préoccupante",
            "description": f"Taux de faux positifs élevé: {fp_rate:.1f}%",
            "insight_type": "anomaly",
            "severity": "medium",
            "confidence": "high",
            "data": {"false_positive_rate": fp_rate},
            "recommendations": [
                "Réviser les processus de validation des IOCs",
                "Améliorer les critères de qualité",
                "Former l'équipe sur l'analyse des IOCs"
            ]
        })
    
    return insights


def _analyze_threat_actor_patterns(actor_name: str, related_iocs: List[Dict]) -> Dict[str, Any]:
    """Analyse les patterns d'un threat actor"""
    if not related_iocs:
        return {}
    
    # Analyse des types d'IOCs utilisés
    ioc_types = {}
    severities = {}
    timeline = {"first_seen": None, "last_seen": None}
    
    for ioc in related_iocs:
        ioc_types[ioc["type"]] = ioc_types.get(ioc["type"], 0) + 1
        severities[ioc["severity"]] = severities.get(ioc["severity"], 0) + 1
        
        first_seen = datetime.fromisoformat(ioc["first_seen"])
        if not timeline["first_seen"] or first_seen < timeline["first_seen"]:
            timeline["first_seen"] = first_seen
        if not timeline["last_seen"] or first_seen > timeline["last_seen"]:
            timeline["last_seen"] = first_seen
    
    # TTPs supposées basées sur les IOCs
    ttps = []
    if "ip_address" in ioc_types:
        ttps.append("T1071.001 - Application Layer Protocol: Web Protocols")
    if "domain" in ioc_types:
        ttps.append("T1071.004 - Application Layer Protocol: DNS")
    if "file_hash" in ioc_types:
        ttps.append("T1204 - User Execution")
    
    return {
        "activity_span": {
            "first_activity": timeline["first_seen"].isoformat() if timeline["first_seen"] else None,
            "last_activity": timeline["last_seen"].isoformat() if timeline["last_seen"] else None,
            "duration_days": (timeline["last_seen"] - timeline["first_seen"]).days if timeline["first_seen"] and timeline["last_seen"] else 0
        },
        "ioc_preferences": ioc_types,
        "severity_distribution": severities,
        "suspected_ttps": ttps,
        "activity_level": "high" if len(related_iocs) > 20 else "medium" if len(related_iocs) > 10 else "low"
    }