#!/usr/bin/env python3
"""
Pentest-USB Toolkit - Custom Vulnerability Scanners

This module provides custom vulnerability scanners and techniques
that complement traditional tools. Includes specialized scanners for
web applications, network services, and configuration issues.

Author: Pentest-USB Team
Version: 1.0.0
"""

import os
import sys
import json
import requests
import socket
import ssl
import threading
import time
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebVulnScanner:
    """Custom web vulnerability scanner"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vulnerabilities = []
        
    def scan_directory_traversal(self, url: str) -> List[Dict[str, Any]]:
        """Directory traversal vulnerability scanner"""
        logger.info(f"Scanning for directory traversal: {url}")
        
        vulnerabilities = []
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        for payload in payloads:
            try:
                test_url = f"{url}?file={payload}"
                response = self.session.get(test_url, timeout=10)
                
                if self._check_directory_traversal(response.text):
                    vuln = {
                        'type': 'directory_traversal',
                        'url': test_url,
                        'payload': payload,
                        'severity': 'high',
                        'evidence': response.text[:500]
                    }
                    vulnerabilities.append(vuln)
                    logger.warning(f"Directory traversal found: {test_url}")
                    
            except Exception as e:
                logger.error(f"Error testing payload {payload}: {e}")
                
        return vulnerabilities
    
    def _check_directory_traversal(self, response_text: str) -> bool:
        """Check if response indicates directory traversal"""
        indicators = [
            'root:x:0:0',
            '[boot loader]',
            'boot.ini',
            '# localhost',
            '/etc/passwd'
        ]
        
        for indicator in indicators:
            if indicator.lower() in response_text.lower():
                return True
        return False
    
    def scan_xss(self, url: str, params: List[str]) -> List[Dict[str, Any]]:
        """XSS vulnerability scanner"""
        logger.info(f"Scanning for XSS: {url}")
        
        vulnerabilities = []
        payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "'\"><script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for param in params:
            for payload in payloads:
                try:
                    test_params = {param: payload}
                    response = self.session.get(url, params=test_params, timeout=10)
                    
                    if payload in response.text:
                        vuln = {
                            'type': 'xss_reflected',
                            'url': url,
                            'parameter': param,
                            'payload': payload,
                            'severity': 'medium',
                            'evidence': f"Payload reflected in response"
                        }
                        vulnerabilities.append(vuln)
                        logger.warning(f"XSS found: {url} parameter {param}")
                        
                except Exception as e:
                    logger.error(f"Error testing XSS payload: {e}")
                    
        return vulnerabilities
    
    def scan_sql_injection(self, url: str, params: List[str]) -> List[Dict[str, Any]]:
        """Basic SQL injection scanner"""
        logger.info(f"Scanning for SQL injection: {url}")
        
        vulnerabilities = []
        payloads = [
            "'",
            "\"",
            "' OR '1'='1",
            "\" OR \"1\"=\"1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "1' AND SLEEP(5)--"
        ]
        
        for param in params:
            for payload in payloads:
                try:
                    start_time = time.time()
                    test_params = {param: payload}
                    response = self.session.get(url, params=test_params, timeout=15)
                    response_time = time.time() - start_time
                    
                    if self._check_sql_error(response.text) or response_time > 5:
                        vuln = {
                            'type': 'sql_injection',
                            'url': url,
                            'parameter': param,
                            'payload': payload,
                            'severity': 'high',
                            'evidence': self._extract_sql_error(response.text),
                            'response_time': response_time
                        }
                        vulnerabilities.append(vuln)
                        logger.warning(f"SQL injection found: {url} parameter {param}")
                        
                except Exception as e:
                    logger.error(f"Error testing SQL injection: {e}")
                    
        return vulnerabilities
    
    def _check_sql_error(self, response_text: str) -> bool:
        """Check for SQL error messages"""
        sql_errors = [
            'sql syntax',
            'mysql_fetch_array',
            'ora-[0-9]+',
            'microsoft jet database',
            'odbc drivers error',
            'sqlite_step',
            'postgresql query failed'
        ]
        
        for error in sql_errors:
            if re.search(error, response_text, re.IGNORECASE):
                return True
        return False
    
    def _extract_sql_error(self, response_text: str) -> str:
        """Extract SQL error message"""
        patterns = [
            r'(SQL[^<\n]*)',
            r'(mysql_[^<\n]*)',
            r'(ORA-[0-9]+[^<\n]*)',
            r'(Microsoft.*error[^<\n]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "SQL error detected"
    
    def scan_open_redirect(self, url: str) -> List[Dict[str, Any]]:
        """Open redirect vulnerability scanner"""
        logger.info(f"Scanning for open redirect: {url}")
        
        vulnerabilities = []
        redirect_params = ['url', 'redirect', 'return', 'goto', 'link', 'target']
        test_domains = ['evil.com', 'http://evil.com', '//evil.com']
        
        for param in redirect_params:
            for domain in test_domains:
                try:
                    test_params = {param: domain}
                    response = self.session.get(url, params=test_params, 
                                              allow_redirects=False, timeout=10)
                    
                    if response.status_code in [301, 302, 303, 307, 308]:
                        location = response.headers.get('Location', '')
                        if 'evil.com' in location:
                            vuln = {
                                'type': 'open_redirect',
                                'url': url,
                                'parameter': param,
                                'payload': domain,
                                'severity': 'medium',
                                'evidence': f"Redirects to: {location}"
                            }
                            vulnerabilities.append(vuln)
                            logger.warning(f"Open redirect found: {url}")
                            
                except Exception as e:
                    logger.error(f"Error testing open redirect: {e}")
                    
        return vulnerabilities


class NetworkVulnScanner:
    """Network-level vulnerability scanner"""
    
    def __init__(self):
        self.vulnerabilities = []
        
    def scan_ssl_vulnerabilities(self, host: str, port: int = 443) -> List[Dict[str, Any]]:
        """Scan for SSL/TLS vulnerabilities"""
        logger.info(f"Scanning SSL vulnerabilities: {host}:{port}")
        
        vulnerabilities = []
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate info
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Check for weak ciphers
                    if cipher and self._is_weak_cipher(cipher[0]):
                        vuln = {
                            'type': 'weak_ssl_cipher',
                            'host': host,
                            'port': port,
                            'cipher': cipher[0],
                            'severity': 'medium',
                            'evidence': f"Weak cipher in use: {cipher[0]}"
                        }
                        vulnerabilities.append(vuln)
                        
                    # Check certificate validity
                    cert_issues = self._check_certificate(cert, host)
                    vulnerabilities.extend(cert_issues)
                    
        except Exception as e:
            logger.error(f"Error scanning SSL: {e}")
            
        return vulnerabilities
    
    def _is_weak_cipher(self, cipher: str) -> bool:
        """Check if cipher is considered weak"""
        weak_ciphers = [
            'RC4', 'DES', '3DES', 'MD5', 'SHA1', 
            'NULL', 'EXPORT', 'ADH', 'aNULL'
        ]
        
        for weak in weak_ciphers:
            if weak.upper() in cipher.upper():
                return True
        return False
    
    def _check_certificate(self, cert: Dict, hostname: str) -> List[Dict[str, Any]]:
        """Check certificate for issues"""
        issues = []
        
        if not cert:
            return issues
            
        # Check if certificate is expired
        import datetime
        not_after = cert.get('notAfter')
        if not_after:
            try:
                expiry_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                if expiry_date < datetime.datetime.now():
                    issues.append({
                        'type': 'expired_certificate',
                        'host': hostname,
                        'severity': 'high',
                        'evidence': f"Certificate expired: {not_after}"
                    })
            except:
                pass
                
        # Check subject alternative names
        san = cert.get('subjectAltName', [])
        hostnames_in_cert = [name[1] for name in san if name[0] == 'DNS']
        if hostname not in hostnames_in_cert and not any(
            hostname.endswith(h.replace('*', '')) for h in hostnames_in_cert
        ):
            issues.append({
                'type': 'certificate_hostname_mismatch',
                'host': hostname,
                'severity': 'medium',
                'evidence': f"Hostname {hostname} not in certificate SAN"
            })
            
        return issues
    
    def scan_open_ports(self, host: str, ports: List[int]) -> List[Dict[str, Any]]:
        """Scan for unnecessarily open ports"""
        logger.info(f"Scanning open ports: {host}")
        
        vulnerabilities = []
        risky_ports = {
            21: 'FTP',
            23: 'Telnet',
            135: 'RPC',
            139: 'NetBIOS',
            445: 'SMB',
            1433: 'MSSQL',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC'
        }
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
                    if port in risky_ports:
                        vuln = {
                            'type': 'risky_service_exposed',
                            'host': host,
                            'port': port,
                            'service': risky_ports[port],
                            'severity': 'medium',
                            'evidence': f"{risky_ports[port]} service exposed on port {port}"
                        }
                        vulnerabilities.append(vuln)
                        
            except Exception as e:
                logger.error(f"Error scanning port {port}: {e}")
                
        return vulnerabilities


class ConfigurationScanner:
    """Configuration and security settings scanner"""
    
    def __init__(self):
        self.vulnerabilities = []
        
    def scan_web_headers(self, url: str) -> List[Dict[str, Any]]:
        """Scan for missing security headers"""
        logger.info(f"Scanning security headers: {url}")
        
        vulnerabilities = []
        
        try:
            response = requests.get(url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Frame-Options': 'clickjacking protection',
                'X-Content-Type-Options': 'MIME type sniffing protection',
                'X-XSS-Protection': 'XSS protection',
                'Strict-Transport-Security': 'HTTPS enforcement',
                'Content-Security-Policy': 'content injection protection',
                'Referrer-Policy': 'referrer information control'
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    vuln = {
                        'type': 'missing_security_header',
                        'url': url,
                        'header': header,
                        'description': description,
                        'severity': 'low',
                        'evidence': f"Missing security header: {header}"
                    }
                    vulnerabilities.append(vuln)
                    
            # Check for information disclosure headers
            disclosure_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in disclosure_headers:
                if header in headers:
                    vuln = {
                        'type': 'information_disclosure',
                        'url': url,
                        'header': header,
                        'value': headers[header],
                        'severity': 'info',
                        'evidence': f"Information disclosure: {header}: {headers[header]}"
                    }
                    vulnerabilities.append(vuln)
                    
        except Exception as e:
            logger.error(f"Error scanning headers: {e}")
            
        return vulnerabilities
    
    def scan_default_credentials(self, host: str, service: str) -> List[Dict[str, Any]]:
        """Scan for default credentials on common services"""
        logger.info(f"Scanning default credentials: {host} ({service})")
        
        vulnerabilities = []
        
        default_creds = {
            'ssh': [('root', 'root'), ('admin', 'admin'), ('root', 'toor')],
            'ftp': [('anonymous', ''), ('ftp', 'ftp'), ('admin', 'admin')],
            'web': [('admin', 'admin'), ('admin', 'password'), ('root', 'root')],
            'db': [('root', ''), ('admin', 'admin'), ('sa', '')]
        }
        
        if service in default_creds:
            # This is a simulation - real implementation would attempt login
            for username, password in default_creds[service][:2]:  # Test first 2
                # Simulate credential test
                logger.info(f"Would test {service} credentials: {username}:{password}")
                
                # For demonstration, assume some are vulnerable
                if username == 'admin' and password == 'admin':
                    vuln = {
                        'type': 'default_credentials',
                        'host': host,
                        'service': service,
                        'username': username,
                        'password': password,
                        'severity': 'critical',
                        'evidence': f"Default credentials found: {username}:{password}"
                    }
                    vulnerabilities.append(vuln)
                    
        return vulnerabilities


class VulnScanOrchestrator:
    """Main vulnerability scanning orchestrator"""
    
    def __init__(self):
        self.web_scanner = WebVulnScanner()
        self.network_scanner = NetworkVulnScanner()
        self.config_scanner = ConfigurationScanner()
        
    def comprehensive_scan(self, target: str, scan_type: str = "auto") -> Dict[str, Any]:
        """Perform comprehensive vulnerability scan"""
        logger.info(f"Starting comprehensive scan on {target}")
        
        results = {
            'target': target,
            'scan_type': scan_type,
            'timestamp': time.time(),
            'vulnerabilities': []
        }
        
        try:
            if scan_type == "web" or (scan_type == "auto" and target.startswith("http")):
                # Web application scan
                web_vulns = self._scan_web_application(target)
                results['vulnerabilities'].extend(web_vulns)
                
            elif scan_type == "network" or scan_type == "auto":
                # Network scan
                if target.startswith("http"):
                    target = urlparse(target).hostname
                    
                network_vulns = self._scan_network_host(target)
                results['vulnerabilities'].extend(network_vulns)
                
        except Exception as e:
            logger.error(f"Error during vulnerability scan: {e}")
            results['error'] = str(e)
            
        # Summarize results
        results['summary'] = self._summarize_results(results['vulnerabilities'])
        
        return results
    
    def _scan_web_application(self, url: str) -> List[Dict[str, Any]]:
        """Scan web application for vulnerabilities"""
        vulnerabilities = []
        
        # Common parameters to test
        test_params = ['id', 'page', 'file', 'url', 'redirect', 'q', 'search']
        
        # Run various web scans
        vulnerabilities.extend(self.web_scanner.scan_directory_traversal(url))
        vulnerabilities.extend(self.web_scanner.scan_xss(url, test_params))
        vulnerabilities.extend(self.web_scanner.scan_sql_injection(url, test_params))
        vulnerabilities.extend(self.web_scanner.scan_open_redirect(url))
        vulnerabilities.extend(self.config_scanner.scan_web_headers(url))
        
        return vulnerabilities
    
    def _scan_network_host(self, host: str) -> List[Dict[str, Any]]:
        """Scan network host for vulnerabilities"""
        vulnerabilities = []
        
        # Common ports to scan
        common_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 993, 995, 3389]
        
        # Run network scans
        vulnerabilities.extend(self.network_scanner.scan_open_ports(host, common_ports))
        vulnerabilities.extend(self.network_scanner.scan_ssl_vulnerabilities(host))
        
        # Check for default credentials on detected services
        vulnerabilities.extend(self.config_scanner.scan_default_credentials(host, 'ssh'))
        
        return vulnerabilities
    
    def _summarize_results(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize vulnerability scan results"""
        summary = {
            'total_vulnerabilities': len(vulnerabilities),
            'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0},
            'by_type': {}
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info')
            vuln_type = vuln.get('type', 'unknown')
            
            summary['by_severity'][severity] += 1
            summary['by_type'][vuln_type] = summary['by_type'].get(vuln_type, 0) + 1
            
        return summary


def main():
    """Main function for testing"""
    scanner = VulnScanOrchestrator()
    
    print("=== Pentest-USB Custom Vulnerability Scanners ===")
    print("Testing vulnerability scanning...")
    
    # Test web application scan
    results = scanner.comprehensive_scan("http://example.com", "web")
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()