"""
Modèles de données pour le service Compliance
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum


class ComplianceFramework(str, Enum):
    """Frameworks de conformité supportés"""
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOX = "sox"
    COBIT = "cobit"
    COSO = "coso"
    ITIL = "itil"


class ComplianceStatus(str, Enum):
    """Statuts de conformité"""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"
    IN_PROGRESS = "in_progress"
    REMEDIATION_REQUIRED = "remediation_required"


class AssessmentType(str, Enum):
    """Types d'évaluation"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    SELF_ASSESSMENT = "self_assessment"
    THIRD_PARTY = "third_party"
    CERTIFICATION = "certification"
    SURVEILLANCE = "surveillance"


class ControlCategory(str, Enum):
    """Catégories de contrôles"""
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"
    PHYSICAL = "physical"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class ComplianceControl(BaseModel):
    """Contrôle de conformité"""
    id: str
    framework: ComplianceFramework
    control_id: str = Field(..., description="ID du contrôle dans le framework")
    title: str = Field(..., description="Titre du contrôle")
    description: str = Field(..., description="Description détaillée")
    
    # Catégorisation
    category: ControlCategory
    domain: str = Field(..., description="Domaine du framework")
    subcategory: Optional[str] = None
    
    # Statut
    status: ComplianceStatus
    compliance_score: float = Field(default=0.0, ge=0, le=1, description="Score de conformité (0-1)")
    
    # Évaluation
    last_assessment_date: Optional[date] = None
    next_assessment_due: Optional[date] = None
    assessor: Optional[str] = None
    
    # Détails d'implémentation
    implementation_status: str = Field(default="not_implemented")
    implementation_details: Optional[str] = None
    evidence_provided: List[str] = Field(default_factory=list)
    
    # Lacunes et remédiation
    gaps_identified: List[str] = Field(default_factory=list)
    remediation_actions: List[str] = Field(default_factory=list)
    remediation_priority: RiskLevel = Field(default=RiskLevel.MEDIUM)
    remediation_deadline: Optional[date] = None
    
    # Métadonnées
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ComplianceAssessment(BaseModel):
    """Évaluation de conformité"""
    id: str
    name: str = Field(..., description="Nom de l'évaluation")
    description: str = Field(..., description="Description de l'évaluation")
    
    # Configuration
    frameworks: List[ComplianceFramework] = Field(..., description="Frameworks évalués")
    assessment_type: AssessmentType
    scope: str = Field(..., description="Périmètre de l'évaluation")
    
    # Timing
    start_date: date
    end_date: Optional[date] = None
    planned_completion: date
    
    # Équipe
    lead_assessor: str = Field(..., description="Évaluateur principal")
    assessment_team: List[str] = Field(default_factory=list)
    
    # Progression
    status: str = Field(default="planning", description="Statut de l'évaluation")
    progress_percentage: float = Field(default=0.0, ge=0, le=1)
    
    # Résultats
    controls_assessed: List[str] = Field(default_factory=list, description="IDs des contrôles évalués")
    overall_score: Optional[float] = None
    compliance_percentage: Optional[float] = None
    
    # Rapports
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ComplianceGap(BaseModel):
    """Lacune de conformité"""
    id: str
    control_id: str = Field(..., description="ID du contrôle concerné")
    framework: ComplianceFramework
    
    # Description de la lacune
    title: str = Field(..., description="Titre de la lacune")
    description: str = Field(..., description="Description détaillée")
    gap_type: str = Field(..., description="Type de lacune")
    
    # Évaluation du risque
    risk_level: RiskLevel
    impact_description: str = Field(..., description="Description de l'impact")
    likelihood: str = Field(..., description="Probabilité d'occurrence")
    
    # Remédiation
    remediation_plan: str = Field(..., description="Plan de remédiation")
    estimated_effort: Optional[str] = None
    estimated_cost: Optional[float] = None
    target_resolution_date: Optional[date] = None
    
    # Assignation
    assigned_to: str = Field(..., description="Responsable de la remédiation")
    priority: str = Field(default="medium")
    
    # Suivi
    status: str = Field(default="open")
    progress_notes: List[str] = Field(default_factory=list)
    
    # Métadonnées
    identified_date: date = Field(default_factory=date.today)
    identified_by: str = Field(..., description="Personne qui a identifié la lacune")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ComplianceReport(BaseModel):
    """Rapport de conformité"""
    id: str
    assessment_id: str
    
    # Métadonnées du rapport
    title: str = Field(..., description="Titre du rapport")
    executive_summary: str = Field(..., description="Résumé exécutif")
    
    # Période couverte
    reporting_period_start: date
    reporting_period_end: date
    
    # Résultats globaux
    overall_compliance_score: float = Field(..., ge=0, le=1)
    frameworks_assessed: List[str] = Field(default_factory=list)
    
    # Détails par framework
    framework_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Contrôles
    total_controls: int
    compliant_controls: int
    partially_compliant_controls: int
    non_compliant_controls: int
    
    # Lacunes et recommandations
    critical_gaps: List[str] = Field(default_factory=list)
    high_priority_gaps: List[str] = Field(default_factory=list)
    key_recommendations: List[str] = Field(default_factory=list)
    
    # Plan d'action
    remediation_timeline: Dict[str, List[str]] = Field(default_factory=dict)
    resource_requirements: Optional[str] = None
    
    # Génération
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(..., description="Personne qui a généré le rapport")
    version: str = Field(default="1.0")
    
    # Approbation
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None


class AuditEvidence(BaseModel):
    """Preuve d'audit pour la conformité"""
    id: str
    control_id: str = Field(..., description="Contrôle associé")
    
    # Type et description
    evidence_type: str = Field(..., description="Type de preuve")
    title: str = Field(..., description="Titre de la preuve")
    description: str = Field(..., description="Description détaillée")
    
    # Fichiers
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Métadonnées
    collected_by: str = Field(..., description="Collecteur de la preuve")
    collection_date: date = Field(default_factory=date.today)
    valid_until: Optional[date] = None
    
    # Classification
    sensitivity_level: str = Field(default="internal")
    tags: List[str] = Field(default_factory=list)
    
    # Validation
    validated: bool = False
    validator: Optional[str] = None
    validation_date: Optional[date] = None
    validation_notes: Optional[str] = None


class ComplianceRequest(BaseModel):
    """Requête d'évaluation de conformité"""
    name: str = Field(..., description="Nom de l'évaluation")
    frameworks: List[ComplianceFramework] = Field(..., description="Frameworks à évaluer")
    assessment_type: AssessmentType
    scope: str = Field(..., description="Périmètre")
    lead_assessor: str = Field(..., description="Évaluateur principal")
    planned_start: date
    planned_completion: date
    priority: str = Field(default="medium")
    notes: Optional[str] = None


class RemediationAction(BaseModel):
    """Action de remédiation"""
    id: str
    gap_id: str = Field(..., description="ID de la lacune")
    
    # Description
    title: str = Field(..., description="Titre de l'action")
    description: str = Field(..., description="Description détaillée")
    action_type: str = Field(..., description="Type d'action")
    
    # Planning
    start_date: date
    target_completion_date: date
    actual_completion_date: Optional[date] = None
    
    # Ressources
    assigned_to: str = Field(..., description="Responsable")
    estimated_hours: Optional[int] = None
    estimated_cost: Optional[float] = None
    
    # Suivi
    status: str = Field(default="planned")
    progress_percentage: float = Field(default=0.0, ge=0, le=1)
    progress_notes: List[str] = Field(default_factory=list)
    
    # Validation
    completion_criteria: List[str] = Field(default_factory=list)
    verification_method: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[date] = None
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ComplianceMetric(BaseModel):
    """Métrique de conformité"""
    id: str
    name: str = Field(..., description="Nom de la métrique")
    description: str = Field(..., description="Description")
    framework: ComplianceFramework
    
    # Valeurs
    current_value: float
    target_value: float
    unit: str = Field(..., description="Unité de mesure")
    
    # Période
    measurement_date: date = Field(default_factory=date.today)
    measurement_frequency: str = Field(..., description="Fréquence de mesure")
    
    # Évaluation
    performance_status: str = Field(..., description="Statut de performance")
    trend: str = Field(..., description="Tendance")
    
    # Métadonnées
    measured_by: str = Field(..., description="Personne qui a mesuré")
    notes: Optional[str] = None


class PolicyDocument(BaseModel):
    """Document de politique/procédure"""
    id: str
    title: str = Field(..., description="Titre du document")
    document_type: str = Field(..., description="Type de document")
    
    # Contenu
    description: str = Field(..., description="Description")
    content: Optional[str] = None
    file_path: Optional[str] = None
    
    # Versioning
    version: str = Field(default="1.0")
    effective_date: date
    review_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Approbation
    author: str = Field(..., description="Auteur")
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    approval_date: Optional[date] = None
    
    # Classification
    classification: str = Field(default="internal")
    applicable_frameworks: List[ComplianceFramework] = Field(default_factory=list)
    related_controls: List[str] = Field(default_factory=list)
    
    # Statut
    status: str = Field(default="draft")
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)