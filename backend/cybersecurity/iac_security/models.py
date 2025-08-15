"""
IaC Security Module - Models
Modèles de données pour l'audit sécurité Infrastructure as Code
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class IaCSecurityScanRequest(BaseModel):
    source_type: str  # git_repo, file_upload, text
    source_content: str  # URL du repo, contenu du fichier, ou texte
    iac_type: str  # terraform, cloudformation, ansible, kubernetes
    scan_options: Optional[Dict[str, Any]] = None

class IaCSecurityScanResponse(BaseModel):
    scan_id: str
    status: str
    created_at: str
    source_type: str
    iac_type: str

class SecurityFinding(BaseModel):
    rule_id: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    resource_type: str
    remediation: str
    compliance_frameworks: List[str] = []

class ComplianceRule(BaseModel):
    rule_id: str
    name: str
    description: str
    severity: str
    category: str  # security, compliance, best_practices
    frameworks: List[str]  # CIS, NIST, PCI-DSS, etc.
    iac_types: List[str]  # terraform, cloudformation, etc.

class ScanResult(BaseModel):
    scan_id: str
    status: str  # scanning, completed, failed
    source_type: str
    iac_type: str
    created_at: str
    completed_at: Optional[str] = None
    total_resources: int = 0
    findings: List[SecurityFinding] = []
    summary: Dict[str, int] = {}  # severity counts
    compliance_score: float = 0.0
    recommendations: List[str] = []

class IaCResource(BaseModel):
    resource_type: str
    resource_name: str
    file_path: str
    line_number: Optional[int] = None
    configuration: Dict[str, Any] = {}
    security_issues: List[SecurityFinding] = []