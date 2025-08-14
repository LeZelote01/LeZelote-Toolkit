# Models pour le service Cloud Security
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CloudProvider(str, Enum):
    """Fournisseurs cloud supportés"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi"

class SeverityLevel(str, Enum):
    """Niveaux de sévérité des findings"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingStatus(str, Enum):
    """Statut des findings"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"

class CloudAuditRequest(BaseModel):
    """Requête d'audit cloud"""
    provider: CloudProvider = Field(..., description="Fournisseur cloud")
    account_id: str = Field(..., description="ID du compte cloud")
    scope: Optional[List[str]] = Field(default_factory=list, description="Services/ressources à auditer")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Options avancées")

class CloudFinding(BaseModel):
    """Finding de sécurité cloud"""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    status: FindingStatus = FindingStatus.OPEN
    service: str
    resource_type: str
    resource_id: str
    region: Optional[str] = None
    compliance_frameworks: List[str] = Field(default_factory=list)
    remediation: str
    impact: str
    references: List[str] = Field(default_factory=list)
    detected_at: datetime
    
class CloudAuditResult(BaseModel):
    """Résultat d'audit cloud"""
    audit_id: str
    provider: CloudProvider
    account_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    findings: List[CloudFinding] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict)
    compliance_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CloudConfigCheck(BaseModel):
    """Vérification de configuration cloud"""
    check_id: str
    name: str
    description: str
    category: str
    severity: SeverityLevel
    compliance_frameworks: List[str]
    remediation_guide: str
    
class CloudServiceConfig(BaseModel):
    """Configuration d'un service cloud"""
    service_name: str
    provider: CloudProvider
    enabled_checks: List[str]
    custom_rules: Optional[Dict[str, Any]] = None