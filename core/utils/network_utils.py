"""
Pentest-USB Toolkit - Network Utilities
======================================

Network utility functions for IP validation, DNS resolution,
port scanning utilities, and network reconnaissance helpers.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import socket
import ipaddress
import urllib.parse
from typing import List, Dict, Tuple, Optional, Union
import dns.resolver
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_handler import get_logger
from .error_handler import PentestError, NetworkError


class NetworkUtils:
    """
    Comprehensive network utilities for pentesting operations
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize network utilities
        
        Args:
            timeout: Default timeout for network operations
        """
        self.timeout = timeout
        self.logger = get_logger(__name__)
        
        # Setup requests session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def validate_ip(self, ip: str) -> bool:
        """
        Validate IP address format
        
        Args:
            ip: IP address string to validate
            
        Returns:
            bool: True if valid IP address
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def validate_network(self, network: str) -> bool:
        """
        Validate network CIDR format
        
        Args:
            network: Network string (e.g., "192.168.1.0/24")
            
        Returns:
            bool: True if valid network format
        """
        try:
            ipaddress.ip_network(network, strict=False)
            return True
        except ValueError:
            return False
    
    def expand_network(self, network: str) -> List[str]:
        """
        Expand network CIDR to list of IP addresses
        
        Args:
            network: Network in CIDR format
            
        Returns:
            List of IP addresses in the network
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            
            # Limit to reasonable size to prevent memory issues
            if net.num_addresses > 65536:  # /16 for IPv4
                raise PentestError(f"Network {network} too large (>{65536} hosts)")
            
            return [str(ip) for ip in net.hosts()]
            
        except ValueError as e:
            raise NetworkError(f"Invalid network format: {network} - {str(e)}")
    
    def resolve_hostname(self, hostname: str, record_type: str = 'A') -> List[str]:
        """
        Resolve hostname to IP addresses
        
        Args:
            hostname: Hostname to resolve
            record_type: DNS record type (A, AAAA, CNAME, MX, etc.)
            
        Returns:
            List of resolved addresses
        """
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            
            answers = resolver.resolve(hostname, record_type)
            
            if record_type in ['A', 'AAAA']:
                return [str(answer) for answer in answers]
            elif record_type == 'MX':
                return [f"{answer.preference} {answer.exchange}" for answer in answers]
            elif record_type == 'CNAME':
                return [str(answer.target) for answer in answers]
            else:
                return [str(answer) for answer in answers]
                
        except dns.exception.DNSException as e:
            raise NetworkError(f"DNS resolution failed for {hostname}: {str(e)}", hostname)
    
    def reverse_dns(self, ip: str) -> Optional[str]:
        """
        Perform reverse DNS lookup
        
        Args:
            ip: IP address to resolve
            
        Returns:
            Hostname or None if resolution fails
        """
        try:
            if not self.validate_ip(ip):
                raise NetworkError(f"Invalid IP address: {ip}")
            
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
            
        except (socket.herror, socket.gaierror):
            return None
        except Exception as e:
            self.logger.warning(f"Reverse DNS failed for {ip}: {str(e)}")
            return None
    
    def check_port(self, host: str, port: int, protocol: str = 'tcp') -> bool:
        """
        Check if a specific port is open on a host
        
        Args:
            host: Target hostname or IP
            port: Port number to check
            protocol: Protocol (tcp/udp)
            
        Returns:
            bool: True if port is open
        """
        try:
            if protocol.lower() == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                
                result = sock.connect_ex((host, port))
                sock.close()
                
                return result == 0
            
            elif protocol.lower() == 'udp':
                # UDP port checking is more complex and less reliable
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                
                try:
                    sock.sendto(b'', (host, port))
                    sock.recv(1024)
                    return True
                except socket.timeout:
                    # UDP timeout might mean port is open but no response
                    return True
                except socket.error:
                    return False
                finally:
                    sock.close()
            
            else:
                raise NetworkError(f"Unsupported protocol: {protocol}")
                
        except Exception as e:
            self.logger.debug(f"Port check failed for {host}:{port} - {str(e)}")
            return False
    
    def port_scan_range(self, host: str, start_port: int, end_port: int, 
                       protocol: str = 'tcp') -> List[int]:
        """
        Scan a range of ports on a host
        
        Args:
            host: Target hostname or IP
            start_port: Starting port number
            end_port: Ending port number
            protocol: Protocol (tcp/udp)
            
        Returns:
            List of open ports
        """
        open_ports = []
        
        self.logger.info(f"Scanning ports {start_port}-{end_port} on {host}")
        
        for port in range(start_port, end_port + 1):
            if self.check_port(host, port, protocol):
                open_ports.append(port)
                self.logger.debug(f"Port {port}/{protocol} open on {host}")
        
        return open_ports
    
    def get_common_ports(self) -> Dict[str, List[int]]:
        """
        Get dictionary of common ports by service category
        
        Returns:
            Dict mapping categories to port lists
        """
        return {
            'web': [80, 443, 8080, 8443, 8000, 8001, 3000, 5000],
            'ftp': [21, 990, 22],
            'mail': [25, 110, 143, 993, 995, 587],
            'database': [1433, 1521, 3306, 5432, 6379, 27017],
            'remote': [22, 23, 3389, 5985, 5986],
            'dns': [53],
            'dhcp': [67, 68],
            'snmp': [161, 162],
            'ldap': [389, 636],
            'smb': [139, 445],
            'nfs': [111, 2049],
            'top_100': [
                7, 9, 13, 21, 22, 23, 25, 26, 37, 53, 79, 80, 81, 88, 106, 110, 111,
                113, 119, 135, 139, 143, 144, 179, 199, 389, 427, 443, 444, 445, 465,
                513, 514, 515, 543, 544, 548, 554, 587, 631, 646, 873, 990, 993, 995,
                1025, 1026, 1027, 1028, 1029, 1110, 1433, 1720, 1723, 1755, 1900, 2000,
                2001, 2049, 2121, 2717, 3000, 3128, 3306, 3389, 3986, 4899, 5000, 5009,
                5051, 5060, 5101, 5190, 5357, 5432, 5631, 5666, 5800, 5900, 6000, 6001,
                6646, 7070, 8000, 8008, 8009, 8080, 8081, 8443, 8888, 9100, 9999, 10000,
                32768, 49152, 49153, 49154, 49155, 49156, 49157
            ]
        }
    
    def get_local_ip(self) -> str:
        """
        Get local IP address
        
        Returns:
            Local IP address string
        """
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def get_public_ip(self) -> Optional[str]:
        """
        Get public IP address using external service
        
        Returns:
            Public IP address or None if failed
        """
        services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ident.me"
        ]
        
        for service in services:
            try:
                response = self.session.get(service, timeout=self.timeout)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self.validate_ip(ip):
                        return ip
            except Exception as e:
                self.logger.debug(f"Failed to get public IP from {service}: {str(e)}")
        
        return None
    
    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse URL into components
        
        Args:
            url: URL to parse
            
        Returns:
            Dict with URL components
        """
        try:
            parsed = urllib.parse.urlparse(url)
            
            return {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'hostname': parsed.hostname,
                'port': parsed.port,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'username': parsed.username,
                'password': parsed.password
            }
        except Exception as e:
            raise NetworkError(f"Invalid URL format: {url} - {str(e)}")
    
    def build_url(self, scheme: str, host: str, port: Optional[int] = None, 
                  path: str = "", params: Optional[Dict[str, str]] = None) -> str:
        """
        Build URL from components
        
        Args:
            scheme: URL scheme (http, https)
            host: Hostname or IP
            port: Port number (optional)
            path: URL path
            params: Query parameters
            
        Returns:
            Complete URL string
        """
        try:
            if port:
                netloc = f"{host}:{port}"
            else:
                netloc = host
            
            query = urllib.parse.urlencode(params or {})
            
            return urllib.parse.urlunparse((
                scheme, netloc, path, "", query, ""
            ))
        except Exception as e:
            raise NetworkError(f"Failed to build URL: {str(e)}")
    
    def is_private_ip(self, ip: str) -> bool:
        """
        Check if IP address is in private range
        
        Args:
            ip: IP address to check
            
        Returns:
            bool: True if IP is private
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    def get_network_info(self, ip: str) -> Dict[str, str]:
        """
        Get network information for IP address
        
        Args:
            ip: IP address to analyze
            
        Returns:
            Dict with network information
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            return {
                'ip': str(ip_obj),
                'version': f"IPv{ip_obj.version}",
                'is_private': ip_obj.is_private,
                'is_multicast': ip_obj.is_multicast,
                'is_loopback': ip_obj.is_loopback,
                'is_link_local': ip_obj.is_link_local,
                'reverse_dns': self.reverse_dns(ip)
            }
        except ValueError as e:
            raise NetworkError(f"Invalid IP address: {ip} - {str(e)}")


class NetworkValidator:
    """
    Network validation utilities for input validation and sanitization
    """
    
    def __init__(self):
        """Initialize NetworkValidator"""
        self.logger = get_logger(__name__)
        self.network_utils = NetworkUtils()
    
    def validate_target(self, target: str) -> bool:
        """
        Validate if target is a valid IP, hostname or network range
        
        Args:
            target: Target to validate
            
        Returns:
            bool: True if valid target
        """
        try:
            # Try IP address
            if self.network_utils.validate_ip(target):
                return True
            
            # Try hostname
            if self.network_utils.validate_hostname(target):
                return True
            
            # Try network range
            if '/' in target:
                try:
                    ipaddress.ip_network(target, strict=False)
                    return True
                except ValueError:
                    pass
            
            return False
        except Exception as e:
            self.logger.error(f"Target validation failed: {e}")
            return False
    
    def sanitize_target(self, target: str) -> str:
        """
        Sanitize target input
        
        Args:
            target: Raw target input
            
        Returns:
            str: Sanitized target
        """
        # Remove whitespace
        target = target.strip()
        
        # Convert to lowercase for hostnames
        if not self.network_utils.validate_ip(target):
            target = target.lower()
        
        return target
    
    def is_valid_port_range(self, port_range: str) -> bool:
        """
        Validate port range string
        
        Args:
            port_range: Port range (e.g., "80", "1-1000", "80,443,8080")
            
        Returns:
            bool: True if valid port range
        """
        try:
            # Single port
            if port_range.isdigit():
                port = int(port_range)
                return 1 <= port <= 65535
            
            # Port range
            if '-' in port_range:
                start, end = port_range.split('-', 1)
                start_port = int(start.strip())
                end_port = int(end.strip())
                return (1 <= start_port <= 65535 and 
                       1 <= end_port <= 65535 and 
                       start_port <= end_port)
            
            # Comma-separated ports
            if ',' in port_range:
                ports = port_range.split(',')
                for port in ports:
                    if not self.is_valid_port_range(port.strip()):
                        return False
                return True
            
            return False
        except (ValueError, AttributeError):
            return False