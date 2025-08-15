"""
Modèles de données pour le service Monitoring 24/7
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

# Enums pour la typologie
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
    INFO = "info"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class MonitoringSource(str, Enum):
    NETWORK = "network"
    SYSTEM = "system"
    APPLICATION = "application"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    USER_BEHAVIOR = "user_behavior"
    THREAT_INTEL = "threat_intel"

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

# Modèles de base
class MonitoringMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: MetricType
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.now)
    labels: Dict[str, str] = Field(default_factory=dict)
    source: MonitoringSource
    description: Optional[str] = None

class SecurityAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    source: MonitoringSource
    source_system: str
    category: str
    detected_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    indicators: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    remediation_steps: List[str] = Field(default_factory=list)
    false_positive: bool = False
    escalation_count: int = 0
    correlation_id: Optional[str] = None

class MonitoringRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    condition: str  # Expression de condition (ex: "cpu_usage > 80")
    severity: AlertSeverity
    enabled: bool = True
    source: MonitoringSource
    threshold_value: float
    threshold_operator: str  # >, <, ==, !=, >=, <=
    evaluation_window: int = 300  # secondes
    cool_down_period: int = 600  # secondes
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    tags: List[str] = Field(default_factory=list)
    notification_channels: List[str] = Field(default_factory=list)

class SystemHealthStatus(BaseModel):
    component: str
    status: str  # healthy, warning, critical, unknown
    last_check: datetime
    uptime: float  # en secondes
    response_time: Optional[float] = None  # en ms
    error_rate: Optional[float] = None  # pourcentage
    details: Dict[str, Any] = Field(default_factory=dict)

class DashboardWidget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    type: str  # chart, gauge, table, alert_list, etc.
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    data_source: str
    refresh_interval: int = 30  # secondes

class MonitoringDashboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    widgets: List[DashboardWidget] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    shared: bool = False
    tags: List[str] = Field(default_factory=list)

# Modèles de requête
class CreateAlertRequest(BaseModel):
    title: str
    description: str
    severity: AlertSeverity
    source: MonitoringSource
    source_system: str
    category: str
    indicators: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class UpdateAlertRequest(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    remediation_steps: Optional[List[str]] = None
    false_positive: Optional[bool] = None
    tags: Optional[List[str]] = None
    updated_by: str

class CreateRuleRequest(BaseModel):
    name: str
    description: str
    condition: str
    severity: AlertSeverity
    source: MonitoringSource
    threshold_value: float
    threshold_operator: str
    evaluation_window: int = 300
    cool_down_period: int = 600
    created_by: str
    tags: List[str] = Field(default_factory=list)
    notification_channels: List[str] = Field(default_factory=list)

class MetricQueryRequest(BaseModel):
    metric_name: Optional[str] = None
    source: Optional[MonitoringSource] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    aggregation: str = "avg"  # avg, sum, min, max, count
    interval: str = "5m"  # 1m, 5m, 15m, 1h, etc.

class AlertSearchRequest(BaseModel):
    query: Optional[str] = None
    severity: Optional[List[AlertSeverity]] = None
    status: Optional[List[AlertStatus]] = None
    source: Optional[List[MonitoringSource]] = None
    assigned_to: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0

# Modèles de réponse
class MonitoringStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    active_alerts: int
    critical_alerts: int
    monitoring_rules: int
    system_health: List[SystemHealthStatus]
    uptime: float
    last_alert_time: Optional[datetime] = None

class AlertStatistics(BaseModel):
    total_alerts: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    by_source: Dict[str, int]
    alerts_last_24h: int
    avg_resolution_time: Optional[float] = None  # en minutes
    false_positive_rate: float

class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

class MetricQueryResponse(BaseModel):
    metric_name: str
    data_points: List[MetricDataPoint]
    total_points: int
    aggregation: str
    interval: str
    query_duration: float  # en secondes

class MonitoringReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    period_start: datetime
    period_end: datetime
    
    # Statistiques principales
    total_alerts: int
    critical_alerts: int
    resolved_alerts: int
    false_positives: int
    avg_resolution_time: float
    
    # Détails par catégorie
    alerts_by_severity: Dict[str, int]
    alerts_by_source: Dict[str, int]
    top_alert_categories: List[Dict[str, Any]]
    
    # Métriques système
    system_availability: float
    average_response_time: float
    performance_trends: List[Dict[str, Any]]
    
    # Recommandations
    recommendations: List[str]
    summary: str