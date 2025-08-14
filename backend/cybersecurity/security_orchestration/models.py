"""
Security Orchestration Module - Models
Modèles de données pour l'orchestration et l'automatisation sécuritaire (SOAR)
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class PlaybookStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class ActionType(str, Enum):
    EMAIL_NOTIFICATION = "email_notification"
    SLACK_NOTIFICATION = "slack_notification"
    TICKET_CREATION = "ticket_creation"
    IP_BLOCKING = "ip_blocking"
    USER_ISOLATION = "user_isolation"
    SCAN_INITIATION = "scan_initiation"
    LOG_COLLECTION = "log_collection"
    THREAT_HUNTING = "threat_hunting"
    CONTAINMENT = "containment"
    EVIDENCE_COLLECTION = "evidence_collection"

class TriggerCondition(BaseModel):
    condition_id: str
    name: str
    description: str
    condition_type: str  # event, schedule, manual, api
    parameters: Dict[str, Any]
    enabled: bool = True

class PlaybookAction(BaseModel):
    action_id: str
    name: str
    action_type: ActionType
    description: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 300
    retry_attempts: int = 3
    continue_on_failure: bool = False
    depends_on: Optional[List[str]] = None  # Liste des action_ids prérequis

class SOARPlaybook(BaseModel):
    playbook_id: str
    name: str
    description: str
    category: str  # incident_response, threat_hunting, compliance, vulnerability_management
    version: str
    created_by: str
    created_at: str
    updated_at: str
    status: PlaybookStatus
    triggers: List[TriggerCondition]
    actions: List[PlaybookAction]
    tags: List[str] = []
    approval_required: bool = False
    auto_execute: bool = False

class PlaybookExecution(BaseModel):
    execution_id: str
    playbook_id: str
    playbook_name: str
    triggered_by: str  # user_id ou system
    trigger_condition: str
    status: PlaybookStatus
    started_at: str
    completed_at: Optional[str] = None
    context: Dict[str, Any] = {}  # Variables et données contextuelles
    results: Dict[str, Any] = {}  # Résultats de chaque action

class ActionExecution(BaseModel):
    action_execution_id: str
    execution_id: str
    action_id: str
    action_name: str
    action_type: ActionType
    status: str  # pending, running, completed, failed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class SOARRunRequest(BaseModel):
    playbook_id: str
    trigger_source: str = "manual"
    context: Optional[Dict[str, Any]] = None
    override_parameters: Optional[Dict[str, Any]] = None

class IntegrationConfig(BaseModel):
    integration_id: str
    name: str
    integration_type: str  # siem, ticketing, email, chat, firewall, etc.
    config: Dict[str, Any]
    enabled: bool = True
    last_tested: Optional[str] = None
    status: str = "active"  # active, inactive, error

class SOARMetrics(BaseModel):
    total_playbooks: int
    active_playbooks: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    executions_last_24h: int
    top_triggered_playbooks: List[Dict[str, Any]]
    integration_status: Dict[str, str]

class IncidentContext(BaseModel):
    incident_id: str
    incident_type: str
    severity: str  # low, medium, high, critical
    source_system: str
    affected_assets: List[str]
    indicators: Dict[str, Any]  # IOCs, IP addresses, domains, etc.
    timeline: List[Dict[str, Any]]
    status: str

class SOARAlert(BaseModel):
    alert_id: str
    title: str
    description: str
    severity: str
    source: str
    created_at: str
    indicators: Dict[str, Any]
    recommended_playbooks: List[str]
    auto_triggered_playbooks: List[str] = []