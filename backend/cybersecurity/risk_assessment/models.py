"""
Risk Assessment Module - Models
Modèles de données pour l'évaluation et la gestion des risques cybersécurité
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LikelihoodLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ImpactLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class AssessmentType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    FOCUSED = "focused"
    RAPID = "rapid"
    REGULATORY = "regulatory"

class RiskCategory(str, Enum):
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    REPUTATIONAL = "reputational"

class ThreatActorType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    NATION_STATE = "nation_state"
    CYBERCRIMINAL = "cybercriminal"
    HACKTIVIST = "hacktivist"
    INSIDER = "insider"

class RiskAssessmentRequest(BaseModel):
    assessment_name: str
    scope: str  # organization, department, project, asset
    target_identifier: str  # nom du département, projet, etc.
    assessment_type: AssessmentType
    frameworks: List[str] = ["NIST", "ISO27001"]  # frameworks à utiliser
    include_threat_modeling: bool = True
    include_vulnerability_scan: bool = True

class Asset(BaseModel):
    asset_id: str
    name: str
    type: str  # server, workstation, database, application, network_device
    category: str  # hardware, software, data, people, facilities
    value: int  # 1-5 scale
    criticality: str  # low, medium, high, critical
    location: Optional[str] = None
    owner: Optional[str] = None
    dependencies: List[str] = []  # asset_ids this asset depends on
    vulnerabilities: List[str] = []

class ThreatActor(BaseModel):
    actor_id: str
    name: str
    type: ThreatActorType
    sophistication: str  # low, medium, high, very_high
    motivation: List[str]
    capabilities: List[str]
    target_preferences: List[str]
    active: bool = True

class Threat(BaseModel):
    threat_id: str
    name: str
    description: str
    category: str  # malware, phishing, ddos, insider, physical
    threat_actors: List[str]  # threat_actor_ids
    attack_vectors: List[str]
    targeted_assets: List[str]  # asset_ids
    likelihood: LikelihoodLevel
    impact_types: List[str]  # confidentiality, integrity, availability

class Vulnerability(BaseModel):
    vulnerability_id: str
    name: str
    description: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    severity: str  # low, medium, high, critical
    affected_assets: List[str]  # asset_ids
    exploit_available: bool = False
    patch_available: bool = False
    remediation_effort: str  # low, medium, high

class RiskItem(BaseModel):
    risk_id: str
    title: str
    description: str
    category: RiskCategory
    threat_id: str
    vulnerability_id: Optional[str] = None
    affected_assets: List[str]
    likelihood: LikelihoodLevel
    impact: ImpactLevel
    risk_score: float
    risk_level: RiskLevel
    existing_controls: List[str] = []
    control_effectiveness: str = "medium"  # low, medium, high
    residual_risk_score: float
    residual_risk_level: RiskLevel

class RiskTreatmentOption(BaseModel):
    option_id: str
    risk_id: str
    treatment_type: str  # accept, mitigate, transfer, avoid
    description: str
    implementation_cost: int  # 1-5 scale
    implementation_time: str  # days, weeks, months
    effectiveness: str  # low, medium, high
    priority: int  # 1-5 scale
    recommended: bool = False

class RiskAssessmentResult(BaseModel):
    assessment_id: str
    assessment_name: str
    scope: str
    target_identifier: str
    assessment_type: AssessmentType
    status: str  # in_progress, completed, failed
    created_at: str
    completed_at: Optional[str] = None
    frameworks_used: List[str]
    total_assets: int
    total_threats: int
    total_vulnerabilities: int
    total_risks: int
    risk_summary: Dict[str, int]  # counts by risk level
    overall_risk_score: float
    overall_risk_level: RiskLevel
    assets: List[Asset]
    threats: List[ThreatActor]
    vulnerabilities: List[Vulnerability]
    risks: List[RiskItem]
    treatment_options: List[RiskTreatmentOption]
    recommendations: List[str]

class RiskRegister(BaseModel):
    register_id: str
    organization: str
    created_at: str
    updated_at: str
    risks: List[RiskItem]
    treatment_plans: List[RiskTreatmentOption]
    total_risks: int
    accepted_risks: int
    mitigated_risks: int
    residual_risk_score: float

class ComplianceFramework(BaseModel):
    framework_id: str
    name: str
    description: str
    version: str
    controls: List[Dict[str, Any]]
    risk_categories: List[str]
    assessment_criteria: Dict[str, Any]

class RiskMatrix(BaseModel):
    matrix_id: str
    name: str
    likelihood_levels: List[Dict[str, Any]]
    impact_levels: List[Dict[str, Any]]
    risk_scoring: Dict[str, Dict[str, float]]  # likelihood -> impact -> score
    risk_thresholds: Dict[str, float]  # risk_level -> threshold

class RiskMetrics(BaseModel):
    total_assessments: int
    active_risks: int
    high_critical_risks: int
    average_risk_score: float
    risk_trend: str  # increasing, stable, decreasing
    compliance_score: float
    treatment_effectiveness: float
    assessment_frequency: str