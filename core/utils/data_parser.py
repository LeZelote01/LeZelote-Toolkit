"""
Pentest-USB Toolkit - Data Parser
================================

Comprehensive data parsing utilities for XML, JSON, CSV
and various scan result formats.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import json
import xml.etree.ElementTree as ET
import csv
import re
from typing import Dict, List, Any, Optional, Union
from io import StringIO
import pandas as pd
import yaml

from .logging_handler import get_logger
from .error_handler import PentestError


class DataParser:
    """
    Comprehensive data parsing and transformation utilities
    """
    
    def __init__(self):
        """Initialize data parser"""
        self.logger = get_logger(__name__)
    
    def parse_json(self, data: Union[str, dict]) -> Dict[str, Any]:
        """
        Parse JSON data with error handling
        
        Args:
            data: JSON string or dict object
            
        Returns:
            Parsed JSON data as dictionary
        """
        try:
            if isinstance(data, str):
                return json.loads(data)
            elif isinstance(data, dict):
                return data
            else:
                raise PentestError(f"Unsupported JSON data type: {type(data)}")
        except json.JSONDecodeError as e:
            raise PentestError(f"Invalid JSON data: {str(e)}")
    
    def parse_xml(self, xml_data: Union[str, bytes], namespace_map: Optional[Dict[str, str]] = None) -> ET.Element:
        """
        Parse XML data with namespace support
        
        Args:
            xml_data: XML string or bytes
            namespace_map: Namespace prefix mapping
            
        Returns:
            XML Element tree root
        """
        try:
            if isinstance(xml_data, bytes):
                xml_data = xml_data.decode('utf-8')
            
            root = ET.fromstring(xml_data)
            
            # Register namespaces if provided
            if namespace_map:
                for prefix, uri in namespace_map.items():
                    ET.register_namespace(prefix, uri)
            
            return root
            
        except ET.ParseError as e:
            raise PentestError(f"Invalid XML data: {str(e)}")
    
    def parse_csv(self, csv_data: str, delimiter: str = ',', 
                  has_header: bool = True) -> List[Dict[str, str]]:
        """
        Parse CSV data to list of dictionaries
        
        Args:
            csv_data: CSV string data
            delimiter: Field delimiter
            has_header: Whether first row contains headers
            
        Returns:
            List of dictionaries with CSV data
        """
        try:
            reader = csv.DictReader(StringIO(csv_data), delimiter=delimiter) if has_header else csv.reader(StringIO(csv_data), delimiter=delimiter)
            
            if has_header:
                return list(reader)
            else:
                # Generate column names if no header
                rows = list(reader)
                if not rows:
                    return []
                
                headers = [f"col_{i}" for i in range(len(rows[0]))]
                return [dict(zip(headers, row)) for row in rows]
                
        except Exception as e:
            raise PentestError(f"Failed to parse CSV data: {str(e)}")
    
    def parse_nmap_xml(self, xml_data: str) -> Dict[str, Any]:
        """
        Parse Nmap XML output
        
        Args:
            xml_data: Nmap XML scan results
            
        Returns:
            Structured scan results
        """
        try:
            root = self.parse_xml(xml_data)
            
            results = {
                'scan_info': {},
                'hosts': [],
                'stats': {}
            }
            
            # Parse scan info
            scaninfo = root.find('scaninfo')
            if scaninfo is not None:
                results['scan_info'] = scaninfo.attrib
            
            # Parse hosts
            for host in root.findall('host'):
                host_data = self._parse_nmap_host(host)
                results['hosts'].append(host_data)
            
            # Parse run stats
            runstats = root.find('runstats')
            if runstats is not None:
                finished = runstats.find('finished')
                if finished is not None:
                    results['stats'] = finished.attrib
            
            return results
            
        except Exception as e:
            raise PentestError(f"Failed to parse Nmap XML: {str(e)}")
    
    def _parse_nmap_host(self, host_elem: ET.Element) -> Dict[str, Any]:
        """Parse individual Nmap host element"""
        host_data = {
            'status': {},
            'addresses': {},
            'hostnames': [],
            'ports': [],
            'os': {},
            'scripts': []
        }
        
        # Host status
        status = host_elem.find('status')
        if status is not None:
            host_data['status'] = status.attrib
        
        # Addresses
        for addr in host_elem.findall('address'):
            addr_type = addr.get('addrtype', 'unknown')
            host_data['addresses'][addr_type] = addr.get('addr')
        
        # Hostnames
        hostnames = host_elem.find('hostnames')
        if hostnames is not None:
            for hostname in hostnames.findall('hostname'):
                host_data['hostnames'].append(hostname.attrib)
        
        # Ports
        ports = host_elem.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                port_data = self._parse_nmap_port(port)
                host_data['ports'].append(port_data)
        
        # OS detection
        os_elem = host_elem.find('os')
        if os_elem is not None:
            host_data['os'] = self._parse_nmap_os(os_elem)
        
        return host_data
    
    def _parse_nmap_port(self, port_elem: ET.Element) -> Dict[str, Any]:
        """Parse individual Nmap port element"""
        port_data = {
            'protocol': port_elem.get('protocol'),
            'portid': int(port_elem.get('portid')),
            'state': {},
            'service': {},
            'scripts': []
        }
        
        # Port state
        state = port_elem.find('state')
        if state is not None:
            port_data['state'] = state.attrib
        
        # Service info
        service = port_elem.find('service')
        if service is not None:
            port_data['service'] = service.attrib
        
        # Scripts
        for script in port_elem.findall('script'):
            script_data = {
                'id': script.get('id'),
                'output': script.get('output'),
                'elements': {}
            }
            
            # Script elements
            for elem in script.findall('elem'):
                key = elem.get('key', 'value')
                script_data['elements'][key] = elem.text
            
            port_data['scripts'].append(script_data)
        
        return port_data
    
    def _parse_nmap_os(self, os_elem: ET.Element) -> Dict[str, Any]:
        """Parse Nmap OS detection results"""
        os_data = {
            'matches': [],
            'classes': [],
            'fingerprints': []
        }
        
        # OS matches
        for osmatch in os_elem.findall('osmatch'):
            match_data = osmatch.attrib.copy()
            match_data['osclass'] = []
            
            for osclass in osmatch.findall('osclass'):
                match_data['osclass'].append(osclass.attrib)
            
            os_data['matches'].append(match_data)
        
        return os_data
    
    def parse_burp_xml(self, xml_data: str) -> Dict[str, Any]:
        """
        Parse Burp Suite XML export
        
        Args:
            xml_data: Burp XML export data
            
        Returns:
            Structured Burp results
        """
        try:
            root = self.parse_xml(xml_data)
            
            results = {
                'issues': []
            }
            
            # Parse issues
            for issue in root.findall('.//issue'):
                issue_data = {
                    'name': self._get_xml_text(issue, 'name'),
                    'type': self._get_xml_text(issue, 'type'),
                    'severity': self._get_xml_text(issue, 'severity'),
                    'confidence': self._get_xml_text(issue, 'confidence'),
                    'host': self._get_xml_text(issue, 'host'),
                    'path': self._get_xml_text(issue, 'path'),
                    'description': self._get_xml_text(issue, 'issueDescription'),
                    'detail': self._get_xml_text(issue, 'issueDetail'),
                    'background': self._get_xml_text(issue, 'issueBackground'),
                    'remediation': self._get_xml_text(issue, 'remediationBackground'),
                    'references': self._get_xml_text(issue, 'references')
                }
                
                results['issues'].append(issue_data)
            
            return results
            
        except Exception as e:
            raise PentestError(f"Failed to parse Burp XML: {str(e)}")
    
    def _get_xml_text(self, parent: ET.Element, tag: str, default: str = "") -> str:
        """Get text content from XML element"""
        elem = parent.find(tag)
        return elem.text if elem is not None and elem.text else default
    
    def parse_nuclei_json(self, json_data: str) -> Dict[str, Any]:
        """
        Parse Nuclei JSON output
        
        Args:
            json_data: Nuclei JSON results
            
        Returns:
            Structured Nuclei results
        """
        try:
            # Nuclei outputs one JSON object per line
            results = {
                'findings': []
            }
            
            for line in json_data.strip().split('\n'):
                if line.strip():
                    finding = json.loads(line)
                    results['findings'].append(finding)
            
            return results
            
        except Exception as e:
            raise PentestError(f"Failed to parse Nuclei JSON: {str(e)}")
    
    def normalize_vulnerability_data(self, vuln_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Normalize vulnerability data from different sources
        
        Args:
            vuln_data: Raw vulnerability data
            source: Source tool (nmap, burp, nuclei, etc.)
            
        Returns:
            Normalized vulnerability data
        """
        normalized = {
            'id': '',
            'title': '',
            'description': '',
            'severity': 'unknown',
            'confidence': 'unknown',
            'cvss_score': 0.0,
            'cve_ids': [],
            'target': {
                'host': '',
                'port': None,
                'protocol': '',
                'service': '',
                'url': ''
            },
            'evidence': {},
            'remediation': '',
            'references': [],
            'source': source,
            'timestamp': ''
        }
        
        if source == 'nmap':
            normalized.update(self._normalize_nmap_vuln(vuln_data))
        elif source == 'burp':
            normalized.update(self._normalize_burp_vuln(vuln_data))
        elif source == 'nuclei':
            normalized.update(self._normalize_nuclei_vuln(vuln_data))
        
        return normalized
    
    def _normalize_nmap_vuln(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Nmap vulnerability data"""
        return {
            'id': vuln_data.get('script_id', ''),
            'title': vuln_data.get('script_output', '').split('\n')[0][:100],
            'description': vuln_data.get('script_output', ''),
            'target': {
                'host': vuln_data.get('host', ''),
                'port': vuln_data.get('port', 0),
                'protocol': vuln_data.get('protocol', ''),
                'service': vuln_data.get('service', '')
            }
        }
    
    def _normalize_burp_vuln(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Burp Suite vulnerability data"""
        severity_map = {
            'High': 'high',
            'Medium': 'medium', 
            'Low': 'low',
            'Information': 'info'
        }
        
        return {
            'id': vuln_data.get('type', ''),
            'title': vuln_data.get('name', ''),
            'description': vuln_data.get('description', ''),
            'severity': severity_map.get(vuln_data.get('severity'), 'unknown'),
            'confidence': vuln_data.get('confidence', '').lower(),
            'target': {
                'host': vuln_data.get('host', ''),
                'url': vuln_data.get('path', '')
            },
            'remediation': vuln_data.get('remediation', '')
        }
    
    def _normalize_nuclei_vuln(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Nuclei vulnerability data"""
        info = vuln_data.get('info', {})
        
        return {
            'id': vuln_data.get('template-id', ''),
            'title': info.get('name', ''),
            'description': info.get('description', ''),
            'severity': info.get('severity', 'unknown').lower(),
            'target': {
                'url': vuln_data.get('matched-at', ''),
                'host': vuln_data.get('host', '')
            },
            'evidence': vuln_data.get('extracted-results', []),
            'references': info.get('reference', [])
        }
    
    def extract_ips_from_text(self, text: str) -> List[str]:
        """
        Extract IP addresses from text using regex
        
        Args:
            text: Text to search for IP addresses
            
        Returns:
            List of found IP addresses
        """
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        matches = re.findall(ip_pattern, text)
        
        # Validate and filter IPs
        valid_ips = []
        for ip in matches:
            try:
                parts = ip.split('.')
                if all(0 <= int(part) <= 255 for part in parts):
                    valid_ips.append(ip)
            except ValueError:
                continue
        
        return list(set(valid_ips))  # Remove duplicates
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from text using regex
        
        Args:
            text: Text to search for URLs
            
        Returns:
            List of found URLs
        """
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        matches = re.findall(url_pattern, text, re.IGNORECASE)
        
        return list(set(matches))  # Remove duplicates
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """
        Extract email addresses from text using regex
        
        Args:
            text: Text to search for email addresses
            
        Returns:
            List of found email addresses
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        return list(set(matches))  # Remove duplicates
    
    def convert_to_csv(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Convert list of dictionaries to CSV format
        
        Args:
            data: List of dictionaries to convert
            filename: Optional filename to write CSV
            
        Returns:
            CSV string
        """
        if not data:
            return ""
        
        try:
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            csv_content = output.getvalue()
            output.close()
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    f.write(csv_content)
            
            return csv_content
            
        except Exception as e:
            raise PentestError(f"Failed to convert to CSV: {str(e)}")
    
    def flatten_dict(self, nested_dict: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary structure
        
        Args:
            nested_dict: Dictionary with nested structure
            separator: String to separate nested keys
            
        Returns:
            Flattened dictionary
        """
        def _flatten(obj, parent_key='', sep=separator):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    items.extend(_flatten(v, new_key, sep=sep).items())
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                    items.extend(_flatten(v, new_key, sep=sep).items())
            else:
                return {parent_key: obj}
            
            return dict(items)
        
        return _flatten(nested_dict)