"""
Modèles de données pour Audit Automatisé
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

# Enums pour Audit Automatisé
class AuditFramework(str, Enum):
    ISO27001 = "iso27001"
    NIST_CSF = "nist_csf"
    CIS_CONTROLS = "cis_controls"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    COBIT = "cobit"
    COSO = "coso"
    OWASP_TOP10 = "owasp_top10"
    SANS_TOP25 = "sans_top25"
    CUSTOM = "custom"

class AuditType(str, Enum):
    COMPLIANCE = "compliance"
    SECURITY_POSTURE = "security_posture"
    VULNERABILITY = "vulnerability"
    CONFIGURATION = "configuration"
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    NETWORK_SECURITY = "network_security"
    ENDPOINT_SECURITY = "endpoint_security"
    CLOUD_SECURITY = "cloud_security"
    APPLICATION_SECURITY = "application_security"

class AuditStatus(str, Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class FindingSeverity(str, Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FindingStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"
    DEFERRED = "deferred"

class RemediationStatus(str, Enum):
    NOT_STARTED = "not_started"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    REJECTED = "rejected"

class AssetType(str, Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    DATABASE = "database"
    APPLICATION = "application"
    CLOUD_SERVICE = "cloud_service"
    MOBILE_DEVICE = "mobile_device"
    IOT_DEVICE = "iot_device"

class TestMethod(str, Enum):
    AUTOMATED_SCAN = "automated_scan"
    MANUAL_REVIEW = "manual_review"
    INTERVIEW = "interview"
    DOCUMENT_REVIEW = "document_review"
    OBSERVATION = "observation"
    CONFIGURATION_CHECK = "configuration_check"
    VULNERABILITY_SCAN = "vulnerability_scan"
    PENETRATION_TEST = "penetration_test"

# Modèles de base
class AuditControl(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    control_id: str  # Ex: ISO.5.1.1, CIS.1.1
    framework: AuditFramework
    title: str
    description: str
    objective: str
    
    # Classification
    category: str
    subcategory: str = ""
    risk_rating: FindingSeverity = FindingSeverity.MEDIUM
    
    # Implementation guidance
    implementation_guidance: str = ""
    testing_procedures: List[str] = Field(default_factory=list)
    expected_evidence: List[str] = Field(default_factory=list)
    
    # Automation
    is_automated: bool = False
    test_method: TestMethod = TestMethod.MANUAL_REVIEW
    automation_script: Optional[str] = None
    
    # Metadata
    references: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Asset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: AssetType
    description: str = ""
    
    # Technical details
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    version: Optional[str] = None
    location: Optional[str] = None
    
    # Business context
    owner: Optional[str] = None
    criticality: FindingSeverity = FindingSeverity.MEDIUM
    business_function: str = ""
    
    # Compliance scope
    in_scope_frameworks: List[AuditFramework] = Field(default_factory=list)
    data_classification: str = "internal"
    
    # Status
    is_active: bool = True
    last_audited: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AuditScope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Framework and controls
    frameworks: List[AuditFramework]
    control_ids: List[str] = Field(default_factory=list)  # Specific controls to audit
    
    # Assets in scope
    asset_ids: List[str] = Field(default_factory=list)
    asset_filters: Dict[str, Any] = Field(default_factory=dict)  # Dynamic asset selection
    
    # Exclusions
    excluded_assets: List[str] = Field(default_factory=list)
    excluded_controls: List[str] = Field(default_factory=list)
    exclusion_reason: str = ""
    
    # Timing
    audit_frequency: str = "annual"  # monthly, quarterly, annual
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: FindingSeverity
    status: FindingStatus = FindingStatus.OPEN
    
    # Context
    audit_id: str
    control_id: str
    asset_id: Optional[str] = None
    
    # Evidence
    evidence: List[str] = Field(default_factory=list)  # File paths, screenshots, logs
    test_method: TestMethod
    test_details: str = ""
    
    # Impact and risk
    business_impact: str = ""
    technical_impact: str = ""
    likelihood: str = "medium"  # low, medium, high
    risk_score: float = Field(ge=0.0, le=10.0, default=5.0)
    
    # Root cause analysis
    root_cause: str = ""
    contributing_factors: List[str] = Field(default_factory=list)
    
    # Remediation
    remediation_recommendation: str = ""
    remediation_effort: str = "medium"  # low, medium, high
    remediation_cost: Optional[float] = None
    remediation_timeline: Optional[str] = None
    
    # Assignment and tracking
    assigned_to: Optional[str] = None
    assigned_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Resolution
    resolution_details: str = ""
    resolved_by: Optional[str] = None
    resolved_date: Optional[datetime] = None
    verification_evidence: List[str] = Field(default_factory=list)
    
    # Compliance mapping
    regulatory_citations: List[str] = Field(default_factory=list)
    framework_mappings: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str

class Audit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: AuditType
    status: AuditStatus = AuditStatus.SCHEDULED
    
    # Scope
    scope_id: str
    frameworks: List[AuditFramework]
    
    # Planning
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    
    # Team
    lead_auditor: str
    audit_team: List[str] = Field(default_factory=list)
    
    # Configuration
    automated_tests_enabled: bool = True
    manual_review_required: bool = True
    sampling_methodology: str = "risk_based"
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.95)
    
    # Progress tracking
    controls_planned: int = 0
    controls_tested: int = 0
    controls_passed: int = 0
    controls_failed: int = 0
    
    # Findings
    findings_count: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    
    # Results
    overall_compliance_score: Optional[float] = None  # 0-100%
    framework_scores: Dict[str, float] = Field(default_factory=dict)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    
    # Documentation
    audit_report_path: Optional[str] = None
    executive_summary: str = ""
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str

class RemediationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Scope
    audit_id: str
    finding_ids: List[str] = Field(default_factory=list)
    
    # Planning
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    
    # Resources
    assigned_team: List[str] = Field(default_factory=list)
    project_manager: Optional[str] = None
    estimated_effort_hours: Optional[int] = None
    estimated_cost: Optional[float] = None
    
    # Status tracking
    status: RemediationStatus = RemediationStatus.NOT_STARTED
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    
    # Tasks
    remediation_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Risk management
    implementation_risks: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)
    
    # Validation
    acceptance_criteria: List[str] = Field(default_factory=list)
    verification_plan: str = ""
    
    # Communication
    stakeholders: List[str] = Field(default_factory=list)
    status_reports: List[Dict[str, Any]] = Field(default_factory=list)
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ComplianceSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    
    # Scope
    frameworks: List[AuditFramework]
    snapshot_date: datetime = Field(default_factory=datetime.now)
    
    # Compliance metrics
    total_controls: int = 0
    compliant_controls: int = 0
    non_compliant_controls: int = 0
    not_applicable_controls: int = 0
    overall_compliance_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    
    # Framework breakdown
    framework_compliance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Risk assessment
    total_findings: int = 0
    critical_risk_findings: int = 0
    high_risk_findings: int = 0
    medium_risk_findings: int = 0
    low_risk_findings: int = 0
    overall_risk_score: float = Field(ge=0.0, le=10.0, default=0.0)
    
    # Trends (compared to previous snapshot)
    compliance_trend: Optional[str] = None  # improving, stable, declining
    risk_trend: Optional[str] = None
    
    # Assets coverage
    total_assets: int = 0
    audited_assets: int = 0
    assets_with_findings: int = 0
    
    # Remediation status
    total_remediation_plans: int = 0
    active_remediation_plans: int = 0
    completed_remediation_plans: int = 0
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

# Modèles de requête
class CreateAuditRequest(BaseModel):
    name: str
    description: str
    type: AuditType
    scope_id: str
    frameworks: List[AuditFramework]
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    lead_auditor: str
    audit_team: List[str] = Field(default_factory=list)
    automated_tests_enabled: bool = True
    manual_review_required: bool = True
    created_by: str

class UpdateAuditRequest(BaseModel):
    status: Optional[AuditStatus] = None
    description: Optional[str] = None
    audit_team: Optional[List[str]] = None
    executive_summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    updated_by: str

class CreateAssetRequest(BaseModel):
    name: str
    type: AssetType
    description: str = ""
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    owner: Optional[str] = None
    criticality: FindingSeverity = FindingSeverity.MEDIUM
    in_scope_frameworks: List[AuditFramework] = Field(default_factory=list)

class CreateScopeRequest(BaseModel):
    name: str
    description: str
    frameworks: List[AuditFramework]
    control_ids: List[str] = Field(default_factory=list)
    asset_ids: List[str] = Field(default_factory=list)
    audit_frequency: str = "annual"
    created_by: str

class CreateFindingRequest(BaseModel):
    title: str
    description: str
    severity: FindingSeverity
    audit_id: str
    control_id: str
    asset_id: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    test_method: TestMethod
    business_impact: str = ""
    remediation_recommendation: str = ""
    created_by: str

class UpdateFindingRequest(BaseModel):
    status: Optional[FindingStatus] = None
    assigned_to: Optional[str] = None
    resolution_details: Optional[str] = None
    verification_evidence: Optional[List[str]] = None
    updated_by: str

class CreateRemediationPlanRequest(BaseModel):
    name: str
    description: str
    audit_id: str
    finding_ids: List[str]
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    assigned_team: List[str] = Field(default_factory=list)
    project_manager: Optional[str] = None
    created_by: str

class AuditSearchRequest(BaseModel):
    query: Optional[str] = None
    type: Optional[AuditType] = None
    status: Optional[List[AuditStatus]] = None
    frameworks: Optional[List[AuditFramework]] = None
    lead_auditor: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

class FindingSearchRequest(BaseModel):
    query: Optional[str] = None
    severity: Optional[List[FindingSeverity]] = None
    status: Optional[List[FindingStatus]] = None
    audit_id: Optional[str] = None
    control_id: Optional[str] = None
    assigned_to: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 50
    offset: int = 0

# Modèles de réponse
class AuditStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    active_audits: int
    total_findings: int
    frameworks_supported: int
    assets_monitored: int
    compliance_score: Optional[float] = None

class AuditStatistics(BaseModel):
    total_audits: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_framework: Dict[str, int]
    average_compliance_score: float
    total_findings: int
    findings_by_severity: Dict[str, int]
    remediation_rate: float
    audit_frequency_compliance: float

class FindingStatistics(BaseModel):
    total_findings: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    by_framework: Dict[str, int]
    avg_resolution_time_days: float
    open_critical_findings: int
    overdue_findings: int
    remediation_progress: Dict[str, int]

class ComplianceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    frameworks: List[AuditFramework]
    
    # Executive summary
    overall_compliance_score: float
    risk_level: str
    key_findings: List[str]
    recommendations: List[str]
    
    # Detailed results
    framework_results: Dict[str, Dict[str, Any]]
    control_results: List[Dict[str, Any]]
    asset_results: Dict[str, Dict[str, Any]]
    
    # Trends and analysis
    compliance_trends: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]
    
    # Action items
    priority_actions: List[Dict[str, Any]]
    remediation_roadmap: Dict[str, Any]
    
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str

class AuditInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    insight_type: str  # compliance_gap, risk_trend, efficiency_opportunity
    severity: FindingSeverity
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    data: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    affected_frameworks: List[AuditFramework] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)