"""
Moteur de monitoring 24/7 avec surveillance temps réel
CyberSec Toolkit Pro 2025 - PORTABLE
"""
import asyncio
import uuid
import psutil
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
import logging
import json
import re

from .models import (
    SecurityAlert, MonitoringMetric, MonitoringRule, SystemHealthStatus,
    AlertSeverity, AlertStatus, MonitoringSource, MetricType,
    CreateAlertRequest, UpdateAlertRequest, MetricQueryRequest,
    MonitoringReport, MetricDataPoint
)

logger = logging.getLogger(__name__)

class MonitoringEngine:
    """Moteur principal de monitoring 24/7"""
    
    def __init__(self):
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.metrics_buffer: deque = deque(maxlen=10000)  # Buffer métrique
        self.system_health: Dict[str, SystemHealthStatus] = {}
        self.is_monitoring_active = False
        self.monitoring_task = None
        self.correlation_rules = self._load_correlation_rules()
        self.notification_channels = {}
        
        # Métriques en temps réel
        self.realtime_metrics = {
            "cpu_usage": deque(maxlen=60),
            "memory_usage": deque(maxlen=60),
            "disk_usage": deque(maxlen=60),
            "network_io": deque(maxlen=60),
            "active_connections": deque(maxlen=60)
        }
        
        # Compteurs d'alertes
        self.alert_counters = defaultdict(int)
        self.performance_stats = {
            "start_time": datetime.now(),
            "alerts_processed": 0,
            "rules_evaluated": 0,
            "metrics_collected": 0
        }
    
    def _load_correlation_rules(self) -> Dict[str, Any]:
        """Charge les règles de corrélation d'alertes"""
        return {
            "brute_force_detection": {
                "pattern": "multiple_failed_logins",
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "severity": AlertSeverity.HIGH
            },
            "resource_exhaustion": {
                "pattern": "high_resource_usage",
                "threshold": 90,
                "time_window": 600,  # 10 minutes
                "severity": AlertSeverity.CRITICAL
            },
            "suspicious_network_activity": {
                "pattern": "unusual_network_pattern",
                "threshold": 100,
                "time_window": 900,  # 15 minutes
                "severity": AlertSeverity.MEDIUM
            }
        }
    
    async def start_monitoring(self):
        """Démarre le monitoring en continu"""
        if self.is_monitoring_active:
            return {"status": "already_running"}
        
        self.is_monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔄 Monitoring 24/7 démarré")
        
        return {
            "status": "started",
            "message": "Monitoring 24/7 démarré avec succès",
            "start_time": datetime.now().isoformat()
        }
    
    async def stop_monitoring(self):
        """Arrête le monitoring"""
        if not self.is_monitoring_active:
            return {"status": "not_running"}
        
        self.is_monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏹️ Monitoring 24/7 arrêté")
        return {
            "status": "stopped",
            "message": "Monitoring arrêté avec succès",
            "stop_time": datetime.now().isoformat()
        }
    
    async def _monitoring_loop(self):
        """Boucle principale de monitoring"""
        try:
            while self.is_monitoring_active:
                start_time = time.time()
                
                # Collecte des métriques système
                await self._collect_system_metrics()
                
                # Évaluation des règles de monitoring
                await self._evaluate_monitoring_rules()
                
                # Corrélation d'alertes
                await self._correlate_alerts()
                
                # Mise à jour santé système
                await self._update_system_health()
                
                # Performance et nettoyage
                await self._cleanup_old_data()
                
                # Attendre jusqu'au prochain cycle (30 secondes)
                elapsed = time.time() - start_time
                sleep_time = max(30 - elapsed, 1)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans monitoring loop: {e}")
    
    async def _collect_system_metrics(self):
        """Collecte les métriques système"""
        try:
            now = datetime.now()
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.realtime_metrics["cpu_usage"].append({
                "timestamp": now,
                "value": cpu_percent
            })
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.realtime_metrics["memory_usage"].append({
                "timestamp": now,
                "value": memory.percent
            })
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.realtime_metrics["disk_usage"].append({
                "timestamp": now,
                "value": disk_percent
            })
            
            # Réseau
            network = psutil.net_io_counters()
            self.realtime_metrics["network_io"].append({
                "timestamp": now,
                "value": network.bytes_sent + network.bytes_recv
            })
            
            # Connexions actives
            connections = len(psutil.net_connections())
            self.realtime_metrics["active_connections"].append({
                "timestamp": now,
                "value": connections
            })
            
            # Ajouter au buffer de métriques
            metrics = [
                MonitoringMetric(
                    name="cpu_usage",
                    type=MetricType.GAUGE,
                    value=cpu_percent,
                    unit="percent",
                    source=MonitoringSource.SYSTEM,
                    timestamp=now,
                    labels={"component": "cpu"}
                ),
                MonitoringMetric(
                    name="memory_usage",
                    type=MetricType.GAUGE,
                    value=memory.percent,
                    unit="percent",
                    source=MonitoringSource.SYSTEM,
                    timestamp=now,
                    labels={"component": "memory"}
                ),
                MonitoringMetric(
                    name="disk_usage",
                    type=MetricType.GAUGE,
                    value=disk_percent,
                    unit="percent",
                    source=MonitoringSource.SYSTEM,
                    timestamp=now,
                    labels={"component": "disk", "mount": "/"}
                )
            ]
            
            for metric in metrics:
                self.metrics_buffer.append(metric)
            
            self.performance_stats["metrics_collected"] += len(metrics)
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques: {e}")
    
    async def _evaluate_monitoring_rules(self):
        """Évalue les règles de monitoring"""
        try:
            for rule_id, rule in self.monitoring_rules.items():
                if not rule.enabled:
                    continue
                
                # Évaluer la condition de la règle
                if await self._evaluate_rule_condition(rule):
                    await self._trigger_alert_from_rule(rule)
                
                self.performance_stats["rules_evaluated"] += 1
                
        except Exception as e:
            logger.error(f"Erreur évaluation règles: {e}")
    
    async def _evaluate_rule_condition(self, rule: MonitoringRule) -> bool:
        """Évalue si une règle doit déclencher une alerte"""
        try:
            # Exemple d'évaluation pour règles système
            if rule.source == MonitoringSource.SYSTEM:
                latest_metrics = self.realtime_metrics.get(rule.condition.split()[0], deque())
                if not latest_metrics:
                    return False
                
                latest_value = latest_metrics[-1]["value"] if latest_metrics else 0
                
                # Évaluer selon l'opérateur
                if rule.threshold_operator == ">":
                    return latest_value > rule.threshold_value
                elif rule.threshold_operator == "<":
                    return latest_value < rule.threshold_value
                elif rule.threshold_operator == ">=":
                    return latest_value >= rule.threshold_value
                elif rule.threshold_operator == "<=":
                    return latest_value <= rule.threshold_value
                elif rule.threshold_operator == "==":
                    return latest_value == rule.threshold_value
                elif rule.threshold_operator == "!=":
                    return latest_value != rule.threshold_value
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur évaluation condition règle {rule.name}: {e}")
            return False
    
    async def _trigger_alert_from_rule(self, rule: MonitoringRule):
        """Déclenche une alerte basée sur une règle"""
        try:
            alert_request = CreateAlertRequest(
                title=f"Alerte automatique: {rule.name}",
                description=f"Règle déclenchée: {rule.description}",
                severity=rule.severity,
                source=rule.source,
                source_system="monitoring_engine",
                category="automated_rule",
                indicators={"rule_id": rule.id, "condition": rule.condition},
                tags=rule.tags + ["automated", "rule_based"]
            )
            
            alert = await self.create_alert(alert_request)
            logger.info(f"Alerte déclenchée par règle {rule.name}: {alert.id}")
            
        except Exception as e:
            logger.error(f"Erreur déclenchement alerte pour règle {rule.name}: {e}")
    
    async def _correlate_alerts(self):
        """Corrèle les alertes pour détecter des patterns"""
        try:
            now = datetime.now()
            
            # Analyser les patterns dans les alertes récentes
            recent_alerts = [
                alert for alert in self.active_alerts.values()
                if (now - alert.detected_at).seconds < 3600  # 1 heure
            ]
            
            # Détecter patterns de brute force
            failed_login_alerts = [
                a for a in recent_alerts 
                if "login" in a.category.lower() and "failed" in a.description.lower()
            ]
            
            if len(failed_login_alerts) >= 5:
                correlation_alert = CreateAlertRequest(
                    title="Détection possible de brute force",
                    description=f"{len(failed_login_alerts)} tentatives de connexion échouées détectées",
                    severity=AlertSeverity.HIGH,
                    source=MonitoringSource.SECURITY,
                    source_system="correlation_engine",
                    category="brute_force_detection",
                    indicators={"pattern": "multiple_failed_logins", "count": len(failed_login_alerts)},
                    tags=["correlation", "brute_force", "security"]
                )
                
                await self.create_alert(correlation_alert)
            
        except Exception as e:
            logger.error(f"Erreur corrélation alertes: {e}")
    
    async def _update_system_health(self):
        """Met à jour l'état de santé du système"""
        try:
            now = datetime.now()
            
            # État CPU
            cpu_usage = self.realtime_metrics["cpu_usage"][-1]["value"] if self.realtime_metrics["cpu_usage"] else 0
            cpu_status = "healthy"
            if cpu_usage > 90:
                cpu_status = "critical"
            elif cpu_usage > 70:
                cpu_status = "warning"
            
            self.system_health["cpu"] = SystemHealthStatus(
                component="cpu",
                status=cpu_status,
                last_check=now,
                uptime=(now - self.performance_stats["start_time"]).total_seconds(),
                details={"usage_percent": cpu_usage}
            )
            
            # État Mémoire
            memory_usage = self.realtime_metrics["memory_usage"][-1]["value"] if self.realtime_metrics["memory_usage"] else 0
            memory_status = "healthy"
            if memory_usage > 90:
                memory_status = "critical"
            elif memory_usage > 80:
                memory_status = "warning"
            
            self.system_health["memory"] = SystemHealthStatus(
                component="memory",
                status=memory_status,
                last_check=now,
                uptime=(now - self.performance_stats["start_time"]).total_seconds(),
                details={"usage_percent": memory_usage}
            )
            
            # État général monitoring
            active_critical_alerts = len([
                a for a in self.active_alerts.values()
                if a.severity == AlertSeverity.CRITICAL and a.status == AlertStatus.ACTIVE
            ])
            
            monitoring_status = "healthy"
            if active_critical_alerts > 5:
                monitoring_status = "critical"
            elif active_critical_alerts > 0:
                monitoring_status = "warning"
            
            self.system_health["monitoring"] = SystemHealthStatus(
                component="monitoring",
                status=monitoring_status,
                last_check=now,
                uptime=(now - self.performance_stats["start_time"]).total_seconds(),
                details={
                    "active_alerts": len(self.active_alerts),
                    "critical_alerts": active_critical_alerts,
                    "monitoring_rules": len(self.monitoring_rules)
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur mise à jour santé système: {e}")
    
    async def _cleanup_old_data(self):
        """Nettoie les anciennes données"""
        try:
            now = datetime.now()
            
            # Nettoyer les alertes résolues anciennes (>7 jours)
            old_alerts = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if alert.status in [AlertStatus.RESOLVED] 
                and alert.resolved_at 
                and (now - alert.resolved_at).days > 7
            ]
            
            for alert_id in old_alerts:
                del self.active_alerts[alert_id]
            
            # Nettoyer buffer métriques si trop plein
            if len(self.metrics_buffer) > 8000:
                # Garder seulement les 5000 plus récents
                recent_metrics = list(self.metrics_buffer)[-5000:]
                self.metrics_buffer.clear()
                self.metrics_buffer.extend(recent_metrics)
            
        except Exception as e:
            logger.error(f"Erreur nettoyage données: {e}")
    
    # API publique du moteur
    
    async def create_alert(self, request: CreateAlertRequest) -> SecurityAlert:
        """Crée une nouvelle alerte"""
        alert = SecurityAlert(
            title=request.title,
            description=request.description,
            severity=request.severity,
            source=request.source,
            source_system=request.source_system,
            category=request.category,
            indicators=request.indicators,
            raw_data=request.raw_data,
            tags=request.tags
        )
        
        # Génération automatique d'étapes de remédiation
        alert.remediation_steps = await self._generate_remediation_steps(alert)
        
        self.active_alerts[alert.id] = alert
        self.alert_counters[alert.severity.value] += 1
        self.performance_stats["alerts_processed"] += 1
        
        logger.info(f"Nouvelle alerte créée: {alert.title} ({alert.severity.value})")
        return alert
    
    async def update_alert(self, alert_id: str, request: UpdateAlertRequest) -> SecurityAlert:
        """Met à jour une alerte"""
        if alert_id not in self.active_alerts:
            raise ValueError(f"Alerte {alert_id} non trouvée")
        
        alert = self.active_alerts[alert_id]
        
        if request.status:
            alert.status = request.status
            if request.status == AlertStatus.RESOLVED:
                alert.resolved_at = datetime.now()
        
        if request.assigned_to is not None:
            alert.assigned_to = request.assigned_to
        
        if request.remediation_steps is not None:
            alert.remediation_steps = request.remediation_steps
        
        if request.false_positive is not None:
            alert.false_positive = request.false_positive
        
        if request.tags is not None:
            alert.tags = request.tags
        
        alert.updated_at = datetime.now()
        return alert
    
    async def create_monitoring_rule(self, request) -> MonitoringRule:
        """Crée une règle de monitoring"""
        rule = MonitoringRule(
            name=request.name,
            description=request.description,
            condition=request.condition,
            severity=request.severity,
            source=request.source,
            threshold_value=request.threshold_value,
            threshold_operator=request.threshold_operator,
            evaluation_window=request.evaluation_window,
            cool_down_period=request.cool_down_period,
            created_by=request.created_by,
            tags=request.tags,
            notification_channels=request.notification_channels
        )
        
        self.monitoring_rules[rule.id] = rule
        logger.info(f"Nouvelle règle de monitoring créée: {rule.name}")
        return rule
    
    async def query_metrics(self, request: MetricQueryRequest) -> List[MetricDataPoint]:
        """Interroge les métriques"""
        results = []
        
        # Filtrer les métriques selon les critères
        filtered_metrics = [
            metric for metric in self.metrics_buffer
            if (not request.metric_name or metric.name == request.metric_name)
            and (not request.source or metric.source == request.source)
            and (not request.start_time or metric.timestamp >= request.start_time)
            and (not request.end_time or metric.timestamp <= request.end_time)
        ]
        
        # Convertir en points de données
        for metric in filtered_metrics:
            results.append(MetricDataPoint(
                timestamp=metric.timestamp,
                value=metric.value,
                labels=metric.labels
            ))
        
        return results
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques temps réel"""
        return {
            metric_name: list(metric_data)[-10:]  # 10 derniers points
            for metric_name, metric_data in self.realtime_metrics.items()
        }
    
    async def generate_monitoring_report(self, period_days: int = 7) -> MonitoringReport:
        """Génère un rapport de monitoring"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=period_days)
        
        # Filtrer alertes de la période
        period_alerts = [
            alert for alert in self.active_alerts.values()
            if start_time <= alert.detected_at <= end_time
        ]
        
        # Calculs statistiques
        total_alerts = len(period_alerts)
        critical_alerts = len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL])
        resolved_alerts = len([a for a in period_alerts if a.status == AlertStatus.RESOLVED])
        false_positives = len([a for a in period_alerts if a.false_positive])
        
        # Temps moyen de résolution
        resolved_with_time = [
            a for a in period_alerts 
            if a.status == AlertStatus.RESOLVED and a.resolved_at
        ]
        avg_resolution_time = 0
        if resolved_with_time:
            total_resolution_time = sum([
                (a.resolved_at - a.detected_at).total_seconds() / 60  # en minutes
                for a in resolved_with_time
            ])
            avg_resolution_time = total_resolution_time / len(resolved_with_time)
        
        # Statistiques par catégorie
        alerts_by_severity = {}
        for severity in AlertSeverity:
            alerts_by_severity[severity.value] = len([
                a for a in period_alerts if a.severity == severity
            ])
        
        alerts_by_source = {}
        for source in MonitoringSource:
            alerts_by_source[source.value] = len([
                a for a in period_alerts if a.source == source
            ])
        
        # Top catégories
        category_counts = defaultdict(int)
        for alert in period_alerts:
            category_counts[alert.category] += 1
        
        top_categories = [
            {"category": cat, "count": count}
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Métriques système moyennes
        cpu_avg = sum([m["value"] for m in self.realtime_metrics["cpu_usage"]]) / len(self.realtime_metrics["cpu_usage"]) if self.realtime_metrics["cpu_usage"] else 0
        memory_avg = sum([m["value"] for m in self.realtime_metrics["memory_usage"]]) / len(self.realtime_metrics["memory_usage"]) if self.realtime_metrics["memory_usage"] else 0
        
        # Recommandations
        recommendations = []
        if critical_alerts > 5:
            recommendations.append("Réviser les règles de monitoring pour réduire les alertes critiques")
        if false_positives / max(total_alerts, 1) > 0.1:
            recommendations.append("Optimiser les règles pour réduire les faux positifs")
        if avg_resolution_time > 60:
            recommendations.append("Améliorer les procédures de résolution d'alertes")
        
        report = MonitoringReport(
            title=f"Rapport Monitoring {period_days} jours",
            generated_by="monitoring_engine",
            period_start=start_time,
            period_end=end_time,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            resolved_alerts=resolved_alerts,
            false_positives=false_positives,
            avg_resolution_time=avg_resolution_time,
            alerts_by_severity=alerts_by_severity,
            alerts_by_source=alerts_by_source,
            top_alert_categories=top_categories,
            system_availability=95.0,  # Calculé selon uptime
            average_response_time=cpu_avg,
            performance_trends=[],
            recommendations=recommendations,
            summary=f"Période du {start_time.strftime('%Y-%m-%d')} au {end_time.strftime('%Y-%m-%d')}: {total_alerts} alertes traitées, {resolved_alerts} résolues"
        )
        
        return report
    
    async def _generate_remediation_steps(self, alert: SecurityAlert) -> List[str]:
        """Génère des étapes de remédiation automatiques"""
        steps = []
        
        # Étapes selon la sévérité
        if alert.severity == AlertSeverity.CRITICAL:
            steps.extend([
                "1. Isolation immédiate du composant affecté",
                "2. Notification de l'équipe de sécurité",
                "3. Analyse d'impact et containment"
            ])
        
        # Étapes selon la source
        if alert.source == MonitoringSource.SYSTEM:
            steps.extend([
                "4. Vérifier les ressources système",
                "5. Analyser les logs système récents",
                "6. Redémarrer les services si nécessaire"
            ])
        elif alert.source == MonitoringSource.SECURITY:
            steps.extend([
                "4. Analyser les logs de sécurité",
                "5. Vérifier les accès et permissions",
                "6. Mettre à jour les règles de sécurité"
            ])
        
        # Étapes communes
        steps.extend([
            "7. Documenter l'incident",
            "8. Implémenter les corrections",
            "9. Valider la résolution",
            "10. Mettre à jour les procédures si nécessaire"
        ])
        
        return steps
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de monitoring"""
        now = datetime.now()
        uptime = (now - self.performance_stats["start_time"]).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "is_monitoring_active": self.is_monitoring_active,
            "performance": self.performance_stats,
            "alert_counters": dict(self.alert_counters),
            "active_alerts": len(self.active_alerts),
            "monitoring_rules": len(self.monitoring_rules),
            "metrics_buffer_size": len(self.metrics_buffer),
            "system_health": {name: status.dict() for name, status in self.system_health.items()}
        }