"""
Pentest-USB Toolkit - Nessus API Interface
==========================================

Python interface to Tenable Nessus for vulnerability scanning.
Integrates Nessus with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import requests
import time
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


class NessusAPI:
    """
    Tenable Nessus API interface for vulnerability scanning
    """
    
    def __init__(self, server_url: str, username: str = None, password: str = None):
        """Initialize Nessus API"""
        self.logger = get_logger(__name__)
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
        # Disable SSL warnings for self-signed certificates
        requests.urllib3.disable_warnings()
        self.session.verify = False
        
        self.logger.info("NessusAPI initialized successfully")
    
    def login(self) -> bool:
        """Authenticate with Nessus server"""
        try:
            url = urljoin(self.server_url, '/session')
            data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get('token')
            
            if self.token:
                self.session.headers.update({'X-Cookie': f'token={self.token}'})
                self.logger.info("Successfully authenticated with Nessus")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Nessus login failed: {str(e)}")
            return False
    
    def logout(self):
        """Logout from Nessus server"""
        try:
            url = urljoin(self.server_url, '/session')
            self.session.delete(url, timeout=10)
            self.token = None
            self.logger.info("Logged out from Nessus")
        except:
            pass
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to Nessus"""
        try:
            url = urljoin(self.server_url, endpoint)
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise PentestError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise PentestError(f"Nessus API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise PentestError(f"Failed to parse Nessus response: {str(e)}")
    
    def get_scan_templates(self) -> List[Dict[str, Any]]:
        """Get available scan templates"""
        try:
            response = self._make_request('/editor/scan/templates')
            return response.get('templates', [])
        except Exception as e:
            self.logger.error(f"Failed to get scan templates: {str(e)}")
            return []
    
    def create_scan(self, name: str, targets: str, template_uuid: str = None) -> Dict[str, Any]:
        """
        Create new scan
        
        Args:
            name: Scan name
            targets: Target IPs/hostnames (comma-separated)
            template_uuid: Template UUID (uses basic network scan if None)
            
        Returns:
            Scan creation result
        """
        try:
            # Use basic network scan template if none specified
            if not template_uuid:
                templates = self.get_scan_templates()
                basic_template = next((t for t in templates if 'basic' in t.get('title', '').lower()), None)
                template_uuid = basic_template.get('uuid') if basic_template else None
                
                if not template_uuid:
                    raise PentestError("No suitable scan template found")
            
            scan_config = {
                'uuid': template_uuid,
                'settings': {
                    'name': name,
                    'description': f'Scan created by Pentest-USB Toolkit',
                    'text_targets': targets,
                    'launch_now': False
                }
            }
            
            response = self._make_request('/scans', 'POST', scan_config)
            
            self.logger.info(f"Created Nessus scan: {name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Scan creation failed: {str(e)}")
            raise PentestError(f"Failed to create scan: {str(e)}")
    
    def launch_scan(self, scan_id: int) -> Dict[str, Any]:
        """Launch existing scan"""
        try:
            response = self._make_request(f'/scans/{scan_id}/launch', 'POST')
            self.logger.info(f"Launched scan: {scan_id}")
            return response
        except Exception as e:
            self.logger.error(f"Scan launch failed: {str(e)}")
            raise PentestError(f"Failed to launch scan: {str(e)}")
    
    def get_scan_status(self, scan_id: int) -> Dict[str, Any]:
        """Get scan status"""
        try:
            response = self._make_request(f'/scans/{scan_id}')
            return response.get('info', {})
        except Exception as e:
            self.logger.error(f"Failed to get scan status: {str(e)}")
            return {}
    
    def wait_for_scan_completion(self, scan_id: int, timeout: int = 3600) -> bool:
        """Wait for scan to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_info = self.get_scan_status(scan_id)
            status = status_info.get('status')
            
            if status == 'completed':
                self.logger.info(f"Scan {scan_id} completed successfully")
                return True
            elif status == 'canceled' or status == 'aborted':
                self.logger.warning(f"Scan {scan_id} was {status}")
                return False
            
            self.logger.info(f"Scan {scan_id} status: {status}")
            time.sleep(30)
        
        self.logger.warning(f"Scan {scan_id} timeout after {timeout} seconds")
        return False
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Get scan results"""
        try:
            response = self._make_request(f'/scans/{scan_id}')
            
            # Process vulnerabilities
            vulnerabilities = response.get('vulnerabilities', [])
            hosts = response.get('hosts', [])
            
            # Categorize vulnerabilities by severity
            vuln_summary = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 0)
                if severity == 4:
                    vuln_summary['critical'] += 1
                elif severity == 3:
                    vuln_summary['high'] += 1
                elif severity == 2:
                    vuln_summary['medium'] += 1
                elif severity == 1:
                    vuln_summary['low'] += 1
                else:
                    vuln_summary['info'] += 1
            
            return {
                'scan_id': scan_id,
                'scan_info': response.get('info', {}),
                'hosts': hosts,
                'vulnerabilities': vulnerabilities,
                'summary': vuln_summary
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get scan results: {str(e)}")
            raise PentestError(f"Failed to get scan results: {str(e)}")
    
    def export_scan(self, scan_id: int, format_type: str = 'nessus') -> Dict[str, Any]:
        """
        Export scan results
        
        Args:
            scan_id: Scan ID
            format_type: Export format (nessus, pdf, html, csv, db)
            
        Returns:
            Export result with file token
        """
        try:
            export_config = {
                'format': format_type
            }
            
            response = self._make_request(f'/scans/{scan_id}/export', 'POST', export_config)
            
            file_token = response.get('token')
            if not file_token:
                raise PentestError("Failed to get export token")
            
            # Wait for export to be ready
            while True:
                status_response = self._make_request(f'/scans/{scan_id}/export/{file_token}/status')
                status = status_response.get('status')
                
                if status == 'ready':
                    break
                elif status == 'error':
                    raise PentestError("Export failed")
                
                time.sleep(5)
            
            return {
                'scan_id': scan_id,
                'file_token': file_token,
                'format': format_type,
                'status': 'ready'
            }
            
        except Exception as e:
            self.logger.error(f"Scan export failed: {str(e)}")
            raise PentestError(f"Failed to export scan: {str(e)}")
    
    def download_scan(self, scan_id: int, file_token: str, output_path: str) -> bool:
        """Download exported scan file"""
        try:
            url = f'/scans/{scan_id}/export/{file_token}/download'
            
            response = self.session.get(urljoin(self.server_url, url), stream=True, timeout=300)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded scan results to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            return False
    
    def scan_and_report(self, name: str, targets: str, output_path: str = None) -> Dict[str, Any]:
        """
        Complete scan workflow: create, launch, wait, and get results
        
        Args:
            name: Scan name
            targets: Target IPs/hostnames
            output_path: Optional file path for exported results
            
        Returns:
            Complete scan results
        """
        try:
            self.logger.info(f"Starting comprehensive Nessus scan: {name}")
            
            # Step 1: Create scan
            scan_response = self.create_scan(name, targets)
            scan_id = scan_response.get('scan', {}).get('id')
            
            if not scan_id:
                raise PentestError("Failed to create scan")
            
            # Step 2: Launch scan
            self.launch_scan(scan_id)
            
            # Step 3: Wait for completion
            if not self.wait_for_scan_completion(scan_id):
                raise PentestError("Scan did not complete successfully")
            
            # Step 4: Get results
            results = self.get_scan_results(scan_id)
            
            # Step 5: Export if requested
            if output_path:
                export_result = self.export_scan(scan_id, 'nessus')
                self.download_scan(scan_id, export_result['file_token'], output_path)
                results['exported_file'] = output_path
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive scan failed: {str(e)}")
            raise PentestError(f"Nessus scan failed: {str(e)}")