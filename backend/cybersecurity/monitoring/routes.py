"""
Routes API pour le service Monitoring 24/7
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, date, timedelta

from .models import (
    SecurityAlert, MonitoringRule, CreateAlertRequest, UpdateAlertRequest,
    CreateRuleRequest, MetricQueryRequest, AlertSearchRequest, MonitoringStatusResponse,
    AlertStatistics, MetricQueryResponse, AlertSeverity, AlertStatus, MonitoringSource,
    MonitoringReport
)
from .monitoring_engine import MonitoringEngine
from database import get_database

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Instance du moteur de monitoring
monitoring_engine = MonitoringEngine()

# Flag pour savoir si le monitoring est démarré
monitoring_started = False

@router.get("/")
async def monitoring_status():
    """Status du service Monitoring 24/7"""
    stats = monitoring_engine.get_monitoring_statistics()
    
    return {
        "status": "operational",
        "service": "Monitoring 24/7",
        "version": "1.0.0-portable",
        "features": {
            "real_time_monitoring": True,
            "automated_alerts": True,
            "correlation_engine": True,
            "custom_rules": True,
            "system_health": True,
            "performance_metrics": True,
            "reporting": True,
            "24_7_surveillance": True
        },
        "monitoring_sources": [source.value for source in MonitoringSource],
        "alert_severities": [sev.value for sev in AlertSeverity],
        "alert_statuses": [status.value for status in AlertStatus],
        "is_monitoring_active": stats["is_monitoring_active"],
        "uptime": stats["uptime_formatted"],
        "active_alerts": stats["active_alerts"],
        "monitoring_rules": stats["monitoring_rules"],
        "system_health": stats["system_health"]
    }


@router.post("/start")
async def start_monitoring():
    """Démarre le monitoring 24/7"""
    global monitoring_started
    
    if monitoring_started:
        return {
            "status": "already_running",
            "message": "Le monitoring 24/7 est déjà actif",
            "uptime": monitoring_engine.get_monitoring_statistics()["uptime_formatted"]
        }
    
    try:
        result = await monitoring_engine.start_monitoring()
        monitoring_started = True
        
        # Créer quelques règles de monitoring par défaut
        await _create_default_monitoring_rules()
        
        return {
            "status": "success",
            "message": "Monitoring 24/7 démarré avec succès",
            "details": result,
            "default_rules_created": True,
            "next_steps": [
                "Consulter /api/monitoring/dashboard pour voir l'état",
                "Configurer des règles personnalisées si besoin",
                "Les alertes seront générées automatiquement"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur démarrage monitoring: {str(e)}")


@router.post("/stop")
async def stop_monitoring():
    """Arrête le monitoring 24/7"""
    global monitoring_started
    
    try:
        result = await monitoring_engine.stop_monitoring()
        monitoring_started = False
        
        return {
            "status": "success",
            "message": "Monitoring 24/7 arrêté avec succès",
            "details": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur arrêt monitoring: {str(e)}")


@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Tableau de bord du monitoring en temps réel"""
    try:
        stats = monitoring_engine.get_monitoring_statistics()
        realtime_metrics = await monitoring_engine.get_realtime_metrics()
        
        # Compter alertes par sévérité
        alerts_by_severity = {}
        alerts_by_status = {}
        
        for alert in monitoring_engine.active_alerts.values():
            # Par sévérité
            alerts_by_severity[alert.severity.value] = alerts_by_severity.get(alert.severity.value, 0) + 1
            # Par statut
            alerts_by_status[alert.status.value] = alerts_by_status.get(alert.status.value, 0) + 1
        
        # Alertes critiques actives
        critical_active = len([
            alert for alert in monitoring_engine.active_alerts.values()
            if alert.severity == AlertSeverity.CRITICAL and alert.status == AlertStatus.ACTIVE
        ])
        
        # Alertes récentes (24h)
        now = datetime.now()
        alerts_24h = len([
            alert for alert in monitoring_engine.active_alerts.values()
            if (now - alert.detected_at).days == 0
        ])
        
        return {
            "overview": {
                "monitoring_status": "active" if stats["is_monitoring_active"] else "inactive",
                "uptime": stats["uptime_formatted"],
                "total_alerts": stats["active_alerts"],
                "critical_active_alerts": critical_active,
                "alerts_last_24h": alerts_24h,
                "monitoring_rules": stats["monitoring_rules"],
                "metrics_collected": stats["performance"]["metrics_collected"]
            },
            "alerts_summary": {
                "by_severity": alerts_by_severity,
                "by_status": alerts_by_status
            },
            "realtime_metrics": realtime_metrics,
            "system_health": stats["system_health"],
            "performance": {
                "alerts_processed": stats["performance"]["alerts_processed"],
                "rules_evaluated": stats["performance"]["rules_evaluated"],
                "metrics_collected": stats["performance"]["metrics_collected"]
            },
            "priority_actions": _generate_priority_actions(monitoring_engine.active_alerts, critical_active),
            "recommendations": _generate_dashboard_recommendations(stats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération dashboard: {str(e)}")


@router.post("/alerts")
async def create_alert(alert_request: CreateAlertRequest, background_tasks: BackgroundTasks):
    """Crée une nouvelle alerte manuellement"""
    try:
        alert = await monitoring_engine.create_alert(alert_request)
        
        # Sauvegarder en base en arrière-plan
        background_tasks.add_task(save_alert_to_db, alert)
        
        return {
            "status": "success",
            "message": f"Alerte '{alert.title}' créée avec succès",
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "source": alert.source.value,
                "detected_at": alert.detected_at.isoformat(),
                "remediation_steps_count": len(alert.remediation_steps)
            },
            "recommendations": _generate_alert_recommendations(alert),
            "next_steps": [
                "Assigner l'alerte à un analyste si nécessaire",
                "Suivre les étapes de remédiation suggérées",
                "Documenter les actions prises"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création alerte: {str(e)}")


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """Récupère les détails d'une alerte"""
    if alert_id not in monitoring_engine.active_alerts:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    alert = monitoring_engine.active_alerts[alert_id]
    
    # Calculer des métriques
    age_minutes = (datetime.now() - alert.detected_at).total_seconds() / 60
    is_overdue = age_minutes > 240 and alert.status == AlertStatus.ACTIVE  # 4 heures
    
    return {
        "alert": alert.dict(),
        "metrics": {
            "age_minutes": round(age_minutes, 2),
            "is_overdue": is_overdue,
            "escalation_count": alert.escalation_count,
            "remediation_progress": f"0/{len(alert.remediation_steps)}"  # Simplifié
        },
        "related_alerts": _find_related_alerts(alert),
        "suggested_actions": _suggest_alert_actions(alert)
    }


@router.put("/alerts/{alert_id}")
async def update_alert(alert_id: str, update_request: UpdateAlertRequest):
    """Met à jour une alerte"""
    try:
        alert = await monitoring_engine.update_alert(alert_id, update_request)
        
        return {
            "status": "success",
            "message": "Alerte mise à jour avec succès",
            "alert": {
                "id": alert.id,
                "status": alert.status.value,
                "assigned_to": alert.assigned_to,
                "updated_at": alert.updated_at.isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour alerte: {str(e)}")


@router.post("/alerts/search")
async def search_alerts(search_request: AlertSearchRequest):
    """Recherche des alertes selon des critères"""
    try:
        results = []
        
        for alert in monitoring_engine.active_alerts.values():
            # Appliquer les filtres
            if search_request.query and search_request.query.lower() not in alert.title.lower() and search_request.query.lower() not in alert.description.lower():
                continue
            
            if search_request.severity and alert.severity not in search_request.severity:
                continue
                
            if search_request.status and alert.status not in search_request.status:
                continue
                
            if search_request.source and alert.source not in search_request.source:
                continue
                
            if search_request.assigned_to and alert.assigned_to != search_request.assigned_to:
                continue
                
            if search_request.date_from and alert.detected_at.date() < search_request.date_from:
                continue
                
            if search_request.date_to and alert.detected_at.date() > search_request.date_to:
                continue
            
            # Filtre par tags
            if search_request.tags:
                if not any(tag in alert.tags for tag in search_request.tags):
                    continue
            
            results.append({
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "source": alert.source.value,
                "detected_at": alert.detected_at.isoformat(),
                "assigned_to": alert.assigned_to,
                "tags": alert.tags,
                "age_minutes": (datetime.now() - alert.detected_at).total_seconds() / 60
            })
        
        # Trier par date de détection (plus récent en premier)
        results.sort(key=lambda x: x["detected_at"], reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[search_request.offset:search_request.offset + search_request.limit]
        
        return {
            "alerts": paginated_results,
            "total_results": total,
            "search_criteria": search_request.dict(),
            "summary": _generate_search_summary(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche alertes: {str(e)}")


@router.post("/rules")
async def create_monitoring_rule(rule_request: CreateRuleRequest):
    """Crée une nouvelle règle de monitoring"""
    try:
        rule = await monitoring_engine.create_monitoring_rule(rule_request)
        
        return {
            "status": "success",
            "message": f"Règle de monitoring '{rule.name}' créée avec succès",
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "condition": rule.condition,
                "severity": rule.severity.value,
                "enabled": rule.enabled,
                "evaluation_window": rule.evaluation_window,
                "threshold_value": rule.threshold_value,
                "threshold_operator": rule.threshold_operator
            },
            "recommendations": [
                "Surveiller les alertes générées par cette règle",
                "Ajuster les seuils si nécessaire",
                "Configurer les canaux de notification appropriés"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création règle: {str(e)}")


@router.get("/rules")
async def list_monitoring_rules():
    """Liste toutes les règles de monitoring"""
    rules_summary = []
    
    for rule in monitoring_engine.monitoring_rules.values():
        rules_summary.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "condition": rule.condition,
            "severity": rule.severity.value,
            "enabled": rule.enabled,
            "source": rule.source.value,
            "threshold_value": rule.threshold_value,
            "threshold_operator": rule.threshold_operator,
            "created_at": rule.created_at.isoformat(),
            "tags": rule.tags
        })
    
    return {
        "rules": rules_summary,
        "total_rules": len(rules_summary),
        "active_rules": len([r for r in monitoring_engine.monitoring_rules.values() if r.enabled])
    }


@router.get("/metrics/realtime")
async def get_realtime_metrics():
    """Récupère les métriques en temps réel"""
    try:
        metrics = await monitoring_engine.get_realtime_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "collection_active": monitoring_engine.is_monitoring_active,
            "metrics_info": {
                "cpu_usage": "Pourcentage d'utilisation CPU",
                "memory_usage": "Pourcentage d'utilisation mémoire",
                "disk_usage": "Pourcentage d'utilisation disque",
                "network_io": "I/O réseau total (bytes)",
                "active_connections": "Nombre de connexions actives"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération métriques: {str(e)}")


@router.post("/metrics/query")
async def query_metrics(query_request: MetricQueryRequest):
    """Interroge les métriques historiques"""
    try:
        data_points = await monitoring_engine.query_metrics(query_request)
        
        return MetricQueryResponse(
            metric_name=query_request.metric_name or "all",
            data_points=data_points,
            total_points=len(data_points),
            aggregation=query_request.aggregation,
            interval=query_request.interval,
            query_duration=0.1  # Temps de requête simulé
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur requête métriques: {str(e)}")


@router.get("/health")
async def get_system_health():
    """État de santé du système surveillé"""
    stats = monitoring_engine.get_monitoring_statistics()
    
    overall_health = "healthy"
    health_details = stats["system_health"]
    
    # Déterminer l'état global
    if any(component["status"] == "critical" for component in health_details.values()):
        overall_health = "critical"
    elif any(component["status"] == "warning" for component in health_details.values()):
        overall_health = "warning"
    
    return {
        "overall_health": overall_health,
        "components": health_details,
        "monitoring_active": stats["is_monitoring_active"],
        "last_check": datetime.now().isoformat(),
        "recommendations": _generate_health_recommendations(health_details)
    }


@router.post("/report")
async def generate_monitoring_report(background_tasks: BackgroundTasks, period_days: int = 7):
    """Génère un rapport de monitoring"""
    try:
        report = await monitoring_engine.generate_monitoring_report(period_days)
        
        # Optionnellement sauvegarder le rapport
        background_tasks.add_task(save_report_to_db, report)
        
        return {
            "status": "success",
            "message": f"Rapport de monitoring généré pour {period_days} jours",
            "report": report.dict(),
            "export_options": {
                "pdf": f"/reports/monitoring/{report.id}.pdf",
                "html": f"/reports/monitoring/{report.id}.html",
                "json": f"/reports/monitoring/{report.id}.json"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")


@router.get("/statistics")
async def get_monitoring_statistics():
    """Statistiques détaillées du monitoring"""
    try:
        stats = monitoring_engine.get_monitoring_statistics()
        
        # Statistiques additionnelles
        alert_stats = AlertStatistics(
            total_alerts=len(monitoring_engine.active_alerts),
            by_severity=stats["alert_counters"],
            by_status={},
            by_source={},
            alerts_last_24h=0,
            avg_resolution_time=None,
            false_positive_rate=0.0
        )
        
        # Calculer statistiques par statut et source
        for alert in monitoring_engine.active_alerts.values():
            alert_stats.by_status[alert.status.value] = alert_stats.by_status.get(alert.status.value, 0) + 1
            alert_stats.by_source[alert.source.value] = alert_stats.by_source.get(alert.source.value, 0) + 1
            
            # Alertes 24h
            if (datetime.now() - alert.detected_at).days == 0:
                alert_stats.alerts_last_24h += 1
        
        return {
            "monitoring_statistics": stats,
            "alert_statistics": alert_stats.dict(),
            "trends": {
                "alerts_trend": "stable",
                "performance_trend": "improving",
                "health_trend": "good"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques: {str(e)}")


# Fonctions utilitaires privées

async def _create_default_monitoring_rules():
    """Crée des règles de monitoring par défaut"""
    default_rules = [
        CreateRuleRequest(
            name="CPU Usage High",
            description="Alerte quand l'usage CPU dépasse 80%",
            condition="cpu_usage > 80",
            severity=AlertSeverity.HIGH,
            source=MonitoringSource.SYSTEM,
            threshold_value=80.0,
            threshold_operator=">",
            evaluation_window=300,
            created_by="system",
            tags=["cpu", "system", "performance"]
        ),
        CreateRuleRequest(
            name="Memory Usage Critical",
            description="Alerte critique quand la mémoire dépasse 90%",
            condition="memory_usage > 90",
            severity=AlertSeverity.CRITICAL,
            source=MonitoringSource.SYSTEM,
            threshold_value=90.0,
            threshold_operator=">",
            evaluation_window=180,
            created_by="system",
            tags=["memory", "system", "critical"]
        ),
        CreateRuleRequest(
            name="Disk Usage Warning",
            description="Alerte quand l'espace disque dépasse 85%",
            condition="disk_usage > 85",
            severity=AlertSeverity.MEDIUM,
            source=MonitoringSource.SYSTEM,
            threshold_value=85.0,
            threshold_operator=">",
            evaluation_window=600,
            created_by="system",
            tags=["disk", "system", "storage"]
        )
    ]
    
    for rule_request in default_rules:
        try:
            await monitoring_engine.create_monitoring_rule(rule_request)
        except Exception as e:
            print(f"Erreur création règle par défaut {rule_request.name}: {e}")


async def save_alert_to_db(alert: SecurityAlert):
    """Sauvegarde une alerte en base de données"""
    try:
        db = await get_database()
        collection = await db.get_collection("monitoring_alerts")
        await collection.insert_one(alert.dict())
    except Exception as e:
        print(f"Erreur sauvegarde alerte {alert.id}: {e}")


async def save_report_to_db(report: MonitoringReport):
    """Sauvegarde un rapport en base de données"""
    try:
        db = await get_database()
        collection = await db.get_collection("monitoring_reports")
        await collection.insert_one(report.dict())
    except Exception as e:
        print(f"Erreur sauvegarde rapport {report.id}: {e}")


def _generate_priority_actions(alerts: Dict, critical_count: int) -> List[str]:
    """Génère les actions prioritaires"""
    actions = []
    
    if critical_count > 0:
        actions.append(f"🚨 URGENT: {critical_count} alertes critiques à traiter immédiatement")
    
    active_count = len([a for a in alerts.values() if a.status == AlertStatus.ACTIVE])
    if active_count > 10:
        actions.append(f"⚠️ CHARGE: {active_count} alertes actives - prioriser les traitements")
    
    unassigned_count = len([a for a in alerts.values() if not a.assigned_to and a.status == AlertStatus.ACTIVE])
    if unassigned_count > 0:
        actions.append(f"👤 ASSIGNATION: {unassigned_count} alertes non assignées")
    
    return actions


def _generate_dashboard_recommendations(stats: Dict) -> List[str]:
    """Génère des recommandations pour le dashboard"""
    recommendations = []
    
    if not stats["is_monitoring_active"]:
        recommendations.append("⚠️ Démarrer le monitoring 24/7 pour une surveillance continue")
    
    if stats["active_alerts"] > 20:
        recommendations.append("📈 Volume élevé d'alertes - réviser les règles de monitoring")
    
    if stats["monitoring_rules"] < 5:
        recommendations.append("📋 Ajouter plus de règles de monitoring personnalisées")
    
    recommendations.extend([
        "🔄 Réviser régulièrement les faux positifs",
        "📊 Analyser les tendances pour optimiser les seuils",
        "🤖 Automatiser les réponses aux alertes récurrentes"
    ])
    
    return recommendations


def _generate_alert_recommendations(alert: SecurityAlert) -> List[str]:
    """Génère des recommandations pour une alerte"""
    recommendations = []
    
    if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
        recommendations.append("🚨 Alerte haute priorité - traitement immédiat requis")
        recommendations.append("📞 Notifier l'équipe de sécurité")
    
    if alert.source == MonitoringSource.SYSTEM:
        recommendations.append("🔍 Vérifier les ressources et performances système")
    elif alert.source == MonitoringSource.SECURITY:
        recommendations.append("🛡️ Analyser les logs de sécurité et les accès")
    
    recommendations.extend([
        "📋 Suivre les étapes de remédiation suggérées",
        "📝 Documenter toutes les actions prises",
        "🔄 Valider la résolution avant fermeture"
    ])
    
    return recommendations


def _find_related_alerts(alert: SecurityAlert) -> List[Dict]:
    """Trouve les alertes liées"""
    related = []
    
    for other_alert in monitoring_engine.active_alerts.values():
        if other_alert.id == alert.id:
            continue
        
        # Même source et catégorie
        if other_alert.source == alert.source and other_alert.category == alert.category:
            related.append({
                "id": other_alert.id,
                "title": other_alert.title,
                "relationship": "same_category",
                "severity": other_alert.severity.value
            })
        
        # Même correlation_id
        if alert.correlation_id and other_alert.correlation_id == alert.correlation_id:
            related.append({
                "id": other_alert.id,
                "title": other_alert.title,
                "relationship": "correlated",
                "severity": other_alert.severity.value
            })
    
    return related[:5]  # Limiter à 5 résultats


def _suggest_alert_actions(alert: SecurityAlert) -> List[str]:
    """Suggère des actions pour une alerte"""
    if alert.status == AlertStatus.ACTIVE:
        return [
            "Assigner l'alerte à un analyste",
            "Commencer l'investigation",
            "Documenter les findings initiaux"
        ]
    elif alert.status == AlertStatus.ACKNOWLEDGED:
        return [
            "Suivre les étapes de remédiation",
            "Mettre à jour le statut régulièrement",
            "Coordonner avec les équipes concernées"
        ]
    else:
        return [
            "Valider la résolution",
            "Documenter les leçons apprises",
            "Mettre à jour les procédures si nécessaire"
        ]


def _generate_search_summary(results: List) -> Dict:
    """Génère un résumé des résultats de recherche"""
    if not results:
        return {"message": "Aucune alerte trouvée"}
    
    by_severity = {}
    for result in results:
        severity = result["severity"]
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    return {
        "total_found": len(results),
        "by_severity": by_severity,
        "most_common_severity": max(by_severity, key=by_severity.get) if by_severity else "N/A"
    }


def _generate_health_recommendations(health_details: Dict) -> List[str]:
    """Génère des recommandations de santé système"""
    recommendations = []
    
    for component, details in health_details.items():
        if details["status"] == "critical":
            recommendations.append(f"🚨 URGENT: Composant {component} en état critique")
        elif details["status"] == "warning":
            recommendations.append(f"⚠️ ATTENTION: Composant {component} nécessite surveillance")
    
    recommendations.extend([
        "🔄 Surveiller régulièrement l'état de santé",
        "📈 Analyser les tendances de performance",
        "🛠️ Maintenir les composants système à jour"
    ])
    
    return recommendations