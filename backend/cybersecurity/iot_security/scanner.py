"""
IoT Security Scanner
Moteur de scan pour dispositifs IoT
"""
import asyncio
import socket
import struct
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import ipaddress
import subprocess
import xml.etree.ElementTree as ET

from .models import IoTDevice, IoTVulnerability, IoTScanResult, IoTDeviceTarget

class IoTSecurityScanner:
    """Scanner de sécurité IoT"""
    
    def __init__(self):
        # Signatures de dispositifs IoT
        self.device_signatures = {
            "camera": {
                "keywords": ["camera", "webcam", "ipcam", "dahua", "hikvision", "axis"],
                "ports": [80, 443, 554, 8080, 8000],
                "patterns": [r"camera", r"video", r"rtsp"]
            },
            "router": {
                "keywords": ["router", "gateway", "modem", "netgear", "linksys", "cisco"],
                "ports": [80, 443, 22, 23, 8080],
                "patterns": [r"router", r"gateway", r"admin"]
            },
            "smart_bulb": {
                "keywords": ["bulb", "light", "philips", "hue", "lifx"],
                "ports": [80, 443],
                "patterns": [r"light", r"bulb", r"hue"]
            },
            "sensor": {
                "keywords": ["sensor", "temperature", "humidity", "motion"],
                "ports": [80, 443, 1883, 5683],
                "patterns": [r"sensor", r"temp", r"humidity"]
            },
            "smart_plug": {
                "keywords": ["plug", "outlet", "switch", "smart"],
                "ports": [80, 443, 9999],
                "patterns": [r"plug", r"outlet", r"switch"]
            }
        }
        
        # Vulnérabilités IoT communes
        self.vulnerability_templates = {
            "default_credentials": {
                "category": "M2_insecure_authentication",
                "severity": "high",
                "title": "Identifiants par défaut détectés",
                "description": "Le dispositif utilise des identifiants par défaut",
                "remediation": "Changer les identifiants par défaut"
            },
            "weak_encryption": {
                "category": "M3_insecure_communication",
                "severity": "medium", 
                "title": "Chiffrement faible détecté",
                "description": "Le dispositif utilise un chiffrement faible ou obsolète",
                "remediation": "Mettre à jour vers des protocoles de chiffrement récents"
            },
            "open_debug_port": {
                "category": "M8_insufficient_security_configurability",
                "severity": "critical",
                "title": "Port de debug ouvert",
                "description": "Un port de débogage est accessible publiquement",
                "remediation": "Fermer les ports de débogage en production"
            },
            "firmware_outdated": {
                "category": "M7_insecure_data_transfer_and_storage",
                "severity": "medium",
                "title": "Firmware obsolète",
                "description": "Version de firmware potentiellement vulnérable",
                "remediation": "Mettre à jour le firmware vers la dernière version"
            }
        }

    async def scan_iot_devices(self, scan_request: Dict[str, Any]) -> IoTScanResult:
        """Lance un scan IoT complet"""
        
        target = scan_request.get("target", {})
        protocols = scan_request.get("protocols", ["mqtt", "coap", "http"])
        scan_type = scan_request.get("scan_type", "discovery")
        
        result = IoTScanResult(
            scan_type=scan_type,
            target_range=target.get("ip_range", "custom"),
            scan_options=scan_request
        )
        
        try:
            result.status = "running"
            
            # 1. Discovery des dispositifs
            devices = await self._discover_devices(target)
            result.devices_discovered = devices
            result.total_devices = len(devices)
            
            # 2. Analyse des protocoles
            for device in devices:
                await self._analyze_device_protocols(device, protocols)
            
            # 3. Test de vulnérabilités si demandé
            vulnerabilities = []
            if scan_type in ["vulnerability", "configuration"]:
                for device in devices:
                    device_vulns = await self._scan_device_vulnerabilities(device)
                    vulnerabilities.extend(device_vulns)
            
            result.vulnerabilities = vulnerabilities
            result.vulnerable_devices = len(set(v.device_id for v in vulnerabilities))
            result.critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == "critical"])
            
            # 4. Statistiques par protocole
            protocol_stats = {}
            for device in devices:
                for protocol in device.protocols:
                    protocol_stats[protocol] = protocol_stats.get(protocol, 0) + 1
            result.protocols_detected = protocol_stats
            
            result.status = "completed"
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - result.started_at).total_seconds()
            
        except Exception as e:
            result.status = "failed"
            result.scan_options["error"] = str(e)
        
        return result

    async def _discover_devices(self, target: Dict[str, Any]) -> List[IoTDevice]:
        """Découvre les dispositifs IoT sur le réseau"""
        devices = []
        
        # IPs spécifiques
        specific_ips = target.get("specific_devices", [])
        for ip in specific_ips:
            device = await self._scan_single_device(ip)
            if device:
                devices.append(device)
        
        # Plage IP
        ip_range = target.get("ip_range")
        if ip_range:
            try:
                network = ipaddress.IPv4Network(ip_range, strict=False)
                # Limiter le scan pour éviter les timeouts
                hosts_to_scan = list(network.hosts())[:50]  # Max 50 hosts
                
                tasks = []
                for ip in hosts_to_scan:
                    tasks.append(self._scan_single_device(str(ip)))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                devices.extend([r for r in results if isinstance(r, IoTDevice)])
                
            except Exception as e:
                print(f"Erreur scan réseau: {e}")
        
        return devices

    async def _scan_single_device(self, ip: str) -> Optional[IoTDevice]:
        """Scanne un dispositif spécifique"""
        try:
            # Test de connectivité basique
            if not await self._is_host_alive(ip):
                return None
            
            device = IoTDevice(
                ip_address=ip,
                device_type="unknown"
            )
            
            # Scan des ports ouverts
            open_ports = await self._scan_ports(ip, [21, 22, 23, 53, 80, 443, 554, 1883, 5683, 8080, 9999])
            device.open_ports = open_ports
            
            # Identification du type de dispositif
            device_type, manufacturer, model = await self._identify_device(ip, open_ports)
            device.device_type = device_type
            device.manufacturer = manufacturer
            device.model = model
            
            # Détection des protocoles IoT
            protocols = await self._detect_iot_protocols(ip, open_ports)
            device.protocols = protocols
            
            # Récupération des services
            services = await self._get_device_services(ip, open_ports)
            device.services = services
            
            return device
            
        except Exception as e:
            print(f"Erreur scan device {ip}: {e}")
            return None

    async def _is_host_alive(self, ip: str, timeout: float = 1.0) -> bool:
        """Teste si un host est joignable"""
        try:
            # Test ping simple
            proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "1000", ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return_code = await proc.wait()
            return return_code == 0
        except:
            return False

    async def _scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Scanne les ports spécifiés"""
        open_ports = []
        
        async def check_port(port: int):
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=2.0
                )
                writer.close()
                await writer.wait_closed()
                return port
            except:
                return None
        
        tasks = [check_port(port) for port in ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        open_ports = [r for r in results if isinstance(r, int)]
        return open_ports

    async def _identify_device(self, ip: str, open_ports: List[int]) -> tuple:
        """Identifie le type de dispositif"""
        device_type = "unknown"
        manufacturer = None
        model = None
        
        # Test HTTP/HTTPS pour identification
        for port in [80, 443, 8080]:
            if port in open_ports:
                try:
                    protocol = "https" if port == 443 else "http"
                    # En production, utiliser aiohttp pour récupérer les headers/contenu
                    # Ici simulation basée sur les ports ouverts
                    
                    if port == 554:  # RTSP
                        device_type = "camera"
                    elif 1883 in open_ports:  # MQTT
                        device_type = "sensor"
                    elif port == 9999:
                        device_type = "smart_plug"
                    elif 80 in open_ports and 443 in open_ports:
                        device_type = "router"
                    
                    break
                except:
                    continue
        
        return device_type, manufacturer, model

    async def _detect_iot_protocols(self, ip: str, open_ports: List[int]) -> List[str]:
        """Détecte les protocoles IoT"""
        protocols = []
        
        # MQTT (port 1883)
        if 1883 in open_ports:
            protocols.append("MQTT")
        
        # CoAP (port 5683)
        if 5683 in open_ports:
            protocols.append("CoAP")
        
        # HTTP/HTTPS
        if 80 in open_ports:
            protocols.append("HTTP")
        if 443 in open_ports:
            protocols.append("HTTPS")
        
        # RTSP (caméras)
        if 554 in open_ports:
            protocols.append("RTSP")
        
        # SSH/Telnet
        if 22 in open_ports:
            protocols.append("SSH")
        if 23 in open_ports:
            protocols.append("Telnet")
        
        return protocols

    async def _get_device_services(self, ip: str, open_ports: List[int]) -> Dict[str, str]:
        """Récupère les services détectés sur les ports"""
        services = {}
        
        port_services = {
            21: "FTP",
            22: "SSH", 
            23: "Telnet",
            53: "DNS",
            80: "HTTP",
            443: "HTTPS",
            554: "RTSP",
            1883: "MQTT",
            5683: "CoAP",
            8080: "HTTP-Alt",
            9999: "Custom"
        }
        
        for port in open_ports:
            if port in port_services:
                services[str(port)] = port_services[port]
        
        return services

    async def _scan_device_vulnerabilities(self, device: IoTDevice) -> List[IoTVulnerability]:
        """Scanne les vulnérabilités d'un dispositif"""
        vulnerabilities = []
        
        # Test des identifiants par défaut
        if await self._check_default_credentials(device):
            vuln = self._create_vulnerability(
                device.id, "default_credentials", 
                protocol="HTTP", port=80
            )
            vulnerabilities.append(vuln)
        
        # Test des ports de debug ouverts
        debug_ports = [23, 2323, 4567, 9000]  # Ports de debug communs
        for port in debug_ports:
            if port in device.open_ports:
                vuln = self._create_vulnerability(
                    device.id, "open_debug_port",
                    protocol="Telnet" if port == 23 else "Debug",
                    port=port
                )
                vulnerabilities.append(vuln)
        
        # Test chiffrement faible (Telnet ouvert)
        if 23 in device.open_ports:
            vuln = self._create_vulnerability(
                device.id, "weak_encryption",
                protocol="Telnet", port=23
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities

    async def _check_default_credentials(self, device: IoTDevice) -> bool:
        """Vérifie les identifiants par défaut (simulation)"""
        # En production, tester les combinaisons courantes
        # admin/admin, admin/password, root/root, etc.
        
        # Simulation basée sur le type de dispositif
        if device.device_type == "camera" and 80 in device.open_ports:
            return True  # Les caméras ont souvent des identifiants par défaut
        elif device.device_type == "router" and 80 in device.open_ports:
            return True  # Routeurs également
        
        return False

    async def _analyze_device_protocols(self, device: IoTDevice, protocols: List[str]) -> None:
        """Analyse approfondie des protocoles"""
        
        for protocol in protocols:
            if protocol.lower() == "mqtt" and "MQTT" in device.protocols:
                # Test MQTT sans authentification
                mqtt_info = await self._test_mqtt_security(device.ip_address)
                if mqtt_info.get("anonymous_access"):
                    device.services["mqtt_anonymous"] = "true"
            
            elif protocol.lower() == "coap" and "CoAP" in device.protocols:
                # Test CoAP
                coap_info = await self._test_coap_security(device.ip_address)
                device.services.update(coap_info)

    async def _test_mqtt_security(self, ip: str) -> Dict[str, Any]:
        """Teste la sécurité MQTT (simulation)"""
        # En production, utiliser paho-mqtt
        return {
            "anonymous_access": True,
            "version": "3.1.1",
            "topics_discoverable": True
        }

    async def _test_coap_security(self, ip: str) -> Dict[str, Any]:
        """Teste la sécurité CoAP (simulation)"""
        # En production, utiliser aiocoap
        return {
            "coap_version": "1.0",
            "resources_enumerable": True,
            "dtls_enabled": False
        }

    def _create_vulnerability(self, device_id: str, vuln_type: str, protocol: str, port: int = None) -> IoTVulnerability:
        """Crée une vulnérabilité à partir d'un template"""
        template = self.vulnerability_templates[vuln_type]
        
        return IoTVulnerability(
            device_id=device_id,
            category=template["category"],
            severity=template["severity"],
            title=template["title"],
            description=template["description"],
            protocol=protocol,
            port=port,
            remediation=template["remediation"],
            confidence=0.8
        )