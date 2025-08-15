"""
Security Orchestration Module - Orchestration Engine
Moteur d'orchestration pour l'automatisation des réponses sécuritaires (SOAR)
"""
import uuid
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .models import (
    SOARPlaybook, PlaybookExecution, ActionExecution, TriggerCondition, 
    PlaybookAction, ActionType, PlaybookStatus, SOARMetrics, IntegrationConfig,
    IncidentContext, SOARAlert
)

class SOAROrchestrationEngine:
    """Moteur principal d'orchestration SOAR"""
    
    def __init__(self):
        self.playbooks = self._load_default_playbooks()
        self.executions = {}
        self.integrations = self._setup_integrations()
        self.metrics = self._initialize_metrics()
        
    def _load_default_playbooks(self) -> List[SOARPlaybook]:
        """Charge les playbooks par défaut"""
        return [
            SOARPlaybook(
                playbook_id="pb_incident_response",
                name="Réponse Incident Standard",
                description="Playbook standard pour la gestion d'incidents de sécurité",
                category="incident_response",
                version="1.0",
                created_by="system",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status=PlaybookStatus.ACTIVE,
                triggers=[
                    TriggerCondition(
                        condition_id="trigger_high_severity",
                        name="Incident haute sévérité",
                        description="Déclenché automatiquement pour les incidents critiques",
                        condition_type="event",
                        parameters={"severity": "high", "auto_trigger": True}
                    )
                ],
                actions=[
                    PlaybookAction(
                        action_id="action_notify_team",
                        name="Notification équipe sécurité",
                        action_type=ActionType.EMAIL_NOTIFICATION,
                        description="Notifie l'équipe de sécurité",
                        parameters={
                            "recipients": ["security-team@company.com"],
                            "template": "incident_alert",
                            "urgent": True
                        }
                    ),
                    PlaybookAction(
                        action_id="action_create_ticket",
                        name="Création ticket incident",
                        action_type=ActionType.TICKET_CREATION,
                        description="Crée un ticket dans le système de gestion",
                        parameters={
                            "system": "jira",
                            "project": "SEC",
                            "priority": "high"
                        },
                        depends_on=["action_notify_team"]
                    ),
                    PlaybookAction(
                        action_id="action_isolate_asset",
                        name="Isolation actif compromis",
                        action_type=ActionType.CONTAINMENT,
                        description="Isole l'actif compromis du réseau",
                        parameters={
                            "isolation_type": "network",
                            "approval_required": True
                        },
                        depends_on=["action_create_ticket"]
                    )
                ],
                tags=["incident", "security", "automated"],
                auto_execute=True
            ),
            SOARPlaybook(
                playbook_id="pb_phishing_response",
                name="Réponse Anti-Phishing",
                description="Playbook pour traiter les incidents de phishing",
                category="incident_response",
                version="1.0",
                created_by="system",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status=PlaybookStatus.ACTIVE,
                triggers=[
                    TriggerCondition(
                        condition_id="trigger_phishing_detected",
                        name="Phishing détecté",
                        description="Déclenché lors de la détection de phishing",
                        condition_type="event",
                        parameters={"event_type": "phishing", "confidence": "high"}
                    )
                ],
                actions=[
                    PlaybookAction(
                        action_id="action_block_domain",
                        name="Blocage domaine malveillant",
                        action_type=ActionType.IP_BLOCKING,
                        description="Bloque le domaine malveillant",
                        parameters={"block_type": "domain", "duration": "24h"}
                    ),
                    PlaybookAction(
                        action_id="action_notify_users",
                        name="Alerte utilisateurs",
                        action_type=ActionType.EMAIL_NOTIFICATION,
                        description="Alerte les utilisateurs du phishing",
                        parameters={
                            "template": "phishing_alert",
                            "scope": "all_users"
                        }
                    ),
                    PlaybookAction(
                        action_id="action_threat_hunt",
                        name="Chasse aux menaces",
                        action_type=ActionType.THREAT_HUNTING,
                        description="Lance une chasse aux menaces liées",
                        parameters={
                            "scope": "related_indicators",
                            "lookback_hours": 72
                        },
                        depends_on=["action_block_domain"]
                    )
                ],
                tags=["phishing", "email", "threat_hunting"],
                auto_execute=True
            ),
            SOARPlaybook(
                playbook_id="pb_vulnerability_remediation",
                name="Remédiation Vulnérabilités",
                description="Playbook pour la remédiation automatisée des vulnérabilités",
                category="vulnerability_management",
                version="1.0",
                created_by="system",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status=PlaybookStatus.ACTIVE,
                triggers=[
                    TriggerCondition(
                        condition_id="trigger_critical_vuln",
                        name="Vulnérabilité critique",
                        description="Déclenché pour les vulnérabilités critiques",
                        condition_type="event",
                        parameters={"cvss_score": ">= 9.0", "exploitability": "high"}
                    )
                ],
                actions=[
                    PlaybookAction(
                        action_id="action_scan_affected_systems",
                        name="Scan systèmes affectés",
                        action_type=ActionType.SCAN_INITIATION,
                        description="Lance un scan des systèmes potentiellement affectés",
                        parameters={"scan_type": "vulnerability", "priority": "high"}
                    ),
                    PlaybookAction(
                        action_id="action_notify_admins",
                        name="Notification administrateurs",
                        action_type=ActionType.EMAIL_NOTIFICATION,
                        description="Notifie les administrateurs systèmes",
                        parameters={
                            "recipients": ["sysadmin@company.com"],
                            "template": "vulnerability_alert"
                        }
                    ),
                    PlaybookAction(
                        action_id="action_create_remediation_ticket",
                        name="Ticket remédiation",
                        action_type=ActionType.TICKET_CREATION,
                        description="Crée un ticket de remédiation",
                        parameters={
                            "priority": "critical",
                            "sla": "24h",
                            "auto_assign": True
                        },
                        depends_on=["action_scan_affected_systems"]
                    )
                ],
                tags=["vulnerability", "remediation", "scanning"],
                approval_required=False,
                auto_execute=True
            )
        ]
    
    def _setup_integrations(self) -> List[IntegrationConfig]:
        """Configure les intégrations par défaut"""
        return [
            IntegrationConfig(
                integration_id="int_email",
                name="Email Service",
                integration_type="email",
                config={
                    "smtp_server": "smtp.company.com",
                    "port": 587,
                    "use_tls": True,
                    "sender": "soar@company.com"
                },
                status="active"
            ),
            IntegrationConfig(
                integration_id="int_jira",
                name="Jira Ticketing",
                integration_type="ticketing",
                config={
                    "base_url": "https://company.atlassian.net",
                    "project_key": "SEC",
                    "issue_type": "Security Incident"
                },
                status="active"
            ),
            IntegrationConfig(
                integration_id="int_firewall",
                name="Firewall Management",
                integration_type="firewall",
                config={
                    "api_endpoint": "https://firewall.company.com/api",
                    "default_action": "block",
                    "backup_method": "manual"
                },
                status="active"
            ),
            IntegrationConfig(
                integration_id="int_siem",
                name="SIEM Integration",
                integration_type="siem",
                config={
                    "siem_type": "splunk",
                    "api_endpoint": "https://splunk.company.com:8089",
                    "search_app": "security"
                },
                status="active"
            )
        ]
    
    def _initialize_metrics(self) -> SOARMetrics:
        """Initialise les métriques SOAR"""
        return SOARMetrics(
            total_playbooks=len(self.playbooks),
            active_playbooks=len([pb for pb in self.playbooks if pb.status == PlaybookStatus.ACTIVE]),
            total_executions=0,
            successful_executions=0,
            failed_executions=0,
            average_execution_time=0.0,
            executions_last_24h=0,
            top_triggered_playbooks=[],
            integration_status={
                integration.integration_id: integration.status 
                for integration in self.integrations
            }
        )
    
    async def execute_playbook(self, playbook_id: str, context: Dict[str, Any] = None, 
                             triggered_by: str = "manual") -> PlaybookExecution:
        """Exécute un playbook SOAR"""
        
        # Trouve le playbook
        playbook = next((pb for pb in self.playbooks if pb.playbook_id == playbook_id), None)
        if not playbook:
            raise ValueError(f"Playbook {playbook_id} non trouvé")
        
        execution_id = str(uuid.uuid4())
        context = context or {}
        
        execution = PlaybookExecution(
            execution_id=execution_id,
            playbook_id=playbook_id,
            playbook_name=playbook.name,
            triggered_by=triggered_by,
            trigger_condition="manual" if triggered_by == "manual" else "automated",
            status=PlaybookStatus.RUNNING,
            started_at=datetime.now().isoformat(),
            context=context
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Exécute les actions du playbook
            results = await self._execute_playbook_actions(playbook, execution, context)
            
            execution.status = PlaybookStatus.COMPLETED
            execution.completed_at = datetime.now().isoformat()
            execution.results = results
            
            self.metrics.successful_executions += 1
            
        except Exception as e:
            execution.status = PlaybookStatus.FAILED
            execution.completed_at = datetime.now().isoformat()
            execution.results = {"error": str(e)}
            
            self.metrics.failed_executions += 1
        
        self.metrics.total_executions += 1
        self._update_metrics()
        
        return execution
    
    async def _execute_playbook_actions(self, playbook: SOARPlaybook, 
                                      execution: PlaybookExecution, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute les actions d'un playbook dans l'ordre des dépendances"""
        
        results = {}
        action_results = {}
        
        # Crée une copie des actions à exécuter
        remaining_actions = playbook.actions.copy()
        executed_actions = set()
        
        while remaining_actions:
            # Trouve les actions qui peuvent être exécutées (sans dépendances non satisfaites)
            executable_actions = [
                action for action in remaining_actions
                if not action.depends_on or all(dep in executed_actions for dep in action.depends_on)
            ]
            
            if not executable_actions:
                # Détection de dépendances circulaires ou manquantes
                remaining_action_ids = [action.action_id for action in remaining_actions]
                raise Exception(f"Dépendances circulaires ou manquantes pour les actions: {remaining_action_ids}")
            
            # Exécute les actions en parallèle si possible
            tasks = []
            for action in executable_actions:
                task = self._execute_action(action, context, action_results)
                tasks.append((action, task))
            
            # Attend les résultats
            for action, task in tasks:
                try:
                    result = await task
                    action_results[action.action_id] = result
                    results[action.action_id] = {
                        "action_name": action.name,
                        "status": "completed",
                        "result": result
                    }
                    executed_actions.add(action.action_id)
                    remaining_actions.remove(action)
                    
                except Exception as e:
                    results[action.action_id] = {
                        "action_name": action.name,
                        "status": "failed",
                        "error": str(e)
                    }
                    
                    if not action.continue_on_failure:
                        raise Exception(f"Action {action.name} a échoué et arrête l'exécution: {str(e)}")
                    
                    executed_actions.add(action.action_id)
                    remaining_actions.remove(action)
        
        return results
    
    async def _execute_action(self, action: PlaybookAction, context: Dict[str, Any], 
                            previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action spécifique"""
        
        # Simulation d'exécution d'action avec délai réaliste
        await asyncio.sleep(0.5)  # Simule le temps d'exécution
        
        if action.action_type == ActionType.EMAIL_NOTIFICATION:
            return await self._execute_email_notification(action, context)
        
        elif action.action_type == ActionType.TICKET_CREATION:
            return await self._execute_ticket_creation(action, context)
        
        elif action.action_type == ActionType.IP_BLOCKING:
            return await self._execute_ip_blocking(action, context)
        
        elif action.action_type == ActionType.CONTAINMENT:
            return await self._execute_containment(action, context)
        
        elif action.action_type == ActionType.SCAN_INITIATION:
            return await self._execute_scan_initiation(action, context)
        
        elif action.action_type == ActionType.THREAT_HUNTING:
            return await self._execute_threat_hunting(action, context)
        
        else:
            return {"status": "not_implemented", "message": f"Action type {action.action_type} not implemented"}
    
    async def _execute_email_notification(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule l'envoi d'email"""
        recipients = action.parameters.get("recipients", [])
        template = action.parameters.get("template", "default")
        
        return {
            "status": "sent",
            "recipients": recipients,
            "template": template,
            "message_id": str(uuid.uuid4()),
            "sent_at": datetime.now().isoformat()
        }
    
    async def _execute_ticket_creation(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule la création de ticket"""
        return {
            "status": "created",
            "ticket_id": f"SEC-{random.randint(1000, 9999)}",
            "system": action.parameters.get("system", "jira"),
            "priority": action.parameters.get("priority", "medium"),
            "created_at": datetime.now().isoformat()
        }
    
    async def _execute_ip_blocking(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule le blocage d'IP/domaine"""
        import random
        
        return {
            "status": "blocked",
            "block_type": action.parameters.get("block_type", "ip"),
            "target": context.get("target_ip", "192.168.1.100"),
            "duration": action.parameters.get("duration", "24h"),
            "rule_id": f"BLOCK_{random.randint(10000, 99999)}",
            "applied_at": datetime.now().isoformat()
        }
    
    async def _execute_containment(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule la containment d'un actif"""
        return {
            "status": "contained",
            "isolation_type": action.parameters.get("isolation_type", "network"),
            "asset": context.get("affected_asset", "workstation-001"),
            "method": "firewall_rule",
            "contained_at": datetime.now().isoformat()
        }
    
    async def _execute_scan_initiation(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule le lancement d'un scan"""
        return {
            "status": "initiated",
            "scan_type": action.parameters.get("scan_type", "vulnerability"),
            "scan_id": str(uuid.uuid4()),
            "targets": context.get("scan_targets", ["192.168.1.0/24"]),
            "estimated_duration": "2 hours",
            "started_at": datetime.now().isoformat()
        }
    
    async def _execute_threat_hunting(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simule une chasse aux menaces"""
        return {
            "status": "completed",
            "hunt_type": "indicator_based",
            "scope": action.parameters.get("scope", "network"),
            "indicators_found": random.randint(0, 5),
            "hunt_id": str(uuid.uuid4()),
            "duration_minutes": random.randint(15, 60),
            "completed_at": datetime.now().isoformat()
        }
    
    def get_playbooks(self) -> List[SOARPlaybook]:
        """Retourne la liste des playbooks"""
        return self.playbooks
    
    def get_execution(self, execution_id: str) -> Optional[PlaybookExecution]:
        """Récupère une exécution par son ID"""
        return self.executions.get(execution_id)
    
    def get_executions(self, limit: int = 50) -> List[PlaybookExecution]:
        """Récupère les dernières exécutions"""
        executions = list(self.executions.values())
        executions.sort(key=lambda x: x.started_at, reverse=True)
        return executions[:limit]
    
    def _update_metrics(self):
        """Met à jour les métriques"""
        # Calcule la durée moyenne d'exécution
        completed_executions = [
            exec for exec in self.executions.values() 
            if exec.status == PlaybookStatus.COMPLETED and exec.completed_at
        ]
        
        if completed_executions:
            total_duration = 0
            for execution in completed_executions:
                start = datetime.fromisoformat(execution.started_at)
                end = datetime.fromisoformat(execution.completed_at)
                total_duration += (end - start).total_seconds()
            
            self.metrics.average_execution_time = total_duration / len(completed_executions)
        
        # Compte les exécutions des dernières 24h
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics.executions_last_24h = len([
            exec for exec in self.executions.values()
            if datetime.fromisoformat(exec.started_at) > cutoff_time
        ])
        
        # Top playbooks déclenchés
        playbook_counts = {}
        for execution in self.executions.values():
            pb_id = execution.playbook_id
            playbook_counts[pb_id] = playbook_counts.get(pb_id, 0) + 1
        
        self.metrics.top_triggered_playbooks = [
            {"playbook_id": pb_id, "executions": count}
            for pb_id, count in sorted(playbook_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def get_metrics(self) -> SOARMetrics:
        """Retourne les métriques actuelles"""
        self._update_metrics()
        return self.metrics

# Instance globale du moteur SOAR
soar_engine = SOAROrchestrationEngine()

# Import manquant pour random
import random