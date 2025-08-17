"""
Pentest-USB Toolkit - OWASP ZAP API Interface
===========================================

Python interface to OWASP ZAP for web application security testing.
Integrates ZAP with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import requests
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


class ZapAPI:
    """
    OWASP ZAP API interface for web application scanning
    """
    
    def __init__(self, zap_host: str = "127.0.0.1", zap_port: int = 8080, 
                 api_key: Optional[str] = None):
        """Initialize ZAP API"""
        self.logger = get_logger(__name__)
        self.zap_host = zap_host
        self.zap_port = zap_port
        self.api_key = api_key
        self.base_url = f"http://{zap_host}:{zap_port}"
        
        # Default session
        self.session = requests.Session()
        
        self.logger.info("ZapAPI initialized successfully")
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to ZAP"""
        try:
            url = f"{self.base_url}/JSON/{endpoint}"
            
            # Add API key if configured
            if self.api_key:
                params = params or {}
                params['apikey'] = self.api_key
            
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            else:
                response = self.session.post(url, data=params, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise PentestError(f"ZAP API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise PentestError(f"Failed to parse ZAP response: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if ZAP is running"""
        try:
            response = self._make_request("core/view/version/")
            return response.get('version') is not None
        except:
            return False
    
    def wait_for_zap(self, timeout: int = 60):
        """Wait for ZAP to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_running():
                self.logger.info("ZAP is ready")
                return True
            time.sleep(2)
        
        raise PentestError("ZAP startup timeout")
    
    def spider_scan(self, target_url: str) -> Dict[str, Any]:
        """
        Perform spider scan on target
        
        Args:
            target_url: Target URL to spider
            
        Returns:
            Spider scan results
        """
        try:
            # Start spider
            response = self._make_request("spider/action/scan/", "POST", {
                'url': target_url,
                'maxChildren': '10',
                'recurse': 'true'
            })
            
            scan_id = response.get('scan')
            if not scan_id:
                raise PentestError("Failed to start spider scan")
            
            self.logger.info(f"Started spider scan: {scan_id}")
            
            # Wait for completion
            while True:
                status_response = self._make_request("spider/view/status/", params={'scanId': scan_id})
                status = int(status_response.get('status', 0))
                
                if status >= 100:
                    break
                
                self.logger.info(f"Spider scan progress: {status}%")
                time.sleep(5)
            
            # Get results
            results_response = self._make_request("spider/view/results/", params={'scanId': scan_id})
            
            return {
                "scan_id": scan_id,
                "status": "completed",
                "urls": results_response.get('results', [])
            }
            
        except Exception as e:
            self.logger.error(f"Spider scan error: {str(e)}")
            raise PentestError(f"Spider scan failed: {str(e)}")
    
    def active_scan(self, target_url: str) -> Dict[str, Any]:
        """
        Perform active scan on target
        
        Args:
            target_url: Target URL to scan
            
        Returns:
            Active scan results
        """
        try:
            # Start active scan
            response = self._make_request("ascan/action/scan/", "POST", {
                'url': target_url,
                'recurse': 'true',
                'inScopeOnly': 'false'
            })
            
            scan_id = response.get('scan')
            if not scan_id:
                raise PentestError("Failed to start active scan")
            
            self.logger.info(f"Started active scan: {scan_id}")
            
            # Wait for completion
            while True:
                status_response = self._make_request("ascan/view/status/", params={'scanId': scan_id})
                status = int(status_response.get('status', 0))
                
                if status >= 100:
                    break
                
                self.logger.info(f"Active scan progress: {status}%")
                time.sleep(10)
            
            return {
                "scan_id": scan_id,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Active scan error: {str(e)}")
            raise PentestError(f"Active scan failed: {str(e)}")
    
    def get_alerts(self, base_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get security alerts"""
        try:
            params = {}
            if base_url:
                params['baseurl'] = base_url
            
            response = self._make_request("core/view/alerts/", params=params)
            
            alerts = response.get('alerts', [])
            
            # Process and categorize alerts
            processed_alerts = []
            for alert in alerts:
                processed_alert = {
                    "id": alert.get('pluginId'),
                    "name": alert.get('alert'),
                    "risk": alert.get('risk'),
                    "confidence": alert.get('confidence'),
                    "url": alert.get('url'),
                    "param": alert.get('param'),
                    "description": alert.get('description'),
                    "solution": alert.get('solution'),
                    "reference": alert.get('reference'),
                    "evidence": alert.get('evidence')
                }
                processed_alerts.append(processed_alert)
            
            return processed_alerts
            
        except Exception as e:
            self.logger.error(f"Get alerts error: {str(e)}")
            return []
    
    def spider_and_scan(self, target_url: str) -> Dict[str, Any]:
        """
        Perform complete spider + active scan
        
        Args:
            target_url: Target URL
            
        Returns:
            Complete scan results
        """
        try:
            self.logger.info(f"Starting comprehensive scan of {target_url}")
            
            # Step 1: Spider scan
            spider_results = self.spider_scan(target_url)
            
            # Step 2: Active scan
            scan_results = self.active_scan(target_url)
            
            # Step 3: Get alerts
            alerts = self.get_alerts(target_url)
            
            # Step 4: Generate summary
            summary = self._generate_scan_summary(alerts)
            
            return {
                "target": target_url,
                "spider": spider_results,
                "scan": scan_results,
                "alerts": alerts,
                "summary": summary,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive scan error: {str(e)}")
            raise PentestError(f"Comprehensive scan failed: {str(e)}")
    
    def _generate_scan_summary(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scan summary from alerts"""
        summary = {
            "total_alerts": len(alerts),
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "info_risk": 0
        }
        
        for alert in alerts:
            risk = alert.get('risk', '').lower()
            if risk == 'high':
                summary['high_risk'] += 1
            elif risk == 'medium':
                summary['medium_risk'] += 1
            elif risk == 'low':
                summary['low_risk'] += 1
            else:
                summary['info_risk'] += 1
        
        return summary
    
    def export_report(self, format_type: str = "html") -> Dict[str, Any]:
        """Export scan report"""
        try:
            if format_type == "html":
                response = self._make_request("core/other/htmlreport/")
            elif format_type == "xml":
                response = self._make_request("core/other/xmlreport/")
            else:
                raise PentestError(f"Unsupported report format: {format_type}")
            
            return {
                "format": format_type,
                "report": response,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Report export error: {str(e)}")
            raise PentestError(f"Report export failed: {str(e)}")
    
    def shutdown(self):
        """Shutdown ZAP instance"""
        try:
            self._make_request("core/action/shutdown/", "POST")
            self.logger.info("ZAP shutdown initiated")
        except:
            # Ignore shutdown errors
            pass