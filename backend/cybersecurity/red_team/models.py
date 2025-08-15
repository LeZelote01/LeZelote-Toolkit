"""
Modèles de données pour le service Red Team Operations
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

# Enums pour Red Team Operations
class CampaignStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AttackPhase(str, Enum):
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

class TTTactic(str, Enum):
    MITRE_ATT_CK = "mitre_attck"
    CUSTOM = "custom"
    OWASP = "owasp"
    NIST = "nist"

class OperationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OperationStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TargetType(str, Enum):
    NETWORK = "network"
    APPLICATION = "application"
    EMAIL = "email"
    PHYSICAL = "physical"
    SOCIAL = "social"
    WIRELESS = "wireless"

class AssetType(str, Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    MOBILE = "mobile"
    IOT = "iot"
    NETWORK_DEVICE = "network_device"
    APPLICATION = "application"
    DATABASE = "database"

# Modèles de base
class TTPTechnique(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    technique_id: str  # Ex: T1566.001
    name: str
    description: str
    tactic: TTTactic
    phase: AttackPhase
    platforms: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard
    stealth_level: str = "medium"  # low, medium, high
    success_rate: float = 0.5
    detection_rate: float = 0.5

class Target(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: TargetType
    description: str
    ip_ranges: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    contacts: List[str] = Field(default_factory=list)
    criticality: OperationSeverity = OperationSeverity.MEDIUM
    business_impact: str = ""
    technical_details: Dict[str, Any] = Field(default_factory=dict)
    vulnerabilities: List[str] = Field(default_factory=list)
    defenses: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RedTeamAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: AssetType
    description: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    credentials: Dict[str, Any] = Field(default_factory=dict)
    access_level: str = "none"  # none, user, admin, system
    compromise_date: Optional[datetime] = None
    persistence_methods: List[str] = Field(default_factory=list)
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Operation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    technique: TTPTechnique
    target_id: str
    status: OperationStatus = OperationStatus.PLANNED
    severity: OperationSeverity = OperationSeverity.MEDIUM
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # en secondes
    
    # Execution details
    commands: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    payload: Optional[str] = None
    
    # Results
    success: Optional[bool] = None
    output: str = ""
    screenshots: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    iocs_generated: List[str] = Field(default_factory=list)
    
    # Analysis
    detection_triggered: bool = False
    blue_team_response: str = ""
    lessons_learned: str = ""
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    operator: str
    campaign_id: Optional[str] = None
    parent_operation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    objective: str
    status: CampaignStatus = CampaignStatus.PLANNING
    
    # Scope
    targets: List[str] = Field(default_factory=list)  # Target IDs
    scope_description: str = ""
    out_of_scope: List[str] = Field(default_factory=list)
    
    # Planning
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # en jours
    
    # Team
    red_team_lead: str
    operators: List[str] = Field(default_factory=list)
    blue_team_contacts: List[str] = Field(default_factory=list)
    
    # Rules of Engagement
    roe_document: Optional[str] = None
    authorized_techniques: List[str] = Field(default_factory=list)
    forbidden_techniques: List[str] = Field(default_factory=list)
    business_hours_only: bool = False
    notification_required: bool = True
    
    # Progress
    phases_completed: List[AttackPhase] = Field(default_factory=list)
    operations_planned: int = 0
    operations_completed: int = 0
    operations_successful: int = 0
    
    # Results
    compromise_objectives: List[str] = Field(default_factory=list)
    compromise_achieved: List[str] = Field(default_factory=list)
    vulnerabilities_found: List[str] = Field(default_factory=list)
    detection_gaps: List[str] = Field(default_factory=list)
    
    # Reports
    daily_reports: List[str] = Field(default_factory=list)
    final_report_path: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str

class PurpleTeamExercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    campaign_id: str
    
    # Participants
    red_team_members: List[str] = Field(default_factory=list)
    blue_team_members: List[str] = Field(default_factory=list)
    facilitators: List[str] = Field(default_factory=list)
    
    # Scenario
    scenario_description: str
    techniques_to_test: List[TTPTechnique] = Field(default_factory=list)
    detection_rules_to_validate: List[str] = Field(default_factory=list)
    
    # Execution
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: OperationStatus = OperationStatus.PLANNED
    
    # Results
    detections_triggered: int = 0
    false_positives: int = 0
    missed_detections: int = 0
    response_time_avg: Optional[float] = None
    
    # Collaboration
    real_time_chat: List[Dict[str, Any]] = Field(default_factory=list)
    shared_observations: List[str] = Field(default_factory=list)
    joint_analysis: str = ""
    
    # Improvements
    detection_improvements: List[str] = Field(default_factory=list)
    response_improvements: List[str] = Field(default_factory=list)
    red_team_lessons: List[str] = Field(default_factory=list)
    blue_team_lessons: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RedTeamReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    campaign_id: str
    report_type: str = "campaign_summary"  # daily, weekly, campaign_summary, purple_team
    
    # Content
    executive_summary: str
    methodology: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    
    # Technical details
    techniques_used: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    iocs_generated: List[str] = Field(default_factory=list)
    detection_evasion: List[str] = Field(default_factory=list)
    
    # Metrics
    objectives_achieved: int = 0
    total_objectives: int = 0
    operations_successful: int = 0
    total_operations: int = 0
    detection_rate: float = 0.0
    dwell_time: Optional[int] = None  # en heures
    
    # Collaboration
    blue_team_feedback: str = ""
    purple_team_insights: List[str] = Field(default_factory=list)
    
    # Files
    attachments: List[str] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str

# Modèles de requête
class CreateCampaignRequest(BaseModel):
    name: str
    description: str
    objective: str
    scope_description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    red_team_lead: str
    operators: List[str] = Field(default_factory=list)
    blue_team_contacts: List[str] = Field(default_factory=list)
    authorized_techniques: List[str] = Field(default_factory=list)
    business_hours_only: bool = False
    notification_required: bool = True
    created_by: str

class UpdateCampaignRequest(BaseModel):
    status: Optional[CampaignStatus] = None
    description: Optional[str] = None
    operators: Optional[List[str]] = None
    phases_completed: Optional[List[AttackPhase]] = None
    updated_by: str

class CreateOperationRequest(BaseModel):
    name: str
    description: str
    technique_id: str  # Reference to TTPTechnique
    target_id: str
    campaign_id: Optional[str] = None
    commands: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    payload: Optional[str] = None
    operator: str

class UpdateOperationRequest(BaseModel):
    status: Optional[OperationStatus] = None
    output: Optional[str] = None
    success: Optional[bool] = None
    detection_triggered: Optional[bool] = None
    blue_team_response: Optional[str] = None
    lessons_learned: Optional[str] = None
    recommendations: Optional[List[str]] = None

class CreateTargetRequest(BaseModel):
    name: str
    type: TargetType
    description: str
    ip_ranges: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    criticality: OperationSeverity = OperationSeverity.MEDIUM
    business_impact: str = ""

class CreatePurpleTeamExerciseRequest(BaseModel):
    name: str
    description: str
    campaign_id: str
    scenario_description: str
    red_team_members: List[str] = Field(default_factory=list)
    blue_team_members: List[str] = Field(default_factory=list)
    techniques_to_test: List[str] = Field(default_factory=list)  # TTP IDs

class CampaignSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[CampaignStatus]] = None
    red_team_lead: Optional[str] = None
    date_from: Optional[date] = None  
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

class OperationSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[OperationStatus]] = None
    campaign_id: Optional[str] = None
    technique: Optional[str] = None
    operator: Optional[str] = None
    success: Optional[bool] = None
    limit: int = 50
    offset: int = 0

# Modèles de réponse
class RedTeamStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    active_campaigns: int
    total_operations: int
    completed_operations: int
    purple_team_exercises: int
    operators_online: int
    last_operation_time: Optional[datetime] = None

class CampaignStatistics(BaseModel):
    total_campaigns: int
    by_status: Dict[str, int]
    by_red_team_lead: Dict[str, int]
    active_campaigns: int
    completed_campaigns: int
    avg_duration_days: float
    success_rate: float
    operations_total: int
    operations_successful: int
    techniques_used: Dict[str, int]
    top_operators: List[Dict[str, Any]]

class OperationStatistics(BaseModel):
    total_operations: int
    by_status: Dict[str, int]
    by_technique: Dict[str, int]
    by_phase: Dict[str, int]
    success_rate: float
    detection_rate: float
    avg_duration_minutes: float
    most_successful_techniques: List[Dict[str, Any]]
    most_detected_techniques: List[Dict[str, Any]]

class RedTeamInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    insight_type: str  # performance, security_gap, technique_effectiveness
    severity: OperationSeverity
    confidence: str  # low, medium, high
    data: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)