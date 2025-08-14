"""
Automation AI - Automatisation workflows CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Intelligence artificielle pour l'automatisation des processus sécurité
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from fastapi import HTTPException
from pydantic import BaseModel, Field
import logging

# Intégration Emergent LLM
try:
    from emergentintegrations import EmergentLLM
except ImportError:
    print("⚠️ EmergentLLM non disponible pour Automation AI - Mode fallback activé")
    EmergentLLM = None

from backend.config import settings
from backend.database import get_collection

# Modèles de données Automation AI
class WorkflowStep(BaseModel):
    step_id: str = Field(..., description="ID unique de l'étape")
    name: str = Field(..., description="Nom de l'étape")
    action_type: str = Field(..., description="Type d'action: scan, analyze, notify, remediate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Paramètres de l'action")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions d'exécution")
    timeout: int = Field(300, description="Timeout en secondes")
    retry_count: int = Field(3, description="Nombre de tentatives")

class SecurityWorkflow(BaseModel):
    workflow_id: str = Field(..., description="ID unique du workflow")
    name: str = Field(..., description="Nom du workflow")
    description: str = Field(..., description="Description du workflow")
    category: str = Field(..., description="Catégorie: incident_response, vulnerability_management, compliance, monitoring")
    trigger_type: str = Field(..., description="Type de déclencheur: manual, scheduled, event_based, threshold")
    trigger_conditions: Dict[str, Any] = Field(..., description="Conditions de déclenchement")
    steps: List[WorkflowStep] = Field(..., description="Étapes du workflow")
    is_active: bool = Field(True, description="Workflow actif ou non")
    created_by: str = Field("automation_ai", description="Créateur du workflow")

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str = Field(..., description="ID du workflow à exécuter")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Données d'entrée")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte d'exécution")
    async_execution: bool = Field(True, description="Exécution asynchrone")

class WorkflowExecutionStep(BaseModel):
    step_id: str = Field(..., description="ID de l'étape")
    name: str = Field(..., description="Nom de l'étape")
    status: str = Field(..., description="Status: pending, running, completed, failed, skipped")
    start_time: Optional[datetime] = Field(None, description="Heure de début")
    end_time: Optional[datetime] = Field(None, description="Heure de fin")
    output: Optional[Dict[str, Any]] = Field(None, description="Sortie de l'étape")
    error_message: Optional[str] = Field(None, description="Message d'erreur si échec")

class WorkflowExecutionResult(BaseModel):
    execution_id: str = Field(..., description="ID d'exécution")
    workflow_id: str = Field(..., description="ID du workflow")
    status: str = Field(..., description="Status global: running, completed, failed, cancelled")
    start_time: datetime = Field(..., description="Heure de début d'exécution")
    end_time: Optional[datetime] = Field(None, description="Heure de fin d'exécution")
    steps_executed: List[WorkflowExecutionStep] = Field(..., description="Étapes exécutées")
    total_steps: int = Field(..., description="Nombre total d'étapes")
    success_count: int = Field(0, description="Nombre d'étapes réussies")
    failure_count: int = Field(0, description="Nombre d'étapes échouées")
    execution_time: Optional[float] = Field(None, description="Temps d'exécution en secondes")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Données de sortie")

class AutomationRule(BaseModel):
    rule_id: str = Field(..., description="ID unique de la règle")
    name: str = Field(..., description="Nom de la règle")
    description: str = Field(..., description="Description de la règle")
    condition: Dict[str, Any] = Field(..., description="Condition de déclenchement")
    action: Dict[str, Any] = Field(..., description="Action à exécuter")
    priority: int = Field(5, description="Priorité (1-10)")
    is_active: bool = Field(True, description="Règle active")

class AutomationAIService:
    """Service IA d'Automatisation - Workflows et règles automatisées"""
    
    def __init__(self):
        self.llm_client = None
        self.active_workflows = {}  # Workflows en cours d'exécution
        self.automation_rules = {}  # Règles d'automatisation actives
        self.workflow_templates = self._initialize_workflow_templates()
        self.action_handlers = self._initialize_action_handlers()
        self._initialize_llm()
        self._load_default_rules()
    
    def _initialize_llm(self):
        """Initialise le client LLM pour Automation AI"""
        try:
            if EmergentLLM and settings.emergent_llm_key:
                self.llm_client = EmergentLLM(
                    api_key=settings.emergent_llm_key,
                    default_provider=settings.default_llm_provider,
                    default_model=settings.default_llm_model
                )
                print("✅ Automation AI initialisé avec Emergent LLM")
            else:
                print("⚠️ Automation AI - Mode simulation activé")
        except Exception as e:
            print(f"❌ Erreur initialisation Automation AI LLM: {e}")
    
    def _initialize_workflow_templates(self) -> Dict[str, SecurityWorkflow]:
        """Initialise les templates de workflows prédéfinis"""
        templates = {}
        
        # Template 1: Incident Response Automatisé
        incident_response_steps = [
            WorkflowStep(
                step_id="detect_incident",
                name="Détection d'incident",
                action_type="analyze",
                parameters={"analysis_type": "behavioral", "threshold": 0.7}
            ),
            WorkflowStep(
                step_id="classify_incident",
                name="Classification d'incident",
                action_type="analyze",
                parameters={"classification_model": "incident_severity"}
            ),
            WorkflowStep(
                step_id="notify_team",
                name="Notification équipe",
                action_type="notify",
                parameters={"channels": ["email", "slack", "sms"], "urgency": "high"}
            ),
            WorkflowStep(
                step_id="isolate_systems",
                name="Isolation systèmes",
                action_type="remediate",
                parameters={"isolation_type": "network", "scope": "affected_only"},
                conditions={"incident_severity": {"$gte": 7}}
            ),
            WorkflowStep(
                step_id="collect_evidence",
                name="Collecte preuves",
                action_type="scan",
                parameters={"evidence_types": ["logs", "network_traffic", "file_hashes"]}
            ),
            WorkflowStep(
                step_id="generate_report",
                name="Génération rapport",
                action_type="analyze",
                parameters={"report_type": "incident_summary", "format": "pdf"}
            )
        ]
        
        templates["incident_response_auto"] = SecurityWorkflow(
            workflow_id="incident_response_auto",
            name="Réponse aux Incidents Automatisée",
            description="Workflow automatisé pour la détection et réponse aux incidents de sécurité",
            category="incident_response",
            trigger_type="event_based",
            trigger_conditions={"alert_severity": {"$gte": "medium"}, "source": "monitoring"},
            steps=incident_response_steps
        )
        
        # Template 2: Scan de Vulnérabilités Automatisé
        vuln_scan_steps = [
            WorkflowStep(
                step_id="port_scan",
                name="Scan de ports",
                action_type="scan",
                parameters={"scan_type": "nmap", "ports": "1-65535", "technique": "stealth"}
            ),
            WorkflowStep(
                step_id="service_enumeration",
                name="Énumération services",
                action_type="scan",
                parameters={"enumeration_depth": "detailed"}
            ),
            WorkflowStep(
                step_id="vulnerability_scan",
                name="Scan vulnérabilités",
                action_type="scan",
                parameters={"scanner": "openvas", "profile": "full_and_fast"}
            ),
            WorkflowStep(
                step_id="analyze_results",
                name="Analyse résultats",
                action_type="analyze",
                parameters={"analysis_type": "risk_assessment", "cvss_threshold": 4.0}
            ),
            WorkflowStep(
                step_id="prioritize_vulnerabilities",
                name="Priorisation vulnérabilités",
                action_type="analyze",
                parameters={"prioritization_model": "business_impact"}
            ),
            WorkflowStep(
                step_id="create_tickets",
                name="Création tickets",
                action_type="notify",
                parameters={"ticket_system": "jira", "assign_automatically": True},
                conditions={"vulnerability_count": {"$gt": 0}}
            )
        ]
        
        templates["vulnerability_scan_auto"] = SecurityWorkflow(
            workflow_id="vulnerability_scan_auto",
            name="Scan Vulnérabilités Automatisé",
            description="Workflow automatisé pour le scan et gestion des vulnérabilités",
            category="vulnerability_management",
            trigger_type="scheduled",
            trigger_conditions={"schedule": "weekly", "day": "sunday", "time": "02:00"},
            steps=vuln_scan_steps
        )
        
        # Template 3: Compliance Check Automatisé
        compliance_steps = [
            WorkflowStep(
                step_id="collect_config",
                name="Collecte configuration",
                action_type="scan",
                parameters={"config_types": ["firewall", "antivirus", "patch_status"]}
            ),
            WorkflowStep(
                step_id="compliance_check",
                name="Vérification conformité",
                action_type="analyze",
                parameters={"standards": ["iso27001", "nist", "gdpr"], "strict_mode": True}
            ),
            WorkflowStep(
                step_id="gap_analysis",
                name="Analyse des écarts",
                action_type="analyze",
                parameters={"analysis_depth": "detailed", "recommendations": True}
            ),
            WorkflowStep(
                step_id="remediation_plan",
                name="Plan de remédiation",
                action_type="analyze",
                parameters={"plan_type": "automated", "priority_based": True}
            ),
            WorkflowStep(
                step_id="compliance_report",
                name="Rapport de conformité",
                action_type="notify",
                parameters={"report_format": "executive_summary", "distribution": "stakeholders"}
            )
        ]
        
        templates["compliance_check_auto"] = SecurityWorkflow(
            workflow_id="compliance_check_auto",
            name="Vérification Conformité Automatisée",
            description="Workflow automatisé pour la vérification de conformité",
            category="compliance",
            trigger_type="scheduled",
            trigger_conditions={"schedule": "monthly", "day": 1, "time": "06:00"},
            steps=compliance_steps
        )
        
        return templates
    
    def _initialize_action_handlers(self) -> Dict[str, Callable]:
        """Initialise les gestionnaires d'actions"""
        return {
            "scan": self._handle_scan_action,
            "analyze": self._handle_analyze_action,
            "notify": self._handle_notify_action,
            "remediate": self._handle_remediate_action,
            "wait": self._handle_wait_action,
            "decision": self._handle_decision_action
        }
    
    def _load_default_rules(self):
        """Charge les règles d'automatisation par défaut"""
        # Règle 1: Auto-isolation pour incidents critiques
        self.automation_rules["auto_isolate_critical"] = AutomationRule(
            rule_id="auto_isolate_critical",
            name="Isolation Automatique Incidents Critiques",
            description="Isole automatiquement les systèmes lors d'incidents critiques",
            condition={
                "incident_severity": {"$gte": 9},
                "incident_type": {"$in": ["malware", "breach", "ransomware"]}
            },
            action={
                "type": "execute_workflow",
                "workflow_id": "emergency_isolation",
                "parameters": {"immediate": True}
            },
            priority=10
        )
        
        # Règle 2: Notification automatique pour vulnérabilités critiques
        self.automation_rules["notify_critical_vulns"] = AutomationRule(
            rule_id="notify_critical_vulns",
            name="Notification Vulnérabilités Critiques",
            description="Notifie automatiquement les vulnérabilités CVSS >= 9.0",
            condition={
                "vulnerability_cvss": {"$gte": 9.0},
                "vulnerability_status": "new"
            },
            action={
                "type": "notify",
                "channels": ["email", "slack", "teams"],
                "urgency": "immediate",
                "escalation": True
            },
            priority=9
        )
        
        # Règle 3: Scan automatique après patch
        self.automation_rules["post_patch_scan"] = AutomationRule(
            rule_id="post_patch_scan",
            name="Scan Post-Patch Automatique",
            description="Lance un scan de vérification après l'application de patches",
            condition={
                "event_type": "patch_applied",
                "system_criticality": {"$gte": "medium"}
            },
            action={
                "type": "execute_workflow",
                "workflow_id": "post_patch_verification",
                "delay": 300  # 5 minutes après patch
            },
            priority=6
        )
    
    async def create_workflow(self, workflow: SecurityWorkflow) -> Dict[str, Any]:
        """Crée un nouveau workflow d'automatisation"""
        try:
            print(f"🤖 Automation AI - Création workflow {workflow.name}")
            
            # Validation du workflow
            validation_result = await self._validate_workflow(workflow)
            if not validation_result["valid"]:
                raise HTTPException(status_code=400, detail=f"Workflow invalide: {validation_result['errors']}")
            
            # Sauvegarde en base
            workflows_collection = await get_collection("automation_workflows")
            
            workflow_doc = {
                "_id": workflow.workflow_id,
                "workflow_data": workflow.dict(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_by": "automation_ai",
                "version": "1.0",
                "is_template": False
            }
            
            # Tenter l'insertion; si doublon d'ID, régénérer un ID unique
            try:
                await workflows_collection.insert_one(workflow_doc)
            except Exception:
                new_id = f"{workflow.workflow_id}-{uuid.uuid4().hex[:6]}"
                workflow.workflow_id = new_id
                workflow_doc["_id"] = new_id
                if isinstance(workflow_doc.get("workflow_data"), dict):
                    workflow_doc["workflow_data"]["workflow_id"] = new_id
                await workflows_collection.insert_one(workflow_doc)
            
            # Enregistrement local pour exécution
            if workflow.is_active:
                self.workflow_templates[workflow.workflow_id] = workflow
            
            print(f"✅ Workflow {workflow.workflow_id} créé avec succès")
            
            return {
                "status": "created",
                "workflow_id": workflow.workflow_id,
                "validation": validation_result,
                "estimated_execution_time": self._estimate_execution_time(workflow),
                "automation_recommendations": [
                    "Ajouter une étape de validation",
                    "Inclure une notification aux parties prenantes",
                    "Définir des conditions de rollback"
                ]
            }
            
        except Exception as e:
            print(f"❌ Erreur création workflow: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur création workflow: {str(e)}")
    
    async def execute_workflow(self, request: WorkflowExecutionRequest) -> WorkflowExecutionResult:
        """Exécute un workflow d'automatisation"""
        try:
            execution_id = str(uuid.uuid4())
            print(f"🚀 Automation AI - Exécution workflow {request.workflow_id} (ID: {execution_id})")
            
            # Récupération du workflow
            workflow = await self._get_workflow(request.workflow_id)
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow non trouvé")
            
            # Initialisation de l'exécution
            execution_result = WorkflowExecutionResult(
                execution_id=execution_id,
                workflow_id=request.workflow_id,
                status="running",
                start_time=datetime.now(timezone.utc),
                steps_executed=[],
                total_steps=len(workflow.steps)
            )
            
            # Enregistrement de l'exécution active
            self.active_workflows[execution_id] = execution_result
            
            # Exécution asynchrone si demandé
            if request.async_execution:
                # Lancer l'exécution en arrière-plan
                asyncio.create_task(
                    self._execute_workflow_steps(execution_result, workflow, request.input_data or {})
                )
                # Retourner immédiatement le statut
                return execution_result
            else:
                # Exécution synchrone
                return await self._execute_workflow_steps(execution_result, workflow, request.input_data or {})
            
        except Exception as e:
            print(f"❌ Erreur exécution workflow: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur exécution workflow: {str(e)}")
    
    async def _execute_workflow_steps(self, execution: WorkflowExecutionResult, 
                                    workflow: SecurityWorkflow, input_data: Dict[str, Any]) -> WorkflowExecutionResult:
        """Exécute les étapes d'un workflow"""
        context_data = input_data.copy()
        
        try:
            for step in workflow.steps:
                print(f"  ▶️ Exécution étape: {step.name}")
                
                # Initialisation de l'étape
                step_execution = WorkflowExecutionStep(
                    step_id=step.step_id,
                    name=step.name,
                    status="running",
                    start_time=datetime.now(timezone.utc)
                )
                execution.steps_executed.append(step_execution)
                
                try:
                    # Vérification des conditions d'exécution
                    if step.conditions and not self._evaluate_conditions(step.conditions, context_data):
                        step_execution.status = "skipped"
                        step_execution.end_time = datetime.now(timezone.utc)
                        print(f"    ⏭️ Étape {step.name} ignorée (conditions non remplies)")
                        continue
                    
                    # Exécution de l'action avec timeout
                    step_output = await asyncio.wait_for(
                        self._execute_step_action(step, context_data),
                        timeout=step.timeout
                    )
                    
                    # Mise à jour du contexte avec la sortie
                    if step_output:
                        context_data[f"step_{step.step_id}_output"] = step_output
                    
                    step_execution.status = "completed"
                    step_execution.output = step_output
                    step_execution.end_time = datetime.now(timezone.utc)
                    execution.success_count += 1
                    
                    print(f"    ✅ Étape {step.name} terminée avec succès")
                    
                except asyncio.TimeoutError:
                    step_execution.status = "failed"
                    step_execution.error_message = f"Timeout après {step.timeout}s"
                    step_execution.end_time = datetime.now(timezone.utc)
                    execution.failure_count += 1
                    print(f"    ⏱️ Timeout étape {step.name}")
                    
                    # Décision sur la continuation
                    if not await self._should_continue_on_failure(step, workflow):
                        break
                
                except Exception as step_error:
                    step_execution.status = "failed"
                    step_execution.error_message = str(step_error)
                    step_execution.end_time = datetime.now(timezone.utc)
                    execution.failure_count += 1
                    print(f"    ❌ Erreur étape {step.name}: {step_error}")
                    
                    # Retry logic
                    for retry in range(step.retry_count):
                        print(f"    🔄 Tentative {retry + 1}/{step.retry_count}")
                        try:
                            await asyncio.sleep(2 ** retry)  # Exponential backoff
                            step_output = await self._execute_step_action(step, context_data)
                            
                            step_execution.status = "completed"
                            step_execution.output = step_output
                            step_execution.error_message = None
                            execution.success_count += 1
                            execution.failure_count -= 1
                            
                            if step_output:
                                context_data[f"step_{step.step_id}_output"] = step_output
                            
                            print(f"    ✅ Étape {step.name} réussie après retry")
                            break
                            
                        except Exception as retry_error:
                            if retry == step.retry_count - 1:  # Dernière tentative
                                print(f"    ❌ Échec définitif étape {step.name}: {retry_error}")
                                if not await self._should_continue_on_failure(step, workflow):
                                    break
            
            # Finalisation de l'exécution
            execution.end_time = datetime.now(timezone.utc)
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            execution.output_data = context_data
            
            # Statut final
            if execution.failure_count == 0:
                execution.status = "completed"
            elif execution.success_count == 0:
                execution.status = "failed"
            else:
                execution.status = "completed_with_errors"
            
            # Sauvegarde du résultat
            await self._save_execution_result(execution)
            
            # Nettoyage
            if execution.execution_id in self.active_workflows:
                del self.active_workflows[execution.execution_id]
            
            print(f"✅ Workflow {workflow.workflow_id} terminé - Status: {execution.status}")
            return execution
            
        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now(timezone.utc)
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            await self._save_execution_result(execution)
            
            if execution.execution_id in self.active_workflows:
                del self.active_workflows[execution.execution_id]
            
            print(f"❌ Échec workflow {workflow.workflow_id}: {e}")
            raise e
    
    async def _execute_step_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Exécute une action d'étape"""
        action_handler = self.action_handlers.get(step.action_type)
        if not action_handler:
            raise ValueError(f"Action type non supporté: {step.action_type}")
        
        return await action_handler(step, context_data)
    
    async def _handle_scan_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions de scan"""
        params = step.parameters
        
        if params.get("scan_type") == "nmap":
            # Simulation d'un scan nmap
            await asyncio.sleep(2)  # Simulation du temps de scan
            return {
                "scan_type": "nmap",
                "target": params.get("target", context_data.get("target", "127.0.0.1")),
                "open_ports": [22, 80, 443, 8080],
                "services": {
                    "22": "ssh",
                    "80": "http",
                    "443": "https",
                    "8080": "http-alt"
                },
                "scan_duration": 2.1,
                "hosts_discovered": 1
            }
        
        elif params.get("scanner") == "openvas":
            # Simulation d'un scan OpenVAS
            await asyncio.sleep(5)  # Simulation du temps de scan
            return {
                "scanner": "openvas",
                "vulnerabilities_found": 7,
                "high_severity": 2,
                "medium_severity": 3,
                "low_severity": 2,
                "scan_coverage": "95%",
                "scan_duration": 5.2
            }
        
        else:
            # Scan générique
            await asyncio.sleep(1)
            return {
                "scan_completed": True,
                "scan_type": params.get("scan_type", "generic"),
                "results": "scan_data_placeholder"
            }
    
    async def _handle_analyze_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions d'analyse"""
        params = step.parameters
        analysis_type = params.get("analysis_type", "generic")
        
        if analysis_type == "risk_assessment":
            # Analyse de risque
            vuln_count = context_data.get("step_vulnerability_scan_output", {}).get("vulnerabilities_found", 5)
            risk_score = min(vuln_count * 8, 100)
            
            return {
                "analysis_type": "risk_assessment",
                "risk_score": risk_score,
                "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low",
                "vulnerabilities_analyzed": vuln_count,
                "cvss_average": round(risk_score / 10, 1),
                "recommendations": [
                    "Patch high severity vulnerabilities immediately",
                    "Implement additional monitoring",
                    "Review security configurations"
                ]
            }
        
        elif analysis_type == "behavioral":
            # Analyse comportementale
            await asyncio.sleep(1)
            return {
                "analysis_type": "behavioral",
                "anomalies_detected": 3,
                "confidence_score": 0.85,
                "threat_indicators": ["unusual_login_patterns", "suspicious_file_access", "network_anomalies"],
                "recommended_actions": ["investigate_further", "increase_monitoring"]
            }
        
        elif params.get("classification_model") == "incident_severity":
            # Classification d'incident
            return {
                "incident_classification": "malware_infection",
                "severity_score": 7,
                "confidence": 0.82,
                "affected_systems": 3,
                "estimated_impact": "medium",
                "response_priority": "high"
            }
        
        else:
            # Analyse générique
            return {
                "analysis_completed": True,
                "analysis_type": analysis_type,
                "confidence": 0.75,
                "results": "analysis_data_placeholder"
            }
    
    async def _handle_notify_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions de notification"""
        params = step.parameters
        channels = params.get("channels", ["email"])
        
        # Simulation d'envoi de notifications
        notifications_sent = []
        
        for channel in channels:
            if channel == "email":
                notifications_sent.append({
                    "channel": "email",
                    "status": "sent",
                    "recipients": ["admin@company.com", "security@company.com"],
                    "message_id": f"email_{uuid.uuid4().hex[:8]}"
                })
            elif channel == "slack":
                notifications_sent.append({
                    "channel": "slack",
                    "status": "sent",
                    "channel_name": "#security-alerts",
                    "message_ts": "1234567890.123456"
                })
            elif channel == "sms":
                notifications_sent.append({
                    "channel": "sms",
                    "status": "sent",
                    "recipients": ["+33123456789"],
                    "message_id": f"sms_{uuid.uuid4().hex[:8]}"
                })
        
        # Simulation du temps d'envoi
        await asyncio.sleep(0.5)
        
        return {
            "notification_action": "completed",
            "notifications_sent": notifications_sent,
            "total_notifications": len(notifications_sent),
            "urgency": params.get("urgency", "medium"),
            "delivery_time": 0.5
        }
    
    async def _handle_remediate_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions de remédiation"""
        params = step.parameters
        
        if params.get("isolation_type") == "network":
            # Isolation réseau
            await asyncio.sleep(1)
            return {
                "remediation_type": "network_isolation",
                "systems_isolated": params.get("scope", "affected_only"),
                "isolation_rules_applied": 5,
                "isolation_status": "active",
                "rollback_available": True,
                "isolated_at": datetime.now(timezone.utc).isoformat()
            }
        
        else:
            # Remédiation générique
            return {
                "remediation_completed": True,
                "remediation_type": params.get("type", "generic"),
                "systems_affected": 1,
                "success": True
            }
    
    async def _handle_wait_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions d'attente"""
        wait_time = step.parameters.get("duration", 5)
        await asyncio.sleep(wait_time)
        
        return {
            "wait_completed": True,
            "wait_duration": wait_time,
            "waited_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _handle_decision_action(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour les actions de décision IA"""
        params = step.parameters
        
        # Utiliser l'IA pour prendre une décision
        if self.llm_client:
            decision = await self._make_ai_decision(step, context_data)
        else:
            # Décision basée sur des règles simples
            decision = await self._make_rule_based_decision(step, context_data)
        
        return decision
    
    async def _make_ai_decision(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prend une décision basée sur l'IA"""
        try:
            decision_context = step.parameters.get("context", "")
            available_data = json.dumps(context_data, indent=2, default=str)
            
            prompt = f"""En tant qu'expert en cybersécurité, analysez cette situation et prenez une décision:

Contexte de décision: {decision_context}
Données disponibles: {available_data}

Options disponibles: {step.parameters.get('options', ['continue', 'stop', 'escalate'])}

Fournissez votre décision sous format JSON avec:
- decision: l'option choisie
- confidence: niveau de confiance (0-1)
- reasoning: justification de la décision
- next_actions: actions recommandées"""

            messages = [
                {"role": "system", "content": "Tu es un expert en cybersécurité qui prend des décisions basées sur l'analyse de données."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat.completions.create,
                model=settings.default_llm_model,
                messages=messages,
                max_tokens=800,
                temperature=0.3
            )
            
            # Tenter de parser la réponse JSON
            try:
                decision_data = json.loads(response.choices[0].message.content)
                return {
                    "decision_type": "ai_powered",
                    "decision": decision_data.get("decision", "continue"),
                    "confidence": decision_data.get("confidence", 0.7),
                    "reasoning": decision_data.get("reasoning", "AI analysis"),
                    "next_actions": decision_data.get("next_actions", [])
                }
            except json.JSONDecodeError:
                # Fallback si pas de JSON valide
                return {
                    "decision_type": "ai_text",
                    "decision": "continue",
                    "confidence": 0.6,
                    "ai_response": response.choices[0].message.content
                }
                
        except Exception as e:
            print(f"⚠️ Erreur décision IA: {e}")
            return await self._make_rule_based_decision(step, context_data)
    
    async def _make_rule_based_decision(self, step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prend une décision basée sur des règles"""
        options = step.parameters.get("options", ["continue", "stop"])
        decision_rules = step.parameters.get("rules", {})
        
        # Évaluer les règles de décision
        decision = "continue"  # Par défaut
        confidence = 0.5
        
        for rule_condition, rule_decision in decision_rules.items():
            if self._evaluate_condition_string(rule_condition, context_data):
                decision = rule_decision
                confidence = 0.8
                break
        
        return {
            "decision_type": "rule_based",
            "decision": decision,
            "confidence": confidence,
            "rules_evaluated": len(decision_rules),
            "context_data_size": len(context_data)
        }

    async def _get_historical_executions(self, limit: int) -> List[Dict[str, Any]]:
        try:
            coll = await get_collection("automation_executions")
            docs = await coll.find({})
            docs = await docs.to_list(length=limit) if hasattr(docs, "to_list") else (docs if isinstance(docs, list) else [])
            return docs[-limit:]
        except Exception as e:
            print(f"⚠️ _get_historical_executions error: {e}")
            return []

    async def _get_execution_from_history(self, execution_id: str) -> Optional[Dict[str, Any]]:
        try:
            coll = await get_collection("automation_executions")
            docs = await coll.find({})
            docs = await docs.to_list(length=2000) if hasattr(docs, "to_list") else (docs if isinstance(docs, list) else [])
            for d in docs:
                if d.get("execution_id") == execution_id:
                    return d
        except Exception as e:
            print(f"⚠️ _get_execution_from_history error: {e}")
        return None

    async def _save_execution_result(self, execution: WorkflowExecutionResult):
        try:
            coll = await get_collection("automation_executions")
            await coll.insert_one({
                "_id": execution.execution_id,
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status,
                "start_time": execution.start_time.isoformat() if hasattr(execution.start_time, 'isoformat') else execution.start_time,
                "end_time": execution.end_time.isoformat() if execution.end_time and hasattr(execution.end_time, 'isoformat') else execution.end_time,
                "execution_time": execution.execution_time,
                "success_count": execution.success_count,
                "failure_count": execution.failure_count
            })
        except Exception as e:
            print(f"⚠️ _save_execution_result error: {e}")


    async def _validate_workflow(self, workflow: SecurityWorkflow) -> Dict[str, Any]:
        errors = []
        if not workflow.steps:
            errors.append("Aucune étape fournie")
        for s in workflow.steps:
            if s.action_type not in self.action_handlers:
                errors.append(f"Action non supportée: {s.action_type}")
        return {"valid": len(errors) == 0, "errors": errors}

    async def _get_workflow(self, workflow_id: str) -> Optional[SecurityWorkflow]:
        # Priorité aux workflows en mémoire (templates + créés)
        wf = self.workflow_templates.get(workflow_id)
        if wf:
            return wf
        try:
            coll = await get_collection("automation_workflows")
            docs = await coll.find({})
            docs = await docs.to_list(length=1000) if hasattr(docs, "to_list") else (docs if isinstance(docs, list) else [])
            for d in docs:
                wd = d.get("workflow_data")
                if wd and wd.get("workflow_id") == workflow_id:
                    # Reconstruction minimale
                    steps = [WorkflowStep(**st) if not isinstance(st, WorkflowStep) else st for st in wd.get("steps", [])]
                    return SecurityWorkflow(
                        workflow_id=wd.get("workflow_id"),
                        name=wd.get("name", "Workflow"),
                        description=wd.get("description", ""),
                        category=wd.get("category", "incident_response"),
                        trigger_type=wd.get("trigger_type", "manual"),
                        trigger_conditions=wd.get("trigger_conditions", {}),
                        steps=steps,
                        is_active=wd.get("is_active", True)
                    )
        except Exception:
            pass
        return None

    def _evaluate_conditions(self, conditions: Optional[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        if not conditions:
            return True
        # Évaluation très simple des opérateurs
        for key, rule in conditions.items():
            value = context.get(key)
            if isinstance(rule, dict):
                if "$gte" in rule and not (value is not None and value >= rule["$gte"]):
                    return False
                if "$gt" in rule and not (value is not None and value > rule["$gt"]):
                    return False
                if "$in" in rule and not (value in rule["$in"]):
                    return False
            else:
                if value != rule:
                    return False
        return True

    async def _should_continue_on_failure(self, step: WorkflowStep, workflow: SecurityWorkflow) -> bool:
        # Politique simple: continuer si priorité faible/modérée
        return True

    async def _save_automation_rule(self, rule: AutomationRule) -> None:
        try:
            coll = await get_collection("automation_rules")
            await coll.insert_one({"_id": rule.rule_id, **rule.dict()})
        except Exception:
            pass

    def _estimate_execution_time(self, workflow: SecurityWorkflow) -> int:
        # Somme des timeouts minimaux par étape (heuristique simple)
        base = 0
        for s in workflow.steps:
            base += min(max(s.timeout // 3, 1), 60)
        return base

    async def _get_recent_executions(self, workflow_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            coll = await get_collection("automation_executions")
            docs = await coll.find({"workflow_id": workflow_id})
            docs = await docs.to_list(length=200) if hasattr(docs, "to_list") else (docs if isinstance(docs, list) else [])
            return docs[-limit:]
        except Exception:
            return []

    def _calculate_status_distribution(self, executions: List[Dict[str, Any]]) -> Dict[str, int]:
        dist: Dict[str, int] = {}
        for exe in executions:
            s = exe.get("status", "unknown")
            dist[s] = dist.get(s, 0) + 1
        return dist

# Instance globale du service Automation AI
automation_ai_service = AutomationAIService()