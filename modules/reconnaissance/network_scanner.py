"""
Pentest-USB Toolkit - Network Scanner Module
===========================================

Network scanning and enumeration using multiple tools.
Orchestrates Nmap, RustScan, and Masscan for comprehensive network discovery.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from ipaddress import ip_network, ip_address

# Fix imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger
from core.utils.error_handler import PentestError
from core.api.nmap_api import NmapAPI


class NetworkScanner:
    """
    Network scanner module for comprehensive network discovery
    """
    
    def __init__(self):
        """Initialize Network Scanner"""
        self.logger = get_logger(__name__)
        self.nmap_api = NmapAPI()
        
        self.logger.info("NetworkScanner module initialized")
    
    def scan_network(self, target: str, profile: str = "default") -> Dict[str, Any]:
        """
        Scan network using specified profile
        
        Args:
            target: Target IP, range, or hostname
            profile: Scan profile (quick, default, comprehensive)
            
        Returns:
            Network scan results
        """
        try:
            self.logger.info(f"Starting network scan: {target} (profile: {profile})")
            
            # Select scan arguments based on profile
            scan_args = self._get_scan_arguments(profile)
            
            # Perform Nmap scan
            nmap_results = self.nmap_api.scan(target, scan_args)
            
            # Process and enrich results
            processed_results = self._process_scan_results(nmap_results)
            
            return {
                'target': target,
                'profile': profile,
                'status': 'completed',
                'results': processed_results,
                'summary': self._generate_summary(processed_results)
            }
            
        except Exception as e:
            self.logger.error(f"Network scan failed: {str(e)}")
            raise PentestError(f"Network scan failed: {str(e)}")
    
    def _get_scan_arguments(self, profile: str) -> str:
        """Get Nmap arguments for scan profile"""
        profiles = {
            'quick': '-sn',  # Ping scan only
            'default': '-sV -sC',  # Service detection + default scripts
            'comprehensive': '-sV -sC -O -A --script vuln',  # Full scan
            'stealth': '-sS -T2 -f'  # Stealth scan
        }
        
        return profiles.get(profile, profiles['default'])
    
    def _process_scan_results(self, nmap_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich Nmap scan results"""
        processed = {
            'hosts': [],
            'services': [],
            'open_ports': [],
            'scan_info': nmap_results.get('scan_info', {})
        }
        
        for host in nmap_results.get('hosts', []):
            if host.get('status', {}).get('state') == 'up':
                processed_host = self._process_host(host)
                processed['hosts'].append(processed_host)
        
        return processed
    
    def _process_host(self, host: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual host data"""
        processed_host = {
            'ip': None,
            'hostnames': [],
            'os': {},
            'ports': [],
            'services': []
        }
        
        # Extract IP address
        for addr in host.get('addresses', []):
            if addr.get('addrtype') == 'ipv4':
                processed_host['ip'] = addr.get('addr')
                break
        
        # Extract hostnames
        processed_host['hostnames'] = [h.get('name') for h in host.get('hostnames', [])]
        
        # Extract OS information
        processed_host['os'] = host.get('os', {})
        
        # Process ports and services
        for port in host.get('ports', []):
            port_info = {
                'port': int(port.get('portid', 0)),
                'protocol': port.get('protocol'),
                'state': port.get('state', {}).get('state'),
                'service': port.get('service', {})
            }
            
            if port_info['state'] == 'open':
                processed_host['ports'].append(port_info)
                
                # Extract service information
                service = port.get('service', {})
                if service.get('name'):
                    service_info = {
                        'name': service.get('name'),
                        'version': service.get('version'),
                        'product': service.get('product'),
                        'port': port_info['port'],
                        'protocol': port_info['protocol']
                    }
                    processed_host['services'].append(service_info)
        
        return processed_host
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {
            'total_hosts': len(results.get('hosts', [])),
            'total_open_ports': 0,
            'services_found': set(),
            'os_detected': set(),
            'common_ports': {}
        }
        
        for host in results.get('hosts', []):
            summary['total_open_ports'] += len(host.get('ports', []))
            
            # Collect services
            for service in host.get('services', []):
                summary['services_found'].add(service.get('name', 'unknown'))
            
            # Collect OS information
            os_info = host.get('os', {})
            if os_info.get('name'):
                summary['os_detected'].add(os_info['name'])
            
            # Count common ports
            for port in host.get('ports', []):
                port_num = port.get('port')
                summary['common_ports'][port_num] = summary['common_ports'].get(port_num, 0) + 1
        
        # Convert sets to lists for JSON serialization
        summary['services_found'] = list(summary['services_found'])
        summary['os_detected'] = list(summary['os_detected'])
        
        return summary
    
    def quick_scan(self, target: str) -> Dict[str, Any]:
        """Perform quick ping scan"""
        return self.scan_network(target, "quick")
    
    def service_scan(self, target: str) -> Dict[str, Any]:
        """Perform service detection scan"""
        return self.scan_network(target, "default")
    
    def comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive scan"""
        return self.scan_network(target, "comprehensive")
    
    def stealth_scan(self, target: str) -> Dict[str, Any]:
        """Perform stealth scan"""
        return self.scan_network(target, "stealth")