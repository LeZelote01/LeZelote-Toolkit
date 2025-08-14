"""
Modèles de données pour le service Incident Response
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class IncidentSeverity(str, Enum):
    """Niveaux de sévérité des incidents"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentStatus(str, Enum):
    """Statuts des incidents"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(str, Enum):
    """Catégories d'incidents"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    DDoS = "ddos"
    INSIDER_THREAT = "insider_threat"
    SYSTEM_COMPROMISE = "system_compromise"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RANSOMWARE = "ransomware"
    WEB_ATTACK = "web_attack"
    NETWORK_INTRUSION = "network_intrusion"
    OTHER = "other"


class Evidence(BaseModel):
    """Élément de preuve"""
    id: str
    type: str = Field(..., description="Type de preuve (log, fichier, capture réseau, etc.)")
    source: str = Field(..., description="Source de la preuve")
    collected_at: datetime = Field(default_factory=datetime.now)
    collected_by: str = Field(..., description="Personne qui a collecté la preuve")
    file_path: Optional[str] = None
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    description: str = Field(..., description="Description de la preuve")


class IncidentAction(BaseModel):
    """Action réalisée sur un incident"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: str = Field(..., description="Type d'action (investigation, containment, etc.)")
    performed_by: str = Field(..., description="Personne qui a effectué l'action")
    description: str = Field(..., description="Description détaillée de l'action")
    results: Optional[str] = None
    evidence_collected: List[str] = Field(default_factory=list, description="IDs des preuves collectées")


class ThreatIndicator(BaseModel):
    """Indicateur de compromission (IOC)"""
    id: str
    type: str = Field(..., description="Type d'indicateur (IP, domaine, hash, etc.)")
    value: str = Field(..., description="Valeur de l'indicateur")
    confidence: float = Field(..., ge=0, le=1, description="Niveau de confiance (0-1)")
    source: str = Field(..., description="Source de l'indicateur")
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class IncidentRequest(BaseModel):
    """Requête pour créer un incident"""
    title: str = Field(..., description="Titre de l'incident")
    description: str = Field(..., description="Description détaillée")
    category: IncidentCategory
    severity: IncidentSeverity
    affected_systems: List[str] = Field(default_factory=list)
    reporter: str = Field(..., description="Personne qui signale l'incident")
    source: str = Field(default="manual", description="Source de détection")
    initial_evidence: List[str] = Field(default_factory=list, description="Preuves initiales")


class Incident(BaseModel):
    """Modèle d'incident complet"""
    id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    
    # Informations temporelles
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    first_detected: Optional[datetime] = None
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Parties prenantes
    reporter: str
    assigned_to: Optional[str] = None
    team_members: List[str] = Field(default_factory=list)
    
    # Systèmes affectés
    affected_systems: List[str] = Field(default_factory=list)
    affected_users: List[str] = Field(default_factory=list)
    
    # Preuves et actions
    evidence: List[Evidence] = Field(default_factory=list)
    actions: List[IncidentAction] = Field(default_factory=list)
    threat_indicators: List[ThreatIndicator] = Field(default_factory=list)
    
    # Analyse
    root_cause: Optional[str] = None
    attack_vector: Optional[str] = None
    attacker_profile: Optional[str] = None
    
    # Impact
    impact_description: Optional[str] = None
    business_impact: Optional[str] = None
    data_compromised: bool = False
    
    # Métadonnées
    source: str = "manual"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentResponse(BaseModel):
    """Réponse d'une opération sur un incident"""
    incident_id: str
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class PlaybookStep(BaseModel):
    """Étape d'un playbook de réponse"""
    id: str
    title: str
    description: str
    category: str  # investigation, containment, eradication, recovery
    automated: bool = False
    script: Optional[str] = None
    estimated_duration: Optional[int] = None  # en minutes
    dependencies: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)


class IncidentPlaybook(BaseModel):
    """Playbook de réponse à incident"""
    id: str
    name: str
    description: str
    incident_types: List[IncidentCategory]
    severity_levels: List[IncidentSeverity]
    steps: List[PlaybookStep]
    estimated_total_duration: Optional[int] = None
    success_criteria: List[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)