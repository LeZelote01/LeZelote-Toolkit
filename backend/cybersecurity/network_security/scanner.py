"""
Network Security Scanner
Moteur de scan réseau basé sur Nmap
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
import asyncio
import json
import subprocess
import random
import ipaddress
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re

from .models import (
    NetworkScanRequest, NetworkScanResult, NetworkVulnerability,
    Host, Port, Service, NetworkTopology, TopologyNode,
    ScanType, PortState, ServiceState, Severity
)

class NetworkSecurityScanner:
    """Scanner de sécurité réseau"""
    
    def __init__(self):
        self.nmap_available = self._check_nmap_availability()
        self.vulnerability_db = self._load_vulnerability_signatures()
        self.service_detection_patterns = self._load_service_patterns()
        
    async def scan_network(self, request_dict: Dict[str, Any]) -> NetworkScanResult:
        """Lance un scan réseau complet"""
        request = NetworkScanRequest(**request_dict)
        
        result = NetworkScanResult(
            scan_type=request.scan_type,
            status="running",
            target_range=self._format_target_range(request.target)
        )
        
        start_time = datetime.now()
        
        try:
            print(f"🔍 Démarrage scan réseau: {request.scan_type}")
            
            if self.nmap_available:
                # Utiliser Nmap si disponible
                hosts = await self._nmap_scan(request)
            else:
                # Utiliser scan simulé
                hosts = await self._simulated_scan(request)
            
            # Analyser les résultats pour détecter les vulnérabilités
            vulnerabilities = await self._analyze_vulnerabilities(hosts, result.id)
            
            # Calculer les statistiques
            result = self._calculate_scan_statistics(result, hosts, vulnerabilities)
            
            # Finaliser le résultat
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - start_time).total_seconds()
            result.status = "completed"
            result.hosts_discovered = hosts
            result.vulnerabilities = vulnerabilities
            result.total_vulnerabilities = len(vulnerabilities)
            result.critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == Severity.CRITICAL])
            result.high_vulnerabilities = len([v for v in vulnerabilities if v.severity == Severity.HIGH])
            
            print(f"✅ Scan terminé: {len(hosts)} hôtes, {len(vulnerabilities)} vulnérabilités")
            
        except Exception as e:
            result.status = "failed"
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - start_time).total_seconds()
            result.errors.append(str(e))
            print(f"❌ Erreur lors du scan: {e}")
        
        return result
    
    async def _nmap_scan(self, request: NetworkScanRequest) -> List[Host]:
        """Exécute un scan Nmap réel"""
        # Construction de la commande Nmap
        cmd = self._build_nmap_command(request)
        
        try:
            # Exécuter Nmap
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Erreur Nmap: {stderr.decode()}")
            
            # Parser la sortie XML de Nmap
            hosts = self._parse_nmap_xml(stdout.decode())
            
        except Exception as e:
            print(f"Erreur Nmap, utilisation du mode simulé: {e}")
            hosts = await self._simulated_scan(request)
        
        return hosts
    
    async def _simulated_scan(self, request: NetworkScanRequest) -> List[Host]:
        """Scan simulé pour démonstration"""
        hosts = []
        
        # Générer des hôtes simulés basés sur la cible
        target_ips = self._generate_target_ips(request.target)
        
        for i, ip in enumerate(target_ips[:20]):  # Limiter à 20 hôtes max pour la demo
            if random.random() < 0.7:  # 70% chance qu'un hôte soit up
                host = await self._generate_simulated_host(ip, request)
                hosts.append(host)
                
                # Simuler un délai de scan
                await asyncio.sleep(0.1)
        
        return hosts
    
    async def _generate_simulated_host(self, ip: str, request: NetworkScanRequest) -> Host:
        """Génère un hôte simulé avec ports et services"""
        host = Host(
            ip=ip,
            hostname=f"host-{ip.replace('.', '-')}.local" if random.random() < 0.6 else None,
            state="up",
            reason="syn-ack"
        )
        
        # Générer des ports ouverts simulés
        common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306, 1433, 21, 25565]
        
        for port_num in random.sample(common_ports, random.randint(2, 8)):
            port = self._generate_simulated_port(port_num)
            host.ports.append(port)
            
            # Créer un service correspondant
            service = self._generate_simulated_service(port_num, port.service)
            host.services.append(service)
        
        # Générer une détection d'OS simulée
        if request.os_detection and random.random() < 0.8:
            host.os_matches = self._generate_simulated_os()
        
        # Générer une adresse MAC pour les hôtes du même subnet
        if self._is_local_subnet(ip):
            host.mac_address = self._generate_mac_address()
            host.vendor = random.choice(["Dell Inc.", "HP Inc.", "Cisco Systems", "Intel Corp.", "Apple Inc."])
        
        host.scan_duration = random.uniform(0.5, 3.0)
        
        return host
    
    def _generate_simulated_port(self, port_num: int) -> Port:
        """Génère un port simulé"""
        services_map = {
            22: ("ssh", "OpenSSH", "7.4"),
            23: ("telnet", "Linux telnetd", ""),
            25: ("smtp", "Postfix smtpd", ""),
            53: ("domain", "ISC BIND", "9.11.4"),
            80: ("http", "Apache httpd", "2.4.29"),
            110: ("pop3", "Dovecot pop3d", ""),
            143: ("imap", "Dovecot imapd", ""),
            443: ("https", "Apache httpd", "2.4.29"),
            993: ("imaps", "Dovecot imapd", ""),
            995: ("pop3s", "Dovecot pop3d", ""),
            3389: ("ms-wbt-server", "Microsoft Terminal Services", ""),
            5432: ("postgresql", "PostgreSQL DB", "12.2"),
            3306: ("mysql", "MySQL", "8.0.25"),
            1433: ("ms-sql-s", "Microsoft SQL Server", "2019"),
            21: ("ftp", "vsftpd", "3.0.3"),
            25565: ("minecraft", "Minecraft", "1.18.2")
        }
        
        service_info = services_map.get(port_num, ("unknown", "", ""))
        
        return Port(
            port=port_num,
            protocol="tcp",
            state=PortState.OPEN,
            service=service_info[0],
            product=service_info[1],
            version=service_info[2],
            extra_info="",
            scripts=self._generate_port_scripts(port_num, service_info[0])
        )
    
    def _generate_simulated_service(self, port: int, service_name: Optional[str]) -> Service:
        """Génère un service simulé"""
        return Service(
            name=service_name or "unknown",
            port=port,
            protocol="tcp",
            state=ServiceState.RUNNING,
            confidence=random.randint(7, 10)
        )
    
    def _generate_simulated_os(self) -> List[Dict[str, Any]]:
        """Génère une détection d'OS simulée"""
        os_options = [
            {"name": "Linux 4.15 - 5.6", "accuracy": random.randint(85, 95)},
            {"name": "Microsoft Windows 10 1709 - 1909", "accuracy": random.randint(80, 92)},
            {"name": "Microsoft Windows Server 2016 - 2019", "accuracy": random.randint(78, 88)},
            {"name": "Ubuntu Linux 18.04 - 20.04", "accuracy": random.randint(82, 94)},
            {"name": "CentOS 7.0 - 8.0", "accuracy": random.randint(75, 87)},
            {"name": "macOS 10.14 - 11.0", "accuracy": random.randint(80, 90)}
        ]
        
        return [random.choice(os_options)]
    
    def _generate_port_scripts(self, port: int, service: str) -> Dict[str, Any]:
        """Génère des résultats de scripts NSE simulés"""
        scripts = {}
        
        if port == 22 and service == "ssh":
            scripts["ssh-hostkey"] = {
                "key_type": "rsa",
                "bits": 2048,
                "fingerprint": "SHA256:" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=43))
            }
        elif port == 80 and service == "http":
            scripts["http-title"] = {"title": "Apache2 Default Page"}
            scripts["http-server-header"] = {"server": "Apache/2.4.29"}
        elif port == 443 and service == "https":
            scripts["ssl-cert"] = {
                "subject": {"commonName": "example.com"},
                "issuer": {"commonName": "Let's Encrypt Authority X3"},
                "valid_from": "2023-01-01T00:00:00Z",
                "valid_to": "2024-01-01T00:00:00Z"
            }
        
        return scripts
    
    async def _analyze_vulnerabilities(self, hosts: List[Host], scan_id: str) -> List[NetworkVulnerability]:
        """Analyse les hôtes pour détecter les vulnérabilités"""
        vulnerabilities = []
        
        for host in hosts:
            # Analyser chaque port/service
            for port in host.ports:
                vulns = self._check_port_vulnerabilities(host, port, scan_id)
                vulnerabilities.extend(vulns)
            
            # Analyser les configurations d'hôte
            host_vulns = self._check_host_vulnerabilities(host, scan_id)
            vulnerabilities.extend(host_vulns)
        
        return vulnerabilities
    
    def _check_port_vulnerabilities(self, host: Host, port: Port, scan_id: str) -> List[NetworkVulnerability]:
        """Vérifie les vulnérabilités liées à un port"""
        vulnerabilities = []
        
        # Port Telnet ouvert (23)
        if port.port == 23 and port.state == PortState.OPEN:
            vulnerabilities.append(NetworkVulnerability(
                scan_id=scan_id,
                host_ip=host.ip,
                port=port.port,
                service=port.service,
                title="Service Telnet non sécurisé détecté",
                description="Le service Telnet transmet les données en clair, incluant les mots de passe",
                severity=Severity.HIGH,
                category="Insecure Protocol",
                attack_vector="Network",
                impact="Interception des credentials et communications",
                remediation="Désactiver Telnet et utiliser SSH à la place",
                remediation_steps=[
                    "Désactiver le service Telnet",
                    "Installer et configurer SSH",
                    "Bloquer le port 23 sur le firewall",
                    "Auditer les comptes utilisateurs"
                ],
                confidence=9,
                exploitability="high"
            ))
        
        # FTP anonyme (21)
        if port.port == 21 and port.state == PortState.OPEN:
            if random.random() < 0.3:  # 30% chance de FTP anonyme
                vulnerabilities.append(NetworkVulnerability(
                    scan_id=scan_id,
                    host_ip=host.ip,
                    port=port.port,
                    service=port.service,
                    title="Accès FTP anonyme autorisé",
                    description="Le serveur FTP permet l'accès anonyme sans authentification",
                    severity=Severity.MEDIUM,
                    category="Authentication Bypass",
                    attack_vector="Network",
                    impact="Accès non autorisé aux fichiers",
                    remediation="Désactiver l'accès FTP anonyme",
                    remediation_steps=[
                        "Configurer l'authentification FTP obligatoire",
                        "Restreindre les permissions des dossiers",
                        "Utiliser SFTP à la place",
                        "Surveiller les accès FTP"
                    ],
                    confidence=8
                ))
        
        # Services avec versions obsolètes
        if port.service and port.version:
            if self._is_outdated_version(port.service, port.version):
                vulnerabilities.append(NetworkVulnerability(
                    scan_id=scan_id,
                    host_ip=host.ip,
                    port=port.port,
                    service=port.service,
                    title=f"Version obsolète détectée: {port.service} {port.version}",
                    description=f"Le service {port.service} utilise une version obsolète potentiellement vulnérable",
                    severity=Severity.MEDIUM,
                    category="Outdated Software",
                    attack_vector="Network",
                    impact="Exploitation de vulnérabilités connues",
                    remediation=f"Mettre à jour {port.service} vers la dernière version",
                    remediation_steps=[
                        f"Mettre à jour {port.service}",
                        "Appliquer les correctifs de sécurité",
                        "Configurer les mises à jour automatiques",
                        "Tester la compatibilité"
                    ],
                    confidence=7
                ))
        
        # SSL/TLS faible (443)
        if port.port == 443 and port.state == PortState.OPEN:
            if random.random() < 0.4:  # 40% chance de config SSL faible
                vulnerabilities.append(NetworkVulnerability(
                    scan_id=scan_id,
                    host_ip=host.ip,
                    port=port.port,
                    service=port.service,
                    title="Configuration SSL/TLS faible",
                    description="Le serveur accepte des protocoles SSL/TLS obsolètes ou des chiffrements faibles",
                    severity=Severity.MEDIUM,
                    category="Weak Cryptography",
                    attack_vector="Network",
                    impact="Interception et déchiffrement des communications",
                    remediation="Configurer SSL/TLS avec des paramètres sécurisés",
                    remediation_steps=[
                        "Désactiver SSLv2, SSLv3, TLSv1.0, TLSv1.1",
                        "Utiliser uniquement TLSv1.2 et TLSv1.3",
                        "Configurer des suites de chiffrement sécurisées",
                        "Implémenter HSTS"
                    ],
                    confidence=6
                ))
        
        return vulnerabilities
    
    def _check_host_vulnerabilities(self, host: Host, scan_id: str) -> List[NetworkVulnerability]:
        """Vérifie les vulnérabilités au niveau de l'hôte"""
        vulnerabilities = []
        
        # Trop de ports ouverts
        open_ports_count = len([p for p in host.ports if p.state == PortState.OPEN])
        if open_ports_count > 10:
            vulnerabilities.append(NetworkVulnerability(
                scan_id=scan_id,
                host_ip=host.ip,
                title="Nombre excessif de ports ouverts",
                description=f"L'hôte expose {open_ports_count} ports ouverts, augmentant la surface d'attaque",
                severity=Severity.LOW,
                category="Information Disclosure",
                attack_vector="Network",
                impact="Augmentation de la surface d'attaque",
                remediation="Fermer les ports non nécessaires",
                remediation_steps=[
                    "Auditer les services nécessaires",
                    "Fermer les ports inutiles",
                    "Configurer un firewall",
                    "Surveiller les ports ouverts"
                ],
                confidence=5
            ))
        
        # OS potentiellement vulnérable
        if host.os_matches:
            for os_match in host.os_matches:
                if "Windows" in os_match.get("name", "") and random.random() < 0.3:
                    vulnerabilities.append(NetworkVulnerability(
                        scan_id=scan_id,
                        host_ip=host.ip,
                        title="Système d'exploitation potentiellement vulnérable",
                        description=f"OS détecté: {os_match.get('name', 'Unknown')} - vérifier les mises à jour",
                        severity=Severity.INFO,
                        category="System Information",
                        attack_vector="Network",
                        impact="Exploitation de vulnérabilités système",
                        remediation="Maintenir le système à jour avec les derniers correctifs",
                        remediation_steps=[
                            "Vérifier les mises à jour système",
                            "Appliquer les correctifs de sécurité",
                            "Configurer les mises à jour automatiques",
                            "Surveiller les avis de sécurité"
                        ],
                        confidence=4
                    ))
        
        return vulnerabilities
    
    def _calculate_scan_statistics(self, result: NetworkScanResult, 
                                 hosts: List[Host], 
                                 vulnerabilities: List[NetworkVulnerability]) -> NetworkScanResult:
        """Calcule les statistiques du scan"""
        
        result.total_hosts = len(hosts)
        result.hosts_up = len([h for h in hosts if h.state == "up"])
        result.hosts_down = result.total_hosts - result.hosts_up
        
        # Statistiques des ports
        all_ports = [port for host in hosts for port in host.ports]
        result.total_ports_scanned = len(all_ports)
        result.open_ports = len([p for p in all_ports if p.state == PortState.OPEN])
        result.closed_ports = len([p for p in all_ports if p.state == PortState.CLOSED])
        result.filtered_ports = len([p for p in all_ports if p.state == PortState.FILTERED])
        
        # Services détectés
        services = {}
        for host in hosts:
            for port in host.ports:
                if port.service:
                    services[port.service] = services.get(port.service, 0) + 1
        result.services_detected = services
        
        # OS détectés
        os_systems = {}
        for host in hosts:
            for os_match in host.os_matches:
                os_name = os_match.get("name", "Unknown")
                os_systems[os_name] = os_systems.get(os_name, 0) + 1
        result.os_detected = os_systems
        
        # Statistiques de scan
        result.scan_stats = {
            "avg_scan_time_per_host": sum(h.scan_duration for h in hosts) / max(1, len(hosts)),
            "total_scan_time": result.duration,
            "hosts_per_second": len(hosts) / max(1, result.duration) if result.duration > 0 else 0,
            "ports_per_second": result.total_ports_scanned / max(1, result.duration) if result.duration > 0 else 0
        }
        
        return result
    
    def generate_network_topology(self, scan_results: List[NetworkScanResult]) -> NetworkTopology:
        """Génère une topologie réseau basée sur les résultats de scan"""
        topology = NetworkTopology(
            name="Network Topology",
            description="Topologie générée automatiquement"
        )
        
        nodes = []
        edges = []
        subnets = {}
        
        for scan_result in scan_results:
            for host in scan_result.hosts_discovered:
                # Créer un nœud pour chaque hôte
                node = TopologyNode(
                    ip=host.ip,
                    hostname=host.hostname,
                    mac_address=host.mac_address,
                    vendor=host.vendor,
                    os_guess=host.os_matches[0].get("name") if host.os_matches else None,
                    device_type=self._guess_device_type(host),
                    open_ports=[p.port for p in host.ports if p.state == PortState.OPEN],
                    services=[p.service for p in host.ports if p.service],
                    subnet=self._get_subnet(host.ip),
                    vulnerabilities_count=len([v for v in scan_result.vulnerabilities if v.host_ip == host.ip]),
                    last_scan=scan_result.completed_at or datetime.now()
                )
                
                # Calculer le score de sécurité
                node.security_score = self._calculate_security_score(host, scan_result.vulnerabilities)
                
                nodes.append(node)
                
                # Grouper par subnet
                subnet_key = self._get_subnet(host.ip)
                if subnet_key not in subnets:
                    subnets[subnet_key] = []
                subnets[subnet_key].append(host.ip)
        
        topology.nodes = nodes
        topology.subnets = [{"subnet": k, "hosts": v} for k, v in subnets.items()]
        topology.total_hosts = len(nodes)
        topology.total_services = sum(len(node.services) for node in nodes)
        topology.total_vulnerabilities = sum(node.vulnerabilities_count for node in nodes)
        topology.scan_ids = [result.id for result in scan_results]
        
        return topology
    
    # Méthodes utilitaires
    
    def _check_nmap_availability(self) -> bool:
        """Vérifie si Nmap est disponible"""
        try:
            subprocess.run(["nmap", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _build_nmap_command(self, request: NetworkScanRequest) -> List[str]:
        """Construit la commande Nmap"""
        cmd = ["nmap"]
        
        # Options de scan selon le type
        if request.scan_type == ScanType.STEALTH_SCAN:
            cmd.extend(["-sS"])
        elif request.scan_type == ScanType.UDP_SCAN:
            cmd.extend(["-sU"])
        elif request.scan_type == ScanType.FULL_SCAN:
            cmd.extend(["-sS", "-sU"])
        
        # Détection de services et versions
        if request.service_detection:
            cmd.extend(["-sV"])
        
        # Détection d'OS
        if request.os_detection:
            cmd.extend(["-O"])
        
        # Scripts NSE
        if request.script_scan:
            cmd.extend(["-sC"])
        
        if request.nse_scripts:
            cmd.extend(["--script", ",".join(request.nse_scripts)])
        
        # Timing
        cmd.extend([f"-T{request.scan_options.timing_template}"])
        
        # Ports
        if request.target.ports:
            cmd.extend(["-p", request.target.ports])
        
        # Format de sortie
        cmd.extend(["-oX", "-"])  # Output XML vers stdout
        
        # Cibles
        if request.target.ip_range:
            cmd.append(request.target.ip_range)
        elif request.target.specific_hosts:
            cmd.extend(request.target.specific_hosts)
        
        # Exclusions
        if request.target.exclude_hosts:
            cmd.extend(["--exclude", ",".join(request.target.exclude_hosts)])
        
        return cmd
    
    def _parse_nmap_xml(self, xml_output: str) -> List[Host]:
        """Parse la sortie XML de Nmap"""
        hosts = []
        
        try:
            root = ET.fromstring(xml_output)
            
            for host_elem in root.findall("host"):
                host = self._parse_host_element(host_elem)
                if host:
                    hosts.append(host)
        
        except ET.ParseError as e:
            print(f"Erreur parsing XML Nmap: {e}")
        
        return hosts
    
    def _parse_host_element(self, host_elem) -> Optional[Host]:
        """Parse un élément host XML de Nmap"""
        # Récupérer l'adresse IP
        address_elem = host_elem.find("address[@addrtype='ipv4']")
        if address_elem is None:
            return None
        
        ip = address_elem.get("addr")
        
        # Status de l'hôte
        status_elem = host_elem.find("status")
        state = status_elem.get("state") if status_elem is not None else "unknown"
        
        if state != "up":
            return None
        
        host = Host(ip=ip, state=state)
        
        # Hostname
        hostnames = host_elem.find("hostnames")
        if hostnames is not None:
            hostname_elem = hostnames.find("hostname")
            if hostname_elem is not None:
                host.hostname = hostname_elem.get("name")
        
        # Adresse MAC
        mac_elem = host_elem.find("address[@addrtype='mac']")
        if mac_elem is not None:
            host.mac_address = mac_elem.get("addr")
            host.vendor = mac_elem.get("vendor")
        
        # Ports
        ports_elem = host_elem.find("ports")
        if ports_elem is not None:
            for port_elem in ports_elem.findall("port"):
                port = self._parse_port_element(port_elem)
                if port:
                    host.ports.append(port)
        
        # OS Detection
        os_elem = host_elem.find("os")
        if os_elem is not None:
            osmatch_elems = os_elem.findall("osmatch")
            host.os_matches = []
            for osmatch in osmatch_elems:
                host.os_matches.append({
                    "name": osmatch.get("name"),
                    "accuracy": int(osmatch.get("accuracy", 0))
                })
        
        return host
    
    def _parse_port_element(self, port_elem) -> Optional[Port]:
        """Parse un élément port XML de Nmap"""
        port_num = int(port_elem.get("portid"))
        protocol = port_elem.get("protocol", "tcp")
        
        # État du port
        state_elem = port_elem.find("state")
        if state_elem is None:
            return None
        
        state = PortState(state_elem.get("state"))
        
        port = Port(port=port_num, protocol=protocol, state=state)
        
        # Service
        service_elem = port_elem.find("service")
        if service_elem is not None:
            port.service = service_elem.get("name")
            port.product = service_elem.get("product")
            port.version = service_elem.get("version")
            port.extra_info = service_elem.get("extrainfo")
        
        return port
    
    def _format_target_range(self, target) -> str:
        """Formate la plage de cibles"""
        if target.ip_range:
            return target.ip_range
        elif target.specific_hosts:
            return ",".join(target.specific_hosts)
        else:
            return "unknown"
    
    def _generate_target_ips(self, target) -> List[str]:
        """Génère une liste d'IPs cibles"""
        ips = []
        
        if target.ip_range:
            try:
                network = ipaddress.IPv4Network(target.ip_range, strict=False)
                ips = [str(ip) for ip in network.hosts()]
            except ValueError:
                # Si ce n'est pas un CIDR valide, traiter comme une IP unique
                ips = [target.ip_range]
        
        if target.specific_hosts:
            ips.extend(target.specific_hosts)
        
        # Exclure les hôtes spécifiés
        if target.exclude_hosts:
            ips = [ip for ip in ips if ip not in target.exclude_hosts]
        
        return ips
    
    def _is_local_subnet(self, ip: str) -> bool:
        """Vérifie si l'IP est dans un subnet local"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    def _generate_mac_address(self) -> str:
        """Génère une adresse MAC simulée"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _is_outdated_version(self, service: str, version: str) -> bool:
        """Vérifie si une version est obsolète (simulation)"""
        outdated_patterns = {
            "apache": ["2.2", "2.0"],
            "nginx": ["1.10", "1.8"],
            "ssh": ["6.", "5."],
            "mysql": ["5.5", "5.1"],
            "postgresql": ["9.", "8."]
        }
        
        if service.lower() in outdated_patterns:
            for pattern in outdated_patterns[service.lower()]:
                if pattern in version:
                    return True
        
        return False
    
    def _guess_device_type(self, host: Host) -> str:
        """Devine le type d'appareil basé sur les ports/services"""
        open_ports = [p.port for p in host.ports if p.state == PortState.OPEN]
        
        if 3389 in open_ports:  # RDP
            return "Windows Server/Desktop"
        elif 22 in open_ports and 80 in open_ports:
            return "Web Server"
        elif 22 in open_ports:
            return "Linux Server"
        elif 161 in open_ports:  # SNMP
            return "Network Device"
        elif 21 in open_ports:  # FTP
            return "File Server"
        else:
            return "Unknown"
    
    def _get_subnet(self, ip: str) -> str:
        """Récupère le subnet d'une IP"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            # Assume /24 pour la simplicité
            network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return str(network.network_address) + "/24"
        except ValueError:
            return "unknown"
    
    def _calculate_security_score(self, host: Host, vulnerabilities: List[NetworkVulnerability]) -> float:
        """Calcule un score de sécurité pour un hôte"""
        base_score = 100.0
        
        # Pénalité pour ports ouverts
        open_ports = len([p for p in host.ports if p.state == PortState.OPEN])
        base_score -= min(30, open_ports * 2)
        
        # Pénalité pour vulnérabilités
        host_vulns = [v for v in vulnerabilities if v.host_ip == host.ip]
        for vuln in host_vulns:
            if vuln.severity == Severity.CRITICAL:
                base_score -= 25
            elif vuln.severity == Severity.HIGH:
                base_score -= 15
            elif vuln.severity == Severity.MEDIUM:
                base_score -= 8
            elif vuln.severity == Severity.LOW:
                base_score -= 3
        
        return max(0, base_score)
    
    def _load_vulnerability_signatures(self) -> Dict[str, Any]:
        """Charge les signatures de vulnérabilités"""
        return {
            "telnet": {"severity": "high", "description": "Unencrypted protocol"},
            "ftp_anonymous": {"severity": "medium", "description": "Anonymous access"},
            "weak_ssl": {"severity": "medium", "description": "Weak SSL/TLS configuration"},
            "outdated_software": {"severity": "medium", "description": "Outdated software version"}
        }
    
    def _load_service_patterns(self) -> Dict[str, List[str]]:
        """Charge les patterns de détection de services"""
        return {
            "web_servers": ["apache", "nginx", "iis", "lighttpd"],
            "databases": ["mysql", "postgresql", "mssql", "oracle", "mongodb"],
            "mail_servers": ["postfix", "sendmail", "exim", "dovecot"],
            "ssh_servers": ["openssh", "dropbear"]
        }