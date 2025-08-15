"""
Moteur Blue Team Defense avec threat hunting et réponse défensive
CyberSec Toolkit Pro 2025 - PORTABLE
"""
import asyncio
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .models import (
    IOC, DetectionRule, Alert, ThreatHunt, DefensiveAction, ThreatIntel, DefenseBaseline,
    ThreatSeverity, AlertStatus, HuntStatus, ResponseAction, DataSource, HuntTechnique,
    CreateIOCRequest, CreateDetectionRuleRequest, CreateAlertRequest, UpdateAlertRequest,
    CreateThreatHuntRequest, UpdateThreatHuntRequest, ExecuteDefensiveActionRequest,
    IOCSearchRequest, AlertSearchRequest, HuntSearchRequest, AlertStatistics,
    HuntStatistics, DefenseInsight
)

logger = logging.getLogger(__name__)

class BlueTeamEngine:
    """Moteur principal Blue Team Defense"""
    
    def __init__(self):
        self.iocs: Dict[str, IOC] = {}
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.threat_hunts: Dict[str, ThreatHunt] = {}
        self.defensive_actions: Dict[str, DefensiveAction] = {}
        self.threat_intel: Dict[str, ThreatIntel] = {}
        self.baselines: Dict[str, DefenseBaseline] = {}
        
        # Status
        self.is_running = False
        self.monitoring_task = None
        self.hunt_executor_task = None
        
        # Performance tracking
        self.performance_stats = {
            "start_time": datetime.now(),
            "alerts_processed": 0,
            "hunts_completed": 0,
            "actions_executed": 0,
            "threats_detected": 0,
            "false_positives": 0
        }
        
        # Detection patterns
        self.detection_patterns = self._load_detection_patterns()
        
        # Threat intelligence feeds
        self.intel_feeds = self._load_intel_feeds()
        
        # Hunt playbooks
        self.hunt_playbooks = self._load_hunt_playbooks()
    
    def _load_detection_patterns(self) -> Dict[str, Any]:
        """Charge les patterns de détection pré-définis"""
        return {
            "suspicious_network": {
                "name": "Suspicious Network Activity",
                "description": "Détection d'activité réseau suspecte",
                "patterns": [
                    "High volume of DNS requests to recently registered domains",
                    "Connections to known malicious IPs",
                    "Unusual port activity outside business hours",
                    "Data exfiltration patterns"
                ]
            },
            "anomalous_behavior": {
                "name": "Anomalous User Behavior",
                "description": "Comportement utilisateur anormal",
                "patterns": [
                    "Login from unusual locations",
                    "Multiple failed authentication attempts",
                    "Access to sensitive files outside normal patterns",
                    "Privilege escalation attempts"
                ]
            },
            "malware_indicators": {
                "name": "Malware Indicators",
                "description": "Indicateurs de présence de malware",
                "patterns": [
                    "Known malicious file hashes",
                    "Suspicious process behavior",
                    "Registry modifications",
                    "Command and control communications"
                ]
            }
        }
    
    def _load_intel_feeds(self) -> Dict[str, Any]:
        """Charge les sources de threat intelligence"""
        return {
            "public_feeds": [
                "AlienVault OTX",
                "VirusTotal",
                "MISP Feeds",
                "US-CERT Advisories",
                "SANS ISC"
            ],
            "commercial_feeds": [
                "FireEye",
                "CrowdStrike",
                "Recorded Future",
                "ThreatConnect",
                "IBM X-Force"
            ],
            "internal_feeds": [
                "Previous incidents",
                "Red Team IOCs",
                "Honeypot data",
                "Custom research"
            ]
        }
    
    def _load_hunt_playbooks(self) -> Dict[str, Any]:
        """Charge les playbooks de threat hunting"""
        return {
            "lateral_movement": {
                "name": "Lateral Movement Detection",
                "description": "Hunt for lateral movement patterns",
                "hypothesis": "Adversary is using compromised accounts to move laterally",
                "data_sources": [DataSource.LOGS, DataSource.NETWORK, DataSource.ENDPOINT],
                "queries": [
                    "Look for authentication events across multiple hosts",
                    "Analyze process creation on multiple systems",
                    "Check for unusual network connections between internal hosts"
                ],
                "expected_artifacts": ["Login events", "Process executions", "Network connections"]
            },
            "command_control": {
                "name": "Command and Control Hunt",
                "description": "Hunt for C2 communications",
                "hypothesis": "Malware is communicating with external C2 infrastructure",
                "data_sources": [DataSource.NETWORK, DataSource.DNS, DataSource.WEB_PROXY],
                "queries": [
                    "Analyze DNS requests for suspicious domains",
                    "Look for periodic communication patterns",
                    "Check for encrypted traffic to unusual destinations"
                ],
                "expected_artifacts": ["DNS queries", "HTTP requests", "Network flows"]
            },
            "data_exfiltration": {
                "name": "Data Exfiltration Hunt",
                "description": "Hunt for data theft activities",
                "hypothesis": "Sensitive data is being stolen from the environment",
                "data_sources": [DataSource.NETWORK, DataSource.ENDPOINT, DataSource.WEB_PROXY],
                "queries": [
                    "Look for large data transfers to external hosts",
                    "Analyze file access patterns",
                    "Check for compression and encryption activities"
                ],
                "expected_artifacts": ["File access logs", "Network transfers", "Process activity"]
            }
        }
    
    async def start_engine(self):
        """Démarre le moteur Blue Team"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        
        # Démarrer le monitoring des alertes
        self.monitoring_task = asyncio.create_task(self._alert_monitoring_loop())
        
        # Démarrer l'exécuteur de hunts
        self.hunt_executor_task = asyncio.create_task(self._hunt_executor_loop())
        
        # Charger IOCs de base
        await self._load_baseline_iocs()
        
        logger.info("🔵 Moteur Blue Team démarré")
        
        return {
            "status": "started",
            "message": "Moteur Blue Team démarré avec succès",
            "start_time": datetime.now().isoformat(),
            "detection_rules": len(self.detection_rules),
            "iocs_loaded": len(self.iocs),
            "hunt_playbooks": len(self.hunt_playbooks)
        }
    
    async def stop_engine(self):
        """Arrête le moteur"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        
        # Arrêter les tâches
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.hunt_executor_task:
            self.hunt_executor_task.cancel()
        
        logger.info("⏹️ Moteur Blue Team arrêté")
        return {
            "status": "stopped",
            "message": "Moteur arrêté avec succès",
            "stop_time": datetime.now().isoformat()
        }
    
    async def _load_baseline_iocs(self):
        """Charge des IOCs de base pour démarrer"""
        baseline_iocs = [
            {
                "type": "ip",
                "value": "192.168.100.100",
                "description": "Known malicious IP from previous incident",
                "confidence": 0.8,
                "severity": ThreatSeverity.HIGH,
                "source": "internal_investigation"
            },
            {
                "type": "domain",
                "value": "evil-c2.com",
                "description": "Command and control domain",
                "confidence": 0.9,
                "severity": ThreatSeverity.CRITICAL,
                "source": "threat_intelligence"
            },
            {
                "type": "hash",
                "value": "5d41402abc4b2a76b9719d911017c592",
                "description": "Malware sample hash",
                "confidence": 0.7,
                "severity": ThreatSeverity.HIGH,
                "source": "sandbox_analysis"
            }
        ]
        
        for ioc_data in baseline_iocs:
            request = CreateIOCRequest(**ioc_data)
            await self.create_ioc(request)
    
    async def _alert_monitoring_loop(self):
        """Boucle de monitoring des alertes"""
        try:
            while self.is_running:
                # Traiter les nouvelles alertes
                new_alerts = [a for a in self.alerts.values() if a.status == AlertStatus.NEW]
                
                for alert in new_alerts:
                    await self._process_alert(alert)
                
                # Vérifier les alertes anciennes non résolues
                old_alerts = [
                    a for a in self.alerts.values() 
                    if a.status == AlertStatus.INVESTIGATING and 
                    (datetime.now() - a.created_at).total_seconds() > 3600  # 1 heure
                ]
                
                for alert in old_alerts:
                    logger.warning(f"Alerte ancienne non résolue: {alert.title}")
                    alert.escalated = True
                
                await asyncio.sleep(60)  # Vérifier toutes les minutes
                
        except asyncio.CancelledError:
            logger.info("Alert monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans alert monitoring loop: {e}")
    
    async def _hunt_executor_loop(self):
        """Boucle d'exécution des hunts programmés"""
        try:
            while self.is_running:
                # Vérifier les hunts à démarrer
                for hunt in self.threat_hunts.values():
                    if (hunt.status == HuntStatus.PLANNED and 
                        hunt.planned_start and 
                        hunt.planned_start <= datetime.now()):
                        await self._execute_hunt(hunt)
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
        except asyncio.CancelledError:
            logger.info("Hunt executor loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans hunt executor loop: {e}")
    
    async def _process_alert(self, alert: Alert):
        """Traite une alerte automatiquement"""
        try:
            logger.info(f"Traitement alerte: {alert.title}")
            
            alert.status = AlertStatus.INVESTIGATING
            
            # Enrichissement avec IOCs
            await self._enrich_alert_with_iocs(alert)
            
            # Classification automatique
            await self._classify_alert(alert)
            
            # Actions automatiques selon la sévérité
            if alert.severity == ThreatSeverity.CRITICAL:
                await self._execute_automatic_response(alert)
            
            self.performance_stats["alerts_processed"] += 1
            
        except Exception as e:
            logger.error(f"Erreur traitement alerte {alert.id}: {e}")
    
    async def _enrich_alert_with_iocs(self, alert: Alert):
        """Enrichit une alerte avec des IOCs"""
        matching_iocs = []
        
        # Vérifier si l'IP source correspond à des IOCs
        if alert.source_ip:
            for ioc in self.iocs.values():
                if ioc.type == "ip" and ioc.value == alert.source_ip:
                    matching_iocs.append(ioc.id)
        
        # Vérifier autres artifacts
        for artifact_key, artifact_value in alert.artifacts.items():
            for ioc in self.iocs.values():
                if ioc.value in str(artifact_value):
                    matching_iocs.append(ioc.id)
        
        alert.iocs = list(set(matching_iocs))
        
        if matching_iocs:
            logger.info(f"Alerte {alert.id} enrichie avec {len(matching_iocs)} IOCs")
    
    async def _classify_alert(self, alert: Alert):
        """Classifie automatiquement une alerte"""
        # Logique de classification simple
        if len(alert.iocs) > 0:
            alert.confidence = min(alert.confidence + 0.3, 1.0)
            alert.true_positive = True
            self.performance_stats["threats_detected"] += 1
        
        # Classification par patterns
        for pattern_name, pattern_data in self.detection_patterns.items():
            if any(pattern.lower() in alert.description.lower() 
                   for pattern in pattern_data["patterns"]):
                alert.tags.append(pattern_name)
    
    async def _execute_automatic_response(self, alert: Alert):
        """Exécute une réponse automatique pour une alerte critique"""
        try:
            # Actions automatiques pour alertes critiques
            if alert.source_ip:
                # Bloquer l'IP source
                action_request = ExecuteDefensiveActionRequest(
                    name=f"Auto-block IP {alert.source_ip}",
                    description="Blocage automatique IP suspecte",
                    action_type=ResponseAction.BLOCK,
                    target_type="ip",
                    target_identifier=alert.source_ip,
                    executed_by="blue_team_engine",
                    alert_id=alert.id
                )
                
                await self.execute_defensive_action(action_request)
            
            if alert.host:
                # Isoler l'host affecté
                action_request = ExecuteDefensiveActionRequest(
                    name=f"Auto-isolate host {alert.host}",
                    description="Isolation automatique host compromis",
                    action_type=ResponseAction.ISOLATE,
                    target_type="host",
                    target_identifier=alert.host,
                    executed_by="blue_team_engine",
                    alert_id=alert.id
                )
                
                await self.execute_defensive_action(action_request)
            
            logger.info(f"Réponse automatique exécutée pour alerte {alert.id}")
            
        except Exception as e:
            logger.error(f"Erreur réponse automatique alerte {alert.id}: {e}")
    
    async def _execute_hunt(self, hunt: ThreatHunt):
        """Exécute un threat hunt"""
        try:
            logger.info(f"Exécution hunt: {hunt.name}")
            
            hunt.status = HuntStatus.ACTIVE
            hunt.actual_start = datetime.now()
            
            # Simuler l'exécution du hunt
            await asyncio.sleep(2)  # Simulation
            
            # Générer des résultats simulés
            findings = await self._generate_hunt_findings(hunt)
            hunt.findings.extend(findings)
            
            # Analyser les résultats
            if findings:
                hunt.true_positives = len([f for f in findings if f.get("is_threat", False)])
                hunt.false_positives = len(findings) - hunt.true_positives
                
                # Générer des IOCs si menaces trouvées
                if hunt.true_positives > 0:
                    new_iocs = await self._generate_iocs_from_hunt(hunt, findings)
                    hunt.new_iocs.extend([ioc.id for ioc in new_iocs])
            
            hunt.status = HuntStatus.COMPLETED
            hunt.actual_end = datetime.now()
            
            # Générer recommandations
            hunt.recommendations = await self._generate_hunt_recommendations(hunt)
            
            self.performance_stats["hunts_completed"] += 1
            logger.info(f"Hunt {hunt.name} terminé - {hunt.true_positives} menaces trouvées")
            
        except Exception as e:
            hunt.status = HuntStatus.CANCELLED
            logger.error(f"Erreur exécution hunt {hunt.name}: {e}")
    
    async def _generate_hunt_findings(self, hunt: ThreatHunt) -> List[Dict[str, Any]]:
        """Génère des résultats simulés pour un hunt"""
        findings = []
        
        # Simuler des findings selon la technique
        if hunt.hunt_technique == HuntTechnique.IOC_HUNTING:
            findings = [
                {
                    "type": "suspicious_ip",
                    "value": "203.0.113.42",
                    "confidence": 0.7,
                    "is_threat": True,
                    "description": "IP communicating with known C2 infrastructure"
                },
                {
                    "type": "suspicious_domain",
                    "value": "update-check.info",
                    "confidence": 0.6,
                    "is_threat": False,
                    "description": "Domain with suspicious patterns but legitimate"
                }
            ]
        elif hunt.hunt_technique == HuntTechnique.BEHAVIOR_ANALYSIS:
            findings = [
                {
                    "type": "anomalous_login",
                    "value": "user123@company.com",
                    "confidence": 0.8,
                    "is_threat": True,
                    "description": "Login from unusual location outside business hours"
                }
            ]
        elif hunt.hunt_technique == HuntTechnique.ANOMALY_DETECTION:
            findings = [
                {
                    "type": "network_anomaly",
                    "value": "192.168.1.100",
                    "confidence": 0.9,
                    "is_threat": True,
                    "description": "Unusual network traffic volume and patterns"
                }
            ]
        
        return findings
    
    async def _generate_iocs_from_hunt(self, hunt: ThreatHunt, findings: List[Dict[str, Any]]) -> List[IOC]:
        """Génère des IOCs à partir des résultats de hunt"""
        new_iocs = []
        
        for finding in findings:
            if finding.get("is_threat", False):
                ioc_request = CreateIOCRequest(
                    type=finding["type"].replace("suspicious_", "").replace("anomalous_", ""),
                    value=finding["value"],
                    description=f"Découvert lors du hunt: {hunt.name} - {finding['description']}",
                    confidence=finding.get("confidence", 0.5),
                    severity=ThreatSeverity.MEDIUM,
                    source=f"threat_hunt_{hunt.id}"
                )
                
                ioc = await self.create_ioc(ioc_request)
                new_iocs.append(ioc)
        
        return new_iocs
    
    async def _generate_hunt_recommendations(self, hunt: ThreatHunt) -> List[str]:
        """Génère des recommandations post-hunt"""
        recommendations = []
        
        if hunt.true_positives > 0:
            recommendations.extend([
                "Créer des règles de détection pour les patterns identifiés",
                "Mettre à jour la threat intelligence avec les nouveaux IOCs",
                "Renforcer le monitoring des assets affectés"
            ])
        
        if hunt.false_positives > hunt.true_positives:
            recommendations.extend([
                "Affiner les critères de recherche pour réduire les faux positifs",
                "Revoir la baseline pour améliorer la précision"
            ])
        
        recommendations.append(f"Planifier un hunt de suivi dans {30} jours")
        
        return recommendations
    
    # API publique du moteur
    
    async def create_ioc(self, request: CreateIOCRequest) -> IOC:
        """Crée un nouvel IOC"""
        ioc = IOC(
            type=request.type,
            value=request.value,
            description=request.description,
            confidence=request.confidence,
            severity=request.severity,
            source=request.source,
            tags=request.tags
        )
        
        self.iocs[ioc.id] = ioc
        logger.info(f"Nouvel IOC créé: {ioc.type} = {ioc.value}")
        
        return ioc
    
    async def create_detection_rule(self, request: CreateDetectionRuleRequest) -> DetectionRule:
        """Crée une nouvelle règle de détection"""
        rule = DetectionRule(
            name=request.name,
            description=request.description,
            rule_type=request.rule_type,
            rule_content=request.rule_content,
            data_sources=request.data_sources,
            mitre_techniques=request.mitre_techniques,
            severity=request.severity,
            created_by=request.created_by,
            tags=request.tags
        )
        
        self.detection_rules[rule.id] = rule
        logger.info(f"Nouvelle règle de détection créée: {rule.name}")
        
        return rule
    
    async def create_alert(self, request: CreateAlertRequest) -> Alert:
        """Crée une nouvelle alerte"""
        alert = Alert(
            title=request.title,
            description=request.description,
            severity=request.severity,
            source_system=request.source_system,
            data_source=request.data_source,
            affected_assets=request.affected_assets,
            source_ip=request.source_ip,
            destination_ip=request.destination_ip,
            user_account=request.user_account,
            host=request.host
        )
        
        self.alerts[alert.id] = alert
        logger.info(f"Nouvelle alerte créée: {alert.title}")
        
        return alert
    
    async def update_alert(self, alert_id: str, request: UpdateAlertRequest) -> Alert:
        """Met à jour une alerte"""
        if alert_id not in self.alerts:
            raise ValueError(f"Alerte {alert_id} non trouvée")
        
        alert = self.alerts[alert_id]
        
        if request.status:
            alert.status = request.status
        if request.assigned_to is not None:
            alert.assigned_to = request.assigned_to
        if request.investigation_notes is not None:
            alert.investigation_notes = request.investigation_notes
        if request.actions_taken is not None:
            alert.actions_taken = request.actions_taken
        if request.false_positive is not None:
            alert.false_positive = request.false_positive
            if request.false_positive:
                self.performance_stats["false_positives"] += 1
        if request.true_positive is not None:
            alert.true_positive = request.true_positive
        if request.mitre_techniques is not None:
            alert.mitre_techniques = request.mitre_techniques
        
        alert.updated_at = datetime.now()
        
        return alert
    
    async def create_threat_hunt(self, request: CreateThreatHuntRequest) -> ThreatHunt:
        """Crée un nouveau threat hunt"""
        hunt = ThreatHunt(
            name=request.name,
            description=request.description,
            hypothesis=request.hypothesis,
            hunt_technique=request.hunt_technique,
            data_sources=request.data_sources,
            query=request.query,
            hunter=request.hunter,
            planned_start=request.planned_start,
            planned_end=request.planned_end
        )
        
        self.threat_hunts[hunt.id] = hunt
        logger.info(f"Nouveau threat hunt créé: {hunt.name}")
        
        return hunt
    
    async def update_threat_hunt(self, hunt_id: str, request: UpdateThreatHuntRequest) -> ThreatHunt:
        """Met à jour un threat hunt"""
        if hunt_id not in self.threat_hunts:
            raise ValueError(f"Hunt {hunt_id} non trouvé")
        
        hunt = self.threat_hunts[hunt_id]
        
        if request.status:
            hunt.status = request.status
        if request.findings is not None:
            hunt.findings = request.findings
        if request.recommendations is not None:
            hunt.recommendations = request.recommendations
        if request.lessons_learned is not None:
            hunt.lessons_learned = request.lessons_learned
        
        hunt.updated_at = datetime.now()
        
        return hunt
    
    async def execute_defensive_action(self, request: ExecuteDefensiveActionRequest) -> DefensiveAction:
        """Exécute une action défensive"""
        action = DefensiveAction(
            name=request.name,
            description=request.description,
            action_type=request.action_type,
            target_type=request.target_type,
            target_identifier=request.target_identifier,
            executed_by=request.executed_by,
            command=request.command,
            parameters=request.parameters,
            alert_id=request.alert_id
        )
        
        # Simuler l'exécution
        await asyncio.sleep(1)
        
        # Résultats simulés selon le type d'action
        if request.action_type == ResponseAction.BLOCK:
            action.result = f"IP {request.target_identifier} blocked successfully"
            action.status = "success"
        elif request.action_type == ResponseAction.ISOLATE:
            action.result = f"Host {request.target_identifier} isolated successfully"
            action.status = "success"
        elif request.action_type == ResponseAction.QUARANTINE:
            action.result = f"File {request.target_identifier} quarantined successfully"
            action.status = "success"
        else:
            action.result = f"Action {request.action_type} executed successfully"
            action.status = "success"
        
        self.defensive_actions[action.id] = action
        self.performance_stats["actions_executed"] += 1
        
        logger.info(f"Action défensive exécutée: {action.name}")
        
        return action
    
    async def search_iocs(self, request: IOCSearchRequest) -> Tuple[List[IOC], int]:
        """Recherche des IOCs"""
        results = []
        
        for ioc in self.iocs.values():
            # Filtres de recherche
            if request.query and request.query.lower() not in ioc.value.lower() and request.query.lower() not in ioc.description.lower():
                continue
            
            if request.ioc_type and ioc.type != request.ioc_type:
                continue
            
            if request.severity and ioc.severity not in request.severity:
                continue
            
            if request.is_active is not None and ioc.is_active != request.is_active:
                continue
            
            if request.date_from and ioc.first_seen.date() < request.date_from:
                continue
            
            if request.date_to and ioc.first_seen.date() > request.date_to:
                continue
            
            results.append(ioc)
        
        # Trier par date de création
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    async def search_alerts(self, request: AlertSearchRequest) -> Tuple[List[Alert], int]:
        """Recherche des alertes"""
        results = []
        
        for alert in self.alerts.values():
            # Filtres de recherche
            if request.query and request.query.lower() not in alert.title.lower() and request.query.lower() not in alert.description.lower():
                continue
            
            if request.status and alert.status not in request.status:
                continue
            
            if request.severity and alert.severity not in request.severity:
                continue
            
            if request.assigned_to and alert.assigned_to != request.assigned_to:
                continue
            
            if request.data_source and alert.data_source != request.data_source:
                continue
            
            if request.date_from and alert.created_at.date() < request.date_from:
                continue
            
            if request.date_to and alert.created_at.date() > request.date_to:
                continue
            
            results.append(alert)
        
        # Trier par date de création
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    async def search_hunts(self, request: HuntSearchRequest) -> Tuple[List[ThreatHunt], int]:
        """Recherche des hunts"""
        results = []
        
        for hunt in self.threat_hunts.values():
            # Filtres de recherche
            if request.query and request.query.lower() not in hunt.name.lower() and request.query.lower() not in hunt.description.lower():
                continue
            
            if request.status and hunt.status not in request.status:
                continue
            
            if request.hunter and hunt.hunter != request.hunter:
                continue
            
            if request.hunt_technique and hunt.hunt_technique != request.hunt_technique:
                continue
            
            if request.date_from and hunt.created_at.date() < request.date_from:
                continue
            
            if request.date_to and hunt.created_at.date() > request.date_to:
                continue
            
            results.append(hunt)
        
        # Trier par date de création
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    def get_alert_statistics(self) -> AlertStatistics:
        """Statistiques des alertes"""
        total_alerts = len(self.alerts)
        
        by_status = {}
        by_severity = {}
        by_data_source = {}
        true_positives = 0
        false_positives = 0
        total_response_time = 0
        total_resolution_time = 0
        response_count = 0
        resolution_count = 0
        escalated_alerts = 0
        alerts_last_24h = 0
        
        now = datetime.now()
        
        for alert in self.alerts.values():
            by_status[alert.status.value] = by_status.get(alert.status.value, 0) + 1
            by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
            by_data_source[alert.data_source.value] = by_data_source.get(alert.data_source.value, 0) + 1
            
            if alert.true_positive:
                true_positives += 1
            if alert.false_positive:
                false_positives += 1
            
            if alert.response_time:
                total_response_time += alert.response_time
                response_count += 1
            
            if alert.resolution_time:
                total_resolution_time += alert.resolution_time
                resolution_count += 1
            
            if alert.escalated:
                escalated_alerts += 1
            
            if (now - alert.created_at).total_seconds() < 86400:  # 24h
                alerts_last_24h += 1
        
        return AlertStatistics(
            total_alerts=total_alerts,
            by_status=by_status,
            by_severity=by_severity,
            by_data_source=by_data_source,
            true_positive_rate=(true_positives / max(total_alerts, 1)) * 100,
            false_positive_rate=(false_positives / max(total_alerts, 1)) * 100,
            avg_response_time=total_response_time / max(response_count, 1),
            avg_resolution_time=total_resolution_time / max(resolution_count, 1),
            escalated_alerts=escalated_alerts,
            alerts_last_24h=alerts_last_24h
        )
    
    def get_hunt_statistics(self) -> HuntStatistics:
        """Statistiques des hunts"""
        total_hunts = len(self.threat_hunts)
        
        by_status = {}
        by_technique = {}
        by_hunter = {}
        successful_hunts = 0
        total_duration = 0
        hunt_count = 0
        new_iocs_discovered = 0
        new_rules_created = 0
        threats_identified = 0
        
        for hunt in self.threat_hunts.values():
            by_status[hunt.status.value] = by_status.get(hunt.status.value, 0) + 1
            by_technique[hunt.hunt_technique.value] = by_technique.get(hunt.hunt_technique.value, 0) + 1
            by_hunter[hunt.hunter] = by_hunter.get(hunt.hunter, 0) + 1
            
            if hunt.true_positives > 0:
                successful_hunts += 1
                threats_identified += hunt.true_positives
            
            if hunt.actual_start and hunt.actual_end:
                duration_hours = (hunt.actual_end - hunt.actual_start).total_seconds() / 3600
                total_duration += duration_hours
                hunt_count += 1
            
            new_iocs_discovered += len(hunt.new_iocs)
            new_rules_created += len(hunt.new_rules)
        
        return HuntStatistics(
            total_hunts=total_hunts,
            by_status=by_status,
            by_technique=by_technique,
            by_hunter=by_hunter,
            success_rate=(successful_hunts / max(total_hunts, 1)) * 100,
            avg_duration_hours=total_duration / max(hunt_count, 1),
            new_iocs_discovered=new_iocs_discovered,
            new_rules_created=new_rules_created,
            threats_identified=threats_identified
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Statut du moteur Blue Team"""
        now = datetime.now()
        uptime = (now - self.performance_stats["start_time"]).total_seconds()
        
        active_alerts = len([a for a in self.alerts.values() if a.status in [AlertStatus.NEW, AlertStatus.INVESTIGATING]])
        active_hunts = len([h for h in self.threat_hunts.values() if h.status == HuntStatus.ACTIVE])
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "performance": self.performance_stats,
            "active_alerts": active_alerts,
            "total_alerts": len(self.alerts),
            "active_hunts": active_hunts,
            "total_hunts": len(self.threat_hunts),
            "iocs_monitored": len([i for i in self.iocs.values() if i.is_active]),
            "detection_rules": len(self.detection_rules),
            "defensive_actions": len(self.defensive_actions)
        }