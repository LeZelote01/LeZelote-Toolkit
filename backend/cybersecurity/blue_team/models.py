"""
Modèles de données pour Blue Team Defense
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

# Enums pour Blue Team Defense
class ThreatSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class HuntStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class ResponseAction(str, Enum):
    MONITOR = "monitor"
    ISOLATE = "isolate"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    PATCH = "patch"
    INVESTIGATE = "investigate"
    ESCALATE = "escalate"

class DataSource(str, Enum):
    LOGS = "logs"
    NETWORK = "network"
    ENDPOINT = "endpoint"
    EMAIL = "email"
    DNS = "dns"
    WEB_PROXY = "web_proxy"
    FIREWALL = "firewall"
    IDS_IPS = "ids_ips"
    SIEM = "siem"
    EDR = "edr"
    THREAT_INTELLIGENCE = "threat_intelligence"

class HuntTechnique(str, Enum):
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    IOC_HUNTING = "ioc_hunting"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_MATCHING = "pattern_matching"
    BASELINE_DEVIATION = "baseline_deviation"
    CORRELATION_ANALYSIS = "correlation_analysis"
    SANDBOXING = "sandboxing"
    HONEYPOT = "honeypot"

class DetectionType(str, Enum):
    SIGNATURE = "signature"
    BEHAVIORAL = "behavioral"
    ANOMALY = "anomaly"
    HEURISTIC = "heuristic"
    ML_BASED = "ml_based"
    STATISTICAL = "statistical"

# Modèles de base
class IOC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # ip, domain, hash, url, email, etc.
    value: str
    description: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    source: str = ""
    tags: List[str] = Field(default_factory=list)
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    false_positive: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)
    related_campaigns: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DetectionRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    rule_type: DetectionType
    rule_content: str  # YARA, Sigma, SQL, etc.
    data_sources: List[DataSource]
    mitre_techniques: List[str] = Field(default_factory=list)
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    is_enabled: bool = True
    is_tuned: bool = False
    false_positive_rate: float = Field(ge=0.0, le=1.0, default=0.1)
    tags: List[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: ThreatSeverity
    status: AlertStatus = AlertStatus.NEW
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    
    # Source
    source_system: str
    detection_rule_id: Optional[str] = None
    data_source: DataSource
    
    # Timeline
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Affected assets
    affected_assets: List[str] = Field(default_factory=list)
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user_account: Optional[str] = None
    host: Optional[str] = None
    
    # IOCs and artifacts
    iocs: List[str] = Field(default_factory=list)  # IOC IDs
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    
    # Investigation
    assigned_to: Optional[str] = None
    investigation_notes: str = ""
    actions_taken: List[ResponseAction] = Field(default_factory=list)
    response_time: Optional[int] = None  # en minutes
    resolution_time: Optional[int] = None  # en minutes
    
    # Classification
    false_positive: bool = False
    true_positive: bool = False
    mitre_techniques: List[str] = Field(default_factory=list)
    attack_stage: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    related_alerts: List[str] = Field(default_factory=list)
    escalated: bool = False

class ThreatHunt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    hypothesis: str
    status: HuntStatus = HuntStatus.PLANNED
    
    # Hunt details
    hunt_technique: HuntTechnique
    data_sources: List[DataSource]
    time_range: Dict[str, datetime] = Field(default_factory=dict)  # start, end
    query: str = ""  # KQL, SQL, Elasticsearch, etc.
    
    # Team
    hunter: str
    collaborators: List[str] = Field(default_factory=list)
    
    # Planning
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    
    # Results
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    new_iocs: List[str] = Field(default_factory=list)
    new_rules: List[str] = Field(default_factory=list)
    alerts_generated: int = 0
    true_positives: int = 0
    false_positives: int = 0
    
    # Analysis
    threat_actors: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    lessons_learned: str = ""
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    related_hunts: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DefensiveAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    action_type: ResponseAction
    
    # Target
    target_type: str  # host, network, user, file, etc.
    target_identifier: str
    
    # Execution
    executed_by: str
    executed_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"  # pending, success, failed, partial
    
    # Details
    command: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: str = ""
    error_message: Optional[str] = None
    
    # Context
    alert_id: Optional[str] = None
    hunt_id: Optional[str] = None
    incident_id: Optional[str] = None
    
    # Validation
    verification_required: bool = False
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.now)

class ThreatIntel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    
    # Threat details
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    malware_family: Optional[str] = None
    ttps: List[str] = Field(default_factory=list)
    targets: List[str] = Field(default_factory=list)
    
    # IOCs
    iocs: List[str] = Field(default_factory=list)  # IOC IDs
    
    # Timeline
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    published_at: datetime = Field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DefenseBaseline(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    data_source: DataSource
    
    # Baseline parameters
    time_period: Dict[str, datetime]  # start, end for baseline
    metrics: Dict[str, Any] = Field(default_factory=dict)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Status
    is_active: bool = True
    last_updated: datetime = Field(default_factory=datetime.now)
    update_frequency: str = "daily"  # hourly, daily, weekly
    
    # Anomalies
    anomalies_detected: int = 0
    last_anomaly: Optional[datetime] = None
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

# Modèles de requête
class CreateIOCRequest(BaseModel):
    type: str
    value: str
    description: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    source: str = ""
    tags: List[str] = Field(default_factory=list)

class CreateDetectionRuleRequest(BaseModel):
    name: str
    description: str
    rule_type: DetectionType
    rule_content: str
    data_sources: List[DataSource]
    mitre_techniques: List[str] = Field(default_factory=list)
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    created_by: str
    tags: List[str] = Field(default_factory=list)

class CreateAlertRequest(BaseModel):
    title: str
    description: str
    severity: ThreatSeverity
    source_system: str
    data_source: DataSource
    affected_assets: List[str] = Field(default_factory=list)
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user_account: Optional[str] = None
    host: Optional[str] = None

class UpdateAlertRequest(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    investigation_notes: Optional[str] = None
    actions_taken: Optional[List[ResponseAction]] = None
    false_positive: Optional[bool] = None
    true_positive: Optional[bool] = None
    mitre_techniques: Optional[List[str]] = None

class CreateThreatHuntRequest(BaseModel):
    name: str
    description: str
    hypothesis: str
    hunt_technique: HuntTechnique
    data_sources: List[DataSource]
    query: str = ""
    hunter: str
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None

class UpdateThreatHuntRequest(BaseModel):
    status: Optional[HuntStatus] = None
    findings: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    lessons_learned: Optional[str] = None

class ExecuteDefensiveActionRequest(BaseModel):
    name: str
    description: str
    action_type: ResponseAction
    target_type: str
    target_identifier: str
    command: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    executed_by: str
    alert_id: Optional[str] = None

class IOCSearchRequest(BaseModel):
    query: Optional[str] = None
    ioc_type: Optional[str] = None
    severity: Optional[List[ThreatSeverity]] = None
    is_active: Optional[bool] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

class AlertSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[AlertStatus]] = None
    severity: Optional[List[ThreatSeverity]] = None
    assigned_to: Optional[str] = None
    data_source: Optional[DataSource] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

class HuntSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[HuntStatus]] = None
    hunter: Optional[str] = None
    hunt_technique: Optional[HuntTechnique] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

# Modèles de réponse
class BlueTeamStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    active_alerts: int
    active_hunts: int
    iocs_monitored: int
    detection_rules: int
    last_threat_detection: Optional[datetime] = None

class AlertStatistics(BaseModel):
    total_alerts: int
    by_status: Dict[str, int]
    by_severity: Dict[str, int]
    by_data_source: Dict[str, int]
    true_positive_rate: float
    false_positive_rate: float
    avg_response_time: float
    avg_resolution_time: float
    escalated_alerts: int
    alerts_last_24h: int

class HuntStatistics(BaseModel):
    total_hunts: int
    by_status: Dict[str, int]
    by_technique: Dict[str, int]
    by_hunter: Dict[str, int]
    success_rate: float
    avg_duration_hours: float
    new_iocs_discovered: int
    new_rules_created: int
    threats_identified: int

class DefenseInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    insight_type: str  # threat_trend, performance, coverage_gap, effectiveness
    severity: ThreatSeverity
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    data: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)