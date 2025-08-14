"""
Modèles de données pour AI Security
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class AIModelType(str, Enum):
    """Types de modèles IA supportés"""
    LLM = "llm"
    IMAGE_CLASSIFICATION = "image_classification"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    DECISION_TREE = "decision_tree"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"

class TestType(str, Enum):
    """Types de tests de sécurité IA"""
    PROMPT_INJECTION = "prompt_injection"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    DATA_POISONING = "data_poisoning"
    MODEL_EXTRACTION = "model_extraction"
    BIAS_EVALUATION = "bias_evaluation"
    FAIRNESS_TESTING = "fairness_testing"
    ROBUSTNESS_TESTING = "robustness_testing"
    PRIVACY_LEAKAGE = "privacy_leakage"

class Severity(str, Enum):
    """Niveaux de sévérité"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AISecurityRequest(BaseModel):
    """Requête d'évaluation de sécurité IA"""
    model_type: AIModelType
    model_name: Optional[str] = Field(None, description="Nom du modèle")
    model_endpoint: Optional[str] = Field(None, description="URL endpoint du modèle")
    model_file: Optional[str] = Field(None, description="Chemin vers le fichier modèle")
    test_suite: List[TestType] = Field(default_factory=lambda: [TestType.PROMPT_INJECTION, TestType.BIAS_EVALUATION])
    
    # Configuration spécifique par test
    test_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Options d'évaluation
    evaluation_options: Dict[str, Any] = Field(
        default_factory=lambda: {
            "sample_size": 100,
            "timeout": 300,
            "parallel_tests": True,
            "detailed_analysis": True
        }
    )

class AIVulnerability(BaseModel):
    """Vulnérabilité IA détectée"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    evaluation_id: str
    test_type: TestType
    severity: Severity
    title: str
    description: str
    
    # Détails techniques
    attack_vector: str
    impact: str
    likelihood: str
    
    # Preuves
    evidence: Dict[str, Any] = Field(default_factory=dict)
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Métriques
    confidence_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    
    # Remédiation
    remediation: str
    mitigation_steps: List[str] = Field(default_factory=list)
    
    # Métadonnées
    detected_at: datetime = Field(default_factory=datetime.now)
    cwe_id: Optional[str] = None
    owasp_ml_category: Optional[str] = None

class BiasMetrics(BaseModel):
    """Métriques de biais"""
    demographic_parity: Optional[float] = None
    equal_opportunity: Optional[float] = None
    equalized_odds: Optional[float] = None
    individual_fairness: Optional[float] = None
    group_fairness: Optional[float] = None
    
    # Groupes analysés
    protected_attributes: List[str] = Field(default_factory=list)
    bias_score: float = Field(ge=0, le=100)
    fairness_score: float = Field(ge=0, le=100)

class RobustnessMetrics(BaseModel):
    """Métriques de robustesse"""
    adversarial_accuracy: float = Field(ge=0, le=100)
    clean_accuracy: float = Field(ge=0, le=100)
    robustness_score: float = Field(ge=0, le=100)
    
    # Tests d'attaque
    fgsm_success_rate: Optional[float] = None
    pgd_success_rate: Optional[float] = None
    carlini_wagner_success_rate: Optional[float] = None
    
    # Métriques de perturbation
    avg_perturbation_l2: Optional[float] = None
    avg_perturbation_linf: Optional[float] = None

class PrivacyMetrics(BaseModel):
    """Métriques de confidentialité"""
    membership_inference_accuracy: Optional[float] = None
    model_inversion_risk: Optional[float] = None
    attribute_inference_risk: Optional[float] = None
    
    privacy_score: float = Field(ge=0, le=100)
    data_leakage_risk: str = Field(default="low")

class AISecurityEvaluation(BaseModel):
    """Résultat d'évaluation de sécurité IA"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    model_type: AIModelType
    model_name: Optional[str] = None
    status: str = "completed"
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration: float = 0.0  # en secondes
    
    # Résultats globaux
    security_score: float = Field(ge=0, le=100)
    robustness_score: float = Field(ge=0, le=100)
    fairness_score: float = Field(ge=0, le=100)
    privacy_score: float = Field(ge=0, le=100)
    
    # Vulnérabilités
    vulnerabilities: List[AIVulnerability] = Field(default_factory=list)
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    
    # Métriques détaillées
    bias_metrics: Optional[BiasMetrics] = None
    robustness_metrics: Optional[RobustnessMetrics] = None
    privacy_metrics: Optional[PrivacyMetrics] = None
    
    # Tests effectués
    tests_performed: List[TestType] = Field(default_factory=list)
    test_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Recommandations
    recommendations: List[str] = Field(default_factory=list)
    mitigation_priority: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Conformité
    ml_security_standards: Dict[str, bool] = Field(default_factory=dict)
    compliance_frameworks: List[str] = Field(default_factory=list)

class AISecurityStatus(BaseModel):
    """Status du service AI Security"""
    status: str = "operational"
    service: str = "AI Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=dict)
    supported_models: List[AIModelType] = Field(default_factory=list)
    supported_tests: List[TestType] = Field(default_factory=list)
    active_evaluations: int = 0
    completed_evaluations: int = 0

class AISecurityMetrics(BaseModel):
    """Métriques globales AI Security"""
    total_evaluations: int = 0
    total_models_tested: int = 0
    vulnerabilities_found: int = 0
    avg_security_score: float = 0.0
    avg_robustness_score: float = 0.0
    avg_fairness_score: float = 0.0
    test_type_stats: Dict[TestType, int] = Field(default_factory=dict)
    model_type_stats: Dict[AIModelType, int] = Field(default_factory=dict)
    severity_stats: Dict[Severity, int] = Field(default_factory=dict)