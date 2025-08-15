"""
Modèles de données pour API Security
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class APIType(str, Enum):
    """Types d'API supportées"""
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    GRPC = "grpc"
    WEBHOOK = "webhook"

class TestType(str, Enum):
    """Types de tests de sécurité API"""
    OWASP_API_TOP10 = "owasp_api_top10"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INJECTION = "injection"
    RATE_LIMITING = "rate_limiting"
    DATA_VALIDATION = "data_validation"
    CORS = "cors"
    SSL_TLS = "ssl_tls"
    ERROR_HANDLING = "error_handling"
    LOGGING_MONITORING = "logging_monitoring"

class Severity(str, Enum):
    """Niveaux de sévérité"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class HTTPMethod(str, Enum):
    """Méthodes HTTP"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class APIEndpoint(BaseModel):
    """Endpoint API"""
    path: str
    method: HTTPMethod
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    authentication_required: bool = False
    rate_limited: bool = False
    deprecated: bool = False

class APISecurityRequest(BaseModel):
    """Requête de test de sécurité API"""
    base_url: str = Field(..., description="URL de base de l'API")
    api_type: APIType = APIType.REST
    
    # Documentation/découverte
    openapi_url: Optional[str] = Field(None, description="URL du fichier OpenAPI/Swagger")
    endpoints: List[APIEndpoint] = Field(default_factory=list, description="Endpoints à tester")
    
    # Authentification
    auth_method: Optional[str] = Field(None, description="Type d'authentification (bearer, basic, api_key)")
    auth_credentials: Dict[str, str] = Field(default_factory=dict, description="Credentials de test")
    
    # Configuration des tests
    test_suite: List[TestType] = Field(
        default_factory=lambda: [TestType.OWASP_API_TOP10, TestType.AUTHENTICATION]
    )
    
    # Options de test
    test_options: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timeout": 30,
            "max_requests": 100,
            "rate_limit_test": True,
            "deep_scan": False,
            "custom_payloads": []
        }
    )

class APIVulnerability(BaseModel):
    """Vulnérabilité API détectée"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    test_id: str
    endpoint_path: str
    method: HTTPMethod
    
    # Classification OWASP API
    owasp_category: Optional[str] = None  # API1:2023, API2:2023, etc.
    
    # Détails de la vulnérabilité
    title: str
    description: str
    severity: Severity
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = Field(None, ge=0, le=10)
    
    # Détails techniques
    test_type: TestType
    attack_vector: str
    impact: str
    likelihood: str
    
    # Preuves
    request_details: Dict[str, Any] = Field(default_factory=dict)
    response_details: Dict[str, Any] = Field(default_factory=dict)
    payload_used: Optional[str] = None
    
    # Remédiation  
    remediation: str
    remediation_steps: List[str] = Field(default_factory=list)
    
    # Métadonnées
    detected_at: datetime = Field(default_factory=datetime.now)
    confidence: int = Field(default=5, ge=1, le=10)
    false_positive_risk: str = Field(default="low")

class APISecurityMetrics(BaseModel):
    """Métriques de sécurité API"""
    security_score: float = Field(ge=0, le=100)
    authentication_score: float = Field(ge=0, le=100)
    authorization_score: float = Field(ge=0, le=100)
    data_protection_score: float = Field(ge=0, le=100)
    rate_limiting_score: float = Field(ge=0, le=100)
    
    # Tests OWASP API Security Top 10
    owasp_compliance: Dict[str, bool] = Field(default_factory=dict)
    
    # Statistiques
    total_endpoints_tested: int = 0
    vulnerable_endpoints: int = 0
    authenticated_endpoints: int = 0
    rate_limited_endpoints: int = 0
    
    # Analyse des réponses
    error_disclosure_count: int = 0
    information_leakage_count: int = 0
    insecure_direct_object_refs: int = 0

class APITestResult(BaseModel):
    """Résultat de test de sécurité API"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    api_type: APIType
    base_url: str
    status: str = "completed"
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration: float = 0.0  # en secondes
    
    # Endpoints testés
    endpoints_discovered: List[APIEndpoint] = Field(default_factory=list)
    endpoints_tested: List[APIEndpoint] = Field(default_factory=list)
    
    # Vulnérabilités
    vulnerabilities: List[APIVulnerability] = Field(default_factory=list)
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    
    # Métriques
    security_metrics: Optional[APISecurityMetrics] = None
    
    # Tests effectués
    tests_performed: List[TestType] = Field(default_factory=list)
    test_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Analyse technique
    api_documentation_found: bool = False
    authentication_methods: List[str] = Field(default_factory=list)
    rate_limiting_detected: bool = False
    cors_configuration: Dict[str, Any] = Field(default_factory=dict)
    ssl_configuration: Dict[str, Any] = Field(default_factory=dict)
    
    # Recommandations
    recommendations: List[str] = Field(default_factory=list)
    compliance_status: Dict[str, Any] = Field(default_factory=dict)
    
    # Données brutes
    raw_responses: List[Dict[str, Any]] = Field(default_factory=list)
    errors_encountered: List[str] = Field(default_factory=list)

class OWASPAPICategory(BaseModel):
    """Catégorie OWASP API Security Top 10"""
    category_id: str  # API1:2023, API2:2023, etc.
    name: str
    description: str
    tested: bool = False
    compliant: bool = False
    vulnerabilities_found: int = 0
    test_details: Dict[str, Any] = Field(default_factory=dict)

class APISecurityStatus(BaseModel):
    """Status du service API Security"""
    status: str = "operational"
    service: str = "API Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=dict)
    supported_api_types: List[APIType] = Field(default_factory=list)
    supported_tests: List[TestType] = Field(default_factory=list)
    active_tests: int = 0
    completed_tests: int = 0

class APIDiscoveryResult(BaseModel):
    """Résultat de découverte d'API"""
    base_url: str
    api_type: APIType
    endpoints_found: List[APIEndpoint] = Field(default_factory=list)
    documentation_urls: List[str] = Field(default_factory=list)
    authentication_methods: List[str] = Field(default_factory=list)
    version_info: Optional[str] = None
    server_info: Dict[str, str] = Field(default_factory=dict)
    cors_enabled: bool = False
    rate_limiting_detected: bool = False
    discovery_method: str = "manual"  # manual, openapi, crawl
    confidence: float = Field(default=0.5, ge=0, le=1)