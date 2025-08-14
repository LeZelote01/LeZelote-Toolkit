"""
IoT Security Models
Modèles Pydantic pour la sécurité IoT
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class IoTDeviceTarget(BaseModel):
    """Configuration de cible IoT"""
    ip_range: Optional[str] = Field(None, description="Plage IP à scanner (ex: 192.168.1.0/24)")
    specific_devices: List[str] = Field(default_factory=list, description="IPs spécifiques")
    ports: List[int] = Field(default_factory=lambda: [21, 22, 23, 53, 80, 443, 1883, 5683], description="Ports à scanner")

class IoTScanRequest(BaseModel):
    """Requête de scan IoT"""
    target: IoTDeviceTarget = Field(..., description="Cibles à scanner")
    protocols: List[str] = Field(default_factory=lambda: ["mqtt", "coap", "modbus", "http"], description="Protocoles IoT à tester")
    scan_type: str = Field(default="discovery", description="Type: discovery|vulnerability|configuration")
    scan_options: Dict[str, Any] = Field(default_factory=dict, description="Options avancées")

class IoTDevice(BaseModel):
    """Dispositif IoT découvert"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ip_address: str = Field(..., description="Adresse IP")
    mac_address: Optional[str] = Field(None, description="Adresse MAC")
    device_type: str = Field(..., description="Type de dispositif détecté")
    manufacturer: Optional[str] = Field(None, description="Fabricant")
    model: Optional[str] = Field(None, description="Modèle")
    firmware_version: Optional[str] = Field(None, description="Version firmware")
    open_ports: List[int] = Field(default_factory=list, description="Ports ouverts")
    protocols: List[str] = Field(default_factory=list, description="Protocoles IoT détectés")
    services: Dict[str, str] = Field(default_factory=dict, description="Services détectés")
    discovered_at: datetime = Field(default_factory=datetime.now)

class IoTVulnerability(BaseModel):
    """Vulnérabilité IoT"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(..., description="ID du dispositif")
    category: str = Field(..., description="Catégorie OWASP IoT")
    severity: str = Field(..., description="Severity: critical|high|medium|low")
    title: str = Field(..., description="Titre de la vulnérabilité")
    description: str = Field(..., description="Description détaillée")
    cve_id: Optional[str] = Field(None, description="CVE ID si disponible")
    protocol: str = Field(..., description="Protocole concerné")
    port: Optional[int] = Field(None, description="Port concerné")
    remediation: str = Field(..., description="Recommandations")
    confidence: float = Field(..., description="Niveau de confiance 0-1")
    detected_at: datetime = Field(default_factory=datetime.now)

class IoTScanResult(BaseModel):
    """Résultat de scan IoT"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scan_type: str = Field(..., description="Type de scan effectué")
    target_range: str = Field(..., description="Plage scannée")
    status: str = Field(default="pending", description="Status: pending|running|completed|failed")
    
    # Résultats
    devices_discovered: List[IoTDevice] = Field(default_factory=list)
    vulnerabilities: List[IoTVulnerability] = Field(default_factory=list)
    protocols_detected: Dict[str, int] = Field(default_factory=dict)
    
    # Métriques
    total_devices: int = 0
    vulnerable_devices: int = 0
    critical_vulnerabilities: int = 0
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)
    duration: Optional[float] = Field(None, description="Durée en secondes")
    
    # Metadata
    scan_options: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class IoTSecurityMetrics(BaseModel):
    """Métriques IoT Security"""
    total_scans: int = 0
    total_devices_discovered: int = 0
    devices_by_type: Dict[str, int] = Field(default_factory=dict)
    protocols_statistics: Dict[str, int] = Field(default_factory=dict)
    vulnerability_trends: Dict[str, int] = Field(default_factory=dict)
    most_vulnerable_types: List[Dict[str, Any]] = Field(default_factory=list)

class IoTSecurityStatus(BaseModel):
    """Status du service IoT Security"""
    status: str = "operational"
    service: str = "IoT Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "device_discovery": True,
        "protocol_analysis": True,
        "vulnerability_scanning": True,
        "configuration_audit": True,
        "mqtt_analysis": True,
        "coap_analysis": True,
        "modbus_analysis": True,
        "network_mapping": True
    })
    supported_protocols: List[str] = Field(default_factory=lambda: [
        "MQTT", "CoAP", "Modbus", "BLE", "Zigbee", "HTTP", "HTTPS", "FTP", "SSH", "Telnet"
    ])
    supported_scan_types: List[str] = Field(default_factory=lambda: [
        "discovery", "vulnerability", "configuration", "protocol_analysis"
    ])
    active_scans: int = 0
    completed_scans: int = 0
    metrics: Optional[IoTSecurityMetrics] = None