"""
Modèles de données pour le service Digital Forensics
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class EvidenceType(str, Enum):
    """Types d'éléments de preuve"""
    DISK_IMAGE = "disk_image"
    MEMORY_DUMP = "memory_dump"
    NETWORK_CAPTURE = "network_capture"
    LOG_FILE = "log_file"
    EMAIL_MESSAGE = "email_message"
    DOCUMENT = "document"
    DATABASE_RECORD = "database_record"
    MOBILE_BACKUP = "mobile_backup"
    REGISTRY_HIVE = "registry_hive"
    BROWSER_ARTIFACT = "browser_artifact"
    METADATA = "metadata"
    OTHER = "other"


class HashAlgorithm(str, Enum):
    """Algorithmes de hachage supportés"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


class AnalysisStatus(str, Enum):
    """Statuts d'analyse"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ForensicsCase(BaseModel):
    """Dossier d'enquête forensique"""
    id: str
    case_number: str = Field(..., description="Numéro officiel du dossier")
    title: str = Field(..., description="Titre du dossier")
    description: str = Field(..., description="Description du dossier")
    
    # Métadonnées du dossier
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(..., description="Investigateur principal")
    assigned_to: List[str] = Field(default_factory=list, description="Équipe assignée")
    
    # Information légale
    incident_id: Optional[str] = None
    client: str = Field(..., description="Client ou organisation")
    case_type: str = Field(..., description="Type d'affaire")
    priority: str = Field(default="medium", description="Priorité du dossier")
    
    # Chaîne de custody
    custody_chain: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statut
    status: str = Field(default="active", description="Statut du dossier")
    
    # Métadonnées
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DigitalEvidence(BaseModel):
    """Élément de preuve numérique"""
    id: str
    case_id: str = Field(..., description="ID du dossier parent")
    
    # Identification
    name: str = Field(..., description="Nom de la preuve")
    description: str = Field(..., description="Description détaillée")
    evidence_type: EvidenceType
    source: str = Field(..., description="Source de la preuve")
    
    # Informations techniques
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Hachages pour intégrité
    hashes: Dict[HashAlgorithm, str] = Field(default_factory=dict)
    
    # Métadonnées temporelles
    acquired_at: datetime = Field(default_factory=datetime.now)
    acquired_by: str = Field(..., description="Personne qui a acquis la preuve")
    original_timestamp: Optional[datetime] = None
    
    # Chaîne de custody
    custody_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analyse
    analyzed: bool = False
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Tags et métadonnées
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisTask(BaseModel):
    """Tâche d'analyse forensique"""
    id: str
    case_id: str
    evidence_id: str
    
    # Détails de la tâche
    task_type: str = Field(..., description="Type d'analyse")
    description: str = Field(..., description="Description de l'analyse")
    
    # Statut et progression
    status: AnalysisStatus
    progress: float = Field(default=0.0, ge=0, le=1, description="Progression (0-1)")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # en minutes
    
    # Configuration
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Résultats
    results: Dict[str, Any] = Field(default_factory=dict)
    artifacts_found: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    
    # Assignation
    assigned_to: str = Field(..., description="Analyste assigné")


class ForensicsArtifact(BaseModel):
    """Artifact forensique découvert"""
    id: str
    case_id: str
    evidence_id: str
    analysis_task_id: str
    
    # Détails de l'artifact
    artifact_type: str = Field(..., description="Type d'artifact")
    name: str = Field(..., description="Nom de l'artifact")
    description: str = Field(..., description="Description")
    
    # Localisation
    source_path: str = Field(..., description="Chemin dans la source")
    extraction_path: Optional[str] = None
    
    # Métadonnées temporelles
    created_timestamp: Optional[datetime] = None
    modified_timestamp: Optional[datetime] = None
    accessed_timestamp: Optional[datetime] = None
    
    # Contenu
    content_preview: Optional[str] = None
    content_hash: Optional[str] = None
    file_size: Optional[int] = None
    
    # Importance
    significance: str = Field(default="medium", description="Importance de l'artifact")
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    
    # Tags et catégories
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Relations
    related_artifacts: List[str] = Field(default_factory=list)
    
    # Métadonnées
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineEvent(BaseModel):
    """Événement de la timeline forensique"""
    id: str
    case_id: str
    
    # Détails de l'événement
    timestamp: datetime
    event_type: str = Field(..., description="Type d'événement")
    source: str = Field(..., description="Source de l'événement")
    description: str = Field(..., description="Description détaillée")
    
    # Localisation
    system: str = Field(..., description="Système source")
    user: Optional[str] = None
    process: Optional[str] = None
    
    # Artifacts liés
    artifact_id: Optional[str] = None
    evidence_id: str
    
    # Importance
    significance: str = Field(default="medium")
    confidence: float = Field(default=0.5, ge=0, le=1)
    
    # Métadonnées
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ForensicsReport(BaseModel):
    """Rapport d'analyse forensique"""
    id: str
    case_id: str
    
    # Détails du rapport
    title: str = Field(..., description="Titre du rapport")
    summary: str = Field(..., description="Résumé exécutif")
    
    # Métadonnées
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(..., description="Analyste qui a généré le rapport")
    version: str = Field(default="1.0")
    
    # Contenu
    executive_summary: str
    methodology: str
    key_findings: List[str] = Field(default_factory=list)
    timeline_summary: List[Dict[str, Any]] = Field(default_factory=list)
    technical_details: Dict[str, Any] = Field(default_factory=dict)
    conclusions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Annexes
    evidence_list: List[Dict[str, Any]] = Field(default_factory=list)
    artifact_summary: List[Dict[str, Any]] = Field(default_factory=list)
    technical_appendix: Dict[str, Any] = Field(default_factory=dict)
    
    # Certification
    chain_of_custody_verified: bool = False
    integrity_verified: bool = False
    examiner_certification: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Requête d'analyse forensique"""
    case_id: str
    evidence_id: str
    analysis_types: List[str] = Field(..., description="Types d'analyses à effectuer")
    priority: str = Field(default="medium")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    assigned_to: str = Field(..., description="Analyste assigné")
    notes: Optional[str] = None


class ForensicsSearchRequest(BaseModel):
    """Requête de recherche dans les preuves"""
    case_id: str
    evidence_ids: List[str] = Field(default_factory=list, description="IDs des preuves à chercher")
    search_terms: List[str] = Field(..., description="Termes de recherche")
    search_type: str = Field(default="keyword", description="Type de recherche")
    file_types: List[str] = Field(default_factory=list, description="Types de fichiers à inclure")
    date_range: Optional[Dict[str, datetime]] = None
    case_sensitive: bool = False
    regex_enabled: bool = False


class CustodyTransfer(BaseModel):
    """Transfert de custody d'une preuve"""
    evidence_id: str
    from_person: str = Field(..., description="Personne qui transfère")
    to_person: str = Field(..., description="Personne qui reçoit")
    transfer_reason: str = Field(..., description="Raison du transfert")
    location: str = Field(..., description="Lieu du transfert")
    transfer_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    witness: Optional[str] = None