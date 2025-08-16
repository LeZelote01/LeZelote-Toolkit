"""
Pentest-USB Toolkit - Nmap API Interface
========================================

Python interface to Nmap for network scanning and enumeration.
Integrates Nmap with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError
from ..utils.network_utils import NetworkValidator


class NmapAPI:
    """
    Nmap API interface for network scanning
    """
    
    def __init__(self, nmap_path: Optional[str] = None):
        """Initialize Nmap API"""
        self.logger = get_logger(__name__)
        self.nmap_path = nmap_path or self._find_nmap()
        self.validator = NetworkValidator()
        
        # Verify Nmap installation
        self._verify_installation()
        
        self.logger.info("NmapAPI initialized successfully")
    
    def _find_nmap(self) -> str:
        """Find Nmap executable"""
        import shutil
        nmap_path = shutil.which('nmap')
        if not nmap_path:
            # Try toolkit binaries
            for path in ['./tools/binaries/nmap', './tools/binaries/windows/nmap.exe']:
                if Path(path).exists():
                    return str(Path(path).absolute())
        return nmap_path or 'nmap'
    
    def _verify_installation(self):
        """Verify Nmap installation"""
        try:
            result = subprocess.run([self.nmap_path, '--version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise PentestError("Nmap not properly installed")
        except Exception as e:
            raise PentestError(f"Nmap verification failed: {str(e)}")
    
    def scan(self, target: str, arguments: str = "-sV -sC", 
             output_format: str = "xml") -> Dict[str, Any]:
        """
        Execute Nmap scan
        
        Args:
            target: Target IP, hostname or network range
            arguments: Nmap arguments
            output_format: Output format (xml, json, normal)
            
        Returns:
            Parsed scan results
        """
        try:
            # Validate target
            if not self.validator.validate_target(target):
                raise PentestError(f"Invalid target: {target}")
            
            # Prepare command
            cmd = [self.nmap_path]
            cmd.extend(arguments.split())
            
            if output_format == "xml":
                cmd.append("-oX")
                cmd.append("-")  # Output to stdout
            
            cmd.append(target)
            
            self.logger.info(f"Starting Nmap scan: {' '.join(cmd)}")
            
            # Execute scan
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                raise PentestError(f"Nmap scan failed: {result.stderr}")
            
            # Parse results
            if output_format == "xml":
                return self._parse_xml_output(result.stdout)
            else:
                return {"raw_output": result.stdout}
                
        except subprocess.TimeoutExpired:
            raise PentestError("Nmap scan timeout")
        except Exception as e:
            self.logger.error(f"Nmap scan error: {str(e)}")
            raise PentestError(f"Nmap scan failed: {str(e)}")
    
    def _parse_xml_output(self, xml_output: str) -> Dict[str, Any]:
        """Parse Nmap XML output"""
        try:
            root = ET.fromstring(xml_output)
            results = {
                "scan_info": {},
                "hosts": [],
                "summary": {}
            }
            
            # Parse scan info
            scaninfo = root.find('scaninfo')
            if scaninfo is not None:
                results["scan_info"] = dict(scaninfo.attrib)
            
            # Parse hosts
            for host in root.findall('host'):
                host_data = self._parse_host(host)
                if host_data:
                    results["hosts"].append(host_data)
            
            # Parse run stats
            runstats = root.find('runstats')
            if runstats is not None:
                finished = runstats.find('finished')
                if finished is not None:
                    results["summary"] = dict(finished.attrib)
            
            return results
            
        except ET.ParseError as e:
            raise PentestError(f"Failed to parse Nmap XML: {str(e)}")
    
    def _parse_host(self, host_element) -> Dict[str, Any]:
        """Parse individual host from XML"""
        host_data = {
            "addresses": [],
            "hostnames": [],
            "status": {},
            "ports": [],
            "os": {}
        }
        
        # Status
        status = host_element.find('status')
        if status is not None:
            host_data["status"] = dict(status.attrib)
        
        # Addresses
        for address in host_element.findall('address'):
            host_data["addresses"].append(dict(address.attrib))
        
        # Hostnames
        hostnames = host_element.find('hostnames')
        if hostnames is not None:
            for hostname in hostnames.findall('hostname'):
                host_data["hostnames"].append(dict(hostname.attrib))
        
        # Ports
        ports = host_element.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                port_data = dict(port.attrib)
                
                # Service info
                service = port.find('service')
                if service is not None:
                    port_data["service"] = dict(service.attrib)
                
                # State info
                state = port.find('state')
                if state is not None:
                    port_data["state"] = dict(state.attrib)
                
                host_data["ports"].append(port_data)
        
        # OS detection
        os_element = host_element.find('os')
        if os_element is not None:
            osmatch = os_element.find('osmatch')
            if osmatch is not None:
                host_data["os"] = dict(osmatch.attrib)
        
        return host_data
    
    def ping_sweep(self, network: str) -> Dict[str, Any]:
        """Perform ping sweep on network"""
        return self.scan(network, "-sn")
    
    def port_scan(self, target: str, ports: str = "1-1000") -> Dict[str, Any]:
        """Perform port scan"""
        return self.scan(target, f"-p {ports} -sV")
    
    def service_detection(self, target: str) -> Dict[str, Any]:
        """Perform service version detection"""
        return self.scan(target, "-sV -sC")
    
    def os_detection(self, target: str) -> Dict[str, Any]:
        """Perform OS detection"""
        return self.scan(target, "-O")
    
    def stealth_scan(self, target: str) -> Dict[str, Any]:
        """Perform stealth SYN scan"""
        return self.scan(target, "-sS -T2")
    
    def vulnerability_scan(self, target: str) -> Dict[str, Any]:
        """Perform vulnerability scan with NSE scripts"""
        return self.scan(target, "--script vuln")