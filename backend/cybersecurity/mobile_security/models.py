"""
Mobile Security Models
Modèles Pydantic pour l'analyse sécurité mobile
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class MobileAppRequest(BaseModel):
    """Requête d'analyse d'application mobile"""
    platform: str = Field(..., description="Platform: android|ios")
    source_type: str = Field(..., description="Source type: file|url")
    source: str = Field(..., description="Base64 content or URL")
    analysis_options: Dict[str, Any] = Field(default_factory=lambda: {
        "static_analysis": True,
        "dynamic_analysis": False,
        "frameworks": ["OWASP_MASVS", "NIST_Mobile"]
    })

class MobileVulnerability(BaseModel):
    """Vulnérabilité mobile détectée"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str = Field(..., description="Catégorie OWASP MASVS")
    severity: str = Field(..., description="Severity: critical|high|medium|low")
    title: str = Field(..., description="Titre de la vulnérabilité")
    description: str = Field(..., description="Description détaillée")
    cwe_id: Optional[str] = Field(None, description="CWE ID si applicable")
    owasp_category: str = Field(..., description="Catégorie OWASP Mobile Top 10")
    remediation: str = Field(..., description="Recommandations de remédiation")
    file_path: Optional[str] = Field(None, description="Fichier concerné")
    line_number: Optional[int] = Field(None, description="Ligne de code")
    confidence: float = Field(..., description="Niveau de confiance 0-1")

class MobileAnalysisResult(BaseModel):
    """Résultat d'analyse mobile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_id: str = Field(..., description="ID unique de l'application")
    platform: str = Field(..., description="Platform analysée")
    app_name: str = Field(..., description="Nom de l'application")
    app_version: Optional[str] = Field(None, description="Version de l'app")
    package_name: str = Field(..., description="Package/Bundle ID")
    status: str = Field(default="pending", description="Status: pending|running|completed|failed")
    
    # Métadonnées d'analyse
    analysis_type: List[str] = Field(default_factory=list, description="Types d'analyse effectués")
    frameworks_used: List[str] = Field(default_factory=list, description="Frameworks utilisés")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)
    
    # Résultats
    vulnerabilities: List[MobileVulnerability] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    compliance_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MobileSecurityMetrics(BaseModel):
    """Métriques Mobile Security"""
    total_analyses: int = 0
    analyses_by_platform: Dict[str, int] = Field(default_factory=dict)
    avg_vulnerabilities_per_app: float = 0.0
    most_common_vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_scores_avg: Dict[str, float] = Field(default_factory=dict)

class MobileSecurityStatus(BaseModel):
    """Status du service Mobile Security"""
    status: str = "operational"
    service: str = "Mobile Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "android_analysis": True,
        "ios_analysis": True,
        "static_analysis": True,
        "dynamic_analysis": False,
        "owasp_masvs": True,
        "nist_mobile": True,
        "automated_reporting": True
    })
    supported_platforms: List[str] = Field(default_factory=lambda: ["android", "ios"])
    supported_frameworks: List[str] = Field(default_factory=lambda: [
        "OWASP_MASVS", "NIST_Mobile", "SANS_Mobile"
    ])
    active_analyses: int = 0
    completed_analyses: int = 0
    metrics: Optional[MobileSecurityMetrics] = None