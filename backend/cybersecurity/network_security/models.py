"""
Modèles de données pour Network Security
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ScanType(str, Enum):
    """Types de scans réseau"""
    PORT_SCAN = "port_scan"
    HOST_DISCOVERY = "host_discovery"
    SERVICE_DETECTION = "service_detection"
    OS_DETECTION = "os_detection"
    VULNERABILITY_SCAN = "vulnerability_scan"
    FULL_SCAN = "full_scan"
    STEALTH_SCAN = "stealth_scan"
    UDP_SCAN = "udp_scan"

class PortState(str, Enum):
    """États des ports"""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"
    OPEN_FILTERED = "open|filtered"
    CLOSED_FILTERED = "closed|filtered"

class ServiceState(str, Enum):
    """États des services"""
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"
    ERROR = "error"

class Severity(str, Enum):
    """Niveaux de sévérité"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class NetworkTarget(BaseModel):
    """Cible réseau pour scan"""
    ip_range: Optional[str] = Field(None, description="Plage IP (ex: 192.168.1.0/24)")
    specific_hosts: Optional[List[str]] = Field(None, description="Hôtes spécifiques")
    exclude_hosts: Optional[List[str]] = Field(default_factory=list, description="Hôtes à exclure")
    ports: Optional[str] = Field(None, description="Ports à scanner (ex: 1-1000, 22,80,443)")

class ScanOptions(BaseModel):
    """Options de scan"""
    timing_template: int = Field(default=3, ge=0, le=5, description="Template de timing (0=paranoid, 5=insane)")
    max_hostgroup: int = Field(default=256, description="Taille max du groupe d'hôtes")
    min_rate: Optional[int] = Field(None, description="Taux minimum de paquets/seconde")
    max_rate: Optional[int] = Field(None, description="Taux maximum de paquets/seconde")
    max_retries: int = Field(default=2, description="Nombre max de tentatives")
    host_timeout: str = Field(default="900s", description="Timeout par hôte")
    scan_delay: Optional[str] = Field(None, description="Délai entre les paquets")
    randomize_hosts: bool = Field(default=True, description="Randomiser l'ordre des hôtes")
    fragment_packets: bool = Field(default=False, description="Fragmenter les paquets")
    decoy_scan: bool = Field(default=False, description="Utiliser des leurres")
    source_port: Optional[int] = Field(None, description="Port source spécifique")
    spoof_mac: Optional[str] = Field(None, description="Adresse MAC usurpée")

class NetworkScanRequest(BaseModel):
    """Requête de scan réseau"""
    target: NetworkTarget
    scan_type: ScanType = ScanType.PORT_SCAN
    scan_options: ScanOptions = Field(default_factory=ScanOptions)
    
    # Options avancées
    service_detection: bool = Field(default=True, description="Détecter les services")
    version_detection: bool = Field(default=True, description="Détecter les versions")
    os_detection: bool = Field(default=False, description="Détecter l'OS")
    script_scan: bool = Field(default=False, description="Exécuter les scripts NSE")
    aggressive_scan: bool = Field(default=False, description="Scan agressif")
    
    # Scripts NSE spécifiques  
    nse_scripts: List[str] = Field(default_factory=list, description="Scripts NSE à exécuter")
    
    # Options de sortie
    output_format: str = Field(default="json", description="Format de sortie")
    save_raw_output: bool = Field(default=True, description="Sauvegarder la sortie brute")

class Port(BaseModel):
    """Information sur un port"""
    port: int
    protocol: str = "tcp"
    state: PortState
    service: Optional[str] = None
    version: Optional[str] = None
    product: Optional[str] = None
    extra_info: Optional[str] = None
    cpe: List[str] = Field(default_factory=list)
    scripts: Dict[str, Any] = Field(default_factory=dict)

class Service(BaseModel):
    """Information sur un service"""
    name: str
    port: int
    protocol: str = "tcp"
    state: ServiceState
    version: Optional[str] = None
    product: Optional[str] = None
    extra_info: Optional[str] = None
    tunnel: Optional[str] = None
    method: Optional[str] = None
    confidence: int = Field(default=0, ge=0, le=10)

class Host(BaseModel):
    """Information sur un hôte"""
    ip: str
    hostname: Optional[str] = None
    state: str = "up"
    reason: Optional[str] = None
    
    # Informations système
    os_matches: List[Dict[str, Any]] = Field(default_factory=list)
    os_fingerprint: Optional[str] = None
    uptime: Optional[str] = None
    
    # Ports et services
    ports: List[Port] = Field(default_factory=list)
    services: List[Service] = Field(default_factory=list)
    
    # Informations réseau
    mac_address: Optional[str] = None
    vendor: Optional[str] = None
    
    # Scripts NSE
    host_scripts: Dict[str, Any] = Field(default_factory=dict)
    
    # Métriques
    scan_duration: float = 0.0
    last_seen: datetime = Field(default_factory=datetime.now)

class NetworkVulnerability(BaseModel):
    """Vulnérabilité réseau détectée"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    scan_id: str
    host_ip: str
    port: Optional[int] = None
    service: Optional[str] = None
    
    # Détails de la vulnérabilité
    title: str
    description: str
    severity: Severity
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = Field(None, ge=0, le=10)
    
    # Classification
    category: str
    attack_vector: str
    impact: str
    
    # Preuves
    evidence: Dict[str, Any] = Field(default_factory=dict)
    script_output: Optional[str] = None
    
    # Remédiation
    remediation: str
    remediation_steps: List[str] = Field(default_factory=list)
    
    # Métadonnées
    detected_at: datetime = Field(default_factory=datetime.now)
    confidence: int = Field(default=5, ge=1, le=10)
    exploitability: str = Field(default="unknown")

class NetworkScanResult(BaseModel):
    """Résultat de scan réseau"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    scan_type: ScanType
    status: str = "completed"
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration: float = 0.0  # en secondes
    
    # Cible et options
    target_range: str
    scan_options_used: Dict[str, Any] = Field(default_factory=dict)
    
    # Résultats
    hosts_discovered: List[Host] = Field(default_factory=list)
    total_hosts: int = 0
    hosts_up: int = 0
    hosts_down: int = 0
    
    # Ports et services
    total_ports_scanned: int = 0
    open_ports: int = 0
    closed_ports: int = 0
    filtered_ports: int = 0
    
    # Services détectés
    services_detected: Dict[str, int] = Field(default_factory=dict)
    os_detected: Dict[str, int] = Field(default_factory=dict)
    
    # Vulnérabilités
    vulnerabilities: List[NetworkVulnerability] = Field(default_factory=list)
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    
    # Informations techniques
    nmap_version: Optional[str] = None
    nmap_command: Optional[str] = None
    raw_output: Optional[str] = None
    
    # Statistiques
    scan_stats: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class NetworkSecurityStatus(BaseModel):
    """Status du service Network Security"""
    status: str = "operational"
    service: str = "Network Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=dict)
    supported_scan_types: List[ScanType] = Field(default_factory=list)
    nmap_available: bool = True
    active_scans: int = 0
    completed_scans: int = 0

class NetworkSecurityMetrics(BaseModel):
    """Métriques globales Network Security"""
    total_scans: int = 0
    total_hosts_scanned: int = 0
    total_ports_scanned: int = 0
    total_services_detected: int = 0
    total_vulnerabilities: int = 0
    scan_type_stats: Dict[ScanType, int] = Field(default_factory=dict)
    top_services: Dict[str, int] = Field(default_factory=dict)
    top_os: Dict[str, int] = Field(default_factory=dict)
    vulnerability_stats: Dict[Severity, int] = Field(default_factory=dict)

class TopologyNode(BaseModel):
    """Nœud dans la topologie réseau"""
    ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    vendor: Optional[str] = None
    os_guess: Optional[str] = None
    device_type: Optional[str] = None
    open_ports: List[int] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    
    # Position dans la topologie
    subnet: Optional[str] = None
    gateway: Optional[str] = None
    
    # Connexions
    connected_to: List[str] = Field(default_factory=list)
    
    # Sécurité
    security_score: float = Field(default=50.0, ge=0, le=100)
    vulnerabilities_count: int = 0
    
    # Métadonnées
    last_scan: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(default=0.5, ge=0, le=1)

class NetworkTopology(BaseModel):
    """Topologie réseau découverte"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str
    description: Optional[str] = None
    
    # Nœuds et connexions
    nodes: List[TopologyNode] = Field(default_factory=list)
    edges: List[Dict[str, str]] = Field(default_factory=list)
    
    # Subnets découverts
    subnets: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statistiques
    total_hosts: int = 0
    total_services: int = 0
    total_vulnerabilities: int = 0
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    scan_ids: List[str] = Field(default_factory=list)