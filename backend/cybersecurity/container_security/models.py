"""
Container Security Module - Models
Modèles de données pour la sécurité des conteneurs
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class ScanType(str, Enum):
    VULNERABILITY = "vulnerability"
    CONFIGURATION = "configuration"
    RUNTIME = "runtime"
    COMPLIANCE = "compliance"

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContainerVulnerability(BaseModel):
    """Modèle de vulnérabilité conteneur"""
    cve_id: str
    severity: SeverityLevel
    package: str
    installed_version: str
    fixed_version: Optional[str] = None
    description: str
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    references: List[str] = []
    published_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None

class ImageInfo(BaseModel):
    """Informations sur l'image conteneur"""
    name: str
    tag: str
    digest: Optional[str] = None
    size: str
    layers: int
    base_image: Optional[str] = None
    architecture: str = "amd64"
    os: str = "linux"
    created: Optional[datetime] = None
    author: Optional[str] = None
    labels: Dict[str, str] = {}

class ComplianceCheck(BaseModel):
    """Résultat de vérification de conformité"""
    standard: str  # CIS Docker, NIST, etc.
    rule_id: str
    rule_name: str
    status: str  # passed, failed, warning
    severity: SeverityLevel
    description: str
    remediation: Optional[str] = None

class SecretFound(BaseModel):
    """Secret détecté dans l'image"""
    type: str  # API Key, Password, Certificate, etc.
    location: str  # Chemin du fichier
    severity: SeverityLevel
    pattern: str
    confidence: float  # 0.0 à 1.0
    context: Optional[str] = None

class ContainerScan(BaseModel):
    """Modèle complet de scan conteneur"""
    scan_id: str
    status: ScanStatus
    scan_type: ScanType
    image_info: ImageInfo
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scan_duration: Optional[str] = None
    
    # Résultats
    vulnerabilities: List[ContainerVulnerability] = []
    compliance_checks: List[ComplianceCheck] = []
    secrets_found: List[SecretFound] = []
    
    # Statistiques
    total_vulnerabilities: int = 0
    severity_breakdown: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "negligible": 0
    }
    
    # Recommandations
    hardening_recommendations: List[str] = []
    compliance_score: Optional[float] = None
    
    # Métadonnées
    scanner_version: Optional[str] = None
    database_version: Optional[str] = None
    scan_options: Dict[str, Any] = {}
    error_message: Optional[str] = None

class ScanSummary(BaseModel):
    """Résumé des scans pour dashboard"""
    total_scans: int
    completed_scans: int
    failed_scans: int
    total_images: int
    total_vulnerabilities: int
    avg_vulnerabilities_per_image: float
    most_vulnerable_images: List[Dict[str, Any]]
    common_vulnerabilities: List[Dict[str, Any]]
    severity_distribution: Dict[str, int]
    scan_trends: List[Dict[str, Any]]  # Évolution dans le temps

class RegistryCredentials(BaseModel):
    """Credentials pour registre de conteneurs"""
    registry_url: str
    username: str
    password: str
    token: Optional[str] = None
    auth_type: str = "basic"  # basic, token, oauth

class ScanConfiguration(BaseModel):
    """Configuration de scan"""
    enable_secrets_detection: bool = True
    enable_compliance_checks: bool = True
    enable_malware_scan: bool = False
    max_scan_time: int = 300  # secondes
    vulnerability_databases: List[str] = ["NVD", "CVE", "GHSA"]
    compliance_standards: List[str] = ["CIS Docker"]
    exclude_packages: List[str] = []
    exclude_severity: List[SeverityLevel] = []