"""
Modèles de données pour le service Threat Intelligence
CyberSec Toolkit Pro 2025 - PORTABLE
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

# Enums pour la typologie
class IOCType(str, Enum):
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL_ADDRESS = "email_address"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    USER_AGENT = "user_agent"
    SSL_CERTIFICATE = "ssl_certificate"
    ASN = "asn"

class ThreatType(str, Enum):
    MALWARE = "malware"
    APT = "apt"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    C2_INFRASTRUCTURE = "c2_infrastructure"
    EXPLOIT_KIT = "exploit_kit"
    TROJAN = "trojan"
    BACKDOOR = "backdoor"
    SPYWARE = "spyware"

class ThreatSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IOCConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class TLPClassification(str, Enum):
    RED = "red"
    AMBER = "amber"
    GREEN = "green"
    WHITE = "white"

class CTIFeedStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

# Modèles de base
class IOC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    value: str
    type: IOCType
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: IOCConfidence
    tlp: TLPClassification = TLPClassification.AMBER
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    false_positive: bool = False
    
    # Attribution
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    malware_family: Optional[str] = None
    
    # Contexte
    description: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
    # Méta-données
    source: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Géolocalisation
    geolocation: Optional[Dict[str, Any]] = None
    
    # Détection
    detection_count: int = 0
    last_detection: Optional[datetime] = None

class ThreatActor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    aliases: List[str] = Field(default_factory=list)
    description: str
    motivation: List[str] = Field(default_factory=list)  # financial, espionage, hacktivism, etc.
    sophistication: str  # novice, practitioner, expert, innovator
    resource_level: str  # individual, team, organization, government
    
    # Attribution
    country: Optional[str] = None
    region: Optional[str] = None
    
    # TTPs (Tactics, Techniques, Procedures)
    ttps: List[str] = Field(default_factory=list)
    attack_patterns: List[str] = Field(default_factory=list)
    
    # Targets
    target_sectors: List[str] = Field(default_factory=list)
    target_countries: List[str] = Field(default_factory=list)
    
    # Historique
    first_seen: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    
    # Relations
    campaigns: List[str] = Field(default_factory=list)
    malware_used: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    
    # Méta-données
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    confidence: IOCConfidence = IOCConfidence.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    aliases: List[str] = Field(default_factory=list)
    description: str
    objective: str
    
    # Attribution
    threat_actors: List[str] = Field(default_factory=list)
    
    # Timeline
    first_seen: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
    # TTPs
    attack_patterns: List[str] = Field(default_factory=list)
    malware_families: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    
    # Targets
    target_sectors: List[str] = Field(default_factory=list)
    target_countries: List[str] = Field(default_factory=list)
    victim_count: int = 0
    
    # IOCs associés
    associated_iocs: List[str] = Field(default_factory=list)
    
    # Méta-données
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    confidence: IOCConfidence = IOCConfidence.MEDIUM
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CTIFeed(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    provider: str
    feed_url: str
    feed_type: str  # json, xml, csv, stix, misp, etc.
    auth_required: bool = False
    api_key: Optional[str] = None
    
    # Configuration
    update_frequency: int = 3600  # secondes
    enabled: bool = True
    status: CTIFeedStatus = CTIFeedStatus.PENDING
    
    # Statistiques
    last_update: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    iocs_imported: int = 0
    iocs_updated: int = 0
    
    # Filtering
    ioc_types: List[IOCType] = Field(default_factory=list)
    min_confidence: IOCConfidence = IOCConfidence.LOW
    max_age_days: int = 30
    
    # Méta-données
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str

class ThreatIntelligenceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    content: str
    
    # Classification
    tlp: TLPClassification = TLPClassification.AMBER
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    confidence: IOCConfidence = IOCConfidence.MEDIUM
    
    # Attribution
    threat_actors: List[str] = Field(default_factory=list)
    campaigns: List[str] = Field(default_factory=list)
    malware_families: List[str] = Field(default_factory=list)
    
    # IOCs associés
    associated_iocs: List[str] = Field(default_factory=list)
    
    # Contexte temporel
    incident_date: Optional[datetime] = None
    reporting_date: datetime = Field(default_factory=datetime.now)
    
    # Géographie
    affected_countries: List[str] = Field(default_factory=list)
    affected_sectors: List[str] = Field(default_factory=list)
    
    # Méta-données
    author: str
    organization: str
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
    # Recommandations
    recommendations: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class EnrichmentResult(BaseModel):
    ioc_id: str
    source: str
    data: Dict[str, Any]
    confidence: IOCConfidence
    enriched_at: datetime = Field(default_factory=datetime.now)
    
    # Géolocalisation
    geolocation: Optional[Dict[str, Any]] = None
    
    # Réputation
    reputation_score: Optional[float] = None
    is_malicious: Optional[bool] = None
    
    # Contexte
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    detection_engines: Optional[int] = None
    
    # Relations
    related_iocs: List[str] = Field(default_factory=list)
    campaigns: List[str] = Field(default_factory=list)

# Modèles de requête
class CreateIOCRequest(BaseModel):
    value: str
    type: IOCType
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: IOCConfidence
    tlp: TLPClassification = TLPClassification.AMBER
    expiry_date: Optional[datetime] = None
    
    # Attribution
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    malware_family: Optional[str] = None
    
    # Contexte
    description: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
    # Méta-données
    source: str
    created_by: str

class UpdateIOCRequest(BaseModel):
    severity: Optional[ThreatSeverity] = None
    confidence: Optional[IOCConfidence] = None
    is_active: Optional[bool] = None
    false_positive: Optional[bool] = None
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_by: str

class IOCSearchRequest(BaseModel):
    query: Optional[str] = None
    types: Optional[List[IOCType]] = None
    threat_types: Optional[List[ThreatType]] = None
    severities: Optional[List[ThreatSeverity]] = None
    confidence: Optional[List[IOCConfidence]] = None
    tlp: Optional[List[TLPClassification]] = None
    is_active: Optional[bool] = None
    false_positive: Optional[bool] = None
    
    # Dates
    first_seen_from: Optional[date] = None
    first_seen_to: Optional[date] = None
    last_seen_from: Optional[date] = None
    last_seen_to: Optional[date] = None
    
    # Attribution
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    malware_family: Optional[str] = None
    
    # Tags et sources
    tags: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    
    # Pagination
    limit: int = 50
    offset: int = 0

class CreateCTIFeedRequest(BaseModel):
    name: str
    description: str
    provider: str
    feed_url: str
    feed_type: str
    auth_required: bool = False
    api_key: Optional[str] = None
    update_frequency: int = 3600
    ioc_types: List[IOCType] = Field(default_factory=list)
    min_confidence: IOCConfidence = IOCConfidence.LOW
    max_age_days: int = 30
    tags: List[str] = Field(default_factory=list)
    created_by: str

class ThreatIntelligenceQuery(BaseModel):
    ioc_value: str
    include_enrichment: bool = True
    include_relations: bool = True
    sources: Optional[List[str]] = None

# Modèles de réponse
class ThreatIntelligenceStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    
    # Statistiques
    total_iocs: int
    active_iocs: int
    total_feeds: int
    active_feeds: int
    threat_actors: int
    campaigns: int
    
    # Performance
    last_feed_update: Optional[datetime] = None
    enrichment_queue_size: int = 0
    
    # Santé
    feeds_status: Dict[str, str]

class IOCStatistics(BaseModel):
    total_iocs: int
    by_type: Dict[str, int]
    by_threat_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_confidence: Dict[str, int]
    by_source: Dict[str, int]
    
    # Temporel
    added_last_24h: int
    updated_last_24h: int
    expiring_soon: int
    false_positives: int
    
    # Top listes
    top_threat_actors: List[Dict[str, Any]]
    top_campaigns: List[Dict[str, Any]]
    top_malware_families: List[Dict[str, Any]]

class ThreatIntelligenceInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    insight_type: str  # trend, anomaly, correlation, prediction
    severity: ThreatSeverity
    confidence: IOCConfidence
    
    # Données
    data: Dict[str, Any]
    supporting_iocs: List[str] = Field(default_factory=list)
    
    # Contexte
    time_range: Dict[str, datetime]
    affected_assets: List[str] = Field(default_factory=list)
    
    # Actions recommandées
    recommendations: List[str] = Field(default_factory=list)
    
    # Méta-données
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = "threat_intelligence_engine"